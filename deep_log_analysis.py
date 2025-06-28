#!/usr/bin/env python3
"""
Deep analysis of simulation event logs to understand patterns and validate realistic initialization.
"""

import sys
import os
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from datetime import datetime
import matplotlib.pyplot as plt

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def analyze_event_log(log_file_path):
    """Perform deep analysis of event log"""
    print("🔍 DEEP ANALYSIS OF SIMULATION LOGS")
    print("=" * 80)
    
    # Read the event log
    try:
        df = pd.read_csv(log_file_path)
        print(f"✅ Loaded event log: {log_file_path}")
        print(f"📊 Total events: {len(df):,}")
        print(f"📅 Date range: {df['date'].min()} to {df['date'].max()}")
    except Exception as e:
        print(f"❌ Error loading log file: {e}")
        return
    
    # Basic statistics
    print(f"\n📈 EVENT TYPE DISTRIBUTION:")
    event_counts = df['event_type'].value_counts()
    for event_type, count in event_counts.items():
        print(f"  {event_type}: {count:,} events")
    
    # Analyze by level
    print(f"\n🏢 ANALYSIS BY LEVEL:")
    level_stats = df.groupby('level').agg({
        'total_tenure_months': ['count', 'min', 'max', 'mean', 'std'],
        'time_on_level_months': ['min', 'max', 'mean', 'std']
    }).round(2)
    
    for level in sorted(df['level'].unique()):
        level_data = df[df['level'] == level]
        print(f"\n📋 {level} Level:")
        print(f"  Total events: {len(level_data):,}")
        
        # Tenure analysis
        tenure_stats = level_data['total_tenure_months'].describe()
        level_tenure_stats = level_data['time_on_level_months'].describe()
        
        print(f"  Total tenure: {tenure_stats['min']:.1f} - {tenure_stats['max']:.1f} months (avg: {tenure_stats['mean']:.1f})")
        print(f"  Time on level: {level_tenure_stats['min']:.1f} - {level_tenure_stats['max']:.1f} months (avg: {level_tenure_stats['mean']:.1f})")
        
        # Promotion analysis
        promotions = level_data[level_data['event_type'] == 'promotion']
        if len(promotions) > 0:
            print(f"  Promotions: {len(promotions):,}")
            avg_promotion_tenure = promotions['total_tenure_months'].mean()
            avg_promotion_level_tenure = promotions['time_on_level_months'].mean()
            print(f"    Avg promotion tenure: {avg_promotion_tenure:.1f} months")
            print(f"    Avg promotion level tenure: {avg_promotion_level_tenure:.1f} months")
        
        # Recruitment analysis
        recruitments = level_data[level_data['event_type'] == 'recruitment']
        if len(recruitments) > 0:
            print(f"  New recruits: {len(recruitments):,}")
            avg_recruit_tenure = recruitments['total_tenure_months'].mean()
            print(f"    Avg recruit tenure: {avg_recruit_tenure:.1f} months")
    
    # Analyze promotion patterns
    print(f"\n🚀 PROMOTION ANALYSIS:")
    promotions = df[df['event_type'] == 'promotion']
    
    if len(promotions) > 0:
        print(f"Total promotions: {len(promotions):,}")
        
        # Promotion by month
        monthly_promotions = promotions.groupby('date').size()
        print(f"\n📅 Promotions by month:")
        for date, count in monthly_promotions.items():
            print(f"  {date}: {count} promotions")
        
        # Promotion by level transition
        level_transitions = promotions.groupby(['from_level', 'to_level']).size()
        print(f"\n🔄 Level transitions:")
        for (from_level, to_level), count in level_transitions.items():
            print(f"  {from_level} → {to_level}: {count} promotions")
        
        # Tenure at promotion
        print(f"\n⏰ Tenure at promotion:")
        for level in sorted(promotions['from_level'].unique()):
            level_promotions = promotions[promotions['from_level'] == level]
            avg_tenure = level_promotions['total_tenure_months'].mean()
            avg_level_tenure = level_promotions['time_on_level_months'].mean()
            print(f"  {level}: {avg_tenure:.1f} months total, {avg_level_tenure:.1f} months on level")
    
    # Analyze recruitment patterns
    print(f"\n👥 RECRUITMENT ANALYSIS:")
    recruitments = df[df['event_type'] == 'recruitment']
    
    if len(recruitments) > 0:
        print(f"Total recruitments: {len(recruitments):,}")
        
        # Recruitment by month
        monthly_recruitments = recruitments.groupby('date').size()
        print(f"\n📅 Recruitments by month:")
        for date, count in monthly_recruitments.items():
            print(f"  {date}: {count} recruitments")
        
        # Recruitment by level
        level_recruitments = recruitments.groupby('level').size()
        print(f"\n📊 Recruitments by level:")
        for level, count in level_recruitments.items():
            print(f"  {level}: {count} recruitments")
    
    # Analyze churn patterns
    print(f"\n🚪 CHURN ANALYSIS:")
    churns = df[df['event_type'] == 'churn']
    
    if len(churns) > 0:
        print(f"Total churns: {len(churns):,}")
        
        # Churn by month
        monthly_churns = churns.groupby('date').size()
        print(f"\n📅 Churns by month:")
        for date, count in monthly_churns.items():
            print(f"  {date}: {count} churns")
        
        # Churn by level
        level_churns = churns.groupby('level').size()
        print(f"\n📊 Churns by level:")
        for level, count in level_churns.items():
            print(f"  {level}: {count} churns")
    
    # Analyze office patterns
    print(f"\n🏢 OFFICE ANALYSIS:")
    office_stats = df.groupby('office').agg({
        'event_type': 'count',
        'total_tenure_months': ['mean', 'std'],
        'time_on_level_months': ['mean', 'std']
    }).round(2)
    
    for office in sorted(df['office'].unique()):
        office_data = df[df['office'] == office]
        print(f"\n📋 {office}:")
        print(f"  Total events: {len(office_data):,}")
        
        # Event types by office
        office_events = office_data['event_type'].value_counts()
        for event_type, count in office_events.items():
            print(f"    {event_type}: {count:,}")
        
        # Average tenure by office
        avg_tenure = office_data['total_tenure_months'].mean()
        avg_level_tenure = office_data['time_on_level_months'].mean()
        print(f"    Avg total tenure: {avg_tenure:.1f} months")
        print(f"    Avg level tenure: {avg_level_tenure:.1f} months")
    
    # Analyze CAT patterns
    print(f"\n📊 CAT ANALYSIS:")
    cat_data = df[df['cat_category'].notna()]
    
    if len(cat_data) > 0:
        print(f"Events with CAT data: {len(cat_data):,}")
        
        # CAT distribution
        cat_counts = cat_data['cat_category'].value_counts()
        print(f"\n📈 CAT distribution:")
        for cat, count in cat_counts.head(10).items():
            print(f"  {cat}: {count:,} events")
        
        # CAT by level
        cat_by_level = cat_data.groupby(['level', 'cat_category']).size()
        print(f"\n📊 CAT by level:")
        for (level, cat), count in cat_by_level.items():
            print(f"  {level} {cat}: {count:,} events")
    
    # Analyze progression probability patterns
    print(f"\n🎯 PROGRESSION PROBABILITY ANALYSIS:")
    prob_data = df[df['progression_probability'].notna()]
    
    if len(prob_data) > 0:
        print(f"Events with progression probability: {len(prob_data):,}")
        
        prob_stats = prob_data['progression_probability'].describe()
        print(f"Progression probability stats:")
        print(f"  Min: {prob_stats['min']:.3f}")
        print(f"  Max: {prob_stats['max']:.3f}")
        print(f"  Mean: {prob_stats['mean']:.3f}")
        print(f"  Std: {prob_stats['std']:.3f}")
        
        # Probability by level
        prob_by_level = prob_data.groupby('level')['progression_probability'].agg(['mean', 'std', 'count'])
        print(f"\n📊 Progression probability by level:")
        for level, stats in prob_by_level.iterrows():
            print(f"  {level}: {stats['mean']:.3f} ± {stats['std']:.3f} ({stats['count']:,} events)")
    
    # Analyze realistic initialization validation
    print(f"\n✅ REALISTIC INITIALIZATION VALIDATION:")
    
    # Check if initial population has realistic tenure
    initial_events = df[df['date'] == '2025-1']
    initial_promotions = initial_events[initial_events['event_type'] == 'promotion']
    
    if len(initial_promotions) > 0:
        print(f"Initial month promotions: {len(initial_promotions):,}")
        
        # Check tenure ranges for each level
        for level in sorted(initial_promotions['from_level'].unique()):
            level_promotions = initial_promotions[initial_promotions['from_level'] == level]
            avg_tenure = level_promotions['total_tenure_months'].mean()
            avg_level_tenure = level_promotions['time_on_level_months'].mean()
            
            print(f"  {level} → {level_promotions['to_level'].iloc[0]}: {avg_tenure:.1f} months total, {avg_level_tenure:.1f} months on level")
            
            # Validate against expected ranges
            expected_ranges = {
                'A': (0, 6),
                'AC': (6, 15),
                'C': (15, 33),
                'SrC': (33, 51),
                'AM': (51, 99),
                'M': (99, 147),
                'SrM': (147, 267)
            }
            
            if level in expected_ranges:
                min_expected, max_expected = expected_ranges[level]
                if min_expected <= avg_tenure <= max_expected:
                    print(f"    ✅ Realistic tenure range")
                else:
                    print(f"    ⚠️  Tenure outside expected range ({min_expected}-{max_expected})")
    
    # Summary statistics
    print(f"\n📊 SUMMARY STATISTICS:")
    print(f"Total events: {len(df):,}")
    print(f"Unique people: {df['person_id'].nunique():,}")
    print(f"Offices: {df['office'].nunique()}")
    print(f"Levels: {df['level'].nunique()}")
    print(f"Roles: {df['role'].nunique()}")
    
    # Event rate analysis
    print(f"\n📈 EVENT RATE ANALYSIS:")
    events_per_month = df.groupby('date').size()
    print(f"Average events per month: {events_per_month.mean():.1f}")
    print(f"Max events in a month: {events_per_month.max()}")
    print(f"Min events in a month: {events_per_month.min()}")
    
    return df

