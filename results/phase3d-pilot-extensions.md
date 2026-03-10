# Phase 3d Pilot — Extended Analyses

## Metadata

- **Generated**: 2026-03-10
- **Script**: `scripts/analyse_h2_pilot_extensions.py`
- **Matching method**: Greedy nearest-neighbour, 20.0 m buffer (consistent
  with Phase 3d pilot evaluation)
- **Data source**: Phase 3d pilot (K=1, T=0.0, 3 verifier strategies)
- **Outputs**: `results/phase3d-pr-curves.csv`,
  `results/phase3d-pilot-extensions.json`,
  `results/figures/phase3d-pr-curves.png`,
  `results/figures/phase3d-cross-modal-venn.png`

## Summary

Three analyses were run on existing Phase 3d pilot data with zero
additional API calls. The most consequential finding is from Analysis 2:
the image and text-only proposer tracks are **complementary**, not
redundant. Their union discovers 84 of 97 ground-truth mounds
(recall = 0.866), compared to 78 for text alone (0.804) or 71 for image
alone (0.732). This strongly supports pursuing a cross-modal union
proposer.

Analysis 1 confirms the pilot's optimal operating points at finer
threshold resolution and reveals that the adversarial verifier is the
only strategy with a genuinely informative precision-recall trade-off.
Analysis 3 shows that ensembling the three verifier strategies adds
negligible value (+0.007 F1 at best) because the standard and checklist
verifiers are functionally redundant.

---

## Analysis 1: Precision-Recall Curves

### Purpose

The Phase 3d pilot swept verifier probability thresholds in 0.1 steps.
This analysis uses 0.01 steps (101 points) to find the precise optimal
operating point for each verifier strategy and to characterise the
precision-recall trade-off space.

### Results

#### AUC-PR and optimal operating points

| Track | Verifier | AUC-PR | Optimal F1 | Threshold | Precision | Recall | N kept |
|-------|----------|-------:|----------:|----------:|----------:|-------:|-------:|
| Image | Standard | 0.147 | 0.706 | 0.11 | 0.683 | 0.732 | 104 |
| Image | Adversarial | 0.191 | 0.711 | 0.21 | 0.711 | 0.711 | 97 |
| Image | Checklist | 0.029 | 0.706 | 0.11 | 0.683 | 0.732 | 104 |
| Text-only | Standard | 0.398 | 0.768 | 0.11 | 0.785 | 0.753 | 93 |
| Text-only | Adversarial | 0.181 | 0.796 | 0.16 | 0.809 | 0.784 | 94 |
| Text-only | Checklist | 0.089 | 0.786 | 0.91 | 0.778 | 0.794 | 99 |

#### Baselines (unfiltered proposer, no verification)

| Track | Precision | Recall | F1 | N candidates |
|-------|----------:|-------:|---:|------------:|
| Image | 0.538 | 0.732 | 0.620 | 132 |
| Text-only | 0.557 | 0.804 | 0.658 | 140 |

**Figure**: `results/figures/phase3d-pr-curves.png`

### Interpretation

**Optimal thresholds are low.** The best thresholds are 0.11–0.21 for
most verifier-track combinations, not the 0.5 midpoint one might
expect. This is a direct consequence of the bimodal probability
distributions: the verifier assigns near-zero or near-one probabilities
to the vast majority of candidates, with very few in between. Any
threshold between ~0.1 and ~0.85 yields effectively the same partition.
The optimal threshold sits just above the "reject" cluster, capturing
every candidate the verifier is even slightly uncertain about.

**Standard and checklist verifiers produce step-function curves.** Their
probability distributions are almost perfectly binary (image track:
28 candidates at 0.0–0.1, 104 at 0.9–1.0, zero between for both
standard and checklist). The curves have only two distinct operating
points. In contrast, the adversarial verifier places 4–14 candidates
in intermediate ranges (0.1–0.9), producing a smoother curve with
genuinely different operating points.

**The adversarial verifier dominates.** On both tracks, the adversarial
verifier achieves the highest optimal F1 (0.711 image, 0.796 text).
Its advantage is clearest on the text track, where it outperforms
standard by +0.028 F1 and checklist by +0.010 F1. The adversarial
framing ("argue this is NOT a mound") appears to produce more
calibrated probability estimates than diagnostic or checklist
approaches.

**AUC-PR values are low due to curve compression.** The AUC-PR figures
(0.029–0.398) reflect the narrow recall range over which the curves
operate, not poor classification quality. Because the proposer already
achieves recall of 0.73–0.80 before verification, the P-R curve starts
at high recall and traverses only a small portion of the recall axis.
The relative AUC-PR values are meaningful for comparison between
verifiers; absolute values should not be compared to full-range
classifiers.

---

## Analysis 2: Cross-Modal Overlap

### Purpose

