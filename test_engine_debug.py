#!/usr/bin/env python3
"""
Debug script to test the simulation engine and see what data structure it produces
"""

from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.kpi.kpi_models import EconomicParameters

def test_engine_debug():
    """Test the simulation engine to see what data structure it produces"""
    
    print("=== Testing Simulation Engine Data Structure ===\n")
    
    # Initialize engine
    engine = SimulationEngine()
    
    # Create economic parameters
    economic_params = EconomicParameters(
        unplanned_absence=0.05,
        other_expense=19000000.0,
        employment_cost_rate=0.40,
        working_hours_per_month=166.4
    )
    
    # Run a simple simulation
    print("Running simulation...")
    results = engine.run_simulation(
        start_year=2024,
        start_month=1,
        end_year=2025,
        end_month=1,
        price_increase=0.05,
        salary_increase=0.03,
        economic_params=economic_params
    )
    
    print(f"\nSimulation completed. Results structure:")
    print(f"Keys in results: {list(results.keys())}")
    
    if 'years' in results:
        years = results['years']
        print(f"Years available: {list(years.keys())}")
        
        for year, year_data in years.items():
            print(f"\nYear {year} structure:")
            print(f"  Keys: {list(year_data.keys())}")
            print(f"  Total FTE: {year_data.get('total_fte', 'N/A')}")
            print(f"  Total Revenue: {year_data.get('total_revenue', 'N/A')}")
            print(f"  EBITDA: {year_data.get('ebitda', 'N/A')}")
            
            if 'offices' in year_data:
                offices = year_data['offices']
                print(f"  Offices: {list(offices.keys())}")
                
                # Check first office structure
                if offices:
                    first_office = list(offices.values())[0]
                    print(f"  First office structure: {list(first_office.keys())}")
                    if 'levels' in first_office:
                        levels = first_office['levels']
                        print(f"  First office levels: {list(levels.keys())}")
    
    print("\n=== End of Test ===")

if __name__ == "__main__":
    test_engine_debug() 