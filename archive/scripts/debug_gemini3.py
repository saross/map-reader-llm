import time
import google.generativeai as genai
from pathlib import Path
from PIL import Image
import sys

# Adjust python path
sys.path.append(str(Path(__file__).parent.parent))
from config import GOOGLE_API_KEY, TILES_DIR

def debug_tile():
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # Specific tile that likely stalled
    tile_name = "K-35-062-2_Rakovski_x4032_y2240.png"
    tile_path = TILES_DIR / "K-35-062-2_Rakovski" / tile_name
    
    if not tile_path.exists():
        print(f"Tile {tile_path} does not exist.")
        return

    print(f"Testing Gemini 3 Pro on {tile_name}...")
    
    model = genai.GenerativeModel(
        model_name="gemini-3-pro-preview",
        generation_config={"response_mime_type": "application/json"}
    )
    
    prompt = "Identify burial mounds. Return JSON."
    img = Image.open(tile_path)
    
    start_time = time.time()
    try:
        # standard call, no custom timeout, let's see what happens or if we can trap it
        # Actually, let's use the explicit timeout we added to validte it
        print("Sending request with 600s timeout...")
        response = model.generate_content(
            [prompt, img],
            request_options={'timeout': 600}
        )
        duration = time.time() - start_time
        print(f"Success! Duration: {duration:.2f}s")
        print(response.text[:100])
        
    except Exception as e:
        duration = time.time() - start_time
        print(f"FAILED after {duration:.2f}s")
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_tile()
