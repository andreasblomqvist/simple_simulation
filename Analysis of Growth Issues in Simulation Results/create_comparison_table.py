import json
import pandas as pd

# Load the simulation data
with open('/home/ubuntu/upload/simulation_results_20250630_161229.json', 'r') as f:
    data = json.load(f)

# Calculate aggregated results
results = []
for year, year_data in data['years'].items():
    for office, office_data in year_data['offices'].items():
        for role, role_data in office_data['levels'].items():
            if isinstance(role_data, dict):
                for level, level_data in role_data.items():
                    total_fte = sum(month['total'] for month in level_data)
                    total_recruited = sum(month['recruited'] for month in level_data)
                    total_churned = sum(month['churned'] for month in level_data)
                    
                    avg_fte = total_fte / 12
                    avg_recruited_per_month = total_recruited / 12
                    avg_churned_per_month = total_churned / 12
                    
                    results.append({
                        'Level': level,
                        'FTE': avg_fte,
                        'Recruitment (FTE/month)': avg_recruited_per_month,
                        'Churn (FTE/month)': avg_churned_per_month,
                    })

df = pd.DataFrame(results)
level_summary = df.groupby('Level').agg({
    'FTE': 'sum',
    'Recruitment (FTE/month)': 'sum',
    'Churn (FTE/month)': 'sum'
}).reset_index()

# Calculate percentages
level_summary['Recruitment %/month'] = (level_summary['Recruitment (FTE/month)'] / level_summary['FTE'] * 100).round(2)
level_summary['Churn %/month'] = (level_summary['Churn (FTE/month)'] / level_summary['FTE'] * 100).round(2)
level_summary['Net Growth %/month'] = level_summary['Recruitment %/month'] - level_summary['Churn %/month']

# Screenshot data
screenshot_data = {
    'Level': ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM'],
    'FTE': [163.0, 231.0, 418.0, 356.0, 156.0, 43.0, 409.0, 66.0],
    'Recruitment (FTE/month)': [2.076, 0.636, 0.011, 0.155, 0.000, 0.000, 0.032, 0.000],
    'Churn (FTE/month)': [0.238, 0.318, 0.168, 0.276, 0.112, 0.000, 0.206, 0.066],
    'Recruitment %/month': [1.27, 0.28, 0.00, 0.04, 0.00, 0.00, 0.01, 0.00],
    'Churn %/month': [0.15, 0.14, 0.04, 0.08, 0.07, 0.00, 0.05, 0.10],
    'Net Growth %/month': [1.13, 0.14, -0.04, -0.03, -0.07, 0.00, -0.04, -0.10]
}

screenshot_df = pd.DataFrame(screenshot_data)

# Create comprehensive comparison table
comparison_data = []

for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    calc_row = level_summary[level_summary['Level'] == level]
    screenshot_row = screenshot_df[screenshot_df['Level'] == level]
    
    if not calc_row.empty and not screenshot_row.empty:
        comparison_data.append({
            'Level': level,
            'Calculated_FTE': round(calc_row['FTE'].iloc[0], 1),
            'Screenshot_FTE': screenshot_row['FTE'].iloc[0],
            'FTE_Ratio': round(calc_row['FTE'].iloc[0] / screenshot_row['FTE'].iloc[0], 1),
            'Calculated_Recruitment': round(calc_row['Recruitment (FTE/month)'].iloc[0], 3),
            'Screenshot_Recruitment': screenshot_row['Recruitment (FTE/month)'].iloc[0],
            'Recruitment_Ratio': round(calc_row['Recruitment (FTE/month)'].iloc[0] / screenshot_row['Recruitment (FTE/month)'].iloc[0], 1) if screenshot_row['Recruitment (FTE/month)'].iloc[0] > 0 else 'N/A',
            'Calculated_Churn': round(calc_row['Churn (FTE/month)'].iloc[0], 3),
            'Screenshot_Churn': screenshot_row['Churn (FTE/month)'].iloc[0],
            'Churn_Ratio': round(calc_row['Churn (FTE/month)'].iloc[0] / screenshot_row['Churn (FTE/month)'].iloc[0], 1) if screenshot_row['Churn (FTE/month)'].iloc[0] > 0 else 'N/A',
            'Calculated_Rec_Pct': round(calc_row['Recruitment %/month'].iloc[0], 2),
            'Screenshot_Rec_Pct': screenshot_row['Recruitment %/month'].iloc[0],
            'Calculated_Churn_Pct': round(calc_row['Churn %/month'].iloc[0], 2),
            'Screenshot_Churn_Pct': screenshot_row['Churn %/month'].iloc[0],
            'Calculated_Net_Growth': round(calc_row['Net Growth %/month'].iloc[0], 2),
            'Screenshot_Net_Growth': screenshot_row['Net Growth %/month'].iloc[0]
        })

comparison_df = pd.DataFrame(comparison_data)

# Save to CSV for easy viewing
comparison_df.to_csv('/home/ubuntu/detailed_comparison.csv', index=False)

print("Detailed Comparison Table Created")
print("=================================")
print(f"Saved to: /home/ubuntu/detailed_comparison.csv")
print()
print("Summary of Discrepancies:")
print("------------------------")

for _, row in comparison_df.iterrows():
    level = row['Level']
    fte_ratio = row['FTE_Ratio']
    rec_ratio = row['Recruitment_Ratio']
    churn_ratio = row['Churn_Ratio']
    
    print(f"{level}: FTE is {fte_ratio}x higher, Recruitment is {rec_ratio}x higher, Churn is {churn_ratio}x higher")

print("\nKey Statistics:")
print("---------------")
avg_fte_ratio = comparison_df['FTE_Ratio'].mean()
print(f"Average FTE ratio: {avg_fte_ratio:.1f}x")

# Calculate average ratios for non-zero values
rec_ratios = [r for r in comparison_df['Recruitment_Ratio'] if r != 'N/A' and r != float('inf')]
churn_ratios = [r for r in comparison_df['Churn_Ratio'] if r != 'N/A' and r != float('inf')]

if rec_ratios:
    avg_rec_ratio = sum(rec_ratios) / len(rec_ratios)
    print(f"Average Recruitment ratio: {avg_rec_ratio:.1f}x")

if churn_ratios:
    avg_churn_ratio = sum(churn_ratios) / len(churn_ratios)
    print(f"Average Churn ratio: {avg_churn_ratio:.1f}x")

print(f"\nTotal calculated FTE across all levels: {level_summary['FTE'].sum():,.0f}")
print(f"Total screenshot FTE across all levels: {screenshot_df['FTE'].sum():,.0f}")
print(f"Overall ratio: {level_summary['FTE'].sum() / screenshot_df['FTE'].sum():.1f}x")

