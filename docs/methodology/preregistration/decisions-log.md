# Decisions Log

**Purpose**: Document major methodological decisions and their rationale for the VLM burial mound detection study.

**Last updated**: 2026-04-13

---

## Decision 1: Model Selection — Gemini 3 Flash (Development)

**Date**: December 2025

**Decision**: Use Gemini 3 Flash for development and prompt engineering; Gemini 3 Pro for production validation.

**Alternatives considered**:

- Gemini 3 Pro only
- Gemini 2.0 Flash
- Claude (Anthropic)

**Rationale**:

1. **Rate limits**: Gemini 3 Pro has severe rate limits (~250 RPD on Tier 1 plan) causing 8+ minute delays per tile. Flash offers ~10k RPD.

2. **Performance parity**: Surprisingly, Flash and Pro achieved similar accuracy on calibration tiles (F1 ~0.86). Flash's lower reasoning capability forces prompts to be explicit and robust ("Strict Teacher" effect).

3. **Cost efficiency**: Flash is ~20× cheaper than Pro. Running Flash 30 times ("Flash Swarm") costs ~15% of running Pro 10 times, with comparable F1.

4. **Development velocity**: Flash enables rapid iteration during prompt engineering. Pro is reserved for final validation.

**Evidence**: Working Notes Observations 21-22, 28-31.

**Implementation**: H6 tests whether Flash-optimal configuration transfers to Pro.

---

## Decision 2: Thinking Level — Minimal

**Date**: 2026-01-15

**Decision**: Use `thinking_level=minimal` for all Gemini 3 configurations.

**Alternatives considered**:

- `thinking_level=low`
- `thinking_level=high`

**Rationale**:

Pilot study on 20 stratified tiles (10 runs each level) found:

| Level | Mean F1 | F1 Std Dev | Latency (20 tiles) |
|-------|---------|------------|-------------------|
| Minimal | 0.752 | 0.023 | 34.2s |
| Low | 0.758 | 0.022 | 66.5s |
| High | 0.748 | 0.044 | 97.3s |

Key findings:

- No significant F1 difference between levels (ANOVA p > 0.05)
- High shows 2× the F1 variance of minimal
- Minimal is 2.84× faster than high

**Conclusion**: Visual pattern matching (symbol detection) does not benefit from extended reasoning. The model either recognises the "sunburst" mound symbol or it doesn't — additional reasoning steps don't improve pattern recognition.

**Evidence**: Preregistration §8.9, execution-plan.md Phase 0 checklist.

---

## Decision 3: Two-Stage Pipeline — Exploratory Status

**Date**: December 2025

**Decision**: Treat two-stage pipeline (H2) as exploratory rather than primary confirmatory hypothesis.

**Alternatives considered**:

- Two-stage as primary detection architecture
- Two-stage only (abandon single-stage)

**Rationale**:

Preliminary testing found two-stage pipelines underperformed single-stage with voting:

| Architecture | F1 | Precision | Recall | Notes |
|--------------|----|-----------|----- --|-------|
| Single-stage 2/5 voting | 0.86 | 0.85 | 0.86 | Simple, effective |
| Two-stage (v4.5 verifier) | 0.80 | 0.77 | 0.84 | Context loss in cropped candidates |
| Two-stage + voting | 0.75 | - | - | Verifier too conservative |

**Root causes of two-stage failure**:

1. **Compounding errors**: If Stage 1 misses a target, Stage 2 never sees it
2. **Context loss**: Verifier sees cropped regions without full map context
3. **Systematic failures**: Two-stage failures are systematic (unfixable by voting); single-stage failures are stochastic (fixable by voting)

**Literature review finding**: The "+5-8% F1" claim for two-stage VLM pipelines could not be traced to peer-reviewed sources. The figure appears extrapolated from traditional ML cascaded classifier literature.

**Evidence**: Working Notes Observations 44, 46, 50.

**Implementation**: H2 remains in preregistration to formally test the null hypothesis (two-stage ≤ single-stage).

---

## Decision 4: Hard Example Selection Criteria

**Date**: 2026-02-01 (Phase 1 complete)

**Decision**: Select hard positives and hard negatives from Phase 1 baseline evaluation using a two-dimensional ranking: (1) frequency (vote count / miss rate), (2) localisation accuracy (proximity to nearest counterpart). See `outputs/phase1-library/fp-fn-register.md` for the full register and Observation 76 in working notes.

### Hard Positive Selection (examples 05-08)

**Preregistered criteria** (§8.4.2): K=5 passes, rank by miss frequency. The appendix (line 115) contains a stale "≥3/10 passes" reference from an earlier draft, but the operative procedure (appendix lines 98–99) and execution simulation both specify K=5 with ≥3/5 threshold. See errata E15.

**Actual execution**: K=5 passes as preregistered. All 24 FNs were complete misses (0/5), so frequency alone provided no differentiation. Applied proximity-based secondary ranking:

- **Recognition failures** (>50m from nearest detection): 9 FNs, genuinely invisible to the model
- **Localisation failures** (20-50m from nearest detection): 15 FNs, detected but misplaced

#### Initial selection (Session 6)

Selected 4 recognition failures, one per map sheet (farthest from nearest detection first):

| Example | fid | Map | Nearest Detection | Source Tile |
|---------|-----|-----|-------------------|-------------|
| 05 | 354 | Rakovski | 2449.9m | K-35-062-2_Rakovski_x0_y1344.png |
| 06 | 249 | Lesovo | 1807.8m | K-35-078-1_Lesovo_x1344_y448.png |
| 07 | 556 | K-35-052-4 | 572.1m | K-35-052-4_32635_x2240_y3136.png |
| 08 | 105 | Elenovo | 243.6m | K-35-053-3_Elenovo_x896_y1344.png |

#### Revision (Session 7) — boundary artefact discovery

Diagnostic analysis revealed that fids 354, 249, and 556 are entirely outside all calibration tile polygons — their reference coordinates fall in gaps between the 5 scattered tiles per sheet. They never contributed to the FN count and are not genuine recognition failures. The evaluation scoping bug (E7, see protocol errata) allowed these out-of-scope references to appear in the FN list because references were tested against `union_all()` of tile polygons rather than individual tiles. With non-adjacent calibration tiles, the union is geometrically equivalent to per-tile scoping, so the bug did not inflate the F1 metrics, but the register included these references in the unscoped crop analysis.

#### Final selection approach

**Priority**: Recognition failures over localisation failures. Localisation failures (detection within 20-50m of reference) would be hits at production tolerances (~50m / 10px at 5m/px). The core hard example library should teach the model to *recognise* mounds, not to place centroids more precisely. See Observation 79 in working notes.

**Ranking**: Among recognition failures (>50m from nearest detection), rank by (1) vote count of nearest detection descending (more votes = more systematic miss), then (2) distance to nearest detection descending.

**Edge clearance**: Candidates where the mound symbol is truncated at the tile edge are excluded. Minimum ~5px clearance from any tile edge is required for the symbol to be fully visible. Truncated symbols are not genuine recognition failures because the 64px tile overlap ensures the full symbol appears in an adjacent tile. Fid 161 (Elenovo, west edge, ~2/3 truncated) was excluded on this basis.

**Map sheet stratification**: One-per-sheet diversity was used as a tiebreaker in the initial selection. In the revised selection, this constraint was relaxed because Lesovo and K-35-052-4 had zero recognition failures among their calibration FNs — all their FNs were either out-of-scope (boundary artefacts) or localisation failures. Requiring one-per-sheet would force inclusion of localisation failures on those sheets, contradicting the recognition-failure priority. The constraint is relaxed only for hard positives; hard negatives retain one-per-sheet stratification.

**Final hard positives**:

