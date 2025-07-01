import json
import pandas as pd

# Load the simulation data
with open('/home/ubuntu/upload/simulation_results_20250630_161229.json', 'r') as f:
    data = json.load(f)

print("=== CORRECTED ANALYSIS: ABSOLUTE NUMBERS COMPARISON ===")
print()

# Baseline ABSOLUTE numbers from screenshot (FTE/month columns)
baseline_absolute = {
    'A': {'fte': 163.0, 'recruitment_per_month': 2.076, 'churn_per_month': 0.238},
    'AC': {'fte': 231.0, 'recruitment_per_month': 0.636, 'churn_per_month': 0.318},
    'AM': {'fte': 418.0, 'recruitment_per_month': 0.011, 'churn_per_month': 0.168},
    'C': {'fte': 356.0, 'recruitment_per_month': 0.155, 'churn_per_month': 0.276},
    'M': {'fte': 156.0, 'recruitment_per_month': 0.000, 'churn_per_month': 0.112},
    'PiP': {'fte': 43.0, 'recruitment_per_month': 0.000, 'churn_per_month': 0.000},
    'SrC': {'fte': 409.0, 'recruitment_per_month': 0.032, 'churn_per_month': 0.206},
    'SrM': {'fte': 66.0, 'recruitment_per_month': 0.000, 'churn_per_month': 0.066}
}

# Baseline percentage rates from screenshot (%/month columns)
baseline_rates = {
    'A': {'recruitment_pct': 1.27, 'churn_pct': 0.15},
    'AC': {'recruitment_pct': 0.28, 'churn_pct': 0.14},
    'AM': {'recruitment_pct': 0.00, 'churn_pct': 0.04},
    'C': {'recruitment_pct': 0.04, 'churn_pct': 0.08},
    'M': {'recruitment_pct': 0.00, 'churn_pct': 0.07},
    'PiP': {'recruitment_pct': 0.00, 'churn_pct': 0.00},
    'SrC': {'recruitment_pct': 0.01, 'churn_pct': 0.05},
    'SrM': {'recruitment_pct': 0.00, 'churn_pct': 0.10}
}

print("1. BASELINE VALUES FROM SCREENSHOT:")
print("===================================")
print("Absolute Numbers (FTE/month):")
for level, data in baseline_absolute.items():
    print(f"{level}: {data['fte']} FTE, {data['recruitment_per_month']} recruited/month, {data['churn_per_month']} churned/month")

print("\nPercentage Rates (%/month):")
for level, data in baseline_rates.items():
    print(f"{level}: {data['recruitment_pct']:.2f}% recruitment rate, {data['churn_pct']:.2f}% churn rate")

print("\n2. SIMULATION RESULTS ANALYSIS:")
print("===============================")

# Calculate actual results from simulation
simulation_results = {}
for year, year_data in data['years'].items():
    for office, office_data in year_data['offices'].items():
        for role, role_data in office_data['levels'].items():
            if isinstance(role_data, dict):
                for level, level_data in role_data.items():
                    if level not in simulation_results:
                        simulation_results[level] = {
                            'total_fte': 0, 
                            'total_recruited': 0, 
                            'total_churned': 0,
                            'months': 0
                        }
                    
                    # Sum across all months and offices
                    for month_data in level_data:
                        simulation_results[level]['total_fte'] += month_data['total']
                        simulation_results[level]['total_recruited'] += month_data['recruited']
                        simulation_results[level]['total_churned'] += month_data['churned']
                        simulation_results[level]['months'] += 1

# Calculate averages
for level in simulation_results:
    months = simulation_results[level]['months']
    simulation_results[level]['avg_fte'] = simulation_results[level]['total_fte'] / months
    simulation_results[level]['avg_recruited_per_month'] = simulation_results[level]['total_recruited'] / months
    simulation_results[level]['avg_churned_per_month'] = simulation_results[level]['total_churned'] / months
    
    # Calculate rates
    avg_fte = simulation_results[level]['avg_fte']
    simulation_results[level]['recruitment_rate'] = (simulation_results[level]['avg_recruited_per_month'] / avg_fte * 100) if avg_fte > 0 else 0
    simulation_results[level]['churn_rate'] = (simulation_results[level]['avg_churned_per_month'] / avg_fte * 100) if avg_fte > 0 else 0

print("Simulation Average Results:")
for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    if level in simulation_results:
        sim = simulation_results[level]
        print(f"{level}: {sim['avg_fte']:.1f} FTE, {sim['avg_recruited_per_month']:.3f} recruited/month, {sim['avg_churned_per_month']:.3f} churned/month")
        print(f"     Rates: {sim['recruitment_rate']:.2f}% recruitment, {sim['churn_rate']:.2f}% churn")

print("\n3. ABSOLUTE NUMBERS COMPARISON:")
print("===============================")

