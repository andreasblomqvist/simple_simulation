#!/usr/bin/env python3
import requests
import json

def test_excel_export():
    print("🧪 Testing Excel Export Functionality")
    print("=" * 50)
    
    # Test parameters
    params = {
        'start_year': 2025,
        'start_month': 1,
        'end_year': 2027,
        'end_month': 12,
        'price_increase': 0.02,
        'salary_increase': 0.02,
        'unplanned_absence': 0.05,
        'hy_working_hours': 166.4,
        'other_expense': 100000.0
    }
    
    try:
        # Run simulation
        print("1. Running simulation...")
        response = requests.post('http://localhost:8000/simulation/run', json=params)
        print(f"   Simulation status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Simulation completed successfully")
            
            # Test Excel export
            print("\n2. Testing Excel export...")
            export_response = requests.post('http://localhost:8000/simulation/export/excel', json=params)
            print(f"   Export status: {export_response.status_code}")
            
            if export_response.status_code == 200:
                print("   ✅ Excel export completed successfully")
                print(f"   📊 Excel file size: {len(export_response.content)} bytes")
                
                # Save file for inspection
                with open('test_export.xlsx', 'wb') as f:
                    f.write(export_response.content)
                print("   💾 Excel file saved as test_export.xlsx")
                
                # Basic validation
                if len(export_response.content) > 1000:  # Should be more than 1KB
                    print("   ✅ File size is reasonable")
                else:
                    print("   ⚠️  File size seems small")
                    
            else:
                print(f"   ❌ Excel export failed")
                print(f"   Error: {export_response.text}")
                
        else:
            print(f"   ❌ Simulation failed")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_excel_export() 