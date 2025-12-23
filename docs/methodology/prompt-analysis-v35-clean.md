# Prompt Analysis: v3.5_clean and Recommendations for H1/H2 Testing

**Document created**: 2024-12-23  
**Purpose**: Analysis of current "clean" prompt and specifications for true image-only variant  
**For**: Claude Code implementation

**Updated**: Filenames aligned with new project structure:
- `detect_image-only` — image-only baseline
- `detect_text-image` — image + text baseline  
- `detect_text-only` — text-only
- `propose_image-only` / `verify_image-only` — two-stage (documenting failure)

---

## Current Prompt Analysis (detect_image-only / v3.5_clean)

### Text Elements Present

The current "clean" prompt contains more text than ideal for a true image-only condition:

**1. System Instruction (~100 words)**
```markdown
You are an expert landscape archaeologist analyzing Soviet Topographic Maps.
Your goal is to find specific symbols in the map tile that **visually match** the provided Reference Examples.

Task: Scan the Target Image and identify all instances that look like the Reference Symbols.
When uncertain whether a feature is a mound or noise, **err on the side of detection**.

Output Format: Return a JSON object with detections using normalized coordinates (0-1000).
```

**2. Example Labels (16 total)**

| Example | Current Label |
|---------|---------------|
| burial_mound.png | "Positive Example: Burial Mound (Standard)" |
| ref_variant_2.png | "Positive Example: Burial Mound (Simple/Degraded)" |
| settlement_mound.png | "Positive Example: Settlement Mound (Irregular)" |
| triangulation_mound.png | "Positive Example: Triangulation Point on Mound" |
| benchmark_mound.png | "Positive Example: Benchmark on Mound" |
| ref_variant_1.png | "Positive Example: Benchmark on Mound (Variant)" |
| ref_pos_green.png | "Positive Example: Mound on Vegetation (Green Background)" |
| ref_pos_intersected.png | "Positive Example: Intersected Mound (Obscured by Lines)" |
| ref_pos_compound.png | "Positive Example: Compound Symbol" |
| ref_negative_1.png | "Negative Example: Noise (Ignore)" |
| neg_sparse.png | "Negative Example: Sparse Area (No Mounds)" |
| neg_topo.png | "Negative Example: Topography / River (No Mounds)" |
| neg_urban.png | "Negative Example: Urban Area (No Mounds)" |
| ref_neg_embankment_2.png | "Negative Example: Embankment (Ignore)" |
| ref_neg_benchmark.png | "Negative Example: Benchmark Symbol (Ignore)" |
| ref_neg_triangulation.png | "Negative Example: Triangulation Point (Ignore)" |

### Semantic Work Done by Labels

The current labels convey significant information beyond classification:
- **Positive vs Negative**: Classification signal
- **Subtype**: burial_mound, settlement_mound, triangulation_mound, benchmark_mound
- **Variant descriptions**: Standard, Simple/Degraded, Irregular, Variant
- **Context**: Green Background, Obscured by Lines, Compound
- **Action instruction**: "Ignore"
- **Area type**: Sparse Area, Urban Area, Topography/River

For H1 (text modality null effect) to be a valid test, the image-only condition should strip this semantic content.

---

## Example Composition Analysis

| Type | Count | Examples |
|------|-------|----------|
| Positive (symbol variants) | 9 | burial, settlement, triangulation on mound, benchmark on mound, etc. |
| Negative (empty area) | 4 | sparse, topo/river, urban, noise |
| Negative (confusable symbol) | 3 | embankment, benchmark alone, triangulation alone |

### Implication for H7 (Hard Negatives)

The current prompt **already includes hard negative examples** (symbol-specific negatives):
- `ref_neg_embankment_2.png`
- `ref_neg_benchmark.png`
- `ref_neg_triangulation.png`

To properly test H7 (hard negatives improve precision), you need:
- **Condition A**: Prompt WITHOUT these three symbol negatives (only area negatives)
- **Condition B**: Prompt WITH these three symbol negatives (current v3.5_clean)

If v3.5_clean is the baseline for all tests, H7 cannot be tested as designed.

---

## Temperature Setting

Current: `"temperature": 0.3`

**Issue**: Google's Gemini documentation recommends temperature 1.0 for complex tasks, warning that lower temperatures can cause "looping or degraded performance."

