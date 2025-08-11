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

def test_recruitment_debug():
    print("=== Testing V2 Engine Recruitment Processing ===\n")
    
    # Load scenario  
    with open('data/scenarios/definitions/4346a731-90a1-4455-9c19-5994bfcd9b00.json', 'r') as f:
        scenario_data = json.load(f)
    
    print(f"Scenario: {scenario_data['name']}")
    print(f"Business Plan ID: {scenario_data.get('business_plan_id')}")
    
    # Load business plan
    business_plan_id = scenario_data.get('business_plan_id')
    if business_plan_id:
        with open(f'data/business_plans/{business_plan_id}.json', 'r') as f:
            business_plan = json.load(f)
        print(f"Business Plan Office: {business_plan['office_id']}")
        
        # Show recruitment targets
        print("\nBusiness Plan Recruitment Targets:")
        for entry in business_plan['entries']:
            if entry['recruitment'] > 0:
                print(f"  {entry['role']} {entry['level']}: recruitment={entry['recruitment']}, churn={entry['churn']}")
    
    # Create V2 engine
    engine = SimulationEngineV2()
    
    # Initialize
    print(f"\nInitializing V2 engine...")
    if not engine.initialize():
        print("ERROR: Failed to initialize V2 engine")
        return
    
    # Create scenario request
    scenario_request = ScenarioRequest(
        scenario_id=scenario_data['id'],
        name=scenario_data['name'],
        time_range=TimeRange(
            start_year=2025,
            start_month=1,
            end_year=2025, 
            end_month=12
        ),
        office_ids=['Oslo'],
        levers=Levers(),
        business_plan_id=business_plan_id
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
            print(f"Oslo results keys: {list(oslo_results.keys())}")
            
            # Check recruitment metrics
            if 'recruitment_by_role' in oslo_results:
                recruitment = oslo_results['recruitment_by_role']
                print(f"\nJanuary recruitment_by_role: {recruitment}")
            
            # Check workforce KPIs
            if 'workforce_kpis' in oslo_results:
                kpis = oslo_results['workforce_kpis']
                print(f"\nOslo Workforce KPIs (January):")
                for kpi_name, kpi_value in kpis.items():
                    print(f"  {kpi_name}: {kpi_value}")
            
            # Check events
            print(f"\nJanuary events: {len(jan_results.events)}")
            hired_events = [e for e in jan_results.events if e.event_type.value == 'hired']
            print(f"Hired events in January: {len(hired_events)}")
            for i, event in enumerate(hired_events):
                if i < 3:  # Show first 3
                    print(f"  HIRED {i+1}: {event.details}, simulation_month={event.simulation_month}")
            if len(hired_events) > 3:
                print(f"  ... and {len(hired_events) - 3} more hired events")
    
    print(f"\nTotal events across all months: {len(results.all_events)}")
    
    # Show events by type
    event_counts = {}
    for event in results.all_events:
        event_type = event.event_type.value
        event_counts[event_type] = event_counts.get(event_type, 0) + 1
    
    print(f"\nEvent Summary:")
    for event_type, count in event_counts.items():
        print(f"  {event_type}: {count}")

if __name__ == "__main__":
    test_recruitment_debug()