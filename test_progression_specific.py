#!/usr/bin/env python3
"""
Test progression specifically to understand why it's showing as zero.
"""
import json
import requests

BASE_URL = "http://localhost:8000"

def create_progression_test_scenario():
    """Create a scenario designed to trigger progression."""
    
    # Create a scenario with high progression levers to force progression
    scenario = {
        "name": "Progression Test Scenario",
        "description": "Test scenario to verify progression is working",
        "time_range": {
            "start_year": 2024,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 12
        },
        "office_scope": ["Stockholm"],
        "baseline_input": {
            "global": {
                "recruitment": {
                    "Consultant": {
                        "levels": {
                            "A": {
                                "recruitment": {"values": {f"2024{m:02d}": 5 for m in range(1, 13)} | {f"2025{m:02d}": 5 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 1 for m in range(1, 13)} | {f"2025{m:02d}": 1 for m in range(1, 13)}}
                            },
                            "AC": {
                                "recruitment": {"values": {f"2024{m:02d}": 3 for m in range(1, 13)} | {f"2025{m:02d}": 3 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 1 for m in range(1, 13)} | {f"2025{m:02d}": 1 for m in range(1, 13)}}
                            },
                            "C": {
                                "recruitment": {"values": {f"2024{m:02d}": 2 for m in range(1, 13)} | {f"2025{m:02d}": 2 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)} | {f"2025{m:02d}": 0 for m in range(1, 13)}}
                            },
                            "SrC": {
                                "recruitment": {"values": {f"2024{m:02d}": 1 for m in range(1, 13)} | {f"2025{m:02d}": 1 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)} | {f"2025{m:02d}": 0 for m in range(1, 13)}}
                            },
                            "AM": {
                                "recruitment": {"values": {f"2024{m:02d}": 1 for m in range(1, 13)} | {f"2025{m:02d}": 1 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)} | {f"2025{m:02d}": 0 for m in range(1, 13)}}
                            },
                            "M": {
                                "recruitment": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)} | {f"2025{m:02d}": 0 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)} | {f"2025{m:02d}": 0 for m in range(1, 13)}}
                            },
                            "SrM": {
                                "recruitment": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)} | {f"2025{m:02d}": 0 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)} | {f"2025{m:02d}": 0 for m in range(1, 13)}}
                            },
                            "Pi": {
                                "recruitment": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)} | {f"2025{m:02d}": 0 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)} | {f"2025{m:02d}": 0 for m in range(1, 13)}}
                            },
                            "P": {
                                "recruitment": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)} | {f"2025{m:02d}": 0 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)} | {f"2025{m:02d}": 0 for m in range(1, 13)}}
                            }
                        }
                    }
                },
                "churn": {
                    "Consultant": {
                        "levels": {
                            "A": {
                                "recruitment": {"values": {f"2024{m:02d}": 5 for m in range(1, 13)} | {f"2025{m:02d}": 5 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 1 for m in range(1, 13)} | {f"2025{m:02d}": 1 for m in range(1, 13)}}
                            },
                            "AC": {
                                "recruitment": {"values": {f"2024{m:02d}": 3 for m in range(1, 13)} | {f"2025{m:02d}": 3 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 1 for m in range(1, 13)} | {f"2025{m:02d}": 1 for m in range(1, 13)}}
                            },
                            "C": {
                                "recruitment": {"values": {f"2024{m:02d}": 2 for m in range(1, 13)} | {f"2025{m:02d}": 2 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)} | {f"2025{m:02d}": 0 for m in range(1, 13)}}
                            },
                            "AC": {
                                "recruitment": {"values": {f"2024{m:02d}": 1 for m in range(1, 13)} | {f"2025{m:02d}": 1 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)} | {f"2025{m:02d}": 0 for m in range(1, 13)}}
                            },
                            "AM": {
                                "recruitment": {"values": {f"2024{m:02d}": 1 for m in range(1, 13)} | {f"2025{m:02d}": 1 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)} | {f"2025{m:02d}": 0 for m in range(1, 13)}}
                            },
                            "M": {
                                "recruitment": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)} | {f"2025{m:02d}": 0 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)} | {f"2025{m:02d}": 0 for m in range(1, 13)}}
                            },
                            "SrM": {
                                "recruitment": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)} | {f"2025{m:02d}": 0 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)} | {f"2025{m:02d}": 0 for m in range(1, 13)}}
                            },
                            "Pi": {
                                "recruitment": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)} | {f"2025{m:02d}": 0 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)} | {f"2025{m:02d}": 0 for m in range(1, 13)}}
                            },
                            "P": {
                                "recruitment": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)} | {f"2025{m:02d}": 0 for m in range(1, 13)}},
                                "churn": {"values": {f"2024{m:02d}": 0 for m in range(1, 13)} | {f"2025{m:02d}": 0 for m in range(1, 13)}}
                            }
                        }
                    }
                }
            }
        },
        "levers": {
            "recruitment": {"A": 1.0, "AC": 1.0, "C": 1.0, "SrC": 1.0, "AM": 1.0, "M": 1.0, "SrM": 1.0, "Pi": 1.0, "P": 1.0},
            "churn": {"A": 1.0, "AC": 1.0, "C": 1.0, "SrC": 1.0, "AM": 1.0, "M": 1.0, "SrM": 1.0, "Pi": 1.0, "P": 1.0},
            "progression": {"A": 3.0, "AC": 3.0, "C": 3.0, "SrC": 3.0, "AM": 3.0, "M": 3.0, "SrM": 3.0, "Pi": 3.0, "P": 3.0}  # High progression multipliers
        },
        "progression_config": None,
        "cat_curves": None
    }
    
    return scenario

