from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.kpi import KPIService, EconomicParameters
from backend.src.services.cache_service import simulation_cache
from backend.src.services.excel_export_service import ExcelExportService
from datetime import datetime
from backend.src.services.config_service import config_service
import io
import tempfile
import os

router = APIRouter(prefix="/simulation", tags=["simulation"])

# Create engine instance (no injection needed with JSON file approach)
engine = SimulationEngine()

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
    employment_cost_rate: Optional[float] = 0.40  # 40% overhead on salary costs
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
    print(f"[SIMULATION]   🏭 Employment Cost Rate: {params.employment_cost_rate:.1%}")
    print(f"[SIMULATION]   📋 Other Expense: {params.other_expense:,} SEK/month")
    
    # Parse office overrides (lever plan)
    lever_plan = None
    if params.office_overrides:
        office_levers = {}
        total_overrides = 0
        print(f"[SIMULATION] 🎛️  Office Overrides Applied:")
        for office_name, office_lever_data in params.office_overrides.items():
            office_levers[office_name] = {}
            office_override_count = 0
            for lever_key, lever_value in office_lever_data.items():
                # Parse lever key like "recruitment_AM" -> role="Consultant", level="AM", attribute="recruitment"
                if '_' in lever_key:
                    parts = lever_key.split('_')
                    if len(parts) == 2:
                        attribute, level = parts
                        # Default to Consultant role for level-based overrides
                        role = "Consultant"
                        
                        if role not in office_levers[office_name]:
                            office_levers[office_name][role] = {}
                        if level not in office_levers[office_name][role]:
                            office_levers[office_name][role][level] = {}
                        
                        # Apply to all 12 months
                        for month in range(1, 13):
                            office_levers[office_name][role][level][f"{attribute}_{month}"] = lever_value
                        
                        print(f"[SIMULATION]     📍 {office_name} → {role} {level} {attribute}: {lever_value:.1%}")
                        office_override_count += 1
                        total_overrides += 1
            
            if office_override_count == 0:
                print(f"[SIMULATION]     📍 {office_name} → No overrides")
        
        # Wrap office levers in the expected structure
        lever_plan = {
            "offices": office_levers
        }
        
        print(f"[SIMULATION] 🎛️  Total Lever Overrides: {total_overrides}")
    else:
        print(f"[SIMULATION] 🎛️  Office Overrides: None (using default config)")
    
    print(f"[SIMULATION] ================================================================\n")
    
    try:
        # CRITICAL: Reset simulation state before each run to prevent accumulation
        print(f"🔄 [SIMULATION] Resetting engine state for fresh simulation...")
        engine.reset_simulation_state()
        print(f"✅ [SIMULATION] Engine state cleared successfully")
        
        # Create economic parameters from frontend request
        economic_params = EconomicParameters.from_simulation_request(params)
        print(f"[SIMULATION] Economic parameters created: {economic_params}")
        
        # Run the simulation
        results = engine.run_simulation(
            start_year=params.start_year,
            start_month=params.start_month,
            end_year=params.end_year,
            end_month=params.end_month,
            price_increase=params.price_increase,
            salary_increase=params.salary_increase,
            lever_plan=lever_plan,
            economic_params=economic_params
        )
        
        # Calculate simulation duration in months
        start_date = datetime(params.start_year, params.start_month, 1)
        end_date = datetime(params.end_year, params.end_month, 1)
        simulation_duration_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
        
        # Calculate KPIs using the KPI service (separation of concerns)
        try:
            kpi_service = KPIService(economic_params=economic_params)
            
            # Calculate KPIs for the simulation
            kpi_results = kpi_service.calculate_all_kpis(
                results,
                simulation_duration_months,
                economic_params=economic_params
            )
            
            # Convert dataclasses to dicts for JSON serialization
            def to_dict(data):
                if hasattr(data, '__dataclass_fields__'):
                    return {k: to_dict(getattr(data, k)) for k in data.__dataclass_fields__}
                elif isinstance(data, dict):
                    return {k: to_dict(v) for k, v in data.items()}
                elif isinstance(data, list):
                    return [to_dict(i) for i in data]
                else:
                    return data
            
            results['kpis'] = to_dict(kpi_results)
            print(f"✅ [SIMULATION] KPIs calculated successfully")
            
        except Exception as e:
            print(f"❌ [SIMULATION] KPI calculation failed: {e}")
            results['kpis'] = None
        
        print(f"✅ [SIMULATION] Completed successfully! Duration: {simulation_duration_months} months")
        print(f"[SIMULATION] Years in results: {list(results['years'].keys())}")
        print(f"[SIMULATION] =================== SIMULATION COMPLETE ===================\n")
        
        return results
    
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

