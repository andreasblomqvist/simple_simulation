"""
High Volume Progression Test

Run multiple simulations or add many people to verify progression events occur
when we have sufficient volume to overcome probability randomness.
"""

import sys
from pathlib import Path
from datetime import date
from collections import Counter

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_progression_with_volume():
    """Test progression with many people to overcome randomness"""
    print("HIGH VOLUME PROGRESSION TEST")
    print("=" * 35)
    
    try:
        from src.services.simulation_engine_v2 import (
            SimulationEngineV2Factory, ScenarioRequest, TimeRange, Levers, Person
        )
        
        print("1. Creating engine with many test people...")
        engine = SimulationEngineV2Factory.create_test_engine(random_seed=42)
        
        scenario = ScenarioRequest(
            scenario_id="volume_progression_test",
            name="Volume Progression Test", 
            time_range=TimeRange(2024, 1, 2024, 6),  # Jan to June
            office_ids=["london"],
            levers=Levers(recruitment_multiplier=0.0, churn_multiplier=0.0)  # Focus only on progression
        )
        
        # Initialize offices
        engine._load_and_initialize_offices(scenario)
        london_office = engine.office_states["london"]
        
        print(f"2. CAT matrices loaded: {len(london_office.cat_matrices)} roles")
        
        # Create many people with high tenure to increase chance of seeing promotions
        print("3. Adding many high-tenure people...")
        
        many_people = []
        
        # Add 50 consultants at level A with high tenure
        for i in range(50):
            person = Person(
                id=f"consultant_{i:03d}",
                current_role="Consultant",
                current_level="A", 
                current_office="london",
                hire_date=date(2022, 6, 1),  # 19 months tenure by Jan 2024
                current_level_start=date(2022, 6, 1),
                is_active=True
            )
            many_people.append(person)
            london_office.add_person(person)
        
        # Add 30 sales people at level A with high tenure
        for i in range(30):
            person = Person(
                id=f"sales_{i:03d}",
                current_role="Sales",
                current_level="A",
                current_office="london",
                hire_date=date(2022, 5, 1),  # 20 months tenure by Jan 2024
                current_level_start=date(2022, 5, 1),
                is_active=True
            )
            many_people.append(person)
            london_office.add_person(person)
        
        # Add 20 recruitment people at level A with high tenure  
        for i in range(20):
            person = Person(
                id=f"recruitment_{i:03d}",
                current_role="Recruitment",
                current_level="A",
                current_office="london",
                hire_date=date(2022, 4, 1),  # 21 months tenure by Jan 2024
                current_level_start=date(2022, 4, 1),
                is_active=True
            )
            many_people.append(person)
            london_office.add_person(person)
        
        total_people = len(many_people)
        print(f"   Added {total_people} people (50 consultants, 30 sales, 20 recruitment)")
        
        # Calculate expected promotions
        consultant_prob = 0.17  # 15% to AC + 2% to C
        sales_prob = 0.21      # 18% to AC + 3% to C  
        recruitment_prob = 0.24 # 20% to AC + 4% to C
        
        expected_consultant_promotions = 50 * consultant_prob
        expected_sales_promotions = 30 * sales_prob
        expected_recruitment_promotions = 20 * recruitment_prob
        total_expected = expected_consultant_promotions + expected_sales_promotions + expected_recruitment_promotions
        
        print(f"   Expected promotions: ~{total_expected:.1f} total")
        print(f"     - Consultants: ~{expected_consultant_promotions:.1f}")
        print(f"     - Sales: ~{expected_sales_promotions:.1f}")
        print(f"     - Recruitment: ~{expected_recruitment_promotions:.1f}")
        
        # Run simulation
        print("4. Running simulation...")
        results = engine.run_simulation(scenario)
        
        print(f"   Total events: {len(results.all_events)}")
        
        # Analyze events
        if results.all_events:
            event_types = Counter(event.event_type.value for event in results.all_events)
            print("5. Event Analysis:")
            for event_type, count in event_types.items():
                print(f"   {event_type}: {count}")
            
            # Focus on promotions
            promotion_events = [e for e in results.all_events if e.event_type.value == 'promoted']
            print(f"\n   PROMOTION EVENTS: {len(promotion_events)}")
            
            if promotion_events:
                print("   SUCCESS! Promotions are working!")
                
                # Analyze by role
                promotions_by_role = Counter(e.details.get('role') for e in promotion_events)
                print("   Promotions by role:")
                for role, count in promotions_by_role.items():
                    print(f"     - {role}: {count}")
                
                # Analyze by promotion path
                promotion_paths = Counter(f"{e.details.get('from_level')}→{e.details.get('to_level')}" for e in promotion_events)
                print("   Promotion paths:")
                for path, count in promotion_paths.items():
                    print(f"     - {path}: {count}")
                
                # Check months
                promotion_months = [e.date.month for e in promotion_events]
                months_with_promotions = Counter(promotion_months)
                print("   Promotions by month:")
                for month, count in sorted(months_with_promotions.items()):
                    print(f"     - Month {month}: {count}")
                
                success = True
                
            else:
                print("   Still no promotions with {total_people} people!")
                print("   This suggests there may still be an issue.")
                success = False
        else:
            print("   No events generated at all!")
            success = False
        
        return success, {
            'total_people': total_people,
            'total_events': len(results.all_events) if results.all_events else 0,
            'promotion_events': len(promotion_events) if 'promotion_events' in locals() else 0,
            'expected_promotions': total_expected
        }
        
    except Exception as e:
        print(f"[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, {'error': str(e)}

if __name__ == "__main__":
    print("Testing progression with high volume...")
    success, metrics = test_progression_with_volume()
    
    if success:
        actual = metrics.get('promotion_events', 0)
        expected = metrics.get('expected_promotions', 0)
        print(f"\n[SUCCESS] Got {actual} promotions (expected ~{expected:.1f})")
        print("Progression functionality is confirmed working!")
    else:
        print(f"\n[ISSUE] No promotions with {metrics.get('total_people', 0)} people")
        if 'error' in metrics:
            print(f"Error: {metrics['error']}")
        else:
            print("May need further debugging")