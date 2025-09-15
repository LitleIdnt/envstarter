#!/usr/bin/env python3
"""
🔧 DEBUG WINDOW TITLES 🔧
Let's see what's actually happening with window titles!
"""

import sys
import os
import time
import ctypes
from ctypes import wintypes
import psutil

def debug_current_windows():
    """Debug what windows are currently open."""
    print("🔍 DEBUGGING CURRENT WINDOWS")
    print("=" * 50)
    
    if os.name != 'nt':
        print("❌ This debug script is Windows-only")
        return
        
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    
    windows_found = []
    
    def enum_callback(hwnd, param):
        if user32.IsWindowVisible(hwnd):
            # Get PID
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            # Get window title
            title_length = user32.GetWindowTextLengthW(hwnd)
            if title_length > 0:
                title_buffer = ctypes.create_unicode_buffer(title_length + 1)
                user32.GetWindowTextW(hwnd, title_buffer, title_length + 1)
                title = title_buffer.value
                
                if title and len(title.strip()) > 0:
                    try:
                        proc = psutil.Process(pid.value)
                        process_name = proc.name()
                    except:
                        process_name = "Unknown"
                        
                    windows_found.append({
                        'hwnd': hwnd,
                        'pid': pid.value,
                        'process': process_name,
                        'title': title
                    })
        return True
    
    # Enumerate windows
    WNDENUMPROC = ctypes.WINFUNCTYPE(
        ctypes.c_bool,
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int)
    )
    user32.EnumWindows(WNDENUMPROC(enum_callback), 0)
    
    # Show results
    print(f"📊 Found {len(windows_found)} visible windows:")
    for i, window in enumerate(windows_found):
        print(f"   {i+1}. PID {window['pid']} ({window['process']})")
        print(f"       HWND: {window['hwnd']}")
        print(f"       Title: '{window['title']}'")
        print()


def test_direct_title_change():
    """Test directly changing a window title."""
    print("🔧 TESTING DIRECT TITLE CHANGE")
    print("=" * 50)
    
    if os.name != 'nt':
        print("❌ This test is Windows-only")
        return
        
    user32 = ctypes.windll.user32
    
    # Find Calculator window
    calc_hwnd = user32.FindWindowW(None, "Calculator")
    if not calc_hwnd:
        calc_hwnd = user32.FindWindowW("ApplicationFrameWindow", None)
        
    if calc_hwnd:
        print(f"✅ Found Calculator window: HWND {calc_hwnd}")
        
        # Get current title
        title_length = user32.GetWindowTextLengthW(calc_hwnd)
        if title_length > 0:
            title_buffer = ctypes.create_unicode_buffer(title_length + 1)
            user32.GetWindowTextW(calc_hwnd, title_buffer, title_length + 1)
            current_title = title_buffer.value
            print(f"   Current title: '{current_title}'")
            
            # Try to change it
            new_title = "[TEST_ENV] Calculator"
            print(f"   Trying to set: '{new_title}'")
            
            # Method 1: SetWindowTextW
            result1 = user32.SetWindowTextW(calc_hwnd, new_title)
            print(f"   SetWindowTextW result: {result1}")
            
            time.sleep(1)
            
            # Check if it worked
            title_buffer2 = ctypes.create_unicode_buffer(256)
            user32.GetWindowTextW(calc_hwnd, title_buffer2, 256)
            actual_title = title_buffer2.value
            print(f"   Actual title after change: '{actual_title}'")
            
            if new_title in actual_title:
                print("   ✅ SUCCESS! Title was changed!")
            else:
                print("   ❌ FAILED! Title was not changed!")
                
        else:
            print("   ⚠️ Window has no title")
    else:
        print("❌ Calculator window not found!")
        print("💡 Please open Calculator first and run this again")


def launch_and_monitor_calc():
    """Launch Calculator and monitor its title changes."""
    print("🚀 LAUNCHING AND MONITORING CALCULATOR")
    print("=" * 50)
    
    import subprocess
    
    try:
        # Launch Calculator
        print("📱 Launching Calculator...")
        proc = subprocess.Popen("calc.exe", shell=True)
        calc_pid = proc.pid
        
        print(f"   Calculator PID: {calc_pid}")
        
        # Wait for window to appear
        print("⏳ Waiting for Calculator window...")
        time.sleep(2)
        
        user32 = ctypes.windll.user32
        
        # Find the calculator window by PID
        calc_hwnd = None
        
        def find_calc_callback(hwnd, param):
            nonlocal calc_hwnd
            if user32.IsWindowVisible(hwnd):
                pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                
                if pid.value == calc_pid:
                    title_length = user32.GetWindowTextLengthW(hwnd)
                    if title_length > 0:
                        calc_hwnd = hwnd
                        return False  # Stop enumeration
            return True
        
        WNDENUMPROC = ctypes.WINFUNCTYPE(
            ctypes.c_bool,
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int)
        )
        user32.EnumWindows(WNDENUMPROC(find_calc_callback), 0)
        
        if calc_hwnd:
            print(f"✅ Found Calculator window: HWND {calc_hwnd}")
            
            # Monitor and inject title every second for 10 seconds
            env_name = "DEBUG_TEST_ENV"
            for i in range(10):
                try:
                    # Get current title
                    title_buffer = ctypes.create_unicode_buffer(256)
                    user32.GetWindowTextW(calc_hwnd, title_buffer, 256)
                    current_title = title_buffer.value
                    
                    print(f"   Second {i+1}: Current title = '{current_title}'")
                    
                    # Inject our environment name if not already there
                    if not current_title.startswith(f"[{env_name}]"):
                        new_title = f"[{env_name}] {current_title}"
                        
                        # Try multiple methods
                        result1 = user32.SetWindowTextW(calc_hwnd, new_title)
                        
                        WM_SETTEXT = 0x000C
                        result2 = user32.SendMessageW(calc_hwnd, WM_SETTEXT, 0, new_title)
                        
                        print(f"      Injecting: '{new_title}'")
                        print(f"      SetWindowText: {result1}, SendMessage: {result2}")
                        
                        # Verify
                        time.sleep(0.5)
                        title_buffer2 = ctypes.create_unicode_buffer(256)
                        user32.GetWindowTextW(calc_hwnd, title_buffer2, 256)
                        actual_title = title_buffer2.value
                        
                        if f"[{env_name}]" in actual_title:
                            print(f"      ✅ SUCCESS: '{actual_title}'")
                        else:
                            print(f"      ❌ FAILED: '{actual_title}'")
                    else:
                        print(f"      ✅ Already has environment name")
                        
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"      ❌ Error: {e}")
                    
        else:
            print("❌ Could not find Calculator window")
            
    except Exception as e:
        print(f"❌ Failed to launch Calculator: {e}")


def main():
    """Main debugging function."""
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                                                                  ║")
    print("║               🔧 WINDOW TITLE DEBUG UTILITY 🔧                   ║")
    print("║                                                                  ║")
    print("║          Let's figure out why titles aren't changing!           ║")
    print("║                                                                  ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    
    print("\n1. First, let's see what windows are currently open:")
    debug_current_windows()
    
    print("\n2. Now let's test direct title changing on Calculator:")
    print("💡 Please open Calculator manually, then press Enter...")
    input()
    test_direct_title_change()
    
    print("\n3. Finally, let's launch Calculator and monitor title injection:")
    launch_and_monitor_calc()
    
    print("\n" + "=" * 60)
    print("🎯 DEBUG COMPLETE!")
    print("💡 If you saw 'SUCCESS' messages, title injection is working")
    print("💡 If you saw 'FAILED' messages, there's a permission issue")


if __name__ == "__main__":
    main()