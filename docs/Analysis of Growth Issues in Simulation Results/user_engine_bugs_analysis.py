import json
import pandas as pd
import numpy as np

print("=== USER'S ENGINE BUG ANALYSIS ===")
print()

# Load user's simulation data
with open('/home/ubuntu/upload/simulation_results_20250630_161229.json', 'r') as f:
    user_data = json.load(f)

# Baseline parameters from the original screenshot
baseline_params = {
    'A': {'fte': 163, 'rec_per_month': 2.076, 'churn_per_month': 0.238, 'rec_rate': 1.27, 'churn_rate': 0.15},
    'AC': {'fte': 231, 'rec_per_month': 0.636, 'churn_per_month': 0.318, 'rec_rate': 0.28, 'churn_rate': 0.14},
    'AM': {'fte': 418, 'rec_per_month': 0.011, 'churn_per_month': 0.168, 'rec_rate': 0.00, 'churn_rate': 0.04},
    'C': {'fte': 356, 'rec_per_month': 0.155, 'churn_per_month': 0.276, 'rec_rate': 0.04, 'churn_rate': 0.08},
    'M': {'fte': 156, 'rec_per_month': 0.000, 'churn_per_month': 0.112, 'rec_rate': 0.00, 'churn_rate': 0.07},
    'PiP': {'fte': 43, 'rec_per_month': 0.000, 'churn_per_month': 0.000, 'rec_rate': 0.00, 'churn_rate': 0.00},
    'SrC': {'fte': 409, 'rec_per_month': 0.032, 'churn_per_month': 0.206, 'rec_rate': 0.01, 'churn_rate': 0.05},
    'SrM': {'fte': 66, 'rec_per_month': 0.000, 'churn_per_month': 0.066, 'rec_rate': 0.00, 'churn_rate': 0.10}
}

# Claude AI results for comparison
claude_results = {
    'A': {'end': 318, 'growth': 95.1},
    'AC': {'end': 251, 'growth': 8.7},
    'AM': {'end': 408, 'growth': -2.4},
    'C': {'end': 348, 'growth': -2.2},
    'M': {'end': 150, 'growth': -3.8},
    'PiP': {'end': 43, 'growth': 0.0},
    'SrC': {'end': 399, 'growth': -2.4},
    'SrM': {'end': 62, 'growth': -6.1}
}

print("1. ANALYZING USER'S ENGINE RECRUITMENT/CHURN PATTERNS:")
print("======================================================")

# Calculate actual recruitment and churn rates from user's data
user_patterns = {}

for year, year_data in user_data['years'].items():
    for office, office_data in year_data['offices'].items():
        for role, role_data in office_data['levels'].items():
            if isinstance(role_data, dict):
                for level, level_data in role_data.items():
                    if level not in user_patterns:
                        user_patterns[level] = {
                            'total_recruited': 0,
                            'total_churned': 0,
                            'total_fte_months': 0,
                            'months': 0
                        }
                    
                    for month_data in level_data:
                        user_patterns[level]['total_recruited'] += month_data['recruited']
                        user_patterns[level]['total_churned'] += month_data['churned']
                        user_patterns[level]['total_fte_months'] += month_data['total']
                        user_patterns[level]['months'] += 1

# Calculate averages
for level in user_patterns:
    months = user_patterns[level]['months']
    user_patterns[level]['avg_recruited_per_month'] = user_patterns[level]['total_recruited'] / months
    user_patterns[level]['avg_churned_per_month'] = user_patterns[level]['total_churned'] / months
    user_patterns[level]['avg_fte'] = user_patterns[level]['total_fte_months'] / months
    
    # Calculate rates
    avg_fte = user_patterns[level]['avg_fte']
    user_patterns[level]['actual_rec_rate'] = (user_patterns[level]['avg_recruited_per_month'] / avg_fte * 100) if avg_fte > 0 else 0
    user_patterns[level]['actual_churn_rate'] = (user_patterns[level]['avg_churned_per_month'] / avg_fte * 100) if avg_fte > 0 else 0

print("User's Engine Actual vs Expected Recruitment/Churn:")
print("Level | Expected Rec/Mo | Actual Rec/Mo | Diff | Expected Churn/Mo | Actual Churn/Mo | Diff")
print("------|-----------------|---------------|------|-------------------|-----------------|------")

