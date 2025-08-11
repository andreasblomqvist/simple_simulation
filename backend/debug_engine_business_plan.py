#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from src.services.simulation_engine_v2 import SimulationEngineV2, ScenarioRequest, TimeRange, Levers
from src.services.business_plan_storage import business_plan_storage
import json

def debug_business_plan_loading():
    print("=== Debugging Business Plan Loading ===\n")
    
    # 1. Check if oslo_complete_business_plan exists
    plan = business_plan_storage.get_plan("oslo_complete_business_plan")
    if plan:
        print(f"OK Found oslo_complete_business_plan:")
        print(f"  - ID: {plan['id']}")
        print(f"  - Office: {plan['office_id']}")
        print(f"  - Entries: {len(plan.get('entries', []))}")
        
        # Show first entry structure
        entries = plan.get('entries', [])
        if entries:
            first_entry = entries[0]
            print(f"  - First entry: {first_entry['role']}/{first_entry['level']}")
            print(f"  - Operating costs in entry:")
            
            operating_cost_fields = [
                'office_rent', 'external_representation', 'internal_representation',
                'external_services', 'it_related_staff', 'education', 'client_loss',
                'office_related', 'other_expenses'
            ]
            
            total_op_costs = 0
            for field in operating_cost_fields:
                value = first_entry.get(field, 0)
                if value > 0:
                    print(f"    {field}: {value}")
                    total_op_costs += value
            
            print(f"    TOTAL OPERATING COSTS: {total_op_costs}")
            
    else:
        print("ERROR oslo_complete_business_plan not found")
        return
    
    # 2. Test the unified plan lookup
    unified_plan = business_plan_storage.get_unified_plan("oslo_complete_business_plan")
    if unified_plan:
        print(f"\nOK Unified plan structure:")
        print(f"  - ID: {unified_plan['id']}")
        print(f"  - Office: {unified_plan['office_id']}")
        print(f"  - Monthly plans: {len(unified_plan.get('monthly_plans', {}))}")
        
        # Check if monthly plans have entries
        monthly_plans = unified_plan.get('monthly_plans', {})
        if monthly_plans:
            first_month = list(monthly_plans.keys())[0]
            first_monthly_plan = monthly_plans[first_month]
            entries = first_monthly_plan.get('entries', [])
            print(f"  - First month ({first_month}) has {len(entries)} entries")
    else:
        print("ERROR Unified plan not found")
        return
    
    # 3. Test engine business plan data lookup
    engine = SimulationEngineV2()
    engine.initialize()
    
    # Create a test scenario
    scenario_request = ScenarioRequest(
        scenario_id="debug_test",
        name="Debug Test",
        time_range=TimeRange(start_year=2025, start_month=1, end_year=2025, end_month=1),
        office_ids=['Oslo'],
        levers=Levers(),
        business_plan_id="oslo_complete_business_plan"
    )
    
    # Try to initialize office (this loads business plan)
    print(f"\n=== Testing Engine Business Plan Loading ===")
    try:
        # This should load the business plan
        results = engine.run_simulation(scenario_request)
        
        # Check what business plan data the engine has
        oslo_state = engine.office_states.get('Oslo')
        if oslo_state and oslo_state.business_plan:
            print(f"OK Engine loaded business plan for Oslo")
            bp = oslo_state.business_plan
            print(f"  - Structure keys: {list(bp.keys())}")
            
            # Test the actual lookup function
            test_data = engine._get_business_plan_data_for_role_level('Oslo', 'Consultant', 'A')
            if test_data:
                print(f"OK Found business plan data for Consultant/A:")
                for key, value in test_data.items():
                    print(f"    {key}: {value}")
            else:
                print("ERROR Could not find business plan data for Consultant/A")
        else:
            print("ERROR Engine did not load business plan")
            
    except Exception as e:
        print(f"ERROR Error running simulation: {e}")

if __name__ == "__main__":
    debug_business_plan_loading()