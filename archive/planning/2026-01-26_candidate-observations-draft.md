# Candidate Observations from Session Archive Mining

**Date**: 2026-01-26
**Purpose**: Draft observations for user review before integration into `working_notes.md`
**Status**: REVISED based on user feedback

---

## Summary

After user review and fact-checking against preregistration.md and pilot archives, the following observations have been:
- **RETAINED with corrections**: 66, 70, 71, 72, 73, 74, 76
- **DROPPED as premature**: 67, 68 (hypotheses under test, not confirmed)
- **REWRITTEN to correct confabulation**: 69, 75

**Final count**: 9 observations ready for integration (66-74, renumbered)

---

## RETAINED Observations

### Observation 66: Univariate Experimental Discipline ("One Dial at a Time")

**Date**: 2025-12-22 (Pipeline Development Session)

Throughout VLM tuning, a strict univariate search discipline was enforced: "again I'd like to only adjust one dial at a time as we search for optimal configuration." This principle was applied to temperature, prompt versions, and image library composition.

**Why this matters**: With multiple interacting parameters (temperature, prompts, image libraries, system instructions), changing multiple variables simultaneously makes it impossible to determine which change caused an effect. Univariate search, though slower, provides interpretable results essential for publication-quality claims.

**Implication**: This should be standard practice for VLM prompt engineering research. Papers that mention "prompt optimisation" rarely document their experimental strategy; this approach could set a methodological standard.

---

### ~~Observation 67~~ DROPPED

*Few-shot library saturation finding based on untrusted early Gemini 3 Pro results. Being re-tested in preregistered study.*

---

### ~~Observation 68~~ DROPPED

*Recency bias in example ordering is a hypothesis from published literature currently under test, not a confirmed finding from this project.*

---

### Observation 67 (renumbered): Underspecified Instructions and Model Corrigibility

**Date**: 2025-12-22 (Pipeline Development Session)

During preliminary work with Gemini 3 Pro in the Antigravity codebase, a subtle methodology drift occurred. After selecting designated training tiles for initial work, subsequent tasks began using underspecified references ("use the usual training tiles") rather than explicit tile identifiers ("use training tiles x, y, z..."). At some point, Gemini began silently selecting new tiles each task rather than maintaining consistency with prior selections.

This failure revealed important differences in model corrigibility:
- **Gemini 3 Pro**: Less tractable when given vague instructions; "drifted" from established conventions without flagging the issue
- **Claude Opus 4.5**: Earned trust over time by responding appropriately to vague or underspecified instructions, asking for clarification or maintaining consistency with established patterns

**Why this matters**: For research workflows requiring methodological consistency, explicit specification matters more with some models than others. The failure led to contaminated experiments and required a full methodology reset with designated training tiles and explicit random seeding.

**Implication**: Researchers should establish explicit naming conventions and document tile/sample identifiers rather than relying on contextual references, especially when working with less tractable models.

---

### Observation 68 (renumbered): Multi-Scale Tiling Trade-offs (Empirical Pilot)

**Date**: 2026-01-06 (Tile Size Pilot Session)

A calibration pilot comparing 256px, 512px, and 1024px tiles revealed unexpected trade-offs. Based on the "4-10% rule" (objects should occupy 4-10% of image dimensions), we expected 256px tiles to perform best since mound symbols are typically 10-20px, placing them squarely in the optimal range. Instead:

| Tile Size | Precision | Recall | F1 (2/5 voting) |
|-----------|-----------|--------|-----------------|
| 256px     | 0.098     | 0.854  | 0.175           |
| 512px     | 0.151     | 0.736  | 0.245           |
| 1024px    | 0.218     | 0.461  | 0.296 (at 4/5)  |

The 256px tiles achieved excellent recall but terrible precision (constant hallucinations). The 512px tiles provided the best single-scale balance. The 1024px tiles showed better precision but unacceptable recall (~37%), limiting their value even for the intended verifier role in proposer-verifier pipelines.

**Why this matters**: Literature predictions from CNN-based computer vision may not transfer directly to VLMs, which process images through fundamentally different mechanisms (hierarchical tiling, internal rescaling).

**Implication**: Tile size should be treated as an empirical design parameter requiring calibration, not derived a priori from object size ratios.

---

### Observation 69 (renumbered): Multi-Scale Voting Shows Asymmetric Complementarity

**Date**: 2026-01-06 (Tile Size Pilot Session)

Analysis of 10 multi-scale voting strategies (documented in `archive/pilot-tile-size/results/multiscale-voting-analysis.md`) revealed that simple pooling across scales performs worse than single-scale optimal configurations. The key insight: scales show **asymmetric complementarity rather than balanced redundancy**:

