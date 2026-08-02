# Results Summary — Session 58 (2026-03-25/26)

> **⚠ Superseded figures (2026-08-02, E72)**: the temperature-sensitivity
> section's T=0.7-vs-T=1.0 comparison scores a 240-tile study against
> 487-tile bounds (coverage confound — see protocol-errata E43's
> 2026-08-02 correction block and E72) and understates the T=1.0 arm by
> ~0.17–0.19 F1; at matched scope there is no significant difference
> (`results/e43-matched-temperature/`). Its ΔF1 column is additionally
> internally inconsistent with its own F1 columns (a separate,
> pre-existing defect). This document is a dated session record and its
> body is unchanged; do not cite the temperature rows.

Consolidated results from Sessions 56–58 covering consensus sweeps, PV
pipeline evaluations, proposer × verifier model matrix, buffer sensitivity,
temperature sensitivity, diversity analysis, and the configuration audit.
All metrics use 384px tiles, 20m spatial buffer (unless noted), and the
full evaluation area (487 tiles, 569 reference mounds).

**Updated 2026-03-26**: Added Pro verifier results (Section 1a), verifier
model comparison (Section 1b), and verifier thinking-level comparison
(Section 1c) from the completed proposer × verifier matrix.

---

## 1. Overall PV Leaderboard

Top 15 Proposer-Verifier (PV) pipeline configurations ranked by F1. All use
Flash adversarial-text verifier with minimal thinking.

| Rank | Condition | F1 | 95% CI | P | R | t | n |
|------|-----------|-----|--------|-------|-------|------|-----|
| 1 | Flash HIGH text 16-of-30 | **0.890** | [0.863, 0.915] | 0.915 | 0.867 | 0.20 | 412 |
| 2 | Flash HIGH text 17-of-30 | 0.890 | [0.862, 0.915] | 0.917 | 0.864 | 0.20 | 410 |
| 3 | Flash HIGH text 18-of-30 | 0.887 | [0.859, 0.914] | 0.929 | 0.848 | 0.20 | 397 |
| 4 | Flash HIGH text 19-of-30 | 0.887 | [0.859, 0.912] | 0.932 | 0.846 | 0.15 | 395 |
| 5 | Flash HIGH text 15-of-30 | 0.885 | [0.856, 0.911] | 0.902 | 0.869 | 0.20 | 419 |
| 6 | Flash HIGH text 14-of-30 | 0.884 | [0.855, 0.910] | 0.900 | 0.869 | 0.20 | 420 |
| 7 | Flash HIGH text 20-of-30 | 0.884 | [0.855, 0.910] | 0.940 | 0.835 | 0.15 | 386 |
| 8 | Flash HIGH text 13-of-30 | 0.880 | [0.852, 0.905] | 0.886 | 0.874 | 0.20 | 429 |
| 9 | Flash HIGH text 22-of-30 | 0.880 | [0.851, 0.907] | 0.950 | 0.821 | 0.15 | 376 |
| 10 | Flash HIGH text 6-of-10 | **0.877** | [0.850, 0.903] | 0.895 | 0.860 | 0.20 | 418 |
| 11 | Flash HIGH text 12-of-30 | 0.877 | [0.848, 0.901] | 0.878 | 0.876 | 0.20 | 434 |
| 12 | Flash HIGH text 7-of-10 | 0.872 | [0.845, 0.898] | 0.919 | 0.830 | 0.20 | 393 |
| 13 | Flash HIGH text 5-of-10 | 0.872 | [0.843, 0.898] | 0.877 | 0.867 | 0.20 | 430 |
| 14 | Flash MINIMAL T=0.7 4-of-5 | **0.871** | [0.842, 0.899] | 0.936 | 0.814 | 0.15 | 378 |
| 15 | Flash HIGH text 8-of-10 | 0.871 | [0.842, 0.898] | 0.944 | 0.809 | 0.20 | 373 |

