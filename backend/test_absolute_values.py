#!/usr/bin/env python3
"""
Test script to verify absolute recruitment values are properly applied.
This script creates a scenario with absolute recruitment values for Stockholm Consultant A
and runs the simulation to see the debug output.
"""

import sys
import os
sys.path.append('.')

from src.services.simulation_engine import SimulationEngine
from src.services.scenario_resolver import ScenarioResolver
from src.services.config_service import config_service
from src.services.office_builder import OfficeBuilder

def test_absolute_values():
    """Test that absolute recruitment values are properly applied."""
    print("=== Testing Absolute Recruitment Values ===")
    
    # Create scenario data with absolute recruitment values
    scenario_data = {
        'baseline_input': {
            'global': {
                'recruitment': {
                    'Consultant': {
                        'A': {
                            '202501': 5.0,  # 5 hires in January 2025
                            '202502': 3.0,  # 3 hires in February 2025
                            '202503': 4.0,  # 4 hires in March 2025
                            '202504': 2.0,  # 2 hires in April 2025
                            '202505': 6.0,  # 6 hires in May 2025
                            '202506': 3.0,  # 3 hires in June 2025
                            '202507': 4.0,  # 4 hires in July 2025
                            '202508': 2.0,  # 2 hires in August 2025
                            '202509': 5.0,  # 5 hires in September 2025
                            '202510': 3.0,  # 3 hires in October 2025
                            '202511': 4.0,  # 4 hires in November 2025
                            '202512': 2.0,  # 2 hires in December 2025
                        }
                    }
                },
                'churn': {
                    'Consultant': {
                        'A': {
                            '202501': 1.0,  # 1 churn in January 2025
                            '202502': 1.0,  # 1 churn in February 2025
                            '202503': 1.0,  # 1 churn in March 2025
                            '202504': 1.0,  # 1 churn in April 2025
                            '202505': 1.0,  # 1 churn in May 2025
                            '202506': 1.0,  # 1 churn in June 2025
                            '202507': 1.0,  # 1 churn in July 2025
                            '202508': 1.0,  # 1 churn in August 2025
                            '202509': 1.0,  # 1 churn in September 2025
                            '202510': 1.0,  # 1 churn in October 2025
                            '202511': 1.0,  # 1 churn in November 2025
                            '202512': 1.0,  # 1 churn in December 2025
                        }
                    }
                }
            }
        },
        'levers': {}
    }
    
    print("Scenario data created with absolute recruitment values for Stockholm Consultant A")
    print(f"Expected recruitment_abs_1: 5.0")
    print(f"Expected churn_abs_1: 1.0")
    print()
    
    # Resolve scenario
    print("=== Resolving Scenario ===")
    scenario_resolver = ScenarioResolver(config_service)
    resolved_data = scenario_resolver.resolve_scenario(scenario_data)
    
    print("Scenario resolved successfully")
    print()
    
    # Build offices
    print("=== Building Offices ===")
    office_builder = OfficeBuilder()
    offices = office_builder.build_offices_from_config(
        resolved_data['offices_config'], 
        resolved_data['progression_config']
    )
    
    print("Offices built successfully")
    print()
    
    # Check Stockholm Consultant A
    if 'Stockholm' in offices and 'Consultant' in offices['Stockholm'].roles:
        stockholm_consultant = offices['Stockholm'].roles['Consultant']
        if 'A' in stockholm_consultant:
            level_a = stockholm_consultant['A']
            print(f"Stockholm Consultant A FTE: {level_a.total}")
            print(f"Stockholm Consultant A recruitment_abs_1: {getattr(level_a, 'recruitment_abs_1', 'NOT FOUND')}")
            print(f"Stockholm Consultant A churn_abs_1: {getattr(level_a, 'churn_abs_1', 'NOT FOUND')}")
        else:
            print("Stockholm Consultant A level not found")
    else:
        print("Stockholm or Consultant role not found")
    
    print()
    
    # Run simulation
    print("=== Running Simulation ===")
    engine = SimulationEngine()
    results = engine.run_simulation_with_offices(
        start_year=2025,
        start_month=1,
        end_year=2025,
        end_month=1,  # Just run January to see the debug output
        offices=offices,
        progression_config=resolved_data['progression_config'],
        cat_curves=resolved_data['cat_curves']
    )
    
    print("Simulation completed")
    print()
    
    # Check results
    if 'years' in results and '2025' in results['years']:
        year_data = results['years']['2025']
        if 'offices' in year_data and 'Stockholm' in year_data['offices']:
            stockholm_data = year_data['offices']['Stockholm']
            if 'levels' in stockholm_data and 'Consultant' in stockholm_data['levels']:
                consultant_data = stockholm_data['levels']['Consultant']
                if 'A' in consultant_data:
                    level_a_data = consultant_data['A']
                    print(f"Final Stockholm Consultant A FTE (raw): {level_a_data} (type: {type(level_a_data)})")
                else:
                    print("Stockholm Consultant A data not found in results")
            else:
                print("Stockholm Consultant levels not found in results")
        else:
            print("Stockholm office data not found in results")
    else:
        print("2025 year data not found in results")

    # --- Print KPIs for 2025 ---
    print("\n=== KPIs for 2025 ===")
    from src.services.kpi.kpi_service import KPIService
    kpi_service = KPIService()
    kpis = kpi_service.calculate_kpis_for_year(results, target_year='2025', simulation_duration_months=12)
    print("Financial KPIs:")
    print(f"  Net Sales: {kpis.financial.net_sales}")
    print(f"  Net Sales (Baseline): {kpis.financial.net_sales_baseline}")
    print(f"  Total Salary Costs: {kpis.financial.total_salary_costs}")
    print(f"  Total Salary Costs (Baseline): {kpis.financial.total_salary_costs_baseline}")
    print(f"  EBITDA: {kpis.financial.ebitda}")
    print(f"  EBITDA (Baseline): {kpis.financial.ebitda_baseline}")
    print(f"  Margin: {kpis.financial.margin}")
    print(f"  Margin (Baseline): {kpis.financial.margin_baseline}")
    print(f"  Total Consultants: {kpis.financial.total_consultants}")
    print(f"  Total Consultants (Baseline): {kpis.financial.total_consultants_baseline}")
    print(f"  Avg Hourly Rate: {kpis.financial.avg_hourly_rate}")
    print(f"  Avg Hourly Rate (Baseline): {kpis.financial.avg_hourly_rate_baseline}")

if __name__ == "__main__":
    test_absolute_values() 