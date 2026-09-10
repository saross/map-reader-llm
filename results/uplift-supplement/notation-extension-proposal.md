# Notation-key extension proposal — uplift supplement

> **Last revised**: 2026-09-10 (regenerated from committed artefacts by `scripts/build_uplift_supplement.py`; original publication; proposed § 7 additions). See [§ Changelog](#changelog) for revision history.
>
> **First published**: 2026-08-29. Regenerated 2026-09-10T07:16:15Z. This document is generated in full from committed artefacts, so its body always reflects the current corpus; git carries the content history.

The canonical key `docs/methodology/notation-key.md` requires that
"new tables and dataset builders must conform to it or extend it here
first". The uplift-supplement builder validates every column it writes
against §§ 6-7, which sanction 151 names. A builder must not
amend the canonical key unilaterally, so columns the key does not name
are declared in `scripts/lib_uplift_supplement.py` (`COLUMN_EXTENSIONS`)
and proposed here for the PI to fold into § 7; an undeclared column
still fails loudly.

## Proposed additions to § 7 (0 pending)

None: every declared extension is sanctioned by the key.

## Extensions already sanctioned by the key (85)

Landed as § 7.1 on 2026-09-10 (PI ruling 2(i) of the supplement's
registration walk-through); still declared here so the builder's
validation and the key cannot drift apart silently.

| Column | Extends |
|---|---|
| `K` | § 1 (K) |
| `aggregation` | conditions-manifest schema |
| `architecture` | conditions-manifest schema |
| `blocked_reason` | anti-confabulation |
| `bounds_path` | § 6 |
| `buffer_m` | § 1 (R / R_m) |
| `ci_method` | § 5 (CI, BCa, percentile) |
| `ci_unreliable` | conditions-manifest schema |
| `command` | anti-confabulation |
| `condition_id` | § 7 (registry ids) |
| `corpus` | § 6 |
| `cost_basis` | § 8 (audited / list / flex) |
| `delta` | § 3 (transfer tax) |
| `detections_path` | anti-confabulation |
| `engine` | anti-confabulation |
| `eval_path` | anti-confabulation |
| `frame_id` | § 6 |
| `geometry` | § 2 (geometry cell) |
| `geometry_basis` | § 2 |
| `headline_reference` | § 4 |
| `is_primary_buffer` | § 1 (R) |
| `job_id` | anti-confabulation |
| `k1_with_verifier` | § 2 (PV) |
| `k1_with_verifier_reason` | anti-confabulation |
| `materialise_command` | anti-confabulation |
| `materialise_filter` | § 1 (k) |
| `mde_50` | § 5 (MDE 50 %/80 %) |
| `mde_80` | § 5 (MDE 50 %/80 %) |
| `mde_instrument` | § 5 |
| `mde_join_basis` | § 5 |
| `mde_source` | § 5 |
| `metric` | § 5 |
| `metrics_source` | anti-confabulation |
| `modality` | § 2 (image / text) |
| `model_used` | passes-manifest schema |
| `n_comparisons` | § 5 |
| `n_conditions` | § 6 |
| `n_refs` | § 4 |
| `notes` | anti-confabulation |
| `null_sd_hi` | § 5 (null SD) |
| `null_sd_lo` | § 5 (null SD) |
| `output_dir` | anti-confabulation |
| `overlap_px` | § 2 (geometry cell) |
| `pair_id` | § 6 (stratum_id) |
| `pairing_basis` | anti-confabulation |
| `proposer_pool` | § 7 (registry ids: run_id::pool::runN) |
| `rationale` | anti-confabulation |
| `reference` | § 4 |
| `reference_basis` | § 4 |
| `reference_consumed_path` | anti-confabulation |
| `reference_path` | § 4 |
| `registered_analysis_id` | analyses-manifest schema |
| `run_id` | § 7 (registry ids) |
| `rung` | § 1 (N) |
| `source_condition` | § 7 (registry ids) |
| `source_condition_id` | § 7 (registry ids) |
| `source_stratum_id` | § 6 |
| `source_value` | § 5 |
| `status` | anti-confabulation |
| `stride_px` | § 2 (geometry cell) |
| `target_condition_id` | § 7 (registry ids) |
| `target_stratum_id` | § 6 |
| `target_value` | § 5 |
| `tax_kind` | § 3 (transfer tax) |
| `temperature` | § 1 (T) |
| `thinking` | § 2 (MIN / HIGH / low) |
| `tile_px` | § 2 (geometry cell) |
| `transfer` | heterogeneity design § 3 |
| `union_path` | anti-confabulation |
| `unverified_condition_id` | § 7 (registry ids) |
| `unverified_detections_path` | anti-confabulation |
| `unverified_eval_path` | anti-confabulation |
| `unverified_stratum_basis` | anti-confabulation |
| `unverified_stratum_id` | § 6 |
| `unverified_value` | § 5 |
| `uplift` | § 3 |
| `uplift_metric` | § 5 |
| `verified` | § 2 (PV) |
| `verified_condition_id` | § 7 (registry ids) |
| `verified_stratum_id` | § 6 |
| `verified_value` | § 5 |
| `verifier_crop_manifest` | anti-confabulation |
| `verifier_floor_basis` | anti-confabulation |
| `verifier_min_vote_seen` | § 1 (k) |
| `verifier_variant` | § 2 (PV) |

## The § 6 frame table against the registered runs

Complete: every frame the registered runs use (7) is named in § 6.

## Changelog

### 2026-09-08 — Verifier pairing completed on the current register (S151): 69 of 169 pairs computed

**Refresh trigger**: the vote-shell materialiser's union mode (`scripts/materialise_pairing_twin.py --union`, `b504a062f`) and the pairing builder's materialise-and-score commands; 47 twins materialised and scored on sapphire (`51392bc59`), their evaluations waived under ruling 1. `verifier-uplift.csv` now computes 69 of 169 pairs on F1 (was 21 of 118) and 68 on MCC; the 100 pending pairs are the unresolved twins the pairing report lists. **One artefact resolved (2026-09-09)**: the pre-existing pair `55maps-generalisation::verified-paired` had read an uplift of 0.7921 because its consensus-file twin scored F1 0 on 2026-08-29 — the committed `consensus-4of5.geojson` carries projected coordinates and no `crs` member, which RFC 7946 readers take as WGS84. The twin is now copied with EPSG:32635 declared (`materialise_pairing_twin.py --consensus --declare-crs`; the pairing builder routes such files through it) and re-scored: twin 0.5063 at 50 m, uplift 0.2858, in line with its siblings (0.28–0.31); the zero-scored evaluation is archived under `archive/uplift-supplement-pairing/`. **What did not change**: every condition row; the strata and MDE joins; the supplement remains unregistered.

### 2026-09-08 — Gemini 3.7 pool pass count corrected (S151): K 4 -> 5 on twelve rows

**Refresh trigger**: the passes extractor could not read the Gemini 3.7 55-map pool's gzipped `run_3` meta, so the passes manifest counted four passes and this supplement summed the pool's runner-estimator cost over four (`edc832c06` fixed the reader). The twelve `gemini37-55map-2026-08-29` rows now carry K = 5 and the five-pass cost (US$48.62, was US$44.59). The same session scored the eight r2 K = 1 anchors that pool's missing pass had blocked (`a0f08475e`), waived under ruling 1. **What did not change**: every metric on every row; the strata and MDE joins.

### 2026-09-08 — Verifier-stage refresh bookkeeping (S151): one late S150-b row swept up

**Refresh trigger**: the after-run bookkeeping of the verifier-stage refresh (`planning/verifier-stage-refresh-2026-09-08.md` § 5). The three refreshed stages are `verifier_passes` inventory rows, not conditions, so they add no row here. The rebuild does pick up one condition registered after the previous build: `pv-diag-384::flash-high-image-n5-image-t0.0-consensus-3of3` (`8e98f8edf`, the consensus-calibration closure; 437 -> 438 conditions, 5,416 -> 5,430 condition x buffer rows; the 4-map-gs strata's condition counts move by one). **What did not change**: every other row's metrics; the MDE joins.

### 2026-09-08 — Recovery-consistency refresh: eleven GS rows re-scored on rebuilt sweeps

**Refresh trigger**: the S150 recovery-consistency audit (`reports/recovery-consistency-audit-2026-09-08.md`). The six `n1-outstanding-384` pro-*-high-t0 consensus rows and the five `e47-propose-brief` consensus rows now cite evaluations scored on consensus sweeps rebuilt from the E71-recovered passes (`results/recovery-reeval-2026-09-08/`); the passes manifest counts recovery fragments towards their pass (70 -> 22 partial passes) and the conditions manifest's per-buffer coverage is filled (355 of 437 rows). **What did not change**: every other row's metrics; the strata and MDE joins.

### 2026-09-07 — Reference r2 stratum; eight canonical rows re-stratified; post-E71 rows

**Refresh trigger**: the r2 recompute chain (card `planning/reference-revision-2026-09-06.md`, step 7a) registered 37 `-r2-gt` conditions, which join as the `55-map|r2|50m|55maps-8541` stratum (n_refs 5,018) beside the canonical, standardised, and student strata — all four kept (PI ruling 3, 2026-09-07: the supplement is the register's flatten; the stratum column separates the chains). Ruling 3a registered nine `-post-e71` conditions on the 4-map corpus (curator reference), which join their runs' strata. **Also fixed**: the corrected-F1 engine records its student BASE layer as `ground_truth`, and once ruling 2 attached that metadata to the stride canonical rows, eight `-canonical-gt` rows had dropped into the student stratum on regeneration; the explicit label suffix now outranks a bare base-layer resolution (`bb545f5f1`), restoring canonical 16 / student 5. **What did not change**: every pre-existing row's metrics and CIs; the MDE joins.

### 2026-08-29 — Original publication

Generated with the first build of the uplift-supplement dataset
(card `planning/uplift-supplement-2026-08-28.md`, Build order step 1).
