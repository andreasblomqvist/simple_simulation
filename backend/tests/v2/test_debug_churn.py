"""
Debug Churn Processing in V2 Engine

Investigate why churn events are not being generated despite business plan targets.
"""

import sys
import json
from pathlib import Path
from datetime import date

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_churn_processing():
    """Debug churn processing step by step"""
    print("DEBUGGING CHURN PROCESSING")
    print("=" * 35)
    
    try:
        from src.services.simulation_engine_v2 import (
            SimulationEngineV2Factory, Person, MonthlyTargets
        )
        
        # 1. Create test people
        print("1. Creating test people...")
        
        test_people = []
        for i in range(5):
            person = Person(
                id=f"TEST_PERSON_{i:02d}",
                current_role="Consultant",
                current_level="A",
                current_office="london",
                hire_date=date(2023, 1, 1),
                current_level_start=date(2023, 1, 1),
                events=[],
                is_active=True
            )
            test_people.append(person)
        
        print(f"   Created {len(test_people)} A-level Consultant people")
        
        # 2. Create workforce manager and test churn directly
        print("\\n2. Testing direct churn processing...")
        
        engine = SimulationEngineV2Factory.create_test_engine(random_seed=42)
        
        # Test direct churn processing
        churn_targets = {"A": 2}  # Should churn 2 A-level people
        test_date = date(2024, 7, 15)
        
        churn_events = engine.workforce_manager.process_churn(
            test_people, churn_targets, test_date
        )
        
        print(f"   Direct churn processing result: {len(churn_events)} events")
        
        if churn_events:
            for event in churn_events:
                print(f"      Event: {event.event_type.value} - {event.details.get('level')} level")
        else:
            print("      No churn events generated")
        
        # Check people status after churn
        churned_people = [p for p in test_people if not p.is_active]
        print(f"   People churned: {len(churned_people)}")
        
        # 3. Test with business plan data
        print("\\n3. Testing with business plan churn targets...")
        
        # Load actual business plan
        test_data_dir = Path(__file__).parent / "test_data"
        with open(test_data_dir / "business_plans.json") as f:
            business_plans_data = json.load(f)
        
        # Check July 2024 churn targets
        july_plan = business_plans_data["london"]["monthly_plans"]["2024-07"]
        july_churn_targets = july_plan["churn"]
        
        print(f"   July 2024 churn targets from business plan:")
        for role, levels in july_churn_targets.items():
            for level, count in levels.items():
                if count > 0:
                    print(f"      {role} {level}: {count}")
        
        # 4. Test engine's monthly processing logic
        print("\\n4. Testing engine monthly processing...")
        
        # Create monthly targets object
        monthly_targets = MonthlyTargets(
            year=2024,
            month=7,
            recruitment_targets=july_plan["recruitment"],
            churn_targets=july_plan["churn"],
            revenue_target=july_plan["revenue"],
            operating_costs=july_plan["costs"],
            salary_budget=300000.0
        )
        
        print(f"   Created monthly targets for July 2024")
        print(f"   Churn targets: {monthly_targets.churn_targets}")
        
        # 5. Check if business processor is working
        print("\\n5. Testing business processor...")
        
        if hasattr(engine.business_processor, 'get_monthly_targets'):
            # This would normally get targets from the business plan
            print("   Business processor available")
        else:
            print("   Business processor missing get_monthly_targets method")
        
        # 6. Test manual office month processing
        print("\\n6. Testing manual office month processing...")
        
        # Create test workforce
        workforce = {
            "Consultant": {
                "A": test_people[:3],  # 3 A-level consultants available for churn
                "AC": []
            }
        }
        
        print(f"   Test workforce: {len(workforce['Consultant']['A'])} A-level Consultants")
        
        # Simulate what happens in _process_office_month for churn
        month_events = []
        
        if engine.workforce_manager:
            for role, levels in workforce.items():
                for level, people in levels.items():
                    if people:
                        churn_target = monthly_targets.churn_targets.get(role, {}).get(level, 0)
                        print(f"   Processing {role} {level}: {len(people)} people, target: {churn_target}")
                        
                        if churn_target > 0:
                            churn_events = engine.workforce_manager.process_churn(
                                people, {level: churn_target}, test_date
                            )
                            month_events.extend(churn_events)
                            print(f"      Generated: {len(churn_events)} churn events")
        
        print(f"\\n   Total month events: {len(month_events)}")
        
        # 7. Final assessment
        print("\\n7. CHURN PROCESSING ASSESSMENT")
        print("-" * 35)
        
        if len(month_events) > 0:
            print("SUCCESS: Churn processing is working!")
            print(f"   Generated {len(month_events)} churn events")
            print("   Issue may be in comprehensive test setup")
        else:
            print("FAILURE: Churn processing is broken")
            print("   No churn events generated despite targets and available people")
        
        return len(month_events) > 0
        
    except Exception as e:
        print(f"\\nERROR: Churn debug failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_churn_processing()
    if success:
        print("\\nChurn processing is functional!")
    else:
        print("\\nChurn processing needs debugging!")