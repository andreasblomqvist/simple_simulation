#!/usr/bin/env python3
"""
Test script to verify that the simulation is actually growing FTE.
"""

import json
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from src.services.office_builder import OfficeBuilder
from src.services.simulation_engine import SimulationEngine

def test_simulation_growth():
    """Test that the simulation actually grows FTE over time."""
    
    # Load the configuration
    config_path = backend_dir / "config" / "office_configuration.json"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Create office builder and simulation engine
    builder = OfficeBuilder()
    engine = SimulationEngine()
    
    # Build offices
    offices = builder.build_offices_from_config(config, {})
    engine.offices = offices
    
    print("Testing simulation growth...")
    print(f"Initial total FTE: {sum(office.total_fte for office in offices.values())}")
    
    # Test a few months to see if FTE grows
    for month in range(1, 4):  # Test first 3 months
        current_date = f"2025-{month:02d}"
        print(f"\n=== Month {month} ({current_date}) ===")
        
        # Process each office
        for office_name, office in offices.items():
            print(f"Office: {office_name}")
            office_recruitment = 0
            office_churn = 0
            
            for role_name, role_data in office.roles.items():
                if isinstance(role_data, dict):  # Leveled role
                    for level_name, level in role_data.items():
                        # Get recruitment and churn rates
                        recruitment_rate = getattr(level, f'recruitment_{month}', 0.0)
                        churn_rate = getattr(level, f'churn_{month}', 0.0)
                        abs_recruitment = getattr(level, f'recruitment_abs_{month}', None)
                        abs_churn = getattr(level, f'churn_abs_{month}', None)
                        
                        current_fte = level.total
                        
                        # Calculate recruitment and churn
                        if abs_recruitment is not None:
                            recruitment_count = int(abs_recruitment)
                        else:
                            recruitment_count = int(recruitment_rate * current_fte / 100)
                        
                        if abs_churn is not None:
                            churn_count = int(abs_churn)
                        else:
                            churn_count = int(churn_rate * current_fte / 100)
                        
                        # Apply recruitment and churn
                        for _ in range(recruitment_count):
                            level.add_new_hire(current_date, role_name, office_name)
                        churned_people = level.apply_churn(churn_count)
                        
                        if recruitment_count > 0 or churn_count > 0:
                            print(f"  {role_name}.{level_name}: FTE={current_fte} -> {level.total}, Recruitment={recruitment_count}, Churn={churn_count}")
                        
                        office_recruitment += recruitment_count
                        office_churn += churn_count
                
                else:  # Flat role (like Operations)
                    recruitment_rate = getattr(role_data, f'recruitment_{month}', 0.0)
                    churn_rate = getattr(role_data, f'churn_{month}', 0.0)
                    abs_recruitment = getattr(role_data, f'recruitment_abs_{month}', None)
                    abs_churn = getattr(role_data, f'churn_abs_{month}', None)
                    
                    current_fte = role_data.total
                    
                    # Calculate recruitment and churn
                    if abs_recruitment is not None:
                        recruitment_count = int(abs_recruitment)
                    else:
                        recruitment_count = int(recruitment_rate * current_fte / 100)
                    
                    if abs_churn is not None:
                        churn_count = int(abs_churn)
                    else:
                        churn_count = int(churn_rate * current_fte / 100)
                    
                    # Apply recruitment and churn
                    for _ in range(recruitment_count):
                        role_data.add_new_hire(current_date, role_name, office_name)
                    churned_people = role_data.apply_churn(churn_count)
                    
                    if recruitment_count > 0 or churn_count > 0:
                        print(f"  {role_name}: FTE={current_fte} -> {role_data.total}, Recruitment={recruitment_count}, Churn={churn_count}")
                    
                    office_recruitment += recruitment_count
                    office_churn += churn_count
            
            # Recalculate office total FTE
            engine._recalculate_office_total_fte(office)
            print(f"  Office total: FTE={office.total_fte}, Recruitment={office_recruitment}, Churn={office_churn}, Net={office_recruitment - office_churn}")
        
        total_fte = sum(office.total_fte for office in offices.values())
        print(f"Total FTE after month {month}: {total_fte}")
    
    print(f"\n=== FINAL SUMMARY ===")
    print(f"Final total FTE: {sum(office.total_fte for office in offices.values())}")
    
    # Test the yearly snapshot
    print(f"\n=== TESTING YEARLY SNAPSHOT ===")
    from src.services.economic_parameters import EconomicParameters
    economic_params = EconomicParameters()
    
    yearly_snapshot = engine._get_yearly_snapshot({}, "2025", economic_params)
    total_fte_in_snapshot = sum(office_data['total_fte'] for office_data in yearly_snapshot.values())
    print(f"Total FTE in yearly snapshot: {total_fte_in_snapshot}")

if __name__ == "__main__":
    test_simulation_growth() 