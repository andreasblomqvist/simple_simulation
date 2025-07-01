import json
import pandas as pd
import numpy as np

# Load the simulation data
with open('/home/ubuntu/upload/simulation_results_20250630_161229.json', 'r') as f:
    data = json.load(f)

print("=== DETAILED ABSOLUTE NUMBERS ANALYSIS ===")
print()

# Baseline absolute numbers from screenshot
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

# Calculate simulation results
simulation_results = {}
for year, year_data in data['years'].items():
    for office, office_data in year_data['offices'].items():
        for role, role_data in office_data['levels'].items():
            if isinstance(role_data, dict):
                for level, level_data in role_data.items():
                    if level not in simulation_results:
                        simulation_results[level] = {
                            'total_recruited': 0, 
                            'total_churned': 0,
                            'months': 0
                        }
                    
                    for month_data in level_data:
                        simulation_results[level]['total_recruited'] += month_data['recruited']
                        simulation_results[level]['total_churned'] += month_data['churned']
                        simulation_results[level]['months'] += 1

# Calculate averages
for level in simulation_results:
    months = simulation_results[level]['months']
    simulation_results[level]['avg_recruited_per_month'] = simulation_results[level]['total_recruited'] / months
    simulation_results[level]['avg_churned_per_month'] = simulation_results[level]['total_churned'] / months

print("1. BASELINE VS SIMULATION COMPARISON:")
print("====================================")

comparison_data = []
total_baseline_rec = 0
total_simulation_rec = 0
total_baseline_churn = 0
total_simulation_churn = 0

print("Level | Baseline Rec | Simulation Rec | Difference | % Diff | Baseline Churn | Simulation Churn | Difference | % Diff")
print("------|--------------|----------------|------------|--------|----------------|------------------|------------|--------")

for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    if level in baseline_absolute and level in simulation_results:
        baseline = baseline_absolute[level]
        sim = simulation_results[level]
        
        baseline_rec = baseline['recruitment_per_month']
        sim_rec = sim['avg_recruited_per_month']
        rec_diff = sim_rec - baseline_rec
        rec_pct_diff = (rec_diff / baseline_rec * 100) if baseline_rec > 0 else 0
        
        baseline_churn = baseline['churn_per_month']
        sim_churn = sim['avg_churned_per_month']
        churn_diff = sim_churn - baseline_churn
        churn_pct_diff = (churn_diff / baseline_churn * 100) if baseline_churn > 0 else 0
        
        print(f"{level:5} | {baseline_rec:12.3f} | {sim_rec:14.3f} | {rec_diff:10.3f} | {rec_pct_diff:6.1f}% | {baseline_churn:14.3f} | {sim_churn:16.3f} | {churn_diff:10.3f} | {churn_pct_diff:6.1f}%")
        
        total_baseline_rec += baseline_rec
        total_simulation_rec += sim_rec
        total_baseline_churn += baseline_churn
        total_simulation_churn += sim_churn
        
        comparison_data.append({
            'Level': level,
            'Baseline_Rec': baseline_rec,
            'Simulation_Rec': sim_rec,
            'Rec_Difference': rec_diff,
            'Rec_Pct_Diff': rec_pct_diff,
            'Baseline_Churn': baseline_churn,
            'Simulation_Churn': sim_churn,
            'Churn_Difference': churn_diff,
            'Churn_Pct_Diff': churn_pct_diff
        })

print("------|--------------|----------------|------------|--------|----------------|------------------|------------|--------")
total_rec_diff = total_simulation_rec - total_baseline_rec
total_churn_diff = total_simulation_churn - total_baseline_churn
total_rec_pct = (total_rec_diff / total_baseline_rec * 100) if total_baseline_rec > 0 else 0
total_churn_pct = (total_churn_diff / total_baseline_churn * 100) if total_baseline_churn > 0 else 0

print(f"TOTAL | {total_baseline_rec:12.3f} | {total_simulation_rec:14.3f} | {total_rec_diff:10.3f} | {total_rec_pct:6.1f}% | {total_baseline_churn:14.3f} | {total_simulation_churn:16.3f} | {total_churn_diff:10.3f} | {total_churn_pct:6.1f}%")

print("\n2. SIGNIFICANCE ASSESSMENT:")
print("===========================")

# Define significance thresholds
significant_absolute_threshold = 0.1  # 0.1 FTE/month
significant_percentage_threshold = 20  # 20%

significant_issues = []
minor_issues = []

