# Prompts & Versioning

This directory contains the configurations and system instructions for the LLM inference. We use a **Modular / Data-Driven** architecture to ensure reproducibility.

## Structure

*   **`versions/*.json`**: The primary entry points. These JSON files define a specific "Experiment" or "Run configuration". They specify:
    *   The Model (e.g., `gemini-3-pro-preview`)
    *   The System Instruction File to use
    *   The Few-Shot Examples (Visual inputs and their labels)
    *   Parameters (Temperature, etc.)
*   **`text/*.md`**: The static System Instructions (the "Brain" or "Logic"). These change rarely.
    *   `v3.0_system_instruction.md`: The stable instruction set for the V3 Visual Pipeline.

## How to Create a New Version

To test a new hypothesis (e.g., "Does temperature 0.3 improve recall?"):
1.  Create `versions/v3.3_temp_test.json`.
2.  Copy content from `v3.1_baseline.json`.
3.  Modify the `temperature` field.
4.  Run: `python scripts/4_detect_mounds_batch.py --config prompts/versions/v3.3_temp_test.json`

This preserves `v3.1` exactly as it was, while capturing your new experiment as a distinct entity.
