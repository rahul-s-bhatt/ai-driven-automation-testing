"""
Web interface server for the testing framework.
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

def setup_webdriver(headless=True):
    """Set up and configure WebDriver."""
    try:
        options = webdriver.ChromeOptions()
        
        if headless:
            options.add_argument('--headless')  # Enable headless mode
            
        # Common options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-notifications')
        
        # Additional performance options for headless mode
        if headless:
            options.add_argument('--disable-software-rasterizer')
            options.add_argument('--disable-setuid-sandbox')
            
        service = ChromeService(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    except Exception as e:
        logger.error(f"Failed to setup WebDriver: {str(e)}")
        raise

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

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

        # Set up WebDriver in headless mode
        driver = setup_webdriver(headless=True)
        
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

        # Set up WebDriver in headless mode
        driver = setup_webdriver(headless=True)
        
        try:
            # Initialize scraping analyzer
            analyzer = ScrapingAnalyzer(driver)
            
            # Analyze website
            analysis_results = analyzer.analyze_page(url)
            
            return jsonify({
                'success': True,
                'analysis': analysis_results
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

@app.route('/run_test', methods=['POST'])
def run_test():
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

        # Parse test scenarios
        parser = ScenarioParser()
        scenarios = parser.parse_scenario_file(str(scenario_file))

        if not scenarios:
            return jsonify({
                'success': False,
                'error': 'No test scenarios found'
            })

        # Set up WebDriver in non-headless mode for test execution
        # Tests need visible browser for accurate interaction
        driver = setup_webdriver(headless=False)
        
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

            return jsonify({
                'success': success,
                'errors': errors,
                'screenshots': screenshots
            })

        finally:
            if driver:
                driver.quit()

    except Exception as e:
        logger.error(f"Error running tests: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/screenshots/<path:filename>')
def serve_screenshot(filename):
    """Serve screenshot files."""
    return send_file(os.path.join(app.config['SCREENSHOT_DIR'], filename))

if __name__ == '__main__':
    app.run(debug=True)