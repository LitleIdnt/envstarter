#!/usr/bin/env python3
"""
🧪 ENHANCED APP TEST 🧪
Quick test of the enhanced main application.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_enhanced_imports():
    """Test enhanced app imports."""
    print("🧪 Testing enhanced app imports...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        print("  ✅ PyQt6.QtWidgets imported")
    except ImportError as e:
        print(f"  ❌ PyQt6 import failed: {e}")
        return False
    
    try:
        from src.envstarter.core.enhanced_app_controller import EnhancedAppController
        print("  ✅ EnhancedAppController imported")
    except ImportError as e:
        print(f"  ❌ EnhancedAppController import failed: {e}")
        return False
    
    try:
        from src.envstarter.gui.multi_environment_dashboard import MultiEnvironmentDashboard
        print("  ✅ MultiEnvironmentDashboard imported")
    except ImportError as e:
        print(f"  ❌ MultiEnvironmentDashboard import failed: {e}")
        return False
    
    return True

def test_controller_creation():
    """Test creating the enhanced controller."""
    print("\n🧪 Testing controller creation...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from src.envstarter.core.enhanced_app_controller import EnhancedAppController
        
        # Create minimal QApplication for testing
        if not QApplication.instance():
            app = QApplication([])
        
        controller = EnhancedAppController()
        print("  ✅ EnhancedAppController created successfully")
        
        # Test basic methods
        environments = controller.get_environments()
        print(f"  ✅ Found {len(environments)} environments")
        
        config = controller.get_config()
        print(f"  ✅ Configuration loaded: {len(config)} settings")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Controller creation failed: {e}")
        return False

def main():
    """Run enhanced app tests."""
    print("🚀 ENHANCED APP TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Enhanced Imports", test_enhanced_imports),
        ("Controller Creation", test_controller_creation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🔬 Running: {test_name}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"  ✅ {test_name} PASSED")
            else:
                print(f"  ❌ {test_name} FAILED")
                
        except Exception as e:
            print(f"  💥 {test_name} CRASHED: {e}")
            results.append((test_name, False))
    
    # Results summary
    print("\n" + "=" * 50)
    print("📊 ENHANCED APP TEST RESULTS")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Enhanced app is ready!")
        print("\n💡 You can now run:")
        print("   python src/envstarter/enhanced_main.py")
        return True
    else:
        print(f"\n💥 SOME TESTS FAILED - Check the issues above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)