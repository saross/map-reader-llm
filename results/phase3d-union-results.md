# Phase 3d — Cross-Modal Union Experiment Results

## Metadata

- **Generated**: 2026-03-10
- **Script**: `scripts/run_union_experiment.py`
- **Matching method**: Greedy nearest-neighbour, 20.0 m buffer
- **Evaluation**: Cluster-level with member-level matching (see
  Methodological Note below)
- **Verifier**: Adversarial (text-only mode, `include_examples=False`)
- **Verifier config**: T=0.0, thinking=minimal, model=gemini-3-flash
- **Candidates**: 184 unique clusters (from 272 raw detections across
  image + text proposers)
- **Ground truth**: 97 mounds (validation tile set)
- **Cost**: ~$2 (184 API calls, 0 failures)
- **Outputs**: `outputs/phase3d-union/union_results.json`,
  `outputs/phase3d-union/verifier_adversarial_probabilities.json`

## Summary

The cross-modal union proposer + adversarial verifier achieves
**F1=0.768** — the highest verified recall (0.835) of any configuration
tested, but 0.028 F1 below the text-only single-track pipeline (0.796).
The recall gain from cross-modal fusion (+0.051 over text-only verified)
partially survives verification, but the larger, more diverse false
positive pool reduces precision enough to offset the recall benefit.

The provenance breakdown reveals a clear quality gradient: candidates
found by both tracks are excellent (P=0.867), text-only discoveries
are good (P=0.706), and image-only discoveries are mostly false
positives (P=0.318). This suggests the image track's unique
contributions are lower quality than the text track's — consistent
with the visual anchoring effect documented in Phase 2c.

---

## Comparison Table

| Pipeline | F1 | Precision | Recall | N | Threshold |
|----------|---:|----------:|-------:|--:|----------:|
| Image single-track (adversarial) | 0.711 | 0.711 | 0.711 | 97 | 0.21 |
| Text single-track (adversarial) | 0.796 | 0.809 | 0.784 | 94 | 0.16 |
| Union unfiltered | 0.598 | 0.457 | 0.866 | 184 | — |
| **Union + adversarial** | **0.768** | 0.711 | 0.835 | 114 | 0.11 |

### Interpretation

**Recall is the best of any verified configuration.** The union's 0.835
recall (81/97 mounds) exceeds text-only verified (0.784, 76/97) by
+0.051. Cross-modal complementarity partially survives verification:
the pre-verification union recall of 0.866 (84/97) drops by only 3
mounds after filtering, confirming the Session 44 prediction that
verification would not preferentially eliminate unique cross-modal
discoveries.

**Precision is the limiting factor.** At 0.711, precision is 0.098 below
text-only verified (0.809). The union introduces 44 image-only and 52
text-only candidates on top of the 88 shared candidates. These
track-specific candidates include more false positives than the shared
pool, and the verifier — which sees each candidate in isolation without
provenance information — cannot fully compensate.

**F1 does not beat text-only.** The −0.028 F1 gap means the recall gain
(+0.051) is insufficient to overcome the precision loss (−0.098) in the
harmonic mean. This is a genuine finding: cross-modal fusion helps
recall but the verifier's precision on the expanded pool is lower than
on the more curated single-track pool.

---

## Provenance Breakdown (at Optimal Threshold)

| Source | N | TP | FP | Precision | Recall |
|--------|--:|---:|---:|----------:|-------:|
| image-only | 22 | 7 | 15 | 0.318 | 0.072 |
| text-only | 17 | 12 | 5 | 0.706 | 0.124 |
| both | 75 | 65 | 10 | 0.867 | 0.670 |

### Interpretation

**Both-track candidates are the strongest.** The 75 candidates found by
both modalities achieve P=0.867, far exceeding either track-specific
category. Cross-modal agreement is a strong signal of true positives —
if both the visual pattern matcher and the textual feature reasoner
independently flag the same location, it is very likely a genuine mound.

**Text-only discoveries are valuable.** The 17 text-only candidates
include 12 TPs (P=0.706). These are mounds that the text-based
proposer's interpretive latitude detects but the image track's visual
prototype misses. At 12 unique TPs, they contribute substantially to
the recall advantage.

**Image-only discoveries are mostly noise.** Only 7 of 22 image-only
candidates are TPs (P=0.318). The image track's unique discoveries
are lower quality — symbols that visually resemble the reference
prototype but lack the features that text-based reasoning would flag.
The verifier (which uses text-only mode) is less effective at filtering
these because they are visually convincing even in isolation.

**The precision asymmetry explains the F1 gap.** If image-only
candidates were removed entirely, the remaining 92 candidates (75 both,
17 text-only) would have 77 TPs and 15 FPs (P=0.837), closer to the
text-only single-track precision. The 7 additional TPs from image-only
come at the cost of 15 FPs — a 1:2.1 TP:FP ratio that drags down
overall precision. A provenance-aware verifier threshold (higher for
image-only candidates) could potentially recover this precision without
sacrificing the 7 TPs.

---

## Threshold Sweep

