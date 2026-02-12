"""Logging configuration and Logger class for the converter."""

import logging
import sys
from enum import Enum
from pathlib import Path
from typing import Optional


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR


class Logger:
    """Logger class for conversion operations."""
    
    def __init__(self, log_level: LogLevel = LogLevel.INFO, output_path: Optional[str] = None):
        """Initialize logger with specified level and output path.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            output_path: Optional path to log file. If None, logs to stderr only.
        """
        self.logger = logging.getLogger("doc2md")
        self.logger.setLevel(log_level.value)
        self.logger.handlers.clear()
        
        # Console handler (stderr)
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(log_level.value)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (if output_path specified)
        if output_path:
            file_handler = logging.FileHandler(output_path, encoding='utf-8')
            file_handler.setLevel(log_level.value)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str, exception: Optional[Exception] = None) -> None:
        """Log error message with optional exception details."""
        if exception:
            self.logger.error(f"{message}: {str(exception)}", exc_info=True)
        else:
            self.logger.error(message)
    
    def log_conversion_start(self, file_path: str, file_size: int) -> None:
        """Log conversion start with file details."""
        self.info(f"Starting conversion - File: {file_path}, Size: {file_size} bytes")
    
    def log_conversion_complete(self, output_path: str, duration: float) -> None:
        """Log conversion completion with output details."""
        self.info(f"Conversion complete - Output: {output_path}, Duration: {duration:.2f}s")
