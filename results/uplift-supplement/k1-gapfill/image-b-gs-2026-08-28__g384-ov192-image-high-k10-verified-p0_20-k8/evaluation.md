# Evaluation: image-b-gs-2026-08-28__g384-ov192-image-high-k10-verified-p0_20-k8-n1

**Generated**: 2026-10-09T09:55:38.022046+00:00  
**Detections**: 2792  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.104 | WITHHELD * | 0.060 | WITHHELD * | 0.371 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 10m | 0.199 | WITHHELD * | 0.116 | WITHHELD * | 0.710 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 15m | 0.250 | WITHHELD * | 0.145 | WITHHELD * | 0.892 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 20m | 0.260 | WITHHELD * | 0.151 | WITHHELD * | 0.930 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 25m | 0.264 | WITHHELD * | 0.153 | WITHHELD * | 0.942 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 30m | 0.266 | WITHHELD * | 0.155 | WITHHELD * | 0.951 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 35m | 0.270 | WITHHELD * | 0.157 | WITHHELD * | 0.965 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 40m | 0.273 | WITHHELD * | 0.159 | WITHHELD * | 0.974 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 45m | 0.275 | WITHHELD * | 0.160 | WITHHELD * | 0.981 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 50m | 0.275 | WITHHELD * | 0.160 | WITHHELD * | 0.984 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 75m | 0.277 | WITHHELD * | 0.161 | WITHHELD * | 0.991 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 100m | 0.278 | WITHHELD * | 0.162 | WITHHELD * | 0.993 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 125m | 0.278 | WITHHELD * | 0.162 | WITHHELD * | 0.993 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 150m | 0.278 | WITHHELD * | 0.162 | WITHHELD * | 0.993 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |

\* **Per-tile statistics WITHHELD** — the tile-join invariant refused this cell's per-tile table (`tile_join_detection_shortfall`): 63 of 2629 in-frame detections were booked to a tile (shortfall 2566, 0 outside the frame entirely, 899 inside more than one tile). The two tile vocabularies: the frame carries 487 names under map prefixes ['K-35-052-4_32635', 'K-35-053-3_Elenovo', 'K-35-062-2_Rakovski', 'K-35-078-1_Lesovo'] (e.g. ['K-35-052-4_32635_x0_y0.png', 'K-35-052-4_32635_x0_y1008.png', 'K-35-052-4_32635_x0_y1344.png']); the detections carry 1007 names under ['K-35-052-4_32635', 'K-35-053-3_Elenovo', 'K-35-062-2_Rakovski', 'K-35-078-1_Lesovo'] (e.g. ['K-35-052-4_32635_x0_y0.png', 'K-35-052-4_32635_x0_y1152.png', 'K-35-052-4_32635_x0_y1344.png']), of which 28 are in the frame's vocabulary. Withheld, and named rather than silently omitted: tile_classification, tile_mcc, tile_sensitivity, tile_specificity, per_tile_table, bootstrap_ci_f1, bootstrap_ci_precision, bootstrap_ci_recall, per_tile_permutation_tests, coverage_diagnostics. The bootstrap confidence intervals are withheld with the tile block because they resample TILES (the resampling unit fixed in Decision 10), not matched pairs, so the refused table is their input too. **Reported in full, and unaffected**: the F1, precision and recall POINT estimates in the columns above — `lib_advanced_metrics.calculate_f1_internal` matches detections to references geometrically per map sheet and consults no tile. Per the PI's ruling of 2026-09-13 (Session 153, ruling 6); see `reports/tile-mcc-geometric-join-2026-09-12.md` and `reports/recovery-drop-fix-2026-09-13.md` § 6.3.

