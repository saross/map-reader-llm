# E43 remediation R1 — matched-scope temperature evidence

> **Last revised**: 2026-08-03 (E72 follow-up, second pass: cost-equivalent
> configuration tests — T=1.0/N=5 against T=0.7/N=10 and N=30, six paired
> tests, all non-significant; see
> [§ 13](#13-cost-equivalent-configurations--e72-follow-up-2026-08-03).
> Earlier the same day: the unpaired-MCC caveat of § 11.2 discharged with
> nine paired ΔMCC permutation tests and situated against the four-rung
> temperature ladder, see
> [§ 12](#12-paired-mcc-and-the-temperature-ladder--e72-follow-up-2026-08-03)).
> See [§ Changelog](#changelog) for revision history.

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

These four cells were subsequently scored at the project's full house
grain — the 14 uniform buffers plus tile-level MCC — and registered in
the manifest; see
[§ 11](#11-house-grain-filing--14-buffers-tile-level-mcc-and-manifest-registration).

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

## 11. House-grain filing — 14 buffers, tile-level MCC, and manifest registration

Sections 1–10 report F1 only. The project's standing rule is that
tile-level Matthews Correlation Coefficient (MCC) is reported
**alongside** F1 wherever the inputs support it, and that an F1-only
table is an omission to fix rather than a defensible choice. This
section closes that gap for the four matched operating points and
discharges item 3 of erratum E72 ("the matched cells filed as their own
first-class analysis, 14-buffer + MCC, manifest-registered").

### 11.1 The four cells at the full house grain

Each cell was re-scored through the standard harness
(`scripts/rescore_conditions.py` → `scripts/evaluate_detections.py`) at
the 14 uniform buffers (5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100,
125, 150 m) with `--mcc`, bias-corrected and accelerated (BCa) bootstrap
of 10,000 iterations, seed 42, against the same 487-tile bounds and
curator ground truth used throughout this document. Zero API calls.

| Arm | N | Threshold | Detections | F1@20 m | F1@30 m | MCC | MCC 95 % CI | Sens. | Spec. | TP / TN / FP / FN |
| :--- | ---: | :--- | ---: | ---: | ---: | ---: | :--- | ---: | ---: | :--- |
| T=0.7 | 5 | 5-of-5 | 653 | 0.6397 | 0.6471 | **0.3148** | [0.2962, 0.3310] | 0.8603 | 0.4264 | 197 / 110 / 148 / 32 |
| T=1.0 | 5 | 5-of-5 | 509 | 0.6610 | 0.6674 | **0.4065** | [0.3881, 0.4237] | 0.8035 | 0.5969 | 184 / 154 / 104 / 45 |
| T=0.7 | 10 | 10-of-10 | 560 | 0.6332 | 0.6412 | **0.3655** | [0.3483, 0.3817] | 0.8341 | 0.5155 | 191 / 133 / 125 / 38 |
| T=1.0 | 10 | 9-of-10 | 549 | 0.6667 | 0.6728 | **0.4153** | [0.3962, 0.4316] | 0.8341 | 0.5698 | 191 / 147 / 111 / 38 |

Confusion counts are tile-level and sum to 487 in every row (229
mound-bearing tiles, 258 empty tiles), confirming both arms are scored
over the same tile universe.

A note on the coverage provenance these files record, since E72 is a
coverage erratum. The evaluations were produced under the hardened
coverage guard (commit `672836a00`), which counts unprocessed tiles
directly from a detection GeoJSON's top-level `processed_tiles` array
instead of inferring coverage from the zero-detection fraction. Consensus
artefacts are written by the aggregation path and do not preserve that
array, so all four cells record
`coverage_source: "zero_fraction_heuristic"` with
`n_unprocessed_tiles: null` and `coverage_status: "normal"`. The
heuristic is not what establishes coverage here: § 2 verifies 487/487
tiles in all 40 runs directly from the per-run `*.tiles.json` sidecars,
which is the stronger evidence and does not depend on the guard.

### 11.2 MCC separates the arms more sharply than F1 — flagged

| Pool | ΔF1@20 m | ΔMCC | MCC intervals | Paired p (§ 12) |
| :--- | ---: | ---: | :--- | ---: |
| N=5 | −0.0213 (p = 0.335, n.s.) | **−0.0917** | [0.2962, 0.3310] vs [0.3881, 0.4237] — **disjoint** | 0.0255 |
| N=10 | −0.0335 (p = 0.082, n.s.) | **−0.0498** | [0.3483, 0.3817] vs [0.3962, 0.4316] — **disjoint** | **0.2114** |

Δ keeps this document's convention: T=0.7 minus T=1.0, so a negative
value favours T=1.0.

> **Read this section against [§ 12](#12-paired-mcc-and-the-temperature-ladder--e72-follow-up-2026-08-03).**
> The paired tests commissioned as the E72 follow-up were run on
> 2026-08-03 and they do not ratify the disjoint-interval reading at
> N=10: the same contrast that shows non-overlapping BCa intervals
> returns p = 0.2114 when the tiles are properly paired. The direction
> below stands; the strength claimed for it at N=10 does not.

**This is worth flagging.** On F1 the matched contrast is a null result
(§ 4). On tile-level MCC the same four cells separate cleanly in
T=1.0's favour, with non-overlapping BCa 95 % intervals at both pool
sizes and an effect four times the F1 gap at N=5. The metric, not the
data, is doing the work: F1 is computed over detections and rewards the
T=0.7 arm's extra recall, whereas MCC is computed over tiles and
charges it for the false-positive tiles that recall costs. The N=10
pair makes the mechanism visible — both arms classify **exactly** the
same mound-bearing tiles (TP 191, FN 38, sensitivity 0.8341 in both),
so the entire MCC gap comes from specificity: T=0.7 raises 125
false-positive tiles to T=1.0's 111.

Two caveats bound this, and neither is dismissible:

1. **The MCC comparison is unpaired.** The intervals are per-condition
   BCa bootstraps, not a paired test on matched tiles. They are not a
   p-value. ~~Non-overlapping intervals are suggestive and, for a paired
   design, conservative~~ — **that expectation was wrong here**, and
   § 12.3 shows why: the two per-condition bootstraps resample tiles
   within one arm, where MCC is stable, whereas the paired null swaps
   arm labels on the 109 (N=5) and 96 (N=10) tiles the arms actually
   classify differently, which is a much noisier quantity. The paired
   test is the
   less significant of the two at N=10, not the more. No paired MCC
   permutation test had been run **at the time of writing**; the kernel
   in fact existed (`pairwise_permutation_test.run_permutation_test_mcc`,
   commit `62d1173af`) but was not exposed on any command line, which is
   how it was missed. It is now — see § 12.
2. **The operating points were selected on F1@20 m** (§ 3, § 8 caveat
   4). Selecting on one metric and reporting another is a known way to
   flatter the metric you did not select on. Both arms were selected by
   the same rule, so this is not a per-arm bias, but the MCC values are
   read off F1-selected thresholds and would move under MCC-optimal
   selection.

What survives both caveats: **nothing in this analysis supports E43's
direction.** F1 says "no reliable difference"; MCC points at T=1.0 —
significantly so at N=5 (paired p = 0.0255) but not at N=10 (paired
p = 0.2114), so "and clearly" overstates the adjacent-rung contrast and
§ 12.5 restates it properly. The published +0.168 to +0.194 claim has no
support at matched scope on either metric.

### 11.3 Buffer saturation

F1 plateaus by 30–35 m in all four cells and is then flat to 150 m (for
example, T=0.7 5-of-5 holds 0.6471 from 30 m through 150 m). The
extended tail therefore adds no discrimination on this 4-map corpus —
unlike the 55-map corpus, where the 50 m headline is load-bearing. The
20 m headline used throughout §§ 1–10 sits below the plateau and remains
the discriminating operating point.

### 11.4 Manifest registration — and why no new conditions were minted

The four cells are registered in
`results/analyses-manifest.json` as the analysis
**`e43-matched-temperature`** (type `comparison`, `preregistered:
exploratory`, `hypothesis_refs: ["H7"]`, `deviations: ["E43", "E72"]`,
`output_path` this document). Its `conditions_compared` are the four
**already-registered** `pv-diag-384` conditions:

| Cell | Condition id (`results/conditions-manifest.json`) |
| :--- | :--- |
| T=0.7, N=5, 5-of-5 | `pv-diag-384::flash-minimal-text-n30-t07-text-t0.7-consensus-n5-5of5` |
| T=1.0, N=5, 5-of-5 | `pv-diag-384::flash-minimal-text-n30-t07-text-t1.0-consensus-n5-5of5` |
| T=0.7, N=10, 10-of-10 | `pv-diag-384::flash-minimal-text-n30-t07-text-t0.7-consensus-n10-10of10` |
| T=1.0, N=10, 9-of-10 | `pv-diag-384::flash-minimal-text-n30-t07-text-t1.0-consensus-9of10` |

**No parallel `matched-temp-*` conditions were minted.** All four
operating points were already first-class conditions, scored at this
identical grain on 2026-06-05 under
`results/rescore-2026-06-05/pv-diag-384/consensus-sweep/`; the re-score
above reproduces their F1@20 m and MCC to within 1e-9 (an exact
reproduction under the current scripts, gate 5 of
`scripts/author_e43_matched_temperature.py`). Minting duplicate labels
for the same GeoJSONs and the same metrics would double-count them in
every board built from the conditions manifest. The house precedent is
explicit: `scripts/author_sweep_promotions.py` declined to promote
completeness-sweep cell #1 because "promotion would duplicate" the
registered headline. What was genuinely missing was the **analysis**
row, and that is what this filing adds.

The four re-scored `evaluation.json` files are waived into
`pv-diag-384`'s `_ignored_evals` — the designed home for deliberate
exclusions — so `scripts/verify_run_conditions.py` keeps flagging any
genuinely unclaimed evaluation.

Manifest counts, before → after: runs 31 → 31, conditions 322 → 322,
passes 1132 → 1132, **analyses 20 → 21**; `ALL VALID`, registry↔facts
drift 0.

### 11.5 Reproduction

```bash
# 1. the four house-grain evaluations (~25 s at 4 workers on sapphire)
.venv/bin/python scripts/rescore_conditions.py \
    --worklist planning/rescore-worklists/e43-matched-temperature-2026-08-02.json \
    --workers 4 --execute

# 2. the registration (dry-run by default; gates refuse to write on failure)
.venv/bin/python scripts/author_e43_matched_temperature.py --execute
.venv/bin/python scripts/generate_post_run_report.py --all --write
.venv/bin/python scripts/verify_run_conditions.py --run pv-diag-384
```

Per-cell artefacts, each carrying all 14 buffers with BCa intervals plus
the tile-classification block:

- `paper-eval/t07-n5-5of5/evaluation.json`
- `paper-eval/t10-n5-5of5/evaluation.json`
- `paper-eval/t07-n10-10of10/evaluation.json`
- `paper-eval/t10-n10-9of10/evaluation.json`

## 12. Paired MCC and the temperature ladder — E72 follow-up (2026-08-03)

§ 11.2 flagged that tile-level MCC separates the matched arms in T=1.0's
favour, and bounded the claim with two caveats: the comparison was
unpaired, and the operating points had been selected on F1. The principal
investigator (PI) commissioned this follow-up to (1) make the MCC
comparison properly paired and (2) situate it against the full
temperature ladder, so that the question it raises — *is this an
exception to the project's lower-temperature-is-better pattern?* — gets a
direct answer.

**Produced**: 2026-08-03, on sapphire, from repository commit
`7356f21fa`. Zero API calls; every figure derives from on-disk
detections and from evaluations already filed in this repository.

### 12.1 The machinery, and one correction to § 11.2

§ 11.2 recorded that "no paired MCC permutation test was run;
`scripts/pairwise_permutation_test.py` tests F1". The first half is
right, the second is not. That script carries **two** permutation
kernels: `run_permutation_test` (F1) and `run_permutation_test_mcc`,
added 2026-04-25 in commit `62d1173af` and in production use by
`build_tiered_leaderboard.py` and `build_cross_architecture_tables.py`.
The MCC kernel implements exactly the commissioned test — per tile, the
full (TP, TN, FP, FN) one-hot 4-tuple is swapped between arms with
probability 0.5, the aggregate MCC is recomputed, and the two-sided
p-value is the fraction of permutations whose |ΔMCC| reaches the
observed |ΔMCC|. It was invisible because it is not reachable from any
command line: the script's own command-line interface (CLI) runs the F1
sibling only.

The new `scripts/paired_mcc_permutation.py` therefore does **not**
reimplement the statistics — duplicating a tested kernel for a house
metric is how two implementations drift apart. It supplies what was
missing around it: a CLI, batch execution over a job file, and a hard
per-arm validation gate.

**The gate.** Per-tile labels come from `lib_advanced_metrics`'s own
`compute_per_tile_classification`, so they cannot diverge from the house
definition by construction. The gate then proves it end to end: the
labels are aggregated and checked against the TP/TN/FP/FN cells, the MCC
point estimate, and the detection count **recorded** in one or more
on-disk `evaluation.json` files for that same cell. Any disagreement
raises `ConfusionGateError` and the pair is not tested. All 18 arm-gates
in this section passed, 10 of them against two independent references
apiece (the § 11.1 house-grain evaluation and the `phase3a-text-matrix`
sweep evaluation, which agree exactly).

### 12.2 Tile-level MCC is buffer-invariant — one Δ, not two

The commission asked for tile classification "at 20 m and 30 m buffers".
Those are the same number, and it is worth saying why rather than
reporting a value twice.

House tile classification asks two questions per tile — does the tile
intersect any ground-truth mound, and did the arm emit any detection
assigned to that tile? Neither involves a spatial matching tolerance
(`lib_advanced_metrics.calculate_tile_classification`). Tile-level MCC
is therefore **invariant to the F1 buffer**, and this is a structural
property of the metric, not a coincidence of these data. It is pinned by
a tier-1 test (`test_delta_is_invariant_to_ground_truth_buffering`) and
noted in the kernel's own docstring. Every ΔMCC below holds identically
at 20 m and 30 m. F1, which does use the buffer, is reported at both.

### 12.3 Paired ΔMCC — the commissioned tests and the ladder

487 tiles, 10,000 permutations, seed 42, bounds
`inputs/vectors/bounds/384/full_evaluation_bounds.geojson`, ground truth
`inputs/vectors/references/mounds-reference.geojson`. Δ = MCC(lower T) −
MCC(higher T), so **a negative Δ favours the higher temperature** — the
same sign convention as the rest of this document.

| # | Contrast | Pool | ΔMCC | Paired p | Discordant tiles (lower-T only / higher-T only) | McNemar exact p |
| :--- | :--- | :--- | ---: | ---: | :--- | ---: |
| 1 | T=0.7 vs T=1.0 | N=5 | **−0.0918** | **0.0255** | 109 (39 / 70) | 0.0039 |
| 2 | T=0.7 vs T=1.0 | N=10 | −0.0498 | 0.2114 | 96 (41 / 55) | 0.1843 |
| 3 | T=0.3 vs T=0.7 | N=5 | −0.0401 | 0.3267 | 93 (41 / 52) | 0.2997 |
| 4 | T=0.3 vs T=0.7 | N=10 | −0.0526 | 0.1668 | 91 (37 / 54) | 0.0929 |
| 5 | T=0.3 vs T=1.0 | N=5 | **−0.1319** | **0.0005** | 96 (27 / 69) | < 0.0001 |
| 6 | T=0.3 vs T=1.0 | N=10 | **−0.1023** | **0.0023** | 77 (23 / 54) | 0.0005 |
| 7 | T=0.0 vs T=0.3 | N=3 vs 10 † | −0.0895 | 0.0060 | 58 (14 / 44) | 0.0001 |
| 8 | T=0.0 vs T=0.7 | N=3 vs 10 † | −0.1421 | 0.0008 | 113 (33 / 80) | < 0.0001 |
| 9 | T=0.0 vs T=1.0 | N=3 vs 10 † | −0.1918 | < 0.0001 | 103 (21 / 82) | < 0.0001 |

† Pool-depth confounded — see § 12.6. Tests 1 and 2 are the two the PI
commissioned; 3–6 complete the pool-matched ladder; 7–9 are descriptive
only.

**Every one of the nine point estimates is negative.** Not one rung of
the ladder favours the lower temperature on tile-level MCC.

**Independent cross-check.** The rightmost column is an exact McNemar
test on the discordant tiles — a different statistic (tile-classification
accuracy, ignoring which cell the tile moved between) computed by a
different route (`scipy.stats.binomtest`). It agrees with the
permutation test on the α = 0.05 verdict in all nine rows. The
permutation p is uniformly the larger of the two, which is expected: it
tests ΔMCC, which additionally depends on *how* the discordance
distributes across mound-bearing and empty tiles, so it spends power the
sign test does not.

**Why the paired p can exceed what disjoint intervals suggest.** The
per-condition BCa intervals of § 11.1 are narrow (half-widths ≈ 0.017)
because resampling tiles within a single arm barely moves that arm's
MCC. The paired null is much wider (standard deviation 0.0327–0.0427)
because swapping arm labels on the 58–113 discordant tiles moves *both*
aggregate tables at once. § 11.2's expectation that non-overlapping
intervals would be "for a paired design, conservative" was therefore
backwards, and is corrected in place.

**Multiplicity.** Following § 8 caveat 7, these are raw p-values and are
not members of any registered Benjamini–Hochberg (BH) family. For
readers who would form one, BH across the six pool-matched tests (1–6)
gives: test 5 q = 0.0030 and test 6 q = 0.0069 (both significant), test 1
q = 0.0510 (marginal), tests 2, 3, 4 q = 0.2537, 0.3267, 0.2502. **Only
the T=0.3-versus-T=1.0 contrast survives correction.**

### 12.4 The temperature ladder — F1 and MCC side by side

All four arms live under the same parent study,
`outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/`. Each arm's
operating point is its own best-F1@20 m cell in the pre-existing
threshold sweep under `results/phase3a-text-matrix/`.

| T | N | Threshold | Detections | F1@20 m | F1@30 m | MCC | MCC 95 % CI | Sens. | Spec. | TP / TN / FP / FN |
| :--- | ---: | :--- | ---: | ---: | ---: | ---: | :--- | ---: | ---: | :--- |
| 0.0 † | 3 | 3-of-3 | 799 | 0.5932 | 0.5981 | 0.2235 | [0.2063, 0.2403] | 0.9039 | 0.2713 | 207 / 70 / 188 / 22 |
| 0.3 | 5 | 5-of-5 | 659 | 0.6307 | 0.6362 | 0.2746 | [0.2565, 0.2930] | 0.8603 | 0.3837 | 197 / 99 / 159 / 32 |
| 0.7 | 5 | 5-of-5 | 653 | 0.6397 | 0.6471 | 0.3148 | [0.2962, 0.3310] | 0.8603 | 0.4264 | 197 / 110 / 148 / 32 |
| 1.0 | 5 | 5-of-5 | 509 | **0.6610** | **0.6674** | **0.4065** | [0.3881, 0.4237] | 0.8035 | 0.5969 | 184 / 154 / 104 / 45 |
| 0.3 | 10 | 10-of-10 | 608 | 0.6424 | 0.6481 | 0.3129 | [0.2956, 0.3301] | 0.8559 | 0.4302 | 196 / 111 / 147 / 33 |
| 0.7 | 10 | 10-of-10 | 560 | 0.6332 | 0.6412 | 0.3655 | [0.3483, 0.3817] | 0.8341 | 0.5155 | 191 / 133 / 125 / 38 |
| 1.0 | 10 | 9-of-10 | 549 | **0.6667** | **0.6728** | **0.4153** | [0.3962, 0.4316] | 0.8341 | 0.5698 | 191 / 147 / 111 / 38 |

† T=0.0 has only three runs; its row is descriptive (§ 12.6).

Every row sums to 487 tiles (229 mound-bearing, 258 empty). Coverage was
verified directly from the per-run `*.tiles.json` sidecars for all
**53** runs across the four arms (3 + 10 + 30 + 10): `total_tiles == 487`
and `len(completed) == 487` in every one, every logged tile failure
retried successfully, and the intersection of completed tiles across each
arm is the full 487. No arm in this ladder carries an E72-style coverage
defect. Configuration parity also holds across all 53 runs — one distinct
`system_instruction_hash` (`e169b7237b…`) and one distinct `library_hash`
(`8580ecb225…`), with `thinking_level: minimal` and
`version: detect_brief-text` throughout; temperature is the only intended
difference. Every pool is a strict first-N pool, verified from the union
of `contributing_passes` across each pool's thresholds rather than from
directory naming (preregistration § 3.8).

**Paired F1 tests for the ladder rungs** (the two T=0.7-versus-T=1.0 rows
are from § 4; the two T=0.3 rows are new, same harness and settings):

| Contrast | Pool | ΔF1@20 m | p | ΔF1@30 m | p |
| :--- | :--- | ---: | ---: | ---: | ---: |
| T=0.3 vs T=0.7 | N=10 | +0.0092 | 0.5950 | +0.0069 | 0.6907 |
| T=0.3 vs T=1.0 | N=10 | −0.0243 | 0.0624 | −0.0246 | 0.0563 |
| T=0.7 vs T=1.0 | N=10 | −0.0335 | 0.0815 | −0.0316 | 0.0963 |
| T=0.7 vs T=1.0 | N=5 | −0.0213 | 0.3352 | −0.0203 | 0.3577 |

**On F1 the entire ladder is a null result** — not one contrast reaches
α = 0.05 at either buffer. The one positive sign in the table (T=0.3 over
T=0.7, +0.0092) matches the direction of the 55-map deployment result
but is nowhere near significance on this corpus.

### 12.5 Does the T=1.0 MCC advantage survive pairing?

**Yes in direction, partly in strength, and not where § 11.2 put the
weight.**

- **Direction: survives completely.** All nine paired contrasts favour
  the higher temperature, and the MCC ladder is strictly monotonic
  increasing in temperature at both pool sizes (N=5: 0.2746 → 0.3148 →
  0.4065; N=10: 0.3129 → 0.3655 → 0.4153; with T=0.0 at 0.2235 below
  both). Nothing in the paired analysis rescues E43's direction.
- **Strength: survives only end to end.** The contrast § 11.2 headlined —
  T=0.7 versus T=1.0, the adjacent rung — is significant at N=5
  (p = 0.0255) but **not** at N=10 (p = 0.2114), and does not survive BH
  correction at either. What does survive, comfortably and at both pool
  sizes, is the **end-to-end** T=0.3-versus-T=1.0 contrast (ΔMCC −0.1319
  p = 0.0005 at N=5; −0.1023 p = 0.0023 at N=10; BH q = 0.0030 and
  0.0069).
- **A methodological correction falls out of this.** § 11.2 reported
  disjoint BCa intervals at *both* pool sizes and read them as
  conservative for a paired design. Pairing does not ratify that at
  N=10. Non-overlapping per-condition bootstrap intervals were the
  weaker evidence here, not the stronger, and the reason is structural
  (§ 12.3), so the lesson generalises beyond this table: in this
  codebase, disjoint per-condition MCC intervals are not a substitute
  for a paired MCC test.

There is also a **cleanliness dividend** the commission did not
anticipate. § 8 caveats 2 and 3 note that the T=0.7 and T=1.0 arms ran 24
days apart by different execution paths — T=0.7 on 2026-03-24 via the
asynchronous Batch API, T=1.0 on 2026-04-17 via the governed real-time
path. Checking the run metadata for the other two arms shows that
**T=0.0, T=0.3, and T=1.0 all ran on 2026-04-17 through the same governed
real-time path** (their run metadata carries a `tpm_governor` block;
T=0.7's carries `batch_api` instead). The T=0.3-versus-T=1.0 contrast is
therefore free of the date and execution-path confound that dogs every
T=0.7 comparison in this document — and it is precisely the contrast that
is significant. The confound cannot explain the result away; if anything,
the cleanest contrast in the ladder is the strongest one.

### 12.6 Does the ladder contradict the lower-temperature-is-better pattern?

**No. It refines it, and the MCC result is not an exception at all — it
is a replication.**

The project already holds a registered finding that says exactly this,
in a different study family. **Observation 274** (2026-04-23,
`docs/notes/working-notes.md`) reports that tile-level MCC in the
**preregistered Phase 2b H7 temperature sweep** "increases monotonically
with T", is "near-worst at T=0.0 and near-best at T=1.3, in both image
and text tracks", and is "orthogonal to, not contradicting, the
object-level F1 headline". Its mechanism section identifies the cause:
sensitivity is essentially flat while specificity climbs — image
sensitivity 0.892 → 0.858 against specificity 0.169 → 0.478; text
sensitivity 0.927 → 0.922 against specificity 0.110 → 0.235.

The ladder in § 12.4 reproduces that signature almost exactly, on a
different corpus era, tile size, model, and replication regime:
sensitivity 0.9039 → 0.8035 (N=5) and 0.8559 → 0.8341 (N=10) as
temperature rises, against specificity 0.2713 → 0.5969 and 0.4302 →
0.5698. At N=10 the T=0.7 and T=1.0 arms have **identical** tile-level
sensitivity (0.8341, TP 191 / FN 38 in both), so the whole MCC gap is
specificity: 125 false-positive tiles against 111. Obs 274's explanation
carries over — higher temperature buys inter-run disagreement, and a
strict consensus threshold converts that disagreement into rejected
hallucinations on empty tiles.

So the two metrics are measuring different things and ordering
temperature differently, consistently, across two independent study
families:

| | What it rewards | Temperature ordering |
| :--- | :--- | :--- |
| Object-level F1 | finding mounds; recall-weighted | lower T better *where it has been tested at scale* |
| Tile-level MCC | correctly rejecting empty tiles; specificity-weighted | **higher T better**, monotonically |

**Against the pattern's canonical statements** — compared directionally
in prose, not recomputed:

- The **55-map deployment oracle**
  (`results/deployment-oracle-2026-06-06/deployment-oracle-findings.md`)
  is the load-bearing lower-temperature result: on corrected F1 @ 50 m,
  "text-high **T0.3** (k4)" scores 0.800 against "text-high T0.7 (k4,
  carried)" 0.780, and the document states "**T0.3 > T0.7 = +0.020
  (p<0.001)**". That is an **F1** claim on the **55-map deployment
  corpus**. Nothing in this section touches it: the ladder here is a
  4-map gold-standard corpus at 384 px, its F1 contrasts are all
  non-significant, and its only significant contrasts are on MCC. The
  two results are compatible because they are about different metrics.
- The **preregistered Phase 2b** F1 result (T=0.0 optimal, monotonic F1
  degradation as T rises) and the **Phase 2b MCC** result (Obs 274, MCC
  monotonic *increasing* in T) come from **the same ten cells**. The
  project has therefore already accepted that F1 and MCC order
  temperature oppositely; § 12.3 simply shows it holds here too, now with
  paired p-values rather than intervals.
- Where the F1 pattern and this ladder *appear* to disagree — T=1.0
  posting the best F1@20 m in § 12.4 — the disagreement is not
  statistically real: ΔF1 against T=0.3 is −0.0243 at p = 0.0624 and
  against T=0.7 is −0.0335 at p = 0.0815. This corpus is simply not
  powered to rank temperatures on F1.

**The honest one-line answer**: the T=1.0 MCC advantage is real,
survives pairing as an end-to-end contrast, and is *not* an exception to
the project's temperature pattern — because that pattern was never an
MCC pattern. It is an F1 pattern, and the project's own Obs 274 recorded
the MCC reversal fifteen weeks before this document raised it as a
surprise.

**T=0.0 is descriptive only.** The arm has three runs, so its best cell
is 3-of-3 against 10-of-10 comparators. The permutation test is
mechanically valid — the same 487 tiles, properly paired — and it was
run, but the contrast varies temperature **and** consensus depth
together, so tests 7–9 are not temperature p-values and must not be read
as such. What the row does contribute is the ladder's bottom rung: at
T=0.0 the arm emits the most detections (799), has the highest
sensitivity (0.9039) and by far the worst specificity (0.2713) and MCC
(0.2235) — the deterministic-decoding end of the diversity mechanism
Obs 274 describes, where near-identical runs produce near-identical
hallucinations that consensus voting cannot filter.

### 12.7 Caveats

1. **The operating points are F1-selected.** Every cell in § 12.4 is its
   arm's best F1@20 m point, and MCC is then read off it. § 11.2 caveat 2
   already flagged this; the ladder makes the cost visible. Within every
   arm's own sweep, MCC rises monotonically with the consensus threshold
   and keeps rising past the F1 optimum — the T=0.7 N=30 pool is the
   clearest case, where 29-of-30 is the best-F1 cell at MCC 0.3814 while
   30-of-30 scores MCC 0.4234 on a lower F1. **MCC-optimal selection
   would move every row of this table**, and quite possibly by different
   amounts per arm. The direction of the ladder is robust across the
   sweeps (higher T dominates at every matched threshold), but the
   magnitudes are not selection-free.
2. **Run counts are unequal.** T=0.7 has 30 runs, T=0.3 and T=1.0 have 10
   each, T=0.0 has 3. Only the N=5 and N=10 pools are comparable across
   arms, which is why the ladder is reported at those depths. No matched
   N=30 comparison is possible.
3. **The N=10 T=1.0 operating point is 9-of-10, not 10-of-10.** Each arm
   was allowed its own best-F1 threshold, so the N=10 row compares
   10-of-10 against 9-of-10. This is the § 3 convention and it is applied
   symmetrically, but it is an asymmetry in the comparison. At 10-of-10
   the T=1.0 arm scores F1@20 m 0.6509 and MCC 0.4273 — a lower F1 and a
   *higher* MCC than the 9-of-10 cell used here, so the choice is
   conservative with respect to the MCC conclusion.
4. **T=0.7 is the odd arm out on provenance.** It alone ran on
   2026-03-24 via the Batch API; the other three ran on 2026-04-17 via
   the governed real-time path (§ 12.5). Every contrast involving T=0.7
   inherits § 8 caveats 2 and 3. The significant contrasts do not.
5. **Multiplicity is uncorrected in the headline table.** § 12.3 reports
   raw p-values per § 8 caveat 7 and gives the BH result inline; only the
   T=0.3-versus-T=1.0 contrasts survive correction.
6. **Tile assignment is by spatial join.** Consensus GeoJSONs carry a
   plural `source_tiles` list and no singular `source_tile`, so every arm
   is assigned to tiles by the same `intersects` join, first match kept —
   identical to `evaluate_detections.py`, and identical across arms, so
   it cannot bias a contrast (§ 8 caveat 5).
7. **This section changes no registered claim.** It supplies the paired
   test § 11.2 asked for and the ladder context the PI commissioned. The
   paper's citable temperature evidence remains the preregistered
   Phase 2b sweep, as § 8 caveat 6 and the E72 erratum both direct.

### 12.8 Reproduction

Run from the repository root on sapphire with the project virtual
environment. Zero API calls; the whole section takes about 30 seconds.

```bash
# 1. the nine paired MCC tests (dry-run first — the gates run, the
#    permutations do not, and nothing is written)
.venv/bin/python scripts/paired_mcc_permutation.py \
    --jobs planning/paired-mcc-jobs/e72-temperature-ladder-2026-08-03.json \
    --output-dir results/e43-matched-temperature/paired-mcc
.venv/bin/python scripts/paired_mcc_permutation.py \
    --jobs planning/paired-mcc-jobs/e72-temperature-ladder-2026-08-03.json \
    --output-dir results/e43-matched-temperature/paired-mcc \
    --seed 42 --n-permutations 10000 --execute

# 2. the two new F1 ladder rungs (20 m and 30 m), for example:
S=outputs/h11/pv-diag-384/flash-minimal-text-n30-t07
.venv/bin/python scripts/pairwise_permutation_test.py --mode geojson \
    --geojson-a $S/text-t0.3/consensus/consensus_t10.geojson \
    --geojson-b $S/text-t1.0/consensus/consensus_t9.geojson \
    --label-a "Flash MIN text T=0.3 10-of-10 (487-tile, first-10)" \
    --label-b "Flash MIN text T=1.0 9-of-10 (487-tile, first-10)" \
    --bounds inputs/vectors/bounds/384/full_evaluation_bounds.geojson \
    --ground-truth inputs/vectors/references/mounds-reference.geojson \
    --buffer-metres 20 --n-permutations 10000 --seed 42 \
    --output-dir results/e43-matched-temperature/ladder-f1/t03-vs-t10-n10-20m

# 3. the tier-1 tests for the new script
.venv/bin/python -m pytest tests/test_paired_mcc_permutation.py -q
```

Artefacts:

- `paired-mcc/paired_mcc_summary.json` — all nine tests, null
  distributions, gate records.
- `paired-mcc/<pair_id>.json` — per-pair result with the full 487-row
  per-tile classification for both arms.
- `ladder-f1/t03-vs-t{07,10}-n10-{20,30}m/pairwise_permutation_result.json`
  — the four new F1 tests.

## 13. Cost-equivalent configurations — E72 follow-up (2026-08-03)

§ 12.4's ladder is descriptive on one point a practitioner cares about
more than any p-value: the best cell in the whole table on both metrics
is a **five-pass** configuration. The principal investigator (PI)
commissioned this section to formalise that observation. The question is
not "which temperature is better at matched pool depth?" — that is § 12 —
but "**can a practitioner buy similar-or-better output for half (or a
sixth) of the proposer calls?**"

**Produced**: 2026-08-03, on sapphire, from repository commit
`9ebc9e523`. Zero API calls; every figure derives from on-disk
detections and from evaluations already filed in this repository.

**Why these contrasts are deliberately cross-cell.** Every test in § 4
and § 12.3 holds pool depth fixed and varies temperature. These two vary
**both at once** — which would be a confound if the question were about
temperature, and is the entire point when the question is about
configurations. A practitioner does not choose a temperature and a pool
depth independently; they choose a configuration and pay for it. So the
comparison is read as "configuration X versus configuration Y", not as
"temperature X versus temperature Y", and no mechanism is attributed to
either factor alone.

### 13.1 The three configurations

Each arm sits at its own best-F1@20 m operating point in the pre-existing
threshold sweep under `results/phase3a-text-matrix/` — the § 3
convention, applied symmetrically. All three are sub-pools of the same
parent study, `outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/`, all
487/487 tiles, all verified strict first-N pools (§ 3.1, § 12.4).

| Configuration | Passes/tile | Threshold | Consensus GeoJSON | Detections | F1@20 m | F1@30 m | MCC | Sens. | Spec. |
| :--- | ---: | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| T=1.0, N=5 | **5** | 5-of-5 | `text-t1.0/consensus-n5/consensus_t5.geojson` | 509 | 0.6610 | 0.6674 | **0.4065** | 0.8035 | 0.5969 |
| T=0.7, N=10 | 10 | 10-of-10 | `text-t0.7/consensus-n10/consensus_t10.geojson` | 560 | 0.6332 | 0.6412 | 0.3655 | 0.8341 | 0.5155 |
| T=0.7, N=30 | 30 | 29-of-30 | `text-t0.7/consensus/consensus_t29.geojson` | 530 | 0.6611 | 0.6694 | 0.3814 | 0.8166 | 0.5543 |

The N=30 operating point was **verified, not assumed**: all 30 thresholds
in `results/phase3a-text-matrix/minimal-t0.7/n30/` were swept, and
F1@20 m peaks at 29-of-30 (0.6611; the neighbours are 28-of-30 at 0.6499
and 30-of-30 at 0.6584). This confirms the "~29-of-30" expectation
recorded in § 12.7 caveat 1. Feature counts read from the GeoJSONs
(509 / 560 / 530) agree with the `n_detections` recorded in each cell's
`evaluation.json`.

### 13.2 Paired tests — F1 at both buffers, and MCC

Same harness and settings as §§ 4 and 12.3: 487 tiles, 10,000
permutations, seed 42, bounds
`inputs/vectors/bounds/384/full_evaluation_bounds.geojson`, ground truth
`inputs/vectors/references/mounds-reference.geojson`. **Condition A is
the higher-cost T=0.7 arm, condition B the five-pass T=1.0 arm**, so
Δ = A − B and **a negative Δ favours the cheap configuration** — the same
orientation as the rest of this document, where negative favours T=1.0.

Tile-level MCC is buffer-invariant (§ 12.2), so each contrast yields one
ΔMCC that holds identically at 20 m and 30 m; F1 is tested at both.

| Contrast | Passes (A vs B) | ΔF1@20 m | p | ΔF1@30 m | p | ΔMCC | Paired p | Discordant tiles (A-only / B-only) | McNemar exact p |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: |
| T=0.7 N=10 vs T=1.0 N=5 | 10 vs 5 | −0.0279 | 0.1744 | −0.0262 | 0.2053 | −0.0410 | 0.2921 | 98 (42 / 56) | 0.1888 |
| T=0.7 N=30 vs T=1.0 N=5 | 30 vs 5 | +0.0001 | 0.9793 | +0.0021 | 0.9353 | −0.0252 | 0.5306 | 100 (46 / 54) | 0.4841 |

Supporting detail, for reference:

| Contrast | Buffer | F1 (A) | F1 (B) | Wins/losses/ties | Null 95 % CI |
| :--- | ---: | ---: | ---: | :--- | :--- |
| T=0.7 N=10 vs T=1.0 N=5 | 20 m | 0.6332 | 0.6610 | 24/33/430 | [−0.0394, +0.0390] |
| T=0.7 N=10 vs T=1.0 N=5 | 30 m | 0.6412 | 0.6674 | 25/32/430 | [−0.0396, +0.0390] |
| T=0.7 N=30 vs T=1.0 N=5 | 20 m | 0.6611 | 0.6610 | 25/27/435 | [−0.0377, +0.0377] |
| T=0.7 N=30 vs T=1.0 N=5 | 30 m | 0.6694 | 0.6674 | 26/26/435 | [−0.0384, +0.0384] |

Both arms of both MCC contrasts passed the confusion-reproduction gate of
§ 12.1 — the T=1.0 N=5 and T=0.7 N=10 arms against two independent
recorded references apiece, the T=0.7 N=30 arm against its
`phase3a-text-matrix` sweep evaluation. The rightmost column is the same
independent exact-McNemar cross-check used in § 12.3, computed with
`scipy.stats.binomtest` on the discordant tiles; it agrees with the
permutation test on the α = 0.05 verdict in both rows. Raw p-values, per
§ 8 caveat 7; no BH correction is reported because nothing here is
significant to begin with, so no correction could change a verdict.

### 13.3 Cost framing

Per-pass costs for **this exact study family** are audited in
`reports/token-load-audit-2026-06-12.md` § 4, at the gold-standard
487-tile corpus scale and at Gemini's flex service tier (the tier every
run in this family executed at):

- **T=1.0 minimal text, measured at 487 tiles**: **$0.289/pass**, from
  the ten `outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t1.0/run_*/`
  metadata files — the very runs pooled here.
- **T=0.7 minimal text: $0.266/pass, scaled not measured.** The 30
  gold-standard T=0.7 metas are Batch API records with zero usage
  (`usage_stats` all 0), so the audit scales the ten measured 55-map
  minimal passes by 487/8,541. This is the `MIN_PASS_USD` constant
  adopted in `scripts/build_pareto_v2.py` (audit § 5).

| Configuration | Passes/tile | Proposer cost, 487 tiles | Per tile | Relative |
| :--- | ---: | ---: | ---: | ---: |
| T=1.0, N=5 | 5 | $1.45 | $0.0030 | **1.00×** |
| T=0.7, N=10 | 10 | $2.66 | $0.0055 | 1.84× |
| T=0.7, N=30 | 30 | $7.98 | $0.0164 | 5.52× |

Two framings, and the pass ratio is the more portable of them:

1. **Pass ratio (model- and price-independent)**: 1 : 2 : 6. Proposer API
   calls are strictly proportional to pool depth — one call per tile per
   pass — so this ratio survives any repricing, any provider, and any
   corpus size.
2. **Dollar ratio (this study family, flex tier, 2026-06-12 prices)**:
   1.00 : 1.84 : 5.52. It is slightly flatter than the pass ratio because
   T=1.0 costs marginally *more* per pass than T=0.7 ($0.289 against
   $0.266 — higher temperature buys slightly longer outputs). Doubling
   both figures gives standard-tier prices; the audit records standard as
   exactly 2× flex.

Neither figure includes a verifier stage: these are proposer-consensus
cells with no verification pass, so the comparison is proposer-side only
and complete on its own terms.

### 13.4 What the tests support

**The honest answer to the PI's question: yes, descriptively, and the
paired tests decline to contradict it — but they cannot confirm it
either.**

- **Against N=10 (half the calls)**, the five-pass T=1.0 configuration is
  ahead on every metric measured: +0.0279 F1@20 m, +0.0262 F1@30 m,
  +0.0410 MCC. Not one of those differences is significant
  (p = 0.17, 0.21, 0.29). The direction is consistent, the evidence is
  weak, and the correct summary is "**no penalty detected for halving the
  proposer budget, with a consistent non-significant hint of a gain**".
- **Against N=30 (a sixth of the calls)**, F1 is a dead heat — 0.6611
  against 0.6610 at 20 m, a gap of 0.0001, p = 0.9793 — while MCC still
  favours the cheap arm by 0.0252 (p = 0.5306). Six times the proposer
  spend buys, on this corpus, **nothing measurable on F1 and a
  non-significant deficit on tile-level MCC**.
- **What "not significant" costs here.** The 20 m null 95 % intervals are
  ±0.038–0.039 F1, so these tests cannot resolve a true difference
  smaller than about 0.04 F1 in either direction. The N=10 contrast
  (−0.028) sits inside that band; a real advantage of that size would not
  be detectable at this corpus size. **This is a non-inferiority-shaped
  result reported with a superiority-shaped test**, and it should be
  read as "no detectable penalty", never as "proven equivalent".
- **Where the mechanism points.** The § 12.6 signature carries over: the
  cheap arm emits the fewest detections of the three (509 against 560 and
  530), has the lowest tile-level sensitivity (0.8035) and the highest
  specificity (0.5969). It buys its MCC edge by rejecting empty tiles, not
  by finding more mounds. A practitioner whose loss function is
  recall-dominated — screening for candidates to be checked by eye — may
  rationally prefer the deeper T=0.7 pools despite the cost, and should
  make that choice on their own loss function rather than on these
  aggregate numbers.

### 13.5 Caveats

These are additional to, not instead of, § 8 and § 12.7.

1. **The operating points are F1-selected** (§ 12.7 caveat 1). Each arm
   sits at its own best F1@20 m cell and MCC is read off it. The N=30 arm
   is the sharpest illustration: at 30-of-30 it scores MCC 0.4234 —
   *above* the cheap arm's 0.4065 — on a lower F1 (0.6584). **An
   MCC-selected N=30 operating point would reverse the sign of the MCC
   contrast in row 2.** The F1 result is unaffected by this (F1 is the
   selection criterion, and 29-of-30 is its optimum), but the MCC column
   of row 2 is selection-dependent and must not be quoted alone.
2. **The T=0.7 arms carry the batch-path and date difference** (§ 8
   caveats 2 and 3, § 12.7 caveat 4). Both T=0.7 arms here ran
   2026-03-24 via the asynchronous Batch API; the T=1.0 arm ran
   2026-04-17 via the governed real-time path. Every contrast in § 13.2
   inherits that uncontrolled variable. Unlike § 12.5's clean
   T=0.3-versus-T=1.0 contrast, there is no confound-free version of the
   cost comparison available in these data, because T=0.7 is the only arm
   with pools deeper than 10.
3. **Cross-cell by construction.** Temperature and pool depth vary
   together (§ 13, opening). These rows license configuration-level
   claims only; no factor-level mechanism may be attributed from them.
4. **The T=0.7 per-pass cost is scaled, not measured** (§ 13.3). The
   audit brackets the analogous HIGH-thinking scaling within its measured
   gold-standard range, but the minimal-text T=0.7 figure has no
   gold-standard measurement to check it against. The **pass ratio**
   (1 : 2 : 6) carries no such uncertainty and is the figure to quote if
   only one is quoted.
5. **Exploratory, single corpus, no registered family.** Four-map
   gold-standard corpus at 384 px, one model, one prompt, one thinking
   level. Six new tests, all non-significant, raw p-values, not members
   of any registered BH family. This section changes no registered claim
   and mints no condition; it is decision support for a practitioner
   question, not preregistered hypothesis evidence.
6. **Absence of evidence, not equivalence.** Restating § 13.4 because it
   is the failure mode this section most invites: a non-significant ΔF1
   of 0.0001 is a dead heat *in these data*, not a demonstration that the
   two configurations are interchangeable.

### 13.6 Reproduction

Run from the repository root on sapphire with the project virtual
environment. Zero API calls; about 15 seconds.

```bash
# 1. the two paired MCC tests (dry-run first — gates run, permutations
#    do not, nothing is written)
.venv/bin/python scripts/paired_mcc_permutation.py \
    --jobs planning/paired-mcc-jobs/e72-cost-equivalent-2026-08-03.json \
    --output-dir results/e43-matched-temperature/cost-equivalent/paired-mcc
.venv/bin/python scripts/paired_mcc_permutation.py \
    --jobs planning/paired-mcc-jobs/e72-cost-equivalent-2026-08-03.json \
    --output-dir results/e43-matched-temperature/cost-equivalent/paired-mcc \
    --seed 42 --n-permutations 10000 --execute

# 2. the four paired F1 tests (two contrasts x 20 m and 30 m), e.g.
S=outputs/h11/pv-diag-384/flash-minimal-text-n30-t07
.venv/bin/python scripts/pairwise_permutation_test.py --mode geojson \
    --geojson-a $S/text-t0.7/consensus/consensus_t29.geojson \
    --geojson-b $S/text-t1.0/consensus-n5/consensus_t5.geojson \
    --label-a "Flash MIN text T=0.7 29-of-30 (487-tile, first-30, 30 passes)" \
    --label-b "Flash MIN text T=1.0 5-of-5 (487-tile, first-5, 5 passes)" \
    --bounds inputs/vectors/bounds/384/full_evaluation_bounds.geojson \
    --ground-truth inputs/vectors/references/mounds-reference.geojson \
    --buffer-metres 20 --n-permutations 10000 --seed 42 \
    --output-dir results/e43-matched-temperature/cost-equivalent/f1/t07n30-vs-t10n5-20m
```

Artefacts:

- `cost-equivalent/paired-mcc/paired_mcc_summary.json` and
  `cost-equivalent/paired-mcc/<pair_id>.json` — the two MCC tests, null
  distributions, gate records, and the full 487-row per-tile
  classification for each arm.
- `cost-equivalent/f1/t07n{10,30}-vs-t10n5-{20,30}m/pairwise_permutation_result.json`
  — the four F1 tests.

## Changelog

### 2026-08-03 (later) — cost-equivalent configurations (E72 follow-up)

**Trigger**: PI commission of 2026-08-03, arising from § 12.4's ladder —
the best cell on both F1 and MCC is a five-pass configuration, which
raises a practitioner question the ladder was not built to answer: can
T=1.0 with N=5 match or beat T=0.7 with N=10 (half the proposer calls) or
N=30 (a sixth)? The ladder answered descriptively; this section
formalises it with paired tests and states the cost basis.

| Claim | Before | After |
|---|---|---|
| Cost-equivalence evidence | descriptive only — § 12.4 ladder rows read side by side | six paired permutation tests (two contrasts × F1@20 m, F1@30 m, MCC), 487 tiles, 10,000 permutations, seed 42, each MCC test cross-checked against an exact McNemar test (§ 13.2) |
| T=1.0/N=5 vs T=0.7/N=10 | F1 0.6610 vs 0.6332, MCC 0.4065 vs 0.3655, untested | ΔF1@20 m −0.0279 (p = 0.1744), ΔF1@30 m −0.0262 (p = 0.2053), ΔMCC −0.0410 (p = 0.2921) — cheap arm ahead on all three, **none significant** |
| T=1.0/N=5 vs T=0.7/N=30 | not compared at 487 tiles | ΔF1@20 m **+0.0001** (p = 0.9793), ΔF1@30 m +0.0021 (p = 0.9353), ΔMCC −0.0252 (p = 0.5306) — a dead heat on F1 at six times the proposer spend |
| T=0.7 N=30 operating point | "~29-of-30" inferred in § 12.7 caveat 1 | **verified** by sweeping all 30 thresholds: F1@20 m peaks at 29-of-30 (0.6611; neighbours 0.6499 and 0.6584), 530 detections, MCC 0.3814 (§ 13.1) |
| Cost basis | not stated in this document | pass ratio 1 : 2 : 6, and audited flex-tier per-pass figures for this exact study family — T=1.0 $0.289/pass measured at 487 tiles, T=0.7 $0.266/pass scaled (`reports/token-load-audit-2026-06-12.md` § 4) → $1.45 / $2.66 / $7.98 per 487-tile run, 1.00× / 1.84× / 5.52× (§ 13.3) |
| Selection sensitivity of the N=30 MCC row | not assessed | flagged as **sign-reversing**: at an MCC-selected 30-of-30 the N=30 arm scores MCC 0.4234, above the cheap arm's 0.4065 (§ 13.5 caveat 1) |

What did NOT change: every figure in §§ 1–12 and their changelog
entries. The four § 3 operating points, the § 12.3 nine-test ΔMCC table,
the § 12.4 ladder, and the § 12.5–12.6 interpretation all stand
untouched; § 13 only adds cross-cell contrasts alongside them. No
conditions were minted, no evaluation was re-scored, no registered claim
was changed. Zero API calls; all computation on sapphire.

### 2026-08-03 — paired MCC tests and the temperature ladder (E72 follow-up)

**Trigger**: PI commission of 2026-08-03, arising from § 11.2's flagged
unpaired-MCC caveat — the matched-scope finding that tile-level MCC
favours T=1.0 read as a possible exception to the project's
lower-temperature-is-better pattern, and needed both a proper paired test
and ladder context before it could be interpreted.

| Claim | Before | After |
|---|---|---|
| MCC evidence type | unpaired per-condition BCa intervals, "disjoint at both pool sizes" | nine paired tile-swap permutation tests, 10,000 permutations, seed 42, each cross-checked against an exact McNemar test (§ 12.3) |
| T=0.7 vs T=1.0, N=5 | ΔMCC −0.0917, disjoint intervals | ΔMCC −0.0918, **paired p = 0.0255** (BH q = 0.0510) |
| T=0.7 vs T=1.0, N=10 | ΔMCC −0.0498, disjoint intervals | ΔMCC −0.0498, **paired p = 0.2114 — not significant** (§ 11.2 corrected in place) |
| Strongest MCC contrast | not assessed | T=0.3 vs T=1.0: −0.1319 p = 0.0005 (N=5), −0.1023 p = 0.0023 (N=10); the only contrasts surviving BH, and the only ones free of the execution-path confound (§ 12.5) |
| "Non-overlapping intervals are, for a paired design, conservative" | asserted in § 11.2 caveat 1 | **withdrawn** — the paired null is the wider of the two here, for a structural reason (§ 12.3) |
| Temperature evidence scope | T=0.7 and T=1.0 only | four-rung ladder T=0.0 / 0.3 / 0.7 / 1.0 with F1@20 m, F1@30 m, MCC, sensitivity, specificity and confusion cells (§ 12.4), plus four new paired F1 tests |
| Tooling | "no paired MCC permutation test was run; `pairwise_permutation_test.py` tests F1" | the MCC kernel existed since commit `62d1173af` but was not CLI-reachable; `scripts/paired_mcc_permutation.py` now exposes it with a hard confusion-reproduction gate and 17 tier-1 tests |
| The exception question | open | **answered: not an exception, a replication** — Obs 274 (2026-04-23) already found MCC rising monotonically with T in the preregistered Phase 2b sweep, by the same flat-sensitivity/climbing-specificity mechanism (§ 12.6) |

What did NOT change: every figure in §§ 1–10 and § 11.1, § 11.3 and
§ 11.4. The four F1@20 m operating points (0.6397, 0.6610, 0.6332,
0.6667), the four § 11.1 MCC values and their confusion cells, the
240-tile leg, the coverage quantification (193/435; ceiling 0.5563), and
the manifest registration all stand. § 11.2 was edited in place in three
places — the results table gained a paired-p column, caveat 1's
"conservative" expectation was withdrawn, and the closing "and clearly"
was qualified — with each edit pointing at § 12. No conditions were
minted; no evaluation was re-scored. Zero API calls; all computation on
sapphire.

### 2026-08-02 (later) — house-grain filing (E72 remediation item 3)

**Trigger**: erratum E72 (`protocol-errata.md` § E72, PI-approved
2026-08-02) requires the matched cells to be filed "as their own
first-class analysis (14-buffer + MCC, manifest-registered)"; the
original publication reported F1 only, which the project's
report-MCC-alongside-F1 rule treats as an omission.

| Claim | Before | After |
|---|---|---|
| Metric coverage | F1 at 20 m and 30 m only | 14 buffers (5–150 m) + tile-level MCC with BCa 95 % intervals for all four cells (§ 11.1) |
| Matched-scope verdict | "no reliable difference" (F1, n.s.) | unchanged on F1; **MCC separates the arms in T=1.0's favour** (ΔMCC −0.0917 at N=5, −0.0498 at N=10, disjoint intervals) — flagged with its unpaired-test and F1-selected-threshold caveats (§ 11.2) |
| Manifest status | unregistered | analysis `e43-matched-temperature` over the four existing `pv-diag-384` condition ids; analyses 20 → 21 (§ 11.4) |

What did NOT change: every figure in §§ 1–10. The four F1@20 m
operating-point values (0.6397, 0.6610, 0.6332, 0.6667) were the sanity
gate on the re-score and reproduce exactly; the permutation results, the
240-tile leg, the coverage quantification (193/435; ceiling 0.5563), the
configuration-parity checks, and the caveats all stand as published. No
new conditions were minted — the four cells were already registered
(§ 11.4). Zero API calls; all computation on sapphire.

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
