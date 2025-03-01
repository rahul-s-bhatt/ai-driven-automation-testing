#!/usr/bin/env python3
"""
Installation and verification script for the automated testing framework.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return its output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            capture_output=True,
            cwd=cwd
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}", file=sys.stderr)
        print(f"Error output:\n{e.stdout}\n{e.stderr}", file=sys.stderr)
        return False

def setup_python_path():
    """Set up PYTHONPATH to include the project root."""
    project_root = Path(__file__).resolve().parent
    if 'PYTHONPATH' in os.environ:
        os.environ['PYTHONPATH'] = f"{project_root}{os.pathsep}{os.environ['PYTHONPATH']}"
    else:
        os.environ['PYTHONPATH'] = str(project_root)
    sys.path.insert(0, str(project_root))
    print(f"PYTHONPATH set to: {os.environ['PYTHONPATH']}")

def verify_imports():
    """Verify that all package components can be imported."""
    print("\nVerifying imports...")
    
    # Core components
    from src.web_analyzer import DOMParser, ElementClassifier, ElementContext
    print("✓ Web analyzer components imported successfully")
    
    from src.test_engine import (
        ScenarioParser, TestExecutor, TestValidator,
        TestScenario, TestStep, ActionType
    )
    print("✓ Test engine components imported successfully")
    
    from src.reporting import ReportGenerator, TestLogger
    print("✓ Reporting components imported successfully")
    
    from src.utils import ConfigLoader, ConfigurationError
    print("✓ Utility components imported successfully")
    
    return True

def verify_scenario_parsing():
    """Verify that scenario parsing works correctly."""
    print("\nVerifying scenario parsing...")
    
    from src.test_engine import ScenarioParser
    parser = ScenarioParser()
    scenarios = parser.parse_scenario_file('examples/test_scenarios.yaml')
    
    print(f"✓ Successfully parsed {len(scenarios)} scenarios")
    
    # Verify first scenario structure
    if scenarios:
        scenario = scenarios[0]
        print(f"\nFirst scenario details:")
        print(f"Name: {scenario.name}")
        print(f"Description: {scenario.description}")
        print(f"Number of steps: {len(scenario.steps)}")
        print(f"Tags: {', '.join(scenario.tags)}")
        print("\nFirst three steps:")
        for i, step in enumerate(scenario.steps[:3], 1):
            print(f"{i}. {step.description}")
    
    return True

def verify_configuration():
    """Verify that configuration loading works correctly."""
    print("\nVerifying configuration loading...")
    
    from src.utils import ConfigLoader
    config = ConfigLoader('examples/config.yaml')
    
    browser_config = config.get_browser_config()
    print(f"✓ Browser configuration loaded: {browser_config.name}")
    
    test_config = config.get_test_config()
    print(f"✓ Test configuration loaded: {test_config.base_url}")
    
    return True

def setup_directories():
    """Create necessary output directories."""
    print("\nSetting up directory structure...")
    
    project_root = Path(__file__).resolve().parent
    dirs = [
        'test_output/screenshots',
        'test_output/reports',
        'test_output/logs'
    ]
    
    for dir_path in dirs:
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {dir_path}")
    
    return True

def main():
    """Install dependencies and verify framework."""
    try:
        project_root = Path(__file__).resolve().parent
        os.chdir(project_root)
        
        # Set up Python path
        setup_python_path()
        
        print("Installing dependencies...")
        if not run_command("pip install -r requirements.txt"):
            return 1

        print("\nInstalling package in development mode...")
        if not run_command("pip install -e ."):
            return 1

        # Verify framework components
        if not all([
            verify_imports(),
            verify_scenario_parsing(),
            verify_configuration(),
            setup_directories()
        ]):
            return 1

        print("\n✅ Framework verification completed successfully!")
        print("\nYou can now run tests using:")
        print("python src/main.py -t examples/test_scenarios.yaml")
        return 0
        
    except Exception as e:
        import traceback
        print(f"\nError during verification: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())