# H11 Results Report: Tile Size Effect on Detection Performance

**Author**: Shawn Ross
**Date**: 2026-03-15
**Status**: Complete (N=30 consensus results added; proposer-verifier pending)
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
| Consensus (T=0.7, N=30) | 30 | 240 | 7,200 | TBD |

Parse failures were resubmitted individually and merged into the affected
run GeoJSON files. The automatic parse-failure retry mechanism was added
during the N=30 campaign.

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

**H11 is conditionally supported but does not improve the project's best
result.** Smaller tiles improve detection when paired with consensus voting
(+2 pp over 512 N=5) or proposer-verifier (+2 pp over 384 consensus), but
the 384 proposer-verifier pipeline (best F1=0.684) falls well short of the
512 proposer-verifier (F1=0.796). The recall advantage of smaller tiles is
overwhelmed by the precision penalty of a denser false positive pool.

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

### 2.4 Consensus Pool Size Comparison (N=5, N=10, N=30)

| Config | Best threshold | F1 | P | R |
|:-------|---------------:|-----:|-----:|-----:|
| 384 N=5 | x=5 | **0.664** | 0.560 | 0.814 |
| 384 N=10 | x=10 | 0.648 | 0.595 | 0.711 |
| 384 N=30 | x=28 | 0.643 | 0.567 | 0.742 |

**N=30 does not improve over N=5 at 384.** Going from N=5 to N=30 *reduces*
F1 by −2.1 pp (0.664 → 0.643). This is the opposite of the pattern at 512,
where N=30 added +9.4 pp over N=5 (0.657 → 0.751 with HIGH thinking).

The explanation is recall saturation (Observation 160): individual 384 runs
achieve ~0.92 recall at T=0.7, so nearly every run finds nearly every mound.
Additional runs beyond N=5 contribute almost no new true positives while
inflating the false positive pool. Stricter thresholds can filter noise but
at the cost of discarding marginal true positives — producing diminishing
returns rather than the diversity dividend seen at 512.

### 2.5 Best Results in Context

| Configuration | N | Tolerance | F1 | P | R |
|:--------------|--:|----------:|-----:|-----:|-----:|
| 512 single-pass (Phase 2a) | 1 | 20 m | 0.542 | 0.434 | 0.725 |
| 512 consensus best at N=5 (Phase 2b) | 5 | 20 m | 0.657 | 0.644 | 0.670 |
| 384 consensus T>=5 | 5 | 20 m | 0.664 | 0.560 | 0.814 |
| 384 PV image (t=0.3) | 1+v | 20 m | 0.684 | 0.602 | 0.794 |
| 384 PV text-only (t=0.2) | 1+v | 20 m | 0.679 | 0.612 | 0.763 |
| 384 consensus best at N=30 | 30 | 20 m | 0.643 | 0.567 | 0.742 |
| 512 consensus best at N=30 (Phase 3a, HIGH) | 30 | 20 m | 0.751 | 0.772 | 0.732 |
| **512 PV text-only (Phase 3d)** | **1+v** | **20 m** | **0.796** | **0.809** | **0.784** |

The 384 proposer-verifier (F1=0.684) beats the 384 consensus (0.664) by
+2 pp, confirming that verification is the right precision intervention
when recall is saturated. However, it falls 11 pp short of the 512 PV
(0.796) because the denser candidate pool degrades verifier precision
(0.60 vs 0.81). The 512 proposer-verifier remains the project's best
configuration.

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

## 5. Proposer-Verifier Pipeline Results (384×384)

### 5.1 Design

The proposer-verifier pipeline pairs a high-recall 384 proposer with the
adversarial verifier from Phase 3d. The proposer runs single-pass detection
(T=0.0) on 240 tiles; the verifier independently evaluates 150×150 px crops
centred on each candidate, arguing for the strongest non-mound interpretation
before confirming (see `verify_adversarial.md`).

Two verifier tracks were tested to match the Phase 3d factorial:

| Track | Config | Examples | Phase 3d F1 (512) |
|:------|:-------|:---------|------------------:|
| Image | `verify_adversarial.json` | 9 reference images sent | 0.711 |
| Text-only | `verify_adversarial-text.json` | No example images | 0.796 |

### 5.2 Execution

| Stage | Tiles/Candidates | API Calls | Cost | Notes |
|:------|:-----------------|----------:|------:|:------|
| Proposer | 240 tiles (239 succeeded) | 240 | ~$0.03 | 1 persistent parse failure |
| Verifier (image) | 572 candidates | 572 | $0.70 | 10 workers, ~6 min |
| Verifier (text-only) | 572 candidates | 572 | $0.14 | 10 workers, ~4 min |

