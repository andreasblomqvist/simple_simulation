import json
import pandas as pd

# Load the simulation data
with open('/home/ubuntu/upload/simulation_results_20250630_161229.json', 'r') as f:
    data = json.load(f)

print("=== RECRUITMENT AND CHURN RATE CONSISTENCY ANALYSIS ===")
print()

# Baseline rates from screenshot
baseline_rates = {
    'A': {'recruitment_pct': 1.27, 'churn_pct': 0.15, 'fte': 163.0},
    'AC': {'recruitment_pct': 0.28, 'churn_pct': 0.14, 'fte': 231.0},
    'AM': {'recruitment_pct': 0.00, 'churn_pct': 0.04, 'fte': 418.0},
    'C': {'recruitment_pct': 0.04, 'churn_pct': 0.08, 'fte': 356.0},
    'M': {'recruitment_pct': 0.00, 'churn_pct': 0.07, 'fte': 156.0},
    'PiP': {'recruitment_pct': 0.00, 'churn_pct': 0.00, 'fte': 43.0},
    'SrC': {'recruitment_pct': 0.01, 'churn_pct': 0.05, 'fte': 409.0},
    'SrM': {'recruitment_pct': 0.00, 'churn_pct': 0.10, 'fte': 66.0}
}

print("1. BASELINE RATES FROM SCREENSHOT:")
print("==================================")
for level, rates in baseline_rates.items():
    print(f"{level}: Recruitment {rates['recruitment_pct']:.2f}%, Churn {rates['churn_pct']:.2f}%")

print("\n2. RATE CONSISTENCY CHECK:")
print("==========================")

# Calculate rates from simulation data
results = []
for year, year_data in data['years'].items():
    for office, office_data in year_data['offices'].items():
        for role, role_data in office_data['levels'].items():
            if isinstance(role_data, dict):
                for level, level_data in role_data.items():
                    # Calculate monthly rates for each month
                    for month_idx, month_data in enumerate(level_data):
                        fte = month_data['total']
                        recruited = month_data['recruited']
                        churned = month_data['churned']
                        
                        recruitment_rate = (recruited / fte * 100) if fte > 0 else 0
                        churn_rate = (churned / fte * 100) if fte > 0 else 0
                        
                        results.append({
                            'Year': year,
                            'Office': office,
                            'Role': role,
                            'Level': level,
                            'Month': month_idx + 1,
                            'FTE': fte,
                            'Recruited': recruited,
                            'Churned': churned,
                            'Recruitment_Rate': recruitment_rate,
                            'Churn_Rate': churn_rate
                        })

df = pd.DataFrame(results)

print("Sample of calculated rates by month:")
print("------------------------------------")
sample_data = df[df['Level'].isin(['A', 'AC']) & (df['Month'] <= 3)].head(10)
print(sample_data[['Level', 'Month', 'FTE', 'Recruitment_Rate', 'Churn_Rate']].to_string(index=False))

print("\n3. RATE VARIABILITY ANALYSIS:")
print("=============================")

