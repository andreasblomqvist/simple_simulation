#!/usr/bin/env python3
"""
Test script to demonstrate correct access to simulation results data structures.
This script shows how to properly navigate the nested structure and extract FTE data.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend/src')))

from services.simulation_engine import SimulationEngine
from services.config_service import ConfigService
from services.kpi.kpi_models import EconomicParameters

def test_data_structure_access():
    """Test accessing simulation results using the correct data structure."""
    
    print("=== Testing Data Structure Access ===\n")
    
    # Initialize services
    config_service = ConfigService()
    simulation_engine = SimulationEngine()
    
    # Set up economic parameters
    economic_params = EconomicParameters(
        unplanned_absence=0.05,
        other_expense=19000000.0,
        employment_cost_rate=0.40,
        working_hours_per_month=166.4
    )
    
    # Run simulation
    simulation_results = simulation_engine.run_simulation(
        start_year=2024,
        start_month=1,
        end_year=2024,
        end_month=12,
        price_increase=0.03,
        salary_increase=0.02,
        economic_params=economic_params
    )
    
    print("Top-level keys:", list(simulation_results.keys()))
    print()
    
    # Access data using the correct structure
    for year, year_data in simulation_results['years'].items():
        print(f"Year: {year}")
        
        for office_name, office_data in year_data['offices'].items():
            print(f"  Office: {office_name}")
            
            # Calculate total FTE for this office
            office_total_fte = 0
            
            for role_name, role_data in office_data['roles'].items():
                print(f"    Role: {role_name}")
                
                if isinstance(role_data, dict):
                    # Role with levels (e.g., Consultant, Sales, Recruitment)
                    role_total_fte = 0
                    for level_name, level_data in role_data.items():
                        if isinstance(level_data, list):
                            # Level data is a list of monthly data (like flat roles)
                            level_total_fte = sum(month_data['fte'] for month_data in level_data)
                            role_total_fte += level_total_fte
                            
                            print(f"      Level: {level_name}")
                            print(f"        FTE by month: {[month_data['fte'] for month_data in level_data]}")
                            print(f"        Total FTE: {level_total_fte}")
                            
                            # Show recruitment and churn for this level
                            if level_data:
                                first_month = level_data[0]
                                if 'recruitment' in first_month:
                                    total_recruitment = sum(month_data['recruitment'] for month_data in level_data)
                                    total_churn = sum(month_data['churn'] for month_data in level_data)
                                    print(f"        Total recruitment: {total_recruitment}")
                                    print(f"        Total churn: {total_churn}")
                        
                        elif isinstance(level_data, dict) and 'fte_by_month' in level_data:
                            # This is a proper level with FTE data (dict format)
                            fte_by_month = level_data['fte_by_month']
                            total_level_fte = sum(fte_by_month.values())
                            role_total_fte += total_level_fte
                            
                            print(f"      Level: {level_name}")
                            print(f"        FTE by month: {list(fte_by_month.values())}")
                            print(f"        Total FTE: {total_level_fte}")
                            
                            if 'recruitment_by_month' in level_data:
                                recruitment_total = sum(level_data['recruitment_by_month'].values())
                                print(f"        Total recruitment: {recruitment_total}")
                            
                            if 'churn_by_month' in level_data:
                                churn_total = sum(level_data['churn_by_month'].values())
                                print(f"        Total churn: {churn_total}")
                        
                        else:
                            print(f"      Level: {level_name} - Unknown data structure")
                            print(f"        Type: {type(level_data)}")
                            if isinstance(level_data, dict):
                                print(f"        Available keys: {list(level_data.keys())}")
                            elif isinstance(level_data, list):
                                print(f"        List length: {len(level_data)}")
                                if level_data:
                                    print(f"        First item keys: {list(level_data[0].keys()) if isinstance(level_data[0], dict) else 'Not a dict'}")
                    
                    print(f"      Role total FTE: {role_total_fte}")
                    office_total_fte += role_total_fte
                    
                elif isinstance(role_data, list):
                    # Flat role (e.g., Operations)
                    role_total_fte = sum(month_data['fte'] for month_data in role_data)
                    office_total_fte += role_total_fte
                    
                    print(f"      Flat role - FTE by month: {[month_data['fte'] for month_data in role_data]}")
                    print(f"      Role total FTE: {role_total_fte}")
                    
                    # Show recruitment and churn for flat roles
                    if role_data:
                        first_month = role_data[0]
                        if 'recruitment' in first_month:
                            total_recruitment = sum(month_data['recruitment'] for month_data in role_data)
                            total_churn = sum(month_data['churn'] for month_data in role_data)
                            print(f"      Total recruitment: {total_recruitment}")
                            print(f"      Total churn: {total_churn}")
                
                else:
                    print(f"      Unknown role data type: {type(role_data)}")
            
            print(f"  Office total FTE: {office_total_fte}")
            
            # Show financial data if available
            if 'financial' in office_data:
                financial = office_data['financial']
                print(f"  Financial summary:")
                print(f"    Total revenue: {financial.get('total_revenue', 0):,.0f} SEK")
                print(f"    Total cost: {financial.get('total_cost', 0):,.0f} SEK")
                print(f"    EBITDA: {financial.get('ebitda', 0):,.0f} SEK")
                print(f"    Total consultants: {financial.get('total_consultants', 0)}")
            
            print()

if __name__ == "__main__":
    test_data_structure_access() 