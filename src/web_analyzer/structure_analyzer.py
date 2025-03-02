"""
Structure Analyzer module for analyzing website structure and suggesting test scenarios.

This module provides comprehensive website structure analysis including:
- DOM structure analysis
- Interactive elements detection
- Content patterns recognition
- Form structure analysis
- Navigation flow mapping
"""

from typing import Dict, List, Optional, Set
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re
import requests
from urllib.parse import urljoin, urlparse
from time import sleep

class WebStructure:
    """Data class to hold website structure information."""
    def __init__(self):
        self.forms = []
        self.inputs = []
        self.buttons = []
        self.links = []
        self.headings = []
        self.navigation = []
        self.lists = []
        self.tables = []
        self.images = []
        self.iframes = []
        self.dynamic_elements = []
        self.ajax_endpoints = set()
        self.patterns = {
            'auth': False,
            'search': False,
            'pagination': False,
            'infinite_scroll': False,
            'load_more': False,
            'filters': False
        }

class StructureAnalyzer:
    """Analyzes website structure using BeautifulSoup and Selenium."""

    def __init__(self, driver: webdriver.Remote):
        """Initialize the analyzer with a WebDriver instance."""
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.logger = logging.getLogger(__name__)
        self.structure = WebStructure()
        self.base_url = None

    def analyze_website(self, url: str) -> Dict:
        """Perform website structure analysis."""
        try:
            self.base_url = url
            self.driver.get(url)
            self.wait.until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )

            # Get page source after JavaScript execution
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Analyze different aspects
            self._analyze_forms(soup)
            self._analyze_navigation(soup)
            self._analyze_dynamic_content()
            self._analyze_content_patterns(soup)

            return self._generate_report()

        except Exception as e:
            self.logger.error(f"Error analyzing website: {str(e)}")
            raise

    def _extract_validation_rules(self, element) -> List[str]:
        """Extract input validation rules from element attributes."""
        rules = []
        
        # HTML5 validation attributes
        if element.get('required'):
            rules.append('required')
        if element.get('pattern'):
            rules.append(f"pattern: {element['pattern']}")
        if element.get('minlength'):
            rules.append(f"minlength: {element['minlength']}")
        if element.get('maxlength'):
            rules.append(f"maxlength: {element['maxlength']}")
        if element.get('min'):
            rules.append(f"min: {element['min']}")
        if element.get('max'):
            rules.append(f"max: {element['max']}")
        
        return rules

    def _analyze_forms(self, soup: BeautifulSoup):
        """Analyze form structures."""
        forms = soup.find_all('form')
        
        for form in forms:
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get'),
                'inputs': [],
                'submit': None,
                'validation': False
            }
            
            # Analyze inputs
            inputs = form.find_all(['input', 'select', 'textarea'])
            for input_field in inputs:
                input_data = {
                    'type': input_field.get('type', 'text'),
                    'name': input_field.get('name', ''),
                    'id': input_field.get('id', ''),
                    'required': input_field.get('required') is not None,
                    'validation': self._extract_validation_rules(input_field)
                }
                form_data['inputs'].append(input_data)
            
            # Check for submit button
            submit = form.find(['button[type="submit"]', 'input[type="submit"]'])
            form_data['submit'] = bool(submit)
            
            # Check for client-side validation
            form_data['validation'] = bool(form_data['inputs'] and any(
                input_data['validation'] for input_data in form_data['inputs']
            ))
            
            self.structure.forms.append(form_data)

    def _analyze_navigation(self, soup: BeautifulSoup):
        """Analyze navigation elements."""
        nav_elements = soup.find_all(['nav', 'header', 'div[role="navigation"]'])
        
        for nav in nav_elements:
            nav_data = {
                'links': [],
                'structure': 'horizontal' if self._is_horizontal_nav(nav) else 'vertical',
                'depth': self._calculate_nav_depth(nav)
            }
            
            links = nav.find_all('a')
            for link in links:
                nav_data['links'].append({
                    'text': link.get_text(strip=True),
                    'url': urljoin(self.base_url, link.get('href', '')),
                    'level': len(link.find_parents(['ul', 'ol']))
                })
            
            self.structure.navigation.append(nav_data)

    def _is_horizontal_nav(self, nav) -> bool:
        """Detect if navigation is horizontal."""
        try:
            display = self.driver.execute_script(
                "return window.getComputedStyle(arguments[0]).display",
                nav
            )
            return display in ['flex', 'inline-block', 'inline-flex']
        except:
            return False

    def _calculate_nav_depth(self, nav) -> int:
        """Calculate navigation depth."""
        max_depth = 0
        lists = nav.find_all(['ul', 'ol'])
        
        for list_elem in lists:
            depth = len(list_elem.find_parents(['ul', 'ol']))
            max_depth = max(max_depth, depth)
        
        return max_depth + 1

    def _analyze_dynamic_content(self):
        """Analyze dynamic content loading."""
        initial_height = self.driver.execute_script("return document.body.scrollHeight")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)
        new_height = self.driver.execute_script("return document.body.scrollHeight")
        
        if new_height > initial_height:
            self.structure.patterns['infinite_scroll'] = True
        
        load_more = self.driver.find_elements(
            By.XPATH,
            "//*[contains(text(), 'Load More') or contains(text(), 'Show More')]"
        )
        if load_more:
            self.structure.patterns['load_more'] = True

    def _analyze_content_patterns(self, soup: BeautifulSoup):
        """Analyze content structure patterns."""
        # Check for search functionality
        search_elements = soup.find_all(['input', 'form'], {'type': 'search'})
        self.structure.patterns['search'] = bool(search_elements)
        
        # Check for pagination
        pagination = soup.find_all(['div', 'nav', 'ul'], {'class': re.compile(r'pagination|pager')})
        self.structure.patterns['pagination'] = bool(pagination)
        
        # Check for filters
        filters = soup.find_all(['div', 'aside'], {'class': re.compile(r'filter|facet')})
        self.structure.patterns['filters'] = bool(filters)

    def _generate_report(self) -> Dict:
        """Generate analysis report."""
        return {
            'structure': {
                'forms': [
                    {
                        'inputs': len(form['inputs']),
                        'validation': form['validation'],
                        'method': form['method']
                    }
                    for form in self.structure.forms
                ],
                'navigation': [
                    {
                        'links': len(nav['links']),
                        'depth': nav['depth'],
                        'structure': nav['structure']
                    }
                    for nav in self.structure.navigation
                ],
                'dynamic_content': {
                    'infinite_scroll': self.structure.patterns['infinite_scroll'],
                    'load_more': self.structure.patterns['load_more']
                },
                'features': {
                    'search': self.structure.patterns['search'],
                    'pagination': self.structure.patterns['pagination'],
                    'filters': self.structure.patterns['filters']
                }
            },
            'test_scenarios': self._generate_test_scenarios()
        }

    def _generate_test_scenarios(self) -> List[Dict]:
        """Generate suggested test scenarios."""
        scenarios = []
        
        # Form testing scenarios
        if self.structure.forms:
            scenarios.append({
                'name': 'Form Submission Test',
                'steps': [
                    'wait for 2 seconds',
                    'type "test@example.com" into email field',
                    'type "test123" into password field',
                    'click on submit button',
                    'wait for 2 seconds',
                    'verify that success message appears'
                ]
            })
        
        # Dynamic content scenarios
        if self.structure.patterns['infinite_scroll']:
            scenarios.append({
                'name': 'Infinite Scroll Test',
                'steps': [
                    'wait for 2 seconds',
                    'scroll down till end',
                    'wait for 2 seconds',
                    'verify that new content appears'
                ]
            })
        elif self.structure.patterns['load_more']:
            scenarios.append({
                'name': 'Load More Test',
                'steps': [
                    'wait for 2 seconds',
                    'click on load more button',
                    'wait for 2 seconds',
                    'verify that new items appear'
                ]
            })
        
        # Navigation scenarios
        if self.structure.navigation:
            scenarios.append({
                'name': 'Navigation Flow Test',
                'steps': [
                    'wait for 2 seconds',
                    'click on menu button',
                    'wait for 2 seconds',
                    'verify that navigation menu appears'
                ]
            })
        
        return scenarios