"""
🎯 ENVIRONMENT HEADER WIDGET 🎯
MASSIVE VISIBLE HEADERS SHOWING WHICH ENVIRONMENT IS RUNNING!
"""

from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                            QFrame, QPushButton, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QRect
from PyQt6.QtGui import QFont, QColor, QPalette, QLinearGradient, QPainter, QBrush


class EnvironmentHeaderWidget(QFrame):
    """
    🚀 BIG VISIBLE ENVIRONMENT HEADER 🚀
    
    Shows the current environment name in a HUGE, UNMISSABLE header!
    """
    
    environment_switched = pyqtSignal(str)  # environment_name
    close_requested = pyqtSignal()
    
    def __init__(self, environment_name: str, container_id: str = None, parent=None):
        super().__init__(parent)
        self.environment_name = environment_name
        self.container_id = container_id
        self.setup_ui()
        self.start_animations()
        
    def setup_ui(self):
        """Set up the MASSIVE header UI."""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setMinimumHeight(100)
        self.setMaximumHeight(150)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(10)
        
        # Top bar with controls
        top_bar = QHBoxLayout()
        top_bar.setSpacing(15)
        
        # Environment label - HUGE AND VISIBLE
        env_label = QLabel(f"🚀 ENVIRONMENT: {self.environment_name.upper()} 🚀")
        env_font = QFont("Arial", 24, QFont.Weight.Bold)
        env_label.setFont(env_font)
        env_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Apply gradient effect
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #667eea, stop: 1 #764ba2);
                border: 3px solid #FFD700;
                border-radius: 15px;
                color: white;
            }
            QLabel {
                color: white;
                background: transparent;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid white;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border-color: #FFD700;
            }
        """)
        
        # Add drop shadow for depth
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)
        
        top_bar.addStretch()
        top_bar.addWidget(env_label)
        top_bar.addStretch()
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setMaximumSize(30, 30)
        close_btn.clicked.connect(self.close_requested.emit)
        close_btn.setToolTip("Hide environment header")
        top_bar.addWidget(close_btn)
        
        main_layout.addLayout(top_bar)
        
        # Status information
        status_layout = QHBoxLayout()
        status_layout.setSpacing(20)
        
        # Container ID
        if self.container_id:
            container_label = QLabel(f"📦 Container: {self.container_id}")
            container_label.setStyleSheet("font-size: 12px; font-weight: 500;")
            status_layout.addWidget(container_label)
        
        # Status indicator
        self.status_label = QLabel("🟢 RUNNING")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        
        # Time running
        self.time_label = QLabel("⏱️ Time: 00:00:00")
        self.time_label.setStyleSheet("font-size: 12px;")
        status_layout.addWidget(self.time_label)
        
        # Stats
        self.stats_label = QLabel("📊 Loading stats...")
        self.stats_label.setStyleSheet("font-size: 12px;")
        status_layout.addWidget(self.stats_label)
        
        status_layout.addStretch()
        main_layout.addLayout(status_layout)
        
        self.setLayout(main_layout)
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_stats)
        self.update_timer.start(1000)  # Update every second
        
        self.start_time = 0
        
    def start_animations(self):
        """Start attention-grabbing animations."""
        # Pulse animation
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self.pulse_effect)
        self.pulse_timer.start(2000)  # Pulse every 2 seconds
        
    def pulse_effect(self):
        """Create a pulsing effect."""
        # This would ideally use QPropertyAnimation for smooth pulsing
        # For now, we'll just update the border
        current_style = self.styleSheet()
        if "border: 3px solid #FFD700" in current_style:
            self.setStyleSheet(current_style.replace("border: 3px solid #FFD700", "border: 5px solid #FFA500"))
        else:
            self.setStyleSheet(current_style.replace("border: 5px solid #FFA500", "border: 3px solid #FFD700"))
            
    def update_stats(self):
        """Update the statistics display."""
        self.start_time += 1
        
        # Update time
        hours = self.start_time // 3600
        minutes = (self.start_time % 3600) // 60
        seconds = self.start_time % 60
        self.time_label.setText(f"⏱️ Time: {hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Try to get real stats
        try:
            if self.container_id:
                from src.envstarter.core.multi_environment_manager import get_multi_environment_manager
                manager = get_multi_environment_manager()
                containers = manager.get_all_containers()
                
                if self.container_id in containers:
                    info = containers[self.container_id]
                    stats = info.get("stats", {})
                    
                    processes = stats.get("total_processes", 0)
                    memory = stats.get("total_memory_mb", 0)
                    cpu = stats.get("total_cpu_percent", 0)
                    
                    self.stats_label.setText(
                        f"📊 Apps: {processes} | RAM: {memory:.0f}MB | CPU: {cpu:.1f}%"
                    )
                    
                    # Update status
                    state = info.get("state", "unknown")
                    if state == "running":
                        self.status_label.setText("🟢 RUNNING")
                    elif state == "paused":
                        self.status_label.setText("⏸️ PAUSED")
                    else:
                        self.status_label.setText("🔴 STOPPED")
                        
        except Exception as e:
            self.stats_label.setText(f"📊 Stats unavailable")
            
    def closeEvent(self, event):
        """Clean up when closing."""
        self.update_timer.stop()
        self.pulse_timer.stop()
        event.accept()


class FloatingEnvironmentHeader(QWidget):
    """
    🎯 FLOATING ENVIRONMENT HEADER 🎯
    
    A floating, always-on-top header that shows the current environment.
    Can be positioned at the top of the screen.
    """
    
    def __init__(self, environment_name: str, container_id: str = None):
        super().__init__()
        self.environment_name = environment_name
        self.container_id = container_id
        self.setup_ui()
        self.position_at_top()
        
    def setup_ui(self):
        """Set up the floating header."""
        # Window flags for always on top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Make it slightly transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Main widget
        self.header_widget = EnvironmentHeaderWidget(
            self.environment_name, 
            self.container_id,
            self
        )
        
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.header_widget)
        self.setLayout(layout)
        
        # Connect signals
        self.header_widget.close_requested.connect(self.hide)
        
        # Make draggable
        self.dragging = False
        self.drag_position = None
        
    def position_at_top(self):
        """Position the header at the top of the screen."""
        from PyQt6.QtWidgets import QApplication
        
        screen = QApplication.primaryScreen()
        if screen:
            screen_rect = screen.availableGeometry()
            
            # Position at top center
            self.resize(screen_rect.width() - 100, 120)
            self.move(50, 10)
            
    def mousePressEvent(self, event):
        """Handle mouse press for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging."""
        if event.buttons() == Qt.MouseButton.LeftButton and self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        self.dragging = False
        

class EnvironmentHeaderManager:
    """
    Manages environment headers for all running environments.
    """
    
    def __init__(self):
        self.headers = {}  # container_id -> FloatingEnvironmentHeader
        
    def show_header(self, environment_name: str, container_id: str):
        """Show a header for an environment."""
        if container_id not in self.headers:
            header = FloatingEnvironmentHeader(environment_name, container_id)
            self.headers[container_id] = header
            header.show()
            
    def hide_header(self, container_id: str):
        """Hide a header for an environment."""
        if container_id in self.headers:
            self.headers[container_id].hide()
            
    def remove_header(self, container_id: str):
        """Remove and destroy a header."""
        if container_id in self.headers:
            self.headers[container_id].close()
            del self.headers[container_id]
            
    def update_all(self):
        """Update all headers."""
        for header in self.headers.values():
            if header.isVisible():
                header.header_widget.update_stats()
                

# Global header manager
_header_manager = None

def get_header_manager() -> EnvironmentHeaderManager:
    """Get the global header manager."""
    global _header_manager
    if _header_manager is None:
        _header_manager = EnvironmentHeaderManager()
    return _header_manager


def show_environment_header(environment_name: str, container_id: str = None):
    """Quick function to show an environment header."""
    manager = get_header_manager()
    manager.show_header(environment_name, container_id or f"env_{environment_name.lower()}")