#!/usr/bin/env python3
"""
Test script to verify that absolute recruitment values are being loaded correctly.
"""

import json
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from src.services.office_builder import OfficeBuilder

def test_absolute_recruitment_loading():
    """Test that absolute recruitment values are loaded correctly."""
    
    # Load the configuration
    config_path = backend_dir / "config" / "office_configuration.json"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Create office builder
    builder = OfficeBuilder()
    
    # Build offices
    offices = builder.build_offices_from_config(config, {})
    
    print("Testing absolute recruitment values in built offices...")
    
    total_levels_checked = 0
    levels_with_absolute_recruitment = 0
    
    for office_name, office in offices.items():
        print(f"\nOffice: {office_name}")
        
        for role_name, role_data in office.roles.items():
            if isinstance(role_data, dict):  # Leveled role
                for level_name, level in role_data.items():
                    total_levels_checked += 1
                    
                    # Check if absolute recruitment values are set
                    has_absolute = False
                    for month in range(1, 13):
                        abs_value = getattr(level, f'recruitment_abs_{month}', None)
                        if abs_value is not None and abs_value > 0:
                            has_absolute = True
                            print(f"  {role_name}.{level_name}: recruitment_abs_{month} = {abs_value}")
                    
                    if has_absolute:
                        levels_with_absolute_recruitment += 1
                    else:
                        print(f"  {role_name}.{level_name}: NO absolute recruitment values found")
            
            else:  # Flat role (like Operations)
                total_levels_checked += 1
                
                # Check if absolute recruitment values are set
                has_absolute = False
                for month in range(1, 13):
                    abs_value = getattr(role_data, f'recruitment_abs_{month}', None)
                    if abs_value is not None and abs_value > 0:
                        has_absolute = True
                        print(f"  {role_name}: recruitment_abs_{month} = {abs_value}")
                
                if has_absolute:
                    levels_with_absolute_recruitment += 1
                else:
                    print(f"  {role_name}: NO absolute recruitment values found")
    
    print(f"\n=== SUMMARY ===")
    print(f"Total levels checked: {total_levels_checked}")
    print(f"Levels with absolute recruitment: {levels_with_absolute_recruitment}")
    print(f"Levels missing absolute recruitment: {total_levels_checked - levels_with_absolute_recruitment}")
    
    if levels_with_absolute_recruitment == 0:
        print("❌ NO absolute recruitment values found! This is the problem.")
    else:
        print("✅ Absolute recruitment values are being loaded correctly.")

if __name__ == "__main__":
    test_absolute_recruitment_loading() 