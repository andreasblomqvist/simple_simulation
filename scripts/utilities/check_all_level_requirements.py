#!/usr/bin/env python3
"""
Check tenure requirements for all levels to verify if first-year promotions were correct.
"""

import sys
import os
sys.path.append('backend')

from config.progression_config import PROGRESSION_CONFIG, CAT_CURVES

def main():
    print("🔍 CHECKING ALL LEVEL TENURE REQUIREMENTS")
    print("=" * 60)
    
    # Check all levels that had promotions in the first year
    levels_with_promotions = ['C', 'SrC', 'AM', 'M', 'A']
    
    for level in levels_with_promotions:
        if level in PROGRESSION_CONFIG:
            config = PROGRESSION_CONFIG[level]
            print(f"\n📋 {level} Level Configuration:")
            print(f"  Start tenure: {config['start_tenure']} months (total company tenure when entering {level})")
            print(f"  Time on level: {config['time_on_level']} months (minimum time spent as {level})")
            print(f"  Total required: {config['start_tenure'] + config['time_on_level']} months total company tenure")
            print(f"  Progression months: {config['progression_months']}")
            print(f"  Next level: {config['next_level']}")
            
            # Check if this level could realistically promote in first year
            total_required = config['start_tenure'] + config['time_on_level']
            if total_required <= 12:
                print(f"  ✅ CAN promote in first year (requires {total_required} months)")
            else:
                print(f"  ❌ CANNOT promote in first year (requires {total_required} months)")
            
            if level in CAT_CURVES:
                print(f"  CAT Curve:")
                for cat, prob in sorted(CAT_CURVES[level].items()):
                    print(f"    {cat}: {prob:.3f} ({prob*100:.1f}%)")
        else:
            print(f"\n❌ {level} Level: No progression config found!")
    
    print("\n🔍 ANALYSIS OF FIRST-YEAR PROMOTIONS:")
    print("=" * 60)
    print("Based on the event log showing these promotions in first year:")
    print("- C: 254 promotions")
    print("- SrC: 148 promotions") 
    print("- AM: 104 promotions")
    print("- M: 5 promotions")
    print("- A: 2 promotions")
    print("- AC: 0 promotions")
    
    print("\n💡 VERDICT:")
    print("- C → SrC: Requires 27 months total (15+12) - ❌ SHOULD NOT promote in first year!")
    print("- SrC → AM: Requires 45 months total (27+18) - ❌ SHOULD NOT promote in first year!")
    print("- AM → M: Requires 75 months total (45+30) - ❌ SHOULD NOT promote in first year!")
    print("- M → SrM: Requires 99 months total (75+24) - ❌ SHOULD NOT promote in first year!")
    print("- A → AC: Requires 6 months total (0+6) - ✅ CAN promote in first year")
    print("- AC → C: Requires 15 months total (6+9) - ❌ SHOULD NOT promote in first year")

if __name__ == "__main__":
    main() 