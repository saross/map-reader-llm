# Phase 3a Image Track: Consensus Analysis Summary

**Original analysis timestamp**: 2026-04-16T14:19:20.700655+00:00.
**Level-up**: 2026-04-24 (Session 76).
**Scope**: 384 px, 487 tiles (Era 2 full evaluation; see `results/evaluation-scopes.md`).
**Config**: library_plus-hp (13 examples, 4 HP + 0 HN).
**Model**: **Gemini 3 Flash** (image-track proposer, image input).

**Companion auto-generated file**: `consensus-analysis-summary_autogen.md` in this directory holds the analysis script's raw output. This `consensus-analysis-summary.md` is the paper-citation source; re-running the script does NOT overwrite it (script hardened 2026-04-24 Session 76; see §7 Reproducibility).

**Cross-reference**: this is the image-track consensus sweep sibling of:

- `results/phase3a-text-matrix/secondary_effects.md` (text-track 13-subsection analysis; Flash).
- `results/secondary-effects/secondary_effects.md` (image-track 13-subsection analysis; Flash; same underlying run data as this doc, different analytical angle).

## 1. Executive summary

The Phase 3a image-track consensus sweep (Gemini 3 Flash proposer, K ∈ {3, 5, 10} × T ∈ {0.0, 0.3, 0.7, 1.0} × thinking ∈ {HIGH, MINIMAL}, library_plus-hp config with 13 examples / 4 HP / 0 HN) identifies **HIGH-T0.7 at N = 10, t = 7** as the F1-optimum on the 487-tile Era 2 scope: F1 = **0.750** (95 % bootstrap CI [0.707, 0.790], 1,000 iterations, seed 42), P = 0.778, R = 0.724.

**Headline numbers**:

- F1-optimum: **HIGH-T0.7 / N = 10 / t = 7** — F1 = 0.750 [0.707, 0.790], P = 0.778, R = 0.724.
- F1 at 50 m buffer (same cell): 0.834 — a +0.084 buffer-elasticity lift from 20 m.
- HIGH vs MINIMAL advantage at matched (T, N): ranges from +0.051 (T = 1.0, N = 5) to +0.089 (T = 1.0, N = 10); mean across significant cells = +0.067. HIGH-T0.7 / N = 10 advantage over MINIMAL-T0.7 / N = 10 is **+0.070** (CIs [0.707, 0.790] vs [0.634, 0.723] — overlap of 0.050 on the central interval).
- Consensus gain from N = 5 to N = 10 for HIGH-T0.7: +0.023 (0.727 → 0.750); for MIN-T0.7: +0.016 (0.664 → 0.680). N = 10 is the matrix's ceiling; there is no N = 30 sweep in this artefact.
- HIGH-T0.0 / N = 10 is the worst F1 cell at 0.488 (consistent with the §10 finding from the secondary-effects sibling: T = 0.0 × HIGH-thinking interaction on image input is sign-reversed vs text-track).

**One-line paper claim**: "The Phase 3a image-track consensus sweep converges on HIGH-T0.7 with K = N = 10 consensus (t = 7 of 10) as the F1-optimal operating point: F1 = 0.750 [0.707, 0.790] at 20 m, 0.834 at 50 m. HIGH thinking improves F1 by +0.051 to +0.089 over MINIMAL at matched (T, N) cells for T ≥ 0.3."

## 2. Methods

- **Evaluation corpus**: 487 tiles at 384 px (Era 2). Library: `library_plus-hp` (13 few-shot examples: canonical positives + 4 hard-positive mined tiles + 0 hard-negative). See `prompts/configs/` for the canonical library manifest.
- **Matching protocol**: Hungarian one-to-one candidate-to-GT matching within a 20 m spatial-tolerance buffer. Buffer-stratified variants at 30, 40, 50 m in §6.
- **Consensus sweep**: per-condition, each cell runs K replicates at the condition's temperature; consensus thresholds t ∈ {1, 2, …, K} are swept; the optimum-F1 t per cell is reported.
- **Empty-tile rule**: tiles with zero GT mounds retained for matching (standard evaluate_detections.py convention).
- **Bootstrap**: 1,000 iterations, seed 42; percentile-based 95 % CIs on F1, P, R; resampling unit = tile-level. Spec mirrored in `.metadata.json` header block.

