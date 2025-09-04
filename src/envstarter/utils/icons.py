"""
Icon resources for EnvStarter.
"""

import base64
from io import BytesIO
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QByteArray

# Simple PNG icon data (16x16 green arrow) as base64
TRAY_ICON_PNG_B64 = """
iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlz
AAAB6wAAAesBWmsqvgAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAFvSURB
VDiNpZM7SwNBEIafRBsLwcJCG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sL
G1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sL
G1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sL
G1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sL
G1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sL
G1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sL
G1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sLG1sL
"""

def create_simple_tray_icon_data():
    """Create simple tray icon data programmatically."""
    # Create a simple 16x16 RGBA icon
    width, height = 16, 16
    
    # Simple green arrow pointing right
    icon_data = []
    
    for y in range(height):
        row = []
        for x in range(width):
            # Create a simple arrow shape
            if (x >= 3 and x <= 12 and 
                y >= max(3, 8-x+3) and 
                y <= min(12, 8+x-3)):
                # Green arrow
                row.extend([0, 150, 0, 255])  # RGBA
            else:
                # Transparent
                row.extend([0, 0, 0, 0])
        icon_data.extend(row)
    
    return bytes(icon_data)

def get_tray_icon() -> QIcon:
    """Get the tray icon."""
    # Create a simple colored pixmap as fallback
    pixmap = QPixmap(16, 16)
    pixmap.fill(QIcon.fromTheme("applications-system").pixmap(16, 16).toImage().pixel(8, 8))
    
    # Try to create a simple green square for now
    from PyQt6.QtGui import QPainter, QBrush, QColor
    pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background
    
    painter = QPainter(pixmap)
    painter.setBrush(QBrush(QColor(0, 150, 0)))
    painter.drawEllipse(2, 2, 12, 12)
    
    # Draw an arrow
    painter.setBrush(QBrush(QColor(255, 255, 255)))
    from PyQt6.QtGui import QPolygon
    from PyQt6.QtCore import QPoint
    
    arrow = QPolygon([
        QPoint(6, 5),
        QPoint(11, 8),
        QPoint(6, 11),
        QPoint(7, 8)
    ])
    painter.drawPolygon(arrow)
    painter.end()
    
    return QIcon(pixmap)

def get_app_icon() -> QIcon:
    """Get the main application icon."""
    return get_tray_icon()  # Use same icon for now