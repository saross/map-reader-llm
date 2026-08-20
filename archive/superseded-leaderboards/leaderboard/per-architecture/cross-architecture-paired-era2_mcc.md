# Cross-architecture paired comparison — Era 2, MCC

**Generated**: Session 79 redesign (2026-04-25)
**Era**: 2
**Metric**: MCC
**Permutations**: 10,000, seed=42
**FDR**: BH at q=0.05 within Era

Pairs of architectures sharing the same proposer config tuple (model, config_version, instruction_file, thinking, T, N/K, track, vote_t). The PV-helps column flags when adding the verifier (or moving from single-pass to consensus, etc.) produces a statistically significant change after BH-FDR.

Conditions tested: 20

| Pair (arch_a -> arch_b) | A | MCC(A) | B | MCC(B) | delta | p_raw | p_BH | sig (q=0.05) |
|:---|:---|---:|:---|---:|---:|---:|---:|:---:|
| consensus -> pv | `h11-pvd-flash-high-image-n5` | 0.678 | `pv-high-image-t0.7-n10` | 0.797 | -0.1184 | 0.0007 | 0.0008 | Y |
| consensus -> pv | `h11-pvd-flash-high-text-n5` | 0.620 | `pv-flash-high-text-16of30` | 0.790 | -0.1698 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `h11-pvd-image-n5` | 0.405 | `pv-min-image-t0.7-n10` | 0.822 | -0.4168 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `h11-pvd-pro-high-image-n5` | 0.761 | `pv-high-image-t0.7-n5` | 0.836 | -0.0745 | 0.0183 | 0.0193 | Y |
| consensus -> pv | `h11-pvd-pro-high-text-n5` | 0.726 | `pv-high-text-t0.7-n10` | 0.764 | -0.0377 | 0.2214 | 0.2214 |  |
| consensus -> pv | `h11-pvd-text-n10` | 0.316 | `pv-min-text-t0.7-n10` | 0.777 | -0.4609 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-high-image-t0.3` | 0.683 | `pv-high-image-t0.3-n10` | 0.815 | -0.1320 | 0.0002 | 0.0002 | Y |
| consensus -> pv | `p3a-high-image-t1.0` | 0.646 | `pv-high-image-t1.0-n10` | 0.800 | -0.1547 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-min-image-t0.3` | 0.340 | `pv-min-image-t0.3-n10` | 0.838 | -0.4981 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-min-image-t1.0` | 0.442 | `pv-min-image-t1.0-n10` | 0.811 | -0.3681 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-high-text-t0.0` | 0.450 | `pv-high-text-t0.0-n3` | 0.775 | -0.3250 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-high-text-t0.3` | 0.587 | `pv-high-text-t0.3-n10` | 0.787 | -0.1999 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-high-text-t0.3-n5` | 0.587 | `pv-high-text-t0.3-n5` | 0.776 | -0.1885 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-high-text-t1.0` | 0.575 | `pv-high-text-t1.0-n10` | 0.791 | -0.2161 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-high-text-t1.0-n5` | 0.575 | `pv-high-text-t1.0-n5` | 0.757 | -0.1818 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-minimal-text-t0.0` | 0.223 | `pv-min-text-t0.0-n3` | 0.783 | -0.5600 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-minimal-text-t0.3` | 0.313 | `pv-min-text-t0.3-n10` | 0.773 | -0.4601 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-minimal-text-t0.3-n5` | 0.313 | `pv-min-text-t0.3-n5` | 0.774 | -0.4606 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-minimal-text-t1.0` | 0.415 | `pv-min-text-t1.0-n10` | 0.781 | -0.3662 | 0.0000 | 0.0000 | Y |
| consensus -> pv | `p3a-minimal-text-t1.0-n5` | 0.415 | `pv-min-text-t1.0-n5` | 0.780 | -0.3644 | 0.0000 | 0.0000 | Y |

