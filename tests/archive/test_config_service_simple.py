#!/usr/bin/env python3
"""
Simplified Configuration Service Test

This test validates the core configuration service functionality:
1. Read configuration from Excel file
2. Update a field value
3. Verify the update worked
4. Restart the server
5. Validate that the update persisted

Usage:
    python test_config_service_simple.py
"""

import os
import sys
import time
import json
import requests
import subprocess
from pathlib import Path

class SimpleConfigTest:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.server_process = None
        self.test_office = "Stockholm"
        self.original_fte = None
        self.updated_fte = None
        
    def log(self, message):
        """Print timestamped log message"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def wait_for_server(self, timeout=30):
        """Wait for server to be ready"""
        self.log("Waiting for server to be ready...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    health_data = response.json()
                    if health_data.get("total_offices", 0) > 0:
                        self.log(f"✅ Server ready with {health_data['total_offices']} offices")
                        return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
            
        raise Exception(f"Server not ready after {timeout} seconds")
        
    def start_server(self):
        """Start the backend server"""
        self.log("Starting backend server...")
        
        # Kill any existing processes
        os.system("pkill -f uvicorn 2>/dev/null || true")
        time.sleep(2)
        
        # Start server in background
        env = os.environ.copy()
        env["PYTHONPATH"] = "."
        
        self.server_process = subprocess.Popen([
            "python3", "-m", "uvicorn", 
            "backend.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to be ready
        self.wait_for_server()
        
    def stop_server(self):
        """Stop the backend server"""
        if self.server_process:
            self.log("Stopping backend server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                self.server_process.wait()
            self.server_process = None
            time.sleep(2)
            
    def test_1_read_config_from_excel(self):
        """Test 1: Read configuration from Excel file"""
        self.log("🧪 TEST 1: Reading configuration from Excel file")
        
        # Server should have loaded configuration during startup
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        
        health_data = response.json()
        assert health_data["total_offices"] > 0, "No offices loaded from Excel"
        assert health_data["total_fte"] > 0, "No FTE data loaded from Excel"
        
        self.log(f"✅ Configuration loaded: {health_data['total_offices']} offices, {health_data['total_fte']} total FTE")
        
        # Get specific office data
        response = requests.get(f"{self.base_url}/offices/config")
        assert response.status_code == 200, f"Config endpoint failed: {response.status_code}"
        
        offices = response.json()
        stockholm_office = next((o for o in offices if o["name"] == self.test_office), None)
        assert stockholm_office is not None, f"Office {self.test_office} not found"
        
        self.original_fte = stockholm_office["total_fte"]
        self.log(f"✅ Original {self.test_office} FTE: {self.original_fte}")
        
    def test_2_update_field(self):
        """Test 2: Update a field value"""
        self.log("🧪 TEST 2: Updating field value")
        
        # Calculate new FTE value
        self.updated_fte = self.original_fte + 10
        
        # Prepare update payload
        update_payload = {
            self.test_office: {
                "name": self.test_office,
                "total_fte": self.updated_fte,
                "journey": "Mature Office"
            }
        }
        
        # Send update request
        response = requests.post(
            f"{self.base_url}/offices/config/update",
            json=update_payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Update failed: {response.status_code} - {response.text}"
        
        update_result = response.json()
        self.log(f"✅ Update response: {update_result['message']}")
        
    def test_3_verify_update(self):
        """Test 3: Verify the update worked"""
        self.log("🧪 TEST 3: Verifying update worked")
        
        # Get updated configuration
        response = requests.get(f"{self.base_url}/offices/config")
        assert response.status_code == 200, f"Config endpoint failed: {response.status_code}"
        
        offices = response.json()
        stockholm_office = next((o for o in offices if o["name"] == self.test_office), None)
        assert stockholm_office is not None, f"Office {self.test_office} not found after update"
        
        current_fte = stockholm_office["total_fte"]
        assert current_fte == self.updated_fte, f"Update failed: expected {self.updated_fte}, got {current_fte}"
        
        self.log(f"✅ Update verified: {self.test_office} FTE changed from {self.original_fte} to {current_fte}")
        
        # Also verify in JSON file
        config_file = Path("config/office_configuration.json")
        assert config_file.exists(), "Configuration JSON file not found"
        
        with open(config_file, 'r') as f:
            config_data = json.load(f)
            
        file_fte = config_data[self.test_office]["total_fte"]
        assert file_fte == self.updated_fte, f"JSON file not updated: expected {self.updated_fte}, got {file_fte}"
        
        self.log(f"✅ JSON file verified: {self.test_office} FTE = {file_fte}")
        
    def test_4_restart_server(self):
        """Test 4: Restart the server"""
        self.log("🧪 TEST 4: Restarting server")
        
        self.stop_server()
        self.start_server()
        
        self.log("✅ Server restarted successfully")
        
    def test_5_validate_persistence(self):
        """Test 5: Validate that the update persisted after restart"""
        self.log("🧪 TEST 5: Validating update persistence after restart")
        
        # Get configuration after restart
        response = requests.get(f"{self.base_url}/offices/config")
        assert response.status_code == 200, f"Config endpoint failed after restart: {response.status_code}"
        
        offices = response.json()
        stockholm_office = next((o for o in offices if o["name"] == self.test_office), None)
        assert stockholm_office is not None, f"Office {self.test_office} not found after restart"
        
        current_fte = stockholm_office["total_fte"]
        assert current_fte == self.updated_fte, f"Update not persisted: expected {self.updated_fte}, got {current_fte}"
        
        self.log(f"✅ Persistence verified: {self.test_office} FTE still = {current_fte} after restart")
        
        # Also verify JSON file still has the correct value
        config_file = Path("config/office_configuration.json")
        with open(config_file, 'r') as f:
            config_data = json.load(f)
            
        file_fte = config_data[self.test_office]["total_fte"]
        assert file_fte == self.updated_fte, f"JSON file lost update after restart: expected {self.updated_fte}, got {file_fte}"
        
        self.log(f"✅ JSON file persistence verified: {self.test_office} FTE = {file_fte}")
        
    def test_6_configuration_validation(self):
        """Test 6: Test configuration validation endpoint"""
        self.log("🧪 TEST 6: Testing configuration validation")
        
        response = requests.get(f"{self.base_url}/offices/config/validation")
        assert response.status_code == 200, f"Validation endpoint failed: {response.status_code}"
        
        validation_result = response.json()
        assert validation_result["status"] == "valid", f"Configuration validation failed: {validation_result}"
        
        summary = validation_result["summary"]
        assert summary["total_offices"] > 0, "No offices in validation summary"
        assert summary["total_fte"] > 0, "No FTE in validation summary"
        
        self.log(f"✅ Validation passed: {summary['total_offices']} offices, {summary['total_fte']} total FTE")
        
    def run_all_tests(self):
        """Run all tests in sequence"""
        try:
            self.log("🚀 Starting Simple Configuration Service Test")
            self.log("=" * 60)
            
            # Start server for initial tests
            self.start_server()
            
            # Run all test steps
            self.test_1_read_config_from_excel()
            self.test_2_update_field()
            self.test_3_verify_update()
            self.test_4_restart_server()
            self.test_5_validate_persistence()
            self.test_6_configuration_validation()
            
            self.log("=" * 60)
            self.log("🎉 ALL TESTS PASSED! Configuration service working correctly.")
            self.log("✅ Key functionality verified:")
            self.log("  - Excel import works")
            self.log("  - Configuration updates work")
            self.log("  - Updates persist to JSON file")
            self.log("  - Updates survive server restarts")
            self.log("  - Validation endpoint works")
            
        except Exception as e:
            self.log(f"❌ TEST FAILED: {str(e)}")
            raise
        finally:
            # Cleanup
            self.stop_server()
            
    def __del__(self):
        """Cleanup on destruction"""
        self.stop_server()

if __name__ == "__main__":
    test = SimpleConfigTest()
    test.run_all_tests()
