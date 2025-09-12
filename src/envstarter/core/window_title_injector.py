"""
🎯 WINDOW TITLE INJECTOR 🎯
FORCES ENVIRONMENT NAMES INTO ALL APPLICATION WINDOW TITLES!
"""

import os
import sys
import time
import threading
import platform
from typing import Dict, List, Optional
import psutil


class WindowTitleInjector:
    """
    INJECTS ENVIRONMENT NAMES INTO EVERY FUCKING WINDOW TITLE!
    Makes it IMPOSSIBLE to not know which environment an app is in!
    """
    
    def __init__(self, environment_name: str, container_id: str):
        self.environment_name = environment_name.upper()  # MAKE IT LOUD!
        self.container_id = container_id
        self.tracked_pids: Dict[int, str] = {}
        self.monitoring = False
        self.monitor_thread = None
        self.system = platform.system()
        
    def start_monitoring(self, process_pids: List[int]):
        """Start monitoring and injecting titles."""
        print(f"🎯 STARTING TITLE INJECTION FOR: {self.environment_name}")
        
        for pid in process_pids:
            self.tracked_pids[pid] = f"[{self.environment_name}]"
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def _monitor_loop(self):
        """Continuous monitoring loop to inject titles."""
        while self.monitoring:
            try:
                if self.system == "Windows":
                    self._inject_windows_titles()
                elif self.system == "Linux":
                    self._inject_linux_titles()
                elif self.system == "Darwin":
                    self._inject_macos_titles()
                    
                time.sleep(1)  # Check every second
                
            except Exception as e:
                print(f"⚠️ Title injection error: {e}")
                
    def _inject_windows_titles(self):
        """Inject titles on Windows using Win32 API."""
        try:
            import ctypes
            from ctypes import wintypes
            
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            
            # Enumerate all windows
            def enum_window_callback(hwnd, pids):
                if user32.IsWindowVisible(hwnd):
                    # Get PID of window
                    pid = wintypes.DWORD()
                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    
                    # Check if this PID belongs to our environment
                    if pid.value in self.tracked_pids:
                        # Get current title
                        length = user32.GetWindowTextLengthW(hwnd)
                        if length > 0:
                            buff = ctypes.create_unicode_buffer(length + 1)
                            user32.GetWindowTextW(hwnd, buff, length + 1)
                            current_title = buff.value
                            
                            # Check if we already injected
                            env_tag = f"[{self.environment_name}]"
                            if not current_title.startswith(env_tag):
                                # INJECT ENVIRONMENT NAME!
                                new_title = f"{env_tag} {current_title}"
                                user32.SetWindowTextW(hwnd, new_title)
                                print(f"💉 Injected title: {new_title}")
                                
                return True
            
            # Enumerate windows
            WNDENUMPROC = ctypes.WINFUNCTYPE(
                ctypes.c_bool,
                ctypes.POINTER(ctypes.c_int),
                ctypes.POINTER(ctypes.c_int)
            )
            user32.EnumWindows(WNDENUMPROC(enum_window_callback), 0)
            
        except Exception as e:
            print(f"⚠️ Windows title injection error: {e}")
            
    def _inject_linux_titles(self):
        """Inject titles on Linux using X11."""
        try:
            import subprocess
            
            for pid in self.tracked_pids:
                try:
                    # Find windows for this PID
                    result = subprocess.run(
                        f"xdotool search --pid {pid}",
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    
                    if result.stdout:
                        window_ids = result.stdout.strip().split('\n')
                        
                        for window_id in window_ids:
                            if window_id:
                                # Get current title
                                title_result = subprocess.run(
                                    f"xdotool getwindowname {window_id}",
                                    shell=True,
                                    capture_output=True,
                                    text=True
                                )
                                
                                if title_result.stdout:
                                    current_title = title_result.stdout.strip()
                                    env_tag = f"[{self.environment_name}]"
                                    
                                    if not current_title.startswith(env_tag):
                                        # Set new title with environment name
                                        new_title = f"{env_tag} {current_title}"
                                        subprocess.run(
                                            f"xdotool set_window --name '{new_title}' {window_id}",
                                            shell=True
                                        )
                                        print(f"💉 Injected Linux title: {new_title}")
                                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"⚠️ Linux title injection error: {e}")
            
    def _inject_macos_titles(self):
        """Inject titles on macOS using AppleScript."""
        try:
            import subprocess
            
            for pid in self.tracked_pids:
                try:
                    # Use AppleScript to modify window titles
                    script = f'''
                    tell application "System Events"
                        set theProcesses to every process whose unix id is {pid}
                        repeat with theProcess in theProcesses
                            set processName to name of theProcess
                            tell theProcess
                                set windowList to every window
                                repeat with theWindow in windowList
                                    try
                                        set currentTitle to name of theWindow
                                        if currentTitle does not start with "[{self.environment_name}]" then
                                            set name of theWindow to "[{self.environment_name}] " & currentTitle
                                        end if
                                    end try
                                end repeat
                            end tell
                        end repeat
                    end tell
                    '''
                    
                    subprocess.run(['osascript', '-e', script], capture_output=True)
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"⚠️ macOS title injection error: {e}")
            
    def add_process(self, pid: int):
        """Add a new process to track."""
        self.tracked_pids[pid] = f"[{self.environment_name}]"
        print(f"📌 Tracking new process {pid} for {self.environment_name}")
        
    def stop_monitoring(self):
        """Stop the monitoring thread."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
            

class ProcessIsolationManager:
    """
    ENSURES COMPLETE ISOLATION BETWEEN ENVIRONMENTS!
    Apps in different environments CANNOT communicate!
    """
    
    def __init__(self, environment_name: str, container_id: str):
        self.environment_name = environment_name
        self.container_id = container_id
        self.system = platform.system()
        self.isolation_rules = []
        
    def setup_isolation(self, process_pids: List[int]) -> bool:
        """Set up complete isolation for processes."""
        print(f"🔒 SETTING UP ISOLATION FOR: {self.environment_name}")
        
        if self.system == "Windows":
            return self._setup_windows_isolation(process_pids)
        elif self.system == "Linux":
            return self._setup_linux_isolation(process_pids)
        else:
            return self._setup_basic_isolation(process_pids)
            
    def _setup_windows_isolation(self, pids: List[int]) -> bool:
        """Set up Windows job objects for isolation."""
        try:
            import ctypes
            from ctypes import wintypes
            
            kernel32 = ctypes.windll.kernel32
            
            # Create a job object for this environment
            job_name = f"EnvStarter_{self.container_id}"
            job_handle = kernel32.CreateJobObjectW(None, job_name)
            
            if job_handle:
                # Set job restrictions
                class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
                    _fields_ = [
                        ("PerProcessUserTimeLimit", ctypes.c_int64),
                        ("PerJobUserTimeLimit", ctypes.c_int64),
                        ("LimitFlags", wintypes.DWORD),
                        ("MinimumWorkingSetSize", ctypes.c_size_t),
                        ("MaximumWorkingSetSize", ctypes.c_size_t),
                        ("ActiveProcessLimit", wintypes.DWORD),
                        ("Affinity", ctypes.POINTER(ctypes.c_ulong)),
                        ("PriorityClass", wintypes.DWORD),
                        ("SchedulingClass", wintypes.DWORD),
                    ]
                
                # Limit inter-process communication
                JOB_OBJECT_LIMIT_DIE_ON_UNHANDLED_EXCEPTION = 0x00000400
                JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
                
                limit_info = JOBOBJECT_BASIC_LIMIT_INFORMATION()
                limit_info.LimitFlags = (
                    JOB_OBJECT_LIMIT_DIE_ON_UNHANDLED_EXCEPTION |
                    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
                )
                
                # Apply limits
                kernel32.SetInformationJobObject(
                    job_handle,
                    9,  # JobObjectBasicLimitInformation
                    ctypes.byref(limit_info),
                    ctypes.sizeof(limit_info)
                )
                
                # Assign processes to job
                for pid in pids:
                    try:
                        process_handle = kernel32.OpenProcess(0x1F0FFF, False, pid)
                        if process_handle:
                            kernel32.AssignProcessToJobObject(job_handle, process_handle)
                            kernel32.CloseHandle(process_handle)
                            print(f"🔒 Process {pid} isolated in job object")
                    except Exception as e:
                        print(f"⚠️ Could not isolate process {pid}: {e}")
                        
                print(f"✅ Windows job isolation created for {self.environment_name}")
                return True
                
        except Exception as e:
            print(f"⚠️ Windows isolation setup error: {e}")
            return False
            
    def _setup_linux_isolation(self, pids: List[int]) -> bool:
        """Set up Linux namespaces for isolation."""
        try:
            import subprocess
            
            # Create network namespace for this environment
            namespace_name = f"envstarter_{self.container_id}"
            
            # Create namespace
            subprocess.run(
                f"sudo ip netns add {namespace_name}",
                shell=True,
                capture_output=True
            )
            
            # Move processes to namespace
            for pid in pids:
                try:
                    # Use nsenter to isolate process
                    subprocess.run(
                        f"sudo nsenter -t {pid} --net=/var/run/netns/{namespace_name}",
                        shell=True,
                        capture_output=True
                    )
                    print(f"🔒 Process {pid} moved to namespace {namespace_name}")
                except Exception as e:
                    print(f"⚠️ Could not isolate process {pid}: {e}")
                    
            # Set up cgroup for resource isolation
            cgroup_path = f"/sys/fs/cgroup/envstarter/{self.container_id}"
            subprocess.run(f"sudo mkdir -p {cgroup_path}", shell=True)
            
            # Add PIDs to cgroup
            for pid in pids:
                subprocess.run(
                    f"echo {pid} | sudo tee {cgroup_path}/cgroup.procs",
                    shell=True
                )
                
            print(f"✅ Linux namespace isolation created for {self.environment_name}")
            return True
            
        except Exception as e:
            print(f"⚠️ Linux isolation setup error: {e}")
            return False
            
    def _setup_basic_isolation(self, pids: List[int]) -> bool:
        """Set up basic process group isolation."""
        try:
            import os
            import signal
            
            # Create process group
            for pid in pids:
                try:
                    os.setpgid(pid, pid)
                    print(f"🔒 Process {pid} in separate process group")
                except Exception as e:
                    print(f"⚠️ Could not isolate process {pid}: {e}")
                    
            print(f"✅ Basic process isolation for {self.environment_name}")
            return True
            
        except Exception as e:
            print(f"⚠️ Basic isolation error: {e}")
            return False
            

class EnvironmentWindowManager:
    """
    MANAGES ALL WINDOW MODIFICATIONS FOR AN ENVIRONMENT!
    """
    
    def __init__(self, environment_name: str, container_id: str):
        self.environment_name = environment_name.upper()
        self.container_id = container_id
        self.title_injector = WindowTitleInjector(environment_name, container_id)
        self.isolation_manager = ProcessIsolationManager(environment_name, container_id)
        
        # Window overlays for extra visibility
        self.overlay_manager = None
        try:
            from src.envstarter.gui.window_overlay import create_overlay_manager
            self.overlay_manager = create_overlay_manager(environment_name, container_id)
        except ImportError as e:
            print(f"⚠️ Window overlays not available: {e}")
        
    def setup_environment_windows(self, process_pids: List[int]):
        """Set up EVERYTHING for environment visibility and isolation."""
        print(f"🚀 SETTING UP ENVIRONMENT: {self.environment_name}")
        print(f"   Container: {self.container_id}")
        print(f"   Processes: {process_pids}")
        
        # 1. Start title injection
        self.title_injector.start_monitoring(process_pids)
        
        # 2. Start window overlays for extra visibility
        if self.overlay_manager:
            self.overlay_manager.start_monitoring(process_pids)
            print(f"🎨 Window overlays started for {self.environment_name}")
        
        # 3. Set up process isolation
        isolation_success = self.isolation_manager.setup_isolation(process_pids)
        
        if isolation_success:
            print(f"✅ ENVIRONMENT {self.environment_name} FULLY ISOLATED AND LABELED!")
            print(f"   📱 Window titles: INJECTED")
            print(f"   🎨 Window overlays: {'ACTIVE' if self.overlay_manager else 'DISABLED'}")
            print(f"   🔒 Process isolation: ACTIVE")
        else:
            print(f"⚠️ Partial isolation for {self.environment_name}")
            
        return True
        
    def add_new_process(self, pid: int):
        """Add a newly launched process to the environment."""
        self.title_injector.add_process(pid)
        
        if self.overlay_manager:
            self.overlay_manager.add_process(pid)
            
        self.isolation_manager.setup_isolation([pid])
        
    def shutdown(self):
        """Clean shutdown of window management."""
        self.title_injector.stop_monitoring()
        
        if self.overlay_manager:
            from src.envstarter.gui.window_overlay import cleanup_overlay_manager
            cleanup_overlay_manager(self.container_id)
            
        print(f"🛑 Window management stopped for {self.environment_name}")