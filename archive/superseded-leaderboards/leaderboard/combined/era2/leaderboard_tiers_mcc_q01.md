# Leaderboard (MCC tiers) — 20m buffer

**Generated**: 2026-05-06T01:12:50.361001+00:00
**Tiering metric**: MCC
**FDR q**: 0.01
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 87 in 8 tier(s)

## Tier 1 (MCC: 0.800–0.841)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | pv-min-image-t0.3-n5 | PV | 2 | image | 5 | 1 | 0.841 | 0.777 | [0.750, 0.803] | 0.803 | 0.752 |
| 2 | pv-n1-image-t0-n3 | PV | 2 | image | 3 | 1 | 0.839 | 0.767 | [0.743, 0.793] | 0.758 | 0.777 |
| 3 | pv-min-image-t0.7-n5 | PV | 2 | image | 5 | 1 | 0.838 | 0.773 | [0.747, 0.797] | 0.786 | 0.761 |
| 4 | pv-min-image-t0.3-n10 | PV | 2 | image | 10 | 1 | 0.837 | 0.782 | [0.752, 0.805] | 0.812 | 0.754 |
| 5 | pv-high-image-t0.7-n5 | PV | 2 | image | 5 | 1 | 0.836 | 0.787 | [0.761, 0.814] | 0.807 | 0.768 |
| 6 | pv-scale4-optimal-n5 | PV | 2 | image | 5 | 1 | 0.835 | 0.763 | [0.733, 0.791] | 0.800 | 0.729 |
| 7 | session-78-image-adversarial | PV | 2 | image | 5 | 1 | 0.831 | 0.787 | [0.760, 0.814] | 0.789 | 0.784 |
| 8 | session-78-image-comparative | PV | 2 | image | 5 | 1 | 0.830 | 0.786 | [0.760, 0.813] | 0.787 | 0.784 |
| 9 | session-78-image-brief | PV | 2 | image | 5 | 1 | 0.829 | 0.784 | [0.758, 0.812] | 0.783 | 0.786 |
| 10 | pv-high-image-t1.0-n5 | PV | 2 | image | 5 | 1 | 0.822 | 0.734 | [0.698, 0.761] | 0.756 | 0.713 |
| 11 | pv-min-image-t0.7-n10 | PV | 2 | image | 10 | 1 | 0.821 | 0.788 | [0.761, 0.811] | 0.817 | 0.761 |
| 12 | session-78-image-checklist-text | PV | 2 | image | 5 | 1 | 0.821 | 0.785 | [0.758, 0.814] | 0.789 | 0.782 |
| 13 | session-78-image-brief-text | PV | 2 | image | 5 | 1 | 0.819 | 0.778 | [0.753, 0.807] | 0.804 | 0.754 |
| 14 | session-78-image-checklist | PV | 2 | image | 5 | 1 | 0.816 | 0.783 | [0.757, 0.812] | 0.782 | 0.784 |
| 15 | pv-scale4-optimal-n10 | PV | 2 | image | 10 | 1 | 0.815 | 0.768 | [0.744, 0.795] | 0.791 | 0.747 |
| 16 | pv-high-image-t0.3-n10 | PV | 2 | image | 10 | 1 | 0.815 | 0.769 | [0.744, 0.796] | 0.802 | 0.738 |
| 17 | pv-min-image-t1.0-n10 | PV | 2 | image | 10 | 1 | 0.810 | 0.741 | [0.713, 0.773] | 0.813 | 0.680 |
| 18 | pv-high-image-t0.3-n5 | PV | 2 | image | 5 | 1 | 0.804 | 0.746 | [0.716, 0.773] | 0.809 | 0.692 |
| 19 | pv-min-image-t1.0-n5 | PV | 2 | image | 5 | 1 | 0.802 | 0.738 | [0.712, 0.770] | 0.810 | 0.678 |
| 20 | pv-high-image-t1.0-n10 | PV | 2 | image | 10 | 1 | 0.800 | 0.763 | [0.736, 0.789] | 0.783 | 0.745 |

