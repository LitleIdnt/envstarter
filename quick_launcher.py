#!/usr/bin/env python3
"""
🚀 QUICK ENVSTARTER LAUNCHER 🚀
Simplified launcher for systems without PyQt6 installed
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    print("=" * 60)
    print("🚀 ENVSTARTER QUICK LAUNCHER")
    print("=" * 60)
    print()
    
    # Check system
    print("🔍 System Check:")
    print(f"   Python: {sys.version}")
    print(f"   Platform: {sys.platform}")
    print(f"   Working Directory: {os.getcwd()}")
    print()
    
    # Check for dependencies
    print("📦 Dependency Check:")
    
    try:
        import PyQt6
        print("   ✅ PyQt6 available")
        pyqt_available = True
    except ImportError:
        print("   ❌ PyQt6 not available")
        pyqt_available = False
    
    try:
        import psutil
        print("   ✅ psutil available")
        psutil_available = True
    except ImportError:
        print("   ❌ psutil not available")
        psutil_available = False
    
    print()
    
    if pyqt_available and psutil_available:
        print("🎮 All dependencies available! Launching Enhanced EnvStarter...")
        try:
            from src.envstarter.enhanced_main import main as enhanced_main
            enhanced_main()
        except Exception as e:
            print(f"❌ Failed to launch enhanced version: {e}")
            print()
            show_dependency_instructions()
    else:
        print("⚠️  Missing dependencies for enhanced version")
        print()
        show_dependency_instructions()

def show_dependency_instructions():
    print("📋 INSTALLATION INSTRUCTIONS:")
    print()
    print("🔧 To install required dependencies:")
    print()
    print("   Option 1 - Using pip:")
    print("   pip install PyQt6 psutil")
    print()
    print("   Option 2 - Using system package manager (Ubuntu/Debian):")
    print("   sudo apt update")
    print("   sudo apt install python3-pyqt6 python3-psutil")
    print()
    print("   Option 3 - Using conda:")
    print("   conda install pyqt psutil")
    print()
    print("🎯 WHAT THE ENHANCED SYSTEM PROVIDES:")
    print("   • 📦 Multi-environment containers (VM-like isolation)")
    print("   • 🚀 Concurrent environment launching")
    print("   • 🎮 Advanced management dashboard")
    print("   • 🔄 Real-time container switching")
    print("   • 📊 System resource monitoring")
    print("   • ⚙️  Complete settings & environment creation UI")
    print()
    print("🎉 Once dependencies are installed, run:")
    print("   python3 src/envstarter/enhanced_main.py")
    print()
    
    # Show current system info for troubleshooting
    print("🔧 SYSTEM INFO FOR TROUBLESHOOTING:")
    print(f"   Python version: {sys.version}")
    print(f"   Python executable: {sys.executable}")
    print(f"   Platform: {sys.platform}")
    
    # Try to detect WSL
    try:
        with open('/proc/version', 'r') as f:
            if 'microsoft' in f.read().lower():
                print("   Environment: Windows Subsystem for Linux (WSL)")
                print("   💡 TIP: You may need to install X11 server for GUI apps in WSL")
    except:
        pass

if __name__ == "__main__":
    main()