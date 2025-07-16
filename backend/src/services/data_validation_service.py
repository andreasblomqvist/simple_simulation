"""
Data Validation Service for Unified Data Structures

Provides comprehensive validation for nested baseline_input structures
and ensures data integrity across all system components.
"""

from typing import Dict, List, Any, Optional, Tuple, Union
from pydantic import ValidationError
import logging
from datetime import datetime

from .unified_data_models import (
    ScenarioDefinition,
    BaselineInput,
    MonthlyValues,
    RoleData,
    LevelData,
    validate_scenario_definition,
    validate_baseline_input_structure
)

logger = logging.getLogger(__name__)


class DataValidationError(Exception):
    """Custom exception for data validation errors"""
    def __init__(self, message: str, errors: List[str] = None):
        super().__init__(message)
        self.errors = errors or []


class DataValidationService:
    """Service for validating unified data structures"""
    
    def __init__(self):
        self.validation_errors = []
    
    def clear_errors(self):
        """Clear accumulated validation errors"""
        self.validation_errors = []
    
    def add_error(self, error: str):
        """Add a validation error"""
        self.validation_errors.append(error)
        logger.warning(f"Validation error: {error}")
    
    def validate_complete_scenario(self, scenario_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a complete scenario definition including all nested structures.
        Returns (is_valid, list_of_errors)
        """
        self.clear_errors()
        
        try:
            # Validate using unified models - this is the primary validation
            scenario_def = validate_scenario_definition(scenario_data)
            logger.info("Scenario definition validation passed")
            
            # Only additional scenario-level consistency checks
            self._validate_scenario_consistency(scenario_data)
            
        except ValidationError as e:
            # Parse Pydantic validation errors for clearer messages
            for error in e.errors():
                field_path = '.'.join(str(x) for x in error['loc'])
                error_msg = error['msg']
                self.add_error(f"{field_path}: {error_msg}")
        except Exception as e:
            self.add_error(f"Unexpected validation error: {e}")
        
        is_valid = len(self.validation_errors) == 0
        return is_valid, self.validation_errors.copy()
    
    def validate_baseline_input(self, baseline_input: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate baseline input structure specifically.
        Returns (is_valid, list_of_errors)
        """
        self.clear_errors()
        
        try:
            # Validate using unified models - this is the primary validation
            validated_input = validate_baseline_input_structure(baseline_input)
            logger.info("Baseline input validation passed")
            
        except ValidationError as e:
            # Parse Pydantic validation errors for clearer messages
            for error in e.errors():
                field_path = '.'.join(str(x) for x in error['loc'])
                error_msg = error['msg']
                self.add_error(f"baseline_input.{field_path}: {error_msg}")
        except Exception as e:
            self.add_error(f"Unexpected baseline input error: {e}")
        
        is_valid = len(self.validation_errors) == 0
        return is_valid, self.validation_errors.copy()
    
    def _validate_scenario_consistency(self, scenario_data: Dict[str, Any]):
        """Validate internal consistency of scenario data"""
        
        # Check time range consistency
        time_range = scenario_data.get('time_range', {})
        if time_range:
            start_year = time_range.get('start_year')
            end_year = time_range.get('end_year')
            start_month = time_range.get('start_month')
            end_month = time_range.get('end_month')
            
            if start_year and end_year and start_year == end_year:
                if start_month and end_month and start_month > end_month:
                    self.add_error("Start month cannot be after end month in the same year")
        
        # Validate office scope
        office_scope = scenario_data.get('office_scope', [])
        if not office_scope:
            self.add_error("Office scope cannot be empty")
        
        # Validate levers structure
        levers = scenario_data.get('levers', {})
        if levers:
            for lever_type, values in levers.items():
                if lever_type not in ['recruitment', 'churn', 'progression']:
                    self.add_error(f"Unknown lever type: {lever_type}")
                
                if isinstance(values, dict):
                    for level, multiplier in values.items():
                        if not isinstance(multiplier, (int, float)) or multiplier < 0:
                            self.add_error(f"Invalid multiplier for {lever_type}.{level}: {multiplier}")
    
    def _validate_baseline_input_completeness(self, baseline_input: Dict[str, Any]):
        """Validate completeness and consistency of baseline input"""
        
        global_data = baseline_input.get('global', {})
        if not global_data:
            self.add_error("Baseline input must contain 'global' data")
            return
        
        # Check required sections
        required_sections = ['recruitment', 'churn']
        for section in required_sections:
            if section not in global_data:
                self.add_error(f"Global data must contain '{section}' section")
        
        # Validate recruitment and churn data structure
        for section_name in ['recruitment', 'churn']:
            section_data = global_data.get(section_name, {})
            if section_data:
                self._validate_section_structure(section_name, section_data)
    
    def _validate_section_structure(self, section_name: str, section_data: Dict[str, Any]):
        """Validate the structure of recruitment or churn section"""
        
        for role_name, role_data in section_data.items():
            if not isinstance(role_data, dict):
                self.add_error(f"{section_name}.{role_name} must be a dictionary")
                continue
            
            # Check if this is a leveled role or flat role
            is_leveled_role = self._is_leveled_role_data(role_data)
            
            if is_leveled_role:
                # Validate leveled role structure
                for level_name, level_data in role_data.items():
                    if not isinstance(level_data, dict):
                        self.add_error(f"{section_name}.{role_name}.{level_name} must be a dictionary")
                        continue
                    
                    self._validate_monthly_values(f"{section_name}.{role_name}.{level_name}", level_data)
            else:
                # Validate flat role structure
                self._validate_monthly_values(f"{section_name}.{role_name}", role_data)
    
    def _is_leveled_role_data(self, role_data: Dict[str, Any]) -> bool:
        """
        Determine if role data represents a leveled role.
        Leveled roles have level names as keys (A, AC, C, etc.)
        Flat roles have YYYYMM format keys directly.
        """
        if not role_data:
            return False
        
        # Check if all keys look like month keys (YYYYMM format)
        keys = list(role_data.keys())
        month_keys = [k for k in keys if len(k) == 6 and k.isdigit()]
        
        # If most keys are month keys, it's a flat role
        if len(month_keys) > len(keys) * 0.5:
            return False
        
        # Otherwise, assume it's a leveled role
        return True
    
    def _validate_monthly_values(self, context: str, monthly_data: Dict[str, Any]):
        """Validate monthly values structure and format"""
        
        for month_key, value in monthly_data.items():
            # Validate month key format (YYYYMM)
            if not (len(month_key) == 6 and month_key.isdigit()):
                self.add_error(f"{context}: Invalid month key format '{month_key}' (should be YYYYMM)")
                continue
            
            # Extract year and month
            try:
                year = int(month_key[:4])
                month = int(month_key[4:6])
                
                # Validate year range
                if not (2020 <= year <= 2040):
                    self.add_error(f"{context}: Year {year} out of valid range (2020-2040)")
                
                # Validate month range
                if not (1 <= month <= 12):
                    self.add_error(f"{context}: Month {month} out of valid range (1-12)")
                
            except ValueError:
                self.add_error(f"{context}: Invalid month key '{month_key}'")
                continue
            
            # Validate value
            if not isinstance(value, (int, float)):
                self.add_error(f"{context}: Value for {month_key} must be numeric, got {type(value)}")
            elif value < 0:
                self.add_error(f"{context}: Value for {month_key} cannot be negative: {value}")
    
    def validate_field_names(self, data: Dict[str, Any], context: str = "root") -> List[str]:
        """
        Validate that data uses standardized field names (fte vs total, etc.)
        Returns list of field name issues found.
        """
        issues = []
        
        if isinstance(data, dict):
            # Check for deprecated field names
            deprecated_fields = {
                'total': 'fte',
                'progression_rate': 'REMOVE_FIELD',
                'Price_1': 'price_1',
                'Price_2': 'price_2',
                # Add more mappings as needed
            }
            
            for deprecated, replacement in deprecated_fields.items():
                if deprecated in data:
                    if replacement == 'REMOVE_FIELD':
                        issues.append(f"{context}: Found deprecated field '{deprecated}' - should be removed")
                    else:
                        issues.append(f"{context}: Found deprecated field '{deprecated}' - should be '{replacement}'")
            
            # Recursively check nested structures
            for key, value in data.items():
                nested_issues = self.validate_field_names(value, f"{context}.{key}")
                issues.extend(nested_issues)
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                nested_issues = self.validate_field_names(item, f"{context}[{i}]")
                issues.extend(nested_issues)
        
        return issues
    
    def generate_validation_report(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive validation report for scenario data.
        Returns detailed report with all validation results.
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'unknown',
            'scenario_validation': {},
            'baseline_input_validation': {},
            'field_name_validation': {},
            'summary': {
                'total_errors': 0,
                'total_warnings': 0,
                'critical_issues': [],
                'recommendations': []
            }
        }
        
        # Validate complete scenario
        is_valid, errors = self.validate_complete_scenario(scenario_data)
        report['scenario_validation'] = {
            'is_valid': is_valid,
            'errors': errors
        }
        
        # Validate baseline input specifically
        baseline_input = scenario_data.get('baseline_input', {})
        if baseline_input:
            is_valid_baseline, baseline_errors = self.validate_baseline_input(baseline_input)
            report['baseline_input_validation'] = {
                'is_valid': is_valid_baseline,
                'errors': baseline_errors
            }
        
        # Validate field names
        field_issues = self.validate_field_names(scenario_data)
        report['field_name_validation'] = {
            'issues_found': len(field_issues),
            'issues': field_issues
        }
        
        # Generate summary
        total_errors = len(errors) + len(baseline_errors if baseline_input else [])
        total_warnings = len(field_issues)
        
        report['summary'] = {
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'critical_issues': errors[:5],  # Top 5 critical issues
            'recommendations': self._generate_recommendations(errors, field_issues)
        }
        
        # Determine overall status
        if total_errors == 0 and total_warnings == 0:
            report['overall_status'] = 'valid'
        elif total_errors == 0:
            report['overall_status'] = 'valid_with_warnings'
        else:
            report['overall_status'] = 'invalid'
        
        return report
    
    def _generate_recommendations(self, errors: List[str], field_issues: List[str]) -> List[str]:
        """Generate actionable recommendations based on validation results"""
        recommendations = []
        
        if any('progression_rate' in error for error in errors + field_issues):
            recommendations.append("Remove all 'progression_rate' fields from scenario definitions")
        
        if any('total' in error for error in field_issues):
            recommendations.append("Replace 'total' property with 'fte' for standardized field naming")
        
        if any('Price_' in error for error in field_issues):
            recommendations.append("Convert 'Price_X' fields to lowercase 'price_X' format")
        
        if any('month key' in error for error in errors):
            recommendations.append("Ensure all month keys use YYYYMM format (e.g., '202501' for Jan 2025)")
        
        if any('baseline input' in error.lower() for error in errors):
            recommendations.append("Review baseline input structure to match documented format")
        
        return recommendations


# Convenience functions for external use

def validate_scenario_data(scenario_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Convenience function to validate scenario data"""
    service = DataValidationService()
    return service.validate_complete_scenario(scenario_data)


def validate_baseline_data(baseline_input: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Convenience function to validate baseline input data"""
    service = DataValidationService()
    return service.validate_baseline_input(baseline_input)


def generate_validation_report(scenario_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to generate validation report"""
    service = DataValidationService()
    return service.generate_validation_report(scenario_data)