from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import sys
sys.path.append('./simple_simulation/src')
from services.simulation_engine import SimulationEngine, HalfYear

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimulationRequest(BaseModel):
    start_year: int
    start_half: str  # "H1" or "H2"
    end_year: int
    end_half: str    # "H1" or "H2"
    price_increase: float
    salary_increase: float
    # Optionally: office overrides, scenario configs, etc.
    office_overrides: Optional[Dict[str, Dict[str, Any]]] = None

@app.post("/simulate")
def run_simulation(req: SimulationRequest):
    engine = SimulationEngine()
    # Optionally apply office_overrides here
    if req.office_overrides:
        for office_name, overrides in req.office_overrides.items():
            office = engine.offices.get(office_name)
            if not office:
                continue
            for level_name, level_data in overrides.get("levels", {}).items():
                for key, value in level_data.items():
                    setattr(office.levels[level_name], key, value)
            if "operations" in overrides:
                for key, value in overrides["operations"].items():
                    setattr(office.operations, key, value)
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
    engine = SimulationEngine()
    return [
        {
            "name": office.name,
            "total_fte": office.total_fte,
            "journey": office.journey.value,
            "levels": {
                level_name: {
                    "total": level.total,
                    "price": level.price,
                    "salary": level.salary
                }
                for level_name, level in office.levels.items()
            },
            "operations": {
                "total": office.operations.total,
                "price": office.operations.price,
                "salary": office.operations.salary
            },
            "metrics": [{
                "journey_percentages": office.calculate_journey_percentages(),
                "non_debit_ratio": office.calculate_non_debit_ratio(),
                "growth": 0.0,  # Initial growth is 0
                "recruitment": 0,  # Initial recruitment is 0
                "churn": 0  # Initial churn is 0
            }]
        }
        for office in engine.offices.values()
    ] 