# Subtype Classification Accuracy (4-map Gold Standard)

**Generated**: 2026-04-20 (analysis); consolidated 2026-04-20
**Buffer**: 50 m (headline); 20 / 30 m also reported (invariant)
**Bounds**: `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` (4 gold-standard maps, 569
reference features; 376 matched pairs at the 50 m buffer, 4-of-5 consensus)
**Source**: `results/gold-standard-subtype-classification/report.md`

## Suggested paper text

> "Conditional on correct detection, the pipeline assigns the correct subtype with weighted-F1 = 0.887 [0.849, 0.922] on the 4-map gold standard (Table `subtype-classification.md`); per-class performance is dominated by an asymmetric benchmark → triangulation confusion (27 of 47 benchmarks mislabelled; reverse cell empty)."

Drop-in sentence for the classification / results section, positioned as a supplementary metric after the detection F1 headline. Cross-references Obs 270 / 271 in working-notes for the mechanism discussion.

## Framing (paper role)

**Supplementary classification metric, conditional on correct detection — NOT a substitute for the
detection F1 headline.** The pipeline's detection F1 (see paper §"Detection performance" and
`metrics_master.json`) is the primary performance claim. This table answers a distinct question:
**given that the pipeline correctly located a feature, how often does it assign the correct subtype?**

The two metrics operate on different denominators. Detection F1 is evaluated against all 569 reference
features regardless of class and counts position agreement. Subtype F1 is evaluated against the 376
correctly-matched pairs at 50 m and counts label agreement on the 4-class subtype vocabulary
(burial_mound / benchmark_mound / triangulation_mound / settlement_mound).

## Headline metrics (50 m buffer, 4-of-5 consensus, matched-pairs 4×4)

| Metric | Value | 95 % CI |
|---|---:|---|
| **Weighted-F1 (headline)** | **0.887** | [0.849, 0.922] |
| Macro-F1 | 0.772 | [0.660, 0.822] |
| Accuracy (flat 4-class) | 0.904 | — |
| Level-1 accuracy (mound-family vs settlement) | 1.000 | — |
| Level-2 accuracy (within mound-family) | 0.904 | — |
| Cohen's kappa (unweighted) | 0.728 | [0.658, 0.797] |
| Cohen's kappa (linearly hierarchical) | 0.736 | [0.664, 0.804] |
| Multi-class Matthews (MCC) | 0.744 | [0.681, 0.807] |

Weighting scheme for the hierarchical kappa: same-family errors (plain ↔ +benchmark ↔ +triangulation)
weight 0.5; across-Level-1 errors (mound-family ↔ settlement) weight 1.0; diagonal 0.0. The small lift
from unweighted (0.728) to hierarchical (0.736) kappa reflects that Level-1 is perfect on matched
pairs — all errors are already within the lower-weight class.

## Per-class precision / recall / F1 (matched-pairs 4×4, 50 m)

| Class | Support | Precision | Recall | F1 | F1 95 % CI | TP | FP | FN |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| burial_mound | 294 | 0.970 | 1.000 | 0.985 | [0.974, 0.994] | 294 | 9 | 0 |
| benchmark_mound | 47 | 1.000 | 0.255 | 0.407 | [0.238, 0.557] | 12 | 0 | 35 |
| triangulation_mound | 33 | 0.542 | 0.970 | 0.696 | [0.578, 0.795] | 32 | 27 | 1 |
| settlement_mound | 2 | 1.000 | 1.000 | 1.000 | sparse (n ≤ 5, no CI) | 2 | 0 | 0 |

TP / FP / FN counts are on the 4×4 matched-pairs table (i.e., conditional on correct detection).
Settlement F1 is not bootstrapped per plan §5 sparse-class policy; its 2 / 2 cell is reported raw.

## Asymmetric within-compound confusion (Obs 270 / 271)

The largest off-diagonal cell in the 4×4 matrix is **benchmark → triangulation, at 27 / 47 matched
benchmarks (57 %)**. The reverse cell (triangulation → benchmark) is **0 / 33**. This asymmetry is
extreme and drives three downstream effects:

