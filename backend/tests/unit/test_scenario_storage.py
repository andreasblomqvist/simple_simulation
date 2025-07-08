"""
Unit tests for ScenarioStorageService.
"""
import json
import os
import tempfile
import shutil
from datetime import datetime
import pytest
from unittest.mock import patch, mock_open

from src.services.scenario_storage import ScenarioStorageService
from src.services.scenario_models import ScenarioDefinition


class TestScenarioStorageService:
    """Test cases for ScenarioStorageService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.storage_service = ScenarioStorageService(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_creates_directories(self):
        """Test that initialization creates required directories."""
        # Create a new service with a fresh temp directory
        fresh_temp_dir = tempfile.mkdtemp()
        try:
            service = ScenarioStorageService(fresh_temp_dir)
            
            # Check that directories were created
            assert os.path.exists(service.definitions_dir)
            assert os.path.exists(service.results_dir)
            assert os.path.isdir(service.definitions_dir)
            assert os.path.isdir(service.results_dir)
            
        finally:
            shutil.rmtree(fresh_temp_dir, ignore_errors=True)
    
    def test_create_scenario_success(self):
        """Test successful scenario creation."""
        scenario_def = ScenarioDefinition(
            name="Test Scenario",
            description="A test scenario",
            time_range={
                "start_year": 2024,
                "start_month": 1,
                "end_year": 2026,
                "end_month": 12
            },
            office_scope=["Stockholm", "Gothenburg"]
        )
        
        scenario_id = self.storage_service.create_scenario(scenario_def)
        
        # Verify scenario was created
        assert scenario_id is not None
        assert len(scenario_id) > 0
        
        # Verify file exists
        file_path = os.path.join(self.storage_service.definitions_dir, f"{scenario_id}.json")
        assert os.path.exists(file_path)
        
        # Verify file content
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        assert data['name'] == "Test Scenario"
        assert data['description'] == "A test scenario"
        assert data['id'] == scenario_id
        assert 'created_at' in data
        assert 'updated_at' in data
    
    def test_create_scenario_with_existing_id(self):
        """Test scenario creation with existing ID."""
        scenario_def = ScenarioDefinition(
            id="existing-id-123",
            name="Test Scenario",
            description="A test scenario",
            time_range={
                "start_year": 2024,
                "start_month": 1,
                "end_year": 2026,
                "end_month": 12
            }
        )
        
        scenario_id = self.storage_service.create_scenario(scenario_def)
        
        assert scenario_id == "existing-id-123"
        
        # Verify file exists with the specified ID
        file_path = os.path.join(self.storage_service.definitions_dir, "existing-id-123.json")
        assert os.path.exists(file_path)
    
    def test_create_scenario_with_existing_timestamps(self):
        """Test scenario creation with existing timestamps."""
        existing_timestamp = "2024-01-01T00:00:00"
        scenario_def = ScenarioDefinition(
            name="Test Scenario",
            description="A test scenario",
            created_at=existing_timestamp,
            time_range={
                "start_year": 2024,
                "start_month": 1,
                "end_year": 2026,
                "end_month": 12
            }
        )
        
        scenario_id = self.storage_service.create_scenario(scenario_def)
        
        # Verify file content
        file_path = os.path.join(self.storage_service.definitions_dir, f"{scenario_id}.json")
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        assert data['created_at'] == existing_timestamp
        assert data['updated_at'] != existing_timestamp  # Should be updated
    
    def test_create_scenario_file_error(self):
        """Test scenario creation with file I/O error."""
        scenario_def = ScenarioDefinition(
            name="Test Scenario",
            description="A test scenario",
            time_range={
                "start_year": 2024,
                "start_month": 1,
                "end_year": 2026,
                "end_month": 12
            }
        )
        
        # Mock file open to raise an exception
        with patch('builtins.open', side_effect=OSError("Permission denied")):
            with pytest.raises(OSError, match="Permission denied"):
                self.storage_service.create_scenario(scenario_def)
    
    def test_get_scenario_success(self):
        """Test successful scenario retrieval."""
        # Create a scenario first
        scenario_def = ScenarioDefinition(
            name="Test Scenario",
            description="A test scenario",
            time_range={
                "start_year": 2024,
                "start_month": 1,
                "end_year": 2026,
                "end_month": 12
            }
        )
        
        scenario_id = self.storage_service.create_scenario(scenario_def)
        
        # Retrieve the scenario
        retrieved_scenario = self.storage_service.get_scenario(scenario_id)
        
        assert retrieved_scenario is not None
        assert retrieved_scenario.name == "Test Scenario"
        assert retrieved_scenario.description == "A test scenario"
        assert retrieved_scenario.id == scenario_id
    
    def test_get_scenario_not_found(self):
        """Test scenario retrieval when scenario doesn't exist."""
        retrieved_scenario = self.storage_service.get_scenario("non-existent-id")
        
        assert retrieved_scenario is None
    
    def test_get_scenario_invalid_json(self):
        """Test scenario retrieval with invalid JSON file."""
        # Create a file with invalid JSON
        file_path = os.path.join(self.storage_service.definitions_dir, "invalid.json")
        with open(file_path, 'w') as f:
            f.write("invalid json content")
        
        retrieved_scenario = self.storage_service.get_scenario("invalid")
        
        assert retrieved_scenario is None
    
    def test_update_scenario_success(self):
        """Test successful scenario update."""
        # Create a scenario first
        scenario_def = ScenarioDefinition(
            name="Original Name",
            description="Original description",
            time_range={
                "start_year": 2024,
                "start_month": 1,
                "end_year": 2026,
                "end_month": 12
            }
        )
        
        scenario_id = self.storage_service.create_scenario(scenario_def)
        
        # Update the scenario
        updated_scenario = ScenarioDefinition(
            name="Updated Name",
            description="Updated description",
            time_range={
                "start_year": 2024,
                "start_month": 1,
                "end_year": 2026,
                "end_month": 12
            }
        )
        
        success = self.storage_service.update_scenario(scenario_id, updated_scenario)
        
        assert success is True
        
        # Verify the update
        retrieved_scenario = self.storage_service.get_scenario(scenario_id)
        assert retrieved_scenario.name == "Updated Name"
        assert retrieved_scenario.description == "Updated description"
        assert retrieved_scenario.id == scenario_id
    
    def test_update_scenario_not_found(self):
        """Test scenario update when scenario doesn't exist."""
        updated_scenario = ScenarioDefinition(
            name="Updated Name",
            description="Updated description",
            time_range={
                "start_year": 2024,
                "start_month": 1,
                "end_year": 2026,
                "end_month": 12
            }
        )
        
        success = self.storage_service.update_scenario("non-existent-id", updated_scenario)
        
        assert success is False
    
    def test_update_scenario_file_error(self):
        """Test scenario update with file I/O error."""
        # Create a scenario first
        scenario_def = ScenarioDefinition(
            name="Original Name",
            description="Original description",
            time_range={
                "start_year": 2024,
                "start_month": 1,
                "end_year": 2026,
                "end_month": 12
            }
        )
        
        scenario_id = self.storage_service.create_scenario(scenario_def)
        
        # Update the scenario with file error
        updated_scenario = ScenarioDefinition(
            name="Updated Name",
            description="Updated description",
            time_range={
                "start_year": 2024,
                "start_month": 1,
                "end_year": 2026,
                "end_month": 12
            }
        )
        
        with patch('builtins.open', side_effect=OSError("Permission denied")):
            success = self.storage_service.update_scenario(scenario_id, updated_scenario)
        
        assert success is False
    
    def test_delete_scenario_success(self):
        """Test successful scenario deletion."""
        # Create a scenario first
        scenario_def = ScenarioDefinition(
            name="Test Scenario",
            description="A test scenario",
            time_range={
                "start_year": 2024,
                "start_month": 1,
                "end_year": 2026,
                "end_month": 12
            }
        )
        
        scenario_id = self.storage_service.create_scenario(scenario_def)
        
        # Create some results for the scenario
        results = {"test": "data"}
        self.storage_service.save_scenario_results(scenario_id, results)
        
        # Delete the scenario
        success = self.storage_service.delete_scenario(scenario_id)
        
        assert success is True
        
        # Verify scenario is deleted
        assert not self.storage_service.scenario_exists(scenario_id)
        assert not self.storage_service.results_exist(scenario_id)
    
    def test_delete_scenario_not_found(self):
        """Test scenario deletion when scenario doesn't exist."""
        success = self.storage_service.delete_scenario("non-existent-id")
        
        assert success is True  # Should return True even if nothing to delete
    
    def test_delete_scenario_partial_failure(self):
        """Test scenario deletion with partial failure."""
        # Create a scenario first
        scenario_def = ScenarioDefinition(
            name="Test Scenario",
            description="A test scenario",
            time_range={
                "start_year": 2024,
                "start_month": 1,
                "end_year": 2026,
                "end_month": 12
            }
        )
        
        scenario_id = self.storage_service.create_scenario(scenario_def)
        
        # Mock os.remove to fail for results file
        with patch('os.remove', side_effect=[None, OSError("Permission denied")]):
            success = self.storage_service.delete_scenario(scenario_id)
        
        assert success is False
    
    def test_list_scenarios_empty(self):
        """Test listing scenarios when none exist."""
        scenarios = self.storage_service.list_scenarios()
        
        assert scenarios == []
    
    def test_list_scenarios_with_data(self):
        """Test listing scenarios with existing data."""
        # Create multiple scenarios
        scenario1 = ScenarioDefinition(
            name="Scenario 1",
            description="First scenario",
            time_range={
                "start_year": 2024,
                "start_month": 1,
                "end_year": 2026,
                "end_month": 12
            }
        )
        
        scenario2 = ScenarioDefinition(
            name="Scenario 2",
            description="Second scenario",
            time_range={
                "start_year": 2024,
                "start_month": 1,
                "end_year": 2026,
                "end_month": 12
            }
        )
        
        self.storage_service.create_scenario(scenario1)
        self.storage_service.create_scenario(scenario2)
        
        scenarios = self.storage_service.list_scenarios()
        
        assert len(scenarios) == 2
        assert all('id' in scenario for scenario in scenarios)
        assert all('name' in scenario for scenario in scenarios)
        assert all('description' in scenario for scenario in scenarios)
        assert all('created_at' in scenario for scenario in scenarios)
        assert all('updated_at' in scenario for scenario in scenarios)
        assert all('time_range' in scenario for scenario in scenarios)
        assert all('office_scope' in scenario for scenario in scenarios)
    
    def test_list_scenarios_with_invalid_file(self):
        """Test listing scenarios with invalid file in directory."""
        # Create a valid scenario
        scenario_def = ScenarioDefinition(
            name="Test Scenario",
            description="A test scenario",
            time_range={
                "start_year": 2024,
                "start_month": 1,
                "end_year": 2026,
                "end_month": 12
            }
        )
        
        self.storage_service.create_scenario(scenario_def)
        
        # Create an invalid file
        invalid_file_path = os.path.join(self.storage_service.definitions_dir, "invalid.txt")
        with open(invalid_file_path, 'w') as f:
            f.write("not a json file")
        
        scenarios = self.storage_service.list_scenarios()
        
        # Should only return the valid scenario
        assert len(scenarios) == 1
        assert scenarios[0]['name'] == "Test Scenario"
    
    def test_save_scenario_results_success(self):
        """Test successful scenario results saving."""
        results = {
            "monthly_data": {
                "2024-01": {"fte": 100, "revenue": 1000000},
                "2024-02": {"fte": 105, "revenue": 1050000}
            },
            "summary": {
                "total_fte": 105,
                "total_revenue": 2050000
            }
        }
        
        success = self.storage_service.save_scenario_results("test-scenario-id", results)
        
        assert success is True
        
        # Verify results file exists
        file_path = os.path.join(self.storage_service.results_dir, "test-scenario-id_results.json")
        assert os.path.exists(file_path)
        
        # Verify file content
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        assert data['scenario_id'] == "test-scenario-id"
        assert 'saved_at' in data
        assert data['results'] == results
    
    def test_save_scenario_results_file_error(self):
        """Test scenario results saving with file I/O error."""
        results = {"test": "data"}
        
        with patch('builtins.open', side_effect=OSError("Permission denied")):
            success = self.storage_service.save_scenario_results("test-scenario-id", results)
        
        assert success is False
    
    def test_get_scenario_results_success(self):
        """Test successful scenario results retrieval."""
        # Save results first
        results = {
            "monthly_data": {
                "2024-01": {"fte": 100, "revenue": 1000000}
            }
        }
        
        self.storage_service.save_scenario_results("test-scenario-id", results)
        
        # Retrieve results
        retrieved_results = self.storage_service.get_scenario_results("test-scenario-id")
        
        assert retrieved_results == results
    
    def test_get_scenario_results_not_found(self):
        """Test scenario results retrieval when results don't exist."""
        retrieved_results = self.storage_service.get_scenario_results("non-existent-id")
        
        assert retrieved_results is None
    
    def test_get_scenario_results_invalid_json(self):
        """Test scenario results retrieval with invalid JSON file."""
        # Create a file with invalid JSON
        file_path = os.path.join(self.storage_service.results_dir, "invalid_results.json")
        with open(file_path, 'w') as f:
            f.write("invalid json content")
        
        retrieved_results = self.storage_service.get_scenario_results("invalid")
        
        assert retrieved_results is None
    
    def test_scenario_exists_true(self):
        """Test scenario existence check when scenario exists."""
        # Create a scenario
        scenario_def = ScenarioDefinition(
            name="Test Scenario",
            description="A test scenario",
            time_range={
                "start_year": 2024,
                "start_month": 1,
                "end_year": 2026,
                "end_month": 12
            }
        )
        
        scenario_id = self.storage_service.create_scenario(scenario_def)
        
        assert self.storage_service.scenario_exists(scenario_id) is True
    
    def test_scenario_exists_false(self):
        """Test scenario existence check when scenario doesn't exist."""
        assert self.storage_service.scenario_exists("non-existent-id") is False
    
    def test_results_exist_true(self):
        """Test results existence check when results exist."""
        # Save results
        results = {"test": "data"}
        self.storage_service.save_scenario_results("test-scenario-id", results)
        
        assert self.storage_service.results_exist("test-scenario-id") is True
    
    def test_results_exist_false(self):
        """Test results existence check when results don't exist."""
        assert self.storage_service.results_exist("non-existent-id") is False
    
    def test_get_storage_stats_empty(self):
        """Test storage statistics when no data exists."""
        stats = self.storage_service.get_storage_stats()
        
        assert stats['total_scenarios'] == 0
        assert stats['total_results'] == 0
        assert stats['total_size_bytes'] == 0
        assert stats['storage_directory'] == self.temp_dir
        assert 'error' not in stats
    
    def test_get_storage_stats_with_data(self):
        """Test storage statistics with existing data."""
        # Create scenarios and results
        scenario_def = ScenarioDefinition(
            name="Test Scenario",
            description="A test scenario",
            time_range={
                "start_year": 2024,
                "start_month": 1,
                "end_year": 2026,
                "end_month": 12
            }
        )
        
        scenario_id = self.storage_service.create_scenario(scenario_def)
        self.storage_service.save_scenario_results(scenario_id, {"test": "data"})
        
        stats = self.storage_service.get_storage_stats()
        
        assert stats['total_scenarios'] == 1
        assert stats['total_results'] == 1
        assert stats['total_size_bytes'] > 0
        assert stats['storage_directory'] == self.temp_dir
        assert 'error' not in stats
    
    def test_get_storage_stats_with_error(self):
        """Test storage statistics with directory access error."""
        # Remove the directory to cause an error
        shutil.rmtree(self.temp_dir)
        
        stats = self.storage_service.get_storage_stats()
        
        assert stats['total_scenarios'] == 0
        assert stats['total_results'] == 0
        assert stats['total_size_bytes'] == 0
        assert stats['storage_directory'] == self.temp_dir
        assert 'error' in stats 