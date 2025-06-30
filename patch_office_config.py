#!/usr/bin/env python3
"""
Patch office_configuration.json to update Consultant recruitment and churn rates and remove the flat fields.
Also set all rates and UTR to 0 for non-Consultant roles and fix Operations structure.
"""

import sys
import json
from pathlib import Path

# Recruitment and churn rates mapping
RECRUITMENT_MAP = {
    "A": 0.0505,
    "AC": 0.0198,
    "C": 0.0097,
    "SrC": 0.0025,
    "AM": 0.0008,
    "M": 0.0,
    "SrM": 0.0,
    "PiP": 0.0,
    "P": 0.0
}
CHURN_MAP = {
    "A": 0.0073,
    "AC": 0.0125,
    "C": 0.0219,
    "SrC": 0.0201,
    "AM": 0.0164,
    "M": 0.0039,
    "SrM": 0.0013,
    "PiP": 0.0,
    "P": 0.0
}

CONFIG_PATH = Path("backend/config/office_configuration.json")
BACKUP_PATH = Path("backend/config/office_configuration.json.bak")

def patch_office_config():
    # Backup original
    if not BACKUP_PATH.exists():
        BACKUP_PATH.write_bytes(CONFIG_PATH.read_bytes())
    
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    
    changes_made = 0
    
    for office_name, office_data in data.items():
        if 'roles' not in office_data:
            continue
            
        for role_name, role_data in office_data['roles'].items():
            if role_name == 'Consultant':
                # Update Consultant levels
                for level_name, level_data in role_data.items():
                    if isinstance(level_data, dict):
                        # Set monthly recruitment rates
                        for month in range(1, 13):
                            level_data[f'recruitment_{month}'] = RECRUITMENT_MAP.get(level_name, 0.0)
                            level_data[f'churn_{month}'] = CHURN_MAP.get(level_name, 0.0)
                        
                        # Remove flat fields
                        level_data.pop('recruitment', None)
                        level_data.pop('churn', None)
                        changes_made += 1
                        
            elif role_name in ['Sales', 'Recruitment']:
                # Set all rates to 0 for Sales and Recruitment
                if isinstance(role_data, dict):
                    for level_name, level_data in role_data.items():
                        if isinstance(level_data, dict):
                            for month in range(1, 13):
                                level_data[f'recruitment_{month}'] = 0.0
                                level_data[f'churn_{month}'] = 0.0
                                level_data[f'progression_{month}'] = 0.0
                                level_data[f'utr_{month}'] = 0.0
                            
                            # Remove flat fields
                            level_data.pop('recruitment', None)
                            level_data.pop('churn', None)
                            level_data.pop('progression', None)
                            level_data.pop('utr', None)
                            changes_made += 1
                            
            elif role_name == 'Operations':
                # Fix Operations structure - remove 'nan' key and set rates to 0
                if isinstance(role_data, dict):
                    # Remove the 'nan' key if it exists
                    if 'nan' in role_data:
                        del role_data['nan']
                    
                    # Set all monthly rates to 0
                    for month in range(1, 13):
                        role_data[f'recruitment_{month}'] = 0.0
                        role_data[f'churn_{month}'] = 0.0
                        role_data[f'progression_{month}'] = 0.0
                        role_data[f'utr_{month}'] = 0.0
                    
                    # Remove flat fields
                    role_data.pop('recruitment', None)
                    role_data.pop('churn', None)
                    role_data.pop('progression', None)
                    role_data.pop('utr', None)
                    changes_made += 1
    
    # Save updated config
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Updated {changes_made} role configurations")
    print(f"✅ Backup saved to {BACKUP_PATH}")
    print("✅ Operations roles fixed (removed 'nan' structure, set rates to 0)")
    print("✅ All non-Consultant roles now have 0 recruitment/churn rates")

if __name__ == "__main__":
    patch_office_config() 