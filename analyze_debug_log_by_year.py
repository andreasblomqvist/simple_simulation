#!/usr/bin/env python3
"""
Analyze debug simulation log by year to identify growth issues.
"""

import re
import os
from collections import defaultdict
from datetime import datetime

def analyze_debug_log_by_year(log_file_path):
    """Split and analyze debug log by year."""
    
    if not os.path.exists(log_file_path):
        print(f"❌ Log file not found: {log_file_path}")
        return
    
    print(f"📖 Analyzing debug log: {log_file_path}")
    print("=" * 80)
    
    # Read the log file
    with open(log_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📊 Total lines in log: {len(lines):,}")
    
    # Split by year
    year_data = defaultdict(list)
    current_year = None
    
    for line in lines:
        # Look for year patterns in the log (timestamp format: 2025-06-30 15:34:16,546)
        year_match = re.search(r'(\d{4})-\d{2}-\d{2}', line)
        if year_match:
            year = year_match.group(1)
            if year.startswith('20'):  # Valid year
                current_year = year
        if current_year:
            year_data[current_year].append(line)
    
    print(f"📅 Found data for years: {sorted(year_data.keys())}")
    print()
    
    # Analyze each year
    for year in sorted(year_data.keys()):
        print(f"🔍 ANALYZING YEAR {year}")
        print("-" * 50)
        
        year_lines = year_data[year]
        print(f"📝 Lines for {year}: {len(year_lines):,}")
        
        # Extract key metrics for this year
        analyze_year_data(year, year_lines)
        print()

def analyze_year_data(year, lines):
    """Analyze data for a specific year."""
    
    # Extract different types of data
    progression_data = []
    recruitment_data = []
    churn_data = []
    fte_data = []
    month_data = []
    
    current_month = None
    current_office = None
    current_role = None
    current_level = None
    
    for line in lines:
        line = line.strip()
        
        # Extract month information
        month_match = re.search(r'PROCESSING.*?(\d{4})-(\d+)', line)
        if month_match:
            year_num, month_num = month_match.groups()
            current_month = f"{year_num}-{month_num}"
            month_data.append(current_month)
        
        # Extract office information
        office_match = re.search(r'PROCESSING.*?-\s*([A-Za-z]+)\s*-', line)
        if office_match:
            current_office = office_match.group(1)
        
        # Extract role information
        role_match = re.search(r'--- ROLE:\s*([A-Za-z]+)\s*---', line)
        if role_match:
            current_role = role_match.group(1)
        
        # Extract level information
        level_match = re.search(r'LEVEL:\s*([A-Za-z]+)', line)
        if level_match:
            current_level = level_match.group(1)
        
        # Extract FTE data
        fte_match = re.search(r'Starting FTE:\s*(\d+\.?\d*)', line)
        if fte_match:
            fte_data.append({
                'month': current_month,
                'office': current_office,
                'role': current_role,
                'level': current_level,
                'fte': float(fte_match.group(1))
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
    
    print(f"📊 FTE data points: {len(fte_data)}")
    print(f"📈 Progression data points: {len(progression_data)}")
    print(f"📅 Unique months: {len(set(month_data))}")
    
    # Analyze monthly patterns
    if month_data:
        unique_months = sorted(set(month_data))
        print(f"\n📅 MONTHLY ANALYSIS:")
        print(f"Months processed: {len(unique_months)}")
        print(f"Month range: {unique_months[0]} to {unique_months[-1]}")
        
        # Group FTE data by month
        monthly_fte = defaultdict(list)
        for data in fte_data:
            if data['month']:
                monthly_fte[data['month']].append(data)
        
        print(f"\n📊 FTE BY MONTH:")
        for month in unique_months[-5:]:  # Last 5 months
            month_entries = monthly_fte[month]
            if month_entries:
                total_fte = sum(entry.get('fte', 0) for entry in month_entries)
                total_fte_after = sum(entry.get('fte_after', 0) for entry in month_entries)
                print(f"   {month}: Start={total_fte:.1f}, After={total_fte_after:.1f}")
    
    # Analyze progression patterns
    if progression_data:
        print(f"\n📈 PROGRESSION ANALYSIS:")
        
        # Group by level
        level_progression = defaultdict(list)
        for data in progression_data:
            if data['level']:
                level_progression[data['level']].append(data)
        
        print(f"Levels with progression data: {len(level_progression)}")
        for level, data_list in level_progression.items():
            total_eligible = sum(d.get('eligible', 0) for d in data_list)
            total_promotions = sum(d.get('promotions', 0) for d in data_list)
            if total_eligible > 0:
                promotion_rate = (total_promotions / total_eligible) * 100
                print(f"   {level}: {total_promotions}/{total_eligible} ({promotion_rate:.1f}%)")
    
    # Look for growth patterns
    if fte_data:
        print(f"\n📈 GROWTH ANALYSIS:")
        
        # Group by office and month
        office_monthly = defaultdict(lambda: defaultdict(list))
        for data in fte_data:
            if data['office'] and data['month']:
                office_monthly[data['office']][data['month']].append(data)
        
        print(f"Offices tracked: {len(office_monthly)}")
        
        # Calculate growth for each office
        for office, months in list(office_monthly.items())[:3]:  # Top 3 offices
            sorted_months = sorted(months.keys())
            if len(sorted_months) >= 2:
                first_month = sorted_months[0]
                last_month = sorted_months[-1]
                
                first_fte = sum(d.get('fte', 0) for d in months[first_month])
                last_fte = sum(d.get('fte_after', 0) for d in months[last_month])
                
                if first_fte > 0:
                    growth_rate = ((last_fte - first_fte) / first_fte) * 100
                    print(f"   {office}: {first_fte:.1f} → {last_fte:.1f} ({growth_rate:+.1f}%)")

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
    
    analyze_debug_log_by_year(log_file)

if __name__ == "__main__":
    main() 