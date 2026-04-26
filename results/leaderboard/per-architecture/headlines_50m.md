# Headlines — top-3 per stratum @ 50 m buffer

**Generated**: 2026-04-26T02:02:19.144875+00:00

Top-3 conditions in Tier 1 of each populated (era, architecture) stratum at q=0.05, separately for F1 and MCC. **Buffer = 50 m** for F1; MCC is buffer-invariant by methodology (per Obs 280) but the F1@50m column shows the same condition's F1 value at this buffer for cross-reference.

For the primary (20 m) headline summary, see `headlines.md`. For the methodology reference, see `README.md` and `docs/notes/reflections/working-notes.md` Obs 279 + 280.

## Era 1 / single-pass

### F1 (50 m)

| # | Condition | F1 [95% CI] | P | R |
|--:|:---|:---|---:|---:|
| 1 | `h4-canonical-last` | 0.724 [0.681, 0.757] | 0.610 | 0.889 |

### MCC

| # | Condition | MCC | F1@50m |
|--:|:---|---:|---:|
| 1 | `h5-track1-image-verbose` | +0.281 | 0.726 |
| 2 | `h5-track1-image-terse` | +0.223 | 0.717 |
| 3 | `h4-config-default` | +0.214 | 0.734 |

## Era 1 / consensus

### F1 (50 m)

| # | Condition | F1 [95% CI] | P | R |
|--:|:---|:---|---:|---:|
| 1 | `h3-high-track2-text-T1.0` | 0.809 [0.766, 0.849] | 0.898 | 0.737 |
| 2 | `h3-high-track2-text-T0.3` | 0.813 [0.772, 0.849] | 0.850 | 0.779 |
| 3 | `h3-high-track2-text-T0.7` | 0.814 [0.771, 0.848] | 0.866 | 0.768 |

### MCC

| # | Condition | MCC | F1@50m |
|--:|:---|---:|---:|
| 1 | `h9-track1-image-h9-B-v4` | +0.714 | 0.788 |
| 2 | `h9-track1-image-h9-A-p5` | +0.694 | 0.806 |
| 3 | `h9-track1-image-h9-A-p3` | +0.691 | 0.779 |

## Era 1 / single-pass+PV

_(empty stratum)_

## Era 1 / pv

_(empty stratum)_

## Era 2 / single-pass

### F1 (50 m)

| # | Condition | F1 [95% CI] | P | R |
|--:|:---|:---|---:|---:|
| 1 | `h11-pvd-pro-medium-text-baseline` | 0.802 [0.761, 0.841] | 0.807 | 0.798 |
| 2 | `h11-pvd-pro-medium-image-baseline` | 0.778 [0.740, 0.812] | 0.715 | 0.853 |

### MCC

| # | Condition | MCC | F1@50m |
|--:|:---|---:|---:|
| 1 | `h11-pvd-pro-medium-text-baseline` | +0.752 | 0.802 |
| 2 | `h11-pvd-pro-medium-image-baseline` | +0.734 | 0.778 |

## Era 2 / consensus

### F1 (50 m)

| # | Condition | F1 [95% CI] | P | R |
|--:|:---|:---|---:|---:|
| 1 | `h11-pvd-pro-high-text-n5` | 0.854 [0.817, 0.885] | 0.947 | 0.777 |
| 2 | `h11-pvd-flash-high-text-n5` | 0.826 [0.793, 0.858] | 0.846 | 0.807 |

### MCC

| # | Condition | MCC | F1@50m |
|--:|:---|---:|---:|
| 1 | `h11-pvd-pro-high-image-n5` | +0.761 | 0.865 |
| 2 | `scale4-optimal-487` | +0.745 | 0.831 |
| 3 | `h11-pvd-pro-high-text-n5` | +0.727 | 0.854 |

## Era 2 / single-pass+PV

### F1 (50 m)

| # | Condition | F1 [95% CI] | P | R |
|--:|:---|:---|---:|---:|
| 1 | `pv-checklist-image` | 0.547 [0.460, 0.612] | 0.638 | 0.478 |
| 2 | `pv-checklist-text` | 0.537 [0.453, 0.602] | 0.616 | 0.476 |
| 3 | `pv-brief-image` | 0.536 [0.454, 0.605] | 0.626 | 0.469 |

### MCC

| # | Condition | MCC | F1@50m |
|--:|:---|---:|---:|
| 1 | `pv-cascade-adversarial-checklist` | +0.432 | 0.521 |
| 2 | `pv-adversarial-text` | +0.431 | 0.483 |
| 3 | `pv-adversarial-image` | +0.416 | 0.511 |

## Era 2 / pv

### F1 (50 m)

| # | Condition | F1 [95% CI] | P | R |
|--:|:---|:---|---:|---:|
| 1 | `pv-flash-high-text-16of30` | 0.904 [0.878, 0.928] | 0.930 | 0.880 |
| 2 | `pv-high-text-t0.3-n5` | 0.908 [0.882, 0.929] | 0.936 | 0.880 |
| 3 | `session-78-text-comparative` | 0.911 [0.886, 0.934] | 0.955 | 0.871 |

### MCC

| # | Condition | MCC | F1@50m |
|--:|:---|---:|---:|
| 1 | `pv-min-image-t0.3-n5` | +0.841 | 0.862 |
| 2 | `pv-n1-image-t0-n3` | +0.839 | 0.872 |
| 3 | `pv-min-image-t0.7-n5` | +0.838 | 0.881 |

## Era 3 / single-pass

_(empty stratum)_

## Era 3 / consensus

### F1 (50 m)

| # | Condition | F1 [95% CI] | P | R |
|--:|:---|:---|---:|---:|
| 1 | `h8v2-scale-4` | 0.816 [0.773, 0.856] | 0.914 | 0.737 |
| 2 | `h12v2-r1-hn-heavy` | 0.833 [0.799, 0.866] | 0.823 | 0.843 |
| 3 | `h8v2-scale-8` | 0.815 [0.777, 0.850] | 0.817 | 0.812 |

### MCC

| # | Condition | MCC | F1@50m |
|--:|:---|---:|---:|
| 1 | `h8v2-scale-4` | +0.772 | 0.816 |
| 2 | `h8v2-scale-8` | +0.739 | 0.815 |
| 3 | `h12v2-r3-hp-heavy` | +0.733 | 0.819 |

## Era 3 / single-pass+PV

_(empty stratum)_

## Era 3 / pv

_(empty stratum)_
