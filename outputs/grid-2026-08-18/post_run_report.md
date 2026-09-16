<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — grid-2026-08-18

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `11e576e9c`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/grid-2026-08-18` · **Registry status**: active · **Purpose**: Post-hoc (E41-class) 2x2 crossing tile size (512/384 px) with tile overlap (12.5/50 %), proposer stage only, ten passes per cell, one configuration throughout. Tests whether the 384 px sweet spot reproduces under a single footprint, and whether extra passes substitute for extra overlap.

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `grid-2026-08-18` |
| Directory | `outputs/grid-2026-08-18` |
| Registry status | active |
| Purpose | Post-hoc (E41-class) 2x2 crossing tile size (512/384 px) with tile overlap (12.5/50 %), proposer stage only, ten passes per cell, one configuration throughout. Tests whether the 384 px sweet spot reproduces under a single footprint, and whether extra passes substitute for extra overlap. |
| Run type (derived) | mixed |
| Primary hypothesis | not supplied |
| Also informs | `H13` |
| Headline condition | grid-2026-08-18::g512-ov256-k10-c2-k8 |
| Headline rationale | Best F1@20 m of the four cells at K=10 (0.7518, tile-MCC 0.5897). Conditional on the absence of a precision stage: no verifier has run over any grid cell, so neither the tile-size ranking nor the overlap effect is unconditional until Phase 1 of the recall-levers programme executes. |
| Historical aliases | — |
| Working-notes Obs | — |
| Registry notes | Post-hoc (E41-class) 2x2 tile-size x overlap grid: 512/384 px crossed with 12.5/50 % overlap, detect\_brief-text, gemini-3-flash-preview, MINIMAL thinking, T=0.7, 10 passes per cell, 30,130 calls, $18.53 billed. Proposer stage only, consensus-only aggregation, NO verifier stage — both headline findings are conditional on that. Six parse-failed tiles recovered as additive one-tile passes and merged at preparation. Scoring chain: outputs/grid-2026-08-18/scoring/ (common four-way tile-union intersection carried on the era-2-487 grid) -&gt; results/grid-2026-08-18/. |

## 2. Scope and evaluation frame

| Field | Value |
|---|---|
| Tile size (px) | not supplied |
| Corpus | 4-map-gs |
| Ground-truth reference | curator |
| Test set id | grid-common-487 |
| Test tiles | 487 |
| Bounds | `outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson` |
| Calibration set id | not supplied |
| Calibration tiles | not supplied |

## 3. Execution — passes on file

### 3.2 Verifier passes (8)

| Pool | Pass | Model used | Modality | Thinking | Temp | Status | Candidates verified | Retries |
|---|---:|---|---|---|---:|---|---:|---:|
| `g384_ov048-union-k10-verify` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 1827 | 23 |
| `g384_ov192-k-ladder-k1-verify` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 1826 | 0 |
| `g384_ov192-k-ladder-k3-verify` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 2481 | 1 |
| `g384_ov192-k-ladder-k5-verify` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 2932 | 0 |
| `g384_ov192-union-k10-verify` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 3319 | 63 |
| `g384_ov192-union-k10-verify37` | 1 | gemini-3.7-flash | text | low | 0.0 | ok | 1 | 0 |
| `g512_ov064-union-k10-verify` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 1402 | 6 |
| `g512_ov256-union-k10-verify` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 2585 | 29 |

Verifier rows report no tile count by design: verifier pass: operates on candidate crops, not tiles. The verifier meta records candidate ids (cand\_NNNN) in execution\_stats.completed\_items and candidate API items in per\_item\_metadata, so no tile-scale record exists to report. Completed crop count is in n\_candidates\_verified. (E71 Defect 2 / GAP-8, resolved E72 2026-08-02.)

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 8 |
| Input tokens (billed) | 29,340,416 |
| Input tokens (cached) | 0 |
| Output tokens | 2,597,685 |
| Thinking tokens | 120 |
| Total tokens | 31,938,221 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$22.4633 over 8 of 8 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 1.61 h over 8 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

Audit and reconciliation reports whose text names this run or its directory — consult these for audited figures; a mention is a pointer, not a claim that the report audits this run in full:

- `reports/r7-gaps-deltas-2026-09-11.md`

## 5. Registered conditions (15)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `g384-ov048-k10-c1-k10` | consensus | consensus | 10 | k=10 | 582 | 0.6475 [0.5935, 0.6966] | not supplied | 0.3137 |
| `g384-ov048-k10-verified-p0.20-k7` | proposer-verifier | verified | 10 | k=7/pt=0.2 | 358 | 0.8677 [0.8335, 0.8957] | not supplied | 0.7751 |
| `g384-ov192-k1-verified-opmax` | proposer-verifier | verified | 1 | k=1/pt=0.2 | 482 | 0.8546 [0.8246, 0.8797] | 0.8658 [0.8376, 0.8896] | 0.8211 |
| `g384-ov192-k1-verified-p0.15-k1` | proposer-verifier | verified | 1 | k=1/pt=0.15 | 493 | 0.8540 [0.8244, 0.8787] | 0.8650 [0.8368, 0.8886] | 0.8079 |
| `g384-ov192-k10-c2-k10` | consensus | consensus | 10 | k=10 | 488 | 0.7205 [0.6749, 0.7618] | not supplied | 0.4909 |
| `g384-ov192-k10-verified-p0.15-k10` | proposer-verifier | verified | 10 | k=10/pt=0.15 | 400 | 0.8961 [0.8657, 0.9198] | not supplied | 0.7965 |
| `g384-ov192-k10-verified-p0.15-k10-era2b` | proposer-verifier | verified | 10 | k=10/pt=0.15 | 400 | 0.8886 [0.8575, 0.9133] | not supplied | 0.7903 |
| `g384-ov192-k10-verified37-p0.98-k10` | proposer-verifier | verified | 10 | k=10/pt=0.98 | 386 | 0.9140 [0.8853, 0.9366] | 0.9263 [0.8998, 0.9470] | 0.8239 |
| `g384-ov192-k10-verified37-p0.98-k10-era2b` | proposer-verifier | verified | 10 | k=10/pt=0.98 | 386 | 0.9062 [0.8769, 0.9293] | 0.9184 [0.8911, 0.9393] | 0.8102 |
| `g384-ov192-k3-verified-opmax` | proposer-verifier | verified | 3 | k=3/pt=0.15 | 450 | 0.8840 [0.8523, 0.9084] | 0.8933 [0.8649, 0.9156] | 0.8167 |
| `g384-ov192-k5-verified-opmax` | proposer-verifier | verified | 5 | k=5/pt=0.15 | 435 | 0.8905 [0.8595, 0.9149] | 0.8999 [0.8704, 0.9229] | 0.8139 |
| `g512-ov064-k10-c1-k8` | consensus | consensus | 10 | k=8 | 507 | 0.6759 [0.6239, 0.7237] | not supplied | 0.5383 |
| `g512-ov064-k10-verified-p0.15-k5` | proposer-verifier | verified | 10 | k=5/pt=0.15 | 383 | 0.8311 [0.7938, 0.8624] | not supplied | 0.7937 |
| `g512-ov256-k10-c2-k8` | consensus | consensus | 10 | k=8 | 426 | 0.7518 [0.7026, 0.7938] | not supplied | 0.5897 |
| `g512-ov256-k10-verified-p0.15-k9` | proposer-verifier | verified | 10 | k=9/pt=0.15 | 382 | 0.8815 [0.8518, 0.9073] | not supplied | 0.8011 |

Buffers on file (metres), by how many conditions carry that set:

- 9 condition(s): 20
- 6 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150

Tile-level MCC is on file for 15 of 15 condition(s).

### 5.1 Condition caveats (7 condition(s), 7 distinct caveat(s))

Grouped by identical text: a caveat written once for a family of sibling cells is reproduced once, with every cell it applies to named. Nothing is elided.

- `g384-ov192-k10-verified37-p0.98-k10`
  A9 — the fourth cell's GS calibration leg (~$3; card planning/gemini37-55map-2026-08-29.md:201, which commits (0.98, k10) as the 55-map fourth cell's carried point BEFORE any deployment scoring). This run's own Gemini-3 g384\_ov192 K=10 union (3,319 candidates) re-verified with gemini-3.7-flash: F1@20 0.914005, P 0.9637 / R 0.8692, tile-MCC 0.8239, 386 detections; +0.0179 over the 0.8961 text-B anchor at p = 0.0563. Registered here rather than under a 3.7 run because the condition belongs to the run that owns its proposer pool (PI ruling 6); the verification lives at outputs/grid-2026-08-18/verifier/g384\_ov192/verify\_37/. GOTCHA: this is a TEXT cell whose best point sits under the 'image\_best' key of results/gemini37-fourth-cell/gs-leg/analysis.json. The verifier\_config variant is recorded as 'v1' (the 3.7-arc convention) while this run's Gemini-3 siblings say 'adversarial-text'; same instruction file, same hash.
- `g384-ov192-k1-verified-p0.15-k1`
  CARRIED POINT (the transfer-tax column of ruling R2): prob\_t 0.15, k = K = 1, fixed before this evaluation rather than selected on it. The probability is 0.15 because that is the committed grid cells' threshold (g384-ov192-k10-verified-p0.15-k10), so the ladder stays a ladder. K-LADDER TIER E (approved by the PI on the evening of 2026-09-12 at US$5.02 for three rungs, hard stop US$7.00; controlling card planning/k-ladder-review-2026-09-11.md, gate results/k-ladder-2026-09-12/tier-e/pre\_launch\_audit.md). First-N rung: the union is passes 1 of pool outputs/grid-2026-08-18/g384\_ov192, built at US$0 by scripts/merge\_passes.py --passes 1 --sweep (union 1826 candidates at vote &gt;= 1, reproducing the PI's approved figure of 1826 EXACTLY, delta +0). Verified by one pass of the carried Gemini 3 verifier (ruling R1: no verifier swaps) at real-time flex tier, US$1.2531 on the audited flex basis (input x 0.25 + (output + thinking) x 1.50 per million). NOTE the verify path stamps cost\_basis 'list' with discount 1.0 even under flex and records the tier nowhere, so the stage meta's total\_cost\_usd is about twice the invoice (reports/r7-gaps-deltas-2026-09-11.md § 2.3). Scored on the board frame era2-b-487: curator reference, 14 buffers, 10,000 BCa draws, seed 42, MCC. CONSTRUCTION CAVEAT, recorded because it makes this rung's candidate universe wider than its K = 10 sibling's: the committed K = 10 rung of this family (outputs/grid-2026-08-18/verifier/g384\_ov192/union\_k10.geojson, 3319 candidates) was built by scripts/materialise\_grid\_unions.py, which filters the union to the grid study's common 487-tile carrier footprint, while this rung is a merge\_passes union on the pool's native footprint (a merge\_passes K = 10 union holds 3591, of which 3325 survive that filter). Scoring on the board frame excludes the out-of-frame candidates, so the F1 comparison across the ladder is like for like, but the universe the verifier priced is not. Put to the PI in reports/k-ladder-closeout-deltas-2026-09-12.md.
- `g384-ov192-k10-verified-p0.15-k10-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell g384-ov192-k10-verified-p0.15-k10 re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on grid\_common\_bounds.geojson stays the row's record.
- `g384-ov192-k10-verified37-p0.98-k10-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell g384-ov192-k10-verified37-p0.98-k10 re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on grid\_common\_bounds.geojson stays the row's record.
- `g384-ov192-k1-verified-opmax`
  IN-SAMPLE OPTIMUM (E56 class): the F1@20 argmax of this rung's own sweep, taken on the BOARD frame per ruling R2. The sweep was also run on the Era-2 frame full\_evaluation\_bounds.geojson and the two frames agree on the argmax for this rung. Tie-break where needed: highest F1@20, then lowest vote\_t, then lowest prob\_t (0 point(s) tied here). K-LADDER TIER E (approved by the PI on the evening of 2026-09-12 at US$5.02 for three rungs, hard stop US$7.00; controlling card planning/k-ladder-review-2026-09-11.md, gate results/k-ladder-2026-09-12/tier-e/pre\_launch\_audit.md). First-N rung: the union is passes 1 of pool outputs/grid-2026-08-18/g384\_ov192, built at US$0 by scripts/merge\_passes.py --passes 1 --sweep (union 1826 candidates at vote &gt;= 1, reproducing the PI's approved figure of 1826 EXACTLY, delta +0). Verified by one pass of the carried Gemini 3 verifier (ruling R1: no verifier swaps) at real-time flex tier, US$1.2531 on the audited flex basis (input x 0.25 + (output + thinking) x 1.50 per million). NOTE the verify path stamps cost\_basis 'list' with discount 1.0 even under flex and records the tier nowhere, so the stage meta's total\_cost\_usd is about twice the invoice (reports/r7-gaps-deltas-2026-09-11.md § 2.3). Scored on the board frame era2-b-487: curator reference, 14 buffers, 10,000 BCa draws, seed 42, MCC. CONSTRUCTION CAVEAT, recorded because it makes this rung's candidate universe wider than its K = 10 sibling's: the committed K = 10 rung of this family (outputs/grid-2026-08-18/verifier/g384\_ov192/union\_k10.geojson, 3319 candidates) was built by scripts/materialise\_grid\_unions.py, which filters the union to the grid study's common 487-tile carrier footprint, while this rung is a merge\_passes union on the pool's native footprint (a merge\_passes K = 10 union holds 3591, of which 3325 survive that filter). Scoring on the board frame excludes the out-of-frame candidates, so the F1 comparison across the ladder is like for like, but the universe the verifier priced is not. Put to the PI in reports/k-ladder-closeout-deltas-2026-09-12.md.
- `g384-ov192-k3-verified-opmax`
  IN-SAMPLE OPTIMUM (E56 class): the F1@20 argmax of this rung's own sweep, taken on the BOARD frame per ruling R2. The sweep was also run on the Era-2 frame full\_evaluation\_bounds.geojson and the two frames agree on the argmax for this rung. Tie-break where needed: highest F1@20, then lowest vote\_t, then lowest prob\_t (0 point(s) tied here). K-LADDER TIER E (approved by the PI on the evening of 2026-09-12 at US$5.02 for three rungs, hard stop US$7.00; controlling card planning/k-ladder-review-2026-09-11.md, gate results/k-ladder-2026-09-12/tier-e/pre\_launch\_audit.md). First-N rung: the union is passes 1,2,3 of pool outputs/grid-2026-08-18/g384\_ov192, built at US$0 by scripts/merge\_passes.py --passes 1,2,3 --sweep (union 2481 candidates at vote &gt;= 1, reproducing the PI's approved figure of 2481 EXACTLY, delta +0). Verified by one pass of the carried Gemini 3 verifier (ruling R1: no verifier swaps) at real-time flex tier, US$1.6989 on the audited flex basis (input x 0.25 + (output + thinking) x 1.50 per million). NOTE the verify path stamps cost\_basis 'list' with discount 1.0 even under flex and records the tier nowhere, so the stage meta's total\_cost\_usd is about twice the invoice (reports/r7-gaps-deltas-2026-09-11.md § 2.3). Scored on the board frame era2-b-487: curator reference, 14 buffers, 10,000 BCa draws, seed 42, MCC. CONSTRUCTION CAVEAT, recorded because it makes this rung's candidate universe wider than its K = 10 sibling's: the committed K = 10 rung of this family (outputs/grid-2026-08-18/verifier/g384\_ov192/union\_k10.geojson, 3319 candidates) was built by scripts/materialise\_grid\_unions.py, which filters the union to the grid study's common 487-tile carrier footprint, while this rung is a merge\_passes union on the pool's native footprint (a merge\_passes K = 10 union holds 3591, of which 3325 survive that filter). Scoring on the board frame excludes the out-of-frame candidates, so the F1 comparison across the ladder is like for like, but the universe the verifier priced is not. Put to the PI in reports/k-ladder-closeout-deltas-2026-09-12.md. THIS ROW IS ALSO THE CARRIED CELL: the sweep argmax lands exactly on the carried point (prob\_t 0.15, k = 3), so one cell serves both operating points and the transfer tax is 0.0000 by construction, not by measurement. No separate carried row is registered, because it would be the same detections file and the same evaluation.
- `g384-ov192-k5-verified-opmax`
  IN-SAMPLE OPTIMUM (E56 class): the F1@20 argmax of this rung's own sweep, taken on the BOARD frame per ruling R2. The sweep was also run on the Era-2 frame full\_evaluation\_bounds.geojson and the two frames agree on the argmax for this rung. Tie-break where needed: highest F1@20, then lowest vote\_t, then lowest prob\_t (0 point(s) tied here). K-LADDER TIER E (approved by the PI on the evening of 2026-09-12 at US$5.02 for three rungs, hard stop US$7.00; controlling card planning/k-ladder-review-2026-09-11.md, gate results/k-ladder-2026-09-12/tier-e/pre\_launch\_audit.md). First-N rung: the union is passes 1,2,3,4,5 of pool outputs/grid-2026-08-18/g384\_ov192, built at US$0 by scripts/merge\_passes.py --passes 1,2,3,4,5 --sweep (union 2932 candidates at vote &gt;= 1, reproducing the PI's approved figure of 2932 EXACTLY, delta +0). Verified by one pass of the carried Gemini 3 verifier (ruling R1: no verifier swaps) at real-time flex tier, US$2.0075 on the audited flex basis (input x 0.25 + (output + thinking) x 1.50 per million). NOTE the verify path stamps cost\_basis 'list' with discount 1.0 even under flex and records the tier nowhere, so the stage meta's total\_cost\_usd is about twice the invoice (reports/r7-gaps-deltas-2026-09-11.md § 2.3). Scored on the board frame era2-b-487: curator reference, 14 buffers, 10,000 BCa draws, seed 42, MCC. CONSTRUCTION CAVEAT, recorded because it makes this rung's candidate universe wider than its K = 10 sibling's: the committed K = 10 rung of this family (outputs/grid-2026-08-18/verifier/g384\_ov192/union\_k10.geojson, 3319 candidates) was built by scripts/materialise\_grid\_unions.py, which filters the union to the grid study's common 487-tile carrier footprint, while this rung is a merge\_passes union on the pool's native footprint (a merge\_passes K = 10 union holds 3591, of which 3325 survive that filter). Scoring on the board frame excludes the out-of-frame candidates, so the F1 comparison across the ladder is like for like, but the universe the verifier priced is not. Put to the PI in reports/k-ladder-closeout-deltas-2026-09-12.md. THIS ROW IS ALSO THE CARRIED CELL: the sweep argmax lands exactly on the carried point (prob\_t 0.15, k = 5), so one cell serves both operating points and the transfer tax is 0.0000 by construction, not by measurement. No separate carried row is registered, because it would be the same detections file and the same evaluation.

### 5.2 Scope overrides (6 condition(s), 1 distinct frame(s))

These conditions are scored on a frame other than the run's nominal scope in § 2 — the 327-vs-487 leakage trap the verifier exists to catch, disclosed per condition:

- `g384-ov192-k1-verified-opmax`, `g384-ov192-k1-verified-p0.15-k1`, `g384-ov192-k10-verified-p0.15-k10-era2b`, `g384-ov192-k10-verified37-p0.98-k10-era2b`, `g384-ov192-k3-verified-opmax`, `g384-ov192-k5-verified-opmax`
  bounds\_path = inputs/vectors/bounds/384/era2\_b\_intersection\_bounds.geojson, calibration\_set\_id = None, n\_calibration\_tiles = None, n\_test\_tiles = 487, test\_set\_id = era2-b-487

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> Pool annotation (2026-09-13, S153 Batch 1 item 2): the conditions name their proposer pool by PROMPT ('brief-text'); the physical passes are keyed by grid geometry (g384\_ov048 / g384\_ov192 / g512\_ov064 / g512\_ov256, each with run\_\*), which was never decomposed into proposer\_pools. source\_run records this run as the pool's home so the benign pool-unresolved WARN is machine-readable. No metric, eval or detection changed.

### 5.4 Waived evaluations (5, 3 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **3 evaluation(s)** — uplift-supplement K=1 anchor (planning/uplift-supplement-2026-08-28.md; scored 5bd514542): an input to the supplement's pairing tables, on the reference of the stratum it pairs with; not a registered condition and not cited by the paper. Waived by PI ruling 2026-09-07 (planning/reference-revision-2026-09-06.md, register-verifier debt).
  - `results/uplift-supplement/verifier-pairing/grid-2026-08-18__g384-ov048-k10-verified-p0_20-k7/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/grid-2026-08-18__g512-ov064-k10-verified-p0_15-k5/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/grid-2026-08-18__g512-ov256-k10-verified-p0_15-k9/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): g384-ov192-k10-verified-p0.15-k10's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/grid-2026-08-18__g384-ov192-k10-verified-p0_15-k10/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): g384-ov192-k10-verified37-p0.98-k10's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/grid-2026-08-18__g384-ov192-k10-verified37-p0_98-k10/evaluation.json`

## 6. Analyses that read this run (12)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `gemini37-fourth-cell-gs-leg-2026-08-31` | 2 of 2 | diagnostic | — | post-hoc | Methods | — | 2026-09-12T09:03:09Z | `results/gemini37-fourth-cell/gs-leg` |
| `gemini37-image-gs-2026-09-01` | 1 of 6 | comparison | `H1` | post-hoc | Results | — | 2026-09-12T09:03:09Z | `results/gemini37-image-gs-2026-09-01` |
| `gemini37-screen-2026-08-28` | 1 of 4 | comparison | — | post-hoc | Results | — | 2026-09-12T09:03:09Z | `results/gemini37-screen-2026-08-28` |
| `grid-postverifier-2026-08-18` | 4 of 4 | comparison | — | post-hoc | Results | `E41`, `E82` | 2026-09-12T09:03:09Z | `results/grid-2026-08-18` |
| `grid-tilesize-overlap-2026-08-18` | 4 of 4 | comparison | — | post-hoc | Results | `E41`, `E82` | 2026-09-12T09:03:09Z | `results/grid-2026-08-18` |
| `gs-era2-verified-board-2026-09-10` | 2 of 103 | leaderboard | `H2`, `H1` | post-hoc | Results | — | 2026-09-16T02:58:00Z | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/tiering_20m.json` |
| `image-b-modality-2026-08-28` | 1 of 2 | comparison | `H1` | registered-exploratory | Results | — | 2026-08-28T12:43:12Z | `results/image-b-gs-2026-08-28/analysis.json` |
| `k-ladder-2026-09-12` | 4 of 94 | comparison | `H3`, `H13` | post-hoc | Results | `E56`, `E85` | 2026-09-13T06:58:12Z | `results/k-ladder-2026-09-12/findings.md` |
| `null-exemplar-sensitivity-2026-09-13` | 6 of 235 | comparison | — | post-hoc | Appendix | — | 2026-09-16T06:43:40Z | `results/null-exemplar-sensitivity-2026-09-13/findings.md` |
| `stride-plateau-2026-08-25` | 4 of 9 | leaderboard | `H13` | post-hoc | Results | — | 2026-08-28T12:16:45Z | `results/stride-2026-08-25/plateau_analyses.json` |
| `uplift-supplement-flatten` | 9 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |
| `verifier-uplift-pairing` | 5 of 170 | comparison | `H2` | post-hoc | Appendix | — | 2026-09-12T06:04:30Z | `results/uplift-supplement/verifier-uplift.csv` |

