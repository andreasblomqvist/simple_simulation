# Logging Guide

## Overview

This document describes the structured logging system implemented in the SimpleSim backend services. The system provides consistent, traceable logging with correlation IDs, structured data, and configurable output formats.

## Architecture

### Logger Service

The `LoggerService` provides a centralized logging interface with correlation ID support:

```python
from backend.src.services.logger_service import LoggerService

class MyService:
    def __init__(self):
        self.logger = LoggerService("my_service")
    
    def process_data(self, data):
        correlation_id = str(uuid.uuid4())[:8]
        self.logger.info("Processing data", correlation_id=correlation_id, extra={"data_size": len(data)})
```

### Log Levels

The system supports standard Python logging levels:

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about program execution
- **WARNING**: Indicate a potential problem
- **ERROR**: A more serious problem
- **CRITICAL**: A critical problem that may prevent the program from running

## Usage Examples

### Basic Logging

```python
from backend.src.services.logger_service import LoggerService

class ScenarioService:
    def __init__(self):
        self.logger = LoggerService("scenario_service")
    
    def run_scenario(self, request):
        correlation_id = str(uuid.uuid4())[:8]
        self.logger.info("Starting scenario execution", correlation_id=correlation_id)
        
        try:
            result = self._execute_scenario(request)
            self.logger.info("Scenario completed successfully", correlation_id=correlation_id)
            return result
        except Exception as e:
            self.logger.error(f"Scenario execution failed: {e}", correlation_id=correlation_id)
            raise
```

### Structured Logging with Context

```python
def validate_scenario(self, scenario_def):
    correlation_id = str(uuid.uuid4())[:8]
    
    self.logger.info(
        "Validating scenario definition",
        correlation_id=correlation_id,
        extra={
            "scenario_name": scenario_def.name,
            "scenario_id": getattr(scenario_def, 'id', None),
            "validation_steps": ["name", "time_range", "office_scope"]
        }
    )
    
    # Validation logic...
    
    self.logger.info(
        "Scenario validation completed",
        correlation_id=correlation_id,
        extra={
            "validation_result": "success",
            "scenario_name": scenario_def.name
        }
    )
```

### Performance Logging

```python
import time

def expensive_operation(self, data):
    correlation_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    self.logger.info(
        "Starting expensive operation",
        correlation_id=correlation_id,
        extra={"data_size": len(data)}
    )
    
    try:
        result = self._perform_operation(data)
        execution_time = time.time() - start_time
        
        self.logger.info(
            "Operation completed successfully",
            correlation_id=correlation_id,
            extra={
                "execution_time_seconds": round(execution_time, 3),
                "result_size": len(result)
            }
        )
        
        return result
    except Exception as e:
        execution_time = time.time() - start_time
        self.logger.error(
            f"Operation failed after {execution_time:.3f}s: {e}",
            correlation_id=correlation_id,
            extra={"execution_time_seconds": round(execution_time, 3)}
        )
        raise
```

## Correlation ID Best Practices

### 1. Generate Correlation IDs at Entry Points

```python
# In API endpoints or main service methods
def run_scenario(self, request: ScenarioRequest) -> ScenarioResponse:
    correlation_id = str(uuid.uuid4())[:8]  # Generate at entry point
    self.logger.info("Scenario request received", correlation_id=correlation_id)
    
    # Pass correlation_id to all subsequent method calls
    scenario_def = self._load_scenario_definition(request, correlation_id)
    results = self._execute_simulation(scenario_def, correlation_id)
    
    return self._create_response(results, correlation_id)
```

### 2. Pass Correlation IDs Through Method Chains

```python
def _load_scenario_definition(self, request, correlation_id):
    self.logger.info("Loading scenario definition", correlation_id=correlation_id)
    
    # Pass correlation_id to nested calls
    scenario = self.storage_service.get_scenario(
        request.scenario_id, 
        correlation_id=correlation_id
    )
    
    return scenario

def _execute_simulation(self, scenario_def, correlation_id):
    self.logger.info("Executing simulation", correlation_id=correlation_id)
    
    # Pass correlation_id to engine
    results = self.simulation_engine.run(
        scenario_def, 
        correlation_id=correlation_id
    )
    
    return results
```

