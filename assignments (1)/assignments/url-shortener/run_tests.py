#!/usr/bin/env python3
"""
Test runner for URL Shortener service
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests for the URL shortener service"""
    print("=" * 50)
    print("Running URL Shortener Tests")
    print("=" * 50)
    
    # Change to the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    try:
        # Run pytest with verbose output
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("\n" + "=" * 50)
            print("✅ All tests passed!")
            print("=" * 50)
            return True
        else:
            print("\n" + "=" * 50)
            print("❌ Some tests failed!")
            print("=" * 50)
            return False
            
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

def run_specific_test(test_name):
    """Run a specific test"""
    print(f"Running test: {test_name}")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            f"tests/test_basic.py::{test_name}",
            "-v"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running test: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
        sys.exit(0 if success else 1)
    else:
        # Run all tests
        success = run_tests()
        sys.exit(0 if success else 1) 