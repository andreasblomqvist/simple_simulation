#!/usr/bin/env python3

import requests
import json

def test_ebitda():
    """Test the current EBITDA calculation"""
    
    # Test the simulation endpoint
    url = "http://localhost:8000/simulation/run"
    payload = {
        "simulation_duration_months": 36,
        "start_year": 2025,
        "start_month": 1,
        "end_year": 2027,
        "end_month": 12,
        "price_increase": 0.0,
        "salary_increase": 0.0,
        "levers": {}
    }
    
    try:
        print("🔍 Testing EBITDA calculation...")
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract KPI data
            kpis = data.get('kpis', {})
            financial = kpis.get('financial', {})
            
            current_ebitda = financial.get('ebitda', 0)
            baseline_ebitda = financial.get('ebitda_baseline', 0)
            current_revenue = financial.get('net_sales', 0)
            baseline_revenue = financial.get('net_sales_baseline', 0)
            current_costs = financial.get('total_salary_costs', 0)
            baseline_costs = financial.get('total_salary_costs_baseline', 0)
            
            print(f"\n📊 CURRENT FINANCIAL RESULTS:")
            print(f"   Current EBITDA: {current_ebitda:,.0f} SEK")
            print(f"   Baseline EBITDA: {baseline_ebitda:,.0f} SEK")
            print(f"   Current Revenue: {current_revenue:,.0f} SEK")
            print(f"   Baseline Revenue: {baseline_revenue:,.0f} SEK")
            print(f"   Current Costs: {current_costs:,.0f} SEK")
            print(f"   Baseline Costs: {baseline_costs:,.0f} SEK")
            
            # Check if EBITDA is around the expected value (550M)
            expected_ebitda = 550_000_000  # 550M SEK
            if abs(current_ebitda - expected_ebitda) < 100_000_000:  # Within 100M
                print(f"\n✅ EBITDA looks correct! (~550M expected)")
            else:
                print(f"\n❌ EBITDA still incorrect. Expected ~550M, got {current_ebitda:,.0f}")
                
                # Check if it's the old bug value
                if abs(current_ebitda - 2433700000) < 100000:  # Close to 2.43B
                    print("   This looks like the old buggy calculation (2.43B)")
                    print("   The git restore likely undid our fixes")
                
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - simulation is taking too long")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server - is it running on port 8000?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ebitda() 