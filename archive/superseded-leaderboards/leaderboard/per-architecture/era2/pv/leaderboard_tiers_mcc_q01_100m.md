# Leaderboard (MCC tiers) — 100m buffer

**Generated**: 2026-04-26T07:18:22.578073+00:00
**Tiering metric**: MCC
**FDR q**: 0.01
**Note**: MCC is buffer-invariant in this codebase (tile-level binary classification). Threshold selection still maximises F1 at the primary buffer for cross-metric alignment; the per-buffer F1 column reflects that.
**Conditions**: 44 in 2 tier(s)

## Tier 1 (MCC: 0.755–0.841)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 1 | pv-min-image-t0.3-n5 | PV | 2 | image | 5 | 1 | 0.841 | 0.869 | [0.840, 0.897] | 0.899 | 0.841 |
| 2 | pv-n1-image-t0-n3 | PV | 2 | image | 3 | 1 | 0.839 | 0.881 | [0.857, 0.904] | 0.870 | 0.892 |
| 3 | pv-min-image-t0.7-n5 | PV | 2 | image | 5 | 1 | 0.838 | 0.888 | [0.864, 0.911] | 0.903 | 0.874 |
| 4 | pv-min-image-t0.3-n10 | PV | 2 | image | 10 | 1 | 0.837 | 0.870 | [0.840, 0.896] | 0.903 | 0.839 |
| 5 | pv-high-image-t0.7-n5 | PV | 2 | image | 5 | 1 | 0.836 | 0.886 | [0.857, 0.910] | 0.908 | 0.864 |
| 6 | pv-scale4-optimal-n5 | PV | 2 | image | 5 | 1 | 0.835 | 0.859 | [0.828, 0.888] | 0.901 | 0.821 |
| 7 | session-78-image-adversarial | PV | 2 | image | 5 | 1 | 0.831 | 0.897 | [0.869, 0.922] | 0.900 | 0.894 |
| 8 | session-78-image-comparative | PV | 2 | image | 5 | 1 | 0.830 | 0.896 | [0.866, 0.921] | 0.898 | 0.894 |
| 9 | session-78-image-brief | PV | 2 | image | 5 | 1 | 0.829 | 0.894 | [0.866, 0.919] | 0.892 | 0.897 |
| 10 | pv-high-image-t1.0-n5 | PV | 2 | image | 5 | 1 | 0.822 | 0.876 | [0.847, 0.901] | 0.902 | 0.851 |
| 11 | pv-min-image-t0.7-n10 | PV | 2 | image | 10 | 1 | 0.821 | 0.883 | [0.858, 0.906] | 0.916 | 0.853 |
| 12 | session-78-image-brief-text | PV | 2 | image | 5 | 1 | 0.819 | 0.864 | [0.829, 0.892] | 0.900 | 0.830 |
| 13 | session-78-image-checklist-text | PV | 2 | image | 5 | 1 | 0.817 | 0.887 | [0.858, 0.912] | 0.897 | 0.878 |
| 14 | session-78-image-checklist | PV | 2 | image | 5 | 1 | 0.816 | 0.893 | [0.863, 0.916] | 0.892 | 0.894 |
| 15 | pv-scale4-optimal-n10 | PV | 2 | image | 10 | 1 | 0.815 | 0.865 | [0.835, 0.890] | 0.890 | 0.841 |
| 16 | pv-high-image-t0.3-n10 | PV | 2 | image | 10 | 1 | 0.815 | 0.886 | [0.859, 0.910] | 0.925 | 0.851 |
| 17 | pv-min-image-t1.0-n10 | PV | 2 | image | 10 | 1 | 0.810 | 0.846 | [0.817, 0.874] | 0.929 | 0.777 |
| 18 | pv-high-image-t0.3-n5 | PV | 2 | image | 5 | 1 | 0.804 | 0.858 | [0.825, 0.889] | 0.930 | 0.795 |
| 19 | pv-min-image-t1.0-n5 | PV | 2 | image | 5 | 1 | 0.802 | 0.849 | [0.818, 0.876] | 0.931 | 0.779 |
| 20 | pv-high-image-t1.0-n10 | PV | 2 | image | 10 | 1 | 0.800 | 0.876 | [0.850, 0.900] | 0.899 | 0.855 |
| 21 | pv-high-image-t0.7-n10 | PV | 2 | image | 10 | 1 | 0.796 | 0.850 | [0.820, 0.880] | 0.952 | 0.768 |
| 22 | session-78-text-comparative | PV | 2 | text | 5 | 1 | 0.793 | 0.916 | [0.891, 0.938] | 0.960 | 0.876 |
| 23 | session-78-image-adversarial-text | PV | 2 | image | 5 | 1 | 0.793 | 0.870 | [0.839, 0.896] | 0.897 | 0.844 |
| 24 | session-78-text-adversarial | PV | 2 | text | 5 | 1 | 0.793 | 0.915 | [0.889, 0.936] | 0.960 | 0.874 |
| 25 | pv-high-text-t1.0-n10 | PV | 2 | text | 10 | 1 | 0.790 | 0.908 | [0.884, 0.930] | 0.918 | 0.899 |
| 26 | pv-flash-high-text-16of30 | PV | 2 | text | 30 | 1 | 0.789 | 0.909 | [0.884, 0.931] | 0.934 | 0.885 |
| 27 | pv-high-text-t0.3-n10 | PV | 2 | text | 10 | 1 | 0.787 | 0.908 | [0.883, 0.929] | 0.945 | 0.874 |
| 28 | pv-min-text-t0.7-n5 | PV | 2 | text | 5 | 1 | 0.786 | 0.893 | [0.870, 0.914] | 0.951 | 0.841 |
| 29 | pv-min-text-t0.0-n3 | PV | 2 | text | 3 | 1 | 0.783 | 0.896 | [0.871, 0.919] | 0.944 | 0.853 |
| 30 | pv-min-text-t1.0-n10 | PV | 2 | text | 10 | 1 | 0.780 | 0.899 | [0.874, 0.922] | 0.944 | 0.858 |
| 31 | pv-min-text-t1.0-n5 | PV | 2 | text | 5 | 1 | 0.778 | 0.902 | [0.879, 0.924] | 0.936 | 0.871 |
| 32 | pv-min-text-t0.7-n10 | PV | 2 | text | 10 | 1 | 0.776 | 0.894 | [0.869, 0.918] | 0.937 | 0.855 |
| 33 | pv-high-text-t0.3-n5 | PV | 2 | text | 5 | 1 | 0.776 | 0.912 | [0.887, 0.934] | 0.941 | 0.885 |
| 34 | pv-high-text-t0.0-n3 | PV | 2 | text | 3 | 1 | 0.774 | 0.864 | [0.821, 0.896] | 0.898 | 0.832 |
| 35 | session-78-text-checklist | PV | 2 | text | 5 | 1 | 0.774 | 0.909 | [0.884, 0.932] | 0.945 | 0.876 |
| 36 | pv-min-text-t0.3-n10 | PV | 2 | text | 10 | 1 | 0.772 | 0.895 | [0.869, 0.918] | 0.944 | 0.851 |
| 37 | pv-min-text-t0.3-n5 | PV | 2 | text | 5 | 1 | 0.772 | 0.906 | [0.882, 0.928] | 0.936 | 0.878 |
| 38 | pv-high-text-t0.7-n5 | PV | 2 | text | 5 | 1 | 0.767 | 0.892 | [0.865, 0.918] | 0.941 | 0.848 |
| 39 | session-78-text-brief | PV | 2 | text | 5 | 1 | 0.765 | 0.907 | [0.882, 0.929] | 0.941 | 0.876 |
| 40 | pv-high-text-t0.7-n10 | PV | 2 | text | 10 | 1 | 0.763 | 0.892 | [0.865, 0.914] | 0.960 | 0.832 |
| 41 | session-78-text-brief-text | PV | 2 | text | 5 | 1 | 0.758 | 0.875 | [0.844, 0.901] | 0.937 | 0.821 |
| 42 | pv-high-text-t1.0-n5 | PV | 2 | text | 5 | 1 | 0.756 | 0.880 | [0.851, 0.906] | 0.950 | 0.821 |
| 43 | session-78-text-checklist-text | PV | 2 | text | 5 | 1 | 0.755 | 0.891 | [0.863, 0.917] | 0.921 | 0.862 |

## Tier 2 (MCC: 0.752–0.752)

| # | Condition | Arch | Era | Track | K | t | MCC | F1@buf | F1 95% CI | P | R |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|---:|:------:|---:|---:|
| 44 | session-78-text-adversarial-text | PV | 2 | text | 5 | 1 | 0.752 | 0.889 | [0.861, 0.915] | 0.946 | 0.839 |
