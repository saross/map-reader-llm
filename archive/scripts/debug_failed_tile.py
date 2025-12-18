import json
import time
import os
import sys
from pathlib import Path
from PIL import Image
import google.generativeai as genai
import sys

# Add parent directory to path to import config
# script is in archive/scripts/, so we need to go up 3 levels to reach root
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import GOOGLE_API_KEY, BASE_DIR, REFERENCES_DIR

# Hardcoded Config from v3.2_experimental.json
MODEL_NAME = "gemini-3-flash-preview" # User confirmed Flash
INSTRUCTION_FILE = "v3.0_system_instruction.md"
TARGET_TILE_PATH = Path(BASE_DIR) / "inputs" / "tiles" / "K-35-052-4_32635" / "K-35-052-4_32635_x3584_y448.png"

# Load v3.2 Config
CONFIG_PATH = Path(BASE_DIR) / "prompts" / "versions" / "v3.2_experimental.json"

def debug_tile():
    print(f"DEBUG: Processing {TARGET_TILE_PATH}")
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY missing")
        return

    genai.configure(api_key=GOOGLE_API_KEY)
    
    # Load Config
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    
    print(f"Model: {MODEL_NAME}")

    # Load System Prompt
    instruction_file = config.get("instruction_file", "v3.0_system_instruction.md")
    prompt_path = Path(BASE_DIR) / "prompts" / "text" / instruction_file
    with open(prompt_path, "r") as f:
        system_instruction = f.read()

    # Build Content with FULL Examples
    content_parts = ["Here are the Reference Symbols:"]
    
    for ex in config.get("examples", []):
        label = ex.get("label", "Example")
        path_str = ex.get("path", "")
        img_path = REFERENCES_DIR / path_str
        
        if img_path.exists():
            content_parts.append(label)
            content_parts.append(Image.open(img_path))
        else:
            print(f"Warning: Reference {path_str} not found")

    content_parts.append("Now, find detection instances in the Target Map Tile:")
    content_parts.append(Image.open(TARGET_TILE_PATH))

    # Model
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config={"temperature": config.get("temperature", 0.1), "response_mime_type": "application/json", "max_output_tokens": 8192},
        system_instruction=system_instruction
    )

    print("Sending request...")
    try:
        response = model.generate_content(content_parts)
        print(f"Response Object ID: {id(response)}")
        
        # Verbose Inspection
        if hasattr(response, 'candidates'):
            print(f"Candidate Count: {len(response.candidates)}")
            for i, cand in enumerate(response.candidates):
                print(f"Candidate {i}: Finish Reason: {cand.finish_reason}")
                print(f"Candidate {i}: Token Count: {cand.token_count}")
                if cand.content and cand.content.parts:
                    print(f"Candidate {i} Parts: {len(cand.content.parts)}")
                    text = cand.content.parts[0].text
                    print(f"--- START PARTIAL TEXT ({len(text)} chars) ---")
                    print(text[:1000]) # First 1k
                    print("... [SNIP] ...")
                    print(text[-1000:]) # Last 1k to check for loops
                    print("--- END PARTIAL TEXT ---")
                else:
                    print(f"Candidate {i} has NO content parts.")
        
    except Exception as e:
        print(f"EXCEPTION: {e}")
        # If response exists, dump it
        if 'response' in locals():
             if hasattr(response, 'candidates'):
                print(response.candidates)

if __name__ == "__main__":
    debug_tile()
