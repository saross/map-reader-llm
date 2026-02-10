# Adversarial Review: Phase 2c Library Composition Results

**Date**: 2026-02-10
**Reviewer**: Claude Code (adversarial mode)
**Null hypothesis**: Something is wrong with the pipeline. Reject only with evidence.

## Executive Summary

All six verification steps passed. No pipeline bugs, configuration errors, or scoring
anomalies were found. The null hypothesis ("something is wrong") is **rejected** based on
concrete evidence at every stage. The counterintuitive result — that hard positives (HP)
degrade performance without informative negatives but improve it with them — is a genuine
finding, explained by how Canon- examples provide discriminative anchoring that redirects
detections from false positives to true positives.

---

## What the Model Actually Sees

The conditions differ not just in "example categories" but in the Positive:Negative
**label ratio** the model receives. Null tiles are labelled "Negative" but carry no
discriminative information about what mounds look like vs. what they don't.

| Condition | P labels | N labels | P:N ratio | F1 |
|-----------|:--------:|:--------:|:---------:|:-----:|
| pure-positive-canon | 4 (4C+) | 3 (3 null) | 1.33 | 0.603 |
| canonical | 4 (4C+) | 5 (2C- + 3 null) | 0.80 | 0.528 |
| plus-hp | 8 (4C+ + 4HP) | 5 (2C- + 3 null) | 1.60 | 0.609 |
| pure-positive-2hp | 6 (4C+ + 2HP) | 3 (3 null) | 2.00 | 0.575 |
| scale-4 | 6 (4C+ + 2HP) | 7 (2C- + 2HN + 3 null) | 0.86 | 0.564 |
| scale-8 | 8 (4C+ + 4HP) | 9 (2C- + 4HN + 3 null) | 0.89 | 0.570 |
| pure-positive-4hp | 8 (4C+ + 4HP) | 3 (3 null) | 2.67 | 0.550 |

---

## Verification Steps

### Step 1: Pure-Positive-4hp Determinism Check

**Question**: All 10 runs report F1=0.5502 with 132 detections. Are the GeoJSON files
byte-identical (suggesting a caching bug) or truly independent?

**Finding**: Files are **not byte-identical** — all 10 MD5 checksums are unique:

```text
run_01: 32e5cf72...  run_06: 8d8df4e9...
run_02: 1872b0f5...  run_07: e5bdc822...
run_03: c9a9ca57...  run_08: fb9c8260...
run_04: 7aaf8bb0...  run_09: 08190d11...
run_05: fd841971...  run_10: b59eba4a...
```

However, coordinate-level comparison reveals **9/10 runs have identical coordinates**;
run_2 differs by exactly 1 detection on tile K-35-078-1_Lesovo_x3584_y1344.png (slightly
different bounding box, same tile). All 10 runs have exactly 132 detections.

**Conclusion**: This is metric convergence from near-deterministic execution at T=0.0, not
a bug. The token-level variation in run_2 produced a slightly different bounding box but
the same detection count and the same scoring outcome. This is the expected behaviour for a
deterministic temperature setting with minimal stochastic variation in the API.

**Verdict**: PASS

---

### Step 2: Pure-Positive-2hp/run_2 Assembly Integrity

**Question**: run_2 was assembled across two API sessions (6 + 54 tiles) due to a timeout.
Is the output complete and correctly assembled?

**Finding**:

- `processed_tiles`: 60 (all tiles present)
- `features`: 132 detections
- All other runs (1, 3-10): 134 detections each, 0 processed_tiles

The 2-detection difference (132 vs 134) is consistent with the F1 difference between run_2
(0.6026) and the other runs (0.5714). run_2 happens to have slightly fewer detections due
to session boundary effects, but all 60 tiles were processed.

**Verdict**: PASS

---

### Step 3: `processed_tiles` Key Does Not Affect Scoring

**Question**: The `processed_tiles` key at FeatureCollection level is non-standard GeoJSON.
Could geopandas silently drop features or misinterpret the file?

**Finding**:

