#!/usr/bin/env python3
"""
Test script to verify JSON download functionality
"""

import requests
import json
import os
from datetime import datetime

def test_download_functionality():
    """Test the download functionality"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing JSON Download Functionality")
    print("=" * 50)
    
    # Step 1: Run a simulation to generate a result file
    print("\n1️⃣ Running simulation to generate result file...")
    
    simulation_params = {
        "start_year": 2025,
        "start_month": 1,
        "end_year": 2026,
        "end_month": 12,
        "price_increase": 0.03,
        "salary_increase": 0.03,
        "unplanned_absence": 0.05,
        "hy_working_hours": 166.4,
        "other_expense": 19000000.0
    }
    
    try:
        response = requests.post(f"{base_url}/simulation/run", json=simulation_params)
        response.raise_for_status()
        results = response.json()
        
        filename = results.get('result_file')
        if not filename:
            print("❌ No result file generated")
            return False
            
        print(f"✅ Simulation completed, result file: {filename}")
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        return False
    
    # Step 2: Test the download endpoint
    print(f"\n2️⃣ Testing download endpoint for {filename}...")
    
    try:
        download_response = requests.get(f"{base_url}/simulation/download/{filename}")
        download_response.raise_for_status()
        
        # Check if we got JSON content
        content_type = download_response.headers.get('content-type', '')
        if 'application/json' in content_type:
            print("✅ Download endpoint returned JSON content")
        else:
            print(f"⚠️ Unexpected content type: {content_type}")
        
        # Check if the downloaded content is valid JSON
        try:
            downloaded_data = download_response.json()
            print(f"✅ Downloaded content is valid JSON with {len(downloaded_data)} top-level keys")
        except json.JSONDecodeError:
            print("❌ Downloaded content is not valid JSON")
            return False
            
        # Check if the file exists on disk
        filepath = os.path.join(os.getcwd(), filename)
        if os.path.exists(filepath):
            print(f"✅ File exists on disk: {filepath}")
            file_size = os.path.getsize(filepath)
            print(f"   File size: {file_size:,} bytes")
        else:
            print(f"❌ File not found on disk: {filepath}")
            return False
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print("❌ File not found (404)")
        else:
            print(f"❌ Download failed with status {e.response.status_code}")
        return False
    except Exception as e:
        print(f"❌ Download test failed: {e}")
        return False
    
    # Step 3: Test invalid filename
    print(f"\n3️⃣ Testing invalid filename protection...")
    
    try:
        invalid_response = requests.get(f"{base_url}/simulation/download/invalid_file.txt")
        if invalid_response.status_code == 400:
            print("✅ Invalid filename correctly rejected (400)")
        else:
            print(f"⚠️ Invalid filename returned status {invalid_response.status_code}")
    except Exception as e:
        print(f"❌ Invalid filename test failed: {e}")
    
    print("\n🎉 Download functionality test completed successfully!")
    return True

if __name__ == "__main__":
    test_download_functionality() 