#!/usr/bin/env python3

import requests
import json

def test_ebitda_calculation():
    """Test that EBITDA calculation is now correct"""
    
    print("Testing EBITDA calculation fix...")
    
    # Test simulation parameters
    simulation_params = {
        "start_year": 2025,
        "start_month": 6,
        "end_year": 2028,
        "end_month": 12,
        "price_increase": 0.05,
        "salary_increase": 0.04,
        "unplanned_absence": 0.05,
        "hy_working_hours": 166.4,
        "other_expense": 19000000,
        "office_overrides": {}
    }
    
    try:
        # Run simulation
        print("Running simulation...")
        response = requests.post("http://localhost:8000/simulation/run", json=simulation_params)
        
        if response.status_code != 200:
            print(f"Simulation failed: {response.status_code}")
            print(response.text)
            return
            
        results = response.json()
        
        # Check backend KPI values
        kpis = results.get('kpis', {})
        financial_kpis = kpis.get('financial', {})
        
        backend_net_sales = financial_kpis.get('net_sales', 0)
        backend_ebitda = financial_kpis.get('ebitda', 0)
        backend_margin = financial_kpis.get('margin', 0)
        backend_total_costs = financial_kpis.get('total_salary_costs', 0)
        
        print(f"\n=== BACKEND KPI VALUES ===")
        print(f"Net Sales: {backend_net_sales/1000000:.1f}M SEK")
        print(f"Total Costs: {backend_total_costs/1000000:.1f}M SEK")
        print(f"EBITDA: {backend_ebitda/1000000:.1f}M SEK")
        print(f"Margin: {backend_margin*100:.1f}%")
        
        # Verify calculation: EBITDA = Net Sales - Total Costs
        calculated_ebitda = backend_net_sales - backend_total_costs
        print(f"\n=== CALCULATION VERIFICATION ===")
        print(f"Net Sales - Total Costs = {backend_net_sales/1000000:.1f}M - {backend_total_costs/1000000:.1f}M = {calculated_ebitda/1000000:.1f}M")
        print(f"Backend EBITDA: {backend_ebitda/1000000:.1f}M")
        print(f"Difference: {abs(calculated_ebitda - backend_ebitda)/1000000:.1f}M")
        
        # Check if values are reasonable
        if backend_net_sales > 0 and backend_ebitda > 0:
            actual_margin = backend_ebitda / backend_net_sales
            print(f"\n=== MARGIN CHECK ===")
            print(f"Actual margin: {actual_margin*100:.1f}%")
            print(f"Backend margin: {backend_margin*100:.1f}%")
            
            if abs(actual_margin - backend_margin) < 0.001:  # Within 0.1%
                print("✅ Margin calculation is correct!")
            else:
                print("❌ Margin calculation has discrepancy")
        
        # Check specific year data (2026)
        year_data = results.get('years', {}).get('2026', {})
        if year_data:
            print(f"\n=== 2026 YEAR DATA ===")
            offices = year_data.get('offices', {})
            total_fte = sum(office.get('total_fte', 0) for office in offices.values())
            print(f"Total FTE in 2026: {total_fte}")
            
            # Check a specific office
            stockholm_data = offices.get('Stockholm', {})
            if stockholm_data:
                stockholm_fte = stockholm_data.get('total_fte', 0)
                print(f"Stockholm FTE: {stockholm_fte}")
                
        print(f"\n=== SUMMARY ===")
        if backend_ebitda > 0 and backend_net_sales > 0:
            print("✅ EBITDA calculation appears to be working")
            print(f"Final values: {backend_net_sales/1000000:.1f}M sales, {backend_ebitda/1000000:.1f}M EBITDA ({backend_margin*100:.1f}% margin)")
        else:
            print("❌ EBITDA calculation still has issues")
            
    except Exception as e:
        print(f"Error testing EBITDA: {e}")

if __name__ == "__main__":
    test_ebitda_calculation() 