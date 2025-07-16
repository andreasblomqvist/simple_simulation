#!/usr/bin/env python3
"""
Debug FTE Zero Issue
====================

This script investigates why the simulation is returning FTE=0 for all years.
"""

import requests
import json
from datetime import datetime
from test_scenarios import get_scenario_by_name, validate_scenario

def debug_fte_zero():
    """Debug why FTE is zero in simulation results."""
    
    print("🔍 DEBUGGING FTE ZERO ISSUE")
    print("=" * 50)
    
    # Get a minimal scenario from our test scenarios
    scenario_definition = get_scenario_by_name("minimal")
    
    # Validate the scenario has everything the engine needs
    try:
        validate_scenario(scenario_definition)
        print("✅ Scenario validation passed")
    except ValueError as e:
        print(f"❌ Scenario validation failed: {e}")
        return
    
    print(f"📋 Scenario: {scenario_definition['name']}")
    print(f"📅 Time Range: {scenario_definition['time_range']}")
    print(f"🏢 Offices: {scenario_definition['office_scope']}")
    
    # Show input FTE
    baseline_input = scenario_definition['baseline_input']
    offices = baseline_input['offices']
    
    print(f"\n📊 INPUT FTE:")
    print("-" * 30)
    for office_name, office_data in offices.items():
        print(f"{office_name}: {office_data['total_fte']} FTE")
        roles = office_data['roles']
        for role_name, role_data in roles.items():
            if role_name == 'Operations':
                print(f"  {role_name}: {role_data['fte']} FTE")
            else:
                for level_name, level_data in role_data.items():
                    print(f"  {role_name}.{level_name}: {level_data['fte']} FTE")
    
    # Send request to backend
    print(f"\n🌐 Sending request to backend...")
    
    request_data = {
        "scenario_definition": scenario_definition
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/scenarios/run",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            results = response.json()
            print("✅ Simulation completed successfully!")
            
            # Debug the results structure
            print(f"\n🔍 RESULTS STRUCTURE:")
            print("-" * 30)
            print(f"Response keys: {list(results.keys())}")
            
            if 'results' in results:
                results_data = results['results']
                print(f"Results keys: {list(results_data.keys())}")
                
                # Check years data
                if 'years' in results_data:
                    years_data = results_data['years']
                    print(f"Years data type: {type(years_data)}")
                    print(f"Years data: {years_data}")
                    
                    if isinstance(years_data, dict):
                        for year_str, year_data in years_data.items():
                            print(f"Year {year_str}: {year_data}")
                            if isinstance(year_data, dict):
                                print(f"  Keys: {list(year_data.keys())}")
                                if 'fte' in year_data:
                                    print(f"  FTE: {year_data['fte']}")
                
                # Check if there are offices data
                if 'offices' in results_data:
                    offices_data = results_data['offices']
                    print(f"Offices data type: {type(offices_data)}")
                    if isinstance(offices_data, dict):
                        print(f"Office names: {list(offices_data.keys())}")
                        for office_name, office_data in offices_data.items():
                            print(f"Office {office_name}: {type(office_data)}")
                            if isinstance(office_data, dict):
                                print(f"  Keys: {list(office_data.keys())}")
                
                # Check if there are other result structures
                for key, value in results_data.items():
                    if key not in ['years', 'offices']:
                        print(f"Other key '{key}': {type(value)}")
                        if isinstance(value, dict):
                            print(f"  Keys: {list(value.keys())}")
            
            # Try to find FTE data in different possible locations
            print(f"\n🔍 SEARCHING FOR FTE DATA:")
            print("-" * 30)
            
            def search_for_fte(data, path=""):
                """Recursively search for FTE data in the response."""
                if isinstance(data, dict):
                    for key, value in data.items():
                        current_path = f"{path}.{key}" if path else key
                        if key.lower() == 'fte':
                            print(f"Found FTE at {current_path}: {value}")
                        elif isinstance(value, (dict, list)):
                            search_for_fte(value, current_path)
                elif isinstance(data, list):
                    for i, item in enumerate(data):
                        current_path = f"{path}[{i}]"
                        search_for_fte(item, current_path)
            
            search_for_fte(results)
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    debug_fte_zero() 