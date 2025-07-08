"""
Unit tests for absolute and percentage-based recruitment/churn support.
"""
import pytest
from src.services.simulation.workforce import get_effective_recruitment_value, get_effective_churn_value
from src.services.simulation_engine import RoleData, Level, Journey, Month
from src.services.config_service import ConfigService


class TestAbsolutePercentageSupport:
    """Test cases for absolute and percentage-based recruitment/churn support."""
    
    def test_recruitment_absolute_takes_precedence(self):
        """Test that absolute recruitment values take precedence over percentage."""
        role_data = RoleData()
        role_data.recruitment_1 = 0.1  # 10% recruitment
        role_data.recruitment_abs_1 = 5  # 5 absolute recruits
        role_data.fte = 100  # 100 FTE
        
        value, method, details = get_effective_recruitment_value(role_data, 1, 100)
        
        assert value == 5
        assert method == "absolute"
        assert details["absolute_value"] == 5
        assert details["percentage_value"] == 0.1
        assert details["field_used"] == "recruitment_abs_1"
    
    def test_recruitment_percentage_fallback(self):
        """Test that percentage calculation is used when no absolute value is present."""
        role_data = RoleData()
        role_data.recruitment_1 = 0.1  # 10% recruitment
        role_data.recruitment_abs_1 = None  # No absolute value
        role_data.fte = 100  # 100 FTE
        
        value, method, details = get_effective_recruitment_value(role_data, 1, 100)
        
        assert value == 10  # 10% of 100 = 10
        assert method == "percentage"
        assert details["absolute_value"] is None
        assert details["percentage_value"] == 0.1
        assert details["calculated_value"] == 10
        assert details["field_used"] == "recruitment_1"
    
    def test_recruitment_zero_absolute(self):
        """Test that zero absolute value is respected."""
        role_data = RoleData()
        role_data.recruitment_1 = 0.1  # 10% recruitment
        role_data.recruitment_abs_1 = 0  # Zero absolute recruits
        role_data.fte = 100  # 100 FTE
        
        value, method, details = get_effective_recruitment_value(role_data, 1, 100)
        
        assert value == 0
        assert method == "absolute"
        assert details["absolute_value"] == 0
    
    def test_recruitment_missing_both_fields(self):
        """Test behavior when neither absolute nor percentage fields are present."""
        role_data = RoleData()
        # Don't set any recruitment fields
        role_data.fte = 100  # 100 FTE
        
        value, method, details = get_effective_recruitment_value(role_data, 1, 100)
        
        assert value == 0  # Should default to 0
        assert method == "percentage"
        assert details["percentage_value"] == 0.0
    
    def test_churn_absolute_takes_precedence(self):
        """Test that absolute churn values take precedence over percentage."""
        role_data = RoleData()
        role_data.churn_1 = 0.05  # 5% churn
        role_data.churn_abs_1 = 3  # 3 absolute churns
        role_data.fte = 100  # 100 FTE
        
        value, method, details = get_effective_churn_value(role_data, 1, 100)
        
        assert value == 3
        assert method == "absolute"
        assert details["absolute_value"] == 3
        assert details["percentage_value"] == 0.05
        assert details["field_used"] == "churn_abs_1"
    
    def test_churn_percentage_fallback(self):
        """Test that percentage calculation is used when no absolute value is present."""
        role_data = RoleData()
        role_data.churn_1 = 0.05  # 5% churn
        role_data.churn_abs_1 = None  # No absolute value
        role_data.fte = 100  # 100 FTE
        
        value, method, details = get_effective_churn_value(role_data, 1, 100)
        
        assert value == 5  # 5% of 100 = 5
        assert method == "percentage"
        assert details["absolute_value"] is None
        assert details["percentage_value"] == 0.05
        assert details["calculated_value"] == 5
        assert details["field_used"] == "churn_1"
    
    def test_churn_zero_absolute(self):
        """Test that zero absolute churn value is respected."""
        role_data = RoleData()
        role_data.churn_1 = 0.05  # 5% churn
        role_data.churn_abs_1 = 0  # Zero absolute churns
        role_data.fte = 100  # 100 FTE
        
        value, method, details = get_effective_churn_value(role_data, 1, 100)
        
        assert value == 0
        assert method == "absolute"
        assert details["absolute_value"] == 0
    
    def test_churn_missing_both_fields(self):
        """Test behavior when neither absolute nor percentage churn fields are present."""
        role_data = RoleData()
        # Don't set any churn fields
        role_data.fte = 100  # 100 FTE
        
        value, method, details = get_effective_churn_value(role_data, 1, 100)
        
        assert value == 0  # Should default to 0
        assert method == "percentage"
        assert details["percentage_value"] == 0.0
    
    def test_level_objects_support(self):
        """Test that Level objects also support absolute/percentage fields."""
        level = Level(
            name="A",
            journey=Journey.JOURNEY_1,
            # Progression fields
            progression_months=[Month.MAY, Month.NOV],
            progression_1=0.0, progression_2=0.0, progression_3=0.0, progression_4=0.0,
            progression_5=0.1, progression_6=0.0, progression_7=0.0, progression_8=0.0,
            progression_9=0.0, progression_10=0.0, progression_11=0.1, progression_12=0.0,
            # Recruitment fields
            recruitment_1=0.1, recruitment_2=0.1, recruitment_3=0.1, recruitment_4=0.1,
            recruitment_5=0.1, recruitment_6=0.1, recruitment_7=0.1, recruitment_8=0.1,
            recruitment_9=0.1, recruitment_10=0.1, recruitment_11=0.1, recruitment_12=0.1,
            # Churn fields
            churn_1=0.05, churn_2=0.05, churn_3=0.05, churn_4=0.05,
            churn_5=0.05, churn_6=0.05, churn_7=0.05, churn_8=0.05,
            churn_9=0.05, churn_10=0.05, churn_11=0.05, churn_12=0.05,
            # Price fields
            price_1=1000, price_2=1000, price_3=1000, price_4=1000,
            price_5=1000, price_6=1000, price_7=1000, price_8=1000,
            price_9=1000, price_10=1000, price_11=1000, price_12=1000,
            # Salary fields
            salary_1=50000, salary_2=50000, salary_3=50000, salary_4=50000,
            salary_5=50000, salary_6=50000, salary_7=50000, salary_8=50000,
            salary_9=50000, salary_10=50000, salary_11=50000, salary_12=50000,
            # UTR fields
            utr_1=0.85, utr_2=0.85, utr_3=0.85, utr_4=0.85,
            utr_5=0.85, utr_6=0.85, utr_7=0.85, utr_8=0.85,
            utr_9=0.85, utr_10=0.85, utr_11=0.85, utr_12=0.85
        )
        
        # Set absolute values
        level.recruitment_abs_1 = 7
        level.churn_abs_1 = 2
        
        # Test recruitment
        value, method, details = get_effective_recruitment_value(level, 1, 50)
        assert value == 7
        assert method == "absolute"
        
        # Test churn
        value, method, details = get_effective_churn_value(level, 1, 50)
        assert value == 2
        assert method == "absolute"
    
    def test_backward_compatibility_percentage_only(self):
        """Test that existing percentage-only configurations continue to work."""
        role_data = RoleData()
        role_data.recruitment_1 = 0.1  # 10% recruitment
        role_data.churn_1 = 0.05  # 5% churn
        # Don't set any absolute fields
        role_data.fte = 100  # 100 FTE
        
        # Test recruitment
        value, method, details = get_effective_recruitment_value(role_data, 1, 100)
        assert value == 10  # 10% of 100 = 10
        assert method == "percentage"
        assert details["absolute_value"] is None
        
        # Test churn
        value, method, details = get_effective_churn_value(role_data, 1, 100)
        assert value == 5  # 5% of 100 = 5
        assert method == "percentage"
        assert details["absolute_value"] is None
    
    def test_mixed_scenarios(self):
        """Test mixing absolute and percentage values across different months."""
        role_data = RoleData()
        
        # Month 1: Absolute recruitment, percentage churn
        role_data.recruitment_abs_1 = 5
        role_data.churn_1 = 0.05
        
        # Month 2: Percentage recruitment, absolute churn
        role_data.recruitment_2 = 0.1
        role_data.churn_abs_2 = 3
        
        # Month 3: Both percentage
        role_data.recruitment_3 = 0.1
        role_data.churn_3 = 0.05
        
        # Month 4: Both absolute
        role_data.recruitment_abs_4 = 2
        role_data.churn_abs_4 = 1
        
        role_data.fte = 100
        
        # Test month 1
        rec_value, rec_method, _ = get_effective_recruitment_value(role_data, 1, 100)
        churn_value, churn_method, _ = get_effective_churn_value(role_data, 1, 100)
        assert rec_value == 5 and rec_method == "absolute"
        assert churn_value == 5 and churn_method == "percentage"
        
        # Test month 2
        rec_value, rec_method, _ = get_effective_recruitment_value(role_data, 2, 100)
        churn_value, churn_method, _ = get_effective_churn_value(role_data, 2, 100)
        assert rec_value == 10 and rec_method == "percentage"
        assert churn_value == 3 and churn_method == "absolute"
        
        # Test month 3
        rec_value, rec_method, _ = get_effective_recruitment_value(role_data, 3, 100)
        churn_value, churn_method, _ = get_effective_churn_value(role_data, 3, 100)
        assert rec_value == 10 and rec_method == "percentage"
        assert churn_value == 5 and churn_method == "percentage"
        
        # Test month 4
        rec_value, rec_method, _ = get_effective_recruitment_value(role_data, 4, 100)
        churn_value, churn_method, _ = get_effective_churn_value(role_data, 4, 100)
        assert rec_value == 2 and rec_method == "absolute"
        assert churn_value == 1 and churn_method == "absolute"


