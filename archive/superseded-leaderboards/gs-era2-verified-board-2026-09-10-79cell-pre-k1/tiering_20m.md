# Era-1 leaderboard — statistical tiering (20 m) — `gs-era2-verified-board-2026-09-10`

- **Cells**: 79 (0 single-pass + 0 consensus + 79 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 3081 (1845 significant) -> **7 tiers**
- **Tie set (Tier 1)**: `gemini37-image-gs-2026-09-01::g37-image-k5-verified-swap37-p0.90-k5-era2b`, `gemini37-screen-2026-08-28::g37-text-k5-verified-swap37-p0.80-k5-era2b`, `gemini37-screen-2026-08-28::g37-text-k5-verified-swap38-p0.88-k5-era2b`, `gemini37-image-gs-2026-09-01::g37-image-k5-verified-carried-p0.10-k5-era2b`, `gemini37-screen-2026-08-28::g37-text-k10-verified-carried-p0.10-k10-era2b`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `g37-image-k5-verified-swap37-p0.90-k5-era2b` | verified-PV | 1 | 0.923 | 0.923 | -0.000 | 0.826 | 1 |
| 2 | `g37-text-k5-verified-swap37-p0.80-k5-era2b` | verified-PV | 1 | 0.919 | 0.919 | -0.000 | 0.794 | 1 |
| 3 | `g37-text-k5-verified-swap38-p0.88-k5-era2b` | verified-PV | 1 | 0.918 | 0.918 | +0.000 | 0.808 | 1 |
| 4 | `g37-image-k5-verified-carried-p0.10-k5-era2b` | verified-PV | 1 | 0.918 | 0.918 | +0.000 | 0.813 | 1 |
| 5 | `g37-text-k10-verified-carried-p0.10-k10-era2b` | verified-PV | 1 | 0.907 | 0.907 | -0.000 | 0.767 | 1 |
| 6 | `g37-text-k5-verified-carried-p0.10-k5-era2b` | verified-PV | 1 | 0.907 | 0.907 | +0.000 | 0.765 | 2 |
| 7 | `g384-ov192-k10-verified37-p0.98-k10-era2b` | verified-PV | 1 | 0.906 | 0.906 | +0.000 | 0.810 | 2 |
| 8 | `verified-384-16of30-t0-3-n5-opmax-era2b` | verified-PV | 1 | 0.895 | 0.895 | +0.000 | 0.794 | 2 |
| 9 | `verified-adv-text-consensus-16of30-era2b` | verified-PV | 1 | 0.890 | 0.890 | +0.000 | 0.790 | 2 |
| 10 | `g384-ov192-k10-verified-p0.15-k10-era2b` | verified-PV | 1 | 0.889 | 0.889 | +0.000 | 0.790 | 2 |
| 11 | `pv-high-text-t0.3-n5-opmax` | verified-PV | 1 | 0.887 | 0.887 | +0.000 | 0.780 | 2 |
| 12 | `session-78-text-comparative-opmax` | verified-PV | 1 | 0.885 | 0.885 | +0.000 | 0.795 | 2 |
| 13 | `verified-adv-text-min-6of10-era2b` | verified-PV | 1 | 0.883 | 0.883 | -0.000 | 0.807 | 2 |
| 14 | `session-78-text-adversarial-opmax` | verified-PV | 1 | 0.883 | 0.883 | -0.000 | 0.795 | 2 |
| 15 | `pv-high-text-t1.0-n10-opmax` | verified-PV | 1 | 0.880 | 0.880 | -0.000 | 0.791 | 2 |
| 16 | `verified-adv-text-pro-vf-4of5-era2b` | verified-PV | 1 | 0.879 | 0.879 | +0.000 | 0.795 | 2 |
| 17 | `verified-adv-text-min-true-3of5-era2b` | verified-PV | 1 | 0.878 | 0.878 | -0.000 | 0.790 | 2 |
| 18 | `verified-adv-text-t03-4of5-era2b` | verified-PV | 1 | 0.878 | 0.878 | -0.000 | 0.783 | 2 |
| 19 | `session-78-text-checklist-opmax` | verified-PV | 1 | 0.878 | 0.878 | -0.000 | 0.776 | 2 |
| 20 | `pv-min-text-t1.0-n10-opmax` | verified-PV | 1 | 0.878 | 0.878 | +0.000 | 0.788 | 2 |
| 21 | `pv-min-text-t0.3-n5-opmax` | verified-PV | 1 | 0.878 | 0.878 | +0.000 | 0.773 | 2 |
| 22 | `verified-adv-text-6of10-era2b` | verified-PV | 1 | 0.877 | 0.877 | +0.000 | 0.790 | 3 |
| 23 | `verified-384-ge3of5-t0-3-high-n5-era2b` | verified-PV | 1 | 0.876 | 0.876 | -0.000 | 0.789 | 3 |
| 24 | `session-78-text-brief-opmax` | verified-PV | 1 | 0.876 | 0.876 | -0.000 | 0.766 | 3 |
| 25 | `pv-high-text-t0.7-n10-opmax` | verified-PV | 1 | 0.874 | 0.874 | -0.000 | 0.764 | 3 |
| 26 | `verified-384-ge3of5-t0-3-n5-era2b` | verified-PV | 1 | 0.874 | 0.874 | +0.000 | 0.771 | 3 |
| 27 | `verified-384-ge3of5-t0-7-high-n5-era2b` | verified-PV | 1 | 0.874 | 0.874 | +0.000 | 0.793 | 3 |
| 28 | `pv-min-text-t0.7-n5-opmax` | verified-PV | 1 | 0.874 | 0.874 | +0.000 | 0.796 | 3 |
| 29 | `pv-min-text-t0.3-n10-opmax` | verified-PV | 1 | 0.873 | 0.873 | -0.000 | 0.791 | 3 |
| 30 | `pv-min-text-t0.7-n10-opmax` | verified-PV | 1 | 0.873 | 0.873 | -0.000 | 0.777 | 3 |
| 31 | `verified-384-union-t0-0-n5-era2b` | verified-PV | 1 | 0.872 | 0.872 | -0.000 | 0.762 | 3 |
| 32 | `pv-high-text-t0.3-n10-opmax` | verified-PV | 1 | 0.872 | 0.872 | -0.000 | 0.787 | 3 |
| 33 | `pv-min-text-t1.0-n5-opmax` | verified-PV | 1 | 0.871 | 0.871 | +0.000 | 0.780 | 3 |
| 34 | `verified-384-ge3of5-t0-7-n5-era2b` | verified-PV | 1 | 0.871 | 0.871 | +0.000 | 0.771 | 3 |
| 35 | `verified-adv-text-min-n30lineage-4of5-era2b` | verified-PV | 1 | 0.871 | 0.871 | +0.000 | 0.787 | 3 |
| 36 | `f3prop-f35vf-6of10-era2b` | verified-PV | 1 | 0.869 | 0.869 | +0.000 | 0.767 | 3 |
| 37 | `pv-high-text-t1.0-n5-opmax` | verified-PV | 1 | 0.869 | 0.869 | -0.000 | 0.786 | 3 |
| 38 | `verified-adv-text-4of5-era2b` | verified-PV | 1 | 0.864 | 0.864 | -0.000 | 0.769 | 4 |
| 39 | `session-78-text-checklist-text-opmax` | verified-PV | 1 | 0.864 | 0.864 | +0.000 | 0.756 | 4 |
| 40 | `pv-high-text-t0.7-n5-opmax` | verified-PV | 1 | 0.863 | 0.863 | -0.000 | 0.768 | 4 |
| 41 | `session-78-text-adversarial-text-opmax` | verified-PV | 1 | 0.860 | 0.860 | -0.000 | 0.753 | 4 |
| 42 | `verified-t0-5-era2b` | verified-PV | 1 | 0.856 | 0.856 | -0.000 | 0.771 | 4 |
| 43 | `verified-adv-text-medium-vf-4of5-era2b` | verified-PV | 1 | 0.855 | 0.854 | -0.000 | 0.721 | 4 |
| 44 | `verified-adv-text-high-vf-4of5-era2b` | verified-PV | 1 | 0.852 | 0.852 | -0.000 | 0.699 | 4 |
| 45 | `session-78-text-brief-text-opmax` | verified-PV | 1 | 0.852 | 0.852 | +0.000 | 0.758 | 4 |
| 46 | `verified-t0-0-era2b` | verified-PV | 1 | 0.851 | 0.851 | +0.000 | 0.778 | 4 |
| 47 | `verified-adv-pro-text-pro-vf-3of5-era2b` | verified-PV | 1 | 0.851 | 0.851 | -0.000 | 0.730 | 4 |
| 48 | `verified-adv-pro-text-medium-vf-3of5-era2b` | verified-PV | 1 | 0.850 | 0.849 | -0.000 | 0.730 | 4 |
| 49 | `verified-adv-pro-text-flash-vf-3of5-era2b` | verified-PV | 1 | 0.849 | 0.849 | +0.000 | 0.730 | 4 |
| 50 | `f35prop-f3vf-4of10-era2b` | verified-PV | 1 | 0.848 | 0.848 | -0.000 | 0.767 | 4 |
| 51 | `verified-t1-0-era2b` | verified-PV | 1 | 0.842 | 0.842 | +0.000 | 0.756 | 4 |
| 52 | `f35prop-f35vf-4of10-era2b` | verified-PV | 1 | 0.836 | 0.836 | +0.000 | 0.737 | 4 |
| 53 | `g384-ov192-image-min-k10-verified-p0.15-k9-era2b` | verified-PV | 1 | 0.834 | 0.834 | +0.000 | 0.793 | 4 |
| 54 | `g384-ov192-image-high-k10-verified-p0.20-k8-era2b` | verified-PV | 1 | 0.826 | 0.826 | +0.000 | 0.794 | 5 |
| 55 | `verified-adv-image-min-6of10-era2b` | verified-PV | 1 | 0.789 | 0.789 | -0.000 | 0.803 | 5 |
| 56 | `pv-min-image-t0.7-n10-opmax` | verified-PV | 1 | 0.788 | 0.788 | -0.000 | 0.822 | 5 |
| 57 | `pv-high-image-t0.7-n5-opmax` | verified-PV | 1 | 0.787 | 0.787 | +0.000 | 0.836 | 5 |
| 58 | `session-78-image-adversarial-opmax` | verified-PV | 1 | 0.787 | 0.787 | +0.000 | 0.831 | 5 |
| 59 | `session-78-image-comparative-opmax` | verified-PV | 1 | 0.786 | 0.786 | +0.000 | 0.831 | 5 |
| 60 | `session-78-image-checklist-text-opmax` | verified-PV | 1 | 0.785 | 0.785 | +0.000 | 0.822 | 5 |
| 61 | `session-78-image-brief-opmax` | verified-PV | 1 | 0.784 | 0.784 | +0.000 | 0.830 | 5 |
| 62 | `session-78-image-checklist-opmax` | verified-PV | 1 | 0.783 | 0.783 | +0.000 | 0.817 | 5 |
| 63 | `pv-min-image-t0.3-n10-opmax` | verified-PV | 1 | 0.782 | 0.782 | -0.000 | 0.838 | 5 |
| 64 | `session-78-image-brief-text-opmax` | verified-PV | 1 | 0.778 | 0.778 | -0.000 | 0.820 | 6 |
| 65 | `verified-adv-image-3of5-era2b` | verified-PV | 1 | 0.778 | 0.778 | -0.000 | 0.827 | 6 |
| 66 | `pv-min-image-t0.3-n5-opmax` | verified-PV | 1 | 0.777 | 0.777 | +0.000 | 0.842 | 6 |
| 67 | `pv-high-image-t0.7-n10-opmax` | verified-PV | 1 | 0.776 | 0.777 | +0.000 | 0.798 | 6 |
| 68 | `pv-min-image-t0.7-n5-opmax` | verified-PV | 1 | 0.773 | 0.773 | -0.000 | 0.838 | 6 |
| 69 | `session-78-image-adversarial-text-opmax` | verified-PV | 1 | 0.772 | 0.772 | -0.000 | 0.797 | 6 |
| 70 | `pv-high-image-t0.3-n10-opmax` | verified-PV | 1 | 0.770 | 0.770 | -0.000 | 0.829 | 6 |
| 71 | `pv-scale4-optimal-n10-opmax` | verified-PV | 1 | 0.768 | 0.768 | +0.000 | 0.815 | 6 |
| 72 | `verified-adv-image-min-3of5-era2b` | verified-PV | 1 | 0.767 | 0.767 | -0.000 | 0.846 | 6 |
| 73 | `pv-scale4-optimal-n5-opmax` | verified-PV | 1 | 0.763 | 0.764 | +0.000 | 0.831 | 6 |
| 74 | `pv-high-image-t1.0-n10-opmax` | verified-PV | 1 | 0.763 | 0.763 | -0.000 | 0.800 | 6 |
| 75 | `pv-high-image-t0.3-n5-opmax` | verified-PV | 1 | 0.748 | 0.748 | +0.000 | 0.805 | 6 |
| 76 | `pv-min-image-t1.0-n10-opmax` | verified-PV | 1 | 0.743 | 0.743 | -0.000 | 0.808 | 6 |
| 77 | `pv-min-image-t1.0-n5-opmax` | verified-PV | 1 | 0.738 | 0.738 | +0.000 | 0.802 | 6 |
| 78 | `pv-high-image-t1.0-n5-opmax` | verified-PV | 1 | 0.734 | 0.734 | +0.000 | 0.823 | 7 |
| 79 | `verified-adv-pro-image-pro-vf-3of5-era2b` | verified-PV | 1 | 0.711 | 0.711 | -0.000 | 0.850 | 7 |
