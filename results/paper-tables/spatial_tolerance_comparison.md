# Spatial Tolerance Comparison

> **⚠ Superseded figures (2026-08-02, E72)**: the three `flash-min-text-t10`
> rows — present in both the F1-by-buffer table and the precision/recall table
> — derive from `outputs/h11/consensus-384-UNINTENDED-T1.0`, a 240-tile study
> scored against the 487-tile bounds this document declares (coverage confound
> — see protocol-errata E43 correction block + E72), and understate that arm by
> ~0.17–0.19 F1 at every buffer. Their buffer-to-buffer *deltas* are less
> affected than their levels, but neither should be cited. (The companion
> `spatial_tolerance_curve.csv` does not include these conditions and is
> unaffected.) Regenerated 23-condition board:
> `results/e43-board-regen/`. Matched-scope analysis:
> `results/e43-matched-temperature/`. Dated snapshot; body unchanged; do not
> cite the affected rows.

**Generated**: 2026-03-26T20:39:40.449698+00:00  
**Buffers**: 20, 30, 40, 50 m  
**Bounds**: full_evaluation_bounds.geojson (487 tiles, 435 mounds)  

## F1 with 95% CI by Buffer Distance

| Condition | Type | F1 @ 20m | F1 @ 30m | F1 @ 40m | F1 @ 50m | Delta 20m->50m |
|---|---|---|---|---|---|---|
| flash-high-text-16-of-30--flash-min-vf | pv | 0.890 [0.863, 0.915] | 0.904 [0.878, 0.928] | 0.904 [0.878, 0.928] | 0.904 [0.878, 0.928] | +0.014 |
| flash-high-text-4-of-5--flash-min-vf | pv | 0.864 [0.833, 0.893] | 0.891 [0.863, 0.916] | 0.891 [0.863, 0.916] | 0.891 [0.863, 0.916] | +0.027 |
| flash-high-text-4-of-5--flash-medium-vf | pv | 0.859 [0.827, 0.887] | 0.885 [0.855, 0.911] | 0.885 [0.855, 0.911] | 0.885 [0.855, 0.911] | +0.026 |
| flash-high-text-9-of-10--flash-min-vf | pv | 0.856 [0.825, 0.885] | 0.869 [0.837, 0.897] | 0.869 [0.837, 0.897] | 0.869 [0.837, 0.897] | +0.013 |
| pro-high-text-3-of-5--flash-min-vf | pv | 0.849 [0.812, 0.883] | 0.865 [0.828, 0.896] | 0.867 [0.832, 0.898] | 0.867 [0.832, 0.898] | +0.018 |
| pro-high-text N=5 | consensus | 0.840 [0.800, 0.875] | 0.855 [0.820, 0.887] | 0.858 [0.822, 0.890] | 0.858 [0.822, 0.890] | +0.017 |
| text-baseline--flash-min-vf | pv | 0.814 [0.780, 0.844] | 0.832 [0.799, 0.857] | 0.839 [0.807, 0.865] | 0.839 [0.807, 0.865] | +0.024 |
| flash-high-text N=30 | consensus | 0.814 [0.778, 0.846] | 0.826 [0.793, 0.858] | 0.826 [0.793, 0.858] | 0.826 [0.793, 0.858] | +0.012 |
| flash-high-text N=10 | consensus | 0.797 [0.757, 0.830] | 0.811 [0.773, 0.842] | 0.811 [0.773, 0.842] | 0.811 [0.773, 0.842] | +0.014 |
| flash-high-text N=5 | consensus | 0.779 [0.739, 0.817] | 0.788 [0.750, 0.823] | 0.788 [0.750, 0.823] | 0.788 [0.750, 0.823] | +0.009 |
| flash-high-image-3-of-5--flash-min-vf | pv | 0.778 [0.735, 0.816] | 0.851 [0.815, 0.882] | 0.872 [0.840, 0.900] | 0.877 [0.847, 0.903] | +0.099 |
| flash-high-image N=10 | consensus | 0.750 [0.707, 0.790] | 0.812 [0.777, 0.841] | 0.829 [0.795, 0.859] | 0.834 [0.799, 0.862] | +0.084 |
| flash-high-image N=5 | consensus | 0.727 [0.687, 0.765] | 0.799 [0.762, 0.829] | 0.818 [0.783, 0.849] | 0.827 [0.793, 0.856] | +0.100 |
| image-baseline--flash-min-vf | pv | 0.717 [0.673, 0.754] | 0.782 [0.744, 0.813] | 0.799 [0.764, 0.829] | 0.808 [0.775, 0.837] | +0.091 |
| pro-high-image N=5 | consensus | 0.700 [0.653, 0.741] | 0.821 [0.787, 0.851] | 0.852 [0.823, 0.881] | 0.865 [0.839, 0.893] | +0.165 |
| flash-min-image N=10 | consensus | 0.680 [0.634, 0.723] | 0.733 [0.692, 0.770] | 0.751 [0.711, 0.786] | 0.753 [0.713, 0.787] | +0.073 |
| flash-min-image N=5 | consensus | 0.664 [0.619, 0.706] | 0.724 [0.681, 0.763] | 0.743 [0.701, 0.779] | 0.750 [0.708, 0.785] | +0.086 |
| flash-min-text-t07 N=30 | consensus | 0.661 [0.610, 0.706] | 0.669 [0.621, 0.715] | 0.669 [0.621, 0.715] | 0.669 [0.621, 0.715] | +0.008 |
| flash-min-text-t07 N=5 | consensus | 0.640 [0.584, 0.690] | 0.647 [0.592, 0.697] | 0.647 [0.592, 0.697] | 0.647 [0.592, 0.697] | +0.007 |
| flash-min-text-t07 N=10 | consensus | 0.633 [0.583, 0.680] | 0.641 [0.591, 0.689] | 0.641 [0.591, 0.689] | 0.641 [0.591, 0.689] | +0.008 |
| single-pass-t0 N=10 | consensus | 0.552 [0.491, 0.610] | 0.563 [0.500, 0.621] | 0.567 [0.505, 0.625] | 0.567 [0.505, 0.625] | +0.015 |
| single-pass-t0 N=5 | consensus | 0.544 [0.481, 0.602] | 0.554 [0.490, 0.611] | 0.558 [0.493, 0.617] | 0.558 [0.493, 0.617] | +0.014 |
| flash-min-text-t10 N=5 | consensus | 0.471 [0.395, 0.535] | 0.479 [0.406, 0.545] | 0.482 [0.410, 0.547] | 0.485 [0.412, 0.549] | +0.014 |
| flash-min-text-t10 N=30 | consensus | 0.467 [0.395, 0.532] | 0.477 [0.406, 0.540] | 0.481 [0.408, 0.546] | 0.484 [0.410, 0.548] | +0.017 |
| flash-min-text-t10 N=10 | consensus | 0.462 [0.391, 0.526] | 0.469 [0.398, 0.535] | 0.475 [0.403, 0.540] | 0.477 [0.407, 0.542] | +0.016 |

