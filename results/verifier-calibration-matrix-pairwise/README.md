# Session 78 Verifier Calibration Matrix — Pairwise Permutation Analysis

Pairwise paired-permutation tests across the seven Session 78 verifier-prompt
variants at four spatial-match buffers, producing Benjamini-Hochberg FDR
corrected tier tables that identify which verifier prompts are statistically
distinguishable from each other.

## Scope

**Variants (7)**: `adversarial`, `adversarial-text` (canonical), `brief`,
`brief-text`, `checklist`, `checklist-text`, `comparative`.

**Tracks (2)**: `image`, `text` (flash-high-image-n5 / flash-high-text-n5
candidate pools; see `outputs/h11/pv-diag-384/`).

**Buffers (4)**: 20, 30, 40, 50 metres.

**Evaluation scope**: 487-tile Era 2 (file
`inputs/vectors/bounds/384/full_evaluation_bounds.geojson`).

**Ground truth**: curator reference
`inputs/vectors/references/mounds-reference.geojson` (569 reference mounds,
EPSG:32635).

**Aggregation**: greedy consensus (project primary).

**Operating point**: each variant evaluated at its own per-cell best
`(vote_t, prob_t)` pair taken from
`results/leaderboard/cells/session-78-<track>-<variant>-487tile.json`.

## Methodology

### Test statistic

Micro-average F1 difference — observed F1(A) − F1(B) at the target buffer
— computed from tile-level TP/FP/FN counts with per-map Hungarian
matching at a tolerance equal to the buffer distance. This is the
project's standard F1 reporting convention (erratum E45).

### Paired permutation test

For each pair (A, B) the test:

1. Pre-computes per-tile (TP, FP, FN) for each variant using
   `lib_advanced_metrics.compute_per_tile_tp_fp_fn`.
2. For each of 10,000 permutations, independently swaps per-tile counts
   between A and B with probability 0.5, then re-aggregates micro-average
   F1 and computes the new difference — building a null distribution of
   F1 differences under the hypothesis of exchangeable condition labels
   within tiles.
3. Computes a two-sided p-value as the proportion of null differences
   whose absolute value is at least as extreme as the observed.

Seed: 42. Implementation reuses the project-standard
`scripts/pairwise_permutation_test.py:run_permutation_test`.

### Benjamini-Hochberg FDR correction

BH step-up applied **within each (track, buffer) family of 21 pairs** at
`q = 0.05`. Raw p-values are sorted, adjusted via `p × m / rank`, then
monotonised by cumulative minimum from the largest rank downward and
capped at 1.0. Implementation reuses
`scripts/apply_fdr_correction.py:apply_bh_correction`.

### Greedy-clique tier construction

Variants ranked by point F1 descending. Starting with the top-ranked
variant in tier 1, each subsequent variant joins the current tier iff its
paired test against **every** existing tier member is non-significant
after FDR. When a variant is significantly different from any member,
the tier closes and a new one opens with that variant.

### F1 + bootstrap CI

Per-variant F1 uses the same tile-level TP/FP/FN aggregation as the
permutation test. 95% percentile bootstrap CIs are computed by resampling
tiles with replacement (10,000 iterations, seed 42) and recomputing
micro-average F1 within each resample.

## Data provenance

- **Detection geojsons**: `results/verifier-calibration-matrix/<track>-<variant>-opt-20m.geojson`
  — one per (track, variant), materialised in Session 78 at each
  variant's 20 m-buffer optimum `(vote_t, prob_t)`.
- **Leaderboard cells**: `results/leaderboard/cells/session-78-<track>-<variant>-487tile.json`
  — per-cell sweep tables (5 vote_t × 10 prob_t × 4 buffer = 200 rows)
  plus `optima_per_buffer` block.
- **Reference**: `inputs/vectors/references/mounds-reference.geojson`
  (569 features, EPSG:32635).
- **Evaluation bounds**: `inputs/vectors/bounds/384/full_evaluation_bounds.geojson`
  (487 tiles, Era 2).

