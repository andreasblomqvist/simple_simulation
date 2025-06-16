import requests
import json
import sys

def test_stockholm_simulation():
    """Test Stockholm simulation directly through MCP server"""
    
    print("🚀 Starting Stockholm simulation test...")
    
    # MCP server endpoint
    url = "http://127.0.0.1:8100/ask"
    
    # Test question about Stockholm simulation
    question = "Run a simulation for Stockholm office from 2025 to 2026 with 3% price increase and 3% salary increase"
    
    # Correct payload format for updated MCP server
    payload = {
        "question": question,
        "simulation_params": {
            "duration_months": 24,
            "start_year": 2025,
            "start_month": 1,
            "price_increase": 0.03,
            "salary_increase": 0.03,
            "unplanned_absence": 0.05,
            "hy_working_hours": 166.4,
            "other_expense": 100000.0
        }
    }
    
    print(f"📋 Testing Stockholm simulation...")
    print(f"🔗 URL: {url}")
    print(f"❓ Question: {question}")
    print(f"⚙️  Parameters: {json.dumps(payload, indent=2)}")
    print("-" * 50)
    
    try:
        print("📡 Sending request...")
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"📄 Response: {json.dumps(result, indent=2)}")
        else:
            print("❌ Error!")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection failed - is MCP server running on port 8100? {e}")
    except requests.exceptions.Timeout as e:
        print(f"❌ Request timed out: {e}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🎯 Stockholm Direct Test Starting...")
    test_stockholm_simulation()
    print("🏁 Test completed.") 