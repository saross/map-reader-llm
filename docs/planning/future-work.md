# Future Work & Remaining Tasks

This document tracks implementation tasks and stretch goals for the Map Reader LLM project.

**Last Updated**: 2026-01-19

> **Note**: Hypothesis testing is now formalised in the preregistration document (`docs/methodology/preregistration/osf/preregistration.md`; lodged 2026-01-31 as v4.7 content). This document covers implementation-specific tasks and exploratory ideas not in the preregistration.

---

## Status: Preregistration Complete

All 15 hypotheses are formalised in the preregistration (lodged v4.7 content, 2026-01-31; hypothesis content changed substantially after v4.2). The sequential OFAT design tests factors one at a time, carrying optimal parameters forward.

| Hypothesis | Description | Phase |
|------------|-------------|-------|
| H1 | Modality/Elaboration level (5 levels) | 2a |
| H2 | Two-stage pipelines | 3c |
| H3 | Consensus voting thresholds | 3a |
| H4 | Example ordering (canonical placement) | 2e |
| H5 | Negative text treatment (3 levels) | 2d |
| H6 | Flash→Pro transfer | 4 |
| H7 | Temperature (4 levels) | 2b |
| H8 | Library composition and scaling | 2c |
| H9 | Diversity mechanisms | 3b |
| H10 | Training pool size | 5 |
| H11 | Tile size effects | 5 |
| H12 | Hard positive to hard negative ratio | 5 |
| H13 | Overlap/stride effects | 5 |
| H14 | Cross-model consistency | 5 |
| H15 | Cross-model consensus voting | 5 |

**See**: `docs/methodology/preregistration/execution-plan.md` for full timeline.

---

## Deferred Implementation Tasks

### Multi-Provider API Clients

| Provider | Client | Status |
|----------|--------|--------|
| Google (Gemini) | `google-generativeai` | ✅ Implemented |
| Anthropic (Claude) | `anthropic` | ⏸️ Deferred |
| OpenAI (GPT) | `openai` | ⏸️ Deferred |

Non-Gemini API clients deferred until needed for H6/H14 (Phase 4-5).

**Claude adaptation notes** (for future reference):

- Multimodal API uses base64 image encoding
- System prompt in separate `system` parameter
- Different token counting

**OpenAI adaptation notes** (for future reference):

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

### 3.4 Null Tile Count and Negative Example Composition

Null tiles (currently fixed at 3 per library) were introduced as necessary
infrastructure — without them the model generates detections until output tokens
fill up. This is well-attested in traditional CV/ML literature (training sets need
negative examples), and 3 is relatively few by ML standards. However, the Phase 2c
P:N ratio analysis (see `reports/phase2c-pn-ratio-analysis.md`) revealed that
negative example *composition* matters more than negative example *count*:

- Canon- examples (clear, informative negatives) redirect false positives to true
  positives when paired with hard positives
- Hard negatives (ambiguous, near-boundary negatives) degrade performance regardless
  of context
- Null tiles provide no discriminative information but are functionally necessary

**Open questions**:

1. Is 3 nulls the right count, or would fewer (1-2) or more (4-5) change results?
2. Does the Canon- + null combination represent a "sweet spot" for negative
   composition, or would Canon- alone (without nulls) work if the model's runaway
   detection behaviour has been addressed by other prompt changes?
3. Can the original runaway detection effect (pre-null) be reproduced under
   controlled conditions to confirm it's still active?

**Motivation**: The 2x2 HP x Canon- interaction analysis showed that both factors
reverse their effect depending on the other's presence. Null tiles may participate
in a similar three-way interaction that is currently invisible because null count
has been held constant.

**Design**: OFAT probe varying null count (0, 1, 3, 5) at the plus-hp library
composition (the current optimum). ~4 cells, cost ~$44 at current rates. Deferred
until after other parameters (modality, text treatment, ordering) are finalised.

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

### Pipeline Preparation (2026-01)

- [x] **Tile selection complete** (2026-01-03): 20 calibration + 60 holdout tiles with documented seeds
- [x] **Instruction files finalised** (2026-01-14): 13 detection/two-stage instruction files
- [x] **Config files created** (2026-01-14): 24 JSON configs for M/E levels, H5 variants, libraries
- [x] **Thinking pilot calibration** (2026-01-15): Minimal thinking achieves equivalent F1 at 1/3 latency
- [x] **End-to-end pipeline verified**: Batch detection scripts working with Gemini Flash/Pro
- [x] **Results directory initialised** (2026-01-19): Structure per execution plan

### Preregistration & Documentation (2026-01)

- [x] **Preregistration finalised** (lodged 2026-01-31, v4.7 content): All 15 hypotheses defined
- [x] **Execution plan created**: Phased OFAT implementation timeline
- [x] **Prompts appendix aligned**: All instruction and config files documented

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
