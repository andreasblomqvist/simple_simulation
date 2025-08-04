#!/usr/bin/env python3
"""
Test script to debug the Level dataclass fields and verify that recruitment_abs_1 is being set correctly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.src.services.simulation.models import Level, Journey, Month
from dataclasses import fields

def test_level_fields():
    """Test that the Level dataclass has the correct fields."""
    
    # Check what fields the Level dataclass has
    level_fields = [f.name for f in fields(Level)]
    
    print("Level dataclass fields:")
    for field in level_fields:
        print(f"  {field}")
    
    # Check if recruitment fields exist
    recruitment_fields = [f for f in level_fields if 'recruitment' in f]
    churn_fields = [f for f in level_fields if 'churn' in f]
    
    print(f"\nRecruitment fields: {recruitment_fields}")
    print(f"Churn fields: {churn_fields}")
    
    # Check if recruitment_1 exists (it shouldn't)
    has_recruitment_1 = 'recruitment_1' in level_fields
    has_recruitment_abs_1 = 'recruitment_abs_1' in level_fields
    
    print(f"\nHas recruitment_1: {has_recruitment_1}")
    print(f"Has recruitment_abs_1: {has_recruitment_abs_1}")
    
    # Create a Level object and try to set recruitment_abs_1
    level = Level(
        name="A",
        journey=Journey.JOURNEY_1,
        progression_months=[Month(1)],
        price_1=1000.0, price_2=1000.0, price_3=1000.0, price_4=1000.0,
        price_5=1000.0, price_6=1000.0, price_7=1000.0, price_8=1000.0,
        price_9=1000.0, price_10=1000.0, price_11=1000.0, price_12=1000.0,
        salary_1=50000.0, salary_2=50000.0, salary_3=50000.0, salary_4=50000.0,
        salary_5=50000.0, salary_6=50000.0, salary_7=50000.0, salary_8=50000.0,
        salary_9=50000.0, salary_10=50000.0, salary_11=50000.0, salary_12=50000.0,
        utr_1=0.85, utr_2=0.85, utr_3=0.85, utr_4=0.85,
        utr_5=0.85, utr_6=0.85, utr_7=0.85, utr_8=0.85,
        utr_9=0.85, utr_10=0.85, utr_11=0.85, utr_12=0.85
    )
    
    # Try to set recruitment_abs_1
    try:
        setattr(level, 'recruitment_abs_1', 4.0)
        print(f"\n✅ Successfully set recruitment_abs_1 to 4.0")
        print(f"Value: {getattr(level, 'recruitment_abs_1', 'NOT FOUND')}")
    except Exception as e:
        print(f"\n❌ Failed to set recruitment_abs_1: {e}")
    
    # Try to set recruitment_1 (should fail)
    try:
        setattr(level, 'recruitment_1', 0.1)
        print(f"✅ Successfully set recruitment_1 to 0.1")
        print(f"Value: {getattr(level, 'recruitment_1', 'NOT FOUND')}")
    except Exception as e:
        print(f"❌ Failed to set recruitment_1: {e}")
    
    # Check what getattr returns for non-existent fields
    print(f"\nTesting getattr for non-existent fields:")
    print(f"getattr(level, 'recruitment_1', 0.0): {getattr(level, 'recruitment_1', 0.0)}")
    print(f"getattr(level, 'recruitment_abs_1', None): {getattr(level, 'recruitment_abs_1', None)}")

if __name__ == "__main__":
    test_level_fields() 