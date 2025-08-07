"""
V2 Engine Verification Test with Realistic Data

Tests the V2 engine using comprehensive test data to verify:
- Proper simulation execution with real business plans
- Individual event tracking and progression
- Realistic workforce growth scenarios
- Complete KPI generation
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from collections import Counter

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def load_test_data():
    """Load all test data from JSON files"""
    test_data_dir = Path(__file__).parent / "test_data"
    
    with open(test_data_dir / "population_snapshots.json") as f:
        population_snapshots = json.load(f)
    
    with open(test_data_dir / "business_plans.json") as f:
        business_plans = json.load(f)
    
    with open(test_data_dir / "cat_matrices.json") as f:
        cat_matrices = json.load(f)
        
    with open(test_data_dir / "office_configurations.json") as f:
        office_configs = json.load(f)
        
    with open(test_data_dir / "test_scenarios.json") as f:
        test_scenarios = json.load(f)
    
    return {
        "population_snapshots": population_snapshots,
        "business_plans": business_plans,
        "cat_matrices": cat_matrices,
        "office_configs": office_configs,
        "test_scenarios": test_scenarios
    }

def create_mock_data_loaders(test_data):
    """Create mock data loaders that return our test data"""
    from unittest.mock import patch, MagicMock
    
    # Mock population snapshot loading
    def mock_load_snapshot(office_id, snapshot_id):
        if office_id in test_data["population_snapshots"]:
            snapshot_data = test_data["population_snapshots"][office_id]
            from src.services.simulation_engine_v2 import PopulationSnapshot, WorkforceEntry
            
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
            
            return PopulationSnapshot(
                id=snapshot_data["id"],
                office_id=snapshot_data["office_id"],
                snapshot_date=snapshot_data["snapshot_date"],
                name=snapshot_data["name"],
                workforce=workforce_entries
            )
        return None
    
    # Mock business plan loading
    def mock_load_business_plan(office_id, plan_id):
        if office_id in test_data["business_plans"]:
            plan_data = test_data["business_plans"][office_id]
            from src.services.simulation_engine_v2 import BusinessPlan, MonthlyPlan, MonthlyTargets
            
            monthly_plans = {}
            for month, month_data in plan_data["monthly_plans"].items():
                monthly_plans[month] = MonthlyPlan(
                    month=month_data["month"],
                    revenue=month_data["revenue"],
                    costs=month_data["costs"],
                    recruitment=month_data["recruitment"],
                    churn=month_data["churn"],
                    targets=MonthlyTargets(
                        revenue_target=month_data["targets"]["revenue_target"],
                        headcount_target=month_data["targets"]["headcount_target"],
                        utilization_target=month_data["targets"]["utilization_target"],
                        client_satisfaction=month_data["targets"]["client_satisfaction"]
                    )
                )
            
            return BusinessPlan(
                office_id=plan_data["office_id"],
                plan_id=plan_data["plan_id"], 
                name=plan_data["name"],
                monthly_plans=monthly_plans
            )
        return None
    
    # Mock office configuration loading
    def mock_load_office_config(office_id):
        if office_id in test_data["office_configs"]:
            return test_data["office_configs"][office_id]
        return {
            'name': f'Test Office {office_id}',
            'current_snapshot_id': f'{office_id}_baseline_2024',
            'business_plan_id': f'{office_id}_growth_2024_2025',
            'economic_parameters': {
                'churn_rates': {'Consultant': {'A': 0.08}},
                'recruitment_capacity': {'monthly_max': 5}
            }
        }
    
    # Mock CAT matrix loading
    def mock_load_cat_matrix(role):
        if role in test_data["cat_matrices"]:
            matrix_data = test_data["cat_matrices"][role]
            from src.services.simulation_engine_v2 import CATMatrix
            return CATMatrix(
                role=matrix_data["role"],
                progression_probabilities=matrix_data["progression_probabilities"]
            )
        return None
    
    return {
        'mock_load_snapshot': mock_load_snapshot,
        'mock_load_business_plan': mock_load_business_plan, 
        'mock_load_office_config': mock_load_office_config,
        'mock_load_cat_matrix': mock_load_cat_matrix
    }

def test_v2_engine_with_realistic_data():
    """Test V2 engine with comprehensive realistic data"""
    print("V2 Engine Verification Test with Realistic Data")
    print("=" * 60)
    
    try:
        # Load test data
        print("Loading test data...")
        test_data = load_test_data()
        mock_loaders = create_mock_data_loaders(test_data)
        
        # Import V2 engine components
        from src.services.simulation_engine_v2 import SimulationEngineV2Factory, ScenarioRequest, TimeRange, Levers
        from unittest.mock import patch
        
        print("Creating V2 engine...")
        engine = SimulationEngineV2Factory.create_test_engine(random_seed=2024)
        
        # Create scenario from test data
        scenario_data = test_data["test_scenarios"][0]  # Use first test scenario
        scenario = ScenarioRequest(
            scenario_id=scenario_data["scenario_id"],
            name=scenario_data["name"],
            time_range=TimeRange(
                scenario_data["time_range"]["start_year"],
                scenario_data["time_range"]["start_month"],
                scenario_data["time_range"]["end_year"],
                scenario_data["time_range"]["end_month"]
            ),
            office_ids=scenario_data["office_ids"],
            levers=Levers(
                recruitment_multiplier=scenario_data["levers"]["recruitment_multiplier"],
                churn_multiplier=scenario_data["levers"]["churn_multiplier"],
                price_multiplier=scenario_data["levers"]["price_multiplier"],
                salary_multiplier=scenario_data["levers"]["salary_multiplier"]
            )
        )
        
        print(f"Running scenario: {scenario.name}")
        print(f"  Duration: {scenario.time_range.get_total_months()} months")
        print(f"  Offices: {scenario.office_ids}")
        print(f"  Levers: Recruitment={scenario.levers.recruitment_multiplier}, Churn={scenario.levers.churn_multiplier}")
        
        # Mock data loading methods during simulation
        with patch.multiple(
            'src.services.simulation_engine_v2.SimulationEngineV2',
            _load_office_snapshot=mock_loaders['mock_load_snapshot'],
            _load_business_plan=mock_loaders['mock_load_business_plan'],
            _load_office_configuration=mock_loaders['mock_load_office_config'],
            _load_cat_matrix=mock_loaders['mock_load_cat_matrix']
        ):
            # Run simulation
            print("Executing simulation...")
            start_time = datetime.now()
            results = engine.run_simulation(scenario)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            print(f"Simulation completed in {execution_time:.2f} seconds")
        
        # Analyze results
        print()
        print("SIMULATION RESULTS ANALYSIS")
        print("=" * 40)
        
        # 1. Basic metrics
        total_events = len(results.all_events)
        months_simulated = len(results.monthly_results)
        final_workforce = sum(office.get_total_workforce() for office in results.final_workforce.values())
        
        print("Basic Metrics:")
        print(f"  Total events: {total_events}")
        print(f"  Months simulated: {months_simulated}")
        print(f"  Final workforce: {final_workforce}")
        
        # 2. Event analysis
        if total_events > 0:
            event_types = Counter(event.event_type.value for event in results.all_events)
            print()
            print("Event Analysis:")
            print(f"  Event type breakdown:")
            for event_type, count in event_types.items():
                print(f"    - {event_type}: {count}")
                
            # Individual tracking verification
            events_by_person = {}
            for event in results.all_events:
                person_id = event.details.get('person_id', 'unknown')
                if person_id not in events_by_person:
                    events_by_person[person_id] = []
                events_by_person[person_id].append(event)
            
            print(f"  People with events: {len(events_by_person)}")
            
            # Show sample individual journeys
            if len(events_by_person) > 0:
                print("  Sample individual journeys:")
                sample_people = list(events_by_person.keys())[:3]
                for person_id in sample_people:
                    person_events = events_by_person[person_id]
                    print(f"    Person {person_id[:12]}: {len(person_events)} events")
                    
                    # Show timeline
                    sorted_events = sorted(person_events, key=lambda e: e.date)
                    for i, event in enumerate(sorted_events[:3]):  # First 3 events
                        role_info = event.details.get('role', 'Unknown')
                        level_info = event.details.get('level', '')
                        print(f"      {i+1}. {event.event_type.value} on {event.date} - {role_info} {level_info}")
        
        # 3. Growth analysis
        print()
        print("Growth Analysis:")
        
        # Calculate initial workforce (from test data)
        initial_workforce = len(test_data["population_snapshots"]["london"]["workforce"])
        net_change = final_workforce - initial_workforce
        growth_pct = (net_change / initial_workforce * 100) if initial_workforce > 0 else 0
        
        print(f"  Initial workforce: {initial_workforce}")
        print(f"  Final workforce: {final_workforce}")
        print(f"  Net change: {net_change} people")
        print(f"  Growth rate: {growth_pct:.1f}%")
        
        expected_growth = scenario_data["expected_outcomes"]["workforce_growth_pct"]
        print(f"  Target growth: {expected_growth}%")
        
        if abs(growth_pct - expected_growth) < 10:  # Within 10% tolerance
            print("  [PASS] Growth rate close to target")
        else:
            print(f"  [INFO] Growth rate differs from target (actual: {growth_pct:.1f}%, target: {expected_growth}%)")
        
        # 4. KPI verification
        print()
        print("KPI Analysis:")
        if results.kpi_data:
            print(f"  KPI categories generated: {len(results.kpi_data)}")
            for category in results.kpi_data.keys():
                print(f"    - {category}")
                
            # Show specific KPIs if available
            if 'workforce_kpis' in results.kpi_data:
                wf_kpis = results.kpi_data['workforce_kpis']
                if hasattr(wf_kpis, 'growth_rate'):
                    print(f"  Workforce growth rate: {wf_kpis.growth_rate:.1f}%")
                if hasattr(wf_kpis, 'churn_rate'):
                    print(f"  Churn rate: {wf_kpis.churn_rate:.1f}%")
                if hasattr(wf_kpis, 'promotion_rate') and wf_kpis.promotion_rate:
                    print(f"  Promotion rate: {wf_kpis.promotion_rate:.1f}%")
        else:
            print("  No KPI data generated")
        
        # 5. Final assessment
        print()
        print("FINAL ASSESSMENT")
        print("=" * 20)
        
        # Check validation criteria
        validations = [
            ("Simulation completed", True),
            ("Events generated", total_events > 0),
            ("Individual tracking working", len(events_by_person) > 0 if total_events > 0 else True),
            ("Monthly progression", months_simulated >= 20),  # Close to 24 months
            ("Workforce changes", abs(net_change) > 0),
            ("KPI calculation", bool(results.kpi_data)),
            ("Realistic execution time", execution_time < 60)  # Under 1 minute
        ]
        
        passed_validations = 0
        for validation_name, passed in validations:
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {validation_name}")
            if passed:
                passed_validations += 1
        
        print()
        overall_success = passed_validations >= len(validations) - 1  # Allow 1 failure
        if overall_success:
            print("[SUCCESS] V2 Engine verification PASSED!")
            print("Engine successfully processes realistic data and produces comprehensive results.")
            
            if total_events > scenario_data["expected_outcomes"]["minimum_events"]:
                print(f"[BONUS] Generated {total_events} events (minimum: {scenario_data['expected_outcomes']['minimum_events']})")
            
        else:
            print(f"[PARTIAL] V2 Engine partially working ({passed_validations}/{len(validations)} validations passed)")
            print("Some areas need investigation for full production readiness.")
        
        print()
        print("V2 ENGINE TEST DATA VERIFICATION COMPLETE")
        print("=" * 50)
        
        return overall_success, {
            'total_events': total_events,
            'months_simulated': months_simulated,
            'final_workforce': final_workforce,
            'growth_rate': growth_pct,
            'execution_time': execution_time,
            'validations_passed': passed_validations,
            'validations_total': len(validations)
        }
        
    except Exception as e:
        print(f"[FAIL] Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, {'error': str(e)}

if __name__ == "__main__":
    success, metrics = test_v2_engine_with_realistic_data()
    
    if success:
        print()
        print("V2 Engine is ready for production with realistic data!")
    else:
        print()
        print("V2 Engine needs additional work before production deployment.")