The proposer produced 572 detections across 239/240 tiles. One tile
(`K-35-062-2_Rakovski_x2352_y1344.png`) consistently returned malformed
JSON across three retry attempts.

### 5.3 Verifier Score Distributions

Both tracks produce strongly bimodal distributions — the adversarial framing
forces decisive accept/reject behaviour rather than hedging:

| Score bucket | Image track | Text-only track |
|:-------------|------------:|----------------:|
| 0.0 | 194 | 154 |
| 0.1 | 82 | 164 |
| 0.2–0.4 | 35 | 39 |
| 0.5–0.8 | 12 | 1 |
| 0.9–1.0 | 249 | 193 |
| **Verified (≥0.5)** | **261** | **215** |
| **Rejected (<0.5)** | **311** | **357** |

The text-only verifier is stricter: it rejects 62% of candidates vs 54%
for the image track. The image examples appear to bias the verifier towards
acceptance — the 0.1 bucket (strong non-mound, but not certain) swells from
82 to 164 in the text-only track, suggesting candidates that would receive
a tentative "possibly a mound" with image examples are more decisively
rejected without them.

### 5.4 Results at 20 m Tolerance

#### Image track (best threshold: 0.3)

| Threshold | Kept | TP | FP | FN | P | R | F1 |
|----------:|-----:|---:|---:|---:|------:|------:|------:|
| 0.1 | 171 | 83 | 88 | 14 | 0.485 | 0.856 | 0.619 |
| 0.2 | 133 | 78 | 55 | 19 | 0.586 | 0.804 | 0.678 |
| **0.3** | **128** | **77** | **51** | **20** | **0.602** | **0.794** | **0.684** |
| 0.5 | 122 | 74 | 48 | 23 | 0.607 | 0.763 | 0.676 |
| 0.9 | 117 | 72 | 45 | 25 | 0.615 | 0.742 | 0.673 |

#### Text-only track (best threshold: 0.2)

| Threshold | Kept | TP | FP | FN | P | R | F1 |
|----------:|-----:|---:|---:|---:|------:|------:|------:|
| 0.1 | 177 | 82 | 95 | 15 | 0.463 | 0.845 | 0.599 |
| **0.2** | **121** | **74** | **47** | **23** | **0.612** | **0.763** | **0.679** |
| 0.3 | 105 | 67 | 38 | 30 | 0.638 | 0.691 | 0.663 |
| 0.5 | 98 | 63 | 35 | 34 | 0.643 | 0.649 | 0.646 |
| 0.9 | 88 | 56 | 32 | 41 | 0.636 | 0.577 | 0.605 |

### 5.5 Multi-Tolerance Comparison

| Buffer | Image (t=0.3) | Text-only (t=0.2) | Phase 3d 512 text-only (t=0.2) |
|-------:|--------------:|-------------------:|-------------------------------:|
| 20 m | 0.684 | 0.679 | **0.796** |
| 30 m | 0.711 | 0.706 | — |
| 40 m | 0.711 | 0.706 | — |

Both tracks plateau at 30 m — only 3 additional true positives are recovered
between 20–30 m, and none beyond 30 m.

### 5.6 Analysis: Why 384 PV Underperforms 512 PV

The back-of-envelope prediction of F1 ≈ 0.83 assumed:

1. The 384 proposer recall advantage (+7 pp) would add ~7 true mounds
2. The verifier would maintain ~0.81 precision from Phase 3d

**Both assumptions partially held, but the net effect was negative:**

- **Recall**: The proposer recall advantage does feed more true mounds into
  the pipeline, but the verifier's own false negative rate erodes this. After
  verification, recall is 0.794 (image) / 0.763 (text-only) — below the
  proposer's raw 0.877, and only marginally above the 512 PV recall of 0.784.
- **Precision**: The 384 proposer generates ~4× the candidates (572 vs ~140
  at 512). The verifier achieves ~0.60 precision — substantially below the
  0.81 seen at 512. Each false positive has an independent chance of fooling
  the verifier, so more candidates means more false positives in the final
  output even at a constant per-candidate error rate.

The fundamental issue is that reducing tile size trades a linear recall gain
for a quadratic false positive increase (2× tiles × constant FP rate per
tile). The verifier is not selective enough to compensate. This mirrors the
single-pass mechanism from Section 4.3 — the precision penalty from denser
tiling propagates through the verification stage.

