#!/usr/bin/env python3
"""
Comprehensive test script to debug print the entire financial calculation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.kpi_service import KPIService
import random

def debug_full_calculation():
    """Debug print the entire financial calculation step by step"""
    
    print("🔍 COMPREHENSIVE FINANCIAL CALCULATION DEBUG")
    print("=" * 70)
    
    # Seed for reproducible results
    random.seed(42)
    
    # Create engine and KPI service
    engine = SimulationEngine()
    kpi_service = KPIService()
    
    print("\n📊 STEP 1: Initial Setup")
    print("-" * 50)
    
    # Access Stockholm A-level properly
    stockholm_a_level = engine.offices['Stockholm'].roles['Consultant']['A']
    print(f"UTR (Utilization Rate): {stockholm_a_level.utr_1}")
    print(f"Working hours per month: {kpi_service.working_hours_per_month}")
    print(f"Employment cost rate: {kpi_service.total_employment_cost_rate}")
    
    print("\n📊 STEP 2: Initial Stockholm State")
    print("-" * 50)
    print(f"Initial Stockholm A-level: {stockholm_a_level.total} people")
    print(f"Initial Stockholm A-level salary: {stockholm_a_level.salary_1} SEK/month")
    print(f"Initial Stockholm A-level price: {stockholm_a_level.price_1} SEK/hour")
    
    # Run simulation for 1 month
    print("\n📊 STEP 3: Running 1-Month Simulation")
    print("-" * 50)
    results = engine.run_simulation(2025, 1, 2025, 1, {})
    
    print("\n📊 STEP 4: Post-Simulation State")
    print("-" * 50)
    stockholm_a_final = engine.offices['Stockholm'].roles['Consultant']['A']
    print(f"Final Stockholm A-level: {stockholm_a_final.total} people")
    print(f"Final Stockholm A-level salary: {stockholm_a_final.salary_1} SEK/month")
    print(f"Final Stockholm A-level price: {stockholm_a_final.price_1} SEK/hour")
    
    print("\n📊 STEP 5: Manual Revenue Calculation for Stockholm A-level")
    print("-" * 50)
    
    # Manual calculation for Stockholm A-level
    a_count = stockholm_a_final.total
    a_price = stockholm_a_final.price_1
    a_salary = stockholm_a_final.salary_1
    a_utr = stockholm_a_final.utr_1
    
    print(f"A-level count: {a_count}")
    print(f"A-level price: {a_price} SEK/hour")
    print(f"A-level salary: {a_salary} SEK/month")
    print(f"A-level UTR: {a_utr}")
    
    # Revenue calculation
    billable_hours = kpi_service.working_hours_per_month * a_utr
    revenue_per_person = billable_hours * a_price
    total_revenue_a = revenue_per_person * a_count
    
    print(f"Billable hours per month: {kpi_service.working_hours_per_month} * {a_utr} = {billable_hours}")
    print(f"Revenue per A-level: {billable_hours} * {a_price} = {revenue_per_person:,.0f} SEK/month")
    print(f"Total A-level revenue: {revenue_per_person:,.0f} * {a_count} = {total_revenue_a:,.0f} SEK/month")
    
    # Cost calculation
    cost_per_person = a_salary * (1 + kpi_service.total_employment_cost_rate)
    total_cost_a = cost_per_person * a_count
    
    print(f"Cost per A-level: {a_salary} * (1 + {kpi_service.total_employment_cost_rate}) = {cost_per_person:,.0f} SEK/month")
    print(f"Total A-level cost: {cost_per_person:,.0f} * {a_count} = {total_cost_a:,.0f} SEK/month")
    
    # Profit calculation
    profit_per_person = revenue_per_person - cost_per_person
    total_profit_a = total_revenue_a - total_cost_a
    margin_a = (profit_per_person / revenue_per_person) * 100
    
    print(f"Profit per A-level: {revenue_per_person:,.0f} - {cost_per_person:,.0f} = {profit_per_person:,.0f} SEK/month")
    print(f"Total A-level profit: {total_profit_a:,.0f} SEK/month")
    print(f"A-level margin: {margin_a:.1f}%")
    
    print("\n📊 STEP 6: Compare with Your Spreadsheet")
    print("-" * 50)
    
    # Compare with user's spreadsheet values for A-level
    expected_revenue = 140648  # From user's spreadsheet
    expected_cost = 80273     # From user's spreadsheet  
    expected_profit = expected_revenue - expected_cost
    expected_margin = (expected_profit / expected_revenue) * 100
    
    print(f"Your spreadsheet A-level (1 person):")
    print(f"  Revenue: {expected_revenue:,} SEK")
    print(f"  Cost: {expected_cost:,} SEK") 
    print(f"  Profit: {expected_profit:,} SEK ({expected_margin:.1f}%)")
    
    print(f"\nSimulation A-level (1 person):")
    print(f"  Revenue: {revenue_per_person:,.0f} SEK")
    print(f"  Cost: {cost_per_person:,.0f} SEK")
    print(f"  Profit: {profit_per_person:,.0f} SEK ({margin_a:.1f}%)")
    
    print(f"\nDifference:")
    print(f"  Revenue diff: {revenue_per_person - expected_revenue:,.0f} SEK")
    print(f"  Cost diff: {cost_per_person - expected_cost:,.0f} SEK")
    print(f"  Profit diff: {profit_per_person - expected_profit:,.0f} SEK")
    
    print("\n📊 STEP 7: Engine Revenue/Cost Methods")
    print("-" * 50)
    
    # Test the engine's own calculation methods
    from backend.src.services.simulation_engine import Month
    stockholm_office = engine.offices['Stockholm']
    
    engine_revenue = engine.calculate_revenue(stockholm_office, Month.JAN)
    engine_costs = engine.calculate_costs(stockholm_office, Month.JAN)
    engine_profit = engine.calculate_profit(stockholm_office, Month.JAN)
    engine_margin = engine.calculate_profit_margin(stockholm_office, Month.JAN)
    
    print(f"Engine revenue calculation: {engine_revenue:,.0f} SEK")
    print(f"Engine costs calculation: {engine_costs:,.0f} SEK")
    print(f"Engine profit calculation: {engine_profit:,.0f} SEK")
    print(f"Engine margin calculation: {engine_margin:.1f}%")
    
    print("\n✅ ANALYSIS COMPLETE!")
    print(f"   Manual A-level profit: {profit_per_person:,.0f} SEK per person")
    print(f"   Expected from spreadsheet: {expected_profit:,} SEK per person") 
    print(f"   Engine total profit: {engine_profit:,.0f} SEK (all levels)")

if __name__ == "__main__":
    debug_full_calculation() 