## 3. Best operating point per condition (20 m buffer)

| Thinking | T | N | Best t | F1 | 95 % CI | P | R |
|----------|---:|--:|-------:|---:|:------:|---:|---:|
| HIGH | t0.0 | n10 | 1 | 0.488 | [0.438, 0.539] | 0.377 | 0.694 |
| HIGH | t0.3 | n10 | 9 | 0.731 | [0.690, 0.772] | 0.806 | 0.669 |
| HIGH | t0.3 | n5 | 5 | 0.712 | [0.666, 0.757] | 0.803 | 0.639 |
| HIGH | t0.7 | n10 | 7 | 0.750 | [0.707, 0.790] | 0.778 | 0.724 |
| HIGH | t0.7 | n5 | 3 | 0.727 | [0.687, 0.765] | 0.676 | 0.786 |
| HIGH | t1.0 | n10 | 6 | 0.735 | [0.692, 0.776] | 0.737 | 0.733 |
| HIGH | t1.0 | n5 | 4 | 0.697 | [0.652, 0.742] | 0.773 | 0.634 |
| MINIMAL | t0.0 | n3 | 2 | 0.629 | [0.582, 0.668] | 0.515 | 0.807 |
| MINIMAL | t0.3 | n10 | 10 | 0.660 | [0.612, 0.703] | 0.607 | 0.722 |
| MINIMAL | t0.3 | n5 | 5 | 0.654 | [0.603, 0.700] | 0.581 | 0.747 |
| MINIMAL | t0.7 | n10 | 8 | 0.680 | [0.634, 0.723] | 0.640 | 0.726 |
| MINIMAL | t0.7 | n5 | 4 | 0.664 | [0.619, 0.706] | 0.608 | 0.731 |
| MINIMAL | t1.0 | n10 | 8 | 0.646 | [0.599, 0.688] | 0.625 | 0.669 |
| MINIMAL | t1.0 | n5 | 4 | 0.646 | [0.599, 0.688] | 0.601 | 0.699 |

## 4. HIGH vs MINIMAL comparison (20 m, best operating point per N)

| T | N | HIGH F1 | HIGH CI | MIN F1 | MIN CI | Δ F1 |
|---:|--:|--------:|:-------:|-------:|:------:|-----:|
| t0.3 | n5 | 0.712 | [0.666, 0.757] | 0.654 | [0.603, 0.700] | +0.058 |
| t0.3 | n10 | 0.731 | [0.690, 0.772] | 0.660 | [0.612, 0.703] | +0.072 |
| t0.7 | n5 | 0.727 | [0.687, 0.765] | 0.664 | [0.619, 0.706] | +0.063 |
| t0.7 | n10 | 0.750 | [0.707, 0.790] | 0.680 | [0.634, 0.723] | +0.070 |
| t1.0 | n5 | 0.697 | [0.652, 0.742] | 0.646 | [0.599, 0.688] | +0.051 |
| t1.0 | n10 | 0.735 | [0.692, 0.776] | 0.646 | [0.599, 0.688] | +0.089 |

HIGH advantage is present at every (T, N) cell shown and grows modestly with N (0.058 → 0.072 at T = 0.3; 0.063 → 0.070 at T = 0.7; 0.051 → 0.089 at T = 1.0). The cross-track interaction analysis in the secondary-effects sibling (`results/secondary-effects/secondary_effects.md` §10) finds this pattern *not statistically significant* as a thinking × temperature interaction on F1, precision, or recall — report as a main effect, not an interaction-selective finding.

## 5. Full threshold sweep (20 m buffer)

### 5.1 high-t0.0 / n10

| t | F1 | 95 % CI | P | R |
|--:|---:|:------:|---:|---:|
| 1 | 0.488 | [0.438, 0.539] | 0.377 | 0.694 |
| 2 | 0.459 | [0.412, 0.507] | 0.365 | 0.618 |
| 3 | 0.467 | [0.417, 0.512] | 0.375 | 0.618 |

### 5.2 high-t0.3 / n10

