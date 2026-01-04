# Preregistration Review: Recommendations and Fixes

**Document reviewed**: `preregistration.md` v3.0 (2026-01-01)
**Review date**: 2026-01-02
**Reviewer**: Claude (Opus 4.5)
**Final update**: 2026-01-02 — All decisions finalized

---

## Overview

This document captures all recommendations from a thorough review of the VLM burial mound detection preregistration, including all decisions made during the review discussion.

**Legend**:
- ✅ Resolved — addressed or accepted
- ⏸️ Deferred — pending external input

---

## 1. Errors and Inconsistencies

### 1.1 ✅ Confirmatory Hypothesis Count Mismatch

**Location**: Section 3.2, line 210

**Current text**: "With 6 confirmatory hypotheses tested on 20 tiles..."

**Fix**: Update to "9 confirmatory hypotheses" and verify FDR correction calculations accommodate this count.

---

### 1.2 ✅ H1 Test Description vs Prediction Mismatch

**Location**: Section 5, H1 (lines 305-316)

**Problem**: The prediction compared image+text vs text-only, but the conditions described image-only vs image+text.

**Resolution**: The comparison is image-only (minimal text) vs text+image. Update to:

```markdown
**Prediction**: Text+image prompts will perform equivalently to image-only prompts.

**Test**: Compare detection performance with:

- Condition A: Image-only (few-shot visual examples with minimal task instruction)
- Condition B: Text+image (few-shot visual examples + detailed text descriptions)
```

---

### 1.3 ✅ Section Reference Error (H10 vs H12)

**Location**: Section 8.1, line 849

**Fix**: Change "H10" to "H12" (cross-model consistency).

---

### 1.4 ✅ H5 Ordering Terminology Mismatch

**Location**: Section 8.4.2, lines 1050-1051

**Fix**: Change "Best-last" to "Canonical-last" throughout:

```markdown
**Ordering (for H5):**

* "Canonical-first" condition: Legend-derived symbols in initial positions, hard examples last
* "Canonical-last" condition: Hard examples in initial positions, legend-derived symbols last
* "Random" condition: Shuffled with documented seed
```

---

### 1.5 ✅ Escaped Characters Throughout

**Fix**: Find and replace `\.` with `.` and similar escaped characters.

---

### 1.6 ✅ Table Formatting Issue

**Location**: Section 2.1, lines 56-61

**Fix**: Ensure "Exploratory test set" table row renders correctly.

---

## 2. Omissions to Address

### 2.1 ✅ Power Analysis

**Add Section 3.6**:

```markdown
### 3.6 Power Considerations

With 20 holdout tiles containing 28 mound symbols, statistical power is limited. 
Approximate detectable effect sizes (80% power, α = 0.05, two-tailed):

- **Symbol-level F1**: Minimum detectable difference ≈ 0.12-0.15
- **Tile-level MCC**: Minimum detectable difference ≈ 0.30

These estimates are approximate and assume moderate correlation between tiles. 
The two-stage trial framework addresses power limitations by treating Stage 1 
as a screening study; techniques showing directional improvement will be 
validated with larger samples in Stage 2.

**Implication**: Small but practically meaningful effects (e.g., F1 +0.05) may 
not reach statistical significance in Stage 1. Such effects will be flagged 
for Stage 2 investigation if directionally consistent.
```

---

### 2.2 ✅ Spatial Tolerance Robustness

**Add to Section 3.5 (Reporting)**:

```markdown
* **Spatial tolerance sensitivity**: All primary results reported at 20m; 
  robustness checks at 10m, 30m, and 50m included in supplementary materials
```

---

### 2.3 ✅ Model Version Documentation

**Add to Section 8.2**:

```markdown
**Version documentation**: Model version identifiers are automatically captured 
from API response metadata and will be reported in supplementary materials.
```

---

### 2.4 ✅ Blinding Statement

**Add new section**:

```markdown
### Blinding

All API calls and metric computations are automated via scripts committed 
before holdout evaluation. The analysis pipeline runs without manual 
intervention between data collection and statistical output, eliminating 
opportunities for analyst degrees of freedom during evaluation.
```

---

### 2.5 ✅ Training Tile Exclusion

**Add to Section 2.1**:

```markdown
**Analysis scope**: Training tiles are excluded from all reported performance 
metrics. F1, precision, recall, and MCC are computed on holdout tiles only.
```

---

### 2.6 ✅ Baseline Library Composition

