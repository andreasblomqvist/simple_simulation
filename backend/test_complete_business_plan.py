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

def test_complete_business_plan():
    print("=== Testing V2 Engine with Complete Business Plan ===\n")
    
    # Create V2 engine
    engine = SimulationEngineV2()
    
    # Initialize
    print(f"Initializing V2 engine...")
    if not engine.initialize():
        print("ERROR: Failed to initialize V2 engine")
        return
    
    # Create scenario request with new complete business plan
    scenario_request = ScenarioRequest(
        scenario_id="oslo_complete_test",
        name="Oslo Complete Business Plan Test",
        time_range=TimeRange(
            start_year=2025,
            start_month=1,
            end_year=2025, 
            end_month=1  # Just test January
        ),
        office_ids=['Oslo'],
        levers=Levers(),
        business_plan_id="oslo_complete_business_plan"
    )
    
    print(f"Running simulation...")
    
    # Run simulation
    results = engine.run_simulation(scenario_request)
    
    print(f"\nJanuary 2025 Financial Results:")
    
    # Get January results
    january_key = "2025-01"
    if january_key in results.monthly_results and 'Oslo' in results.monthly_results[january_key].office_results:
        oslo_results = results.monthly_results[january_key].office_results['Oslo']
        
        revenue = oslo_results.get('revenue', 0)
        costs = oslo_results.get('costs', 0) 
        salary_costs = oslo_results.get('salary_costs', 0)
        
        print(f"  Revenue: {revenue:,.0f} NOK")
        print(f"  Salary Costs: {salary_costs:,.0f} NOK")
        print(f"  Total Costs: {costs:,.0f} NOK")
        print(f"  EBITDA: {revenue - costs:,.0f} NOK")
        
        # Calculate operating costs
        operating_costs = costs - salary_costs
        print(f"  Operating Costs: {operating_costs:,.0f} NOK")
        
        # Show workforce
        total_workforce = oslo_results.get('total_workforce', 0)
        print(f"  Total Workforce: {total_workforce} people")
        
        if operating_costs > 0:
            print(f"\n✅ SUCCESS: Operating costs now included in calculations!")
        else:
            print(f"\n❌ ISSUE: Operating costs still missing from calculations")
    else:
        print("ERROR: Could not find January 2025 Oslo results")

if __name__ == "__main__":
    test_complete_business_plan()