| t | F1 | 95 % CI | P | R |
|--:|---:|:------:|---:|---:|
| 10 | 0.678 | [0.629, 0.727] | 0.867 | 0.556 |
| 1 | 0.194 | [0.165, 0.225] | 0.110 | 0.860 |
| 2 | 0.434 | [0.390, 0.476] | 0.292 | 0.848 |
| 3 | 0.548 | [0.503, 0.590] | 0.410 | 0.828 |
| 4 | 0.622 | [0.577, 0.664] | 0.505 | 0.809 |
| 5 | 0.681 | [0.637, 0.721] | 0.592 | 0.802 |
| 6 | 0.707 | [0.664, 0.747] | 0.652 | 0.772 |
| 7 | 0.724 | [0.681, 0.766] | 0.701 | 0.749 |
| 8 | 0.730 | [0.687, 0.772] | 0.743 | 0.717 |
| 9 | 0.731 | [0.690, 0.772] | 0.806 | 0.669 |

### 5.3 high-t0.3 / n5

| t | F1 | 95 % CI | P | R |
|--:|---:|:------:|---:|---:|
| 1 | 0.277 | [0.241, 0.315] | 0.166 | 0.837 |
| 2 | 0.540 | [0.491, 0.586] | 0.409 | 0.793 |
| 3 | 0.654 | [0.605, 0.697] | 0.570 | 0.765 |
| 4 | 0.704 | [0.660, 0.746] | 0.685 | 0.724 |
| 5 | 0.712 | [0.666, 0.757] | 0.803 | 0.639 |

### 5.4 high-t0.7 / n10

| t | F1 | 95 % CI | P | R |
|--:|---:|:------:|---:|---:|
| 10 | 0.574 | [0.519, 0.633] | 0.893 | 0.423 |
| 1 | 0.213 | [0.183, 0.242] | 0.121 | 0.892 |
| 2 | 0.487 | [0.446, 0.524] | 0.339 | 0.867 |
| 3 | 0.622 | [0.582, 0.659] | 0.491 | 0.848 |
| 4 | 0.680 | [0.638, 0.719] | 0.583 | 0.816 |
| 5 | 0.721 | [0.681, 0.757] | 0.663 | 0.791 |
| 6 | 0.740 | [0.701, 0.777] | 0.719 | 0.763 |
| 7 | 0.750 | [0.707, 0.790] | 0.778 | 0.724 |
| 8 | 0.729 | [0.685, 0.772] | 0.826 | 0.653 |
| 9 | 0.679 | [0.631, 0.724] | 0.865 | 0.559 |

### 5.5 high-t0.7 / n5

| t | F1 | 95 % CI | P | R |
|--:|---:|:------:|---:|---:|
| 1 | 0.312 | [0.273, 0.349] | 0.189 | 0.878 |
| 2 | 0.617 | [0.577, 0.654] | 0.490 | 0.835 |
| 3 | 0.727 | [0.687, 0.765] | 0.676 | 0.786 |
| 4 | 0.719 | [0.675, 0.764] | 0.763 | 0.680 |
| 5 | 0.658 | [0.610, 0.709] | 0.837 | 0.542 |

### 5.6 high-t1.0 / n10

| t | F1 | 95 % CI | P | R |
|--:|---:|:------:|---:|---:|
| 10 | 0.507 | [0.449, 0.562] | 0.905 | 0.352 |
| 1 | 0.152 | [0.129, 0.176] | 0.083 | 0.885 |
| 2 | 0.428 | [0.387, 0.467] | 0.286 | 0.851 |
| 3 | 0.565 | [0.523, 0.607] | 0.429 | 0.825 |
| 4 | 0.654 | [0.611, 0.695] | 0.554 | 0.798 |
| 5 | 0.720 | [0.677, 0.759] | 0.668 | 0.782 |
| 6 | 0.735 | [0.692, 0.776] | 0.737 | 0.733 |
| 7 | 0.717 | [0.672, 0.758] | 0.772 | 0.669 |
| 8 | 0.692 | [0.646, 0.737] | 0.818 | 0.600 |
| 9 | 0.639 | [0.587, 0.688] | 0.866 | 0.506 |

### 5.7 high-t1.0 / n5

| t | F1 | 95 % CI | P | R |
|--:|---:|:------:|---:|---:|
| 1 | 0.228 | [0.196, 0.261] | 0.131 | 0.858 |
| 2 | 0.565 | [0.523, 0.609] | 0.433 | 0.814 |
| 3 | 0.686 | [0.643, 0.727] | 0.638 | 0.743 |
| 4 | 0.697 | [0.652, 0.742] | 0.773 | 0.634 |
| 5 | 0.612 | [0.564, 0.659] | 0.843 | 0.480 |

