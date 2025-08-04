#!/usr/bin/env python3
"""
Test script to trace scenario resolution process and identify FTE inflation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.config_service import ConfigService
from src.services.scenario_resolver import ScenarioResolver
import json

def test_scenario_resolution():
    """Test scenario resolution process to trace FTE inflation."""
    print("🔍 Testing scenario resolution process...")
    
    # Initialize services
    config_service = ConfigService()
    scenario_resolver = ScenarioResolver(config_service)
    
    # Load scenario data
    scenario_file = "../data/scenarios/definitions/f5f26bc5-3830-4f64-ba53-03b58ae72353.json"
    with open(scenario_file, 'r') as f:
        scenario_data = json.load(f)
    
    print(f"📄 Loaded scenario: {scenario_data.get('name', 'Unknown')}")
    
    # Get base config
    base_config = config_service.get_config()
    print(f"\n📊 Base config total FTE: {sum(office.get('total_fte', 0) for office in base_config.values())}")
    
    # Resolve scenario
    resolved_data = scenario_resolver.resolve_scenario(scenario_data)
    
    # Check resolved config
    resolved_config = resolved_data['offices_config']
    print(f"📊 Resolved config total FTE: {sum(office.get('total_fte', 0) for office in resolved_config.values())}")
    
    # Compare office by office
    print(f"\n📋 Office-by-office comparison:")
    for office_name in base_config.keys():
        base_fte = base_config[office_name].get('total_fte', 0)
        resolved_fte = resolved_config[office_name].get('total_fte', 0)
        diff = resolved_fte - base_fte
        print(f"  📍 {office_name}: {base_fte} → {resolved_fte} ({diff:+d})")
    
    return resolved_data

if __name__ == "__main__":
    test_scenario_resolution() 