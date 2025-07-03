import os
import json

def log_422_error(resp, context):
    if resp.status_code == 422:
        log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, '422_error_details.json')
        with open(log_path, 'a') as f:
            f.write(f'--- {context} ---\n')
            json.dump(resp.json(), f, indent=2)
            f.write('\n')

def test_create_and_get_scenario(client, sample_scenario):
    # Create scenario
    resp = client.post("/scenarios/create", json={"scenario_definition": sample_scenario})
    print("Status:", resp.status_code)
    try:
        print("Response JSON:", resp.json())
    except Exception as e:
        print("Error reading response JSON:", e)
    assert resp.status_code == 200
    scenario_id = resp.json()
    assert isinstance(scenario_id, str)

    # Get scenario
    resp = client.get(f"/scenarios/{scenario_id}")
    print("Status:", resp.status_code)
    try:
        print("Response JSON:", resp.json())
    except Exception as e:
        print("Error reading response JSON:", e)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == sample_scenario["name"]
    assert data["description"] == sample_scenario["description"]
    assert data["office_scope"] == sample_scenario["office_scope"]

def test_list_scenarios(client, sample_scenario):
    # Create two scenarios
    resp1 = client.post("/scenarios/create", json={"scenario_definition": sample_scenario})
    print("Status:", resp1.status_code)
    try:
        print("Response JSON:", resp1.json())
    except Exception as e:
        print("Error reading response JSON:", e)
    sample_scenario2 = dict(sample_scenario)
    sample_scenario2["name"] = "Integration Test Scenario 2"
    resp2 = client.post("/scenarios/create", json={"scenario_definition": sample_scenario2})
    print("Status:", resp2.status_code)
    try:
        print("Response JSON:", resp2.json())
    except Exception as e:
        print("Error reading response JSON:", e)

    # List scenarios
    resp = client.get("/scenarios/list")
    print("Status:", resp.status_code)
    try:
        print("Response JSON:", resp.json())
    except Exception as e:
        print("Error reading response JSON:", e)
    assert resp.status_code == 200
    scenarios = resp.json()["scenarios"]
    assert len(scenarios) >= 2
    names = [s["name"] for s in scenarios]
    assert sample_scenario["name"] in names
    assert sample_scenario2["name"] in names

def test_run_scenario(client, sample_scenario):
    # Create scenario
    resp = client.post("/scenarios/create", json={"scenario_definition": sample_scenario})
    print("Status:", resp.status_code)
    try:
        print("Response JSON:", resp.json())
    except Exception as e:
        print("Error reading response JSON:", e)
    scenario_id = resp.json()
    # Run scenario
    resp = client.post("/scenarios/run", json={"scenario_id": scenario_id})
    print("Status:", resp.status_code)
    try:
        print("Response JSON:", resp.json())
    except Exception as e:
        print("Error reading response JSON:", e)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "results" in data
    assert "years" in data["results"] 