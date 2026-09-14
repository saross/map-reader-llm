<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — h13

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `5570447b9`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/h13` · **Registry status**: active · **Purpose**: Registered three-arm tile-overlap contrast (E75 remediation): arms B (25%) and C (50%) at 512 px, brief-text, three passes each. Arm A (12.5%) is the reused retest-phase2a::brief-text condition.

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `h13` |
| Directory | `outputs/h13` |
| Registry status | active |
| Purpose | Registered three-arm tile-overlap contrast (E75 remediation): arms B (25%) and C (50%) at 512 px, brief-text, three passes each. Arm A (12.5%) is the reused retest-phase2a::brief-text condition. |
| Run type (derived) | single-pass |
| Primary hypothesis | H13 |
| Also informs | — |
| Headline condition | not supplied |
| Headline rationale | not supplied |
| Historical aliases | — |
| Working-notes Obs | — |
| Registry notes | H13 overlap arms B (25%) and C (50%), 512 px brief-text, 3 passes each (+ one additive single-tile recovery in armB run\_1) plus the 5-tile smoke test. Arm A is the reused retest-phase2a::brief-text condition. Scoring chain: results/h13-overlap-2026-08-18/. |

## 2. Scope and evaluation frame

| Field | Value |
|---|---|
| Tile size (px) | 512 |
| Corpus | 4-map-gs |
| Ground-truth reference | curator |
| Test set id | h13-common-338 |
| Test tiles | 340 |
| Bounds | `outputs/h13/scoring/bounds/h13_common_bounds.geojson` |
| Calibration set id | not supplied |
| Calibration tiles | not supplied |

## 3. Execution — passes on file

### 3.1 Proposer passes (6)

| Pool | Pass | Model used | Model requested | Modality | Thinking | Temp | Status | Tiles done | Dispatched | Retries |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| `armb` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 1.0 | ok | 430 | 430 | 2 |
| `armb` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 1.0 | ok | 430 | 430 | 0 |
| `armb` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 1.0 | ok | 430 | 430 | 0 |
| `armc` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 1.0 | ok | 999 | 999 | 21 |
| `armc` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 1.0 | ok | 999 | 999 | 0 |
| `armc` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 1.0 | ok | 999 | 999 | 0 |

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 6 |
| Input tokens (billed) | 6,439,074 |
| Input tokens (cached) | 0 |
| Output tokens | 840,701 |
| Thinking tokens | 0 |
| Total tokens | 7,279,775 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$5.7416 over 6 of 6 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 0.20 h over 6 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

No cost audit on file names this run or its directory: an independently audited cost for this run is **not supplied**. The four audits checked are `reports/token-load-audit-2026-06-12.md`, `reports/r7-gaps-deltas-2026-09-11.md`, `reports/k-ladder-phase2-deltas-2026-09-12.md`, `reports/billing-reconciliation-2026-09-11.md`.

## 5. Registered conditions (6)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `arm-a-native-12-5` | single-pass | none | 3 | — | not supplied | 0.5576 [0.4948, 0.6175] | not supplied | 0.1477 |
| `arm-a-overlap-12-5` | single-pass | none | 3 | — | not supplied | 0.5580 [0.4949, 0.6175] | not supplied | 0.1058 |
| `arm-b-native-25` | single-pass | none | 3 | — | not supplied | 0.5222 [0.4692, 0.5718] | not supplied | 0.0123 |
| `arm-b-overlap-25` | single-pass | none | 3 | — | not supplied | 0.5198 [0.4607, 0.5765] | not supplied | 0.2579 |
| `arm-c-native-50` | single-pass | none | 3 | — | not supplied | 0.4067 [0.3667, 0.4461] | not supplied | 0.0342 |
| `arm-c-overlap-50` | single-pass | none | 3 | — | not supplied | 0.4024 [0.3477, 0.4583] | not supplied | 0.0593 |

Buffers on file (metres), by how many conditions carry that set:

- 6 condition(s): 20

Tile-level MCC is on file for 6 of 6 condition(s).

### 5.1 Condition caveats (3 condition(s), 1 distinct caveat(s))

Grouped by identical text: a caveat written once for a family of sibling cells is reproduced once, with every cell it applies to named. Nothing is elided.

- `arm-a-native-12-5`, `arm-b-native-25`, `arm-c-native-50`
  h13 overlap experiment, NATIVE-tiling arm (scored 2026-08-18 as the common-frame arm's comparator; results/h13-overlap-2026-08-18/native/). Registered 2026-09-07 under the PI's 'register what was scored' ruling (planning/reference-revision-2026-09-06.md, register-verifier debt 3); the per-pass inputs are gitignored outputs and are recorded in the evaluation's \_metadata.

### 5.2 Scope overrides (3 condition(s), 3 distinct frame(s))

These conditions are scored on a frame other than the run's nominal scope in § 2 — the 327-vs-487 leakage trap the verifier exists to catch, disclosed per condition:

- `arm-a-native-12-5`
  bounds\_path = outputs/h13/scoring/bounds/h13\_armA\_bounds.geojson, calibration\_set\_id = None, n\_calibration\_tiles = None, n\_test\_tiles = 340, test\_set\_id = h13-native-a
- `arm-b-native-25`
  bounds\_path = outputs/h13/scoring/bounds/h13\_armB\_bounds.geojson, calibration\_set\_id = None, n\_calibration\_tiles = None, n\_test\_tiles = 430, test\_set\_id = h13-native-b
- `arm-c-native-50`
  bounds\_path = outputs/h13/scoring/bounds/h13\_armC\_bounds.geojson, calibration\_set\_id = None, n\_calibration\_tiles = None, n\_test\_tiles = 999, test\_set\_id = h13-native-c

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> Pool annotation (2026-09-13, S153 Batch 1 item 2): the conditions name their proposer pool by PROMPT ('brief-text'); the per-arm passes live under scoring/{common,native}/arm{A,B,C}/run\_{1..3} while proposer\_pools registers only the two top-level armB/armC dirs. source\_run records this run as the pool's home. No metric, eval or detection changed.

## 6. Analyses that read this run (2)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `h13-overlap-2026-08-18` | 3 of 3 | comparison | `H13` | registered-exploratory | Results | `E75`, `E66`, `E54` | 2026-09-12T09:03:09Z | `results/h13-overlap-2026-08-18` |
| `uplift-supplement-flatten` | 6 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |

## 7. Findings documents (1)

| Document | Named by |
|---|---|
| `results/h13-overlap-2026-08-18/findings.md` | `h13-overlap-2026-08-18` |

## 8. Protocol errata

### 8.1 Registered as deviations (3)

Listed in the `deviations` field of an analysis that reads this run:

- **E54** — Bootstrap iteration count — preregistered 1 000 for primary F1, post-hoc 10 000 for narrow-effect analyses
- **E66** — `run\_study.py` → `run\_phase1.py` / `run\_phase2.py` orchestration substitution — formalising Decision 15
- **E75** — H13 (overlap/stride) — registered in-scope exploratory contrast silently dropped; arms B and C never executed

### 8.2 Mentioning this run (2)

The entry's text names this run id or its directory path. A mention is a pointer to read the entry, not a claim that the erratum is about this run:

- **E79** — Order-dependent tile assignment in `evaluate\_detections.py` — a scoring sensitivity of ~0.01 F1 on the 123 conditions whose detection artefact carries no `source\_tile`
- **E80** — No within-pass deduplication in the scoring path — a comparability confound on 155 of 333 conditions, preregistration-compliant but asymmetric across architectures

## 9. Documents and structure in the run directory

| Document class | Filename | Count |
|---|---|---:|
| per-pass/per-run intent | `experiment_intent.md` | 8 |

These classes are in Revision-Policy scope going forward (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope").

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `armb` | text | `armB` |
| `armc` | text | `armC` |

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `5570447b9` |
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
- `outputs/h13/scoring/bounds/h13_common_bounds.geojson`

Regenerate and drift-check with:

```bash
python3 scripts/generate_run_reports.py --all --write
python3 scripts/generate_run_reports.py --check
```
