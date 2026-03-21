# Production Retest Summary (340-Tile Corpus)

**Generated**: 2026-03-21
**Corpus**: 340 tiles (569 ground truth mounds, 4 map sheets)
**Baseline**: Phase 3 holdout set (60 tiles) — see `results/phase3d-pilot-results.md`
**Model**: Gemini 2.0 Flash (`gemini-2.0-flash`)
**Bootstrap**: 1000 iterations, tile-level resampling, seed 42
**Spatial matching**: 20 m tolerance

## Context

The Phase 3 holdout-set experiment (60 tiles) established initial parameter rankings but
lacked statistical power to distinguish closely-spaced conditions — wide confidence
intervals meant many pairwise comparisons were inconclusive (Obs 155). The production
retest re-runs the full factorial design on a 340-tile corpus (5.7x more tiles, 569
ground truth mounds across 4 map sheets), substantially narrowing confidence intervals
and enabling meaningful pairwise discrimination.

Single-pass phases (2a–2e) use K=1–3 runs per condition. Consensus phases (3a) use K=30
runs per temperature. All evaluation uses the same 20 m spatial matching pipeline
(`scripts/10_evaluate_detections_bootstrap.py`). Bootstrap confidence intervals for
individual runs are drawn from `results/pv/all-bootstrap-cis.json`.

## Phase 2a: H1 Modality (5 conditions)

| Condition | F1 | 95% CI | P | R | K |
|-----------|----:|:------:|----:|----:|---:|
| brief-text | 0.5518 | [0.477, 0.595] | 0.4336 | 0.7588 | 3 |
| brief-text-image | 0.5220 | [0.469, 0.564] | 0.4392 | 0.6432 | 3 |
| verbose-text | 0.5016 | [0.443, 0.556] | 0.3928 | 0.6939 | 3 |
| verbose-text-image | 0.5169 | [0.467, 0.560] | 0.4343 | 0.6382 | 3 |
| image-only | 0.4693 | [0.401, 0.502] | 0.3829 | 0.6061 | 3 |

**Key finding**: Text-only conditions outperform image-only, consistent with Phase 3
pilot results. Brief-text achieves the highest mean F1 (0.5518). The brief-text vs
image-only difference is significant (dF1 = +0.088, p = 0.004). Adding images to text
does not improve F1 and tends to reduce recall. No significant difference between
brief-text and verbose-text (p = 0.106), though brief-text trends higher.

## Phase 2b: H7 Temperature (2 tracks x 5 temperatures)

### Track 1 — Image

| Temperature | F1 | 95% CI | P | R | K |
|-------------|----:|:------:|----:|----:|---:|
| T0.0 | 0.5869 | [0.541, 0.633] | 0.4987 | 0.7130 | 3 |
| T0.3 | 0.5751 | [0.528, 0.612] | 0.4883 | 0.6994 | 3 |
| T0.7 | 0.5367 | [0.489, 0.580] | 0.4523 | 0.6599 | 3 |
| T1.0 | 0.5269 | [0.474, 0.561] | 0.4396 | 0.6574 | 3 |
| T1.3 | 0.4903 | [0.459, 0.540] | 0.4062 | 0.6184 | 3 |

**Key finding**: T0.0 achieves the best image-track F1. T0.0 is significantly better
than T0.7 (p = 0.002), T1.0 (p = 0.001), and T1.3 (p = 0.001). T0.0 vs T0.3 is not
significant (p = 0.30). Clear monotonic decline from T0.0 to T1.3.

### Track 2 — Text

| Temperature | F1 | 95% CI | P | R | K |
|-------------|----:|:------:|----:|----:|---:|
| T0.3 | 0.6065 | [0.553, 0.654] | 0.4908 | 0.7934 | 3 |
| T0.0 | 0.6048 | [0.547, 0.655] | 0.4870 | 0.7978 | 3 |
| T0.7 | 0.5842 | [0.521, 0.636] | 0.4606 | 0.7984 | 3 |
| T1.3 | 0.5442 | [0.487, 0.603] | 0.4252 | 0.7557 | 3 |
| T1.0 | 0.5335 | [0.432, 0.583] | 0.4148 | 0.7483 | 3 |

