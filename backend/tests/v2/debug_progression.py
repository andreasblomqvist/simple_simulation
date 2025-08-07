"""
Debug Progression Logic

This test specifically investigates why progression events aren't being generated
despite CAT matrices being loaded correctly.
"""

import sys
from pathlib import Path
from datetime import datetime, date

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def debug_progression_month_logic():
    """Test progression month logic step by step"""
    print("DEBUG: Progression Month Logic")
    print("=" * 35)
    
    try:
        from src.services.workforce_manager_v2 import WorkforceManagerV2, ProgressionConfiguration
        from src.services.simulation_engine_v2 import Person, CATMatrix
        
        # 1. Check progression configuration
        print("1. Checking progression configuration...")
        progression_config = ProgressionConfiguration([6, 12])
        print(f"   Progression months: {progression_config.progression_months}")
        print(f"   Minimum tenure months: {progression_config.minimum_tenure_months}")
        print(f"   Use CAT probabilities: {progression_config.use_cat_probabilities}")
        
        # 2. Test with June (month 6)
        print()
        print("2. Testing progression eligibility in June...")
        
        current_date = date(2024, 6, 15)  # June 15, 2024
        print(f"   Current date: {current_date} (month {current_date.month})")
        print(f"   Is progression month: {current_date.month in progression_config.progression_months}")
        
        # 3. Create test person with sufficient tenure
        test_person = Person(
            id="debug_person",
            current_role="Consultant", 
            current_level="A",
            current_office="london",
            hire_date=date(2023, 6, 1),  # Hired 12 months ago
            current_level_start=date(2023, 6, 1),
            is_active=True
        )
        
        tenure_months = test_person.get_tenure_months(current_date)
        level_tenure_months = test_person.get_level_tenure_months(current_date)
        print(f"   Test person tenure: {tenure_months} months")
        print(f"   Level tenure: {level_tenure_months} months")
        print(f"   Meets minimum tenure: {level_tenure_months >= progression_config.minimum_tenure_months}")
        
        # 4. Create CAT matrix
        cat_matrix = CATMatrix(
            progression_probabilities={
                "A": {"CAT12": 0.15, "CAT18": 0.02}  # From A to AC/C levels
            }
        )
        
        print()
        print("3. Testing CAT matrix progression logic...")
        print(f"   CAT matrix progression paths: {cat_matrix.progression_probabilities}")
        
        # 5. Test workforce manager progression
        print()
        print("4. Testing workforce manager progression process...")
        
        workforce_manager = WorkforceManagerV2()
        workforce_manager.initialize(random_seed=42)
        
        # Test progression for single person
        people = [test_person]
        
        print("   Running full process_progression method...")
        print("   Step-by-step trace:")
        
        # Manually trace through process_progression
        print(f"     Input: {len(people)} people")
        
        # Check if current month is a progression month
        is_progression_month = current_date.month in workforce_manager.progression_config.progression_months
        print(f"     Is progression month: {is_progression_month}")
        
        if not is_progression_month:
            print("     STOPPING: Not a progression month")
            return
        
        # Group people by role and level
        role_level_groups = workforce_manager._group_people_by_role_level(people)
        print(f"     Role/level groups: {list(role_level_groups.keys())}")
        
        total_events = []
        for (role, level), level_people in role_level_groups.items():
            print(f"     Processing group: {role} {level} ({len(level_people)} people)")
            
            # Get eligible people
            eligible_people = [
                p for p in level_people 
                if (p.is_active and 
                    p.get_level_tenure_months(current_date) >= workforce_manager.progression_config.minimum_tenure_months)
            ]
            print(f"       Eligible people: {len(eligible_people)}")
            
            if not eligible_people:
                print("       SKIPPING: No eligible people")
                continue
            
            # Process individual progression
            for i, person in enumerate(eligible_people):
                print(f"       Processing person {i+1}: {person.id}")
                
                should_progress = workforce_manager._should_person_progress(person, level, cat_matrix, current_date)
                print(f"         Should progress: {should_progress}")
                
                if should_progress:
                    next_level = workforce_manager._get_next_level(role, level)
                    print(f"         Next level: {next_level}")
                    
                    if next_level:
                        print(f"         Creating promotion event: {level} -> {next_level}")
                        event = workforce_manager._create_promotion_event(person, level, next_level, current_date, cat_matrix)
                        print(f"         Event created: {event.event_type}")
                        
                        # Manually add to person (like the real method does)
                        person.add_event(event)
                        total_events.append(event)
                        print(f"         Event added to person and list")
                    else:
                        print("         NO NEXT LEVEL FOUND!")
                else:
                    print("         No progression (random result)")
        
        print(f"   Manual trace generated: {len(total_events)} events")
        
        # Now run actual method
        progression_events = workforce_manager.process_progression(people, cat_matrix, current_date)
        print(f"   Actual method generated: {len(progression_events)} events")
        
        if progression_events:
            for event in progression_events:
                print(f"     - {event.details.get('person_id')}: {event.details.get('from_level')} -> {event.details.get('to_level')}")
        else:
            print("   Still no events from actual method. Checking for differences...")
            
    except Exception as e:
        print(f"[ERROR] Debug failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_progression_month_logic()