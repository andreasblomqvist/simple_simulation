import json
import pandas as pd
import numpy as np

# Load the simulation data
with open('/home/ubuntu/upload/simulation_results_20250630_161229.json', 'r') as f:
    data = json.load(f)

print("=== REAL ISSUES ANALYSIS ===")
print()

# Based on the previous analysis, we identified these key issues:
# 1. Systematic under-recruitment (-34.9% overall)
# 2. Net growth 49% lower than expected (-0.754 FTE/month difference)
# 3. Specific levels with major deviations (A, AC, AM, C)

print("1. IDENTIFIED ISSUES SUMMARY:")
print("============================")

issues_identified = [
    "Level A: 52% under-recruitment and under-churn",
    "Level AC: 30% over-recruitment and over-churn", 
    "Level AM: 74% over-churn (recruitment close to baseline)",
    "Level C: 73% under-recruitment and 71% under-churn",
    "Level SrM: 86% under-churn",
    "Overall: 35% under-recruitment, 19% under-churn",
    "Net growth: 49% lower than baseline expectation"
]

for i, issue in enumerate(issues_identified, 1):
    print(f"{i}. {issue}")

print("\n2. ROOT CAUSE ANALYSIS:")
print("=======================")

# Let's analyze the data more deeply to understand why these discrepancies exist

# Check if it's a data aggregation issue
print("Checking data aggregation...")

# Count total data points and see if we're missing data
total_data_points = 0
level_counts = {}

for year, year_data in data['years'].items():
    for office, office_data in year_data['offices'].items():
        for role, role_data in office_data['levels'].items():
            if isinstance(role_data, dict):
                for level, level_data in role_data.items():
                    if level not in level_counts:
                        level_counts[level] = 0
                    level_counts[level] += len(level_data)
                    total_data_points += len(level_data)

print(f"Total data points analyzed: {total_data_points:,}")
print("Data points per level:")
for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    if level in level_counts:
        print(f"  {level}: {level_counts[level]:,} data points")

# Expected data points: 6 years × 12 months × 12 offices × 4 roles = 3,456 per level
expected_per_level = 6 * 12 * 12 * 4  # But not all roles have all levels
print(f"Expected data points per level (if all roles had all levels): {expected_per_level:,}")

print("\n3. TEMPORAL ANALYSIS:")
print("=====================")

# Check if the issues are consistent over time or getting worse/better
print("Analyzing trends over time...")

# Sample Level A to see if recruitment/churn changes over time
level_a_monthly = []
for year, year_data in data['years'].items():
    for office, office_data in year_data['offices'].items():
        for role, role_data in office_data['levels'].items():
            if isinstance(role_data, dict) and 'A' in role_data:
                for month_idx, month_data in enumerate(role_data['A']):
                    level_a_monthly.append({
                        'Year': int(year),
                        'Month': month_idx + 1,
                        'Office': office,
                        'Role': role,
                        'Recruited': month_data['recruited'],
                        'Churned': month_data['churned'],
                        'FTE': month_data['total']
                    })

if level_a_monthly:
    df_a = pd.DataFrame(level_a_monthly)
    
    # Group by year to see trends
    yearly_trends = df_a.groupby('Year').agg({
        'Recruited': 'sum',
        'Churned': 'sum',
        'FTE': 'mean'
    }).reset_index()
    
    print("Level A trends by year:")
    print(yearly_trends.to_string(index=False))
    
    # Calculate if recruitment/churn is declining over time
    if len(yearly_trends) > 1:
        rec_trend = yearly_trends['Recruited'].iloc[-1] - yearly_trends['Recruited'].iloc[0]
        churn_trend = yearly_trends['Churned'].iloc[-1] - yearly_trends['Churned'].iloc[0]
        print(f"\nLevel A trends over simulation period:")
        print(f"  Recruitment change: {rec_trend:+.0f}")
        print(f"  Churn change: {churn_trend:+.0f}")

print("\n4. OFFICE-LEVEL ANALYSIS:")
print("=========================")

# Check if certain offices are driving the discrepancies
print("Checking office-level variations...")

office_summary = {}
for year, year_data in data['years'].items():
    for office, office_data in year_data['offices'].items():
        if office not in office_summary:
            office_summary[office] = {'recruited': 0, 'churned': 0, 'months': 0}
        
        for role, role_data in office_data['levels'].items():
            if isinstance(role_data, dict):
                for level, level_data in role_data.items():
                    for month_data in level_data:
                        office_summary[office]['recruited'] += month_data['recruited']
                        office_summary[office]['churned'] += month_data['churned']
                        office_summary[office]['months'] += 1

print("Average monthly recruitment/churn by office:")
print("Office        | Recruited/Month | Churned/Month")
print("--------------|-----------------|---------------")

office_rec_rates = []
office_churn_rates = []

for office, summary in office_summary.items():
    avg_rec = summary['recruited'] / summary['months'] if summary['months'] > 0 else 0
    avg_churn = summary['churned'] / summary['months'] if summary['months'] > 0 else 0
    office_rec_rates.append(avg_rec)
    office_churn_rates.append(avg_churn)
    print(f"{office:13} | {avg_rec:15.3f} | {avg_churn:13.3f}")

