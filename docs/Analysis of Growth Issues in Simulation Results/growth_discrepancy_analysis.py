import json
import pandas as pd
import numpy as np

print("=== GROWTH RATE DISCREPANCY ANALYSIS ===")
print()

# Data from both simulations
new_sim = {
    'A': {'start': 163, 'end': 318, 'growth': 95.1},
    'AC': {'start': 231, 'end': 251, 'growth': 8.7},
    'AM': {'start': 418, 'end': 408, 'growth': -2.4},
    'C': {'start': 356, 'end': 348, 'growth': -2.2},
    'M': {'start': 156, 'end': 150, 'growth': -3.8},
    'PiP': {'start': 43, 'end': 43, 'growth': 0.0},
    'SrC': {'start': 409, 'end': 399, 'growth': -2.4},
    'SrM': {'start': 66, 'end': 62, 'growth': -6.1}
}

old_sim = {
    'A': {'start': 163, 'end': 256, 'growth': 57.1},
    'AC': {'start': 231, 'end': 425, 'growth': 84.0},
    'AM': {'start': 418, 'end': 382, 'growth': -8.6},
    'C': {'start': 356, 'end': 270, 'growth': -24.2},
    'M': {'start': 156, 'end': 161, 'growth': 3.2},
    'PiP': {'start': 43, 'end': 43, 'growth': 0.0},
    'SrC': {'start': 409, 'end': 428, 'growth': 4.6},
    'SrM': {'start': 66, 'end': 66, 'growth': 0.0}
}

print("1. DETAILED GROWTH COMPARISON:")
print("==============================")

print("Level | New Sim | Old Sim | Difference | Magnitude | Pattern")
print("------|---------|---------|------------|-----------|----------")

total_discrepancy = 0
major_discrepancies = []
pattern_reversals = []

for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    new_growth = new_sim[level]['growth']
    old_growth = old_sim[level]['growth']
    difference = new_growth - old_growth
    magnitude = abs(difference)
    
    # Classify the discrepancy
    if magnitude < 5:
        pattern = "Consistent"
    elif magnitude < 20:
        pattern = "Moderate"
    else:
        pattern = "MAJOR"
        major_discrepancies.append(level)
    
    # Check for pattern reversals (growth vs decline)
    if (new_growth > 0 and old_growth < 0) or (new_growth < 0 and old_growth > 0):
        pattern_reversals.append(level)
        pattern += " + REVERSAL"
    
    print(f"{level:5} | {new_growth:7.1f}% | {old_growth:7.1f}% | {difference:10.1f} | {magnitude:9.1f} | {pattern}")
    total_discrepancy += magnitude

print("------|---------|---------|------------|-----------|----------")
print(f"TOTAL |         |         |            | {total_discrepancy:9.1f} | ")

print(f"\nSummary Statistics:")
print(f"- Total discrepancy magnitude: {total_discrepancy:.1f} percentage points")
print(f"- Average discrepancy per level: {total_discrepancy/8:.1f} percentage points")
print(f"- Levels with major discrepancies: {len(major_discrepancies)}")
print(f"- Levels with pattern reversals: {len(pattern_reversals)}")

print("\n2. MATHEMATICAL ANALYSIS:")
print("=========================")

# Calculate implied annual growth rates
print("Implied Annual Growth Rates:")
print("Level | New Sim (5Y) | Old Sim (6Y) | New Annual | Old Annual | Difference")
print("------|--------------|--------------|------------|------------|------------")

for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    new_start = new_sim[level]['start']
    new_end = new_sim[level]['end']
    old_start = old_sim[level]['start']
    old_end = old_sim[level]['end']
    
    # Calculate annual growth rates
    new_annual = ((new_end / new_start) ** (1/5) - 1) * 100 if new_start > 0 else 0
    old_annual = ((old_end / old_start) ** (1/6) - 1) * 100 if old_start > 0 else 0
    
    annual_diff = new_annual - old_annual
    
    print(f"{level:5} | {new_sim[level]['growth']:12.1f}% | {old_sim[level]['growth']:12.1f}% | {new_annual:10.2f}% | {old_annual:10.2f}% | {annual_diff:10.2f}%")

print("\n3. RECRUITMENT/CHURN IMPLICATIONS:")
print("==================================")

# Based on the baseline recruitment/churn rates from the original screenshot
baseline_rates = {
    'A': {'rec_rate': 1.27, 'churn_rate': 0.15, 'net_rate': 1.12},
    'AC': {'rec_rate': 0.28, 'churn_rate': 0.14, 'net_rate': 0.14},
    'AM': {'rec_rate': 0.00, 'churn_rate': 0.04, 'net_rate': -0.04},
    'C': {'rec_rate': 0.04, 'churn_rate': 0.08, 'net_rate': -0.04},
    'M': {'rec_rate': 0.00, 'churn_rate': 0.07, 'net_rate': -0.07},
    'PiP': {'rec_rate': 0.00, 'churn_rate': 0.00, 'net_rate': 0.00},
    'SrC': {'rec_rate': 0.01, 'churn_rate': 0.05, 'net_rate': -0.04},
    'SrM': {'rec_rate': 0.00, 'churn_rate': 0.10, 'net_rate': -0.10}
}

