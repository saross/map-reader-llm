
import json
from pathlib import Path
from collections import defaultdict
import sys

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))
from config import INPUTS_DIR

def split_references():
    input_file = INPUTS_DIR / "mounds-reference.geojson"
    if not input_file.exists():
        print(f"Error: Reference file not found at {input_file}")
        return

    print(f"Reading {input_file}...")
    with open(input_file, 'r') as f:
        data = json.load(f)

    if "features" not in data:
        print("Error: Invalid GeoJSON, no 'features' list.")
        return

    # Group features by Map
    map_features = defaultdict(list)
    for feature in data["features"]:
        props = feature.get("properties", {})
        map_name = props.get("Map")
        if map_name:
            map_features[map_name].append(feature)
        else:
            print(f"Warning: Feature missing 'Map' property. Skipped.")

    # Save individual files
    for map_name, features in map_features.items():
        output_file = INPUTS_DIR / f"reference_{map_name}.geojson"
        
        output_data = {
            "type": "FeatureCollection",
            "name": f"reference_{map_name}",
            "crs": data.get("crs"), # Preserve CRS
            "features": features
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"Saved {len(features)} features to {output_file.name}")

if __name__ == "__main__":
    split_references()
