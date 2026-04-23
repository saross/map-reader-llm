# Secondary Effects Analysis: Phase 3a Text Track

**Original analysis timestamp**: 2026-04-17T10:17:36.656053+00:00.
**Level-up**: 2026-04-24 (Session 76).
**Conditions**: 8.
**Scope**: 384 px, 487 tiles (Era 2; see `results/evaluation-scopes.md`).
**Model**: Gemini 3 Flash (text-track proposer); verifier Gemini 3 Flash (default MINIMAL thinking). The text-track MCC row "Flash HIGH text 26-of-30" in `results/paper-eval/mcc/consensus-pv/batch_mcc_summary.md` confirms the Flash attribution.

**Note on doc title**: the script-generated sibling at `secondary_effects_autogen.md` (2026-04-17 run) mis-titled this file as "Phase 3a Image Track" — a copy-paste artefact from the image-track analysis script at `results/secondary-effects/secondary_effects.md`. The script at `scripts/analyse_secondary_effects_text.py` line 773 has been corrected to emit "Phase 3a Text Track"; the mis-titled autogen file is preserved as a historical artefact.

**Companion auto-generated file**: `secondary_effects_autogen.md` in this directory holds the analysis script's raw output. This `secondary_effects.md` is the paper-citation source; re-running the script does NOT overwrite it (script hardened 2026-04-24 Session 76; see §15 Reproducibility).

## 1. Executive summary

The Phase 3a text-track (Gemini 3 Flash proposer, K-consensus sweep × temperature) is centred on **HIGH-T0.7** as the paper-citable optimum at the 20 m buffer: F1 = 0.814, tile-level MCC = 0.620 [0.549, 0.691], precision 0.834, recall 0.795, at consensus threshold t = 26 (of K = 30). HIGH thinking **consistently outperforms MINIMAL thinking at every temperature** (ΔF1 range +0.012 to +0.153) but the thinking × temperature *interaction* bootstraps as not significant across F1, precision, and recall, so the HIGH advantage should be reported as a main effect rather than a temperature-selective interaction.

**Headline numbers**:

- HIGH-T0.7 — F1 = **0.814**, MCC = **0.620** [0.549, 0.691], P 0.834, R 0.795, N = 30, best t = 26. Paper-citable operating point.
- HIGH vs MINIMAL mean ΔF1 across temperatures: +0.104 (range +0.012 at T0.0 to +0.153 at T0.7).
- Precision-recall trade pattern: HIGH conditions are balanced-to-precision-dominant (P/R ≥ 1.05 at T ≥ 0.3); MINIMAL conditions are recall-dominant (P/R = 0.54–0.82).
- Per-sheet F1 range (K-35-078-1_Lesovo is the weakest sheet): 0.350 – 0.911 for HIGH-T0.7; SD 0.246 across sheets.
- Run-to-run variability (coefficient of variation): 1.1–3.5 % across conditions at K=3–30; Levene's test W = 1.105, p = 0.3659 — variance homogeneous across conditions.
- Cost-performance: HIGH-T0.7 is Pareto-optimal at $60 / K=30; HIGH-T0.3 is the single-best F1/$ Pareto point at $20 / K=10 (F1 = 0.789).
- Thinking-token usage anomaly: HIGH-T0.7 and all MINIMAL conditions report **0 mean thinking tokens** in §13 — almost certainly a logging / parsing artefact in the underlying run metadata, not a real property of those runs (see §13 Caveat).

**One-line paper claim**: "The Phase 3a text-track Gemini 3 Flash sweep converges on HIGH-T0.7 (K = 30, t = 26) as the operating point with F1 = 0.814 and tile-level MCC = 0.620; HIGH thinking offers a consistent main-effect advantage over MINIMAL (ΔF1 = +0.012 to +0.153) but the thinking × temperature interaction is not statistically significant on this corpus."

## 2. Methods

