#!/usr/bin/env python3
"""
Debug script to test tenure calculation and initialization.
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.src.services.simulation.models import Person, Level
from backend.src.services.simulation.office_manager import OfficeManager
from backend.src.services.config_service import config_service

def test_tenure_calculation():
    """Test tenure calculation with realistic initialization"""
    print("🔍 TESTING TENURE CALCULATION")
    print("=" * 50)
    
    # Set random seed for reproducible results
    random.seed(42)
    
    # Create a test level
    level = Level(
        name="C",
        journey="Journey 1",
        progression_months=[1, 7],
        progression_1=0.1, progression_2=0.0, progression_3=0.0, progression_4=0.0,
        progression_5=0.0, progression_6=0.0, progression_7=0.1, progression_8=0.0,
        progression_9=0.0, progression_10=0.0, progression_11=0.0, progression_12=0.0,
        recruitment_1=0.05, recruitment_2=0.0, recruitment_3=0.0, recruitment_4=0.0,
        recruitment_5=0.0, recruitment_6=0.0, recruitment_7=0.05, recruitment_8=0.0,
        recruitment_9=0.0, recruitment_10=0.0, recruitment_11=0.0, recruitment_12=0.0,
        churn_1=0.02, churn_2=0.0, churn_3=0.0, churn_4=0.0,
        churn_5=0.0, churn_6=0.0, churn_7=0.02, churn_8=0.0,
        churn_9=0.0, churn_10=0.0, churn_11=0.0, churn_12=0.0,
        price_1=1400, price_2=1400, price_3=1400, price_4=1400,
        price_5=1400, price_6=1400, price_7=1400, price_8=1400,
        price_9=1400, price_10=1400, price_11=1400, price_12=1400,
        salary_1=55000, salary_2=55000, salary_3=55000, salary_4=55000,
        salary_5=55000, salary_6=55000, salary_7=55000, salary_8=55000,
        salary_9=55000, salary_10=55000, salary_11=55000, salary_12=55000,
        utr_1=0.8, utr_2=0.8, utr_3=0.8, utr_4=0.8,
        utr_5=0.8, utr_6=0.8, utr_7=0.8, utr_8=0.8,
        utr_9=0.8, utr_10=0.8, utr_11=0.8, utr_12=0.8
    )
    
    # Test the initialization logic directly
    base_date = datetime(2025, 1, 1)  # January 2025
    
    # Career path for C level
    career_path = {
        'time_on_level': 18, 
        'start_tenure': 15, 
        'end_tenure': 33, 
        'progression_months': [1, 7]
    }
    
    # Generate realistic tenure
    total_tenure = random.randint(15, 33)  # 15-33 months total tenure
    time_on_level = random.randint(0, 18)  # 0-18 months on level
    
    # Calculate dates
    career_start_date = base_date - timedelta(days=total_tenure * 30)
    level_start_date = base_date - timedelta(days=time_on_level * 30)
    
    # Ensure level start is after career start
    if level_start_date < career_start_date:
        level_start_date = career_start_date
    
    print(f"Generated tenure:")
    print(f"  Total tenure: {total_tenure} months")
    print(f"  Time on level: {time_on_level} months")
    print(f"  Career start: {career_start_date.strftime('%Y-%m')}")
    print(f"  Level start: {level_start_date.strftime('%Y-%m')}")
    
    # Create person using the initialization logic
    person = level.add_new_hire(
        career_start_date.strftime("%Y-%m"),
        "Consultant",
        "TestOffice"
    )
    
    # Override level start (this is what the initialization logic does)
    person.level_start = level_start_date.strftime("%Y-%m")
    
    print(f"\nPerson created:")
    print(f"  Career start: {person.career_start}")
    print(f"  Level start: {person.level_start}")
    
    # Test tenure calculation
    current_date = "2025-01"
    career_tenure = person.get_career_tenure_months(current_date)
    level_tenure = person.get_level_tenure_months(current_date)
    
    print(f"\nTenure calculation for {current_date}:")
    print(f"  Career tenure: {career_tenure} months")
    print(f"  Level tenure: {level_tenure} months")
    
    # Verify the calculation is correct
    expected_career_tenure = total_tenure
    expected_level_tenure = time_on_level
    
    print(f"\nExpected vs Actual:")
    print(f"  Career tenure: expected {expected_career_tenure}, got {career_tenure}")
    print(f"  Level tenure: expected {expected_level_tenure}, got {level_tenure}")
    
    if career_tenure == expected_career_tenure and level_tenure == expected_level_tenure:
        print("✅ Tenure calculation is working correctly!")
    else:
        print("❌ Tenure calculation is incorrect!")
    
    return person

def test_office_manager_initialization():
    """Test the office manager initialization"""
    print("\n🔍 TESTING OFFICE MANAGER INITIALIZATION")
    print("=" * 50)
    
    # Initialize the office manager
    office_manager = OfficeManager(config_service)
    
    # Create a simple test office
    test_office_config = {
        "name": "TestOffice",
        "total_fte": 100,
        "journey": "Mature Office",
        "roles": {
            "Consultant": {
                "C": {
                    "fte": 10,
                    "salary": 55000,
                    "price_1": 1400,
                    "progression_1": 0.1,
                    "progression_7": 0.1,
                    "recruitment_1": 0.05,
                    "recruitment_7": 0.05,
                    "churn_1": 0.02,
                    "churn_7": 0.02
                }
            }
        }
    }
    
    # Create office
    office = office_manager._create_office_from_config(test_office_config)
    
    print(f"Office created: {office.name}")
    print(f"Total FTE: {office.total_fte}")
    
    # Check the C level
    c_level = office.roles["Consultant"]["C"]
    print(f"C level FTE: {c_level.total}")
    
    if c_level.total > 0:
        # Check the first person
        person = c_level.people[0]
        print(f"\nFirst person:")
        print(f"  Career start: {person.career_start}")
        print(f"  Level start: {person.level_start}")
        
        # Calculate tenure
        current_date = "2025-01"
        career_tenure = person.get_career_tenure_months(current_date)
        level_tenure = person.get_level_tenure_months(current_date)
        
        print(f"  Career tenure: {career_tenure} months")
        print(f"  Level tenure: {level_tenure} months")
        
        # Check if this person could promote in first year
        if career_tenure >= 27 and level_tenure >= 12:
            print("  ⚠️  This person could promote in first year!")
        else:
            print("  ✅ This person cannot promote in first year (correct)")

if __name__ == "__main__":
    test_tenure_calculation()
    test_office_manager_initialization() 