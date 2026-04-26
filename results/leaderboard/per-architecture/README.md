# Per-architecture x per-era tier leaderboards

**Generated**: 2026-04-26 (Session 79 redesign)
**Scope**: 12-stratum matrix (3 eras x 4 architectures)

## Overview

This tree stratifies the burial-mound-detection corpus into a 12-cell matrix of (Era x Architecture) and builds parallel F1 and MCC tier leaderboards within each populated stratum, plus cross-architecture comparisons within and across Eras.

**Populated strata**: 7 (see directories below). **Empty strata**: 5 (with stub READMEs explaining the absence).

| Era | single-pass | consensus | single-pass+PV | pv |
|:---:|:---:|:---:|:---:|:---:|
| **1** | populated | populated | empty | empty |
| **2** | populated | populated | populated | populated |
| **3** | empty | populated | empty | empty |

## Methodology

### Tier-building algorithm

Each populated stratum runs the following pipeline (driver: `scripts/build_per_arch_redesign.sh`, library: `scripts/build_tiered_leaderboard.py`):

1. **Resolve conditions** from `planning/condition-inventory-with-s78.json`.
2. **Evaluate** each condition at all 5 buffers (20, 30, 40, 50, 100 m) with 1,000 stratified bootstrap iterations for F1/P/R 95% CIs and tile-level MCC + sensitivity + specificity (also 1,000 iterations).
3. **Select thresholds**: per condition, choose the consensus threshold maximising F1 at the 20 m primary buffer (metric-independent: F1 at 20 m is the operational point even when MCC is the tier-building metric).
4. **Pairwise permutation tests**: all C(N, 2) pairs with 10,000 permutations, seed=42, paired tile-swap (F1 path) or per-tile (TP, TN, FP, FN) classification swap (MCC path). MCC null distribution validated symmetric and zero-centred in `docs/methodology/mcc-permutation-validation-2026-04-25.md`.
5. **BH-FDR correction**: Benjamini-Hochberg adjusted p-values at q=0.05 (base) and q=0.01 (sensitivity).
6. **Greedy-clique tiering**: conditions sorted by score descending; each appended to the current tier if indistinguishable (BH-adjusted p >= q) from all current members; otherwise a new tier starts.

**F1 tier construction is per-buffer (Option A, 2026-04-26).** Per-cell thresholds are fixed at the primary buffer (20 m) via the `--threshold-buffer` flag of `build_tiered_leaderboard.py`; pairwise permutation tests and tier construction then run independently at each of 20 / 30 / 40 / 50 / 100 m. The F1 tier tables at the non-primary buffers therefore reflect genuine buffer-dependent reorganisation, not propagated 20 m results. MCC tier construction remains a single pass per stratum because the tile-level MCC permutation test is buffer-independent.

See `planning/leaderboard-construction-plan.md` for the full methodology rationale.

### F1 + MCC parallel tiers

Each populated stratum produces parallel tier tables under F1 and MCC. F1 is the canonical detection-quality metric (precision-recall harmonic mean at the matching buffer); MCC is the binary-classification metric over tile presence (buffer-invariant in this codebase). The pair is reported per the project's `feedback_mcc_with_f1` policy: report tile-level MCC alongside F1 wherever inputs support it.

MCC threshold selection still uses F1 at 20 m for cross-metric alignment — both F1 and MCC tier tables for the same stratum read off the same operational threshold per condition.

### Why the parallel tier tables can disagree

F1 and MCC weight detections differently. F1 counts mound-level matching (TP within buffer of GT mound) and is buffer-aware; MCC counts tile-level presence (any detection in any tile that has any GT mound) and is buffer-invariant. Strata where the bottom of the F1 ranking has high tile presence but low mound-level matching will see those conditions descend into MCC's lower tiers, while top-F1 conditions usually align with top-MCC.

### Tier stability across buffers

F1 tiers are constructed independently at each buffer (20 / 30 / 40 / 50 / 100 m) using per-cell thresholds optimised at the primary buffer (20 m) via the `--threshold-buffer` flag (Option A semantics). Each stratum's `tier_stability.md` reports the Spearman rank correlation between tier@20m and tier@30/40/50/100m; rho values are substantive — they surface buffer-dependent tier reorganisations rather than a tautology.

MCC tiers are identical across buffers by methodology — the tile-level MCC permutation test does not take a buffer argument, and the greedy-clique tiering sorts by a single buffer-independent MCC value per condition. Therefore each stratum's `tier_stability_mcc.md` reports rho = 1.0 across all non-primary buffers; this is correct, not degenerate.

**Headline F1 tier-stability summary** (across the 7 populated strata x 4 non-primary buffers; 22/28 buffer comparisons yielded a defined Spearman rho):

- Median Spearman rho: **+0.956**
- Range: +0.909 (`era2/single-pass` vs 30_vs_20) to +1.000 (`era1/single-pass` vs 30_vs_20)
- Strata with the largest cross-buffer F1 tier reorganisation (lowest per-stratum median rho): `era2/single-pass` (median rho = +0.909), `era1/consensus` (median rho = +0.944). (6 of 28 buffer comparisons returned undefined rho — one or both rank vectors had all ties; see the per-stratum tables.)

### q=0.01 sensitivity pass