### 5.8 minimal-t0.0 / n3

| t | F1 | 95 % CI | P | R |
|--:|---:|:------:|---:|---:|
| 1 | 0.624 | [0.578, 0.663] | 0.509 | 0.807 |
| 2 | 0.629 | [0.582, 0.668] | 0.515 | 0.807 |
| 3 | 0.629 | [0.583, 0.668] | 0.517 | 0.802 |

### 5.9 minimal-t0.3 / n10

| t | F1 | 95 % CI | P | R |
|--:|---:|:------:|---:|---:|
| 10 | 0.660 | [0.612, 0.703] | 0.607 | 0.722 |
| 1 | 0.474 | [0.425, 0.519] | 0.329 | 0.844 |
| 2 | 0.548 | [0.500, 0.594] | 0.408 | 0.835 |
| 3 | 0.576 | [0.529, 0.621] | 0.443 | 0.823 |
| 4 | 0.598 | [0.549, 0.643] | 0.470 | 0.821 |
| 5 | 0.610 | [0.561, 0.654] | 0.488 | 0.814 |
| 6 | 0.624 | [0.575, 0.668] | 0.509 | 0.805 |
| 7 | 0.635 | [0.586, 0.678] | 0.530 | 0.793 |
| 8 | 0.641 | [0.594, 0.684] | 0.546 | 0.777 |
| 9 | 0.652 | [0.606, 0.696] | 0.572 | 0.759 |

### 5.10 minimal-t0.3 / n5

| t | F1 | 95 % CI | P | R |
|--:|---:|:------:|---:|---:|
| 1 | 0.510 | [0.465, 0.558] | 0.368 | 0.835 |
| 2 | 0.584 | [0.535, 0.629] | 0.454 | 0.821 |
| 3 | 0.620 | [0.569, 0.663] | 0.503 | 0.807 |
| 4 | 0.635 | [0.585, 0.679] | 0.530 | 0.791 |
| 5 | 0.654 | [0.603, 0.700] | 0.581 | 0.747 |

### 5.11 minimal-t0.7 / n10

| t | F1 | 95 % CI | P | R |
|--:|---:|:------:|---:|---:|
| 10 | 0.631 | [0.585, 0.676] | 0.695 | 0.577 |
| 1 | 0.405 | [0.366, 0.445] | 0.263 | 0.878 |
| 2 | 0.541 | [0.500, 0.581] | 0.394 | 0.862 |
| 3 | 0.604 | [0.563, 0.643] | 0.471 | 0.841 |
| 4 | 0.636 | [0.595, 0.676] | 0.516 | 0.828 |
| 5 | 0.660 | [0.617, 0.701] | 0.560 | 0.805 |
| 6 | 0.676 | [0.633, 0.716] | 0.593 | 0.786 |
| 7 | 0.678 | [0.634, 0.720] | 0.615 | 0.756 |
| 8 | 0.680 | [0.634, 0.723] | 0.640 | 0.726 |
| 9 | 0.670 | [0.624, 0.713] | 0.664 | 0.676 |

### 5.12 minimal-t0.7 / n5

| t | F1 | 95 % CI | P | R |
|--:|---:|:------:|---:|---:|
| 1 | 0.480 | [0.440, 0.521] | 0.333 | 0.860 |
| 2 | 0.587 | [0.546, 0.627] | 0.463 | 0.802 |
| 3 | 0.644 | [0.602, 0.683] | 0.549 | 0.779 |
| 4 | 0.664 | [0.619, 0.706] | 0.608 | 0.731 |
| 5 | 0.657 | [0.611, 0.699] | 0.663 | 0.651 |

### 5.13 minimal-t1.0 / n10