**Key finding**: T0.0 and T0.3 are essentially tied at the top (dF1 = -0.003,
p = 0.862). Both significantly outperform T1.0 (p = 0.001) and T1.3 (p = 0.004–0.006).
T0.7 is not significantly different from T0.0 or T0.3 but is significantly better than
T1.0 (p = 0.004). Optimal text-track temperature: T0.0–T0.3.

## Phase 2c: H8 Library Composition (2 tracks + exploratory)

### Track 1 — Image (5 conditions)

| Condition | F1 | 95% CI | P | R | K |
|-----------|----:|:------:|----:|----:|---:|
| plus-hp | 0.5983 | [0.546, 0.646] | 0.5091 | 0.7254 | 1 |
| scale-8 | 0.5872 | [0.542, 0.633] | 0.4993 | 0.7124 | 1 |
| scale-4 | 0.5841 | [0.534, 0.631] | 0.4864 | 0.7310 | 1 |
| canonical | 0.5755 | [0.528, 0.623] | 0.5056 | 0.6679 | 1 |
| pure-positive-canon | 0.5656 | [0.520, 0.608] | 0.4905 | 0.6679 | 1 |

**Key finding**: No significant pairwise F1 differences among any image-track library
conditions (all p > 0.19). The pipeline is robust to library composition on the image
track.

### Track 2 — Text (5 conditions)

| Condition | F1 | 95% CI | P | R | K |
|-----------|----:|:------:|----:|----:|---:|
| scale-4 | 0.6089 | [0.552, 0.659] | 0.4909 | 0.8015 | 1 |
| scale-8 | 0.6065 | [0.548, 0.656] | 0.4892 | 0.7978 | 1 |
| canonical | 0.6039 | [0.545, 0.654] | 0.4838 | 0.8033 | 1 |
| pure-positive-canon | 0.6039 | [0.546, 0.653] | 0.4859 | 0.7978 | 1 |
| plus-hp | 0.5963 | [0.540, 0.648] | 0.4802 | 0.7866 | 1 |

**Key finding**: Minimal sensitivity to library composition on the text track. The only
significant comparison is plus-hp vs scale-4 (dF1 = -0.013, p = 0.001), a tiny effect
driven by scale-4's marginally higher recall. All five conditions cluster within a
0.013 F1 range.

### Exploratory — HP Scaling (Image, pure-positive variants)

| Condition | F1 | 95% CI | P | R | K |
|-----------|----:|:------:|----:|----:|---:|
| pure-positive-4hp | 0.5985 | [0.550, 0.646] | 0.5084 | 0.7273 | 1 |
| pure-positive-2hp | 0.5721 | [0.521, 0.618] | 0.4738 | 0.7217 | 1 |
| pure-positive-canon | 0.5676 | [0.521, 0.609] | 0.4945 | 0.6660 | 1 |

**Key finding**: No significant F1 differences (all p > 0.09). Increasing hard-positive
examples does not reliably improve detection.

## Phase 2d: H5 Negation Text (2 tracks)

### Track 1 — Image

| Condition | F1 | 95% CI | P | R | K |
|-----------|----:|:------:|----:|----:|---:|
| terse | 0.6056 | [0.564, 0.646] | 0.5142 | 0.7365 | 1 |
| verbose | 0.6027 | [0.554, 0.647] | 0.5202 | 0.7161 | 1 |

**Key finding**: No significant difference (dF1 = +0.003, p = 0.85). Negation text
style has negligible effect on the image track.

### Track 2 — Text

