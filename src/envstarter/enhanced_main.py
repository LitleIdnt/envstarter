#!/usr/bin/env python3
"""
🚀 ENHANCED ENVSTARTER MAIN APPLICATION 🚀
The revolutionary multi-environment system entry point!

This is the new main application that supports:
- Multiple concurrent environments (like VMs)
- Advanced container management
- Multi-environment dashboard
- VM-like isolation and switching
"""

import sys
import os
import asyncio
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.envstarter.core.enhanced_app_controller import EnhancedAppController
from src.envstarter.gui.environment_selector import EnvironmentSelector
from src.envstarter.gui.enhanced_settings_dialog import EnhancedSettingsDialog
from src.envstarter.gui.multi_environment_dashboard import MultiEnvironmentDashboard
from src.envstarter.utils.system_integration import SystemIntegration


class EnhancedEnvStarterApp:
    """
    🎮 THE ULTIMATE ENHANCED ENVSTARTER APPLICATION!
    
    Features:
    - Multi-environment container management
    - Concurrent environment launching
    - VM-like isolation and switching
    - Advanced dashboard interface
    - Enhanced system tray integration
    """
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Set application properties
        self.app.setApplicationName("EnvStarter Multi-Environment")
        self.app.setApplicationVersion("2.0.0")
        self.app.setOrganizationName("EnvStarter Enhanced")
        
        # Initialize enhanced components
        self.controller = EnhancedAppController()
        self.environment_selector = None
        self.settings_dialog = None
        self.dashboard = None
        self.system_integration = SystemIntegration()
        
        self._setup_application()
        self._setup_connections()
        
        print("🎮 Enhanced EnvStarter Application initialized!")
        print("   ✅ Multi-environment support enabled")
        print("   ✅ Container management ready")
        print("   ✅ Advanced dashboard available")
    
    def _setup_application(self):
        """Initialize the enhanced application components."""
        print("🚀 Setting up enhanced EnvStarter...")
        
        # Set up enhanced system tray
        if self.system_integration.is_tray_available():
            success = self.controller.setup_system_tray()
            if success:
                print("   ✅ Enhanced system tray initialized")
            else:
                print("   ⚠️  System tray initialization failed")
        else:
            print("   ⚠️  System tray not available")
        
        # Set up system integration
        self.controller.setup_system_integration()
        print("   ✅ System integration configured")
        
        # Check if this is first run
        if self.controller.is_first_run():
            self._show_first_run_experience()
            self.controller.mark_first_run_complete()
        else:
            # Enhanced mode: Show dashboard if no environments running
            containers = self.controller.manager.get_all_containers()
            if not containers:
                print("   💡 No containers running, showing dashboard")
                self._show_dashboard()
            else:
                print(f"   📦 {len(containers)} containers already running")
    
    def _show_first_run_experience(self):
        """Show the first run experience."""
        print("🎉 Welcome to Enhanced EnvStarter!")
        
        # Show welcome message
        msg = QMessageBox()
        msg.setWindowTitle("🎮 Welcome to Enhanced EnvStarter!")
        msg.setText("""
🚀 <b>Enhanced EnvStarter 2.0</b> is ready!

<b>🆕 New Features:</b>
• 📦 Run multiple environments simultaneously
• 🔄 Switch between environments like VMs
• 📊 Real-time container monitoring
• ⚡ Concurrent batch launching
• 🎮 Advanced management dashboard

<b>🎯 Choose your experience:</b>
        """)
        
        dashboard_btn = msg.addButton("🎮 Open Dashboard", QMessageBox.ButtonRole.AcceptRole)
        selector_btn = msg.addButton("🎯 Environment Selector", QMessageBox.ButtonRole.ActionRole)
        
        msg.setDefaultButton(dashboard_btn)
        msg.exec()
        
        if msg.clickedButton() == dashboard_btn:
            self._show_dashboard()
        else:
            self._show_environment_selector()
    
    def _show_dashboard(self):
        """Show the multi-environment dashboard."""
        print("🎮 Opening Multi-Environment Dashboard...")
        
        if not self.dashboard:
            self.dashboard = MultiEnvironmentDashboard()
        
        self.dashboard.show()
        self.dashboard.raise_()
        self.dashboard.activateWindow()
    
    def _show_environment_selector(self):
        """Show the traditional environment selector."""
        print("🎯 Opening Environment Selector...")
        
        if not self.environment_selector:
            self.environment_selector = EnvironmentSelector(self.controller)
            self.environment_selector.settings_requested.connect(self._show_settings_dialog)
        
        self.environment_selector.show()
        self.environment_selector.raise_()
        self.environment_selector.activateWindow()
    
    def _setup_connections(self):
        """Set up enhanced signal connections.""" 
        # Enhanced controller signals
        self.controller.settings_requested.connect(self._show_settings_dialog)
        self.controller.show_selector_requested.connect(self._show_environment_selector)
        self.controller.show_dashboard_requested.connect(self._show_dashboard)
        self.controller.quit_requested.connect(self.app.quit)
        
        # Multi-environment signals
        self.controller.container_started.connect(self._on_container_started)
        self.controller.container_stopped.connect(self._on_container_stopped)
        self.controller.container_switched.connect(self._on_container_switched)
        self.controller.system_resources_updated.connect(self._on_resources_updated)
    
    def _show_settings_dialog(self):
        """Show the settings dialog."""
        print("⚙️  Opening Settings Dialog...")
        
        if not self.settings_dialog:
            self.settings_dialog = EnhancedSettingsDialog(self.controller)
            self.settings_dialog.environment_changed.connect(self._on_environments_changed)
        
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()
    
    def _on_environments_changed(self):
        """Handle environment changes."""
        print("🔄 Environments changed, refreshing UI...")
        
        # Refresh environment selector
        if self.environment_selector:
            self.environment_selector.load_environments()
        
        # Refresh dashboard
        if self.dashboard:
            self.dashboard.refresh_containers()
        
        print("✅ UI refreshed")
    
    def _on_container_started(self, container_id: str):
        """Handle container started event."""
        print(f"✅ Container started event: {container_id}")
        
        # If dashboard is open, it will auto-refresh
        # If selector is open and no containers were running, show dashboard
        if self.environment_selector and self.environment_selector.isVisible():
            containers = self.controller.manager.get_all_containers()
            if len(containers) == 1:  # First container started
                print("💡 First container started, showing dashboard")
                self._show_dashboard()
    
    def _on_container_stopped(self, container_id: str):
        """Handle container stopped event."""
        print(f"🛑 Container stopped event: {container_id}")
        
        # Check if this was the last container
        containers = self.controller.manager.get_all_containers()
        if not containers:
            print("💡 No containers running")
    
    def _on_container_switched(self, container_id: str):
        """Handle container switched event."""
        print(f"🔄 Container switched event: {container_id}")
    
    def _on_resources_updated(self, resources: dict):
        """Handle system resources update."""
        # Dashboard will handle this automatically
        pass
    
    def run(self):
        """Start the enhanced application event loop."""
        print("🚀 Starting Enhanced EnvStarter application loop...")
        
        # Show startup status in tray
        running_containers = len(self.controller.manager.get_all_containers())
        print(f"📊 Startup status: {running_containers} containers running")
        
        return self.app.exec()


def main():
    """Enhanced main entry point."""
    print("=" * 60)
    print("🎮 ENHANCED ENVSTARTER 2.0 - MULTI-ENVIRONMENT SYSTEM")
    print("=" * 60)
    print()
    
    try:
        # Check system requirements
        if sys.version_info < (3, 8):
            print("❌ Error: Python 3.8 or higher required")
            print(f"   Current version: {sys.version}")
            sys.exit(1)
        
        # Check PyQt6 availability
        try:
            from PyQt6.QtWidgets import QApplication
            print("✅ PyQt6 available")
        except ImportError:
            print("❌ Error: PyQt6 not available")
            print("   Install with: pip install PyQt6")
            sys.exit(1)
        
        # Check Windows (for full features)
        if os.name != 'nt':
            print("⚠️  Warning: Enhanced features designed for Windows")
            print("   Some features may not work on other platforms")
        else:
            print("✅ Windows platform detected")
        
        # Initialize and run enhanced application
        app = EnhancedEnvStarterApp()
        exit_code = app.run()
        
        print()
        print("✅ Enhanced EnvStarter shutdown complete")
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error starting Enhanced EnvStarter: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()