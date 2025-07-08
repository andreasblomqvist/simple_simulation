"""
Unit tests for error_handler.py error handling infrastructure.
"""
import pytest
from src.services.error_handler import (
    handle_service_errors,
    ScenarioServiceError,
    ValidationError,
    SimulationEngineError,
    StorageError
)

# Dummy service functions for testing

@handle_service_errors
def raise_validation_error():
    raise ValidationError("Validation failed!")

@handle_service_errors
def raise_simulation_engine_error():
    raise SimulationEngineError("Engine failed!")

@handle_service_errors
def raise_storage_error():
    raise StorageError("Storage failed!")

@handle_service_errors
def raise_unexpected_error():
    raise RuntimeError("Unexpected!")

def test_validation_error_handling():
    with pytest.raises(ValidationError, match="Validation failed!"):
        raise_validation_error()

def test_simulation_engine_error_handling():
    with pytest.raises(SimulationEngineError, match="Engine failed!"):
        raise_simulation_engine_error()

def test_storage_error_handling():
    with pytest.raises(StorageError, match="Storage failed!"):
        raise_storage_error()

def test_unexpected_error_handling():
    with pytest.raises(ScenarioServiceError, match="Unexpected error: Unexpected!"):
        raise_unexpected_error() 