# Check rate consistency across time for each level
for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    level_data = df[df['Level'] == level]
    
    if not level_data.empty:
        # Calculate statistics for rates
        rec_rates = level_data['Recruitment_Rate']
        churn_rates = level_data['Churn_Rate']
        
        rec_mean = rec_rates.mean()
        rec_std = rec_rates.std()
        rec_min = rec_rates.min()
        rec_max = rec_rates.max()
        
        churn_mean = churn_rates.mean()
        churn_std = churn_rates.std()
        churn_min = churn_rates.min()
        churn_max = churn_rates.max()
        
        baseline_rec = baseline_rates[level]['recruitment_pct']
        baseline_churn = baseline_rates[level]['churn_pct']
        
        print(f"\nLevel {level}:")
        print(f"  Recruitment Rate - Baseline: {baseline_rec:.2f}%, Simulation Mean: {rec_mean:.2f}% (±{rec_std:.2f})")
        print(f"                   Range: {rec_min:.2f}% - {rec_max:.2f}%")
        print(f"  Churn Rate      - Baseline: {baseline_churn:.2f}%, Simulation Mean: {churn_mean:.2f}% (±{churn_std:.2f})")
        print(f"                   Range: {churn_min:.2f}% - {churn_max:.2f}%")
        
        # Check for significant deviations
        rec_deviation = abs(rec_mean - baseline_rec)
        churn_deviation = abs(churn_mean - baseline_churn)
        
        if rec_deviation > 0.1:  # More than 0.1% difference
            print(f"  *** RECRUITMENT RATE DEVIATION: {rec_deviation:.2f}% difference from baseline ***")
        
        if churn_deviation > 0.1:  # More than 0.1% difference
            print(f"  *** CHURN RATE DEVIATION: {churn_deviation:.2f}% difference from baseline ***")
        
        # Check for high variability
        if rec_std > 0.5:
            print(f"  *** HIGH RECRUITMENT RATE VARIABILITY: {rec_std:.2f}% standard deviation ***")
        
        if churn_std > 0.5:
            print(f"  *** HIGH CHURN RATE VARIABILITY: {churn_std:.2f}% standard deviation ***")

print("\n4. TEMPORAL ANALYSIS:")
print("=====================")

# Check if rates change over time (they shouldn't if simulation parameters are constant)
print("Rate trends over time (first 12 months):")
print("-----------------------------------------")

for level in ['A', 'AC']:  # Sample two levels
    level_data = df[(df['Level'] == level) & (df['Month'] <= 12)]
    
    if not level_data.empty:
        monthly_rates = level_data.groupby('Month').agg({
            'Recruitment_Rate': 'mean',
            'Churn_Rate': 'mean'
        }).reset_index()
        
        print(f"\nLevel {level} - Monthly Average Rates:")
        print(monthly_rates.to_string(index=False))
        
        # Check for trends
        rec_trend = monthly_rates['Recruitment_Rate'].iloc[-1] - monthly_rates['Recruitment_Rate'].iloc[0]
        churn_trend = monthly_rates['Churn_Rate'].iloc[-1] - monthly_rates['Churn_Rate'].iloc[0]
        
        if abs(rec_trend) > 0.2:
            print(f"*** RECRUITMENT RATE TREND DETECTED: {rec_trend:.2f}% change from month 1 to 12 ***")
        
        if abs(churn_trend) > 0.2:
            print(f"*** CHURN RATE TREND DETECTED: {churn_trend:.2f}% change from month 1 to 12 ***")

print("\n5. POTENTIAL ISSUES IDENTIFIED:")
print("===============================")

# Summary of issues found
issues = []

for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    level_data = df[df['Level'] == level]
    
    if not level_data.empty:
        rec_mean = level_data['Recruitment_Rate'].mean()
        churn_mean = level_data['Churn_Rate'].mean()
        
        baseline_rec = baseline_rates[level]['recruitment_pct']
        baseline_churn = baseline_rates[level]['churn_pct']
        
        rec_deviation = abs(rec_mean - baseline_rec)
        churn_deviation = abs(churn_mean - baseline_churn)
        
        if rec_deviation > 0.1:
            issues.append(f"Level {level}: Recruitment rate differs by {rec_deviation:.2f}% from baseline")
        
        if churn_deviation > 0.1:
            issues.append(f"Level {level}: Churn rate differs by {churn_deviation:.2f}% from baseline")

if issues:
    print("Issues found:")
    for issue in issues:
        print(f"- {issue}")
else:
    print("No significant rate deviations found - simulation appears to be running with consistent parameters.")

print(f"\nTotal data points analyzed: {len(df)}")
print(f"Offices: {df['Office'].nunique()}")
print(f"Roles: {df['Role'].nunique()}")
print(f"Time periods: {df['Month'].nunique()} months")