**Update Section 8.4.2** to clarify initial library before hard example mining:

```markdown
**Hard example selection procedure:**

1. Construct initial library: 4 canonical positives (legend-derived) + 3 null tiles
2. Run initial library on all 20 training tiles with 5-pass consensus voting
3. Identify False Negatives (ground truth mounds missed in ≥3/5 passes)
4. Rank FNs by frequency; select top K as hard positive examples (target K=4)
5. Identify False Positives (detections in ≥3/5 passes with no matching ground truth)
6. Rank FPs by frequency; select top M as hard negative examples (target M=3)
7. If ties occur, select randomly (document seed)
8. Construct augmented library: canonical + hard positives + hard negatives + null
```

---

### 2.7 ✅ Lesovo Terrain Documentation

**Add to Section 2.5 or 2.6**:

```markdown
**Terrain representation**: Lesovo represents mountainous terrain with 
characteristically low mound density, consistent with similar regions near 
the Bulgarian-Turkish border and Stara Planina. Its inclusion ensures the 
pipeline is evaluated on terrain representative of sparse-mound contexts, 
testing both detection in low-density environments and false positive rates 
in unfamiliar terrain types.
```

---

### 2.8 ✅ Hypothesis Numbering

**Fix**: Renumber all exploratory hypotheses with H-prefix (H10-H16). Remove E7 designation.

---

### 2.9 ✅ Exploratory Hypotheses in Implementation Table

**Update Section 8.7.1**: Add H10-H16 to implementation status table.

---

### 2.10 ✅ Administrative Statements

**Add**:

```markdown
## Conflict of Interest

The authors declare no competing interests. This research received no 
external funding from AI model providers.

## Ethics

This study analyses historical map imagery and involves no human participants. 
No ethics approval was required.

## Registration

This preregistration will be submitted to OSF Registries using the 
OSF Preregistration format.
```

---

### 2.11 ⏸️ Data/Code Availability

**Status**: PENDING Bulgarian requirements for mound location data (looting sensitivity).

**Placeholder**:

```markdown
## Data and Code Availability

- **Code**: All analysis scripts will be released via GitHub/OSF upon publication
- **API responses**: Raw API response logs will be archived (with timestamps)
- **Ground truth**: [Pending confirmation of Bulgarian data sharing requirements]
- **Map tiles**: [Pending confirmation of Bulgarian data sharing requirements]
- **Prompts**: All prompt text and configuration files included in repository
```

---

## 3. Hypothesis-Specific Updates

### 3.1 ✅ H3: Testing Approach and Stopping Rule

**Add to Section 5, H3**:

```markdown
**Testing approach**: The two-stage pipeline will be tested using the optimal 
single-stage configuration identified from H1, H5, H7, H9 (modality, ordering, 
hard negatives, temperature). This ensures a fair comparison where any 
performance difference reflects architectural rather than configurational factors.

**Stopping rule**: If two-stage F1 is ≥0.10 lower than single-stage F1 at the 
same configuration, we will conclude the architecture is unsuitable for this 
task and will not pursue further optimization. This threshold accounts for 
the inherent cost (~2× API calls) and complexity overhead of two-stage 
pipelines — marginal performance parity would not justify the additional 
operational burden.

**Scope limitation**: Exhaustive optimization of proposer-verifier configurations 
(e.g., varying proposer/verifier thresholds, prompt variants for each stage) is 
beyond the scope of this study. Such investigation would be warranted only if 
initial testing shows the architecture is competitive (within 0.10 F1 of 
single-stage baseline).

**Applicability to other two-stage approaches**: The same stopping rule 
(F1 ≥0.10 below single-stage baseline) applies to H10 (fine-to-coarse 
validation) and any other multi-stage architecture tested. Two-stage 
approaches must demonstrate near-parity to justify their overhead.
```

---

### 3.2 ✅ H4: Primary vs Exploratory Analysis

**Clarify in Section 5, H4**:

```markdown
**Primary confirmatory test**: Single-pass (N=1) vs optimal voting configuration 
(single comparison). The optimal configuration is determined by maximum F1 across 
the full grid search.

**Exploratory/descriptive analysis**: Full threshold curves (all T for each N) 
reported as descriptive visualizations characterising the precision-recall 
tradeoff. Preliminary testing suggests optimal thresholds cluster around 30-40% 
(e.g., 2-of-5, 4-of-10, 10-of-30).

**Single-configuration rationale**: Voting threshold is determined at the optimal 
base prompt configuration. Preliminary work suggests the ~30-40% optimum is 
consistent across configurations; however, if main factorial results reveal 
substantial precision/recall shifts between conditions, targeted voting 
threshold testing at contrasting configurations may be warranted (see 
Section 8: Extended Coverage).
```