### 3. Use Correlation IDs in Error Handling

```python
@handle_service_errors
def process_data(self, data, correlation_id=None):
    try:
        self.logger.info("Processing data", correlation_id=correlation_id)
        result = self._transform_data(data)
        self.logger.info("Data processing completed", correlation_id=correlation_id)
        return result
    except Exception as e:
        self.logger.error(
            f"Data processing failed: {e}", 
            correlation_id=correlation_id,
            extra={"data_type": type(data).__name__}
        )
        raise
```

### 4. Include Correlation IDs in External Service Calls

```python
def call_external_api(self, data, correlation_id):
    self.logger.info(
        "Calling external API",
        correlation_id=correlation_id,
        extra={"api_endpoint": "/api/data", "data_size": len(data)}
    )
    
    # Include correlation ID in headers
    headers = {
        "X-Correlation-ID": correlation_id,
        "Content-Type": "application/json"
    }
    
    response = requests.post("/api/data", json=data, headers=headers)
    
    self.logger.info(
        "External API call completed",
        correlation_id=correlation_id,
        extra={"status_code": response.status_code}
    )
    
    return response
```

## Log Format and Structure

### Standard Log Format

```
2025-07-07 15:30:00,123 [INFO] simplesim: ScenarioService.run_scenario [corr:abc12345]: 
Starting scenario execution
Extra: {'scenario_name': 'Growth Scenario', 'user_id': 'user123'}
```

### JSON Log Format (Development)

```json
{
  "timestamp": "2025-07-07T15:30:00.123Z",
  "level": "INFO",
  "logger": "simplesim",
  "message": "Starting scenario execution",
  "correlation_id": "abc12345",
  "service": "scenario_service",
  "method": "run_scenario",
  "extra": {
    "scenario_name": "Growth Scenario",
    "user_id": "user123"
  }
}
```

## Configuration

### Environment Variables

```bash
# Log level
SIMPLE_SIM_LOG_LEVEL=INFO

# Log format (text|json)
SIMPLE_SIM_LOG_FORMAT=text

# Include correlation IDs
SIMPLE_SIM_INCLUDE_CORRELATION_ID=true

# Log file path
SIMPLE_SIM_LOG_FILE=logs/backend.log

# Enable console output
SIMPLE_SIM_CONSOLE_LOGGING=true
```

### Logger Service Configuration

```python
from backend.src.services.logger_service import LoggerService

# Configure with custom settings
logger = LoggerService(
    service_name="my_service",
    log_level="DEBUG",
    include_correlation_id=True,
    log_format="json"
)
```

## Log Analysis and Monitoring

### Correlation ID Tracking

To track a request through the system:

```bash
# Search for all logs with a specific correlation ID
grep "corr:abc12345" logs/backend.log

# Search for correlation ID in JSON logs
grep '"correlation_id": "abc12345"' logs/backend.log
```

### Performance Analysis

```bash
# Find slow operations
grep "execution_time_seconds" logs/backend.log | grep -E "([0-9]+\.[0-9]{3})" | sort -k2 -n

# Find errors by correlation ID
grep "ERROR.*corr:" logs/backend.log
```

### Log Aggregation

For production environments, consider using log aggregation tools:

- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Fluentd** for log collection
- **CloudWatch** (AWS) or **Stackdriver** (GCP)

## Testing with Logging

### Unit Test Example

```python
import pytest
from unittest.mock import patch
from backend.src.services.logger_service import LoggerService

class TestMyService:
    def test_logging_with_correlation_id(self):
        with patch('backend.src.services.logger_service.LoggerService') as mock_logger:
            service = MyService()
            service.process_data({"test": "data"})
            
            # Verify logging calls
            mock_logger.return_value.info.assert_called()
            mock_logger.return_value.error.assert_not_called()
    
    def test_error_logging(self):
        with patch('backend.src.services.logger_service.LoggerService') as mock_logger:
            service = MyService()
            
            with pytest.raises(ValueError):
                service.process_data(None)
            
            # Verify error was logged
            mock_logger.return_value.error.assert_called_once()
```

### Integration Test Example

