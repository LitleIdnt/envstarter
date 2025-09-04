"""
Settings and environment management dialog for EnvStarter.
"""

import os
from pathlib import Path
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                            QWidget, QLabel, QPushButton, QListWidget, 
                            QListWidgetItem, QLineEdit, QTextEdit, QSpinBox,
                            QCheckBox, QFileDialog, QMessageBox, QFormLayout,
                            QGroupBox, QScrollArea, QFrame, QSplitter,
                            QComboBox, QTableWidget, QTableWidgetItem,
                            QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from src.envstarter.core.models import Environment, Application, Website
from src.envstarter.core.app_controller import AppController
from src.envstarter.utils.system_integration import SystemIntegration


class ApplicationEditWidget(QWidget):
    """Widget for editing application settings."""
    
    def __init__(self, app: Application = None):
        super().__init__()
        self.app = app or Application("", "")
        self.setup_ui()
        self.populate_fields()
    
    def setup_ui(self):
        """Set up the UI."""
        layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        layout.addRow("Name:", self.name_edit)
        
        # Path selection
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_for_executable)
        self.scan_button = QPushButton("Scan PC Apps")
        self.scan_button.clicked.connect(self.scan_for_applications)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_button)
        path_layout.addWidget(self.scan_button)
        layout.addRow("Path:", path_layout)
        
        self.arguments_edit = QLineEdit()
        layout.addRow("Arguments:", self.arguments_edit)
        
        self.working_dir_edit = QLineEdit()
        browse_wd_layout = QHBoxLayout()
        browse_wd_button = QPushButton("Browse...")
        browse_wd_button.clicked.connect(self.browse_for_directory)
        browse_wd_layout.addWidget(self.working_dir_edit)
        browse_wd_layout.addWidget(browse_wd_button)
        layout.addRow("Working Directory:", browse_wd_layout)
        
        self.wait_checkbox = QCheckBox("Wait for application to exit")
        layout.addRow("", self.wait_checkbox)
        
        self.setLayout(layout)
    
    def populate_fields(self):
        """Populate fields with application data."""
        self.name_edit.setText(self.app.name)
        self.path_edit.setText(self.app.path)
        self.arguments_edit.setText(self.app.arguments)
        self.working_dir_edit.setText(self.app.working_directory or "")
        self.wait_checkbox.setChecked(self.app.wait_for_exit)
    
    def get_application(self) -> Application:
        """Get application from form data."""
        self.app.name = self.name_edit.text()
        self.app.path = self.path_edit.text()
        self.app.arguments = self.arguments_edit.text()
        self.app.working_directory = self.working_dir_edit.text() or None
        self.app.wait_for_exit = self.wait_checkbox.isChecked()
        return self.app
    
    def browse_for_executable(self):
        """Browse for executable file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Application",
            "",
            "Executable Files (*.exe *.msi *.bat *.cmd);;All Files (*.*)"
        )
        if file_path:
            self.path_edit.setText(file_path)
            if not self.name_edit.text():
                self.name_edit.setText(Path(file_path).stem)
    
    def scan_for_applications(self):
        """Show installed applications scanner."""
        from src.envstarter.gui.app_scanner_dialog import AppScannerDialog
        
        dialog = AppScannerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_app = dialog.get_selected_application()
            if selected_app:
                self.path_edit.setText(selected_app["path"])
                if not self.name_edit.text():
                    self.name_edit.setText(selected_app["name"])
    
    def browse_for_directory(self):
        """Browse for working directory."""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Working Directory")
        if dir_path:
            self.working_dir_edit.setText(dir_path)


class WebsiteEditWidget(QWidget):
    """Widget for editing website settings."""
    
    def __init__(self, website: Website = None):
        super().__init__()
        self.website = website or Website("", "")
        self.setup_ui()
        self.populate_fields()
    
    def setup_ui(self):
        """Set up the UI."""
        layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        layout.addRow("Name:", self.name_edit)
        
        self.url_edit = QLineEdit()
        layout.addRow("URL:", self.url_edit)
        
        # Browser selection
        browser_layout = QHBoxLayout()
        self.browser_combo = QComboBox()
        self.browser_combo.addItem("System Default", "")
        self.browser_combo.addItem("Custom Browser...", "custom")
        browse_browser_button = QPushButton("Browse...")
        browse_browser_button.clicked.connect(self.browse_for_browser)
        browser_layout.addWidget(self.browser_combo)
        browser_layout.addWidget(browse_browser_button)
        layout.addRow("Browser:", browser_layout)
        
        self.browser_path_edit = QLineEdit()
        self.browser_path_edit.setVisible(False)
        layout.addRow("Browser Path:", self.browser_path_edit)
        
        self.new_tab_checkbox = QCheckBox("Open in new tab")
        self.new_tab_checkbox.setChecked(True)
        layout.addRow("", self.new_tab_checkbox)
        
        self.browser_combo.currentTextChanged.connect(self.on_browser_changed)
        
        self.setLayout(layout)
    
    def populate_fields(self):
        """Populate fields with website data."""
        self.name_edit.setText(self.website.name)
        self.url_edit.setText(self.website.url)
        self.new_tab_checkbox.setChecked(self.website.new_tab)
        
        if self.website.browser:
            self.browser_combo.setCurrentText("Custom Browser...")
            self.browser_path_edit.setText(self.website.browser)
            self.browser_path_edit.setVisible(True)
    
    def get_website(self) -> Website:
        """Get website from form data."""
        self.website.name = self.name_edit.text()
        self.website.url = self.url_edit.text()
        self.website.new_tab = self.new_tab_checkbox.isChecked()
        
        if self.browser_combo.currentData() == "custom":
            self.website.browser = self.browser_path_edit.text() or None
        else:
            self.website.browser = None
        
        return self.website
    
    def on_browser_changed(self):
        """Handle browser selection change."""
        is_custom = self.browser_combo.currentData() == "custom"
        self.browser_path_edit.setVisible(is_custom)
    
    def browse_for_browser(self):
        """Browse for browser executable."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Browser",
            "",
            "Executable Files (*.exe);;All Files (*.*)"
        )
        if file_path:
            self.browser_path_edit.setText(file_path)
            self.browser_combo.setCurrentText("Custom Browser...")
            self.browser_path_edit.setVisible(True)


