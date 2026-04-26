# Headlines — top-3 per stratum @ 100 m buffer

**Generated**: 2026-04-26T02:02:19.194536+00:00

Top-3 conditions in Tier 1 of each populated (era, architecture) stratum at q=0.05, separately for F1 and MCC. **Buffer = 100 m** for F1; MCC is buffer-invariant by methodology (per Obs 280) but the F1@100m column shows the same condition's F1 value at this buffer for cross-reference.

For the primary (20 m) headline summary, see `headlines.md`. For the methodology reference, see `README.md` and `docs/notes/reflections/working-notes.md` Obs 279 + 280.

## Era 1 / single-pass

### F1 (100 m)

| # | Condition | F1 [95% CI] | P | R |
|--:|:---|:---|---:|---:|
| 1 | `h4-canonical-last` | 0.730 [0.688, 0.762] | 0.615 | 0.896 |

### MCC

| # | Condition | MCC | F1@100m |
|--:|:---|---:|---:|
| 1 | `h5-track1-image-verbose` | +0.281 | 0.742 |
| 2 | `h5-track1-image-terse` | +0.223 | 0.738 |
| 3 | `h4-config-default` | +0.214 | 0.753 |

## Era 1 / consensus

### F1 (100 m)

| # | Condition | F1 [95% CI] | P | R |
|--:|:---|:---|---:|---:|
| 1 | `h3-high-track2-text-T1.0` | 0.811 [0.768, 0.850] | 0.900 | 0.738 |
| 2 | `h3-high-track2-text-T0.3` | 0.815 [0.775, 0.851] | 0.852 | 0.781 |
| 3 | `h3-high-track2-text-T0.7` | 0.816 [0.774, 0.849] | 0.868 | 0.770 |

### MCC

| # | Condition | MCC | F1@100m |
|--:|:---|---:|---:|
| 1 | `h9-track1-image-h9-B-v4` | +0.714 | 0.807 |
| 2 | `h9-track1-image-h9-A-p5` | +0.694 | 0.825 |
| 3 | `h9-track1-image-h9-A-p3` | +0.691 | 0.790 |

## Era 1 / single-pass+PV

_(empty stratum)_

## Era 1 / pv

_(empty stratum)_

## Era 2 / single-pass

### F1 (100 m)

| # | Condition | F1 [95% CI] | P | R |
|--:|:---|:---|---:|---:|
| 1 | `h11-pvd-pro-medium-text-baseline` | 0.807 [0.765, 0.845] | 0.812 | 0.802 |
| 2 | `h11-pvd-pro-medium-image-baseline` | 0.794 [0.755, 0.829] | 0.730 | 0.871 |

### MCC

| # | Condition | MCC | F1@100m |
|--:|:---|---:|---:|
| 1 | `h11-pvd-pro-medium-text-baseline` | +0.752 | 0.807 |
| 2 | `h11-pvd-pro-medium-image-baseline` | +0.734 | 0.794 |

## Era 2 / consensus

### F1 (100 m)

| # | Condition | F1 [95% CI] | P | R |
|--:|:---|:---|---:|---:|
| 1 | `h11-pvd-pro-high-text-n5` | 0.859 [0.823, 0.890] | 0.952 | 0.782 |
| 2 | `h11-pvd-flash-high-text-n5` | 0.826 [0.793, 0.858] | 0.846 | 0.807 |

### MCC

| # | Condition | MCC | F1@100m |
|--:|:---|---:|---:|
| 1 | `h11-pvd-pro-high-image-n5` | +0.761 | 0.885 |
| 2 | `scale4-optimal-487` | +0.745 | 0.835 |
| 3 | `h11-pvd-pro-high-text-n5` | +0.727 | 0.859 |

## Era 2 / single-pass+PV

### F1 (100 m)

| # | Condition | F1 [95% CI] | P | R |
|--:|:---|:---|---:|---:|
| 1 | `pv-checklist-image` | 0.552 [0.468, 0.617] | 0.644 | 0.483 |
| 2 | `pv-checklist-text` | 0.542 [0.460, 0.606] | 0.622 | 0.480 |
| 3 | `pv-brief-image` | 0.541 [0.462, 0.610] | 0.632 | 0.474 |

### MCC

| # | Condition | MCC | F1@100m |
|--:|:---|---:|---:|
| 1 | `pv-cascade-adversarial-checklist` | +0.432 | 0.526 |
| 2 | `pv-adversarial-text` | +0.431 | 0.486 |
| 3 | `pv-adversarial-image` | +0.416 | 0.517 |

## Era 2 / pv

### F1 (100 m)

| # | Condition | F1 [95% CI] | P | R |
|--:|:---|:---|---:|---:|
| 1 | `pv-flash-high-text-16of30` | 0.909 [0.884, 0.931] | 0.934 | 0.885 |
| 2 | `pv-high-text-t0.3-n5` | 0.912 [0.887, 0.934] | 0.941 | 0.885 |
| 3 | `session-78-text-comparative` | 0.916 [0.891, 0.938] | 0.960 | 0.876 |

### MCC

| # | Condition | MCC | F1@100m |
|--:|:---|---:|---:|
| 1 | `pv-min-image-t0.3-n5` | +0.841 | 0.869 |
| 2 | `pv-n1-image-t0-n3` | +0.839 | 0.881 |
| 3 | `pv-min-image-t0.7-n5` | +0.838 | 0.888 |

## Era 3 / single-pass

_(empty stratum)_

## Era 3 / consensus

### F1 (100 m)

| # | Condition | F1 [95% CI] | P | R |
|--:|:---|:---|---:|---:|
| 1 | `h8v2-scale-4` | 0.823 [0.782, 0.863] | 0.922 | 0.743 |
| 2 | `h12v2-r1-hn-heavy` | 0.842 [0.808, 0.874] | 0.832 | 0.853 |
| 3 | `h8v2-scale-8` | 0.827 [0.789, 0.863] | 0.830 | 0.825 |

### MCC

| # | Condition | MCC | F1@100m |
|--:|:---|---:|---:|
| 1 | `h8v2-scale-4` | +0.772 | 0.823 |
| 2 | `h8v2-scale-8` | +0.739 | 0.827 |
| 3 | `h12v2-r3-hp-heavy` | +0.733 | 0.834 |

## Era 3 / single-pass+PV

_(empty stratum)_

## Era 3 / pv

_(empty stratum)_
