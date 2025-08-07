"""
Debug July Progression in Comprehensive Test Population

Test progression specifically in July 2024 with the comprehensive test population
to identify why 0 progression events are generated.
"""

import sys
import json
from pathlib import Path
from datetime import date

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_july_progression():
    """Debug progression in July 2024 with real population"""
    print("DEBUGGING JULY 2024 PROGRESSION")
    print("=" * 40)
    
    try:
        from src.services.simulation_engine_v2 import (
            SimulationEngineV2Factory, Person, CATMatrix, OfficeState
        )
        
        # 1. Load the exact same data as comprehensive test
        print("1. Loading comprehensive test data...")
        
        test_data_dir = Path(__file__).parent / "test_data"
        
        with open(test_data_dir / "cat_matrices_correct.json") as f:
            cat_data = json.load(f)
        
        with open(test_data_dir / "population_snapshots.json") as f:
            population_data = json.load(f)
        
        # 2. Create CAT matrices
        print("2. Setting up CAT matrices...")
        cat_matrices = {}
        for role, matrix_data in cat_data.items():
            cat_matrices[role] = CATMatrix(
                progression_probabilities=matrix_data["progression_probabilities"]
            )
        
        consultant_cat = cat_matrices["Consultant"]
        print(f"   Consultant CAT matrix levels: {list(consultant_cat.progression_probabilities.keys())}")
        
        # 3. Create people from population snapshot
        print("3. Creating population from snapshot...")
        
        people_by_level = {"A": [], "AC": [], "C": [], "SrC": []}
        
        for person_data in population_data["london"]["workforce"]:
            if person_data["role"] == "Consultant":
                person = Person(
                    id=person_data["id"],
                    current_role=person_data["role"],
                    current_level=person_data["level"],
                    current_office=person_data["office"],
                    hire_date=date.fromisoformat(person_data["hire_date"] + "-01"),
                    current_level_start=date.fromisoformat(person_data["level_start_date"] + "-01"),
                    events=[],
                    is_active=True
                )
                
                if person.current_level in people_by_level:
                    people_by_level[person.current_level].append(person)
        
        july_date = date(2024, 7, 15)
        
        for level, people in people_by_level.items():
            print(f"   {level} level: {len(people)} people")
            if people:
                # Show first person's details
                first_person = people[0]
                tenure = first_person.get_level_tenure_months(july_date)
                print(f"      Example: {first_person.id}, tenure: {tenure} months")
        
        # 4. Create engine and test progression
        print("4. Testing progression with engine...")
        
        engine = SimulationEngineV2Factory.create_test_engine(random_seed=42)
        
        print(f"   WM progression months: {engine.workforce_manager.level_progression_months}")
        print(f"   A level progression months: {engine.workforce_manager.level_progression_months.get('A', 'MISSING')}")
        print(f"   Is July (month 7) a progression month for A? {7 in engine.workforce_manager.level_progression_months.get('A', [])}")
        
        # Test progression for A-level people specifically
        print("\\n5. Testing A-level progression...")
        
        a_people = people_by_level["A"]
        print(f"   Testing {len(a_people)} A-level people")
        
        if a_people:
            # Set seed for reproducibility
            import random
            random.seed(42)
            
            progression_events = engine.workforce_manager.process_progression(
                a_people, consultant_cat, july_date
            )
            
            print(f"   Progression events generated: {len(progression_events)}")
            
            if progression_events:
                for event in progression_events:
                    print(f"      Event: {event.event_type.value} {event.details.get('from_level')} -> {event.details.get('to_level')}")
            else:
                print("   No events generated - debugging...")
                
                # Test individual progression decisions
                sample_person = a_people[0]
                print(f"\\n   Debugging sample person: {sample_person.id}")
                print(f"      Level: {sample_person.current_level}")
                print(f"      Hire date: {sample_person.hire_date}")
                print(f"      Level start: {sample_person.current_level_start}")
                print(f"      July tenure: {sample_person.get_level_tenure_months(july_date)} months")
                
                # Check progression requirements
                level_progression_months = engine.workforce_manager.level_progression_months.get('A', [])
                is_progression_month = july_date.month in level_progression_months
                print(f"      Is progression month: {is_progression_month}")
                
                tenure_months = sample_person.get_level_tenure_months(july_date)
                min_tenure = engine.workforce_manager.progression_config.minimum_tenure_months
                meets_tenure = tenure_months >= min_tenure
                print(f"      Meets tenure requirement: {meets_tenure} ({tenure_months} >= {min_tenure})")
                
                # Check CAT probability
                alice_prob = engine.workforce_manager.calculate_cat_probability(sample_person, consultant_cat, july_date)
                cat_category = engine.workforce_manager._get_cat_category(tenure_months)
                print(f"      CAT category: {cat_category}")
                print(f"      Progression probability: {alice_prob}")
                
                # Test should_progress decision
                random.seed(42)
                should_progress = engine.workforce_manager._should_person_progress(sample_person, 'A', consultant_cat, july_date)
                print(f"      Should progress decision: {should_progress}")
                
                # Check random value
                random.seed(42)
                rand_val = random.random()
                print(f"      Random value: {rand_val:.3f}")
                print(f"      Would progress: {rand_val < alice_prob}")
        
        # 6. Test all levels
        print("\\n6. Testing all eligible levels...")
        
        total_events = 0
        for level, people in people_by_level.items():
            if not people:
                continue
                
            level_progression_months = engine.workforce_manager.level_progression_months.get(level, [])
            if 7 not in level_progression_months:  # July
                print(f"   {level} level: NOT eligible in July")
                continue
            
            print(f"   {level} level: {len(people)} people eligible")
            
            import random
            random.seed(42)
            
            events = engine.workforce_manager.process_progression(
                people, consultant_cat, july_date
            )
            
            print(f"      Generated: {len(events)} events")
            total_events += len(events)
        
        print(f"\\n   Total progression events: {total_events}")
        
        if total_events > 0:
            print("\\nSUCCESS: Progression working with population data!")
        else:
            print("\\nFAILURE: Still no progression events with population data")
        
        return total_events > 0
        
    except Exception as e:
        print(f"\\nERROR: Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_july_progression()
    if success:
        print("\\nProgression debugging complete - progression working!")
    else:
        print("\\nProgression debugging complete - issue still present!")