---

### 3.3 ✅ H6: Symmetric Replication

**Update Section 5, H6**:

```markdown
**Replication**: Each condition (A, B, C, D) is run 5 times to provide symmetric 
variance estimates and adequate power for detecting diversity effects. For 
Conditions A and B (fixed images), each run uses a different randomly-sampled 
fixed library (documented seeds). Analysis compares condition means with 
appropriate variance pooling.

**Single-configuration rationale**: Diversity effects are tested at the optimal 
base prompt configuration identified from the main factorial. Generalization 
to other configurations is assumed based on the general mechanism of reducing 
error correlation across passes — this mechanism should operate similarly 
regardless of base configuration.
```

---

### 3.4 ✅ H8: Model Transfer Approach

**Update/add to Section 5, H8**:

```markdown
**Transfer testing approach**: Cross-model testing uses stepwise adjustment 
from Flash-optimal configuration rather than independent optimization. If a 
factor shows different behaviour on Pro (e.g., different optimal ordering), 
that factor is adjusted while holding others constant.

**Scope limitation**: Full per-model optimization is beyond the scope of this 
study unless a model demonstrates substantially superior cost-effectiveness 
(operationalized as: ≥20% higher F1 at comparable cost, OR comparable F1 at 
≤50% cost). Such a finding would warrant model-specific optimization as a 
separate investigation.
```

---

## 4. Factorial Design Decisions

### 4.1 ✅ Core Factorial Coverage

**Decision**: Run full 48-condition factorial (M×O×H×T) plus complete pairwise coverage for elaboration.

**Pairwise coverage matrix** (all 10 pairs of core factors covered):

| Pair | Covered By |
|------|------------|
| M × H, M × O, M × T, H × O, H × T, O × T | Main factorial (48 cond) |
| M × E, E × H | H2 design (8 cond) |
| E × O | Added coverage (6 cond) |
| E × T | Added coverage (8 cond) |

---

### 4.2 ✅ H2 Elaboration Methodology

**Add to Section 8.4.6 or new subsection**:

```markdown
### H2 (Elaboration) Testing Methodology

H2 is tested via a separate focused design rather than integration into the 
main factorial. This approach allows:
- Direct comparison of brief vs elaborate text at matched conditions
- Isolation of elaboration effects from the larger factorial

**Core H2 design** (documented in h2-text-elaboration-comparison.md):
- 2 × 2 × 2: Modality (text-only, text+image) × Elaboration (brief, elaborate) × Hard negatives (without, with)
- 8 conditions at T=1.0, canonical-first ordering

**Pairwise coverage extensions**:
- E × O: 2 × 3 = 6 conditions (elaboration × ordering)
- E × T: 2 × 4 = 8 conditions (elaboration × temperature)

Total H2-related conditions: 8 + 6 + 8 = 22 conditions
```

---

### 4.3 ✅ Extended Coverage (Beyond Baseline)

**Decision**: Add additional interaction tests where mechanisms suggest effects could plausibly differ.

**Add new Section 8.4.7 or extend 8.4.6**:

```markdown
### Extended Interaction Coverage

Beyond the core factorial and H2 pairwise coverage, additional tests are 
conducted for interactions with plausible mechanisms:

#### Tier 1: Diversity × Hard Negatives
| Test | Design | Rationale |
|------|--------|-----------|
| TD × H | 2 × 2 | Does text diversity help more when hard negatives present? |
| ID × H | 2 × 2 | Does image diversity help more when hard negatives present? |

#### Tier 2: Voting/Diversity × Modality
| Test | Design | Rationale |
|------|--------|-----------|
| N × H | Grid × 2 | Does optimal voting threshold change with hard negatives? |
| N × M | Grid × 2 | Does optimal voting threshold differ by modality? |
| TD × M | 2 × 2 | Does text diversity help more with image-only? |
| ID × M | 2 × 2 | Does image diversity help more with image-only? |
| Pro voting grid | Full grid | Validate Flash threshold transfers to Pro |

#### Tier 3: Temperature × Voting, Extended Cross-Model
| Test | Design | Rationale |
|------|--------|-----------|
| N × T | Grid × 4 | Does temperature affect optimal threshold? (variance → voting) |
| Extended Claude/GPT | +conditions | Strengthen generalizability claims |

**Total extended coverage**: ~$35 additional
```

