"""
Unit tests for the enhanced scenario validator.
"""
import pytest
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from src.services.scenario_validator import ScenarioValidator


class TestScenarioValidator:
    """Test the enhanced scenario validator with comprehensive validation methods."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ScenarioValidator()
    
    def test_validate_scenario_data_with_valid_dict(self):
        """Test validation of valid scenario data dictionary."""
        scenario_data = {
            'time_range': {'start_year': 2025, 'start_month': 1, 'end_year': 2027, 'end_month': 12},
            'office_scope': ['Stockholm', 'Berlin'],
            'levers': {'global': {'recruitment': {'A': 1.2}}},
            'baseline_input': {'global': {'recruitment': {'Consultant': {'A': {'202501': 3.0}}}}}
        }
        
        # Should not raise any exception
        self.validator.validate_scenario_data(scenario_data)
    
    def test_validate_scenario_data_with_empty_dict(self):
        """Test validation of empty scenario data."""
        scenario_data = {}
        
        # Should not raise any exception
        self.validator.validate_scenario_data(scenario_data)
    
    def test_validate_scenario_data_with_invalid_type(self):
        """Test validation of scenario data with invalid type."""
        scenario_data = "not a dict"
        
        with pytest.raises(ValueError, match="Scenario data must be a dictionary or Pydantic model"):
            self.validator.validate_scenario_data(scenario_data)
    
    def test_validate_scenario_data_with_invalid_baseline_input(self):
        """Test validation of scenario data with invalid baseline input."""
        scenario_data = {
            'baseline_input': "not a dict"
        }
        
        with pytest.raises(ValueError, match="baseline_input must be a dictionary"):
            self.validator.validate_scenario_data(scenario_data)
    
    def test_validate_scenario_data_with_invalid_levers(self):
        """Test validation of scenario data with invalid levers."""
        scenario_data = {
            'levers': "not a dict"
        }
        
        with pytest.raises(ValueError, match="levers must be a dictionary"):
            self.validator.validate_scenario_data(scenario_data)
    
    def test_validate_scenario_definition_with_valid_dict(self):
        """Test validation of valid scenario definition dictionary."""
        scenario_def = {
            'name': 'Test Scenario',
            'description': 'A test scenario',
            'time_range': {'start_year': 2025, 'start_month': 1, 'end_year': 2027, 'end_month': 12},
            'office_scope': ['Stockholm', 'Berlin'],
            'levers': {'global': {'recruitment': {'A': 1.2}}},
            'economic_params': {'unplanned_absence': 0.05, 'utilization': 0.85}
        }
        
        # Should not raise any exception
        self.validator.validate_scenario_definition(scenario_def)
    
    def test_validate_scenario_definition_with_missing_required_fields(self):
        """Test validation of scenario definition with missing required fields."""
        scenario_def = {
            'name': 'Test Scenario'
            # Missing description, time_range, office_scope
        }
        
        with pytest.raises(ValueError, match="Scenario definition must contain description"):
            self.validator.validate_scenario_definition(scenario_def)
    
    def test_validate_scenario_definition_with_invalid_name(self):
        """Test validation of scenario definition with invalid name."""
        scenario_def = {
            'name': '',  # Empty name
            'description': 'A test scenario',
            'time_range': {'start_year': 2025, 'start_month': 1, 'end_year': 2027, 'end_month': 12},
            'office_scope': ['Stockholm']
        }
        
        with pytest.raises(ValueError, match="Scenario name must be a non-empty string"):
            self.validator.validate_scenario_definition(scenario_def)
    
    def test_validate_scenario_definition_with_invalid_description(self):
        """Test validation of scenario definition with invalid description."""
        scenario_def = {
            'name': 'Test Scenario',
            'description': 123,  # Not a string
            'time_range': {'start_year': 2025, 'start_month': 1, 'end_year': 2027, 'end_month': 12},
            'office_scope': ['Stockholm']
        }
        
        with pytest.raises(ValueError, match="Scenario description must be a string"):
            self.validator.validate_scenario_definition(scenario_def)
    
    def test_validate_time_range_with_valid_data(self):
        """Test validation of valid time range."""
        time_range = {
            'start_year': 2025,
            'start_month': 1,
            'end_year': 2027,
            'end_month': 12
        }
        
        # Should not raise any exception
        self.validator.validate_time_range(time_range)
    
    def test_validate_time_range_with_missing_fields(self):
        """Test validation of time range with missing fields."""
        time_range = {
            'start_year': 2025,
            'start_month': 1
            # Missing end_year, end_month
        }
        
        with pytest.raises(ValueError, match="time_range must contain end_year"):
            self.validator.validate_time_range(time_range)
    
    def test_validate_time_range_with_invalid_month(self):
        """Test validation of time range with invalid month."""
        time_range = {
            'start_year': 2025,
            'start_month': 13,  # Invalid month
            'end_year': 2027,
            'end_month': 12
        }
        
        with pytest.raises(ValueError, match="start_month must be between 1 and 12"):
            self.validator.validate_time_range(time_range)
    
    def test_validate_time_range_with_invalid_year(self):
        """Test validation of time range with invalid year."""
        time_range = {
            'start_year': 2019,  # Too early
            'start_month': 1,
            'end_year': 2027,
            'end_month': 12
        }
        
        with pytest.raises(ValueError, match="start_year must be between 2020 and 2030"):
            self.validator.validate_time_range(time_range)
    
    def test_validate_time_range_with_end_before_start(self):
        """Test validation of time range with end date before start date."""
        time_range = {
            'start_year': 2027,
            'start_month': 12,
            'end_year': 2025,
            'end_month': 1
        }
        
        with pytest.raises(ValueError, match="End date must be after start date"):
            self.validator.validate_time_range(time_range)
    
    def test_validate_office_scope_with_valid_data(self):
        """Test validation of valid office scope."""
        office_scope = ['Stockholm', 'Berlin', 'Oslo']
        
        # Should not raise any exception
        self.validator.validate_office_scope(office_scope)
    
    def test_validate_office_scope_with_invalid_type(self):
        """Test validation of office scope with invalid type."""
        office_scope = "not a list"
        
        with pytest.raises(ValueError, match="office_scope must be a list"):
            self.validator.validate_office_scope(office_scope)
    
    def test_validate_office_scope_with_invalid_office_name(self):
        """Test validation of office scope with invalid office name."""
        office_scope = ['Stockholm', 123, 'Berlin']  # Non-string office name
        
        with pytest.raises(ValueError, match="All office names in office_scope must be strings"):
            self.validator.validate_office_scope(office_scope)
    
    def test_validate_office_scope_with_empty_office_name(self):
        """Test validation of office scope with empty office name."""
        office_scope = ['Stockholm', '', 'Berlin']  # Empty office name
        
        with pytest.raises(ValueError, match="Office names cannot be empty"):
            self.validator.validate_office_scope(office_scope)
    
    def test_validate_economic_params_with_valid_data(self):
        """Test validation of valid economic parameters."""
        economic_params = {
            'unplanned_absence': 0.05,
            'other_expense': 19000000.0,
            'employment_cost_rate': 0.40,
            'working_hours_per_month': 166.4,
            'utilization': 0.85,
            'price_increase': 0.03,
            'salary_increase': 0.02
        }
        
        # Should not raise any exception
        self.validator._validate_economic_params(economic_params)
    
    def test_validate_economic_params_with_invalid_type(self):
        """Test validation of economic parameters with invalid type."""
        economic_params = "not a dict"
        
        with pytest.raises(ValueError, match="economic_params must be a dictionary"):
            self.validator._validate_economic_params(economic_params)
    
    def test_validate_economic_params_with_unknown_parameter(self):
        """Test validation of economic parameters with unknown parameter."""
        economic_params = {
            'unplanned_absence': 0.05,
            'unknown_param': 123
        }
        
        with pytest.raises(ValueError, match="Unknown economic parameter: unknown_param"):
            self.validator._validate_economic_params(economic_params)
    
    def test_validate_economic_params_with_invalid_range(self):
        """Test validation of economic parameters with invalid range."""
        economic_params = {
            'unplanned_absence': 1.5  # Should be between 0 and 1
        }
        
        with pytest.raises(ValueError, match="unplanned_absence must be between 0 and 1"):
            self.validator._validate_economic_params(economic_params)
    
    def test_validate_progression_config_with_valid_data(self):
        """Test validation of valid progression configuration."""
        progression_config = {
            'A': {
                'progression_months': [5, 11],
                'time_on_level': 6,
                'progression_rate': 0.15,
                'journey': 'Journey 1'
            },
            'AC': {
                'progression_months': [5, 11],
                'time_on_level': 9,
                'progression_rate': 0.12,
                'journey': 'Journey 1'
            }
        }
        
        # Should not raise any exception
        self.validator._validate_progression_config(progression_config)
    
    def test_validate_progression_config_with_missing_fields(self):
        """Test validation of progression config with missing required fields."""
        progression_config = {
            'A': {
                'progression_months': [5, 11]
                # Missing time_on_level, progression_rate
            }
        }
        
        with pytest.raises(ValueError, match="progression_config.A must contain time_on_level"):
            self.validator._validate_progression_config(progression_config)
    
    def test_validate_progression_config_with_invalid_months(self):
        """Test validation of progression config with invalid months."""
        progression_config = {
            'A': {
                'progression_months': [5, 13],  # Invalid month 13
                'time_on_level': 6,
                'progression_rate': 0.15
            }
        }
        
        with pytest.raises(ValueError, match="progression_config.A.progression_months must contain integers between 1 and 12"):
            self.validator._validate_progression_config(progression_config)
    
    def test_validate_progression_config_with_invalid_rate(self):
        """Test validation of progression config with invalid progression rate."""
        progression_config = {
            'A': {
                'progression_months': [5, 11],
                'time_on_level': 6,
                'progression_rate': 1.5  # Should be between 0 and 1
            }
        }
        
        with pytest.raises(ValueError, match="progression_config.A.progression_rate must be a number between 0 and 1"):
            self.validator._validate_progression_config(progression_config)
    
    def test_validate_cat_curves_with_valid_data(self):
        """Test validation of valid CAT curves."""
        cat_curves = {
            'A': {
                'CAT0': 0.0,
                'CAT6': 0.85,
                'CAT12': 0.90,
                'CAT18': 0.0
            },
            'AC': {
                'CAT0': 0.0,
                'CAT6': 0.10,
                'CAT12': 0.80,
                'CAT18': 0.50
            }
        }
        
        # Should not raise any exception
        self.validator._validate_cat_curves(cat_curves)
    
    def test_validate_cat_curves_with_invalid_probability(self):
        """Test validation of CAT curves with invalid probability."""
        cat_curves = {
            'A': {
                'CAT6': 1.5  # Should be between 0 and 1
            }
        }
        
        with pytest.raises(ValueError, match="CAT probability for A.CAT6 must be a number between 0 and 1"):
            self.validator._validate_cat_curves(cat_curves)
    
    def test_validate_cat_curves_with_invalid_category_type(self):
        """Test validation of CAT curves with invalid category type."""
        cat_curves = {
            'A': {
                123: 0.85  # Category should be string
            }
        }
        
        with pytest.raises(ValueError, match="CAT categories in cat_curves.A must be strings"):
            self.validator._validate_cat_curves(cat_curves)
    
    def test_validate_pydantic_model_with_valid_model(self):
        """Test validation of Pydantic model."""
        class TestModel(BaseModel):
            name: str = Field(..., description="Test name")
            value: int = Field(..., description="Test value")
        
        model_instance = TestModel(name="test", value=123)
        
        # Should not raise any exception
        self.validator.validate_pydantic_model(model_instance, TestModel)
    
    def test_validate_pydantic_model_with_wrong_type(self):
        """Test validation of Pydantic model with wrong type."""
        class TestModel(BaseModel):
            name: str = Field(..., description="Test name")
            value: int = Field(..., description="Test value")
        
        class WrongModel(BaseModel):
            name: str = Field(..., description="Wrong model")
        
        model_instance = TestModel(name="test", value=123)
        
        with pytest.raises(ValueError, match="Model instance must be of type WrongModel"):
            self.validator.validate_pydantic_model(model_instance, WrongModel)
    
    def test_validate_baseline_input_with_valid_data(self):
        """Test validation of valid baseline input."""
        baseline_input = {
            'global': {
                'recruitment': {
                    'Consultant': {
                        'A': {
                            '202501': 3.0,
                            '202502': 3.0
                        }
                    }
                },
                'churn': {
                    'Consultant': {
                        'A': {
                            '202501': 1.0,
                            '202502': 1.0
                        }
                    }
                }
            }
        }
        
        # Should not raise any exception
        self.validator._validate_baseline_input(baseline_input)
    
    def test_validate_baseline_input_with_invalid_value_type(self):
        """Test validation of baseline input with invalid value type."""
        baseline_input = {
            'global': {
                'recruitment': {
                    'Consultant': {
                        'A': {
                            '202501': "not a number"
                        }
                    }
                }
            }
        }
        
        with pytest.raises(ValueError, match="Invalid recruitment value for Consultant.202501 in A"):
            self.validator._validate_baseline_input(baseline_input)
    
    def test_validate_levers_with_valid_data(self):
        """Test validation of valid levers."""
        levers = {
            'global': {
                'recruitment': {'A': 1.2, 'AC': 1.1},
                'churn': {'A': 0.9, 'AC': 0.8},
                'price': {'A': 1.05, 'AC': 1.03},
                'salary': {'A': 1.02, 'AC': 1.01}
            }
        }
        
        # Should not raise any exception
        self.validator._validate_levers(levers)
    
    def test_validate_levers_with_unknown_type(self):
        """Test validation of levers with unknown lever type."""
        levers = {
            'global': {
                'unknown_lever': {'A': 1.2}
            }
        }
        
        with pytest.raises(ValueError, match="Unknown lever type: unknown_lever"):
            self.validator._validate_levers(levers)
    
    def test_validate_levers_with_invalid_value_type(self):
        """Test validation of levers with invalid value type."""
        levers = {
            'global': {
                'recruitment': {'A': "not a number"}
            }
        }
        
        with pytest.raises(ValueError, match="Invalid recruitment lever value for level A"):
            self.validator._validate_levers(levers) 