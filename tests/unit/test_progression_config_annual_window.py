import pytest
import sys
import os
import random
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from backend.src.services.simulation.models import Person, Level
from backend.config.progression_config import PROGRESSION_CONFIG

def make_level(level_name, people):
    return Level(
        name=level_name,
        journey=None,
        progression_months=[1],
        progression_1=0.0, progression_2=0.0, progression_3=0.0, progression_4=0.0,
        progression_5=0.0, progression_6=0.0, progression_7=0.0, progression_8=0.0,
        progression_9=0.0, progression_10=0.0, progression_11=0.0, progression_12=0.0,
        recruitment_1=0.0, recruitment_2=0.0, recruitment_3=0.0, recruitment_4=0.0,
        recruitment_5=0.0, recruitment_6=0.0, recruitment_7=0.0, recruitment_8=0.0,
        recruitment_9=0.0, recruitment_10=0.0, recruitment_11=0.0, recruitment_12=0.0,
        churn_1=0.0, churn_2=0.0, churn_3=0.0, churn_4=0.0,
        churn_5=0.0, churn_6=0.0, churn_7=0.0, churn_8=0.0,
        churn_9=0.0, churn_10=0.0, churn_11=0.0, churn_12=0.0,
        price_1=0.0, price_2=0.0, price_3=0.0, price_4=0.0,
        price_5=0.0, price_6=0.0, price_7=0.0, price_8=0.0,
        price_9=0.0, price_10=0.0, price_11=0.0, price_12=0.0,
        salary_1=0.0, salary_2=0.0, salary_3=0.0, salary_4=0.0,
        salary_5=0.0, salary_6=0.0, salary_7=0.0, salary_8=0.0,
        salary_9=0.0, salary_10=0.0, salary_11=0.0, salary_12=0.0,
        utr_1=1.0, utr_2=1.0, utr_3=1.0, utr_4=1.0,
        utr_5=1.0, utr_6=1.0, utr_7=1.0, utr_8=1.0,
        utr_9=1.0, utr_10=1.0, utr_11=1.0, utr_12=1.0,
        people=people,
        fractional_recruitment=0.0,
        fractional_churn=0.0
    )

def make_person(level_name, months_on_level, total_tenure, start_month=None):
    # Set level_start so that tenure is correct for 2025-01
    # Optionally bias start month for A
    if start_month is None:
        year = 2025 - (months_on_level // 12)
        month = 1 - (months_on_level % 12)
        if month <= 0:
            month += 12
            year -= 1
    else:
        # Use the provided start_month
        year = 2025 - (months_on_level // 12)
        month = start_month
    level_start = f"{year}-{month:02d}"
    # Calculate career_start so that total_tenure is correct
    career_year = 2025 - (total_tenure // 12)
    career_month = 1 - (total_tenure % 12)
    if career_month <= 0:
        career_month += 12
        career_year -= 1
    career_start = f"{career_year}-{career_month:02d}"
    return Person(
        id=f"{level_name}_{months_on_level}_{total_tenure}",
        career_start=career_start,
        current_level=level_name,
        level_start=level_start,
        role="Consultant",
        office="TestOffice"
    )

def test_progression_windows_one_year():
    random.seed(42)
    results = []
    for level_name, config in PROGRESSION_CONFIG.items():
        people = []
        for i in range(10):
            # Random months on level (1-24)
            months_on_level = random.randint(1, 24)
            # Random total tenure (at least months_on_level, up to +36 more)
            total_tenure = months_on_level + random.randint(0, 36)
            # For A, bias 70% to start in August
            if level_name == 'A' and random.random() < 0.7:
                start_month = 8
            else:
                start_month = None
            p = make_person(level_name, months_on_level, total_tenure, start_month)
            people.append(p)
        # Printout for this level
        print(f"\nLevel {level_name} FTEs:")
        for p in people:
            print(f"  id={p.id}, months_on_level={months_on_level}, total_tenure={total_tenure}, level_start={p.level_start}, career_start={p.career_start}")
        level = make_level(level_name, people)
        progression_months = config['progression_months']
        for month in range(1, 13):
            date = f"2025-{month:02d}"
            eligible = level.get_eligible_for_progression(date)
            results.append((level_name, month, len(eligible)))
    # Print table
    print("\nLevel | Month | Eligible FTEs")
    print("----------------------------")
    for level_name, month, count in results:
        print(f"{level_name:>4}  |  {month:>2}   |    {count}")
    # Check OPE never eligible
    for month in range(1, 13):
        assert results.count(('OPE', month, 0)) == 1
    # Check A and AC have eligible FTEs only in 1,4,7,10
    for level_name in ['A', 'AC']:
        for month in [1, 4, 7, 10]:
            assert any(l == level_name and m == month and c == 10 for l, m, c in results)
        for month in [2, 3, 5, 6, 8, 9, 11, 12]:
            assert any(l == level_name and m == month and c == 0 for l, m, c in results)
    # Check C, SrC, AM have eligible FTEs only in 1,7
    for level_name in ['C', 'SrC', 'AM']:
        for month in [1, 7]:
            assert any(l == level_name and m == month and c == 10 for l, m, c in results)
        for month in [2, 3, 4, 5, 6, 8, 9, 10, 11, 12]:
            assert any(l == level_name and m == month and c == 0 for l, m, c in results)
    # Check seniors only in 1
    for level_name in ['M', 'SrM', 'Pi', 'P', 'X']:
        for month in [1]:
            assert any(l == level_name and m == month and c == 10 for l, m, c in results)
        for month in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
            assert any(l == level_name and m == month and c == 0 for l, m, c in results) 