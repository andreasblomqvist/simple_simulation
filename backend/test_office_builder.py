#!/usr/bin/env python3
"""
Test script to verify office builder functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.config_service import ConfigService
from src.services.scenario_resolver import ScenarioResolver
from src.services.office_builder import OfficeBuilder
import json

def test_office_builder():
    """Test office builder functionality."""
    print("🔍 Testing office builder...")
    
    # Initialize services
    config_service = ConfigService()
    scenario_resolver = ScenarioResolver(config_service)
    office_builder = OfficeBuilder()
    
    # Load scenario data
    scenario_file = "../data/scenarios/definitions/f5f26bc5-3830-4f64-ba53-03b58ae72353.json"
    with open(scenario_file, 'r') as f:
        scenario_data = json.load(f)
    
    print(f"📄 Loaded scenario: {scenario_data.get('name', 'Unknown')}")
    
    # Resolve scenario
    resolved_data = scenario_resolver.resolve_scenario(scenario_data)
    offices_config = resolved_data['offices_config']
    progression_config = resolved_data['progression_config']
    
    print(f"📊 Resolved config total FTE: {sum(office.get('total_fte', 0) for office in offices_config.values())}")
    
    # Build Office objects
    print(f"🔄 Building Office objects...")
    offices = office_builder.build_offices_from_config(offices_config, progression_config)
    
    print(f"✅ Created {len(offices)} Office objects")
    
    # Verify Office objects
    total_fte = 0
    for office_name, office in offices.items():
        print(f"  📍 {office_name}: {office.total_fte} FTE")
        total_fte += office.total_fte
        
        # Check that it's a proper Office object
        if not hasattr(office, 'total_fte'):
            print(f"❌ ERROR: {office_name} is not a proper Office object!")
            return False
        
        # Check roles
        for role_name, role_data in office.roles.items():
            if isinstance(role_data, dict):
                # Leveled role
                for level_name, level in role_data.items():
                    if not hasattr(level, 'total'):
                        print(f"❌ ERROR: {office_name}.{role_name}.{level_name} is not a proper Level object!")
                        return False
            else:
                # Flat role
                if not hasattr(role_data, 'total'):
                    print(f"❌ ERROR: {office_name}.{role_name} is not a proper RoleData object!")
                    return False
    
    print(f"\n📊 Total FTE in Office objects: {total_fte}")
    print(f"📊 Expected total FTE: 1972")
    
    if total_fte == 1972:
        print(f"✅ Office builder working correctly!")
        return True
    else:
        print(f"❌ ERROR: Total FTE mismatch! Expected 1972, got {total_fte}")
        return False

if __name__ == "__main__":
    test_office_builder() 