- Small tiles (256px) detect ~95% of mounds but with only ~10% precision
- Large tiles (1024px) achieve ~30% precision but miss ~63% of mounds
- Error correlation across scales was low to negative, supporting the theoretical basis for multi-scale fusion
- Multi-scale confidence fusion strategies showed modest F1 improvement (0.61 vs 0.49 single-scale) but at significant computational cost

**Why this matters**: The fundamental constraint is that large-tile low recall means confirmation signals are unavailable for most true positives detected by smaller tiles. This creates a recall cost that may exceed precision gains.

**Implication**: Multi-scale ensemble voting, while theoretically appealing, may not generalise to sparse-feature detection tasks where scales have fundamentally different accuracy characteristics. Multi-scale fusion has been designated as exploratory analysis for Paper 2, contingent on validation with a larger ground truth set.

---

### Observation 70 (renumbered): Sequential Design with Embedded Factorial

**Date**: 2026-01-17 (Phase 2 Execution Planning)

The preregistration underwent significant restructuring from an initial balanced factorial design (potentially 50+ cells) to a streamlined **sequential design with embedded factorial**, totalling 26 core confirmatory cells (Section 8.4.7 of preregistration.md).

The design chains stages together, with optimal parameters carried forward:

| Stage | Hypothesis | Structure | Cells |
|-------|------------|-----------|-------|
| 1 | H1 (M/E level) | One-way (3 levels) | 3 |
| 2 | H7 (temperature) | One-way (5 levels) at optimal M/E | 5 |
| 3 | H8 (library) | Sequential addition (7 levels) at optimal M/E + temp | 7 |
| 4 | H5 (negative text) | **3×3 factorial (M/E × H5)** at optimal temp + library | 9 (6 new) |
| 5 | H4 (ordering) | One-way (3 levels) at optimal M/E | 3 |

Most stages use OFAT (one-way comparisons), but H5 uses a small **2-way factorial** to test the M/E × H5 interaction—whether the effect of negative text guidance varies by modality/elaboration level. This interaction is theoretically important and worth the additional cells.

**Why this matters**: Pure factorial designs become infeasible with limited budgets and many factors. The hybrid approach uses OFAT where factors are expected to be independent, but embeds small factorials where interactions are theoretically important.

**Implication**: This illustrates practical tension between experimental purity and budget realism in frontier model research. The design prioritises statistical power for main effects while preserving interaction testing only where theoretically motivated. 

---

### Observation 71 (renumbered): Thinking Level Efficiency in Frontier Models

**Date**: 2026-01-17 (OSF Preparation Sessions)

This investigation was prompted by a Substack essay on LLM-based handwriting recognition, which found that lower thinking levels (and temperatures) produced better results for visual pattern recognition tasks.

Calibration testing three "thinking level" settings in Gemini 3 Flash (minimal, medium, high) confirmed similar findings for symbol detection:
- Minimal thinking: Fastest inference, equivalent F1 to high thinking
- Medium/high thinking: 2-3× slower with no F1 improvement

Result: All Gemini configs set to `thinking_level: minimal` to reduce cost and latency without sacrificing accuracy. This was treated as **infrastructure configuration** rather than an experimental factor—something to calibrate once and fix, not vary as part of the study.

**Why this matters**: Frontier models' extended thinking features are motivated by complex reasoning tasks (multi-step logic, mathematical proofs). For symbol detection—which requires pattern recognition rather than multi-step reasoning—extended thinking appears computationally wasteful.

**Implication**: Thinking-level settings should be task-dependent. Practitioners should run calibration pilots to determine optimal infrastructure configuration before running the main study, rather than assuming vendor defaults are optimal.

---

### Observation 72 (renumbered): Prompt Orthogonality and Quality Audit

**Date**: 2026-01-19 (Prompt Template Implementation)

During implementation of the factorial design, several issues emerged with prompt text:

1. **Orthogonality violations**: To test factors independently (e.g., H5 negative text guidance orthogonal to H1 modality), identical base text must appear across conditions. Initial implementations had subtle variations that would confound factor effects.

2. **Quality issues**: Many prompt variants had been composed with Gemini's assistance during preliminary work. Systematic review diagnosed them as suboptimal—unnecessary role framing, insufficient length difference between terse and verbose variants.

3. **Structural solution**: Variation is now controlled through discrete filename suffixes (`_terse`, `_verbose`) rather than mixing guidance into base text. All prompts were revised for consistency and quality, not just H5 variants.

**Why this matters**: Prompting strategies can interact in complex ways. Factorial orthogonality in prompt engineering requires careful structural design where effects attributed to one factor aren't confounded with another.

**Implication**: When designing factorial experiments on prompt variants, audit all prompts for both orthogonality (identical base text where required) and quality (clear, consistent instruction structure). AI-assisted prompt drafting may require human review and revision.

