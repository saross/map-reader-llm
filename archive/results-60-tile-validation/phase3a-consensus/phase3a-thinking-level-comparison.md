# Phase 3a: Thinking Level × Modality Interaction in Consensus Voting

**Author**: Shawn Ross
**Date**: 2026-02-16
**Status**: Draft for paper inclusion
**Phase**: 3a (H3 — Consensus Voting)

---

## 1. Overview

This document presents a comparative analysis of consensus voting performance
across a 2×2 factorial design: input modality (image vs text) crossed with
extended thinking level (MINIMAL vs HIGH). The analysis addresses a finding
that emerged unexpectedly from Phase 3a data collection: the effect of
extended thinking on consensus voting quality is conditional on input
modality, contradicting the simpler narrative that extended thinking
uniformly improves ensemble performance.

The analysis draws on 360 batch runs (90 per condition × 4 conditions),
each comprising 30 independent inference passes at three temperature settings
(T=0.3, T=0.7, T=1.0) across the 60-tile holdout set. All runs used
Gemini 2.0 Flash (gemini-2.0-flash-001) via the Gemini Batch API.

---

## 2. Background and Motivation

### 2.1 Consensus Voting (H3)

The preregistration (Section 3.8) specifies that K=10 independent runs per
condition support consensus voting analysis at pool sizes N=5 and N=10, with
an additional 20 runs at the optimal configuration enabling N=30 threshold
sweeps. Hypothesis H3 predicts that consensus voting will improve F1
compared to single-pass detection.

The consensus voting algorithm operates as follows. For each
(temperature, pool size *N*, vote threshold *x*) combination: (1)
detection GeoDataFrames from *N* runs are converted to GeoJSON features;
(2) within-run deduplication at 20 m tolerance removes overlapping-tile
duplicates; (3) cross-run clustering at 20 m tolerance groups spatially
coincident detections and counts how many runs contribute to each cluster;
(4) clusters receiving fewer than *x* votes are discarded; (5) consensus
centroids are spatially joined to tile boundaries for F1 evaluation. All
confidence intervals use tile-level bootstrap resampling (K=1000 iterations,
seed=42).

### 2.2 Extended Thinking

Gemini 2.0 Flash supports a "thinking" mode in which the model performs
extended internal deliberation before producing its response. The `thinking`
parameter accepts a budget controlling the depth of this deliberation:
MINIMAL (default) uses no extended thinking; higher budgets allocate
progressively more internal reasoning tokens.

A calibration pilot (Observation 71, Phase 2a) evaluated thinking levels
under single-pass conditions (T=0.0, K=1) and found no meaningful
performance difference, leading to the decision to use MINIMAL thinking
throughout the main factorial. This decision was later revisited when
Phase 3a data collection — which included both MINIMAL and HIGH thinking
runs due to an initial configuration error — revealed that thinking level
functions as an experimental factor under consensus voting conditions,
not merely an infrastructure setting.

### 2.3 The Modality Factor

Phase 3a employs two input modalities:

- **Track 1 (Image)**: Each tile is presented as a base64-encoded map
  excerpt alongside textual prompts. The model must visually parse
  cartographic symbols from pixel data.
- **Track 2 (Text)**: Each tile is described using textual coordinate
  specifications derived from the same map data. The model receives
  structured descriptions rather than raw imagery.

Both tracks share the same ground truth (79 mound symbols across 60
holdout tiles) and evaluation methodology. The single-pass baseline
F1 differs between modalities: 0.609 for image, 0.660 for text.

---

## 3. Results

### 3.1 Global Optima

Table 1 presents the best-performing consensus configuration for each of the
four conditions, along with the single-pass baseline and the improvement
(ΔF1) attributable to consensus voting.

**Table 1.** Best consensus voting configuration per condition.

