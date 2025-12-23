
import json
from pathlib import Path

def generate_config():
    # Load v4.6 Config (Base Text-Free)
    base_config_path = Path("prompts/versions/v4.6_verifier.json")
    with open(base_config_path) as f:
        base_config = json.load(f)
        
    examples = base_config.get("examples", [])
    
    new_config = {
        "version": "v4.9_gemini3_lowtemp",
        "model": "gemini-3-flash-preview", 
        "instruction_file": "v4.6_verifier_instructions.md",
        "temperature": 0.2, # Low Temp for Stability (User Request)
        "visual_cot": True,
        "confidence_rubric": True,
        "grid_overlay": False,
        "examples": examples
    }
    
    with open("prompts/versions/v4.9_gemini3_lowtemp.json", "w") as f:
        json.dump(new_config, f, indent=4)
        
    print(f"Generated v4.9 config (Gemini 3, Temp 0.2).")

if __name__ == "__main__":
    generate_config()
