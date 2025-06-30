#!/usr/bin/env python3
"""
Debug script to test promotion logic and identify where people are being lost
"""

import sys
sys.path.append('.')
from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.config_service import ConfigService

def debug_progression_issue():
    """Debug the promotion logic to find where people are being lost"""
    
    print("🔍 PROGRESSION LOGIC DEBUG")
    print("=" * 50)
    
    # Run a short simulation with detailed logging
    engine = SimulationEngine()
    
    # Get initial state
    config_service = ConfigService()
    config = config_service.get_configuration()
    starting_fte = sum(office.get('total_fte', 0) for office in config.values())
    print(f"📊 Starting FTE: {starting_fte}")
    
    # Run simulation for just 1 year to see what happens
    results = engine.run_simulation(2025, 1, 2025, 12)
    
    # Check final state
    final_fte = sum(office.total_fte for office in engine.offices.values())
    print(f"📊 Final FTE: {final_fte}")
    print(f"📊 Net change: {final_fte - starting_fte}")
    
    # Check each office
    print("\n📋 Office breakdown:")
    for office_name, office in engine.offices.items():
        print(f"  {office_name}: {office.total_fte}")
        
        # Check each role
        for role_name, role_data in office.roles.items():
            if isinstance(role_data, dict):  # Leveled roles
                role_total = sum(level.total for level in role_data.values())
                print(f"    {role_name}: {role_total}")
                for level_name, level in role_data.items():
                    print(f"      {level_name}: {level.total}")
            else:  # Flat roles
                print(f"    {role_name}: {role_data.total}")
    
    # Check event log
    print("\n📋 Event log summary:")
    event_logger = engine.workforce_manager.get_event_logger()
    if event_logger:
        events = event_logger.get_all_events()
        recruitment_count = len([e for e in events if e.event_type.value == 'recruitment'])
        churn_count = len([e for e in events if e.event_type.value == 'churn'])
        promotion_count = len([e for e in events if e.event_type.value == 'promotion'])
        
        print(f"  Recruitments: {recruitment_count}")
        print(f"  Churn: {churn_count}")
        print(f"  Promotions: {promotion_count}")
        
        # Check if promotions are being logged correctly
        if promotion_count > 0:
            print(f"  Promotion details:")
            for event in events:
                if event.event_type.value == 'promotion':
                    print(f"    {event.date}: {event.from_level} -> {event.to_level} ({event.office})")
    
    # Calculate expected FTE
    expected_fte = starting_fte + recruitment_count - churn_count
    print(f"\n📊 Expected FTE (start + recruits - churn): {expected_fte}")
    print(f"📊 Actual FTE: {final_fte}")
    print(f"📊 Discrepancy: {final_fte - expected_fte}")
    
    if final_fte != expected_fte:
        print(f"\n❌ PEOPLE ARE BEING LOST!")
        print(f"   The discrepancy of {expected_fte - final_fte} people suggests:")
        print(f"   1. People are being removed during promotions but not logged")
        print(f"   2. People are being lost in the promotion transfer logic")
        print(f"   3. There's a bug in the workforce management code")

if __name__ == "__main__":
    debug_progression_issue() 