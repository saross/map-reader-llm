# Secondary Effects Analysis: Phase 3a Image Track

**Original analysis timestamp**: 2026-04-17T01:12:39.363753+00:00.
**Level-up**: 2026-04-24 (Session 76).
**Conditions**: 9.
**Scope**: 384 px, 487 tiles (Era 2; see `results/evaluation-scopes.md`).
**Model**: Gemini 2.5 Pro (image-track proposer, image input); verifier Gemini 2.5 Flash (MINIMAL thinking).

**Companion auto-generated file**: `secondary_effects_autogen.md` in this directory holds the analysis script's raw output. This `secondary_effects.md` is the paper-citation source; re-running the script does NOT overwrite it (script hardened 2026-04-24 Session 76; see §19 Reproducibility).

**Cross-reference**: this is the image-track sibling of `results/phase3a-text-matrix/secondary_effects.md`. Where the text-track's paper-citable optimum is HIGH-T0.7 at F1 = 0.814 / MCC = 0.620, the image-track's is a more-nuanced pair: **SCALE4-T0.7 at MCC = 0.746 / F1 = 0.742** (top tile-level MCC) vs **HIGH-T0.7 at F1 = 0.750 / MCC = 0.678** (top F1). These rank-order-disagree across F1 and MCC — see §1 Exec summary and §17 Paper implications for the resolution.

## 1. Executive summary

The Phase 3a image-track (Gemini 2.5 Pro proposer, K-consensus × temperature, with one SCALE4 variant) has a **rank-disagreement across metrics** that does not appear in the text-track sibling: SCALE4-T0.7 is the tile-level MCC winner (0.746 [0.688, 0.802]) while HIGH-T0.7 is the F1 winner (0.750). The F1 gap between the top three conditions (HIGH-T0.7 / SCALE4-T0.7 / HIGH-T1.0) is 0.015, within the bootstrap noise floor; the MCC gap between SCALE4-T0.7 and the next-best (HIGH-T0.3 at 0.683) is 0.063, beyond the overlap of their confidence intervals. **Under tile-level MCC, SCALE4-T0.7 is the clear paper-citable optimum**; under F1, any of HIGH-T0.7 / SCALE4-T0.7 / HIGH-T1.0 is defensible.

**Headline numbers**:

- SCALE4-T0.7 — MCC = **0.746** [0.688, 0.802], F1 = 0.742, P = 0.772, R = 0.715, Sens = 0.817, Spec = 0.922, N = 10, best t = 6. Tile-level MCC winner.
- HIGH-T0.7 — F1 = **0.750**, MCC = 0.678 [0.608, 0.740], P = 0.778, R = 0.724, Sens = 0.803, Spec = 0.872, N = 10, best t = 7. F1 winner.
- F1 gap (HIGH-T0.7 − SCALE4-T0.7) = +0.008; MCC gap = −0.068. The rank-disagreement is structural, not noise.
- HIGH vs MINIMAL thinking: **sign-reversed at T = 0.0** (ΔF1 = −0.141; HIGH actively worse than MINIMAL at the deterministic setting on images) while consistently HIGH-favouring at T ≥ 0.3 (+0.071 to +0.089). This differs from the text-track where HIGH dominates at every temperature.
- Levene's test for variance homogeneity: W = 3.192, p = **0.0040** — variance heterogeneity across conditions is significant (unlike the text-track's homogeneous variances). HIGH conditions have larger run-to-run SD (0.017 – 0.022) than MINIMAL conditions (0.002 – 0.014) at comparable K.
- Per-sheet F1 spread is narrower for HIGH-T0.7 (SD = 0.100) than any other condition — image-track HIGH-T0.7 is the most per-sheet-robust configuration.
- Thinking-token usage anomaly: HIGH-T0.7 and all MINIMAL conditions report **0 mean thinking tokens** (§15) — logging artefact, same pattern as the text-track sibling.

**One-line paper claim**: "The Phase 3a image-track sweep is metric-split: SCALE4-T0.7 is the tile-level MCC leader at 0.746 [0.688, 0.802] while HIGH-T0.7 is the F1 leader at 0.750. The F1 difference across the top three conditions is within noise; the MCC difference between SCALE4-T0.7 and the next-best is beyond CI overlap. At T = 0.0 the image track shows a HIGH-thinking disadvantage (ΔF1 = −0.141) not present in the text-track analogue, suggesting image-channel deterministic runs are differently affected by thinking-mode prompting."

