"""
Test script to verify dual-mode test generation and execution.
"""

import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.test_engine.dual_mode.parser import DualModeParser
from src.test_engine.dual_mode.generators import HumanInstructionsGenerator, AutomationGenerator
from src.test_engine.dual_mode.executor import DualModeExecutor

def generate_and_execute_tests():
    """Generate and execute both automated and manual tests from dual-mode scenarios."""
    try:
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
        
        # Generate tests
        logger.info("Generating test artifacts...")
        human_output = human_generator.generate_test_plan(scenarios, str(output_dir))
        automation_output = automation_generator.generate_test_suite(scenarios, str(output_dir))
        
        logger.info(f"Generated human test plan: {human_output}")
        logger.info(f"Generated automation test suite: {automation_output}")
        
        # Initialize and run the executor
        logger.info("\nInitializing test executor...")
        executor = DualModeExecutor(str(output_dir))
        
        # Execute both types of tests
        logger.info("\nExecuting dual-mode tests...")
        executor.execute_all(automation_output, human_output)
        
        logger.info("\nDual-mode testing complete!")
        
    except Exception as e:
        logger.error(f"Error during test execution: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    generate_and_execute_tests()