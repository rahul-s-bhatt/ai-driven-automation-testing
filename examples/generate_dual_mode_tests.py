"""
Example script demonstrating the dual-mode test generation capabilities.
"""

import os
from pathlib import Path
from src.test_engine.dual_mode.parser import DualModeParser
from src.test_engine.dual_mode.generators import HumanInstructionsGenerator, AutomationGenerator

def main():
    """Generate both human and automation test outputs from dual-mode scenarios."""
    # Initialize components
    parser = DualModeParser()
    human_generator = HumanInstructionsGenerator()
    automation_generator = AutomationGenerator()

    # Load and parse the enhanced test scenarios
    scenario_file = 'examples/dual_mode_scenario.yaml'
    scenarios = parser.parse_file(scenario_file)

    # Create output directory
    output_dir = Path('test_output/dual_mode')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate human-readable test plan
    human_output = human_generator.generate_test_plan(scenarios, str(output_dir))
    print(f"\nGenerated human test plan: {human_output}")

    # Generate automated test suite
    automation_output = automation_generator.generate_test_suite(scenarios, str(output_dir))
    print(f"Generated automation test suite: {automation_output}")

    # Print sample of both outputs
    print("\nSample of human test plan:")
    print("-" * 40)
    with open(human_output, 'r') as f:
        print(f.read()[:500] + "...\n")

    print("\nSample of automation test suite:")
    print("-" * 40)
    with open(automation_output, 'r') as f:
        print(f.read()[:500] + "...")

if __name__ == "__main__":
    main()