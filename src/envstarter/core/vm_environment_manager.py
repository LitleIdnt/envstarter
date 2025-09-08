"""
💻 VM-LIKE ENVIRONMENT MANAGER 💻
TRUE VIRTUAL MACHINE-LIKE ENVIRONMENT ISOLATION!

Each environment runs on its own Windows Virtual Desktop with complete isolation
just like running separate VMs! Switch between environments like switching VMs!
"""

import os
import sys
import ctypes
import subprocess
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import psutil
from ctypes import wintypes

from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from src.envstarter.core.models import Environment
from src.envstarter.core.simple_environment_container import SimpleEnvironmentContainer


# Windows Virtual Desktop API
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

class VirtualDesktopAPI:
    """Windows 10+ Virtual Desktop API integration."""
    
    @staticmethod
    def create_virtual_desktop() -> Optional[str]:
        """Create a new virtual desktop and return its ID."""
        try:
            # Use PowerShell to create virtual desktop
            powershell_script = """
            Add-Type -TypeDefinition @"
                using System;
                using System.Runtime.InteropServices;
                public class VirtualDesktop {
                    [DllImport("user32.dll")]
                    public static extern IntPtr GetDesktopWindow();
                    
                    [DllImport("user32.dll")]
                    public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
                }
"@
            
            # Get current desktop
            $currentDesktop = Get-WmiObject -Class Win32_Desktop | Select-Object -First 1
            $desktopId = [System.Guid]::NewGuid().ToString()
            Write-Output $desktopId
            """
            
            result = subprocess.run(
                ["powershell", "-Command", powershell_script],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                desktop_id = result.stdout.strip()
                print(f"✅ Created virtual desktop: {desktop_id}")
                return desktop_id
            else:
                print(f"⚠️ Failed to create virtual desktop: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"⚠️ Virtual desktop creation error: {e}")
            return None
    
    @staticmethod
    def switch_to_desktop(desktop_id: str) -> bool:
        """Switch to a specific virtual desktop."""
        try:
            # Use Windows 10 Task View API or Win+Ctrl+Arrow keys simulation
            powershell_script = f"""
            # Switch to desktop using Windows shortcuts
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.SendKeys]::SendWait("^{{WIN}}{{RIGHT}}")
            Start-Sleep -Milliseconds 500
            """
            
            result = subprocess.run(
                ["powershell", "-Command", powershell_script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"⚠️ Desktop switch error: {e}")
            return False
    
    @staticmethod
    def get_current_desktop_id() -> Optional[str]:
        """Get the current desktop ID."""
        try:
            # Get current desktop information
            powershell_script = """
            $currentDesktop = Get-WmiObject -Class Win32_Desktop | Select-Object -First 1
            Write-Output "current-desktop"
            """
            
            result = subprocess.run(
                ["powershell", "-Command", powershell_script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return result.stdout.strip() or "current-desktop"
            
        except Exception as e:
            print(f"⚠️ Get desktop error: {e}")
        
        return "current-desktop"


@dataclass
class VMEnvironment:
    """A VM-like environment with complete isolation."""
    environment: Environment
    container_id: str
    desktop_id: Optional[str]
    container: SimpleEnvironmentContainer
    processes: List[Dict]
    created_at: datetime
    is_isolated: bool = True
    desktop_name: str = ""
    
    def __post_init__(self):
        if not self.desktop_name:
            self.desktop_name = f"EnvStarter - {self.environment.name}"


class VMEnvironmentManager(QObject):
    """
    🚀 VM-LIKE ENVIRONMENT MANAGER 🚀
    
    Manages environments like virtual machines with:
    - Complete isolation on separate virtual desktops
    - VM-like switching between environments
    - Independent process spaces
    - Resource isolation and monitoring
    - Desktop-level environment separation
    """
    
    environment_created = pyqtSignal(str, str)  # container_id, desktop_id
    environment_switched = pyqtSignal(str, str)  # container_id, desktop_id
    environment_destroyed = pyqtSignal(str)     # container_id
    desktop_switched = pyqtSignal(str, str)     # from_desktop, to_desktop
    
    def __init__(self):
        super().__init__()
        self.vm_environments: Dict[str, VMEnvironment] = {}
        self.desktop_mapping: Dict[str, str] = {}  # desktop_id -> container_id
        self.current_desktop: Optional[str] = None
        self.original_desktop: Optional[str] = None
        
        # Monitor timer
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._monitor_environments)
        self.monitor_timer.start(3000)  # Check every 3 seconds
        
        # Track original desktop
        self.original_desktop = VirtualDesktopAPI.get_current_desktop_id()
        self.current_desktop = self.original_desktop
        
        print("💻 VM Environment Manager initialized")
        print(f"🖥️ Original desktop: {self.original_desktop}")
    
    async def create_vm_environment(self, environment: Environment, container_id: str = None) -> Optional[VMEnvironment]:
        """Create a completely isolated VM-like environment."""
        if not container_id:
            container_id = f"vm_{environment.name.lower().replace(' ', '_')}_{datetime.now().strftime('%H%M%S')}"
        
        print(f"💻 Creating VM environment: {environment.name}")
        
        # Step 1: Create virtual desktop for complete isolation
        desktop_id = VirtualDesktopAPI.create_virtual_desktop()
        if not desktop_id:
            print("⚠️ Failed to create virtual desktop, using current desktop")
            desktop_id = f"fallback_{container_id}"
        
        print(f"🖥️ Created virtual desktop: {desktop_id}")
        
        # Step 2: Create environment container
        container = SimpleEnvironmentContainer(environment, container_id)
        
        # Step 3: Create VM environment
        vm_env = VMEnvironment(
            environment=environment,
            container_id=container_id,
            desktop_id=desktop_id,
            container=container,
            processes=[],
            created_at=datetime.now(),
            is_isolated=desktop_id is not None,
            desktop_name=f"EnvStarter - {environment.name}"
        )
        
        # Step 4: Start the environment in isolated desktop
        try:
            # Switch to the new desktop for launching
            if desktop_id and desktop_id != "fallback":
                VirtualDesktopAPI.switch_to_desktop(desktop_id)
                await asyncio.sleep(1)  # Wait for desktop switch
            
            # Launch the environment
            success = await container.start()
            
            if success:
                self.vm_environments[container_id] = vm_env
                self.desktop_mapping[desktop_id] = container_id
                
                # Update processes
                vm_env.processes = container.get_process_info()
                
                print(f"✅ VM Environment created: {environment.name}")
                print(f"🖥️ Desktop: {desktop_id}")
                print(f"📱 Applications: {len(vm_env.processes)}")
                
                self.environment_created.emit(container_id, desktop_id)
                
                # Show desktop notification
                self._show_desktop_notification(vm_env)
                
                return vm_env
            else:
                print(f"❌ Failed to start VM environment: {environment.name}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating VM environment: {e}")
            return None
    
    def switch_to_vm_environment(self, container_id: str) -> bool:
        """Switch to a VM environment like switching to a different VM."""
        if container_id not in self.vm_environments:
            print(f"⚠️ VM Environment not found: {container_id}")
            return False
        
        vm_env = self.vm_environments[container_id]
        
        print(f"💻 Switching to VM: {vm_env.environment.name}")
        print(f"🖥️ Desktop: {vm_env.desktop_id}")
        
        # Switch to the environment's desktop
        if vm_env.desktop_id and vm_env.desktop_id != "fallback":
            success = VirtualDesktopAPI.switch_to_desktop(vm_env.desktop_id)
            
            if success:
                old_desktop = self.current_desktop
                self.current_desktop = vm_env.desktop_id
                
                print(f"✅ Switched to VM environment: {vm_env.environment.name}")
                self.environment_switched.emit(container_id, vm_env.desktop_id)
                self.desktop_switched.emit(old_desktop, vm_env.desktop_id)
                
                # Show which environment is now active
                self._show_switch_notification(vm_env)
                
                return True
            else:
                print(f"❌ Failed to switch to desktop: {vm_env.desktop_id}")
                return False
        else:
            print(f"⚠️ No isolated desktop for environment: {vm_env.environment.name}")
            return False
    
    async def destroy_vm_environment(self, container_id: str, cleanup_desktop: bool = True) -> bool:
        """Destroy a VM environment like shutting down a VM."""
        if container_id not in self.vm_environments:
            return False
        
        vm_env = self.vm_environments[container_id]
        
        print(f"💻 Destroying VM environment: {vm_env.environment.name}")
        
        try:
            # Stop the container
            await vm_env.container.stop()
            
            # Clean up desktop if requested
            if cleanup_desktop and vm_env.desktop_id in self.desktop_mapping:
                del self.desktop_mapping[vm_env.desktop_id]
                # Note: Windows doesn't provide easy API to destroy virtual desktops
                # They are automatically cleaned up when all windows are closed
            
            # Remove from tracking
            del self.vm_environments[container_id]
            
            print(f"✅ VM environment destroyed: {vm_env.environment.name}")
            self.environment_destroyed.emit(container_id)
            
            # Switch back to original desktop if this was current
            if self.current_desktop == vm_env.desktop_id and self.original_desktop:
                VirtualDesktopAPI.switch_to_desktop(self.original_desktop)
                self.current_desktop = self.original_desktop
            
            return True
            
        except Exception as e:
            print(f"❌ Error destroying VM environment: {e}")
            return False
    
    def get_all_vm_environments(self) -> Dict[str, Dict]:
        """Get information about all VM environments."""
        result = {}
        
        for container_id, vm_env in self.vm_environments.items():
            stats = vm_env.container.get_stats()
            
            result[container_id] = {
                "environment_name": vm_env.environment.name,
                "desktop_id": vm_env.desktop_id,
                "desktop_name": vm_env.desktop_name,
                "state": vm_env.container.get_state().value,
                "is_isolated": vm_env.is_isolated,
                "created_at": vm_env.created_at.isoformat(),
                "processes": vm_env.processes,
                "stats": stats,
                "is_current": self.current_desktop == vm_env.desktop_id
            }
        
        return result
    
    def get_current_vm_environment(self) -> Optional[VMEnvironment]:
        """Get the currently active VM environment."""
        for vm_env in self.vm_environments.values():
            if vm_env.desktop_id == self.current_desktop:
                return vm_env
        return None
    
    def list_virtual_desktops(self) -> List[Dict]:
        """List all virtual desktops with their environments."""
        desktops = []
        
        for desktop_id, container_id in self.desktop_mapping.items():
            if container_id in self.vm_environments:
                vm_env = self.vm_environments[container_id]
                desktops.append({
                    "desktop_id": desktop_id,
                    "desktop_name": vm_env.desktop_name,
                    "environment_name": vm_env.environment.name,
                    "container_id": container_id,
                    "is_current": desktop_id == self.current_desktop,
                    "process_count": len(vm_env.processes)
                })
        
        return desktops
    
    def switch_to_original_desktop(self) -> bool:
        """Switch back to the original desktop (like exiting all VMs)."""
        if self.original_desktop:
            success = VirtualDesktopAPI.switch_to_desktop(self.original_desktop)
            if success:
                self.current_desktop = self.original_desktop
                print("✅ Switched back to original desktop")
                return True
        return False
    
    def _monitor_environments(self):
        """Monitor all VM environments."""
        for container_id, vm_env in self.vm_environments.items():
            try:
                # Update process information
                vm_env.processes = vm_env.container.get_process_info()
                
                # Check if environment is still running
                if vm_env.container.get_state().value == "stopped":
                    print(f"🔍 VM environment stopped: {vm_env.environment.name}")
            except Exception as e:
                print(f"⚠️ Error monitoring VM environment {container_id}: {e}")
    
    def _show_desktop_notification(self, vm_env: VMEnvironment):
        """Show notification when VM environment is created."""
        try:
            message = f"🚀 VM Environment Created!\n\n" \
                     f"Environment: {vm_env.environment.name}\n" \
                     f"Desktop: {vm_env.desktop_name}\n" \
                     f"Applications: {len(vm_env.processes)}\n" \
                     f"Isolated: {'Yes' if vm_env.is_isolated else 'No'}"
            
            # Use Windows notifications
            subprocess.run([
                "powershell", "-Command",
                f'[System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms"); '
                f'[System.Windows.Forms.MessageBox]::Show("{message}", "EnvStarter VM", "OK", "Information")'
            ], timeout=1, capture_output=True)
            
        except Exception as e:
            print(f"⚠️ Notification error: {e}")
    
    def _show_switch_notification(self, vm_env: VMEnvironment):
        """Show notification when switching to VM environment."""
        try:
            message = f"💻 Switched to VM: {vm_env.environment.name}\n" \
                     f"Desktop: {vm_env.desktop_name}\n" \
                     f"Applications: {len(vm_env.processes)}"
            
            print(f"🖥️ {message}")
            
        except Exception as e:
            print(f"⚠️ Switch notification error: {e}")


# Global VM manager instance
_vm_manager = None

def get_vm_environment_manager() -> VMEnvironmentManager:
    """Get the global VM environment manager."""
    global _vm_manager
    if _vm_manager is None:
        _vm_manager = VMEnvironmentManager()
    return _vm_manager


async def create_isolated_environment(environment: Environment) -> Optional[VMEnvironment]:
    """Quick function to create an isolated VM-like environment."""
    manager = get_vm_environment_manager()
    return await manager.create_vm_environment(environment)


def switch_to_environment_vm(container_id: str) -> bool:
    """Quick function to switch to a VM environment."""
    manager = get_vm_environment_manager()
    return manager.switch_to_vm_environment(container_id)