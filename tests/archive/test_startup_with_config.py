#!/usr/bin/env python3
"""
Test script to verify the startup_with_config.py script works correctly
and that the configuration service properly loads data for simulation engine.
"""

import sys
import os
import time
import requests
import json
sys.path.append('.')

def test_configuration_service():
    """Test that configuration service has data loaded"""
    print("🔍 [TEST] Testing configuration service...")
    
    try:
        # Test configuration service endpoint
        response = requests.get('http://localhost:8000/offices/config')
        
        if response.status_code == 200:
            config_data = response.json()
            print(f"✅ [TEST] Configuration service returned {len(config_data)} offices")
            
            if len(config_data) > 0:
                total_fte = sum(office.get('total_fte', 0) for office in config_data)
                print(f"✅ [TEST] Total FTE across all offices: {total_fte}")
                
                # Test first office structure
                first_office = config_data[0]
                print(f"✅ [TEST] First office: {first_office.get('name', 'Unknown')}")
                print(f"✅ [TEST] First office FTE: {first_office.get('total_fte', 0)}")
                
                return True, len(config_data), total_fte
            else:
                print("❌ [TEST] Configuration service returned empty data")
                return False, 0, 0
        else:
            print(f"❌ [TEST] Configuration service failed: {response.status_code}")
            return False, 0, 0
            
    except Exception as e:
        print(f"❌ [TEST] Configuration service error: {e}")
        return False, 0, 0

def test_simulation_engine():
    """Test that simulation engine can read from configuration service"""
    print("🔍 [TEST] Testing simulation engine...")
    
    try:
        # Test simulation validation endpoint (this initializes engine from config service)
        response = requests.get('http://localhost:8000/simulation/config/validation')
        
        if response.status_code == 200:
            validation_data = response.json()
            print(f"✅ [TEST] Simulation validation successful")
            print(f"✅ [TEST] Validation response: {json.dumps(validation_data, indent=2)}")
            return True
        else:
            print(f"❌ [TEST] Simulation validation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ [TEST] Simulation engine error: {e}")
        return False

def test_simulation_run():
    """Test that simulation can run successfully"""
    print("🔍 [TEST] Testing simulation run...")
    
    try:
        # Test simulation run
        simulation_request = {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 3,
            "price_increase": 0.025,
            "salary_increase": 0.025
        }
        
        response = requests.post(
            'http://localhost:8000/simulation/run',
            headers={'Content-Type': 'application/json'},
            json=simulation_request
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ [TEST] Simulation run successful")
                
                # Check KPIs
                kpis = result.get('kpis', {})
                financial = kpis.get('financial', {})
                baseline_revenue = financial.get('baseline_net_sales', 0)
                current_revenue = financial.get('current_net_sales', 0)
                
                print(f"✅ [TEST] Baseline revenue: {baseline_revenue:,.0f} SEK")
                print(f"✅ [TEST] Current revenue: {current_revenue:,.0f} SEK")
                
                if baseline_revenue > 0:
                    print(f"✅ [TEST] Simulation has proper baseline data")
                    return True, baseline_revenue, current_revenue
                else:
                    print(f"❌ [TEST] Simulation baseline is 0 - configuration issue")
                    return False, 0, 0
            else:
                print(f"❌ [TEST] Simulation run failed: {result}")
                return False, 0, 0
        else:
            print(f"❌ [TEST] Simulation run HTTP error: {response.status_code}")
            return False, 0, 0
            
    except Exception as e:
        print(f"❌ [TEST] Simulation run error: {e}")
        return False, 0, 0

def test_backend_health():
    """Test that backend is running"""
    print("🔍 [TEST] Testing backend health...")
    
    try:
        response = requests.get('http://localhost:8000/health')
        if response.status_code == 200:
            health_data = response.json()
            print("✅ [TEST] Backend is healthy")
            print(f"✅ [TEST] Health data: {health_data}")
            return True
        else:
            print(f"❌ [TEST] Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ [TEST] Backend health error: {e}")
        return False

def run_test():
    """Run basic tests"""
    print("🚀 [TEST] Starting basic configuration test...")
    print("=" * 60)
    
    # Test 1: Backend Health
    if not test_backend_health():
        print("❌ [TEST] Backend is not running")
        return False
    
    print("-" * 60)
    
    # Test 2: Configuration Service
    config_success, num_offices, total_fte = test_configuration_service()
    if not config_success:
        print("❌ [TEST] Configuration service failed")
        return False
    
    print("=" * 60)
    print("🎉 [TEST] BASIC TESTS PASSED!")
    print(f"✅ Configuration: {num_offices} offices, {total_fte:,.0f} total FTE")
    
    return True

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1) 