1. **Benchmark recall collapses to 0.255** — the minority class among the well-supported subtypes is
   the hardest for the Vision Language Model (VLM).
2. **Triangulation precision collapses to 0.542** — half of the triangulation predictions are actually
   benchmarks.
3. **Level-2 accuracy (0.904) is misleading without the per-class breakdown** — it reads as "90 %
   within mound-family" but the errors are concentrated in one asymmetric cell.

Per-map concentration: Rakovski (K-35-062-2) carries 15 of 27 confusions (56 %). The pattern is
present on every map that carries benchmarks, but Rakovski's dense benchmark population (31 of 65
corpus-wide) amplifies it. Mechanism hypothesis and full detail: see Obs 270 (headline) and Obs 271
(new sub-pattern) in `docs/notes/reflections/working-notes.md`, and §7 of the source report.

## Settlement: detection failure, not classification failure

Three of the five ground-truth settlement features are entirely unmatched at 50 m (detection
failures); the remaining two are correctly matched and correctly classified (2 / 2). No GT settlement
was matched to a non-settlement detection. The pipeline's settlement failure mode is therefore a
**detection** failure, not a **classification** failure — remediation should target the detection
prompt, not the classification prompt. See source report §11 for per-feature trace.

## Methods notes

- **Bootstrap**: 10 000 iterations, matched-pair-level resample, stratified by map, seed = 42
  (cf. errata E54 on bootstrap counts — the 10 000 iteration count for this analysis is deliberate
  and separate from the paper-wide 1 000-iteration detection-F1 default).
- **Matching**: Hungarian algorithm, one-to-one, 50 m buffer in metres; reuses
  `scripts/lib_advanced_metrics.py::match_detections_to_references` — same matcher as the paper's
  detection F1.
- **Buffer invariance**: weighted-F1 is effectively constant across 20 / 30 / 50 m (0.888 / 0.887 /
  0.887). The risk that a subtype-mismatched GT is chosen as the nearest neighbour is inactive on
  this subset; 50 m is retained as the headline buffer for continuity with the detection F1.
- **Consensus sweep**: 3-of-5 / 4-of-5 / 5-of-5 weighted-F1 is flat (0.891 / 0.887 / 0.888). Higher
  consensus does not buy higher subtype accuracy — vote-share is a detection-quality signal, not a
  subtype-quality signal. This contradicts the working hypothesis that vote-share would carry
  subtype-correctness signal (see source report §8).
- **Confidence ≠ posterior probability**: the per-prediction `confidence` field is vote-share across
  the 5 passes, not a calibratable posterior. Brier score and per-class PR-curves are therefore not
  computed for subtype classification.

## Companion artefacts

- Source report (full 17 sections, confusion matrices, per-map diagnostics, settlement trace):
  `results/gold-standard-subtype-classification/report.md`.
- Machine-readable per-class P / R / F1 with CIs:
  `results/gold-standard-subtype-classification/per_class_f1_buf50.csv`.
- Headline summary JSON: `results/gold-standard-subtype-classification/macro_weighted_summary.json`.
- Agreement measures JSON: `results/gold-standard-subtype-classification/kappa_mcc.json`.
- Hierarchical decomposition JSON:
  `results/gold-standard-subtype-classification/hierarchical_decomposition.json`.
- Confusion matrices (4×4 and 5×5, raw / row-norm / col-norm):
  `results/gold-standard-subtype-classification/confusion_matrix_{4x4,5x5}_buf50.csv`.
- Consensus-threshold sweep and buffer sensitivity:
  `results/gold-standard-subtype-classification/{consensus_threshold_sweep,buffer_sensitivity}.csv`.
- Run manifest (git commit, seed, paths, vocabulary mapping):
  `results/gold-standard-subtype-classification/run_manifest.json`.
- Companion CSV with the headline and per-class rows in this directory:
  `subtype-classification.csv`.
