"""
🎮 MULTI-ENVIRONMENT DASHBOARD 🎮
The ultimate control center for managing multiple environment containers!

This is like VMware vCenter but for desktop environments - 
manage, monitor and switch between multiple running environments
like a hypervisor admin console!
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QProgressBar, QTabWidget,
    QGroupBox, QListWidget, QListWidgetItem, QTextEdit,
    QSplitter, QFrame, QGridLayout, QComboBox, QSpinBox,
    QCheckBox, QSlider, QMessageBox, QScrollArea, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QPainter
import asyncio
import threading
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from src.envstarter.core.models import Environment
from src.envstarter.core.multi_environment_manager import get_multi_environment_manager
from src.envstarter.core.concurrent_launcher import get_concurrent_launcher, LaunchMode, LaunchThread
from src.envstarter.core.simple_environment_container import EnvironmentState


class ContainerStatusCard(QFrame):
    """Visual card showing container status like a VM tile."""
    
    switch_requested = pyqtSignal(str)  # container_id
    stop_requested = pyqtSignal(str)   # container_id
    pause_requested = pyqtSignal(str)  # container_id
    resume_requested = pyqtSignal(str) # container_id
    
    def __init__(self, container_id: str, container_info: Dict):
        super().__init__()
        self.container_id = container_id
        self.container_info = container_info
        self.setup_ui()
        self.update_info(container_info)
    
    def setup_ui(self):
        """Set up the container status card UI."""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setMinimumSize(320, 180)
        self.setMaximumSize(400, 220)
        
        # Dynamic styling based on state
        self.setStyleSheet("""
            ContainerStatusCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 2px solid #e1e4e8;
                border-radius: 12px;
                margin: 8px;
                padding: 12px;
            }
            ContainerStatusCard:hover {
                border-color: #0366d6;
                box-shadow: 0 4px 8px rgba(3, 102, 214, 0.1);
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Header with environment name and status
        header_layout = QHBoxLayout()
        
        self.name_label = QLabel()
        name_font = QFont()
        name_font.setBold(True)
        name_font.setPointSize(14)
        self.name_label.setFont(name_font)
        header_layout.addWidget(self.name_label)
        
        header_layout.addStretch()
        
        self.status_badge = QLabel()
        self.status_badge.setStyleSheet("""
            QLabel {
                padding: 4px 8px;
                border-radius: 10px;
                font-size: 10px;
                font-weight: bold;
                text-align: center;
            }
        """)
        header_layout.addWidget(self.status_badge)
        
        layout.addLayout(header_layout)
        
        # Desktop info
        desktop_layout = QHBoxLayout()
        self.desktop_label = QLabel()
        self.desktop_label.setStyleSheet("color: #586069; font-size: 12px;")
        desktop_layout.addWidget(self.desktop_label)
        desktop_layout.addStretch()
        
        self.uptime_label = QLabel()
        self.uptime_label.setStyleSheet("color: #586069; font-size: 12px;")
        desktop_layout.addWidget(self.uptime_label)
        
        layout.addLayout(desktop_layout)
        
        # Resource stats
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #f6f8fa;
                border: 1px solid #d1d5da;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        stats_layout = QGridLayout()
        stats_layout.setSpacing(4)
        
        # Processes
        stats_layout.addWidget(QLabel("Processes:"), 0, 0)
        self.processes_label = QLabel()
        self.processes_label.setStyleSheet("font-weight: bold; color: #0366d6;")
        stats_layout.addWidget(self.processes_label, 0, 1)
        
        # Memory
        stats_layout.addWidget(QLabel("Memory:"), 1, 0)
        self.memory_label = QLabel()
        self.memory_label.setStyleSheet("font-weight: bold; color: #28a745;")
        stats_layout.addWidget(self.memory_label, 1, 1)
        
        # CPU
        stats_layout.addWidget(QLabel("CPU:"), 0, 2)
        self.cpu_label = QLabel()
        self.cpu_label.setStyleSheet("font-weight: bold; color: #fd7e14;")
        stats_layout.addWidget(self.cpu_label, 0, 3)
        
        # Desktop
        stats_layout.addWidget(QLabel("Desktop:"), 1, 2)
        self.desktop_idx_label = QLabel()
        self.desktop_idx_label.setStyleSheet("font-weight: bold; color: #6f42c1;")
        stats_layout.addWidget(self.desktop_idx_label, 1, 3)
        
        stats_frame.setLayout(stats_layout)
        layout.addWidget(stats_frame)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        
        self.switch_btn = QPushButton("🔄 Switch")
        self.switch_btn.setStyleSheet("""
            QPushButton {
                background-color: #0366d6;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #0256cc;
            }
        """)
        self.switch_btn.clicked.connect(lambda: self.switch_requested.emit(self.container_id))
        buttons_layout.addWidget(self.switch_btn)
        
        self.pause_btn = QPushButton("⏸️ Pause")
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #212529;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)
        self.pause_btn.clicked.connect(lambda: self.pause_requested.emit(self.container_id))
        buttons_layout.addWidget(self.pause_btn)
        
        self.resume_btn = QPushButton("▶️ Resume")
        self.resume_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.resume_btn.clicked.connect(lambda: self.resume_requested.emit(self.container_id))
        buttons_layout.addWidget(self.resume_btn)
        
        self.stop_btn = QPushButton("🛑 Stop")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.stop_btn.clicked.connect(lambda: self.stop_requested.emit(self.container_id))
        buttons_layout.addWidget(self.stop_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def update_info(self, container_info: Dict):
        """Update container information display."""
        self.container_info = container_info
        
        # Update labels
        env_name = container_info.get("environment_name", "Unknown")
        self.name_label.setText(f"🎯 {env_name}")
        
        state = container_info.get("state", "unknown")
        
        # Update status badge with color
        status_colors = {
            "running": ("#28a745", "white", "🟢 RUNNING"),
            "paused": ("#ffc107", "#212529", "⏸️ PAUSED"),
            "starting": ("#17a2b8", "white", "🚀 STARTING"),
            "stopping": ("#fd7e14", "white", "🛑 STOPPING"),
            "stopped": ("#6c757d", "white", "⭕ STOPPED"),
            "error": ("#dc3545", "white", "❌ ERROR")
        }
        
        bg_color, text_color, text = status_colors.get(state, ("#6c757d", "white", f"❓ {state.upper()}"))
        self.status_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                padding: 4px 8px;
                border-radius: 10px;
                font-size: 10px;
                font-weight: bold;
            }}
        """)
        self.status_badge.setText(text)
        
        # Update desktop info
        desktop_idx = container_info.get("desktop_index", -1)
        desktop_name = f"Desktop {desktop_idx}" if desktop_idx > 0 else "Default Desktop"
        self.desktop_label.setText(f"🖥️ {desktop_name}")
        
        # Update uptime
        uptime = container_info.get("uptime", 0)
        uptime_str = self.format_uptime(uptime)
        self.uptime_label.setText(f"⏱️ {uptime_str}")
        
        # Update stats
        stats = container_info.get("stats", {})
        self.processes_label.setText(str(stats.get("total_processes", 0)))
        self.memory_label.setText(f"{stats.get('total_memory_mb', 0):.1f} MB")
        self.cpu_label.setText(f"{stats.get('total_cpu_percent', 0):.1f}%")
        self.desktop_idx_label.setText(f"#{desktop_idx}" if desktop_idx > 0 else "N/A")
        
        # Update button states
        is_running = state == "running"
        is_paused = state == "paused"
        is_stopped = state in ["stopped", "error"]
        
        self.switch_btn.setEnabled(is_running)
        self.pause_btn.setEnabled(is_running)
        self.resume_btn.setEnabled(is_paused)
        self.stop_btn.setEnabled(not is_stopped)
        
        # Hide resume button if not paused
        self.resume_btn.setVisible(is_paused)
        self.pause_btn.setVisible(not is_paused)
    
    def format_uptime(self, seconds: int) -> str:
        """Format uptime in human readable format."""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"


class SystemResourcesWidget(QWidget):
    """Widget showing system-wide resource usage."""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the system resources UI."""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Header
        header_label = QLabel("🖥️ System Resources")
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(14)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Resource grid
        grid_layout = QGridLayout()
        
        # Containers overview
        grid_layout.addWidget(QLabel("Containers:"), 0, 0)
        self.containers_label = QLabel("0 total, 0 running")
        self.containers_label.setStyleSheet("font-weight: bold; color: #0366d6;")
        grid_layout.addWidget(self.containers_label, 0, 1)
        
        # Total processes
        grid_layout.addWidget(QLabel("Total Processes:"), 1, 0)
        self.processes_label = QLabel("0")
        self.processes_label.setStyleSheet("font-weight: bold; color: #28a745;")
        grid_layout.addWidget(self.processes_label, 1, 1)
        
        # Total memory
        grid_layout.addWidget(QLabel("Total Memory:"), 0, 2)
        self.memory_label = QLabel("0.0 MB")
        self.memory_label.setStyleSheet("font-weight: bold; color: #fd7e14;")
        grid_layout.addWidget(self.memory_label, 0, 3)
        
        # Total CPU
        grid_layout.addWidget(QLabel("Total CPU:"), 1, 2)
        self.cpu_label = QLabel("0.0%")
        self.cpu_label.setStyleSheet("font-weight: bold; color: #dc3545;")
        grid_layout.addWidget(self.cpu_label, 1, 3)
        
        layout.addLayout(grid_layout)
        
        # Resource bars
        self.memory_bar = QProgressBar()
        self.memory_bar.setRange(0, 100)
        self.memory_bar.setTextVisible(True)
        self.memory_bar.setFormat("Memory Usage: %p%")
        layout.addWidget(self.memory_bar)
        
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.cpu_bar.setTextVisible(True)
        self.cpu_bar.setFormat("CPU Usage: %p%")
        layout.addWidget(self.cpu_bar)
        
        # Active desktops
        self.desktops_label = QLabel("Active Desktops: None")
        self.desktops_label.setStyleSheet("color: #586069; font-size: 12px;")
        layout.addWidget(self.desktops_label)
        
        self.setLayout(layout)
    
    def update_resources(self, resources: Dict):
        """Update system resource display."""
        total_containers = resources.get("total_containers", 0)
        running_containers = resources.get("running_containers", 0)
        self.containers_label.setText(f"{total_containers} total, {running_containers} running")
        
        self.processes_label.setText(str(resources.get("total_processes", 0)))
        self.memory_label.setText(f"{resources.get('total_memory_mb', 0):.1f} MB")
        self.cpu_label.setText(f"{resources.get('total_cpu_percent', 0):.1f}%")
        
        # Update progress bars (assuming 8GB RAM and 100% CPU as max)
        memory_percent = min(resources.get("total_memory_mb", 0) / 8192 * 100, 100)
        self.memory_bar.setValue(int(memory_percent))
        
        cpu_percent = min(resources.get("total_cpu_percent", 0), 100)
        self.cpu_bar.setValue(int(cpu_percent))
        
        # Update active desktops
        active_desktops = resources.get("active_desktops", [])
        if active_desktops:
            desktop_str = ", ".join([f"#{d}" for d in sorted(active_desktops)])
            self.desktops_label.setText(f"Active Desktops: {desktop_str}")
        else:
            self.desktops_label.setText("Active Desktops: None")