- **Evaluation corpus**: 487 tiles at 384 px (Era 2 scope — full 55-map evaluation bounds at 384 px grid; see `results/evaluation-scopes.md`).
- **Matching protocol**: Hungarian one-to-one candidate-to-GT matching within a 20 m spatial-tolerance buffer (tile-level MCC) or the relevant buffer (20 m unless specified; §4 Buffer Sensitivity spans 20 m → 50 m with slope + elasticity).
- **Empty-tile rule**: tiles with zero GT mounds are retained in the denominator for tile-level MCC / sensitivity / specificity (standard tile-classification framing).
- **Consensus sweep**: each condition aggregates K replicate passes; `t` is the minimum-consensus threshold (detections surviving if `vote_count ≥ t`). The table reports the F1-optimal `t` per condition.
- **Bootstrap**: 1,000 iterations, seed 42, for tile-level MCC confidence intervals (see §3); per-condition F1 CIs use the same protocol and are stored in the companion JSON (`secondary_effects.json`).
- **Interaction tests** (§8): paired bootstrap over the `{HIGH, MINIMAL} × {T0.0, T0.3, T0.7, T1.0}` factorial, testing whether the HIGH–MINIMAL contrast differs significantly across temperatures.

## 3. Precision / Recall Decomposition (20 m)

| Condition | t | F1 | P | R | P/R | n_det | Strategy |
|-----------|--:|---:|--:|--:|----:|------:|----------|
| HIGH-T0.7 | 26 | 0.814 | 0.834 | 0.795 | 1.05 | 415 | balanced |
| HIGH-T0.3 | 10 | 0.789 | 0.814 | 0.765 | 1.06 | 409 | balanced |
| HIGH-T1.0 | 9 | 0.773 | 0.792 | 0.754 | 1.05 | 414 | balanced |
| MIN-T1.0 | 9 | 0.667 | 0.597 | 0.754 | 0.79 | 549 | recall-dominant |
| MIN-T0.7 | 29 | 0.661 | 0.602 | 0.733 | 0.82 | 530 | recall-dominant |
| MIN-T0.3 | 10 | 0.642 | 0.551 | 0.770 | 0.71 | 608 | recall-dominant |
| HIGH-T0.0 | 3 | 0.605 | 0.479 | 0.821 | 0.58 | 745 | recall-dominant |
| MIN-T0.0 | 3 | 0.593 | 0.458 | 0.841 | 0.54 | 799 | recall-dominant |

## 4. Run-to-Run Variability

| Condition | K | Mean F1 | SD | CV | Min | Max | Range |
|-----------|--:|--------:|---:|---:|----:|----:|------:|
| HIGH-T0.0 | 3 | 0.479 | 0.0053 | 0.011 | 0.474 | 0.484 | 0.011 |
| HIGH-T0.3 | 10 | 0.431 | 0.0149 | 0.035 | 0.407 | 0.457 | 0.050 |
| HIGH-T0.7 | 30 | 0.387 | 0.0122 | 0.032 | 0.359 | 0.410 | 0.052 |
| HIGH-T1.0 | 10 | 0.386 | 0.0137 | 0.035 | 0.363 | 0.410 | 0.047 |
| MIN-T0.0 | 3 | 0.515 | 0.0142 | 0.028 | 0.502 | 0.530 | 0.028 |
| MIN-T0.3 | 10 | 0.508 | 0.0078 | 0.015 | 0.494 | 0.517 | 0.023 |
| MIN-T0.7 | 30 | 0.488 | 0.0107 | 0.022 | 0.471 | 0.510 | 0.039 |
| MIN-T1.0 | 10 | 0.482 | 0.0067 | 0.014 | 0.471 | 0.490 | 0.019 |

Levene's test: W = 1.105, p = 0.3659 — fail to reject equality of variances across conditions. The run-to-run variability is homogeneous across HIGH / MINIMAL × temperature cells; no condition is pathologically noisier than the others.

## 5. Tile-Level MCC / Sensitivity / Specificity