| Condition | Best Config | F1 | 95% CI | P | R | Baseline | ΔF1 |
|:----------|:------------|----:|:------:|----:|----:|--------:|---------:|
| Track 1 Image MINIMAL | T0.7 N=10 x=6 | 0.650 | [0.494, 0.714] | 0.640 | 0.660 | 0.609 | +0.041 |
| Track 1 Image HIGH | T0.3 N=30 x=25 | 0.644 | [0.492, 0.707] | 0.699 | 0.598 | 0.609 | +0.035 |
| Track 2 Text MINIMAL | T1.0 N=30 x=22 | 0.683 | [0.523, 0.757] | 0.657 | 0.711 | 0.660 | +0.023 |
| Track 2 Text HIGH | T0.7 N=30 x=22 | 0.751 | [0.610, 0.795] | 0.772 | 0.732 | 0.660 | +0.091 |

All four conditions confirm H3: consensus voting improves F1 over
single-pass detection. The magnitude of improvement, however, varies
dramatically. Track 2 Text HIGH achieves the largest gain (+9.1 pp),
while Track 2 Text MINIMAL shows the smallest (+2.3 pp). The two image
conditions fall between these extremes with similar, moderate gains
(+3.5 to +4.1 pp).

### 3.2 The Thinking Level × Modality Interaction

The central finding of this analysis is a crossover interaction between
thinking level and input modality. For image-based detection (Track 1),
MINIMAL and HIGH thinking produce virtually identical consensus
performance: F1 = 0.650 vs 0.644, a difference of 0.5 pp that falls well
within bootstrap confidence intervals. For text-based detection (Track 2),
HIGH thinking dramatically outperforms MINIMAL: F1 = 0.751 vs 0.683, a
gap of 6.8 pp.

This interaction is summarised in Table 2.

**Table 2.** Thinking level effect by modality.

| Modality | MINIMAL F1 | HIGH F1 | Δ (HIGH − MINIMAL) | Direction |
|:---------|----------:|---------:|-------------------:|:----------|
| Image | 0.650 | 0.644 | −0.005 | Negligible |
| Text | 0.683 | 0.751 | +0.068 | HIGH advantage |

The confidence intervals for all four conditions overlap substantially
(Table 1), meaning that formal pairwise significance testing would not
reject the null of equal performance at conventional thresholds. This is
expected given the 60-tile evaluation set and between-tile variance in
mound density. A paired permutation test controlling for tile difficulty
would narrow the intervals substantially by eliminating this between-tile
variance; this analysis is planned but not yet conducted.

### 3.3 Per-Temperature Performance

Table 3 reports the optimal consensus configuration at each temperature
for all four conditions. This decomposition reveals how thinking level
and modality interact across the temperature gradient.

**Table 3.** Per-temperature optima.

| Condition | T0.3 | T0.7 | T1.0 |
|:----------|:-----|:-----|:-----|
| Track 1 Image MINIMAL | N=30 x=22, F1=0.619 | N=10 x=6, F1=0.650 | N=30 x=15, F1=0.598 |
| Track 1 Image HIGH | N=30 x=25, F1=0.644 | N=30 x=14, F1=0.638 | N=30 x=12, F1=0.579 |
| Track 2 Text MINIMAL | N=5 x=5, F1=0.676 | N=30 x=28, F1=0.660 | N=30 x=22, F1=0.683 |
| Track 2 Text HIGH | N=30 x=17, F1=0.748 | N=30 x=22, F1=0.751 | N=30 x=21, F1=0.733 |

Two patterns emerge. First, Track 2 Text HIGH achieves F1 > 0.73 at all
three temperatures, a level of consistency unmatched by any other condition.
Second, Track 1 Image MINIMAL is the only condition where the global optimum
occurs at a pool size smaller than N=30 (specifically N=10), suggesting that
image-mode MINIMAL runs produce insufficient detection diversity for
aggressive large-pool consensus filtering.

### 3.4 Detection Cluster Diversity

The mechanism underlying the interaction effect becomes apparent when
examining detection cluster counts. Table 4 reports the number of unique
detection clusters at the most permissive threshold (N=30, x=1) — a proxy
for the total detection diversity available for consensus filtering.

**Table 4.** Detection cluster counts at N=30, x=1 (total detection
diversity).

