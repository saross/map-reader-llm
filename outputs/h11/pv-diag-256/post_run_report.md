<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — pv-diag-256

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `2fa91cdb1`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/h11/pv-diag-256` · **Registry status**: active · **Purpose**: 256px H11 tile-size diagnostic (px256-1032 scope, 1032 tiles, curator GT): the small-tile anchor for the tile-size comparison, where F1@20m orders 256 &lt; 512 &lt; 384 (0.46 / 0.69 / 0.79). Unregistered exploratory extension of the registered H11 two-level design (E62); populated 2026-07-30 per the PI ruling at reports/verification/phase2-rulings-2026-07-30.md S 1b.

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `pv-diag-256` |
| Directory | `outputs/h11/pv-diag-256` |
| Registry status | active |
| Purpose | 256px H11 tile-size diagnostic (px256-1032 scope, 1032 tiles, curator GT): the small-tile anchor for the tile-size comparison, where F1@20m orders 256 &lt; 512 &lt; 384 (0.46 / 0.69 / 0.79). Unregistered exploratory extension of the registered H11 two-level design (E62); populated 2026-07-30 per the PI ruling at reports/verification/phase2-rulings-2026-07-30.md S 1b. |
| Run type (derived) | mixed |
| Primary hypothesis | H11 |
| Also informs | — |
| Headline condition | not supplied |
| Headline rationale | not supplied |
| Historical aliases | — |
| Working-notes Obs | — |
| Registry notes | H11 (pv-diag, 256px). Absent from inventory. |

## 2. Scope and evaluation frame

| Field | Value |
|---|---|
| Tile size (px) | 256 |
| Corpus | 4-map-gs |
| Ground-truth reference | curator |
| Test set id | px256-1032 |
| Test tiles | 1032 |
| Bounds | `inputs/vectors/bounds/256/full_evaluation_bounds.geojson` |
| Calibration set id | not supplied |
| Calibration tiles | not supplied |

## 3. Execution — passes on file

No pass rows in `results/passes-manifest.json` for this run. A run is decomposed into passes only where its proposer/verifier metas were materialised as resolvable pass files; where they were not, the decomposition records pools and conditions without passes. See § 5 for the registered conditions and § 1 for the registry note.

## 4. Token load and recorded cost

No pass rows, so no recorded token load. not supplied: this run's spend is not reconstructable from the passes manifest.

No cost audit on file names this run or its directory: an independently audited cost for this run is **not supplied**. The four audits checked are `reports/token-load-audit-2026-06-12.md`, `reports/r7-gaps-deltas-2026-09-11.md`, `reports/k-ladder-phase2-deltas-2026-09-12.md`, `reports/billing-reconciliation-2026-09-11.md`.

## 5. Registered conditions (3)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `text-baseline` | single-pass | none | 1 | — | 1828 | 0.3417 [0.3033, 0.3834] | 0.3462 [0.3075, 0.3880] | 0.0883 |
| `text-consensus-5of5` | consensus | consensus | 5 | k=5 | 1165 | 0.4599 [0.4131, 0.5089] | 0.4662 [0.4198, 0.5147] | 0.1527 |
| `verified-adv-text-consensus-5of5` | proposer-verifier | verified | 1 | pt=0.2 | 394 | 0.8558 [0.8222, 0.8843] | 0.8679 [0.8363, 0.8944] | 0.7448 |

Buffers on file (metres), by how many conditions carry that set:

- 3 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150

Tile-level MCC is on file for 3 of 3 condition(s).

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> 256px H11 tile-size diagnostic (px256-1032 scope, 1032 tiles, curator GT). Re-scored at 14-buf+MCC (Session 106) from the 6 on-disk consensus geojsons. text-baseline = single-pass; text-{1..5}of5 = 5-pass consensus vote sweep. One citable single-pass + the best-F1@20m consensus champion (text-5of5, F1 0.460); non-headline thresholds -&gt; \_ignored\_evals. Proposer passes were NOT materialised as run\_\* dirs (only consensus + crops), so proposer\_pools is empty and conditions reference the pool by string (benign pool-unresolved; pv-384/512 precedent). 256px is the small-tile anchor for the tile-size comparison: F1@20m orders 256 &lt; 512 &lt; 384 (0.46 / 0.69 / 0.79). | Pool annotation (2026-09-13, S153 Batch 1 item 2): the 'benign pool-unresolved' adjudication stated above is now machine-readable — source\_run 'pv-diag-256' on both conditions. Two uplift-supplement verifier-pairing evaluations of this run's text-5of5 detections, which belong to the cross-run verifier-robustness 256 conditions, are waived into \_ignored\_evals with reasons. No metric, eval or detection changed.

### 5.4 Waived evaluations (6, 3 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **4 evaluation(s)** — not supplied — a bare-string entry, written before the waiver register carried reasons
  - `results/rescore-2026-06-08/pv-diag-256/text-1of5/evaluation.json`
  - `results/rescore-2026-06-08/pv-diag-256/text-2of5/evaluation.json`
  - `results/rescore-2026-06-08/pv-diag-256/text-3of5/evaluation.json`
  - `results/rescore-2026-06-08/pv-diag-256/text-4of5/evaluation.json`
- **1 evaluation(s)** — Uplift-supplement verifier-pairing input for the CROSS-RUN condition verifier-robustness::verified-256-union-t0-0-n5, which draws its proposer pool from this run (source\_run 'pv-diag-256' in scripts/author\_verifier\_robustness\_registration.py) and so scores outputs/h11/pv-diag-256/consensus/text-5of5.geojson. It surfaces under pv-diag-256 only because the detections live here; it is an input to the supplement's pairing tables (planning/uplift-supplement-2026-08-28.md), not a pv-diag-256 condition. Same waiver class as the 55maps-text-min-n10-uplift pairing entries (PI ruling 2026-09-07, planning/reference-revision-2026-09-06.md).
  - `results/uplift-supplement/verifier-pairing/verifier-robustness__verified-256-union-t0-0-n5/evaluation.json`
- **1 evaluation(s)** — Uplift-supplement verifier-pairing input for the CROSS-RUN condition verifier-robustness::verified-256-ge3of5-t0-3-n5, which draws its proposer pool from this run (source\_run 'pv-diag-256' in scripts/author\_verifier\_robustness\_registration.py) and so scores outputs/h11/pv-diag-256/consensus/text-5of5.geojson. It surfaces under pv-diag-256 only because the detections live here; it is an input to the supplement's pairing tables (planning/uplift-supplement-2026-08-28.md), not a pv-diag-256 condition. Same waiver class as the 55maps-text-min-n10-uplift pairing entries (PI ruling 2026-09-07, planning/reference-revision-2026-09-06.md).
  - `results/uplift-supplement/verifier-pairing/verifier-robustness__verified-256-ge3of5-t0-3-n5/evaluation.json`

## 6. Analyses that read this run (3)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `tile-size-sweep` | 3 of 35 | sweep | `H11` | registered-exploratory | Results | `E36`, `E41`, `E43`, `E44`, `E56`, `E57`, `E62` | 2026-06-09T01:52:52Z | `results/tile-size-sweep` |
| `uplift-supplement-flatten` | 3 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |
| `verifier-uplift-pairing` | 1 of 170 | comparison | `H2` | post-hoc | Appendix | — | 2026-09-12T06:04:30Z | `results/uplift-supplement/verifier-uplift.csv` |

## 7. Findings documents (0)

No findings document on disk is named by an analysis that reads this run: a findings write-up for this run is **not supplied** from the register. § 6's `output_path` column gives each analysis's artefact directory.

## 8. Protocol errata

### 8.1 Registered as deviations (7)

Listed in the `deviations` field of an analysis that reads this run:

- **E36** — 340-tile production retest replaces 60-tile holdout evaluation (corrected 2026-07-30)
- **E41** — 384px tile size and full evaluation set used for Pro comparison
- **E43** — consensus-384 executed at T=1.0 instead of T=0.7
- **E44** — single-pass-384 executed at T=1.0 instead of T=0.0
- **E56** — Verifier probability-threshold operating points are in-sample (test-set-selected), not calibrated
- **E57** — H11 384px Pro/baseline detection metadata — model template default and output\_dir overrides
- **E62** — Three unregistered proposer-verifier extension studies (`flash35-pv-2x2`, `pv-diag-256`, `verifier-robustness`) and four unregistered verifier-parameter levels — additional exploratory extensions of the registered PV contingency

## 9. Documents and structure in the run directory

No `experiment_intent.md`, `evaluation.md`, `pre_launch_audit.md` or retrospective report under this directory.

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `2fa91cdb1` |
| Manifest extractor | `0.7.1` |
| Run row last extracted | `2026-09-13T09:02:37Z` |

Inputs:

- `results/run-registry.json`
- `results/runs-manifest.json`
- `results/conditions-manifest.json`
- `results/passes-manifest.json`
- `results/analyses-manifest.json`
- `results/run-conditions.json`
- `results/run-analyses.json`
- `docs/methodology/preregistration/protocol-errata.md`

The run row's own upstream sources, as the manifest records them:

- `results/run-facts.json`
- `inputs/vectors/bounds/256/full_evaluation_bounds.geojson`

Regenerate and drift-check with:

```bash
python3 scripts/generate_run_reports.py --all --write
python3 scripts/generate_run_reports.py --check
```
