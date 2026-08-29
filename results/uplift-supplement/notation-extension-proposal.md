# Notation-key extension proposal — uplift supplement

> **Last revised**: 2026-08-29 (regenerated from committed artefacts by `scripts/build_uplift_supplement.py`; original publication; proposed § 7 additions). See [§ Changelog](#changelog) for revision history.
>
> **First published**: 2026-08-29. Regenerated 2026-08-29T04:34:08Z. This document is generated in full from committed artefacts, so its body always reflects the current corpus; git carries the content history.

The canonical key `docs/methodology/notation-key.md` requires that
"new tables and dataset builders must conform to it or extend it here
first". The uplift-supplement builder validates every column it writes
against §§ 6-7, which sanction 60 names. The columns below are
the ones the dataset needs that §§ 6-7 do not yet name. A builder must
not amend the canonical key unilaterally, so they are proposed here for
the PI to fold into § 7.

Until they land in the key, they are declared in
`scripts/lib_uplift_supplement.py` (`COLUMN_EXTENSIONS`), which is what
the builder validates against — so an undeclared column still fails
loudly.

## Proposed additions to § 7

| Column | Extends | Rationale |
|---|---|---|
| `K` | § 1 (K) | Passes RUN in the pool. The key defines the symbol; this is the column. |
| `aggregation` | conditions-manifest schema | none / greedy / wbf / consensus / verified. |
| `architecture` | conditions-manifest schema | single-pass / consensus / proposer-verifier — the evaluable architecture. |
| `blocked_reason` | anti-confabulation | Why a blocked job cannot run; never a placeholder, always a measured fact. |
| `bounds_path` | § 6 | The evaluation bounds defining the frame. |
| `buffer_m` | § 1 (R / R_m) | Third component, as an integer column; `R_m` is the corrected-F1 CSV's name. |
| `ci_method` | § 5 (CI, BCa, percentile) | The CI method the source evaluation recorded; omitted where it recorded none. |
| `ci_unreliable` | conditions-manifest schema | The measured D28/E72 reliability verdict carried through from the source. |
| `command` | anti-confabulation | The exact invocation the operator runs on sapphire. |
| `condition_id` | § 7 (registry ids) | The `run_id::label` composite spelled as a column name. |
| `corpus` | § 6 | First component of stratum_id: 4-map-gs or 55-map, from run-facts.json. |
| `cost_basis` | § 8 (audited / list / flex) | Which cost basis `cost_usd` carries; NOT the audited basis (see build report). |
| `delta` | § 3 (transfer tax) | target_value - source_value; a transfer tax when the sign is negative. |
| `detections_path` | anti-confabulation | The detection set scored. |
| `engine` | anti-confabulation | Which scorer the job needs: evaluate_detections or corrected_f1_multi_buffer. |
| `eval_path` | anti-confabulation | The evaluation artefact the metrics came from. |
| `frame_id` | § 6 | Fourth component: the evaluation frame id (era-1-340, era-2-487, ...). |
| `geometry` | § 2 (geometry cell) | The geometry cell label the key defines, as a column. |
| `geometry_basis` | § 2 | Which rule resolved the geometry: pool-name, label, or run-facts-tile-size. |
| `is_primary_buffer` | § 1 (R) | True where buffer_m is the corpus headline buffer (20 m GS / 50 m 55-map). |
| `job_id` | anti-confabulation | Primary key of a scoring job in a worklist. |
| `k1_with_verifier` | § 2 (PV) | derivable / blocked / not-applicable — the card's disclosed K = 1 PV anchor. |
| `k1_with_verifier_reason` | anti-confabulation | The measured ground for that verdict; never an approximation. |
| `materialise_filter` | § 1 (k) | The vote_count predicate that turns the union into the paired shell. |
| `mde_50` | § 5 (MDE 50 %/80 %) | Minimum detectable effect at 50 % power, joined from sensitivity.json. |
| `mde_80` | § 5 (MDE 50 %/80 %) | Minimum detectable effect at 80 % power, joined from sensitivity.json. |
| `mde_instrument` | § 5 | The named permutation instrument the MDE and null SD describe. |
| `mde_join_basis` | § 5 | The join key used (n_tiles + buffer_m) and any ambiguity it carries. |
| `mde_source` | § 5 | The artefact the instrument's null SD was measured from. |
| `metric` | § 5 | Which metric the delta is on (F1, MCC, precision, recall). |
| `metrics_source` | anti-confabulation | conditions-manifest or evaluation-json — where this row's metrics were read. |
| `modality` | § 2 (image / text) | Proposer input modality; the key names the values, not a column. |
| `model_used` | passes-manifest schema | Authoritative model identity, read from per-item metadata, never a name. |
| `n_comparisons` | § 5 | Pairwise comparisons the instrument's null SD was measured over. |
| `n_conditions` | § 6 | How many registered conditions resolve into the stratum. |
| `n_refs` | § 4 | Reference mounds in the stratum's reference file; the key gives no column name. |
| `notes` | anti-confabulation | Free text recording any gap or caveat attached to this row. |
| `null_sd_hi` | § 5 (null SD) | High end of the instrument's observed null-SD range. |
| `null_sd_lo` | § 5 (null SD) | Low end of the instrument's observed null-SD range. |
| `output_dir` | anti-confabulation | Where the job writes its evaluation. |
| `overlap_px` | § 2 (geometry cell) | Overlap in pixels, the second half of the geometry cell. |
| `pair_id` | § 6 (stratum_id) | Primary key of a transfer pair; the key defines the object, not the column. |
| `pairing_basis` | anti-confabulation | Which rule located the pre-verifier twin: registered, consensus-file, union. |
| `proposer_pool` | § 7 (registry ids: run_id::pool::runN) | The pool component of the pass id, as a column. |
| `rationale` | anti-confabulation | Why this pair is a meaningful comparison despite spanning strata. |
| `reference` | § 4 | Second component: curator / student / canonical / standardised. |
| `reference_basis` | § 4 | Which rule resolved `reference`: eval-ground-truth, label-suffix, or run-facts. |
| `reference_consumed_path` | anti-confabulation | The path the evaluation literally recorded, where it differs from the anchor. |
| `reference_path` | § 4 | The ground-truth GeoJSON the evaluation consumed (the re-verify anchor). |
| `registered_analysis_id` | analyses-manifest schema | The registered analysis this pair belongs to, where one exists. |
| `run_id` | § 7 (registry ids) | Foreign key to the run registry; the key names the composite, not the part. |
| `rung` | § 1 (N) | Which ladder rung the job scores (N = 1 for the K = 1 gap-fill). |
| `source_condition` | § 7 (registry ids) | The K >= 3 consensus cell whose K = 1 rung this job supplies. |
| `source_condition_id` | § 7 (registry ids) | The cell a calibration or claim came FROM. |
| `source_stratum_id` | § 6 | Its stratum — necessarily different from the target's. |
| `source_value` | § 5 | The metric's value in the source cell. |
| `status` | anti-confabulation | ready / blocked / already-registered — whether the job can run at all. |
| `stride_px` | § 2 (geometry cell) | tile_px - overlap_px, which the key defines as the stride. |
| `target_condition_id` | § 7 (registry ids) | The cell the claim was carried TO. |
| `target_stratum_id` | § 6 | The target cell's stratum; the delta is a transfer across the two. |
| `target_value` | § 5 | The metric's value in the target cell. |
| `tax_kind` | § 3 (transfer tax) | Which tax the pair isolates: geometry, reference, corpus, buffer, or frame. |
| `temperature` | § 1 (T) | Sampling temperature. `T` alone is too short to be a safe CSV header. |
| `thinking` | § 2 (MIN / HIGH / low) | Thinking level; the key names the levels, not a column. |
| `tile_px` | § 2 (geometry cell) | Tile size in pixels, the first half of the geometry cell. |
| `transfer` | heterogeneity design § 3 | Always TRUE here: the flag that licenses a cross-stratum number. |
| `union_path` | anti-confabulation | The committed vote >= 1 union the vote shell must be filtered out of. |
| `unverified_condition_id` | § 7 (registry ids) | The registered pre-verifier cell, where one already exists. |
| `unverified_detections_path` | anti-confabulation | The pre-verifier consensus set at the same vote threshold. |
| `unverified_eval_path` | anti-confabulation | That cell's committed evaluation, where one already exists. |
| `unverified_stratum_basis` | anti-confabulation | Whether the twin's stratum was derived from its own cell or from the recipe. |
| `unverified_stratum_id` | § 6 | The twin's stratum, keyed independently; a tripwire, not a lineage check. |
| `unverified_value` | § 5 | The paired unverified cell's metric value. |
| `uplift` | § 3 | verified minus unverified on the same metric, same stratum. |
| `uplift_metric` | § 5 | Which metric the uplift column is computed on. |
| `verified` | § 2 (PV) | Boolean: a verifier stage ran. The key names the architecture, not a flag. |
| `verified_condition_id` | § 7 (registry ids) | The verified cell of a with/without-verifier pair. |
| `verified_stratum_id` | § 6 | The verified cell's own stratum, keyed from its own evidence. |
| `verified_value` | § 5 | The verified cell's metric value. |
| `verifier_crop_manifest` | anti-confabulation | The candidate manifest that measurement came from. |
| `verifier_floor_basis` | anti-confabulation | How the cell's verifier stage was matched: lineage, shell, sole, or ambiguous. |
| `verifier_min_vote_seen` | § 1 (k) | Lowest vote_count the verifier actually saw, measured from the crop manifest. |
| `verifier_variant` | § 2 (PV) | Verifier variant id from the condition's verifier_config. |

## Also worth the PI's eye: the § 6 frame table is incomplete

§ 6 names three frames (`era-1-340`, `grid-common-487`, `55maps-8541`).
`results/run-facts.json` uses four more across the registered runs:
`era-2-487`, `era-3-327`, `h13-common-338`, and `px256-1032`. The
dataset's `frame_id` column carries whichever the run records, so the
gap is visible in the data; closing it in the key would make the
vocabulary checkable rather than merely observable.

## Changelog

### 2026-08-29 — Original publication

Generated with the first build of the uplift-supplement dataset
(card `planning/uplift-supplement-2026-08-28.md`, Build order step 1).
