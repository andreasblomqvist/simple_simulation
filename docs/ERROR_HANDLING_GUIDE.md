# Error Handling Guide

## Overview

This document describes the error handling infrastructure implemented in the SimpleSim backend services. The system provides consistent error handling across all services with proper logging, error categorization, and user-friendly error messages.

## Architecture

### Error Classes

The error handling system uses a hierarchy of custom exception classes:

```python
# Base error class
class SimpleSimError(Exception):
    """Base exception for all SimpleSim errors."""
    
# Service-specific errors
class ScenarioServiceError(SimpleSimError):
    """Raised when scenario service operations fail."""
    
class ValidationError(SimpleSimError):
    """Raised when data validation fails."""
    
class ConfigurationError(SimpleSimError):
    """Raised when configuration operations fail."""
    
class SimulationError(SimpleSimError):
    """Raised when simulation engine operations fail."""
```

### Error Handler Decorator

The `@handle_service_errors` decorator provides automatic error handling for service methods:

```python
from backend.src.services.error_handler import handle_service_errors

@handle_service_errors
def my_service_method(self, param1, param2):
    # Your service logic here
    pass
```

## Usage Examples

### Basic Service Method

```python
from backend.src.services.error_handler import handle_service_errors, ScenarioServiceError

class MyService:
    @handle_service_errors
    def process_data(self, data: dict) -> dict:
        if not data:
            raise ScenarioServiceError("Data cannot be empty")
        
        # Process data...
        return processed_data
```

### Service Method with Custom Error Context

```python
from backend.src.services.error_handler import handle_service_errors, ValidationError

class ScenarioValidator:
    @handle_service_errors
    def validate_scenario_definition(self, scenario_def: ScenarioDefinition) -> None:
        if not scenario_def.name:
            raise ValidationError(
                "Scenario name is required",
                context={"field": "name", "scenario_id": getattr(scenario_def, 'id', None)}
            )
        
        if not scenario_def.time_range:
            raise ValidationError(
                "Time range is required",
                context={"field": "time_range", "scenario_name": scenario_def.name}
            )
```

### Nested Service Calls

```python
class ScenarioService:
    @handle_service_errors
    def run_scenario(self, request: ScenarioRequest) -> ScenarioResponse:
        # This method can call other decorated methods
        scenario_def = self._load_scenario_definition(request)
        validated_data = self._validate_scenario(scenario_def)
        results = self._execute_simulation(scenario_def, validated_data)
        return self._create_response(results)
    
    @handle_service_errors
    def _load_scenario_definition(self, request: ScenarioRequest) -> ScenarioDefinition:
        # Nested error handling works correctly
        pass
```

## Error Handling Best Practices

### 1. Use Specific Error Types

```python
# Good: Specific error type
if not data:
    raise ValidationError("Data is required")

# Avoid: Generic exceptions
if not data:
    raise Exception("Data is required")
```

### 2. Provide Context in Errors

```python
# Good: Include context for debugging
raise ScenarioServiceError(
    "Failed to load scenario",
    context={
        "scenario_id": scenario_id,
        "user_id": user_id,
        "operation": "load"
    }
)
```

### 3. Use Descriptive Error Messages

```python
# Good: Clear, actionable message
raise ValidationError("Scenario name must be between 3 and 50 characters")

# Avoid: Vague messages
raise ValidationError("Invalid input")
```

### 4. Handle Expected Errors Gracefully

```python
@handle_service_errors
def get_scenario(self, scenario_id: str) -> Optional[ScenarioDefinition]:
    try:
        return self.storage_service.get_scenario(scenario_id)
    except FileNotFoundError:
        # This is expected behavior, not an error
        return None
    except Exception as e:
        # Unexpected errors are re-raised and handled by decorator
        raise
```

## Integration with Logging

The error handler automatically integrates with the structured logging system:

```python
@handle_service_errors
def my_method(self, param):
    # If an error occurs, it will be logged with:
    # - Error type and message
    # - Stack trace
    # - Method name and parameters
    # - Correlation ID (if available)
    pass
```

### Log Output Example

