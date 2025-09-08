"""
🎯 ENVIRONMENT INDICATOR SYSTEM 🎯
Visual indicators to show which environment is running and which apps belong to it!
"""

import sys
import ctypes
from ctypes import wintypes
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                             QFrame, QPushButton, QApplication)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint, QRect
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush
from typing import Dict, List, Optional, Tuple
import psutil
from datetime import datetime


class EnvironmentStatusOverlay(QWidget):
    """
    🎯 ENVIRONMENT STATUS OVERLAY
    
    Shows environment status in the corner of the screen with:
    - Environment name and status
    - Running applications list
    - CPU/Memory usage
    - Quick actions
    """
    
    switch_requested = pyqtSignal(str)  # environment_name
    stop_requested = pyqtSignal(str)    # environment_name
    
    def __init__(self, environment_name: str, container_id: str):
        super().__init__()
        self.environment_name = environment_name
        self.container_id = container_id
        self.applications = []
        self.is_minimized = False
        
        self.setup_ui()
        self.setup_positioning()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(2000)  # Update every 2 seconds
    
    def setup_ui(self):
        """Set up the overlay UI."""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Apply EnvStarter icon
        from src.envstarter.utils.icons import apply_icon_to_widget
        apply_icon_to_widget(self)
        
        # Apply modern styling
        from src.envstarter.utils.theme_manager import get_theme_manager
        theme = get_theme_manager()
        
        bg_color = theme.get_color("surface")
        text_color = theme.get_color("text_primary")
        primary_color = theme.get_color("primary")
        border_color = theme.get_color("border")
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                color: {text_color};
                border: 2px solid {primary_color};
                border-radius: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QLabel {{
                background: transparent;
                padding: 2px;
            }}
            QPushButton {{
                background-color: {primary_color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 10px;
                font-weight: 600;
                min-height: 20px;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)
        
        # Header with environment name and minimize button
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        # Environment name
        self.env_label = QLabel(f"🎯 {self.environment_name}")
        env_font = QFont()
        env_font.setBold(True)
        env_font.setPointSize(11)
        self.env_label.setFont(env_font)
        header_layout.addWidget(self.env_label)
        
        header_layout.addStretch()
        
        # Minimize/Maximize button
        self.toggle_btn = QPushButton("−")
        self.toggle_btn.setMaximumSize(20, 20)
        self.toggle_btn.clicked.connect(self.toggle_minimize)
        header_layout.addWidget(self.toggle_btn)
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setMaximumSize(20, 20)
        close_btn.clicked.connect(self.stop_environment)
        header_layout.addWidget(close_btn)
        
        layout.addLayout(header_layout)
        
        # Status info
        self.status_label = QLabel("🟢 Running")
        self.status_label.setStyleSheet("color: #3fb950; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Applications list (collapsible)
        self.apps_frame = QFrame()
        self.apps_layout = QVBoxLayout()
        self.apps_layout.setContentsMargins(0, 0, 0, 0)
        self.apps_layout.setSpacing(2)
        
        # Apps header
        apps_header = QLabel("📱 Applications:")
        apps_header_font = QFont()
        apps_header_font.setBold(True)
        apps_header_font.setPointSize(9)
        apps_header.setFont(apps_header_font)
        self.apps_layout.addWidget(apps_header)
        
        # Apps list container
        self.apps_list_widget = QWidget()
        self.apps_list_layout = QVBoxLayout()
        self.apps_list_layout.setContentsMargins(8, 0, 0, 0)
        self.apps_list_layout.setSpacing(1)
        self.apps_list_widget.setLayout(self.apps_list_layout)
        self.apps_layout.addWidget(self.apps_list_widget)
        
        self.apps_frame.setLayout(self.apps_layout)
        layout.addWidget(self.apps_frame)
        
        # Resource usage
        self.resource_label = QLabel("💾 Memory: 0MB | ⚡ CPU: 0%")
        resource_font = QFont()
        resource_font.setPointSize(8)
        self.resource_label.setFont(resource_font)
        layout.addWidget(self.resource_label)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(4)
        
        switch_btn = QPushButton("🔄 Switch")
        switch_btn.clicked.connect(self.switch_environment)
        actions_layout.addWidget(switch_btn)
        
        stop_btn = QPushButton("🛑 Stop")
        stop_btn.clicked.connect(self.stop_environment)
        actions_layout.addWidget(stop_btn)
        
        layout.addLayout(actions_layout)
        
        self.setLayout(layout)
        
        # Initial size
        self.setFixedWidth(280)
        self.adjustSize()
    
    def setup_positioning(self):
        """Position the overlay in the top-right corner."""
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        
        # Position in top-right corner with margin
        margin = 20
        x = screen_rect.width() - self.width() - margin
        y = margin
        
        self.move(x, y)
    
    def toggle_minimize(self):
        """Toggle between minimized and expanded view."""
        self.is_minimized = not self.is_minimized
        
        if self.is_minimized:
            self.apps_frame.hide()
            self.resource_label.hide()
            self.toggle_btn.setText("+")
            self.setFixedHeight(50)
        else:
            self.apps_frame.show()
            self.resource_label.show()
            self.toggle_btn.setText("−")
            self.adjustSize()
    
    def update_status(self):
        """Update the environment status."""
        try:
            # Get container info from the multi-environment manager
            from src.envstarter.core.multi_environment_manager import get_multi_environment_manager
            manager = get_multi_environment_manager()
            
            containers = manager.get_all_containers()
            container_info = containers.get(self.container_id)
            
            if not container_info:
                self.close()
                return
            
            # Update status
            state = container_info.get("state", "unknown")
            if state == "running":
                self.status_label.setText("🟢 Running")
                self.status_label.setStyleSheet("color: #3fb950; font-weight: bold;")
            elif state == "paused":
                self.status_label.setText("⏸️ Paused")
                self.status_label.setStyleSheet("color: #d29922; font-weight: bold;")
            else:
                self.status_label.setText("🔴 Stopped")
                self.status_label.setStyleSheet("color: #f85149; font-weight: bold;")
            
            # Update applications list
            self.update_applications_list(container_info)
            
            # Update resource usage
            stats = container_info.get("stats", {})
            memory_mb = stats.get("total_memory_mb", 0)
            cpu_percent = stats.get("total_cpu_percent", 0)
            process_count = stats.get("total_processes", 0)
            
            self.resource_label.setText(
                f"💾 {memory_mb:.0f}MB | ⚡ {cpu_percent:.1f}% | 📊 {process_count} apps"
            )
            
        except Exception as e:
            print(f"⚠️ Error updating environment indicator: {e}")
    
    def update_applications_list(self, container_info: Dict):
        """Update the applications list."""
        # Clear existing apps
        for i in reversed(range(self.apps_list_layout.count())):
            child = self.apps_list_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        # Add current applications
        processes = container_info.get("processes", [])
        
        if not processes:
            no_apps_label = QLabel("No applications running")
            no_apps_label.setStyleSheet("color: #6e7681; font-style: italic; font-size: 9px;")
            self.apps_list_layout.addWidget(no_apps_label)
        else:
            # Show up to 8 applications
            for process in processes[:8]:
                app_name = process.get("name", "Unknown")
                pid = process.get("pid", 0)
                memory_mb = process.get("memory_mb", 0)
                
                app_label = QLabel(f"• {app_name}")
                app_label.setStyleSheet("font-size: 9px; padding: 1px;")
                app_label.setToolTip(f"PID: {pid} | Memory: {memory_mb:.1f}MB")
                
                self.apps_list_layout.addWidget(app_label)
            
            if len(processes) > 8:
                more_label = QLabel(f"... and {len(processes) - 8} more")
                more_label.setStyleSheet("color: #6e7681; font-style: italic; font-size: 9px;")
                self.apps_list_layout.addWidget(more_label)
        
        # Adjust size if not minimized
        if not self.is_minimized:
            self.adjustSize()
    
    def switch_environment(self):
        """Switch to this environment."""
        self.switch_requested.emit(self.container_id)
    
    def stop_environment(self):
        """Stop this environment."""
        self.stop_requested.emit(self.container_id)
        self.close()
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.globalPosition().toPoint()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging."""
        if not hasattr(self, 'drag_start_position'):
            return
        
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        
        # Move the window
        distance = (event.globalPosition().toPoint() - self.drag_start_position).manhattanLength()
        if distance >= QApplication.startDragDistance():
            new_pos = self.pos() + event.globalPosition().toPoint() - self.drag_start_position
            self.move(new_pos)
            self.drag_start_position = event.globalPosition().toPoint()


class EnvironmentIndicatorManager:
    """
    🎯 ENVIRONMENT INDICATOR MANAGER
    
    Manages environment status overlays for all running containers.
    """
    
    def __init__(self):
        self.indicators: Dict[str, EnvironmentStatusOverlay] = {}
        
        # Connect to multi-environment manager
        from src.envstarter.core.multi_environment_manager import get_multi_environment_manager
        self.manager = get_multi_environment_manager()
        
        # Monitor timer
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.update_indicators)
        self.monitor_timer.start(5000)  # Check every 5 seconds
    
    def update_indicators(self):
        """Update indicators based on running containers."""
        try:
            containers = self.manager.get_all_containers()
            running_containers = {
                cid: info for cid, info in containers.items()
                if info.get("state") == "running"
            }
            
            # Remove indicators for stopped containers
            for container_id in list(self.indicators.keys()):
                if container_id not in running_containers:
                    indicator = self.indicators.pop(container_id)
                    indicator.close()
            
            # Add indicators for new containers
            for container_id, container_info in running_containers.items():
                if container_id not in self.indicators:
                    env_name = container_info.get("environment_name", "Unknown Environment")
                    
                    indicator = EnvironmentStatusOverlay(env_name, container_id)
                    indicator.switch_requested.connect(self._handle_switch_request)
                    indicator.stop_requested.connect(self._handle_stop_request)
                    
                    # Position indicators vertically
                    self._position_indicator(indicator, len(self.indicators))
                    
                    indicator.show()
                    self.indicators[container_id] = indicator
            
        except Exception as e:
            print(f"⚠️ Error updating environment indicators: {e}")
    
    def _position_indicator(self, indicator: EnvironmentStatusOverlay, index: int):
        """Position indicator based on its index."""
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        
        margin = 20
        indicator_height = 200  # Approximate height
        spacing = 10
        
        x = screen_rect.width() - indicator.width() - margin
        y = margin + (indicator_height + spacing) * index
        
        # Wrap to left side if too far down
        if y + indicator_height > screen_rect.height() - margin:
            x = margin
            y = margin + (indicator_height + spacing) * (index % 4)
        
        indicator.move(x, y)
    
    def _handle_switch_request(self, container_id: str):
        """Handle switch request."""
        try:
            # Use enhanced app controller to switch
            from src.envstarter.core.enhanced_app_controller import EnhancedAppController
            controller = EnhancedAppController()
            controller.switch_to_container(container_id)
        except Exception as e:
            print(f"⚠️ Error switching to container: {e}")
    
    def _handle_stop_request(self, container_id: str):
        """Handle stop request."""
        try:
            # Use enhanced app controller to stop
            from src.envstarter.core.enhanced_app_controller import EnhancedAppController
            controller = EnhancedAppController()
            controller.stop_container(container_id)
        except Exception as e:
            print(f"⚠️ Error stopping container: {e}")
    
    def show_all_indicators(self):
        """Show all environment indicators."""
        for indicator in self.indicators.values():
            indicator.show()
    
    def hide_all_indicators(self):
        """Hide all environment indicators."""
        for indicator in self.indicators.values():
            indicator.hide()
    
    def close_all_indicators(self):
        """Close all environment indicators."""
        for indicator in list(self.indicators.values()):
            indicator.close()
        self.indicators.clear()


# Global indicator manager instance
_indicator_manager = None

def get_environment_indicator_manager() -> EnvironmentIndicatorManager:
    """Get the global environment indicator manager."""
    global _indicator_manager
    if _indicator_manager is None:
        _indicator_manager = EnvironmentIndicatorManager()
    return _indicator_manager