for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    if level in baseline_params and level in user_patterns:
        expected_rec = baseline_params[level]['rec_per_month']
        actual_rec = user_patterns[level]['avg_recruited_per_month']
        rec_diff = actual_rec - expected_rec
        
        expected_churn = baseline_params[level]['churn_per_month']
        actual_churn = user_patterns[level]['avg_churned_per_month']
        churn_diff = actual_churn - expected_churn
        
        print(f"{level:5} | {expected_rec:15.3f} | {actual_rec:13.3f} | {rec_diff:4.3f} | {expected_churn:17.3f} | {actual_churn:15.3f} | {churn_diff:4.3f}")

print("\n2. IDENTIFYING SPECIFIC BUGS:")
print("=============================")

bugs_found = []

print("Bug Analysis by Level:")
for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    if level in baseline_params and level in user_patterns and level in claude_results:
        print(f"\nLevel {level} Analysis:")
        print("-" * 20)
        
        # Expected values
        expected_rec = baseline_params[level]['rec_per_month']
        expected_churn = baseline_params[level]['churn_per_month']
        expected_net = expected_rec - expected_churn
        
        # User's actual values
        actual_rec = user_patterns[level]['avg_recruited_per_month']
        actual_churn = user_patterns[level]['avg_churned_per_month']
        actual_net = actual_rec - actual_churn
        
        # Claude's implied values (working backwards from results)
        start_fte = baseline_params[level]['fte']
        claude_end = claude_results[level]['end']
        claude_growth = claude_results[level]['growth']
        
        # Calculate what Claude's monthly net should be
        claude_monthly_net = (claude_end - start_fte) / 60  # 60 months
        
        print(f"Expected monthly net: {expected_net:.3f}")
        print(f"User's actual net: {actual_net:.3f}")
        print(f"Claude's implied net: {claude_monthly_net:.3f}")
        
        # Identify specific issues
        rec_error = abs(actual_rec - expected_rec)
        churn_error = abs(actual_churn - expected_churn)
        
        if rec_error > 0.1:
            if actual_rec > expected_rec:
                bugs_found.append(f"Level {level}: Over-recruitment by {rec_error:.3f} FTE/month")
            else:
                bugs_found.append(f"Level {level}: Under-recruitment by {rec_error:.3f} FTE/month")
        
        if churn_error > 0.1:
            if actual_churn > expected_churn:
                bugs_found.append(f"Level {level}: Over-churn by {churn_error:.3f} FTE/month")
            else:
                bugs_found.append(f"Level {level}: Under-churn by {churn_error:.3f} FTE/month")
        
        # Check if the net effect explains the growth difference
        user_end_fte = start_fte + (actual_net * 60)  # 60 months
        user_growth_calc = ((user_end_fte / start_fte) - 1) * 100
        
        print(f"User's calculated end FTE: {user_end_fte:.1f}")
        print(f"User's calculated growth: {user_growth_calc:.1f}%")
        print(f"Claude's actual growth: {claude_growth:.1f}%")
        print(f"Growth difference: {user_growth_calc - claude_growth:.1f}pp")

print(f"\n3. SUMMARY OF BUGS FOUND:")
print("=========================")

if bugs_found:
    print("Specific bugs identified in user's engine:")
    for i, bug in enumerate(bugs_found, 1):
        print(f"{i}. {bug}")
else:
    print("No major recruitment/churn bugs found at the absolute number level.")

print("\n4. RATE-BASED BUG ANALYSIS:")
print("===========================")

print("Comparing actual vs expected rates:")
print("Level | Expected Rec% | Actual Rec% | Diff | Expected Churn% | Actual Churn% | Diff")
print("------|---------------|-------------|------|-----------------|---------------|------")

rate_bugs = []

for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    if level in baseline_params and level in user_patterns:
        expected_rec_rate = baseline_params[level]['rec_rate']
        actual_rec_rate = user_patterns[level]['actual_rec_rate']
        rec_rate_diff = actual_rec_rate - expected_rec_rate
        
        expected_churn_rate = baseline_params[level]['churn_rate']
        actual_churn_rate = user_patterns[level]['actual_churn_rate']
        churn_rate_diff = actual_churn_rate - expected_churn_rate
        
        print(f"{level:5} | {expected_rec_rate:13.2f}% | {actual_rec_rate:11.2f}% | {rec_rate_diff:4.2f}% | {expected_churn_rate:15.2f}% | {actual_churn_rate:13.2f}% | {churn_rate_diff:4.2f}%")
        
        # Identify rate-based bugs
        if abs(rec_rate_diff) > 0.5:  # More than 0.5% difference
            rate_bugs.append(f"Level {level}: Recruitment rate off by {rec_rate_diff:+.2f}%")
        
        if abs(churn_rate_diff) > 0.5:  # More than 0.5% difference
            rate_bugs.append(f"Level {level}: Churn rate off by {churn_rate_diff:+.2f}%")

