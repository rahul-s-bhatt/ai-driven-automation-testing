"""
Standalone test of dual-mode test generation.
All necessary code included in one file for simplicity.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Basic test scenario structure
@dataclass
class TestScenario:
    name: str
    description: str
    steps: List[str]
    tags: List[str]
    human_instructions: List[str]
    automation_code: str

class SimpleAnalyzer:
    """Simple analyzer that creates test scenarios."""
    
    def analyze_element(self, element_type: str, selector: str) -> TestScenario:
        """Create a test scenario for an element."""
        steps = [
            f"Find the {element_type} element",
            f"Verify it is visible",
            f"Verify it is interactive"
        ]
        
        human_instructions = [
            f"1. Look for a {element_type} on the page",
            "2. Ensure it is clearly visible",
            "3. Check that you can interact with it"
        ]
        
        automation_code = f"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_{element_type.lower()}_element(driver):
    # Wait for element
    wait = WebDriverWait(driver, 10)
    element = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "{selector}"))
    )
    
    # Verify visibility
    assert element.is_displayed(), "Element should be visible"
    
    # Verify interactivity
    assert element.is_enabled(), "Element should be interactive"
"""
        
        return TestScenario(
            name=f"Test {element_type} Element",
            description=f"Verify {element_type} element functionality",
            steps=steps,
            tags=[element_type.lower(), "element-test"],
            human_instructions=human_instructions,
            automation_code=automation_code
        )

def generate_test_files(scenarios: List[TestScenario]) -> Dict[str, str]:
    """Generate test files from scenarios."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path('test_output/standalone_test')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate human instructions file
    human_file = output_dir / f'human_instructions_{timestamp}.md'
    human_content = []
    for scenario in scenarios:
        human_content.extend([
            f"# {scenario.name}",
            f"\n{scenario.description}\n",
            "## Steps\n",
            *scenario.human_instructions,
            "\n---\n"
        ])
    human_file.write_text('\n'.join(human_content))
    
    # Generate automation file
    auto_file = output_dir / f'automated_tests_{timestamp}.py'
    auto_content = [
        "import pytest",
        "from selenium import webdriver",
        "from selenium.webdriver.common.by import By",
        "from selenium.webdriver.support.ui import WebDriverWait",
        "from selenium.webdriver.support import expected_conditions as EC\n",
        "@pytest.fixture",
        "def driver():",
        "    driver = webdriver.Chrome()",
        "    yield driver",
        "    driver.quit()\n"
    ]
    for scenario in scenarios:
        auto_content.append(scenario.automation_code)
    auto_file.write_text('\n'.join(auto_content))
    
    return {
        'human_instructions': str(human_file),
        'automation_script': str(auto_file)
    }

def main():
    """Run standalone test."""
    print("Starting standalone test...")
    
    # Create analyzer
    analyzer = SimpleAnalyzer()
    
    # Generate test scenarios
    print("\nGenerating test scenarios...")
    scenarios = [
        analyzer.analyze_element("Button", "#submit-btn"),
        analyzer.analyze_element("Form", "#login-form"),
        analyzer.analyze_element("Navigation", "nav.main-nav")
    ]
    print(f"Generated {len(scenarios)} test scenarios")
    
    # Generate test files
    print("\nGenerating test files...")
    output_files = generate_test_files(scenarios)
    
    # Print results
    print("\nGenerated files:")
    for file_type, file_path in output_files.items():
        print(f"\n{file_type}:")
        print(f"Path: {file_path}")
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                print("\nFirst 200 characters:")
                print(content[:200])
        except Exception as e:
            print(f"Error reading file: {e}")

if __name__ == "__main__":
    print("Script starting...")
    main()
    print("\nScript complete")