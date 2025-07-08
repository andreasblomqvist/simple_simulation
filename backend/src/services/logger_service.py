"""
Structured logger service for backend.
Provides contextual logging with correlation ID support for tracing requests.

Usage:
    from src.services.logger_service import LoggerService
    logger = LoggerService()
    logger.info("Message", correlation_id="abc123", extra={"user_id": 42})

Best Practices:
    1. Always use correlation IDs for request tracing:
       - Generate a unique correlation ID at the start of each request
       - Pass it through all service calls for end-to-end tracing
       - Use short, readable IDs (e.g., first 8 chars of UUID)
    
    2. Include relevant context in extra data:
       - User IDs, request IDs, scenario IDs
       - Performance metrics (execution time, counts)
       - Error codes and status information
    
    3. Use appropriate log levels:
       - DEBUG: Detailed debugging information
       - INFO: General operational messages
       - WARNING: Potential issues that don't stop execution
       - ERROR: Errors that affect functionality
    
    4. Structure your extra data consistently:
       - Use descriptive key names
       - Include both scalar and structured data
       - Avoid sensitive information in logs
    
Example:
    # In a service method
    correlation_id = str(uuid.uuid4())[:8]
    logger.info("Starting operation", correlation_id=correlation_id, extra={
        "user_id": user.id,
        "operation": "scenario_execution",
        "scenario_id": scenario.id
    })
    
    try:
        result = perform_operation()
        logger.info("Operation completed", correlation_id=correlation_id, extra={
            "execution_time": execution_time,
            "result_count": len(result)
        })
    except Exception as e:
        logger.error(f"Operation failed: {e}", correlation_id=correlation_id, extra={
            "error_type": type(e).__name__,
            "execution_time": execution_time
        })
        raise
"""
import logging
import json
from typing import Optional, Dict, Any

class LoggerService:
    def __init__(self, name: str = "simplesim"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def _format_message(self, message: str, correlation_id: Optional[str] = None, extra: Optional[Dict[str, Any]] = None) -> str:
        log_record = {"message": message}
        if correlation_id:
            log_record["correlation_id"] = correlation_id
        if extra:
            log_record.update(extra)
        return json.dumps(log_record, default=str)

    def info(self, message: str, correlation_id: Optional[str] = None, extra: Optional[Dict[str, Any]] = None):
        self.logger.info(self._format_message(message, correlation_id, extra))

    def warning(self, message: str, correlation_id: Optional[str] = None, extra: Optional[Dict[str, Any]] = None):
        self.logger.warning(self._format_message(message, correlation_id, extra))

    def error(self, message: str, correlation_id: Optional[str] = None, extra: Optional[Dict[str, Any]] = None):
        self.logger.error(self._format_message(message, correlation_id, extra))

    def debug(self, message: str, correlation_id: Optional[str] = None, extra: Optional[Dict[str, Any]] = None):
        self.logger.debug(self._format_message(message, correlation_id, extra)) 