Each tier table at q=0.05 has a parallel tier table at q=0.01 (`leaderboard_tiers_q01_<buf>m.md`). Larger Tier 1 sets at q=0.05 benefit from a stricter q=0.01 directional inspection — the tighter cut groups together only the conditions that pass a stricter test of indistinguishability.

### Within-stratum vs cross-stratum FDR

BH-FDR is applied **within stratum**: each (Era x Architecture x Buffer x Metric) family is corrected independently. Cross-stratum claims (e.g. "Era 1 best vs Era 2 best") have **inflated family-wise error rate** and are not statistically grounded. Use within-stratum claims for paper citations; treat cross-stratum claims as descriptive.

Also note that the Era 1 vs Era 2/3 comparison is across different tile grids (512 px vs 384 px); paired permutation is impossible without re-tiling. Era 2 vs Era 3 share the same grid (Era 3 is a 327-tile subset of Era 2's 487 tiles).

### Greedy clique vs alternatives

Greedy clique was chosen because it stops a tier at the first significant difference -- a more conservative grouping than the alternative connected-components algorithm (transitive closure of indistinguishability). Greedy clique matches the standard leaderboard-reporting convention used across the project's other tier tables. Alternatives exist; the choice is a point of methodological consistency rather than absolute correctness.

### Monte-Carlo precision

Pairwise tests at p <= 5/N (where N=10,000) are precision-limited; the true p might be much smaller. See `mc-precision-flags.md` for the catalog. If a paper-citation hinges on a flagged comparison, re-run that pair at N=100,000 to tighten the bound.

### Cross-architecture paired comparisons

Within each Era, proposer-config tuples (model, config_version, instruction_file, thinking, T, N, track, vote_t) that appear in 2+ architecture columns are tested pairwise on the shared tiles. The output answers the question "does adding the verifier (or moving from single-pass to consensus) help on this proposer?". See `cross-architecture-paired-era<N>_<metric>.md` per Era.

## Era definitions

| Era | Tiles | Tile size | Stride | GT mounds | Bounds file |
|:---:|:-----:|:---------:|:------:|:---------:|:-----------|
| **1** | 340 | 512 px | 448 px | 539 | `inputs/vectors/bounds/full_evaluation_bounds.geojson` |
| **2** | 487 | 384 px | 336 px | 435 | `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` |
| **3** | 327 | 384 px | 336 px | 319 | `inputs/vectors/bounds/384/h10_test_bounds.geojson` |

## Architecture definitions

| Architecture | Description | Threshold sweep |
|:---|:---|:---|
| `single-pass` | One stochastic detection pass per tile (K=1). No consensus, no verifier. | — |
| `consensus` | K stochastic passes + greedy-voting consensus at threshold vote_t. No verifier. | vote_t in {1..K} |
| `single-pass+PV` | One detection pass + one verifier pass. The detection GeoJSON is post-thresholded by the verifier's binary cut. | — |
| `pv` | K passes + greedy consensus + verifier pass, materialised at the 20 m-optimal (vote_t, prob_t) pair per cell. | Optimised both vote_t and prob_t |

## File guide

| File pattern | Description |
|:---|:---|
| `era<N>/<arch>/leaderboard_tiers_<buf>m.md` | F1 tier table at q=0.05 |
| `era<N>/<arch>/leaderboard_tiers_q01_<buf>m.md` | F1 tier table at q=0.01 (sensitivity) |
| `era<N>/<arch>/leaderboard_tiers_mcc_<buf>m.md` | MCC tier table at q=0.05 |
| `era<N>/<arch>/leaderboard_tiers_mcc_q01_<buf>m.md` | MCC tier table at q=0.01 (sensitivity) |
| `era<N>/<arch>/leaderboard_tiers_<...>.json` | Machine-readable tier JSONs (with pairwise tests) |
| `era<N>/<arch>/leaderboard_all_evaluations.json` | Full threshold x buffer sweep for the stratum |
| `era<N>/<arch>/tier_stability.md` | Spearman rho across buffers (F1) |
| `era<N>/<arch>/tier_stability_mcc.md` | Spearman rho across buffers (MCC) |
| `cross-architecture-era<N>_<buf>m_<metric>.md` | Flat cross-arch comparison within Era at buffer |
| `cross-architecture-paired-era<N>_<metric>.md` | Paired test of shared proposer-config tuples within Era |
| `mc-precision-flags.md` | Pairwise tests where p <= 5/N (precision-limited) |
| `headlines.md` | Top-3 leaders per (Era, arch, metric, q=0.05) cell |

## See also

- **Combined / cross-architecture tier tables**: `../combined/` — same per-buffer F1 + MCC + q=0.05/0.01 sensitivity machinery, but pooled across all architectures within each Era so a single Era-wide tier table identifies the overall best conditions regardless of architecture. Complements (does not replace) the within-architecture stratified tables in this directory.
- `planning/leaderboard-construction-plan.md` -- methodology rationale and the 2026-04-25 redesign addendum
- `docs/methodology/mcc-permutation-validation-2026-04-25.md` -- proof that the MCC null distribution is valid
- `docs/methodology/data-reproduction-2026-04-25.md` -- Session 78 shared-crops re-derivation provenance (prerequisite for the Era 2 PV stratum)