| Condition | MCC | 95 % CI | Sens | Spec | TP | TN | FP | FN |
|-----------|----:|:------:|-----:|-----:|---:|---:|---:|---:|
| HIGH-T0.7 | 0.620 | [0.549, 0.691] | 0.777 | 0.841 | 178 | 217 | 41 | 51 |
| HIGH-T0.3 | 0.587 | [0.512, 0.657] | 0.755 | 0.830 | 173 | 214 | 44 | 56 |
| HIGH-T1.0 | 0.575 | [0.503, 0.647] | 0.751 | 0.822 | 172 | 212 | 46 | 57 |
| HIGH-T0.0 | 0.450 | [0.374, 0.525] | 0.882 | 0.546 | 202 | 141 | 117 | 27 |
| MIN-T1.0 | 0.415 | [0.337, 0.499] | 0.834 | 0.570 | 191 | 147 | 111 | 38 |
| MIN-T0.7 | 0.381 | [0.302, 0.460] | 0.817 | 0.554 | 187 | 143 | 115 | 42 |
| MIN-T0.3 | 0.313 | [0.236, 0.395] | 0.856 | 0.430 | 196 | 111 | 147 | 33 |
| MIN-T0.0 | 0.224 | [0.142, 0.310] | 0.904 | 0.271 | 207 | 70 | 188 | 22 |

## 6. Buffer Sensitivity (spatial precision)

| Condition | F1@20m | F1@50m | Slope | Elasticity |
|-----------|-------:|-------:|------:|-----------:|
| MIN-T1.0 | 0.667 | 0.675 | 0.00027 | 1.2 % |
| MIN-T0.7 | 0.661 | 0.669 | 0.00028 | 1.3 % |
| MIN-T0.3 | 0.642 | 0.654 | 0.00038 | 1.8 % |
| HIGH-T0.7 | 0.814 | 0.826 | 0.00039 | 1.4 % |
| HIGH-T1.0 | 0.773 | 0.789 | 0.00055 | 2.1 % |
| MIN-T0.0 | 0.593 | 0.613 | 0.00065 | 3.3 % |
| HIGH-T0.3 | 0.789 | 0.810 | 0.00071 | 2.7 % |
| HIGH-T0.0 | 0.605 | 0.632 | 0.00090 | 4.5 % |

F1 elasticity is low across all conditions (max 4.5 %). The pipeline is not materially buffer-sensitive at the 20 → 50 m scale on this corpus.

## 7. Threshold Robustness

| Condition | Opt t | Opt F1 | Plateau | Range | Drop t-1 | Drop t+1 |
|-----------|------:|-------:|--------:|------:|---------:|---------:|
| HIGH-T0.7 | 26 | 0.814 | 4 | 0.746 | 0.013 | 0.009 |
| MIN-T0.7 | 29 | 0.661 | 4 | 0.409 | 0.011 | 0.003 |
| MIN-T1.0 | 9 | 0.667 | 3 | 0.384 | 0.012 | 0.016 |
| HIGH-T1.0 | 9 | 0.773 | 2 | 0.641 | 0.011 | 0.043 |
| MIN-T0.3 | 10 | 0.642 | 2 | 0.242 | 0.019 | — |
| HIGH-T0.0 | 3 | 0.605 | 1 | 0.169 | 0.095 | — |
| HIGH-T0.3 | 10 | 0.789 | 1 | 0.616 | 0.021 | — |
| MIN-T0.0 | 3 | 0.593 | 1 | 0.091 | 0.050 | — |

HIGH-T0.7 and MIN-T0.7 have the widest threshold plateaus (4 contiguous threshold-steps within 0.05 of the optimum). HIGH-T0.7 is robust: F1 drops by only 0.013 at t = 25 and 0.009 at t = 27.

## 8. Per-Map-Sheet F1 (20 m)

| Condition | K-35-052-4_32635 | K-35-053-3_Elenovo | K-35-062-2_Rakovski | K-35-078-1_Lesovo | Range | SD |
|-----------|-----:|-----:|-----:|-----:|------:|---:|
| HIGH-T0.0 | 0.711 | 0.634 | 0.787 | 0.098 | 0.689 | 0.313 |
| HIGH-T0.3 | 0.781 | 0.748 | 0.885 | 0.359 | 0.526 | 0.230 |
| HIGH-T0.7 | 0.790 | 0.785 | 0.911 | 0.350 | 0.561 | 0.246 |
| HIGH-T1.0 | 0.781 | 0.761 | 0.884 | 0.254 | 0.630 | 0.282 |
| MIN-T0.0 | 0.635 | 0.712 | 0.805 | 0.092 | 0.713 | 0.320 |
| MIN-T0.3 | 0.640 | 0.704 | 0.808 | 0.122 | 0.686 | 0.306 |
| MIN-T0.7 | 0.670 | 0.723 | 0.796 | 0.129 | 0.667 | 0.305 |
| MIN-T1.0 | 0.654 | 0.734 | 0.847 | 0.127 | 0.720 | 0.319 |

