# Future Work & Remaining Tasks

This document tracks methodological tasks, experiments, and stretch goals for the Map Reader LLM project.

**Last Updated**: 2025-12-22

---

## Priority 1: Immediate Implementation Tasks

### 1.1 Fix v4.x Two-Stage Verification Bugs

**Status**: Ready to implement
**Priority**: High
**Discovered**: 2025-12-22 (Code review session)

The v4.x two-stage pipeline (F1 0.716, P=0.97, R=0.57) underperforms due to implementation bugs, not architectural limitations.

**Critical bugs identified:**

1. **Missing instruction file** (`prompts/versions/v4.6_verifier.json:4`)
   - Config references `"instruction_file": "v4.6_verifier_instructions.md"`
   - File does not exist in `prompts/text/`
   - Causes fallback to basic 12-line default prompt in `scripts/5_verify_crops.py:126-141`
   - **Fix**: Create `prompts/text/v4.6_verifier_instructions.md` with proper visual chain-of-thought instructions

2. **Contradictory example labels** (`prompts/versions/v4.6_verifier.json:13-24`)
   - `benchmark_mound.png` labelled as "Negative Example: Hard Benchmark"
   - `triangulation_mound.png` labelled as "Negative Example: Hard Triangulation"
   - These ARE positive examples (mounds with survey markers)
   - This teaches the verifier to reject valid detections, explaining the 0.57 recall
   - **Fix**: Change labels to "Positive Example: Benchmark on Mound" etc.

3. **Unused config flags** (`prompts/versions/v4.6_verifier.json`)
   - `"visual_cot": true` and `"confidence_rubric": "explicit"` are defined but never read by `5_verify_crops.py`
   - **Fix**: Either implement flag handling or remove dead config

4. **Temperature 0.0 may be suboptimal**
   - Deterministic output prevents stochastic voting benefits
   - Consider temperature 0.3-0.5 for light variation

**Expected outcome**: With fixes applied, two-stage should approach consensus performance (F1 ~0.90) while maintaining high precision (P≥0.95).

---

### 1.2 Investigate v3.5 Flash Swarm Collapse

**Status**: Root cause identified (2025-12-22)
**Priority**: High
**Reference**: Observation 45 in `docs/working_notes.md`

**The paradox:**
- v3.2 (Text+Image) Flash Swarm N=30: F1 0.920 (excellent)
- v3.5 (Image-Only) Flash Swarm N=30: F1 0.000 (2,327 hallucinations)

**Root Cause Analysis (COMPLETED)**:

The original comparison was **not controlled**. Two variables differed simultaneously:

| Parameter | v3.2 Swarm (F1 0.92) | v3.5 Swarm (F1 0.00) |
|-----------|----------------------|----------------------|
| **Temperature** | **0.3** | **1.0** |
| Text scaffolding | "No Spikes = No Mound" rules | Minimal (27 lines) |
| Verbose neg labels | "NO MOUNDS." (emphatic) | "No Mounds" (passive) |
| Detections/run | ~59 | ~86 (more hallucinations) |

Source: Meta files at:
- `outputs/results/v3.2_experimental/variability_study_v3.2_flash_30_run_01.meta.json`
- `outputs/results/v3.5_clean/flash_swarm_replay_temp1_run_01.meta.json`

**Conclusion**: The collapse was caused by **both** factors:
1. Temperature 1.0 introduces excessive stochasticity
2. No text rails means Flash has no anchor to suppress hallucinations

**Next Steps (Controlled Experiments)**:
- [ ] Test v3.5 at temperature **0.3** (isolate text effect)
- [ ] Test v3.2 at temperature **1.0** (isolate temperature effect)
- [ ] If v3.5 @ 0.3 works: Text is unnecessary, just use lower temperature
- [ ] If v3.5 @ 0.3 fails: Text scaffolding is essential for Flash stability

---

## Priority 2: Optimisation Tasks

### 2.1 Tune v3.2 and v3.5 Prompts

**Status**: Pending
**Goal**: Find optimal scaffolding balance

- Test systematic variations:
  - Text-only, Image-only, Text+Image hybrids
  - Different instruction lengths
  - Alternative phrasing for detection criteria