print("Expected vs Actual Growth (based on baseline rates):")
print("Level | Baseline Net | Expected 5Y | New Actual | Old Actual | New vs Exp | Old vs Exp")
print("------|--------------|-------------|------------|------------|------------|------------")

for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    net_monthly_rate = baseline_rates[level]['net_rate']
    
    # Calculate expected growth over 5 years with baseline rate
    expected_5y = ((1 + net_monthly_rate/100) ** 60 - 1) * 100  # 60 months
    
    new_actual = new_sim[level]['growth']
    old_actual_5y = ((old_sim[level]['end'] / old_sim[level]['start']) ** (5/6) - 1) * 100
    
    new_vs_exp = new_actual - expected_5y
    old_vs_exp = old_actual_5y - expected_5y
    
    print(f"{level:5} | {net_monthly_rate:12.2f}% | {expected_5y:11.1f}% | {new_actual:10.1f}% | {old_actual_5y:10.1f}% | {new_vs_exp:10.1f}% | {old_vs_exp:10.1f}%")

print("\n4. CONSISTENCY ANALYSIS:")
print("========================")

# Check which simulation is more consistent with baseline expectations
new_total_deviation = 0
old_total_deviation = 0

print("Deviation from baseline expectations:")
print("Level | New Dev | Old Dev | More Consistent")
print("------|---------|---------|----------------")

for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    net_monthly_rate = baseline_rates[level]['net_rate']
    expected_5y = ((1 + net_monthly_rate/100) ** 60 - 1) * 100
    
    new_actual = new_sim[level]['growth']
    old_actual_5y = ((old_sim[level]['end'] / old_sim[level]['start']) ** (5/6) - 1) * 100
    
    new_dev = abs(new_actual - expected_5y)
    old_dev = abs(old_actual_5y - expected_5y)
    
    new_total_deviation += new_dev
    old_total_deviation += old_dev
    
    more_consistent = "New" if new_dev < old_dev else "Old"
    
    print(f"{level:5} | {new_dev:7.1f}% | {old_dev:7.1f}% | {more_consistent}")

print("------|---------|---------|----------------")
print(f"TOTAL | {new_total_deviation:7.1f}% | {old_total_deviation:7.1f}% | {'New' if new_total_deviation < old_total_deviation else 'Old'}")

print("\n5. CRITICAL ISSUES IDENTIFIED:")
print("==============================")

critical_issues = []

# Issue 1: Major discrepancies
if len(major_discrepancies) > 0:
    critical_issues.append(f"Major discrepancies in {len(major_discrepancies)} levels: {', '.join(major_discrepancies)}")

# Issue 2: Pattern reversals
if len(pattern_reversals) > 0:
    critical_issues.append(f"Growth pattern reversals in {len(pattern_reversals)} levels: {', '.join(pattern_reversals)}")

# Issue 3: Total discrepancy magnitude
if total_discrepancy > 100:
    critical_issues.append(f"Excessive total discrepancy: {total_discrepancy:.1f} percentage points")

# Issue 4: Inconsistency with baseline
baseline_inconsistency = min(new_total_deviation, old_total_deviation)
if baseline_inconsistency > 50:
    critical_issues.append(f"Both simulations deviate significantly from baseline expectations")

print("Critical Issues Found:")
for i, issue in enumerate(critical_issues, 1):
    print(f"{i}. {issue}")

print("\n6. ROOT CAUSE HYPOTHESES:")
print("=========================")

hypotheses = [
    "Random seed differences: Simulations using different random number seeds",
    "Parameter drift: Simulation parameters changing between runs",
    "Version differences: Different versions of simulation engine used",
    "Configuration errors: Different simulation configurations applied",
    "Data corruption: Input data corrupted or modified between runs",
    "Timing issues: Race conditions or timing-dependent calculations",
    "Memory issues: Memory corruption affecting calculation accuracy",
    "Floating point errors: Accumulating numerical precision errors",
    "Logic bugs: Conditional logic behaving differently under different conditions",
    "External dependencies: Different external data or services used"
]

print("Most likely root causes (in order of probability):")
for i, hypothesis in enumerate(hypotheses, 1):
    print(f"{i:2}. {hypothesis}")

print("\n7. IMPACT ASSESSMENT:")
print("====================")

print("Business Impact of Simulation Inconsistency:")
print("- Strategic Planning: Cannot rely on simulation for long-term planning")
print("- Resource Allocation: Uncertain recruitment and capacity needs")
print("- Financial Forecasting: Revenue projections unreliable")
print("- Risk Management: Cannot assess growth scenarios accurately")
print("- Stakeholder Confidence: Credibility of modeling approach compromised")

print(f"\nReliability Assessment: FAILED")
print(f"Recommendation: STOP using simulation until root cause identified and fixed")

print(f"\nAnalysis complete. The simulation engine shows critical reliability issues.")
print(f"Same inputs are producing significantly different outputs, making it unsuitable for business use.")

