"""
Create a simple tray icon for EnvStarter.
"""

from PIL import Image, ImageDraw
import os

def create_tray_icon():
    """Create a simple tray icon."""
    # Create a 32x32 icon
    size = 32
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple arrow pointing right (representing "start")
    color = (0, 150, 0, 255)  # Green
    border_color = (0, 100, 0, 255)  # Darker green
    
    # Arrow shape points
    points = [
        (6, 8),   # Top left of arrow
        (20, 16), # Arrow tip
        (6, 24),  # Bottom left of arrow
        (10, 16), # Arrow base right
    ]
    
    # Draw arrow
    draw.polygon(points, fill=color, outline=border_color, width=2)
    
    # Add a small circle for the "environment"
    circle_pos = (20, 8)
    circle_size = 8
    draw.ellipse([
        circle_pos[0] - circle_size//2, 
        circle_pos[1] - circle_size//2,
        circle_pos[0] + circle_size//2, 
        circle_pos[1] + circle_size//2
    ], fill=(0, 100, 200, 255), outline=(0, 50, 150, 255), width=1)
    
    return img

if __name__ == "__main__":
    # Create the icon
    icon = create_tray_icon()
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(__file__), exist_ok=True)
    
    # Save as PNG for Python usage
    icon_path = os.path.join(os.path.dirname(__file__), "envstarter_icon.png")
    icon.save(icon_path, "PNG")
    
    # Also save as ICO for Windows
    icon_ico_path = os.path.join(os.path.dirname(__file__), "envstarter_icon.ico")
    icon.save(icon_ico_path, "ICO")
    
    print(f"Icons created:")
    print(f"  PNG: {icon_path}")
    print(f"  ICO: {icon_ico_path}")