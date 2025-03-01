#!/usr/bin/env python3
"""
Example script to test the automated testing framework.
"""

import os
import sys
from pathlib import Path

def install_package():
    """Install the package in development mode."""
    project_root = Path(__file__).resolve().parent
    print(f"Installing package from {project_root}...")
    if sys.platform.startswith('win'):
        os.system(f'pip install -e "{project_root}"')
    else:
        os.system(f'pip install -e {project_root}')

def main():
    """Run a simple test to verify the framework."""
    # First, ensure the package is installed
    install_package()
    
    print("\nInitializing test framework...")
    
    # Import our package
    from src.utils import ConfigLoader
    from src.test_engine import ScenarioParser
    from src.reporting import TestLogger

    try:
        # Load configuration
        config_loader = ConfigLoader('examples/config.yaml')
        config = config_loader.get_test_config()
        browser_config = config_loader.get_browser_config()

        # Set up logging
        logger = TestLogger(config.log_dir)
        test_logger = logger.get_logger('test_example')
        test_logger.info("Starting test example...")

        # Parse test scenarios
        scenario_parser = ScenarioParser()
        scenarios = scenario_parser.parse_scenario_file('examples/test_scenarios.yaml')
        
        if not scenarios:
            test_logger.error("No test scenarios found!")
            return 1

        test_logger.info(f"Found {len(scenarios)} test scenarios")
        test_logger.info("Framework initialized successfully!")
        
        # Print the first scenario details as verification
        test_scenario = scenarios[0]
        test_logger.info("\nFirst Test Scenario Details:")
        test_logger.info(f"Name: {test_scenario.name}")
        test_logger.info(f"Description: {test_scenario.description}")
        test_logger.info("Steps:")
        for i, step in enumerate(test_scenario.steps, 1):
            test_logger.info(f"{i}. {step.description}")

        return 0

    except Exception as e:
        print(f"Error during framework test: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())