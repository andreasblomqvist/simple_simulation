from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.cache_service import simulation_cache

router = APIRouter(prefix="/simulation", tags=["simulation"])

# Global engine instance - will be injected from main
engine: SimulationEngine = None

def set_engine(simulation_engine: SimulationEngine):
    """Set the global engine instance"""
    global engine
    engine = simulation_engine

class SimulationRequest(BaseModel):
    start_year: int
    start_month: int = Field(ge=1, le=12)  # 1-12
    end_year: int
    end_month: int = Field(ge=1, le=12)    # 1-12
    price_increase: float
    salary_increase: float
    unplanned_absence: Optional[float] = 0.05  # 5% default
    hy_working_hours: Optional[float] = 166.4  # Monthly working hours
    other_expense: Optional[float] = 100000.0  # Monthly other expenses
    # Advanced: office overrides for FTE, level, and operations params
    office_overrides: Optional[Dict[str, Dict[str, Any]]] = None

class YearNavigationRequest(BaseModel):
    """Request for year-specific data"""
    year: int
    include_monthly_data: Optional[bool] = False

class YearComparisonRequest(BaseModel):
    """Request for comparing two years"""
    year1: int
    year2: int
    include_monthly_data: Optional[bool] = False

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
    
    # Invalidate cache for all years in the simulation
    for year in range(req.start_year, req.end_year + 1):
        simulation_cache.invalidate_year(year)
    
    return results_with_kpis

@router.post("/year/{year}")
def get_year_data(year: int, req: YearNavigationRequest):
    """Get data for a specific year"""
    if not engine:
        raise HTTPException(status_code=500, detail="Simulation engine not initialized")
    
    # Try to get data from cache first
    cached_data = simulation_cache.get_year_data(year, req.include_monthly_data)
    if cached_data is not None:
        return cached_data
    
    # Get the simulation results
    results = engine.get_simulation_results()
    if not results or 'years' not in results:
        raise HTTPException(status_code=404, detail="No simulation results found")
    
    # Get the requested year's data
    year_str = str(year)
    if year_str not in results['years']:
        raise HTTPException(status_code=404, detail=f"No data found for year {year}")
    
    year_data = results['years'][year_str]
    
    # If monthly data is not requested, remove it to reduce response size
    if not req.include_monthly_data:
        for office in year_data['offices'].values():
            for role_name, role_data in office['levels'].items():
                if isinstance(role_data, dict):
                    for level_name in role_data:
                        # Keep only the last month's data
                        role_data[level_name] = [role_data[level_name][-1]]
                else:
                    # Keep only the last month's data
                    office['levels'][role_name] = [role_data[-1]]
            
            # Keep only the last month's data for journeys
            for journey in office['journeys'].values():
                journey[:] = [journey[-1]]
            
            # Keep only the last month's data for metrics
            office['metrics'] = [office['metrics'][-1]]
    
    # Cache the processed data
    simulation_cache.set_year_data(year, year_data, req.include_monthly_data)
    
    return year_data

@router.post("/years/compare")
def compare_years(req: YearComparisonRequest):
    """Compare data between two years"""
    if not engine:
        raise HTTPException(status_code=500, detail="Simulation engine not initialized")
    
    # Try to get comparison from cache first
    cached_comparison = simulation_cache.get_comparison(
        req.year1,
        req.year2,
        req.include_monthly_data
    )
    if cached_comparison is not None:
        return cached_comparison
    
    # Get the simulation results
    results = engine.get_simulation_results()
    if not results or 'years' not in results:
        raise HTTPException(status_code=404, detail="No simulation results found")
    
    # Get data for both years
    year1_str = str(req.year1)
    year2_str = str(req.year2)
    
    if year1_str not in results['years'] or year2_str not in results['years']:
        raise HTTPException(status_code=404, detail="One or both years not found in simulation results")
    
    year1_data = results['years'][year1_str]
    year2_data = results['years'][year2_str]
    
    # Calculate year-over-year changes
    comparison = {
        'year1': year1_data,
        'year2': year2_data,
        'changes': {
            'total_fte': {
                'absolute': year2_data['summary']['total_fte'] - year1_data['summary']['total_fte'],
                'percentage': (
                    (year2_data['summary']['total_fte'] - year1_data['summary']['total_fte']) /
                    year1_data['summary']['total_fte'] * 100
                ) if year1_data['summary']['total_fte'] > 0 else 0.0
            },
            'revenue': {
                'absolute': year2_data['summary']['total_revenue'] - year1_data['summary']['total_revenue'],
                'percentage': (
                    (year2_data['summary']['total_revenue'] - year1_data['summary']['total_revenue']) /
                    year1_data['summary']['total_revenue'] * 100
                ) if year1_data['summary']['total_revenue'] > 0 else 0.0
            },
            'margin': {
                'absolute': year2_data['summary']['average_margin'] - year1_data['summary']['average_margin'],
                'percentage': (
                    (year2_data['summary']['average_margin'] - year1_data['summary']['average_margin']) /
                    year1_data['summary']['average_margin'] * 100
                ) if year1_data['summary']['average_margin'] > 0 else 0.0
            }
        }
    }
    
    # If monthly data is not requested, remove it to reduce response size
    if not req.include_monthly_data:
        for year_data in [year1_data, year2_data]:
            for office in year_data['offices'].values():
                for role_name, role_data in office['levels'].items():
                    if isinstance(role_data, dict):
                        for level_name in role_data:
                            # Keep only the last month's data
                            role_data[level_name] = [role_data[level_name][-1]]
                    else:
                        # Keep only the last month's data
                        office['levels'][role_name] = [role_data[-1]]
                
                # Keep only the last month's data for journeys
                for journey in office['journeys'].values():
                    journey[:] = [journey[-1]]
                
                # Keep only the last month's data for metrics
                office['metrics'] = [office['metrics'][-1]]
    
    # Cache the comparison
    simulation_cache.set_comparison(
        req.year1,
        req.year2,
        comparison,
        req.include_monthly_data
    )
    
    return comparison

@router.get("/years")
def get_available_years():
    """Get list of available years in the simulation results"""
    if not engine:
        raise HTTPException(status_code=500, detail="Simulation engine not initialized")
    
    # Get the simulation results
    results = engine.get_simulation_results()
    if not results or 'years' not in results:
        raise HTTPException(status_code=404, detail="No simulation results found")
    
    # Return sorted list of years
    return sorted(results['years'].keys(), key=int) 