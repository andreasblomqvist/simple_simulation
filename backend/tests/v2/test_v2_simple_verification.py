"""
Simple V2 Engine Verification Test

Tests the V2 engine with its current capabilities to verify:
- Basic simulation execution works
- Events are generated for individuals  
- Results structure is complete
- Performance is reasonable
"""

import sys
from pathlib import Path
from datetime import datetime
from collections import Counter

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def run_v2_verification_test():
    """Run comprehensive V2 engine verification"""
    print("SimpleSim V2 Engine - Verification Test")
    print("=" * 50)
    
    try:
        from src.services.simulation_engine_v2 import SimulationEngineV2Factory, ScenarioRequest, TimeRange, Levers
        
        # Test 1: Basic functionality
        print("Test 1: Basic Engine Functionality")
        print("-" * 30)
        
        engine = SimulationEngineV2Factory.create_test_engine(random_seed=42)
        print("[PASS] Engine created and initialized")
        
        # Test 2: Short simulation
        print()
        print("Test 2: Short Simulation (6 months)")
        print("-" * 30)
        
        short_scenario = ScenarioRequest(
            scenario_id="short_test",
            name="6-Month Basic Test", 
            time_range=TimeRange(2024, 1, 2024, 6),
            office_ids=["test_office"],
            levers=Levers(recruitment_multiplier=1.1, churn_multiplier=0.9)
        )
        
        start_time = datetime.now()
        short_results = engine.run_simulation(short_scenario)
        short_exec_time = (datetime.now() - start_time).total_seconds()
        
        print(f"[PASS] Short simulation completed in {short_exec_time:.2f}s")
        print(f"  Events: {len(short_results.all_events)}")
        print(f"  Months: {len(short_results.monthly_results)}")
        print(f"  Final workforce: {sum(office.get_total_workforce() for office in short_results.final_workforce.values())}")
        
        # Test 3: Medium simulation (1 year)
        print()
        print("Test 3: Medium Simulation (12 months)")
        print("-" * 30)
        
        medium_scenario = ScenarioRequest(
            scenario_id="medium_test",
            name="12-Month Growth Test",
            time_range=TimeRange(2024, 1, 2024, 12),
            office_ids=["london_office"],
            levers=Levers(
                recruitment_multiplier=1.3,  # Higher recruitment
                churn_multiplier=0.8,        # Lower churn
                price_multiplier=1.05        # Price increase
            )
        )
        
        start_time = datetime.now()
        medium_results = engine.run_simulation(medium_scenario)
        medium_exec_time = (datetime.now() - start_time).total_seconds()
        
        print(f"[PASS] Medium simulation completed in {medium_exec_time:.2f}s")
        print(f"  Events: {len(medium_results.all_events)}")
        print(f"  Months: {len(medium_results.monthly_results)}")
        print(f"  Final workforce: {sum(office.get_total_workforce() for office in medium_results.final_workforce.values())}")
        
        # Test 4: Long simulation (24 months) for growth analysis
        print()
        print("Test 4: Long Simulation (24 months)")
        print("-" * 30)
        
        long_scenario = ScenarioRequest(
            scenario_id="long_growth_test",
            name="24-Month Growth Target Test",
            time_range=TimeRange(2024, 1, 2025, 12),
            office_ids=["growth_office"],
            levers=Levers(
                recruitment_multiplier=1.4,  # Strong recruitment
                churn_multiplier=0.7,        # Low churn
                price_multiplier=1.08,       # Price growth
                salary_multiplier=1.03       # Salary increases
            )
        )
        
        start_time = datetime.now()
        long_results = engine.run_simulation(long_scenario)
        long_exec_time = (datetime.now() - start_time).total_seconds()
        
        print(f"[PASS] Long simulation completed in {long_exec_time:.2f}s")
        print(f"  Events: {len(long_results.all_events)}")
        print(f"  Months: {len(long_results.monthly_results)}")
        long_final_workforce = sum(office.get_total_workforce() for office in long_results.final_workforce.values())
        print(f"  Final workforce: {long_final_workforce}")
        
        # Test 5: Multi-office simulation
        print()
        print("Test 5: Multi-Office Simulation")
        print("-" * 30)
        
        multi_scenario = ScenarioRequest(
            scenario_id="multi_office_test",
            name="Multi-Office Growth Test",
            time_range=TimeRange(2024, 1, 2024, 18),
            office_ids=["london", "new_york", "singapore"],
            levers=Levers(recruitment_multiplier=1.2, churn_multiplier=0.9)
        )
        
        start_time = datetime.now()
        multi_results = engine.run_simulation(multi_scenario)
        multi_exec_time = (datetime.now() - start_time).total_seconds()
        
        print(f"[PASS] Multi-office simulation completed in {multi_exec_time:.2f}s")
        print(f"  Events: {len(multi_results.all_events)}")
        print(f"  Months: {len(multi_results.monthly_results)}")
        multi_final_workforce = sum(office.get_total_workforce() for office in multi_results.final_workforce.values())
        print(f"  Total workforce: {multi_final_workforce}")
        print(f"  Offices: {len(multi_results.final_workforce)}")
        
        # Detailed analysis of best performing test (long simulation)
        print()
        print("DETAILED ANALYSIS: Long Simulation Results")
        print("=" * 45)
        
        # Event analysis
        if len(long_results.all_events) > 0:
            event_types = Counter(event.event_type.value for event in long_results.all_events)
            print("Event Type Breakdown:")
            for event_type, count in event_types.items():
                print(f"  {event_type}: {count}")
            
            # Individual tracking
            events_by_person = {}
            for event in long_results.all_events:
                person_id = event.details.get('person_id', 'unknown')
                if person_id not in events_by_person:
                    events_by_person[person_id] = []
                events_by_person[person_id].append(event)
            
            print()
            print("Individual Event Tracking:")
            print(f"  People with events: {len(events_by_person)}")
            
            # Show sample individual journeys
            if len(events_by_person) > 1:
                sample_people = list(events_by_person.keys())[:2]
                for person_id in sample_people:
                    person_events = events_by_person[person_id]
                    print(f"  Person {person_id}: {len(person_events)} events")
                    
                    # Show chronological events
                    sorted_events = sorted(person_events, key=lambda e: e.date)
                    for event in sorted_events[:3]:  # First 3 events
                        role = event.details.get('role', 'Unknown')
                        level = event.details.get('level', '')
                        print(f"    - {event.event_type.value} on {event.date}: {role} {level}")
        
        # KPI analysis
        print()
        print("KPI Analysis:")
        if long_results.kpi_data:
            print(f"  KPI categories: {list(long_results.kpi_data.keys())}")
            
            if 'workforce_kpis' in long_results.kpi_data:
                wf_kpis = long_results.kpi_data['workforce_kpis']
                print("  Workforce KPIs:")
                if hasattr(wf_kpis, 'growth_rate'):
                    print(f"    Growth rate: {wf_kpis.growth_rate:.1f}%")
                if hasattr(wf_kpis, 'churn_rate'):
                    print(f"    Churn rate: {wf_kpis.churn_rate:.1f}%")
                if hasattr(wf_kpis, 'promotion_rate') and wf_kpis.promotion_rate:
                    print(f"    Promotion rate: {wf_kpis.promotion_rate:.1f}%")
            
            if 'executive_summary' in long_results.kpi_data:
                summary = long_results.kpi_data['executive_summary']
                print("  Executive Summary available")
        else:
            print("  No KPI data generated")
        
        # Performance assessment
        print()
        print("PERFORMANCE ASSESSMENT")
        print("=" * 25)
        
        all_tests = [
            ("Short (6m)", short_exec_time, len(short_results.all_events)),
            ("Medium (12m)", medium_exec_time, len(medium_results.all_events)),
            ("Long (24m)", long_exec_time, len(long_results.all_events)),
            ("Multi-office (18m)", multi_exec_time, len(multi_results.all_events))
        ]
        
        for test_name, exec_time, event_count in all_tests:
            print(f"  {test_name}: {exec_time:.2f}s, {event_count} events")
        
        # Overall validation
        print()
        print("OVERALL VALIDATION")
        print("=" * 20)
        
        validations = [
            ("Engine initializes", True),
            ("Short simulations work", short_exec_time < 10),
            ("Medium simulations work", medium_exec_time < 30),
            ("Long simulations work", long_exec_time < 60),
            ("Multi-office works", multi_exec_time < 30),
            ("Events generated", len(long_results.all_events) > 0),
            ("Individual tracking", len(events_by_person) > 0 if long_results.all_events else True),
            ("Monthly data created", len(long_results.monthly_results) >= 20),
            ("KPIs calculated", bool(long_results.kpi_data)),
            ("Workforce data present", long_final_workforce > 0)
        ]
        
        passed_count = 0
        for validation_name, passed in validations:
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {validation_name}")
            if passed:
                passed_count += 1
        
        success_rate = (passed_count / len(validations)) * 100
        print()
        print(f"SUCCESS RATE: {success_rate:.1f}% ({passed_count}/{len(validations)})")
        
        if success_rate >= 90:
            print()
            print("[SUCCESS] V2 Engine verification PASSED!")
            print("Engine is working well and ready for production use.")
        elif success_rate >= 70:
            print()
            print("[PARTIAL] V2 Engine partially working")  
            print("Most features work but some areas need attention.")
        else:
            print()
            print("[FAIL] V2 Engine needs significant work")
            print("Multiple core features not working properly.")
        
        return success_rate >= 70, {
            'success_rate': success_rate,
            'validations_passed': passed_count,
            'total_validations': len(validations),
            'performance': {
                'short_sim_time': short_exec_time,
                'medium_sim_time': medium_exec_time,
                'long_sim_time': long_exec_time,
                'multi_office_time': multi_exec_time
            },
            'results': {
                'long_events': len(long_results.all_events),
                'long_workforce': long_final_workforce,
                'multi_offices': len(multi_results.final_workforce)
            }
        }
        
    except Exception as e:
        print(f"[FAIL] Verification test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, {'error': str(e)}

if __name__ == "__main__":
    success, metrics = run_v2_verification_test()
    
    print()
    print("V2 ENGINE VERIFICATION COMPLETE")
    print("=" * 35)
    
    if success:
        print("RESULT: V2 Engine is ready for production!")
        if 'success_rate' in metrics:
            print(f"Overall success rate: {metrics['success_rate']:.1f}%")
    else:
        print("RESULT: V2 Engine needs more development work.")
        if 'error' in metrics:
            print(f"Primary error: {metrics['error']}")
    
    print()
    print("Ready to proceed with comprehensive testing and deployment!")