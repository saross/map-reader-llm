# Pre-Reorganisation Prompt Archive

**Date**: 2025-12-23
**Reason**: Standardising prompt naming scheme for clarity

## Archived Files

### Prompt Configs (`versions/`)

| Original Name | Workflow | Modality | Notes |
|---------------|----------|----------|-------|
| `v3.2_experimental.json` | Single-shot | Text + Image | Minimal text, legacy baseline |
| `v3.5_clean.json` | Single-shot | Image-only | Visual-first, recommended |
| `v3.5_clean_pro.json` | Single-shot | Image-only | Pro model variant |
| `v4.1_recall_augmented.json` | Two-stage Proposer | Image-only | High recall |
| `v4.2_recall_high_temp.json` | Two-stage Proposer | Image-only | High temperature variant |
| `v4.6_verifier.json` | Two-stage Verifier | Image-only | Precision filter |
| `v4.6_verifier_pro.json` | Two-stage Verifier | Image-only | Pro model variant |

### System Instructions (`text/`)

| Original Name | Used By | Notes |
|---------------|---------|-------|
| `v3.0_system_instruction.md` | v3.2_experimental | Verbose text constraints |
| `v3.5_clean_instruction.md` | v3.5_clean, v3.5_clean_pro | Minimal text, visual-first |
| `v3.7_visual_instruction.md` | v4.1, v4.2 | Proposer instructions |
| `v4.6_verifier_instructions.md` | v4.6_verifier, v4.6_verifier_pro | Verifier instructions |

## New Naming Scheme

Prompts now follow this pattern: `{workflow}_{modality}[_{variant}].json`

- **Workflow**: `detect` (single-shot), `propose` (two-stage S1), `verify` (two-stage S2)
- **Modality**: `text-only`, `text-image`, `image-only`
- **Variant**: Optional suffix for model/parameter variants (e.g., `_pro`, `_liberal`)

## Migration Mapping

| Old Config | New Config |
|------------|------------|
| (V2.3 resurrected) | `detect_text-only.json` |
| `v3.2_experimental.json` | `detect_text-image.json` |
| `v3.5_clean.json` | `detect_image-only.json` |
| `v3.5_clean_pro.json` | `detect_image-only_pro.json` |
| `v4.1_recall_augmented.json` | `propose_image-only.json` |
| `v4.2_recall_high_temp.json` | `propose_image-only_liberal.json` |
| `v4.6_verifier.json` | `verify_image-only.json` |
| `v4.6_verifier_pro.json` | `verify_image-only_pro.json` |

| Old Instruction | New Instruction |
|-----------------|-----------------|
| (V2.3 extracted) | `detect_text-only.md` |
| `v3.0_system_instruction.md` | `detect_text-image.md` |
| `v3.5_clean_instruction.md` | `detect_image-only.md` |
| `v3.7_visual_instruction.md` | `propose_image-only.md` |
| `v4.6_verifier_instructions.md` | `verify_image-only.md` |