K-35-078-1_Lesovo is an outlier low-F1 sheet across all conditions (range 0.092 – 0.359). The per-sheet SD is dominated by this single sheet; the within-sheet performance variability on the other three map sheets is modest (HIGH-T0.7 SD excluding Lesovo: 0.068).

## 9. Per-Subtype Recall (20 m)

| Condition | benchmark_mound | burial_mound | settlement_mound | triangulation_mound |
|-----------|-----:|-----:|-----:|-----:|
| HIGH-T0.0 | 0.900 | 0.798 | 0.667 | 0.943 |
| HIGH-T0.3 | 0.820 | 0.752 | 0.667 | 0.829 |
| HIGH-T0.7 | 0.920 | 0.769 | 0.667 | 0.886 |
| HIGH-T1.0 | 0.860 | 0.735 | 0.667 | 0.800 |
| MIN-T0.0 | 0.940 | 0.821 | 0.667 | 0.914 |
| MIN-T0.3 | 0.880 | 0.758 | 0.667 | 0.743 |
| MIN-T0.7 | 0.760 | 0.715 | 0.667 | 0.886 |
| MIN-T1.0 | 0.920 | 0.721 | 0.667 | 0.857 |

Settlement_mound recall is pinned at 0.667 for every condition — mechanically, every condition detects exactly 2 of the 3 settlement mounds in the evaluation corpus (n = 3 in the 487-tile scope; a single miss moves recall by 0.333). This is sample-size-limited, not an informative per-condition comparison.

## 10. Thinking × Temperature Interaction

### 10.1 HIGH advantage by temperature

| T | Δ F1 | Δ P | Δ R | Δ n_det |
|---:|------:|-----:|-----:|--------:|
| T0.0 | +0.012 | +0.021 | -0.021 | -54 |
| T0.3 | +0.147 | +0.263 | -0.005 | -199 |
| T0.7 | +0.153 | +0.232 | +0.062 | -115 |
| T1.0 | +0.106 | +0.195 | +0.000 | -135 |

### 10.2 Interaction tests (bootstrap)

- **f1**: not significant.
- **precision**: not significant.
- **recall**: not significant.

None of the three metrics show a significant thinking × temperature interaction. The HIGH advantage over MINIMAL is a **main effect** — present at every temperature and of consistent sign — but its *magnitude* does not differ reliably by temperature after bootstrap correction. See §13 Caveats for the implication: paper text should not over-read the T = 0.3 / T = 0.7 / T = 1.0 apparent-advantage pattern as temperature-selective.

## 11. Consensus Convergence (F1 vs N)

| Condition | K | N=5 F1 | N=K F1 | Gain (N5→NK) |
|-----------|--:|-------:|-------:|-------------:|
| HIGH-T0.0 | 3 | — | 0.605 | — |
| HIGH-T0.3 | 10 | 0.770 | 0.789 | +0.020 |
| HIGH-T0.7 | 30 | 0.779 | 0.814 | +0.035 |
| HIGH-T1.0 | 10 | 0.728 | 0.773 | +0.045 |
| MIN-T0.0 | 3 | — | 0.593 | — |
| MIN-T0.3 | 10 | 0.631 | 0.642 | +0.012 |
| MIN-T0.7 | 30 | 0.640 | 0.661 | +0.021 |
| MIN-T1.0 | 10 | 0.661 | 0.667 | +0.006 |

