#!/usr/bin/env python3
"""
Debug script to check monthly_office_metrics and KPI calculation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.kpi.kpi_models import EconomicParameters

def debug_monthly_metrics():
    """Debug the monthly metrics and KPI calculation"""
    
    print("🔧 Debugging Monthly Metrics and KPI Calculation")
    print("=" * 60)
    
    # Create engine and economic parameters
    engine = SimulationEngine()
    economic_params = EconomicParameters(
        unplanned_absence=0.05,
        other_expense=19000000.0,
        employment_cost_rate=0.40,
        working_hours_per_month=166.4
    )
    
    # Run simulation
    print("📊 Running simulation...")
    results = engine.run_simulation(
        start_year=2025,
        start_month=1,
        end_year=2025,
        end_month=12,
        price_increase=0.02,
        salary_increase=0.02,
        economic_params=economic_params
    )
    
    print("✅ Simulation completed")
    print("")
    
    # Check the structure of results
    print("📋 Results Structure:")
    print(f"Keys in results: {list(results.keys())}")
    print(f"Years in results: {list(results['years'].keys())}")
    
    # Check the 2025 year data
    year_2025 = results['years']['2025']
    print(f"\n📊 Year 2025 Structure:")
    print(f"Keys in year_2025: {list(year_2025.keys())}")
    print(f"Total FTE: {year_2025.get('total_fte', 0)}")
    
    # Check offices data
    offices = year_2025.get('offices', {})
    print(f"Number of offices: {len(offices)}")
    
    # Check first office structure
    if offices:
        first_office_name = list(offices.keys())[0]
        first_office = offices[first_office_name]
        print(f"\n🏢 First office ({first_office_name}) structure:")
        print(f"Keys: {list(first_office.keys())}")
        print(f"Total FTE: {first_office.get('total_fte', 0)}")
        
        # Check levels data
        levels = first_office.get('levels', {})
        print(f"Number of roles: {len(levels)}")
        print(f"Roles: {list(levels.keys())}")
        
        # Check Consultant role structure
        if 'Consultant' in levels:
            consultant_levels = levels['Consultant']
            print(f"\n👥 Consultant levels structure:")
            print(f"Number of levels: {len(consultant_levels)}")
            print(f"Levels: {list(consultant_levels.keys())}")
            
            # Check first level data
            if consultant_levels:
                first_level_name = list(consultant_levels.keys())[0]
                first_level_data = consultant_levels[first_level_name]
                print(f"\n📈 First level ({first_level_name}) data:")
                print(f"Type: {type(first_level_data)}")
                if isinstance(first_level_data, list):
                    print(f"Number of months: {len(first_level_data)}")
                    if first_level_data:
                        print(f"First month data: {first_level_data[0]}")
                        print(f"Last month data: {first_level_data[-1]}")
                else:
                    print(f"Data: {first_level_data}")
    
    # Check KPIs
    kpis = year_2025.get('kpis', {})
    print(f"\n📊 KPIs structure:")
    print(f"Keys: {list(kpis.keys())}")
    
    if 'financial' in kpis:
        financial = kpis['financial']
        print(f"\n💰 Financial KPIs:")
        print(f"Net Sales: {financial.get('net_sales', 0):,.0f}")
        print(f"Net Sales Baseline: {financial.get('net_sales_baseline', 0):,.0f}")
        print(f"EBITDA: {financial.get('ebitda', 0):,.0f}")
        print(f"EBITDA Baseline: {financial.get('ebitda_baseline', 0):,.0f}")
        print(f"Total Salary Costs: {financial.get('total_salary_costs', 0):,.0f}")
        print(f"Total Salary Costs Baseline: {financial.get('total_salary_costs_baseline', 0):,.0f}")
    
    # Check if there's monthly_office_metrics in results
    if 'monthly_office_metrics' in results:
        monthly_metrics = results['monthly_office_metrics']
        print(f"\n📅 Monthly Office Metrics:")
        print(f"Number of offices: {len(monthly_metrics)}")
        
        if monthly_metrics:
            first_office_name = list(monthly_metrics.keys())[0]
            first_office_metrics = monthly_metrics[first_office_name]
            print(f"First office ({first_office_name}) metrics:")
            print(f"Number of months: {len(first_office_metrics)}")
            print(f"Months: {list(first_office_metrics.keys())}")
            
            # Check first month data
            if first_office_metrics:
                first_month = list(first_office_metrics.keys())[0]
                first_month_data = first_office_metrics[first_month]
                print(f"First month ({first_month}) data:")
                print(f"Keys: {list(first_month_data.keys())}")
                
                if 'Consultant' in first_month_data:
                    consultant_data = first_month_data['Consultant']
                    print(f"Consultant data: {consultant_data}")
    else:
        print("\n❌ No monthly_office_metrics found in results")

if __name__ == "__main__":
    debug_monthly_metrics() 