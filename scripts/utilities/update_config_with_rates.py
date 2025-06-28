#!/usr/bin/env python3
"""
Update office configuration with 2% churn on all levels and 3% recruitment on A-SrC levels
Preserves existing FTE values and other data
"""

import json
import os

def update_config_with_rates():
    # Load current configuration
    config_path = "backend/config/office_configuration.json"
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Define levels that should have 3% recruitment (A-SrC)
    recruitment_levels = ['A', 'AC', 'C', 'SrC']
    
    # Update each office
    for office_name, office_data in config.items():
        print(f"Updating {office_name}...")
        
        for role_name, role_data in office_data['roles'].items():
            for level_name, level_data in role_data.items():
                # Skip if level_data is not a dict (some roles might be flat)
                if not isinstance(level_data, dict):
                    continue
                
                # Update recruitment rates for A-SrC levels
                if level_name in recruitment_levels:
                    for month in range(1, 13):
                        level_data[f'recruitment_{month}'] = 0.03
                    print(f"  {role_name} {level_name}: Set recruitment to 3%")
                else:
                    # Set recruitment to 0 for other levels
                    for month in range(1, 13):
                        level_data[f'recruitment_{month}'] = 0.0
                    print(f"  {role_name} {level_name}: Set recruitment to 0%")
                
                # Update churn rates for ALL levels to 2%
                for month in range(1, 13):
                    level_data[f'churn_{month}'] = 0.02
                print(f"  {role_name} {level_name}: Set churn to 2%")
    
    # Save updated configuration
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Configuration updated successfully!")
    print(f"📊 Changes applied:")
    print(f"  - 2% churn rate on ALL levels")
    print(f"  - 3% recruitment rate on A, AC, C, SrC levels")
    print(f"  - 0% recruitment rate on other levels")
    print(f"  - Existing FTE values preserved")

if __name__ == "__main__":
    update_config_with_rates() 