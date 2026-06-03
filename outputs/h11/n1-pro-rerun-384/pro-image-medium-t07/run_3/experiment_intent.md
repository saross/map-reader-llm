# Experiment Intent

Written at launch time by `scripts/4_detect_mounds_batch.py` via `scripts/lib_experiment_intent.py`.

## Hypothesis

- **ID**: H8-3
- **Description**: (no requirements registered)

## Configs

- **Variant config**: `prompts/configs/library_plus-hp.json`
- **Base config**: `(not recorded)`
- **Variant version**: `library_plus-hp`

## Verified values

| Field | Value |
|---|---|
| `model` | gemini-3.1-pro |
| `instruction_file` | detect_brief-text-image.md |
| `include_example_images` | **true** |
| `temperature` | 0.7 |
| `thinking_level` | medium |
| `max_output_tokens` | 8192 |

## Transmission check

- No registered varied factor for this hypothesis; transmission check skipped.

## Config diff vs base

Diff skipped: no `base_config` field in the variant (legacy config), or the base config file could not be loaded.

## Provenance

- Git commit: `5c3480fd`
- Launched at: 2026-06-03T12:04:30.004722+00:00
- Python: 3.13.3
- User: shawn