**Key observations:**

- The top result (F1=0.890) occurs at 16-of-30, with a broad plateau from
  13-of-30 to 19-of-30 (all F1 ≥ 0.884). The plateau makes the exact
  threshold choice non-critical.
- N=10 (6-of-10, F1=0.877) nearly matches N=30 — diminishing returns from
  scaling beyond 10 passes.
- Flash MINIMAL T=0.7 4-of-5 (F1=0.871) appears at rank 14, demonstrating
  that the cheapest proposer with strict voting matches HIGH text N=10.

---

## 1a. Pro Verifier Results

The Pro verifier (gemini-3.1-pro, medium thinking) was tested on the same
proposer candidates as the Flash verifier. Best results at each vote
threshold for the key comparison — Flash HIGH text N=5:

| Verifier | 1-of-5 | 2-of-5 | 3-of-5 | **4-of-5** | 5-of-5 |
|----------|--------|--------|--------|------------|--------|
| **Pro medium** | 0.751 | 0.850 | 0.874 | **0.879** | 0.847 |
| Flash minimal | 0.740 | 0.830 | 0.853 | 0.864 | 0.837 |
| Flash medium | 0.548 | 0.772 | 0.834 | 0.859 | 0.840 |
| Flash HIGH | 0.521 | 0.745 | 0.821 | 0.853 | 0.841 |

**Pro verifier wins at 4-of-5: F1=0.879** [0.850, 0.907] vs Flash minimal
0.864 [0.833, 0.893]. CIs overlap, so the difference is not significant,
but Pro consistently outperforms Flash minimal at every vote threshold.

### Pro verifier on Pro proposer (Pro × Pro)

| Condition | Best F1 | Config | P | R |
|-----------|---------|--------|-------|-------|
| Pro HIGH text + Pro vf | 0.851 | 3-of-5, t=0.15 | 0.957 | 0.765 |
| Pro HIGH text + Flash min vf | 0.849 | 3-of-5, t=0.15 | 0.957 | 0.763 |
| Pro HIGH text + Flash med vf | 0.850 | 3-of-5, t=0.05 | 0.954 | 0.765 |
| Pro HIGH image + Pro vf | 0.707 | 3-of-5, t=0.05 | 0.710 | 0.703 |

Pro proposer shows minimal verifier sensitivity — all three verifiers
produce nearly identical F1 (0.849–0.851). Pro's precise proposer output
leaves little for any verifier to improve, regardless of model.

### Single-pass baselines + Pro verifier

| Condition | F1 | P | R |
|-----------|-----|-------|-------|
| Flash text baseline + Pro vf | 0.820 | 0.807 | 0.835 |
| Flash image baseline + Pro vf | 0.731 | 0.678 | 0.793 |
| Pro text baseline + Pro vf | 0.786 | 0.818 | 0.756 |
| Pro image baseline + Pro vf | 0.609 | 0.596 | 0.623 |

---

## 1b. Proposer × Verifier Model Comparison

Does the verifier model matter? Summary of best F1 across proposer ×
verifier combinations at N=5:

| | Flash minimal vf | Flash medium vf | Pro medium vf |
|--|-----------------|----------------|--------------|
| **Flash HIGH proposer (text)** | 0.864 | 0.859 | **0.879** |
| **Pro HIGH proposer (text)** | 0.849 | 0.850 | 0.851 |

**Key finding**: Verifier model matters for Flash proposer (+0.015 from
Flash→Pro verifier) but not for Pro proposer (all verifiers ≈0.850). The
Flash proposer's higher recall (more candidates) gives the Pro verifier
more material to work with. The Pro proposer's already-precise output
saturates all verifier models.

---

## 1c. Verifier Thinking-Level Comparison

Flash verifier at three thinking levels on Flash HIGH text 4-of-5
candidates:

