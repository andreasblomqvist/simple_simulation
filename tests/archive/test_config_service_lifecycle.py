#!/usr/bin/env python3
"""
Comprehensive Configuration Service Lifecycle Test

This test validates the entire configuration service workflow:
1. Read configuration from Excel file
2. Update a field value
3. Verify the update worked
4. Restart the server
5. Validate that the update persisted
6. Run a simulation
7. Verify the updated value is still there

Usage:
    python test_config_service_lifecycle.py
"""

import os
import sys
import time
import json
import requests
import subprocess
import signal
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.src.services.config_service import config_service

class ConfigServiceLifecycleTest:
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
        
    def test_6_run_simulation(self):
        """Test 6: Run a simulation"""
        self.log("🧪 TEST 6: Running simulation")
        
        # Prepare simulation request with correct format
        simulation_payload = {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 3,
            "price_increase": 0.02,
            "salary_increase": 0.03,
            "office_overrides": {}
        }
        
        # Run simulation
        response = requests.post(
            f"{self.base_url}/simulation/run",
            json=simulation_payload,
            headers={"Content-Type": "application/json"},
            timeout=60  # Simulation can take time
        )
        assert response.status_code == 200, f"Simulation failed: {response.status_code} - {response.text}"
        
        simulation_result = response.json()
        assert "years" in simulation_result, "Simulation result missing 'years' data"
        assert "kpis" in simulation_result, "Simulation result missing 'kpis' data"
        
        # Check that simulation has data
        years_data = simulation_result["years"]
        assert len(years_data) > 0, "Simulation returned no years data"
        
        # Get financial KPIs
        financial_kpis = simulation_result["kpis"]["financial"]
        revenue = financial_kpis.get("net_sales", 0)
        ebitda = financial_kpis.get("ebitda", 0)
        
        self.log(f"✅ Simulation completed: Revenue={revenue:,.0f} SEK, EBITDA={ebitda:,.0f} SEK")
        
        return simulation_result
        
    def test_7_verify_updated_value_in_simulation(self):
        """Test 7: Verify the updated value is reflected in simulation"""
        self.log("🧪 TEST 7: Verifying updated value in simulation results")
        
        # Get current configuration to compare
        response = requests.get(f"{self.base_url}/offices/config")
        assert response.status_code == 200, f"Config endpoint failed: {response.status_code}"
        
        offices = response.json()
        stockholm_office = next((o for o in offices if o["name"] == self.test_office), None)
        current_fte = stockholm_office["total_fte"]
        
        # Verify it's still our updated value
        assert current_fte == self.updated_fte, f"Configuration changed during simulation: expected {self.updated_fte}, got {current_fte}"
        
        # Run another simulation to ensure configuration is still used
        simulation_payload = {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 1,
            "price_increase": 0.02,
            "salary_increase": 0.03,
            "office_overrides": {}
        }
        
        response = requests.post(
            f"{self.base_url}/simulation/run",
            json=simulation_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        assert response.status_code == 200, f"Second simulation failed: {response.status_code}"
        
        self.log(f"✅ Updated value verified: {self.test_office} FTE = {current_fte} still used in simulation")
        
    def run_all_tests(self):
        """Run all tests in sequence"""
        try:
            self.log("🚀 Starting Configuration Service Lifecycle Test")
            self.log("=" * 60)
            
            # Start server for initial tests
            self.start_server()
            
            # Run all test steps
            self.test_1_read_config_from_excel()
            self.test_2_update_field()
            self.test_3_verify_update()
            self.test_4_restart_server()
            self.test_5_validate_persistence()
            self.test_6_run_simulation()
            self.test_7_verify_updated_value_in_simulation()
            
            self.log("=" * 60)
            self.log("🎉 ALL TESTS PASSED! Configuration service lifecycle working correctly.")
            
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
    test = ConfigServiceLifecycleTest()
    test.run_all_tests() 