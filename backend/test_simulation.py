#!/usr/bin/env python3
"""
Simple test script to verify the simulation API is working correctly.
"""

import requests
import json
import time

def test_simulation_api():
    """Test the simulation API endpoint"""
    
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
    
    print("🧪 Testing Simulation API...")
    print(f"📊 Test Parameters:")
    print(f"   📅 Period: {test_data['start_year']}-{test_data['start_month']:02d} to {test_data['end_year']}-{test_data['end_month']:02d}")
    print(f"   💰 Price Increase: {test_data['price_increase']:.1%}")
    print(f"   💵 Salary Increase: {test_data['salary_increase']:.1%}")
    print()
    
    try:
        # Make the API call
        print("\U0001F680 Making API request to /api/simulation/run...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:8000/simulation/run",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\u23F1\uFE0F  Request completed in {duration:.2f} seconds")
        print(f"\U0001F4E1 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("\u2705 Simulation completed successfully!")
            
            # Parse the response
            result = response.json()
            
            # Check for key data structures
            if 'yearly_results' in result:
                yearly_data = result['yearly_results']
                print(f"📈 Found {len(yearly_data)} years of data")
                
                # Check FTE growth
                for year, year_data in yearly_data.items():
                    if 'office_aggregates' in year_data:
                        total_fte = year_data['office_aggregates'].get('total_fte', 0)
                        print(f"   📊 {year}: Total FTE = {total_fte:,.0f}")
                
                # Check if FTE is growing
                years = list(yearly_data.keys())
                if len(years) >= 2:
                    first_year_fte = yearly_data[years[0]]['office_aggregates'].get('total_fte', 0)
                    last_year_fte = yearly_data[years[-1]]['office_aggregates'].get('total_fte', 0)
                    
                    if last_year_fte > first_year_fte:
                        growth_rate = ((last_year_fte - first_year_fte) / first_year_fte) * 100
                        print(f"🎉 FTE Growth: {first_year_fte:,.0f} → {last_year_fte:,.0f} (+{growth_rate:.1f}%)")
                    else:
                        print(f"⚠️  FTE Growth: {first_year_fte:,.0f} → {last_year_fte:,.0f} (No growth)")
            
            if 'monthly_office_metrics' in result:
                monthly_data = result['monthly_office_metrics']
                print(f"📅 Found {len(monthly_data)} months of data")
            
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
            else:
                print("No yearly breakdown found in response.")
            
            print("\nFull response (first 1000 chars):")
            print(json.dumps(result, indent=2)[:1000] + "..." if len(json.dumps(result)) > 1000 else json.dumps(result, indent=2))
            
            print("\u2705 Test completed successfully!")
            return True
            
        else:
            print(f"\u274C Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the backend server is running on http://localhost:8000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Simulation took too long to complete")
        return False
    except Exception as e:
        print(f"\u274C Request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_simulation_api()
    exit(0 if success else 1) 