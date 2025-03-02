"""
Enhanced scenario parser supporting both human and automation modes.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import yaml
from pathlib import Path

@dataclass
class AutomationConfig:
    """Configuration for automation mode."""
    selector: str
    wait_for: str
    timeout: Optional[int] = None
    assertions: Optional[List[Dict[str, Any]]] = None

@dataclass
class TestModes:
    """Configuration for different test modes."""
    human: Dict[str, str]
    automation: Dict[str, Any]

@dataclass
class EnhancedTestStep:
    """Enhanced test step supporting both modes."""
    description: str
    action: str
    target: str
    value: Optional[str] = None
    timeout: Optional[int] = None
    human_instruction: Optional[str] = None
    automation: Optional[AutomationConfig] = None

@dataclass
class EnhancedTestScenario:
    """Enhanced test scenario supporting both modes."""
    name: str
    description: str
    tags: List[str]
    modes: TestModes
    steps: List[EnhancedTestStep]

class DualModeParser:
    """Parser for dual-mode test scenarios."""

    def parse_file(self, file_path: str) -> List[EnhancedTestScenario]:
        """Parse scenarios from a YAML file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Scenario file not found: {file_path}")

        with open(path, 'r') as f:
            content = yaml.safe_load(f)

        if not isinstance(content, dict) or 'scenarios' not in content:
            raise ValueError("Invalid scenario file format. Expected 'scenarios' key.")

        return [self._parse_scenario(scenario) for scenario in content['scenarios']]

    def _parse_scenario(self, data: Dict) -> EnhancedTestScenario:
        """Parse a single scenario."""
        if not isinstance(data, dict):
            raise ValueError("Invalid scenario data format")

        # Parse modes configuration
        modes = TestModes(
            human=data.get('modes', {}).get('human', {}),
            automation=data.get('modes', {}).get('automation', {})
        )

        # Parse steps
        steps = [self._parse_step(step) for step in data.get('steps', [])]

        return EnhancedTestScenario(
            name=data.get('name', 'Unnamed Scenario'),
            description=data.get('description', ''),
            tags=data.get('tags', []),
            modes=modes,
            steps=steps
        )

    def _parse_step(self, data: Dict) -> EnhancedTestStep:
        """Parse a single test step."""
        # Parse automation configuration if present
        automation_config = None
        if 'automation' in data:
            auto_data = data['automation']
            automation_config = AutomationConfig(
                selector=auto_data.get('selector', ''),
                wait_for=auto_data.get('wait_for', ''),
                timeout=auto_data.get('timeout'),
                assertions=auto_data.get('assertions', [])
            )

        return EnhancedTestStep(
            description=data.get('description', ''),
            action=data.get('action', ''),
            target=data.get('target', ''),
            value=data.get('value'),
            timeout=data.get('timeout'),
            human_instruction=data.get('human_instruction'),
            automation=automation_config
        )