**Recommendation**: 
- Either use 1.0 consistently across all conditions (per vendor guidance)
- Or document 0.3 as a deliberate choice with rationale
- Temperature variation could be tested as H9 (exploratory)

---

## Recommended Prompt Variants

### Naming Convention (Updated)

Based on project restructuring:
- **Baseline prompts** (no hard negatives): `detect_image-only`, `detect_text-image`, `detect_text-only`
- **With hard negatives**: `detect_image-only-hardneg`, `detect_text-image-hardneg`
- **Two-stage** (documenting failure): `propose_image-only`, `verify_image-only`
- **Elaborate text** (for H2): `detect_text-image-elaborate`

### Hard Negatives Strategy Clarification

The current v3.5_clean (to become `detect_image-only`) **already includes hard negative examples**. For clean hypothesis testing:

1. **Create baseline WITHOUT hard negatives** — remove `ref_neg_embankment_2.png`, `ref_neg_benchmark.png`, `ref_neg_triangulation.png`
2. **Rename current prompt WITH hard negatives** — e.g., `detect_image-only-hardneg`
3. **H7 tests**: baseline vs hardneg variant

This means the "baseline" is actually simpler than what currently exists.

---

### Variant 1: True Image-Only Baseline (for H1)

**Filename**: `detect_image-only.json`

**Principle**: Minimal text, no hard negatives, labels indicate classification only.

```json
{
    "version": "detect_image-only",
    "description": "Minimal text baseline for H1 testing. No hard negatives. Labels indicate classification only.",
    "model": "gemini-3-flash-preview",
    "instruction_file": "detect_image-only.md",
    "temperature": 1.0,
    "examples": [
        {"path": "burial_mound.png", "label": "Positive"},
        {"path": "ref_variant_2.png", "label": "Positive"},
        {"path": "settlement_mound.png", "label": "Positive"},
        {"path": "triangulation_mound.png", "label": "Positive"},
        {"path": "benchmark_mound.png", "label": "Positive"},
        {"path": "ref_variant_1.png", "label": "Positive"},
        {"path": "ref_pos_green.png", "label": "Positive"},
        {"path": "ref_pos_intersected.png", "label": "Positive"},
        {"path": "ref_pos_compound.png", "label": "Positive"},
        {"path": "ref_negative_1.png", "label": "Negative"},
        {"path": "neg_sparse.png", "label": "Negative"},
        {"path": "neg_topo.png", "label": "Negative"},
        {"path": "neg_urban.png", "label": "Negative"}
    ]
}
```

**Note**: Hard negative symbol examples (`ref_neg_embankment_2.png`, `ref_neg_benchmark.png`, `ref_neg_triangulation.png`) are **removed** from baseline.

**Instruction file** (`detect_image-only.md`):
```markdown
Scan the Target Image. Mark all symbols that look like the Positive examples.

Return JSON with normalized coordinates (0-1000):
{"detections": [{"box_2d": [ymin, xmin, ymax, xmax], "label": "mound"}]}
```

---

### Variant 2: Image-Only with Hard Negatives (for H7)

**Filename**: `detect_image-only-hardneg.json`

Same as Variant 1, but ADD hard negative examples:

```json
{
    "version": "detect_image-only-hardneg",
    "description": "Image-only with hard negative examples for H7 testing.",
    "examples": [
        // ... all positives from Variant 1 ...
        // ... area negatives from Variant 1 ...
        {"path": "ref_neg_embankment_2.png", "label": "Negative: Not a mound (embankment)"},
        {"path": "ref_neg_benchmark.png", "label": "Negative: Not a mound (benchmark alone)"},
        {"path": "ref_neg_triangulation.png", "label": "Negative: Not a mound (triangulation alone)"}
    ]
}
```

**H7 Test**: Compare `detect_image-only` vs `detect_image-only-hardneg`

---

### Variant 3: Image + Minimal Text Baseline

**Filename**: `detect_text-image.json`

Your current working prompt with descriptive labels, but **without hard negatives** for baseline.

---

### Variant 4: Image + Minimal Text with Hard Negatives

**Filename**: `detect_text-image-hardneg.json`

Current working prompt **with** hard negatives (this is essentially what you had before).

---

### Variant 5: Image + Elaborate Text (for H2)