| Condition | T=0.3 | T=0.7 | T=1.0 |
|:----------|------:|------:|------:|
| Track 1 Image MINIMAL | 329 | 573 | 763 |
| Track 1 Image HIGH | 337 | 586 | 685 |
| Track 2 Text MINIMAL | 247 | 425 | 529 |
| Track 2 Text HIGH | 940 | 1,396 | 2,045 |

For Track 1 (Image), MINIMAL and HIGH produce nearly identical cluster
counts at every temperature: the ratios (HIGH/MINIMAL) are 1.02×, 1.02×,
and 0.90× at T=0.3, T=0.7, and T=1.0 respectively. Extended thinking does
not generate detectably more diverse visual interpretations of map tiles.

For Track 2 (Text), the picture is qualitatively different. HIGH thinking
generates 3.8×, 3.3×, and 3.9× more clusters than MINIMAL at the three
temperatures. This dramatic increase in detection diversity is the
mechanism through which consensus voting achieves its advantage: a larger
and more varied detection pool allows majority-vote filtering to
aggressively remove false positives while retaining spatially consistent
true positives.

### 3.5 Precision-Recall Profiles

The four conditions achieve their optimal F1 scores through different
precision-recall trade-offs (Table 1). Track 1 Image HIGH is the most
precision-oriented (P=0.699, R=0.598), while Track 2 Text HIGH achieves
the strongest balance (P=0.772, R=0.732). Track 2 Text MINIMAL operates
at a lower precision point (P=0.657, R=0.711), trading precision for
recall.

Track 2 Text HIGH's precision-recall profile is noteworthy: it achieves
both the highest precision and the highest recall of any condition. This is
characteristic of a detection pool rich enough that consensus filtering can
simultaneously suppress false positives (driving precision upward) and
retain consistently detected true positives (preserving recall). At
intermediate thresholds (e.g., T0.3 N=30 x=17: P=0.684, R=0.825), the
condition achieves recall exceeding 82% — a level that suggests the
majority of mound symbols are being detected by at least a simple majority
of runs.

---

## 4. Discussion

### 4.1 Confirmation of H3

All four conditions confirm the preregistered prediction that consensus
voting improves F1 relative to single-pass detection. The best consensus
configuration outperforms the corresponding single-pass baseline in every
case, with improvements ranging from +2.3 pp (Track 2 Text MINIMAL) to
+9.1 pp (Track 2 Text HIGH). H3 is therefore supported across both
modalities and both thinking levels.

### 4.2 The Diversity Dividend is Modality-Specific

The most consequential finding is that extended thinking's benefit to
consensus voting is conditional on input modality. For text-based
detection, HIGH thinking generates a substantially more diverse detection
pool — 3–4× more unique clusters — which consensus filtering then
leverages to achieve a 6.8 pp F1 advantage. For image-based detection,
HIGH thinking produces essentially the same detection diversity as MINIMAL,
and consequently the same consensus performance.

This asymmetry has a plausible mechanistic interpretation. When processing
text-based tile descriptions, extended thinking operates on the model's
strongest modality (natural language processing), where additional
deliberation can generate genuinely different interpretative pathways
through the feature space. When processing base64-encoded map images,
extended thinking has less leverage: the visual parsing of cartographic
symbols is likely constrained by early-stage visual feature extraction
rather than by the depth of subsequent reasoning. Extended deliberation on
the same visual features may simply converge on the same detections.

### 4.3 Implications for Calibration Methodology

The original calibration pilot (Observation 71) evaluated thinking levels
under single-pass conditions at T=0.0 — deterministic inference with no
stochastic sampling. Under these conditions, extended thinking indeed shows
no measurable benefit, because there is no diversity to generate and no
consensus mechanism to exploit it. The pilot was structurally incapable of
detecting the effect observed here.

This represents a general methodological lesson: calibration decisions made
under one evaluation protocol (single-pass, deterministic) may not transfer
to a different protocol (multi-pass consensus voting). When the downstream
analytical strategy changes — as it did when this project shifted from
single-pass Protocol A to ensemble consensus Protocol B — prior calibration
decisions warrant re-evaluation.

### 4.4 Temperature, Thinking, and the Diversity Ceiling

