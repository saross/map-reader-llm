# Post-Run Report — 55-Map Text Generalisation (retrospective)

**Run name**: `55maps-text-generalisation`
**Completed**: 2026-04-10 (start of pipeline); evaluation finalised over
the following days via the cleanup-retry loop described below.
**Host**: sapphire (per launch scripts)
**Orchestrator**: `scripts/55maps-overnight.sh` (bash, pre-publication-launcher)
**Config (retrospective reconstruction)**:
`configs/run-configs/55maps_text_generalisation_retrospective.yaml`

## Why this report is retrospective

The text-based 55-map generalisation run preceded the publishable
Python launcher (`scripts/run_generalisation.py`) by ~8 days. It was
driven by `scripts/55maps-overnight.sh` and its cleanup-retry
companions (`scripts/55maps-cleanup-stragglers.sh`,
`scripts/55maps-cleanup-analysis.py`). These are session-specific bash
scripts, not publishable kit. No `launch_manifest.json`,
`cost_manifest.json`, or `experiment_intent.md` were written at the
time.

This report reconstructs the equivalent information from what the run
left behind (per-run proposer `*.meta.json`, verifier `run.meta.json`,
threshold-sweep evaluation JSONs, the cleanup report, the Dawid-Skene
analysis) so the text run can be cited and reproduced symmetrically
with the image run's full audit trail. Numbers derived here are
labelled **(measured)** when read directly from meta files,
**(reconstructed)** when inferred from logs or archaeology, and
**(estimated)** when computed by scaling analogous runs.

## Top-line result

### Measured (against student-annotated ground truth)

From `results/55maps-generalisation/threshold-sweep-50m/threshold_sweep.json`
(bootstrap = 1,000, seed = 42, 50 m buffer, 1,000-iteration tile-level
resampling):

| Verifier | prob_t | F1 | 95% CI | Precision | Recall | n_detections |
|----------|-------:|---:|:------:|----------:|-------:|-------------:|
| v1 | 0.15 | 0.7898 | — | 0.858 | 0.732 | 4,068 |
| v1 | **0.20 (optimum)** | **0.7902** | [0.780, 0.801] | 0.863 | 0.729 | 4,030 |
| v2 | **0.15 (optimum)** | **0.7912** | [0.780, 0.803] | 0.862 | 0.731 | 4,047 |

The paper headline uses **v1** for cross-modality symmetry with the
image run. Reported F1 ≈ **0.790 @ 50 m** (optimum at 0.20, nearly
identical at 0.15).

### Corrected for annotator incompleteness

From `results/dawid-skene/dawid-skene-results.json` (2-annotator D-S
model; student GT + VLM v1 pipeline; threshold 0.15, buffer 50 m;
item set 5,348 = 3,490 matched + 1,280 student-only + 578 VLM-only):

| Method | F1 | Precision | Recall |
|--------|---:|---------:|------:|
| Measured (vs student GT, v1 @ 0.15) | 0.7898 | 0.8579 | 0.7317 |
| Simple correction (5 % FN) | 0.8084 | 0.9031 | 0.7317 |
| **Dawid-Skene posterior** | **0.8144** | **0.9031** | **0.7416** |

Δ F1 = **+0.0246** after correction. EM converged in 15 iterations.
VLM-only posterior P(true=1) = 0.318 → ~184 of 578 VLM-only items
estimated to be real mounds missed by student annotators.

### Side-by-side with the image run (Obs 256)

| Track | Completed | Measured F1 @ 50 m | D-S corrected F1 @ 50 m |
|-------|-----------|-------------------:|------------------------:|
| Text | 2026-04-10 | **0.790** | **0.814** |
| Image | 2026-04-18 | 0.771 | 0.795 |
| Δ (image − text) | | −0.019 | −0.019 |

The modality gap is preserved after D-S correction, consistent with
the Era 2 cross-modality finding (Obs 250–251).

## Cost accounting (partial)

### Verifier (measured)

From `outputs/55maps-generalisation/verified/run.meta.json`:

