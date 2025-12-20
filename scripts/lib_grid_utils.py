
from PIL import Image, ImageDraw
import config

def apply_grid(image: Image.Image, spacing: int = None, color: tuple = None) -> Image.Image:
    """Overlays a grid on the image."""
    if spacing is None:
        spacing = config.GRID_SPACING_PX
    if color is None:
        color = config.GRID_COLOR
        
    # Convert to RGBA to support transparency
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
        
    overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    width, height = image.size
    
    # Draw Vertical
    for x in range(0, width, spacing):
        draw.line([(x, 0), (x, height)], fill=color, width=1)
        
    # Draw Horizontal
    for y in range(0, height, spacing):
        draw.line([(0, y), (width, y)], fill=color, width=1)
        
    return Image.alpha_composite(image, overlay).convert('RGB')
