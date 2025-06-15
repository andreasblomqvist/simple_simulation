from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from backend.src.services.simulation_engine import SimulationEngine, Month
from fastapi import UploadFile, File
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a global engine instance
engine = SimulationEngine()

class SimulationRequest(BaseModel):
    start_year: int
    start_month: int  # 1-12
    end_year: int
    end_month: int    # 1-12
    price_increase: float
    salary_increase: float
    # Advanced: office overrides for FTE, level, and operations params
    office_overrides: Optional[Dict[str, Dict[str, Any]]] = None

# Example office_overrides structure:
# {
#   "Oslo": {
#     "total_fte": 120,
#     "roles": {
#       "Consultant": {
#         "A": {"recruitment_1": 0.2, "churn_1": 0.05, ...},
#         ...
#       },
#       "Sales": {
#         ...
#       },
#       "Recruitment": {
#         ...
#       },
#       ...
#     },
#     "operations": {"recruitment_1": 0.1, "churn_1": 0.02, ...}
#   },
#   ...
# }

@app.post("/simulate")
def run_simulation(req: SimulationRequest):
    lever_plan = None
    if req.office_overrides:
        lever_plan = {}
        for office_name, overrides in req.office_overrides.items():
            lever_plan[office_name] = {}
            for role_name, role_data in overrides.get("roles", {}).items():
                lever_plan[office_name][role_name] = {}
                if isinstance(role_data, dict):
                    for level_name, level_overrides in role_data.items():
                        lever_plan[office_name][role_name][level_name] = {}
                        for key, value in level_overrides.items():
                            lever_plan[office_name][role_name][level_name][key.lower()] = value
                else:
                    for key, value in role_data.items():
                        lever_plan[office_name][role_name][key.lower()] = value
    results = engine.run_simulation(
        start_year=req.start_year,
        start_month=req.start_month,
        end_year=req.end_year,
        end_month=req.end_month,
        price_increase=req.price_increase,
        salary_increase=req.salary_increase,
        lever_plan=lever_plan
    )
    return results

@app.get("/")
def root():
    return {"message": "Organization Growth Simulator API"}

@app.get("/offices")
def list_offices():
    offices_out = []
    for office in engine.offices.values():
        roles_out = {}
        for role, data in office.roles.items():
            if isinstance(data, dict):
                # Roles with levels (Consultant, Sales, Recruitment)
                roles_out[role] = {
                    level_name: {
                        "total": level.total,
                        **{f"price_{i}": getattr(level, f'price_{i}') for i in range(1, 13)},
                        **{f"salary_{i}": getattr(level, f'salary_{i}') for i in range(1, 13)},
                        **{f"recruitment_{i}": getattr(level, f'recruitment_{i}') for i in range(1, 13)},
                        **{f"churn_{i}": getattr(level, f'churn_{i}') for i in range(1, 13)},
                        **{f"progression_{i}": getattr(level, f'progression_{i}') for i in range(1, 13)},
                        **{f"utr_{i}": getattr(level, f'utr_{i}') for i in range(1, 13)}
                    }
                    for level_name, level in data.items()
                }
            else:
                # Flat roles (Operations)
                roles_out[role] = {
                    "total": data.total,
                    **{f"price_{i}": getattr(data, f'price_{i}') for i in range(1, 13)},
                    **{f"salary_{i}": getattr(data, f'salary_{i}') for i in range(1, 13)},
                    **{f"recruitment_{i}": getattr(data, f'recruitment_{i}') for i in range(1, 13)},
                    **{f"churn_{i}": getattr(data, f'churn_{i}') for i in range(1, 13)},
                    **{f"progression_{i}": getattr(data, f'progression_{i}', 0.0) for i in range(1, 13)},
                    **{f"utr_{i}": getattr(data, f'utr_{i}') for i in range(1, 13)}
                }
        offices_out.append({
            "name": office.name,
            "total_fte": office.total_fte,
            "journey": office.journey.value,
            "roles": roles_out
        })
    return offices_out

@app.post("/import-office-levers")
async def import_office_levers(file: UploadFile = File(...)):
    import pandas as pd
    df = pd.read_excel(file.file)
    # Use the global engine
    for _, row in df.iterrows():
        office_name = row["Office"]
        role_name = row["Role"]
        level_name = row["Level"] if not pd.isna(row["Level"]) else None
        office = engine.offices.get(office_name)
        if not office:
            continue
        if role_name in office.roles:
            if isinstance(office.roles[role_name], dict) and level_name:
                # Roles with levels (Consultant, Sales, Recruitment)
                if level_name in office.roles[role_name]:
                    level = office.roles[role_name][level_name]
                    print(f"[IMPORT] Updating {office_name} {role_name} {level_name} with FTE={row['FTE']}")
                    level.total = int(row["FTE"]) if not pd.isna(row["FTE"]) else level.total
                    
                    # Update monthly values (1-12)
                    for i in range(1, 13):
                        for attr in ["Price", "Salary", "Recruitment", "Churn", "Progression", "UTR"]:
                            col_name = f"{attr}_{i}"
                            if col_name in row and not pd.isna(row[col_name]):
                                setattr(level, col_name.lower(), float(row[col_name]))
                                
            elif not isinstance(office.roles[role_name], dict) and not level_name:
                # Flat role (Operations)
                role = office.roles[role_name]
                print(f"[IMPORT] Updating {office_name} {role_name} with FTE={row['FTE']}")
                role.total = int(row["FTE"]) if not pd.isna(row["FTE"]) else role.total
                
                # Update monthly values (1-12)
                for i in range(1, 13):
                    for attr in ["Price", "Salary", "Recruitment", "Churn", "UTR"]:
                        col_name = f"{attr}_{i}"
                        if col_name in row and not pd.isna(row[col_name]):
                            if hasattr(role, col_name.lower()):
                                setattr(role, col_name.lower(), float(row[col_name]))
                            
    return {"status": "success", "rows": len(df)} 