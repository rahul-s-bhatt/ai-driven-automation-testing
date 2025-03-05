"""
Service layer for coordinating web analysis operations with enhanced capabilities.
"""
from typing import Dict, Optional, List
from bs4 import BeautifulSoup
from selenium import webdriver
import logging
from pathlib import Path
from datetime import datetime

from src.web_analyzer.interfaces.tag_analyzer import SmartTagAnalyzer
from src.web_analyzer.interfaces.structure_analyzer import EnhancedStructureAnalyzer
from src.test_engine.dual_mode.parser import DualModeParser
from src.test_engine.dual_mode.generators import HumanInstructionsGenerator, AutomationGenerator

class WebAnalysisService:
    """Service for coordinating web analysis operations."""

    def __init__(self, driver: webdriver.Remote):
        """Initialize the analysis service with required analyzers."""
        self.driver = driver
        self.logger = logging.getLogger(__name__)
        
        # Configure logger
        if not self.logger.handlers:
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)  # Reduce logging verbosity
            
        self.logger.info("Initializing WebAnalysisService")
        
        try:
            self.tag_analyzer = SmartTagAnalyzer()
            self.structure_analyzer = EnhancedStructureAnalyzer()
            self.current_page_source = None
            self.current_soup = None
            self.last_analysis = None

            # Initialize dual-mode components
            self.human_generator = HumanInstructionsGenerator()
            self.automation_generator = AutomationGenerator()
            
            self.logger.info("Successfully initialized all analyzers and components")
        except Exception as e:
            self.logger.error(f"Error initializing service: {str(e)}", exc_info=True)
            raise

    def analyze_page(self, url: str) -> Dict:
        """
        Perform comprehensive page analysis using enhanced analyzers.
        
        Args:
            url: The URL to analyze
            
        Returns:
            Dict containing analysis results including dual-mode tests
        """
        try:
            self.logger.info("Starting analysis")
            
            # Load and parse page
            self._load_page(url)
            if not self.current_soup:
                raise ValueError("Failed to parse page content")

            # Perform analysis using enhanced components
            # Get all analysis results
            tag_analysis = self._perform_tag_analysis()
            structure_analysis = self._perform_structure_analysis()
            
            # Create properly structured analysis result with metrics
            analysis_result = {
                'url': url,
                'tag_analysis': tag_analysis or {},
                'structure_analysis': structure_analysis or {'structure': {}},
                'analysis': {
                    'structure': structure_analysis or {}
                },
                'element_suggestions': self._generate_element_suggestions() or [],
                'test_recommendations': self._generate_test_recommendations() or [],
                'dual_mode_tests': self._generate_dual_mode_tests() or {}
            }

            # Ensure the nested structure is complete even if analysis failed
            structure_data = analysis_result.get('structure_analysis', {}).get('structure', {})
            if not structure_data.get('page_metrics'):
                structure_data['page_metrics'] = {
                    'performance': {
                        'load_time': 0,
                        'dom_ready': 0,
                        'resources_loaded': 0
                    },
                    'accessibility': {},
                    'dynamic_content': {},
                    'component_metrics': {
                        'total_components': 0,
                        'interactive_elements': 0,
                        'forms': 0
                    }
                }
            
            self.last_analysis = analysis_result
            return analysis_result

        except Exception as e:
            self.logger.error(f"Error during page analysis: {str(e)}")
            error_result = {
                'error': str(e),
                'url': url,
                'tag_analysis': {},
                'structure_analysis': {
                    'structure': {
                        'layout': {},
                        'components': {
                            'reusable_components': [],
                            'interactive_elements': [],
                            'forms': []
                        },
                        'dynamic_content': {},
                        'relationships': {},
                        'accessibility': {}
                    }
                },
                'analysis': {
                    'structure': {
                        'page_metrics': {
                            'load_time': 0,
                            'dom_ready': 0,
                            'resources_loaded': 0,
                            'element_counts': {}
                        },
                        'layout': {},
                        'components': {
                            'reusable_components': [],
                            'interactive_elements': [],
                            'forms': []
                        },
                        'dynamic_content': {},
                        'relationships': {},
                        'accessibility': {}
                    }
                },
                'element_suggestions': [],
                'test_recommendations': [],
                'dual_mode_tests': {}
            }
            self.last_analysis = error_result  # Ensure last_analysis is also updated
            self.logger.debug(f"Returning error result with complete structure")
            return error_result

    def _generate_dual_mode_tests(self) -> Dict:
        """Generate both human and automated test scenarios based on analysis."""
        if not self.last_analysis:
            return {}

        scenarios = []

        # Generate scenarios based on element suggestions
        for suggestion in self.last_analysis.get('element_suggestions', []):
            scenario = self._create_element_test_scenario(suggestion)
            if scenario:
                scenarios.append(scenario)

        # Generate scenarios based on structure analysis
        structure_data = self.last_analysis.get('structure_analysis', {}).get('structure', {})
        if 'components' in structure_data:
            for scenario in self._create_component_test_scenarios(structure_data['components']):
                scenarios.append(scenario)

        if not scenarios:
            return {}

        # Generate both human and automated outputs
        output_dir = Path('test_output/analysis')
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        human_output = self.human_generator.generate_test_plan(scenarios, str(output_dir))
        automation_output = self.automation_generator.generate_test_suite(scenarios, str(output_dir))

        return {
            'scenarios': scenarios,
            'outputs': {
                'human_instructions': human_output,
                'automation_script': automation_output
            }
        }

    def _create_element_test_scenario(self, suggestion: Dict) -> Optional[Dict]:
        """Create a test scenario for a suggested element."""
        if not suggestion.get('selector'):
            return None

        return {
            'name': f"Test {suggestion['type']} Element",
            'description': suggestion.get('description', ''),
            'tags': [suggestion['type'], 'element-test'],
            'modes': {
                'human': {
                    'preparation': "Ensure the page is loaded and visible",
                    'success_criteria': f"The {suggestion['type']} element should be visible and interactive"
                },
                'automation': {
                    'setup': {
                        'dependencies': ['selenium', 'pytest'],
                        'test_data': {}
                    }
                }
            },
            'steps': [
                {
                    'description': f"Verify {suggestion['type']} element presence",
                    'action': 'verify',
                    'target': suggestion['selector'],
                    'human_instruction': f"Check if the {suggestion['type']} element is visible",
                    'automation': {
                        'selector': suggestion['selector'],
                        'wait_for': 'element_visible'
                    }
                }
            ]
        }

    def _create_component_test_scenarios(self, components: Dict) -> List[Dict]:
        """Create test scenarios for identified components."""
        scenarios = []

        if 'interactive_elements' in components:
            for element in components['interactive_elements']:
                scenario = {
                    'name': f"Test {element.get('description', 'Interactive')} Component",
                    'description': f"Verify functionality of {element.get('description', 'component')}",
                    'tags': ['component', 'interactive'],
                    'modes': {
                        'human': {
                            'preparation': "Ensure the component is in its initial state",
                            'success_criteria': "Component should respond to interactions correctly"
                        },
                        'automation': {
                            'setup': {
                                'dependencies': ['selenium', 'pytest'],
                                'test_data': {}
                            }
                        }
                    },
                    'steps': [
                        {
                            'description': "Verify component presence",
                            'action': 'verify',
                            'target': element.get('selector', ''),
                            'human_instruction': f"Locate the {element.get('description', 'component')}",
                            'automation': {
                                'selector': element.get('selector', ''),
                                'wait_for': 'element_visible'
                            }
                        }
                    ]
                }
                scenarios.append(scenario)

        return scenarios

    def get_element_suggestions(self, human_input: str) -> List[Dict]:
        """Generate element suggestions based on human input."""
        if not self.last_analysis:
            return []

        try:
            search_terms = self._normalize_input(human_input)
            suggestions = []
            analyzed_tags = self.last_analysis.get('tag_analysis', {})
            
            if analyzed_tags:
                semantic_data = analyzed_tags.get('semantic_structure', {})
                if semantic_data:
                    suggestions.extend(
                        self._find_semantic_matches(search_terms, semantic_data)
                    )
                
                pattern_data = analyzed_tags.get('tag_patterns', {})
                if pattern_data:
                    suggestions.extend(
                        self._find_pattern_matches(search_terms, pattern_data)
                    )
                
                attribute_data = analyzed_tags.get('key_attributes', {})
                if attribute_data:
                    suggestions.extend(
                        self._find_attribute_matches(search_terms, attribute_data)
                    )

            return self._prioritize_suggestions(suggestions)

        except Exception as e:
            self.logger.error(f"Error generating element suggestions: {str(e)}")
            return []

    def get_test_scenarios(self, element_type: str) -> List[Dict]:
        """Generate test scenarios for specific element types."""
        if not self.last_analysis:
            return []

        try:
            scenarios = []
            structure_data = self.last_analysis.get('structure_analysis', {}).get('structure', {})
            
            if structure_data:
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
            self.logger.debug(f"Attempting to load URL: {url}")
            self.driver.get(url)
            
            # Wait for page load
            self.logger.debug("Waiting for page to load completely...")
            self.driver.execute_script("return document.readyState") == 'complete'
            
            self.current_page_source = self.driver.page_source
            if not self.current_page_source:
                raise ValueError("Empty page source received")
                
            self.logger.debug("Parsing page content with BeautifulSoup")
            self.current_soup = BeautifulSoup(self.current_page_source, 'lxml')
            
            if not self.current_soup.find():
                raise ValueError("BeautifulSoup parser returned empty document")
                
            self.logger.debug("Page successfully loaded and parsed")
            
        except Exception as e:
            self.logger.error("Error loading page", exc_info=False)
            self.current_page_source = None
            self.current_soup = None
            raise

    def _perform_tag_analysis(self) -> Dict:
        """Perform enhanced tag analysis."""
        default_tags = {
            'semantic_structure': {
                'header_elements': {'hierarchy': []},
                'navigation_elements': {'primary_nav': None}
            },
            'tag_patterns': {'forms': []},
            'key_attributes': {'data_attributes': {}}
        }
        
        try:
            result = self.tag_analyzer.analyze_tags(self.current_soup)
            if not result:
                self.logger.warning("Tag analyzer returned empty result")
                return default_tags
                
            # Ensure required structure exists
            for key, default_value in default_tags.items():
                if key not in result:
                    result[key] = default_value
                    
            return result
            
        except Exception as e:
            self.logger.error(f"Error in tag analysis: {str(e)}", exc_info=True)
            return default_tags

    def _perform_structure_analysis(self) -> Dict:
        """Perform enhanced structure analysis."""
        default_structure = {
            'page_metrics': {
                'performance': {
                    'load_time': 0,
                    'dom_ready': 0,
                    'resources_loaded': 0
                },
                'accessibility': {},
                'dynamic_content': {},
                'component_metrics': {
                    'total_components': 0,
                    'interactive_elements': 0,
                    'forms': 0
                }
            },
            'layout': {},
            'components': {
                'reusable_components': [],
                'interactive_elements': [],
                'forms': []
            },
            'dynamic_content': {},
            'relationships': {},
            'accessibility': {}
        }
        
        try:
            if not self.current_soup:
                self.logger.error("Cannot perform structure analysis: BeautifulSoup object is None")
                return default_structure
                
            if not self.current_soup.find():
                self.logger.error("Cannot perform structure analysis: Empty document")
                return default_structure
                
            self.logger.debug("Starting structure analysis...")
            result = self.structure_analyzer.analyze_structure(self.current_soup, self.driver)
            
            if result is None:
                self.logger.warning("Structure analyzer returned None")
                return default_structure
            
            # Ensure all required fields exist in the result
            for key in default_structure:
                if key not in result:
                    result[key] = default_structure[key]
                    
            self.logger.debug(f"Structure analysis completed successfully: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in structure analysis: {str(e)}", exc_info=True)
            return default_structure

    def _generate_element_suggestions(self) -> List[Dict]:
        """Generate smart element suggestions based on analysis."""
        suggestions = []
        
        if not self.last_analysis:
            return suggestions
            
        # Handle tag analysis suggestions
        tag_analysis = self.last_analysis.get('tag_analysis', {})
        if tag_analysis:
            semantic_data = tag_analysis.get('semantic_structure', {})
            
            # Process header elements
            header_elements = semantic_data.get('header_elements', {})
            for header in header_elements.get('hierarchy', []):
                suggestions.append({
                    'type': 'header',
                    'selector': f"h{header}",
                    'confidence': 0.9,
                    'description': f"Level {header} heading"
                })

            # Process navigation elements
            nav_data = semantic_data.get('navigation_elements', {})
            if nav_data.get('primary_nav'):
                suggestions.append({
                    'type': 'navigation',
                    'selector': 'nav[role="navigation"]',
                    'confidence': 0.95,
                    'description': "Primary navigation"
                })

        # Handle structure analysis suggestions
        structure_analysis = self.last_analysis.get('structure_analysis', {}).get('structure', {})
        if structure_analysis:
            component_data = structure_analysis.get('components', {})
            
            # Process interactive elements
            for element in component_data.get('interactive_elements', []):
                if element:  # Ensure element is not None
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
        
        if not self.last_analysis:
            return recommendations

        structure_analysis = self.last_analysis.get('structure_analysis', {}).get('structure', {})
        if structure_analysis:
            dynamic_data = structure_analysis.get('dynamic_content', {})
            
            mutation_info = dynamic_data.get('mutations', {})
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

        tag_analysis = self.last_analysis.get('tag_analysis', {})
        if tag_analysis:
            pattern_data = tag_analysis.get('tag_patterns', {})
            
            for form in pattern_data.get('forms', []):
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
        words = input_text.lower().split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to'}
        return [w for w in words if w not in stop_words]

    def _find_semantic_matches(self, search_terms: List[str], semantic_data: Dict) -> List[Dict]:
        """Find matches based on semantic structure."""
        matches = []
        
        header_elements = semantic_data.get('header_elements', {})
        for header in header_elements.get('hierarchy', []):
            if any(term in str(header).lower() for term in search_terms):
                matches.append({
                    'type': 'semantic',
                    'selector': f"h{header}",
                    'confidence': 0.8
                })
        
        return matches

    def _find_pattern_matches(self, search_terms: List[str], pattern_data: Dict) -> List[Dict]:
        """Find matches based on pattern analysis."""
        matches = []
        
        for list_pattern in pattern_data.get('lists', []):
            if any(term in str(list_pattern).lower() for term in search_terms):
                matches.append({
                    'type': 'pattern',
                    'selector': f"{list_pattern.get('type', '')}",
                    'confidence': 0.7
                })
        
        return matches

    def _find_attribute_matches(self, search_terms: List[str], attribute_data: Dict) -> List[Dict]:
        """Find matches based on attributes."""
        matches = []
        
        for attr, count in attribute_data.get('data_attributes', {}).items():
            if any(term in attr.lower() for term in search_terms):
                matches.append({
                    'type': 'attribute',
                    'selector': f"[{attr}]",
                    'confidence': 0.6
                })
        
        return matches

    def _prioritize_suggestions(self, suggestions: List[Dict]) -> List[Dict]:
        """Prioritize and sort element suggestions."""
        sorted_suggestions = sorted(
            suggestions,
            key=lambda x: x.get('confidence', 0),
            reverse=True
        )
        return sorted_suggestions[:5]

    def _generate_layout_scenarios(self, element_type: str, layout_data: Dict) -> List[Dict]:
        """Generate test scenarios for layout elements."""
        scenarios = []
        
        if not layout_data:
            return scenarios
            
        # Test responsive layout behavior
        if layout_data.get('layout_type') in ['grid', 'flexbox']:
            scenarios.append({
                'name': f"Test {layout_data['layout_type']} Layout Responsiveness",
                'description': f"Verify {layout_data['layout_type']} layout behavior across breakpoints",
                'priority': 'high',
                'steps': [
                    "Verify initial layout",
                    "Test layout at different viewport sizes",
                    "Check element alignment and spacing"
                ]
            })
        
        # Test region-specific scenarios
        for region in layout_data.get('regions', []):
            if region.get('type') == element_type:
                scenarios.append({
                    'name': f"Test {region['type']} Region Layout",
                    'description': f"Verify layout of {region['type']} region",
                    'priority': 'medium',
                    'steps': [
                        "Check region positioning",
                        "Verify content alignment",
                        "Test nested region behavior"
                    ]
                })
                
        return scenarios
    
    def _generate_component_scenarios(self, element_type: str, component_data: Dict) -> List[Dict]:
        """Generate test scenarios for UI components."""
        scenarios = []
        
        if not component_data:
            return scenarios
            
        # Test interactive elements
        for element in component_data.get('interactive_elements', []):
            if element.get('type') == element_type:
                scenarios.append({
                    'name': f"Test {element['type']} Interaction",
                    'description': f"Verify {element['type']} component behavior",
                    'priority': 'high',
                    'steps': [
                        "Test click/tap interaction",
                        "Verify state changes",
                        "Check accessibility features"
                    ]
                })
        
        # Test form components
        for form in component_data.get('forms', []):
            if form.get('type') == element_type:
                scenarios.append({
                    'name': f"Test {element_type} Form Component",
                    'description': "Verify form component functionality",
                    'priority': 'high',
                    'steps': [
                        "Test input validation",
                        "Verify form submission",
                        "Check error handling"
                    ]
                })
                
        return scenarios
    
    def _generate_dynamic_scenarios(self, element_type: str, dynamic_data: Dict) -> List[Dict]:
        """Generate test scenarios for dynamic content."""
        scenarios = []
        
        if not dynamic_data:
            return scenarios
            
        # Test mutation-based scenarios
        mutations = dynamic_data.get('mutations', {})
        if mutations.get('total_mutations', 0) > 0:
            scenarios.append({
                'name': f"Test Dynamic Content Updates for {element_type}",
                'description': "Verify dynamic content behavior",
                'priority': 'high',
                'steps': [
                    "Monitor content changes",
                    "Verify update frequency",
                    "Check data consistency"
                ]
            })
        
        # Test loading pattern scenarios
        loading = dynamic_data.get('loading_patterns', {})
        if loading.get('lazy_loading') or loading.get('infinite_scroll'):
            scenarios.append({
                'name': f"Test Loading Patterns for {element_type}",
                'description': "Verify content loading behavior",
                'priority': 'medium',
                'steps': [
                    "Test scroll-based loading",
                    "Verify lazy loading triggers",
                    "Check loading indicators"
                ]
            })
                
        return scenarios