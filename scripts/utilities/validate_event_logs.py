#!/usr/bin/env python3
"""
Event Log Validation Script

This script analyzes the event logs to validate that all events follow the business logic:
1. Progression only occurs in allowed months
2. Progression only occurs with sufficient time on level
3. CAT categories are correctly assigned
4. Progression probabilities match the configuration
5. No invalid level transitions
"""

import csv
import sys
from datetime import datetime
from collections import defaultdict, Counter

# Import progression configuration
sys.path.append('backend')
from config.progression_config import PROGRESSION_CONFIG, CAT_CURVES

def parse_date(date_str):
    """Parse date string in format YYYY-MM"""
    try:
        return datetime.strptime(date_str, "%Y-%m")
    except ValueError:
        return None

def get_cat_category(time_on_level):
    """Determine CAT category based on time on level"""
    if time_on_level < 6:
        return "CAT0"
    elif time_on_level < 12:
        return "CAT6"
    elif time_on_level < 18:
        return "CAT12"
    elif time_on_level < 24:
        return "CAT18"
    elif time_on_level < 30:
        return "CAT24"
    elif time_on_level < 36:
        return "CAT30"
    elif time_on_level < 42:
        return "CAT36"
    elif time_on_level < 48:
        return "CAT42"
    elif time_on_level < 54:
        return "CAT48"
    elif time_on_level < 60:
        return "CAT54"
    else:
        return "CAT60"

