# consensus-384-UNINTENDED-T1.0

## What happened

These runs were intended as the **MINIMAL thinking, T=0.7 consensus baseline**
at 384px tile size (30 runs × 487 tiles, Flash). However, they executed at
**T=1.0** due to a config propagation failure: the `detect_brief-text.json`
prompt config has `"temperature": 1.0` hardcoded, and `run_phase2.py` used the
config's default instead of the YAML-specified `fixed.temperature: 0.7`.

Discovered during the comprehensive configuration audit (Session 57,
2026-03-25). See protocol errata E43.

## Data validity

The data is **scientifically valid as T=1.0 consensus data**. It is used in
the T=0.7 vs T=1.0 temperature sensitivity analysis, which found T=0.7
dramatically outperforms T=1.0 at all pool sizes (dF1 ~+0.15, p<0.0001).

## Corrected baseline

The corrected T=0.7 baseline is at:
`outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/`

## Do not delete

Per project policy: archive, never delete. This data has analytical value
as an unplanned temperature comparison.
