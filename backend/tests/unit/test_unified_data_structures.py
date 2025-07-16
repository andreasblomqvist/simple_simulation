"""
Unit tests for unified data structures implementation.

Tests validation, transformation, and consistency of the unified data models.
"""

import pytest
from pydantic import ValidationError
from datetime import datetime
import json

from src.services.unified_data_models import (
    ScenarioDefinition,
    TimeRange,
    EconomicParameters,
    BaselineInput,
    MonthlyValues,
    RoleData,
    LevelData,
    Levers,
    ProgressionConfig,
    CATCurves,
    validate_scenario_definition,
    validate_baseline_input_structure,
    migrate_old_scenario_to_unified
)

from src.services.data_validation_service import (
    DataValidationService,
    validate_scenario_data,
    validate_baseline_data
)

from src.services.data_transformation_service import (
    DataTransformationService,
    transform_legacy_scenario,
    generate_month_keys
)


class TestUnifiedDataModels:
    """Test unified data model validation"""
    
    def test_time_range_validation(self):
        """Test TimeRange model validation"""
        # Valid time range
        valid_time_range = TimeRange(
            start_year=2025,
            start_month=1,
            end_year=2030,
            end_month=12
        )
        assert valid_time_range.start_year == 2025
        assert valid_time_range.end_month == 12
        
        # Invalid year range
        with pytest.raises(ValidationError):
            TimeRange(start_year=2050, start_month=1, end_year=2025, end_month=12)
        
        # Invalid month range
        with pytest.raises(ValidationError):
            TimeRange(start_year=2025, start_month=13, end_year=2030, end_month=12)
    
    def test_monthly_values_validation(self):
        """Test MonthlyValues model validation"""
        # Valid monthly values
        valid_monthly = MonthlyValues(values={
            "202501": 10.0,
            "202502": 15.0,
            "202503": 12.0
        })
        assert valid_monthly.values["202501"] == 10.0
        
        # Invalid month key format
        with pytest.raises(ValidationError):
            MonthlyValues(values={"2025-01": 10.0})  # Wrong format
        
        # Invalid month range
        with pytest.raises(ValidationError):
            MonthlyValues(values={"202513": 10.0})  # Month 13
        
        # Negative values
        with pytest.raises(ValidationError):
            MonthlyValues(values={"202501": -5.0})
    
    def test_baseline_input_validation(self):
        """Test BaselineInput model validation"""
        valid_baseline = {
            "global": {
                "recruitment": {
                    "Consultant": {
                        "levels": {
                            "A": {
                                "recruitment": {"values": {"202501": 20}},
                                "churn": {"values": {"202501": 2}}
                            }
                        }
                    }
                },
                "churn": {
                    "Consultant": {
                        "levels": {
                            "A": {
                                "recruitment": {"values": {"202501": 20}},
                                "churn": {"values": {"202501": 2}}
                            }
                        }
                    }
                }
            }
        }
        
        # This should validate successfully
        baseline_input = BaselineInput(**valid_baseline)
        assert "recruitment" in baseline_input.global_data
        assert "churn" in baseline_input.global_data
    
    def test_scenario_definition_validation(self):
        """Test complete ScenarioDefinition validation"""
        valid_scenario = {
            "name": "Test Scenario",
            "description": "Test description",
            "time_range": {
                "start_year": 2025,
                "start_month": 1,
                "end_year": 2030,
                "end_month": 12
            },
            "office_scope": ["Stockholm"],
            "levers": {
                "recruitment": {"A": 1.0},
                "churn": {"A": 1.0},
                "progression": {"A": 1.0}
            },
            "economic_params": {
                "working_hours_per_month": 160.0,
                "employment_cost_rate": 0.3,
                "unplanned_absence": 0.05,
                "other_expense": 1000000.0
            },
            "baseline_input": {
                "global": {
                    "recruitment": {},
                    "churn": {}
                }
            }
        }
        
        scenario = ScenarioDefinition(**valid_scenario)
        assert scenario.name == "Test Scenario"
        assert scenario.time_range.start_year == 2025
        assert scenario.economic_params.working_hours_per_month == 160.0
    
    def test_lever_validation(self):
        """Test Levers model validation"""
        valid_levers = Levers(
            recruitment={"A": 1.2, "AC": 1.0},
            churn={"A": 0.8, "AC": 1.0},
            progression={"A": 1.1, "AC": 1.0}
        )
        assert valid_levers.recruitment["A"] == 1.2
        
        # Negative multipliers should fail
        with pytest.raises(ValidationError):
            Levers(recruitment={"A": -0.5})


