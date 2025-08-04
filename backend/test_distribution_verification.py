#!/usr/bin/env python3
"""
Test script to verify that distributed recruitment and churn numbers sum up to global numbers.
"""

import json
import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from src.services.config_service import config_service
from src.services.scenario_service import ScenarioService
from src.services.scenario_resolver import ScenarioResolver

def test_distribution_verification():
    """Test that distributed values sum up to global values."""
    print("🔍 Testing Distribution Verification")
    print("=" * 50)
    
    # Load scenario file
    scenario_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data", "scenarios", "definitions", "f5f26bc5-3830-4f64-ba53-03b58ae72353.json"
    )
    
    with open(scenario_file, 'r') as f:
        scenario_data = json.load(f)
    
    # Get global baseline data
    baseline_input = scenario_data.get('baseline_input', {})
    global_data = baseline_input.get('global', {})
    
    print("📊 Global Recruitment Numbers (Consultant role):")
    if 'recruitment' in global_data and 'Consultant' in global_data['recruitment']:
        consultant_recruitment = global_data['recruitment']['Consultant']
        for level_name, level_data in consultant_recruitment.items():
            print(f"  {level_name}:")
            for month in range(1, 13):
                month_key = f"2025{month:02d}"
                value = level_data.get(month_key, 0.0)
                print(f"    Month {month}: {value}")
    
    print("\n📊 Global Churn Numbers (Consultant role):")
    if 'churn' in global_data and 'Consultant' in global_data['churn']:
        consultant_churn = global_data['churn']['Consultant']
        for level_name, level_data in consultant_churn.items():
            print(f"  {level_name}:")
            for month in range(1, 13):
                month_key = f"2025{month:02d}"
                value = level_data.get(month_key, 0.0)
                print(f"    Month {month}: {value}")
    
    # Resolve scenario using the resolver directly
    scenario_resolver = ScenarioResolver(config_service)
    resolved_data = scenario_resolver.resolve_scenario(scenario_data)
    offices_config = resolved_data.get('offices_config', {})
    
    print(f"\n📊 Distribution Results (Consultant role):")
    
    # Calculate total distributed values for each month
    total_distributed_recruitment = {month: {level: 0.0 for level in ['A', 'AC', 'C', 'SrC', 'AM']} for month in range(1, 13)}
    total_distributed_churn = {month: {level: 0.0 for level in ['A', 'AC', 'C', 'SrC', 'AM']} for month in range(1, 13)}
    
    for office_name, office_config in offices_config.items():
        office_fte = office_config.get('total_fte', 0)
        print(f"\n🏢 {office_name} (FTE: {office_fte}):")
        
        if 'Consultant' in office_config.get('roles', {}):
            consultant_role = office_config['roles']['Consultant']
            for level_name, level_config in consultant_role.items():
                if level_name in ['A', 'AC', 'C', 'SrC', 'AM']:
                    print(f"  {level_name}:")
                    for month in range(1, 13):
                        recruitment_value = level_config.get(f'recruitment_abs_{month}', 0.0)
                        churn_value = level_config.get(f'churn_abs_{month}', 0.0)
                        
                        total_distributed_recruitment[month][level_name] += recruitment_value
                        total_distributed_churn[month][level_name] += churn_value
                        
                        print(f"    Month {month}: Rec={recruitment_value:.2f}, Churn={churn_value:.2f}")
    
    # Verify totals match global values
    print(f"\n✅ Verification - Total Distributed vs Global:")
    
    for month in range(1, 13):
        month_key = f"2025{month:02d}"
        print(f"\n📅 Month {month}:")
        
        for level_name in ['A', 'AC', 'C', 'SrC', 'AM']:
            global_recruitment = 0.0
            global_churn = 0.0
            
            if 'recruitment' in global_data and 'Consultant' in global_data['recruitment']:
                if level_name in global_data['recruitment']['Consultant']:
                    global_recruitment = global_data['recruitment']['Consultant'][level_name].get(month_key, 0.0)
            
            if 'churn' in global_data and 'Consultant' in global_data['churn']:
                if level_name in global_data['churn']['Consultant']:
                    global_churn = global_data['churn']['Consultant'][level_name].get(month_key, 0.0)
            
            distributed_recruitment = total_distributed_recruitment[month][level_name]
            distributed_churn = total_distributed_churn[month][level_name]
            
            recruitment_match = abs(global_recruitment - distributed_recruitment) < 0.01
            churn_match = abs(global_churn - distributed_churn) < 0.01
            
            print(f"  {level_name}:")
            print(f"    Recruitment: Global={global_recruitment}, Distributed={distributed_recruitment:.2f}, Match={recruitment_match}")
            print(f"    Churn: Global={global_churn}, Distributed={distributed_churn:.2f}, Match={churn_match}")

if __name__ == "__main__":
    test_distribution_verification() 