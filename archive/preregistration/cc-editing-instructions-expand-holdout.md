# Editing Instructions: Expand Holdout Set to 60 Tiles

**Purpose**: Increase statistical power by expanding holdout from 20 to 60 tiles
**Rationale**: With 28 mounds, MDE ≈ 0.12-0.15; with ~84 mounds, MDE ≈ 0.07-0.09
**Files to edit**: `preregistration.md`

---

## 1. Tile Selection (New Tiles)

### 1.1 Selection Parameters

Run tile selection with updated parameters:

| Parameter | Original | New |
|-----------|----------|-----|
| Samples per map | 5 | 15 |
| Total holdout | 20 | 60 |
| Random seed | [NEW SEED REQUIRED] | Document new seed |

**Constraints** (same as original):
- Content threshold: ≤75% background
- Spatial separation: Not adjacent to training tiles
- Not adjacent to existing holdout tiles
- Stratification by density maintained

### 1.2 Selection Procedure

1. Use same selection script as original (Section 8.6)
2. Exclude all 20 training tiles from eligible pool
3. Exclude all 20 existing holdout tiles from eligible pool
4. Select 10 additional tiles per map (to reach 15 total per map)
5. Maintain density stratification as closely as possible
6. Document new random seed

**Note**: If exact stratification (equal empty/sparse/dense per map) is not achievable with 15 tiles per map, document the actual distribution achieved.

---

## 2. Edit Section 2.1 (Map Tile Corpus)

Find:
```markdown
| Dataset | Tiles | Purpose | Status |
| :---- | :---- | :---- | :---- |
| Development set ('training tiles') | 20 | Prompt engineering, iteration | Used \- contaminated |
| Exploratory test set ('holdout tiles') | 20 | Generalization checks (no feedback to prompts) | Used for evaluation only |
| Reserve set | 321 | Confirmatory testing | **Untouched** |
```

Replace with:
```markdown
| Dataset | Tiles | Purpose | Status |
| :---- | :---- | :---- | :---- |
| Development set ('training tiles') | 20 | Prompt engineering, iteration | Used — contaminated |
| Exploratory test set ('holdout tiles') | 60 | Generalization checks (no feedback to prompts) | Used for evaluation only |
| Reserve set | 281 | Confirmatory testing | **Untouched** |
```

Also update the total line if present:
```markdown
**Total**: 361 tiles from 4 annotated Soviet topographic map sheets.
```

---

## 3. Edit Section 2.2 (Selection Methodology)

Find:
```markdown
| Parameter | Value |
| :--- | :--- |
| Selection date | 2025-12-23 |
| Random seed | 1766464625 |
| Samples per map | 5 |
```

Replace with:
```markdown
| Parameter | Training | Holdout |
| :--- | :--- | :--- |
| Selection date | 2025-12-23 | [NEW DATE] |
| Random seed | 1766464625 | [NEW SEED] |
| Samples per map | 5 | 15 |
```

Or add a note explaining the expanded holdout selection.

---

## 4. Edit Section 2.4 (Holdout Tiles)

### 4.1 Update header

Find:
```markdown
### 2.4 Holdout Tiles (n=20)

Tiles reserved for final evaluation. Spatially separated from training tiles.
```

Replace with:
```markdown
### 2.4 Holdout Tiles (n=60)

Tiles reserved for final evaluation. Spatially separated from training tiles.
```

### 4.2 Expand tile tables

Each map section needs to expand from 5 to 15 tiles. 

**Template for each map:**

```markdown
#### K-35-052-4_32635 (15 tiles)

| Tile ID | Mound Count | Density |
| :---- | :---- | :---- |
| K-35-052-4_32635_x0_y2688.png | 4 | dense |
| K-35-052-4_32635_x1792_y1344.png | 2 | sparse |
| K-35-052-4_32635_x3584_y0.png | 0 | empty |
| K-35-052-4_32635_x3584_y2240.png | 1 | sparse |
| K-35-052-4_32635_x448_y896.png | 0 | empty |
| [10 NEW TILES FROM SELECTION] | | |
```

Repeat for all 4 maps:
- K-35-052-4_32635 (15 tiles)
- K-35-053-3_Elenovo (15 tiles)
- K-35-062-2_Rakovski (15 tiles)
- K-35-078-1_Lesovo (15 tiles)

### 4.3 Update summary

Find:
```markdown
**Holdout set summary**: 20 tiles, 28 mounds total
```

Replace with:
```markdown
**Holdout set summary**: 60 tiles, [X] mounds total
```

Where [X] is the actual mound count from the selected tiles.

---

## 5. Edit Section 2.5 (Density Distribution)

Find:
```markdown
| Density | Training | Holdout |
| :---- | :---- | :---- |
| Empty (0 mounds) | 8 | 8 |
| Sparse (1-2 mounds) | 7 | 7 |
| Dense (3+ mounds) | 5 | 5 |
```

Replace with actual counts from expanded selection:
```markdown
| Density | Training | Holdout |
| :---- | :---- | :---- |
| Empty (0 mounds) | 8 | [NEW COUNT] |
| Sparse (1-2 mounds) | 7 | [NEW COUNT] |
| Dense (3+ mounds) | 5 | [NEW COUNT] |
```

