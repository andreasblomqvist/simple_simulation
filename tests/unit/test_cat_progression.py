import pytest
import random
from datetime import datetime, timedelta
from backend.src.services.simulation.models import Person, Level
from backend.config.progression_config import CAT_CURVES, PROGRESSION_CONFIG

# Import actual CAT curves from progression config
from backend.config.progression_config import CAT_CURVES

def calculate_level_start_date(cat_months, current_date="2025-01"):
    """Calculate a valid level start date that gives the specified CAT months"""
    current_dt = datetime.strptime(current_date, "%Y-%m")
    # Subtract the CAT months to get the level start date
    level_start_dt = current_dt - timedelta(days=cat_months * 30)  # Approximate
    return level_start_dt.strftime("%Y-%m")

@pytest.mark.parametrize("level_name, fte, progression_1, cat_months, expected_multiplier", [
    ("A", 100, 0.10, 6, CAT_CURVES['A']['CAT6']),
    ("AC", 50, 0.20, 12, CAT_CURVES['AC']['CAT12']),
    ("C", 0, 0.50, 18, CAT_CURVES['C']['CAT18']),
    ("SrC", 100, 0.0, 24, CAT_CURVES['SrC']['CAT24']),
    ("AM", 100, 0.8, 30, CAT_CURVES['AM']['CAT30']),  # Changed from 1.0 to 0.8
])
def test_cat_progression_varied(level_name, fte, progression_1, cat_months, expected_multiplier):
    # Set random seed for reproducibility
    random.seed(42)
    # Create people with the specified tenure
    people = [
        Person(
            id=str(i),
            career_start="2020-01",
            current_level=level_name,
            level_start=calculate_level_start_date(cat_months),
            role="Consultant",
            office="TestOffice"
        ) for i in range(fte)
    ]
    # Create a Level and assign people
    level = Level(
        name=level_name,
        journey=None,
        progression_months=[1],
        progression_1=progression_1,
        progression_2=0.0,
        progression_3=0.0,
        progression_4=0.0,
        progression_5=0.0,
        progression_6=0.0,
        progression_7=0.0,
        progression_8=0.0,
        progression_9=0.0,
        progression_10=0.0,
        progression_11=0.0,
        progression_12=0.0,
        recruitment_1=0.0,
        recruitment_2=0.0,
        recruitment_3=0.0,
        recruitment_4=0.0,
        recruitment_5=0.0,
        recruitment_6=0.0,
        recruitment_7=0.0,
        recruitment_8=0.0,
        recruitment_9=0.0,
        recruitment_10=0.0,
        recruitment_11=0.0,
        recruitment_12=0.0,
        churn_1=0.0,
        churn_2=0.0,
        churn_3=0.0,
        churn_4=0.0,
        churn_5=0.0,
        churn_6=0.0,
        churn_7=0.0,
        churn_8=0.0,
        churn_9=0.0,
        churn_10=0.0,
        churn_11=0.0,
        churn_12=0.0,
        price_1=0.0,
        price_2=0.0,
        price_3=0.0,
        price_4=0.0,
        price_5=0.0,
        price_6=0.0,
        price_7=0.0,
        price_8=0.0,
        price_9=0.0,
        price_10=0.0,
        price_11=0.0,
        price_12=0.0,
        salary_1=0.0,
        salary_2=0.0,
        salary_3=0.0,
        salary_4=0.0,
        salary_5=0.0,
        salary_6=0.0,
        salary_7=0.0,
        salary_8=0.0,
        salary_9=0.0,
        salary_10=0.0,
        salary_11=0.0,
        salary_12=0.0,
        utr_1=1.0,
        utr_2=1.0,
        utr_3=1.0,
        utr_4=1.0,
        utr_5=1.0,
        utr_6=1.0,
        utr_7=1.0,
        utr_8=1.0,
        utr_9=1.0,
        utr_10=1.0,
        utr_11=1.0,
        utr_12=1.0,
        people=people,
        fractional_recruitment=0.0,
        fractional_churn=0.0
    )
    # Run progression for January
    promoted = level.apply_cat_based_progression("2025-01", PROGRESSION_CONFIG, CAT_CURVES)
    # Calculate expected promotions using actual CAT curve probability
    expected_prob = expected_multiplier  # CAT curve value is already the probability
    expected_promoted = fte * expected_prob
    # Allow for binomial variance (±3σ)
    if expected_prob >= 1.0:
        stddev = 0.0
    else:
        stddev = (fte * expected_prob * (1 - expected_prob)) ** 0.5 if fte > 0 else 0
    lower = max(0, expected_promoted - 3 * stddev)
    upper = min(fte, expected_promoted + 3 * stddev)
    print(f"Level {level_name}: FTE={fte}, prog_1={progression_1}, CAT_months={cat_months}, multiplier={expected_multiplier}, expected={expected_promoted:.1f}, actual={len(promoted)}, range=({lower:.1f}, {upper:.1f})")
    # Assert actual is within 3σ of expected
    assert lower <= len(promoted) <= upper
    # Edge cases
    if fte == 0 or expected_multiplier == 0.0:
        assert len(promoted) == 0

