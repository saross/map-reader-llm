# Retracted H10/H12 v1 library-composition probe

**Archive date**: 2026-04-24 (Session 75, paper write-up Step 4 item 2)
**Retraction source**: `docs/notes/reflections/working-notes.md` Observation 235 (2026-04-14)
**Original working-paths**: `outputs/h10/{consensus, evaluation, verified, verifier-crops, wbf}/` + `results/h10/{sweep_results.json, statistical_analysis.json, verifier_independence_probe.{json,md}, k5_replicate_sweep.json, consensus_dedup_magnitude_diagnostic.json, wbf/}`

## ⚠️ Do NOT cite these numbers

The five-config library-composition / HP:HN-ratio probe
(pool_160 × {hp2hn6, hp4hn4, hp6hn2, hp8hn8, hp16hn16}, K=10, 2026-04-11)
was executed with a text-only proposer config
(`detect_brief-text_pool_160_*`) that has
`include_example_images: false`. Under that flag,
`scripts/4_detect_mounds_batch.py` skips the entire example loop —
the 17 library examples per pool (including the HP and HN crops
central to H12's preregistered question) are **never transmitted to
the API**. The library_hash difference between pools is bookkeeping
only.

Quoting Obs 235 directly:

> The "null result" is tautological because the library was not
> manipulated… The claimed library effect is physically impossible;
> the apparent F1 gap is driven by consensus-threshold differences in
> the manifests plus a residual attributable to estimation bias,
> model drift, and code-version differences.

None of the bootstrap CIs, pairwise permutation tests, verifier-
independence probe verdict, consensus dedup diagnostics, or K=5
replicate sub-sweeps in this archive support any claim about
calibration-pool composition, HP:HN ratio, or library size. The
F1 values observed (0.86–0.89 at post-verifier 2D optima) reflect
Gemini's run-to-run stochasticity on the same text-only prompt,
augmented by a verifier stage.

## One partially-preserved finding — the Obs 230 aggregation-method test

Obs 235 §"PARTIAL CORRECTION" explicitly retained one specific use of
this data:

| Aggregation | (vote_t, prob_t) | F1 [95 % CI] | Precision | Recall | n |
|-------------|------------------|--------------|-----------|--------|---|
| Greedy | (6, 0.15) | 0.885 [0.848, 0.917] | 0.913 | 0.859 | 300 |
| WBF variant C | (7, 0.15) | 0.880 [0.845, 0.911] | 0.899 | 0.862 | 306 |

Paired permutation: greedy ΔF1 over WBF = +0.005, p = 0.602, tied at
305 / 327 tiles. This is an **aggregation-method test**, valid on any
underlying detection set. The detections here happen to come from a
text-only K=10 proposer, but for the purpose of comparing WBF vs
greedy at fixed candidates, that is irrelevant. The file at
`results/h10/wbf/variant_c_vs_greedy_hp4hn4.json` (here at
`archive/h10-h12-v1-retracted-probe/results/h10/wbf/variant_c_vs_greedy_hp4hn4.json`)
is cited in the paper as Obs 230 evidence, explicitly framed as "WBF
vs greedy on a K=10 `detect_brief-text` text-only run" rather than
"on pool_160_hp4hn4 library".

## Clean analytical coverage of the library axis

The five configs originally in this retracted probe are collectively
covered by the sibling clean K=5 re-runs distributed across H8 v2
and H12 v2, all launched 2026-04-15 with `include_example_images:
true`:

| Config | Clean source | Greedy t=4 F1 | Reference |
|--------|--------------|:-------------:|-----------|
| pool_160_hp2hn6 | H12 v2 R1 (HN-heavy) | 0.708 | `outputs/h12-v2/r1-hn-heavy/` + `results/h12-v2/analysis_summary.md` |
| pool_160_hp4hn4 | H8 v2 Scale-8 (fresh) / H12 v2 R2 (H10 reuse) | 0.710 / 0.717 | `outputs/h8-v2/scale-8/`, `outputs/h10/evaluation-v2/pool_160_hp4hn4/` |
| pool_160_hp6hn2 | H12 v2 R3 (HP-heavy) | 0.688 | `outputs/h12-v2/r3-hp-heavy/` |
| pool_160_hp8hn8 | H8 v2 Scale-16 | 0.693 | `outputs/h8-v2/scale-16/` |
| pool_160_hp16hn16 | H8 v2 Scale-32 | 0.713 | `outputs/h8-v2/scale-32/` |

Clean summaries:

- `results/h8-v2/analysis_summary.md` — H8 v2 seven-contrast null after BH-FDR (Obs 238)
- `results/h12-v2/analysis_summary.md` — H12 v2 three-way null after BH-FDR (Obs 239)
- `results/h10/analysis_summary.md` — H10 v2 primary pool-size null under PV (Obs 236) + this archive's scope note

The clean cross-study synthesis appears in `results/meta-findings-summary.md`
Themes T2 (failure taxonomies) and T5 (library-axis closure).

## Archive contents

### `outputs/h10/evaluation/` — raw detections

- 5 configs × 10 runs × 3 files (geojson, tiles.json, meta.json) = 150 files
- Config name: `detect_brief-text_pool_160_{hp2hn6, hp4hn4, hp6hn2, hp8hn8, hp16hn16}`
- `include_example_images: false` in every meta.json
- Timestamps: 2026-04-11T08:57 through 2026-04-11T13:55 UTC
- Model: `gemini-3-flash-preview` (same as clean v2 runs — the only difference is the proposer config's include_example_images flag and the resulting payload)

### `outputs/h10/consensus/` — greedy consensus outputs

- 5 configs × 5 consensus tiers (1of10, 2of10, 4of10, 5of10, 6of10) = 25 files
- Built from the retracted raw detections on 2026-04-14

### `outputs/h10/verified/` — verifier probability outputs

- 5 configs × 2 files (probabilities.json, run.meta.json) = 10 files
- Verifier applied to the retracted candidate pool

### `outputs/h10/verifier-crops/` — candidate crops for verifier input

- 5 configs × 1 manifest + ~1,554 PNG crops per config = 7,771 files total
- Crops extracted from the retracted candidate pool

### `outputs/h10/wbf/` — WBF aggregation variants (all on retracted detections)

- 6 WBF variant directories at pool_160_hp4hn4:
  - `pool_160_hp4hn4/` (baseline)
  - `pool_160_hp4hn4_no_minsep/`
  - `pool_160_hp4hn4_variant_c/` (the Obs 230 comparison target)
  - `pool_160_hp4hn4_voteaware/`
  - `pool_160_hp4hn4_voteaware_v5/`
  - `pool_160_hp4hn4_voteaware_v6/`
- Each has `wbf_candidates.geojson`, `wbf_candidates.json`, `wbf_diagnostics.json` (plus `variant_c` has verified/ and a v2+ candidate file)

### `results/h10/` — aggregated analyses (must not cite for composition claims)

| File | What it reports |
|------|-----------------|
| `sweep_results.json` | 315-cell 2D vote × probability sweep across 5 configs |
| `statistical_analysis.json` | Bootstrap CIs + 10 pairwise permutation tests for 5 configs at (vote_t=6, prob_t=0.15) |
| `verifier_independence_probe.{json,md}` | Cross-config clustering + ICC(2,1) agreement + H-A verdict |
| `k5_replicate_sweep.json` | K=5 replicate consistency sub-sweep (240 cells) |
| `consensus_dedup_magnitude_diagnostic.json` | Cross-config clustering sensitivity to dedup radius |
| `wbf/sweep_results_pool_160_hp4hn4_variant_c.json` | WBF 2D sweep on hp4hn4 K=10 (text-only) |
| `wbf/variant_c_vs_greedy_hp4hn4.json` | WBF variant C vs greedy paired permutation on hp4hn4 (Obs 230 aggregation-method test) |
| `wbf/variant_c_vs_greedy_hp4hn4.metadata.json` | Resolved bootstrap-CI metadata sidecar for the file above (generated 2026-04-21 by the ci-metadata-registry work; describes retracted-data source) |

## Why preserved and not deleted

`CLAUDE.md` §"Unexpected Data as Discovery Opportunities":

> When an error, misconfiguration, or protocol deviation produces
> data from an unplanned region of the parameter space, the default
> response should be to **preserve the unexpected data and compare it
> to the intended results** before correcting the error and moving
> on.

And the project's archive-never-delete directive:

> Archive outdated files — do not delete. Use a single `archive/`
> folder at repo root with categorical subdirectories.

The retracted data is preserved so that (a) the Obs 230 partial-
preservation aggregation test remains citable, (b) the causal chain
from Obs 227 → Obs 234 → Obs 235 retraction is physically inspectable
in the working tree, and (c) future audits can confirm the
retraction was scoped correctly. These files are read-only reference
material, not an active analysis source.

## Background reading

- Obs 235 — formal retraction (working-notes.md ~line 9396)
- Obs 236 — clean v2 pool-size null (working-notes.md ~line 9745)
- Obs 238 — H8 v2 null (working-notes.md ~line 9830)
- Obs 239 — H12 v2 null (working-notes.md ~line 10044)
- Obs 230 — WBF vs greedy aggregation test (working-notes.md, earlier)
- Protocol errata E49 — H10 cold-start config deviation
- Protocol errata E45 — tile-level micro-average F1 permutation methodology
- `results/h10/analysis_summary.md` — the clean H10 v2 paper-citation summary that supersedes any narrative previously tied to this archive
