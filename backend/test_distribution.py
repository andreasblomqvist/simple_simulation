#!/usr/bin/env python3
"""
Test script to verify proportional distribution of recruitment by office size.
"""

import json
import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from src.services.config_service import config_service
from src.services.scenario_service import ScenarioService

def test_proportional_distribution():
    """Test that recruitment is distributed proportionally by office size."""
    print("🔍 Testing Proportional Distribution")
    print("=" * 50)
    
    # Load scenario file
    scenario_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data", "scenarios", "definitions", "f5f26bc5-3830-4f64-ba53-03b58ae72353.json"
    )
    
    with open(scenario_file, 'r') as f:
        scenario_data = json.load(f)
    
    # Create scenario service
    scenario_service = ScenarioService(config_service)
    
    # Resolve scenario
    resolved_data = scenario_service.resolve_scenario(scenario_data)
    offices_config = resolved_data.get('offices_config', {})
    
    # Get base config for comparison
    base_config = config_service.get_config()
    
    print("📊 Office Size Distribution:")
    print("-" * 30)
    
    total_fte = sum(office.get('total_fte', 0) for office in base_config.values())
    
    for office_name, office_config in base_config.items():
        office_fte = office_config.get('total_fte', 0)
        distribution_factor = office_fte / total_fte if total_fte > 0 else 0
        print(f"{office_name}: {office_fte:.0f} FTE ({distribution_factor:.3f} = {distribution_factor*100:.1f}%)")
    
    print(f"\n📊 Total FTE: {total_fte}")
    
    # Check recruitment distribution for A-level consultants
    print("\n🎯 A-Level Consultant Recruitment Distribution (Month 1):")
    print("-" * 60)
    
    global_a_recruitment = scenario_data['baseline_input']['global']['recruitment']['Consultant']['A']['202501']
    print(f"Global A-level recruitment (Month 1): {global_a_recruitment}")
    
    for office_name, office_config in offices_config.items():
        base_office = base_config[office_name]
        office_fte = base_office.get('total_fte', 0)
        distribution_factor = office_fte / total_fte if total_fte > 0 else 0
        
        # Get the distributed recruitment value
        distributed_recruitment = office_config['roles']['Consultant']['A'].get('recruitment_1', 0)
        expected_recruitment = global_a_recruitment * distribution_factor
        
        print(f"{office_name}: {distributed_recruitment:.3f} (expected: {expected_recruitment:.3f})")

if __name__ == "__main__":
    test_proportional_distribution() 