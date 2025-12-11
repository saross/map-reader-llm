
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
            
            # --- SPATIAL METADATA REFACTOR ---
            # 1. Get Transform for this specific window
            # Rasterio returns transform for the window corner
            window_transform = rasterio.windows.transform(window, src.transform)
            
            # 2. Write World File (.pgw)
            # Format: A, D, B, E, C, F
            # A: x-res, D: y-rot (0), B: x-rot (0), E: y-res (neg), C: x-center, F: y-center
            # window_transform gives Top-Left CORNER.
            # World File expects Center of Top-Left Pixel.
            # CenterX = CornerX + (ResX / 2)
            # CenterY = CornerY + (ResY / 2)
            
            res_x = window_transform.a
            res_y = window_transform.e # usually negative
            
            center_x = window_transform.c + (res_x / 2.0)
            center_y = window_transform.f + (res_y / 2.0)
            
            pgw_content = f"{res_x}\n0.0\n0.0\n{res_y}\n{center_x}\n{center_y}"
            pgw_path = tile_path.with_suffix(".pgw")
            with open(pgw_path, "w") as f:
                f.write(pgw_content)
                
            # 3. Write CRS to .aux.xml (PAMDataset format) for complete compatibility
            # This allows QGIS/GDAL to recognize the CRS automatically.
            aux_xml_path = tile_path.with_suffix(".png.aux.xml")
            crs_wkt = src.crs.to_wkt()
            # Minimal PAM XML
            xml_content = f"""<PAMDataset>
  <SRS>{crs_wkt}</SRS>
</PAMDataset>"""
            with open(aux_xml_path, "w") as f:
                f.write(xml_content)

            # Store legacy metadata just in case, but rely on sidecars now
            w, s, e, n = rasterio.windows.bounds(window, src.transform)
            metadata[tile_filename] = [w, s, src.res[0], src.res[1]]
 
    # Save legacy metadata as backup
    with open(map_output_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
        
    print(f"Finished tiling {map_name}. Saved {len(windows)*3} files (png+pgw+aux) to {map_output_dir}")

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
