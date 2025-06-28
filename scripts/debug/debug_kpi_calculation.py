#!/usr/bin/env python3
"""
Debug script to test KPI calculation and see EBITDA values
"""

import requests
import json

def debug_kpi_calculation():
    """Debug KPI calculation to see EBITDA values"""
    
    print("=== Debugging KPI Calculation ===\n")
    
    # Run a simulation
    payload = {
        "start_year": 2025,
        "start_month": 1,
        "end_year": 2025,
        "end_month": 12,
        "price_increase": 0.02,
        "salary_increase": 0.02,
        "unplanned_absence": 0.05,
        "hy_working_hours": 166.4,
        "other_expense": 19000000.0
    }
    
    try:
        print("🔄 Running simulation...")
        response = requests.post("http://localhost:8000/simulation/run", json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Extract KPI data
        kpis = data.get("kpis", {})
        financial = kpis.get("financial", {})
        
        print("📊 KPI Results:")
        print(f"  Current EBITDA: {financial.get('ebitda', 0):,.0f} SEK")
        print(f"  Baseline EBITDA: {financial.get('ebitda_baseline', 0):,.0f} SEK")
        print(f"  Current Net Sales: {financial.get('net_sales', 0):,.0f} SEK")
        print(f"  Baseline Net Sales: {financial.get('net_sales_baseline', 0):,.0f} SEK")
        print(f"  Current Margin: {financial.get('margin', 0):.2%}")
        print(f"  Baseline Margin: {financial.get('margin_baseline', 0):.2%}")
        
        # Check if there are multiple years
        years = data.get("years", {})
        print(f"\n📅 Available years: {list(years.keys())}")
        
        # Look at the final year data structure
        if years:
            final_year = max(years.keys())
            final_year_data = years[final_year]
            print(f"\n🔍 Final year ({final_year}) structure:")
            print(f"  Offices: {list(final_year_data.get('offices', {}).keys())}")
            
            # Check Stockholm office data
            stockholm = final_year_data.get('offices', {}).get('Stockholm', {})
            if stockholm:
                print(f"  Stockholm total_fte: {stockholm.get('total_fte', 0)}")
                print(f"  Stockholm has 'levels': {'levels' in stockholm}")
                print(f"  Stockholm has 'roles': {'roles' in stockholm}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    debug_kpi_calculation() 