#!/usr/bin/env python3
"""
Test script to compare single-year vs multi-year simulation results for 2025
This will help identify why 2025 shows different values in different simulation contexts
"""

import requests
import json

def test_single_vs_multi_year():
    """Compare single-year 2025 vs multi-year simulation 2025 results"""
    
    print("🔍 TESTING: Single-Year vs Multi-Year Simulation Results for 2025")
    print("=" * 70)
    
    # Base simulation parameters
    base_params = {
        "price_increase": 0.0,  # No price increase for baseline comparison
        "salary_increase": 0.0,  # No salary increase for baseline comparison
        "unplanned_absence": 0.05,
        "hy_working_hours": 166.4,
        "other_expense": 19000000.0
    }
    
    # Test 1: Single year 2025 simulation
    print("\n📊 Test 1: Single Year 2025 Simulation")
    print("-" * 40)
    
    single_year_params = {
        **base_params,
        "start_year": 2025,
        "start_month": 1,
        "end_year": 2025,
        "end_month": 12
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/simulation/run",
            json=single_year_params,
            timeout=60
        )
        response.raise_for_status()
        single_year_results = response.json()
        
        # Extract 2025 financial data
        single_year_2025 = single_year_results['years']['2025']
        single_kpis = single_year_results.get('kpis', {}).get('financial', {})
        
        print(f"✅ Single year simulation completed")
        print(f"   Revenue: {single_kpis.get('net_sales', 0):,.0f} SEK")
        print(f"   EBITDA: {single_kpis.get('ebitda', 0):,.0f} SEK")
        print(f"   Margin: {single_kpis.get('margin', 0):.2%}")
        print(f"   Consultants: {single_kpis.get('total_consultants', 0):,}")
        
    except Exception as e:
        print(f"❌ Single year simulation failed: {e}")
        return
    
    # Test 2: Multi-year simulation (2025-2027) and extract 2025 data
    print("\n📊 Test 2: Multi-Year 2025-2027 Simulation (extract 2025)")
    print("-" * 50)
    
    multi_year_params = {
        **base_params,
        "start_year": 2025,
        "start_month": 1,
        "end_year": 2027,
        "end_month": 12
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/simulation/run",
            json=multi_year_params,
            timeout=120
        )
        response.raise_for_status()
        multi_year_results = response.json()
        
        # Extract 2025 financial data from multi-year simulation
        multi_year_2025 = multi_year_results['years']['2025']
        multi_kpis = multi_year_results.get('kpis', {}).get('financial', {})
        
        print(f"✅ Multi-year simulation completed")
        print(f"   Revenue (final year): {multi_kpis.get('net_sales', 0):,.0f} SEK")
        print(f"   EBITDA (final year): {multi_kpis.get('ebitda', 0):,.0f} SEK")
        print(f"   Margin (final year): {multi_kpis.get('margin', 0):.2%}")
        print(f"   Consultants (final year): {multi_kpis.get('total_consultants', 0):,}")
        
        # Calculate year-specific KPIs for 2025 in multi-year simulation
        print(f"\n   Calculating 2025-specific KPIs from multi-year data...")
        
        # Get 2025-specific KPIs from the backend endpoint
        year_kpi_response = requests.get(
            f"http://localhost:8000/simulation/years/2025/kpis",
            timeout=30
        )
        
        if year_kpi_response.status_code == 200:
            year_2025_kpis = year_kpi_response.json().get('financial', {})
            print(f"   Revenue (2025 only): {year_2025_kpis.get('net_sales', 0):,.0f} SEK")
            print(f"   EBITDA (2025 only): {year_2025_kpis.get('ebitda', 0):,.0f} SEK")
            print(f"   Margin (2025 only): {year_2025_kpis.get('margin', 0):.2%}")
            print(f"   Consultants (2025 only): {year_2025_kpis.get('total_consultants', 0):,}")
        else:
            print(f"   ❌ Failed to get 2025-specific KPIs: {year_kpi_response.status_code}")
        
    except Exception as e:
        print(f"❌ Multi-year simulation failed: {e}")
        return
    
    # Test 3: Compare the results
    print("\n📊 Test 3: Comparison Analysis")
    print("-" * 30)
    
    single_revenue = single_kpis.get('net_sales', 0)
    multi_revenue = multi_kpis.get('net_sales', 0)
    
    single_ebitda = single_kpis.get('ebitda', 0)
    multi_ebitda = multi_kpis.get('ebitda', 0)
    
    single_consultants = single_kpis.get('total_consultants', 0)
    multi_consultants = multi_kpis.get('total_consultants', 0)
    
    if single_revenue > 0 and multi_revenue > 0:
        revenue_ratio = single_revenue / multi_revenue
        ebitda_ratio = single_ebitda / multi_ebitda if multi_ebitda > 0 else 0
        consultant_ratio = single_consultants / multi_consultants if multi_consultants > 0 else 0
        
        print(f"Revenue Ratio (Single/Multi): {revenue_ratio:.2f}x")
        print(f"EBITDA Ratio (Single/Multi): {ebitda_ratio:.2f}x")
        print(f"Consultant Ratio (Single/Multi): {consultant_ratio:.2f}x")
        
        if revenue_ratio > 1.1 or revenue_ratio < 0.9:
            print(f"\n⚠️  SIGNIFICANT DIFFERENCE DETECTED!")
            print(f"   Single-year 2025 revenue: {single_revenue:,.0f} SEK")
            print(f"   Multi-year 2025 revenue: {multi_revenue:,.0f} SEK")
            print(f"   Difference: {single_revenue - multi_revenue:,.0f} SEK ({(revenue_ratio-1)*100:.1f}%)")
            
            print(f"\n🔍 POSSIBLE CAUSES:")
            print(f"   1. State accumulation: Multi-year simulation may carry forward changes")
            print(f"   2. Baseline calculation: Different baselines for single vs multi-year")
            print(f"   3. KPI calculation: Different duration handling in KPI calculations")
            print(f"   4. Engine reset: Simulation engine may not reset properly between runs")
            
        else:
            print(f"\n✅ Results are reasonably consistent (within 10%)")
    else:
        print(f"\n❌ Cannot compare - missing data")
        print(f"   Single year revenue: {single_revenue}")
        print(f"   Multi year revenue: {multi_revenue}")

if __name__ == "__main__":
    test_single_vs_multi_year() 