
import json
import time
import os
from pathlib import Path
from tqdm import tqdm
import google.generativeai as genai
from PIL import Image

# Adjust python path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import GOOGLE_API_KEY, MODEL_NAME, TILES_DIR, OUTPUTS_DIR

def detect_mounds():
    # Configure Gemini
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY not found.")
        return

    genai.configure(api_key=GOOGLE_API_KEY)
    
    # Model Configuration
    generation_config = {
        "temperature": 0.1,
        "response_mime_type": "application/json",
    }
    
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config=generation_config,
        system_instruction="""
        You are an expert analyst of Soviet 1:50,000 Topographic Maps.
        Your goal is to identify archaeological "Burial Mound" (Tumulus) symbols.
        
        Target Symbols:
        1. "Sunburst": An orange/brown circle with radiating spikes.
        2. "Mound": A simple small orange circle with a central dot.
        3. "Triangulation Mound": A sunburst with a black triangle or symbol inside.
        
        Negative Constraints:
        - DISTINCTLY IGNORE brown contour lines that do not form a distinct sunburst or circle-dot.
        - IGNORE black elevation points (simple dots) unless surrounded by a mound circle.
        - IGNORE blue wells (circles with blue filling).
        - IGNORE vegetation patterns.
        
        Return a JSON object with a list of bounding boxes.
        """
    )

    # Output file
    output_file = OUTPUTS_DIR / "all_detections.json"
    
    # Load existing results if any (to allow resuming)
    if output_file.exists():
        with open(output_file, 'r') as f:
            try:
                results = json.load(f)
            except json.JSONDecodeError:
                results = {}
    else:
        results = {}

    # Gather all tiles
    all_tiles = []
    # Walk through map subdirectories
    for map_dir in TILES_DIR.iterdir():
        if map_dir.is_dir():
            # Check for metadata first to ensure valid tile set
            if (map_dir / "metadata.json").exists():
                all_tiles.extend(list(map_dir.glob("*.png")))
    
    all_tiles = sorted(all_tiles)
    print(f"Found {len(all_tiles)} tiles total.")
    
    # Filter out already processed tiles
    tiles_to_process = [t for t in all_tiles if t.name not in results]
    print(f"Processing {len(tiles_to_process)} new tiles...")

    prompt = """
    Look at this Soviet map tile. 
    Identify the bounding boxes of all 'Burial Mound' symbols.
    
    Return a JSON object in the following format:
    {
        "detections": [
            {
                "box_2d": [ymin, xmin, ymax, xmax], 
                "label": "mound", 
                "reasoning": "Briefly explain why this is a mound (e.g., 'Orange circle with spikes', 'Circle with dot')"
            }
        ]
    }
    
    If no mounds are found, return {"detections": []}.
    """

    save_frequency = 10
    
    for i, tile_path in enumerate(tqdm(tiles_to_process)):
        try:
            img = Image.open(tile_path)
            
            response = model.generate_content([prompt, img])
            
            try:
                json_response = json.loads(response.text)
                results[tile_path.name] = json_response
            except json.JSONDecodeError:
                print(f"Failed to parse JSON for {tile_path.name}")
                results[tile_path.name] = {"raw_text": response.text, "error": "JSONDecodeError"}
            except Exception as e:
                 # Catch 'finish_reason' errors or other generation errors
                results[tile_path.name] = {"error": str(e)}

            # Rate Limit Sleep
            # For Free Tier, we need to be careful. 
            # 10 detections per minute roughly? 
            # We used 10s previously and it was borderline. 
            # Let's stick to 10s to be safe.
            time.sleep(10)
            
            # Periodically save
            if (i + 1) % save_frequency == 0:
                with open(output_file, "w") as f:
                    json.dump(results, f, indent=2)

        except Exception as e:
            print(f"Error processing {tile_path.name}: {e}")
            results[tile_path.name] = {"error": str(e)}
            # If we hit a hard API error, maybe wait longer
            time.sleep(20)

    # Final Save
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"Finished. Results saved to {output_file}")

if __name__ == "__main__":
    detect_mounds()
