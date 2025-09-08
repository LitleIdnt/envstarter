"""
🎯 ENVIRONMENT STATUS WIDGET 🎯
Shows running environment info in application headers!
"""

from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton, 
                             QFrame, QVBoxLayout, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor
from typing import Dict, List


class EnvironmentStatusWidget(QWidget):
    """
    🎯 ENVIRONMENT STATUS WIDGET
    
    Shows running environments in application headers with:
    - Environment names and status
    - Quick switching
    - Visual indicators
    """
    
    switch_requested = pyqtSignal(str)  # container_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.containers_info = {}
        self.setup_ui()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(2000)  # Update every 2 seconds
    
    def setup_ui(self):
        """Set up the status widget UI."""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Status indicator
        self.status_frame = QFrame()
        self.status_layout = QHBoxLayout()
        self.status_layout.setContentsMargins(8, 4, 8, 4)
        self.status_layout.setSpacing(6)
        
        # Apply theme-aware styling
        from src.envstarter.utils.theme_manager import get_theme_manager
        theme = get_theme_manager()
        
        bg_color = theme.get_color("surface")
        text_color = theme.get_color("text_primary")
        border_color = theme.get_color("border")
        primary_color = theme.get_color("primary")
        
        self.status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 2px;
            }}
            QLabel {{
                background: transparent;
                color: {text_color};
                font-size: 11px;
                font-weight: 600;
                padding: 2px 4px;
            }}
            QPushButton {{
                background-color: {primary_color};
                color: white;
                border: none;
                border-radius: 3px;
                padding: 2px 6px;
                font-size: 9px;
                font-weight: 600;
                min-height: 18px;
                max-height: 18px;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)
        
        # Default message
        self.default_label = QLabel("No environments running")
        self.default_label.setStyleSheet(f"color: {theme.get_color('text_muted')}; font-style: italic;")
        self.status_layout.addWidget(self.default_label)
        
        self.status_frame.setLayout(self.status_layout)
        layout.addWidget(self.status_frame)
        
        layout.addStretch()
        self.setLayout(layout)
        
        self.setMaximumHeight(32)
    
    def update_status(self):
        """Update the environment status display."""
        try:
            from src.envstarter.core.multi_environment_manager import get_multi_environment_manager
            manager = get_multi_environment_manager()
            
            containers = manager.get_all_containers()
            running_containers = {
                cid: info for cid, info in containers.items()
                if info.get("state") == "running"
            }
            
            # Clear existing widgets
            for i in reversed(range(self.status_layout.count())):
                child = self.status_layout.itemAt(i).widget()
                if child:
                    child.deleteLater()
            
            if not running_containers:
                # No environments running
                self.default_label = QLabel("No environments running")
                from src.envstarter.utils.theme_manager import get_theme_manager
                theme = get_theme_manager()
                self.default_label.setStyleSheet(f"color: {theme.get_color('text_muted')}; font-style: italic;")
                self.status_layout.addWidget(self.default_label)
            else:
                # Show running environments
                self.status_layout.addWidget(QLabel("🎯 Active:"))
                
                for i, (container_id, info) in enumerate(running_containers.items()):
                    if i > 0:
                        # Add separator
                        separator = QLabel("|")
                        from src.envstarter.utils.theme_manager import get_theme_manager
                        theme = get_theme_manager()
                        separator.setStyleSheet(f"color: {theme.get_color('border')};")
                        self.status_layout.addWidget(separator)
                    
                    # Environment button
                    env_name = info.get("environment_name", "Unknown")
                    stats = info.get("stats", {})
                    process_count = stats.get("total_processes", 0)
                    memory_mb = stats.get("total_memory_mb", 0)
                    
                    # Create clickable environment button
                    env_btn = QPushButton(f"{env_name} ({process_count} apps)")
                    env_btn.setToolTip(f"Environment: {env_name}\n"
                                     f"Applications: {process_count}\n"
                                     f"Memory: {memory_mb:.0f}MB\n"
                                     f"Click to switch")
                    
                    # Connect switch signal
                    env_btn.clicked.connect(lambda checked, cid=container_id: self.switch_requested.emit(cid))
                    
                    self.status_layout.addWidget(env_btn)
                    
                    # Limit to 4 environments to avoid overcrowding
                    if i >= 3:
                        if len(running_containers) > 4:
                            more_label = QLabel(f"... +{len(running_containers) - 4} more")
                            from src.envstarter.utils.theme_manager import get_theme_manager
                            theme = get_theme_manager()
                            more_label.setStyleSheet(f"color: {theme.get_color('text_muted')}; font-style: italic;")
                            self.status_layout.addWidget(more_label)
                        break
            
        except Exception as e:
            print(f"⚠️ Error updating environment status widget: {e}")
    
    def closeEvent(self, event):
        """Clean up when widget is closed."""
        self.update_timer.stop()
        event.accept()


class EnvironmentStatusBar(QWidget):
    """
    🎯 ENVIRONMENT STATUS BAR
    
    A more prominent status bar showing all running environments.
    """
    
    switch_requested = pyqtSignal(str)  # container_id
    stop_requested = pyqtSignal(str)    # container_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_environments)
        self.update_timer.start(1500)  # Update every 1.5 seconds
    
    def setup_ui(self):
        """Set up the status bar UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("🎯 Running Environments")
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(12)
        header_label.setFont(header_font)
        header_layout.addWidget(header_label)
        
        header_layout.addStretch()
        
        # Minimize button
        self.toggle_btn = QPushButton("−")
        self.toggle_btn.setMaximumSize(24, 24)
        self.toggle_btn.clicked.connect(self.toggle_visibility)
        header_layout.addWidget(self.toggle_btn)
        
        layout.addLayout(header_layout)
        
        # Environments scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMaximumHeight(200)
        
        self.environments_widget = QWidget()
        self.environments_layout = QVBoxLayout()
        self.environments_layout.setContentsMargins(0, 0, 0, 0)
        self.environments_layout.setSpacing(4)
        self.environments_widget.setLayout(self.environments_layout)
        
        self.scroll_area.setWidget(self.environments_widget)
        layout.addWidget(self.scroll_area)
        
        # Apply styling
        from src.envstarter.utils.theme_manager import get_theme_manager
        theme = get_theme_manager()
        
        bg_color = theme.get_color("surface")
        text_color = theme.get_color("text_primary")
        border_color = theme.get_color("border")
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                color: {text_color};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QScrollArea {{
                border: 1px solid {border_color};
                border-radius: 6px;
                background-color: {bg_color};
            }}
        """)
        
        self.setLayout(layout)
        self.setMaximumHeight(250)
        self.is_minimized = False
    
    def toggle_visibility(self):
        """Toggle between minimized and expanded view."""
        self.is_minimized = not self.is_minimized
        
        if self.is_minimized:
            self.scroll_area.hide()
            self.toggle_btn.setText("+")
            self.setMaximumHeight(50)
        else:
            self.scroll_area.show()
            self.toggle_btn.setText("−")
            self.setMaximumHeight(250)
    
    def update_environments(self):
        """Update the environments display."""
        try:
            from src.envstarter.core.multi_environment_manager import get_multi_environment_manager
            manager = get_multi_environment_manager()
            
            containers = manager.get_all_containers()
            
            # Clear existing widgets
            for i in reversed(range(self.environments_layout.count())):
                child = self.environments_layout.itemAt(i).widget()
                if child:
                    child.deleteLater()
            
            if not containers:
                no_env_label = QLabel("No environments running")
                from src.envstarter.utils.theme_manager import get_theme_manager
                theme = get_theme_manager()
                no_env_label.setStyleSheet(f"color: {theme.get_color('text_muted')}; font-style: italic; padding: 12px;")
                self.environments_layout.addWidget(no_env_label)
            else:
                for container_id, info in containers.items():
                    env_widget = self.create_environment_widget(container_id, info)
                    self.environments_layout.addWidget(env_widget)
        
        except Exception as e:
            print(f"⚠️ Error updating environment status bar: {e}")
    
    def create_environment_widget(self, container_id: str, info: Dict) -> QWidget:
        """Create a widget for a single environment."""
        widget = QFrame()
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)
        
        # Environment info
        env_name = info.get("environment_name", "Unknown")
        state = info.get("state", "unknown")
        stats = info.get("stats", {})
        
        process_count = stats.get("total_processes", 0)
        memory_mb = stats.get("total_memory_mb", 0)
        cpu_percent = stats.get("total_cpu_percent", 0)
        
        # Status indicator
        if state == "running":
            status_icon = "🟢"
            status_color = "#3fb950"
        elif state == "paused":
            status_icon = "⏸️"
            status_color = "#d29922"
        else:
            status_icon = "🔴"
            status_color = "#f85149"
        
        # Environment name and status
        env_label = QLabel(f"{status_icon} {env_name}")
        env_font = QFont()
        env_font.setBold(True)
        env_label.setFont(env_font)
        env_label.setStyleSheet(f"color: {status_color};")
        layout.addWidget(env_label)
        
        # Stats
        stats_label = QLabel(f"📱 {process_count} apps | 💾 {memory_mb:.0f}MB | ⚡ {cpu_percent:.1f}%")
        from src.envstarter.utils.theme_manager import get_theme_manager
        theme = get_theme_manager()
        stats_label.setStyleSheet(f"color: {theme.get_color('text_secondary')}; font-size: 10px;")
        layout.addWidget(stats_label)
        
        layout.addStretch()
        
        # Action buttons
        if state == "running":
            switch_btn = QPushButton("🔄 Switch")
            switch_btn.clicked.connect(lambda: self.switch_requested.emit(container_id))
            layout.addWidget(switch_btn)
        
        stop_btn = QPushButton("🛑 Stop")
        stop_btn.clicked.connect(lambda: self.stop_requested.emit(container_id))
        layout.addWidget(stop_btn)
        
        # Styling
        border_color = theme.get_color("border")
        hover_color = theme.get_color("hover")
        
        widget.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {border_color};
                border-radius: 6px;
                background-color: transparent;
                padding: 2px;
            }}
            QFrame:hover {{
                background-color: {hover_color};
            }}
            QPushButton {{
                padding: 4px 8px;
                font-size: 9px;
                min-height: 20px;
                max-height: 20px;
            }}
        """)
        
        widget.setLayout(layout)
        return widget