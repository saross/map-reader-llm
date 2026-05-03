# Subtype-classification accuracy on the 4-map gold-standard — analysis report

**Date**: 2026-04-21
**Recovery 2026-05-03**: data files refreshed against the post-recovery
GS-v2 consensus (commits `90890ae9..c6023034`). The 4-of-5 consensus
went from 607 to 608 detections; matched pairs at 50 m from 376 to 377
(+1 burial_mound, raising burial total from 294 to 295). Headline
weighted-F1 lifted from 0.8873 to **0.8876** (+0.0003) — unchanged at
the 3-decimal precision used in this report. The 27/47 benchmark →
triangulation cell, the asymmetric-confusion finding, and Level-1
accuracy = 1.000 are preserved exactly. Refreshed CIs in the headline
table; remaining confusion-matrix tables remain accurate at 3-decimal
precision (the +1 matched burial shifts column totals from 303 to 304
but row-normalised values are unchanged at three decimals; see source
CSVs for 4-decimal values).

**Analysis script**: `scripts/analyse_subtype_classification.py` v1.0.0
**Git commit at run time**: `508f7698` (original); `c6023034` (post-recovery refresh)
**Plan**: `planning/gold-standard-classification-accuracy-plan.md`
**Decision record**: `planning/gold-standard-classification-metrics-decisions.md`
**Primary observation**: Obs 270 (headline) and Obs 271 (new failure sub-pattern) in `docs/notes/reflections/working-notes.md`
**Related detection-level result**: corrected F1 ≥ 0.830 at 50 m on the 55-map image-generalisation set (`results/55maps-image-generalisation/human-reviewed-corrected/`)

## 1. Executive summary

The 5-pass VLM consensus pipeline produced **608** detections at 4-of-5 consensus (post-recovery 2026-05-03; was 607); **377** of these (was 376) matched expert ground-truth (GT) features at a 50 m buffer across the four calibration maps. Conditional on a correct detection, the VLM assigns the correct subtype with **weighted-F1 = 0.887 [0.850, 0.923]** (post-recovery; pre-recovery [0.849, 0.922]) and **Level-1 accuracy (mound-family vs settlement) = 1.000**. The pipeline is strong on the detection-to-subtype mapping in aggregate, but an asymmetric within-compound confusion dominates the error: **benchmark_mound is misread as triangulation_mound for 27 of 47 matched benchmarks (57 %)**, while the reverse confusion is zero. This is a **new sub-pattern not anticipated by the Obs 266 failure-mode taxonomy** — see §7 and Obs 271.

Headline metrics (50 m buffer, 4-of-5 consensus, matched-pairs 4×4):

| Metric                                  |   Value | 95 % bootstrap CI    |
|-----------------------------------------|--------:|----------------------|
| **Weighted-F1 (HEADLINE)**              | **0.887** | [0.850, 0.923]    |
| Macro-F1                                |   0.772 | [0.660, 0.822]       |
| Matched-pair accuracy                   |   0.904 | —                    |
| Level-1 accuracy (mound-family vs tell) |   1.000 | —                    |
| Level-2 accuracy (within mound-family)  |   0.904 | —                    |
| Cohen's kappa (unweighted)              |   0.728 | [0.659, 0.797]       |
| Cohen's kappa (linearly hierarchical)   |   0.736 | [0.665, 0.804]       |
| Multi-class Matthews (MCC)              |   0.744 | [0.681, 0.806]       |

Bootstrap: 10 000 iterations, matched-pair-level resample, stratified by map, seed 42.

## 2. Data

### 2.1 Ground truth and predictions

- **Ground truth**: `inputs/vectors/references/reference_*.geojson` (four files, 569 features total — burial 456 / benchmark 65 / triangulation 43 / settlement 5).
- **Predictions (headline)**: `outputs/h11/gold-standard-v2/consensus/consensus-4of5.geojson` (607 features).
- **Predictions (sweep)**: `consensus-3of5.geojson` (865 features), `consensus-5of5.geojson` (405 features). Both generated via `scripts/merge_passes.py` at thresholds 3 and 5.
- **Bounds**: `inputs/vectors/bounds/384/full_evaluation_bounds.geojson`.
- **Vocabulary mapping** (logged in `run_manifest.json`): `Burial mound`/`Burial Mound` → `burial_mound`; `Bench mark on burial mound` → `benchmark_mound`; `Triangulation point on burial mound` → `triangulation_mound`; `Settlement mound` → `settlement_mound`.

