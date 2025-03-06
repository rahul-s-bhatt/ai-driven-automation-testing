#!/usr/bin/env python3
"""
Setup script to download and configure Chrome headless shell for the project.
This is particularly useful for Render.com deployments or when you can't install Chrome system-wide.
"""

import os
import sys
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path
import urllib.request
import zipfile

def get_chrome_url():
    """Get the appropriate Chrome download URL based on the platform."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "linux":
        if machine == "x86_64" or machine == "amd64":
            return "https://download-chromium.appspot.com/dl/Linux_x64?type=snapshots"
    elif system == "darwin":  # MacOS
        if machine == "x86_64" or machine == "amd64":
            return "https://download-chromium.appspot.com/dl/Mac?type=snapshots"
        elif machine == "arm64":
            return "https://download-chromium.appspot.com/dl/Mac_Arm?type=snapshots"
    elif system == "windows":
        return "https://download-chromium.appspot.com/dl/Win?type=snapshots"
    
    raise SystemError(f"Unsupported platform: {system} {machine}")

def download_chrome(chrome_dir):
    """Download and extract Chrome to the specified directory."""
    print("Downloading Chrome headless shell...")
    
    # Create temporary directory for download
    with tempfile.TemporaryDirectory() as temp_dir:
        # Download Chrome
        chrome_zip = os.path.join(temp_dir, "chrome.zip")
        url = get_chrome_url()
        urllib.request.urlretrieve(url, chrome_zip)
        
        # Extract to bin directory
        print("Extracting Chrome...")
        with zipfile.ZipFile(chrome_zip, 'r') as zip_ref:
            zip_ref.extractall(chrome_dir.parent)
        
        # On Linux/MacOS, make Chrome executable
        if platform.system() != "Windows":
            chrome_binary = chrome_dir / "chrome"
            if chrome_binary.exists():
                chrome_binary.chmod(0o755)
                print(f"Made Chrome executable: {chrome_binary}")

def main():
    """Main setup function."""
    try:
        # Get project root directory
        project_root = Path(__file__).resolve().parent
        chrome_dir = project_root / "bin" / "chrome-linux"
        
        # Create bin directory if it doesn't exist
        chrome_dir.parent.mkdir(parents=True, exist_ok=True)
        
        # Remove existing Chrome directory if it exists
        if chrome_dir.exists():
            shutil.rmtree(chrome_dir)
        
        # Download and extract Chrome
        download_chrome(chrome_dir)
        
        print("\nChrome headless shell has been successfully set up!")
        print(f"Location: {chrome_dir}")
        
    except Exception as e:
        print(f"Error setting up Chrome: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()