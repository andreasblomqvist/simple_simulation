#!/usr/bin/env python3
"""
Debug script to check if recruitment is actually being applied to people lists.
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.src.services.scenario_service import ScenarioService
from backend.src.services.config_service import config_service
from backend.src.services.scenario_models import ScenarioRequest

def debug_recruitment_application(scenario_id):
    """Debug if recruitment is actually being applied to people lists."""
    
    print(f"🔍 Debugging Recruitment Application for Scenario: {scenario_id}")
    print("=" * 70)
    
    # Initialize services
    scenario_service = ScenarioService(config_service)
    
    # Load the scenario definition
    scenario_path = f"data/scenarios/definitions/{scenario_id}.json"
    
    if not os.path.exists(scenario_path):
        print(f"❌ Scenario file not found: {scenario_path}")
        return False
    
    with open(scenario_path, 'r') as f:
        scenario_data = json.load(f)
    
    print(f"📋 Scenario Name: {scenario_data.get('name', 'Unknown')}")
    
    # Create scenario request
    request = ScenarioRequest(scenario_id=scenario_id)
    
    print("\n🚀 Running scenario...")
    
    # Run the scenario
    response = scenario_service.run_scenario(request)
    
    if response.status != "success":
        print(f"❌ Scenario failed: {response.error_message}")
        return False
    
    print(f"✅ Scenario completed successfully")
    
    # Get the simulation engine to inspect the office objects
    try:
        # Access the engine state from the scenario service
        if hasattr(scenario_service, '_engine') and scenario_service._engine:
            engine = scenario_service._engine
            
            print(f"\n🔧 Office State Analysis:")
            print("=" * 70)
            
            for office_name, office in engine.offices.items():
                print(f"\n🏢 {office_name}:")
                
                # Check each role and level
                for role_name, role_data in office.roles.items():
                    if isinstance(role_data, dict):  # Leveled roles
                        print(f"  📊 {role_name}:")
                        for level_name, level in role_data.items():
                            people_count = len(level.people)
                            print(f"    {level_name}: {people_count} people")
                            
                            # Check if there are any people
                            if people_count > 0:
                                # Show some sample people
                                sample_person = level.people[0]
                                print(f"      Sample person: {sample_person.role} {sample_person.current_level} (started {sample_person.career_start})")
                    else:  # Flat roles
                        people_count = len(role_data.people)
                        print(f"  📊 {role_name}: {people_count} people")
                        
                        if people_count > 0:
                            sample_person = role_data.people[0]
                            print(f"    Sample person: {sample_person.role} {sample_person.current_level} (started {sample_person.career_start})")
                
                # Calculate total people
                total_people = 0
                for role_name, role_data in office.roles.items():
                    if isinstance(role_data, dict):
                        for level_name, level in role_data.items():
                            total_people += len(level.people)
                    else:
                        total_people += len(role_data.people)
                
                print(f"  Total people: {total_people}")
                print(f"  Office total_fte: {office.total_fte}")
                
        else:
            print("❌ Could not access simulation engine state")
    except Exception as e:
        print(f"❌ Error accessing engine state: {e}")
    
    print("\n" + "=" * 70)
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 debug_recruitment_application.py <scenario_id>")
        print("Example: python3 debug_recruitment_application.py f5f26bc5-3830-4f64-ba53-03b58ae72353")
        sys.exit(1)
    
    scenario_id = sys.argv[1]
    success = debug_recruitment_application(scenario_id)
    sys.exit(0 if success else 1) 