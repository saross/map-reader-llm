import json
import time
import os
import sys
from pathlib import Path
from PIL import Image
import google.generativeai as genai

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import GOOGLE_API_KEY, BASE_DIR, REFERENCES_DIR

# Using confirmed Flash model
MODEL_NAME = "gemini-3-flash-preview"
CONFIG_PATH = Path(BASE_DIR) / "prompts" / "versions" / "v3.2_experimental.json"

# The 5 specific tiles that failed with "finish_reason: 2" (Max Tokens)
FAILED_TILES = [
    "inputs/tiles/K-35-052-4_32635/K-35-052-4_32635_x3584_y448.png",
    "inputs/tiles/K-35-053-3_Elenovo/K-35-053-3_Elenovo_x1344_y3584.png",
    "inputs/tiles/K-35-053-3_Elenovo/K-35-053-3_Elenovo_x1792_y3136.png",
    "inputs/tiles/K-35-053-3_Elenovo/K-35-053-3_Elenovo_x1792_y896.png",
    "inputs/tiles/K-35-053-3_Elenovo/K-35-053-3_Elenovo_x2240_y448.png"
]

def run_retries():
    print(f"Starting Retry Experiment on {len(FAILED_TILES)} tiles (3 attempts each)...")
    
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY missing")
        return

    genai.configure(api_key=GOOGLE_API_KEY)
    
    # Load Config
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    # Load Instruction
    instruction_file = config.get("instruction_file", "v3.0_system_instruction.md")
    prompt_path = Path(BASE_DIR) / "prompts" / "text" / instruction_file
    with open(prompt_path, "r") as f:
        system_instruction = f.read()

    # Build Examples (Static)
    reference_content = []
    for ex in config.get("examples", []):
         label = ex.get("label", "Example")
         path_str = ex.get("path", "")
         img_path = REFERENCES_DIR / path_str
         if img_path.exists():
             reference_content.append(label)
             reference_content.append(Image.open(img_path))

    # Model
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config={"temperature": 0.3, "response_mime_type": "application/json", "max_output_tokens": 8192},
        system_instruction=system_instruction
    )
    
    results = {}

    for tile_rel_path in FAILED_TILES:
        tile_path = Path(BASE_DIR) / tile_rel_path
        tile_name = tile_path.name
        print(f"\nProcessing: {tile_name}")
        
        successes = 0
        attempts = 3
        
        content = ["Reference Symbols:"] + reference_content + ["Target Tile:", Image.open(tile_path)]
        
        for i in range(attempts):
            try:
                print(f"  Attempt {i+1}/{attempts}...", end="", flush=True)
                start_t = time.time()
                response = model.generate_content(content)
                dur = time.time() - start_t
                
                # Check for Valid Finish Reason (1 = STOP)
                # Finish Reason 2 = MAX_TOKENS (Failure in this context)
                finish_reason = "UNKNOWN"
                if hasattr(response, 'candidates') and response.candidates:
                     finish_reason = response.candidates[0].finish_reason
                
                if finish_reason == 1:
                    print(f" SUCCESS ({dur:.2f}s)")
                    successes += 1
                else:
                    print(f" FAILED (Reason: {finish_reason}, {dur:.2f}s)")
                    
            except Exception as e:
                print(f" ERROR: {e}")
                time.sleep(2)
        
        results[tile_name] = f"{successes}/{attempts}"

    print("\n=== Experiment Results ===")
    for tile, score in results.items():
        print(f"{tile}: {score}")

if __name__ == "__main__":
    run_retries()