def run_progression_test():
    """Run the progression test scenario."""
    
    print("🔄 Running progression test scenario...")
    
    scenario = create_progression_test_scenario()
    payload = {"scenario_definition": scenario}
    
    response = requests.post(f"{BASE_URL}/scenarios/run", json=payload)
    
    if response.status_code != 200:
        print(f"❌ Simulation failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    
    result = response.json()
    if result.get("status") != "success":
        print(f"❌ Simulation error: {result.get('error_message', 'Unknown error')}")
        return None
    
    print(f"✅ Simulation completed in {result.get('execution_time', 0):.2f}s")
    return result

def analyze_progression_results(result):
    """Analyze the results specifically for progression."""
    
    if not result or not result.get("results"):
        print("❌ No results data found")
        return
    
    scenario_id = result.get("scenario_id")
    print(f"📋 Analyzing scenario: {scenario_id}")
    
    results_data = result["results"]
    total_progression = 0
    month_progression = {}
    level_progression = {}
    
    # Navigate through years → offices → levels → roles → monthly data
    for year, year_data in results_data.get("years", {}).items():
        for office_name, office_data in year_data.get("offices", {}).items():
            for role_name, role_data in office_data.get("levels", {}).items():
                for level_name, level_monthly_data in role_data.items():
                    if isinstance(level_monthly_data, list):
                        for month_idx, month_data in enumerate(level_monthly_data):
                            if isinstance(month_data, dict):
                                progression = month_data.get("promoted_people", 0)
                                
                                if progression > 0:
                                    total_progression += progression
                                    month_key = f"{year}-{month_idx+1:02d}"
                                    month_progression[month_key] = month_progression.get(month_key, 0) + progression
                                    level_progression[level_name] = level_progression.get(level_name, 0) + progression
                                    
                                    print(f"🎯 Found progression: {year}/{office_name}/{role_name}/{level_name}/month{month_idx+1}: {progression}")
    
    print(f"\n📊 Progression Analysis:")
    print(f"   Total progression across all periods: {total_progression}")
    
    if month_progression:
        print(f"   Progression by month:")
        for month, prog in sorted(month_progression.items()):
            print(f"      {month}: {prog}")
    else:
        print(f"   No progression found in any month")
    
    if level_progression:
        print(f"   Progression by level:")
        for level, prog in sorted(level_progression.items()):
            print(f"      {level}: {prog}")
    else:
        print(f"   No progression found in any level")
    
    # Let's also check what the simulation engine thinks about progression configuration
    print(f"\n🔍 Detailed progression investigation:")
    
    # Fetch the full results to examine what happened
    if scenario_id:
        response = requests.get(f"{BASE_URL}/scenarios/{scenario_id}/results")
        if response.status_code == 200:
            full_results = response.json()
            print(f"   Fetched full results for detailed analysis")
            
            # Look at a few sample months for A level to see what's happening
            sample_results = full_results.get("results", {}).get("years", {}).get("2024", {}).get("offices", {}).get("Stockholm", {}).get("levels", {}).get("Consultant", {}).get("A", [])
            if sample_results:
                print(f"   Sample A-level data (first 3 months):")
                for i, month_data in enumerate(sample_results[:3]):
                    print(f"      Month {i+1}: FTE={month_data.get('fte', 0)}, Recruitment={month_data.get('recruitment', 0)}, Churn={month_data.get('churn', 0)}, Progression={month_data.get('promoted_people', 0)}")
            else:
                print(f"   No A-level sample data found")
        else:
            print(f"   Failed to fetch full results: {response.status_code}")
    
    if total_progression == 0:
        print(f"\n⚠️  ISSUE: No progression detected despite high progression levers")
        print(f"   This suggests either:")
        print(f"   1. Progression config is not properly loaded/applied")
        print(f"   2. People don't have sufficient tenure for progression")
        print(f"   3. Progression calculation has a bug")
        print(f"   4. Progression months don't align with simulation timing")
    else:
        print(f"\n✅ Progression is working correctly!")

def main():
    """Run progression-specific test."""
    print("🎯 Testing progression functionality specifically")
    print("=" * 60)
    
    result = run_progression_test()
    if result:
        analyze_progression_results(result)
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()