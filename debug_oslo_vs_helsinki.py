#!/usr/bin/env python3
"""
Debug the specific difference between Oslo and Helsinki distribution.
"""
import json
import requests

def debug_oslo_vs_helsinki():
    """Debug why Oslo and Helsinki get different churn despite similar size."""
    
    print("🔍 DEBUGGING OSLO vs HELSINKI DISTRIBUTION")
    print("=" * 70)
    
    # Load office configuration
    with open('backend/config/office_configuration.json', 'r') as f:
        config = json.load(f)
    
    oslo_config = config['Oslo']
    helsinki_config = config['Helsinki']
    
    print(f"Oslo FTE: {oslo_config['total_fte']}")
    print(f"Helsinki FTE: {helsinki_config['total_fte']}")
    print(f"Difference: {abs(oslo_config['total_fte'] - helsinki_config['total_fte'])} FTE")
    
    # Compare their level structures
    print(f"\n📊 LEVEL STRUCTURE COMPARISON:")
    print("-" * 50)
    print(f"{'Level':<6} {'Oslo FTE':<10} {'Helsinki FTE':<14} {'Difference'}")
    print("-" * 50)
    
    oslo_levels = oslo_config['roles']['Consultant']
    helsinki_levels = helsinki_config['roles']['Consultant']
    
    all_levels = set(list(oslo_levels.keys()) + list(helsinki_levels.keys()))
    
    for level in sorted(all_levels):
        oslo_fte = oslo_levels.get(level, {}).get('fte', 0)
        helsinki_fte = helsinki_levels.get(level, {}).get('fte', 0)
        diff = oslo_fte - helsinki_fte
        
        print(f"{level:<6} {oslo_fte:<10} {helsinki_fte:<14} {diff:+}")
    
    # Check if there are any remaining absolute values that might be interfering
    print(f"\n🔍 CHECKING FOR REMAINING ABSOLUTE OVERRIDES:")
    print("-" * 60)
    
    for office_name, office_config in [("Oslo", oslo_config), ("Helsinki", helsinki_config)]:
        print(f"\n{office_name}:")
        found_abs_values = False
        
        for level_name, level_data in office_config['roles']['Consultant'].items():
            abs_keys = [k for k in level_data.keys() if 'abs_' in k]
            if abs_keys:
                print(f"  {level_name}: {abs_keys}")
                found_abs_values = True
        
        if not found_abs_values:
            print(f"  ✅ No absolute overrides found")
    
    # Simulate the exact distribution calculation for both
    print(f"\n🧮 SIMULATING DISTRIBUTION CALCULATION:")
    print("-" * 60)
    
    # Calculate total FTE for Consultant role across all offices
    total_consultant_fte = 0
    for office_config in config.values():
        if 'roles' in office_config and 'Consultant' in office_config['roles']:
            for level_config in office_config['roles']['Consultant'].values():
                if isinstance(level_config, dict):
                    total_consultant_fte += level_config.get('fte', 0)
    
    print(f"Total Consultant FTE across all offices: {total_consultant_fte}")
    
    # Test with a simple churn value
    test_global_churn = 25  # 25 people globally for A level
    
    for office_name, office_config in [("Oslo", oslo_config), ("Helsinki", helsinki_config)]:
        office_consultant_fte = sum(
            level_config.get('fte', 0) 
            for level_config in office_config['roles']['Consultant'].values()
            if isinstance(level_config, dict)
        )
        
        office_weight = office_consultant_fte / total_consultant_fte
        proportional_value = test_global_churn * office_weight
        quota = int(proportional_value)
        remainder = proportional_value - quota
        
        print(f"\n{office_name}:")
        print(f"  Consultant FTE: {office_consultant_fte}")
        print(f"  Weight: {office_weight:.6f}")
        print(f"  Proportional value: {proportional_value:.4f}")
        print(f"  Quota (int): {quota}")
        print(f"  Remainder: {remainder:.4f}")
    
    # Get the actual simulation results to see what each level got
    print(f"\n📊 ACTUAL SIMULATION RESULTS BY LEVEL:")
    print("-" * 60)
    
    # Get most recent scenario
    BASE_URL = "http://localhost:8000"
    response = requests.get(f"{BASE_URL}/scenarios/list")
    scenarios = response.json().get("scenarios", [])
    recent_scenario = sorted(scenarios, key=lambda x: x.get("created_at", ""), reverse=True)[0]
    
    scenario_id = recent_scenario["id"]
    
    # Get results
    response = requests.get(f"{BASE_URL}/scenarios/{scenario_id}/results")
    result_data = response.json()
    results = result_data.get("results", {})
    
    if "years" in results and "2024" in results["years"]:
        year_data = results["years"]["2024"]
        
        for office_name in ["Oslo", "Helsinki"]:
            if office_name in year_data.get("offices", {}):
                office_data = year_data["offices"][office_name]
                
                print(f"\n{office_name} - Level by Level Results:")
                
                for role_name, role_data in office_data.get("levels", {}).items():
                    for level_name, level_monthly_data in role_data.items():
                        if isinstance(level_monthly_data, list):
                            level_total_churn = sum(month.get("churn", 0) for month in level_monthly_data if isinstance(month, dict))
                            level_total_recruitment = sum(month.get("recruitment", 0) for month in level_monthly_data if isinstance(month, dict))
                            
                            if level_total_churn > 0 or level_total_recruitment > 0:
                                print(f"  {level_name}: {level_total_recruitment} rec, {level_total_churn} churn")
    
    print(f"\n🔍 CONCLUSION:")
    print("-" * 30)
    print("If Oslo and Helsinki have similar sizes but different churn results,")
    print("the issue is NOT purely about office size proportional distribution.")
    print("There may be:")
    print("1. Different level structures affecting which levels get distributed values")
    print("2. Office-specific logic or ordering effects in the distribution")
    print("3. Bugs in how the distributed values are applied to specific offices")

def main():
    """Run the Oslo vs Helsinki debug."""
    debug_oslo_vs_helsinki()

if __name__ == "__main__":
    main()