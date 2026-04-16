# Experiment Intent

Written at launch time by `scripts/4_detect_mounds_batch.py` via `scripts/lib_experiment_intent.py`.

## Hypothesis

- **ID**: H12
- **Description**: Hard-positive to hard-negative ratio — tests whether the HP:HN balance in the few-shot library affects detection performance.
- **Factor being varied**: `examples`

## Configs

- **Variant config**: `prompts/configs/h12/v2/detect_h12_r1-hn-heavy_v2.json`
- **Base config**: `(not recorded)`
- **Variant version**: `detect_h12_r1-hn-heavy_v2`

## Verified values

| Field | Value |
|---|---|
| `model` | gemini-3-flash |
| `instruction_file` | detect_brief-text-image.md |
| `include_example_images` | **true** |
| `temperature` | 0.7 |
| `thinking_level` | high |
| `max_output_tokens` | 8192 |

## Transmission check

- The varied factor is `examples`.
- `include_example_images` is **true**.
- The varied factor is expected to reach the API payload.

## Config diff vs base

Diff skipped: no `base_config` field in the variant (legacy config), or the base config file could not be loaded.

## Provenance

- Git commit: `d89596fa`
- Launched at: 2026-04-15T13:45:20.730036+00:00
- Python: 3.13.3
- User: shawn
