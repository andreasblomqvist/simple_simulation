import pandas as pd
import sys
import os

# Add parent directory to path to import config
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
sys.path.append(os.path.join(parent_dir, 'simple_simulation', 'config'))

from default_config import ACTUAL_OFFICE_LEVEL_DATA, BASE_PRICING, BASE_SALARIES, DEFAULT_RATES

# Define the structure
ROLES_WITH_LEVELS = ['Consultant', 'Sales', 'Recruitment']
FLAT_ROLES = ['Operations']
LEVELS = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']

# Create data for Excel
data = []

for office_name, office_data in ACTUAL_OFFICE_LEVEL_DATA.items():
    # Get pricing and salary data for this office
    base_prices = BASE_PRICING.get(office_name, BASE_PRICING['Stockholm'])
    base_salaries = BASE_SALARIES.get(office_name, BASE_SALARIES['Stockholm'])
    
    # Process roles with levels
    for role_name in ROLES_WITH_LEVELS:
        role_levels = office_data.get(role_name, {})
        for level_name in LEVELS:
            fte = role_levels.get(level_name, 0)
            if fte > 0:  # Only include levels with actual FTE
                price = base_prices.get(level_name, 0.0)
                salary = base_salaries.get(level_name, 0.0)
                
                row = {
                    'Office': office_name,
                    'Role': role_name,
                    'Level': level_name,
                    'FTE': fte
                }
                
                # Add monthly columns
                for month in range(1, 13):
                    # Add slight monthly increase (0.25% per month)
                    monthly_price = price * (1 + 0.0025 * (month - 1))
                    monthly_salary = salary * (1 + 0.0025 * (month - 1))
                    
                    row[f'Price_{month}'] = monthly_price
                    row[f'Salary_{month}'] = monthly_salary
                    row[f'Recruitment_{month}'] = DEFAULT_RATES['recruitment']
                    row[f'Churn_{month}'] = DEFAULT_RATES['churn']
                    row[f'UTR_{month}'] = DEFAULT_RATES['utr']
                    
                    # Set progression rate based on level and month
                    if month in DEFAULT_RATES['progression']['evaluation_months']:
                        if level_name in ['M', 'SrM', 'PiP']:
                            # M+ levels only progress in November
                            if month == 11:
                                progression_rate = DEFAULT_RATES['progression']['M_plus_rate']
                            else:
                                progression_rate = DEFAULT_RATES['progression']['non_evaluation_rate']
                        else:
                            # A-AM levels progress in May and November
                            progression_rate = DEFAULT_RATES['progression']['A_AM_rate']
                    else:
                        progression_rate = DEFAULT_RATES['progression']['non_evaluation_rate']
                    
                    row[f'Progression_{month}'] = progression_rate
                
                data.append(row)
    
    # Process flat roles (Operations)
    for role_name in FLAT_ROLES:
        fte = office_data.get(role_name, 0)
        if fte > 0:
            price = base_prices.get('Operations', 80.0)
            salary = base_salaries.get('Operations', 40000.0)
            
            row = {
                'Office': office_name,
                'Role': role_name,
                'Level': '',  # No level for flat roles
                'FTE': fte
            }
            
            # Add monthly columns
            for month in range(1, 13):
                monthly_price = price * (1 + 0.0025 * (month - 1))
                monthly_salary = salary * (1 + 0.0025 * (month - 1))
                
                row[f'Price_{month}'] = monthly_price
                row[f'Salary_{month}'] = monthly_salary
                row[f'Recruitment_{month}'] = DEFAULT_RATES['recruitment']
                row[f'Churn_{month}'] = DEFAULT_RATES['churn']
                row[f'UTR_{month}'] = DEFAULT_RATES['utr']
                # Operations doesn't have progression
                row[f'Progression_{month}'] = 0.0
            
            data.append(row)

# Create DataFrame and save to Excel
df = pd.DataFrame(data)

# Reorder columns to have basic info first, then monthly data
basic_cols = ['Office', 'Role', 'Level', 'FTE']
monthly_cols = []
for month in range(1, 13):
    monthly_cols.extend([f'Price_{month}', f'Salary_{month}', f'Recruitment_{month}', f'Churn_{month}', f'Progression_{month}', f'UTR_{month}'])

df = df[basic_cols + monthly_cols]

# Save to Excel
filename = 'office_config_monthly.xlsx'
df.to_excel(filename, index=False)
print(f"Excel file '{filename}' has been created successfully!")
print(f"Total rows: {len(df)}")
print(f"Total FTE: {df['FTE'].sum()}") 