```python
def test_correlation_id_propagation(self):
    """Test that correlation IDs are properly propagated through the system."""
    service = ScenarioService()
    
    # Capture logs
    with self.assertLogs('simplesim', level='INFO') as captured:
        service.run_scenario(request)
    
    # Extract correlation IDs from logs
    correlation_ids = set()
    for record in captured.records:
        if hasattr(record, 'correlation_id'):
            correlation_ids.add(record.correlation_id)
    
    # All logs should have the same correlation ID
    assert len(correlation_ids) == 1
```

## Best Practices

### 1. Use Descriptive Log Messages

```python
# Good: Clear, actionable message
self.logger.info("Scenario validation started", correlation_id=correlation_id)

# Avoid: Vague messages
self.logger.info("Processing", correlation_id=correlation_id)
```

### 2. Include Relevant Context

```python
# Good: Include relevant data
self.logger.info(
    "User authentication successful",
    correlation_id=correlation_id,
    extra={
        "user_id": user.id,
        "auth_method": "jwt",
        "session_duration": "24h"
    }
)

# Avoid: Too much or irrelevant data
self.logger.info(
    "User authentication successful",
    correlation_id=correlation_id,
    extra={"user": user.__dict__}  # Too much data
)
```

### 3. Use Appropriate Log Levels

```python
# DEBUG: Detailed debugging information
self.logger.debug("Parsing configuration file", correlation_id=correlation_id)

# INFO: General information
self.logger.info("Configuration loaded successfully", correlation_id=correlation_id)

# WARNING: Potential issues
self.logger.warning("Using default configuration values", correlation_id=correlation_id)

# ERROR: Actual errors
self.logger.error("Failed to load configuration", correlation_id=correlation_id)

# CRITICAL: System-breaking errors
self.logger.critical("Database connection lost", correlation_id=correlation_id)
```

### 4. Avoid Sensitive Data in Logs

```python
# Good: Log metadata, not sensitive data
self.logger.info(
    "User login attempt",
    correlation_id=correlation_id,
    extra={
        "user_id": user.id,
        "login_method": "password",
        "ip_address": "192.168.1.1"
    }
)

# Avoid: Logging sensitive data
self.logger.info(
    "User login attempt",
    correlation_id=correlation_id,
    extra={
        "password": "secret123",  # Never log passwords!
        "ssn": "123-45-6789"      # Never log PII!
    }
)
```

### 5. Use Structured Data

```python
# Good: Use structured extra data
self.logger.info(
    "API request processed",
    correlation_id=correlation_id,
    extra={
        "endpoint": "/api/scenarios",
        "method": "POST",
        "status_code": 200,
        "response_time_ms": 150
    }
)

# Avoid: String concatenation
self.logger.info(f"API request to /api/scenarios returned 200 in 150ms", correlation_id=correlation_id)
```

## Troubleshooting

### Common Issues

1. **Missing correlation IDs**
   - Ensure correlation IDs are generated at entry points
   - Pass correlation IDs through all method calls
   - Check that LoggerService is properly initialized

2. **Log level too verbose**
   - Set appropriate log level for environment
   - Use DEBUG only in development
   - Use INFO or WARNING in production

3. **Performance impact**
   - Avoid expensive operations in log statements
   - Use lazy evaluation for complex data
   - Consider log sampling for high-volume operations

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging
logging.getLogger('simplesim').setLevel(logging.DEBUG)
```

## Migration Guide

### From Basic Logging

**Before:**
```python
import logging

logger = logging.getLogger(__name__)

def process_data(self, data):
    logger.info("Processing data")
    # Process data...
    logger.info("Data processed")
```

**After:**
```python
from backend.src.services.logger_service import LoggerService

class MyService:
    def __init__(self):
        self.logger = LoggerService("my_service")
    
    def process_data(self, data):
        correlation_id = str(uuid.uuid4())[:8]
        self.logger.info("Processing data", correlation_id=correlation_id)
        # Process data...
        self.logger.info("Data processed", correlation_id=correlation_id)
```

## Related Documentation

- [Error Handling Guide](ERROR_HANDLING_GUIDE.md) - Error handling system
- [Architecture Documentation](ARCHITECTURE.md) - Overall system architecture
- [Testing Guide](TESTING_GUIDE.md) - Testing best practices 