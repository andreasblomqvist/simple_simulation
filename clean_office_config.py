#!/usr/bin/env python3
"""
Clean office configuration by removing absolute recruitment and churn values.
These should only come from the frontend baseline scenario configuration.
"""
import json

def clean_office_configuration():
    """Remove all recruitment_abs_* and churn_abs_* values from office configuration."""
    
    config_path = "/Users/andreasblomqvist/Code/simple-simulation/simple_simulation/backend/config/office_configuration.json"
    backup_path = "/Users/andreasblomqvist/Code/simple-simulation/simple_simulation/backend/config/office_configuration.json.backup"
    
    print("🧹 CLEANING OFFICE CONFIGURATION")
    print("=" * 60)
    
    # Load current configuration
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Create backup
    with open(backup_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"📁 Backup created: {backup_path}")
    
    total_removed = 0
    offices_processed = 0
    
    # Process each office
    for office_name, office_data in config.items():
        offices_processed += 1
        office_removed = 0
        
        if 'roles' in office_data:
            for role_name, role_data in office_data['roles'].items():
                for level_name, level_data in role_data.items():
                    
                    # Track what we're removing
                    removed_keys = []
                    
                    # Remove all recruitment_abs_* keys
                    keys_to_remove = [key for key in level_data.keys() if key.startswith('recruitment_abs_')]
                    for key in keys_to_remove:
                        del level_data[key]
                        removed_keys.append(key)
                    
                    # Remove all churn_abs_* keys  
                    keys_to_remove = [key for key in level_data.keys() if key.startswith('churn_abs_')]
                    for key in keys_to_remove:
                        del level_data[key]
                        removed_keys.append(key)
                    
                    office_removed += len(removed_keys)
                    total_removed += len(removed_keys)
        
        if office_removed > 0:
            print(f"🏢 {office_name}: Removed {office_removed} recruitment/churn overrides")
    
    # Write cleaned configuration
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("=" * 60)
    print(f"✅ CLEANING COMPLETE")
    print(f"📊 Offices processed: {offices_processed}")
    print(f"🗑️ Total keys removed: {total_removed}")
    print(f"📁 Configuration updated: {config_path}")
    print(f"💡 Now only frontend baseline values will control recruitment/churn")

def verify_cleaning():
    """Verify that no recruitment_abs_ or churn_abs_ values remain."""
    
    config_path = "/Users/andreasblomqvist/Code/simple-simulation/simple_simulation/backend/config/office_configuration.json"
    
    with open(config_path, 'r') as f:
        config_text = f.read()
    
    recruitment_abs_count = config_text.count('recruitment_abs_')
    churn_abs_count = config_text.count('churn_abs_')
    
    print("\n🔍 VERIFICATION")
    print("-" * 30)
    print(f"recruitment_abs_ found: {recruitment_abs_count}")
    print(f"churn_abs_ found: {churn_abs_count}")
    
    if recruitment_abs_count == 0 and churn_abs_count == 0:
        print("✅ Configuration is clean - no absolute overrides remain")
        return True
    else:
        print("❌ Configuration still contains absolute overrides")
        return False

def main():
    """Clean the office configuration and verify results."""
    clean_office_configuration()
    verify_cleaning()

if __name__ == "__main__":
    main()