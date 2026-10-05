<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — phase1-library

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `1d6f29db3`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `archive/outputs-pre-retest-60-tile/phase1-library` · **Registry status**: active · **Purpose**: Library construction (prereg 8.4.1 Step 1): the image-only baseline whose calibration-tile failures were mined for the hard examples (HP 05-08, HN 11-14; HN 18-29 for H9-C) that the image-modality production libraries still carry.

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `phase1-library` |
| Directory | `archive/outputs-pre-retest-60-tile/phase1-library` |
| Registry status | active |
| Purpose | Library construction (prereg 8.4.1 Step 1): the image-only baseline whose calibration-tile failures were mined for the hard examples (HP 05-08, HN 11-14; HN 18-29 for H9-C) that the image-modality production libraries still carry. |
| Run type (derived) | not supplied |
| Primary hypothesis | not supplied |
| Also informs | `H8`, `H9` |
| Headline condition | not supplied |
| Headline rationale | not supplied |
| Historical aliases | `Phase 1` |
| Working-notes Obs | — |
| Registry notes | Registered library-construction step (prereg 8.4.1 Step 1; execution checklist 'Phase 1: Library + Text', 2026-02-01): image-only baseline (library\_pure-positive-canon, 4 Canon+ and 3 null examples, detect\_image-only.md, T=1.0, minimal thinking), 5 passes over the 20 calibration tiles (cal-20-512), 100 calls. Its FP/FN register (fp-fn-register.md) selected HP 05-08 and HN 11-14 (Decision 4) and the H9-C pool HN 18-29 (6e772b55a), which every image-modality library still transmits. Never re-run; archived in 276e4ca80 under a manifest line ('superseded by retest/phase2a') that D40 corrects. No condition: the calibration-set F1 is a selection diagnostic (D41 precedent). Passes are laid out pass\_01..pass\_05. Registered 2026-10-05 (S160, ruling D40). |

## 2. Scope and evaluation frame

| Field | Value |
|---|---|
| Tile size (px) | 512 |
| Corpus | 4-map-gs |
| Ground-truth reference | curator |
| Test set id | cal-20-512 |
| Test tiles | 20 |
| Bounds | `inputs/vectors/bounds/calibration_bounds.geojson` |
| Calibration set id | not supplied |
| Calibration tiles | not supplied |

## 3. Execution — passes on file

### 3.1 Proposer passes (5)

| Pool | Pass | Model used | Model requested | Modality | Thinking | Temp | Status | Tiles done | Dispatched | Retries |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| `image-only-baseline` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | image | not supplied | 1.0 | ok | 20 | 20 | 0 |
| `image-only-baseline` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | image | not supplied | 1.0 | ok | 20 | 20 | 0 |
| `image-only-baseline` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | image | not supplied | 1.0 | ok | 20 | 20 | 0 |
| `image-only-baseline` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | image | not supplied | 1.0 | ok | 20 | 20 | 0 |
| `image-only-baseline` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | image | not supplied | 1.0 | ok | 20 | 20 | 0 |

## 4. Token load and audited cost

| Field | Value |
|---|---|
| Passes on file | 5 |
| Input tokens (billed) | 889,200 |
| Input tokens (cached) | 0 |
| Output tokens | 18,114 |
| Thinking tokens | 0 |
| Total tokens | 907,314 |
| Passes with no token record | 0 |
| `cost_usd` by basis | audited US$0.4989 (5) |
| Run total (range) | US$0.4989 |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 0.13 h over 5 pass(es) |

> **The cost above is on the audited basis, labelled per pass.** Since generator 0.8.0 (2026-10-03; PI ruling D11) each `cost_usd` is the pass's own tokens, recovery fragments included, priced by `scripts/lib_cost.price_usage` at the service tier the evidence supports; the pass's `cost_basis` says whether that is `audited`, an `audited-upper-bound` (tier unresolved, priced at the highest candidate), an `audited-lower-bound` (part of the pass is not in its metas: a cleanup overwrote one, or a fragment recorded nothing), `published`, `unrecorded`, or `unpriceable` (no date, or a model the rate card lacks), and its `cost_source` cites the evidence. It is no longer the pass meta's own `cost_estimate`, which priced at standard rates and omitted thinking tokens (`reports/token-load-audit-2026-06-12.md` § 1, § 2). A sum mixing upper and lower bounds is neither, so the run total is given as a range.

No cost audit on file names this run or its directory: an independently audited cost for this run is **not supplied**. The four audits checked are `reports/token-load-audit-2026-06-12.md`, `reports/r7-gaps-deltas-2026-09-11.md`, `reports/k-ladder-phase2-deltas-2026-09-12.md`, `reports/billing-reconciliation-2026-09-11.md`.

## 5. Registered conditions (0)

This run registers no conditions in `results/conditions-manifest.json`.

## 6. Analyses that read this run (0)

No registered analysis in `results/analyses-manifest.json` compares a condition of this run. That is a statement about the register, not about the run's usefulness: a run can inform the paper through a findings document without a register row.

## 7. Findings documents (0)

No findings document on disk is named by an analysis that reads this run: a findings write-up for this run is **not supplied** from the register. § 6's `output_path` column gives each analysis's artefact directory.

## 8. Protocol errata

### 8.2 Mentioning this run (1)

The entry's text names this run id or its directory path. A mention is a pointer to read the entry, not a claim that the erratum is about this run:

- **E10** — 50m recognition/localisation threshold — post-hoc narrowing of the registered HP definition (reclassified 2026-07-28)

## 9. Documents and structure in the run directory

No `experiment_intent.md`, `evaluation.md`, `pre_launch_audit.md` or retrospective report under this directory.

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `image-only-baseline` | image | `.` |

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `1d6f29db3` |
| Manifest extractor | `0.8.0` |
| Run row last extracted | `2026-10-05T02:00:04Z` |

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
- `inputs/vectors/bounds/calibration_bounds.geojson`

Regenerate and drift-check with:

```bash
python3 scripts/generate_run_reports.py --all --write
python3 scripts/generate_run_reports.py --check
```
