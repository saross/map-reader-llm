<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — retest-phase2c

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `f307c1932`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/retest/phase2c` · **Registry status**: active · **Purpose**: not supplied

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `retest-phase2c` |
| Directory | `outputs/retest/phase2c` |
| Registry status | active |
| Purpose | not supplied |
| Run type (derived) | single-pass |
| Primary hypothesis | H8 |
| Also informs | — |
| Headline condition | not supplied |
| Headline rationale | not supplied |
| Historical aliases | `Era 1` |
| Working-notes Obs | — |
| Registry notes | H8. |

## 2. Scope and evaluation frame

| Field | Value |
|---|---|
| Tile size (px) | 512 |
| Corpus | 4-map-gs |
| Ground-truth reference | curator |
| Test set id | era-1-340 |
| Test tiles | 340 |
| Bounds | `inputs/vectors/bounds/full_evaluation_bounds.geojson` |
| Calibration set id | cal-20-512 |
| Calibration tiles | 20 |

## 3. Execution — passes on file

### 3.1 Proposer passes (13)

| Pool | Pass | Model used | Model requested | Modality | Thinking | Temp | Status | Tiles done | Dispatched | Retries |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| `track1-image-canonical` | 1 | gemini-3-flash | gemini-3-flash | image | minimal | 0.0 | ok | 340 | not supplied | 0 |
| `track1-image-exploratory-pure-positive-2hp` | 1 | gemini-3-flash | gemini-3-flash | image | minimal | 0.0 | ok | 340 | not supplied | 0 |
| `track1-image-exploratory-pure-positive-4hp` | 1 | gemini-3-flash | gemini-3-flash | image | minimal | 0.0 | ok | 340 | not supplied | 0 |
| `track1-image-exploratory-pure-positive-canon` | 1 | gemini-3-flash | gemini-3-flash | image | minimal | 0.0 | ok | 340 | not supplied | 0 |
| `track1-image-plus-hp` | 1 | gemini-3-flash | gemini-3-flash | image | minimal | 0.0 | ok | 340 | not supplied | 0 |
| `track1-image-pure-positive-canon` | 1 | gemini-3-flash | gemini-3-flash | image | minimal | 0.0 | ok | 340 | not supplied | 0 |
| `track1-image-scale-4` | 1 | gemini-3-flash | gemini-3-flash | image | minimal | 0.0 | ok | 340 | not supplied | 0 |
| `track1-image-scale-8` | 1 | gemini-3-flash | gemini-3-flash | image | minimal | 0.0 | ok | 340 | not supplied | 0 |
| `track2-text-canonical` | 1 | gemini-3-flash | gemini-3-flash | text | minimal | 0.0 | ok | 340 | not supplied | 0 |
| `track2-text-plus-hp` | 1 | gemini-3-flash | gemini-3-flash | text | minimal | 0.0 | ok | 340 | not supplied | 0 |
| `track2-text-pure-positive-canon` | 1 | gemini-3-flash | gemini-3-flash | text | minimal | 0.0 | ok | 340 | not supplied | 0 |
| `track2-text-scale-4` | 1 | gemini-3-flash | gemini-3-flash | text | minimal | 0.0 | ok | 340 | not supplied | 0 |
| `track2-text-scale-8` | 1 | gemini-3-flash | gemini-3-flash | text | minimal | 0.0 | ok | 340 | not supplied | 0 |

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 13 |
| Input tokens (billed) | 0 |
| Input tokens (cached) | 0 |
| Output tokens | 0 |
| Thinking tokens | 0 |
| Total tokens | 0 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$0.0000 over 13 of 13 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 0.00 h over 13 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

No cost audit on file names this run or its directory: an independently audited cost for this run is **not supplied**. The four audits checked are `reports/token-load-audit-2026-06-12.md`, `reports/r7-gaps-deltas-2026-09-11.md`, `reports/k-ladder-phase2-deltas-2026-09-12.md`, `reports/billing-reconciliation-2026-09-11.md`.

## 5. Registered conditions (13)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `image-canonical` | single-pass | none | 1 | — | 720 | 0.5814 [0.5352, 0.6286] | 0.6894 [0.6482, 0.7308] | 0.0942 |
| `image-exploratory-pure-positive-2hp` | single-pass | none | 1 | — | 823 | 0.5712 [0.5214, 0.6210] | 0.6784 [0.6264, 0.7229] | not supplied |
| `image-exploratory-pure-positive-4hp` | single-pass | none | 1 | — | 771 | 0.5985 [0.5510, 0.6465] | 0.7237 [0.6841, 0.7620] | 0.1642 |
| `image-exploratory-pure-positive-canon` | single-pass | none | 1 | — | 728 | 0.5699 [0.5233, 0.6141] | 0.6993 [0.6567, 0.7392] | 0.0942 |
| `image-plus-hp` | single-pass | none | 1 | — | 771 | 0.5985 [0.5503, 0.6494] | 0.7298 [0.6911, 0.7682] | 0.0942 |
| `image-pure-positive-canon` | single-pass | none | 1 | — | 736 | 0.5678 [0.5209, 0.6126] | 0.6949 [0.6508, 0.7362] | 0.0942 |
| `image-scale-4` | single-pass | none | 1 | — | 811 | 0.5837 [0.5313, 0.6318] | 0.6904 [0.6342, 0.7348] | 0.1336 |
| `image-scale-8` | single-pass | none | 1 | — | 770 | 0.5867 [0.5425, 0.6324] | 0.7044 [0.6651, 0.7422] | 0.1496 |
| `text-canonical` | single-pass | none | 1 | — | 897 | 0.6045 [0.5477, 0.6578] | 0.6504 [0.5920, 0.7017] | not supplied |
| `text-plus-hp` | single-pass | none | 1 | — | 885 | 0.5969 [0.5404, 0.6516] | 0.6545 [0.5981, 0.7041] | not supplied |
| `text-pure-positive-canon` | single-pass | none | 1 | — | 887 | 0.6045 [0.5477, 0.6586] | 0.6550 [0.5982, 0.7050] | not supplied |
| `text-scale-4` | single-pass | none | 1 | — | 882 | 0.6094 [0.5532, 0.6629] | 0.6545 [0.5980, 0.7043] | not supplied |
| `text-scale-8` | single-pass | none | 1 | — | 881 | 0.6070 [0.5511, 0.6619] | 0.6577 [0.6006, 0.7073] | not supplied |

Buffers on file (metres), by how many conditions carry that set:

- 13 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150

Tile-level MCC is on file for 7 of 13 condition(s).

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> Era-1 retest, H8 (phase2c). Single-pass replicate conditions (K passes per condition, metric = replicate-mean over runs), scored at the 14-buffer+MCC standard (Session 102 re-score, results/paper-eval/phase2/512px-14buf-mcc/). Era-1 340-tile, curator GT, 512px. Model of record: gemini-3-flash. detections points at the condition dir (the replicate-mean eval has no single geojson); n\_detections=None is expected. proposer\_pools = the leaf condition dirs (run\_\* = replicates).

### 5.4 Waived evaluations (30, 1 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **30 evaluation(s)** — not supplied — a bare-string entry, written before the waiver register carried reasons
  - `results/paper-eval/mcc/512px/p2c-image-canonical/evaluation.json`
  - `results/paper-eval/mcc/512px/p2c-image-plus-hp/evaluation.json`
  - `results/paper-eval/mcc/512px/p2c-image-pure-positive-canon/evaluation.json`
  - `results/paper-eval/mcc/512px/p2c-image-scale-4/evaluation.json`
  - `results/paper-eval/mcc/512px/p2c-image-scale-8/evaluation.json`
  - `results/paper-eval/mcc/512px/p2c-text-canonical/evaluation.json`
  - `results/paper-eval/mcc/512px/p2c-text-plus-hp/evaluation.json`
  - `results/paper-eval/mcc/512px/p2c-text-pure-positive-canon/evaluation.json`
  - `results/paper-eval/mcc/512px/p2c-text-scale-4/evaluation.json`
  - `results/paper-eval/mcc/512px/p2c-text-scale-8/evaluation.json`
  - `results/paper-eval/n1/512px-all-buffers/p2c-image-canonical/evaluation.json`
  - `results/paper-eval/n1/512px-all-buffers/p2c-image-plus-hp/evaluation.json`
  - … and 18 more under the same waiver (full list in `results/run-conditions.json`, this run's `_ignored_evals`)

## 6. Analyses that read this run (4)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `era1-leaderboard` | 13 of 82 | leaderboard | `H2`, `H1`, `H3`, `H4`, `H5`, `H7`, `H8`, `H9` | post-hoc | Results | `E25`, `E27`, `E28`, `E29`, `E30`, `E31`, `E36`, `E37`, `E58` | 2026-06-09T01:22:50Z | `results/era1-leaderboard` |
| `era1-single-pass-baseline-matrix` | 13 of 36 | leaderboard | `H1`, `H4`, `H5`, `H7`, `H8` | post-hoc | Results | `E25`, `E27`, `E28`, `E29`, `E30`, `E31`, `E36` | 2026-06-09T01:22:50Z | `results/paper-eval/n1/512px-14buf-mcc` |
| `null-exemplar-sensitivity-2026-09-13` | 13 of 235 | comparison | — | post-hoc | Appendix | — | 2026-09-16T06:43:40Z | `results/null-exemplar-sensitivity-2026-09-13/findings.md` |
| `uplift-supplement-flatten` | 13 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |

## 7. Findings documents (1)

| Document | Named by |
|---|---|
| `results/null-exemplar-sensitivity-2026-09-13/findings.md` | `null-exemplar-sensitivity-2026-09-13` |

## 8. Protocol errata

### 8.1 Registered as deviations (9)

Listed in the `deviations` field of an analysis that reads this run:

- **E25** — Modality manipulation not implemented — text-only conditions received images
- **E27** — Dual-track carry-forward from Phase 2a (OFAT deviation)
- **E28** — H5 instruction text adapted for Phase 2d (HN image references removed, OFAT simplification)
- **E29** — `reorder\_examples()` canonical-first was a no-op
- **E30** — Phase 2e tests 4 ordering conditions instead of preregistered 3
- **E31** — Deterministic runs at T=0.0 copied instead of re-executed
- **E36** — 340-tile production retest replaces 60-tile holdout evaluation (corrected 2026-07-30)
- **E37** — Proposer-Verifier (PV) pipeline — production implementation of registered H2 Condition B (corrected 2026-07-28)
- **E58** — Registered H2 proposer prompt (`propose\_brief`) never used — `detect\_brief-text` substituted in all PV experiments

### 8.2 Mentioning this run (1)

The entry's text names this run id or its directory path. A mention is a pointer to read the entry, not a claim that the erratum is about this run:

- **E81** — Undefined tile-level MCC published as `0.0` — nine conditions reported at the value the scale calls "random" where the metric is not computable, four more depressed by averaging an undefined pass into a mean

## 9. Documents and structure in the run directory

No `experiment_intent.md`, `evaluation.md`, `pre_launch_audit.md` or retrospective report under this directory.

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `track1-image-canonical` | image | `track1-image/canonical` |
| `track1-image-exploratory-pure-positive-2hp` | image | `track1-image-exploratory/pure-positive-2hp` |
| `track1-image-exploratory-pure-positive-4hp` | image | `track1-image-exploratory/pure-positive-4hp` |
| `track1-image-exploratory-pure-positive-canon` | image | `track1-image-exploratory/pure-positive-canon` |
| `track1-image-plus-hp` | image | `track1-image/plus-hp` |
| `track1-image-pure-positive-canon` | image | `track1-image/pure-positive-canon` |
| `track1-image-scale-4` | image | `track1-image/scale-4` |
| `track1-image-scale-8` | image | `track1-image/scale-8` |
| `track2-text-canonical` | text | `track2-text/canonical` |
| `track2-text-plus-hp` | text | `track2-text/plus-hp` |
| `track2-text-pure-positive-canon` | text | `track2-text/pure-positive-canon` |
| `track2-text-scale-4` | text | `track2-text/scale-4` |
| `track2-text-scale-8` | text | `track2-text/scale-8` |

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `f307c1932` |
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
- `inputs/vectors/bounds/full_evaluation_bounds.geojson`

Regenerate and drift-check with:

```bash
python3 scripts/generate_run_reports.py --all --write
python3 scripts/generate_run_reports.py --check
```
