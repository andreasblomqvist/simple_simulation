#!/usr/bin/env python3
"""
Debug the exact distribution values that Oslo is receiving.
"""
import json
import requests

def debug_oslo_distribution():
    """Debug the exact distribution calculation for Oslo."""
    
    print("🔍 DEBUGGING OSLO CHURN DISTRIBUTION")
    print("=" * 60)
    
    # Load office configuration
    with open('backend/config/office_configuration.json', 'r') as f:
        config = json.load(f)
    
    # Calculate the exact same distribution logic as the scenario resolver
    print("📊 REPLICATING SCENARIO RESOLVER LOGIC:")
    print("-" * 50)
    
    # Global churn rates from our scenario
    global_churn_rates = {
        "A": 20,    # 20 people per month globally
        "AC": 8,    # 8 people per month globally
        "C": 4,     # 4 people per month globally
        "SrC": 1,   # 1 person per month globally
        "AM": 0,    # 0 people per month globally
        "M": 0,     # 0 people per month globally
        "SrM": 0,   # 0 people per month globally
        "Pi": 0,    # 0 people per month globally
        "P": 0      # 0 people per month globally
    }
    
    # Calculate total FTE for this role across all offices (sum of all levels)
    total_role_fte = 0
    office_role_ftes = {}
    
    for office_name, office_config in config.items():
        office_role_fte = 0
        
        if ('roles' in office_config and 
            'Consultant' in office_config['roles']):
            
            role_config = office_config['roles']['Consultant']
            
            if isinstance(role_config, dict):
                # Sum all levels
                for level_config in role_config.values():
                    if isinstance(level_config, dict):
                        office_role_fte += level_config.get('fte', 0)
        
        office_role_ftes[office_name] = office_role_fte
        total_role_fte += office_role_fte
    
    print(f"Total Consultant FTE across all offices: {total_role_fte}")
    print(f"Oslo Consultant FTE: {office_role_ftes.get('Oslo', 0)}")
    
    oslo_weight = office_role_ftes.get('Oslo', 0) / total_role_fte if total_role_fte > 0 else 0
    print(f"Oslo weight: {oslo_weight:.6f}")
    
    print(f"\n📈 EXACT DISTRIBUTION CALCULATION:")
    print("-" * 50)
    print(f"{'Level':<6} {'Global':<8} {'Oslo Share':<12} {'Quota':<6} {'Remainder':<10} {'Final':<6}")
    print("-" * 50)
    
    oslo_distributed_values = {}
    total_oslo_churn = 0
    
    for level_name, global_value in global_churn_rates.items():
        if global_value > 0:
            # Calculate proportional value
            proportional_value = global_value * oslo_weight
            quota = int(proportional_value)
            remainder = proportional_value - quota
            
            oslo_distributed_values[level_name] = {
                'proportional': proportional_value,
                'quota': quota,
                'remainder': remainder
            }
            
            total_oslo_churn += proportional_value
            
            print(f"{level_name:<6} {global_value:<8} {proportional_value:<12.4f} {quota:<6} {remainder:<10.4f} {quota:<6}")
        else:
            oslo_distributed_values[level_name] = {
                'proportional': 0,
                'quota': 0,
                'remainder': 0
            }
            print(f"{level_name:<6} {global_value:<8} {0:<12.4f} {0:<6} {0:<10.4f} {0:<6}")
    
    print("-" * 50)
    print(f"Total proportional churn for Oslo: {total_oslo_churn:.4f}")
    
    # Apply largest remainder method
    print(f"\n🧮 LARGEST REMAINDER METHOD:")
    print("-" * 50)
    
    # Calculate total distributed quota
    total_quota = sum(v['quota'] for v in oslo_distributed_values.values())
    total_global_churn = sum(global_churn_rates.values())
    remaining_churn = total_global_churn * oslo_weight - total_quota
    
    print(f"Total quota distributed: {total_quota}")
    print(f"Expected total for Oslo: {total_global_churn * oslo_weight:.4f}")
    print(f"Remaining to distribute: {remaining_churn:.4f}")
    
    # Sort by remainder
    sorted_levels = sorted(
        [(level, data['remainder']) for level, data in oslo_distributed_values.items() 
         if data['remainder'] > 0],
        key=lambda x: x[1], reverse=True
    )
    
    print(f"Levels sorted by remainder: {sorted_levels}")
    
    # Distribute remaining
    remaining_int = round(remaining_churn)
    final_values = {level: data['quota'] for level, data in oslo_distributed_values.items()}
    
    for i in range(remaining_int):
        if i < len(sorted_levels):
            level_name = sorted_levels[i][0]
            final_values[level_name] += 1
    
    print(f"\n📋 FINAL OSLO CHURN DISTRIBUTION:")
    print("-" * 40)
    for level_name, final_value in final_values.items():
        if final_value > 0:
            print(f"{level_name}: {final_value} churn/month")
    
    total_final = sum(final_values.values())
    print(f"Total: {total_final} churn/month")
    
    if total_final == 0:
        print("🚨 FOUND THE ISSUE: Oslo gets 0 total churn after distribution!")
        print("This happens because Oslo's proportion is too small.")
        print(f"Oslo weight: {oslo_weight:.6f} * Total global: {total_global_churn} = {total_global_churn * oslo_weight:.4f}")
        print("This rounds down to 0 in the largest remainder method.")
    else:
        print("✅ Oslo should get churn. The issue is elsewhere.")

def main():
    """Run the Oslo distribution debug."""
    debug_oslo_distribution()

if __name__ == "__main__":
    main()