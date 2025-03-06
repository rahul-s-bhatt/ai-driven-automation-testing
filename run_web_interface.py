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
        # Get port from environment variable or use 5000 as default
        port = int(os.environ.get('PORT', 5000))
        host = '0.0.0.0'  # Listen on all interfaces
        debug = os.environ.get('FLASK_ENV') != 'production'

        print("""
Website Testing Framework - Web Interface

The web interface will be available at:
    http://{}:{}

You can:
1. Enter any website URL to test
2. Write test steps in plain English
3. See real-time test execution results
4. View screenshots and error reports

Press Ctrl+C to stop the server
""".format('localhost' if debug else 'your-app-url', port))
        # Get port from environment variable or use 5000 as default
        port = int(os.environ.get('PORT', 5000))
        
        # Set debug mode based on environment
        debug = os.environ.get('FLASK_ENV') != 'production'
        
        # Run the Flask app
        app.run(
            host='0.0.0.0',  # Listen on all interfaces
            port=port,
            debug=debug
        )

    except ImportError as e:
        print(f"Error: Import failed - {str(e)}")
        print(f"Python path: {sys.path}")
        print("Current directory:", os.getcwd())
        print("Please run: pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"Error starting web interface: {str(e)}")
        print(f"Python path: {sys.path}")
        print("Current directory:", os.getcwd())
        return 1

if __name__ == '__main__':
    sys.exit(main())