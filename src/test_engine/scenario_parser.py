"""
Scenario Parser module for processing test scenarios.

This module provides functionality to parse test scenarios from YAML files into
executable test steps.
"""

from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum, auto
import yaml
import re
from pathlib import Path

class ActionType(Enum):
    """Enumeration of supported test actions."""
    CLICK = auto()
    TYPE = auto()
    SELECT = auto()
    VERIFY = auto()
    WAIT = auto()
    SCROLL = auto()
    HOVER = auto()
    ASSERT = auto()

@dataclass
class TestStep:
    """Represents a single step in a test scenario."""
    description: str
    action: ActionType
    target: str
    value: Optional[str] = None
    timeout: int = 10

@dataclass
class TestScenario:
    """Represents a complete test scenario."""
    name: str
    description: str
    steps: List[TestStep]
    tags: List[str]

class ScenarioParser:
    """Main class for parsing test scenarios from YAML files."""

    def __init__(self):
        """Initialize the scenario parser."""
        self.action_mappings = {
            'click': ActionType.CLICK,
            'type': ActionType.TYPE,
            'select': ActionType.SELECT,
            'verify': ActionType.VERIFY,
            'wait': ActionType.WAIT,
            'scroll': ActionType.SCROLL,
            'hover': ActionType.HOVER,
            'assert': ActionType.ASSERT
        }

        self.scroll_patterns = {
            'end': r'(?:scroll )?(?:down )?(?:to |till |until )?(?:the )?(?:bottom|end)(?:of (?:the )?page)?',
            'top': r'(?:scroll )?(?:up )?(?:to |till |until )?(?:the )?top(?:of (?:the )?page)?',
            'up': r'scroll up(?: (\d+))?',
            'down': r'scroll down(?: (\d+))?',
            'left': r'scroll left(?: (\d+))?',
            'right': r'scroll right(?: (\d+))?',
            'element': r'scroll (?:to|into view) (?:the )?(.+)',
        }

    def parse_scenario_file(self, file_path: str) -> List[TestScenario]:
        """
        Parse test scenarios from a YAML file.

        Args:
            file_path: Path to the YAML file containing test scenarios

        Returns:
            List[TestScenario]: List of parsed test scenarios
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Scenario file not found: {file_path}")

        with open(path, 'r') as f:
            yaml_content = yaml.safe_load(f)

        if not isinstance(yaml_content, dict) or 'scenarios' not in yaml_content:
            raise ValueError("Invalid scenario file format. Expected 'scenarios' key.")

        scenarios = []
        for scenario_data in yaml_content['scenarios']:
            scenario = self._parse_scenario(scenario_data)
            scenarios.append(scenario)

        return scenarios

    def _parse_scenario(self, scenario_data: Dict) -> TestScenario:
        """Parse a single scenario from YAML data."""
        if not isinstance(scenario_data, dict):
            raise ValueError("Invalid scenario data format")

        name = scenario_data.get('name', 'Unnamed Scenario')
        description = scenario_data.get('description', '')
        tags = scenario_data.get('tags', [])
        steps_data = scenario_data.get('steps', [])

        if not isinstance(steps_data, list):
            raise ValueError("Steps must be a list")
        
        steps = []
        for step_text in steps_data:
            if not isinstance(step_text, str):
                raise ValueError(f"Invalid step format in scenario '{name}': {step_text}")
            
            step = self._parse_step(step_text)
            if step:
                steps.append(step)

        return TestScenario(
            name=name,
            description=description,
            steps=steps,
            tags=tags
        )

    def _parse_step(self, step_text: str) -> Optional[TestStep]:
        """Parse a single step from its description."""
        description = step_text.strip().lower()

        # Handle scroll actions first as they have multiple patterns
        scroll_step = self._parse_scroll_step(description)
        if scroll_step:
            return scroll_step

        # Click action
        if description.startswith('click'):
            target = description.replace('click on', '').replace('click', '').strip()
            return TestStep(description, ActionType.CLICK, target)

        # Type action
        if description.startswith(('type', 'enter')):
            parts = description.split(' into ')
            if len(parts) == 2:
                value = parts[0].replace('type', '').replace('enter', '').strip()
                target = parts[1].strip()
                # Remove quotes if present
                value = value.strip('"\'')
                return TestStep(description, ActionType.TYPE, target, value)

        # Select action
        if description.startswith('select'):
            parts = description.split(' from ')
            if len(parts) == 2:
                value = parts[0].replace('select', '').strip()
                target = parts[1].strip()
                value = value.strip('"\'')
                return TestStep(description, ActionType.SELECT, target, value)

        # Verify action
        if description.startswith(('verify', 'check')):
            if ' appears' in description:
                target = description.split(' appears')[0]
                target = target.replace('verify that', '').replace('verify', '').strip()
                return TestStep(description, ActionType.VERIFY, target)
            elif ' contains' in description:
                parts = description.split(' contains ')
                if len(parts) == 2:
                    target = parts[0].replace('verify that', '').replace('verify', '').strip()
                    value = parts[1].strip().strip('"\'')
                    return TestStep(description, ActionType.VERIFY, target, value)

        # Wait action
        if description.startswith('wait'):
            # Extract timeout if specified
            timeout_match = re.search(r'for (\d+) seconds?', description)
            timeout = int(timeout_match.group(1)) if timeout_match else 10
            
            # Extract target
            target = 'page'  # Default to page
            if ' for the ' in description:
                target = description.split(' for the ')[1].split(' for ')[0].strip()
            elif ' the ' in description:
                target = description.split(' the ')[1].split(' for ')[0].strip()
            
            return TestStep(description, ActionType.WAIT, target, timeout=timeout)

        # Hover action
        if description.startswith(('hover', 'move')):
            target = description.replace('hover over', '').replace('move to', '').strip()
            return TestStep(description, ActionType.HOVER, target)

        # Assert action
        if description.startswith(('assert', 'expect')):
            if ' contains' in description:
                parts = description.split(' contains ')
                if len(parts) == 2:
                    target = parts[0].replace('assert that', '').replace('assert', '').strip()
                    value = parts[1].strip().strip('"\'')
                    return TestStep(description, ActionType.ASSERT, target, value)

        return None

    def _parse_scroll_step(self, description: str) -> Optional[TestStep]:
        """Parse scroll commands with support for various formats."""
        for scroll_type, pattern in self.scroll_patterns.items():
            match = re.match(pattern, description)
            if match:
                if scroll_type == 'end':
                    return TestStep(description, ActionType.SCROLL, 'down till end')
                elif scroll_type == 'top':
                    return TestStep(description, ActionType.SCROLL, 'up till top')
                elif scroll_type in {'up', 'down', 'left', 'right'}:
                    amount = match.group(1) if match.groups() else None
                    return TestStep(description, ActionType.SCROLL, scroll_type, value=amount)
                elif scroll_type == 'element':
                    target = match.group(1)
                    return TestStep(description, ActionType.SCROLL, target)
        
        return None