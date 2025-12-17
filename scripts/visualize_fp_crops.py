
import geopandas as gpd
from pathlib import Path
import rasterio
from rasterio.mask import mask
from shapely.geometry import box
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import BASE_DIR, TILES_DIR

def visualize_crops():
    fp_path = Path("analysis/phase12_failures/errors_fp.geojson")
    if not fp_path.exists():
        print("FP file not found.")
        return
        
    gdf = gpd.read_file(fp_path)
    output_dir = Path("analysis/phase12_failures/crops")
    output_dir.mkdir(exist_ok=True)
    
    print(f"Generating crops for {len(gdf)} FPs...")
    
    # Pre-scan tiles
    all_tiles = {}
    for p in TILES_DIR.rglob("*.png"):
        all_tiles[p.name] = p
        
    crop_size = 256 # 256px around centroid
    
    for idx, row in gdf.iterrows():
        tile_name = row['source_tile']
        if tile_name not in all_tiles:
            print(f"Tile {tile_name} not found.")
            continue
            
        tile_path = all_tiles[tile_name]
        
        # Load Tile to get CRS and transform
        with rasterio.open(tile_path) as src:
            # Re-project geometry to Tile's CRS if needed?
            # Actually, detections are in 32635.
            # Tile *might* be raw pixels but georeferenced.
            # Rasterio handles window reading by bounds.
            
            # Create a box around the centroid
            # Centroid is in map units (meters)
            center = row.geometry.centroid
            # Box is center +/- 128 meters? (Assume 1px ~ 5m on these maps? No, 1px ~ 5m? 
            # Resolution is typically ~3-5m (2m for high res). 
            # Let's say we want 200m context.
            window_size = 200
            
            minx = center.x - window_size/2
            maxx = center.x + window_size/2
            miny = center.y - window_size/2
            maxy = center.y + window_size/2
            
            bbox = box(minx, miny, maxx, maxy)
            
            # Crop
            try:
                out_image, out_transform = mask(src, [bbox], crop=True)
                
                # Save
                # Convert to image format
                from rasterio.plot import reshape_as_image
                from PIL import Image
                import numpy as np
                
                img_data = reshape_as_image(out_image)
                # Handle types
                img = Image.fromarray(img_data)
                
                # Draw box?
                # Maybe later. Raw image is better for analysis.
                
                filename = f"FP_{idx}_{tile_name}"
                img.save(output_dir / filename)
                print(f"Saved {filename}")
                
            except Exception as e:
                print(f"Error cropping {idx}: {e}")

if __name__ == "__main__":
    visualize_crops()
