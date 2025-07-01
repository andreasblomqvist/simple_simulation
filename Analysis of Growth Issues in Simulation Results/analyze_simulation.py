import json
import pandas as pd

# Load the simulation data
with open('/home/ubuntu/upload/simulation_results_20250630_161229.json', 'r') as f:
    data = json.load(f)

# Extract data for analysis
results = []

# Navigate through the data structure
for year, year_data in data['years'].items():
    for office, office_data in year_data['offices'].items():
        for role, role_data in office_data['levels'].items():
            for level, level_data in role_data.items():
                # Each level contains monthly data (12 months)
                total_fte = 0
                total_recruited = 0
                total_churned = 0
                
                for month_data in level_data:
                    total_fte += month_data['total']
                    total_recruited += month_data['recruited']
                    total_churned += month_data['churned']
                
                # Calculate averages
                avg_fte = total_fte / 12
                avg_recruited_per_month = total_recruited / 12
                avg_churned_per_month = total_churned / 12
                
                # Calculate rates
                recruitment_rate_per_month = (avg_recruited_per_month / avg_fte) * 100 if avg_fte > 0 else 0
                churn_rate_per_month = (avg_churned_per_month / avg_fte) * 100 if avg_fte > 0 else 0
                net_growth_rate_per_month = recruitment_rate_per_month - churn_rate_per_month
                
                results.append({
                    'Level': level,
                    'FTE': round(avg_fte, 1),
                    'Recruitment (FTE/month)': round(avg_recruited_per_month, 3),
                    'Churn (FTE/month)': round(avg_churned_per_month, 3),
                    'Recruitment %/month': f"{recruitment_rate_per_month:.2f}%",
                    'Churn %/month': f"{churn_rate_per_month:.2f}%",
                    'Net Growth %/month': f"{net_growth_rate_per_month:.2f}%"
                })

# Create DataFrame and sort by level
df = pd.DataFrame(results)
df = df.sort_values('Level')

print("Calculated Results:")
print("==================")
print(df.to_string(index=False))

print("\n\nScreenshot Data for Comparison:")
print("===============================")
screenshot_data = {
    'Level': ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM'],
    'FTE': [163.0, 231.0, 418.0, 356.0, 156.0, 43.0, 409.0, 66.0],
    'Recruitment (FTE/month)': [2.076, 0.636, 0.011, 0.155, 0.000, 0.000, 0.032, 0.000],
    'Churn (FTE/month)': [0.238, 0.318, 0.168, 0.276, 0.112, 0.000, 0.206, 0.066],
    'Recruitment %/month': ['1.27%', '0.28%', '0.00%', '0.04%', '0.00%', '0.00%', '0.01%', '0.00%'],
    'Churn %/month': ['0.15%', '0.14%', '0.04%', '0.08%', '0.07%', '0.00%', '0.05%', '0.10%'],
    'Net Growth %/month': ['1.13%', '0.14%', '-0.04%', '-0.03%', '-0.07%', '0.00%', '-0.04%', '-0.10%']
}

screenshot_df = pd.DataFrame(screenshot_data)
print(screenshot_df.to_string(index=False))

print("\n\nDiscrepancy Analysis:")
print("====================")

# Compare the data
for level in ['A', 'AC', 'AM', 'C', 'M']:
    calc_row = df[df['Level'] == level]
    screenshot_row = screenshot_df[screenshot_df['Level'] == level]
    
    if not calc_row.empty and not screenshot_row.empty:
        calc_fte = calc_row['FTE'].iloc[0]
        screenshot_fte = screenshot_row['FTE'].iloc[0]
        
        calc_recruitment = calc_row['Recruitment (FTE/month)'].iloc[0]
        screenshot_recruitment = screenshot_row['Recruitment (FTE/month)'].iloc[0]
        
        calc_churn = calc_row['Churn (FTE/month)'].iloc[0]
        screenshot_churn = screenshot_row['Churn (FTE/month)'].iloc[0]
        
        print(f"\nLevel {level}:")
        print(f"  FTE - Calculated: {calc_fte}, Screenshot: {screenshot_fte}, Diff: {calc_fte - screenshot_fte}")
        print(f"  Recruitment - Calculated: {calc_recruitment}, Screenshot: {screenshot_recruitment}, Diff: {calc_recruitment - screenshot_recruitment}")
        print(f"  Churn - Calculated: {calc_churn}, Screenshot: {screenshot_churn}, Diff: {calc_churn - screenshot_churn}")
        
        # Verify percentage calculations
        calc_rec_pct = (calc_recruitment / calc_fte) * 100 if calc_fte > 0 else 0
        calc_churn_pct = (calc_churn / calc_fte) * 100 if calc_fte > 0 else 0
        calc_net_growth = calc_rec_pct - calc_churn_pct
        
        screenshot_rec_pct = float(screenshot_row['Recruitment %/month'].iloc[0].replace('%', ''))
        screenshot_churn_pct = float(screenshot_row['Churn %/month'].iloc[0].replace('%', ''))
        screenshot_net_growth = float(screenshot_row['Net Growth %/month'].iloc[0].replace('%', ''))
        
        print(f"  Recruitment % - Calculated: {calc_rec_pct:.2f}%, Screenshot: {screenshot_rec_pct:.2f}%, Diff: {calc_rec_pct - screenshot_rec_pct:.2f}%")
        print(f"  Churn % - Calculated: {calc_churn_pct:.2f}%, Screenshot: {screenshot_churn_pct:.2f}%, Diff: {calc_churn_pct - screenshot_churn_pct:.2f}%")
        print(f"  Net Growth % - Calculated: {calc_net_growth:.2f}%, Screenshot: {screenshot_net_growth:.2f}%, Diff: {calc_net_growth - screenshot_net_growth:.2f}%")

