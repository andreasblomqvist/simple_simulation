#!/usr/bin/env python3
"""
Script to set all price fields to 0 for non-consultant roles in office_configuration.json
Non-consultant roles: Operations, Sales, Recruitment
"""

import json
import os
from pathlib import Path

def set_non_consultant_prices_to_zero():
    """Set all price fields to 0 for non-consultant roles"""
    
    # Path to the configuration file
    config_path = Path("backend/config/office_configuration.json")
    
    # Non-consultant roles to modify
    non_consultant_roles = ["Operations", "Sales", "Recruitment"]
    
    # Price fields to set to 0
    price_fields = [
        "price_1", "price_2", "price_3", "price_4", "price_5", "price_6",
        "price_7", "price_8", "price_9", "price_10", "price_11", "price_12",
        "price"
    ]
    
    print(f"Loading configuration from {config_path}")
    
    # Load the configuration
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    total_offices = len(config)
    total_roles_modified = 0
    total_price_fields_modified = 0
    
    print(f"Processing {total_offices} offices...")
    
    # Process each office
    for office_name, office_data in config.items():
        print(f"Processing office: {office_name}")
        
        if "roles" not in office_data:
            print(f"  Warning: No roles found in {office_name}")
            continue
        
        roles = office_data["roles"]
        
        # Process each role
        for role_name, role_data in roles.items():
            if role_name in non_consultant_roles:
                print(f"  Modifying non-consultant role: {role_name}")
                total_roles_modified += 1
                
                # Handle different role structures
                if isinstance(role_data, dict):
                    # Check if this role has levels (like Recruitment with A, AC, etc.)
                    if any(isinstance(v, dict) for v in role_data.values()):
                        # Role has levels (like Recruitment)
                        for level_name, level_data in role_data.items():
                            if isinstance(level_data, dict):
                                for field in price_fields:
                                    if field in level_data:
                                        old_value = level_data[field]
                                        level_data[field] = 0
                                        total_price_fields_modified += 1
                                        print(f"    {level_name}: {field} = {old_value} → 0")
                    else:
                        # Role is flat (like Operations)
                        for field in price_fields:
                            if field in role_data:
                                old_value = role_data[field]
                                role_data[field] = 0
                                total_price_fields_modified += 1
                                print(f"    {field} = {old_value} → 0")
    
    print(f"\nSummary:")
    print(f"  Offices processed: {total_offices}")
    print(f"  Non-consultant roles modified: {total_roles_modified}")
    print(f"  Price fields set to 0: {total_price_fields_modified}")
    
    # Create backup
    backup_path = config_path.with_suffix('.json.backup')
    print(f"\nCreating backup at {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    # Save the modified configuration
    print(f"Saving modified configuration to {config_path}")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("✅ Successfully set all non-consultant role prices to 0!")

if __name__ == "__main__":
    set_non_consultant_prices_to_zero() 