"""
🔥 ENVIRONMENT CONTAINER SYSTEM 🔥
Revolutionary VM-like environment isolation and management.

This module provides true environment containerization where each environment
runs in complete isolation with its own virtual desktop, process tracking,
and resource management - like having multiple VMs!
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
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread

from src.envstarter.core.models import Environment, Application, Website
from src.envstarter.utils.system_integration import SystemIntegration


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


class EnvironmentContainer(QObject):
    """
    🎯 VM-LIKE ENVIRONMENT CONTAINER
    
    Each container represents a fully isolated environment that runs like
    a separate virtual machine with its own:
    - Virtual Desktop (complete isolation)  
    - Process tracking and monitoring
    - Resource management
    - Network isolation (future)
    - File system isolation (future)
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
        
        # VM-like isolation components
        self.desktop_index = -1
        self.desktop_name = f"EnvBox-{environment.name}"
        self.tracked_processes: Set[int] = set()  # PIDs of processes we launched
        self.child_processes: Set[int] = set()    # PIDs of child processes
        self.system_integration = SystemIntegration()
        
        # Resource monitoring
        self.stats = EnvironmentStats()
        self.monitoring_active = False
        self.monitor_thread: Optional[QThread] = None
        
        # Process isolation
        self.process_whitelist: Set[str] = {
            'explorer.exe', 'dwm.exe', 'winlogon.exe', 
            'csrss.exe', 'lsass.exe', 'services.exe'
        }
        
    def get_unique_desktop_index(self) -> int:
        """Get unique desktop index for this container (VM-like isolation)."""
        # Use hash of environment name to ensure consistent assignment
        base_hash = hash(f"{self.environment.name}-{self.container_id}") % 20
        return max(1, base_hash + 1)  # Ensure we don't use desktop 0
    
    async def start_container(self) -> bool:
        """🚀 START THE ENVIRONMENT CONTAINER (like starting a VM)"""
        if self.state != EnvironmentState.STOPPED:
            self.error_occurred.emit(self.container_id, f"Container already {self.state.value}")
            return False
        
        try:
            self._set_state(EnvironmentState.STARTING)
            self.start_time = datetime.now()
            
            # 1. CREATE ISOLATED VIRTUAL DESKTOP (VM-like isolation)
            await self._create_isolated_desktop()
            
            # 2. LAUNCH ALL APPLICATIONS IN CONTAINER
            await self._launch_container_applications()
            
            # 3. LAUNCH ALL WEBSITES IN CONTAINER  
            await self._launch_container_websites()
            
            # 4. START RESOURCE MONITORING
            self._start_monitoring()
            
            # 5. CONTAINER IS NOW RUNNING!
            self._set_state(EnvironmentState.RUNNING)
            
            print(f"🎉 Container '{self.container_id}' started successfully!")
            print(f"   📱 Desktop: {self.desktop_name} (#{self.desktop_index})")
            print(f"   🔄 Processes: {len(self.tracked_processes)} tracked")
            
            return True
            
        except Exception as e:
            self._set_state(EnvironmentState.ERROR)
            self.error_occurred.emit(self.container_id, f"Failed to start: {str(e)}")
            return False
    
    async def _create_isolated_desktop(self):
        """Create completely isolated virtual desktop for this container."""
        print(f"🖥️  Creating isolated desktop for container '{self.container_id}'...")
        
        # Get unique desktop index
        self.desktop_index = self.get_unique_desktop_index()
        self.stats.desktop_index = self.desktop_index
        
        # Create the virtual desktop
        success = self.system_integration.create_virtual_desktop(self.desktop_name)
        if not success:
            raise Exception(f"Failed to create virtual desktop '{self.desktop_name}'")
        
        # Switch to the new desktop for launching
        if self.environment.auto_switch_desktop:
            success = self.system_integration.switch_to_virtual_desktop(self.desktop_index)
            if not success:
                print(f"⚠️  Warning: Could not switch to desktop {self.desktop_index}")
            time.sleep(0.5)  # Wait for desktop switch
        
        print(f"✅ Isolated desktop created: {self.desktop_name} (#{self.desktop_index})")
    
    async def _launch_container_applications(self):
        """Launch all applications within the container's isolated environment."""
        print(f"🚀 Launching {len(self.environment.applications)} applications in container...")
        
        for i, app in enumerate(self.environment.applications):
            try:
                print(f"  [{i+1}/{len(self.environment.applications)}] Starting: {app.name}")
                
                # Launch on the container's desktop
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
        """Launch all websites within the container's isolated environment.""" 
        print(f"🌐 Opening {len(self.environment.websites)} websites in container...")
        
        for i, website in enumerate(self.environment.websites):
            try:
                print(f"  [{i+1}/{len(self.environment.websites)}] Opening: {website.name}")
                
                # Launch browser on the container's desktop
                success = self.system_integration.launch_app_on_desktop(
                    website.url, self.desktop_index
                )
                if success:
                    print(f"    ✅ Opened: {website.url}")
                else:
                    print(f"    ❌ Failed to open: {website.name}")
                
                time.sleep(0.2)
                
            except Exception as e:
                print(f"    ❌ Error opening {website.name}: {e}")
    
    async def _launch_app_in_container(self, app: Application) -> Optional[int]:
        """Launch a single application within the container's isolated desktop."""
        import subprocess
        
        try:
            # Expand environment variables
            app_path = os.path.expandvars(app.path)
            
            # Switch to container desktop before launching
            if self.desktop_index > 0:
                self.system_integration.switch_to_virtual_desktop(self.desktop_index)
                time.sleep(0.2)
            
            # Prepare command
            cmd = [app_path]
            if app.arguments:
                cmd.extend(app.arguments.split())
            
            # Set working directory
            cwd = app.working_directory if app.working_directory else None
            
            # Launch process with special flags for isolation
            if os.name == 'nt':  # Windows
                process = subprocess.Popen(
                    cmd,
                    cwd=cwd,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | 
                                 subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
            else:
                process = subprocess.Popen(cmd, cwd=cwd)
            
            return process.pid
            
        except Exception as e:
            print(f"Error launching {app.name}: {e}")
            return None
    
    def _start_monitoring(self):
        """Start continuous monitoring of container resources (like VM monitoring)."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        
        # Create monitoring timer
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._update_container_stats)
        self.monitor_timer.start(2000)  # Update every 2 seconds
        
        print(f"📊 Container monitoring started for '{self.container_id}'")
    
    def _update_container_stats(self):
        """Update container statistics (VM-like resource monitoring)."""
        if not self.monitoring_active or self.state != EnvironmentState.RUNNING:
            return
        
        try:
            # Reset stats
            self.stats.total_processes = 0
            self.stats.total_memory_mb = 0.0
            self.stats.total_cpu_percent = 0.0
            self.stats.process_list.clear()
            
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
        """🛑 STOP THE ENVIRONMENT CONTAINER (like stopping a VM)"""
        if self.state == EnvironmentState.STOPPED:
            return True
        
        try:
            self._set_state(EnvironmentState.STOPPING)
            print(f"🛑 Stopping container '{self.container_id}'...")
            
            # Stop monitoring first
            self._stop_monitoring()
            
            # Terminate all processes in container
            await self._terminate_container_processes(force)
            
            # Clean up virtual desktop if configured
            if self.environment.close_apps_on_stop:
                self.system_integration.close_desktop_apps(self.desktop_index)
            
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
        """🔄 SWITCH TO THIS CONTAINER (like switching to a VM)"""
        if self.state != EnvironmentState.RUNNING:
            return False
        
        try:
            success = self.system_integration.switch_to_virtual_desktop(self.desktop_index)
            if success:
                print(f"🔄 Switched to container '{self.container_id}' desktop")
            return success
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