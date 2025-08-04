#!/usr/bin/env python3
"""
Test script to verify office-level KPI calculation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.src.services.kpi.kpi_service import KPIService
from backend.src.services.kpi.kpi_models import EconomicParameters
import requests
import json

def test_office_kpis():
    """Test office-level KPI calculation with actual simulation results"""
    
    print("🔍 Testing Office-Level KPI Calculation")
    print("=" * 60)
    
    # Get the actual simulation results
    scenario_id = "542b3850-1e46-4b7d-9d3e-bcd4a105071b"
    
    try:
        response = requests.get(f"http://localhost:8000/scenarios/{scenario_id}/results")
        if response.status_code == 200:
            results = response.json()
            print("✅ Successfully retrieved simulation results")
            
            # Get the year data
            year_data = results['results']['years']['2025']
            print(f"📊 Year 2025 data structure: {list(year_data.keys())}")
            
            # Get Stockholm office data
            stockholm_data = year_data['offices']['Stockholm']
            print(f"🏢 Stockholm office structure: {list(stockholm_data.keys())}")
            
            # Check if financial data exists
            if 'financial' in stockholm_data:
                financial_data = stockholm_data['financial']
                print(f"💰 Stockholm financial data: {json.dumps(financial_data, indent=2)}")
            else:
                print("❌ No financial data found in Stockholm office")
            
            # Check the roles data structure
            if 'roles' in stockholm_data:
                roles_data = stockholm_data['roles']
                print(f"👥 Stockholm roles structure: {list(roles_data.keys())}")
                
                # Check Consultant role data
                if 'Consultant' in roles_data:
                    consultant_data = roles_data['Consultant']
                    print(f"💼 Consultant structure: {list(consultant_data.keys())}")
                    
                    # Check Level A data
                    if 'A' in consultant_data:
                        level_a_data = consultant_data['A']
                        print(f"📈 Level A data length: {len(level_a_data)}")
                        print(f"📈 Level A first month: {level_a_data[0]}")
                        print(f"📈 Level A last month: {level_a_data[-1]}")
            
            # Test KPI calculation manually
            print("\n🧮 Testing Manual KPI Calculation")
            print("-" * 40)
            
            # Create economic parameters
            economic_params = EconomicParameters(
                price_increase=0.03,
                salary_increase=0.025,
                unplanned_absence=0.05,
                working_hours_per_month=166.4,
                other_expense=19000000.0,
                employment_cost_rate=0.40
            )
            
            # Create KPI service
            kpi_service = KPIService(economic_params)
            
            # Calculate KPIs for the year
            year_kpis = kpi_service.calculate_kpis_for_year(
                results['results'],
                target_year='2025',
                simulation_duration_months=1,  # 1-month simulation
                economic_params=economic_params
            )
            
            print(f"📊 Year KPIs calculated successfully")
            print(f"💰 Financial KPIs: {json.dumps(year_kpis.financial.__dict__, indent=2)}")
            
            # Test office-specific KPI calculation
            print("\n🏢 Testing Office-Specific KPI Calculation")
            print("-" * 50)
            
            # Create office-specific year data
            office_year_data = {
                'years': {
                    '2025': {
                        'offices': {
                            'Stockholm': stockholm_data
                        },
                        'total_fte': stockholm_data.get('total_fte', 0)
                    }
                }
            }
            
            # Calculate office-specific KPIs
            office_kpis = kpi_service.calculate_kpis_for_year(
                office_year_data,
                target_year='2025',
                simulation_duration_months=1,
                economic_params=economic_params
            )
            
            print(f"🏢 Stockholm Office KPIs:")
            print(f"💰 Net Sales: {office_kpis.financial.net_sales:,.2f}")
            print(f"💰 Salary Costs: {office_kpis.financial.total_salary_costs:,.2f}")
            print(f"💰 EBITDA: {office_kpis.financial.ebitda:,.2f}")
            print(f"💰 Margin: {office_kpis.financial.margin:.2%}")
            print(f"👥 Total Consultants: {office_kpis.financial.total_consultants}")
            
        else:
            print(f"❌ Failed to retrieve results: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_office_kpis() 