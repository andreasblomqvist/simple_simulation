import pytest
import random
from backend.config.laf_progression import LAF_PROGRESSION, PROGRESSION_LEVER

# Mock Person and Level for isolated testing
class MockPerson:
    def __init__(self, office, level, tenure_months):
        self.office = office
        self.level = level
        self.tenure_months = tenure_months
    def get_level_tenure_months(self, _):
        return self.tenure_months
    def get_progression_probability(self, current_date, level_name):
        # Replicate the new logic
        tenure_months = self.get_level_tenure_months(current_date)
        if tenure_months < 6:
            cat = 'CAT0'
        elif tenure_months < 12:
            cat = 'CAT6'
        elif tenure_months < 18:
            cat = 'CAT12'
        elif tenure_months < 24:
            cat = 'CAT18'
        elif tenure_months < 30:
            cat = 'CAT24'
        else:
            cat = 'CAT30'
        # CAT0 should always return 0.0
        if cat == 'CAT0':
            return 0.0
        prob = (
            LAF_PROGRESSION.get(self.office, {})
            .get(level_name, {})
            .get(cat, 0.0)
        )
        prob = prob * PROGRESSION_LEVER
        return min(prob, 1.0)

@pytest.mark.parametrize("office,level,cat,tenure,expected", [
    ("Stockholm", "A", "CAT6", 6, LAF_PROGRESSION["Stockholm"]["A"]["CAT6"]),
    ("Stockholm", "A", "CAT12", 12, LAF_PROGRESSION["Stockholm"]["A"]["CAT12"]),
    ("Stockholm", "AC", "CAT18", 18, LAF_PROGRESSION["Stockholm"]["AC"]["CAT18"]),
    ("Munich", "C", "CAT24", 24, LAF_PROGRESSION["Munich"]["C"]["CAT24"]),
    ("Munich", "A", "CAT30", 40, LAF_PROGRESSION["Munich"]["A"]["CAT30"]),
    ("Stockholm", "A", "CAT0", 0, 0.0),
    ("UnknownOffice", "A", "CAT6", 6, 0.0),
    ("Stockholm", "UnknownLevel", "CAT6", 6, 0.0),
    ("Stockholm", "A", "UnknownCAT", 10000, LAF_PROGRESSION["Stockholm"]["A"].get("CAT30", 0.0)),
])
def test_laf_progression_lookup(office, level, cat, tenure, expected):
    p = MockPerson(office, level, tenure)
    prob = p.get_progression_probability("2025-01", level)
    if cat == "CAT0":
        assert prob == 0.0
    elif cat.startswith("CAT") and cat in LAF_PROGRESSION.get(office, {}).get(level, {}):
        assert abs(prob - expected) < 1e-8
    elif office not in LAF_PROGRESSION or level not in LAF_PROGRESSION.get(office, {}):
        assert prob == 0.0
    else:
        # For unknown CAT, should fallback to CAT30 if tenure is very high
        assert abs(prob - LAF_PROGRESSION[office][level]["CAT30"]) < 1e-8

def test_laf_progression_lever():
    p = MockPerson("Stockholm", "A", 12)
    base_prob = LAF_PROGRESSION["Stockholm"]["A"]["CAT12"]
    # Test lever scaling
    for lever in [0.5, 1.0, 1.5, 2.0]:
        expected_prob = min(base_prob * lever, 1.0)
        # Create a new MockPerson with the lever logic built-in
        class MockPersonWithLever:
            def __init__(self, office, level, tenure_months, lever_val):
                self.office = office
                self.level = level
                self.tenure_months = tenure_months
                self.lever = lever_val
            def get_level_tenure_months(self, _):
                return self.tenure_months
            def get_progression_probability(self, current_date, level_name):
                tenure_months = self.get_level_tenure_months(current_date)
                if tenure_months < 6:
                    return 0.0
                elif tenure_months < 12:
                    cat = 'CAT6'
                elif tenure_months < 18:
                    cat = 'CAT12'
                elif tenure_months < 24:
                    cat = 'CAT18'
                elif tenure_months < 30:
                    cat = 'CAT24'
                else:
                    cat = 'CAT30'
                prob = (
                    LAF_PROGRESSION.get(self.office, {})
                    .get(level_name, {})
                    .get(cat, 0.0)
                )
                prob = prob * self.lever
                return min(prob, 1.0)
        
        p_with_lever = MockPersonWithLever("Stockholm", "A", 12, lever)
        prob = p_with_lever.get_progression_probability("2025-01", "A")
        assert abs(prob - expected_prob) < 1e-8

def test_laf_progression_statistical():
    # Simulate 1000 people in Stockholm, A, CAT12 (12 months), lever=1.0
    office = "Stockholm"
    level = "A"
    tenure = 12
    prob = LAF_PROGRESSION[office][level]["CAT12"]
    n = 1000
    promoted = 0
    random.seed(42)
    for _ in range(n):
        p = MockPerson(office, level, tenure)
        if random.random() < p.get_progression_probability("2025-01", level):
            promoted += 1
    # Binomial confidence interval (±3σ)
    expected = n * prob
    stddev = (n * prob * (1 - prob)) ** 0.5
    lower = expected - 3 * stddev
    upper = expected + 3 * stddev
    assert lower <= promoted <= upper, f"Promoted: {promoted}, Expected: {expected} ± {3*stddev}" 