
import json
from pathlib import Path

def generate_overnight_configs():
    # 1. Job A: v3.5 using Gemini 3 Pro
    with open("prompts/versions/v3.5_clean.json") as f:
        v35_config = json.load(f)
    v35_pro = v35_config.copy()
    v35_pro["version"] = "v3.5_clean_pro"
    v35_pro["model"] = "gemini-3-pro-preview"
    with open("prompts/versions/v3.5_clean_pro.json", "w") as f:
        json.dump(v35_pro, f, indent=4)

    # 2. Job C: v4.6 Verifier using Gemini 3 Pro
    with open("prompts/versions/v4.6_verifier.json") as f:
        v46_config = json.load(f)
    v46_pro = v46_config.copy()
    v46_pro["version"] = "v4.6_verifier_pro"
    v46_pro["model"] = "gemini-3-pro-preview"
    with open("prompts/versions/v4.6_verifier_pro.json", "w") as f:
        json.dump(v46_pro, f, indent=4)
        
    print("Generated: v3.5_clean_pro.json, v4.6_verifier_pro.json")

if __name__ == "__main__":
    generate_overnight_configs()
