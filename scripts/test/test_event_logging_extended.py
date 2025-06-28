#!/usr/bin/env python3
"""
Test script to run a 3-year simulation with smaller, diverse population.
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

def create_small_diverse_population():
    """Create a smaller configuration with diverse seniority levels"""
    
    # Create a minimal config with just Stockholm office
    config = {
        "Stockholm": {
            "name": "Stockholm",
            "total_fte": 100,  # Smaller total
            "journey": "Mature Office",
            "roles": {
                "Consultant": {
                    "A": {
                        "fte": 20,  # 20 A-level consultants
                        "price_1": 1200.0, "salary_1": 45000.0, "recruitment_1": 0.02, "churn_1": 0.03, "utr_1": 0.85, "progression_1": 0.0,
                        "price_2": 1200.0, "salary_2": 45000.0, "recruitment_2": 0.02, "churn_2": 0.03, "utr_2": 0.85, "progression_2": 0.0,
                        "price_3": 1200.0, "salary_3": 45000.0, "recruitment_3": 0.02, "churn_3": 0.03, "utr_3": 0.85, "progression_3": 0.0,
                        "price_4": 1200.0, "salary_4": 45000.0, "recruitment_4": 0.02, "churn_4": 0.03, "utr_4": 0.85, "progression_4": 0.0,
                        "price_5": 1200.0, "salary_5": 45000.0, "recruitment_5": 0.02, "churn_5": 0.03, "utr_5": 0.85, "progression_5": 0.0,
                        "price_6": 1200.0, "salary_6": 45000.0, "recruitment_6": 0.02, "churn_6": 0.03, "utr_6": 0.85, "progression_6": 0.0,
                        "price_7": 1200.0, "salary_7": 45000.0, "recruitment_7": 0.02, "churn_7": 0.03, "utr_7": 0.85, "progression_7": 0.0,
                        "price_8": 1200.0, "salary_8": 45000.0, "recruitment_8": 0.02, "churn_8": 0.03, "utr_8": 0.85, "progression_8": 0.0,
                        "price_9": 1200.0, "salary_9": 45000.0, "recruitment_9": 0.02, "churn_9": 0.03, "utr_9": 0.85, "progression_9": 0.0,
                        "price_10": 1200.0, "salary_10": 45000.0, "recruitment_10": 0.02, "churn_10": 0.03, "utr_10": 0.85, "progression_10": 0.0,
                        "price_11": 1200.0, "salary_11": 45000.0, "recruitment_11": 0.02, "churn_11": 0.03, "utr_11": 0.85, "progression_11": 0.0,
                        "price_12": 1200.0, "salary_12": 45000.0, "recruitment_12": 0.02, "churn_12": 0.03, "utr_12": 0.85, "progression_12": 0.0,
                    },
                    "AC": {
                        "fte": 15,  # 15 AC-level consultants
                        "price_1": 1300.0, "salary_1": 55000.0, "recruitment_1": 0.015, "churn_1": 0.025, "utr_1": 0.87, "progression_1": 0.0,
                        "price_2": 1300.0, "salary_2": 55000.0, "recruitment_2": 0.015, "churn_2": 0.025, "utr_2": 0.87, "progression_2": 0.0,
                        "price_3": 1300.0, "salary_3": 55000.0, "recruitment_3": 0.015, "churn_3": 0.025, "utr_3": 0.87, "progression_3": 0.0,
                        "price_4": 1300.0, "salary_4": 55000.0, "recruitment_4": 0.015, "churn_4": 0.025, "utr_4": 0.87, "progression_4": 0.0,
                        "price_5": 1300.0, "salary_5": 55000.0, "recruitment_5": 0.015, "churn_5": 0.025, "utr_5": 0.87, "progression_5": 0.0,
                        "price_6": 1300.0, "salary_6": 55000.0, "recruitment_6": 0.015, "churn_6": 0.025, "utr_6": 0.87, "progression_6": 0.0,
                        "price_7": 1300.0, "salary_7": 55000.0, "recruitment_7": 0.015, "churn_7": 0.025, "utr_7": 0.87, "progression_7": 0.0,
                        "price_8": 1300.0, "salary_8": 55000.0, "recruitment_8": 0.015, "churn_8": 0.025, "utr_8": 0.87, "progression_8": 0.0,
                        "price_9": 1300.0, "salary_9": 55000.0, "recruitment_9": 0.015, "churn_9": 0.025, "utr_9": 0.87, "progression_9": 0.0,
                        "price_10": 1300.0, "salary_10": 55000.0, "recruitment_10": 0.015, "churn_10": 0.025, "utr_10": 0.87, "progression_10": 0.0,
                        "price_11": 1300.0, "salary_11": 55000.0, "recruitment_11": 0.015, "churn_11": 0.025, "utr_11": 0.87, "progression_11": 0.0,
                        "price_12": 1300.0, "salary_12": 55000.0, "recruitment_12": 0.015, "churn_12": 0.025, "utr_12": 0.87, "progression_12": 0.0,
                    },
                    "C": {
                        "fte": 12,  # 12 C-level consultants
                        "price_1": 1500.0, "salary_1": 75000.0, "recruitment_1": 0.01, "churn_1": 0.02, "utr_1": 0.89, "progression_1": 0.0,
                        "price_2": 1500.0, "salary_2": 75000.0, "recruitment_2": 0.01, "churn_2": 0.02, "utr_2": 0.89, "progression_2": 0.0,
                        "price_3": 1500.0, "salary_3": 75000.0, "recruitment_3": 0.01, "churn_3": 0.02, "utr_3": 0.89, "progression_3": 0.0,
                        "price_4": 1500.0, "salary_4": 75000.0, "recruitment_4": 0.01, "churn_4": 0.02, "utr_4": 0.89, "progression_4": 0.0,
                        "price_5": 1500.0, "salary_5": 75000.0, "recruitment_5": 0.01, "churn_5": 0.02, "utr_5": 0.89, "progression_5": 0.0,
                        "price_6": 1500.0, "salary_6": 75000.0, "recruitment_6": 0.01, "churn_6": 0.02, "utr_6": 0.89, "progression_6": 0.0,
                        "price_7": 1500.0, "salary_7": 75000.0, "recruitment_7": 0.01, "churn_7": 0.02, "utr_7": 0.89, "progression_7": 0.0,
                        "price_8": 1500.0, "salary_8": 75000.0, "recruitment_8": 0.01, "churn_8": 0.02, "utr_8": 0.89, "progression_8": 0.0,
                        "price_9": 1500.0, "salary_9": 75000.0, "recruitment_9": 0.01, "churn_9": 0.02, "utr_9": 0.89, "progression_9": 0.0,
                        "price_10": 1500.0, "salary_10": 75000.0, "recruitment_10": 0.01, "churn_10": 0.02, "utr_10": 0.89, "progression_10": 0.0,
                        "price_11": 1500.0, "salary_11": 75000.0, "recruitment_11": 0.01, "churn_11": 0.02, "utr_11": 0.89, "progression_11": 0.0,
                        "price_12": 1500.0, "salary_12": 75000.0, "recruitment_12": 0.01, "churn_12": 0.02, "utr_12": 0.89, "progression_12": 0.0,
                    },
                    "SrC": {
                        "fte": 10,  # 10 SrC-level consultants
                        "price_1": 1800.0, "salary_1": 95000.0, "recruitment_1": 0.008, "churn_1": 0.015, "utr_1": 0.91, "progression_1": 0.0,
                        "price_2": 1800.0, "salary_2": 95000.0, "recruitment_2": 0.008, "churn_2": 0.015, "utr_2": 0.91, "progression_2": 0.0,
                        "price_3": 1800.0, "salary_3": 95000.0, "recruitment_3": 0.008, "churn_3": 0.015, "utr_3": 0.91, "progression_3": 0.0,
                        "price_4": 1800.0, "salary_4": 95000.0, "recruitment_4": 0.008, "churn_4": 0.015, "utr_4": 0.91, "progression_4": 0.0,
                        "price_5": 1800.0, "salary_5": 95000.0, "recruitment_5": 0.008, "churn_5": 0.015, "utr_5": 0.91, "progression_5": 0.0,
                        "price_6": 1800.0, "salary_6": 95000.0, "recruitment_6": 0.008, "churn_6": 0.015, "utr_6": 0.91, "progression_6": 0.0,
                        "price_7": 1800.0, "salary_7": 95000.0, "recruitment_7": 0.008, "churn_7": 0.015, "utr_7": 0.91, "progression_7": 0.0,
                        "price_8": 1800.0, "salary_8": 95000.0, "recruitment_8": 0.008, "churn_8": 0.015, "utr_8": 0.91, "progression_8": 0.0,
                        "price_9": 1800.0, "salary_9": 95000.0, "recruitment_9": 0.008, "churn_9": 0.015, "utr_9": 0.91, "progression_9": 0.0,
                        "price_10": 1800.0, "salary_10": 95000.0, "recruitment_10": 0.008, "churn_10": 0.015, "utr_10": 0.91, "progression_10": 0.0,
                        "price_11": 1800.0, "salary_11": 95000.0, "recruitment_11": 0.008, "churn_11": 0.015, "utr_11": 0.91, "progression_11": 0.0,
                        "price_12": 1800.0, "salary_12": 95000.0, "recruitment_12": 0.008, "churn_12": 0.015, "utr_12": 0.91, "progression_12": 0.0,
                    },
                    "AM": {
                        "fte": 8,  # 8 AM-level consultants
                        "price_1": 2200.0, "salary_1": 120000.0, "recruitment_1": 0.005, "churn_1": 0.01, "utr_1": 0.93, "progression_1": 0.0,
                        "price_2": 2200.0, "salary_2": 120000.0, "recruitment_2": 0.005, "churn_2": 0.01, "utr_2": 0.93, "progression_2": 0.0,
                        "price_3": 2200.0, "salary_3": 120000.0, "recruitment_3": 0.005, "churn_3": 0.01, "utr_3": 0.93, "progression_3": 0.0,
                        "price_4": 2200.0, "salary_4": 120000.0, "recruitment_4": 0.005, "churn_4": 0.01, "utr_4": 0.93, "progression_4": 0.0,
                        "price_5": 2200.0, "salary_5": 120000.0, "recruitment_5": 0.005, "churn_5": 0.01, "utr_5": 0.93, "progression_5": 0.0,
                        "price_6": 2200.0, "salary_6": 120000.0, "recruitment_6": 0.005, "churn_6": 0.01, "utr_6": 0.93, "progression_6": 0.0,
                        "price_7": 2200.0, "salary_7": 120000.0, "recruitment_7": 0.005, "churn_7": 0.01, "utr_7": 0.93, "progression_7": 0.0,
                        "price_8": 2200.0, "salary_8": 120000.0, "recruitment_8": 0.005, "churn_8": 0.01, "utr_8": 0.93, "progression_8": 0.0,
                        "price_9": 2200.0, "salary_9": 120000.0, "recruitment_9": 0.005, "churn_9": 0.01, "utr_9": 0.93, "progression_9": 0.0,
                        "price_10": 2200.0, "salary_10": 120000.0, "recruitment_10": 0.005, "churn_10": 0.01, "utr_10": 0.93, "progression_10": 0.0,
                        "price_11": 2200.0, "salary_11": 120000.0, "recruitment_11": 0.005, "churn_11": 0.01, "utr_11": 0.93, "progression_11": 0.0,
                        "price_12": 2200.0, "salary_12": 120000.0, "recruitment_12": 0.005, "churn_12": 0.01, "utr_12": 0.93, "progression_12": 0.0,
                    },
                    "M": {
                        "fte": 6,  # 6 M-level consultants
                        "price_1": 2800.0, "salary_1": 150000.0, "recruitment_1": 0.003, "churn_1": 0.008, "utr_1": 0.95, "progression_1": 0.0,
                        "price_2": 2800.0, "salary_2": 150000.0, "recruitment_2": 0.003, "churn_2": 0.008, "utr_2": 0.95, "progression_2": 0.0,
                        "price_3": 2800.0, "salary_3": 150000.0, "recruitment_3": 0.003, "churn_3": 0.008, "utr_3": 0.95, "progression_3": 0.0,
                        "price_4": 2800.0, "salary_4": 150000.0, "recruitment_4": 0.003, "churn_4": 0.008, "utr_4": 0.95, "progression_4": 0.0,
                        "price_5": 2800.0, "salary_5": 150000.0, "recruitment_5": 0.003, "churn_5": 0.008, "utr_5": 0.95, "progression_5": 0.0,
                        "price_6": 2800.0, "salary_6": 150000.0, "recruitment_6": 0.003, "churn_6": 0.008, "utr_6": 0.95, "progression_6": 0.0,
                        "price_7": 2800.0, "salary_7": 150000.0, "recruitment_7": 0.003, "churn_7": 0.008, "utr_7": 0.95, "progression_7": 0.0,
                        "price_8": 2800.0, "salary_8": 150000.0, "recruitment_8": 0.003, "churn_8": 0.008, "utr_8": 0.95, "progression_8": 0.0,
                        "price_9": 2800.0, "salary_9": 150000.0, "recruitment_9": 0.003, "churn_9": 0.008, "utr_9": 0.95, "progression_9": 0.0,
                        "price_10": 2800.0, "salary_10": 150000.0, "recruitment_10": 0.003, "churn_10": 0.008, "utr_10": 0.95, "progression_10": 0.0,
                        "price_11": 2800.0, "salary_11": 150000.0, "recruitment_11": 0.003, "churn_11": 0.008, "utr_11": 0.95, "progression_11": 0.0,
                        "price_12": 2800.0, "salary_12": 150000.0, "recruitment_12": 0.003, "churn_12": 0.008, "utr_12": 0.95, "progression_12": 0.0,
                    },
                    "SrM": {
                        "fte": 4,  # 4 SrM-level consultants
                        "price_1": 3500.0, "salary_1": 200000.0, "recruitment_1": 0.002, "churn_1": 0.005, "utr_1": 0.97, "progression_1": 0.0,
                        "price_2": 3500.0, "salary_2": 200000.0, "recruitment_2": 0.002, "churn_2": 0.005, "utr_2": 0.97, "progression_2": 0.0,
                        "price_3": 3500.0, "salary_3": 200000.0, "recruitment_3": 0.002, "churn_3": 0.005, "utr_3": 0.97, "progression_3": 0.0,
                        "price_4": 3500.0, "salary_4": 200000.0, "recruitment_4": 0.002, "churn_4": 0.005, "utr_4": 0.97, "progression_4": 0.0,
                        "price_5": 3500.0, "salary_5": 200000.0, "recruitment_5": 0.002, "churn_5": 0.005, "utr_5": 0.97, "progression_5": 0.0,
                        "price_6": 3500.0, "salary_6": 200000.0, "recruitment_6": 0.002, "churn_6": 0.005, "utr_6": 0.97, "progression_6": 0.0,
                        "price_7": 3500.0, "salary_7": 200000.0, "recruitment_7": 0.002, "churn_7": 0.005, "utr_7": 0.97, "progression_7": 0.0,
                        "price_8": 3500.0, "salary_8": 200000.0, "recruitment_8": 0.002, "churn_8": 0.005, "utr_8": 0.97, "progression_8": 0.0,
                        "price_9": 3500.0, "salary_9": 200000.0, "recruitment_9": 0.002, "churn_9": 0.005, "utr_9": 0.97, "progression_9": 0.0,
                        "price_10": 3500.0, "salary_10": 200000.0, "recruitment_10": 0.002, "churn_10": 0.005, "utr_10": 0.97, "progression_10": 0.0,
                        "price_11": 3500.0, "salary_11": 200000.0, "recruitment_11": 0.002, "churn_11": 0.005, "utr_11": 0.97, "progression_11": 0.0,
                        "price_12": 3500.0, "salary_12": 200000.0, "recruitment_12": 0.002, "churn_12": 0.005, "utr_12": 0.97, "progression_12": 0.0,
                    },
                    "PiP": {
                        "fte": 2,  # 2 PiP-level consultants
                        "price_1": 4500.0, "salary_1": 250000.0, "recruitment_1": 0.001, "churn_1": 0.003, "utr_1": 0.98, "progression_1": 0.0,
                        "price_2": 4500.0, "salary_2": 250000.0, "recruitment_2": 0.001, "churn_2": 0.003, "utr_2": 0.98, "progression_2": 0.0,
                        "price_3": 4500.0, "salary_3": 250000.0, "recruitment_3": 0.001, "churn_3": 0.003, "utr_3": 0.98, "progression_3": 0.0,
                        "price_4": 4500.0, "salary_4": 250000.0, "recruitment_4": 0.001, "churn_4": 0.003, "utr_4": 0.98, "progression_4": 0.0,
                        "price_5": 4500.0, "salary_5": 250000.0, "recruitment_5": 0.001, "churn_5": 0.003, "utr_5": 0.98, "progression_5": 0.0,
                        "price_6": 4500.0, "salary_6": 250000.0, "recruitment_6": 0.001, "churn_6": 0.003, "utr_6": 0.98, "progression_6": 0.0,
                        "price_7": 4500.0, "salary_7": 250000.0, "recruitment_7": 0.001, "churn_7": 0.003, "utr_7": 0.98, "progression_7": 0.0,
                        "price_8": 4500.0, "salary_8": 250000.0, "recruitment_8": 0.001, "churn_8": 0.003, "utr_8": 0.98, "progression_8": 0.0,
                        "price_9": 4500.0, "salary_9": 250000.0, "recruitment_9": 0.001, "churn_9": 0.003, "utr_9": 0.98, "progression_9": 0.0,
                        "price_10": 4500.0, "salary_10": 250000.0, "recruitment_10": 0.001, "churn_10": 0.003, "utr_10": 0.98, "progression_10": 0.0,
                        "price_11": 4500.0, "salary_11": 250000.0, "recruitment_11": 0.001, "churn_11": 0.003, "utr_11": 0.98, "progression_11": 0.0,
                        "price_12": 4500.0, "salary_12": 250000.0, "recruitment_12": 0.001, "churn_12": 0.003, "utr_12": 0.98, "progression_12": 0.0,
                    }
                },
                "Operations": {
                    "fte": 23,  # 23 operations staff
                    "price": 0.0, "salary": 40000.0, "recruitment": 0.02, "churn": 0.02, "utr": 0.85, "progression": 0.0
                }
            }
        }
    }
    
    return config

def run_extended_simulation():
    """Run a 3-year simulation with diverse population"""
    
    print("=== 3-YEAR SIMULATION WITH DIVERSE POPULATION ===")
    
    # Create custom config with diverse population
    custom_config = create_small_diverse_population()
    
    # Initialize services with custom config
    config_service = ConfigService()
    # Temporarily replace the config with our custom one
    config_service._config = custom_config
    
    office_manager = OfficeManager(config_service)
    workforce_manager = WorkforceManager({})
    
    # Set run ID to initialize event logger
    workforce_manager.set_run_id()
    
    # Initialize offices with realistic people
    offices = office_manager.initialize_offices_from_config()
    workforce_manager.offices = offices
    
    print(f"Initialized {len(offices)} offices with diverse population")
    print("Population distribution:")
    for office_name, office in offices.items():
        print(f"\n{office_name}:")
        for role_name, role_data in office.roles.items():
            if isinstance(role_data, dict):  # Leveled roles
                for level_name, level in role_data.items():
                    print(f"  {role_name} {level_name}: {level.total} FTEs")
            else:  # Flat roles
                print(f"  {role_name}: {role_data.total} FTEs")
    
    # Track simulation results
    monthly_metrics = {}
    
    # Run simulation for 3 years (36 months)
    start_year = 2025
    start_month = 1
    
    print(f"\nRunning simulation from {start_year}-{start_month:02d} for 36 months...")
    
    # Run simulation month by month
    for year in range(start_year, start_year + 3):
        for month in range(1, 13):
            current_date_str = f"{year}-{month:02d}"
            print(f"Processing month: {current_date_str}")
            
            # Process the month
            workforce_manager.process_month(year, month, current_date_str, monthly_metrics)
            
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
        events = event_logger.events[:15]  # First 15 events
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
    run_extended_simulation() 