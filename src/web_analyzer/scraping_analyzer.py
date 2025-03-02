"""
Scraping Analyzer module for analyzing webpage structure for scraping purposes.
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

class ScrapingAnalyzer:
    def __init__(self, driver: webdriver.Remote):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.logger = logging.getLogger(__name__)
        self.page_source = None
        self.soup = None

    def analyze_page(self, url: str) -> Dict:
        """Analyze webpage for scraping opportunities."""
        try:
            self.logger.info(f"Starting scraping analysis of {url}")

            # Load page with error handling
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

            # Parse page content safely
            try:
                self.page_source = self.driver.page_source
                self.soup = BeautifulSoup(self.page_source, 'lxml')
            except Exception as e:
                self.logger.error(f"Error parsing page source: {str(e)}")
                raise

            # Perform analysis with error handling
            try:
                page_structure = self._analyze_page_structure()
                recommended_selectors = self._generate_selectors()

                return {
                    'page_structure': page_structure,
                    'recommended_selectors': recommended_selectors
                }
            except Exception as e:
                self.logger.error(f"Error in page analysis: {str(e)}")
                raise

        except Exception as e:
            self.logger.error(f"Error analyzing webpage: {str(e)}")
            raise

    def _analyze_page_structure(self) -> Dict:
        """Analyze page structure with error handling."""
        structure = {
            'tags': {},
            'repeated_patterns': [],
            'data_attributes': [],
            'common_classes': {}
        }

        try:
            # Count tags
            for tag in self.soup.find_all():
                tag_name = tag.name
                structure['tags'][tag_name] = structure['tags'].get(tag_name, 0) + 1

            # Find repeated patterns
            self._find_repeated_patterns(structure)

            # Analyze data attributes
            self._analyze_data_attributes(structure)

            # Find common classes
            self._analyze_common_classes(structure)

        except Exception as e:
            self.logger.error(f"Error analyzing page structure: {str(e)}")

        return structure

    def _find_repeated_patterns(self, structure: Dict) -> None:
        """Find repeated element patterns safely."""
        try:
            # Look for common list patterns
            lists = self.soup.find_all(['ul', 'ol'])
            for lst in lists:
                if len(lst.find_all('li')) > 2:
                    structure['repeated_patterns'].append({
                        'type': 'list',
                        'selector': self._get_unique_selector(lst),
                        'items': len(lst.find_all('li'))
                    })

            # Look for grid/card patterns
            common_containers = self.soup.find_all(['div', 'section'])
            for container in common_containers:
                children = container.find_all(recursive=False)
                if len(children) > 2:
                    similar_children = self._check_similar_structure(children)
                    if similar_children:
                        structure['repeated_patterns'].append({
                            'type': 'grid',
                            'selector': self._get_unique_selector(container),
                            'items': len(children)
                        })

        except Exception as e:
            self.logger.warning(f"Error finding repeated patterns: {str(e)}")

    def _analyze_data_attributes(self, structure: Dict) -> None:
        """Analyze data attributes safely."""
        try:
            for tag in self.soup.find_all():
                for attr in tag.attrs:
                    if attr.startswith('data-'):
                        if attr not in structure['data_attributes']:
                            structure['data_attributes'].append(attr)

        except Exception as e:
            self.logger.warning(f"Error analyzing data attributes: {str(e)}")

    def _analyze_common_classes(self, structure: Dict) -> None:
        """Analyze common classes safely."""
        try:
            class_count = {}
            for tag in self.soup.find_all(class_=True):
                for class_name in tag.get('class', []):
                    class_count[class_name] = class_count.get(class_name, 0) + 1

            # Filter for commonly used classes
            structure['common_classes'] = {
                cls: count for cls, count in class_count.items()
                if count > 2  # Classes used more than twice
            }

        except Exception as e:
            self.logger.warning(f"Error analyzing common classes: {str(e)}")

    def _generate_selectors(self) -> List[Dict]:
        """Generate recommended CSS selectors safely."""
        selectors = []
        try:
            # Handle lists
            self._generate_list_selectors(selectors)
            
            # Handle forms
            self._generate_form_selectors(selectors)
            
            # Handle tables
            self._generate_table_selectors(selectors)
            
            # Handle common containers
            self._generate_container_selectors(selectors)

        except Exception as e:
            self.logger.error(f"Error generating selectors: {str(e)}")

        return selectors

    def _generate_list_selectors(self, selectors: List) -> None:
        """Generate selectors for lists safely."""
        try:
            lists = self.soup.find_all(['ul', 'ol'])
            for lst in lists:
                if len(lst.find_all('li')) > 2:
                    selector = self._get_unique_selector(lst)
                    if selector:
                        selectors.append({
                            'purpose': 'List Items',
                            'selector': f"{selector} > li",
                            'note': f"Found {len(lst.find_all('li'))} items"
                        })
        except Exception as e:
            self.logger.warning(f"Error generating list selectors: {str(e)}")

    def _generate_form_selectors(self, selectors: List) -> None:
        """Generate selectors for forms safely."""
        try:
            forms = self.soup.find_all('form')
            for form in forms:
                selector = self._get_unique_selector(form)
                if selector:
                    selectors.append({
                        'purpose': 'Form Fields',
                        'selector': f"{selector} input, {selector} select, {selector} textarea",
                        'note': "Form input fields"
                    })
        except Exception as e:
            self.logger.warning(f"Error generating form selectors: {str(e)}")

    def _generate_table_selectors(self, selectors: List) -> None:
        """Generate selectors for tables safely."""
        try:
            tables = self.soup.find_all('table')
            for table in tables:
                selector = self._get_unique_selector(table)
                if selector:
                    selectors.append({
                        'purpose': 'Table Data',
                        'selector': f"{selector} tr",
                        'note': "Table rows"
                    })
        except Exception as e:
            self.logger.warning(f"Error generating table selectors: {str(e)}")

    def _generate_container_selectors(self, selectors: List) -> None:
        """Generate selectors for common containers safely."""
        try:
            # Look for article containers
            articles = self.soup.find_all('article')
            if articles:
                selectors.append({
                    'purpose': 'Article Content',
                    'selector': 'article',
                    'note': f"Found {len(articles)} articles"
                })

            # Look for card-like containers
            cards = self.soup.find_all(class_=re.compile(r'card|item|product'))
            if cards:
                selectors.append({
                    'purpose': 'Content Cards',
                    'selector': '.' + cards[0].get('class')[0],
                    'note': f"Found {len(cards)} card elements"
                })

        except Exception as e:
            self.logger.warning(f"Error generating container selectors: {str(e)}")

    def _get_unique_selector(self, element) -> str:
        """Generate a unique CSS selector for an element safely."""
        try:
            # Try ID first
            if element.get('id'):
                return f"#{element['id']}"

            # Try unique class combination
            classes = element.get('class', [])
            if classes:
                class_selector = '.'.join(classes)
                if len(self.soup.select(f'.{class_selector}')) == 1:
                    return f'.{class_selector}'

            # Build path-based selector
            path = []
            current = element
            for _ in range(3):  # Limit depth to avoid too complex selectors
                if not current.parent:
                    break
                siblings = current.parent.find_all(current.name, recursive=False)
                if len(siblings) == 1:
                    path.append(current.name)
                else:
                    index = siblings.index(current) + 1
                    path.append(f"{current.name}:nth-child({index})")
                current = current.parent
                if current.get('id'):
                    path.append(f"#{current['id']}")
                    break

            return ' > '.join(reversed(path))

        except Exception as e:
            self.logger.warning(f"Error generating unique selector: {str(e)}")
            return ""

    def _check_similar_structure(self, elements) -> bool:
        """Check if elements have similar structure safely."""
        try:
            if len(elements) < 2:
                return False

            # Get tag structure of first element
            first_structure = self._get_element_structure(elements[0])
            
            # Compare with other elements
            return all(
                self._get_element_structure(elem) == first_structure
                for elem in elements[1:]
            )

        except Exception as e:
            self.logger.warning(f"Error checking element structure: {str(e)}")
            return False

    def _get_element_structure(self, element) -> str:
        """Get string representation of element structure safely."""
        try:
            return ''.join(
                child.name for child in element.find_all(recursive=False)
            )
        except Exception as e:
            self.logger.warning(f"Error getting element structure: {str(e)}")
            return ""