#!/usr/bin/env python3
"""
Fix Operations structure in office_configuration.json
"""

import sys
import json
from pathlib import Path

CONFIG_PATH = Path("backend/config/office_configuration.json")
BACKUP_PATH = Path("backend/config/office_configuration.json.bak")

def fix_operations():
    # Backup original
    if not BACKUP_PATH.exists():
        BACKUP_PATH.write_bytes(CONFIG_PATH.read_bytes())
    
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    
    changes_made = 0
    
    for office_name, office_data in data.items():
        if 'roles' not in office_data:
            continue
            
        if 'Operations' in office_data['roles']:
            ops = office_data['roles']['Operations']
            
            # Remove the 'nan' key if it exists
            if 'nan' in ops:
                del ops['nan']
                print(f"✅ Removed 'nan' key from {office_name} Operations")
                changes_made += 1
            
            # Set all monthly rates to 0
            for month in range(1, 13):
                ops[f'recruitment_{month}'] = 0.0
                ops[f'churn_{month}'] = 0.0
                ops[f'progression_{month}'] = 0.0
                ops[f'utr_{month}'] = 0.0
            
            # Remove flat fields
            for field in ['recruitment', 'churn', 'progression', 'utr']:
                if field in ops:
                    del ops[field]
            
            print(f"✅ Fixed {office_name} Operations rates")
            changes_made += 1
    
    # Save updated config
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Fixed {changes_made} Operations configurations")
    print(f"✅ Backup saved to {BACKUP_PATH}")

if __name__ == "__main__":
    fix_operations() 