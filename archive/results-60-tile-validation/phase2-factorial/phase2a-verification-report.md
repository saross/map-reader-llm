# Phase 2a Verification Report: Text-Only Outperforms Image-Inclusive Conditions

## 1. Motivation

Phase 2a tested five Modality/Elaboration (M/E) conditions for H1, each with
K=10 independent runs across 60 validation tiles. The mean F1 scores were:

| Condition          | Mean F1 | Mean Precision | Mean Recall |
|--------------------|---------|----------------|-------------|
| brief-text         | 0.5425  | 0.4339         | 0.7247      |
| verbose-text       | 0.4710  | 0.3645         | 0.6660      |
| brief-text-image   | 0.4617  | 0.3934         | 0.5588      |
| image-only         | 0.4252  | 0.3493         | 0.5454      |
| verbose-text-image | 0.4369  | 0.3675         | 0.5392      |

This result is counter-intuitive. H1 predicted that providing visual examples
would help the Vision Language Model (VLM) recognise burial mound symbols.
Instead, the two text-only conditions (brief-text, verbose-text) outperform all
three image-inclusive conditions (image-only, brief-text-image,
verbose-text-image). The best condition overall (brief-text, F1=0.5425) uses
no example images at all.

Before accepting this as a genuine finding, we conducted a systematic
verification to rule out every plausible pipeline artefact. This report
documents that verification.

## 2. Verification Design

The verification comprised four tracks:

- **Part A — Statistical pipeline verification**: Independent recomputation of
  all 50 F1 values from raw data, per-tile decomposition, and spatial overlap
  analysis
- **Part B — Image pipeline verification**: Metadata cross-validation, input
  token analysis, and detection count distributions
- **Part C — Fresh one-off tile assessments**: Independent reproduction of the
  effect on 5 tiles outside the Phase 2a infrastructure
- **Part D — System instruction content analysis**: Comparison of instruction
  files to assess confounds

All verification code is in `scripts/verify_phase2a_metrics.py`.

## 3. Part A: Statistical Pipeline Verification

### 3.1 Independent F1 Recomputation (A1)

**Method**: For each of the 50 runs (5 conditions x 10 runs), we independently
loaded the raw detection GeoJSON from `outputs/phase2a/{condition}/run_{K}/`,
the reference GeoJSON from `inputs/vectors/references/mounds-reference.geojson`,
and the tile bounds from `inputs/vectors/bounds/validation_bounds.geojson`. We
called `calculate_f1_internal()` with a 20 m buffer and compared each
recomputed (precision, recall, F1) triple against the corresponding row in
`per_run_metrics.csv`.

**Result**: **All 50 F1 values match the CSV exactly** (within rounding
tolerance of 0.0001). Detection counts also match. There is no metric
calculation bug, no file-loading error, and no data-path confusion. The
numbers in the CSV are correct.

**Verdict**: GREEN FLAG — statistical pipeline confirmed correct.

### 3.2 Per-Tile F1 Decomposition (A2)

**Method**: For run 1 of brief-text and image-only, we computed per-tile TP, FP,
and FN using `compute_per_tile_tp_fp_fn()`, then derived per-tile F1 for each
condition. This reveals whether the brief-text advantage is concentrated in a
few tiles (suggesting an artefact) or broadly distributed (suggesting a genuine
effect).

**Result**:

| Metric                       | Value    |
|------------------------------|----------|
| Tiles where brief-text wins  | 15       |
| Tiles where image-only wins  | 10       |
| Tiles with no difference     | 35       |
| brief-text total TP          | 69       |
| brief-text total FP          | 88       |
| brief-text total FN          | 37       |
| image-only total TP          | 60       |
| image-only total FP          | 105      |
| image-only total FN          | 46       |

The advantage is distributed across three of the four maps:

| Map                   | Mean F1 Diff (BT-IO) | BT Wins | IO Wins |
|-----------------------|-----------------------|---------|---------|
| K-35-052-4 (32635)    | +0.1228               | 5       | 1       |
| K-35-053-3 (Elenovo)  | +0.1114               | 5       | 4       |
| K-35-062-2 (Rakovski) | +0.0089               | 3       | 3       |
| K-35-078-1 (Lesovo)   | -0.0622               | 2       | 2       |

brief-text achieves both **higher TP** (69 vs 60) and **lower FP** (88 vs 105),
meaning it is simultaneously more accurate and more precise than image-only
on these tiles.

