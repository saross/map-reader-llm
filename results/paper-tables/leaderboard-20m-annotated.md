# VLM Burial Mound Detection: Comprehensive Leaderboard

**Evaluation tolerance**: 20m (preregistered primary)
**Tier clustering**: 325 pairwise permutation tests (10,000 iterations,
seed 42), FDR-corrected at q=0.05. Conditions within the same tier are
statistically indistinguishable.
**Date**: 2026-03-29 (updated with Pro N=10 results)

## How to read this table

- **F1/P/R** are mound-level metrics: does the system detect each
  individual burial mound? Evaluated by centroid-to-centroid matching
  within 20m, with the Hungarian algorithm for globally optimal
  one-to-one assignment per map sheet.
- **MCC/Sens/Spec** are tile-level metrics: does the system correctly
  classify whether each 384px tile (~1,920m ground extent) contains any
  mound? These are buffer-independent.
- **95% CIs** from 1,000-iteration stratified bootstrap (seed 42).

## Abbreviations

| Abbreviation | Meaning |
|---|---|
| FH | Flash HIGH thinking (Gemini 3 Flash, extended reasoning) |
| FM | Flash MINIMAL thinking (Gemini 3 Flash, minimal reasoning) |
| Pro H | Pro HIGH thinking (Gemini 3.1 Pro, extended reasoning) |
| PV | Proposer-Verifier two-stage pipeline |
| min vf | Flash MINIMAL thinking verifier |
| med vf | Flash MEDIUM thinking verifier |
| N/K | Pool size N, consensus threshold K (e.g., 16/30 = 16-of-30 agreement) |
| T=X | Temperature parameter |

---

## Tier 1 — Best (solitary)

| # | Condition | F1 | 95% CI | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|---|:---:|:---:|:---:|---|:---:|:---:|
| 1 | FH text 16/30 + PV (min vf) | **0.890** | [0.863, 0.915] | 0.915 | 0.867 | 0.790 | [0.733, 0.840] | 0.821 | 0.957 |

The only condition to stand alone at 20m. Uses the largest proposer pool
(N=30, threshold 16) feeding the cheapest verifier (Flash MINIMAL). The
large pool catches mounds that smaller pools miss, and the verifier's
high specificity (0.957) filters false positives without losing true
detections.

