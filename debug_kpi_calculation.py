#!/usr/bin/env python3
"""
Debug script to test KPI calculation with actual simulation results
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.src.services.kpi.kpi_service import KPIService
from backend.src.services.kpi.kpi_models import EconomicParameters
from backend.src.services.kpi.financial_kpis import FinancialKPICalculator
import requests
import json

def debug_kpi_calculation():
    """Debug KPI calculation with actual simulation results"""
    
    print("🔍 Debugging KPI Calculation")
    print("=" * 60)
    
    # Get the actual simulation results
    scenario_id = "ce0ed914-628e-485e-91f1-73877fbae750"
    
    try:
        response = requests.get(f"http://localhost:8000/scenarios/{scenario_id}/results")
        if response.status_code == 200:
            results = response.json()
            print("✅ Successfully retrieved simulation results")
        else:
            print(f"❌ Failed to retrieve results: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error retrieving results: {e}")
        return
    
    # Extract the simulation results
    simulation_results = results.get('results', {})
    
    print(f"\n📊 Simulation Results Structure:")
    print(f"  Years: {list(simulation_results.get('years', {}).keys())}")
    
    year_2025 = simulation_results.get('years', {}).get('2025', {})
    print(f"  2025 offices: {list(year_2025.get('offices', {}).keys())}")
    
    # Check Stockholm office structure
    stockholm = year_2025.get('offices', {}).get('Stockholm', {})
    print(f"  Stockholm keys: {list(stockholm.keys())}")
    
    # Check roles structure
    roles = stockholm.get('roles', {})
    print(f"  Roles: {list(roles.keys())}")
    
    # Check Consultant levels
    consultant = roles.get('Consultant', {})
    print(f"  Consultant levels: {list(consultant.keys())}")
    
    # Check first level data
    level_a = consultant.get('A', [])
    if level_a:
        print(f"  Level A first month: {level_a[0]}")
        print(f"  Level A last month: {level_a[-1]}")
        print(f"  Level A length: {len(level_a)}")
    
    # Create KPI service
    economic_params = EconomicParameters(
        working_hours_per_month=166.4,
        unplanned_absence=0.05,
        other_expense=19000000.0,
        employment_cost_rate=0.40,
        utilization=0.85
    )
    
    # Test financial calculator directly
    print(f"\n🧮 Testing Financial Calculator Directly:")
    financial_calculator = FinancialKPICalculator(economic_params)
    
    try:
        current_metrics = financial_calculator.calculate_current_financial_metrics(
            year_2025,
            unplanned_absence=0.05,
            other_expense=19000000.0,
            duration_months=1
        )
        
        print("✅ Financial calculator successful!")
        print(f"  Total Revenue: ${current_metrics['total_revenue']:,.0f}")
        print(f"  Total Salary Costs: ${current_metrics['total_salary_costs']:,.0f}")
        print(f"  Total Consultants: {current_metrics['total_consultants']}")
        
    except Exception as e:
        print(f"❌ Financial calculator failed: {e}")
        import traceback
        traceback.print_exc()
    
    kpi_service = KPIService(economic_params)
    
    print(f"\n🧮 Testing KPI Calculation:")
    
    # Calculate KPIs
    try:
        kpi_results = kpi_service.calculate_all_kpis(
            simulation_results,
            simulation_duration_months=1,  # 1 month simulation
            economic_params=economic_params
        )
        
        print("✅ KPI calculation successful!")
        print(f"\n💰 Financial KPIs:")
        print(f"  Net Sales: ${kpi_results.financial.net_sales:,.0f}")
        print(f"  Net Sales Baseline: ${kpi_results.financial.net_sales_baseline:,.0f}")
        print(f"  Total Salary Costs: ${kpi_results.financial.total_salary_costs:,.0f}")
        print(f"  Total Salary Costs Baseline: ${kpi_results.financial.total_salary_costs_baseline:,.0f}")
        print(f"  EBITDA: ${kpi_results.financial.ebitda:,.0f}")
        print(f"  EBITDA Baseline: ${kpi_results.financial.ebitda_baseline:,.0f}")
        print(f"  Margin: {kpi_results.financial.margin:.2%}")
        print(f"  Margin Baseline: {kpi_results.financial.margin_baseline:.2%}")
        print(f"  Total Consultants: {kpi_results.financial.total_consultants}")
        print(f"  Total Consultants Baseline: {kpi_results.financial.total_consultants_baseline}")
        
    except Exception as e:
        print(f"❌ KPI calculation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_kpi_calculation() 