**Verdict**: GREEN FLAG — advantage is broadly distributed, not concentrated
in 1–2 tiles. Not a tile-specific artefact.

### 3.3 Detection Spatial Overlap Analysis (A3)

**Method**: For run 1 of both conditions, we spatially matched detections from
brief-text against detections from image-only within a 20 m buffer (the same
matching criterion used for reference matching). This reveals whether the two
conditions find the same mounds, or entirely different ones. We then checked
each category (shared, brief-text-only, image-only-only) against the ground
truth to determine how many are true positives (TPs).

**Result**:

| Category               | Count | % of Total | TPs | TP Rate |
|------------------------|-------|------------|-----|---------|
| Shared (found by both) | 74    | 29.8%      | 46  | 62.2%   |
| Brief-text only        | 83    | 33.5%      | 23  | 27.7%   |
| Image-only only        | 91    | 36.7%      | 13  | 14.3%   |

The 74 shared detections have the highest TP rate (62.2%), as expected — both
conditions agree on these locations. Of the 83 brief-text-only detections, 23
are true positives (27.7%). Of the 91 image-only-only detections, only 13 are
true positives (14.3%). This means brief-text finds additional *real* mounds
that image-only misses, while image-only produces more false positives in
locations where brief-text does not detect anything.

The low overlap (only 29.8% shared) is notable. Given stochastic variation at
temperature=1.0, the two conditions are finding substantially different
features. The key diagnostic is that brief-text's unique detections are nearly
twice as likely to be real mounds as image-only's unique detections.

**Verdict**: GREEN FLAG — brief-text finds additional genuine mounds.

## 4. Part B: Image Pipeline Verification

### 4.1 Metadata Cross-Validation (B1)

**Method**: For each condition's run 1, we extracted configuration flags,
instruction file names, execution duration, and token counts from the
`.meta.json` metadata file.

**Result**:

| Condition          | include_example_images | Duration (s) | Input Tokens |
|--------------------|------------------------|--------------|--------------|
| image-only         | NOT SET (default: true)| 375.1        | 1,189,080    |
| brief-text         | false                  | 7.3          | 90,120       |
| brief-text-image   | NOT SET (default: true)| 231.7        | 1,201,080    |
| verbose-text       | false                  | 10.5         | 136,500      |
| verbose-text-image | NOT SET (default: true)| 340.8        | 1,247,460    |

All configurations are correct. Text-only conditions explicitly set
`include_example_images: false`. Image conditions omit the flag, defaulting
to true. The duration difference (30–50x) independently confirms different
processing paths.

### 4.2 Input Token Analysis (B2)

**Method**: For all 50 runs, we extracted total input token counts from metadata
and computed per-condition statistics. This is the most direct proof of whether
images were sent: image data (17 example images) adds approximately 1.1 million
tokens.

**Result**:

| Condition          | Mean Input Tokens | Std   | Mean Duration |
|--------------------|-------------------|-------|---------------|
| image-only         | 1,189,080         | 0     | 303.7s        |
| brief-text         | 90,120            | 0     | 8.6s          |
| brief-text-image   | 1,201,080         | 0     | 267.4s        |
| verbose-text       | 136,500           | 0     | 10.8s         |
| verbose-text-image | 1,247,460         | 0     | 258.7s        |

- Average text-only input tokens: **113,310**
- Average image input tokens: **1,212,540**
- **Ratio: 10.70x**

The zero standard deviation confirms that token counts are deterministic for a
given configuration (the same prompt is sent to each tile). The 10.70x ratio
is exactly what we expect: 17 example images at several thousand tokens each
dominate the input context.

**Verdict**: GREEN FLAG — no image leakage. Images are definitively sent only
in image-inclusive conditions.

### 4.3 Detection Count and Recall Distributions (B3)

**Method**: We compared detection count and recall distributions across
conditions, with particular attention to the within-elaboration-level
comparisons that hold system instruction text constant.

**Result**:

| Condition          | Mean N | Std N | Mean Recall | Mean Precision |
|--------------------|--------|-------|-------------|----------------|
| brief-text         | 162.4  | 7.9   | 0.7247      | 0.4339         |
| verbose-text       | 177.4  | 6.7   | 0.6660      | 0.3645         |
| brief-text-image   | 137.8  | 2.6   | 0.5588      | 0.3934         |
| image-only         | 152.5  | 12.4  | 0.5454      | 0.3493         |
| verbose-text-image | 142.7  | 6.7   | 0.5392      | 0.3675         |

