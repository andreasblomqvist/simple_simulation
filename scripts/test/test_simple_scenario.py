#!/usr/bin/env python3
"""
Test script to verify a simple scenario runs correctly with absolute recruitment and churn values.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend/src')))

import requests
import json

def test_simple_scenario():
    """Test a simple scenario with absolute recruitment and churn values."""
    
    # Simple scenario definition with absolute values
    scenario_definition = {
        "name": "Absolute Values Test",
        "description": "Test scenario with absolute recruitment and churn values",
        "time_range": {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 2
        },
        "office_scope": ["Stockholm"],
        "levers": {},
        "economic_params": {
            "employment_cost_rate": 0.4,
            "other_expense": 19000000.0,
            "unplanned_absence": 0.05,
            "utilization": 0.85
        },
        "baseline_input": {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "New Office",
                "roles": {
                    "Consultant": {
                        "A": {
                            "fte": 100.0,
                            "price_1": 1200.0,
                            "price_2": 1200.0,
                            "salary_1": 80000.0,
                            "salary_2": 80000.0,
                            "utr_1": 0.85,
                            "utr_2": 0.85,
                            # Absolute recruitment and churn values
                            "recruitment_abs_1": 5,
                            "recruitment_abs_2": 5,
                            "churn_abs_1": 2,
                            "churn_abs_2": 2
                        }
                    }
                }
            }
        },
        "progression_config": {
            "A": {
                "journey": "Journey 1",
                "progression_months": [6],
                "time_on_level": 6
            }
        },
        "cat_curves": {
            "A": {
                "CAT6": 0.1,
                "CAT12": 0.15,
                "CAT18": 0.2,
                "CAT24": 0.25,
                "CAT30": 0.3
            }
        }
    }
    
    print("Testing simple scenario with absolute values...")
    
    try:
        # Send request to the backend
        response = requests.post(
            "http://localhost:8000/scenarios/run",
            json={"scenario_definition": scenario_definition},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Scenario executed successfully!")
            
            # Extract FTE information
            if "results" in result and "years" in result["results"]:
                year_2025 = result["results"]["years"]["2025"]
                if "offices" in year_2025 and "Stockholm" in year_2025["offices"]:
                    stockholm = year_2025["offices"]["Stockholm"]
                    total_fte = stockholm.get("total_fte", 0)
                    print(f"Stockholm total FTE: {total_fte}")
                    
                    # Check if roles data exists
                    if "roles" in stockholm and "Consultant" in stockholm["roles"]:
                        consultant_data = stockholm["roles"]["Consultant"]["A"]
                        if len(consultant_data) >= 2:
                            month_1_data = consultant_data[0]
                            month_2_data = consultant_data[1]
                            
                            print(f"Month 1 FTE: {month_1_data.get('fte', 'N/A')}")
                            print(f"Month 2 FTE: {month_2_data.get('fte', 'N/A')}")
                            print(f"Month 1 recruitment: {month_1_data.get('recruitment', 'N/A')}")
                            print(f"Month 1 churn: {month_1_data.get('churn', 'N/A')}")
                            
                            # Verify that recruitment and churn are being applied
                            if month_1_data.get('fte', 0) > 0:
                                print("✅ FTE data is being calculated correctly!")
                            else:
                                print("⚠️  FTE data shows 0 - may need investigation")
                        else:
                            print("⚠️  Not enough monthly data in results")
                    else:
                        print("⚠️  No roles data found in results")
                else:
                    print("⚠️  No Stockholm office data found in results")
            else:
                print("⚠️  No results data found in response")
                
        else:
            print(f"❌ Scenario execution failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"❌ Error during scenario execution: {e}")

if __name__ == "__main__":
    test_simple_scenario() 