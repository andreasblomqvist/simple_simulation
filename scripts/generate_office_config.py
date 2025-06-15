import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os
import importlib

# Add the parent directory to the Python path to import from simple_simulation
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import and reload the default_config module
from simple_simulation.config.default_config import (
    OFFICE_HEADCOUNT,
    ROLE_DISTRIBUTION,
    CONSULTANT_LEVEL_DISTRIBUTION,
    DEFAULT_RATES,
    BASE_PRICING,
    BASE_SALARIES,
    get_monthly_pricing,
    get_monthly_salaries,
    get_monthly_rates,
    CURRENCY_CONFIG,
    ACTUAL_OFFICE_LEVEL_DATA
)

# Force reload the module to ensure we get the latest values
importlib.reload(sys.modules['simple_simulation.config.default_config'])

def generate_office_config():
    """
    Generate office configuration using real headcount data from ACTUAL_OFFICE_LEVEL_DATA
    All monetary values (prices and salaries) are in SEK (Swedish Krona)
    """
    data = []
    
    for office_name in OFFICE_HEADCOUNT.keys():
        # Get actual office data
        office_data = ACTUAL_OFFICE_LEVEL_DATA.get(office_name, {})
        
        # Get pricing and salary base values (already in SEK from default_config.py)
        office_pricing = BASE_PRICING.get(office_name, BASE_PRICING['Stockholm'])
        office_salaries = BASE_SALARIES.get(office_name, BASE_SALARIES['Stockholm'])
        
        # Get monthly rates
        monthly_rates = get_monthly_rates()
        
        # Add roles with levels (Consultant, Sales, Recruitment)
        for role_name in ['Consultant', 'Sales', 'Recruitment']:
            role_levels = office_data.get(role_name, {})
            
            for level, fte in role_levels.items():
                if fte > 0:  # Only add levels with actual FTE
                    base_price = office_pricing.get(level, office_pricing.get('A', 1000))  # Default fallback
                    base_salary = office_salaries.get(level, office_salaries.get('A', 40000))  # Default fallback
                    
                    row = {
                        'Office': office_name,
                        'Role': role_name,
                        'Level': level,
                        'FTE': fte,
                        **get_monthly_pricing(base_price),
                        **get_monthly_salaries(base_salary),
                        **monthly_rates
                    }
                    
                    # Adjust progression rates for M+ levels (only November)
                    if level in ['M', 'SrM', 'PiP']:
                        for i in range(1, 13):
                            if i == 11:  # November only for senior levels
                                row[f'progression_{i}'] = DEFAULT_RATES['progression']['M_plus_rate']
                            else:
                                row[f'progression_{i}'] = DEFAULT_RATES['progression']['non_evaluation_rate']
                    
                    data.append(row)
        
        # Add Operations (flat role) using real data
        operations_fte = office_data.get('Operations', 0)
        if operations_fte > 0:
            # Operations base values in SEK
            operations_base_price = 80.0 * CURRENCY_CONFIG['conversion_to_sek']['EUR']  # Convert EUR to SEK
            operations_base_salary = 40000.0  # SEK per month
            
            row = {
                'Office': office_name,
                'Role': 'Operations',
                'Level': None,
                'FTE': operations_fte,
                **get_monthly_pricing(operations_base_price),
                **get_monthly_salaries(operations_base_salary),
                **monthly_rates
            }
            
            # Operations has no progression
            for i in range(1, 13):
                row[f'progression_{i}'] = 0.0
            
            data.append(row)
    
    return data

if __name__ == "__main__":
    # Generate configuration
    config_data = generate_office_config()
    
    # Create DataFrame
    df = pd.DataFrame(config_data)
    
    # Save to Excel with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'office_config_{timestamp}.xlsx'
    df.to_excel(output_file, index=False)
    print(f"Generated {output_file}")
    print(f"Total rows: {len(config_data)}")
    print(f"Offices: {len(OFFICE_HEADCOUNT)}")
    print(f"Total FTE: {df['FTE'].sum()}")
    print("Note: All monetary values (prices and salaries) are in SEK") 