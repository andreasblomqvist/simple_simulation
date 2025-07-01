import json
import pandas as pd

# Load the simulation data
with open('/home/ubuntu/upload/simulation_results_20250630_161229.json', 'r') as f:
    data = json.load(f)

print("=== SINGLE OFFICE ANALYSIS ===")
print()

# Let's analyze each office individually to see which one matches the screenshot
screenshot_data = {
    'Level': ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM'],
    'FTE': [163.0, 231.0, 418.0, 356.0, 156.0, 43.0, 409.0, 66.0],
    'Recruitment (FTE/month)': [2.076, 0.636, 0.011, 0.155, 0.000, 0.000, 0.032, 0.000],
    'Churn (FTE/month)': [0.238, 0.318, 0.168, 0.276, 0.112, 0.000, 0.206, 0.066],
}

screenshot_df = pd.DataFrame(screenshot_data)

for year, year_data in data['years'].items():
    for office_name, office_data in year_data['offices'].items():
        print(f"\n{'='*50}")
        print(f"OFFICE: {office_name}")
        print(f"{'='*50}")
        
        office_results = []
        
        # Aggregate all roles for this office
        for role, role_data in office_data['levels'].items():
            if isinstance(role_data, dict):
                for level, level_data in role_data.items():
                    # Calculate annual averages
                    total_fte = sum(month['total'] for month in level_data)
                    total_recruited = sum(month['recruited'] for month in level_data)
                    total_churned = sum(month['churned'] for month in level_data)
                    
                    avg_fte = total_fte / 12
                    avg_recruited_per_month = total_recruited / 12
                    avg_churned_per_month = total_churned / 12
                    
                    office_results.append({
                        'Level': level,
                        'FTE': avg_fte,
                        'Recruitment (FTE/month)': avg_recruited_per_month,
                        'Churn (FTE/month)': avg_churned_per_month,
                    })
        
        if office_results:
            office_df = pd.DataFrame(office_results)
            office_summary = office_df.groupby('Level').agg({
                'FTE': 'sum',
                'Recruitment (FTE/month)': 'sum',
                'Churn (FTE/month)': 'sum'
            }).reset_index()
            
            # Round for display
            office_summary['FTE'] = office_summary['FTE'].round(1)
            office_summary['Recruitment (FTE/month)'] = office_summary['Recruitment (FTE/month)'].round(3)
            office_summary['Churn (FTE/month)'] = office_summary['Churn (FTE/month)'].round(3)
            
            print(f"\n{office_name} Results:")
            print(office_summary.to_string(index=False))
            
            # Calculate match score with screenshot
            total_diff = 0
            matches = 0
            
            print(f"\nComparison with Screenshot:")
            for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
                office_row = office_summary[office_summary['Level'] == level]
                screenshot_row = screenshot_df[screenshot_df['Level'] == level]
                
                if not office_row.empty and not screenshot_row.empty:
                    office_fte = office_row['FTE'].iloc[0]
                    screenshot_fte = screenshot_row['FTE'].iloc[0]
                    
                    office_rec = office_row['Recruitment (FTE/month)'].iloc[0]
                    screenshot_rec = screenshot_row['Recruitment (FTE/month)'].iloc[0]
                    
                    office_churn = office_row['Churn (FTE/month)'].iloc[0]
                    screenshot_churn = screenshot_row['Churn (FTE/month)'].iloc[0]
                    
                    fte_diff = abs(office_fte - screenshot_fte)
                    rec_diff = abs(office_rec - screenshot_rec)
                    churn_diff = abs(office_churn - screenshot_churn)
                    
                    total_diff += fte_diff + rec_diff + churn_diff
                    matches += 1
                    
                    print(f"{level}: FTE {office_fte:.1f} vs {screenshot_fte:.1f} (diff: {fte_diff:.1f})")
                    print(f"     Rec {office_rec:.3f} vs {screenshot_rec:.3f} (diff: {rec_diff:.3f})")
                    print(f"     Churn {office_churn:.3f} vs {screenshot_churn:.3f} (diff: {churn_diff:.3f})")
            
            avg_diff = total_diff / matches if matches > 0 else float('inf')
            print(f"\nAverage difference: {avg_diff:.3f}")
            
            # Check if this is a very close match
            if avg_diff < 10:  # Threshold for "close match"
                print(f"*** {office_name} appears to be a CLOSE MATCH to the screenshot! ***")

# Let's also check if the screenshot might be showing just the Consultant role from one office
print(f"\n\n{'='*60}")
print("CONSULTANT-ONLY ANALYSIS BY OFFICE")
print(f"{'='*60}")

for year, year_data in data['years'].items():
    for office_name, office_data in year_data['offices'].items():
        consultant_data = office_data['levels'].get('Consultant', {})
        
        if isinstance(consultant_data, dict):
            consultant_results = []
            
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
            
            if consultant_results:
                consultant_df = pd.DataFrame(consultant_results)
                
                # Calculate match score with screenshot for consultant data
                total_diff = 0
                matches = 0
                
                for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
                    cons_row = consultant_df[consultant_df['Level'] == level]
                    screenshot_row = screenshot_df[screenshot_df['Level'] == level]
                    
                    if not cons_row.empty and not screenshot_row.empty:
                        cons_fte = cons_row['FTE'].iloc[0]
                        screenshot_fte = screenshot_row['FTE'].iloc[0]
                        
                        fte_diff = abs(cons_fte - screenshot_fte)
                        total_diff += fte_diff
                        matches += 1
                
                avg_diff = total_diff / matches if matches > 0 else float('inf')
                
                if avg_diff < 50:  # Only show offices with reasonable matches
                    print(f"\n{office_name} - Consultant Only:")
                    print(consultant_df.to_string(index=False))
                    print(f"Average FTE difference: {avg_diff:.1f}")
                    
                    if avg_diff < 10:
                        print(f"*** {office_name} Consultant data appears to be a CLOSE MATCH! ***")

