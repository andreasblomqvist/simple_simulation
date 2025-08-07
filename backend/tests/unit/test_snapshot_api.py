"""
Unit tests for snapshot FastAPI endpoints
Tests HTTP requests, response formatting, error handling, and validation
"""

import pytest
from datetime import datetime, date
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

from fastapi.testclient import TestClient
from fastapi import HTTPException
import json

# Import the FastAPI app or create a test app with the snapshot router
from backend.routers.snapshots import router, convert_snapshot_to_response
from backend.src.services.snapshot_service import (
    SnapshotService, SnapshotCreationRequest, SimulationSnapshotRequest,
    SnapshotComparison as ServiceSnapshotComparison
)
from backend.src.database.models import PopulationSnapshot, SnapshotSource, Office


@pytest.fixture
def mock_snapshot_service():
    """Mock SnapshotService for testing"""
    service = AsyncMock(spec=SnapshotService)
    return service


@pytest.fixture
def test_client(mock_snapshot_service):
    """Create test client with mocked dependencies"""
    from fastapi import FastAPI
    
    app = FastAPI()
    app.include_router(router)
    
    # Override dependency
    app.dependency_overrides[router.get_snapshot_service_dep] = lambda: mock_snapshot_service
    
    return TestClient(app), mock_snapshot_service


@pytest.fixture
def sample_office():
    """Create sample office for testing"""
    office = MagicMock(spec=Office)
    office.id = uuid4()
    office.name = "Test Office"
    return office


@pytest.fixture
def sample_snapshot(sample_office):
    """Create sample PopulationSnapshot for testing"""
    snapshot = MagicMock(spec=PopulationSnapshot)
    snapshot.id = uuid4()
    snapshot.office_id = sample_office.id
    snapshot.office = sample_office
    snapshot.snapshot_name = "Test Snapshot"
    snapshot.snapshot_date = "202501"
    snapshot.description = "Test description"
    snapshot.total_fte = 50
    snapshot.is_default = False
    snapshot.is_approved = True
    snapshot.source = SnapshotSource.CURRENT
    snapshot.created_at = datetime(2025, 1, 15, 10, 30, 0)
    snapshot.created_by = "test@example.com"
    snapshot.last_used_at = None
    snapshot.metadata = {"test": True}
    
    # Mock methods
    snapshot.tag_list = ["quarterly", "approved"]
    snapshot.to_dict.return_value = {
        "workforce_data": {
            "Consultant": {"A": 15, "AC": 10},
            "Operations": 5
        }
    }
    
    return snapshot


