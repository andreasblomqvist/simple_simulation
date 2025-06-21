"""
Shared test configuration and fixtures for SimpleSim
"""

import pytest
import sys
import os
import requests
import time
from typing import Dict, Any, Optional

# Add backend src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

@pytest.fixture(scope="session")
def base_url():
    """Base URL for API tests"""
    return "http://localhost:8000"

@pytest.fixture(scope="session")
def api_client(base_url):
    """API client for making requests"""
    class APIClient:
        def __init__(self, base_url: str):
            self.base_url = base_url
            
        def get(self, endpoint: str, **kwargs):
            return requests.get(f"{self.base_url}{endpoint}", **kwargs)
            
        def post(self, endpoint: str, json_data: Dict[Any, Any] = None, **kwargs):
            return requests.post(f"{self.base_url}{endpoint}", json=json_data, **kwargs)
            
        def health_check(self) -> bool:
            """Check if the API is healthy"""
            try:
                response = self.get("/health")
                return response.status_code == 200
            except:
                return False
    
    return APIClient(base_url)

@pytest.fixture(scope="session")
def ensure_server_running(api_client):
    """Ensure the server is running before tests"""
    if not api_client.health_check():
        pytest.skip("Server is not running. Start with: PYTHONPATH=. python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000")

@pytest.fixture
def test_config():
    """Standard test configuration for simulations"""
    return {
        "start_year": 2025,
        "start_month": 1,
        "end_year": 2025,
        "end_month": 1,
        "price_increase": 0.0,
        "salary_increase": 0.0,
        "unplanned_absence": 0.05,
        "hy_working_hours": 166.4,
        "other_expense": 100000.0
    }

@pytest.fixture
def stockholm_consultant_a_config():
    """Configuration update for Stockholm Consultant A level"""
    def _update_config(recruitment_rate: float, churn_rate: Optional[float] = None, progression_rate: Optional[float] = None):
        config = {"Stockholm.Consultant.A.recruitment_1": recruitment_rate}
        if churn_rate is not None:
            config["Stockholm.Consultant.A.churn_1"] = churn_rate
        if progression_rate is not None:
            config["Stockholm.Consultant.A.progression_1"] = progression_rate
        return config
    return _update_config

@pytest.fixture
def logger():
    """Test logger with timestamps"""
    def _log(message: str):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    return _log

class TestHelper:
    """Helper class for common test operations"""
    
    @staticmethod
    def get_stockholm_a_level_data(offices_data: list) -> Dict[str, Any]:
        """Extract Stockholm Consultant A level data from offices configuration"""
        stockholm = next((o for o in offices_data if o["name"] == "Stockholm"), None)
        if not stockholm:
            raise ValueError("Stockholm office not found")
        
        consultant_a = stockholm["roles"]["Consultant"]["A"]
        return {
            "fte": consultant_a["fte"],
            "recruitment_1": consultant_a["recruitment_1"],
            "churn_1": consultant_a["churn_1"],
            "progression_1": consultant_a["progression_1"]
        }
    
    @staticmethod
    def extract_simulation_results(results: Dict[str, Any], office: str = "Stockholm", role: str = "Consultant", level: str = "A") -> Dict[str, Any]:
        """Extract specific level results from simulation output"""
        final_year_data = results['years']['2025']
        level_data = final_year_data['offices'][office]['levels'][role][level][0]
        
        return {
            "total": level_data.get('total', 0),
            "recruited": level_data.get('recruited', 0),
            "churned": level_data.get('churned', 0),
            "progressed_out": level_data.get('progressed_out', 0)
        }
    
    @staticmethod
    def calculate_expected_dynamics(baseline_fte: int, recruitment_rate: float, churn_rate: float, progression_rate: float) -> Dict[str, int]:
        """Calculate expected results based on recruitment, churn, and progression rates"""
        expected_recruited = int(baseline_fte * recruitment_rate)
        after_recruitment = baseline_fte + expected_recruited
        
        expected_churned = int(after_recruitment * churn_rate)
        after_churn = after_recruitment - expected_churned
        
        expected_progressed_out = int(after_churn * progression_rate)
        expected_final = after_churn - expected_progressed_out
        
        return {
            "recruited": expected_recruited,
            "churned": expected_churned,
            "progressed_out": expected_progressed_out,
            "final": expected_final
        }

@pytest.fixture
def test_helper():
    """Test helper instance"""
    return TestHelper 