for item in comparison_data:
    level = item['Level']
    
    # Check recruitment significance
    if abs(item['Rec_Difference']) > significant_absolute_threshold:
        if abs(item['Rec_Pct_Diff']) > significant_percentage_threshold:
            significant_issues.append(f"{level}: Recruitment differs by {item['Rec_Difference']:+.3f} FTE/month ({item['Rec_Pct_Diff']:+.1f}%)")
        else:
            minor_issues.append(f"{level}: Recruitment differs by {item['Rec_Difference']:+.3f} FTE/month ({item['Rec_Pct_Diff']:+.1f}%)")
    
    # Check churn significance
    if abs(item['Churn_Difference']) > significant_absolute_threshold:
        if abs(item['Churn_Pct_Diff']) > significant_percentage_threshold:
            significant_issues.append(f"{level}: Churn differs by {item['Churn_Difference']:+.3f} FTE/month ({item['Churn_Pct_Diff']:+.1f}%)")
        else:
            minor_issues.append(f"{level}: Churn differs by {item['Churn_Difference']:+.3f} FTE/month ({item['Churn_Pct_Diff']:+.1f}%)")

print("Significant Issues (>0.1 FTE/month AND >20% difference):")
if significant_issues:
    for issue in significant_issues:
        print(f"  ⚠️  {issue}")
else:
    print("  ✅ No significant issues found")

print("\nMinor Issues (>0.1 FTE/month but <20% difference):")
if minor_issues:
    for issue in minor_issues:
        print(f"  ℹ️  {issue}")
else:
    print("  ✅ No minor issues found")

print("\n3. PATTERN ANALYSIS:")
print("===================")

# Analyze patterns in the differences
rec_differences = [item['Rec_Difference'] for item in comparison_data]
churn_differences = [item['Churn_Difference'] for item in comparison_data]

print(f"Recruitment differences - Mean: {np.mean(rec_differences):.3f}, Std: {np.std(rec_differences):.3f}")
print(f"Churn differences - Mean: {np.mean(churn_differences):.3f}, Std: {np.std(churn_differences):.3f}")

# Check for systematic bias
if np.mean(rec_differences) > 0.05:
    print("⚠️  Systematic over-recruitment detected")
elif np.mean(rec_differences) < -0.05:
    print("⚠️  Systematic under-recruitment detected")
else:
    print("✅ No systematic recruitment bias")

if np.mean(churn_differences) > 0.05:
    print("⚠️  Systematic over-churn detected")
elif np.mean(churn_differences) < -0.05:
    print("⚠️  Systematic under-churn detected")
else:
    print("✅ No systematic churn bias")

print("\n4. IMPACT ON GROWTH:")
print("====================")

# Calculate net impact on growth
baseline_net_growth = total_baseline_rec - total_baseline_churn
simulation_net_growth = total_simulation_rec - total_simulation_churn
net_growth_difference = simulation_net_growth - baseline_net_growth

print(f"Baseline net growth: {baseline_net_growth:+.3f} FTE/month")
print(f"Simulation net growth: {simulation_net_growth:+.3f} FTE/month")
print(f"Net growth difference: {net_growth_difference:+.3f} FTE/month")

if abs(net_growth_difference) > 0.1:
    print(f"⚠️  Net growth differs by {net_growth_difference:+.3f} FTE/month from baseline")
else:
    print("✅ Net growth is consistent with baseline")

print("\n5. OVERALL ASSESSMENT:")
print("======================")

# Overall assessment
total_absolute_error = sum(abs(item['Rec_Difference']) + abs(item['Churn_Difference']) for item in comparison_data)
average_absolute_error = total_absolute_error / (len(comparison_data) * 2)

print(f"Total absolute error: {total_absolute_error:.3f} FTE/month")
print(f"Average absolute error: {average_absolute_error:.3f} FTE/month per metric")

if average_absolute_error < 0.05:
    print("✅ EXCELLENT: Simulation closely matches baseline parameters")
elif average_absolute_error < 0.1:
    print("✅ GOOD: Simulation reasonably matches baseline parameters")
elif average_absolute_error < 0.2:
    print("⚠️  FAIR: Simulation has some deviations from baseline")
else:
    print("❌ POOR: Simulation significantly deviates from baseline")

print("\n6. RECOMMENDATIONS:")
print("==================")

if len(significant_issues) == 0 and average_absolute_error < 0.1:
    print("✅ The simulation appears to be working correctly.")
    print("✅ Recruitment and churn numbers are close to baseline parameters.")
    print("✅ Any growth observed is due to the natural net difference between recruitment and churn.")
    print("✅ Results can be used for business planning with confidence.")
else:
    print("⚠️  Some discrepancies found that may need investigation:")
    if len(significant_issues) > 0:
        print("   - Address significant issues listed above")
    if abs(net_growth_difference) > 0.1:
        print("   - Investigate why net growth differs from expected")
    print("   - Consider calibrating the simulation parameters")
    print("   - Validate the simulation logic for affected levels")

# Save detailed results
comparison_df = pd.DataFrame(comparison_data)
comparison_df.to_csv('/home/ubuntu/corrected_absolute_comparison.csv', index=False)
print(f"\nDetailed comparison saved to: /home/ubuntu/corrected_absolute_comparison.csv")

