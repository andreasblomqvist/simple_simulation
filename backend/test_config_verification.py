#!/usr/bin/env python3
"""
Test script to verify configuration loading and FTE calculations.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.config_service import ConfigService

def test_config_loading():
    """Test configuration loading and FTE calculation."""
    print("🔍 Testing configuration loading...")
    
    # Initialize config service
    config_service = ConfigService()
    
    # Get configuration
    config = config_service.get_config()
    
    print(f"📊 Loaded {len(config)} offices from configuration")
    
    # Calculate total FTE
    total_fte = 0
    office_breakdown = {}
    
    for office_name, office_config in config.items():
        office_fte = office_config.get('total_fte', 0)
        total_fte += office_fte
        office_breakdown[office_name] = office_fte
        print(f"  📍 {office_name}: {office_fte} FTE")
    
    print(f"\n📊 Total FTE across all offices: {total_fte}")
    print(f"📊 Expected total FTE: 1972")
    print(f"📊 Difference: {total_fte - 1972}")
    
    # Check if there's a discrepancy
    if total_fte != 1972:
        print(f"⚠️  WARNING: Configuration total FTE ({total_fte}) doesn't match expected (1972)")
    else:
        print(f"✅ Configuration total FTE matches expected value")
    
    return config, total_fte, office_breakdown

if __name__ == "__main__":
    test_config_loading() 