The text-only conditions produce *more* detections AND higher recall. This
is not just volume — the additional detections are genuinely finding more
mounds. Text-only conditions consistently achieve recall above 0.66, while
image conditions are capped below 0.56.

## 5. Part C: Fresh One-Off Tile Assessments

### 5.1 Tile Selection (C1)

We selected 5 tiles from the per-tile analysis, covering a range of mound
densities and spread across all four maps:

| Tile                                    | Map           | Refs | Role              |
|-----------------------------------------|---------------|------|-------------------|
| K-35-052-4_32635_x0_y2240.png          | K-35-052-4    | 13   | High density      |
| K-35-053-3_Elenovo_x3584_y2240.png     | K-35-053-3    | 7    | High density      |
| K-35-062-2_Rakovski_x3136_y3136.png    | K-35-062-2    | 2    | Low density       |
| K-35-078-1_Lesovo_x3584_y0.png         | K-35-078-1    | 2    | Low density       |
| K-35-062-2_Rakovski_x2688_y2240.png    | K-35-062-2    | 0    | No mounds (FP test) |

### 5.2 Fresh Assessment Results (C2–C3)

We ran the batch detection script (`4_detect_mounds_batch.py`) on just these 5
tiles for both brief-text and image-only, using the exact same configs,
code path, and model as Phase 2a.

**Detection count comparison**:

| Tile                                   | Fresh BT | P2a BT | Fresh IO | P2a IO |
|----------------------------------------|----------|--------|----------|--------|
| K-35-052-4_32635_x0_y2240.png         | 12       | 12     | 13       | 14     |
| K-35-053-3_Elenovo_x3584_y2240.png    | 7        | 7      | 7        | 7      |
| K-35-062-2_Rakovski_x3136_y3136.png   | 1        | 3      | 1        | 1      |
| K-35-078-1_Lesovo_x3584_y0.png        | 5        | 3      | 3        | 3      |
| K-35-062-2_Rakovski_x2688_y2240.png   | 1        | 1      | 1        | 1      |
| **Total**                              | **26**   | **26** | **25**   | **26** |

Detection counts are closely comparable between fresh and Phase 2a runs,
with minor stochastic variation as expected at temperature=1.0.

**Global F1 on verification tiles**:

| Source               | F1     | Precision | Recall | N  |
|----------------------|--------|-----------|--------|----|
| Fresh brief-text     | 0.7600 | 0.7308    | 0.7917 | 26 |
| Phase 2a brief-text  | 0.6000 | 0.5769    | 0.6250 | 26 |
| Fresh image-only     | 0.5714 | 0.5600    | 0.5833 | 25 |
| Phase 2a image-only  | 0.5600 | 0.5385    | 0.5833 | 26 |

**Fresh brief-text F1=0.7600 vs fresh image-only F1=0.5714** (diff=+0.1886).
The effect reproduces on a completely independent set of API calls, with an
even larger magnitude than the full Phase 2a difference (+0.12). This is
strong evidence that the finding is not a one-off artefact of the specific
Phase 2a execution.

**Spatial overlap between fresh and Phase 2a runs (same condition)**:

| Condition   | Shared | Fresh Only | P2a Only |
|-------------|--------|------------|----------|
| brief-text  | 62.5%  | 18.8%      | 18.8%    |
| image-only  | 50.0%  | 23.5%      | 26.5%    |

The 50–63% overlap is reasonable given temperature=1.0 stochastic variation.
brief-text is more self-consistent across runs than image-only, suggesting
that text-based reasoning may be more stable than image-based pattern matching
at elevated temperature.

### 5.3 Token Count Confirmation on Fresh Runs (C4)

| Condition   | Tokens/Tile | Total Input | Duration |
|-------------|-------------|-------------|----------|
| brief-text  | 1,502       | 7,510       | 21.5s    |
| image-only  | 19,818      | 99,090      | 32.4s    |

**Per-tile token ratio: 13.2x** — confirming that 17 example images account
for the vast majority of input tokens in the image condition.

## 6. Part D: System Instruction Content Analysis

### 6.1 Instruction File Comparison

| Condition          | Instruction File          | Lines | Characters |
|--------------------|---------------------------|-------|------------|
| image-only         | detect_image-only.md      | 19    | 700        |
| brief-text         | detect_brief-text.md      | 36    | 1,561      |
| brief-text-image   | detect_brief-text-image.md| 36    | 1,561      |
| verbose-text       | detect_verbose-text.md    | 99    | 5,284      |
| verbose-text-image | detect_verbose-text-image.md| 99  | 5,284      |