| Condition | F1 | 95% CI | P | R | K |
|-----------|----:|:------:|----:|----:|---:|
| terse | 0.5984 | [0.537, 0.651] | 0.4850 | 0.7811 | 1 |
| verbose | 0.5834 | [0.525, 0.636] | 0.4887 | 0.7236 | 1 |

**Key finding**: No significant F1 difference (dF1 = +0.016, p = 0.376), though terse
negation text achieves significantly higher recall (p = 0.001). Terse trends better but
the F1 difference does not reach significance.

## Phase 2e: H4 Example Ordering (4 conditions)

| Condition | F1 | 95% CI | P | R | K |
|-----------|----:|:------:|----:|----:|---:|
| canonical-last | 0.6314 | [0.587, 0.672] | 0.5325 | 0.7755 | 1 |
| config-default | 0.6047 | [0.559, 0.653] | 0.5193 | 0.7236 | 1 |
| canonical-first | 0.5983 | [0.546, 0.646] | 0.5091 | 0.7254 | 1 |
| random | 0.5710 | [0.519, 0.618] | 0.4732 | 0.7199 | 1 |

**Key finding**: Canonical-last achieves the best single-run F1 of 0.6314 — the highest
non-consensus score in the entire production retest. Canonical-last is significantly
better than random (dF1 = +0.060, p = 0.002). Config-default also significantly beats
random (dF1 = +0.034, p = 0.046). Canonical-last vs config-default and canonical-first
are not significant (p = 0.158 and p = 0.124 respectively). Placing the canonical
example last in the few-shot sequence improves performance, consistent with recency bias
in the attention mechanism.

## Phase 3a: Consensus Voting

Detailed sweep results are in the per-track consensus analysis summaries:

- Image track: `results/retest/phase3a-consensus/track1-image/consensus-analysis-summary.md`
- Text track: `results/retest/phase3a-consensus/track2-text/consensus-analysis-summary.md`
- Replication (HIGH vs minimal thinking): `results/retest/phase3a-consensus/replication/consensus-analysis-summary.md`

### Cross-Track Comparison (Best N=30 consensus per track)

| Track | Temp | Threshold | F1 | 95% CI | P | R |
|-------|------|-----------|----:|:------:|----:|----:|
| Replication HIGH | — | 21-of-30 | 0.7705 | [0.725, 0.811] | 0.7846 | 0.7570 |
| Replication HIGH | — | 25-of-30 | 0.7583 | [0.710, 0.801] | 0.8646 | 0.6753 |
| Replication minimal | — | 25-of-30 | 0.7033 | [0.652, 0.750] | 0.6729 | 0.7365 |
| Text | T0.3 | 23-of-30 | 0.6921 | [0.637, 0.739] | 0.6261 | 0.7737 |
| Text | T0.7 | 24-of-30 | 0.6915 | [0.639, 0.741] | 0.6488 | 0.7403 |
| Image | T0.7 | 18-of-30 | 0.6909 | [0.649, 0.730] | 0.6935 | 0.6883 |
| Text | T1.0 | 22-of-30 | 0.6860 | [0.633, 0.735] | 0.6506 | 0.7254 |
| Image | T1.0 | 18-of-30 | 0.6803 | [0.636, 0.721] | 0.7166 | 0.6475 |
| Image | T0.3 | 22-of-30 | 0.6661 | [0.625, 0.706] | 0.6519 | 0.6809 |

**Key findings**:

- Consensus voting consistently improves over single-run baselines (+0.11 to +0.21 dF1).
- **Best consensus: Replication HIGH 21-of-30 at F1 = 0.7705** — the highest F1 in the
  entire study (non-PV). HIGH thinking with consensus produces a large gain over minimal
  thinking consensus (dF1 = +0.068, p = 0.001).
- Text and image tracks achieve comparable consensus F1 (~0.69), but via different
  precision-recall trade-offs: image consensus is higher precision, text consensus is
  higher recall.
- Image-track consensus peaks at T0.7 (F1 = 0.6909), while text-track consensus peaks
  at T0.3 (F1 = 0.6921) — both outperforming T1.0.
