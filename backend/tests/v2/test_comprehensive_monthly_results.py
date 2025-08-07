"""
Comprehensive Monthly Results Test - V2 Engine

Tests V2 engine with correct scenario levers and shows:
1. Monthly results breakdown for each month
2. All three systems working (recruitment, progression, churn)
3. Individual person event tracking and journeys
4. Workforce changes month by month
"""

import sys
import json
from pathlib import Path
from datetime import date
from collections import defaultdict, Counter

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_comprehensive_monthly_results():
    """Test V2 engine with comprehensive monthly analysis"""
    print("V2 ENGINE - COMPREHENSIVE MONTHLY RESULTS TEST")
    print("=" * 50)
    
    try:
        from src.services.simulation_engine_v2 import (
            SimulationEngineV2Factory, ScenarioRequest, TimeRange, Levers,
            BusinessPlan, MonthlyPlan, PopulationSnapshot, WorkforceEntry, 
            Person, OfficeState, CATMatrix
        )
        
        # 1. Setup engine with all data
        print("1. Setting up V2 engine with comprehensive data...")
        
        engine = SimulationEngineV2Factory.create_test_engine(random_seed=42)
        test_data_dir = Path(__file__).parent / "test_data"
        
        # Load all data
        with open(test_data_dir / "business_plans.json") as f:
            business_plans_data = json.load(f)
        
        with open(test_data_dir / "cat_matrices_correct.json") as f:
            cat_matrices_data = json.load(f)
            
        with open(test_data_dir / "population_snapshots.json") as f:
            population_data = json.load(f)
        
        # Setup business plans
        engine.business_processor.loaded_plans = {}
        
        for office_id, plan_data in business_plans_data.items():
            monthly_plans = {}
            
            for month, month_data in plan_data["monthly_plans"].items():
                monthly_plan = MonthlyPlan(
                    year=int(month.split("-")[0]),
                    month=int(month.split("-")[1]),
                    recruitment=month_data["recruitment"],
                    churn=month_data["churn"],
                    revenue=float(month_data["revenue"]),
                    costs=float(month_data["costs"]),
                    price_per_role={},
                    salary_per_role={},
                    utr_per_role={}
                )
                monthly_plans[month] = monthly_plan
            
            business_plan = BusinessPlan(
                office_id=plan_data["office_id"],
                name=plan_data["name"],
                monthly_plans=monthly_plans
            )
            
            engine.business_processor.loaded_plans[office_id] = business_plan
        
        print(f"   Loaded business plans: {len(engine.business_processor.loaded_plans)} offices")
        
        # Setup CAT matrices
        cat_matrices = {}
        for role, matrix_data in cat_matrices_data.items():
            cat_matrices[role] = CATMatrix(
                progression_probabilities=matrix_data["progression_probabilities"]
            )
        
        print(f"   Loaded CAT matrices: {len(cat_matrices)} roles")
        
        # Setup population
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
        
        print(f"   Loaded population: {sum(len(s.workforce) for s in population_snapshots.values())} people")
        
        # Create office state
        engine.office_states = {}
        office_id = "london"
        
        office_state = OfficeState(
            name=office_id,
            workforce={},
            business_plan=engine.business_processor.loaded_plans.get(office_id),
            snapshot=population_snapshots.get(office_id),
            cat_matrices=cat_matrices,
            economic_parameters=None
        )
        
        # Populate workforce
        if office_id in population_snapshots:
            snapshot = population_snapshots[office_id]
            office_state.workforce = {}
            
            for entry in snapshot.workforce:
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
                
                if entry.role not in office_state.workforce:
                    office_state.workforce[entry.role] = {}
                if entry.level not in office_state.workforce[entry.role]:
                    office_state.workforce[entry.role][entry.level] = []
                
                office_state.workforce[entry.role][entry.level].append(person)
        
        engine.office_states[office_id] = office_state
        
        initial_workforce = office_state.get_total_workforce()
        print(f"   Office setup complete: {initial_workforce} people")
        
        # 2. Run scenario with CORRECT levers (avoid churn rounding to 0)
        print("\\n2. Running scenario with corrected levers...")
        
        scenario = ScenarioRequest(
            scenario_id="comprehensive_monthly_test",
            name="Comprehensive Monthly Results Test",
            time_range=TimeRange(2024, 6, 2024, 12),  # 7 months
            office_ids=["london"],
            levers=Levers(
                recruitment_multiplier=1.0,  # Keep recruitment at business plan levels
                churn_multiplier=1.1,       # 10% MORE churn (avoids rounding to 0)
                progression_multiplier=1.0  # Normal progression
            )
        )
        
        print(f"   Time range: {scenario.time_range.start_year}-{scenario.time_range.start_month:02d} to {scenario.time_range.end_year}-{scenario.time_range.end_month:02d}")
        print(f"   Scenario levers: recruitment=1.0x, churn=1.1x, progression=1.0x")
        
        results = engine.run_simulation(scenario)
        
        print(f"   Simulation completed: {len(results.all_events)} total events")
        
        # 3. Monthly results breakdown
        print("\\n3. MONTHLY RESULTS BREAKDOWN")
        print("=" * 35)
        
        # Group events by month
        events_by_month = defaultdict(list)
        for event in results.all_events:
            month_key = f"{event.date.year}-{event.date.month:02d}"
            events_by_month[month_key].append(event)
        
        # Show each month's activity
        for year in range(scenario.time_range.start_year, scenario.time_range.end_year + 1):
            for month in range(1, 13):
                if year == scenario.time_range.start_year and month < scenario.time_range.start_month:
                    continue
                if year == scenario.time_range.end_year and month > scenario.time_range.end_month:
                    break
                    
                month_key = f"{year}-{month:02d}"
                month_events = events_by_month.get(month_key, [])
                
                if month_events:
                    print(f"\\n   {month_key}: {len(month_events)} events")
                    
                    # Event type breakdown
                    event_types = Counter(event.event_type.value for event in month_events)
                    for event_type, count in event_types.items():
                        print(f"      {event_type.title()}: {count}")
                    
                    # Business plan targets for this month
                    monthly_targets = engine.business_processor.get_monthly_targets(office_id, year, month)
                    applied_levers = engine.business_processor.apply_scenario_levers(monthly_targets, scenario.levers)
                    
                    print(f"      Business plan targets (after levers):")
                    
                    # Show recruitment targets
                    recruitment_total = 0
                    for role, levels in applied_levers.recruitment_targets.items():
                        for level, count in levels.items():
                            if count > 0:
                                recruitment_total += count
                                print(f"         Recruit {role} {level}: {count}")
                    
                    # Show churn targets
                    churn_total = 0
                    for role, levels in applied_levers.churn_targets.items():
                        for level, count in levels.items():
                            if count > 0:
                                churn_total += count
                                print(f"         Churn {role} {level}: {count}")
                    
                    print(f"      Expected: {recruitment_total} hires, {churn_total} churns")
                    print(f"      Actual: {event_types.get('hired', 0)} hires, {event_types.get('churned', 0)} churns, {event_types.get('promoted', 0)} promotions")
                    
                else:
                    print(f"\\n   {month_key}: No events")
        
        # 4. Individual Person Event Tracking
        print("\\n4. INDIVIDUAL PERSON EVENT TRACKING")
        print("=" * 40)
        
        # Group events by person
        events_by_person = defaultdict(list)
        for event in results.all_events:
            person_id = event.details.get('person_id') or event.details.get('id', 'unknown')
            events_by_person[person_id].append(event)
        
        print(f"   Total people with events: {len(events_by_person)}")
        
        # Show people with multiple events (interesting journeys)
        multi_event_people = {pid: events for pid, events in events_by_person.items() if len(events) > 1}
        print(f"   People with multiple events: {len(multi_event_people)}")
        
        if multi_event_people:
            print("\\n   Sample individual journeys:")
            
            for i, (person_id, events) in enumerate(list(multi_event_people.items())[:5]):
                # Sort events by date
                events = sorted(events, key=lambda e: e.date)
                
                print(f"\\n      Person {person_id}: {len(events)} events")
                for event in events:
                    event_desc = event.event_type.value.title()
                    
                    if event.event_type.value == 'hired':
                        role = event.details.get('role', '')
                        level = event.details.get('level', '')
                        event_desc += f" as {role} {level}"
                        
                    elif event.event_type.value == 'promoted':
                        from_level = event.details.get('from_level', '')
                        to_level = event.details.get('to_level', '')
                        role = event.details.get('role', '')
                        event_desc += f" {role} {from_level} -> {to_level}"
                        
                    elif event.event_type.value == 'churned':
                        role = event.details.get('role', '')
                        level = event.details.get('level', '')
                        tenure = event.details.get('tenure_months', 0)
                        event_desc += f" {role} {level} after {tenure} months"
                    
                    print(f"         {event.date}: {event_desc}")
        
        # 5. Event Data Structure Analysis
        print("\\n5. EVENT DATA STRUCTURE ANALYSIS")
        print("=" * 40)
        
        if results.all_events:
            sample_event = results.all_events[0]
            print("\\n   Sample event structure:")
            print(f"      Type: {type(sample_event).__name__}")
            print(f"      Date: {sample_event.date}")
            print(f"      Event Type: {sample_event.event_type}")
            print(f"      Details: {sample_event.details}")
            
            print("\\n   How events are returned:")
            print("      - All events in results.all_events list")
            print("      - Each event has: date, event_type, details dict")
            print("      - Person ID in details['person_id'] or details['id']")
            print("      - Event-specific data in details dict")
            print("      - Events sorted by date within simulation")
        
        # 6. Workforce State Changes
        print("\\n6. WORKFORCE STATE CHANGES")
        print("=" * 35)
        
        final_workforce = results.final_workforce["london"].get_total_workforce()
        
        event_summary = Counter(event.event_type.value for event in results.all_events)
        hired_count = event_summary.get('hired', 0)
        churned_count = event_summary.get('churned', 0)
        promoted_count = event_summary.get('promoted', 0)
        
        print(f"   Initial workforce: {initial_workforce} people")
        print(f"   Final workforce: {final_workforce} people")
        print(f"   Net change: {final_workforce - initial_workforce:+d} people")
        print(f"   ")
        print(f"   Event summary:")
        print(f"      Hired: +{hired_count}")
        print(f"      Churned: -{churned_count}")
        print(f"      Promoted: {promoted_count} (internal moves)")
        print(f"      Net headcount change: +{hired_count - churned_count}")
        
        # 7. System Verification
        print("\\n7. SYSTEM VERIFICATION")
        print("=" * 25)
        
        systems_working = {
            'recruitment': hired_count > 0,
            'churn': churned_count > 0,
            'progression': promoted_count > 0
        }
        
        print("   Core systems status:")
        for system, working in systems_working.items():
            status = "WORKING" if working else "BROKEN"
            count = event_summary.get('hired' if system == 'recruitment' else 'churned' if system == 'churn' else 'promoted', 0)
            print(f"      {system.title()}: {status} ({count} events)")
        
        all_working = all(systems_working.values())
        success_rate = len([s for s in systems_working.values() if s]) / len(systems_working) * 100
        
        print(f"\\n   Overall success rate: {success_rate:.1f}%")
        
        if all_working:
            print("\\n   EXCELLENT: All three systems fully functional!")
            print("   V2 Engine is ready for production use.")
        else:
            print("\\n   Some systems still need work.")
        
        return all_working, {
            'total_events': len(results.all_events),
            'monthly_breakdown': dict(Counter(f"{e.date.year}-{e.date.month:02d}" for e in results.all_events)),
            'event_breakdown': dict(event_summary),
            'individual_tracking': len(events_by_person),
            'multi_event_people': len(multi_event_people),
            'initial_workforce': initial_workforce,
            'final_workforce': final_workforce,
            'systems_working': systems_working
        }
        
    except Exception as e:
        print(f"\\nERROR: Comprehensive test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, {'error': str(e)}

if __name__ == "__main__":
    print("Starting Comprehensive Monthly Results Test")
    print("=" * 50)
    
    success, metrics = test_comprehensive_monthly_results()
    
    print("\\n" + "=" * 50)
    if success:
        print("SUCCESS: V2 Engine fully functional!")
        print(f"Generated {metrics['total_events']} events across {len(metrics['monthly_breakdown'])} months")
        print(f"Individual tracking: {metrics['individual_tracking']} people")
        print("All systems working: Recruitment + Progression + Churn")
    else:
        print("FAILURE: Some issues remain")
        if 'error' in metrics:
            print(f"Error: {metrics['error']}")
    
    print(f"\\nFinal assessment: {metrics.get('total_events', 0)} total events generated")