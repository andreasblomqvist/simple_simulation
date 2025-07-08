"""
Unit tests for logger_service.py structured logging functionality.
"""
import json
import pytest
from unittest.mock import patch, MagicMock
from src.services.logger_service import LoggerService

class TestLoggerService:
    """Test the structured logger service functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.logger_service = LoggerService("test_logger")
    
    def test_logger_initialization(self):
        """Test that logger is properly initialized."""
        assert self.logger_service.logger is not None
        assert self.logger_service.logger.name == "test_logger"
    
    def test_format_message_with_correlation_id(self):
        """Test message formatting with correlation ID."""
        message = "Test message"
        correlation_id = "abc123"
        
        formatted = self.logger_service._format_message(message, correlation_id)
        parsed = json.loads(formatted)
        
        assert parsed["message"] == message
        assert parsed["correlation_id"] == correlation_id
    
    def test_format_message_with_extra_data(self):
        """Test message formatting with extra data."""
        message = "Test message"
        extra = {"user_id": 42, "action": "test"}
        
        formatted = self.logger_service._format_message(message, extra=extra)
        parsed = json.loads(formatted)
        
        assert parsed["message"] == message
        assert parsed["user_id"] == 42
        assert parsed["action"] == "test"
    
    def test_format_message_with_correlation_id_and_extra(self):
        """Test message formatting with both correlation ID and extra data."""
        message = "Test message"
        correlation_id = "abc123"
        extra = {"user_id": 42, "action": "test"}
        
        formatted = self.logger_service._format_message(message, correlation_id, extra)
        parsed = json.loads(formatted)
        
        assert parsed["message"] == message
        assert parsed["correlation_id"] == correlation_id
        assert parsed["user_id"] == 42
        assert parsed["action"] == "test"
    
    def test_format_message_without_optional_params(self):
        """Test message formatting without optional parameters."""
        message = "Test message"
        
        formatted = self.logger_service._format_message(message)
        parsed = json.loads(formatted)
        
        assert parsed["message"] == message
        assert "correlation_id" not in parsed
    
    @patch('src.services.logger_service.LoggerService._format_message')
    def test_info_logging(self, mock_format):
        """Test info level logging."""
        mock_format.return_value = '{"message": "test"}'
        
        with patch.object(self.logger_service.logger, 'info') as mock_info:
            self.logger_service.info("Test message", "abc123", {"key": "value"})
            
            mock_format.assert_called_once_with("Test message", "abc123", {"key": "value"})
            mock_info.assert_called_once_with('{"message": "test"}')
    
    @patch('src.services.logger_service.LoggerService._format_message')
    def test_error_logging(self, mock_format):
        """Test error level logging."""
        mock_format.return_value = '{"message": "error"}'
        
        with patch.object(self.logger_service.logger, 'error') as mock_error:
            self.logger_service.error("Error message", "abc123", {"error_code": 500})
            
            mock_format.assert_called_once_with("Error message", "abc123", {"error_code": 500})
            mock_error.assert_called_once_with('{"message": "error"}')
    
    @patch('src.services.logger_service.LoggerService._format_message')
    def test_warning_logging(self, mock_format):
        """Test warning level logging."""
        mock_format.return_value = '{"message": "warning"}'
        
        with patch.object(self.logger_service.logger, 'warning') as mock_warning:
            self.logger_service.warning("Warning message", "abc123")
            
            mock_format.assert_called_once_with("Warning message", "abc123", None)
            mock_warning.assert_called_once_with('{"message": "warning"}')
    
    @patch('src.services.logger_service.LoggerService._format_message')
    def test_debug_logging(self, mock_format):
        """Test debug level logging."""
        mock_format.return_value = '{"message": "debug"}'
        
        with patch.object(self.logger_service.logger, 'debug') as mock_debug:
            self.logger_service.debug("Debug message", "abc123", {"debug_info": "test"})
            
            mock_format.assert_called_once_with("Debug message", "abc123", {"debug_info": "test"})
            mock_debug.assert_called_once_with('{"message": "debug"}')
    
    def test_json_serialization_of_complex_objects(self):
        """Test that complex objects are properly serialized to JSON."""
        message = "Test message"
        extra = {
            "list_data": [1, 2, 3],
            "dict_data": {"nested": {"value": "test"}},
            "none_value": None,
            "boolean": True
        }
        
        formatted = self.logger_service._format_message(message, extra=extra)
        parsed = json.loads(formatted)
        
        assert parsed["message"] == message
        assert parsed["list_data"] == [1, 2, 3]
        assert parsed["dict_data"]["nested"]["value"] == "test"
        assert parsed["none_value"] is None
        assert parsed["boolean"] is True
    
    def test_custom_logger_name(self):
        """Test that custom logger name is properly set."""
        custom_logger = LoggerService("custom_name")
        assert custom_logger.logger.name == "custom_name" 