#!/usr/bin/env python3
"""
Simple test to validate V2 engine components are working
"""

import sys
import os
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_imports():
    """Test that all V2 components can be imported"""
    print("Testing V2 component imports...")
    
    try:
        from backend.src.services.simulation_engine_v2 import (
            SimulationEngineV2Factory, ScenarioRequest, TimeRange, Levers
        )
        print("✅ Core engine imports successful")
        
        from backend.src.services.workforce_manager_v2 import WorkforceManagerV2
        print("✅ Workforce manager import successful")
        
        from backend.src.services.business_plan_processor_v2 import BusinessPlanProcessorV2
        print("✅ Business plan processor import successful")
        
        from backend.src.services.growth_model_manager_v2 import GrowthModelManagerV2
        print("✅ Growth model manager import successful")
        
        from backend.src.services.snapshot_loader_v2 import SnapshotLoaderV2
        print("✅ Snapshot loader import successful")
        
        from backend.src.services.kpi_calculator_v2 import KPICalculatorV2
        print("✅ KPI calculator import successful")
        
        print("✅ All V2 component imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        return False

def test_engine_creation():
    """Test that engines can be created"""
    print("\nTesting engine creation...")
    
    try:
        from backend.src.services.simulation_engine_v2 import SimulationEngineV2Factory
        
        # Test engine creation
        engine = SimulationEngineV2Factory.create_test_engine(random_seed=42)
        print("✅ Test engine created successfully")
        
        # Test initialization
        if engine.initialize():
            print("✅ Engine initialized successfully")
        else:
            print("❌ Engine initialization failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Engine creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_scenario():
    """Test basic scenario creation"""
    print("\nTesting basic scenario...")
    
    try:
        from backend.src.services.simulation_engine_v2 import (
            ScenarioRequest, TimeRange, Levers
        )
        
        # Create scenario
        scenario = ScenarioRequest(
            scenario_id="simple_test",
            name="Simple Test Scenario", 
            time_range=TimeRange(2024, 1, 2024, 6),
            office_ids=["test_office"],
            levers=Levers()
        )
        
        print(f"✅ Scenario created: {scenario.name}")
        print(f"   Time range: {scenario.time_range.get_total_months()} months")
        print(f"   Offices: {len(scenario.office_ids)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Scenario creation failed: {str(e)}")
        return False

def main():
    """Run simple validation tests"""
    print("🚀 SimpleSim Engine V2 - Simple Validation Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_engine_creation, 
        test_basic_scenario
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print("⚠️ Stopping tests due to failure")
            break
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All validation tests passed! V2 engine is working.")
        return True
    else:
        print("❌ Some tests failed. Check the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)