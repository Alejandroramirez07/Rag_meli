# tests/debug_tests.py
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def debug_setup():
    print("🔍 DEBUG MODE - Checking test setup")
    
    print("\n1. Directory Structure:")
    print(f"   Current directory: {os.getcwd()}")
    print(f"   Script location: {__file__}")
    print(f"   Project root: {project_root}")
    
    print("\n2. Python Path:")
    for i, path in enumerate(sys.path[:5]):  # Show first 5 paths
        print(f"   {i+1}. {path}")
    
    print("\n3. Test Files in tests/ directory:")
    test_files = [f for f in os.listdir('.') if f.startswith('test_') and f.endswith('.py')]
    for file in test_files:
        print(f"   ✅ {file}")
    
    print("\n4. Import Tests:")
    try:
        from selenium import webdriver
        print("   ✅ selenium: SUCCESS")
    except ImportError as e:
        print(f"   ❌ selenium: FAILED - {e}")
    
    try:
        import requests
        print("   ✅ requests: SUCCESS")
    except ImportError as e:
        print(f"   ❌ requests: FAILED - {e}")
    
    print("\n5. Streamlit Check:")
    try:
        import requests
        response = requests.get("http://localhost:8501", timeout=5)
        print(f"   ✅ Streamlit: RUNNING (HTTP {response.status_code})")
    except Exception as e:
        print(f"   ❌ Streamlit: NOT RUNNING - {e}")

if __name__ == "__main__":
    debug_setup()