## Tier 2 (MCC: 0.755–0.797)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 21 | session-78-image-adversarial-text | PV | 2 | image | 5 | 1 | 0.797 | 0.772 | [0.748, 0.801] | 0.790 | 0.754 |
| 22 | pv-high-image-t0.7-n10 | PV | 2 | image | 10 | 1 | 0.796 | 0.776 | [0.748, 0.805] | 0.869 | 0.701 |
| 23 | session-78-text-comparative | PV | 2 | text | 5 | 1 | 0.793 | 0.885 | [0.863, 0.904] | 0.927 | 0.846 |
| 24 | session-78-text-adversarial | PV | 2 | text | 5 | 1 | 0.793 | 0.883 | [0.862, 0.901] | 0.927 | 0.844 |
| 25 | pv-high-text-t1.0-n10 | PV | 2 | text | 10 | 1 | 0.790 | 0.880 | [0.862, 0.901] | 0.890 | 0.871 |
| 26 | pv-flash-high-text-16of30 | PV | 2 | text | 30 | 1 | 0.789 | 0.890 | [0.874, 0.910] | 0.915 | 0.867 |
| 27 | pv-high-text-t0.3-n10 | PV | 2 | text | 10 | 1 | 0.787 | 0.872 | [0.853, 0.892] | 0.908 | 0.839 |
| 28 | pv-min-text-t0.7-n5 | PV | 2 | text | 5 | 1 | 0.786 | 0.873 | [0.854, 0.891] | 0.930 | 0.823 |
| 29 | pv-min-text-t0.0-n3 | PV | 2 | text | 3 | 1 | 0.783 | 0.862 | [0.842, 0.884] | 0.908 | 0.821 |
| 30 | pv-min-text-t1.0-n10 | PV | 2 | text | 10 | 1 | 0.780 | 0.877 | [0.860, 0.895] | 0.921 | 0.837 |
| 31 | pv-min-text-t1.0-n5 | PV | 2 | text | 5 | 1 | 0.778 | 0.871 | [0.852, 0.890] | 0.904 | 0.841 |
| 32 | pv-min-text-t0.7-n10 | PV | 2 | text | 10 | 1 | 0.776 | 0.873 | [0.853, 0.893] | 0.914 | 0.835 |
| 33 | pv-high-text-t0.3-n5 | PV | 2 | text | 5 | 1 | 0.776 | 0.886 | [0.868, 0.905] | 0.914 | 0.860 |
| 34 | pv-high-text-t0.0-n3 | PV | 2 | text | 3 | 1 | 0.774 | 0.823 | [0.797, 0.850] | 0.856 | 0.793 |
| 35 | session-78-text-checklist | PV | 2 | text | 5 | 1 | 0.774 | 0.878 | [0.856, 0.896] | 0.913 | 0.846 |
| 36 | pv-min-text-t0.3-n10 | PV | 2 | text | 10 | 1 | 0.772 | 0.868 | [0.850, 0.886] | 0.916 | 0.825 |
| 37 | pv-min-text-t0.3-n5 | PV | 2 | text | 5 | 1 | 0.772 | 0.878 | [0.860, 0.897] | 0.907 | 0.851 |
| 38 | pv-high-text-t0.7-n5 | PV | 2 | text | 5 | 1 | 0.767 | 0.863 | [0.842, 0.883] | 0.911 | 0.821 |
| 39 | session-78-text-brief | PV | 2 | text | 5 | 1 | 0.765 | 0.876 | [0.854, 0.894] | 0.909 | 0.846 |
| 40 | pv-high-text-t0.7-n10 | PV | 2 | text | 10 | 1 | 0.763 | 0.874 | [0.857, 0.894] | 0.942 | 0.816 |
| 41 | h11-pvd-pro-high-image-n5 | greedy | 2 | image | 5 | 3 | 0.761 | 0.700 | [0.667, 0.732] | 0.673 | 0.729 |
| 42 | session-78-text-brief-text | PV | 2 | text | 5 | 1 | 0.758 | 0.852 | [0.827, 0.873] | 0.902 | 0.807 |
| 43 | pv-high-text-t1.0-n5 | PV | 2 | text | 5 | 1 | 0.756 | 0.861 | [0.841, 0.881] | 0.928 | 0.802 |
| 44 | session-78-text-checklist-text | PV | 2 | text | 5 | 1 | 0.755 | 0.864 | [0.842, 0.883] | 0.890 | 0.839 |

