from fastapi import APIRouter, UploadFile, File
import pandas as pd
from backend.src.services.simulation_engine import SimulationEngine
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
    """Get raw office configuration data WITHOUT going through simulation engine"""
    offices_out = []
    
    for office_name, office_data in ACTUAL_OFFICE_LEVEL_DATA.items():
        total_fte = OFFICE_HEADCOUNT.get(office_name, 0)
        
        # Determine office journey based on total FTE
        if total_fte >= 500:
            journey = "Mature Office"
        elif total_fte >= 200:
            journey = "Established Office"
        elif total_fte >= 25:
            journey = "Emerging Office"
        else:
            journey = "New Office"
        
        roles_out = {}
        
        # Process roles with levels (Consultant, Sales, Recruitment)
        for role_name in ["Consultant", "Sales", "Recruitment"]:
            if role_name in office_data:
                role_levels = office_data[role_name]
                roles_out[role_name] = {}
                
                for level_name, fte in role_levels.items():
                    if fte > 0:  # Only include levels with actual FTE
                        # Get pricing and salary
                        base_prices = BASE_PRICING.get(office_name, BASE_PRICING['Stockholm'])
                        base_salaries = BASE_SALARIES.get(office_name, BASE_SALARIES['Stockholm'])
                        price = base_prices.get(level_name, 0.0)
                        salary = base_salaries.get(level_name, 0.0)
                        
                        # Get rates
                        if role_name in DEFAULT_RATES['recruitment'] and isinstance(DEFAULT_RATES['recruitment'][role_name], dict):
                            recruitment_rate = DEFAULT_RATES['recruitment'][role_name].get(level_name, 0.01)
                        else:
                            recruitment_rate = 0.01
                        
                        if role_name in DEFAULT_RATES['churn'] and isinstance(DEFAULT_RATES['churn'][role_name], dict):
                            churn_rate = DEFAULT_RATES['churn'][role_name].get(level_name, 0.014)
                        elif role_name in DEFAULT_RATES['churn']:
                            churn_rate = DEFAULT_RATES['churn'][role_name]
                        else:
                            churn_rate = 0.014
                        
                        # Set progression rate based on level using correct rates
                        progression_map = {
                            'C': 0.26, 'SrC': 0.20, 'AM': 0.07, 'M': 0.12, 'SrM': 0.14,
                            'A': 0.15, 'AC': 0.12, 'PiP': 0.0
                        }
                        progression_rate = progression_map.get(level_name, 0.10)
                        
                        roles_out[role_name][level_name] = {
                            "total": fte,
                            **{f"price_{i}": price * (1 + 0.0025 * (i - 1)) for i in range(1, 13)},
                            **{f"salary_{i}": salary * (1 + 0.0025 * (i - 1)) for i in range(1, 13)},
                            **{f"recruitment_{i}": recruitment_rate for i in range(1, 13)},
                            **{f"churn_{i}": churn_rate for i in range(1, 13)},
                            **{f"progression_{i}": progression_rate if i in [1, 6] else 0.0 for i in range(1, 13)},
                            **{f"utr_{i}": DEFAULT_RATES['utr'] for i in range(1, 13)}
                        }
        
        # Process Operations (flat role)
        if "Operations" in office_data and office_data["Operations"] > 0:
            operations_fte = office_data["Operations"]
            base_prices = BASE_PRICING.get(office_name, BASE_PRICING['Stockholm'])
            base_salaries = BASE_SALARIES.get(office_name, BASE_SALARIES['Stockholm'])
            op_price = base_prices.get('Operations', 80.0)
            op_salary = base_salaries.get('Operations', 40000.0)
            
            operations_recruitment = DEFAULT_RATES['recruitment'].get('Operations', 0.021)
            operations_churn = DEFAULT_RATES['churn'].get('Operations', 0.0149)
            
            roles_out["Operations"] = {
                "total": operations_fte,
                **{f"price_{i}": op_price * (1 + 0.0025 * (i - 1)) for i in range(1, 13)},
                **{f"salary_{i}": op_salary * (1 + 0.0025 * (i - 1)) for i in range(1, 13)},
                **{f"recruitment_{i}": operations_recruitment for i in range(1, 13)},
                **{f"churn_{i}": operations_churn for i in range(1, 13)},
                **{f"progression_{i}": 0.0 for i in range(1, 13)},  # Operations has no progression
                **{f"utr_{i}": DEFAULT_RATES['utr'] for i in range(1, 13)}
            }
        
        offices_out.append({
            "name": office_name,
            "total_fte": total_fte,
            "journey": journey,
            "roles": roles_out
        })
    
    return offices_out

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
    """Get offices from simulation engine (for simulation results, not configuration)"""
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
    # Read file content into memory to avoid SpooledTemporaryFile issues
    content = await file.read()
    df = pd.read_excel(content)
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
                
                # Update FTE by adjusting people list
                if not pd.isna(row["FTE"]):
                    target_fte = int(row["FTE"])
                    current_fte = level.total
                    
                    if target_fte != current_fte:
                        print(f"[IMPORT] Adjusting FTE from {current_fte} to {target_fte}")
                        
                        if target_fte > current_fte:
                            # Add people
                            for i in range(target_fte - current_fte):
                                level.add_new_hire("2024-01", role_name, office_name)
                        elif target_fte < current_fte:
                            # Remove people (simple truncation)
                            excess = current_fte - target_fte
                            level.people = level.people[:-excess]
                
                # Update monthly values (1-12)
                _update_monthly_attributes(level, row)
                updated_count += 1
                
        elif not isinstance(office.roles[role_name], dict) and not level_name:
            # Flat role (Operations)
            role = office.roles[role_name]
            print(f"[IMPORT] Updating {office_name} {role_name} with FTE={row['FTE']}")
            
            # Update FTE by adjusting people list
            if not pd.isna(row["FTE"]):
                target_fte = int(row["FTE"])
                current_fte = role.total
                
                if target_fte != current_fte:
                    print(f"[IMPORT] Adjusting FTE from {current_fte} to {target_fte}")
                    
                    if target_fte > current_fte:
                        # Add people
                        for i in range(target_fte - current_fte):
                            role.add_new_hire("2024-01", role_name, office_name)
                    elif target_fte < current_fte:
                        # Remove people (simple truncation)
                        excess = current_fte - target_fte
                        role.people = role.people[:-excess]
            
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
                    try:
                        # Handle different value types from Excel
                        value = row[col_name]
                        
                        # If it's already a number, use it directly
                        if isinstance(value, (int, float)):
                            setattr(obj, attr_name, float(value))
                        elif isinstance(value, str):
                            # Handle string values - remove spaces and replace comma with dot
                            cleaned_value = value.strip().replace(',', '.')
                            # Remove any non-numeric characters except dots and minus signs
                            cleaned_value = ''.join(c for c in cleaned_value if c.isdigit() or c in '.-')
                            if cleaned_value:
                                setattr(obj, attr_name, float(cleaned_value))
                            else:
                                print(f"[IMPORT] Skipping {col_name}: empty string after cleaning")
                        else:
                            # Try direct conversion for other types
                            setattr(obj, attr_name, float(value))
                            
                    except (ValueError, TypeError) as e:
                        # Skip if it's not a valid float
                        print(f"[IMPORT] Skipping {col_name}: invalid value type ({type(row[col_name])}) - {row[col_name]}")
                        continue 