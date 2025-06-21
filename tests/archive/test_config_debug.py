#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

from backend.src.services.config_service import config_service
from backend.src.services.simulation_engine import SimulationEngine

def test_config_service():
    """Test if configuration service is working correctly"""
    print("🔍 [TEST] Testing configuration service...")
    
    # Check if configuration service has data
    config = config_service.get_configuration()
    print(f"[TEST] Configuration service has {len(config)} offices")
    
    if len(config) > 0:
        print(f"[TEST] Office names: {list(config.keys())}")
        
        # Check first office structure
        first_office_name = list(config.keys())[0]
        first_office = config[first_office_name]
        print(f"[TEST] First office '{first_office_name}' structure:")
        print(f"[TEST]   - total_fte: {first_office.get('total_fte', 'MISSING')}")
        print(f"[TEST]   - journey: {first_office.get('journey', 'MISSING')}")
        print(f"[TEST]   - roles: {list(first_office.get('roles', {}).keys())}")
        
        # Check if Stockholm exists and has data
        if 'Stockholm' in config:
            stockholm = config['Stockholm']
            print(f"[TEST] Stockholm office:")
            print(f"[TEST]   - total_fte: {stockholm.get('total_fte', 'MISSING')}")
            print(f"[TEST]   - roles: {list(stockholm.get('roles', {}).keys())}")
            
            # Check Consultant role
            if 'Consultant' in stockholm.get('roles', {}):
                consultant_levels = list(stockholm['roles']['Consultant'].keys())
                print(f"[TEST]   - Consultant levels: {consultant_levels}")
                
                if 'A' in stockholm['roles']['Consultant']:
                    a_level = stockholm['roles']['Consultant']['A']
                    print(f"[TEST]   - Consultant A FTE: {a_level.get('fte', 'MISSING')}")
    else:
        print("❌ [TEST] Configuration service is empty!")
    
    print("\n🔍 [TEST] Testing simulation engine...")
    
    # Test simulation engine
    engine = SimulationEngine()
    print(f"[TEST] Simulation engine initialized")
    print(f"[TEST] Engine has {len(engine.offices)} offices")
    
    # Test if engine can read from config service
    engine._initialize_offices_from_config_service()
    print(f"[TEST] After initialization: {len(engine.offices)} offices")
    
    if len(engine.offices) > 0:
        print(f"[TEST] Engine office names: {list(engine.offices.keys())}")
        print("✅ [TEST] Configuration service is working correctly!")
    else:
        print("❌ [TEST] Simulation engine cannot read from configuration service!")

if __name__ == "__main__":
    test_config_service() 