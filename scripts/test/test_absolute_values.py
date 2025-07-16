#!/usr/bin/env python3
"""
Test script to verify the simulation engine works with absolute recruitment and churn values.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend/src')))

from services.simulation.workforce import get_effective_recruitment_value, get_effective_churn_value

def test_absolute_values():
    """Test that the workforce functions work correctly with absolute values."""
    
    class TestObject:
        def __init__(self):
            # Set absolute values for month 1
            self.recruitment_abs_1 = 5
            self.churn_abs_1 = 2
            
            # Set absolute values for month 6
            self.recruitment_abs_6 = 10
            self.churn_abs_6 = 3
    
    print("Testing absolute recruitment and churn values...")
    
    # Create test object
    obj = TestObject()
    
    # Test recruitment values
    recruitment_1 = get_effective_recruitment_value(obj, 1)
    recruitment_6 = get_effective_recruitment_value(obj, 6)
    recruitment_12 = get_effective_recruitment_value(obj, 12)  # Should be 0 (not set)
    
    print(f"Month 1 recruitment: {recruitment_1} (expected: 5)")
    print(f"Month 6 recruitment: {recruitment_6} (expected: 10)")
    print(f"Month 12 recruitment: {recruitment_12} (expected: 0)")
    
    # Test churn values
    churn_1 = get_effective_churn_value(obj, 1)
    churn_6 = get_effective_churn_value(obj, 6)
    churn_12 = get_effective_churn_value(obj, 12)  # Should be 0 (not set)
    
    print(f"Month 1 churn: {churn_1} (expected: 2)")
    print(f"Month 6 churn: {churn_6} (expected: 3)")
    print(f"Month 12 churn: {churn_12} (expected: 0)")
    
    # Verify results
    assert recruitment_1 == 5, f"Expected 5, got {recruitment_1}"
    assert recruitment_6 == 10, f"Expected 10, got {recruitment_6}"
    assert recruitment_12 == 0, f"Expected 0, got {recruitment_12}"
    
    assert churn_1 == 2, f"Expected 2, got {churn_1}"
    assert churn_6 == 3, f"Expected 3, got {churn_6}"
    assert churn_12 == 0, f"Expected 0, got {churn_12}"
    
    print("✅ All tests passed! Absolute recruitment and churn values work correctly.")
    
    # Test net growth calculation
    net_growth_1 = recruitment_1 - churn_1
    net_growth_6 = recruitment_6 - churn_6
    
    print(f"Month 1 net growth: {net_growth_1} (5 - 2 = 3)")
    print(f"Month 6 net growth: {net_growth_6} (10 - 3 = 7)")
    
    assert net_growth_1 == 3, f"Expected 3, got {net_growth_1}"
    assert net_growth_6 == 7, f"Expected 7, got {net_growth_6}"
    
    print("✅ Net growth calculations work correctly!")

if __name__ == "__main__":
    test_absolute_values() 