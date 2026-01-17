
import geopandas as gpd
from pathlib import Path
import sys
from PIL import Image
import rasterio
from rasterio.windows import Window
from shapely.geometry import shape

# Setup Path to import config
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

try:
    from config import TILES_DIR, CONTEXT_SIZE
except ImportError:
    print("Error: config.py not found.")
    sys.exit(1)

def get_tile_path(tile_id: str) -> Path:
    """Resolves tile ID to absolute path."""
    tiles_dir = TILES_DIR
    print(f"DEBUG: Searching for {tile_id} in {tiles_dir}")
    found = list(tiles_dir.glob(f"**/{tile_id}")) 
    if not found:
        print("DEBUG: Direct match failed. Trying with .png extension.")
        found = list(tiles_dir.glob(f"**/{tile_id}.png"))
    
    if found:
        print(f"DEBUG: Found {found[0]}")
        return found[0]
    print("DEBUG: Not found.")
    return None

def crop_candidate(raster_path: Path, geom, context_px: int = CONTEXT_SIZE):
    """Crops the raster around the candidate geometry."""
    with rasterio.open(raster_path) as src:
        bounds = shape(geom).bounds
        cx = (bounds[0] + bounds[2]) / 2
        cy = (bounds[1] + bounds[3]) / 2
        
        row, col = src.index(cx, cy)
        half_size = context_px // 2
        window = Window(col - half_size, row - half_size, context_px, context_px)
        
        try:
            arr = src.read(window=window)
            if arr.shape[0] == 0: return None
            img_data = arr.transpose(1, 2, 0)
            return Image.fromarray(img_data)
        except Exception:
            return None

def mine_crops(geojson_path, output_dir, label, bounds_path=None):
    print(f"Mining {label} from {geojson_path}")
    try:
        gdf = gpd.read_file(geojson_path)
    except Exception as e:
        print(f"Error reading {geojson_path}: {e}")
        return

    print(f"DEBUG: Loaded {len(gdf)} rows.")
    
    # Load bounds if needed
    gdf_bounds = None
    if bounds_path:
        try:
             gdf_bounds = gpd.read_file(bounds_path)
             # Index for speed? sjoin is fast enough for small N
        except Exception as e:
             print(f"Error loading bounds {bounds_path}: {e}")

    out_path = Path(output_dir) / label
    out_path.mkdir(parents=True, exist_ok=True)
    
    saved = 0
    for idx, row in gdf.iterrows():
        tile_id = row.get('source_tile')
        
        # Fallback: Spatial Lookup
        if not tile_id and gdf_bounds is not None:
             # Find which tile contains this geometry
             # Using centroid to avoid tile overlap issues (just pick one)
             query_geom = row.geometry.centroid
             match = gdf_bounds[gdf_bounds.contains(query_geom)]
             if not match.empty:
                 tile_id = match.iloc[0]['tile_name'] # Assuming tile_name is the ID
                 # print(f"DEBUG: Spatially resolved FN {idx} to {tile_id}")
        
        if not tile_id: 
            # print(f"DEBUG: Row {idx} missing source_tile and no spatial match.")
            continue
        
        tile_path = get_tile_path(tile_id)
        if not tile_path: continue
        
        # Crop
        img = crop_candidate(tile_path, row['geometry'])
        if img:
            fname = f"{label}_{idx}_{tile_id}.png"
            img.save(out_path / fname)
            saved += 1
            
    print(f"Saved {saved} {label} crops to {out_path}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python mine_hard_cases.py <fp_path> <fn_path> <output_dir> [bounds_path]")
        sys.exit(1)
        
    fp_path = sys.argv[1]
    fn_path = sys.argv[2]
    out_dir = sys.argv[3]
    bounds_path = sys.argv[4] if len(sys.argv) > 4 else None
    
    mine_crops(fp_path, out_dir, "hard_negative_fp", bounds_path)
    mine_crops(fn_path, out_dir, "hard_positive_fn", bounds_path)