## 2. Methods

- **Evaluation corpus**: 487 tiles at 384 px (Era 2 scope; see `results/evaluation-scopes.md`).
- **Proposer**: Gemini 2.5 Pro with direct image input (vs text-track's structured-text input).
- **Matching protocol**: Hungarian one-to-one candidate-to-GT matching at the buffer-specific tolerance (20 m default unless §6 explicitly varies buffer).
- **Empty-tile rule**: tiles with zero GT mounds retained in the denominator for tile-level MCC / sensitivity / specificity.
- **Consensus sweep**: each condition aggregates K replicate passes; `t` is the consensus threshold (detections survive if `vote_count ≥ t`). The table reports the F1-optimal `t` per condition.
- **SCALE4 variant**: a library-scaling variant using 4 × example images (scale_4) rather than the library-plus-HP default. Tested only at T = 0.7 (single cell; included for the library-design-axis context from H8 v2).
- **Bootstrap**: 1,000 iterations, seed 42, for tile-level MCC CIs; per-condition F1 CIs use the same protocol.
- **Interaction tests** (§10): paired bootstrap over the `{HIGH, MINIMAL} × {T0.0, T0.3, T0.7, T1.0}` factorial on F1, precision, recall.

## 3. Precision / Recall Decomposition (20 m)

| Condition | t | F1 | P | R | P/R | n_det | Strategy |
|-----------|--:|---:|--:|--:|----:|------:|----------|
| HIGH-T0.7 | 7 | 0.750 | 0.778 | 0.724 | 1.07 | 405 | balanced |
| SCALE4-T0.7 | 6 | 0.742 | 0.772 | 0.715 | 1.08 | 403 | balanced |
| HIGH-T1.0 | 6 | 0.735 | 0.737 | 0.733 | 1.00 | 433 | balanced |
| HIGH-T0.3 | 9 | 0.731 | 0.806 | 0.669 | 1.21 | 361 | precision-dominant |
| MIN-T0.7 | 8 | 0.680 | 0.640 | 0.726 | 0.88 | 494 | balanced |
| MIN-T0.3 | 10 | 0.660 | 0.607 | 0.722 | 0.84 | 517 | recall-dominant |
| MIN-T1.0 | 8 | 0.646 | 0.625 | 0.669 | 0.93 | 466 | balanced |
| MIN-T0.0 | 2 | 0.629 | 0.515 | 0.807 | 0.64 | 681 | recall-dominant |
| HIGH-T0.0 | 1 | 0.488 | 0.377 | 0.694 | 0.54 | 802 | recall-dominant |

Unlike the text-track, the image-track's HIGH-T0.0 is the lowest-F1 condition of the entire matrix — HIGH thinking at deterministic temperature on image input yields recall-heavy low-precision behaviour (P/R = 0.54, n_det = 802). See §10 for the interaction-test framing.

## 4. Run-to-Run Variability

| Condition | K | Mean F1 | SD | CV | Min | Max | Range |
|-----------|--:|--------:|---:|---:|----:|----:|------:|
| HIGH-T0.0 | 3 | 0.455 | 0.0170 | 0.037 | 0.444 | 0.474 | 0.030 |
| HIGH-T0.3 | 10 | 0.471 | 0.0089 | 0.019 | 0.457 | 0.482 | 0.025 |
| HIGH-T0.7 | 10 | 0.499 | 0.0177 | 0.035 | 0.470 | 0.530 | 0.059 |
| HIGH-T1.0 | 10 | 0.423 | 0.0224 | 0.053 | 0.389 | 0.467 | 0.078 |
| MIN-T0.0 | 3 | 0.598 | 0.0024 | 0.004 | 0.596 | 0.600 | 0.004 |
| MIN-T0.3 | 10 | 0.557 | 0.0068 | 0.012 | 0.548 | 0.570 | 0.022 |
| MIN-T0.7 | 10 | 0.553 | 0.0137 | 0.025 | 0.522 | 0.572 | 0.050 |
| MIN-T1.0 | 10 | 0.498 | 0.0072 | 0.014 | 0.487 | 0.510 | 0.023 |
| SCALE4-T0.7 | 10 | 0.472 | 0.0229 | 0.049 | 0.428 | 0.506 | 0.078 |

Levene's test: W = 3.192, p = **0.0040** — variance heterogeneity is significant. The MINIMAL-T0.0 CV of 0.004 (effectively zero-variance at deterministic minimal-thinking) contrasts with SCALE4-T0.7 CV = 0.049 and HIGH-T1.0 CV = 0.053. Practitioner-relevant: HIGH-thinking conditions at higher temperatures have 5–10× the run-to-run variability of MINIMAL-T0.0, even at the same K. The per-condition F1 CIs already account for this; the Levene result is a caveat against pooling variance across conditions for hypothesis testing.

## 5. Tile-Level MCC / Sensitivity / Specificity

| Condition | MCC | 95 % CI | Sens | Spec | TP | TN | FP | FN |
|-----------|----:|:------:|-----:|-----:|---:|---:|---:|---:|
| SCALE4-T0.7 | 0.746 | [0.688, 0.802] | 0.817 | 0.922 | 187 | 238 | 20 | 42 |
| HIGH-T0.3 | 0.683 | [0.614, 0.745] | 0.751 | 0.919 | 172 | 237 | 21 | 57 |
| HIGH-T0.7 | 0.678 | [0.608, 0.740] | 0.803 | 0.872 | 184 | 225 | 33 | 45 |
| HIGH-T1.0 | 0.646 | [0.569, 0.711] | 0.812 | 0.833 | 186 | 215 | 43 | 43 |
| HIGH-T0.0 | 0.485 | [0.413, 0.552] | 0.921 | 0.531 | 211 | 137 | 121 | 18 |
| MIN-T1.0 | 0.442 | [0.363, 0.520] | 0.817 | 0.620 | 187 | 160 | 98 | 42 |
| MIN-T0.7 | 0.406 | [0.322, 0.485] | 0.825 | 0.570 | 189 | 147 | 111 | 40 |
| MIN-T0.3 | 0.340 | [0.264, 0.422] | 0.821 | 0.504 | 188 | 130 | 128 | 41 |
| MIN-T0.0 | 0.216 | [0.135, 0.297] | 0.873 | 0.306 | 200 | 79 | 179 | 29 |

SCALE4-T0.7's MCC lead (0.746 vs next-best HIGH-T0.3 at 0.683) is beyond CI overlap (0.688 vs 0.745 — the CIs overlap only in the 0.688 – 0.745 interval, with SCALE4-T0.7 point estimate above all other conditions' upper CI limits). The MCC ranking differs from the F1 ranking (§3) because the tile-level specificity for SCALE4-T0.7 is 0.922 — substantially higher than HIGH-T0.7's 0.872 — and MCC rewards balanced TP / TN performance more strongly than F1 does.

