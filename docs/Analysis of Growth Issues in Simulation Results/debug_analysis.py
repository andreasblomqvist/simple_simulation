import json
import pandas as pd

print("Loading JSON file...")
try:
    with open('/home/ubuntu/upload/simulation_results_20250630_161229.json', 'r') as f:
        data = json.load(f)
    print("✓ JSON loaded successfully")
    print("Top level keys:", list(data.keys()))
except Exception as e:
    print("✗ Error loading JSON:", e)
    exit(1)

print("\nChecking years structure...")
if 'years' in data:
    print("✓ 'years' key found")
    print("Years available:", list(data['years'].keys()))
    
    # Check first year structure
    first_year = list(data['years'].keys())[0]
    print(f"Checking structure of year {first_year}...")
    year_data = data['years'][first_year]
    print("Year data keys:", list(year_data.keys()))
    
    if 'offices' in year_data:
        print("✓ 'offices' key found")
        print("Offices available:", list(year_data['offices'].keys()))
        
        # Check first office
        first_office = list(year_data['offices'].keys())[0]
        print(f"Checking structure of office {first_office}...")
        office_data = year_data['offices'][first_office]
        print("Office data keys:", list(office_data.keys()))
        
        if 'levels' in office_data:
            print("✓ 'levels' key found")
            print("Roles available:", list(office_data['levels'].keys()))
            
            # Check first role
            first_role = list(office_data['levels'].keys())[0]
            role_data = office_data['levels'][first_role]
            print(f"Role {first_role} type:", type(role_data))
            
            if isinstance(role_data, dict):
                print("Role levels:", list(role_data.keys()))
                
                # Check first level
                first_level = list(role_data.keys())[0]
                level_data = role_data[first_level]
                print(f"Level {first_level} type:", type(level_data))
                print(f"Level {first_level} length:", len(level_data))
                
                if len(level_data) > 0:
                    print("First month data keys:", list(level_data[0].keys()))
                    print("Sample data:", level_data[0])
else:
    print("✗ 'years' key not found")
    exit(1)

print("\n" + "="*50)
print("STRUCTURE CONFIRMED - PROCEEDING WITH ANALYSIS")
print("="*50)

# Now do the actual analysis
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

print("\nCalculating simulation averages...")
simulation_results = {}

try:
    for year, year_data in data['years'].items():
        print(f"Processing year {year}...")
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
                        
                        # Sum across all months
                        for month_data in level_data:
                            simulation_results[level]['total_recruited'] += month_data['recruited']
                            simulation_results[level]['total_churned'] += month_data['churned']
                            simulation_results[level]['months'] += 1

    print("✓ Data processing complete")
    
    # Calculate averages
    print("\nSimulation Average Monthly Numbers:")
    print("Level | Recruited/Month | Churned/Month | Baseline Rec | Baseline Churn | Rec Diff | Churn Diff")
    print("------|-----------------|---------------|--------------|----------------|----------|------------")
    
    for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
        if level in simulation_results and level in baseline_absolute:
            sim = simulation_results[level]
            baseline = baseline_absolute[level]
            
            avg_recruited = sim['total_recruited'] / sim['months']
            avg_churned = sim['total_churned'] / sim['months']
            
            rec_diff = avg_recruited - baseline['recruitment_per_month']
            churn_diff = avg_churned - baseline['churn_per_month']
            
            print(f"{level:5} | {avg_recruited:15.3f} | {avg_churned:13.3f} | {baseline['recruitment_per_month']:12.3f} | {baseline['churn_per_month']:14.3f} | {rec_diff:8.3f} | {churn_diff:10.3f}")
    
    print("\nAnalysis complete!")
    
except Exception as e:
    print("✗ Error during analysis:", e)
    import traceback
    traceback.print_exc()

