#!/usr/bin/env python3
"""
Fix progression rates for AC and AM levels in the office configuration.
The current config has progression_1: 0 for all months, which prevents promotions.
"""

import json
import sys
from pathlib import Path

# Import the progression configuration
sys.path.append('backend/config')
from config.progression_config import CAT_CURVES

def calculate_monthly_progression_rates(level, cat_curves):
    """Calculate monthly progression rates from CAT curves."""
    rates = {}
    
    # Map CAT months to progression months
    # CAT6 = 6 months, CAT12 = 12 months, etc.
    cat_to_months = {
        'CAT0': 0, 'CAT6': 6, 'CAT12': 12, 'CAT18': 18, 'CAT24': 24, 
        'CAT30': 30, 'CAT36': 36, 'CAT42': 42, 'CAT48': 48, 'CAT54': 54, 'CAT60': 60
    }
    
    # Get the CAT curve for this level
    if level not in cat_curves:
        print(f"Warning: No CAT curve found for level {level}")
        return rates
    
    level_curve = cat_curves[level]
    
    # Calculate rates for each month (1-12)
    for month in range(1, 13):
        # Find the appropriate CAT category for this month
        # Use the highest CAT category that applies to this month
        applicable_cat = None
        for cat, cat_months in cat_to_months.items():
            if cat_months <= month:
                applicable_cat = cat
        
        if applicable_cat and applicable_cat in level_curve:
            rates[f"progression_{month}"] = level_curve[applicable_cat]
        else:
            rates[f"progression_{month}"] = 0.0
    
    return rates

def fix_office_configuration():
    """Fix progression rates in the office configuration file."""
    config_path = Path("backend/config/office_configuration.json")
    
    if not config_path.exists():
        print(f"Error: Configuration file not found at {config_path}")
        return
    
    # Load the current configuration
    print("Loading current configuration...")
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Track changes
    changes_made = 0
    
    # Process each office
    for office_name, office_data in config.items():
        print(f"\nProcessing office: {office_name}")
        
        if 'roles' not in office_data:
            continue
            
        for role_name, role_data in office_data['roles'].items():
            if role_name != 'Consultant':  # Only process Consultant role
                continue
                
            for level_name, level_data in role_data.items():
                if level_name in ['AC', 'AM']:  # Only fix AC and AM levels
                    print(f"  Fixing {level_name} level...")
                    
                    # Calculate correct progression rates
                    progression_rates = calculate_monthly_progression_rates(level_name, CAT_CURVES)
                    
                    # Update the progression rates for each month
                    for month in range(1, 13):
                        rate_key = f"progression_{month}"
                        if rate_key in progression_rates:
                            old_rate = level_data.get(rate_key, 0)
                            new_rate = progression_rates[rate_key]
                            
                            if old_rate != new_rate:
                                level_data[rate_key] = new_rate
                                changes_made += 1
                                print(f"    Month {month}: {old_rate} → {new_rate}")
    
    if changes_made == 0:
        print("\nNo changes needed - progression rates are already correct.")
        return
    
    # Save the updated configuration
    print(f"\nSaving configuration with {changes_made} changes...")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Configuration updated successfully!")
    print(f"Fixed progression rates for {changes_made} month/level combinations")

if __name__ == "__main__":
    print("🔧 FIXING PROGRESSION RATES FOR AC AND AM LEVELS")
    print("=" * 50)
    
    # Show the CAT curves for AC and AM
    print("\nCAT Curves for AC and AM levels:")
    print("AC:", CAT_CURVES.get('AC', 'Not found'))
    print("AM:", CAT_CURVES.get('AM', 'Not found'))
    
    fix_office_configuration()
    
    print("\n✅ Done! Run the simulation again to see AC and AM promotions.") 