#!/usr/bin/env python3
"""
Analysis script to examine growth patterns in simulation data
"""

import pandas as pd
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
from datetime import datetime

def analyze_growth_patterns(log_file):
    """Analyze growth patterns in the simulation log"""
    
    print(f"Analyzing growth patterns in: {log_file}")
    print("=" * 60)
    
    # Read the CSV file
    df = pd.read_csv(log_file)
    
    # Convert date to datetime for easier analysis
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m')
    
    # Extract year and month
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    
    print(f"Simulation period: {df['date'].min()} to {df['date'].max()}")
    print(f"Total events: {len(df)}")
    
    # Analyze by event type
    event_counts = df['event_type'].value_counts()
    print(f"\nEvent type distribution:")
    for event_type, count in event_counts.items():
        print(f"  {event_type}: {count}")
    
    # Analyze recruitment patterns
    recruitment_df = df[df['event_type'] == 'recruitment']
    print(f"\nRecruitment Analysis:")
    print(f"  Total recruitments: {len(recruitment_df)}")
    
    # Recruitment by level
    level_recruitment = recruitment_df['level'].value_counts()
    print(f"  Recruitment by level:")
    for level, count in level_recruitment.items():
        print(f"    {level}: {count}")
    
    # Recruitment by office
    office_recruitment = recruitment_df['office'].value_counts()
    print(f"  Recruitment by office:")
    for office, count in office_recruitment.head(10).items():
        print(f"    {office}: {count}")
    
    # Monthly recruitment trends
    monthly_recruitment = recruitment_df.groupby(['year', 'month']).size()
    print(f"\nMonthly recruitment trends:")
    print(f"  Average recruitments per month: {monthly_recruitment.mean():.1f}")
    print(f"  Max recruitments in a month: {monthly_recruitment.max()}")
    print(f"  Min recruitments in a month: {monthly_recruitment.min()}")
    
    # Analyze churn patterns
    churn_df = df[df['event_type'] == 'churn']
    print(f"\nChurn Analysis:")
    print(f"  Total churns: {len(churn_df)}")
    
    # Churn by level
    level_churn = churn_df['level'].value_counts()
    print(f"  Churn by level:")
    for level, count in level_churn.items():
        print(f"    {level}: {count}")
    
    # Net growth calculation (recruitment - churn)
    monthly_recruitment_counts = recruitment_df.groupby(['year', 'month']).size()
    monthly_churn_counts = churn_df.groupby(['year', 'month']).size()
    
    # Combine the series
    monthly_growth = monthly_recruitment_counts.sub(monthly_churn_counts, fill_value=0)
    
    print(f"\nNet Growth Analysis (Recruitment - Churn):")
    print(f"  Total net growth: {monthly_growth.sum()}")
    print(f"  Average net growth per month: {monthly_growth.mean():.1f}")
    print(f"  Max net growth in a month: {monthly_growth.max()}")
    print(f"  Min net growth in a month: {monthly_growth.min()}")
    
    # Analyze progression patterns
    promotion_df = df[df['event_type'] == 'promotion']
    print(f"\nPromotion Analysis:")
    print(f"  Total promotions: {len(promotion_df)}")
    
    # Promotion by level
    level_promotion = promotion_df['level'].value_counts()
    print(f"  Promotions by level:")
    for level, count in level_promotion.items():
        print(f"    {level}: {count}")
    
    # Check recruitment rates
    print(f"\nRecruitment Rate Analysis:")
    recruitment_rates = recruitment_df['recruitment_rate'].value_counts()
    print(f"  Recruitment rates used:")
    for rate, count in recruitment_rates.items():
        print(f"    {rate}: {count} recruitments")
    
    # Check churn rates
    print(f"\nChurn Rate Analysis:")
    churn_rates = churn_df['churn_rate'].value_counts()
    print(f"  Churn rates used:")
    for rate, count in churn_rates.items():
        print(f"    {rate}: {count} churns")
    
    # Calculate cumulative headcount over time
    print(f"\nCumulative Headcount Analysis:")
    
    # Start with initial headcount (estimate from first month)
    initial_month = df['date'].min()
    first_month_events = df[df['date'] == initial_month]
    
    # Count people who existed before this month (not recruited in this month)
    existing_people = set()
    for _, row in first_month_events.iterrows():
        if row['event_type'] != 'recruitment':
            existing_people.add(row['person_id'])
    
    print(f"  Estimated initial headcount: {len(existing_people)}")
    
    # Calculate monthly net changes
    monthly_changes = []
    current_headcount = len(existing_people)
    
    for (year, month), net_growth in monthly_growth.items():
        current_headcount += net_growth
        monthly_changes.append({
            'year': year,
            'month': month,
            'net_growth': net_growth,
            'headcount': current_headcount
        })
    
    changes_df = pd.DataFrame(monthly_changes)
    
    if not changes_df.empty:
        print(f"  Final headcount: {current_headcount}")
        print(f"  Total growth: {current_headcount - len(existing_people)}")
        print(f"  Growth rate: {((current_headcount / len(existing_people)) - 1) * 100:.1f}%")
        
        # Show growth by year
        yearly_growth = changes_df.groupby('year')['net_growth'].sum()
        print(f"  Yearly net growth:")
        for year, growth in yearly_growth.items():
            print(f"    {year}: {growth}")
    
    return df, changes_df

