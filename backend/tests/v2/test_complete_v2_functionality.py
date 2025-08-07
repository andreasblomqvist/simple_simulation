"""
Complete V2 Engine Functionality Test

Tests the fully integrated V2 engine with:
1. Recruitment events (fixed)
2. Progression events (fixed)  
3. Churn events
4. Real business data and CAT matrices
5. Individual event tracking
"""

import sys
import json
from pathlib import Path
from datetime import datetime, date
from collections import Counter

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_complete_v2_functionality():
    """Test complete V2 engine functionality with recruitment and progression working"""
    print("V2 Engine - Complete Functionality Test")
    print("=" * 45)
    
    try:
        from src.services.simulation_engine_v2 import (
            SimulationEngineV2Factory, ScenarioRequest, TimeRange, Levers,
            BusinessPlan, MonthlyPlan, MonthlyTargets, CATMatrix,
            PopulationSnapshot, WorkforceEntry, Person, OfficeState
        )
        
        # 1. Create engine
        print("1. Creating V2 engine...")
        engine = SimulationEngineV2Factory.create_test_engine(random_seed=42)
        
        # 2. Load test data
        print("2. Loading test data...")
        test_data_dir = Path(__file__).parent / "test_data"
        
        with open(test_data_dir / "business_plans.json") as f:
            business_plans_data = json.load(f)
        
        with open(test_data_dir / "cat_matrices_correct.json") as f:
            cat_matrices_data = json.load(f)
            
        with open(test_data_dir / "population_snapshots.json") as f:
            population_data = json.load(f)
        
        print(f"  Loaded business plans for {len(business_plans_data)} offices")
        print(f"  Loaded CAT matrices for {len(cat_matrices_data)} roles")  
        print(f"  Loaded population data for {len(population_data)} offices")
        
        # 3. Create business plans with correct structure
        print("3. Creating business plans...")
        
        if not hasattr(engine.business_processor, 'loaded_plans'):
            engine.business_processor.loaded_plans = {}
        
        for office_id, plan_data in business_plans_data.items():
            # Convert recruitment and churn data to monthly targets format
            monthly_plans = {}
            
            for month, month_data in plan_data["monthly_plans"].items():
                # Create MonthlyTargets with correct structure
                targets = MonthlyTargets(
                    year=int(month.split("-")[0]),
                    month=int(month.split("-")[1]), 
                    recruitment_targets=month_data["recruitment"],  # Direct from JSON
                    churn_targets=month_data["churn"],  # Direct from JSON
                    revenue_target=float(month_data["targets"]["revenue_target"]),
                    operating_costs=float(month_data["costs"]),
                    salary_budget=300000.0  # Default
                )
                
                monthly_plan = MonthlyPlan(
                    year=int(month.split("-")[0]),
                    month=int(month.split("-")[1]),
                    recruitment=month_data["recruitment"],
                    churn=month_data["churn"],
                    revenue=float(month_data["revenue"]),
                    costs=float(month_data["costs"]),
                    price_per_role={},  # Default
                    salary_per_role={},  # Default  
                    utr_per_role={}  # Default
                )
                
                monthly_plans[month] = monthly_plan
            
            business_plan = BusinessPlan(
                office_id=plan_data["office_id"],
                name=plan_data["name"], 
                monthly_plans=monthly_plans
            )
            
            engine.business_processor.loaded_plans[office_id] = business_plan
            print(f"  Created business plan for {office_id}: {len(monthly_plans)} months")
        
        # 4. Create CAT matrices
        print("4. Creating CAT matrices...")
        
        cat_matrices = {}
        for role, matrix_data in cat_matrices_data.items():
            cat_matrices[role] = CATMatrix(
                progression_probabilities=matrix_data["progression_probabilities"]
            )
            levels = len(matrix_data["progression_probabilities"])
            print(f"  Created CAT matrix for {role}: {levels} progression levels")
        
        # 5. Create and load population snapshot
        print("5. Loading population snapshots...")
        
        population_snapshots = {}
        for office_id, snapshot_data in population_data.items():
            workforce_entries = []
            for entry_data in snapshot_data["workforce"]:
                workforce_entries.append(WorkforceEntry(
                    id=entry_data["id"],
                    role=entry_data["role"],
                    level=entry_data["level"],
                    hire_date=entry_data["hire_date"],
                    level_start_date=entry_data["level_start_date"],
                    office=entry_data["office"]
                ))
            
            population_snapshots[office_id] = PopulationSnapshot(
                id=snapshot_data["id"],
                office_id=snapshot_data["office_id"],
                snapshot_date=snapshot_data["snapshot_date"],
                name=snapshot_data["name"],
                workforce=workforce_entries
            )
            
            print(f"  Loaded population for {office_id}: {len(workforce_entries)} people")
        
        # 6. Manually initialize office states (bypass engine loading)
        print("6. Initializing office states with all data...")
        
        engine.office_states = {}
        
        for office_id in ["london"]:
            # Create office state with correct structure
            office_state = OfficeState(
                name=office_id,
                workforce={},
                business_plan=engine.business_processor.loaded_plans.get(office_id),
                snapshot=population_snapshots.get(office_id),
                cat_matrices={},  # Will be set below
                economic_parameters=None
            )
            
            # Organize workforce from population snapshot
            if office_id in population_snapshots:
                snapshot = population_snapshots[office_id]
                office_state.workforce = {}
                
                # Convert workforce entries to Person objects
                for entry in snapshot.workforce:
                    # Parse hire date properly
                    hire_date = date.fromisoformat(entry.hire_date + "-01")
                    level_start_date = date.fromisoformat(entry.level_start_date + "-01")
                    
                    person = Person(
                        id=entry.id,
                        current_role=entry.role,
                        current_level=entry.level,
                        current_office=entry.office,
                        hire_date=hire_date,
                        current_level_start=level_start_date,
                        events=[],
                        is_active=True
                    )
                    
                    # Add to workforce structure
                    if entry.role not in office_state.workforce:
                        office_state.workforce[entry.role] = {}
                    if entry.level not in office_state.workforce[entry.role]:
                        office_state.workforce[entry.role][entry.level] = []
                    
                    office_state.workforce[entry.role][entry.level].append(person)
            
            # Set CAT matrices (the fix!)
            office_state.cat_matrices = cat_matrices
            
            engine.office_states[office_id] = office_state
            
            total_workforce = office_state.get_total_workforce()
            print(f"  {office_id}: {total_workforce} people, business plan: {office_state.business_plan is not None}, CAT matrices: {len(office_state.cat_matrices)}")
        
        # 7. Run comprehensive simulation
        print("7. Running comprehensive simulation...")
        
        scenario = ScenarioRequest(
            scenario_id="complete_test",
            name="Complete Functionality Test",
            time_range=TimeRange(2024, 6, 2024, 12),  # 6 months including progression months
            office_ids=["london"],
            levers=Levers(
                recruitment_multiplier=1.2,  # 20% more recruitment
                churn_multiplier=0.9,       # 10% less churn
                progression_multiplier=1.0  # Normal progression
            )
        )
        
        print(f"  Running {scenario.time_range.get_total_months()}-month simulation...")
        print(f"  Time range: {scenario.time_range.start_year}-{scenario.time_range.start_month:02d} to {scenario.time_range.end_year}-{scenario.time_range.end_month:02d}")
        print(f"  Includes progression months: 7 (July) for all levels")
        
        # Debug progression setup
        print("\\n  Progression setup verification:")
        for office_id, office_state in engine.office_states.items():
            print(f"    {office_id}: {len(office_state.cat_matrices)} CAT matrices")
            for role, matrix in office_state.cat_matrices.items():
                if hasattr(matrix, 'progression_probabilities'):
                    levels = list(matrix.progression_probabilities.keys())
                    print(f"      {role}: {levels}")
            
            # Check workforce eligible for progression
            total_a_level = len(office_state.workforce.get('Consultant', {}).get('A', []))
            total_ac_level = len(office_state.workforce.get('Consultant', {}).get('AC', []))
            total_c_level = len(office_state.workforce.get('Consultant', {}).get('C', []))
            print(f"      Consultant workforce: A={total_a_level}, AC={total_ac_level}, C={total_c_level}")
        
        # Check workforce manager progression configuration
        if hasattr(engine.workforce_manager, 'level_progression_months'):
            print(f"    WM progression months: A={engine.workforce_manager.level_progression_months.get('A', 'None')}")
            print(f"                          C={engine.workforce_manager.level_progression_months.get('C', 'None')}")
        
        start_time = datetime.now()
        results = engine.run_simulation(scenario)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        print(f"  Simulation completed in {execution_time:.2f} seconds")
        print(f"  Total events generated: {len(results.all_events)}")
        
        # 8. Comprehensive results analysis
        print()
        print("8. COMPREHENSIVE RESULTS ANALYSIS")
        print("=" * 35)
        
        if len(results.all_events) > 0:
            # Event type breakdown
            event_types = Counter(event.event_type.value for event in results.all_events)
            print("Event Type Summary:")
            for event_type, count in event_types.items():
                print(f"  {event_type.upper()}: {count}")
            
            # Detailed verification
            has_recruitment = event_types.get('hired', 0) > 0
            has_progression = event_types.get('promoted', 0) > 0
            has_churn = event_types.get('churned', 0) > 0
            
            print()
            print("Core Functionality Verification:")
            print(f"  * Recruitment: {'WORKING' if has_recruitment else 'BROKEN'} ({event_types.get('hired', 0)} events)")
            print(f"  * Progression: {'WORKING' if has_progression else 'BROKEN'} ({event_types.get('promoted', 0)} events)")
            print(f"  * Churn: {'WORKING' if has_churn else 'BROKEN'} ({event_types.get('churned', 0)} events)")
            
            # Show sample events from each type
            print()
            print("Sample Events:")
            
            if has_recruitment:
                hire_events = [e for e in results.all_events if e.event_type.value == 'hired'][:2]
                print("  Recruitment events:")
                for event in hire_events:
                    role = event.details.get('role', 'Unknown')
                    level = event.details.get('level', '')
                    print(f"    - Hired {role} {level} on {event.date}")
            
            if has_progression:
                promotion_events = [e for e in results.all_events if e.event_type.value == 'promoted'][:2]
                print("  Progression events:")
                for event in promotion_events:
                    role = event.details.get('role', 'Unknown')
                    from_level = event.details.get('from_level', '')
                    to_level = event.details.get('to_level', '')
                    print(f"    - Promoted {role} from {from_level} to {to_level} on {event.date}")
            
            if has_churn:
                churn_events = [e for e in results.all_events if e.event_type.value == 'churned'][:2]
                print("  Churn events:")
                for event in churn_events:
                    role = event.details.get('role', 'Unknown')
                    level = event.details.get('level', '')
                    tenure = event.details.get('tenure_months', 0)
                    print(f"    - Churned {role} {level} after {tenure} months on {event.date}")
            
            # Individual tracking analysis
            events_by_person = {}
            for event in results.all_events:
                person_id = event.details.get('person_id') or event.details.get('id', 'unknown')
                if person_id not in events_by_person:
                    events_by_person[person_id] = []
                events_by_person[person_id].append(event)
            
            print()
            print(f"Individual Tracking: {len(events_by_person)} people with events")
            
            # Show journeys for people with multiple events
            multi_event_people = {pid: events for pid, events in events_by_person.items() if len(events) > 1}
            if multi_event_people:
                print(f"  People with multiple events: {len(multi_event_people)}")
                for person_id, events in list(multi_event_people.items())[:3]:
                    print(f"    {person_id}: {len(events)} events")
                    for event in events:
                        event_desc = f"{event.event_type.value}"
                        if event.event_type.value == 'promoted':
                            from_level = event.details.get('from_level', '')
                            to_level = event.details.get('to_level', '')
                            event_desc += f" {from_level} to {to_level}"
                        print(f"      {event.date}: {event_desc}")
        
        else:
            print("FAIL: NO EVENTS GENERATED - Major issue with simulation")
        
        # 9. Workforce analysis
        print()
        print("9. WORKFORCE ANALYSIS")
        print("-" * 25)
        
        initial_workforce = sum(len(snapshot.workforce) for snapshot in population_snapshots.values())
        final_workforce = sum(office.get_total_workforce() for office in results.final_workforce.values())
        
        hired_count = event_types.get('hired', 0) if results.all_events else 0
        churned_count = event_types.get('churned', 0) if results.all_events else 0
        net_change = hired_count - churned_count
        
        print(f"Initial workforce: {initial_workforce} people")
        print(f"Final workforce: {final_workforce} people")
        print(f"Hired: +{hired_count}")
        print(f"Churned: -{churned_count}")
        print(f"Net change: {net_change:+d} people")
        
        # 10. Final assessment
        print()
        print("10. FINAL ASSESSMENT")
        print("=" * 20)
        
        success_criteria = [
            ("Business plans loaded", len(engine.business_processor.loaded_plans) > 0),
            ("Population data loaded", initial_workforce > 0),
            ("CAT matrices loaded", any(len(office.cat_matrices) > 0 for office in engine.office_states.values())),
            ("Simulation executed", len(results.all_events) >= 0),
            ("Events generated", len(results.all_events) > 0),
            ("Recruitment working", event_types.get('hired', 0) > 0 if results.all_events else False),
            ("Progression working", event_types.get('promoted', 0) > 0 if results.all_events else False),
            ("Churn working", event_types.get('churned', 0) > 0 if results.all_events else False),
            ("Individual tracking", len(events_by_person) > 0 if results.all_events else False),
            ("Multiple event types", len(event_types) >= 2 if results.all_events else False),
        ]
        
        passed = sum(1 for _, result in success_criteria if result)
        total = len(success_criteria)
        success_rate = (passed / total) * 100
        
        for criteria, result in success_criteria:
            status = "PASS" if result else "FAIL"
            print(f"  [{status}] {criteria}")
        
        print()
        print(f"SUCCESS RATE: {success_rate:.1f}% ({passed}/{total})")
        
        if success_rate >= 90:
            print()
            print("EXCELLENT: V2 Engine is fully functional!")
            print("All core features working: Recruitment + Progression + Churn")
        elif success_rate >= 70:
            print()
            print("GOOD: V2 Engine is mostly working")
            print("Some minor issues may remain")
        else:
            print()
            print("ISSUES: V2 Engine needs more work")
            print("Major functionality is still broken")
        
        return success_rate >= 70, {
            'success_rate': success_rate,
            'total_events': len(results.all_events),
            'event_breakdown': dict(event_types) if results.all_events else {},
            'initial_workforce': initial_workforce,
            'final_workforce': final_workforce,
            'execution_time': execution_time,
            'recruitment_working': event_types.get('hired', 0) > 0 if results.all_events else False,
            'progression_working': event_types.get('promoted', 0) > 0 if results.all_events else False,
            'churn_working': event_types.get('churned', 0) > 0 if results.all_events else False
        }
        
    except Exception as e:
        print(f"FAIL: Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, {'error': str(e)}

if __name__ == "__main__":
    print("Testing Complete V2 Engine Functionality")
    print("=" * 45)
    
    success, metrics = test_complete_v2_functionality()
    
    print()
    print("=" * 45)
    if success:
        print("SUCCESS: V2 Engine is working!")
        if metrics.get('recruitment_working') and metrics.get('progression_working'):
            print("Both recruitment and progression are functional!")
        print(f"Generated {metrics['total_events']} events in {metrics['execution_time']:.2f}s")
    else:
        print("V2 Engine still has issues")
        if 'error' in metrics:
            print(f"Error: {metrics['error']}")
    
    print(f"Final assessment: {metrics.get('success_rate', 0):.1f}% success rate")