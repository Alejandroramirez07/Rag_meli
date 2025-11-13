# tests/run_tests.py
import unittest
import sys
import os
from pathlib import Path
import importlib.util

def import_from_path(module_name, file_path):
    """Import a module from a specific file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_tests():
    """Discover and run all tests in the tests directory"""
    
    # Check if Streamlit is running
    try:
        import requests
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code != 200:
            print("❌ ERROR: Streamlit app is not running on http://localhost:8501")
            print("💡 Please start your app first: streamlit run main_workflow.py")
            return 1
    except:
        print("❌ ERROR: Streamlit app is not running on http://localhost:8501")
        print("💡 Please start your app first: streamlit run main_workflow.py")
        return 1
    
    print("✅ Streamlit app is running")
    
    # Import test modules directly
    try:
        # Import test modules using relative paths
        test_config = import_from_path("test_config", "test_config.py")
        test_base = import_from_path("test_base", "test_base.py")
        test_authentication = import_from_path("test_authentication", "test_authentication.py")
        test_main_app = import_from_path("test_main_app", "test_main_app.py")
        test_admin_features = import_from_path("test_admin_features", "test_admin_features.py")
        
        print("✅ All test modules imported successfully")
    except Exception as e:
        print(f"❌ Error importing test modules: {e}")
        return 1
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases directly
    suite.addTests(loader.loadTestsFromModule(test_authentication))
    suite.addTests(loader.loadTestsFromModule(test_main_app))
    suite.addTests(loader.loadTestsFromModule(test_admin_features))
    
    print(f"📊 Loaded {suite.countTestCases()} test cases")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*50)
    print("📋 TEST SUMMARY")
    print("="*50)
    print(f"✅ Tests passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Tests failed: {len(result.failures)}")
    print(f"⚠️  Tests with errors: {len(result.errors)}")
    print(f"📊 Total tests: {result.testsRun}")
    
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests())