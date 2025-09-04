#!/usr/bin/env python3
"""
Test script to verify EnvStarter installation and dependencies.
Run this script to check if EnvStarter can run properly on your system.
"""

import sys
import os
import importlib.util
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    print("Checking Python version...")
    version = sys.version_info
    required = (3, 8)
    
    if version >= required:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (FAILED)")
        print(f"    Required: Python {required[0]}.{required[1]} or higher")
        return False

def check_dependency(package_name, min_version=None):
    """Check if a package is installed and optionally check version."""
    try:
        if package_name == 'PyQt6':
            import PyQt6
            from PyQt6.QtCore import QT_VERSION_STR
            version = QT_VERSION_STR
            print(f"  ✓ {package_name} {version} (OK)")
        elif package_name == 'pystray':
            import pystray
            version = getattr(pystray, '__version__', 'unknown')
            print(f"  ✓ {package_name} {version} (OK)")
        elif package_name == 'Pillow':
            import PIL
            version = PIL.__version__
            print(f"  ✓ {package_name} {version} (OK)")
        elif package_name == 'psutil':
            import psutil
            version = psutil.__version__
            print(f"  ✓ {package_name} {version} (OK)")
        elif package_name == 'winreg':
            import winreg
            print(f"  ✓ {package_name} (built-in) (OK)")
        else:
            module = importlib.import_module(package_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"  ✓ {package_name} {version} (OK)")
        return True
    except ImportError:
        print(f"  ✗ {package_name} (MISSING)")
        return False
    except Exception as e:
        print(f"  ✗ {package_name} (ERROR: {e})")
        return False

def check_dependencies():
    """Check all required dependencies."""
    print("\nChecking dependencies...")
    
    dependencies = [
        'PyQt6',
        'pystray', 
        'Pillow',
        'psutil',
    ]
    
    if os.name == 'nt':  # Windows only
        dependencies.append('winreg')
    
    success = True
    for dep in dependencies:
        if not check_dependency(dep):
            success = False
    
    return success

def check_project_structure():
    """Check if project files are present."""
    print("\nChecking project structure...")
    
    required_files = [
        'src/envstarter/__init__.py',
        'src/envstarter/main.py',
        'src/envstarter/core/app_controller.py',
        'src/envstarter/core/models.py',
        'src/envstarter/core/storage.py',
        'src/envstarter/core/launcher.py',
        'src/envstarter/gui/environment_selector.py',
        'src/envstarter/gui/settings_dialog.py',
        'src/envstarter/utils/system_integration.py',
        'src/envstarter/utils/icons.py',
        'requirements.txt',
        'setup.py'
    ]
    
    success = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✓ {file_path} (OK)")
        else:
            print(f"  ✗ {file_path} (MISSING)")
            success = False
    
    return success

def check_envstarter_import():
    """Try to import EnvStarter modules."""
    print("\nChecking EnvStarter imports...")
    
    modules_to_test = [
        'src.envstarter',
        'src.envstarter.main',
        'src.envstarter.core.models',
        'src.envstarter.core.storage',
        'src.envstarter.core.launcher',
        'src.envstarter.core.app_controller',
        'src.envstarter.gui.environment_selector',
        'src.envstarter.gui.settings_dialog',
        'src.envstarter.utils.system_integration',
        'src.envstarter.utils.icons',
    ]
    
    success = True
    
    # Add src directory to path for imports
    src_dir = Path(__file__).parent / 'src'
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    
    for module_name in modules_to_test:
        try:
            importlib.import_module(module_name)
            print(f"  ✓ {module_name} (OK)")
        except ImportError as e:
            print(f"  ✗ {module_name} (IMPORT ERROR: {e})")
            success = False
        except Exception as e:
            print(f"  ✗ {module_name} (ERROR: {e})")
            success = False
    
    return success

def check_system_tray():
    """Check if system tray is available."""
    print("\nChecking system tray support...")
    
    try:
        from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
        
        # Need QApplication for tray check
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        if QSystemTrayIcon.isSystemTrayAvailable():
            print("  ✓ System tray available (OK)")
            return True
        else:
            print("  ✗ System tray not available (WARNING)")
            print("    EnvStarter will work but won't have system tray integration")
            return False
    except Exception as e:
        print(f"  ✗ System tray check failed (ERROR: {e})")
        return False

def check_windows_features():
    """Check Windows-specific features (if on Windows)."""
    if os.name != 'nt':
        print("\nSkipping Windows features check (not on Windows)")
        return True
    
    print("\nChecking Windows features...")
    
    # Test registry access
    try:
        import winreg
        test_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, test_key, 0, winreg.KEY_READ):
            print("  ✓ Registry read access (OK)")
    except Exception as e:
        print(f"  ✗ Registry access (ERROR: {e})")
        return False
    
    # Test write access to AppData
    try:
        appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
        test_dir = Path(appdata) / 'EnvStarter_Test'
        test_dir.mkdir(exist_ok=True)
        test_file = test_dir / 'test.txt'
        test_file.write_text('test')
        test_file.unlink()
        test_dir.rmdir()
        print("  ✓ AppData write access (OK)")
    except Exception as e:
        print(f"  ✗ AppData write access (ERROR: {e})")
        return False
    
    return True

def run_quick_test():
    """Run a quick functionality test."""
    print("\nRunning quick functionality test...")
    
    try:
        # Add src to path
        src_dir = Path(__file__).parent / 'src'
        if str(src_dir) not in sys.path:
            sys.path.insert(0, str(src_dir))
        
        # Test basic functionality
        from envstarter.core.models import Environment, Application, Website
        from envstarter.core.storage import ConfigManager
        
        # Create test environment
        test_env = Environment(
            name="Test Environment",
            description="Test environment for validation"
        )
        
        test_app = Application(
            name="Notepad",
            path="notepad.exe"
        )
        
        test_website = Website(
            name="Google",
            url="https://www.google.com"
        )
        
        test_env.applications.append(test_app)
        test_env.websites.append(test_website)
        
        # Test serialization
        env_dict = test_env.to_dict()
        restored_env = Environment.from_dict(env_dict)
        
        if restored_env.name == test_env.name:
            print("  ✓ Model serialization (OK)")
        else:
            print("  ✗ Model serialization (FAILED)")
            return False
        
        # Test config manager (without actually saving)
        config_manager = ConfigManager()
        environments = config_manager.get_environments()
        print(f"  ✓ Configuration system (OK) - Found {len(environments)} sample environments")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Quick test failed (ERROR: {e})")
        return False

def main():
    """Main test function."""
    print("EnvStarter Installation Test")
    print("=" * 40)
    
    results = []
    
    # Run all checks
    results.append(("Python Version", check_python_version()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("Project Structure", check_project_structure()))
    results.append(("EnvStarter Imports", check_envstarter_import()))
    results.append(("System Tray", check_system_tray()))
    results.append(("Windows Features", check_windows_features()))
    results.append(("Quick Functionality Test", run_quick_test()))
    
    # Summary
    print("\n" + "=" * 40)
    print("TEST SUMMARY")
    print("=" * 40)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:.<25} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("-" * 40)
    print(f"TOTAL: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All tests passed! EnvStarter should work correctly.")
        print("\nTo run EnvStarter:")
        print("  python -m src.envstarter.main")
    else:
        print("\n❌ Some tests failed. Please fix the issues above before running EnvStarter.")
        
        if failed == 1 and not check_system_tray():
            print("\nNote: System tray failure is not critical - EnvStarter will still work.")
        
        print("\nTo install missing dependencies:")
        print("  pip install -r requirements.txt")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)