<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — pv-diag-256

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `a710152d1`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

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

### 3.1 Proposer passes (6)

| Pool | Pass | Model used | Model requested | Modality | Thinking | Temp | Status | Tiles done | Dispatched | Retries |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| `text-baseline-text-t0.0` | 1 | gemini-3-flash | gemini-3-flash | text | minimal | 0.0 | ok | 1032 | not supplied | 0 |
| `text-n5-text-t0.7` | 1 | gemini-3-flash | gemini-3-flash | text | minimal | 0.7 | ok | 1032 | not supplied | 0 |
| `text-n5-text-t0.7` | 2 | gemini-3-flash | gemini-3-flash | text | minimal | 0.7 | ok | 1032 | not supplied | 0 |
| `text-n5-text-t0.7` | 3 | gemini-3-flash | gemini-3-flash | text | minimal | 0.7 | ok | 1032 | not supplied | 0 |
| `text-n5-text-t0.7` | 4 | gemini-3-flash | gemini-3-flash | text | minimal | 0.7 | ok | 1032 | not supplied | 0 |
| `text-n5-text-t0.7` | 5 | gemini-3-flash | gemini-3-flash | text | minimal | 0.7 | ok | 1032 | not supplied | 0 |

### 3.2 Verifier passes (1)

| Pool | Pass | Model used | Modality | Thinking | Temp | Status | Candidates verified | Retries |
|---|---:|---|---|---|---:|---|---:|---:|
| `verified-adv-text-consensus-5of5` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 1165 | 36 |

Verifier rows report no tile count by design: verifier pass: operates on candidate crops, not tiles. The verifier meta records candidate ids (cand\_NNNN) in execution\_stats.completed\_items and candidate API items in per\_item\_metadata, so no tile-scale record exists to report. Completed crop count is in n\_candidates\_verified. (E71 Defect 2 / GAP-8, resolved E72 2026-08-02.)

## 4. Token load and audited cost

| Field | Value |
|---|---|
| Passes on file | 7 |
| Input tokens (billed) | 2,087,680 |
| Input tokens (cached) | 0 |
| Output tokens | 184,732 |
| Thinking tokens | 0 |
| Total tokens | 2,272,412 |
| Passes with no token record | 0 |
| `cost_usd` by basis | audited US$0.7990 (1); unrecorded no figure (6) |
| Run total (range) | at least US$0.7990; no ceiling (6 unrecorded pass(es)) |
| Passes with no `cost_usd` | 6 |
| Summed wall clock | 0.15 h over 7 pass(es) |

> **The cost above is on the audited basis, labelled per pass.** Since generator 0.8.0 (2026-10-03; PI ruling D11) each `cost_usd` is the pass's own tokens, recovery fragments included, priced by `scripts/lib_cost.price_usage` at the service tier the evidence supports; the pass's `cost_basis` says whether that is `audited`, an `audited-upper-bound` (tier unresolved, priced at the highest candidate), an `audited-lower-bound` (part of the pass is not in its metas: a cleanup overwrote one, or a fragment recorded nothing), `published`, `unrecorded`, or `unpriceable` (no date, or a model the rate card lacks), and its `cost_source` cites the evidence. It is no longer the pass meta's own `cost_estimate`, which priced at standard rates and omitted thinking tokens (`reports/token-load-audit-2026-06-12.md` § 1, § 2). A sum mixing upper and lower bounds is neither, so the run total is given as a range.

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

> 256px H11 tile-size diagnostic (px256-1032 scope, 1032 tiles, curator GT). Re-scored at 14-buf+MCC (Session 106) from the 6 on-disk consensus geojsons. text-baseline = single-pass; text-{1..5}of5 = 5-pass consensus vote sweep. One citable single-pass + the best-F1@20m consensus champion (text-5of5, F1 0.460); non-headline thresholds -&gt; \_ignored\_evals. Proposer passes were NOT materialised as run\_\* dirs (only consensus + crops), so proposer\_pools is empty and conditions reference the pool by string (benign pool-unresolved; pv-384/512 precedent). 256px is the small-tile anchor for the tile-size comparison: F1@20m orders 256 &lt; 512 &lt; 384 (0.46 / 0.69 / 0.79). | Pool annotation (2026-09-13, S153 Batch 1 item 2): the 'benign pool-unresolved' adjudication stated above is now machine-readable — source\_run 'pv-diag-256' on both conditions. Two uplift-supplement verifier-pairing evaluations of this run's text-5of5 detections, which belong to the cross-run verifier-robustness 256 conditions, are waived into \_ignored\_evals with reasons. No metric, eval or detection changed. | Corrected 2026-10-07 (stale register notes, PI-approved; reviewed bindings pv-diag-256-text-baseline and pv-diag-256-text-5of5-union in results/manipulation-gate-bindings.json): 'Proposer passes were NOT materialised as run\_\* dirs' above is wrong. They were materialised, and they are tracked with their metas under archive/outputs-non-production-tile-sizes/, where 276e4ca80 (2026-04-16) archived them from outputs/h11/pv-diag-256/: the N=1 T=0.0 baseline pass at text-baseline/text-t0.0/run\_1 and the five N=5 T=0.7 passes at text-n5/text-t0.7/run\_1..run\_5 (detect\_brief-text, gemini-3-flash, MINIMAL, 1,032 tiles each). consensus/text-baseline.geojson is byte-identical to the baseline pass's detections (sha256 bf44bc7b11e3...), and a read-only reproduction from the five T=0.7 passes gives the feature counts of text-1of5..text-5of5 and the coordinates of text-5of5 exactly. proposer\_pools stays empty only because no registered pool spec reaches archive/; registering one is a separate decision. No metric, eval or detection changed. | Registered in place 2026-10-08 (PI ruling 2026-10-08, approving the Session 162 close's recommendation 'register pv-diag-256 in place', planning/paper-writeup-continuity.md; record: reports/stale-register-notes-2026-10-07.md section 10): 'proposer\_pools stays empty' in the 2026-10-07 correction above is superseded. The six archived passes are registered where they lie, and no file moved: proposer\_pools text-baseline-text-t0.0 (the N=1 T=0.0 baseline pass) and text-n5-text-t0.7 (the five N=5 T=0.7 passes) name repo\_path archive/outputs-non-production-tile-sizes, the mechanism h10's coldstart-pool\_160 uses (ruling D41); the keys follow pv-diag-384's names for the same layout. Their metas record no token usage (Batch API), so their passes-manifest rows carry cost\_usd null with basis unrecorded (ruling D12). The conditions are unchanged: both still name proposer\_pool 'text' with source\_run pv-diag-256, as pv-diag-384's baseline conditions name theirs beside registered pools. scripts/check\_union\_provenance.py now re-derives consensus/ from text-n5-text-t0.7 (POOL\_OVERRIDES) and reproduces text-1of5..text-5of5 exactly (2,558 / 1,909 / 1,645 / 1,423 / 1,165 features). No metric, eval or detection changed.

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

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `text-baseline-text-t0.0` | text | none: outside the run directory, at `archive/outputs-non-production-tile-sizes/text-baseline/text-t0.0` (`repo_path`) |
| `text-n5-text-t0.7` | text | none: outside the run directory, at `archive/outputs-non-production-tile-sizes/text-n5/text-t0.7` (`repo_path`) |

1 registered verifier-pass directory/directories; see `results/run-conditions.json` for the full list.

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `a710152d1` |
| Manifest extractor | `0.8.0` |
| Run row last extracted | `2026-10-03T07:57:28Z` |

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
