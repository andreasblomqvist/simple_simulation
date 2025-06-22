#!/usr/bin/env python3
"""
Simple KPI debug script to trace EBITDA calculations
"""

import requests
import json

def debug_kpi_simple():
    """Debug KPI calculation with minimal simulation"""
    
    print("🔍 SIMPLE KPI DEBUG - Tracing EBITDA Calculation")
    print("=" * 60)
    
    # Run a very simple 1-month simulation to see calculations clearly
    payload = {
        "start_year": 2025,
        "start_month": 1,
        "end_year": 2025,
        "end_month": 1,  # Just 1 month
        "price_increase": 0.0,  # No increases
        "salary_increase": 0.0,  # No increases
        "unplanned_absence": 0.0,  # No absence for clarity
        "hy_working_hours": 166.4,
        "other_expense": 10000000.0  # 10M SEK/month for clarity
    }
    
    try:
        print("🔄 Running 1-month simulation with no increases...")
        response = requests.post("http://localhost:8000/simulation/run", json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Extract financial data
        kpis = data.get("kpis", {})
        financial = kpis.get("financial", {})
        
        print("\n📊 SIMPLIFIED RESULTS:")
        print(f"Current EBITDA: {financial.get('ebitda', 0):,.0f} SEK")
        print(f"Baseline EBITDA: {financial.get('ebitda_baseline', 0):,.0f} SEK")
        print(f"Current Revenue: {financial.get('net_sales', 0):,.0f} SEK")
        print(f"Baseline Revenue: {financial.get('net_sales_baseline', 0):,.0f} SEK")
        print(f"Current Costs: {financial.get('total_salary_costs', 0):,.0f} SEK")
        print(f"Baseline Costs: {financial.get('total_salary_costs_baseline', 0):,.0f} SEK")
        
        # Check if these numbers look reasonable for 1 month
        monthly_current_ebitda = financial.get('ebitda', 0) / 12  # Should be monthly
        monthly_baseline_ebitda = financial.get('ebitda_baseline', 0) / 12
        
        print(f"\n📅 MONTHLY EQUIVALENTS (if annualized):")
        print(f"Monthly Current EBITDA: {monthly_current_ebitda:,.0f} SEK")
        print(f"Monthly Baseline EBITDA: {monthly_baseline_ebitda:,.0f} SEK")
        
        # Look at the raw simulation data structure
        years = data.get("years", {})
        if "2025" in years:
            year_data = years["2025"]
            offices = year_data.get("offices", {})
            
            print(f"\n🏢 OFFICE COUNT: {len(offices)}")
            
            total_fte = 0
            for office_name, office_data in offices.items():
                office_fte = office_data.get('total_fte', 0)
                total_fte += office_fte
                print(f"  {office_name}: {office_fte} FTE")
            
            print(f"\n👥 TOTAL SYSTEM FTE: {total_fte}")
            
            # Check if the numbers are reasonable
            if total_fte > 0:
                revenue_per_fte = financial.get('net_sales', 0) / total_fte
                ebitda_per_fte = financial.get('ebitda', 0) / total_fte
                
                print(f"\n💰 PER-FTE ANALYSIS:")
                print(f"Revenue per FTE: {revenue_per_fte:,.0f} SEK/year")
                print(f"EBITDA per FTE: {ebitda_per_fte:,.0f} SEK/year")
                print(f"EBITDA margin: {financial.get('margin', 0):.1%}")
                
                # These should be reasonable numbers
                # Revenue per consultant should be around 1.5-2M SEK/year
                # EBITDA per FTE should be much lower
                
                if revenue_per_fte > 3000000:  # 3M SEK per FTE is very high
                    print("⚠️  WARNING: Revenue per FTE seems very high!")
                
                if ebitda_per_fte > 1000000:  # 1M SEK EBITDA per FTE is very high
                    print("⚠️  WARNING: EBITDA per FTE seems very high!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    debug_kpi_simple() 