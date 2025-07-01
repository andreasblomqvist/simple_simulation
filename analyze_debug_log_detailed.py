#!/usr/bin/env python3
"""
Detailed analysis of debug simulation log to understand the FTE drop issue.
"""

import re
import os
from collections import defaultdict

def analyze_debug_log_detailed(log_file_path):
    """Detailed analysis of debug log."""
    
    if not os.path.exists(log_file_path):
        print(f"❌ Log file not found: {log_file_path}")
        return
    
    print(f"📖 Analyzing debug log: {log_file_path}")
    print("=" * 80)
    
    # Read the log file
    with open(log_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📊 Total lines in log: {len(lines):,}")
    
    # Extract detailed data
    step_data = defaultdict(lambda: defaultdict(list))
    current_month = None
    current_office = None
    current_step = None
    
    for line in lines:
        line = line.strip()
        
        # Extract month
        month_match = re.search(r'PROCESSING.*?(\d{4})-(\d+)', line)
        if month_match:
            year, month = month_match.groups()
            current_month = f"{year}-{month}"
        
        # Extract office
        office_match = re.search(r'PROCESSING.*?-\s*([A-Za-z]+)\s*-', line)
        if office_match:
            current_office = office_match.group(1)
        
        # Extract step type
        if 'PROCESSING RECRUITMENT' in line:
            current_step = 'recruitment'
        elif 'PROCESSING CHURN' in line:
            current_step = 'churn'
        elif 'PROCESSING PROGRESSION' in line:
            current_step = 'progression'
        
        # Extract FTE data for each step
        fte_match = re.search(r'Starting FTE:\s*(\d+\.?\d*)', line)
        if fte_match and current_month and current_office and current_step:
            step_data[current_month][current_step].append({
                'office': current_office,
                'fte': float(fte_match.group(1))
            })
        
        # Extract FTE after each step
        fte_after_match = re.search(r'FTE after.*?:\s*(\d+\.?\d*)', line)
        if fte_after_match and current_month and current_office and current_step:
            step_data[current_month][f"{current_step}_after"].append({
                'office': current_office,
                'fte': float(fte_after_match.group(1))
            })
    
    print(f"📊 Data extracted for {len(step_data)} months")
    
    # Analyze each month
    for month in sorted(step_data.keys()):
        print(f"\n🔍 MONTH {month} ANALYSIS:")
        print("-" * 50)
        
        month_data = step_data[month]
        
        # Calculate totals for each step
        step_totals = {}
        for step in ['recruitment', 'churn', 'progression']:
            if step in month_data:
                total_fte = sum(d['fte'] for d in month_data[step])
                step_totals[step] = total_fte
                
                after_step = f"{step}_after"
                if after_step in month_data:
                    total_after = sum(d['fte'] for d in month_data[after_step])
                    step_totals[f"{step}_after"] = total_after
        
        # Show step-by-step progression
        print(f"📊 Step-by-step FTE progression:")
        
        if 'recruitment' in step_totals:
            start_fte = step_totals['recruitment']
            print(f"   Start: {start_fte:.1f} FTE")
            
            if 'recruitment_after' in step_totals:
                after_recruitment = step_totals['recruitment_after']
                recruitment_change = after_recruitment - start_fte
                print(f"   After Recruitment: {after_recruitment:.1f} FTE ({recruitment_change:+.1f})")
                
                if 'churn' in step_totals:
                    after_churn = step_totals.get('churn_after', after_recruitment)
                    churn_change = after_churn - after_recruitment
                    print(f"   After Churn: {after_churn:.1f} FTE ({churn_change:+.1f})")
                    
                    if 'progression' in step_totals:
                        after_progression = step_totals.get('progression_after', after_churn)
                        progression_change = after_progression - after_churn
                        print(f"   After Progression: {after_progression:.1f} FTE ({progression_change:+.1f})")
                        
                        total_change = after_progression - start_fte
                        total_change_rate = (total_change / start_fte) * 100 if start_fte > 0 else 0
                        print(f"   Total Change: {total_change:+.1f} FTE ({total_change_rate:+.1f}%)")
        
        # Look for specific issues
        print(f"\n🔍 ISSUE ANALYSIS:")
        
        # Check if recruitment is happening
        if 'recruitment' in step_totals and 'recruitment_after' in step_totals:
            recruitment_change = step_totals['recruitment_after'] - step_totals['recruitment']
            if recruitment_change <= 0:
                print(f"   ⚠️  RECRUITMENT ISSUE: No new hires ({recruitment_change:+.1f})")
            else:
                print(f"   ✅ Recruitment: +{recruitment_change:.1f} FTE")
        
        # Check churn impact
        if 'churn' in step_totals and 'churn_after' in step_totals and 'recruitment_after' in step_totals:
            churn_change = step_totals['churn_after'] - step_totals['recruitment_after']
            churn_rate = (abs(churn_change) / step_totals['recruitment_after']) * 100 if step_totals['recruitment_after'] > 0 else 0
            print(f"   📉 Churn: {churn_change:+.1f} FTE ({churn_rate:.1f}% rate)")
        
        # Check progression impact
        if 'progression' in step_totals and 'progression_after' in step_totals and 'churn_after' in step_totals:
            progression_change = step_totals['progression_after'] - step_totals['churn_after']
            print(f"   📈 Progression: {progression_change:+.1f} FTE")
    
    # Look for patterns across months
    print(f"\n📈 CROSS-MONTH PATTERNS:")
    print("-" * 40)
    
    monthly_changes = []
    for month in sorted(step_data.keys()):
        month_data = step_data[month]
        
        if 'recruitment' in month_data and 'progression_after' in month_data:
            start = sum(d['fte'] for d in month_data['recruitment'])
            end = sum(d['fte'] for d in month_data['progression_after'])
            change = end - start
            change_rate = (change / start) * 100 if start > 0 else 0
            monthly_changes.append((month, start, end, change, change_rate))
    
    if monthly_changes:
        print(f"Monthly FTE changes:")
        for month, start, end, change, rate in monthly_changes:
            print(f"   {month}: {start:.1f} → {end:.1f} ({change:+.1f}, {rate:+.1f}%)")
        
        # Check for consistent patterns
        avg_change_rate = sum(rate for _, _, _, _, rate in monthly_changes) / len(monthly_changes)
        print(f"\n   Average monthly change rate: {avg_change_rate:+.1f}%")
        
        if avg_change_rate < -10:
            print(f"   ⚠️  CONSISTENT DECLINE: Average {abs(avg_change_rate):.1f}% monthly loss")
        elif avg_change_rate > 10:
            print(f"   ⚠️  CONSISTENT GROWTH: Average {avg_change_rate:.1f}% monthly growth")
    
    # Show what steps are missing
    print(f"\n🔍 MISSING DATA ANALYSIS:")
    print("-" * 40)
    
    for month in sorted(step_data.keys()):
        month_data = step_data[month]
        missing_steps = []
        
        for step in ['recruitment', 'churn', 'progression']:
            if step not in month_data:
                missing_steps.append(step)
            elif f"{step}_after" not in month_data:
                missing_steps.append(f"{step}_after")
        
        if missing_steps:
            print(f"   {month}: Missing {', '.join(missing_steps)}")

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
    
    analyze_debug_log_detailed(log_file)

if __name__ == "__main__":
    main() 