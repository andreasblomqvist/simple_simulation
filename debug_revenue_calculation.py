#!/usr/bin/env python3
"""
Debug script to examine why revenue calculation is producing unrealistic numbers
"""

import json
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from test_scenarios import get_complete_scenario

def debug_revenue_calculation():
    """Debug why revenue calculation is producing unrealistic numbers"""
    
    # Get the complete scenario with proper global data distribution
    scenario = get_complete_scenario()
    
    print("=== COMPLETE SCENARIO ANALYSIS ===")
    print(f"Scenario name: {scenario['name']}")
    print(f"Office scope: {scenario['office_scope']}")
    print(f"Time range: {scenario['time_range']}")

    # Run the scenario to get results
    import requests
    response = requests.post(
        'http://localhost:8000/scenarios/run',
        json={'scenario_definition': scenario}
    )
    if response.status_code != 200:
        print(f"Simulation failed: {response.status_code} {response.text}")
        return
    results = response.json().get('results', {})

    print("\n=== SIMULATION RESULTS ANALYSIS ===\n")
    # Descend into 'years' key if present
    years = results.get('years', results)
    for year, year_data in years.items():
        print(f"Year {year} offices: {list(year_data.get('offices', {}).keys())}")
        offices = year_data.get('offices', {})
        for office_name, office_data in offices.items():
            if isinstance(office_data, dict) and 'roles' in office_data:
                total_fte = office_data.get('total_fte', 'N/A')
                financial = office_data.get('financial', {})
                revenue = financial.get('net_sales', 'N/A')
                cost = financial.get('salary_costs', 'N/A')
                print(f"  {office_name}: FTE={total_fte}, Revenue={revenue}, Cost={cost}")
        print()

if __name__ == "__main__":
    debug_revenue_calculation() 