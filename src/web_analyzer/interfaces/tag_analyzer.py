"""
Interface and implementations for smart tag analysis functionality.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

class TagAnalyzer(ABC):
    """Interface for tag analysis implementations."""
    
    @abstractmethod
    def analyze_tags(self, soup: BeautifulSoup) -> Dict:
        """Analyze tags and return structured information."""
        pass

class SmartTagAnalyzer(TagAnalyzer):
    """Enhanced tag analyzer with pattern recognition and semantic analysis."""
    
    def analyze_tags(self, soup: BeautifulSoup) -> Dict:
        """
        Perform enhanced tag analysis including:
        - Pattern recognition
        - Semantic structure analysis
        - Enhanced attribute analysis
        """
        try:
            analysis = {
                'tag_patterns': self._analyze_patterns(soup),
                'semantic_structure': self._analyze_semantics(soup),
                'key_attributes': self._analyze_attributes(soup)
            }
            return analysis
        except Exception as e:
            return {
                'error': str(e),
                'tag_patterns': {},
                'semantic_structure': {},
                'key_attributes': {}
            }

    def _analyze_patterns(self, soup: BeautifulSoup) -> Dict:
        """Analyze common web component patterns."""
        patterns = {
            'lists': self._find_list_patterns(soup),
            'cards': self._find_card_patterns(soup),
            'grids': self._find_grid_patterns(soup)
        }
        return patterns

    def _analyze_semantics(self, soup: BeautifulSoup) -> Dict:
        """Analyze semantic meaning of page structure."""
        semantics = {
            'header_elements': self._find_header_elements(soup),
            'content_sections': self._find_content_sections(soup),
            'navigation_elements': self._find_navigation_elements(soup)
        }
        return semantics

    def _analyze_attributes(self, soup: BeautifulSoup) -> Dict:
        """Analyze HTML attributes for better element identification."""
        attributes = {
            'data_attributes': self._find_data_attributes(soup),
            'aria_attributes': self._find_aria_attributes(soup),
            'class_patterns': self._find_class_patterns(soup)
        }
        return attributes

    def _find_list_patterns(self, soup: BeautifulSoup) -> List[Dict]:
        """Find and analyze list patterns."""
        patterns = []
        for list_tag in soup.find_all(['ul', 'ol']):
            if len(list_tag.find_all('li')) >= 2:
                patterns.append({
                    'type': list_tag.name,
                    'items': len(list_tag.find_all('li')),
                    'classes': list_tag.get('class', []),
                    'structure': self._analyze_list_structure(list_tag)
                })
        return patterns

    def _find_card_patterns(self, soup: BeautifulSoup) -> List[Dict]:
        """Find and analyze card-like component patterns."""
        card_patterns = []
        card_candidates = soup.find_all(class_=['card', 'item', 'product'])
        
        for card in card_candidates:
            card_patterns.append({
                'tag': card.name,
                'classes': card.get('class', []),
                'has_image': bool(card.find('img')),
                'has_title': bool(card.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
                'has_link': bool(card.find('a')),
                'content_structure': self._analyze_component_structure(card)
            })
        return card_patterns

    def _find_grid_patterns(self, soup: BeautifulSoup) -> List[Dict]:
        """Find and analyze grid layout patterns."""
        grid_patterns = []
        grid_candidates = soup.find_all(class_=['grid', 'row', 'container'])
        
        for grid in grid_candidates:
            children = grid.find_all(recursive=False)
            if len(children) >= 2:
                grid_patterns.append({
                    'tag': grid.name,
                    'classes': grid.get('class', []),
                    'children_count': len(children),
                    'layout_type': self._determine_layout_type(grid),
                    'structure': self._analyze_component_structure(grid)
                })
        return grid_patterns

    def _find_header_elements(self, soup: BeautifulSoup) -> Dict:
        """Find and analyze header elements."""
        return {
            'main_header': bool(soup.find('header')),
            'navigation': bool(soup.find('nav')),
            'branding': bool(soup.find(class_=['logo', 'brand'])),
            'hierarchy': [h.name for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
        }

    def _find_content_sections(self, soup: BeautifulSoup) -> List[Dict]:
        """Find and analyze content sections."""
        sections = []
        for section in soup.find_all(['section', 'article', 'main', 'aside']):
            sections.append({
                'tag': section.name,
                'role': section.get('role', ''),
                'aria_label': section.get('aria-label', ''),
                'has_heading': bool(section.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
            })
        return sections

    def _find_navigation_elements(self, soup: BeautifulSoup) -> Dict:
        """Find and analyze navigation elements."""
        return {
            'primary_nav': bool(soup.find('nav', {'role': 'navigation'})),
            'links': len(soup.find_all('a')),
            'menu_items': len(soup.find_all(['nav', 'menu'])),
            'dropdowns': len(soup.find_all(class_=['dropdown', 'menu']))
        }

    def _find_data_attributes(self, soup: BeautifulSoup) -> Dict:
        """Find and analyze data attributes."""
        data_attrs = {}
        for tag in soup.find_all():
            for attr in tag.attrs:
                if attr.startswith('data-'):
                    data_attrs[attr] = data_attrs.get(attr, 0) + 1
        return data_attrs

    def _find_aria_attributes(self, soup: BeautifulSoup) -> Dict:
        """Find and analyze ARIA attributes."""
        aria_attrs = {}
        for tag in soup.find_all():
            for attr in tag.attrs:
                if attr.startswith('aria-'):
                    aria_attrs[attr] = aria_attrs.get(attr, 0) + 1
        return aria_attrs

    def _find_class_patterns(self, soup: BeautifulSoup) -> Dict:
        """Find and analyze class patterns."""
        class_patterns = {}
        for tag in soup.find_all(class_=True):
            for class_name in tag.get('class', []):
                class_patterns[class_name] = class_patterns.get(class_name, 0) + 1
        return class_patterns

    def _analyze_list_structure(self, list_tag) -> Dict:
        """Analyze the structure of a list component."""
        items = list_tag.find_all('li')
        return {
            'item_count': len(items),
            'nested_lists': len([i for i in items if i.find(['ul', 'ol'])]),
            'has_links': any(i.find('a') for i in items),
            'has_images': any(i.find('img') for i in items)
        }

    def _analyze_component_structure(self, element) -> Dict:
        """Analyze the structure of a component."""
        return {
            'depth': len(list(element.parents)),
            'direct_children': len(element.find_all(recursive=False)),
            'text_nodes': len([t for t in element.strings if t.strip()]),
            'total_descendants': len(element.find_all())
        }

    def _determine_layout_type(self, element) -> str:
        """Determine the type of layout used."""
        classes = element.get('class', [])
        if any('grid' in cls for cls in classes):
            return 'grid'
        elif any('flex' in cls for cls in classes):
            return 'flexbox'
        elif any('row' in cls for cls in classes):
            return 'row-based'
        return 'standard'