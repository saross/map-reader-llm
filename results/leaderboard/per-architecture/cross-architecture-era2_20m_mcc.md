# Cross-architecture flat comparison — Era 2, 20 m buffer, MCC

**Generated**: Session 79 redesign (2026-04-25)
**Era**: 2
**Buffer**: 20 m
**Metric**: MCC

Each row shows the best Tier-1 representative of one architecture within Era. The score column shows the metric (F1 or MCC) at the requested buffer.

| Architecture | Best condition | MCC | F1 95% CI (at 20 m) | Tier (within stratum) | K | t | Track |
|:---|:---|---:|:---:|---:|---:|---:|:---|
| single-pass | `h11-pvd-pro-medium-text-baseline` | +0.752 | [0.732, 0.797] | 1 | 1 | 1 | text |
| consensus | `h11-pvd-pro-high-image-n5` | +0.761 | [0.667, 0.732] | 1 | 5 | 3 | image |
| single-pass+PV | `pv-cascade-adversarial-checklist` | +0.432 | [0.446, 0.549] | 1 | 1 | 1 | text |
| pv | `pv-min-image-t0.3-n5` | +0.841 | [0.750, 0.803] | 1 | 5 | 1 | image |

