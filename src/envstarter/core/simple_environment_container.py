"""
🔥 SIMPLIFIED ENVIRONMENT CONTAINER 🔥
A working version without virtual desktop dependencies for testing.

This is a fallback container that provides multi-environment support
without relying on Windows virtual desktop creation.
"""

import os
import sys
import time
import psutil
import threading
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Callable
from datetime import datetime
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from src.envstarter.core.models import Environment, Application, Website
from src.envstarter.core.aggressive_title_injector import AggressiveWindowTitleInjector
from src.envstarter.core.robust_app_launcher import get_robust_launcher


class EnvironmentState(Enum):
    """Environment container states."""
    STOPPED = "stopped"
    STARTING = "starting" 
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class ProcessInfo:
    """Information about a process running in an environment."""
    pid: int
    name: str
    exe_path: str
    command_line: str
    memory_mb: float
    cpu_percent: float
    create_time: datetime
    parent_pid: Optional[int] = None
    
    def to_dict(self) -> Dict:
        return {
            "pid": self.pid,
            "name": self.name,
            "exe_path": self.exe_path,
            "command_line": self.command_line,
            "memory_mb": self.memory_mb,
            "cpu_percent": self.cpu_percent,
            "create_time": self.create_time.isoformat(),
            "parent_pid": self.parent_pid
        }


@dataclass
class EnvironmentStats:
    """Runtime statistics for an environment container."""
    total_processes: int = 0
    total_memory_mb: float = 0.0
    total_cpu_percent: float = 0.0
    uptime_seconds: int = 0
    desktop_index: int = -1
    process_list: List[ProcessInfo] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "total_processes": self.total_processes,
            "total_memory_mb": self.total_memory_mb,
            "total_cpu_percent": self.total_cpu_percent,
            "uptime_seconds": self.uptime_seconds,
            "desktop_index": self.desktop_index,
            "process_count": len(self.process_list)
        }