## Tier 3 (MCC: 0.676–0.752)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 45 | session-78-text-adversarial-text | PV | 2 | text | 5 | 1 | 0.752 | 0.860 | [0.839, 0.880] | 0.912 | 0.814 |
| 46 | h11-pvd-pro-medium-text-baseline | 1-pass | 2 | text | 1 | 1 | 0.752 | 0.763 | [0.732, 0.797] | 0.767 | 0.759 |
| 47 | scale4-optimal-487 | greedy | 2 | image | 10 | 6 | 0.746 | 0.742 | [0.713, 0.771] | 0.772 | 0.715 |
| 48 | h11-pvd-pro-medium-image-baseline | 1-pass | 2 | image | 1 | 1 | 0.734 | 0.606 | [0.575, 0.636] | 0.557 | 0.664 |
| 49 | h11-pvd-pro-high-text-n5 | greedy | 2 | text | 10 | 6 | 0.727 | 0.836 | [0.810, 0.859] | 0.927 | 0.761 |
| 50 | p3a-high-image-t0.3 | greedy | 2 | image | 10 | 9 | 0.682 | 0.731 | [0.698, 0.757] | 0.806 | 0.669 |
| 51 | h11-pvd-flash-high-image-n5 | greedy | 2 | image | 10 | 7 | 0.676 | 0.750 | [0.722, 0.781] | 0.778 | 0.724 |

## Tier 4 (MCC: 0.565–0.644)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 52 | p3a-high-image-t1.0 | greedy | 2 | image | 10 | 6 | 0.644 | 0.735 | [0.707, 0.765] | 0.737 | 0.733 |
| 53 | h11-pvd-flash-high-text-n5 | greedy | 2 | text | 30 | 26 | 0.620 | 0.814 | [0.792, 0.839] | 0.834 | 0.795 |
| 54 | h11-n1-pro-image-medium-t07 | 1-pass | 2 | image | 1 | 1 | 0.597 | 0.452 | [0.418, 0.485] | 0.331 | 0.715 |
| 55 | p3a-high-text-t0.3 | greedy | 2 | text | 10 | 10 | 0.587 | 0.789 | [0.763, 0.811] | 0.814 | 0.765 |
| 56 | p3a-high-text-t0.3-n5 | greedy | 2 | text | 5 | 10 | 0.587 | 0.789 | [0.763, 0.811] | 0.814 | 0.765 |
| 57 | p3a-high-text-t1.0 | greedy | 2 | text | 10 | 9 | 0.575 | 0.773 | [0.744, 0.800] | 0.792 | 0.754 |
| 58 | p3a-high-text-t1.0-n5 | greedy | 2 | text | 5 | 9 | 0.575 | 0.773 | [0.744, 0.800] | 0.792 | 0.754 |
| 59 | h11-n1-pro-image-high-t0 | greedy | 2 | image | 3 | 3 | 0.565 | 0.552 | [0.517, 0.587] | 0.475 | 0.660 |

