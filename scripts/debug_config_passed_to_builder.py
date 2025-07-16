#!/usr/bin/env python3
"""
Debug script to see the exact configuration being passed to the office builder.
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.src.services.scenario_service import ScenarioService
from backend.src.services.config_service import config_service
from backend.src.services.scenario_models import ScenarioRequest

def debug_config_passed_to_builder(scenario_id):
    """Debug the exact configuration being passed to the office builder."""
    
    print(f"🔍 Debugging Config Passed to Builder for Scenario: {scenario_id}")
    print("=" * 70)
    
    # Initialize services
    scenario_service = ScenarioService(config_service)
    
    # Load the scenario definition
    scenario_path = f"data/scenarios/definitions/{scenario_id}.json"
    
    with open(scenario_path, 'r') as f:
        scenario_data = json.load(f)
    
    print(f"📋 Scenario Name: {scenario_data.get('name', 'Unknown')}")
    
    # Check baseline configuration
    print("\n📊 Baseline Configuration:")
    baseline_config = config_service.get_configuration()
    total_baseline_fte = sum(office.get('total_fte', 0) for office in baseline_config.values())
    print(f"  Total Baseline FTE: {total_baseline_fte}")
    
    # Resolve scenario data to see what config is passed to builder
    print("\n🚀 Resolving scenario data...")
    resolved_data = scenario_service.resolve_scenario(scenario_data)
    
    if 'offices_config' in resolved_data:
        offices_config = resolved_data['offices_config']
        print(f"\n📊 Resolved Offices Config:")
        print(f"  Number of offices: {len(offices_config)}")
        
        for office_name, office_config in offices_config.items():
            print(f"\n  {office_name}:")
            print(f"    Total FTE: {office_config.get('total_fte', 0)}")
            print(f"    Journey: {office_config.get('journey', 'Unknown')}")
            
            # Check each role and level FTE values
            roles = office_config.get('roles', {})
            for role_name, role_data in roles.items():
                if isinstance(role_data, dict):
                    # Leveled role
                    print(f"    {role_name}:")
                    for level_name, level_config in role_data.items():
                        if isinstance(level_config, dict):
                            fte = level_config.get('fte', 0)
                            print(f"      {level_name}: {fte} FTE")
                            
                            # Check if recruitment_abs_1 is set
                            recruitment_abs_1 = level_config.get('recruitment_abs_1', None)
                            churn_abs_1 = level_config.get('churn_abs_1', None)
                            if recruitment_abs_1 is not None:
                                print(f"        recruitment_abs_1: {recruitment_abs_1}")
                            if churn_abs_1 is not None:
                                print(f"        churn_abs_1: {churn_abs_1}")
                else:
                    # Flat role
                    fte = role_data.get('fte', 0)
                    print(f"    {role_name}: {fte} FTE")
    
    # Now check what the office builder actually creates
    print("\n🚀 Building offices from resolved config...")
    from backend.src.services.office_builder import OfficeBuilder
    from backend.src.services.scenario_resolver import ScenarioResolver
    
    office_builder = OfficeBuilder()
    scenario_resolver = ScenarioResolver(config_service)
    
    # Get the resolved config
    resolved_data = scenario_resolver.resolve_scenario(scenario_data)
    offices_config = resolved_data['offices_config']
    
    # Build offices
    offices = office_builder.build_offices_from_config(offices_config, {})
    
    print(f"\n📊 Built Offices:")
    print(f"  Number of offices: {len(offices)}")
    
    for office_name, office in offices.items():
        print(f"\n  {office_name}:")
        print(f"    Total FTE: {office.total_fte}")
        print(f"    Journey: {office.journey.value}")
        
        # Check each role and level
        for role_name, role_data in office.roles.items():
            if isinstance(role_data, dict):
                # Leveled role
                print(f"    {role_name}:")
                for level_name, level in role_data.items():
                    print(f"      {level_name}:")
                    print(f"        FTE field: {getattr(level, 'fte', 'NOT FOUND')}")
                    print(f"        Total property: {level.total}")
                    print(f"        People count: {len(level.people)}")
            else:
                # Flat role
                print(f"    {role_name}:")
                print(f"      FTE field: {getattr(role_data, 'fte', 'NOT FOUND')}")
                print(f"      Total property: {role_data.total}")
                print(f"      People count: {len(role_data.people)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 debug_config_passed_to_builder.py <scenario_id>")
        sys.exit(1)
    
    scenario_id = sys.argv[1]
    debug_config_passed_to_builder(scenario_id) 