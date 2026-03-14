# H11 Results Report: Tile Size Effect on Detection Performance

**Author**: Shawn Ross
**Date**: 2026-03-14
**Status**: Preliminary (N=30 consensus results pending)
**Phase**: H11 (Tile Size)
**Model**: Gemini 3 Flash (`gemini-3-flash-preview`)

---

## Purpose

This report documents results from H11, which tests whether smaller tiles
(384×384, stride 336, 12.5% overlap) improve burial mound detection compared
to the standard 512×512 tiles (stride 448, 12.5% overlap). The hypothesis is
that 384 tiles increase the mound-to-tile area ratio from 3.9–9.8% (at 512)
to 5.2–13% (at 384), placing it more squarely within the literature's
4–10% sweet spot for object detection.

Results are evaluated in two configurations: single-pass (T=0.0) and
consensus voting (T=0.7, N=5).

---

## 1. Experimental Design

### 1.1 Conditions

| Tile Size | Tiles | Stride | Overlap | Mound-to-Tile Ratio |
|----------:|------:|-------:|--------:|:--------------------|
| 512 | 60 | 448 | 64 (12.5%) | 3.9–9.8% |
| 384 | 240 | 336 | 48 (12.5%) | 5.2–13% |

Both conditions use the same modality/elaboration configuration:
`detect_brief-text` (text-only, no example images). The 384 tile set was
generated with a 10% minimum geographic overlap threshold against the 512
validation region.

### 1.2 Fixed Parameters

| Parameter | Value |
|:----------|:------|
| Config | `detect_brief-text.json` |
| Modality | Text-only (tile image sent, text-only examples) |
| Thinking level | Minimal (config default) |
| Example set | Standard (plus-hp, minimal-neg, K=10) |
| Ordering | Config default (canonical-first) |

### 1.3 Execution Summary

| Experiment | Runs | Tiles/Run | Total API Calls | Parse Failures |
|:-----------|-----:|----------:|----------------:|---------------:|
| Single-pass (T=0.0) | 10 | 240 | 2,400 | 4 (0.17%) |
| Consensus (T=0.7, N=5) | 5 | 240 | 1,200 | 1 (0.08%) |

Parse failures were resubmitted individually and merged into the affected
run GeoJSON files.

### 1.4 Evaluation Design

| Parameter | Value |
|:----------|:------|
| Matching tolerance | 20 m (preregistered default) |
| Consensus clustering | 20 m |
| Within-run deduplication | 20 m |
| Bootstrap iterations | 1,000 |
| Ground truth | 569 reference mounds (97 in 512 scope, 242 in 384 scope) |

### 1.5 Geographic Scope and the Bounds Question

The 384 tile grid covers **727 km²** — nearly double the 512 grid's **370 km²** —
because edge tiles that meet the 10% overlap threshold extend well beyond the
512 footprint. This creates a critical evaluation decision:

- **242** reference mounds fall within the 384 bounds
- **97** reference mounds fall within the 512 bounds
- **47.5%** of 384 detections fall outside the 512 footprint

Evaluating 384 detections against 512 bounds produces misleadingly low F1
(0.245) because detections outside the 512 footprint are counted as false
positives with no corresponding references in scope.

**Resolution**: All 384 results in this report are **clipped to the 512
geographic footprint** before evaluation — detections outside the 512 bounds
union are discarded. This ensures both tile sizes are evaluated over the same
97 reference mounds in the same 370 km² area.

---

## 2. Headline Results

### 2.1 Primary Finding

**H11 is conditionally supported.** Smaller tiles improve detection only when
paired with consensus voting at high thresholds. Single-pass performance
degrades.

### 2.2 Single-Pass Comparison (T=0.0, 10 runs)

| Tile Size | F1 | 95% CI | Precision | Recall | Dets/Run |
|----------:|-----:|:------:|----------:|-------:|---------:|
| 512 | 0.542 | [0.424, 0.650] | 0.434 | 0.725 | ~162 |
| **384** | **0.415** | [0.393, 0.433]* | **0.272** | **0.877** | **~313** |

\* Per-run F1 range; formal bootstrap CI pending.

384 tiles boost recall by +15 pp but precision collapses by −16 pp, yielding
a net F1 drop of −13 pp. Within the same 370 km² evaluation area, 384 tiles
produce nearly **2× the detections** (~313 vs ~162) because more tiles cover
the same area (each smaller tile still generates ~2.5 detections on average).