## Tier 5 (MCC: 0.388–0.503)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 60 | h11-e47-propose-brief | greedy | 2 | text | 5 | 5 | 0.503 | 0.714 | [0.678, 0.745] | 0.694 | 0.736 |
| 61 | p3a-high-image-t0.0 | greedy | 2 | image | 3 | 1 | 0.484 | 0.488 | [0.457, 0.520] | 0.377 | 0.694 |
| 62 | p3a-high-text-t0.0 | greedy | 2 | text | 3 | 3 | 0.451 | 0.605 | [0.565, 0.642] | 0.479 | 0.821 |
| 63 | p3a-min-image-t1.0 | greedy | 2 | image | 10 | 8 | 0.441 | 0.646 | [0.613, 0.676] | 0.625 | 0.669 |
| 64 | pv-cascade-adversarial-checklist | 1-pass+PV | 2 | text | 1 | 1 | 0.432 | 0.504 | [0.446, 0.549] | 0.667 | 0.405 |
| 65 | pv-adversarial-text | 1-pass+PV | 2 | text | 1 | 1 | 0.432 | 0.471 | [0.408, 0.517] | 0.712 | 0.352 |
| 66 | pv-adversarial-image | 1-pass+PV | 2 | image | 1 | 1 | 0.416 | 0.494 | [0.434, 0.539] | 0.659 | 0.395 |
| 67 | p3a-minimal-text-t1.0 | greedy | 2 | text | 10 | 9 | 0.415 | 0.667 | [0.631, 0.705] | 0.597 | 0.754 |
| 68 | p3a-minimal-text-t1.0-n5 | greedy | 2 | text | 5 | 9 | 0.415 | 0.667 | [0.631, 0.705] | 0.597 | 0.754 |
| 69 | pv-cascade-checklist-adversarial | 1-pass+PV | 2 | text | 1 | 1 | 0.413 | 0.495 | [0.435, 0.540] | 0.661 | 0.395 |
| 70 | h11-pvd-image-n5 | greedy | 2 | image | 10 | 8 | 0.404 | 0.680 | [0.650, 0.711] | 0.640 | 0.726 |
| 71 | pv-brief-text | 1-pass+PV | 2 | text | 1 | 1 | 0.397 | 0.514 | [0.456, 0.560] | 0.673 | 0.416 |
| 72 | h11-n1-pro-text-high-t0 | greedy | 2 | text | 3 | 3 | 0.395 | 0.567 | [0.530, 0.603] | 0.441 | 0.793 |
| 73 | pv-checklist-image | 1-pass+PV | 2 | image | 1 | 1 | 0.388 | 0.531 | [0.473, 0.580] | 0.620 | 0.464 |

## Tier 6 (MCC: 0.310–0.380)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 74 | h11-pvd-flash-minimal-text-n30-t07 | greedy | 2 | text | 30 | 29 | 0.380 | 0.661 | [0.627, 0.694] | 0.602 | 0.733 |
| 75 | h11-n1-image-t03 | greedy | 2 | image | 3 | 3 | 0.349 | 0.677 | [0.648, 0.707] | 0.598 | 0.779 |
| 76 | pv-brief-image | 1-pass+PV | 2 | image | 1 | 1 | 0.341 | 0.520 | [0.463, 0.569] | 0.607 | 0.455 |
| 77 | p3a-min-image-t0.3 | greedy | 2 | image | 10 | 10 | 0.340 | 0.660 | [0.629, 0.690] | 0.607 | 0.722 |
| 78 | h11-pvd-text-n10 | greedy | 2 | text | 10 | 10 | 0.316 | 0.619 | [0.582, 0.659] | 0.528 | 0.747 |
| 79 | pv-checklist-text | 1-pass+PV | 2 | text | 1 | 1 | 0.315 | 0.521 | [0.463, 0.569] | 0.598 | 0.462 |
| 80 | h11-pvd-image-baseline | 1-pass | 2 | image | 1 | 1 | 0.311 | 0.600 | [0.575, 0.629] | 0.474 | 0.814 |
| 81 | p3a-minimal-text-t0.3 | greedy | 2 | text | 10 | 10 | 0.311 | 0.642 | [0.606, 0.679] | 0.551 | 0.770 |
| 82 | p3a-minimal-text-t0.3-n5 | greedy | 2 | text | 5 | 10 | 0.311 | 0.642 | [0.606, 0.679] | 0.551 | 0.770 |
| 83 | h11-n1-pro-text-medium-t07 | 1-pass | 2 | text | 1 | 1 | 0.310 | 0.416 | [0.385, 0.459] | 0.271 | 0.899 |

## Tier 7 (MCC: 0.170–0.223)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 84 | p3a-minimal-text-t0.0 | greedy | 2 | text | 3 | 3 | 0.223 | 0.593 | [0.547, 0.631] | 0.458 | 0.841 |
| 85 | h11-n1-image-t0 | greedy | 2 | image | 3 | 2 | 0.214 | 0.629 | [0.600, 0.657] | 0.515 | 0.807 |
| 86 | h11-n1-brief-text-t03 | greedy | 2 | text | 3 | 3 | 0.170 | 0.591 | [0.550, 0.634] | 0.457 | 0.835 |

## Tier 8 (MCC: -0.001–-0.001)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 87 | h11-pvd-text-baseline | 1-pass | 2 | text | 1 | 1 | -0.001 | 0.520 | [0.475, 0.555] | 0.368 | 0.885 |
