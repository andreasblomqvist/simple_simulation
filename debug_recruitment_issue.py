#!/usr/bin/env python3
"""
Debug the recruitment issue by examining the simulation engine directly
"""

import sys
import os
import json

# Add the backend src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from services.simulation_engine import SimulationEngine
from services.config_service import ConfigService

def debug_recruitment():
    print("🔍 DEBUGGING RECRUITMENT ISSUE")
    print("=" * 50)
    
    # Initialize services
    config_service = ConfigService()
    engine = SimulationEngine(config_service)
    
    # Initialize with configuration
    engine.reinitialize_with_config()
    
    print(f"📊 Engine initialized with {len(engine.offices)} offices")
    print(f"   Office names: {list(engine.offices.keys())}")
    
    # Check Stockholm A level before simulation
    stockholm_office = engine.offices.get('Stockholm')
    if not stockholm_office:
        print("❌ Stockholm office not found")
        return
    
    if 'Consultant' not in stockholm_office.roles or 'A' not in stockholm_office.roles['Consultant']:
        print("❌ Stockholm Consultant A level not found")
        return
    
    a_level = stockholm_office.roles['Consultant']['A']
    
    print(f"📊 BEFORE SIMULATION:")
    print(f"   Stockholm A Level FTE: {a_level.total}")
    print(f"   People count: {len(a_level.people)}")
    print(f"   Recruitment rate (month 1): {a_level.recruitment_1:.1%}")
    print(f"   Churn rate (month 1): {a_level.churn_1:.1%}")
    
    # Show first few people for verification
    if a_level.people:
        print(f"   Sample people:")
        for i, person in enumerate(a_level.people[:3]):
            print(f"     {i+1}. {person.id[:8]}... - {person.role} {person.current_level}")
    
    # Run a single month simulation
    print(f"\n📊 RUNNING 1-MONTH SIMULATION:")
    
    # Run simulation for just January 2025
    results = engine.run_simulation(
        start_year=2025, start_month=1,
        end_year=2025, end_month=1
    )
    
    print(f"📊 AFTER SIMULATION:")
    print(f"   Stockholm A Level FTE: {a_level.total}")
    print(f"   People count: {len(a_level.people)}")
    
    # Check results data
    if '2025' in results.get('years', {}):
        year_data = results['years']['2025']
        if 'offices' in year_data and 'Stockholm' in year_data['offices']:
            stockholm_results = year_data['offices']['Stockholm']
            if 'levels' in stockholm_results and 'Consultant' in stockholm_results['levels']:
                consultant_results = stockholm_results['levels']['Consultant']
                if 'A' in consultant_results and len(consultant_results['A']) > 0:
                    a_result = consultant_results['A'][0]  # First month
                    print(f"   Results data:")
                    print(f"     Total: {a_result.get('total', 'N/A')}")
                    print(f"     Recruited: {a_result.get('recruited', 'N/A')}")
                    print(f"     Churned: {a_result.get('churned', 'N/A')}")
    
    # Show what happened to people
    if a_level.people:
        print(f"   Remaining people:")
        for i, person in enumerate(a_level.people[:3]):
            print(f"     {i+1}. {person.id[:8]}... - {person.role} {person.current_level}")
    
    print("\n🔍 DIAGNOSIS:")
    if a_level.total < 69:
        print(f"   ❌ FTE dropped from 69 to {a_level.total}")
        print(f"   ❌ This suggests massive churn with no recruitment")
        
        # Check if recruitment rate is actually being applied
        expected_recruitment = int(69 * a_level.recruitment_1)
        expected_churn = int(69 * a_level.churn_1)
        print(f"   Expected recruitment (6%): {expected_recruitment} people")
        print(f"   Expected churn: {expected_churn} people")
        print(f"   Expected net change: {expected_recruitment - expected_churn}")
        
        if a_level.total == 4:
            print(f"   🚨 CRITICAL: FTE = 4 suggests recruitment is NOT working!")
    else:
        print(f"   ✅ FTE maintained or grew")

if __name__ == "__main__":
    debug_recruitment()
