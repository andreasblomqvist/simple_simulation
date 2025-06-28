#!/usr/bin/env python3
"""
Deep analysis of simulation event log to verify progression, recruitment, and churn logic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.kpi.kpi_models import EconomicParameters
from collections import defaultdict, Counter
import pandas as pd
from datetime import datetime
from backend.src.services.simulation.event_logger import EventType

def analyze_event_log():
    """Analyze the event log for progression, recruitment, and churn events"""
    
    print("🔍 DEEP EVENT LOG ANALYSIS")
    print("=" * 60)
    
    # Create engine and run simulation
    engine = SimulationEngine()
    economic_params = EconomicParameters(
        unplanned_absence=0.05,
        other_expense=19000000.0,
        employment_cost_rate=0.40,
        working_hours_per_month=166.4
    )
    
    print("📊 Running simulation to generate event log...")
    results = engine.run_simulation(
        start_year=2025,
        start_month=1,
        end_year=2025,
        end_month=12,
        price_increase=0.02,
        salary_increase=0.02,
        economic_params=economic_params
    )
    
    print("✅ Simulation completed")
    print("")
    
    # Get event logger
    event_logger = results.get('event_logger')
    if not event_logger:
        print("❌ No event logger found in results")
        return
    
    events = event_logger.events
    print(f"📋 Total events logged: {len(events)}")
    print("")
    
    # 1. Event Type Analysis
    print("📊 EVENT TYPE BREAKDOWN")
    print("-" * 40)
    event_types = Counter(getattr(event, 'event_type', None) for event in events)
    for event_type, count in event_types.most_common():
        print(f"  {event_type}: {count} events")
    print("")
    
    # 2. Monthly Distribution
    print("📅 MONTHLY EVENT DISTRIBUTION")
    print("-" * 40)
    monthly_events = defaultdict(int)
    for event in events:
        month = getattr(event, 'current_date', None)
        monthly_events[month] += 1
    
    for month in sorted(monthly_events.keys()):
        print(f"  {month}: {monthly_events[month]} events")
    print("")
    
    # 3. Office Distribution
    print("🏢 OFFICE EVENT DISTRIBUTION")
    print("-" * 40)
    office_events = Counter(getattr(event, 'office', None) for event in events)
    for office, count in office_events.most_common():
        print(f"  {office}: {count} events")
    print("")
    
    # 4. Role Distribution
    print("👥 ROLE EVENT DISTRIBUTION")
    print("-" * 40)
    role_events = Counter(getattr(event, 'role', None) for event in events)
    for role, count in role_events.most_common():
        print(f"  {role}: {count} events")
    print("")
    
    # 5. Level Distribution
    print("📈 LEVEL EVENT DISTRIBUTION")
    print("-" * 40)
    level_events = Counter(getattr(event, 'level', 'N/A') for event in events)
    for level, count in level_events.most_common():
        print(f"  {level}: {count} events")
    print("")
    
    # 6. Detailed Progression Analysis
    print("🚀 PROGRESSION ANALYSIS")
    print("-" * 40)
    progression_events = [e for e in events if getattr(e, 'event_type', None) == EventType.PROMOTION]
    print(f"Total progression events: {len(progression_events)}")
    
    if progression_events:
        # Progression by office
        prog_by_office = Counter(getattr(e, 'office', None) for e in progression_events)
        print("\nProgression by office:")
        for office, count in prog_by_office.most_common():
            print(f"  {office}: {count} promotions")
        
        # Progression by level
        prog_by_level = Counter(getattr(e, 'level', 'N/A') for e in progression_events)
        print("\nProgression by level:")
        for level, count in prog_by_level.most_common():
            print(f"  {level}: {count} promotions")
        
        # Progression by month
        prog_by_month = Counter(getattr(e, 'current_date', None) for e in progression_events)
        print("\nProgression by month:")
        for month in sorted(prog_by_month.keys()):
            print(f"  {month}: {prog_by_month[month]} promotions")
        
        # Check for progression in disallowed months
        print("\n🔍 PROGRESSION VALIDATION:")
        from backend.config.progression_config import PROGRESSION_CONFIG
        
        invalid_progressions = []
        for event in progression_events:
            level = getattr(event, 'level', None)
            month_str = getattr(event, 'current_date', '1-1')
            month = int(month_str.split('-')[1])
            
            if level in PROGRESSION_CONFIG:
                allowed_months = PROGRESSION_CONFIG[level]['progression_months']
                if month not in allowed_months:
                    invalid_progressions.append({
                        'level': level,
                        'month': month,
                        'allowed_months': allowed_months,
                        'office': getattr(event, 'office', None)
                    })
        
        if invalid_progressions:
            print("  ❌ INVALID PROGRESSIONS FOUND:")
            for invalid in invalid_progressions:
                print(f"    {invalid['office']} {invalid['level']}: Month {invalid['month']} (allowed: {invalid['allowed_months']})")
        else:
            print("  ✅ All progressions occurred in allowed months")
    
    print("")
    
    # 7. Detailed Recruitment Analysis
    print("📥 RECRUITMENT ANALYSIS")
    print("-" * 40)
    recruitment_events = [e for e in events if getattr(e, 'event_type', None) == EventType.RECRUITMENT]
    print(f"Total recruitment events: {len(recruitment_events)}")
    
    if recruitment_events:
        # Recruitment by office
        rec_by_office = Counter(getattr(e, 'office', None) for e in recruitment_events)
        print("\nRecruitment by office:")
        for office, count in rec_by_office.most_common():
            print(f"  {office}: {count} recruits")
        
        # Recruitment by role
        rec_by_role = Counter(getattr(e, 'role', None) for e in recruitment_events)
        print("\nRecruitment by role:")
        for role, count in rec_by_role.most_common():
            print(f"  {role}: {count} recruits")
        
        # Recruitment by level
        rec_by_level = Counter(getattr(e, 'level', 'N/A') for e in recruitment_events)
        print("\nRecruitment by level:")
        for level, count in rec_by_level.most_common():
            print(f"  {level}: {count} recruits")
        
        # Recruitment by month
        rec_by_month = Counter(getattr(e, 'current_date', None) for e in recruitment_events)
        print("\nRecruitment by month:")
        for month in sorted(rec_by_month.keys()):
            print(f"  {month}: {rec_by_month[month]} recruits")
    
    print("")
    
    # 8. Detailed Churn Analysis
    print("📤 CHURN ANALYSIS")
    print("-" * 40)
    churn_events = [e for e in events if getattr(e, 'event_type', None) == EventType.CHURN]
    print(f"Total churn events: {len(churn_events)}")
    
    if churn_events:
        # Churn by office
        churn_by_office = Counter(getattr(e, 'office', None) for e in churn_events)
        print("\nChurn by office:")
        for office, count in churn_by_office.most_common():
            print(f"  {office}: {count} churns")
        
        # Churn by role
        churn_by_role = Counter(getattr(e, 'role', None) for e in churn_events)
        print("\nChurn by role:")
        for role, count in churn_by_role.most_common():
            print(f"  {role}: {count} churns")
        
        # Churn by level
        churn_by_level = Counter(getattr(e, 'level', 'N/A') for e in churn_events)
        print("\nChurn by level:")
        for level, count in churn_by_level.most_common():
            print(f"  {level}: {count} churns")
        
        # Churn by month
        churn_by_month = Counter(getattr(e, 'current_date', None) for e in churn_events)
        print("\nChurn by month:")
        for month in sorted(churn_by_month.keys()):
            print(f"  {month}: {churn_by_month[month]} churns")
    
    print("")
    
    # 9. Net Change Analysis
    print("📊 NET CHANGE ANALYSIS")
    print("-" * 40)
    
    # Calculate net changes by office
    office_changes = defaultdict(lambda: {'recruitment': 0, 'churn': 0, 'progression': 0})
    
    for event in events:
        office = getattr(event, 'office', None)
        event_type = getattr(event, 'event_type', None)
        
        if event_type == EventType.RECRUITMENT:
            office_changes[office]['recruitment'] += 1
        elif event_type == EventType.CHURN:
            office_changes[office]['churn'] += 1
        elif event_type == EventType.PROMOTION:
            office_changes[office]['progression'] += 1
    
    print("Net changes by office (recruitment - churn):")
    for office, changes in sorted(office_changes.items()):
        net_change = changes['recruitment'] - changes['churn']
        print(f"  {office}: +{changes['recruitment']} -{changes['churn']} = {net_change:+d} (progression: {changes['progression']})")
    
    print("")
    
    # 10. Sample Event Details
    print("🔍 SAMPLE EVENT DETAILS")
    print("-" * 40)
    
    event_type_map = {
        'progression': EventType.PROMOTION,
        'recruitment': EventType.RECRUITMENT,
        'churn': EventType.CHURN
    }
    for label, enum_val in event_type_map.items():
        type_events = [e for e in events if getattr(e, 'event_type', None) == enum_val]
        if type_events:
            sample = type_events[0]
            print(f"\nSample {label} event:")
            for key in dir(sample):
                if not key.startswith('_') and not callable(getattr(sample, key)):
                    value = getattr(sample, key)
                    print(f"  {key}: {value}")
    
    print("")
    print("✅ Event log analysis completed")

if __name__ == "__main__":
    analyze_event_log() 