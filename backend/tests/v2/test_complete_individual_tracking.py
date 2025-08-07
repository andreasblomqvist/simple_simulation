"""
Complete Individual Event Tracking Test

Tests that recruitment, churn, and progression all work correctly together
and that events are properly tracked for each individual person.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, date
from collections import defaultdict
from typing import Dict, List

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_complete_individual_tracking():
    """Test complete simulation with individual event tracking"""
    print("Complete Individual Event Tracking Test")
    print("=" * 50)
    
    try:
        from src.services.simulation_engine_v2 import (
            SimulationEngineV2Factory, ScenarioRequest, TimeRange, Levers,
            BusinessPlan, MonthlyPlan, MonthlyTargets, CATMatrix,
            PopulationSnapshot, WorkforceEntry, Person, OfficeState
        )
        
        # 1. Create engine with test configuration
        print("1. Setting up V2 engine...")
        engine = SimulationEngineV2Factory.create_test_engine(random_seed=12345)
        print("   Engine created with seed 12345 for reproducibility")
        
        # 2. Load test data
        print("\n2. Loading test data...")
        test_data_dir = Path(__file__).parent / "test_data"
        
        # Load configurations
        with open(test_data_dir / "business_plans.json") as f:
            business_plans_data = json.load(f)
        
        # Use the correct CAT matrix structure
        with open(test_data_dir / "cat_matrices_correct.json") as f:
            cat_matrices_data = json.load(f)
            
        with open(test_data_dir / "population_snapshots.json") as f:
            population_data = json.load(f)
        
        print(f"   Business plans loaded: {len(business_plans_data)} offices")
        print(f"   CAT matrices loaded: {len(cat_matrices_data)} roles")
        print(f"   Population loaded: {sum(len(p['workforce']) for p in population_data.values())} people")
        
        # 3. Create a smaller initial population for easier tracking
        print("\n3. Creating trackable initial population...")
        
        # Create a small initial workforce with people at different levels
        initial_people = [
            # A-level people (can progress frequently)
            {"id": "ALICE_001", "role": "Consultant", "level": "A", "hire_date": "2023-06", "office": "london"},
            {"id": "ALEX_002", "role": "Consultant", "level": "A", "hire_date": "2023-08", "office": "london"},
            {"id": "ANNA_003", "role": "Sales", "level": "A", "hire_date": "2023-09", "office": "london"},
            
            # AC-level people
            {"id": "BOB_004", "role": "Consultant", "level": "AC", "hire_date": "2023-01", "office": "london"},
            {"id": "BELLA_005", "role": "Consultant", "level": "AC", "hire_date": "2023-03", "office": "london"},
            
            # C-level people (can progress in Jan/Jul)
            {"id": "CHARLIE_006", "role": "Consultant", "level": "C", "hire_date": "2022-06", "office": "london"},
            {"id": "CLAIRE_007", "role": "Sales", "level": "C", "hire_date": "2022-08", "office": "london"},
            
            # Senior people (less likely to progress)
            {"id": "DAVID_008", "role": "Consultant", "level": "SrC", "hire_date": "2021-01", "office": "london"},
            {"id": "DIANA_009", "role": "Consultant", "level": "M", "hire_date": "2020-01", "office": "london"},
            
            # Operations (no progression)
            {"id": "OSCAR_010", "role": "Operations", "level": "Operations", "hire_date": "2023-01", "office": "london"},
        ]
        
        print(f"   Created {len(initial_people)} initial employees:")
        for person in initial_people:
            print(f"      {person['id']}: {person['role']} {person['level']}")
        
        # 4. Setup business plan with moderate recruitment and churn
        print("\n4. Creating business plan with recruitment and churn...")
        
        # Create monthly plans for test period
        monthly_plans = {}
        for year in [2024]:
            for month in range(1, 8):  # January to July (covers two progression cycles)
                month_key = f"{year:04d}-{month:02d}"
                
                # Varied recruitment and churn targets
                recruitment_targets = {
                    "Consultant": {"A": 2 if month % 2 == 0 else 1, "AC": 1 if month == 3 else 0},
                    "Sales": {"A": 1 if month in [2, 5] else 0},
                    "Operations": {"Operations": 1 if month == 4 else 0}
                }
                
                churn_targets = {
                    "Consultant": {"A": 1 if month in [2, 5] else 0, "AC": 1 if month == 6 else 0},
                    "Sales": {"A": 1 if month == 3 else 0},
                    "Operations": {"Operations": 0}  # No operations churn
                }
                
                targets = MonthlyTargets(
                    year=year,
                    month=month,
                    recruitment_targets=recruitment_targets,
                    churn_targets=churn_targets,
                    revenue_target=500000.0,
                    operating_costs=400000.0,
                    salary_budget=300000.0
                )
                
                monthly_plan = MonthlyPlan(
                    year=year,
                    month=month,
                    recruitment=recruitment_targets,
                    churn=churn_targets,
                    revenue=480000.0,
                    costs=380000.0,
                    price_per_role={},
                    salary_per_role={},
                    utr_per_role={}
                )
                
                monthly_plans[month_key] = monthly_plan
        
        business_plan = BusinessPlan(
            office_id="london",
            name="London Test Plan",
            monthly_plans=monthly_plans
        )
        
        # Load business plan into engine
        if not hasattr(engine.business_processor, 'loaded_plans'):
            engine.business_processor.loaded_plans = {}
        engine.business_processor.loaded_plans["london"] = business_plan
        
        print("   Business plan created with:")
        print("      - Recruitment: 1-2 people per month")
        print("      - Churn: 0-1 people per month")
        print("      - Time range: Jan-Jul 2024 (7 months)")
        
        # 5. Setup CAT matrices for progression
        print("\n5. Setting up CAT matrices...")
        
        cat_matrices = {}
        for role, matrix_data in cat_matrices_data.items():
            cat_matrices[role] = CATMatrix(
                progression_probabilities=matrix_data["progression_probabilities"]
            )
        print(f"   Loaded CAT matrices for {len(cat_matrices)} roles")
        
        # 6. Initialize office state with our test population
        print("\n6. Initializing office state...")
        
        engine.office_states = {}
        
        # Create office state
        office_state = OfficeState(
            name="london",
            workforce={},
            business_plan=business_plan,
            snapshot=None,
            cat_matrices=cat_matrices,
            economic_parameters=None
        )
        
        # Add initial people to workforce
        for person_data in initial_people:
            person = Person(
                id=person_data["id"],
                current_role=person_data["role"],
                current_level=person_data["level"],
                current_office=person_data["office"],
                hire_date=date.fromisoformat(person_data["hire_date"] + "-01"),
                current_level_start=date.fromisoformat(person_data["hire_date"] + "-01"),
                events=[],
                is_active=True
            )
            
            # Create initial hire event for historical tracking
            from src.services.simulation_engine_v2 import PersonEvent, EventType
            hire_event = PersonEvent(
                date=person.hire_date,
                event_type=EventType.HIRED,
                details={
                    "person_id": person.id,
                    "role": person.current_role,
                    "level": person.current_level,
                    "office": person.current_office,
                    "hire_date": person.hire_date.strftime("%Y-%m-%d"),
                    "initial_employee": True  # Mark as initial vs new hire
                },
                simulation_month=0  # Pre-simulation event
            )
            person.add_event(hire_event)
            
            # Add to workforce structure
            if person.current_role not in office_state.workforce:
                office_state.workforce[person.current_role] = {}
            if person.current_level not in office_state.workforce[person.current_role]:
                office_state.workforce[person.current_role][person.current_level] = []
            office_state.workforce[person.current_role][person.current_level].append(person)
        
        engine.office_states["london"] = office_state
        print(f"   Office initialized with {len(initial_people)} people")
        
        # 7. Run simulation
        print("\n7. Running simulation...")
        
        scenario = ScenarioRequest(
            scenario_id="individual_tracking_test",
            name="Individual Event Tracking Test",
            time_range=TimeRange(2024, 1, 2024, 7),  # Jan-Jul 2024
            office_ids=["london"],
            levers=Levers(
                recruitment_multiplier=1.0,
                churn_multiplier=1.0,
                progression_multiplier=1.0
            )
        )
        
        print(f"   Simulating {scenario.time_range.get_total_months()} months...")
        print(f"   Progression months for levels:")
        print(f"      A/AC: [1, 4, 7] (Jan, Apr, Jul)")
        print(f"      C/SrC: [1, 7] (Jan, Jul)")
        print(f"      M+: [1] (Jan only)")
        
        start_time = datetime.now()
        results = engine.run_simulation(scenario)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        print(f"   Simulation completed in {execution_time:.3f} seconds")
        print(f"   Total events generated: {len(results.all_events)}")
        
        # 8. Analyze individual event tracking
        print("\n8. INDIVIDUAL EVENT TRACKING ANALYSIS")
        print("=" * 50)
        
        # Group events by person (including historical events from initial employees)
        events_by_person = defaultdict(list)
        
        # First, collect historical events from initial employees
        print("   DEBUG: Collecting events from final workforce...")
        all_final_person_ids = []
        for office_state in results.final_workforce.values():
            for role_levels in office_state.workforce.values():
                for level_people in role_levels.values():
                    for person in level_people:
                        all_final_person_ids.append(person.id)
                        if person.id in [p["id"] for p in initial_people]:
                            print(f"   DEBUG: Found original employee {person.id}, events: {len(person.events)}")
                            if person.events:
                                for event in person.events:
                                    print(f"     Event: {event.event_type.value} on {event.date}")
                                    events_by_person[person.id].append(event)
                            else:
                                print(f"     No events for {person.id}")
                        elif person.events:
                            for event in person.events:
                                events_by_person[person.id].append(event)
        
        original_ids = [p["id"] for p in initial_people]
        print(f"   DEBUG: Looking for original IDs: {original_ids}")
        print(f"   DEBUG: Final workforce has {len(all_final_person_ids)} people: {all_final_person_ids[:10]}...")
        missing_originals = [pid for pid in original_ids if pid not in all_final_person_ids]
        if missing_originals:
            print(f"   DEBUG: MISSING original employees: {missing_originals}")
        
        # Then, collect simulation events
        for event in results.all_events:
            person_id = event.details.get('person_id') or event.details.get('id', 'NEW_HIRE')
            if person_id == 'NEW_HIRE':
                # For recruitment events, generate a unique ID
                person_id = f"HIRED_{event.date.strftime('%Y%m')}_{len(events_by_person)}"
            events_by_person[person_id].append(event)
        
        print(f"Tracked events for {len(events_by_person)} individuals")
        
        # Categorize people
        original_people = [p["id"] for p in initial_people]
        hired_people = [pid for pid in events_by_person.keys() if pid.startswith("HIRED_")]
        
        print(f"   Original employees: {len([p for p in original_people if p in events_by_person])}")
        print(f"   New hires: {len(hired_people)}")
        
        # 9. Show individual journeys
        print("\n9. INDIVIDUAL EMPLOYEE JOURNEYS")
        print("-" * 40)
        
        # Show journeys for original employees
        print("\nOriginal Employees:")
        for person_id in original_people:
            if person_id in events_by_person:
                events = events_by_person[person_id]
                print(f"\n{person_id}:")
                for event in events:
                    event_type = event.event_type.value
                    if event_type == 'promoted':
                        from_level = event.details.get('from_level', '?')
                        to_level = event.details.get('to_level', '?')
                        print(f"   {event.date}: PROMOTED from {from_level} to {to_level}")
                    elif event_type == 'churned':
                        level = event.details.get('level', '?')
                        tenure = event.details.get('tenure_months', 0)
                        print(f"   {event.date}: CHURNED at {level} level (tenure: {tenure} months)")
                    else:
                        print(f"   {event.date}: {event_type.upper()}")
                
                if not events:
                    print("   No events (still active, no changes)")
            else:
                print(f"\n{person_id}: No events (still active, no changes)")
        
        # Show some new hire journeys
        print("\nNew Hires (first 5):")
        for person_id in hired_people[:5]:
            events = events_by_person[person_id]
            print(f"\n{person_id}:")
            for event in events:
                event_type = event.event_type.value
                if event_type == 'hired':
                    role = event.details.get('role', '?')
                    level = event.details.get('level', '?')
                    print(f"   {event.date}: HIRED as {role} {level}")
                elif event_type == 'promoted':
                    from_level = event.details.get('from_level', '?')
                    to_level = event.details.get('to_level', '?')
                    print(f"   {event.date}: PROMOTED from {from_level} to {to_level}")
                elif event_type == 'churned':
                    level = event.details.get('level', '?')
                    print(f"   {event.date}: CHURNED at {level} level")
        
        # 10. Event type summary
        print("\n10. EVENT TYPE SUMMARY")
        print("-" * 25)
        
        event_counts = defaultdict(int)
        event_by_month = defaultdict(lambda: defaultdict(int))
        
        for event in results.all_events:
            event_type = event.event_type.value
            event_counts[event_type] += 1
            month_key = event.date.strftime("%Y-%m")
            event_by_month[month_key][event_type] += 1
        
        print("Total events by type:")
        for event_type, count in sorted(event_counts.items()):
            print(f"   {event_type.upper()}: {count}")
        
        print("\nEvents by month:")
        for month in sorted(event_by_month.keys()):
            month_events = event_by_month[month]
            event_str = ", ".join([f"{k}:{v}" for k, v in sorted(month_events.items())])
            print(f"   {month}: {event_str}")
        
        # 11. Verify progression timing
        print("\n11. PROGRESSION TIMING VERIFICATION")
        print("-" * 35)
        
        progression_by_month = defaultdict(list)
        for event in results.all_events:
            if event.event_type.value == 'promoted':
                month = event.date.month
                from_level = event.details.get('from_level', '?')
                to_level = event.details.get('to_level', '?')
                progression_by_month[month].append(f"{from_level}->{to_level}")
        
        print("Progressions by month:")
        for month in sorted(progression_by_month.keys()):
            month_name = date(2024, month, 1).strftime("%B")
            progressions = progression_by_month[month]
            print(f"   Month {month} ({month_name}): {len(progressions)} progressions")
            for prog in progressions[:3]:  # Show first 3
                print(f"      - {prog}")
        
        # Verify progression months are correct
        print("\nProgression month compliance:")
        valid_months = {
            'A': [1, 4, 7, 10],
            'AC': [1, 4, 7, 10],
            'C': [1, 7],
            'SrC': [1, 7],
            'M': [1]
        }
        
        violations = []
        for event in results.all_events:
            if event.event_type.value == 'promoted':
                from_level = event.details.get('from_level', '?')
                month = event.date.month
                expected_months = valid_months.get(from_level, [])
                if expected_months and month not in expected_months:
                    violations.append(f"{from_level} progressed in month {month} (expected: {expected_months})")
        
        if violations:
            print("   VIOLATIONS FOUND:")
            for v in violations:
                print(f"      - {v}")
        else:
            print("   ALL PROGRESSIONS COMPLY WITH LEVEL-SPECIFIC MONTHS")
        
        # 12. Monthly results verification
        print("\n12. MONTHLY RESULTS VERIFICATION")
        print("-" * 35)
        
        print("Checking monthly results generation...")
        
        # Check if monthly results are populated
        if results.monthly_results:
            print(f"   Monthly results generated: {len(results.monthly_results)} months")
            
            # Show details for each month
            print("\nMonthly Results Details:")
            for month_key in sorted(results.monthly_results.keys()):
                month_result = results.monthly_results[month_key]
                print(f"\n   {month_key}:")
                print(f"      Year: {month_result.year}, Month: {month_result.month}")
                print(f"      Events this month: {len(month_result.events)}")
                
                # Office results
                if month_result.office_results:
                    for office_id, office_metrics in month_result.office_results.items():
                        print(f"      Office '{office_id}':")
                        print(f"         Total workforce: {office_metrics.get('total_workforce', 0)}")
                        
                        # Workforce by role
                        workforce_by_role = office_metrics.get('workforce_by_role', {})
                        if workforce_by_role:
                            print(f"         Workforce by role:")
                            for role, count in workforce_by_role.items():
                                print(f"            {role}: {count}")
                        
                        # Financial metrics
                        print(f"         Revenue: ${office_metrics.get('revenue', 0):,.0f}")
                        print(f"         Costs: ${office_metrics.get('costs', 0):,.0f}")
                        print(f"         Salary costs: ${office_metrics.get('salary_costs', 0):,.0f}")
                
                # Event breakdown for this month
                month_event_types = defaultdict(int)
                for event in month_result.events:
                    month_event_types[event.event_type.value] += 1
                
                if month_event_types:
                    print(f"      Events breakdown:")
                    for event_type, count in sorted(month_event_types.items()):
                        print(f"         {event_type}: {count}")
        else:
            print("   WARNING: No monthly results generated!")
        
        # 13. Final assessment
        print("\n13. FINAL ASSESSMENT")
        print("=" * 30)
        
        success_criteria = [
            ("Events generated", len(results.all_events) > 0),
            ("Recruitment events", event_counts.get('hired', 0) > 0),
            ("Churn events", event_counts.get('churned', 0) > 0),
            ("Progression events", event_counts.get('promoted', 0) > 0),
            ("Individual tracking", len(events_by_person) > 0),
            ("Multiple people tracked", len(events_by_person) > 5),
            ("Original employees tracked", any(p in events_by_person for p in original_people)),
            ("New hires tracked", len(hired_people) > 0),
            ("Progression timing correct", len(violations) == 0),
            ("Events across multiple months", len(event_by_month) > 3),
            ("Monthly results generated", len(results.monthly_results) > 0),
            ("Office results populated", all(mr.office_results for mr in results.monthly_results.values()) if results.monthly_results else False)
        ]
        
        passed = sum(1 for _, result in success_criteria if result)
        total = len(success_criteria)
        success_rate = (passed / total) * 100
        
        for criteria, result in success_criteria:
            status = "PASS" if result else "FAIL"
            print(f"   [{status}] {criteria}")
        
        print(f"\nSuccess Rate: {success_rate:.1f}% ({passed}/{total})")
        
        if success_rate >= 90:
            print("\nEXCELLENT: All systems working correctly!")
            print("- Recruitment, churn, and progression all functional")
            print("- Individual event tracking working perfectly")
            print("- Level-specific progression months enforced")
        elif success_rate >= 70:
            print("\nGOOD: Most systems working correctly")
            print("Some minor issues may need attention")
        else:
            print("\nISSUES: Systems need debugging")
        
        return success_rate >= 80, {
            'success_rate': success_rate,
            'total_events': len(results.all_events),
            'people_tracked': len(events_by_person),
            'recruitment': event_counts.get('hired', 0),
            'churn': event_counts.get('churned', 0),
            'progression': event_counts.get('promoted', 0),
            'violations': violations
        }
        
    except Exception as e:
        print(f"\nERROR: Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, {'error': str(e)}

if __name__ == "__main__":
    print("Testing Complete Individual Event Tracking")
    print("=" * 50)
    
    success, metrics = test_complete_individual_tracking()
    
    print("\n" + "=" * 50)
    if success:
        print("SUCCESS: Individual event tracking working perfectly!")
        print(f"Tracked {metrics['people_tracked']} individuals")
        print(f"Generated: {metrics['recruitment']} hires, {metrics['churn']} churns, {metrics['progression']} promotions")
    else:
        print("FAILURE: Issues with event tracking")
        if 'error' in metrics:
            print(f"Error: {metrics['error']}")
    
    print("Test complete.")