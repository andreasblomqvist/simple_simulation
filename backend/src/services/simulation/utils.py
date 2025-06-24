"""
Utility functions for the simulation engine.

This module contains helper functions that support the simulation:
- Configuration validation
- Checksum calculation
- Monthly attribute helpers
"""

from typing import Dict, Any
from datetime import datetime
import json
import hashlib
from copy import deepcopy

from .models import Office, Month


def calculate_configuration_checksum(offices: Dict[str, Office]) -> str:
    """
    Calculates a checksum for the initial office configuration to detect changes.
    This helps in deciding whether to re-run a baseline simulation.
    """
    # Create a deep copy to avoid modifying the original data
    offices_copy = deepcopy(offices)

    # Convert the configuration to a JSON string for hashing
    # Using a custom serializer to handle dataclasses
    def json_default(o):
        if hasattr(o, '__dict__'):
            return o.__dict__
        if isinstance(o, (datetime,)):
            return o.isoformat()
        if isinstance(o, type) and hasattr(o, '__name__') and o.__name__ in ['Month', 'HalfYear', 'Journey', 'OfficeJourney']:
            return o.__name__
        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

    config_string = json.dumps(
        {name: office for name, office in offices_copy.items()}, 
        sort_keys=True, 
        default=json_default
    )

    return hashlib.md5(config_string.encode('utf-8')).hexdigest()


def validate_configuration_completeness(offices: Dict[str, Office]) -> Dict[str, Any]:
    """
    Validates that the configuration for all offices, roles, and levels is complete.
    Checks for missing rates, salaries, prices, etc. for all 12 months.
    """
    issues = {}
    
    for office_name, office in offices.items():
        office_issues = {}
        for role_name, role_data in office.roles.items():
            role_issues = {}
            if isinstance(role_data, dict): # Leveled roles
                for level_name, level in role_data.items():
                    level_issues = []
                    for i in range(1, 13):
                        for key in ['progression', 'recruitment', 'churn', 'price', 'salary', 'utr']:
                            if not hasattr(level, f'{key}_{i}'):
                                level_issues.append(f"Missing '{key}' for month {i}")
                    if level_issues:
                        role_issues[level_name] = level_issues
            else: # Flat roles
                flat_role_issues = []
                for i in range(1, 13):
                    for key in ['recruitment', 'churn']:
                        if not hasattr(role_data, f'{key}_{i}'):
                            flat_role_issues.append(f"Missing '{key}' for month {i}")
                if flat_role_issues:
                    role_issues['base'] = flat_role_issues
            
            if role_issues:
                office_issues[role_name] = role_issues
        
        if office_issues:
            issues[office_name] = office_issues
            
    return {
        'is_complete': not issues,
        'issues': issues
    }


def get_monthly_attribute(obj, attribute_base: str, month: Month) -> float:
    """Gets a monthly attribute from an object (e.g., price_1, churn_5)"""
    return getattr(obj, f"{attribute_base}_{month.value}", 0.0)


def set_monthly_attribute(obj, attribute_base: str, month: Month, value: float) -> None:
    """Sets a monthly attribute on an object"""
    setattr(obj, f"{attribute_base}_{month.value}", value)


def get_next_level_name(current_level: str, level_order: list) -> str:
    """Get the name of the next level in the progression path"""
    try:
        current_index = level_order.index(current_level)
        if current_index + 1 < len(level_order):
            return level_order[current_index + 1]
        return None
    except ValueError:
        return None


def determine_level_order(config_data: list) -> list:
    """Dynamically determine the level order from configuration."""
    levels = set()
    for office_config in config_data:
        for role_name, role_data in office_config.get('roles', {}).items():
            if role_name != 'Operations':
                levels.update(role_data.keys())
    
    # Use a standard, sorted progression path
    standard_order = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']
    
    # Filter and sort found levels according to the standard order
    sorted_levels = [level for level in standard_order if level in levels]
    
    return sorted_levels


def get_journey_for_level(level_name: str) -> str:
    """Get the Journey enum for a given level name."""
    from backend.config.default_config import JOURNEY_CLASSIFICATION
    
    for journey, levels in JOURNEY_CLASSIFICATION.items():
        if level_name in levels:
            return journey
    return "Journey 1"  # Default 