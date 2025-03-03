"""
Simple test script for dual-mode generators.
"""

print("Starting generator test...")

from pathlib import Path
from src.test_engine.dual_mode.generators import HumanInstructionsGenerator, AutomationGenerator

def test_generators():
    """Test the dual-mode generators directly."""
    print("\nInitializing generators...")
    human_gen = HumanInstructionsGenerator()
    auto_gen = AutomationGenerator()

    # Create a simple test scenario
    test_scenario = {
        'name': 'Test Login Form',
        'description': 'Verify login form functionality',
        'tags': ['login', 'form'],
        'modes': {
            'human': {
                'preparation': 'Ensure test account credentials are ready',
                'success_criteria': 'Successfully log in with valid credentials'
            },
            'automation': {
                'setup': {
                    'dependencies': ['selenium', 'pytest'],
                    'test_data': {
                        'username': 'test@example.com',
                        'password': 'password123'
                    }
                }
            }
        },
        'steps': [
            {
                'description': 'Enter login credentials',
                'action': 'type',
                'target': 'username field',
                'value': 'test@example.com',
                'human_instruction': 'Type the test email into the username field',
                'automation': {
                    'selector': '#username',
                    'wait_for': 'element_present'
                }
            }
        ]
    }

    print("\nGenerating test outputs...")
    output_dir = Path('test_output/simple_test')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate human instructions
    print("\nGenerating human instructions...")
    human_output = human_gen.generate_test_plan([test_scenario], str(output_dir))
    print(f"Human instructions saved to: {human_output}")

    # Generate automation script
    print("\nGenerating automation script...")
    auto_output = auto_gen.generate_test_suite([test_scenario], str(output_dir))
    print(f"Automation script saved to: {auto_output}")

    # Try to read and display the generated files
    print("\nReading generated files:")
    try:
        with open(human_output, 'r') as f:
            print("\nHuman Instructions (first 5 lines):")
            for i, line in enumerate(f):
                if i < 5:
                    print(line.rstrip())
                else:
                    break
    except Exception as e:
        print(f"Error reading human instructions: {e}")

    try:
        with open(auto_output, 'r') as f:
            print("\nAutomation Script (first 5 lines):")
            for i, line in enumerate(f):
                if i < 5:
                    print(line.rstrip())
                else:
                    break
    except Exception as e:
        print(f"Error reading automation script: {e}")

if __name__ == "__main__":
    test_generators()