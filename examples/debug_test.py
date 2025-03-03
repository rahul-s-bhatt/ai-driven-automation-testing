"""
Debug script to identify issues.
"""

print("Script starting...")

import os
import sys
from pathlib import Path

# Add project root to Python path
try:
    project_root = Path(__file__).resolve().parent.parent
    print(f"Project root: {project_root}")
    sys.path.insert(0, str(project_root))
    print("Added to Python path")
except Exception as e:
    print(f"Error setting up path: {e}")

# Try imports
try:
    print("\nTrying imports...")
    from src.test_engine.dual_mode.generators import HumanInstructionsGenerator, AutomationGenerator
    print("Successfully imported generators")
except Exception as e:
    print(f"Import error: {e}")
    import traceback
    print("\nTraceback:")
    traceback.print_exc()
    sys.exit(1)

def main():
    """Basic test of functionality."""
    print("\nStarting main function")
    try:
        # Create test directory
        output_dir = Path('test_output/debug_test')
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created output directory: {output_dir}")

        # Initialize generators
        print("Initializing generators...")
        human_gen = HumanInstructionsGenerator()
        auto_gen = AutomationGenerator()
        print("Generators initialized")

        # Simple test scenario
        test_scenario = {
            'name': 'Debug Test',
            'description': 'Simple test scenario',
            'tags': ['debug'],
            'modes': {
                'human': {
                    'preparation': 'Debug prep',
                    'success_criteria': 'Debug success'
                },
                'automation': {
                    'setup': {
                        'dependencies': ['pytest'],
                        'test_data': {}
                    }
                }
            },
            'steps': [
                {
                    'description': 'Debug step',
                    'action': 'verify',
                    'target': 'debug element',
                    'human_instruction': 'Check debug element',
                    'automation': {
                        'selector': '#debug',
                        'wait_for': 'element_present'
                    }
                }
            ]
        }

        print("\nGenerating outputs...")
        
        # Generate and check human instructions
        print("Generating human instructions...")
        human_file = human_gen.generate_test_plan([test_scenario], str(output_dir))
        print(f"Human instructions file: {human_file}")
        if os.path.exists(human_file):
            print("Human instructions file exists")
            with open(human_file, 'r') as f:
                print("\nFirst few lines of human instructions:")
                print(f.read()[:200])
        else:
            print("Human instructions file not found!")

        # Generate and check automation script
        print("\nGenerating automation script...")
        auto_file = auto_gen.generate_test_suite([test_scenario], str(output_dir))
        print(f"Automation script file: {auto_file}")
        if os.path.exists(auto_file):
            print("Automation script file exists")
            with open(auto_file, 'r') as f:
                print("\nFirst few lines of automation script:")
                print(f.read()[:200])
        else:
            print("Automation script file not found!")

    except Exception as e:
        print(f"\nError in main function: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("\nStarting debug test...")
    main()
    print("\nDebug test complete")