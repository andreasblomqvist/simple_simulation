#!/usr/bin/env python3
"""
Debug Economic Parameters
========================

Script to debug why economic parameters are not being applied correctly
in the simulation results.
"""

import requests
import json
from test_scenarios import get_scenario_by_name

def debug_economic_params(scenario_name):
    """Debug economic parameters for a scenario."""
    
    print(f"🔍 ECONOMIC PARAMETERS DEBUG: {scenario_name}")
    print("=" * 60)
    
    # Get the scenario
    scenario_definition = get_scenario_by_name(scenario_name)
    
    # Show the economic parameters being sent
    print(f"\n📊 ECONOMIC PARAMETERS IN SCENARIO:")
    print("-" * 40)
    economic_params = scenario_definition.get('economic_params', {})
    for key, value in economic_params.items():
        print(f"  {key}: {value}")
    
    # Show baseline input with prices and salaries
    print(f"\n💰 BASELINE INPUT PRICES & SALARIES:")
    print("-" * 40)
    baseline_input = scenario_definition.get('baseline_input', {})
    offices = baseline_input.get('offices', {})
    
    for office_name, office_data in offices.items():
        print(f"\n🏢 {office_name}:")
        roles = office_data.get('roles', {})
        
        for role_name, role_data in roles.items():
            print(f"  📋 {role_name}:")
            
            if isinstance(role_data, dict):
                for level_name, level_data in role_data.items():
                    if isinstance(level_data, dict):
                        price = level_data.get('price_1', 0)
                        salary = level_data.get('salary_1', 0)
                        utr = level_data.get('utr_1', 0)
                        fte = level_data.get('fte', 0)
                        
                        print(f"    {level_name}:")
                        print(f"      FTE: {fte}")
                        print(f"      Price: ${price:,.0f}")
                        print(f"      Salary: ${salary:,.0f}")
                        print(f"      UTR: {utr:.2f}")
                        
                        # Calculate expected revenue and cost
                        working_hours = economic_params.get('working_hours_per_month', 160)
                        employment_cost_rate = economic_params.get('employment_cost_rate', 0.3)
                        unplanned_absence = economic_params.get('unplanned_absence', 0.05)
                        
                        # Revenue calculation
                        effective_hours = working_hours * (1 - unplanned_absence)
                        monthly_revenue = fte * effective_hours * price * utr
                        annual_revenue = monthly_revenue * 12
                        
                        # Cost calculation
                        monthly_cost = fte * salary * (1 + employment_cost_rate)
                        annual_cost = monthly_cost * 12
                        
                        print(f"      Expected Monthly Revenue: ${monthly_revenue:,.0f}")
                        print(f"      Expected Annual Revenue: ${annual_revenue:,.0f}")
                        print(f"      Expected Monthly Cost: ${monthly_cost:,.0f}")
                        print(f"      Expected Annual Cost: ${annual_cost:,.0f}")
                        print(f"      Expected Monthly Profit: ${monthly_revenue - monthly_cost:,.0f}")
                        print(f"      Expected Annual Profit: ${annual_revenue - annual_cost:,.0f}")
    
    # Run the simulation
    print(f"\n🔄 Running simulation...")
    
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
            
            # Show actual results vs expected
            print(f"\n📈 ACTUAL RESULTS vs EXPECTED:")
            print("-" * 40)
            show_actual_vs_expected(results, scenario_definition)
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def show_actual_vs_expected(results, scenario_definition):
    """Show actual results vs expected calculations."""
    
    # Get economic parameters
    economic_params = scenario_definition.get('economic_params', {})
    working_hours = economic_params.get('working_hours_per_month', 160)
    employment_cost_rate = economic_params.get('employment_cost_rate', 0.3)
    unplanned_absence = economic_params.get('unplanned_absence', 0.05)
    
    # Get baseline input for comparison
    baseline_input = scenario_definition.get('baseline_input', {})
    offices = baseline_input.get('offices', {})
    
    # Extract results
    years_data = results.get('results', {}).get('years', {})
    
    for year_str, year_data in years_data.items():
        print(f"\n📅 YEAR {year_str}:")
        offices_data = year_data.get('offices', {})
        
        for office_name in scenario_definition.get('office_scope', []):
            if office_name in offices_data:
                office_data = offices_data[office_name]
                baseline_office = offices.get(office_name, {})
                
                print(f"\n🏢 {office_name}:")
                print("-" * 30)
                
                roles_data = office_data.get('roles', {})
                baseline_roles = baseline_office.get('roles', {})
                
                for role_name, role_data in roles_data.items():
                    print(f"  📋 {role_name}:")
                    baseline_role = baseline_roles.get(role_name, {})
                    
                    if isinstance(role_data, dict):
                        for level_name, level_data in role_data.items():
                            if isinstance(level_data, list) and level_data:
                                # Get the last month's data
                                last_month = level_data[-1]
                                actual_fte = last_month.get('fte', 0)
                                
                                # Get financial metrics from office financial field
                                office_financial = office_data.get('financial', {})
                                actual_revenue = office_financial.get('net_sales', 0)
                                actual_cost = office_financial.get('total_salary_costs', 0)
                                actual_profit = office_financial.get('ebitda', 0)
                                
                                # Get baseline data for this level
                                baseline_level = baseline_role.get(level_name, {})
                                baseline_fte = baseline_level.get('fte', 0)
                                baseline_price = baseline_level.get('price_1', 0)
                                baseline_salary = baseline_level.get('salary_1', 0)
                                baseline_utr = baseline_level.get('utr_1', 0)
                                
                                # Calculate expected values
                                effective_hours = working_hours * (1 - unplanned_absence)
                                expected_monthly_revenue = actual_fte * effective_hours * baseline_price * baseline_utr
                                expected_monthly_cost = actual_fte * baseline_salary * (1 + employment_cost_rate)
                                expected_monthly_profit = expected_monthly_revenue - expected_monthly_cost
                                
                                print(f"    {level_name}:")
                                print(f"      FTE: {actual_fte:.1f} (baseline: {baseline_fte})")
                                print(f"      Revenue: ${actual_revenue:,.0f} (expected: ${expected_monthly_revenue:,.0f})")
                                print(f"      Cost: ${actual_cost:,.0f} (expected: ${expected_monthly_cost:,.0f})")
                                print(f"      Profit: ${actual_profit:,.0f} (expected: ${expected_monthly_profit:,.0f})")
                                
                                if actual_revenue != expected_monthly_revenue:
                                    print(f"      ⚠️  Revenue mismatch!")
                                if actual_cost != expected_monthly_cost:
                                    print(f"      ⚠️  Cost mismatch!")
                                if actual_profit != expected_monthly_profit:
                                    print(f"      ⚠️  Profit mismatch!")

def main():
    """Main function."""
    
    print("🔍 ECONOMIC PARAMETERS DEBUG")
    print("=" * 60)
    
    # Debug minimal scenario
    debug_economic_params("minimal")
    
    print(f"\n" + "=" * 60)
    print("✅ Debug completed!")

if __name__ == "__main__":
    main() 