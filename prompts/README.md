# Prompts & Versioning

This directory contains the configurations and system instructions for LLM inference. We use a **Modular / Data-Driven** architecture to ensure reproducibility.

## Structure

- **`configs/*.json`**: Run configurations. See **[docs/PIPELINES.md](../docs/PIPELINES.md)** for active pipelines.
- **`system-instructions/*.md`**: System instructions (the "Brain" or "Logic").

## Naming Convention

Prompts follow this pattern: `{workflow}_{modality}.json`

| Component | Values | Meaning |
|-----------|--------|---------|
| **workflow** | `detect`, `propose`, `verify` | Single-shot, Two-stage S1, Two-stage S2 |
| **modality** | `text-only`, `text-image`, `image-only` | What drives the prompt |

Optional variant suffixes (e.g., `_liberal`) indicate parameter variations within the same workflow/modality.

**Note:** Model selection (Flash vs Pro) is a runtime parameter passed to the script, not encoded in the prompt config.

## Active Configs

| Config | Instruction | Workflow | Modality |
|--------|-------------|----------|----------|
| `detect_text-only.json` | `detect_text-only.md` | Single-shot | Text only |
| `detect_text-image.json` | `detect_text-image.md` | Single-shot | Text + Image |
| `detect_image-only.json` | `detect_image-only.md` | Single-shot | Image only |
| `propose_image-only.json` | `propose_image-only.md` | Two-stage S1 | Image only |
| `verify_image-only.json` | `verify_image-only.md` | Two-stage S2 | Image only |

## Migration from Old Names (2025-12-23)

The prompts were reorganised for clarity. Old versions archived at `archive/prompts-pre-reorganisation/`.

### Config Files

| Old Name | New Name |
|----------|----------|
| *(V2.3 resurrected)* | `detect_text-only.json` |
| `v3.2_experimental.json` | `detect_text-image.json` |
| `v3.5_clean.json` | `detect_image-only.json` |
| `v3.5_clean_pro.json` | *(deleted — model is runtime param)* |
| `v4.1_recall_augmented.json` | *(deleted — v4.2 performed better)* |
| `v4.2_recall_high_temp.json` | `propose_image-only.json` |
| `v4.6_verifier.json` | `verify_image-only.json` |
| `v4.6_verifier_pro.json` | *(deleted — model is runtime param)* |

### Instruction Files

| Old Name | New Name |
|----------|----------|
| *(V2.3 extracted)* | `detect_text-only.md` |
| `v3.0_system_instruction.md` | `detect_text-image.md` |
| `v3.5_clean_instruction.md` | `detect_image-only.md` |
| `v3.7_visual_instruction.md` | `propose_image-only.md` |
| `v4.6_verifier_instructions.md` | `verify_image-only.md` |

## How to Create a New Version

To test a new hypothesis (e.g., "Does removing hard negatives improve recall?"):

1. Create `configs/propose_image-only_no-negatives.json`
2. Copy content from `propose_image-only.json`
3. Modify the `examples` array
4. Run: `python scripts/4_detect_mounds_batch.py --config prompts/configs/propose_image-only_no-negatives.json`

This preserves the baseline exactly while capturing your experiment as a distinct entity.
