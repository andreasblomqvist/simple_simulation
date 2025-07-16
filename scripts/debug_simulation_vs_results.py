#!/usr/bin/env python3
"""
Debug script to compare simulation engine calculations vs scenario service results.
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.src.services.scenario_service import ScenarioService
from backend.src.services.config_service import config_service
from backend.src.services.scenario_models import ScenarioRequest

def debug_simulation_vs_results(scenario_id):
    """Debug the difference between simulation engine and scenario service results."""
    
    print(f"🔍 Debugging Simulation vs Results for Scenario: {scenario_id}")
    print("=" * 70)
    
    # Initialize services
    scenario_service = ScenarioService(config_service)
    
    # Load the scenario definition
    scenario_path = f"data/scenarios/definitions/{scenario_id}.json"
    
    if not os.path.exists(scenario_path):
        print(f"❌ Scenario file not found: {scenario_path}")
        return False
    
    with open(scenario_path, 'r') as f:
        scenario_data = json.load(f)
    
    print(f"📋 Scenario Name: {scenario_data.get('name', 'Unknown')}")
    
    # Create scenario request
    request = ScenarioRequest(scenario_id=scenario_id)
    
    print("\n🚀 Running scenario...")
    
    # Run the scenario
    response = scenario_service.run_scenario(request)
    
    if response.status != "success":
        print(f"❌ Scenario failed: {response.error_message}")
        return False
    
    print(f"✅ Scenario completed successfully")
    
    # Extract results
    results = response.results
    
    print("\n📊 Results Analysis:")
    print("=" * 70)
    
    # Show office-level results from scenario service
    if 'years' in results:
        years = results['years']
        print(f"🏢 Office Results from Scenario Service:")
        for year, year_data in years.items():
            print(f"  Year {year}:")
            offices = year_data.get('offices', {})
            total_scenario_fte = 0
            for office_name, office_data in offices.items():
                total_fte = office_data.get('total_fte', 0)
                total_scenario_fte += total_fte
                print(f"    {office_name}: {total_fte:,.1f} FTE")
            print(f"    Total: {total_scenario_fte:,.1f} FTE")
    
    # Now let's check what the simulation engine actually calculated
    print(f"\n🔧 Simulation Engine State:")
    print("=" * 70)
    
    # Get the simulation engine from the scenario service
    # This is a bit hacky but we need to access the engine state
    try:
        # Try to access the engine state from the scenario service
        if hasattr(scenario_service, '_engine') and scenario_service._engine:
            engine = scenario_service._engine
            print(f"Engine offices count: {len(engine.offices)}")
            
            total_engine_fte = 0
            for office_name, office in engine.offices.items():
                total_engine_fte += office.total_fte
                print(f"  {office_name}: {office.total_fte} FTE")
            print(f"  Total Engine FTE: {total_engine_fte}")
            
            # Check if there's a mismatch
            if 'years' in results:
                years = results['years']
                for year, year_data in years.items():
                    offices = year_data.get('offices', {})
                    total_scenario_fte = sum(office_data.get('total_fte', 0) for office_data in offices.values())
                    print(f"\n  Year {year} Comparison:")
                    print(f"    Scenario Service: {total_scenario_fte:,.1f} FTE")
                    print(f"    Engine State: {total_engine_fte:,.1f} FTE")
                    print(f"    Difference: {total_engine_fte - total_scenario_fte:,.1f} FTE")
        else:
            print("❌ Could not access simulation engine state")
    except Exception as e:
        print(f"❌ Error accessing engine state: {e}")
    
    print("\n" + "=" * 70)
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 debug_simulation_vs_results.py <scenario_id>")
        print("Example: python3 debug_simulation_vs_results.py f5f26bc5-3830-4f64-ba53-03b58ae72353")
        sys.exit(1)
    
    scenario_id = sys.argv[1]
    success = debug_simulation_vs_results(scenario_id)
    sys.exit(0 if success else 1) 