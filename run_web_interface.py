#!/usr/bin/env python3
"""
Launch script for the web interface of the testing framework.
"""

import os
import sys
from pathlib import Path

def main():
    """Main entry point to start the web interface."""
    # Add project root to Python path
    project_root = Path(__file__).resolve().parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    try:
        from src.web_interface.server import app
        print("""
Website Testing Framework - Web Interface

The web interface will be available at:
    http://localhost:5000

You can:
1. Enter any website URL to test
2. Write test steps in plain English
3. See real-time test execution results
4. View screenshots and error reports

Press Ctrl+C to stop the server
""")
        # Run the Flask app
        app.run(debug=True)

    except ImportError as e:
        print("Error: Missing required dependencies.")
        print("Please run: pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"Error starting web interface: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())