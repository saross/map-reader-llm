# single-pass-384-UNINTENDED-T1.0

## What happened

These runs were intended as the **single-pass T=0.0 baseline** at 384px tile
size (10 runs × 240 tiles, Flash MINIMAL). However, they executed at **T=1.0**
due to the same config propagation failure as consensus-384: the
`detect_brief-text.json` prompt config has `"temperature": 1.0` hardcoded, and
the YAML-specified `fixed.temperature: 0.0` / `carried_forward.optimal_temperature: 0.0`
was not propagated to the API call.

Discovered during the comprehensive configuration audit (Session 57,
2026-03-25). See protocol errata E44.

## Data validity

The data is valid as T=1.0 single-pass data but should NOT be used as the
T=0.0 deterministic baseline for the tile-size comparison (H11).

## Corrected rerun

The corrected T=0.0 rerun (487 tiles, matching full evaluation area) is at:
`outputs/retest/h11-single-pass-384-t0/`

## Do not delete

Per project policy: archive, never delete.
