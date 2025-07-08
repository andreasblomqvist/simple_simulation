"""
Error handling infrastructure for service layer.

Defines custom error classes and decorators for consistent error handling.

Usage:
    from src.services.error_handler import handle_service_errors, ValidationError

    @handle_service_errors
    def my_service_method(...):
        ...
        if not valid:
            raise ValidationError("Invalid input!")
        ...

    # All exceptions will be logged and wrapped as ScenarioServiceError if not explicitly handled.
"""

import logging
from functools import wraps

logger = logging.getLogger(__name__)

class ScenarioServiceError(Exception):
    """Base exception for scenario service errors."""
    pass

class ValidationError(ScenarioServiceError):
    """Exception for validation errors."""
    pass

class SimulationEngineError(ScenarioServiceError):
    """Exception for simulation engine errors."""
    pass

class StorageError(ScenarioServiceError):
    """Exception for storage-related errors."""
    pass

# Decorator for consistent error handling

def handle_service_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as ve:
            logger.error(f"Validation error: {ve}")
            raise
        except SimulationEngineError as se:
            logger.error(f"Simulation engine error: {se}")
            raise
        except StorageError as ste:
            logger.error(f"Storage error: {ste}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise ScenarioServiceError(f"Unexpected error: {e}") from e
    return wrapper 