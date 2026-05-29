# Stage B Verifier-Temperature Accuracy Pilot — Report

> **Last revised**: 2026-05-29 (`gold-standard-v2` relocated to `outputs/gs/`). See [§ Changelog](#changelog) for revision history.

**Date:** 2026-04-27
**Author:** Claude Code (Opus 4.7) acting under Shawn's Stage B brief
**Compute:** sapphire (192.168.1.150)
**Status:** Pilot complete; outputs and report committed.

## 1. Background

Stage A (commit `f27842a5`) established that raising the verifier sampling
temperature from T=0.0 to T=0.5 or T=1.0 eliminates the 1.65% (10/607)
deterministic verifier-failure rate observed at T=0.0 on the canonical
4-of-5 consensus candidate set. Stage A measured *completion only*, not
accuracy. Stage B answers the natural follow-up: does T>0 degrade detection
accuracy (F1 / Matthews Correlation Coefficient (MCC)) on the same
candidates?

The operational case for raising the verifier temperature is strong only if
the answer is "no degradation". A small accuracy cost would have to be
weighed against the failure-rate elimination; a clear degradation would
shut down the proposal.

## 2. Method

### 2.1 Canonical operating point

The headline operating point matches the published canonical greedy cell
for `gold-standard-v2` on the 4-map gold-standard corpus (Era 2, 487-tile):
`(vote_t=4, prob_t=0.15, buffer=20m)`. Source of truth:
`results/leaderboard/cells/gold-standard-v2-greedy-v1-487tile.json` and the
matching extended-buffer evaluation at
`results/gold-standard-extended-buffer-sweep-era2/`.

### 2.2 Comparator parameters

Mirror the per-architecture leaderboard methodology
(`results/leaderboard/per-architecture/README.md`):

| Parameter | Value |
|---|---|
| Consensus input | `outputs/gs/gold-standard-v2/consensus/consensus-4of5.geojson` (607 features) |
| Vote threshold | `vote_t = 4` (already enforced by 4-of-5 consensus; explicit for config) |
| Probability sweep | `prob_t in {0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50}` |
| Buffers | `[20, 30, 40, 50, 100]` m |
| Bootstrap | 1,000 iterations, `seed=42`, tile-level resampling |
| MCC | tile-level, computed against bounds, 1,000-iteration bootstrap |
| Ground truth | `inputs/vectors/references/mounds-reference.geojson` (569 mounds) |
| Bounds | `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` (487 tiles) |

### 2.3 Pipeline

The driver `scripts/run_verifier_t_stage_b.py` calls
`scripts/materialise_pv_geojson.py:materialise` to filter the consensus
GeoJSON by `(vote_t, prob_t)` against each per-T `probabilities.json`, then
calls `scripts/evaluate_detections.py:_evaluate_condition` against the
gold-standard reference + bounds with `--mcc --bootstrap 1000`. The T=0.0
baseline was re-evaluated with **identical** parameters so that all three
cells share bootstrap seed, buffer set, and bounds.

For T=0.0 at `prob_t=0.15, buffer=20m` the re-evaluated F1 reproduces the
previously published canonical value (0.8536 [0.8206, 0.8825]) and
tile-level confusion (TP=181, TN=250, FP=8, FN=48), confirming the
pipeline is byte-equivalent to the published comparator.

### 2.4 Sample-size accounting

| T | n_results | n_materialised at prob_t=0.15 |
|---|---|---|
| 0.0 | 597 (10 verifier failures) | 371 |
| 0.5 | 607 (zero failures) | 377 |
| 1.0 | 607 (zero failures) | 376 |

T=0.0 has 10 fewer materialised candidates because the verifier never
returned a probability for those candidates (Obs 281 thinking-budget
exhaustion). The T>0 cells include those 10 candidates, with whichever
probability the verifier assigned.

## 3. Results

### 3.1 Headline cell

`(vote_t=4, prob_t=0.15, buffer=20m, 487-tile, 1,000 bootstrap, seed=42)`

| T | n | F1 mean (95% CI) | MCC mean (95% CI) | Sens | Spec |
|---|---:|---|---|---:|---:|
| 0.0 | 371 | **0.8536** [0.8206, 0.8825] | **0.7781** [0.7264, 0.8283] | 0.789 | 0.970 |
| 0.5 | 377 | **0.8645** [0.8316, 0.8924] | **0.7707** [0.7189, 0.8208] | 0.776 | 0.973 |
| 1.0 | 376 | **0.8434** [0.8081, 0.8736] | **0.7454** [0.6889, 0.7988] | 0.785 | 0.946 |

Per-T tile confusion at the headline cell:

| T | TP | TN | FP | FN |
|---|---:|---:|---:|---:|
| 0.0 | 181 | 250 |  8 | 48 |
| 0.5 | 178 | 251 |  7 | 51 |
| 1.0 | 180 | 244 | 14 | 49 |

### 3.2 Wider F1 sweep (buffer=20m, mean F1)

| prob_t | T=0.0 | T=0.5 | T=1.0 | dF1(0.5) | dF1(1.0) |
|---:|---:|---:|---:|---:|---:|
| 0.05 | 0.7615 | 0.7485 | 0.7356 | -0.0130 | -0.0259 |
| 0.10 | 0.8069 | 0.8303 | 0.8225 | **+0.0234** | **+0.0156** |
| 0.15 | 0.8536 | **0.8645** | 0.8434 | **+0.0109** | -0.0102 |
| 0.20 | 0.8507 | 0.8561 | 0.8422 | +0.0054 | -0.0085 |
| 0.25 | 0.8316 | 0.8176 | 0.8241 | -0.0140 | -0.0075 |
| 0.30 | 0.8316 | 0.8176 | 0.8211 | -0.0140 | -0.0105 |
| 0.40 | 0.8282 | 0.8130 | 0.8150 | -0.0152 | -0.0132 |
| 0.50 | 0.8146 | 0.7926 | 0.7915 | -0.0220 | -0.0231 |

Mean dF1 across all 40 cells (5 buffers x 8 prob_t):

- T=0.5 vs T=0.0: median -0.0137, mean -0.0041, 25/40 cells negative
- T=1.0 vs T=0.0: median -0.0102, mean -0.0100, 35/40 cells negative
- No cell has a 95% CI lying entirely below the T=0.0 CI (no clear
  degradation by the brief's decision rule).

### 3.3 MCC sweep (buffer-invariant)

| prob_t | T=0.0 | T=0.5 | T=1.0 | dMCC(0.5) | dMCC(1.0) |
|---:|---:|---:|---:|---:|---:|
| 0.05 | 0.5845 | 0.5263 | 0.5409 | -0.0582 | -0.0436 |
| 0.10 | 0.6902 | 0.6697 | 0.6783 | -0.0205 | -0.0119 |
| 0.15 | 0.7781 | 0.7707 | 0.7454 | -0.0074 | -0.0327 |
| 0.20 | 0.7781 | 0.7707 | 0.7554 | -0.0074 | -0.0227 |
| 0.25 | 0.7660 | 0.7480 | 0.7596 | -0.0180 | -0.0064 |
| 0.30 | 0.7660 | 0.7480 | 0.7558 | -0.0180 | -0.0102 |
| 0.40 | 0.7660 | 0.7446 | 0.7558 | -0.0214 | -0.0102 |
| 0.50 | 0.7679 | 0.7408 | 0.7545 | -0.0271 | -0.0134 |

MCC is uniformly slightly lower at T>0: dMCC negative in 8/8 cells for
both T=0.5 and T=1.0 (median dMCC = -0.0193 / -0.0127). However, every
T>0 MCC 95% CI overlaps the corresponding T=0.0 CI. The MCC drop is
small in absolute terms (worst case -0.058 at prob_t=0.05) and not
statistically distinguishable from sampling noise at any cell.

### 3.4 Decision-rule evaluation (the brief)

> **Flag any cell where the T=0.5 or T=1.0 95% CI lies entirely BELOW
> T=0.0's CI (clear degradation)**

**No cells flagged across F1 or MCC across the full 40-cell sweep.** All
T=0.5 / T=1.0 confidence intervals overlap the T=0.0 CI at every
(prob_t, buffer) combination tested.

## 4. Verdict

**F1 / MCC NOT degraded by the brief's CI-non-overlap test.** No
statistically clear (95% CI) degradation at any of the 40 (prob_t,
buffer) cells, including the canonical paper-load-bearing operating
point.

**Subtle directional finding worth flagging** (per the project's
"Research Finding Calibration" convention): MCC mean is uniformly lower
at T>0 (8/8 cells negative for both T=0.5 and T=1.0), and F1 mean is
lower at high prob_t (>= 0.25) for both T=0.5 and T=1.0. The deltas are
within sampling noise at every cell, but the sign-consistency across
8/8 MCC cells is itself non-trivial — it suggests T>0 introduces a
small, real, but statistically-undetectable accuracy cost on this
candidate set.

At the **headline cell** (vote_t=4, prob_t=0.15, buffer=20m):

- **T=0.5 marginally improves F1** (+0.0109) and marginally degrades
  MCC (-0.0074) versus T=0.0; both CI-overlapping.
- **T=1.0 marginally degrades both** F1 (-0.0102) and MCC (-0.0327)
  versus T=0.0; both CI-overlapping. T=1.0 has a notable rise in false
  positives at the tile level (FP=14 vs T=0.0's 8).

## 5. Recommendation

**Adopt T=0.5 as the production verifier default**, contingent on
Shawn's review of the directional MCC pattern in §3.3.

Rationale:

1. **Failure rate**: Stage A established T=0.5 has zero verifier
   failures vs T=0.0's 1.65% rate.
2. **Headline F1**: T=0.5 marginally *improves* F1 at the canonical
   operating point (0.8645 vs 0.8536) — a process improvement that does
   not silently cost F1.
3. **Headline MCC**: T=0.5's MCC drop of -0.0074 is the smallest of the
   T>0 options at this cell and is well within the T=0.0 95% CI.
4. **T=1.0 is dominated by T=0.5** at the headline cell on every metric
   (lower F1, lower MCC, more FPs). T=1.0 is not preferred.
5. **Sweep robustness**: Across the 40-cell grid, T=0.5 has the fewer
   negative-delta F1 cells (25/40 vs T=1.0's 35/40) and the smaller
   median absolute dF1.

**Caveats Shawn should weigh before adopting**:

- The MCC drop is small but sign-consistent (8/8 cells negative for
  T=0.5). With a larger candidate set this trend could become
  statistically detectable.
- This is a single-pass (k=1) verifier comparison. Production "K=10
  verifier+proposer" pipelines could amplify or attenuate the
  directional finding.
- The accuracy comparison was run on the same candidate set Stage A
  used, so the gold-standard 4-of-5 consensus is somewhat correlated
  with the T=0.0 verifier (the T=0.0 verifier was used to filter
  candidates that produced the existing gold standard's verified
  detections). This is a self-evaluation bias against T>0; a fresh,
  independent gold standard would tighten the comparison.

**Production-default config change is left as a recommendation only.**
No automated config rewrite has been performed; per Shawn's brief, that
remains his call.

## 6. Artefacts

| Path | Description |
|---|---|
| `scripts/run_verifier_t_stage_b.py` | Driver script (reusable) |
| `outputs/verifier-t-pilot/T{0.0,0.5,1.0}/materialised/vote4_prob{0.05..0.50}.geojson` | 24 materialised detection GeoJSONs |
| `results/verifier-t-pilot/T{0.0,0.5,1.0}/eval-vote4-prob{X}/{evaluation.json,csv,md}` | 24 per-cell evaluations with bootstrap CIs |
| `results/verifier-t-pilot/stage-b-summary.json` | Machine-readable cross-T summary |
| `results/verifier-t-pilot/stage-b-report.md` | This report |

## 7. Comparability with the canonical greedy cell

The canonical greedy cell at `(vote_t=4, prob_t=0.15, buffer=20m)`
records F1=0.8536, P=0.9272, R=0.7908 (without bootstrap CIs in that
file). The Stage B re-evaluation of T=0.0 reproduces F1=0.8536 with
P=0.9272 and R=0.7908 (Sens=0.789 in the tile-level confusion). The CI
and MCC values match the existing
`results/gold-standard-extended-buffer-sweep-era2/evaluation.json`
exactly, confirming pipeline byte-equivalence.

## 8. Next steps (open questions)

1. **K=10 production validation**. If T=0.5 is adopted, repeat this
   exercise on the K=10 verifier+proposer matrix to confirm the
   headline finding survives in the production architecture.
2. **Independent gold standard**. The current gold standard's verified
   detections were filtered with the T=0.0 verifier; this biases MCC
   slightly against T>0. A fresh gold standard built from a T-agnostic
   source would tighten the accuracy comparison.
3. **Verifier-disagreement diagnostic**. Compile a candidate-by-candidate
   table of `mound_probability` at T=0.0 / 0.5 / 1.0 to see whether the
   small directional MCC delta is concentrated in a small number of
   high-uncertainty candidates (and could be addressed by a per-candidate
   ensemble across temperatures). Out of scope for Stage B.

## Changelog

### 2026-05-29 — gold-standard-v2 relocated to outputs/gs/

**Refresh trigger**: H11 reorganisation — the `gold-standard-v2` run was moved
out of `outputs/h11/` to the new `outputs/gs/` umbrella (relocation landed in
commit `c5983adb`). Its `run_id` slug is unchanged (`gold-standard-v2`);
only the directory path moved.

**What changed**: every `outputs/h11/gold-standard-v2/…` path reference in this
document was repointed to `outputs/gs/gold-standard-v2/…`.

**What did NOT change**: no numerical results, tables, rankings, or findings —
this is a pure path relocation.

### 2026-04-27 — Original publication

Document first authored on 2026-04-27; see git history for substantive content.
This banner and changelog were added on 2026-05-29 (the first Revision-Policy
stub for this document) as part of the H11 reorganisation.
