
import json
from pathlib import Path

def generate_config():
    # Load v4.6 Config (Base Text-Free with 48 examples)
    base_config_path = Path("prompts/versions/v4.6_verifier.json")
    with open(base_config_path) as f:
        base_config = json.load(f)
        
    examples = base_config.get("examples", [])
    
    new_config = {
        "version": "v4.9_gemini3_n1",
        "model": "gemini-3-flash-preview", # Frontier Model
        "instruction_file": "v4.6_verifier_instructions.md", # Use v4.6 (Text Free) instructions
        "temperature": 0.7, # Standard Temperature
        "visual_cot": True,
        "confidence_rubric": True,
        "grid_overlay": False,
        "examples": examples
    }
    
    with open("prompts/versions/v4.9_gemini3_n1.json", "w") as f:
        json.dump(new_config, f, indent=4)
        
    print(f"Generated v4.9 config (Gemini 3, Temp 0.7, No Consensus).")

if __name__ == "__main__":
    generate_config()