This condition **separates from Tier 2 at 20m** (p=0.040 vs #2, p=0.021
vs #3 after FDR). At 30m tolerance, the top 3 were statistically
indistinguishable — the tighter tolerance reveals #1's recall advantage
from the large proposer pool.

---

## Tier 2 — Strong PV and best consensus (F1: 0.836–0.864)

| # | Condition | F1 | 95% CI | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|---|:---:|:---:|:---:|---|:---:|:---:|
| 2 | FH text 4/5 + PV (min vf) | 0.864 | [0.833, 0.893] | 0.915 | 0.818 | 0.769 | [0.716, 0.820] | 0.786 | 0.965 |
| 3 | FH text 4/5 + PV (med vf) | 0.859 | [0.827, 0.887] | 0.878 | 0.841 | 0.739 | [0.679, 0.793] | 0.804 | 0.926 |
| 4 | FH text 9/10 + PV (min vf) | 0.856 | [0.825, 0.885] | **0.957** | 0.775 | 0.749 | [0.696, 0.797] | 0.738 | **0.981** |
| 5 | Pro H text 3/5 + PV (min vf) | 0.849 | [0.812, 0.883] | **0.957** | 0.763 | 0.730 | [0.676, 0.783] | 0.703 | **0.988** |
| 6 | Pro H text 3/5 (N=5 cons.) | 0.840 | [0.800, 0.875] | 0.918 | 0.775 | 0.736 | [0.682, 0.788] | 0.747 | 0.965 |
| 7 | Pro H text 6/10 (N=10 cons.) | 0.837 | [0.798, 0.874] | 0.921 | 0.767 | 0.710 | [0.654, 0.764] | 0.703 | 0.973 |

**Key observations:**

- **Pro N=10 (#7) does not improve over Pro N=5 (#6).** F1 drops
  marginally from 0.840 to 0.837 (well within CIs). This confirms the
  **pool-size plateau** — Pro does not benefit from larger consensus
  pools, paralleling the Flash result where N=5→N=10 was also
  non-significant. Pro's high per-run quality means consensus adds
  little beyond N=5.
- **Pro consensus without a verifier (#6) sits alongside Flash PV
  conditions.** Pro's inherent precision (0.918) is high enough that the
  verifier adds little (+0.009 F1, not significant at 20m).
- **#4 and #5 achieve the highest precision** of any conditions (0.957)
  but sacrifice recall. The strict consensus thresholds (9-of-10,
  3-of-5) filter aggressively; the verifier then has very little to
  reject (specificity 0.981–0.988).
- **#3 (medium verifier) recovers more recall** than the minimal verifier
  (#2) at the cost of some precision — the softer threshold (0.95 vs
  0.15) retains more borderline detections.
- **Flash + pipeline matches Pro** — #2 (Flash, F1=0.864) is
  indistinguishable from #5 (Pro, F1=0.849) despite Pro costing ~10×
  more per API call.

---

## Tier 3 — Good PV and large-pool consensus (F1: 0.778–0.814)

| # | Condition | F1 | 95% CI | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|---|:---:|:---:|:---:|---|:---:|:---:|
| 8 | Text baseline + PV | 0.814 | [0.780, 0.844] | 0.789 | 0.841 | 0.833 | [0.783, 0.877] | 0.869 | 0.957 |
| 9 | FH text 26/30 (consensus) | 0.814 | [0.778, 0.846] | 0.834 | 0.795 | 0.620 | [0.549, 0.691] | 0.777 | 0.841 |
| 10 | FH image 3/5 + PV | 0.778 | [0.735, 0.816] | 0.800 | 0.756 | 0.827 | [0.777, 0.873] | 0.847 | 0.969 |

**Key observations:**

- **The text baseline + PV (#8) is striking:** a naive single-pass
  proposer (no consensus, no HIGH thinking) plus a verifier outperforms
  most consensus-only conditions. The verifier compensates for poor
  proposer precision. This demonstrates that the verifier stage is
  independently valuable — it does not merely polish already-good
  consensus output.
- **FH image 3/5 + PV (#10)** reaches this tier despite image modality's
  lower raw performance. The verifier rescues image-based detection,
  closing roughly half the text-image gap.
- **Note the MCC divergence:** #8 and #10 have high tile-level MCC
  (0.833, 0.827) despite lower mound-level F1, indicating accurate
  tile classification but imprecise mound localisation at 20m.

---

## Tier 4 — Mid-range consensus, HIGH thinking, text (F1: 0.779–0.797)

| # | Condition | F1 | 95% CI | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|---|:---:|:---:|:---:|---|:---:|:---:|
| 11 | FH text 9/10 (consensus) | 0.797 | [0.757, 0.830] | 0.800 | 0.793 | 0.621 | [0.545, 0.691] | 0.795 | 0.826 |
| 12 | FH text 5/5 (consensus) | 0.779 | [0.739, 0.817] | 0.798 | 0.761 | 0.600 | [0.529, 0.671] | 0.769 | 0.830 |

Flash HIGH text consensus conditions **without a verifier**. The N=5 and
N=10 pools are statistically indistinguishable — bigger pools do not
help without a verifier to exploit the additional recall. Consensus alone
hits a ceiling around F1=0.80 for Flash.

---

## Tier 5 — Image modality ceiling (F1: 0.700–0.750)

| # | Condition | F1 | 95% CI | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|---|:---:|:---:|:---:|---|:---:|:---:|
| 13 | FH image 7/10 (consensus) | 0.750 | [0.707, 0.790] | 0.778 | 0.724 | ~0.675 | [0.604, 0.736] | 0.838 | 0.837 |
| 14 | FH image 3/5 (consensus) | 0.727 | [0.687, 0.765] | 0.676 | 0.786 | 0.665 | [0.598, 0.724] | 0.856 | 0.810 |
| 15 | Image baseline + PV | 0.717 | [0.673, 0.754] | 0.663 | 0.779 | **0.877** | [0.833, 0.919] | **0.943** | 0.934 |
| 16 | Pro H image 3/5 (consensus) | 0.700 | [0.653, 0.741] | 0.673 | 0.729 | 0.761 | [0.706, 0.816] | 0.843 | 0.915 |

Image modality clusters here **regardless of model** (Flash or Pro) **or
pipeline stage** (consensus or PV). The ceiling for image-only is ~0.75
F1 at 20m.

**Key observations:**

- **#15 (image baseline + PV) has the highest tile-level MCC of any
  condition** (0.877) and tile sensitivity of 0.943 — it almost never
  misses a tile that contains mounds. But its mound-level localisation
  is imprecise at 20m, pushing it to Tier 5 on F1.
- **Pro image (#16) does not outperform Flash image (#13–14).** The model
  upgrade does not overcome the image modality's fundamental
  localisation limitation.
- MCC for #13 (FH image 7/10) is approximate (~), from the nearest
  evaluated threshold (6-of-10).

---

## Tier 6 — MINIMAL thinking, T=0.7 (F1: 0.640–0.680)

| # | Condition | F1 | 95% CI | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|---|:---:|:---:|:---:|---|:---:|:---:|
| 17 | FM image 8/10 (consensus) | 0.680 | [0.634, 0.723] | 0.640 | 0.726 | ~0.361 | [0.283, 0.433] | 0.860 | 0.477 |
| 18 | FM image 4/5 (consensus) | 0.664 | [0.619, 0.706] | 0.608 | 0.731 | 0.390 | [0.310, 0.469] | 0.843 | 0.531 |
| 19 | FM text T=0.7 29/30 | 0.661 | [0.610, 0.706] | 0.602 | 0.733 | 0.381 | [0.302, 0.460] | 0.817 | 0.554 |
| 20 | FM text T=0.7 5/5 | 0.640 | [0.584, 0.690] | 0.533 | 0.800 | 0.315 | [0.230, 0.395] | 0.860 | 0.426 |

MINIMAL thinking produces high recall (0.73–0.80) but poor precision
(0.53–0.61). **Tile specificity collapses to 0.43–0.55** — the model
hallucinates detections on nearly half of empty tiles. Text and image
modalities are **indistinguishable** here, suggesting that at MINIMAL
thinking the model is not meaningfully processing the prompt modality
distinction.

---

## Tier 7 — Solitary (F1: 0.633)

| # | Condition | F1 | 95% CI | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|---|:---:|:---:|:---:|---|:---:|:---:|
| 21 | FM text T=0.7 10/10 | 0.633 | [0.583, 0.680] | 0.562 | 0.724 | 0.366 | [0.284, 0.444] | 0.834 | 0.516 |

Sits between Tiers 6 and 8 — significantly worse than the N=5 and N=30
variants of the same condition. This is a non-monotonic pool-size
effect at MINIMAL thinking, where N=10 happens to produce worse
consensus than either N=5 or N=30.

---

## Tier 8 — Single-pass and T=1.0 (F1: 0.471–0.552)

| # | Condition | F1 | 95% CI | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|---|:---:|:---:|:---:|---|:---:|:---:|
| 22 | Single-pass T=0 10/10 | 0.552 | [0.491, 0.610] | 0.410 | 0.846 | 0.212 | [0.126, 0.293] | 0.913 | 0.248 |
| 23 | Single-pass T=0 5/5 | 0.544 | [0.481, 0.602] | 0.396 | 0.867 | 0.178 | [0.096, 0.255] | 0.926 | 0.198 |
| 24 | FM text T=1.0 5/5 | 0.471 | [0.395, 0.535] | 0.583 | 0.395 | 0.257 | [0.176, 0.338] | 0.454 | 0.787 |

The single-pass conditions (#22–23) have excellent recall (0.85–0.87)
but ruinous precision (0.40) — they detect almost everything but
generate massive false positive volumes. Tile specificity is ~0.20,
meaning they flag 80% of empty tiles. These represent the **raw proposer
output** before consensus filtering.

T=1.0 (#24) shows the **opposite failure mode**: precision is acceptable
but recall crashes to 0.395. The high temperature causes the model to
miss real mounds rather than hallucinate false ones.

---

## Tier 9 — Worst (F1: 0.462–0.467)

| # | Condition | F1 | 95% CI | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|---|:---:|:---:|:---:|---|:---:|:---:|
| 25 | FM text T=1.0 22/30 | 0.467 | [0.395, 0.532] | 0.499 | 0.439 | 0.208 | [0.122, 0.298] | 0.498 | 0.705 |
| 26 | FM text T=1.0 9/10 | 0.462 | [0.391, 0.526] | 0.545 | 0.400 | 0.212 | [0.122, 0.303] | 0.467 | 0.736 |

T=1.0 was effectively a configuration error (the Gemini API default).
Consensus voting on incoherent high-temperature outputs does not
recover quality — larger pools just confirm the same noise.

---

## Pipeline progression story

Tracing the Flash HIGH text pipeline from raw single-run output to the
best configuration, at 20m:

| Stage | F1 | P | R | What it adds |
|---|:---:|:---:|:---:|---|
| N=1 single run (mean of 30) | 0.387 | 0.249 | 0.869 | Raw detection — high recall, ruinous precision |
| Consensus N=5 (5-of-5) | 0.779 | 0.798 | 0.761 | **+0.392 F1**: precision 0.25→0.80; recall trades down |
| Consensus N=10 (9-of-10) | 0.797 | 0.800 | 0.793 | +0.018: marginal |
| Consensus N=30 (26-of-30) | 0.814 | 0.834 | 0.795 | +0.017: marginal |
| + PV verifier (min, from 16/30) | **0.890** | **0.915** | **0.867** | **+0.076 F1**: precision 0.83→0.92; recall *increases* |

**Total pipeline lift: +0.503 F1** (0.387 → 0.890).

The verifier's recall increase (+0.07) is counterintuitive — adding a
filter should not increase recall. It works because the consensus
threshold (16-of-30) is deliberately set low to maximise proposer
recall, accepting more noise. The verifier then surgically removes
false positives (0.957 tile specificity) while retaining true detections
that a stricter threshold would have excluded. The **large pool + low
threshold + verifier** architecture outperforms **small pool + high
threshold** because it separates the "find everything" and "confirm it's
real" tasks.

---

## Pro pool-size plateau

| Pool | Best threshold | F1 | 95% CI | P | R |
|---|---|:---:|---|:---:|:---:|
| N=5 | 3-of-5 | 0.843 | [0.806, 0.879] | 0.917 | 0.781 |
| N=10 | 6-of-10 | 0.837 | [0.798, 0.874] | 0.921 | 0.767 |

Pro N=10 is marginally **worse** than Pro N=5 (ΔF1 = -0.006, well within
CIs). Adding 5 more Pro runs ($~60) produced no improvement. This
parallels the Flash result (N=5→N=10 was non-significant, ΔF1=+0.018).

The plateau is stronger for Pro than Flash because Pro's per-run quality
is already high — individual runs agree more, so additional runs add
less diversity. For both models, the consensus mechanism saturates at
N=5; further gains require architectural change (the verifier stage).

---

## Hypothesis-driven pairwise comparisons (20m, FDR-corrected)

32 structured comparisons testing specific research questions. 20/26
confirmatory and 3/6 exploratory significant after FDR at q=0.05.

### Architecture matters most

PV adds +0.05 to +0.09 F1 on top of consensus for Flash (p<0.001 for
5/6 comparisons). For Pro, the PV effect is only +0.009 (ns) — Pro's
inherent precision means the verifier has little to filter.

### Thinking level is decisive

HIGH vs MINIMAL: +0.06 to +0.16 F1 (all p<0.001). The effect is larger
for text (+0.14–0.16) than image (+0.06), suggesting HIGH thinking helps
the model process textual legend descriptions more effectively.

### Temperature is the single largest effect

T=0.7 vs T=1.0: **+0.17 to +0.19 F1** (all p<0.001). The largest effect
in the study. T=1.0 was the API default — using it without adjustment
halves detection quality. A cautionary finding for practitioners.

### Text outperforms image

Text vs image at HIGH thinking: +0.05 to +0.09 F1 (significant for 3/4
comparisons). The advantage **vanishes** at MINIMAL thinking, where
neither modality is processed effectively.

### Flash matches Pro with the right pipeline

Pro vs Flash (text consensus): +0.062 (p=0.006). But with PV: -0.015
(ns). Flash + pipeline matches Pro at ~1/10th the cost.

### Pool size plateaus for both models

Flash N=5→N=10: +0.018 (ns). Pro N=5→N=10: -0.006 (ns). Neither model
benefits significantly from doubling the consensus pool beyond N=5.

---

## Summary: what works and what does not

### What works

1. **Multi-stage pipeline architecture** is the dominant factor.
   Consensus + PV together contribute +0.50 F1 over single runs. No
   amount of prompt engineering on a single pass approaches this.
2. **Text-based prompts** outperform image-only by 0.05–0.09 F1 at HIGH
   thinking. The model reads map legends more effectively than it
   interprets raw cartographic symbols.
3. **HIGH thinking** outperforms MINIMAL by 0.06–0.16 F1. The cost is
   ~3× per call, but the pipeline amortises this.
4. **Large proposer pools with low thresholds + verifier** beat small
   pools with high thresholds. The separation of concerns
   (over-generate then verify) outperforms trying to get it right in
   one stage.
5. **Flash + pipeline matches Pro** at ~1/10th the cost.

### What does not work

1. **T=1.0 (API default temperature)** halves detection quality. The
   single most damaging parameter choice.
2. **MINIMAL thinking without pipeline** — tile specificity collapses to
   0.20–0.55. The model hallucinates detections on the majority of
   empty tiles.
3. **Image modality alone** — ceiling of ~0.75 F1 regardless of model or
   pipeline stage.
4. **Prompt engineering within a fixed architecture** — effect sizes
   (0.06–0.17) are dwarfed by architectural effects (+0.50).
5. **Consensus on incoherent outputs** — voting on high-temperature or
   MINIMAL-thinking runs does not recover quality.
6. **Larger consensus pools** — N=10 does not improve over N=5 for
   either Flash or Pro. The consensus mechanism saturates early;
   further gains require the verifier stage.

---

## Statistics

- 26 conditions evaluated at 20m spatial tolerance
- 325 pairwise permutation tests (10,000 iterations, seed 42)
- 265/325 significant after Benjamini-Hochberg FDR correction (q=0.05)
- 9 tiers identified via greedy clique-based clustering
- Bootstrap CIs: 1,000 iterations, seed 42, stratified by map sheet
- Ground truth: 569 hand-placed reference mounds across 4 Soviet
  topographic map sheets
- Evaluation area: 487 tiles (384px, ~5 m/px)
- Pro N=10 evaluation: 5 additional Batch API runs ($~60), consensus
  clustering with DBSCAN (eps=30m), full threshold sweep at 20/30/40/50m
