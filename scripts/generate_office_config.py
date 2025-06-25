#!/usr/bin/env python3
"""
Generate a timestamped office configuration Excel file with current data
Files are saved in the scripts directory with timestamp format: office_config_YYYYMMDD_HHMMSS.xlsx
"""

import sys
import os
from datetime import datetime
import pandas as pd
import json

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.config.default_config import ACTUAL_OFFICE_LEVEL_DATA, BASE_PRICING, BASE_SALARIES

def get_default_recruitment_rate(role_name, level_name):
    """Get default recruitment rate - simplified without DEFAULT_RATES"""
    return 0.01  # Simple 1% default

def get_default_churn_rate(role_name, level_name):
    """Get default churn rate - simplified without DEFAULT_RATES"""
    return 0.014  # Simple 1.4% default

def get_default_progression_rate(level_name):
    """Get default progression rate - simplified without DEFAULT_RATES"""
    return 0.0  # No default progression

def generate_office_config():
    """Generate timestamped office configuration Excel file"""
    rows = []
    
    # Process all offices
    for office_name, office_data in ACTUAL_OFFICE_LEVEL_DATA.items():
        
        # Process roles with levels (Consultant, Sales, Recruitment)
        for role_name in ['Consultant', 'Sales', 'Recruitment']:
            if role_name in office_data:
                for level_name, fte in office_data[role_name].items():
                    if fte > 0:  # Only include levels with actual FTE
                        # Get pricing and salary
                        base_prices = BASE_PRICING.get(office_name, BASE_PRICING['Stockholm'])
                        base_salaries = BASE_SALARIES.get(office_name, BASE_SALARIES['Stockholm'])
                        price = base_prices.get(level_name, 0.0)
                        salary = base_salaries.get(level_name, 0.0)
                        
                        # Get rates
                        recruitment_rate = get_default_recruitment_rate(role_name, level_name)
                        churn_rate = get_default_churn_rate(role_name, level_name)
                        
                        # Set progression rate based on level
                        progression_rate = get_default_progression_rate(level_name)
                        
                        # Create row
                        row = {
                            'Office': office_name,
                            'Role': role_name,
                            'Level': level_name,
                            'FTE': fte
                        }
                        
                        # Add monthly values (1-12)
                        for i in range(1, 13):
                            row[f'Price_{i}'] = price * (1 + 0.0025 * (i - 1))
                            row[f'Salary_{i}'] = salary * (1 + 0.0025 * (i - 1))
                            row[f'Recruitment_{i}'] = recruitment_rate
                            row[f'Churn_{i}'] = churn_rate
                            row[f'Progression_{i}'] = progression_rate if i in [1, 6] else 0.0
                            row[f'UTR_{i}'] = 0.0  # Assuming default UTR
                        
                        rows.append(row)
        
        # Process Operations (flat role)
        if 'Operations' in office_data and office_data['Operations'] > 0:
            operations_fte = office_data['Operations']
            base_prices = BASE_PRICING.get(office_name, BASE_PRICING['Stockholm'])
            base_salaries = BASE_SALARIES.get(office_name, BASE_SALARIES['Stockholm'])
            op_price = base_prices.get('Operations', 80.0)
            op_salary = base_salaries.get('Operations', 40000.0)
            
            operations_recruitment = get_default_recruitment_rate('Operations', None)
            operations_churn = get_default_churn_rate('Operations', None)
            
            # Create row
            row = {
                'Office': office_name,
                'Role': 'Operations',
                'Level': None,  # Operations has no levels
                'FTE': operations_fte
            }
            
            # Add monthly values (1-12)
            for i in range(1, 13):
                row[f'Price_{i}'] = op_price * (1 + 0.0025 * (i - 1))
                row[f'Salary_{i}'] = op_salary * (1 + 0.0025 * (i - 1))
                row[f'Recruitment_{i}'] = operations_recruitment
                row[f'Churn_{i}'] = operations_churn
                row[f'Progression_{i}'] = 0.0  # Operations has no progression
                row[f'UTR_{i}'] = 0.0  # Assuming default UTR
            
            rows.append(row)
    
    # Create DataFrame and save to Excel with timestamp
    df = pd.DataFrame(rows)
    
    # Generate timestamp filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'office_config_{timestamp}.xlsx'
    
    # Ensure we're in the scripts directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)
    
    df.to_excel(filepath, index=False)
    
    print(f"✅ Generated {filename} with {len(df)} rows")
    print(f"📁 Saved to: {filepath}")
    
    # Verify Stockholm Operations
    stockholm_ops = df[(df['Office'] == 'Stockholm') & (df['Role'] == 'Operations')]
    if not stockholm_ops.empty:
        print(f"✅ Stockholm Operations FTE: {stockholm_ops['FTE'].iloc[0]}")
    else:
        print("❌ Stockholm Operations not found")
    
    # Show summary
    print(f"\n📊 Summary:")
    print(f"   Timestamp: {timestamp}")
    print(f"   Offices: {df['Office'].nunique()}")
    print(f"   Total rows: {len(df)}")
    print(f"   Operations rows: {len(df[df['Role'] == 'Operations'])}")
    print(f"   Operations recruitment rate: {operations_recruitment}")
    print(f"   Operations churn rate: {operations_churn}")
    
    return filepath

if __name__ == "__main__":
    generate_office_config() 