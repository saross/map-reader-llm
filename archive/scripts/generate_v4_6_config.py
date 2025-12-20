
import json
from pathlib import Path

def generate_config():
    # Load v4.5 Base
    base_config_path = Path("prompts/versions/v4.5_verifier.json")
    with open(base_config_path) as f:
        base_config = json.load(f)
        
    examples = base_config.get("examples", [])
    
    # Mined Hard Negatives (Now in inputs/references)
    ref_dir = Path("inputs/references")
    
    fp_count = 0
    for img in ref_dir.glob("hard_negative_fp_*.png"):
        examples.append({
            "label": "Negative Example: Hard Mined (False Positive)",
            "path": str(img.name)
        })
        fp_count += 1
        
    # Mined Hard Positives
    fn_count = 0
    for img in ref_dir.glob("hard_positive_fn_*.png"):
        examples.append({
            "label": "Positive Example: Hard Mined (False Negative)",
            "path": str(img.name)
        })
        fn_count += 1
        
    print(f"Added {fp_count} FPs and {fn_count} FNs.")

    new_config = {
        "version": "v4.6_verifier",
        # Switch to Gemini 3 Flash
        "model": "gemini-3-flash-preview",
        "instruction_file": "v4.6_verifier_instructions.md",
        "temperature": 0.0,
        "visual_cot": True,
        "confidence_rubric": True,
        "examples": examples
    }
    
    with open("prompts/versions/v4.6_verifier.json", "w") as f:
        json.dump(new_config, f, indent=4)
        
    print(f"Generated v4.6 config with {len(examples)} examples.")

if __name__ == "__main__":
    generate_config()