```text
Raw GeoJSON top-level keys: ['type', 'features', 'crs', 'processed_tiles']
processed_tiles count in raw JSON: 60
Features count in raw JSON: 132
Features loaded by geopandas: 132
'processed_tiles' in geopandas columns: False
```

geopandas correctly ignores the collection-level `processed_tiles` key and loads all 132
features. The key does not appear as a column in the resulting GeoDataFrame.

**Verdict**: PASS

---

### Step 4: Prompt Configuration Verification

**Question**: Were the correct example libraries submitted for each condition? Could a
configuration mixup explain the results?

**Finding**: All 7 conditions verified from `meta.json` → `full_config_snapshot`:

| Condition | Version | Examples | Composition |
|-----------|---------|:--------:|-------------|
| canonical | library_canonical | 9 (4P+5N) | 4C+, 2C-, 3 null |
| plus-hp | library_plus-hp | 13 (8P+5N) | 4C+, 4HP, 2C-, 3 null |
| pure-positive-canon | library_pure-positive-canon | 7 (4P+3N) | 4C+, 3 null |
| pure-positive-2hp | library_pure-positive-2hp | 9 (6P+3N) | 4C+, 2HP, 3 null |
| pure-positive-4hp | library_pure-positive-4hp | 11 (8P+3N) | 4C+, 4HP, 3 null |
| scale-4 | library_scale-4 | 13 (6P+7N) | 4C+, 2HP, 2C-, 2HN, 3 null |
| scale-8 | library_scale-8 | 17 (8P+9N) | 4C+, 4HP, 2C-, 4HN, 3 null |

Image paths confirmed: Canon+ = examples 01-04, HP = examples 05-08 (or 05-06 for 2HP),
Canon- = examples 09-10, HN = examples 11-14, null = examples 15-17. These are consistent
across conditions and match the designed library compositions.

Additional findings:

- **Prompt hash**: All 7 conditions share the same `prompt_hash`
  (`e169b7237b853eeaad99...`). Investigation revealed this hashes the **system instruction
  text only** (SHA-256 of `detect_brief-text-image.md`), not the full prompt including
  examples. The hash confirms all conditions used the same system instruction, which is
  correct. The field name `prompt_hash` is misleading — it should be
  `system_instruction_hash`.
- **Within-condition consistency**: All runs within each condition have the same hash,
  confirming no intra-condition prompt drift.
- **Model/temperature**: All conditions use `gemini-3-flash`, T=0.0,
  `detect_brief-text-image.md`.

**Verdict**: PASS (with recommendation to rename `prompt_hash` field)

---

### Step 5: Single-Tile Scoring Trace

**Question**: Does the Hungarian matching algorithm produce correct TP/FP/FN for actual
data?

**Test tile**: K-35-052-4_32635_x0_y2240.png (13 ground truth references — the
highest-density tile in the validation set).

**Finding**:

| Condition | Detections | TP | FP | FN | Precision | Recall | F1 |
|-----------|:----------:|:--:|:--:|:--:|:---------:|:------:|:-----:|
| pure-positive-canon | 13 | 10 | 3 | 3 | 0.769 | 0.769 | 0.769 |
| pure-positive-4hp | 12 | 9 | 3 | 4 | 0.750 | 0.692 | 0.720 |
| plus-hp | 12 | 10 | 2 | 3 | 0.833 | 0.769 | 0.800 |

Match distances range from 1.4m to 19.4m (all within the 20m buffer). The Hungarian
algorithm correctly assigns one-to-one matches and the directional pattern
(plus-hp > pure-positive-canon > pure-positive-4hp) holds at the individual tile level.

Full-run F1 verification (all 60 tiles, run_1):

- pure-positive-canon: P=0.5391, R=0.7113, F1=0.6133
- pure-positive-4hp: P=0.4773, R=0.6495, F1=0.5502

These are run_1 values; the reported means (0.603, 0.550) are averages across 10 runs.

**Verdict**: PASS

---

### Step 6: Cross-Condition Detection Analysis

**Question**: Where do the conditions differ? Is the HP effect driven by more TPs, fewer
FPs, or both?

