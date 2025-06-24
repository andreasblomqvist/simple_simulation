"""
Simulation package for SimpleSim.

This package contains the refactored simulation engine components:
- models: Core data structures and enums
- utils: Helper functions and utilities
- workforce: People movement and progression logic (TODO)
- office_manager: Office initialization and management (TODO)
- runner: Core simulation execution (TODO)
- results: Results processing and formatting (TODO)
- engine: Main orchestration class (TODO)
"""

# Import models and utils for now
from .models import Person, RoleData, Level, Office, Month, HalfYear, Journey, OfficeJourney
from .utils import calculate_configuration_checksum, validate_configuration_completeness

__all__ = [
    'Person',
    'RoleData', 
    'Level',
    'Office',
    'Month',
    'HalfYear',
    'Journey',
    'OfficeJourney',
    'calculate_configuration_checksum',
    'validate_configuration_completeness'
] 