def identify_potential_issues(df, changes_df):
    """Identify potential issues with the growth model"""
    
    print(f"\n" + "=" * 60)
    print("POTENTIAL ISSUES ANALYSIS")
    print("=" * 60)
    
    # Issue 1: Check if recruitment rates are too high
    recruitment_df = df[df['event_type'] == 'recruitment']
    high_recruitment_rates = recruitment_df[recruitment_df['recruitment_rate'] > 0.1]
    
    if len(high_recruitment_rates) > 0:
        print(f"⚠️  ISSUE 1: High recruitment rates detected")
        print(f"   {len(high_recruitment_rates)} recruitments with rate > 10%")
        print(f"   Max recruitment rate: {recruitment_df['recruitment_rate'].max():.3f}")
        print(f"   Average recruitment rate: {recruitment_df['recruitment_rate'].mean():.3f}")
    
    # Issue 2: Check if churn rates are too low
    churn_df = df[df['event_type'] == 'churn']
    if len(churn_df) > 0:
        print(f"\n📊 Churn rate analysis:")
        print(f"   Average churn rate: {churn_df['churn_rate'].mean():.3f}")
        print(f"   Max churn rate: {churn_df['churn_rate'].max():.3f}")
        print(f"   Min churn rate: {churn_df['churn_rate'].min():.3f}")
    
    # Issue 3: Check recruitment vs churn balance
    total_recruitments = len(recruitment_df)
    total_churns = len(churn_df)
    net_growth = total_recruitments - total_churns
    
    print(f"\n📈 Growth balance analysis:")
    print(f"   Total recruitments: {total_recruitments}")
    print(f"   Total churns: {total_churns}")
    print(f"   Net growth: {net_growth}")
    print(f"   Recruitment/Churn ratio: {total_recruitments/total_churns if total_churns > 0 else 'N/A'}")
    
    if net_growth > total_churns * 0.5:  # If net growth is more than 50% of churns
        print(f"⚠️  ISSUE 2: Very high net growth rate")
        print(f"   Net growth is {net_growth/total_churns:.1f}x the churn rate")
    
    # Issue 4: Check monthly growth patterns
    if not changes_df.empty:
        monthly_growth_rates = changes_df['net_growth'].values
        avg_monthly_growth = np.mean(monthly_growth_rates)
        
        print(f"\n📅 Monthly growth analysis:")
        print(f"   Average monthly net growth: {avg_monthly_growth:.1f}")
        print(f"   Max monthly growth: {np.max(monthly_growth_rates)}")
        print(f"   Min monthly growth: {np.min(monthly_growth_rates)}")
        
        if avg_monthly_growth > 50:  # Arbitrary threshold
            print(f"⚠️  ISSUE 3: Very high average monthly growth")
            print(f"   Average of {avg_monthly_growth:.1f} new people per month")
    
    # Issue 5: Check if growth is accelerating
    if len(changes_df) > 6:  # Need at least 6 months to see trend
        early_growth = changes_df.head(6)['net_growth'].mean()
        late_growth = changes_df.tail(6)['net_growth'].mean()
        
        print(f"\n📈 Growth acceleration analysis:")
        print(f"   Early months (first 6) avg growth: {early_growth:.1f}")
        print(f"   Late months (last 6) avg growth: {late_growth:.1f}")
        
        if late_growth > early_growth * 1.5:
            print(f"⚠️  ISSUE 4: Growth appears to be accelerating")
            print(f"   Later growth is {late_growth/early_growth:.1f}x higher than early growth")

def main():
    """Main analysis function"""
    
    # Analyze the most recent log file
    log_file = "logs/person_events_c37d3279-1e13-4d17-b826-dd00deebc926.csv"
    
    try:
        df, changes_df = analyze_growth_patterns(log_file)
        identify_potential_issues(df, changes_df)
        
        print(f"\n" + "=" * 60)
        print("RECOMMENDATIONS")
        print("=" * 60)
        print("1. Review recruitment rates - they may be too high")
        print("2. Check if churn rates are realistic for the industry")
        print("3. Consider implementing growth caps or constraints")
        print("4. Review the initial headcount calculation")
        print("5. Consider adding office capacity limits")
        
    except Exception as e:
        print(f"Error analyzing file: {e}")

if __name__ == "__main__":
    main() 