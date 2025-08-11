#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from src.services.simulation_engine_v2 import (
    SimulationEngineV2, ScenarioRequest, TimeRange, Levers
)
import json
import logging

# Setup detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

def test_financial_kpis():
    print("=== Testing V2 Engine Financial KPIs ===\n")
    
    # Create V2 engine
    engine = SimulationEngineV2()
    
    # Initialize
    print(f"Initializing V2 engine...")
    if not engine.initialize():
        print("ERROR: Failed to initialize V2 engine")
        return
    
    # Create scenario request
    scenario_request = ScenarioRequest(
        scenario_id="oslo_financial_test",
        name="Oslo Financial Test",
        time_range=TimeRange(
            start_year=2025,
            start_month=1,
            end_year=2025, 
            end_month=12
        ),
        office_ids=['Oslo'],
        levers=Levers(),
        business_plan_id="oslo_with_churn_test"
    )
    
    print(f"Running simulation...")
    
    # Run simulation
    results = engine.run_simulation(scenario_request)
    
    print(f"\nFinancial KPIs Analysis:")
    
    # Analyze each month's financial data
    total_yearly_revenue = 0
    total_yearly_salary_costs = 0
    total_yearly_operation_costs = 0
    
    for month_key in sorted(results.monthly_results.keys()):
        month_results = results.monthly_results[month_key]
        
        if 'Oslo' in month_results.office_results:
            oslo_results = month_results.office_results['Oslo']
            
            # Extract financial metrics
            revenue = oslo_results.get('revenue', 0)
            costs = oslo_results.get('costs', 0) 
            salary_costs = oslo_results.get('salary_costs', 0)
            
            total_yearly_revenue += revenue
            total_yearly_salary_costs += salary_costs
            total_yearly_operation_costs += costs
            
            print(f"\n{month_key} Oslo Financial Results:")
            print(f"  Revenue: {revenue:,.0f} NOK")
            print(f"  Salary Costs: {salary_costs:,.0f} NOK")
            print(f"  Total Costs: {costs:,.0f} NOK")
            print(f"  EBITDA: {revenue - costs:,.0f} NOK")
    
    print(f"\n=== YEARLY FINANCIAL SUMMARY ===")
    print(f"Net Sales (Total Revenue): {total_yearly_revenue:,.0f} NOK")
    print(f"Total Salary Cost: {total_yearly_salary_costs:,.0f} NOK")
    print(f"Total Operation Cost: {total_yearly_operation_costs:,.0f} NOK")
    print(f"Yearly EBITDA: {total_yearly_revenue - total_yearly_operation_costs:,.0f} NOK")
    print(f"EBITDA Margin: {((total_yearly_revenue - total_yearly_operation_costs) / total_yearly_revenue * 100):.1f}%")
    
    # Show workforce growth impact
    jan_workforce = 0
    dec_workforce = 0
    
    if '2025-01' in results.monthly_results and 'Oslo' in results.monthly_results['2025-01'].office_results:
        jan_workforce = results.monthly_results['2025-01'].office_results['Oslo'].get('total_workforce', 0)
    
    if '2025-12' in results.monthly_results and 'Oslo' in results.monthly_results['2025-12'].office_results:
        dec_workforce = results.monthly_results['2025-12'].office_results['Oslo'].get('total_workforce', 0)
    
    print(f"\n=== WORKFORCE GROWTH ===")
    print(f"January Workforce: {jan_workforce} people")
    print(f"December Workforce: {dec_workforce} people")
    print(f"Net Growth: {dec_workforce - jan_workforce} people")
    print(f"Growth Rate: {((dec_workforce - jan_workforce) / jan_workforce * 100):.1f}%")

if __name__ == "__main__":
    test_financial_kpis()