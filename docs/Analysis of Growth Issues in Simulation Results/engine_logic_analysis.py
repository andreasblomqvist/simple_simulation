import json
import pandas as pd
import numpy as np

print("=== USER'S ENGINE LOGIC ANALYSIS ===")
print()

# Load user's simulation data
with open('/home/ubuntu/upload/simulation_results_20250630_161229.json', 'r') as f:
    user_data = json.load(f)

print("1. SCALING ERROR ANALYSIS:")
print("=========================")

# The key finding: rates are 10-20x higher than expected
# Let's analyze the scaling patterns

baseline_rates = {
    'A': {'expected_rec_rate': 1.27, 'expected_churn_rate': 0.15},
    'AC': {'expected_rec_rate': 0.28, 'expected_churn_rate': 0.14},
    'AM': {'expected_rec_rate': 0.00, 'expected_churn_rate': 0.04},
    'C': {'expected_rec_rate': 0.04, 'expected_churn_rate': 0.08},
    'M': {'expected_rec_rate': 0.00, 'expected_churn_rate': 0.07},
    'PiP': {'expected_rec_rate': 0.00, 'expected_churn_rate': 0.00},
    'SrC': {'expected_rec_rate': 0.01, 'expected_churn_rate': 0.05},
    'SrM': {'expected_rec_rate': 0.00, 'expected_churn_rate': 0.10}
}

# From previous analysis, we know the actual rates
actual_rates = {
    'A': {'actual_rec_rate': 14.53, 'actual_churn_rate': 1.65},
    'AC': {'actual_rec_rate': 4.86, 'actual_churn_rate': 2.49},
    'AM': {'actual_rec_rate': 0.07, 'actual_churn_rate': 1.28},
    'C': {'actual_rec_rate': 1.00, 'actual_churn_rate': 1.92},
    'M': {'actual_rec_rate': 0.00, 'actual_churn_rate': 0.85},
    'PiP': {'actual_rec_rate': 0.00, 'actual_churn_rate': 0.00},
    'SrC': {'actual_rec_rate': 0.20, 'actual_churn_rate': 1.47},
    'SrM': {'actual_rec_rate': 0.00, 'actual_churn_rate': 0.48}
}

print("Scaling Factor Analysis:")
print("Level | Expected Rec% | Actual Rec% | Scale Factor | Expected Churn% | Actual Churn% | Scale Factor")
print("------|---------------|-------------|--------------|-----------------|---------------|-------------")

rec_scale_factors = []
churn_scale_factors = []

for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    if level in baseline_rates and level in actual_rates:
        expected_rec = baseline_rates[level]['expected_rec_rate']
        actual_rec = actual_rates[level]['actual_rec_rate']
        rec_scale = actual_rec / expected_rec if expected_rec > 0 else 0
        
        expected_churn = baseline_rates[level]['expected_churn_rate']
        actual_churn = actual_rates[level]['actual_churn_rate']
        churn_scale = actual_churn / expected_churn if expected_churn > 0 else 0
        
        print(f"{level:5} | {expected_rec:13.2f}% | {actual_rec:11.2f}% | {rec_scale:12.1f}x | {expected_churn:15.2f}% | {actual_churn:13.2f}% | {churn_scale:11.1f}x")
        
        if expected_rec > 0:
            rec_scale_factors.append(rec_scale)
        if expected_churn > 0:
            churn_scale_factors.append(churn_scale)

if rec_scale_factors:
    avg_rec_scale = np.mean(rec_scale_factors)
    std_rec_scale = np.std(rec_scale_factors)
    print(f"\nRecruitment scaling: Average {avg_rec_scale:.1f}x, Std Dev {std_rec_scale:.1f}x")

if churn_scale_factors:
    avg_churn_scale = np.mean(churn_scale_factors)
    std_churn_scale = np.std(churn_scale_factors)
    print(f"Churn scaling: Average {avg_churn_scale:.1f}x, Std Dev {std_churn_scale:.1f}x")

print("\n2. PATTERN ANALYSIS:")
print("===================")

# Analyze if there are consistent patterns in the errors
print("Looking for systematic patterns in the scaling errors...")

# Check if scaling is consistent across levels
consistent_scaling = True
if rec_scale_factors:
    rec_cv = std_rec_scale / avg_rec_scale if avg_rec_scale > 0 else 0
    if rec_cv > 0.3:  # More than 30% variation
        consistent_scaling = False
        print(f"❌ Recruitment scaling is INCONSISTENT (CV: {rec_cv:.2f})")
    else:
        print(f"✅ Recruitment scaling is relatively consistent (CV: {rec_cv:.2f})")