### 2.2 Per-class support on the matched-pairs 4-map subset (50 m buffer)

| Class               | GT total (all 4 maps) | GT matched at 50 m | Matched rate |
|---------------------|----------------------:|-------------------:|-------------:|
| burial_mound        |                  456  |                294 |        0.645 |
| benchmark_mound     |                   65  |                 47 |        0.723 |
| triangulation_mound |                   43  |                 33 |        0.767 |
| settlement_mound    |                    5  |                  2 |        0.400 |
| **Total**           |              **569**  |            **376** |    **0.661** |

The settlement matched rate (2 / 5) is the low outlier; see §9 for the per-feature trace.

## 3. Confusion matrices (50 m buffer, 4-of-5 consensus)

### 3.1 Matched-pairs 4×4 — raw counts

Rows = GT, columns = predicted.

|                     | burial | benchmark | triangulation | settlement | Row total |
|---------------------|-------:|----------:|--------------:|-----------:|----------:|
| burial_mound        |   294  |        0  |            0  |         0  |      294  |
| benchmark_mound     |     8  |       12  |           27  |         0  |       47  |
| triangulation_mound |     1  |        0  |           32  |         0  |       33  |
| settlement_mound    |     0  |        0  |            0  |         2  |        2  |
| **Col total**       | **303**|    **12** |        **59** |      **2** |  **376**  |

### 3.2 Matched-pairs 4×4 — row-normalised (recall view, P(predicted | GT))

|                     | burial | benchmark | triangulation | settlement |
|---------------------|-------:|----------:|--------------:|-----------:|
| burial_mound        | 1.000  |    0.000  |        0.000  |     0.000  |
| benchmark_mound     | 0.170  |    0.255  |        0.574  |     0.000  |
| triangulation_mound | 0.030  |    0.000  |        0.970  |     0.000  |
| settlement_mound    | 0.000  |    0.000  |        0.000  |     1.000  |

### 3.3 Matched-pairs 4×4 — column-normalised (precision view, P(GT | predicted))

|                     | burial | benchmark | triangulation | settlement |
|---------------------|-------:|----------:|--------------:|-----------:|
| burial_mound        | 0.970  |    0.000  |        0.000  |     0.000  |
| benchmark_mound     | 0.026  |    1.000  |        0.458  |     0.000  |
| triangulation_mound | 0.003  |    0.000  |        0.542  |     0.000  |
| settlement_mound    | 0.000  |    0.000  |        0.000  |     1.000  |

### 3.4 5×5 confusion matrix (adds no_match row/column)

Row `no_match` = detection with no matching GT at 50 m (false positive); column `no_match` = GT with no matching detection at 50 m (false negative).

|                     | burial | benchmark | triangulation | settlement | no_match | Row total |
|---------------------|-------:|----------:|--------------:|-----------:|---------:|----------:|
| burial_mound        |   294  |        0  |            0  |         0  |      162 |      456  |
| benchmark_mound     |     8  |       12  |           27  |         0  |       18 |       65  |
| triangulation_mound |     1  |        0  |           32  |         0  |       10 |       43  |
| settlement_mound    |     0  |        0  |            0  |         2  |        3 |        5  |
| no_match            |   159  |       55  |           15  |         2  |        0 |      231  |
| **Col total**       | **462**|    **67** |        **74** |      **4** |  **193** |   **800** |

### 3.5 Per-class precision / recall / F1 (matched-pairs 4×4, 50 m)

Bootstrap: 10 000 iterations, matched-pair-level, map-stratified, seed 42.

| Class               | Support | Precision | Recall | F1    | F1 95 % CI        | TP | FP | FN |
|---------------------|--------:|----------:|-------:|------:|:-----------------:|---:|---:|---:|
| burial_mound        |     294 |     0.970 |  1.000 | 0.985 | [0.974, 0.994]    | 294 |  9 |  0 |
| benchmark_mound     |      47 |     1.000 |  0.255 | 0.407 | [0.238, 0.557]    |  12 |  0 | 35 |
| triangulation_mound |      33 |     0.542 |  0.970 | 0.696 | [0.578, 0.795]    |  32 | 27 |  1 |
| settlement_mound    |       2 |     1.000 |  1.000 | 1.000 | — (sparse, n ≤ 5) |   2 |  0 |  0 |