---

### 4.4 ✅ Explicitly Excluded Coverage

**Add new section**:

```markdown
### Coverage Exclusions and Rationale

The following interactions are explicitly NOT tested, with rationale:

#### Weak Mechanism (Tier 4 — Excluded)

| Interaction | Reason for Exclusion |
|-------------|---------------------|
| TD × O (text diversity × ordering) | No plausible mechanism for interaction; diversity operates independently of example ordering |
| TD × T (text diversity × temperature) | Weak mechanism; temperature affects output variance, not prompt diversity effects |
| ID × O (image diversity × ordering) | Same as TD × O |
| ID × T (image diversity × temperature) | Same as TD × T |
| Full TD × ID × H × M (16-cond factorial) | Diminishing returns; core diversity question answered by TD × ID |

#### Gated by Stopping Rules

| Interaction | Reason for Exclusion |
|-------------|---------------------|
| P × {anything} (pipeline × other factors) | Two-stage architecture must first demonstrate competitiveness (-0.10 F1 threshold); exhaustive optimization only if competitive |

#### Deferred to Stage 2

| Interaction | Reason for Exclusion |
|-------------|---------------------|
| Full MT × {everything} (model × all factors) | Goal is transfer validation, not per-model optimization; full optimization only if model shows dramatically superior cost-effectiveness |
| Stage 2 pilot | Stage 1 results needed to inform Stage 2 design; premature piloting would contaminate reserve pool |
```

---

## 5. Stage 2 Planning

### 5.1 ✅ Defer Pilot, Pre-specify Principles

**Decision**: Do not run Stage 2 pilot during Stage 1. Design Stage 2 based on Stage 1 results.

**Add/update Section 10**:

```markdown
## 10. Stage 2 Planning (Contingent on Stage 1 Results)

### Design Principles

Stage 2 will be designed after Stage 1 completion, informed by:

1. **Observed effect sizes** from Stage 1 (for power calculations)
2. **Which factors showed significant effects** (focus Stage 2 testing)
3. **Whether interactions were detected** (determines if factorial needed)

**Reserve pool**: 321 tiles remain untouched for Stage 2 use.

### Configuration Testing Strategy

Stage 2 will test the **top 3-5 configurations** from Stage 1, not just the 
single "winner". This approach:
- Validates that the winning configuration is robustly best (not an artifact of Stage 1 sample)
- Identifies whether runner-up configurations generalize better
- Provides confidence intervals on performance gaps between top configurations

### Contingent Designs

| Stage 1 Outcome | Stage 2 Design |
|-----------------|----------------|
| Clear winner, no interactions | Validate top 3-5 configs on 80-160 reserve tiles |
| Significant interactions | Factorial on key interacting factors, larger N |
| Transfer failures (H8) | Model-specific optimization |
| Marginal effects | Larger sample to resolve ambiguity |

### Rationale for Deferring Pilot

A Stage 2 pilot was considered but deferred because:
1. Stage 1 results are needed to properly design Stage 2 (effect sizes, which factors matter)
2. Using reserve tiles now would partially contaminate them for Stage 2 purposes
3. Stage 1 is explicitly framed as a screening study; the two-stage framework already accounts for this
4. Power calculations for Stage 2 require observed effect sizes from Stage 1

Stage 2 will be separately preregistered based on Stage 1 findings.
```

---

## 6. Cost Summary (INTERNAL — Do Not Include in Preregistration)

**Note**: This section is for internal planning only. Cost estimates should be recorded in a separate internal document, not in the preregistration.

### 6.1 Final Budget

**Total estimated cost: ~$130-135** (well under $250 soft budget)

