#!/usr/bin/env python3
"""
Comprehensive investigation of financial calculation issues
Let's trace through the entire financial calculation process step by step
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.kpi_service import KPIService
import random

def investigate_financial_calculations():
    """Deep dive into financial calculation issues"""
    
    print("🔍 COMPREHENSIVE FINANCIAL INVESTIGATION")
    print("=" * 60)
    
    # Seed for reproducible results
    random.seed(42)
    
    # Create engine with baseline (no levers)
    engine = SimulationEngine()
    kpi_service = KPIService()
    
    print("📊 STEP 1: Baseline Data Analysis")
    print("-" * 40)
    
    # Get baseline data for analysis
    stockholm = engine.offices['Stockholm']
    print(f"Stockholm office journey: {stockholm.journey}")
    print(f"Stockholm total FTE: {stockholm.total_fte}")
    
    # Show detailed breakdown
    total_consultants = 0
    for role_name, role_data in stockholm.roles.items():
        if role_name == 'Consultant' and isinstance(role_data, dict):
            print(f"\n{role_name} levels:")
            for level_name, level_obj in role_data.items():
                print(f"  {level_name}: {level_obj.total} FTE, Salary: {level_obj.salary_1:,.0f} SEK/month, Price: {level_obj.price_1:,.0f} SEK/hour")
                total_consultants += level_obj.total
    
    print(f"\nTotal Stockholm consultants: {total_consultants}")
    
    print("\n📊 STEP 2: Single Month Financial Calculation")
    print("-" * 40)
    
    # Run just 1 month to see what happens
    result = engine.run_simulation(
        start_year=2025,
        start_month=1,
        end_year=2025,
        end_month=1,
        lever_plan={}
    )
    
    # Calculate KPIs for this single month
    kpis = kpi_service.calculate_kpis(result['monthly_results'], 1)
    
    print("Single Month Results:")
    print(f"  Net Sales: {kpis.get('net_sales', 'N/A'):,.1f} SEK")
    print(f"  EBITDA: {kpis.get('ebitda', 'N/A'):,.1f} SEK")
    print(f"  Total FTE: {kpis.get('total_fte', 'N/A')}")
    
    print("\n📊 STEP 3: Manual Financial Calculation")
    print("-" * 40)
    
    # Let's manually calculate what the financials SHOULD be
    total_consultants = 0
    total_monthly_costs = 0
    total_monthly_revenue = 0
    
    # Get the last month data
    monthly_results = result['monthly_results']
    last_month = monthly_results[-1]  # Last month data
    
    for office_name, office_data in last_month.items():
        if office_name == 'metadata':
            continue
            
        print(f"\n{office_name} Office:")
        
        for role, role_data in office_data.items():
            if role != 'Consultant':
                continue
                
            for level, level_data in role_data.items():
                count = level_data['total']
                salary = level_data['salary']
                price = level_data.get('price', 0)
                
                if count > 0:
                    total_consultants += count
                    
                    # Monthly costs (salary + employment costs)
                    monthly_cost = count * salary * 1.40  # 40% employment costs
                    total_monthly_costs += monthly_cost
                    
                    # Monthly revenue (assuming 166.4 working hours, 95% utilization)
                    working_hours = 166.4 * 0.95  # 95% utilization
                    monthly_revenue = count * working_hours * price
                    total_monthly_revenue += monthly_revenue
                    
                    print(f"  {level}: {count} FTE")
                    print(f"    Salary: {salary:,.0f} SEK/month")
                    print(f"    Price: {price:,.0f} SEK/hour") 
                    print(f"    Monthly Cost: {monthly_cost:,.0f} SEK")
                    print(f"    Monthly Revenue: {monthly_revenue:,.0f} SEK")
    
    print(f"\nMANUAL CALCULATION TOTALS:")
    print(f"  Total Consultants: {total_consultants}")
    print(f"  Total Monthly Costs: {total_monthly_costs:,.0f} SEK")
    print(f"  Total Monthly Revenue: {total_monthly_revenue:,.0f} SEK")
    print(f"  Monthly Profit: {total_monthly_revenue - total_monthly_costs:,.0f} SEK")
    print(f"  Margin: {((total_monthly_revenue - total_monthly_costs) / total_monthly_revenue * 100) if total_monthly_revenue > 0 else 0:.1f}%")
    
    print("\n📊 STEP 4: KPI Service Deep Dive")
    print("-" * 40)
    
    # Let's examine the KPI calculation in detail
    print("KPI Service Results:")
    for key, value in kpis.items():
        if isinstance(value, (int, float)):
            print(f"  {key}: {value:,.1f}")
        else:
            print(f"  {key}: {value}")
    
    # Let's look at the raw data structure
    print("\nRaw Result Structure:")
    print(f"  Keys: {list(result.keys())}")
    print(f"  Monthly results length: {len(result['monthly_results'])}")
    
    # Look at first and last month structure
    first_month = result['monthly_results'][0]
    print(f"  First month offices: {list(first_month.keys())}")
    
    if 'Stockholm' in first_month:
        stockholm_data = first_month['Stockholm']
        print(f"  Stockholm roles: {list(stockholm_data.keys())}")
        if 'Consultant' in stockholm_data:
            consultant_data = stockholm_data['Consultant']
            print(f"  Consultant levels: {list(consultant_data.keys())}")
            
            # Show one level in detail
            if 'A' in consultant_data:
                a_level = consultant_data['A']
                print(f"  A level data: {a_level}")
    
    print("\n📊 STEP 5: Multi-Year Simulation Analysis")
    print("-" * 40)
    
    # Run 36 months (3 years) to see the progression
    result_36m = engine.run_simulation(
        start_year=2025,
        start_month=1,
        end_year=2027,
        end_month=12,
        lever_plan={}
    )
    
    kpis_36m = kpi_service.calculate_kpis(result_36m['monthly_results'], 36)
    
    print("36-Month Results:")
    print(f"  Net Sales: {kpis_36m.get('net_sales', 'N/A'):,.1f} SEK")
    print(f"  EBITDA: {kpis_36m.get('ebitda', 'N/A'):,.1f} SEK")
    print(f"  Total FTE: {kpis_36m.get('total_fte', 'N/A')}")
    
    # Compare first and last month FTE
    first_month_36 = result_36m['monthly_results'][0]
    last_month_36 = result_36m['monthly_results'][-1]
    
    print("\nFTE Growth Analysis (36 months):")
    for office_name in ['Stockholm']:  # Focus on Stockholm
        if office_name in first_month_36 and office_name in last_month_36:
            first_total = 0
            last_total = 0
            
            # Count all roles and levels
            for role_name, role_data in first_month_36[office_name].items():
                if isinstance(role_data, dict):
                    for level_name, level_data in role_data.items():
                        if isinstance(level_data, dict) and 'total' in level_data:
                            first_total += level_data['total']
            
            for role_name, role_data in last_month_36[office_name].items():
                if isinstance(role_data, dict):
                    for level_name, level_data in role_data.items():
                        if isinstance(level_data, dict) and 'total' in level_data:
                            last_total += level_data['total']
            
            growth_rate = ((last_total/first_total-1)*100) if first_total > 0 else 0
            print(f"  {office_name}: {first_total} → {last_total} FTE ({growth_rate:.1f}% growth)")
            
            # If growth is excessive, that's likely the problem
            if abs(growth_rate) > 50:  # More than 50% growth in 3 years
                print(f"    ⚠️  WARNING: Excessive growth rate detected!")
                print(f"    This could explain the negative financial results")

if __name__ == "__main__":
    investigate_financial_calculations() 