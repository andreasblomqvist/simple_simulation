"""
Unit tests for progression models to ensure they can be created with input data
and don't hardcode values.
"""
import pytest
from src.services.simulation.progression_models import (
    ProgressionConfig, 
    LevelProgressionConfig,
    CATCurves,
    CATCurve
)


class TestProgressionConfig:
    """Test ProgressionConfig creation and usage with input data."""
    
    def test_create_progression_config_from_input_data(self):
        """Test that ProgressionConfig can be created from input data."""
        # Custom input data
        input_data = {
            'A': {
                'progression_months': [5, 11],  # Custom months
                'time_on_level': 8,  # Custom time
                'progression_rate': 0.15,  # Custom rate
                'journey': 'Journey 1'  # Custom journey
            },
            'AC': {
                'progression_months': [5, 11],
                'time_on_level': 10,
                'progression_rate': 0.12,
                'journey': 'Journey 1'
            },
            'C': {
                'progression_months': [5],  # Different pattern
                'time_on_level': 15,
                'progression_rate': 0.10,
                'journey': 'Journey 2'
            }
        }
        
        # Create from input data
        config = ProgressionConfig.from_dict(input_data)
        
        # Verify the data was used correctly
        assert 'A' in config.levels
        assert 'AC' in config.levels
        assert 'C' in config.levels
        
        # Check A level
        level_a = config.get_level_config('A')
        assert level_a.progression_months == [5, 11]
        assert level_a.time_on_level == 8
        assert level_a.progression_rate == 0.15
        assert level_a.journey == 'Journey 1'
        
        # Check AC level
        level_ac = config.get_level_config('AC')
        assert level_ac.progression_months == [5, 11]
        assert level_ac.time_on_level == 10
        assert level_ac.progression_rate == 0.12
        
        # Check C level
        level_c = config.get_level_config('C')
        assert level_c.progression_months == [5]  # Different from A/AC
        assert level_c.time_on_level == 15
        assert level_c.progression_rate == 0.10
        assert level_c.journey == 'Journey 2'
    
    def test_progression_config_methods_work_with_input_data(self):
        """Test that ProgressionConfig methods work correctly with input data."""
        input_data = {
            'A': {
                'progression_months': [3, 9],
                'time_on_level': 6,
                'progression_rate': 0.20,
                'journey': 'Journey 1'
            }
        }
        
        config = ProgressionConfig.from_dict(input_data)
        
        # Test is_progression_month
        assert config.is_progression_month('A', 3) == True
        assert config.is_progression_month('A', 9) == True
        assert config.is_progression_month('A', 6) == False
        
        # Test get_minimum_tenure
        assert config.get_minimum_tenure('A') == 6
        
        # Test non-existent level
        assert config.is_progression_month('X', 3) == False
        assert config.get_minimum_tenure('X') == 6  # Default value
    
    def test_progression_config_to_dict_preserves_input_data(self):
        """Test that to_dict() preserves the original input data structure."""
        input_data = {
            'A': {
                'progression_months': [1, 7],
                'time_on_level': 12,
                'progression_rate': 0.25,
                'journey': 'Custom Journey'
            }
        }
        
        config = ProgressionConfig.from_dict(input_data)
        output_data = config.to_dict()
        
        # Should preserve the structure
        assert 'A' in output_data
        assert output_data['A']['progression_months'] == [1, 7]
        assert output_data['A']['time_on_level'] == 12
        assert output_data['A']['progression_rate'] == 0.25
        assert output_data['A']['journey'] == 'Custom Journey'


class TestCATCurves:
    """Test CATCurves creation and usage with input data."""
    
    def test_create_cat_curves_from_input_data(self):
        """Test that CATCurves can be created from input data."""
        # Custom input data
        input_data = {
            'A': {
                'CAT0': 0.0,
                'CAT6': 0.85,  # Custom probability
                'CAT12': 0.90,  # Custom probability
                'CAT18': 0.0
            },
            'AC': {
                'CAT0': 0.0,
                'CAT6': 0.10,  # Different pattern
                'CAT12': 0.80,
                'CAT18': 0.50,
                'CAT24': 0.0
            },
            'C': {
                'CAT0': 0.0,
                'CAT6': 0.05,
                'CAT12': 0.60,  # Custom probability
                'CAT18': 0.70,
                'CAT24': 0.30,
                'CAT30': 0.80
            }
        }
        
        # Create from input data
        cat_curves = CATCurves.from_dict(input_data)
        
        # Verify the data was used correctly
        assert 'A' in cat_curves.curves
        assert 'AC' in cat_curves.curves
        assert 'C' in cat_curves.curves
        
        # Check A level
        curve_a = cat_curves.get_curve('A')
        assert curve_a.get_probability('CAT6') == 0.85
        assert curve_a.get_probability('CAT12') == 0.90
        assert curve_a.get_probability('CAT18') == 0.0
        
        # Check AC level
        curve_ac = cat_curves.get_curve('AC')
        assert curve_ac.get_probability('CAT6') == 0.10
        assert curve_ac.get_probability('CAT12') == 0.80
        assert curve_ac.get_probability('CAT18') == 0.50
        
        # Check C level
        curve_c = cat_curves.get_curve('C')
        assert curve_c.get_probability('CAT12') == 0.60
        assert curve_c.get_probability('CAT30') == 0.80
    
    def test_cat_curves_methods_work_with_input_data(self):
        """Test that CATCurves methods work correctly with input data."""
        input_data = {
            'A': {
                'CAT0': 0.0,
                'CAT6': 0.75,
                'CAT12': 0.85
            }
        }
        
        cat_curves = CATCurves.from_dict(input_data)
        
        # Test get_probability
        assert cat_curves.get_probability('A', 'CAT6') == 0.75
        assert cat_curves.get_probability('A', 'CAT12') == 0.85
        assert cat_curves.get_probability('A', 'CAT18') == 0.0  # Default for missing
        
        # Test non-existent level
        assert cat_curves.get_probability('X', 'CAT6') == 0.0
    
    def test_cat_curves_to_dict_preserves_input_data(self):
        """Test that to_dict() preserves the original input data structure."""
        input_data = {
            'A': {
                'CAT0': 0.0,
                'CAT6': 0.80,
                'CAT12': 0.90
            }
        }
        
        cat_curves = CATCurves.from_dict(input_data)
        output_data = cat_curves.to_dict()
        
        # Should preserve the structure
        assert 'A' in output_data
        assert output_data['A']['CAT0'] == 0.0
        assert output_data['A']['CAT6'] == 0.80
        assert output_data['A']['CAT12'] == 0.90