| Verifier | Duration (API) | Cost | Input tokens | Output tokens | Cached | Thinking |
|----------|---------------:|-----:|-------------:|--------------:|-------:|---------:|
| v1 (primary) | 65.7 min | **$12.43** | (see meta) | — | 0 | 0 (minimal thinking) |
| v2 (sensitivity) | 57.7 min | $12.89 | — | — | 0 | 0 |

### Proposer (estimated — meta files only show last retry)

The text run used an iterative retry loop orchestrated by
`scripts/55maps-cleanup-stragglers.sh`. On each logical "run" the
cleanup script re-invoked the proposer repeatedly until missing tiles
were recovered:

| Run | Initial tiles processed | Final tiles processed | Tiles recovered by retry |
|----:|-----------------------:|----------------------:|-------------------------:|
| 1 | 28 / 8,541 | 8,541 | 8,513 |
| 2 | 8,039 / 8,541 | 8,541 | 502 |
| 3 | 8,209 / 8,541 | 8,540 (1 missing) | 331 |
| 4 | 8,436 / 8,541 | 8,541 | 105 |
| 5 | 8,449 / 8,541 | 8,541 | 92 |

Source: `results/55maps-cleanup-report.json`.

The final `detections-*.meta.json` file in each `run_N/` directory
records only the **last retry pass's** token and cost totals (e.g.,
4,527 tokens and $0.00 for run_1). The aggregate cost across all
retries is not stored anywhere. **Per-pass aggregate proposer cost is
therefore unrecoverable from meta artefacts alone.**

**Estimate**: scaling from the Phase 3a text matrix
(`outputs/h11/pv-diag-384/flash-high-text-n5/`, text K=30 on 487 tiles
at HIGH + T = 0.7), per-run cost was ≈ $0.70 per 487 tiles. Scaling
to 8,541 tiles × 5 passes:

- Proposer estimate: 5 × (8541 / 487) × $0.70 ≈ **$61 (estimated)**
- Verifier v1 (measured): **$12.43**
- **Total estimated: ~$75** (v1-only); **~$88** including v2

The image run ran at $364.70 measured (3–4 × higher than the text
estimate) because the image pipeline sends 13 example images per
proposer call, whereas the text pipeline sends none (text-only
examples).

### What a future text rerun should track

If this run is reproduced under the publishable launcher, the
`cost_manifest.json` would provide the full per-stage / per-map /
unit-cost breakdown automatically. This retrospective report's
`(estimated)` proposer cost would then be superseded by measurement.

## Configuration (reconstructed from run_1 meta)

**Proposer**:

| Field | Value |
|-------|-------|
| config | `prompts/configs/detect_brief-text.json` |
| model | `gemini-3-flash` |
| instruction_file | `detect_brief-text.md` (text-only) |
| temperature | 0.7 |
| thinking_level | HIGH |
| include_example_images | **false** (text-only; examples are text descriptions) |
| example_count | 17 |
| max_output_tokens | 8192 |
| tile_size | 384 |
| passes (K) | 5 |

