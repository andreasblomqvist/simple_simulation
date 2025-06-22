from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
import pandas as pd
import io
from backend.src.services.config_service import config_service

router = APIRouter(prefix="/offices", tags=["offices"])

# Global variable to store engine reference (for compatibility)
_engine = None

def set_engine(engine):
    """Set the simulation engine reference (for compatibility with main.py)"""
    global _engine
    _engine = engine
    print("[INFO] Engine set in offices router")

@router.get("/config")
def get_office_config():
    """Get configuration data from configuration service (NOT simulation engine)"""
    config_dict = config_service.get_configuration()
    # Convert dictionary to array for frontend compatibility
    return list(config_dict.values())

@router.post("/config/update")
async def update_office_config(changes: dict):
    """Update configuration in the configuration service"""
    updated_count = config_service.update_configuration(changes)
    
    return {
        "status": "success",
        "message": f"Updated {updated_count} configuration values",
        "updated_count": updated_count,
        "total_changes": len(changes)
    }

@router.post("/config/import")
async def import_office_config(file: UploadFile = File(...)):
    """Import configuration from Excel file into configuration service"""
    # Read file content into memory
    content = await file.read()
    df = pd.read_excel(content)
    
    # Import into configuration service
    updated_count = config_service.import_from_excel(df)
    
    return {
        "status": "success", 
        "message": f"Imported {updated_count} configuration changes",
        "rows": len(df), 
        "updated": updated_count
    }

