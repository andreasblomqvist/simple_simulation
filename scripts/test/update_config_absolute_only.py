#!/usr/bin/env python3
"""
Script to update the configuration file to use only absolute values.
- Remove all percentage-based recruitment and churn fields
- Set recruitment to 0 for all roles
- Distribute a global churn of 20/month for Consultant A across all offices, weighted by A FTE
- All other churns 0
- Focus only on consultants
"""

import json
import os
import sys

def update_config_absolute_only():
    """Update configuration to use only absolute values."""
    
    config_path = "../../backend/config/office_configuration.json"
    
    print("Loading configuration file...")
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print("Calculating total Consultant A FTE across all offices...")
    total_A_fte = 0
    office_A_fte = {}
    for office_name, office_data in config.items():
        consultant = office_data.get('roles', {}).get('Consultant', {})
        A_level = consultant.get('A', {})
        fte = A_level.get('fte', 0)
        office_A_fte[office_name] = fte
        total_A_fte += fte
    print(f"Total Consultant A FTE: {total_A_fte}")
    
    print("Updating configuration...")
    for office_name, office_data in config.items():
        print(f"Processing office: {office_name}")
        # Keep only Consultant role, remove Sales and Recruitment
        if 'roles' in office_data:
            consultant_role = office_data['roles'].get('Consultant', {})
            office_data['roles'] = {'Consultant': consultant_role}
        # Update Consultant role
        if 'Consultant' in office_data['roles']:
            consultant_data = office_data['roles']['Consultant']
            for level_name, level_data in consultant_data.items():
                print(f"  Updating level: {level_name}")
                # Remove percentage-based fields
                fields_to_remove = []
                for key in list(level_data.keys()):
                    if key.startswith('recruitment_') and not key.startswith('recruitment_abs_'):
                        fields_to_remove.append(key)
                    elif key.startswith('churn_') and not key.startswith('churn_abs_'):
                        fields_to_remove.append(key)
                for field in fields_to_remove:
                    del level_data[field]
                # Set recruitment to 0 for all months
                for month in range(1, 13):
                    level_data[f'recruitment_abs_{month}'] = 0
                # Set churn: only Consultant A gets distributed churn, others 0
                if level_name == 'A' and total_A_fte > 0:
                    # Weighted churn for this office
                    churn_val = round(20 * (office_A_fte[office_name] / total_A_fte))
                else:
                    churn_val = 0
                for month in range(1, 13):
                    level_data[f'churn_abs_{month}'] = churn_val
    # Update total FTE calculation
    for office_name, office_data in config.items():
        if 'roles' in office_data and 'Consultant' in office_data['roles']:
            total_fte = 0
            consultant_data = office_data['roles']['Consultant']
            for level_name, level_data in consultant_data.items():
                if 'fte' in level_data:
                    total_fte += level_data['fte']
            office_data['total_fte'] = total_fte
            print(f"Updated {office_name} total FTE: {total_fte}")
    # Save updated configuration
    backup_path = config_path + ".backup"
    print(f"Creating backup: {backup_path}")
    with open(backup_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Saving updated configuration: {config_path}")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print("Configuration updated successfully!")
    print("Changes made:")
    print("- Removed all percentage-based recruitment and churn fields")
    print("- Set recruitment to 0 for all roles")
    print("- Distributed global churn of 20/month for Consultant A across offices, weighted by A FTE")
    print("- All other churns set to 0")
    print("- Removed Sales and Recruitment roles, kept only Consultant")
    print("- Updated total FTE calculations")

if __name__ == "__main__":
    update_config_absolute_only() 