# Check for office-level consistency
rec_cv = np.std(office_rec_rates) / np.mean(office_rec_rates) if np.mean(office_rec_rates) > 0 else 0
churn_cv = np.std(office_churn_rates) / np.mean(office_churn_rates) if np.mean(office_churn_rates) > 0 else 0

print(f"\nOffice-level variability:")
print(f"  Recruitment coefficient of variation: {rec_cv:.3f}")
print(f"  Churn coefficient of variation: {churn_cv:.3f}")

if rec_cv > 0.3:
    print("  ⚠️  High variability in recruitment across offices")
if churn_cv > 0.3:
    print("  ⚠️  High variability in churn across offices")

print("\n5. ROLE-LEVEL ANALYSIS:")
print("=======================")

# Check if certain roles are driving the issues
role_summary = {}
for year, year_data in data['years'].items():
    for office, office_data in year_data['offices'].items():
        for role, role_data in office_data['levels'].items():
            if role not in role_summary:
                role_summary[role] = {'recruited': 0, 'churned': 0, 'months': 0}
            
            if isinstance(role_data, dict):
                for level, level_data in role_data.items():
                    for month_data in level_data:
                        role_summary[role]['recruited'] += month_data['recruited']
                        role_summary[role]['churned'] += month_data['churned']
                        role_summary[role]['months'] += 1

print("Average monthly recruitment/churn by role:")
print("Role        | Recruited/Month | Churned/Month | Share of Total")
print("------------|-----------------|---------------|---------------")

total_rec = sum(s['recruited'] for s in role_summary.values())
total_churn = sum(s['churned'] for s in role_summary.values())

for role, summary in role_summary.items():
    avg_rec = summary['recruited'] / summary['months'] if summary['months'] > 0 else 0
    avg_churn = summary['churned'] / summary['months'] if summary['months'] > 0 else 0
    rec_share = (summary['recruited'] / total_rec * 100) if total_rec > 0 else 0
    print(f"{role:11} | {avg_rec:15.3f} | {avg_churn:13.3f} | {rec_share:13.1f}%")

print("\n6. POTENTIAL CAUSES:")
print("===================")

potential_causes = [
    "Parameter Drift: Simulation parameters may not be held constant",
    "Scaling Issues: Baseline numbers may represent different scale/scope",
    "Role Distribution: Not all roles may be included in baseline calculation", 
    "Time Period Mismatch: Baseline may represent different time period",
    "Office Subset: Baseline may represent subset of offices",
    "Calculation Method: Different aggregation method used for baseline",
    "Simulation Logic: Bug in recruitment/churn implementation",
    "Data Quality: Missing or incorrect data in simulation results"
]

print("Most likely causes of the discrepancies:")
for i, cause in enumerate(potential_causes, 1):
    print(f"{i}. {cause}")

print("\n7. IMPACT ASSESSMENT:")
print("====================")

# Calculate the business impact of these discrepancies
baseline_total_rec = 2.910  # From previous analysis
baseline_total_churn = 1.384
baseline_net_growth = baseline_total_rec - baseline_total_churn

simulation_total_rec = 1.894  # From previous analysis  
simulation_total_churn = 1.121
simulation_net_growth = simulation_total_rec - simulation_total_churn

print(f"Expected monthly net growth: {baseline_net_growth:.3f} FTE")
print(f"Actual monthly net growth: {simulation_net_growth:.3f} FTE")
print(f"Monthly shortfall: {baseline_net_growth - simulation_net_growth:.3f} FTE")

# Annualized impact
annual_shortfall = (baseline_net_growth - simulation_net_growth) * 12
print(f"Annualized growth shortfall: {annual_shortfall:.1f} FTE")

if annual_shortfall > 5:
    print("⚠️  SIGNIFICANT IMPACT: Growth shortfall exceeds 5 FTE annually")
elif annual_shortfall > 1:
    print("⚠️  MODERATE IMPACT: Growth shortfall 1-5 FTE annually")
else:
    print("ℹ️  MINOR IMPACT: Growth shortfall less than 1 FTE annually")

print("\n8. NEXT STEPS:")
print("==============")

next_steps = [
    "Verify baseline calculation method and scope",
    "Check if simulation parameters match intended baseline",
    "Investigate Level A under-performance (largest impact)",
    "Review Level AC over-performance (may offset other issues)",
    "Validate simulation logic for recruitment/churn calculations",
    "Consider recalibrating simulation parameters",
    "Implement monitoring for parameter drift over time",
    "Document assumptions and calculation methods clearly"
]

print("Recommended next steps:")
for i, step in enumerate(next_steps, 1):
    print(f"{i}. {step}")

print(f"\nAnalysis complete. Key finding: Simulation shows systematic under-recruitment")
print(f"leading to {annual_shortfall:.1f} FTE annual growth shortfall vs. baseline expectations.")

