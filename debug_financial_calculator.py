#!/usr/bin/env python3
"""
Debug script to test the financial calculator with actual office data structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.src.services.kpi.financial_kpis import FinancialKPICalculator
from backend.src.services.kpi.kpi_models import EconomicParameters
import requests
import json

def debug_financial_calculator():
    """Debug financial calculator with actual office data structure"""
    
    print("🔍 Debugging Financial Calculator")
    print("=" * 60)
    
    # Get the actual simulation results
    scenario_id = "ff3288f5-3dd5-4656-a2c3-870999a6347e"
    
    try:
        response = requests.get(f"http://localhost:8000/scenarios/{scenario_id}/results")
        if response.status_code == 200:
            results = response.json()
            print("✅ Successfully retrieved simulation results")
            
            # Get Stockholm office data
            stockholm_data = results['results']['years']['2025']['offices']['Stockholm']
            print(f"🏢 Stockholm office structure: {list(stockholm_data.keys())}")
            
            # Check roles data
            if 'roles' in stockholm_data:
                roles_data = stockholm_data['roles']
                print(f"👥 Roles structure: {list(roles_data.keys())}")
                
                if 'Consultant' in roles_data:
                    consultant_data = roles_data['Consultant']
                    print(f"💼 Consultant structure: {list(consultant_data.keys())}")
                    
                    if 'A' in consultant_data:
                        level_a_data = consultant_data['A']
                        print(f"📈 Level A data length: {len(level_a_data)}")
                        print(f"📈 Level A first month: {level_a_data[0]}")
            
            # Create economic parameters
            economic_params = EconomicParameters(
                price_increase=0.03,
                salary_increase=0.025,
                unplanned_absence=0.05,
                working_hours_per_month=166.4,
                other_expense=19000000.0,
                employment_cost_rate=0.40
            )
            
            # Create financial calculator
            financial_calculator = FinancialKPICalculator(economic_params)
            
            # Test with the actual office data structure
            print("\n🧮 Testing Financial Calculator with Office Data")
            print("-" * 50)
            
            # Create year data structure that matches what the KPI service expects
            year_data = {
                'offices': {
                    'Stockholm': stockholm_data
                }
            }
            
            # Calculate financial metrics
            financial_metrics = financial_calculator.calculate_current_financial_metrics(
                year_data,
                unplanned_absence=0.05,
                other_expense=19000000.0,
                duration_months=1
            )
            
            print(f"💰 Financial Metrics Calculated:")
            print(f"   Net Sales: {financial_metrics['total_revenue']:,.2f}")
            print(f"   Salary Costs: {financial_metrics['total_salary_costs']:,.2f}")
            print(f"   EBITDA: {financial_metrics['ebitda']:,.2f}")
            print(f"   Margin: {financial_metrics['margin']:.2%}")
            print(f"   Total Consultants: {financial_metrics['total_consultants']}")
            
            # Debug the calculation process
            print("\n🔍 Debugging Calculation Process")
            print("-" * 40)
            
            total_revenue = 0.0
            total_consultants = 0
            
            for office_name, office_data in year_data.get('offices', {}).items():
                print(f"🏢 Processing office: {office_name}")
                
                if 'roles' in office_data:
                    office_roles = office_data.get('roles', {})
                    print(f"   Found roles: {list(office_roles.keys())}")
                    
                    for role_name, role_data in office_roles.items():
                        print(f"   Processing role: {role_name}")
                        
                        if isinstance(role_data, dict):  # Hierarchical roles
                            for level_name, level_data in role_data.items():
                                print(f"     Processing level: {level_name}")
                                
                                if isinstance(level_data, list) and level_data:
                                    # Use first month data for 1-month simulation
                                    month_data = level_data[0]
                                    fte_count = month_data.get('fte', 0)
                                    hourly_rate = month_data.get('price', 0)
                                    salary = month_data.get('salary', 0)
                                    utr = month_data.get('utr', 0.85)
                                    
                                    print(f"       FTE: {fte_count}, Price: {hourly_rate}, Salary: {salary}, UTR: {utr}")
                                    
                                    if fte_count > 0:
                                        if role_name == 'Consultant':
                                            available_hours = 166.4 * (1 - 0.05)  # working_hours * (1 - unplanned_absence)
                                            billable_hours = available_hours * utr
                                            monthly_revenue_per_person = hourly_rate * billable_hours
                                            level_total_revenue = fte_count * monthly_revenue_per_person * 1  # duration_months
                                            total_revenue += level_total_revenue
                                            total_consultants += fte_count
                                            
                                            print(f"         Revenue calculation:")
                                            print(f"           Available hours: {available_hours}")
                                            print(f"           Billable hours: {billable_hours}")
                                            print(f"           Monthly revenue per person: {monthly_revenue_per_person:,.2f}")
                                            print(f"           Level total revenue: {level_total_revenue:,.2f}")
                                            print(f"           Running total revenue: {total_revenue:,.2f}")
                                            print(f"           Running total consultants: {total_consultants}")
            
            print(f"\n📊 Final Results:")
            print(f"   Total Revenue: {total_revenue:,.2f}")
            print(f"   Total Consultants: {total_consultants}")
            
        else:
            print(f"❌ Failed to retrieve results: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_financial_calculator() 