| Example | fid | Map | Votes | Nearest Det. | Source Tile |
|---------|-----|-----|-------|-------------|-------------|
| 05 | 399 | Rakovski | 0/5 | 1243.1m | K-35-062-2_Rakovski_x448_y2688.png |
| 06 | 99 | Elenovo | 0/5 | 1047.1m | K-35-053-3_Elenovo_x896_y1344.png |
| 07 | 15 | Rakovski | 0/5 | 905.6m | K-35-062-2_Rakovski_x896_y2688.png |
| 08 | 105 | Elenovo | 0/5 | 243.6m | K-35-053-3_Elenovo_x896_y1344.png |

**Note**: Examples 05 and 07 share Rakovski; examples 06 and 08 share Elenovo. This doubles up on two sheets while leaving Lesovo and K-35-052-4 unrepresented in hard positives. The trade-off is justified: prioritising genuine recognition failures provides more useful training signal than sheet diversity with inappropriate examples. The expanded library (Scale-16, Scale-32) will restore sheet diversity as more candidates are added.

**Crop extraction** (Session 7, continued): 128×128 pixel crops, centred on the reference mound coordinate, extracted from the full map GeoTIFFs (`inputs/rasters/*.tif`) rather than from detection tiles. This ensures the target symbol is always at the crop centre with symmetric real map context, even when the reference point is near a tile edge. See errata E8 for rationale and alternatives considered, and Observation 80 in working notes. Crop size (128×128) is flagged as a future OFAT exploratory variable (see Observation 78).

**Departure from preregistered frequency-only ranking**: Proximity-based secondary ranking was applied because frequency alone provided no differentiation (all FNs were 0/5 complete misses). The proximity dimension provides stricter differentiation than frequency alone. K=5 passes were used as preregistered (see E15 regarding an inconsistent stale reference in the appendix). The one-per-sheet tiebreaker and its relaxation are not preregistered — they are post-hoc selection criteria applied during library construction.

### Hard Negative Selection (examples 11-14)

**Preregistered criteria** (§8.4.2): K=5 passes, FPs occurring ≥3/5, rank by detection frequency.

**Actual execution**: 18 FPs at vote ≥3/5 (6 at 5/5, 3 at 4/5, 9 at 3/5). Among the 6 vote-5/5 FPs, applied proximity-based secondary ranking:

- **Hallucinations** (>500m from any reference): Model fabricates detections with no nearby ground truth
- **Near-misses** (20-30m from a reference): Poorly localised true positives, not genuine false alarms

Selected 4 hallucinations from vote-5/5 tier, one per map sheet:

| Example | Subtype | Map | Nearest Reference | Source Tile |
|---------|---------|-----|-------------------|-------------|
| 11 | burial_mound | Rakovski | 1896.0m | K-35-062-2_Rakovski_x0_y3136.png |
| 12 | triangulation_mound | Lesovo | 1807.8m | K-35-078-1_Lesovo_x1344_y896.png |
| 13 | burial_mound | K-35-052-4 | 872.9m | K-35-052-4_32635_x1344_y1344.png |
| 14 | burial_mound | Elenovo | 725.0m | K-35-053-3_Elenovo_x3136_y3136.png |

**Tiebreaker**: Map sheet stratification (one per sheet) was used as the primary tiebreaker after vote count and proximity classification. This maximises cartographic diversity in the library.

### Legend-Derived Negatives

Two hard negatives can be specified before empirical analysis:

- Standalone triangulation point (no associated mound)
- Standalone benchmark (no associated mound)

These are categorised as `canonical_negative` in the library configs.

**Evidence**: Preregistration §8.4.2, `outputs/phase1-library/fp-fn-register.md`, Observation 76 in working notes.

---

## Decision 5: Temperature Default — 1.0

**Date**: December 2025

**Decision**: Use T=1.0 as the baseline temperature, with H7 testing alternatives.

**Alternatives considered**:

- T=0.0 (deterministic)
- T=0.7 (moderate variance)
- T=0.3 (evidence from literature)

**Rationale**:

1. **Vendor recommendation**: Gemini documentation recommends T=1.0 for reasoning tasks

2. **Preliminary testing**: Found T<1.0 degraded single-pass performance, but lower temperatures may benefit voting ensembles

3. **Voting benefit**: Higher temperature increases output diversity across passes. T=0.7 achieved Union Recall of 0.94 on training set

**Remaining uncertainty**: The optimal temperature may differ for single-pass vs voting. H7 tests 5 levels (0.0, 0.3, 0.7, 1.0, 1.3) to characterise the temperature-performance curve.

**Evidence**: Working Notes Observations 42-43.

---

## Decision 6: Consensus Voting as Primary Strategy

**Date**: December 2025

**Decision**: Use consensus voting (n-of-x) as the primary performance optimisation strategy.

**Alternatives considered**:

- Complex prompt engineering
- Two-stage pipelines
- Cross-model ensembles

**Rationale**:

Voting is the only strategy that consistently improved performance:

| Strategy | F1 Improvement | Complexity | Status |
|----------|---------------|------------|--------|
| Text minimisation | Negative (v3.5 < v3.2) | Low | Failed |
| Two-stage pipeline | Negative (0.80 vs 0.86) | High | Failed |
| Consensus voting | +0.06 to +0.12 | Low | Success |

Voting addresses stochastic variation in VLM outputs without assumptions about:

- Text-image interference (task-specific)
- Model architecture (model-specific)
- Reasoning patterns (domain-specific)

**Evidence**: Working Notes Observations 29-32, 44, 50.

**Implementation**: H3 tests voting pool sizes (N=5, 10, 30) and thresholds.

---

## Decision 7: Neutral Filenames for Examples

**Date**: January 2026

**Decision**: Use neutral filenames (`example_01.png`, `example_02.png`, ...) for few-shot examples rather than descriptive names.

**Rationale**:

1. **Prevent semantic leakage**: Descriptive filenames like `burial_mound.png` or `false_positive.png` could bias the model through filename parsing

2. **Consistent treatment**: All examples use the same naming pattern regardless of category

3. **Symlink approach**: Neutral names are symlinks to the actual files, preserving organisation while hiding semantic information from the model

**Implementation**: `inputs/examples/neutral-naming/MANIFEST.md` documents the mapping.

---

## Decision 8: Scale-8 as Default Library

**Date**: January 2026

**Decision**: Use Scale-8 library (17 examples) as the default for H5 testing and as the baseline for H8 comparisons.

**Composition**:

| Component | Count |
|-----------|-------|
| Canonical Positive | 4 |
| Canonical Negative | 2 |
| Hard Positive | 4 |
| Hard Negative | 4 |
| Null | 3 |
| **Total** | **17** |

**Rationale**:

1. **Includes all component types**: Enables testing negative text treatment (H5) with full library

2. **Balanced HP:HN ratio**: 1:1 ratio avoids majority label bias

3. **Manageable token count**: 17 examples fit comfortably in context window

4. **Scaling baseline**: Serves as midpoint for H8 scaling comparisons (Scale-4 → Scale-8 → Scale-16 → Scale-32)

**Evidence**: Preregistration §8.3.4, library_scale-8.json.

---

## Decision 9: Sequential OFAT Design

**Date**: January 2026

**Decision**: Use One-Factor-At-a-Time (OFAT) sequential design rather than full factorial for confirmatory hypotheses.

**Alternatives considered**:

- Full factorial (all combinations)
- Parallel OFAT (test factors independently)

**Rationale**:

1. **Budget constraint**: Full factorial would require ~54 cells at $11/cell ≈ $594. Sequential OFAT requires 26 cells ≈ $286.

2. **Optimal parameter propagation**: Each factor is tested at the optimal level of previous factors, ensuring comparisons are made at truly optimal conditions.

3. **Interaction sensitivity**: If major interactions exist, OFAT will underestimate their effects — but preliminary testing suggests factor effects are largely additive.

