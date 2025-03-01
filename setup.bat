@echo off
echo Setting up Website Testing Framework...

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

REM Install the package in development mode
echo Installing package in development mode...
pip install -e .

REM Create necessary directories
echo Creating output directories...
if not exist "test_output\screenshots" mkdir test_output\screenshots
if not exist "test_output\reports" mkdir test_output\reports
if not exist "test_output\logs" mkdir test_output\logs

echo.
echo Setup complete! You can now:
echo.
echo 1. Start the web interface:
echo    python run_web_interface.py
echo.
echo 2. Run tests via command line:
echo    python src/main.py -t examples/test_scenarios.yaml -u https://your-website.com
echo.
echo 3. Open your browser and go to:
echo    http://localhost:5000
echo.
echo For more information, see README.md
echo.

pause