#!/usr/bin/env python3
"""
Debug script to see exact distribution values being calculated.
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.src.services.scenario_service import ScenarioService
from backend.src.services.config_service import config_service
from backend.src.services.scenario_models import ScenarioRequest

def debug_distribution_values(scenario_id):
    """Debug the exact distribution values being calculated."""
    
    print(f"🔍 Debugging Distribution Values for Scenario: {scenario_id}")
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
        
        # Calculate expected distribution
        print(f"\n🎯 Expected Distribution by Office:")
        for office_name, office_data in baseline_config.items():
            office_fte = office_data.get('total_fte', 0)
            office_weight = office_fte / total_baseline_fte if total_baseline_fte else 0
            
            expected_recruitment = total_recruitment * office_weight
            expected_churn = total_churn * office_weight
            expected_net = expected_recruitment - expected_churn
            expected_final = office_fte + expected_net
            
            print(f"  {office_name}:")
            print(f"    Baseline FTE: {office_fte}")
            print(f"    Weight: {office_weight:.4f}")
            print(f"    Expected Recruitment: {expected_recruitment:.1f} FTE")
            print(f"    Expected Churn: {expected_churn:.1f} FTE")
            print(f"    Expected Net Change: {expected_net:.1f} FTE")
            print(f"    Expected Final FTE: {expected_final:.1f} FTE")
    
    # Run scenario and get detailed results
    print("\n🚀 Running scenario for detailed analysis...")
    request = ScenarioRequest(scenario_id=scenario_id)
    response = scenario_service.run_scenario(request)
    
    if response.status != "success":
        print(f"❌ Scenario failed: {response.error_message}")
        return
    
    results = response.results
    
    print("\n📊 Actual Results vs Expected:")
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
                office_weight = baseline_office_fte / total_baseline_fte if total_baseline_fte else 0
                expected_recruitment = total_recruitment * office_weight
                expected_churn = total_churn * office_weight
                expected_net = expected_recruitment - expected_churn
                expected_final = baseline_office_fte + expected_net
                
                print(f"  {office_name}:")
                print(f"    Expected: {expected_final:.1f} FTE (baseline {baseline_office_fte} + net {expected_net:.1f})")
                print(f"    Actual:   {office_fte:.1f} FTE")
                print(f"    Diff:     {office_fte - expected_final:.1f} FTE")
            
            print(f"  Year {year} Total: {year_total:,.1f} FTE")
            expected_year_total = total_baseline_fte + total_recruitment - total_churn
            print(f"  Expected Total: {expected_year_total:,.1f} FTE")
            print(f"  Total Diff: {year_total - expected_year_total:.1f} FTE")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 debug_distribution_values.py <scenario_id>")
        sys.exit(1)
    
    scenario_id = sys.argv[1]
    debug_distribution_values(scenario_id) 