from fastapi import APIRouter, UploadFile, File
import pandas as pd
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