**Filename**: `detect_text-image-elaborate.json`

Take `detect_text-image` baseline and ADD detailed criteria to instruction file:

**Instruction file** (`detect_text-image-elaborate.md`):

```markdown
# Soviet Map Mound Detection (Elaborate)

**System Instruction:**

You are an expert landscape archaeologist analyzing Soviet Topographic Maps.
Your goal is to find specific symbols in the map tile that **visually match** the provided Reference Examples.

## Detection Criteria

Burial mound symbols on Soviet 1:50,000 topographic maps appear as:
- Small circular or oval shapes, typically 2-4mm diameter at map scale
- Often with radiating hachure lines indicating elevated terrain
- May appear individually or in clusters on elevated terrain
- Settlement mounds are larger and more irregular in outline
- Triangulation points ON mounds show a triangle with the mound symbol
- Benchmarks ON mounds show the benchmark symbol with the mound symbol

## Exclusion Criteria

Do NOT mark the following as mounds:
- Spot heights: small dots accompanied by elevation numbers (e.g., "185")
- Triangulation points ALONE: triangles with central dots, no mound symbol
- Benchmark symbols ALONE: circles with crosshairs, no mound symbol
- Embankments: linear raised features, often along roads or railways
- Quarry symbols: similar circular shapes but with distinct internal markings
- Urban features: buildings, structures within settlement areas

## Decision Procedure

When uncertain whether a feature is a mound:
1. Check for accompanying text or numbers (suggests spot height, not mound)
2. Look for the characteristic hachure pattern indicating elevation
3. Consider whether the symbol matches ANY of the positive reference examples
4. If the feature has partial similarity to positive examples, INCLUDE it
5. Only exclude if it clearly matches a negative example type

**Task:**
Scan the **Target Image** and identify all instances that look like the Reference Symbols.
When uncertain whether a feature is a mound or noise, **err on the side of detection**.

**Output Format:**
Return a JSON object with detections using normalized coordinates (0-1000).
{
    "detections": [
        {
            "box_2d": [ymin, xmin, ymax, xmax], 
            "label": "mound", 
            "subtype": "burial_mound" | "settlement_mound" | "triangulation_mound" | "benchmark_mound",
            "reasoning": "Visual match to Reference Image. [Briefly describe geometry]"
        }
    ]
}
```

---

## Revised Test Matrix

| Condition | Config File | Labels | Hard Negatives | Instruction | Tests |
|-----------|-------------|--------|----------------|-------------|-------|
| Image-only baseline | detect_image-only | "Positive"/"Negative" | **No** | Minimal | H1, H7 baseline |
| Image-only + hardneg | detect_image-only-hardneg | "Positive"/"Negative" | Yes | Minimal | H7 treatment |
| Image + text baseline | detect_text-image | Descriptive | **No** | Standard | H1 comparison |
| Image + text + hardneg | detect_text-image-hardneg | Descriptive | Yes | Standard | Reference |
| Image + elaborate | detect_text-image-elaborate | Descriptive | No | Detailed | H2 |

---

## Questions Requiring Decision

### 1. Temperature
**Options**:
- A) Use 0.3 consistently (current setting)
- B) Use 1.0 consistently (vendor recommendation)
- C) Document as variable to test in H9

### 2. Subtype Classification in Image-Only
**Options**:
- A) Image-only condition outputs detection only (`"label": "mound"`), no subtype
- B) Image-only condition still requests subtype (model infers from visual similarity)

**Recommendation**: Option A. Detection is primary outcome; subtype is secondary.

---

## Files to Create/Modify

| Filename | Purpose | Priority |
|----------|---------|----------|
| `detect_image-only.json` | True image-only baseline (no hard negatives) | High |
| `detect_image-only.md` | Minimal instruction | High |
| `detect_image-only-hardneg.json` | Image-only with hard negatives for H7 | High |
| `detect_text-image.json` | Verify no hard negatives in baseline | Medium |
| `detect_text-image-hardneg.json` | Image+text with hard negatives | Medium |
| `detect_text-image-elaborate.json` | Elaborate text for H2 | High |
| `detect_text-image-elaborate.md` | Detailed instruction | High |

---

*Document version: 1.1*
*Updated: 2024-12-23 — Aligned filenames with project structure; clarified hard negatives baseline strategy*
