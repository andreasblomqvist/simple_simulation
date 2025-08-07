"""
API Validation Tests for SimpleSim Engine V2

Tests the V2 API endpoints for proper validation, error handling,
and integration with the actual V2 engine components.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, date, timedelta

from backend.main import app
from backend.routers.simulation_v2 import simulation_manager
from backend.src.services.simulation_engine_v2 import (
    SimulationEngineV2Factory, ScenarioRequest, TimeRange, Levers
)

# Test client
client = TestClient(app)

class TestV2EngineAPIValidation:
    """Test V2 API endpoints with comprehensive validation"""
    
    def setup_method(self):
        """Setup for each test"""
        # Clear simulation manager state
        simulation_manager.running_simulations.clear()
        simulation_manager.completed_results.clear()
        simulation_manager.engine_cache.clear()
    
    def test_health_check_endpoint(self):
        """Test V2 health check endpoint"""
        response = client.get("/api/v2/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.8.0-beta"
        assert data["engine"] == "SimulationEngineV2"
        assert "timestamp" in data
    
    def test_health_check_engine_failure(self):
        """Test health check when engine creation fails"""
        with patch('backend.routers.simulation_v2.get_v2_engine', side_effect=Exception("Engine failure")):
            response = client.get("/api/v2/health")
            assert response.status_code == 503
            assert "V2 engine unhealthy" in response.json()["detail"]
    
    def test_scenario_request_validation_valid(self):
        """Test valid scenario request"""
        scenario_data = {
            "scenario_id": "test_scenario_123",
            "name": "Test Scenario",
            "time_range": {
                "start_year": 2024,
                "start_month": 1,
                "end_year": 2024,
                "end_month": 12
            },
            "office_ids": ["london", "new_york"],
            "levers": {
                "recruitment_multiplier": 1.2,
                "churn_multiplier": 0.8,
                "progression_multiplier": 1.0,
                "price_multiplier": 1.1,
                "salary_multiplier": 1.05
            }
        }
        
        response = client.post("/api/v2/scenarios/run", json=scenario_data)
        # Should return 200 and queue the simulation
        assert response.status_code == 200
        
        result = response.json()
        assert result["scenario_id"] == "test_scenario_123"
        assert result["status"] == "queued"
        assert "started_at" in result
    
    def test_scenario_request_validation_invalid_time_range(self):
        """Test scenario with invalid time range"""
        scenario_data = {
            "scenario_id": "invalid_time",
            "name": "Invalid Time Range",
            "time_range": {
                "start_year": 1999,  # Too early
                "start_month": 1,
                "end_year": 2024,
                "end_month": 12
            },
            "office_ids": ["london"]
        }
        
        response = client.post("/api/v2/scenarios/run", json=scenario_data)
        assert response.status_code == 422  # Validation error
        
        error_detail = response.json()["detail"][0]
        assert "start_year" in str(error_detail)
    
    def test_scenario_request_validation_invalid_levers(self):
        """Test scenario with invalid lever values"""
        scenario_data = {
            "scenario_id": "invalid_levers",
            "name": "Invalid Levers",
            "time_range": {
                "start_year": 2024,
                "start_month": 1,
                "end_year": 2024,
                "end_month": 12
            },
            "office_ids": ["london"],
            "levers": {
                "recruitment_multiplier": 10.0,  # Too high
                "churn_multiplier": 0.05  # Too low
            }
        }
        
        response = client.post("/api/v2/scenarios/run", json=scenario_data)
        assert response.status_code == 422
        
        errors = response.json()["detail"]
        lever_errors = [e for e in errors if "multiplier" in str(e)]
        assert len(lever_errors) >= 2  # Both invalid values should be caught
    
    def test_scenario_request_missing_required_fields(self):
        """Test scenario with missing required fields"""
        scenario_data = {
            "scenario_id": "missing_fields",
            # Missing name, time_range, office_ids
        }
        
        response = client.post("/api/v2/scenarios/run", json=scenario_data)
        assert response.status_code == 422
        
        errors = response.json()["detail"]
        required_field_errors = [e for e in errors if e["type"] == "missing"]
        assert len(required_field_errors) >= 3  # name, time_range, office_ids
    
    def test_scenario_request_duplicate_running(self):
        """Test submitting duplicate scenario while one is running"""
        scenario_data = {
            "scenario_id": "duplicate_test",
            "name": "Duplicate Test",
            "time_range": {
                "start_year": 2024,
                "start_month": 1,
                "end_year": 2024,
                "end_month": 6
            },
            "office_ids": ["london"]
        }
        
        # Submit first scenario
        response1 = client.post("/api/v2/scenarios/run", json=scenario_data)
        assert response1.status_code == 200
        
        # Submit duplicate immediately
        response2 = client.post("/api/v2/scenarios/run", json=scenario_data)
        assert response2.status_code == 409  # Conflict
        assert "already" in response2.json()["detail"]
    
    def test_get_scenario_status_not_found(self):
        """Test getting status for non-existent scenario"""
        response = client.get("/api/v2/scenarios/nonexistent/status")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_get_scenario_status_valid(self):
        """Test getting status for valid scenario"""
        # First, submit a scenario
        scenario_data = {
            "scenario_id": "status_test",
            "name": "Status Test",
            "time_range": {
                "start_year": 2024,
                "start_month": 1,
                "end_year": 2024,
                "end_month": 3
            },
            "office_ids": ["london"]
        }
        
        submit_response = client.post("/api/v2/scenarios/run", json=scenario_data)
        assert submit_response.status_code == 200
        
        # Get status
        status_response = client.get("/api/v2/scenarios/status_test/status")
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert status_data["scenario_id"] == "status_test"
        assert status_data["status"] in ["queued", "running", "completed", "failed"]
        assert "started_at" in status_data
    
    def test_get_results_scenario_not_found(self):
        """Test getting results for non-existent scenario"""
        response = client.get("/api/v2/scenarios/nonexistent/results")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_get_results_still_running(self):
        """Test getting results for scenario still running"""
        # Submit scenario and immediately try to get results
        scenario_data = {
            "scenario_id": "running_test",
            "name": "Running Test",
            "time_range": {
                "start_year": 2024,
                "start_month": 1,
                "end_year": 2024,
                "end_month": 12
            },
            "office_ids": ["london"]
        }
        
        submit_response = client.post("/api/v2/scenarios/run", json=scenario_data)
        assert submit_response.status_code == 200
        
        # Try to get results immediately
        results_response = client.get("/api/v2/scenarios/running_test/results")
        # Should return 202 (Accepted) indicating still processing
        assert results_response.status_code == 202
        assert "still" in results_response.json()["detail"]
    
    def test_get_events_with_filters(self):
        """Test getting events with various filters"""
        # This test requires a completed scenario, so we'll mock the results
        from backend.src.services.simulation_engine_v2 import SimulationResults, PersonEvent, EventType
        
        # Create mock results with events
        mock_events = [
            PersonEvent(
                date=date(2024, 1, 15),
                event_type=EventType.HIRED,
                details={"role": "Consultant", "level": "A", "office": "london", "person_id": "person1"},
                simulation_month=1
            ),
            PersonEvent(
                date=date(2024, 2, 15),
                event_type=EventType.PROMOTED,
                details={"role": "Consultant", "level": "AC", "office": "london", "person_id": "person1"},
                simulation_month=2
            ),
            PersonEvent(
                date=date(2024, 3, 15),
                event_type=EventType.CHURNED,
                details={"role": "Sales", "level": "A", "office": "new_york", "person_id": "person2"},
                simulation_month=3
            )
        ]
        
        mock_results = MagicMock(spec=SimulationResults)
        mock_results.all_events = mock_events
        
        # Add to simulation manager
        simulation_manager.completed_results["events_test"] = mock_results
        
        # Test getting all events
        response = client.get("/api/v2/scenarios/events_test/events")
        assert response.status_code == 200
        events = response.json()
        assert len(events) == 3
        
        # Test filtering by event type
        response = client.get("/api/v2/scenarios/events_test/events?event_type=hired")
        assert response.status_code == 200
        events = response.json()
        assert len(events) == 1
        assert events[0]["event_type"] == "hired"
        
        # Test filtering by office
        response = client.get("/api/v2/scenarios/events_test/events?office_id=london")
        assert response.status_code == 200
        events = response.json()
        assert len(events) == 2  # hired and promoted events in london
        
        # Test invalid event type filter
        response = client.get("/api/v2/scenarios/events_test/events?event_type=invalid")
        assert response.status_code == 400
        assert "Invalid event type" in response.json()["detail"]
    
    def test_get_events_pagination(self):
        """Test event pagination"""
        # Create mock results with many events
        mock_events = []
        for i in range(150):  # Create 150 events
            mock_events.append(PersonEvent(
                date=date(2024, 1, 1),
                event_type=EventType.HIRED,
                details={"role": "Consultant", "level": "A", "office": "london", "person_id": f"person{i}"},
                simulation_month=1
            ))
        
        mock_results = MagicMock(spec=SimulationResults)
        mock_results.all_events = mock_events
        simulation_manager.completed_results["pagination_test"] = mock_results
        
        # Test default limit (100)
        response = client.get("/api/v2/scenarios/pagination_test/events")
        assert response.status_code == 200
        events = response.json()
        assert len(events) == 100
        
        # Test custom limit
        response = client.get("/api/v2/scenarios/pagination_test/events?limit=50")
        assert response.status_code == 200
        events = response.json()
        assert len(events) == 50
        
        # Test offset
        response = client.get("/api/v2/scenarios/pagination_test/events?limit=50&offset=50")
        assert response.status_code == 200
        events = response.json()
        assert len(events) == 50
        
        # Test offset beyond available data
        response = client.get("/api/v2/scenarios/pagination_test/events?limit=50&offset=200")
        assert response.status_code == 200
        events = response.json()
        assert len(events) == 0
    
    def test_get_kpis_not_found(self):
        """Test getting KPIs for non-existent scenario"""
        response = client.get("/api/v2/scenarios/nonexistent/kpis")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_get_kpis_no_data(self):
        """Test getting KPIs when no KPI data available"""
        mock_results = MagicMock(spec=SimulationResults)
        mock_results.kpi_data = None
        simulation_manager.completed_results["no_kpis"] = mock_results
        
        response = client.get("/api/v2/scenarios/no_kpis/kpis")
        assert response.status_code == 404
        assert "KPI data not available" in response.json()["detail"]
    
    def test_delete_scenario_not_found(self):
        """Test deleting non-existent scenario"""
        response = client.delete("/api/v2/scenarios/nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_delete_scenario_success(self):
        """Test successful scenario deletion"""
        # Add a scenario to both tracking dicts
        simulation_manager.running_simulations["delete_test"] = {"status": "completed"}
        simulation_manager.completed_results["delete_test"] = MagicMock()
        
        response = client.delete("/api/v2/scenarios/delete_test")
        assert response.status_code == 200
        
        result = response.json()
        assert result["deleted"] == ["simulation_status", "results"]
        
        # Verify deletion
        assert "delete_test" not in simulation_manager.running_simulations
        assert "delete_test" not in simulation_manager.completed_results
    
    def test_list_scenarios_empty(self):
        """Test listing scenarios when none exist"""
        response = client.get("/api/v2/scenarios")
        assert response.status_code == 200
        
        scenarios = response.json()
        assert isinstance(scenarios, list)
        assert len(scenarios) == 0
    
    def test_list_scenarios_with_data(self):
        """Test listing scenarios with some data"""
        # Add some test scenarios
        simulation_manager.running_simulations["scenario1"] = {
            "status": "running",
            "progress": 50.0,
            "started_at": datetime.now(),
            "scenario": {"name": "Test Scenario 1"}
        }
        simulation_manager.running_simulations["scenario2"] = {
            "status": "completed",
            "progress": 100.0,
            "started_at": datetime.now(),
            "scenario": {"name": "Test Scenario 2"}
        }
        
        response = client.get("/api/v2/scenarios")
        assert response.status_code == 200
        
        scenarios = response.json()
        assert len(scenarios) == 2
        
        # Check structure
        for scenario in scenarios:
            assert "scenario_id" in scenario
            assert "name" in scenario
            assert "status" in scenario
            assert "started_at" in scenario
            assert "progress" in scenario
    
    def test_engine_stats_endpoint(self):
        """Test engine statistics endpoint"""
        # Add some test data
        simulation_manager.running_simulations["test1"] = {"status": "running"}
        simulation_manager.completed_results["test2"] = MagicMock()
        simulation_manager.engine_cache["cached_engine"] = MagicMock()
        
        response = client.get("/api/v2/engine/stats")
        assert response.status_code == 200
        
        stats = response.json()
        assert stats["version"] == "0.8.0-beta"
        assert stats["running_simulations"] == 1
        assert stats["completed_simulations"] == 1
        assert stats["cached_engines"] == 1
        assert "uptime" in stats
    
    def test_query_parameter_validation(self):
        """Test query parameter validation"""
        # Test invalid engine type
        scenario_data = {
            "scenario_id": "engine_type_test",
            "name": "Engine Type Test",
            "time_range": {"start_year": 2024, "start_month": 1, "end_year": 2024, "end_month": 12},
            "office_ids": ["london"]
        }
        
        response = client.post("/api/v2/scenarios/run?engine_type=invalid", json=scenario_data)
        assert response.status_code == 422  # Validation error
        
        # Test valid engine types
        for engine_type in ["production", "test", "development"]:
            response = client.post(f"/api/v2/scenarios/run?engine_type={engine_type}", json=scenario_data)
            # Should not fail on engine_type validation (might fail on other things)
            assert response.status_code != 422 or "engine_type" not in str(response.json())


class TestV2EnginePerformanceAPI:
    """Performance-focused API tests"""
    
    def test_concurrent_scenario_submissions(self):
        """Test submitting multiple scenarios concurrently"""
        import threading
        import time
        
        results = {}
        
        def submit_scenario(scenario_id):
            scenario_data = {
                "scenario_id": scenario_id,
                "name": f"Concurrent Test {scenario_id}",
                "time_range": {"start_year": 2024, "start_month": 1, "end_year": 2024, "end_month": 6},
                "office_ids": ["london"]
            }
            
            response = client.post("/api/v2/scenarios/run", json=scenario_data)
            results[scenario_id] = response.status_code
        
        # Submit 5 scenarios concurrently
        threads = []
        for i in range(5):
            thread = threading.Thread(target=submit_scenario, args=[f"concurrent_{i}"])
            threads.append(thread)
            thread.start()
        
        # Wait for all submissions
        for thread in threads:
            thread.join()
        
        # All should have succeeded
        for scenario_id, status_code in results.items():
            assert status_code == 200, f"Scenario {scenario_id} failed with {status_code}"
        
        # All should be tracked
        assert len(simulation_manager.running_simulations) == 5
    
    def test_api_response_time_limits(self):
        """Test that API endpoints respond within reasonable time limits"""
        import time
        
        # Health check should be very fast
        start_time = time.time()
        response = client.get("/api/v2/health")
        health_time = time.time() - start_time
        
        assert response.status_code == 200
        assert health_time < 2.0, f"Health check took {health_time:.2f} seconds, should be < 2s"
        
        # Scenario submission should be fast (just queuing)
        scenario_data = {
            "scenario_id": "timing_test",
            "name": "Timing Test",
            "time_range": {"start_year": 2024, "start_month": 1, "end_year": 2024, "end_month": 12},
            "office_ids": ["london"]
        }
        
        start_time = time.time()
        response = client.post("/api/v2/scenarios/run", json=scenario_data)
        submission_time = time.time() - start_time
        
        assert response.status_code == 200
        assert submission_time < 5.0, f"Scenario submission took {submission_time:.2f} seconds, should be < 5s"
        
        # Status check should be very fast
        start_time = time.time()
        response = client.get("/api/v2/scenarios/timing_test/status")
        status_time = time.time() - start_time
        
        assert response.status_code == 200
        assert status_time < 1.0, f"Status check took {status_time:.2f} seconds, should be < 1s"


class TestV2EngineAPIErrorHandling:
    """Test comprehensive error handling in API"""
    
    def test_malformed_json_request(self):
        """Test handling of malformed JSON in request"""
        # Send malformed JSON
        response = client.post(
            "/api/v2/scenarios/run",
            data="{invalid json}",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_empty_request_body(self):
        """Test handling of empty request body"""
        response = client.post("/api/v2/scenarios/run", json={})
        assert response.status_code == 422
        
        errors = response.json()["detail"]
        required_fields = ["scenario_id", "name", "time_range", "office_ids"]
        for field in required_fields:
            field_errors = [e for e in errors if field in str(e)]
            assert len(field_errors) > 0, f"Missing validation error for required field: {field}"
    
    def test_internal_server_errors(self):
        """Test handling of internal server errors"""
        # Mock the simulation manager to raise an exception
        with patch('backend.routers.simulation_v2.simulation_manager') as mock_manager:
            mock_manager.running_simulations = {}
            mock_manager.start_simulation.side_effect = Exception("Internal error")
            
            scenario_data = {
                "scenario_id": "error_test",
                "name": "Error Test",
                "time_range": {"start_year": 2024, "start_month": 1, "end_year": 2024, "end_month": 12},
                "office_ids": ["london"]
            }
            
            response = client.post("/api/v2/scenarios/run", json=scenario_data)
            assert response.status_code == 500
            assert "Failed to start simulation" in response.json()["detail"]
    
    def test_engine_initialization_failure(self):
        """Test handling when engine initialization fails"""
        with patch('backend.routers.simulation_v2.get_v2_engine', side_effect=RuntimeError("Engine init failed")):
            scenario_data = {
                "scenario_id": "init_fail_test",
                "name": "Init Fail Test",
                "time_range": {"start_year": 2024, "start_month": 1, "end_year": 2024, "end_month": 12},
                "office_ids": ["london"]
            }
            
            response = client.post("/api/v2/scenarios/run", json=scenario_data)
            # The background task will fail, but the initial response should succeed
            assert response.status_code == 200
            
            # The failure should be recorded in the simulation status
            # (We'd need to wait for the background task to complete to test this fully)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])