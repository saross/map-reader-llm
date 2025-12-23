
import geopandas as gpd
import pandas as pd
from shapely.geometry import box

def evaluate_single_tile():
    # Paths
    det_path = "outputs/results/detections_verification_green_tile.geojson"
    ref_path = "inputs/reference_K-35-053-3_Elenovo.geojson"
    try:
        det_gdf = gpd.read_file(det_path)
    except Exception:
        print("No detections found.")
        return

    ref_gdf = gpd.read_file(ref_path)
    if ref_gdf.crs != "EPSG:32635": ref_gdf = ref_gdf.to_crs("EPSG:32635")
    
    # Define Tile Bounds (x1344, y1792)
    # We need to reconstruct the EXACT bounds of the tile to filter references
    # Tile size 512, Overlap 64. Step = 448.
    # Actually, simpler: Use the bounds of the detections to infer the area?
    # Or just use the original bounds file if available.
    # Let's filter References by intersection with Detections' total bounds + buffer
    
    # Or better: Assume the user wants to know if we hit the ones we missed last time.
    # Load the OLD FN file
    fn_path = "outputs/results/errors_fn.geojson"
    fn_gdf = gpd.read_file(fn_path)
    
    # Filter for this tile's FNs (using the spatial join logic from before or just bounds)
    # Bounds for x1344, y1792:
    # We don't have the transformation matrix handy in this script, BUT
    # We can check which of the PREVIOUS FNs are now COVERED by a NEW Detection.
    
    print(f"New Detections: {len(det_gdf)}")
    
    # Check coverage of known FNs
    # Buffer detections by small amount (e.g. 5m) or just check intersection
    # Evaluation logic uses 20m buffer on Ref.
    
    print("Checking against previous False Negatives...")
    hits = 0
    for idx, fn in fn_gdf.iterrows():
        # Check if this FN is covered by any new detection
        # Use 20m buffer on FN
        fn_buffered = fn.geometry.buffer(20)
        matches = det_gdf[det_gdf.geometry.intersects(fn_buffered)]
        
        if not matches.empty:
            print(f"  [RECOVERED] FN {fn['fid']} is now DETECTED by {len(matches)} box(es)!")
            hits += 1
            
    print(f"Total Previous FNs Recovered: {hits}")
    
    # Check for False Positives
    # We need the tile geometry to filter references
    # Approximate tile bounds from detections or just use the whole map references (spatial join will handle it)
    # Let's verify how many detections did NOT match a reference.
    
    print("\nChecking for False Positives...")
    # Buffer references by 20m
    ref_buffered = ref_gdf.copy()
    ref_buffered['geometry'] = ref_buffered.geometry.buffer(20)
    
    # Join Detections -> References
    # Left join: Keep all detections, match to refs
    join_fp = gpd.sjoin(det_gdf, ref_buffered, how='left', predicate='intersects')
    
    # FPs are those with NaN index_right
    fps = join_fp[join_fp.index_right.isna()]
    fp_count = len(fps)
    
    print(f"Total Detections: {len(det_gdf)}")
    print(f"Matched Detections (TP): {len(det_gdf) - fp_count}")
    print(f"Unmatched Detections (FP): {fp_count}")
    
    if fp_count > 0:
        print("Potential False Positives found at:")
        # Reconstruct tile geometry from bounds of DETECTIONS (approximate) or hardcode
        # Since I ran on single tile, the union of detections + buffer is roughly the area, but risky.
        # Better: use the source tile name to find the bounds from the bounds file?
        
        # Load bounds file
        bounds_gdf = gpd.read_file("outputs/results/detections-calibration-stratified_bounds.geojson")
        tile_name = "K-35-053-3_Elenovo_x1344_y1792.png"
        tile_geom = bounds_gdf[bounds_gdf['tile_name'] == tile_name].geometry.iloc[0]
        
        for idx, fp in fps.iterrows():
            dist = tile_geom.boundary.distance(fp.geometry)
            print(f"  FP at {fp.geometry.centroid} - Distance to Edge: {dist:.2f}m")
            if dist < 50:
                print("    -> IGNORE: Would be excluded by 50m buffer.")
            else:
                print("    -> REAL: Valid False Positive > 50m from edge.")

if __name__ == "__main__":
    evaluate_single_tile()
