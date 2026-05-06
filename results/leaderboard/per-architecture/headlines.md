# Per-architecture headline statistics @ 20 m

**Generated**: 2026-05-06T00:25:57.146766+00:00

Tier-1 top per stratum + overall counts. All numbers are at 20 m buffer. CIs are stratified bootstrap (1,000 iterations, seed 42).

## Tier-1 top per (era, architecture)

| Era | Architecture | Top condition | Track | F1 | 95% CI | Vote t | Verifier | Prob t | #Tier-1 | #Total |
|:---:|:-------------|:--------------|:-----:|---:|:------:|:-----:|:---------|:-----:|---:|---:|
| 1 | single-pass | `h4-canonical-last` | image | 0.631 | [0.609, 0.657] | 1 | — | — | 21 | 21 |
| 1 | consensus | `h3-high-track2-text-T1.0` | text | 0.775 | [0.750, 0.798] | 23 | — | — | 4 | 72 |
| 1 | single-pass+PV | _(empty stratum)_ | — | — | — | — | — | — | 0 | 0 |
| 1 | pv | _(empty stratum)_ | — | — | — | — | — | — | 0 | 0 |
| 2 | single-pass | `h11-pvd-pro-medium-text-baseline` | text | 0.763 | [0.732, 0.797] | 1 | — | — | 1 | 6 |
| 2 | consensus | `h11-pvd-pro-high-text-n5` | text | 0.836 | [0.810, 0.859] | 6 | — | — | 2 | 29 |
| 2 | single-pass+PV | `pv-checklist-image` | image | 0.531 | [0.473, 0.580] | 1 | checklist-image | — | 8 | 8 |
| 2 | pv | `pv-flash-high-text-16of30` | text | 0.890 | [0.874, 0.910] | 16 | v1 (adversarial-text canonical) | 0.20 | 8 | 44 |
| 3 | single-pass | _(empty stratum)_ | — | — | — | — | — | — | 0 | 0 |
| 3 | consensus | `h8v2-scale-4` | image | 0.733 | [0.699, 0.760] | 4 | — | — | 14 | 14 |
| 3 | single-pass+PV | _(empty stratum)_ | — | — | — | — | — | — | 0 | 0 |
| 3 | pv | _(empty stratum)_ | — | — | — | — | — | — | 0 | 0 |

## Architecture deltas (within Era 2)

- Era 2: PV Tier-1 top (0.890) vs Consensus Tier-1 top (0.836) → ΔF1 = +0.054
- Era 2: Consensus Tier-1 top (0.836) vs Single-pass Tier-1 top (0.763) → ΔF1 = +0.073 (K-pass benefit)
- Era 2: Single-pass + PV Tier-1 top (0.531) vs Single-pass (raw) Tier-1 top (0.763) → ΔF1 = -0.232 (verifier benefit @ K=1)
