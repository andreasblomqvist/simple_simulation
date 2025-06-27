import pytest
import numpy as np

# Updated minimum tenure for progression eligibility
MIN_TENURE = {
    'A': 6,
    'AC': 12,
    'C': 12,
    'SrC': 12,
    'AM': 24,
    'M': 24,
    'SrM': 24,
    'PiP': 1000,
    'P': 1000,
    'OPE': 1000
}

# Classic CAT multipliers
CAT_MULTIPLIERS = [
    (0, 6, 0.0),    # CAT0: <6 months
    (6, 12, 0.5),   # CAT6: 6-11 months
    (12, 18, 1.0),  # CAT12: 12-17 months
    (18, 24, 1.5),  # CAT18: 18-23 months
    (24, 1000, 2.0) # CAT24+: 24+ months
]

# Level: (progression_rate, FTE, tenure_months)
LEVEL_DATA = {
    'A':   (0.69, 100, [3, 6, 8, 15, 25]),
    'AC':  (0.67, 80, [10, 12, 14, 20, 30]),
    'C':   (0.65, 60, [5, 12, 16, 22, 30]),
    'SrC': (0.63, 50, [8, 12, 18, 24, 36]),
    'AM':  (0.60, 40, [10, 20, 24, 30, 40]),
    'M':   (0.55, 30, [5, 12, 18, 24, 36]),
    'SrM': (0.38, 20, [10, 18, 24, 30, 50]),
    'PiP': (0.31, 10, [10, 20, 30, 40, 60]),
    'P':   (0.10, 5, [10, 20, 30, 40, 60]),
    'OPE': (0.05, 5, [10, 20, 30, 40, 60]),
}

def assign_cat(tenure):
    for start, end, mult in CAT_MULTIPLIERS:
        if start <= tenure < end:
            return mult, f"CAT{int(start) if start < 24 else '24+'}"
    return 0.0, "CAT?"

def test_cat_progression_min_tenure():
    np.random.seed(42)
    print("| Name   | Level | Time on Level | Total Tenure | Eligible? | CAT | Mult | Prob |")
    print("|--------|-------|---------------|--------------|-----------|-----|------|------|")
    for level, (rate, fte, tenure_list) in LEVEL_DATA.items():
        for i, tenure in enumerate(tenure_list):
            total_tenure = tenure + 12 * i  # Just for variety
            eligible = tenure >= MIN_TENURE[level]
            cat_mult, cat_name = assign_cat(tenure)
            prob = rate * cat_mult if eligible else 0.0
            prob = min(prob, 1.0)
            name = f"{level}_Emp{i+1}"
            print(f"| {name:<6} | {level:<5} | {tenure:^13} | {total_tenure:^12} | {str(eligible):^9} | {cat_name:^3} | {cat_mult:^4.1f} | {prob:^4.2f} |")
    # No assertion, this is a demonstration/inspection test 