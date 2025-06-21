#!/usr/bin/env python3
"""
Specific test to verify price increase is applied yearly, not monthly
"""

import requests
import json

def test_price_increase_verification():
    """Test with 20% price increase to clearly see if it's monthly vs yearly"""
    print("🔍 Testing price increase application (yearly vs monthly)...")
    
    # Test with 20% price increase over 2 years
    # If applied yearly: ~44% total increase (1.2^2 = 1.44)
    # If applied monthly: ~890% total increase (1.2^24 = 8.9)
    params = {
        "start_year": 2025,
        "start_month": 1,
        "end_year": 2026,
        "end_month": 12,
        "price_increase": 0.20,  # 20% yearly
        "salary_increase": 0.0,
        "hy_working_hours": 166.4,
        "unplanned_absence": 0.05,
        "other_expense": 19000000,
        "office_overrides": {}
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/simulation/run",
            json=params,
            timeout=60
        )
        
        if response.status_code == 200:
            results = response.json()
            
            if 'kpis' in results and 'financial' in results['kpis']:
                financial = results['kpis']['financial']
                current_rate = financial.get('avg_hourly_rate', 0)
                baseline_rate = financial.get('avg_hourly_rate_baseline', 0)
                
                if baseline_rate > 0:
                    rate_increase_percent = (current_rate - baseline_rate) / baseline_rate * 100
                    
                    print(f"📊 Results after 2 years with 20% yearly price increase:")
                    print(f"   Baseline rate: {baseline_rate:.2f} SEK/hr")
                    print(f"   Current rate:  {current_rate:.2f} SEK/hr")
                    print(f"   Total increase: {rate_increase_percent:.1f}%")
                    
                    # Expected: ~44% for yearly, ~890% for monthly
                    if rate_increase_percent < 60:
                        print("   ✅ CORRECT: Price increase applied yearly")
                        print("   Expected ~44% for yearly application, got {:.1f}%".format(rate_increase_percent))
                        return True
                    elif rate_increase_percent > 300:
                        print("   ❌ ERROR: Price increase appears to be applied monthly!")
                        print("   Got {:.1f}% increase, which suggests monthly compounding".format(rate_increase_percent))
                        return False
                    else:
                        print("   ⚠️ UNCLEAR: Unexpected increase of {:.1f}%".format(rate_increase_percent))
                        return False
                else:
                    print("   ❌ No baseline rate found")
                    return False
            else:
                print("   ❌ No financial KPIs in response")
                return False
        else:
            print(f"❌ Simulation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_price_increase_verification()
    if success:
        print("\n🎉 Price increase verification PASSED!")
        print("The system correctly applies price increases yearly, not monthly.")
    else:
        print("\n❌ Price increase verification FAILED!")
        print("The system may be applying price increases incorrectly.")
    
    exit(0 if success else 1)
