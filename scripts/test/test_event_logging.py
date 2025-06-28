#!/usr/bin/env python3
"""
Test script to run simulation with comprehensive event logging.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from backend.src.services.simulation.office_manager import OfficeManager
from backend.src.services.simulation.workforce import WorkforceManager
from backend.src.services.config_service import ConfigService
from backend.src.services.simulation.models import Month
from collections import defaultdict, Counter
import pandas as pd
from backend.config.progression_config import PROGRESSION_CONFIG

def run_simulation_with_event_logging():
    """Run a simulation with comprehensive event logging"""
    
    print("=== SIMULATION WITH EVENT LOGGING ===")
    
    # Initialize services
    config_service = ConfigService()
    office_manager = OfficeManager(config_service)
    workforce_manager = WorkforceManager({})
    
    # Set run ID to initialize event logger
    workforce_manager.set_run_id()
    
    # Initialize offices with realistic people
    offices = office_manager.initialize_offices_from_config()
    workforce_manager.offices = offices
    
    print(f"Initialized {len(offices)} offices with realistic population")
    
    # Track simulation results
    monthly_metrics = {}
    
    # Run simulation for 1 year (12 months)
    start_year = 2025
    start_month = 1
    
    print(f"\nRunning simulation from {start_year}-{start_month:02d} for 12 months...")
    
    # Run simulation month by month
    for month in range(1, 13):
        current_date_str = f"{start_year}-{month:02d}"
        print(f"Processing month: {current_date_str}")
        
        # Process the month
        workforce_manager.process_month(start_year, month, current_date_str, monthly_metrics)
        
        # Print summary for this month
        total_fte = sum(office.total_fte for office in offices.values())
        print(f"  Total FTE: {total_fte}")
    
    # Get event logger and analyze results
    event_logger = workforce_manager.get_event_logger()
    
    if event_logger:
        print("\n=== EVENT LOGGING RESULTS ===")
        
        # Get events summary
        summary = event_logger.get_events_summary()
        
        print(f"Total events logged: {summary['total_events']}")
        
        print("\nEvents by type:")
        for event_type, count in summary['events_by_type'].items():
            print(f"  {event_type}: {count}")
        
        print("\nEvents by office:")
        for office, count in summary['events_by_office'].items():
            print(f"  {office}: {count}")
        
        print("\nEvents by role:")
        for role, count in summary['events_by_role'].items():
            print(f"  {role}: {count}")
        
        print("\nEvents by level:")
        for level, count in summary['events_by_level'].items():
            print(f"  {level}: {count}")
        
        print("\nEvents by month:")
        for month, count in summary['events_by_month'].items():
            print(f"  {month}: {count}")
        
        # Export events summary
        summary_file = event_logger.export_events_summary()
        print(f"\nEvents summary exported to: {summary_file}")
        
        # Show some sample events
        print("\n=== SAMPLE EVENTS ===")
        events = event_logger.events[:10]  # First 10 events
        for event in events:
            print(f"Event {event.event_id}: {event.event_type.value} - {event.person_id[:8]}... - {event.date} - {event.role} {event.level} at {event.office}")
            print(f"  Total tenure: {event.total_tenure_months} months, Time on level: {event.time_on_level_months} months")
            if event.event_type.value == 'promotion':
                print(f"  Promoted from {event.from_level} to {event.to_level} (CAT: {event.cat_category}, Prob: {event.progression_probability:.3f})")
            elif event.event_type.value == 'churn':
                print(f"  Churn rate: {event.churn_rate:.3f}")
            elif event.event_type.value == 'recruitment':
                print(f"  Recruitment rate: {event.recruitment_rate}")
            print()
        
        # Show final population
        print("=== FINAL POPULATION ===")
        for office_name, office in offices.items():
            print(f"\n{office_name}:")
            for role_name, role_data in office.roles.items():
                if isinstance(role_data, dict):  # Leveled roles
                    for level_name, level in role_data.items():
                        print(f"  {role_name} {level_name}: {level.total} FTEs")
                else:  # Flat roles
                    print(f"  {role_name}: {role_data.total} FTEs")
    
    else:
        print("No event logger available!")

if __name__ == "__main__":
    run_simulation_with_event_logging() 