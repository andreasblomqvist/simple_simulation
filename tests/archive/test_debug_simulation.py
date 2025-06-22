#!/usr/bin/env python3
"""
Test script to trigger a simulation and see debug output
"""

import requests
import json

def run_test_simulation():
    """Run a test simulation to see debug output"""
    
    # Simulation parameters with 2% price increase to test the debug logging
    params = {
        "start_year": 2025,
        "start_month": 1,
        "end_year": 2027,  # 3 years to see price increases
        "end_month": 12,
        "price_increase": 0.02,  # 2% price increase (correct format)
        "salary_increase": 0.02,  # 2% salary increase
        "hy_working_hours": 166.4,
        "unplanned_absence": 0.05,  # 5% unplanned absence
        "other_expense": 19000000,  # 19M SEK monthly
        "office_overrides": {}
    }
    
    print("🚀 Testing simulation with debug logging...")
    print(f"Parameters: {json.dumps(params, indent=2)}")
    
    try:
        # Send simulation request
        response = requests.post(
            "http://localhost:8000/simulation/run",
            json=params,
            timeout=60
        )
        
        if response.status_code == 200:
            results = response.json()
            print("✅ Simulation completed successfully!")
            
            # Show basic results
            if 'kpis' in results and 'financial' in results['kpis']:
                financial = results['kpis']['financial']
                print(f"\n📊 Financial Results:")
                print(f"   Net Sales: {financial.get('net_sales', 0):,.0f} SEK")
                print(f"   EBITDA: {financial.get('ebitda', 0):,.0f} SEK")
                print(f"   Margin: {financial.get('margin', 0):.1f}%")
                print(f"   Avg Hourly Rate: {financial.get('avg_hourly_rate', 0):.2f} SEK/hr")
            
            print(f"\n📝 Check the backend logs for detailed debug output:")
            print(f"   tail -f logs/backend.log | grep -E '(DEBUG|REVENUE|COSTS|PROFIT|KPI|PRICE UPDATE)'")
            
        else:
            print(f"❌ Simulation failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error running simulation: {e}")

if __name__ == "__main__":
    run_test_simulation()
