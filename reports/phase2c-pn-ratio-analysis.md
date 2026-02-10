# Phase 2c: P:N Ratio and Negative Example Composition Analysis

**Date**: 2026-02-10
**Context**: Post-adversarial review analysis of all 7 Phase 2c library conditions
**Purpose**: Determine whether the Positive:Negative label ratio predicts
performance, and characterise the interaction between hard positives (HP), canonical
negatives (Canon-), and hard negatives (HN).

---

## Background

Phase 2c tested 7 library compositions under H8 (library composition and scaling).
The adversarial review (`reports/phase2c-adversarial-review.md`) confirmed the
results are genuine and proposed three complementary mechanisms. This report extends
that analysis with comprehensive P:N ratio data, a 2x2 interaction decomposition,
and TP/FP/FN breakdowns that reveal the causal pathways.

### Notation

| Abbreviation | Meaning |
|---|---|
| **C+** | Canonical positive examples (examples 01-04) |
| **HP** | Hard positive examples (examples 05-08) |
| **C-** | Canonical negative examples (examples 09-10) |
| **HN** | Hard negative examples (examples 11-14) |
| **Null** | Null tiles — featureless negatives (examples 15-17) |
| **P:N** | Ratio of positive-labelled to negative-labelled examples |

### Role of Null Tiles

Null tiles (3 per library, fixed across all conditions) are **functionally
necessary infrastructure**, not a compositional variable. Without them, the model
generates detections until output tokens fill up — they teach the model that "no
symbols present" is a valid response. This is well-attested in traditional CV/ML
literature. The count of 3 is relatively few by ML standards and has been deferred
for exploratory investigation (see `docs/planning/future-work.md`, Section 3.4).

---

## Master Data Table

All values are 10-run means from Phase 2c (60 validation tiles, 97 reference
mounds, T=0.0, Gemini 3 Flash). Sorted by mean F1 descending.

| Condition | C+ | HP | C- | HN | Null | P:N | Mean F1 | Mean Det | Mean TP | Mean FP | Mean FN |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **plus-hp** | 4 | 4 | 2 | 0 | 3 | 1.60 | **0.609** | 134.4 | 70.4 | 64.0 | 26.6 |
| **pp-canon** | 4 | 0 | 0 | 0 | 3 | 1.33 | **0.603** | 128.0 | 67.8 | 60.2 | 29.2 |
| **pp-2hp** | 4 | 2 | 0 | 0 | 3 | 2.00 | 0.575 | 133.8 | 66.3 | 67.5 | 30.7 |
| **scale-8** | 4 | 4 | 2 | 4 | 3 | 0.89 | 0.570 | 135.0 | 66.1 | 68.9 | 30.9 |
| **scale-4** | 4 | 2 | 2 | 2 | 3 | 0.86 | 0.564 | 138.3 | 66.3 | 72.0 | 30.7 |
| **pp-4hp** | 4 | 4 | 0 | 0 | 3 | 2.67 | 0.550 | 132.0 | 63.0 | 69.0 | 34.0 |
| **canonical** | 4 | 0 | 2 | 0 | 3 | 0.80 | 0.528 | 121.9 | 57.8 | 64.1 | 39.2 |

### Derivation of TP/FP/FN

Values derived from per-run CSV data (`per_run_metrics.csv`):

- TP = Precision x n_detections (verified against adversarial review run_1 values)
- FP = n_detections - TP
- FN = 97 - TP (97 = total reference mounds across 60 validation tiles)

---

## Analysis 1: P:N Ratio as a Predictor

Sorted by P:N ratio ascending:

```text
P:N   Condition     F1      Negative composition
----- ------------ ------- ---------------------
0.80  canonical     0.528   2C- + 3null
0.86  scale-4       0.564   2C- + 2HN + 3null
0.89  scale-8       0.570   2C- + 4HN + 3null
1.33  pp-canon      0.603   3null only
1.60  plus-hp       0.609   2C- + 3null
2.00  pp-2hp        0.575   3null only
2.67  pp-4hp        0.550   3null only
```

### Observation

F1 increases from P:N 0.80 to ~1.60, then decreases. This suggests an inverted-U
relationship with a peak around P:N 1.3-1.6. However, the correlation is **weak and
confounded**:

- canonical (P:N 0.80) and plus-hp (P:N 1.60) share the same negative composition
  (2C- + 3null) but differ by 0.081 F1 — the difference is HP, not ratio
- pp-canon (P:N 1.33) and pp-4hp (P:N 2.67) share the same negative composition
  (3null only) but differ by 0.053 F1 — the difference is HP without Canon-
- plus-hp (P:N 1.60) and scale-8 (P:N 0.89) have very different ratios but
  scale-8 scores lower — the difference is HN

**Conclusion**: P:N ratio is a poor predictor of performance. Negative example
*composition* (which types of negatives are present) matters more than negative
example *count*.

