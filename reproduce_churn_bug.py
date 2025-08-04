#!/usr/bin/env python3
"""
Reproduce the exact churn distribution bug described:
- Expected: 3,600 annual churn (300/month)
- Actual: 275 annual churn 
- 8 offices get 0 churn, only 4 get churn values
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from services.scenario_resolver import ScenarioResolver
from services.config_service import config_service

def reproduce_churn_bug():
    """Reproduce the exact churn distribution issue."""
    
    resolver = ScenarioResolver(config_service)
    config = config_service.get_config()
    
    print("=== REPRODUCING CHURN DISTRIBUTION BUG ===")
    
    # Calculate total Consultant FTE across all offices for role-based distribution
    total_consultant_fte = 0
    office_consultant_ftes = {}
    
    for office_name, office_config in config.items():
        office_consultant_fte = 0
        
        if ('roles' in office_config and 
            'Consultant' in office_config['roles']):
            
            consultant_role = office_config['roles']['Consultant']
            
            if isinstance(consultant_role, dict):
                # Sum all consultant levels
                for level_config in consultant_role.values():
                    if isinstance(level_config, dict):
                        office_consultant_fte += level_config.get('fte', 0)
        
        office_consultant_ftes[office_name] = office_consultant_fte
        total_consultant_fte += office_consultant_fte
    
    print(f"Total Consultant FTE across all offices: {total_consultant_fte}")
    print("\nConsultant FTE by office:")
    for office_name, fte in sorted(office_consultant_ftes.items(), key=lambda x: x[1], reverse=True):
        weight = fte / total_consultant_fte if total_consultant_fte > 0 else 0
        print(f"  {office_name:12} | {fte:5.1f} FTE | Weight: {weight:.3f}")
    
    # Test with realistic monthly churn values (expecting 300/month = 3600/year)
    monthly_churn = 300.0 / 12  # 25 per month per level on average
    
    print(f"\n=== TESTING MONTHLY CHURN DISTRIBUTION: {monthly_churn} ===")
    
    # Test distribution for Consultant level A specifically
    distributed = resolver._exact_distribute_value(
        monthly_churn, config, 'Consultant', 'A', total_consultant_fte
    )
    
    # Show detailed results
    total_distributed = sum(distributed.values())
    offices_with_churn = [(name, value) for name, value in distributed.items() if value > 0]
    offices_without_churn = [name for name, value in distributed.items() if value == 0]
    
    print(f"Input monthly churn: {monthly_churn}")
    print(f"Total distributed: {total_distributed}")
    print(f"Distribution accuracy: {abs(monthly_churn - total_distributed):.6f}")
    print(f"Offices with churn: {len(offices_with_churn)}/{len(distributed)}")
    print(f"Offices without churn: {len(offices_without_churn)}/{len(distributed)}")
    
    # Show offices that receive churn
    if offices_with_churn:
        print("\nOffices receiving churn:")
        offices_with_churn.sort(key=lambda x: x[1], reverse=True)
        for name, value in offices_with_churn:
            consultant_a_fte = 0
            if ('roles' in config[name] and 
                'Consultant' in config[name]['roles'] and
                'A' in config[name]['roles']['Consultant']):
                consultant_a_fte = config[name]['roles']['Consultant']['A'].get('fte', 0)
            
            weight = consultant_a_fte / sum(
                config[off]['roles']['Consultant']['A'].get('fte', 0) 
                for off in config
                if 'roles' in config[off] and 'Consultant' in config[off]['roles'] and 'A' in config[off]['roles']['Consultant']
            ) if consultant_a_fte > 0 else 0
            
            annual_churn = value * 12
            print(f"  {name:12} | Monthly: {value:4.1f} | Annual: {annual_churn:5.1f} | Consultant A FTE: {consultant_a_fte:4.1f} | Weight: {weight:.3f}")
    
    # Show offices that don't receive churn  
    if offices_without_churn:
        print(f"\nOffices with 0 churn: {', '.join(offices_without_churn)}")
        
        # Analyze why they get 0
        print("\nAnalyzing why these offices get 0 churn:")
        for office_name in offices_without_churn:
            consultant_a_fte = 0
            if ('roles' in config[office_name] and 
                'Consultant' in config[office_name]['roles'] and
                'A' in config[office_name]['roles']['Consultant']):
                consultant_a_fte = config[office_name]['roles']['Consultant']['A'].get('fte', 0)
            
            total_consultant_a_fte = sum(
                config[off]['roles']['Consultant']['A'].get('fte', 0) 
                for off in config
                if 'roles' in config[off] and 'Consultant' in config[off]['roles'] and 'A' in config[off]['roles']['Consultant']
            )
            
            weight = consultant_a_fte / total_consultant_a_fte if total_consultant_a_fte > 0 else 0
            proportional = monthly_churn * weight
            quota = int(proportional)
            remainder = proportional - quota
            
            print(f"  {office_name:12} | Consultant A FTE: {consultant_a_fte:4.1f} | Weight: {weight:.4f} | Proportional: {proportional:.4f} | Quota: {quota} | Remainder: {remainder:.4f}")

def analyze_int_truncation_issue():
    """Analyze the specific int() truncation issue."""
    
    print(f"\n=== ANALYZING INT() TRUNCATION ISSUE ===")
    
    # Example: small office with weight that results in fractional proportional value
    test_cases = [
        {"monthly_churn": 25.0, "office_weight": 0.014, "office_name": "Amsterdam"},
        {"monthly_churn": 25.0, "office_weight": 0.007, "office_name": "Frankfurt"},
        {"monthly_churn": 25.0, "office_weight": 0.029, "office_name": "Cologne"},
    ]
    
    for case in test_cases:
        monthly_churn = case["monthly_churn"]
        weight = case["office_weight"]
        office_name = case["office_name"]
        
        proportional_value = monthly_churn * weight
        quota = int(proportional_value)  # This is the problematic line!
        remainder = proportional_value - quota
        
        print(f"\n{office_name}:")
        print(f"  Monthly churn pool: {monthly_churn}")
        print(f"  Office weight: {weight:.3f}")
        print(f"  Proportional value: {proportional_value:.3f}")
        print(f"  Quota (int() truncation): {quota}")
        print(f"  Remainder: {remainder:.3f}")
        print(f"  Lost due to truncation: {remainder:.3f}")
        
        # What should happen vs what actually happens
        if quota == 0:
            print(f"  ISSUE: Office gets 0 churn despite having {proportional_value:.3f} proportional share!")
            print(f"  This office needs to compete in largest remainder method for any allocation.")

if __name__ == "__main__":
    reproduce_churn_bug()
    analyze_int_truncation_issue()