import json
import pandas as pd
import numpy as np

# Load the simulation data
with open('/home/ubuntu/upload/simulation_results_20250630_161229.json', 'r') as f:
    data = json.load(f)

print("=== GROWTH PATTERNS AND ANOMALIES ANALYSIS ===")
print()

# Baseline data for reference
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

print("1. ANOMALY CLASSIFICATION:")
print("==========================")

# Collect all data points for analysis
all_data = []
for year, year_data in data['years'].items():
    for office, office_data in year_data['offices'].items():
        for role, role_data in office_data['levels'].items():
            if isinstance(role_data, dict):
                for level, level_data in role_data.items():
                    for month_idx, month_data in enumerate(level_data):
                        fte = month_data['total']
                        recruited = month_data['recruited']
                        churned = month_data['churned']
                        
                        recruitment_rate = (recruited / fte * 100) if fte > 0 else 0
                        churn_rate = (churned / fte * 100) if fte > 0 else 0
                        
                        all_data.append({
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

df = pd.DataFrame(all_data)

# Identify extreme anomalies
print("Extreme Rate Anomalies (>10x baseline):")
print("----------------------------------------")

anomaly_count = 0
for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    level_data = df[df['Level'] == level]
    baseline_rec = baseline_data[level]['recruitment_rate']
    baseline_churn = baseline_data[level]['churn_rate']
    
    # Find extreme recruitment rate anomalies
    extreme_rec = level_data[level_data['Recruitment_Rate'] > baseline_rec * 10]
    extreme_churn = level_data[level_data['Churn_Rate'] > baseline_churn * 10]
    
    if len(extreme_rec) > 0:
        max_rec_rate = extreme_rec['Recruitment_Rate'].max()
        print(f"{level}: {len(extreme_rec)} instances of extreme recruitment rates (max: {max_rec_rate:.1f}% vs baseline {baseline_rec:.2f}%)")
        anomaly_count += len(extreme_rec)
    
    if len(extreme_churn) > 0:
        max_churn_rate = extreme_churn['Churn_Rate'].max()
        print(f"{level}: {len(extreme_churn)} instances of extreme churn rates (max: {max_churn_rate:.1f}% vs baseline {baseline_churn:.2f}%)")
        anomaly_count += len(extreme_churn)

print(f"\nTotal extreme anomalies found: {anomaly_count}")

print("\n2. IMPOSSIBLE VALUES ANALYSIS:")
print("===============================")

# Check for impossible values (>100% rates)
impossible_rec = df[df['Recruitment_Rate'] > 100]
impossible_churn = df[df['Churn_Rate'] > 100]

print(f"Impossible recruitment rates (>100%): {len(impossible_rec)} instances")
if len(impossible_rec) > 0:
    print("Sample impossible recruitment rates:")
    sample_impossible = impossible_rec.head(5)[['Level', 'Office', 'FTE', 'Recruited', 'Recruitment_Rate']]
    print(sample_impossible.to_string(index=False))

print(f"\nImpossible churn rates (>100%): {len(impossible_churn)} instances")
if len(impossible_churn) > 0:
    print("Sample impossible churn rates:")
    sample_impossible_churn = impossible_churn.head(5)[['Level', 'Office', 'FTE', 'Churned', 'Churn_Rate']]
    print(sample_impossible_churn.to_string(index=False))

print("\n3. ZERO FTE ANALYSIS:")
print("=====================")

# Check for zero FTE entries (which would cause division by zero issues)
zero_fte = df[df['FTE'] == 0]
print(f"Zero FTE instances: {len(zero_fte)}")

if len(zero_fte) > 0:
    print("Zero FTE breakdown by level:")
    zero_breakdown = zero_fte.groupby('Level').size().reset_index(name='Count')
    print(zero_breakdown.to_string(index=False))

print("\n4. GROWTH ACCELERATION ANALYSIS:")
print("=================================")

# Analyze growth acceleration over time
print("Monthly FTE growth patterns (first 12 months, Level A sample):")
level_a_data = df[(df['Level'] == 'A') & (df['Month'] <= 12)]
monthly_fte = level_a_data.groupby('Month')['FTE'].sum().reset_index()
monthly_fte['Growth_Rate'] = monthly_fte['FTE'].pct_change() * 100

print(monthly_fte.to_string(index=False))

# Check for exponential growth patterns
if len(monthly_fte) > 1:
    total_growth = (monthly_fte['FTE'].iloc[-1] / monthly_fte['FTE'].iloc[0] - 1) * 100
    avg_monthly_growth = monthly_fte['Growth_Rate'].mean()
    print(f"\nLevel A - Total growth in 12 months: {total_growth:.1f}%")
    print(f"Average monthly growth rate: {avg_monthly_growth:.1f}%")
    
    if avg_monthly_growth > 10:
        print("*** UNSUSTAINABLE EXPONENTIAL GROWTH DETECTED ***")

print("\n5. RECRUITMENT/CHURN LOGIC ISSUES:")
print("===================================")

# Check for logical inconsistencies
print("Checking for recruitment without available positions...")

# Look for cases where recruitment > churn but FTE is decreasing
logic_issues = []
for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    level_data = df[df['Level'] == level].sort_values(['Office', 'Month'])
    
    for office in level_data['Office'].unique():
        office_data = level_data[level_data['Office'] == office].sort_values('Month')
        
        for i in range(1, len(office_data)):
            current = office_data.iloc[i]
            previous = office_data.iloc[i-1]
            
            net_change = current['Recruited'] - current['Churned']
            fte_change = current['FTE'] - previous['FTE']
            
            # Check if net recruitment doesn't match FTE change
            if abs(net_change - fte_change) > 1:  # Allow for small rounding errors
                logic_issues.append({
                    'Level': level,
                    'Office': office,
                    'Month': current['Month'],
                    'Net_Recruitment': net_change,
                    'FTE_Change': fte_change,
                    'Discrepancy': abs(net_change - fte_change)
                })

print(f"Logic inconsistencies found: {len(logic_issues)}")

if len(logic_issues) > 0:
    print("Sample logic issues:")
    sample_issues = pd.DataFrame(logic_issues).head(5)
    print(sample_issues.to_string(index=False))

print("\n6. RATE STABILITY ANALYSIS:")
print("===========================")

# Check how much rates vary from their baseline
rate_stability = {}
for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    level_data = df[df['Level'] == level]
    
    baseline_rec = baseline_data[level]['recruitment_rate']
    baseline_churn = baseline_data[level]['churn_rate']
    
    rec_rates = level_data['Recruitment_Rate']
    churn_rates = level_data['Churn_Rate']
    
    # Calculate coefficient of variation (std/mean) as a measure of stability
    rec_cv = rec_rates.std() / rec_rates.mean() if rec_rates.mean() > 0 else 0
    churn_cv = churn_rates.std() / churn_rates.mean() if churn_rates.mean() > 0 else 0
    
    rate_stability[level] = {
        'recruitment_cv': rec_cv,
        'churn_cv': churn_cv,
        'recruitment_deviation': abs(rec_rates.mean() - baseline_rec),
        'churn_deviation': abs(churn_rates.mean() - baseline_churn)
    }
    
    print(f"{level}:")
    print(f"  Recruitment rate stability: CV = {rec_cv:.2f} (lower is more stable)")
    print(f"  Churn rate stability: CV = {churn_cv:.2f}")
    print(f"  Deviation from baseline: Rec {rate_stability[level]['recruitment_deviation']:.2f}%, Churn {rate_stability[level]['churn_deviation']:.2f}%")
    
    if rec_cv > 2.0 or churn_cv > 2.0:
        print(f"  *** HIGH RATE INSTABILITY ***")
    
    if rate_stability[level]['recruitment_deviation'] > 1.0 or rate_stability[level]['churn_deviation'] > 1.0:
        print(f"  *** SIGNIFICANT DEVIATION FROM BASELINE ***")

print("\n7. SUMMARY OF CRITICAL ISSUES:")
print("==============================")

critical_issues = []

# Summarize all critical findings
if anomaly_count > 100:
    critical_issues.append(f"Extreme rate anomalies: {anomaly_count} instances")

if len(impossible_rec) > 0 or len(impossible_churn) > 0:
    critical_issues.append(f"Impossible rates (>100%): {len(impossible_rec)} recruitment, {len(impossible_churn)} churn")

if len(zero_fte) > 0:
    critical_issues.append(f"Zero FTE instances: {len(zero_fte)} (causes division by zero)")

if len(logic_issues) > 10:
    critical_issues.append(f"Logic inconsistencies: {len(logic_issues)} instances")

unstable_levels = [level for level, data in rate_stability.items() 
                  if data['recruitment_cv'] > 2.0 or data['churn_cv'] > 2.0]
if unstable_levels:
    critical_issues.append(f"Highly unstable rates in levels: {', '.join(unstable_levels)}")

deviant_levels = [level for level, data in rate_stability.items() 
                 if data['recruitment_deviation'] > 1.0 or data['churn_deviation'] > 1.0]
if deviant_levels:
    critical_issues.append(f"Significant baseline deviations in levels: {', '.join(deviant_levels)}")

print("Critical Issues Found:")
for i, issue in enumerate(critical_issues, 1):
    print(f"{i}. {issue}")

if not critical_issues:
    print("No critical issues found - simulation appears to be functioning correctly.")
else:
    print(f"\n*** {len(critical_issues)} CRITICAL ISSUES IDENTIFIED ***")
    print("The simulation has significant problems that need immediate attention.")

print(f"\nTotal data points analyzed: {len(df):,}")
print(f"Analysis covers {df['Office'].nunique()} offices, {df['Role'].nunique()} roles, {df['Month'].nunique()} months")

