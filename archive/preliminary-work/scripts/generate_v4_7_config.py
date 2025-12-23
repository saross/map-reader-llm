
import json
from pathlib import Path

def generate_config():
    # Load v4.6 Config (It has the 48 examples)
    base_config_path = Path("prompts/versions/v4.6_verifier.json")
    with open(base_config_path) as f:
        base_config = json.load(f)
        
    examples = base_config.get("examples", [])
    
    new_config = {
        "version": "v4.7_gemini3_grid",
        "model": "gemini-3-flash-preview",
        "instruction_file": "v4.7_verifier_instructions.md",
        "temperature": 0.0,
        "visual_cot": True,
        "confidence_rubric": True,
        "grid_overlay": True, # Triggers grid usage in script
        "examples": examples
    }
    
    with open("prompts/versions/v4.7_gemini3_grid.json", "w") as f:
        json.dump(new_config, f, indent=4)
        
    print(f"Generated v4.7 config with Grid Overlay enabled.")

if __name__ == "__main__":
    generate_config()