class TestConfigServiceValidation:
    """Test cases for config service validation of absolute/percentage fields."""
    
    def test_validation_with_mixed_fields(self):
        """Test validation with mixed absolute and percentage fields."""
        config_service = ConfigService()
        
        config = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {
                            "fte": 50,
                            "recruitment_1": 0.1,      # 10% fallback
                            "recruitment_abs_1": 5,    # 5 absolute (overrides)
                            "churn_1": 0.05,           # 5% fallback
                            "churn_abs_1": None,       # Use percentage
                            "recruitment_2": 0.1,      # 10% fallback
                            "recruitment_abs_2": None, # Use percentage
                            "churn_2": 0.05,           # 5% fallback
                            "churn_abs_2": 2,          # 2 absolute (overrides)
                        }
                    }
                }
            }
        }
        
        results = config_service.validate_absolute_percentage_fields(config)
        
        assert results["validated_offices"] == 1
        assert results["validated_roles"] == 1
        assert results["validated_levels"] == 1
        assert len(results["errors"]) == 0
        # Should have warnings about consistency
        assert len(results["warnings"]) > 0
    
    def test_validation_missing_fields(self):
        """Test validation when fields are missing."""
        config_service = ConfigService()
        
        config = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {
                            "fte": 50,
                            # Missing recruitment_1 and recruitment_abs_1
                            "churn_1": 0.05,           # Only percentage
                            # Missing churn_abs_1
                        }
                    }
                }
            }
        }
        
        results = config_service.validate_absolute_percentage_fields(config)
        
        assert len(results["warnings"]) > 0
        # Should warn about missing recruitment fields
        assert any("recruitment_1" in warning for warning in results["warnings"])
    
    def test_validation_invalid_ranges(self):
        """Test validation with invalid value ranges."""
        config_service = ConfigService()
        
        config = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {
                            "fte": 50,
                            "recruitment_1": 1.5,      # Invalid: > 1.0
                            "churn_1": -0.1,           # Invalid: < 0
                            "recruitment_abs_1": 2000, # Invalid: > 1000
                            "churn_abs_1": -5,         # Invalid: < 0
                        }
                    }
                }
            }
        }
        
        results = config_service.validate_absolute_percentage_fields(config)
        
        assert len(results["errors"]) > 0
        # Should have errors for invalid ranges
        assert any("outside valid range" in error for error in results["errors"])


if __name__ == "__main__":
    pytest.main([__file__]) 