| Component | Conditions | Calls | Cost |
|-----------|------------|-------|------|
| **Core Confirmatory (Flash)** | | | |
| Main factorial (M×O×H×T) | 48 | 4,800 | $7 |
| H2 core (M×E×H) | 8 | 800 | $1 |
| H2 pairwise (E×O, E×T) | 14 | 1,400 | $2 |
| H3 two-stage | 2 | 400 | $1 |
| H4 voting grid | ~45 | 900 | $1 |
| H6 diversity (4 cond × 5 runs) | 20 | 2,000 | $3 |
| **Flash confirmatory subtotal** | | ~10,300 | **$15** |
| | | | |
| **Transfer & Cross-Model** | | | |
| H8 Pro transfer (corners) | ~14 | 1,400 | $21 |
| **Confirmatory total** | | ~11,700 | **$36** |
| | | | |
| **Exploratory (H10-H16)** | | ~6,400 | $62 |
| | | | |
| **Extended Coverage (Tiers 1-3)** | | | |
| TD×H, ID×H | 8 | 800 | $1 |
| N×H, N×M | 2 grids | 1,800 | $2 |
| TD×M, ID×M | 8 | 800 | $1 |
| Pro voting grid | 1 grid | 900 | $9 |
| N×T | 4 grids | 3,600 | $5 |
| Extended cross-model | +cond | 2,000 | $15 |
| **Extended subtotal** | | ~9,900 | **$33** |
| | | | |
| **GRAND TOTAL** | | ~28,000 | **~$131** |
| **Remaining budget** | | | **~$119** |

### 6.2 Budget Reserves

Remaining ~$119 allocated for:
- Contingency (API failures, retries): ~$20
- H8 escalation if triggers activate: ~$30
- Unexpected findings worth pursuing: ~$30
- Stage 2 seed funding: ~$39

---

## 7. Summary Checklist

### Errors to Fix
- [x] 1.1 Update confirmatory hypothesis count (6 → 9)
- [x] 1.2 Update H1 prediction to match conditions
- [x] 1.3 Fix H10 → H12 reference
- [x] 1.4 Standardize H5 ordering terminology
- [x] 1.5 Clean escaped characters
- [x] 1.6 Check table rendering

### Sections to Add/Update
- [x] 2.1 Add power considerations section (3.6)
- [x] 2.2 Commit spatial tolerance reporting (3.5)
- [x] 2.3 Add model version documentation (8.2)
- [x] 2.4 Add blinding statement
- [x] 2.5 Add training tile exclusion statement (2.1)
- [x] 2.6 Clarify baseline library composition (8.4.2)
- [x] 2.7 Add Lesovo terrain documentation (2.5/2.6)
- [x] 2.8 Renumber hypotheses (all H-prefix)
- [x] 2.9 Add exploratory hypotheses to implementation table (8.7.1)
- [x] 2.10 Add COI, ethics, OSF format statements
- [ ] 2.11 Add data availability statement — ⏸️ PENDING Bulgarian requirements

### Hypothesis Updates
- [x] 3.1 H3: Add testing approach, stopping rule (-0.10 F1), scope limitation
- [x] 3.2 H4: Clarify primary vs exploratory analysis
- [x] 3.3 H6: Update to 5× symmetric replication, add single-config rationale
- [x] 3.4 H8: Add stepwise adjustment approach, cost-effectiveness threshold

### Factorial Design
- [x] 4.1 Document complete pairwise coverage for core factors
- [x] 4.2 Add H2 elaboration methodology section
- [x] 4.3 Add extended coverage section (Tiers 1-3)
- [x] 4.4 Add coverage exclusions and rationale section

### Stage 2 Planning
- [x] 5.1 Update Section 10 with design principles, top 3-5 config strategy, deferral rationale

### Cost Documentation (INTERNAL ONLY — not in preregistration)
- [x] 6.1 Cost summary (~$131 total) — record in internal document
- [x] 6.2 Budget reserves allocation — record in internal document

---

## 8. OSF Preregistration Document Structure

### 8.1 File Organization (4 Files)

The preregistration will be submitted as 4 markdown files:

| File | Contents | Purpose |
|------|----------|---------|
| **preregistration-overview.md** | Sections 1-4: Background, Research Questions, Framework, Data Resources, Statistical Plan, Outcomes | The "what and why" — study rationale and methods |
| **preregistration-hypotheses.md** | Sections 5-7: Confirmatory (H1-H9), Exploratory (H10-H16), Summary Tables | The predictions — what we expect and how we'll test |
| **preregistration-implementation.md** | Sections 8-9: Models, API params, Prompts, Library construction, Voting, Tile selection, Hypothesis mapping, Priority | The technical "how" — specifications for execution |
| **preregistration-coverage.md** | Factorial coverage matrix, extended tests (Tiers 1-3), explicit exclusions with rationale, Stage 2 planning principles | What's tested, what's not, and why |

