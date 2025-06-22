#!/usr/bin/env python3

import requests
import json

def debug_simulation_structure():
    """Debug script to examine simulation results structure."""
    
    payload = {
        "start_year": 2025,
        "start_month": 1,
        "end_year": 2025,
        "end_month": 3,
        "price_increase": 0.02,
        "salary_increase": 0.02,
        "unplanned_absence": 0.05,
        "hy_working_hours": 166.4,
        "other_expense": 19000000.0
    }
    
    try:
        response = requests.post("http://localhost:8000/simulation/run", json=payload)
        response.raise_for_status()
        data = response.json()
        
        print("🔍 Simulation Results Structure Analysis")
        print("=" * 60)
        
        years = data.get("years", {})
        if not years:
            print("❌ No 'years' key found in simulation results.")
            return False

        # Get the first year's data
        first_year_key = next(iter(years), None)
        if not first_year_key:
            print("❌ No year data found.")
            return False
            
        year_data = years[first_year_key]
        
        offices = year_data.get("offices", {})
        if not offices:
            print("❌ No 'offices' key found in year data.")
            return False

        # Get Stockholm office data
        stockholm_office = offices.get("Stockholm")
        if not stockholm_office:
            print("❌ No 'Stockholm' office data found.")
            return False

        office_levels = stockholm_office.get("levels", {})
        if not office_levels:
            print("❌ No 'levels' found in Stockholm office data.")
            return False

        # Get Consultant roles
        consultant_roles = office_levels.get("Consultant", {})
        if not consultant_roles:
            print("❌ No 'Consultant' role found.")
            return False

        # Get a specific level to inspect, e.g., 'A'
        level_to_inspect = "A"
        level_monthly_data = consultant_roles.get(level_to_inspect)

        if not isinstance(level_monthly_data, list) or not level_monthly_data:
            print(f"❌ No monthly data for Consultant/{level_to_inspect}.")
            return False

        # Inspect the keys of the first month's data record
        first_month_data = level_monthly_data[0]
        print(f"✅ Found data for Stockholm/Consultant/{level_to_inspect}.")
        print(f"📊 Keys for first month data: {list(first_month_data.keys())}")
        print("-" * 20)
        print("Sample month data:")
        print(json.dumps(first_month_data, indent=2))
        
        return True
        
    except Exception as e:
        import traceback
        print(f"❌ Error: {e}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    debug_simulation_structure() 