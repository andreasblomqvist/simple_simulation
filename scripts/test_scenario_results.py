#!/usr/bin/env python3
"""
Test Scenario Results
====================

Simple script to test scenarios and show clear FTE results.
"""

import requests
import json
from test_scenarios import get_scenario_by_name, validate_scenario

def test_scenario(scenario_name):
    """Test a scenario and show clear results."""
    
    print(f"🧪 Testing scenario: {scenario_name}")
    print("=" * 50)
    
    # Get the scenario
    scenario_definition = get_scenario_by_name(scenario_name)
    
    # Validate the scenario
    try:
        validate_scenario(scenario_definition)
        print("✅ Scenario validation passed")
    except ValueError as e:
        print(f"❌ Scenario validation failed: {e}")
        return
    
    # Send request to backend
    print(f"🌐 Sending request to backend...")
    
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
            
            # Extract and display FTE results
            display_fte_results(results, scenario_definition)
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def display_fte_results(results, scenario_definition):
    """Display FTE results in a clear format."""
    
    print(f"\n📊 FTE RESULTS:")
    print("=" * 50)
    
    # Get the office scope from the scenario
    office_scope = scenario_definition.get('office_scope', [])
    
    # Extract years data
    years_data = results.get('results', {}).get('years', {})
    
    if not years_data:
        print("❌ No years data found in results")
        return
    
    # For each year
    for year_str, year_data in years_data.items():
        print(f"\n📅 YEAR {year_str}:")
        print("-" * 30)
        
        # Check if we have offices data
        offices_data = year_data.get('offices', {})
        
        if not offices_data:
            print("❌ No offices data found for this year")
            continue
        
        # For each office in scope
        for office_name in office_scope:
            if office_name in offices_data:
                office_data = offices_data[office_name]
                print(f"\n🏢 {office_name}:")
                
                # Check roles structure
                roles_data = office_data.get('roles', {})
                
                if roles_data:
                    # Calculate total FTE for this office
                    total_fte = 0
                    
                    for role_name, role_data in roles_data.items():
                        if isinstance(role_data, dict):
                            # Handle levels within roles
                            for level_name, level_data in role_data.items():
                                if isinstance(level_data, list):
                                    # Get the last month's FTE (most recent)
                                    if level_data:
                                        last_month_fte = level_data[-1].get('fte', 0)
                                        total_fte += last_month_fte
                                        print(f"  {role_name}.{level_name}: {last_month_fte:.1f} FTE")
                                elif isinstance(level_data, dict) and 'fte' in level_data:
                                    # Direct FTE value
                                    fte = level_data['fte']
                                    total_fte += fte
                                    print(f"  {role_name}.{level_name}: {fte:.1f} FTE")
                    
                    print(f"  📈 Total: {total_fte:.1f} FTE")
                else:
                    print("  ❌ No roles data found")
            else:
                print(f"🏢 {office_name}: ❌ Not found in results")

def main():
    """Main function to test different scenarios."""
    
    print("🚀 SIMPLE SIMULATION TEST")
    print("=" * 50)
    
    # Test minimal scenario
    test_scenario("minimal")
    
    print(f"\n" + "=" * 50)
    print("✅ Test completed!")

if __name__ == "__main__":
    main() 