- Consensus significantly outperforms the best single-pass condition: image consensus
  T0.7 18-of-30 vs canonical-last single-pass gives dF1 = +0.060 (p = 0.001).

## Phase 3a-HIGH Text Track

**Status**: 90/90 runs complete (30 runs x 3 temperatures). Bootstrap CIs computed for
all 90 runs.

| Temperature | Mean F1 | P | R | K |
|-------------|--------:|----:|----:|---:|
| T0.3 | 0.4776 | 0.3450 | 0.7797 | 30 |
| T0.7 | 0.4248 | 0.2948 | 0.7641 | 30 |
| T1.0 | 0.4107 | 0.2829 | 0.7534 | 30 |

**Key finding**: HIGH-thinking single-pass runs on the text track produce *substantially
worse* F1 than minimal-thinking runs (cf. Phase 3a text T0.3 at F1 = 0.610 vs HIGH T0.3
at F1 = 0.478). This replicates the Phase 3d pilot finding that HIGH thinking degrades
single-pass precision by generating verbose, over-inclusive detections. However, the
replication consensus results (above) show that HIGH thinking *recovers dramatically*
under consensus voting — the diversity of HIGH-thinking runs provides the variance that
consensus needs to filter signal from noise.

## Phase 3c: H9 Diversity (Text Track)

**Status**: 100/100 output runs complete (20 profiles x 5 runs). Bootstrap CIs computed
for 60/100 runs. Image track: 83/100 output runs complete.

Partial results from the 60 bootstrapped text-track runs across 20 diversity profiles
(4 strategy groups: A = prompt permutation, B = vocabulary substitution,
D = temperature diversity, E = example permutation):

| Strategy Group | Profiles | Runs (bootstrapped) | Mean F1 |
|----------------|----------|---------------------|--------:|
| A (prompt) | h9-A-p1 to p5 | 15 | 0.4227 |
| B (vocabulary) | h9-B-v1 to v5 | 14 | 0.4105 |
| D (temperature) | h9-D-t1 to t5 | 18 | 0.4335 |
| E (example) | h9-E-p1 to p5 | 13 | 0.4217 |

**Key finding**: All diversity profiles produce single-run F1 values substantially below
the canonical single-pass conditions (F1 ~0.42 vs ~0.55–0.61), as expected since
diversity profiles deliberately deviate from optimised parameters. The value of these
runs lies in their consensus-voting potential — whether diverse pools outperform
homogeneous pools at the same pool size remains to be tested once all bootstrap CIs are
available (Obs 148 re: variance stabilisation). Full analysis is deferred until all 100
runs are bootstrapped.

[PENDING: Consensus voting sweep over diversity pools]
[PENDING: Bootstrap CIs for remaining 40 text-track runs]

## Pairwise Comparison Highlights

24 significant comparisons (p < 0.05, raw) out of 70 total pairwise tests. FDR
correction is deferred until all experimental data are available.

### Phase 2a — H1 Modality (3 significant)

| Comparison | dF1 | p |
|------------|----:|---:|
| brief-text > image-only | +0.088 | 0.004 |
| brief-text-image > image-only | +0.065 | 0.006 |
| verbose-text-image > image-only | +0.063 | 0.004 |

### Phase 2b T1 — H7 Temperature, Image (6 significant)

| Comparison | dF1 | p |
|------------|----:|---:|
| T0.0 > T0.7 | +0.050 | 0.002 |
| T0.0 > T1.0 | +0.064 | 0.001 |
| T0.0 > T1.3 | +0.085 | 0.001 |
| T0.3 > T1.0 | +0.050 | 0.006 |
| T0.3 > T1.3 | +0.071 | 0.001 |
| T0.7 > T1.3 | +0.035 | 0.042 |

### Phase 2b T2 — H7 Temperature, Text (5 significant)