**Trade-off acknowledged**: OFAT cannot detect interactions. If H5 × M/E interaction is suspected, exploratory bootstrap interaction test (difference-of-differences) is included in Phase 2d analysis.

**Evidence**: Preregistration §8.3.1a, execution-plan.md dependency graph.

---

## Decision 10: Statistical Methods — Bootstrap CIs with FDR Correction

**Date**: 2026-01-22

**Decision**: Use bootstrap confidence intervals with Benjamini-Hochberg FDR correction for multiple comparisons.

**Statistical approach**:

| Component | Method | Parameters |
|-----------|--------|------------|
| Confidence intervals | Bootstrap resampling (tile-level) | 1000 iterations, percentile method (2.5th/97.5th) |
| Multiple comparisons | Benjamini-Hochberg FDR | q = 0.05 |
| Effect sizes | F1 difference with 95% CI | Signed difference between conditions |

**Rationale**:

1. **Bootstrap CIs**: Non-parametric approach makes no distributional assumptions. Tile-level resampling preserves spatial structure.

2. **Benjamini-Hochberg**: Controls false discovery rate rather than family-wise error rate, offering better power for multiple comparisons while controlling type I error.

3. **Effect size focus**: Primary inference is based on effect sizes (F1 differences) with CIs, not p-values. This aligns with modern statistical practice.

**Implementation note — Pseudo-p-values**:

The FDR correction uses pseudo-p-values derived from bootstrap CI position rather than formal p-values. If the 95% CI for a difference excludes zero, we treat this as "significant" for FDR purposes (pseudo-p < 0.05). This is a pragmatic simplification:

- It is conservative: the CI must fully exclude zero
- It aligns with our preregistered focus on effect sizes with CIs
- It avoids the need for formal null hypothesis significance testing

This approach is not standard but is appropriate for CI-based inference where we prioritise effect size estimation over binary significance decisions.

**Implementation**: `scripts/lib_advanced_metrics.py` (bootstrap functions), `scripts/analyse_phase2_results.py` (FDR correction, lines 174-183).

---

## Decision 11: 50m Recognition/Localisation Threshold and HP Pool Exhaustion

**Date**: 2026-02-02

**Decision**: Formally adopt a 50m distance threshold to distinguish recognition failures
from localisation failures. Exclude localisation errors (nearest detection <50m) from
hard example libraries. Accept that the hard positive (HP) pool is structurally capped
at 4 examples, and defer Scale-16/Scale-32 H8 conditions to post-H10.

### 50m threshold rationale

**Distributional evidence**: CC's boundary/edge-clearance analysis of all 24 FNs
revealed a distributional cliff between 30m and 50m:

| Threshold | Usable FNs | Selected | Available for expansion |
|-----------|-----------|----------|------------------------|
| >20m      | 18        | 4        | 14                     |
| >30m      | 9         | 4        | 5                      |
| >50m      | 4         | 4        | 0                      |
| >100m     | 3         | 3        | 0                      |

Below 30m: clear localisation territory. 30–50m: ambiguous. Above 50m: genuine
recognition failures. The cliff itself is the empirical evidence for the threshold.

**Conceptual rationale**: Few-shot libraries teach the model *what to look for*. A
recognition failure (FN >50m from nearest detection) is a mound the model could not
identify — showing it as an HP directly addresses that gap. A localisation failure
(FN 20–50m from nearest detection) is a mound the model *did* recognise but placed
incorrectly. Showing more examples of already-recognised mounds will not fix coordinate
prediction — that is an architectural limitation, not a pattern-matching failure.

Similarly, "phantom" FPs from localisation errors are not genuine confusable symbols.
Including them as HNs would teach the model to avoid random map patches, which is
uninformative.

**Alternative considered**: 100m threshold (~25px, Opus suggestion). Rejected because it
would disqualify fid 99 (96.4m), dropping the usable HP pool from 4 to 3 and leaving
Scale-8 unfillable. The 50m boundary is supported by the distributional cliff and is the
maximum threshold that retains all 4 selected HPs.

### HP pool exhaustion

Of 9 recognition failures (>50m) in the FN register:

- 4 selected for Scale-8 (fids 399, 99, 15, 105)
- 3 out of scope — boundary artefacts (fids 354, 249, 556; see errata E7)
- 1 out of scope — newly discovered (fid 489, outside all calibration tiles)
- 1 edge risk — symbol truncated (fid 161, 3.3px from tile edge)

Zero recognition failures remain for library expansion. The expansion pool is entirely
localisation failures (14 usable, 20–50m from nearest detection), which are excluded by
this decision.

### HN pool status

The HN pool is not constrained. At the 50m threshold, 46 usable FPs are available for
expansion (89 total, all in scope). At a stricter 100m threshold, 30 remain available.
Vote-band distribution among available HN candidates: 2 at 4/5, 3 at 3/5, 5 at 2/5,
36 at 1/5.

### Implications for H8 library scaling

| H8 Condition    | HP | HN | Status |
|-----------------|----|----|--------|
| Pure Pos. Canon | 0  | 0  | Runs as designed |
| Canonical       | 0  | 0  | Runs as designed |
| +HP             | 4  | 0  | Runs as designed |
| Scale-4         | 2  | 2  | Runs as designed |
| Scale-8         | 4  | 4  | Runs as designed |
| Scale-16        | 8  | 8  | Deferred — capped at Scale-8 under 1:1 HP:HN |
| Scale-32        | 16 | 16 | Deferred — capped at Scale-8 under 1:1 HP:HN |

This is anticipated by the preregistration (line 815): "If fewer than 16 distinct HPs
or HNs are available, Scale-32 (and possibly Scale-16) will be capped at the maximum
available while preserving 1:1 ratio."

Testable contrasts C1–C3, S1, and B1 are unaffected. Scaling contrasts S2 and S3 are
deferred to post-H10 (calibration tile expansion).

### Implications for H9 (diversity) and H12 (ratio)

**H9**: Runs as HN-diversity-only test. HP channel is frozen (4 slots, 4 examples —
every HP appears in every pass). HN rotation is the more important diversity dimension
given that FPs outnumber FNs. HP diversity is untestable due to pool exhaustion.

**H12**: Deferred to post-H10. With HP capped at 4, the only testable ratios are
HP-constant with varying HN (e.g., 4:4, 4:8), which confounds ratio with total count.
Deferring until H10 expands the HP pool enables the full symmetric ratio design.

### Reportable finding

The structural asymmetry between HP and HN pools is itself a finding. It indicates the
model's primary weakness at baseline is **precision** (too many false alarms → abundant
HN candidates) rather than **recall** (missing mounds → few HP candidates). A model that
over-detects but needs human filtering is operationally different from one that silently
misses features.

**Evidence**: `outputs/phase1-library/fp-fn-register.md`, `planning/hard-example-library-decisions.md`, CC boundary/edge-clearance analysis (Session 8).

---

## Decision 12: Centre-Pointing Language in Prompts

**Date**: 2026-02-02 (revised 2026-02-02)

**Decision**: Add a descriptive centre-pointing statement to all detection prompt
preambles, applied uniformly across all 11 prompt variants including all H5 conditions
(Minimal, Terse, Verbose).

**Language added** (single sentence, identical in all 11 files):

> Each reference image is centred on the feature being labelled — the target symbol
> for Positive examples, the confusable feature for Negative examples.

