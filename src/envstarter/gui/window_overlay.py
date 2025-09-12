"""
🎯 WINDOW OVERLAY SYSTEM 🎯
ADDS VISIBLE ENVIRONMENT LABELS TO ALL APPLICATION WINDOWS!
"""

import sys
import time
import threading
import platform
from typing import Dict, List, Optional
from PyQt6.QtWidgets import QWidget, QLabel, QApplication, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import QFont, QPainter, QColor


class EnvironmentOverlay(QWidget):
    """
    OVERLAY THAT SHOWS ON TOP OF ANY APPLICATION WINDOW!
    Shows big environment name that can't be missed!
    """
    
    def __init__(self, environment_name: str, target_hwnd=None):
        super().__init__()
        self.environment_name = environment_name.upper()
        self.target_hwnd = target_hwnd
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the overlay widget."""
        # Window flags for overlay
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Make it semi-transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        
        # Environment label
        self.env_label = QLabel(f"{self.environment_name}")
        self.env_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.env_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(255, 69, 0, 180);
                border: 2px solid #FFD700;
                border-radius: 8px;
                padding: 4px 8px;
                text-align: center;
            }
        """)
        
        layout.addWidget(self.env_label)
        self.setLayout(layout)
        
        # Size and position
        self.setFixedSize(len(self.environment_name) * 12 + 40, 35)
        
    def position_on_window(self, x: int, y: int, width: int, height: int):
        """Position overlay on top-right corner of target window."""
        overlay_x = x + width - self.width() - 10
        overlay_y = y + 5
        
        self.move(overlay_x, overlay_y)
        

