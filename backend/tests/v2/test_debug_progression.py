"""
Debug Progression Events in Engine V2

Systematically debug why progression works in isolation but fails in engine simulation.
"""

import sys
import json
from pathlib import Path
from datetime import date
from collections import defaultdict

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_debug_progression():
    """Debug progression step by step"""
    print("DEBUGGING PROGRESSION EVENTS IN ENGINE V2")
    print("=" * 50)
    
    try:
        from src.services.simulation_engine_v2 import (
            SimulationEngineV2Factory, ScenarioRequest, TimeRange, Levers,
            Person, CATMatrix, OfficeState
        )
        from src.services.workforce_manager_v2 import WorkforceManagerV2
        
        # 1. Setup test data
        print("1. Setting up test scenario...")
        
        # Create Alice with specific details
        alice = Person(
            id="ALICE_DEBUG",
            current_role="Consultant",
            current_level="A",
            current_office="london",
            hire_date=date(2023, 6, 1),  # Hired June 2023
            current_level_start=date(2023, 6, 1),  # Started at A level when hired
            events=[],
            is_active=True
        )
        
        # Test date: January 2024 (progression month for A level)
        test_date = date(2024, 1, 15)
        alice_tenure = alice.get_level_tenure_months(test_date)
        
        print(f"   Alice: {alice.current_role} {alice.current_level}")
        print(f"   Hired: {alice.hire_date}")
        print(f"   Level start: {alice.current_level_start}")
        print(f"   Test date: {test_date}")
        print(f"   Tenure: {alice_tenure} months")
        
        print("\\nAlice date verification:")
        print(f"   hire_date: {alice.hire_date} ({type(alice.hire_date)})")
        print(f"   current_level_start: {alice.current_level_start} ({type(alice.current_level_start)})")
        print(f"   test_date: {test_date} ({type(test_date)})")
        
        # Manual tenure calculation
        manual_tenure = (test_date.year - alice.current_level_start.year) * 12 + (test_date.month - alice.current_level_start.month)
        print(f"   Manual tenure calculation: {manual_tenure} months")
        
        # 2. Load CAT matrix
        print("\n2. Loading CAT matrix...")
        
        test_data_dir = Path(__file__).parent / "test_data"
        with open(test_data_dir / "cat_matrices_correct.json") as f:
            cat_data = json.load(f)
        
        consultant_cat = CATMatrix(
            progression_probabilities=cat_data['Consultant']['progression_probabilities']
        )
        
        # Check Alice's progression probability
        wm = WorkforceManagerV2()
        wm.initialize()
        
        alice_prob = wm.calculate_cat_probability(alice, consultant_cat, test_date)
        cat_category = wm._get_cat_category(alice_tenure)
        
        print(f"   CAT category: {cat_category}")
        print(f"   Progression probability: {alice_prob}")
        print(f"   Level progression months: {wm.level_progression_months.get('A', 'NOT FOUND')}")
        
        # 3. Test direct workforce manager progression (using a separate Alice to avoid modifying the original)
        print("\n3. Testing direct workforce manager progression...")
        
        # Create a separate Alice for direct testing to avoid modifying the original
        alice_direct = Person(
            id="ALICE_DIRECT",
            current_role="Consultant",
            current_level="A",
            current_office="london",
            hire_date=date(2023, 6, 1),
            current_level_start=date(2023, 6, 1),
            events=[],
            is_active=True
        )
        
        # Set seed for reproducibility
        import random
        random.seed(42)
        
        direct_events = wm.process_progression([alice_direct], consultant_cat, test_date)
        
        print(f"   Direct call result: {len(direct_events)} events")
        if direct_events:
            for event in direct_events:
                print(f"      Event: {event.event_type.value}")
                print(f"      From: {event.details.get('from_level')} -> To: {event.details.get('to_level')}")
        else:
            print("      No events generated - checking why...")
            
            # Debug the progression logic step by step
            print(f"      Month check: {test_date.month} in {wm.level_progression_months.get('A', [])}? {test_date.month in wm.level_progression_months.get('A', [])}")
            print(f"      Tenure check: {alice_tenure} >= {wm.progression_config.minimum_tenure_months}? {alice_tenure >= wm.progression_config.minimum_tenure_months}")
            print(f"      Active check: {alice.is_active}")
            
            # Test the random progression decision
            random.seed(42)
            rand_val = random.random()
            print(f"      Random value: {rand_val:.3f}")
            print(f"      Would progress: {rand_val < alice_prob}")
        
        # 4. Create engine and test engine progression
        print("\n4. Testing engine progression processing...")
        
        engine = SimulationEngineV2Factory.create_test_engine(random_seed=42)
        
        # Create minimal office state
        office_state = OfficeState(
            name="london",
            workforce={"Consultant": {"A": [alice]}},
            business_plan=None,
            snapshot=None,
            cat_matrices={"Consultant": consultant_cat},
            economic_parameters=None
        )
        
        # Manually set office state in engine
        engine.office_states = {"london": office_state}
        
        print(f"   Office state workforce: {len(office_state.workforce['Consultant']['A'])} people")
        print(f"   Office CAT matrices: {list(office_state.cat_matrices.keys())}")
        
        # Check Alice's state right after putting in office state
        alice_in_office = office_state.workforce['Consultant']['A'][0]
        print(f"   Alice in office current_level_start: {alice_in_office.current_level_start}")
        print(f"   Alice in office events count: {len(alice_in_office.events)}")
        if alice_in_office.events:
            for event in alice_in_office.events:
                print(f"      Event: {event.event_type.value} on {event.date}")
        
        # Test engine's month processing with debugging
        print("\n5. Debugging engine month processing...")
        
        # Set the same seed
        random.seed(42)
        
        # Simulate what happens in _process_office_month
        month_events = []
        current_date = test_date
        
        print(f"   Processing office month: {current_date}")
        
        # Check if workforce manager is available
        print(f"   Workforce manager available: {engine.workforce_manager is not None}")
        print(f"   CAT matrices available: {office_state.cat_matrices is not None}")
        
        if engine.workforce_manager and office_state.cat_matrices:
            print("   Entering progression processing loop...")
            
            for role, levels in office_state.workforce.items():
                print(f"      Processing role: {role}")
                
                # Get role-specific CAT matrix
                role_cat_matrix = office_state.cat_matrices.get(role)
                print(f"         CAT matrix for {role}: {role_cat_matrix is not None}")
                
                if role_cat_matrix:
                    for level, people in levels.items():
                        print(f"         Processing level: {level}")
                        print(f"            Number of people: {len(people)}")
                        
                        if people:
                            # This is the actual engine call
                            progression_events = engine.workforce_manager.process_progression(
                                people, role_cat_matrix, current_date
                            )
                            print(f"            Events generated: {len(progression_events)}")
                            
                            if progression_events:
                                for event in progression_events:
                                    print(f"               Event: {event.event_type.value} {event.details.get('from_level')} -> {event.details.get('to_level')}")
                            
                            month_events.extend(progression_events)
                        else:
                            print("            No people to process")
                else:
                    print(f"         No CAT matrix for {role}")
        else:
            print("   Progression processing skipped - missing components")
            print(f"      workforce_manager: {engine.workforce_manager is not None}")
            print(f"      cat_matrices: {office_state.cat_matrices is not None}")
        
        print(f"\n   Total engine events: {len(month_events)}")
        
        # 6. Compare results
        print("\n6. COMPARISON ANALYSIS")
        print("-" * 30)
        
        print(f"Direct WorkforceManager call: {len(direct_events)} events")
        print(f"Engine simulation call: {len(month_events)} events")
        
        if len(direct_events) != len(month_events):
            print("MISMATCH: Different number of events generated!")
            
            # Let's check if the workforce manager instances are different
            print("\n7. DEEP DEBUGGING")
            print("-" * 20)
            
            print("Comparing WorkforceManager instances:")
            print(f"   Direct WM level_progression_months: {wm.level_progression_months}")
            print(f"   Engine WM level_progression_months: {engine.workforce_manager.level_progression_months}")
            
            print("Comparing progression config:")
            print(f"   Direct WM minimum_tenure_months: {wm.progression_config.minimum_tenure_months}")
            print(f"   Engine WM minimum_tenure_months: {engine.workforce_manager.progression_config.minimum_tenure_months}")
            
            # Test the engine's workforce manager directly
            print("\nTesting engine's workforce manager directly:")
            random.seed(42)
            engine_direct_events = engine.workforce_manager.process_progression([alice], consultant_cat, test_date)
            print(f"   Engine WM direct call: {len(engine_direct_events)} events")
            
            # Let's debug the random seed issue
            print("\nTesting random seed behavior:")
            
            # Test the progression decision logic directly
            alice_prob = engine.workforce_manager.calculate_cat_probability(alice, consultant_cat, test_date)
            print(f"   Engine WM calculated probability: {alice_prob}")
            
            # Test if the progression month check passes
            level_progression_months = engine.workforce_manager.level_progression_months.get('A', [])
            is_progression_month = test_date.month in level_progression_months
            print(f"   Is progression month check: {is_progression_month}")
            
            # Test tenure requirement
            tenure_months = alice.get_level_tenure_months(test_date)
            min_tenure = engine.workforce_manager.progression_config.minimum_tenure_months
            meets_tenure = tenure_months >= min_tenure
            print(f"   Meets tenure requirement: {meets_tenure} ({tenure_months} >= {min_tenure})")
            
            # Test the actual should_progress decision
            random.seed(42)
            should_progress = engine.workforce_manager._should_person_progress(alice, 'A', consultant_cat, test_date)
            print(f"   Should progress decision: {should_progress}")
            
            # Check random values
            random.seed(42)
            rand_val1 = random.random()
            print(f"   Random value 1: {rand_val1:.3f}")
            
            random.seed(42)
            rand_val2 = random.random()
            print(f"   Random value 2: {rand_val2:.3f}")
            
            print(f"   Probability threshold: {alice_prob:.3f}")
            print(f"   Should progress: {rand_val1 < alice_prob}")
            
            # DEBUG: Check Alice's dates in engine context
            print("\\nDebugging Alice's dates in engine context:")
            alice_in_engine = office_state.workforce['Consultant']['A'][0]
            print(f"   Alice ID: {alice_in_engine.id}")
            print(f"   Alice hire_date: {alice_in_engine.hire_date}")
            print(f"   Alice current_level_start: {alice_in_engine.current_level_start}")
            print(f"   Test date: {test_date}")
            
            engine_tenure = alice_in_engine.get_level_tenure_months(test_date)
            direct_tenure = alice.get_level_tenure_months(test_date)
            
            print(f"   Engine Alice tenure: {engine_tenure} months")
            print(f"   Direct Alice tenure: {direct_tenure} months")
            
            print("\\nDate calculation debugging:")
            print(f"   Engine Alice hire_date type: {type(alice_in_engine.hire_date)}")
            print(f"   Direct Alice hire_date type: {type(alice.hire_date)}")
            
            if alice_in_engine.id != alice.id:
                print("   WARNING: Different Alice objects!")
            
            if alice_in_engine is alice:
                print("   Same Alice object reference")
            else:
                print("   DIFFERENT Alice object reference")
                
            print("\\nTiming verification:")
            print(f"   Expected tenure: 7 months (June 2023 -> Jan 2024)")
            print(f"   Actual calculation: ({test_date.year} - {alice_in_engine.current_level_start.year}) * 12 + ({test_date.month} - {alice_in_engine.current_level_start.month})")
            print(f"   = ({test_date.year - alice_in_engine.current_level_start.year}) * 12 + ({test_date.month - alice_in_engine.current_level_start.month})")
            print(f"   = {(test_date.year - alice_in_engine.current_level_start.year) * 12 + (test_date.month - alice_in_engine.current_level_start.month)} months")
            
        else:
            print("MATCH: Same number of events generated!")
        
        # 7. Final assessment
        print("\n8. FINAL ASSESSMENT")
        print("=" * 25)
        
        if len(month_events) > 0:
            print("SUCCESS: Engine progression is working!")
            return True
        else:
            print("FAILURE: Engine progression is still broken")
            print("\nPossible causes:")
            print("- WorkforceManager initialization difference")
            print("- CAT matrix structure mismatch")
            print("- Random seed not being set properly")
            print("- Progression configuration not loaded")
            return False
            
    except Exception as e:
        print(f"\nERROR: Debug test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_debug_progression()
    if success:
        print("\nProgression debugging complete - issue resolved!")
    else:
        print("\nProgression debugging complete - issue identified!")