print(f"\nRate-based bugs found:")
if rate_bugs:
    for i, bug in enumerate(rate_bugs, 1):
        print(f"{i}. {bug}")
else:
    print("No significant rate-based bugs found.")

print("\n5. ROOT CAUSE ANALYSIS:")
print("=======================")

# Analyze patterns to identify root causes
print("Analyzing patterns to identify root causes...")

# Check for systematic issues
total_rec_error = sum(abs(user_patterns[level]['avg_recruited_per_month'] - baseline_params[level]['rec_per_month']) 
                     for level in baseline_params if level in user_patterns)

total_churn_error = sum(abs(user_patterns[level]['avg_churned_per_month'] - baseline_params[level]['churn_per_month']) 
                       for level in baseline_params if level in user_patterns)

print(f"Total recruitment error: {total_rec_error:.3f} FTE/month")
print(f"Total churn error: {total_churn_error:.3f} FTE/month")

# Identify the most problematic levels
problem_levels = []
for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    if level in baseline_params and level in user_patterns and level in claude_results:
        start_fte = baseline_params[level]['fte']
        claude_growth = claude_results[level]['growth']
        
        # Calculate user's actual growth
        actual_rec = user_patterns[level]['avg_recruited_per_month']
        actual_churn = user_patterns[level]['avg_churned_per_month']
        actual_net = actual_rec - actual_churn
        user_end_fte = start_fte + (actual_net * 60)
        user_growth = ((user_end_fte / start_fte) - 1) * 100
        
        growth_error = abs(user_growth - claude_growth)
        if growth_error > 20:  # More than 20% difference
            problem_levels.append((level, growth_error, user_growth, claude_growth))

problem_levels.sort(key=lambda x: x[1], reverse=True)  # Sort by error magnitude

print(f"\nMost problematic levels (>20% growth difference):")
for level, error, user_growth, claude_growth in problem_levels:
    print(f"- Level {level}: {error:.1f}pp difference (User: {user_growth:.1f}%, Claude: {claude_growth:.1f}%)")

print("\n6. LIKELY ROOT CAUSES:")
print("======================")

root_causes = [
    "Parameter scaling issues: Baseline parameters may not be properly scaled in user's engine",
    "Calculation logic errors: Recruitment/churn calculations may have bugs",
    "Compounding errors: Small errors accumulating over 60 months",
    "Rate vs absolute number confusion: Engine may be mixing percentage rates with absolute numbers",
    "Population growth feedback: Engine may not be adjusting recruitment/churn as population grows",
    "Rounding or precision errors: Floating point arithmetic issues",
    "Time step calculation errors: Monthly calculations may be incorrect",
    "Level-specific parameter bugs: Different levels may have different calculation errors"
]

print("Most likely root causes (in order of probability):")
for i, cause in enumerate(root_causes, 1):
    print(f"{i}. {cause}")

print("\n7. RECOMMENDED DEBUGGING STEPS:")
print("===============================")

debug_steps = [
    "Verify parameter input: Check if baseline parameters are correctly loaded",
    "Test single level: Run simulation for one level only to isolate issues",
    "Check calculation order: Verify recruitment happens before churn (or vice versa)",
    "Validate monthly calculations: Ensure monthly growth is calculated correctly",
    "Test with simple parameters: Use round numbers to verify calculation logic",
    "Compare month-by-month: Check if errors accumulate over time",
    "Verify population updates: Ensure FTE count is updated after each recruitment/churn",
    "Check for off-by-one errors: Verify array indexing and loop boundaries"
]

print("Recommended debugging approach:")
for i, step in enumerate(debug_steps, 1):
    print(f"{i}. {step}")

print(f"\nAnalysis complete. User's engine has significant calculation errors that need debugging.")

