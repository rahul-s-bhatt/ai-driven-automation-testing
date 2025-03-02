"""
Example script demonstrating enhanced web analysis and test execution capabilities.
"""
import os
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from src.web_analyzer.scraping_analyzer import ScrapingAnalyzer
from src.web_analyzer.services.analysis_service import WebAnalysisService
from src.test_engine.test_executor import TestExecutor
from src.test_engine.scenario_parser import TestScenario
from src.reporting.logger import setup_logger

def load_test_scenario(file_path: str) -> list:
    """Load test scenarios from YAML file."""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def setup_webdriver() -> webdriver.Chrome:
    """Setup Chrome WebDriver with optimal configuration."""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    # Enable better logging
    chrome_options.set_capability('goog:loggingPrefs', {
        'browser': 'ALL',
        'performance': 'ALL'
    })
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def analyze_website(url: str, driver: webdriver.Chrome):
    """Perform enhanced website analysis."""
    print("\n=== Starting Enhanced Website Analysis ===")
    
    # Initialize analysis service
    analysis_service = WebAnalysisService(driver)
    
    # Perform analysis
    try:
        analysis_result = analysis_service.analyze_page(url)
        
        print("\nPage Structure Analysis:")
        print("-" * 30)
        
        if 'tag_analysis' in analysis_result:
            tag_analysis = analysis_result['tag_analysis']
            print("\nTag Patterns:")
            for pattern_type, patterns in tag_analysis.get('tag_patterns', {}).items():
                print(f"\n{pattern_type.capitalize()}:")
                for pattern in patterns:
                    print(f"- {pattern}")

        if 'structure_analysis' in analysis_result:
            structure = analysis_result['structure_analysis']
            print("\nStructure Analysis:")
            print(f"Layout Type: {structure.get('layout', {}).get('layout_type', 'unknown')}")
            print("\nDynamic Content:")
            dynamic = structure.get('dynamic_content', {})
            for key, value in dynamic.items():
                print(f"- {key}: {value}")

        if 'element_suggestions' in analysis_result:
            print("\nSuggested Elements:")
            for suggestion in analysis_result['element_suggestions']:
                print(f"\n- Type: {suggestion.get('type')}")
                print(f"  Selector: {suggestion.get('selector')}")
                print(f"  Confidence: {suggestion.get('confidence')}")

    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        raise

def execute_test_scenarios(driver: webdriver.Chrome, scenarios: list):
    """Execute test scenarios with enhanced capabilities."""
    print("\n=== Starting Enhanced Test Execution ===")
    
    # Initialize test executor with screenshot directory
    screenshot_dir = os.path.join('test_output', 'screenshots')
    executor = TestExecutor(driver, screenshot_dir=screenshot_dir)
    
    for scenario_data in scenarios:
        print(f"\nExecuting Scenario: {scenario_data['name']}")
        print("-" * 30)
        
        # Create test scenario
        scenario = TestScenario(
            name=scenario_data['name'],
            description=scenario_data['description'],
            steps=scenario_data['steps']
        )
        
        # Execute scenario
        try:
            success, errors = executor.execute_scenario(scenario)
            
            if success:
                print(f"✓ Scenario '{scenario.name}' completed successfully")
            else:
                print(f"✗ Scenario '{scenario.name}' failed:")
                for error in errors:
                    print(f"  - {error}")
                    
        except Exception as e:
            print(f"Error executing scenario: {str(e)}")

def main():
    """Main execution function."""
    # Setup logging
    logger = setup_logger()
    
    # Load test scenarios
    scenarios = load_test_scenario('examples/enhanced_test_scenario.yaml')
    
    # Test URL (replace with actual test website)
    test_url = "https://example.com"
    
    # Initialize WebDriver
    driver = setup_webdriver()
    
    try:
        # Perform enhanced analysis
        analyze_website(test_url, driver)
        
        # Execute test scenarios
        execute_test_scenarios(driver, scenarios)
        
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        raise
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()