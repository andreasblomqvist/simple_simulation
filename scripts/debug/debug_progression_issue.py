#!/usr/bin/env python3
"""
Debug script to investigate progression logic issues.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.config_service import ConfigService

def debug_progression_issue():
    """Debug the progression logic issue"""
    print("🔍 Debugging progression logic issue...")
    
    # Initialize services
    config_service = ConfigService()
    engine = SimulationEngine(config_service)
    
    # Check if offices are initialized
    print(f"📊 Number of offices: {len(engine.offices)}")
    
    # Check each office and its levels
    total_people = 0
    for office_name, office in engine.offices.items():
        print(f"\n🏢 Office: {office_name}")
        print(f"   Total FTE: {office.total_fte}")
        
        for role_name, role_data in office.roles.items():
            if isinstance(role_data, dict):  # Leveled roles
                print(f"   📋 Role: {role_name} (leveled)")
                for level_name, level in role_data.items():
                    people_count = len(level.people)
                    total_people += people_count
                    print(f"     - {level_name}: {people_count} people")
                    
                    # Check progression rates
                    progression_1 = getattr(level, 'progression_1', 0.0)
                    progression_6 = getattr(level, 'progression_6', 0.0)
                    print(f"       Progression rates: Jan={progression_1:.1%}, Jun={progression_6:.1%}")
                    
                    # Check if people are eligible for progression
                    if people_count > 0:
                        eligible = level.get_eligible_for_progression("2025-01")
                        print(f"       Eligible for progression: {len(eligible)}/{people_count}")
                        
                        # Check CAT categories
                        if len(eligible) > 0:
                            sample_person = eligible[0]
                            cat = sample_person.get_cat_category("2025-01")
                            prob = sample_person.get_progression_probability("2025-01", progression_1, level_name)
                            print(f"       Sample CAT: {cat}, Progression probability: {prob:.1%}")
            else:  # Flat roles
                people_count = len(role_data.people)
                total_people += people_count
                print(f"   📋 Role: {role_name} (flat): {people_count} people")
    
    print(f"\n📊 Total people across all offices: {total_people}")
    
    if total_people == 0:
        print("❌ PROBLEM: No people in any levels! This is why progression isn't working.")
        print("   The levels need to be populated with people during initialization.")
        return False
    
    # Test progression logic directly
    print("\n🧪 Testing progression logic directly...")
    for office_name, office in engine.offices.items():
        for role_name, role_data in office.roles.items():
            if isinstance(role_data, dict):  # Leveled roles
                for level_name, level in role_data.items():
                    if len(level.people) > 0:
                        print(f"   Testing {office_name}.{role_name}.{level_name}")
                        
                        # Test progression
                        progression_rate = getattr(level, 'progression_1', 0.0)
                        if progression_rate > 0:
                            promoted = level.apply_cat_based_progression(progression_rate, "2025-01")
                            print(f"     Applied progression rate {progression_rate:.1%}: {len(promoted)} people promoted")
                        else:
                            print(f"     No progression rate set (rate: {progression_rate:.1%})")
    
    return True

if __name__ == "__main__":
    debug_progression_issue() 