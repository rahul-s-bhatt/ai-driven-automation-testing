"""
Dual-mode test scenario package supporting both human and automation testing.
"""

from .parser import (
    DualModeParser,
    EnhancedTestScenario,
    EnhancedTestStep,
    AutomationConfig,
    TestModes
)

from .generators import (
    HumanInstructionsGenerator,
    AutomationGenerator
)

__all__ = [
    'DualModeParser',
    'EnhancedTestScenario',
    'EnhancedTestStep',
    'AutomationConfig',
    'TestModes',
    'HumanInstructionsGenerator',
    'AutomationGenerator'
]