Temperature and thinking level are mechanistically independent axes of
stochastic variation: temperature controls token-level sampling randomness,
while thinking level governs the depth of internal deliberation. Both
increase detection diversity, but they may interact differently depending
on which processing stage constrains diversity.

For Track 2 Text, both axes appear additive: HIGH thinking at elevated
temperatures (T=0.7, T=1.0) produces substantially more clusters than
either HIGH thinking at low temperature or MINIMAL thinking at high
temperature. Whether this additivity holds at saturation — whether there
is a diversity ceiling beyond which further stochasticity yields
diminishing returns — remains an open empirical question suitable for a
temperature × thinking factorial experiment.

For Track 1 Image, the diversity ceiling appears to be set by the visual
processing pipeline rather than by either stochasticity axis. Neither
elevated temperature nor extended thinking substantially increases the
diversity of detected features, suggesting that the bottleneck lies in
how the model parses cartographic symbols from pixel data.

### 4.5 Optimal Configuration Strategy

The optimal consensus configurations differ systematically across
conditions:

- **Track 2 Text HIGH** achieves its best performance at large pool sizes
  (N=30) with moderate vote thresholds (x=17 to x=22, i.e., 57–73% of
  runs agreeing). The abundance of detection clusters enables aggressive
  filtering.
- **Track 2 Text MINIMAL** shows a fragmented pattern: the global optimum
  occurs at T=1.0 with a moderate threshold, but the T=0.3 optimum appears
  at the smallest pool size (N=5 x=5). The limited cluster diversity at
  low temperatures cannot sustain large-pool consensus.
- **Track 1 Image MINIMAL** uniquely achieves its best F1 at N=10 rather
  than N=30, the only condition exhibiting this pattern. This is consistent
  with insufficient diversity: with ~300–750 clusters across temperatures,
  the signal-to-noise ratio at N=30 is too low for aggressive filtering to
  outperform gentler thresholds on a smaller pool.
- **Track 1 Image HIGH** favours N=30 with a strict threshold (x=25/30 =
  83% agreement at T=0.3), reflecting a precision-oriented strategy that
  trades recall for low false-positive rates.

### 4.6 Cross-Modality Performance Gap

Across all conditions, text-based detection outperforms image-based
detection. The baselines differ (0.660 vs 0.609), and the gap persists or
widens after consensus voting: the best text condition (F1=0.751) exceeds
the best image condition (F1=0.650) by over 10 pp. This gap likely
reflects the fundamental difficulty of parsing cartographic symbols from
base64-encoded pixel data versus processing structured textual descriptions
— a finding consistent with the broader VLM literature on vision-language
performance disparities in domain-specific tasks.

---

## 5. Limitations

### 5.1 Statistical Power

With 60 holdout tiles containing 79 mound symbols, the evaluation set
provides adequate power for detecting moderate effects (MDE ≈ 0.07–0.09 for
F1; preregistration Section 3.6). The observed interaction effect (+6.8 pp
for text, ~0 pp for image) approaches the lower bound of detectable effect
sizes. Bootstrap confidence intervals are correspondingly wide,
particularly for image-track conditions, and formal pairwise comparisons
may not reach conventional significance thresholds.

A paired permutation test on per-tile F1 differences — which controls
for between-tile variance in mound density and terrain difficulty — would
provide substantially narrower confidence intervals by eliminating the
dominant source of CI width. This analysis is planned.

### 5.2 Single Model

All results pertain to Gemini 2.0 Flash. Whether the modality-specific
diversity dividend generalises to other VLM architectures (Claude, GPT)
remains an open question. Model-specific differences in visual processing
pipelines may produce different thinking-level × modality interactions.

### 5.3 Post-Hoc Discovery

The comparison between MINIMAL and HIGH thinking levels was not
preregistered; it emerged from an accidental configuration that produced
HIGH-thinking runs alongside the planned MINIMAL runs. The finding should
therefore be treated as exploratory and confirmed in future work.
The analysis was, however, conducted using the same preregistered sweep
methodology (same ground truth, same evaluation pipeline, same bootstrap
parameters) applied identically across all four conditions.

---

## 6. Summary of Key Findings

1. **H3 confirmed**: Consensus voting improves F1 over single-pass
   detection across all four conditions of the 2×2 design.

