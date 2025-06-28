#!/usr/bin/env python3
"""
Debug why the simulation can produce negative financials when it should be impossible
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.kpi_service import KPIService
import random

def debug_negative_financials():
    """Debug the simulation to find why it can produce negative values"""
    
    print("🚨 DEBUGGING NEGATIVE FINANCIALS")
    print("=" * 60)
    
    # Seed for reproducible results
    random.seed(42)
    
    # Create engine and test with EXTREME aggressive rates
    engine = SimulationEngine()
    kpi_service = KPIService()
    
    print("📊 Testing with EXTREME aggressive rates to see if we can break it...")
    print("-" * 50)
    
    # Create an extreme test scenario
    extreme_levers = {
        'Stockholm': {
            'Consultant': {
                'A': {
                    'recruitment_1': 50.0,  # 50% monthly recruitment (impossible but let's test)
                    'churn_1': 1.0,         # 1% churn
                    'progression_1': 90.0   # 90% progression in January
                },
                'AC': {
                    'recruitment_1': 0.0,
                    'churn_1': 1.0,
                    'progression_1': 90.0
                },
                'C': {
                    'recruitment_1': 0.0,
                    'churn_1': 1.0,
                    'progression_1': 90.0
                }
            }
        }
    }
    
    print("🧪 EXTREME TEST SCENARIO:")
    print("- A level: 50% monthly recruitment, 90% progression")
    print("- AC/C levels: 90% progression")
    print("- This should cause massive growth but NEVER negative profits")
    
    try:
        # Run 1 month simulation with extreme rates
        results = engine.run_simulation(2025, 1, 2025, 1, extreme_levers)
        
        print("\n📊 Results after 1 month with EXTREME rates:")
        print("-" * 50)
        
        # Check Stockholm A level
        stockholm_a = engine.offices['Stockholm'].roles['Consultant']['A']
        print(f"Stockholm A level: {stockholm_a.total} people")
        
        # Calculate revenue and costs manually
        from backend.src.services.simulation_engine import Month
        stockholm_office = engine.offices['Stockholm']
        
        revenue = engine.calculate_revenue(stockholm_office, Month.JAN)
        costs = engine.calculate_costs(stockholm_office, Month.JAN)
        profit = engine.calculate_profit(stockholm_office, Month.JAN)
        margin = engine.calculate_profit_margin(stockholm_office, Month.JAN)
        
        print(f"Stockholm revenue: {revenue:,.0f} SEK")
        print(f"Stockholm costs:   {costs:,.0f} SEK")
        print(f"Stockholm profit:  {profit:,.0f} SEK")
        print(f"Stockholm margin:  {margin:.1f}%")
        
        # Check if any values are negative
        if revenue < 0:
            print("🚨 REVENUE IS NEGATIVE! This should be impossible!")
        if costs < 0:
            print("🚨 COSTS ARE NEGATIVE! This should be impossible!")
        if profit < 0:
            print("⚠️  Profit is negative (expected with extreme rates)")
        
        # Let's also check individual level calculations
        print("\n📊 Individual Level Analysis:")
        print("-" * 50)
        
        for role_name, role_data in stockholm_office.roles.items():
            if role_name == 'Consultant':
                for level_name, level in role_data.items():
                    count = level.total
                    if count > 0:
                        price = level.price_1
                        salary = level.salary_1
                        utr = level.utr_1
                        
                        # Calculate per-person values
                        billable_hours = kpi_service.working_hours_per_month * utr
                        revenue_per_person = billable_hours * price
                        cost_per_person = salary * (1 + kpi_service.total_employment_cost_rate)
                        profit_per_person = revenue_per_person - cost_per_person
                        
                        print(f"{level_name}: {count} people, {profit_per_person:,.0f} SEK profit/person")
                        
                        # Check for impossible values
                        if revenue_per_person < 0:
                            print(f"🚨 {level_name} revenue per person is NEGATIVE!")
                        if cost_per_person < 0:
                            print(f"🚨 {level_name} cost per person is NEGATIVE!")
        
    except Exception as e:
        print(f"🚨 SIMULATION CRASHED: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🔍 INVESTIGATING POTENTIAL BUGS:")
    print("-" * 50)
    
    # Let's check if there are any hardcoded negative values or calculation errors
    print("1. Checking for hardcoded negative multipliers...")
    
    # Check the calculate_revenue method
    print("2. Checking revenue calculation method...")
    
    # Create a simple test case
    test_office = engine.offices['Stockholm']
    test_month = Month.JAN
    
    # Manually trace through revenue calculation
    print("3. Manual revenue calculation trace:")
    
    total_revenue = 0
    for role_name, role_data in test_office.roles.items():
        if role_name == 'Consultant':
            for level_name, level in role_data.items():
                count = level.total
                price = getattr(level, f'price_{test_month.value}')
                utr = getattr(level, f'utr_{test_month.value}')
                
                print(f"   {level_name}: {count} × {price} × {kpi_service.working_hours_per_month} × {utr}")
                
                level_revenue = count * price * kpi_service.working_hours_per_month * utr
                total_revenue += level_revenue
                
                if level_revenue < 0:
                    print(f"🚨 {level_name} level revenue is negative: {level_revenue}")
                    print(f"    count={count}, price={price}, hours={kpi_service.working_hours_per_month}, utr={utr}")
    
    print(f"Manual total revenue: {total_revenue:,.0f} SEK")
    
    print("\n✅ ANALYSIS COMPLETE")
    print("If we see negative values above, there's a bug in the calculation logic.")
    print("If all values are positive, the issue is elsewhere (likely in KPI aggregation).")

if __name__ == "__main__":
    debug_negative_financials() 