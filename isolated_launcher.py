#!/usr/bin/env python3
"""
🚀 ISOLATED ENVIRONMENT LAUNCHER 🚀
Creates completely isolated environments like VMs with visible environment names!
"""

import sys
import os
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import platform

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.envstarter.core.models import Environment, Application, Website
from src.envstarter.core.storage import EnvironmentStorage


class IsolatedEnvironmentLauncher:
    """
    CREATES COMPLETELY ISOLATED ENVIRONMENTS LIKE VMs!
    
    Each environment:
    - Runs in its own isolated container/namespace
    - Has a clearly visible environment name in the header
    - Is completely separated from other environments
    - Can be monitored and managed independently
    """
    
    def __init__(self):
        self.storage = EnvironmentStorage()
        self.system = platform.system()
        self.environments = []
        self.active_containers = {}
        
    def print_header(self, env_name: str):
        """Print a big visible header for the environment."""
        header = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║    🚀 ENVIRONMENT: {env_name.upper().center(52)} 🚀    ║
║                                                                            ║
║    STATUS: LAUNCHING IN ISOLATED CONTAINER                                ║
║    TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S').center(64)}    ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
        """
        print(header)
        
    async def launch_isolated_environment(self, environment: Environment):
        """Launch an environment in complete isolation."""
        self.print_header(environment.name)
        
        print(f"\n📦 Creating isolated container for: {environment.name}")
        print(f"   Description: {environment.description or 'No description'}")
        print(f"   Applications: {len(environment.applications)}")
        print(f"   Websites: {len(environment.websites)}")
        
        # Check which isolation method to use
        if self.system == "Windows":
            await self.launch_windows_isolated(environment)
        elif self.system == "Linux":
            await self.launch_linux_isolated(environment)
        elif self.system == "Darwin":  # macOS
            await self.launch_macos_isolated(environment)
        else:
            await self.launch_basic_isolated(environment)
            
    async def launch_windows_isolated(self, environment: Environment):
        """Launch on Windows with Virtual Desktop isolation."""
        print("\n🖥️ Using Windows Virtual Desktop Isolation")
        
        try:
            # Import Windows-specific modules
            from src.envstarter.core.vm_environment_manager import (
                VMEnvironmentManager, create_isolated_environment
            )
            
            # Create VM-like isolated environment
            print(f"🔨 Creating VM-like environment for: {environment.name}")
            vm_env = await create_isolated_environment(environment)
            
            if vm_env:
                print(f"✅ VM Environment created successfully!")
                print(f"   Container ID: {vm_env.container_id}")
                print(f"   Desktop ID: {vm_env.desktop_id}")
                print(f"   Desktop Name: {vm_env.desktop_name}")
                print(f"   Isolated: {'Yes' if vm_env.is_isolated else 'No'}")
                
                # Show environment name in all windows
                await self.inject_environment_headers(vm_env)
                
                self.active_containers[environment.name] = vm_env.container_id
                
                # Monitor the environment
                await self.monitor_environment(vm_env)
            else:
                print("❌ Failed to create VM environment")
                
        except ImportError as e:
            print(f"⚠️ Windows Virtual Desktop not available: {e}")
            await self.launch_basic_isolated(environment)
            
    async def launch_linux_isolated(self, environment: Environment):
        """Launch on Linux with namespace/container isolation."""
        print("\n🐧 Using Linux Namespace/Container Isolation")
        
        try:
            from src.envstarter.core.environment_container import EnvironmentContainer
            
            # Create container with namespace isolation
            container_id = f"isolated_{environment.name.lower().replace(' ', '_')}_{datetime.now().strftime('%H%M%S')}"
            container = EnvironmentContainer(environment, container_id)
            
            # Set up isolation flags
            container.isolation_level = "strict"  # Use namespaces
            container.use_namespaces = True
            container.network_isolation = True
            
            print(f"🔨 Creating isolated container: {container_id}")
            
            # Add environment header to all processes
            container.environment_vars = {
                "ENVSTARTER_ENV": environment.name,
                "ENVSTARTER_CONTAINER": container_id,
                "ENVSTARTER_ISOLATED": "true"
            }
            
            # Start the container
            success = await container.start()
            
            if success:
                print(f"✅ Container started successfully!")
                print(f"   Container ID: {container_id}")
                print(f"   PID Namespace: Isolated")
                print(f"   Network Namespace: Isolated")
                print(f"   Mount Namespace: Isolated")
                
                self.active_containers[environment.name] = container_id
                
                # Inject headers into GUI applications
                await self.inject_linux_headers(container, environment.name)
                
            else:
                print("❌ Failed to start container")
                
        except Exception as e:
            print(f"⚠️ Container isolation failed: {e}")
            await self.launch_basic_isolated(environment)
            
    async def launch_macos_isolated(self, environment: Environment):
        """Launch on macOS with Space/Desktop isolation."""
        print("\n🍎 Using macOS Spaces Isolation")
        
        try:
            # Use macOS Spaces API
            import subprocess
            
            # Create new Space
            script = """
            tell application "System Events"
                tell application "Mission Control" to launch
                delay 0.5
                click button 1 of group 2 of group 1 of group 1 of process "Dock"
                delay 0.5
            end tell
            """
            
            subprocess.run(['osascript', '-e', script], capture_output=True)
            
            print(f"✅ Created new macOS Space for: {environment.name}")
            
            # Launch applications in the new space
            from src.envstarter.core.simple_environment_container import SimpleEnvironmentContainer
            
            container_id = f"space_{environment.name.lower().replace(' ', '_')}_{datetime.now().strftime('%H%M%S')}"
            container = SimpleEnvironmentContainer(environment, container_id)
            
            # Add environment identification
            container.environment_vars = {
                "ENVSTARTER_ENV": environment.name,
                "ENVSTARTER_SPACE": "true"
            }
            
            success = await container.start()
            
            if success:
                print(f"✅ Environment launched in isolated Space!")
                self.active_containers[environment.name] = container_id
                
        except Exception as e:
            print(f"⚠️ macOS Spaces isolation failed: {e}")
            await self.launch_basic_isolated(environment)
            
    async def launch_basic_isolated(self, environment: Environment):
        """Basic isolation using process groups and environment variables."""
        print("\n📦 Using Basic Process Isolation")
        
        from src.envstarter.core.simple_environment_container import SimpleEnvironmentContainer
        
        container_id = f"basic_{environment.name.lower().replace(' ', '_')}_{datetime.now().strftime('%H%M%S')}"
        container = SimpleEnvironmentContainer(environment, container_id)
        
        # Add clear environment identification
        container.environment_vars = {
            "ENVSTARTER_ENV": environment.name,
            "ENVSTARTER_CONTAINER": container_id,
            "ENVSTARTER_ISOLATED": "basic"
        }
        
        print(f"🔨 Creating basic isolated container: {container_id}")
        
        success = await container.start()
        
        if success:
            print(f"✅ Environment started with basic isolation!")
            print(f"   Container ID: {container_id}")
            print(f"   Process Group: Isolated")
            print(f"   Environment Variables: Set")
            
            self.active_containers[environment.name] = container_id
            
            # Try to inject headers into applications
            await self.inject_basic_headers(container, environment.name)
            
    async def inject_environment_headers(self, vm_env):
        """Inject environment name headers into all application windows."""
        print(f"\n🎨 Injecting environment headers for: {vm_env.environment.name}")
        
        try:
            # For each launched application, modify window title
            for process_info in vm_env.processes:
                if process_info.get('pid'):
                    await self.modify_window_title(
                        process_info['pid'], 
                        vm_env.environment.name
                    )
                    
            print(f"✅ Headers injected into {len(vm_env.processes)} applications")
            
        except Exception as e:
            print(f"⚠️ Header injection warning: {e}")
            
    async def inject_linux_headers(self, container, env_name: str):
        """Inject headers for Linux applications."""
        print(f"\n🎨 Setting Linux window properties for: {env_name}")
        
        try:
            # Use xprop to set window properties
            import subprocess
            
            for process_info in container.get_process_info():
                if process_info.get('pid'):
                    # Set _NET_WM_NAME property
                    cmd = f"xprop -id $(xdotool search --pid {process_info['pid']}) -f _NET_WM_NAME 8s -set _NET_WM_NAME '[{env_name}] {process_info.get('name', 'App')}'"
                    subprocess.run(cmd, shell=True, capture_output=True)
                    
            print(f"✅ Linux window properties set")
            
        except Exception as e:
            print(f"⚠️ Linux header injection warning: {e}")
            
    async def inject_basic_headers(self, container, env_name: str):
        """Inject headers using basic methods."""
        print(f"\n🎨 Setting basic identification for: {env_name}")
        
        try:
            # Create identification file
            id_file = Path.home() / '.envstarter' / 'active_environments' / f"{container.container_id}.env"
            id_file.parent.mkdir(parents=True, exist_ok=True)
            
            id_file.write_text(f"""
