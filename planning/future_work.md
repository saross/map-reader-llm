# Future Work & Remaining Tasks

This document tracks implementation tasks and stretch goals for the Map Reader LLM project.

**Last Updated**: 2026-01-08

> **Note**: Hypothesis testing is now formalised in the preregistration document (`docs/methodology/preregistration/preregistration.md` v4.2). This document covers implementation-specific tasks and exploratory ideas not in the preregistration.

---

## Status: Preregistration Complete

The following areas from earlier planning are now addressed by the preregistration:

| Earlier Task | Preregistration Coverage |
|--------------|-------------------------|
| Text vs image modality effects | H1 (M/E factor: 5 levels) |
| Text elaboration (brief vs verbose) | H2 (text elaboration) |
| Two-stage pipeline | H2 (two-stage confirmatory) |
| Voting/consensus strategies | H3 (voting threshold) |
| Example ordering | H4 (canonical-first/last/random) |
| Hard negatives | H5 (3 levels: None/Images-only/Text+Images) |
| Model selection | H6 (4 models), H14 (architecture transfer) |
| Temperature optimisation | H7 (4 levels: 0.0, 0.7, 1.0, 1.3) |
| Library size | H8 (training pool size) |
| Hard positives | H9 (exploratory) |
| Multi-scale detection | H10 (tile size pilot) |

**See**: `docs/methodology/preregistration/execution-plan.md` for implementation timeline.

---

## Implementation Tasks (Pre-Execution)

### 1.1 Pipeline Preparation

**Status**: Pending
**Priority**: High

Before executing the preregistration:

- [ ] Verify all 26 config files exist and are correct
- [ ] Verify all 10 instruction files match preregistration appendix
- [ ] Test pipeline end-to-end on a single tile
- [ ] Confirm API clients work for all 4 models (Gemini Flash, Gemini Pro, Claude Sonnet, GPT-5.2)
- [ ] Set up results directory structure per execution plan

### 1.2 Tile Selection (Phase 1)

**Status**: Pending
**Reference**: `scripts/select_tiles_phase2.py`

- [ ] Finalise Phase 1 stratified tile selection (60 development tiles)
- [ ] Generate tile bounds files
- [ ] Verify ground truth annotations for selected tiles

---

## Multi-Provider Implementation

### 2.1 API Client Status

| Provider | Client | Status |
|----------|--------|--------|
| Google (Gemini) | `google-generativeai` | ✅ Implemented |
| Anthropic (Claude) | `anthropic` | ❌ Pending |
| OpenAI (GPT) | `openai` | ❌ Pending |

### 2.2 Provider-Specific Adaptations

**Claude adaptation notes:**
- Multimodal API uses base64 image encoding
- System prompt in separate `system` parameter
- Different token counting

**OpenAI adaptation notes:**
- Vision API uses URL or base64 images
- Different response format

---

## Exploratory Ideas (Post-Preregistration)

These are not in the preregistration but may be worth exploring:

### 3.1 Cross-Provider Ensemble

Test whether mixing models improves consensus:
- Gemini Pro + Claude Sonnet + GPT-4o consensus
- Compare to single-provider consensus

### 3.2 Automated Hard Negative Mining

Systematic FP analysis pipeline:
- Cluster FPs by visual similarity
- Generate hard negative categories automatically
- Feed back into prompt library

### 3.3 Active Learning Loop

Prioritise ambiguous cases for human review:
- Identify low-confidence detections
- Request human annotation
- Update training set iteratively

---

## Stretch Goals

### S1. Automated Map-to-Reader Pipeline

**Goal**: Zero-shot generalisation from legend to detection

Given a new map sheet with its legend, automatically:
1. Extract symbol definitions from legend
2. Generate appropriate few-shot examples
3. Construct detection prompt
4. Run detection without human prompt engineering

---

## Completed Tasks

### Preregistration & Documentation (2026-01)
- [x] **Preregistration finalised** (v4.2): All 15 hypotheses defined
- [x] **Execution plan created** (v2.5): Phased implementation timeline
- [x] **Prompts appendix aligned** (v2.6): All instruction and config files documented
- [x] **Prompt library standardised**: 10 instruction files, 26 config files

### Methodological Records (2025-12)
- [x] **Log Retention Strategy**: `~/.gemini/antigravity/` logs reviewed, methodology archived
- [x] **v4.x Implementation Review**: Identified root cause of two-stage underperformance

### Open Science Standards (2025-12)
- [x] **FAIR4RS Compliance**: Repository upgraded to meet FAIR principles
  - [x] Add `CITATION.cff`
  - [x] Ensure comprehensive licence coverage
  - [x] Improve documentation for reusability

---

## Reference: Pre-Preregistration Performance Baselines

> **Note**: These baselines are from exploratory v3.x/v4.x experiments (Dec 2025) before the preregistration was finalised. They use different prompt configurations than the preregistered conditions.

| Strategy | Model | F1 | Precision | Recall | Notes |
|----------|-------|-----|-----------|--------|-------|
| v3.2 Swarm 10/30 | Flash | **0.920** | 0.92 | 0.92 | Text+Image, T=0.3 |
| v3.5 Consensus 2/5 | Pro | **0.914** | 0.914 | 0.914 | Image-only, T=1.0 |
| v3.5 Single | Pro | 0.886 | 0.877 | 0.894 | Image-only baseline |
| v4.6 Verifier | Pro | 0.716 | **0.970** | 0.57 | Two-stage (had bugs) |

**Preregistered target**: F1 ≥ 0.85 on holdout set with optimal configuration.
