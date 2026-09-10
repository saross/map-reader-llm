# Era-1 leaderboard — statistical tiering (20 m) — `gs-era2-verified-board-2026-09-10`

- **Cells**: 39 (0 single-pass + 0 consensus + 39 verified-PV), 487 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 741 (375 significant) -> **6 tiers**
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
| 11 | `verified-adv-text-min-6of10-era2b` | verified-PV | 1 | 0.883 | 0.883 | -0.000 | 0.807 | 2 |
| 12 | `verified-adv-text-pro-vf-4of5-era2b` | verified-PV | 1 | 0.879 | 0.879 | +0.000 | 0.795 | 2 |
| 13 | `verified-adv-text-min-true-3of5-era2b` | verified-PV | 1 | 0.878 | 0.878 | -0.000 | 0.790 | 2 |
| 14 | `verified-adv-text-t03-4of5-era2b` | verified-PV | 1 | 0.878 | 0.878 | -0.000 | 0.783 | 2 |
| 15 | `verified-adv-text-6of10-era2b` | verified-PV | 1 | 0.877 | 0.877 | +0.000 | 0.790 | 2 |
| 16 | `verified-384-ge3of5-t0-3-high-n5-era2b` | verified-PV | 1 | 0.876 | 0.876 | -0.000 | 0.789 | 2 |
| 17 | `verified-384-ge3of5-t0-3-n5-era2b` | verified-PV | 1 | 0.874 | 0.874 | +0.000 | 0.771 | 2 |
| 18 | `verified-384-ge3of5-t0-7-high-n5-era2b` | verified-PV | 1 | 0.874 | 0.874 | +0.000 | 0.793 | 2 |
| 19 | `verified-384-union-t0-0-n5-era2b` | verified-PV | 1 | 0.872 | 0.872 | -0.000 | 0.762 | 3 |
| 20 | `verified-384-ge3of5-t0-7-n5-era2b` | verified-PV | 1 | 0.871 | 0.871 | +0.000 | 0.771 | 3 |
| 21 | `verified-adv-text-min-n30lineage-4of5-era2b` | verified-PV | 1 | 0.871 | 0.871 | +0.000 | 0.787 | 3 |
| 22 | `f3prop-f35vf-6of10-era2b` | verified-PV | 1 | 0.869 | 0.869 | +0.000 | 0.767 | 3 |
| 23 | `verified-adv-text-4of5-era2b` | verified-PV | 1 | 0.864 | 0.864 | -0.000 | 0.769 | 3 |
| 24 | `verified-t0-5-era2b` | verified-PV | 1 | 0.856 | 0.856 | -0.000 | 0.771 | 3 |
| 25 | `verified-adv-text-medium-vf-4of5-era2b` | verified-PV | 1 | 0.855 | 0.854 | -0.000 | 0.721 | 4 |
| 26 | `verified-adv-text-high-vf-4of5-era2b` | verified-PV | 1 | 0.852 | 0.852 | -0.000 | 0.699 | 4 |
| 27 | `verified-t0-0-era2b` | verified-PV | 1 | 0.851 | 0.851 | +0.000 | 0.778 | 4 |
| 28 | `verified-adv-pro-text-pro-vf-3of5-era2b` | verified-PV | 1 | 0.851 | 0.851 | -0.000 | 0.730 | 4 |
| 29 | `verified-adv-pro-text-medium-vf-3of5-era2b` | verified-PV | 1 | 0.850 | 0.849 | -0.000 | 0.730 | 4 |
| 30 | `verified-adv-pro-text-flash-vf-3of5-era2b` | verified-PV | 1 | 0.849 | 0.849 | +0.000 | 0.730 | 4 |
| 31 | `f35prop-f3vf-4of10-era2b` | verified-PV | 1 | 0.848 | 0.848 | -0.000 | 0.767 | 4 |
| 32 | `verified-t1-0-era2b` | verified-PV | 1 | 0.842 | 0.842 | +0.000 | 0.756 | 4 |
| 33 | `f35prop-f35vf-4of10-era2b` | verified-PV | 1 | 0.836 | 0.836 | +0.000 | 0.737 | 4 |
| 34 | `g384-ov192-image-min-k10-verified-p0.15-k9-era2b` | verified-PV | 1 | 0.834 | 0.834 | +0.000 | 0.793 | 4 |
| 35 | `g384-ov192-image-high-k10-verified-p0.20-k8-era2b` | verified-PV | 1 | 0.826 | 0.826 | +0.000 | 0.794 | 4 |
| 36 | `verified-adv-image-min-6of10-era2b` | verified-PV | 1 | 0.789 | 0.789 | -0.000 | 0.803 | 5 |
| 37 | `verified-adv-image-3of5-era2b` | verified-PV | 1 | 0.778 | 0.778 | -0.000 | 0.827 | 5 |
| 38 | `verified-adv-image-min-3of5-era2b` | verified-PV | 1 | 0.767 | 0.767 | -0.000 | 0.846 | 6 |
| 39 | `verified-adv-pro-image-pro-vf-3of5-era2b` | verified-PV | 1 | 0.711 | 0.711 | -0.000 | 0.850 | 6 |
