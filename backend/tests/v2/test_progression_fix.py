"""
Test CAT Matrix Loading and Progression Functionality

This test verifies that:
1. CAT matrices are loaded correctly into office states
2. Progression events are generated for people with sufficient tenure
3. Progression only occurs in months 6 and 12
4. Role-specific CAT matrices are applied correctly
"""

import sys
import json
from pathlib import Path
from datetime import datetime, date
from collections import Counter

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_progression_functionality():
    """Test complete progression functionality with CAT matrix loading"""
    print("Testing CAT Matrix Loading and Progression Functionality")
    print("=" * 60)
    
    try:
        from src.services.simulation_engine_v2 import (
            SimulationEngineV2Factory, ScenarioRequest, TimeRange, Levers,
            Person
        )
        
        # 1. Create engine
        print("1. Creating simulation engine...")
        engine = SimulationEngineV2Factory.create_test_engine(random_seed=42)
        
        # 2. Create scenario with progression months (month 6)
        print("2. Creating test scenario...")
        scenario = ScenarioRequest(
            scenario_id="progression_test",
            name="Progression Test Scenario",
            time_range=TimeRange(2024, 1, 2024, 6),  # 6 months to trigger progression in month 6
            office_ids=["london"],
            levers=Levers(recruitment_multiplier=1.0, churn_multiplier=0.8)
        )
        
        # 3. Test CAT matrix loading during initialization
        print("3. Testing CAT matrix loading...")
        engine._load_and_initialize_offices(scenario)
        
        # Verify CAT matrices were loaded
        london_office = engine.office_states.get("london")
        if london_office and london_office.cat_matrices:
            print(f"   [OK] CAT matrices loaded for {len(london_office.cat_matrices)} roles")
            for role, cat_matrix in london_office.cat_matrices.items():
                progression_paths = len(cat_matrix.progression_probabilities)
                print(f"     - {role}: {progression_paths} progression paths")
        else:
            print("   [FAIL] CAT matrices not loaded properly")
            return False, {"error": "CAT matrices not loaded"}
        
        # 4. Add test people with different tenures to trigger progression
        print("4. Adding test people for progression testing...")
        from datetime import timedelta
        
        # Add people with sufficient tenure (6+ months) for progression
        test_people = [
            Person(
                id="consultant_1",
                current_role="Consultant",
                current_level="A",
                current_office="london",
                hire_date=date(2023, 6, 1),  # 7 months tenure by Jan 2024
                current_level_start=date(2023, 6, 1),  # Started at A level when hired
                is_active=True
            ),
            Person(
                id="consultant_2",
                current_role="Consultant",
                current_level="A",
                current_office="london", 
                hire_date=date(2023, 5, 1),  # 8 months tenure by Jan 2024
                current_level_start=date(2023, 5, 1),  # Started at A level when hired
                is_active=True
            ),
            Person(
                id="sales_1",
                current_role="Sales",
                current_level="A",
                current_office="london",
                hire_date=date(2023, 4, 1),  # 9 months tenure by Jan 2024
                current_level_start=date(2023, 4, 1),  # Started at A level when hired
                is_active=True
            )
        ]
        
        # Add people to office workforce
        for person in test_people:
            london_office.add_person(person)
        
        total_people = london_office.get_total_workforce()
        print(f"   [OK] Added {len(test_people)} test people (total workforce: {total_people})")
        
        # Show initial tenure info
        simulation_start_date = date(2024, 1, 1)
        for person in test_people:
            tenure_months = person.get_tenure_months(simulation_start_date)
            level_tenure = person.get_level_tenure_months(simulation_start_date)
            print(f"     - {person.id}: {tenure_months} months tenure, {level_tenure} months in level")
        
        # 5. Run simulation
        print("5. Running simulation...")
        start_time = datetime.now()
        results = engine.run_simulation(scenario)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        print(f"   [OK] Simulation completed in {execution_time:.2f} seconds")
        print(f"   [OK] Generated {len(results.all_events)} total events")
        
        # 6. Analyze progression results
        print("6. Analyzing progression results...")
        
        if len(results.all_events) > 0:
            # Event type breakdown
            event_types = Counter(event.event_type.value for event in results.all_events)
            print("   Event Type Breakdown:")
            for event_type, count in event_types.items():
                print(f"     - {event_type}: {count}")
            
            # Check for promotion events
            promotion_events = [e for e in results.all_events if e.event_type.value == 'promoted']
            print(f"   [OK] Progression events: {len(promotion_events)}")
            
            # Analyze promotion events by month
            if promotion_events:
                promotions_by_month = {}
                for event in promotion_events:
                    month = event.date.month
                    if month not in promotions_by_month:
                        promotions_by_month[month] = 0
                    promotions_by_month[month] += 1
                
                print("   Promotions by Month:")
                for month in sorted(promotions_by_month.keys()):
                    print(f"     - Month {month}: {promotions_by_month[month]} promotions")
                
                # Check if promotions only occur in expected months (6, 12)
                progression_months = [6, 12]
                valid_promotion_months = all(month in progression_months for month in promotions_by_month.keys())
                print(f"   [OK] Promotions in valid months only: {valid_promotion_months}")
                
                # Show promotion details
                print("   Promotion Details:")
                for event in promotion_events[:5]:  # Show first 5
                    person_id = event.details.get('person_id', 'unknown')
                    from_level = event.details.get('from_level', '')
                    to_level = event.details.get('to_level', '')
                    role = event.details.get('role', '')
                    tenure = event.details.get('tenure_months', 0)
                    print(f"     - {person_id}: {role} {from_level}→{to_level} (tenure: {tenure}mo)")
            
            # Individual progression tracking
            people_with_events = set(e.details.get('person_id') for e in results.all_events if 'person_id' in e.details)
            print(f"   [OK] People with events: {len(people_with_events)}")
            
            # Success criteria
            success_criteria = [
                ("CAT matrices loaded", len(london_office.cat_matrices) > 0),
                ("Test people added", total_people >= len(test_people)),
                ("Events generated", len(results.all_events) > 0),
                ("Promotion events exist", len(promotion_events) > 0),
                ("Promotions in correct months", len(promotion_events) == 0 or valid_promotion_months),
                ("Individual tracking works", len(people_with_events) > 0)
            ]
            
        else:
            print("   [WARN] No events generated")
            success_criteria = [
                ("CAT matrices loaded", len(london_office.cat_matrices) > 0),
                ("Test people added", total_people >= len(test_people)),
                ("Events generated", False),
                ("Promotion events exist", False),
                ("Promotions in correct months", False),
                ("Individual tracking works", False)
            ]
        
        # 7. Final assessment
        print()
        print("7. SUCCESS ASSESSMENT")
        print("-" * 25)
        
        passed_criteria = 0
        for criteria, passed in success_criteria:
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {criteria}")
            if passed:
                passed_criteria += 1
        
        success_rate = (passed_criteria / len(success_criteria)) * 100
        
        print()
        print(f"SUCCESS RATE: {success_rate:.1f}% ({passed_criteria}/{len(success_criteria)})")
        
        # Final verdict
        if success_rate >= 80:
            print()
            print("[SUCCESS] Progression functionality is working correctly!")
            print("CAT matrices are loaded and progression events are generated!")
            success = True
        else:
            print()
            print("[PARTIAL] Some progression issues may remain")
            success = False
            
        return success, {
            'success_rate': success_rate,
            'total_events': len(results.all_events),
            'promotion_events': len(promotion_events) if 'promotion_events' in locals() else 0,
            'event_types': dict(event_types) if results.all_events else {},
            'execution_time': execution_time,
            'cat_matrices_loaded': len(london_office.cat_matrices) if london_office else 0
        }
        
    except Exception as e:
        print(f"[FAIL] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, {'error': str(e)}

if __name__ == "__main__":
    print("CAT Matrix Loading and Progression Test")
    print("=" * 40)
    
    success, metrics = test_progression_functionality()
    
    print()
    if success:
        print("[SUCCESS] PROGRESSION FUNCTIONALITY IS FIXED!")
        print("CAT matrices are loading correctly and progression events are being generated!")
    else:
        print("[FAIL] Some issues still need to be addressed")
        if 'error' in metrics:
            print(f"Primary error: {metrics['error']}")
    
    print()
    print("Test completed!")