<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — n1-pro-rerun-384

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `d9ea97c2e`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/h11/n1-pro-rerun-384` · **Registry status**: active · **Purpose**: Genuine-Pro re-run (E57): re-dispatch of the four anti-diagonal Pro corners as genuine gemini-3.1-pro-preview after the n1-outstanding originals were found to have billed as Flash. Supplies the four Pro anti-diagonal cells of the n1-baseline-matrix-384 leaderboard.

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `n1-pro-rerun-384` |
| Directory | `outputs/h11/n1-pro-rerun-384` |
| Registry status | active |
| Purpose | Genuine-Pro re-run (E57): re-dispatch of the four anti-diagonal Pro corners as genuine gemini-3.1-pro-preview after the n1-outstanding originals were found to have billed as Flash. Supplies the four Pro anti-diagonal cells of the n1-baseline-matrix-384 leaderboard. |
| Run type (derived) | single-pass |
| Primary hypothesis | H11 |
| Also informs | `H6` |
| Headline condition | not supplied |
| Headline rationale | not supplied |
| Historical aliases | — |
| Working-notes Obs | — |
| Registry notes | H11 genuine-Pro re-run (E57). The four anti-diagonal Pro corners (text/image x {HIGH-T=0.0, MEDIUM-T=0.7}) re-dispatched as genuine gemini-3.1-pro-preview (model\_version verified on all 8 passes) after the n1-outstanding originals were found to have billed as Flash. Completes the genuine Pro 2x2 x modality; supplies the four Pro anti-diagonal cells of the n1-baseline-matrix-384 leaderboard. |

## 2. Scope and evaluation frame

| Field | Value |
|---|---|
| Tile size (px) | 384 |
| Corpus | 4-map-gs |
| Ground-truth reference | curator |
| Test set id | era-2-487 |
| Test tiles | 487 |
| Bounds | `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` |
| Calibration set id | cal-20-384 |
| Calibration tiles | 20 |

## 3. Execution — passes on file

### 3.1 Proposer passes (12)

| Pool | Pass | Model used | Model requested | Modality | Thinking | Temp | Status | Tiles done | Dispatched | Retries |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| `pro-image-high-t0` | 1 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | image | high | 0.0 | ok | 487 | 487 | 0 |
| `pro-image-high-t0` | 2 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | image | high | 0.0 | ok | 487 | 487 | 0 |
| `pro-image-high-t0` | 3 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | image | high | 0.0 | ok | 487 | 487 | 0 |
| `pro-image-medium-t07` | 1 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | image | medium | 0.7 | ok | 487 | 487 | 0 |
| `pro-image-medium-t07` | 2 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | image | medium | 0.7 | ok | 487 | 487 | 0 |
| `pro-image-medium-t07` | 3 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | image | medium | 0.7 | ok | 487 | 487 | 0 |
| `pro-text-high-t0` | 1 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | text | high | 0.0 | ok | 487 | 487 | 0 |
| `pro-text-high-t0` | 2 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | text | high | 0.0 | ok | 487 | 487 | 0 |
| `pro-text-high-t0` | 3 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | text | high | 0.0 | ok | 487 | 487 | 0 |
| `pro-text-medium-t07` | 1 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | text | medium | 0.7 | ok | 487 | 487 | 0 |
| `pro-text-medium-t07` | 2 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | text | medium | 0.7 | ok | 487 | 487 | 0 |
| `pro-text-medium-t07` | 3 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | text | medium | 0.7 | ok | 487 | 487 | 0 |

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 12 |
| Input tokens (billed) | 50,144,442 |
| Input tokens (cached) | 42,512,178 |
| Output tokens | 433,275 |
| Thinking tokens | 94,939 |
| Total tokens | 50,672,656 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$105.4882 over 12 of 12 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 0.26 h over 12 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

No cost audit on file names this run or its directory: an independently audited cost for this run is **not supplied**. The four audits checked are `reports/token-load-audit-2026-06-12.md`, `reports/r7-gaps-deltas-2026-09-11.md`, `reports/k-ladder-phase2-deltas-2026-09-12.md`, `reports/billing-reconciliation-2026-09-11.md`.

## 5. Registered conditions (4)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `baseline-pro-image-high-t-0-0` | single-pass | none | 1 | — | not supplied | 0.6658 [0.6230, 0.7060] | 0.8339 [0.8055, 0.8610] | 0.8679 |
| `baseline-pro-image-medium-t-0-7` | single-pass | none | 1 | — | not supplied | 0.5950 [0.5496, 0.6381] | 0.8427 [0.8152, 0.8677] | 0.9108 |
| `baseline-pro-text-high-t-0-0` | single-pass | none | 1 | — | not supplied | 0.8045 [0.7678, 0.8371] | 0.8281 [0.7932, 0.8580] | 0.7900 |
| `baseline-pro-text-medium-t-0-7` | single-pass | none | 1 | — | not supplied | 0.7555 [0.7148, 0.7937] | 0.8230 [0.7882, 0.8530] | 0.7680 |

Buffers on file (metres), by how many conditions carry that set:

- 4 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150

Tile-level MCC is on file for 4 of 4 condition(s).

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> Genuine-Pro re-run of the four anti-diagonal Pro corners (E57). Re-dispatched as genuine gemini-3.1-pro-preview (per\_item\_metadata.model\_version verified on all 8 passes; committed 1cdf9438) after the n1-outstanding originals were found to have billed as Flash. Supplies the four Pro anti-diagonal cells of the n1-baseline-matrix-384 leaderboard, REPLACING the n1-outstanding (Flash) cells of the same corners. Realtime(+flex) dispatch -&gt; per-pass files are detections-&lt;prompt&gt;-3.1-pro-&lt;date&gt;.geojson (hyphen).

## 6. Analyses that read this run (5)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `diversity-dividend-384` | 4 of 22 | leaderboard | `H3` | confirmatory-with-deviation | Results | `None for the operating-point selection: the registered H3 analysis plan (osf/preregistration.md:519-521) specifies 'Generate threshold sweep curves', 'Identify optimal (N, threshold)', and 'Compare single-pass mean F1 vs voted F1' against the test tiles, so the best-operating- point characterisation is the preregistered method (not in-sample/E56 -- that rule governs the verifier prob_t diagnostics, a distinct case; see E56 Update 2026-06-06).`, `E49/E51 (T=0.7 production carry-forward temperature; HIGH thinking) -- the characterised configurations, carried forward from Phase 2b.`, `Production operating point reported alongside best: text 4-of-5, image 3-of-5 (the 55maps deployment thresholds); the best-minus-N5 delta is the within-test operating-point sensitivity.` | 2026-06-06T00:07:40Z | `results/diversity-dividend-384` |
| `h6-a06-decision-rule` | 4 of 8 | comparison | `H6` | post-hoc | Methods | `E74`, `E40` | 2026-08-17T13:02:16Z | `results/h6-registered-analyses` |
| `h6-a09-cost-gate` | 2 of 4 | diagnostic | `H6` | post-hoc | Methods | `E74`, `E57`, `E71` | 2026-09-08T01:53:31Z | `results/h6-registered-analyses` |
| `n1-baseline-matrix-384` | 4 of 18 | leaderboard | `H1`, `H7` | post-hoc | Results | `E57` | 2026-06-04T02:05:31Z | `results/paper-eval/n1/384px-14buf-mcc` |
| `uplift-supplement-flatten` | 4 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |

## 7. Findings documents (0)

No findings document on disk is named by an analysis that reads this run: a findings write-up for this run is **not supplied** from the register. § 6's `output_path` column gives each analysis's artefact directory.

## 8. Protocol errata

### 8.1 Registered as deviations (7)

Listed in the `deviations` field of an analysis that reads this run:

- **E40** — Gemini 3.1 Pro requires MEDIUM thinking — deviation from §8.2/§8.9 (clarified 2026-07-30)
- **E57** — H11 384px Pro/baseline detection metadata — model template default and output\_dir overrides
- **E71** — `n\_tiles\_processed` manifest column carries two semantics (dispatched vs completed) plus a verifier-row placeholder (GAP-8) — 15 passes with genuine coverage shortfalls, two live conditions carrying dead tiles as artificial false negatives
- **E74** — H6 (Flash→Pro transfer, Phase 4) — registered confirmatory hypothesis never executed; deferral never ratified
- **E49/E51 (T=0.7 production carry-forward temperature; HIGH thinking) -- the characterised configurations, carried forward from Phase 2b.** — not supplied
- **None for the operating-point selection: the registered H3 analysis plan (osf/preregistration.md:519-521) specifies 'Generate threshold sweep curves', 'Identify optimal (N, threshold)', and 'Compare single-pass mean F1 vs voted F1' against the test tiles, so the best-operating- point characterisation is the preregistered method (not in-sample/E56 -- that rule governs the verifier prob_t diagnostics, a distinct case; see E56 Update 2026-06-06).** — not supplied
- **Production operating point reported alongside best: text 4-of-5, image 3-of-5 (the 55maps deployment thresholds); the best-minus-N5 delta is the within-test operating-point sensitivity.** — not supplied

### 8.2 Mentioning this run (2)

The entry's text names this run id or its directory path. A mention is a pointer to read the entry, not a claim that the erratum is about this run:

- **E80** — No within-pass deduplication in the scoring path — a comparability confound on 155 of 333 conditions, preregistration-compliant but asymmetric across architectures
- **E83** — Tier-1 membership was decided by an order-dependent sequential rule, not by the clique its docstring promised — eight boards' tie sets revised to Hsu MCB, including one that published a sole leader it does not have

## 9. Documents and structure in the run directory

| Document class | Filename | Count |
|---|---|---:|
| per-pass/per-run intent | `experiment_intent.md` | 12 |

These classes are in Revision-Policy scope going forward (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope").

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `pro-image-high-t0` | image | `pro-image-high-t0` |
| `pro-image-medium-t07` | image | `pro-image-medium-t07` |
| `pro-text-high-t0` | text | `pro-text-high-t0` |
| `pro-text-medium-t07` | text | `pro-text-medium-t07` |

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `d9ea97c2e` |
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
- `inputs/vectors/bounds/384/full_evaluation_bounds.geojson`

Regenerate and drift-check with:

```bash
python3 scripts/generate_run_reports.py --all --write
python3 scripts/generate_run_reports.py --check
```
