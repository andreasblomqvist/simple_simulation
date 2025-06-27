import pytest
import random
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from backend.src.services.simulation.models import Person, Level
from backend.config.laf_progression import LAF_PROGRESSION, PROGRESSION_LEVER

def create_test_office():
    """Create a test office with realistic data"""
    office_name = "Stockholm"
    
    # Create people with different tenures
    people_data = [
        # Level A people
        {"level": "A", "tenure": 3, "count": 20},   # CAT0 - no progression
        {"level": "A", "tenure": 8, "count": 30},   # CAT6
        {"level": "A", "tenure": 14, "count": 25},  # CAT12
        {"level": "A", "tenure": 20, "count": 15},  # CAT18
        {"level": "A", "tenure": 26, "count": 10},  # CAT24
        
        # Level AC people
        {"level": "AC", "tenure": 10, "count": 25}, # CAT6
        {"level": "AC", "tenure": 16, "count": 30}, # CAT12
        {"level": "AC", "tenure": 22, "count": 20}, # CAT18
        {"level": "AC", "tenure": 28, "count": 15}, # CAT24
        {"level": "AC", "tenure": 35, "count": 10}, # CAT30
        
        # Level C people
        {"level": "C", "tenure": 12, "count": 20},  # CAT12
        {"level": "C", "tenure": 18, "count": 25},  # CAT18
        {"level": "C", "tenure": 24, "count": 20},  # CAT24
        {"level": "C", "tenure": 30, "count": 15},  # CAT30
    ]
    
    levels = {}
    for data in people_data:
        level_name = data["level"]
        if level_name not in levels:
            # Create Level with all required parameters
            levels[level_name] = Level(
                name=level_name,
                journey=None,
                progression_months=[1],
                # Monthly progression rates (not used in LAF system)
                progression_1=0.0, progression_2=0.0, progression_3=0.0, progression_4=0.0,
                progression_5=0.0, progression_6=0.0, progression_7=0.0, progression_8=0.0,
                progression_9=0.0, progression_10=0.0, progression_11=0.0, progression_12=0.0,
                # Monthly recruitment rates
                recruitment_1=0.0, recruitment_2=0.0, recruitment_3=0.0, recruitment_4=0.0,
                recruitment_5=0.0, recruitment_6=0.0, recruitment_7=0.0, recruitment_8=0.0,
                recruitment_9=0.0, recruitment_10=0.0, recruitment_11=0.0, recruitment_12=0.0,
                # Monthly churn rates
                churn_1=0.0, churn_2=0.0, churn_3=0.0, churn_4=0.0,
                churn_5=0.0, churn_6=0.0, churn_7=0.0, churn_8=0.0,
                churn_9=0.0, churn_10=0.0, churn_11=0.0, churn_12=0.0,
                # Monthly prices
                price_1=0.0, price_2=0.0, price_3=0.0, price_4=0.0,
                price_5=0.0, price_6=0.0, price_7=0.0, price_8=0.0,
                price_9=0.0, price_10=0.0, price_11=0.0, price_12=0.0,
                # Monthly salaries
                salary_1=0.0, salary_2=0.0, salary_3=0.0, salary_4=0.0,
                salary_5=0.0, salary_6=0.0, salary_7=0.0, salary_8=0.0,
                salary_9=0.0, salary_10=0.0, salary_11=0.0, salary_12=0.0,
                # Monthly UTR rates
                utr_1=1.0, utr_2=1.0, utr_3=1.0, utr_4=1.0,
                utr_5=1.0, utr_6=1.0, utr_7=1.0, utr_8=1.0,
                utr_9=1.0, utr_10=1.0, utr_11=1.0, utr_12=1.0,
                people=[],
                fractional_recruitment=0.0,
                fractional_churn=0.0
            )
        
        # Create people for this level/tenure combination
        for i in range(data["count"]):
            # Calculate level_start date based on tenure
            # If tenure is 3 months, level_start should be 2024-09 (3 months before 2025-01)
            # If tenure is 35 months, level_start should be 2022-02 (35 months before 2025-01)
            target_date = "2025-01"
            tenure_months = data['tenure']
            
            # Calculate the year and month for level_start
            if tenure_months <= 12:
                # Within same year
                level_start_month = 12 - tenure_months + 1
                level_start_year = 2024
            else:
                # Previous year(s)
                level_start_month = 12 - (tenure_months - 12) + 1
                level_start_year = 2024 - ((tenure_months - 1) // 12)
            
            # Handle month overflow
            if level_start_month <= 0:
                level_start_month += 12
                level_start_year -= 1
            
            level_start = f"{level_start_year}-{level_start_month:02d}"
            
            person = Person(
                id=f"{level_name}_{data['tenure']}_{i}",
                career_start="2020-01",
                current_level=level_name,
                level_start=level_start,
                role="Consultant",
                office=office_name
            )
            levels[level_name].people.append(person)
    
    return levels

def test_laf_integration():
    """Test the complete LAF-based progression system"""
    random.seed(42)
    
    # Create test office
    levels = create_test_office()
    
    # Track expected vs actual progressions
    results = []
    
    for level_name, level in levels.items():
        if len(level.people) == 0:
            continue
            
        # Group people by CAT
        cat_groups = {}
        for person in level.people:
            tenure = person.get_level_tenure_months("2025-01")
            if tenure < 6:
                cat = "CAT0"
            elif tenure < 12:
                cat = "CAT6"
            elif tenure < 18:
                cat = "CAT12"
            elif tenure < 24:
                cat = "CAT18"
            elif tenure < 30:
                cat = "CAT24"
            else:
                cat = "CAT30"
            
            if cat not in cat_groups:
                cat_groups[cat] = []
            cat_groups[cat].append(person)
        
        # Calculate expected progressions for each CAT group
        for cat, people in cat_groups.items():
            if cat == "CAT0":
                expected_prob = 0.0
            else:
                expected_prob = LAF_PROGRESSION["Stockholm"][level_name].get(cat, 0.0) * PROGRESSION_LEVER
                expected_prob = min(expected_prob, 1.0)
            
            expected_count = len(people) * expected_prob
            
            # Apply progression
            promoted = level.apply_cat_based_progression("2025-01")
            
            # Count how many from this CAT group were promoted
            promoted_from_cat = sum(1 for p in promoted if p in people)
            
            # Statistical test (±3σ for binomial distribution)
            if expected_prob > 0 and expected_prob < 1:
                stddev = (len(people) * expected_prob * (1 - expected_prob)) ** 0.5
                lower = max(0, expected_count - 3 * stddev)
                upper = min(len(people), expected_count + 3 * stddev)
                in_range = lower <= promoted_from_cat <= upper
            else:
                in_range = promoted_from_cat == expected_count
            
            results.append({
                "Level": level_name,
                "CAT": cat,
                "People": len(people),
                "Expected": round(expected_count, 1),
                "Actual": promoted_from_cat,
                "Pass": in_range
            })
    
    # Print results table
    print("\nLAF Integration Test Results:")
    print("=" * 80)
    print(f"{'Level':<6} {'CAT':<6} {'People':<8} {'Expected':<10} {'Actual':<8} {'Pass':<6}")
    print("-" * 80)
    
    passed = 0
    total = 0
    
    for result in results:
        status = "✅" if result["Pass"] else "❌"
        print(f"{result['Level']:<6} {result['CAT']:<6} {result['People']:<8} {result['Expected']:<10.1f} {result['Actual']:<8} {status:<6}")
        if result["Pass"]:
            passed += 1
        total += 1
    
    print("-" * 80)
    print(f"Pass Rate: {passed}/{total} ({passed/total*100:.1f}%)")
    
    # Assert most tests pass (allow for some statistical variance)
    assert passed >= total * 0.8, f"Only {passed}/{total} tests passed, expected at least 80%" 