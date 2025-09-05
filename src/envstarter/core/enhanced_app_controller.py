"""
🚀 ENHANCED APP CONTROLLER 🚀
Revolutionary multi-environment controller with VM-like capabilities!

This is the new brain of EnvStarter that can handle multiple environments
running simultaneously like a hypervisor managing VMs!
"""

import sys
import asyncio
import threading
from typing import Optional, List, Dict
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication, QMessageBox
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from src.envstarter.core.storage import ConfigManager
from src.envstarter.core.models import Environment
from src.envstarter.core.multi_environment_manager import get_multi_environment_manager, shutdown_multi_environment_manager
from src.envstarter.core.concurrent_launcher import get_concurrent_launcher, LaunchMode
from src.envstarter.core.simple_environment_container import EnvironmentState
from src.envstarter.utils.system_integration import SystemIntegration
from src.envstarter.utils.icons import get_tray_icon


class EnhancedAppController(QObject):
    """
    🎯 ENHANCED APPLICATION CONTROLLER
    
    The revolutionary new controller that provides:
    - Multi-environment management (like a VM hypervisor)
    - Concurrent environment launching
    - Real-time container monitoring
    - Advanced system tray with container switching
    - VM-like isolation and control
    """
    
    # Enhanced signals
    container_started = pyqtSignal(str)  # container_id
    container_stopped = pyqtSignal(str)  # container_id
    container_switched = pyqtSignal(str) # container_id
    system_resources_updated = pyqtSignal(dict)  # resources
    settings_requested = pyqtSignal()
    show_selector_requested = pyqtSignal()
    show_dashboard_requested = pyqtSignal()
    quit_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Core components
        self.config_manager = ConfigManager()
        self.system_integration = SystemIntegration()
        
        # Multi-environment system
        self.manager = get_multi_environment_manager()
        self.launcher = get_concurrent_launcher()
        
        # UI components
        self.tray_icon = None
        self.tray_menu = None
        
        # State tracking
        self.active_containers: Dict[str, Dict] = {}
        self.tray_update_timer = QTimer()
        
        self._setup_connections()
        self._setup_tray_updates()
        
        print("🚀 Enhanced App Controller initialized!")
        print("   ✅ Multi-environment manager ready")
        print("   ✅ Concurrent launcher ready")
        print("   ✅ System integration ready")
    
    def _setup_connections(self):
        """Set up signal connections."""
        # Manager signals
        self.manager.container_started.connect(self._on_container_started)
        self.manager.container_stopped.connect(self._on_container_stopped)
        self.manager.container_switched.connect(self._on_container_switched)
        self.manager.resources_updated.connect(self._on_resources_updated)
        self.manager.max_containers_reached.connect(self._on_max_containers_reached)
        
        # Launcher signals
        self.launcher.launch_started.connect(self._on_launch_started)
        self.launcher.launch_completed.connect(self._on_launch_completed)
        self.launcher.all_launches_completed.connect(self._on_all_launches_completed)
    
    def _setup_tray_updates(self):
        """Set up automatic tray menu updates."""
        self.tray_update_timer.timeout.connect(self._update_tray_menu)
        self.tray_update_timer.start(10000)  # Update every 10 seconds
    
    def setup_system_tray(self) -> bool:
        """🎯 Set up the ENHANCED system tray with multi-environment support."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("⚠️  System tray not available")
            return False
        
        self.tray_icon = QSystemTrayIcon()
        
        # Create tray icon
        icon = get_tray_icon()
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("🎮 EnvStarter Multi-Environment")
        
        # Create enhanced context menu
        self._create_tray_menu()
        
        # Double-click to show dashboard
        self.tray_icon.activated.connect(self._on_tray_activated)
        
        self.tray_icon.show()
        
        print("✅ Enhanced system tray initialized")
        return True
    
    def _create_tray_menu(self):
        """Create the enhanced tray context menu."""
        menu = QMenu()
        
        # Header
        header_action = QAction("🎮 EnvStarter Multi-Environment", menu)
        header_action.setEnabled(False)
        header_font = header_action.font()
        header_font.setBold(True)
        header_action.setFont(header_font)
        menu.addAction(header_action)
        
        menu.addSeparator()
        
        # Dashboard
        dashboard_action = QAction("🎮 Open Dashboard", menu)
        dashboard_action.triggered.connect(self.show_dashboard_requested.emit)
        menu.addAction(dashboard_action)
        
        # Environment Selector
        selector_action = QAction("🎯 Environment Selector", menu)
        selector_action.triggered.connect(self.show_selector_requested.emit)
        menu.addAction(selector_action)
        
        menu.addSeparator()
        
        # Running Containers Section
        self.containers_menu = menu.addMenu("📦 Running Containers")
        self._update_containers_menu()
        
        # Quick Launch Section
        quick_launch_menu = menu.addMenu("🚀 Quick Launch")
        self._populate_quick_launch_menu(quick_launch_menu)
        
        menu.addSeparator()
        
        # Batch Operations
        batch_menu = menu.addMenu("⚡ Batch Operations")
        
        launch_all_action = QAction("🚀 Launch All Environments", menu)
        launch_all_action.triggered.connect(self.launch_all_environments)
        batch_menu.addAction(launch_all_action)
        
        stop_all_action = QAction("🛑 Stop All Containers", menu)
        stop_all_action.triggered.connect(self.stop_all_containers)
        batch_menu.addAction(stop_all_action)
        
        menu.addSeparator()
        
        # System Status
        status_menu = menu.addMenu("📊 System Status")
        self._populate_status_menu(status_menu)
        
        menu.addSeparator()
        
        # Settings
        settings_action = QAction("⚙️ Settings", menu)
        settings_action.triggered.connect(self.settings_requested.emit)
        menu.addAction(settings_action)
        
        # Exit
        exit_action = QAction("❌ Exit", menu)
        exit_action.triggered.connect(self.quit_application)
        menu.addAction(exit_action)
        
        self.tray_menu = menu
        self.tray_icon.setContextMenu(menu)
    
    def _update_containers_menu(self):
        """Update the running containers menu."""
        if not self.containers_menu:
            return
        
        self.containers_menu.clear()
        
        containers = self.manager.get_all_containers()
        running_containers = {
            cid: info for cid, info in containers.items()
            if info["state"] == "running"
        }
        
        if not running_containers:
            no_containers_action = QAction("No containers running", self.containers_menu)
            no_containers_action.setEnabled(False)
            self.containers_menu.addAction(no_containers_action)
            return
        
        for container_id, info in running_containers.items():
            env_name = info.get("environment_name", "Unknown")
            desktop_idx = info.get("desktop_index", -1)
            
            # Create container submenu
            container_menu = self.containers_menu.addMenu(f"🎯 {env_name}")
            
            # Switch action
            switch_action = QAction(f"🔄 Switch to Desktop #{desktop_idx}", container_menu)
            switch_action.triggered.connect(lambda checked, cid=container_id: self.switch_to_container(cid))
            container_menu.addAction(switch_action)
            
            # Container stats
            stats = info.get("stats", {})
            processes = stats.get("total_processes", 0)
            memory_mb = stats.get("total_memory_mb", 0)
            
            stats_action = QAction(f"📊 {processes} processes, {memory_mb:.0f}MB", container_menu)
            stats_action.setEnabled(False)
            container_menu.addAction(stats_action)
            
            container_menu.addSeparator()
            
            # Pause/Resume
            if info["state"] == "running":
                pause_action = QAction("⏸️ Pause Container", container_menu)
                pause_action.triggered.connect(lambda checked, cid=container_id: self.pause_container(cid))
                container_menu.addAction(pause_action)
            
            # Stop action
            stop_action = QAction("🛑 Stop Container", container_menu)
            stop_action.triggered.connect(lambda checked, cid=container_id: self.stop_container(cid))
            container_menu.addAction(stop_action)
    
    def _populate_quick_launch_menu(self, menu: QMenu):
        """Populate the quick launch menu."""
        environments = self.get_environments()
        
        if not environments:
            no_envs_action = QAction("No environments available", menu)
            no_envs_action.setEnabled(False)
            menu.addAction(no_envs_action)
            return
        
        # Add environments to quick launch
        for env in environments[:10]:  # Limit to first 10 environments
            action = QAction(f"🚀 {env.name}", menu)
            action.triggered.connect(lambda checked, e=env: self.launch_environment_quick(e))
            menu.addAction(action)
        
        if len(environments) > 10:
            menu.addSeparator()
            more_action = QAction(f"... and {len(environments) - 10} more", menu)
            more_action.setEnabled(False)
            menu.addAction(more_action)
    
    def _populate_status_menu(self, menu: QMenu):
        """Populate the system status menu."""
        system_status = self.manager.get_system_status()
        resources = system_status.get("system_resources", {})
        
        # Containers overview
        total_containers = resources.get("total_containers", 0)
        running_containers = resources.get("running_containers", 0)
        
        overview_action = QAction(f"📦 {total_containers} total, {running_containers} running", menu)
        overview_action.setEnabled(False)
        menu.addAction(overview_action)
        
        # Resource usage
        total_memory = resources.get("total_memory_mb", 0)
        total_cpu = resources.get("total_cpu_percent", 0)
        
        memory_action = QAction(f"💾 Memory: {total_memory:.1f} MB", menu)
        memory_action.setEnabled(False)
        menu.addAction(memory_action)
        
        cpu_action = QAction(f"⚡ CPU: {total_cpu:.1f}%", menu)
        cpu_action.setEnabled(False)
        menu.addAction(cpu_action)
        
        # Active desktops
        active_desktops = resources.get("active_desktops", [])
        if active_desktops:
            desktop_str = ", ".join([f"#{d}" for d in sorted(active_desktops)])
            desktop_action = QAction(f"🖥️ Desktops: {desktop_str}", menu)
        else:
            desktop_action = QAction("🖥️ No active desktops", menu)
        
        desktop_action.setEnabled(False)
        menu.addAction(desktop_action)
    
    def _update_tray_menu(self):
        """Update the tray menu with current information."""
        if self.tray_menu:
            self._update_containers_menu()
            self._populate_status_menu(self.tray_menu.children()[-3])  # Status menu
    
    def _on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Show dashboard on double-click
            self.show_dashboard_requested.emit()
    
    # ======================================
    # MULTI-ENVIRONMENT OPERATIONS
    # ======================================
    
    async def launch_environment_async(self, environment: Environment, 
                                     container_id: Optional[str] = None,
                                     switch_to: bool = True) -> str:
        """Launch an environment in a new container."""
        try:
            container_id = await self.manager.start_environment_container(
                environment=environment,
                container_id=container_id,
                switch_to=switch_to
            )
            
            print(f"✅ Environment '{environment.name}' launched in container '{container_id}'")
            return container_id
            
        except Exception as e:
            print(f"❌ Failed to launch environment '{environment.name}': {e}")
            raise e
    
    def launch_environment_quick(self, environment: Environment):
        """Quick launch an environment from tray menu."""
        def launch_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                container_id = loop.run_until_complete(
                    self.launch_environment_async(environment, switch_to=True)
                )
                print(f"🚀 Quick launched: {environment.name} → {container_id}")
            except Exception as e:
                print(f"❌ Quick launch failed: {e}")
            finally:
                loop.close()
        
        thread = threading.Thread(target=launch_async, daemon=True)
        thread.start()
    
    def launch_all_environments(self):
        """Launch all environments concurrently."""
        environments = self.get_environments()
        
        if not environments:
            print("⚠️  No environments to launch")
            return
        
        # Check if we can launch all environments
        if len(environments) > self.manager.max_concurrent_containers:
            reply = QMessageBox.question(
                None, "Too Many Environments",
                f"You have {len(environments)} environments but can only run "
                f"{self.manager.max_concurrent_containers} concurrently.\n\n"
                f"Launch the first {self.manager.max_concurrent_containers}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                return
            
            environments = environments[:self.manager.max_concurrent_containers]
        
        # Add all environments to launcher queue
        container_ids = self.launcher.add_multiple_environments(
            environments, 
            switch_to_last=True, 
            launch_mode=LaunchMode.CONCURRENT
        )
        
        # Launch the queue
        def launch_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                results = loop.run_until_complete(
                    self.launcher.launch_all_queued(LaunchMode.CONCURRENT)
                )
                successful = len([r for r in results if r.success])
                print(f"🎉 Batch launch complete: {successful}/{len(results)} successful")
            except Exception as e:
                print(f"❌ Batch launch failed: {e}")
            finally:
                loop.close()
        
        thread = threading.Thread(target=launch_async, daemon=True)
        thread.start()
        
        print(f"🚀 Starting batch launch of {len(environments)} environments...")
    
    def switch_to_container(self, container_id: str):
        """Switch to a specific container."""
        def switch_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success = loop.run_until_complete(self.manager.switch_to_container(container_id))
                if success:
                    print(f"🔄 Switched to container: {container_id}")
                else:
                    print(f"❌ Failed to switch to container: {container_id}")
            except Exception as e:
                print(f"❌ Error switching to container: {e}")
            finally:
                loop.close()
        
        thread = threading.Thread(target=switch_async, daemon=True)
        thread.start()
    
    def stop_container(self, container_id: str):
        """Stop a specific container."""
        def stop_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success = loop.run_until_complete(self.manager.stop_environment_container(container_id))
                if success:
                    print(f"🛑 Stopped container: {container_id}")
                else:
                    print(f"❌ Failed to stop container: {container_id}")
            except Exception as e:
                print(f"❌ Error stopping container: {e}")
            finally:
                loop.close()
        
        thread = threading.Thread(target=stop_async, daemon=True)
        thread.start()
    
    def pause_container(self, container_id: str):
        """Pause a specific container."""
        def pause_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success = loop.run_until_complete(self.manager.pause_container(container_id))
                if success:
                    print(f"⏸️ Paused container: {container_id}")
                else:
                    print(f"❌ Failed to pause container: {container_id}")
            except Exception as e:
                print(f"❌ Error pausing container: {e}")
            finally:
                loop.close()
        
        thread = threading.Thread(target=pause_async, daemon=True)
        thread.start()
    
    def stop_all_containers(self):
        """Stop all running containers."""
        containers = self.manager.get_all_containers()
        
        if not containers:
            print("⚠️  No containers to stop")
            return
        
        reply = QMessageBox.question(
            None, "Stop All Containers",
            f"Stop all {len(containers)} containers?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            def stop_all_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    count = loop.run_until_complete(self.manager.stop_all_containers())
                    print(f"🛑 Stopped {count} containers")
                except Exception as e:
                    print(f"❌ Error stopping all containers: {e}")
                finally:
                    loop.close()
            
            thread = threading.Thread(target=stop_all_async, daemon=True)
            thread.start()
    
    # ======================================
    # LEGACY COMPATIBILITY METHODS
    # ======================================
    
    def is_first_run(self) -> bool:
        """Check if this is the first run."""
        return self.config_manager.is_first_run()
    
    def mark_first_run_complete(self):
        """Mark first run as completed."""
        self.config_manager.mark_first_run_complete()
    
    def get_config(self) -> dict:
        """Get application configuration."""
        return self.config_manager.get_config()
    
    def update_config(self, **kwargs):
        """Update configuration."""
        self.config_manager.update_config(**kwargs)
    
    def get_environments(self) -> List[Environment]:
        """Get all environments."""
        return self.config_manager.get_environments()
    
    def add_environment(self, environment: Environment) -> bool:
        """Add a new environment."""
        success = self.config_manager.add_environment(environment)
        if success:
            self._update_tray_menu()
        return success
    
    def update_environment(self, environment: Environment) -> bool:
        """Update an existing environment."""
        success = self.config_manager.update_environment(environment)
        if success:
            self._update_tray_menu()
        return success
    
    def delete_environment(self, environment_id: str) -> bool:
        """Delete an environment."""
        success = self.config_manager.delete_environment(environment_id)
        if success:
            self._update_tray_menu()
        return success
    
    def get_environment_by_id(self, environment_id: str) -> Optional[Environment]:
        """Get environment by ID."""
        return self.config_manager.get_environment_by_id(environment_id)
    
    def get_environment_by_name(self, name: str) -> Optional[Environment]:
        """Get environment by name."""
        return self.config_manager.get_environment_by_name(name)
    
    def launch_environment(self, environment: Environment) -> bool:
        """Launch an environment (legacy compatibility)."""
        self.launch_environment_quick(environment)
        return True  # Always return True for compatibility
    
    def is_launching(self) -> bool:
        """Check if currently launching."""
        return self.launcher.is_launching
    
    def setup_system_integration(self):
        """Set up Windows system integration."""
        config = self.get_config()
        
        # Auto-start integration
        if config.get("auto_start", True):
            if not self.system_integration.is_in_startup():
                self.system_integration.add_to_startup()
        
        # Desktop shortcut (only create once)
        if self.is_first_run():
            self.system_integration.create_desktop_shortcut()
    
    def toggle_auto_start(self, enabled: bool):
        """Toggle auto-start functionality."""
        if enabled:
            success = self.system_integration.add_to_startup()
        else:
            success = self.system_integration.remove_from_startup()
        
        if success:
            self.update_config(auto_start=enabled)
        
        return success
    
    # ======================================
    # EVENT HANDLERS
    # ======================================
    
    def _on_container_started(self, container_id: str):
        """Handle container started event."""
        self.container_started.emit(container_id)
        self._update_tray_menu()
        
        if self.tray_icon:
            containers = self.manager.get_all_containers()
            container_info = containers.get(container_id, {})
            env_name = container_info.get("environment_name", "Unknown")
            
            self.tray_icon.showMessage(
                "🚀 Container Started",
                f"Environment '{env_name}' is now running!",
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )
    
    def _on_container_stopped(self, container_id: str):
        """Handle container stopped event."""
        self.container_stopped.emit(container_id)
        self._update_tray_menu()
        
        if self.tray_icon:
            self.tray_icon.showMessage(
                "🛑 Container Stopped",
                f"Container '{container_id}' has been stopped",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
    
    def _on_container_switched(self, container_id: str):
        """Handle container switched event."""
        self.container_switched.emit(container_id)
        
        if self.tray_icon:
            containers = self.manager.get_all_containers()
            container_info = containers.get(container_id, {})
            env_name = container_info.get("environment_name", "Unknown")
            desktop_idx = container_info.get("desktop_index", -1)
            
            self.tray_icon.showMessage(
                "🔄 Switched Environment",
                f"Now on {env_name} (Desktop #{desktop_idx})",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
    
    def _on_resources_updated(self, resources: Dict):
        """Handle system resources update."""
        self.system_resources_updated.emit(resources)
        
        # Update tray tooltip with resource info
        if self.tray_icon:
            running_containers = resources.get("running_containers", 0)
            total_memory = resources.get("total_memory_mb", 0)
            
            tooltip = f"🎮 EnvStarter Multi-Environment\\n"
            tooltip += f"📦 {running_containers} containers running\\n"
            tooltip += f"💾 {total_memory:.0f} MB memory in use"
            
            self.tray_icon.setToolTip(tooltip)
    
    def _on_max_containers_reached(self, max_limit: int):
        """Handle max containers reached event."""
        if self.tray_icon:
            self.tray_icon.showMessage(
                "⚠️ Container Limit Reached",
                f"Maximum of {max_limit} concurrent containers reached!",
                QSystemTrayIcon.MessageIcon.Warning,
                5000
            )
    
    def _on_launch_started(self, container_id: str, environment_name: str):
        """Handle launch started event."""
        if self.tray_icon:
            self.tray_icon.showMessage(
                "🚀 Launching Environment",
                f"Starting {environment_name}...",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
    
    def _on_launch_completed(self, container_id: str, success: bool):
        """Handle launch completed event.""" 
        # Container started/stopped events will handle notifications
        pass
    
    def _on_all_launches_completed(self, results: List[Dict]):
        """Handle all launches completed event."""
        successful = len([r for r in results if r.get("success", False)])
        total = len(results)
        
        if self.tray_icon:
            self.tray_icon.showMessage(
                "🎉 Batch Launch Complete",
                f"Started {successful}/{total} environments successfully!",
                QSystemTrayIcon.MessageIcon.Information,
                4000
            )
    
    def quit_application(self):
        """Quit the application with proper cleanup."""
        print("🛑 Shutting down Enhanced App Controller...")
        
        # Stop tray updates
        self.tray_update_timer.stop()
        
        # Hide tray icon
        if self.tray_icon:
            self.tray_icon.hide()
        
        # Shutdown multi-environment system
        shutdown_multi_environment_manager()
        
        # Emit quit signal
        self.quit_requested.emit()
        
        # Quit application
        QApplication.quit()
        
        print("✅ Enhanced App Controller shutdown complete")