class EnvironmentEditDialog(QDialog):
    """Dialog for editing environment settings."""
    
    def __init__(self, environment: Environment = None, controller: AppController = None):
        super().__init__()
        self.environment = environment or Environment("")
        self.controller = controller
        self.is_new = environment is None
        
        self.setWindowTitle("Edit Environment" if not self.is_new else "New Environment")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        
        self.setup_ui()
        self.populate_fields()
    
    def setup_ui(self):
        """Set up the UI."""
        layout = QVBoxLayout()
        
        # Basic info
        basic_group = QGroupBox("Environment Information")
        basic_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        basic_layout.addRow("Name:", self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        basic_layout.addRow("Description:", self.description_edit)
        
        self.startup_delay_spin = QSpinBox()
        self.startup_delay_spin.setRange(0, 300)
        self.startup_delay_spin.setSuffix(" seconds")
        basic_layout.addRow("Startup Delay:", self.startup_delay_spin)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Applications and websites
        content_tabs = QTabWidget()
        
        # Applications tab
        apps_widget = QWidget()
        apps_layout = QVBoxLayout()
        
        apps_header = QHBoxLayout()
        apps_label = QLabel("Applications")
        apps_label.setFont(QFont("", 12, QFont.Weight.Bold))
        add_app_button = QPushButton("Add Application")
        add_app_button.clicked.connect(self.add_application)
        apps_header.addWidget(apps_label)
        apps_header.addStretch()
        apps_header.addWidget(add_app_button)
        apps_layout.addLayout(apps_header)
        
        self.apps_table = QTableWidget()
        self.apps_table.setColumnCount(4)
        self.apps_table.setHorizontalHeaderLabels(["Name", "Path", "Arguments", "Actions"])
        self.apps_table.horizontalHeader().setStretchLastSection(False)
        self.apps_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.apps_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.apps_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.apps_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.apps_table.setColumnWidth(3, 180)  # Fixed width for action buttons
        self.apps_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.apps_table.setAlternatingRowColors(True)
        self.apps_table.setRowHeight(0, 50)  # Minimum row height for buttons
        # WCAG compliant table styling matching app colors
        self.apps_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d1d5da;
                background-color: #ffffff;
                alternate-background-color: #f6f8fa;
                border: 2px solid #d1d5da;
                border-radius: 8px;
                font-size: 14px;
                color: #24292e;
                selection-background-color: #0366d6;
                selection-color: white;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #e1e4e8;
                border-right: 1px solid #e1e4e8;
                min-height: 20px;
            }
            QTableWidget::item:selected {
                background-color: #0366d6;
                color: white;
            }
            QHeaderView::section {
                background-color: #24292e;
                padding: 12px 8px;
                border: none;
                border-right: 1px solid #444d56;
                font-weight: 600;
                font-size: 14px;
                color: #ffffff;
            }
            QHeaderView::section:last {
                border-right: none;
            }
        """)
        apps_layout.addWidget(self.apps_table)
        
        apps_widget.setLayout(apps_layout)
        content_tabs.addTab(apps_widget, "Applications")
        
        # Websites tab
        websites_widget = QWidget()
        websites_layout = QVBoxLayout()
        
        websites_header = QHBoxLayout()
        websites_label = QLabel("Websites")
        websites_label.setFont(QFont("", 12, QFont.Weight.Bold))
        add_website_button = QPushButton("Add Website")
        add_website_button.clicked.connect(self.add_website)
        websites_header.addWidget(websites_label)
        websites_header.addStretch()
        websites_header.addWidget(add_website_button)
        websites_layout.addLayout(websites_header)
        
        self.websites_table = QTableWidget()
        self.websites_table.setColumnCount(3)
        self.websites_table.setHorizontalHeaderLabels(["Name", "URL", "Actions"])
        self.websites_table.horizontalHeader().setStretchLastSection(False)
        self.websites_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.websites_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.websites_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.websites_table.setColumnWidth(2, 180)  # Fixed width for action buttons
        self.websites_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.websites_table.setAlternatingRowColors(True)
        # WCAG compliant table styling matching app colors
        self.websites_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d1d5da;
                background-color: #ffffff;
                alternate-background-color: #f6f8fa;
                border: 2px solid #d1d5da;
                border-radius: 8px;
                font-size: 14px;
                color: #24292e;
                selection-background-color: #0366d6;
                selection-color: white;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #e1e4e8;
                border-right: 1px solid #e1e4e8;
                min-height: 20px;
            }
            QTableWidget::item:selected {
                background-color: #0366d6;
                color: white;
            }
            QHeaderView::section {
                background-color: #24292e;
                padding: 12px 8px;
                border: none;
                border-right: 1px solid #444d56;
                font-weight: 600;
                font-size: 14px;
                color: #ffffff;
            }
            QHeaderView::section:last {
                border-right: none;
            }
        """)
        websites_layout.addWidget(self.websites_table)
        
        websites_widget.setLayout(websites_layout)
        content_tabs.addTab(websites_widget, "Websites")
        
        layout.addWidget(content_tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_environment)
        self.save_button.setDefault(True)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def populate_fields(self):
        """Populate fields with environment data."""
        self.name_edit.setText(self.environment.name)
        self.description_edit.setPlainText(self.environment.description)
        self.startup_delay_spin.setValue(self.environment.startup_delay)
        
        self.populate_applications_table()
        self.populate_websites_table()
    
    def populate_applications_table(self):
        """Populate applications table."""
        self.apps_table.setRowCount(len(self.environment.applications))
        
        for row, app in enumerate(self.environment.applications):
            # Set minimum row height for buttons
            self.apps_table.setRowHeight(row, 50)
            self.apps_table.setItem(row, 0, QTableWidgetItem(app.name))
            self.apps_table.setItem(row, 1, QTableWidgetItem(app.path))
            self.apps_table.setItem(row, 2, QTableWidgetItem(app.arguments))
            
            # Actions with WCAG compliant buttons
            actions_layout = QHBoxLayout()
            actions_layout.setSpacing(8)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            
            edit_button = QPushButton("✏️ Edit")
            edit_button.setMinimumHeight(32)  # WCAG touch target
            edit_button.setMinimumWidth(80)
            edit_button.setStyleSheet("""
                QPushButton {
                    background-color: #0366d6;
                    color: white;
                    border: 2px solid #0366d6;
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #0256cc;
                    border-color: #0256cc;
                }
                QPushButton:focus {
                    outline: 2px solid #0366d6;
                    outline-offset: 2px;
                }
            """)
            edit_button.clicked.connect(lambda checked, r=row: self.edit_application(r))
            actions_layout.addWidget(edit_button)
            
            remove_button = QPushButton("🗑️ Remove")
            remove_button.setMinimumHeight(32)  # WCAG touch target
            remove_button.setMinimumWidth(80)
            remove_button.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: 2px solid #dc3545;
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #c82333;
                    border-color: #bd2130;
                }
                QPushButton:focus {
                    outline: 2px solid #dc3545;
                    outline-offset: 2px;
                }
            """)
            remove_button.clicked.connect(lambda checked, r=row: self.remove_application(r))
            actions_layout.addWidget(remove_button)
            
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.apps_table.setCellWidget(row, 3, actions_widget)
    
    def populate_websites_table(self):
        """Populate websites table."""
        self.websites_table.setRowCount(len(self.environment.websites))
        
        for row, website in enumerate(self.environment.websites):
            # Set minimum row height for buttons  
            self.websites_table.setRowHeight(row, 50)
            self.websites_table.setItem(row, 0, QTableWidgetItem(website.name))
            self.websites_table.setItem(row, 1, QTableWidgetItem(website.url))
            
            # Actions with WCAG compliant buttons
            actions_layout = QHBoxLayout()
            actions_layout.setSpacing(8)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            
            edit_button = QPushButton("✏️ Edit")
            edit_button.setMinimumHeight(32)  # WCAG touch target
            edit_button.setMinimumWidth(80)
            edit_button.setStyleSheet("""
                QPushButton {
                    background-color: #0366d6;
                    color: white;
                    border: 2px solid #0366d6;
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #0256cc;
                    border-color: #0256cc;
                }
                QPushButton:focus {
                    outline: 2px solid #0366d6;
                    outline-offset: 2px;
                }
            """)
            edit_button.clicked.connect(lambda checked, r=row: self.edit_website(r))
            actions_layout.addWidget(edit_button)
            
            remove_button = QPushButton("🗑️ Remove")
            remove_button.setMinimumHeight(32)  # WCAG touch target
            remove_button.setMinimumWidth(80)
            remove_button.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: 2px solid #dc3545;
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #c82333;
                    border-color: #bd2130;
                }
                QPushButton:focus {
                    outline: 2px solid #dc3545;
                    outline-offset: 2px;
                }
            """)
            remove_button.clicked.connect(lambda checked, r=row: self.remove_website(r))
            actions_layout.addWidget(remove_button)
            
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.websites_table.setCellWidget(row, 2, actions_widget)
    
    def add_application(self):
        """Add a new application."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Application")
        dialog.setModal(True)
        dialog.resize(500, 300)
        
        layout = QVBoxLayout()
        edit_widget = ApplicationEditWidget()
        layout.addWidget(edit_widget)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        add_button = QPushButton("Add")
        add_button.clicked.connect(dialog.accept)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(add_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            app = edit_widget.get_application()
            if app.name and app.path:
                self.environment.applications.append(app)
                self.populate_applications_table()
    
    def edit_application(self, row: int):
        """Edit an application."""
        if row >= len(self.environment.applications):
            return
        
        app = self.environment.applications[row]
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Application")
        dialog.setModal(True)
        dialog.resize(500, 300)
        
        layout = QVBoxLayout()
        edit_widget = ApplicationEditWidget(app)
        layout.addWidget(edit_widget)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        save_button = QPushButton("Save")
        save_button.clicked.connect(dialog.accept)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_app = edit_widget.get_application()
            if updated_app.name and updated_app.path:
                self.environment.applications[row] = updated_app
                self.populate_applications_table()
    
    def remove_application(self, row: int):
        """Remove an application."""
        if row >= len(self.environment.applications):
            return
        
        app = self.environment.applications[row]
        reply = QMessageBox.question(
            self,
            "Remove Application",
            f"Are you sure you want to remove '{app.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.environment.applications.pop(row)
            self.populate_applications_table()
    
    def add_website(self):
        """Add a new website."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Website")
        dialog.setModal(True)
        dialog.resize(500, 200)
        
        layout = QVBoxLayout()
        edit_widget = WebsiteEditWidget()
        layout.addWidget(edit_widget)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        add_button = QPushButton("Add")
        add_button.clicked.connect(dialog.accept)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(add_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            website = edit_widget.get_website()
            if website.name and website.url:
                self.environment.websites.append(website)
                self.populate_websites_table()
    
    def edit_website(self, row: int):
        """Edit a website."""
        if row >= len(self.environment.websites):
            return
        
        website = self.environment.websites[row]
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Website")
        dialog.setModal(True)
        dialog.resize(500, 200)
        
        layout = QVBoxLayout()
        edit_widget = WebsiteEditWidget(website)
        layout.addWidget(edit_widget)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        save_button = QPushButton("Save")
        save_button.clicked.connect(dialog.accept)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_website = edit_widget.get_website()
            if updated_website.name and updated_website.url:
                self.environment.websites[row] = updated_website
                self.populate_websites_table()
    
    def remove_website(self, row: int):
        """Remove a website."""
        if row >= len(self.environment.websites):
            return
        
        website = self.environment.websites[row]
        reply = QMessageBox.question(
            self,
            "Remove Website",
            f"Are you sure you want to remove '{website.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.environment.websites.pop(row)
            self.populate_websites_table()
    
    def save_environment(self):
        """Save the environment."""
        # Validate
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Environment name is required.")
            return
        
        # Check for duplicate names (except for current environment)
        environments = self.controller.get_environments() if self.controller else []
        for env in environments:
            if (env.name.lower() == name.lower() and 
                (self.is_new or env.id != self.environment.id)):
                QMessageBox.warning(self, "Validation Error", 
                                  f"An environment named '{name}' already exists.")
                return
        
        # Update environment
        self.environment.name = name
        self.environment.description = self.description_edit.toPlainText().strip()
        self.environment.startup_delay = self.startup_delay_spin.value()
        
        # Validate that environment has at least one item
        if not self.environment.applications and not self.environment.websites:
            QMessageBox.warning(self, "Validation Error", 
                              "Environment must have at least one application or website.")
            return
        
        self.accept()


class SettingsDialog(QDialog):
    """Main settings dialog."""
    
    environment_changed = pyqtSignal()
    
    def __init__(self, controller: AppController):
        super().__init__()
        self.controller = controller
        self.system_integration = SystemIntegration()
        
        self.setWindowTitle("EnvStarter Settings")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Set up the UI."""
        layout = QVBoxLayout()
        
        tabs = QTabWidget()
        
        # General settings tab
        general_tab = self.create_general_tab()
        tabs.addTab(general_tab, "General")
        
        # Environments tab
        environments_tab = self.create_environments_tab()
        tabs.addTab(environments_tab, "Environments")
        
        # System integration tab
        system_tab = self.create_system_tab()
        tabs.addTab(system_tab, "System")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.save_and_close)
        ok_button.setDefault(True)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def create_general_tab(self) -> QWidget:
        """Create general settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Application settings
        app_group = QGroupBox("Application Settings")
        app_layout = QFormLayout()
        
        self.minimize_to_tray_checkbox = QCheckBox("Minimize to system tray instead of closing")
        app_layout.addRow("", self.minimize_to_tray_checkbox)
        
        self.show_notifications_checkbox = QCheckBox("Show notifications when launching environments")
        app_layout.addRow("", self.show_notifications_checkbox)
        
        app_group.setLayout(app_layout)
        layout.addWidget(app_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_environments_tab(self) -> QWidget:
        """Create environments management tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Manage Environments")
        header_label.setFont(QFont("", 14, QFont.Weight.Bold))
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        self.new_env_button = QPushButton("➕ New Environment")
        self.new_env_button.setMinimumHeight(44)  # WCAG touch target
        self.new_env_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: 2px solid #28a745;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #218838;
                border-color: #1e7e34;
                box-shadow: 0 2px 4px rgba(40, 167, 69, 0.2);
            }
            QPushButton:focus {
                outline: 3px solid #28a745;
                outline-offset: 2px;
            }
        """)
        self.new_env_button.clicked.connect(self.create_new_environment)
        header_layout.addWidget(self.new_env_button)
        
        layout.addLayout(header_layout)
        
        # Environments list
        self.environments_list = QListWidget()
        self.environments_list.setAlternatingRowColors(True)
        layout.addWidget(self.environments_list)
        
        # Environment actions
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        
        self.edit_env_button = QPushButton("✏️ Edit")
        self.edit_env_button.setMinimumHeight(40)  # WCAG touch target
        self.edit_env_button.setStyleSheet("""
            QPushButton {
                background-color: #0366d6;
                color: white;
                border: 2px solid #0366d6;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0256cc;
                border-color: #0256cc;
            }
            QPushButton:focus {
                outline: 2px solid #0366d6;
                outline-offset: 2px;
            }
            QPushButton:disabled {
                background-color: #e1e4e8;
                border-color: #e1e4e8;
                color: #6a737d;
            }
        """)
        self.edit_env_button.clicked.connect(self.edit_selected_environment)
        self.edit_env_button.setEnabled(False)
        actions_layout.addWidget(self.edit_env_button)
        
        self.duplicate_env_button = QPushButton("📋 Duplicate")
        self.duplicate_env_button.setMinimumHeight(40)  # WCAG touch target
        self.duplicate_env_button.setStyleSheet("""
            QPushButton {
                background-color: #6f42c1;
                color: white;
                border: 2px solid #6f42c1;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                min-width: 90px;
            }
            QPushButton:hover {
                background-color: #5a32a3;
                border-color: #5a32a3;
            }
            QPushButton:focus {
                outline: 2px solid #6f42c1;
                outline-offset: 2px;
            }
            QPushButton:disabled {
                background-color: #e1e4e8;
                border-color: #e1e4e8;
                color: #6a737d;
            }
        """)
        self.duplicate_env_button.clicked.connect(self.duplicate_selected_environment)
        self.duplicate_env_button.setEnabled(False)
        actions_layout.addWidget(self.duplicate_env_button)
        
        self.delete_env_button = QPushButton("🗑️ Delete")
        self.delete_env_button.setMinimumHeight(40)  # WCAG touch target
        self.delete_env_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: 2px solid #dc3545;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #c82333;
                border-color: #bd2130;
            }
            QPushButton:focus {
                outline: 2px solid #dc3545;
                outline-offset: 2px;
            }
            QPushButton:disabled {
                background-color: #e1e4e8;
                border-color: #e1e4e8;
                color: #6a737d;
            }
        """)
        self.delete_env_button.clicked.connect(self.delete_selected_environment)
        self.delete_env_button.setEnabled(False)
        actions_layout.addWidget(self.delete_env_button)
        
        layout.addLayout(actions_layout)
        
        # Connect signals
        self.environments_list.itemSelectionChanged.connect(self.on_environment_selection_changed)
        self.environments_list.itemDoubleClicked.connect(self.edit_selected_environment)
        
        widget.setLayout(layout)
        return widget
    
    def create_system_tab(self) -> QWidget:
        """Create system integration tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Startup settings
        startup_group = QGroupBox("Startup Settings")
        startup_layout = QFormLayout()
        
        self.auto_start_checkbox = QCheckBox("Start with Windows")
        startup_layout.addRow("", self.auto_start_checkbox)
        
        startup_group.setLayout(startup_layout)
        layout.addWidget(startup_group)
        
        # Desktop integration
        desktop_group = QGroupBox("Desktop Integration")
        desktop_layout = QVBoxLayout()
        
        shortcut_layout = QHBoxLayout()
        shortcut_label = QLabel("Desktop shortcut:")
        self.create_shortcut_button = QPushButton("Create Shortcut")
        self.create_shortcut_button.clicked.connect(self.create_desktop_shortcut)
        self.remove_shortcut_button = QPushButton("Remove Shortcut")
        self.remove_shortcut_button.clicked.connect(self.remove_desktop_shortcut)
        shortcut_layout.addWidget(shortcut_label)
        shortcut_layout.addStretch()
        shortcut_layout.addWidget(self.create_shortcut_button)
        shortcut_layout.addWidget(self.remove_shortcut_button)
        
        desktop_layout.addLayout(shortcut_layout)
        desktop_group.setLayout(desktop_layout)
        layout.addWidget(desktop_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def load_settings(self):
        """Load current settings."""
        config = self.controller.get_config()
        
        # General settings
        self.minimize_to_tray_checkbox.setChecked(config.get("minimize_to_tray", True))
        self.show_notifications_checkbox.setChecked(config.get("show_notifications", True))
        
        # System settings
        self.auto_start_checkbox.setChecked(self.system_integration.is_in_startup())
        
        # Load environments
        self.load_environments()
    
    def load_environments(self):
        """Load environments into the list."""
        self.environments_list.clear()
        environments = self.controller.get_environments()
        
        for env in environments:
            item_text = f"{env.name}"
            if env.description:
                item_text += f" - {env.description}"
            
            item_text += f" ({env.get_total_items()} items)"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, env.id)
            self.environments_list.addItem(item)
    
    def on_environment_selection_changed(self):
        """Handle environment selection change."""
        has_selection = bool(self.environments_list.selectedItems())
        self.edit_env_button.setEnabled(has_selection)
        self.duplicate_env_button.setEnabled(has_selection)
        self.delete_env_button.setEnabled(has_selection)
    
    def create_new_environment(self):
        """Create a new environment."""
        dialog = EnvironmentEditDialog(None, self.controller)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            success = self.controller.add_environment(dialog.environment)
            if success:
                self.load_environments()
                self.environment_changed.emit()
            else:
                QMessageBox.warning(self, "Error", "Failed to create environment.")
    
    def edit_selected_environment(self):
        """Edit the selected environment."""
        selected_items = self.environments_list.selectedItems()
        if not selected_items:
            return
        
        env_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        environment = self.controller.get_environment_by_id(env_id)
        
        if environment:
            dialog = EnvironmentEditDialog(environment, self.controller)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                success = self.controller.update_environment(dialog.environment)
                if success:
                    self.load_environments()
                    self.environment_changed.emit()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update environment.")
    
    def duplicate_selected_environment(self):
        """Duplicate the selected environment."""
        selected_items = self.environments_list.selectedItems()
        if not selected_items:
            return
        
        env_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        environment = self.controller.get_environment_by_id(env_id)
        
        if environment:
            # Create a copy
            new_env = Environment.from_dict(environment.to_dict())
            new_env.name += " (Copy)"
            new_env.id = ""  # Reset ID to generate new one
            
            dialog = EnvironmentEditDialog(new_env, self.controller)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                success = self.controller.add_environment(dialog.environment)
                if success:
                    self.load_environments()
                    self.environment_changed.emit()
                else:
                    QMessageBox.warning(self, "Error", "Failed to duplicate environment.")
    
    def delete_selected_environment(self):
        """Delete the selected environment."""
        selected_items = self.environments_list.selectedItems()
        if not selected_items:
            return
        
        env_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        environment = self.controller.get_environment_by_id(env_id)
        
        if environment:
            reply = QMessageBox.question(
                self,
                "Delete Environment",
                f"Are you sure you want to delete the environment '{environment.name}'?\n\n"
                "This action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                success = self.controller.delete_environment(env_id)
                if success:
                    self.load_environments()
                    self.environment_changed.emit()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete environment.")
    
    def create_desktop_shortcut(self):
        """Create desktop shortcut."""
        success = self.system_integration.create_desktop_shortcut()
        if success:
            QMessageBox.information(self, "Success", "Desktop shortcut created successfully.")
        else:
            QMessageBox.warning(self, "Error", "Failed to create desktop shortcut.")
    
    def remove_desktop_shortcut(self):
        """Remove desktop shortcut."""
        success = self.system_integration.remove_desktop_shortcut()
        if success:
            QMessageBox.information(self, "Success", "Desktop shortcut removed successfully.")
        else:
            QMessageBox.warning(self, "Error", "Failed to remove desktop shortcut.")
    
    def apply_settings(self):
        """Apply settings without closing."""
        # General settings
        self.controller.update_config(
            minimize_to_tray=self.minimize_to_tray_checkbox.isChecked(),
            show_notifications=self.show_notifications_checkbox.isChecked()
        )
        
        # System integration
        auto_start_enabled = self.auto_start_checkbox.isChecked()
        current_auto_start = self.system_integration.is_in_startup()
        
        if auto_start_enabled != current_auto_start:
            success = self.controller.toggle_auto_start(auto_start_enabled)
            if not success:
                QMessageBox.warning(self, "Error", "Failed to update auto-start setting.")
                self.auto_start_checkbox.setChecked(current_auto_start)
    
    def save_and_close(self):
        """Save settings and close dialog."""
        self.apply_settings()
        self.accept()