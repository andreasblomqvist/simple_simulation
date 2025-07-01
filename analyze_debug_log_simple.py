#!/usr/bin/env python3
"""
Simple analysis of debug simulation log to identify growth issues.
"""

import re
import os
from collections import defaultdict

def analyze_debug_log_simple(log_file_path):
    """Simple analysis of debug log."""
    
    if not os.path.exists(log_file_path):
        print(f"❌ Log file not found: {log_file_path}")
        return
    
    print(f"📖 Analyzing debug log: {log_file_path}")
    print("=" * 80)
    
    # Read the log file
    with open(log_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📊 Total lines in log: {len(lines):,}")
    
    # Extract key data
    fte_data = []
    progression_data = []
    month_data = []
    
    current_month = None
    current_office = None
    current_role = None
    current_level = None
    
    for line in lines:
        line = line.strip()
        
        # Extract month
        month_match = re.search(r'PROCESSING.*?(\d{4})-(\d+)', line)
        if month_match:
            year, month = month_match.groups()
            current_month = f"{year}-{month}"
            month_data.append(current_month)
        
        # Extract office
        office_match = re.search(r'PROCESSING.*?-\s*([A-Za-z]+)\s*-', line)
        if office_match:
            current_office = office_match.group(1)
        
        # Extract role
        role_match = re.search(r'--- ROLE:\s*([A-Za-z]+)\s*---', line)
        if role_match:
            current_role = role_match.group(1)
        
        # Extract level
        level_match = re.search(r'LEVEL:\s*([A-Za-z]+)', line)
        if level_match:
            current_level = level_match.group(1)
        
        # Extract starting FTE
        fte_match = re.search(r'Starting FTE:\s*(\d+\.?\d*)', line)
        if fte_match:
            fte_data.append({
                'month': current_month,
                'office': current_office,
                'role': current_role,
                'level': current_level,
                'fte': float(fte_match.group(1))
            })
        
        # Extract FTE after progression
        fte_after_match = re.search(r'FTE after progression:\s*(\d+\.?\d*)', line)
        if fte_after_match:
            fte_data.append({
                'month': current_month,
                'office': current_office,
                'role': current_role,
                'level': current_level,
                'fte_after': float(fte_after_match.group(1))
            })
        
        # Extract progression data
        if 'Eligible for progression:' in line:
            eligible_match = re.search(r'Eligible for progression:\s*(\d+)', line)
            if eligible_match:
                progression_data.append({
                    'month': current_month,
                    'office': current_office,
                    'role': current_role,
                    'level': current_level,
                    'eligible': int(eligible_match.group(1))
                })
        
        if 'Promotions applied:' in line:
            promotions_match = re.search(r'Promotions applied:\s*(\d+)', line)
            if promotions_match:
                progression_data.append({
                    'month': current_month,
                    'office': current_office,
                    'role': current_role,
                    'level': current_level,
                    'promotions': int(promotions_match.group(1))
                })
    
    print(f"📊 FTE data points: {len(fte_data)}")
    print(f"📈 Progression data points: {len(progression_data)}")
    
    # Analyze monthly patterns
    unique_months = sorted(set(month_data))
    print(f"📅 Unique months: {len(unique_months)}")
    if unique_months:
        print(f"Month range: {unique_months[0]} to {unique_months[-1]}")
    
    # Group FTE data by month
    monthly_totals = defaultdict(lambda: {'start': 0, 'after': 0})
    
    for data in fte_data:
        if data['month']:
            if 'fte' in data:
                monthly_totals[data['month']]['start'] += data['fte']
            if 'fte_after' in data:
                monthly_totals[data['month']]['after'] += data['fte_after']
    
    print(f"\n📊 MONTHLY FTE TOTALS:")
    print("-" * 50)
    
    for month in unique_months:
        totals = monthly_totals[month]
        start_fte = totals['start']
        after_fte = totals['after']
        
        if start_fte > 0:
            growth = after_fte - start_fte
            growth_rate = (growth / start_fte) * 100
            print(f"{month}: {start_fte:.1f} → {after_fte:.1f} ({growth:+.1f}, {growth_rate:+.1f}%)")
        else:
            print(f"{month}: {start_fte:.1f} → {after_fte:.1f}")
    
    # Analyze progression patterns
    if progression_data:
        print(f"\n📈 PROGRESSION SUMMARY:")
        print("-" * 30)
        
        level_stats = defaultdict(lambda: {'eligible': 0, 'promotions': 0})
        
        for data in progression_data:
            if data['level']:
                if 'eligible' in data:
                    level_stats[data['level']]['eligible'] += data['eligible']
                if 'promotions' in data:
                    level_stats[data['level']]['promotions'] += data['promotions']
        
        for level, stats in level_stats.items():
            eligible = stats['eligible']
            promotions = stats['promotions']
            if eligible > 0:
                rate = (promotions / eligible) * 100
                print(f"{level}: {promotions}/{eligible} ({rate:.1f}%)")
    
    # Look for anomalies
    print(f"\n🔍 ANOMALY DETECTION:")
    print("-" * 30)
    
    # Check for high growth months
    high_growth_months = []
    for month in unique_months:
        totals = monthly_totals[month]
        if totals['start'] > 0:
            growth_rate = ((totals['after'] - totals['start']) / totals['start']) * 100
            if growth_rate > 5:  # More than 5% growth
                high_growth_months.append((month, growth_rate))
    
    if high_growth_months:
        print(f"⚠️  High growth months (>5%):")
        for month, rate in high_growth_months[-5:]:  # Last 5
            print(f"   {month}: {rate:+.1f}%")
    else:
        print("✅ No high growth months detected")
    
    # Check for negative churn (more people than expected)
    negative_churn_months = []
    for month in unique_months:
        totals = monthly_totals[month]
        if totals['after'] > totals['start'] * 1.1:  # More than 10% increase
            negative_churn_months.append((month, totals['start'], totals['after']))
    
    if negative_churn_months:
        print(f"⚠️  Potential negative churn months (>10% increase):")
        for month, start, after in negative_churn_months[-3:]:  # Last 3
            increase = after - start
            print(f"   {month}: {start:.1f} → {after:.1f} (+{increase:.1f})")

def main():
    """Main function."""
    log_file = "backend/logs/debug_simulation_20250630_153416.log"
    
    if not os.path.exists(log_file):
        print(f"❌ Log file not found: {log_file}")
        print("Available debug logs:")
        for file in os.listdir("backend/logs"):
            if file.startswith("debug_simulation_"):
                print(f"   - {file}")
        return
    
    analyze_debug_log_simple(log_file)

if __name__ == "__main__":
    main() 