- TP/FP/FN are measured on the 4×4 matched-pairs table — i.e., conditional on a correct detection.
- Settlement F1 is not bootstrapped per plan §5 (sparse-class policy).
- **Benchmark recall (0.255) and triangulation precision (0.542) are the weakest cells**; see §7 for mechanism.

## 4. Hierarchical decomposition

### 4.1 Level 1: mound-family (burial / benchmark / triangulation) vs settlement

|                | predicted mound-family | predicted settlement |
|----------------|-----------------------:|---------------------:|
| GT mound-family|                   374  |                   0  |
| GT settlement  |                     0  |                   2  |

**Level-1 accuracy = 1.000** (n = 376 matched pairs). On this subset, the VLM never crosses the mound-family ↔ settlement boundary when it has correctly located a feature. Obs 266's sub-pattern 3 ("settlement-class under-assignment") is **not** a Level-1 misclassification on matched pairs — see §6.

### 4.2 Level 2: plain burial / + benchmark / + triangulation (within mound-family)

|                     | burial | benchmark | triangulation |
|---------------------|-------:|----------:|--------------:|
| burial_mound        |   294  |        0  |            0  |
| benchmark_mound     |     8  |       12  |           27  |
| triangulation_mound |     1  |        0  |           32  |

**Level-2 accuracy = 0.904** (n = 374). Within the mound-family, the plain-vs-compound axis collapses almost entirely to a single cell: **benchmark → triangulation (27 cells)**. This is Obs 271's target — see §7.

### 4.3 Flat 4-class accuracy

0.904 (n = 376). Numerically identical to Level-2 accuracy because Level-1 is perfect on matched pairs.

## 5. Agreement measures

| Measure                               |  Value | 95 % CI          |
|---------------------------------------|-------:|------------------|
| Cohen's kappa (unweighted)            |  0.728 | [0.658, 0.797]   |
| Cohen's kappa (linearly hierarchical) |  0.736 | [0.664, 0.804]   |
| Multi-class Matthews (MCC)            |  0.744 | [0.681, 0.807]   |

The hierarchical kappa uses weights from decision D8: same-family errors (plain ↔ +benchmark ↔ +trig) weight 0.5; across-Level-1 errors (mound-family ↔ settlement) weight 1.0; diagonal 0.0. The lift from unweighted (0.728) to hierarchical (0.736) is small because Level-1 is perfect — all errors are already within the lower-weight class.

MCC (0.744) and hierarchical kappa (0.736) are close, as expected for a predominantly one-axis error structure.

## 6. Obs 266 verification — quantitative verdict

Plan §1.3 predicted three confusion-matrix signatures from the Obs 266 failure taxonomy. Quantitative verdicts:

| Obs 266 sub-pattern                              | Predicted signature                                     | Quantitative verdict                       |
|--------------------------------------------------|---------------------------------------------------------|--------------------------------------------|
| 1. Compound-boundary over-assignment             | Predicted trig/benchmark where GT has no match          | **Partially confirmed** (trig only; see below) |
| 2. Built-environment → settlement_mound          | Predicted settlement where GT has no match              | **Not confirmed on this subset** (n too small) |
| 3. Settlement-class under-assignment             | GT settlement → predicted burial (Level-1 error)        | **Confirmed but via missed detection, not Level-1 misclassification** |

- **Sub-pattern 1**: the 5×5 no_match row shows 55 predicted benchmarks and 15 predicted triangulations with no GT match. But benchmark has only +3 % over-prediction vs GT support (67 vs 65), while triangulation has +72 % (74 vs 43). The "over-assignment" pattern holds for triangulation but not benchmark. Obs 271 explains why: much of the apparent triangulation over-assignment is actually mis-labelled benchmarks from the matched-pairs side, not phantom triangulations from the unmatched-detection side.
- **Sub-pattern 2**: the pipeline produced only 4 predicted settlements corpus-wide; 2 of 4 are correct (fids 6, 26) and 2 of 4 are unmatched (potential FPs). n is too small for inference on this subset; the 55-map human-review data is the better testbed.
- **Sub-pattern 3**: 3 of 5 GT settlements are entirely unmatched at 50 m (fids 1, 3, 4 on K-35-052-4); 2 of 5 are correctly matched and correctly classified (fids 6, 26). No GT settlement was matched to a non-settlement detection. The pipeline's settlement failure is therefore a **detection** failure, not a **classification** failure. This refines Obs 266: settlement under-assignment lives in the 5×5 `settlement → no_match` row, not in the 4×4 `settlement → burial` cell.

