#!/usr/bin/env python3
"""
🧪 SIMPLE TEST SCRIPT 🧪
Quick test without PyQt6 dependencies to verify core functionality.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test basic imports without GUI components."""
    print("🧪 Testing basic imports...")
    
    try:
        from src.envstarter.core.models import Environment, Application, Website
        print("  ✅ Models imported successfully")
    except ImportError as e:
        print(f"  ❌ Models import failed: {e}")
        return False
    
    try:
        from src.envstarter.core.storage import ConfigManager
        print("  ✅ Storage manager imported successfully")
    except ImportError as e:
        print(f"  ❌ Storage manager import failed: {e}")
        return False
    
    return True


def test_model_creation():
    """Test creating environment models."""
    print("\n🧪 Testing model creation...")
    
    from src.envstarter.core.models import Environment, Application, Website
    
    try:
        # Test application model
        app = Application(name="Notepad", path="notepad.exe", arguments="")
        print(f"  ✅ Application created: {app.name}")
        
        # Test website model
        website = Website(name="Google", url="https://google.com")
        print(f"  ✅ Website created: {website.name}")
        
        # Test environment model
        env = Environment(
            name="Test Environment",
            description="Test environment for validation",
            applications=[app],
            websites=[website]
        )
        print(f"  ✅ Environment created: {env.name}")
        print(f"     📱 Applications: {len(env.applications)}")
        print(f"     🌐 Websites: {len(env.websites)}")
        
        # Test serialization
        env_dict = env.to_dict()
        restored_env = Environment.from_dict(env_dict)
        
        if restored_env.name == env.name:
            print("  ✅ Model serialization works correctly")
        else:
            print("  ❌ Model serialization failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Model creation failed: {e}")
        return False


def test_storage():
    """Test storage functionality."""
    print("\n🧪 Testing storage functionality...")
    
    try:
        from src.envstarter.core.storage import ConfigManager
        
        config_manager = ConfigManager()
        print("  ✅ ConfigManager created")
        
        # Test getting environments
        environments = config_manager.get_environments()
        print(f"  ✅ Found {len(environments)} sample environments")
        
        for i, env in enumerate(environments):
            print(f"     {i+1}. {env.name}: {len(env.applications)} apps, {len(env.websites)} sites")
        
        # Test configuration
        config = config_manager.get_config()
        print(f"  ✅ Configuration loaded: {len(config)} settings")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Storage test failed: {e}")
        return False


def main():
    """Run simple tests."""
    print("🚀 ENVSTARTER SIMPLE TEST SUITE")
    print("=" * 50)
    print("Testing core functionality without GUI dependencies...")
    print()
    
    tests = [
        ("Basic Imports", test_imports),
        ("Model Creation", test_model_creation),
        ("Storage System", test_storage),
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
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Core system is working!")
        print("\n💡 Next steps:")
        print("   1. Install PyQt6: pip install PyQt6")
        print("   2. Run: python src/envstarter/enhanced_main.py")
        print("   3. Try the new Multi-Environment Dashboard")
        return True
    else:
        print(f"\n💥 SOME TESTS FAILED")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)