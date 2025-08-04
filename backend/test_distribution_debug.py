#!/usr/bin/env python3
"""
Debug script to see the actual structure of resolved scenario data.
"""

import json
import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from src.services.config_service import config_service
from src.services.scenario_service import ScenarioService

def debug_resolved_structure():
    """Debug the structure of resolved scenario data."""
    print("🔍 Debugging Resolved Scenario Structure")
    print("=" * 50)
    
    # Load scenario file
    scenario_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data", "scenarios", "definitions", "f5f26bc5-3830-4f64-ba53-03b58ae72353.json"
    )
    
    with open(scenario_file, 'r') as f:
        scenario_data = json.load(f)
    
    # Resolve scenario
    scenario_service = ScenarioService(config_service)
    resolved_data = scenario_service.resolve_scenario(scenario_data)
    
    print("📊 Resolved data keys:", list(resolved_data.keys()))
    
    offices_config = resolved_data.get('offices_config', {})
    print(f"📊 Number of offices in config: {len(offices_config)}")
    
    # Check first office structure
    if offices_config:
        first_office_name = list(offices_config.keys())[0]
        first_office = offices_config[first_office_name]
        print(f"\n🏢 First office: {first_office_name}")
        print(f"📊 Office keys: {list(first_office.keys())}")
        
        if 'roles' in first_office:
            roles = first_office['roles']
            print(f"📊 Roles: {list(roles.keys())}")
            
            if 'Consultant' in roles:
                consultant_role = roles['Consultant']
                print(f"📊 Consultant levels: {list(consultant_role.keys())}")
                
                if 'A' in consultant_role:
                    level_a = consultant_role['A']
                    print(f"📊 Level A keys: {list(level_a.keys())}")
                    
                    # Check for recruitment fields
                    recruitment_fields = [k for k in level_a.keys() if k.startswith('recruitment')]
                    churn_fields = [k for k in level_a.keys() if k.startswith('churn')]
                    
                    print(f"📊 Recruitment fields: {recruitment_fields}")
                    print(f"📊 Churn fields: {churn_fields}")
                    
                    # Show some actual values
                    for month in range(1, 4):  # Just first 3 months
                        rec_field = f'recruitment_abs_{month}'
                        churn_field = f'churn_abs_{month}'
                        if rec_field in level_a:
                            print(f"📊 {rec_field}: {level_a[rec_field]}")
                        if churn_field in level_a:
                            print(f"📊 {churn_field}: {level_a[churn_field]}")

if __name__ == "__main__":
    debug_resolved_structure() 