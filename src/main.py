#!/usr/bin/env python3
"""
Main entry point for the automated website testing framework.

This script provides a command-line interface to run tests and configure
the testing framework.
"""

import sys
import argparse
from pathlib import Path
import logging
from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

# Add the project root to Python path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.web_analyzer.dom_parser import DOMParser
from src.web_analyzer.element_classifier import ElementClassifier
from src.test_engine.scenario_parser import ScenarioParser
from src.test_engine.test_executor import TestExecutor
from src.test_engine.validator import TestValidator
from src.reporting.report_generator import ReportGenerator
from src.reporting.logger import TestLogger
from src.utils.config_loader import ConfigLoader, ConfigurationError

def setup_argument_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(
        description='Automated Website Testing Framework'
    )
    
    parser.add_argument(
        '-c', '--config',
        help='Path to configuration file',
        type=str,
        default=str(project_root / 'examples/config.yaml')
    )
    
    parser.add_argument(
        '-t', '--tests',
        help='Path to test scenarios file or directory',
        type=str,
        required=True
    )
    
    parser.add_argument(
        '-u', '--url',
        help='Target website URL (overrides config)',
        type=str
    )
    
    parser.add_argument(
        '--browser',
        help='Browser to use (chrome/firefox)',
        choices=['chrome', 'firefox'],
        type=str
    )
    
    parser.add_argument(
        '--headless',
        help='Run browser in headless mode',
        action='store_true'
    )
    
    return parser

def setup_webdriver(browser: str, headless: bool) -> webdriver.Remote:
    """
    Set up and configure WebDriver.

    Args:
        browser: Browser name ('chrome' or 'firefox')
        headless: Whether to run in headless mode

    Returns:
        webdriver.Remote: Configured WebDriver instance
    """
    if browser.lower() == 'chrome':
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        service = ChromeService(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    
    elif browser.lower() == 'firefox':
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument('--headless')
        service = FirefoxService(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=options)
    
    raise ValueError(f"Unsupported browser: {browser}")

def load_test_scenarios(path: str, parser: ScenarioParser) -> List:
    """
    Load test scenarios from file or directory.

    Args:
        path: Path to scenario file or directory
        parser: ScenarioParser instance

    Returns:
        List: List of parsed test scenarios
    """
    path_obj = Path(path)
    scenarios = []

    if path_obj.is_file():
        scenarios.extend(parser.parse_scenario_file(str(path_obj)))
    elif path_obj.is_dir():
        for file in path_obj.glob('*.yaml'):
            scenarios.extend(parser.parse_scenario_file(str(file)))
    else:
        raise FileNotFoundError(f"Test scenario path not found: {path}")

    return scenarios

def main():
    """Main entry point for the testing framework."""
    # Parse command line arguments
    parser = setup_argument_parser()
    args = parser.parse_args()

    try:
        # Load configuration
        config_loader = ConfigLoader(args.config)
        config = config_loader.get_test_config()
        browser_config = config_loader.get_browser_config()

        # Override configuration with command line arguments
        if args.url:
            config.base_url = args.url
        if args.browser:
            browser_config.name = args.browser
        if args.headless:
            browser_config.headless = True

        # Validate base URL
        if not config.base_url:
            raise ConfigurationError("No base URL provided. Use -u/--url option or set base_url in config file.")

        # Set up logging
        logger = TestLogger(config.log_dir)
        framework_logger = logger.get_logger('framework')
        framework_logger.info("Starting test framework...")
        framework_logger.info(f"Target URL: {config.base_url}")

        # Set up WebDriver
        driver = setup_webdriver(browser_config.name, browser_config.headless)
        driver.implicitly_wait(browser_config.implicit_wait)
        driver.set_page_load_timeout(browser_config.page_load_timeout)
        driver.set_window_size(*browser_config.window_size)

        try:
            # Initialize components
            dom_parser = DOMParser(driver)
            element_classifier = ElementClassifier()
            scenario_parser = ScenarioParser()
            test_executor = TestExecutor(
                driver=driver,
                screenshot_dir=config.screenshot_dir,
                base_url=config.base_url  # Pass base_url to TestExecutor
            )
            validator = TestValidator(driver, config.report_dir)
            report_generator = ReportGenerator(config.report_dir)

            # Load and execute test scenarios
            scenarios = load_test_scenarios(args.tests, scenario_parser)
            if not scenarios:
                framework_logger.error("No test scenarios found!")
                return 1

            framework_logger.info(f"Found {len(scenarios)} test scenarios")
            all_reports = []

            for scenario in scenarios:
                framework_logger.info(f"Executing scenario: {scenario.name}")
                logger.log_test_start(scenario.name)

                try:
                    # Execute test scenario
                    success, errors = test_executor.execute_scenario(scenario)
                    
                    # Validate results
                    validation_results = []
                    for step in scenario.steps:
                        result = validator.validate_step(step)
                        validation_results.append(result)

                    # Generate report
                    report = validator.generate_report(scenario, validation_results)
                    all_reports.append(report)

                    # Generate HTML report
                    html_report = report_generator.generate_html_report(report)
                    framework_logger.info(f"HTML report generated: {html_report}")

                    if errors:
                        framework_logger.error(f"Scenario failed with errors: {errors}")

                except Exception as e:
                    framework_logger.error(f"Error executing scenario {scenario.name}: {str(e)}")
                    logger.log_error(f"Scenario execution failed", e)

            # Generate summary report
            summary_report = report_generator.generate_summary_report(all_reports)
            framework_logger.info(f"Summary report generated: {summary_report}")

            return 0

        finally:
            # Ensure driver is always cleaned up
            driver.quit()

    except ConfigurationError as e:
        print(f"Configuration error: {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())