class MultiEnvironmentDashboard(QWidget):
    """
    🎮 THE ULTIMATE MULTI-ENVIRONMENT DASHBOARD!
    
    This is the control center for managing multiple environment containers:
    - Visual overview of all running containers
    - Real-time resource monitoring
    - Quick actions (switch, pause, stop)
    - Batch launch capabilities
    - VM-like management interface
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Core components
        self.manager = get_multi_environment_manager()
        self.launcher = get_concurrent_launcher()  # Keep for queue functionality
        
        # VM manager for isolated environments
        from src.envstarter.core.vm_environment_manager import get_vm_environment_manager
        self.vm_manager = get_vm_environment_manager()
        
        # UI state
        self.container_cards: Dict[str, ContainerStatusCard] = {}
        self.refresh_timer = QTimer()
        
        self.setup_ui()
        self.setup_connections()
        self.setup_auto_refresh()
        
        # Initial load
        self.refresh_containers()
        
    def setup_ui(self):
        """Set up the dashboard UI."""
        self.setWindowTitle("🎮 Multi-Environment Dashboard")
        self.setMinimumSize(1200, 800)
        
        # Apply EnvStarter icon
        from src.envstarter.utils.icons import apply_icon_to_widget
        apply_icon_to_widget(self)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Environment Status Bar
        from src.envstarter.gui.environment_status_widget import EnvironmentStatusWidget
        self.env_status_widget = EnvironmentStatusWidget()
        self.env_status_widget.switch_requested.connect(self.switch_to_environment)
        main_layout.addWidget(self.env_status_widget)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🎮 Multi-Environment Dashboard")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Global actions
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_containers)
        header_layout.addWidget(self.refresh_btn)
        
        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.clicked.connect(self.show_settings)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #0366d6;
                color: white;
                border: 2px solid #0366d6;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0256cc;
                border-color: #0256cc;
            }
        """)
        header_layout.addWidget(self.settings_btn)
        
        self.quick_launch_btn = QPushButton("⚡ Quick Launch")
        self.quick_launch_btn.clicked.connect(self.show_quick_launch_dialog)
        header_layout.addWidget(self.quick_launch_btn)
        
        self.launch_multiple_btn = QPushButton("🚀 Launch Multiple")
        self.launch_multiple_btn.clicked.connect(self.show_batch_launch_dialog)
        header_layout.addWidget(self.launch_multiple_btn)
        
        self.launch_all_btn = QPushButton("🚀 Launch All")
        self.launch_all_btn.clicked.connect(self.launch_all_environments)
        header_layout.addWidget(self.launch_all_btn)
        
        self.stop_all_btn = QPushButton("🛑 Stop All")
        self.stop_all_btn.clicked.connect(self.stop_all_containers)
        header_layout.addWidget(self.stop_all_btn)
        
        main_layout.addLayout(header_layout)
        
        # Create tabbed interface
        self.tab_widget = QTabWidget()
        
        # Tab 1: Container Overview
        containers_tab = self.create_containers_tab()
        self.tab_widget.addTab(containers_tab, "🎯 Containers")
        
        # Tab 2: System Resources
        resources_tab = self.create_resources_tab()
        self.tab_widget.addTab(resources_tab, "📊 Resources")
        
        # Tab 3: Quick Launch
        quick_launch_tab = self.create_quick_launch_tab()
        self.tab_widget.addTab(quick_launch_tab, "⚡ Quick Launch")
        
        # Tab 4: Launch Queue
        queue_tab = self.create_queue_tab()
        self.tab_widget.addTab(queue_tab, "📋 Launch Queue")
        
        # Tab 5: Batch Operations
        batch_tab = self.create_batch_operations_tab()
        self.tab_widget.addTab(batch_tab, "🚀 Batch Operations")
        
        main_layout.addWidget(self.tab_widget)
        
        self.setLayout(main_layout)
    
    def create_containers_tab(self) -> QWidget:
        """Create the containers overview tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Container cards area
        self.containers_scroll = QScrollArea()
        self.containers_widget = QWidget()
        self.containers_layout = QGridLayout()
        self.containers_layout.setSpacing(12)
        
        self.containers_widget.setLayout(self.containers_layout)
        self.containers_scroll.setWidget(self.containers_widget)
        self.containers_scroll.setWidgetResizable(True)
        self.containers_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        layout.addWidget(self.containers_scroll)
        
        # Status area
        self.status_label = QLabel("No containers running")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                padding: 12px;
                color: #586069;
                font-size: 14px;
            }
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        tab.setLayout(layout)
        return tab
    
    def create_resources_tab(self) -> QWidget:
        """Create the system resources tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # System resources widget
        self.system_resources = SystemResourcesWidget()
        layout.addWidget(self.system_resources)
        
        # Resource history chart (placeholder)
        chart_label = QLabel("📈 Resource History (Coming Soon)")
        chart_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 2px dashed #d1d5da;
                border-radius: 8px;
                padding: 40px;
                color: #586069;
                font-size: 16px;
            }
        """)
        chart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_label.setMinimumHeight(300)
        layout.addWidget(chart_label)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_queue_tab(self) -> QWidget:
        """Create the launch queue tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Queue controls
        controls_layout = QHBoxLayout()
        
        self.launch_mode_combo = QComboBox()
        self.launch_mode_combo.addItems([
            "Concurrent", "Sequential", "Batched", "Staggered"
        ])
        controls_layout.addWidget(QLabel("Launch Mode:"))
        controls_layout.addWidget(self.launch_mode_combo)
        
        self.max_concurrent_spin = QSpinBox()
        self.max_concurrent_spin.setRange(1, 10)
        self.max_concurrent_spin.setValue(self.launcher.max_concurrent_launches)
        controls_layout.addWidget(QLabel("Max Concurrent:"))
        controls_layout.addWidget(self.max_concurrent_spin)
        
        controls_layout.addStretch()
        
        self.launch_queue_btn = QPushButton("🚀 Launch Queue")
        self.launch_queue_btn.clicked.connect(self.launch_queue)
        controls_layout.addWidget(self.launch_queue_btn)
        
        self.clear_queue_btn = QPushButton("🗑️ Clear Queue")
        self.clear_queue_btn.clicked.connect(self.clear_queue)
        controls_layout.addWidget(self.clear_queue_btn)
        
        layout.addLayout(controls_layout)
        
        # Queue status
        self.queue_status_label = QLabel("Queue: 0 items")
        layout.addWidget(self.queue_status_label)
        
        # Queue progress
        self.queue_progress = QProgressBar()
        self.queue_progress.setVisible(False)
        layout.addWidget(self.queue_progress)
        
        # Queue list (placeholder)
        self.queue_list = QListWidget()
        layout.addWidget(self.queue_list)
        
        tab.setLayout(layout)
        return tab
    
    def setup_connections(self):
        """Set up signal connections."""
        # Manager signals
        self.manager.container_started.connect(self.on_container_started)
        self.manager.container_stopped.connect(self.on_container_stopped)
        self.manager.container_switched.connect(self.on_container_switched)
        self.manager.resources_updated.connect(self.on_resources_updated)
        
        # Launcher signals
        self.launcher.queue_updated.connect(self.on_queue_updated)
        self.launcher.launch_started.connect(self.on_launch_started)
        self.launcher.launch_completed.connect(self.on_launch_completed)
        self.launcher.all_launches_completed.connect(self.on_all_launches_completed)
    
    def setup_auto_refresh(self):
        """Set up automatic refresh timer."""
        self.refresh_timer.timeout.connect(self.refresh_containers)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
    
    def refresh_containers(self):
        """Refresh container display."""
        try:
            containers = self.manager.get_all_containers()
            self.update_container_cards(containers)
            
            # Update status
            if containers:
                running_count = len([c for c in containers.values() if c["state"] == "running"])
                total_count = len(containers)
                self.status_label.setText(f"💼 {total_count} containers total, {running_count} running")
            else:
                self.status_label.setText("No containers running")
                
        except Exception as e:
            print(f"Error refreshing containers: {e}")
    
    def update_container_cards(self, containers: Dict[str, Dict]):
        """Update container status cards."""
        # Remove cards for containers that no longer exist
        for container_id in list(self.container_cards.keys()):
            if container_id not in containers:
                card = self.container_cards[container_id]
                self.containers_layout.removeWidget(card)
                card.deleteLater()
                del self.container_cards[container_id]
        
        # Update or create cards for existing containers
        row, col = 0, 0
        max_cols = 3  # 3 cards per row
        
        for container_id, container_info in containers.items():
            if container_id in self.container_cards:
                # Update existing card
                self.container_cards[container_id].update_info(container_info)
            else:
                # Create new card
                card = ContainerStatusCard(container_id, container_info)
                
                # Connect card signals
                card.switch_requested.connect(self.switch_to_container)
                card.stop_requested.connect(self.stop_container)
                card.pause_requested.connect(self.pause_container)
                card.resume_requested.connect(self.resume_container)
                
                self.container_cards[container_id] = card
            
            # Position the card
            self.containers_layout.addWidget(self.container_cards[container_id], row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def switch_to_container(self, container_id: str):
        """Switch to a container."""
        print(f"🔄 Switching to container: {container_id}")
        
        def switch_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(self.manager.switch_to_container(container_id))
            loop.close()
            return success
        
        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=switch_async)
        thread.daemon = True
        thread.start()
    
    def stop_container(self, container_id: str):
        """Stop a container."""
        reply = QMessageBox.question(
            self, "Stop Container", 
            f"Stop container '{container_id}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            print(f"🛑 Stopping container: {container_id}")
            
            def stop_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                success = loop.run_until_complete(self.manager.stop_environment_container(container_id))
                loop.close()
                return success
            
            thread = threading.Thread(target=stop_async)
            thread.daemon = True
            thread.start()
    
    def pause_container(self, container_id: str):
        """Pause a container."""
        def pause_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(self.manager.pause_container(container_id))
            loop.close()
            return success
        
        thread = threading.Thread(target=pause_async)
        thread.daemon = True
        thread.start()
    
    def resume_container(self, container_id: str):
        """Resume a container."""
        def resume_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(self.manager.resume_container(container_id))
            loop.close()
            return success
        
        thread = threading.Thread(target=resume_async)
        thread.daemon = True
        thread.start()
    
    def stop_all_containers(self):
        """Stop all containers."""
        containers = self.manager.get_all_containers()
        
        if not containers:
            return
        
        reply = QMessageBox.question(
            self, "Stop All Containers", 
            f"Stop all {len(containers)} containers?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            print("🛑 Stopping all containers...")
            
            def stop_all_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                count = loop.run_until_complete(self.manager.stop_all_containers())
                loop.close()
                print(f"✅ Stopped {count} containers")
            
            thread = threading.Thread(target=stop_all_async)
            thread.daemon = True
            thread.start()
    
    def show_batch_launch_dialog(self):
        """Show dialog for batch launching environments."""
        from src.envstarter.core.storage import ConfigManager
        
        dialog = QDialog(self)
        dialog.setWindowTitle("🚀 Batch Launch Environments")
        dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel("Select environments to launch simultaneously:")
        layout.addWidget(instructions)
        
        # Environment checkboxes
        config_manager = ConfigManager()
        environments = config_manager.get_environments()
        
        self.env_checkboxes = {}
        
        for env in environments:
            checkbox = QCheckBox(f"{env.name} ({len(env.applications)} apps, {len(env.websites)} sites)")
            self.env_checkboxes[env.name] = (checkbox, env)
            layout.addWidget(checkbox)
        
        if not environments:
            no_envs_label = QLabel("No environments available. Create some environments first!")
            layout.addWidget(no_envs_label)
        
        # Launch mode selection
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Launch Mode:"))
        
        mode_combo = QComboBox()
        mode_combo.addItems(["Concurrent", "Sequential", "Batched", "Staggered"])
        mode_layout.addWidget(mode_combo)
        layout.addLayout(mode_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        launch_btn = QPushButton("🚀 Launch Selected")
        launch_btn.clicked.connect(lambda: self.batch_launch_selected(dialog, mode_combo.currentText()))
        button_layout.addWidget(launch_btn)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def batch_launch_selected(self, dialog, mode_str: str):
        """Launch selected environments as isolated VMs."""
        selected_envs = []
        
        for checkbox, env in self.env_checkboxes.values():
            if checkbox.isChecked():
                selected_envs.append(env)
        
        if not selected_envs:
            QMessageBox.warning(self, "No Selection", "Please select at least one environment to launch.")
            return
        
        dialog.accept()
        
        print(f"💻 Launching {len(selected_envs)} environments as isolated VMs")
        
        # Launch environments as VM containers
        self.launch_environments(selected_envs)
        
        # Show success message
        QMessageBox.information(
            self, "VM Launch Started", 
            f"🚀 Started creating {len(selected_envs)} VM environments!\n\n"
            "Each environment will run on its own virtual desktop.\n"
            "You can switch between them like switching VMs."
        )
    
    def launch_queue(self):
        """Launch all items in the queue."""
        if self.launcher.is_launching:
            QMessageBox.warning(self, "Launch In Progress", "A launch is already in progress.")
            return
        
        mode_str = self.launch_mode_combo.currentText()
        mode_map = {
            "Concurrent": LaunchMode.CONCURRENT,
            "Sequential": LaunchMode.SEQUENTIAL, 
            "Batched": LaunchMode.BATCHED,
            "Staggered": LaunchMode.STAGGERED
        }
        
        launch_mode = mode_map.get(mode_str, LaunchMode.CONCURRENT)
        
        # Update launcher settings
        self.launcher.max_concurrent_launches = self.max_concurrent_spin.value()
        
        # Start launch in thread
        self.launch_thread = LaunchThread(self.launcher, launch_mode)
        self.launch_thread.finished_signal.connect(self.on_launch_thread_finished)
        self.launch_thread.error_signal.connect(self.on_launch_thread_error)
        self.launch_thread.start()
        
        # Show progress
        self.queue_progress.setVisible(True)
        self.launch_queue_btn.setEnabled(False)
        
        print(f"🚀 Starting queue launch with mode: {launch_mode.value}")
    
    def clear_queue(self):
        """Clear the launch queue."""
        self.launcher.clear_queue()
        self.queue_list.clear()
    
    def on_container_started(self, container_id: str):
        """Handle container started event."""
        print(f"✅ Container started: {container_id}")
        self.refresh_containers()
    
    def on_container_stopped(self, container_id: str):
        """Handle container stopped event."""
        print(f"🛑 Container stopped: {container_id}")
        self.refresh_containers()
    
    def on_container_switched(self, container_id: str):
        """Handle container switched event."""
        print(f"🔄 Switched to container: {container_id}")
    
    def on_resources_updated(self, resources: Dict):
        """Handle system resources update."""
        self.system_resources.update_resources(resources)
    
    def on_queue_updated(self, queue_size: int):
        """Handle queue update."""
        self.queue_status_label.setText(f"Queue: {queue_size} items")
    
    def on_launch_started(self, container_id: str, environment_name: str):
        """Handle launch started."""
        item = QListWidgetItem(f"🚀 Launching: {environment_name}")
        self.queue_list.addItem(item)
    
    def on_launch_completed(self, container_id: str, success: bool):
        """Handle launch completed."""
        status = "✅" if success else "❌"
        # Update the list item if needed
        
    def on_all_launches_completed(self, results: List[Dict]):
        """Handle all launches completed."""
        self.queue_progress.setVisible(False)
        self.launch_queue_btn.setEnabled(True)
        
        successful = len([r for r in results if r["success"]])
        total = len(results)
        
        QMessageBox.information(
            self, "Launch Complete",
            f"Batch launch completed!\n{successful}/{total} environments started successfully."
        )
        
        self.refresh_containers()
    
    def on_launch_thread_finished(self, results: List[Dict]):
        """Handle launch thread finished."""
        self.on_all_launches_completed(results)
    
    def on_launch_thread_error(self, error_message: str):
        """Handle launch thread error."""
        self.queue_progress.setVisible(False)
        self.launch_queue_btn.setEnabled(True)
        
        QMessageBox.critical(self, "Launch Error", f"Launch failed: {error_message}")
    
    def create_quick_launch_tab(self) -> QWidget:
        """Create the quick launch tab with all environments."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("⚡ Quick Launch Environments:"))
        header_layout.addStretch()
        
        # Search/filter
        from PyQt6.QtWidgets import QLineEdit
        self.quick_search = QLineEdit()
        self.quick_search.setPlaceholderText("Search environments...")
        self.quick_search.textChanged.connect(self.filter_quick_launch)
        header_layout.addWidget(self.quick_search)
        
        layout.addLayout(header_layout)
        
        # Environment list for quick launch
        self.quick_launch_list = QListWidget()
        self.quick_launch_list.setMinimumHeight(400)
        layout.addWidget(self.quick_launch_list)
        
        # Load environments
        self.load_quick_launch_environments()
        
        # Quick actions
        actions_layout = QHBoxLayout()
        
        launch_selected_btn = QPushButton("🚀 Launch Selected")
        launch_selected_btn.clicked.connect(self.launch_selected_environments)
        actions_layout.addWidget(launch_selected_btn)
        
        select_all_btn = QPushButton("✅ Select All")
        select_all_btn.clicked.connect(self.select_all_environments)
        actions_layout.addWidget(select_all_btn)
        
        select_none_btn = QPushButton("❌ Select None")
        select_none_btn.clicked.connect(self.select_no_environments)
        actions_layout.addWidget(select_none_btn)
        
        layout.addLayout(actions_layout)
        
        tab.setLayout(layout)
        return tab
    
    def create_batch_operations_tab(self) -> QWidget:
        """Create the batch operations tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Batch Launch Section
        batch_group = QGroupBox("🚀 Batch Launch Operations")
        batch_layout = QVBoxLayout()
        
        # Launch mode selection
        from PyQt6.QtWidgets import QRadioButton, QButtonGroup
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Launch Mode:"))
        
        self.launch_mode_group = QButtonGroup()
        
        concurrent_radio = QRadioButton("Concurrent")
        concurrent_radio.setChecked(True)
        self.launch_mode_group.addButton(concurrent_radio, 0)
        mode_layout.addWidget(concurrent_radio)
        
        sequential_radio = QRadioButton("Sequential")
        self.launch_mode_group.addButton(sequential_radio, 1)
        mode_layout.addWidget(sequential_radio)
        
        batched_radio = QRadioButton("Batched")
        self.launch_mode_group.addButton(batched_radio, 2)
        mode_layout.addWidget(batched_radio)
        
        staggered_radio = QRadioButton("Staggered")
        self.launch_mode_group.addButton(staggered_radio, 3)
        mode_layout.addWidget(staggered_radio)
        
        batch_layout.addLayout(mode_layout)
        
        # Batch size and delay
        settings_layout = QHBoxLayout()
        
        settings_layout.addWidget(QLabel("Batch Size:"))
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(1, 20)
        self.batch_size_spin.setValue(3)
        settings_layout.addWidget(self.batch_size_spin)
        
        settings_layout.addWidget(QLabel("Delay (ms):"))
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 10000)
        self.delay_spin.setValue(1000)
        self.delay_spin.setSuffix(" ms")
        settings_layout.addWidget(self.delay_spin)
        
        settings_layout.addStretch()
        batch_layout.addLayout(settings_layout)
        
        # Action buttons
        batch_actions_layout = QHBoxLayout()
        
        self.launch_all_btn2 = QPushButton("🚀 Launch All Environments")
        self.launch_all_btn2.clicked.connect(self.launch_all_environments)
        batch_actions_layout.addWidget(self.launch_all_btn2)
        
        self.stop_all_btn2 = QPushButton("🛑 Stop All Containers")
        self.stop_all_btn2.clicked.connect(self.stop_all_containers)
        batch_actions_layout.addWidget(self.stop_all_btn2)
        
        batch_layout.addLayout(batch_actions_layout)
        batch_group.setLayout(batch_layout)
        layout.addWidget(batch_group)
        
        # Container Operations Section
        container_group = QGroupBox("📦 Container Operations")
        container_layout = QVBoxLayout()
        
        container_actions_layout = QHBoxLayout()
        
        pause_all_btn = QPushButton("⏸️ Pause All Containers")
        pause_all_btn.clicked.connect(self.pause_all_containers)
        container_actions_layout.addWidget(pause_all_btn)
        
        resume_all_btn = QPushButton("▶️ Resume All Containers")
        resume_all_btn.clicked.connect(self.resume_all_containers)
        container_actions_layout.addWidget(resume_all_btn)
        
        container_layout.addLayout(container_actions_layout)
        container_group.setLayout(container_layout)
        layout.addWidget(container_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def load_quick_launch_environments(self):
        """Load environments into quick launch list."""
        from src.envstarter.core.enhanced_app_controller import EnhancedAppController
        from src.envstarter.core.storage import ConfigManager
        
        config_manager = ConfigManager()
        environments = config_manager.get_environments()
        
        self.quick_launch_list.clear()
        
        for env in environments:
            from PyQt6.QtCore import Qt
            item = QListWidgetItem(f"🎯 {env.name}")
            item.setData(Qt.ItemDataRole.UserRole, env)
            item.setCheckState(Qt.CheckState.Unchecked)
            
            # Add description as tooltip
            if env.description:
                item.setToolTip(f"{env.name}: {env.description}")
            
            self.quick_launch_list.addItem(item)
    
    def filter_quick_launch(self):
        """Filter quick launch environments."""
        filter_text = self.quick_search.text().lower()
        
        for i in range(self.quick_launch_list.count()):
            item = self.quick_launch_list.item(i)
            env = item.data(Qt.ItemDataRole.UserRole)
            
            # Show item if filter matches name or description
            visible = (filter_text in env.name.lower() or 
                      filter_text in (env.description or "").lower())
            item.setHidden(not visible)
    
    def launch_selected_environments(self):
        """Launch selected environments from quick launch."""
        selected_envs = []
        
        for i in range(self.quick_launch_list.count()):
            item = self.quick_launch_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                env = item.data(Qt.ItemDataRole.UserRole)
                selected_envs.append(env)
        
        if not selected_envs:
            QMessageBox.warning(self, "No Selection", "Please select environments to launch.")
            return
        
        # Launch selected environments
        self.launch_environments(selected_envs)
    
    def select_all_environments(self):
        """Select all visible environments."""
        for i in range(self.quick_launch_list.count()):
            item = self.quick_launch_list.item(i)
            if not item.isHidden():
                item.setCheckState(Qt.CheckState.Checked)
    
    def select_no_environments(self):
        """Deselect all environments."""
        for i in range(self.quick_launch_list.count()):
            item = self.quick_launch_list.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)
    
    def launch_all_environments(self):
        """Launch all available environments."""
        from src.envstarter.core.storage import ConfigManager
        
        config_manager = ConfigManager()
        environments = config_manager.get_environments()
        
        if not environments:
            QMessageBox.warning(self, "No Environments", "No environments available to launch.")
            return
        
        reply = QMessageBox.question(
            self, "Launch All Environments",
            f"Are you sure you want to launch all {len(environments)} environments?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.launch_environments(environments)
    
    def launch_environments(self, environments: List):
        """Launch multiple environments as isolated VM-like containers."""
        print(f"💻 Launching {len(environments)} environments as isolated VMs")
        
        # Import VM manager
        from src.envstarter.core.vm_environment_manager import get_vm_environment_manager
        vm_manager = get_vm_environment_manager()
        
        # Get launch mode for timing
        delay_ms = 1000  # Default delay between launches
        if hasattr(self, 'delay_spin') and self.delay_spin:
            delay_ms = self.delay_spin.value()
        
        # Launch environments asynchronously as isolated VMs
        async def launch_vm_environments():
            successful_launches = 0
            
            for i, env in enumerate(environments):
                try:
                    print(f"💻 Creating VM environment {i+1}/{len(environments)}: {env.name}")
                    
                    # Create VM environment with complete isolation
                    vm_env = await vm_manager.create_vm_environment(env)
                    
                    if vm_env:
                        print(f"✅ VM environment created: {env.name} (Desktop: {vm_env.desktop_id})")
                        successful_launches += 1
                        
                        # Emit container started signal for UI updates
                        self.manager.container_started.emit(vm_env.container_id)
                        
                        # Small delay between launches if multiple environments
                        if len(environments) > 1 and i < len(environments) - 1:
                            await asyncio.sleep(delay_ms / 1000.0)
                    else:
                        print(f"❌ Failed to create VM environment: {env.name}")
                        
                except Exception as e:
                    print(f"❌ Error creating VM environment {env.name}: {e}")
            
            print(f"✅ VM launch completed: {successful_launches}/{len(environments)} environments created")
            
            # Refresh containers display
            self.refresh_containers()
        
        # Run in thread to avoid blocking UI
        def run_vm_launch():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(launch_vm_environments())
            finally:
                loop.close()
        
        # Start VM launch thread
        import threading
        launch_thread = threading.Thread(target=run_vm_launch)
        launch_thread.daemon = True
        launch_thread.start()
            
            # Update UI
            QMessageBox.information(
                self, "Launch Started",
                f"Started launching {len(environments)} environments in {mode.value} mode."
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Launch Error", f"Failed to start launch: {str(e)}")
            print(f"❌ Launch error: {e}")
    
    def pause_all_containers(self):
        """Pause all running containers."""
        containers = self.manager.get_all_containers()
        running = [cid for cid, info in containers.items() if info["state"] == "running"]
        
        if not running:
            QMessageBox.information(self, "No Containers", "No running containers to pause.")
            return
        
        reply = QMessageBox.question(
            self, "Pause All Containers",
            f"Are you sure you want to pause {len(running)} running containers?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for container_id in running:
                try:
                    asyncio.create_task(self.manager.pause_container(container_id))
                except Exception as e:
                    print(f"Failed to pause container {container_id}: {e}")
            
            QMessageBox.information(self, "Containers Paused", f"Paused {len(running)} containers.")
            QTimer.singleShot(2000, self.refresh_containers)
    
    def resume_all_containers(self):
        """Resume all paused containers."""
        containers = self.manager.get_all_containers()
        paused = [cid for cid, info in containers.items() if info["state"] == "paused"]
        
        if not paused:
            QMessageBox.information(self, "No Containers", "No paused containers to resume.")
            return
        
        reply = QMessageBox.question(
            self, "Resume All Containers",
            f"Are you sure you want to resume {len(paused)} paused containers?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for container_id in paused:
                try:
                    def resume_async():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            loop.run_until_complete(self.manager.resume_container(container_id))
                        finally:
                            loop.close()
                    
                    thread = threading.Thread(target=resume_async, daemon=True)
                    thread.start()
                except Exception as e:
                    print(f"Failed to resume container {container_id}: {e}")
            
            QMessageBox.information(self, "Containers Resumed", f"Resumed {len(paused)} containers.")
            QTimer.singleShot(2000, self.refresh_containers)
    
    def show_settings(self):
        """Show the settings dialog."""
        try:
            from src.envstarter.gui.enhanced_settings_dialog import EnhancedSettingsDialog
            from src.envstarter.core.enhanced_app_controller import EnhancedAppController
            from src.envstarter.core.storage import ConfigManager
            
            # Create a temporary controller for settings if needed
            if not hasattr(self, 'controller'):
                self.controller = EnhancedAppController()
            
            # Create or show settings dialog
            if not hasattr(self, 'settings_dialog') or not self.settings_dialog:
                self.settings_dialog = EnhancedSettingsDialog(self.controller)
                self.settings_dialog.environment_changed.connect(self.on_environments_changed)
            
            self.settings_dialog.show()
            self.settings_dialog.raise_()
            self.settings_dialog.activateWindow()
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Settings Error", f"Failed to open settings: {str(e)}")
    
    def on_environments_changed(self):
        """Handle environment changes."""
        # Refresh the quick launch list and containers
        if hasattr(self, 'quick_launch_list'):
            self.load_quick_launch_environments()
        self.refresh_containers()
    
    def switch_to_environment(self, container_id: str):
        """Switch to the specified VM environment like switching between VMs."""
        try:
            from src.envstarter.core.vm_environment_manager import get_vm_environment_manager
            vm_manager = get_vm_environment_manager()
            
            # Use VM manager to switch between virtual desktops
            success = vm_manager.switch_to_vm_environment(container_id)
            
            if success:
                print(f"💻 Successfully switched to VM environment: {container_id}")
                # Also update multi-environment manager tracking
                from src.envstarter.core.enhanced_app_controller import EnhancedAppController
                controller = EnhancedAppController()
                controller.switch_to_container(container_id)
            else:
                print(f"⚠️ Failed to switch to VM environment: {container_id}")
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Switch Error", f"Failed to switch to VM environment: {container_id}")
                
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Switch Error", f"Failed to switch to environment: {str(e)}")
            print(f"❌ Error switching to environment: {e}")
    
    def show_quick_launch_dialog(self):
        """Show quick launch dialog."""
        # Switch to quick launch tab
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == "⚡ Quick Launch":
                self.tab_widget.setCurrentIndex(i)
                break
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.refresh_timer.stop()
        event.accept()