def run_cat_progression_case(level_name, fte, progression_1, cat_months, cat_multiplier, seed=42):
    random.seed(seed)
    # Use the local CAT curves for this test
    # Note: This function is not used in the current test, but keeping for compatibility
    people = [
        Person(
            id=str(i),
            career_start="2020-01",
            current_level=level_name,
            level_start=calculate_level_start_date(cat_months),
            role="Consultant",
            office="TestOffice"
        ) for i in range(fte)
    ]
    level = Level(
        name=level_name,
        journey=None,
        progression_months=[1],
        progression_1=progression_1,
        progression_2=0.0,
        progression_3=0.0,
        progression_4=0.0,
        progression_5=0.0,
        progression_6=0.0,
        progression_7=0.0,
        progression_8=0.0,
        progression_9=0.0,
        progression_10=0.0,
        progression_11=0.0,
        progression_12=0.0,
        recruitment_1=0.0,
        recruitment_2=0.0,
        recruitment_3=0.0,
        recruitment_4=0.0,
        recruitment_5=0.0,
        recruitment_6=0.0,
        recruitment_7=0.0,
        recruitment_8=0.0,
        recruitment_9=0.0,
        recruitment_10=0.0,
        recruitment_11=0.0,
        recruitment_12=0.0,
        churn_1=0.0,
        churn_2=0.0,
        churn_3=0.0,
        churn_4=0.0,
        churn_5=0.0,
        churn_6=0.0,
        churn_7=0.0,
        churn_8=0.0,
        churn_9=0.0,
        churn_10=0.0,
        churn_11=0.0,
        churn_12=0.0,
        price_1=0.0,
        price_2=0.0,
        price_3=0.0,
        price_4=0.0,
        price_5=0.0,
        price_6=0.0,
        price_7=0.0,
        price_8=0.0,
        price_9=0.0,
        price_10=0.0,
        price_11=0.0,
        price_12=0.0,
        salary_1=0.0,
        salary_2=0.0,
        salary_3=0.0,
        salary_4=0.0,
        salary_5=0.0,
        salary_6=0.0,
        salary_7=0.0,
        salary_8=0.0,
        salary_9=0.0,
        salary_10=0.0,
        salary_11=0.0,
        salary_12=0.0,
        utr_1=1.0,
        utr_2=1.0,
        utr_3=1.0,
        utr_4=1.0,
        utr_5=1.0,
        utr_6=1.0,
        utr_7=1.0,
        utr_8=1.0,
        utr_9=1.0,
        utr_10=1.0,
        utr_11=1.0,
        utr_12=1.0,
        people=people,
        fractional_recruitment=0.0,
        fractional_churn=0.0
    )
    promoted = level.apply_cat_based_progression("2025-01", PROGRESSION_CONFIG, CAT_CURVES)
    # If tenure < 6, no one is eligible
    if cat_months < 6:
        expected_promoted = 0.0
        lower = 0
        upper = 0
    else:
        prob = min(progression_1 * cat_multiplier, 1.0)
        expected_promoted = fte * prob
        if prob >= 1.0:
            stddev = 0.0
        else:
            stddev = (fte * prob * (1 - prob)) ** 0.5 if fte > 0 else 0
        lower = max(0, expected_promoted - 3 * stddev)
        upper = min(fte, expected_promoted + 3 * stddev)
    pass_fail = lower <= len(promoted) <= upper
    return {
        'Level': level_name,
        'FTE': fte,
        'Progression Rate': progression_1,
        'CAT Multiplier': cat_multiplier,
        'Expected': round(expected_promoted, 1),
        'Actual': len(promoted),
        'Range': f"({round(lower,1)}, {round(upper,1)})",
        'Pass': pass_fail
    }

def test_cat_progression_matrix():
    # Matrix of scenarios
    fte_cases = [1, 10, 100, 1000]
    prog_cases = [0.0, 0.01, 0.5, 1.0]
    cat_cases = [0.0, 0.5, 1.0, 2.0]
    tenure_cases = [5, 6]  # 5 = ineligible, 6 = eligible
    results = []
    for fte in fte_cases:
        for prog in prog_cases:
            for cat in cat_cases:
                for tenure in tenure_cases:
                    # Use a unique level name for each scenario
                    level_name = f"L{fte}_{prog}_{cat}_{tenure}"
                    res = run_cat_progression_case(level_name, fte, prog, tenure, cat)
                    results.append(res)
    # Print markdown table
    print("\n| Level | FTE | Progression Rate | CAT Multiplier | Expected Promoted | Actual Promoted | Range (3σ) | Pass |\n|-------|-----|------------------|----------------|-------------------|-----------------|------------|------|")
    for r in results:
        print(f"| {r['Level']} | {r['FTE']} | {r['Progression Rate']} | {r['CAT Multiplier']} | {r['Expected']} | {r['Actual']} | {r['Range']} | {'✅' if r['Pass'] else '❌'} |")
    # Assert all pass
    assert all(r['Pass'] for r in results), "Some CAT progression edge cases failed!" 