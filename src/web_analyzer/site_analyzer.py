"""
Site Analyzer module for analyzing website structure and suggesting test scenarios.

This module analyzes a website's DOM structure, interactive elements, and patterns
to suggest relevant test scenarios.
"""

from typing import Dict, List, Optional, Set
import logging
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class WebsiteStructure:
    """Data class to hold website structure information."""
    def __init__(self):
        self.forms = []
        self.buttons = []
        self.links = []
        self.inputs = []
        self.dynamic_elements = []
        self.navigation = []
        self.authentication = False
        self.infinite_scroll = False
        self.load_more = False
        self.ajax_updates = False

class WebsiteAnalyzer:
    """Analyzes website structure and suggests test scenarios."""

    def __init__(self, driver: webdriver.Remote):
        """Initialize the analyzer with a WebDriver instance."""
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.logger = logging.getLogger(__name__)
        self.structure = WebsiteStructure()

    def analyze_website(self, url: str) -> Dict:
        """
        Analyze website structure and return analysis results.

        Args:
            url: Website URL to analyze

        Returns:
            Dict containing analysis results and suggested test scenarios
        """
        try:
            self.driver.get(url)
            self.wait.until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            
            # Analyze different aspects of the website
            self._analyze_forms()
            self._analyze_navigation()
            self._analyze_dynamic_content()
            self._analyze_authentication()
            
            # Generate test suggestions
            return self._generate_test_suggestions()
            
        except Exception as e:
            self.logger.error(f"Error analyzing website: {str(e)}")
            raise

    def _analyze_forms(self):
        """Analyze forms and input fields."""
        # Find all forms
        forms = self.driver.find_elements(By.TAG_NAME, "form")
        for form in forms:
            form_data = {
                "inputs": [],
                "submit": None,
                "validation": False
            }
            
            # Analyze form inputs
            inputs = form.find_elements(By.TAG_NAME, "input")
            for input_field in inputs:
                input_type = input_field.get_attribute("type")
                if input_type:
                    form_data["inputs"].append({
                        "type": input_type,
                        "name": input_field.get_attribute("name"),
                        "required": input_field.get_attribute("required") is not None
                    })
            
            # Check for submit button
            submit = form.find_elements(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            if submit:
                form_data["submit"] = True
            
            # Check for client-side validation
            if "required" in form.get_attribute("innerHTML"):
                form_data["validation"] = True
            
            self.structure.forms.append(form_data)

    def _analyze_navigation(self):
        """Analyze navigation elements and menu structure."""
        # Check for common navigation patterns
        nav_elements = self.driver.find_elements(By.TAG_NAME, "nav")
        for nav in nav_elements:
            nav_items = nav.find_elements(By.TAG_NAME, "a")
            self.structure.navigation.extend([
                {
                    "text": item.text,
                    "href": item.get_attribute("href"),
                    "visible": item.is_displayed()
                }
                for item in nav_items
            ])

        # Check for menu toggles (hamburger menu)
        menu_toggles = self.driver.find_elements(
            By.CSS_SELECTOR,
            "[class*='menu'], [class*='navbar'], [class*='nav-toggle']"
        )
        if menu_toggles:
            self.structure.navigation.append({"type": "mobile_menu"})

    def _analyze_dynamic_content(self):
        """Analyze dynamic content loading patterns."""
        initial_height = self.driver.execute_script("return document.body.scrollHeight")
        
        # Scroll to check for infinite scroll
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.wait.until(lambda d: True)  # Small wait
        
        new_height = self.driver.execute_script("return document.body.scrollHeight")
        if new_height > initial_height:
            self.structure.infinite_scroll = True
        
        # Check for "Load More" buttons
        load_more = self.driver.find_elements(
            By.XPATH,
            "//*[contains(text(), 'Load') and contains(text(), 'More')] | " +
            "//*[contains(text(), 'Show') and contains(text(), 'More')]"
        )
        if load_more:
            self.structure.load_more = True

        # Check for dynamic updates (AJAX)
        observer_script = """
            return !!window.fetch || 
                   !!window.XMLHttpRequest ||
                   !!document.querySelector('[data-ajax]');
        """
        try:
            has_ajax = self.driver.execute_script(observer_script)
            self.structure.ajax_updates = has_ajax
        except:
            pass

    def _analyze_authentication(self):
        """Detect authentication-related features."""
        auth_indicators = [
            "login",
            "signin",
            "signup",
            "register",
            "forgot.*password",
            "reset.*password",
            "auth"
        ]
        
        # Check for auth-related elements
        for indicator in auth_indicators:
            elements = self.driver.find_elements(
                By.XPATH,
                f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{indicator}')]"
            )
            if elements:
                self.structure.authentication = True
                break

    def _generate_test_suggestions(self) -> Dict:
        """Generate test scenario suggestions based on analysis."""
        suggestions = {
            "scenarios": [],
            "structure": {
                "forms": len(self.structure.forms),
                "navigation": len(self.structure.navigation),
                "dynamic_content": bool(self.structure.infinite_scroll or self.structure.load_more),
                "authentication": self.structure.authentication
            }
        }

        # Form testing scenarios
        for i, form in enumerate(self.structure.forms):
            scenario = {
                "name": f"Form Submission Test {i+1}",
                "steps": []
            }
            
            for input_data in form["inputs"]:
                if input_data["type"] == "text":
                    scenario["steps"].append(f"type 'test' into {input_data['name']} field")
                elif input_data["type"] == "email":
                    scenario["steps"].append(f"type 'test@example.com' into {input_data['name']} field")
                elif input_data["type"] == "password":
                    scenario["steps"].append(f"type 'password123' into {input_data['name']} field")
            
            if form["submit"]:
                scenario["steps"].append("click on submit button")
                scenario["steps"].append("wait for 2 seconds")
                
            if form["validation"]:
                scenario["steps"].append("verify that success message appears")
            
            suggestions["scenarios"].append(scenario)

        # Navigation testing
        if self.structure.navigation:
            scenario = {
                "name": "Navigation Flow Test",
                "steps": ["wait for 2 seconds"]
            }
            for nav in self.structure.navigation[:5]:  # Limit to first 5 items
                if isinstance(nav, dict) and "text" in nav:
                    scenario["steps"].extend([
                        f"click on {nav['text']}",
                        "wait for 2 seconds",
                        "verify that page loads"
                    ])
            suggestions["scenarios"].append(scenario)

        # Dynamic content testing
        if self.structure.infinite_scroll:
            suggestions["scenarios"].append({
                "name": "Infinite Scroll Test",
                "steps": [
                    "wait for 2 seconds",
                    "scroll down till end",
                    "wait for 2 seconds",
                    "verify that new content appears",
                    "scroll down till end",
                    "wait for 2 seconds",
                    "verify that more content appears"
                ]
            })
        elif self.structure.load_more:
            suggestions["scenarios"].append({
                "name": "Load More Content Test",
                "steps": [
                    "wait for 2 seconds",
                    "click on load more button",
                    "wait for 2 seconds",
                    "verify that new content appears",
                    "click on load more button",
                    "wait for 2 seconds",
                    "verify that more content appears"
                ]
            })

        # Authentication testing
        if self.structure.authentication:
            suggestions["scenarios"].append({
                "name": "Authentication Flow Test",
                "steps": [
                    "wait for 2 seconds",
                    "click on login button",
                    "wait for 2 seconds",
                    "type 'test@example.com' into email field",
                    "type 'password123' into password field",
                    "click on submit button",
                    "wait for 2 seconds",
                    "verify that dashboard appears"
                ]
            })

        return suggestions