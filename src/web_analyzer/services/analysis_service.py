"""
Service layer for coordinating web analysis operations with enhanced capabilities.
"""
from typing import Dict, Optional, List
from bs4 import BeautifulSoup
from selenium import webdriver
import logging

from src.web_analyzer.interfaces.tag_analyzer import SmartTagAnalyzer
from src.web_analyzer.interfaces.structure_analyzer import EnhancedStructureAnalyzer

class WebAnalysisService:
    """Service for coordinating web analysis operations."""

    def __init__(self, driver: webdriver.Remote):
        """Initialize the analysis service with required analyzers."""
        self.driver = driver
        self.logger = logging.getLogger(__name__)
        self.tag_analyzer = SmartTagAnalyzer()
        self.structure_analyzer = EnhancedStructureAnalyzer()
        self.current_page_source = None
        self.current_soup = None
        self.last_analysis = None

    def analyze_page(self, url: str) -> Dict:
        """
        Perform comprehensive page analysis using enhanced analyzers.
        
        Args:
            url: The URL to analyze
            
        Returns:
            Dict containing analysis results
        """
        try:
            self.logger.info(f"Starting enhanced analysis of {url}")
            
            # Load and parse page
            self._load_page(url)
            if not self.current_soup:
                raise ValueError("Failed to parse page content")

            # Perform analysis using enhanced components
            analysis_result = {
                'url': url,
                'tag_analysis': self._perform_tag_analysis(),
                'structure_analysis': self._perform_structure_analysis(),
                'element_suggestions': self._generate_element_suggestions(),
                'test_recommendations': self._generate_test_recommendations()
            }

            self.last_analysis = analysis_result
            return analysis_result

        except Exception as e:
            self.logger.error(f"Error during page analysis: {str(e)}")
            return {
                'error': str(e),
                'url': url,
                'tag_analysis': {},
                'structure_analysis': {},
                'element_suggestions': [],
                'test_recommendations': []
            }

    def get_element_suggestions(self, human_input: str) -> List[Dict]:
        """
        Generate element suggestions based on human input.
        
        Args:
            human_input: Natural language description of desired elements
            
        Returns:
            List of suggested elements with selectors
        """
        if not self.last_analysis:
            return []

        try:
            # Clean and normalize input
            search_terms = self._normalize_input(human_input)
            
            suggestions = []
            analyzed_tags = self.last_analysis['tag_analysis']
            
            # Check semantic matches
            if 'semantic_structure' in analyzed_tags:
                suggestions.extend(
                    self._find_semantic_matches(search_terms, analyzed_tags['semantic_structure'])
                )
            
            # Check pattern matches
            if 'tag_patterns' in analyzed_tags:
                suggestions.extend(
                    self._find_pattern_matches(search_terms, analyzed_tags['tag_patterns'])
                )
            
            # Check attribute matches
            if 'key_attributes' in analyzed_tags:
                suggestions.extend(
                    self._find_attribute_matches(search_terms, analyzed_tags['key_attributes'])
                )

            return self._prioritize_suggestions(suggestions)

        except Exception as e:
            self.logger.error(f"Error generating element suggestions: {str(e)}")
            return []

    def get_test_scenarios(self, element_type: str) -> List[Dict]:
        """
        Generate test scenarios for specific element types.
        
        Args:
            element_type: Type of element to generate scenarios for
            
        Returns:
            List of recommended test scenarios
        """
        if not self.last_analysis:
            return []

        try:
            scenarios = []
            
            # Get relevant analysis data
            structure_data = self.last_analysis['structure_analysis']
            
            if 'layout' in structure_data:
                scenarios.extend(
                    self._generate_layout_scenarios(element_type, structure_data['layout'])
                )
            
            if 'components' in structure_data:
                scenarios.extend(
                    self._generate_component_scenarios(element_type, structure_data['components'])
                )
            
            if 'dynamic_content' in structure_data:
                scenarios.extend(
                    self._generate_dynamic_scenarios(element_type, structure_data['dynamic_content'])
                )

            return scenarios

        except Exception as e:
            self.logger.error(f"Error generating test scenarios: {str(e)}")
            return []

    def _load_page(self, url: str) -> None:
        """Load and parse page content."""
        try:
            self.driver.get(url)
            self.current_page_source = self.driver.page_source
            self.current_soup = BeautifulSoup(self.current_page_source, 'lxml')
        except Exception as e:
            self.logger.error(f"Error loading page: {str(e)}")
            raise

    def _perform_tag_analysis(self) -> Dict:
        """Perform enhanced tag analysis."""
        return self.tag_analyzer.analyze_tags(self.current_soup)

    def _perform_structure_analysis(self) -> Dict:
        """Perform enhanced structure analysis."""
        return self.structure_analyzer.analyze_structure(self.current_soup, self.driver)

    def _generate_element_suggestions(self) -> List[Dict]:
        """Generate smart element suggestions based on analysis."""
        suggestions = []
        
        # Add suggestions based on tag analysis
        if 'semantic_structure' in self.last_analysis['tag_analysis']:
            semantic_data = self.last_analysis['tag_analysis']['semantic_structure']
            
            # Add header suggestions
            if 'header_elements' in semantic_data:
                for header in semantic_data['header_elements'].get('hierarchy', []):
                    suggestions.append({
                        'type': 'header',
                        'selector': f"h{header}",
                        'confidence': 0.9,
                        'description': f"Level {header} heading"
                    })

            # Add navigation suggestions
            if 'navigation_elements' in semantic_data:
                nav_data = semantic_data['navigation_elements']
                if nav_data.get('primary_nav'):
                    suggestions.append({
                        'type': 'navigation',
                        'selector': 'nav[role="navigation"]',
                        'confidence': 0.95,
                        'description': "Primary navigation"
                    })

        # Add suggestions based on structure analysis
        if 'components' in self.last_analysis['structure_analysis']:
            component_data = self.last_analysis['structure_analysis']['components']
            
            # Add interactive element suggestions
            if 'interactive_elements' in component_data:
                for element in component_data['interactive_elements']:
                    suggestions.append({
                        'type': 'interactive',
                        'selector': element.get('selector', ''),
                        'confidence': 0.85,
                        'description': element.get('description', '')
                    })

        return suggestions

    def _generate_test_recommendations(self) -> List[Dict]:
        """Generate test recommendations based on analysis."""
        recommendations = []
        
        # Add recommendations based on structure analysis
        if 'dynamic_content' in self.last_analysis['structure_analysis']:
            dynamic_data = self.last_analysis['structure_analysis']['dynamic_content']
            
            # Add mutation-based recommendations
            if 'mutations' in dynamic_data:
                mutation_info = dynamic_data['mutations']
                if mutation_info.get('total_mutations', 0) > 0:
                    recommendations.append({
                        'type': 'dynamic_content',
                        'priority': 'high',
                        'description': "Test dynamic content updates",
                        'steps': [
                            "Monitor DOM mutations",
                            "Verify content updates",
                            "Check state consistency"
                        ]
                    })

        # Add recommendations based on tag analysis
        if 'tag_patterns' in self.last_analysis['tag_analysis']:
            pattern_data = self.last_analysis['tag_analysis']['tag_patterns']
            
            # Add form testing recommendations
            if 'forms' in pattern_data:
                for form in pattern_data['forms']:
                    recommendations.append({
                        'type': 'form_validation',
                        'priority': 'high',
                        'description': f"Test form with {len(form.get('inputs', []))} fields",
                        'steps': [
                            "Validate required fields",
                            "Test input constraints",
                            "Verify form submission"
                        ]
                    })

        return recommendations

    def _normalize_input(self, input_text: str) -> List[str]:
        """Normalize and tokenize human input."""
        # Convert to lowercase and split into words
        words = input_text.lower().split()
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to'}
        words = [w for w in words if w not in stop_words]
        
        return words

    def _find_semantic_matches(self, search_terms: List[str], semantic_data: Dict) -> List[Dict]:
        """Find matches based on semantic structure."""
        matches = []
        
        if 'header_elements' in semantic_data:
            for header in semantic_data['header_elements'].get('hierarchy', []):
                if any(term in header.lower() for term in search_terms):
                    matches.append({
                        'type': 'semantic',
                        'selector': f"h{header}",
                        'confidence': 0.8
                    })
        
        return matches

    def _find_pattern_matches(self, search_terms: List[str], pattern_data: Dict) -> List[Dict]:
        """Find matches based on pattern analysis."""
        matches = []
        
        if 'lists' in pattern_data:
            for list_pattern in pattern_data['lists']:
                if any(term in str(list_pattern).lower() for term in search_terms):
                    matches.append({
                        'type': 'pattern',
                        'selector': f"{list_pattern['type']}",
                        'confidence': 0.7
                    })
        
        return matches

    def _find_attribute_matches(self, search_terms: List[str], attribute_data: Dict) -> List[Dict]:
        """Find matches based on attributes."""
        matches = []
        
        if 'data_attributes' in attribute_data:
            for attr, count in attribute_data['data_attributes'].items():
                if any(term in attr.lower() for term in search_terms):
                    matches.append({
                        'type': 'attribute',
                        'selector': f"[{attr}]",
                        'confidence': 0.6
                    })
        
        return matches

    def _prioritize_suggestions(self, suggestions: List[Dict]) -> List[Dict]:
        """Prioritize and sort element suggestions."""
        # Sort by confidence score
        sorted_suggestions = sorted(
            suggestions,
            key=lambda x: x.get('confidence', 0),
            reverse=True
        )
        
        # Limit to top 5 suggestions
        return sorted_suggestions[:5]