## 7. New finding — asymmetric within-compound confusion (Obs 271)

The largest off-diagonal cell in the 4×4 matrix is **benchmark → triangulation at 27 / 47 matched benchmarks (57 %)**. The reverse cell (triangulation → benchmark) is **0 / 33**. The asymmetry is extreme and not predicted by Obs 266's original taxonomy, which treated the two compound classes symmetrically.

Consequences:

1. **Benchmark per-class recall collapses to 0.255** — the minority class among the well-supported subtypes is the hardest for the VLM.
2. **Triangulation precision collapses to 0.542** — half of the predictions labelled triangulation are actually benchmarks. Triangulation's apparent strong recall (0.970) masks this.
3. **Level-2 accuracy (0.904) is misleading without the per-class breakdown** — it reads as "90 % within mound-family" but the distribution of errors is concentrated in one asymmetric cell.

Per-map concentration: Rakovski carries 15 of 27 confusions (56 %). The pattern is present on every map that carries benchmarks, but Rakovski's dense benchmark population (31 of 65 corpus GT) amplifies it.

Mechanism hypothesis (see Obs 271 for full argument): symbol-similarity at 384 px + a triangulation-as-default attractor. Both symbols are compound marks on the burial-mound circle; at crop resolution, mark-shape may be sub-pixel-reliable, and the VLM falls back on a learned prior. The consensus-sweep evidence (§8) supports this — five independent passes converge on the wrong label, so this is confident systematic error, not vote noise.

Remediation is future work (Phase 2b): targeted prompt-engineering disambiguation, higher-resolution crops, or class-prior correction.

## 8. Consensus-threshold sweep

Per D3. Question: does higher vote-share consensus buy higher subtype accuracy? (Analogue of the verifier-calibration hypothesis from Obs 269.)

| Threshold | N detections | N matched | Weighted F1 | Macro F1 | Accuracy | Level-2 acc | Kappa (linear hier) | MCC    |
|-----------|-------------:|----------:|------------:|---------:|---------:|------------:|--------------------:|-------:|
| 3 / 5     |          865 |       400 |       0.891 |    0.769 |    0.908 |       0.907 |               0.734 |  0.742 |
| 4 / 5     |          607 |       376 |       0.887 |    0.772 |    0.904 |       0.904 |               0.736 |  0.744 |
| 5 / 5     |          405 |       326 |       0.888 |    0.780 |    0.905 |       0.904 |               0.747 |  0.754 |

**Weighted-F1 is flat** (0.891 / 0.887 / 0.888); **kappa creeps** from 0.734 to 0.747 (Δ = +0.013). The headline metric does not improve with consensus; the margin of improvement on secondary measures is within bootstrap noise.

Interpretation: vote-share is a signal for **detection** quality (higher consensus → fewer detections, higher per-detection precision — the Obs 269 pattern) but **not for subtype quality** among accepted detections. Higher consensus discards uncertain detections proportionally across all subtypes; the benchmark → triangulation confusion is approximately equally present at every threshold. This **contradicts the working hypothesis** that vote-share carries subtype-correctness signal — it does not.

## 9. Buffer sensitivity

Per plan §4.2. Question: is the subtype-error pattern an artefact of loose matching?

| Buffer (m) | N matched | Accuracy | Macro-F1 | Weighted-F1 | Level-1 acc | Level-2 acc | Kappa (linear hier) | MCC    |
|-----------:|----------:|---------:|---------:|------------:|------------:|------------:|--------------------:|-------:|
|         20 |       366 |    0.904 |    0.775 |       0.888 |       1.000 |       0.904 |               0.739 |  0.747 |
|         30 |       374 |    0.904 |    0.772 |       0.887 |       1.000 |       0.903 |               0.736 |  0.744 |
|         50 |       376 |    0.904 |    0.772 |       0.887 |       1.000 |       0.904 |               0.736 |  0.744 |

All metrics are effectively invariant to buffer choice across 20 m → 50 m. The risk flagged in plan §9 ("buffer may pair a subtype-mismatched GT that happens to be the nearest") is inactive on this subset. 50 m is retained as the headline buffer for continuity with the paper's detection F1.