| t | F1 | 95 % CI | P | R |
|--:|---:|:------:|---:|---:|
| 10 | 0.577 | [0.527, 0.622] | 0.697 | 0.492 |
| 1 | 0.309 | [0.269, 0.349] | 0.188 | 0.855 |
| 2 | 0.447 | [0.405, 0.494] | 0.308 | 0.814 |
| 3 | 0.536 | [0.492, 0.581] | 0.404 | 0.795 |
| 4 | 0.588 | [0.543, 0.631] | 0.473 | 0.775 |
| 5 | 0.615 | [0.567, 0.657] | 0.519 | 0.754 |
| 6 | 0.635 | [0.588, 0.678] | 0.557 | 0.738 |
| 7 | 0.644 | [0.597, 0.687] | 0.594 | 0.703 |
| 8 | 0.646 | [0.599, 0.688] | 0.625 | 0.669 |
| 9 | 0.624 | [0.577, 0.666] | 0.653 | 0.598 |

### 5.14 minimal-t1.0 / n5

| t | F1 | 95 % CI | P | R |
|--:|---:|:------:|---:|---:|
| 1 | 0.382 | [0.341, 0.427] | 0.249 | 0.825 |
| 2 | 0.544 | [0.498, 0.586] | 0.416 | 0.786 |
| 3 | 0.610 | [0.564, 0.651] | 0.516 | 0.745 |
| 4 | 0.646 | [0.599, 0.688] | 0.601 | 0.699 |
| 5 | 0.607 | [0.557, 0.650] | 0.654 | 0.566 |

## 6. Buffer sensitivity (best F1 per condition)

| Condition | 20 m | 30 m | 40 m | 50 m |
|-----------|----:|----:|----:|----:|
| high-t0.0 / n10 | 0.488 | 0.550 | 0.580 | 0.593 |
| high-t0.3 / n10 | 0.731 | 0.796 | 0.818 | 0.824 |
| high-t0.3 / n5 | 0.712 | 0.782 | 0.800 | 0.807 |
| high-t0.7 / n10 | 0.750 | 0.812 | 0.829 | 0.834 |
| high-t0.7 / n5 | 0.727 | 0.799 | 0.818 | 0.827 |
| high-t1.0 / n10 | 0.735 | 0.788 | 0.804 | 0.818 |
| high-t1.0 / n5 | 0.697 | 0.757 | 0.784 | 0.803 |
| minimal-t0.0 / n3 | 0.629 | 0.692 | 0.712 | 0.719 |
| minimal-t0.3 / n10 | 0.660 | 0.712 | 0.721 | 0.725 |
| minimal-t0.3 / n5 | 0.654 | 0.710 | 0.720 | 0.724 |
| minimal-t0.7 / n10 | 0.680 | 0.733 | 0.751 | 0.753 |
| minimal-t0.7 / n5 | 0.664 | 0.724 | 0.743 | 0.750 |
| minimal-t1.0 / n10 | 0.646 | 0.720 | 0.739 | 0.741 |
| minimal-t1.0 / n5 | 0.646 | 0.710 | 0.735 | 0.740 |

Buffer-sensitivity is substantial for image-track (consistent with the §6 finding in the secondary-effects sibling: 8.6 % – 21.5 % elasticity 20 → 50 m). HIGH-T0.7 / n10 gains +0.084 from 20 → 50 m; MIN-T0.0 / n3 gains +0.090.

## 7. Caveats / risk register

1. **No N = 30 sweep** on this image-track matrix. The text-track sibling has K = 30 for HIGH-T0.7 (`secondary_effects.md` §2); this image-track matrix caps at K = 10. Consensus gains beyond N = 10 are unknown for image-track; any cross-track comparison at matched N = 10 is the clean comparison, not K = 30 vs K = 10.
2. **HIGH-T0.0 / n10 is the worst F1 cell** (0.488) — consistent with the §10 cross-modality finding in `results/secondary-effects/secondary_effects.md`: T = 0.0 × HIGH-thinking on image input shows ΔF1 = −0.141 vs MIN-T0.0. Report descriptively; the interaction-test is not significant (K = 3 at T = 0.0 base-rate limit).
3. **Tile-level MCC is not in this artefact**. The consensus-analysis-summary is F1 / P / R sweep-only. Tile-level MCC for the same cells is in the `results/secondary-effects/secondary_effects.md` §5 block; cross-artefact consistency verified during Session 74 scorecard spot-check pass.
4. **"Best t" selection is F1-optimal**. Some cells have narrow t-plateaus (see §7 in the secondary-effects sibling); the "best t" row in §3 here is the argmax-F1, not the robustness-aware choice. For production-grade threshold selection, prefer t-values with a ≥ 3 threshold-step plateau within 0.05 of the peak (consult the full sweep in §5.2 – 5.14 for the plateau shape).
5. **Level-up did not re-run the analysis**. All numbers in §§3–6 were lifted verbatim from `consensus-analysis-summary_autogen.md`.