**5th slot reserved** for pre-holdout specifications (final library, seeds) — to be added to connected OSF Project and linked via Resources tab.

### 8.2 Administrative Sections

The following go in **preregistration-overview.md** (front matter or appendix):

- Conflict of Interest statement
- Ethics statement
- OSF Registration format note
- Data/Code Availability statement (placeholder pending Bulgarian requirements)
- Preregistration Checklist (Section 11)
- Outstanding Questions (Section 12) — should be empty or minimal at submission
- References

### 8.3 Items to EXCLUDE from Preregistration

The following are **operational/internal** and should NOT appear in the preregistration files:

| Item | Reason for Exclusion | Where to Record Instead |
|------|---------------------|------------------------|
| **Cost estimates** ($131 total, per-component breakdown) | Operational planning; not methodological commitment; will change | Internal project document |
| **API pricing tables** | Will be outdated; actual costs documented post-study | Internal project document |
| **Budget allocation** (contingency, reserves) | Internal resource planning | Internal project document |
| **Review recommendations document** | Internal working document; decisions incorporated into preregistration | Project archive |
| **Factor inventory analysis** | Working analysis; key decisions captured in coverage document | Project archive |
| **Tier prioritization rationale** (beyond what's in coverage) | Internal decision-making process | Project archive |

### 8.4 Post-Submission Documents (Connected OSF Project)

These will be uploaded to the connected OSF Project and linked via Resources tab:

| Document | Contents | Timing |
|----------|----------|--------|
| **pre-holdout-specifications.md** | Final few-shot library images (filenames, labels), exact prompt text for all conditions, hard negative images selected, all random seeds, final config files | After library construction, before holdout evaluation |
| **transparent-changes.md** | Any deviations from preregistration, rationale for changes, assessment of impact on interpretation | After study completion |
| **cost-and-operations-report.md** | Actual API costs incurred, any operational issues, model versions used | After study completion |

---

## 9. Final Action Items for Claude Code

### Document Structure

Split the current preregistration.md into 4 files:

1. **preregistration-overview.md**: Sections 1-4 + administrative statements (COI, ethics, data availability, checklist, references)
2. **preregistration-hypotheses.md**: Sections 5-7 (H1-H16 + summary tables)
3. **preregistration-implementation.md**: Sections 8-9 (technical specifications)
4. **preregistration-coverage.md**: Factorial coverage matrix, extended tests, exclusions, Stage 2 principles

### Direct Edits (find and replace)
1. Section 3.2: "6 confirmatory hypotheses" → "9 confirmatory hypotheses"
2. Section 5 H1: Update prediction text
3. Section 8.1: "H10" → "H12"
4. Section 8.4.2: "Best-last" → "Canonical-last"
5. Throughout: Clean escaped characters (`\.` → `.`)
6. Throughout: Renumber E7 → H16

### New Sections to Add
7. Section 3.6: Power considerations
8. Section 3.x: Blinding statement
9. Section 8.4.7 (or extend 8.4.6): Extended interaction coverage
10. Section 8.4.8 (or new): Coverage exclusions and rationale
11. Section 13: COI, ethics, data availability statements

### Sections to Update
12. Section 2.1: Add analysis scope (training tile exclusion)
13. Section 2.5/2.6: Add Lesovo terrain paragraph
14. Section 3.5: Add spatial tolerance sensitivity commitment
15. Section 5 H1: Fix prediction/conditions alignment
16. Section 5 H3: Add testing approach, stopping rule, scope limitation
17. Section 5 H4: Add primary vs exploratory clarification, single-config rationale
18. Section 5 H6: Update replication design, add single-config rationale
19. Section 5 H8: Add stepwise adjustment approach, cost-effectiveness threshold
20. Section 8.2: Add model version documentation statement
21. Section 8.4.2: Clarify initial library composition, fix ordering terminology
22. Section 8.4.6: Add H2 methodology, E×O and E×T coverage
23. Section 8.7.1: Add H10-H16 to implementation status table
24. Section 10: Update with design principles, top 3-5 config strategy, deferral rationale

### Content for preregistration-coverage.md (new file)
25. Pairwise coverage matrix for all core factors
26. Extended coverage (Tiers 1-3) with rationale
27. Explicit exclusions with rationale (weak mechanism, gated, deferred)
28. Stage 2 planning principles
29. Single-configuration testing rationale and caveats

---

*Final version — 2026-01-02*
*All decisions from review discussion incorporated*
