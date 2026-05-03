# 55-map corrected runs: tile-level MCC cross-run summary (v2)

**Generated**: 2026-04-27 (initial 3-run); extended 2026-04-28 to add
text-MIN as a fourth corrected run; refreshed 2026-05-03 (cross-track-v2
commit `42ed1d32`) to incorporate post-recovery numbers from all four
corrected runs (T=0.7 + image + text-MIN re-evaluations against the
canonical 4,745-mound updated curator ground truth; T=0.3 unchanged).
**Scope**: tile-level Matthews Correlation Coefficient (MCC), sensitivity, and specificity for the four manually-corrected 55-map runs (T=0.3 text-HIGH, T=0.7 text-HIGH, image, text-MIN), against the canonical post-review ground truth.
**Methodology mirror**: `scripts/evaluate_detections.py --mcc --bootstrap 1000 --seed 42`, mirroring commit `163161a4` (matrix sweep MCC re-eval).
**Policy**: per `feedback_mcc_with_f1.md`, MCC must accompany F1 wherever inputs support it; this report closes the gap for the four corrected 55-map runs.

## 1. Input convention

All four runs are evaluated against:

- **Ground truth**: `inputs/vectors/references/student-mounds-55maps-reviewed.geojson` (4,744 features) — the canonical post-review GT used by `compute_corrected_f1_multi_buffer.py`.
- **Bounds**: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson` (8,541 tiles).
- **Buffers**: 50, 75, 100, 125, 150 m (canonical for the corrected-F1 pipeline).
- **Bootstrap**: 1,000 iterations, seed 42, tile-level resampling.

**Methodological choice — student GT vs extended GT.** The corrected-F1 pipeline (`compute_corrected_f1_multi_buffer.py`) augments the student GT with reviewer-promoted phantoms (Approach B: extended-GT-at-R Hungarian matching). For MCC, however, the matrix-sweep convention (commit `163161a4`) uses standard tile-level classification against the un-augmented reviewed GT. This report follows the matrix convention: MCC against `student-mounds-55maps-reviewed.geojson`, no phantoms. Rationale — comparability with the other 55-map MCC artefacts (T=0.7 and image full-buffer-eval already used this convention) and with the matrix sweep. An extended-GT MCC variant could be added later but is not required for the cross-run comparison this report addresses.

**MCC is buffer-invariant** under this implementation: tile classification is binary ("does the tile contain any reference mound? does the tile contain any detection?"), with no buffer-dependent matching. The MCC values reported are therefore single per-run figures and do not vary across the [50, 75, 100, 125, 150] m buffer set. Sensitivity and specificity are likewise buffer-invariant.

## 2. Per-run MCC, sensitivity, specificity

Detection counts (verified): T=0.3 = 4,350; T=0.7 = 4,164 (post-recovery; +21 from pre-recovery 4,143); image = 4,680 (post-recovery; +15 from pre-recovery 4,665, including the +1 phantom-promoted from cand 2397); text-MIN = 3,865 (post-recovery; +4 from pre-recovery 3,861; recovery was effectively no-op). All four are evaluated over the same 8,541 tiles and the canonical 4,745-mound updated curator GT.

| Run | Detections | TP | TN | FP | FN | MCC [95% CI] | Sensitivity | Specificity |
|:----|----------:|---:|---:|---:|---:|:------------:|------------:|------------:|
| 55maps-text-high-t0.3-generalisation | 4,350 | 2,216 | 4,906 | 255 | 1,164 | **0.6538** [0.6393, 0.6684] | 0.6556 | 0.9506 |
| 55maps-text-high-generalisation (T=0.7) | 4,164 | 2,176 | 4,918 | 243 | 1,204 | **0.6476** [0.6331, 0.6620] | 0.6438 | 0.9529 |
| 55maps-image-generalisation | 4,680 | 2,394 | 4,891 | 270 | 986 | **0.6924** [0.6784, 0.7062] | 0.7083 | 0.9477 |
| 55maps-text-min-generalisation | 3,865 | 2,075 | 4,927 | 234 | 1,305 | **0.6260** [0.6114, 0.6408] | 0.6139 | 0.9547 |

Post-recovery 2026-05-03 (cross-track-v2 commit `42ed1d32`): three rows refreshed against the canonical updated curator GT (4,745 mounds). T=0.7 row refreshed against the post-recovery evaluation (n_detections 4,143 → 4,164, +21); MCC shifts from 0.6472 to 0.6476 (negligible). image row refreshed against the cand 2397 promotion (n_detections 4,665 → 4,680; TP 2,390 → 2,394; FN 990 → 986); MCC shifts from 0.6912 to 0.6924 (negligible). text-MIN row refreshed (n_detections 3,861 → 3,865; TP 2,072 → 2,075; FN 1,308 → 1,305); MCC shifts from 0.6253 to 0.6260 (negligible). Qualitative ranking is preserved on all four rows: image leads MCC; T=0.3 and T=0.7 sit closely below; text-MIN remains last. T=0.3 row carries forward unchanged from the 2026-04-27 baseline. text-MIN was first added on 2026-04-28 (commit `7b7509d5`).

## 3. Cross-run comparison at canonical buffer R = 50 m

Corrected-F1 numbers come from `results/<run>/corrected-f1-multi-buffer/summary.json` (Approach B, extended-GT-at-R Hungarian matching with reviewer-promoted phantoms).

| Run | Corrected F1 @50m [95% CI] | P @50m | R @50m | MCC [95% CI] | F1 rank | MCC rank |
|:----|:--------------------------:|------:|-----:|:-------------:|:-------:|:--------:|
| T=0.3 (text-HIGH) | 0.844 [0.834, 0.852] | 0.912 | 0.785 | **0.654** [0.639, 0.668] | 1 | 2 |
| T=0.7 (text-HIGH) | 0.827 [0.817, 0.837] | 0.912 | 0.757 | **0.648** [0.633, 0.662] | 3 | 3 |
| Image | 0.833 [0.824, 0.842] | 0.881 | 0.790 | **0.692** [0.678, 0.706] | 2 | 1 |
| text-MIN | 0.797 [0.786, 0.808] | 0.913 | 0.707 | **0.626** [0.611, 0.641] | 4 | 4 |

## 4. Rank-order disagreement

- **F1 rank** (corrected, R = 50 m): T=0.3 (0.8437) > Image (0.8332) > T=0.7 (0.8273) > text-MIN (0.7968).
- **MCC rank**: Image (0.6924) > T=0.3 (0.6538) > T=0.7 (0.6476) > text-MIN (0.6260).

The F1 leader (T=0.3) is **not** the MCC leader (image). The disagreement concentrates on the T=0.3-vs-image swap at the top. **Both metrics agree text-MIN is bottom and T=0.7 sits in the middle of the text-track**; the divergence is confined to the T=0.3-vs-image positions. text-MIN's joint-bottom result confirms HIGH thinking earns its tokens at 55-map scope on both metrics — the in-corpus extension of Obs 284's 4-map matrix finding. The post-recovery 2026-05-03 refresh leaves all four rank positions and both rank orderings unchanged.

This is exactly the pattern documented in **Obs 280** (working-notes.md L13642, 2026-04-26): "Pervasive F1 / MCC tier-leader divergence ... text track wins F1 (saturating, high-recall detection profile); image track wins MCC (selective profile with high TN)." The corrected 55-map runs reproduce that pattern under the post-review GT and the corrected-F1 pipeline:

- **Text proposers (T=0.3, T=0.7) win on F1 via higher precision-and-FN-trading**: text precision is ~0.91 vs image ~0.88, with similar recall profiles. F1 (the harmonic mean of precision and recall) rewards the precision lead while ignoring TN.
- **Image proposers win on MCC via higher sensitivity**: image sensitivity is 0.71 vs text 0.64–0.66, with comparable specificity (~0.95). MCC weights all four confusion-matrix cells equally; the image profile populates more TP tiles without a TN penalty, lifting MCC.

The buffer-elasticity finding from **Obs 252** (text track ~4× lower buffer elasticity than image) is consistent with this picture: text detections sit closer to GT centroids (tighter spatial precision per detection), but image detections cover more tiles overall (higher tile-level recall / sensitivity).

## 5. R-sensitivity check (corrected F1 across [50, 75, 100, 125, 150] m)

The F1 rank order is **not stable across R**. Image catches up to (and overtakes) T=0.3 by R = 75 m, because image's recall-per-detection compounds faster with buffer relaxation than text's already-tight spatial pattern.

| R (m) | T=0.3 F1 | T=0.7 F1 | Image F1 | text-MIN F1 | Leader |
|:-----:|:--------:|:--------:|:--------:|:--------:|:------:|
| 50 | **0.844** | 0.827 | 0.833 | 0.797 | T=0.3 |
| 75 | 0.847 | 0.830 | **0.849** | 0.799 | image |
| 100 | 0.849 | 0.832 | **0.854** | 0.801 | image |
| 125 (practitioner cap) | 0.850 | 0.834 | **0.855** | 0.801 | image |
| 150 (upper bound) | 0.851 | 0.835 | **0.857** | 0.802 | image |

text-MIN is bottom at every buffer; its precision-leaning profile (P=0.913, R=0.707) compounds less with buffer relaxation than the HIGH-thinking conditions (~0.005 absolute F1 gain from R=50 m to R=150 m, vs ~0.007 for HIGH text conditions whose F1 already sits near the corpus ceiling, and ~0.023 for the image track whose buffer elasticity remains the largest of the four).

Source: `results/<run>/corrected-f1-multi-buffer/summary.json`.

At R = 125 m (the practitioner-useful cap per Obs 272 — beyond which the attractor-pull effect is statistically indistinguishable from within-tile random placement), image leads F1 by ~0.005 over T=0.3. MCC, being buffer-invariant, gives a single image-leads-by-0.039 verdict that holds regardless of buffer.

## 6. Practical implication

For this corpus + pipeline (55-map generalisation set, post-review GT, corrected-F1 with reviewer-promoted phantoms), the answer to "which configuration is best?" depends on the metric:

- **If the reader trusts F1 at R = 50 m as the headline**, T=0.3 leads.
- **If the reader trusts F1 at R = 125 m (practitioner cap)**, image leads.
- **If the reader trusts MCC as a balanced classifier metric**, image leads.

This is exactly the pattern Obs 280 anticipated: paper structure should report both F1 and MCC in parallel, not single-metric.

## 7. Cross-references and provenance

- **Obs 252** (Buffer elasticity, working-notes.md L11047): text ~4× lower elasticity than image — explains why text wins F1 at tight R but image catches up as R relaxes.
- **Obs 272**: attractor-pull effect significant only through 125 m; 150 m row is upper bound, not practitioner-useful.
- **Obs 280**: F1/MCC tier-leader divergence pattern (text wins F1, image wins MCC) — confirmed here for the corrected 55-map runs.
- **Commit `163161a4`** (matrix sweep MCC re-eval): methodology mirror — same `evaluate_detections.py --mcc --bootstrap 1000 --seed 42` invocation pattern.
- **Commit `bdd61bcc`** (MCC rendering fix): MCC now appears in `evaluation.md` and `evaluation.csv` alongside `evaluation.json`.
- **Commit `98b128ae`** (initial 3-run re-eval data commit): the per-run MCC artefacts that grounded the 2026-04-27 baseline of this report.
- **Commit `42ed1d32`** (cross-track-v2): post-recovery image / T=0.7 / text-MIN re-evaluations against the 4,745-mound updated curator GT — the source of the 2026-05-03 row refreshes in §2.

### Per-run MCC artefact locations

- `results/55maps-text-high-t0.3-generalisation/mcc/evaluation.{json,csv,md}` — new (commit `98b128ae`); unchanged in 2026-05-03 refresh.
- `results/55maps-text-high-generalisation/mcc/evaluation.{json,csv,md}` — new (commit `98b128ae`); refreshed post-recovery 2026-05-03 (commit `42ed1d32`); MCC matches `outputs/55maps-text-high-generalisation/full-buffer-eval/evaluation.json` (0.6476).
- `results/55maps-image-generalisation/mcc/evaluation.{json,csv,md}` — new (commit `98b128ae`); refreshed post-recovery 2026-05-03 (commit `42ed1d32`); MCC matches `outputs/55maps-image-generalisation/full-buffer-eval/evaluation.json` (0.6924).
- `results/55maps-text-min-generalisation/mcc/evaluation.{json,csv,md}` — new (commit `7b7509d5`, 2026-04-28); refreshed post-recovery 2026-05-03 (commit `42ed1d32`); MCC matches `outputs/55maps-text-min-generalisation/full-buffer-eval/evaluation.json` (0.6260).

Reproducibility command (run on sapphire):

```bash
python3 scripts/evaluate_detections.py \
  --detections outputs/<run>/verified/verified_detections.geojson \
  --ground-truth inputs/vectors/references/student-mounds-55maps-reviewed.geojson \
  --bounds inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson \
  --buffers 50 75 100 125 150 \
  --bootstrap 1000 --seed 42 --mcc \
  --output-dir results/<run>/mcc \
  --label "<run>"
```