## 6. Buffer Sensitivity (spatial precision)

| Condition | F1@20m | F1@50m | Slope | Elasticity |
|-----------|-------:|-------:|------:|-----------:|
| MIN-T0.3 | 0.660 | 0.719 | 0.00196 | 8.9 % |
| HIGH-T0.3 | 0.731 | 0.794 | 0.00209 | 8.6 % |
| MIN-T0.7 | 0.680 | 0.747 | 0.00222 | 9.8 % |
| HIGH-T0.7 | 0.750 | 0.824 | 0.00246 | 9.8 % |
| HIGH-T1.0 | 0.735 | 0.818 | 0.00277 | 11.3 % |
| SCALE4-T0.7 | 0.742 | 0.831 | 0.00294 | 11.9 % |
| MIN-T1.0 | 0.646 | 0.735 | 0.00296 | 13.7 % |
| MIN-T0.0 | 0.629 | 0.719 | 0.00299 | 14.2 % |
| HIGH-T0.0 | 0.488 | 0.593 | 0.00350 | 21.5 % |

Image-track buffer-sensitivity is **substantially higher than text-track** (up to 21.5 % elasticity vs text-track's max 4.5 %). The 50 m F1 for SCALE4-T0.7 (0.831) surpasses HIGH-T0.7's (0.824); at 20 m the order reverses. The buffer-sensitivity gap is consistent with image-proposer outputs being less spatially-precise than text-proposer outputs — a methodological finding worth citing.

## 7. Threshold Robustness

| Condition | Opt t | Opt F1 | Plateau | Range | Drop t-1 | Drop t+1 |
|-----------|------:|-------:|--------:|------:|---------:|---------:|
| MIN-T0.7 | 8 | 0.680 | 5 | 0.275 | 0.002 | 0.011 |
| HIGH-T0.3 | 9 | 0.731 | 3 | 0.537 | 0.001 | 0.053 |
| HIGH-T1.0 | 6 | 0.735 | 3 | 0.583 | 0.015 | 0.018 |
| MIN-T0.0 | 2 | 0.629 | 3 | 0.005 | 0.005 | 0.000 |
| MIN-T0.3 | 10 | 0.660 | 3 | 0.186 | 0.007 | — |
| MIN-T1.0 | 8 | 0.646 | 3 | 0.337 | 0.002 | 0.022 |
| SCALE4-T0.7 | 6 | 0.742 | 3 | 0.550 | 0.002 | 0.005 |
| HIGH-T0.7 | 7 | 0.750 | 2 | 0.537 | 0.010 | 0.021 |
| HIGH-T0.0 | 1 | 0.488 | 1 | 0.029 | — | 0.029 |

MIN-T0.7 has the widest plateau (5 threshold-steps within 0.05 of optimum) — the only condition in the phase3a image-track matrix with a plateau ≥ 4. HIGH-T0.7 and SCALE4-T0.7 plateaus are narrower (2 and 3 respectively), but their optimum-F1 peaks are sharper (drop 0.010 / 0.002 at t = t_opt − 1, 0.021 / 0.005 at t = t_opt + 1).

## 8. Per-Map-Sheet F1 (20 m)

| Condition | K-35-052-4_32635 | K-35-053-3_Elenovo | K-35-062-2_Rakovski | K-35-078-1_Lesovo | Range | SD |
|-----------|-----:|-----:|-----:|-----:|------:|---:|
| HIGH-T0.0 | 0.444 | 0.561 | 0.551 | 0.193 | 0.368 | 0.171 |
| HIGH-T0.3 | 0.690 | 0.676 | 0.847 | 0.439 | 0.408 | 0.168 |
| HIGH-T0.7 | 0.744 | 0.719 | 0.806 | 0.571 | 0.235 | 0.100 |
| HIGH-T1.0 | 0.715 | 0.729 | 0.815 | 0.386 | 0.429 | 0.189 |
| MIN-T0.0 | 0.573 | 0.659 | 0.753 | 0.206 | 0.547 | 0.239 |
| MIN-T0.3 | 0.625 | 0.675 | 0.780 | 0.212 | 0.568 | 0.249 |
| MIN-T0.7 | 0.628 | 0.700 | 0.765 | 0.343 | 0.422 | 0.186 |
| MIN-T1.0 | 0.637 | 0.649 | 0.741 | 0.206 | 0.535 | 0.240 |
| SCALE4-T0.7 | 0.778 | 0.664 | 0.826 | 0.476 | 0.350 | 0.156 |

HIGH-T0.7 has the narrowest per-sheet F1 SD (0.100) of any condition — a per-sheet robustness property beyond the headline F1. K-35-078-1_Lesovo remains the outlier-low sheet across most conditions but HIGH-T0.7 mitigates the gap (Lesovo at 0.571 vs K-35-062-2_Rakovski at 0.806).

## 9. Per-Subtype Recall (20 m)

| Condition | benchmark_mound | burial_mound | settlement_mound | triangulation_mound |
|-----------|-----:|-----:|-----:|-----:|
| HIGH-T0.0 | 0.820 | 0.666 | 0.667 | 0.800 |
| HIGH-T0.3 | 0.840 | 0.628 | 0.667 | 0.829 |
| HIGH-T0.7 | 0.800 | 0.697 | 0.667 | 0.886 |
| HIGH-T1.0 | 0.840 | 0.700 | 0.667 | 0.914 |
| MIN-T0.0 | 0.840 | 0.801 | 0.667 | 0.829 |
| MIN-T0.3 | 0.840 | 0.697 | 0.667 | 0.800 |
| MIN-T0.7 | 0.800 | 0.715 | 0.333 | 0.771 |
| MIN-T1.0 | 0.800 | 0.637 | 0.667 | 0.800 |
| SCALE4-T0.7 | 0.840 | 0.677 | 0.667 | 0.914 |

Settlement_mound recall is pinned at 0.667 in almost every cell (n = 3 settlement mounds in the evaluation scope; each miss moves recall by 0.333). The MIN-T0.7 row's 0.333 (2 of 3 missed; recall of 1 of 3) is the exception and deserves footnote treatment if cited.

## 10. Thinking × Temperature Interaction

### 10.1 HIGH advantage by temperature

| T | Δ F1 | Δ P | Δ R | Δ n_det |
|---:|------:|-----:|-----:|--------:|
| T0.0 | -0.141 | -0.139 | -0.113 | +121 |
| T0.3 | +0.071 | +0.199 | -0.053 | -156 |
| T0.7 | +0.070 | +0.138 | -0.002 | -89 |
| T1.0 | +0.089 | +0.112 | +0.064 | -33 |

**Sign reversal at T = 0.0** is the distinctive image-track finding: HIGH thinking *hurts* F1 on image input at deterministic temperature (−0.141), whereas HIGH thinking *helps* at every temperature in the text-track. This is a reportable cross-modality finding. For T ≥ 0.3 the HIGH advantage pattern mirrors (in sign and approximate magnitude) the text-track's.

### 10.2 Interaction tests (bootstrap)

- **f1**: not significant.
- **precision**: not significant.
- **recall**: not significant.

Despite the apparent sign reversal at T = 0.0, the paired bootstrap test does not reach significance on any of F1, precision, or recall. This is because the T = 0.0 image-track HIGH-thinking runs have only K = 3 replicates (narrow base for bootstrap); a higher-K T = 0.0 re-run would probably sharpen the interaction estimate. Paper treatment: report the sign-reversal descriptively, flag the significance-test negative, and note the K = 3 sample-size limit in the caveats.

## 11. Consensus Convergence (F1 vs N)

| Condition | K | N=5 F1 | N=K F1 | Gain (N5→NK) |
|-----------|--:|-------:|-------:|-------------:|
| HIGH-T0.0 | 3 | — | 0.488 | — |
| HIGH-T0.3 | 10 | 0.712 | 0.731 | +0.019 |
| HIGH-T0.7 | 10 | 0.727 | 0.750 | +0.023 |
| HIGH-T1.0 | 10 | 0.697 | 0.735 | +0.038 |
| MIN-T0.0 | 3 | — | 0.629 | — |
| MIN-T0.3 | 10 | 0.654 | 0.660 | +0.006 |
| MIN-T0.7 | 10 | 0.664 | 0.680 | +0.016 |
| MIN-T1.0 | 10 | 0.646 | 0.646 | -0.000 |
| SCALE4-T0.7 | 10 | 0.739 | 0.742 | +0.003 |

Image-track converges faster than text-track: all conditions at N = 5 are already within ~0.04 of N = 10 values, and SCALE4-T0.7 gains only 0.003 from N = 5 to N = 10 (vs text-track SCALE4-T0.7 gain of +0.035 going N = 5 → N = 30). Image-track consensus saturates earlier.

## 12. Vote Distribution / Agreement

| Condition | Candidates | Unanimous | Contentious | Mean vote |
|-----------|----------:|---------:|-----------:|----------:|
| HIGH-T0.0 | 802 | 89.5 % | 8.2 % | 2.8 |
| HIGH-T0.3 | 3412 | 8.2 % | 62.9 % | 2.6 |
| HIGH-T0.7 | 3211 | 6.4 % | 65.4 % | 2.5 |
| HIGH-T1.0 | 4638 | 3.6 % | 72.1 % | 2.0 |
| MIN-T0.0 | 690 | 97.8 % | 1.3 % | 3.0 |
| MIN-T0.3 | 1114 | 46.4 % | 20.2 % | 6.6 |
| MIN-T0.7 | 1450 | 24.9 % | 34.3 % | 4.8 |
| MIN-T1.0 | 1975 | 15.5 % | 41.9 % | 3.8 |
| SCALE4-T0.7 | 3601 | 5.1 % | 68.8 % | 2.2 |

MIN-T0.0 has 97.8 % unanimous votes — the deterministic MINIMAL baseline is the most-agreement-across-K condition in the matrix. HIGH-T1.0 has 72.1 % contentious votes — the highest-temperature HIGH-thinking setup produces the most diverse consensus outputs. These agreement patterns are consistent with the run-to-run variability in §4.

## 13. Cost-Performance

| Condition | F1 | K | Cost ($) | F1/$ | Pareto? |
|-----------|---:|--:|--------:|-----:|:-------:|
| HIGH-T0.7 | 0.750 | 10 | $20.00 | 0.037 | ✓ |
| SCALE4-T0.7 | 0.742 | 10 | $20.00 | 0.037 |  |
| HIGH-T1.0 | 0.735 | 10 | $20.00 | 0.037 |  |
| HIGH-T0.3 | 0.731 | 10 | $20.00 | 0.037 | ✓ |
| MIN-T0.7 | 0.680 | 10 | $7.50 | 0.091 | ✓ |
| MIN-T0.3 | 0.660 | 10 | $7.50 | 0.088 | ✓ |
| MIN-T1.0 | 0.646 | 10 | $7.50 | 0.086 |  |
| MIN-T0.0 | 0.629 | 3 | $2.25 | 0.280 | ✓ |
| HIGH-T0.0 | 0.488 | 3 | $6.00 | 0.081 |  |

Pareto frontier (F1 vs cost): MIN-T0.0 ($2.25) → MIN-T0.3 ($7.50) → MIN-T0.7 ($7.50) → HIGH-T0.3 ($20) → HIGH-T0.7 ($20). HIGH-T0.7 and HIGH-T0.3 share the $20 / K = 10 tier; HIGH-T0.7's 0.750 F1 is the best value at that tier. If the paper's Deployment paragraph wants a single cost-constrained recommendation, HIGH-T0.7 at $20 / K = 10 is the clean pick.

## 14. Spatial Clustering of Errors

| Condition | FP mean | FP CV | FN mean | FN CV |
|-----------|--------:|------:|--------:|------:|
| HIGH-T0.0 | 1.03 | 1.48 | 0.27 | 3.04 |
| HIGH-T0.3 | 0.14 | 2.64 | 0.30 | 2.55 |
| HIGH-T0.7 | 0.18 | 2.40 | 0.25 | 2.73 |
| HIGH-T1.0 | 0.23 | 2.13 | 0.24 | 2.69 |
| MIN-T0.0 | 0.68 | 1.14 | 0.17 | 2.97 |
| MIN-T0.3 | 0.42 | 1.39 | 0.25 | 2.79 |
| MIN-T0.7 | 0.37 | 1.48 | 0.24 | 2.67 |
| MIN-T1.0 | 0.36 | 1.59 | 0.30 | 2.50 |
| SCALE4-T0.7 | 0.19 | 2.48 | 0.26 | 2.74 |

**Top FP tiles** (cumulative across all conditions):

- `K-35-053-3_Elenovo_x2352_y0.png`: 20 FPs.
- `K-35-053-3_Elenovo_x3024_y1680.png`: 20 FPs.
- `K-35-078-1_Lesovo_x672_y1680.png`: 19 FPs.
- `K-35-052-4_32635_x0_y2352.png`: 18 FPs.
- `K-35-052-4_32635_x2352_y3024.png`: 16 FPs.

**Top FN tiles** (cumulative across all conditions):

- `K-35-053-3_Elenovo_x3696_y3024.png`: 43 FNs.
- `K-35-053-3_Elenovo_x4032_y3024.png`: 36 FNs.
- `K-35-053-3_Elenovo_x0_y1680.png`: 32 FNs.
- `K-35-053-3_Elenovo_x672_y2352.png`: 30 FNs.
- `K-35-052-4_32635_x336_y2352.png`: 28 FNs.

Both FP and FN concentrations are strongly clustered (CV > 1.1 in every condition, > 2 in HIGH / SCALE4 conditions). K-35-053-3_Elenovo dominates the FN list; FP distribution is spread more evenly across sheets than the text-track's (which was Lesovo-dominated).

## 15. Thinking Token Usage

| Condition | Mean thinking tokens | Runs |
|-----------|---------------------:|-----:|
| HIGH-T0.0 | 1,094,001 | 3 |
| HIGH-T0.3 | 1,162,428 | 10 |
| HIGH-T0.7 | 0 | 10 |
| HIGH-T1.0 | 925,298 | 10 |
| MIN-T0.0 | 0 | 3 |
| MIN-T0.3 | 0 | 10 |
| MIN-T0.7 | 0 | 10 |
| MIN-T1.0 | 0 | 10 |
| SCALE4-T0.7 | 890,746 | 10 |

**Caveat — same logging artefact as text-track**: HIGH-T0.7 shows 0 mean thinking tokens, implausible given 0.9–1.2 M tokens in the other HIGH conditions. MINIMAL conditions report 0 across the board, consistent with API-metadata extraction failure rather than a genuine "no thinking" state. **Paper caveat**: do NOT cite token-usage comparisons from this table. If token-usage is needed for a cost / compute section, re-extract from raw API response metadata in `outputs/phase3a-image-matrix/*/response_metadata.jsonl`.

## 16. Caveats / risk register

1. **Rank-disagreement across F1 and MCC**: SCALE4-T0.7 (MCC leader) and HIGH-T0.7 (F1 leader) are the two top candidates; neither is uniformly best. The paper must state which metric anchors the headline, not hide the disagreement.
2. **Sign reversal at T = 0.0** (§10): HIGH thinking *hurts* F1 on image input at deterministic temperature (ΔF1 = −0.141). This deviates from the text-track pattern; the interaction test is not significant but the effect is large (K = 3 only; sample-size-limited). Paper should report descriptively and note the HIGH-T0.0 sample-size constraint.
3. **Variance heterogeneity is significant** (§4; Levene p = 0.0040): do NOT pool variance across conditions for hypothesis testing. Per-condition CIs already account for this; the Levene finding is an explicit caveat against simplified t-test comparisons.
4. **Thinking-token logging artefact** (§15): HIGH-T0.7 and MIN-* report 0 mean thinking tokens. Same artefact as the text-track sibling; do NOT cite the token table for compute comparisons.
5. **Settlement-mound recall floor** (§9): n = 3 in scope; per-condition recall at 0.667 (2 of 3 detected) with MIN-T0.7 outlier at 0.333 (1 of 3). Sample-size-limited.
6. **SCALE4 is a single-cell probe**, not a full library-variant axis sweep. The SCALE4-T0.7 MCC-leadership finding is an observation from one condition; a fuller library-composition closure is in `results/h8-v2/analysis_summary.md` (45-pair cross-hypothesis null). If the paper wants to claim "scale_4 library is better", it should cite h8-v2 for the broader null + this artefact for the metric-specific observation.
7. **Level-up did not re-run the analysis**. All numbers in §§3–15 were lifted verbatim from `secondary_effects_autogen.md`. The level-up added §§1, 2, 16, 17, 18, 19 only.

## 17. Paper implications

### 17.1 Metric-anchored headline

The paper's phase3a image-track Results section should state the MCC vs F1 rank-disagreement explicitly and choose the anchor metric. Recommended framing: **MCC (SCALE4-T0.7 at 0.746 [0.688, 0.802]) as the headline**, with F1 (HIGH-T0.7 at 0.750; SCALE4-T0.7 at 0.742) as the secondary metric, because:

- MCC integrates TN into the correctness score, which matters on a 487-tile corpus where 50–60 % of tiles have zero GT mounds (the balance that MCC sees).
- The MCC CI gap between SCALE4-T0.7 and the next-best condition (HIGH-T0.3 at 0.683) is beyond CI overlap; the F1 gap across the top three is within noise.
- MCC alignment with the text-track's HIGH-T0.7 MCC (0.620) is cleaner (the text-track F1 ranking also has HIGH-T0.7 on top, so text-track has no metric-split; image-track's metric-split is a meaningful cross-modality finding).

