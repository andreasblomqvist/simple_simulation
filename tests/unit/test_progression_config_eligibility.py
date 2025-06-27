import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from backend.src.services.simulation.models import Person, Level
from backend.config.progression_config import PROGRESSION_CONFIG

def make_level(level_name, people):
    # Create a Level with all required fields set to 0 or defaults
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

def make_person(level_name, tenure_months):
    # Set level_start so that tenure is correct for 2025-01
    year = 2025 - (tenure_months // 12)
    month = 1 - (tenure_months % 12)
    if month <= 0:
        month += 12
        year -= 1
    level_start = f"{year}-{month:02d}"
    return Person(
        id=f"{level_name}_{tenure_months}",
        career_start="2020-01",
        current_level=level_name,
        level_start=level_start,
        role="Consultant",
        office="TestOffice"
    )

def test_progression_months_and_tenure():
    # Test for level 'A' (progression months: 1,4,7,10; start_tenure: 0)
    level_name = 'A'
    config = PROGRESSION_CONFIG[level_name]
    # Eligible in Jan (1), not in Feb (2)
    p1 = make_person(level_name, 6)  # 6 months tenure
    p2 = make_person(level_name, 0)  # 0 months tenure
    level = make_level(level_name, [p1, p2])
    print('A:', [(p.id, p.get_level_tenure_months('2025-01')) for p in [p1, p2]])
    eligible_jan = level.get_eligible_for_progression("2025-01")
    eligible_feb = level.get_eligible_for_progression("2025-02")
    # Should be eligible in Jan, not in Feb
    assert p1 in eligible_jan
    assert p2 in eligible_jan  # start_tenure is 0
    assert p1 not in eligible_feb
    assert p2 not in eligible_feb

    # Test for level 'C' (progression months: 1,7; start_tenure: 15)
    level_name = 'C'
    config = PROGRESSION_CONFIG[level_name]
    p3 = make_person(level_name, 20)  # 20 months tenure
    p4 = make_person(level_name, 10)  # 10 months tenure
    level = make_level(level_name, [p3, p4])
    print('C:', [(p.id, p.get_level_tenure_months('2025-01')) for p in [p3, p4]])
    eligible_jan = level.get_eligible_for_progression("2025-01")
    eligible_jul = level.get_eligible_for_progression("2025-07")
    eligible_feb = level.get_eligible_for_progression("2025-02")
    # Only p3 should be eligible in Jan and Jul
    assert p3 in eligible_jan
    assert p3 in eligible_jul
    assert p4 not in eligible_jan
    assert p4 not in eligible_jul
    # No one eligible in Feb
    assert eligible_feb == [] 