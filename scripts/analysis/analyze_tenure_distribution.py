#!/usr/bin/env python3
"""
Analyze tenure distribution for AC and AM levels to understand why no promotions are happening.
"""

import sys
import os
import random
from datetime import datetime
from collections import defaultdict, Counter

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.config_service import config_service
from backend.config.progression_config import PROGRESSION_CONFIG, CAT_CURVES

def analyze_tenure_distribution():
    """Analyze tenure distribution for AC and AM levels"""
    print("🔍 ANALYZING TENURE DISTRIBUTION FOR AC AND AM LEVELS")
    print("=" * 60)
    
    # Set random seed for reproducible results
    random.seed(42)
    
    # Initialize the simulation engine
    engine = SimulationEngine(config_service)
    
    # Get the current configuration
    config = config_service.get_configuration()
    
    # Analyze each office
    for office_name, office_data in config.items():
        if 'roles' not in office_data or 'Consultant' not in office_data['roles']:
            continue
            
        print(f"\n🏢 OFFICE: {office_name}")
        print("-" * 40)
        
        consultant_roles = office_data['roles']['Consultant']
        
        # Analyze AC level
        if 'AC' in consultant_roles:
            ac_data = consultant_roles['AC']
            ac_fte = ac_data.get('fte', 0)
            print(f"📊 AC Level: {ac_fte} FTE")
            
            if ac_fte > 0:
                # Simulate people with various tenure distributions
                tenure_distribution = simulate_tenure_distribution(ac_fte, 'AC')
                analyze_level_eligibility('AC', tenure_distribution, office_name)
        
        # Analyze AM level
        if 'AM' in consultant_roles:
            am_data = consultant_roles['AM']
            am_fte = am_data.get('fte', 0)
            print(f"📊 AM Level: {am_fte} FTE")
            
            if am_fte > 0:
                # Simulate people with various tenure distributions
                tenure_distribution = simulate_tenure_distribution(am_fte, 'AM')
                analyze_level_eligibility('AM', tenure_distribution, office_name)

def simulate_tenure_distribution(fte, level_name):
    """Simulate realistic tenure distribution for a level"""
    # Create a realistic distribution of tenure months
    # For AC: most people should be 6-18 months, some 18-30 months
    # For AM: most people should be 18-60 months, some 60+ months
    
    if level_name == 'AC':
        # AC level: mix of people with 6-30 months tenure
        tenure_ranges = [
            (6, 12, 0.4),    # 40% with 6-12 months
            (12, 18, 0.3),   # 30% with 12-18 months
            (18, 24, 0.2),   # 20% with 18-24 months
            (24, 30, 0.1),   # 10% with 24-30 months
        ]
    elif level_name == 'AM':
        # AM level: mix of people with 18-60+ months tenure
        tenure_ranges = [
            (18, 24, 0.2),   # 20% with 18-24 months
            (24, 30, 0.3),   # 30% with 24-30 months
            (30, 36, 0.2),   # 20% with 30-36 months
            (36, 42, 0.15),  # 15% with 36-42 months
            (42, 48, 0.1),   # 10% with 42-48 months
            (48, 60, 0.05),  # 5% with 48-60 months
        ]
    else:
        return []
    
    distribution = []
    for start_months, end_months, percentage in tenure_ranges:
        count = int(fte * percentage)
        for i in range(count):
            tenure = random.randint(start_months, end_months - 1)
            distribution.append(tenure)
    
    # Fill any remaining slots
    while len(distribution) < fte:
        if level_name == 'AC':
            tenure = random.randint(6, 30)
        else:  # AM
            tenure = random.randint(18, 60)
        distribution.append(tenure)
    
    return distribution[:fte]  # Ensure exact FTE count

def analyze_level_eligibility(level_name, tenure_distribution, office_name):
    """Analyze eligibility for progression based on tenure distribution"""
    if level_name not in PROGRESSION_CONFIG:
        print(f"  ❌ No progression config found for {level_name}")
        return
    
    config = PROGRESSION_CONFIG[level_name]
    min_tenure = config['time_on_level']
    progression_months = config['progression_months']
    next_level = config['next_level']
    
    print(f"  📋 Progression Requirements:")
    print(f"     Minimum tenure: {min_tenure} months")
    print(f"     Progression months: {progression_months}")
    print(f"     Next level: {next_level}")
    
    # Analyze tenure distribution
    tenure_counter = Counter(tenure_distribution)
    print(f"  📊 Tenure Distribution:")
    
    eligible_count = 0
    total_count = len(tenure_distribution)
    
    for tenure_months in sorted(tenure_counter.keys()):
        count = tenure_counter[tenure_months]
        is_eligible = tenure_months >= min_tenure
        status = "✅" if is_eligible else "❌"
        
        if is_eligible:
            eligible_count += count
        
        # Calculate CAT category
        if tenure_months < 6:
            cat = 'CAT0'
        else:
            cat_number = min(60, 6 * ((tenure_months // 6)))
            cat = f'CAT{cat_number}'
        
        # Get progression probability
        if level_name in CAT_CURVES and cat in CAT_CURVES[level_name]:
            prob = CAT_CURVES[level_name][cat]
        else:
            prob = 0.0
        
        print(f"     {tenure_months:2d} months: {count:3d} people {status} (CAT: {cat}, Prob: {prob:.3f})")
    
    print(f"  📈 Eligibility Summary:")
    print(f"     Total people: {total_count}")
    print(f"     Eligible for progression: {eligible_count} ({eligible_count/total_count*100:.1f}%)")
    
    if eligible_count == 0:
        print(f"  ❌ NO PEOPLE ELIGIBLE FOR PROGRESSION!")
        print(f"     All people have less than {min_tenure} months tenure")
    else:
        print(f"  ✅ {eligible_count} people are eligible for progression")
        
        # Check if any are in progression months
        print(f"  📅 Progression Month Analysis:")
        for month in progression_months:
            month_name = get_month_name(month)
            print(f"     {month_name} (month {month}): Progression allowed")

def get_month_name(month_num):
    """Get month name from number"""
    months = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }
    return months.get(month_num, f'Month {month_num}')

def check_cat_curves():
    """Check CAT curves for AC and AM levels"""
    print("\n📊 CAT CURVE ANALYSIS")
    print("=" * 40)
    
    for level in ['AC', 'AM']:
        if level in CAT_CURVES:
            print(f"\n{level} Level CAT Curve:")
            curve = CAT_CURVES[level]
            for cat, prob in sorted(curve.items()):
                print(f"  {cat}: {prob:.3f} ({prob*100:.1f}%)")
        else:
            print(f"\n{level} Level: No CAT curve found!")

if __name__ == "__main__":
    print("🔍 TENURE DISTRIBUTION ANALYSIS")
    print("=" * 60)
    
    check_cat_curves()
    analyze_tenure_distribution()
    
    print("\n✅ Analysis complete!")
    print("\nKey findings:")
    print("- AC level requires 9 months minimum tenure")
    print("- AM level requires 48 months minimum tenure")
    print("- Progression only occurs in specific months")
    print("- CAT curves determine progression probabilities") 