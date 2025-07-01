#!/usr/bin/env python3
"""
Script to get recruitment and churn rates for each level in the current configuration
"""

import json
import os
from collections import defaultdict

def get_recruitment_churn_totals():
    """Get recruitment and churn rates for each level across all offices"""
    
    # Load the configuration
    config_path = "backend/config/office_configuration.json"
    
    if not os.path.exists(config_path):
        print(f"❌ Configuration file not found: {config_path}")
        return
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return
    
    # Initialize totals
    level_recruitment = defaultdict(float)
    level_churn = defaultdict(float)
    level_fte = defaultdict(float)
    
    print("📊 Recruitment and Churn Rates by Level (Current Configuration)")
    print("=" * 80)
    
    # Process each office
    for office_name, office_data in config.items():
        print(f"\n🏢 {office_name} ({office_data.get('journey', 'N/A')})")
        
        # Process roles
        for role_name, role_data in office_data.get('roles', {}).items():
            if isinstance(role_data, dict):
                # Role has levels (e.g., Consultant -> A, AC, C, etc.)
                print(f"   📋 {role_name}:")
                for level_name, level_data in role_data.items():
                    if isinstance(level_data, dict):
                        fte = level_data.get('fte', 0)
                        
                        # Get recruitment and churn from month 1 (current rates)
                        recruitment = level_data.get('recruitment_1', 0)
                        churn = level_data.get('churn_1', 0)
                        
                        if fte > 0:  # Only show levels with actual FTE
                            level_fte[level_name] += fte
                            level_recruitment[level_name] += recruitment
                            level_churn[level_name] += churn
                            
                            print(f"      {level_name}: {fte:.1f} FTE, {recruitment:.3f} recruitment, {churn:.3f} churn")
            else:
                # Role is a single level (e.g., Operations)
                if isinstance(role_data, dict):
                    fte = role_data.get('fte', 0)
                    recruitment = role_data.get('recruitment_1', 0)
                    churn = role_data.get('churn_1', 0)
                    
                    if fte > 0:  # Only show roles with actual FTE
                        level_fte[role_name] += fte
                        level_recruitment[role_name] += recruitment
                        level_churn[role_name] += churn
                        
                        print(f"   📋 {role_name}: {fte:.1f} FTE, {recruitment:.3f} recruitment, {churn:.3f} churn")
    
    # Display summary table
    print("\n" + "=" * 80)
    print("📈 SUMMARY TABLE - Recruitment and Churn by Level")
    print("=" * 80)
    
    # Define valid level names (exclude configuration metadata)
    valid_levels = {'A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM', 'fte'}
    
    # Print table header
    print(f"{'Level':<8} {'FTE':<8} {'Recruitment':<12} {'Churn':<12} {'Net Growth':<12} {'Growth %':<10}")
    print("-" * 80)
    
    total_fte = 0
    total_recruitment = 0
    total_churn = 0
    
    for level in sorted(valid_levels):
        if level in level_fte and level_fte[level] > 0:
            fte = level_fte[level]
            recruitment = level_recruitment[level]
            churn = level_churn[level]
            net_growth = recruitment - churn
            growth_pct = (net_growth / fte * 100) if fte > 0 else 0
            
            print(f"{level:<8} {fte:<8.1f} {recruitment:<12.3f} {churn:<12.3f} {net_growth:<12.3f} {growth_pct:<10.2f}%")
            
            total_fte += fte
            total_recruitment += recruitment
            total_churn += churn
    
    # Print totals
    print("-" * 80)
    total_net_growth = total_recruitment - total_churn
    total_growth_pct = (total_net_growth / total_fte * 100) if total_fte > 0 else 0
    
    print(f"{'TOTAL':<8} {total_fte:<8.1f} {total_recruitment:<12.3f} {total_churn:<12.3f} {total_net_growth:<12.3f} {total_growth_pct:<10.2f}%")
    
    # Additional insights
    print("\n" + "=" * 80)
    print("📊 INSIGHTS")
    print("=" * 80)
    
    print(f"💼 Total FTE: {total_fte:.1f}")
    print(f"📈 Total Monthly Recruitment: {total_recruitment:.3f}")
    print(f"📉 Total Monthly Churn: {total_churn:.3f}")
    print(f"🔄 Net Monthly Growth: {total_net_growth:.3f}")
    print(f"📊 Overall Growth Rate: {total_growth_pct:.2f}% per month")
    print(f"📊 Annual Growth Rate: {total_growth_pct * 12:.2f}% per year")
    
    # Growth by level type
    print(f"\n🎯 Growth by Level Type:")
    junior_levels = ['A', 'AC']
    mid_levels = ['C', 'SrC', 'AM']
    senior_levels = ['M', 'SrM', 'PiP']
    
    for level_group, levels in [("Junior", junior_levels), ("Mid", mid_levels), ("Senior", senior_levels)]:
        group_fte = sum(level_fte.get(level, 0) for level in levels)
        group_recruitment = sum(level_recruitment.get(level, 0) for level in levels)
        group_churn = sum(level_churn.get(level, 0) for level in levels)
        group_net = group_recruitment - group_churn
        group_pct = (group_net / group_fte * 100) if group_fte > 0 else 0
        
        print(f"   {level_group}: {group_fte:.1f} FTE, {group_net:.3f} net growth ({group_pct:.2f}% monthly)")
    
    return {
        'level_fte': dict(level_fte),
        'level_recruitment': dict(level_recruitment),
        'level_churn': dict(level_churn),
        'total_fte': total_fte,
        'total_recruitment': total_recruitment,
        'total_churn': total_churn
    }

if __name__ == "__main__":
    get_recruitment_churn_totals() 