- Document what text is essential vs. harmful (modality interference)

### 2.2 Optimise Few-Shot Image Libraries

**Status**: Pending
**Goal**: Statistically select optimal example sets

- Current approach: Manual curation of 16-48 examples
- Proposed approach:
  - Bootstrap sampling of example subsets
  - Measure per-example contribution to F1
  - Identify high-value and harmful examples
  - Implement ablation study automation

### 2.3 Experiment with Training Dataset Sizes

**Status**: Pending
**Current**: 20 tiles (~5% of corpus)

- Test hypotheses:
  - Is 20 tiles sufficient for generalisation?
  - What's the learning curve shape?
  - Diminishing returns threshold?
- Expand to 40, 80, 160 tiles if variance remains high

---

## Priority 3: Multi-Provider Support

### 3.1 Add Anthropic Model Support

**Status**: Pending
**Models**: Claude Sonnet 4, Claude Opus 4.5

- Implement Anthropic API client in detection pipeline
- Adapt prompt format for Claude's multimodal interface
- Test single-shot and consensus strategies
- Compare cost/performance ratios

### 3.2 Add OpenAI Model Support

**Status**: Pending
**Models**: GPT-4o, GPT-4-Vision

- Implement OpenAI API client
- Adapt prompt format for OpenAI's vision interface
- Test and benchmark

### 3.3 Cross-Provider Consensus Voting

**Status**: Pending
**Goal**: Test whether diverse models improve consensus

- Hypotheses:
  - Mixed-provider ensemble may reduce correlated errors
  - "Wisdom of crowds" across different training regimes
- Experiments:
  - Gemini Pro + Claude Sonnet + GPT-4o consensus
  - Compare to single-provider 3/3 consensus

---

## Priority 4: Advanced Techniques

### 4.1 Explore Additional Improvement Techniques

**Status**: Pending
**Ideas to investigate:**

- **Chain-of-thought variations**: Test explicit reasoning steps vs. direct detection
- **Self-consistency decoding**: Multiple reasoning paths, majority vote on answer
- **Calibration**: Adjust confidence thresholds based on validation set
- **Active learning**: Prioritise ambiguous cases for human review
- **Hard negative mining automation**: Systematic FP analysis pipeline

---

## Stretch Goals

### S1. Automated Map-to-Reader Pipeline

**Status**: Stretch goal
**Goal**: Zero-shot generalisation from legend to detection

**Vision**: Given a new map sheet with its legend, automatically:
1. Extract symbol definitions from legend
2. Generate appropriate few-shot examples
3. Construct detection prompt
4. Run detection without human prompt engineering

**Research questions:**
- Can LLMs learn symbol patterns from legend crops alone?
- What legend quality/resolution is required?
- Can we bootstrap from a "meta-prompt" describing how to read legends?

---

## Completed Tasks

### Methodological Records
- [x] **Log Retention Strategy**: `~/.gemini/antigravity/` logs reviewed, methodology archived.

### Open Science Standards
- [x] **FAIR4RS Compliance**: Repository upgraded to meet FAIR principles.
  - [x] Add `CITATION.cff`
  - [x] Ensure comprehensive licence coverage
  - [x] Improve documentation for reusability

### Analysis & Documentation
- [x] **v4.x Implementation Review** (2025-12-22): Identified root cause of two-stage underperformance (bugs, not architecture).

---

## Reference: Current Performance Baselines

| Strategy | Model | F1 | Precision | Recall | Notes |
|----------|-------|-----|-----------|--------|-------|
| v3.2 Swarm 10/30 | Flash | **0.920** | 0.92 | 0.92 | Current ceiling |
| v3.5 Consensus 2/5 | Pro | **0.914** | 0.914 | 0.914 | SOTA recommendation |
| v3.5 Single | Pro | 0.886 | 0.877 | 0.894 | Strong baseline |
| v4.6 Verifier | Pro | 0.716 | **0.970** | 0.57 | Precision specialist (buggy) |
| v3.5 Swarm 30 | Flash | 0.000 | 0.00 | 0.00 | Collapsed (needs investigation) |

**Target**: Reproducible F1 > 0.90 across strategies and providers.