**Target stratification** (if achievable): ~24 empty, ~21 sparse, ~15 dense
(Proportional to original 8:7:5 ratio, scaled to 60 tiles)

---

## 6. Edit Section 3.3 (Interpretation Guidelines)

Find:
```markdown
### 3.3 Interpretation Guidelines

* **Statistically significant (FDR-corrected p < 0.05)**: Technique shows promise; advance to Stage 2 validation
* **Nominally significant (uncorrected p < 0.05, FDR-corrected p ≥ 0.05)**: Suggestive evidence; consider for Stage 2 with lower priority
* **Non-significant (uncorrected p ≥ 0.05)**: No evidence of benefit; do not advance unless strong theoretical rationale
```

Replace with:
```markdown
### 3.3 Interpretation Guidelines

* **Statistically significant (FDR-corrected p < 0.05)**: Technique shows promise; advance to Stage 2 validation
* **Nominally significant (uncorrected p < 0.05, FDR-corrected p ≥ 0.05)**: Suggestive evidence; consider for Stage 2 with lower priority
* **Non-significant (uncorrected p ≥ 0.05)**: No statistical evidence of benefit. However, techniques showing consistent directional improvement (e.g., positive point estimate in ≥75% of conditions where tested) may be flagged for Stage 2 investigation with lowest priority if theoretically motivated. This guards against discarding genuinely useful techniques due to sampling noise.
```

---

## 7. Edit Section 3.6 (Power Considerations)

Find:
```markdown
### 3.6 Power Considerations

With 20 holdout tiles containing 28 mound symbols, statistical power is limited. Approximate detectable effect sizes (80% power, α = 0.05, two-tailed):

- **Symbol-level F1**: Minimum detectable difference ≈ 0.12-0.15
- **Tile-level MCC**: Minimum detectable difference ≈ 0.30

These estimates are approximate and assume moderate correlation between tiles. The two-stage trial framework addresses power limitations by treating Stage 1 as a screening study; techniques showing directional improvement will be validated with larger samples in Stage 2.

**Implication**: Small but practically meaningful effects (e.g., F1 +0.05) may not reach statistical significance in Stage 1. Such effects will be flagged for Stage 2 investigation if directionally consistent.
```

Replace with:
```markdown
### 3.6 Power Considerations

With 60 holdout tiles containing approximately [X] mound symbols, statistical power is adequate for detecting moderate effects. Approximate detectable effect sizes (80% power, α = 0.05, two-tailed):

- **Symbol-level F1**: Minimum detectable difference ≈ 0.07-0.09
- **Tile-level MCC**: Minimum detectable difference ≈ 0.20

These estimates are approximate and assume moderate correlation between tiles. The two-stage trial framework treats Stage 1 as a screening study; techniques showing promise will be validated with additional samples in Stage 2.

**Implication**: Effects of F1 ≈ 0.08 or larger should be detectable with reasonable power. Smaller effects (e.g., F1 +0.05) may still fall below the detection threshold and will be flagged for Stage 2 investigation if directionally consistent.
```

---

## 8. Edit Section 10 (Stage 2 Planning)

Find:
```markdown
- **Larger sample**: 80-160 additional tiles from the 321-tile reserve set
```

Replace with:
```markdown
- **Larger sample**: 80-160 additional tiles from the 281-tile reserve set
```

---

## 9. Global Search and Replace

Search entire document for these patterns and update as needed:

| Search for | Replace with | Notes |
|------------|--------------|-------|
| `20 holdout tiles` | `60 holdout tiles` | Context-dependent |
| `28 mound symbols` | `[X] mound symbols` | Use actual count |
| `28 mounds` | `[X] mounds` | Use actual count |
| `321-tile reserve` | `281-tile reserve` | |
| `321 tiles` (in reserve context) | `281 tiles` | Context-dependent |

---

## 10. Verification Checklist

After edits, verify:

- [ ] Section 2.1 table shows 60 holdout, 281 reserve
- [ ] Section 2.2 documents new selection parameters/seed
- [ ] Section 2.4 header says (n=60)
- [ ] Section 2.4 contains 15 tiles per map (60 total)
- [ ] Section 2.4 summary has correct mound count
- [ ] Section 2.5 density table sums to 60 holdout
- [ ] Section 3.3 includes directional consistency criterion
- [ ] Section 3.6 power estimates updated (~0.07-0.09 F1, ~0.20 MCC)
- [ ] Section 10 references 281-tile reserve
- [ ] No stale references to "20 holdout" or "28 mounds" remain
- [ ] New random seed documented

---

## 11. Note to Implementer

**The actual tile selection must be performed** before the preregistration can be updated with specific tile IDs. Options:

1. Run selection script now and provide tile list to CC
2. Have CC run selection script if access to tile data is available
3. User performs selection and provides results

The preregistration cannot be finalized until the 40 new holdout tile IDs and their mound counts are known.

---

*Instructions prepared 2026-01-03*