## 10. Per-map diagnostic

Per plan §4.5 (diagnostic only; raw cells, no CIs).

| Map                      | N matched | Accuracy | Macro-F1 | Weighted-F1 |
|--------------------------|----------:|---------:|---------:|------------:|
| K-35-052-4 (Elhovo NW)   |        83 |    0.916 |    0.835 |       0.906 |
| K-35-053-3 (Elenovo)     |       129 |    0.938 |    0.798 |       0.931 |
| K-35-062-2 (Rakovski)    |       155 |    0.865 |    0.622 |       0.835 |
| K-35-078-1 (Lesovo)      |         9 |    1.000 |    1.000 |       1.000 |

Rakovski carries the largest error load — driven by its disproportionate benchmark count (31 of 65 benchmarks corpus-wide). Its macro-F1 (0.622) is dragged down by the benchmark recall (0.16 on this map; see §7). Lesovo is perfect but under-powered at n = 9.

The `per_map_confusion.csv` artefact gives per-map full 4×4 cells for QA inspection.

## 11. Settlement trace (sparse-class qualitative)

Per plan §5. With n = 5 GT settlements, individual inspection is cheap.

| Map                 | fid | Fate       | Predicted subtype  | Distance to match (m) |
|---------------------|----:|------------|--------------------|----------------------:|
| K-35-052-4          |   1 | unmatched  | no_match           |                     — |
| K-35-052-4          |   3 | unmatched  | no_match           |                     — |
| K-35-052-4          |   4 | unmatched  | no_match           |                     — |
| K-35-052-4          |   6 | correct    | settlement_mound   |                   9.5 |
| K-35-053-3 (Elenovo)|  26 | correct    | settlement_mound   |                   3.5 |

Three of four K-35-052-4 settlements are not detected at all; the pipeline's settlement failure mode is **missed detection**, not subtype misclassification. When matched, settlement is classified correctly (2 / 2). The matched detections are tight (3.5 m, 9.5 m — well inside the 20 m buffer). Obs 271 implication: settlement remediation should focus on the detection prompt, not the classification prompt.

## 12. Methods notes

### 12.1 Matching protocol

Reuses `scripts/lib_advanced_metrics.py::match_detections_to_references` (Hungarian algorithm, one-to-one, buffer in metres). Same matcher as the paper's detection F1 — consistency matters.

### 12.2 Bootstrap protocol

- Iterations: 10 000.
- Resample unit: **matched pair**, stratified by map (per D6).
- Seed: 42.
- Settlement F1 is not bootstrapped (per plan §5 sparse-class policy); its 2/2 cell is reported raw.
- CIs are percentile 2.5 / 97.5.

### 12.3 Vocabulary normalisation

The Rakovski case-variant `Burial Mound` (capital M) is case-folded to `Burial mound` at load time. The mapping is logged verbatim in `run_manifest.json` for audit.

### 12.4 VLM "confidence" ≠ posterior probability

The `confidence` field on each prediction is **vote-share across the 5 passes** (e.g., 0.8 = agreed on by 4 / 5 passes), not a per-class posterior probability. Brier score, PR-curves per class, and calibration analysis are therefore not computed for subtype classification — vote-share does not support them. This is explicit in plan §3.2 and re-stated here for the paper methods section.

## 13. Reproducibility

- Script: `scripts/analyse_subtype_classification.py` v1.0.0 (ruff-clean).
- Git commit at run time: `508f7698`.
- Random seed: 42.
- Bootstrap iterations: 10 000.
- Input hashes: `run_manifest.json` records the exact input paths and git-commit identifier (per-file SHA256s can be regenerated with `sha256sum inputs/vectors/references/reference_*.geojson` against the commit state).
- Compute: full bootstrap ran in ~2 min on sapphire (192.168.1.150); plan §8 estimated 30 min, which was conservative.
- Re-run command (from the repo root):

  ```bash
  python scripts/analyse_subtype_classification.py \
      --gt-dir inputs/vectors/references/ \
      --detections outputs/h11/gold-standard-v2/consensus/consensus-4of5.geojson \
      --bounds inputs/vectors/bounds/384/full_evaluation_bounds.geojson \
      --buffers 20 30 50 \
      --output-dir results/gold-standard-subtype-classification/ \
      --bootstrap-n 10000 \
      --seed 42 \
      --consensus-thresholds 3 4 5
  ```

