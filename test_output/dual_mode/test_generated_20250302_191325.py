import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture
def wait(driver):
    return WebDriverWait(driver, 10)

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_login_flow_test(driver):
    """
    Test the website login functionality
    """
    wait = WebDriverWait(driver, 10)

    username = 'testuser@example.com'
    password = 'password123'

    # Navigate to login page
    element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#loginBtn')))
    element.click()

    # Enter email
    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name='email']')))
    element.send_keys('testuser@example.com')

    # Enter password
    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type='password']')))
    element.send_keys('password123')

    # Submit login form
    element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type='submit']')))
    element.click()

    # Wait for dashboard
    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.dashboard-container')))

    # Verify login success
    assert wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.dashboard-container')))
    is not None, 'Element should be visible'
    element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.user-info')))
    assert 'testuser@example.com' in element.text, 'Text should be present'

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_product_search_test(driver):
    """
    Test the product search functionality
    """
    wait = WebDriverWait(driver, 10)

    search_term = 'laptop'

    # Enter search term
    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#searchInput')))
    element.send_keys('laptop')

    # Submit search
    element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type='submit']')))
    element.click()

    # Wait for results
    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.search-results')))

    # Verify results
    assert wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.search-results')))
    is not None, 'Element should be visible'
    elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.product-card')))
    assert len(elements) >= 1, 'Should have minimum number of elements'
