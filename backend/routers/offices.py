from fastapi import APIRouter, UploadFile, File
import pandas as pd
from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.config_service import config_service
from backend.config.default_config import ACTUAL_OFFICE_LEVEL_DATA, BASE_PRICING, BASE_SALARIES, DEFAULT_RATES, OFFICE_HEADCOUNT

router = APIRouter(prefix="/offices", tags=["offices"])

# Global engine instance - will be injected from main
engine: SimulationEngine = None

def set_engine(simulation_engine: SimulationEngine):
    """Set the global engine instance"""
    global engine
    engine = simulation_engine

@router.get("/config")
def get_office_config():
    """Get configuration data from configuration service (NOT simulation engine)"""
    return config_service.get_configuration()

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

@router.post("/config/reset")
async def reset_office_config():
    """Reset configuration back to defaults"""
    config_service.reset_to_defaults()
    
    return {
        "status": "success",
        "message": "Configuration reset to defaults"
    }

def _serialize_monthly_attributes(obj, attributes: list) -> dict:
    """Helper to serialize monthly attributes (1-12) for an object"""
    result = {}
    for attr in attributes:
        for i in range(1, 13):
            attr_name = f"{attr}_{i}"
            if attr == "progression" and not hasattr(obj, attr_name):
                result[attr_name] = 0.0  # Default for operations
            else:
                result[attr_name] = getattr(obj, attr_name, 0.0)
    return result

def _serialize_role_data(role_data) -> dict:
    """Serialize role data (either dict of levels or flat role)"""
    if isinstance(role_data, dict):
        # Roles with levels (Consultant, Sales, Recruitment)
        return {
            level_name: {
                "total": level.total,
                **_serialize_monthly_attributes(level, ["price", "salary", "recruitment", "churn", "progression", "utr"])
            }
            for level_name, level in role_data.items()
        }
    else:
        # Flat roles (Operations)
        return {
            "total": role_data.total,
            **_serialize_monthly_attributes(role_data, ["price", "salary", "recruitment", "churn", "progression", "utr"])
        }

@router.get("/")
def list_offices():
    """Get offices from simulation engine (includes imported changes)"""
    # Initialize engine offices if not already done
    if not engine.offices:
        print("[API] Initializing simulation engine offices for first time...")
        engine._initialize_offices()
        engine._initialize_roles_with_levers(None)
        print(f"[API] ✓ Initialized {len(engine.offices)} offices")
    
    offices_out = []
    for office in engine.offices.values():
        roles_out = {}
        for role_name, role_data in office.roles.items():
            roles_out[role_name] = _serialize_role_data(role_data)
        
        offices_out.append({
            "name": office.name,
            "total_fte": office.total_fte,
            "journey": office.journey.value,
            "roles": roles_out
        })
    
    print(f"[API] Returning {len(offices_out)} offices with live simulation engine data")
    return offices_out

@router.post("/import")
async def import_office_levers(file: UploadFile = File(...)):
    """Import office configuration from Excel file"""
    # Initialize engine offices if not already done
    if not engine.offices:
        print("[IMPORT] Initializing simulation engine offices before import...")
        engine._initialize_offices()
        engine._initialize_roles_with_levers(None)
        print(f"[IMPORT] ✓ Initialized {len(engine.offices)} offices")
    
    # Read file content into memory to avoid SpooledTemporaryFile issues
    content = await file.read()
    df = pd.read_excel(content)
    updated_count = 0
    
    print(f"[IMPORT] Processing {len(df)} rows from Excel file...")
    
    for _, row in df.iterrows():
        office_name = row.get("Office")
        role_type = row.get("Role")
        role_level = row.get("Level")
        
        if office_name and role_type and role_level:
            office = engine.offices.get(office_name)
            if office and role_type in office.roles:
                role_data = office.roles[role_type]
                
                # Check if this role has levels (dict) or is flat (RoleData)
                if isinstance(role_data, dict):
                    # Role with levels (Consultant, Sales, Recruitment)
                    if role_level in role_data:
                        level_obj = role_data[role_level]
                        _update_monthly_attributes(level_obj, row)
                        updated_count += 1
                else:
                    # Flat role (Operations) - ignore level, update directly
                    if role_type == "Operations":  # Only update Operations for flat roles
                        _update_monthly_attributes(role_data, row)
                        updated_count += 1
    
    print(f"[IMPORT] ✅ Import complete: {updated_count} rows updated")
    return {"status": "success", "rows": len(df), "updated": updated_count}