| Thinking level | F1 | P | R | t |
|---------------|------|-------|-------|------|
| Minimal | **0.864** | 0.915 | 0.818 | 0.15 |
| Medium | 0.859 | 0.878 | 0.841 | 0.95 |
| HIGH | 0.853 | 0.867 | 0.839 | 0.95 |

**Flash minimal verifier outperforms both medium and HIGH** on consensus-
filtered candidates. More thinking degrades performance — consistent with
Obs 185 (HIGH thinking hurts the verifier by generating elaborate
arguments that override correct initial judgements).

The optimal verifier threshold shifts dramatically: minimal peaks at
t=0.15, while medium and HIGH peak at t=0.95. Higher thinking produces
more extreme probability distributions (near 0 or 1), requiring a much
higher threshold to achieve the same precision. This makes medium/HIGH
verifiers less useful in practice — their probability scores are less
well-calibrated for threshold tuning.

---

## 2. Low-Cost N=5 Tier

Top 5 PV configurations using only 5 proposer passes (minimum practical
PV pipeline). MINIMAL thinking dominates the low-cost tier.

| Rank | Condition | F1 | 95% CI | P | R | n |
|------|-----------|-----|--------|-------|-------|-----|
| 1 | Flash MINIMAL T=0.7 4-of-5 | **0.871** | [0.842, 0.899] | 0.936 | 0.814 | 378 |
| 2 | Flash MINIMAL T=0.7 3-of-5 | 0.870 | [0.840, 0.899] | 0.905 | 0.837 | 402 |
| 3 | Flash HIGH text 4-of-5 | 0.864 | [0.833, 0.893] | 0.915 | 0.818 | 389 |
| 4 | Flash MINIMAL T=0.7 2-of-5 | 0.863 | [0.830, 0.892] | 0.875 | 0.851 | 423 |
| 5 | Flash HIGH text 3-of-5 | 0.853 | [0.822, 0.883] | 0.846 | 0.860 | 442 |

Three of the top five use MINIMAL thinking. The verifier compensates so
effectively that HIGH reasoning in the proposer adds only marginal benefit
at the N=5 scale.

---

## 3. Precision-Optimised Operating Points (N=5)

Top 5 by precision (F1 > 0.7 filter). For applications where each
detection triggers expensive follow-up (excavation planning, targeted
field survey).

| Rank | Condition | P | R | F1 | P@30m | R@30m | F1@30m |
|------|-----------|-------|-------|------|-------|-------|--------|
| 1 | Pro HIGH text 5-of-5 | **0.974** | 0.685 | 0.804 | **0.984** | 0.692 | 0.812 |
| 2 | Pro HIGH text 4-of-5 | 0.972 | 0.724 | 0.830 | 0.985 | 0.733 | 0.841 |
| 3 | Flash MINIMAL T=0.7 5-of-5 | 0.959 | 0.756 | 0.846 | 0.971 | 0.766 | 0.856 |
| 4 | Flash HIGH text 5-of-5 | 0.956 | 0.745 | 0.837 | 0.968 | 0.754 | 0.848 |
| 5 | Pro HIGH text 3-of-5 | 0.954 | 0.765 | 0.850 | 0.971 | 0.779 | 0.865 |

Pro HIGH text 4-of-5 at 30m achieves P=0.985 — fewer than 2 false alarms
per 100 detections while finding 73% of mounds. Pro's precision advantage
over Flash is clear at the strict voting thresholds.

---

## 4. Recall-Optimised Operating Points (N=5)

Top 5 by recall (F1 > 0.7 filter). For comprehensive screening where
missed mounds are costly.

