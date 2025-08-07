"""
Debug Process Progression Method

Step through the process_progression method line by line to find where it fails.
"""

import sys
from pathlib import Path
from datetime import date

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def debug_process_progression_method():
    """Debug the process_progression method step by step"""
    print("DEBUG PROCESS PROGRESSION METHOD")
    print("=" * 35)
    
    try:
        from src.services.workforce_manager_v2 import WorkforceManagerV2
        from src.services.simulation_engine_v2 import Person, CATMatrix
        
        # Create test setup
        workforce_manager = WorkforceManagerV2()
        workforce_manager.initialize(random_seed=42)
        
        test_person = Person(
            id="debug_person",
            current_role="Consultant",
            current_level="A",
            current_office="london",
            hire_date=date(2022, 6, 1),
            current_level_start=date(2022, 6, 1),
            is_active=True
        )
        
        cat_matrix = CATMatrix(
            progression_probabilities={
                "A": {"AC": 0.15, "C": 0.02}
            }
        )
        
        current_date = date(2024, 6, 15)
        people = [test_person]
        
        print("1. Input setup:")
        print(f"   People: {len(people)}")
        print(f"   Person: {test_person.id}, {test_person.current_role} {test_person.current_level}")
        print(f"   Current date: {current_date} (month {current_date.month})")
        print(f"   CAT matrix progressions: {cat_matrix.progression_probabilities}")
        
        print()
        print("2. Step-by-step process_progression execution:")
        
        # Step 1: Check month
        print(f"   Step 1 - Month check:")
        is_progression_month = current_date.month in workforce_manager.progression_config.progression_months
        print(f"     Is progression month: {is_progression_month}")
        print(f"     Progression months config: {workforce_manager.progression_config.progression_months}")
        
        if not is_progression_month:
            print("     STOPPING: Not a progression month")
            return
        
        # Step 2: Group people
        print(f"   Step 2 - Grouping people:")
        role_level_groups = workforce_manager._group_people_by_role_level(people)
        print(f"     Groups: {list(role_level_groups.keys())}")
        print(f"     Group details: {role_level_groups}")
        
        # Step 3: Process each group
        total_events = []
        for (role, level), level_people in role_level_groups.items():
            print(f"   Step 3 - Processing group ({role}, {level}):")
            print(f"     People in group: {len(level_people)}")
            
            # Check eligibility
            eligible_people = [
                p for p in level_people 
                if (p.is_active and 
                    p.get_level_tenure_months(current_date) >= workforce_manager.progression_config.minimum_tenure_months)
            ]
            print(f"     Eligible people: {len(eligible_people)}")
            
            for person in eligible_people:
                tenure = person.get_level_tenure_months(current_date)
                print(f"       {person.id}: active={person.is_active}, tenure={tenure}mo")
            
            if not eligible_people:
                print("     SKIPPING: No eligible people")
                continue
            
            # Process individuals
            for person in eligible_people:
                print(f"   Step 4 - Processing person {person.id}:")
                
                should_progress = workforce_manager._should_person_progress(person, level, cat_matrix, current_date)
                print(f"     Should progress: {should_progress}")
                
                if should_progress:
                    print(f"     Person should progress! Getting next level...")
                    
                    # Get next level
                    next_level = workforce_manager._get_next_level_from_matrix(person.current_level, cat_matrix)
                    print(f"     Next level: {next_level}")
                    
                    if next_level:
                        print(f"     Creating promotion event...")
                        
                        # Create event
                        try:
                            event = workforce_manager._create_promotion_event(person, level, next_level, current_date, cat_matrix)
                            print(f"     Event created: {event.event_type}")
                            print(f"     Event details: {event.details}")
                            
                            # Add event to person
                            print(f"     Adding event to person...")
                            person.add_event(event)
                            print(f"     Person now has {len(person.events)} events")
                            
                            # Add to results
                            total_events.append(event)
                            print(f"     Added to results. Total events: {len(total_events)}")
                            
                        except Exception as e:
                            print(f"     ERROR creating event: {str(e)}")
                            import traceback
                            traceback.print_exc()
                    else:
                        print(f"     NO NEXT LEVEL - cannot create event")
                else:
                    print(f"     No progression (random result)")
        
        print()
        print(f"3. Manual step-by-step result: {len(total_events)} events")
        
        # Now call actual method
        print()
        print("4. Calling actual process_progression method...")
        actual_events = workforce_manager.process_progression(people, cat_matrix, current_date)
        print(f"   Actual method result: {len(actual_events)} events")
        
        if len(actual_events) != len(total_events):
            print(f"   MISMATCH: Manual={len(total_events)}, Actual={len(actual_events)}")
        else:
            print(f"   MATCH: Both methods returned {len(actual_events)} events")
        
        # Show event details
        if actual_events:
            for event in actual_events:
                print(f"     Event: {event.details}")
        
        return len(actual_events) > 0
        
    except Exception as e:
        print(f"[ERROR] Debug failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_process_progression_method()
    
    if success:
        print("\n[SUCCESS] process_progression is working!")
    else:
        print("\n[ISSUE] process_progression has problems")