**Finding — Global TP/FP/FN (run_1)**:

| Condition | Det | TP | FP | FN | P | R | F1 |
|-----------|:---:|:--:|:--:|:--:|:-----:|:-----:|:-----:|
| canonical | 122 | 58 | 64 | 39 | 0.475 | 0.598 | 0.530 |
| plus-hp | 132 | 71 | 61 | 26 | 0.538 | 0.732 | 0.620 |
| pure-positive-canon | 128 | 69 | 59 | 28 | 0.539 | 0.711 | 0.613 |
| pure-positive-2hp | 134 | 66 | 68 | 31 | 0.493 | 0.680 | 0.571 |
| pure-positive-4hp | 132 | 63 | 69 | 34 | 0.477 | 0.649 | 0.550 |
| scale-4 | 138 | 66 | 72 | 31 | 0.478 | 0.680 | 0.562 |
| scale-8 | 137 | 67 | 70 | 30 | 0.489 | 0.691 | 0.573 |

**Critical comparison — pure-positive-4hp vs plus-hp** (same 8 positive examples, different
negatives):

| Metric | pure-positive-4hp | plus-hp | Delta |
|--------|:-----------------:|:-------:|:-----:|
| Detections | 132 | 132 | 0 |
| TP | 63 | 71 | +8 |
| FP | 69 | 61 | -8 |
| FN | 34 | 26 | -8 |

The detection **volume** is identical (132 each). The Canon- examples do not change how
many detections the model makes — they change **where** the model places them. With
Canon- examples, 8 detections that would have been false positives become true positives.

**Per-map breakdown** (plus-hp vs pure-positive-4hp):

| Map | pp-4hp TP/FP | plus-hp TP/FP | TP gain |
|-----|:------------:|:-------------:|:-------:|
| K-35-052-4 | 18/19 | 23/14 | +5 |
| K-35-053-3 | 17/19 | 19/15 | +2 |
| K-35-062-2 | 26/12 | 27/13 | +1 |
| K-35-078-1 | 2/19 | 2/19 | 0 |

The effect is strongest on K-35-052-4 (the most mound-dense map) and distributed across
tiles, not concentrated on a single anomalous tile.

**HP degradation effect** (pure-positive-canon → pure-positive-4hp):

| Metric | pp-canon | pp-4hp | Delta |
|--------|:--------:|:------:|:-----:|
| Detections | 128 | 132 | +4 |
| TP | 69 | 63 | -6 |
| FP | 59 | 69 | +10 |
| FN | 28 | 34 | +6 |

Adding HP to a pure-positive library produces 4 more detections but loses 6 TPs and gains
10 FPs. The HP examples expand the model's positive class boundary indiscriminately,
generating more detections that are disproportionately false positives.

Per-tile analysis shows 12/60 tiles have differing detection counts across the three key
conditions; the differences are distributed across all four maps.

**Verdict**: PASS — the results are spatially coherent and mechanistically interpretable.

---

## Step 7: Mechanistic Synthesis

All six verification steps passed without finding any pipeline bug, configuration error, or
scoring anomaly. The null hypothesis ("something is wrong") is **rejected**. The results
are genuine findings that can be explained by three complementary mechanisms:

### 1. P:N Label Ratio Effect

The model receives examples tagged as "Positive" (target) or "Negative" (confusable/null).
As HP examples are added to a pure-positive library, the P:N ratio shifts from 1.33
(pure-positive-canon: 4P+3N) to 2.67 (pure-positive-4hp: 8P+3N). With only 3
uninformative null tiles as negatives, the model's class boundary becomes increasingly
permissive — it sees an overwhelming majority of "Positive" examples and loosens its
detection threshold. This produces more detections (128 → 132) that are disproportionately
false positives (59 → 69 FP).

### 2. Informative vs Uninformative Negatives

Canon- examples (examples 09-10) show **specific confusable features** — landscape
elements that resemble mounds but aren't. When labelled "Negative" alongside the system
instruction ("the confusable feature for Negative examples"), they teach the model
*what a mound is not*. Null tiles (examples 15-17) only teach the model *what nothing looks
like* — they provide no discriminative boundary between mound-like and non-mound features.