## 7. Findings documents (4)

| Document | Named by |
|---|---|
| `results/image-b-gs-2026-08-28/findings.md` | `image-b-modality-2026-08-28` |
| `results/k-ladder-2026-09-12/findings.md` | `k-ladder-2026-09-12` |
| `results/null-exemplar-sensitivity-2026-09-13/findings.md` | `null-exemplar-sensitivity-2026-09-13` |
| `results/stride-2026-08-25/findings.md` | `stride-plateau-2026-08-25` |

## 8. Protocol errata

### 8.1 Registered as deviations (4)

Listed in the `deviations` field of an analysis that reads this run:

- **E41** — 384px tile size and full evaluation set used for Pro comparison
- **E56** — Verifier probability-threshold operating points are in-sample (test-set-selected), not calibrated
- **E82** — Bootstrap confidence intervals depart from Decision 10 on both method and iteration count — BCa replaced the registered percentile method undisclosed, its vectorised adapter transposed its axes until 2026-08-19, and the corpus runs at 10 000 iterations where E54 records 1 000
- **E85** — The temperature study's five consensus conditions were labelled N = 30 but read a 5-pass union — relabelled `consensus-{1..5}of5`; no measured value changes

## 9. Documents and structure in the run directory

| Document class | Filename | Count |
|---|---|---:|
| per-pass/per-run intent | `experiment_intent.md` | 52 |

These classes are in Revision-Policy scope going forward (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope").

### 9.1 Registered pools

8 registered verifier-pass directory/directories; see `results/run-conditions.json` for the full list.

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `11e576e9c` |
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
- `outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson`

Regenerate and drift-check with:

```bash
python3 scripts/generate_run_reports.py --all --write
python3 scripts/generate_run_reports.py --check
```