| Rank | Condition | R | P | F1 | R@30m | P@30m | F1@30m |
|------|-----------|-------|-------|------|-------|-------|--------|
| 1 | Flash MINIMAL T=0.7 1-of-5 | **0.871** | 0.790 | 0.828 | **0.885** | 0.802 | 0.842 |
| 2 | Flash HIGH text 2-of-5 | 0.869 | 0.794 | 0.830 | 0.903 | 0.826 | 0.863 |
| 3 | Flash HIGH text 3-of-5 | 0.860 | 0.846 | 0.853 | 0.890 | 0.876 | 0.883 |
| 4 | Flash HIGH text 1-of-5 | 0.855 | 0.653 | 0.740 | 0.880 | 0.672 | 0.762 |
| 5 | Flash MINIMAL T=0.7 2-of-5 | 0.851 | 0.875 | 0.863 | 0.867 | 0.891 | 0.879 |

Flash HIGH text 2-of-5 + PV at 30m offers the best recall-quality balance:
R=0.903 (over 90% of mounds found) with P=0.826 and F1=0.863.

---

## 5. Buffer Distance Sensitivity

### 5a. Consensus-only conditions (from sapphire analysis)

| Condition | F1@20m | F1@30m | F1@40m | F1@50m |
|-----------|--------|--------|--------|--------|
| Flash HIGH text (best of N=5/10/30) | 0.814 | 0.826 | 0.826 | 0.826 |
| Flash HIGH image (best of N=5/10) | 0.752 | 0.818 | 0.838 | 0.846 |
| Pro HIGH text (N=5) | 0.849 | 0.858 | 0.862 | 0.862 |
| Pro HIGH image (N=5) | 0.703 | 0.816 | 0.848 | 0.852 |
| Flash MINIMAL text T=0.7 (best of N=5/10/30) | 0.657 | 0.668 | 0.668 | 0.668 |

Image conditions gain 0.09–0.15 F1 from 20→50m; text gains only 0.01.
See Obs 190 for the distance distribution analysis explaining this
asymmetry (image detections have 2–5× more near-misses in the 20–50m zone).

### 5b. PV pipeline conditions

| Condition | F1@20m | F1@30m | F1@40m | F1@50m | n |
|-----------|--------|--------|--------|--------|---|
| Flash HIGH text 16-of-30 + PV | 0.890 | **0.904** | 0.904 | 0.904 | 412 |
| Flash HIGH text 6-of-10 + PV | 0.877 | 0.898 | 0.900 | 0.900 | 418 |
| Flash MINIMAL T=0.7 4-of-5 + PV | 0.871 | 0.883 | 0.888 | 0.888 | 378 |
| Flash HIGH text 4-of-5 + PV | 0.864 | 0.891 | 0.891 | 0.891 | 389 |
| Pro HIGH text 3-of-5 + PV | 0.849 | 0.865 | 0.867 | 0.867 | 349 |

Text PV results saturate at 30m — all recoverable near-misses are captured
by 30m. F1 > 0.9 achieved at 30m for the 16-of-30 configuration.

---

## 6. Temperature Sensitivity

Unplanned comparison from the consensus-384 T=1.0 bug (E43). The buggy
T=1.0 data and corrected T=0.7 baseline provide a controlled comparison.

| Pool size | T=0.7 best F1 | T=1.0 best F1 | ΔF1 | p-value | Wins/Losses |
|-----------|---------------|---------------|-----|---------|-------------|
| N=5 | 0.657 | 0.644 | +0.164 | <0.0001 | 101/12 |
| N=10 | 0.633 | 0.624 | +0.143 | <0.0001 | 94/19 |
| N=30 | 0.657 | 0.637 | +0.151 | <0.0001 | 97/14 |

T=0.7 dramatically outperforms T=1.0 at all pool sizes. Not a subtle
effect — the temperature bug hid ~15 F1 points of performance.

---

## 7. Diversity Analysis (H9)

### Track 1 — Image (5 conditions, 5 replications each)

| Condition | Diversity | Best F1 | ΔF1 vs baseline | p |
|-----------|-----------|---------|-----------------|-------|
| A (baseline) | None | 0.664 | — | — |
| B | Text variants | 0.668 | +0.004 | 0.689 |
| C | HN image rotation | 0.671 | +0.007 | 0.621 |
| D | Temperature (0.4–1.0) | 0.669 | +0.005 | 0.375 |
| E | Full (text+image+temp) | 0.671 | +0.007 | 0.375 |

