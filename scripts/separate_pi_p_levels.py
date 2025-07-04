#!/usr/bin/env python3
"""
Script to separate PiP levels into Pi (Principe) and P (Partner) levels
in the office configuration file.
"""

import json
import os
import sys
from pathlib import Path

def separate_pip_levels():
    """Separate PiP levels into Pi and P levels in office configuration."""
    
    # Paths
    config_path = Path("backend/config/office_configuration.json")
    backup_path = Path("backend/config/office_configuration.json.backup_separated")
    
    if not config_path.exists():
        print(f"Error: Configuration file not found at {config_path}")
        return False
    
    # Load current configuration
    print("Loading current configuration...")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Create backup
    print("Creating backup...")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    # Process each office
    print("Processing offices...")
    for office in config:
        if 'roles' in office:
            for role_name, role_data in office['roles'].items():
                if role_name != 'Operations' and 'PiP' in role_data:
                    # Get the PiP data
                    pip_data = role_data['PiP']
                    
                    # Create Pi (Principe) level - 80% of PiP data
                    pi_data = pip_data.copy()
                    if 'fte' in pi_data:
                        pi_data['fte'] = int(pip_data['fte'] * 0.8)
                    
                    # Create P (Partner) level - 20% of PiP data  
                    p_data = pip_data.copy()
                    if 'fte' in p_data:
                        p_data['fte'] = int(pip_data['fte'] * 0.2)
                    
                    # Replace PiP with Pi and P
                    del role_data['PiP']
                    role_data['Pi'] = pi_data
                    role_data['P'] = p_data
    
    # Save updated configuration
    print("Saving updated configuration...")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully separated PiP levels into Pi and P levels")
    print(f"Backup saved to: {backup_path}")
    return True

def update_tests():
    """Update test files to expect Pi and P instead of PiP."""
    
    test_files = [
        "backend/tests/unit/test_scenario_service_refactored.py",
        "backend/tests/unit/test_scenario_service.py", 
        "backend/tests/unit/test_engine_basic.py",
        "backend/tests/unit/test_engine_refactored.py"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"Updating {test_file}...")
            
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace expected levels
            content = content.replace(
                'expected_levels = ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"]',
                'expected_levels = ["A", "AC", "C", "SrC", "AM", "M", "SrM", "Pi", "P"]'
            )
            content = content.replace(
                "expected_levels = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']",
                "expected_levels = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P']"
            )
            
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(content)

def update_utils():
    """Update utils.py to include Pi and P in level order."""
    
    utils_file = "backend/src/services/simulation/utils.py"
    
    if os.path.exists(utils_file):
        print(f"Updating {utils_file}...")
        
        with open(utils_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update the actual_order list
        content = content.replace(
            "actual_order = ['A', 'AC', 'AM', 'C', 'SrC', 'M', 'SrM', 'PiP']",
            "actual_order = ['A', 'AC', 'AM', 'C', 'SrC', 'M', 'SrM', 'Pi', 'P']"
        )
        
        with open(utils_file, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == "__main__":
    print("Separating PiP levels into Pi and P levels...")
    
    try:
        # Separate levels in configuration
        if separate_pip_levels():
            # Update tests
            update_tests()
            
            # Update utils
            update_utils()
            
            print("Successfully completed all updates!")
        else:
            print("Failed to separate levels")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 