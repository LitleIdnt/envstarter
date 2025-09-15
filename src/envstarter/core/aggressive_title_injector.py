"""
🔥 AGGRESSIVE WINDOW TITLE INJECTOR 🔥
FORCES ENVIRONMENT NAMES INTO EVERY FUCKING WINDOW TITLE!
NO EXCEPTIONS! NO FAILURES! NO MERCY!
"""

import os
import sys
import time
import threading
import platform
import ctypes
from typing import Dict, List, Set
import psutil


class AggressiveWindowTitleInjector:
    """
    AGGRESSIVE TITLE INJECTION SYSTEM!
    FORCES ENVIRONMENT NAMES INTO EVERY WINDOW TITLE!
    CHECKS EVERY 500MS AND RE-INJECTS IF NEEDED!
    """
    
    def __init__(self, environment_name: str, container_id: str):
        self.environment_name = environment_name.upper()
        self.container_id = container_id
        self.env_prefix = f"[{self.environment_name}]"
        
        # Tracking
        self.tracked_pids: Set[int] = set()
        self.window_handles: Dict[int, List[int]] = {}  # pid -> [hwnds]
        self.injected_titles: Dict[int, str] = {}  # hwnd -> original_title
        
        # Control
        self.monitoring = False
        self.monitor_thread = None
        self.injection_count = 0
        
        self.system = platform.system()
        
        # Windows API setup
        if self.system == "Windows":
            self.user32 = ctypes.windll.user32
            self.kernel32 = ctypes.windll.kernel32
            
    def start_aggressive_monitoring(self, process_pids: List[int]):
        """Start AGGRESSIVE monitoring and title injection."""
        print(f"🔥 STARTING AGGRESSIVE TITLE INJECTION FOR: {self.environment_name}")
        print(f"   Target PIDs: {process_pids}")
        
        self.tracked_pids.update(process_pids)
        self.monitoring = True
        
        # Start monitoring thread with HIGH FREQUENCY
        self.monitor_thread = threading.Thread(target=self._aggressive_monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print(f"🚀 AGGRESSIVE TITLE INJECTOR ACTIVE!")
        
    def _aggressive_monitor_loop(self):
        """AGGRESSIVE monitoring loop - checks every 500ms!"""
        while self.monitoring:
            try:
                if self.system == "Windows":
                    self._inject_windows_titles_aggressive()
                elif self.system == "Linux":
                    self._inject_linux_titles_aggressive()
                    
                # SHORT delay for aggressive updating
                time.sleep(0.5)  # Check every 500ms!
                
            except Exception as e:
                print(f"⚠️ Aggressive injection error: {e}")
                
    def _inject_windows_titles_aggressive(self):
        """AGGRESSIVE Windows title injection - FORCE CHANGES!"""
        try:
            # Get ALL windows for tracked processes
            current_windows = self._get_all_windows_for_tracked_pids()
            
            for hwnd, window_info in current_windows.items():
                pid = window_info['pid']
                current_title = window_info['title']
                
                # Skip if already has our prefix
                if current_title.startswith(self.env_prefix):
                    continue
                    
                # FORCE inject the environment name!
                new_title = f"{self.env_prefix} {current_title}"
                
                # Use multiple methods to ensure it works
                success1 = self._set_window_text_method1(hwnd, new_title)
                success2 = self._set_window_text_method2(hwnd, new_title)
                success3 = self._set_window_text_method3(hwnd, new_title)
                
                if success1 or success2 or success3:
                    self.injection_count += 1
                    self.injected_titles[hwnd] = current_title
                    print(f"🔥 INJECTED TITLE #{self.injection_count}: {new_title}")
                else:
                    print(f"❌ FAILED TO INJECT: {current_title} (HWND: {hwnd})")
                    
        except Exception as e:
            print(f"❌ Windows aggressive injection error: {e}")
            
    def _get_all_windows_for_tracked_pids(self) -> Dict[int, Dict]:
        """Get ALL windows for tracked processes."""
        windows = {}
        
        def enum_callback(hwnd, param):
            try:
                if self.user32.IsWindowVisible(hwnd):
                    # Get PID
                    pid = ctypes.wintypes.DWORD()
                    self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    
                    if pid.value in self.tracked_pids:
                        # Get window title
                        title_length = self.user32.GetWindowTextLengthW(hwnd)
                        if title_length > 0:
                            title_buffer = ctypes.create_unicode_buffer(title_length + 1)
                            self.user32.GetWindowTextW(hwnd, title_buffer, title_length + 1)
                            title = title_buffer.value
                            
                            if title and len(title.strip()) > 0:
                                windows[hwnd] = {
                                    'pid': pid.value,
                                    'title': title,
                                    'hwnd': hwnd
                                }
            except:
                pass
            return True
            
        # Enumerate ALL windows
        WNDENUMPROC = ctypes.WINFUNCTYPE(
            ctypes.c_bool,
            ctypes.POINTER(ctypes.c_int), 
            ctypes.POINTER(ctypes.c_int)
        )
        self.user32.EnumWindows(WNDENUMPROC(enum_callback), 0)
        
        return windows
        
    def _set_window_text_method1(self, hwnd: int, title: str) -> bool:
        """Method 1: Direct SetWindowTextW."""
        try:
            result = self.user32.SetWindowTextW(hwnd, title)
            return result != 0
        except:
            return False
            
    def _set_window_text_method2(self, hwnd: int, title: str) -> bool:
        """Method 2: SendMessage with WM_SETTEXT."""
        try:
            WM_SETTEXT = 0x000C
            result = self.user32.SendMessageW(hwnd, WM_SETTEXT, 0, title)
            return result == 1
        except:
            return False
            
    def _set_window_text_method3(self, hwnd: int, title: str) -> bool:
        """Method 3: PostMessage with WM_SETTEXT."""
        try:
            WM_SETTEXT = 0x000C
            result = self.user32.PostMessageW(hwnd, WM_SETTEXT, 0, title)
            return result != 0
        except:
            return False
            
    def _inject_linux_titles_aggressive(self):
        """AGGRESSIVE Linux title injection using xdotool."""
        try:
            import subprocess
            
            for pid in self.tracked_pids:
                try:
                    # Find ALL windows for this PID
                    result = subprocess.run(
                        f"xdotool search --pid {pid}",
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    
                    if result.stdout:
                        window_ids = result.stdout.strip().split('\n')
                        
                        for window_id in window_ids:
                            if window_id and window_id.isdigit():
                                # Get current title
                                title_result = subprocess.run(
                                    f"xdotool getwindowname {window_id}",
                                    shell=True,
                                    capture_output=True,
                                    text=True,
                                    timeout=1
                                )
                                
                                if title_result.stdout:
                                    current_title = title_result.stdout.strip()
                                    
                                    # Skip if already has our prefix
                                    if current_title.startswith(self.env_prefix):
                                        continue
                                        
                                    # INJECT environment name
                                    new_title = f"{self.env_prefix} {current_title}"
                                    
                                    # Method 1: xdotool set_window
                                    subprocess.run(
                                        f"xdotool set_window --name '{new_title}' {window_id}",
                                        shell=True,
                                        timeout=1
                                    )
                                    
                                    # Method 2: wmctrl (if available)
                                    subprocess.run(
                                        f"wmctrl -i -r {window_id} -T '{new_title}'",
                                        shell=True,
                                        timeout=1,
                                        capture_output=True
                                    )
                                    
                                    self.injection_count += 1
                                    print(f"🔥 LINUX INJECTED #{self.injection_count}: {new_title}")
                                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"❌ Linux aggressive injection error: {e}")
            
    def add_process(self, pid: int):
        """Add a new process to aggressive tracking."""
        if pid not in self.tracked_pids:
            self.tracked_pids.add(pid)
            print(f"🔥 ADDED PID {pid} TO AGGRESSIVE TITLE INJECTION")
            
            # Immediately try to inject titles for this PID
            if self.system == "Windows":
                self._force_immediate_injection_for_pid(pid)
                
    def _force_immediate_injection_for_pid(self, pid: int):
        """IMMEDIATELY inject titles for a specific PID."""
        try:
            # Wait a moment for windows to appear
            time.sleep(1)
            
            # Force injection for this specific PID
            windows = self._get_all_windows_for_tracked_pids()
            pid_windows = {hwnd: info for hwnd, info in windows.items() if info['pid'] == pid}
            
            for hwnd, window_info in pid_windows.items():
                current_title = window_info['title']
                if not current_title.startswith(self.env_prefix):
                    new_title = f"{self.env_prefix} {current_title}"
                    
                    # Try all methods immediately
                    success = (
                        self._set_window_text_method1(hwnd, new_title) or
                        self._set_window_text_method2(hwnd, new_title) or  
                        self._set_window_text_method3(hwnd, new_title)
                    )
                    
                    if success:
                        print(f"🔥 IMMEDIATE INJECTION SUCCESS: {new_title}")
                    else:
                        print(f"❌ IMMEDIATE INJECTION FAILED: {current_title}")
                        
        except Exception as e:
            print(f"❌ Immediate injection error: {e}")
            
    def get_injection_stats(self) -> Dict:
        """Get statistics about title injection."""
        return {
            'environment_name': self.environment_name,
            'tracked_pids': len(self.tracked_pids),
            'total_injections': self.injection_count,
            'active_windows': len(self.injected_titles),
            'monitoring_active': self.monitoring
        }
        
    def stop_monitoring(self):
        """Stop aggressive monitoring."""
        print(f"🛑 STOPPING AGGRESSIVE TITLE INJECTION FOR: {self.environment_name}")
        print(f"   Total injections performed: {self.injection_count}")
        
        self.monitoring = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
            
        # Optionally restore original titles
        self._restore_original_titles()
        
    def _restore_original_titles(self):
        """Restore original window titles."""
        try:
            restored = 0
            for hwnd, original_title in self.injected_titles.items():
                if self.system == "Windows":
                    if self._set_window_text_method1(hwnd, original_title):
                        restored += 1
                        
            if restored > 0:
                print(f"🔄 Restored {restored} original window titles")
                
        except Exception as e:
            print(f"⚠️ Error restoring titles: {e}")


def test_aggressive_injection():
    """Test the aggressive injection system."""
    print("🧪 TESTING AGGRESSIVE TITLE INJECTION")
    print("=" * 60)
    
    # Create injector
    injector = AggressiveWindowTitleInjector("TEST_AGGRESSIVE", "test_container")
    
    try:
        # Get current running processes (for demo)
        current_processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() in ['notepad.exe', 'calc.exe', 'calculator.exe']:
                    current_processes.append(proc.info['pid'])
            except:
                continue
                
        if current_processes:
            print(f"📊 Found test processes: {current_processes}")
            
            # Start aggressive injection
            injector.start_aggressive_monitoring(current_processes)
            
            # Let it run for 10 seconds
            for i in range(10):
                time.sleep(1)
                stats = injector.get_injection_stats()
                print(f"   Second {i+1}: {stats['total_injections']} injections")
                
            # Stop
            injector.stop_monitoring()
            
            final_stats = injector.get_injection_stats()
            print(f"✅ Test complete! Total injections: {final_stats['total_injections']}")
            
        else:
            print("⚠️ No test applications running (notepad, calc)")
            print("   Open notepad or calculator and run this test again")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        injector.stop_monitoring()


if __name__ == "__main__":
    test_aggressive_injection()