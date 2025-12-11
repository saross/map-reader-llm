
import os
import json
import random
import time
from pathlib import Path
import google.generativeai as genai
from PIL import Image
from tqdm import tqdm

# Adjust python path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import GOOGLE_API_KEY, MODEL_NAME, TILES_DIR, OUTPUTS_DIR

def test_inference():
    # Configure Gemini
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY not found in environment variables or .env file.")
        return

    genai.configure(api_key=GOOGLE_API_KEY)
    
    # Use the model
    # Generation config to enforce JSON
    generation_config = {
        "temperature": 0.1,
        "response_mime_type": "application/json",
    }
    
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config=generation_config,
        system_instruction="You are an expert map analyst. Your task is to identify archaeological 'Burial Mound' symbols on topographic maps. These appear as small orange circles, sometimes with radiating spikes (sunburst) or a central dot. Ignore contour lines (which are also orange) and other text. Return ONLY a JSON object with a list of bounding boxes."
    )

    # Gather all tiles
    all_tiles = list(TILES_DIR.rglob("*.png"))
    if not all_tiles:
        print(f"No tiles found in {TILES_DIR}")
        return

    # Select 5 random tiles
    selected_tiles = random.sample(all_tiles, min(5, len(all_tiles)))
    print(f"Selected {len(selected_tiles)} tiles for testing:")
    for t in selected_tiles:
        print(f" - {t.name}")

    results = {}

    for tile_path in tqdm(selected_tiles):
        try:
            img = Image.open(tile_path)
            
            prompt = """
            Identify the bounding boxes of all 'Burial Mound' symbols in this map tile. 
            
            Return a JSON object in the following format:
            {
                "detections": [
                    {"box_2d": [ymin, xmin, ymax, xmax], "label": "mound"}
                ]
            }
            
            If no mounds are found, return {"detections": []}.
            """
            
            response = model.generate_content([prompt, img])
            
            # Parse response
            try:
                json_response = json.loads(response.text)
                results[tile_path.name] = json_response
            except json.JSONDecodeError:
                print(f"Failed to parse JSON for {tile_path.name}")
                results[tile_path.name] = {"raw_text": response.text, "error": "JSONDecodeError"}

            # Rate limiting safety
            print("Sleeping for 10s to respect rate limits...")
            time.sleep(10)

        except Exception as e:
            print(f"Error processing {tile_path.name}: {e}")
            results[tile_path.name] = {"error": str(e)}

    # Save results
    output_file = OUTPUTS_DIR / "test_detections.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"\nTest detailed results saved to {output_file}")
    
    # Print summary
    print("\nSummary:")
    for filename, result in results.items():
        detections = result.get("detections", [])
        if isinstance(detections, list):
            print(f"{filename}: {len(detections)} detections")
        else:
             print(f"{filename}: Error or unexpected format")

if __name__ == "__main__":
    test_inference()
