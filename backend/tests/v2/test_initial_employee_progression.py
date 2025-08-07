"""
Test progression for initial employees specifically
"""

import sys
from pathlib import Path
from datetime import date
import json

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_initial_employee_progression():
    """Test that initial employees get progression events"""
    print("Testing Initial Employee Progression")
    print("=" * 45)
    
    from src.services.simulation_engine_v2 import (
        Person, OfficeState, CATMatrix
    )
    from src.services.workforce_manager_v2 import WorkforceManagerV2
    
    # 1. Create workforce manager
    print("1. Setting up workforce manager...")
    wm = WorkforceManagerV2()
    wm.initialize()
    
    # 2. Create Alice (A level, 7 months tenure by Jan 2024)
    print("\n2. Creating Alice (initial employee)...")
    
    alice = Person(
        id='ALICE_001',
        current_role='Consultant',
        current_level='A',
        current_office='london',
        hire_date=date(2023, 6, 1),  # Hired June 2023
        current_level_start=date(2023, 6, 1),
        events=[],
        is_active=True
    )
    
    jan_2024 = date(2024, 1, 15)
    tenure = alice.get_level_tenure_months(jan_2024)
    cat_category = wm._get_cat_category(tenure)
    
    print(f"   Alice details:")
    print(f"   - Role: {alice.current_role}")
    print(f"   - Level: {alice.current_level}")
    print(f"   - Hire date: {alice.hire_date}")
    print(f"   - Tenure by Jan 2024: {tenure} months")
    print(f"   - CAT category: {cat_category}")
    
    # 3. Load correct CAT matrix
    print("\n3. Loading CAT matrix...")
    
    test_data_dir = Path(__file__).parent / "test_data"
    with open(test_data_dir / "cat_matrices_correct.json") as f:
        cat_data = json.load(f)
    
    consultant_cat = CATMatrix(
        progression_probabilities=cat_data['Consultant']['progression_probabilities']
    )
    
    # Check probability
    alice_prob = consultant_cat.get_probability('A', cat_category)
    print(f"   A level {cat_category} probability: {alice_prob}")
    
    # 4. Check if January is a progression month for A level
    print("\n4. Checking progression month...")
    
    a_progression_months = wm.level_progression_months.get('A', [])
    is_progression_month = jan_2024.month in a_progression_months
    
    print(f"   A level progression months: {a_progression_months}")
    print(f"   Is January a progression month? {is_progression_month}")
    
    # 5. Check minimum tenure requirement
    print("\n5. Checking tenure requirement...")
    
    min_tenure = wm.progression_config.minimum_tenure_months
    meets_requirement = tenure >= min_tenure
    
    print(f"   Minimum tenure required: {min_tenure} months")
    print(f"   Alice's tenure: {tenure} months")
    print(f"   Meets requirement? {meets_requirement}")
    
    # 6. Process progression directly
    print("\n6. Processing progression for Alice...")
    
    # Set seed for reproducibility
    import random
    random.seed(42)
    
    events = wm.process_progression([alice], consultant_cat, jan_2024)
    
    if events:
        print(f"   SUCCESS: Generated {len(events)} progression event(s)!")
        for event in events:
            print(f"   Event: {event.event_type.value}")
            print(f"   - From: {event.details.get('from_level')}")
            print(f"   - To: {event.details.get('to_level')}")
            print(f"   - CAT: {event.details.get('cat_category')}")
    else:
        print("   NO EVENTS generated")
        
        # Debug why not
        print("\n   Debugging...")
        
        # Manually check the logic flow
        print(f"   Step 1: Check progression month for level A")
        print(f"      Month {jan_2024.month} in {a_progression_months}? {jan_2024.month in a_progression_months}")
        
        if jan_2024.month in a_progression_months:
            print(f"   Step 2: Check tenure requirement")
            print(f"      {tenure} >= {min_tenure}? {tenure >= min_tenure}")
            
            if tenure >= min_tenure:
                print(f"   Step 3: Check progression probability")
                print(f"      CAT category: {cat_category}")
                print(f"      Probability: {alice_prob}")
                
                # Test random value
                random.seed(42)
                rand_val = random.random()
                print(f"      Random value: {rand_val:.3f}")
                print(f"      Would progress? {rand_val < alice_prob}")
    
    # 7. Test in a simulated office state
    print("\n7. Testing in office state context...")
    
    office_state = OfficeState(
        name='london',
        workforce={'Consultant': {'A': [alice]}},
        business_plan=None,
        snapshot=None,
        cat_matrices={'Consultant': consultant_cat},
        economic_parameters=None
    )
    
    print(f"   Office workforce structure:")
    print(f"   - Roles: {list(office_state.workforce.keys())}")
    print(f"   - Consultant levels: {list(office_state.workforce.get('Consultant', {}).keys())}")
    print(f"   - A level people: {len(office_state.workforce['Consultant']['A'])}")
    
    # Process progression as the engine would
    print("\n8. Simulating engine progression processing...")
    
    month_events = []
    if office_state.cat_matrices:
        for role, levels in office_state.workforce.items():
            role_cat_matrix = office_state.cat_matrices.get(role)
            print(f"   Processing role: {role}")
            print(f"   - Has CAT matrix? {role_cat_matrix is not None}")
            
            if role_cat_matrix:
                for level, people in levels.items():
                    print(f"   Processing level: {level}")
                    print(f"   - Number of people: {len(people)}")
                    
                    if people:
                        # Reset seed for consistency
                        random.seed(42)
                        progression_events = wm.process_progression(
                            people, role_cat_matrix, jan_2024
                        )
                        print(f"   - Events generated: {len(progression_events)}")
                        month_events.extend(progression_events)
    
    print(f"\n   Total events from engine simulation: {len(month_events)}")
    
    # Final assessment
    print("\n9. FINAL ASSESSMENT")
    print("-" * 30)
    
    if events or month_events:
        print("SUCCESS: Initial employee progression WORKS!")
        print(f"- Direct processing: {len(events)} events")
        print(f"- Engine simulation: {len(month_events)} events")
    else:
        print("FAILURE: Initial employee progression NOT working")
        print("Possible issues:")
        print("- CAT matrix structure mismatch")
        print("- Progression month configuration")
        print("- Random seed affecting probability")

if __name__ == "__main__":
    test_initial_employee_progression()