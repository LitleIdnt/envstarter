"""
🔧 ENHANCED SETTINGS DIALOG 🔧
Complete environment management interface for the new multi-environment system!

This provides full CRUD operations for environments, applications, and settings.
"""

import os
import asyncio
import threading
from pathlib import Path
from typing import List, Dict, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QLineEdit, QTextEdit, QSpinBox, QCheckBox, 
    QFileDialog, QMessageBox, QFormLayout, QGroupBox, QScrollArea, QFrame, 
    QSplitter, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, 
    QAbstractItemView, QProgressBar, QSlider, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt6.QtGui import QFont, QIcon, QPalette

from src.envstarter.core.models import Environment, Application, Website
from src.envstarter.core.enhanced_app_controller import EnhancedAppController
from src.envstarter.core.multi_environment_manager import get_multi_environment_manager
from src.envstarter.utils.system_integration import SystemIntegration


class ApplicationScanDialog(QDialog):
    """Dialog for scanning and selecting applications from the system."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_apps = []
        self.setup_ui()
        self.start_scan()
    
    def setup_ui(self):
        """Set up the application scan dialog UI."""
        self.setWindowTitle("🔍 Scan System Applications")
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("🔍 Scanning System for Applications...")
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(14)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Initializing scan...")
        layout.addWidget(self.status_label)
        
        # Applications list
        self.apps_tree = QTreeWidget()
        self.apps_tree.setHeaderLabels(["Application", "Path", "Type"])
        self.apps_tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        layout.addWidget(self.apps_tree)
        
        # Filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Type to filter applications...")
        self.filter_edit.textChanged.connect(self.filter_applications)
        filter_layout.addWidget(self.filter_edit)
        layout.addLayout(filter_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("✅ Select All")
        self.select_all_btn.clicked.connect(self.select_all)
        button_layout.addWidget(self.select_all_btn)
        
        self.select_none_btn = QPushButton("❌ Select None")
        self.select_none_btn.clicked.connect(self.select_none)
        button_layout.addWidget(self.select_none_btn)
        
        button_layout.addStretch()
        
        self.ok_btn = QPushButton("✅ Add Selected")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setEnabled(False)
        button_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def start_scan(self):
        """Start scanning for applications in a separate thread."""
        self.scan_thread = ApplicationScanThread()
        self.scan_thread.progress_updated.connect(self.update_progress)
        self.scan_thread.app_found.connect(self.add_application)
        self.scan_thread.scan_completed.connect(self.scan_finished)
        self.scan_thread.start()
    
    def update_progress(self, value: int, status: str):
        """Update scan progress."""
        self.progress_bar.setValue(value)
        self.status_label.setText(status)
    
    def add_application(self, app_data: Dict):
        """Add found application to the tree."""
        item = QTreeWidgetItem([
            app_data["name"],
            app_data["path"],
            app_data.get("type", "Application")
        ])
        item.setCheckState(0, Qt.CheckState.Unchecked)
        item.app_data = app_data
        self.apps_tree.addTopLevelItem(item)
    
    def scan_finished(self):
        """Handle scan completion."""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Found {self.apps_tree.topLevelItemCount()} applications")
        self.ok_btn.setEnabled(True)
        
        # Auto-expand tree
        self.apps_tree.expandAll()
    
    def filter_applications(self):
        """Filter applications based on search text."""
        filter_text = self.filter_edit.text().lower()
        
        for i in range(self.apps_tree.topLevelItemCount()):
            item = self.apps_tree.topLevelItem(i)
            app_name = item.text(0).lower()
            app_path = item.text(1).lower()
            
            # Show item if filter matches name or path
            visible = (filter_text in app_name or filter_text in app_path)
            item.setHidden(not visible)
    
    def select_all(self):
        """Select all visible applications."""
        for i in range(self.apps_tree.topLevelItemCount()):
            item = self.apps_tree.topLevelItem(i)
            if not item.isHidden():
                item.setCheckState(0, Qt.CheckState.Checked)
    
    def select_none(self):
        """Deselect all applications."""
        for i in range(self.apps_tree.topLevelItemCount()):
            item = self.apps_tree.topLevelItem(i)
            item.setCheckState(0, Qt.CheckState.Unchecked)
    
    def get_selected_applications(self) -> List[Dict]:
        """Get list of selected applications."""
        selected = []
        for i in range(self.apps_tree.topLevelItemCount()):
            item = self.apps_tree.topLevelItem(i)
            if item.checkState(0) == Qt.CheckState.Checked:
                selected.append(item.app_data)
        return selected


class ApplicationScanThread(QThread):
    """Thread for scanning system applications."""
    
    progress_updated = pyqtSignal(int, str)  # progress, status
    app_found = pyqtSignal(dict)  # app_data
    scan_completed = pyqtSignal()
    
    def run(self):
        """Run the application scan."""
        system_integration = SystemIntegration()
        
        def progress_callback(progress: int, status: str):
            self.progress_updated.emit(progress, status)
        
        try:
            # Get all applications
            all_apps = system_integration.get_all_applications(progress_callback)
            
            # Emit each application found
            for app in all_apps:
                self.app_found.emit(app)
            
            self.scan_completed.emit()
            
        except Exception as e:
            self.progress_updated.emit(100, f"Scan failed: {str(e)}")
            self.scan_completed.emit()


class EnvironmentEditDialog(QDialog):
    """Dialog for creating/editing environments."""
    
    def __init__(self, environment: Environment = None, parent=None):
        super().__init__(parent)
        self.environment = environment or Environment("New Environment", "")
        self.is_editing = environment is not None
        self.setup_ui()
        self.populate_fields()
    
    def setup_ui(self):
        """Set up the environment editing UI."""
        title = "✏️ Edit Environment" if self.is_editing else "➕ Create Environment"
        self.setWindowTitle(title)
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel(title)
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(16)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Main form
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter environment name...")
        form_layout.addRow("🏷️ Name:", self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Enter environment description...")
        form_layout.addRow("📝 Description:", self.description_edit)
        
        self.startup_delay_spin = QSpinBox()
        self.startup_delay_spin.setRange(0, 60)
        self.startup_delay_spin.setSuffix(" seconds")
        form_layout.addRow("⏱️ Startup Delay:", self.startup_delay_spin)
        
        layout.addLayout(form_layout)
        
        # Tabs for applications and websites
        self.tab_widget = QTabWidget()
        
        # Applications tab
        self.apps_tab = self.create_applications_tab()
        self.tab_widget.addTab(self.apps_tab, "📱 Applications")
        
        # Websites tab
        self.websites_tab = self.create_websites_tab()
        self.tab_widget.addTab(self.websites_tab, "🌐 Websites")
        
        # Advanced tab
        self.advanced_tab = self.create_advanced_tab()
        self.tab_widget.addTab(self.advanced_tab, "⚙️ Advanced")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.test_btn = QPushButton("🧪 Test Environment")
        self.test_btn.clicked.connect(self.test_environment)
        button_layout.addWidget(self.test_btn)
        
        button_layout.addStretch()
        
        self.save_btn = QPushButton("💾 Save Environment")
        self.save_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_applications_tab(self) -> QWidget:
        """Create the applications management tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Header with buttons
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("📱 Applications to Launch:"))
        header_layout.addStretch()
        
        self.add_app_btn = QPushButton("➕ Add Application")
        self.add_app_btn.clicked.connect(self.add_application)
        header_layout.addWidget(self.add_app_btn)
        
        self.scan_apps_btn = QPushButton("🔍 Scan System")
        self.scan_apps_btn.clicked.connect(self.scan_system_applications)
        header_layout.addWidget(self.scan_apps_btn)
        
        layout.addLayout(header_layout)
        
        # Applications table
        self.apps_table = QTableWidget(0, 4)
        self.apps_table.setHorizontalHeaderLabels(["Name", "Path", "Arguments", "Actions"])
        self.apps_table.horizontalHeader().setStretchLastSection(True)
        self.apps_table.setAlternatingRowColors(True)
        layout.addWidget(self.apps_table)
        
        tab.setLayout(layout)
        return tab
    
    def create_websites_tab(self) -> QWidget:
        """Create the websites management tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Header with buttons
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("🌐 Websites to Open:"))
        header_layout.addStretch()
        
        self.add_website_btn = QPushButton("➕ Add Website")
        self.add_website_btn.clicked.connect(self.add_website)
        header_layout.addWidget(self.add_website_btn)
        
        layout.addLayout(header_layout)
        
        # Websites table
        self.websites_table = QTableWidget(0, 3)
        self.websites_table.setHorizontalHeaderLabels(["Name", "URL", "Actions"])
        self.websites_table.horizontalHeader().setStretchLastSection(True)
        self.websites_table.setAlternatingRowColors(True)
        layout.addWidget(self.websites_table)
        
        tab.setLayout(layout)
        return tab
    
    def create_advanced_tab(self) -> QWidget:
        """Create the advanced settings tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Virtual Desktop Settings
        vd_group = QGroupBox("🖥️ Virtual Desktop Settings")
        vd_layout = QFormLayout()
        
        self.use_vd_check = QCheckBox("Use Virtual Desktop")
        self.use_vd_check.setChecked(True)
        vd_layout.addRow(self.use_vd_check)
        
        self.desktop_name_edit = QLineEdit()
        self.desktop_name_edit.setPlaceholderText("Auto-generate from environment name")
        vd_layout.addRow("Desktop Name:", self.desktop_name_edit)
        
        self.auto_switch_check = QCheckBox("Auto-switch to desktop when launching")
        self.auto_switch_check.setChecked(True)
        vd_layout.addRow(self.auto_switch_check)
        
        self.close_apps_check = QCheckBox("Close apps when stopping environment")
        vd_layout.addRow(self.close_apps_check)
        
        vd_group.setLayout(vd_layout)
        layout.addWidget(vd_group)
        
        # Container Settings
        container_group = QGroupBox("📦 Container Settings")
        container_layout = QFormLayout()
        
        self.container_priority_spin = QSpinBox()
        self.container_priority_spin.setRange(1, 10)
        self.container_priority_spin.setValue(5)
        container_layout.addRow("Launch Priority:", self.container_priority_spin)
        
        container_group.setLayout(container_layout)
        layout.addWidget(container_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def add_application(self):
        """Add a new application to the environment."""
        dialog = QDialog(self)
        dialog.setWindowTitle("➕ Add Application")
        dialog.setMinimumSize(500, 300)
        
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Application name...")
        form_layout.addRow("Name:", name_edit)
        
        path_layout = QHBoxLayout()
        path_edit = QLineEdit()
        path_edit.setPlaceholderText("Path to executable...")
        browse_btn = QPushButton("Browse...")
        
        def browse_executable():
            file_path, _ = QFileDialog.getOpenFileName(
                dialog, "Select Executable", "", 
                "Executables (*.exe);;All Files (*.*)"
            )
            if file_path:
                path_edit.setText(file_path)
                if not name_edit.text():
                    name_edit.setText(Path(file_path).stem)
        
        browse_btn.clicked.connect(browse_executable)
        path_layout.addWidget(path_edit)
        path_layout.addWidget(browse_btn)
        form_layout.addRow("Path:", path_layout)
        
        args_edit = QLineEdit()
        args_edit.setPlaceholderText("Command line arguments (optional)...")
        form_layout.addRow("Arguments:", args_edit)
        
        workdir_edit = QLineEdit()
        workdir_edit.setPlaceholderText("Working directory (optional)...")
        form_layout.addRow("Working Dir:", workdir_edit)
        
        wait_check = QCheckBox("Wait for application to exit")
        form_layout.addRow(wait_check)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_btn = QPushButton("✅ Add")
        cancel_btn = QPushButton("❌ Cancel")
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if name_edit.text() and path_edit.text():
                app = Application(
                    name=name_edit.text(),
                    path=path_edit.text(),
                    arguments=args_edit.text(),
                    working_directory=workdir_edit.text() or None,
                    wait_for_exit=wait_check.isChecked()
                )
                self.add_application_to_table(app)
    
    def add_website(self):
        """Add a new website to the environment."""
        dialog = QDialog(self)
        dialog.setWindowTitle("➕ Add Website")
        dialog.setMinimumSize(400, 200)
        
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Website name...")
        form_layout.addRow("Name:", name_edit)
        
        url_edit = QLineEdit()
        url_edit.setPlaceholderText("https://example.com")
        form_layout.addRow("URL:", url_edit)
        
        new_tab_check = QCheckBox("Open in new tab")
        new_tab_check.setChecked(True)
        form_layout.addRow(new_tab_check)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_btn = QPushButton("✅ Add")
        cancel_btn = QPushButton("❌ Cancel")
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if name_edit.text() and url_edit.text():
                website = Website(
                    name=name_edit.text(),
                    url=url_edit.text(),
                    new_tab=new_tab_check.isChecked()
                )
                self.add_website_to_table(website)
    
    def scan_system_applications(self):
        """Scan system for applications."""
        dialog = ApplicationScanDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_apps = dialog.get_selected_applications()
            for app_data in selected_apps:
                app = Application(
                    name=app_data["name"],
                    path=app_data["path"]
                )
                self.add_application_to_table(app)
    
    def add_application_to_table(self, app: Application):
        """Add application to the table."""
        row = self.apps_table.rowCount()
        self.apps_table.insertRow(row)
        
        self.apps_table.setItem(row, 0, QTableWidgetItem(app.name))
        self.apps_table.setItem(row, 1, QTableWidgetItem(app.path))
        self.apps_table.setItem(row, 2, QTableWidgetItem(app.arguments))
        
        # Actions
        actions_layout = QHBoxLayout()
        edit_btn = QPushButton("✏️")
        edit_btn.setMaximumSize(30, 30)
        edit_btn.clicked.connect(lambda: self.edit_application(row))
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setMaximumSize(30, 30)
        delete_btn.clicked.connect(lambda: self.delete_application(row))
        
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(delete_btn)
        
        actions_widget = QWidget()
        actions_widget.setLayout(actions_layout)
        self.apps_table.setCellWidget(row, 3, actions_widget)
    
    def add_website_to_table(self, website: Website):
        """Add website to the table."""
        row = self.websites_table.rowCount()
        self.websites_table.insertRow(row)
        
        self.websites_table.setItem(row, 0, QTableWidgetItem(website.name))
        self.websites_table.setItem(row, 1, QTableWidgetItem(website.url))
        
        # Actions
        actions_layout = QHBoxLayout()
        edit_btn = QPushButton("✏️")
        edit_btn.setMaximumSize(30, 30)
        edit_btn.clicked.connect(lambda: self.edit_website(row))
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setMaximumSize(30, 30)
        delete_btn.clicked.connect(lambda: self.delete_website(row))
        
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(delete_btn)
        
        actions_widget = QWidget()
        actions_widget.setLayout(actions_layout)
        self.websites_table.setCellWidget(row, 2, actions_widget)
    
    def edit_application(self, row: int):
        """Edit application at the given row."""
        # Implementation for editing existing application
        pass
    
    def delete_application(self, row: int):
        """Delete application at the given row."""
        self.apps_table.removeRow(row)
    
    def edit_website(self, row: int):
        """Edit website at the given row."""
        # Implementation for editing existing website
        pass
    
    def delete_website(self, row: int):
        """Delete website at the given row."""
        self.websites_table.removeRow(row)
    
    def populate_fields(self):
        """Populate fields with environment data."""
        self.name_edit.setText(self.environment.name)
        self.description_edit.setPlainText(self.environment.description)
        self.startup_delay_spin.setValue(self.environment.startup_delay)
        
        # Populate applications
        for app in self.environment.applications:
            self.add_application_to_table(app)
        
        # Populate websites
        for website in self.environment.websites:
            self.add_website_to_table(website)
        
        # Populate advanced settings
        self.use_vd_check.setChecked(self.environment.use_virtual_desktop)
        self.desktop_name_edit.setText(self.environment.desktop_name or "")
        self.auto_switch_check.setChecked(self.environment.auto_switch_desktop)
        self.close_apps_check.setChecked(self.environment.close_apps_on_stop)
    
    def test_environment(self):
        """Test the environment configuration."""
        env = self.get_environment()
        if not env.applications and not env.websites:
            QMessageBox.warning(self, "Test Environment", 
                              "Environment has no applications or websites to test!")
            return
        
        # Create a temporary test
        QMessageBox.information(self, "Test Environment", 
                               f"Environment '{env.name}' has:\n"
                               f"• {len(env.applications)} applications\n"
                               f"• {len(env.websites)} websites\n\n"
                               f"Test functionality coming soon!")
    
    def get_environment(self) -> Environment:
        """Get the configured environment."""
        # Collect applications from table
        applications = []
        for row in range(self.apps_table.rowCount()):
            name_item = self.apps_table.item(row, 0)
            path_item = self.apps_table.item(row, 1)
            args_item = self.apps_table.item(row, 2)
            
            if name_item and path_item:
                app = Application(
                    name=name_item.text(),
                    path=path_item.text(),
                    arguments=args_item.text() if args_item else ""
                )
                applications.append(app)
        
        # Collect websites from table
        websites = []
        for row in range(self.websites_table.rowCount()):
            name_item = self.websites_table.item(row, 0)
            url_item = self.websites_table.item(row, 1)
            
            if name_item and url_item:
                website = Website(
                    name=name_item.text(),
                    url=url_item.text()
                )
                websites.append(website)
        
        # Update environment
        self.environment.name = self.name_edit.text()
        self.environment.description = self.description_edit.toPlainText()
        self.environment.startup_delay = self.startup_delay_spin.value()
        self.environment.applications = applications
        self.environment.websites = websites
        self.environment.use_virtual_desktop = self.use_vd_check.isChecked()
        self.environment.desktop_name = self.desktop_name_edit.text() or None
        self.environment.auto_switch_desktop = self.auto_switch_check.isChecked()
        self.environment.close_apps_on_stop = self.close_apps_check.isChecked()
        
        return self.environment


class EnhancedSettingsDialog(QDialog):
    """
    🔧 ENHANCED SETTINGS DIALOG 🔧
    Complete settings and environment management for the multi-environment system.
    """
    
    environment_changed = pyqtSignal()
    
    def __init__(self, controller: EnhancedAppController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.manager = get_multi_environment_manager()
        self.setup_ui()
        self.load_environments()
        
    def setup_ui(self):
        """Set up the enhanced settings dialog UI."""
        self.setWindowTitle("🔧 EnvStarter Settings & Environment Management")
        self.setMinimumSize(1000, 700)
        
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("🔧 EnvStarter Enhanced Settings")
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(18)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Environments tab
        self.environments_tab = self.create_environments_tab()
        self.tab_widget.addTab(self.environments_tab, "🎯 Environments")
        
        # System settings tab
        self.system_tab = self.create_system_tab()
        self.tab_widget.addTab(self.system_tab, "⚙️ System Settings")
        
        # Container management tab
        self.containers_tab = self.create_containers_tab()
        self.tab_widget.addTab(self.containers_tab, "📦 Active Containers")
        
        layout.addWidget(self.tab_widget)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_all)
        button_layout.addWidget(self.refresh_btn)
        
        button_layout.addStretch()
        
        self.apply_btn = QPushButton("💾 Apply")
        self.apply_btn.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_btn)
        
        self.ok_btn = QPushButton("✅ OK")
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_environments_tab(self) -> QWidget:
        """Create the environments management tab."""
        tab = QWidget()
        layout = QHBoxLayout()
        
        # Left side - Environment list
        left_layout = QVBoxLayout()
        
        # Header with buttons
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("🎯 Environments:"))
        header_layout.addStretch()
        
        self.new_env_btn = QPushButton("➕ New")
        self.new_env_btn.clicked.connect(self.create_new_environment)
        header_layout.addWidget(self.new_env_btn)
        
        self.import_env_btn = QPushButton("📥 Import")
        self.import_env_btn.clicked.connect(self.import_environments)
        header_layout.addWidget(self.import_env_btn)
        
        left_layout.addLayout(header_layout)
        
        # Environment list
        self.env_list = QListWidget()
        self.env_list.itemSelectionChanged.connect(self.on_environment_selected)
        self.env_list.itemDoubleClicked.connect(self.edit_selected_environment)
        left_layout.addWidget(self.env_list)
        
        layout.addLayout(left_layout, 1)
        
        # Right side - Environment details and actions
        right_layout = QVBoxLayout()
        
        # Environment details
        details_group = QGroupBox("📋 Environment Details")
        details_layout = QVBoxLayout()
        
        self.env_details_label = QLabel("Select an environment to view details")
        self.env_details_label.setWordWrap(True)
        self.env_details_label.setStyleSheet("padding: 10px; background: #f0f0f0; border-radius: 5px;")
        details_layout.addWidget(self.env_details_label)
        
        details_group.setLayout(details_layout)
        right_layout.addWidget(details_group)
        
        # Actions
        actions_group = QGroupBox("⚡ Actions")
        actions_layout = QVBoxLayout()
        
        self.edit_env_btn = QPushButton("✏️ Edit Environment")
        self.edit_env_btn.clicked.connect(self.edit_selected_environment)
        self.edit_env_btn.setEnabled(False)
        actions_layout.addWidget(self.edit_env_btn)
        
        self.duplicate_env_btn = QPushButton("📋 Duplicate Environment")
        self.duplicate_env_btn.clicked.connect(self.duplicate_selected_environment)
        self.duplicate_env_btn.setEnabled(False)
        actions_layout.addWidget(self.duplicate_env_btn)
        
        self.launch_env_btn = QPushButton("🚀 Launch Environment")
        self.launch_env_btn.clicked.connect(self.launch_selected_environment)
        self.launch_env_btn.setEnabled(False)
        actions_layout.addWidget(self.launch_env_btn)
        
        self.export_env_btn = QPushButton("📤 Export Environment")
        self.export_env_btn.clicked.connect(self.export_selected_environment)
        self.export_env_btn.setEnabled(False)
        actions_layout.addWidget(self.export_env_btn)
        
        actions_layout.addStretch()
        
        self.delete_env_btn = QPushButton("🗑️ Delete Environment")
        self.delete_env_btn.clicked.connect(self.delete_selected_environment)
        self.delete_env_btn.setEnabled(False)
        self.delete_env_btn.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; }")
        actions_layout.addWidget(self.delete_env_btn)
        
        actions_group.setLayout(actions_layout)
        right_layout.addWidget(actions_group)
        
        layout.addLayout(right_layout, 1)
        
        tab.setLayout(layout)
        return tab
    
    def create_system_tab(self) -> QWidget:
        """Create the system settings tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # General settings
        general_group = QGroupBox("🔧 General Settings")
        general_layout = QFormLayout()
        
        self.auto_start_check = QCheckBox("Start with Windows")
        general_layout.addRow(self.auto_start_check)
        
        self.minimize_tray_check = QCheckBox("Minimize to system tray")
        general_layout.addRow(self.minimize_tray_check)
        
        self.show_notifications_check = QCheckBox("Show notifications")
        general_layout.addRow(self.show_notifications_check)
        
        general_group.setLayout(general_layout)
        layout.addWidget(general_group)
        
        # Multi-environment settings
        multi_env_group = QGroupBox("📦 Multi-Environment Settings")
        multi_env_layout = QFormLayout()
        
        self.max_containers_spin = QSpinBox()
        self.max_containers_spin.setRange(1, 20)
        self.max_containers_spin.setValue(10)
        multi_env_layout.addRow("Max Concurrent Containers:", self.max_containers_spin)
        
        self.default_launch_mode_combo = QComboBox()
        self.default_launch_mode_combo.addItems(["Concurrent", "Sequential", "Batched", "Staggered"])
        multi_env_layout.addRow("Default Launch Mode:", self.default_launch_mode_combo)
        
        self.auto_refresh_check = QCheckBox("Auto-refresh container status")
        self.auto_refresh_check.setChecked(True)
        multi_env_layout.addRow(self.auto_refresh_check)
        
        multi_env_group.setLayout(multi_env_layout)
        layout.addWidget(multi_env_group)
        
        # Performance settings
        perf_group = QGroupBox("⚡ Performance Settings")
        perf_layout = QFormLayout()
        
        self.monitoring_interval_spin = QSpinBox()
        self.monitoring_interval_spin.setRange(1, 30)
        self.monitoring_interval_spin.setValue(5)
        self.monitoring_interval_spin.setSuffix(" seconds")
        perf_layout.addRow("Monitoring Interval:", self.monitoring_interval_spin)
        
        self.resource_limit_check = QCheckBox("Enable resource limits")
        perf_layout.addRow(self.resource_limit_check)
        
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_containers_tab(self) -> QWidget:
        """Create the active containers management tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("📦 Active Containers:"))
        header_layout.addStretch()
        
        self.refresh_containers_btn = QPushButton("🔄 Refresh")
        self.refresh_containers_btn.clicked.connect(self.refresh_containers)
        header_layout.addWidget(self.refresh_containers_btn)
        
        self.stop_all_containers_btn = QPushButton("🛑 Stop All")
        self.stop_all_containers_btn.clicked.connect(self.stop_all_containers)
        header_layout.addWidget(self.stop_all_containers_btn)
        
        layout.addLayout(header_layout)
        
        # Containers table
        self.containers_table = QTableWidget(0, 6)
        self.containers_table.setHorizontalHeaderLabels([
            "Environment", "State", "Processes", "Memory (MB)", "CPU (%)", "Actions"
        ])
        self.containers_table.horizontalHeader().setStretchLastSection(True)
        self.containers_table.setAlternatingRowColors(True)
        layout.addWidget(self.containers_table)
        
        # System resources summary
        resources_group = QGroupBox("📊 System Resources")
        resources_layout = QFormLayout()
        
        self.total_containers_label = QLabel("0")
        resources_layout.addRow("Total Containers:", self.total_containers_label)
        
        self.running_containers_label = QLabel("0")
        resources_layout.addRow("Running Containers:", self.running_containers_label)
        
        self.total_memory_label = QLabel("0.0 MB")
        resources_layout.addRow("Total Memory:", self.total_memory_label)
        
        self.total_processes_label = QLabel("0")
        resources_layout.addRow("Total Processes:", self.total_processes_label)
        
        resources_group.setLayout(resources_layout)
        layout.addWidget(resources_group)
        
        tab.setLayout(layout)
        return tab
    
    def load_environments(self):
        """Load environments into the list."""
        self.env_list.clear()
        environments = self.controller.get_environments()
        
        for env in environments:
            item = QListWidgetItem(f"🎯 {env.name}")
            item.setData(Qt.ItemDataRole.UserRole, env)
            self.env_list.addItem(item)
    
    def on_environment_selected(self):
        """Handle environment selection."""
        items = self.env_list.selectedItems()
        if items:
            env = items[0].data(Qt.ItemDataRole.UserRole)
            self.show_environment_details(env)
            self.enable_environment_actions(True)
        else:
            self.show_environment_details(None)
            self.enable_environment_actions(False)
    
    def show_environment_details(self, env: Environment):
        """Show environment details."""
        if not env:
            self.env_details_label.setText("Select an environment to view details")
            return
        
        details = f"""
        <h3>🎯 {env.name}</h3>
        <p><b>Description:</b> {env.description or 'No description'}</p>
        <p><b>📱 Applications:</b> {len(env.applications)}</p>
        <p><b>🌐 Websites:</b> {len(env.websites)}</p>
        <p><b>⏱️ Startup Delay:</b> {env.startup_delay} seconds</p>
        <p><b>🖥️ Virtual Desktop:</b> {'Yes' if env.use_virtual_desktop else 'No'}</p>
        """
        
        if env.applications:
            details += "<p><b>Applications:</b><br>"
            for app in env.applications[:5]:  # Show first 5
                details += f"  • {app.name}<br>"
            if len(env.applications) > 5:
                details += f"  ... and {len(env.applications) - 5} more<br>"
            details += "</p>"
        
        if env.websites:
            details += "<p><b>Websites:</b><br>"
            for site in env.websites[:5]:  # Show first 5
                details += f"  • {site.name}<br>"
            if len(env.websites) > 5:
                details += f"  ... and {len(env.websites) - 5} more<br>"
            details += "</p>"
        
        self.env_details_label.setText(details)
    
    def enable_environment_actions(self, enabled: bool):
        """Enable/disable environment action buttons."""
        self.edit_env_btn.setEnabled(enabled)
        self.duplicate_env_btn.setEnabled(enabled)
        self.launch_env_btn.setEnabled(enabled)
        self.export_env_btn.setEnabled(enabled)
        self.delete_env_btn.setEnabled(enabled)
    
    def create_new_environment(self):
        """Create a new environment."""
        dialog = EnvironmentEditDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            env = dialog.get_environment()
            if self.controller.add_environment(env):
                self.load_environments()
                self.environment_changed.emit()
                QMessageBox.information(self, "Success", 
                                      f"Environment '{env.name}' created successfully!")
            else:
                QMessageBox.warning(self, "Error", 
                                  "Failed to create environment. Name might already exist.")
    
    def edit_selected_environment(self):
        """Edit the selected environment."""
        items = self.env_list.selectedItems()
        if not items:
            return
        
        env = items[0].data(Qt.ItemDataRole.UserRole)
        dialog = EnvironmentEditDialog(env, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_env = dialog.get_environment()
            if self.controller.update_environment(updated_env):
                self.load_environments()
                self.environment_changed.emit()
                QMessageBox.information(self, "Success", 
                                      f"Environment '{updated_env.name}' updated successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to update environment.")
    
    def duplicate_selected_environment(self):
        """Duplicate the selected environment."""
        items = self.env_list.selectedItems()
        if not items:
            return
        
        env = items[0].data(Qt.ItemDataRole.UserRole)
        
        # Create a copy
        new_env = Environment(
            name=f"{env.name} (Copy)",
            description=env.description,
            applications=env.applications.copy(),
            websites=env.websites.copy(),
            startup_delay=env.startup_delay,
            use_virtual_desktop=env.use_virtual_desktop,
            desktop_name=env.desktop_name,
            auto_switch_desktop=env.auto_switch_desktop,
            close_apps_on_stop=env.close_apps_on_stop
        )
        
        if self.controller.add_environment(new_env):
            self.load_environments()
            self.environment_changed.emit()
            QMessageBox.information(self, "Success", 
                                  f"Environment duplicated as '{new_env.name}'!")
        else:
            QMessageBox.warning(self, "Error", "Failed to duplicate environment.")
    
    def launch_selected_environment(self):
        """Launch the selected environment."""
        items = self.env_list.selectedItems()
        if not items:
            return
        
        env = items[0].data(Qt.ItemDataRole.UserRole)
        
        try:
            self.controller.launch_environment_quick(env)
            QMessageBox.information(self, "Environment Launched", 
                                  f"Environment '{env.name}' is starting...")
        except Exception as e:
            QMessageBox.warning(self, "Launch Failed", f"Failed to launch environment: {str(e)}")
    
    def export_selected_environment(self):
        """Export the selected environment."""
        items = self.env_list.selectedItems()
        if not items:
            return
        
        env = items[0].data(Qt.ItemDataRole.UserRole)
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Environment", f"{env.name}.json", 
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if file_path:
            try:
                import json
                env_data = env.to_dict()
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(env_data, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(self, "Export Successful", 
                                      f"Environment exported to {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Failed", f"Failed to export: {str(e)}")
    
    def import_environments(self):
        """Import environments from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Environments", "", 
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle single environment or list of environments
                if isinstance(data, dict):
                    if 'environments' in data:
                        # EnvStarter format
                        env_data_list = data['environments']
                    else:
                        # Single environment
                        env_data_list = [data]
                else:
                    # List of environments
                    env_data_list = data
                
                imported = 0
                for env_data in env_data_list:
                    try:
                        env = Environment.from_dict(env_data)
                        if self.controller.add_environment(env):
                            imported += 1
                    except Exception as e:
                        print(f"Failed to import environment: {e}")
                        continue
                
                if imported > 0:
                    self.load_environments()
                    self.environment_changed.emit()
                    QMessageBox.information(self, "Import Successful", 
                                          f"Imported {imported} environment(s)")
                else:
                    QMessageBox.warning(self, "Import Failed", "No environments were imported")
                    
            except Exception as e:
                QMessageBox.warning(self, "Import Failed", f"Failed to import: {str(e)}")
    
    def delete_selected_environment(self):
        """Delete the selected environment."""
        items = self.env_list.selectedItems()
        if not items:
            return
        
        env = items[0].data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, "Delete Environment", 
            f"Are you sure you want to delete '{env.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.controller.delete_environment(env.id):
                self.load_environments()
                self.environment_changed.emit()
                QMessageBox.information(self, "Success", "Environment deleted successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to delete environment.")
    
    def refresh_containers(self):
        """Refresh the containers table."""
        self.containers_table.setRowCount(0)
        containers = self.manager.get_all_containers()
        
        for container_id, info in containers.items():
            row = self.containers_table.rowCount()
            self.containers_table.insertRow(row)
            
            self.containers_table.setItem(row, 0, QTableWidgetItem(info["environment_name"]))
            self.containers_table.setItem(row, 1, QTableWidgetItem(info["state"]))
            
            stats = info.get("stats", {})
            self.containers_table.setItem(row, 2, QTableWidgetItem(str(stats.get("total_processes", 0))))
            self.containers_table.setItem(row, 3, QTableWidgetItem(f"{stats.get('total_memory_mb', 0):.1f}"))
            self.containers_table.setItem(row, 4, QTableWidgetItem(f"{stats.get('total_cpu_percent', 0):.1f}"))
            
            # Actions
            actions_layout = QHBoxLayout()
            
            if info["state"] == "running":
                switch_btn = QPushButton("🔄")
                switch_btn.setMaximumSize(30, 30)
                switch_btn.clicked.connect(lambda checked, cid=container_id: self.switch_container(cid))
                actions_layout.addWidget(switch_btn)
                
                pause_btn = QPushButton("⏸️")
                pause_btn.setMaximumSize(30, 30)
                pause_btn.clicked.connect(lambda checked, cid=container_id: self.pause_container(cid))
                actions_layout.addWidget(pause_btn)
            
            elif info["state"] == "paused":
                resume_btn = QPushButton("▶️")
                resume_btn.setMaximumSize(30, 30)
                resume_btn.clicked.connect(lambda checked, cid=container_id: self.resume_container(cid))
                actions_layout.addWidget(resume_btn)
            
            stop_btn = QPushButton("🛑")
            stop_btn.setMaximumSize(30, 30)
            stop_btn.clicked.connect(lambda checked, cid=container_id: self.stop_container(cid))
            actions_layout.addWidget(stop_btn)
            
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.containers_table.setCellWidget(row, 5, actions_widget)
        
        # Update system resources
        system_status = self.manager.get_system_status()
        resources = system_status.get("system_resources", {})
        
        self.total_containers_label.setText(str(resources.get("total_containers", 0)))
        self.running_containers_label.setText(str(resources.get("running_containers", 0)))
        self.total_memory_label.setText(f"{resources.get('total_memory_mb', 0):.1f} MB")
        self.total_processes_label.setText(str(resources.get("total_processes", 0)))
    
    def switch_container(self, container_id: str):
        """Switch to container."""
        self.controller.switch_to_container(container_id)
    
    def pause_container(self, container_id: str):
        """Pause container."""
        self.controller.pause_container(container_id)
        QTimer.singleShot(1000, self.refresh_containers)  # Refresh after 1 second
    
    def resume_container(self, container_id: str):
        """Resume container."""
        def resume_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.manager.resume_container(container_id))
            finally:
                loop.close()
        
        thread = threading.Thread(target=resume_async, daemon=True)
        thread.start()
        QTimer.singleShot(1000, self.refresh_containers)  # Refresh after 1 second
    
    def stop_container(self, container_id: str):
        """Stop container."""
        self.controller.stop_container(container_id)
        QTimer.singleShot(2000, self.refresh_containers)  # Refresh after 2 seconds
    
    def stop_all_containers(self):
        """Stop all containers."""
        reply = QMessageBox.question(
            self, "Stop All Containers", 
            "Are you sure you want to stop all running containers?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.controller.stop_all_containers()
            QTimer.singleShot(3000, self.refresh_containers)  # Refresh after 3 seconds
    
    def refresh_all(self):
        """Refresh all tabs."""
        self.load_environments()
        self.refresh_containers()
    
    def apply_settings(self):
        """Apply settings changes."""
        # Apply system settings
        config_updates = {
            "auto_start": self.auto_start_check.isChecked(),
            "minimize_to_tray": self.minimize_tray_check.isChecked(),
            "show_notifications": self.show_notifications_check.isChecked(),
        }
        
        self.controller.update_config(**config_updates)
        
        # Apply auto-start setting
        self.controller.toggle_auto_start(self.auto_start_check.isChecked())
        
        QMessageBox.information(self, "Settings Applied", "Settings have been saved successfully!")
    
    def load_current_settings(self):
        """Load current settings into the UI."""
        config = self.controller.get_config()
        
        self.auto_start_check.setChecked(config.get("auto_start", True))
        self.minimize_tray_check.setChecked(config.get("minimize_to_tray", True))
        self.show_notifications_check.setChecked(config.get("show_notifications", True))
    
    def showEvent(self, event):
        """Handle dialog show event."""
        super().showEvent(event)
        self.load_current_settings()
        self.refresh_containers()