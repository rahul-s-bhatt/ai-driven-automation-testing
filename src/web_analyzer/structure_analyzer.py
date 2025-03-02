"""
Structure Analyzer module for analyzing website structure and suggesting test scenarios.
"""

from typing import Dict, List, Optional
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import re
import time

class StructureAnalyzer:
    def __init__(self, driver: webdriver.Remote):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.logger = logging.getLogger(__name__)

    def analyze_website(self, url: str) -> Dict:
        """Perform website structure analysis."""
        try:
            start_time = time.time()
            self.logger.info(f"Starting analysis of {url}")

            try:
                self.driver.get(url)
                self.wait.until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
            except TimeoutException:
                self.logger.warning("Page load timed out, proceeding with partial analysis")
            except WebDriverException as e:
                self.logger.error(f"WebDriver error: {str(e)}")
                raise

            load_time = time.time() - start_time

            try:
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, 'lxml')
            except Exception as e:
                self.logger.error(f"Error parsing page source: {str(e)}")
                raise

            # Perform analysis
            forms = self._analyze_forms(soup)
            navigation = self._analyze_navigation(soup)
            dynamic_content = self._analyze_dynamic_content()
            page_metrics = self._get_page_metrics(soup, load_time)
            suggested_scenarios = self._generate_test_scenarios(soup, forms, navigation, dynamic_content)

            return {
                'structure': {
                    'forms': forms,
                    'navigation': navigation,
                    'dynamic_content': dynamic_content,
                    'page_metrics': page_metrics,
                    'suggested_scenarios': suggested_scenarios
                }
            }

        except Exception as e:
            self.logger.error(f"Error analyzing website: {str(e)}")
            raise

    def _generate_test_scenarios(self, soup: BeautifulSoup, forms: List[Dict], 
                               navigation: List[Dict], dynamic_content: Dict) -> List[Dict]:
        """Generate suggested test scenarios based on page analysis."""
        scenarios = []

        # Form testing scenarios
        for form in forms:
            form_scenario = {
                'name': 'Form Interaction',
                'description': f"Test form with {len(form['inputs'])} fields",
                'steps': [
                    'wait for 2 seconds'
                ]
            }
            
            # Add steps for each input
            for input_field in form['inputs']:
                if input_field['type'] in ['text', 'email', 'password']:
                    form_scenario['steps'].append(
                        f"type \"test\" into {input_field['name'] or input_field['type']} field"
                    )
                elif input_field['type'] == 'checkbox':
                    form_scenario['steps'].append(
                        f"click on {input_field['name'] or 'checkbox'}"
                    )
                elif input_field['type'] == 'select':
                    form_scenario['steps'].append(
                        f"select option from {input_field['name'] or 'dropdown'}"
                    )

            # Add submit step
            if form['buttons']:
                submit_button = next((b for b in form['buttons'] if b['type'] == 'submit'), None)
                if submit_button:
                    form_scenario['steps'].append(
                        f"click on {submit_button['text'] or 'submit'} button"
                    )
                    form_scenario['steps'].append("wait for 2 seconds")
                    form_scenario['steps'].append("verify that success message appears")

            scenarios.append(form_scenario)

        # Navigation testing scenarios
        for nav in navigation:
            if nav['items']:
                nav_scenario = {
                    'name': 'Navigation Flow',
                    'description': f"Test {nav['type']} navigation with {len(nav['items'])} links",
                    'steps': [
                        'wait for 2 seconds'
                    ]
                }
                
                # Add steps for navigation items
                for item in nav['items'][:3]:  # Test first 3 links
                    nav_scenario['steps'].extend([
                        f"click on {item['text']} link",
                        "wait for 2 seconds",
                        "verify that page loads",
                        "go back",
                        "wait for 2 seconds"
                    ])

                scenarios.append(nav_scenario)

        # Dynamic content scenarios
        if dynamic_content['infinite_scroll']:
            scenarios.append({
                'name': 'Infinite Scroll',
                'description': 'Test infinite scroll functionality',
                'steps': [
                    'wait for 2 seconds',
                    'scroll down till end',
                    'wait for 2 seconds',
                    'verify that new content appears',
                    'scroll down till end',
                    'wait for 2 seconds',
                    'verify that more content appears'
                ]
            })

        if dynamic_content['load_more']:
            scenarios.append({
                'name': 'Load More Content',
                'description': 'Test load more functionality',
                'steps': [
                    'wait for 2 seconds',
                    'click on load more button',
                    'wait for 2 seconds',
                    'verify that new items appear'
                ]
            })

        # Search functionality scenario (if found)
        search_form = soup.find('form', {'role': 'search'}) or soup.find('input', {'type': 'search'})
        if search_form:
            scenarios.append({
                'name': 'Search Functionality',
                'description': 'Test search feature',
                'steps': [
                    'wait for 2 seconds',
                    'type "test" into search field',
                    'press enter key',
                    'wait for 2 seconds',
                    'verify that search results appear'
                ]
            })

        # Login/Signup scenarios (if found)
        login_link = soup.find('a', text=re.compile(r'login|sign in', re.I))
        if login_link:
            scenarios.append({
                'name': 'Login Flow',
                'description': 'Test login functionality',
                'steps': [
                    'wait for 2 seconds',
                    'click on login link',
                    'wait for 2 seconds',
                    'type "test@example.com" into email field',
                    'type "password123" into password field',
                    'click on login button',
                    'wait for 2 seconds',
                    'verify that login succeeds'
                ]
            })

        # Add responsiveness test scenario
        scenarios.append({
            'name': 'Responsive Design',
            'description': 'Test responsive layout',
            'steps': [
                'wait for 2 seconds',
                'set viewport size to mobile',
                'wait for 2 seconds',
                'verify that layout adjusts',
                'set viewport size to tablet',
                'wait for 2 seconds',
                'verify that layout adjusts',
                'set viewport size to desktop',
                'wait for 2 seconds',
                'verify that layout adjusts'
            ]
        })

        return scenarios

    def _analyze_forms(self, soup):
        """
        Analyze form elements in the webpage.
        
        Args:
            soup (BeautifulSoup): The BeautifulSoup object of the webpage
            
        Returns:
            list: List of dictionaries containing form information
        """
        forms_data = []
        forms = soup.find_all('form')
        
        for i, form in enumerate(forms):
            form_data = {
                'id': form.get('id', f'form_{i+1}'),
                'method': form.get('method', 'get').upper(),
                'action': form.get('action', ''),
                'inputs': []
            }
            
            # Analyze inputs
            inputs = form.find_all(['input', 'textarea', 'select'])
            for input_elem in inputs:
                input_type = input_elem.get('type', 'text') if input_elem.name == 'input' else input_elem.name
                input_data = {
                    'name': input_elem.get('name', ''),
                    'id': input_elem.get('id', ''),
                    'type': input_type,
                    'required': input_elem.has_attr('required')
                }
                form_data['inputs'].append(input_data)
                
            # Analyze buttons
            buttons = form.find_all(['button', 'input'])
            button_types = ['submit', 'button', 'reset']
            form_data['buttons'] = [
                {
                    'text': btn.text.strip() if btn.name == 'button' else btn.get('value', ''),
                    'type': btn.get('type', 'submit') if btn.name == 'input' else btn.get('type', 'button')
                }
                for btn in buttons 
                if (btn.name == 'button' or (btn.name == 'input' and btn.get('type') in button_types))
            ]
            
            forms_data.append(form_data)
        
        return forms_data

    def _analyze_navigation(self, soup: BeautifulSoup) -> List[Dict]:
        """Analyze navigation elements in the webpage."""
        navigation = []
        
        # Find main navigation
        nav_elements = soup.find_all('nav')
        for nav in nav_elements:
            nav_data = {
                'type': 'main' if nav.get('role') == 'navigation' else 'secondary',
                'items': []
            }
            
            # Analyze links
            links = nav.find_all('a')
            for link in links:
                nav_data['items'].append({
                    'text': link.text.strip(),
                    'href': link.get('href', ''),
                    'aria_label': link.get('aria-label', '')
                })
                
            navigation.append(nav_data)
        
        return navigation

    def _analyze_dynamic_content(self) -> Dict:
        """Analyze dynamic content loading patterns."""
        dynamic_content = {
            'infinite_scroll': False,
            'load_more': False,
            'auto_refresh': False
        }
        
        try:
            # Check for infinite scroll
            initial_height = self.driver.execute_script("return document.body.scrollHeight")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)  # Wait for potential content load
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            dynamic_content['infinite_scroll'] = new_height > initial_height
            
            # Check for load more buttons
            load_more_buttons = self.driver.find_elements(By.XPATH, 
                "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'load more') or contains(., '...') or contains(., 'show more')]")
            dynamic_content['load_more'] = len(load_more_buttons) > 0
            
        except Exception as e:
            self.logger.warning(f"Error during dynamic content analysis: {str(e)}")
        
        return dynamic_content

    def _get_page_metrics(self, soup: BeautifulSoup, load_time: float) -> Dict:
        """Calculate various page metrics."""
        metrics = {
            'load_time': round(load_time, 2),
            'element_counts': {
                'images': 0,
                'links': 0,
                'buttons': 0,
                'forms': 0,
                'input_fields': 0
            }
        }
        
        if soup:
            try:
                metrics['element_counts'] = {
                    'images': len(soup.find_all('img') or []),
                    'links': len(soup.find_all('a') or []),
                    'buttons': len(soup.find_all('button') or []),
                    'forms': len(soup.find_all('form') or []),
                    'input_fields': len(soup.find_all('input') or [])
                }
            except Exception as e:
                self.logger.warning(f"Error counting page elements: {str(e)}")
        
        return metrics