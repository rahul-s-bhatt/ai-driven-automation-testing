"""
Validator module for test result validation and reporting.

This module provides functionality to validate test results, capture failures,
and generate detailed validation reports.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import logging
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement

# Use absolute imports
from src.test_engine.scenario_parser import TestScenario, TestStep
from src.web_analyzer.dom_parser import DOMParser
from src.web_analyzer.element_classifier import ElementClassifier, ElementContext

@dataclass
class ValidationResult:
    """Represents the result of a test validation."""
    success: bool
    message: str
    timestamp: datetime
    screenshot_path: Optional[str] = None
    element_state: Optional[Dict] = None
    error_details: Optional[Dict] = None

@dataclass
class TestReport:
    """Represents a complete test execution report."""
    scenario_name: str
    start_time: datetime
    end_time: datetime
    total_steps: int
    passed_steps: int
    failed_steps: int
    results: List[ValidationResult]
    environment_info: Dict
    performance_metrics: Optional[Dict] = None

class TestValidator:
    """Main class for validating test results and generating reports."""

    def __init__(self, driver: webdriver.Remote, output_dir: str):
        """
        Initialize the test validator.

        Args:
            driver: Selenium WebDriver instance
            output_dir: Directory to store validation reports and artifacts
        """
        self.driver = driver
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self._setup_logging()

    def _setup_logging(self):
        """Set up logging configuration."""
        self.logger.setLevel(logging.INFO)
        log_file = self.output_dir / 'validation.log'
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def validate_step(self, step: TestStep, element: Optional[WebElement] = None) -> ValidationResult:
        """
        Validate a single test step execution.

        Args:
            step: The test step that was executed
            element: The WebElement involved in the step (if any)

        Returns:
            ValidationResult: The result of the validation
        """
        timestamp = datetime.now()
        screenshot_path = None
        element_state = None

        try:
            if element:
                element_state = self._capture_element_state(element)
            
            validation_success = self._validate_step_result(step, element)
            
            if not validation_success:
                screenshot_path = self._take_screenshot(f"validation_failure_{timestamp.strftime('%Y%m%d_%H%M%S')}")
            
            return ValidationResult(
                success=validation_success,
                message=f"Step '{step.description}' {'passed' if validation_success else 'failed'} validation",
                timestamp=timestamp,
                screenshot_path=screenshot_path,
                element_state=element_state
            )
        
        except Exception as e:
            self.logger.error(f"Validation error: {str(e)}")
            return ValidationResult(
                success=False,
                message=f"Validation failed: {str(e)}",
                timestamp=timestamp,
                error_details={'type': type(e).__name__, 'message': str(e)}
            )

    def _validate_step_result(self, step: TestStep, element: Optional[WebElement]) -> bool:
        """
        Validate the result of a test step based on its type and expected outcome.

        Args:
            step: The test step to validate
            element: The WebElement involved in the step (if any)

        Returns:
            bool: True if validation passed, False otherwise
        """
        if element and not element.is_enabled():
            return False

        if step.action in {'verify', 'assert'}:
            return self._validate_assertion(step, element)
        elif step.action == 'click':
            return element.is_displayed() if element else False
        elif step.action in {'type', 'select'}:
            return self._validate_input(step, element)
        
        return True

    def _validate_assertion(self, step: TestStep, element: Optional[WebElement]) -> bool:
        """
        Validate an assertion step.

        Args:
            step: The assertion step to validate
            element: The WebElement to validate against

        Returns:
            bool: True if assertion passed, False otherwise
        """
        if not element:
            return False

        if 'contains' in step.description.lower():
            return step.value.lower() in element.text.lower()
        elif 'visible' in step.description.lower():
            return element.is_displayed()
        elif 'enabled' in step.description.lower():
            return element.is_enabled()
        
        return True

    def _validate_input(self, step: TestStep, element: Optional[WebElement]) -> bool:
        """
        Validate an input step.

        Args:
            step: The input step to validate
            element: The WebElement to validate against

        Returns:
            bool: True if input validation passed, False otherwise
        """
        if not element:
            return False

        if step.action == 'type':
            return element.get_attribute('value') == step.value
        elif step.action == 'select':
            return element.get_attribute('value') == step.value or \
                   element.text == step.value
        
        return True

    def _capture_element_state(self, element: WebElement) -> Dict:
        """
        Capture the current state of a WebElement.

        Args:
            element: The WebElement to capture state for

        Returns:
            Dict: The element's state information
        """
        return {
            'tag_name': element.tag_name,
            'text': element.text,
            'is_displayed': element.is_displayed(),
            'is_enabled': element.is_enabled(),
            'attributes': self._get_element_attributes(element),
            'location': element.location,
            'size': element.size
        }

    def _get_element_attributes(self, element: WebElement) -> Dict:
        """
        Get all attributes of a WebElement.

        Args:
            element: The WebElement to get attributes for

        Returns:
            Dict: The element's attributes
        """
        return self.driver.execute_script(
            """
            let attrs = {};
            let element = arguments[0];
            for (let i = 0; i < element.attributes.length; i++) {
                attrs[element.attributes[i].name] = element.attributes[i].value
            }
            return attrs;
            """,
            element
        )

    def _take_screenshot(self, name: str) -> str:
        """
        Take a screenshot and save it to the output directory.

        Args:
            name: Name for the screenshot file

        Returns:
            str: Path to the saved screenshot
        """
        filepath = self.output_dir / f"{name}.png"
        self.driver.save_screenshot(str(filepath))
        return str(filepath)

    def generate_report(self, scenario: TestScenario, results: List[ValidationResult]) -> TestReport:
        """
        Generate a test execution report.

        Args:
            scenario: The test scenario that was executed
            results: List of validation results from the test execution

        Returns:
            TestReport: The generated test report
        """
        end_time = datetime.now()
        total_steps = len(scenario.steps)
        passed_steps = sum(1 for r in results if r.success)

        report = TestReport(
            scenario_name=scenario.name,
            start_time=results[0].timestamp if results else end_time,
            end_time=end_time,
            total_steps=total_steps,
            passed_steps=passed_steps,
            failed_steps=total_steps - passed_steps,
            results=results,
            environment_info=self._get_environment_info(),
            performance_metrics=self._collect_performance_metrics()
        )

        self._save_report(report)
        return report

    def _get_environment_info(self) -> Dict:
        """
        Collect information about the test environment.

        Returns:
            Dict: Environment information
        """
        return {
            'browser': self.driver.capabilities.get('browserName', 'unknown'),
            'browser_version': self.driver.capabilities.get('browserVersion', 'unknown'),
            'platform': self.driver.capabilities.get('platformName', 'unknown'),
            'viewport_size': self.driver.get_window_size(),
            'timestamp': datetime.now().isoformat()
        }

    def _collect_performance_metrics(self) -> Dict:
        """
        Collect performance metrics from the browser.

        Returns:
            Dict: Performance metrics
        """
        metrics = {}
        try:
            timing = self.driver.execute_script('return window.performance.timing.toJSON()')
            metrics['page_load_time'] = timing['loadEventEnd'] - timing['navigationStart']
            metrics['dom_complete_time'] = timing['domComplete'] - timing['domLoading']
            metrics['network_latency'] = timing['responseEnd'] - timing['requestStart']
        except Exception as e:
            self.logger.warning(f"Failed to collect performance metrics: {str(e)}")
        
        return metrics

    def _save_report(self, report: TestReport):
        """
        Save the test report to a file.

        Args:
            report: The test report to save
        """
        report_path = self.output_dir / f"report_{report.scenario_name}_{report.end_time.strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert the report to a dictionary
        report_dict = {
            'scenario_name': report.scenario_name,
            'start_time': report.start_time.isoformat(),
            'end_time': report.end_time.isoformat(),
            'total_steps': report.total_steps,
            'passed_steps': report.passed_steps,
            'failed_steps': report.failed_steps,
            'results': [
                {
                    'success': r.success,
                    'message': r.message,
                    'timestamp': r.timestamp.isoformat(),
                    'screenshot_path': r.screenshot_path,
                    'element_state': r.element_state,
                    'error_details': r.error_details
                }
                for r in report.results
            ],
            'environment_info': report.environment_info,
            'performance_metrics': report.performance_metrics
        }

        with open(report_path, 'w') as f:
            json.dump(report_dict, f, indent=2)

        self.logger.info(f"Test report saved to: {report_path}")

    def cleanup(self):
        """Clean up resources."""
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)