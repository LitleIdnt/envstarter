"""
Main environment selector GUI for EnvStarter.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QListWidget, QListWidgetItem,
                            QProgressBar, QTextEdit, QSplitter, QFrame,
                            QMessageBox, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette, QIcon

from src.envstarter.core.models import Environment
from src.envstarter.core.enhanced_app_controller import EnhancedAppController


class EnvironmentListItem(QFrame):
    """Custom widget for environment list items."""
    
    def __init__(self, environment: Environment):
        super().__init__()
        self.environment = environment
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI for the list item."""
        self.setFrameStyle(QFrame.Shape.Box)
        # WCAG AA compliant colors and improved accessibility
        self.setStyleSheet("""
            EnvironmentListItem {
                background-color: #ffffff;
                border: 2px solid #e1e4e8;
                border-radius: 8px;
                margin: 4px;
                padding: 8px;
                min-height: 80px;
            }
            EnvironmentListItem:hover {
                background-color: #f6f8fa;
                border-color: #0366d6;
                border-width: 3px;
            }
            EnvironmentListItem:focus {
                outline: 3px solid #0366d6;
                outline-offset: 2px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        
        # Environment name
        name_label = QLabel(self.environment.name)
        name_font = QFont()
        name_font.setBold(True)
        name_font.setPointSize(14)  # Larger for better readability
        name_label.setFont(name_font)
        name_label.setStyleSheet("color: #24292e; margin-bottom: 4px;")  # WCAG AA compliant contrast
        layout.addWidget(name_label)
        
        # Description
        if self.environment.description:
            desc_label = QLabel(self.environment.description)
            desc_label.setStyleSheet("""
                color: #586069; 
                font-size: 12px; 
                margin-bottom: 6px;
                line-height: 1.4;
            """)  # Better contrast ratio (4.54:1)
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        # Stats with better visual hierarchy
        stats_layout = QHBoxLayout()
        stats_layout.setContentsMargins(0, 6, 0, 0)
        
        app_count = len(self.environment.applications)
        website_count = len(self.environment.websites)
        
        # Create individual badges for better readability
        apps_badge = QLabel(f"📱 {app_count} Apps")
        apps_badge.setStyleSheet("""
            color: #0366d6;
            background-color: #f1f8ff;
            border: 1px solid #c8e1ff;
            border-radius: 12px;
            padding: 4px 8px;
            font-size: 11px;
            font-weight: 500;
        """)
        
        websites_badge = QLabel(f"🌐 {website_count} Sites")
        websites_badge.setStyleSheet("""
            color: #28a745;
            background-color: #f0fff4;
            border: 1px solid #c3e6cb;
            border-radius: 12px;
            padding: 4px 8px;
            font-size: 11px;
            font-weight: 500;
        """)
        
        stats_layout.addWidget(apps_badge)
        stats_layout.addWidget(websites_badge)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        self.setLayout(layout)


class LaunchProgressWidget(QWidget):
    """Widget to show launch progress."""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI."""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Progress bar with better styling
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(24)  # Better touch target
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #d1d5da;
                border-radius: 12px;
                background-color: #f6f8fa;
                text-align: center;
                font-size: 12px;
                font-weight: 500;
            }
            QProgressBar::chunk {
                background-color: #28a745;
                border-radius: 10px;
                margin: 1px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Status text with better visibility
        self.status_label = QLabel()
        self.status_label.setVisible(False)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #24292e;
                font-size: 13px;
                font-weight: 500;
                padding: 8px;
                background-color: #f1f8ff;
                border: 1px solid #c8e1ff;
                border-radius: 6px;
                margin: 4px 0;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Launch log with improved readability
        self.log_text = QTextEdit()
        self.log_text.setVisible(False)
        self.log_text.setMaximumHeight(120)
        self.log_text.setStyleSheet("""
            QTextEdit {
                font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, monospace;
                font-size: 11px;
                line-height: 1.4;
                background-color: #f6f8fa;
                border: 2px solid #d1d5da;
                border-radius: 8px;
                padding: 8px;
                color: #24292e;
            }
            QTextEdit:focus {
                border-color: #0366d6;
                outline: none;
            }
        """)
        layout.addWidget(self.log_text)
        
        self.setLayout(layout)
    
    def show_progress(self):
        """Show progress widgets."""
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        self.log_text.setVisible(True)
        self.log_text.clear()
    
    def hide_progress(self):
        """Hide progress widgets."""
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        self.log_text.setVisible(False)
    
    def update_progress(self, value: int, status: str):
        """Update progress."""
        self.progress_bar.setValue(value)
        self.status_label.setText(status)
    
    def add_log_entry(self, message: str, success: bool = True):
        """Add entry to launch log."""
        color = "green" if success else "red"
        symbol = "✓" if success else "✗"
        self.log_text.append(f'<span style="color: {color};">{symbol} {message}</span>')


class EnvironmentSelector(QWidget):
    """Main environment selector window."""
    
    settings_requested = pyqtSignal()
    
    def __init__(self, controller: EnhancedAppController):
        super().__init__()
        self.controller = controller
        self.current_environment = None
        
        self.setup_ui()
        self.setup_connections()
        self.load_environments()
        
        # Connect controller signals
        self.controller.launcher.launch_started.connect(self.on_launch_started)
        self.controller.launcher.progress_updated.connect(self.on_progress_updated)
        self.controller.launcher.item_launched.connect(self.on_item_launched)
        self.controller.launcher.launch_completed.connect(self.on_launch_completed)
        self.controller.launcher.error_occurred.connect(self.on_launch_error)
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("EnvStarter - Select Environment")
        self.setMinimumSize(900, 650)  # Larger for better accessibility
        self.resize(1000, 750)
        
        # Apply EnvStarter icon
        from src.envstarter.utils.icons import apply_icon_to_widget
        apply_icon_to_widget(self)
        
        # Main layout with better spacing
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)  # More breathing room
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Environment Status Bar
        from src.envstarter.gui.environment_status_widget import EnvironmentStatusWidget
        self.env_status_widget = EnvironmentStatusWidget()
        self.env_status_widget.switch_requested.connect(self.switch_to_environment)
        main_layout.addWidget(self.env_status_widget)
        
        # Header with improved accessibility
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        
        title_label = QLabel("EnvStarter")
        title_label.setObjectName("main-title")  # For accessibility
        title_font = QFont()
        title_font.setPointSize(28)  # Larger for better readability
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel#main-title {
                color: #24292e;
                margin-bottom: 8px;
                letter-spacing: -0.5px;
            }
        """)
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Start your perfect work environment with one click")
        subtitle_label.setObjectName("subtitle")
        subtitle_label.setStyleSheet("""
            QLabel#subtitle {
                color: #586069; 
                font-size: 16px;
                font-weight: 400;
                letter-spacing: 0.1px;
            }
        """)  # WCAG AA compliant contrast
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle_label)
        
        main_layout.addLayout(header_layout)
        
        # Content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Environment list
        left_panel = QWidget()
        left_panel.setObjectName("left-panel")
        left_layout = QVBoxLayout()
        left_layout.setSpacing(12)
        
        list_header = QLabel("Select Environment:")
        list_header.setObjectName("section-header")
        list_header.setStyleSheet("""
            QLabel#section-header {
                font-weight: 600; 
                font-size: 16px; 
                color: #24292e;
                margin-bottom: 8px;
                padding: 4px 0;
            }
        """)  # Better contrast and sizing
        left_layout.addWidget(list_header)
        
        # Add keyboard navigation hint
        nav_hint = QLabel("Use ↑↓ arrow keys to navigate, Enter to select")
        nav_hint.setStyleSheet("""
            color: #6a737d;
            font-size: 12px;
            font-style: italic;
            margin-bottom: 8px;
        """)
        left_layout.addWidget(nav_hint)
        
        self.environment_list = QListWidget()
        self.environment_list.setObjectName("environment-list")
        # WCAG compliant list styling with better focus indicators
        self.environment_list.setStyleSheet("""
            QListWidget#environment-list {
                border: 2px solid #d1d5da;
                border-radius: 8px;
                background-color: #fafbfc;
                padding: 8px;
                outline: none;
            }
            QListWidget#environment-list:focus {
                border-color: #0366d6;
                border-width: 3px;
            }
            QListWidget#environment-list::item {
                border: none;
                padding: 0px;
                margin: 4px;
                border-radius: 6px;
            }
            QListWidget#environment-list::item:selected {
                background-color: transparent;
            }
            QListWidget#environment-list::item:focus {
                outline: 2px solid #0366d6;
                outline-offset: 2px;
            }
        """)
        left_layout.addWidget(self.environment_list)
        
        # Buttons with improved accessibility
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        # Enhanced multi-environment buttons
        self.launch_button = QPushButton("🚀 Launch Environment")
        self.launch_button.setObjectName("primary-button")
        self.launch_button.setMinimumHeight(44)  # WCAG minimum touch target
        self.launch_button.setStyleSheet("""
            QPushButton#primary-button {
                background-color: #28a745;
                color: white;
                border: 2px solid #28a745;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                min-width: 160px;
            }
            QPushButton#primary-button:hover {
                background-color: #218838;
                border-color: #1e7e34;
                border-width: 3px;
            }
            QPushButton#primary-button:focus {
                outline: 3px solid #28a745;
                outline-offset: 2px;
            }
            QPushButton#primary-button:disabled {
                background-color: #e9ecef;
                border-color: #dee2e6;
                color: #6c757d;
            }
        """)
        self.launch_button.setEnabled(False)
        self.launch_button.setToolTip("Launch the selected environment (Ctrl+Enter)")
        button_layout.addWidget(self.launch_button)
        
        self.settings_button = QPushButton("⚙️ Settings")
        self.settings_button.setObjectName("secondary-button")
        self.settings_button.setMinimumHeight(44)  # WCAG minimum touch target
        self.settings_button.setStyleSheet("""
            QPushButton#secondary-button {
                background-color: #0366d6;
                color: white;
                border: 2px solid #0366d6;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                min-width: 120px;
            }
            QPushButton#secondary-button:hover {
                background-color: #0256cc;
                border-color: #0256cc;
                border-width: 3px;
            }
            QPushButton#secondary-button:focus {
                outline: 3px solid #0366d6;
                outline-offset: 2px;
            }
        """)
        self.settings_button.setToolTip("Open settings to manage environments (Ctrl+,)")
        button_layout.addWidget(self.settings_button)
        
        # Enhanced multi-environment buttons
        enhanced_layout = QHBoxLayout()
        enhanced_layout.setSpacing(8)
        
        self.launch_all_button = QPushButton("🚀 Launch All")
        self.launch_all_button.setMinimumHeight(36)
        self.launch_all_button.setStyleSheet("""
            QPushButton {
                background-color: #fd7e14;
                color: white;
                border: 2px solid #fd7e14;
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #e8590c;
                border-color: #e8590c;
            }
        """)
        self.launch_all_button.clicked.connect(self.launch_all_environments)
        enhanced_layout.addWidget(self.launch_all_button)
        
        self.stop_all_button = QPushButton("🛑 Stop All")
        self.stop_all_button.setMinimumHeight(36)
        self.stop_all_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: 2px solid #dc3545;
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #c82333;
                border-color: #c82333;
            }
        """)
        self.stop_all_button.clicked.connect(self.stop_all_containers)
        enhanced_layout.addWidget(self.stop_all_button)
        
        self.dashboard_button = QPushButton("🎮 Dashboard")
        self.dashboard_button.setMinimumHeight(36)
        self.dashboard_button.setStyleSheet("""
            QPushButton {
                background-color: #6f42c1;
                color: white;
                border: 2px solid #6f42c1;
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5a32a3;
                border-color: #5a32a3;
            }
        """)
        self.dashboard_button.clicked.connect(self.show_dashboard)
        enhanced_layout.addWidget(self.dashboard_button)
        
        left_layout.addLayout(button_layout)
        left_layout.addLayout(enhanced_layout)
        left_panel.setLayout(left_layout)
        
        # Right panel - Details and progress
        right_panel = QWidget()
        right_panel.setObjectName("right-panel")
        right_layout = QVBoxLayout()
        right_layout.setSpacing(16)
        
        # Environment details
        details_header = QLabel("Environment Details:")
        details_header.setObjectName("section-header")
        details_header.setStyleSheet("""
            QLabel#section-header {
                font-weight: 600; 
                font-size: 16px; 
                color: #24292e;
                margin-bottom: 8px;
                padding: 4px 0;
            }
        """)
        right_layout.addWidget(details_header)
        
        self.details_text = QTextEdit()
        self.details_text.setObjectName("details-text")
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(220)
        # Improved readability and WCAG compliance
        self.details_text.setStyleSheet("""
            QTextEdit#details-text {
                border: 2px solid #d1d5da;
                border-radius: 8px;
                background-color: #f6f8fa;
                padding: 12px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 13px;
                line-height: 1.5;
                color: #24292e;
            }
            QTextEdit#details-text:focus {
                border-color: #0366d6;
                outline: none;
                border-width: 3px;
            }
        """)
        right_layout.addWidget(self.details_text)
        
        # Launch progress
        progress_header = QLabel("Launch Progress:")
        progress_header.setObjectName("section-header")
        progress_header.setStyleSheet("""
            QLabel#section-header {
                font-weight: 600; 
                font-size: 16px; 
                color: #24292e;
                margin-bottom: 8px;
                padding: 4px 0;
            }
        """)
        right_layout.addWidget(progress_header)
        
        self.progress_widget = LaunchProgressWidget()
        right_layout.addWidget(self.progress_widget)
        
        right_layout.addStretch()
        right_panel.setLayout(right_layout)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # Bottom buttons with better accessibility
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(12)
        bottom_layout.addStretch()
        
        self.minimize_button = QPushButton("↓ Minimize to Tray")
        self.minimize_button.setObjectName("tertiary-button")
        self.minimize_button.setMinimumHeight(36)
        self.minimize_button.setStyleSheet("""
            QPushButton#tertiary-button {
                background-color: #ffeaa7;
                color: #2d3436;
                border: 2px solid #fdcb6e;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton#tertiary-button:hover {
                background-color: #fdcb6e;
                border-color: #e17055;
                border-width: 3px;
            }
            QPushButton#tertiary-button:focus {
                outline: 3px solid #fdcb6e;
                outline-offset: 2px;
            }
        """)
        self.minimize_button.setToolTip("Minimize to system tray (Ctrl+M)")
        bottom_layout.addWidget(self.minimize_button)
        
        self.exit_button = QPushButton("❌ Exit")
        self.exit_button.setObjectName("danger-button")
        self.exit_button.setMinimumHeight(36)
        self.exit_button.setStyleSheet("""
            QPushButton#danger-button {
                background-color: #fff5f5;
                color: #dc3545;
                border: 2px solid #dc3545;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton#danger-button:hover {
                background-color: #dc3545;
                color: white;
                border-width: 3px;
            }
            QPushButton#danger-button:focus {
                outline: 3px solid #dc3545;
                outline-offset: 2px;
            }
        """)
        self.exit_button.setToolTip("Exit EnvStarter completely (Ctrl+Q)")
        bottom_layout.addWidget(self.exit_button)
        
        main_layout.addLayout(bottom_layout)
        
        self.setLayout(main_layout)
    
    def setup_connections(self):
        """Set up signal connections."""
        self.environment_list.itemClicked.connect(self.on_environment_selected)
        self.environment_list.itemDoubleClicked.connect(self.on_environment_double_clicked)
        self.launch_button.clicked.connect(self.on_launch_clicked)
        self.settings_button.clicked.connect(self.show_settings)
        self.minimize_button.clicked.connect(self.hide)
        self.exit_button.clicked.connect(self.controller.quit_application)
        
        # Add keyboard shortcuts for accessibility
        from PyQt6.QtGui import QShortcut, QKeySequence
        from PyQt6.QtCore import Qt
        
        # Ctrl+Enter to launch environment
        launch_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        launch_shortcut.activated.connect(self.on_launch_clicked)
        
        # Enter key to launch environment
        enter_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        enter_shortcut.activated.connect(self.on_launch_clicked)
        
        # Ctrl+, to open settings
        settings_shortcut = QShortcut(QKeySequence("Ctrl+,"), self)
        settings_shortcut.activated.connect(self.settings_requested.emit)
        
        # Ctrl+M to minimize
        minimize_shortcut = QShortcut(QKeySequence("Ctrl+M"), self)
        minimize_shortcut.activated.connect(self.hide)
        
        # Ctrl+Q to quit
        quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        quit_shortcut.activated.connect(self.controller.quit_application)
        
        # Escape key to minimize
        escape_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        escape_shortcut.activated.connect(self.hide)
    
    def load_environments(self):
        """Load environments into the list."""
        self.environment_list.clear()
        environments = self.controller.get_environments()
        
        for env in environments:
            item = QListWidgetItem()
            widget = EnvironmentListItem(env)
            item.setSizeHint(widget.sizeHint())
            
            self.environment_list.addItem(item)
            self.environment_list.setItemWidget(item, widget)
        
        if environments:
            self.environment_list.setCurrentRow(0)
            self.on_environment_selected(self.environment_list.item(0))
    
    def on_environment_selected(self, item):
        """Handle environment selection."""
        if not item:
            return
        
        widget = self.environment_list.itemWidget(item)
        if widget:
            self.current_environment = widget.environment
            self.launch_button.setEnabled(True)
            self.update_environment_details()
    
    def on_environment_double_clicked(self, item):
        """Handle double-click to launch environment."""
        self.on_environment_selected(item)
        if self.current_environment:
            self.on_launch_clicked()
    
    def update_environment_details(self):
        """Update environment details display."""
        if not self.current_environment:
            self.details_text.clear()
            return
        
        details = []
        details.append(f"<b>Name:</b> {self.current_environment.name}")
        
        if self.current_environment.description:
            details.append(f"<b>Description:</b> {self.current_environment.description}")
        
        if self.current_environment.applications:
            details.append(f"<b>Applications ({len(self.current_environment.applications)}):</b>")
            for app in self.current_environment.applications:
                details.append(f"  • {app.name}")
        
        if self.current_environment.websites:
            details.append(f"<b>Websites ({len(self.current_environment.websites)}):</b>")
            for website in self.current_environment.websites:
                details.append(f"  • {website.name} ({website.url})")
        
        if self.current_environment.startup_delay > 0:
            details.append(f"<b>Startup Delay:</b> {self.current_environment.startup_delay} seconds")
        
        self.details_text.setHtml("<br>".join(details))
    
    def on_launch_clicked(self):
        """Handle launch button click."""
        if not self.current_environment:
            return
        
        if self.controller.is_launching():
            QMessageBox.warning(self, "Launch in Progress", 
                              "Another environment is currently being launched.")
            return
        
        # Start launch
        self.launch_button.setEnabled(False)
        self.progress_widget.show_progress()
        
        success = self.controller.launch_environment(self.current_environment)
        if not success:
            self.launch_button.setEnabled(True)
            self.progress_widget.hide_progress()
            QMessageBox.warning(self, "Launch Failed", 
                              "Failed to start environment launch.")
    
    def on_launch_started(self, environment_name: str):
        """Handle launch started."""
        self.progress_widget.update_progress(0, f"Starting {environment_name}...")
    
    def on_progress_updated(self, progress: int, status: str):
        """Handle progress update."""
        self.progress_widget.update_progress(progress, status)
    
    def on_item_launched(self, item_name: str, success: bool):
        """Handle item launched."""
        self.progress_widget.add_log_entry(item_name, success)
    
    def on_launch_completed(self, environment_name: str, success: bool):
        """Handle launch completed."""
        self.launch_button.setEnabled(True)
        
        if success:
            self.progress_widget.update_progress(100, f"{environment_name} launched successfully!")
            
            # Auto-hide after successful launch (with delay)
            config = self.controller.get_config()
            if config.get("minimize_to_tray", True):
                QTimer.singleShot(2000, self.hide)
        else:
            self.progress_widget.update_progress(0, f"Failed to launch {environment_name}")
    
    def on_launch_error(self, error_message: str):
        """Handle launch error."""
        self.launch_button.setEnabled(True)
        self.progress_widget.add_log_entry(f"Error: {error_message}", False)
    
    def launch_all_environments(self):
        """Launch all available environments."""
        environments = self.controller.get_environments()
        
        if not environments:
            QMessageBox.warning(self, "No Environments", "No environments available to launch.")
            return
        
        reply = QMessageBox.question(
            self, "Launch All Environments",
            f"Are you sure you want to launch all {len(environments)} environments?\n\n"
            f"This will start all environments simultaneously.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            from src.envstarter.core.concurrent_launcher import LaunchMode
            
            # Use concurrent launch mode for maximum speed
            success_count = 0
            for env in environments:
                try:
                    if self.controller.launch_environment_quick(env):
                        success_count += 1
                        self.progress_widget.add_log_entry(f"Launched: {env.name}", True)
                    else:
                        self.progress_widget.add_log_entry(f"Failed to launch: {env.name}", False)
                except Exception as e:
                    self.progress_widget.add_log_entry(f"Error launching {env.name}: {str(e)}", False)
            
            QMessageBox.information(
                self, "Launch All Complete",
                f"Launch completed!\n{success_count}/{len(environments)} environments started successfully."
            )
    
    def stop_all_containers(self):
        """Stop all running containers."""
        containers = self.controller.manager.get_all_containers()
        running = [cid for cid, info in containers.items() if info["state"] == "running"]
        
        if not running:
            QMessageBox.information(self, "No Containers", "No running containers to stop.")
            return
        
        reply = QMessageBox.question(
            self, "Stop All Containers",
            f"Are you sure you want to stop all {len(running)} running containers?\n\n"
            f"This will close all applications in all environments.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.controller.stop_all_containers()
            QMessageBox.information(self, "Containers Stopped", f"Stopped {len(running)} containers.")
            self.progress_widget.add_log_entry(f"Stopped {len(running)} containers", True)
    
    def show_dashboard(self):
        """Show the multi-environment dashboard."""
        try:
            from src.envstarter.gui.multi_environment_dashboard import MultiEnvironmentDashboard
            
            # Create or show dashboard
            if not hasattr(self, 'dashboard') or not self.dashboard:
                self.dashboard = MultiEnvironmentDashboard()
            
            self.dashboard.show()
            self.dashboard.raise_()
            self.dashboard.activateWindow()
            
            # Optionally minimize this selector
            self.showMinimized()
            
        except Exception as e:
            QMessageBox.warning(self, "Dashboard Error", f"Failed to open dashboard: {str(e)}")
    
    def show_settings(self):
        """Show the enhanced settings dialog."""
        try:
            from src.envstarter.gui.enhanced_settings_dialog import EnhancedSettingsDialog
            
            # Create or show settings dialog
            if not hasattr(self, 'settings_dialog') or not self.settings_dialog:
                self.settings_dialog = EnhancedSettingsDialog(self.controller)
                self.settings_dialog.environment_changed.connect(self.on_environments_changed)
            
            self.settings_dialog.show()
            self.settings_dialog.raise_()
            self.settings_dialog.activateWindow()
            
        except Exception as e:
            QMessageBox.warning(self, "Settings Error", f"Failed to open settings: {str(e)}")
    
    def switch_to_environment(self, container_id: str):
        """Switch to the specified environment."""
        try:
            self.controller.switch_to_container(container_id)
        except Exception as e:
            QMessageBox.warning(self, "Switch Error", f"Failed to switch to environment: {str(e)}")
    
    def on_environments_changed(self):
        """Handle environment changes."""
        # Refresh the environment list
        self.load_environments()
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.controller.get_config().get("minimize_to_tray", True):
            event.ignore()
            self.hide()
        else:
            self.controller.quit_application()
            event.accept()