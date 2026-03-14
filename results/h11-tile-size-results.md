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
| 384 PV best (adversarial image, t=0.3) | 1+v | 20 m | 0.684 | 0.602 | 0.794 |
| 384 consensus best at N=30 | 30 | 20 m | 0.643 | 0.567 | 0.742 |
| 512 consensus best at N=30 (Phase 3a, HIGH) | 30 | 20 m | 0.751 | 0.772 | 0.732 |
| **512 PV text-only (Phase 3d)** | **1+v** | **20 m** | **0.796** | **0.809** | **0.784** |

The 384 proposer-verifier best (adversarial image, F1=0.684) beats the 384
consensus (0.664) by +2 pp, confirming that verification is the right
precision intervention when recall is saturated. All six 384 PV
configurations (3 strategies × 2 tracks) fall within a narrow 0.661–0.684
range, 11 pp short of the 512 PV (0.796). The denser candidate pool
degrades verifier precision across all strategies (0.53–0.61 vs 0.81). The
512 proposer-verifier remains the project's best configuration.

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

The proposer-verifier pipeline pairs a high-recall 384 proposer with each
of three verifier strategies from Phase 3d, tested across two example tracks
(image and text-only). The proposer runs single-pass detection (T=0.0) on
240 tiles; each verifier independently evaluates 150×150 px crops centred on
each candidate.

**Verifier strategies (3 × 2 factorial):**

| Strategy | System instruction | Framing |
|:---------|:-------------------|:--------|
| B (brief/standard) | `verify_brief.md` | Direct diagnostic classification |
| C (adversarial) | `verify_adversarial.md` | Argue for strongest non-mound interpretation |
| D (checklist) | `verify_checklist.md` | Structured evaluation of 5 diagnostic features |

Each strategy was run on two tracks: **image** (9 canonical reference images
sent alongside the candidate crop) and **text-only** (no example images; model
sees only the candidate crop and the system instruction).

### 5.2 Execution

| Stage | Items | API Calls | Cost | Notes |
|:------|------:|----------:|------:|:------|
| Proposer | 240 tiles (239 succeeded) | 240 | ~$0.03 | 1 persistent parse failure |
| Adversarial image | 572 candidates | 572 | $0.70 | 10 workers, ~6 min |
| Adversarial text-only | 572 candidates | 572 | $0.14 | 10 workers, ~4 min |
| Brief image | 572 candidates | 572 | $0.67 | 10 workers, ~6 min |
| Brief text-only | 572 candidates | 572 | $0.10 | 10 workers, ~3 min |
| Checklist image | 572 candidates | 572 | $0.71 | 10 workers, ~6 min |
| Checklist text-only | 572 candidates | 572 | $0.14 | 10 workers, ~3 min |
| **Total** | | **3,672** | **$2.49** | |

The proposer produced 572 detections across 239/240 tiles. One tile
(`K-35-062-2_Rakovski_x2352_y1344.png`) consistently returned malformed
JSON across three retry attempts.

### 5.3 Verification Rates by Strategy

| Strategy | Image verified | Image rejected | Text verified | Text rejected |
|:---------|---------------:|---------------:|--------------:|--------------:|
| Adversarial (C) | 261 (46%) | 311 (54%) | 215 (38%) | 357 (62%) |
| Brief (B) | 326 (57%) | 246 (43%) | 269 (47%) | 303 (53%) |
| Checklist (D) | 326 (57%) | 246 (43%) | 336 (59%) | 236 (41%) |

The adversarial strategy is consistently the strictest verifier. The checklist
is the most permissive — its structured feature decomposition appears to give
candidates more opportunities to accumulate evidence for mound classification.

### 5.4 Full Factorial Results (Best F1 at 20 m)

| Strategy | Track | Threshold | Kept | TP | FP | FN | P | R | F1 |
|:---------|:------|----------:|-----:|---:|---:|---:|------:|------:|------:|
| **Adversarial** | **image** | **0.3** | **128** | **77** | **51** | **20** | **0.602** | **0.794** | **0.684** |
| Adversarial | text | 0.2 | 121 | 74 | 47 | 23 | 0.612 | 0.763 | 0.679 |
| Brief | text | 0.2 | 131 | 77 | 54 | 20 | 0.588 | 0.794 | 0.675 |
| Checklist | image | 0.2 | 150 | 83 | 67 | 14 | 0.553 | 0.856 | 0.672 |
| Brief | image | 0.2 | 151 | 82 | 69 | 15 | 0.543 | 0.845 | 0.661 |
| Checklist | text | 0.2 | 157 | 84 | 73 | 13 | 0.535 | 0.866 | 0.661 |

The adversarial strategy (C) retains its Phase 3d advantage at 384, leading
the factorial with F1=0.684. All six configurations fall within a 2.3 pp
range (0.661–0.684), suggesting that the dominant constraint is the candidate
pool quality, not the verifier strategy.

### 5.5 Multi-Tolerance Comparison

