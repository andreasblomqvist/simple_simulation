#!/usr/bin/env python3
"""
Debug script to track FTE discrepancies between event logs and simulation engine
"""

import json
import os
from datetime import datetime
from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.config_service import ConfigService

def analyze_fte_discrepancy():
    """Analyze the FTE discrepancy between event logs and simulation results"""
    
    print("🔍 FTE DISCREPANCY ANALYSIS")
    print("=" * 50)
    
    # 1. Get starting FTE from configuration
    config_service = ConfigService()
    config = config_service.get_configuration()
    starting_fte = sum(office.get('total_fte', 0) for office in config.values())
    print(f"📊 Starting FTE (from config): {starting_fte}")
    
    # 2. Find the latest event log
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
    
    # 3. Count events in the log
    recruitment_count = 0
    churn_count = 0
    promotion_count = 0
    
    with open(log_path, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:  # Skip header
            parts = line.strip().split(',')
            if len(parts) >= 3:
                event_type = parts[2]
                if event_type == 'recruitment':
                    recruitment_count += 1
                elif event_type == 'churn':
                    churn_count += 1
                elif event_type == 'promotion':
                    promotion_count += 1
    
    print(f"📈 Event counts:")
    print(f"   - Recruitment: {recruitment_count}")
    print(f"   - Churn: {churn_count}")
    print(f"   - Promotion: {promotion_count}")
    
    # 4. Calculate expected FTE from events
    expected_fte = starting_fte + recruitment_count - churn_count
    print(f"🧮 Expected FTE (from events): {starting_fte} + {recruitment_count} - {churn_count} = {expected_fte}")
    
    # 5. Run a simulation to get actual FTE
    print(f"\n🚀 Running simulation to get actual FTE...")
    engine = SimulationEngine()
    
    # Run a 4-year simulation (2025-2028)
    results = engine.run_simulation(2025, 1, 2028, 12)
    
    # Get the final FTE from simulation results
    final_year = "2028"
    if final_year in results.get('years', {}):
        year_data = results['years'][final_year]
        actual_fte = year_data.get('total_fte', 0)
        print(f"📊 Actual FTE (from simulation): {actual_fte}")
        
        # Calculate discrepancy
        discrepancy = expected_fte - actual_fte
        print(f"❌ Discrepancy: {discrepancy} people")
        print(f"   - Expected: {expected_fte}")
        print(f"   - Actual: {actual_fte}")
        print(f"   - Difference: {discrepancy}")
        
        # 6. Detailed analysis by office
        print(f"\n🏢 Detailed analysis by office:")
        offices_data = year_data.get('offices', {})
        for office_name, office_data in offices_data.items():
            office_fte = office_data.get('total_fte', 0)
            print(f"   - {office_name}: {office_fte} FTE")
        
        # 7. Check if there are any issues in the simulation engine
        print(f"\n🔧 Checking simulation engine state:")
        
        # Get current office states from engine
        total_engine_fte = sum(office.total_fte for office in engine.offices.values())
        print(f"   - Engine total FTE: {total_engine_fte}")
        
        # Check if engine FTE matches simulation results
        if total_engine_fte != actual_fte:
            print(f"   ⚠️  Engine FTE ({total_engine_fte}) != Simulation results FTE ({actual_fte})")
        else:
            print(f"   ✅ Engine FTE matches simulation results")
        
        # 8. Check for potential issues
        print(f"\n🔍 Potential issues:")
        
        # Check if any offices have negative FTE
        negative_offices = [name for name, office in engine.offices.items() if office.total_fte < 0]
        if negative_offices:
            print(f"   ❌ Offices with negative FTE: {negative_offices}")
        
        # Check if any levels have negative FTE
        for office_name, office in engine.offices.items():
            for role_name, role_data in office.roles.items():
                if isinstance(role_data, dict):
                    for level_name, level in role_data.items():
                        if level.total < 0:
                            print(f"   ❌ {office_name}.{role_name}.{level_name}: {level.total} FTE")
                else:
                    if role_data.total < 0:
                        print(f"   ❌ {office_name}.{role_name}: {role_data.total} FTE")
        
        # 9. Summary
        print(f"\n📋 SUMMARY:")
        print(f"   - Starting FTE: {starting_fte}")
        print(f"   - Events: +{recruitment_count} -{churn_count}")
        print(f"   - Expected ending FTE: {expected_fte}")
        print(f"   - Actual ending FTE: {actual_fte}")
        print(f"   - Discrepancy: {discrepancy} people")
        
        if discrepancy == 0:
            print(f"   ✅ No discrepancy found!")
        else:
            print(f"   ❌ Discrepancy of {discrepancy} people needs investigation")
            
    else:
        print(f"❌ No data for year {final_year} in simulation results")

if __name__ == "__main__":
    analyze_fte_discrepancy() 