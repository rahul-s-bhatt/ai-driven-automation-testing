"""
Web interface server for the testing framework.

This module provides a Flask server to serve the HTML interface and handle
test execution and analysis requests.
"""

import os
import sys
import tempfile
import logging
from pathlib import Path
import json
from flask import Flask, render_template, request, jsonify, send_file
import yaml

# Add the project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.test_engine.scenario_parser import ScenarioParser
from src.test_engine.test_executor import TestExecutor
from src.web_analyzer.dom_parser import DOMParser
from src.web_analyzer.element_classifier import ElementClassifier
from src.web_analyzer.structure_analyzer import StructureAnalyzer
from src.web_analyzer.scraping_analyzer import ScrapingAnalyzer
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_webdriver():
    """Set up and configure WebDriver."""
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        service = ChromeService(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    except Exception as e:
        logger.error(f"Failed to setup WebDriver: {str(e)}")
        raise

def run_tests(url: str, test_yaml: str) -> dict:
    """Run tests with the provided URL and test steps."""
    temp_dir = None
    driver = None
    
    try:
        # Create temporary directory for test outputs
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir)
        
        # Create output directories
        screenshots_dir = temp_path / 'screenshots'
        reports_dir = temp_path / 'reports'
        logs_dir = temp_path / 'logs'

        for dir_path in [screenshots_dir, reports_dir, logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Save test scenario
        scenario_file = temp_path / 'test_scenario.yaml'
        with open(scenario_file, 'w') as f:
            f.write(test_yaml)

        logger.info(f"Running tests against URL: {url}")
        logger.info(f"Test scenario:\n{test_yaml}")

        # Parse test scenarios
        parser = ScenarioParser()
        scenarios = parser.parse_scenario_file(str(scenario_file))

        if not scenarios:
            return {
                'success': False,
                'error': 'No test scenarios found'
            }

        # Set up WebDriver
        driver = setup_webdriver()
        
        try:
            # Initialize test executor
            executor = TestExecutor(
                driver=driver,
                screenshot_dir=str(screenshots_dir),
                base_url=url
            )

            # Execute test scenario
            scenario = scenarios[0]  # We only run the first scenario
            success, errors = executor.execute_scenario(scenario)

            # Collect screenshots
            screenshots = []
            if screenshots_dir.exists():
                screenshots = [
                    str(f.relative_to(temp_path))
                    for f in screenshots_dir.glob('*.png')
                ]

            return {
                'success': success,
                'scenario_name': scenario.name,
                'errors': errors,
                'screenshots': screenshots
            }

        finally:
            if driver:
                driver.quit()

    except Exception as e:
        logger.error(f"Error running tests: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/analyze_scraping', methods=['POST'])
def analyze_scraping():
    """Handle scraping analysis requests."""
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400

        # Set up WebDriver
        driver = setup_webdriver()
        
        try:
            # Initialize scraping analyzer
            analyzer = ScrapingAnalyzer(driver)
            
            # Analyze website
            analysis_results = analyzer.analyze_page(url)
            
            # Get HTML visualization
            visualization = analyzer.get_html_visualization()
            
            return jsonify({
                'success': True,
                'analysis': analysis_results,
                'visualization': visualization
            })
        
        finally:
            if driver:
                driver.quit()

    except Exception as e:
        logger.error("Error analyzing website for scraping", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/analyze_site', methods=['POST'])
def analyze_site():
    """Handle website analysis requests."""
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400

        # Set up WebDriver
        driver = setup_webdriver()
        
        try:
            # Initialize analyzer
            analyzer = StructureAnalyzer(driver)
            
            # Analyze website
            analysis_results = analyzer.analyze_website(url)
            
            return jsonify({
                'success': True,
                'analysis': analysis_results
            })
        
        finally:
            if driver:
                driver.quit()

    except Exception as e:
        logger.error("Error analyzing website", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/screenshots/<path:filename>')
def get_screenshot(filename):
    """Serve screenshot files."""
    return send_file(os.path.join(app.config['SCREENSHOT_DIR'], filename))

@app.route('/run_test', methods=['POST'])
def handle_test():
    """Handle test execution requests."""
    try:
        data = request.get_json()
        url = data.get('url')
        test_yaml = data.get('test_yaml')

        if not url:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400

        if not test_yaml:
            return jsonify({
                'success': False,
                'error': 'Test steps are required'
            }), 400

        # Validate YAML format
        try:
            yaml.safe_load(test_yaml)
        except yaml.YAMLError as e:
            return jsonify({
                'success': False,
                'error': f'Invalid YAML format: {str(e)}'
            }), 400

        # Run tests
        results = run_tests(url, test_yaml)
        return jsonify(results)

    except Exception as e:
        logger.error("Error handling test request", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Run the Flask server
    app.run(debug=True)