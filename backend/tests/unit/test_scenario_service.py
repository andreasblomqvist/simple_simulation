"""
Unit tests for the scenario service.
"""
import pytest
import tempfile
import os
import json
from unittest.mock import Mock, patch
from datetime import datetime

from backend.src.services.scenario_service import ScenarioService
from backend.src.services.scenario_models import ScenarioDefinition, ScenarioRequest

class TestScenarioService:
    """Test cases for ScenarioService."""
    
    @pytest.fixture
    def temp_storage_dir(self):
        """Create a temporary storage directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def scenario_service(self, temp_storage_dir):
        """Create a ScenarioService instance with temporary storage."""
        return ScenarioService(storage_dir=temp_storage_dir)
    
    @pytest.fixture
    def sample_scenario_def(self):
        """Create a sample scenario definition for testing."""
        return ScenarioDefinition(
            name="Test Scenario",
            description="A test scenario for unit testing",
            time_range={
                "start_year": 2025,
                "start_month": 1,
                "end_year": 2026,
                "end_month": 12
            },
            office_scope=["Stockholm"],
            levers={
                "recruitment": {"A": 1.2, "AC": 1.1},
                "churn": {"A": 0.9, "AC": 1.0},
                "progression": {"A": 1.0, "AC": 1.0}
            }
        )
    
    def test_create_scenario(self, scenario_service, sample_scenario_def):
        """Test creating a new scenario."""
        scenario_id = scenario_service.create_scenario(sample_scenario_def)
        
        # Verify scenario ID is returned
        assert scenario_id is not None
        assert isinstance(scenario_id, str)
        
        # Verify scenario file was created
        scenario_file = os.path.join(scenario_service.storage_dir, f"{scenario_id}.json")
        assert os.path.exists(scenario_file)
        
        # Verify scenario data is correct
        with open(scenario_file, 'r') as f:
            scenario_data = json.load(f)
        
        assert scenario_data["id"] == scenario_id
        assert scenario_data["definition"]["name"] == sample_scenario_def.name
        assert scenario_data["definition"]["description"] == sample_scenario_def.description
    
    def test_get_scenario(self, scenario_service, sample_scenario_def):
        """Test retrieving a scenario by ID."""
        # Create a scenario first
        scenario_id = scenario_service.create_scenario(sample_scenario_def)
        
        # Retrieve the scenario
        retrieved_scenario = scenario_service.get_scenario(scenario_id)
        
        # Verify retrieved scenario matches original
        assert retrieved_scenario is not None
        assert retrieved_scenario.name == sample_scenario_def.name
        assert retrieved_scenario.description == sample_scenario_def.description
        assert retrieved_scenario.time_range == sample_scenario_def.time_range
        assert retrieved_scenario.office_scope == sample_scenario_def.office_scope
        assert retrieved_scenario.levers == sample_scenario_def.levers
    
    def test_get_nonexistent_scenario(self, scenario_service):
        """Test retrieving a scenario that doesn't exist."""
        scenario = scenario_service.get_scenario("nonexistent-id")
        assert scenario is None
    
    def test_list_scenarios(self, scenario_service, sample_scenario_def):
        """Test listing all scenarios."""
        # Create multiple scenarios
        scenario_id1 = scenario_service.create_scenario(sample_scenario_def)
        
        # Create another scenario with different name
        scenario_def2 = sample_scenario_def.model_copy()
        scenario_def2.name = "Test Scenario 2"
        scenario_id2 = scenario_service.create_scenario(scenario_def2)
        
        # List scenarios
        scenarios = scenario_service.list_scenarios()
        
        # Verify scenarios are listed
        assert len(scenarios) == 2
        
        # Verify scenario data is correct
        scenario_names = [s["name"] for s in scenarios]
        assert "Test Scenario" in scenario_names
        assert "Test Scenario 2" in scenario_names
        
        # Verify scenarios are sorted by updated_at descending
        assert scenarios[0]["updated_at"] >= scenarios[1]["updated_at"]
    
    def test_list_scenarios_empty_directory(self, scenario_service):
        """Test listing scenarios when directory is empty."""
        scenarios = scenario_service.list_scenarios()
        assert scenarios == []
    
    def test_delete_scenario(self, scenario_service, sample_scenario_def):
        """Test deleting a scenario."""
        # Create a scenario
        scenario_id = scenario_service.create_scenario(sample_scenario_def)
        
        # Verify scenario file exists
        scenario_file = os.path.join(scenario_service.storage_dir, f"{scenario_id}.json")
        assert os.path.exists(scenario_file)
        
        # Delete the scenario
        success = scenario_service.delete_scenario(scenario_id)
        assert success is True
        
        # Verify scenario file is deleted
        assert not os.path.exists(scenario_file)
    
    def test_delete_nonexistent_scenario(self, scenario_service):
        """Test deleting a scenario that doesn't exist."""
        success = scenario_service.delete_scenario("nonexistent-id")
        assert success is False
    
    @patch('backend.src.services.scenario_service.config_service')
    @patch('backend.src.services.scenario_service.SimulationEngine')
    def test_transform_to_lever_plan(self, mock_engine, mock_config_service, scenario_service, sample_scenario_def):
        """Test transformation of scenario definition to lever plan."""
        # Mock configuration service
        mock_config_service.get_config.return_value = {
            "Stockholm": {
                "roles": {
                    "Consultant": {
                        "A": {
                            "recruitment_1": 20.0,
                            "recruitment_2": 20.0,
                            "churn_1": 2.0,
                            "churn_2": 2.0
                        },
                        "AC": {
                            "recruitment_1": 8.0,
                            "recruitment_2": 8.0,
                            "churn_1": 4.0,
                            "churn_2": 4.0
                        }
                    }
                }
            }
        }
        
        # Transform scenario to lever plan
        lever_plan = scenario_service._transform_to_lever_plan(sample_scenario_def)
        
        # Verify lever plan structure
        assert "offices" in lever_plan
        assert "Stockholm" in lever_plan["offices"]
        assert "Consultant" in lever_plan["offices"]["Stockholm"]
        
        # Verify recruitment values are multiplied correctly
        stockholm_consultant = lever_plan["offices"]["Stockholm"]["Consultant"]
        assert "A" in stockholm_consultant
        assert "AC" in stockholm_consultant
        
        # Check A level recruitment (baseline 20.0 * multiplier 1.2 = 24.0)
        assert stockholm_consultant["A"]["recruitment_1"] == 24.0
        assert stockholm_consultant["A"]["recruitment_2"] == 24.0
        
        # Check A level churn (baseline 2.0 * multiplier 0.9 = 1.8)
        assert stockholm_consultant["A"]["churn_1"] == 1.8
        assert stockholm_consultant["A"]["churn_2"] == 1.8
        
        # Check AC level recruitment (baseline 8.0 * multiplier 1.1 = 8.8)
        assert stockholm_consultant["AC"]["recruitment_1"] == 8.8
        assert stockholm_consultant["AC"]["recruitment_2"] == 8.8
    
    def test_create_economic_params(self, scenario_service, sample_scenario_def):
        """Test creation of economic parameters."""
        # Test with default values
        economic_params = scenario_service._create_economic_params(sample_scenario_def)
        
        assert economic_params.unplanned_absence == 0.05
        assert economic_params.working_hours_per_month == 166.4
        assert economic_params.other_expense == 19000000.0
        assert economic_params.employment_cost_rate == 0.40
        assert economic_params.utilization == 0.85
        
        # Test with custom values
        sample_scenario_def.economic_params = {
            "unplanned_absence": 0.1,
            "working_hours_per_month": 160.0
        }
        
        economic_params = scenario_service._create_economic_params(sample_scenario_def)
        assert economic_params.unplanned_absence == 0.1
        assert economic_params.working_hours_per_month == 160.0
    
    @patch('backend.src.services.scenario_service.config_service')
    @patch('backend.src.services.scenario_service.KPIService')
    def test_run_scenario_success(self, mock_kpi_service, mock_config_service, scenario_service, sample_scenario_def):
        """Test successful scenario execution."""
        # Mock configuration service
        mock_config_service.get_config.return_value = {
            "Stockholm": {
                "roles": {
                    "Consultant": {
                        "A": {"recruitment_1": 20.0, "churn_1": 2.0},
                        "AC": {"recruitment_1": 8.0, "churn_1": 4.0}
                    }
                }
            }
        }

        # Mock the engine instance that's already created in the service
        mock_engine = Mock()
        scenario_service.engine = mock_engine
        mock_engine.run_simulation.return_value = {"years": {"2025": {"offices": {}}}}

        # Mock KPI service
        mock_kpi_service.return_value.calculate_all_kpis.return_value = {"ebitda": 1000000}

        # Create scenario request
        request = ScenarioRequest(scenario_definition=sample_scenario_def)

        # Run scenario
        response = scenario_service.run_scenario(request)

        # Verify response
        assert response.status == "success"
        assert response.scenario_name == sample_scenario_def.name
        assert response.execution_time > 0
        assert "years" in response.results

        # Verify engine was called correctly
        mock_engine.run_simulation.assert_called_once()
        call_args = mock_engine.run_simulation.call_args
        assert call_args[1]["start_year"] == 2025
        assert call_args[1]["start_month"] == 1
        assert call_args[1]["end_year"] == 2026
        assert call_args[1]["end_month"] == 12
    
    def test_run_scenario_with_existing_id(self, scenario_service, sample_scenario_def):
        """Test running a scenario using existing scenario ID."""
        # Create a scenario first
        scenario_id = scenario_service.create_scenario(sample_scenario_def)
        
        # Create request with existing scenario ID
        request = ScenarioRequest(scenario_id=scenario_id)
        
        # Mock the engine to avoid actual simulation
        with patch.object(scenario_service, '_call_simulation_engine') as mock_engine:
            mock_engine.return_value = {"years": {"2025": {"offices": {}}}}
            
            # Run scenario
            response = scenario_service.run_scenario(request)
            
            # Verify response
            assert response.status == "success"
            assert response.scenario_id == scenario_id
            assert response.scenario_name == sample_scenario_def.name
    
    def test_run_scenario_with_nonexistent_id(self, scenario_service):
        """Test running a scenario with non-existent ID."""
        request = ScenarioRequest(scenario_id="nonexistent-id")
        
        response = scenario_service.run_scenario(request)
        
        assert response.status == "error"
        assert "Scenario not found" in response.error_message 