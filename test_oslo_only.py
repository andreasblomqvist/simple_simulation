#!/usr/bin/env python3
"""
Test Oslo with explicit absolute values to bypass distribution logic.
"""
import json
import requests

def test_oslo_only():
    """Test Oslo with explicit absolute churn values."""
    
    print("🧪 TESTING OSLO WITH EXPLICIT ABSOLUTE VALUES")
    print("=" * 60)
    
    # Create scenario with only Oslo and explicit absolute values
    scenario = {
        "name": "Oslo Only - Explicit Values",
        "description": "Test Oslo with explicit absolute churn values",
        "time_range": {
            "start_year": 2024,
            "start_month": 1,
            "end_year": 2024,
            "end_month": 12
        },
        "office_scope": ["Oslo"],
        "baseline_input": {
            "global": {
                "churn": {
                    "Consultant": {
                        "levels": {
                            "A": {
                                "recruitment": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 2 for m in range(1, 13)}}  # 2 churn per month
                            },
                            "AC": {
                                "recruitment": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 1 for m in range(1, 13)}}  # 1 churn per month
                            },
                            "C": {
                                "recruitment": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 1 for m in range(1, 13)}}  # 1 churn per month
                            }
                        }
                    }
                },
                "recruitment": {
                    "Consultant": {
                        "levels": {
                            "A": {
                                "recruitment": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)}}
                            },
                            "AC": {
                                "recruitment": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)}}
                            },
                            "C": {
                                "recruitment": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)}}
                            }
                        }
                    }
                }
            }
        },
        "levers": {
            "recruitment": {"A": 1.0, "AC": 1.0, "C": 1.0, "SrC": 1.0, "AM": 1.0, "M": 1.0, "SrM": 1.0, "Pi": 1.0, "P": 1.0},
            "churn": {"A": 1.0, "AC": 1.0, "C": 1.0, "SrC": 1.0, "AM": 1.0, "M": 1.0, "SrM": 1.0, "Pi": 1.0, "P": 1.0},
            "progression": {"A": 1.0, "AC": 1.0, "C": 1.0, "SrC": 1.0, "AM": 1.0, "M": 1.0, "SrM": 1.0, "Pi": 1.0, "P": 1.0}
        }
    }
    
    print("📊 Scenario: Oslo only with explicit churn values")
    print("📊 A level: 2 churn/month (24 annual)")
    print("📊 AC level: 1 churn/month (12 annual)")
    print("📊 C level: 1 churn/month (12 annual)")
    print("📊 Expected total: 48 annual churn")
    
    # Run the scenario
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
    print(f"✅ Oslo simulation completed - ID: {scenario_id}")
    
    # Get results
    response = requests.get(f"{BASE_URL}/scenarios/{scenario_id}/results")
    result_data = response.json()
    results = result_data.get("results", {})
    
    if "years" in results and "2024" in results["years"]:
        year_data = results["years"]["2024"]
        
        if "Oslo" in year_data.get("offices", {}):
            oslo_data = year_data["offices"]["Oslo"]
            
            print(f"\n📊 OSLO RESULTS:")
            print("-" * 40)
            
            total_churn = 0
            total_recruitment = 0
            
            for role_name, role_data in oslo_data.get("levels", {}).items():
                for level_name, level_monthly_data in role_data.items():
                    if isinstance(level_monthly_data, list):
                        level_total_churn = sum(month.get("churn", 0) for month in level_monthly_data if isinstance(month, dict))
                        level_total_recruitment = sum(month.get("recruitment", 0) for month in level_monthly_data if isinstance(month, dict))
                        
                        total_churn += level_total_churn
                        total_recruitment += level_total_recruitment
                        
                        if level_total_churn > 0 or level_total_recruitment > 0:
                            print(f"{level_name}: {level_total_recruitment} recruitment, {level_total_churn} churn")
            
            print(f"TOTAL: {total_recruitment} recruitment, {total_churn} churn")
            
            if total_churn == 48:
                print("✅ SUCCESS: Oslo gets correct churn with explicit values")
            elif total_churn == 0:
                print("❌ CRITICAL: Oslo STILL gets 0 churn even with explicit values!")
                print("This indicates a fundamental issue with the simulation engine")
            else:
                print(f"❌ PARTIAL: Oslo gets {total_churn} churn instead of expected 48")
        else:
            print("❌ Oslo not found in results")
    else:
        print("❌ No 2024 results found")

def main():
    """Run the Oslo only test."""
    test_oslo_only()

if __name__ == "__main__":
    main()