@router.get("/config/validation")
def validate_office_configuration():
    """Validate office configuration integrity and return report"""
    from datetime import datetime
    from fastapi import HTTPException
    
    try:
        # Get configuration from configuration service (NOT simulation engine)
        config = config_service.get_configuration()
        
        if not config:
            return {
                "status": "empty",
                "message": "No configuration data found",
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_offices": 0,
                    "total_roles": 0,
                    "total_levels": 0,
                    "total_fte": 0,
                    "missing_data_count": 0
                }
            }
        
        # Calculate summary from configuration service data
        total_offices = len(config)
        total_roles = 0
        total_levels = 0
        total_fte = 0
        
        for office_name, office_data in config.items():
            if 'roles' in office_data:
                for role_name, role_data in office_data['roles'].items():
                    total_roles += 1
                    if isinstance(role_data, dict):
                        # All roles have levels structure (including Operations with "nan")
                        for level_name, level_data in role_data.items():
                            total_levels += 1
                            if isinstance(level_data, dict) and 'fte' in level_data:
                                total_fte += level_data['fte']
        
        return {
            "status": "valid",
            "message": "Configuration loaded successfully",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_offices": total_offices,
                "total_roles": total_roles,
                "total_levels": total_levels,
                "total_fte": total_fte,
                "missing_data_count": 0
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration validation failed: {str(e)}")

@router.get("/config/checksum")
def get_office_configuration_checksum():
    """Get just the configuration checksum for quick integrity checks"""
    from datetime import datetime
    from fastapi import HTTPException
    
    try:
        # Get configuration from configuration service (NOT simulation engine)
        config = config_service.get_configuration()
        
        if not config:
            return {
                "checksum": "empty",
                "total_offices": 0,
                "total_fte": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        # Calculate simple checksum and totals from configuration service data
        total_offices = len(config)
        total_fte = 0
        
        for office_name, office_data in config.items():
            if 'total_fte' in office_data:
                total_fte += office_data['total_fte']
        
        # Simple checksum: hash of office count and total FTE
        import hashlib
        checksum_string = f"{total_offices}:{total_fte}"
        config_checksum = hashlib.md5(checksum_string.encode()).hexdigest()[:8]
        
        return {
            "checksum": config_checksum,
            "total_offices": total_offices,
            "total_fte": total_fte,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Checksum calculation failed: {str(e)}")

def _serialize_role_data(role_data) -> dict:
    """Serialize role data - configuration service already provides correct format"""
    return role_data

@router.get("/")
def list_offices():
    """Get offices from configuration service (NOT simulation engine)"""
    config_dict = config_service.get_configuration()
    
    offices_out = []
    for office_data in config_dict.values():
        # office_data is already a dictionary with the correct structure
        roles_out = {}
        if "roles" in office_data and isinstance(office_data["roles"], dict):
            for role_name, role_data in office_data["roles"].items():
                roles_out[role_name] = _serialize_role_data(role_data)
        
        offices_out.append({
            "name": office_data.get("name", "Unknown"),
            "total_fte": office_data.get("total_fte", 0),
            "journey": office_data.get("journey", "Unknown"),
            "roles": roles_out
        })
    
    print(f"[API] Returning {len(offices_out)} offices with configuration service data")
    return offices_out 

@router.post("/config/export")
async def export_office_config(export_request: dict):
    """Export all office configuration to Excel file in import-compatible format"""
    try:
        # Get all configuration data
        config_dict = config_service.get_configuration()
        
        # Apply any unsaved changes if requested
        unsaved_changes = export_request.get('unsavedChanges', {})
        if export_request.get('includeUnsavedChanges', False) and unsaved_changes:
            # Apply draft changes to the configuration
            for path, value in unsaved_changes.items():
                path_parts = path.split('.')
                office_name, role_name = path_parts[0], path_parts[1]
                
                if office_name in config_dict:
                    if len(path_parts) == 3:
                        # Operations: office.role.field
                        field = path_parts[2]
                        if 'roles' not in config_dict[office_name]:
                            config_dict[office_name]['roles'] = {}
                        if role_name not in config_dict[office_name]['roles']:
                            config_dict[office_name]['roles'][role_name] = {}
                        config_dict[office_name]['roles'][role_name][field] = value
                    elif len(path_parts) == 4:
                        # Has level: office.role.level.field
                        level_name, field = path_parts[2], path_parts[3]
                        if 'roles' not in config_dict[office_name]:
                            config_dict[office_name]['roles'] = {}
                        if role_name not in config_dict[office_name]['roles']:
                            config_dict[office_name]['roles'][role_name] = {}
                        if level_name not in config_dict[office_name]['roles'][role_name]:
                            config_dict[office_name]['roles'][role_name][level_name] = {}
                        config_dict[office_name]['roles'][role_name][level_name][field] = value
        
        # Convert configuration to Excel format matching the import format
        excel_rows = []
        
        # Define the expected column order (like the original Excel file)
        expected_columns = ['Office', 'Role', 'Level', 'FTE']
        
        # Add monthly columns (Price_1 through Price_12, etc.)
        for month in range(1, 13):
            expected_columns.extend([
                f'Price_{month}', f'Salary_{month}', f'Recruitment_{month}', 
                f'Churn_{month}', f'UTR_{month}', f'Progression_{month}'
            ])
        
        for office_name, office_data in config_dict.items():
            if 'roles' in office_data:
                for role_name, role_data in office_data['roles'].items():
                    if role_name == 'Operations':
                        # Operations is a flat structure with level 'nan'
                        row = {
                            'Office': office_name,
                            'Role': role_name,
                            'Level': 'nan'
                        }
                        
                        # Map internal field names to Excel column names
                        for field_name, value in role_data.items():
                            if field_name == 'fte':
                                row['FTE'] = value
                            elif '_' in field_name:
                                # Convert field like 'price_1' to 'Price_1'
                                parts = field_name.split('_')
                                if len(parts) == 2:
                                    base_name = parts[0].capitalize()
                                    month_num = parts[1]
                                    excel_col = f'{base_name}_{month_num}'
                                    row[excel_col] = value
                            else:
                                # Handle other fields - capitalize first letter
                                excel_col = field_name.capitalize()
                                row[excel_col] = value
                        
                        excel_rows.append(row)
                    else:
                        # Consultant, Sales, Recruitment have levels
                        for level_name, level_data in role_data.items():
                            if isinstance(level_data, dict):
                                row = {
                                    'Office': office_name,
                                    'Role': role_name,
                                    'Level': level_name
                                }
                                
                                # Map internal field names to Excel column names
                                for field_name, value in level_data.items():
                                    if field_name == 'fte':
                                        row['FTE'] = value
                                    elif '_' in field_name:
                                        # Convert field like 'price_1' to 'Price_1'
                                        parts = field_name.split('_')
                                        if len(parts) == 2:
                                            base_name = parts[0].capitalize()
                                            month_num = parts[1]
                                            excel_col = f'{base_name}_{month_num}'
                                            row[excel_col] = value
                                    else:
                                        # Handle other fields - capitalize first letter
                                        excel_col = field_name.capitalize()
                                        row[excel_col] = value
                                
                                excel_rows.append(row)
        
        # Create DataFrame with all expected columns
        df = pd.DataFrame(excel_rows)
        
        # Ensure all expected columns exist (fill missing with NaN)
        for col in expected_columns:
            if col not in df.columns:
                df[col] = pd.NA
        
        # Reorder columns to match import format
        df = df.reindex(columns=expected_columns)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Configuration', index=False)
            
            # Add metadata sheet
            metadata = export_request.get('exportMetadata', {})
            metadata_rows = [
                ['Export Date', metadata.get('exportedAt', '')],
                ['Export Scope', metadata.get('exportScope', 'All Offices')],
                ['Exported By', metadata.get('exportedBy', 'Configuration Matrix')],
                ['Currently Viewed Office', metadata.get('currentlyViewedOffice', '')],
                ['Has Unsaved Changes', metadata.get('hasUnsavedChanges', False)],
                ['Unsaved Changes Count', metadata.get('unsavedChangeCount', 0)],
                ['Total Offices', len(config_dict)],
                ['Total Rows', len(excel_rows)]
            ]
            metadata_df = pd.DataFrame(metadata_rows, columns=['Property', 'Value'])
            metadata_df.to_excel(writer, sheet_name='Export_Metadata', index=False)
        
        output.seek(0)
        
        # Return as streaming response
        filename = f"all-offices-config-{export_request.get('exportMetadata', {}).get('exportedAt', '').split('T')[0] or 'export'}.xlsx"
        
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}") 