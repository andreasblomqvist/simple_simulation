import json
import pandas as pd

# Load the simulation data
with open('/home/ubuntu/upload/simulation_results_20250630_161229.json', 'r') as f:
    data = json.load(f)

print("=== ROOT CAUSE ANALYSIS ===")
print()

# Let's examine what roles and offices exist
print("1. DATA STRUCTURE ANALYSIS:")
print("==========================")

for year, year_data in data['years'].items():
    print(f"Year: {year}")
    print(f"Total offices: {len(year_data['offices'])}")
    
    for office, office_data in year_data['offices'].items():
        print(f"\nOffice: {office}")
        print(f"Office total FTE: {office_data['total_fte']}")
        print(f"Available roles: {list(office_data['levels'].keys())}")
        
        # Check each role structure
        for role, role_data in office_data['levels'].items():
            if isinstance(role_data, dict):
                print(f"  {role}: {list(role_data.keys())}")
                # Sample one level to see monthly data
                first_level = list(role_data.keys())[0]
                print(f"    {first_level} has {len(role_data[first_level])} months of data")
            else:
                print(f"  {role}: Direct list with {len(role_data)} months")

print("\n\n2. HYPOTHESIS TESTING:")
print("======================")

# Hypothesis 1: Screenshot shows only one role (e.g., Consultant)
print("Hypothesis 1: Screenshot shows only Consultant role data")

consultant_results = []
for year, year_data in data['years'].items():
    for office, office_data in year_data['offices'].items():
        consultant_data = office_data['levels'].get('Consultant', {})
        if isinstance(consultant_data, dict):
            for level, level_data in consultant_data.items():
                total_fte = sum(month['total'] for month in level_data)
                total_recruited = sum(month['recruited'] for month in level_data)
                total_churned = sum(month['churned'] for month in level_data)
                
                avg_fte = total_fte / 12
                avg_recruited_per_month = total_recruited / 12
                avg_churned_per_month = total_churned / 12
                
                consultant_results.append({
                    'Level': level,
                    'FTE': round(avg_fte, 1),
                    'Recruitment (FTE/month)': round(avg_recruited_per_month, 3),
                    'Churn (FTE/month)': round(avg_churned_per_month, 3),
                })

consultant_df = pd.DataFrame(consultant_results)
consultant_summary = consultant_df.groupby('Level').agg({
    'FTE': 'sum',
    'Recruitment (FTE/month)': 'sum',
    'Churn (FTE/month)': 'sum'
}).reset_index()

print("\nConsultant-only results:")
print(consultant_summary.to_string(index=False))

# Hypothesis 2: Screenshot shows only one office or a specific subset
print("\n\nHypothesis 2: Screenshot shows data for a specific office or subset")

# Let's check if there are multiple offices
office_count = 0
for year, year_data in data['years'].items():
    office_count = len(year_data['offices'])
    print(f"Total offices in data: {office_count}")
    for office_name in year_data['offices'].keys():
        print(f"  - {office_name}")

# Hypothesis 3: Screenshot shows end-of-year snapshot vs annual averages
print("\n\nHypothesis 3: Screenshot shows end-of-year snapshot")

# Let's look at December data (month 12) only
december_results = []
for year, year_data in data['years'].items():
    for office, office_data in year_data['offices'].items():
        for role, role_data in office_data['levels'].items():
            if isinstance(role_data, dict):
                for level, level_data in role_data.items():
                    # Get December data (index 11, since 0-indexed)
                    if len(level_data) >= 12:
                        dec_data = level_data[11]  # December
                        december_results.append({
                            'Role': role,
                            'Level': level,
                            'FTE': dec_data['total'],
                            'Recruitment (FTE/month)': dec_data['recruited'],
                            'Churn (FTE/month)': dec_data['churned'],
                        })

december_df = pd.DataFrame(december_results)
december_summary = december_df.groupby('Level').agg({
    'FTE': 'sum',
    'Recruitment (FTE/month)': 'sum',
    'Churn (FTE/month)': 'sum'
}).reset_index()

print("\nDecember snapshot results:")
print(december_summary.to_string(index=False))

print("\n\n3. COMPARISON WITH SCREENSHOT:")
print("==============================")

screenshot_data = {
    'Level': ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM'],
    'FTE': [163.0, 231.0, 418.0, 356.0, 156.0, 43.0, 409.0, 66.0],
    'Recruitment (FTE/month)': [2.076, 0.636, 0.011, 0.155, 0.000, 0.000, 0.032, 0.000],
    'Churn (FTE/month)': [0.238, 0.318, 0.168, 0.276, 0.112, 0.000, 0.206, 0.066],
}

screenshot_df = pd.DataFrame(screenshot_data)

print("Screenshot data:")
print(screenshot_df.to_string(index=False))

print("\nComparison - December vs Screenshot:")
for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    dec_row = december_summary[december_summary['Level'] == level]
    screenshot_row = screenshot_df[screenshot_df['Level'] == level]
    
    if not dec_row.empty and not screenshot_row.empty:
        dec_fte = dec_row['FTE'].iloc[0]
        screenshot_fte = screenshot_row['FTE'].iloc[0]
        
        print(f"{level}: December FTE = {dec_fte}, Screenshot FTE = {screenshot_fte}, Ratio = {dec_fte/screenshot_fte:.2f}")

print("\nComparison - Consultant-only vs Screenshot:")
for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    cons_row = consultant_summary[consultant_summary['Level'] == level]
    screenshot_row = screenshot_df[screenshot_df['Level'] == level]
    
    if not cons_row.empty and not screenshot_row.empty:
        cons_fte = cons_row['FTE'].iloc[0]
        screenshot_fte = screenshot_row['FTE'].iloc[0]
        
        print(f"{level}: Consultant FTE = {cons_fte}, Screenshot FTE = {screenshot_fte}, Ratio = {cons_fte/screenshot_fte:.2f}")

# Hypothesis 4: Check if screenshot is showing monthly rates vs annual totals
print("\n\nHypothesis 4: Units mismatch - monthly vs annual")
print("Screenshot recruitment/churn might be monthly averages, not totals")

# Let's see if the screenshot values match when we look at monthly averages
print("\nMonthly averages from December snapshot:")
for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    dec_row = december_summary[december_summary['Level'] == level]
    screenshot_row = screenshot_df[screenshot_df['Level'] == level]
    
    if not dec_row.empty and not screenshot_row.empty:
        dec_rec = dec_row['Recruitment (FTE/month)'].iloc[0]
        screenshot_rec = screenshot_row['Recruitment (FTE/month)'].iloc[0]
        
        dec_churn = dec_row['Churn (FTE/month)'].iloc[0]
        screenshot_churn = screenshot_row['Churn (FTE/month)'].iloc[0]
        
        print(f"{level}: Dec Rec = {dec_rec}, Screenshot Rec = {screenshot_rec}")
        print(f"      Dec Churn = {dec_churn}, Screenshot Churn = {screenshot_churn}")

