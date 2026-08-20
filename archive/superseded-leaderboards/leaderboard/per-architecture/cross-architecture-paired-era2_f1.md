# Cross-architecture paired comparison — Era 2, F1

**Generated**: Session 79 redesign (2026-04-25)
**Era**: 2
**Metric**: F1
**Permutations**: 10,000, seed=42
**FDR**: BH at q=0.05 within Era

Pairs of architectures sharing the same proposer config tuple (model, config_version, instruction_file, thinking, T, N/K, track, vote_t). The PV-helps column flags when adding the verifier (or moving from single-pass to consensus, etc.) produces a statistically significant change after BH-FDR.

Conditions tested: 20

| Pair (arch_a -> arch_b) | A | F1(A) | B | F1(B) | delta | p_raw | p_BH | sig (q=0.05) |
|:---|:---|---:|:---|---:|---:|---:|---:|:---:|
| consensus -> pv | `h11-pvd-flash-high-image-n5` | 0.750 | `pv-high-image-t0.7-n10` | 0.776 | -0.0261 | 0.0211 | 0.0234 | Y |
| consensus -> pv | `h11-pvd-flash-high-text-n5` | 0.814 | `pv-flash-high-text-16of30` | 0.890 | -0.0761 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `h11-pvd-image-n5` | 0.680 | `pv-min-image-t0.7-n10` | 0.788 | -0.1078 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `h11-pvd-pro-high-image-n5` | 0.700 | `pv-high-image-t0.7-n5` | 0.787 | -0.0870 | 0.0012 | 0.0015 | Y |
| consensus -> pv | `h11-pvd-pro-high-text-n5` | 0.836 | `pv-high-text-t0.7-n10` | 0.874 | -0.0385 | 0.0375 | 0.0395 | Y |
| consensus -> pv | `h11-pvd-text-n10` | 0.618 | `pv-min-text-t0.7-n10` | 0.873 | -0.2541 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-high-image-t0.3` | 0.731 | `pv-high-image-t0.3-n10` | 0.769 | -0.0377 | 0.0149 | 0.0175 | Y |
| consensus -> pv | `p3a-high-image-t1.0` | 0.735 | `pv-high-image-t1.0-n10` | 0.763 | -0.0282 | 0.0607 | 0.0607 |  |
| consensus -> pv | `p3a-min-image-t0.3` | 0.660 | `pv-min-image-t0.3-n10` | 0.782 | -0.1222 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-min-image-t1.0` | 0.646 | `pv-min-image-t1.0-n10` | 0.741 | -0.0950 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-high-text-t0.0` | 0.605 | `pv-high-text-t0.0-n3` | 0.823 | -0.2183 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-high-text-t0.3` | 0.789 | `pv-high-text-t0.3-n10` | 0.872 | -0.0831 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-high-text-t0.3-n5` | 0.789 | `pv-high-text-t0.3-n5` | 0.886 | -0.0972 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-high-text-t1.0` | 0.773 | `pv-high-text-t1.0-n10` | 0.880 | -0.1077 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-high-text-t1.0-n5` | 0.773 | `pv-high-text-t1.0-n5` | 0.861 | -0.0880 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-minimal-text-t0.0` | 0.593 | `pv-min-text-t0.0-n3` | 0.862 | -0.2691 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-minimal-text-t0.3` | 0.642 | `pv-min-text-t0.3-n10` | 0.868 | -0.2258 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-minimal-text-t0.3-n5` | 0.642 | `pv-min-text-t0.3-n5` | 0.878 | -0.2354 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-minimal-text-t1.0` | 0.667 | `pv-min-text-t1.0-n10` | 0.877 | -0.2104 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-minimal-text-t1.0-n5` | 0.667 | `pv-min-text-t1.0-n5` | 0.871 | -0.2048 | 0.0000 | 0.0000 | Y |

