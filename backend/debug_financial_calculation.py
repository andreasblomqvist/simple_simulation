#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

import json
from typing import Dict, Any

def debug_financial_calculation():
    print("=== Debug Financial Calculation Logic ===\n")
    
    # Load the business plan
    with open('data/business_plans/oslo_with_churn_test.json', 'r') as f:
        business_plan = json.load(f)
    
    print(f"Business Plan: {business_plan['office_id']}")
    print(f"Business Plan entries: {len(business_plan['entries'])}")
    
    # Manual calculation based on V2 engine logic
    print(f"\n=== Manual Financial Calculation ===")
    
    # Simulate 124 people (from test results) - January workforce
    workforce = {
        'Consultant': {'A': 11, 'AC': 3, 'C': 3, 'SrC': 3, 'AM': 4, 'M': 5, 'SrM': 5, 'PiP': 5},
        'Sales': {'A': 5, 'AC': 5, 'C': 5, 'SrC': 5, 'AM': 5, 'M': 5, 'SrM': 5, 'PiP': 5},
        'Recruitment': {'A': 5, 'AC': 5, 'C': 5, 'SrC': 5, 'AM': 5, 'M': 5, 'SrM': 5, 'PiP': 5},
        'Operations': 5  # Flat role
    }
    
    print(f"Total workforce: {sum(sum(levels.values()) if isinstance(levels, dict) else levels for levels in workforce.values())}")
    
    # Create lookup for business plan data
    bp_lookup = {}
    for entry in business_plan['entries']:
        key = f"{entry['role']}-{entry['level']}"
        bp_lookup[key] = entry
    
    print(f"\nBusiness plan lookup keys: {list(bp_lookup.keys())[:5]}...")  # Show first 5
    
    total_monthly_revenue = 0.0
    total_monthly_salary_costs = 0.0
    
    # Calculate for each role/level
    for role, levels in workforce.items():
        if isinstance(levels, dict):  # Leveled roles
            for level, count in levels.items():
                key = f"{role}-{level}"
                if key in bp_lookup:
                    bp_data = bp_lookup[key]
                    
                    # Revenue calculation
                    hourly_rate = bp_data.get('price', 0)
                    utilization = bp_data.get('utr', 0)
                    working_hours = 160
                    monthly_revenue_per_person = hourly_rate * utilization * working_hours
                    level_revenue = monthly_revenue_per_person * count
                    total_monthly_revenue += level_revenue
                    
                    # Salary calculation
                    annual_salary = bp_data.get('salary', 0)
                    monthly_salary_per_person = annual_salary / 12
                    level_salary_costs = monthly_salary_per_person * count
                    total_monthly_salary_costs += level_salary_costs
                    
                    print(f"{role} {level}: {count} people, {hourly_rate} NOK/hr, {annual_salary} NOK/year")
                    print(f"  Monthly revenue: {level_revenue:,.0f} NOK")
                    print(f"  Monthly salary costs: {level_salary_costs:,.0f} NOK")
                else:
                    print(f"WARNING: No business plan data for {key}")
        else:  # Flat roles like Operations
            key = f"{role}-General"
            if key in bp_lookup:
                bp_data = bp_lookup[key]
                count = levels
                
                # Revenue calculation (likely 0 for support roles)
                hourly_rate = bp_data.get('price', 0)
                utilization = bp_data.get('utr', 0)
                working_hours = 160
                monthly_revenue_per_person = hourly_rate * utilization * working_hours
                role_revenue = monthly_revenue_per_person * count
                total_monthly_revenue += role_revenue
                
                # Salary calculation
                annual_salary = bp_data.get('salary', 0)
                monthly_salary_per_person = annual_salary / 12
                role_salary_costs = monthly_salary_per_person * count
                total_monthly_salary_costs += role_salary_costs
                
                print(f"{role} General: {count} people, {hourly_rate} NOK/hr, {annual_salary} NOK/year")
                print(f"  Monthly revenue: {role_revenue:,.0f} NOK")
                print(f"  Monthly salary costs: {role_salary_costs:,.0f} NOK")
            else:
                print(f"WARNING: No business plan data for {key}")
    
    print(f"\n=== MONTHLY TOTALS (January) ===")
    print(f"Total Monthly Revenue: {total_monthly_revenue:,.0f} NOK")
    print(f"Total Monthly Salary Costs: {total_monthly_salary_costs:,.0f} NOK")
    print(f"Monthly EBITDA: {total_monthly_revenue - total_monthly_salary_costs:,.0f} NOK")
    
    print(f"\n=== YEARLY PROJECTIONS (if flat) ===")
    print(f"Yearly Revenue: {total_monthly_revenue * 12:,.0f} NOK")
    print(f"Yearly Salary Costs: {total_monthly_salary_costs * 12:,.0f} NOK")
    print(f"Yearly EBITDA: {(total_monthly_revenue - total_monthly_salary_costs) * 12:,.0f} NOK")
    
    # Compare to engine results
    print(f"\n=== COMPARISON TO ENGINE RESULTS ===")
    engine_jan_revenue = 7_328_360
    engine_jan_costs = 834_833
    
    print(f"Engine January Revenue: {engine_jan_revenue:,.0f} NOK")
    print(f"Manual January Revenue: {total_monthly_revenue:,.0f} NOK")
    print(f"Difference: {engine_jan_revenue - total_monthly_revenue:,.0f} NOK")
    
    print(f"Engine January Costs: {engine_jan_costs:,.0f} NOK")
    print(f"Manual January Costs: {total_monthly_salary_costs:,.0f} NOK")
    print(f"Difference: {engine_jan_costs - total_monthly_salary_costs:,.0f} NOK")

if __name__ == "__main__":
    debug_financial_calculation()