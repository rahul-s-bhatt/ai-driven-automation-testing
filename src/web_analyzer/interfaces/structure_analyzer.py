"""
Interface and implementations for enhanced structure analysis functionality.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import logging
import time

class StructureAnalyzerInterface(ABC):
    """Interface for structure analysis implementations."""
    
    @abstractmethod
    def analyze_structure(self, soup: BeautifulSoup, driver: webdriver.Remote) -> Dict:
        """Analyze page structure and return detailed information."""
        pass

class EnhancedStructureAnalyzer(StructureAnalyzerInterface):
    """Enhanced structure analyzer with advanced pattern detection and dynamic content analysis."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._last_content_hash = None
        self._mutation_count = 0
        self._content_update_times = []

    def analyze_structure(self, soup: BeautifulSoup, driver: webdriver.Remote) -> Dict:
        """
        Perform enhanced structure analysis including:
        - Layout pattern detection
        - Component relationships
        - Dynamic content analysis
        - DOM mutation tracking
        """
        try:
            structure_info = {
                'layout': self._analyze_layout(soup),
                'components': self._analyze_components(soup),
                'dynamic_content': self._analyze_dynamic_content(driver),
                'relationships': self._analyze_relationships(soup),
                'accessibility': self._analyze_accessibility(soup)
            }
            return structure_info
        except Exception as e:
            self.logger.error(f"Error in structure analysis: {str(e)}")
            return {
                'error': str(e),
                'layout': {},
                'components': {},
                'dynamic_content': {},
                'relationships': {},
                'accessibility': {}
            }

    def _analyze_layout(self, soup: BeautifulSoup) -> Dict:
        """Analyze page layout patterns."""
        return {
            'layout_type': self._detect_layout_type(soup),
            'regions': self._identify_regions(soup),
            'hierarchy': self._analyze_hierarchy(soup),
            'breakpoints': self._detect_breakpoints(soup)
        }

    def _analyze_components(self, soup: BeautifulSoup) -> Dict:
        """Analyze component patterns and relationships."""
        return {
            'reusable_components': self._find_reusable_components(soup),
            'interactive_elements': self._find_interactive_elements(soup),
            'content_blocks': self._analyze_content_blocks(soup),
            'forms': self._analyze_form_components(soup)
        }

    def _analyze_dynamic_content(self, driver: webdriver.Remote) -> Dict:
        """Analyze dynamic content behavior."""
        return {
            'mutations': self._track_dom_mutations(driver),
            'loading_patterns': self._analyze_loading_patterns(driver),
            'ajax_patterns': self._detect_ajax_patterns(driver),
            'state_changes': self._analyze_state_changes(driver)
        }

    def _analyze_relationships(self, soup: BeautifulSoup) -> Dict:
        """Analyze relationships between components."""
        return {
            'parent_child': self._analyze_parent_child_relationships(soup),
            'sibling_relationships': self._analyze_sibling_relationships(soup),
            'containment': self._analyze_containment_patterns(soup),
            'dependencies': self._analyze_component_dependencies(soup)
        }

    def _analyze_sibling_relationships(self, soup: BeautifulSoup) -> List[Dict]:
        """Analyze sibling relationships between elements."""
        siblings = []
        for tag in soup.find_all():
            # Only analyze tags that have siblings
            if tag.next_sibling or tag.previous_sibling:
                sibling_info = {
                    'element': tag.name,
                    'siblings': [],
                    'pattern': ''
                }
                
                # Analyze previous siblings
                prev_sibling = tag.find_previous_sibling()
                if prev_sibling:
                    sibling_info['siblings'].append({
                        'type': 'previous',
                        'element': prev_sibling.name
                    })
                
                # Analyze next siblings
                next_sibling = tag.find_next_sibling()
                if next_sibling:
                    sibling_info['siblings'].append({
                        'type': 'next',
                        'element': next_sibling.name
                    })
                
                # Identify common sibling patterns
                if len(sibling_info['siblings']) > 0:
                    elements = [s['element'] for s in sibling_info['siblings']]
                    if all(e == elements[0] for e in elements):
                        sibling_info['pattern'] = 'repeated'
                    elif 'h' in tag.name and any('h' in s['element'] for s in sibling_info['siblings']):
                        sibling_info['pattern'] = 'heading-sequence'
                    elif tag.name in ['li', 'tr', 'td']:
                        sibling_info['pattern'] = 'list-or-table'
                    
                siblings.append(sibling_info)
        
        return siblings


    def _detect_layout_type(self, soup: BeautifulSoup) -> str:
        """Detect the primary layout system used."""
        layout_indicators = {
            'grid': ['display: grid', 'grid-template', 'grid-area'],
            'flexbox': ['display: flex', 'flex-direction', 'justify-content'],
            'float': ['float:', 'clear:'],
            'table': ['display: table', '<table']
        }
        
        style_tags = soup.find_all('style')
        inline_styles = [tag.get('style', '') for tag in soup.find_all()]
        
        layout_scores = {layout: 0 for layout in layout_indicators}
        
        # Check style tags
        for style in style_tags:
            for layout, indicators in layout_indicators.items():
                for indicator in indicators:
                    if indicator in style.text:
                        layout_scores[layout] += 1
        
        # Check inline styles
        for style in inline_styles:
            for layout, indicators in layout_indicators.items():
                for indicator in indicators:
                    if indicator in style:
                        layout_scores[layout] += 1
        
        # Get the most used layout system
        primary_layout = max(layout_scores.items(), key=lambda x: x[1])[0]
        return primary_layout if layout_scores[primary_layout] > 0 else 'standard'

    def _identify_regions(self, soup: BeautifulSoup) -> List[Dict]:
        """Identify and analyze distinct page regions."""
        regions = []
        region_tags = ['header', 'nav', 'main', 'article', 'aside', 'footer', 'section']
        
        for tag in soup.find_all(region_tags):
            region = {
                'type': tag.name,
                'role': tag.get('role', ''),
                'aria_label': tag.get('aria-label', ''),
                'children_count': len(tag.find_all()),
                'text_content': bool(tag.text.strip()),
                'has_headings': bool(tag.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
                'nested_regions': [t.name for t in tag.find_all(region_tags)]
            }
            regions.append(region)
        
        return regions

    def _analyze_hierarchy(self, soup: BeautifulSoup) -> Dict:
        """Analyze document hierarchy and structure."""
        return {
            'depth': self._calculate_max_depth(soup),
            'heading_structure': self._analyze_heading_structure(soup),
            'landmark_roles': self._find_landmark_roles(soup),
            'nesting_patterns': self._analyze_nesting_patterns(soup)
        }

    def _detect_breakpoints(self, soup: BeautifulSoup) -> List[Dict]:
        """Detect responsive design breakpoints."""
        breakpoints = []
        media_queries = []
        
        # Find all style tags and look for media queries
        for style in soup.find_all('style'):
            content = style.string
            if content:
                media_starts = [i for i in range(len(content)) if content.startswith('@media', i)]
                for start in media_starts:
                    query = self._extract_media_query(content[start:])
                    if query:
                        media_queries.append(query)
        
        # Process found media queries
        for query in media_queries:
            breakpoint = self._parse_media_query(query)
            if breakpoint:
                breakpoints.append(breakpoint)
        
        return breakpoints

    def _track_dom_mutations(self, driver: webdriver.Remote) -> Dict:
        """Track and analyze DOM mutations."""
        script = """
            let mutations = [];
            const observer = new MutationObserver(records => {
                mutations.push(...records.map(r => ({
                    type: r.type,
                    target: r.target.tagName,
                    addedNodes: r.addedNodes.length,
                    removedNodes: r.removedNodes.length,
                    timestamp: Date.now()
                })));
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true,
                attributes: true
            });
            
            return mutations;
        """
        
        try:
            # Initialize mutations array in window scope
            driver.execute_script("window.mutations = [];")
            # Set up mutation observer
            driver.execute_script(script)
            time.sleep(2)  # Wait for potential dynamic content
            final_mutations = driver.execute_script("return window.mutations;")
            
            return {
                'total_mutations': len(final_mutations),
                'mutation_types': self._analyze_mutation_types(final_mutations),
                'mutation_frequency': self._calculate_mutation_frequency(final_mutations),
                'affected_elements': self._analyze_affected_elements(final_mutations)
            }
        except Exception as e:
            self.logger.error(f"Error tracking DOM mutations: {str(e)}")
            return {}

    def _analyze_mutation_types(self, mutations: List[Dict]) -> Dict:
        """Analyze types of mutations that occurred."""
        type_counts = {}
        for mutation in mutations:
            type_counts[mutation['type']] = type_counts.get(mutation['type'], 0) + 1
        return type_counts

    def _calculate_mutation_frequency(self, mutations: List[Dict]) -> float:
        """Calculate the frequency of mutations over time."""
        if not mutations:
            return 0
        
        start_time = mutations[0]['timestamp']
        end_time = mutations[-1]['timestamp']
        duration = (end_time - start_time) / 1000  # Convert to seconds
        
        return len(mutations) / duration if duration > 0 else 0

    def _analyze_affected_elements(self, mutations: List[Dict]) -> Dict:
        """Analyze which elements were affected by mutations."""
        affected_elements = {}
        for mutation in mutations:
            target = mutation['target']
            affected_elements[target] = affected_elements.get(target, 0) + 1
        return affected_elements

    def _extract_media_query(self, content: str) -> Optional[str]:
        """Extract media query from content string."""
        try:
            start = content.index('@media')
            end = content.index('{', start)
            return content[start:end].strip()
        except ValueError:
            return None

    def _parse_media_query(self, query: str) -> Optional[Dict]:
        """Parse media query into structured data."""
        try:
            conditions = query.replace('@media', '').strip()
            return {
                'query': conditions,
                'type': 'max-width' if 'max-width' in conditions else 'min-width',
                'value': int(''.join(filter(str.isdigit, conditions)))
            }
        except Exception:
            return None

    def _calculate_max_depth(self, soup: BeautifulSoup) -> int:
        """Calculate maximum nesting depth of elements."""
        max_depth = 0
        for tag in soup.find_all():
            depth = len(list(tag.parents))
            max_depth = max(max_depth, depth)
        return max_depth

    def _analyze_heading_structure(self, soup: BeautifulSoup) -> Dict:
        """Analyze heading hierarchy."""
        headings = {'h1': [], 'h2': [], 'h3': [], 'h4': [], 'h5': [], 'h6': []}
        for level in range(1, 7):
            tag = f'h{level}'
            headings[tag] = [h.text.strip() for h in soup.find_all(tag)]
        return headings

    def _find_landmark_roles(self, soup: BeautifulSoup) -> List[str]:
        """Find and return landmark roles."""
        landmarks = []
        for element in soup.find_all(attrs={'role': True}):
            role = element.get('role')
            if role in ['banner', 'navigation', 'main', 'complementary', 'contentinfo']:
                landmarks.append(role)
        return landmarks

    def _analyze_nesting_patterns(self, soup: BeautifulSoup) -> Dict:
        """Analyze element nesting patterns."""
        patterns = {}
        for tag in soup.find_all():
            if tag.parent:
                pattern = f"{tag.parent.name} > {tag.name}"
                patterns[pattern] = patterns.get(pattern, 0) + 1
        return patterns

    def _analyze_parent_child_relationships(self, soup: BeautifulSoup) -> Dict:
        """Analyze parent-child relationships between elements."""
        relationships = {
            'common_children': self._find_common_children(soup),
            'nested_structures': self._analyze_nested_structures(soup),
            'containment_patterns': self._analyze_containment_patterns(soup)
        }
        return relationships

    def _find_common_children(self, soup: BeautifulSoup) -> Dict:
        """Find common parent-child element combinations."""
        child_patterns = {}
        for tag in soup.find_all():
            if tag.parent:
                key = f"{tag.parent.name} > {tag.name}"
                child_patterns[key] = child_patterns.get(key, 0) + 1
        return {k: v for k, v in child_patterns.items() if v > 1}

    def _analyze_nested_structures(self, soup: BeautifulSoup) -> List[Dict]:
        """Analyze deeply nested structures."""
        nested_structures = []
        for tag in soup.find_all():
            depth = len(list(tag.parents))
            if depth > 3:  # Consider structures with depth > 3 as significant
                structure = {
                    'element': tag.name,
                    'depth': depth,
                    'path': ' > '.join(reversed([p.name for p in tag.parents]))
                }
                nested_structures.append(structure)
        return nested_structures

    def _analyze_containment_patterns(self, soup: BeautifulSoup) -> Dict:
        """Analyze common element containment patterns."""
        containment = {
            'list_structures': self._analyze_list_containment(soup),
            'section_structures': self._analyze_section_containment(soup),
            'form_structures': self._analyze_form_containment(soup)
        }
        return containment

    def _analyze_list_containment(self, soup: BeautifulSoup) -> List[Dict]:
        """Analyze list containment patterns."""
        list_structures = []
        for list_tag in soup.find_all(['ul', 'ol']):
            structure = {
                'type': list_tag.name,
                'items': len(list_tag.find_all('li')),
                'nested_lists': len(list_tag.find_all(['ul', 'ol'], recursive=False))
            }
            list_structures.append(structure)
        return list_structures

    def _analyze_section_containment(self, soup: BeautifulSoup) -> List[Dict]:
        """Analyze section containment patterns."""
        section_structures = []
        for section in soup.find_all(['section', 'article', 'div']):
            if section.get('role') in ['main', 'complementary', 'navigation']:
                structure = {
                    'type': section.name,
                    'role': section.get('role'),
                    'has_heading': bool(section.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
                    'child_sections': len(section.find_all(['section', 'article'], recursive=False))
                }
                section_structures.append(structure)
        return section_structures

    def _analyze_form_containment(self, soup: BeautifulSoup) -> List[Dict]:
        """Analyze form containment patterns."""
        form_structures = []
        for form in soup.find_all('form'):
            structure = {
                'fieldsets': len(form.find_all('fieldset')),
                'input_groups': len(form.find_all('div', class_=lambda x: x and 'group' in x.lower())),
                'nested_forms': len(form.find_all('form', recursive=False))
            }
            form_structures.append(structure)
        return form_structures

    def _find_reusable_components(self, soup: BeautifulSoup) -> List[Dict]:
        """Find reusable components in the page."""
        components = []
        # Look for repeated class patterns
        class_counts = {}
        for tag in soup.find_all(class_=True):
            classes = ' '.join(sorted(tag.get('class')))
            if classes:
                class_counts[classes] = class_counts.get(classes, 0) + 1

        # Components are elements with same classes used multiple times
        for classes, count in class_counts.items():
            if count > 1:
                components.append({
                    'type': 'reusable',
                    'classes': classes.split(),
                    'count': count
                })
        return components

    def _find_interactive_elements(self, soup: BeautifulSoup) -> List[Dict]:
        """Find interactive elements in the page."""
        interactive = []
        selectors = ['button', 'a', 'input', 'select', 'textarea']
        for tag in soup.find_all(selectors):
            interactive.append({
                'type': tag.name,
                'id': tag.get('id', ''),
                'class': tag.get('class', []),
                'text': tag.text.strip() if tag.name != 'input' else tag.get('placeholder', '')
            })
        return interactive

    def _analyze_content_blocks(self, soup: BeautifulSoup) -> List[Dict]:
        """Analyze content block structures."""
        blocks = []
        content_tags = ['article', 'section', 'div']
        for tag in soup.find_all(content_tags):
            if len(tag.get_text(strip=True)) > 0:
                blocks.append({
                    'type': tag.name,
                    'classes': tag.get('class', []),
                    'has_heading': bool(tag.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
                    'word_count': len(tag.get_text(strip=True).split())
                })
        return blocks

    def _analyze_form_components(self, soup: BeautifulSoup) -> List[Dict]:
        """Analyze form components."""
        forms = []
        for form in soup.find_all('form'):
            forms.append({
                'id': form.get('id', ''),
                'method': form.get('method', 'get'),
                'inputs': [
                    {
                        'type': input_tag.get('type', 'text'),
                        'name': input_tag.get('name', ''),
                        'required': input_tag.has_attr('required')
                    }
                    for input_tag in form.find_all('input')
                ]
            })
        return forms

    def _analyze_accessibility(self, soup: BeautifulSoup) -> Dict:
        """Analyze accessibility features of the page."""
        return {
            'aria_labels': self._find_aria_labels(soup),
            'heading_hierarchy': self._analyze_heading_structure(soup),
            'landmarks': self._find_landmark_roles(soup),
            'alt_texts': self._analyze_alt_texts(soup)
        }

    def _find_aria_labels(self, soup: BeautifulSoup) -> List[Dict]:
        """Find and analyze ARIA labels."""
        aria_elements = []
        for tag in soup.find_all(attrs=lambda x: any(k.startswith('aria-') for k in x.keys() if k)):
            aria_attrs = {k: v for k, v in tag.attrs.items() if k.startswith('aria-')}
            if aria_attrs:
                aria_elements.append({
                    'element': tag.name,
                    'attributes': aria_attrs
                })
        return aria_elements

    def _analyze_alt_texts(self, soup: BeautifulSoup) -> Dict:
        """Analyze alt text usage in images."""
        images = soup.find_all('img')
        return {
            'total_images': len(images),
            'with_alt': len([img for img in images if img.get('alt')]),
            'without_alt': len([img for img in images if not img.get('alt')])
        }

    def _analyze_loading_patterns(self, driver: webdriver.Remote) -> Dict:
        """Analyze page loading patterns."""
        try:
            # Check for infinite scroll
            initial_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            # Check for lazy loading images
            lazy_images = driver.execute_script(
                "return document.querySelectorAll('img[loading=\"lazy\"]').length"
            )
            
            return {
                'infinite_scroll': new_height > initial_height,
                'lazy_loading': lazy_images > 0
            }
        except Exception as e:
            self.logger.error(f"Error analyzing loading patterns: {str(e)}")
            return {}

    def _detect_ajax_patterns(self, driver: webdriver.Remote) -> Dict:
        """Detect AJAX usage patterns."""
        try:
            # Inject and execute detection script
            ajax_detection = driver.execute_script("""
                return {
                    'fetch_used': 'fetch' in window,
                    'xhr_used': 'XMLHttpRequest' in window,
                    'jquery_ajax': typeof jQuery !== 'undefined' && jQuery.ajax,
                    'axios_used': typeof axios !== 'undefined'
                }
            """)
            
            return ajax_detection
        except Exception as e:
            self.logger.error(f"Error detecting AJAX patterns: {str(e)}")
            return {}

    def _analyze_state_changes(self, driver: webdriver.Remote) -> Dict:
        """Analyze DOM state changes."""
        try:
            return {
                'mutation_frequency': self._mutation_count / max(1, len(self._content_update_times)),
                'update_patterns': self._analyze_update_patterns(),
                'dynamic_elements': self._find_dynamic_elements(driver)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing state changes: {str(e)}")
            return {}

    def _analyze_update_patterns(self) -> Dict:
        """Analyze patterns in content updates."""
        if not self._content_update_times:
            return {'regular_updates': False, 'update_interval': 0}
            
        intervals = []
        for i in range(1, len(self._content_update_times)):
            intervals.append(self._content_update_times[i] - self._content_update_times[i-1])
            
        avg_interval = sum(intervals) / max(1, len(intervals))
        variance = sum((x - avg_interval) ** 2 for x in intervals) / max(1, len(intervals))
        
        return {
            'regular_updates': variance < 1000,  # Less than 1s variance
            'update_interval': avg_interval
        }

    def _find_dynamic_elements(self, driver: webdriver.Remote) -> List[Dict]:
        """Find elements that change frequently."""
        try:
            dynamic_elements = driver.execute_script("""
                return Array.from(document.querySelectorAll('*')).filter(el => {
                    return el.getAttribute('data-dynamic') ||
                           el.classList.contains('dynamic') ||
                           el.getAttribute('aria-live') === 'polite' ||
                           el.getAttribute('aria-live') === 'assertive';
                }).map(el => ({
                    tagName: el.tagName.toLowerCase(),
                    id: el.id,
                    classes: Array.from(el.classList)
                }));
            """)
            
            return dynamic_elements
        except Exception as e:
            self.logger.error(f"Error finding dynamic elements: {str(e)}")
            return []
            
    def _analyze_component_dependencies(self, soup: BeautifulSoup) -> Dict:
        """Analyze dependencies between components based on DOM relationships and interactions."""
        dependencies = {
            'event_handlers': [],
            'aria_controls': [],
            'form_relationships': [],
            'modal_triggers': []
        }
        
        # Find elements with event handlers
        for tag in soup.find_all(attrs={'onclick': True}):
            dependencies['event_handlers'].append({
                'source': tag.name,
                'target': tag.get('onclick'),
                'type': 'event'
            })
            
        # Find ARIA relationships
        for tag in soup.find_all(attrs={'aria-controls': True}):
            dependencies['aria_controls'].append({
                'source': tag.name,
                'target_id': tag.get('aria-controls'),
                'type': 'aria'
            })
            
        # Analyze form relationships
        for form in soup.find_all('form'):
            submit_buttons = form.find_all(['button', 'input'], attrs={'type': 'submit'})
            for button in submit_buttons:
                dependencies['form_relationships'].append({
                    'source': button.name,
                    'target': form.get('id', 'unnamed_form'),
                    'type': 'form_submission'
                })
                
        # Find modal/dialog triggers
        for tag in soup.find_all(attrs={'data-toggle': 'modal'}):
            target = tag.get('data-target') or tag.get('href')
            if target:
                dependencies['modal_triggers'].append({
                    'source': tag.name,
                    'target': target,
                    'type': 'modal'
                })
                
        return dependencies