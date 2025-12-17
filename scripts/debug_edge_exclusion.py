
import geopandas as gpd
import pandas as pd
from shapely.geometry import box, Point
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import RESULTS_DIR

def debug_edge_failure():
    # 1. Load Data
    bounds_path = RESULTS_DIR / "detections-calibration-stratified_bounds.geojson"
    fp_path = RESULTS_DIR / "errors_fp.geojson"
    
    # Load all references
    from config import INPUTS_DIR
    ref_files = list(INPUTS_DIR.glob("reference_*.geojson"))
    ref_gdfs = []
    for rf in ref_files:
        gdf = gpd.read_file(rf)
        if gdf.crs != "EPSG:32635": gdf = gdf.to_crs("EPSG:32635")
        ref_gdfs.append(gdf)
    gdf_ref_all = pd.concat(ref_gdfs, ignore_index=True)
    
    gdf_bounds = gpd.read_file(bounds_path)
    gdf_fp = gpd.read_file(fp_path)
    
    # 2. Identify Target Tile
    target_tile_name = "K-35-053-3_Elenovo_x448_y3136.png"
    target_tile = gdf_bounds[gdf_bounds['tile_name'] == target_tile_name]
    
    if target_tile.empty:
        print(f"Target tile {target_tile_name} not found in bounds file!")
        return
        
    tile_geom = target_tile.geometry.iloc[0]
    print(f"Target Tile Bounds: {tile_geom.bounds}")
    
    # 3. Identify Target FP
    # Search for FP intersecting tile
    fps_in_tile = gdf_fp[gdf_fp.geometry.intersects(tile_geom)]
    
    if fps_in_tile.empty:
        print("No FPs STRICTLY intersecting this tile.")
        # Search nearest
        gdf_fp['dist'] = gdf_fp.distance(tile_geom)
        nearest = gdf_fp.sort_values('dist').iloc[0]
        print(f"Nearest FP is {nearest['dist']:.4f} meters away.")
        if nearest['dist'] < 1000:
             fps_in_tile = gpd.GeoDataFrame([nearest], crs=gdf_fp.crs)
        else:
             return
             
    print(f"Found {len(fps_in_tile)} FPs relevant to tile.")
    
    for idx, fp in fps_in_tile.iterrows():
        print(f"\nEvaluating FP index {idx}...")
        fp_geom = fp.geometry
        
        # Distance to Tile Edge
        boundary = tile_geom.boundary
        dist_fp = boundary.distance(fp_geom)
        print(f"  FP Geometry Distance to Edge: {dist_fp:.4f} meters")
        
        # Centroid Distance
        centroid = fp_geom.centroid
        dist_centroid = boundary.distance(centroid)
        print(f"  FP Centroid Distance to Edge: {dist_centroid:.4f} meters")
        
        if dist_centroid < 50:
             print("  [CRITICAL] Centroid is < 50m from edge! It SHOULD have been filtered.")
        
        # Find Nearest Reference
        gdf_ref_all['dist'] = gdf_ref_all.distance(fp_geom)
        nearest_ref = gdf_ref_all.sort_values('dist').iloc[0]
        dist_ref = nearest_ref['dist']
        print(f"  Nearest Reference (OID {nearest_ref.get('fid', 'N/A')}) Distance: {dist_ref:.4f} meters")
        
        ref_geom = nearest_ref.geometry
        dist_ref_edge = boundary.distance(ref_geom)
        print(f"  Ref Distance to Edge: {dist_ref_edge:.4f} meters")
        
        # Check Neighbors logic
        # Is the edge internal?
        elenovo_bounds = gdf_bounds[gdf_bounds['tile_name'].str.contains("Elenovo")]
        neighbors = elenovo_bounds[elenovo_bounds.geometry.touches(tile_geom)]
        if not neighbors.empty:
             print(f"  Tile has neighbors: {neighbors['tile_name'].tolist()}")
             # Check if this specific edge is shared
             # Create union of neighbors
             neigh_union = neighbors.geometry.union_all()
             # Distance of FP to neighbor union
             dist_neigh = neigh_union.distance(fp_geom)
             print(f"  FP Distance to Neighbor Union: {dist_neigh:.4f} meters")
             if dist_neigh < 1:
                 print("  FP is on a SHARED (Internal) Edge. It is protected.")
             else:
                 print("  FP is on an EXTERNAL Edge.")
        else:
             print("  Tile is ISOLATED (No touch neighbors). All edges are external.")

if __name__ == "__main__":
    debug_edge_failure()