## Precision and Recall at Each Buffer

| Condition | P @ 20m | R @ 20m | P @ 30m | R @ 30m | P @ 40m | R @ 40m | P @ 50m | R @ 50m |
|---|---|---|---|---|---|---|---|---|
| flash-high-text-16-of-30--flash-min-vf | 0.915 | 0.867 | 0.930 | 0.880 | 0.930 | 0.880 | 0.930 | 0.880 |
| flash-high-text-4-of-5--flash-min-vf | 0.915 | 0.818 | 0.943 | 0.844 | 0.943 | 0.844 | 0.943 | 0.844 |
| flash-high-text-4-of-5--flash-medium-vf | 0.878 | 0.841 | 0.904 | 0.867 | 0.904 | 0.867 | 0.904 | 0.867 |
| flash-high-text-9-of-10--flash-min-vf | 0.957 | 0.775 | 0.972 | 0.786 | 0.972 | 0.786 | 0.972 | 0.786 |
| pro-high-text-3-of-5--flash-min-vf | 0.957 | 0.763 | 0.974 | 0.777 | 0.977 | 0.779 | 0.977 | 0.779 |
| pro-high-text N=5 | 0.918 | 0.775 | 0.935 | 0.788 | 0.937 | 0.791 | 0.937 | 0.791 |
| text-baseline--flash-min-vf | 0.789 | 0.841 | 0.806 | 0.860 | 0.812 | 0.867 | 0.812 | 0.867 |
| flash-high-text N=30 | 0.834 | 0.795 | 0.846 | 0.807 | 0.846 | 0.807 | 0.846 | 0.807 |
| flash-high-text N=10 | 0.800 | 0.793 | 0.814 | 0.807 | 0.814 | 0.807 | 0.814 | 0.807 |
| flash-high-text N=5 | 0.798 | 0.761 | 0.807 | 0.770 | 0.807 | 0.770 | 0.807 | 0.770 |
| flash-high-image-3-of-5--flash-min-vf | 0.800 | 0.756 | 0.876 | 0.828 | 0.898 | 0.848 | 0.903 | 0.853 |
| flash-high-image N=10 | 0.778 | 0.724 | 0.788 | 0.837 | 0.805 | 0.855 | 0.809 | 0.860 |
| flash-high-image N=5 | 0.676 | 0.786 | 0.743 | 0.864 | 0.761 | 0.885 | 0.769 | 0.894 |
| image-baseline--flash-min-vf | 0.663 | 0.779 | 0.724 | 0.851 | 0.740 | 0.869 | 0.748 | 0.878 |
| pro-high-image N=5 | 0.673 | 0.729 | 0.790 | 0.855 | 0.820 | 0.887 | 0.832 | 0.901 |
| flash-min-image N=10 | 0.640 | 0.726 | 0.643 | 0.853 | 0.659 | 0.874 | 0.660 | 0.876 |
| flash-min-image N=5 | 0.608 | 0.731 | 0.663 | 0.798 | 0.681 | 0.818 | 0.686 | 0.825 |
| flash-min-text-t07 N=30 | 0.602 | 0.733 | 0.609 | 0.743 | 0.609 | 0.743 | 0.609 | 0.743 |
| flash-min-text-t07 N=5 | 0.533 | 0.800 | 0.539 | 0.809 | 0.539 | 0.809 | 0.539 | 0.809 |
| flash-min-text-t07 N=10 | 0.562 | 0.724 | 0.570 | 0.733 | 0.570 | 0.733 | 0.570 | 0.733 |
| single-pass-t0 N=10 | 0.410 | 0.846 | 0.418 | 0.862 | 0.421 | 0.869 | 0.421 | 0.869 |
| single-pass-t0 N=5 | 0.396 | 0.867 | 0.404 | 0.883 | 0.407 | 0.890 | 0.407 | 0.890 |
| flash-min-text-t10 N=5 | 0.583 | 0.395 | 0.593 | 0.402 | 0.597 | 0.405 | 0.600 | 0.407 |
| flash-min-text-t10 N=30 | 0.499 | 0.439 | 0.509 | 0.448 | 0.571 | 0.416 | 0.574 | 0.418 |
| flash-min-text-t10 N=10 | 0.545 | 0.400 | 0.555 | 0.407 | 0.561 | 0.411 | 0.564 | 0.414 |

