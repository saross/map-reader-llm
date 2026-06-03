# Experiment Intent

Written at launch time by `scripts/4_detect_mounds_batch.py` via `scripts/lib_experiment_intent.py`.

## Hypothesis

- **ID**: H1
- **Description**: Modality and elaboration level — tests how text presence and detail level affect detection performance.
- **Factor being varied**: `include_example_images`

## Configs

- **Variant config**: `prompts/configs/detect_brief-text.json`
- **Base config**: `(not recorded)`
- **Variant version**: `detect_brief-text`

## Verified values

| Field | Value |
|---|---|
| `model` | gemini-3.1-pro |
| `instruction_file` | detect_brief-text.md |
| `include_example_images` | **false** |
| `temperature` | 0.0 |
| `thinking_level` | high |
| `max_output_tokens` | 8192 |

## Transmission check

- The varied factor is `include_example_images`.
- `include_example_images` is **false**.
- The varied factor is expected to reach the API payload.

## Config diff vs base

Diff skipped: no `base_config` field in the variant (legacy config), or the base config file could not be loaded.

## Provenance

- Git commit: `5a1c3f90`
- Launched at: 2026-06-03T05:40:24.175355+00:00
- Python: 3.13.3
- User: shawn