| Comparison | dF1 | p |
|------------|----:|---:|
| T0.0 > T1.0 | +0.093 | 0.001 |
| T0.0 > T1.3 | +0.057 | 0.004 |
| T0.3 > T1.0 | +0.096 | 0.001 |
| T0.3 > T1.3 | +0.060 | 0.006 |
| T0.7 > T1.0 | +0.072 | 0.004 |

### Phase 2c T2 — H8 Library, Text (1 significant)

| Comparison | dF1 | p |
|------------|----:|---:|
| scale-4 > plus-hp | +0.013 | 0.001 |

### Phase 2e — H4 Ordering (2 significant)

| Comparison | dF1 | p |
|------------|----:|---:|
| canonical-last > random | +0.061 | 0.002 |
| config-default > random | +0.034 | 0.046 |

### Phase 3a T1 — Consensus Voting, Image (2 significant)

| Comparison | dF1 | p |
|------------|----:|---:|
| T0.3 > T1.0 | +0.075 | 0.001 |
| T0.7 > T1.0 | +0.054 | 0.008 |

### Phase 3a T2 — Consensus Voting, Text (2 significant)

| Comparison | dF1 | p |
|------------|----:|---:|
| T0.3 > T0.7 | +0.038 | 0.024 |
| T0.3 > T1.0 | +0.071 | 0.001 |

### Phase 3a — Cross-Condition (3 significant)

| Comparison | dF1 | p |
|------------|----:|---:|
| minimal > high (single-run) | +0.139 | 0.001 |
| consensus image T0.7 18-of-30 > canonical-last single-pass | +0.060 | 0.001 |
| HIGH consensus 21-of-30 > minimal consensus 25-of-30 | +0.068 | 0.001 |

## Best Configurations (Non-PV)

Top 10 configurations across all phases, ranked by F1:

| Rank | Configuration | F1 | 95% CI | P | R |
|-----:|---------------|----:|:------:|----:|----:|
| 1 | Replication HIGH consensus 21-of-30 | 0.7705 | [0.725, 0.811] | 0.7846 | 0.7570 |
| 2 | Replication HIGH consensus 25-of-30 | 0.7583 | [0.710, 0.801] | 0.8646 | 0.6753 |
| 3 | Replication minimal consensus 25-of-30 | 0.7033 | [0.652, 0.750] | 0.6729 | 0.7365 |
| 4 | Text consensus T0.3 23-of-30 | 0.6921 | [0.637, 0.739] | 0.6261 | 0.7737 |
| 5 | Text consensus T0.7 24-of-30 | 0.6915 | [0.639, 0.741] | 0.6488 | 0.7403 |
| 6 | Image consensus T0.7 18-of-30 | 0.6909 | [0.649, 0.730] | 0.6935 | 0.6883 |
| 7 | Text consensus T1.0 22-of-30 | 0.6860 | [0.633, 0.735] | 0.6506 | 0.7254 |
| 8 | Image consensus T1.0 18-of-30 | 0.6803 | [0.636, 0.721] | 0.7166 | 0.6475 |
| 9 | Image consensus T0.3 22-of-30 | 0.6661 | [0.625, 0.706] | 0.6519 | 0.6809 |
| 10 | Single-pass canonical-last | 0.6314 | [0.587, 0.672] | 0.5325 | 0.7755 |

## [PENDING] Sections

- **Phase 3a-HIGH image track consensus**: 90 runs complete, bootstrap CIs not yet
  computed. Consensus voting sweep pending.
- **Phase 3c diversity image track**: 83/100 output runs complete, not yet bootstrapped.
- **Phase 3c diversity text track consensus**: All 100 output runs complete, 60/100
  bootstrapped. Consensus sweep pending once all CIs available.
- **FDR-corrected pairwise comparisons**: Deferred until all experimental data are
  available. Currently reporting raw p-values only (24/70 significant at p < 0.05).
- **Proposer-Verifier (PV) pipeline results**: Separate analysis — see
  `results/pv/` for PV batch verification outputs.
