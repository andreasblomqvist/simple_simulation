#!/usr/bin/env python3
"""
Debug to verify that absolute churn values are being set correctly.
"""
import json
import requests

def debug_absolute_values():
    """Check what absolute values are actually being set in the configuration."""
    
    print("🔍 DEBUGGING ABSOLUTE VALUES AFTER SCENARIO RESOLUTION")
    print("=" * 70)
    
    # Get the most recent scenario
    BASE_URL = "http://localhost:8000"
    response = requests.get(f"{BASE_URL}/scenarios/list")
    scenarios = response.json().get("scenarios", [])
    recent_scenario = sorted(scenarios, key=lambda x: x.get("created_at", ""), reverse=True)[0]
    
    scenario_id = recent_scenario["id"]
    print(f"📋 Scenario ID: {scenario_id}")
    
    # Try to get the resolved configuration from the backend
    # This might require adding an endpoint or debugging directly
    
    # For now, let's create a minimal test scenario and check the resolution
    print("\n🧪 CREATING MINIMAL TEST SCENARIO")
    
    minimal_scenario = {
        "name": "Absolute Values Debug",
        "description": "Test to verify absolute value setting",
        "time_range": {
            "start_year": 2024,
            "start_month": 1,
            "end_year": 2024,
            "end_month": 3  # Just 3 months
        },
        "office_scope": ["Oslo"],  # Just Oslo
        "baseline_input": {
            "global": {
                "churn": {
                    "Consultant": {
                        "levels": {
                            "A": {
                                "recruitment": {
                                    "values": {
                                        "202401": 0,
                                        "202402": 0,
                                        "202403": 0
                                    }
                                },
                                "churn": {
                                    "values": {
                                        "202401": 5,  # 5 people churn in January
                                        "202402": 5,  # 5 people churn in February  
                                        "202403": 5   # 5 people churn in March
                                    }
                                }
                            }
                        }
                    }
                },
                "recruitment": {
                    "Consultant": {
                        "levels": {
                            "A": {
                                "recruitment": {
                                    "values": {
                                        "202401": 3,  # 3 people recruited in January
                                        "202402": 3,  # 3 people recruited in February
                                        "202403": 3   # 3 people recruited in March
                                    }
                                },
                                "churn": {
                                    "values": {
                                        "202401": 0,
                                        "202402": 0,
                                        "202403": 0
                                    }
                                }
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
    
    print("📊 Test scenario: 5 churn, 3 recruitment for Oslo A level each month")
    print("📊 Oslo A level has 5 FTE initially")
    print("📊 Expected result: 3 recruitment, 5 churn each month (net -2)")
    
    # Run the scenario
    payload = {"scenario_definition": minimal_scenario}
    response = requests.post(f"{BASE_URL}/scenarios/run", json=payload)
    
    if response.status_code != 200:
        print(f"❌ Simulation failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    result = response.json()
    if result.get("status") != "success":
        print(f"❌ Simulation error: {result.get('error_message', 'Unknown error')}")
        return
    
    test_scenario_id = result.get('scenario_id')
    print(f"✅ Test simulation completed - ID: {test_scenario_id}")
    
    # Get results
    response = requests.get(f"{BASE_URL}/scenarios/{test_scenario_id}/results")
    result_data = response.json()
    results = result_data.get("results", {})
    
    if "years" in results and "2024" in results["years"]:
        year_data = results["years"]["2024"]
        
        if "Oslo" in year_data.get("offices", {}):
            oslo_data = year_data["offices"]["Oslo"]
            
            print(f"\n📊 OSLO A LEVEL RESULTS:")
            print("-" * 40)
            
            # Look at Consultant A level data
            if ("levels" in oslo_data and 
                "Consultant" in oslo_data["levels"] and 
                "A" in oslo_data["levels"]["Consultant"]):
                
                a_level_data = oslo_data["levels"]["Consultant"]["A"]
                
                if isinstance(a_level_data, list):
                    print(f"{'Month':<6} {'Rec':<5} {'Churn':<7} {'FTE':<5} {'Note'}")
                    print("-" * 40)
                    
                    for i, month_data in enumerate(a_level_data[:3], 1):  # First 3 months
                        if isinstance(month_data, dict):
                            rec = month_data.get("recruitment", 0)
                            churn = month_data.get("churn", 0)
                            fte = month_data.get("fte", 0)
                            
                            note = ""
                            if rec == 3 and churn == 5:
                                note = "✅ Correct"
                            elif churn == 0:
                                note = "❌ No churn"
                            else:
                                note = "❌ Wrong values"
                            
                            print(f"{i:<6} {rec:<5} {churn:<7} {fte:<5} {note}")
                    
                    # Summary
                    total_rec = sum(month.get("recruitment", 0) for month in a_level_data[:3] if isinstance(month, dict))
                    total_churn = sum(month.get("churn", 0) for month in a_level_data[:3] if isinstance(month, dict))
                    
                    print("-" * 40)
                    print(f"Total: {total_rec} recruitment, {total_churn} churn")
                    
                    if total_rec == 9 and total_churn == 15:
                        print("✅ SUCCESS: Absolute values are working correctly!")
                    elif total_churn == 0:
                        print("❌ FAILURE: Still getting 0 churn - absolute values not working")
                    else:
                        print("❌ FAILURE: Getting wrong values - calculation error")
                        
                else:
                    print("❌ A level data is not in expected list format")
            else:
                print("❌ Could not find Oslo Consultant A level data")
        else:
            print("❌ Oslo not found in results")
    else:
        print("❌ No 2024 results found")

def main():
    """Run the absolute values debug test."""
    debug_absolute_values()

if __name__ == "__main__":
    main()