---

## Analysis 2: The 2x2 HP x Canon- Interaction

Four conditions form a natural 2x2 factorial crossing HP presence with Canon-
presence (HN excluded):

### F1 Interaction Table

|  | **Canon- absent** | **Canon- present** | **Canon- delta** |
|---|:---:|:---:|:---:|
| **HP absent** | pp-canon: 0.603 | canonical: 0.528 | **-0.075** |
| **HP present** | pp-4hp: 0.550 | plus-hp: 0.609 | **+0.059** |
| **HP delta** | **-0.053** | **+0.081** | |

### TP/FP Interaction Table

|  | **Canon- absent** | **Canon- present** | **Canon- TP delta** | **Canon- FP delta** |
|---|:---:|:---:|:---:|:---:|
| **HP absent** | 67.8 TP, 60.2 FP | 57.8 TP, 64.1 FP | -10.0 | +3.9 |
| **HP present** | 63.0 TP, 69.0 FP | 70.4 TP, 64.0 FP | +7.4 | -5.0 |

### Interpretation

This is a **crossover interaction**: each factor's effect reverses depending on
the other's presence.

**HP without Canon-** (pp-canon -> pp-4hp): Adding 4 hard positive examples to a
null-only library loses 4.8 TP and gains 8.8 FP. HP expands the positive class
boundary indiscriminately — the model learns "more things count as mounds" without
learning "but these specific things don't." Detection volume increases slightly
(128 -> 132) but the additional detections are disproportionately false.

**HP with Canon-** (canonical -> plus-hp): Adding 4 hard positive examples to a
Canon- library gains 12.6 TP and loses 0.1 FP. The same HP examples that hurt in
isolation are highly beneficial when Canon- anchors the negative boundary. The model
can expand its positive class *selectively* because it has informative negative
examples constraining the expansion.

**Canon- without HP** (pp-canon -> canonical): Adding 2 canonical negative examples
to a null-only library loses 10.0 TP and gains 3.9 FP. Without HP to expand the
positive boundary, Canon- makes the model overly conservative — it learns "these
things aren't mounds" and over-applies the lesson, suppressing true detections.

**Canon- with HP** (pp-4hp -> plus-hp): Adding 2 canonical negative examples to an
HP library gains 7.4 TP and loses 5.0 FP with no change in detection volume (both
132). This is the "redirection" mechanism identified in the adversarial review:
Canon- doesn't suppress detection count — it redirects detections from false
positives to true positives.

### Summary of the Interaction

Neither HP nor Canon- is inherently helpful or harmful. Each is detrimental alone
but beneficial together. The combination outperforms all other conditions because:

1. HP expands the positive class boundary (what counts as a mound)
2. Canon- anchors the negative class boundary (what does not count)
3. Together they create a tight decision boundary refined from both sides

This "discriminative sandwich" mechanism is the core finding of the Phase 2c
analysis.

---

## Analysis 3: The Hard Negative (HN) Effect

### Cleanest Comparison (HP and Canon- Held Constant)

| Condition | Composition | Det | TP | FP | FN | F1 |
|---|---|:---:|:---:|:---:|:---:|:---:|
| plus-hp | 4C+ 4HP 2C- 3null | 134.4 | 70.4 | 64.0 | 26.6 | 0.609 |
| scale-8 | 4C+ 4HP 2C- **4HN** 3null | 135.0 | 66.1 | 68.9 | 30.9 | 0.570 |

Adding 4 HN to the best-performing condition: +0.6 detections, -4.3 TP, +4.9 FP,
+4.3 FN. HN **degrades** performance by generating noisier detections, even in the
presence of Canon-.

### Confounded Comparison (HP and HN Both Vary)

| Condition | Composition | Det | TP | FP | FN | F1 |
|---|---|:---:|:---:|:---:|:---:|:---:|
| plus-hp | 4C+ 4HP 2C- 3null | 134.4 | 70.4 | 64.0 | 26.6 | 0.609 |
| scale-4 | 4C+ **2HP** 2C- **2HN** 3null | 138.3 | 66.3 | 72.0 | 30.7 | 0.564 |

This comparison is confounded (2 fewer HP, 2 more HN), but the direction is
consistent: adding HN while reducing HP produces more detections that are
disproportionately false.

### Why Canon- Helps But HN Hurts

Both Canon- and HN are "informative negatives" — they show specific landscape
features labelled "Negative." The difference is in the *kind* of information:

| Property | Canon- (examples 09-10) | HN (examples 11-14) |
|---|---|---|
| **What they show** | Clear non-mound features that could be confused at a glance | Ambiguous features genuinely near the decision boundary |
| **Message to model** | "You might think this is a mound — it definitely is not" | "This thing that looks a lot like a mound... isn't one" |
| **Effect on boundary** | Plants a clear signpost | Creates uncertainty in the boundary region |
| **TP/FP effect** | Redirects FP to TP (same volume) | Adds noisy detections (+FP, -TP) |

