#!/usr/bin/env python3
"""
Show Correct KPIs
=================

Script to show the correct financial KPIs from the office-level financial field.
"""

import requests
import json
from test_scenarios import get_scenario_by_name

def show_correct_kpis(scenario_name):
    """Show the correct financial KPIs from the simulation results."""
    
    print(f"📊 CORRECT KPIs ANALYSIS: {scenario_name}")
    print("=" * 60)
    
    # Get the scenario
    scenario_definition = get_scenario_by_name(scenario_name)
    
    # Run the simulation
    print(f"🔄 Running simulation...")
    
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
            print("✅ Simulation completed!")
            results = response.json()
            
            # Extract the results data
            scenario_results = results.get('results', {})
            
            print(f"\n📈 CORRECT FINANCIAL KPIs:")
            print("=" * 60)
            
            # Check if we have years data
            years_data = scenario_results.get('years', {})
            
            for year_str, year_data in years_data.items():
                print(f"\n📅 YEAR {year_str}:")
                print("-" * 40)
                
                offices_data = year_data.get('offices', {})
                
                for office_name, office_data in offices_data.items():
                    print(f"\n🏢 {office_name}:")
                    print("-" * 30)
                    
                    # Get office-level financial metrics
                    financial_data = office_data.get('financial', {})
                    
                    if financial_data:
                        print(f"  💰 FINANCIAL METRICS:")
                        print(f"    Net Sales: ${financial_data.get('net_sales', 0):,.0f}")
                        print(f"    Net Sales Baseline: ${financial_data.get('net_sales_baseline', 0):,.0f}")
                        print(f"    Total Salary Costs: ${financial_data.get('total_salary_costs', 0):,.0f}")
                        print(f"    Total Salary Costs Baseline: ${financial_data.get('total_salary_costs_baseline', 0):,.0f}")
                        print(f"    EBITDA: ${financial_data.get('ebitda', 0):,.0f}")
                        print(f"    EBITDA Baseline: ${financial_data.get('ebitda_baseline', 0):,.0f}")
                        print(f"    Margin: {financial_data.get('margin', 0):.2%}")
                        print(f"    Margin Baseline: {financial_data.get('margin_baseline', 0):.2%}")
                        print(f"    Total Consultants: {financial_data.get('total_consultants', 0)}")
                        print(f"    Total Consultants Baseline: {financial_data.get('total_consultants_baseline', 0)}")
                        print(f"    Avg Hourly Rate: ${financial_data.get('avg_hourly_rate', 0):,.0f}")
                        print(f"    Avg Hourly Rate Baseline: ${financial_data.get('avg_hourly_rate_baseline', 0):,.0f}")
                        print(f"    Avg UTR: {financial_data.get('avg_utr', 0):.2f}")
                    else:
                        print(f"  ❌ No financial data found")
                    
                    # Get growth metrics
                    growth_data = office_data.get('growth', {})
                    if growth_data:
                        print(f"\n  📈 GROWTH METRICS:")
                        print(f"    Total Growth %: {growth_data.get('total_growth_percent', 0):.1f}%")
                        print(f"    Total Growth Absolute: {growth_data.get('total_growth_absolute', 0)}")
                        print(f"    Current Total FTE: {growth_data.get('current_total_fte', 0)}")
                        print(f"    Baseline Total FTE: {growth_data.get('baseline_total_fte', 0)}")
                        print(f"    Non-Debit Ratio: {growth_data.get('non_debit_ratio', 0):.1f}%")
                        print(f"    Non-Debit Ratio Baseline: {growth_data.get('non_debit_ratio_baseline', 0):.1f}%")
                        print(f"    Non-Debit Delta: {growth_data.get('non_debit_delta', 0):.1f}%")
                    
                    # Get journey metrics
                    journey_data = office_data.get('journeys', {})
                    if journey_data:
                        print(f"\n  🛤️  JOURNEY METRICS:")
                        for journey_name, journey_metrics in journey_data.items():
                            if isinstance(journey_metrics, dict):
                                current = journey_metrics.get('current', 0)
                                baseline = journey_metrics.get('baseline', 0)
                                delta = journey_metrics.get('delta', 0)
                                print(f"    {journey_name}: Current: {current}, Baseline: {baseline}, Delta: {delta}")
                    
                    # Show FTE breakdown by role
                    roles_data = office_data.get('roles', {})
                    if roles_data:
                        print(f"\n  👥 FTE BREAKDOWN BY ROLE:")
                        total_fte = 0
                        for role_name, role_data in roles_data.items():
                            if isinstance(role_data, dict):
                                # Leveled role
                                role_fte = 0
                                for level_name, level_data in role_data.items():
                                    if isinstance(level_data, list) and level_data:
                                        last_month = level_data[-1]
                                        level_fte = last_month.get('fte', 0)
                                        role_fte += level_fte
                                        print(f"      {role_name}.{level_name}: {level_fte:.1f}")
                                print(f"    {role_name} Total: {role_fte:.1f}")
                                total_fte += role_fte
                            elif isinstance(role_data, list) and role_data:
                                # Flat role
                                last_month = role_data[-1]
                                role_fte = last_month.get('fte', 0)
                                print(f"    {role_name}: {role_fte:.1f}")
                                total_fte += role_fte
                        
                        print(f"    Office Total FTE: {total_fte:.1f}")
                
                # Show year-level KPIs if available
                year_kpis = year_data.get('kpis', {})
                if year_kpis:
                    print(f"\n📊 YEAR-LEVEL KPIs:")
                    print(f"  {year_kpis}")
                
        else:
            print(f"❌ Simulation failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n============================================================")
    print(f"✅ Analysis completed!")

if __name__ == "__main__":
    show_correct_kpis("minimal") 