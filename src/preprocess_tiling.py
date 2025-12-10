
import json
import rasterio
from rasterio.windows import Window
from PIL import Image
from tqdm import tqdm
from pathlib import Path
import numpy as np

# Adjust python path if run as script, though standard import is better
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import INPUTS_DIR, TILES_DIR, TILE_SIZE, OVERLAP

def tile_raster(input_path: Path):
    """
    Tiles a GeoTIFF into smaller PNGs and saves metadata.
    """
    input_path = Path(input_path)
    map_name = input_path.stem
    
    # Create output directory for this map
    map_output_dir = TILES_DIR / map_name
    map_output_dir.mkdir(parents=True, exist_ok=True)
    
    metadata = {}
    
    with rasterio.open(input_path) as src:
        width = src.width
        height = src.height
        
        # Calculate steps
        step = TILE_SIZE - OVERLAP
        
        # Generate windows
        # Using a list comprehension for a cleaner progress bar setup
        windows = []
        for y in range(0, height, step):
            for x in range(0, width, step):
                # Handle edge cases where window goes out of bounds
                # Rasterio handles this automatically if we request a window larger than the image
                # by padding or clipping? Let's be explicit to avoid black bars if possible, 
                # or just accept them. 
                # Actually, standard practice for VLM is padding or just clipping.
                # Let's clip the window to the image bounds.
                
                window = Window(x, y, TILE_SIZE, TILE_SIZE)
                
                # Check if window is completely out of bounds (shouldn't happen with range)
                # But we might want to clip the width/height if it goes over
                # However, for the VLM, constant size is nicer. 
                # Let's stick to requesting the window and letting rasterio read it.
                # If it's valid, we process it.
                
                windows.append((x, y, window))

        print(f"Processing {len(windows)} tiles for {map_name}...")
        
        for x, y, window in tqdm(windows):
            # Read the data from the window
            # boundless=True pads with 0 (black) if window is outside image
            img_data = src.read(window=window, boundless=True, fill_value=0)
            
            # Rasterio reads as (Bands, Height, Width). Convert to (H, W, B) for Pillow
            img_data = img_data.transpose(1, 2, 0)
            
            # If 1 band (grayscale), convert to RGB for consistency
            if img_data.shape[2] == 1:
                img_data = np.dstack([img_data]*3)
            elif img_data.shape[2] > 3:
                 # Drop alpha if present or take just first 3 bands
                img_data = img_data[:, :, :3]
                
            # Create Image
            img = Image.fromarray(img_data.astype('uint8'), 'RGB')
            
            # Filename
            tile_filename = f"{map_name}_x{x}_y{y}.png"
            tile_path = map_output_dir / tile_filename
            img.save(tile_path)
            
            # Calculate Lower Left Coordinate
            # Affine Transform: (x_off, a, b, y_off, d, e)
            # x_coord = x_off + a * col + b * row
            # y_coord = y_off + d * col + e * row
            # Lower Left pixel of the tile is (0, height) in local image coordinates? 
            # OR (0, TILE_SIZE) depending on if we consider outside or edge.
            # Usually strict lower-left corner of the image extent.
            w, s, e, n = rasterio.windows.bounds(window, src.transform)
            # rasterio bounds returns (left, bottom, right, top)
            # This is exactly what we need. left = min x, bottom = min y
            
            # Store [LowerLeftX, LowerLeftY, ResolutionX, ResolutionY]
            # using src.res which returns (res_x, res_y) - usually positive values
            metadata[tile_filename] = [w, s, src.res[0], src.res[1]]

    # Save metadata
    with open(map_output_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
        
    print(f"Finished tiling {map_name}. Saved to {map_output_dir}")

def main():
    # Process all TIFs in inputs
    tif_files = list(INPUTS_DIR.glob("*.tif"))
    
    if not tif_files:
        print(f"No .tif files found in {INPUTS_DIR}")
        return

    for tif_path in tif_files:
        print(f"Starting {tif_path.name}...")
        try:
            tile_raster(tif_path)
        except Exception as e:
            print(f"Error processing {tif_path.name}: {e}")

if __name__ == "__main__":
    main()
