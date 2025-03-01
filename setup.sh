#!/bin/bash

# Setup script for Website Testing Framework

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
if [ -f "venv/Scripts/activate" ]; then
    # Windows
    source venv/Scripts/activate
else
    # Unix/Linux/Mac
    source venv/bin/activate
fi

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Install the package in development mode
echo "Installing package in development mode..."
pip install -e .

# Create necessary directories
echo "Creating output directories..."
mkdir -p test_output/screenshots
mkdir -p test_output/reports
mkdir -p test_output/logs

echo """
Setup complete! You can now:

1. Start the web interface:
   python run_web_interface.py

2. Run tests via command line:
   python src/main.py -t examples/test_scenarios.yaml -u https://your-website.com

3. Open your browser and go to:
   http://localhost:5000

For more information, see README.md
"""