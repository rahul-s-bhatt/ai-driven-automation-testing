"""
Scraping Analyzer module for analyzing webpage structure and identifying useful elements for scraping.

This module provides detailed analysis of HTML elements, tags, and their relationships
to assist in web scraping tasks.
"""

from typing import Dict, List, Set
from bs4 import BeautifulSoup
from collections import defaultdict
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
import json

class ScrapingAnalyzer:
    """Analyzes webpage structure for scraping purposes."""

    def __init__(self, driver: webdriver.Remote):
        self.driver = driver
        self.soup = None
        self.tag_stats = defaultdict(int)
        self.class_stats = defaultdict(int)
        self.id_stats = defaultdict(int)
        self.repeated_patterns = []
        self.data_attributes = []
        self.common_selectors = []
        self.text_content_patterns = []

    def analyze_page(self, url: str = None) -> Dict:
        """
        Analyze the current page or navigate to URL first.
        
        Args:
            url: Optional URL to analyze
            
        Returns:
            Dict containing analysis results
        """
        if url:
            self.driver.get(url)
        
        # Get page source after JavaScript execution
        page_source = self.driver.execute_script("return document.documentElement.outerHTML")
        self.soup = BeautifulSoup(page_source, 'lxml')
        
        # Perform various analyses
        self._analyze_tags()
        self._analyze_classes()
        self._analyze_ids()
        self._find_repeated_patterns()
        self._analyze_data_attributes()
        self._generate_selectors()
        self._analyze_text_patterns()
        
        return self._generate_report()

    def _analyze_tags(self):
        """Analyze HTML tags and their frequency."""
        for tag in self.soup.find_all():
            self.tag_stats[tag.name] += 1

    def _analyze_classes(self):
        """Analyze CSS classes and their usage."""
        for tag in self.soup.find_all(class_=True):
            for class_name in tag.get('class', []):
                self.class_stats[class_name] += 1

    def _analyze_ids(self):
        """Analyze element IDs."""
        for tag in self.soup.find_all(id=True):
            self.id_stats[tag['id']] += 1

    def _find_repeated_patterns(self):
        """Find repeated element patterns that might indicate lists or grids."""
        # Look for parent elements with multiple similar children
        for tag in self.soup.find_all():
            children = tag.find_all(recursive=False)
            if len(children) >= 3:  # At least 3 similar items
                first_child = children[0]
                similar_children = [
                    c for c in children[1:]
                    if c.name == first_child.name and 
                    set(c.get('class', [])) == set(first_child.get('class', []))
                ]
                
                if len(similar_children) >= 2:
                    self.repeated_patterns.append({
                        'parent': self._get_element_description(tag),
                        'pattern': self._get_element_description(first_child),
                        'count': len(similar_children) + 1,
                        'selector': self._generate_selector(first_child)
                    })

    def _analyze_data_attributes(self):
        """Find and analyze data attributes that might contain useful information."""
        for tag in self.soup.find_all():
            data_attrs = {
                attr: tag[attr] for attr in tag.attrs
                if attr.startswith('data-')
            }
            if data_attrs:
                self.data_attributes.append({
                    'element': self._get_element_description(tag),
                    'attributes': data_attrs,
                    'selector': self._generate_selector(tag)
                })

    def _generate_selectors(self):
        """Generate useful CSS selectors for common elements."""
        # Find elements that might contain valuable data
        valuable_elements = []
        
        # Links with specific patterns
        for a in self.soup.find_all('a', href=True):
            href = a['href']
            if re.search(r'/(product|item|article|post)/\d+', href):
                valuable_elements.append(('link', a))

        # Tables with data
        for table in self.soup.find_all('table'):
            if table.find('th') or table.find('td'):
                valuable_elements.append(('table', table))

        # Lists that might contain data
        for ul in self.soup.find_all(['ul', 'ol']):
            if len(ul.find_all('li')) >= 3:
                valuable_elements.append(('list', ul))

        # Generate selectors for valuable elements
        for element_type, element in valuable_elements:
            self.common_selectors.append({
                'type': element_type,
                'selector': self._generate_selector(element),
                'sample_content': self._get_sample_content(element)
            })

    def _analyze_text_patterns(self):
        """Analyze text content patterns."""
        # Look for common text patterns
        patterns = {
            'price': r'\$\d+\.?\d*|\d+\.?\d*\s*€|£\d+\.?\d*',
            'date': r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}-\d{2}-\d{2}',
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'phone': r'\+?\d{1,3}[-.]?\d{3}[-.]?\d{3,4}[-.]?\d{4}',
            'url': r'https?://[^\s<>"]+|www\.[^\s<>"]+',
        }

        for pattern_name, pattern in patterns.items():
            elements_with_pattern = self.soup.find_all(
                string=re.compile(pattern)
            )
            if elements_with_pattern:
                self.text_content_patterns.append({
                    'type': pattern_name,
                    'count': len(elements_with_pattern),
                    'sample': str(elements_with_pattern[0]),
                    'elements': [
                        self._get_element_description(elem.parent)
                        for elem in elements_with_pattern[:5]
                    ]
                })

    def _get_element_description(self, element) -> Dict:
        """Get a readable description of an element."""
        return {
            'tag': element.name,
            'classes': element.get('class', []),
            'id': element.get('id', ''),
            'text_sample': element.get_text()[:50] if element.get_text() else ''
        }

    def _generate_selector(self, element) -> str:
        """Generate a unique CSS selector for an element."""
        if element.get('id'):
            return f"#{element['id']}"
        
        classes = element.get('class', [])
        if classes:
            return f"{element.name}.{'.'.join(classes)}"
        
        # Generate path based on parent structure
        path = []
        for parent in element.parents:
            if parent.name == '[document]':
                break
            if parent.get('id'):
                path.append(f"#{parent['id']}")
                break
            if parent.get('class'):
                path.append(f"{parent.name}.{'.'.join(parent.get('class', []))}")
            else:
                path.append(parent.name)
        
        path.reverse()
        return ' > '.join(path + [element.name])

    def _get_sample_content(self, element) -> str:
        """Get a sample of the element's content."""
        text = element.get_text(strip=True)
        return text[:100] + '...' if len(text) > 100 else text

    def _generate_report(self) -> Dict:
        """Generate a comprehensive analysis report."""
        return {
            'page_structure': {
                'tags': dict(sorted(
                    self.tag_stats.items(),
                    key=lambda x: x[1],
                    reverse=True
                )),
                'classes': dict(sorted(
                    self.class_stats.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:20]),  # Top 20 most used classes
                'ids': dict(self.id_stats)
            },
            'repeated_patterns': self.repeated_patterns,
            'data_attributes': self.data_attributes,
            'useful_selectors': self.common_selectors,
            'content_patterns': self.text_content_patterns,
            'recommended_selectors': self._generate_recommended_selectors()
        }

    def _generate_recommended_selectors(self) -> List[Dict]:
        """Generate recommended selectors for scraping."""
        recommendations = []
        
        # For repeated patterns (lists, grids)
        if self.repeated_patterns:
            for pattern in self.repeated_patterns:
                recommendations.append({
                    'purpose': 'List/Grid Items',
                    'selector': pattern['selector'],
                    'count': pattern['count'],
                    'note': 'Repeated element pattern - good for scraping lists of items'
                })

        # For data attributes
        if self.data_attributes:
            for data_attr in self.data_attributes:
                recommendations.append({
                    'purpose': 'Data Container',
                    'selector': data_attr['selector'],
                    'attributes': list(data_attr['attributes'].keys()),
                    'note': 'Contains structured data in attributes'
                })

        # For text patterns
        for pattern in self.text_content_patterns:
            if pattern['elements']:
                recommendations.append({
                    'purpose': f'Extract {pattern["type"]}',
                    'selector': self._generate_selector(
                        BeautifulSoup(pattern['elements'][0]['text_sample'], 'lxml')
                    ),
                    'count': pattern['count'],
                    'note': f'Contains {pattern["type"]} data'
                })

        return recommendations

    def get_html_visualization(self) -> str:
        """Generate an HTML visualization of the analysis."""
        html = """
        <div class="scraping-analysis">
            <h3>Page Structure Overview</h3>
            <div class="tag-cloud">
                {}
            </div>
            
            <h3>Recommended Selectors</h3>
            <div class="selectors-list">
                {}
            </div>
            
            <h3>Content Patterns</h3>
            <div class="patterns-list">
                {}
            </div>
        </div>
        """.format(
            self._generate_tag_cloud(),
            self._generate_selectors_html(),
            self._generate_patterns_html()
        )
        
        return html

    def _generate_tag_cloud(self) -> str:
        """Generate HTML for tag usage visualization."""
        max_size = max(self.tag_stats.values())
        tags_html = []
        
        for tag, count in sorted(self.tag_stats.items(), key=lambda x: x[1], reverse=True):
            size = 1 + (count / max_size) * 2
            tags_html.append(
                f'<span class="tag" style="font-size: {size}em">'
                f'{tag} ({count})</span>'
            )
        
        return ' '.join(tags_html)

    def _generate_selectors_html(self) -> str:
        """Generate HTML for recommended selectors."""
        html = []
        for rec in self._generate_recommended_selectors():
            html.append(f"""
                <div class="selector-item">
                    <div class="purpose">{rec['purpose']}</div>
                    <code class="selector">{rec['selector']}</code>
                    <div class="note">{rec['note']}</div>
                </div>
            """)
        return ''.join(html)

    def _generate_patterns_html(self) -> str:
        """Generate HTML for content patterns."""
        html = []
        for pattern in self.text_content_patterns:
            html.append(f"""
                <div class="pattern-item">
                    <div class="type">{pattern['type']}</div>
                    <div class="sample">{pattern['sample']}</div>
                    <div class="count">Found {pattern['count']} instances</div>
                </div>
            """)
        return ''.join(html)