| Threshold | F1 | Precision | Recall | N kept |
|----------:|---:|----------:|-------:|-------:|
| 0.00 | 0.598 | 0.457 | 0.866 | 184 |
| 0.05 | 0.672 | 0.549 | 0.866 | 153 |
| 0.10 | 0.728 | 0.634 | 0.856 | 131 |
| 0.11 * | 0.768 | 0.711 | 0.835 | 114 |
| 0.15 | 0.768 | 0.711 | 0.835 | 114 |
| 0.20 | 0.768 | 0.711 | 0.835 | 114 |
| 0.25 | 0.749 | 0.717 | 0.784 | 106 |
| 0.50 | 0.744 | 0.725 | 0.763 | 102 |
| 0.90 | 0.729 | 0.737 | 0.722 | 95 |
| 1.00 | 0.703 | 0.753 | 0.660 | 85 |

### Interpretation

**The same bimodal threshold pattern.** As with the single-track pilot,
the optimal threshold (0.11) sits just above the "reject" cluster,
and thresholds from 0.11 to 0.20 produce identical results. The
verifier's probability distribution remains strongly bimodal.

**The wide plateau from t=0.45 to t=0.80** (F1=0.744, constant)
reflects the gap between the reject and accept clusters: no candidates
have probabilities in this range, so sweeping through it changes
nothing.

---

## Methodological Note: Cluster-Level Evaluation

This experiment required a novel evaluation approach to handle
deduplicated cross-modal candidates correctly.

### The problem

Spatial deduplication clusters co-occurring detections from image and
text tracks. When two detections (one from each track) are within 20 m
on the same tile, they are merged into a single cluster. The cluster's
crop is extracted at the averaged centroid for verifier input.

Two evaluation approaches were tested:

1. **Averaged-centroid evaluation**: Use the averaged centroid as the
   single coordinate per cluster. This loses 3 TPs (recall drops from
   0.866 to 0.835) because averaging can push the representative
   coordinate beyond the 20 m matching buffer.

2. **Coordinate-level evaluation**: Use all 272 original member
   coordinates. This preserves recall (0.866) but inflates the
   detection count, depressing precision (0.309 instead of 0.457)
   because each cluster's second member is counted as a separate
   false positive.

### The solution

**Cluster-level evaluation with member-level matching**: use all
original member coordinates for the greedy spatial matcher (preserving
recall), but count at the cluster level for precision (each cluster
contributes one detection, regardless of member count). A cluster is
a TP if *any* of its members match a reference point within 20 m.

This approach correctly reports:

- Recall from the full member coordinate pool (0.866 unfiltered)
- Precision from the cluster count (0.457 unfiltered, 184 clusters)
- F1 as the harmonic mean of cluster-level precision and recall

The distinction matters: the initial (incorrect) coordinate-level
evaluation reported F1=0.566 at optimal threshold; the correct
cluster-level evaluation reports F1=0.768 — a 0.202 difference purely
from how duplicates are counted. Any pipeline that deduplicates
multi-source detections should use cluster-level evaluation.

---

## Implications

### Cross-modal fusion is confirmed as a recall strategy

The union proposer achieves the project's highest verified recall
(0.835). For use cases where recall is paramount (e.g., survey
completeness, preliminary site identification), the union pipeline is
preferable to either single-track approach.

### Precision-optimised fusion was tested and does not help

Two follow-up analyses tested whether the union's recall advantage
could be converted into an F1 advantage:

**Provenance-aware thresholding** (free reanalysis): Applying different
thresholds by provenance category (e.g., t=0.11 for both-track and
text-only, t=1.0 for image-only) was tested but cannot separate
image-only TPs from FPs. Of the 15 image-only FPs that pass t=0.11,
9 have probability 1.0 — identical to the TPs. The verifier is
confidently wrong about these candidates, and no threshold can fix it.

**HIGH-thinking verifier** ($0.50, 44 API calls): Re-verifying all
44 image-only candidates with `thinking_level="high"` (vs the original
`"minimal"`) made things *worse*. The HIGH-thinking verifier accepted
6 additional FPs (candidates that minimal-thinking correctly rejected)
while losing 1 TP (candidate 115: 0.85 → 0.30). Combined F1 dropped
from 0.768 to 0.747. Extended reasoning acts as a liberaliser, not
a regulariser: the model generates more elaborate justifications for
accepting candidates rather than more rigorous reasons to reject them.

**Evaluation methodology note**: The per-provenance TP counts in the
table above (65 + 12 + 7 = 84) cannot be summed to derive whole-pool
metrics. Each category is evaluated independently against all 97
references; when evaluated as a single pool, greedy matching assigns
each reference at most once, producing different TP/FP counts (81 TP,
33 FP at t=0.11). This is a standard property of 1:1 matching
evaluation.

See `results/phase3d-high-thinking-results.md` for the full
HIGH-thinking experiment write-up.

### The text-only pipeline remains the F1 champion

For balanced precision-recall performance, text-only proposer +
adversarial verifier (F1=0.796) remains the best single pipeline. The
union adds complexity and cost (184 vs 140 verifier calls) for a recall
gain that doesn't translate to F1 improvement.

### Remaining experiment options

1. **High-recall text proposer** (~$7) — if text-only recall can be
   pushed from 0.804 to ~0.85 through recall-biased prompting, the
   text-only pipeline may achieve both the recall and F1 advantages
2. **Provenance-informed verification** (~$1) — telling the verifier
   that the text track did NOT flag a location adds genuinely new
   information (unlike HIGH thinking, which only adds reasoning time)
