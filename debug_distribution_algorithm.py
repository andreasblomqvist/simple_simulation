#!/usr/bin/env python3
"""
Debug script to analyze the distribution algorithm issue.
Based on the provided context:
- Expected global totals: 4,752 recruitment, 3,600 churn annually
- Actual global totals: 363 recruitment, 275 churn annually
- 8 out of 12 offices show 0 churn: Amsterdam, Berlin, Cologne, Copenhagen, Frankfurt, Oslo, Toronto, Zurich
- Only 4 offices get churn: Hamburg (44), Helsinki (33), Munich (66), Stockholm (132)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from services.scenario_resolver import ScenarioResolver
from services.config_service import config_service

def debug_exact_distribute_value():
    """Debug the exact distribution algorithm with example values."""
    
    resolver = ScenarioResolver(config_service)
    
    # Get the actual office configuration
    config = config_service.get_config()
    
    print("=== DEBUGGING DISTRIBUTION ALGORITHM ===")
    print(f"Total offices: {len(config)}")
    
    # Extract office names and sizes for analysis
    offices_info = []
    for office_name, office_config in config.items():
        total_fte = office_config.get('total_fte', 0)
        consultant_a_fte = 0
        
        # Get Consultant A FTE specifically
        if 'roles' in office_config and 'Consultant' in office_config['roles']:
            consultant_role = office_config['roles']['Consultant']
            if isinstance(consultant_role, dict) and 'A' in consultant_role:
                consultant_a_fte = consultant_role['A'].get('fte', 0)
        
        offices_info.append({
            'name': office_name,
            'total_fte': total_fte,
            'consultant_a_fte': consultant_a_fte
        })
    
    # Sort by total FTE to see distribution pattern
    offices_info.sort(key=lambda x: x['total_fte'], reverse=True)
    
    print("\n=== OFFICE SIZES (by total FTE) ===")
    total_fte_all = sum(info['total_fte'] for info in offices_info)
    for info in offices_info:
        weight = info['total_fte'] / total_fte_all if total_fte_all > 0 else 0
        print(f"{info['name']:12} | Total FTE: {info['total_fte']:5.0f} | Consultant A: {info['consultant_a_fte']:5.1f} | Weight: {weight:.3f}")
    
    print(f"\nTotal FTE across all offices: {total_fte_all}")
    
    # Test distribution with different churn values
    test_values = [300.0, 100.0, 50.0, 10.0, 5.0, 1.0]
    
    for test_value in test_values:
        print(f"\n=== TESTING DISTRIBUTION OF {test_value} CHURN ===")
        
        # Test distribution for Consultant level A
        distributed = resolver._exact_distribute_value(
            test_value, config, 'Consultant', 'A', total_fte_all
        )
        
        # Show results
        total_distributed = sum(distributed.values())
        offices_with_values = sum(1 for v in distributed.values() if v > 0)
        
        print(f"Input value: {test_value}")
        print(f"Total distributed: {total_distributed}")
        print(f"Offices receiving values: {offices_with_values}/{len(distributed)}")
        print(f"Distribution accuracy: {abs(test_value - total_distributed):.6f}")
        
        # Show non-zero distributions
        non_zero = [(name, value) for name, value in distributed.items() if value > 0]
        non_zero.sort(key=lambda x: x[1], reverse=True)
        
        print("Non-zero distributions:")
        for name, value in non_zero:
            office_info = next(info for info in offices_info if info['name'] == name)
            weight = office_info['consultant_a_fte'] / sum(info['consultant_a_fte'] for info in offices_info)
            print(f"  {name:12} | {value:6.1f} | Weight: {weight:.3f}")
        
        # Show zero distributions
        zero_offices = [name for name, value in distributed.items() if value == 0]
        if zero_offices:
            print(f"Offices with 0 churn: {', '.join(zero_offices)}")

def analyze_largest_remainder_issue():
    """Analyze potential issues in the largest remainder method."""
    
    print("\n=== ANALYZING LARGEST REMAINDER METHOD ===")
    
    # Simulate the algorithm with a small example
    total_value = 3600  # Annual churn target
    monthly_value = total_value / 12  # 300 per month
    
    # Example office weights (simplified)
    office_weights = {
        'Stockholm': 0.25,  # Large office
        'Hamburg': 0.15,    # Medium office  
        'Munich': 0.12,     # Medium office
        'Helsinki': 0.08,   # Medium office
        'Oslo': 0.05,       # Small office
        'Amsterdam': 0.04,  # Small office
        'Berlin': 0.04,     # Small office
        'Toronto': 0.03,    # Small office
        'Zurich': 0.03,     # Small office
        'Copenhagen': 0.03, # Small office
        'Cologne': 0.02,    # Small office
        'Frankfurt': 0.02,  # Small office
    }
    
    print(f"Testing with monthly value: {monthly_value}")
    print(f"Total weight: {sum(office_weights.values())}")
    
    # Calculate proportional values and remainders
    office_quotas = {}
    office_remainders = {}
    total_distributed = 0
    
    for office_name, weight in office_weights.items():
        proportional_value = monthly_value * weight
        quota = int(proportional_value)  # This is the issue!
        remainder = proportional_value - quota
        
        office_quotas[office_name] = quota
        office_remainders[office_name] = remainder
        total_distributed += quota
        
        print(f"{office_name:12} | Weight: {weight:.3f} | Proportional: {proportional_value:6.2f} | Quota: {quota:2d} | Remainder: {remainder:.3f}")
    
    print(f"\nTotal distributed after int() truncation: {total_distributed}")
    print(f"Remaining to distribute: {monthly_value - total_distributed}")
    
    # Apply largest remainder method
    remaining_fte = monthly_value - total_distributed
    remaining_fte_int = round(remaining_fte)
    
    # Sort by remainder
    sorted_offices = sorted(office_remainders.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\nLargest remainder method - distributing {remaining_fte_int} additional units:")
    for i in range(remaining_fte_int):
        if i < len(sorted_offices):
            office_name = sorted_offices[i][0]
            office_quotas[office_name] += 1
            print(f"  +1 to {office_name} (remainder: {sorted_offices[i][1]:.3f})")
    
    print(f"\nFinal distribution:")
    final_total = 0
    for office_name, quota in office_quotas.items():
        final_total += quota
        print(f"{office_name:12} | Final: {quota:2d}")
    
    print(f"Final total: {final_total}")
    print(f"Accuracy: {abs(monthly_value - final_total):.6f}")
    
    # Count offices with zero allocation
    zero_count = sum(1 for quota in office_quotas.values() if quota == 0)
    print(f"Offices with 0 allocation: {zero_count}/{len(office_quotas)}")

if __name__ == "__main__":
    debug_exact_distribute_value()
    analyze_largest_remainder_issue()