class WindowOverlayManager:
    """
    MANAGES OVERLAYS FOR ALL WINDOWS IN AN ENVIRONMENT!
    """
    
    def __init__(self, environment_name: str, container_id: str):
        self.environment_name = environment_name.upper()
        self.container_id = container_id
        self.overlays: Dict[int, EnvironmentOverlay] = {}  # hwnd -> overlay
        self.monitoring = False
        self.monitor_thread = None
        self.system = platform.system()
        self.tracked_pids: List[int] = []
        
    def start_monitoring(self, process_pids: List[int]):
        """Start monitoring windows and adding overlays."""
        print(f"🎯 Starting window overlay monitoring for: {self.environment_name}")
        
        self.tracked_pids = process_pids
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                if self.system == "Windows":
                    self._update_windows_overlays()
                elif self.system == "Linux":
                    self._update_linux_overlays()
                    
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                print(f"⚠️ Overlay monitoring error: {e}")
                
    def _update_windows_overlays(self):
        """Update overlays on Windows."""
        try:
            import ctypes
            from ctypes import wintypes
            
            user32 = ctypes.windll.user32
            current_windows = {}
            
            def enum_window_callback(hwnd, param):
                if user32.IsWindowVisible(hwnd):
                    # Get window PID
                    pid = wintypes.DWORD()
                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    
                    # Check if this window belongs to our environment
                    if pid.value in self.tracked_pids:
                        # Get window position
                        rect = wintypes.RECT()
                        user32.GetWindowRect(hwnd, ctypes.byref(rect))
                        
                        # Get window title to check if it's a real window
                        title_length = user32.GetWindowTextLengthW(hwnd)
                        if title_length > 0:
                            title_buffer = ctypes.create_unicode_buffer(title_length + 1)
                            user32.GetWindowTextW(hwnd, title_buffer, title_length + 1)
                            title = title_buffer.value
                            
                            if title and len(title.strip()) > 0:
                                current_windows[hwnd] = {
                                    'pid': pid.value,
                                    'title': title,
                                    'x': rect.left,
                                    'y': rect.top,
                                    'width': rect.right - rect.left,
                                    'height': rect.bottom - rect.top
                                }
                                
                return True
            
            # Enumerate all windows
            WNDENUMPROC = ctypes.WINFUNCTYPE(
                ctypes.c_bool,
                ctypes.POINTER(ctypes.c_int),
                ctypes.POINTER(ctypes.c_int)
            )
            user32.EnumWindows(WNDENUMPROC(enum_window_callback), 0)
            
            # Update overlays
            self._update_overlay_widgets(current_windows)
            
        except Exception as e:
            print(f"⚠️ Windows overlay update error: {e}")
            
    def _update_linux_overlays(self):
        """Update overlays on Linux."""
        try:
            import subprocess
            
            current_windows = {}
            
            for pid in self.tracked_pids:
                try:
                    # Get windows for this PID
                    result = subprocess.run(
                        f"xdotool search --pid {pid}",
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    
                    if result.stdout:
                        window_ids = result.stdout.strip().split('\n')
                        
                        for window_id in window_ids:
                            if window_id:
                                # Get window geometry
                                geo_result = subprocess.run(
                                    f"xdotool getwindowgeometry {window_id}",
                                    shell=True,
                                    capture_output=True,
                                    text=True
                                )
                                
                                if geo_result.stdout:
                                    lines = geo_result.stdout.split('\n')
                                    for line in lines:
                                        if 'Position:' in line:
                                            pos = line.split(':')[1].strip().split(',')
                                            x, y = int(pos[0]), int(pos[1])
                                        elif 'Geometry:' in line:
                                            size = line.split(':')[1].strip().split('x')
                                            width, height = int(size[0]), int(size[1])
                                            
                                            current_windows[int(window_id)] = {
                                                'pid': pid,
                                                'x': x,
                                                'y': y,
                                                'width': width,
                                                'height': height
                                            }
                                            
                except Exception as e:
                    continue
                    
            # Update overlays
            self._update_overlay_widgets(current_windows)
            
        except Exception as e:
            print(f"⚠️ Linux overlay update error: {e}")
            
    def _update_overlay_widgets(self, windows: Dict):
        """Update overlay widgets based on current windows."""
        # Remove overlays for windows that no longer exist
        for hwnd in list(self.overlays.keys()):
            if hwnd not in windows:
                overlay = self.overlays.pop(hwnd)
                overlay.close()
                
        # Add or update overlays for current windows
        for hwnd, window_info in windows.items():
            if hwnd not in self.overlays:
                # Create new overlay
                overlay = EnvironmentOverlay(self.environment_name, hwnd)
                self.overlays[hwnd] = overlay
                overlay.show()
                
            # Update overlay position
            overlay = self.overlays[hwnd]
            overlay.position_on_window(
                window_info['x'],
                window_info['y'], 
                window_info['width'],
                window_info['height']
            )
            
            # Ensure overlay is visible
            if not overlay.isVisible():
                overlay.show()
                
    def add_process(self, pid: int):
        """Add a new process to monitor."""
        if pid not in self.tracked_pids:
            self.tracked_pids.append(pid)
            print(f"📌 Added PID {pid} to overlay monitoring")
            
    def stop_monitoring(self):
        """Stop monitoring and close all overlays."""
        self.monitoring = False
        
        # Close all overlays
        for overlay in self.overlays.values():
            overlay.close()
        self.overlays.clear()
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
            
        print(f"🛑 Stopped overlay monitoring for {self.environment_name}")


# Global overlay managers for each environment
_overlay_managers: Dict[str, WindowOverlayManager] = {}

def create_overlay_manager(environment_name: str, container_id: str) -> WindowOverlayManager:
    """Create and return an overlay manager for an environment."""
    manager = WindowOverlayManager(environment_name, container_id)
    _overlay_managers[container_id] = manager
    return manager

def get_overlay_manager(container_id: str) -> Optional[WindowOverlayManager]:
    """Get overlay manager for a container."""
    return _overlay_managers.get(container_id)

def cleanup_overlay_manager(container_id: str):
    """Clean up overlay manager for a container."""
    if container_id in _overlay_managers:
        manager = _overlay_managers.pop(container_id)
        manager.stop_monitoring()