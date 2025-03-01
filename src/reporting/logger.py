"""
Logger module for consistent logging across the framework.

This module provides a centralized logging configuration and custom formatters
for the testing framework.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme
import json

class TestLogger:
    """Main class for managing logging across the testing framework."""

    def __init__(self, log_dir: str, log_level: int = logging.INFO):
        """
        Initialize the test logger.

        Args:
            log_dir: Directory to store log files
            log_level: Logging level (default: INFO)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_level = log_level
        
        # Create rich console for formatted output
        self.console = Console(theme=Theme({
            "info": "cyan",
            "warning": "yellow",
            "error": "red",
            "critical": "red reverse"
        }))

        # Set up logging configuration
        self._setup_logging()

    def _setup_logging(self):
        """Set up logging configuration with file and console handlers."""
        # Create base logger
        self.logger = logging.getLogger('test_framework')
        self.logger.setLevel(self.log_level)

        # Remove existing handlers
        self.logger.handlers = []

        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create file handler
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.log_dir / f"test_execution_{timestamp}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(self.log_level)
        
        # Create rich console handler
        console_handler = RichHandler(
            console=self.console,
            show_time=True,
            show_path=True
        )
        console_handler.setLevel(self.log_level)

        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # Store handlers for cleanup
        self.handlers = [file_handler, console_handler]

    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance with the specified name.

        Args:
            name: Name for the logger

        Returns:
            logging.Logger: Configured logger instance
        """
        return logging.getLogger(f"test_framework.{name}")

    def log_test_start(self, scenario_name: str):
        """
        Log the start of a test scenario.

        Args:
            scenario_name: Name of the test scenario
        """
        self.logger.info("="*80)
        self.logger.info(f"Starting Test Scenario: {scenario_name}")
        self.logger.info("="*80)

    def log_test_end(self, scenario_name: str, success: bool, duration: float):
        """
        Log the end of a test scenario.

        Args:
            scenario_name: Name of the test scenario
            success: Whether the test passed
            duration: Test duration in seconds
        """
        self.logger.info("="*80)
        status = "PASSED" if success else "FAILED"
        self.logger.info(f"Test Scenario: {scenario_name} - {status}")
        self.logger.info(f"Duration: {duration:.2f} seconds")
        self.logger.info("="*80)

    def log_step_start(self, step_description: str):
        """
        Log the start of a test step.

        Args:
            step_description: Description of the test step
        """
        self.logger.info(f"--> Starting step: {step_description}")

    def log_step_end(self, step_description: str, success: bool, details: Optional[dict] = None):
        """
        Log the end of a test step.

        Args:
            step_description: Description of the test step
            success: Whether the step passed
            details: Additional details about the step execution
        """
        status = "✓" if success else "✗"
        self.logger.info(f"{status} Completed step: {step_description}")
        if details:
            self.logger.debug(f"Step details: {json.dumps(details, indent=2)}")

    def log_error(self, error_message: str, exception: Optional[Exception] = None):
        """
        Log an error with optional exception details.

        Args:
            error_message: Error message to log
            exception: Optional exception object
        """
        self.logger.error(error_message)
        if exception:
            self.logger.exception(exception)

    def log_warning(self, warning_message: str):
        """
        Log a warning message.

        Args:
            warning_message: Warning message to log
        """
        self.logger.warning(warning_message)

    def log_debug(self, debug_message: str):
        """
        Log a debug message.

        Args:
            debug_message: Debug message to log
        """
        self.logger.debug(debug_message)

    def log_performance_metric(self, metric_name: str, value: float, unit: str = "ms"):
        """
        Log a performance metric.

        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement (default: ms)
        """
        self.logger.info(f"Performance Metric - {metric_name}: {value} {unit}")

    def log_validation_result(self, element_name: str, validation_type: str, result: bool, details: Optional[dict] = None):
        """
        Log a validation result.

        Args:
            element_name: Name of the validated element
            validation_type: Type of validation performed
            result: Validation result
            details: Additional validation details
        """
        status = "PASSED" if result else "FAILED"
        self.logger.info(f"Validation {status} - {validation_type} on {element_name}")
        if details:
            self.logger.debug(f"Validation details: {json.dumps(details, indent=2)}")

    def log_section(self, section_name: str):
        """
        Log a section header.

        Args:
            section_name: Name of the section
        """
        self.logger.info("\n" + "="*40)
        self.logger.info(f"== {section_name} ==")
        self.logger.info("="*40 + "\n")

    def cleanup(self):
        """Clean up logging resources."""
        for handler in self.handlers:
            handler.close()
            self.logger.removeHandler(handler)