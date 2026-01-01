"""
Generate Overnight Configs (DEPRECATED)

This script previously generated _pro variants of configs.
Model selection is now a runtime parameter (--model flag).

Example:
    python scripts/4_detect_mounds_batch.py \\
        --config prompts/configs/detect_image-only.json \\
        --model gemini-3-pro-preview
"""

def generate_overnight_configs():
    print("Note: Model-specific configs are deprecated.")
    print("Use --model flag at runtime instead.")
    print("Example: --config prompts/configs/detect_image-only.json --model gemini-3-pro-preview")

if __name__ == "__main__":
    generate_overnight_configs()
