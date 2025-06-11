from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import sys
sys.path.append('./simple_simulation/src')
from services.simulation_engine import SimulationEngine, HalfYear
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
    start_half: str  # "H1" or "H2"
    end_year: int
    end_half: str    # "H1" or "H2"
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
#         "A": {"recruitment_h1": 0.2, "churn_h1": 0.05, ...},
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
#     "operations": {"recruitment_h1": 0.1, "churn_h1": 0.02, ...}
#   },
#   ...
# }

@app.post("/simulate")
def run_simulation(req: SimulationRequest):
    print("[SIMULATION INPUT]", req)
    # Use the global engine
    # Apply office_overrides if provided
    if req.office_overrides:
        for office_name, overrides in req.office_overrides.items():
            office = engine.offices.get(office_name)
            if not office:
                continue
            # Override FTE if provided
            if "total_fte" in overrides:
                office.total_fte = overrides["total_fte"]
            # Override role/level params
            for role_name, role_data in overrides.get("roles", {}).items():
                if role_name not in office.roles:
                    continue
                if isinstance(role_data, dict):
                    # Roles with levels (Consultant, Sales, Recruitment)
                    if isinstance(office.roles[role_name], dict):
                        for level_name, level_overrides in role_data.items():
                            if level_name in office.roles[role_name]:
                                for key, value in level_overrides.items():
                                    setattr(office.roles[role_name][level_name], key.lower(), value)
                else:
                    # Flat roles (Operations)
                    for key, value in role_data.items():
                        setattr(office.roles[role_name], key.lower(), value)
    results = engine.run_simulation(
        start_year=req.start_year,
        start_half=HalfYear[req.start_half],
        end_year=req.end_year,
        end_half=HalfYear[req.end_half],
        price_increase=req.price_increase,
        salary_increase=req.salary_increase
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
                        "price_h1": level.price_h1,
                        "price_h2": level.price_h2,
                        "salary_h1": level.salary_h1,
                        "salary_h2": level.salary_h2,
                        "recruitment_h1": level.recruitment_h1,
                        "recruitment_h2": level.recruitment_h2,
                        "churn_h1": level.churn_h1,
                        "churn_h2": level.churn_h2,
                        "progression_h1": level.progression_h1,
                        "progression_h2": level.progression_h2,
                        "utr_h1": level.utr_h1,
                        "utr_h2": level.utr_h2
                    }
                    for level_name, level in data.items()
                }
            else:
                # Flat roles (Operations)
                roles_out[role] = {
                    "total": data.total,
                    "price_h1": data.price_h1,
                    "price_h2": data.price_h2,
                    "salary_h1": data.salary_h1,
                    "salary_h2": data.salary_h2,
                    "recruitment_h1": data.recruitment_h1,
                    "recruitment_h2": data.recruitment_h2,
                    "churn_h1": data.churn_h1,
                    "churn_h2": data.churn_h2,
                    "progression_h1": data.progression_h1,
                    "progression_h2": data.progression_h2,
                    "utr_h1": data.utr_h1,
                    "utr_h2": data.utr_h2
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
                    level.price_h1 = float(row["Price_H1"]) if not pd.isna(row["Price_H1"]) else level.price_h1
                    level.price_h2 = float(row["Price_H2"]) if not pd.isna(row["Price_H2"]) else level.price_h2
                    level.salary_h1 = float(row["Salary_H1"]) if not pd.isna(row["Salary_H1"]) else level.salary_h1
                    level.salary_h2 = float(row["Salary_H2"]) if not pd.isna(row["Salary_H2"]) else level.salary_h2
                    level.recruitment_h1 = float(row["Recruitment_H1"]) if not pd.isna(row["Recruitment_H1"]) else level.recruitment_h1
                    level.recruitment_h2 = float(row["Recruitment_H2"]) if not pd.isna(row["Recruitment_H2"]) else level.recruitment_h2
                    level.churn_h1 = float(row["Churn_H1"]) if not pd.isna(row["Churn_H1"]) else level.churn_h1
                    level.churn_h2 = float(row["Churn_H2"]) if not pd.isna(row["Churn_H2"]) else level.churn_h2
                    level.progression_h1 = float(row["Progression_H1"]) if not pd.isna(row["Progression_H1"]) else level.progression_h1
                    level.progression_h2 = float(row["Progression_H2"]) if not pd.isna(row["Progression_H2"]) else level.progression_h2
                    level.utr_h1 = float(row["UTR_H1"]) if not pd.isna(row["UTR_H1"]) else level.utr_h1
                    level.utr_h2 = float(row["UTR_H2"]) if not pd.isna(row["UTR_H2"]) else level.utr_h2
            elif isinstance(office.roles[role_name], type(office.roles["Operations"])) and not level_name:
                # Flat role
                role = office.roles[role_name]
                print(f"[IMPORT] Updating {office_name} {role_name} with FTE={row['FTE']}")
                role.total = int(row["FTE"]) if not pd.isna(row["FTE"]) else role.total
                role.price_h1 = float(row["Price_H1"]) if not pd.isna(row["Price_H1"]) else role.price_h1
                role.price_h2 = float(row["Price_H2"]) if not pd.isna(row["Price_H2"]) else role.price_h2
                role.salary_h1 = float(row["Salary_H1"]) if not pd.isna(row["Salary_H1"]) else role.salary_h1
                role.salary_h2 = float(row["Salary_H2"]) if not pd.isna(row["Salary_H2"]) else role.salary_h2
                role.recruitment_h1 = float(row["Recruitment_H1"]) if not pd.isna(row["Recruitment_H1"]) else role.recruitment_h1
                role.recruitment_h2 = float(row["Recruitment_H2"]) if not pd.isna(row["Recruitment_H2"]) else role.recruitment_h2
                role.churn_h1 = float(row["Churn_H1"]) if not pd.isna(row["Churn_H1"]) else role.churn_h1
                role.churn_h2 = float(row["Churn_H2"]) if not pd.isna(row["Churn_H2"]) else role.churn_h2
                role.progression_h1 = float(row["Progression_H1"]) if not pd.isna(row["Progression_H1"]) else role.progression_h1
                role.progression_h2 = float(row["Progression_H2"]) if not pd.isna(row["Progression_H2"]) else role.progression_h2
                role.utr_h1 = float(row["UTR_H1"]) if not pd.isna(row["UTR_H1"]) else role.utr_h1
                role.utr_h2 = float(row["UTR_H2"]) if not pd.isna(row["UTR_H2"]) else role.utr_h2
    print("[IMPORT] Completed updating office levers from Excel.")
    return {"status": "success", "rows": len(df)} 