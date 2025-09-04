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

from envstarter.core.app_controller import AppController
from envstarter.gui.environment_selector import EnvironmentSelector
from envstarter.utils.system_integration import SystemIntegration


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
        self.system_integration = SystemIntegration()
        
        self._setup_application()
    
    def _setup_application(self):
        """Initialize the application components."""
        # Set up system tray if available
        if self.system_integration.is_tray_available():
            self.controller.setup_system_tray()
        
        # Check if this is first run
        if self.controller.is_first_run():
            self._show_environment_selector()
        else:
            # Start in system tray
            pass
    
    def _show_environment_selector(self):
        """Show the main environment selector window."""
        if not self.environment_selector:
            self.environment_selector = EnvironmentSelector(self.controller)
        
        self.environment_selector.show()
        self.environment_selector.raise_()
        self.environment_selector.activateWindow()
    
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