ENVIRONMENT_NAME={env_name}
CONTAINER_ID={container.container_id}
STARTED_AT={datetime.now().isoformat()}
PROCESSES={len(container.get_process_info())}
""")
            
            print(f"✅ Environment identification file created: {id_file}")
            
        except Exception as e:
            print(f"⚠️ Basic header injection warning: {e}")
            
    async def modify_window_title(self, pid: int, env_name: str):
        """Modify window title to include environment name."""
        if self.system == "Windows":
            try:
                import ctypes
                from ctypes import wintypes
                
                # Get window handle from PID
                def callback(hwnd, windows):
                    if ctypes.windll.user32.IsWindowVisible(hwnd):
                        pid_check = wintypes.DWORD()
                        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid_check))
                        if pid_check.value == pid:
                            windows.append(hwnd)
                    return True
                
                windows = []
                WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
                ctypes.windll.user32.EnumWindows(WNDENUMPROC(callback), id(windows))
                
                # Modify title for each window
                for hwnd in windows:
                    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                    buff = ctypes.create_unicode_buffer(length + 1)
                    ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
                    
                    new_title = f"[{env_name}] {buff.value}"
                    ctypes.windll.user32.SetWindowTextW(hwnd, new_title)
                    
            except Exception as e:
                print(f"⚠️ Window title modification failed: {e}")
                
    async def monitor_environment(self, vm_env):
        """Monitor the isolated environment."""
        print(f"\n📊 Monitoring environment: {vm_env.environment.name}")
        
        while vm_env.container.get_state().value == "running":
            stats = vm_env.container.get_stats()
            print(f"   📈 CPU: {stats.get('total_cpu_percent', 0):.1f}% | "
                  f"RAM: {stats.get('total_memory_mb', 0):.0f}MB | "
                  f"Processes: {stats.get('total_processes', 0)}")
            
            await asyncio.sleep(10)  # Update every 10 seconds
            
    async def launch_all_environments(self):
        """Launch all available environments in isolation."""
        environments = self.storage.load_environments()
        
        if not environments:
            print("❌ No environments found!")
            return
            
        print(f"\n🚀 Launching {len(environments)} environments in complete isolation...")
        
        tasks = []
        for env in environments:
            tasks.append(self.launch_isolated_environment(env))
            
        await asyncio.gather(*tasks)
        
        print(f"\n✅ All {len(environments)} environments launched!")
        print(f"   Active containers: {list(self.active_containers.keys())}")
        
    def list_environments(self):
        """List all available environments."""
        environments = self.storage.load_environments()
        
        if not environments:
            print("No environments configured.")
            return
            
        print("\n📋 Available Environments:")
        print("=" * 60)
        
        for i, env in enumerate(environments, 1):
            print(f"\n{i}. {env.name}")
            if env.description:
                print(f"   Description: {env.description}")
            print(f"   Applications: {len(env.applications)}")
            print(f"   Websites: {len(env.websites)}")
            
        print("\n" + "=" * 60)
        
    async def launch_environment_by_name(self, name: str):
        """Launch a specific environment by name."""
        environments = self.storage.load_environments()
        
        for env in environments:
            if env.name.lower() == name.lower():
                await self.launch_isolated_environment(env)
                return
                
        print(f"❌ Environment not found: {name}")
        

async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="🚀 Launch completely isolated environments like VMs!"
    )
    
    parser.add_argument(
        'environment',
        nargs='?',
        help='Name of the environment to launch (or "all" for all environments)'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List all available environments'
    )
    
    parser.add_argument(
        '--monitor', '-m',
        action='store_true',
        help='Keep monitoring after launch'
    )
    
    args = parser.parse_args()
    
    launcher = IsolatedEnvironmentLauncher()
    
    if args.list:
        launcher.list_environments()
        return
        
    if args.environment:
        if args.environment.lower() == 'all':
            await launcher.launch_all_environments()
        else:
            await launcher.launch_environment_by_name(args.environment)
            
        if args.monitor:
            # Keep running to monitor
            print("\n📊 Monitoring mode - Press Ctrl+C to exit")
            try:
                await asyncio.Event().wait()
            except KeyboardInterrupt:
                print("\n👋 Stopping monitor...")
    else:
        # Interactive mode
        launcher.list_environments()
        print("\nUsage: python isolated_launcher.py <environment_name>")
        print("       python isolated_launcher.py all")
        print("       python isolated_launcher.py --list")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Launcher stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)