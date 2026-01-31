# Decisions Log

**Purpose**: Document major methodological decisions and their rationale for the VLM burial mound detection study.

**Last updated**: 2026-01-22

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

**Date**: TBD (After Phase 1)

**Decision**: Select hard positives and hard negatives from Phase 1 baseline evaluation using frequency-based criteria.

### Hard Positive Selection

**Criteria** (from preregistration §8.4.2):

1. Run image-only baseline on 20 training tiles, K=10 passes
2. Identify False Negatives (ground truth mounds missed in ≥3/10 passes)
3. Rank by miss frequency (most frequently missed first)
4. Select top M as hard positives (M=4 for Scale-8 library)

**Purpose**: Teach model to recognise edge cases — genuine mound symbols that may be missed due to occlusion, degradation, or atypical appearance.

### Hard Negative Selection

**Criteria** (from preregistration §8.4.2):

1. Run image-only baseline on 20 training tiles, K=5 passes
2. Identify False Positives (detections with no ground truth match, occurring in ≥3/5 passes)
3. Rank by detection frequency (most frequently detected first)
4. Select top M as hard negatives (M=4 for Scale-8 library)

**Purpose**: Teach model to distinguish confusable symbols — map features that visually resemble mounds but are not.

### Legend-Derived Negatives

Two hard negatives can be specified before empirical analysis:

- Standalone triangulation point (no associated mound)
- Standalone benchmark (no associated mound)

These are categorised as `canonical_negative` in the library configs.

**Evidence**: Preregistration §8.4.2, preregistration-appendix-prompts.md.

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

## Future Decisions (TBD After Phase 1)

The following decisions will be documented after Phase 1 analysis:

- [ ] Specific hard positive examples selected (with source tile, coordinates, miss frequency)
- [ ] Specific hard negative examples selected (with source tile, coordinates, detection frequency)
- [ ] Any adjustments to library composition based on available hard examples
- [ ] Scale-32 feasibility (depends on number of distinct hard examples available)

---

## Related Documents

- **Preregistration**: `preregistration.md` — Full study design
- **Working notes**: `docs/notes/working_notes.md` — Observations and evidence
- **Hypothesis tracking**: `hypothesis-tracking.md` — Condition mappings
- **Example manifest**: `inputs/examples/neutral-naming/MANIFEST.md` — Library composition
