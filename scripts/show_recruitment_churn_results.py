#!/usr/bin/env python3
"""
Show Recruitment and Churn Results
==================================

Script to show exactly what recruitment and churn values were applied
and what the resulting FTE changes were.
"""

import requests
import json
from test_scenarios import get_scenario_by_name, validate_scenario

def show_recruitment_churn_analysis(scenario_name):
    """Show recruitment and churn analysis for a scenario."""
    
    print(f"📊 RECRUITMENT & CHURN ANALYSIS: {scenario_name}")
    print("=" * 60)
    
    # Get the scenario
    scenario_definition = get_scenario_by_name(scenario_name)
    
    # Show input recruitment and churn values
    print("\n📥 INPUT VALUES:")
    print("-" * 30)
    
    baseline_input = scenario_definition['baseline_input']
    offices = baseline_input['offices']
    
    for office_name, office_data in offices.items():
        print(f"\n🏢 {office_name}:")
        roles = office_data['roles']
        
        for role_name, role_data in roles.items():
            if role_name == 'Operations':
                # Operations is a single level
                recruitment_values = []
                churn_values = []
                for i in range(1, 13):
                    recruitment_values.append(role_data.get(f'recruitment_abs_{i}', 0))
                    churn_values.append(role_data.get(f'churn_abs_{i}', 0))
                
                print(f"  {role_name}:")
                print(f"    Initial FTE: {role_data['fte']}")
                print(f"    Monthly Recruitment: {recruitment_values}")
                print(f"    Monthly Churn: {churn_values}")
                print(f"    Net Monthly Change: {[r - c for r, c in zip(recruitment_values, churn_values)]}")
                print(f"    Total Annual Recruitment: {sum(recruitment_values)}")
                print(f"    Total Annual Churn: {sum(churn_values)}")
                print(f"    Net Annual Change: {sum(recruitment_values) - sum(churn_values)}")
            else:
                # Consultant has multiple levels
                for level_name, level_data in role_data.items():
                    recruitment_values = []
                    churn_values = []
                    for i in range(1, 13):
                        recruitment_values.append(level_data.get(f'recruitment_abs_{i}', 0))
                        churn_values.append(level_data.get(f'churn_abs_{i}', 0))
                    
                    print(f"  {role_name}.{level_name}:")
                    print(f"    Initial FTE: {level_data['fte']}")
                    print(f"    Monthly Recruitment: {recruitment_values}")
                    print(f"    Monthly Churn: {churn_values}")
                    print(f"    Net Monthly Change: {[r - c for r, c in zip(recruitment_values, churn_values)]}")
                    print(f"    Total Annual Recruitment: {sum(recruitment_values)}")
                    print(f"    Total Annual Churn: {sum(churn_values)}")
                    print(f"    Net Annual Change: {sum(recruitment_values) - sum(churn_values)}")
    
    # Run the simulation
    print(f"\n🔄 RUNNING SIMULATION...")
    
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
            print("✅ Simulation completed!")
            
            # Show results
            show_simulation_results(results, scenario_definition)
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def show_simulation_results(results, scenario_definition):
    """Show the simulation results."""
    
    print(f"\n📤 SIMULATION RESULTS:")
    print("-" * 30)
    
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
                    role_totals = {}
                    
                    for role_name, role_data in roles_data.items():
                        role_total = 0
                        
                        if isinstance(role_data, dict):
                            # Handle levels within roles
                            for level_name, level_data in role_data.items():
                                if isinstance(level_data, list):
                                    # Get the last month's FTE (most recent)
                                    if level_data:
                                        last_month_fte = level_data[-1].get('fte', 0)
                                        total_fte += last_month_fte
                                        role_total += last_month_fte
                                        print(f"  {role_name}.{level_name}: {last_month_fte:.1f} FTE")
                                elif isinstance(level_data, dict) and 'fte' in level_data:
                                    # Direct FTE value
                                    fte = level_data['fte']
                                    total_fte += fte
                                    role_total += fte
                                    print(f"  {role_name}.{level_name}: {fte:.1f} FTE")
                        
                        role_totals[role_name] = role_total
                    
                    print(f"  📈 Total: {total_fte:.1f} FTE")
                    
                    # Show role breakdown
                    print(f"  📊 Role Breakdown:")
                    for role_name, role_total in role_totals.items():
                        print(f"    {role_name}: {role_total:.1f} FTE")
                else:
                    print("  ❌ No roles data found")
            else:
                print(f"🏢 {office_name}: ❌ Not found in results")

def main():
    """Main function."""
    
    print("🔍 RECRUITMENT & CHURN ANALYSIS")
    print("=" * 60)
    
    # Test minimal scenario
    show_recruitment_churn_analysis("minimal")
    
    print(f"\n" + "=" * 60)
    print("✅ Analysis completed!")

if __name__ == "__main__":
    main() 