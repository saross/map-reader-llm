# Experimental Progression: From Preregistered Design to Production Pipeline

> **Last revised**: 2026-07-31 (C4 sweep: missed "1/10 FDR" instance
> fixed; 20 m CI updated to the era-current provenance artefact). See
> [§ Changelog](#changelog) for revision history.

**Purpose**: Reference document for the paper's methods section,
characterising the three-phase experimental progression, what was tested
where, and why the design evolved.

**Date**: 2026-03-30

> **Cost-basis note (2026-06-13)**: dollar figures in this document
> predate the 2026-06-12 token-load audit
> (`reports/token-load-audit-2026-06-12.md`) and are retained as
> historical context only. The audit found recorded costs understated
> thinking-token spend and, for some manifests, double-counted recovery
> merges. Any dollar entering paper text must come from the audited
> basis, not from here.

---

## Overview

This study followed a preregistered One-Factor-At-a-Time (OFAT)
sequential design (OSF registration, lodged 2026-01-31; v4.7 content —
the posted file's own header retains a stale v4.6 label, see the errata)
that was
progressively adapted as findings accumulated. The experimental
progression has three phases:

1. **Preregistered exploration** (February 2026): OFAT design on 60-tile
   holdout at 512px, testing prompt engineering variables
2. **Scaled validation** (March 2026): Re-execution on 340 tiles at
   512px with adequate statistical power, plus post-registration
   pipeline development
3. **Production optimisation** (late March 2026): Full evaluation on
   487 tiles at 384px, focusing on factors identified as significant

All deviations from the preregistration are documented in the protocol
errata (57 entries, E1–E57) maintained alongside the preregistration
document.

---

## Phase 1: Preregistered OFAT exploration (60 tiles, 512px)

### Design

The preregistration specified a sequential OFAT design testing five
prompt engineering factors on a 60-tile holdout set drawn from four
Soviet 1:50,000 topographic map sheets covering the Thracian Plain and
surrounding areas, Bulgaria (K-35-052-4_32635, K-35-053-3_Elenovo,
K-35-062-2_Rakovski, K-35-078-1_Lesovo; `osf/preregistration.md:42`,
`:1919-1920`). The tile size (512×512 pixels, 448px stride with 64px
overlap) was selected during a calibration pilot (2026-01-07) comparing
256px, 512px, and 1024px tiles at K=5 passes with a 2-of-5 voting
threshold (`archive/pilot-tile-size/outputs/pilot_decision.md`;
preregistration §12.2).

The OFAT sequence tested each factor in order, carrying optimal
parameters forward:

| Phase | Hypothesis | Factor | Conditions | Runs per condition |
|---|---|---|:---:|:---:|
| 2a | H1 | Modality/elaboration | 5 | 10 |
| 2b | H7 | Temperature | 5 × 2 tracks | 10 |
| 2c | H8 | Library composition | 5 × 2 tracks | 10 |
| 2d | H5 | Negative text treatment | 2 × 2 tracks | 10 |
| 2e | H4 | Example ordering | 4 | 10 |

All five phases were executed on the 60-tile holdout set at 512px
between 2026-02-04 and 2026-02-12. Minor protocol deviations were
documented in errata E25–E31 (e.g., text-only conditions initially
included example images by mistake; ordering had 4 conditions instead
of the preregistered 3).

### Findings

The 60-tile OFAT produced directional results for each factor but
**insufficient statistical power for formal significance testing**.
At 60 tiles, bootstrap confidence intervals spanned ~0.20 F1, and
**no** Phase 2a pairwise comparison survived FDR correction (0 of 10;
`results/phase2a-analysis-report.json`, `n_fdr_significant: 0` — the
long-standing "1 of 10" figure was a misreport, corrected 2026-07-30;
see the E36 correction block and Obs 372).
The results were informative for parameter selection (carrying optimal
values forward through the OFAT sequence) but could not support
definitive claims about individual factor effects.

Key directional findings at 60 tiles:

- **Modality (H1)**: Text-based prompts outperformed image-only, with
  mixed text+image performing best — but no pairwise comparison was
  significant after FDR
- **Temperature (H7)**: T=0.0–0.3 marginally outperformed T=0.7–1.0 at
  N=1 — consistent with lower temperatures producing more precise
  single-pass outputs
- **Library composition (H8)**: Negligible differences between 5
  library configurations — no comparison approached significance
- **Text treatment (H5)**: Terse vs verbose descriptions produced
  nearly identical results
- **Ordering (H4)**: Canonical-last marginally outperformed random —
  suggestive but not significant

### Consensus voting pilot

Phase 3a (H3 consensus voting) was also initiated on the 60-tile set
(2026-02-15), testing N=30 consensus pools at two temperatures on both
image and text tracks. The consensus results showed substantial F1
improvements over N=1 baselines, motivating the expanded evaluation
in Phase 2.

---

## Phase 2: Scaled validation (340 tiles, 512px)

### Motivation

The 60-tile results demonstrated that the evaluation set was
underpowered for the study's analytical goals (errata E36, 2026-03-17).
The decision to expand to the full 340-tile evaluation corpus at 512px
was driven by:

1. **Wide confidence intervals**: ~0.20 F1 span at 60 tiles made
   meaningful comparison impossible
2. **FDR attrition**: 0/10 Phase 2a comparisons survived
   multiple-comparison correction
3. **Documented deviation**: the expansion is recorded as a
   Deviation-class erratum (E36, `protocol-errata.md:878`). The
   preregistration did not anticipate evaluation-set expansion — it
   reserved the 281-tile pool for Stage 2 (`osf/preregistration.md:76`);
   §3.5's "robustness checks" concern spatial tolerance only

### What was re-run

All Phase 2 conditions were re-executed on the 340-tile corpus
(outputs in `outputs/retest/`). The re-runs used fewer replications
per condition for factors already shown to be non-significant at 60
tiles:

| Phase | Factor | Re-run scope | Runs per condition | Rationale |
|---|---|---|:---:|---|
| 2a | Modality | All 5 conditions | 3 | Significant factor; needs adequate power |
| 2b | Temperature | All 10 conditions (2 tracks) | 3 | Significant factor |
| 2c | Library composition | All 10 conditions (2 tracks) | 1 | Non-significant at 60 tiles; 1 run sufficient for confirmation |
| 2d | Text treatment | All 4 conditions (2 tracks) | 1 | Non-significant at 60 tiles |
| 2e | Ordering | All 4 conditions | 1 | Non-significant at 60 tiles |
| 3a | Consensus voting | N=30, both tracks + HIGH thinking | 30 | Core pipeline evaluation |

### Pipeline development (post-registration)

During the 512px validation phase, two architectural innovations were
developed that were not in the original preregistration:

1. **HIGH thinking consensus**: The preregistration fixed thinking at
   MINIMAL (Section 8.9), but exploratory experiments found that HIGH
   thinking produced better consensus outcomes despite worse
   N=1 performance — the diversity dividend (Obs 141). This motivated
   systematic comparison of HIGH vs MINIMAL at consensus level.

2. **Proposer-Verifier (PV) pipeline** (errata E37, 2026-03-15):
   A two-stage pipeline where consensus candidates are individually
   verified by a second VLM pass was developed as a post-registration
   extension. The PV stage added +0.05 to +0.09 F1 on top of consensus
   for Flash models and became the dominant architectural feature.

### Findings at 340 tiles

The scaled evaluation confirmed and extended the 60-tile findings with
adequate statistical power:

- **Prompt engineering factors (library, treatment, ordering)**: Confirmed
  non-significant. 0 of 28 comparisons significant after FDR (Obs 207).
  The 60-tile directional findings were validated as noise.
- **Temperature**: T=0.7 vs T=1.0 confirmed significant (ΔF1=+0.17,
  all p<0.001 at consensus). T=1.0 is the Gemini API default; the
  finding that practitioners should change this default is a practical
  contribution.
- **Modality**: Text outperforms image confirmed significant at HIGH
  thinking (+0.05 to +0.09 F1). The advantage vanishes at MINIMAL
  thinking.
- **Architecture**: Consensus voting and PV verification each produce
  large, significant improvements (Obs 202, 207).

---

## Phase 3: Production optimisation (487 tiles, 384px)

### Tile-size diagnostic

The preregistered tile-size calibration (Phase 0, 2026-01-07) selected
512px on single-scale precision-recall balance, run at K=5 passes with
a 2-of-5 voting threshold (`pilot_decision.md`; preregistration §12.2).
H11, a preregistered conditional hypothesis (to be tested if F1 < 0.85),
triggered a diagnostic comparison of 256px, 384px, and 512px tiles
(2026-03-22–23).

The diagnostic revealed a **tile-size × architecture interaction**
(Obs 203): 384px tiles outperform 512px in the consensus+PV pipeline
despite underperforming at N=1. The mechanism is that 384px tiles
produce higher recall (each tile shows less context, so the model flags
more potential targets) at the cost of precision. The consensus pipeline
exploits this high-recall raw material — it can filter diverse false
positives but cannot resurrect missed detections.

This crossover was invisible to the preregistered single-stage
screening because the consensus+PV pipeline architecture that exploits
it was developed after the tile-size decision was locked in. The finding generalises: for
multi-stage detection pipelines, first-stage parameters should be
optimised for recall, not F1.

### What was run at 384px

The 384px production runs (487 tiles across all four map sheets) focused
on the factors identified as significant in Phases 1–2, plus the new
architectural variables:

| Factor | Conditions tested | Runs |
|---|---|---|
| **Architecture** | N=1, consensus (N=5, 10, 30), consensus+PV | Varied |
| **Thinking level** | MINIMAL, HIGH (Flash); MEDIUM, HIGH (Pro) | 5–30 per condition |
| **Modality** | Text, image (both tracks) | Per condition |
| **Temperature** | T=0.0, T=0.3, T=0.7 | Per condition |
| **Model** | Flash, Pro | Per condition |
| **Verifier** | Flash MINIMAL, Flash MEDIUM | Per PV condition |

**What was NOT re-run at 384px** (justified by Phase 2 null results):

- Library composition (Phase 2c): 0/20 significant at 512px; no reason
  to expect different results at 384px
- Text treatment (Phase 2d): 0/2 significant; the model is indifferent
  to terse vs verbose instruction text
- Example ordering (Phase 2e): 1/6 marginally significant at raw
  p<0.05 but ns after FDR; not a productive optimisation axis
- Full temperature sweep (T=1.0, T=1.3): T=1.0 confirmed poor in Phase
  2b; T=1.3 worse still. Only the sensible range (T=0.0–0.7) was
  tested at 384px

### Key findings

The 384px production evaluation produced the study's headline results:

- **Best F1 = 0.890** [0.874, 0.910] at 20m tolerance (Flash HIGH text
  16-of-30 consensus + Flash MINIMAL verifier)
- **Pipeline lift = +0.503 F1** from N=1 (0.387) to best pipeline
  (0.890)
- **Thinking-level crossover** (Obs 208): HIGH thinking is worse at
  N=1 (ΔF1=-0.101) but better at consensus (+0.139) due to the
  diversity mechanism
- **Pool-size plateau** (Obs 204): N=10 does not improve over N=5 for
  either Flash or Pro
- **Pro dominated by Flash + pipeline** (Obs 205): Flash + PV at ~$3
  matches or exceeds Pro consensus at ~$54
- **Prompt engineering inert**: 0/28 comparisons significant after FDR
  (Obs 207)

---

## Design evolution summary

| Aspect | Preregistered | Actual | Justification |
|---|---|---|---|
| Tile size | 512px | 512px → 384px (H11) | Crossover: 384px better for pipeline (Obs 203) |
| Evaluation set | 60 tiles | 60 → 340 → 487 tiles | Statistical power (E36) |
| Thinking level | MINIMAL (fixed) | MINIMAL and HIGH | Diversity dividend (Obs 141; no erratum yet — E40 covers only Pro's MINIMAL unavailability) |
| Pipeline | Single-pass + consensus | + Proposer-Verifier | Post-registration extension (E37) |
| Spatial tolerance | 20m primary | 20m primary (E47, reverting E46) | Preregistration alignment |
| Temperature | 5 levels tested | T=0.7 adopted for production | T=1.0 confirmed poor (Phase 2b) |

### What the paper should argue

The evolution from preregistered OFAT design to production pipeline is
not a weakness — it is the finding. The preregistration tested the
hypothesis space that the literature suggested was important (prompt
engineering variables). The result — that none of those variables
matter — redirected the investigation toward the architectural factors.
Both architectures were themselves registered: consensus voting as H3,
and the proposer-verifier pipeline as H2 Condition B
(`osf/preregistration.md:455-476`), with a registered *null* prediction
that neither two-stage architecture would help. That prediction was
falsified, and the registered stopping rule (≥0.05 F1, `osf:491`) fired
— licensing the pursuit of PV at production scale (see the corrected
E37). What the preregistration did not anticipate is the *scale* of the
effect and the optimisation layer built on it, not the architecture.

The three-phase structure maps to a natural scientific progression:

1. **Exploration** (60 tiles): What might matter? → Most prompt
   variables don't; modality and temperature do
2. **Validation** (340 tiles): Confirm with adequate power → Prompt
   engineering confirmed inert; architecture matters
3. **Optimisation** (487 tiles): Given what works, how well can we do?
   → F1=0.890, pipeline dominates, optimal parameters depend on
   architecture

Each phase's findings motivated the next phase's design. The protocol
errata (47 entries) provide full transparency about how and why the
design evolved.

---

## Evaluation scope mapping

For reference, here is which factors were tested at which tile set:

| Factor | 60 tiles (512px) | 340 tiles (512px) | 487 tiles (384px) |
|---|:---:|:---:|:---:|
| Library composition (5×2) | ✓ (10 runs) | ✓ (1 run) | — |
| Text treatment (2×2) | ✓ (10 runs) | ✓ (1 run) | — |
| Example ordering (4) | ✓ (10 runs) | ✓ (1 run) | — |
| Temperature (5 levels) | ✓ (10 runs) | ✓ (3 runs) | T=0.0/0.3/0.7 only |
| Modality (text/image) | ✓ (10 runs) | ✓ (3 runs) | ✓ (5–30 runs) |
| Thinking (HIGH/MIN) | — | ✓ (30 runs) | ✓ (5–30 runs) |
| Consensus voting | ✓ (30 runs) | ✓ (30 runs) | ✓ (5/10/30 runs) |
| PV verifier | — | ✓ (pilot) | ✓ (full evaluation) |
| Model (Flash/Pro) | — | — | ✓ (5–10 runs) |
| Pool-size plateau | — | — | ✓ (N=5 vs N=10) |

Factors not re-run at 384px (library, treatment, ordering) were
confirmed non-significant at 340 tiles with adequate power — repeating
them at 384px would have consumed API budget on factors already shown
to be inert.

---

## Statistical methodology across phases

| Phase | Tile count | Statistical tests | Power |
|---|:---:|---|---|
| 60 tiles | 60 | Bootstrap CIs (1,000 iterations) | Insufficient — CIs ~0.20 wide |
| 340 tiles | 340 | Permutation tests (10,000 iterations) + FDR | Adequate for most comparisons |
| 487 tiles | 487 | Permutation tests (10,000 iterations) + FDR + leaderboard round-robin | Full power for all comparisons |

All statistical tests use tile-swap permutation (null: condition labels
exchangeable within tiles) with Benjamini-Hochberg FDR correction
(q=0.05) applied within factor families. Bootstrap CIs use tile-level
stratified resampling (1,000 iterations, seed 42).

---

*This document can be adapted for the paper's methods section. The
three-phase structure (exploration → validation → optimisation) provides
a natural narrative for presenting the experimental design and its
evolution.*

---

## Changelog

### 2026-07-31 — C4 quantitative-sweep corrections (Session 123)

**Refresh trigger**: the Phase 3 (C4) recompute harness flagged two
divergences in this document
(`reports/verification/c4-triage/mismatch-triage-2026-07-31.json`,
rows 035#29 and 035#59).

| before | after |
| :--- | :--- |
| "Only 1/10 Phase 2a comparisons survived" (line 126) | 0/10 — a surviving instance the 2026-07-30 correction missed |
| Best-F1 20 m CI "[0.863, 0.915]" | [0.874, 0.910] (`results/era1-pv-stage-d/384-consensus-text-high/evaluation.json`, `$.summary.buffers[3]` — the provenance source for condition `pv-diag-384::verified-adv-text-consensus-16of30`; the old bounds were the March-era `threshold_sweep.json` bootstrap, superseded by the 14-buf+MCC re-score) |

What did NOT change: the F1 point estimate (0.890), all tier claims,
and every other figure in the document (the C4 sweep verified 607
values MATCH across the extracted corpus at this date).

### 2026-07-30 — Phase 2a FDR-survivor figure corrected (Session 121)

**Refresh trigger**: the Phase 1 verification campaign's execution
census caught the "only 1 of 10 Phase 2a pairwise comparisons survived
FDR correction" claim as a misreport; PI-approved handling at
`reports/verification/phase2-rulings-2026-07-30.md` § 1d.

| before | after |
| :--- | :--- |
| "only 1 of 10 Phase 2a pairwise comparisons survived FDR correction" | 0 of 10 (`results/phase2a-analysis-report.json`, `n_fdr_significant: 0`) |

What did NOT change: the insufficient-power conclusion (which the
corrected figure strengthens), the directional findings, and the
corpus-expansion rationale. Companion corrections: the E36 correction
block in `protocol-errata.md`, Obs 372, and
`reports/gs-tile-pool-mapping-2026-05-28.md`.

### 2026-07-28 — Preregistration-attribution corrections (D17 audit)

**Refresh trigger**: the Session-118/119 preregistration-integrity audit
(`reports/d17-inventory/prereg-attribution-sweep.md`, findings FALSE-14,
FALSE-15, U10, S2, S3; Fable review Finding 4). Corrections:

| before | after |
| :--- | :--- |
| corpus "1:25,000 … Kazanlak Valley" | 1:50,000, Thracian Plain and surrounding areas, four named sheets |
| tile-size pilot "at N=1 (single-pass)" (×2) | K=5 passes, 2-of-5 voting (per `pilot_decision.md` and prereg §12.2) |
| §3.5 quoted as "robustness checks on the full corpus" | fabricated quotation removed; expansion cited to erratum E36 |
| "OSF registration v4.6, 2026-01-14" | lodged 2026-01-31, v4.7 content (posted header retains stale v4.6 label) |
| "errata (47 entries, E1–E47)" | 57 entries, E1–E57 |
| HIGH-thinking deviation attributed to E32 (×2) | E32 concerns temperature; deviation currently has no erratum |

What did NOT change: the three-phase narrative, all findings and
observations, all cost figures, and the deviations table's substance.

### 2026-06-13 — Cost-basis note added (currency sweep)

**Refresh trigger**: the Session-114 final currency sweep before
§Results prose. The Obs 205 cost comparison ("Flash + PV at ~$3 …
Pro consensus at ~$54") predates the 2026-06-12 token-load audit; a
cost-basis note now directs readers to the audited basis. The
qualitative conclusion (Flash + pipeline dominates Pro on cost) is
unaffected and strengthens under the audit (Pro thinking tokens were
unbilled in the recorded figures). No other content changed.

### 2026-03-30 — Original publication

Methods-section reference document: the three-phase experimental
progression (exploration → validation → optimisation), what was tested
where, and why the design evolved. Written before the 55-map
generalisation campaigns, the token-load audit, and the working-precision
derivations; results quoted are GS-instrument values as of late March
2026.
