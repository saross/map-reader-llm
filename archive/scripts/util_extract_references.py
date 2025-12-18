import os
import sys
from pathlib import Path
import json
import rasterio
from PIL import Image
import google.generativeai as genai

# Adjust path to import config
sys.path.append(str(Path(__file__).parent.parent))
from config import GOOGLE_API_KEY, MODEL_NAME, INPUTS_DIR, BASE_DIR

# Setup output dir
REFERENCES_DIR = BASE_DIR / "references"
REFERENCES_DIR.mkdir(exist_ok=True)

def extract_references():
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY not found.")
        return

    genai.configure(api_key=GOOGLE_API_KEY)
    
    legend_path = INPUTS_DIR / "legend.tif"
    if not legend_path.exists():
        # Fallback to png if tif not found (though user said tif)
        legend_path = INPUTS_DIR / "legend.png"
    
    if not legend_path.exists():
        print(f"Error: Legend file not found at {legend_path}")
        return

    print(f"Processing legend: {legend_path}")
    
    # Load Image
    try:
        # Open with PIL to likely convert to RGB if needed for Gemini
        img = Image.open(legend_path)
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config={"response_mime_type": "application/json"}
    )

    prompt = """
    Analyze this map legend. Identify the bounding boxes for the following specific symbols.
    Return a JSON object with the format: {"crops": [{"name": "symbol_name", "box_2d": [ymin, xmin, ymax, xmax]}]}
    Use normalized coordinates (0-1000).

    Targets:
    1. "burial_mound": A hollow circle with radiating spikes/rays (Kurgan).
    2. "settlement_mound": A larger irregular/oval shape with outward ticks (Ancient Settlement).
    3. "triangulation_mound": A black triangle inside a spiked mound circle.
    4. "benchmark_mound": A black square inside a spiked mound circle.
    """

    print("Sending to Gemini for identification...")
    # Convert to PNG for API support
    temp_png = BASE_DIR / "temp_legend_gemini.png"
    if img.mode == 'CMYK':
        img = img.convert('RGB')
    img.save(temp_png, format="PNG")
    img_for_api = Image.open(temp_png)

    try:
        response = model.generate_content([prompt, img_for_api])
        result = json.loads(response.text)
    except Exception as e:
        print(f"Error from API: {e}")
        return
    finally:
        if temp_png.exists():
            temp_png.unlink() # Cleanup
    
    width, height = img.size
    print(f"Image Size: {width}x{height}")

    crops_found = result.get("crops", [])
    print(f"Found {len(crops_found)} symbols.")

    for item in crops_found:
        name = item["name"]
        ymin, xmin, ymax, xmax = item["box_2d"]
        
        # Convert to pixels
        left = int((xmin / 1000) * width)
        top = int((ymin / 1000) * height)
        right = int((xmax / 1000) * width)
        bottom = int((ymax / 1000) * height)
        
        # Buffer slightly? Maybe 5px
        buffer = 5
        left = max(0, left - buffer)
        top = max(0, top - buffer)
        right = min(width, right + buffer)
        bottom = min(height, bottom + buffer)
        
        crop = img.crop((left, top, right, bottom))
        
        out_path = REFERENCES_DIR / f"{name}.png"
        crop.save(out_path)
        print(f"Saved {name} to {out_path}")

if __name__ == "__main__":
    extract_references()
