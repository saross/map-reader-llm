
import geopandas as gpd
from pathlib import Path
import sys

# Adjust python path
sys.path.append(str(Path(__file__).parent.parent))
from config import OUTPUTS_DIR

def deduplicate_detections(gdf, distance_threshold=20.0):
    """
    Deduplicates points by buffering and merging.
    """
    if gdf.empty:
        return gdf

    print(f"Deduplicating {len(gdf)} detections with {distance_threshold}m threshold...")
    
    # 1. Convert to centroids for clustering (boxes might overlap oddly)
    #    Actually buffering the boxes themselves is fine too.
    #    Let's buffer the centroids.
    
    # Ensure we use centroids for the location logic
    points = gdf.geometry.centroid
    buffered = points.buffer(distance_threshold / 2)
    merged = buffered.unary_union
    
    if merged.is_empty:
        return gpd.GeoDataFrame(columns=gdf.columns, crs=gdf.crs)

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
    print(f"Reduced by {len(gdf) - len(deduplicated_gdf)} detections (Final: {len(deduplicated_gdf)})")
    return deduplicated_gdf

def process_results():
    input_file = OUTPUTS_DIR / "all_detections.geojson"
    
    if not input_file.exists():
        print(f"File not found: {input_file}")
        return

    print(f"Reading {input_file}...")
    try:
        gdf = gpd.read_file(input_file)
    except Exception as e:
        print(f"Error reading GeoJSON: {e}")
        return

    if gdf.empty:
        print("No detections found within file.")
        return

    # Ensure CRS is correct (it should be read from the file, but we can enforce if missing)
    if gdf.crs is None:
        print("Warning: CRS missing, assigning EPSG:32635")
        gdf.set_crs(epsg=32635, inplace=True)
        
    print(f"Loaded {len(gdf)} raw detections.")

    # Deduplicate
    deduped_gdf = deduplicate_detections(gdf)
    
    # Export
    output_gpkg = OUTPUTS_DIR / "mounds.gpkg"
    
    # Save Layers
    gdf.to_file(output_gpkg, layer="raw_boxes", driver="GPKG")
    deduped_gdf.to_file(output_gpkg, layer="deduped_points", driver="GPKG")
    
    print(f"Saved results to {output_gpkg}")

if __name__ == "__main__":
    process_results()
