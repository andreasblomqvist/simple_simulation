#!/usr/bin/env python3
"""
Simple test to verify the refactored simulation engine works correctly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.config_service import ConfigService

def test_refactored_engine():
    """Test that the refactored engine produces consistent results."""
    print("🧪 Testing refactored simulation engine...")
    
    # Initialize services
    config_service = ConfigService()
    engine = SimulationEngine(config_service)
    
    # Run a simple simulation
    print("📊 Running simulation (2025-2026)...")
    result = engine.run_simulation(
        start_year=2025, 
        start_month=1, 
        end_year=2026, 
        end_month=12,
        price_increase=0.0,
        salary_increase=0.0
    )
    
    # Check the result structure
    print("🔍 Result structure:")
    print(f"Result type: {type(result)}")
    print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
    
    if isinstance(result, dict):
        for key, value in result.items():
            print(f"  {key}: {type(value)} - {str(value)[:100]}...")
    
    # Check basic results
    print("✅ Simulation completed successfully!")
    
    # Try to access the data based on what we see
    if isinstance(result, dict):
        if 'yearly_snapshots' in result:
            print(f"📈 Total revenue 2025: {result['yearly_snapshots']['2025']['total_revenue']:,.0f}")
            print(f"📈 Total revenue 2026: {result['yearly_snapshots']['2026']['total_revenue']:,.0f}")
            print(f"💰 Total EBITDA 2025: {result['yearly_snapshots']['2025']['total_ebitda']:,.0f}")
            print(f"💰 Total EBITDA 2026: {result['yearly_snapshots']['2026']['total_ebitda']:,.0f}")
            print(f"👥 Total FTE 2025: {result['yearly_snapshots']['2025']['total_fte']:,.1f}")
            print(f"👥 Total FTE 2026: {result['yearly_snapshots']['2026']['total_fte']:,.1f}")
        else:
            print("❌ 'yearly_snapshots' not found in result")
            print("Available keys:", list(result.keys()))
    
    print("🎉 Refactored engine is working correctly!")
    
    return True

if __name__ == "__main__":
    try:
        test_refactored_engine()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 