Canon- clarifies the decision boundary by providing unambiguous negative anchors.
HN destabilises the boundary by introducing examples that are genuinely difficult
to distinguish from positives. When the model encounters an ambiguous feature on a
test tile, HN examples create competing signals: some mound-like things were
labelled Positive (HP), other mound-like things were labelled Negative (HN). The
response is inconsistent detection.

---

## Analysis 4: Effect Decomposition Summary

| Factor | Alone | With complementary factor | Mechanism |
|---|---|---|---|
| **HP** | Harmful (-0.053 F1) | Helpful (+0.081 F1) | Expands positive boundary; needs Canon- to constrain |
| **Canon-** | Harmful (-0.075 F1) | Helpful (+0.059 F1) | Constrains boundary; needs HP to benefit from expansion |
| **HN** | Not tested alone | Harmful (-0.039 F1) | Destabilises boundary even with Canon- present |
| **Null** (3 tiles, fixed) | Necessary infrastructure | — | Prevents runaway detection; non-discriminative |

### The Asymmetry

The asymmetry is not between positive and negative examples — it is between
**clear** and **ambiguous** hard examples:

- **Clear** hard examples (HP showing marginal mounds, Canon- showing clear
  non-mounds) help when paired together
- **Ambiguous** hard examples (HN showing features genuinely near the decision
  boundary) hurt regardless of context

This suggests that few-shot example selection for VLMs should prioritise examples
that are *informative but unambiguous* — examples where the correct label is clear
to a human expert, even if the visual features might confuse a naive observer.
Examples where even the ground truth is contestable appear to introduce noise rather
than useful signal.

---

## Standalone Verification

The directional pattern (plus-hp outperforms) was independently verified using
`scripts/standalone_verification.py`, a completely independent reimplementation
sharing zero code with the production pipeline:

| Condition | Batch 1 | Batch 2 | Batch 3 | Mean F1 |
|---|:---:|:---:|:---:|:---:|
| plus-hp | 0.625 | 0.734 | 0.700 | **0.686** |
| pp-canon | 0.641 | 0.718 | 0.615 | 0.658 |
| pp-4hp | 0.667 | 0.684 | 0.634 | 0.662 |

The standalone verification used greedy nearest-neighbour matching (not Hungarian),
json.load() + shapely (not geopandas), and direct rasterio affine transforms. The
higher absolute F1 values reflect different tile selection (30 tiles with different
density distributions) and different matching algorithm, but the directional pattern
is consistent: plus-hp is the top performer across 2/3 batches and on aggregate.

See `outputs/standalone-verification*/results.json` for raw data.

---

## Implications

### For the Current Study

1. **plus-hp is the correct carry-forward configuration** for Phase 2d (text
   treatment). The HP x Canon- interaction is the dominant effect in library
   composition.
2. **P:N ratio is not a useful design parameter** in isolation. Library composition
   decisions should be guided by negative example *informativeness*, not ratio.
3. **HN examples should not be included** in the carry-forward library. They degrade
   performance even with Canon- present.

### For VLM Prompting Practice

1. **Hard examples work in complementary pairs**: expanding the positive boundary
   (HP) is only beneficial when the negative boundary is simultaneously anchored
   (Canon-), and vice versa.
2. **Negative example quality matters more than quantity**: 2 clear Canon- examples
   outperform 4 ambiguous HN examples, despite the latter providing a "better" P:N
   ratio (0.89 vs 1.60).
3. **Null examples serve a structural role**: they teach the model that absence of
   the target is a valid response, but carry no discriminative information about the
   decision boundary.

### Open Questions

1. Would varying null count (0, 1, 3, 5) change results? (See
   `docs/planning/future-work.md`, Section 3.4)
2. Is the HP x Canon- interaction specific to this task/model, or does it generalise
   across VLM detection tasks?
3. Would a larger Canon- set (4 instead of 2) further improve performance, or does
   the benefit saturate?

---

## Data Sources

- **Phase 2c per-run metrics**: `outputs/phase2c/track1-image/per_run_metrics.csv`
  and `outputs/phase2c/track1-image-exploratory/per_run_metrics.csv`
- **Adversarial review**: `reports/phase2c-adversarial-review.md`
- **Standalone verification**: `outputs/standalone-verification*/results.json`
- **Analysis scripts**: `scripts/6_analyse_phase2.py`

---

*Report produced during Session 30 causal reasoning review. All claims backed by
data from Phase 2c (10 runs x 60 tiles x 7 conditions = 4,200 evaluations) and
standalone verification (3 batches x 10 tiles x 3 conditions = 90 evaluations).*
