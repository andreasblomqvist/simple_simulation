import json
import pandas as pd
import numpy as np

# Load the simulation data
with open('/home/ubuntu/upload/simulation_results_20250630_161229.json', 'r') as f:
    data = json.load(f)

print("=== GROWTH TRAJECTORY ANALYSIS ===")
print()

# Baseline values from screenshot
baseline_data = {
    'A': {'fte': 163.0, 'recruitment_rate': 1.27, 'churn_rate': 0.15},
    'AC': {'fte': 231.0, 'recruitment_rate': 0.28, 'churn_rate': 0.14},
    'AM': {'fte': 418.0, 'recruitment_rate': 0.00, 'churn_rate': 0.04},
    'C': {'fte': 356.0, 'recruitment_rate': 0.04, 'churn_rate': 0.08},
    'M': {'fte': 156.0, 'recruitment_rate': 0.00, 'churn_rate': 0.07},
    'PiP': {'fte': 43.0, 'recruitment_rate': 0.00, 'churn_rate': 0.00},
    'SrC': {'fte': 409.0, 'recruitment_rate': 0.01, 'churn_rate': 0.05},
    'SrM': {'fte': 66.0, 'recruitment_rate': 0.00, 'churn_rate': 0.10}
}

print("1. BASELINE STARTING POINT:")
print("===========================")
total_baseline_fte = sum(level['fte'] for level in baseline_data.values())
print(f"Total baseline FTE: {total_baseline_fte:,.0f}")

for level, data_point in baseline_data.items():
    net_growth_rate = data_point['recruitment_rate'] - data_point['churn_rate']
    print(f"{level}: {data_point['fte']:,.0f} FTE, Net Growth: {net_growth_rate:+.2f}%/month")

print("\n2. EXPECTED GROWTH WITH BASELINE RATES:")
print("=======================================")

# Calculate what growth should look like with consistent baseline rates
def calculate_expected_growth(initial_fte, monthly_net_rate, months):
    """Calculate expected FTE after given months with constant monthly growth rate"""
    monthly_multiplier = 1 + (monthly_net_rate / 100)
    return initial_fte * (monthly_multiplier ** months)

# Assuming 72 months of simulation (6 years)
simulation_months = 72

expected_results = {}
for level, baseline in baseline_data.items():
    net_rate = baseline['recruitment_rate'] - baseline['churn_rate']
    expected_final_fte = calculate_expected_growth(baseline['fte'], net_rate, simulation_months)
    expected_results[level] = {
        'initial_fte': baseline['fte'],
        'expected_final_fte': expected_final_fte,
        'expected_growth_factor': expected_final_fte / baseline['fte'],
        'net_monthly_rate': net_rate
    }
    
    print(f"{level}: {baseline['fte']:,.0f} → {expected_final_fte:,.0f} FTE ({expected_final_fte/baseline['fte']:.1f}x growth)")

print("\n3. ACTUAL SIMULATION RESULTS:")
print("=============================")

# Calculate actual final results from simulation
actual_results = {}
for year, year_data in data['years'].items():
    for office, office_data in year_data['offices'].items():
        for role, role_data in office_data['levels'].items():
            if isinstance(role_data, dict):
                for level, level_data in role_data.items():
                    if level not in actual_results:
                        actual_results[level] = {'total_fte': 0, 'total_recruitment': 0, 'total_churn': 0}
                    
                    # Sum across all months and offices
                    for month_data in level_data:
                        actual_results[level]['total_fte'] += month_data['total']
                        actual_results[level]['total_recruitment'] += month_data['recruited']
                        actual_results[level]['total_churn'] += month_data['churned']

# Calculate averages and final values
for level in actual_results:
    avg_fte = actual_results[level]['total_fte'] / 72  # 72 months
    avg_recruitment = actual_results[level]['total_recruitment'] / 72
    avg_churn = actual_results[level]['total_churn'] / 72
    
    actual_results[level]['avg_fte'] = avg_fte
    actual_results[level]['avg_recruitment_rate'] = (avg_recruitment / avg_fte * 100) if avg_fte > 0 else 0
    actual_results[level]['avg_churn_rate'] = (avg_churn / avg_fte * 100) if avg_fte > 0 else 0
    actual_results[level]['actual_growth_factor'] = avg_fte / baseline_data[level]['fte']

