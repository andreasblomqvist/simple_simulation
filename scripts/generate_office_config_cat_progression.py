#!/usr/bin/env python3
"""
Generate office configuration Excel file with CAT-based progression timing
- Progression only happens in January (month 1) and June (month 6)
- Uses proper half-yearly progression rates by level
- All other months have 0% progression
"""

import sys
import os
from datetime import datetime

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config.default_config import ACTUAL_OFFICE_LEVEL_DATA, BASE_PRICING, BASE_SALARIES, DEFAULT_RATES
import pandas as pd

# Half-yearly progression rates (from user data)
HALF_YEARLY_PROGRESSION_RATES = {
    'C->SrC': 0.26,    # 26% half-yearly
    'SrC->AM': 0.20,   # 20% half-yearly
    'AM->M': 0.07,     # 7% half-yearly
    'M->SrM': 0.12,    # 12% half-yearly
    'SrM->PiP': 0.14   # 14% half-yearly
}

def get_progression_rate_for_level(level_name: str) -> float:
    """Get appropriate progression rate for a level"""
    progression_mapping = {
        'A': HALF_YEARLY_PROGRESSION_RATES['C->SrC'],      # Assume A follows similar pattern
        'AC': HALF_YEARLY_PROGRESSION_RATES['C->SrC'],     # Assume AC follows similar pattern  
        'C': HALF_YEARLY_PROGRESSION_RATES['C->SrC'],      # 26%
        'SrC': HALF_YEARLY_PROGRESSION_RATES['SrC->AM'],   # 20%
        'AM': HALF_YEARLY_PROGRESSION_RATES['AM->M'],      # 7%
        'M': HALF_YEARLY_PROGRESSION_RATES['M->SrM'],      # 12%
        'SrM': HALF_YEARLY_PROGRESSION_RATES['SrM->PiP'],  # 14%
        'PiP': 0.0  # No progression from PiP
    }
    return progression_mapping.get(level_name, 0.0)

def generate_cat_progression_config():
    """Generate office configuration with CAT-based progression timing"""
    rows = []
    
    print("🎯 Generating CAT-Based Progression Configuration")
    print("=" * 60)
    print("✅ Progression Timing: January (month 1) and June (month 6)")
    print("✅ All other months: 0% progression")
    print("✅ Half-yearly progression rates:")
    for transition, rate in HALF_YEARLY_PROGRESSION_RATES.items():
        print(f"   {transition}: {rate:.0%}")
    print("")
    
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
                        if role_name in DEFAULT_RATES['recruitment'] and isinstance(DEFAULT_RATES['recruitment'][role_name], dict):
                            recruitment_rate = DEFAULT_RATES['recruitment'][role_name].get(level_name, 0.01)
                        else:
                            recruitment_rate = 0.01
                        
                        if role_name in DEFAULT_RATES['churn'] and isinstance(DEFAULT_RATES['churn'][role_name], dict):
                            churn_rate = DEFAULT_RATES['churn'][role_name].get(level_name, 0.014)
                        elif role_name in DEFAULT_RATES['churn']:
                            churn_rate = DEFAULT_RATES['churn'][role_name]
                        else:
                            churn_rate = 0.014
                        
                        # Get CAT-based progression rate for this level
                        progression_rate = get_progression_rate_for_level(level_name)
                        
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
                            
                            # CAT-based progression: Only January (1) and June (6)
                            if i in [1, 6]:  # January and June
                                row[f'Progression_{i}'] = progression_rate
                            else:
                                row[f'Progression_{i}'] = 0.0
                            
                            row[f'UTR_{i}'] = DEFAULT_RATES['utr']
                        
                        rows.append(row)
        
        # Process Operations (flat role - no progression)
        if 'Operations' in office_data and office_data['Operations'] > 0:
            operations_fte = office_data['Operations']
            base_prices = BASE_PRICING.get(office_name, BASE_PRICING['Stockholm'])
            base_salaries = BASE_SALARIES.get(office_name, BASE_SALARIES['Stockholm'])
            op_price = base_prices.get('Operations', 80.0)
            op_salary = base_salaries.get('Operations', 40000.0)
            
            operations_recruitment = DEFAULT_RATES['recruitment'].get('Operations', 0.021)
            operations_churn = DEFAULT_RATES['churn'].get('Operations', 0.0149)
            
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
                row[f'UTR_{i}'] = DEFAULT_RATES['utr']
            
            rows.append(row)
    
    # Create DataFrame and save to Excel with timestamp
    df = pd.DataFrame(rows)
    
    # Generate timestamp filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'office_config_cat_progression_{timestamp}.xlsx'
    
    # Ensure we're in the scripts directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)
    
    df.to_excel(filepath, index=False)
    
    print(f"✅ Generated {filename} with {len(df)} rows")
    print(f"📁 Saved to: {filepath}")
    
    # Show progression timing verification
    print(f"\n🎯 Progression Timing Verification:")
    sample_consultant = df[(df['Role'] == 'Consultant') & (df['Level'] == 'C')].iloc[0] if len(df[df['Role'] == 'Consultant']) > 0 else None
    if sample_consultant is not None:
        for month in range(1, 13):
            prog_rate = sample_consultant[f'Progression_{month}']
            if prog_rate > 0:
                month_name = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][month]
                print(f"   {month_name} (month {month}): {prog_rate:.0%} progression")
    
    # Show summary
    print(f"\n📊 Summary:")
    print(f"   Timestamp: {timestamp}")
    print(f"   Offices: {df['Office'].nunique()}")
    print(f"   Total rows: {len(df)}")
    print(f"   Roles with progression: {len(df[(df['Role'] != 'Operations') & (df['Progression_1'] > 0)])}")
    print(f"   Operations rows: {len(df[df['Role'] == 'Operations'])}")
    
    # Show progression rates by level
    print(f"\n📈 Progression Rates by Level:")
    for level in ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']:
        level_data = df[df['Level'] == level]
        if not level_data.empty:
            prog_rate = level_data.iloc[0]['Progression_1']  # January rate
            print(f"   {level}: {prog_rate:.0%} (Jan/Jun)")
    
    return filepath

if __name__ == "__main__":
    generate_cat_progression_config() 