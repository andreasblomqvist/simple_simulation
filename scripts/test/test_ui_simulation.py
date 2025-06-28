#!/usr/bin/env python3
"""
Test script to debug UI simulation issue
"""

import requests
import json

def test_ui_simulation():
    """Test the simulation API with UI parameters"""
    
    # Parameters that the UI would send
    simulation_params = {
        "start_year": 2025,
        "start_month": 1,
        "end_year": 2025,
        "end_month": 12,
        "price_increase": 0.02,
        "salary_increase": 0.02,
        "unplanned_absence": 0.05,
        "hy_working_hours": 166.4,
        "other_expense": 19000000.0,
        "employment_cost_rate": 0.40
    }
    
    print("🚀 Testing UI simulation with parameters:")
    print(json.dumps(simulation_params, indent=2))
    
    try:
        # Call the simulation API
        response = requests.post(
            "http://localhost:8000/simulation/run",
            json=simulation_params,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Simulation successful!")
            print(f"📋 Result keys: {list(result.keys())}")
            
            if 'years' in result:
                years = result['years']
                print(f"📅 Years available: {list(years.keys())}")
                
                # Check first year data
                first_year = list(years.keys())[0]
                year_data = years[first_year]
                print(f"📊 First year data keys: {list(year_data.keys())}")
                
                # Check offices data
                if 'offices' in year_data:
                    offices = year_data['offices']
                    print(f"🏢 Offices in simulation: {list(offices.keys())}")
                    
                    # Check first office data
                    if offices:
                        first_office = list(offices.keys())[0]
                        office_data = offices[first_office]
                        print(f"🏢 First office ({first_office}) data: {list(office_data.keys())}")
                        
                        if 'levels' in office_data:
                            levels = office_data['levels']
                            print(f"📈 Levels in {first_office}: {list(levels.keys())}")
                            
                            # Check Consultant levels
                            if 'Consultant' in levels:
                                consultant_levels = levels['Consultant']
                                print(f"👥 Consultant levels: {list(consultant_levels.keys())}")
                                
                                # Check first level data
                                if consultant_levels:
                                    first_level = list(consultant_levels.keys())[0]
                                    level_data = consultant_levels[first_level]
                                    print(f"📊 Level {first_level} data type: {type(level_data)}")
                                    if isinstance(level_data, list) and level_data:
                                        print(f"📊 Level {first_level} first month data: {level_data[0]}")
                
                # Check KPIs
                if 'kpis' in year_data:
                    kpis = year_data['kpis']
                    print(f"📊 KPI keys: {list(kpis.keys())}")
                    
                    if 'financial' in kpis:
                        financial = kpis['financial']
                        print(f"💰 Financial KPIs: {financial}")
                    
                    if 'growth' in kpis:
                        growth = kpis['growth']
                        print(f"📈 Growth KPIs: {growth}")
                
                # Check total FTE
                if 'total_fte' in year_data:
                    print(f"👥 Total FTE: {year_data['total_fte']}")
                
            else:
                print("❌ No 'years' field in response!")
                print(f"🔍 Full response structure: {json.dumps(result, indent=2)[:1000]}...")
        else:
            print(f"❌ Simulation failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ui_simulation() 