#!/usr/bin/env python3
"""
Debug script to analyze promotion events in detail
"""

import json
import os
from datetime import datetime
from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.config_service import ConfigService

def analyze_promotion_events():
    """Analyze promotion events to understand FTE losses"""
    
    print("🔍 PROMOTION EVENT ANALYSIS")
    print("=" * 50)
    
    # 1. Find the latest event log
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        print("❌ No logs directory found")
        return
    
    event_logs = [f for f in os.listdir(logs_dir) if f.startswith("person_events_") and f.endswith(".csv")]
    if not event_logs:
        print("❌ No event logs found")
        return
    
    # Get the most recent log
    latest_log = sorted(event_logs)[-1]
    log_path = os.path.join(logs_dir, latest_log)
    print(f"📄 Analyzing log: {latest_log}")
    
    # 2. Analyze promotion events
    promotions_by_level = {}
    promotions_by_office = {}
    total_promotions = 0
    
    with open(log_path, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:  # Skip header
            parts = line.strip().split(',')
            if len(parts) >= 8:
                event_type = parts[2]
                if event_type == 'promotion':
                    total_promotions += 1
                    person = parts[1]
                    from_level = parts[4]
                    to_level = parts[5]
                    office = parts[6]
                    
                    # Track by from_level
                    if from_level not in promotions_by_level:
                        promotions_by_level[from_level] = {'out': 0, 'to': {}}
                    promotions_by_level[from_level]['out'] += 1
                    
                    if to_level not in promotions_by_level[from_level]['to']:
                        promotions_by_level[from_level]['to'][to_level] = 0
                    promotions_by_level[from_level]['to'][to_level] += 1
                    
                    # Track by office
                    if office not in promotions_by_office:
                        promotions_by_office[office] = {'out': 0, 'in': 0}
                    promotions_by_office[office]['out'] += 1
    
    print(f"📈 Total promotions: {total_promotions}")
    
    # 3. Analyze promotions by level
    print(f"\n🏢 Promotions by level:")
    for level, data in promotions_by_level.items():
        print(f"   {level}:")
        print(f"     - Promoted out: {data['out']}")
        for to_level, count in data['to'].items():
            print(f"     - To {to_level}: {count}")
    
    # 4. Check for people graduating (no next level)
    print(f"\n🎓 Graduation analysis:")
    config_service = ConfigService()
    config = config_service.get_configuration()
    
    # Get actual level order from config
    actual_levels = set()
    for office_config in config.values():
        for role_name, role_data in office_config.get('roles', {}).items():
            if role_name != 'Operations':
                actual_levels.update(role_data.keys())
    
    actual_level_order = ['A', 'AC', 'AM', 'C', 'SrC', 'M', 'SrM', 'PiP']
    actual_level_order = [level for level in actual_level_order if level in actual_levels]
    
    print(f"   Actual level order: {actual_level_order}")
    
    # Check which levels are at the top (no next level)
    top_levels = []
    for level in actual_level_order:
        next_level_index = actual_level_order.index(level) + 1
        if next_level_index >= len(actual_level_order):
            top_levels.append(level)
    
    print(f"   Top levels (no next level): {top_levels}")
    
    # Count graduations (promotions from top levels)
    graduations = 0
    for level in top_levels:
        if level in promotions_by_level:
            graduations += promotions_by_level[level]['out']
    
    print(f"   Total graduations: {graduations}")
    
    # 5. Check for missing next levels
    print(f"\n🔍 Missing next level analysis:")
    for level, data in promotions_by_level.items():
        if level not in actual_level_order:
            print(f"   ❌ {level} not in actual level order!")
            continue
            
        level_index = actual_level_order.index(level)
        next_level_index = level_index + 1
        
        if next_level_index < len(actual_level_order):
            expected_next = actual_level_order[next_level_index]
            actual_nexts = list(data['to'].keys())
            
            if expected_next not in actual_nexts:
                print(f"   ❌ {level} -> expected {expected_next}, got {actual_nexts}")
            else:
                print(f"   ✅ {level} -> {expected_next} ({data['to'][expected_next]} people)")
        else:
            print(f"   🎓 {level} -> GRADUATION ({data['out']} people)")
    
    # 6. Run simulation to get final state
    print(f"\n🚀 Running simulation to check final state...")
    engine = SimulationEngine()
    results = engine.run_simulation(2025, 1, 2028, 12)
    
    # Check final FTE by level
    print(f"\n📊 Final FTE by level:")
    for office_name, office in engine.offices.items():
        print(f"   {office_name}:")
        for role_name, role_data in office.roles.items():
            if isinstance(role_data, dict):
                for level_name, level in role_data.items():
                    if level.total > 0:
                        print(f"     {role_name}.{level_name}: {level.total} FTE")
            else:
                if role_data.total > 0:
                    print(f"     {role_name}: {role_data.total} FTE")

if __name__ == "__main__":
    analyze_promotion_events() 