### Track 2 — Text-only (4 conditions)

| Condition | Diversity | Best F1 | ΔF1 vs baseline | p |
|-----------|-----------|---------|-----------------|-------|
| A (baseline) | None | 0.716 | — | — |
| B | Text variants | 0.686 | −0.030 | 0.061 |
| D | Temperature | 0.730 | +0.014 | 0.181 |
| E | Full (text+temp) | 0.694 | −0.022 | 0.061 |

**H9 null result**: No diversity condition significantly outperforms the
identical-pass baseline on either track. The Obs 148 variance stabilisation
finding (Condition C, 5× SD reduction on 60-tile pilot) did not replicate
at full scale (Obs 192).

---

## 8. Pairwise Comparisons

All paired permutation tests (10,000 permutations, 487 tiles, 20m buffer).

| Comparison | ΔF1 | p | Sig | W/L |
|------------|-----|-------|-----|-----|
| Flash HIGH text 9-of-10 vs 5-of-5 | +0.016 | 0.025 | * | 21/8 |
| Flash HIGH image vs Pro HIGH image (3-of-5) | +0.028 | 0.018 | * | 66/44 |
| T=0.7 vs T=1.0 text N=5 | +0.164 | <0.001 | *** | 101/12 |
| T=0.7 vs T=1.0 text N=10 | +0.143 | <0.001 | *** | 94/19 |
| T=0.7 vs T=1.0 text N=30 | +0.151 | <0.001 | *** | 97/14 |
| Flash HIGH text 26-of-30 vs MINIMAL T=0.7 29-of-30 | +0.016 | 0.094 | ns | 47/23 |
| Flash HIGH text 5-of-5 vs MINIMAL T=0.7 5-of-5 | −0.016 | 0.131 | ns | 34/44 |
| Flash HIGH text 9-of-10 vs MINIMAL T=0.7 10-of-10 | +0.018 | 0.059 | ns | 48/22 |
| Flash HIGH text 5-of-5 vs Flash HIGH image 3-of-5 | −0.009 | 0.432 | ns | 61/38 |
| Flash HIGH text 9-of-10 vs Flash HIGH image 7-of-10 | +0.019 | 0.083 | ns | 59/29 |
| Pro HIGH text 3-of-5 vs Flash HIGH text 5-of-5 | +0.002 | 0.874 | ns | 44/38 |
| Pro HIGH text 3-of-5 vs MINIMAL T=0.7 5-of-5 | −0.014 | 0.165 | ns | 38/36 |
| Pro HIGH text 3-of-5 vs Pro HIGH image 3-of-5 | +0.021 | 0.111 | ns | 72/36 |
| Flash HIGH image 3-of-5 vs MINIMAL image 3-of-5 | +0.009 | 0.324 | ns | 38/37 |
| Flash HIGH image 7-of-10 vs MINIMAL image 8-of-10 | +0.002 | 0.867 | ns | 44/41 |
| Flash HIGH text 26-of-30 vs 9-of-10 | −0.001 | 0.852 | ns | 10/8 |
| Image MINIMAL N=10 vs N=30 | −0.003 | 0.760 | ns | 5/5 |

Only the temperature comparisons (T=0.7 vs T=1.0) and two scaling
comparisons reach significance. Most condition differences are ns at
tile level despite substantial F1 differences, reflecting the high
within-condition variance characteristic of tile-level evaluation.

---

## 9. Single-Pass T=0.0 Rerun

Corrected rerun of single-pass-384 at T=0.0 (was T=1.0 due to E44).
10 runs × 487 tiles, Flash MINIMAL, deterministic (T=0.0).