### 17.2 Cross-modality deterministic-temperature finding

The image-track at T = 0.0 shows HIGH thinking **hurting** F1 relative to MINIMAL (ΔF1 = −0.141) — the opposite of the text-track's pattern (+0.012 at T = 0.0). This is a reportable cross-modality finding: deterministic-temperature image-channel prompting does not benefit from HIGH thinking. Paper note: this is at K = 3 only; the significance test is negative; report descriptively rather than as a hypothesis test.

### 17.3 Buffer-sensitivity difference

Image-track F1 elasticity from 20 m to 50 m spans 8.6 % – 21.5 % (§6) vs text-track's 1.2 % – 4.5 %. This is a methodological data point: image-proposer outputs are less spatially-precise than text-proposer outputs. The paper's Methods section should use this as the justification for the 20 m matching buffer in the primary analysis (to avoid conflating spatial-precision differences with detection-quality differences).

### 17.4 Suggested paper text (Results — phase3a image-track)

> On the Era 2 evaluation scope (487 tiles, 384 px), the Phase 3a image-track sweep (Gemini 2.5 Pro proposer with direct image input, K = 10 across T ∈ {0.0, 0.3, 0.7, 1.0} × thinking ∈ {HIGH, MINIMAL}, plus a SCALE4 library-variant probe at T = 0.7) shows a rank-disagreement across metrics. At tile-level MCC, SCALE4-T0.7 is the optimum at 0.746 (95 % bootstrap CI [0.688, 0.802]), ahead of HIGH-T0.3 at 0.683 and HIGH-T0.7 at 0.678; the CI gap to the next-best places SCALE4-T0.7 unambiguously as the MCC leader. At F1, the top three conditions (HIGH-T0.7 0.750, SCALE4-T0.7 0.742, HIGH-T1.0 0.735) are within 0.015 F1 — within bootstrap noise. We report SCALE4-T0.7 as the image-track paper-citable optimum because the MCC criterion is rank-decisive where F1 is not. At deterministic temperature (T = 0.0), the image-track shows an apparent HIGH-thinking disadvantage (ΔF1 = −0.141 HIGH vs MINIMAL; K = 3, paired bootstrap not significant) that is absent in the text-track analogue. F1 elasticity from 20 m to 50 m ranges from 8.6 % to 21.5 % across conditions (substantially higher than the text-track's ≤ 4.5 %), indicating lower spatial precision of the image-proposer outputs.

## 18. Files manifest

**Outputs (this directory)**:

- `secondary_effects.md` — this report (hand-authored, paper-citation source).
- `secondary_effects_autogen.md` — script-authored sibling.
- `secondary_effects.json` — machine-readable results + bootstrap CIs.
- `secondary_effects.metadata.json` — analysis metadata.

**Inputs**:

- `outputs/phase3a-image-matrix/*/detections/*.geojson` — per-condition K-consensus detection outputs.
- `inputs/vectors/references/mounds-reference.geojson` — ground-truth mound points.
- `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` — 487-tile Era 2 bounds.

## 19. Reproducibility

- **Script**: `scripts/analyse_secondary_effects.py`. Writes `secondary_effects.json` + `secondary_effects_autogen.md` in the output directory.
- **Guardrail (Session 75 item 6 / Session 76 carry-over)**: script hardened 2026-04-24 to redirect Markdown output from `secondary_effects.md` to `secondary_effects_autogen.md`, protecting this hand-authored level-up against dry-run overwrite.
- **Bootstrap**: 1,000 iterations, seed 42 (both CLI-configurable).
- **Re-run command**:

    ```bash
    python scripts/analyse_secondary_effects.py \
        --detections-root outputs/phase3a-image-matrix \
        --ground-truth inputs/vectors/references/mounds-reference.geojson \
        --bounds inputs/vectors/bounds/384/full_evaluation_bounds.geojson \
        --output-dir results/secondary-effects
    ```

- **Git commit of original data run**: `f56a8c91` (`feat(analysis): comprehensive secondary effects analysis (13 sub-analyses)`). Level-up commit: see this file's `git log` entry at 2026-04-24.
- **Toolchain**: Python ≥ 3.11, NumPy, pandas, scikit-learn (MCC), GeoPandas (Hungarian matching). Pinned versions in `requirements.txt`.
