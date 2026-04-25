# Leaderboard (MCC tiers) — 30m buffer

**Generated**: 2026-04-25T14:37:39.720005+00:00
**Tiering metric**: MCC
**FDR q**: 0.01
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 44 in 2 tier(s)

## Tier 1 (MCC: 0.755–0.841)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | pv-min-image-t0.3-n5 | PV | 2 | image | 5 | 1 | 0.841 | 0.843 | [0.810, 0.872] | 0.872 | 0.816 |
| 2 | pv-n1-image-t0-n3 | PV | 2 | image | 3 | 1 | 0.839 | 0.842 | [0.810, 0.872] | 0.832 | 0.853 |
| 3 | pv-min-image-t0.7-n5 | PV | 2 | image | 5 | 1 | 0.838 | 0.846 | [0.815, 0.876] | 0.860 | 0.832 |
| 4 | pv-min-image-t0.3-n10 | PV | 2 | image | 10 | 1 | 0.837 | 0.853 | [0.822, 0.881] | 0.886 | 0.823 |
| 5 | pv-high-image-t0.7-n5 | PV | 2 | image | 5 | 1 | 0.836 | 0.858 | [0.824, 0.887] | 0.879 | 0.837 |
| 6 | pv-scale4-optimal-n5 | PV | 2 | image | 5 | 1 | 0.835 | 0.821 | [0.783, 0.854] | 0.861 | 0.784 |
| 7 | session-78-image-adversarial | PV | 2 | image | 5 | 1 | 0.831 | 0.865 | [0.830, 0.895] | 0.868 | 0.862 |
| 8 | session-78-image-comparative | PV | 2 | image | 5 | 1 | 0.830 | 0.864 | [0.827, 0.894] | 0.866 | 0.862 |
| 9 | session-78-image-brief | PV | 2 | image | 5 | 1 | 0.829 | 0.862 | [0.826, 0.892] | 0.860 | 0.864 |
| 10 | pv-high-image-t1.0-n5 | PV | 2 | image | 5 | 1 | 0.822 | 0.812 | [0.775, 0.843] | 0.837 | 0.788 |
| 11 | pv-min-image-t0.7-n10 | PV | 2 | image | 10 | 1 | 0.821 | 0.852 | [0.823, 0.880] | 0.884 | 0.823 |
| 12 | session-78-image-brief-text | PV | 2 | image | 5 | 1 | 0.819 | 0.840 | [0.799, 0.870] | 0.875 | 0.807 |
| 13 | session-78-image-checklist-text | PV | 2 | image | 5 | 1 | 0.817 | 0.857 | [0.820, 0.887] | 0.866 | 0.848 |
| 14 | session-78-image-checklist | PV | 2 | image | 5 | 1 | 0.816 | 0.861 | [0.825, 0.890] | 0.860 | 0.862 |
| 15 | pv-scale4-optimal-n10 | PV | 2 | image | 10 | 1 | 0.815 | 0.832 | [0.798, 0.861] | 0.856 | 0.809 |
| 16 | pv-high-image-t0.3-n10 | PV | 2 | image | 10 | 1 | 0.815 | 0.836 | [0.805, 0.864] | 0.873 | 0.802 |
| 17 | pv-min-image-t1.0-n10 | PV | 2 | image | 10 | 1 | 0.810 | 0.819 | [0.786, 0.849] | 0.898 | 0.752 |
| 18 | pv-high-image-t0.3-n5 | PV | 2 | image | 5 | 1 | 0.804 | 0.825 | [0.791, 0.857] | 0.895 | 0.765 |
| 19 | pv-min-image-t1.0-n5 | PV | 2 | image | 5 | 1 | 0.802 | 0.806 | [0.769, 0.841] | 0.885 | 0.740 |
| 20 | pv-high-image-t1.0-n10 | PV | 2 | image | 10 | 1 | 0.800 | 0.834 | [0.803, 0.862] | 0.855 | 0.814 |
| 21 | pv-high-image-t0.7-n10 | PV | 2 | image | 10 | 1 | 0.796 | 0.832 | [0.798, 0.866] | 0.932 | 0.752 |
| 22 | session-78-text-comparative | PV | 2 | text | 5 | 1 | 0.793 | 0.911 | [0.886, 0.934] | 0.955 | 0.871 |
| 23 | session-78-image-adversarial-text | PV | 2 | image | 5 | 1 | 0.793 | 0.846 | [0.813, 0.876] | 0.873 | 0.821 |
| 24 | session-78-text-adversarial | PV | 2 | text | 5 | 1 | 0.793 | 0.910 | [0.884, 0.932] | 0.955 | 0.869 |
| 25 | pv-high-text-t1.0-n10 | PV | 2 | text | 10 | 1 | 0.790 | 0.904 | [0.879, 0.926] | 0.913 | 0.894 |
| 26 | pv-flash-high-text-16of30 | PV | 2 | text | 30 | 1 | 0.789 | 0.904 | [0.878, 0.928] | 0.930 | 0.880 |
| 27 | pv-high-text-t0.3-n10 | PV | 2 | text | 10 | 1 | 0.787 | 0.901 | [0.873, 0.925] | 0.938 | 0.867 |
| 28 | pv-min-text-t0.7-n5 | PV | 2 | text | 5 | 1 | 0.786 | 0.885 | [0.859, 0.911] | 0.943 | 0.835 |
| 29 | pv-min-text-t0.0-n3 | PV | 2 | text | 3 | 1 | 0.783 | 0.870 | [0.839, 0.898] | 0.916 | 0.828 |
| 30 | pv-min-text-t1.0-n10 | PV | 2 | text | 10 | 1 | 0.780 | 0.892 | [0.865, 0.916] | 0.937 | 0.851 |
| 31 | pv-min-text-t1.0-n5 | PV | 2 | text | 5 | 1 | 0.778 | 0.888 | [0.861, 0.911] | 0.921 | 0.858 |
| 32 | pv-min-text-t0.7-n10 | PV | 2 | text | 10 | 1 | 0.776 | 0.887 | [0.858, 0.913] | 0.929 | 0.848 |
| 33 | pv-high-text-t0.3-n5 | PV | 2 | text | 5 | 1 | 0.776 | 0.903 | [0.875, 0.925] | 0.931 | 0.876 |
| 34 | pv-high-text-t0.0-n3 | PV | 2 | text | 3 | 1 | 0.774 | 0.854 | [0.811, 0.888] | 0.888 | 0.823 |
| 35 | session-78-text-checklist | PV | 2 | text | 5 | 1 | 0.774 | 0.904 | [0.878, 0.927] | 0.940 | 0.871 |
| 36 | pv-min-text-t0.3-n10 | PV | 2 | text | 10 | 1 | 0.772 | 0.873 | [0.842, 0.901] | 0.921 | 0.830 |
| 37 | pv-min-text-t0.3-n5 | PV | 2 | text | 5 | 1 | 0.772 | 0.890 | [0.862, 0.914] | 0.919 | 0.862 |
| 38 | pv-high-text-t0.7-n5 | PV | 2 | text | 5 | 1 | 0.767 | 0.887 | [0.859, 0.914] | 0.936 | 0.844 |
| 39 | session-78-text-brief | PV | 2 | text | 5 | 1 | 0.765 | 0.902 | [0.876, 0.925] | 0.936 | 0.871 |
| 40 | pv-high-text-t0.7-n10 | PV | 2 | text | 10 | 1 | 0.763 | 0.889 | [0.862, 0.912] | 0.958 | 0.830 |
| 41 | session-78-text-brief-text | PV | 2 | text | 5 | 1 | 0.758 | 0.870 | [0.839, 0.897] | 0.932 | 0.816 |
| 42 | pv-high-text-t1.0-n5 | PV | 2 | text | 5 | 1 | 0.756 | 0.880 | [0.851, 0.906] | 0.950 | 0.821 |
| 43 | session-78-text-checklist-text | PV | 2 | text | 5 | 1 | 0.755 | 0.886 | [0.858, 0.912] | 0.916 | 0.858 |

## Tier 2 (MCC: 0.752–0.752)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 44 | session-78-text-adversarial-text | PV | 2 | text | 5 | 1 | 0.752 | 0.884 | [0.856, 0.910] | 0.940 | 0.835 |
