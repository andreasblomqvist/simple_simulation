#!/usr/bin/env python3
"""
Script to split PiP (Principal/Partner) levels into separate Pi (Principal) and P (Partner) levels
in the office configuration file.
"""

import json
import os
import shutil
from datetime import datetime

def split_pip_levels():
    """Split PiP entries into separate Pi and P entries."""
    
    config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'office_configuration.json')
    
    # Create backup
    backup_file = f"{config_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(config_file, backup_file)
    print(f"Created backup: {backup_file}")
    
    # Load configuration
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Process each office
    for office_name, office_data in config.items():
        if 'roles' in office_data:
            for role_name, role_data in office_data['roles'].items():
                if 'PiP' in role_data:
                    pip_data = role_data['PiP']
                    
                    # Split the FTE roughly in half (60% Pi, 40% P)
                    total_fte = pip_data.get('fte', 0)
                    pi_fte = round(total_fte * 0.6)
                    p_fte = total_fte - pi_fte
                    
                    # Create Pi entry (Principal level)
                    pi_data = pip_data.copy()
                    pi_data['fte'] = pi_fte
                    
                    # Create P entry (Partner level) 
                    p_data = pip_data.copy()
                    p_data['fte'] = p_fte
                    
                    # Adjust salaries - Partners typically earn more
                    for i in range(1, 13):  # 12 months
                        salary_key = f'salary_{i}'
                        price_key = f'price_{i}'
                        
                        if salary_key in p_data:
                            # Increase Partner salary by 20%
                            p_data[salary_key] = round(p_data[salary_key] * 1.2)
                        
                        if price_key in p_data:
                            # Increase Partner price by 15%
                            p_data[price_key] = round(p_data[price_key] * 1.15, 2)
                    
                    # Remove old PiP entry and add new Pi and P entries
                    del role_data['PiP']
                    role_data['Pi'] = pi_data
                    role_data['P'] = p_data
                    
                    print(f"Split {office_name} {role_name} PiP ({total_fte} FTE) -> Pi ({pi_fte} FTE) + P ({p_fte} FTE)")
    
    # Save updated configuration
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Updated configuration saved to {config_file}")
    print("PiP levels have been successfully split into Pi and P levels!")

if __name__ == '__main__':
    split_pip_levels()