class TestSnapshotCreationEndpoints:
    """Test snapshot creation endpoints"""
    
    def test_create_snapshot_from_current_success(self, test_client, sample_snapshot):
        """Test successful creation of snapshot from current workforce"""
        client, mock_service = test_client
        mock_service.create_snapshot_from_current.return_value = sample_snapshot
        
        request_data = {
            "office_id": str(sample_snapshot.office_id),
            "snapshot_name": "New Current Snapshot",
            "description": "Snapshot from current workforce",
            "tags": ["current", "baseline"],
            "is_default": True,
            "created_by": "admin@example.com"
        }
        
        response = client.post("/snapshots/", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert data["id"] == str(sample_snapshot.id)
        assert data["office_id"] == str(sample_snapshot.office_id)
        assert data["snapshot_name"] == sample_snapshot.snapshot_name
        assert data["total_fte"] == sample_snapshot.total_fte
        assert data["is_default"] == sample_snapshot.is_default
        assert data["is_approved"] == sample_snapshot.is_approved
        assert data["source"] == sample_snapshot.source.value
        assert data["tags"] == sample_snapshot.tag_list
        
        # Verify service was called with correct parameters
        mock_service.create_snapshot_from_current.assert_called_once()
        call_args = mock_service.create_snapshot_from_current.call_args[0][0]
        assert isinstance(call_args, SnapshotCreationRequest)
        assert call_args.office_id == UUID(request_data["office_id"])
        assert call_args.snapshot_name == request_data["snapshot_name"]
        assert call_args.is_default == request_data["is_default"]
    
    def test_create_snapshot_from_current_validation_errors(self, test_client):
        """Test validation errors for create snapshot request"""
        client, mock_service = test_client
        
        # Test missing required fields
        response = client.post("/snapshots/", json={})
        assert response.status_code == 422
        
        # Test invalid office_id format
        invalid_data = {
            "office_id": "not-a-uuid",
            "snapshot_name": "Test",
            "created_by": "test@example.com"
        }
        response = client.post("/snapshots/", json=invalid_data)
        assert response.status_code == 422
        
        # Test empty snapshot_name
        invalid_data = {
            "office_id": str(uuid4()),
            "snapshot_name": "",
            "created_by": "test@example.com"
        }
        response = client.post("/snapshots/", json=invalid_data)
        assert response.status_code == 422
        
        # Test snapshot_name too long
        invalid_data = {
            "office_id": str(uuid4()),
            "snapshot_name": "x" * 201,  # Over 200 character limit
            "created_by": "test@example.com"
        }
        response = client.post("/snapshots/", json=invalid_data)
        assert response.status_code == 422
    
    def test_create_snapshot_from_current_service_error(self, test_client):
        """Test handling of service errors during creation"""
        client, mock_service = test_client
        mock_service.create_snapshot_from_current.side_effect = ValueError("Office not found")
        
        request_data = {
            "office_id": str(uuid4()),
            "snapshot_name": "Test Snapshot",
            "created_by": "test@example.com"
        }
        
        response = client.post("/snapshots/", json=request_data)
        
        assert response.status_code == 400
        assert "Office not found" in response.json()["detail"]
    
    def test_create_snapshot_from_current_internal_error(self, test_client):
        """Test handling of unexpected internal errors"""
        client, mock_service = test_client
        mock_service.create_snapshot_from_current.side_effect = Exception("Database connection failed")
        
        request_data = {
            "office_id": str(uuid4()),
            "snapshot_name": "Test Snapshot",
            "created_by": "test@example.com"
        }
        
        response = client.post("/snapshots/", json=request_data)
        
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]
    
    def test_create_snapshot_from_simulation_success(self, test_client, sample_snapshot):
        """Test successful creation from simulation results"""
        client, mock_service = test_client
        mock_service.create_snapshot_from_simulation.return_value = sample_snapshot
        
        simulation_results = {
            "2025": {
                "Test Office": {
                    "roles": {
                        "Consultant": {
                            "A": [10, 11, 12, 13, 14, 15],
                            "AC": [5, 6, 7, 8, 9, 10]
                        },
                        "Operations": [3, 4, 5, 6, 7, 8]
                    }
                }
            }
        }
        
        request_data = {
            "office_name": "Test Office",
            "simulation_results": simulation_results,
            "snapshot_date": "202503",
            "snapshot_name": "Simulation March 2025",
            "description": "Projected workforce",
            "tags": ["simulation", "q1"],
            "created_by": "analyst@example.com"
        }
        
        response = client.post("/snapshots/from-simulation", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_snapshot.id)
        
        # Verify service call
        mock_service.create_snapshot_from_simulation.assert_called_once()
        call_args = mock_service.create_snapshot_from_simulation.call_args[0][0]
        assert isinstance(call_args, SimulationSnapshotRequest)
        assert call_args.office_name == "Test Office"
        assert call_args.snapshot_date == "202503"
    
    def test_create_snapshot_from_simulation_date_validation(self, test_client):
        """Test date validation for simulation snapshot"""
        client, mock_service = test_client
        
        # Test invalid date format
        invalid_data = {
            "office_name": "Test Office",
            "simulation_results": {},
            "snapshot_date": "2025-03",  # Should be YYYYMM
            "snapshot_name": "Test",
            "created_by": "test@example.com"
        }
        
        response = client.post("/snapshots/from-simulation", json=invalid_data)
        assert response.status_code == 422
        
        # Test invalid month
        invalid_data = {
            "office_name": "Test Office",
            "simulation_results": {},
            "snapshot_date": "202513",  # Month 13 doesn't exist
            "snapshot_name": "Test",
            "created_by": "test@example.com"
        }
        
        response = client.post("/snapshots/from-simulation", json=invalid_data)
        assert response.status_code == 422
    
    def test_create_snapshot_from_business_plan_success(self, test_client, sample_snapshot):
        """Test successful creation from business plan"""
        client, mock_service = test_client
        mock_service.create_snapshot_from_business_plan.return_value = sample_snapshot
        
        business_plan_data = {
            "entries": [
                {
                    "year": 2025, "month": 6, "role": "Consultant", "level": "A",
                    "recruitment": 12, "churn": 2
                },
                {
                    "year": 2025, "month": 6, "role": "Operations",
                    "recruitment": 5, "churn": 1
                }
            ]
        }
        
        request_data = {
            "office_id": str(uuid4()),
            "business_plan_data": business_plan_data,
            "snapshot_name": "Business Plan June 2025",
            "snapshot_date": "202506",
            "description": "Business plan projection",
            "tags": ["business-plan"],
            "created_by": "planner@example.com"
        }
        
        response = client.post("/snapshots/from-business-plan", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_snapshot.id)
        
        # Verify service call
        mock_service.create_snapshot_from_business_plan.assert_called_once()


