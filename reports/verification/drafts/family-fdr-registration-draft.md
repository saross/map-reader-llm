# Pre-execution registration — registered-family Benjamini–Hochberg correction

> **Last revised**: 2026-07-30 (original publication; DRAFT awaiting PI
> confirmation). See [§ Changelog](#changelog) for revision history.

**Status**: `planned` — **not yet executed**. This document is the rule-10
pre-execution registration for the family-level Benjamini–Hochberg false
discovery rate (BH-FDR) correction across the confirmatory hypotheses. It
fixes the **family membership and the primary test per hypothesis** before
the correction is computed. It must be committed, and the ambiguities in
§ 5 ruled on by the Principal Investigator (PI), before the correction is
run.

**Repository anchor**: `562d185a44b33d4c3f3c504d1e5981767c896df8` (working
tree clean at drafting).

**Authority chain**:

| authority | locator | content |
| --- | --- | --- |
| Charter execution rule 10 | `planning/audit-charter.md` § 5 item 10 | "**Pre-execution registration for any new run**: registry entry, conditions, `predicted_outcome` committed with `status: planned` BEFORE the API call (`audit-and-completion-plan.md` § 6.4)." |
| PI decision, family definition | `planning/audit-and-completion-plan.md` § 4, line 119 | "\| BH-FDR family \| one primary test per hypothesis (7; H6 never ran) as primary, all-contrasts correction as a reported sensitivity \|" |
| GATE 1 ruling 7(d) | `planning/audit-charter.md` § 10 item 7(d) | "**Eight-hypothesis BH-FDR family**: run it now (zero API cost), plus a Methods/Discussion disclosure of why practice deviated." |
| Backlog entry | `reports/d17-inventory/unexecuted-register.md` § A-01 | the registered correction, its non-execution, and the proposed construction |

**API spend**: **US$0.00.** This is pure recomputation over p-values already
committed to the repository. No API call is made; the rule-10 gate is
honoured because the *analysis* is new, not because spend is at stake.

---

## 1. What this registration does and does not fix

**It fixes**: which hypotheses constitute the family (seven); which single
executed test represents each hypothesis; which artefact and which JSON
field supplies each p-value; the correction procedure; and the sensitivity
analysis reported alongside it.

**It does not fix outcome blindness.** Every p-value named below is already
committed to this repository and is quoted verbatim in § 5. See § 9
(`predicted_outcome`) for the honest statement of what this registration
can and cannot claim.

---

## 2. The registered obligation, verbatim

From the lodged registration
`docs/methodology/preregistration/osf/preregistration.md` § 3.1
"Significance Testing" (lines 268–270):

> - **Per-hypothesis α**: 0.05
> - **Direction**: One-tailed for directional predictions; two-tailed for
>   equivalence tests (H1)
> - **Multiple comparison correction**: Benjamini-Hochberg FDR at q = 0.05
>   across confirmatory hypotheses

And § 3.5 "Reporting" (line 295):

> - Report both uncorrected and FDR-corrected p-values

And § 3.2 "Rationale for FDR" (line 274), which fixes the intended family
size at the hypothesis level, not the contrast level:

> With 8 confirmatory hypotheses tested on 60 tiles (79 mound symbols),
> statistical power is adequate for detecting moderate effects.

The registered inference machinery is **bootstrap** — § 3.5 line 293:

> - Report **effect sizes** (F1 difference, precision difference, recall
>   difference) with 95% bootstrapped CIs

---

## 3. Family membership

| # | hypothesis | in family? | reason |
| --- | --- | --- | --- |
| 1 | H1 Modality and elaboration | yes | executed (Era 1) |
| 2 | H2 Two-stage pipelines | yes | Condition B executed (Era 2); Condition C never ran (E59) |
| 3 | H3 Consensus voting | yes | executed (Era 1 and Era 2) |
| 4 | H4 Example ordering | yes | executed (Era 1) |
| 5 | H5 Negative text treatment | yes | partially executed (Era 1); registered headline contrast inestimable |
| 6 | H6 Flash→Pro transfer | **no** | **never run** — see § 6 |
| 7 | H7 Temperature | yes | executed (Era 1) |
| 8 | H8 Library composition | yes | executed (Era 3, all seven registered contrasts) |

**Family size m = 7.** The registration's own § 3.2 framing anticipated
eight; the reduction to seven is a factual consequence of H6's
non-execution, not a selection made on results.

---

## 4. Selection rule (fixed before inspection of the ranking)

Applied in order, per hypothesis:

1. **Named headline.** If the registration names a single headline
   contrast or a single directional hypothesis for that hypothesis, that
   is the primary test.
2. **Omnibus / main effect.** Otherwise, if an omnibus or main-effect test
   was executed, that is the primary test.
3. **AMBIGUOUS.** Otherwise, the hypothesis is flagged AMBIGUOUS, two or
   three candidate primaries are listed with their p-values, and the PI
   rules. A recommended default is offered but carries no authority until
   ratified.

**Metric**: the registered decision statistic for that hypothesis (F1 for
H1–H4 and H7–H8; **precision** for H5 — see § 5.5).

**Tail convention**: **two-sided throughout**, per the operative reading in
the E64 draft (see § 7.1 for the divergence and its status).

---

## 5. Per-hypothesis primary-test selection

### 5.1 H1 — Modality and elaboration level

**Registered primary test** (verbatim, `results/commitments.json`
`CMT-0102`, source `preregistration.md:436`):

> - Primary: Pairwise bootstrap comparisons across 5 M/E levels (95% CIs,
>   FDR-corrected)

`decision_statistic` field of `CMT-0102`, verbatim:

> ABSENT — the primary analysis names the procedure (pairwise bootstrap
> comparisons) but not the performance metric being compared; F1 is named
> only in prediction 2 (line 407).

**Registered planned contrasts** (`preregistration.md:438-441`;
`CMT-0103`–`CMT-0106`), verbatim:

> Image-only vs Brief+image (does adding text help?)
> Brief+image vs Verbose+image (does more detail help?)
> Brief-text vs Brief+image (do images help?)
> Text-only conditions vs Image-using conditions (modality effect)

**Registered tail rule** (`preregistration.md:442-443`; `CMT-0107`,
`CMT-0108`), verbatim:

> - Two-tailed tests for modality comparisons
> - One-tailed for elaboration: H0: verbose ≤ brief; H1: verbose > brief

**Executed artefact**: `results/retest/pairwise-bootstrap-comparisons.json`
(Era 1, 340 tiles, 20 m buffer, 1 000 bootstrap iterations, seed 42;
`metadata.n_comparisons` = 70, `metadata.note` = "Raw p-values — FDR
correction deferred until all data available"). Field carrying the
p-value: `comparisons[i].f1_p_value`.

**VERDICT: AMBIGUOUS.** The registration names four planned contrasts and
designates none as headline; no omnibus/main-effect test across the five
M/E levels was executed. Selection is outcome-material here (candidate
p-values span 0.004 to 0.94).

| option | contrast | artefact index | `f1_delta` | `f1_p_value` |
| --- | --- | --- | --- | --- |
| **(i)** first-listed registered contrast `CMT-0103`: Image-only vs Brief+image | `brief-text-image` vs `image-only` | `comparisons[4]` | +0.06536107577746958 | **0.006** |
| (ii) registered contrast `CMT-0105`: Brief-text vs Brief+image ("do images help?") | `brief-text` vs `brief-text-image` | `comparisons[0]` | +0.022473818822873966 | **0.38** |
| (iii) "significant differences detected between levels" reading — minimum-p over the ten executed level pairs | `brief-text` vs `image-only` | `comparisons[1]` | +0.08783489460034355 | **0.004** |

**Recommended default**: option (i). It is the registration's own
first-listed planned contrast; it is two-tailed by the registered rule
(a modality comparison); and it is a genuine contrast rather than a
minimum-p statistic, which would be anti-conservative inside a BH
step-up.

**Not available**: registered contrast 4 (`CMT-0106`, "Text-only
conditions vs Image-using conditions") was **never executed as a pooled
contrast** — the artefact carries only the ten level-versus-level pairs.
`CMT-0106`'s own `decision_statistic` records the underlying defect:
"ABSENT — contrast named without a metric; the text also does not state
how the two groups of conditions are pooled or aggregated."

**One-tailed limb**: the registered one-tailed elaboration test
(`CMT-0108`, verbose > brief) is available at `comparisons[6]`
(`brief-text-image` vs `verbose-text-image`, `f1_delta` =
+0.0021486512989132792, `f1_p_value` = 0.94) and, on the text-only arm, at
`comparisons[2]` (`brief-text` vs `verbose-text`, `f1_p_value` = 0.106).
Both are null in the registered direction and neither is proposed as the
H1 primary.

**Current-instrument cross-check** (permutation, not registered method):
`results/era1-leaderboard/tiering_20m.json`, `pairwise[81]`
(`retest-phase2a::brief-text-image` vs `retest-phase2a::image-only`),
`p_value` = 0.001, `bh_adjusted_p` = 0.001751.

---

### 5.2 H2 — Two-stage pipelines do not improve detection

**Registered prediction** (`CMT-0112`, `preregistration.md:461`),
verbatim:

> **Prediction**: Neither two-stage architecture will improve F1 over
> single-stage detection with voting.

**Registered test** (`CMT-0113`, `preregistration.md:463`), verbatim:

> **Test**: Compare at optimal single-stage configuration:

with conditions `CMT-0114`/`CMT-0115`/`CMT-0116`, verbatim:

> | A (baseline) | Single-stage | Optimal config with consensus voting |
> | B | Coarse-to-fine | Liberal proposer → strict verifier |
> | C | Fine-to-coarse | Standard detection → context-expanded re-query for uncertain cases |

**Registered analysis** (`CMT-0124`, `preregistration.md:488`), verbatim:

> - One-tailed tests: H0: two-stage ≥ single-stage; H1: two-stage <
>   single-stage

**Registered stopping rule** (`CMT-0126`, `preregistration.md:491`),
verbatim:

> **Stopping rule**: Two-stage architectures will only be pursued further
> if either demonstrates F1 at least 0.05 higher than single-stage. Given
> the inherent cost (~2× API calls) and complexity overhead, parity or
> marginal improvement would not justify adoption.

**Executed artefact**:
`results/pairwise/20m/group_1_architecture/pv-vs-consensus-flash-high-text-16-of-30-pv-vs-flash-high-text-26-of-30.json`
(Era 2, 487 tiles, 20 m buffer, 10 000 permutations, seed 42). Field:
`permutation_test.p_value`.

Same row in the corrected roll-up
`results/pairwise/20m/fdr/pairwise_results_fdr.json` at
`comparisons[0]`: `p_value_raw`, `p_value_adj`.

**VERDICT: SELECTED** (rule 1 — the registration names the comparator:
"at optimal single-stage configuration").

| field | value |
| --- | --- |
| condition A (two-stage, B) | Flash HIGH text 16-of-30 + PV, F1 = 0.890201 |
| condition B (single-stage optimal with voting) | Flash HIGH text 26-of-30, F1 = 0.814118 |
| `permutation_test.observed_f1_diff` | 0.076083 |
| **`permutation_test.p_value`** | **0.0** (10 000 permutations ⇒ p < 1 × 10⁻⁴) |
| `comparisons[0].p_value_adj` (existing 26-row family) | 0.0 |

**Divergences** (detail in § 7):

- **Direction reversed.** The registered prediction is that two-stage will
  *not* improve; the executed result is that it improves by +0.0761 F1,
  which also **clears the registered stopping-rule threshold of ≥ 0.05**.
  Under the registered one-tailed alternative (two-stage < single-stage)
  the p-value would be ≈ 1.0; under the operative two-sided reading it is
  < 1 × 10⁻⁴. The two-sided reading is used.
- **Condition C never executed** (E59) — H2 is represented by Condition B
  alone.
- **Instrument**: permutation, not the registered bootstrap (E45).
- **Proposer prompt substituted** (E58: registered `propose_brief` never
  used; `detect_brief-text` substituted in all PV experiments).
- **Corpus**: Era 2 (487 tiles at 384 px), not the registered 60-tile
  512 px holdout (E36).

**Alternatives not selected** (same file family, all Era 2): the N = 5 pair
(`pv-vs-consensus-flash-high-text-4-of-5-pv-vs-flash-high-text-5-of-5.json`,
`p_value` = 0.0), the N = 10 pair (`p_value` = 0.0), the image pair
(`p_value` = 0.0004), and the Pro pair (`p_value` = 0.258). The Pro pair is
the only non-significant one; it is not at the optimal single-stage
configuration and is therefore excluded by rule 1.

---

### 5.3 H3 — Consensus voting improves F1

**Registered prediction** (`CMT-0128`, `preregistration.md:501`),
verbatim:

> **Prediction**: Consensus voting will improve F1 compared to single-pass
> detection.

**Registered primary comparison** (`CMT-0135`, `preregistration.md:519`),
verbatim:

> - Compare single-pass mean F1 vs voted F1 at each (N, threshold)
>   combination

**Registered tail rule** (`CMT-0138`, `preregistration.md:522`), verbatim:

> - One-tailed test for primary comparison: H0: voting ≤ single-pass; H1:
>   voting > single-pass

**Executed artefact**:
`results/diversity-dividend-384/tiering-champions/tiering_20m.json`
(Era 2, 487 tiles, 20 m buffer, 10 000 permutations, seed 42, `fdr_q` =
0.05, `git_commit` = `db582f1d`). Field:
`headline_contrasts[2].p_value`.

**VERDICT: SELECTED** (rule 1 — the registration names the comparison
"single-pass mean F1 vs voted F1"; the (N, threshold) is taken at the
optimal operating point, as `CMT-0137`/`preregistration.md:521` directs).

| field | value |
| --- | --- |
| `headline_contrasts[2].claim` | "consensus vs matched single-pass (consensus-flash-high-text-26of30)" |
| `ref_a` / `f1_a` | `consensus-flash-high-text-26of30` / 0.8141 |
| `ref_b` / `f1_b` | `pv-diag-384::baseline-flash-text-high-t-0-7` / 0.3871 |
| `f1_diff` | 0.427 |
| **`p_value`** | **0.0** (10 000 permutations ⇒ p < 1 × 10⁻⁴) |
| `bh_adjusted_p` (within that artefact's own family) | 0.0 |

**Divergences**: registered one-tailed, executed two-sided (conservative —
the observed direction is the predicted one); permutation not bootstrap
(E45); Era 2 not the registered 60-tile corpus.

**Alternatives, all concordant** (selection is not outcome-material —
every candidate is at its instrument's resolution floor):

| alternative | artefact | field | p |
| --- | --- | --- | --- |
| Era 1 bootstrap, registered method, **not** condition-matched | `results/retest/pairwise-bootstrap-comparisons.json` `comparisons[68]` (`consensus_T0.7_18of30_image` vs `single_pass_canonical_last`) | `f1_p_value` | 0.001 |
| Era 1 permutation, condition-matched (image) | `results/era1-leaderboard/tiering_20m.json` `pairwise[579]` | `p_value` | 0.0 |
| Era 1 permutation, condition-matched (text) | `results/era1-leaderboard/tiering_20m.json` `pairwise[871]` | `p_value` | 0.0 |

**Note on the bootstrap alternative**: `comparisons[68]` compares an image
consensus cell against a *different* condition's single-pass cell (the
Phase 2e canonical-last ordering arm), so it is not the registered
"single-pass mean F1 vs voted F1" matched comparison. This is why the
matched Era-2 contrast is preferred despite the instrument divergence.

---

### 5.4 H4 — Example ordering (canonical placement)

**Registered directional hypothesis** (`CMT-0147`,
`preregistration.md:546`), verbatim:

> **Directional hypothesis**: H0: canonical-last ≤ canonical-first; H1:
> canonical-last > canonical-first

**Registered primary analysis** (`CMT-0158`, `preregistration.md:570`),
verbatim:

> - **Primary**: Pairwise bootstrap comparisons across 3 ordering
>   conditions (95% CIs, FDR-corrected)

**Registered planned contrasts** (`CMT-0159`, `preregistration.md:571`),
verbatim:

> - **Planned contrasts**: Canonical-first vs Canonical-last; Optimal vs
>   Random

**Executed artefact**: `results/retest/pairwise-bootstrap-comparisons.json`
`comparisons[55]` (Era 1, 340 tiles). Field: `f1_p_value`.

**VERDICT: SELECTED** (rule 1 — the registration names a single
directional hypothesis, and the first-listed planned contrast is its
test).

| field | value |
| --- | --- |
| `phase` | "Phase 2e: H4 Ordering" |
| `condition_a` / `condition_b` | `canonical-first` / `canonical-last` |
| `f1_delta` | −0.03294330664745624 (canonical-last is the higher of the two) |
| **`f1_p_value`** | **0.124** |
| `significant_raw` | false |

**Divergences**: registered one-tailed, executed two-sided. The observed
direction *is* the predicted one, so the one-tailed p would be
approximately 0.062 — still null at α = 0.05, and consistent with the
independently derived estimate at
`reports/d17-inventory/d17-inventory-h1-h4.md:1098` ("p ≈ 0.06"). The
two-sided value 0.124 is used and is strictly conservative. A fourth
condition (`config-default`) was added post-lodgement (E30), so the
registered three-condition family became four.

**Finding-calibration flag** (carried from
`reports/d17-inventory/unexecuted-register.md` § A-11): the registered
primary contrast is **null**, while
`results/retest/retest-production-summary.md` narrates canonical-last as
supporting the recency-bias hypothesis on the strength of the
canonical-last vs random contrast (`comparisons[59]`, `f1_p_value` =
0.002). The BH family must use the registered contrast, not the
significant neighbour.

**Current-instrument cross-check**:
`results/era1-leaderboard/tiering_20m.json` `pairwise[2096]`, `p_value` =
0.1366, `bh_adjusted_p` = 0.176243 — concordant and null.

---

### 5.5 H5 — Negative text treatment

**Registered primary analysis** (`CMT-0181`, `preregistration.md:632`),
verbatim:

> - **Primary**: Pairwise bootstrap comparisons across 3 H5 levels on
>   precision (95% CIs, FDR-corrected; within each M/E level)

`decision_statistic` field of `CMT-0181`, verbatim: `precision`.

**Registered planned contrasts** (`CMT-0182`, `preregistration.md:633`),
verbatim:

> - **Planned contrasts**: Minimal vs Terse; Terse vs Verbose

**Registered scope** (`preregistration.md:622-624`), verbatim:

> - **M/E level**: All image-based conditions (Image-only, Brief-text+image,
>   Verbose-text+image)
> …
> - **Text-only exclusion**: Brief-text and Verbose-text M/E levels cannot
>   have "Images-only" negative guidance and serve only as H1 baselines

**Executed artefact**: `results/retest/pairwise-bootstrap-comparisons.json`
`comparisons[53]` (Era 1, 340 tiles). Field: `precision_p`.

**VERDICT: SELECTED — but by constraint, not by choice.** The registered
headline contrast (Minimal vs Terse, the subject of registered prediction 1
at `preregistration.md:615`) is **not executable on the current-era
corpus**: the Era-1 retest ran only `terse` and `verbose`
(`results/retest/phase2d-track1-evaluation.json` and
`.../phase2d-track2-evaluation.json` both carry
`conditions` = `["terse", "verbose"]`). Terse vs Verbose is therefore the
only registered H5 contrast with a current-era p-value, and the
registration's own text-only exclusion (line 624) forces the **image
track**.

| field | value |
| --- | --- |
| `phase` | "Phase 2d T1: H5 Negtext (Image)" |
| `condition_a` / `condition_b` | `terse` / `verbose` |
| `precision_delta` | −0.006023599105863865 |
| **`precision_p`** | **0.756** |
| `f1_p_value` (tertiary metric, for reference) | 0.85 |

**Divergences**:

- The registered headline contrast is unavailable at current era. On the
  original 60-tile registered corpus all three levels *were* run —
  `results/phase2d-track1-image-analysis.json`
  (`per_condition_metrics` carries `minimal`, `terse`, `verbose`) — but
  that artefact reports **confidence intervals only, no p-values**
  (`pairwise_comparisons[i].precision_difference` has `mean`, `ci_lower`,
  `ci_upper`), so it cannot supply a BH input without recomputation.
- The registered "within each M/E level" stratification is inestimable:
  only one image-based M/E level (`brief-text-image`) received H5 variants
  (E28; `reports/d17-inventory/unexecuted-register.md` § E-12), which also
  makes the registered M/E × H5 difference-of-differences interaction test
  (`CMT-0186`) inestimable (§ A-02).
- Text-track counterpart, **not selected** (excluded by
  `preregistration.md:624`): `comparisons[54]`, `precision_p` = 0.862.

**PI check requested**: confirm that the image-track terse-vs-verbose
precision contrast is an acceptable stand-in for a hypothesis whose
registered headline never ran, or rule that H5 be reported as
**unresolvable** and the family reduced to six.

---

### 5.6 H6 — Optimisations transfer from Gemini 3 Flash to Pro — **EXCLUDED**

**Status: NEVER RUN.** Excluded from the family per the PI decision at
`planning/audit-and-completion-plan.md` § 4 line 119
("7; H6 never ran").

**Evidence of non-execution** (`reports/d17-inventory/unexecuted-register.md`
§ E-01, verbatim):

> **Not at all.** No run in `results/runs-manifest.json` (31 runs) carries
> `primary_hypothesis: "H6"`. `studies/phase4-transfer.yaml` still holds 13
> `PLACEHOLDER` strings (`:28,31,32,35,38,41,44,47,48,103,104,105,106`).
> `inputs/tiles/phase4_validation_manifest.json` and
> `inputs/vectors/bounds/phase4_validation_bounds.geojson` do not exist.
> `scripts/analyse_phase4_transfer.py` does not exist.
> `execution-checklist.md:108` (Phase 4 row) is blank.

**E41-licensed substitution, noted and NOT used as an H6 primary.** The
Pro-versus-Flash work that exists is the `n1-baseline-matrix-384`
leaderboard (`results/analyses-manifest.json`, `analysis_id` =
`n1-baseline-matrix-384`, `hypothesis_refs` = `["H1", "H6", "H7"]`,
`preregistered` = `"exploratory"`, `deviations` = `["E57"]`). E41
(`docs/methodology/preregistration/protocol-errata.md:1019-1033`) records
its status verbatim:

> The preregistered H6 (Flash→Pro transfer, §3.6) specifies a 20-tile
> stratified holdout subset at 512px tile size. Our Pro comparison uses 487
> tiles at 384px — the optimal tile size identified by the H11 diagnostic
> (Obs 181).

and:

> The Pro comparison is best characterised as an exploratory extension
> rather than a strict implementation of H6.

The `n1-baseline-matrix-384` board therefore **cannot** supply an H6
primary p-value: it is licensed as exploratory by E41 and by a dated
PI-approved provenance decision (`reports/d17-inventory/step0-h6-walkthrough.md`
§ 0: "labelling the analysis `exploratory` and expressly denying it is H6's
confirmatory test"). Including it would import an exploratory result into a
confirmatory family.

**Consequence for reporting**: the paper must state that the registered
confirmatory family comprised eight hypotheses, that one (H6) was never
executed, and that the BH correction is therefore over seven. E40 (Pro
cannot run `thinking_level=minimal`) means a strictly compliant H6 is no
longer obtainable even in principle.

---

### 5.7 H7 — Temperature affects detection performance

**Registered primary analysis** (`CMT-0217`, `preregistration.md:727`),
verbatim:

> - Pairwise bootstrap comparisons across 5 temperature levels (95% CIs,
>   FDR-corrected)

`decision_statistic` field of `CMT-0217`, verbatim: `F1`.

**Registered planned contrasts** (`CMT-0218`, `preregistration.md:728`),
verbatim:

> - Planned contrasts: T=1.0 vs each other level

**Registered advance rule** (`CMT-0222`, `preregistration.md:733`),
verbatim:

> **Advance to Stage 2 if**: Any temperature significantly outperforms
> T=1.0, or if escalation trigger activates and higher or low temperatures
> show improvement.

**Executed artefact**: `results/retest/pairwise-bootstrap-comparisons.json`
(Era 1, 340 tiles). Field: `comparisons[i].f1_p_value`.

**VERDICT: AMBIGUOUS.** The registration names a contrast *set* ("T=1.0 vs
each other level"), not a single contrast, and the dual-track split
(image versus text) is itself a post-lodgement construct (E27,
Decision 16) with no registered primary track. No omnibus across the five
levels was executed.

**Selection is not outcome-material**: every candidate sits at the
bootstrap resolution floor of p = 0.001 (B = 1 000 iterations).

| option | contrast | artefact index | `f1_delta` | `f1_p_value` |
| --- | --- | --- | --- | --- |
| **(i)** text track, best alternative vs vendor default | `T0.3` vs `T1.0` | `comparisons[25]` | +0.09584910578988215 | **0.001** |
| (ii) image track, best alternative vs vendor default | `T0.0` vs `T1.0` | `comparisons[12]` | +0.06390203981488053 | **0.001** |
| (iii) text track, T = 0.0 vs vendor default | `T0.0` vs `T1.0` | `comparisons[22]` | +0.0930388572836824 | **0.001** |

**Recommended default**: option (i) — the largest registered
T = 1.0-versus-alternative effect, on the track carrying the study's
optimum (`results/phase2b-carry-forward-parameters.md`: Track 2 optimum
T = 0.3, F1 = 0.606).

**Note on the p-value floor**: 0.001 is the smallest value the bootstrap
can report at B = 1 000. It must be recorded as **p ≤ 0.001**, not as an
exact value, and its BH rank handled accordingly (see § 8.3).

**Current-instrument cross-check**:
`results/era1-leaderboard/tiering_20m.json` `pairwise[837]`
(`retest-phase2b::text-t0.3` vs `retest-phase2b::text-t1.0`), `p_value` =
0.0, `bh_adjusted_p` = 0.0; and `pairwise[397]` (image T0.0 vs T1.0),
`p_value` = 0.0.

**Trigger context, for the record**: the H7 escalation trigger
(`CMT-0220`, `preregistration.md:731`) fired as written on a point
estimate and was judged uninformative; recorded in **E60** and in
`planning/audit-and-completion-plan.md` § 6.1. This does not affect the
primary-test selection.

---

### 5.8 H8 — Library composition and scaling

**Registered primary analysis** (`CMT-0259`, `preregistration.md:821`),
verbatim:

> - **Primary**: Pairwise bootstrap comparisons across 7 library
>   conditions (95% CIs, FDR-corrected)

`decision_statistic` field of `CMT-0259`, verbatim: `F1`.

**Registered planned contrasts** (`CMT-0239`–`CMT-0245`,
`preregistration.md:781-797`), verbatim:

> | C1 | Pure Positive Canon → Canonical | Does Canon- help? | Canon+ constant (4), HP=0, HN=0 |
> | C2 | Canonical → +HP | Do HP help? | Canon+/- constant, HN=0 |
> | C3 | +HP → Scale-8 | Do HN help? | Canon+/- constant, HP constant (4) |
> | S1 | Scale-4 → Scale-8 | 4 → 8 | Initial scaling value |
> | S2 | Scale-8 → Scale-16 | 8 → 16 | Mid-range scaling |
> | S3 | Scale-16 → Scale-32 | 16 → 32 | Ceiling/diminishing returns |
> | B1 | +HP vs Scale-4 | At matched total (13 examples): is 4+0 or 2+2 better? |

**Registered advance rule** (`preregistration.md:828`), verbatim:

> - Significant main effect of library composition (FDR-corrected p <
>   0.05), OR

**Executed artefact**: `results/h8-v2/permutation-t4/fdr_summary.json`
(Era 3, 327 tiles, greedy consensus t = 4, 20 m buffer, 10 000
permutations, seed 42; `method` = "Benjamini-Hochberg FDR at q=0.05 over 7
H8 preregistered contrasts", `any_significant` = false). Fields:
`contrasts[i].p` (raw) and `contrasts[i].bh_adjusted_p` (within-H8).

**VERDICT: AMBIGUOUS.** All seven registered contrasts were executed, but
the registration names no single headline among them and no omnibus
"main effect" test exists — the advance rule at line 828 asks for a
"main effect" the analysis section never operationalises.

**Selection is not outcome-material**: all seven contrasts are null, raw
p from 0.1636 to 0.932.

| option | contrast | array index | `delta` | raw `p` | within-H8 `bh_adjusted_p` |
| --- | --- | --- | --- | --- | --- |
| **(i)** minimum-p contrast — the "any significant difference between conditions" reading | B1 (`plus-hp` vs `scale-4`) | `contrasts[3]` | −0.027578 | **0.1636** | 0.8344 |
| (ii) the registration's own named component question — H5 background at `preregistration.md:582` states "The question of *whether* negatives help is now answered by H8 (contrast C3: +HP → Scale-8)" | C3 (`plus-hp` vs `scale-8`) | `contrasts[2]` | −0.004956 | **0.8538** | 0.932 |
| (iii) hypothesis-level summary — the smallest within-H8 BH-adjusted p, treating the existing seven-contrast correction as the H8 test | B1 | `contrasts[3]` | −0.027578 | — | **0.8344** |

**Recommended default**: option (i), with the explicit caveat that a
minimum-p statistic is anti-conservative inside a second BH step-up.
Option (iii) is the conservative alternative and is defensible precisely
because the within-H8 correction is already registered
(`preregistration.md:821` requires the seven-condition comparison to be
FDR-corrected).

**Divergences**: permutation not bootstrap (E45); Era 3 (327 tiles at
384 px) under the production carry-forward, not the registered 60-tile
512 px design (E51 records 15 deviations from the original Phase 2c H8);
greedy consensus at t = 4 as the aggregation, per Decision 26.

**Era-1 predecessor, not selected**: the original Phase 2c H8 ran only
five of the seven library conditions
(`results/retest/pairwise-bootstrap-comparisons.json`, "Phase 2c T1/T2",
20 contrasts; Scale-16 and Scale-32 absent). Its only nominally
significant row is `plus-hp` vs `scale-4` on the text track
(`f1_p_value` = 0.001, ΔF1 = −0.0127) — a 0.013 F1 difference that
`results/retest/retest-production-summary.md` itself describes as "a tiny
effect". The Era-3 re-run supersedes it.

---

## 6. Summary — the seven primary tests

| H | primary contrast | artefact | field | p (two-sided) | status |
| --- | --- | --- | --- | ---: | --- |
| H1 | Image-only vs Brief-text+image (F1) | `results/retest/pairwise-bootstrap-comparisons.json` | `comparisons[4].f1_p_value` | 0.006 | **AMBIGUOUS** (default) |
| H2 | Flash HIGH text 16-of-30 + PV vs Flash HIGH text 26-of-30 (F1) | `results/pairwise/20m/group_1_architecture/pv-vs-consensus-flash-high-text-16-of-30-pv-vs-flash-high-text-26-of-30.json` | `permutation_test.p_value` | 0.0 (< 1e-4) | SELECTED |
| H3 | consensus-flash-high-text-26of30 vs matched single-pass (F1) | `results/diversity-dividend-384/tiering-champions/tiering_20m.json` | `headline_contrasts[2].p_value` | 0.0 (< 1e-4) | SELECTED |
| H4 | canonical-first vs canonical-last (F1) | `results/retest/pairwise-bootstrap-comparisons.json` | `comparisons[55].f1_p_value` | 0.124 | SELECTED |
| H5 | terse vs verbose, image track (**precision**) | `results/retest/pairwise-bootstrap-comparisons.json` | `comparisons[53].precision_p` | 0.756 | SELECTED (by constraint) |
| H6 | — | — | — | — | **EXCLUDED — never run** |
| H7 | T = 0.3 vs T = 1.0, text track (F1) | `results/retest/pairwise-bootstrap-comparisons.json` | `comparisons[25].f1_p_value` | ≤ 0.001 | **AMBIGUOUS** (default) |
| H8 | B1: plus-hp vs scale-4 (F1) | `results/h8-v2/permutation-t4/fdr_summary.json` | `contrasts[3].p` | 0.1636 | **AMBIGUOUS** (default) |

**Three AMBIGUOUS flags (H1, H7, H8).** Of these, only H1 is
outcome-material; H7's candidates are all at the bootstrap floor and H8's
are all null.

---

## 7. Divergence register

### 7.1 Tail direction — two-sided throughout

The registration specifies (`preregistration.md:269`): "One-tailed for
directional predictions; two-tailed for equivalence tests (H1)". Four
places carry an explicit one-tailed rule: H1's elaboration contrast
(`CMT-0108`), H2 (`CMT-0124`), H3 (`CMT-0138`), and H4 (`CMT-0147`).

**Every executed test in this repository is two-sided.** The operative
reading — two-sided throughout — is the E64 draft's, and is recorded in
committed form at `reports/verification/phase1-gate-package.md:66-68`,
verbatim:

> The one-tailed rule bites H2/H3/H4 + one H1 contrast only, and the
> executed two-sided test is strictly conservative; no tailedness licence
> exists anywhere.

**Anchor caveat, stated plainly**: E64 itself is **not yet on disk**. The
errata register `docs/methodology/preregistration/protocol-errata.md`
currently ends at **E61**; E62–E67 exist only as a drafting pass recorded
at `reports/verification/phase1-gate-package.md:316` ("The E62–E67
drafting pass re-verified every specific and caught two package errors").
The reconciliation erratum they belong to is item 3 of the GATE 1 erratum
queue (`phase1-gate-package.md:176-181`), which names "one-tailed rule vs
registered two-tailed instances" among the registration-internal
contradictions to be reconciled. **This registration should not be
finalised until E64 is filed**, or should record explicitly that it
anticipates E64's operative reading.

Consequence for H4, the only case where tail choice changes the numeral:
two-sided p = 0.124 versus one-tailed p ≈ 0.062. Both are null at
α = 0.05; the two-sided value is used and is conservative.

Consequence for H2: the executed direction is opposite to the registered
alternative. A one-tailed test in the registered direction would give
p ≈ 1.0. The two-sided reading (p < 1 × 10⁻⁴, favouring two-stage) is used
and must be reported as a **falsified directional prediction**, not as a
confirmation.

### 7.2 Inference method — bootstrap versus permutation (E45)

The registered method is bootstrap CIs (§ 3.5, line 293) with BH-FDR
(§ 3.1, line 270). E45
(`docs/methodology/preregistration/protocol-errata.md:1156`) is titled
"Unregistered inference method — tile-swap permutation testing (corrected
2026-07-28…)" and states, verbatim:

> **There was never a preregistered permutation test to deviate from.**
> `permutation` appears zero times in the lodged registration…

and:

> The registered analysis for confirmatory hypotheses is bootstrap CIs +
> BH-FDR, and must be reported alongside permutation results wherever
> confirmatory claims are made.

**Family composition under this constraint**: four primaries (H1, H4, H5,
H7) come from the registered bootstrap instrument; three (H2, H3, H8) come
from permutation artefacts because no bootstrap execution of those
contrasts exists at the current era. This is disclosed, not hidden.

**A uniform-instrument variant is not available.** A
permutation-only family cannot supply H5's primary: the registered H5
statistic is **precision**, and the permutation leaderboards
(`results/era1-leaderboard/tiering_20m.json`, `metric` = `"f1"`) compute
F1 only.

### 7.3 Corpus heterogeneity

| H | corpus | tiles | tile size | era |
| --- | --- | ---: | --- | --- |
| H1, H4, H5, H7 | Era 1 retest | 340 | 512 px | 1 |
| H2, H3 | Era 2 (`pv-diag-384`, `h11`) | 487 | 384 px | 2 |
| H8 | Era 3 (`h10-384` test set) | 327 | 384 px | 3 |

The three sets are **strictly nested** (Era 3 ⊂ Era 2 ⊂ Era 1, 100.000 %
area containment, zero mounds unique to a smaller scope —
`results/evaluation-scopes.md` § 3). None is the registered 60-tile
holdout; the expansion is licensed by E36. The heterogeneity is the
condition the correction must be reported under, and matches the
`unexecuted-register.md` § A-01 diagnosis, verbatim:

> The eight confirmatory hypotheses now have heterogeneous inference
> (bootstrap CI pseudo-p in Era 1; tile-swap permutation in the
> leaderboards), different scopes (60/327/340/487 tiles), and H6 has no
> result at all.

### 7.4 Other structural divergences carried into the family

| H | erratum | divergence |
| --- | --- | --- |
| H2 | E37 | PV pipeline is the production implementation of registered Condition B |
| H2 | E58 | registered proposer prompt `propose_brief` never used |
| H2 | E59 | Condition C (fine-to-coarse) never executed, never formally dropped |
| H3 | E53 | Phase 3a-HIGH image track moved from 512 px (Era 1) to 384 px (Era 2) |
| H4 | E30 | Phase 2e tests 4 ordering conditions instead of the preregistered 3 |
| H5 | E28 | single-factor OFAT replaced the registered 3 × 3 M/E × H5 design |
| H7 | E60 | escalation trigger fired on a point estimate; escalation not run |
| H8 | E51 | H8 re-run under production carry-forward, 384 px / v2 pipeline (15 deviations) |
| all | E36 | corpus expansion beyond the registered 60-tile holdout |
| all | E54 | bootstrap iteration count (1 000 primary; 10 000 for narrow effects) |

---

## 8. The BH-FDR procedure

### 8.1 Specification

- **Family**: the seven primary p-values in § 6 (H1, H2, H3, H4, H5, H7,
  H8). H6 excluded as never-run.
- **q**: 0.05, per `preregistration.md:270`.
- **Procedure**: Benjamini–Hochberg step-up. Order the seven p-values
  ascending as p₍₁₎ ≤ … ≤ p₍₇₎. Find the largest k such that
  p₍ₖ₎ ≤ (k / 7) · q. Reject H₍₁₎ … H₍ₖ₎.
- **Adjusted p-values**: p_adj₍ₖ₎ = min over j ≥ k of (7 / j) · p₍ⱼ₎,
  clipped at 1.0 (the standard monotone step-up adjustment, matching
  `scripts/apply_fdr_correction.py` as used for the existing 26-row
  family).
- **Reporting**: both uncorrected and adjusted p-values, per
  `preregistration.md:295`.
- **Implementation**: to be run on sapphire (project CLAUDE.md compute
  rule); a single script under `scripts/`, tier-1 tested, writing to
  `results/family-fdr/` with a `.metadata.json` sidecar.

### 8.2 Fixed before execution

Family membership; the artefact and field for each p-value; q; the
step-up procedure; the tie-handling rule (§ 8.3); and the sensitivity
analysis (§ 8.4). Nothing about the family may be revised after the
correction is computed without a dated amendment block in this document.

### 8.3 Resolution floors and ties

Two primaries sit at instrument resolution floors and must be recorded as
inequalities, not point values:

- **Bootstrap floor**: H7 at `f1_p_value` = 0.001 with B = 1 000 is
  **p ≤ 0.001**.
- **Permutation floor**: H2 and H3 at `p_value` = 0.0 with 10 000
  permutations are **p < 1 × 10⁻⁴**. The literature-standard reporting is
  (b + 1)/(B + 1) = 1/10 001 ≈ 9.999 × 10⁻⁵; this registration adopts
  that convention rather than a literal zero.

**Tie rule**: where two p-values are equal at the floor, they are assigned
consecutive ranks in the order H2, H3, H7 (fixed here, before execution,
so that rank assignment cannot be chosen on results). BH adjusted p-values
are identical for tied inputs under the monotone step-up, so this rule is
presentational only.

### 8.4 The sensitivity analysis

The **all-contrasts correction already committed** at
`results/pairwise/20m/fdr/pairwise_results_fdr.json` is reported alongside
the family-level correction, per the PI decision at
`planning/audit-and-completion-plan.md` § 4 line 119 ("all-contrasts
correction as a reported sensitivity").

Verified properties of that artefact:

| property | value | source |
| --- | --- | --- |
| total rows | 32 | `metadata.n_comparisons` |
| **confirmatory rows** | **26** | `comparisons[i].family == "confirmatory"` |
| exploratory rows | 6 | same field |
| method | "Benjamini-Hochberg" | `metadata.fdr_correction.method` |
| generated by | `apply_fdr_correction.py` v1.0.0, 2026-03-28T06:54:43Z | `metadata.fdr_correction` |
| test | tile-swap permutation, 10 000 permutations, seed 42 | `metadata` |
| buffer / corpus | 20 m / 487 tiles (Era 2) | `metadata.buffer_metres`, `comparisons[i].n_tiles` |
| significant | 20 of 26 confirmatory | `results/pairwise/20m/fdr/pairwise_results_fdr.md` § "Confirmatory (20/26 significant)" |

The correction is applied **within family**: the 26 confirmatory rows are
corrected together and the 6 exploratory rows separately (verified by
re-deriving the adjusted values — e.g. `comparisons[29].p_value_raw` =
0.0375 → `p_value_adj` = 0.0488 = 0.0375 × 26/20).

**How the two are contrasted in the paper**: the family-level correction
answers "which of the seven registered confirmatory hypotheses survives
FDR control?"; the all-contrasts correction answers "which of the 26
executed confirmatory comparisons survives?". The first is the registered
question; the second is what practice actually delivered. Reporting both
side by side is the GATE 1 ruling 7(c) "promised-versus-chosen" pattern.

**Caveat to record**: the 26-row family is not a superset of the seven
primaries. It contains no H4, H5, H7, or H8 rows at all, and its H1 limb
is the Era-2 HIGH-thinking text-versus-image comparison rather than the
registered M/E-level contrasts. The two corrections are complementary
views, not nested ones.

### 8.5 Deliverables

1. `results/family-fdr/family_fdr.json` — the seven inputs (with artefact
   path and field for each), the adjusted p-values, the rejection set, and
   a `provenance` block naming this registration.
2. `results/family-fdr/family_fdr.md` — human-readable table, with the
   revision-policy banner and changelog.
3. A side-by-side section reporting the all-contrasts sensitivity.
4. A ledger row per charter § 6.
5. A Methods/Discussion disclosure paragraph explaining why practice
   deviated (GATE 1 ruling 7(d)).

---

## 9. `predicted_outcome`

**This registration does not, and cannot, claim outcome blindness.** Every
one of the seven p-values is already committed to this repository, was
read during the drafting of this document, and is quoted verbatim in § 5.
Anyone can compute the BH result from § 6 in under a minute. Saying
otherwise would be false.

**What the registration does fix is the family selection**: which
hypotheses are in, which single contrast represents each, which artefact
and field supplies its p-value, how ties and resolution floors are
handled, and what the sensitivity analysis is. Those are the degrees of
freedom that could otherwise be exercised after seeing the correction —
dropping a null hypothesis from the family, swapping H1's contrast for a
more favourable one, or promoting the all-contrasts result to primary
because it looks better. The commit timestamp on this file makes those
moves auditable. That is a real but **strictly weaker** guarantee than
preregistration, and the paper must describe it in exactly those terms.

**Prediction (stated for the record, given visible inputs)**:

1. H2, H3 and H7 will be rejected at q = 0.05 (all at or near their
   instrument floors).
2. H1 will be rejected under the recommended default (p = 0.006) and under
   option (iii) (p = 0.004); it is **the single selection whose resolution
   changes the rejection set**, since option (ii) at p = 0.38 would not
   survive.
3. H4 (p = 0.124), H5 (p = 0.756) and H8 (p = 0.1636 at best) will not be
   rejected under any of the candidate selections.
4. The family-level and all-contrasts corrections will agree on direction
   for every hypothesis they share, and will differ chiefly in coverage —
   the 26-row family says nothing about H4, H5, H7 or H8.

**Falsifiable commitments in that prediction**: item 2 is the one that
matters. If the PI selects H1 option (ii), the rejection set shrinks by
one. Recording this before the ruling is the point of the exercise.

**What this registration cannot rescue**: the registered family-level
correction was **deferred and never resolved**
(`results/retest/pairwise-bootstrap-comparisons.json`,
`metadata.note` = "Raw p-values — FDR correction deferred until all data
available"; `results/retest/retest-production-summary.md`: "FDR correction
is **deferred** until all experimental data are available"). Running it now
discharges the obligation; it does not make it prospective. The Methods
disclosure must say so.

---

## 10. Companion metadata (to commit with this document)

Per `planning/audit-and-completion-plan.md` § 6.4, an entry in
`results/run-analyses.json` with `status: planned`:

```json
{
  "analysis_id": "family-bh-fdr-confirmatory",
  "hypothesis_refs": ["H1", "H2", "H3", "H4", "H5", "H7", "H8"],
  "preregistered": "preregistered",
  "deviations": ["E28", "E30", "E36", "E41", "E45", "E51", "E53", "E54", "E58", "E59", "E60"],
  "predicted_outcome": "See reports/verification/family-fdr-registration.md § 9. Family selection fixed before computation; p-values already visible in-repo — this is not outcome blindness. Predicted rejections at q=0.05: H2, H3, H7, and H1 under the recommended default; H4, H5, H8 not rejected.",
  "outcome": null,
  "paper_section": "Methods — statistical analysis; Results — confirmatory family"
}
```

---

## 11. Open questions requiring a PI ruling before execution

1. **H1 (outcome-material)**: which of the three candidate primaries in
   § 5.1? The default is option (i), p = 0.006.
2. **H7 (immaterial)**: which track? Default option (i), text track,
   p ≤ 0.001.
3. **H8 (immaterial)**: minimum-p contrast (option i), the registration's
   named C3 (option ii), or the within-H8 BH-adjusted minimum (option iii)?
4. **H5**: accept the constrained substitute (terse vs verbose on
   precision, image track) or declare H5 unresolvable and reduce the
   family to six?
5. **E64**: file the reconciliation erratum before executing the
   correction, or execute now and record the anticipated operative
   reading? § 7.1 recommends the former.
6. **Reporting of H2**: confirm that the falsified directional prediction
   is reported as such — a two-stage architecture that *significantly
   improves* F1 by +0.076, clearing the registered ≥ 0.05 stopping-rule
   threshold in the direction the registration predicted it would not.

---

## Changelog

### 2026-07-30 — Original publication

Drafted as the rule-10 pre-execution registration for the registered-family
BH-FDR correction, per `planning/audit-charter.md` § 5 rule 10, the PI
decision at `planning/audit-and-completion-plan.md` § 4 line 119, and GATE 1
ruling 7(d) (`planning/audit-charter.md` § 10 item 7(d)). Contents: verbatim
registered primary tests for H1–H8 from `results/commitments.json` and the
lodged `preregistration.md`; the executed artefact, JSON field, and p-value
for each of the seven executable hypotheses; H6 recorded as never-run with
the E41-licensed `n1-baseline-matrix-384` substitution noted and excluded;
three AMBIGUOUS flags (H1, H7, H8) with candidate options and p-values; the
BH procedure at q = 0.05 over seven primaries; the all-contrasts sensitivity
(26 confirmatory rows at
`results/pairwise/20m/fdr/pairwise_results_fdr.json`); and a
`predicted_outcome` section stating plainly that the p-values are already
visible and that this registration fixes family selection, not outcome
blindness. Repository anchor at drafting:
`562d185a44b33d4c3f3c504d1e5981767c896df8`. **Status: DRAFT — not yet
executed, awaiting PI rulings on the six items in § 11.**