def validate_event_log(log_file):
    """Validate all events in the log file"""
    anomalies = []
    stats = {
        'total_events': 0,
        'promotions': 0,
        'churn_events': 0,
        'recruitment_events': 0,
        'invalid_months': 0,
        'insufficient_time': 0,
        'wrong_cat': 0,
        'wrong_probability': 0,
        'invalid_transition': 0
    }
    
    person_history = defaultdict(list)
    
    with open(log_file, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            stats['total_events'] += 1
            event_type = row['event_type']
            
            if event_type == 'promotion':
                stats['promotions'] += 1
                anomalies.extend(validate_promotion_event(row, person_history))
            elif event_type == 'churn':
                stats['churn_events'] += 1
            elif event_type == 'recruitment':
                stats['recruitment_events'] += 1
            
            # Track person history
            person_id = row['person_id']
            person_history[person_id].append(row)
    
    return anomalies, stats, person_history

def validate_promotion_event(event, person_history):
    """Validate a single promotion event"""
    anomalies = []
    
    # Extract event data
    date = parse_date(event['date'])
    from_level = event['from_level']
    to_level = event['to_level']
    time_on_level = int(event['time_on_level_months'])
    total_tenure = int(event['total_tenure_months'])
    cat_category = event['cat_category']
    progression_probability = float(event['progression_probability'])
    
    # 1. Check if progression month is allowed
    if from_level in PROGRESSION_CONFIG:
        allowed_months = PROGRESSION_CONFIG[from_level]['progression_months']
        if date and date.month not in allowed_months:
            anomalies.append({
                'type': 'invalid_month',
                'event_id': event['event_id'],
                'person_id': event['person_id'],
                'date': event['date'],
                'level': from_level,
                'allowed_months': allowed_months,
                'actual_month': date.month
            })
    
    # 2. Check if person has sufficient time on level
    if from_level in PROGRESSION_CONFIG:
        required_time = PROGRESSION_CONFIG[from_level]['time_on_level']
        if time_on_level < required_time:
            anomalies.append({
                'type': 'insufficient_time',
                'event_id': event['event_id'],
                'person_id': event['person_id'],
                'level': from_level,
                'required_time': required_time,
                'actual_time': time_on_level
            })
    
    # 3. Check if CAT category is correct
    expected_cat = get_cat_category(time_on_level)
    if cat_category != expected_cat:
        anomalies.append({
            'type': 'wrong_cat',
            'event_id': event['event_id'],
            'person_id': event['person_id'],
            'level': from_level,
            'time_on_level': time_on_level,
            'expected_cat': expected_cat,
            'actual_cat': cat_category
        })
    
    # 4. Check if progression probability matches configuration
    if from_level in CAT_CURVES and cat_category in CAT_CURVES[from_level]:
        expected_prob = CAT_CURVES[from_level][cat_category]
        if abs(progression_probability - expected_prob) > 0.001:  # Allow small floating point differences
            anomalies.append({
                'type': 'wrong_probability',
                'event_id': event['event_id'],
                'person_id': event['person_id'],
                'level': from_level,
                'cat_category': cat_category,
                'expected_probability': expected_prob,
                'actual_probability': progression_probability
            })
    
    # 5. Check if level transition is valid
    if from_level in PROGRESSION_CONFIG:
        expected_next = PROGRESSION_CONFIG[from_level]['next_level']
        if to_level != expected_next:
            anomalies.append({
                'type': 'invalid_transition',
                'event_id': event['event_id'],
                'person_id': event['person_id'],
                'from_level': from_level,
                'to_level': to_level,
                'expected_next': expected_next
            })
    
    return anomalies

def analyze_promotion_patterns(person_history):
    """Analyze promotion patterns across individuals"""
    patterns = {
        'multiple_promotions': [],
        'rapid_promotions': [],
        'level_skipping': []
    }
    
    for person_id, events in person_history.items():
        promotions = [e for e in events if e['event_type'] == 'promotion']
        
        if len(promotions) > 1:
            patterns['multiple_promotions'].append({
                'person_id': person_id,
                'promotion_count': len(promotions),
                'promotions': promotions
            })
        
        # Check for rapid promotions (less than 6 months between)
        for i in range(len(promotions) - 1):
            date1 = parse_date(promotions[i]['date'])
            date2 = parse_date(promotions[i + 1]['date'])
            if date1 and date2:
                months_diff = (date2.year - date1.year) * 12 + (date2.month - date1.month)
                if months_diff < 6:
                    patterns['rapid_promotions'].append({
                        'person_id': person_id,
                        'promotion1': promotions[i],
                        'promotion2': promotions[i + 1],
                        'months_between': months_diff
                    })
    
    return patterns

def print_validation_report(anomalies, stats, patterns):
    """Print a comprehensive validation report"""
    print("=" * 80)
    print("EVENT LOG VALIDATION REPORT")
    print("=" * 80)
    
    print(f"\nEVENT STATISTICS:")
    print(f"  Total events: {stats['total_events']}")
    print(f"  Promotions: {stats['promotions']}")
    print(f"  Churn events: {stats['churn_events']}")
    print(f"  Recruitment events: {stats['recruitment_events']}")
    
    print(f"\nANOMALIES FOUND: {len(anomalies)}")
    if anomalies:
        anomaly_types = Counter([a['type'] for a in anomalies])
        for anomaly_type, count in anomaly_types.most_common():
            print(f"  {anomaly_type}: {count}")
        
        print(f"\nDETAILED ANOMALIES:")
        for i, anomaly in enumerate(anomalies[:20], 1):  # Show first 20
            print(f"\n{i}. {anomaly['type'].upper()}")
            print(f"   Event ID: {anomaly['event_id']}")
            print(f"   Person ID: {anomaly['person_id']}")
            
            if anomaly['type'] == 'invalid_month':
                print(f"   Level: {anomaly['level']}")
                print(f"   Allowed months: {anomaly['allowed_months']}")
                print(f"   Actual month: {anomaly['actual_month']}")
            elif anomaly['type'] == 'insufficient_time':
                print(f"   Level: {anomaly['level']}")
                print(f"   Required time: {anomaly['required_time']} months")
                print(f"   Actual time: {anomaly['actual_time']} months")
            elif anomaly['type'] == 'wrong_cat':
                print(f"   Level: {anomaly['level']}")
                print(f"   Time on level: {anomaly['time_on_level']} months")
                print(f"   Expected CAT: {anomaly['expected_cat']}")
                print(f"   Actual CAT: {anomaly['actual_cat']}")
            elif anomaly['type'] == 'wrong_probability':
                print(f"   Level: {anomaly['level']}")
                print(f"   CAT: {anomaly['cat_category']}")
                print(f"   Expected probability: {anomaly['expected_probability']}")
                print(f"   Actual probability: {anomaly['actual_probability']}")
            elif anomaly['type'] == 'invalid_transition':
                print(f"   From level: {anomaly['from_level']}")
                print(f"   To level: {anomaly['to_level']}")
                print(f"   Expected next: {anomaly['expected_next']}")
        
        if len(anomalies) > 20:
            print(f"\n... and {len(anomalies) - 20} more anomalies")
    else:
        print("  ✅ No anomalies found! All events follow business logic.")
    
    print(f"\nPROMOTION PATTERNS:")
    print(f"  People with multiple promotions: {len(patterns['multiple_promotions'])}")
    print(f"  Rapid promotions (<6 months): {len(patterns['rapid_promotions'])}")
    
    if patterns['multiple_promotions']:
        print(f"\n  Top promotion counts:")
        promotion_counts = Counter([p['promotion_count'] for p in patterns['multiple_promotions']])
        for count, num_people in promotion_counts.most_common(5):
            print(f"    {count} promotions: {num_people} people")

def main():
    """Main validation function"""
    import glob
    
    # Find all event log files
    log_files = glob.glob("logs/person_events_*.csv")
    
    if not log_files:
        print("No event log files found in logs/ directory")
        return
    
    print(f"Found {len(log_files)} event log files")
    
    for log_file in log_files:
        print(f"\n{'='*60}")
        print(f"VALIDATING: {log_file}")
        print(f"{'='*60}")
        
        try:
            anomalies, stats, person_history = validate_event_log(log_file)
            patterns = analyze_promotion_patterns(person_history)
            print_validation_report(anomalies, stats, patterns)
        except Exception as e:
            print(f"Error processing {log_file}: {e}")

if __name__ == "__main__":
    main() 