class TestLevelProgressionConfig:
    """Test LevelProgressionConfig creation and usage."""
    
    def test_create_level_progression_config_with_input_data(self):
        """Test that LevelProgressionConfig can be created with input data."""
        config = LevelProgressionConfig(
            level_name='CustomLevel',
            progression_months=[2, 8],  # Custom months
            time_on_level=10,  # Custom time
            progression_rate=0.18,  # Custom rate
            journey='Custom Journey'  # Custom journey
        )
        
        assert config.level_name == 'CustomLevel'
        assert config.progression_months == [2, 8]
        assert config.time_on_level == 10
        assert config.progression_rate == 0.18
        assert config.journey == 'Custom Journey'
    
    def test_level_progression_config_defaults(self):
        """Test that LevelProgressionConfig uses sensible defaults."""
        config = LevelProgressionConfig(
            level_name='TestLevel',
            progression_months=[1, 7]
        )
        
        assert config.level_name == 'TestLevel'
        assert config.progression_months == [1, 7]
        assert config.time_on_level == 6  # Default
        assert config.progression_rate == 0.0  # Default
        assert config.journey == 'Journey 1'  # Default


class TestCATCurve:
    """Test CATCurve creation and usage."""
    
    def test_create_cat_curve_with_input_data(self):
        """Test that CATCurve can be created with input data."""
        input_data = {
            'CAT0': 0.0,
            'CAT6': 0.85,
            'CAT12': 0.90,
            'CAT18': 0.0
        }
        
        curve = CATCurve.from_dict('TestLevel', input_data)
        
        assert curve.level_name == 'TestLevel'
        assert curve.get_probability('CAT6') == 0.85
        assert curve.get_probability('CAT12') == 0.90
        assert curve.get_probability('CAT18') == 0.0
        assert curve.get_probability('CAT24') == 0.0  # Default for missing
    
    def test_cat_curve_to_dict_preserves_input_data(self):
        """Test that to_dict() preserves the original input data."""
        input_data = {
            'CAT0': 0.0,
            'CAT6': 0.75,
            'CAT12': 0.85
        }
        
        curve = CATCurve.from_dict('TestLevel', input_data)
        output_data = curve.to_dict()
        
        assert output_data == input_data


class TestIntegration:
    """Integration tests to ensure models work together with input data."""
    
    def test_full_workflow_with_custom_data(self):
        """Test complete workflow using custom input data."""
        # Custom progression config
        progression_data = {
            'A': {
                'progression_months': [4, 10],
                'time_on_level': 8,
                'progression_rate': 0.20,
                'journey': 'Journey 1'
            }
        }
        
        # Custom CAT curves
        cat_data = {
            'A': {
                'CAT0': 0.0,
                'CAT6': 0.80,
                'CAT12': 0.90,
                'CAT18': 0.0
            }
        }
        
        # Create models from input data
        progression_config = ProgressionConfig.from_dict(progression_data)
        cat_curves = CATCurves.from_dict(cat_data)
        
        # Verify they work together
        level_config = progression_config.get_level_config('A')
        cat_curve = cat_curves.get_curve('A')
        
        assert level_config.progression_months == [4, 10]
        assert level_config.progression_rate == 0.20
        assert cat_curve.get_probability('CAT6') == 0.80
        assert cat_curve.get_probability('CAT12') == 0.90
        
        # Test progression month check
        assert progression_config.is_progression_month('A', 4) == True
        assert progression_config.is_progression_month('A', 10) == True
        assert progression_config.is_progression_month('A', 6) == False 