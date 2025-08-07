"""
Test Level-Specific Progression Months

Verifies that progression happens according to level-specific months:
- A/AC levels: months 1, 4, 7, 10
- C/SrC/AM levels: months 1, 7
- M+ levels: month 1 only
"""

import sys
from pathlib import Path
from datetime import date

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_level_specific_progression():
    """Test that progression months are level-specific"""
    print("Testing Level-Specific Progression Months")
    print("=" * 45)
    
    from src.services.workforce_manager_v2 import WorkforceManagerV2
    from src.services.simulation_engine_v2 import Person, CATMatrix
    
    # 1. Create workforce manager
    wm = WorkforceManagerV2()
    wm.initialize()
    
    # 2. Check loaded progression months
    print("\n1. Loaded Level Progression Months:")
    if wm.level_progression_months:
        for level, months in sorted(wm.level_progression_months.items()):
            print(f"   {level:4s}: {months}")
    else:
        print("   WARNING: No level progression months loaded!")
    
    # 3. Create test people at different levels
    print("\n2. Creating test people at different levels...")
    
    people = [
        Person(
            id='person_A',
            current_role='Consultant',
            current_level='A',
            current_office='london',
            hire_date=date(2023, 1, 1),
            current_level_start=date(2023, 1, 1),
            events=[],
            is_active=True
        ),
        Person(
            id='person_C',
            current_role='Consultant', 
            current_level='C',
            current_office='london',
            hire_date=date(2022, 1, 1),
            current_level_start=date(2023, 1, 1),
            events=[],
            is_active=True
        ),
        Person(
            id='person_M',
            current_role='Consultant',
            current_level='M',
            current_office='london',
            hire_date=date(2020, 1, 1),
            current_level_start=date(2022, 1, 1),
            events=[],
            is_active=True
        )
    ]
    
    # Create simple CAT matrix
    cat_matrix = CATMatrix(
        progression_probabilities={
            'A': {'AC': 0.9, 'C': 0.1},
            'C': {'SrC': 0.8},
            'M': {'SrM': 0.5}
        }
    )
    
    # 4. Test progression in different months
    print("\n3. Testing Progression in Different Months:")
    
    test_months = [
        (1, "January"),
        (4, "April"),
        (6, "June"),
        (7, "July"),
        (10, "October"),
        (12, "December")
    ]
    
    for month, month_name in test_months:
        print(f"\n   Month {month} ({month_name}):")
        current_date = date(2024, month, 15)
        
        # Check which levels can progress this month
        can_progress = []
        for level in ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM']:
            level_months = wm.level_progression_months.get(level, [])
            if month in level_months:
                can_progress.append(level)
        
        if can_progress:
            print(f"      Levels that can progress: {', '.join(can_progress)}")
        else:
            print(f"      No levels can progress this month")
        
        # Test actual progression
        events = wm.process_progression(people, cat_matrix, current_date)
        if events:
            print(f"      Generated {len(events)} progression events:")
            for event in events:
                from_level = event.details.get('from_level', '?')
                to_level = event.details.get('to_level', '?')
                print(f"         - {from_level} -> {to_level}")
        else:
            print(f"      No progression events generated")
    
    # 5. Verify correct behavior
    print("\n4. Verification Summary:")
    print("   Expected behavior:")
    print("      - A level: Can progress in months 1, 4, 7, 10")
    print("      - C level: Can progress in months 1, 7")
    print("      - M level: Can progress in month 1 only")
    
    # Test specific cases
    print("\n5. Specific Test Cases:")
    
    # Test A level in April (month 4)
    april_date = date(2024, 4, 15)
    a_person = [p for p in people if p.current_level == 'A'][0]
    events = wm.process_progression([a_person], cat_matrix, april_date)
    print(f"   A level in April: {'PASS' if events else 'FAIL'} (Should progress)")
    
    # Test C level in April (month 4)  
    c_person = [p for p in people if p.current_level == 'C'][0]
    events = wm.process_progression([c_person], cat_matrix, april_date)
    print(f"   C level in April: {'PASS' if not events else 'FAIL'} (Should NOT progress)")
    
    # Test M level in July (month 7)
    july_date = date(2024, 7, 15)
    m_person = [p for p in people if p.current_level == 'M'][0]
    events = wm.process_progression([m_person], cat_matrix, july_date)
    print(f"   M level in July: {'PASS' if not events else 'FAIL'} (Should NOT progress)")
    
    print("\n" + "=" * 45)
    print("Level-Specific Progression Test Complete")

if __name__ == "__main__":
    test_level_specific_progression()