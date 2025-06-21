from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.cache_service import simulation_cache
from datetime import datetime

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
    other_expense: Optional[float] = 19000000.0  # Monthly other expenses
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
def run_simulation(params: SimulationRequest):
    """Run a simulation with the given parameters"""
    if not engine:
        raise HTTPException(status_code=500, detail="Simulation engine not initialized")
    
    # DEBUG: Show raw parameter values
    print(f"\n🔍 [DEBUG] RAW PARAMETERS RECEIVED:")
    print(f"[DEBUG] Raw price_increase: {params.price_increase} (type: {type(params.price_increase)})")
    print(f"[DEBUG] Raw salary_increase: {params.salary_increase} (type: {type(params.salary_increase)})")
    print(f"[DEBUG] Expected for 2%: 0.02")
    
    print(f"\n🚀 [SIMULATION] =================== NEW SIMULATION RUN ===================")
    print(f"[SIMULATION] 📅 Timeframe: {params.start_year}-{params.start_month:02d} to {params.end_year}-{params.end_month:02d}")
    print(f"[SIMULATION] 📊 Economic Parameters:")
    print(f"[SIMULATION]   💰 Price Increase: {params.price_increase:.1%}")
    print(f"[SIMULATION]   💵 Salary Increase: {params.salary_increase:.1%}")
    print(f"[SIMULATION]   🕒 Working Hours/Month: {params.hy_working_hours}")
    print(f"[SIMULATION]   😴 Unplanned Absence: {params.unplanned_absence:.1%}")
    print(f"[SIMULATION]   📋 Other Expense: {params.other_expense:,} SEK/month")
    
    # Parse office overrides (lever plan)
    lever_plan = None
    if params.office_overrides:
        lever_plan = {}
        total_overrides = 0
        print(f"[SIMULATION] 🎛️  Office Overrides Applied:")
        for office_name, office_levers in params.office_overrides.items():
            lever_plan[office_name] = {}
            office_override_count = 0
            for lever_key, lever_value in office_levers.items():
                # Parse lever key like "recruitment_AM" -> role="Consultant", level="AM", attribute="recruitment"
                if '_' in lever_key:
                    parts = lever_key.split('_')
                    if len(parts) == 2:
                        attribute, level = parts
                        # Default to Consultant role for level-based overrides
                        role = "Consultant"
                        
                        if role not in lever_plan[office_name]:
                            lever_plan[office_name][role] = {}
                        if level not in lever_plan[office_name][role]:
                            lever_plan[office_name][role][level] = {}
                        
                        # Apply to all 12 months
                        for month in range(1, 13):
                            lever_plan[office_name][role][level][f"{attribute}_{month}"] = lever_value
                        
                        print(f"[SIMULATION]     📍 {office_name} → {role} {level} {attribute}: {lever_value:.1%}")
                        office_override_count += 1
                        total_overrides += 1
            
            if office_override_count == 0:
                print(f"[SIMULATION]     📍 {office_name} → No overrides")
        
        print(f"[SIMULATION] 🎛️  Total Lever Overrides: {total_overrides}")
    else:
        print(f"[SIMULATION] 🎛️  Office Overrides: None (using default config)")
    
    print(f"[SIMULATION] ================================================================\n")
    
    try:
        # CRITICAL: Reset simulation state before each run to prevent accumulation
        print(f"🔄 [SIMULATION] Resetting engine state for fresh simulation...")
        engine.reset_simulation_state()
        print(f"✅ [SIMULATION] Engine state cleared successfully")
        
        # Run the simulation
        results = engine.run_simulation(
            start_year=params.start_year,
            start_month=params.start_month,
            end_year=params.end_year,
            end_month=params.end_month,
            price_increase=params.price_increase,
            salary_increase=params.salary_increase,
            lever_plan=lever_plan
        )
        
        # Calculate simulation duration in months
        start_date = datetime(params.start_year, params.start_month, 1)
        end_date = datetime(params.end_year, params.end_month, 1)
        simulation_duration_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
        
        # Calculate KPIs
        results_with_kpis = engine.calculate_kpis_for_simulation(
            results,
            simulation_duration_months,
            params.unplanned_absence,
            params.other_expense
        )
        
        print(f"✅ [SIMULATION] Completed successfully! Duration: {simulation_duration_months} months")
        print(f"[SIMULATION] Years in results: {list(results_with_kpis['years'].keys())}")
        print(f"[SIMULATION] =================== SIMULATION COMPLETE ===================\n")
        
        return results_with_kpis
    
    except Exception as e:
        print(f"❌ [SIMULATION] Failed with error: {str(e)}")
        print(f"[SIMULATION] =================== SIMULATION FAILED ===================\n")
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

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

@router.post("/reset")
def reset_simulation():
    """Reset the simulation engine state for fresh simulation runs"""
    if not engine:
        raise HTTPException(status_code=500, detail="Simulation engine not initialized")
    
    # Reset the simulation state
    engine.reset_simulation_state()
    
    # Clear all cached data
    simulation_cache.clear_all()
    
    return {"message": "Simulation state reset successfully"}

@router.get("/config/validation")
def validate_configuration():
    """Validate configuration integrity and return checksum and completeness report"""
    if not engine:
        raise HTTPException(status_code=500, detail="Simulation engine not initialized")
    
    # Check if offices are initialized
    if not engine.offices:
        # Initialize offices temporarily for validation
        engine._initialize_offices()
        engine._initialize_roles_with_levers(None)
    
    from backend.src.services.simulation_engine import calculate_configuration_checksum, validate_configuration_completeness
    
    try:
        # Calculate checksum and validation report
        config_checksum = calculate_configuration_checksum(engine.offices)
        config_report = validate_configuration_completeness(engine.offices)
        
        return {
            "checksum": config_checksum,
            "validation": config_report,
            "timestamp": datetime.now().isoformat(),
            "status": "valid" if not config_report['missing_data'] else "incomplete",
            "summary": {
                "total_offices": config_report['total_offices'],
                "total_roles": config_report['total_roles'],
                "total_levels": config_report['total_levels'],
                "total_fte": config_report['total_fte'],
                "missing_data_count": len(config_report['missing_data'])
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration validation failed: {str(e)}")

@router.get("/config/checksum")
def get_configuration_checksum():
    """Get just the configuration checksum for quick integrity checks"""
    if not engine:
        raise HTTPException(status_code=500, detail="Simulation engine not initialized")
    
    # Check if offices are initialized
    if not engine.offices:
        # Initialize offices temporarily for checksum
        engine._initialize_offices()
        engine._initialize_roles_with_levers(None)
    
    from backend.src.services.simulation_engine import calculate_configuration_checksum
    
    try:
        config_checksum = calculate_configuration_checksum(engine.offices)
        total_fte = sum(
            sum(
                getattr(level, 'total', 0) 
                for role_data in office.roles.values() 
                for level in (role_data.values() if isinstance(role_data, dict) else [role_data])
            )
            for office in engine.offices.values()
        )
        
        return {
            "checksum": config_checksum,
            "total_offices": len(engine.offices),
            "total_fte": total_fte,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Checksum calculation failed: {str(e)}") 