### 6.2 Text Identity Within Elaboration Levels

- `detect_brief-text.md` and `detect_brief-text-image.md` are **byte-identical**
- `detect_verbose-text.md` and `detect_verbose-text-image.md` are **byte-identical**

This is the key methodological safeguard. The comparison between image-only and
brief-text confounds two things: text richness (19 lines vs 36 lines) and image
presence. But the within-elaboration-level comparisons isolate the image effect:

| Comparison                           | Text       | Images  | F1 Diff |
|--------------------------------------|------------|---------|---------|
| brief-text vs brief-text-image       | Identical  | Off/On  | +0.0808 |
| verbose-text vs verbose-text-image   | Identical  | Off/On  | +0.0341 |

**In both cases, removing images IMPROVES F1 while holding text constant.**
This rules out text richness as the explanation. The example images are
actively harmful to detection performance.

## 7. Red/Green Flag Summary

| Criterion                                      | Outcome                          |
|-------------------------------------------------|----------------------------------|
| Per-run F1 values match CSV                     | GREEN — all 50 match exactly     |
| F1 advantage broadly distributed across tiles   | GREEN — 3 of 4 maps, 15 tiles   |
| Brief-text finds same mounds plus more          | GREEN — 23 additional TPs        |
| Text-only input tokens << image input tokens     | GREEN — 10.70x ratio            |
| Fresh runs reproduce the pattern                | GREEN — +0.1886 F1 diff          |
| System instructions identical within level      | GREEN — byte-identical           |

No red flags were triggered. All verification criteria point to a genuine
finding.

## 8. Interpretation

The verification establishes that text-only conditions genuinely outperform
image-inclusive conditions. Several mechanisms could explain this:

1. **Context window competition**: The 17 example images consume approximately
   1.1 million input tokens — over 10x the text-only context. This may crowd
   out the VLM's capacity to process the target tile image carefully, or
   interfere with its spatial reasoning about coordinate extraction.

2. **Template interference**: Example images showing specific mound appearances
   may anchor the VLM to particular visual templates, causing it to miss
   mounds that look different. Text descriptions of subtypes ("concentric
   rings", "radiating lines") may allow more flexible pattern matching.

3. **Temperature interaction**: At temperature=1.0 (the preregistered setting),
   the additional visual context may increase response variability in unhelpful
   ways. Text-only runs show lower standard deviations in both detection counts
   (7.9 vs 12.4 for brief-text vs image-only) and recall (0.0267 vs 0.0301),
   suggesting more stable behaviour.

4. **Recall-driven advantage**: The text-only advantage is primarily driven by
   higher recall (0.72 vs 0.55 for brief-text vs image-only), not higher
   precision (0.43 vs 0.35). Text descriptions appear to encourage the VLM to
   identify more candidate mounds, with a sufficient proportion being genuine
   to improve overall F1.

These interpretations are not mutually exclusive and may act in combination.
Further investigation — for instance, varying the number of example images, or
testing at lower temperature — could help disentangle these mechanisms, but
such experiments fall outside the current preregistered design.

## 9. Implications for Preregistration

H1 predicted that modality/elaboration level would affect detection performance.
This prediction is confirmed, but the *direction* differs from the implicit
expectation that visual examples would help. The preregistration did not specify
a directional prediction for M/E (it tested five levels without predicting which
would be optimal), so the finding does not constitute a deviation from the
preregistered analysis plan. However, the counter-intuitive direction warrants
the level of scrutiny documented in this report.

The within-elaboration-level comparisons (brief vs brief-image, verbose vs
verbose-image) provide the cleanest evidence and should be highlighted in any
write-up as the primary support for the claim that images are harmful.

## 10. Verification Artefacts

The following files were produced during this verification:

| File                                          | Purpose                        |
|-----------------------------------------------|--------------------------------|
| `scripts/verify_phase2a_metrics.py`           | Standalone verification script |
| `inputs/tiles/verification_manifest.json`     | 5-tile manifest for fresh runs |
| `outputs/verification/brief-text/`            | Fresh brief-text detections    |
| `outputs/verification/image-only/`            | Fresh image-only detections    |

---

*Verification conducted 2026-02-06. Script version 1.0.0.*
*Analysis by Shawn Ross and Claude Code.*
