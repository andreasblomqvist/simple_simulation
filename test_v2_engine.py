#!/usr/bin/env python3
"""
Test script for V2 Simulation Engine
Tests the fixed engine with Oslo snapshot and business plan
"""
import sys
import os
import logging

# Set correct module paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from src.services.simulation_engine_v2 import ScenarioRequest, TimeRange, Levers, SimulationEngineV2Factory

def test_v2_engine():
    """Test V2 engine with Oslo scenario"""
    print("Testing V2 Simulation Engine...")
    
    # Create scenario
    scenario = ScenarioRequest(
        scenario_id='test_v2',
        name='V2 Engine Test - Oslo',
        office_ids=['Oslo'], 
        business_plan_id='oslo_realistic_complete_plan',
        time_range=TimeRange(start_year=2025, start_month=1, end_year=2025, end_month=12),
        levers=Levers()
    )
    
    # Create engine
    config = {
        'validation_enabled': False,  
        'random_seed': 12345,
        'component_configs': {
            'workforce_manager': {'random_seed': 12345},
            'snapshot_loader': {'storage_path': 'backend/data/snapshots'}
        }
    }
    
    engine = SimulationEngineV2Factory.create_engine(config)
    print("Engine created successfully")
    
    try:
        print("\nRunning 12-month simulation...")
        results = engine.run_simulation(scenario)
        
        # Check Oslo office state 
        oslo_state = engine.office_states.get('Oslo')
        if oslo_state:
            total = oslo_state.get_total_workforce()
            print(f"\nFINAL RESULTS:")
            print(f"Total workforce: {total} people")
            
            # Calculate billable ratio
            consultant_count = 0
            support_count = 0
            
            for role, levels in oslo_state.workforce.items():
                if isinstance(levels, dict):  # Leveled role
                    role_total = sum(len(people) for people in levels.values())
                    if role == 'Consultant':
                        consultant_count = role_total
                    else:
                        support_count += role_total
                    print(f"  {role}: {role_total} people")
                    
                    # Show level breakdown for consultants
                    if role == 'Consultant':
                        for level, people in levels.items():
                            if people:
                                print(f"    {level}: {len(people)} people")
                else:  # Flat role
                    support_count += len(levels)
                    print(f"  {role}: {len(levels)} people")
            
            # Calculate and display key metrics
            billable_ratio = consultant_count / total * 100 if total > 0 else 0
            print(f"\nKEY METRICS:")
            print(f"Consultant ratio: {billable_ratio:.1f}% ({consultant_count} consultants / {total} total)")
            print(f"Support staff: {support_count} people")
            
            # Determine if results are good
            if billable_ratio >= 80:
                print("EXCELLENT: Consultant ratio is healthy (>80%)")
            elif billable_ratio >= 70:
                print("ACCEPTABLE: Consultant ratio is acceptable (70-80%)")
            else:
                print("PROBLEM: Consultant ratio is too low (<70%)")
                
            # Show monthly results summary
            if results.monthly_results:
                first_month = list(results.monthly_results.values())[0]
                last_month = list(results.monthly_results.values())[-1]
                
                if 'Oslo' in first_month.office_results and 'Oslo' in last_month.office_results:
                    start_workforce = first_month.office_results['Oslo']['total_workforce']
                    end_workforce = last_month.office_results['Oslo']['total_workforce']
                    growth = ((end_workforce - start_workforce) / start_workforce * 100) if start_workforce > 0 else 0
                    
                    print(f"\nGROWTH:")
                    print(f"Starting workforce: {start_workforce} people")
                    print(f"Ending workforce: {end_workforce} people") 
                    print(f"Growth rate: {growth:.1f}%")
        
        print("\nV2 Engine test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nV2 Engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_v2_engine()
    sys.exit(0 if success else 1)