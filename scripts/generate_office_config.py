import pandas as pd
import numpy as np
from datetime import datetime

# Define offices and their total FTE
OFFICE_FTE = {
    'Stockholm': 850,
    'Munich': 450,
    'Hamburg': 200,
    'Helsinki': 120,
    'Oslo': 120,
    'Berlin': 100,
    'Copenhagen': 100,
    'Zurich': 50,
    'Frankfurt': 50,
    'Cologne': 30,
    'Amsterdam': 30,
    'Toronto': 10,
    'London': 2
}

ROLES_WITH_LEVELS = ['Consultant', 'Sales', 'Recruitment']
FLAT_ROLE = 'Operations'
CONSULTANT_LEVELS = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']

# Base values for levels
base_price = {
    'A': 106.09, 'AC': 127.31, 'C': 159.13, 'SrC': 190.96, 
    'AM': 233.40, 'M': 297.05, 'SrM': 371.31, 'PiP': 477.41
}
base_salary = {
    'A': 53.05, 'AC': 63.65, 'C': 79.57, 'SrC': 95.48, 
    'AM': 116.70, 'M': 148.53, 'SrM': 185.66, 'PiP': 238.70
}

# Role percentages
SALES_PCT = 0.06  # 6%
RECRUITMENT_PCT = 0.04  # 4%
OPERATIONS_PCT = 0.04  # 4%
CONSULTANT_PCT = 0.86  # 86%

# Generate data
data = []

for office, total_fte in OFFICE_FTE.items():
    # Calculate role FTEs
    sales_fte = round(total_fte * SALES_PCT)
    recruitment_fte = round(total_fte * RECRUITMENT_PCT)
    operations_fte = round(total_fte * OPERATIONS_PCT)
    consultant_fte = total_fte - sales_fte - recruitment_fte - operations_fte

    # Consultant levels (distribute remaining FTE)
    consultant_per_level = round(consultant_fte / len(CONSULTANT_LEVELS))
    remaining_consultant = consultant_fte - (consultant_per_level * len(CONSULTANT_LEVELS))
    
    # Sales and Recruitment levels (distribute evenly)
    sales_per_level = round(sales_fte / len(CONSULTANT_LEVELS))
    recruitment_per_level = round(recruitment_fte / len(CONSULTANT_LEVELS))
    
    # Add Consultant rows
    for level in CONSULTANT_LEVELS:
        fte = consultant_per_level + (1 if remaining_consultant > 0 else 0)
        remaining_consultant -= 1 if remaining_consultant > 0 else 0
        
        data.append({
            'Office': office,
            'Role': 'Consultant',
            'Level': level,
            'FTE': fte,
            'Price_H1': base_price[level],
            'Price_H2': base_price[level] * 1.03,  # 3% increase
            'Salary_H1': base_salary[level],
            'Salary_H2': base_salary[level] * 1.03,  # 3% increase
            'Recruitment_H1': 0.1,
            'Recruitment_H2': 0.1,
            'Churn_H1': 0.05,
            'Churn_H2': 0.05,
            'Progression_H1': 0.15,
            'Progression_H2': 0.15,
            'UTR_H1': 0.85,
            'UTR_H2': 0.85
        })
    
    # Add Sales rows
    for level in CONSULTANT_LEVELS:
        data.append({
            'Office': office,
            'Role': 'Sales',
            'Level': level,
            'FTE': sales_per_level,
            'Price_H1': base_price[level],
            'Price_H2': base_price[level] * 1.03,
            'Salary_H1': base_salary[level],
            'Salary_H2': base_salary[level] * 1.03,
            'Recruitment_H1': 0.1,
            'Recruitment_H2': 0.1,
            'Churn_H1': 0.05,
            'Churn_H2': 0.05,
            'Progression_H1': 0.15,
            'Progression_H2': 0.15,
            'UTR_H1': 0.85,
            'UTR_H2': 0.85
        })
    
    # Add Recruitment rows
    for level in CONSULTANT_LEVELS:
        data.append({
            'Office': office,
            'Role': 'Recruitment',
            'Level': level,
            'FTE': recruitment_per_level,
            'Price_H1': base_price[level],
            'Price_H2': base_price[level] * 1.03,
            'Salary_H1': base_salary[level],
            'Salary_H2': base_salary[level] * 1.03,
            'Recruitment_H1': 0.1,
            'Recruitment_H2': 0.1,
            'Churn_H1': 0.05,
            'Churn_H2': 0.05,
            'Progression_H1': 0.15,
            'Progression_H2': 0.15,
            'UTR_H1': 0.85,
            'UTR_H2': 0.85
        })
    
    # Add Operations row (flat role)
    data.append({
        'Office': office,
        'Role': 'Operations',
        'Level': None,
        'FTE': operations_fte,
        'Price_H1': 80.0,
        'Price_H2': 82.4,
        'Salary_H1': 40.0,
        'Salary_H2': 41.2,
        'Recruitment_H1': 0.1,
        'Recruitment_H2': 0.1,
        'Churn_H1': 0.05,
        'Churn_H2': 0.05,
        'Progression_H1': 0.0,
        'Progression_H2': 0.0,
        'UTR_H1': 0.85,
        'UTR_H2': 0.85
    })

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel with timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file = f'scripts/office_config_{timestamp}.xlsx'
df.to_excel(output_file, index=False)
print(f"Generated {output_file}") 