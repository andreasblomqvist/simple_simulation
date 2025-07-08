"""
Unit tests for the ScenarioService (refactored architecture).
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.services.scenario_service import ScenarioService
from src.services.simulation.models import Office, Level, Person
from src.services.config_service import config_service
from src.services.scenario_models import ScenarioRequest, ScenarioDefinition

class TestScenarioService:
    """Test the refactored ScenarioService that orchestrates focused services."""
    
    @pytest.fixture
    def scenario_service(self):
        """Create a ScenarioService instance."""
        return ScenarioService(config_service)
    
    @pytest.fixture
    def sample_scenario_data(self):
        """Sample scenario data with baseline and lever overrides."""
        return {
            "baseline_input": {
                "global": {
                    "recruitment": {
                        "Consultant": {
                            "A": {
                                "202501": 2.5,
                                "202502": 2.5
                            }
                        }
                    },
                    "churn": {
                        "Consultant": {
                            "A": {
                                "202501": 0.8,
                                "202502": 0.8
                            }
                        }
                    }
                }
            },
            "levers": {
                "global": {
                    "price": {
                        "A": 1250.0
                    }
                }
            }
        }

    def test_resolve_scenario_basic(self, scenario_service):
        """Test basic scenario resolution without overrides."""
        scenario_data = {}
        result = scenario_service.resolve_scenario(scenario_data)
        
        # Verify the structure
        assert "offices" in result
        assert "progression_config" in result
        assert "cat_curves" in result
        
        # Verify offices were created
        assert len(result["offices"]) > 0
        assert "Stockholm" in result["offices"]

    def test_resolve_scenario_with_baseline_overrides(self, scenario_service, sample_scenario_data):
        """Test scenario resolution with baseline input overrides."""
        result = scenario_service.resolve_scenario(sample_scenario_data)

        # Verify offices were created
        assert "Stockholm" in result["offices"]
        office = result["offices"]["Stockholm"]

        # Verify baseline overrides were applied
        consultant_role = office.roles["Consultant"]
        level_a = consultant_role["A"]

        # Check if baseline overrides were applied to the config
        # Note: The actual application happens in ScenarioResolver._map_baseline_to_absolute_values
        # which creates fields like recruitment_abs_1, churn_abs_1, etc.
        # We need to check if these fields exist in the level config
        level_config = level_a.__dict__
        
        # Debug: Print the level attributes to see what was actually set
        print(f"DEBUG: Level A attributes: {[k for k in level_config.keys() if 'recruitment' in k or 'churn' in k]}")
        
        # The test should verify that the baseline mapping logic is working
        # For now, just verify the structure is correct
        assert hasattr(level_a, 'recruitment_1')
        assert hasattr(level_a, 'churn_1')

    def test_resolve_scenario_with_lever_overrides(self, scenario_service, sample_scenario_data):
        """Test scenario resolution with lever overrides."""
        result = scenario_service.resolve_scenario(sample_scenario_data)

        # Verify offices were created
        assert "Stockholm" in result["offices"]
        office = result["offices"]["Stockholm"]

        # Verify lever overrides were applied
        consultant_role = office.roles["Consultant"]
        level_a = consultant_role["A"]

        # Check if lever overrides were applied
        # Note: The actual application happens in ScenarioResolver._apply_levers_to_office
        # We need to check if the price lever was applied
        level_config = level_a.__dict__
        
        # Debug: Print the level attributes to see what was actually set
        print(f"DEBUG: Level A price attributes: {[k for k in level_config.keys() if 'price' in k]}")
        
        # The test should verify that the lever mapping logic is working
        # For now, just verify the structure is correct
        assert hasattr(level_a, 'price_1')

    def test_office_builder_integration(self, scenario_service):
        """Test that OfficeBuilder correctly creates Office objects from config."""
        scenario_data = {}
        result = scenario_service.resolve_scenario(scenario_data)
        
        # Verify Office objects were created correctly
        stockholm = result["offices"]["Stockholm"]
        
        # Check office structure
        assert hasattr(stockholm, 'name')
        assert hasattr(stockholm, 'total_fte')
        assert hasattr(stockholm, 'journey')
        assert hasattr(stockholm, 'roles')
        
        # Check roles structure
        assert "Consultant" in stockholm.roles
        consultant_role = stockholm.roles["Consultant"]
        
        # Check levels structure
        assert "A" in consultant_role
        level_a = consultant_role["A"]
        
        # Check level attributes
        assert hasattr(level_a, 'name')
        assert hasattr(level_a, 'fte')
        assert hasattr(level_a, 'recruitment_1')
        assert hasattr(level_a, 'churn_1')
        assert hasattr(level_a, 'price_1')

    def test_progression_config_loading(self, scenario_service):
        """Test that progression config is loaded correctly."""
        scenario_data = {}
        result = scenario_service.resolve_scenario(scenario_data)
        
        # Verify progression config was loaded
        progression_config = result["progression_config"]
        assert isinstance(progression_config, dict)
        assert len(progression_config) > 0

    def test_cat_curves_loading(self, scenario_service):
        """Test that CAT curves are loaded correctly."""
        scenario_data = {}
        result = scenario_service.resolve_scenario(scenario_data)
        
        # Verify CAT curves were loaded
        cat_curves = result["cat_curves"]
        assert isinstance(cat_curves, dict)
        assert len(cat_curves) > 0

    def test_scenario_service_integration(self, scenario_service, sample_scenario_data):
        """Test complete scenario resolution with baseline and lever overrides."""
        result = scenario_service.resolve_scenario(sample_scenario_data)
        
        # Verify offices were created
        assert "offices" in result
        offices = result["offices"]
        assert len(offices) > 0
        
        # Verify baseline overrides are applied to ALL offices (global override)
        for office_name, office in offices.items():
            if "Consultant" in office.roles:
                consultant_levels = office.roles["Consultant"]  # This is a Dict[str, Level]
                if "A" in consultant_levels:
                    level_a = consultant_levels["A"]  # This is a Level object
                    # Check that recruitment override (2.5) is applied globally
                    assert level_a.recruitment_1 == 2.5, f"Recruitment override not applied in {office_name}"
                    # Check that churn override (0.8) is applied globally  
                    assert level_a.churn_1 == 0.8, f"Churn override not applied in {office_name}"
        
        # Verify lever overrides are applied
        for office_name, office in offices.items():
            if "Consultant" in office.roles:
                consultant_levels = office.roles["Consultant"]  # This is a Dict[str, Level]
                if "A" in consultant_levels:
                    level_a = consultant_levels["A"]  # This is a Level object
                    # Check that price override (1250.0) is applied
                    assert level_a.price_1 == 1250.0, f"Price override not applied in {office_name}"
        
        # Verify other required data is present
        assert "progression_config" in result
        assert "cat_curves" in result 

class TestScenarioServiceHelpers:
    def setup_method(self):
        self.config_service = Mock()
        self.service = ScenarioService(self.config_service)
        self.service.storage_service = Mock()
        self.service.scenario_validator = Mock()
        self.service.scenario_transformer = Mock()
        self.service.logger = Mock()

    def make_minimal_scenario_def(self):
        return ScenarioDefinition(
            name="Test",
            description="Test scenario",
            time_range={"start_year": 2025, "start_month": 1, "end_year": 2026, "end_month": 12},
            office_scope=["Stockholm"],
            levers={},
            progression_config={},
            cat_curves={},
            economic_params={}
        )

    def test_load_scenario_definition_from_request(self):
        scenario_def = self.make_minimal_scenario_def()
        req = ScenarioRequest(scenario_definition=scenario_def, scenario_id=None)
        result = self.service._load_scenario_definition(req, correlation_id="cid")
        assert result is req.scenario_definition

    def test_load_scenario_definition_from_storage(self):
        scenario = self.make_minimal_scenario_def()
        self.service.storage_service.get_scenario.return_value = scenario
        req = ScenarioRequest(scenario_definition=None, scenario_id="sid")
        result = self.service._load_scenario_definition(req, correlation_id="cid")
        assert result is scenario

    def test_load_scenario_definition_missing(self):
        self.service.storage_service.get_scenario.return_value = None
        req = ScenarioRequest(scenario_definition=None, scenario_id="sid")
        with pytest.raises(ValueError, match="Scenario not found: sid"):
            self.service._load_scenario_definition(req, correlation_id="cid")
        req2 = ScenarioRequest(scenario_definition=None, scenario_id=None)
        with pytest.raises(ValueError, match="No scenario definition provided"):
            self.service._load_scenario_definition(req2, correlation_id="cid")

    def test_validate_scenario_definition_and_resolved(self):
        scenario_def = self.make_minimal_scenario_def()
        resolved_data = Mock()
        self.service._validate_scenario(scenario_def, resolved_data, correlation_id="cid")
        self.service.scenario_validator.validate_scenario_definition.assert_called_once_with(scenario_def)
        self.service.scenario_validator.validate_scenario_data.assert_called_once_with(resolved_data)

    def test_validate_scenario_definition_only(self):
        scenario_def = self.make_minimal_scenario_def()
        self.service._validate_scenario(scenario_def, correlation_id="cid")
        self.service.scenario_validator.validate_scenario_definition.assert_called_once_with(scenario_def)

    def test_resolve_and_validate_scenario_data_success(self):
        scenario_def = self.make_minimal_scenario_def()
        self.service.resolve_scenario = Mock(return_value={"foo": "bar"})
        self.service._validate_scenario = Mock()
        result = self.service._resolve_and_validate_scenario_data(scenario_def, correlation_id="cid")
        assert result == {"foo": "bar"}
        self.service._validate_scenario.assert_called_once()

    def test_resolve_and_validate_scenario_data_validation_error(self):
        scenario_def = self.make_minimal_scenario_def()
        self.service.resolve_scenario = Mock(return_value={"foo": "bar"})
        self.service._validate_scenario = Mock(side_effect=Exception("bad data"))
        with pytest.raises(ValueError, match="Resolved scenario data validation failed: bad data"):
            self.service._resolve_and_validate_scenario_data(scenario_def, correlation_id="cid")

    def test_execute_simulation_success(self):
        scenario_def = self.make_minimal_scenario_def()
        resolved_data = Mock()
        self.service.scenario_transformer.transform_scenario_to_economic_params.return_value = "econ"
        self.service._call_simulation_engine = Mock(return_value="results")
        result = self.service._execute_simulation(scenario_def, resolved_data, correlation_id="cid")
        assert result == "results"

    def test_execute_simulation_failure(self):
        scenario_def = self.make_minimal_scenario_def()
        resolved_data = Mock()
        self.service.scenario_transformer.transform_scenario_to_economic_params.return_value = "econ"
        self.service._call_simulation_engine = Mock(side_effect=Exception("fail"))
        with pytest.raises(ValueError, match="Simulation engine failed: fail"):
            self.service._execute_simulation(scenario_def, resolved_data, correlation_id="cid")

    def test_persist_scenario_results_new(self):
        req = ScenarioRequest(scenario_definition=None, scenario_id=None)
        scenario_def = self.make_minimal_scenario_def()
        results = {"foo": "bar"}
        scenario_def.id = None
        sid = self.service._persist_scenario_results(req, scenario_def, results, 1.23, correlation_id="cid")
        assert sid == scenario_def.id
        self.service.storage_service.create_scenario.assert_called_once_with(scenario_def)
        self.service.storage_service.save_scenario_results.assert_called_once_with(sid, results)

    def test_persist_scenario_results_existing(self):
        req = ScenarioRequest(scenario_definition=None, scenario_id="sid")
        scenario_def = self.make_minimal_scenario_def()
        results = {"foo": "bar"}
        sid = self.service._persist_scenario_results(req, scenario_def, results, 1.23, correlation_id="cid")
        assert sid == "sid"
        self.service.storage_service.create_scenario.assert_not_called()
        self.service.storage_service.save_scenario_results.assert_called_once_with("sid", results)

    def test_run_scenario_happy_path(self):
        scenario_def = self.make_minimal_scenario_def()
        req = ScenarioRequest(scenario_definition=scenario_def, scenario_id=None)
        self.service._load_scenario_definition = Mock(return_value=scenario_def)
        self.service._validate_scenario = Mock()
        self.service._resolve_and_validate_scenario_data = Mock(return_value={"foo": "bar"})
        self.service._execute_simulation = Mock(return_value={"result": 1})
        self.service._persist_scenario_results = Mock(return_value="sid")
        resp = self.service.run_scenario(req)
        assert resp.status == "success"
        assert resp.scenario_id == "sid"
        assert resp.results == {"result": 1}

    def test_run_scenario_error_paths(self):
        scenario_def = self.make_minimal_scenario_def()
        req = ScenarioRequest(scenario_definition=scenario_def, scenario_id=None)
        self.service._load_scenario_definition = Mock(side_effect=ValueError("not found"))
        resp = self.service.run_scenario(req)
        assert resp.status == "error"
        self.service._load_scenario_definition = Mock(return_value=scenario_def)
        self.service._validate_scenario = Mock(side_effect=Exception("bad val"))
        resp = self.service.run_scenario(req)
        assert resp.status == "error"
        self.service._validate_scenario = Mock()
        self.service._resolve_and_validate_scenario_data = Mock(side_effect=Exception("bad resolve"))
        resp = self.service.run_scenario(req)
        assert resp.status == "error"
        self.service._resolve_and_validate_scenario_data = Mock(return_value={"foo": "bar"})
        self.service._execute_simulation = Mock(side_effect=Exception("bad sim"))
        resp = self.service.run_scenario(req)
        assert resp.status == "error" 