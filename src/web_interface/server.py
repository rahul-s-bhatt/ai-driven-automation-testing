"""
Web interface server for the testing framework.
"""

import os
import sys
import tempfile
import logging
from pathlib import Path
import json
import time
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
from src.web_analyzer.services.analysis_service import WebAnalysisService
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# Configure logging and app settings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize with temporary directory for test outputs
app.config['TEST_OUTPUT_DIR'] = tempfile.mkdtemp()

def setup_browser(headless=True):
    """Set up and configure Playwright browser."""
    try:
        # Initialize Playwright
        playwright = sync_playwright().start()
        
        # Launch browser with appropriate options
        browser = playwright.chromium.launch(
            headless=headless,
            args=['--disable-dev-shm-usage']  # Helpful for containerized environments
        )
        
        # Create a new browser context with viewport size
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        
        # Create a new page
        page = context.new_page()
        logger.info("Playwright browser initialized successfully")
        
        return playwright, browser, page
        
    except Exception as e:
        logger.error(f"Failed to setup Playwright browser: {str(e)}")
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

        # Set up Playwright browser in headless mode
        playwright, browser, page = setup_browser(headless=True)
        
        try:
            # Navigate to the URL
            page.goto(url)
            page.wait_for_load_state('networkidle')
            
            # Initialize analysis service with the page object
            analysis_service = WebAnalysisService(page)
            
            # Analyze website
            analysis_results = analysis_service.analyze_page()

            # Generate test output files
            if 'dual_mode_tests' in analysis_results:
                temp_dir = tempfile.mkdtemp()
                temp_path = Path(temp_dir)
                
                # Create output directories
                test_output_dir = temp_path / 'test_output'
                test_output_dir.mkdir(parents=True, exist_ok=True)

                # Store file paths in the results
                if 'outputs' in analysis_results['dual_mode_tests']:
                    outputs = analysis_results['dual_mode_tests']['outputs']
                    
                    # Save and update path for human instructions
                    if 'human_instructions' in outputs:
                        human_file = test_output_dir / f'human_instructions_{int(time.time())}.md'
                        with open(human_file, 'w') as f:
                            f.write(outputs['human_instructions'])
                        outputs['human_instructions'] = str(human_file.relative_to(temp_path))

                    # Save and update path for automation script
                    if 'automation_script' in outputs:
                        auto_file = test_output_dir / f'automation_test_{int(time.time())}.py'
                        with open(auto_file, 'w') as f:
                            f.write(outputs['automation_script'])
                        outputs['automation_script'] = str(auto_file.relative_to(temp_path))

                app.config['TEST_OUTPUT_DIR'] = str(temp_dir)
            
            return jsonify({
                'success': True,
                'analysis': analysis_results
            })
        
        finally:
            # Clean up Playwright resources
            if page:
                page.close()
            if browser:
                browser.close()
            if playwright:
                playwright.stop()

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

        # Set up Playwright browser in headless mode
        playwright, browser, page = setup_browser(headless=True)
        
        try:
            # Navigate to the URL
            page.goto(url)
            page.wait_for_load_state('networkidle')
            
            # Initialize scraping analyzer with page object
            analyzer = ScrapingAnalyzer(page)
            
            # Analyze website
            analysis_results = analyzer.analyze_page()
            
            return jsonify({
                'success': True,
                'analysis': analysis_results
            })
        
        finally:
            # Clean up Playwright resources
            if page:
                page.close()
            if browser:
                browser.close()
            if playwright:
                playwright.stop()

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

        # Set up Playwright browser in non-headless mode for test execution
        # Tests need visible browser for accurate interaction
        playwright, browser, page = setup_browser(headless=False)
        
        try:
            # Initialize test executor with Playwright page
            executor = TestExecutor(
                page=page,
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
            # Clean up Playwright resources
            if page:
                page.close()
            if browser:
                browser.close()
            if playwright:
                playwright.stop()

    except Exception as e:
        logger.error(f"Error running tests: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/screenshots/<path:filename>')
def serve_screenshot(filename):
    """Serve screenshot files."""
    return send_file(os.path.join(app.config['TEST_OUTPUT_DIR'], 'screenshots', filename))

@app.route('/test_output/<path:filename>')
def serve_test_output(filename):
    """Serve test output files (human instructions and automation scripts)."""
    try:
        file_path = os.path.join(app.config['TEST_OUTPUT_DIR'], 'test_output', filename)
        mimetype = 'text/markdown' if filename.endswith('.md') else 'text/x-python'
        return send_file(
            file_path,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"Error serving test output file: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'File not found'
        }), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)