"""
Test Executor module for running automated tests with enhanced structure analysis.

This module provides functionality to execute test scenarios using Selenium WebDriver,
handling element interactions and validations with structure-aware element finding.
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
from bs4 import BeautifulSoup

from src.web_analyzer.dom_parser import DOMParser
from src.web_analyzer.element_classifier import ElementClassifier
from src.web_analyzer.structure_analyzer import StructureAnalyzer
from src.test_engine.scenario_parser import TestScenario, TestStep, ActionType

class TestExecutor:
    """Main class for executing test scenarios with structure analysis."""

    def __init__(self, driver: webdriver.Remote, screenshot_dir: Optional[str] = None, base_url: str = None):
        """Initialize the test executor."""
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.dom_parser = DOMParser(driver)
        self.element_classifier = ElementClassifier()
        self.structure_analyzer = StructureAnalyzer(driver)
        self.screenshot_dir = Path(screenshot_dir) if screenshot_dir else None
        self.base_url = base_url
        self.logger = self._setup_logger()
        self.structure_analysis = None
        self.element_selectors = {}

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

    def execute_scenario(self, scenario: TestScenario) -> Tuple[bool, List[str]]:
        """Execute a test scenario with structure analysis."""
        if not self.base_url:
            raise ValueError("Base URL is not set")

        self.logger.info(f"Executing scenario: {scenario.name}")
        self.logger.info(f"Analyzing website structure: {self.base_url}")
        
        try:
            # First analyze website structure
            self.structure_analysis = self.structure_analyzer.analyze_website(self.base_url)
            self.element_selectors = self.structure_analysis.get('suggested_selectors', {})
            
            self.logger.info("Website structure analysis completed")
            
            self.driver.get(self.base_url)
            self.wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
        except Exception as e:
            error_msg = f"Failed to analyze website: {str(e)}"
            self.logger.error(error_msg)
            return False, [error_msg]

        errors = []
        success = True

        for i, step in enumerate(scenario.steps, 1):
            try:
                self.logger.info(f"Step {i}: {step.description}")
                self._execute_step(step)
                self.take_screenshot(f"{scenario.name}_step_{i}")
                time.sleep(1)  # Small delay between steps
            except Exception as e:
                error_msg = self._format_error_message(step, str(e))
                self.logger.error(error_msg)
                errors.append(error_msg)
                self.take_screenshot(f"{scenario.name}_step_{i}_error")
                success = False
                break

        return success, errors

    def _find_element(self, target: str, timeout: int = 10) -> webdriver.Remote:
        """Find an element using structure analysis and multiple strategies."""
        # First try structure-based selectors
        if self.element_selectors:
            try:
                if selector := self._get_structure_based_selector(target):
                    return self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
            except TimeoutException:
                pass

        # Fallback to multiple strategies
        strategies = [
            (By.ID, target),
            (By.NAME, target),
            (By.CLASS_NAME, target),
            (By.CSS_SELECTOR, target),
            (By.XPATH, f"//*[contains(text(), '{target}')]"),
            (By.XPATH, f"//button[contains(text(), '{target}')]"),
            (By.XPATH, f"//input[@placeholder='{target}']"),
            (By.XPATH, f"//label[contains(text(), '{target}')]/..//input"),
            (By.XPATH, f"//a[contains(text(), '{target}')]"),
        ]

        for by, selector in strategies:
            try:
                return self.wait.until(
                    EC.presence_of_element_located((by, selector))
                )
            except TimeoutException:
                continue

        raise NoSuchElementException(f"Could not find element: {target}")

    def _get_structure_based_selector(self, target: str) -> Optional[str]:
        """Get selector from structure analysis results."""
        target = target.lower()
        
        # Check form input selectors
        for form_id, form_data in self.element_selectors.get('forms', {}).items():
            for input_name, selector in form_data.get('inputs', {}).items():
                if target in input_name.lower():
                    return selector

        # Check dynamic content selectors
        dynamic_selectors = self.element_selectors.get('dynamic_content', {})
        if 'load_more' in target and 'load_more_button' in dynamic_selectors:
            return dynamic_selectors['load_more_button']

        return None

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

    def _handle_click(self, step: TestStep):
        """Handle click action."""
        element = self._find_element(step.target)
        self.wait.until(EC.element_to_be_clickable(element))
        element.click()

    def _handle_type(self, step: TestStep):
        """Handle type action."""
        element = self._find_element(step.target)
        element.clear()
        element.send_keys(step.value)

    def _handle_select(self, step: TestStep):
        """Handle select action."""
        element = self._find_element(step.target)
        select = Select(element)
        select.select_by_visible_text(step.value)

    def _handle_verify(self, step: TestStep):
        """Handle verify action with structure awareness."""
        try:
            if 'new content' in step.description.lower():
                # Use structure analysis for content verification
                if self.structure_analysis['structure']['dynamic_content']['infinite_scroll']:
                    current_height = self.driver.execute_script("return document.body.scrollHeight")
                    assert current_height > self._last_height, "No new content loaded"
                    self._last_height = current_height
            else:
                element = self._find_element(step.target)
                if 'appears' in step.description:
                    assert element.is_displayed(), f"Element {step.target} is not visible"
                elif 'contains' in step.description:
                    assert step.value.lower() in element.text.lower(), \
                        f"Expected text '{step.value}' not found in element {step.target}"
        except (TimeoutException, AssertionError) as e:
            raise AssertionError(f"Verification failed: {str(e)}")

    def _handle_wait(self, step: TestStep):
        """Handle wait action."""
        if step.target.lower() == 'page':
            time.sleep(int(step.value or 2))
        else:
            self._find_element(step.target, timeout=int(step.value or 10))

    def _handle_scroll(self, step: TestStep):
        """Handle scroll action using structure analysis."""
        description = step.description.lower()
        target = step.target.lower()

        # Use structure analysis for scroll container
        scroll_container = None
        if self.structure_analysis['structure']['dynamic_content']['infinite_scroll']:
            scroll_container = self.element_selectors['dynamic_content'].get('scroll_container')

        if 'till end' in description or 'to end' in description:
            if scroll_container:
                self.driver.execute_script(
                    f"document.querySelector('{scroll_container}').scrollTo(0, document.querySelector('{scroll_container}').scrollHeight);"
                )
            else:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        elif 'till top' in description or 'to top' in description:
            if scroll_container:
                self.driver.execute_script(
                    f"document.querySelector('{scroll_container}').scrollTo(0, 0);"
                )
            else:
                self.driver.execute_script("window.scrollTo(0, 0);")
        else:
            element = self._find_element(target)
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                element
            )

        time.sleep(1)  # Wait for scroll to complete

    def _handle_hover(self, step: TestStep):
        """Handle hover action."""
        element = self._find_element(step.target)
        ActionChains(self.driver).move_to_element(element).perform()

    def _handle_assert(self, step: TestStep):
        """Handle assert action."""
        element = self._find_element(step.target)
        assert step.value.lower() in element.text.lower(), \
            f"Assertion failed: Expected '{step.value}' in element {step.target}"

    def take_screenshot(self, name: str):
        """Take a screenshot if screenshot directory is configured."""
        if self.screenshot_dir:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{name}_{timestamp}.png"
            filepath = self.screenshot_dir / filename
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)
            self.driver.save_screenshot(str(filepath))
            self.logger.info(f"Screenshot saved: {filepath}")

    def _format_error_message(self, step: TestStep, error: str) -> str:
        """Format error message with helpful context and structure information."""
        base_msg = f"Failed to execute: {step.description}\n"
        
        if "new content" in step.description.lower():
            return base_msg + "No new content was detected. Structure analysis shows:\n" + \
                   f"- Infinite scroll: {self.structure_analysis['structure']['dynamic_content']['infinite_scroll']}\n" + \
                   f"- Load more: {self.structure_analysis['structure']['dynamic_content']['load_more']}\n" + \
                   "Try:\n" + \
                   "1. Increasing wait time\n" + \
                   "2. Scrolling more slowly\n" + \
                   "3. Checking if the page has dynamic loading"
        
        if "Could not find element" in error:
            suggested_selector = self._get_structure_based_selector(step.target)
            return base_msg + f"Could not find: {step.target}\n" + \
                   (f"Suggested selector: {suggested_selector}\n" if suggested_selector else "") + \
                   "Try:\n" + \
                   "1. Adding a wait step before this action\n" + \
                   "2. Checking if the element name matches exactly\n" + \
                   "3. Verifying the element is visible on the page"
        
        return base_msg + str(error)

    def cleanup(self):
        """Clean up resources."""
        if self.driver:
            self.driver.quit()