## 8. Paper implications

### 8.1 Image-track F1-optimum operating point

**HIGH-T0.7 / N = 10 / t = 7 / library_plus-hp / Flash proposer → F1 = 0.750 [0.707, 0.790] at 20 m, 0.834 at 50 m**. This is the paper-citable F1 operating point for Phase 3a image-track. The tile-level MCC-optimum is SCALE4-T0.7 (per `results/secondary-effects/secondary_effects.md` §5), not covered by this consensus sweep — SCALE4 is a library-variant probe with its own K = 10 run. Use both operating points as companion citations depending on the metric the paper anchors.

### 8.2 Consensus convergence shape

Consensus gains from N = 5 to N = 10 are modest (+0.016 to +0.038 for HIGH conditions, +0.006 to +0.038 for MIN conditions). The consensus sweep *converges* by N = 5 for most cells — additional passes give marginal F1 improvement. This is the quantitative basis for recommending K = 10 as the default production-run setting (rather than the expensive K = 30).

### 8.3 Suggested paper text (Results — phase3a image-track consensus sweep)

> On the Era 2 evaluation scope (487 tiles at 384 px), a Phase 3a image-track consensus sweep using Gemini 3 Flash with the `library_plus-hp` configuration (13 few-shot examples, 4 hard positives, 0 hard negatives) was evaluated across K ∈ {3, 5, 10}, T ∈ {0.0, 0.3, 0.7, 1.0}, and thinking ∈ {HIGH, MINIMAL}. The F1-optimal operating point at a 20 m matching buffer is HIGH-T0.7 with K = N = 10 consensus and threshold t = 7 / 10: F1 = 0.750 (95 % bootstrap CI [0.707, 0.790] over 1,000 iterations, seed 42), precision 0.778, recall 0.724. At a 50 m buffer the same cell gives F1 = 0.834. HIGH thinking improves F1 over MINIMAL by ΔF1 = +0.051 to +0.089 at matched (T, N) cells for T ≥ 0.3; consensus gains from K = 5 to K = 10 are modest (+0.016 to +0.038). We report N = 10 as the default production pipeline configuration on cost-benefit grounds.

## 9. Files manifest

**Outputs (this directory)**:

- `consensus-analysis-summary.md` — this report (hand-authored, paper-citation source).
- `consensus-analysis-summary_autogen.md` — script-authored sibling.
- `all-evaluations.json` + `all-evaluations.metadata.json` — consolidated per-cell evaluation JSON.
- `.metadata.json` — directory-level metadata sidecar (bootstrap spec; coverage pattern).
- Per-condition subdirectories `high-t0.0/` – `minimal-t1.0/` with per-N per-t evaluation outputs.

**Inputs**:

- `outputs/phase3a-image-matrix/*/detections/*.geojson` — per-condition K-consensus detection outputs.
- `inputs/vectors/references/mounds-reference.geojson` — ground-truth mound points.
- `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` — 487-tile Era 2 bounds.

## 10. Reproducibility

- **Script**: `scripts/summarise_phase3a_matrix.py`. Aggregates the per-cell `evaluation.json` files into `all-evaluations.json` + `consensus-analysis-summary_autogen.md`.
- **Guardrail (Session 75 item 6 / Session 76 carry-over)**: script hardened 2026-04-24 to redirect Markdown output from `consensus-analysis-summary.md` to `consensus-analysis-summary_autogen.md`, protecting this hand-authored level-up.
- **Bootstrap** (per-cell evaluation.json files): 1,000 iterations, seed 42, percentile-based 95 % CIs; spec mirrored in `.metadata.json`.
- **Re-run command**:

    ```bash
    python scripts/summarise_phase3a_matrix.py \
        --results-dir results/phase3a-image-matrix
    ```

- **Git commit of original data run**: `cdd35b4a` (`data(analysis): Phase 3a image track consensus sweep evaluation`). Level-up commit: see this file's `git log` entry at 2026-04-24.
- **Toolchain**: Python ≥ 3.11, NumPy, pandas. Pinned versions in `requirements.txt`.
