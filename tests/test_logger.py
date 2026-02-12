"""Unit tests for Logger class."""

import pytest
from pathlib import Path
from src.logger import Logger, LogLevel


class TestLogger:
    """Test suite for Logger class."""
    
    def test_logger_initialization_console_only(self):
        """Test logger initialization with console output only."""
        logger = Logger(log_level=LogLevel.INFO)
        assert logger.logger is not None
        assert len(logger.logger.handlers) == 1  # Console handler only
    
    def test_logger_initialization_with_file(self, temp_dir):
        """Test logger initialization with file output."""
        log_file = temp_dir / "test.log"
        logger = Logger(log_level=LogLevel.DEBUG, output_path=str(log_file))
        assert logger.logger is not None
        assert len(logger.logger.handlers) == 2  # Console + file handlers
    
    def test_logger_debug_message(self, temp_dir):
        """Test debug message logging."""
        log_file = temp_dir / "debug.log"
        logger = Logger(log_level=LogLevel.DEBUG, output_path=str(log_file))
        logger.debug("Test debug message")
        
        log_content = log_file.read_text()
        assert "Test debug message" in log_content
        assert "DEBUG" in log_content
    
    def test_logger_info_message(self, temp_dir):
        """Test info message logging."""
        log_file = temp_dir / "info.log"
        logger = Logger(log_level=LogLevel.INFO, output_path=str(log_file))
        logger.info("Test info message")
        
        log_content = log_file.read_text()
        assert "Test info message" in log_content
        assert "INFO" in log_content
    
    def test_logger_warning_message(self, temp_dir):
        """Test warning message logging."""
        log_file = temp_dir / "warning.log"
        logger = Logger(log_level=LogLevel.WARNING, output_path=str(log_file))
        logger.warning("Test warning message")
        
        log_content = log_file.read_text()
        assert "Test warning message" in log_content
        assert "WARNING" in log_content
    
    def test_logger_error_message(self, temp_dir):
        """Test error message logging."""
        log_file = temp_dir / "error.log"
        logger = Logger(log_level=LogLevel.ERROR, output_path=str(log_file))
        logger.error("Test error message")
        
        log_content = log_file.read_text()
        assert "Test error message" in log_content
        assert "ERROR" in log_content
    
    def test_logger_error_with_exception(self, temp_dir):
        """Test error logging with exception."""
        log_file = temp_dir / "exception.log"
        logger = Logger(log_level=LogLevel.ERROR, output_path=str(log_file))
        
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            logger.error("Error occurred", exception=e)
        
        log_content = log_file.read_text()
        assert "Error occurred" in log_content
        assert "Test exception" in log_content
    
    def test_log_conversion_start(self, temp_dir):
        """Test conversion start logging."""
        log_file = temp_dir / "conversion.log"
        logger = Logger(log_level=LogLevel.INFO, output_path=str(log_file))
        logger.log_conversion_start("/path/to/file.docx", 1024)
        
        log_content = log_file.read_text()
        assert "Starting conversion" in log_content
        assert "/path/to/file.docx" in log_content
        assert "1024 bytes" in log_content
    
    def test_log_conversion_complete(self, temp_dir):
        """Test conversion completion logging."""
        log_file = temp_dir / "conversion.log"
        logger = Logger(log_level=LogLevel.INFO, output_path=str(log_file))
        logger.log_conversion_complete("/path/to/output.md", 2.5)
        
        log_content = log_file.read_text()
        assert "Conversion complete" in log_content
        assert "/path/to/output.md" in log_content
        assert "2.50s" in log_content
    
    def test_logger_level_filtering(self, temp_dir):
        """Test that log level filtering works correctly."""
        log_file = temp_dir / "filtered.log"
        logger = Logger(log_level=LogLevel.WARNING, output_path=str(log_file))
        
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        log_content = log_file.read_text()
        assert "Debug message" not in log_content
        assert "Info message" not in log_content
        assert "Warning message" in log_content
        assert "Error message" in log_content
