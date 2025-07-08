#!/usr/bin/env python3
"""
Test script to verify the frontend API endpoint (with /api/ prefix) is working correctly.
This tests the complete flow: frontend → Vite proxy → backend → response.
"""

import requests
import json
import time

def test_frontend_api():
    """Test the frontend API endpoint with /api/ prefix"""
    
    # Test data
    test_data = {
        "start_year": 2025,
        "start_month": 1,
        "end_year": 2027,
        "end_month": 12,
        "price_increase": 0.05,
        "salary_increase": 0.03,
        "unplanned_absence": 0.05,
        "hy_working_hours": 166.4,
        "other_expense": 19000000.0,
        "employment_cost_rate": 0.40,
        "office_overrides": {}
    }
    
    print("🧪 Testing Frontend API (with /api/ prefix)...")
    print(f"📊 Test Parameters:")
    print(f"   📅 Period: {test_data['start_year']}-{test_data['start_month']:02d} to {test_data['end_year']}-{test_data['end_month']:02d}")
    print(f"   💰 Price Increase: {test_data['price_increase']*100}%")
    print(f"   💵 Salary Increase: {test_data['salary_increase']*100}%")
    print(f"   🏥 Unplanned Absence: {test_data['unplanned_absence']*100}%")
    print(f"   ⏰ HY Working Hours: {test_data['hy_working_hours']}")
    print(f"   💸 Other Expense: {test_data['other_expense']:,.0f}")
    print(f"   📈 Employment Cost Rate: {test_data['employment_cost_rate']*100}%")
    
    print("\n🚀 Making API request to /api/simulation/run (frontend endpoint)...")
    try:
        response = requests.post(
            "http://localhost:3000/api/simulation/run",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return
    
    print(f"⏱️  Request completed in {response.elapsed.total_seconds():.2f} seconds")
    print(f"📡 Response Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Error: {response.text}")
        return
    
    print("✅ Frontend API simulation completed successfully!")
    
    try:
        result = response.json()
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON response: {e}")
        print(f"Raw response: {response.text[:500]}...")
        return
    
    # Print clear yearly and office FTE summary
    print("\n--- Yearly and Office FTE Summary (via Frontend API) ---")
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
    else:
        print("❌ No yearly breakdown found in response.")
        print("Response keys:", list(result.keys()) if isinstance(result, dict) else "Not a dict")
    
    print(f"\n📁 Result file: {result.get('result_file', 'Not specified')}")
    print("✅ Frontend API test completed successfully!")

if __name__ == "__main__":
    test_frontend_api() 