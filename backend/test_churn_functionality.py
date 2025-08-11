#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from src.services.simulation_engine_v2 import (
    SimulationEngineV2, ScenarioRequest, TimeRange, Levers
)
import json
import logging

# Setup detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

def test_churn_functionality():
    print("=== Testing V2 Engine Churn Functionality ===\n")
    
    # Load business plan with churn
    with open('data/business_plans/oslo_with_churn_test.json', 'r') as f:
        business_plan = json.load(f)
    
    print(f"Business Plan: {business_plan['office_id']}")
    
    # Show churn targets from business plan
    print("\nBusiness Plan Churn & Recruitment Targets:")
    total_monthly_recruitment = 0
    total_monthly_churn = 0
    
    for entry in business_plan['entries']:
        if entry['recruitment'] > 0 or entry['churn'] > 0:
            print(f"  {entry['role']} {entry['level']}: recruitment={entry['recruitment']}, churn={entry['churn']}")
            total_monthly_recruitment += entry['recruitment']
            total_monthly_churn += entry['churn']
    
    print(f"\nExpected Monthly Totals:")
    print(f"  Recruitment: {total_monthly_recruitment}")
    print(f"  Churn: {total_monthly_churn}")
    print(f"  Net Growth: {total_monthly_recruitment - total_monthly_churn}")
    
    print(f"\nExpected Yearly Totals:")
    print(f"  Recruitment: {total_monthly_recruitment * 12}")
    print(f"  Churn: {total_monthly_churn * 12}")
    print(f"  Net Growth: {(total_monthly_recruitment - total_monthly_churn) * 12}")
    
    # Create V2 engine
    engine = SimulationEngineV2()
    
    # Initialize
    print(f"\nInitializing V2 engine...")
    if not engine.initialize():
        print("ERROR: Failed to initialize V2 engine")
        return
    
    # Create scenario request
    scenario_request = ScenarioRequest(
        scenario_id="oslo_churn_test_scenario",
        name="Oslo Churn Test",
        time_range=TimeRange(
            start_year=2025,
            start_month=1,
            end_year=2025, 
            end_month=12
        ),
        office_ids=['Oslo'],
        levers=Levers(),
        business_plan_id="oslo_with_churn_test"
    )
    
    print(f"\nRunning simulation...")
    
    # Run simulation
    results = engine.run_simulation(scenario_request)
    
    print(f"\nResults received")
    print(f"Monthly results keys: {list(results.monthly_results.keys())}")
    
    # Check January 2025 results
    january_key = "2025-01"
    if january_key in results.monthly_results:
        jan_results = results.monthly_results[january_key]
        print(f"\nJanuary 2025 office results keys: {list(jan_results.office_results.keys())}")
        
        if 'Oslo' in jan_results.office_results:
            oslo_results = jan_results.office_results['Oslo']
            
            # Check recruitment metrics
            if 'recruitment_by_role' in oslo_results:
                recruitment = oslo_results['recruitment_by_role']
                print(f"\nJanuary recruitment_by_role: {recruitment}")
                
            # Check churn metrics  
            if 'churn_by_role' in oslo_results:
                churn = oslo_results['churn_by_role']
                print(f"January churn_by_role: {churn}")
            
            # Check events
            print(f"\nJanuary events: {len(jan_results.events)}")
            hired_events = [e for e in jan_results.events if e.event_type.value == 'hired']
            churned_events = [e for e in jan_results.events if e.event_type.value == 'churned']
            promoted_events = [e for e in jan_results.events if e.event_type.value == 'promoted']
            
            print(f"  Hired events: {len(hired_events)}")
            print(f"  Churned events: {len(churned_events)}")
            print(f"  Promoted events: {len(promoted_events)}")
            
            # Show some examples
            if hired_events:
                print(f"\nExample hired events:")
                for i, event in enumerate(hired_events[:3]):
                    print(f"  {i+1}: {event.details}")
                    
            if churned_events:
                print(f"\nExample churned events:")
                for i, event in enumerate(churned_events[:3]):
                    print(f"  {i+1}: {event.details}")
    
    print(f"\nTotal events across all months: {len(results.all_events)}")
    
    # Show events by type
    event_counts = {}
    for event in results.all_events:
        event_type = event.event_type.value
        event_counts[event_type] = event_counts.get(event_type, 0) + 1
    
    print(f"\nYearly Event Summary:")
    for event_type, count in event_counts.items():
        print(f"  {event_type}: {count}")
        
    print(f"\nActual vs Expected:")
    hired_actual = event_counts.get('hired', 0)
    churned_actual = event_counts.get('churned', 0)
    
    print(f"  Hired - Expected: ~{total_monthly_recruitment * 12}, Actual: {hired_actual}")
    print(f"  Churned - Expected: ~{total_monthly_churn * 12}, Actual: {churned_actual}")

if __name__ == "__main__":
    test_churn_functionality()