# Methods Section Outline

Draft outline for the methods section of a journal article reporting the
VLM burial mound detection study. Structured to reflect the preregistered
design while transparently documenting deviations.

Key methodological decisions include: (1) **model selection** — use of Gemini 3 Flash (Google's `gemini-3-flash-preview`) as a cost-effective, free-tier model with sufficient capability for detection tasks at consensus scales up to K=30; (2) **design strategy** — sequential One-Factor-At-A-Time (OFAT) design with adaptive dual-track extension to preserve preregistered pipeline scope while exploring unexpected findings; (3) **spatial tolerance** — 20 m matching threshold to account for georeferencing error, symbol centroid ambiguity, and map digitisation precision; (4) **consensus voting approach** — pooling K=10–30 independent runs with cross-pass clustering and optimal threshold identification to improve precision through diversity; (5) **two-stage proposer-verifier approach** — high-recall proposer pass followed by independent verification of candidates with diagnostic checklists and voting thresholds; (6) **statistical methods** — 95% bootstrap confidence intervals (1,000 iterations) with Benjamini-Hochberg FDR correction across confirmatory hypotheses; and (7) **matching algorithm** — Hungarian algorithm for globally optimal one-to-one spatial assignment to prevent double-counting. A dedicated subsection (§6.3) documents the human–LLM collaborative development process, drawing on 50+ archived session transcripts and structured reflections to demonstrate how AI-assisted research methodology enabled systematic implementation at scale while preserving human scientific judgement.

**Status**: Outline only — not yet prose. Intended as a scaffold for
collaborative drafting.

---

## 1. Study Design Overview

- Preregistered, stranded-factorial study (OSF registration, 2026-01-31)
- 15 hypotheses: 8 confirmatory (H1–H8), 7 exploratory (H9–H15)
- Sequential One-Factor-At-A-Time (OFAT) design with carry-forward of
  optimal parameters between phases
- Rationale for OFAT over full factorial: cost constraint (~$250 budget
  ceiling; full factorial would require ~54+ cells × 10 runs × 60 tiles)
- **Adaptive protocol extension**: dual-track carry-forward after Phase 2a
  (see §4.1) — additive to preregistered design, not a substitution

## 2. Study Area and Materials

### 2.1 Cartographic Sources

- Four Soviet 1:50,000 topographic map sheets of Bulgaria (Thracian
  Plain / eastern Thrace region)
  - K-35-052-4 (32635), K-35-053-3 (Elenovo), K-35-062-2 (Rakovski),
    K-35-078-1 (Lesovo)
- Coordinate reference system: EPSG:32635 (UTM Zone 35N)
- Pixel resolution: ~5.02 m/pixel at native scan resolution
- Target features: burial mound symbols (sunburst pattern with radiating
  hachures) — a standardised Soviet cartographic convention

### 2.2 Tile Generation

- 512 × 512 pixel tiles with 64-pixel overlap (stride 448 px)
- Content threshold: tiles with >75% background filtered out
- Total corpus: 361 tiles across 4 map sheets
- Each tile covers approximately 2.57 × 2.57 km on the ground

### 2.3 Ground Truth

- 569 annotated mound symbols across the full corpus
- Initial annotation by students using FAIMS v2.6 mobile data capture
  application
- Comprehensive expert review and verification by primary researcher
- Symbol categories: burial mounds, settlement mounds, and mounds with
  benchmarks or triangulation points (all treated as positive detections)
- Reference data stored as GeoJSON (EPSG:32635)

### 2.4 Data Allocation

- **Training/calibration set**: 20 tiles (5 per map sheet) — used for
  prompt development and hard example selection (contaminated, excluded
  from evaluation)
- **Holdout evaluation set**: 60 tiles (15 per map sheet, stratified by
  density: 30 empty, 18 sparse [1–2 mounds], 12 dense [3+]) — 79 mound
  symbols; used for all confirmatory and most exploratory tests
- **Reserve pool**: 281 tiles — untouched, reserved for future Stage 2
  validation
- Tile selection stratified by mound density with documented random seeds

## 3. VLM Detection Pipeline

### 3.1 Model

- Gemini 3 Flash (Google; model identifier `gemini-3-flash-preview`)
- All runs used `thinking_level: minimal` unless explicitly testing
  thinking level as a factor (Phase 3a replication)
- Rationale for single-model focus: free-tier access, sufficient
  capability for detection task, cost-effective at K=30 consensus scale

### 3.2 Prompt Architecture

- **System instruction**: task definition, target symbol description,
  output format specification (JSON with normalised 0–1000 coordinates)
- **Few-shot examples**: configurable library of labelled example tiles
  (positive, negative, null categories) — images and/or text
  descriptions depending on modality condition
- **Target tile**: 512 × 512 px PNG tile as final input
- Multimodal content assembled via google-genai SDK (v1alpha) as
  sequential `types.Part` objects
- Forced JSON output via `response_mime_type="application/json"`
- Maximum output tokens: 8192 (accommodates thinking tokens + detection
  JSON)

### 3.3 Experimental Factors

Brief table of the factors manipulated across phases:

| Factor | Abbrev. | Levels | Phase |
|--------|---------|--------|-------|
| Modality/Elaboration | M/E | 5: image-only, brief-text, brief-text+image, verbose-text, verbose-text+image | 2a |
| Temperature | T | 5: 0.0, 0.3, 0.7, 1.0, 1.3 | 2b |
| Library composition | Lib | 7: pure-positive-canon through scale-32 | 2c |
| Negative text treatment | H5 | 3: minimal, terse, verbose | 2d |
| Example ordering | Ord | 4: config-default, canonical-first, canonical-last, random | 2e |
| Consensus voting pool | N | 3: 5, 10, 30 | 3a |
| Two-stage pipeline | PV | single-stage vs proposer–verifier | 3d |

### 3.4 Output Processing

- VLM returns JSON array of detections with normalised bounding-box
  coordinates (0–1000 scale)
- Coordinates converted: normalised → pixel → UTM via tile
  georeferencing
- Detections saved as GeoJSON features per tile, incrementally (enables
  resume on failure)

### 3.5 Two-Stage Proposer–Verifier Pipeline (H2)

- **Proposer**: high-recall detection pass (standard pipeline with
  recall-optimised prompt)
- **Verifier**: each candidate cropped from original raster at higher
  resolution; verified independently via VLM with diagnostic checklist
  prompt
- Multiple verification iterations (K=5) with voting threshold
- Tested as exploratory hypothesis; preregistered as expected null
  (single-stage ≥ two-stage)

### 3.6 Consensus Voting Mechanism (H3)

- **Within-pass deduplication**: greedy clustering at 20 m tolerance
  removes duplicates from overlapping tiles within a single detection
  pass
- **Cross-pass clustering**: pool deduplicated detections from K passes;
  cluster across passes at 20 m Euclidean distance; count distinct
  passes per cluster
- **Vote threshold**: retain clusters where vote count ≥ T; sweep all T
  ∈ [1, K] to identify optimal threshold
- Voting tested at multiple temperatures (T=0.0, 0.3, 0.7) and pool
  sizes (N=5, 10, 30)

## 4. Execution Protocol

### 4.1 Sequential OFAT with Dual-Track Protocol Extension

**Preregistered design**: single carry-forward path; each phase
determines the optimal level of one factor, which is fixed for all
subsequent phases.

**Adaptive extension (Erratum E27)**: Phase 2a revealed that the
text-only condition (`brief-text`, F1=0.543) outperformed the best
image-using condition (`brief-text-image`, F1=0.462) by +0.08 F1. This
contradicted the foundational assumption that visual few-shot examples
would enhance detection. Strictly following the preregistered
carry-forward rule would have selected text-only as the winner, rendering
Phases 2c (library composition) and 2e (example ordering) inapplicable
since those factors only operate on image-based examples.

**Resolution**: rather than truncating the preregistered pipeline, we
extended the protocol to carry forward both winners as independent
tracks:

- **Track 1** (`brief-text-image`): full OFAT sequence through all
  phases (2b → 2c → 2d → 2e), preserving the preregistered pipeline
  intact
- **Track 2** (`brief-text`): temperature testing (2b); library and
  ordering phases skipped (no images to compose/order); carried through
  to Phase 3a voting

This is additive — all preregistered tests were executed on Track 1;
Track 2 added scope to explore the unexpected finding. The modest
additional cost (~$55 for extra temperature cells) was justified by the
scientific value of understanding the text-only pathway.

### 4.2 Runs Per Condition

- K=10 independent single-pass runs per condition per phase (preregistered)
- K=30 runs for Phase 3a voting study
- All runs on the same 60-tile holdout set

### 4.3 Phase Execution Summary

| Phase | Hypothesis | Cells | Runs/Cell | Status | Optimal Result |
|-------|-----------|-------|-----------|--------|----------------|
| 2a | H1 (M/E) | 5 | 10 | Complete | brief-text (T2), brief-text-image (T1) |
| 2b | H7 (Temp) | 5×2 tracks | 10 | Complete | T=0.0 (both tracks) |
| 2c | H8 (Library) | 4×2 tracks | 10 | Complete | plus-hp (13 examples) |
| 2d | H5 (Neg text) | 3×2 tracks | 10 | Complete | Minimal |
| 2e | H4 (Ordering) | 4 | 10 | Complete | No significant effect |
| 3a | H3 (Voting) | 4 conditions | 30 | Complete | N=30, T=0.7, F1=0.751 |
| 3d | H2 (Two-stage) | Multiple configs | Varies | Complete | PV improved +0.09–0.14 F1 |

### 4.4 Errata

Two implementation errors affected data collection and analysis
methodology respectively; both were detected and corrected before results
were interpreted:

- **E25 (Modality manipulation failure)**: The batch detection script
  failed to conditionally skip example images for text-only conditions in
  Phase 2a. All five M/E conditions received identical images, producing
  anomalously clustered results that prompted investigation. Corrected
  and re-run.
- **E26 (Bootstrap CI bias)**: Reference de-duplication during bootstrap
  resampling produced confidence intervals that did not contain point
  estimates. Fixed by pre-computing per-tile TP/FP/FN counts before
  resampling.

A complete errata log (30+ entries, classified as correction /
clarification / deviation with impact assessment) is provided in the
supplementary materials alongside the full preregistration text.

## 5. Evaluation

### 5.1 Primary Outcome: Symbol-Level F1

- Spatial tolerance: 20 m (accounts for georeferencing error, symbol
  centroid ambiguity, and map digitisation precision)
- **Matching algorithm**: Hungarian algorithm
  (`scipy.optimize.linear_sum_assignment`) for globally optimal
  one-to-one assignment between detections and reference symbols
  - Cost matrix: pairwise Euclidean distances; distances >20 m set to ∞
  - True positive: matched detection–reference pair within tolerance
  - False negative: unmatched reference symbol
  - False positive: unmatched detection
- Strict one-to-one matching prevents double-counting
- Robustness checks at 10 m, 30 m, and 50 m tolerances (supplementary)

### 5.2 Secondary Outcome: Tile-Level MCC

- Matthews Correlation Coefficient for binary tile classification (has
  mounds vs empty)
- Balanced holdout set (30 empty, 30 populated tiles) makes MCC
  preferable to accuracy
- Also report sensitivity and specificity

### 5.3 Statistical Analysis

- **Confidence intervals**: 95% bootstrap CIs (1,000 iterations)
- **Multiple comparison correction**: Benjamini-Hochberg FDR at q = 0.05
  across 8 confirmatory hypotheses
- **Power**: minimum detectable effect ~0.07–0.09 F1 (80% power,
  α = 0.05, two-tailed) given 60 holdout tiles with 79 mound symbols
- Per-condition metrics computed as mean across K runs (K=10 for phases
  2a–2e; K=30 for Phase 3a)

### 5.4 Cost Measurement and Reporting Basis

[Added 2026-06-13 (Session 114); source:
`reports/token-load-audit-2026-06-12.md`. Cite audited dollars ONLY.]

- **Audited basis**: every dollar figure in the paper is computed from
  per-request token metadata priced at June 2026 Gemini flex-tier rates
  (Flash 3 $0.25/$1.50 per 1M input/output tokens), with **thinking
  tokens billed at the output rate** — verified against
  <https://ai.google.dev/gemini-api/docs/pricing> (retrieved 2026-06-12).
- **Why an audit was needed**: recorded run-time cost manifests carried
  three defect classes — recovery-merge double-counting (2–3× on three
  of four deployment campaigns), standard-tier rates recorded for runs
  executed at flex, and omitted thinking tokens (HIGH-thinking passes
  under-priced ~1.4×). Corrected per-pass costs (8,541-tile deployment):
  minimal text $4.66, HIGH text T0.7 $40.19, HIGH text T0.3 $50.82,
  image (cached) $39.07 — a true min : HIGH ratio of **8.6×** per pass,
  not the 3× of the superseded model.
- **Billing-console corroboration**: audited predictions match the
  Google billing console (ground truth) — 18 April single-day check:
  $402.08 billed vs $419.64 predicted (−4%) for the three campaign
  proposer legs, excluding the legacy manifest figures by ~3×; June
  10–11 dailies consistent with the audited uplift incremental (~$34.5).
- **Lower-bound caveat**: clean token loads are lower bounds — retry
  spend is not recorded on disk (audit § 8). Total corrected spend
  across the five 55-map deployment campaigns ≈ $722 flex (audit § 6).
- **Write-time gate**: any dollar entering paper text must carry its
  pricing basis (audited flex, per-item metadata) and date.

## 6. Reproducibility and Transparency

### 6.1 Preregistration

- Registered at OSF prior to confirmatory data collection (2026-01-31)
- Protocol version 4.6 with versioned changelog
- All deviations documented in a living errata log (30+ entries) with
  classification (correction / clarification / deviation) and impact
  assessment

### 6.2 Software and Data

- Detection pipeline: Python scripts using google-genai SDK
- Evaluation: custom spatial matching library using scipy (Hungarian
  algorithm), geopandas, shapely
- All prompt configurations, system instructions, and study YAML
  definitions version-controlled
- Ground truth, tile manifests, and prompt text archived for
  reproducibility
- Comprehensive per-request metadata logging: tokens, latency, cost,
  config snapshot, retry counts

### 6.3 Human–AI Collaborative Development

The detection pipeline, evaluation framework, and statistical analysis
were developed collaboratively between the primary researcher and an
LLM-based coding assistant (Claude Code, Anthropic). The collaboration
spanned 50+ documented sessions over approximately six weeks.

**Division of responsibility**:

- *Human researcher*: hypothesis formulation, experimental design
  decisions, protocol deviation judgements, domain calibration (e.g.,
  flagging anomalous results from archaeological knowledge), result
  interpretation
- *AI assistant*: pipeline implementation, prompt configuration
  management, systematic error detection (e.g., E25 modality bug, E26
  bootstrap bias), statistical analysis code, metadata logging

**What the collaboration enabled**:

- Rapid iteration on pipeline components (tile generation, spatial
  matching, consensus voting) with immediate testing
- Systematic checking at a scale impractical for a solo researcher
  (63 config files, 30+ errata entries, per-request metadata logging)
- Living documentation: session transcripts and structured reflections
  archived for transparency

**What it could not replace**:

- Domain expertise for calibrating expectations (recognising when results
  contradicted archaeological or methodological priors)
- Scientific judgement on deviation decisions (dual-track extension,
  erratum classification, hypothesis prioritisation)
- Experimental design choices that required understanding the research
  question, not just the implementation

Session transcripts are archived at [Zenodo DOI TBD]. A more detailed
analysis of the collaboration process and its implications for
AI-assisted research methodology is planned as a separate contribution.

---

## Notes for Drafting

### What the Preregistration Planned but Was Not Executed

| Hypothesis | Reason Deferred |
|-----------|----------------|
| H6 (Flash → Pro transfer) | Not started; budget prioritised for Flash experiments |
| H10 (Training pool size) | Hard positive pool exhausted at 4 examples |
| H12 (HP:HN ratio) | Depends on H10 (larger HP pool) |
| H13 (Overlap/stride) | Low priority; would require re-tiling |
| H14 (Cross-model consistency) | Deferred to future work |
| H15 (Cross-model voting) | Deferred to future work |

### Key Surprises Worth Foregrounding in Discussion (Not Methods)

1. **Text-only outperformance (H1)**: Images constrained rather than
   enriched the model — opposite to the project's founding assumption
2. **Two-stage improvement (H2)**: Contradicted preregistered null;
   proposer–verifier achieved +0.09–0.14 F1
3. **Deterministic temperature (H7)**: T=0.0 best for single-pass
   despite literature suggesting stochasticity aids diversity
4. **Minimal negative text (H5)**: Less guidance was better — verbose
   exclusion instructions may have introduced confusion
5. **Consensus voting ceiling (H3)**: N=30 at T=0.7 achieved F1=0.751,
   a substantial improvement but with diminishing returns

### Resolved Framing Decisions

- **Dual-track**: framed as adaptive protocol extension (additive, not
  substitutive) — all preregistered tests executed on Track 1; Track 2
  added scope
- **Errata**: E25 and E26 in main text (affected data collection and
  statistical methodology); full errata log in supplementary material on
  Zenodo alongside preregistration text
- **Human–AI collaboration**: methods subsection (§6.3) in this paper;
  deeper analysis of 40+ session reflections planned as separate
  contribution
- **Deferred hypotheses**: TBD — some still running; will assign to
  limitations or future work once final execution status is known
