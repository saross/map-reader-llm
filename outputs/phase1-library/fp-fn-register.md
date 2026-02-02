# Phase 1 False Positive / False Negative Register

**Purpose**: Comprehensive register of all false positives (FPs) and false negatives
(FNs) from the Phase 1 library construction baseline (image-only, 5 passes, 20
calibration tiles). This register supports hard example selection (Decision 4) and
future library size experiments (H10-H15).

**Source data**: `merged_detections_fp.geojson`, `merged_detections_fn.geojson`,
per-sheet reference files in `inputs/vectors/references/`

**Selection methodology**: Two-dimensional ranking combining *frequency* (vote count /
miss rate) with *localisation accuracy* (proximity to nearest counterpart). See
[Ranking Framework](#ranking-framework) below. Post-hoc regression to quantify marginal
contribution of each example (preregistration §8.4.5).

**Generated**: 2026-02-01

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Total merged detections | 128 |
| False positives (hard negative candidates) | 91 |
| False negatives (hard positive candidates) | 24 |
| True positives (matched at any threshold) | 37 |
| Ground truth references in calibration tiles | ~50 (from 569 total across all sheets) |

---

## Ranking Framework

Each error is characterised on two independent dimensions:

### Dimension 1: Frequency (vote count / miss rate)

- **FPs**: ranked by vote count across 5 passes (5/5 = most systematic)
- **FNs**: all 24 are tied at 5/5 miss rate (missed in every pass), so this
  dimension provides no differentiation

### Dimension 2: Localisation accuracy (proximity)

Measures whether the error represents a *recognition failure* (the model saw nothing
nearby) or a *localisation failure* (the model detected something in the right area
but placed it outside the 20m matching tolerance).

**For FNs** — distance from missed reference to nearest detection (any vote level):

| Category | Distance | Interpretation |
|----------|----------|----------------|
| Recognition failure | >50m | Model completely missed the feature |
| Localisation failure | 20-50m | Model detected something nearby but placed it poorly |

**For FPs** — distance from false detection to nearest ground truth reference:

| Category | Distance | Interpretation |
|----------|----------|----------------|
| Hallucination | >500m | No real feature anywhere nearby |
| Distant | 100-500m | Possibly confused by a distant feature |
| Moderate | 50-100m | Marginal spatial relationship to a real feature |
| Marginal | 30-50m | Close to a real feature but clearly misplaced |
| Near-miss | 20-30m | Barely outside the 20m matching tolerance |

### Combined ranking (hardest first)

- **FNs**: Recognition failures ranked farthest-first, then localisation failures
  ranked farthest-first
- **FPs**: Primary sort by vote count (descending), secondary sort by reference
  distance (descending, i.e., hallucinations before near-misses)

---

## FN Register (Hard Positive Candidates)

All 24 FNs have identical miss frequency (5/5 = 100%). They are differentiated solely
by the localisation accuracy dimension: distance from the missed ground truth reference
to the nearest merged detection.

### Recognition Failures (9 FNs) — nearest detection >50m

These references have **no detection anywhere nearby**. The model completely failed to
recognise the feature. These are the hardest hard positive candidates.

| Rank | fid | Symbol | Map | Easting | Northing | Nearest det. | Det. votes | Author |
|------|-----|--------|-----|---------|----------|-------------|-----------|--------|
| 1 | 354 | Burial mound | Rakovski | 316035 | 4680216 | 2449.9m | 5 | Lachlan Hanley |
| 2 | 249 | Burial mound | Lesovo | 466964 | 4645357 | 1807.8m | 5 | Briana Barton |
| 3 | 399 | BM on burial mound | Rakovski | 316546 | 4675395 | 847.4m | 5 | Lachlan Hanley |
| 4 | 15 | Burial mound | Rakovski | 319731 | 4673949 | 705.5m | 1 | Shawn Ross |
| 5 | 556 | Burial mound | K-35-052-4 | 408621 | 4688051 | 572.1m | 5 | Samuel Riley |
| 6 | 105 | Burial mound | Elenovo | 424510 | 4696739 | 243.6m | 2 | Stephanie Black |
| 7 | 161 | Burial mound | Elenovo | 426480 | 4693923 | 148.0m | 1 | Stephanie Black |
| 8 | 99 | Burial mound | Elenovo | 423446 | 4696655 | 96.4m | 2 | Stephanie Black |
| 9 | 489 | Burial mound | K-35-052-4 | 404689 | 4696704 | 50.3m | 3 | Samuel Riley |

**Observations**:

- The top 5 are truly isolated misses (>500m from any detection) — these represent
  features the model has no capacity to recognise in its current configuration
- Ranks 1-3 cluster on Rakovski — this sheet may have particularly challenging
  cartographic conditions or mound symbol variants
- Rank 3 (fid 399) is the only "Bench mark on burial mound" FN — a compound symbol
  that may look different from standard burial mounds
- Rank 9 (fid 489, 50.3m) is borderline — a vote-3 detection at 50.3m just barely
  failed both the 20m tolerance and the 50m near-miss threshold

### Localisation Failures (15 FNs) — nearest detection 20-50m

These references have a detection **nearby but outside the 20m tolerance**. The model
partially recognised the feature but placed it inaccurately. Ranked by distance
(farthest = hardest localisation error).

| Rank | fid | Symbol | Map | Easting | Northing | Nearest det. | Det. votes | Author |
|------|-----|--------|-----|---------|----------|-------------|-----------|--------|
| 10 | 76 | Burial mound | Elenovo | 422553 | 4698814 | 47.6m | 2 | Stephanie Black |
| 11 | 17 | Burial mound | Rakovski | 320197 | 4673463 | 37.5m | 5 | Shawn Ross |
| 12 | 155 | Burial mound | Elenovo | 428622 | 4694288 | 34.7m | 2 | Stephanie Black |
| 13 | 188 | Burial mound | Elenovo | 428578 | 4692805 | 31.2m | 3 | Stephanie Black |
| 14 | 468 | Burial mound | K-35-052-4 | 414365 | 4699252 | 31.0m | 1 | Samuel Riley |
| 15 | 245 | Burial mound | Lesovo | 466418 | 4648292 | 29.9m | 5 | Briana Barton |
| 16 | 466 | Burial mound | K-35-052-4 | 412869 | 4699083 | 28.9m | 1 | Samuel Riley |
| 17 | 160 | Burial mound | Elenovo | 426972 | 4693362 | 28.1m | 2 | Stephanie Black |
| 18 | 412 | Burial mound | Rakovski | 318509 | 4672680 | 27.5m | 2 | Stephanie Black |
| 19 | 157 | Burial mound | Elenovo | 428800 | 4693957 | 26.8m | 1 | Stephanie Black |
| 20 | 238 | Burial mound | Elenovo | 433528 | 4688978 | 24.7m | 2 | Stephanie Black |
| 21 | 490 | Burial mound | K-35-052-4 | 404509 | 4696780 | 24.1m | 2 | Samuel Riley |
| 22 | 74 | Burial mound | Elenovo | 424501 | 4697335 | 22.1m | 4 | Stephanie Black |
| 23 | 18 | Burial mound | Rakovski | 320195 | 4673378 | 20.6m | 1 | Shawn Ross |
| 24 | 156 | Burial mound | Elenovo | 428238 | 4694251 | 20.4m | 1 | Stephanie Black |

**Observations**:

- 8 of 15 localisation failures are on Elenovo — this sheet has a disproportionate
  share of near-misses, suggesting the model partially recognises features there but
  struggles with precise placement
- Ranks 11, 15, and 22 have high-vote nearby detections (5, 5, and 4 respectively) —
  the model *confidently and repeatedly* detected these features but placed them
  20-38m from the reference. These may reflect reference annotation imprecision as
  much as model error
- The localisation failures concentrate in the 20-35m range, just outside the 20m
  tolerance — a tolerance of 40m would reclassify most of these as TPs

### FN Distribution Summary

| Category | Count | Map distribution |
|----------|-------|-----------------|
| Recognition failures (>50m) | 9 | Rakovski 3, Elenovo 3, K-35-052-4 2, Lesovo 1 |
| Localisation failures (20-50m) | 15 | Elenovo 8, K-35-052-4 3, Rakovski 3, Lesovo 1 |
| **Total** | **24** | Elenovo 11, Rakovski 6, K-35-052-4 5, Lesovo 2 |

---

## FP Register (Hard Negative Candidates)

FPs are ranked primarily by vote count (Dimension 1), secondarily by distance to
nearest ground truth reference (Dimension 2, descending = hallucinations first).

### FP Vote Distribution

| Vote count | FPs | Meets ≥3/5 threshold | Hallucinations | Near-miss/Marginal |
|------------|-----|----------------------|----------------|-------------------|
| 5/5 | 6 | Yes | 4 | 2 |
| 4/5 | 3 | Yes | 2 | 1 |
| 3/5 | 9 | Yes | 2 | 5 |
| 2/5 | 14 | No | 3 | 6 |
| 1/5 | 59 | No | 15 | 22 |

### Tier 1: Vote 5/5 (6 FPs) — Most systematic

| Rank | Subtype | Tile | E | N | Nearest ref | Ref fid | Proximity |
|------|---------|------|---|---|------------|---------|-----------|
| 1 | burial_mound | Rakovski_x0_y3136 | 315509 | 4672881 | 1896.0m | 416 | Hallucination |
| 2 | triangulation_mound | Lesovo_x1344_y896 | 465692 | 4644072 | 1807.8m | 249 | Hallucination |
| 3 | burial_mound | K-35-052-4_x1344_y1344 | 404070 | 4698143 | 872.9m | 478 | Hallucination |
| 4 | burial_mound | Elenovo_x3136_y3136 | 434246 | 4689081 | 725.0m | 238 | Hallucination |
| 5 | burial_mound | Rakovski_x896_y2688 | 320213 | 4673430 | 37.5m | 17 | Marginal |
| 6 | burial_mound | Lesovo_x1344_y0 | 466443 | 4648307 | 29.9m | 245 | Near-miss |

**Observations**:

- Ranks 1-4 are **systematic hallucinations**: detected 5/5 times with no real feature
  within 700m. These are the strongest hard negative candidates — the model is
  consistently and confidently fabricating detections
- Rank 2 is `triangulation_mound` — a standalone triangulation point already covered
  by canonical negatives; confirms the confusion pattern
- Rank 5 (37.5m from ref fid 17) and Rank 6 (29.9m from ref fid 245) are systematic
  detections very near real references. These may be annotation offset issues or
  genuine nearby confusable features. Note that fid 17 appears as FN rank 11 (a
  localisation failure) — the same detection is simultaneously an FP and the nearest
  detection to an FN

### Tier 2: Vote 4/5 (3 FPs) — Highly systematic

| Rank | Subtype | Tile | E | N | Nearest ref | Ref fid | Proximity |
|------|---------|------|---|---|------------|---------|-----------|
| 7 | burial_mound | Elenovo_x2240_y2240 | 429810 | 4693479 | 1117.8m | 157 | Hallucination |
| 8 | benchmark_mound | Elenovo_x2240_y3584 | 428882 | 4687480 | 916.3m | 235 | Hallucination |
| 9 | burial_mound | Elenovo_x896_y1344 | 424492 | 4697355 | 22.1m | 74 | Near-miss |

**Observations**:

- Rank 8 is `benchmark_mound` — the model sees a benchmark symbol and associates it
  with a mound (a known confusable type)
- Rank 9 (22.1m from ref fid 74) is barely outside tolerance. Ref fid 74 appears as
  FN rank 22 — another mutual FP/FN near-miss pair

### Tier 3: Vote 3/5 (9 FPs) — Meets preregistered threshold

| Rank | Subtype | Tile | E | N | Nearest ref | Ref fid | Proximity |
|------|---------|------|---|---|------------|---------|-----------|
| 10 | burial_mound | Lesovo_x3136_y2688 | 475652 | 4635088 | 5922.4m | 24 | Hallucination |
| 11 | burial_mound | Lesovo_x896_y3136 | 464370 | 4633361 | 2259.4m | 565 | Hallucination |
| 12 | burial_mound | K-35-052-4_x1344_y1344 | 404452 | 4696789 | 57.8m | 490 | Moderate |
| 13 | burial_mound | K-35-052-4_x1344_y1344 | 404645 | 4696729 | 50.3m | 489 | Moderate |
| 14 | burial_mound | Lesovo_x1344_y0 | 467390 | 4649087 | 38.5m | 241 | Marginal |
| 15 | triangulation_mound | K-35-052-4_x1344_y2240 | 404858 | 4693817 | 32.3m | 4 | Marginal |
| 16 | burial_mound | Elenovo_x1792_y2240 | 428547 | 4692810 | 31.2m | 188 | Marginal |
| 17 | burial_mound | Rakovski_x896_y3136 | 318865 | 4671541 | 26.5m | 419 | Near-miss |
| 18 | triangulation_mound | K-35-052-4_x2240_y3584 | 410191 | 4687769 | 24.8m | 560 | Near-miss |

**Observations**:

- Ranks 10-11 are isolated hallucinations on Lesovo tiles with very sparse reference
  coverage — the model fabricates detections in areas with few real features
- Ranks 15 and 18 are `triangulation_mound` — further confirmation that standalone
  triangulation points are a systematic confusable
- Ranks 12-13 are close together on the same tile, near refs fid 490 and 489 (which
  are FN ranks 21 and 9 respectively) — a cluster of mutual near-misses

### Tier 4: Vote 2/5 (14 FPs) — Below preregistered threshold

| Rank | Subtype | Tile | E | N | Nearest ref | Proximity |
|------|---------|------|---|---|------------|-----------|
| 19 | burial_mound | Lesovo_x3584_y3136 | 477610 | 4633894 | 7901.1m | Hallucination |
| 20 | burial_mound | Lesovo_x896_y3136 | 464324 | 4633371 | 2224.9m | Hallucination |
| 21 | burial_mound | Lesovo_x896_y3136 | 464077 | 4633566 | 2134.4m | Hallucination |
| 22 | settlement_mound | Elenovo_x896_y1344 | 422497 | 4698852 | 68.3m | Moderate |
| 23 | burial_mound | Elenovo_x896_y1344 | 422506 | 4698823 | 57.8m | Moderate |
| 24 | burial_mound | Elenovo_x896_y1344 | 423419 | 4696747 | 47.6m | Marginal |
| 25 | burial_mound | Elenovo_x1792_y2240 | 427016 | 4693371 | 45.3m | Marginal |
| 26 | burial_mound | Elenovo_x1792_y2240 | 427903 | 4693885 | 44.3m | Marginal |
| 27 | burial_mound | Rakovski_x896_y3136 | 318536 | 4672677 | 38.0m | Marginal |
| 28 | burial_mound | Elenovo_x1792_y2240 | 428592 | 4694305 | 34.7m | Marginal |
| 29 | burial_mound | Elenovo_x1792_y2240 | 426995 | 4693379 | 28.1m | Near-miss |
| 30 | burial_mound | Rakovski_x896_y3136 | 320202 | 4672554 | 27.5m | Near-miss |
| 31 | burial_mound | Elenovo_x3136_y3136 | 433548 | 4688992 | 24.7m | Near-miss |
| 32 | burial_mound | K-35-052-4_x1344_y1344 | 404485 | 4696782 | 24.1m | Near-miss |

**Observations**:

- Rank 22 is the only `settlement_mound` FP — a unique confusion type
- Lesovo tiles dominate the hallucination category at this tier, consistent with
  sparse reference coverage on that sheet

### Tier 5: Vote 1/5 (59 FPs) — Sporadic false alarms

These appeared in only a single pass. Not listed individually — see
`merged_detections_fp.geojson` for coordinates.

| Proximity category | Count |
|-------------------|-------|
| Hallucination (>500m) | 15 |
| Distant (100-500m) | 8 |
| Moderate (50-100m) | 14 |
| Marginal (30-50m) | 12 |
| Near-miss (20-30m) | 10 |

---

## Distribution Summaries

### FP by Map Sheet

| Map sheet | Total | Vote ≥3 | Hallucinations (≥3) |
|-----------|-------|---------|---------------------|
| K-35-053-3_Elenovo | 48 | 3 | 0 |
| K-35-078-1_Lesovo | 23 | 4 | 4 |
| K-35-052-4_32635 | 10 | 5 | 1 |
| K-35-062-2_Rakovski | 10 | 6 | 1 |
| **Total** | **91** | **18** | **6** |

Elenovo dominates total FP count (53%) but has **zero hallucinations at ≥3 votes** —
its systematic FPs are all near real features. Lesovo contributes all 4 of its
systematic FPs as hallucinations, suggesting the model fabricates detections in areas
with sparse reference coverage.

### FP by Subtype

| Subtype | Count | % |
|---------|-------|---|
| burial_mound | 85 | 93.4% |
| triangulation_mound | 3 | 3.3% |
| benchmark_mound | 2 | 2.2% |
| settlement_mound | 1 | 1.1% |

---

## Selection Implications

### Hard Negatives (from FPs): Recommended Top 4

Selecting the 4 hardest: vote 5/5 AND hallucination (>500m from any reference).

| Priority | Rank | Subtype | Map sheet | Nearest ref | Rationale |
|----------|------|---------|-----------|------------|-----------|
| 1 | 1 | burial_mound | Rakovski | 1896.0m | Most isolated systematic hallucination |
| 2 | 3 | burial_mound | K-35-052-4 | 872.9m | Systematic hallucination, different sheet |
| 3 | 4 | burial_mound | Elenovo | 725.0m | Systematic hallucination, different sheet |
| 4 | 2 | triangulation_mound | Lesovo | 1807.8m | Systematic hallucination, different sheet + different subtype |

**Alternates** (for library expansion):

- Tier 1 ranks 5-6 (vote 5/5, near-miss) — interesting as "systematic near-confusions"
- Tier 2 ranks 7-8 (vote 4/5, hallucinations) — next strongest systematic fabrications
- Tier 3 ranks 10-11 (vote 3/5, hallucinations on Lesovo) — sparse-area fabrications

### Hard Positives (from FNs): Recommended Top 4

~~Selecting the 4 hardest: recognition failures, farthest from any detection, one per
map sheet for diversity.~~

**SUPERSEDED (Session 7)**: The original selection below was based on distance from
nearest detection with one-per-sheet stratification. Session 7 discovered that fids
354, 249, and 556 are entirely outside all calibration tile polygons (boundary
artefacts, see errata E7). Revised selection prioritises recognition failures with
confirmed in-tile visibility, relaxing one-per-sheet in favour of genuine examples.

#### Original selection (superseded)

| Priority | Rank | fid | Map sheet | Nearest det. | Rationale | Status |
|----------|------|-----|-----------|-------------|-----------|--------|
| 1 | 1 | 354 | Rakovski | 2449.9m | Most isolated complete miss | **Out of scope** — outside all tiles |
| 2 | 2 | 249 | Lesovo | 1807.8m | Second most isolated, different sheet | **Out of scope** — outside all tiles |
| 3 | 5 | 556 | K-35-052-4 | 572.1m | Most isolated on this sheet | **Out of scope** — outside all tiles |
| 4 | 6 | 105 | Elenovo | 243.6m | Most isolated on this sheet | Confirmed ✓ |

#### Revised selection (Session 7)

Selection criteria: recognition failures only (>50m from any detection), ranked by
votes of nearest detection (descending) then distance (descending). One-per-sheet
relaxed because Lesovo and K-35-052-4 had no recognition failures. Minimum ~5px
edge clearance required (fid 161 excluded — symbol truncated at west edge of tile).

| Priority | fid | Map sheet | Nearest det. | Source tile | Rationale |
|----------|-----|-----------|-------------|-------------|-----------|
| 1 | 399 | Rakovski | 1243.1m | x448_y2688 | Recognition failure, confirmed in-tile |
| 2 | 99 | Elenovo | 1047.1m | x896_y1344 | Recognition failure, confirmed in-tile |
| 3 | 15 | Rakovski | 905.6m | x896_y2688 | Recognition failure, confirmed in-tile |
| 4 | 105 | Elenovo | 243.6m | x896_y1344 | Recognition failure, confirmed in-tile (retained from original) |

See Decision 4 in `docs/methodology/preregistration/decisions-log.md` for full rationale.

**Alternates** (for library expansion):

- Remaining recognition failures (ranks 4, 7-9) are next in difficulty
- Localisation failures (ranks 10-24) would be added when expanding the library for
  H10-H15 experiments, with the regression analysis (§8.4.5) quantifying each
  example's marginal F1 contribution

### Tiebreaker Discussion

After applying both ranking dimensions, the top 4 selections for each category are
well-differentiated (no ties). For future library expansion where more candidates must
be ranked, options include:

**Map sheet stratification** (recommended):

- *Pro*: Different sheets have different cartographic styles, paper condition, and
  scanning quality. Stratifying ensures the library captures diverse visual contexts.
- *Pro*: Consistent with the study's use of 4 distinct map sheets for ecological
  validity.
- *Con*: Introduces a selection criterion not explicitly stated in the preregistration.

**Random selection** (defensible alternative):

- *Pro*: Fully objective, eliminates all selection bias, easily reproducible with a
  documented seed.
- *Pro*: More conservative for a preregistered study — avoids post-hoc reasoning
  about which sheets are "harder".
- *Con*: May cluster examples on one sheet and miss spatial diversity.

**Spatial isolation** (additional metric):

- Prefer examples that are far from *other selected examples* to maximise diversity
  of the library set. This is a greedy sequential criterion: after selecting the first
  example, each subsequent selection maximises minimum distance to all previously
  selected examples.

**Recommendation**: Use map sheet stratification as the primary tiebreaker (one per
sheet), with random selection (documented seed) for ties within a sheet. Record the
rationale and seed in Decision 4. The spatial isolation metric could serve as a
validation check (verify that selected examples are not spatially clustered).

---

## Future Library Size Experiments

For H10-H15 (library size variation), the full register provides the ranked pool:

- **Hard negatives**: 6 hallucinations at ≥3/5, 8 total hallucinations at ≥2/5, 18
  total at ≥3/5, 91 total
- **Hard positives**: 9 recognition failures, 15 localisation failures, 24 total

The two-dimensional ranking provides a natural expansion order:

1. **Core library (Scale-8)**: Top 4 recognition failures + top 4 hallucinations
2. **First expansion**: Add remaining recognition failures + remaining hallucinations
3. **Second expansion**: Add localisation failures (farthest first) + marginal/near-miss FPs
4. **Full library**: All 24 FNs + all 18+ FPs meeting ≥3/5

The post-hoc regression (§8.4.5) — `F1_pass ~ β₀ + Σᵢ βᵢ(exampleᵢ_present)` — will
quantify each example's marginal F1 contribution, allowing evidence-based reranking
after the initial experiments.

---

*This register is a working document. Hard example selection decisions should be
recorded in `decisions-log.md` (Decision 4).*