**Revision note**: The initial wording ("Each reference image is centred on the relevant
feature") was ambiguous for negative examples — "relevant feature" could be interpreted
as a nearby mound rather than the confusable non-mound at the crop centre. The revised
wording explicitly ties the label to the centred feature for both positive and negative
cases.

**Rationale**:

1. At 128×128 crops, images may contain 2–3 mound symbols if they cluster. Without
   centre-pointing, the model may latch onto an easy neighbouring mound instead of the
   difficult target HP.

2. For HNs, a crop centred on a confusable symbol may also contain a real mound at
   the periphery. Labelling the whole image "Negative" without centre-pointing sends
   a contradictory signal. The revised wording resolves this by making clear that the
   negative label applies to the *centred* feature specifically.

3. The Stage 2 verifier prompt already uses "candidate symbol in the centre" language,
   so this is consistent with existing design.

4. Framed as *descriptive* ("each image is centred on...") rather than *imperative*
   ("look at the centre of...") to avoid biasing spatial scanning during detection.

5. **Uniform across H5 conditions**: Centre-pointing is spatial orientation (telling the
   model *where* to look), distinct from H5's diagnostic text (explaining *why* something
   is or isn't a mound). Varying spatial language across H5 levels would co-vary spatial
   instruction with diagnostic text, introducing a confound. Keeping the single sentence
   identical across all H5 conditions preserves factor orthogonality.

6. "Confusable" was chosen over the more neutral "non-target" because it primes the model
   to understand these examples were selected specifically because they resemble mounds,
   setting up a discrimination task rather than mere classification. This is a marginal
   wording choice, not strong enough to constitute diagnostic content that would interfere
   with H5.

**Watch for**: Spatial bias in detections clustering toward tile centres. This would
suggest the centering instruction bleeds from exemplar interpretation into detection
behaviour. Low risk given that detection prompts explicitly say "scan the target image."

**Files modified**: All 11 `detect_*.md` system instruction files in
`prompts/system-instructions/`.

**Evidence**: `planning/hard-example-library-decisions.md` §2.

---

## Decision 13: VLM-Calibrated Prompt Diagnostics

**Date**: 2026-02-03

**Decision**: Prompt text describing hard example features should use only diagnostics
that are reliably resolved by VLMs at exemplar crop resolution (128×128 pixels), not
all diagnostics that are cartographically valid at higher resolution.

**Context**: During human review of hard-example-derived prompt text, the researcher
(Shawn) identified detailed visual diagnostics for each hard negative — solid vs hollow
fill, black outlines, mixed black-brown colouring, half-black-half-white patterns. CC
(Opus 4.5) was then asked to check these observations against the crops from a VLM
perspective. Several diagnostics that are clear to a human examining the map proved
unreliable or ambiguous when viewed at 128×128 pixel resolution.

**Diagnostic reliability at 128px exemplar resolution**:

| Diagnostic | Human | VLM at 128px | Prompt use |
|---|---|---|---|
| Outward-radiating rays (present/absent) | High | High | Primary — use |
| Ray/mark direction (inward vs outward) | High | Medium-high | Use |
| Overall colour composition (mixed dark + brown) | High | Medium-high | Use |
| Solid fill vs hollow centre | High | Low | Avoid — blur erases at ~3-5px |
| Black outline around shape | Medium-high | Medium | Use cautiously |
| Specific fill patterns (e.g., half-and-half) | High (at zoom) | Low | Avoid |
| Clustering — multiple nearby symbols | High | Medium | Needs explicit prompt guidance |
| "Keep looking after first find" behaviour | Natural for trained humans | Low | Needs explicit prompt guidance |

**Rationale**:

1. **Resolution arithmetic**: At 128×128, a 15-20px mound symbol occupies ~1-2.5% of
   crop area. The hollow centre is ~3-5px across — barely resolved even before any
   compression or resampling artefacts. Fine internal structure is lost at this scale.

2. **False negative risk**: A diagnostic like "mound symbols have hollow centres" could
   cause the VLM to reject legitimate mounds whose centres appear filled due to blur,
   scanning artefacts, or internal image resampling. The ray diagnostic is more robust
   because rays extend outward into surrounding space where there is more contrast.

3. **Internal model resampling**: VLMs typically resize input images to an internal grid
   (architecture-dependent, often 224×224 or 336×336 tokens). A 128px crop is upscaled
   ~1.75-2.6×, which introduces interpolation. Fine details that barely survive in the
   input may be smoothed away during this resampling step. Features that extend into
   surrounding space (rays) survive resampling better than features confined to a small
   interior region (fill pattern).

4. **Descriptive principle interaction**: This decision reinforces the existing principle
   that prompt text should describe visual appearance rather than interpret map symbology
   (Decision 12 note). Both principles point toward the same practice: describe features
   the VLM can reliably perceive, at the resolution it will encounter them.

**Implications for crop-size exploratory variable**: The diagnostic reliability table
suggests specific evaluation criteria for the flagged crop-size OFAT variable (see
`planning/hard-example-library-decisions.md` §1, "Future exploratory"). Rather than
measuring only overall F1 at each crop size, the study could assess whether increasing
crop size makes previously-unreliable diagnostics (fill pattern, outline detail) become
reliable — and whether prompts can then be enriched with those diagnostics. This would
connect crop size to prompt content in a principled way. This interaction is
observational (not preregistered), but worth documenting during exploratory runs.

**Evidence**: Session 11 human-VLM cross-check of hard example crops, Working Notes
Observation 87.

---

## Decision 14: Visual Appearance over Cartographic Identity in Prompts

**Date**: 2026-02-03

**Decision**: Prompt text describing map features should use visual appearance
descriptions (colours, shapes, spatial relationships) rather than cartographic
feature names (grid lines, contour lines, roads, infrastructure markers).

**Alternatives considered**:

- Cartographic naming (preregistered approach): "Contour Line Artefacts",
  "Infrastructure Markers", "Roads (black/red lines), contour lines (brown),
  grid lines (blue)"
- Visual description (adopted): "Closed Curved Line Patterns", "Dots on
  Linear Features", "Lines in various colours (black, red, brown, blue)"

**Rationale**:

1. **VLM perception mismatch**: The VLM may not interpret feature identities
   the same way a human cartographer would. A human reads "grid line" and knows
   what to look for; a VLM may not map that label to the correct visual pattern.
   Visual descriptions ("vertical blue line") are robust because they describe
   what the model actually sees in the image.

2. **Consistency with target symbol register**: The target burial mound symbol
   is already described visually ("sunburst with outward-radiating rays"), not
   cartographically ("symbol 78 from the legend"). Exclusion criteria should use
   the same descriptive register.

3. **Interpretive glosses removed**: Phrases like "(inward = excavation,
   outward = elevation)" assume cartographic knowledge the VLM does not have.
   The visual distinction (marks pointing inward vs rays extending outward)
   is sufficient and directly observable.