class SimpleEnvironmentContainer(QObject):
    """
    🎯 SIMPLIFIED ENVIRONMENT CONTAINER
    
    A working version that provides multi-environment support without
    virtual desktop creation issues. Perfect for testing and systems
    where virtual desktop creation is problematic.
    """
    
    # Signals for container state changes
    state_changed = pyqtSignal(str, str)  # container_id, new_state
    stats_updated = pyqtSignal(str, dict)  # container_id, stats_dict
    process_started = pyqtSignal(str, int, str)  # container_id, pid, process_name
    process_stopped = pyqtSignal(str, int, str)  # container_id, pid, process_name
    error_occurred = pyqtSignal(str, str)  # container_id, error_message
    
    def __init__(self, environment: Environment, container_id: str):
        super().__init__()
        
        self.environment = environment
        self.container_id = container_id
        self.state = EnvironmentState.STOPPED
        self.start_time: Optional[datetime] = None
        
        # Process tracking
        self.tracked_processes: Set[int] = set()  # PIDs of processes we launched
        self.child_processes: Set[int] = set()    # PIDs of child processes
        
        # Resource monitoring
        self.stats = EnvironmentStats()
        self.monitoring_active = False
        
        # Process isolation
        self.process_whitelist: Set[str] = {
            'explorer.exe', 'dwm.exe', 'winlogon.exe', 
            'csrss.exe', 'lsass.exe', 'services.exe'
        }
        
        # Simulate desktop index for compatibility
        self.desktop_index = hash(f"{environment.name}-{container_id}") % 10 + 1
        self.desktop_name = f"EnvBox-{environment.name}"
        
        # AGGRESSIVE WINDOW TITLE INJECTION
        self.title_injector = AggressiveWindowTitleInjector(environment.name, container_id)
        self.isolation_active = False
        
    async def start_container(self) -> bool:
        """🚀 START THE ENVIRONMENT CONTAINER (simplified version)"""
        if self.state != EnvironmentState.STOPPED:
            self.error_occurred.emit(self.container_id, f"Container already {self.state.value}")
            return False
        
        try:
            self._set_state(EnvironmentState.STARTING)
            self.start_time = datetime.now()
            
            print(f"🚀 Starting simplified container '{self.container_id}'...")
            print(f"   📱 Environment: {self.environment.name}")
            print(f"   🖥️  Desktop: {self.desktop_name} (Simulated #{self.desktop_index})")
            
            # Apply startup delay if specified
            if self.environment.startup_delay > 0:
                print(f"⏱️  Waiting {self.environment.startup_delay} seconds...")
                time.sleep(self.environment.startup_delay)
            
            # Launch all applications
            await self._launch_container_applications()
            
            # Launch all websites  
            await self._launch_container_websites()
            
            # Start resource monitoring
            self._start_monitoring()
            
            # Container is now running
            self._set_state(EnvironmentState.RUNNING)
            
            # START AGGRESSIVE TITLE INJECTION!
            if self.tracked_processes:
                self.title_injector.start_aggressive_monitoring(list(self.tracked_processes))
                self.isolation_active = True
                print(f"🔥 AGGRESSIVE TITLE INJECTION ACTIVE FOR: {self.environment.name.upper()}")
                print(f"   Tracking {len(self.tracked_processes)} processes")
                print(f"   Environment prefix: [{self.environment.name.upper()}]")
            
            print(f"✅ Simplified container '{self.container_id}' started successfully!")
            print(f"   🔄 Processes: {len(self.tracked_processes)} tracked")
            print(f"   🎯 Environment: {self.environment.name.upper()}")
            print(f"   🔒 Isolation: {'ACTIVE' if self.isolation_active else 'DISABLED'}")
            
            return True
            
        except Exception as e:
            self._set_state(EnvironmentState.ERROR)
            self.error_occurred.emit(self.container_id, f"Failed to start: {str(e)}")
            print(f"❌ Container start failed: {e}")
            return False
    
    async def _launch_container_applications(self):
        """Launch all applications within the container."""
        print(f"🚀 Launching {len(self.environment.applications)} applications...")
        
        for i, app in enumerate(self.environment.applications):
            try:
                print(f"  [{i+1}/{len(self.environment.applications)}] Starting: {app.name}")
                
                pid = await self._launch_app_in_container(app)
                if pid:
                    self.tracked_processes.add(pid)
                    self.process_started.emit(self.container_id, pid, app.name)
                    print(f"    ✅ Started with PID: {pid}")
                else:
                    print(f"    ❌ Failed to start: {app.name}")
                
                # Small delay between launches
                time.sleep(0.3)
                
            except Exception as e:
                print(f"    ❌ Error launching {app.name}: {e}")
    
    async def _launch_container_websites(self):
        """Launch all websites within the container.""" 
        print(f"🌐 Opening {len(self.environment.websites)} websites...")
        
        for i, website in enumerate(self.environment.websites):
            try:
                print(f"  [{i+1}/{len(self.environment.websites)}] Opening: {website.name}")
                
                success = await self._launch_website_in_container(website)
                if success:
                    print(f"    ✅ Opened: {website.url}")
                else:
                    print(f"    ❌ Failed to open: {website.name}")
                
                time.sleep(0.2)
                
            except Exception as e:
                print(f"    ❌ Error opening {website.name}: {e}")
    
    async def _launch_app_in_container(self, app: Application) -> Optional[int]:
        """Launch a single application within the container using ROBUST launcher."""
        try:
            # Get the robust launcher
            launcher = get_robust_launcher()
            
            # Prepare environment variables
            env_vars = {
                'ENVSTARTER_ENV': self.environment.name,
                'ENVSTARTER_CONTAINER': self.container_id,
                'ENVSTARTER_ISOLATED': 'true'
            }
            
            # Launch using robust launcher
            print(f"🚀 LAUNCHING {app.name} IN ENVIRONMENT: {self.environment.name.upper()}")
            process = launcher.launch_application(
                app_name=app.name,
                app_path=app.path,
                arguments=app.arguments or "",
                working_dir=app.working_directory or "",
                environment_vars=env_vars
            )
            
            if process and process.pid:
                pid = process.pid
                
                # Track this process
                self.tracked_processes.add(pid)
                
                # Add to AGGRESSIVE title injector
                self.title_injector.add_process(pid)
                
                # Emit signal
                self.process_started.emit(self.container_id, pid, app.name)
                
                print(f"✅ LAUNCHED {app.name} (PID: {pid}) - TITLE INJECTION ACTIVE!")
                return pid
            else:
                print(f"❌ FAILED TO LAUNCH {app.name}")
                return None
            
        except Exception as e:
            print(f"❌ Error launching {app.name}: {e}")
            return None
    
    async def _launch_website_in_container(self, website: Website) -> bool:
        """Launch a website within the container."""
        try:
            import webbrowser
            
            if website.browser and Path(website.browser).exists():
                # Use specific browser
                import subprocess
                if os.name == 'nt':
                    subprocess.Popen([website.browser, website.url],
                                   creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
                else:
                    subprocess.Popen([website.browser, website.url])
            else:
                # Use system default browser
                webbrowser.open(website.url, new=2 if website.new_tab else 1)
            
            return True
            
        except Exception as e:
            print(f"Error opening website {website.name}: {e}")
            return False
    
    def _start_monitoring(self):
        """Start continuous monitoring of container resources."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        
        # Create monitoring timer
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._update_container_stats)
        self.monitor_timer.start(2000)  # Update every 2 seconds
        
        print(f"📊 Container monitoring started for '{self.container_id}'")
    
    def _update_container_stats(self):
        """Update container statistics."""
        if not self.monitoring_active or self.state != EnvironmentState.RUNNING:
            return
        
        try:
            # Reset stats
            self.stats.total_processes = 0
            self.stats.total_memory_mb = 0.0
            self.stats.total_cpu_percent = 0.0
            self.stats.process_list.clear()
            self.stats.desktop_index = self.desktop_index
            
            # Calculate uptime
            if self.start_time:
                self.stats.uptime_seconds = int((datetime.now() - self.start_time).total_seconds())
            
            # Find all our tracked processes and their children
            all_container_pids = set()
            
            # Start with our directly launched processes
            for pid in list(self.tracked_processes):
                if psutil.pid_exists(pid):
                    all_container_pids.add(pid)
                    # Add all children of this process
                    try:
                        parent = psutil.Process(pid)
                        for child in parent.children(recursive=True):
                            all_container_pids.add(child.pid)
                            self.child_processes.add(child.pid)
                    except psutil.NoSuchProcess:
                        self.tracked_processes.discard(pid)
                else:
                    # Process died, remove from tracking
                    self.tracked_processes.discard(pid)
            
            # Collect stats for all container processes
            for pid in all_container_pids:
                try:
                    proc = psutil.Process(pid)
                    proc_info = ProcessInfo(
                        pid=pid,
                        name=proc.name(),
                        exe_path=proc.exe() if proc.exe() else "Unknown",
                        command_line=" ".join(proc.cmdline()) if proc.cmdline() else "",
                        memory_mb=proc.memory_info().rss / 1024 / 1024,
                        cpu_percent=proc.cpu_percent(),
                        create_time=datetime.fromtimestamp(proc.create_time()),
                        parent_pid=proc.ppid() if proc.ppid() != pid else None
                    )
                    
                    self.stats.process_list.append(proc_info)
                    self.stats.total_memory_mb += proc_info.memory_mb
                    self.stats.total_cpu_percent += proc_info.cpu_percent
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            self.stats.total_processes = len(self.stats.process_list)
            
            # Emit updated stats
            self.stats_updated.emit(self.container_id, self.stats.to_dict())
            
        except Exception as e:
            print(f"Error updating container stats: {e}")
    
    async def stop_container(self, force: bool = False) -> bool:
        """🛑 STOP THE ENVIRONMENT CONTAINER"""
        if self.state == EnvironmentState.STOPPED:
            return True
        
        try:
            self._set_state(EnvironmentState.STOPPING)
            print(f"🛑 Stopping container '{self.container_id}'...")
            
            # Stop monitoring first
            self._stop_monitoring()
            
            # Clean up AGGRESSIVE title injection
            if hasattr(self, 'title_injector'):
                self.title_injector.stop_monitoring()
                self.isolation_active = False
                print(f"🔥 Stopped aggressive title injection for: {self.environment.name.upper()}")
            
            # Terminate all processes in container
            await self._terminate_container_processes(force)
            
            # Container stopped
            self._set_state(EnvironmentState.STOPPED)
            self.start_time = None
            
            print(f"✅ Container '{self.container_id}' stopped successfully")
            return True
            
        except Exception as e:
            self._set_state(EnvironmentState.ERROR)
            self.error_occurred.emit(self.container_id, f"Failed to stop: {str(e)}")
            return False
    
    async def _terminate_container_processes(self, force: bool = False):
        """Terminate all processes running in this container."""
        all_pids = self.tracked_processes.union(self.child_processes)
        
        print(f"  🔄 Terminating {len(all_pids)} container processes...")
        
        for pid in all_pids:
            try:
                if psutil.pid_exists(pid):
                    proc = psutil.Process(pid)
                    proc_name = proc.name()
                    
                    # Don't kill system processes
                    if proc_name.lower() in self.process_whitelist:
                        continue
                    
                    if force:
                        proc.kill()
                        print(f"    💀 Killed: {proc_name} (PID: {pid})")
                    else:
                        proc.terminate()
                        print(f"    🔄 Terminated: {proc_name} (PID: {pid})")
                    
                    self.process_stopped.emit(self.container_id, pid, proc_name)
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                continue
        
        # Wait for processes to actually terminate
        if not force:
            time.sleep(2)
            # Force kill any remaining processes
            await self._terminate_container_processes(force=True)
        
        # Clear tracking sets
        self.tracked_processes.clear()
        self.child_processes.clear()
    
    def _stop_monitoring(self):
        """Stop container monitoring."""
        self.monitoring_active = False
        if hasattr(self, 'monitor_timer'):
            self.monitor_timer.stop()
    
    def pause_container(self) -> bool:
        """⏸️ PAUSE THE CONTAINER (suspend all processes)"""
        if self.state != EnvironmentState.RUNNING:
            return False
        
        try:
            # Suspend all container processes
            all_pids = self.tracked_processes.union(self.child_processes)
            for pid in all_pids:
                try:
                    if psutil.pid_exists(pid):
                        proc = psutil.Process(pid)
                        proc.suspend()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            self._set_state(EnvironmentState.PAUSED)
            print(f"⏸️  Container '{self.container_id}' paused")
            return True
            
        except Exception as e:
            self.error_occurred.emit(self.container_id, f"Failed to pause: {str(e)}")
            return False
    
    def resume_container(self) -> bool:
        """▶️ RESUME THE CONTAINER (resume all processes)"""
        if self.state != EnvironmentState.PAUSED:
            return False
        
        try:
            # Resume all container processes
            all_pids = self.tracked_processes.union(self.child_processes)
            for pid in all_pids:
                try:
                    if psutil.pid_exists(pid):
                        proc = psutil.Process(pid)
                        proc.resume()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            self._set_state(EnvironmentState.RUNNING)
            print(f"▶️  Container '{self.container_id}' resumed")
            return True
            
        except Exception as e:
            self.error_occurred.emit(self.container_id, f"Failed to resume: {str(e)}")
            return False
    
    def switch_to_container(self) -> bool:
        """🔄 SWITCH TO THIS CONTAINER (simplified - no actual desktop switch)"""
        if self.state != EnvironmentState.RUNNING:
            return False
        
        try:
            print(f"🔄 Switched to container '{self.container_id}' (simulated)")
            return True
        except Exception as e:
            self.error_occurred.emit(self.container_id, f"Failed to switch: {str(e)}")
            return False
    
    def get_container_info(self) -> Dict:
        """Get comprehensive container information."""
        return {
            "container_id": self.container_id,
            "environment_name": self.environment.name,
            "state": self.state.value,
            "desktop_name": self.desktop_name,
            "desktop_index": self.desktop_index,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "tracked_processes": len(self.tracked_processes),
            "child_processes": len(self.child_processes),
            "stats": self.stats.to_dict(),
            "is_running": self.state == EnvironmentState.RUNNING
        }
    
    def _set_state(self, new_state: EnvironmentState):
        """Update container state and emit signal."""
        old_state = self.state
        self.state = new_state
        self.state_changed.emit(self.container_id, new_state.value)
        print(f"🔄 Container '{self.container_id}': {old_state.value} → {new_state.value}")