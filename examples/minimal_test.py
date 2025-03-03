"""
Minimal test script to verify environment setup.
"""

import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current working directory: {sys.path[0]}")
print("Python path:")
for p in sys.path:
    print(f"  {p}")

print("\nTesting basic imports...")
try:
    import selenium
    print("Successfully imported selenium")
except ImportError as e:
    print(f"Failed to import selenium: {e}")

try:
    from pathlib import Path
    print("Successfully imported pathlib")
except ImportError as e:
    print(f"Failed to import pathlib: {e}")

print("\nTrying to create a directory...")
try:
    test_dir = Path('test_output/minimal_test')
    test_dir.mkdir(parents=True, exist_ok=True)
    print(f"Successfully created directory: {test_dir}")
    
    test_file = test_dir / 'test.txt'
    with open(test_file, 'w') as f:
        f.write('Test content')
    print(f"Successfully wrote to file: {test_file}")
    
    with open(test_file, 'r') as f:
        content = f.read()
    print(f"Successfully read from file: {content}")
except Exception as e:
    print(f"Error during file operations: {e}")

print("\nTest complete")