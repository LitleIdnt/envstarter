"""
🎨 THEME MANAGER 🎨
Complete light/dark mode theme system for Enhanced EnvStarter!
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPalette, QColor
from typing import Dict, Optional
import json
from pathlib import Path


class ThemeManager(QObject):
    """
    🎨 ADVANCED THEME MANAGER
    
    Provides complete light/dark mode theming with:
    - Dynamic theme switching
    - Custom color palettes
    - Component-specific styling
    - Theme persistence
    """
    
    theme_changed = pyqtSignal(str)  # theme_name
    
    def __init__(self):
        super().__init__()
        self.current_theme = "light"
        self.themes = self._load_themes()
        self.app_instance = None
    
    def _load_themes(self) -> Dict:
        """Load theme definitions."""
        return {
            "light": {
                "name": "Light Mode",
                "colors": {
                    # Base colors
                    "primary": "#0366d6",
                    "secondary": "#6f42c1", 
                    "success": "#28a745",
                    "danger": "#dc3545",
                    "warning": "#ffc107",
                    "info": "#17a2b8",
                    
                    # Background colors
                    "background": "#ffffff",
                    "surface": "#f8f9fa",
                    "card": "#ffffff",
                    "sidebar": "#f6f8fa",
                    
                    # Text colors
                    "text_primary": "#24292e",
                    "text_secondary": "#586069",
                    "text_muted": "#6c757d",
                    "text_inverse": "#ffffff",
                    
                    # Border colors
                    "border": "#e1e4e8",
                    "border_light": "#f0f0f0",
                    "border_dark": "#d1d5da",
                    
                    # Interactive colors
                    "hover": "#f6f8fa",
                    "active": "#e1e4e8",
                    "focus": "#0366d6",
                    "disabled": "#e9ecef",
                    
                    # Status colors
                    "running": "#28a745",
                    "stopped": "#dc3545",
                    "paused": "#ffc107",
                    "loading": "#17a2b8"
                },
                "styles": {
                    "window": """
                        QWidget {
                            background-color: {background};
                            color: {text_primary};
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        }
                    """,
                    "button": """
                        QPushButton {
                            background-color: {primary};
                            color: {text_inverse};
                            border: 2px solid {primary};
                            border-radius: 6px;
                            padding: 8px 16px;
                            font-size: 12px;
                            font-weight: 600;
                            min-height: 36px;
                        }
                        QPushButton:hover {
                            background-color: {primary};
                            opacity: 0.9;
                        }
                        QPushButton:pressed {
                            background-color: {primary};
                            opacity: 0.8;
                        }
                        QPushButton:disabled {
                            background-color: {disabled};
                            color: {text_muted};
                            border-color: {disabled};
                        }
                    """,
                    "card": """
                        QFrame {
                            background-color: {card};
                            border: 1px solid {border};
                            border-radius: 8px;
                            padding: 16px;
                        }
                        QFrame:hover {
                            border-color: {primary};
                            background-color: {hover};
                        }
                    """,
                    "list": """
                        QListWidget {
                            background-color: {background};
                            border: 1px solid {border};
                            border-radius: 6px;
                            padding: 8px;
                        }
                        QListWidget::item {
                            background-color: {card};
                            border: 1px solid {border_light};
                            border-radius: 4px;
                            padding: 8px;
                            margin: 2px;
                        }
                        QListWidget::item:selected {
                            background-color: {primary};
                            color: {text_inverse};
                        }
                        QListWidget::item:hover {
                            background-color: {hover};
                            border-color: {primary};
                        }
                    """,
                    "text_input": """
                        QLineEdit, QTextEdit {
                            background-color: {background};
                            border: 2px solid {border};
                            border-radius: 6px;
                            padding: 8px;
                            color: {text_primary};
                            font-size: 14px;
                        }
                        QLineEdit:focus, QTextEdit:focus {
                            border-color: {primary};
                            outline: none;
                        }
                    """,
                    "environment_details": """
                        QLabel {
                            background-color: {surface};
                            border: 1px solid {border};
                            border-radius: 8px;
                            padding: 16px;
                            color: {text_primary};
                            font-size: 14px;
                            line-height: 1.5;
                        }
                    """
                }
            },
            "dark": {
                "name": "Dark Mode",
                "colors": {
                    # Base colors
                    "primary": "#58a6ff",
                    "secondary": "#a5a5f5",
                    "success": "#3fb950", 
                    "danger": "#f85149",
                    "warning": "#d29922",
                    "info": "#79c0ff",
                    
                    # Background colors
                    "background": "#0d1117",
                    "surface": "#161b22",
                    "card": "#21262d",
                    "sidebar": "#161b22",
                    
                    # Text colors
                    "text_primary": "#f0f6fc",
                    "text_secondary": "#8b949e",
                    "text_muted": "#6e7681",
                    "text_inverse": "#0d1117",
                    
                    # Border colors
                    "border": "#30363d",
                    "border_light": "#21262d",
                    "border_dark": "#30363d",
                    
                    # Interactive colors
                    "hover": "#262c36",
                    "active": "#30363d",
                    "focus": "#58a6ff",
                    "disabled": "#21262d",
                    
                    # Status colors
                    "running": "#3fb950",
                    "stopped": "#f85149",
                    "paused": "#d29922",
                    "loading": "#79c0ff"
                },
                "styles": {
                    "window": """
                        QWidget {
                            background-color: {background};
                            color: {text_primary};
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        }
                    """,
                    "button": """
                        QPushButton {
                            background-color: {primary};
                            color: {text_inverse};
                            border: 2px solid {primary};
                            border-radius: 6px;
                            padding: 8px 16px;
                            font-size: 12px;
                            font-weight: 600;
                            min-height: 36px;
                        }
                        QPushButton:hover {
                            background-color: {primary};
                            opacity: 0.9;
                        }
                        QPushButton:pressed {
                            background-color: {primary};
                            opacity: 0.8;
                        }
                        QPushButton:disabled {
                            background-color: {disabled};
                            color: {text_muted};
                            border-color: {disabled};
                        }
                    """,
                    "card": """
                        QFrame {
                            background-color: {card};
                            border: 1px solid {border};
                            border-radius: 8px;
                            padding: 16px;
                        }
                        QFrame:hover {
                            border-color: {primary};
                            background-color: {hover};
                        }
                    """,
                    "list": """
                        QListWidget {
                            background-color: {background};
                            border: 1px solid {border};
                            border-radius: 6px;
                            padding: 8px;
                        }
                        QListWidget::item {
                            background-color: {card};
                            border: 1px solid {border_light};
                            border-radius: 4px;
                            padding: 8px;
                            margin: 2px;
                        }
                        QListWidget::item:selected {
                            background-color: {primary};
                            color: {text_inverse};
                        }
                        QListWidget::item:hover {
                            background-color: {hover};
                            border-color: {primary};
                        }
                    """,
                    "text_input": """
                        QLineEdit, QTextEdit {
                            background-color: {surface};
                            border: 2px solid {border};
                            border-radius: 6px;
                            padding: 8px;
                            color: {text_primary};
                            font-size: 14px;
                        }
                        QLineEdit:focus, QTextEdit:focus {
                            border-color: {primary};
                            outline: none;
                        }
                    """,
                    "environment_details": """
                        QLabel {
                            background-color: {surface};
                            border: 1px solid {border};
                            border-radius: 8px;
                            padding: 16px;
                            color: {text_primary};
                            font-size: 14px;
                            line-height: 1.5;
                        }
                    """
                }
            }
        }
    
    def set_application_instance(self, app: QApplication):
        """Set the QApplication instance for theme management."""
        self.app_instance = app
    
    def get_available_themes(self) -> Dict[str, str]:
        """Get available theme names and display names."""
        return {key: theme["name"] for key, theme in self.themes.items()}
    
    def set_theme(self, theme_name: str):
        """Set the current theme and apply it to the application."""
        if theme_name not in self.themes:
            print(f"⚠️ Theme '{theme_name}' not found, using 'light'")
            theme_name = "light"
        
        self.current_theme = theme_name
        self._apply_theme()
        self.theme_changed.emit(theme_name)
        
        print(f"🎨 Theme switched to: {self.themes[theme_name]['name']}")
    
    def get_current_theme(self) -> str:
        """Get the current theme name."""
        return self.current_theme
    
    def _apply_theme(self):
        """Apply the current theme to the application."""
        if not self.app_instance:
            print("⚠️ No application instance set for theming")
            return
        
        theme = self.themes[self.current_theme]
        colors = theme["colors"]
        
        # Create application palette
        palette = QPalette()
        
        # Set basic palette colors
        palette.setColor(QPalette.ColorRole.Window, QColor(colors["background"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors["text_primary"]))
        palette.setColor(QPalette.ColorRole.Base, QColor(colors["surface"]))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors["card"]))
        palette.setColor(QPalette.ColorRole.Text, QColor(colors["text_primary"]))
        palette.setColor(QPalette.ColorRole.Button, QColor(colors["card"]))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors["text_primary"]))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors["primary"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors["text_inverse"]))
        palette.setColor(QPalette.ColorRole.Link, QColor(colors["primary"]))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(colors["secondary"]))
        
        # Apply palette to application
        self.app_instance.setPalette(palette)
    
    def get_style(self, component: str, **kwargs) -> str:
        """Get styled CSS for a component with color substitution."""
        theme = self.themes[self.current_theme]
        colors = theme["colors"]
        
        if component not in theme["styles"]:
            return ""
        
        style = theme["styles"][component]
        
        # Replace color placeholders
        for color_name, color_value in colors.items():
            style = style.replace(f"{{{color_name}}}", color_value)
        
        # Replace custom parameters
        for key, value in kwargs.items():
            style = style.replace(f"{{{key}}}", str(value))
        
        return style
    
    def get_color(self, color_name: str) -> str:
        """Get a color value from the current theme."""
        theme = self.themes[self.current_theme]
        return theme["colors"].get(color_name, "#000000")
    
    def is_dark_theme(self) -> bool:
        """Check if the current theme is dark."""
        return self.current_theme == "dark"


# Global theme manager instance
_theme_manager = None

def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance."""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager