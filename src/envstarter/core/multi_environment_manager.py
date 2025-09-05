"""
🚀 MULTI-ENVIRONMENT CONTAINER MANAGER 🚀
The brain that manages multiple environment containers simultaneously!

This is like having a hypervisor that manages multiple VMs, but for 
Windows desktop environments. Run 5+ environments concurrently,
each in complete isolation!
"""

import asyncio
import threading
from typing import Dict, List, Optional, Set, Callable
from datetime import datetime
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from concurrent.futures import ThreadPoolExecutor

from src.envstarter.core.models import Environment
from src.envstarter.core.simple_environment_container import SimpleEnvironmentContainer as EnvironmentContainer, EnvironmentState
from src.envstarter.core.storage import ConfigManager


@dataclass 
class SystemResources:
    """Overall system resource usage across all containers."""
    total_containers: int = 0
    running_containers: int = 0
    paused_containers: int = 0
    total_processes: int = 0
    total_memory_mb: float = 0.0
    total_cpu_percent: float = 0.0
    active_desktops: List[int] = None
    
    def __post_init__(self):
        if self.active_desktops is None:
            self.active_desktops = []
    
    def to_dict(self) -> Dict:
        return {
            "total_containers": self.total_containers,
            "running_containers": self.running_containers, 
            "paused_containers": self.paused_containers,
            "total_processes": self.total_processes,
            "total_memory_mb": round(self.total_memory_mb, 1),
            "total_cpu_percent": round(self.total_cpu_percent, 1),
            "active_desktops": self.active_desktops
        }