Each JSON artefact includes an `_metadata` block with
`run_timestamp_utc`, `git_commit`, `script_version`, `input_files`, the
permutation / bootstrap seeds and iteration counts, and the FDR method.

## Outputs

```text
results/verifier-calibration-matrix-pairwise/
├── README.md                              # this file
├── canonical-shared-crops-vs-old-comparison.md
├── scripts/
│   └── run_pairwise_matrix.py             # driver (UK English)
├── image/
│   ├── permutation_tiers_20m.{json,md}
│   ├── permutation_tiers_30m.{json,md}
│   ├── permutation_tiers_40m.{json,md}
│   └── permutation_tiers_50m.{json,md}
└── text/
    ├── permutation_tiers_20m.{json,md}
    ├── permutation_tiers_30m.{json,md}
    ├── permutation_tiers_40m.{json,md}
    └── permutation_tiers_50m.{json,md}
```

Each cell JSON contains: `_metadata`, per-variant `variant_metrics`,
`variants_by_f1_desc`, `tiers` (each tier listing member variants with
F1 + 95% CI + precision + recall + TP/FP/FN + N), full `pairwise_tests`
list (21 rows, with raw p, BH-adjusted p, significance flag), and
`canonical_vs_each` (the 6 canonical-vs-alternative rows).

## Headline findings

| track | buffer | canonical F1 | canonical tier | top tier members (F1-desc) | top F1 |
|-------|-------:|-------------:|---------------:|----------------------------|-------:|
| image | 20 m   | 0.7868       | 1              | adversarial; adversarial-text; comparative; brief; checklist; checklist-text; brief-text | 0.7884 |
| image | 30 m   | 0.8575       | 1              | adversarial; comparative; checklist-text; brief; checklist; adversarial-text; brief-text | 0.8671 |
| image | 40 m   | 0.8763       | 1              | adversarial; comparative; checklist-text; brief; checklist; adversarial-text | 0.8879 |
| image | 50 m   | 0.8810       | **2**          | adversarial; comparative; checklist-text; brief; checklist | 0.8971 |
| text  | 20 m   | 0.8634       | **2**          | comparative; adversarial; checklist; brief | 0.8846 |
| text  | 30 m   | 0.8875       | **2**          | comparative; adversarial; checklist; brief | 0.9111 |
| text  | 40 m   | 0.8875       | **2**          | comparative; adversarial; checklist; brief | 0.9111 |
| text  | 50 m   | 0.8875       | **2**          | comparative; adversarial; checklist; brief | 0.9111 |

**Interpretation**:

- **Image track, 20–40 m**: all seven variants (or near-all — brief-text
  drops out at 40 m) are statistically indistinguishable from the
  canonical `adversarial-text`. At these buffers, verifier-prompt
  variation does not produce F1 differences that survive FDR correction.
- **Image track, 50 m**: canonical falls into tier 2 alongside
  `brief-text`; five other variants (`adversarial`, `comparative`,
  `checklist-text`, `brief`, `checklist`) form a statistically superior
  tier 1. Largest single delta is `adversarial` − canonical = +0.0161.
- **Text track, all buffers (20, 30, 40, 50 m)**: canonical is in
  tier 2, alongside `checklist-text` and `brief-text`. Four variants
  (`comparative`, `adversarial`, `checklist`, `brief`) form a
  statistically superior tier 1. This is a robust pattern across all
  four buffers. Largest single delta at 20 m: `comparative` − canonical
  = +0.0213 (BH-adj p = 0.0014).
- **Is canonical in the top tier?** — only on the image track at 20 m,
  30 m, and 40 m buffers. At all four text-track buffers and at the
  50 m image-track buffer, the canonical is statistically outperformed
  by at least four alternatives.

### Which variants differ from canonical?

At each (track, buffer) cell, the variants that are statistically
**different** from canonical after BH-FDR (q = 0.05):