| Strategy–Track | 20 m | 30 m | 40 m | Phase 3d 512 text (20 m) |
|:---------------|-----:|-----:|-----:|-------------------------:|
| Adversarial image (t=0.3) | **0.684** | 0.711 | 0.711 | — |
| Adversarial text (t=0.2) | 0.679 | 0.706 | 0.706 | **0.796** |
| Brief image (t=0.2) | 0.661 | 0.685 | 0.685 | — |
| Brief text (t=0.2) | 0.675 | 0.693 | 0.693 | 0.768 |
| Checklist image (t=0.2) | 0.672 | 0.696 | 0.696 | — |
| Checklist text (t=0.2) | 0.661 | 0.685 | 0.685 | 0.782 |

All configurations plateau at 30 m with no further gains at 40 m.

### 5.6 Analysis: Why 384 PV Underperforms 512 PV

The back-of-envelope prediction of F1 ≈ 0.83 assumed:

1. The 384 proposer recall advantage (+7 pp) would add ~7 true mounds
2. The verifier would maintain ~0.81 precision from Phase 3d

**Both assumptions partially held, but the net effect was negative:**

- **Recall**: The proposer recall advantage does feed more true mounds into
  the pipeline, but the verifier's own false negative rate erodes this. After
  verification, recall ranges from 0.763 to 0.866 — the checklist achieves
  the highest recall (0.866) but at the cost of more false positives.
- **Precision**: The 384 proposer generates ~4× the candidates (572 vs ~140
  at 512). All strategies achieve 0.53–0.61 precision, substantially below
  the 0.81 seen at 512. Each false positive has an independent chance of
  fooling the verifier, so more candidates means more false positives in the
  final output even at a constant per-candidate error rate.

The fundamental issue is that reducing tile size trades a linear recall gain
for a quadratic false positive increase (2× tiles × constant FP rate per
tile). No verifier strategy is selective enough to compensate. This mirrors
the single-pass mechanism from Section 4.3 — the precision penalty from
denser tiling propagates through the verification stage.

### 5.7 The Collapse of the Text-Only vs Image Gap

At 512, the text-only verifier dramatically outperformed the image variant
across all three strategies. At 384, this gap collapses:

| Strategy | 512 image | 512 text | 512 gap | 384 image | 384 text | 384 gap |
|:---------|----------:|---------:|--------:|----------:|---------:|--------:|
| Adversarial | 0.711 | 0.796 | +8.5 pp | 0.684 | 0.679 | −0.5 pp |
| Brief | 0.706 | 0.768 | +6.2 pp | 0.661 | 0.675 | +1.4 pp |
| Checklist | 0.706 | 0.782 | +7.6 pp | 0.672 | 0.661 | −1.1 pp |

The text-only advantage that was consistent and large at 512 (+6–9 pp)
disappears entirely at 384 (−1 to +1.4 pp, all within noise). This is not
strategy-specific — it holds across all three verifiers, ruling out
explanations specific to the adversarial framing.

Two factors likely explain this convergence:

1. **False positive composition**: At 384, the denser tiling produces more
   false positives that are visually distinctive (infrastructure, text,
   boundary symbols in smaller crops), making them easier to reject
   regardless of whether example images are present. At 512, the false
   positives may be more ambiguous, and example images may prime the model
   towards false acceptance.
2. **Volume dilution**: With 572 candidates (vs ~140 at 512), the marginal
   impact of example images on each individual decision is smaller relative
   to the noise floor of the candidate pool. The text-only advantage may
   require a lower-volume, more ambiguous candidate pool to manifest.

### 5.8 Strategy Ranking Comparison (384 vs 512)

The strategy ranking is preserved at 384 for both tracks:

| Rank | 512 text-only | 512 image | 384 text-only | 384 image |
|:-----|:--------------|:----------|:--------------|:----------|
| 1st | Adversarial (0.796) | Adversarial (0.711) | Adversarial (0.679) | Adversarial (0.684) |
| 2nd | Checklist (0.782) | Brief/Checklist (0.706) | Brief (0.675) | Checklist (0.672) |
| 3rd | Brief (0.768) | Brief/Checklist (0.706) | Checklist (0.661) | Brief (0.661) |

The adversarial strategy consistently leads. The brief and checklist strategies
are close to each other and swap positions across tracks — their difference
is within noise at both tile sizes.

### 5.9 Cascaded Verification (Exploratory)

Two cascade experiments tested whether a second verification stage could
improve precision by applying a different strategy to the first stage's
output:

| Cascade | F1 | P | R | Kept |
|:--------|-----:|------:|------:|-----:|
| Adversarial (t≥0.3) → Checklist text | 0.691 | 0.611 | 0.794 | 126 |
| Checklist image (t≥0.2) → Adversarial image | 0.684 | 0.602 | 0.794 | 128 |
| Adversarial image single-pass (reference) | 0.684 | 0.602 | 0.794 | 128 |

Both cascades converge to approximately the same ~128 candidates with
77 TP / 51 FP. The strategies' errors are near-perfectly correlated on
this candidate pool: the 51 false positives that survive one verifier also
survive the other. These candidates are genuinely mound-like to the model
regardless of evaluation framing.

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