class TestDataValidationService:
    """Test data validation service functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.validation_service = DataValidationService()
        
        self.valid_scenario_data = {
            "name": "Test Scenario",
            "description": "Test description",
            "time_range": {
                "start_year": 2025,
                "start_month": 1,
                "end_year": 2030,
                "end_month": 12
            },
            "office_scope": ["Stockholm"],
            "levers": {
                "recruitment": {"A": 1.0},
                "churn": {"A": 1.0},
                "progression": {"A": 1.0}
            },
            "economic_params": {
                "working_hours_per_month": 160.0,
                "employment_cost_rate": 0.3,
                "unplanned_absence": 0.05,
                "other_expense": 1000000.0
            },
            "baseline_input": {
                "global": {
                    "recruitment": {
                        "Consultant": {
                            "A": {"202501": 20, "202502": 15}
                        }
                    },
                    "churn": {
                        "Consultant": {
                            "A": {"202501": 2, "202502": 1}
                        }
                    }
                }
            }
        }
    
    def test_valid_scenario_validation(self):
        """Test validation of valid scenario data"""
        is_valid, errors = self.validation_service.validate_complete_scenario(self.valid_scenario_data)
        assert is_valid, f"Validation failed with errors: {errors}"
        assert len(errors) == 0
    
    def test_invalid_time_range_validation(self):
        """Test validation of invalid time range"""
        invalid_data = self.valid_scenario_data.copy()
        invalid_data["time_range"]["start_month"] = 13  # Invalid month
        
        is_valid, errors = self.validation_service.validate_complete_scenario(invalid_data)
        assert not is_valid
        assert len(errors) > 0
        assert any("month" in error.lower() for error in errors)
    
    def test_baseline_input_validation(self):
        """Test baseline input validation"""
        baseline_input = self.valid_scenario_data["baseline_input"]
        
        is_valid, errors = self.validation_service.validate_baseline_input(baseline_input)
        assert is_valid, f"Baseline validation failed: {errors}"
    
    def test_field_name_validation(self):
        """Test deprecated field name detection"""
        data_with_deprecated_fields = {
            "total": 100,  # Should be 'fte'
            "progression_rate": 0.5,  # Should be removed
            "Price_1": 1200.0,  # Should be 'price_1'
            "nested": {
                "total": 50,
                "progression_rate": 0.3
            }
        }
        
        issues = self.validation_service.validate_field_names(data_with_deprecated_fields)
        assert len(issues) > 0
        assert any("total" in issue for issue in issues)
        assert any("progression_rate" in issue for issue in issues)
        assert any("Price_1" in issue for issue in issues)
    
    def test_validation_report_generation(self):
        """Test comprehensive validation report generation"""
        report = self.validation_service.generate_validation_report(self.valid_scenario_data)
        
        assert "timestamp" in report
        assert "overall_status" in report
        assert "summary" in report
        assert report["overall_status"] in ["valid", "valid_with_warnings", "invalid"]


class TestDataTransformationService:
    """Test data transformation service functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.transformation_service = DataTransformationService()
        
        self.legacy_scenario_data = {
            "name": "Legacy Scenario",
            "description": "Legacy description",
            "time_range": {
                "start_year": 2025,
                "start_month": 1,
                "end_year": 2030,
                "end_month": 12
            },
            "office_scope": ["Stockholm"],
            "total": 100,  # Should become 'fte'
            "progression_rate": 0.5,  # Should be removed
            "Price_1": 1200.0,  # Should become 'price_1'
            "baseline_input": {
                "recruitment": {  # Missing 'global' wrapper
                    "Consultant": {
                        "A": {"202501": 20}
                    }
                },
                "churn": {
                    "Consultant": {
                        "A": {"202501": 2}
                    }
                }
            }
        }
    
    def test_legacy_scenario_transformation(self):
        """Test transformation of legacy scenario data"""
        transformed = self.transformation_service.transform_legacy_scenario(self.legacy_scenario_data)
        
        # Should be a valid ScenarioDefinition
        assert isinstance(transformed, ScenarioDefinition)
        assert transformed.name == "Legacy Scenario"
        
        # Check that baseline_input has proper structure
        baseline_dump = transformed.baseline_input.model_dump(by_alias=True)
        assert "global" in baseline_dump
    
    def test_field_name_standardization(self):
        """Test field name standardization"""
        data = {
            "total": 100,
            "Price_1": 1200.0,
            "Price_2": 1300.0,
            "nested": {
                "total": 50,
                "Price_3": 1400.0
            }
        }
        
        self.transformation_service._standardize_field_names(data)
        
        # Check field name changes
        assert "fte" in data
        assert "total" not in data
        assert "price_1" in data
        assert "Price_1" not in data
        assert data["nested"]["fte"] == 50
        assert "price_3" in data["nested"]
    
    def test_deprecated_field_removal(self):
        """Test removal of deprecated fields"""
        data = {
            "name": "Test",
            "progression_rate": 0.5,
            "valid_field": "keep_me",
            "nested": {
                "progression_rate": 0.3,
                "another_valid": "also_keep"
            }
        }
        
        self.transformation_service._remove_deprecated_fields(data)
        
        assert "progression_rate" not in data
        assert "progression_rate" not in data["nested"]
        assert data["valid_field"] == "keep_me"
        assert data["nested"]["another_valid"] == "also_keep"
    
    def test_month_key_generation(self):
        """Test month key generation"""
        month_keys = self.transformation_service.generate_month_keys(2025, 1, 2025, 3)
        
        expected_keys = ["202501", "202502", "202503"]
        assert month_keys == expected_keys
    
    def test_month_key_validation(self):
        """Test month key validation"""
        assert self.transformation_service.validate_month_key("202501")
        assert self.transformation_service.validate_month_key("202512")
        assert not self.transformation_service.validate_month_key("202513")  # Invalid month
        assert not self.transformation_service.validate_month_key("2025-01")  # Wrong format
        assert not self.transformation_service.validate_month_key("20251")  # Too short
    
    def test_month_key_parsing(self):
        """Test month key parsing"""
        parsed = self.transformation_service.parse_month_key("202503")
        assert parsed == {"year": 2025, "month": 3}
        
        invalid_parsed = self.transformation_service.parse_month_key("invalid")
        assert invalid_parsed is None
    
    def test_frontend_to_backend_transformation(self):
        """Test frontend to backend data transformation"""
        frontend_data = {
            "name": "Frontend Scenario",
            "baseline_input": {
                "global": {
                    "recruitment": {
                        "Consultant": {
                            "A": {
                                "202501": "20",  # String value from frontend
                                "202502": 15
                            }
                        }
                    },
                    "churn": {
                        "Consultant": {
                            "A": {
                                "202501": "2",
                                "202502": None  # Null value from frontend
                            }
                        }
                    }
                }
            }
        }
        
        backend_data = self.transformation_service.transform_frontend_to_backend(frontend_data)
        
        # Check that string values are converted to numbers
        consultant_a_recruitment = backend_data["baseline_input"]["global"]["recruitment"]["Consultant"]["A"]
        assert consultant_a_recruitment["202501"] == 20.0
        
        # Check that null values are converted to 0
        consultant_a_churn = backend_data["baseline_input"]["global"]["churn"]["Consultant"]["A"]
        assert consultant_a_churn["202502"] == 0.0
        
        # Check that timestamps are added
        assert "created_at" in backend_data
        assert "updated_at" in backend_data


