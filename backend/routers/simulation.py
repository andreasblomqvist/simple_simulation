from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional
from backend.src.services.simulation_engine import SimulationEngine

router = APIRouter(prefix="/simulation", tags=["simulation"])

# Global engine instance - will be injected from main
engine: SimulationEngine = None

def set_engine(simulation_engine: SimulationEngine):
    """Set the global engine instance"""
    global engine
    engine = simulation_engine

class SimulationRequest(BaseModel):
    start_year: int
    start_month: int  # 1-12
    end_year: int
    end_month: int    # 1-12
    price_increase: float
    salary_increase: float
    unplanned_absence: Optional[float] = 0.05  # 5% default
    hy_working_hours: Optional[float] = 166.4  # Monthly working hours
    other_expense: Optional[float] = 100000.0  # Monthly other expenses
    # Advanced: office overrides for FTE, level, and operations params
    office_overrides: Optional[Dict[str, Dict[str, Any]]] = None

def _build_lever_plan(office_overrides: Dict[str, Dict[str, Any]]) -> Dict:
    """Convert office overrides to lever plan format"""
    lever_plan = {}
    for office_name, overrides in office_overrides.items():
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
    return lever_plan

@router.post("/run")
def run_simulation(req: SimulationRequest):
    """Run a simulation with the given parameters"""
    lever_plan = None
    if req.office_overrides:
        lever_plan = _build_lever_plan(req.office_overrides)
    
    # Run the simulation
    results = engine.run_simulation(
        start_year=req.start_year,
        start_month=req.start_month,
        end_year=req.end_year,
        end_month=req.end_month,
        price_increase=req.price_increase,
        salary_increase=req.salary_increase,
        lever_plan=lever_plan
    )
    
    # Calculate simulation duration in months
    duration_months = (req.end_year - req.start_year) * 12 + (req.end_month - req.start_month) + 1
    
    # Calculate and add KPIs to results
    results_with_kpis = engine.calculate_kpis_for_simulation(
        results,
        duration_months,
        req.unplanned_absence,
        req.other_expense
    )
    
    return results_with_kpis 