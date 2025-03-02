"""
Test scenario generators for human and automation modes.
"""

from typing import List, Dict
from pathlib import Path
from datetime import datetime
from .parser import EnhancedTestScenario, EnhancedTestStep

class HumanInstructionsGenerator:
    """Generates human-readable test instructions."""

    def generate_markdown(self, scenario: EnhancedTestScenario) -> str:
        """Generate markdown formatted instructions for manual testing."""
        lines = [
            f"# {scenario.name}",
            f"\n{scenario.description}\n",
            "## Prerequisites",
            f"- {scenario.modes.human.get('preparation', 'No specific preparation required')}\n",
            "## Steps"
        ]

        for i, step in enumerate(scenario.steps, 1):
            lines.append(f"{i}. [ ] {step.human_instruction or step.description}")
            if step.value:
                lines.append(f"   - Input: `{step.value}`")
            if step.timeout:
                lines.append(f"   - Wait up to {step.timeout} seconds")

        lines.extend([
            "\n## Success Criteria",
            f"- {scenario.modes.human.get('success_criteria', 'No specific success criteria defined')}"
        ])

        return "\n".join(lines)

    def generate_test_plan(self, scenarios: List[EnhancedTestScenario], output_dir: str):
        """Generate a complete test plan document for all scenarios."""
        output_path = Path(output_dir) / f"manual_test_plan_{datetime.now():%Y%m%d_%H%M%S}.md"
        
        content = [
            "# Manual Test Plan",
            f"\nGenerated: {datetime.now():%Y-%m-%d %H:%M:%S}\n",
            "## Overview",
            f"This test plan contains {len(scenarios)} scenarios to be executed manually.\n"
        ]

        for i, scenario in enumerate(scenarios, 1):
            content.extend([
                f"## Scenario {i}: {scenario.name}",
                "\n### Tags",
                ", ".join(scenario.tags),
                "\n" + self.generate_markdown(scenario),
                "\n---\n"
            ])

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(content))
        return str(output_path)

class AutomationGenerator:
    """Generates Python test automation code."""

    def generate_python_test(self, scenario: EnhancedTestScenario) -> str:
        """Generate a Python test function for the scenario."""
        setup = scenario.modes.automation.get('setup', {})
        dependencies = setup.get('dependencies', [])
        test_data = setup.get('test_data', {})

        lines = [
            "import pytest",
            "from selenium.webdriver.common.by import By",
            "from selenium.webdriver.support.ui import WebDriverWait",
            "from selenium.webdriver.support import expected_conditions as EC",
            "",
            f"def test_{scenario.name.lower().replace(' ', '_')}(driver):",
            "    \"\"\"",
            f"    {scenario.description}",
            "    \"\"\"",
            "    wait = WebDriverWait(driver, 10)\n"
        ]

        # Add test data as variables
        for key, value in test_data.items():
            lines.append(f"    {key} = {repr(value)}")
        lines.append("")

        for step in scenario.steps:
            lines.extend(self._generate_step_code(step))

        return "\n".join(lines)

    def _generate_step_code(self, step: EnhancedTestStep) -> List[str]:
        """Generate Python code for a single test step."""
        if not step.automation:
            return [f"    # TODO: Implement step - {step.description}"]

        lines = [f"    # {step.description}"]
        selector = step.automation.selector
        wait_type = step.automation.wait_for
        timeout = step.automation.timeout or 10

        # Generate wait condition
        wait_condition = {
            'element_present': f"presence_of_element_located((By.CSS_SELECTOR, '{selector}'))",
            'element_visible': f"visibility_of_element_located((By.CSS_SELECTOR, '{selector}'))",
            'element_clickable': f"element_to_be_clickable((By.CSS_SELECTOR, '{selector}'))"
        }.get(wait_type)

        if wait_condition:
            lines.append(f"    element = wait.until(EC.{wait_condition})")

        # Generate action code
        if step.action == 'click':
            lines.append("    element.click()")
        elif step.action == 'type':
            lines.append(f"    element.send_keys({repr(step.value)})")
        elif step.action == 'verify':
            for assertion in step.automation.assertions or []:
                lines.extend(self._generate_assertion_code(assertion))

        lines.append("")
        return lines

    def _generate_assertion_code(self, assertion: Dict) -> List[str]:
        """Generate assertion code based on assertion type."""
        assertion_type = assertion['type']
        selector = assertion.get('selector', '')
        
        if assertion_type == 'element_visible':
            return [
                f"    assert wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '{selector}')))",
                "    is not None, 'Element should be visible'"
            ]
        elif assertion_type == 'text_present':
            return [
                f"    element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '{selector}')))",
                f"    assert {repr(assertion['text'])} in element.text, 'Text should be present'"
            ]
        elif assertion_type == 'minimum_elements':
            return [
                f"    elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '{selector}')))",
                f"    assert len(elements) >= {assertion['count']}, 'Should have minimum number of elements'"
            ]
        
        return [f"    # TODO: Implement {assertion_type} assertion"]

    def generate_test_suite(self, scenarios: List[EnhancedTestScenario], output_dir: str):
        """Generate a complete test suite file for all scenarios."""
        output_path = Path(output_dir) / f"test_generated_{datetime.now():%Y%m%d_%H%M%S}.py"
        
        content = [
            "import pytest",
            "from selenium.webdriver.common.by import By",
            "from selenium.webdriver.support.ui import WebDriverWait",
            "from selenium.webdriver.support import expected_conditions as EC",
            "",
            "@pytest.fixture",
            "def wait(driver):",
            "    return WebDriverWait(driver, 10)",
            ""
        ]

        for scenario in scenarios:
            content.append(self.generate_python_test(scenario))

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(content))
        return str(output_path)