### 2.3 Consensus Comparison (T=0.7, N=5)

| Config | F1 | Precision | Recall | Dets |
|:-------|-----:|----------:|-------:|-----:|
| **512 T>=1** | 0.378 | 0.254 | 0.742 | 284 |
| 384 T>=1 | 0.307 | 0.184 | **0.918** | 483 |
| **512 T>=2** | **0.540** | 0.444 | 0.691 | 151 |
| 384 T>=2 | 0.447 | 0.296 | **0.918** | 301 |
| **512 T>=3** | **0.607** | **0.587** | 0.629 | 104 |
| 384 T>=3 | 0.518 | 0.368 | **0.876** | 231 |
| 512 T>=4 | 0.584 | 0.614 | 0.557 | 88 |
| **384 T>=4** | **0.578** | 0.439 | **0.845** | 187 |
| 512 T>=5 | 0.497 | 0.650 | 0.402 | 60 |
| **384 T>=5** | **0.664** | **0.560** | **0.814** | 141 |

The 512 consensus peaks at T>=3 (F1=0.607) and then degrades as the high
vote threshold eliminates too many detections (recall drops to 0.40 at T>=5).
The 384 consensus improves monotonically up to T>=5 (F1=0.664) because the
denser detection pool retains sufficient signal even under strict filtering.

**Crossover point**: 384 consensus first exceeds 512 consensus at T>=4
(0.578 vs 0.584 — approximately equal) and clearly surpasses it at T>=5
(0.664 vs 0.497).

### 2.4 Best Results in Context

| Configuration | N | Tolerance | F1 | P | R |
|:--------------|--:|----------:|-----:|-----:|-----:|
| 512 single-pass (Phase 2a) | 1 | 20 m | 0.542 | 0.434 | 0.725 |
| 512 consensus best at N=5 (Phase 2b) | 5 | 20 m | 0.657 | 0.644 | 0.670 |
| **384 consensus T>=5** | **5** | **20 m** | **0.664** | **0.560** | **0.814** |
| 512 consensus best at N=30 (Phase 3a, MINIMAL) | 30 | 20 m | 0.683 | 0.657 | 0.711 |
| 512 consensus best at N=30 (Phase 3a, MINIMAL) | 30 | 40 m | 0.782 | 0.752 | 0.814 |

The 384 consensus at N=5 already matches the 512 consensus at N=5 (F1 0.664
vs 0.657) while delivering substantially higher recall (0.814 vs 0.670).
The 384 result achieves the same recall as the best 512 N=30 result at 40 m
tolerance — but with only 5 runs instead of 30 and at the tighter 20 m
tolerance.

**Pending**: N=30 consensus at 384 (25 additional runs in progress) will
enable a direct comparison with the Phase 3a N=30 results.

---

## 3. Multi-Tolerance Analysis (384 Consensus N=5)

All results clipped to the 512 geographic footprint.

| Threshold | 20 m F1 | 30 m F1 | 40 m F1 | 50 m F1 |
|----------:|--------:|--------:|--------:|--------:|
| T>=1 | 0.307 | 0.314 | 0.317 | 0.317 |
| T>=2 | 0.447 | 0.457 | 0.462 | 0.462 |
| T>=3 | 0.518 | 0.537 | 0.543 | 0.543 |
| T>=4 | 0.578 | 0.592 | 0.599 | 0.599 |
| T>=5 | 0.664 | 0.681 | 0.689 | 0.689 |

At 40 m tolerance, 384 consensus T>=5 achieves F1=0.689. This is above the
512 best at 20 m (0.683) but below the 512 best at 40 m (0.782). The gap
at 40 m (0.689 vs 0.782) suggests the 512 N=30 pool's larger voting base
provides additional discriminative power that N=5 at 384 cannot match despite
the denser detection pool.

---

## 4. Mechanism: Why Smaller Tiles Help Recall but Hurt Precision

### 4.1 Detection Density

| Metric | 512 | 384 |
|:-------|----:|----:|
| Tiles covering 370 km² | 60 | ~120 |
| Detections per tile | ~2.7 | ~2.5 |
| Total detections in 370 km² | ~162 | ~313 |

The per-tile detection rate is similar, but twice as many tiles cover the
same area, producing approximately twice the total detections.

### 4.2 Why Recall Improves

