# Experiment Intent

Written at launch time by `scripts/4_detect_mounds_batch.py` via `scripts/lib_experiment_intent.py`.

## Hypothesis

- **ID**: H1
- **Description**: Modality and elaboration level — tests how text presence and detail level affect detection performance.
- **Factor being varied**: `include_example_images`

## Configs

- **Variant config**: `prompts/configs/detect_brief-text-image.json`
- **Base config**: `(not recorded)`
- **Variant version**: `detect_brief-text-image`

## Verified values

| Field | Value |
|---|---|
| `model` | gemini-3.7-flash |
| `instruction_file` | detect_brief-text-image.md |
| `instruction_file_sha256` | e169b7237b853eeaad990fc2e54fbd7214afb435d85c8e444a4a784432200e12 |
| `include_example_images` | **true** |
| `temperature` | 0.7 |
| `thinking_level` | low |
| `max_output_tokens` | 8192 |

## Transmission check

- The varied factor is `include_example_images`.
- `include_example_images` is **true**.
- The varied factor is expected to reach the API payload.

## Config diff vs base

Diff skipped: no `base_config` field in the variant (legacy config), or the base config file could not be loaded.

## Provenance

- Git commit: `7750d194b`
- Launched at: 2026-09-13T15:00:43.711632+00:00
- Python: 3.13.3
- User: shawn