class TestSnapshotRetrievalEndpoints:
    """Test snapshot retrieval endpoints"""
    
    def test_get_snapshot_by_id_success(self, test_client, sample_snapshot):
        """Test successful retrieval of snapshot by ID"""
        client, mock_service = test_client
        mock_service.get_snapshot.return_value = sample_snapshot
        
        response = client.get(f"/snapshots/{sample_snapshot.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_snapshot.id)
        assert data["snapshot_name"] == sample_snapshot.snapshot_name
        
        mock_service.get_snapshot.assert_called_once_with(sample_snapshot.id)
    
    def test_get_snapshot_by_id_not_found(self, test_client):
        """Test handling when snapshot is not found"""
        client, mock_service = test_client
        mock_service.get_snapshot.return_value = None
        
        snapshot_id = uuid4()
        response = client.get(f"/snapshots/{snapshot_id}")
        
        assert response.status_code == 404
        assert "Snapshot not found" in response.json()["detail"]
    
    def test_get_snapshot_by_id_invalid_uuid(self, test_client):
        """Test handling of invalid UUID format"""
        client, mock_service = test_client
        
        response = client.get("/snapshots/not-a-uuid")
        
        assert response.status_code == 422  # Validation error
    
    def test_search_snapshots_success(self, test_client, sample_snapshot):
        """Test successful snapshot search"""
        client, mock_service = test_client
        mock_service.search_snapshots.return_value = ([sample_snapshot], 1)
        
        response = client.get(
            "/snapshots/",
            params={
                "office_id": str(sample_snapshot.office_id),
                "tags": "quarterly,approved",
                "source": "current",
                "approved_only": True,
                "page": 1,
                "limit": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_count"] == 1
        assert data["page"] == 1
        assert data["limit"] == 10
        assert len(data["snapshots"]) == 1
        assert data["snapshots"][0]["id"] == str(sample_snapshot.id)
        
        # Verify service call parameters
        mock_service.search_snapshots.assert_called_once()
        call_kwargs = mock_service.search_snapshots.call_args.kwargs
        assert call_kwargs["office_id"] == sample_snapshot.office_id
        assert call_kwargs["tags"] == ["quarterly", "approved"]
        assert call_kwargs["approved_only"] is True
        assert call_kwargs["limit"] == 10
        assert call_kwargs["offset"] == 0  # page 1 = offset 0
    
    def test_search_snapshots_pagination(self, test_client, sample_snapshot):
        """Test search pagination calculations"""
        client, mock_service = test_client
        mock_service.search_snapshots.return_value = ([sample_snapshot], 25)
        
        # Test page 3 with limit 10 = offset 20
        response = client.get(
            "/snapshots/",
            params={"page": 3, "limit": 10}
        )
        
        assert response.status_code == 200
        
        call_kwargs = mock_service.search_snapshots.call_args.kwargs
        assert call_kwargs["offset"] == 20  # (3-1) * 10
        assert call_kwargs["limit"] == 10
    
    def test_search_snapshots_validation(self, test_client):
        """Test search parameter validation"""
        client, mock_service = test_client
        
        # Test invalid page number
        response = client.get("/snapshots/", params={"page": 0})
        assert response.status_code == 422
        
        # Test limit too high
        response = client.get("/snapshots/", params={"limit": 101})
        assert response.status_code == 422
        
        # Test limit too low
        response = client.get("/snapshots/", params={"limit": 0})
        assert response.status_code == 422
    
    def test_search_snapshots_empty_results(self, test_client):
        """Test search with no results"""
        client, mock_service = test_client
        mock_service.search_snapshots.return_value = ([], 0)
        
        response = client.get("/snapshots/", params={"search_term": "nonexistent"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 0
        assert len(data["snapshots"]) == 0


class TestSnapshotUpdateEndpoints:
    """Test snapshot update endpoints"""
    
    def test_update_snapshot_success(self, test_client, sample_snapshot):
        """Test successful snapshot update"""
        client, mock_service = test_client
        
        # Create updated snapshot
        updated_snapshot = MagicMock(spec=PopulationSnapshot)
        updated_snapshot.id = sample_snapshot.id
        updated_snapshot.office_id = sample_snapshot.office_id
        updated_snapshot.office = sample_snapshot.office
        updated_snapshot.snapshot_name = "Updated Name"
        updated_snapshot.description = "Updated description"
        updated_snapshot.is_approved = True
        updated_snapshot.snapshot_date = sample_snapshot.snapshot_date
        updated_snapshot.total_fte = sample_snapshot.total_fte
        updated_snapshot.is_default = sample_snapshot.is_default
        updated_snapshot.source = sample_snapshot.source
        updated_snapshot.created_at = sample_snapshot.created_at
        updated_snapshot.created_by = sample_snapshot.created_by
        updated_snapshot.last_used_at = sample_snapshot.last_used_at
        updated_snapshot.metadata = sample_snapshot.metadata
        updated_snapshot.tag_list = sample_snapshot.tag_list
        updated_snapshot.to_dict.return_value = sample_snapshot.to_dict.return_value
        
        mock_service.update_snapshot.return_value = updated_snapshot
        
        update_data = {
            "snapshot_name": "Updated Name",
            "description": "Updated description",
            "is_approved": True,
            "updated_by": "admin@example.com"
        }
        
        response = client.put(f"/snapshots/{sample_snapshot.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["snapshot_name"] == "Updated Name"
        assert data["description"] == "Updated description"
        
        mock_service.update_snapshot.assert_called_once()
    
    def test_set_default_snapshot_success(self, test_client, sample_snapshot):
        """Test setting snapshot as default"""
        client, mock_service = test_client
        mock_service.set_default_snapshot.return_value = True
        
        response = client.post(
            f"/snapshots/{sample_snapshot.id}/set-default",
            params={"user_id": "admin@example.com"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        mock_service.set_default_snapshot.assert_called_once_with(
            sample_snapshot.id, "admin@example.com"
        )
    
    def test_approve_snapshot_success(self, test_client, sample_snapshot):
        """Test approving snapshot"""
        client, mock_service = test_client
        mock_service.approve_snapshot.return_value = True
        
        response = client.post(
            f"/snapshots/{sample_snapshot.id}/approve",
            params={"user_id": "approver@example.com"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        mock_service.approve_snapshot.assert_called_once_with(
            sample_snapshot.id, "approver@example.com"
        )
    
    def test_update_workforce_data_success(self, test_client, sample_snapshot):
        """Test updating workforce data"""
        client, mock_service = test_client
        mock_service.update_workforce_data.return_value = True
        
        new_workforce = {
            "Consultant": {"A": 20, "AC": 15, "C": 8},
            "Operations": 10,
            "Manager": {"M1": 3}
        }
        
        request_data = {"workforce_data": new_workforce}
        
        response = client.put(
            f"/snapshots/{sample_snapshot.id}/workforce",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        mock_service.update_workforce_data.assert_called_once_with(
            sample_snapshot.id, new_workforce
        )
    
    def test_update_tags_success(self, test_client, sample_snapshot):
        """Test updating snapshot tags"""
        client, mock_service = test_client
        mock_service.update_tags.return_value = True
        
        new_tags = ["updated", "validated", "q2-2025"]
        request_data = {"tags": new_tags}
        
        response = client.put(
            f"/snapshots/{sample_snapshot.id}/tags",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        mock_service.update_tags.assert_called_once_with(
            sample_snapshot.id, new_tags
        )
    
    def test_update_tags_validation(self, test_client, sample_snapshot):
        """Test tag validation (empty tags filtered out)"""
        client, mock_service = test_client
        mock_service.update_tags.return_value = True
        
        # Include empty and whitespace-only tags
        request_data = {"tags": ["valid", "", "  whitespace  ", "another_valid"]}
        
        response = client.put(
            f"/snapshots/{sample_snapshot.id}/tags",
            json=request_data
        )
        
        assert response.status_code == 200
        
        # Verify filtered tags were passed to service
        call_args = mock_service.update_tags.call_args
        passed_tags = call_args[0][1]
        assert len(passed_tags) == 3  # Empty tag filtered out
        assert "valid" in passed_tags
        assert "whitespace" in passed_tags  # Stripped
        assert "another_valid" in passed_tags
        assert "" not in passed_tags


class TestSnapshotComparisonEndpoints:
    """Test snapshot comparison endpoints"""
    
    def test_compare_snapshots_success(self, test_client, sample_snapshot, sample_office):
        """Test successful snapshot comparison"""
        client, mock_service = test_client
        
        # Create second snapshot for comparison
        snapshot_2 = MagicMock(spec=PopulationSnapshot)
        snapshot_2.id = uuid4()
        snapshot_2.office_id = sample_office.id
        snapshot_2.office = sample_office
        snapshot_2.snapshot_name = "Comparison Snapshot"
        snapshot_2.snapshot_date = "202506"
        snapshot_2.total_fte = 60
        snapshot_2.source = SnapshotSource.SIMULATION
        snapshot_2.created_at = datetime(2025, 6, 15, 10, 30, 0)
        snapshot_2.created_by = "analyst@example.com"
        snapshot_2.tag_list = ["simulation", "growth"]
        snapshot_2.to_dict.return_value = {
            "workforce_data": {
                "Consultant": {"A": 20, "AC": 15},
                "Operations": 8
            }
        }
        
        # Create comparison result
        comparison_result = ServiceSnapshotComparison(
            snapshot_1=sample_snapshot,
            snapshot_2=snapshot_2,
            total_fte_delta=10,
            workforce_changes={
                "Consultant": {
                    "A": {"from": 15, "to": 20, "change": 5},
                    "AC": {"from": 10, "to": 15, "change": 5}
                },
                "Operations": {
                    "total": {"from": 5, "to": 8, "change": 3}
                }
            },
            insights=[
                "Total workforce increased by 10 FTE",
                "All roles showed growth"
            ]
        )
        
        mock_service.compare_snapshots.return_value = comparison_result
        
        response = client.post(
            "/snapshots/compare",
            json={
                "baseline_id": str(sample_snapshot.id),
                "comparison_id": str(snapshot_2.id)
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_fte_delta"] == 10
        assert len(data["insights"]) == 2
        assert "Total workforce increased by 10 FTE" in data["insights"]
        
        # Verify snapshot data in response
        assert data["snapshot_1"]["id"] == str(sample_snapshot.id)
        assert data["snapshot_2"]["id"] == str(snapshot_2.id)
        
        # Verify workforce changes structure
        assert "Consultant" in data["workforce_changes"]
        assert "Operations" in data["workforce_changes"]
        
        mock_service.compare_snapshots.assert_called_once()
    
    def test_compare_snapshots_not_found(self, test_client):
        """Test comparison when snapshot doesn't exist"""
        client, mock_service = test_client
        mock_service.compare_snapshots.side_effect = ValueError("One or both snapshots not found")
        
        response = client.post(
            "/snapshots/compare",
            json={
                "baseline_id": str(uuid4()),
                "comparison_id": str(uuid4())
            }
        )
        
        assert response.status_code == 400
        assert "One or both snapshots not found" in response.json()["detail"]


class TestSnapshotDeletionEndpoints:
    """Test snapshot deletion endpoints"""
    
    def test_delete_snapshot_success(self, test_client, sample_snapshot):
        """Test successful snapshot deletion"""
        client, mock_service = test_client
        mock_service.delete_snapshot.return_value = True
        
        response = client.delete(f"/snapshots/{sample_snapshot.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        mock_service.delete_snapshot.assert_called_once_with(sample_snapshot.id)
    
    def test_delete_snapshot_not_found(self, test_client):
        """Test deleting non-existent snapshot"""
        client, mock_service = test_client
        mock_service.delete_snapshot.return_value = False
        
        response = client.delete(f"/snapshots/{uuid4()}")
        
        assert response.status_code == 404
        assert "Snapshot not found" in response.json()["detail"]


class TestSnapshotAuditEndpoints:
    """Test snapshot audit and tracking endpoints"""
    
    def test_get_audit_log_success(self, test_client, sample_snapshot):
        """Test retrieving audit log"""
        client, mock_service = test_client
        
        mock_audit_logs = [
            {
                "id": str(uuid4()),
                "action": "created",
                "entity_type": None,
                "entity_id": None,
                "user_id": "admin@example.com",
                "timestamp": "2025-01-15T10:30:00",
                "details": {"initial_fte": 50}
            },
            {
                "id": str(uuid4()),
                "action": "approved",
                "entity_type": None,
                "entity_id": None,
                "user_id": "approver@example.com",
                "timestamp": "2025-01-16T14:20:00",
                "details": {"approval_reason": "data_validated"}
            }
        ]
        
        mock_service.get_audit_log.return_value = mock_audit_logs
        
        response = client.get(f"/snapshots/{sample_snapshot.id}/audit-log")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["entries"]) == 2
        assert data["entries"][0]["action"] == "created"
        assert data["entries"][1]["action"] == "approved"
        
        mock_service.get_audit_log.assert_called_once_with(sample_snapshot.id, 50)
    
    def test_get_audit_log_with_limit(self, test_client, sample_snapshot):
        """Test retrieving audit log with custom limit"""
        client, mock_service = test_client
        mock_service.get_audit_log.return_value = []
        
        response = client.get(
            f"/snapshots/{sample_snapshot.id}/audit-log",
            params={"limit": 25}
        )
        
        assert response.status_code == 200
        mock_service.get_audit_log.assert_called_once_with(sample_snapshot.id, 25)


class TestUtilityFunctions:
    """Test utility functions and helpers"""
    
    def test_convert_snapshot_to_response(self, sample_snapshot):
        """Test conversion from database model to API response"""
        response = convert_snapshot_to_response(sample_snapshot)
        
        assert response.id == sample_snapshot.id
        assert response.office_id == sample_snapshot.office_id
        assert response.office_name == sample_snapshot.office.name
        assert response.snapshot_name == sample_snapshot.snapshot_name
        assert response.snapshot_date == sample_snapshot.snapshot_date
        assert response.description == sample_snapshot.description
        assert response.total_fte == sample_snapshot.total_fte
        assert response.is_default == sample_snapshot.is_default
        assert response.is_approved == sample_snapshot.is_approved
        assert response.source == sample_snapshot.source.value
        assert response.created_at == sample_snapshot.created_at
        assert response.created_by == sample_snapshot.created_by
        assert response.last_used_at == sample_snapshot.last_used_at
        assert response.tags == sample_snapshot.tag_list
        assert response.metadata == sample_snapshot.metadata
    
    def test_convert_snapshot_to_response_no_office(self, sample_snapshot):
        """Test conversion when office relationship is not loaded"""
        sample_snapshot.office = None
        
        response = convert_snapshot_to_response(sample_snapshot)
        
        assert response.office_name is None
        # Other fields should still be populated correctly
        assert response.id == sample_snapshot.id
        assert response.office_id == sample_snapshot.office_id
    
    def test_convert_snapshot_to_response_empty_metadata(self, sample_snapshot):
        """Test conversion with empty metadata"""
        sample_snapshot.metadata = None
        
        response = convert_snapshot_to_response(sample_snapshot)
        
        assert response.metadata == {}


class TestErrorHandling:
    """Test comprehensive error handling scenarios"""
    
    def test_internal_server_errors(self, test_client):
        """Test handling of unexpected server errors"""
        client, mock_service = test_client
        
        # Test different endpoints with internal errors
        mock_service.get_snapshot.side_effect = Exception("Database connection lost")
        
        response = client.get(f"/snapshots/{uuid4()}")
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]
        
        mock_service.search_snapshots.side_effect = Exception("Search index corrupted")
        
        response = client.get("/snapshots/")
        assert response.status_code == 500
    
    def test_validation_error_details(self, test_client):
        """Test that validation errors provide helpful details"""
        client, mock_service = test_client
        
        # Test multiple validation errors in single request
        response = client.post("/snapshots/", json={
            "office_id": "invalid-uuid",
            "snapshot_name": "",  # Empty string
            "created_by": ""  # Empty string
        })
        
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data
        
        # Should have multiple validation errors
        errors = error_data["detail"]
        assert len(errors) >= 2  # At least office_id and name errors
    
    def test_http_method_not_allowed(self, test_client):
        """Test proper handling of unsupported HTTP methods"""
        client, mock_service = test_client
        
        # Test unsupported methods
        response = client.patch("/snapshots/")
        assert response.status_code == 405
        
        response = client.put("/snapshots/")
        assert response.status_code == 405
    
    def test_request_timeout_simulation(self, test_client):
        """Test handling of request timeouts (simulated)"""
        client, mock_service = test_client
        
        # Simulate timeout with very slow response
        import asyncio
        
        async def slow_response(*args, **kwargs):
            await asyncio.sleep(10)  # Simulate slow operation
            return MagicMock()
        
        mock_service.create_snapshot_from_current = slow_response
        
        # Note: This test would require custom timeout configuration
        # In a real implementation, you'd configure request timeouts
        # and test that they're handled appropriately