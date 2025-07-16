#!/usr/bin/env python3
"""
Debug KPI Data Structure
========================

Script to debug the exact data structure being passed to the KPI service.
"""

import requests
import json
from test_scenarios import get_scenario_by_name

def debug_kpi_data_structure(scenario_name):
    """Debug the data structure being passed to the KPI service."""
    
    print(f"🔍 KPI DATA STRUCTURE DEBUG: {scenario_name}")
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
            
            print(f"\n📊 RESULTS STRUCTURE ANALYSIS:")
            print("-" * 40)
            
            # Check if we have years data
            years_data = scenario_results.get('years', {})
            print(f"Years available: {list(years_data.keys())}")
            
            if '2025' in years_data:
                year_2025 = years_data['2025']
                print(f"\n📅 YEAR 2025 STRUCTURE:")
                print(f"  Keys: {list(year_2025.keys())}")
                
                offices_data = year_2025.get('offices', {})
                print(f"  Offices: {list(offices_data.keys())}")
                
                if 'Stockholm' in offices_data:
                    stockholm_data = offices_data['Stockholm']
                    print(f"\n🏢 STOCKHOLM OFFICE STRUCTURE:")
                    print(f"  Keys: {list(stockholm_data.keys())}")
                    
                    # Check for roles vs levels
                    if 'roles' in stockholm_data:
                        roles_data = stockholm_data['roles']
                        print(f"  ✅ Found 'roles' field")
                        print(f"  Roles: {list(roles_data.keys())}")
                        
                        if 'Consultant' in roles_data:
                            consultant_data = roles_data['Consultant']
                            print(f"\n  📋 CONSULTANT ROLE STRUCTURE:")
                            print(f"    Type: {type(consultant_data)}")
                            
                            if isinstance(consultant_data, dict):
                                print(f"    Levels: {list(consultant_data.keys())}")
                                
                                if 'A' in consultant_data:
                                    level_a_data = consultant_data['A']
                                    print(f"\n    📊 LEVEL A STRUCTURE:")
                                    print(f"      Type: {type(level_a_data)}")
                                    
                                    if isinstance(level_a_data, list) and level_a_data:
                                        print(f"      Array length: {len(level_a_data)}")
                                        last_month = level_a_data[-1]
                                        print(f"      Last month data: {last_month}")
                                        
                                        # Check for economic fields
                                        print(f"\n      💰 ECONOMIC FIELDS:")
                                        print(f"        fte: {last_month.get('fte', 'MISSING')}")
                                        print(f"        price: {last_month.get('price', 'MISSING')}")
                                        print(f"        salary: {last_month.get('salary', 'MISSING')}")
                                        print(f"        utr: {last_month.get('utr', 'MISSING')}")
                                        
                                        # Calculate expected revenue
                                        fte = last_month.get('fte', 0)
                                        price = last_month.get('price', 0)
                                        salary = last_month.get('salary', 0)
                                        utr = last_month.get('utr', 0.85)
                                        
                                        if fte > 0 and price > 0:
                                            working_hours = 160.0
                                            unplanned_absence = 0.05
                                            available_hours = working_hours * (1 - unplanned_absence)
                                            billable_hours = available_hours * utr
                                            monthly_revenue_per_person = price * billable_hours
                                            annual_revenue = fte * monthly_revenue_per_person * 12
                                            annual_cost = fte * salary * 12
                                            
                                            print(f"\n      📈 CALCULATED VALUES:")
                                            print(f"        Expected Annual Revenue: ${annual_revenue:,.0f}")
                                            print(f"        Expected Annual Cost: ${annual_cost:,.0f}")
                                            print(f"        Expected Annual Profit: ${annual_revenue - annual_cost:,.0f}")
                                        else:
                                            print(f"\n      ⚠️  Cannot calculate - missing data")
                                            print(f"        FTE: {fte}, Price: {price}, Salary: {salary}, UTR: {utr}")
                    
                    elif 'levels' in stockholm_data:
                        print(f"  ⚠️  Found 'levels' field (old structure)")
                    else:
                        print(f"  ❌ No 'roles' or 'levels' field found")
                        print(f"  Available fields: {list(stockholm_data.keys())}")
                
                # Check financial metrics
                financial_metrics = year_2025.get('financial', {})
                if financial_metrics:
                    print(f"\n💰 FINANCIAL METRICS:")
                    print(f"  {financial_metrics}")
                else:
                    print(f"\n❌ No financial metrics found")
                    
            else:
                print(f"❌ No 2025 data found")
                
        else:
            print(f"❌ Simulation failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n============================================================")
    print(f"✅ Debug completed!")

if __name__ == "__main__":
    debug_kpi_data_structure("minimal") 