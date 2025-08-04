#!/usr/bin/env python3
"""
Debug why Oslo shows 0 churn after cleaning the configuration.
"""
import json
import requests

def debug_oslo_churn():
    """Debug Oslo churn issue step by step."""
    
    print("🔍 DEBUGGING OSLO CHURN ISSUE")
    print("=" * 60)
    
    # 1. Check the current office configuration
    print("\n1. 📁 CHECKING CLEAN OFFICE CONFIGURATION")
    with open('backend/config/office_configuration.json', 'r') as f:
        config = json.load(f)
    
    oslo_config = config['Oslo']
    print(f"Oslo total FTE: {oslo_config['total_fte']}")
    print("Oslo levels and FTE:")
    for level, level_data in oslo_config['roles']['Consultant'].items():
        fte = level_data['fte']
        # Check if any recruitment/churn abs values remain
        abs_keys = [k for k in level_data.keys() if 'abs_' in k]
        print(f"  {level}: {fte} FTE, abs_keys: {abs_keys}")
    
    # 2. Create a simple test scenario
    print("\n2. 🧪 CREATING SIMPLE TEST SCENARIO")
    
    # Simple scenario with only Oslo and Stockholm for comparison
    scenario = {
        "name": "Oslo Churn Debug Test",
        "description": "Simple test to debug Oslo churn issue",
        "time_range": {
            "start_year": 2024,
            "start_month": 1,
            "end_year": 2024,
            "end_month": 12
        },
        "office_scope": ["Oslo", "Stockholm"],  # Just two offices for debugging
        "baseline_input": {
            "global": {
                "recruitment": {
                    "Consultant": {
                        "levels": {}
                    }
                },
                "churn": {
                    "Consultant": {
                        "levels": {}
                    }
                }
            }
        },
        "levers": {
            "recruitment": {"A": 1.0, "AC": 1.0, "C": 1.0, "SrC": 1.0, "AM": 1.0, "M": 1.0, "SrM": 1.0, "Pi": 1.0, "P": 1.0},
            "churn": {"A": 1.0, "AC": 1.0, "C": 1.0, "SrC": 1.0, "AM": 1.0, "M": 1.0, "SrM": 1.0, "Pi": 1.0, "P": 1.0},
            "progression": {"A": 1.0, "AC": 1.0, "C": 1.0, "SrC": 1.0, "AM": 1.0, "M": 1.0, "SrM": 1.0, "Pi": 1.0, "P": 1.0}
        },
        "progression_config": None,
        "cat_curves": None
    }
    
    # Simple churn rates - just focus on the levels Oslo has
    churn_rates = {
        "A": 1,     # 1 person per month - Oslo has 5 FTE
        "AC": 1,    # 1 person per month - Oslo has 11 FTE  
        "C": 2,     # 2 people per month - Oslo has 23 FTE
        "SrC": 2,   # 2 people per month - Oslo has 20 FTE
        "AM": 2,    # 2 people per month - Oslo has 21 FTE
        "M": 1,     # 1 person per month - Oslo has 10 FTE
        "SrM": 0,   # 0 people per month - Oslo has 5 FTE
        "PiP": 0,   # 0 people per month - Oslo has 1 FTE
        "P": 0
    }
    
    recruitment_rates = {level: 0 for level in churn_rates.keys()}  # No recruitment for simplicity
    
    # Build the baseline input
    for level in churn_rates.keys():
        rec_value = recruitment_rates[level]
        churn_value = churn_rates[level]
        
        monthly_rec_values = {}
        monthly_churn_values = {}
        
        for month in range(1, 13):
            month_key = f"2024{month:02d}"
            monthly_rec_values[month_key] = rec_value
            monthly_churn_values[month_key] = churn_value
        
        scenario["baseline_input"]["global"]["recruitment"]["Consultant"]["levels"][level] = {
            "recruitment": {"values": monthly_rec_values},
            "churn": {"values": monthly_churn_values}
        }
        
        scenario["baseline_input"]["global"]["churn"]["Consultant"]["levels"][level] = {
            "recruitment": {"values": monthly_rec_values},
            "churn": {"values": monthly_churn_values}
        }
    
    print(f"Created scenario with churn rates: {churn_rates}")
    
    # 3. Run the scenario
    print("\n3. 🚀 RUNNING DEBUG SCENARIO")
    BASE_URL = "http://localhost:8000"
    payload = {"scenario_definition": scenario}
    
    response = requests.post(f"{BASE_URL}/scenarios/run", json=payload)
    
    if response.status_code != 200:
        print(f"❌ Simulation failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    result = response.json()
    if result.get("status") != "success":
        print(f"❌ Simulation error: {result.get('error_message', 'Unknown error')}")
        return
    
    scenario_id = result.get('scenario_id')
    print(f"✅ Simulation completed - ID: {scenario_id}")
    
    # 4. Check results
    print("\n4. 📊 CHECKING RESULTS")
    response = requests.get(f"{BASE_URL}/scenarios/{scenario_id}/results")
    result_data = response.json()
    results = result_data.get("results", {})
    
    if "years" in results and "2024" in results["years"]:
        year_data = results["years"]["2024"]
        
        for office_name in ["Oslo", "Stockholm"]:
            if office_name in year_data.get("offices", {}):
                office_data = year_data["offices"][office_name]
                
                print(f"\n🏢 {office_name.upper()} RESULTS:")
                
                total_churn = 0
                total_recruitment = 0
                
                for role_name, role_data in office_data.get("levels", {}).items():
                    for level_name, level_monthly_data in role_data.items():
                        if isinstance(level_monthly_data, list):
                            level_total_churn = sum(month.get("churn", 0) for month in level_monthly_data if isinstance(month, dict))
                            level_total_recruitment = sum(month.get("recruitment", 0) for month in level_monthly_data if isinstance(month, dict))
                            
                            total_churn += level_total_churn
                            total_recruitment += level_total_recruitment
                            
                            if level_total_churn > 0 or level_total_recruitment > 0:
                                print(f"  {level_name}: {level_total_recruitment} recruitment, {level_total_churn} churn")
                
                print(f"  TOTAL: {total_recruitment} recruitment, {total_churn} churn")
                
                if office_name == "Oslo" and total_churn == 0:
                    print("  🚨 OSLO STILL HAS 0 CHURN!")
                elif office_name == "Oslo" and total_churn > 0:
                    print("  ✅ Oslo now has churn - issue fixed!")
    
    print("\n=" * 60)

def main():
    """Run the Oslo churn debug."""
    debug_oslo_churn()

if __name__ == "__main__":
    main()