## 14. Caveats and risk register

- **Sparse settlement class (n = 5 GT)**: a single error moves the ratio by 20 pp. We report raw cells and individual fates (§11); we do not smooth or bootstrap settlement F1.
- **Buffer-dependent matching**: although the sensitivity table (§9) shows invariance 20 m → 50 m, a subtype-mismatched GT being the nearest neighbour is a logical possibility. At 20 m the error pattern persists — this is real, not coincidence pairing.
- **Corpus scope**: 569 GT features across 4 maps is adequate for burial / benchmark / triangulation but under-powered for settlement. The 55-map human-review subset may deepen settlement and sub-pattern 2 evidence; treated as future work.
- **Vocabulary coverage**: the 4-class vocabulary assumes the GT legend is complete. The Rakovski case-variant (`Burial Mound`) is handled; no other out-of-vocabulary GT symbols were encountered.
- **VLM confidence quantisation**: §12.4 — vote-share is not a calibratable probability. Any "calibration" of subtype predictions would require a separate probability head.

## 15. Bug caught and fixed during audit

An `/audit` pass on the analysis script surfaced a bug in the `settlement_trace` output: the trace originally zipped the settlement pair-list to GT file-order, but the Hungarian matcher returns matched pairs in detection-index order — so fids were mis-assigned in the original trace. The fix threads `ref_global_idx` through `build_pair_list` and does a keyed lookup in `settlement_trace`. All other metric outputs (confusion matrices, F1, kappa, MCC, hierarchical decomposition, sweep, buffer sensitivity) are derived from the raw pair-list rather than fid-labelled rows and were **unaffected**. The sapphire analysis was re-run end-to-end after the fix; the present report reflects the corrected state.

## 16. Files in this directory

| File                                    | Contents |
|-----------------------------------------|----------|
| `confusion_matrix_4x4_buf50.csv`        | Raw + row-norm + col-norm blocks (§3.1–3.3) |
| `confusion_matrix_5x5_buf50.csv`        | Raw + row-norm + col-norm blocks (§3.4) |
| `per_class_f1_buf50.csv`                | Per-class P/R/F1 with 10k bootstrap CIs (§3.5) |
| `macro_weighted_summary.json`           | Headline weighted / macro / accuracy + CIs (§1) |
| `kappa_mcc.json`                        | Kappa (unweighted + linear hierarchical) + MCC + CIs (§5) |
| `hierarchical_decomposition.json`       | Level-1 and Level-2 confusion matrices + accuracies (§4) |
| `buffer_sensitivity.csv`                | 20 / 30 / 50 m comparison (§9) |
| `consensus_threshold_sweep.csv`         | 3/5, 4/5, 5/5 comparison (§8) |
| `per_map_confusion.csv`                 | Per-map 4×4 cells (§10) |
| `per_map_summary.csv`                   | Per-map summary row (§10) |
| `settlement_trace.csv`                  | Per-feature fate for 5 GT settlements (§11) |
| `run_manifest.json`                     | Git commit, seed, paths, vocabulary mapping (§13) |
| `analysis.log`                          | Structured log of the run |
| `run.log`                               | Sapphire stdout + stderr from the bootstrap run |
| `report.md`                             | This document |

## 17. Paper implications — quick take

1. **Headline for the subtype section**: weighted-F1 = 0.887 [0.849, 0.922] at 50 m / 4-of-5. Per-class F1: burial 0.985 / benchmark 0.407 / triangulation 0.696 / settlement 1.000 (2 / 2).
2. **Narrative framing**: "Conditional on correct detection, the VLM's subtype output is strong in aggregate (Level-1 = 1.000; weighted-F1 = 0.887) but carries a specific asymmetric failure at the benchmark ↔ triangulation boundary."
3. **Headline figure**: row-normalised 4×4 confusion heat map (§3.2) plus column-normalised (§3.3). Both perspectives are needed — the asymmetry is starker in the precision view.
4. **Quoted cells for text**: "27 of 47 matched benchmarks (57 %) were labelled triangulation; the reverse cell is empty."
5. **Settlement framing**: a one-paragraph note that settlement failure is detection-stage, not classification-stage. Quote the 3 / 5 unmatched fids and the 2 / 2 correct classification.
6. **Future-work paragraph**: prompt-engineering disambiguation for benchmark vs triangulation; higher-resolution crops; class-prior correction.

---

**End of report.**