if churn_scale_factors:
    churn_cv = std_churn_scale / avg_churn_scale if avg_churn_scale > 0 else 0
    if churn_cv > 0.3:  # More than 30% variation
        consistent_scaling = False
        print(f"❌ Churn scaling is INCONSISTENT (CV: {churn_cv:.2f})")
    else:
        print(f"✅ Churn scaling is relatively consistent (CV: {churn_cv:.2f})")

print("\n3. DATA STRUCTURE ANALYSIS:")
print("===========================")

# Analyze the data structure to understand how the engine works
print("Analyzing user's simulation data structure...")

# Check the configuration
if 'configuration' in user_data:
    print("Configuration found:")
    config = user_data['configuration']
    for key, value in config.items():
        print(f"  {key}: {value}")

# Check simulation period
if 'simulation_period' in user_data:
    print(f"\nSimulation period: {user_data['simulation_period']}")

# Analyze the data dimensions
total_data_points = 0
offices = set()
roles = set()
levels = set()

for year, year_data in user_data['years'].items():
    for office, office_data in year_data['offices'].items():
        offices.add(office)
        for role, role_data in office_data['levels'].items():
            roles.add(role)
            if isinstance(role_data, dict):
                for level, level_data in role_data.items():
                    levels.add(level)
                    total_data_points += len(level_data)

print(f"\nData dimensions:")
print(f"  Years: {len(user_data['years'])}")
print(f"  Offices: {len(offices)} - {sorted(offices)}")
print(f"  Roles: {len(roles)} - {sorted(roles)}")
print(f"  Levels: {len(levels)} - {sorted(levels)}")
print(f"  Total data points: {total_data_points:,}")

# Expected data points: 6 years × 12 months × offices × roles × levels
expected_points = 6 * 12 * len(offices) * len(roles) * len(levels)
print(f"  Expected data points: {expected_points:,}")

if total_data_points != expected_points:
    print(f"  ⚠️  Data point mismatch: {total_data_points - expected_points:+,}")

print("\n4. MONTHLY PROGRESSION ANALYSIS:")
print("================================")

# Analyze how values change month by month for Level A (most problematic)
print("Analyzing Level A monthly progression (first year)...")

level_a_data = []
for year in ['2025']:  # Just first year
    if year in user_data['years']:
        for office, office_data in user_data['years'][year]['offices'].items():
            for role, role_data in office_data['levels'].items():
                if isinstance(role_data, dict) and 'A' in role_data:
                    for month_idx, month_data in enumerate(role_data['A'][:12]):  # First 12 months
                        level_a_data.append({
                            'Month': month_idx + 1,
                            'Office': office,
                            'Role': role,
                            'FTE': month_data['total'],
                            'Recruited': month_data['recruited'],
                            'Churned': month_data['churned'],
                            'Net': month_data['recruited'] - month_data['churned']
                        })

if level_a_data:
    df_a = pd.DataFrame(level_a_data)
    
    # Group by month to see overall trends
    monthly_summary = df_a.groupby('Month').agg({
        'FTE': 'sum',
        'Recruited': 'sum',
        'Churned': 'sum',
        'Net': 'sum'
    }).reset_index()
    
    print("Level A Monthly Summary (2025):")
    print("Month | Total FTE | Recruited | Churned | Net | Rec Rate% | Churn Rate%")
    print("------|-----------|-----------|---------|-----|-----------|------------")
    
    for _, row in monthly_summary.iterrows():
        rec_rate = (row['Recruited'] / row['FTE'] * 100) if row['FTE'] > 0 else 0
        churn_rate = (row['Churned'] / row['FTE'] * 100) if row['FTE'] > 0 else 0
        print(f"{row['Month']:5} | {row['FTE']:9.0f} | {row['Recruited']:9.0f} | {row['Churned']:7.0f} | {row['Net']:3.0f} | {rec_rate:9.2f}% | {churn_rate:10.2f}%")
    
    # Check if rates are stable over time
    rec_rates = [(row['Recruited'] / row['FTE'] * 100) if row['FTE'] > 0 else 0 for _, row in monthly_summary.iterrows()]
    churn_rates = [(row['Churned'] / row['FTE'] * 100) if row['FTE'] > 0 else 0 for _, row in monthly_summary.iterrows()]
    
    rec_rate_cv = np.std(rec_rates) / np.mean(rec_rates) if np.mean(rec_rates) > 0 else 0
    churn_rate_cv = np.std(churn_rates) / np.mean(churn_rates) if np.mean(churn_rates) > 0 else 0
    
    print(f"\nRate stability analysis:")
    print(f"  Recruitment rate CV: {rec_rate_cv:.3f} ({'stable' if rec_rate_cv < 0.1 else 'variable'})")
    print(f"  Churn rate CV: {churn_rate_cv:.3f} ({'stable' if churn_rate_cv < 0.1 else 'variable'})")

print("\n5. OFFICE/ROLE DISTRIBUTION ANALYSIS:")
print("=====================================")

