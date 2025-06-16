import requests
import json

def test_simulation_direct():
    """Test simulation backend directly"""
    
    print("🚀 Testing simulation backend directly...")
    
    # Simulation backend endpoint
    url = "http://127.0.0.1:8000/simulation/run"
    
    # Test simulation parameters
    payload = {
        "start_year": 2025,
        "start_month": 1,
        "end_year": 2026,
        "end_month": 12,
        "price_increase": 0.03,
        "salary_increase": 0.03,
        "unplanned_absence": 0.05,
        "hy_working_hours": 166.4,
        "other_expense": 100000.0
    }
    
    print(f"📋 Testing simulation...")
    print(f"🔗 URL: {url}")
    print(f"⚙️  Parameters: {json.dumps(payload, indent=2)}")
    print("-" * 50)
    
    try:
        print("📡 Sending request...")
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            
            # Print key results
            if 'kpis' in result:
                kpis = result['kpis']
                if 'financial' in kpis:
                    financial = kpis['financial']
                    print(f"💰 Net Sales: {financial.get('net_sales', 0):,.0f} SEK")
                    print(f"💰 EBITDA: {financial.get('ebitda', 0):,.0f} SEK")
                    print(f"📈 Margin: {financial.get('margin', 0):.1f}%")
                
                if 'growth' in kpis:
                    growth = kpis['growth']
                    print(f"📊 Total Growth: {growth.get('total_growth_percent', 0):.1f}% ({growth.get('total_growth_absolute', 0):+d} FTE)")
                    print(f"👥 Current FTE: {growth.get('current_total_fte', 0)}")
            
            print(f"📄 Full Response: {json.dumps(result, indent=2)}")
        else:
            print("❌ Error!")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection failed - is simulation backend running on port 8000? {e}")
    except requests.exceptions.Timeout as e:
        print(f"❌ Request timed out: {e}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🎯 Simulation Backend Direct Test Starting...")
    test_simulation_direct()
    print("🏁 Test completed.") 