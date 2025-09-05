"""
Application scanner dialog for selecting installed applications.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QAbstractItemView, QLineEdit,
                            QProgressBar, QMessageBox, QSplitter,
                            QTextEdit, QCheckBox, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont, QIcon

from src.envstarter.utils.system_integration import SystemIntegration
from typing import List, Dict, Optional


class AppScanWorker(QThread):
    """Worker thread for scanning installed applications."""
    
    progress_updated = pyqtSignal(int, str)  # progress, status
    apps_found = pyqtSignal(list)  # list of applications
    scan_completed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.system_integration = SystemIntegration()
    
    def run(self):
        """Scan for installed applications."""
        try:
            self.progress_updated.emit(5, "Starting fast application scan...")
            
            # Use the new comprehensive scanning method with progress callback
            all_apps = self.system_integration.get_all_applications(
                progress_callback=lambda progress, status: self.progress_updated.emit(progress, status)
            )
            
            self.progress_updated.emit(90, "Sorting and filtering results...")
            
            # Sort by name
            all_apps.sort(key=lambda x: x["name"].lower())
            
            self.progress_updated.emit(100, f"Scan complete! Found {len(all_apps)} applications")
            self.apps_found.emit(all_apps)
            self.scan_completed.emit()
            
        except Exception as e:
            self.progress_updated.emit(0, f"Error during scan: {str(e)}")
            self.apps_found.emit([])
            self.scan_completed.emit()


class AppScannerDialog(QDialog):
    """Dialog for scanning and selecting installed applications."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.applications = []
        self.filtered_apps = []
        self.selected_application = None
        
        self.setWindowTitle("Select Installed Application")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        self.setup_ui()
        self.start_scan()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("Select an Installed Application")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Progress section
        self.progress_widget = QGroupBox("Scanning Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_status = QLabel("Initializing scan...")
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_status)
        
        self.progress_widget.setLayout(progress_layout)
        layout.addWidget(self.progress_widget)
        
        # Search and filter section
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Search:"))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Type to filter applications...")
        self.search_edit.textChanged.connect(self.filter_applications)
        filter_layout.addWidget(self.search_edit)
        
        self.show_all_checkbox = QCheckBox("Show all (including system apps)")
        self.show_all_checkbox.stateChanged.connect(self.filter_applications)
        filter_layout.addWidget(self.show_all_checkbox)
        
        layout.addLayout(filter_layout)
        
        # Main content area
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Applications table
        self.apps_table = QTableWidget()
        self.apps_table.setColumnCount(3)
        self.apps_table.setHorizontalHeaderLabels(["Application Name", "Location", "Install Path"])
        self.apps_table.horizontalHeader().setStretchLastSection(True)
        self.apps_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.apps_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.apps_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.apps_table.setAlternatingRowColors(True)
        self.apps_table.setSortingEnabled(True)
        self.apps_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.apps_table.itemDoubleClicked.connect(self.on_double_click)
        
        splitter.addWidget(self.apps_table)
        
        # Application details
        details_widget = QGroupBox("Application Details")
        details_layout = QVBoxLayout()
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumWidth(300)
        details_layout.addWidget(self.details_text)
        
        details_widget.setLayout(details_layout)
        splitter.addWidget(details_widget)
        
        splitter.setSizes([600, 300])
        layout.addWidget(splitter)
        
        # Status
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.rescan_button = QPushButton("Rescan")
        self.rescan_button.clicked.connect(self.start_scan)
        button_layout.addWidget(self.rescan_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        self.select_button = QPushButton("Select Application")
        self.select_button.clicked.connect(self.accept)
        self.select_button.setDefault(True)
        self.select_button.setEnabled(False)
        button_layout.addWidget(self.select_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def start_scan(self):
        """Start scanning for applications."""
        self.progress_widget.setVisible(True)
        self.apps_table.setEnabled(False)
        self.rescan_button.setEnabled(False)
        self.select_button.setEnabled(False)
        
        # Start worker thread
        self.scan_worker = AppScanWorker()
        self.scan_worker.progress_updated.connect(self.update_progress)
        self.scan_worker.apps_found.connect(self.populate_applications)
        self.scan_worker.scan_completed.connect(self.scan_finished)
        self.scan_worker.start()
    
    def update_progress(self, progress: int, status: str):
        """Update scan progress."""
        self.progress_bar.setValue(progress)
        self.progress_status.setText(status)
    
    def populate_applications(self, applications: List[Dict]):
        """Populate the applications table."""
        self.applications = applications
        self.filter_applications()
        
        self.status_label.setText(f"Found {len(self.applications)} applications")
    
    def filter_applications(self):
        """Filter applications based on search text and options."""
        search_text = self.search_edit.text().lower()
        show_all = self.show_all_checkbox.isChecked()
        
        # Filter applications
        self.filtered_apps = []
        
        for app in self.applications:
            # Skip system/Windows apps unless show_all is checked
            app_name = app["name"].lower()
            if not show_all:
                skip_keywords = [
                    "microsoft", "windows", "system", "update", "security",
                    "driver", "intel", "nvidia", "amd", "realtek", "hotfix",
                    "redistributable", "runtime", "framework", ".net"
                ]
                if any(keyword in app_name for keyword in skip_keywords):
                    if not any(good_keyword in app_name for good_keyword in 
                              ["office", "visual studio", "teams", "edge", "outlook"]):
                        continue
            
            # Apply search filter
            if search_text:
                if (search_text not in app_name and 
                    search_text not in app.get("path", "").lower()):
                    continue
            
            self.filtered_apps.append(app)
        
        # Update table
        self.apps_table.setRowCount(len(self.filtered_apps))
        
        for row, app in enumerate(self.filtered_apps):
            # Name
            name_item = QTableWidgetItem(app["name"])
            name_item.setData(Qt.ItemDataRole.UserRole, app)
            self.apps_table.setItem(row, 0, name_item)
            
            # Path
            path_item = QTableWidgetItem(app.get("path", ""))
            self.apps_table.setItem(row, 1, path_item)
            
            # Install location
            install_item = QTableWidgetItem(app.get("install_location", ""))
            self.apps_table.setItem(row, 2, install_item)
        
        # Update status
        if search_text:
            self.status_label.setText(f"Showing {len(self.filtered_apps)} of {len(self.applications)} applications (filtered)")
        else:
            self.status_label.setText(f"Showing {len(self.filtered_apps)} applications")
    
    def scan_finished(self):
        """Handle scan completion."""
        self.progress_widget.setVisible(False)
        self.apps_table.setEnabled(True)
        self.rescan_button.setEnabled(True)
        
        if len(self.applications) == 0:
            QMessageBox.information(self, "No Applications Found", 
                                  "No applications were found. This might be due to:\n"
                                  "• Limited registry permissions\n"
                                  "• No applications installed\n"
                                  "• Antivirus blocking registry access\n\n"
                                  "You can still browse for executables manually.")
    
    def on_selection_changed(self):
        """Handle table selection change."""
        selected_rows = self.apps_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            if row < len(self.filtered_apps):
                app = self.filtered_apps[row]
                self.selected_application = app
                self.select_button.setEnabled(True)
                self.update_details(app)
            else:
                self.selected_application = None
                self.select_button.setEnabled(False)
                self.details_text.clear()
        else:
            self.selected_application = None
            self.select_button.setEnabled(False)
            self.details_text.clear()
    
    def update_details(self, app: Dict):
        """Update application details display."""
        details = []
        details.append(f"<b>Name:</b> {app['name']}")
        
        if app.get("path"):
            details.append(f"<b>Executable:</b><br>{app['path']}")
        
        if app.get("install_location"):
            details.append(f"<b>Install Location:</b><br>{app['install_location']}")
        
        # Check if executable exists
        from pathlib import Path
        if app.get("path"):
            if Path(app["path"]).exists():
                details.append("<b>Status:</b> <span style='color: green'>✓ Available</span>")
            else:
                details.append("<b>Status:</b> <span style='color: red'>✗ File not found</span>")
        
        self.details_text.setHtml("<br><br>".join(details))
    
    def on_double_click(self, item):
        """Handle double-click to select application."""
        if self.selected_application:
            self.accept()
    
    def get_selected_application(self) -> Optional[Dict]:
        """Get the selected application."""
        return self.selected_application