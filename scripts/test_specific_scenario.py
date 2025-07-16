#!/usr/bin/env python3
"""
Test script to run a specific scenario by ID.
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.src.services.scenario_service import ScenarioService
from backend.src.services.config_service import config_service
from backend.src.services.scenario_models import ScenarioRequest

def test_specific_scenario(scenario_id):
    """Test a specific scenario by ID."""
    
    print(f"🔍 Testing Scenario: {scenario_id}")
    print("=" * 50)
    
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
    print(f"📅 Time Range: {scenario_data.get('time_range', {})}")
    print(f"🏢 Office Scope: {scenario_data.get('office_scope', [])}")
    
    # Check if scenario has baseline_input
    baseline_input = scenario_data.get('baseline_input', {})
    if baseline_input:
        print("✅ Scenario has baseline_input - will test recruitment distribution")
        global_recruitment = baseline_input.get('global', {}).get('recruitment', {})
        if global_recruitment:
            print("📊 Global recruitment values found:")
            for role, levels in global_recruitment.items():
                for level, months in levels.items():
                    if months:  # Only show non-empty
                        total = sum(months.values())
                        print(f"  {role}.{level}: {total} total FTE")
    else:
        print("⚠️  No baseline_input found - will use config values only")
    
    # Create scenario request
    request = ScenarioRequest(scenario_id=scenario_id)
    
    print("\n🚀 Running scenario...")
    
    # Run the scenario
    response = scenario_service.run_scenario(request)
    
    if response.status != "success":
        print(f"❌ Scenario failed: {response.error_message}")
        return False
    
    print(f"✅ Scenario completed successfully in {response.execution_time:.2f} seconds")
    
    # Extract results
    results = response.results
    
    print("\n📈 Scenario Results:")
    print("=" * 50)
    
    # Show key KPIs
    key_kpis = [
        ("baseline_total_fte", "Baseline Total FTE"),
        ("current_total_fte", "Current Total FTE"),
        ("fte_growth_absolute", "FTE Growth (Absolute)"),
        ("fte_growth_percentage", "FTE Growth (%)"),
        ("baseline_total_sales", "Baseline Total Sales"),
        ("current_total_sales", "Current Total Sales"),
        ("sales_growth_absolute", "Sales Growth (Absolute)"),
        ("sales_growth_percentage", "Sales Growth (%)"),
        ("baseline_total_ebitda", "Baseline Total EBITDA"),
        ("current_total_ebitda", "Current Total EBITDA"),
        ("ebitda_growth_absolute", "EBITDA Growth (Absolute)"),
        ("ebitda_growth_percentage", "EBITDA Growth (%)")
    ]
    
    for key, name in key_kpis:
        value = results.get(key, 0)
        if isinstance(value, (int, float)):
            if "percentage" in key:
                print(f"  {name}: {value:.2f}%")
            else:
                print(f"  {name}: {value:,.2f}")
        else:
            print(f"  {name}: {value}")
    
    # Show office-level results if available
    if 'years' in results:
        years = results['years']
        print(f"\n🏢 Office Results:")
        for year, year_data in years.items():
            print(f"  Year {year}:")
            offices = year_data.get('offices', {})
            for office_name, office_data in offices.items():
                total_fte = office_data.get('total_fte', 0)
                print(f"    {office_name}: {total_fte:,.1f} FTE")
    
    print("\n" + "=" * 50)
    print("✅ Scenario test completed successfully!")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 test_specific_scenario.py <scenario_id>")
        print("Example: python3 test_specific_scenario.py f5f26bc5-3830-4f64-ba53-03b58ae72353")
        sys.exit(1)
    
    scenario_id = sys.argv[1]
    success = test_specific_scenario(scenario_id)
    sys.exit(0 if success else 1) 