def analyze_tenure_distribution(df):
    """Analyze tenure distribution patterns"""
    print(f"\n🔍 TENURE DISTRIBUTION ANALYSIS:")
    print("=" * 50)
    
    # Overall tenure distribution
    print(f"Overall tenure distribution:")
    tenure_stats = df['total_tenure_months'].describe()
    print(f"  Min: {tenure_stats['min']:.1f} months")
    print(f"  25%: {tenure_stats['25%']:.1f} months")
    print(f"  50%: {tenure_stats['50%']:.1f} months")
    print(f"  75%: {tenure_stats['75%']:.1f} months")
    print(f"  Max: {tenure_stats['max']:.1f} months")
    
    # Tenure distribution by level
    print(f"\nTenure distribution by level:")
    for level in sorted(df['level'].unique()):
        level_data = df[df['level'] == level]
        level_tenure = level_data['total_tenure_months']
        
        print(f"\n  {level}:")
        print(f"    Count: {len(level_data):,}")
        print(f"    Mean: {level_tenure.mean():.1f} months")
        print(f"    Std: {level_tenure.std():.1f} months")
        print(f"    Range: {level_tenure.min():.1f} - {level_tenure.max():.1f} months")
        
        # Tenure buckets
        buckets = [0, 6, 12, 24, 36, 48, 60, 120, float('inf')]
        bucket_labels = ['0-6m', '6-12m', '12-24m', '24-36m', '36-48m', '48-60m', '60-120m', '120m+']
        
        tenure_buckets = pd.cut(level_tenure, bins=buckets, labels=bucket_labels, include_lowest=True)
        bucket_counts = tenure_buckets.value_counts().sort_index()
        
        print(f"    Distribution:")
        for bucket, count in bucket_counts.items():
            if count > 0:
                percentage = (count / len(level_data)) * 100
                print(f"      {bucket}: {count:,} ({percentage:.1f}%)")

if __name__ == "__main__":
    # Find the most recent log file
    import glob
    log_files = glob.glob("logs/person_events_*.csv")
    
    if not log_files:
        print("❌ No event log files found!")
        sys.exit(1)
    
    # Get the most recent file
    latest_log = max(log_files, key=os.path.getctime)
    print(f"📁 Analyzing latest log file: {latest_log}")
    
    # Perform analysis
    df = analyze_event_log(latest_log)
    
    if df is not None:
        analyze_tenure_distribution(df)
        
        print(f"\n✅ Analysis complete!")
        print(f"📁 Log file: {latest_log}")
        print(f"📊 Total events analyzed: {len(df):,}") 