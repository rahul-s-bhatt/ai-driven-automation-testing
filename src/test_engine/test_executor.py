"""
Test Executor module for running automated tests.

This module provides functionality to execute test scenarios using Selenium WebDriver,
handling element interactions and validations.
"""

import time
from typing import Dict, List, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException
)
import logging
from pathlib import Path
from datetime import datetime

from src.web_analyzer.dom_parser import DOMParser
from src.web_analyzer.element_classifier import ElementClassifier, ElementContext
from src.test_engine.scenario_parser import TestScenario, TestStep, ActionType

class TestExecutor:
    """Main class for executing test scenarios."""

    def __init__(self, driver: webdriver.Remote, screenshot_dir: Optional[str] = None, base_url: str = None):
        """Initialize the test executor."""
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.dom_parser = DOMParser(driver)
        self.element_classifier = ElementClassifier()
        self.screenshot_dir = Path(screenshot_dir) if screenshot_dir else None
        self.base_url = base_url
        self.logger = self._setup_logger()
        self.page_state = {
            'initial_height': 0,
            'last_height': 0,
            'element_count': 0
        }

    def _setup_logger(self):
        """Set up logging configuration."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        if not logger.handlers:
            logger.addHandler(console_handler)
        
        return logger

    def _get_page_state(self):
        """Capture current page state."""
        self.page_state['last_height'] = self.driver.execute_script("return document.body.scrollHeight")
        self.page_state['element_count'] = len(self.driver.find_elements(By.XPATH, "//*"))

    def _check_content_change(self) -> bool:
        """Check if page content has changed."""
        current_height = self.driver.execute_script("return document.body.scrollHeight")
        current_elements = len(self.driver.find_elements(By.XPATH, "//*"))
        
        height_changed = current_height > self.page_state['last_height']
        elements_changed = current_elements > self.page_state['element_count']
        
        if height_changed or elements_changed:
            self.logger.info("Detected new content: " + 
                          f"Height changed: {height_changed}, " +
                          f"Elements changed: {elements_changed}")
            return True
        return False

    def _verify_new_content(self, timeout: int = 5) -> bool:
        """
        Verify if new content appears on the page.
        
        Args:
            timeout: Maximum time to wait for content
            
        Returns:
            bool: True if new content detected
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self._check_content_change():
                return True
            time.sleep(1)
        return False

    def execute_scenario(self, scenario: TestScenario) -> Tuple[bool, List[str]]:
        """Execute a test scenario."""
        if not self.base_url:
            raise ValueError("Base URL is not set. Please provide a base URL in configuration or via command line.")

        self.logger.info(f"Executing scenario: {scenario.name}")
        self.logger.info(f"Navigating to base URL: {self.base_url}")
        
        try:
            self.driver.get(self.base_url)
            self.wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
            self._get_page_state()  # Initial page state
        except Exception as e:
            error_msg = f"Failed to load base URL {self.base_url}: {str(e)}"
            self.logger.error(error_msg)
            return False, [error_msg]

        errors = []
        success = True

        for i, step in enumerate(scenario.steps, 1):
            try:
                self.logger.info(f"Step {i}: {step.description}")
                
                # Special handling for content verification
                if step.action == ActionType.VERIFY and 'new content' in step.description.lower():
                    if not self._verify_new_content():
                        raise AssertionError("No new content detected after waiting")
                else:
                    self._execute_step(step)
                
                self._take_screenshot(f"{scenario.name}_step_{i}")
                self._get_page_state()  # Update page state after each step
                time.sleep(1)  # Small delay between steps
            
            except Exception as e:
                error_msg = self._format_error_message(step, str(e))
                self.logger.error(error_msg)
                errors.append(error_msg)
                self._take_screenshot(f"{scenario.name}_step_{i}_error")
                success = False
                break

        return success, errors

    def _format_error_message(self, step: TestStep, error: str) -> str:
        """Format error message with helpful context."""
        base_msg = f"Failed to execute: {step.description}\n"
        
        if "new content" in step.description.lower():
            return base_msg + "No new content was detected. Try:\n" + \
                   "1. Increasing wait time\n" + \
                   "2. Scrolling more slowly\n" + \
                   "3. Checking if the page has dynamic loading"
        
        if "Could not find element" in error:
            return base_msg + f"Could not find: {step.target}\nTry:\n" + \
                   "1. Adding a 'wait for 2 seconds' step before this action\n" + \
                   "2. Checking if the element name matches exactly\n" + \
                   "3. Verifying the element is visible on the page"
        
        return base_msg + str(error)

    def _execute_step(self, step: TestStep):
        """Execute a single test step."""
        if step.action == ActionType.CLICK:
            self._handle_click(step)
        elif step.action == ActionType.TYPE:
            self._handle_type(step)
        elif step.action == ActionType.SELECT:
            self._handle_select(step)
        elif step.action == ActionType.VERIFY:
            self._handle_verify(step)
        elif step.action == ActionType.WAIT:
            self._handle_wait(step)
        elif step.action == ActionType.SCROLL:
            self._handle_scroll(step)
        elif step.action == ActionType.HOVER:
            self._handle_hover(step)
        elif step.action == ActionType.ASSERT:
            self._handle_assert(step)

    # ... (rest of the methods remain the same) ...