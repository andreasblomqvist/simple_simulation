#!/usr/bin/env python3
"""
Test script to run a single month simulation and see actual recruitment/churn numbers.
"""

import json
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from src.services.office_builder import OfficeBuilder
from src.services.simulation_engine import SimulationEngine

def test_single_month():
    """Test a single month simulation to see recruitment/churn numbers."""
    
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
    
    print("Testing single month simulation...")
    print(f"Initial total FTE: {sum(office.total_fte for office in offices.values())}")
    
    # Test a single month (January 2025)
    current_date = "2025-01"
    current_month = 1
    
    total_recruitment = 0
    total_churn = 0
    
    for office_name, office in offices.items():
        print(f"\nOffice: {office_name}")
        office_recruitment = 0
        office_churn = 0
        
        for role_name, role_data in office.roles.items():
            if isinstance(role_data, dict):  # Leveled role
                for level_name, level in role_data.items():
                    # Get recruitment and churn rates
                    recruitment_rate = getattr(level, f'recruitment_{current_month}', 0.0)
                    churn_rate = getattr(level, f'churn_{current_month}', 0.0)
                    abs_recruitment = getattr(level, f'recruitment_abs_{current_month}', None)
                    abs_churn = getattr(level, f'churn_abs_{current_month}', None)
                    
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
                    
                    if recruitment_count > 0 or churn_count > 0:
                        print(f"  {role_name}.{level_name}: FTE={current_fte}, Recruitment={recruitment_count}, Churn={churn_count}")
                        print(f"    (rates: {recruitment_rate}%, {churn_rate}%, abs: {abs_recruitment}, {abs_churn})")
                    
                    office_recruitment += recruitment_count
                    office_churn += churn_count
            
            else:  # Flat role (like Operations)
                recruitment_rate = getattr(role_data, f'recruitment_{current_month}', 0.0)
                churn_rate = getattr(role_data, f'churn_{current_month}', 0.0)
                abs_recruitment = getattr(role_data, f'recruitment_abs_{current_month}', None)
                abs_churn = getattr(role_data, f'churn_abs_{current_month}', None)
                
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
                
                if recruitment_count > 0 or churn_count > 0:
                    print(f"  {role_name}: FTE={current_fte}, Recruitment={recruitment_count}, Churn={churn_count}")
                    print(f"    (rates: {recruitment_rate}%, {churn_rate}%, abs: {abs_recruitment}, {abs_churn})")
                
                office_recruitment += recruitment_count
                office_churn += churn_count
        
        print(f"  Office total: Recruitment={office_recruitment}, Churn={office_churn}, Net={office_recruitment - office_churn}")
        total_recruitment += office_recruitment
        total_churn += office_churn
    
    print(f"\n=== SUMMARY ===")
    print(f"Total recruitment: {total_recruitment}")
    print(f"Total churn: {total_churn}")
    print(f"Net growth: {total_recruitment - total_churn}")
    
    if total_recruitment == 0:
        print("❌ NO recruitment happening! This is the problem.")
    elif total_recruitment - total_churn <= 0:
        print("❌ Churn is canceling out recruitment!")
    else:
        print("✅ Recruitment is happening and exceeding churn!")

if __name__ == "__main__":
    test_single_month() 