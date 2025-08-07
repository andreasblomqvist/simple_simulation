"""
Debug why progression events aren't being generated
"""

import sys
from pathlib import Path
from datetime import date

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def debug_progression_issues():
    """Debug progression issues in the simulation"""
    print("Debugging Progression Issues")
    print("=" * 40)
    
    from src.services.simulation_engine_v2 import (
        SimulationEngineV2Factory, Person, CATMatrix
    )
    from src.services.workforce_manager_v2 import WorkforceManagerV2
    
    # 1. Test workforce manager directly
    print("1. Testing workforce manager progression logic...")
    
    wm = WorkforceManagerV2()
    wm.initialize()
    
    # Check if level progression months loaded
    print("\nLevel progression months loaded:")
    for level, months in sorted(wm.level_progression_months.items())[:5]:
        print(f"   {level}: {months}")
    
    # 2. Create test person with good tenure
    print("\n2. Creating test person...")
    
    test_person = Person(
        id='TEST_001',
        current_role='Consultant',
        current_level='A',
        current_office='london',
        hire_date=date(2023, 1, 1),  # 1 year old
        current_level_start=date(2023, 1, 1),
        events=[],
        is_active=True
    )
    
    jan_2024 = date(2024, 1, 15)
    tenure = test_person.get_level_tenure_months(jan_2024)
    print(f"   Person: {test_person.current_role} {test_person.current_level}")
    print(f"   Tenure: {tenure} months")
    
    # 3. Create CAT matrix with high probability
    print("\n3. Creating CAT matrix with high progression probability...")
    
    cat_matrix = CATMatrix(
        progression_probabilities={
            'A': {'AC': 0.99, 'C': 0.01}  # 99% chance to progress
        }
    )
    print(f"   A->AC probability: 0.99")
    
    # 4. Test progression directly
    print("\n4. Testing process_progression directly...")
    
    # Set random seed for reproducibility
    import random
    random.seed(42)
    
    events = wm.process_progression([test_person], cat_matrix, jan_2024)
    
    if events:
        print(f"   SUCCESS: Generated {len(events)} progression events!")
        for event in events:
            print(f"      {event.event_type.value}: {event.details}")
    else:
        print("   FAILURE: No progression events generated")
        
        # Debug why
        print("\n   Debugging why no events...")
        
        # Check month
        is_progression_month = jan_2024.month in wm.level_progression_months.get('A', [])
        print(f"   Is January a progression month for A? {is_progression_month}")
        print(f"   A progression months: {wm.level_progression_months.get('A', [])}")
        
        # Check tenure
        meets_tenure = tenure >= wm.progression_config.minimum_tenure_months
        print(f"   Meets tenure requirement ({wm.progression_config.minimum_tenure_months} months)? {meets_tenure}")
        
        # Check probability calculation
        print("\n   Testing probability calculation...")
        from src.services.workforce_manager_v2 import WorkforceManagerV2
        
        # Test the _should_person_progress method
        wm2 = WorkforceManagerV2()
        wm2.initialize()
        
        # Test CAT category calculation
        cat_category = wm2._get_cat_category(tenure)
        print(f"   CAT category for {tenure} months tenure: {cat_category}")
        
        # Check if CAT matrix has this category
        prob = cat_matrix.get_probability('A', cat_category)
        print(f"   Probability from CAT matrix: {prob}")
        
        # The issue: CAT matrix uses level-to-level probabilities, not CAT categories!
        print("\n   ISSUE IDENTIFIED:")
        print("   CAT matrix structure mismatch!")
        print("   - CAT matrix has: A -> {AC: 0.99, C: 0.01}")
        print("   - But code expects: A -> {CAT0: x, CAT6: y, CAT12: z, ...}")
    
    # 5. Test with correct CAT matrix structure
    print("\n5. Testing with correct CAT matrix structure...")
    
    correct_cat_matrix = CATMatrix(
        progression_probabilities={
            'A': {
                'CAT0': 0.0,
                'CAT6': 0.9,
                'CAT12': 0.85,
                'CAT18': 0.8,
                'CAT24': 0.75,
                'CAT30+': 0.7
            }
        }
    )
    
    events2 = wm.process_progression([test_person], correct_cat_matrix, jan_2024)
    
    if events2:
        print(f"   SUCCESS: Generated {len(events2)} events with correct structure!")
    else:
        print("   Still no events - checking why...")
        
        # Manually test probability
        cat_cat = wm._get_cat_category(tenure)
        prob = correct_cat_matrix.get_probability('A', cat_cat)
        print(f"   CAT category: {cat_cat}, Probability: {prob}")
        
        # Test random generation
        random.seed(42)
        rand_val = random.random()
        print(f"   Random value: {rand_val:.3f}, Would progress: {rand_val < prob}")

if __name__ == "__main__":
    debug_progression_issues()