| track | buffer | sig-different variants | direction (all) |
|-------|-------:|-----------------------|-----------------|
| image | 20 m   | (none)                 | — |
| image | 30 m   | (none)                 | — |
| image | 40 m   | `brief-text`           | canonical > brief-text |
| image | 50 m   | adversarial; comparative; checklist-text; brief; checklist | alternative > canonical |
| text  | 20 m   | adversarial; checklist; comparative | alternative > canonical |
| text  | 30 m   | adversarial; checklist; comparative; brief | alternative > canonical |
| text  | 40 m   | adversarial; checklist; comparative; brief | alternative > canonical |
| text  | 50 m   | adversarial; checklist; comparative; brief | alternative > canonical |

The pattern is asymmetric: at finer buffers (20–30 m) the image-track
F1 signal is too noisy to distinguish canonical from any alternative;
at wider buffers (50 m) the canonical is statistically **outperformed**
by most alternatives. On the text track, the canonical is outperformed
at every buffer.

## Data-quality caveats

### 1. Shared-crops canonical refresh could not be executed

The original task prompt specified that a new canonical `adversarial-text`
probabilities file had been re-run against the shared-crops candidate
manifest (1994 image / 3686 text scored candidates) and lived at
`outputs/h11/pv-diag-384/flash-high-{image,text}-n5/{track}-t0.7/session-78-matrix/verified-adversarial-text/probabilities.json`.
These files were confirmed present on sapphire at job dispatch, but
**were deleted before the refresh pipeline could execute** (see
`canonical-shared-crops-vs-old-comparison.md` for details).

Consequently:

- The canonical cell used in this analysis is the pre-existing
  `results/leaderboard/cells/session-78-<track>-adversarial-text-487tile.json`,
  whose upstream probabilities are
  `outputs/h11/pv-diag-384/flash-high-<track>-n5/<track>-t0.7/verified-v1-n5/probabilities.json`.
  This pool uses a **different** (larger: 2016 / 3736) candidate crop
  set than the six alternatives, whose shared-crops pool covers 2017 /
  3736 candidates.
- The pairwise comparison is therefore **not strictly crop-parity**:
  the six alternatives ran on the shared-crops manifest, while the
  canonical used the historical verified-v1-n5 probabilities.
- The crop-set difference is small (2016 vs 2017 image; identical 3736
  text). Given this, the tier structure reported here is expected to
  closely approximate a true shared-crops-parity comparison, but we
  cannot directly verify this without the lost probabilities file.

**Action for user**: the deleted canonical probabilities are not
recoverable from local copies or backups; regenerating them requires
a Gemini API call (≤ 0.4 USD at the flex-tier rate for ~2017 + ~3736
candidates). No API call was made as part of this task per the no-API
constraint.

### 2. Missing candidates in each pool

Regardless of which probabilities file is used, the verifier always
fails to parse a small fraction of candidate responses. For the
canonical (verified-v1-n5):

- image: 2016 of 2017 candidates scored (1 unparseable)
- text: 3736 of 3736 candidates scored

For the six alternatives (shared-crops, per the earlier 14-cell
calibration matrix): candidate counts of 1994–2016 (image) and
3712–3736 (text) depending on variant-specific parser failures. These
gaps are shared across variants as tile-level outcomes — a candidate
that goes un-verified simply doesn't contribute to TP/FP/FN counts for
that variant at that tile. In a paired tile-swap test, a tile with
unequal candidate coverage between A and B still has valid (TP, FP,
FN) counts per variant, and the permutation respects the pairing.

### 3. Buffer-optimum approximation

For 13 of 14 cells the per-buffer optima at 20/30/40/50 m are
identical to the 20 m optimum — meaning the 20 m-optimum geojson
evaluates exactly at the correct operating point at each buffer.