The mound-to-tile area ratio hypothesis (H11) appears correct: at 384×384,
burial mounds occupy a larger fraction of the tile, making them more
visually salient to the model. This manifests as a +15 pp recall gain
(0.877 vs 0.725 in single-pass). The model genuinely finds more mounds.

### 4.3 Why Precision Degrades

Each tile independently generates false positives at a roughly constant
rate (~2.5 detections/tile regardless of tile size). With ~2× more tiles
covering the same area, the absolute number of false positives approximately
doubles while the number of true positives grows by only ~15%, producing a
substantial precision drop (0.272 vs 0.434).

### 4.4 Why Consensus Rescues Performance

Consensus voting exploits the higher detection density. True mounds appear
consistently across overlapping 384 tiles and across runs, accumulating
votes. Random false positives are spatially inconsistent and fail to reach
high vote thresholds. The unanimous agreement filter (T>=5) is particularly
effective because 384 tiles generate enough overlapping detections to achieve
unanimity for real mounds while filtering out the noise.

At 512, the T>=5 filter is too aggressive — the sparser detection pool
means even real mounds sometimes fail to appear in all 5 runs (recall drops
to 0.402). At 384, the denser pool sustains recall at 0.814 even under
unanimous filtering.

---

## 5. Methodological Notes

### 5.1 Bounds Clipping

All 384 results are clipped to the 512 geographic footprint for fair
comparison. Without clipping, 47.5% of 384 detections fall outside the 512
evaluation area and are counted as false positives against an out-of-scope
reference set, producing misleadingly low F1 (0.245 vs the true 0.415).

Future work should consider whether the extended 384 footprint (727 km²)
has independent value for surveying — the model does detect real mounds in
the peripheral area, but we lack evaluated ground truth there.

### 5.2 Parse Failures

Four tiles across 2,400 single-pass submissions (0.17%) returned malformed
JSON from the model. These were resubmitted individually and merged into the
affected GeoJSON files. A pipeline improvement to handle parse-failure retry
automatically is planned (tracked as a development task).

### 5.3 Batch File Cleanup

The Gemini batch API assigns file IDs that exceed the 40-character limit for
the `files.delete()` endpoint. Cleanup failures are logged but do not affect
results — uploaded files auto-expire after 48 hours. This is a known issue
(#1759) in the batch pipeline.

---

## 6. Open Questions

1. **N=30 at 384**: Can the 384 consensus with a larger voting pool (N=30)
   match or exceed the Phase 3a best of F1=0.782 at 40 m? The 25 additional
   runs are in progress. The high recall at N=5 (0.814) suggests the
   detection pool is rich enough to sustain performance at high thresholds.

2. **Optimal tile size**: Is 384 the optimum, or would 448 or 320 perform
   differently? The current results show 384 is not a drop-in improvement
   over 512 — it requires consensus voting to realise its advantage. A
   tile size that increases recall without doubling the tile count might
   offer a better precision/recall balance.

3. **Cost-effectiveness**: 384 tiles require 4× the API calls per pass
   (240 vs 60 tiles). At N=5 consensus, this is 1,200 vs 300 calls for
   a +0.7 pp F1 gain over the best 512 N=5 result. Whether this tradeoff
   is worthwhile depends on the application's recall requirements.

4. **Evaluation scope**: The 384 grid covers 727 km² vs 370 km². The
   peripheral detections outside the 512 footprint are discarded in this
   analysis but may represent genuine archaeological features worth
   evaluating against independent ground truth.

---

## 7. File Inventory

| File | Location |
|:-----|:---------|
| Study YAML (single-pass) | `studies/h11-384-single-pass.yaml` |
| Study YAML (consensus) | `studies/h11-384-consensus.yaml` |
| Single-pass outputs | `outputs/h11/single-pass-384/384/run_{1..10}/` |
| Consensus outputs (N=5) | `outputs/h11/consensus-384/384/run_{1..5}/` |
| Consensus voting sweep | `outputs/h11/consensus-384/voting/` |
| Clipped single-pass | `outputs/h11/single-pass-384/384-clipped-to-512/` |
| 384 tiles | `inputs/tiles_384/` (zbook only) |
| 384 bounds | `inputs/vectors/bounds/384/validation_bounds.geojson` |
| 384 validation manifest | `inputs/tiles_384/validation_manifest.json` |
| This report | `results/h11-tile-size-results.md` |