**Distinction from Decision 13**: Decision 13 asks *which diagnostics are
reliable at 128px resolution* (a resolution-dependent filtering question).
Decision 14 asks *what register of description to use* (a conceptual framing
question). Both principles were articulated in the same review session but
address different aspects of prompt design. A diagnostic could be resolution-
robust but still described in cartographic terms (e.g., "contour lines are
brown" is reliable at 128px but assumes the VLM knows what a contour line is).

**Changes to preregistered prompt text** (commit `2d46311`, 2026-02-03):

| Preregistered text | Revised text |
|--------------------|--------------|
| "Contour Line Artefacts" | "Closed Curved Line Patterns" |
| "Infrastructure Markers" | "Dots on Linear Features" |
| "Quarry and Pit Symbols" | "Inward-Pointing Marks" |
| "Roads (black/red lines), contour lines (brown), grid lines (blue)" | "Lines in various colours (black, red, brown, blue)" |
| "(inward = excavation, outward = elevation)" | Removed |

Applied across all 10 detection prompt files. See errata E16.

**Evidence**: Session 11 prompt text review,
`archive/planning/hard-example-review/prompt-text-review-synopsis.md` §1
(Governing Principles), Working Notes Observation 87.

---

## Phase 1 Decisions (Resolved)

The following items from the original "Future Decisions" section are now resolved:

- [x] Specific hard positive examples selected — Decision 4 (2026-02-01)
- [x] Specific hard negative examples selected — Decision 4 (2026-02-01)
- [x] Adjustments to library composition — Decision 11 (Scale-16/32 deferred)
- [x] Scale-32 feasibility — Decision 11 (HP pool exhausted at 4)

---

## Phase 2 Execution Decisions

---

### Decision 15: Replace run_study.py with run_phase2.py for Phase 2 Execution

**Date**: 2026-02-05

**Decision**: Create a purpose-built `scripts/run_phase2.py` OFAT runner for Phase 2 sub-phases (2a–2e), replacing the generic `scripts/run_study.py` which has been archived to `archive/deprecated-scripts/`.

**Alternatives considered**:

- Modify `run_study.py` to handle OFAT YAMLs
- Use `run_study.py` as-is with adapted YAML files

**Rationale**:

`run_study.py` has four incompatibilities with the OFAT YAML structure:

1. **Hardcoded factor names**: `generate_conditions()` expects `modality`, `ordering`, `hard_negatives`, `temperature` as factor keys. Phase 2a has a single factor `modality_elaboration`.
2. **`defaults` vs `fixed`**: Validation requires a `defaults` section; Phase 2 YAMLs use `fixed` and `inputs`/`execution`.
3. **No runs loop**: The YAML declares `runs: 10`, but the runner calls the batch detector once per condition (one pass total), with no run iteration.
4. **No output hierarchy**: No `{condition}/run_{K}/` directory structure.

Modifying `run_study.py` would require rewriting most of its logic while maintaining backwards compatibility with an unused factorial YAML format. A clean replacement is simpler and more maintainable.

**Key design points of `run_phase2.py`**:

- Parses OFAT YAML: single factor's levels (each with `name` + `config`), `fixed` params, `inputs`, `execution` sections
- Also handles Phase 2d's pre-enumerated `conditions` list with `reuse_from` support
- Loops condition × run, calling `4_detect_mounds_batch.py` via subprocess (one pass per run)
- Output to: `{output_dir}/{condition_name}/run_{K}/`
- JSON checkpoint tracking `(condition, run)` tuples for resume
- CLI overrides: `--runs`, `--limit` (tiles), `--condition`, `--dry-run`, `--resume`
- Cost monitoring with 120% warning threshold
- Randomised execution order with fixed seed to distribute temporal effects

**Evidence**: Session 17 plan mode analysis of `run_study.py` vs OFAT YAML structure.

---

## Decision 16: Dual-Track Carry-Forward After Unexpected H1 Result

**Date**: 2026-02-06

**Decision**: Carry forward two M/E levels from Phase 2a rather than the preregistered
single winner: (1) **brief-text** (text-only, highest overall F1=0.5425) and
(2) **brief-text-image** (best image-using condition, F1=0.4617). Each track
follows an independent optimisation path through subsequent phases, with the
text-only track receiving a tailored subset of tests.

**Deviation from preregistration**: The preregistered OFAT design (§8.3.1a)
specifies a single carry-forward: "select M/E level with highest F1" for all
subsequent phases. This decision deviates by carrying two levels, because the
preregistered design assumed the winner would be image-using and several
downstream phases are structurally incompatible with a text-only winner.

See erratum E27.

### Rationale

Phase 2a produced a counter-intuitive result: text-only conditions outperformed
image-using conditions. Brief-text achieved the highest mean F1 (0.5425),
exceeding brief-text-image by +0.08. However, no pairwise comparisons survived
FDR correction (q=0.05), so the result is suggestive rather than conclusive.

The preregistered single-winner carry-forward creates a structural problem:

1. **Phase 2d (H5 negative text)**: Explicitly excludes text-only M/E levels
   ("requires images to show"). No H5 variant configs exist for brief-text.
2. **Phase 2c (H8 library composition)**: Tests which example *images* to
   include. With `include_example_images: false`, the test is meaningless.
3. **Phase 2e (H4 ordering)**: Tests example image ordering, a different
   construct from prompt section ordering in text-only prompts.

Carrying forward only brief-text would abandon the image-based pipeline
entirely — despite it being the project's primary optimisation target and
despite the non-significance of the H1 differences. Carrying forward only
brief-text-image would ignore the best-performing condition.

The dual-track approach resolves this by:

- Preserving the image-based optimisation pipeline (brief-text-image through
  all preregistered phases)
- Exploring the text-only result with targeted tests where they make sense
- Allowing potential convergence at Phase 3, where voting ensembles could
  combine runs from both tracks

### Track 1: brief-text-image (image-using)

Follows the preregistered OFAT sequence as originally designed:

| Phase | Factor | Status |
|-------|--------|--------|
| 2b | H7 Temperature (5 levels) | Planned |
| 2c | H8 Library composition (7 cells) | Planned |
| 2d | H5 Negative text treatment (6 cells) | Planned |
| 2e | H4 Ordering (3 cells) | Planned |

### Track 2: brief-text (text-only)

Receives a tailored subset of tests:

| Phase | Factor | Status | Notes |
|-------|--------|--------|-------|
| 2b | H7 Temperature (5 levels) | Planned | Same 5 temperature levels; may optimise at a different T than Track 1 |
| 2c | H8 Library composition | **Skipped** | Meaningless without images |
| 2d | Negative guidance text | **Deferred** | If FP rate warrants it, ad hoc testing of additional negative text guidance (distinct from preregistered H5 which is about text attached to negative *images*) |
| 2e | Prompt section ordering | **Deferred** | If pursued, tests ordering of major prompt sections (positive guidance, negative guidance, task description) — a different construct from preregistered H4 (example library ordering) |

### Independent optimisation

Each track carries its own optimal parameters forward independently. If the
two tracks optimise at different temperatures in Phase 2b, those different
optima are carried forward into their respective subsequent phases rather than
selecting a single global temperature.

### Budget implications

Track 1 runs the full preregistered sequence (21 cells beyond 2a). Track 2
adds 5 cells for temperature testing, plus potential ad hoc cells for deferred
items if pursued. Total additional cost from dual-track: ~$55 (5 cells × $11).

### Convergence at Phase 3

Both tracks feed into Phase 3a (H3 voting), where ensembles mixing text-only
and image-using runs could be tested alongside single-track ensembles. The
K=10 runs from Phase 2a already provide data for post-hoc voting analysis at
both M/E levels.

**Evidence**: Phase 2a analysis (`outputs/phase2a/analysis_summary.md`),
Phase 2a verification report (`results/phase2-factorial/phase2a-verification-report.md`),
Working Notes Observation 103.

---

### Decision 17: Phase 2d Design — Plus-hp Carry-Forward, Instruction Adaptation, Dual-Track OFAT

**Date**: 2026-02-11

**Decision**: Phase 2d tests H5 (exclusion guidance levels) using an OFAT
single-factor design across two tracks, with instruction text adapted to
remove references to non-existent hard negative (HN) reference images.

### Design changes from preregistration

| Aspect | Preregistered | Actual |
|--------|---------------|--------|
| Library | Scale-8 (17 examples, incl. 4 HN) | plus-hp (13 examples, no HN) |
| Design | 3×3 factorial (M/E × H5) | Single-factor OFAT (H5 at optimal M/E) |
| Tracks | Image-using only | Dual-track (image-using + text-only) |
| Instruction text | References HN images | HN image references removed |

### Library carry-forward

Phase 2c determined plus-hp (4C+ 4HP 2C- 3null, no HN) as the optimal
library. The preregistered H5 design assumed Scale-8 (including 4 HN) would
be the library, but HN were found to be counterproductive — they hurt
performance rather than helping. The exclusion *guidance text* (describing
what not to detect) remains valuable regardless of library contents; it is
domain knowledge that applies independently of whether HN examples are shown.

### Instruction text adaptation

Two edits to terse and verbose instruction files:

1. **Guideline 3** (shared across terse/verbose): Removed the second sentence
   describing negative reference image content. Canon- examples are legend
   entries (triangulation point, benchmark), not "confusable features"; HN
   images that were confusable features no longer exist in the library.

2. **Verbose exclusion intro**: Removed "Study any negative reference images
   carefully." — no negative reference images exist to study.

The minimal instruction is **not** modified. It serves as the Phase 2c
baseline for Track 1 and Phase 2b baseline for Track 2. Re-running 1,200
API calls to fix a conditional sentence ("If reference examples are provided")
that the model ignores when no negative images are present is not justified
by the minor confound it introduces.

### OFAT simplification

The preregistered 3×3 M/E × H5 factorial (9 cells) collapsed because the
OFAT chain selected a single optimal M/E per track. Testing H5 at only
the carried-forward M/E level gives 3 cells per track (1 reused baseline,
2 new), totalling 4 new cells across both tracks.

This sacrifices the ability to detect M/E × H5 interactions but is
consistent with the OFAT design philosophy applied throughout Phase 2.

### Track 2 activation

Decision 16 deferred Phase 2d for the text-only track. Activation is
justified because:

1. Precision is the bottleneck for both tracks (~52–56% for text-only at
   T=0.0 vs ~56–61% for image-using at T=0.0)
2. Exclusion guidance is purely textual — it does not depend on example
   images and applies identically in both modalities
3. Cost is low (~$2.50 for 1,200 API calls, no images in prompt)

### Implementation

| Track | M/E | Library | Baseline | New cells |
|-------|-----|---------|----------|-----------|
| Track 1 (image) | brief-text-image | plus-hp (13 ex.) | Phase 2c | terse, verbose |
| Track 2 (text) | brief-text | Scale-8 metadata (17 ex., none sent) | Phase 2b T=0.0 | terse, verbose |

**Total new API calls**: 2,400 (4 cells × 600)
**Estimated cost**: ~$6.90 ($4.40 Track 1 + $2.50 Track 2)

**Evidence**: Phase 2c analysis (plus-hp optimal), Phase 2b Track 2
analysis (precision bottleneck), Session 31 plan mode analysis of
instruction text confounds.

---

### Decision 18: Add Config-Default as 4th Ordering Condition in Phase 2e

**Date**: 2026-02-12

**Decision**: Add `config-default` as an explicit 4th ordering condition in Phase 2e
(H4 — Example Ordering), distinct from the true `canonical-first` ordering.

**Context**: During Phase 2e setup, review of the `reorder_examples()` function
revealed that the `canonical-first` ordering was a no-op — it returned examples
in config-file order `[C+, HP, C−, null]` rather than the intended canonical-first
grouping `[C+, C−, HP, null]` (see E29). All prior phases (2a–2d) therefore used
config-file order as their baseline, not true canonical-first.

**Alternatives considered**:

1. **Proceed with 3 conditions** (fix canonical-first, drop config-default): Would
   lose the ability to compare against the ordering all prior phases used.
2. **Treat config-default as canonical-first** (keep the no-op): Would conflate two
   meaningfully different orderings and miss the opportunity to test whether
   interleaving HP before C− matters.
3. **Add config-default as 4th condition** (selected): Preserves continuity with
   prior phases whilst enabling the intended canonical-first test.

**Rationale**:

The two orderings differ in HP placement relative to canonical negatives:

| Condition | Order | HP position |
|-----------|-------|-------------|
| config-default | `[C+, HP, C−, null]` | Between C+ and C− |
| canonical-first | `[C+, C−, HP, null]` | After all canonicals |

This difference is scientifically informative: if example ordering matters (H4),
the relative position of hard positives versus canonical negatives could affect
whether the model learns from the hard examples before or after seeing the
canonical baseline.

**Cost**: Zero additional API calls. The 10 config-default runs are reused from
Phase 2c plus-hp outputs via symlinks and are pre-checkpointed.

**Design**:

| Condition | Runs | API calls | Source |
|-----------|------|-----------|--------|
| config-default | 10 | 0 (reused) | Phase 2c plus-hp symlinks |
| canonical-first | 10 | 600 | New |
| canonical-last | 10 | 600 | New |
| random | 10 | 600 | New |
| **Total** | **40** | **1,800** | |

**Cross-references**: E29 (canonical-first bug), E30 (4th condition deviation).

**Evidence**: Session 32 Phase 2e setup analysis, `studies/phase2e-h4-ordering.yaml`.

---

## Decision 19: Re-run H11 PV Factorial with Corrected Configs

**Date**: 2026-03-15

**Decision**: Re-run all H11 proposer-verifier experiments (512 and 384)
with verifier configs corrected to match the Phase 3d baseline prompt
assembly. Supersede all prior PV results with "v2" corrected results.

### Rationale

A config audit (Observation 163) revealed that verifier configs created for
the H11 experiments had silently diverged from the Phase 3d baseline in
three ways:

1. **Text-only configs** (`verify_*-text.json`): missing the 6 text-only
   example labels that Phase 3d's `run_h2_pilot.py` sent
2. **Image configs** (`verify_*.json`): 9 examples instead of Phase 3d's 6,
   with modified labels and 3 extra null examples
3. **Crop introduction text**: "**Target Candidate:**" instead of Phase 3d's
   "Now classify the candidate symbol at the centre of this crop:"

These are non-target parameter changes that violate experimental control.
The original results cannot be attributed solely to the tile-size factor.

### Alternatives considered

1. **Accept results with caveat**: Document the config drift as a known
   limitation. Rejected — the drift affects multiple prompt elements
   simultaneously, making the results difficult to interpret.
2. **Re-run with corrected configs**: Ensures only the target parameter
   (tile size) differs between 384 and 512. Selected.

### Result

v2 corrected results: 512 PV F1=0.732 (was 0.796 pre-correction), 384 PV
best F1=0.682. Gap narrowed from 11.2 pp to 5.0 pp, though model drift
between March 8 and March 15 is a confound (Observation 165).

**Evidence**: Commits `cad5d33`, `9b023ae`, `6159416`. See Observation 163.

---

## Decision 20: Replicate Phase 3a Consensus with Controlled Thinking Levels

**Date**: 2026-03-15

**Decision**: Run a clean N=30 consensus replication at T=0.7 with both
minimal and HIGH thinking levels, using separate config files
(`detect_brief-text.json` and `detect_brief-text-high.json`) that differ
only in the `thinking_level` field.

### Rationale

Investigation of the Phase 3a metadata revealed that both `track2-text`
and `track2-text-high` directories recorded `thinking_level: minimal` in
their metadata files. Per Observation 141, the metadata captured the
config file's default value rather than the actual API parameter — the
HIGH directory did use HIGH thinking at the API level, but the metadata
is unreliable. This metadata bug means:

1. The Phase 3a thinking-level comparison (F1=0.751 vs 0.683) is valid
   but the metadata cannot verify it
2. A clean replication with properly controlled and metadata-verifiable
   configs eliminates this ambiguity
3. The replication also serves as a model drift test — if minimal
   replication departs from the historical range [0.683, 0.751], the
   model has changed

### Result

Replication confirms the direction: HIGH F1=0.735 vs minimal F1=0.699
(+3.6 pp). Model drift is modest — minimal replication (0.699) falls
within historical CI.

**Evidence**: Study YAML `phase3a-replication.yaml`, Observations 140-141.

---

## Decision 21: Abandon Flash-Lite Transfer Pathway

**Date**: 2026-03-15

**Decision**: Abandon Gemini 3.1 Flash-Lite (`gemini-3.1-flash-lite-preview`)
as a cheaper proxy for Flash. The model cannot perform the mound detection
task at a useful level.

### Rationale

The Flash-Lite transfer pilot (`planning/flash-lite-transfer-pilot.md`)
tested whether Flash-Lite preserves Flash's performance shape, which would
enable comprehensive statistical reruns at 4× lower cost (Batch API pricing).

Stage 1 (basic capability gate, F1 > 0.2) failed across all three variants:

| Variant | Detections | TP | FP | F1 |
|---------|----------:|----|----|----|
| Minimal T=0.0 | 282 | 21 | 261 | 0.111 |
| Minimal T=0.3 | 267 | 23 | 244 | 0.126 |
| HIGH T=0.0 | 89 | 9 | 80 | 0.097 |

Flash-Lite can detect map features but cannot discriminate mound symbols
from other cartographic elements. The 4.4 pp MMMU Pro gap (76.8% vs 81.2%)
translates to a ~43 pp F1 collapse on this task.

### Alternatives considered

1. **Flash-Lite with additional prompt engineering**: Rejected — the failure
   is at the visual discrimination level, not the prompt level. HIGH thinking
   made performance worse, not better.
2. **Try other cheaper models (Claude Haiku, GPT-4o-mini)**: Deferred to
   H14 cross-model testing. Models with MMMU Pro < 77% are likely to fail
   similarly.
3. **Proceed with Flash at standard pricing**: Accepted as the only viable
   option for now.

### Implications

Full-scale statistical reruns must use Flash pricing ($0.50/M input,
$3.00/M output standard; $0.25/$1.50 Batch API). This constrains the
budget for comprehensive reruns. The staged pilot design limited wasted
budget to ~$0.05.

**Evidence**: Observation 164, `planning/flash-lite-transfer-pilot.md`.

---

## Decision 22: Adopt Proposer-Verifier Pipeline for Production Evaluation

**Date**: 2026-03-19

**Decision**: Introduce a two-stage Proposer-Verifier (PV) pipeline as a post-hoc extension to the preregistered single-stage detection approach. The PV pipeline reuses existing proposer detections and adds a verifier stage that classifies candidate crops as mound/not-mound.

**Alternatives considered**:

- Continue with single-stage detection only (preregistered approach)
- Implement cascade verification (multiple verifier stages in sequence)
- Use model ensembling (multiple models instead of multiple stages)

**Rationale**:

1. The 60-tile pilot demonstrated +0.14 F1 improvement (0.605 → 0.796) from adding a verifier stage (Obs 150)
2. The PV approach reuses all existing proposer data — zero additional proposer API calls needed
3. Verifier cost is negligible (~$0.0002 per candidate) compared to proposer cost
4. The architecture is transparent: the verifier's reasoning (best alternative hypothesis, evidence, probability) is fully auditable per candidate
5. Cascade verification was tested in the pilot (Obs 161) but did not improve over single-stage verification

**Implementation**: `scripts/run_pv.py` with dual-mode execution (batch + real-time API). See E37 in protocol errata.

**Evidence**: Obs 150, 170; `results/phase3d-verifier-experiments-abc.md`; `results/pv/phase1/pv-phase1-analysis.md`

---

## Decision 23: 150px Crop Size as Verifier Default

**Date**: 2026-03-20

**Decision**: Use 150×150 pixel crops (padding=75) as the default crop size for the PV verifier. Users may adjust without meaningful performance change.

**Alternatives considered**:

- 75×75 px (tighter, better signal-to-noise ratio for small symbols)
- 300×300 px (more context for disambiguation)
- 40×40 px (minimal context, smallest possible crop)

**Rationale**:

1. Empirical sweep across 4 crop sizes (40, 76, 150, 300 px) showed F1 is insensitive between 75–300px (Obs 166)
2. 150px is the sweet spot: mound symbols are ~10–20px, so 150px provides 7–15× context
3. 40px showed the only noticeable degradation (F1 0.741 vs 0.770), confirming a lower bound
4. 300px was marginally worse than 150px, suggesting additional context adds noise

**Implementation**: `DEFAULT_PADDING = 75` in `extract_candidates.py` (crop size = padding × 2)

**Evidence**: Obs 166; `results/pv/phase1/pv-phase1-analysis.md`

---

## Decision 24: Single-Pass Verifier (No Consensus) as Default

**Date**: 2026-03-20

**Decision**: Use N=1 single-pass verification rather than N=5 consensus voting for the verifier stage. Consensus voting adds no significant value at the verification stage.

**Alternatives considered**:

- N=5 consensus at T=0.7 (matching proposer consensus approach)
- N=3 consensus as a lighter alternative

**Rationale**:

1. N=5 T=0.7 consensus produced F1=0.774 vs N=1 T=0.0 at F1=0.770 — a +0.004 difference well within CI overlap (Obs 167)
2. The adversarial verifier is already well-calibrated at T=0.0; adding stochastic variation via temperature doesn't improve judgements
3. N=1 is 5× cheaper in API calls and 5× faster in wall-clock time
4. Unlike the proposer stage (where consensus filters FPs via agreement), the verifier makes a binary judgement on a single crop — there is no "diversity dividend" to exploit

**Implementation**: `--iterations 1` default in `run_pv.py verify`

**Evidence**: Obs 167; `results/pv/phase1/pv-phase1-analysis.md`

---

## Decision 25: Moderate Consensus (3–5 of 10) as Recommended Proposer Strategy for PV

**Date**: 2026-03-21

**Decision**: Recommend 10 proposer passes with a 3-of-10 or 5-of-10 vote threshold, followed by a single verifier pass, as the optimal PV pipeline configuration. This achieves F1=0.823–0.831.

**Alternatives considered**:

- N=1 single pass + verifier (simpler, cheaper, F1 ≈ 0.77)
- N=30 strict consensus + verifier (expensive, HIGH thinking needed, F1 ≈ 0.79)
- N=30 loose union (1-of-30) + verifier (extreme recall but verifier can't filter enough FPs)

**Rationale**:

1. Moderate consensus (3-of-10) creates a "Goldilocks zone": enough agreement to filter single-run FPs, enough diversity to boost recall above N=1 (Obs 171)
2. Text 5-of-10 + PV achieves F1=0.831 — new project best, surpassing HIGH 25-of-30 consensus (F1=0.763) by +0.068
3. The approach uses 11 total API calls per tile (10 proposer + 1 verifier) vs 30 for the previous best — 63% fewer passes at 6.5× lower cost per tile (Obs 174)
4. No HIGH thinking required — minimal thinking throughout — further reducing per-call cost
5. Works with text-only examples (no image examples needed), the cheapest modality

**Implementation**: Documented in `results/pv/phase2/pv-phase2-analysis.md`

**Evidence**: Obs 170, 171, 174; `results/pv/phase2/pv-phase2-analysis.md`

---

## Decision 26: Retain Greedy-Ball Consensus Clustering as Primary; Validate via Weighted Boxes Fusion

**Date**: 2026-04-13

**Decision**: Retain the greedy-ball spatial clustering at a 20 m radius (implemented in `scripts/lib_consensus.py`, constant `DISTANCE_THRESHOLD_METRES = 20.0`) as the primary consensus-voting aggregation method for all preregistered phases (Phase 2a–2e, Phase 3a–3d, H10/H12, production run, generalisation run). Validate that the headline F1 results are robust to this implementation choice by replicating key analyses using Weighted Boxes Fusion (Solovyev et al. 2019, arXiv:1910.13302) adapted for multi-pass VLM detections. Recommend WBF as the preferred method for future work.

**Alternatives considered**:

- **Replace greedy ball with WBF wholesale**: re-run every preregistered phase, rewrite affected memos and observations, present WBF as the primary method with greedy ball as "historical" supplementary material. Rejected because (a) it would require explanation for every reader who checks against the prior observations and working notes, (b) it risks subtly breaking finalised figures and tables, and (c) it creates the appearance of a corrective methodology change when the statistical equivalence shows no correction is needed.
- **Retain greedy ball without a robustness check**: continue as-is with no WBF validation. Rejected because the audit process (Obs 228) surfaced legitimate concerns about the greedy-ball choice — it does not use the ensemble confidence signal (vote counts) during clustering, operates on centroid distance rather than spatial overlap (IoU), and produces duplicate candidates for ~11.6 % of ground-truth mounds due to centroid drift exceeding the 20 m radius. A reviewer familiar with the modern object-detection literature would ask about these issues, and a post-hoc robustness check is the right response.
- **Switch to WBF for H10/H12 and production only**: mixed methodology within the paper. Rejected because it creates a "why here but not there" question.

**Rationale**:

1. **The preregistration specifies the 20 m matching tolerance (Hungarian evaluation buffer) and the consensus voting framework (N passes, vote threshold sweep), but NOT the specific clustering algorithm that merges per-pass detections into voted candidates.** See `docs/methodology/preregistration/analysis-summary.md`. The clustering algorithm is implementation detail within the preregistered framework, so replacing it is not a protocol deviation — but retaining the original choice is also not a protocol obligation.
2. **Statistical equivalence validated** on the H10/H12 hp4hn4 configuration: paired permutation test across 327 test tiles with 10,000 iterations gave ΔF1 = 0.0053 (greedy minus WBF) with two-sided p = 0.6019. Bootstrap 95 % CIs for F1 overlap by ~97 % of their range (greedy [0.8483, 0.9165]; WBF [0.8452, 0.9108]). The tile-level disagreement is exactly symmetric: greedy wins 11 tiles, WBF wins 11 tiles, 305 tiles are exact F1 ties. On this representative config the two methods are statistically indistinguishable.
3. **Retaining greedy ball as primary preserves every prior result** without recomputation. Every F1 number in working notes, memos, and the paper draft remains valid as measured. The WBF replication is framed as methodological robustness, not corrective action.
4. **The methodology investigation itself is the rigor story**. The audit process (described in detail in Obs 228) discovered and documented the greedy-ball limitations, investigated the cartographic floor (68.1 m minimum GT separation), developed a principled alternative (WBF with vote-aware minimum separation anchored at the preregistered vote threshold), and validated statistical equivalence before committing to any change. This sequence is the paper's "due diligence" narrative.
5. **WBF as recommended future-work method**: Weighted Boxes Fusion is the established modern approach for ensemble-based object detection aggregation (standard in Kaggle object-detection competitions and production pipelines). It uses the per-detection confidence signal, operates on spatial overlap rather than centroid distance, handles the drift-fragment long tail principally, and automatically enforces the minimum inter-feature separation through the IoU metric. For any extension of this pipeline beyond the preregistered study, WBF is the correct default.

**Evidence**:

- **Investigation**: Obs 228 (upstream consensus dedup radius audit); Obs 229 (tile-boundary edge artefacts, separate finding)
- **Validation**: `results/h10/wbf/sweep_results_pool_160_hp4hn4_variant_c.json` (full (vote_t, prob_t) sweep); `results/h10/wbf/variant_c_vs_greedy_hp4hn4.json` (bootstrap CIs, paired permutation test)
- **Implementation**: `scripts/lib_fusion.py` (WBF library); `scripts/fuse_detections_wbf.py` (end-to-end runner); `scripts/sweep_f1_wbf.py` (F1 sweep); `scripts/compare_wbf_vs_greedy.py` (statistical comparison)
- **Tests**: `tests/test_lib_fusion.py` (33 tier-1 unit tests covering box IoU, size filtering, WBF clustering, vote-aware minimum-separation, end-to-end pipeline)

**Parameters of the WBF robustness implementation (Variant C)**:

- Algorithm: canonical Weighted Boxes Fusion (Solovyev et al. 2019) on the axis-aligned polygon bounding boxes returned by the proposer; no adaptation for point detections was needed
- Confidence weights: uniform (1.0) — the proposer returns categorical `"confidence": "high"` for every detection, so WBF's weighted averaging degenerates to arithmetic mean; vote count emerges as a cluster property used by the downstream vote filter
- IoU threshold for clustering: 0.25 (captures same-mound drift up to ~45 m centroid offset for 75 m diameter symbols, while keeping IoU at zero at the 68 m cartographic floor)
- Post-fusion minimum separation: 30 m, vote-aware with anchor threshold ≥ 6 (matches the preregistered F1-sweep optimal vote_t for H10/H12 greedy ball; only merges pairs where at least one cluster has vote_count ≥ 6, preventing spurious FP-fragment combination while absorbing tight drift into high-confidence cores)
- Box size filter: 20 m ≤ width, height ≤ 200 m; 400 m² ≤ area ≤ 40,000 m² (rejects pathological detections such as a 560 m wide outlier observed in the raw proposer output)
- Matching tolerance for downstream evaluation: **20 m Hungarian buffer, unchanged from the preregistration**

**Paper methods-section language (draft)**:

> Per-pass detections from the ten-pass proposer stage were aggregated into consensus candidates using greedy spatial clustering at a 20 m centroid-distance radius, feeding the preregistered Hungarian-matching evaluation at the same 20 m tolerance. To validate that the headline F1 results are not sensitive to the specific aggregation algorithm, we replicated the end-to-end analysis using Weighted Boxes Fusion (Solovyev et al. 2019) with an IoU threshold of 0.25 and a vote-aware minimum-separation post-step (30 m radius, anchor vote_count ≥ 6) derived from the empirical cartographic constraint that burial mound symbols are never closer than ~68 m on these Soviet topographic maps (minimum observed separation = 68.1 m in the 569-mound reference corpus; 1st percentile = 72.0 m). Paired permutation tests on the H10/H12 hp4hn4 configuration confirmed statistical equivalence (ΔF1 = 0.005, two-sided p = 0.60 at n = 10,000 permutations; bootstrap 95 % F1 CIs overlapping by ~97 % of their range). We recommend Weighted Boxes Fusion as the preferred aggregation method for future extensions of this pipeline, noting that it uses the ensemble vote signal during clustering, operates on spatial overlap rather than centroid distance, and handles drift-fragment aggregation more principally than the ad hoc greedy-ball approach.

**Scope of robustness-check replication** (pending decision on scale vs cost):

- **Required**: H10/H12 rollout to remaining 4 configs (hp2hn6, hp6hn2, hp8hn8, hp16hn16) at ~$7 API each = ~$28 total. Confirms the p=0.60 equivalence holds across the library-composition sweep.
- **Recommended**: Production run (4 maps, F1 = 0.885) WBF replication at ~$10 API. Directly validates the paper's headline number.
- **Optional**: Generalisation run (55 maps, F1 = 0.790 → D-S 0.808–0.814) WBF replication at ~$50–100 API. Strongest defence but substantial API spend.
- **Not required**: Phase 2a–2e or Phase 3a–3d replications. These are preregistered hypothesis tests whose validity does not depend on the clustering-algorithm choice, and the WBF replication on H10/H12 demonstrates equivalence at the aggregation level.

**Protocol classification**: **Not a protocol deviation** — the preregistration specifies the Hungarian matching tolerance and consensus voting framework but not the clustering algorithm. No erratum required.

**Related observations**: Obs 228 (investigation narrative); Obs 229 (edge artefact separate finding).

---

## Related Documents

- **Preregistration**: `preregistration.md` — Full study design
- **Working notes**: `docs/notes/reflections/working-notes.md` — Observations and evidence
- **Hypothesis tracking**: `hypothesis-tracking.md` — Condition mappings
- **Example manifest**: `inputs/examples/neutral-naming/MANIFEST.md` — Library composition
