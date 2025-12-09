#!/usr/bin/env python3
"""
Wrapper script to run EDGAR data extraction with proper environment setup
"""

import subprocess
import sys
import os

def run_edgar_extraction():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the virtual environment python
    venv_python = os.path.join(script_dir, 'edgar_env', 'bin', 'python')
    
    # Path to the extraction script
    extraction_script = os.path.join(script_dir, 'edgar_data_extractor.py')
    
    # Check if virtual environment exists
    if not os.path.exists(venv_python):
        print("Error: Virtual environment not found. Please run setup first.")
        return 1
    
    # Check if extraction script exists
    if not os.path.exists(extraction_script):
        print("Error: EDGAR extraction script not found.")
        return 1
    
    try:
        # Run the extraction script using the virtual environment python
        print("Starting EDGAR data extraction...")
        result = subprocess.run([venv_python, extraction_script], 
                              capture_output=True, text=True, cwd=script_dir)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr, file=sys.stderr)
        
        return result.returncode
        
    except Exception as e:
        print(f"Error running extraction: {e}")
        return 1

if __name__ == "__main__":
    exit(run_edgar_extraction())