class TestIntegration:
    """Integration tests for unified data structures"""
    
    def test_complete_scenario_workflow(self):
        """Test complete workflow from legacy data to unified structure"""
        # Start with legacy data
        legacy_data = {
            "name": "Integration Test Scenario",
            "description": "Testing complete workflow",
            "time_range": {
                "start_year": 2025,
                "start_month": 1,
                "end_year": 2026,
                "end_month": 12
            },
            "office_scope": ["Stockholm"],
            "total": 150,  # Legacy field
            "progression_rate": 0.4,  # Deprecated field
            "baseline_input": {
                "recruitment": {  # Missing global wrapper
                    "Consultant": {
                        "A": {"202501": 25, "202502": 20}
                    }
                },
                "churn": {
                    "Consultant": {
                        "A": {"202501": 3, "202502": 2}
                    }
                }
            }
        }
        
        # Transform legacy data
        transformation_service = DataTransformationService()
        unified_scenario = transformation_service.transform_legacy_scenario(legacy_data)
        
        # Validate transformed data
        validation_service = DataValidationService()
        scenario_dict = unified_scenario.model_dump(by_alias=True)
        is_valid, errors = validation_service.validate_complete_scenario(scenario_dict)
        
        assert is_valid, f"Transformed scenario validation failed: {errors}"
        
        # Check that legacy fields are handled correctly
        scenario_dict = unified_scenario.model_dump()
        scenario_json = json.dumps(scenario_dict, default=str)  # Handle datetime serialization
        assert "progression_rate" not in scenario_json
        assert scenario_dict["baseline_input"]["global_data"]["recruitment"] is not None
    
    def test_validation_and_transformation_consistency(self):
        """Test that validation and transformation work consistently together"""
        # Create scenario with known issues - using unified format
        problematic_data = {
            "name": "Problematic Scenario",
            "description": "Has validation issues",
            "time_range": {
                "start_year": 2025,
                "start_month": 1,
                "end_year": 2025,
                "end_month": 6
            },
            "office_scope": ["Stockholm"],
            "baseline_input": {
                "global": {
                    "recruitment": {
                        "Consultant": {
                            "levels": {
                                "A": {
                                    "recruitment": {"values": {"202501": 20, "invalid_key": 10}},  # Invalid month key
                                    "churn": {"values": {"202501": -5}}  # Negative value
                                }
                            }
                        }
                    },
                    "churn": {
                        "Consultant": {
                            "levels": {
                                "A": {
                                    "recruitment": {"values": {"202501": 20, "invalid_key": 10}},  # Invalid month key
                                    "churn": {"values": {"202501": -5}}  # Negative value
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # Validate and expect errors
        validation_service = DataValidationService()
        is_valid, errors = validation_service.validate_complete_scenario(problematic_data)
        
        assert not is_valid
        assert len(errors) > 0
        
        # Generate comprehensive report
        report = validation_service.generate_validation_report(problematic_data)
        assert report["overall_status"] == "invalid"
        assert report["summary"]["total_errors"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])