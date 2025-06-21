#!/usr/bin/env python3

import requests
import json

def test_ebitda_calculation():
    """Test to debug EBITDA calculation discrepancy"""
    
    print("🔍 EBITDA CALCULATION DEBUG")
    print("=" * 50)
    
    # Run a simple simulation
    payload = {
        "start_year": 2025,
        "start_month": 1,
        "end_year": 2025,
        "end_month": 1,
        "price_increase": 0.0,
        "salary_increase": 0.0,
        "hy_working_hours": 166.4,
        "unplanned_absence": 0.0,
        "other_expense": 20000000,
        "office_overrides": {}
    }
    
    try:
        response = requests.post("http://localhost:8000/simulation/run", json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Extract financial data
        overall_kpis = data['kpis']['financial']
        yearly_kpis = data['years']['2025']['kpis']['financial']
        
        print("\n📊 FINANCIAL KPI COMPARISON")
        print("-" * 30)
        print(f"{'Metric':<20} {'Overall KPIs':<15} {'Yearly KPIs':<15} {'Difference':<15}")
        print("-" * 65)
        
        net_sales_overall = overall_kpis['current_net_sales']
        net_sales_yearly = yearly_kpis['net_sales']
        net_sales_diff = net_sales_yearly - net_sales_overall
        
        ebitda_overall = overall_kpis['current_ebitda']
        ebitda_yearly = yearly_kpis['ebitda']
        ebitda_diff = ebitda_yearly - ebitda_overall
        
        margin_overall = overall_kpis['current_margin']
        margin_yearly = yearly_kpis['margin']
        margin_diff = margin_yearly - margin_overall
        
        print(f"{'Net Sales (M SEK)':<20} {net_sales_overall/1e6:<15.1f} {net_sales_yearly/1e6:<15.1f} {net_sales_diff/1e6:<15.1f}")
        print(f"{'EBITDA (M SEK)':<20} {ebitda_overall/1e6:<15.1f} {ebitda_yearly/1e6:<15.1f} {ebitda_diff/1e6:<15.1f}")
        print(f"{'Margin (%)':<20} {margin_overall:<15.1f} {margin_yearly:<15.1f} {margin_diff:<15.1f}")
        
        # Calculate implied costs
        costs_overall = net_sales_overall - ebitda_overall
        costs_yearly = net_sales_yearly - ebitda_yearly
        costs_diff = costs_yearly - costs_overall
        
        print(f"{'Implied Costs (M)':<20} {costs_overall/1e6:<15.1f} {costs_yearly/1e6:<15.1f} {costs_diff/1e6:<15.1f}")
        
        print("\n🔍 ANALYSIS")
        print("-" * 20)
        
        if abs(net_sales_diff) < 1000:  # Less than 1K SEK difference
            print("✅ Net Sales match - revenue calculation is correct")
        else:
            print(f"❌ Net Sales mismatch: {net_sales_diff:,.0f} SEK difference")
            
        if abs(ebitda_diff) < 1000000:  # Less than 1M SEK difference
            print("✅ EBITDA calculations match")
        else:
            print(f"❌ EBITDA mismatch: {ebitda_diff:,.0f} SEK difference")
            print(f"   This suggests a {costs_diff:,.0f} SEK difference in cost calculations")
            
        # Check if the difference is related to other expenses
        other_expense_annual = 20000000 * 12  # Annual other expenses
        if abs(costs_diff - other_expense_annual) < 1000000:
            print("🔍 Cost difference matches annual other expenses - possible double counting")
        
        print(f"\n💡 Key Insights:")
        print(f"   - Revenue calculation: {'✅ Consistent' if abs(net_sales_diff) < 1000 else '❌ Inconsistent'}")
        print(f"   - Cost calculation: {'✅ Consistent' if abs(costs_diff) < 1000000 else '❌ Inconsistent'}")
        print(f"   - Overall vs Yearly: {'✅ Match' if abs(ebitda_diff) < 1000000 else '❌ Different methods'}")
        
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_ebitda_calculation() 