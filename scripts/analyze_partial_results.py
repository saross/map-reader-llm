
import geopandas as gpd
import pandas as pd
from pathlib import Path
import sys

def analyze_partial():
    output_path = Path("outputs/results/detections-visual-2025-12-17-3-pro.geojson")
    if not output_path.exists():
        print("Output file not found.")
        return

    try:
        gdf = gpd.read_file(output_path)
    except Exception as e:
        print(f"Could not read GeoJSON: {e}")
        return

    print(f"Total Detections: {len(gdf)}")
    
    if 'source_tile' not in gdf.columns:
        print("Column 'source_tile' not found.")
        return

    # Extract Map Name from tile name
    # Format: K-35-053-3_Elenovo_x...
    # We want the part before the coordinates
    def get_map_name(tile_name):
        parts = tile_name.split('_')
        # Rejoin until the 'x' part
        # Usually it's ID_Name_x...
        # K-35-052-4_32635_x... -> K-35-052-4_32635
        # K-35-053-3_Elenovo_x... -> K-35-053-3_Elenovo
        
        # Heuristic: Join all parts except the last two (x, y) if they are coordinates
        # Or just regex. 
        # Safer: The map directories are known.
        if "32635" in tile_name: return "32635"
        if "Elenovo" in tile_name: return "Elenovo"
        if "Rakovski" in tile_name: return "Rakovski"
        if "Lesovo" in tile_name: return "Lesovo"
        return "Unknown"

    gdf['Map'] = gdf['source_tile'].apply(get_map_name)
    
    # Count processed tiles?
    # We only have detections, so we don't know about empty tiles unless we have bounds.
    # But we can count unique tiles that yielded at least one detection.
    print("\n--- Unique Tiles with Detections ---")
    print(gdf.groupby('Map')['source_tile'].nunique())
    
    print("\n--- Detection Counts by Map ---")
    print(gdf['Map'].value_counts())

if __name__ == "__main__":
    analyze_partial()
