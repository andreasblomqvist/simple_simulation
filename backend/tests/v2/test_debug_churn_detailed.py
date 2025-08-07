"""
Debug Churn Processing - Detailed Workforce Analysis

Investigate why churn events are 0 by examining the exact workforce state
during churn processing in the comprehensive test.
"""

import sys
import json
from pathlib import Path
from datetime import date

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_churn_detailed():
    """Debug churn by examining workforce state during processing"""
    print("DEBUGGING CHURN - DETAILED WORKFORCE ANALYSIS")
    print("=" * 50)
    
    try:
        from src.services.simulation_engine_v2 import (
            SimulationEngineV2Factory, ScenarioRequest, TimeRange, Levers,
            BusinessPlan, MonthlyPlan, PopulationSnapshot, WorkforceEntry, 
            Person, OfficeState, CATMatrix
        )
        
        # 1. Setup exact same as comprehensive test
        print("1. Setting up exact same data as comprehensive test...")
        
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
        
        # Setup CAT matrices
        cat_matrices = {}
        for role, matrix_data in cat_matrices_data.items():
            cat_matrices[role] = CATMatrix(
                progression_probabilities=matrix_data["progression_probabilities"]
            )
        
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
        
        print(f"   London office setup complete: {office_state.get_total_workforce()} people")
        
        # 2. Test specific months with churn targets
        print("\n2. Testing months with churn targets...")
        
        churn_months = [
            (2024, 6),  # June: A=1, AC=1, Sales A=1
            (2024, 7),  # July: A=1
        ]
        
        for year, month in churn_months:
            print(f"\n   Testing {year}-{month:02d}...")
            
            # Get business plan targets for this month
            monthly_targets = engine.business_processor.get_monthly_targets(office_id, year, month)
            
            print(f"      Business plan churn targets:")
            for role, levels in monthly_targets.churn_targets.items():
                for level, count in levels.items():
                    if count > 0:
                        print(f"         {role} {level}: {count}")
            
            # Check available workforce BEFORE any processing
            print(f"      Available workforce BEFORE processing:")
            total_available = 0
            for role, levels in office_state.workforce.items():
                for level, people in levels.items():
                    active_people = [p for p in people if p.is_active]
                    if active_people:
                        print(f"         {role} {level}: {len(active_people)} people")
                        total_available += len(active_people)
            
            print(f"      Total active workforce: {total_available}")
            
            # Now test churn processing specifically
            test_date = date(year, month, 15)
            month_churn_events = []
            
            print(f"      Processing churn for {year}-{month:02d}...")
            
            # Apply levers to targets (same as engine does)
            levers = Levers(recruitment_multiplier=1.2, churn_multiplier=0.9, progression_multiplier=1.0)
            adjusted_targets = engine.business_processor.apply_scenario_levers(monthly_targets, levers)
            
            print(f"      Adjusted churn targets (with 0.9x multiplier):")
            total_churn_target = 0
            for role, levels in adjusted_targets.churn_targets.items():
                for level, count in levels.items():
                    if count > 0:
                        print(f"         {role} {level}: {count}")
                        total_churn_target += count
            
            # Process churn exactly like the engine does
            for role, levels in office_state.workforce.items():
                for level, people in levels.items():
                    if people:
                        active_people = [p for p in people if p.is_active]
                        churn_target = adjusted_targets.churn_targets.get(role, {}).get(level, 0)
                        
                        if churn_target > 0 and active_people:
                            print(f"         Processing churn: {role} {level} - {len(active_people)} people, target: {churn_target}")
                            
                            churn_events = engine.workforce_manager.process_churn(
                                active_people, {level: churn_target}, test_date
                            )
                            month_churn_events.extend(churn_events)
                            
                            print(f"            Generated: {len(churn_events)} churn events")
                        elif churn_target > 0 and not active_people:
                            print(f"         PROBLEM: {role} {level} - target: {churn_target} but NO active people!")
            
            print(f"      Total churn events for {year}-{month:02d}: {len(month_churn_events)}")
            
            if len(month_churn_events) == 0 and total_churn_target > 0:
                print(f"      ERROR: Expected {total_churn_target} churn events, got 0")
            elif len(month_churn_events) > 0:
                print(f"      SUCCESS: Generated {len(month_churn_events)} churn events")
        
        # 3. Final analysis
        print("\n3. CHURN PROCESSING ANALYSIS")
        print("-" * 35)
        
        print("   Key findings:")
        print("   - Business plan has churn targets")
        print("   - Workforce has people available")
        print("   - Processing order: Churn → Progression → Recruitment")
        print("   - Need to check if workforce manager churn logic is working")
        
        # 4. Test workforce manager churn directly
        print("\n4. Testing workforce manager churn directly...")
        
        # Create test people
        test_people = []
        for i in range(3):
            person = Person(
                id=f"TEST_CHURN_{i:02d}",
                current_role="Consultant",
                current_level="A",
                current_office="london",
                hire_date=date(2023, 1, 1),
                current_level_start=date(2023, 1, 1),
                events=[],
                is_active=True
            )
            test_people.append(person)
        
        print(f"   Created {len(test_people)} test A-level people")
        
        # Test direct churn
        direct_churn_events = engine.workforce_manager.process_churn(
            test_people, {"A": 1}, date(2024, 7, 15)
        )
        
        print(f"   Direct churn processing result: {len(direct_churn_events)} events")
        
        if len(direct_churn_events) > 0:
            print("   SUCCESS: Workforce manager churn is working")
            print("   CONCLUSION: Issue must be in comprehensive test setup or data")
        else:
            print("   FAILURE: Workforce manager churn is broken")
            print("   CONCLUSION: Core churn logic has a bug")
        
        return len(direct_churn_events) > 0
        
    except Exception as e:
        print(f"\nERROR: Detailed churn debug failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_churn_detailed()
    if success:
        print("\nWorkforce manager churn is functional!")
        print("Issue is in comprehensive test setup or data.")
    else:
        print("\nWorkforce manager churn is broken!")
        print("Core churn logic needs debugging.")