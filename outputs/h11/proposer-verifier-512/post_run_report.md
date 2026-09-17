<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — proposer-verifier-512

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `22ffe6b43`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/h11/proposer-verifier-512` · **Registry status**: active · **Purpose**: not supplied

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `proposer-verifier-512` |
| Directory | `outputs/h11/proposer-verifier-512` |
| Registry status | active |
| Purpose | not supplied |
| Run type (derived) | proposer-verifier |
| Primary hypothesis | H11 |
| Also informs | `pv-strategy` |
| Headline condition | not supplied |
| Headline rationale | not supplied |
| Historical aliases | `Era 1` |
| Working-notes Obs | — |
| Registry notes | H11 (proposer-verifier, 512px). Absent from inventory. |

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

### 3.2 Verifier passes (1)

| Pool | Pass | Model used | Modality | Thinking | Temp | Status | Candidates verified | Retries |
|---|---:|---|---|---|---:|---|---:|---:|
| `verified-adversarial-text` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 140 | 0 |

Verifier rows report no tile count by design: verifier pass: operates on candidate crops, not tiles. The verifier meta records candidate ids (cand\_NNNN) in execution\_stats.completed\_items and candidate API items in per\_item\_metadata, so no tile-scale record exists to report. Completed crop count is in n\_candidates\_verified. (E71 Defect 2 / GAP-8, resolved E72 2026-08-02.)

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 1 |
| Input tokens (billed) | 241,780 |
| Input tokens (cached) | 0 |
| Output tokens | 25,802 |
| Thinking tokens | 0 |
| Total tokens | 267,582 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$0.0345 over 1 of 1 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 0.01 h over 1 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

No cost audit on file names this run or its directory: an independently audited cost for this run is **not supplied**. The four audits checked are `reports/token-load-audit-2026-06-12.md`, `reports/r7-gaps-deltas-2026-09-11.md`, `reports/k-ladder-phase2-deltas-2026-09-12.md`, `reports/billing-reconciliation-2026-09-11.md`.

## 5. Registered conditions (1)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `verified-adversarial-text` | proposer-verifier | verified | 1 | — | 72 | 0.1931 [0.1215, 0.2946] | 0.2160 [0.1413, 0.3248] | 0.2350 |

Buffers on file (metres), by how many conditions carry that set:

- 1 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150

Tile-level MCC is on file for 1 of 1 condition(s).

### 5.1 Condition caveats (1 condition(s), 1 distinct caveat(s))

Grouped by identical text: a caveat written once for a family of sibling cells is reproduced once, with every cell it applies to named. Nothing is elided.

- `verified-adversarial-text`
  SIDELINED (D1, Session 107): superseded by the clean Era-1 Stage-D PV grid (verified-adv-\* conditions on pv-diag-256 / retest-phase3a / -phase3a-high / -phase2b). Thin GAP-9 provenance, pool-unresolved, n=1. Data kept (archive-never-delete); excluded from era1-leaderboard.

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> Batch A residual (H11), thin Era-1 sibling of pv-384 at 512px / era-1-340. Only the adversarial-text verifier strategy was run here; 1 verified condition at its verifier-accepted operating point (Session 100, user-confirmed). proposer\_pools EMPTY: the proposer dir holds only detections.geojson with NO meta (GAP-9 Era-1 weak provenance), so no proposer pass is extractable; condition references the pool by string -&gt; benign pool-unresolved WARN. The 1 verifier\_pass is a real sidecar meta (verified-adversarial-text.meta.json, 140 items, 0 failures). The v2 replicate re-run is excluded -&gt; \_ignored\_evals at the deferred 3b close-out sweep. SIDELINED from the Era-1 leaderboard (Session 106 decision): thin GAP-9 provenance + n=1 -&gt; superseded by the planned clean Era-1 PV verifier run (Stage D, planning/era1-leaderboard-plan-2026-06-08.md). Data kept (archive-never-delete); excluded from the leaderboard cell set. | Pool annotation (2026-09-13, S153 Batch 1 item 2): as for proposer-verifier-384 — one un-numbered proposer pass at proposer/detections.geojson, empty proposer\_pools, pool named by prompt string; source\_run records this run as the pool's home. No metric, eval or detection changed.

### 5.4 Waived evaluations (4, 2 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **3 evaluation(s)** — not supplied — a bare-string entry, written before the waiver register carried reasons
  - `results/rescore-2026-05-31/proposer-verifier-512/verified-adversarial-text-v2-accepted/evaluation.json`
  - `results/rescore-2026-05-31/proposer-verifier-512/verified-adversarial-text-v2/evaluation.json`
  - `results/rescore-2026-05-31/proposer-verifier-512/verified-adversarial-text/evaluation.json`
- **1 evaluation(s)** — uplift-supplement pairing/gap-fill anchor (planning/uplift-supplement-2026-08-28.md): an input to the supplement's pairing tables, scored on the reference, buffer, and frame of the stratum it pairs with; not a registered condition and not cited by the paper. Waived by PI ruling 2026-09-07 (planning/reference-revision-2026-09-06.md, register-verifier debt).
  - `results/uplift-supplement/verifier-pairing/proposer-verifier-512__verified-adversarial-text/evaluation.json`

## 6. Analyses that read this run (2)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `uplift-supplement-flatten` | 1 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |
| `verifier-uplift-pairing` | 1 of 170 | comparison | `H2` | post-hoc | Appendix | — | 2026-09-12T06:04:30Z | `results/uplift-supplement/verifier-uplift.csv` |

## 7. Findings documents (0)

No findings document on disk is named by an analysis that reads this run: a findings write-up for this run is **not supplied** from the register. § 6's `output_path` column gives each analysis's artefact directory.

## 8. Protocol errata

No erratum in `docs/methodology/preregistration/protocol-errata.md` is registered against an analysis of this run, and none mentions the run or its directory.

## 9. Documents and structure in the run directory

No `experiment_intent.md`, `evaluation.md`, `pre_launch_audit.md` or retrospective report under this directory.

### 9.1 Registered pools

1 registered verifier-pass directory/directories; see `results/run-conditions.json` for the full list.

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `22ffe6b43` |
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