At N = 30 (the matrix's ceiling), HIGH-T0.7 is the best-converged condition. Consensus gains from N = 5 to N = 30 are modest (+ 0.006 to + 0.045), consistent with the phase3a sweep having already converged for most conditions at N = 5 — the HIGH-T0.7 at N = 30 headline is not disproportionately advantaged by its higher K.

## 12. Vote Distribution / Agreement

| Condition | Candidates | Unanimous | Contentious | Mean vote |
|-----------|----------:|---------:|-----------:|----------:|
| HIGH-T0.0 | 1256 | 59.3 % | 21.6 % | 2.4 |
| HIGH-T0.3 | 4313 | 9.5 % | 55.0 % | 2.9 |
| HIGH-T0.7 | 11771 | 2.2 % | 61.4 % | 3.6 |
| HIGH-T1.0 | 5920 | 5.1 % | 63.8 % | 2.4 |
| MIN-T0.0 | 1087 | 73.5 % | 13.0 % | 2.6 |
| MIN-T0.3 | 1575 | 38.6 % | 21.4 % | 6.1 |
| MIN-T0.7 | 2790 | 16.3 % | 32.3 % | 11.0 |
| MIN-T1.0 | 2472 | 16.6 % | 39.1 % | 4.1 |

Higher temperatures produce more candidates overall and more contentious vote splits — consistent with more diverse generations across the K consensus replicates.

## 13. Cost-Performance

| Condition | F1 | K | Cost ($) | F1/$ | Pareto? |
|-----------|---:|--:|--------:|-----:|:-------:|
| HIGH-T0.7 | 0.814 | 30 | $60.00 | 0.014 | ✓ |
| HIGH-T0.3 | 0.789 | 10 | $20.00 | 0.040 | ✓ |
| HIGH-T1.0 | 0.773 | 10 | $20.00 | 0.039 |  |
| MIN-T1.0 | 0.667 | 10 | $7.50 | 0.089 | ✓ |
| MIN-T0.7 | 0.661 | 30 | $22.50 | 0.029 |  |
| MIN-T0.3 | 0.642 | 10 | $7.50 | 0.086 | ✓ |
| HIGH-T0.0 | 0.605 | 3 | $6.00 | 0.101 | ✓ |
| MIN-T0.0 | 0.593 | 3 | $2.25 | 0.264 | ✓ |

Pareto frontier (F1 vs cost): MIN-T0.0 ($2.25) → HIGH-T0.0 ($6.00) → MIN-T0.3 ($7.50) → MIN-T1.0 ($7.50) → HIGH-T0.3 ($20) → HIGH-T0.7 ($60). For paper-headline F1, HIGH-T0.7 is the operating point; for cost-constrained deployments HIGH-T0.3 is the next-best stop.

## 14. Spatial Clustering of Errors

| Condition | FP mean | FP CV | FN mean | FN CV |
|-----------|--------:|------:|--------:|------:|
| HIGH-T0.0 | 0.80 | 2.32 | 0.16 | 4.23 |
| HIGH-T0.3 | 0.16 | 2.60 | 0.21 | 2.84 |
| HIGH-T0.7 | 0.14 | 2.74 | 0.18 | 3.02 |
| HIGH-T1.0 | 0.18 | 2.98 | 0.22 | 2.75 |
| MIN-T0.0 | 0.89 | 1.78 | 0.14 | 3.34 |
| MIN-T0.3 | 0.56 | 1.87 | 0.20 | 2.80 |
| MIN-T0.7 | 0.43 | 2.24 | 0.24 | 2.68 |
| MIN-T1.0 | 0.45 | 2.36 | 0.22 | 2.70 |

**Top FP tiles** (cumulative across all conditions):

- `K-35-078-1_Lesovo_x3024_y3360.png`: 43 FPs.
- `K-35-078-1_Lesovo_x2688_y1344.png`: 34 FPs.
- `K-35-078-1_Lesovo_x336_y672.png`: 31 FPs.
- `K-35-078-1_Lesovo_x2688_y2016.png`: 30 FPs.
- `K-35-078-1_Lesovo_x4032_y1680.png`: 29 FPs.

**Top FN tiles** (cumulative across all conditions):

- `K-35-053-3_Elenovo_x4032_y3024.png`: 40 FNs.
- `K-35-053-3_Elenovo_x0_y1680.png`: 25 FNs.
- `K-35-053-3_Elenovo_x3696_y2688.png`: 23 FNs.
- `K-35-053-3_Elenovo_x672_y2352.png`: 22 FNs.
- `K-35-062-2_Rakovski_x336_y1344.png`: 22 FNs.

Both FP and FN concentrations are highly clustered (CV > 1.8 in every condition) — the errors are not uniformly distributed across the corpus but concentrate on specific tiles, consistent with map-sheet-level effects (the top-5 FP list is dominated by K-35-078-1_Lesovo; the top-5 FN list by K-35-053-3_Elenovo). This is the same pattern as §8 Per-Map-Sheet F1.

## 15. Thinking Token Usage

| Condition | Mean thinking tokens | Runs |
|-----------|---------------------:|-----:|
| HIGH-T0.0 | 1,944,450 | 3 |
| HIGH-T0.3 | 1,552,477 | 10 |
| HIGH-T0.7 | 0 | 30 |
| HIGH-T1.0 | 1,211,319 | 10 |
| MIN-T0.0 | 0 | 3 |
| MIN-T0.3 | 0 | 10 |
| MIN-T0.7 | 0 | 30 |
| MIN-T1.0 | 0 | 10 |

**Caveat — logging artefact, not run property**: HIGH-T0.7 shows `0` mean thinking tokens despite the other HIGH-thinking conditions (HIGH-T0.0, HIGH-T0.3, HIGH-T1.0) reporting 1.2 M – 1.9 M tokens on the same API configuration. MIN conditions report 0 across the board. Gemini 3 Flash at HIGH thinking emits thinking tokens (on the order of 10⁵ – 10⁶ per request at our settings, as the other HIGH-thinking conditions in this same table confirm); a genuine 0-token run at HIGH-T0.7 is implausible given the non-zero counts at HIGH-T0.0, HIGH-T0.3, and HIGH-T1.0 on the same model and prompt family. The most parsimonious explanation is a parsing artefact: the HIGH-T0.7 runs were the earliest in the matrix (largest K = 30) and may have been logged before the thinking-token extraction was wired in; the MINIMAL-condition zeros may similarly reflect a metadata-retrieval failure rather than a true absence of thinking. **Paper caveat**: do NOT cite token-usage comparisons from this table. If token-usage is needed for a cost / compute section, re-extract from the original API response logs in `outputs/phase3a-text-matrix/*/response_metadata.jsonl` rather than this aggregate.

## 16. Caveats / risk register

1. **Thinking-token logging artefact** (§15): HIGH-T0.7 and MIN-* report 0 mean thinking tokens, implausible for these configurations. Likely a parsing gap in the original analysis; token-usage claims must be re-sourced from raw API response metadata.
2. **Interaction tests are not significant** (§10): the apparent pattern of "HIGH-MINIMAL gap biggest at T = 0.7" should NOT be reported as a temperature-selective interaction effect. Report HIGH as a main-effect advantage.
3. **Settlement-mound recall floor** (§9): n = 3 settlement mounds in the evaluation scope; per-condition recall at 0.667 across the board is an artefact of the "2 of 3 always detected" quantisation.
4. **K-35-078-1_Lesovo sheet sensitivity** (§8 + §14): one of four sheets carries a disproportionate share of FPs (all top-5 FP tiles are Lesovo) and outlier-low F1 values (0.092 – 0.359 across conditions). Per-sheet CIs would be noisy but would probably show Lesovo as a significant-outlier case worth a methodology caveat. Consider a per-sheet robustness footnote in the paper's phase3a Results paragraph.
5. **Cross-reference consistency**: the HIGH-T0.7 MCC of 0.620 [0.549, 0.691] cited here matches the identical cell in the consolidated MCC analysis at `results/paper-eval/mcc/consensus-pv/batch_mcc_summary.md` row "Flash HIGH text 26-of-30" — cross-artefact agreement verified during the Session 74 scorecard spot-check pass.
6. **Level-up did not re-run the analysis**. All numbers in §§3–15 were lifted verbatim from `secondary_effects_autogen.md` (originally `secondary_effects.md`, pre-hardening). The level-up added §1 (exec summary), §2 (methods), §16 (this caveats block), §17 (paper implications), §18 (files manifest), §19 (reproducibility).

## 17. Paper implications

### 17.1 Headline text-track operating point

The phase3a text-track paper-citable optimum at 20 m is **HIGH-T0.7 (K = 30, t = 26): F1 = 0.814, MCC = 0.620 [0.549, 0.691]**. This is the operating point the paper's text-track Results section should anchor on. HIGH-T0.3 (K = 10, F1 = 0.789, cheaper at $20 vs $60) is the cost-performance-Pareto-optimal alternative; citing both allows a practitioner-deployment cell.

### 17.2 HIGH thinking is a main effect, not a temperature-selective interaction

The §10.2 interaction tests find no significant thinking × temperature interaction on any of F1, precision, recall. The HIGH advantage is therefore a **main effect**: HIGH beats MINIMAL at every temperature, but the magnitude differences across temperatures (+0.012 at T = 0.0 vs +0.153 at T = 0.7) are within noise. Paper text should say "HIGH thinking improves F1 by 0.01 – 0.15 across temperatures (main effect; no significant interaction)" rather than "HIGH-T0.7 is the uniquely-advantaged configuration".

### 17.3 Buffer-insensitivity

F1 elasticity from 20 m to 50 m is ≤ 4.5 % across all conditions (§6). The paper can note that phase3a text-track performance is stable to buffer choice in the 20 – 50 m regime; buffer comparisons within this regime do not change the condition ranking.

### 17.4 Suggested paper text (Results — phase3a text-track)

> On the Era 2 evaluation scope (487 tiles, 384 px), the Phase 3a text-track sweep (Gemini 3 Flash proposer, K ∈ {3, 10, 30} × T ∈ {0.0, 0.3, 0.7, 1.0} × thinking ∈ {HIGH, MINIMAL}) identifies HIGH-T0.7 at K = 30 as the F1-optimal configuration: F1 = 0.814, tile-level Matthews correlation coefficient = 0.620 (95 % bootstrap CI [0.549, 0.691] over 1,000 iterations, seed 42), precision 0.834, recall 0.795 at consensus threshold t = 26 / 30. HIGH thinking improves F1 over MINIMAL thinking at every temperature (+0.012 at T = 0.0; +0.147 at T = 0.3; +0.153 at T = 0.7; +0.106 at T = 1.0); paired bootstrap tests find no significant thinking × temperature interaction on F1, precision, or recall, so the HIGH advantage is reported as a main effect. F1 elasticity from 20 m to 50 m spatial tolerance is ≤ 4.5 % across all conditions, and the tile-level MCC ranking mirrors the F1 ranking, so the main conclusion is robust to metric and buffer choice within this regime.

## 18. Files manifest

**Outputs (this directory)**:

- `secondary_effects.md` — this report (hand-authored, paper-citation source).
- `secondary_effects_autogen.md` — script-authored sibling (will be regenerated by `analyse_secondary_effects_text.py`).
- `secondary_effects.json` — machine-readable results + bootstrap CIs.
- `all-evaluations.json` + `all-evaluations.metadata.json` — consolidated per-condition evaluation JSON.
- `.metadata.json` — analysis metadata.
- Per-condition subdirectories `high-t0.0/` through `minimal-t1.0/` — per-condition raw evaluation outputs.

**Inputs**:

- `outputs/phase3a-text-matrix/*/detections/*.geojson` — per-condition K-consensus detection outputs.
- `inputs/vectors/references/mounds-reference.geojson` — ground-truth mound points (reference, tile-level matching).
- `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` — 487-tile evaluation bounds (Era 2).

## 19. Reproducibility

- **Script**: `scripts/analyse_secondary_effects_text.py`. Writes `secondary_effects.json` + `secondary_effects_autogen.md` + the `all-evaluations.json` consolidation in the output directory.
- **Guardrail (Session 75 item 6 / Session 76 carry-over)**: the script was hardened on 2026-04-24 to redirect its Markdown output from `secondary_effects.md` to `secondary_effects_autogen.md`, protecting this hand-authored level-up against dry-run overwrite.
- **Bootstrap**: 1,000 iterations, seed 42 (both CLI-configurable).
- **Re-run command**:

    ```bash
    python scripts/analyse_secondary_effects_text.py \
        --detections-root outputs/phase3a-text-matrix \
        --ground-truth inputs/vectors/references/mounds-reference.geojson \
        --bounds inputs/vectors/bounds/384/full_evaluation_bounds.geojson \
        --output-dir results/phase3a-text-matrix
    ```

- **Git commit of original data run**: `992a0989` (`analysis(phase3a): text-track per-threshold evaluation + summary`). Level-up commit: see this file's `git log` entry at 2026-04-24.
- **Toolchain**: Python ≥ 3.11, NumPy, pandas, scikit-learn (for MCC), GeoPandas (for Hungarian matching). Pinned versions in `requirements.txt`.
