#!/usr/bin/env python3
"""
Analyze the initial tenure values from event logs to see what people were initialized with.
"""

import sys
import os
from collections import defaultdict, Counter

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.config_service import config_service

def analyze_initial_tenure():
    """Analyze initial tenure values from event logs"""
    print("🔍 ANALYZING INITIAL TENURE FROM EVENT LOGS")
    print("=" * 60)
    
    # Initialize the simulation engine
    engine = SimulationEngine(config_service)
    
    # Run simulation to get event logs
    print("Running simulation to generate event logs...")
    results = engine.run_simulation(
        start_year=2025, 
        start_month=1, 
        end_year=2025, 
        end_month=12
    )
    
    # Get event logger
    event_logger = results.get('event_logger')
    if not event_logger:
        print("❌ No event logger found!")
        return
    
    # Get all events
    events = event_logger.events
    print(f"📋 Total events logged: {len(events)}")
    
    # Analyze initial tenure by level
    print("\n📊 INITIAL TENURE ANALYSIS BY LEVEL:")
    print("=" * 50)
    
    # Group events by level and analyze tenure
    level_tenure_data = defaultdict(list)
    
    for event in events:
        level = event.level
        total_tenure = event.total_tenure_months
        time_on_level = event.time_on_level_months
        
        level_tenure_data[level].append({
            'total_tenure': total_tenure,
            'time_on_level': time_on_level,
            'event_type': event.event_type.value,
            'date': event.date
        })
    
    # Analyze each level
    for level in sorted(level_tenure_data.keys()):
        events_for_level = level_tenure_data[level]
        
        print(f"\n📋 {level} Level:")
        print(f"  Total events: {len(events_for_level)}")
        
        # Get unique people (by looking at first event for each person)
        unique_people = {}
        for event in events_for_level:
            # Use a simple heuristic: first event for each person
            if event['event_type'] == 'recruitment':
                unique_people[event['total_tenure']] = event
        
        print(f"  Unique people (from recruitment events): {len(unique_people)}")
        
        if unique_people:
            # Analyze tenure distribution
            total_tenures = [data['total_tenure'] for data in unique_people.values()]
            time_on_levels = [data['time_on_level'] for data in unique_people.values()]
            
            print(f"  Total tenure range: {min(total_tenures)} - {max(total_tenures)} months")
            print(f"  Time on level range: {min(time_on_levels)} - {max(time_on_levels)} months")
            print(f"  Average total tenure: {sum(total_tenures) / len(total_tenures):.1f} months")
            print(f"  Average time on level: {sum(time_on_levels) / len(time_on_levels):.1f} months")
            
            # Show distribution
            tenure_counter = Counter(total_tenures)
            print(f"  Total tenure distribution:")
            for tenure, count in sorted(tenure_counter.items()):
                print(f"    {tenure:3d} months: {count:3d} people")
        
        # Check if any people could promote in first year
        if level in ['C', 'SrC', 'AM', 'M']:
            print(f"  🔍 First-year promotion eligibility:")
            
            # Check requirements
            if level == 'C':
                required_total = 27  # 15 + 12
                required_level = 12
            elif level == 'SrC':
                required_total = 45  # 27 + 18
                required_level = 18
            elif level == 'AM':
                required_total = 75  # 45 + 30
                required_level = 30
            elif level == 'M':
                required_total = 99  # 75 + 24
                required_level = 24
            
            eligible_count = 0
            for data in unique_people.values():
                if data['total_tenure'] >= required_total and data['time_on_level'] >= required_level:
                    eligible_count += 1
            
            print(f"    Required total tenure: {required_total} months")
            print(f"    Required time on level: {required_level} months")
            print(f"    Eligible for first-year promotion: {eligible_count}/{len(unique_people)} people")
            
            if eligible_count > 0:
                print(f"    ⚠️  WARNING: {eligible_count} people initialized with unrealistic high tenure!")

if __name__ == "__main__":
    analyze_initial_tenure() 