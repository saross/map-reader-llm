
import google.generativeai as genai
import os
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv
import time

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

TILE_PATH = Path("outputs/tiles/K-35-053-3_Elenovo/K-35-053-3_Elenovo_x1344_y1792.png")
if not TILE_PATH.exists():
    # Fallback to any tile
    TILE_PATH = list(Path("outputs/tiles").rglob("*.png"))[0]

PROMPT_PATH = Path("prompts/V3_visual_mound_detection.md")
with open(PROMPT_PATH, "r") as f:
    prompt_text = f.read()

# Models to test
candidates = [
    "models/gemini-1.5-pro-latest",
    "models/gemini-1.5-pro-001",
    "models/gemini-1.5-pro-002",
    "models/gemini-1.5-pro",
    "models/gemini-flash-latest" 
]

print(f"Testing tile: {TILE_PATH.name}")

for model_name in candidates:
    print(f"\n--- Testing Model: {model_name} ---")
    try:
        model = genai.GenerativeModel(model_name=model_name, system_instruction=prompt_text)
        response = model.generate_content(
            ["Find mound symbols.", Image.open(TILE_PATH)],
            request_options={"timeout": 60}
        )
        print(f"Status: Success")
        print(f"Response Preview: {response.text[:200]}...")
    except Exception as e:
        print(f"Status: Failed ({e})")
        