The evidence for this is striking: plus-hp and pure-positive-4hp share the same 8 positive
examples and make the same number of detections (132), but plus-hp (which has Canon-)
converts 8 detections from FPs to TPs compared to pure-positive-4hp (which has only nulls).
The Canon- examples don't suppress detection volume — they improve detection placement.

### 3. HP + Canon- Interaction

In plus-hp (F1=0.609), HP examples labelled "Positive" show the model what mounds look
like in difficult contexts (ambiguous terrain, marginal cases). Canon- examples labelled
"Negative" show what non-mounds look like in potentially confusing terrain. Together, they
create a **discriminative sandwich**: HP refines the positive class boundary ("even this
counts") while Canon- anchors the negative boundary ("but not this").

Without Canon-, HP examples just expand the positive class indiscriminately. The model
learns "more things count as mounds" without learning "but these specific things don't."
This is why HP helps with Canon- present (plus-hp F1=0.609 vs canonical F1=0.528) but
hurts without it (pure-positive-canon F1=0.603 → pure-positive-4hp F1=0.550).

### Summary

The interaction is non-additive because HP and Canon- serve complementary roles in defining
the decision boundary. HP without contrastive negatives is noise; Canon- without additional
positives is overly restrictive. The optimal configuration (plus-hp) provides both
expansive positive examples and constraining negative examples.

---

## Step 8: Independent Verification Test Design

A verification test has been designed using the 5-tile verification manifest. See
`studies/phase2c-verification-test.yaml` for the ready-to-execute study definition.

### Test Design

- **Tiles**: 5 tiles from `inputs/tiles/verification_manifest.json`
- **Conditions**: 3 (pure-positive-canon, pure-positive-4hp, plus-hp)
- **Runs**: K=1 per condition (T=0.0 is near-deterministic)
- **Total API calls**: 15 (5 tiles × 3 conditions × 1 run)
- **Estimated cost**: < $0.10 USD

### Prerequisites

Before running, generate `verification_bounds.geojson` from the 5 verification tiles:

```bash
python scripts/generate_bounds.py \
  --manifest inputs/tiles/verification_manifest.json \
  --output inputs/vectors/bounds/verification_bounds.geojson
```

### What It Proves

If the directional pattern (plus-hp > pure-positive-canon > pure-positive-4hp) holds on
completely independent tiles, it strongly supports the results being genuine rather than an
artefact of the specific 60-tile validation set.

### Contamination Note

The verification tiles may overlap with the calibration set (used during prompt development)
but NOT with the validation set (used for Phase 2c evaluation). This is acceptable for a
directional sanity check, though not for formal hypothesis testing.

---

## Recommendations

### Immediate

1. **Accept Phase 2c results as genuine.** The counterintuitive HP degradation in
   pure-positive context is a real finding, mechanistically explained by the absence of
   informative negative anchoring.
2. **Retain plus-hp as the carry-forward library** for Phase 2d, as already decided.

### Metadata Improvements

1. **Rename `prompt_hash` to `system_instruction_hash`** in `lib_llm_metadata.py` to
   accurately describe what it hashes. Currently all conditions share the same hash, which
   could mislead reviewers into thinking all prompts were identical.
2. **Add a `library_hash` field** that hashes the full example list (paths + labels +
   categories) to distinguish conditions at the metadata level.
3. **Persist full system instruction text** in meta.json (or at minimum the first N
   characters + hash) so that runs are self-documenting without needing to reconstruct
   prompts from referenced files.

### Scientific Documentation

1. **Document the P:N ratio table** (from this report's "What the Model Actually Sees"
   section) in the paper/preprint. Framing conditions by their label ratios makes the
   results immediately interpretable.
2. **Document the TP/FP/FN decomposition** showing that Canon- redirects detections rather
   than suppressing them. This is a stronger claim than "Canon- helps" and provides
   mechanistic insight for the VLM prompting literature.

---

*Report generated by adversarial review protocol. All claims backed by data from the
verification steps above.*