The image and text-only proposer tracks were designed as parallel
conditions for the modality factor (H1). This analysis repurposes them
as candidate components of a cross-modal union proposer: if the two
tracks discover substantially different mounds, their union could
achieve higher recall than either track alone, providing more candidates
for the verifier to filter.

### Results

#### Pre-verification overlap (proposer candidates only)

| Metric | Value |
|--------|------:|
| Total ground-truth mounds | 97 |
| Image track true positives (TPs) | 71 |
| Text track TPs | 78 |
| Found by both tracks | 65 |
| Image-only discoveries | 6 |
| Text-only discoveries | 13 |
| Found by neither track | 13 |
| **Union recall** | **0.866 (84/97)** |
| Jaccard index | 0.774 |

#### False positive overlap

| Metric | Value |
|--------|------:|
| Image false positives (FPs) | 61 |
| Text FPs | 62 |
| Co-occurring FPs (within 20 m) | 20 |
| Image-unique FPs | 41 |
| Text-unique FPs | 42 |

#### Post-verification overlap (adversarial verifier, threshold ≥ 0.5)

| Metric | Pre-verification | Post-verification | Change |
|--------|:----------------:|:-----------------:|:------:|
| Image TPs | 71 | 67 | −4 |
| Text TPs | 78 | 72 | −6 |
| Found by both | 65 | 55 | −10 |
| Image-only | 6 | 12 | +6 |
| Text-only | 13 | 17 | +4 |
| Found by neither | 13 | 13 | 0 |
| Union recall | 0.866 | 0.866 | 0 |
| Jaccard index | 0.774 | 0.655 | −0.119 |

**Figure**: `results/figures/phase3d-cross-modal-venn.png`

### Interpretation

**Cross-modal union is strongly supported.** The union of both proposer
tracks finds 84 of 97 ground-truth mounds (recall = 0.866), a
substantial improvement over either track alone (image: 0.732, text:
0.804). The 19 unique discoveries (6 image-only + 13 text-only) come
from mounds that one modality's cognitive process detects but the
other's does not.

**Text-only makes more unique discoveries.** Text finds 13 mounds that
image misses, while image finds only 6 that text misses. This is
consistent with Phase 2a's finding that images *constrain* detection by
anchoring the model to specific visual patterns: text's interpretive
latitude allows it to flag symbols that don't match the visual prototype
closely enough for the image track's more conservative detection.

**False positives are largely independent.** Only 20 of the ~61–62 FPs
per track co-occur at the same location. This means a cross-modal union
proposer would produce roughly 103 unique FPs (41 + 42 + 20), not 123
(61 + 62). More importantly, the two tracks hallucinate in mostly
different places — they are not redundantly fooled by the same
confusable symbols. This independence is exactly the structural property
that Phase 3c (H9) found lacking within same-task diversity: different
modalities produce genuinely different error profiles in a way that
prompt reformulation, temperature variation, and image rotation did not.

**Verification preserves union recall.** After adversarial filtering,
the union still finds 84/97 mounds — verification does not
preferentially eliminate the unique discoveries. However, verification
does shift *which* mounds are found uniquely: the Jaccard index drops
from 0.774 to 0.655, meaning each track loses some of its shared
detections while retaining its unique ones. This increased
complementarity post-verification suggests the verifier is dropping
borderline candidates that happen to differ between tracks, not
systematically eliminating one track's contributions.

**13 mounds are a hard ceiling for the current proposer.** Neither
track finds these 13 mounds at T=0.0 with the current prompt. They
represent the target for a high-recall proposer experiment: higher
temperature, HIGH thinking, recall-biased prompting, and 1-of-N union
across passes could plausibly recover some of these. If even
5 of the 13 are recoverable, combined with cross-modal union, overall
recall could exceed 0.90.

---

## Analysis 3: Multi-Verifier Ensemble

### Purpose

The Phase 3d pilot tested three verifier strategies: standard
diagnostic criteria, adversarial rejection, and feature checklist.
Phase 3c showed that diversity within identical tasks fails to improve
consensus. This analysis tests whether diversity *across different
cognitive tasks* (the three verifier strategies) improves on the best
single verifier — a qualitatively different form of ensemble.

### Note on experimental design

The original to-do item proposed "reconstructing consensus from K=10
verifier passes." This was incorrect: the pilot ran K=1 verifier passes
at T=0.0 (deterministic), not K=10. There is only one probability
estimate per (candidate, strategy) pair. This analysis was revised to
treat the three verifier strategies as ensemble members rather than
attempting to build consensus from repeated passes that do not exist.

### Results

#### Agreement statistics (decision threshold = 0.5)

| Track | Pair | Agreement |
|-------|------|----------:|
| Image | standard vs adversarial | 0.924 (122/132) |
| Image | standard vs checklist | **1.000** (132/132) |
| Image | adversarial vs checklist | 0.924 (122/132) |
| Image | 3-way | 0.924 (122/132) |
| Text-only | standard vs adversarial | 0.879 (123/140) |
| Text-only | standard vs checklist | 0.936 (131/140) |
| Text-only | adversarial vs checklist | 0.900 (126/140) |
| Text-only | 3-way | 0.857 (120/140) |