# Check if the scaling issues are consistent across offices and roles
print("Analyzing distribution across offices and roles...")

office_totals = {}
role_totals = {}

for year, year_data in user_data['years'].items():
    for office, office_data in year_data['offices'].items():
        if office not in office_totals:
            office_totals[office] = {'recruited': 0, 'churned': 0, 'months': 0}
        
        for role, role_data in office_data['levels'].items():
            if role not in role_totals:
                role_totals[role] = {'recruited': 0, 'churned': 0, 'months': 0}
            
            if isinstance(role_data, dict):
                for level, level_data in role_data.items():
                    for month_data in level_data:
                        office_totals[office]['recruited'] += month_data['recruited']
                        office_totals[office]['churned'] += month_data['churned']
                        office_totals[office]['months'] += 1
                        
                        role_totals[role]['recruited'] += month_data['recruited']
                        role_totals[role]['churned'] += month_data['churned']
                        role_totals[role]['months'] += 1

print("Top 5 offices by recruitment activity:")
office_rec_sorted = sorted(office_totals.items(), key=lambda x: x[1]['recruited'], reverse=True)
for office, data in office_rec_sorted[:5]:
    avg_rec = data['recruited'] / data['months'] if data['months'] > 0 else 0
    print(f"  {office}: {avg_rec:.3f} recruited/month")

print("\nRole distribution:")
for role, data in role_totals.items():
    avg_rec = data['recruited'] / data['months'] if data['months'] > 0 else 0
    avg_churn = data['churned'] / data['months'] if data['months'] > 0 else 0
    print(f"  {role}: {avg_rec:.3f} recruited/month, {avg_churn:.3f} churned/month")

print("\n6. ROOT CAUSE HYPOTHESES:")
print("=========================")

hypotheses = []

# Based on the analysis, form hypotheses about the root cause
if rec_scale_factors and avg_rec_scale > 5:
    hypotheses.append(f"MAJOR: Recruitment rates scaled up by ~{avg_rec_scale:.0f}x - likely unit conversion error")

if churn_scale_factors and avg_churn_scale > 5:
    hypotheses.append(f"MAJOR: Churn rates scaled up by ~{avg_churn_scale:.0f}x - likely unit conversion error")

if consistent_scaling:
    hypotheses.append("Pattern suggests systematic scaling error rather than random bugs")
else:
    hypotheses.append("Inconsistent scaling suggests level-specific parameter errors")

# Check if it's a percentage vs decimal issue
if rec_scale_factors and 8 <= avg_rec_scale <= 12:
    hypotheses.append("LIKELY: Percentage vs decimal confusion (10x scaling suggests % treated as decimal)")

if churn_scale_factors and 8 <= avg_churn_scale <= 12:
    hypotheses.append("LIKELY: Percentage vs decimal confusion (10x scaling suggests % treated as decimal)")

# Check for office/role concentration
total_offices = len(offices)
total_roles = len(roles)
if total_offices > 1 and total_roles > 1:
    hypotheses.append("Multi-office/role simulation may have aggregation issues")

print("Root cause hypotheses (most likely first):")
for i, hypothesis in enumerate(hypotheses, 1):
    print(f"{i}. {hypothesis}")

print("\n7. SPECIFIC BUG THEORIES:")
print("=========================")

bug_theories = [
    "Percentage input error: Baseline rates entered as percentages (1.27) but engine expects decimals (0.0127)",
    "Rate calculation error: Engine calculates rates incorrectly, possibly missing division by 100",
    "Parameter loading error: Baseline parameters loaded incorrectly or scaled wrong",
    "Monthly vs annual confusion: Engine may be applying annual rates monthly",
    "Population base error: Rates calculated against wrong population base",
    "Aggregation error: Multi-office/role data aggregated incorrectly",
    "Time step error: Monthly calculations applied incorrectly",
    "Compounding error: Rates compounded when they should be simple"
]

print("Specific bug theories to investigate:")
for i, theory in enumerate(bug_theories, 1):
    print(f"{i}. {theory}")

print("\n8. DEBUGGING PRIORITY:")
print("=====================")

print("High Priority Issues:")
print("1. 🚨 Level A recruitment rate: 14.53% vs 1.27% expected (11.4x higher)")
print("2. 🚨 Level AC recruitment rate: 4.86% vs 0.28% expected (17.4x higher)")
print("3. ⚠️  All churn rates consistently 5-30x higher than expected")

print("\nMost Likely Fix:")
print("✅ Check if baseline percentage rates are being treated as decimals")
print("✅ Verify rate calculation logic (division by 100 missing?)")
print("✅ Test with simple parameters to isolate the scaling issue")

print(f"\nAnalysis complete. Primary suspect: Percentage vs decimal conversion error in rate calculations.")

