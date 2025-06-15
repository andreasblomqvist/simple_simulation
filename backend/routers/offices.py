from fastapi import APIRouter, UploadFile, File
import pandas as pd
from backend.src.services.simulation_engine import SimulationEngine

router = APIRouter(prefix="/offices", tags=["offices"])

# Global engine instance - will be injected from main
engine: SimulationEngine = None

def set_engine(simulation_engine: SimulationEngine):
    """Set the global engine instance"""
    global engine
    engine = simulation_engine

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
    """Get all offices with their current configuration"""
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
    return offices_out

@router.post("/import")
async def import_office_levers(file: UploadFile = File(...)):
    """Import office configuration from Excel file"""
    df = pd.read_excel(file.file)
    updated_count = 0
    
    for _, row in df.iterrows():
        office_name = row["Office"]
        role_name = row["Role"]
        level_name = row["Level"] if not pd.isna(row["Level"]) else None
        
        office = engine.offices.get(office_name)
        if not office or role_name not in office.roles:
            continue
            
        if isinstance(office.roles[role_name], dict) and level_name:
            # Roles with levels (Consultant, Sales, Recruitment)
            if level_name in office.roles[role_name]:
                level = office.roles[role_name][level_name]
                print(f"[IMPORT] Updating {office_name} {role_name} {level_name} with FTE={row['FTE']}")
                
                # Update FTE
                if not pd.isna(row["FTE"]):
                    level.total = int(row["FTE"])
                
                # Update monthly values (1-12)
                _update_monthly_attributes(level, row)
                updated_count += 1
                
        elif not isinstance(office.roles[role_name], dict) and not level_name:
            # Flat role (Operations)
            role = office.roles[role_name]
            print(f"[IMPORT] Updating {office_name} {role_name} with FTE={row['FTE']}")
            
            # Update FTE
            if not pd.isna(row["FTE"]):
                role.total = int(row["FTE"])
            
            # Update monthly values (1-12)
            _update_monthly_attributes(role, row)
            updated_count += 1
    
    return {"status": "success", "rows": len(df), "updated": updated_count}

def _update_monthly_attributes(obj, row):
    """Update monthly attributes from Excel row"""
    for i in range(1, 13):
        for attr in ["Price", "Salary", "Recruitment", "Churn", "Progression", "UTR"]:
            col_name = f"{attr}_{i}"
            if col_name in row and not pd.isna(row[col_name]):
                attr_name = col_name.lower()
                if hasattr(obj, attr_name):
                    setattr(obj, attr_name, float(row[col_name])) 