#!/usr/bin/env python3
"""
Test different approaches to fix the distribution algorithm.
"""
import json
import math

def load_office_data():
    """Load office SrC FTE data."""
    with open('backend/config/office_configuration.json', 'r') as f:
        config = json.load(f)
    
    office_src_ftes = {}
    for office_name, office_config in config.items():
        src_fte = 0
        if ('roles' in office_config and 
            'Consultant' in office_config['roles'] and
            'SrC' in office_config['roles']['Consultant']):
            src_fte = office_config['roles']['Consultant']['SrC'].get('fte', 0)
        office_src_ftes[office_name] = src_fte
    
    return office_src_ftes

def test_distribution_method(office_src_ftes, total_churn, method_name, quota_func):
    """Test a specific distribution method."""
    total_src_fte = sum(office_src_ftes.values())
    
    print(f"\n🧮 {method_name}")
    print("=" * 60)
    
    office_quotas = {}
    office_remainders = {}
    total_distributed = 0
    
    for office_name, src_fte in office_src_ftes.items():
        weight = src_fte / total_src_fte if total_src_fte > 0 else 0
        proportional_value = total_churn * weight
        quota = quota_func(proportional_value)
        remainder = proportional_value - quota
        
        office_quotas[office_name] = quota
        office_remainders[office_name] = remainder
        total_distributed += quota
    
    # Largest remainder method for remaining allocation
    remaining_churn = total_churn - total_distributed
    sorted_offices = sorted(
        [(name, remainder) for name, remainder in office_remainders.items() 
         if office_src_ftes[name] > 0],
        key=lambda x: x[1], reverse=True
    )
    
    final_distribution = office_quotas.copy()
    remaining_int = round(remaining_churn)
    
    for i in range(remaining_int):
        if i < len(sorted_offices):
            office_name = sorted_offices[i][0]
            final_distribution[office_name] += 1
    
    # Results
    print(f"Total to distribute: {total_churn}")
    print(f"Initial distribution: {total_distributed}")
    print(f"Remaining: {remaining_int}")
    print()
    
    oslo_churn = final_distribution.get('Oslo', 0)
    helsinki_churn = final_distribution.get('Helsinki', 0)
    
    offices_with_zero = sum(1 for office, churn in final_distribution.items() 
                           if churn == 0 and office_src_ftes[office] > 0)
    
    print(f"Oslo gets: {oslo_churn} churn/month")
    print(f"Helsinki gets: {helsinki_churn} churn/month") 
    print(f"Offices with 0 churn despite having FTE: {offices_with_zero}")
    
    return final_distribution, offices_with_zero

def main():
    """Test different distribution methods."""
    office_src_ftes = load_office_data()
    total_churn = 7
    
    print("🔍 TESTING DIFFERENT DISTRIBUTION METHODS")
    print("=" * 80)
    
    methods = [
        ("CURRENT: int() truncation", int),
        ("FIX 1: round() method", round),  
        ("FIX 2: math.floor() + better remainder", math.floor),
        ("FIX 3: Minimum 1 for offices with FTE", lambda x: max(1, round(x)) if x > 0 else 0)
    ]
    
    results = []
    
    for method_name, quota_func in methods:
        dist, zero_count = test_distribution_method(office_src_ftes, total_churn, method_name, quota_func)
        results.append((method_name, dist, zero_count))
    
    print("\n📊 SUMMARY COMPARISON")
    print("=" * 60)
    for method_name, dist, zero_count in results:
        oslo_churn = dist.get('Oslo', 0)
        helsinki_churn = dist.get('Helsinki', 0)
        total_dist = sum(dist.values())
        print(f"{method_name}:")
        print(f"  Oslo: {oslo_churn}, Helsinki: {helsinki_churn}, Zero offices: {zero_count}, Total: {total_dist}")

if __name__ == "__main__":
    main()