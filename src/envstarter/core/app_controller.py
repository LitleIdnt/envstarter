"""
Main application controller for EnvStarter.
"""

import sys
from typing import Optional, List
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject, pyqtSignal

from src.envstarter.core.storage import ConfigManager
from src.envstarter.core.launcher import EnvironmentLauncher
from src.envstarter.core.models import Environment
from src.envstarter.utils.system_integration import SystemIntegration
from src.envstarter.utils.icons import get_tray_icon


class AppController(QObject):
    """Main application controller."""
    
    environment_launched = pyqtSignal(str)  # environment name
    settings_requested = pyqtSignal()
    show_selector_requested = pyqtSignal()
    quit_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.launcher = EnvironmentLauncher()
        self.system_integration = SystemIntegration()
        self.tray_icon = None
        
        # Connect launcher signals
        self.launcher.launch_started.connect(self._on_launch_started)
        self.launcher.launch_completed.connect(self._on_launch_completed)
        self.launcher.error_occurred.connect(self._on_launch_error)
    
    def setup_system_tray(self):
        """Set up the system tray icon and menu."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return False
        
        self.tray_icon = QSystemTrayIcon()
        
        # Create tray icon
        icon = get_tray_icon()
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("EnvStarter")
        
        # Create context menu
        menu = QMenu()
        
        # Show main window
        show_action = QAction("Show EnvStarter", menu)
        show_action.triggered.connect(self.show_selector_requested.emit)
        menu.addAction(show_action)
        
        menu.addSeparator()
        
        # Quick environment selection
        environments = self.get_environments()
        if environments:
            env_menu = menu.addMenu("Launch Environment")
            for env in environments:
                action = QAction(env.name, menu)
                action.triggered.connect(lambda checked, e=env: self.launch_environment(e))
                env_menu.addAction(action)
            
            menu.addSeparator()
        
        # Stop current environment
        stop_action = QAction("Stop Current", menu)
        stop_action.triggered.connect(self.stop_current_environment)
        menu.addAction(stop_action)
        
        menu.addSeparator()
        
        # Settings
        settings_action = QAction("Settings", menu)
        settings_action.triggered.connect(self.settings_requested.emit)
        menu.addAction(settings_action)
        
        # Exit
        exit_action = QAction("Exit", menu)
        exit_action.triggered.connect(self.quit_application)
        menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()
        
        # Double-click to show environment selector
        self.tray_icon.activated.connect(self._on_tray_activated)
        
        return True
    
    def _on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Show environment selector
            self.show_selector_requested.emit()
    
    def refresh_tray_menu(self):
        """Refresh the tray icon menu with current environments."""
        if self.tray_icon:
            self.setup_system_tray()
    
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
            self.refresh_tray_menu()
        return success
    
    def update_environment(self, environment: Environment) -> bool:
        """Update an existing environment."""
        success = self.config_manager.update_environment(environment)
        if success:
            self.refresh_tray_menu()
        return success
    
    def delete_environment(self, environment_id: str) -> bool:
        """Delete an environment."""
        success = self.config_manager.delete_environment(environment_id)
        if success:
            self.refresh_tray_menu()
        return success
    
    def get_environment_by_id(self, environment_id: str) -> Optional[Environment]:
        """Get environment by ID."""
        return self.config_manager.get_environment_by_id(environment_id)
    
    def get_environment_by_name(self, name: str) -> Optional[Environment]:
        """Get environment by name."""
        return self.config_manager.get_environment_by_name(name)
    
    def launch_environment(self, environment: Environment):
        """Launch an environment."""
        if self.launcher.is_launching():
            return False
        
        self.launcher.launch_environment(environment)
        
        # Update last selected environment
        self.update_config(last_selected_environment=environment.id)
        return True
    
    def stop_current_environment(self):
        """Stop the currently launching environment."""
        self.launcher.stop_current_environment()
    
    def is_launching(self) -> bool:
        """Check if currently launching."""
        return self.launcher.is_launching()
    
    def _on_launch_started(self, environment_name: str):
        """Handle launch started."""
        if self.tray_icon:
            self.tray_icon.showMessage(
                "EnvStarter",
                f"Launching {environment_name}...",
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )
    
    def _on_launch_completed(self, environment_name: str, success: bool):
        """Handle launch completed."""
        if self.tray_icon:
            if success:
                self.tray_icon.showMessage(
                    "EnvStarter",
                    f"{environment_name} launched successfully!",
                    QSystemTrayIcon.MessageIcon.Information,
                    3000
                )
            else:
                self.tray_icon.showMessage(
                    "EnvStarter",
                    f"Failed to launch {environment_name}",
                    QSystemTrayIcon.MessageIcon.Warning,
                    5000
                )
        
        self.environment_launched.emit(environment_name)
    
    def _on_launch_error(self, error_message: str):
        """Handle launch error."""
        if self.tray_icon:
            self.tray_icon.showMessage(
                "EnvStarter",
                f"Error: {error_message}",
                QSystemTrayIcon.MessageIcon.Critical,
                5000
            )
    
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
    
    def quit_application(self):
        """Quit the application."""
        if self.launcher.is_launching():
            self.launcher.stop_current_environment()
        
        if self.tray_icon:
            self.tray_icon.hide()
        
        self.quit_requested.emit()
        QApplication.quit()