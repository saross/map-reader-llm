# Evaluation: gemini37-screen-2026-08-28__g37-text-k1-verified-opmax

**Generated**: 2026-09-13T13:56:22.394480+00:00  
**Detections**: 502  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.473 | WITHHELD * | 0.438 | WITHHELD * | 0.513 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 10m | 0.780 | WITHHELD * | 0.723 | WITHHELD * | 0.846 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 15m | 0.831 | WITHHELD * | 0.771 | WITHHELD * | 0.902 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 20m | 0.842 | WITHHELD * | 0.781 | WITHHELD * | 0.914 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 25m | 0.855 | WITHHELD * | 0.793 | WITHHELD * | 0.928 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 30m | 0.857 | WITHHELD * | 0.795 | WITHHELD * | 0.930 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 35m | 0.857 | WITHHELD * | 0.795 | WITHHELD * | 0.930 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 40m | 0.857 | WITHHELD * | 0.795 | WITHHELD * | 0.930 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 45m | 0.859 | WITHHELD * | 0.797 | WITHHELD * | 0.932 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 50m | 0.864 | WITHHELD * | 0.801 | WITHHELD * | 0.937 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 75m | 0.864 | WITHHELD * | 0.801 | WITHHELD * | 0.937 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 100m | 0.870 | WITHHELD * | 0.807 | WITHHELD * | 0.944 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 125m | 0.870 | WITHHELD * | 0.807 | WITHHELD * | 0.944 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |
| 150m | 0.870 | WITHHELD * | 0.807 | WITHHELD * | 0.944 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |

\* **Per-tile statistics WITHHELD** — the tile-join invariant refused this cell's per-tile table (`tile_join_detection_shortfall`): 21 of 468 in-frame detections were booked to a tile (shortfall 447, 34 outside the frame entirely, 122 inside more than one tile). The two tile vocabularies: the frame carries 467 names under map prefixes ['K-35-052-4_32635', 'K-35-053-3_Elenovo', 'K-35-062-2_Rakovski', 'K-35-078-1_Lesovo'] (e.g. ['K-35-052-4_32635_x0_y0.png', 'K-35-052-4_32635_x0_y1008.png', 'K-35-052-4_32635_x0_y1344.png']); the detections carry 319 names under ['K-35-052-4_32635', 'K-35-053-3_Elenovo', 'K-35-062-2_Rakovski', 'K-35-078-1_Lesovo'] (e.g. ['K-35-052-4_32635_x0_y1152.png', 'K-35-052-4_32635_x0_y1536.png', 'K-35-052-4_32635_x0_y192.png']), of which 11 are in the frame's vocabulary. Withheld, and named rather than silently omitted: tile_classification, tile_mcc, tile_sensitivity, tile_specificity, per_tile_table, bootstrap_ci_f1, bootstrap_ci_precision, bootstrap_ci_recall, per_tile_permutation_tests, coverage_diagnostics. The bootstrap confidence intervals are withheld with the tile block because they resample TILES (the resampling unit fixed in Decision 10), not matched pairs, so the refused table is their input too. **Reported in full, and unaffected**: the F1, precision and recall POINT estimates in the columns above — `lib_advanced_metrics.calculate_f1_internal` matches detections to references geometrically per map sheet and consults no tile. Per the PI's ruling of 2026-09-13 (Session 153, ruling 6); see `reports/tile-mcc-geometric-join-2026-09-12.md` and `reports/recovery-drop-fix-2026-09-13.md` § 6.3.

