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
from src.envstarter.core.environment_container import EnvironmentState


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
        self.launcher = get_concurrent_launcher()
        
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
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
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
        
        self.launch_multiple_btn = QPushButton("🚀 Launch Multiple")
        self.launch_multiple_btn.clicked.connect(self.show_batch_launch_dialog)
        header_layout.addWidget(self.launch_multiple_btn)
        
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
        
        # Tab 3: Launch Queue
        queue_tab = self.create_queue_tab()
        self.tab_widget.addTab(queue_tab, "📋 Launch Queue")
        
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
        """Launch selected environments in batch."""
        selected_envs = []
        
        for checkbox, env in self.env_checkboxes.values():
            if checkbox.isChecked():
                selected_envs.append(env)
        
        if not selected_envs:
            QMessageBox.warning(self, "No Selection", "Please select at least one environment to launch.")
            return
        
        dialog.accept()
        
        # Convert mode string to enum
        mode_map = {
            "Concurrent": LaunchMode.CONCURRENT,
            "Sequential": LaunchMode.SEQUENTIAL,
            "Batched": LaunchMode.BATCHED,
            "Staggered": LaunchMode.STAGGERED
        }
        
        launch_mode = mode_map.get(mode_str, LaunchMode.CONCURRENT)
        
        # Add environments to queue
        self.launcher.add_multiple_environments(selected_envs, switch_to_last=True, launch_mode=launch_mode)
        
        print(f"🚀 Added {len(selected_envs)} environments to launch queue")
        
        # Switch to queue tab
        self.tab_widget.setCurrentIndex(2)
    
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
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.refresh_timer.stop()
        event.accept()