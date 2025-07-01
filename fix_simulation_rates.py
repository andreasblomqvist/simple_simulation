#!/usr/bin/env python3
"""
Fix simulation rates based on the debugging report analysis.
Update configuration with correct baseline rates to resolve the 18x scaling error.
"""
import json
from pathlib import Path

# Correct baseline rates from debugging report (monthly, as decimals)
CORRECT_RATES = {
    'Consultant': {
        'A': {
            'recruitment': 0.0127,  # 1.27% monthly
            'churn': 0.0015,        # 0.15% monthly
        },
        'AC': {
            'recruitment': 0.0028,  # 0.28% monthly
            'churn': 0.0014,        # 0.14% monthly
        },
        'AM': {
            'recruitment': 0.0000,  # 0.00% monthly
            'churn': 0.0004,        # 0.04% monthly
        },
        'C': {
            'recruitment': 0.0004,  # 0.04% monthly
            'churn': 0.0008,        # 0.08% monthly
        },
        'M': {
            'recruitment': 0.0000,  # 0.00% monthly
            'churn': 0.0007,        # 0.07% monthly
        },
        'SrC': {
            'recruitment': 0.0001,  # 0.01% monthly
            'churn': 0.0005,        # 0.05% monthly
        },
        'SrM': {
            'recruitment': 0.0000,  # 0.00% monthly
            'churn': 0.0010,        # 0.10% monthly
        },
        'PiP': {
            'recruitment': 0.0000,  # 0.00% monthly
            'churn': 0.0000,        # 0.00% monthly
        }
    },
    'Sales': {
        'A': {
            'recruitment': 0.025,   # 2.5% monthly
            'churn': 0.018,         # 1.8% monthly
        },
        'AC': {
            'recruitment': 0.020,   # 2.0% monthly
            'churn': 0.018,         # 1.8% monthly
        },
        'C': {
            'recruitment': 0.015,   # 1.5% monthly
            'churn': 0.018,         # 1.8% monthly
        },
        'SrC': {
            'recruitment': 0.010,   # 1.0% monthly
            'churn': 0.018,         # 1.8% monthly
        },
        'AM': {
            'recruitment': 0.008,   # 0.8% monthly
            'churn': 0.018,         # 1.8% monthly
        },
        'M': {
            'recruitment': 0.005,   # 0.5% monthly
            'churn': 0.018,         # 1.8% monthly
        },
        'SrM': {
            'recruitment': 0.000,   # 0.0% monthly
            'churn': 0.018,         # 1.8% monthly
        },
        'PiP': {
            'recruitment': 0.000,   # 0.0% monthly
            'churn': 0.018,         # 1.8% monthly
        }
    },
    'Recruitment': {
        'A': {
            'recruitment': 0.020,   # 2.0% monthly
            'churn': 0.016,         # 1.6% monthly
        },
        'AC': {
            'recruitment': 0.018,   # 1.8% monthly
            'churn': 0.016,         # 1.6% monthly
        },
        'C': {
            'recruitment': 0.016,   # 1.6% monthly
            'churn': 0.016,         # 1.6% monthly
        },
        'SrC': {
            'recruitment': 0.014,   # 1.4% monthly
            'churn': 0.016,         # 1.6% monthly
        },
        'AM': {
            'recruitment': 0.012,   # 1.2% monthly
            'churn': 0.016,         # 1.6% monthly
        },
        'M': {
            'recruitment': 0.010,   # 1.0% monthly
            'churn': 0.016,         # 1.6% monthly
        },
        'SrM': {
            'recruitment': 0.008,   # 0.8% monthly
            'churn': 0.016,         # 1.6% monthly
        },
        'PiP': {
            'recruitment': 0.000,   # 0.0% monthly
            'churn': 0.016,         # 1.6% monthly
        }
    },
    'Operations': {
        'recruitment': 0.021,       # 2.1% monthly
        'churn': 0.021,             # 2.1% monthly
    }
}

def fix_configuration():
    """Update the configuration with correct baseline rates."""
    config_path = Path('backend/config/office_configuration.json')
    
    print("🔧 Fixing simulation rates based on debugging report...")
    print("=" * 60)
    
    # Load current configuration
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Track changes
    changes_made = 0
    
    # Update each office
    for office_name, office_data in config.items():
        print(f"📊 Processing office: {office_name}")
        
        roles = office_data.get('roles', {})
        
        for role_name, role_data in roles.items():
            if role_name in CORRECT_RATES:
                print(f"  🔄 Updating role: {role_name}")
                
                if isinstance(role_data, dict) and role_name != 'Operations':
                    # Roles with levels (Consultant, Sales, Recruitment)
                    for level_name, level_data in role_data.items():
                        if level_name in CORRECT_RATES[role_name]:
                            correct_rates = CORRECT_RATES[role_name][level_name]
                            
                            # Update all 12 months
                            for month in range(1, 13):
                                old_recruitment = level_data.get(f'recruitment_{month}', 0)
                                old_churn = level_data.get(f'churn_{month}', 0)
                                
                                level_data[f'recruitment_{month}'] = correct_rates['recruitment']
                                level_data[f'churn_{month}'] = correct_rates['churn']
                                
                                if old_recruitment != correct_rates['recruitment'] or old_churn != correct_rates['churn']:
                                    changes_made += 1
                                    print(f"    ✅ {level_name}: {old_recruitment:.3f}→{correct_rates['recruitment']:.3f} recruitment, {old_churn:.3f}→{correct_rates['churn']:.3f} churn")
                
                elif role_name == 'Operations':
                    # Flat role (Operations)
                    correct_rates = CORRECT_RATES[role_name]
                    
                    # Update all 12 months
                    for month in range(1, 13):
                        old_recruitment = role_data.get(f'recruitment_{month}', 0)
                        old_churn = role_data.get(f'churn_{month}', 0)
                        
                        role_data[f'recruitment_{month}'] = correct_rates['recruitment']
                        role_data[f'churn_{month}'] = correct_rates['churn']
                        
                        if old_recruitment != correct_rates['recruitment'] or old_churn != correct_rates['churn']:
                            changes_made += 1
                            print(f"    ✅ Operations: {old_recruitment:.3f}→{correct_rates['recruitment']:.3f} recruitment, {old_churn:.3f}→{correct_rates['churn']:.3f} churn")
    
    # Save updated configuration
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("=" * 60)
    print(f"✅ Configuration updated! {changes_made} rate changes made.")
    print("📈 Expected results after fix:")
    print("   - Level A: Should grow from 163 to ~318 (95.1% growth)")
    print("   - Level AC: Should grow from 231 to ~251 (8.7% growth)")
    print("   - Level C: Should decline from 356 to ~348 (-2.2% decline)")
    print("   - Overall: Should match Claude AI results within 1-2%")
    print("\n🚀 Ready to test the fixed simulation!")

if __name__ == "__main__":
    fix_configuration() 