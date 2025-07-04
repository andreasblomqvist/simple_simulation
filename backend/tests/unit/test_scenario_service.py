"""
Unit tests for the ScenarioService (refactored architecture).
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from backend.src.services.scenario_service import ScenarioService
from backend.src.services.simulation.models import Office, Level, Person

class TestScenarioService:
    """Test cases for the refactored ScenarioService."""
    
    @pytest.fixture
    def mock_config_service(self):
        """Create a mock config service."""
        config_service = Mock()
        config_service.get_config.return_value = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {
                            "fte": 20.0,
                            "recruitment_1": 2.0,
                            "recruitment_2": 2.0,
                            "churn_1": 1.0,
                            "churn_2": 1.0,
                            "price_1": 1200.0,
                            "salary_1": 45000.0
                        },
                        "AC": {
                            "fte": 15.0,
                            "recruitment_1": 1.5,
                            "recruitment_2": 1.5,
                            "churn_1": 0.8,
                            "churn_2": 0.8,
                            "price_1": 1300.0,
                            "salary_1": 55000.0
                        }
                    },
                    "Operations": {
                        "fte": 5.0,
                        "recruitment_1": 0.5,
                        "recruitment_2": 0.5,
                        "churn_1": 0.2,
                        "churn_2": 0.2,
                        "price_1": 80.0,
                        "salary_1": 35000.0
                    }
                }
            }
        }
        return config_service
    
    @pytest.fixture
    def scenario_service(self, mock_config_service):
        """Create a ScenarioService instance with mock config service."""
        return ScenarioService(mock_config_service)
    
    @pytest.fixture
    def sample_scenario_data(self):
        """Create sample scenario data for testing."""
        return {
            "baseline_input": {
                "global": {
                    "recruitment": {
                        "A": {
                            "recruitment_1": 2.5,  # Override baseline 2.0
                            "recruitment_2": 2.5
                        }
                    },
                    "churn": {
                        "A": {
                            "churn_1": 0.8,  # Override baseline 1.0
                            "churn_2": 0.8
                        }
                    }
                }
            },
            "levers": {
                "global": {
                    "price": {
                        "A": {
                            "price_1": 1250.0  # Override baseline 1200.0
                        }
                    }
                }
            }
        }
    
    def test_resolve_scenario_basic(self, scenario_service, sample_scenario_data):
        """Test basic scenario resolution without overrides."""
        # Test with minimal scenario data
        scenario_data = {}
        
        result = scenario_service.resolve_scenario(scenario_data)
        
        # Verify result structure
        assert "offices" in result
        assert "progression_config" in result
        assert "cat_curves" in result
        
        # Verify offices were created
        assert "Stockholm" in result["offices"]
        assert isinstance(result["offices"]["Stockholm"], Office)
        
        # Verify progression config was loaded
        assert isinstance(result["progression_config"], dict)
        assert len(result["progression_config"]) > 0
        
        # Verify CAT curves were loaded
        assert isinstance(result["cat_curves"], dict)
        assert len(result["cat_curves"]) > 0
    
    def test_resolve_scenario_with_baseline_overrides(self, scenario_service, sample_scenario_data):
        """Test scenario resolution with baseline input overrides."""
        result = scenario_service.resolve_scenario(sample_scenario_data)
        
        # Verify offices were created
        assert "Stockholm" in result["offices"]
        office = result["offices"]["Stockholm"]
        
        # Verify baseline overrides were applied
        consultant_role = office.roles["Consultant"]
        level_a = consultant_role["A"]
        
        # Check recruitment override (2.0 -> 2.5)
        assert level_a.recruitment_1 == 2.5
        assert level_a.recruitment_2 == 2.5
        
        # Check churn override (1.0 -> 0.8)
        assert level_a.churn_1 == 0.8
        assert level_a.churn_2 == 0.8
    
    def test_resolve_scenario_with_lever_overrides(self, scenario_service, sample_scenario_data):
        """Test scenario resolution with lever overrides."""
        result = scenario_service.resolve_scenario(sample_scenario_data)
        
        # Verify offices were created
        assert "Stockholm" in result["offices"]
        office = result["offices"]["Stockholm"]
        
        # Verify lever overrides were applied
        consultant_role = office.roles["Consultant"]
        level_a = consultant_role["A"]
        
        # Check price override (1200.0 -> 1250.0)
        assert level_a.price_1 == 1250.0
    
    def test_apply_scenario_baseline_global(self, scenario_service, sample_scenario_data):
        """Test applying global baseline overrides."""
        base_config = scenario_service.config_service.get_config()
        result = scenario_service.apply_scenario_baseline(base_config, sample_scenario_data)
        # Debug print
        stockholm = result["Stockholm"]
        consultant_a = stockholm["roles"]["Consultant"]["A"]
        print(f"DEBUG: consultant_a['recruitment_1'] = {consultant_a['recruitment_1']}")
        # Verify Stockholm office was modified
        
        # Check recruitment override
        assert consultant_a["recruitment_1"] == 2.5
        assert consultant_a["recruitment_2"] == 2.5
        
        # Check churn override
        assert consultant_a["churn_1"] == 0.8
        assert consultant_a["churn_2"] == 0.8
        
        # Verify other values remain unchanged
        assert consultant_a["price_1"] == 1200.0  # No override
        assert consultant_a["salary_1"] == 45000.0  # No override
    
    def test_apply_scenario_baseline_office_specific(self, scenario_service):
        """Test applying office-specific baseline overrides."""
        base_config = scenario_service.config_service.get_config()
        baseline_data = {
            "baseline_input": {
                "offices": {
                    "Stockholm": {
                        "recruitment": {
                            "AC": {
                                "recruitment_1": 2.0,  # Override baseline 1.5
                                "recruitment_2": 2.0
                            }
                        }
                    }
                }
            }
        }
        result = scenario_service.apply_scenario_baseline(base_config, baseline_data)
        # Verify Stockholm office was modified
        stockholm = result["Stockholm"]
        consultant_ac = stockholm["roles"]["Consultant"]["AC"]
        
        # Check recruitment override
        assert consultant_ac["recruitment_1"] == 2.0
        assert consultant_ac["recruitment_2"] == 2.0
        
        # Verify other offices and levels remain unchanged
        consultant_a = stockholm["roles"]["Consultant"]["A"]
        assert consultant_a["recruitment_1"] == 2.0  # Original value
    
    def test_apply_scenario_levers_global(self, scenario_service, sample_scenario_data):
        """Test applying global lever overrides."""
        base_config = scenario_service.config_service.get_config()
        levers_data = sample_scenario_data["levers"]
        
        result = scenario_service.apply_scenario_levers(base_config, levers_data)
        
        # Verify Stockholm office was modified
        stockholm = result["Stockholm"]
        consultant_a = stockholm["roles"]["Consultant"]["A"]
        
        # Check price override
        assert consultant_a["price_1"] == 1250.0
        
        # Verify other values remain unchanged
        assert consultant_a["recruitment_1"] == 2.0  # No override
        assert consultant_a["churn_1"] == 1.0  # No override
    
    def test_apply_scenario_levers_office_specific(self, scenario_service):
        """Test applying office-specific lever overrides."""
        base_config = scenario_service.config_service.get_config()
        levers_data = {
            "offices": {
                "Stockholm": {
                    "salary": {
                        "A": {
                            "salary_1": 50000.0  # Override baseline 45000.0
                        }
                    }
                }
            }
        }
        
        result = scenario_service.apply_scenario_levers(base_config, levers_data)
        
        # Verify Stockholm office was modified
        stockholm = result["Stockholm"]
        consultant_a = stockholm["roles"]["Consultant"]["A"]
        
        # Check salary override
        assert consultant_a["salary_1"] == 50000.0
        
        # Verify other offices and levels remain unchanged
        consultant_ac = stockholm["roles"]["Consultant"]["AC"]
        assert consultant_ac["salary_1"] == 55000.0  # Original value
    
    def test_create_offices_from_config(self, scenario_service):
        """Test creating Office objects from config data."""
        config = scenario_service.config_service.get_config()
        
        # Mock progression config
        progression_config = {
            "A": {"time_on_level": 6, "progression_months": [6, 12]},
            "AC": {"time_on_level": 12, "progression_months": [12, 24]}
        }
        
        offices = scenario_service.create_offices_from_config(config, progression_config)
        
        # Verify offices were created
        assert "Stockholm" in offices
        office = offices["Stockholm"]
        
        # Verify office structure
        assert isinstance(office, Office)
        assert office.name == "Stockholm"
        assert office.total_fte == 100
        
        # Verify roles were created
        assert "Consultant" in office.roles
        assert "Operations" in office.roles
        
        # Verify levels were created
        consultant_role = office.roles["Consultant"]
        assert "A" in consultant_role
        assert "AC" in consultant_role
        
        # Verify level data
        level_a = consultant_role["A"]
        assert isinstance(level_a, Level)
        assert level_a.name == "A"
        assert level_a.fte == 20.0
    
    def test_load_progression_config(self, scenario_service):
        """Test loading progression configuration."""
        progression_config = scenario_service.load_progression_config()
        
        # Verify progression config structure
        assert isinstance(progression_config, dict)
        assert len(progression_config) > 0
        
        # Verify it contains expected levels
        expected_levels = ["A", "AC", "C", "SrC", "AM", "M", "SrM", "Pi", "P"]
        for level in expected_levels:
            assert level in progression_config
    
    def test_load_cat_curves(self, scenario_service):
        """Test loading CAT curves."""
        cat_curves = scenario_service.load_cat_curves()
        
        # Verify CAT curves structure
        assert isinstance(cat_curves, dict)
        assert len(cat_curves) > 0
        
        # Verify it contains expected levels
        expected_levels = ["A", "AC", "C", "SrC", "AM", "M", "SrM", "Pi", "P"]
        for level in expected_levels:
            assert level in cat_curves
    
    def test_validate_scenario_data_valid(self, scenario_service, sample_scenario_data):
        """Test validation of valid scenario data."""
        # Should not raise any exceptions
        scenario_service.validate_scenario_data(sample_scenario_data)
    
    def test_validate_scenario_data_empty(self, scenario_service):
        """Test validation of empty scenario data."""
        # Should not raise any exceptions
        scenario_service.validate_scenario_data({})
    
    def test_validate_scenario_data_invalid_baseline(self, scenario_service):
        """Test validation of invalid baseline data."""
        invalid_data = {
            "baseline_input": {
                "global": {
                    "recruitment": {
                        "A": {
                            "recruitment_1": "invalid"  # Should be number
                        }
                    }
                }
            }
        }
        
        with pytest.raises(ValueError, match="Invalid recruitment value"):
            scenario_service.validate_scenario_data(invalid_data)
    
    def test_validate_scenario_data_invalid_levers(self, scenario_service):
        """Test validation of invalid lever data."""
        invalid_data = {
            "levers": {
                "global": {
                    "price": {
                        "A": {
                            "price_1": "invalid"  # Should be number
                        }
                    }
                }
            }
        }
        
        with pytest.raises(ValueError, match="Invalid price value"):
            scenario_service.validate_scenario_data(invalid_data)
    
    def test_scenario_service_integration(self, scenario_service, sample_scenario_data):
        """Test full integration of scenario service methods."""
        # Test the complete flow
        result = scenario_service.resolve_scenario(sample_scenario_data)
        
        # Verify all components are present
        assert "offices" in result
        assert "progression_config" in result
        assert "cat_curves" in result
        
        # Verify office was created with overrides
        office = result["offices"]["Stockholm"]
        consultant_a = office.roles["Consultant"]["A"]
        
        # Check that overrides were applied
        assert consultant_a.recruitment_1 == 2.5  # Baseline override
        assert consultant_a.churn_1 == 0.8  # Baseline override
        assert consultant_a.price_1 == 1250.0  # Lever override
        
        # Verify progression config and CAT curves are loaded
        assert len(result["progression_config"]) > 0
        assert len(result["cat_curves"]) > 0 