class MultiEnvironmentManager(QObject):
    """
    🎯 THE ULTIMATE MULTI-ENVIRONMENT HYPERVISOR!
    
    Manages multiple environment containers simultaneously like a VM hypervisor:
    - Start/Stop multiple environments concurrently
    - Switch between running environments instantly  
    - Monitor resource usage across all containers
    - Handle environment isolation and conflicts
    - Provide VM-like container management
    """
    
    # Signals for multi-environment events
    container_started = pyqtSignal(str)  # container_id
    container_stopped = pyqtSignal(str)  # container_id  
    container_switched = pyqtSignal(str)  # container_id
    resources_updated = pyqtSignal(dict)  # system_resources
    max_containers_reached = pyqtSignal(int)  # max_limit
    environment_conflict = pyqtSignal(str, str)  # env1, env2
    
    def __init__(self):
        super().__init__()
        
        # Container management
        self.containers: Dict[str, EnvironmentContainer] = {}
        self.active_container_id: Optional[str] = None
        self.config_manager = ConfigManager()
        
        # System settings
        self.max_concurrent_containers = 10  # Maximum simultaneous containers
        self.desktop_index_pool = set(range(1, 21))  # Available desktop indices
        self.used_desktop_indices: Set[int] = set()
        
        # Resource monitoring
        self.system_resources = SystemResources()
        self.resource_monitor_active = False
        
        # Async event loop for container operations
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="EnvContainer")
        
        self._setup_resource_monitoring()
        
        print("🚀 Multi-Environment Manager initialized!")
        print(f"   📊 Max concurrent containers: {self.max_concurrent_containers}")
        print(f"   🖥️  Available desktop indices: {len(self.desktop_index_pool)}")
    
    def _setup_resource_monitoring(self):
        """Set up system-wide resource monitoring."""
        self.resource_timer = QTimer()
        self.resource_timer.timeout.connect(self._update_system_resources)
        self.resource_timer.start(3000)  # Update every 3 seconds
        self.resource_monitor_active = True
        
        print("📊 System resource monitoring started")
    
    def get_running_containers(self) -> List[str]:
        """Get list of currently running container IDs."""
        return [
            container_id for container_id, container in self.containers.items()
            if container.state == EnvironmentState.RUNNING
        ]
    
    def get_all_containers(self) -> Dict[str, Dict]:
        """Get information about all containers."""
        return {
            container_id: container.get_container_info()
            for container_id, container in self.containers.items()
        }
    
    def can_start_container(self) -> bool:
        """Check if we can start another container."""
        running_count = len(self.get_running_containers())
        return running_count < self.max_concurrent_containers
    
    async def start_environment_container(self, environment: Environment, 
                                        container_id: Optional[str] = None,
                                        switch_to: bool = True) -> str:
        """🚀 START A NEW ENVIRONMENT CONTAINER"""
        
        # Check if we can start another container
        if not self.can_start_container():
            self.max_containers_reached.emit(self.max_concurrent_containers)
            raise Exception(f"Maximum concurrent containers ({self.max_concurrent_containers}) reached!")
        
        # Generate container ID if not provided
        if not container_id:
            timestamp = datetime.now().strftime("%H%M%S")
            container_id = f"{environment.name}-{timestamp}"
        
        # Check for duplicate container ID
        if container_id in self.containers:
            raise Exception(f"Container '{container_id}' already exists!")
        
        print(f"🚀 Starting environment container: '{container_id}'")
        print(f"   🎯 Environment: {environment.name}")
        print(f"   📱 Apps: {len(environment.applications)}")
        print(f"   🌐 Websites: {len(environment.websites)}")
        
        try:
            # Create new container
            container = EnvironmentContainer(environment, container_id)
            
            # Connect container signals
            self._connect_container_signals(container)
            
            # Add to our container registry
            self.containers[container_id] = container
            
            # Start the container (this is async and VM-like)
            success = await container.start_container()
            
            if success:
                # Mark desktop index as used
                if container.desktop_index > 0:
                    self.used_desktop_indices.add(container.desktop_index)
                
                # Switch to the new container if requested
                if switch_to:
                    await self.switch_to_container(container_id)
                
                self.container_started.emit(container_id)
                
                print(f"✅ Container '{container_id}' started successfully!")
                return container_id
            else:
                # Cleanup on failure
                del self.containers[container_id]
                raise Exception("Container failed to start")
                
        except Exception as e:
            print(f"❌ Failed to start container '{container_id}': {e}")
            if container_id in self.containers:
                del self.containers[container_id]
            raise e
    
    async def stop_environment_container(self, container_id: str, force: bool = False) -> bool:
        """🛑 STOP AN ENVIRONMENT CONTAINER"""
        
        if container_id not in self.containers:
            print(f"⚠️  Container '{container_id}' not found")
            return False
        
        container = self.containers[container_id]
        
        print(f"🛑 Stopping container: '{container_id}'")
        
        try:
            # Stop the container
            success = await container.stop_container(force=force)
            
            if success:
                # Free up desktop index
                if container.desktop_index > 0:
                    self.used_desktop_indices.discard(container.desktop_index)
                
                # Remove from registry
                del self.containers[container_id]
                
                # If this was the active container, clear it
                if self.active_container_id == container_id:
                    self.active_container_id = None
                
                self.container_stopped.emit(container_id)
                
                print(f"✅ Container '{container_id}' stopped successfully")
                return True
            else:
                print(f"❌ Failed to stop container '{container_id}'")
                return False
                
        except Exception as e:
            print(f"❌ Error stopping container '{container_id}': {e}")
            return False
    
    async def restart_environment_container(self, container_id: str) -> bool:
        """🔄 RESTART AN ENVIRONMENT CONTAINER"""
        
        if container_id not in self.containers:
            return False
        
        container = self.containers[container_id]
        environment = container.environment
        
        print(f"🔄 Restarting container: '{container_id}'")
        
        # Stop the container
        await self.stop_environment_container(container_id, force=False)
        
        # Start it again
        try:
            new_container_id = await self.start_environment_container(
                environment, container_id, switch_to=True
            )
            return new_container_id == container_id
        except Exception as e:
            print(f"❌ Failed to restart container: {e}")
            return False
    
    async def switch_to_container(self, container_id: str) -> bool:
        """🔄 SWITCH TO A RUNNING CONTAINER (like switching VMs)"""
        
        if container_id not in self.containers:
            print(f"⚠️  Container '{container_id}' not found")
            return False
        
        container = self.containers[container_id]
        
        if container.state != EnvironmentState.RUNNING:
            print(f"⚠️  Container '{container_id}' is not running (state: {container.state.value})")
            return False
        
        try:
            # Switch to container's desktop
            success = container.switch_to_container()
            
            if success:
                self.active_container_id = container_id
                self.container_switched.emit(container_id)
                
                print(f"🔄 Switched to container: '{container_id}'")
                print(f"   🖥️  Desktop: {container.desktop_name} (#{container.desktop_index})")
                return True
            else:
                print(f"❌ Failed to switch to container '{container_id}'")
                return False
                
        except Exception as e:
            print(f"❌ Error switching to container '{container_id}': {e}")
            return False
    
    async def pause_container(self, container_id: str) -> bool:
        """⏸️ PAUSE A CONTAINER (suspend all processes)"""
        
        if container_id not in self.containers:
            return False
        
        container = self.containers[container_id]
        success = container.pause_container()
        
        if success:
            print(f"⏸️  Container '{container_id}' paused")
        
        return success
    
    async def resume_container(self, container_id: str) -> bool:
        """▶️ RESUME A PAUSED CONTAINER"""
        
        if container_id not in self.containers:
            return False
        
        container = self.containers[container_id]
        success = container.resume_container()
        
        if success:
            print(f"▶️  Container '{container_id}' resumed")
        
        return success
    
    def _connect_container_signals(self, container: EnvironmentContainer):
        """Connect container signals to manager handlers."""
        
        container.state_changed.connect(self._on_container_state_changed)
        container.stats_updated.connect(self._on_container_stats_updated)
        container.error_occurred.connect(self._on_container_error)
    
    def _on_container_state_changed(self, container_id: str, new_state: str):
        """Handle container state changes."""
        print(f"📊 Container '{container_id}' state: {new_state}")
    
    def _on_container_stats_updated(self, container_id: str, stats: Dict):
        """Handle container stats updates."""
        # This gets called frequently, so we just update our internal tracking
        pass
    
    def _on_container_error(self, container_id: str, error_message: str):
        """Handle container errors."""
        print(f"❌ Container '{container_id}' error: {error_message}")
    
    def _update_system_resources(self):
        """Update system-wide resource statistics."""
        if not self.resource_monitor_active:
            return
        
        try:
            # Reset totals
            self.system_resources.total_containers = len(self.containers)
            self.system_resources.running_containers = 0
            self.system_resources.paused_containers = 0
            self.system_resources.total_processes = 0
            self.system_resources.total_memory_mb = 0.0
            self.system_resources.total_cpu_percent = 0.0
            self.system_resources.active_desktops.clear()
            
            # Aggregate stats from all containers
            for container in self.containers.values():
                if container.state == EnvironmentState.RUNNING:
                    self.system_resources.running_containers += 1
                    self.system_resources.total_processes += container.stats.total_processes
                    self.system_resources.total_memory_mb += container.stats.total_memory_mb
                    self.system_resources.total_cpu_percent += container.stats.total_cpu_percent
                    
                    if container.desktop_index > 0:
                        self.system_resources.active_desktops.append(container.desktop_index)
                        
                elif container.state == EnvironmentState.PAUSED:
                    self.system_resources.paused_containers += 1
            
            # Emit updated resources
            self.resources_updated.emit(self.system_resources.to_dict())
            
        except Exception as e:
            print(f"Error updating system resources: {e}")
    
    async def stop_all_containers(self, force: bool = False) -> int:
        """🛑 STOP ALL RUNNING CONTAINERS"""
        
        container_ids = list(self.containers.keys())
        stopped_count = 0
        
        print(f"🛑 Stopping {len(container_ids)} containers...")
        
        # Stop all containers concurrently
        tasks = []
        for container_id in container_ids:
            task = self.stop_environment_container(container_id, force=force)
            tasks.append(task)
        
        # Wait for all containers to stop
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Error stopping container {container_ids[i]}: {result}")
            elif result:
                stopped_count += 1
        
        print(f"✅ Stopped {stopped_count}/{len(container_ids)} containers")
        return stopped_count
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status."""
        
        container_details = {}
        for container_id, container in self.containers.items():
            container_details[container_id] = {
                "environment_name": container.environment.name,
                "state": container.state.value,
                "desktop_index": container.desktop_index,
                "uptime": container.stats.uptime_seconds,
                "processes": container.stats.total_processes,
                "memory_mb": container.stats.total_memory_mb
            }
        
        return {
            "system_resources": self.system_resources.to_dict(),
            "containers": container_details,
            "active_container": self.active_container_id,
            "max_containers": self.max_concurrent_containers,
            "available_desktop_indices": len(self.desktop_index_pool - self.used_desktop_indices)
        }
    
    def shutdown(self):
        """Shutdown the manager and cleanup all resources."""
        print("🛑 Shutting down Multi-Environment Manager...")
        
        # Stop resource monitoring
        self.resource_monitor_active = False
        if hasattr(self, 'resource_timer'):
            self.resource_timer.stop()
        
        # Stop all containers
        if self.containers:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.stop_all_containers(force=True))
            loop.close()
        
        # Shutdown thread pool
        self.executor.shutdown(wait=True)
        
        print("✅ Multi-Environment Manager shutdown complete")


# Global instance for the application
_manager_instance: Optional[MultiEnvironmentManager] = None


def get_multi_environment_manager() -> MultiEnvironmentManager:
    """Get the global multi-environment manager instance."""
    global _manager_instance
    
    if _manager_instance is None:
        _manager_instance = MultiEnvironmentManager()
    
    return _manager_instance


def shutdown_multi_environment_manager():
    """Shutdown the global manager instance."""
    global _manager_instance
    
    if _manager_instance is not None:
        _manager_instance.shutdown()
        _manager_instance = None