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

            # Load page with timeout and error handling
            try:
                self.driver.get(url)
                # Wait for page load with timeout
                self.wait.until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
            except TimeoutException:
                self.logger.warning("Page load timed out, proceeding with partial analysis")
            except WebDriverException as e:
                self.logger.error(f"WebDriver error: {str(e)}")
                raise

            load_time = time.time() - start_time

            # Get page source safely
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

            return {
                'structure': {
                    'forms': forms,
                    'navigation': navigation,
                    'dynamic_content': dynamic_content,
                    'page_metrics': page_metrics
                }
            }

        except Exception as e:
            self.logger.error(f"Error analyzing website: {str(e)}")
            raise

    def _analyze_forms(self, soup: BeautifulSoup) -> List[Dict]:
        """Analyze form structures with error handling."""
        forms = []
        try:
            for form in soup.find_all('form'):
                try:
                    form_data = {
                        'action': form.get('action', ''),
                        'method': form.get('method', 'get'),
                        'inputs': [],
                        'buttons': []
                    }
                    
                    # Analyze inputs
                    for input_tag in form.find_all(['input', 'select', 'textarea']):
                        try:
                            input_data = {
                                'type': input_tag.get('type', 'text'),
                                'name': input_tag.get('name', ''),
                                'required': input_tag.get('required') is not None
                            }
                            form_data['inputs'].append(input_data)
                        except Exception as e:
                            self.logger.warning(f"Error analyzing input: {str(e)}")
                            continue
                    
                    # Analyze buttons
                    for button in form.find_all(['button', 'input[type="submit"]']):
                        try:
                            form_data['buttons'].append({
                                'type': button.get('type', 'submit'),
                                'text': button.text.strip() if button.text else button.get('value', '')
                            })
                        except Exception as e:
                            self.logger.warning(f"Error analyzing button: {str(e)}")
                            continue
                    
                    forms.append(form_data)
                except Exception as e:
                    self.logger.warning(f"Error analyzing form: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error in form analysis: {str(e)}")
            return []
        
        return forms

    def _analyze_navigation(self, soup: BeautifulSoup) -> List[Dict]:
        """Analyze navigation elements with error handling."""
        nav_elements = []
        try:
            for nav in soup.find_all(['nav', 'header']):
                try:
                    nav_data = {
                        'items': [],
                        'type': 'primary' if 'main-nav' in nav.get('class', []) else 'secondary'
                    }
                    
                    for link in nav.find_all('a'):
                        try:
                            nav_data['items'].append({
                                'text': link.text.strip(),
                                'href': link.get('href', '#'),
                                'current': 'active' in link.get('class', [])
                            })
                        except Exception as e:
                            self.logger.warning(f"Error analyzing navigation link: {str(e)}")
                            continue
                    
                    nav_elements.append(nav_data)
                except Exception as e:
                    self.logger.warning(f"Error analyzing navigation element: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error in navigation analysis: {str(e)}")
            return []
        
        return nav_elements

    def _analyze_dynamic_content(self) -> Dict:
        """Analyze dynamic content loading with error handling."""
        dynamic_content = {
            'infinite_scroll': False,
            'load_more': False
        }

        try:
            # Check for infinite scroll
            try:
                initial_height = self.driver.execute_script("return document.body.scrollHeight")
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Wait for potential content load
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                
                if new_height > initial_height:
                    dynamic_content['infinite_scroll'] = True
            except Exception as e:
                self.logger.warning(f"Error checking infinite scroll: {str(e)}")

            # Check for load more buttons
            try:
                load_more = self.driver.find_elements(By.XPATH, 
                    "//*[contains(text(), 'Load More') or contains(text(), 'Show More')]")
                if load_more:
                    dynamic_content['load_more'] = True
            except Exception as e:
                self.logger.warning(f"Error checking load more buttons: {str(e)}")

        except Exception as e:
            self.logger.error(f"Error in dynamic content analysis: {str(e)}")

        return dynamic_content

    def _get_page_metrics(self, soup: BeautifulSoup, load_time: float) -> Dict:
        """Get basic page metrics with error handling."""
        metrics = {
            'load_time': round(load_time, 2),
            'elements': {
                'images': 0,
                'scripts': 0,
                'styles': 0,
                'total': 0
            },
            'meta': {
                'title': None,
                'has_description': False,
                'viewport': False
            }
        }

        try:
            # Count elements
            metrics['elements']['images'] = len(soup.find_all('img'))
            metrics['elements']['scripts'] = len(soup.find_all('script'))
            metrics['elements']['styles'] = len(soup.find_all('link', rel='stylesheet'))
            metrics['elements']['total'] = len(soup.find_all())

            # Get meta information
            try:
                metrics['meta']['title'] = soup.title.string if soup.title else None
            except:
                pass

            try:
                metrics['meta']['has_description'] = bool(soup.find('meta', {'name': 'description'}))
            except:
                pass

            try:
                metrics['meta']['viewport'] = bool(soup.find('meta', {'name': 'viewport'}))
            except:
                pass

        except Exception as e:
            self.logger.error(f"Error getting page metrics: {str(e)}")

        return metrics