#!/usr/bin/env python3
"""
Debug test to trace simulation engine input and identify the total_fte error.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.config_service import ConfigService
from src.services.scenario_resolver import ScenarioResolver
from src.services.office_builder import OfficeBuilder
from src.services.simulation_engine import SimulationEngine
import json

def test_debug_simulation():
    """Debug test to trace simulation engine input."""
    print("🔍 Debug test for simulation engine...")
    
    # Initialize services
    config_service = ConfigService()
    scenario_resolver = ScenarioResolver(config_service)
    office_builder = OfficeBuilder()
    engine = SimulationEngine()
    
    # Load scenario data
    scenario_file = "../data/scenarios/definitions/f5f26bc5-3830-4f64-ba53-03b58ae72353.json"
    with open(scenario_file, 'r') as f:
        scenario_data = json.load(f)
    
    print(f"📄 Loaded scenario: {scenario_data.get('name', 'Unknown')}")
    
    # Resolve scenario
    resolved_data = scenario_resolver.resolve_scenario(scenario_data)
    offices_config = resolved_data['offices_config']
    progression_config = resolved_data['progression_config']
    cat_curves = resolved_data['cat_curves']
    
    print(f"📊 Resolved config total FTE: {sum(office.get('total_fte', 0) for office in offices_config.values())}")
    
    # Build Office objects
    print(f"🔄 Building Office objects...")
    offices = office_builder.build_offices_from_config(offices_config, progression_config)
    
    print(f"✅ Created {len(offices)} Office objects")
    
    # Debug: Check what we're passing to the simulation engine
    print(f"\n🔍 Debug: Checking simulation engine input...")
    print(f"📊 Offices type: {type(offices)}")
    print(f"📊 Offices keys: {list(offices.keys())}")
    
    # Check each office
    for office_name, office in offices.items():
        print(f"  📍 {office_name}: type={type(office)}, has total_fte={hasattr(office, 'total_fte')}")
        if hasattr(office, 'total_fte'):
            print(f"      total_fte={office.total_fte}")
        else:
            print(f"      ❌ ERROR: {office_name} is not a proper Office object!")
            print(f"      Object: {office}")
            return False
    
    print(f"📊 Progression config type: {type(progression_config)}")
    print(f"📊 CAT curves type: {type(cat_curves)}")
    
    # Try to call the simulation engine
    print(f"\n🚀 Attempting to call simulation engine...")
    try:
        results = engine.run_simulation_with_offices(
            start_year=2025,
            start_month=1,
            end_year=2027,
            end_month=12,
            offices=offices,
            progression_config=progression_config,
            cat_curves=cat_curves,
            economic_params=None
        )
        print(f"✅ Simulation completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Simulation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_debug_simulation() 