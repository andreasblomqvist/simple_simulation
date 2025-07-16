#!/usr/bin/env python3
"""
Debug script to understand recruitment distribution issues.
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.src.services.scenario_service import ScenarioService
from backend.src.services.config_service import config_service
from backend.src.services.scenario_models import ScenarioRequest

def debug_scenario_distribution(scenario_id):
    """Debug the recruitment distribution for a specific scenario."""
    
    print(f"🔍 Debugging Scenario: {scenario_id}")
    print("=" * 60)
    
    # Initialize services
    scenario_service = ScenarioService(config_service)
    
    # Load the scenario definition
    scenario_path = f"data/scenarios/definitions/{scenario_id}.json"
    
    with open(scenario_path, 'r') as f:
        scenario_data = json.load(f)
    
    print(f"📋 Scenario Name: {scenario_data.get('name', 'Unknown')}")
    print(f"📅 Time Range: {scenario_data.get('time_range', {})}")
    
    # Check baseline configuration
    print("\n📊 Baseline Configuration:")
    baseline_config = config_service.get_configuration()
    total_baseline_fte = sum(office.get('total_fte', 0) for office in baseline_config.values())
    print(f"  Total Baseline FTE: {total_baseline_fte}")
    
    for office_name, office_data in baseline_config.items():
        print(f"  {office_name}: {office_data.get('total_fte', 0)} FTE")
    
    # Check baseline_input
    baseline_input = scenario_data.get('baseline_input', {})
    if baseline_input:
        print("\n📈 Baseline Input Analysis:")
        global_recruitment = baseline_input.get('global', {}).get('recruitment', {})
        global_churn = baseline_input.get('global', {}).get('churn', {})
        
        # Calculate totals
        total_recruitment = 0
        total_churn = 0
        
        print("  Recruitment by Role/Level:")
        for role, levels in global_recruitment.items():
            for level, months in levels.items():
                if months:
                    role_total = sum(months.values())
                    total_recruitment += role_total
                    print(f"    {role}.{level}: {role_total} FTE")
        
        print("  Churn by Role/Level:")
        for role, levels in global_churn.items():
            for level, months in levels.items():
                if months:
                    role_total = sum(months.values())
                    total_churn += role_total
                    print(f"    {role}.{level}: {role_total} FTE")
        
        print(f"\n  Summary:")
        print(f"    Total Recruitment: {total_recruitment} FTE")
        print(f"    Total Churn: {total_churn} FTE")
        print(f"    Net Change: {total_recruitment - total_churn} FTE")
        print(f"    Expected Final FTE: {total_baseline_fte + total_recruitment - total_churn}")
    
    # Run scenario and get detailed results
    print("\n🚀 Running scenario for detailed analysis...")
    request = ScenarioRequest(scenario_id=scenario_id)
    response = scenario_service.run_scenario(request)
    
    if response.status != "success":
        print(f"❌ Scenario failed: {response.error_message}")
        return
    
    results = response.results
    
    print("\n📊 Detailed Results Analysis:")
    print("=" * 60)
    
    # Check if we have year-by-year data
    if 'years' in results:
        years = results['years']
        for year, year_data in years.items():
            print(f"\n📅 Year {year}:")
            offices = year_data.get('offices', {})
            
            year_total = 0
            for office_name, office_data in offices.items():
                office_fte = office_data.get('total_fte', 0)
                year_total += office_fte
                print(f"  {office_name}: {office_fte:,.1f} FTE")
            
            print(f"  Year {year} Total: {year_total:,.1f} FTE")
            
            # Check if we have level details
            if offices:
                first_office = list(offices.values())[0]
                if 'levels' in first_office:
                    print(f"  Level Details for {list(offices.keys())[0]}:")
                    levels = first_office['levels']
                    for role, role_data in levels.items():
                        for level, level_data in role_data.items():
                            if isinstance(level_data, list) and level_data:
                                level_fte = level_data[0].get('fte', 0) if isinstance(level_data[0], dict) else 0
                                print(f"    {role}.{level}: {level_fte:,.1f} FTE")
    
    # Check KPIs
    print(f"\n💰 KPI Summary:")
    kpis = [
        ("baseline_total_fte", "Baseline Total FTE"),
        ("current_total_fte", "Current Total FTE"),
        ("fte_growth_absolute", "FTE Growth (Absolute)"),
        ("fte_growth_percentage", "FTE Growth (%)")
    ]
    
    for key, name in kpis:
        value = results.get(key, 0)
        if isinstance(value, (int, float)):
            if "percentage" in key:
                print(f"  {name}: {value:.2f}%")
            else:
                print(f"  {name}: {value:,.2f}")
        else:
            print(f"  {name}: {value}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 debug_scenario_distribution.py <scenario_id>")
        sys.exit(1)
    
    scenario_id = sys.argv[1]
    debug_scenario_distribution(scenario_id) 