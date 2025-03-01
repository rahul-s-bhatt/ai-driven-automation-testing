"""
DOM Parser module for analyzing website structure.

This module provides functionality to parse and analyze website DOM structure
using Selenium and BeautifulSoup.
"""

from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class DOMParser:
    """Main class for parsing and analyzing website DOM structure."""

    def __init__(self, driver: webdriver.Remote):
        """
        Initialize the DOM parser.

        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self._page_source = None
        self._soup = None

    def load_page(self, url: str) -> bool:
        """
        Load a webpage and wait for it to be ready.

        Args:
            url: The URL to load

        Returns:
            bool: True if page loaded successfully, False otherwise
        """
        try:
            self.driver.get(url)
            # Wait for document to be ready
            self.wait.until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            self._page_source = self.driver.page_source
            self._soup = BeautifulSoup(self._page_source, 'html.parser')
            return True
        except TimeoutException:
            return False

    def get_element_hierarchy(self) -> Dict:
        """
        Create a hierarchical representation of the page structure.

        Returns:
            Dict: Hierarchical representation of the page
        """
        if not self._soup:
            return {}

        def parse_element(element) -> Dict:
            result = {
                'tag': element.name,
                'attributes': element.attrs,
                'text': element.string.strip() if element.string else None,
                'children': []
            }

            for child in element.children:
                if child.name:  # Skip NavigableString objects
                    result['children'].append(parse_element(child))
            return result

        return parse_element(self._soup.find('html'))

    def find_interactive_elements(self) -> List[Dict]:
        """
        Find and categorize all interactive elements on the page.

        Returns:
            List[Dict]: List of interactive elements with their properties
        """
        interactive_elements = []
        
        # Common interactive elements and their selectors
        selectors = {
            'button': 'button, input[type="button"], input[type="submit"]',
            'link': 'a[href]',
            'input': 'input[type="text"], input[type="password"], input[type="email"]',
            'form': 'form',
            'select': 'select',
            'checkbox': 'input[type="checkbox"]',
            'radio': 'input[type="radio"]'
        }

        for element_type, selector in selectors.items():
            elements = self._soup.select(selector)
            for elem in elements:
                element_info = {
                    'type': element_type,
                    'tag': elem.name,
                    'attributes': elem.attrs,
                    'text': elem.get_text(strip=True),
                    'selector': self._generate_css_selector(elem),
                    'visible': self._is_element_visible(self._generate_css_selector(elem))
                }
                interactive_elements.append(element_info)

        return interactive_elements

    def _generate_css_selector(self, element) -> str:
        """
        Generate a unique CSS selector for an element.

        Args:
            element: BeautifulSoup element

        Returns:
            str: CSS selector
        """
        if element.get('id'):
            return f"#{element['id']}"
        
        if element.get('class'):
            classes = '.'.join(element['class'])
            return f".{classes}"

        # Generate path using tag names and nth-child
        path = []
        current = element
        while current and current.name != 'html':
            tag = current.name
            siblings = current.find_previous_siblings(tag)
            if siblings:
                tag = f"{tag}:nth-of-type({len(siblings) + 1})"
            path.append(tag)
            current = current.parent

        return ' > '.join(reversed(path))

    def _is_element_visible(self, selector: str) -> bool:
        """
        Check if an element is visible on the page.

        Args:
            selector: CSS selector for the element

        Returns:
            bool: True if element is visible, False otherwise
        """
        try:
            element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element.is_displayed()
        except TimeoutException:
            return False

    def get_navigation_structure(self) -> Dict:
        """
        Analyze and return the navigation structure of the page.

        Returns:
            Dict: Navigation structure including menus and links
        """
        nav_structure = {
            'main_nav': [],
            'footer_nav': [],
            'other_nav': []
        }

        # Find main navigation
        main_nav = self._soup.find('nav') or self._soup.find(class_='navigation') or self._soup.find(class_='nav')
        if main_nav:
            nav_structure['main_nav'] = self._extract_nav_items(main_nav)

        # Find footer navigation
        footer = self._soup.find('footer')
        if footer:
            nav_structure['footer_nav'] = self._extract_nav_items(footer)

        # Find other navigation elements
        other_navs = self._soup.find_all(['nav', 'ul'], class_=lambda x: x and ('nav' in x or 'menu' in x))
        for nav in other_navs:
            if nav != main_nav:
                nav_structure['other_nav'].extend(self._extract_nav_items(nav))

        return nav_structure

    def _extract_nav_items(self, nav_element) -> List[Dict]:
        """
        Extract navigation items from a navigation element.

        Args:
            nav_element: BeautifulSoup element containing navigation items

        Returns:
            List[Dict]: List of navigation items with their properties
        """
        items = []
        for link in nav_element.find_all('a'):
            items.append({
                'text': link.get_text(strip=True),
                'href': link.get('href'),
                'selector': self._generate_css_selector(link),
                'visible': self._is_element_visible(self._generate_css_selector(link))
            })
        return items