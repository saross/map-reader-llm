# Evaluation: image-b-gs-2026-08-28__g384-ov192-image-min-k10-verified-p0_15-k9-n1

**Generated**: 2026-10-09T09:55:37.226646+00:00  
**Detections**: 2428  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.129 | WITHHELD * | 0.076 | WITHHELD * | 0.414 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 10m | 0.230 | WITHHELD * | 0.136 | WITHHELD * | 0.736 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 15m | 0.276 | WITHHELD * | 0.163 | WITHHELD * | 0.883 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 20m | 0.285 | WITHHELD * | 0.169 | WITHHELD * | 0.914 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 25m | 0.296 | WITHHELD * | 0.175 | WITHHELD * | 0.949 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 30m | 0.298 | WITHHELD * | 0.177 | WITHHELD * | 0.956 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 35m | 0.300 | WITHHELD * | 0.177 | WITHHELD * | 0.960 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 40m | 0.300 | WITHHELD * | 0.178 | WITHHELD * | 0.963 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 45m | 0.302 | WITHHELD * | 0.179 | WITHHELD * | 0.970 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 50m | 0.303 | WITHHELD * | 0.180 | WITHHELD * | 0.972 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 75m | 0.307 | WITHHELD * | 0.182 | WITHHELD * | 0.984 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 100m | 0.308 | WITHHELD * | 0.182 | WITHHELD * | 0.986 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 125m | 0.308 | WITHHELD * | 0.182 | WITHHELD * | 0.986 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 150m | 0.308 | WITHHELD * | 0.182 | WITHHELD * | 0.986 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |

\* **Per-tile statistics WITHHELD** — the tile-join invariant refused this cell's per-tile table (`tile_join_detection_shortfall`): 61 of 2316 in-frame detections were booked to a tile (shortfall 2255, 0 outside the frame entirely, 820 inside more than one tile). The two tile vocabularies: the frame carries 487 names under map prefixes ['K-35-052-4_32635', 'K-35-053-3_Elenovo', 'K-35-062-2_Rakovski', 'K-35-078-1_Lesovo'] (e.g. ['K-35-052-4_32635_x0_y0.png', 'K-35-052-4_32635_x0_y1008.png', 'K-35-052-4_32635_x0_y1344.png']); the detections carry 1295 names under ['K-35-052-4_32635', 'K-35-053-3_Elenovo', 'K-35-062-2_Rakovski', 'K-35-078-1_Lesovo'] (e.g. ['K-35-052-4_32635_x0_y0.png', 'K-35-052-4_32635_x0_y1152.png', 'K-35-052-4_32635_x0_y1344.png']), of which 39 are in the frame's vocabulary. Withheld, and named rather than silently omitted: tile_classification, tile_mcc, tile_sensitivity, tile_specificity, per_tile_table, bootstrap_ci_f1, bootstrap_ci_precision, bootstrap_ci_recall, per_tile_permutation_tests, coverage_diagnostics. The bootstrap confidence intervals are withheld with the tile block because they resample TILES (the resampling unit fixed in Decision 10), not matched pairs, so the refused table is their input too. **Reported in full, and unaffected**: the F1, precision and recall POINT estimates in the columns above — `lib_advanced_metrics.calculate_f1_internal` matches detections to references geometrically per map sheet and consults no tile. Per the PI's ruling of 2026-09-13 (Session 153, ruling 6); see `reports/tile-mcc-geometric-join-2026-09-12.md` and `reports/recovery-drop-fix-2026-09-13.md` § 6.3.

