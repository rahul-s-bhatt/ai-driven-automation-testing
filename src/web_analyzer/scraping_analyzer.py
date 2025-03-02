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

from src.web_analyzer.services.analysis_service import WebAnalysisService

class ScrapingAnalyzer:
    def __init__(self, driver: webdriver.Remote):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.logger = logging.getLogger(__name__)
        self.page_source = None
        self.soup = None
        # Initialize the enhanced analysis service
        self.analysis_service = WebAnalysisService(driver)

    def analyze_page(self, url: str) -> Dict:
        """
        Analyze webpage for scraping opportunities using enhanced analysis service.
        Maintains backward compatibility while providing enhanced analysis.
        """
        try:
            self.logger.info(f"Starting enhanced scraping analysis of {url}")
            
            # Use enhanced analysis service
            analysis_result = self.analysis_service.analyze_page(url)
            
            # Update instance variables for backward compatibility
            self.page_source = self.driver.page_source
            self.soup = BeautifulSoup(self.page_source, 'lxml')
            
            # Transform enhanced analysis into original format
            return self._transform_analysis_result(analysis_result)
            
        except Exception as e:
            self.logger.error(f"Error analyzing webpage: {str(e)}")
            raise

    def _transform_analysis_result(self, enhanced_result: Dict) -> Dict:
        """Transform enhanced analysis result to maintain backward compatibility."""
        try:
            # Extract relevant data from enhanced analysis
            tag_analysis = enhanced_result.get('tag_analysis', {})
            structure_analysis = enhanced_result.get('structure_analysis', {})
            
            # Create backward-compatible structure
            page_structure = {
                'tags': tag_analysis.get('tag_patterns', {}).get('counts', {}),
                'repeated_patterns': self._extract_repeated_patterns(tag_analysis),
                'data_attributes': self._extract_data_attributes(tag_analysis),
                'common_classes': self._extract_common_classes(tag_analysis)
            }
            
            # Create backward-compatible selectors
            recommended_selectors = self._extract_selectors(
                enhanced_result.get('element_suggestions', [])
            )
            
            return {
                'page_structure': page_structure,
                'recommended_selectors': recommended_selectors
            }
            
        except Exception as e:
            self.logger.error(f"Error transforming analysis result: {str(e)}")
            return {
                'page_structure': self._analyze_page_structure(),  # Fallback to original
                'recommended_selectors': self._generate_selectors()  # Fallback to original
            }

    def _extract_repeated_patterns(self, tag_analysis: Dict) -> List[Dict]:
        """Extract repeated patterns from enhanced analysis."""
        patterns = []
        
        # Extract list patterns
        for list_pattern in tag_analysis.get('tag_patterns', {}).get('lists', []):
            if list_pattern.get('items', 0) > 2:
                patterns.append({
                    'type': 'list',
                    'selector': f"{list_pattern.get('type', 'ul')}",
                    'items': list_pattern.get('items', 0)
                })
        
        # Extract grid patterns
        for grid_pattern in tag_analysis.get('tag_patterns', {}).get('grids', []):
            patterns.append({
                'type': 'grid',
                'selector': grid_pattern.get('selector', ''),
                'items': grid_pattern.get('children_count', 0)
            })
            
        return patterns

    def _extract_data_attributes(self, tag_analysis: Dict) -> List[str]:
        """Extract data attributes from enhanced analysis."""
        attributes = []
        key_attributes = tag_analysis.get('key_attributes', {})
        data_attrs = key_attributes.get('data_attributes', {})
        
        for attr in data_attrs:
            if attr.startswith('data-'):
                attributes.append(attr)
                
        return attributes

    def _extract_common_classes(self, tag_analysis: Dict) -> Dict[str, int]:
        """Extract common classes from enhanced analysis."""
        classes = {}
        class_patterns = tag_analysis.get('key_attributes', {}).get('class_patterns', {})
        
        # Filter for commonly used classes (used more than twice)
        return {
            cls: count for cls, count in class_patterns.items()
            if count > 2
        }

    def _extract_selectors(self, suggestions: List[Dict]) -> List[Dict]:
        """Convert enhanced suggestions to backward-compatible selectors."""
        selectors = []
        
        for suggestion in suggestions:
            selector_type = suggestion.get('type', '')
            if selector_type == 'list':
                selectors.append({
                    'purpose': 'List Items',
                    'selector': f"{suggestion.get('selector', '')} > li",
                    'note': suggestion.get('description', 'List elements')
                })
            elif selector_type == 'form':
                selectors.append({
                    'purpose': 'Form Fields',
                    'selector': suggestion.get('selector', ''),
                    'note': suggestion.get('description', 'Form elements')
                })
            elif selector_type == 'grid':
                selectors.append({
                    'purpose': 'Grid Items',
                    'selector': suggestion.get('selector', ''),
                    'note': suggestion.get('description', 'Grid elements')
                })
                
        return selectors

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