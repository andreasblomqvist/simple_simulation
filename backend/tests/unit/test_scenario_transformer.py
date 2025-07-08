"""
Unit tests for ScenarioTransformer service.
Tests data transformation operations and validation.
"""
import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from src.services.scenario_transformer import ScenarioTransformer
from src.services.error_handler import ValidationError
from src.services.simulation.progression_models import ProgressionConfig, CATCurves
from src.services.kpi.kpi_models import EconomicParameters


class TestScenarioTransformer:
    """Test cases for ScenarioTransformer service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = ScenarioTransformer()
        self.correlation_id = "test-123"
    
    def test_transform_scenario_to_economic_params_with_defaults(self):
        """Test economic parameters transformation with default values."""
        # Create mock scenario definition with no economic params
        scenario_def = Mock()
        scenario_def.economic_params = None
        
        result = self.transformer.transform_scenario_to_economic_params(scenario_def, self.correlation_id)
        
        assert isinstance(result, EconomicParameters)
        assert result.unplanned_absence == 0.05
        assert result.other_expense == 19000000.0
        assert result.employment_cost_rate == 0.40
        assert result.working_hours_per_month == 166.4
        assert result.utilization == 0.85
        assert result.price_increase == 0.03
        assert result.salary_increase == 0.02
    
    def test_transform_scenario_to_economic_params_with_custom_values(self):
        """Test economic parameters transformation with custom values."""
        # Create mock scenario definition with custom economic params
        scenario_def = Mock()
        scenario_def.economic_params = {
            'unplanned_absence': 0.08,
            'other_expense': 25000000.0,
            'employment_cost_rate': 0.45,
            'working_hours_per_month': 160.0,
            'utilization': 0.90,
            'price_increase': 0.05,
            'salary_increase': 0.03
        }
        
        result = self.transformer.transform_scenario_to_economic_params(scenario_def, self.correlation_id)
        
        assert isinstance(result, EconomicParameters)
        assert result.unplanned_absence == 0.08
        assert result.other_expense == 25000000.0
        assert result.employment_cost_rate == 0.45
        assert result.working_hours_per_month == 160.0
        assert result.utilization == 0.90
        assert result.price_increase == 0.05
        assert result.salary_increase == 0.03
    
    def test_transform_scenario_to_economic_params_filters_invalid_keys(self):
        """Test that invalid keys are filtered out from economic parameters."""
        scenario_def = Mock()
        scenario_def.economic_params = {
            'unplanned_absence': 0.08,
            'invalid_key': 'should_be_filtered',
            'other_expense': 25000000.0,
            'another_invalid': 123
        }
        
        result = self.transformer.transform_scenario_to_economic_params(scenario_def, self.correlation_id)
        
        assert isinstance(result, EconomicParameters)
        assert result.unplanned_absence == 0.08
        assert result.other_expense == 25000000.0
        # Other values should be defaults
        assert result.employment_cost_rate == 0.40
        assert result.utilization == 0.85
    
    def test_transform_dict_to_progression_config_success(self):
        """Test successful transformation of dict to ProgressionConfig."""
        progression_data = {
            'A': {'progression_months': [5, 11], 'progression_rate': 0.15},
            'AC': {'progression_months': [5, 11], 'progression_rate': 0.12},
            'C': {'progression_months': [5, 11], 'progression_rate': 0.10}
        }
        
        with patch.object(ProgressionConfig, 'from_dict') as mock_from_dict:
            mock_config = Mock(spec=ProgressionConfig)
            mock_from_dict.return_value = mock_config
            
            result = self.transformer.transform_dict_to_progression_config(progression_data, self.correlation_id)
            
            mock_from_dict.assert_called_once_with(progression_data)
            assert result == mock_config
    
    def test_transform_dict_to_progression_config_failure(self):
        """Test transformation failure raises ValidationError."""
        progression_data = {'invalid': 'data'}
        
        with patch.object(ProgressionConfig, 'from_dict', side_effect=ValueError("Invalid data")):
            with pytest.raises(ValidationError, match="ProgressionConfig transformation failed"):
                self.transformer.transform_dict_to_progression_config(progression_data, self.correlation_id)
    
    def test_transform_dict_to_cat_curves_success(self):
        """Test successful transformation of dict to CATCurves."""
        cat_curves_data = {
            'A': {'progression_probability': 0.80, 'retention_probability': 0.95},
            'AC': {'progression_probability': 0.75, 'retention_probability': 0.96},
            'C': {'progression_probability': 0.70, 'retention_probability': 0.97}
        }
        
        with patch.object(CATCurves, 'from_dict') as mock_from_dict:
            mock_curves = Mock(spec=CATCurves)
            mock_from_dict.return_value = mock_curves
            
            result = self.transformer.transform_dict_to_cat_curves(cat_curves_data, self.correlation_id)
            
            mock_from_dict.assert_called_once_with(cat_curves_data)
            assert result == mock_curves
    
    def test_transform_dict_to_cat_curves_failure(self):
        """Test transformation failure raises ValidationError."""
        cat_curves_data = {'invalid': 'data'}
        
        with patch.object(CATCurves, 'from_dict', side_effect=ValueError("Invalid data")):
            with pytest.raises(ValidationError, match="CATCurves transformation failed"):
                self.transformer.transform_dict_to_cat_curves(cat_curves_data, self.correlation_id)
    
    def test_transform_results_to_serializable_with_pydantic_model(self):
        """Test results transformation with Pydantic model."""
        # Create a mock Pydantic model
        mock_model = Mock()
        mock_model.model_dump.return_value = {'key': 'value', 'number': 42}
        
        result = self.transformer.transform_results_to_serializable(mock_model, self.correlation_id)
        
        assert result == {'key': 'value', 'number': 42}
        mock_model.model_dump.assert_called_once()
    
    def test_transform_results_to_serializable_with_dict(self):
        """Test results transformation with dictionary."""
        input_data = {
            'level1': {'key1': 'value1', 'key2': 123},
            'level2': {'nested': {'deep': 'value'}}
        }
        
        result = self.transformer.transform_results_to_serializable(input_data, self.correlation_id)
        
        assert result == input_data  # Should remain unchanged
    
    def test_transform_results_to_serializable_with_list(self):
        """Test results transformation with list."""
        input_data = [
            {'id': 1, 'name': 'item1'},
            {'id': 2, 'name': 'item2'}
        ]
        
        result = self.transformer.transform_results_to_serializable(input_data, self.correlation_id)
        
        assert result == input_data  # Should remain unchanged
    
    def test_transform_results_to_serializable_with_nested_pydantic(self):
        """Test results transformation with nested Pydantic models."""
        # Create nested structure with Pydantic models
        inner_model = Mock()
        inner_model.model_dump.return_value = {'inner': 'data'}
        
        outer_model = Mock()
        outer_model.model_dump.return_value = {
            'outer': 'data',
            'nested': inner_model
        }
        
        result = self.transformer.transform_results_to_serializable(outer_model, self.correlation_id)
        
        expected = {
            'outer': 'data',
            'nested': {'inner': 'data'}
        }
        assert result == expected
    
    def test_transform_results_to_serializable_with_non_serializable(self):
        """Test results transformation with non-serializable objects."""
        # Create object with non-serializable data
        class NonSerializable:
            def __init__(self):
                self.data = "test"
        
        non_serializable = NonSerializable()
        input_data = {
            'normal': 'value',
            'problematic': non_serializable
        }
        
        result = self.transformer.transform_results_to_serializable(input_data, self.correlation_id)
        
        assert result['normal'] == 'value'
        assert result['problematic'] == str(non_serializable)
    
    def test_transform_scenario_data_for_engine_success(self):
        """Test successful transformation of scenario data for engine."""
        resolved_data = {
            'offices': {'office1': Mock(), 'office2': Mock()},
            'progression_config': {'A': {'progression_months': [5, 11]}},
            'cat_curves': {'A': {'progression_probability': 0.80}}
        }
        
        with patch.object(self.transformer, 'transform_dict_to_progression_config') as mock_prog:
            with patch.object(self.transformer, 'transform_dict_to_cat_curves') as mock_cat:
                mock_prog_config = Mock(spec=ProgressionConfig)
                mock_cat_curves = Mock(spec=CATCurves)
                mock_prog.return_value = mock_prog_config
                mock_cat.return_value = mock_cat_curves
                
                result = self.transformer.transform_scenario_data_for_engine(resolved_data, self.correlation_id)
                
                assert result['offices'] == resolved_data['offices']
                assert result['progression_config'] == mock_prog_config
                assert result['cat_curves'] == mock_cat_curves
                
                mock_prog.assert_called_once_with(resolved_data['progression_config'], self.correlation_id)
                mock_cat.assert_called_once_with(resolved_data['cat_curves'], self.correlation_id)
    
    def test_transform_scenario_data_for_engine_failure(self):
        """Test transformation failure raises ValidationError."""
        resolved_data = {
            'offices': {'office1': Mock()},
            'progression_config': {'invalid': 'data'},
            'cat_curves': {'invalid': 'data'}
        }
        
        with patch.object(self.transformer, 'transform_dict_to_progression_config', side_effect=ValidationError("Test error")):
            with pytest.raises(ValidationError, match="Engine data transformation failed"):
                self.transformer.transform_scenario_data_for_engine(resolved_data, self.correlation_id)
    
    def test_clean_for_serialization_removes_none_keys(self):
        """Test that None keys are removed during serialization cleaning."""
        input_data = {
            'valid_key': 'value',
            None: 'should_be_removed',
            'another_valid': 123
        }
        
        result = self.transformer._clean_for_serialization(input_data)
        
        assert 'valid_key' in result
        assert 'another_valid' in result
        assert None not in result
        assert len(result) == 2
    
    def test_clean_for_serialization_handles_nested_structures(self):
        """Test cleaning of nested data structures."""
        input_data = {
            'level1': {
                'level2': {
                    None: 'removed',
                    'valid': 'kept'
                }
            },
            'list': [
                {'item1': 'value1', None: 'removed'},
                {'item2': 'value2'}
            ]
        }
        
        result = self.transformer._clean_for_serialization(input_data)
        
        assert result['level1']['level2']['valid'] == 'kept'
        assert None not in result['level1']['level2']
        assert result['list'][0]['item1'] == 'value1'
        assert None not in result['list'][0]
        assert result['list'][1]['item2'] == 'value2'
    
    def test_to_dict_with_pydantic_model(self):
        """Test _to_dict method with Pydantic model."""
        mock_model = Mock()
        mock_model.model_dump.return_value = {'pydantic': 'data'}
        
        result = self.transformer._to_dict(mock_model)
        
        assert result == {'pydantic': 'data'}
        mock_model.model_dump.assert_called_once()
    
    def test_to_dict_with_nested_structures(self):
        """Test _to_dict method with nested structures containing Pydantic models."""
        inner_model = Mock()
        inner_model.model_dump.return_value = {'inner': 'data'}
        
        input_data = {
            'normal': 'value',
            'nested': {
                'model': inner_model,
                'list': [inner_model, 'string']
            }
        }
        
        result = self.transformer._to_dict(input_data)
        
        expected = {
            'normal': 'value',
            'nested': {
                'model': {'inner': 'data'},
                'list': [{'inner': 'data'}, 'string']
            }
        }
        assert result == expected 