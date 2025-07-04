import os
import tempfile
import json
import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture(scope="module")
def client():
    # Use a temp dir for scenario storage
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ["SCENARIO_STORAGE_DIR"] = temp_dir
        
        # Create a test configuration file
        test_config = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {
                            "fte": 50,
                            "recruitment_1": 0.1, "recruitment_2": 0.1, "recruitment_3": 0.1, "recruitment_4": 0.1,
                            "recruitment_5": 0.1, "recruitment_6": 0.1, "recruitment_7": 0.1, "recruitment_8": 0.1,
                            "recruitment_9": 0.1, "recruitment_10": 0.1, "recruitment_11": 0.1, "recruitment_12": 0.1,
                            "churn_1": 0.05, "churn_2": 0.05, "churn_3": 0.05, "churn_4": 0.05,
                            "churn_5": 0.05, "churn_6": 0.05, "churn_7": 0.05, "churn_8": 0.05,
                            "churn_9": 0.05, "churn_10": 0.05, "churn_11": 0.05, "churn_12": 0.05,
                            "price_1": 1000, "price_2": 1000, "price_3": 1000, "price_4": 1000,
                            "price_5": 1000, "price_6": 1000, "price_7": 1000, "price_8": 1000,
                            "price_9": 1000, "price_10": 1000, "price_11": 1000, "price_12": 1000,
                            "salary_1": 50000, "salary_2": 50000, "salary_3": 50000, "salary_4": 50000,
                            "salary_5": 50000, "salary_6": 50000, "salary_7": 50000, "salary_8": 50000,
                            "salary_9": 50000, "salary_10": 50000, "salary_11": 50000, "salary_12": 50000,
                            "utr_1": 0.85, "utr_2": 0.85, "utr_3": 0.85, "utr_4": 0.85,
                            "utr_5": 0.85, "utr_6": 0.85, "utr_7": 0.85, "utr_8": 0.85,
                            "utr_9": 0.85, "utr_10": 0.85, "utr_11": 0.85, "utr_12": 0.85
                        },
                        "AC": {
                            "fte": 30,
                            "recruitment_1": 0.08, "recruitment_2": 0.08, "recruitment_3": 0.08, "recruitment_4": 0.08,
                            "recruitment_5": 0.08, "recruitment_6": 0.08, "recruitment_7": 0.08, "recruitment_8": 0.08,
                            "recruitment_9": 0.08, "recruitment_10": 0.08, "recruitment_11": 0.08, "recruitment_12": 0.08,
                            "churn_1": 0.04, "churn_2": 0.04, "churn_3": 0.04, "churn_4": 0.04,
                            "churn_5": 0.04, "churn_6": 0.04, "churn_7": 0.04, "churn_8": 0.04,
                            "churn_9": 0.04, "churn_10": 0.04, "churn_11": 0.04, "churn_12": 0.04,
                            "price_1": 1200, "price_2": 1200, "price_3": 1200, "price_4": 1200,
                            "price_5": 1200, "price_6": 1200, "price_7": 1200, "price_8": 1200,
                            "price_9": 1200, "price_10": 1200, "price_11": 1200, "price_12": 1200,
                            "salary_1": 60000, "salary_2": 60000, "salary_3": 60000, "salary_4": 60000,
                            "salary_5": 60000, "salary_6": 60000, "salary_7": 60000, "salary_8": 60000,
                            "salary_9": 60000, "salary_10": 60000, "salary_11": 60000, "salary_12": 60000,
                            "utr_1": 0.85, "utr_2": 0.85, "utr_3": 0.85, "utr_4": 0.85,
                            "utr_5": 0.85, "utr_6": 0.85, "utr_7": 0.85, "utr_8": 0.85,
                            "utr_9": 0.85, "utr_10": 0.85, "utr_11": 0.85, "utr_12": 0.85
                        }
                    }
                }
            }
        }
        
        # Create test config file
        test_config_path = os.path.join(temp_dir, "test_config.json")
        with open(test_config_path, 'w') as f:
            json.dump(test_config, f, indent=2)
        
        # Set environment variable for config file
        os.environ["CONFIG_FILE_PATH"] = test_config_path
        
        yield TestClient(app)
        
        # Cleanup
        del os.environ["SCENARIO_STORAGE_DIR"]
        del os.environ["CONFIG_FILE_PATH"]

@pytest.fixture
def sample_scenario():
    return {
        "name": "Integration Test Scenario",
        "description": "Scenario for integration testing",
        "time_range": {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2026,
            "end_month": 12
        },
        "office_scope": ["Stockholm"],
        "levers": {
            "recruitment": {"A": 1.2, "AC": 1.1},
            "churn": {"A": 0.9, "AC": 1.0},
            "progression": {"A": 1.0, "AC": 1.0}
        }
    }

def test_create_and_get_scenario(client, sample_scenario):
    # Create scenario
    resp = client.post("/scenarios/create", json=sample_scenario)
    assert resp.status_code == 200
    scenario_id = resp.json()["scenario_id"]
    assert isinstance(scenario_id, str)

    # Get scenario
    resp = client.get(f"/scenarios/{scenario_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == sample_scenario["name"]
    assert data["description"] == sample_scenario["description"]
    assert data["office_scope"] == sample_scenario["office_scope"]

def test_list_scenarios(client, sample_scenario):
    # Create two scenarios
    client.post("/scenarios/create", json=sample_scenario)
    sample_scenario2 = dict(sample_scenario)
    sample_scenario2["name"] = "Integration Test Scenario 2"
    client.post("/scenarios/create", json=sample_scenario2)

    # List scenarios
    resp = client.get("/scenarios/list")
    assert resp.status_code == 200
    scenarios = resp.json()["scenarios"]
    assert len(scenarios) >= 2
    names = [s["name"] for s in scenarios]
    assert sample_scenario["name"] in names
    assert sample_scenario2["name"] in names

def test_run_scenario(client, sample_scenario):
    # Create scenario
    resp = client.post("/scenarios/create", json=sample_scenario)
    scenario_id = resp.json()["scenario_id"]
    # Run scenario
    resp = client.post("/scenarios/run", json={"scenario_id": scenario_id})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "results" in data
    assert "years" in data["results"]

def test_delete_scenario(client, sample_scenario):
    # Create scenario
    resp = client.post("/scenarios/create", json=sample_scenario)
    scenario_id = resp.json()["scenario_id"]
    # Delete scenario
    resp = client.delete(f"/scenarios/{scenario_id}")
    assert resp.status_code == 200
    # Try to get deleted scenario
    resp = client.get(f"/scenarios/{scenario_id}")
    assert resp.status_code == 404

def test_run_nonexistent_scenario(client):
    # Try to run a scenario that doesn't exist
    resp = client.post("/scenarios/run", json={"scenario_id": "nonexistent-id"})
    assert resp.status_code == 404
    data = resp.json()
    assert "detail" in data
    assert "Scenario not found" in data["detail"] 