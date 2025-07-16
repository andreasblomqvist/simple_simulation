#!/usr/bin/env python3
"""
Script to show current recruitment and churn input values for all offices and Consultant levels.
"""

import json

def show_recruitment_churn_values():
    """Show recruitment and churn values for all offices and Consultant levels."""
    
    config_path = "../../backend/config/office_configuration.json"
    
    print("Loading configuration file...")
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print("\n=== RECRUITMENT AND CHURN VALUES ===\n")
    
    for office_name, office_data in config.items():
        print(f"Office: {office_name}")
        
        if 'roles' in office_data and 'Consultant' in office_data['roles']:
            consultant_data = office_data['roles']['Consultant']
            
            for level_name, level_data in consultant_data.items():
                print(f"  Level: {level_name}")
                
                # Get recruitment values for all 12 months
                recruitment_values = []
                for month in range(1, 13):
                    value = level_data.get(f'recruitment_abs_{month}', 0)
                    recruitment_values.append(value)
                
                # Get churn values for all 12 months
                churn_values = []
                for month in range(1, 13):
                    value = level_data.get(f'churn_abs_{month}', 0)
                    churn_values.append(value)
                
                print(f"    Recruitment (12 months): {recruitment_values}")
                print(f"    Churn (12 months):       {churn_values}")
                print(f"    Total recruitment: {sum(recruitment_values)}")
                print(f"    Total churn: {sum(churn_values)}")
                print()
        else:
            print("  No Consultant role found")
            print()
    
    # Summary statistics
    print("=== SUMMARY STATISTICS ===")
    total_recruitment = 0
    total_churn = 0
    
    for office_name, office_data in config.items():
        if 'roles' in office_data and 'Consultant' in office_data['roles']:
            consultant_data = office_data['roles']['Consultant']
            
            for level_name, level_data in consultant_data.items():
                office_level_recruitment = sum(level_data.get(f'recruitment_abs_{month}', 0) for month in range(1, 13))
                office_level_churn = sum(level_data.get(f'churn_abs_{month}', 0) for month in range(1, 13))
                
                total_recruitment += office_level_recruitment
                total_churn += office_level_churn
    
    print(f"Total recruitment across all offices and levels: {total_recruitment}")
    print(f"Total churn across all offices and levels: {total_churn}")
    print(f"Net change (recruitment - churn): {total_recruitment - total_churn}")

if __name__ == "__main__":
    show_recruitment_churn_values() 