2. **Modality-specific diversity dividend**: Extended thinking (HIGH)
   generates 3–4× more detection clusters for text-only processing but
   produces virtually identical cluster counts for image processing.

3. **Conditional performance advantage**: The diversity dividend translates
   to a +6.8 pp F1 advantage for text-based consensus voting (HIGH vs
   MINIMAL), but no meaningful advantage for image-based consensus voting.

4. **Best overall performance**: Track 2 Text HIGH at T=0.7 N=30 x=22
   achieves F1=0.751 (95% CI [0.610, 0.795]), the highest F1 observed in
   the study, with both the highest precision (0.772) and strong recall
   (0.732).

5. **Visual processing bottleneck**: The lack of a thinking-level effect on
   image-track diversity suggests that detection diversity is constrained by
   visual feature extraction rather than by reasoning depth, implying that
   improvements to image-based performance may require changes to image
   representation or preprocessing rather than inference parameters.

6. **Calibration protocol dependency**: The original pilot's null result for
   thinking level was an artefact of evaluating under deterministic
   single-pass conditions, which are structurally incapable of revealing
   ensemble-mediated effects. This underscores the importance of matching
   calibration protocols to downstream evaluation strategies.

---

## Appendix A: Experimental Parameters

| Parameter | Value |
|:----------|:------|
| Model | Gemini 2.0 Flash (gemini-2.0-flash-001) |
| Temperatures | T=0.3, T=0.7, T=1.0 |
| Runs per temperature | 30 |
| Total runs per condition | 90 |
| Pool sizes evaluated | N=5, N=10, N=30 |
| Pool selection | First-N (preregistration Section 3.8) |
| Spatial matching tolerance | 20 m |
| Within-run deduplication | 20 m |
| Cross-run clustering | 20 m |
| Bootstrap iterations | 1,000 |
| Bootstrap seed | 42 |
| Holdout tiles | 60 (from 4 annotated Soviet map sheets) |
| Ground truth symbols | 79 burial mounds |
| Analysis script | `analyse_consensus_sweep.py` v2.0.0 |

## Appendix B: Full Per-Temperature Optima

**Table B1.** Per-temperature optima with precision-recall decomposition.

| Condition | Temp | N | x | F1 | P | R | n_det | ΔF1 |
|:----------|:-----|--:|--:|----:|----:|----:|------:|--------:|
| Track 1 Image MINIMAL | T0.3 | 30 | 22 | 0.619 | 0.619 | 0.619 | 97 | +0.010 |
| Track 1 Image MINIMAL | T0.7 | 10 | 6 | 0.650 | 0.640 | 0.660 | 100 | +0.041 |
| Track 1 Image MINIMAL | T1.0 | 30 | 15 | 0.598 | 0.598 | 0.598 | 97 | −0.011 |
| Track 1 Image HIGH | T0.3 | 30 | 25 | 0.644 | 0.699 | 0.598 | 83 | +0.035 |
| Track 1 Image HIGH | T0.7 | 30 | 14 | 0.638 | 0.600 | 0.680 | 110 | +0.029 |
| Track 1 Image HIGH | T1.0 | 30 | 12 | 0.579 | 0.530 | 0.639 | 117 | −0.030 |
| Track 2 Text MINIMAL | T0.3 | 5 | 5 | 0.676 | 0.628 | 0.732 | 113 | +0.016 |
| Track 2 Text MINIMAL | T0.7 | 30 | 28 | 0.660 | 0.693 | 0.629 | 88 | −0.001 |
| Track 2 Text MINIMAL | T1.0 | 30 | 22 | 0.683 | 0.657 | 0.711 | 105 | +0.023 |
| Track 2 Text HIGH | T0.3 | 30 | 17 | 0.748 | 0.684 | 0.825 | 117 | +0.088 |
| Track 2 Text HIGH | T0.7 | 30 | 22 | 0.751 | 0.772 | 0.732 | 92 | +0.091 |
| Track 2 Text HIGH | T1.0 | 30 | 21 | 0.733 | 0.795 | 0.680 | 83 | +0.073 |
