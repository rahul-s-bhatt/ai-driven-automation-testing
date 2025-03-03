"""
Executor for dual-mode tests.
"""

import pytest
from pathlib import Path
import sys
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

class DualModeExecutor:
    """Executes both automated and manual tests generated from dual-mode scenarios."""

    def __init__(self, output_dir: str):
        """Initialize the executor with output directory."""
        self.output_dir = Path(output_dir)
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging for the executor."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(self.output_dir / 'test_execution.log')
            ]
        )

    def _setup_webdriver(self):
        """Set up ChromeDriver with standard options."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def execute_automated_tests(self, test_file: str):
        """Execute the automated test suite."""
        logger.info(f"Executing automated tests from: {test_file}")
        
        test_file = Path(test_file)
        if not test_file.exists():
            raise FileNotFoundError(f"Test file not found: {test_file}")

        # Add the test file's directory to Python path
        test_dir = str(test_file.parent)
        if test_dir not in sys.path:
            sys.path.insert(0, test_dir)

        try:
            # Create a pytest fixture for the webdriver
            @pytest.fixture(scope="module")
            def driver():
                browser = self._setup_webdriver()
                yield browser
                browser.quit()

            # Run the tests
            pytest.main([
                str(test_file),
                '-v',
                '--html=' + str(self.output_dir / 'automated_test_report.html'),
                '--self-contained-html'
            ])

        except Exception as e:
            logger.error(f"Error executing automated tests: {str(e)}")
            raise

    def prepare_manual_testing(self, instruction_file: str):
        """Prepare for manual testing by displaying instructions."""
        logger.info(f"Loading manual test instructions from: {instruction_file}")
        
        instruction_path = Path(instruction_file)
        if not instruction_path.exists():
            raise FileNotFoundError(f"Instruction file not found: {instruction_file}")

        try:
            with open(instruction_path) as f:
                instructions = f.read()
                
            logger.info("\nManual Test Instructions:")
            logger.info("=" * 50)
            logger.info(instructions)
            logger.info("=" * 50)
            
            # Save formatted instructions to an HTML file for better readability
            html_path = self.output_dir / 'manual_test_instructions.html'
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Manual Test Instructions</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    pre {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
                    .step {{ margin: 20px 0; }}
                    .success-criteria {{ 
                        background: #e6ffe6;
                        padding: 15px;
                        border-left: 4px solid #00cc00;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <h1>Manual Test Instructions</h1>
                <pre>{instructions}</pre>
            </body>
            </html>
            """
            html_path.write_text(html_content)
            logger.info(f"\nDetailed instructions available at: {html_path}")

        except Exception as e:
            logger.error(f"Error preparing manual test instructions: {str(e)}")
            raise

    def execute_all(self, automated_test_file: str, manual_instruction_file: str):
        """Execute both automated and manual tests."""
        try:
            # First run automated tests
            self.execute_automated_tests(automated_test_file)
            
            # Then prepare manual testing instructions
            self.prepare_manual_testing(manual_instruction_file)
            
        except Exception as e:
            logger.error(f"Error during test execution: {str(e)}")
            raise