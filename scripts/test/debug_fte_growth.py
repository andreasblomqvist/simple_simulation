#!/usr/bin/env python3
"""
Debug script to print FTE by office, role, and level for each month, and show recruitment, churn, and progression events.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend/src')))

from services.simulation_engine import SimulationEngine
from services.config_service import ConfigService
from services.kpi.kpi_models import EconomicParameters

# Set up economic parameters (match your main simulation)
economic_params = EconomicParameters(
    unplanned_absence=0.05,
    other_expense=19000000.0,
    employment_cost_rate=0.40,
    working_hours_per_month=166.4
)

# Initialize services
config_service = ConfigService()
simulation_engine = SimulationEngine()

# Run a simulation for one year (adjust as needed)
simulation_results = simulation_engine.run_simulation(
    start_year=2024,
    start_month=1,
    end_year=2024,
    end_month=12,
    price_increase=0.03,
    salary_increase=0.02,
    economic_params=economic_params
)

print("Top-level keys in simulation_results:", simulation_results.keys())

def print_fte_breakdown(sim_results):
    print("\n=== FTE Breakdown by Year, Office, Role, Level, and Month ===\n")
    for year, year_data in sim_results['years'].items():
        print(f"Year: {year}")
        for office_name, office_data in year_data['offices'].items():
            print(f"  Office: {office_name}")
            for role_name, role_data in office_data['roles'].items():
                print(f"    Role: {role_name}")
                if isinstance(role_data, list):
                    print(f"      role_data is a list with length {len(role_data)}. Contents:")
                    for idx, item in enumerate(role_data):
                        print(f"        [{idx}]: {item}")
                elif isinstance(role_data, dict):
                    print(f"      role_data keys: {list(role_data.keys())}")
                    if all(isinstance(v, dict) and ('fte_by_month' in v or 'recruitment_by_month' in v) for v in role_data.values()):
                        for level_name, level_data in role_data.items():
                            print(f"      Level: {level_name}")
                            print(f"        level_data keys: {list(level_data.keys())}")
                            fte_by_month = [level_data.get('fte_by_month', {}).get(str(m), 0) for m in range(1, 13)]
                            print(f"        FTE by month: {fte_by_month}")
                            if 'recruitment_by_month' in level_data:
                                print(f"        Recruitment: {[level_data['recruitment_by_month'].get(str(m), 0) for m in range(1, 13)]}")
                            if 'churn_by_month' in level_data:
                                print(f"        Churn: {[level_data['churn_by_month'].get(str(m), 0) for m in range(1, 13)]}")
                            if 'progression_by_month' in level_data:
                                print(f"        Progression: {[level_data['progression_by_month'].get(str(m), 0) for m in range(1, 13)]}")
                    else:
                        fte_by_month = [role_data.get('fte_by_month', {}).get(str(m), 0) for m in range(1, 13)]
                        print(f"      FTE by month: {fte_by_month}")
                        if 'recruitment_by_month' in role_data:
                            print(f"      Recruitment: {[role_data['recruitment_by_month'].get(str(m), 0) for m in range(1, 13)]}")
                        if 'churn_by_month' in role_data:
                            print(f"      Churn: {[role_data['churn_by_month'].get(str(m), 0) for m in range(1, 13)]}")
                        if 'progression_by_month' in role_data:
                            print(f"      Progression: {[role_data['progression_by_month'].get(str(m), 0) for m in range(1, 13)]}")
            print()

print_fte_breakdown(simulation_results) 