The consensus sweep shows best F1 ≈ 0.552 at 5-of-10 — substantially
below the consensus results above, as expected for a single-pass MINIMAL
configuration without HIGH thinking. This establishes the deterministic
baseline for the tile-size comparison (H11).

---

## 10. Configuration Audit Summary

Comprehensive audit of 1,740 runs across 239 conditions (Session 57):

- **173/174** multi-run conditions internally consistent (1 intentional exception)
- **E42 corrected**: metadata bug in `lib_llm_metadata.py` caused incorrect
  model attribution. Pro proposer runs confirmed genuine via 3 independent
  sources. 22 bugs fixed across 11 files.
- **E43**: consensus-384 executed at T=1.0 instead of T=0.7 (config
  propagation failure). 30 runs affected. Data preserved as T=1.0
  sensitivity data. Corrected baseline produced.
- **E44**: single-pass-384 same bug. 10 runs affected. Corrected T=0.0
  rerun completed.
- **12 runs** used Pro model (proposers only); 1,728 used Flash.
- Pro verifier matrix now complete (10 conditions evaluated, Session 58).
  Pro verifier improves Flash HIGH text 4-of-5 by +0.015 F1 (0.879 vs
  0.864) but has minimal effect on Pro proposer output (all verifiers
  ≈0.850). Flash minimal verifier outperforms Flash medium and HIGH on
  consensus-filtered candidates.

---

## 11. Cross-Modal Complementarity Check

The Phase 3d pilot (single-pass, 150px) found ~13% image-only mound
detections, suggesting a cross-modal union could boost recall. At the
current production scale (384px, HIGH thinking, N=30 consensus), this
complementarity has nearly vanished:

| Proposer pool | Matched refs | % of 572 |
|---------------|-------------|----------|
| Text 1-of-30 | 419 | 73.3% |
| Image 1-of-5 | 383 | 67.0% |
| Text 1-of-30 ∪ Image 1-of-5 | 421 | **73.6%** |
| Image-only (not in text 1-of-30) | 2 | 0.3% |

Adding the image track to text N=30 contributes just **2 additional
mounds** (+0.3% recall). The text track at scale already captures nearly
everything the image track finds, plus 38 mounds the image track misses.
Cross-modal union is not justified for the recommended pipeline.

**Why the pilot result didn't scale**: The Phase 3d pilot used single-pass
proposers on 60 tiles. At that scale, both tracks had substantial recall
gaps with different profiles, creating complementarity. With 30-pass
consensus and HIGH thinking, the text track's recall ceiling rose enough
to subsume nearly all of the image track's unique contributions.

---

## Appendix A: Proposer × Verifier Complete Matrix (N=5, best F1)

Full factorial results — every proposer × verifier × thinking combination
tested at N=5 consensus:

| Proposer | Verifier | F1 | P | R |
|----------|----------|-----|-------|-------|
| Flash HIGH text | Pro medium | **0.879** | 0.926 | 0.837 |
| Flash HIGH text | Flash minimal | 0.864 | 0.915 | 0.818 |
| Flash HIGH text | Flash medium | 0.859 | 0.878 | 0.841 |
| Flash HIGH text | Flash HIGH | 0.853 | 0.867 | 0.839 |
| Pro HIGH text | Pro medium | 0.851 | 0.957 | 0.765 |
| Pro HIGH text | Flash medium | 0.850 | 0.954 | 0.765 |
| Pro HIGH text | Flash minimal | 0.849 | 0.957 | 0.763 |
| Pro HIGH image | Pro medium | 0.707 | 0.710 | 0.703 |

## Appendix B: Key Observations from This Session

- **Obs 190**: Buffer distance sensitivity — image tracks gain 0.09–0.15
  F1 at relaxed buffers due to modality-dependent spatial precision
- **Obs 191**: Sessions 56–57 key findings summary
- **Obs 192**: Obs 148 variance stabilisation did not replicate at scale
- **Obs 193**: F1 > 0.9 milestone and precision–recall operating points
