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
| `model` | gemini-3.5-flash |
| `instruction_file` | detect_brief-text.md |
| `include_example_images` | **false** |
| `temperature` | 0.7 |
| `thinking_level` | minimal |
| `max_output_tokens` | 8192 |

## Transmission check

- The varied factor is `include_example_images`.
- `include_example_images` is **false**.
- The varied factor is expected to reach the API payload.

## Config diff vs base

Diff skipped: no `base_config` field in the variant (legacy config), or the base config file could not be loaded.

## Provenance

- Git commit: `8cc7d5a6b`
- Launched at: 2026-06-10T13:41:00.025131+00:00
- Python: 3.12.3
- User: shawn
