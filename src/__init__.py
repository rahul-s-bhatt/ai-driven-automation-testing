"""
Intelligent Automated Website Testing Framework

A powerful, flexible testing framework that combines Selenium WebDriver with
semantic understanding capabilities to create robust, maintainable automated
tests for web applications.
"""

__version__ = '0.1.0'

from . import web_analyzer
from . import test_engine
from . import reporting
from . import utils

__all__ = [
    'web_analyzer',
    'test_engine',
    'reporting',
    'utils',
]