def _update_monthly_attributes(obj, row):
    """Update monthly attributes from Excel row"""
    for i in range(1, 13):
        for attr in ["Price", "Salary", "Recruitment", "Churn", "Progression", "UTR"]:
            col_name = f"{attr}_{i}"
            if col_name in row and not pd.isna(row[col_name]):
                attr_name = col_name.lower()
                if hasattr(obj, attr_name):
                    try:
                        # Handle different value types from Excel
                        value = row[col_name]
                        
                        # If it's already a number, use it directly
                        if isinstance(value, (int, float)):
                            converted_value = float(value)
                        # If it's a string, handle European decimal format (comma separator)
                        elif isinstance(value, str):
                            # Replace comma with dot for European decimal format
                            cleaned_value = value.replace(',', '.')
                            converted_value = float(cleaned_value)
                        else:
                            # Try direct conversion for other types
                            converted_value = float(value)
                        
                        # Set the converted value
                        setattr(obj, attr_name, converted_value)
                        print(f"[IMPORT] Set {attr_name} = {converted_value} (from '{value}')")
                        
                    except (ValueError, TypeError) as e:
                        print(f"[IMPORT] Error converting {col_name}='{row[col_name]}': {e}")
                        continue 

@router.post("/config/apply")
async def apply_config_changes(changes: dict):
    """Apply configuration changes to the simulation engine"""
    # Initialize engine offices if not already done
    if not engine.offices:
        print("[CONFIG] Initializing simulation engine offices before applying changes...")
        engine._initialize_offices()
        engine._initialize_roles_with_levers(None)
        print(f"[CONFIG] ✓ Initialized {len(engine.offices)} offices")
    
    updated_count = 0
    
    print(f"[CONFIG] Applying {len(changes)} configuration changes...")
    
    for path, value in changes.items():
        try:
            # Parse the path: office.role.level.field or office.role.field
            path_parts = path.split('.')
            if len(path_parts) < 3:
                print(f"[CONFIG] ⚠️ Skipping invalid path: {path}")
                continue
                
            office_name = path_parts[0]
            role_type = path_parts[1]
            
            # Find the office
            office = engine.offices.get(office_name)
                    
            if not office:
                print(f"[CONFIG] ⚠️ Office not found: {office_name}")
                continue
                
            # Handle Operations (flat structure) vs other roles (level-based)
            if role_type == "Operations":
                # Operations: office.role.field
                if len(path_parts) != 3:
                    print(f"[CONFIG] ⚠️ Invalid Operations path: {path}")
                    continue
                    
                field = path_parts[2]
                if hasattr(office.roles.get(role_type), field):
                    setattr(office.roles[role_type], field, value)
                    print(f"[CONFIG] ✓ Updated {path} = {value}")
                    updated_count += 1
                else:
                    print(f"[CONFIG] ⚠️ Field not found: {field} in {role_type}")
                    
            else:
                # Other roles: office.role.level.field
                if len(path_parts) != 4:
                    print(f"[CONFIG] ⚠️ Invalid role path: {path}")
                    continue
                    
                level = path_parts[2]
                field = path_parts[3]
                
                # Check if role and level exist
                if role_type in office.roles:
                    role_data = office.roles[role_type]
                    
                    # Check if role has levels (dict) or is flat (RoleData object)
                    if isinstance(role_data, dict) and level in role_data:
                        # Dictionary-based role with levels
                        role_level_obj = role_data[level]
                        if hasattr(role_level_obj, field):
                            setattr(role_level_obj, field, value)
                            print(f"[CONFIG] ✓ Updated {path} = {value}")
                            updated_count += 1
                        else:
                            print(f"[CONFIG] ⚠️ Field not found: {field} in {role_type}.{level}")
                    else:
                        print(f"[CONFIG] ⚠️ Level not found or role is not dict-based: {role_type}.{level}")
                else:
                    print(f"[CONFIG] ⚠️ Role not found: {role_type}")
                    
        except Exception as e:
            print(f"[CONFIG] ❌ Error updating {path}: {str(e)}")
    
    print(f"[CONFIG] ✅ Applied {updated_count} configuration changes")
    
    return {
        "status": "success",
        "message": f"Applied {updated_count} configuration changes",
        "updated_count": updated_count,
        "total_changes": len(changes)
    } 