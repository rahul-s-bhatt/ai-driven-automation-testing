"""Web analyzer package for DOM parsing and element classification."""

from .dom_parser import DOMParser
from .element_classifier import ElementClassifier, ElementContext

__all__ = [
    'DOMParser',
    'ElementClassifier',
    'ElementContext'
]