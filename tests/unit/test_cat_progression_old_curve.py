import pytest
import numpy as np

# Old CAT curve multipliers
CAT_MULTIPLIERS = [
    (0, 6, 0.0),    # CAT0: <6 months
    (6, 12, 0.5),   # CAT6: 6-11 months
    (12, 18, 1.0),  # CAT12: 12-17 months
    (18, 24, 1.5),  # CAT18: 18-23 months
    (24, 1000, 2.0) # CAT24+: 24+ months (large upper bound)
]

# Level: (progression_rate, FTE, tenure_start, tenure_end)
LEVEL_DATA = {
    'A':   (0.69, 201, 0, 6),
    'AC':  (0.67, 188, 6, 15),
    'C':   (0.65, 152, 15, 33),
    'SrC': (0.63, 270, 33, 51),
    'AM':  (0.60, 327, 51, 99),
    'M':   (0.55, 134, 99, 147),
    'SrM': (0.38, 102, 147, 267),
    'P':   (0.10, 13, 267, 279),
    'Pi':  (0.31, 6, 267, 279),
}


def assign_cat(tenure):
    for start, end, mult in CAT_MULTIPLIERS:
        if start <= tenure < end:
            return mult, f"CAT{int(start) if start < 24 else '24+'}"
    return 0.0, "CAT?"


def test_cat_progression_old_curve():
    np.random.seed(42)
    results = []
    for level, (rate, fte, t_start, t_end) in LEVEL_DATA.items():
        # Distribute FTEs evenly across tenure months
        tenure_months = list(range(t_start, t_end))
        if not tenure_months:
            continue
        fte_per_month = fte / len(tenure_months)
        expected = 0.0
        simulated = 0
        print(f"\nLevel: {level} | FTE: {fte} | Rate: {rate:.2f} | Tenure: {t_start}-{t_end-1} months | Months: {len(tenure_months)}")
        print("| Tenure | FTE | CAT  | Mult | Prob  | Exp | Sim |")
        print("|--------|-----|------|------|-------|-----|-----|")
        for tenure in tenure_months:
            cat_mult, cat_name = assign_cat(tenure)
            prob = min(rate * cat_mult, 1.0)
            n = int(round(fte_per_month))
            exp = n * prob
            sim = np.random.binomial(n, prob)
            expected += exp
            simulated += sim
            print(f"| {tenure:6} | {n:3} | {cat_name:4} | {cat_mult:4.2f} | {prob:5.2f} | {exp:3.1f} | {sim:3} |")
        # Allow 3 sigma for binomial variance
        sigma = np.sqrt(expected * (1 - (expected / max(fte, 1))))
        lower = expected - 3 * sigma
        upper = expected + 3 * sigma
        pass_fail = lower <= simulated <= upper
        print(f"| TOTAL  | {fte:3} |      |      |       | {expected:.1f} | {simulated} | {'✅' if pass_fail else '❌'} |\n")
        results.append((level, fte, rate, expected, simulated, pass_fail))
    # Print summary
    print("\n| Level | FTE | Rate | Expected | Simulated | Pass? |")
    print("|-------|-----|------|----------|-----------|-------|")
    for level, fte, rate, expected, simulated, pass_fail in results:
        print(f"| {level} | {fte} | {rate:.2f} | {expected:.2f} | {simulated} | {'✅' if pass_fail else '❌'} |")
    # Assert all pass
    assert all(pf for _,_,_,_,_,pf in results), "Some levels failed the statistical check." 