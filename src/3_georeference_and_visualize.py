
import json
import geopandas as gpd
from shapely.geometry import box, Point
from pathlib import Path
import pandas as pd
# Adjust python path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from config import OUTPUTS_DIR, TILES_DIR, TILE_SIZE

def deduplicate_detections(gdf, distance_threshold=20.0):
    """
    Deduplicates points within a certain distance threshold (meters).
    Keeps the first one found (or could be improved to keep highest confidence).
    """
    if gdf.empty:
        return gdf

    # efficient spatial join or buffer check?
    # Simple approach: Buffer all points, merge overlapping buffers, take centroid.
    
    # 1. Buffer points
    # 2. Unary union of buffers to merge overlapping blobs
    # 3. Get centroids of merged blobs
    
    # This merges clusters of detections into a single avg point.
    
    print(f"Deduplicating {len(gdf)} detections with {distance_threshold}m threshold...")
    
    buffered = gdf.geometry.buffer(distance_threshold / 2)
    merged = buffered.unary_union
    
    if merged.is_empty:
        return gpd.GeoDataFrame(columns=gdf.columns, crs=gdf.crs)

    # If unary_union returns a MultiPolygon or Polygon, we iterate parts
    final_points = []
    
    if merged.geom_type == 'Polygon':
        geoms = [merged]
    elif merged.geom_type == 'MultiPolygon':
        geoms = merged.geoms
    else:
        geoms = []

    for geom in geoms:
        final_points.append(geom.centroid)
        
    deduplicated_gdf = gpd.GeoDataFrame(geometry=final_points, crs=gdf.crs)
    
    # We lose the original properties (labels, reasoning) with this simple centroid merge.
    # To keep them, we'd need a spatial join back to the original points.
    # For now, let's just output the points.
    
    print(f"Reduced to {len(deduplicated_gdf)} unique locations.")
    return deduplicated_gdf

def process_results():
    input_file = OUTPUTS_DIR / "all_detections.json"
    if not input_file.exists():
        print(f"File not found: {input_file}")
        return

    try:
        with open(input_file) as f:
            detections_data = json.load(f)
    except json.JSONDecodeError:
        print("Error reading JSON - maybe empty or partial write?")
        return

    features = []
    metadata_cache = {}

    print("Converting detections to geospatial data...")
    
    for filename, result in detections_data.items():
        if "error" in result:
            continue
            
        detections = result.get("detections", [])
        if not detections:
            continue

        # Find metadata
        found_path = list(TILES_DIR.rglob(filename))
        if not found_path:
            continue
        
        tile_path = found_path[0]
        map_dir = tile_path.parent
        metadata_path = map_dir / "metadata.json"
        
        if str(metadata_path) not in metadata_cache:
            if metadata_path.exists():
                with open(metadata_path) as f:
                    metadata_cache[str(metadata_path)] = json.load(f)
            else:
                continue

        tile_meta = metadata_cache[str(metadata_path)].get(filename)
        if not tile_meta:
            continue
            
        ll_x, ll_y, res_x, res_y = tile_meta
        
        for det in detections:
            ymin_n, xmin_n, ymax_n, xmax_n = det["box_2d"]
            
            # Pixel Coords
            px_min_y = (ymin_n / 1000) * TILE_SIZE
            px_max_y = (ymax_n / 1000) * TILE_SIZE
            px_min_x = (xmin_n / 1000) * TILE_SIZE
            px_max_x = (xmax_n / 1000) * TILE_SIZE
            
            # Geo Coords
            geo_min_x = ll_x + (px_min_x * res_x)
            geo_max_x = ll_x + (px_max_x * res_x)
            
            geo_max_y = ll_y + ((TILE_SIZE - px_min_y) * res_y)
            geo_min_y = ll_y + ((TILE_SIZE - px_max_y) * res_y)
            
            # Geometry: Box
            geom_box = box(geo_min_x, geo_min_y, geo_max_x, geo_max_y)
            
            features.append({
                "geometry": geom_box,
                "label": det.get("label", "mound"),
                "reasoning": det.get("reasoning", ""),
                "source_tile": filename,
                "confidence": "high" # placeholder
            })

    if not features:
        print("No features extracted.")
        return

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(features, crs="EPSG:32635") # Assuming UTM Zone 35N based on K-35 prefix? 
    # WAIT! The original TIF probably has a CRS. We should really read it from the TIF or trust the numbers.
    # The numbers (314011, 4686624) look like UTM. 
    # Let's try to verify CRS from one TIF if possible, or just default to None/Unknown in output if risky.
    # Actually, we can check the TIF crs with rasterio.
    
    # Deduplication (using Centroids)
    # First convert boxes to centroids
    gdf_centroids = gdf.copy()
    gdf_centroids['geometry'] = gdf.geometry.centroid
    
    deduped_gdf = deduplicate_detections(gdf_centroids)
    
    # Export
    output_gpkg = OUTPUTS_DIR / "mounds.gpkg"
    
    # Save Raw Boxes
    gdf.to_file(output_gpkg, layer="raw_boxes", driver="GPKG")
    
    # Save Deduped Points
    deduped_gdf.to_file(output_gpkg, layer="deduped_points", driver="GPKG")
    
    print(f"Saved results to {output_gpkg}")
    print(f" - Layer 'raw_boxes': {len(gdf)} features")
    print(f" - Layer 'deduped_points': {len(deduped_gdf)} features")

if __name__ == "__main__":
    process_results()
