"""
Element Classifier module for semantic understanding of website elements.

This module provides functionality to classify and understand website elements
based on their characteristics and context.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum, auto

class ElementType(Enum):
    """Enumeration of different types of web elements."""
    HEADER = auto()
    NAVIGATION = auto()
    CONTENT = auto()
    FORM = auto()
    BUTTON = auto()
    INPUT = auto()
    LINK = auto()
    FOOTER = auto()
    SIDEBAR = auto()
    UNKNOWN = auto()

@dataclass
class ElementContext:
    """Data class containing contextual information about an element."""
    tag_name: str
    classes: List[str]
    attributes: Dict
    text_content: Optional[str]
    parent_tags: List[str]
    siblings_count: int
    depth: int

class ElementClassifier:
    """Main class for classifying website elements based on their characteristics."""

    def __init__(self):
        """Initialize the element classifier with classification rules."""
        self._setup_classification_rules()

    def _setup_classification_rules(self):
        """Set up the rule sets for element classification."""
        self.header_indicators = {
            'tags': {'header', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'},
            'classes': {'header', 'page-header', 'site-header', 'main-header'},
            'attributes': {'role': 'banner'}
        }

        self.navigation_indicators = {
            'tags': {'nav', 'ul', 'ol'},
            'classes': {'nav', 'navigation', 'menu', 'navbar'},
            'attributes': {'role': 'navigation'}
        }

        self.form_indicators = {
            'tags': {'form', 'fieldset'},
            'classes': {'form', 'search-form', 'login-form'},
            'attributes': {'role': 'form'}
        }

        self.button_indicators = {
            'tags': {'button'},
            'classes': {'btn', 'button', 'submit'},
            'attributes': {
                'type': {'submit', 'button'},
                'role': 'button'
            }
        }

        self.input_indicators = {
            'tags': {'input', 'textarea', 'select'},
            'classes': {'form-control', 'input', 'field'},
            'attributes': {'role': 'textbox'}
        }

    def classify_element(self, context: ElementContext) -> ElementType:
        """
        Classify an element based on its context.

        Args:
            context: ElementContext object containing element information

        Returns:
            ElementType: The classified type of the element
        """
        # Order matters - more specific classifications first
        if self._is_header(context):
            return ElementType.HEADER
        elif self._is_navigation(context):
            return ElementType.NAVIGATION
        elif self._is_form(context):
            return ElementType.FORM
        elif self._is_button(context):
            return ElementType.BUTTON
        elif self._is_input(context):
            return ElementType.INPUT
        elif self._is_footer(context):
            return ElementType.FOOTER
        elif self._is_sidebar(context):
            return ElementType.SIDEBAR
        elif self._is_link(context):
            return ElementType.LINK
        elif self._is_content(context):
            return ElementType.CONTENT
        return ElementType.UNKNOWN

    def get_element_importance(self, context: ElementContext) -> float:
        """
        Calculate the relative importance of an element.

        Args:
            context: ElementContext object containing element information

        Returns:
            float: Importance score between 0 and 1
        """
        score = 0.0
        
        # Base score from element type
        element_type = self.classify_element(context)
        type_scores = {
            ElementType.HEADER: 0.9,
            ElementType.NAVIGATION: 0.8,
            ElementType.FORM: 0.7,
            ElementType.BUTTON: 0.6,
            ElementType.INPUT: 0.5,
            ElementType.CONTENT: 0.4,
            ElementType.FOOTER: 0.3,
            ElementType.UNKNOWN: 0.1
        }
        score += type_scores.get(element_type, 0.1)

        # Adjust based on position in hierarchy
        score *= (1.0 - (context.depth * 0.1))  # Deeper elements are less important
        
        # Adjust based on content
        if context.text_content and len(context.text_content.strip()) > 0:
            score += 0.1

        # Normalize score
        return min(max(score, 0.0), 1.0)

    def _is_header(self, context: ElementContext) -> bool:
        """Check if element is a header."""
        return (
            context.tag_name in self.header_indicators['tags'] or
            any(c in self.header_indicators['classes'] for c in context.classes) or
            any(context.attributes.get(k) == v 
                for k, v in self.header_indicators['attributes'].items())
        )

    def _is_navigation(self, context: ElementContext) -> bool:
        """Check if element is navigation."""
        return (
            context.tag_name in self.navigation_indicators['tags'] or
            any(c in self.navigation_indicators['classes'] for c in context.classes) or
            any(context.attributes.get(k) == v 
                for k, v in self.navigation_indicators['attributes'].items())
        )

    def _is_form(self, context: ElementContext) -> bool:
        """Check if element is a form."""
        return (
            context.tag_name in self.form_indicators['tags'] or
            any(c in self.form_indicators['classes'] for c in context.classes) or
            any(context.attributes.get(k) == v 
                for k, v in self.form_indicators['attributes'].items())
        )

    def _is_button(self, context: ElementContext) -> bool:
        """Check if element is a button."""
        return (
            context.tag_name in self.button_indicators['tags'] or
            any(c in self.button_indicators['classes'] for c in context.classes) or
            any(context.attributes.get(k) in v if isinstance(v, set) else context.attributes.get(k) == v
                for k, v in self.button_indicators['attributes'].items())
        )

    def _is_input(self, context: ElementContext) -> bool:
        """Check if element is an input."""
        return (
            context.tag_name in self.input_indicators['tags'] or
            any(c in self.input_indicators['classes'] for c in context.classes) or
            any(context.attributes.get(k) == v 
                for k, v in self.input_indicators['attributes'].items())
        )

    def _is_footer(self, context: ElementContext) -> bool:
        """Check if element is a footer."""
        return context.tag_name == 'footer' or 'footer' in context.classes

    def _is_sidebar(self, context: ElementContext) -> bool:
        """Check if element is a sidebar."""
        return (
            any(c in {'sidebar', 'side-bar', 'aside'} for c in context.classes) or
            context.tag_name == 'aside'
        )

    def _is_link(self, context: ElementContext) -> bool:
        """Check if element is a link."""
        return context.tag_name == 'a' and 'href' in context.attributes

    def _is_content(self, context: ElementContext) -> bool:
        """Check if element is main content."""
        return (
            context.tag_name in {'article', 'section', 'main'} or
            any(c in {'content', 'main-content', 'article'} for c in context.classes) or
            context.attributes.get('role') == 'main'
        )