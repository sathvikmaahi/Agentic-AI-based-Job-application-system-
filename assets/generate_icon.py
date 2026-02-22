"""
Generate ApplyAI App Icon
Creates a beautiful icon with paper airplane + briefcase concept
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size=1024):
    """Create a modern app icon"""
    # Create base image with gradient background
    img = Image.new('RGB', (size, size), color='#6366F1')
    draw = ImageDraw.Draw(img)
    
    # Create gradient effect
    for y in range(size):
        r = int(99 + (139 - 99) * y / size)  # #6366F1 to #8B5CF6
        g = int(102 + (92 - 102) * y / size)
        b = int(241 + (246 - 241) * y / size)
        draw.line([(0, y), (size, y)], fill=(r, g, b))
    
    # Draw paper airplane symbol
    center_x, center_y = size // 2, size // 2
    
    # Airplane body (triangle)
    airplane_color = "white"
    margin = size // 4
    
    # Main triangle
    points = [
        (center_x, margin),  # Top
        (size - margin, center_y + margin // 2),  # Bottom right
        (center_x, center_y + margin // 3),  # Inner point
        (margin, center_y + margin // 2),  # Bottom left
    ]
    
    # Draw the airplane shape
    draw.polygon(points, fill=airplane_color)
    
    # Add a small circle/dot to represent AI/brain
    dot_size = size // 12
    dot_x = size - margin - dot_size
    dot_y = margin + dot_size
    draw.ellipse(
        [(dot_x - dot_size, dot_y - dot_size), 
         (dot_x + dot_size, dot_y + dot_size)],
        fill="#10B981"  # Emerald accent
    )
    
    return img

def generate_all_icons():
    """Generate icons in all required sizes"""
    sizes = {
        'icon.png': 1024,
        'icon_512.png': 512,
        'icon_256.png': 256,
        'icon_128.png': 128,
    }
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for filename, size in sizes.items():
        img = create_icon(size)
        filepath = os.path.join(base_dir, filename)
        img.save(filepath, 'PNG')
        print(f"✅ Created {filename} ({size}x{size})")
    
    # Also create .icns for macOS (simplified version)
    # For now, we'll use the 1024px version as the main icon
    print("\n🎨 Icon generation complete!")
    print("📱 ApplyAI icon is ready to use")

if __name__ == "__main__":
    generate_all_icons()
