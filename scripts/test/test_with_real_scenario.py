#!/usr/bin/env python3
"""
Script to test the simulation engine using a real scenario file with accurate input data.
Follows canonical data access patterns from docs/SIMULATION_DATA_STRUCTURES.md.
"""

import json
import sys
import os

# Add the backend/src to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend/src'))

from services.simulation_engine import SimulationEngine
from services.scenario_service import ScenarioService
from services.config_service import ConfigService

def test_with_real_scenario():
    """Test simulation engine with real scenario data."""
    
    # Load a real scenario file
    scenario_path = "data/scenarios/definitions/complete_working_scenario_no_progression.json"
    
    print("Loading real scenario file...")
    with open(scenario_path, 'r') as f:
        scenario_data = json.load(f)
    
    print(f"Scenario: {scenario_data['name']}")
    print(f"Time range: {scenario_data['time_range']['start_year']}-{scenario_data['time_range']['start_month']} to {scenario_data['time_range']['end_year']}-{scenario_data['time_range']['end_month']}")
    print(f"Office scope: {scenario_data['office_scope']}")
    
    # Extract recruitment and churn data
    baseline_input = scenario_data.get('baseline_input', {})
    global_data = baseline_input.get('global', {})
    
    recruitment_data = global_data.get('recruitment', {})
    churn_data = global_data.get('churn', {})
    
    print("\n=== RECRUITMENT DATA FROM SCENARIO ===")
    for role, levels in recruitment_data.items():
        print(f"\n{role}:")
        for level, months in levels.items():
            if months:  # Only show levels with data
                total_recruitment = sum(months.values())
                print(f"  {level}: {total_recruitment} total ({len(months)} months)")
                sample_months = dict(list(months.items())[:3])
                print(f"    Sample: {sample_months}")
    
    print("\n=== CHURN DATA FROM SCENARIO ===")
    for role, levels in churn_data.items():
        print(f"\n{role}:")
        for level, months in levels.items():
            if months:
                total_churn = sum(months.values())
                print(f"  {level}: {total_churn} total ({len(months)} months)")
                sample_months = dict(list(months.items())[:3])
                print(f"    Sample: {sample_months}")
    
    # Calculate totals
    total_recruitment = sum(
        sum(months.values()) 
        for role_data in recruitment_data.values() 
        for months in role_data.values() 
        if months
    )
    total_churn = sum(
        sum(months.values()) 
        for role_data in churn_data.values() 
        for months in role_data.values() 
        if months
    )
    print(f"\n=== SUMMARY ===")
    print(f"Total recruitment across all roles/levels/months: {total_recruitment}")
    print(f"Total churn across all roles/levels/months: {total_churn}")
    print(f"Net change (recruitment - churn): {total_recruitment - total_churn}")
    
    # Now run the simulation with this scenario
    print("\n=== RUNNING SIMULATION WITH REAL SCENARIO ===")
    try:
        # Initialize services (following docs/SIMULATION_DATA_STRUCTURES.md)
        config_service = ConfigService()
        scenario_service = ScenarioService(config_service)
        simulation_engine = SimulationEngine()
        
        # Extract time parameters from scenario
        time_range = scenario_data['time_range']
        start_year = time_range['start_year']
        start_month = time_range['start_month']
        end_year = time_range['end_year']
        end_month = time_range['end_month']
        
        # Resolve scenario data using scenario service
        print("Resolving scenario data...")
        resolved_data = scenario_service.resolve_scenario(scenario_data)
        print(f"Resolved data keys: {list(resolved_data.keys())}")
        print(f"Number of offices: {len(resolved_data['offices'])}")
        
        # Run simulation with resolved data
        print("Running simulation...")
        results = simulation_engine.run_simulation_with_offices(
            start_year=start_year,
            start_month=start_month,
            end_year=end_year,
            end_month=end_month,
            offices=resolved_data['offices'],
            progression_config=resolved_data['progression_config'],
            cat_curves=resolved_data['cat_curves']
        )
        
        print("Simulation completed successfully!")
        print(f"Results type: {type(results)}")
        
        # Canonical access pattern from docs/SIMULATION_DATA_STRUCTURES.md
        if 'years' in results:
            years = list(results['years'].keys())
            first_year = years[0]
            offices = list(results['years'][first_year]['offices'].keys())
            first_office = offices[0]
            office_data = results['years'][first_year]['offices'][first_office]
            print(f"\nSample year: {first_year}, office: {first_office}")
            roles = office_data['roles']
            if 'Consultant' in roles:
                consultant = roles['Consultant']
                print("\nConsultant FTE, Recruitment, Churn by Level and Month:")
                for level, months in consultant.items():
                    print(f"  Level {level}:")
                    for month_idx, month_data in enumerate(months):
                        fte = month_data.get('fte', None)
                        recruitment = month_data.get('recruitment', None)
                        churn = month_data.get('churn', None)
                        print(f"    Month {month_idx+1}: FTE={fte}, Recruitment={recruitment}, Churn={churn}")
                        if month_idx == 2:  # Only show first 3 months for brevity
                            break
            else:
                print("No Consultant role found in results.")
        else:
            print("No 'years' key in simulation results.")
        return results
    except Exception as e:
        print(f"Error running simulation: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_with_real_scenario() 