comparison_results = []
print("Level | Baseline Rec/Month | Simulation Rec/Month | Difference | Baseline Churn/Month | Simulation Churn/Month | Difference")
print("------|-------------------|---------------------|------------|---------------------|----------------------|------------")

for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    if level in baseline_absolute and level in simulation_results:
        baseline = baseline_absolute[level]
        sim = simulation_results[level]
        
        rec_diff = sim['avg_recruited_per_month'] - baseline['recruitment_per_month']
        churn_diff = sim['avg_churned_per_month'] - baseline['churn_per_month']
        
        print(f"{level:5} | {baseline['recruitment_per_month']:17.3f} | {sim['avg_recruited_per_month']:19.3f} | {rec_diff:10.3f} | {baseline['churn_per_month']:19.3f} | {sim['avg_churned_per_month']:20.3f} | {churn_diff:10.3f}")
        
        comparison_results.append({
            'Level': level,
            'Baseline_Rec': baseline['recruitment_per_month'],
            'Simulation_Rec': sim['avg_recruited_per_month'],
            'Rec_Difference': rec_diff,
            'Baseline_Churn': baseline['churn_per_month'],
            'Simulation_Churn': sim['avg_churned_per_month'],
            'Churn_Difference': churn_diff
        })

print("\n4. RATE CONSISTENCY CHECK:")
print("==========================")

print("Level | Baseline Rate% | Simulation Rate% | Expected Absolute | Actual Absolute | Issue?")
print("------|---------------|------------------|------------------|-----------------|--------")

for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    if level in baseline_rates and level in simulation_results:
        baseline_rate = baseline_rates[level]
        sim = simulation_results[level]
        
        # Check recruitment rate consistency
        expected_rec_absolute = (baseline_rate['recruitment_pct'] / 100) * sim['avg_fte']
        actual_rec_absolute = sim['avg_recruited_per_month']
        rec_issue = abs(expected_rec_absolute - actual_rec_absolute) > 0.1
        
        print(f"{level:5} | Rec: {baseline_rate['recruitment_pct']:6.2f}% | Rec: {sim['recruitment_rate']:10.2f}% | {expected_rec_absolute:15.3f} | {actual_rec_absolute:14.3f} | {'YES' if rec_issue else 'NO'}")
        
        # Check churn rate consistency  
        expected_churn_absolute = (baseline_rate['churn_pct'] / 100) * sim['avg_fte']
        actual_churn_absolute = sim['avg_churned_per_month']
        churn_issue = abs(expected_churn_absolute - actual_churn_absolute) > 0.1
        
        print(f"      | Churn: {baseline_rate['churn_pct']:5.2f}% | Churn: {sim['churn_rate']:9.2f}% | {expected_churn_absolute:15.3f} | {actual_churn_absolute:14.3f} | {'YES' if churn_issue else 'NO'}")

print("\n5. SUMMARY OF FINDINGS:")
print("=======================")

# Check if the simulation is maintaining the baseline absolute numbers
total_rec_diff = sum(abs(r['Rec_Difference']) for r in comparison_results)
total_churn_diff = sum(abs(r['Churn_Difference']) for r in comparison_results)

print(f"Total absolute recruitment difference: {total_rec_diff:.3f} FTE/month")
print(f"Total absolute churn difference: {total_churn_diff:.3f} FTE/month")

# Identify levels with significant differences
significant_issues = []
for result in comparison_results:
    level = result['Level']
    if abs(result['Rec_Difference']) > 0.1:
        significant_issues.append(f"{level}: Recruitment off by {result['Rec_Difference']:+.3f} FTE/month")
    if abs(result['Churn_Difference']) > 0.1:
        significant_issues.append(f"{level}: Churn off by {result['Churn_Difference']:+.3f} FTE/month")

if significant_issues:
    print("\nSignificant discrepancies found:")
    for issue in significant_issues:
        print(f"- {issue}")
else:
    print("\nNo significant discrepancies found in absolute numbers.")

print("\n6. CONCLUSION:")
print("==============")

if total_rec_diff < 1.0 and total_churn_diff < 1.0:
    print("✓ The simulation appears to be maintaining baseline absolute recruitment and churn numbers correctly.")
    print("✓ Any growth in the organization is coming from the net difference between recruitment and churn.")
    print("✓ The simulation logic appears to be working as intended.")
else:
    print("✗ The simulation is NOT maintaining baseline absolute numbers correctly.")
    print("✗ There are significant discrepancies that need investigation.")
    print("✗ The simulation may have bugs in its recruitment/churn logic.")

# Save detailed comparison
comparison_df = pd.DataFrame(comparison_results)
comparison_df.to_csv('/home/ubuntu/absolute_numbers_comparison.csv', index=False)
print(f"\nDetailed comparison saved to: /home/ubuntu/absolute_numbers_comparison.csv")