@router.get("/years/{year}/kpis")
def get_year_kpis(year: int, unplanned_absence: float = 0.05, other_expense: float = 19000000.0):
    """Get KPIs for a specific year"""
    if not engine:
        raise HTTPException(status_code=500, detail="Simulation engine not initialized")
    
    # Get the simulation results
    results = engine.get_simulation_results()
    if not results or 'years' not in results:
        raise HTTPException(status_code=404, detail="No simulation results found")
    
    # Check if the year exists
    year_str = str(year)
    if year_str not in results['years']:
        raise HTTPException(status_code=404, detail=f"No data found for year {year}")
    
    try:
        # Calculate KPIs for the specific year
        year_kpis = engine.kpi_service.calculate_kpis_for_year(
            results,
            year_str,
            12,  # Always use 12 months for annual comparison
            unplanned_absence,
            other_expense
        )
        
        return {
            "financial": year_kpis.financial.__dict__,
            "growth": year_kpis.growth.__dict__,
            "journeys": year_kpis.journeys.__dict__,
            "year": year_str
        }
        
    except Exception as e:
        print(f"❌ [KPI] Failed to calculate KPIs for year {year}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"KPI calculation failed: {str(e)}")

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

@router.post("/export/excel")
def export_simulation_to_excel(params: SimulationRequest):
    """Export simulation results to Excel format"""
    if not engine:
        raise HTTPException(status_code=500, detail="Simulation engine not initialized")
    
    try:
        print(f"🚀 [EXPORT] Starting Excel export for simulation...")
        print(f"[EXPORT] Parameters: {params.start_year}-{params.start_month} to {params.end_year}-{params.end_month}")
        
        # Parse office overrides (lever plan) - same as simulation run
        lever_plan = None
        if params.office_overrides:
            office_levers = {}
            for office_name, office_lever_data in params.office_overrides.items():
                office_levers[office_name] = {}
                for lever_key, lever_value in office_lever_data.items():
                    if '_' in lever_key:
                        parts = lever_key.split('_')
                        if len(parts) == 2:
                            attribute, level = parts
                            role = "Consultant"
                            
                            if role not in office_levers[office_name]:
                                office_levers[office_name][role] = {}
                            if level not in office_levers[office_name][role]:
                                office_levers[office_name][role][level] = {}
                            
                            for month in range(1, 13):
                                office_levers[office_name][role][level][f"{attribute}_{month}"] = lever_value
            
            # Wrap office levers in the expected structure
            lever_plan = {
                "offices": office_levers
            }
        
        # Reset engine state for fresh simulation
        engine.reset_simulation_state()
        
        # Create economic parameters from frontend request  
        economic_params = EconomicParameters.from_simulation_request(params)
        
        # Run the simulation
        results = engine.run_simulation(
            start_year=params.start_year,
            start_month=params.start_month,
            end_year=params.end_year,
            end_month=params.end_month,
            price_increase=params.price_increase,
            salary_increase=params.salary_increase,
            lever_plan=lever_plan,
            economic_params=economic_params
        )
        
        # Calculate simulation duration in months
        start_date = datetime(params.start_year, params.start_month, 1)
        end_date = datetime(params.end_year, params.end_month, 1)
        simulation_duration_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
        
        # Calculate KPIs for the export using the KPI service
        try:
            from backend.src.services.kpi import KPIService
            kpi_service = KPIService()
            
            kpi_results = kpi_service.calculate_all_kpis(
                results,
                simulation_duration_months,
                params.unplanned_absence,
                params.other_expense
            )
            
            # Convert dataclasses to dicts for JSON serialization
            def to_dict(data):
                if hasattr(data, '__dataclass_fields__'):
                    return {k: to_dict(getattr(data, k)) for k in data.__dataclass_fields__}
                elif isinstance(data, dict):
                    return {k: to_dict(v) for k, v in data.items()}
                elif isinstance(data, list):
                    return [to_dict(i) for i in data]
                else:
                    return data
            
            results_with_kpis = results.copy()
            results_with_kpis['kpis'] = to_dict(kpi_results)
            
        except Exception as e:
            print(f"❌ [EXPORT] KPI calculation failed: {e}")
            results_with_kpis = results
            results_with_kpis['kpis'] = {}
        
        print(f"✅ [EXPORT] Simulation completed, generating Excel file...")
        
        # Create Excel export service
        export_service = ExcelExportService()
        
        # Create temporary file for Excel export
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Generate Excel file
        export_service.export_simulation_results(
            results_with_kpis,
            results_with_kpis.get('kpis', {}),
            temp_path
        )
        
        # Read the Excel file into memory
        with open(temp_path, 'rb') as excel_file:
            excel_content = excel_file.read()
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"SimulationExport_{timestamp}.xlsx"
        
        print(f"✅ [EXPORT] Excel file generated successfully: {filename} ({len(excel_content)} bytes)")
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(excel_content),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        print(f"❌ [EXPORT] Excel export failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Excel export failed: {str(e)}") 