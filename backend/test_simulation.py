#!/usr/bin/env python3
"""
Simple test script to verify the simulation API is working correctly.
Uses a specific scenario file for realistic testing.
"""

import requests
import json
import os

SCENARIO_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data", "scenarios", "definitions", "f5f26bc5-3830-4f64-ba53-03b58ae72353.json"
)

def load_scenario_file(file_path):
    """Load and parse a scenario file"""
    try:
        with open(file_path, 'r') as f:
            scenario = json.load(f)
        
        # Extract time range from scenario
        time_range = scenario.get('time_range', {})
        
        # Build the complete request data including scenario data
        test_data = {
            "start_year": time_range.get("start_year", 2025),
            "start_month": time_range.get("start_month", 1),
            "end_year": time_range.get("end_year", 2027),
            "end_month": time_range.get("end_month", 12),
            "price_increase": 0.05,  # Default values
            "salary_increase": 0.03,
            "unplanned_absence": 0.05,
            "hy_working_hours": 166.4,
            "other_expense": 19000000.0,
            "employment_cost_rate": 0.40,
            "office_overrides": {},
            # Include the scenario data for the scenario service
            "scenario_data": scenario
        }
        return test_data
    except Exception as e:
        print(f"Failed to load scenario file: {e}")
        return None

def test_simulation_api():
    """Test the simulation API endpoint using the specified scenario file"""
    test_data = load_scenario_file(SCENARIO_FILE)
    if not test_data:
        print("No valid scenario data found. Exiting.")
        return
    print(f"\U0001F4C4 Using scenario file: {SCENARIO_FILE}")
    print(f"\U0001F4DD Test Parameters: {json.dumps({k: v for k, v in test_data.items() if k != 'scenario_data'}, indent=2)}")
    print(f"\U0001F4DD Scenario data keys: {list(test_data['scenario_data'].keys())}")
    print("\U0001F680 Making API request to /simulation/run...")
    try:
        response = requests.post(
            "http://localhost:8000/simulation/run",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
    except Exception as e:
        print(f"\u274C Request failed: {e}")
        return
    print(f"\u23F1\uFE0F  Request completed in {response.elapsed.total_seconds():.2f} seconds")
    print(f"\U0001F4E1 Response Status: {response.status_code}")
    if response.status_code != 200:
        print(f"\u274C Error: {response.text}")
        return
    print("\u2705 Simulation completed successfully!")
    result = response.json()
    # Print simulation metadata
    print(f"\n--- Simulation Metadata ---")
    print(f"Result file: {result.get('result_file', 'N/A')}")
    if "kpis" in result:
        print(f"KPIs calculated: {len(result['kpis'])} metrics")
    # Print clear yearly and office FTE summary
    print("\n--- Yearly and Office FTE Summary ---")
    if "years" in result and isinstance(result["years"], dict):
        for year, year_data in result["years"].items():
            print(f"\nYear {year}:")
            offices = year_data.get("offices", {})
            year_total_fte = 0
            for office_name, office_data in offices.items():
                office_fte = office_data.get("total_fte", 0)
                year_total_fte += office_fte
                print(f"   - {office_name}: {office_fte} FTE")
            print(f"   Total FTE for {year}: {year_total_fte}")
    # Print global recruitment and churn data if available
    print("\n--- Global Recruitment and Churn Data ---")
    if "years" in result and isinstance(result["years"], dict):
        for year, year_data in result["years"].items():
            print(f"\nYear {year}:")
            if "global_level_stats" in year_data:
                for month, month_stats in year_data["global_level_stats"].items():
                    print(f"  Month {month}:")
                    for level, stats in month_stats.items():
                        rec = stats.get("recruitment", 0)
                        churn = stats.get("churn", 0)
                        print(f"    {level}: Recruitment={rec}, Churn={churn}")
            else:
                print("  No global_level_stats found for this year.")
    # Debug: Print response structure
    print(f"\n--- Response Structure Debug ---")
    print(f"Top-level keys: {list(result.keys())}")
    if "years" in result:
        first_year = list(result["years"].keys())[0] if result["years"] else None
        if first_year:
            year_data = result["years"][first_year]
            print(f"Year {first_year} keys: {list(year_data.keys())}")
            if "offices" in year_data:
                first_office = list(year_data["offices"].keys())[0] if year_data["offices"] else None
                if first_office:
                    print(f"Office {first_office} keys: {list(year_data['offices'][first_office].keys())}")

if __name__ == "__main__":
    test_simulation_api() 