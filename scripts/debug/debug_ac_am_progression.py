#!/usr/bin/env python3
"""
Debug script to understand why AC and AM levels have no promotions.
"""

import sys
import os
sys.path.append('backend')

from config.progression_config import PROGRESSION_CONFIG, CAT_CURVES

def main():
    print("🔍 DEBUGGING AC AND AM PROGRESSION")
    print("=" * 50)
    
    # Check AC level configuration
    print("\n📋 AC Level Configuration:")
    if 'AC' in PROGRESSION_CONFIG:
        ac_config = PROGRESSION_CONFIG['AC']
        print(f"  Start tenure: {ac_config['start_tenure']} months (total company tenure when entering AC)")
        print(f"  Time on level: {ac_config['time_on_level']} months (minimum time spent as AC)")
        print(f"  Total required: {ac_config['start_tenure'] + ac_config['time_on_level']} months total company tenure")
        print(f"  Progression months: {ac_config['progression_months']}")
        print(f"  Next level: {ac_config['next_level']}")
        
        if 'AC' in CAT_CURVES:
            print(f"  CAT Curve:")
            for cat, prob in sorted(CAT_CURVES['AC'].items()):
                print(f"    {cat}: {prob:.3f} ({prob*100:.1f}%)")
        else:
            print(f"  ❌ No CAT curve found!")
    else:
        print(f"  ❌ No progression config found!")
    
    # Check AM level configuration
    print("\n📋 AM Level Configuration:")
    if 'AM' in PROGRESSION_CONFIG:
        am_config = PROGRESSION_CONFIG['AM']
        print(f"  Start tenure: {am_config['start_tenure']} months (total company tenure when entering AM)")
        print(f"  Time on level: {am_config['time_on_level']} months (minimum time spent as AM)")
        print(f"  Total required: {am_config['start_tenure'] + am_config['time_on_level']} months total company tenure")
        print(f"  Progression months: {am_config['progression_months']}")
        print(f"  Next level: {am_config['next_level']}")
        
        if 'AM' in CAT_CURVES:
            print(f"  CAT Curve:")
            for cat, prob in sorted(CAT_CURVES['AM'].items()):
                print(f"    {cat}: {prob:.3f} ({prob*100:.1f}%)")
        else:
            print(f"  ❌ No CAT curve found!")
    else:
        print(f"  ❌ No progression config found!")
    
    print("\n🔍 UPDATED TENURE REQUIREMENTS:")
    print("- AC → C: Requires 15 months total company tenure (6+9)")
    print("- AM → M: Requires 75 months total company tenure (45+30)")
    print("- AC progression months: [1, 4, 7, 10]")
    print("- AM progression months: [1, 7] (only Jan & Jul)")
    
    print("\n💡 IMPACT OF CHANGES:")
    print("- AM level tenure reduced from 48 to 30 months at level")
    print("- AM total requirement reduced from 99 to 75 months")
    print("- This should make AM promotions much more likely!")
    
    print("\n📊 CAREER PROGRESSION PATH:")
    print("A (0-6mo) → AC (6-15mo) → C (15-27mo) → SrC (27-45mo) → AM (45-75mo) → M (75-99mo)")

if __name__ == "__main__":
    main() 