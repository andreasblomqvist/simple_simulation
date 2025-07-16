#!/usr/bin/env python3
"""
Debug script to understand the office building process and FTE values.
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.src.services.scenario_service import ScenarioService
from backend.src.services.config_service import config_service
from backend.src.services.scenario_models import ScenarioRequest

def debug_office_building(scenario_id):
    """Debug the office building process and FTE values."""
    
    print(f"🔍 Debugging Office Building for Scenario: {scenario_id}")
    print("=" * 70)
    
    # Initialize services
    scenario_service = ScenarioService(config_service)
    
    # Load the scenario definition
    scenario_path = f"data/scenarios/definitions/{scenario_id}.json"
    
    with open(scenario_path, 'r') as f:
        scenario_data = json.load(f)
    
    print(f"📋 Scenario Name: {scenario_data.get('name', 'Unknown')}")
    
    # Check baseline configuration
    print("\n📊 Baseline Configuration:")
    baseline_config = config_service.get_configuration()
    total_baseline_fte = sum(office.get('total_fte', 0) for office in baseline_config.values())
    print(f"  Total Baseline FTE: {total_baseline_fte}")
    
    for office_name, office_data in baseline_config.items():
        print(f"  {office_name}: {office_data.get('total_fte', 0)} FTE")
        
        # Check individual role/level FTE values
        roles = office_data.get('roles', {})
        for role_name, role_data in roles.items():
            if isinstance(role_data, dict):
                # Leveled role
                for level_name, level_data in role_data.items():
                    if isinstance(level_data, dict):
                        fte = level_data.get('fte', 0)
                        print(f"    {role_name}.{level_name}: {fte} FTE")
            else:
                # Flat role
                fte = role_data.get('fte', 0)
                print(f"    {role_name}: {fte} FTE")
    
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
    
    # Resolve scenario data to see what offices are built
    print("\n🚀 Resolving scenario data...")
    resolved_data = scenario_service.resolve_scenario(scenario_data)
    
    if 'offices' in resolved_data:
        offices = resolved_data['offices']
        print(f"\n📊 Resolved Offices:")
        print(f"  Number of offices: {len(offices)}")
        
        for office_name, office in offices.items():
            print(f"\n  {office_name}:")
            print(f"    Total FTE: {office.total_fte}")
            print(f"    Journey: {office.journey.value}")
            
            # Check each role and level
            for role_name, role_data in office.roles.items():
                if isinstance(role_data, dict):
                    # Leveled role
                    print(f"    {role_name}:")
                    for level_name, level in role_data.items():
                        print(f"      {level_name}:")
                        print(f"        FTE field: {getattr(level, 'fte', 'NOT FOUND')}")
                        print(f"        Total property: {level.total}")
                        print(f"        People count: {len(level.people)}")
                else:
                    # Flat role
                    print(f"    {role_name}:")
                    print(f"      FTE field: {getattr(role_data, 'fte', 'NOT FOUND')}")
                    print(f"      Total property: {role_data.total}")
                    print(f"      People count: {len(role_data.people)}")
    
    # Run scenario and get detailed results
    print("\n🚀 Running scenario for detailed analysis...")
    request = ScenarioRequest(scenario_id=scenario_id)
    response = scenario_service.run_scenario(request)
    
    if response.status != "success":
        print(f"❌ Scenario failed: {response.error_message}")
        return
    
    results = response.results
    
    print("\n📊 Simulation Results:")
    print("=" * 70)
    
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
                
                # Get expected values
                baseline_office_fte = baseline_config.get(office_name, {}).get('total_fte', 0)
                
                print(f"  {office_name}:")
                print(f"    Baseline FTE: {baseline_office_fte}")
                print(f"    Actual FTE: {office_fte}")
                print(f"    Diff: {office_fte - baseline_office_fte}")
            
            print(f"  Year {year} Total: {year_total:,.1f} FTE")
            print(f"  Baseline Total: {total_baseline_fte:,.1f} FTE")
            print(f"  Total Diff: {year_total - total_baseline_fte:.1f} FTE")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 debug_office_building.py <scenario_id>")
        sys.exit(1)
    
    scenario_id = sys.argv[1]
    debug_office_building(scenario_id) 