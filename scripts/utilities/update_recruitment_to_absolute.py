#!/usr/bin/env python3
"""
Script to update recruitment rates from tiny percentages to absolute values.
This will make the simulation actually hire people instead of getting 0 new hires.
"""

import json
import os
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

def update_recruitment_to_absolute():
    """Update recruitment rates to use absolute values instead of tiny percentages."""
    
    # Load the current configuration
    config_path = backend_dir / "config" / "office_configuration.json"
    
    if not config_path.exists():
        print(f"Configuration file not found: {config_path}")
        return
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("Updating recruitment rates to absolute values...")
    
    # Define absolute recruitment targets per month
    # These are reasonable monthly hiring targets
    absolute_recruitment_targets = {
        "Consultant": {
            "A": 20,      # 20 A-level consultants per month
            "AC": 15,     # 15 AC-level consultants per month  
            "AM": 10,     # 10 AM-level consultants per month
            "M": 5,       # 5 M-level consultants per month
            "SM": 3,      # 3 SM-level consultants per month
            "PiP": 1      # 1 PiP-level consultant per month
        },
        "Sales": {
            "A": 8,       # 8 A-level sales per month
            "AC": 6,      # 6 AC-level sales per month
            "AM": 4,      # 4 AM-level sales per month
            "M": 2,       # 2 M-level sales per month
            "SM": 1,      # 1 SM-level sales per month
            "PiP": 1      # 1 PiP-level sales per month
        },
        "Recruitment": {
            "A": 5,       # 5 A-level recruiters per month
            "AC": 3,      # 3 AC-level recruiters per month
            "AM": 2,      # 2 AM-level recruiters per month
            "M": 1,       # 1 M-level recruiter per month
            "SM": 1,      # 1 SM-level recruiter per month
            "PiP": 0      # 0 PiP-level recruiters per month
        },
        "Operations": {
            "Operations": 3  # 3 operations staff per month
        }
    }
    
    total_updates = 0
    
    # Update each office
    for office_name, office_data in config.items():
        if "roles" not in office_data:
            continue
            
        for role_name, role_data in office_data["roles"].items():
            if role_name not in absolute_recruitment_targets:
                continue
                
            for level_name, level_data in role_data.items():
                if level_name not in absolute_recruitment_targets[role_name]:
                    continue
                    
                target_recruitment = absolute_recruitment_targets[role_name][level_name]
                
                # Update all 12 months
                for month in range(1, 13):
                    # Add absolute recruitment values
                    level_data[f"recruitment_abs_{month}"] = target_recruitment
                    
                    # Keep the percentage values as backup but set them to 0
                    # since we're using absolute values
                    level_data[f"recruitment_{month}"] = 0.0
                    
                    total_updates += 1
                
                print(f"  {office_name} - {role_name}.{level_name}: {target_recruitment} per month")
    
    # Save the updated configuration
    backup_path = config_path.with_suffix('.json.backup_absolute_recruitment')
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Updated {total_updates} recruitment entries to use absolute values")
    print(f"📁 Backup saved to: {backup_path}")
    print(f"📁 Updated configuration: {config_path}")
    print("\nThe simulation will now hire actual people instead of getting 0 new hires!")

if __name__ == "__main__":
    update_recruitment_to_absolute() 