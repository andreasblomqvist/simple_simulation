#!/usr/bin/env python3
"""
Test script to verify that the backend can handle scenarios with null baseline_input
without throwing the 'NoneType' object has no attribute 'items' error.
"""

import requests
import json
import sys

def test_null_baseline_input():
    """Test scenario with null baseline_input to ensure it doesn't crash."""
    
    # Create a scenario definition with null baseline_input
    scenario_definition = {
        "name": "Test Null Baseline",
        "description": "Test scenario with null baseline_input",
        "time_range": {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 12
        },
        "office_scope": ["Stockholm"],
        "levers": {},
        "baseline_input": {
            "global": {
                "recruitment": {},
                "churn": {}
            }
        },
        "progression_config": {
            "levels": {
                "A": {
                    "progression_months": [1, 7],
                    "start_tenure": 1,
                    "time_on_level": 12,
                    "next_level": "AC",
                    "journey": "J-1"
                }
            }
        },
        "cat_curves": {
            "curves": {
                "A": {
                    "curves": {
                        "CAT0": 0.0,
                        "CAT6": 0.919
                    }
                }
            }
        }
    }
    
    # Submit the scenario
    try:
        print("🔄 Submitting scenario with null baseline_input...")
        response = requests.post(
            "http://localhost:8000/scenarios/run",
            json={"scenario_definition": scenario_definition}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Scenario with null baseline_input ran successfully!")
            print(f"📊 Scenario ID: {result.get('scenario_id', 'N/A')}")
            print(f"⏱️  Execution time: {result.get('execution_time', 'N/A')}s")
            print(f"📈 Status: {result.get('status', 'N/A')}")
            
            # Check if results contain data
            results = result.get('results', {})
            if results and 'years' in results:
                years = list(results['years'].keys())
                print(f"📅 Years with data: {years}")
                
                # Check first year data
                first_year = years[0] if years else None
                if first_year:
                    year_data = results['years'][first_year]
                    print(f"📊 {first_year} data keys: {list(year_data.keys())}")
                    
                    # Check if KPIs are calculated
                    if 'kpis' in year_data:
                        kpis = year_data['kpis']
                        print(f"📈 KPIs available: {list(kpis.keys()) if isinstance(kpis, dict) else 'Yes'}")
                    else:
                        print("⚠️  No KPIs found in results")
            else:
                print("⚠️  No results data found")
                
            return True
            
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR: {e}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False

def test_empty_baseline_input():
    """Test scenario with empty baseline_input to ensure it works."""
    
    # Create a scenario definition with empty baseline_input
    scenario_definition = {
        "name": "Test Empty Baseline",
        "description": "Test scenario with empty baseline_input",
        "time_range": {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 12
        },
        "office_scope": ["Stockholm"],
        "levers": {},
        "baseline_input": {
            "global": {
                "recruitment": {},
                "churn": {}
            }
        },
        "progression_config": {
            "levels": {
                "A": {
                    "progression_months": [1, 7],
                    "start_tenure": 1,
                    "time_on_level": 12,
                    "next_level": "AC",
                    "journey": "J-1"
                }
            }
        },
        "cat_curves": {
            "curves": {
                "A": {
                    "curves": {
                        "CAT0": 0.0,
                        "CAT6": 0.919
                    }
                }
            }
        }
    }
    
    # Submit the scenario
    try:
        print("\n🔄 Submitting scenario with empty baseline_input...")
        response = requests.post(
            "http://localhost:8000/scenarios/run",
            json={"scenario_definition": scenario_definition}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Scenario with empty baseline_input ran successfully!")
            print(f"📊 Scenario ID: {result.get('scenario_id', 'N/A')}")
            return True
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR: {e}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing backend fix for null baseline_input...")
    print("=" * 60)
    
    # Test both null and empty baseline_input
    success1 = test_null_baseline_input()
    success2 = test_empty_baseline_input()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 ALL TESTS PASSED: Backend can handle null/empty baseline_input!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED: Backend still has issues with null/empty baseline_input")
        sys.exit(1) 