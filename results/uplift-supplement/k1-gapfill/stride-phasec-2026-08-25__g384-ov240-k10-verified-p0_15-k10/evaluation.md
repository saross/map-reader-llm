# Evaluation: stride-phasec-2026-08-25__g384-ov240-k10-verified-p0_15-k10-n1

**Generated**: 2026-10-09T09:59:18.037704+00:00  
**Detections**: 5698  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 20m | 0.143 | WITHHELD * | 0.077 | WITHHELD * | 0.970 | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * | WITHHELD * |

\* **Per-tile statistics WITHHELD** — the tile-join invariant refused this cell's per-tile table (`tile_join_detection_shortfall`): 116 of 5361 in-frame detections were booked to a tile (shortfall 5245, 0 outside the frame entirely, 1796 inside more than one tile). The two tile vocabularies: the frame carries 487 names under map prefixes ['K-35-052-4_32635', 'K-35-053-3_Elenovo', 'K-35-062-2_Rakovski', 'K-35-078-1_Lesovo'] (e.g. ['K-35-052-4_32635_x0_y0.png', 'K-35-052-4_32635_x0_y1008.png', 'K-35-052-4_32635_x0_y1344.png']); the detections carry 2365 names under ['K-35-052-4_32635', 'K-35-053-3_Elenovo', 'K-35-062-2_Rakovski', 'K-35-078-1_Lesovo'] (e.g. ['K-35-052-4_32635_x0_y0.png', 'K-35-052-4_32635_x0_y1008.png', 'K-35-052-4_32635_x0_y1152.png']), of which 64 are in the frame's vocabulary. Withheld, and named rather than silently omitted: tile_classification, tile_mcc, tile_sensitivity, tile_specificity, per_tile_table, bootstrap_ci_f1, bootstrap_ci_precision, bootstrap_ci_recall, per_tile_permutation_tests, coverage_diagnostics. The bootstrap confidence intervals are withheld with the tile block because they resample TILES (the resampling unit fixed in Decision 10), not matched pairs, so the refused table is their input too. **Reported in full, and unaffected**: the F1, precision and recall POINT estimates in the columns above — `lib_advanced_metrics.calculate_f1_internal` matches detections to references geometrically per map sheet and consults no tile. Per the PI's ruling of 2026-09-13 (Session 153, ruling 6); see `reports/tile-mcc-geometric-join-2026-09-12.md` and `reports/recovery-drop-fix-2026-09-13.md` § 6.3.

