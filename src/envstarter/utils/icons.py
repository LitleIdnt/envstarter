"""
🎨 ICON RESOURCES FOR ENVSTARTER 🎨
Centralized icon management using the envstarter_icon.ico file.
"""

import os
from pathlib import Path
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor
from PyQt6.QtCore import QSize


def get_icon_path() -> str:
    """Get the path to the envstarter_icon.ico file."""
    # Try multiple possible locations
    possible_paths = [
        # Root directory
        Path(__file__).parent.parent.parent.parent / "envstarter_icon.ico",
        # Resources directory  
        Path(__file__).parent.parent.parent.parent / "resources" / "envstarter_icon.ico",
        # Current working directory
        Path.cwd() / "envstarter_icon.ico",
        Path.cwd() / "resources" / "envstarter_icon.ico",
        # Relative to this file
        Path(__file__).parent / "envstarter_icon.ico",
        Path(__file__).parent.parent / "envstarter_icon.ico"
    ]
    
    for path in possible_paths:
        if path.exists():
            print(f"✅ Found icon at: {path}")
            return str(path)
    
    print("⚠️ envstarter_icon.ico not found, using fallback icon")
    return None


def create_fallback_icon() -> QIcon:
    """Create a fallback icon if envstarter_icon.ico is not found."""
    pixmap = QPixmap(32, 32)
    pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background
    
    painter = QPainter(pixmap)
    
    # Draw a modern circular icon
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Main circle (gradient blue to green)
    painter.setBrush(QBrush(QColor(0, 120, 180)))  # Blue
    painter.drawEllipse(2, 2, 28, 28)
    
    # Inner highlight
    painter.setBrush(QBrush(QColor(0, 180, 120)))  # Green
    painter.drawEllipse(6, 6, 20, 20)
    
    # Center icon (play/start symbol)
    painter.setBrush(QBrush(QColor(255, 255, 255)))
    from PyQt6.QtGui import QPolygon
    from PyQt6.QtCore import QPoint
    
    # Play triangle
    play_triangle = QPolygon([
        QPoint(12, 10),
        QPoint(22, 16),
        QPoint(12, 22)
    ])
    painter.drawPolygon(play_triangle)
    
    painter.end()
    
    return QIcon(pixmap)


def get_app_icon() -> QIcon:
    """Get the main application icon."""
    icon_path = get_icon_path()
    
    if icon_path and os.path.exists(icon_path):
        try:
            icon = QIcon(icon_path)
            
            # Verify the icon loaded properly
            if not icon.isNull():
                print(f"🎨 Loaded application icon from: {icon_path}")
                return icon
            else:
                print("⚠️ Icon file exists but failed to load, using fallback")
        except Exception as e:
            print(f"⚠️ Error loading icon: {e}")
    
    # Fallback to programmatic icon
    return create_fallback_icon()


def get_tray_icon() -> QIcon:
    """Get the system tray icon."""
    # Use the same icon as the main app for consistency
    icon = get_app_icon()
    
    # Ensure we have multiple sizes for the tray
    if not icon.isNull():
        # The .ico file should contain multiple sizes, but let's ensure we have common tray sizes
        pixmap = icon.pixmap(QSize(16, 16))
        if not pixmap.isNull():
            print("🎨 Using envstarter_icon.ico for system tray")
            return icon
    
    # Fallback
    print("🎨 Using fallback icon for system tray")
    return create_fallback_icon()


def get_window_icon() -> QIcon:
    """Get icon for windows and dialogs."""
    return get_app_icon()


def apply_icon_to_app(app):
    """Apply the EnvStarter icon to the entire application."""
    try:
        icon = get_app_icon()
        app.setWindowIcon(icon)
        print("🎨 Applied EnvStarter icon to application")
    except Exception as e:
        print(f"⚠️ Failed to apply application icon: {e}")


def apply_icon_to_widget(widget):
    """Apply the EnvStarter icon to a specific widget/window."""
    try:
        icon = get_window_icon()
        widget.setWindowIcon(icon)
    except Exception as e:
        print(f"⚠️ Failed to apply widget icon: {e}")


# Icon sizes for different uses
ICON_SIZES = {
    'tray': (16, 16),
    'small': (24, 24),  
    'medium': (32, 32),
    'large': (48, 48),
    'extra_large': (64, 64)
}


def get_icon_pixmap(size: str = 'medium') -> QPixmap:
    """Get icon as pixmap with specified size."""
    icon = get_app_icon()
    width, height = ICON_SIZES.get(size, (32, 32))
    return icon.pixmap(QSize(width, height))