#### Ensemble vs best single verifier

| Track | Strategy | F1 | Threshold | Precision | Recall | N kept |
|-------|----------|----|----------:|----------:|-------:|-------:|
| Image | Best single (adversarial) | 0.711 | 0.21 | 0.711 | 0.711 | 97 |
| Image | Ensemble (average) | 0.717 | 0.71 | 0.703 | 0.732 | 101 |
| Image | Ensemble (majority) | 0.706 | 0.11 | 0.683 | 0.732 | 104 |
| Image | Ensemble (union) | 0.718 | 0.96 | 0.714 | 0.722 | 98 |
| Text-only | Best single (adversarial) | **0.796** | 0.16 | 0.809 | 0.784 | 94 |
| Text-only | Ensemble (average) | 0.794 | 0.67 | 0.815 | 0.773 | 92 |
| Text-only | Ensemble (majority) | 0.790 | 0.16 | 0.786 | 0.794 | 98 |
| Text-only | Ensemble (union) | 0.784 | 0.11 | 0.765 | 0.804 | 102 |

### Interpretation

**Standard and checklist are functionally identical.** On the image
track, standard and checklist agree on 100% of candidates (132/132).
On the text track, agreement is 93.6%. Despite different prompt
framings (diagnostic criteria vs structured feature checklist), the
two strategies converge on the same binary decisions for nearly every
candidate. The structured decomposition in the checklist prompt does
not produce meaningfully different judgements from the holistic
diagnostic approach.

**The adversarial verifier is the sole source of diversity.** All
disagreement in the 3-way ensemble comes from the adversarial verifier.
On the image track, 10 candidates (7.6%) receive different decisions
from the adversarial verifier than from standard/checklist. On the text
track, 17 candidates (12.1%) differ. This is insufficient diversity to
produce a meaningful ensemble benefit.

**Ensembling adds negligible value.** The best ensemble strategy
(image: union at F1=0.718; text: average at F1=0.794) improves over the
best single verifier by +0.007 F1 on image and −0.002 F1 on text.
These differences are well within noise for a pilot with no bootstrap
confidence intervals. On the text track, the adversarial verifier alone
remains the best option.

**This confirms a pattern from Phase 3c.** Diversity through surface
variation (rephrasing, reordering, temperature) fails because VLM
outputs are highly stable. The three verifier strategies represent a
stronger form of diversity (different cognitive tasks: diagnose, argue
against, decompose into features), yet even this is insufficient when
two of the three strategies converge. True performance gains in this
pipeline come from structural changes — different *stages* (proposer vs
verifier) or different *modalities* (image vs text) — not from
recombining variants of the same stage.

---

## Implications for Next Experiments

### Strong support: cross-modal union proposer

Analysis 2 provides the clearest actionable finding: combining image
and text proposer outputs produces a recall of 0.866 at the proposer
stage, before any verification. An adversarial verifier applied to the
union candidate pool should achieve precision comparable to single-track
verification (0.71–0.81) while preserving the higher recall.

The false positive analysis shows the union would contribute ~103
unique FPs — roughly 1.7× the single-track count. Given that the
adversarial verifier already handles 60+ FPs effectively (reducing them
by ~40–50%), the larger pool should not overwhelm it. The key question
is whether verification performance degrades with more candidates, which
can be tested cheaply by running the existing verifier on the union
candidate set.

### Moderate support: high-recall proposer for the 13-mound ceiling

The 13 mounds found by neither track at T=0.0 are the hard limit of
the current proposer configuration. These are likely degraded symbols,
unusual subtypes, or symbols in cluttered regions that the model fails
to flag under conservative (T=0.0) proposer settings. A high-recall
proposer experiment (higher temperature, HIGH thinking, recall-biased
prompt, 1-of-N union across passes) targets this ceiling specifically.

### Not supported: verifier ensembling

Analysis 3 shows that combining the three verifier strategies adds no
meaningful value. Future verifier experiments should focus on
alternative approaches (HIGH thinking, different prompts, multi-pass
with escalation) rather than ensembling existing strategies.

### Recommended experiment prioritisation

1. **Cross-modal union proposer + adversarial verifier** (free to
   construct from existing candidates; verifier cost ~$7). Directly
   tests whether Analysis 2's union recall of 0.866 translates to
   improved F1 after verification.
2. **High-recall text proposer pilot** (~$7). Explores the 13-mound
   ceiling with recall-optimised configuration.
3. **HIGH-thinking adversarial verifier** (~$7). Tests whether extended
   reasoning improves verification, particularly on the borderline
   candidates (probability 0.1–0.7) that the adversarial verifier
   currently handles.
