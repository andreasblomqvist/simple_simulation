#!/usr/bin/env python3

"""
Debug script to test V2 simulation engine with business plan
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.src.services.simulation_engine_v2 import (
    SimulationEngineV2, ScenarioRequest, TimeRange, Levers
)
from backend.src.services.simulation_engine_v2 import logger
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def test_v2_simulation():
    """Test V2 simulation with business plan"""
    
    # Create scenario
    scenario = ScenarioRequest(
        scenario_id="debug-test-v2",
        name="V2 Debug Test",
        time_range=TimeRange(
            start_year=2025,
            start_month=1,
            end_year=2025,
            end_month=3
        ),
        office_ids=["Oslo"],
        levers=Levers(),
        business_plan_id="20ba0f6d-a238-4ab5-a7aa-488efa393797"
    )
    
    # Create and run simulation
    engine = SimulationEngineV2()
    success = engine.initialize()
    
    if not success:
        print("X Failed to initialize engine")
        return
    
    print("Engine initialized")
    
    try:
        results = engine.run_simulation(scenario)
        
        # Check final results
        for month_key, monthly_result in results.monthly_results.items():
            print(f"\n>> Results for {month_key}:")
            
            for office_id, office_metrics in monthly_result.office_results.items():
                workforce = office_metrics.get('total_workforce', 0)
                revenue = office_metrics.get('revenue', 0)
                costs = office_metrics.get('costs', 0)
                
                print(f"  Office {office_id}: {workforce} FTE, Revenue: ${revenue:,.0f}, Costs: ${costs:,.0f}")
                
                # Check workforce by role
                workforce_by_role = office_metrics.get('workforce_by_role', {})
                for role, role_data in workforce_by_role.items():
                    if isinstance(role_data, dict):
                        total_in_role = sum(role_data.values())
                        print(f"    {role}: {total_in_role} people ({role_data})")
                    else:
                        print(f"    {role}: {role_data} people")
        
        print(f"\nTotal events: {len(results.all_events)}")
        
        # Check if we have 0 workforce issue
        has_zero_workforce = False
        for monthly_result in results.monthly_results.values():
            for office_metrics in monthly_result.office_results.values():
                if office_metrics.get('total_workforce', 0) == 0:
                    has_zero_workforce = True
                    break
        
        if has_zero_workforce:
            print("X Issue: Found months with 0 total workforce")
        else:
            print("OK All months show non-zero workforce")
            
    except Exception as e:
        print(f"X Simulation failed: {e}")
        raise

if __name__ == "__main__":
    test_v2_simulation()