for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    if level in actual_results:
        actual = actual_results[level]
        baseline_fte = baseline_data[level]['fte']
        print(f"{level}: {baseline_fte:,.0f} → {actual['avg_fte']:,.0f} FTE ({actual['actual_growth_factor']:.1f}x growth)")
        print(f"     Rates - Recruitment: {actual['avg_recruitment_rate']:.2f}%, Churn: {actual['avg_churn_rate']:.2f}%")

print("\n4. GROWTH COMPARISON:")
print("====================")

comparison_results = []
for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    if level in expected_results and level in actual_results:
        expected = expected_results[level]
        actual = actual_results[level]
        baseline = baseline_data[level]
        
        growth_difference = actual['actual_growth_factor'] - expected['expected_growth_factor']
        rate_recruitment_diff = actual['avg_recruitment_rate'] - baseline['recruitment_rate']
        rate_churn_diff = actual['avg_churn_rate'] - baseline['churn_rate']
        
        comparison_results.append({
            'Level': level,
            'Baseline_FTE': baseline['fte'],
            'Expected_Final_FTE': expected['expected_final_fte'],
            'Actual_Final_FTE': actual['avg_fte'],
            'Expected_Growth': expected['expected_growth_factor'],
            'Actual_Growth': actual['actual_growth_factor'],
            'Growth_Difference': growth_difference,
            'Recruitment_Rate_Diff': rate_recruitment_diff,
            'Churn_Rate_Diff': rate_churn_diff
        })
        
        print(f"{level}:")
        print(f"  Expected growth: {expected['expected_growth_factor']:.1f}x")
        print(f"  Actual growth:   {actual['actual_growth_factor']:.1f}x")
        print(f"  Difference:      {growth_difference:+.1f}x")
        print(f"  Rate deviations: Recruitment {rate_recruitment_diff:+.2f}%, Churn {rate_churn_diff:+.2f}%")
        
        if abs(growth_difference) > 1.0:
            print(f"  *** SIGNIFICANT GROWTH DEVIATION ***")
        
        if abs(rate_recruitment_diff) > 0.5 or abs(rate_churn_diff) > 0.5:
            print(f"  *** SIGNIFICANT RATE DEVIATION ***")
        print()

print("5. SUMMARY OF ISSUES:")
print("====================")

total_expected_final = sum(expected_results[level]['expected_final_fte'] for level in expected_results)
total_actual_final = sum(actual_results[level]['avg_fte'] for level in actual_results if level in expected_results)

print(f"Total expected final FTE: {total_expected_final:,.0f}")
print(f"Total actual final FTE:   {total_actual_final:,.0f}")
print(f"Overall difference:       {total_actual_final - total_expected_final:+,.0f} ({(total_actual_final/total_expected_final):.1f}x)")

# Identify levels with biggest issues
print("\nLevels with significant issues:")
for result in comparison_results:
    if abs(result['Growth_Difference']) > 1.0:
        print(f"- {result['Level']}: Growth off by {result['Growth_Difference']:+.1f}x")
    if abs(result['Recruitment_Rate_Diff']) > 0.5:
        print(f"- {result['Level']}: Recruitment rate off by {result['Recruitment_Rate_Diff']:+.2f}%")
    if abs(result['Churn_Rate_Diff']) > 0.5:
        print(f"- {result['Level']}: Churn rate off by {result['Churn_Rate_Diff']:+.2f}%")

print("\n6. ROOT CAUSE ANALYSIS:")
print("=======================")

print("The simulation appears to have the following issues:")
print("1. Recruitment and churn rates are NOT consistent with baseline parameters")
print("2. Actual growth significantly exceeds expected growth based on baseline rates")
print("3. High variability in rates suggests simulation logic errors")
print("4. Some levels show extreme deviations (e.g., Level A recruitment rate 3.28% vs baseline 1.27%)")

print("\nPossible causes:")
print("- Incorrect implementation of recruitment/churn logic")
print("- Compounding errors in growth calculations")
print("- Missing constraints on growth rates")
print("- Incorrect handling of progression between levels")
print("- Bug in the simulation engine itself")

# Save detailed comparison
comparison_df = pd.DataFrame(comparison_results)
comparison_df.to_csv('/home/ubuntu/growth_comparison.csv', index=False)
print(f"\nDetailed comparison saved to: /home/ubuntu/growth_comparison.csv")