**One exception**: `text-adversarial` has a 50 m optimum of
`(vote_t=3, prob_t=0.25)` versus the 20/30/40 m optimum of
`(vote_t=4, prob_t=0.20)`. Using the 20 m-optimum geojson at 50 m gives
F1 = 0.9087 while the 50 m-optimum would give F1 = 0.9089 — a
difference of 0.0002, which does not affect any tier placement.

### 4. Borderline BH-adjusted p-values

Several pairs sit near the FDR q = 0.05 threshold. Sensitivity of the
significance count to FDR level:

| track | buffer | sig @ q=0.01 | sig @ q=0.05 | sig @ q=0.10 |
|-------|-------:|-------------:|-------------:|-------------:|
| image | 20 m   | 0            | 0            | 0            |
| image | 30 m   | 0            | 0            | 0            |
| image | 40 m   | 0            | 1            | 2            |
| image | 50 m   | 0            | 5            | 6            |
| text  | 20 m   | 9            | 11           | 15           |
| text  | 30 m   | 10           | 12           | 13           |
| text  | 40 m   | 10           | 12           | 13           |
| text  | 50 m   | 10           | 12           | 13           |

Specific borderline (`0.03 ≤ BH-adj p ≤ 0.10`) cases worth awareness:

- **text@20 m, canonical vs brief**: BH-adj p = 0.091 (not significant
  at q = 0.05 but would be at q = 0.10). The canonical-vs-brief
  tier-membership finding (both brief is in tier 1 and canonical is in
  tier 2) is driven by brief's significance against other tier-2
  members, not this pair.
- **image@50 m, adversarial vs canonical**: BH-adj p = 0.0399 — just
  inside the q = 0.05 threshold; this is the sig pair that moves
  canonical from tier 1 to tier 2 at 50 m on the image track. A stricter
  q = 0.01 correction would keep canonical in tier 1.
- **text@30/40/50 m, canonical vs brief**: BH-adj p = 0.0471 — just
  inside the q = 0.05 threshold. Also borderline.

The image-track 50 m and image-track 40 m tier structures are the most
sensitive to the chosen q level. The text-track tier structure (canonical
in tier 2 at every buffer) is robust: it holds at both q = 0.01 and
q = 0.05.

### 5. Family-wise FDR scope

The BH-FDR correction is applied within each (track, buffer) family of
21 pairs. It is NOT applied across the full 168 pairs. This matches
the prompt specification and the convention in
`scripts/build_tiered_leaderboard.py`. Cross-buffer or cross-track
comparisons should be interpreted as exploratory.

### 6. Parallel-agent coexistence

This analysis ran on sapphire alongside a per-architecture leaderboard
agent (process group 2653020-…) that was concurrently executing
`build_tiered_leaderboard.py`. The two workloads touch disjoint
filesystem paths (the per-arch agent writes to
`results/leaderboard/per-architecture/`; this analysis writes to
`results/verifier-calibration-matrix-pairwise/`). CPU contention was
mitigated by running this analysis with only 8 worker processes
against sapphire's 24 logical cores.

## Reproducing this analysis

```bash
ssh sapphire
cd /home/shawn/Code/map-reader-llm/
.venv/bin/python results/verifier-calibration-matrix-pairwise/scripts/run_pairwise_matrix.py
```

Wall-clock: ~25 seconds on sapphire (all 168 pairwise tests + 56
bootstrap CIs executed in parallel).

## Related artefacts

- `planning/session-78-matrix-calibration-summary.md` — AUC/Brier/ECE
  crosstab across the 14 cells (from `compute_session78_calibration_matrix.py`).
- `docs/notes/reflections/working-notes.md` — Observation 277
  (canonical Pareto-dominance in calibration) and Obs 278+ (if authored).
- `results/leaderboard/cells/session-78-*.json` — per-cell threshold
  sweep (upstream of the materialised geojsons).
- `scripts/pairwise_permutation_test.py` — underlying permutation engine.
- `scripts/apply_fdr_correction.py` — BH step-up implementation.
- `scripts/build_tiered_leaderboard.py` — reference for
  greedy-clique tiering.