### 5.7 The Narrowing of the Text-Only vs Image Gap

At 512, the text-only adversarial verifier dramatically outperformed the
image variant (+8.5 pp F1: 0.796 vs 0.711). At 384, this gap narrows to
−0.5 pp (0.679 vs 0.684 — within noise).

| Tile Size | Image F1 | Text-only F1 | Gap |
|----------:|---------:|-------------:|----:|
| 512 | 0.711 | 0.796 | +8.5 pp |
| 384 | 0.684 | 0.679 | −0.5 pp |

Two factors may explain this convergence:

1. **Different false positive composition**: At 384, the false positives may
   be more visually distinctive (infrastructure, text, boundaries in smaller
   crops), making them easier for the verifier to reject even with the
   potentially distracting example images. At 512, the false positives may
   be more ambiguous, and the example images may prime the model towards
   false acceptance.
2. **Saturation of the adversarial framing**: With 572 candidates (vs ~140
   at 512), both tracks are working harder. The text-only track's advantage
   may be specific to a lower-volume candidate pool where individual
   decisions are more marginal.

This finding warrants further investigation across the full H11 tile size
range (Section 6, Q5).

---

## 6. Methodological Notes

### 6.1 Bounds Clipping

All 384 results are clipped to the 512 geographic footprint for fair
comparison. Without clipping, 47.5% of 384 detections fall outside the 512
evaluation area and are counted as false positives against an out-of-scope
reference set, producing misleadingly low F1 (0.245 vs the true 0.415).

Future work should consider whether the extended 384 footprint (727 km²)
has independent value for surveying — the model does detect real mounds in
the peripheral area, but we lack evaluated ground truth there.

### 6.2 Parse Failures

Four tiles across 2,400 single-pass submissions (0.17%) returned malformed
JSON from the model. These were resubmitted individually and merged into the
affected GeoJSON files. Automatic parse-failure retry via the synchronous
Application Programming Interface (API) is now built into the batch pipeline.
The proposer-verifier run had one persistent parse failure
(`K-35-062-2_Rakovski_x2352_y1344.png`) that failed on three successive
retry attempts, suggesting a tile-specific issue rather than a transient
API error.

### 6.3 Batch File Cleanup

The Gemini batch API assigns file IDs that exceed the 40-character limit for
the `files.delete()` endpoint. Cleanup failures are logged but do not affect
results — uploaded files auto-expire after 48 hours. This is a known issue
(#1759) in the batch pipeline.

---

## 7. Open Questions

1. ~~**N=30 at 384**~~: **Answered — no.** N=30 at 384 (best F1=0.643) does
   not match N=5 (F1=0.664), let alone the Phase 3a N=30 best (0.751).
   Recall saturation at 384 means additional runs add noise, not signal
   (see Section 2.4 and Observation 160).

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

5. **Text-only vs image gap at other tile sizes**: The text-only advantage
   that was substantial at 512 (+8.5 pp) disappeared at 384 (−0.5 pp).
   Running both verifier tracks across additional tile sizes (256, 448,
   1024) would determine whether this convergence is specific to 384 or
   a general feature of denser candidate pools.

---

## 8. File Inventory

| File | Location |
|:-----|:---------|
| Study YAML (single-pass) | `studies/h11-384-single-pass.yaml` |
| Study YAML (consensus) | `studies/h11-384-consensus.yaml` |
| Study YAML (proposer-verifier) | `studies/h11-384-proposer-verifier.yaml` |
| Single-pass outputs | `outputs/h11/single-pass-384/384/run_{1..10}/` |
| Consensus outputs (N=5) | `outputs/h11/consensus-384/384/run_{1..5}/` |
| Consensus outputs (N=30) | `outputs/h11/consensus-384/384/run_{1..30}/` |
| Consensus voting sweep | `outputs/h11/consensus-384/voting/` |
| Clipped single-pass | `outputs/h11/single-pass-384/384-clipped-to-512/` |
| Proposer-verifier outputs | `outputs/h11/proposer-verifier-384/` |
| Verifier config (image) | `prompts/configs/verify_adversarial.json` |
| Verifier config (text-only) | `prompts/configs/verify_adversarial-text.json` |
| 384 tiles | `inputs/tiles_384/` (zbook only) |
| 384 bounds | `inputs/vectors/bounds/384/validation_bounds.geojson` |
| 384 validation manifest | `inputs/tiles_384/validation_manifest.json` |
| This report | `results/h11-tile-size-results.md` |