```
2025-07-07 15:30:00,123 [ERROR] simplesim: ScenarioServiceError in ScenarioService.run_scenario: 
Failed to validate scenario data
Context: {'scenario_id': 'abc123', 'operation': 'validation'}
Traceback (most recent call last):
  File "scenario_service.py", line 45, in run_scenario
    self._validate_scenario(scenario_def)
  File "scenario_service.py", line 167, in validate_scenario
    raise ValidationError("Invalid time range")
```

## Testing Error Handling

### Unit Test Example

```python
import pytest
from backend.src.services.error_handler import ValidationError, ScenarioServiceError

class TestMyService:
    def test_validation_error_handling(self):
        service = MyService()
        
        with pytest.raises(ValidationError) as exc_info:
            service.process_data({})
        
        assert "Data cannot be empty" in str(exc_info.value)
    
    def test_service_error_handling(self):
        service = MyService()
        
        with pytest.raises(ScenarioServiceError) as exc_info:
            service.process_data(None)
        
        assert "Invalid input" in str(exc_info.value)
```

### Mock Testing

```python
from unittest.mock import Mock, patch

class TestScenarioService:
    def test_error_propagation(self):
        with patch('backend.src.services.scenario_validator.ScenarioValidator') as mock_validator:
            mock_validator.return_value.validate_scenario_definition.side_effect = ValidationError("Test error")
            
            service = ScenarioService()
            
            with pytest.raises(ValidationError):
                service.run_scenario(request)
```

## Error Recovery Strategies

### 1. Retry Logic

```python
from backend.src.services.error_handler import handle_service_errors, SimulationError
import time

class SimulationService:
    @handle_service_errors
    def run_simulation_with_retry(self, config, max_retries=3):
        for attempt in range(max_retries):
            try:
                return self._run_simulation(config)
            except SimulationError as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
```

### 2. Fallback Behavior

```python
@handle_service_errors
def get_scenario_with_fallback(self, scenario_id: str) -> ScenarioDefinition:
    try:
        return self.storage_service.get_scenario(scenario_id)
    except FileNotFoundError:
        # Fallback to default scenario
        return self._create_default_scenario()
```

## Configuration

### Error Handler Configuration

The error handler can be configured through environment variables:

```bash
# Enable/disable error handling
SIMPLE_SIM_ERROR_HANDLING=true

# Log level for errors
SIMPLE_SIM_ERROR_LOG_LEVEL=ERROR

# Include stack traces in logs
SIMPLE_SIM_INCLUDE_STACK_TRACE=true
```

## Migration Guide

### From Manual Error Handling

**Before:**
```python
def old_method(self, data):
    try:
        # Process data
        return result
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        raise
```

**After:**
```python
@handle_service_errors
def new_method(self, data):
    # Process data
    return result
```

### From Generic Exceptions

**Before:**
```python
if not data:
    raise Exception("Invalid data")
```

**After:**
```python
if not data:
    raise ValidationError("Data is required")
```

## Troubleshooting

### Common Issues

1. **Error not being caught by decorator**
   - Ensure the method is decorated with `@handle_service_errors`
   - Check that the error inherits from `SimpleSimError`

2. **Missing error context**
   - Add context parameter when raising errors
   - Use structured logging for additional context

3. **Error messages not user-friendly**
   - Override `__str__` method in custom error classes
   - Use descriptive, actionable error messages

### Debug Mode

Enable debug mode for detailed error information:

```python
import logging
logging.getLogger('simplesim').setLevel(logging.DEBUG)
```

## Best Practices Summary

1. **Always use `@handle_service_errors`** for service methods
2. **Use specific error types** instead of generic exceptions
3. **Provide context** in error messages for debugging
4. **Write descriptive error messages** that help users understand the issue
5. **Test error scenarios** in unit tests
6. **Use structured logging** for error tracking
7. **Implement retry logic** for transient failures
8. **Provide fallback behavior** when possible

## Related Documentation

- [Logging Guide](LOGGING_GUIDE.md) - Structured logging system
- [Architecture Documentation](ARCHITECTURE.md) - Overall system architecture
- [Testing Guide](TESTING_GUIDE.md) - Testing best practices 