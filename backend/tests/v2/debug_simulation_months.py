"""
Debug Simulation Months

Check what months the simulation processes and when progression should occur.
"""

import sys
from pathlib import Path
from datetime import date

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def debug_simulation_months():
    """Check what months simulation processes"""
    print("DEBUG SIMULATION MONTHS")
    print("=" * 25)
    
    try:
        from src.services.simulation_engine_v2 import (
            SimulationEngineV2Factory, ScenarioRequest, TimeRange, Levers, Person
        )
        
        # Create basic scenario
        scenario = ScenarioRequest(
            scenario_id="debug_months",
            name="Debug Months",
            time_range=TimeRange(2024, 1, 2024, 6),  # Jan to June
            office_ids=["london"],
            levers=Levers(recruitment_multiplier=0.0, churn_multiplier=0.0)
        )
        
        print("1. Time range analysis:")
        print(f"   Start: {scenario.time_range.start_year}-{scenario.time_range.start_month}")
        print(f"   End: {scenario.time_range.end_year}-{scenario.time_range.end_month}")
        print(f"   Total months: {scenario.time_range.get_total_months()}")
        
        # Get month list
        month_list = scenario.time_range.get_month_list()
        print(f"   Month list: {month_list}")
        
        # Check which months are progression months
        progression_months = [6, 12]
        print(f"   Progression months: {progression_months}")
        
        months_with_progression = []
        for year, month in month_list:
            if month in progression_months:
                months_with_progression.append((year, month))
        
        print(f"   Simulation months that have progression: {months_with_progression}")
        
        if not months_with_progression:
            print("   WARNING: No progression months in simulation time range!")
            print("   This explains why no promotions occur.")
            return False
        
        # Create engine and test person
        print()
        print("2. Testing progression in month 6 specifically...")
        
        engine = SimulationEngineV2Factory.create_test_engine(random_seed=42)
        engine._load_and_initialize_offices(scenario)
        london_office = engine.office_states["london"]
        
        # Add test person
        test_person = Person(
            id="debug_person",
            current_role="Consultant",
            current_level="A",
            current_office="london", 
            hire_date=date(2022, 6, 1),  # High tenure
            current_level_start=date(2022, 6, 1),
            is_active=True
        )
        london_office.add_person(test_person)
        
        # Manually test progression for June 2024
        june_2024 = date(2024, 6, 15)
        print(f"   Test date: {june_2024} (month {june_2024.month})")
        
        role_cat_matrix = london_office.cat_matrices.get("Consultant")
        if role_cat_matrix and engine.workforce_manager:
            # Test progression directly
            people = [test_person]
            progression_events = engine.workforce_manager.process_progression(
                people, role_cat_matrix, june_2024
            )
            
            print(f"   Direct progression test result: {len(progression_events)} events")
            if progression_events:
                for event in progression_events:
                    print(f"     - {event.details}")
            else:
                print("     No events from direct test either")
                
                # Check progression requirements step by step
                print("     Checking progression requirements:")
                print(f"       Month {june_2024.month} in progression months: {june_2024.month in [6, 12]}")
                
                tenure = test_person.get_level_tenure_months(june_2024)
                print(f"       Person tenure: {tenure} months (min required: 6)")
                print(f"       Meets tenure requirement: {tenure >= 6}")
                
                probability = engine.workforce_manager.calculate_cat_probability(test_person, role_cat_matrix, june_2024)
                print(f"       Progression probability: {probability}")
                
                should_progress = engine.workforce_manager._should_person_progress(test_person, "A", role_cat_matrix, june_2024)
                print(f"       Should progress (random): {should_progress}")
        else:
            print("   Missing CAT matrix or workforce manager")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Debug failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_simulation_months()