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
            self.driver.get(url)
            self.wait.until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            load_time = time.time() - start_time

            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')

            return {
                'structure': {
                    'forms': self._analyze_forms(soup),
                    'navigation': self._analyze_navigation(soup),
                    'dynamic_content': self._analyze_dynamic_content(),
                    'page_metrics': self._get_page_metrics(soup, load_time)
                }
            }
        except Exception as e:
            self.logger.error(f"Error analyzing website: {str(e)}")
            raise

    def _analyze_forms(self, soup: BeautifulSoup) -> List[Dict]:
        """Analyze form structures."""
        forms = []
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get'),
                'inputs': [],
                'buttons': []
            }
            
            # Analyze inputs
            for input_tag in form.find_all(['input', 'select', 'textarea']):
                input_data = {
                    'type': input_tag.get('type', 'text'),
                    'name': input_tag.get('name', ''),
                    'required': input_tag.get('required') is not None
                }
                form_data['inputs'].append(input_data)
            
            # Analyze buttons
            for button in form.find_all(['button', 'input[type="submit"]']):
                form_data['buttons'].append({
                    'type': button.get('type', 'submit'),
                    'text': button.text.strip() if button.text else button.get('value', '')
                })
            
            forms.append(form_data)
        
        return forms

    def _analyze_navigation(self, soup: BeautifulSoup) -> List[Dict]:
        """Analyze navigation elements."""
        nav_elements = []
        
        for nav in soup.find_all(['nav', 'header']):
            nav_data = {
                'items': [],
                'type': 'primary' if 'main-nav' in nav.get('class', []) else 'secondary'
            }
            
            for link in nav.find_all('a'):
                nav_data['items'].append({
                    'text': link.text.strip(),
                    'href': link.get('href', '#'),
                    'current': 'active' in link.get('class', [])
                })
            
            nav_elements.append(nav_data)
        
        return nav_elements

    def _analyze_dynamic_content(self) -> Dict:
        """Analyze dynamic content loading."""
        dynamic_content = {
            'infinite_scroll': False,
            'load_more': False
        }

        # Check for infinite scroll
        initial_height = self.driver.execute_script("return document.body.scrollHeight")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = self.driver.execute_script("return document.body.scrollHeight")
        
        if new_height > initial_height:
            dynamic_content['infinite_scroll'] = True

        # Check for load more buttons
        load_more = self.driver.find_elements(By.XPATH, 
            "//*[contains(text(), 'Load More') or contains(text(), 'Show More')]")
        if load_more:
            dynamic_content['load_more'] = True

        return dynamic_content

    def _get_page_metrics(self, soup: BeautifulSoup, load_time: float) -> Dict:
        """Get basic page metrics."""
        try:
            # Count basic elements
            images = len(soup.find_all('img'))
            scripts = len(soup.find_all('script'))
            styles = len(soup.find_all('link', rel='stylesheet'))

            # Get page title and meta description
            title = soup.title.string if soup.title else None
            meta_desc = soup.find('meta', {'name': 'description'})
            description = meta_desc['content'] if meta_desc else None

            return {
                'load_time': round(load_time, 2),
                'elements': {
                    'images': images,
                    'scripts': scripts,
                    'styles': styles,
                    'total': len(soup.find_all())
                },
                'meta': {
                    'title': title,
                    'has_description': bool(description),
                    'viewport': bool(soup.find('meta', {'name': 'viewport'}))
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting page metrics: {str(e)}")
            return {}