**Consensus**: greedy, 20 m radius, vote_threshold = **4-of-5** (one
level stricter than the image run's 3-of-5).

**Verifier (primary, v1)**:

| Field | Value |
|-------|-------|
| config | `prompts/configs/verify_adversarial-text.json` |
| model | `gemini-3-flash` |
| thinking_level | minimal |
| temperature | 0.0 |
| include_example_images | false |
| iterations | 1 |

**Evaluation**: 20 / 30 / 40 / 50 m buffers, bootstrap = 1,000, seed = 42,
prob_threshold = **0.15** (v1 optimum shared with image run; v1 @ 0.20
was the numerical peak with Δ F1 = +0.0004).

## Git provenance

- Launch commit (from run_1/meta → environment.git_commit):
  `d59798ac7f32c0f6a4a050eb40824fffea8ec029`
- Proposer script version at launch: `4_detect_mounds_batch.py` v6.0.0
- Verifier script version at launch: `run_pv.py` v1.0.0

## Timeline (measured)

| Event | UTC |
|-------|-----|
| Proposer run 1 start | 2026-04-10 00:48 |
| Proposer run 5 start | 2026-04-10 01:32 |
| (Subsequent cleanup/retry loop) | 2026-04-10 through ~2026-04-11 |
| Verifier v1 | 2026-04-10 02:25 → 03:31 (66 min) |
| Verifier v2 | 2026-04-10 XX:XX → XX:XX (58 min) |
| Threshold sweep (v1) | 2026-04-10 15:56 → 16:19 |

Precise end-to-end elapsed is not recovered from artefacts (the
cleanup loop was re-invoked interactively over hours).

## Scope (measured)

| Field | Value |
|-------|------:|
| Maps | 55 |
| Tiles | 8,541 |
| Proposer passes | 5 (after cleanup: 42,705 calls attempted, 1 tile permanently missing) |
| Consensus candidates (4-of-5) | 8,942 |
| Verifier v1 candidates scored | 8,939 |
| Final detections at v1 prob_t=0.15 | 4,068 |
| Final detections at v1 prob_t=0.20 | 4,030 (optimum) |
| Reference mounds (student-annotated) | 4,770 |

## Operational note: the retry / cleanup loop

The prior text run used a multi-pass cleanup/retry loop to recover
tiles that failed on the first proposer pass. At the scale of 55
maps × 5 passes, ~0.3–100 % of tiles would fail any single attempt
(Flex tier + long-running realtime calls); running to full coverage
required up to **3 retry passes per logical run** (observed:
"A-standard", "B-longer-backoff", "C-safemode"). The
`results/55maps-cleanup-report.json` shows 0.06–100 % recovery per
initial pass, with safe-mode (C) never required.

This was a valuable operational finding but the implementation — a
bash script outside the launcher — made aggregate cost and timing
hard to reconstruct. The publishable launcher's `max_retries=15` at
the call level plus its per-tile retry logic inside
`4_detect_mounds_batch.py` now handle equivalent recovery internally,
with all costs captured in one `cost_manifest.json` per run.

## Artefacts (unchanged since 2026-04-10)

| File | Status |
|------|--------|
| `outputs/55maps-generalisation/proposer/detect_brief-text/run_{1..5}/` | measured, last-retry pass only |
| `outputs/55maps-generalisation/consensus/consensus-4of5.geojson` | measured (8,942 features) |
| `outputs/55maps-generalisation/crops/candidate_manifest.json` | measured |
| `outputs/55maps-generalisation/verified/run.meta.json` | measured |
| `outputs/55maps-generalisation/verified/probabilities.json` | measured |
| `outputs/55maps-generalisation/verified-v2/` | measured (sensitivity analysis) |
| `results/55maps-generalisation/threshold-sweep-50m/` | measured (1,000-iter bootstrap) |
| `results/55maps-generalisation/v2-threshold-sweep-50m/` | measured |
| `results/55maps-generalisation/buffer_sensitivity.{csv,json}` | measured |
| `results/55maps-cleanup-report.json` | measured |
| `results/dawid-skene/` | measured |

## Limitations of this retrospective

Compared to the image run's post-run report, this one cannot
reconstruct:

- **Per-stage wall-clock timing of the proposer** — only verifier API
  time is recorded.
- **Aggregate proposer cost with measurement confidence** — only an
  estimate from analogous runs is available.
- **Per-tile failure rate across all retries** — the cleanup loop
  succeeded, but the per-try failure rates were not archived.
- **Cache hit rate** — not recorded (context caching was not used on
  text prompts because the cacheable preamble was below Gemini Flash's
  1,024-token minimum at the time).
- **Per-map cost attribution** — no cost_manifest to stratify by map.

These are exactly the fields the publishable launcher now records
automatically via `cost_manifest.json`. They are not recoverable for
this historical run.

The **F1 and per-tile evaluation** numbers are fully measured — those
are what goes in the paper. The retrospective limits only the cost
and operational accounting, not the headline scientific result.
