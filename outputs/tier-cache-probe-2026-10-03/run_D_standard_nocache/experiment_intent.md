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
| `model` | gemini-3-flash |
| `instruction_file` | detect_brief-text-image.md |
| `instruction_file_sha256` | e169b7237b853eeaad990fc2e54fbd7214afb435d85c8e444a4a784432200e12 |
| `include_example_images` | **true** |
| `temperature` | 0.0 |
| `thinking_level` | minimal |
| `max_output_tokens` | 8192 |

## Transmission check

- No registered varied factor for this hypothesis; transmission check skipped.

## Config diff vs base

Diff skipped: no `base_config` field in the variant (legacy config), or the base config file could not be loaded.

## Provenance

- Git commit: `651a2eb90`
- Launched at: 2026-10-03T12:05:59.374125+00:00
- Python: 3.13.3
- User: shawn
