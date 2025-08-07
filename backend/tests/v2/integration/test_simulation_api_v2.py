"""
Integration Tests for SimulationV2 API Router

Tests API endpoints for SimpleSim Engine V2 including:
- Scenario execution endpoints
- KPI retrieval endpoints
- Component status endpoints
- Error handling in API layer
- Request validation
- Response formatting
- Performance monitoring
"""

import pytest
from unittest.mock import Mock, patch
import json
from datetime import datetime, date
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Import the actual router
from backend.routers.simulation_v2 import router
from backend.src.services.simulation_engine_v2 import (
    SimulationResults, MonthlyResults, ScenarioRequest, TimeRange, Levers
)


@pytest.fixture
def app():
    """Create FastAPI test application"""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


class TestSimulationV2APIBasics:
    """Basic API functionality tests"""

    def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/api/v2/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data
        assert "engine_info" in data

    def test_api_info_endpoint(self, client):
        """Test API information endpoint"""
        response = client.get("/api/v2/info")
        
        assert response.status_code == 200
        data = response.json()
        assert "api_version" in data
        assert "engine_version" in data
        assert "supported_features" in data
        assert isinstance(data["supported_features"], list)

    def test_component_status_endpoint(self, client):
        """Test component status endpoint"""
        response = client.get("/api/v2/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "components" in data
        
        # Should have status for each component
        components = data["components"]
        expected_components = [
            "simulation_engine", "workforce_manager", "business_processor",
            "growth_manager", "snapshot_loader", "kpi_calculator"
        ]
        
        for component in expected_components:
            assert component in components
            assert "status" in components[component]
            assert "initialized" in components[component]


class TestScenarioExecutionAPI:
    """Test scenario execution API endpoints"""

    @pytest.fixture
    def mock_scenario_request(self):
        """Mock scenario request data"""
        return {
            "name": "API Test Scenario",
            "description": "Test scenario execution via API",
            "time_range": {
                "start_year": 2025,
                "start_month": 1,
                "end_year": 2025,
                "end_month": 12
            },
            "office_scope": ["Stockholm"],
            "levers": {
                "recruitment_multiplier": 1.1,
                "churn_multiplier": 0.9,
                "price_multiplier": 1.0,
                "salary_multiplier": 1.0,
                "progression_multiplier": 1.0
            },
            "use_snapshot": True,
            "snapshot_id": "test-snapshot-123",
            "use_business_plan": True,
            "business_plan_id": "test-business-plan-456"
        }

    def test_execute_scenario_endpoint_success(self, client, mock_scenario_request):
        """Test successful scenario execution"""
        # Mock the engine execution
        mock_results = SimulationResults(
            scenario_id="test-scenario-id",
            monthly_results={
                "2025-01": MonthlyResults(
                    year=2025,
                    month=1,
                    office_results={
                        "Stockholm": {
                            "total_fte": 850,
                            "total_recruitment": 25,
                            "total_churn": 12,
                            "revenue": 850000,
                            "costs": 650000
                        }
                    },
                    aggregate_kpis={
                        "total_headcount": 850,
                        "net_recruitment": 13,
                        "profit": 200000
                    },
                    events_summary={"hired": 25, "churned": 12}
                )
            },
            execution_metadata={
                "execution_time_seconds": 2.5,
                "total_events_processed": 37,
                "simulation_seed": 42
            }
        )
        
        with patch('backend.routers.simulation_v2.execute_scenario_service') as mock_execute:
            mock_execute.return_value = mock_results
            
            response = client.post("/api/v2/scenarios/execute", json=mock_scenario_request)
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify response structure
            assert "scenario_id" in data
            assert "monthly_results" in data
            assert "execution_metadata" in data
            
            # Verify monthly results structure
            assert "2025-01" in data["monthly_results"]
            january_results = data["monthly_results"]["2025-01"]
            assert january_results["year"] == 2025
            assert january_results["month"] == 1
            assert "Stockholm" in january_results["office_results"]

    def test_execute_scenario_endpoint_validation_error(self, client):
        """Test scenario execution with validation errors"""
        invalid_request = {
            "name": "",  # Empty name
            "time_range": {
                "start_year": 2026,
                "start_month": 1,
                "end_year": 2025,  # End before start
                "end_month": 12
            },
            "office_scope": [],  # Empty scope
            "levers": {}
        }
        
        response = client.post("/api/v2/scenarios/execute", json=invalid_request)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], list)  # Pydantic validation errors

    def test_execute_scenario_endpoint_missing_data(self, client, mock_scenario_request):
        """Test scenario execution with missing snapshot/business plan data"""
        with patch('backend.routers.simulation_v2.execute_scenario_service') as mock_execute:
            mock_execute.side_effect = ValueError("Snapshot not found: test-snapshot-123")
            
            response = client.post("/api/v2/scenarios/execute", json=mock_scenario_request)
            
            assert response.status_code == 400  # Bad request
            data = response.json()
            assert "error" in data
            assert "Snapshot not found" in data["error"]

    def test_execute_scenario_endpoint_internal_error(self, client, mock_scenario_request):
        """Test scenario execution with internal server error"""
        with patch('backend.routers.simulation_v2.execute_scenario_service') as mock_execute:
            mock_execute.side_effect = Exception("Internal simulation error")
            
            response = client.post("/api/v2/scenarios/execute", json=mock_scenario_request)
            
            assert response.status_code == 500  # Internal server error
            data = response.json()
            assert "error" in data
            assert "Internal server error" in data["error"]

    def test_execute_scenario_async_endpoint(self, client, mock_scenario_request):
        """Test async scenario execution endpoint"""
        with patch('backend.routers.simulation_v2.create_async_task') as mock_async:
            mock_async.return_value = {"task_id": "async-task-123"}
            
            response = client.post("/api/v2/scenarios/execute-async", json=mock_scenario_request)
            
            assert response.status_code == 202  # Accepted
            data = response.json()
            assert "task_id" in data
            assert "status" in data
            assert data["status"] == "queued"

    def test_get_async_task_status(self, client):
        """Test async task status endpoint"""
        task_id = "async-task-123"
        
        with patch('backend.routers.simulation_v2.get_task_status') as mock_status:
            mock_status.return_value = {
                "task_id": task_id,
                "status": "running",
                "progress": 0.6,
                "estimated_completion": "2025-01-15T10:30:00Z"
            }
            
            response = client.get(f"/api/v2/scenarios/tasks/{task_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["task_id"] == task_id
            assert data["status"] == "running"
            assert data["progress"] == 0.6

    def test_cancel_async_task(self, client):
        """Test async task cancellation"""
        task_id = "async-task-123"
        
        with patch('backend.routers.simulation_v2.cancel_task') as mock_cancel:
            mock_cancel.return_value = {"status": "cancelled"}
            
            response = client.delete(f"/api/v2/scenarios/tasks/{task_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "cancelled"


class TestKPIEndpoints:
    """Test KPI calculation and retrieval endpoints"""

    def test_calculate_kpis_endpoint(self, client):
        """Test KPI calculation endpoint"""
        request_data = {
            "scenario_id": "test-scenario-123",
            "kpi_types": ["workforce", "financial", "business_intelligence"],
            "time_period": {
                "start_year": 2025,
                "start_month": 1,
                "end_year": 2025,
                "end_month": 6
            },
            "offices": ["Stockholm"]
        }
        
        mock_kpis = {
            "workforce": {
                "total_headcount": 850,
                "recruitment_rate": 0.029,
                "churn_rate": 0.014,
                "growth_rate": 0.015
            },
            "financial": {
                "total_revenue": 850000,
                "profit_margin": 0.235,
                "revenue_per_fte": 1000
            },
            "business_intelligence": {
                "average_utilization_rate": 0.78,
                "project_completion_rate": 0.92
            }
        }
        
        with patch('backend.routers.simulation_v2.calculate_kpis_service') as mock_calc:
            mock_calc.return_value = mock_kpis
            
            response = client.post("/api/v2/kpis/calculate", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "workforce" in data
            assert "financial" in data
            assert "business_intelligence" in data
            assert data["workforce"]["total_headcount"] == 850

    def test_get_kpi_trends_endpoint(self, client):
        """Test KPI trends retrieval endpoint"""
        scenario_id = "test-scenario-123"
        kpi_name = "total_headcount"
        
        mock_trends = {
            "kpi_name": kpi_name,
            "data_points": [
                {"period": "2025-01", "value": 820, "target": 800},
                {"period": "2025-02", "value": 835, "target": 810},
                {"period": "2025-03", "value": 850, "target": 820}
            ],
            "trend_analysis": {
                "direction": "increasing",
                "growth_rate": 0.018,
                "volatility": 0.02
            }
        }
        
        with patch('backend.routers.simulation_v2.get_kpi_trends_service') as mock_trends_service:
            mock_trends_service.return_value = mock_trends
            
            response = client.get(f"/api/v2/kpis/trends/{scenario_id}/{kpi_name}")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["kpi_name"] == kpi_name
            assert "data_points" in data
            assert "trend_analysis" in data
            assert data["trend_analysis"]["direction"] == "increasing"

    def test_get_comparative_kpis_endpoint(self, client):
        """Test comparative KPIs endpoint"""
        request_data = {
            "base_scenario_id": "base-scenario-123",
            "comparison_scenario_id": "comparison-scenario-456",
            "kpi_types": ["workforce", "financial"],
            "comparison_type": "side_by_side"
        }
        
        mock_comparison = {
            "base_scenario": {
                "workforce": {"total_headcount": 850, "churn_rate": 0.014},
                "financial": {"revenue": 850000, "profit_margin": 0.235}
            },
            "comparison_scenario": {
                "workforce": {"total_headcount": 920, "churn_rate": 0.012},
                "financial": {"revenue": 920000, "profit_margin": 0.268}
            },
            "variance_analysis": {
                "workforce": {
                    "total_headcount": {"absolute_diff": 70, "percent_diff": 0.082},
                    "churn_rate": {"absolute_diff": -0.002, "percent_diff": -0.143}
                },
                "financial": {
                    "revenue": {"absolute_diff": 70000, "percent_diff": 0.082},
                    "profit_margin": {"absolute_diff": 0.033, "percent_diff": 0.140}
                }
            }
        }
        
        with patch('backend.routers.simulation_v2.compare_kpis_service') as mock_compare:
            mock_compare.return_value = mock_comparison
            
            response = client.post("/api/v2/kpis/compare", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "base_scenario" in data
            assert "comparison_scenario" in data
            assert "variance_analysis" in data

    def test_generate_executive_summary_endpoint(self, client):
        """Test executive summary generation endpoint"""
        scenario_id = "test-scenario-123"
        
        mock_summary = {
            "scenario_id": scenario_id,
            "period": "2025-01 to 2025-12",
            "key_highlights": [
                "Strong revenue growth of 12% year-over-year",
                "Successful retention with churn rate below 5%",
                "High utilization rate of 85% across all roles"
            ],
            "key_concerns": [
                "Recruitment targets missed by 8% in Q3",
                "Salary costs growing faster than revenue"
            ],
            "recommendations": [
                "Increase recruitment efforts in high-demand roles",
                "Review salary progression policies",
                "Implement retention programs for senior levels"
            ],
            "overall_health_score": 78
        }
        
        with patch('backend.routers.simulation_v2.generate_executive_summary_service') as mock_summary_service:
            mock_summary_service.return_value = mock_summary
            
            response = client.get(f"/api/v2/executive-summary/{scenario_id}")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["scenario_id"] == scenario_id
            assert len(data["key_highlights"]) > 0
            assert len(data["recommendations"]) > 0
            assert data["overall_health_score"] == 78


class TestDataManagementEndpoints:
    """Test data management endpoints (snapshots, business plans)"""

    def test_list_snapshots_endpoint(self, client):
        """Test list available snapshots endpoint"""
        mock_snapshots = [
            {
                "id": "snapshot-1",
                "office_id": "Stockholm",
                "snapshot_date": "2025-01",
                "name": "Stockholm January 2025",
                "workforce_count": 850
            },
            {
                "id": "snapshot-2",
                "office_id": "Munich",
                "snapshot_date": "2025-01",
                "name": "Munich January 2025",
                "workforce_count": 450
            }
        ]
        
        with patch('backend.routers.simulation_v2.list_snapshots_service') as mock_list:
            mock_list.return_value = mock_snapshots
            
            response = client.get("/api/v2/snapshots")
            
            assert response.status_code == 200
            data = response.json()
            
            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]["office_id"] == "Stockholm"
            assert data[1]["office_id"] == "Munich"

    def test_get_snapshot_details_endpoint(self, client):
        """Test get snapshot details endpoint"""
        snapshot_id = "snapshot-123"
        
        mock_snapshot_details = {
            "id": snapshot_id,
            "office_id": "Stockholm",
            "snapshot_date": "2025-01",
            "name": "Stockholm January 2025",
            "workforce_count": 850,
            "role_breakdown": {
                "Consultant": 680,
                "Operations": 170
            },
            "level_breakdown": {
                "A": 120, "AC": 100, "C": 80,
                "SC": 60, "P": 40, "SP": 20
            }
        }
        
        with patch('backend.routers.simulation_v2.get_snapshot_details_service') as mock_details:
            mock_details.return_value = mock_snapshot_details
            
            response = client.get(f"/api/v2/snapshots/{snapshot_id}")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["id"] == snapshot_id
            assert data["office_id"] == "Stockholm"
            assert "role_breakdown" in data
            assert "level_breakdown" in data

    def test_list_business_plans_endpoint(self, client):
        """Test list business plans endpoint"""
        mock_plans = [
            {
                "id": "plan-1",
                "office_id": "Stockholm",
                "name": "Stockholm Growth Plan 2025-2027",
                "date_range": "2025-01 to 2027-12",
                "status": "active"
            },
            {
                "id": "plan-2", 
                "office_id": "Munich",
                "name": "Munich Expansion Plan 2025-2026",
                "date_range": "2025-01 to 2026-12",
                "status": "draft"
            }
        ]
        
        with patch('backend.routers.simulation_v2.list_business_plans_service') as mock_list:
            mock_list.return_value = mock_plans
            
            response = client.get("/api/v2/business-plans")
            
            assert response.status_code == 200
            data = response.json()
            
            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]["office_id"] == "Stockholm"

    def test_validate_scenario_endpoint(self, client, mock_scenario_request):
        """Test scenario validation endpoint"""
        mock_validation = {
            "is_valid": True,
            "errors": [],
            "warnings": [
                {
                    "type": "data_availability",
                    "message": "Business plan data incomplete for months 10-12"
                }
            ]
        }
        
        with patch('backend.routers.simulation_v2.validate_scenario_service') as mock_validate:
            mock_validate.return_value = mock_validation
            
            response = client.post("/api/v2/scenarios/validate", json=mock_scenario_request)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["is_valid"] is True
            assert len(data["errors"]) == 0
            assert len(data["warnings"]) == 1


class TestAPIPerformanceAndMonitoring:
    """Test API performance monitoring and optimization"""

    def test_performance_metrics_endpoint(self, client):
        """Test performance metrics endpoint"""
        mock_metrics = {
            "api_version": "2.0.0",
            "uptime_seconds": 3600,
            "total_requests": 1543,
            "average_response_time_ms": 245,
            "active_simulations": 3,
            "cache_hit_rate": 0.73,
            "memory_usage_mb": 512,
            "cpu_usage_percent": 15.2
        }
        
        with patch('backend.routers.simulation_v2.get_performance_metrics') as mock_perf:
            mock_perf.return_value = mock_metrics
            
            response = client.get("/api/v2/metrics")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "total_requests" in data
            assert "average_response_time_ms" in data
            assert "cache_hit_rate" in data

    def test_api_rate_limiting(self, client, mock_scenario_request):
        """Test API rate limiting functionality"""
        # This would test rate limiting if implemented
        # For now, verify multiple requests don't crash
        
        responses = []
        for i in range(5):  # Multiple rapid requests
            mock_scenario_request["name"] = f"Rate Test {i}"
            
            with patch('backend.routers.simulation_v2.execute_scenario_service') as mock_execute:
                mock_execute.return_value = Mock(scenario_id=f"scenario-{i}")
                
                response = client.post("/api/v2/scenarios/execute", json=mock_scenario_request)
                responses.append(response.status_code)
        
        # All should succeed (or implement actual rate limiting test)
        assert all(status in [200, 429] for status in responses)  # 429 = Too Many Requests

    def test_request_timeout_handling(self, client, mock_scenario_request):
        """Test request timeout handling"""
        with patch('backend.routers.simulation_v2.execute_scenario_service') as mock_execute:
            # Simulate very slow execution
            import time
            def slow_execution(*args, **kwargs):
                time.sleep(0.1)  # Simulate delay
                raise Exception("Execution timeout")
            
            mock_execute.side_effect = slow_execution
            
            response = client.post("/api/v2/scenarios/execute", json=mock_scenario_request)
            
            # Should handle timeout gracefully
            assert response.status_code in [500, 504]  # Internal error or Gateway timeout

    def test_concurrent_api_requests(self, client, mock_scenario_request):
        """Test concurrent API request handling"""
        import threading
        import time
        
        results = []
        
        def make_request(request_id):
            try:
                test_request = mock_scenario_request.copy()
                test_request["name"] = f"Concurrent Test {request_id}"
                
                with patch('backend.routers.simulation_v2.execute_scenario_service') as mock_execute:
                    mock_execute.return_value = Mock(scenario_id=f"scenario-{request_id}")
                    
                    response = client.post("/api/v2/scenarios/execute", json=test_request)
                    results.append(response.status_code)
                    
            except Exception as e:
                results.append(500)  # Error occurred
        
        # Create multiple concurrent threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join(timeout=10)
        
        # All should complete successfully
        assert len(results) == 3
        assert all(status == 200 for status in results)


class TestAPIDocumentationAndOpenAPI:
    """Test API documentation and OpenAPI schema"""

    def test_openapi_schema_endpoint(self, client):
        """Test OpenAPI schema is accessible"""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        
        # Verify basic OpenAPI structure
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        
        # Verify V2 endpoints are documented
        paths = schema["paths"]
        assert "/api/v2/scenarios/execute" in paths
        assert "/api/v2/kpis/calculate" in paths
        assert "/api/v2/health" in paths

    def test_api_docs_endpoint(self, client):
        """Test API documentation UI is accessible"""
        response = client.get("/docs")
        
        assert response.status_code == 200
        # Should return HTML for Swagger UI
        assert "text/html" in response.headers.get("content-type", "")

    def test_redoc_endpoint(self, client):
        """Test ReDoc documentation is accessible"""
        response = client.get("/redoc")
        
        assert response.status_code == 200
        # Should return HTML for ReDoc
        assert "text/html" in response.headers.get("content-type", "")

    def test_endpoint_parameter_validation(self, client):
        """Test API parameter validation through schema"""
        # Test invalid parameter types
        invalid_request = {
            "name": 123,  # Should be string
            "time_range": {
                "start_year": "invalid",  # Should be int
                "start_month": 1,
                "end_year": 2025,
                "end_month": 12
            },
            "office_scope": "Stockholm",  # Should be list
            "levers": {
                "recruitment_multiplier": "invalid"  # Should be float
            }
        }
        
        response = client.post("/api/v2/scenarios/execute", json=invalid_request)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data
        
        # Should have validation errors for each invalid field
        errors = data["detail"]
        assert len(errors) > 0