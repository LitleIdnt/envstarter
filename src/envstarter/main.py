#!/usr/bin/env python3
"""
EnvStarter Main Application
Entry point for the EnvStarter application.
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon

from src.envstarter.core.app_controller import AppController
from src.envstarter.gui.environment_selector import EnvironmentSelector
from src.envstarter.gui.settings_dialog import SettingsDialog
from src.envstarter.utils.system_integration import SystemIntegration


class EnvStarterApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Set application properties
        self.app.setApplicationName("EnvStarter")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("EnvStarter")
        
        # Initialize components
        self.controller = AppController()
        self.environment_selector = None
        self.settings_dialog = None
        self.system_integration = SystemIntegration()
        
        self._setup_application()
        self._setup_connections()
    
    def _setup_application(self):
        """Initialize the application components."""
        # Set up system tray if available
        if self.system_integration.is_tray_available():
            self.controller.setup_system_tray()
        
        # Set up system integration
        self.controller.setup_system_integration()
        
        # Check if this is first run
        if self.controller.is_first_run():
            self._show_environment_selector()
            self.controller.mark_first_run_complete()
        else:
            # Start in system tray
            pass
    
    def _show_environment_selector(self):
        """Show the main environment selector window."""
        if not self.environment_selector:
            self.environment_selector = EnvironmentSelector(self.controller)
            self.environment_selector.settings_requested.connect(self._show_settings_dialog)
        
        self.environment_selector.show()
        self.environment_selector.raise_()
        self.environment_selector.activateWindow()
    
    def _setup_connections(self):
        """Set up signal connections."""
        # Connect controller signals
        self.controller.settings_requested.connect(self._show_settings_dialog)
        self.controller.show_selector_requested.connect(self._show_environment_selector)
        self.controller.quit_requested.connect(self.app.quit)
    
    def _show_settings_dialog(self):
        """Show the settings dialog."""
        if not self.settings_dialog:
            self.settings_dialog = SettingsDialog(self.controller)
            self.settings_dialog.environment_changed.connect(self._on_environments_changed)
        
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()
    
    def _on_environments_changed(self):
        """Handle environment changes."""
        if self.environment_selector:
            self.environment_selector.load_environments()
        
        # Refresh tray menu
        if self.controller.tray_icon:
            self.controller.refresh_tray_menu()
    
    def run(self):
        """Start the application event loop."""
        return self.app.exec()


def main():
    """Main entry point."""
    try:
        app = EnvStarterApp()
        sys.exit(app.run())
    except Exception as e:
        print(f"Error starting EnvStarter: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()