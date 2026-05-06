# Leaderboard (MCC tiers) — 20m buffer

**Generated**: 2026-05-06T03:01:20.022623+00:00
**Tiering metric**: MCC
**FDR q**: 0.05
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 44 in 2 tier(s)

## Tier 1 (MCC: 0.755–0.841)

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
| 41 | session-78-text-brief-text | PV | 2 | text | 5 | 1 | 0.758 | 0.852 | [0.827, 0.873] | 0.902 | 0.807 |
| 42 | pv-high-text-t1.0-n5 | PV | 2 | text | 5 | 1 | 0.756 | 0.861 | [0.841, 0.881] | 0.928 | 0.802 |
| 43 | session-78-text-checklist-text | PV | 2 | text | 5 | 1 | 0.755 | 0.864 | [0.842, 0.883] | 0.890 | 0.839 |

## Tier 2 (MCC: 0.752–0.752)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 44 | session-78-text-adversarial-text | PV | 2 | text | 5 | 1 | 0.752 | 0.860 | [0.839, 0.880] | 0.912 | 0.814 |