---

### ~~Observation 75~~ REWRITTEN

*Original claimed H2 and H9 were reclassified from confirmatory to exploratory. Fact-check against preregistration.md shows: H2 (two-stage) remains **Confirmatory**; H9 (diversity mechanisms) was always **Exploratory (Tier A)**. The original observation was incorrect.*

### Observation 73 (renumbered): Preregistration as Living Document with Version Control

**Date**: 2026-01-17 (Phase 2 Execution Planning)

The preregistration document (now at v4.4) has undergone substantial revision through the planning process, with explicit changelog entries documenting each modification. Key evolution patterns:

- **Hypothesis refinement**: Predictions sharpened based on pilot results (e.g., H2 now explicitly notes 1024px tiles achieve only 37% recall, limiting confirmation value)
- **Terminology standardisation**: Multiple passes to ensure consistent use of abbreviations (Canon+, Canon-, HP, HN) and terminology (elaborate → verbose)
- **Cross-reference corrections**: Systematic audit caught references to wrong hypothesis numbers or sections after renumbering
- **Implementation alignment**: Explicit hypothesis-to-config mapping tables to ensure experimental configs match documented conditions

**Why this matters**: Preregistration is often presented as a one-time document. In practice, refining a preregistration through pilot testing and implementation planning improves its quality—provided changes are version-controlled and justified.

**A notable aspect of this project**: The degree of front-loading was unusual. Before running the main study, the research involved: carefully creating and reviewing hypotheses, determining statistical approaches, writing all scripts, testing infrastructure, running calibration pilots, and conducting dry-run simulations. Throughout this process, the preregistration document served as the touchstone—the central reference point that all other work aligned to.

**Current status**: At time of writing, the preregistration has not yet been submitted to OSF, but all revisions have been captured in git version control with explicit changelog entries. OSF submission is the next step before running the preregistered experiment.

**Implication**: Treat preregistration as a living document during the planning phase. Use version control with explicit changelog entries. Freeze the document only when registering at OSF, then report any post-registration deviations transparently.

---

### Observation 74 (renumbered): Calibration Pilots as Integral Design Elements

**Date**: 2026-01-17 (OSF Preparation Sessions)

The project integrated two distinct calibration pilots into the formal study design before the main preregistered experiment:

1. **Tile-size pilot** (256/512/1024px): Tested primary methodological choice with preregistered decision algorithm. Results informed the choice of 512px as the standard tile size.

2. **Thinking-level pilot** (minimal/medium/high): Optimised computational efficiency by comparing Gemini inference modes. Results informed the decision to use minimal thinking.

These pilots were specified in Phase 0 of the execution plan with explicit procedures and success criteria, not treated as ad-hoc pre-study optimisation. A third pilot (reference example selection via hard-negative mining) is planned as Phase 1 of the preregistered experiment itself.

**Why this matters**: Frontier VLM behaviour is not well-characterised across diverse tasks. Calibration pilots reduce risk by validating key design choices before committing to full factorial evaluation.

**Implication**: For methods papers on using frontier models, this illustrates how careful design can incorporate exploration without compromising preregistration integrity. Pilots test design assumptions; the preregistered study then tests hypotheses about prompting factors.

---

## Summary Table: Final Observations for Integration

| New # | Topic | Key Insight |
|-------|-------|-------------|
| 66 | Univariate discipline | "One dial at a time" for interpretable results |
| 67 | Model corrigibility | Gemini 3 Pro drifted from underspecified instructions; Opus 4.5 maintained consistency |
| 68 | Tile size trade-offs | 256px expected best (4-10% rule) but 512px optimal; predictions didn't transfer to VLMs |
| 69 | Multi-scale asymmetry | Scales show asymmetric complementarity; multi-scale voting deferred to exploratory |
| 70 | Sequential design with embedded factorial | Mostly OFAT, but 3×3 factorial for M/E × H5 interaction; optimal params carried forward |
| 71 | Thinking level efficiency | Minimal = high thinking for symbol detection; infrastructure config, not experimental factor |
| 72 | Prompt orthogonality audit | All prompts revised for orthogonality and quality; AI-drafted prompts needed revision |
| 73 | Preregistration as touchstone | Living document through extensive front-loading; git version control until OSF freeze |
| 74 | Calibration pilots | Tile-size and thinking-level pilots as infrastructure config before main study |

---

## Next Steps

1. User confirms these 9 observations are ready for integration
2. Add to `working_notes.md` Part 1, continuing from Observation 65
3. Archive this planning document

---

*Revised 2026-01-26 based on user feedback. Original confabulations corrected; premature hypotheses dropped.*
