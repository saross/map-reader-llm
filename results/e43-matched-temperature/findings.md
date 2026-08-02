# E43 remediation R1 — matched-scope temperature evidence

> **Last revised**: 2026-08-02 (original publication). See
> [§ Changelog](#changelog) for revision history.

**Purpose**: Supplies the matched-scope evidence that Phase R1 of
`reports/e43-coverage-confound-remediation-2026-08-02.md` § 5 calls
for. The registered erratum E43 reported that T=0.7 "dramatically
outperforms" T=1.0 (ΔF1 ≈ +0.15–0.19, p ≈ 0 at all pool sizes). That
comparison scored a 240-tile T=1.0 arm against 487-tile bounds. This
document re-runs the comparison with both arms at 487 tiles and
re-verifies the independent 240-tile matched leg.

**Produced**: 2026-08-02, on sapphire, from repository commit
`7035b19db`. Zero application programming interface (API) calls — every
figure derives from on-disk detections.

**Scope of this document**: evidence only. It changes no existing
artefact; remediation of the register, the paper tables, and the
Benjamini–Hochberg (BH) families is deferred to Phases R2–R4 of the
proposal.

## 1. Headline evidence table

Δ is defined throughout as **F1(T=0.7) − F1(T=1.0)**, so a positive
value favours T=0.7 (E43's claimed direction).

| Comparison | Scope | N=5 | N=10 | N=30 | Source |
| :--- | :--- | ---: | ---: | ---: | :--- |
| **Published (group_4)** — confounded | MISMATCHED: T=0.7 at 487 tiles, T=1.0 at 240 tiles, both scored at 487 | **+0.1685**, p=0.0 | **+0.1716**, p=0.0 | **+0.1941**, p=0.0 | `results/pairwise/20m/group_4_temperature/` |
| **Matched 487-tile** (this document) | both arms 487/487 tiles | **−0.0213**, p=0.3352 (n.s.) | **−0.0335**, p=0.0815 (n.s.) | not possible (T=1.0 has 10 runs) | `results/e43-matched-temperature/n{5,10}-20m/` |
| **Matched 240-tile** (archived, 2026-03-24) | both arms 240/240 tiles | **−0.0072** (5-of-5 vs 5-of-5) | **+0.0090** (10-of-10 vs 9-of-10) | **+0.0123** at each arm's own optimum; 95 % confidence intervals (CIs) overlap | `archive/results-60-tile-validation/h11-384-consensus-flash-minimal-text-t{07,10}/` |
| **Preregistered Phase 2b** (Era 1, 340 tiles, K=3, single-pass) | matched 340 | **+0.072**, FDR-adjusted p=0.004 (text track) | — | — | `results/retest/phase2b/analysis_summary.md` |

**Reading**: at matched 487-tile scope the effect **reverses sign** and
is not statistically significant at either pool size or either spatial
buffer. At matched 240-tile scope the effect is near zero and its
direction depends on which operating point is chosen. The only
matched-scope evidence that survives significance testing is the
preregistered Phase 2b text-track contrast (+0.072), which is roughly
**one quarter** of the magnitude E43 reported and comes from a
different corpus era, tile size, and replication regime.

## 2. Arms and coverage verification

Both arms live under the same parent study directory
`outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/`.

| Arm | Path | Runs | Date | Coverage |
| :--- | :--- | ---: | :--- | :--- |
| T=0.7 | `text-t0.7/` | 30 | 2026-03-24 | 487/487 tiles in every run |
| T=1.0 | `text-t1.0/` | 10 | 2026-04-17 | 487/487 tiles in every run |

**Verification method**: each run's `*.tiles.json` sidecar was read
directly. For all 40 runs, `total_tiles == 487` and
`len(completed) == 487`. The intersection of the `completed` sets
across all 30 T=0.7 runs is 487 tiles; likewise across all 10 T=1.0
runs. The evaluation bounds file
`inputs/vectors/bounds/384/full_evaluation_bounds.geojson` contains
exactly 487 tile polygons.

Eight of the ten T=1.0 runs logged 1–3 transient tile failures (runs 1,
3, 5, 6, 7, 8, 9, 10 — chiefly `503 UNAVAILABLE` responses). **Every
one was retried successfully**: for all runs the failed-tile set is a
subset of the completed-tile set, leaving zero unresolved tiles. The
T=0.7 arm logged no failures. Coverage is therefore 487/487 on both
sides, and no coverage confound of the E43 kind exists here.

## 3. Operating points and their provenance

The project's standard selection rule is best-F1 at the 20 m buffer.
Operating points were taken from the pre-existing threshold sweeps
under `results/phase3a-text-matrix/`, one evaluation per consensus
threshold.

| Arm | N | Best threshold | Consensus GeoJSON | Features | F1@20 m | F1@30 m |
| :--- | ---: | :--- | :--- | ---: | ---: | ---: |
| T=0.7 | 5 | 5-of-5 | `text-t0.7/consensus-n5/consensus_t5.geojson` | 653 | 0.6397 | 0.6471 |
| T=1.0 | 5 | 5-of-5 | `text-t1.0/consensus-n5/consensus_t5.geojson` | 509 | 0.6610 | 0.6674 |
| T=0.7 | 10 | 10-of-10 | `text-t0.7/consensus-n10/consensus_t10.geojson` | 560 | 0.6332 | 0.6412 |
| T=1.0 | 10 | 9-of-10 | `text-t1.0/consensus/consensus_t9.geojson` | 549 | 0.6667 | 0.6728 |

All paths are relative to
`outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/`. Feature counts
were read from the GeoJSONs themselves and agree with the
`n_detections` recorded in the corresponding `evaluation.json` and with
the `voting_summary.json` threshold tallies.

**Operating-point convention**: the point was selected at the 20 m
buffer for each arm independently and then **held fixed** for the 30 m
test. The 30 m test is therefore a spatial-tolerance sensitivity check
on a 20 m-selected operating point, not an independent
re-optimisation. (Re-optimising at 30 m would in fact select the same
four thresholds — the F1-versus-threshold curves rank identically at
both buffers — so the distinction is immaterial here, but it is
recorded for transparency.)

### 3.1 First-N verification — PASSED

The preregistration (§ 3.8) requires sub-pools to be the **first N**
runs, not an arbitrary or best-of subset. Verification did not rely on
directory naming: every feature in every consensus GeoJSON carries a
`contributing_passes` property listing the runs that voted for it. The
union of `contributing_passes` across all thresholds of each pool was
computed:

| Pool | `total_passes` | Union of contributing runs |
| :--- | ---: | :--- |
| `text-t0.7/consensus-n5` | 5 | `run_1`–`run_5` (exactly) |
| `text-t0.7/consensus-n10` | 10 | `run_1`–`run_10` (exactly) |
| `text-t0.7/consensus` | 30 | `run_1`–`run_30` (exactly) |
| `text-t1.0/consensus-n5` | 5 | `run_1`–`run_5` (exactly) |
| `text-t1.0/consensus` | 10 | `run_1`–`run_10` (exactly) |

The T=0.7 sub-pools are strict first-N pools. **No re-materialisation
with `scripts/merge_passes.py` was required**; the on-disk consensus
artefacts were used as found.

### 3.2 Sanity anchors — all four reproduce

The four figures nominated in the Phase R1 brief as anchors were
reproduced exactly from the sweep `evaluation.json` files before any
new computation was trusted:

| Anchor | Expected | Observed |
| :--- | :--- | :--- |
| T=0.7, 10-of-10 | F1 0.6332, 560 detections | 0.6332, 560 |
| T=0.7, 5-of-5 | F1 0.6397, 653 detections | 0.6397, 653 |
| T=1.0, 9-of-10 | F1 0.6667, 549 detections | 0.6667, 549 |
| T=1.0, 5-of-5 | F1 0.6610, 509 detections | 0.6610, 509 |

The permutation runs independently re-derived the same four F1 values
from the GeoJSONs, so the sweep files and the new tests agree to four
decimal places.

## 4. Paired permutation tests (new)

Four tests, `--mode geojson`, 10,000 permutations, seed 42, bounds
`inputs/vectors/bounds/384/full_evaluation_bounds.geojson`, ground
truth `inputs/vectors/references/mounds-reference.geojson` (the
`configs/pairwise-comparisons.yaml` defaults, set explicitly).
Condition A is always T=0.7, condition B always T=1.0.

| Test | Buffer | F1 (A) | F1 (B) | ΔF1 | p | Wins/losses/ties | Null 95 % CI |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- | :--- |
| N=5 | 20 m | 0.6397 | 0.6610 | **−0.0213** | 0.3352 | 37/27/423 | [−0.0444, +0.0436] |
| N=5 | 30 m | 0.6471 | 0.6674 | **−0.0203** | 0.3577 | 37/25/425 | [−0.0440, +0.0437] |
| N=10 | 20 m | 0.6332 | 0.6667 | **−0.0335** | 0.0815 | 23/35/429 | [−0.0372, +0.0372] |
| N=10 | 30 m | 0.6412 | 0.6728 | **−0.0316** | 0.0963 | 24/34/429 | [−0.0369, +0.0370] |

All four tests use n_tiles = 487. Confusion counts (20 m buffer):

| Test | A: TP/FP/FN | B: TP/FP/FN |
| :--- | :--- | :--- |
| N=5 | 348/305/87 | 312/197/123 |
| N=10 | 315/245/120 | 328/221/107 |

TP + FN = 435 in every cell, confirming both arms are scored against
the same 435 in-bounds ground-truth mounds — the arithmetic that failed
in the published group_4 tests, where the T=1.0 arm could reach at most
242 of those 435.

**Interpretation**: none of the four tests is significant at α = 0.05.
All four point estimates favour **T=1.0**, by 0.02–0.03 F1. The N=10
tests sit just outside significance (p ≈ 0.08–0.10), so the honest
summary is "no reliable difference, with a weak hint against E43's
direction" — not "T=1.0 is better".

**Detection-count asymmetry worth noting**: at N=5 the two arms are
matched on operating point (5-of-5) but not on volume — T=0.7 emits 653
consensus detections to T=1.0's 509, buying 36 extra true positives for
108 extra false positives. At N=10 the arms are near-matched on volume
(560 versus 549) and T=1.0 wins on both precision and recall.

### 4.1 What the published group_4 tests reported

For reference, the confounded tests that these supersede
(`results/pairwise/{20m,30m}/group_4_temperature/`, run 2026-03-28):

| N | Buffer | F1 (T=0.7) | F1 (T=1.0, 240-tile arm) | ΔF1 | p |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 5 | 20 m | 0.6397 (5-of-5) | 0.4712 (5-of-5) | +0.1685 | 0.0 |
| 10 | 20 m | 0.6332 (10-of-10) | 0.4615 (9-of-10) | +0.1716 | 0.0 |
| 30 | 20 m | 0.6611 (29-of-30) | 0.4670 (22-of-30) | +0.1941 | 0.0 |
| 5 | 30 m | 0.6471 (5-of-5) | 0.4795 (5-of-5) | +0.1676 | 0.0001 |
| 10 | 30 m | 0.6412 (10-of-10) | 0.4695 (9-of-10) | +0.1717 | 0.0 |
| 30 | 30 m | 0.6694 (29-of-30) | 0.4768 (22-of-30) | +0.1927 | 0.0 |

The T=0.7 side of those tests is identical to the T=0.7 side here (same
study, same operating points). The entire ΔF1 shift of ~0.19 comes from
replacing the 240-tile T=1.0 arm
(`outputs/h11/consensus-384-UNINTENDED-T1.0`) with the matched 487-tile
one (`.../flash-minimal-text-n30-t07/text-t1.0`).

## 5. The 240-tile matched leg — read-back verification

The two archived consensus-analysis reports dated 2026-03-24 were
re-read and their headline figures confirmed. Both used
`inputs/vectors/bounds/384/validation_bounds.geojson` (240 tiles),
buffer 20 m, 1,000 bootstrap iterations, seed 42, and both record
`pool_selection: "first-N (preregistration Section 3.8)"`.

| Arm | Report | Global optimum | F1 | 95 % CI |
| :--- | :--- | :--- | ---: | :--- |
| T=0.7 | `h11-384-consensus-flash-minimal-text-t07/consensus-analysis-report.json` | 29-of-30 | **0.6566** | [0.5887, 0.7166] |
| T=1.0 | `h11-384-consensus-flash-minimal-text-t10/consensus-analysis-report.json` | 5-of-5 | **0.6443** | [0.5680, 0.7117] |

Both under `archive/results-60-tile-validation/`. The expected values
(≈0.6566 and ≈0.6443) read back exactly. ΔF1 at each arm's own optimum
is **+0.0123**, with CIs overlapping across almost their whole width.

Matched-N rows from the same two reports (a stricter comparison than
global-optimum versus global-optimum):

| Operating point | T=0.7 F1 [CI] | T=1.0 F1 [CI] | ΔF1 |
| :--- | :--- | :--- | ---: |
| 5-of-5 | 0.6371 [0.5646, 0.7030] | 0.6443 [0.5680, 0.7117] | **−0.0072** |
| 10-of-10 vs 9-of-10 | 0.6329 [0.5622, 0.6940] | 0.6239 [0.5487, 0.6924] | **+0.0090** |
| 29-of-30 | 0.6566 [0.5887, 0.7166] | 0.6173 [0.5504, 0.6792] | **+0.0393** |

Note the archived T=1.0 report's `study_dir` is
`outputs/h11/consensus-384` — the 240-tile study since renamed
`consensus-384-UNINTENDED-T1.0`, and the same data the confounded
group_4 tests drew on. The difference between this leg and group_4 is
purely the evaluation bounds.

This leg is a **restore, not a recomputation**: no new analysis was run
against the 240-tile bounds.

## 6. Coverage quantification — and a correction to the proposal

Ground-truth mounds within each bounds set, computed two independent
ways (point-in-polygon against the dissolved bounds, and a per-tile
spatial join with an `intersects` predicate; both agree exactly):

| Quantity | Value |
| :--- | ---: |
| Mounds in the reference file | 569 |
| Mounds within the 487-tile bounds | 435 |
| Mounds within the 240-tile bounds | 242 |
| Mounds in the 487-tile scope but outside the 240 tiles | **193** (44.37 %) |
| Recall ceiling for a 240-tile arm scored at 487 | **0.5563** |

The 240 tiles are a strict subset of the 487 (zero tile names in the
240 set are absent from the 487 set).

**Correction to the proposal.** The remediation proposal § 1 states
that the mis-scoped evaluation counted "221 of 435 ground-truth mounds
(50.8 %)" as automatic false negatives. The correct figure is **193
(44.37 %)**. The proposal's own recall-ceiling figure (0.556) is
consistent with 242 covered mounds — that is, with 193 missing, not 221
— so § 1 is internally inconsistent and 193 is the coherent value.

Two independent corroborations of 242:

- The archived 240-tile T=1.0 report gives recall 0.7231 at 9-of-10;
  0.7231 × 242 ≈ 175 true positives.
- The confounded group_4 N=10 test records TP = 174 for that same
  condition at 487-tile scope, with FN = 261. Subtracting the
  within-240 false negatives (242 − 175 = 67) leaves 194 automatic
  false negatives from uncovered tiles — matching 193 to within the
  one-mound boundary tolerance between the two matching routines.

The mechanism the E43 remediation should record is therefore: **193
mounds (44 % of the in-bounds ground truth) lay in the 247 tiles the
T=1.0 arm never saw, and were charged to it as false negatives**,
capping its achievable recall at 0.5563.

## 7. Configuration parity between the arms

Every one of the 40 run metadata files was checked. The two
experiment-defining hashes are identical across all 40:

| Field | Value | Distinct values across 40 runs |
| :--- | :--- | ---: |
| `configuration.system_instruction_hash` | `e169b7237b853eeaad990fc2e54fbd7214afb435d85c8e444a4a784432200e12` | 1 |
| `configuration.library_hash` | `8580ecb2258b64a0fdbcee707714bc9dd8f8e698a29d304e3980dac18a831cb4` | 1 |

Also matched: `version: detect_brief-text`, `instruction_file:
detect_brief-text.md`, `max_output_tokens: 8192`, `thinking_level:
minimal`, `include_example_images: false`, `example_count: 17`, and the
`full_config_snapshot` hypothesis and ordering fields. The only
intended difference is `temperature` (0.7 versus 1.0).

## 8. Caveats

1. **N=30 cannot be matched at 487 tiles.** The 487-tile T=1.0 arm has
   10 runs; the T=0.7 arm has 30. The N=30 comparison exists only at
   240-tile scope (§ 5, ΔF1 +0.0393 at 29-of-30 — the largest
   matched-scope gap found anywhere, but on half the corpus and with
   wide overlapping CIs). No matched 487-tile N=30 claim can be made
   without ~20 further T=1.0 runs.

2. **The arms are 24 days apart.** T=0.7 ran 2026-03-24; T=1.0 ran
   2026-04-17. Configuration hashes are identical (§ 7), but a
   provider-side model update inside that window cannot be excluded
   from on-disk evidence.

3. **The arms used different execution paths.** T=0.7 was collected via
   the asynchronous Batch API (`lib_batch_api.py` v1.5.0, repository
   commit `2126c3efaf758589a7ffa72f75462680d35b0c8c`); T=1.0 via the
   real-time governed path (`4_detect_mounds_batch.py` v6.0.0,
   commit `b57cf6c22bd58325b554a3e64abfc629a7063914`). Relatedly,
   `configuration.model` records `gemini-3-flash` for T=0.7 and
   `gemini-3-flash-preview` for T=1.0, while
   `full_config_snapshot.model` is `gemini-3-flash` in both and
   `cost_estimate.pricing_used.model` is `gemini-3-flash-preview` in
   both — that is, the requested model is identical and the two scripts
   record the resolved alias differently. This is a metadata-recording
   difference rather than a demonstrated model difference, but it is a
   real uncontrolled variable and should be stated as such.

4. **Operating points are selected, not preregistered.** Best-F1@20 m
   per arm is the project's standard rule, but selecting a threshold on
   the same data used for the test inflates both arms' F1 equally; it
   is not a per-arm bias. It does mean the reported F1 values are
   optimistic in absolute terms.

5. **Consensus GeoJSONs lack a singular `source_tile` property**, so
   `pairwise_permutation_test.py` assigned tiles by spatial join
   (100 % assignment: 653/653, 509/509, 560/560, 549/549). Both arms
   were processed identically, so this cannot bias the contrast.

6. **The Phase 2b row is track-specific.** The +0.072 / FDR p=0.004
   figure is the **text** track, which matches the modality of the arms
   compared here. The image track of the same preregistered experiment
   gives T=0.7 versus T=1.0 = +0.014, non-significant
   (`results/retest/phase2b/analysis_summary.md`, "Track 1 —
   FDR-significant pairwise contrasts", non-significant list). Phase 2b
   supports "T=1.0 is a poor default" more strongly than it supports
   "T=0.7 specifically beats T=1.0".

7. **This document does not re-run the BH families.** The four new
   tests are reported with raw p-values and are not members of any
   corrected family. Recomputing the four affected BH families is a
   Phase R3 decision.

## 9. Reproduction

Run from the repository root on sapphire with the project virtual
environment. Paths are abbreviated with
`S=outputs/h11/pv-diag-384/flash-minimal-text-n30-t07`.

```bash
.venv/bin/python scripts/pairwise_permutation_test.py \
    --mode geojson \
    --geojson-a $S/text-t0.7/consensus-n5/consensus_t5.geojson \
    --geojson-b $S/text-t1.0/consensus-n5/consensus_t5.geojson \
    --label-a "Flash MIN text T=0.7 5-of-5 (487-tile, first-5)" \
    --label-b "Flash MIN text T=1.0 5-of-5 (487-tile, first-5)" \
    --bounds inputs/vectors/bounds/384/full_evaluation_bounds.geojson \
    --ground-truth inputs/vectors/references/mounds-reference.geojson \
    --buffer-metres 20 --n-permutations 10000 --seed 42 \
    --output-dir results/e43-matched-temperature/n5-20m
```

The N=10 tests substitute
`$S/text-t0.7/consensus-n10/consensus_t10.geojson` and
`$S/text-t1.0/consensus/consensus_t9.geojson`; the 30 m tests
substitute `--buffer-metres 30` and the `-30m` output directory. Each
test takes under two seconds.

Per-test artefacts, each with full per-tile F1 breakdowns:

- `n5-20m/pairwise_permutation_result.json`
- `n5-30m/pairwise_permutation_result.json`
- `n10-20m/pairwise_permutation_result.json`
- `n10-30m/pairwise_permutation_result.json`

## 10. Implications for Phases R2–R4

- E43's impact row and its "~+0.15 at all pool sizes" direction are not
  supported at matched scope and should be superseded (Phase R2).
- The corrected coverage mechanism to record is **193/435 mounds
  (44.37 %) charged as automatic false negatives; recall ceiling
  0.5563** — not 221/435 (§ 6).
- Paper tables and leaderboards carrying the confounded T=1.0
  comparator (group_4, group_12, the 141 group_8 files) can point at
  this document for the matched figures (Phase R3).
- Any new Obs correcting Obs 190 should state the reversal honestly:
  the matched effect is **negative and non-significant** at 487 tiles,
  not merely "smaller than reported" (Phase R4).

## Changelog

### 2026-08-02 — Original publication

Phase R1 of `reports/e43-coverage-confound-remediation-2026-08-02.md`.
Four new paired permutation tests at matched 487-tile scope (N=5 and
N=10 × 20 m and 30 m buffers), first-N provenance verification of the
T=0.7 sub-pools, coverage verification of both arms (487/487),
read-back of the two archived 240-tile reports, and configuration-parity
checks. Also records one correction to the proposal document: the
automatic false-negative count is 193, not 221 (§ 6). Trigger: the E43
coverage-confound investigation of the same date. Nothing outside
`results/e43-matched-temperature/` was modified.
