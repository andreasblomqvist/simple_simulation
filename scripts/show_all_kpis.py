#!/usr/bin/env python3
"""
Show All KPIs
=============

Script to show all KPIs from the simulation results.
"""

import requests
import json
from test_scenarios import get_scenario_by_name, validate_scenario

def show_all_kpis(scenario_name):
    """Show all KPIs from a scenario simulation."""
    
    print(f"📊 ALL KPIs ANALYSIS: {scenario_name}")
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
            results = response.json()
            print("✅ Simulation completed!")
            
            # Show all KPIs
            display_all_kpis(results, scenario_definition)
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def display_all_kpis(results, scenario_definition):
    """Display all KPIs from the results."""
    
    print(f"\n📈 ALL KPIs:")
    print("=" * 60)
    
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
        print("-" * 50)
        
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
                print("-" * 30)
                
                # Show all available KPIs for this office
                show_office_kpis(office_data)
            else:
                print(f"🏢 {office_name}: ❌ Not found in results")

def show_office_kpis(office_data):
    """Show all KPIs for a specific office."""
    
    # Check roles structure
    roles_data = office_data.get('roles', {})
    
    if roles_data:
        # Calculate total FTE for this office
        total_fte = 0
        total_revenue = 0
        total_cost = 0
        total_profit = 0
        role_totals = {}
        
        for role_name, role_data in roles_data.items():
            role_total_fte = 0
            role_total_revenue = 0
            role_total_cost = 0
            role_total_profit = 0
            
            if isinstance(role_data, dict):
                # Handle levels within roles
                for level_name, level_data in role_data.items():
                    if isinstance(level_data, list):
                        # Get the last month's data (most recent)
                        if level_data:
                            last_month = level_data[-1]
                            fte = last_month.get('fte', 0)
                            revenue = last_month.get('revenue', 0)
                            cost = last_month.get('cost', 0)
                            profit = last_month.get('profit', 0)
                            
                            total_fte += fte
                            total_revenue += revenue
                            total_cost += cost
                            total_profit += profit
                            
                            role_total_fte += fte
                            role_total_revenue += revenue
                            role_total_cost += cost
                            role_total_profit += profit
                            
                            print(f"  {role_name}.{level_name}:")
                            print(f"    FTE: {fte:.1f}")
                            print(f"    Revenue: ${revenue:,.0f}")
                            print(f"    Cost: ${cost:,.0f}")
                            print(f"    Profit: ${profit:,.0f}")
                            print(f"    Margin: {(profit/revenue*100) if revenue > 0 else 0:.1f}%")
                            
                    elif isinstance(level_data, dict):
                        # Direct values
                        fte = level_data.get('fte', 0)
                        revenue = level_data.get('revenue', 0)
                        cost = level_data.get('cost', 0)
                        profit = level_data.get('profit', 0)
                        
                        total_fte += fte
                        total_revenue += revenue
                        total_cost += cost
                        total_profit += profit
                        
                        role_total_fte += fte
                        role_total_revenue += revenue
                        role_total_cost += cost
                        role_total_profit += profit
                        
                        print(f"  {role_name}.{level_name}:")
                        print(f"    FTE: {fte:.1f}")
                        print(f"    Revenue: ${revenue:,.0f}")
                        print(f"    Cost: ${cost:,.0f}")
                        print(f"    Profit: ${profit:,.0f}")
                        print(f"    Margin: {(profit/revenue*100) if revenue > 0 else 0:.1f}%")
            
            role_totals[role_name] = {
                'fte': role_total_fte,
                'revenue': role_total_revenue,
                'cost': role_total_cost,
                'profit': role_total_profit
            }
        
        # Show office totals
        print(f"\n  📊 OFFICE TOTALS:")
        print(f"    Total FTE: {total_fte:.1f}")
        print(f"    Total Revenue: ${total_revenue:,.0f}")
        print(f"    Total Cost: ${total_cost:,.0f}")
        print(f"    Total Profit: ${total_profit:,.0f}")
        print(f"    Overall Margin: {(total_profit/total_revenue*100) if total_revenue > 0 else 0:.1f}%")
        print(f"    Revenue per FTE: ${(total_revenue/total_fte) if total_fte > 0 else 0:,.0f}")
        print(f"    Cost per FTE: ${(total_cost/total_fte) if total_fte > 0 else 0:,.0f}")
        print(f"    Profit per FTE: ${(total_profit/total_fte) if total_fte > 0 else 0:,.0f}")
        
        # Show role breakdown
        print(f"\n  📈 ROLE BREAKDOWN:")
        for role_name, role_data in role_totals.items():
            print(f"    {role_name}:")
            print(f"      FTE: {role_data['fte']:.1f}")
            print(f"      Revenue: ${role_data['revenue']:,.0f}")
            print(f"      Cost: ${role_data['cost']:,.0f}")
            print(f"      Profit: ${role_data['profit']:,.0f}")
            print(f"      Margin: {(role_data['profit']/role_data['revenue']*100) if role_data['revenue'] > 0 else 0:.1f}%")
    else:
        print("  ❌ No roles data found")

def main():
    """Main function."""
    
    print("📊 ALL KPIs ANALYSIS")
    print("=" * 60)
    
    # Test minimal scenario
    show_all_kpis("minimal")
    
    print(f"\n" + "=" * 60)
    print("✅ Analysis completed!")

if __name__ == "__main__":
    main() 