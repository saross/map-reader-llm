# Register of registered-but-unexecuted work — VLM burial-mound detection

**Compiled**: 2026-07-28. **Repository**: `/home/shawn/Code/map-reader-llm` (read-only
inspection; no repository files were created, edited, or committed).

**Registration of record**: `docs/methodology/preregistration/osf/preregistration.md`
(v4.6 in the header at `:9`, v4.7 in the changelog at `:2394`). All `preregistration.md:N`
anchors below are to that file. Lodged **2026-01-31 23:54 UTC**
(`docs/methodology/preregistration/execution-checklist.md:61`).

**The bright line.** Anything decided before lodgement fed into writing the registration
and is baked in. Pre-lodgement drafting material is used below only to explain *why the
registration says what it says*, or as the sole surviving costing for a registered item —
never as authority for what should have been run. Where a pre-lodgement figure is the only
cost anchor available, it is labelled as such.

**Trust policy.** `hypothesis-tracking.md`, `docs/methods-outline.md`,
`docs/paper/results-outline.md`, and the phase status tables have all been shown to carry
stale or invented content, and are treated here as **untrusted**. Every execution claim
below was re-derived from `results/runs-manifest.json`, `results/conditions-manifest.json`,
`results/passes-manifest.json`, `results/analyses-manifest.json`, `studies/*.yaml`,
`config.py`, the `results/` artefact tree, or `protocol-errata.md`. Where a claim rests on
a prior inventory that I did not independently re-derive, it is marked
**[prior-inventory]**.

**Counts** — **46 distinct items** across 48 rows:

- **17 experiments** (§ 1, E-01 … E-17) — unexecuted or partially executed registered
  hypotheses, conditions, factors, and protocol elements.
- **25 analyses** (§ 2, A-01 … A-19, plus § 3, A-20 … A-25) — registered analyses never
  performed or performed differently, and registered documentation/reporting commitments
  not discharged.
- **6 triggers** (§ 4, T-01 … T-06) — of which **4 were not honoured** (T-01 fired and
  ignored; T-03 fired and ignored; T-04 unevaluable because its gating analysis was never
  run; T-05 arguably fired and never formally evaluated), 1 is arguably discharged by
  construction (T-02), and 1 did not fire but was deliberately overridden and disclosed
  (T-06). **T-03 and T-04 are cross-references to E-10 and E-11**, hence 46 distinct items
  rather than 48.

A further 4 triggers were checked and found to impose no obligation; they are listed at the
end of § 4 for completeness and are not counted.

---

## 1. Experiments — unexecuted or partially executed

### E-01 · H6 Phase 1 — Pro baseline at Flash-optimal

| field | content |
|---|---|
| **Registered at** | `preregistration.md:659-664` |
| **Status** | Confirmatory (Tier 3, `preregistration.md:2168`) |
| **What was registered** | "Run Flash-optimal configuration on Pro: K=10 runs on 20 stratified holdout tiles (subset of 60, preserving density distribution); Compare Pro vs Flash performance at matched configuration; Establish baseline for factor sensitivity testing" |
| **Executed?** | **Not at all.** No run in `results/runs-manifest.json` (31 runs) carries `primary_hypothesis: "H6"`. `studies/phase4-transfer.yaml` still holds 13 `PLACEHOLDER` strings (`:28,31,32,35,38,41,44,47,48,103,104,105,106`). `inputs/tiles/phase4_validation_manifest.json` and `inputs/vectors/bounds/phase4_validation_bounds.geojson` do not exist. `scripts/analyse_phase4_transfer.py` does not exist. `execution-checklist.md:108` (Phase 4 row) is blank. |
| **Run instead** | `n1-pro-rerun-384` and `pv-diag-384` (both `primary_hypothesis: "H11"` in `results/runs-manifest.json`), 487 tiles at 384 px on the 4-map gold-standard corpus, crossing modality × thinking level × temperature. Pro conditions: `n1-pro-rerun-384::baseline-pro-{image,text}-{high-t-0-0,medium-t-0-7}`, `pv-diag-384::baseline-pro-{image,text}-{high-t-0-7,medium-t-0-0}`. |
| **Decision on record?** | **No formal decision.** The nearest is a deferral for a competing deadline (2026-03-11) recorded only in a session transcript **[prior-inventory]**. `docs/methods-outline.md:341` records the reason as "budget prioritised for Flash experiments" — arithmetically false against a $48 registered cost, and identified as assistant-invented **[prior-inventory]**. E41 (`protocol-errata.md:960-972`) records only that the Pro work *is not* H6, never that H6 was dropped. |
| **Cost to run now** | **US$48 maximum**, the study's own costing at `studies/phase4-transfer.yaml:165` (1,600 calls at `per_call: 0.03`, `:161`, annotated "Pro pricing (~10× Flash), verify at execution"). Corroborated at `execution-plan.md:723` ("~$42-48"). This is a January-2026 estimate at 512 px on 20 tiles; it has not been re-priced. |
| **Feasibility now** | Scaffolding intact: `scripts/lib_phase4_transfer.py` and `scripts/select_tiles_phase4.py` exist. Missing: the 20-tile manifest and bounds, the YAML placeholders, and the analysis driver. **But E40 (`protocol-errata.md:944-958`) means a re-run still deviates** — Gemini 3.1 Pro cannot run `thinking_level=minimal`, so a Pro-vs-Flash contrast at matched thinking is not obtainable at all. |
| **Blocks a paper claim?** | **Yes.** Any claim that H6 (Flash→Pro transfer) was tested. `docs/paper/results-draft.md` contains no "H6" string **[prior-inventory]** — currently the study neither reports H6 nor discloses its non-execution. |

### E-02 · H6 OFAT factor — M/E ("2 adjacent levels")

| field | content |
|---|---|
| **Registered at** | `preregistration.md:670-675` (factor table row 1) |
| **Status** | Confirmatory |
| **What was registered** | "\| M/E \| 2 adjacent levels \| Does Pro prefer more/less text? \|" |
| **Executed?** | **Partially.** Pro was run at text vs image only — not two adjacent levels of the registered 5-level M/E ladder (Image-only, Brief+image, Verbose+image, Brief-text, Verbose-text; `preregistration.md:1740`). |
| **Run instead** | `n1-pro-rerun-384::baseline-pro-{image,text}-*` and `pv-diag-384::baseline-pro-{image,text}-*`. |
| **Decision on record?** | No. `docs/methodology/preregistration/tasks/phase4-remaining-tasks.md:43` ("Identify OFAT alternative levels for M/E") is still "☐ Pending". |
| **Cost to run now** | Folded into E-01's $48 (`studies/phase4-transfer.yaml:165`); the YAML costs Phase 4b (all four OFAT factors) at $36 (`:163`). |
| **Feasibility now** | High — the Pro pathway is proven at 384 px; the registered form requires the 512 px 20-tile manifest first. |
| **Blocks a paper claim?** | Yes — any claim that M/E transfer was tested OFAT-style on Pro. |

### E-03 · H6 OFAT factor — H5 ("2 alternatives")

| field | content |
|---|---|
| **Registered at** | `preregistration.md:670-675` (factor table row 2) |
| **Status** | Confirmatory |
| **What was registered** | "\| H5 \| 2 alternatives \| Does Pro need different hard negative approach? \|" |
| **Executed?** | **Not at all.** `grep -l "h5_level\|ordering" studies/h11-384-pro-*.yaml studies/h11-384-n1-outstanding.yaml` returns nothing — no Pro study varies the H5 factor. |
| **Run instead** | Nothing. Thinking level (MEDIUM/HIGH) was varied instead — not a registered H6 factor, and forced by E40. |
| **Decision on record?** | No. `phase4-remaining-tasks.md:44` still "☐ Pending". |
| **Cost to run now** | Within E-01's $48 (`studies/phase4-transfer.yaml:165`). |
| **Feasibility now** | High — H5 instruction variants exist (`prompts/system-instructions/detect_brief-text-image_{terse,verbose}.md`). |
| **Blocks a paper claim?** | Yes — any "transfer confirmed" verdict, which requires all four factors. |

### E-04 · H6 OFAT factor — Ordering ("2 alternative orderings")

| field | content |
|---|---|
| **Registered at** | `preregistration.md:670-675` (factor table row 4) |
| **Status** | Confirmatory |
| **What was registered** | "\| O \| 2 alternative orderings \| Does ordering effect transfer? \|" |
| **Executed?** | **Not at all.** Same grep as E-03 returns nothing. |
| **Decision on record?** | No. `phase4-remaining-tasks.md:46` still "☐ Pending". |
| **Cost to run now** | Within E-01's $48. |
| **Feasibility now** | High — `reorder_examples()` supports all four orderings post-E29 (`protocol-errata.md:669-690`). |
| **Blocks a paper claim?** | Yes — same as E-03. |

*(H6's fourth registered OFAT factor, temperature, **was** varied on Pro — T=0.0 vs T=0.7 — albeit at 384 px on 487 tiles rather than the registered scope. No row; noted for completeness.)*

### E-05 · H6 Phase 4 — conditional refinement

| field | content |
|---|---|
| **Registered at** | `preregistration.md:685-689` |
| **Status** | Confirmatory (conditional) |
| **What was registered** | "If Phase 2 identifies factors needing adjustment: Test one additional level in the indicated direction; For voting: if threshold differs >20%, run N=30 at Pro-adjusted config" |
| **Executed?** | **Not at all** — and not evaluable, because Phase 2 (E-02 to E-04) never produced the inputs. |
| **Decision on record?** | No. |
| **Cost to run now** | $6 conditional, `studies/phase4-transfer.yaml:164` ("phase4d: 6 # Conditional"). |
| **Feasibility now** | Contingent on E-01 to E-04. |
| **Blocks a paper claim?** | Only insofar as E-01 to E-04 do. |

### E-06 · H2 Condition C — fine-to-coarse (context expansion)

| field | content |
|---|---|
| **Registered at** | `preregistration.md:469` (condition table), implementation at `:478-484` |
| **Status** | Confirmatory (architectural, `preregistration.md:453`) |
| **What was registered** | "\| C \| Fine-to-coarse \| Standard detection → context-expanded re-query for uncertain cases \|"; implementation: "Stage 1: Standard detection on 512×512 tiles with 5-pass voting; Identify uncertain candidates: Detections with 2/5 or 3/5 agreement; Stage 2: For each uncertain candidate, extract larger tile (~1024×1024) centred on candidate, re-query with verification prompt" |
| **Executed?** | **Not at all.** `prompts/configs/` has `propose_*.json` and `verify_*.json` but no `expand_*.json`; `prompts/system-instructions/` has no `expand_*.md` — the files `preregistration.md:2015` names as H2-C's implementation **[prior-inventory]**. |
| **Run instead** | Condition B (coarse-to-fine) was executed extensively as the proposer-verifier programme (runs `verifier-t-pilot`, `verifier-robustness` with `primary_hypothesis: "H2"`, plus `proposer-verifier-{384,512}`, `pv-diag-{256,384}`, `flash35-pv-2x2` under H11). A *fine-to-coarse approximation* ran as "Strategy 10" in `analyze_multiscale_voting.py` (7 configurations, best F1 0.533), but with fixed grid tiles and a detection prompt rather than candidate-centred crops with a verification prompt **[prior-inventory]**. |
| **Decision on record?** | **No — only post-hoc rationalisation.** `hypothesis-tracking.md:86-87` says C "was not tested — the coarse-to-fine results were strong enough that context expansion was deprioritised", added 2026-03-15 **[prior-inventory]**. That reason is invalid under the registered logic: the registration predicted *neither* architecture would help, and C tests the opposite mechanism independently. No erratum covers the drop. |
| **Cost to run now** | **UNVERIFIED — would need a 1024 px crop pricing run.** The audited comparator in the repo is for 384 px crops (`results/analyses-manifest.md:24`, `pass-budget-pareto-v2`, costs rebuilt 2026-06-12 from per-item token metadata: min6 $2.43, min11 $4.00 at 487 tiles). 1024 px is ~7× the pixel area of 384 px; **do not extrapolate those figures without re-pricing**. |
| **Feasibility now** | Good. Stage 1 exists (`outputs/retest/phase3a/`, 512 px, 30 runs per cell; subpool builder and `vote_count` already implemented). Stage 2 needs no new crop code (`extract_candidates.py --padding 512` yields 1024×1024). New work: a verification prompt file (drafted at `preregistration-appendix-prompts.md:1129-1160` but never became a file), an `expand_*.json`, and orchestration — estimated ~1–1.5 days, mostly glue **[prior-inventory]**. Two flags: the spec contradicts itself on crop size (1024 px at `preregistration.md:482` vs 896 px at `preregistration-appendix-prompts.md:1144`), and the 37 %-recall premise behind the pilot note (`preregistration.md:484`) is stale given model drift. |
| **Blocks a paper claim?** | **Yes.** Any statement that H2 was tested, and any H2 conclusion phrased over "two-stage architectures" rather than "coarse-to-fine". |

### E-07 · H13 Conditions B and C — 128 px and 256 px overlap

| field | content |
|---|---|
| **Registered at** | `preregistration.md:1024-1028` |
| **Status** | Exploratory, Tier B |
| **What was registered** | "\| B \| 128px \| 384px \| 25% \| ~1.4× \| ~1.4× \|"; "\| C \| 256px \| 256px \| 50% \| ~2× \| ~2× \|" |
| **Executed?** | **Not at all.** `config.py:67` sets `OVERLAP = 64` and there is no variant. Zero occurrences of "H13" in `results/`, `studies/`, `prompts/`, `scripts/`, `protocol-errata.md`, `decisions-log.md`, `session-log.md`, or `working-notes.md` **[prior-inventory, spot-checked]**. |
| **Run instead** | Overlap was held at 12.5 % at every tile size (512→stride 448, 384→336, 256→224). This is **not** arm A: arm A is specified in *pixels* (64 px / 448 px stride, `preregistration.md:1026`), so only the 512 px corpus matches; and a single arm answers none of the three registered comparative analyses **[prior-inventory]**. |
| **Decision on record?** | **No.** Four undated, unattributed status assertions exist giving three different reasons (`execution-plan.md:702` "if budget allows"; `hypothesis-tracking.md:32` "Not started (low priority)", date column empty; `hypothesis-tracking.md:291`; `docs/methods-outline.md:344` "would require re-tiling") **[prior-inventory]**. |
| **Cost to run now** | **~$6** — but the *only* surviving costing is pre-lodgement: the drafting document `archive/preregistration/document-revisions/cc-prereg-simplifications.md` (Change 8) gives "3 conditions × K=10 × variable tiles ≈ 3,800 calls average (~$6)" and a trigger note "~$8 additional" **[prior-inventory]**. The registered text carries no costing. Treat $6–8 as indicative of scale only. |
| **Feasibility now** | High. The repository already holds three independently generated tile trees (`inputs/tiles/`, `inputs/tiles_256/`, `inputs/tiles_384/`), so re-tiling is routine. Spatial deduplication for overlapping detections already exists (region-level pooling, `preregistration.md:1869`). |
| **Blocks a paper claim?** | Only a claim that overlap/stride was characterised. Currently H13 is silently absent — **that silence is the disclosure risk**, and H13 cannot shelter under H14/H15's "registered as deferred" framing because it was registered in scope. |

### E-08 · H14 — cross-model consistency (Claude, GPT)

| field | content |
|---|---|
| **Registered at** | `preregistration.md:1056-1070`; roster at `:1201` |
| **Status** | Exploratory, **Tier C — deferred at registration** (`preregistration.md:1058`) |
| **What was registered** | "**Scope**: This hypothesis is deferred to future work due to: 1. Budget constraints for cross-provider API costs 2. Need to first establish robust findings on single provider 3. Complexity of managing multiple API integrations"; brief protocol at `:1070`. |
| **Executed?** | **Not at all.** All 1,132 pass rows in `results/passes-manifest.json` are Gemini: `model_used` = `gemini-3-flash` (784), `gemini-3-flash-preview` (305), `gemini-3.1-pro-preview` (30), `gemini-3.5-flash` (12), blank (1). `requirements.txt` contains no `anthropic` or `openai` client. |
| **Run instead** | Within-Gemini model comparisons only: `n1-baseline-matrix-384` (Flash vs Pro; `hypothesis_refs: ["H1","H6","H7"]`) and `flash35-model-roles` (Flash 3.5 role permutations; `hypothesis_refs: ["H2"]`). Neither is H14. |
| **Decision on record?** | **Yes — in the registration itself**, at `preregistration.md:1064-1068`. This is the honest case. Two qualifications: the deferral was introduced *during* the v4.0 restructure (pre-v4.0 the same hypothesis read "Exploratory but important for generalisability claims" with a four-phase protocol), and `execution-plan.md:683-686` still promotes H14 to first priority at "~$40-60" **[prior-inventory]**. |
| **Cost to run now** | **~$40-60**, `execution-plan.md:683-686` — a figure that contradicts the registered deferral and predates current provider pricing. Cross-provider pricing has not been checked. |
| **Feasibility now** | Moderate. Would need Anthropic and OpenAI clients (deferred per `docs/planning/future-work.md:41-47`), plus schema-conformant response handling. The registered model IDs (`preregistration.md:1226-1243`) are 2025-vintage and would need re-selection. |
| **Blocks a paper claim?** | **Yes** — any generalisation claim beyond Gemini. The paper must scope generalisation claims to Gemini and cite H6 / `flash35-model-roles`, never H14. |

### E-09 · H15 — cross-model consensus voting

| field | content |
|---|---|
| **Registered at** | `preregistration.md:1074-1088` |
| **Status** | Exploratory, **Tier C — deferred at registration** (`preregistration.md:1076`) |
| **What was registered** | "**Brief protocol**: Compare N=6 pass voting: 6× single model vs 2× each of three models." Deferral grounds at `:1082-1086`, first of which is "Dependency on H14 results". |
| **Executed?** | **Not at all.** No scored condition aggregates votes across models — verified over the 265 distinct `(run_id, proposer_pool)` pairs in `results/passes-manifest.json`. |
| **Run instead** | Cross-model *verification* (a Pro verifier over a Flash proposer pool) exists in `pv-diag-384` and is reported under `unswept-pools-completeness` (`hypothesis_refs: ["H2","H11"]`). That is a cascade, not a vote. |
| **Decision on record?** | **Yes — in the registration**, `preregistration.md:1082-1086`. The registered precondition (H14) was never satisfied, so H15 was gated, not skipped. `execution-plan.md:688-690` contradicts the registration with "~$15-25". |
| **Cost to run now** | Full registered form: **~$15-25** per `execution-plan.md:688-690` (contradicts the registered deferral; excludes the cross-provider client work in E-08). **A within-Gemini analogue costs $0** — see below. |
| **Feasibility now** | The registered cross-*provider* form is gated on E-08. **However**: `pv-diag-384::pro-high-text-n5-text-t0.7` holds a 10-pass pool where runs 1–5 record `gemini-3-flash` and runs 6–10 record `gemini-3.1-pro-preview`, all at T=0.7, HIGH thinking, 487 tiles (verified directly in `results/passes-manifest.json`). That is 5 Flash + 5 Pro at matched settings — raw material for a *within-provider* cross-model voting comparison at zero API cost. **Caveat**: for these batch-API passes `model_version` is `null` and `tokens`/`cost_usd` are zero, i.e. the fields E57 designates authoritative (`protocol-errata.md:1782`ff) are absent, so the model attribution rests on `config.model` — the field E57 says never to trust. Provenance must be settled before any such analysis is published. |
| **Blocks a paper claim?** | Yes — any claim about cross-architecture ensemble diversity. |

### E-10 · Triggered exploratory — M/E sensitivity at H8-optimal library (3 cells)

| field | content |
|---|---|
| **Registered at** | `preregistration.md:1179` (summary row) and `:1181-1191` (specification) |
| **Status** | Triggered exploratory |
| **What was registered** | "**Trigger**: H8 optimal library differs from Scale-8 by ≥2 levels (e.g., Scale-4 or Scale-16+)"; "**Conditions tested (3 cells)**: 1. H1-optimal M/E at H8-optimal library 2. One adjacent M/E alternative at H8-optimal library 3. Image-only at H8-optimal library (if not already covered by condition 1 or 2)" |
| **Executed?** | **Not at all.** |
| **Run instead** | Nothing. |
| **Decision on record?** | **No — and no trace whatsoever.** Outside `preregistration.md` (`:1179`, `:1181`, `:1189-1191`, `:1727`, `:2396`) and one archived pre-lodgement instruction file (`archive/implemented-instructions/cc_execution_checklist_corrections.md:77`), this triggered exploratory appears nowhere in the repository. It was **dropped from the execution plan's own triggered-exploratory table**, which lists only H4b and HN-only (`execution-plan.md:730-734`). It is not in `hypothesis-tracking.md`, `protocol-errata.md`, or `decisions-log.md`. |
| **Cost to run now** | 3 cells. The closest anchored comparator is H8 v2's own meta-reported spend — "~$107 + ~$17" for 7 cells plus one re-run cell at 384 px, HIGH thinking, K=5, 327 tiles (`results/h8-v2/analysis_summary.md:275`) — i.e. **~$15-17 per cell, so ~$45-51 for three**. That document flags its own cost estimate as "untrustworthy in both directions" (`:310-318`, `estimate_cost()` ignores flex-tier and cache discounts but also omits thinking-token billing). **Treat as order-of-magnitude only.** |
| **Feasibility now** | High. All five M/E instruction files and all seven H8 library configs exist; this is three additional cells on an existing pipeline. |
| **Blocks a paper claim?** | Any claim that the M/E ranking is robust to library composition — and, more sharply, any claim that all registered triggers were honoured. |
| **Trigger analysis** | **The trigger fired, under both H8 executions.** H8 v2's optimum at the primary operating point (greedy consensus t=4) is **scale-4, F1 0.733** vs scale-8's 0.710 (`results/h8-v2/analysis_summary.md:66-67`) — and Scale-4 is the *first* example the registered trigger names. H8 v1 (`retest-phase2c`, 512 px) had image-track optimum `plus-hp` at F1 0.5985, also a different library size (13 vs 17 examples) — verified from `results/conditions-manifest.json`. See § 4 for the counter-argument. |

### E-11 · Triggered exploratory — HN-only condition (1 cell)

| field | content |
|---|---|
| **Registered at** | `preregistration.md:1121-1142`; summary row `:1178` |
| **Status** | Triggered exploratory |
| **What was registered** | "**Trigger**: Example-level regression (Section 8.4.5) shows \|β_hardneg\| > 2×\|β_hardpos\| AND both coefficients significant (p < 0.05)"; test: a 13-example Canon+/Canon−/HN library with HP=0. |
| **Executed?** | **Not at all**, and the trigger was never **evaluable** — the § 8.4.5 regression it depends on was never run (see A-03/A-04). |
| **Decision on record?** | No. |
| **Cost to run now** | **~$2** for 1 cell / 600 calls, `execution-plan.md:733` — a January-2026 estimate at 512 px Flash. |
| **Feasibility now** | High as a standalone cell. Note H8 v2's C3 contrast (+HP → Scale-8, i.e. adding HN) was null (BH-adj p 0.932, `results/h8-v2/analysis_summary.md:25`), which weakens the scientific motivation even though it does not discharge the registered condition. |
| **Blocks a paper claim?** | Only a completeness claim. |

### E-12 · H5 — the two unrun image-based M/E arms (4 net new cells)

| field | content |
|---|---|
| **Registered at** | `preregistration.md:620-628` (execution parameters), `:1331-1340` (the 3×3 table), `:1806` |
| **Status** | Confirmatory (Tier 1, `preregistration.md:2157`) |
| **What was registered** | "**M/E level**: All image-based conditions (Image-only, Brief-text+image, Verbose-text+image)"; "**H5 totals**: 9 cells (3 M/E × 3 H5), but 3 overlap with H1 → 6 net new cells" |
| **Executed?** | **Partially.** Only the `brief-text-image` M/E level received H5 variants, plus a text-only Track 2 that the registration explicitly excludes from H5 (`preregistration.md:624`). Conditions on disk: `retest-phase2d::{image,text}-{terse,verbose}` (4), with H5=Minimal reused from `retest-phase2c::image-plus-hp` and `retest-phase2b::text-t0.0`. **Image-only × {terse, verbose} and Verbose-text+image × {terse, verbose} were never run.** |
| **Run instead** | A single-factor OFAT at the carried-forward optimal M/E per track, plus a text-only track — E28 (`protocol-errata.md:643-667`), Decision 17. |
| **Decision on record?** | **Yes**, E28 (`protocol-errata.md:643`, Type: Deviation), which concedes the change "reduces statistical power for detecting M/E × H5 interactions" (`:665`). The concession understates it: the interaction is not merely underpowered but **not estimable** (see A-02). |
| **Cost to run now** | 4 cells. No study-YAML costing survives for H5 at production settings. The **registration's own** costing is **~$11/cell** — "~$286 for confirmatory tests (26 cells × ~$11/cell)" (`preregistration.md:1841`), corroborated by the H5 budget row "\| H5 (Negative Text) \| 6 \| 18,000 \| ~$66 \|" (`execution-plan.md:716`). Both are January-2026 figures at 512 px Flash K=10. At 384 px production settings the H8 v2 comparator is ~$15-17/cell (`results/h8-v2/analysis_summary.md:275`, self-flagged untrustworthy). |
| **Feasibility now** | High for the mechanics — the six H5 instruction files exist (`preregistration.md:1344-1348`). But E28 also **trimmed the terse/verbose instruction text** to remove HN-image references after HN images were dropped, so re-running the full 3×3 now would not use the registered instruction text unless it is restored first. |
| **Blocks a paper claim?** | **Yes** — the registered H5 advance criterion (`preregistration.md:1156`) requires "M/E × H5 interaction non-significant", which cannot be evaluated. |

### E-13 · H9 Condition C — hard-positive diversity channel

| field | content |
|---|---|
| **Registered at** | `preregistration.md:873-878` and `:1574-1577` |
| **Status** | Exploratory, Tier A |
| **What was registered** | "**Variable elements (subject to H9 diversity sampling)**: Hard positives — mounds the model struggles with (from FN analysis); Hard negatives — subject to sampling for diversity across passes" |
| **Executed?** | **Partially.** HN rotate; **HP were frozen** — 4 slots, 4 examples, every HP in every pass. E12 (`protocol-errata.md:258-271`): "H9-C tests HN rotation only; HP diversity is untestable." |
| **Run instead** | `retest-phase3c::image-h9-c-diversity-3of5`, HN-rotation only. Condition C has **no text-track counterpart** (`retest-phase3c` text conditions are a, b, d, e only) — structurally inapplicable, but not covered by any erratum **[prior-inventory]**. |
| **Decision on record?** | **Yes**, E12 (Type: Clarification), rooting the cause in E11 HP-pool exhaustion and deferring HP diversity "to post-H10". H10 subsequently mined 108 HP (`protocol-errata.md:1386`ff, E51 table) — **the stated precondition for un-deferring was satisfied and the deferral was never revisited.** |
| **Cost to run now** | 1 cell (image track). Audited comparator: a 5-replication × 5-pass H9 cell is 25 passes; at 487 tiles / 384 px a 6-pass minimal config costs $2.43 (`results/analyses-manifest.md:24`, rebuilt 2026-06-12 from per-item token metadata) — so **order ~$10, UNVERIFIED at HIGH thinking and 340-tile scope**. |
| **Feasibility now** | High — `inputs/examples/h10-v2/pool_160_hp16hn16/` supplies 16 HP for genuine rotation. |
| **Blocks a paper claim?** | Any claim that image diversity as a mechanism was tested; currently only half of it was. |

### E-14 · H3 — the registered 512 px image-track K=30 study

| field | content |
|---|---|
| **Registered at** | `preregistration.md:512-516`, `:329`, `:1907` |
| **Status** | Confirmatory (Tier 1, `preregistration.md:2155`) |
| **What was registered** | "**Extended voting (N=30)**: Additional 20 runs at optimal configuration to enable: N=30 threshold sweep (1, 2, ..., 30); Cost-benefit characterisation of deeper voting" |
| **Executed?** | **Partially / substituted.** N=30 pools do exist and are extensive (18 conditions at `n_passes: 30` in `results/conditions-manifest.json`, across `retest-phase3a`, `retest-phase3a-high`, `retest-phase3a-replication`, `consensus-384-t1-0`, `pv-diag-384`). But the *image-track* 512 px K=30 study "was never launched" and was replaced by a 2×4 thinking × temperature matrix at 384 px / 487 tiles — E53 (`protocol-errata.md:1581`, Type: Deviation) **[prior-inventory]**. |
| **Run instead** | E53's 384 px matrix. Consequence: the H3 image-track and text-track consensus results are on different tile sizes and tile sets; cross-track H3 comparisons at matched scope are not available. |
| **Decision on record?** | **Yes**, E53, which argues the replacement is "more informative". |
| **Cost to run now** | **UNVERIFIED** — no surviving costing for the 512 px image-track K=30 cell. Comparator: `execution-plan.md:719` costs the whole "Phase 3a: H3 N=30 Extension" at ~$44 for ~12,000 calls (512 px Flash, January 2026). |
| **Feasibility now** | Possible but of low value — it would produce an off-pipeline number that cannot be pooled with anything current. |
| **Blocks a paper claim?** | Only a matched-scope cross-track H3 comparison, which the paper should not attempt. |

### E-15 · K=10 replication across the confirmatory factorial

| field | content |
|---|---|
| **Registered at** | `preregistration.md:315` (§ 3.8), restated `:628`, `:2088` |
| **Status** | Confirmatory protocol element, applies to H1, H4, H5, H7, H8 |
| **What was registered** | "**Independent runs**: Each condition in the main factorial is evaluated using K=10 independent single-pass runs. Results are characterised statistically (mean F1, SD, 95% CI)." |
| **Executed?** | **Partially.** E36 (`protocol-errata.md:878-890`, Type: Deviation) replaced the 60-tile holdout with a 340-tile retest and cut K to 1–3 for single-pass conditions. Verified: Phase 2a/2b run K=3, Phase 2c/2d/2e run K=1 (`results/retest/retest-production-summary.md:281`, caveat 5). |
| **Run instead** | 340-tile K=1–3. Power went up; per-condition replicate variance went away. |
| **Decision on record?** | **Yes**, E36. |
| **Cost to run now** | Restoring K=10 at 340 tiles would be ~3–10× the original Phase 2 spend (~$286 for 26 cells — `preregistration.md:1841`, corroborated at `execution-plan.md:718` — at the *registered* 60-tile scale). **UNVERIFIED at 340-tile scale.** |
| **Feasibility now** | Technically trivial, scientifically retrograde at the 60-tile scope. |
| **Blocks a paper claim?** | **Yes, a wording claim**: any sentence inheriting "K=10 independent runs" from `preregistration.md:315` is false for most cells and must be rewritten. |

### E-16 · H10 — PV leg run on 2 of 4 calibration pools

| field | content |
|---|---|
| **Registered at** | `preregistration.md:912-919` (four conditions A–D) |
| **Status** | Exploratory, Tier B |
| **What was registered** | Four nested training pools (20, 40, 80, 160) evaluated on the same holdout. |
| **Executed?** | **Consensus leg complete (all four pools: `h10::greedy-pool-{020,040,080,160}`); PV leg on pool_020 and pool_160 only.** The study's own caveat (`results/h10/analysis_summary.md:228-233`) states the 040/080 assumption "has not been directly tested and is a minor limitation" **[prior-inventory]**. |
| **Decision on record?** | Yes, in the analysis summary's caveat — but the PV leg is itself non-preregistered (E37), so the shortfall is in a post-hoc extension, not in the registered design. |
| **Cost to run now** | 2 additional PV sweeps. Comparator: H12 v2's actual **~$34.00 for 3,270 calls** at 384 px / HIGH / K=5 / 327 tiles (`results/h12-v2/analysis_summary.md:161,166`). |
| **Feasibility now** | High. |
| **Blocks a paper claim?** | No — the registered "F1 vs pool size curve" is complete. |

### E-17 · H10 — registered sequencing constraint

| field | content |
|---|---|
| **Registered at** | `preregistration.md:940` |
| **Status** | Exploratory, Tier B |
| **What was registered** | "**Sequencing**: Conducted after Stage 2 completion but before generalisation to out-of-sample maps. Training pool expansion draws from the reserve set, which is permissible after Stage 2 evaluation is complete." |
| **Executed?** | The experiment ran (2026-04-15); the **sequencing constraint was not honoured** — Stage 2 (`preregistration.md:2181-2214`) never happened, and H10 drew 160 calibration tiles from the reserve set regardless. |
| **Decision on record?** | **No.** E49 and E50 (`protocol-errata.md:1313`, `:1343`) document H10's configuration and scope changes but not the sequencing violation. |
| **Cost to run now** | n/a — this is a disclosure item, not a re-run item. |
| **Feasibility now** | n/a. |
| **Blocks a paper claim?** | The reserve-set integrity claim at `preregistration.md:76` ("Reserve set \| 281 \| Confirmatory testing \| **Untouched**"). The reserve set is no longer untouched. This should be disclosed. |

---

## 2. Registered analyses never performed (or performed differently)

### A-01 · Family-level BH-FDR across the eight confirmatory hypotheses ★

| field | content |
|---|---|
| **Registered at** | `preregistration.md:270`; rationale `:272-278`; reporting rule `:295` |
| **Status** | Confirmatory — the study's registered inference correction |
| **What was registered** | "**Multiple comparison correction**: Benjamini-Hochberg FDR at q = 0.05 across confirmatory hypotheses"; and "Report both uncorrected and FDR-corrected p-values" (`:295`) |
| **Executed?** | **Not at all as a single family.** `results/retest/pairwise-bootstrap-comparisons.json` carries `metadata.note`: "Raw p-values — FDR correction deferred until all data available", over `n_comparisons: 70`. `results/retest/retest-production-summary.md:209`: "FDR correction is **deferred** until all experimental data are available." Caveat 2 at `:278`: "FDR-corrected contrasts are **not yet in this doc**". |
| **Run instead** | BH-FDR applied **within stratum** on individual leaderboards — "each (Era x Architecture x Buffer x Metric) family is corrected independently. Cross-stratum claims … have **inflated family-wise error rate**" (`results/leaderboard/per-architecture/README.md:63`). Per-phase FDR also exists, e.g. `results/cross-hypothesis-library/permutation-t4/fdr_summary.json`. |
| **Decision on record?** | **Only a deferral, never resolved.** No erratum records that the registered family-level correction was not applied. Separately, the census flags that **the preregistration never specifies a permutation test at all** (zero hits for "permut" in `preregistration.md`), yet the study's headline inference engine is round-robin tile-swap micro-F1 permutation with BH-FDR **[prior-inventory]**. |
| **Cost to run now** | **$0 API.** Pure recomputation over existing p-values. |
| **Feasibility now** | High, but requires a decision the PI must make: define the family. The eight confirmatory hypotheses now have heterogeneous inference (bootstrap CI pseudo-p in Era 1; tile-swap permutation in the leaderboards), different scopes (60/327/340/487 tiles), and H6 has no result at all. A defensible construction is one p-value per confirmatory hypothesis at its headline contrast, BH-corrected across the seven that produced one, with H6 declared unexecuted. |
| **Blocks a paper claim?** | **Yes — the largest one in this register.** Every "FDR-corrected" claim traceable to `preregistration.md:270` is currently unsupported at the registered level. The paper cannot say its confirmatory family was FDR-controlled. |

### A-02 · M/E × H5 bootstrap difference-of-differences interaction test ★

| field | content |
|---|---|
| **Registered at** | `preregistration.md:638-645`; test type in the summary table `:1156`; prediction 4 at `:618` |
| **Status** | Confirmatory (named as an advance criterion) |
| **What was registered** | "**Bootstrap interaction test**: For each M/E level, compute the H5 simple effect (e.g., Terse − Minimal on precision and F1). Test whether H5 effects differ across M/E levels via paired difference-of-differences bootstrap (95% CI). Interaction present if any pairwise CI excludes zero." |
| **Executed?** | **Not at all**, and **not estimable** from what was run — only one image-based M/E level received H5 variants (see E-12). |
| **Decision on record?** | Partially: E28 (`protocol-errata.md:665`) concedes reduced power, but does not state that the registered test became inestimable or that registered prediction 4 therefore cannot be resolved. |
| **Cost to run now** | $0 given E-12's 4 cells; otherwise not computable. |
| **Feasibility now** | Contingent on E-12. |
| **Blocks a paper claim?** | **Yes.** `preregistration.md:1156` makes "M/E × H5 interaction non-significant" an explicit advance criterion. Prediction 4 must be reported as unresolved. |

### A-03 · Example-level effectiveness regression (primary), § 8.4.5

| field | content |
|---|---|
| **Registered at** | `preregistration.md:1611-1630` |
| **Status** | Registered post-hoc analysis, downstream of H9 |
| **What was registered** | "After completing H9 experiments, fit a linear model predicting pass-level F1 from example presence: `F1_pass ~ β₀ + Σᵢ βᵢ(exampleᵢ_present) + ε`"; reporting: "Coefficient estimates (βᵢ) with 95% bootstrapped confidence intervals; Flag examples where \|βᵢ\| > 0.02 F1 as 'high-impact'; Rank examples by absolute effect size within each category" |
| **Executed?** | **Not at all.** No regression script exists in `scripts/`; no `statsmodels`/OLS example-level model anywhere; § 8.4.5 appears only in the preregistration, the execution plan, the prompts appendix, and one planning document. |
| **Decision on record?** | No. |
| **Cost to run now** | **$0 API** — but see feasibility. |
| **Feasibility now** | **Conditional.** Requires the per-pass example assignments. No assignment artefact was found under `outputs/retest/phase3c/` (only `study_manifest.json` and `checkpoint.json` at the track level). If assignments are reconstructible from the study manifests and pass configs, this is a day's analysis; if not, it is unrecoverable. **Determine recoverability first.** Note E11/E12 also mean HP presence is constant, so HP coefficients are unidentifiable by construction — only HN coefficients could be estimated. |
| **Blocks a paper claim?** | Any § 8.4.5 claim, and it gates E-11's trigger. |

### A-04 · Example-level category regression (secondary), § 8.4.5

| field | content |
|---|---|
| **Registered at** | `preregistration.md:1631-1640` |
| **Status** | Registered post-hoc analysis |
| **What was registered** | "`F1_pass ~ β₀ + β_canon(n_canonical) + β_hardpos(n_hard_positive) + β_hardneg(n_hard_negative) + β_null(n_null) + ε` — This estimates the marginal value of adding one more example of each type." |
| **Executed?** | **Not at all.** |
| **Decision on record?** | No. |
| **Cost to run now** | $0 API; same recoverability condition as A-03. |
| **Feasibility now** | Same as A-03; and `β_hardpos` is unidentifiable in H9 data (HP frozen). **However** it *is* identifiable from H8 v2, which varies `n_hard_positive` and `n_hard_negative` across seven library conditions on a common test set — a legitimate substitute worth flagging. |
| **Blocks a paper claim?** | Directly gates E-11's registered trigger (`β_hardneg > 2×β_hardpos`), which is therefore currently unevaluable. |

### A-05 · BIBD variance decomposition (tertiary), § 8.4.5

| field | content |
|---|---|
| **Registered at** | `preregistration.md:1642-1655` |
| **Status** | Registered **conditionally**: "**Tertiary analysis (BIBD, if feasible)**: If library size k ≤ 10 and N ≥ 20…" |
| **Executed?** | Not at all — zero occurrences of "BIBD" outside `preregistration.md`. |
| **Decision on record?** | No, but **the registered precondition was not met**: the H9 baseline library is Scale-8 with 17 examples (`preregistration.md:609`), so k = 17 > 10. |
| **Cost to run now** | n/a. |
| **Feasibility now** | Not applicable under the registered condition. |
| **Blocks a paper claim?** | No. Include one sentence noting the condition was not met. |

### A-06 · H6 Phase 2 decision rule (≥0.03 F1 per factor)

| field | content |
|---|---|
| **Registered at** | `preregistration.md:677` |
| **What was registered** | "**Decision rule**: If alternative outperforms Flash-optimal by ≥0.03 F1, flag factor for adjustment." |
| **Executed?** | **Never computed.** `scripts/lib_phase4_transfer.py` implements the logic (with tests) but was never fed data **[prior-inventory]**. |
| **Decision on record?** | No. |
| **Cost to run now** | **$0 API** if computed over the Pro data that exists (`n1-pro-rerun-384`, `pv-diag-384`) — but that data varies only modality, thinking, and temperature, so the rule can be applied to at most one registered factor. |
| **Feasibility now** | Partial now, full only after E-01 to E-04. |
| **Blocks a paper claim?** | Yes — any per-factor transfer verdict. |

### A-07 · H6 Phase 3 voting-threshold comparison

| field | content |
|---|---|
| **Registered at** | `preregistration.md:679-683` |
| **What was registered** | "Compute voting curves from Phase 1-2 runs (no additional API calls): Compare Pro optimal threshold to Flash optimal threshold; Note any differences >10% relative" |
| **Executed?** | **Never computed**, despite the inputs partly existing: `n1-outstanding-384::pro-{text,image}-high-t0-consensus-{1,2,3}of3` and `pv-diag-384::verified-adv-pro-*` **[prior-inventory]**. |
| **Decision on record?** | No. |
| **Cost to run now** | **$0 API** — the registration itself says "no additional API calls". |
| **Feasibility now** | High. Flash optimal thresholds are already tabulated (`phase3a-consensus-calibration`, `diversity-dividend-384`); the Pro consensus pools exist at N=3. Scope caveat: 384 px / 487 tiles, not the registered scope. |
| **Blocks a paper claim?** | Yes — any statement about whether the optimal vote threshold transfers between models. |

### A-08 · H6 three-way transfer verdict

| field | content |
|---|---|
| **Registered at** | `preregistration.md:693-699` |
| **What was registered** | "\| All factors within 0.03 of Flash-optimal \| Full transfer; report unified recommendation \|"; "\| 1-2 factors need adjustment \| Partial transfer… \|"; "\| ≥3 factors need adjustment \| Poor transfer… \|" |
| **Executed?** | **Never computed.** |
| **Decision on record?** | No. |
| **Cost to run now** | $0, contingent on A-06. |
| **Feasibility now** | Cannot be honestly computed with only 1 of 4 registered factors varied. |
| **Blocks a paper claim?** | **Yes** — the registered advance criterion at `preregistration.md:701` ("Advance to Stage 2 if: Transfer confirmed") cannot be evaluated. |

### A-09 · H6 scope-limitation gate

| field | content |
|---|---|
| **Registered at** | `preregistration.md:691` |
| **What was registered** | "**Scope limitation**: Full per-model optimisation only if Pro demonstrates substantially superior cost-effectiveness (≥20% higher F1 at comparable cost, OR comparable F1 at ≤50% cost)." |
| **Executed?** | **Never evaluated as such** — no artefact applies this gate. |
| **Decision on record?** | No. |
| **Cost to run now** | **$0** — the ingredients exist (`pass-budget-pareto-v2` gives audited per-configuration costs, `results/analyses-manifest.md:24`; `n1-baseline-matrix-384` gives Pro and Flash F1). |
| **Feasibility now** | High and cheap; would let the paper state whether the registered gate opened or closed. |
| **Blocks a paper claim?** | A Pro cost-effectiveness recommendation. |

### A-10 · H1 planned contrasts with FDR correction

| field | content |
|---|---|
| **Registered at** | `preregistration.md:436-443` |
| **What was registered** | "Primary: Pairwise bootstrap comparisons across 5 M/E levels (95% CIs, **FDR-corrected**)"; four named planned contrasts; "Two-tailed tests for modality comparisons; One-tailed for elaboration: H0: verbose ≤ brief" |
| **Executed?** | **Partially.** The pairwise bootstrap ran (`results/retest/phase2a-evaluation.json`, 10 contrasts) **[prior-inventory]**; the **FDR component was not applied** (see A-01), and the registered one-tailed convention for the elaboration contrast is not evidenced in the artefacts, which report two-sided CIs **[prior-inventory, UNVERIFIED — would need to read `scripts/evaluate_retest_all.py`]**. |
| **Decision on record?** | No. |
| **Cost to run now** | $0. |
| **Feasibility now** | High — folds into A-01. |
| **Blocks a paper claim?** | Yes — any "FDR-corrected" H1 statement, and the tail convention must be stated honestly. |

### A-11 · H4 primary analysis with FDR correction

| field | content |
|---|---|
| **Registered at** | `preregistration.md:570`; advance rule `:574` |
| **What was registered** | "**Primary**: Pairwise bootstrap comparisons across 3 ordering conditions (95% CIs, **FDR-corrected**)"; "**Advance to Stage 2 if**: Significant ordering effect detected (FDR-corrected p < 0.05)." |
| **Executed?** | **Partially** — bootstrap yes (4 conditions after E30), FDR no. The registered primary contrast is null in any case: canonical-first vs canonical-last ΔF1 = −0.0316, raw p = 0.124 **[prior-inventory]**. |
| **Decision on record?** | No. Note also that `results/retest/retest-production-summary.md:145` and `:300` describe H4 as showing canonical-last "improves performance, consistent with recency bias" — an overstatement of a null registered contrast **[prior-inventory]**, and a finding-calibration issue in its own right. |
| **Cost to run now** | $0. |
| **Feasibility now** | High; check the FDR family is defined over 4 conditions (E30), not 3. |
| **Blocks a paper claim?** | Yes. |

### A-12 · H5 cross-hypothesis comparison (H1-optimal vs H5-optimal text level)

| field | content |
|---|---|
| **Registered at** | `preregistration.md:636`; prediction 3 at `:617` |
| **What was registered** | "**Cross-hypothesis (H1/H5)**: Compare optimal positive text level (H1) vs optimal negative text level (H5) — if they differ, indicates asymmetric elaboration requirements" |
| **Executed?** | **No artefact found [prior-inventory, and I did not find one either].** Marked **UNVERIFIED — would need a targeted search of `results/**` for an H1-optimal-vs-H5-optimal contrast.** |
| **Decision on record?** | No. |
| **Cost to run now** | $0 — both optima are already recorded (`results/phase2a-carry-forward-parameters.md`, `results/phase2d-carry-forward-parameters.md:45`). |
| **Feasibility now** | Trivial. |
| **Blocks a paper claim?** | The asymmetric-elaboration claim; registered prediction 3 is currently unresolved. |

### A-13 · H7 temperature × voting interaction

| field | content |
|---|---|
| **Registered at** | `preregistration.md:729` |
| **What was registered** | "Examine temperature × voting interaction via post-hoc analysis" |
| **Executed?** | **Arguably discharged, but never labelled as this registered analysis.** `phase3a-consensus-calibration` sweeps 2 tracks × 3 temperatures × N ∈ {5,10,30} (`results/analyses-manifest.md:14`), which is the interaction; and the single-pass-vs-consensus temperature crossover is documented at `results/phase2b-carry-forward-parameters.md:98-115`. Neither is registered as the H7 interaction analysis. |
| **Decision on record?** | No. |
| **Cost to run now** | $0 — a labelling and write-up task. |
| **Feasibility now** | Trivial. |
| **Blocks a paper claim?** | No, provided the existing analysis is cited as discharging it. |

### A-14 · H8 diminishing-returns curve

| field | content |
|---|---|
| **Registered at** | `preregistration.md:823` |
| **What was registered** | "**Secondary**: Characterise diminishing returns curve (F1 vs hard example count)" |
| **Executed?** | **Not as a curve.** `results/h8-v2/analysis_summary.md:61-69` tabulates F1 by condition, and the text notes the 0.040 spread and instability of ranking across thresholds, but no F1-vs-hard-example-count characterisation is produced. |
| **Decision on record?** | No. |
| **Cost to run now** | **$0** — the seven data points exist. |
| **Feasibility now** | Trivial. |
| **Blocks a paper claim?** | Registered prediction 6 ("F1 increase from Scale-16 → Scale-32 will show minimal or no improvement", `preregistration.md:806`) is best answered by this curve. |

### A-15 · H8 cost-efficiency analysis (F1 improvement per input token)

| field | content |
|---|---|
| **Registered at** | `preregistration.md:824` |
| **What was registered** | "**Tertiary**: Cost-efficiency analysis (F1 improvement per input token)" |
| **Executed?** | **Not at all.** `results/secondary-effects-token-efficiency/` exists but analyses ΔF1 per 1k **thinking** tokens for HIGH-vs-MINIMAL (Obs 284), not F1 per input token across library sizes. `results/h8-v2/analysis_summary.md` mentions cost only as a total-spend caveat (`:275`, `:310-318`). |
| **Decision on record?** | No. |
| **Cost to run now** | **$0** — cache-hit rates and library sizes are already recorded (`results/h8-v2/analysis_summary.md:273-274`: 87.8 % at 7 examples, 97.6 % at 41). |
| **Feasibility now** | High, and unusually well-suited to this data: input tokens scale directly with library size, so the registered analysis is a genuinely informative practitioner result the study currently leaves on the table. |
| **Blocks a paper claim?** | A library-size cost recommendation. |

### A-16 · H10 library-composition comparison

| field | content |
|---|---|
| **Registered at** | `preregistration.md:932`; documentation requirement `:926` |
| **What was registered** | "Compare library composition across conditions (do larger pools find different hard examples?)"; "Document resulting library composition for each condition" |
| **Executed?** | **Not as a formal comparison.** `results/h10/analysis_summary.md` reports F1 by pool size, the PV leg, permutation, and WBF, but contains no comparison of *which* hard examples each pool selected. The registered question is addressed only qualitatively, via the operating-point shift (`:83-87`) **[prior-inventory]**. |
| **Decision on record?** | No. |
| **Cost to run now** | **$0** — the four pools' example crops are on disk under `inputs/examples/h10-v2/`. |
| **Feasibility now** | Trivial (hash/diff the selected crops across pools). |
| **Blocks a paper claim?** | The mechanism behind the H10 null: whether larger pools find *different* examples or merely *more of the same* is exactly what a null pool-size result needs to explain. |

### A-17 · H11 qualitative crowded-area assessment

| field | content |
|---|---|
| **Registered at** | `preregistration.md:976` |
| **What was registered** | "Qualitative assessment: Does smaller size help with crowded areas?" |
| **Executed?** | **Not discharged as a standalone analysis [prior-inventory]**. Marked **UNVERIFIED — would need a full read of `results/h11-tile-size-results.md` §§ 8-9**, noting that file's §§ 2-7 are formally retracted as citable material. |
| **Decision on record?** | No. |
| **Cost to run now** | $0. |
| **Feasibility now** | High — density strata are recorded per tile (`inputs/tiles/tile_selection_metadata.json`). |
| **Blocks a paper claim?** | Minor. |

### A-18 · H12 ratio × baseline error-profile interaction

| field | content |
|---|---|
| **Registered at** | `preregistration.md:1008` |
| **What was registered** | "Identify whether ratio interacts with baseline error profile (FP-heavy vs FN-heavy tiles)" |
| **Executed?** | **Not discharged [prior-inventory]**. The registered *secondary* analysis (precision vs recall differential) **was** performed (`results/h12-v2/analysis_summary.md:116-120`). Marked **UNVERIFIED — would need a full read of `results/h12-v2/analysis_summary.txt` and the `permutation-t4/` subtree.** |
| **Decision on record?** | No. |
| **Cost to run now** | **$0** — per-tile TP/FP/FN are in the evaluation JSONs. |
| **Feasibility now** | High. |
| **Blocks a paper claim?** | The completeness of the "library axis closed" claim, which currently rests on three nulls whose registered mechanism analyses were not all run. |

### A-19 · H13 edge-detection analysis

| field | content |
|---|---|
| **Registered at** | `preregistration.md:1046` |
| **What was registered** | "Edge-detection analysis: Does overlap specifically help symbols near original tile boundaries?" |
| **Executed?** | **Not at all** — no artefact anywhere answers it **[prior-inventory]**. The two registered companions ("F1 as function of overlap", "Cost-efficiency: F1 improvement per additional API dollar", `:1044-1045`) are equally unexecuted, since all three require at least two arms. |
| **Decision on record?** | No. |
| **Cost to run now** | $0 given E-07's runs; not computable without them. |
| **Feasibility now** | Contingent on E-07. |
| **Blocks a paper claim?** | Any edge-effect claim. |

---

## 3. Registered documentation and reporting commitments not discharged

### A-20 · § 8.4.1 Step 6 — pre-holdout OSF upload of the library documentation

| field | content |
|---|---|
| **Registered at** | `preregistration.md:1500` |
| **What was registered** | "Before any holdout evaluation, upload to OSF: library manifest, brief text, verbose text, mapping table (hard example image ↔ corresponding text guidance)." |
| **Executed?** | **Partially at best.** The brief and verbose instruction text is in `preregistration-appendix-prompts.md`. No **library manifest** file and no **mapping table** artefact exists in the repository (searched `inputs/examples/`, `docs/`). At lodgement the appendix still carried placeholders: "Configuration files with hard negative images currently use placeholder paths for empirically-derived examples" (`preregistration-appendix-prompts.md:96`), consistent with the unticked checklist item at `preregistration.md:2228`. |
| **Decision on record?** | No. |
| **Cost to run now** | $0. |
| **Feasibility now** | High for the manifest and mapping table as *supplementary* artefacts — but the registered commitment was **pre-holdout**, so producing them now discharges the documentation, not the timing. Say so. |
| **Blocks a paper claim?** | A pre-registration-integrity claim about library provenance. |

### A-21 · § 8.4.5 documentation commitment

| field | content |
|---|---|
| **Registered at** | `preregistration.md:1657-1664` |
| **What was registered** | "The following will be published as supplementary data: Exact example assignment matrix (passes × examples); Achieved frequency distribution per example; Regression coefficients and diagnostics; Random seeds used for all sampling" |
| **Executed?** | **Not found.** No assignment-matrix or frequency-distribution artefact under `outputs/retest/phase3c/` or `inputs/`. Regression coefficients cannot exist (A-03/A-04). |
| **Decision on record?** | No. |
| **Cost to run now** | $0 if the assignments are recoverable from the study manifests; otherwise unrecoverable. |
| **Feasibility now** | Same recoverability question as A-03 — **resolve this first, because it determines four rows** (A-03, A-04, A-21, and E-11's trigger). |
| **Blocks a paper claim?** | A supplementary-data completeness claim. |

### A-22 · § 8.2 Practitioner Effort Analysis

| field | content |
|---|---|
| **Registered at** | `preregistration.md:1289-1304` |
| **What was registered** | Three reporting commitments: "**Time-on-task**: Expert time spent on prompt development, pipeline implementation, and result interpretation will be tracked and reported"; "**Expertise characterisation**: Interaction logs (archived Gemini Antigravity, gemini.google.com, Claude Code and claude.ai sessions) will be analysed to characterise the domain knowledge and technical skills required"; "**Development tool costs**… including AI coding assistant subscriptions (e.g., Claude Code Max monthly subscription)" |
| **Executed?** | **Not at all.** No time-tracking artefact exists; no expertise-characterisation analysis exists; no development-tool cost line exists. |
| **Decision on record?** | No. |
| **Cost to run now** | $0 API. The *inputs* for the expertise characterisation do exist — the session-archiving programme (`docs/methodology/transparency/cc-session-archiving-specification.md`) was built for exactly this. |
| **Feasibility now** | **Split.** Expertise characterisation and development-tool costs are recoverable from the session archives and subscription records. **Time-on-task is not** — it was never tracked prospectively, and a retrospective reconstruction would be an estimate, not a measurement. Report it as such or drop the commitment explicitly. |
| **Blocks a paper claim?** | The registered rationale (`preregistration.md:1304`) is that "Reporting only API costs understates the true cost of adopting VLM-based workflows" — a distinctive contribution the paper currently cannot make. |

### A-23 · § 8.6 tile-exclusion documentation requirement

| field | content |
|---|---|
| **Registered at** | `preregistration.md:1970-1975` |
| **What was registered** | "**Documentation requirement**: Any tile excluded after selection must be documented with: Tile filename; Exclusion reason; Number of retry attempts (if applicable); Whether the exclusion affected training or holdout set" |
| **Executed?** | **No register exists.** No file matching `*exclusion*`/`*excluded*` outside `archive/`. `results/passes-manifest.json` records 97 passes with `status: "partial"` against 1,035 `"ok"`, and per-run `retries` fields exist, but nothing aggregates these into the registered per-tile form. |
| **Decision on record?** | No. |
| **Cost to run now** | **$0.** |
| **Feasibility now** | High — the raw material (`status`, `retries`, `n_tiles_processed` per pass) is already in the manifest; this is a reduction, not a new measurement. |
| **Blocks a paper claim?** | A data-completeness claim. Reviewers of preregistered work routinely check exclusion accounting. |

### A-24 · § 8.9 post-experiment thinking-level verification

| field | content |
|---|---|
| **Registered at** | `preregistration.md:2139-2145` |
| **What was registered** | "**Post-experiment verification:** A confirmatory analysis with full Hungarian matching at the optimal configuration will compare: Detection accuracy (F1, precision, recall); Latency per tile; Token usage and API costs. If minimal is truly equivalent at 1/3 the latency, this is a practical finding for practitioners scaling VLM detection pipelines." |
| **Executed?** | **Partially.** The accuracy limb is well covered for minimal vs HIGH (`retest-phase3a-replication`, `min-vs-high-thinking-pv`, `results/analyses-manifest.md:16,23`), and token/cost is covered by `pass-budget-pareto-v2` (`:24`). **Not covered**: the `low` level (never tested at scale), and a per-tile **latency** comparison at the optimal configuration. |
| **Decision on record?** | Partially — E40 (`protocol-errata.md:944`) explains why Pro cannot run minimal, but nothing addresses the missing `low` arm on Flash or the latency limb. |
| **Cost to run now** | Latency: **$0** (`wall_clock_s` and `n_tiles_processed` are in `results/passes-manifest.json`). The `low` arm: 1 cell — comparator ~$2.43 for a 6-pass config at 487 tiles / 384 px (`results/analyses-manifest.md:24`, audited). |
| **Feasibility now** | High for both. |
| **Blocks a paper claim?** | The registered practitioner claim about latency, which the registration itself flags as the point of the exercise. |

### A-25 · § 8.2 pricing documentation

| field | content |
|---|---|
| **Registered at** | `preregistration.md:1282` |
| **What was registered** | "**Pricing documentation**: API pricing will be recorded at experiment start and included in supplementary materials. If pricing changes during the study, both prices will be documented." |
| **Executed?** | **Partially.** Per-pass `cost_usd` and token counts are in `results/passes-manifest.json`, and `results/paper-tables/cost_retrospective.json` exists. But `results/h8-v2/analysis_summary.md:310-318` documents that `estimate_cost()` is wrong in both directions (ignores flex-tier and cache discounts, omits thinking-token billing), and `pass-budget-pareto-v2` records a full cost rebuild on 2026-06-12 after a token-load audit (`results/analyses-manifest.md:24`). No single supplementary pricing table exists, and no change-over-time record. |
| **Decision on record?** | The rebuild is documented in the analysis outcome; the registered supplementary artefact is not. |
| **Cost to run now** | $0. |
| **Feasibility now** | High. |
| **Blocks a paper claim?** | Any headline cost figure not traceable to the 2026-06-12 rebuild. |

---

## 4. Registered triggers — fired / not fired / overridden

### T-01 · H7 temperature escalation, upper limb — **FIRED, NOT HONOURED** ★

| field | content |
|---|---|
| **Registered at** | `preregistration.md:731` |
| **What was registered** | "**Temperature escalation trigger**: If T=1.3 yields higher F1 than T=1.0 (point estimate, same M/E and H5 condition), exploratory testing at T=1.6 and T=2.0 will be conducted at the optimal configuration to characterise the upper bound of the temperature-performance curve." |
| **Did it fire?** | **Yes, on the text track.** T=1.3 F1 = 0.544 vs T=1.0 F1 = 0.533 (`results/phase2b-carry-forward-parameters.md:54-55`). On the image track it did not: T=1.3 = 0.490 < T=1.0 = 0.527 (`:38-39`). The trigger is written per-condition ("same M/E and H5 condition"), so the text-track firing stands. |
| **Honoured?** | **No.** No T=1.6 or T=2.0 pass exists anywhere. The complete temperature set in `results/passes-manifest.json` (1,132 passes) is {0.0, 0.3, 0.4, 0.5, 0.55, 0.7, 0.85, 1.0, 1.3}; the intermediate values are H9 temperature-diversity ladders, not escalation. |
| **Decision on record?** | **None. No erratum covers this** — verified against the 57-entry census. |
| **Cost to run now** | 2 cells at the optimal configuration. Audited comparator: $2.43 for a 6-pass minimal config at 487 tiles / 384 px (`results/analyses-manifest.md:24`); a single-pass cell is a fraction of that. **Order $5-15 for both cells; UNVERIFIED at the specific scope chosen.** |
| **Feasibility now** | Trivial — temperature is a runtime parameter (`preregistration.md:1421`). |
| **Blocks a paper claim?** | **Yes.** The paper's practitioner claim is that users should lower the Gemini temperature default. That claim rests on a monotone-degradation reading of the temperature curve which the registration itself anticipated might not hold above 1.3 — and required checking. |

### T-02 · H7 temperature escalation, lower limb — **FIRED, arguably discharged**

| field | content |
|---|---|
| **Registered at** | `preregistration.md:731` (second sentence) |
| **What was registered** | "If T=0.3 or T=0.7 improves performance (alone or in ensembles), further testing at low temperatures will be conducted at the optimal configuration to characterise the lower bound of the temperature-performance curve." |
| **Did it fire?** | **Yes, on both tracks.** T=0.3 beats T=1.0 significantly on both (image +0.048; text +0.073 — `results/phase2b-carry-forward-parameters.md:36,38,51,55,74`). |
| **Honoured?** | **Arguably yes by construction**: T=0.0 is the floor of the parameter space and was already in the registered grid, and T=0.0/T=0.3 are statistically tied on the text track (p = 0.862, `:60-61`). No intermediate temperatures (0.1, 0.2) were tested. |
| **Decision on record?** | No. |
| **Cost to run now** | 2 cells, same order as T-01. |
| **Feasibility now** | Trivial. |
| **Blocks a paper claim?** | Marginal. Worth one disclosure sentence rather than a run. |

### T-03 · M/E sensitivity at H8-optimal — **FIRED, NOT HONOURED, NO TRACE** ★

See **E-10** for the full row. Trigger text: "H8 optimal library differs from Scale-8 by ≥2 levels
(e.g., Scale-4 or Scale-16+)" (`preregistration.md:1183`). H8 v2 optimum = **scale-4** (F1 0.733 vs
scale-8 0.710, `results/h8-v2/analysis_summary.md:66-67`), and Scale-4 is the registered example.
H8 v1 optimum = `plus-hp` (F1 0.5985, `results/conditions-manifest.json`), also a different size.
Never run; zero trace outside the preregistration; **dropped from `execution-plan.md`'s own
triggered-exploratory table** (`:730-734`).

**This is the item the prior inventories missed.**

### T-04 · HN-only condition — **UNEVALUABLE, NOT HONOURED**

See **E-11**. Trigger: "Example-level regression (Section 8.4.5) shows |β_hardneg| > 2×|β_hardpos|
AND both coefficients significant" (`preregistration.md:1125`). The gating regression was never run
(A-03/A-04), so the trigger could never be evaluated. An unevaluable trigger is a distinct
disclosure category from an unfired one and should not be reported as "not triggered".

### T-05 · H13 trigger — **second clause arguably fired; never formally evaluated**

| field | content |
|---|---|
| **Registered at** | `preregistration.md:1048` |
| **What was registered** | "**Trigger**: Run if significant edge-effect errors observed in Stage 2 holdout evaluation or if disappointing F1 performance warrants testing multiple perspectives on the same location ." (source typo retained) |
| **Did it fire?** | **Clause 1: never evaluated** — no edge-effect assessment exists anywhere (A-19), and Stage 2 never happened. **Clause 2: arguably yes** — single-pass F1 was disappointing by the project's own standard, and the project responded exactly as the clause anticipates, by testing multiple perspectives on the same location — but via consensus voting (H3) and proposer-verifier cascades (H2) rather than via overlap **[prior-inventory]**. |
| **Honoured?** | No overlap contrast was ever run. |
| **Decision on record?** | **No.** The only "not triggered" statement is an assistant turn in a session transcript, never checked and addressing only clause 1 **[prior-inventory]**. |
| **Note on the bright line** | Clause 2 was added post-drafting on 2026-01-09 (commit `ce17da492`) without a changelog note **[prior-inventory]** — but that is **three weeks before lodgement**, so under the governing rule the broadened clause **is** the registered trigger. Its provenance is context, not a defence. |
| **Blocks a paper claim?** | Any claim that H13's trigger was assessed. |

### T-06 · H12 trigger — **DID NOT FIRE; OVERRIDDEN, disclosed**

| field | content |
|---|---|
| **Registered at** | `preregistration.md:1010` |
| **What was registered** | "**Trigger**: Run if H8 shows library size matters" |
| **Did it fire?** | **No.** H8 v2 returned all seven contrasts null after BH-FDR with a 0.040 F1 spread (`results/h8-v2/analysis_summary.md:13-19`, `:21-29`). |
| **Honoured?** | **Overridden — H12 was run anyway.** E52 (`protocol-errata.md:1494-1519`) states plainly: "Strictly read, the trigger is not met", then gives two reasons (orthogonality of balance vs size; publishability of nulls). |
| **Decision on record?** | **Yes**, E52 — a model of how to document a trigger override. It must appear in the paper's deviations passage, not be left in the errata file: a registered trigger that was not met but was overridden is precisely what a preregistration-checking reviewer looks for. |
| **Cost** | Already spent: **~$34.00**, 3,270 calls (`results/h12-v2/analysis_summary.md:161,166`). |
| **Blocks a paper claim?** | No, provided the override is disclosed. |

### Triggers checked that impose no obligation (not counted in the totals)

- **H4b** (`preregistration.md:1100`, "H4 main effect is significant"): **did not fire** — H4 was null
  (A-11). Correctly not run. Should still be *mentioned*: the draft currently does not say H4b was
  registered and did not trigger **[prior-inventory]**.
- **H11** (`preregistration.md:948`, "F1 < 0.85"): **fired and honoured** — every 512 px cell is below
  0.85 and H11 ran. Note the checklist states the trigger backwards
  (`preregistration.md:2225`: "F1 ≥ 0.85 triggers H11 tile size testing"); the H11 section governs.
- **H2 stopping rule** (`preregistration.md:491`, "F1 at least 0.05 higher than single-stage"):
  **fired and honoured** — the proposer-verifier lift far exceeded 0.05 and the architecture was
  pursued. This is the registered prediction being *refuted*, which the paper must state.
- **H8 availability contingency** (`preregistration.md:815`): fired (HP pool exhausted at 4), honoured
  via E11's cap, and later resolved when E51 re-enabled Scale-16/32 on the v2 pool.

---

## 5. Tiering for the PI

### Tier 1 — RUN NOW

Cheap, feasible with what is on disk, and each closes a registered gap. **Zero-API items first;
they carry no spend decision at all.**

| # | Item | Cost | Why now |
|---|---|---|---|
| 1 | **A-01** family-level BH-FDR across the confirmatory family | **$0** | The single highest-value item in the register. It is *the* registered inference correction; until it exists, no confirmatory FDR claim in the paper is supported. Requires a PI decision on family definition, not new data. |
| 2 | **A-07** H6 voting-threshold comparison + **A-06** ≥0.03 decision rule + **A-09** cost-effectiveness gate, computed on the Pro data that exists | **$0** | The registration itself says Phase 3 needs "no additional API calls" (`preregistration.md:680`). Converts three "never computed" disclosures into three computed-with-scope-caveat results. Cannot produce a full **A-08** verdict — say so. |
| 3 | **A-15** H8 F1-per-input-token + **A-14** diminishing-returns curve | **$0** | Both are one afternoon on existing data, and A-15 is a genuinely useful practitioner result (input tokens scale directly with library size) that the study is currently leaving on the table. |
| 4 | **A-16** H10 library-composition comparison | **$0** | Hash/diff of crops already on disk. It is the mechanism explanation the H10 null needs: same examples or different ones? |
| 5 | **A-23** tile-exclusion register | **$0** | A reduction over `results/passes-manifest.json` (97 `partial` passes). Reviewers of preregistered work check exclusion accounting. |
| 6 | **A-24** latency limb of the § 8.9 verification | **$0** | `wall_clock_s` is already in the manifest; the registration flags this as the practitioner payoff. |
| 7 | **A-12** H1-optimal vs H5-optimal text-level comparison | **$0** | Both optima are already recorded; resolves registered prediction 3. |
| 8 | **A-18** H12 ratio × error-profile + **A-17** H11 crowded-area | **$0** | Both from existing per-tile evaluations. Verify my UNVERIFIED marks first — they may already be discharged inside files I did not read in full. |
| 9 | **A-20** library manifest + mapping table; **A-21** H9 assignment matrix | **$0** | Do A-21's **recoverability check first** — it determines A-03, A-04, and T-04 as well. |
| 10 | **T-01** H7 escalation, T=1.6 and T=2.0 | **~$5-15** (2 cells; comparator `results/analyses-manifest.md:24`) | A registered trigger that demonstrably fired and was never honoured, with no erratum. Trivially cheap. Directly supports or qualifies the paper's temperature recommendation. |
| 11 | **E-10 / T-03** M/E sensitivity at H8-optimal (3 cells) | **~$45-51** (comparator `results/h8-v2/analysis_summary.md:275`, self-flagged untrustworthy) | A registered triggered exploratory with *zero* project trail, dropped from the execution plan, whose trigger fired under both H8 executions. Cheapest possible way to close it. |
| 12 | **E-11 / T-04** HN-only (1 cell) | **~$2** (`execution-plan.md:733`, Jan-2026 512 px Flash) | Trivial. Closes an unevaluable trigger by running the cell regardless of the gate. |

**Tier 1 total incremental API spend: roughly $55-70**, on the best anchors available, all of which
are flagged as approximate. Everything else in Tier 1 is $0.

### Tier 2 — RUN IF TIME

| # | Item | Cost | Judgement |
|---|---|---|---|
| 13 | **E-12** H5's four missing image-based M/E × H5 cells (→ makes **A-02** estimable) | ~$44: 4 cells at the registration's own ~$11/cell (`preregistration.md:1841`); ~$60-68 at the H8 v2 384 px production comparator | Highest scientific value in Tier 2 — it converts an inestimable registered advance criterion into an answerable one. Demoted from Tier 1 only because E28 trimmed the registered instruction text, so a faithful re-run needs the text restored first, which is a decision, not a task. |
| 14 | **E-07** H13 conditions B and C | ~$6-8 (**pre-lodgement drafting estimate only**) | Cheap, feasible, three tile trees already exist, and it closes the one hypothesis that was registered fully in scope and dropped with no decision and three contradictory recorded reasons. Only below Tier 1 because it needs a re-tiling pass and dedup validation. |
| 15 | **E-06** H2 Condition C | **UNVERIFIED** — needs a 1024 px pricing run; ~1-1.5 days build | Converts a disclosure into a completed registration, and the stale 37 %-recall premise argues for re-testing rather than against. Below Tier 1 purely on build cost. Gate on a proper cost estimate. |
| 16 | **E-13** H9 Condition C with a genuine HP channel | order ~$10, UNVERIFIED | The stated precondition for un-deferring (a larger HP pool) was satisfied by H10 and never revisited. Cheap, and it completes a half-tested registered mechanism. |
| 17 | **A-24** `low` thinking arm | ~$2.43 comparator | Completes the registered three-level § 8.9 comparison. Low value on its own. |
| 18 | **E-16** H10 PV legs for pools 040 and 080 | comparator ~$34 for 3,270 calls (`results/h12-v2/analysis_summary.md:161,166`) | Closes a self-identified limitation, but in a *non-preregistered* extension — so it strengthens the paper without discharging a registered obligation. |
| 19 | **E-01 to E-05** H6 Phase 4 at the registered spec | **$48 max** (`studies/phase4-transfer.yaml:165`) | See "arguable" below. |
| 20 | **A-22** expertise characterisation + development-tool costs | $0 | Recoverable from the session archives. Time-on-task is not recoverable and should be explicitly withdrawn. |

### Tier 3 — DISCLOSE ONLY

| # | Item | Why |
|---|---|---|
| 21 | **E-08** H14 and **E-09** H15 (registered form) | Registered as **deferred at lodgement**, with reasons stated in the registration itself (`preregistration.md:1064-1068`, `:1082-1086`). This is the honest case and needs no remedy — only a Methods sentence, and a discipline about scoping every generalisation claim to Gemini. Two qualifications to include: the deferral was introduced during the v4.0 restructure rather than being the hypothesis's original status, and `execution-plan.md:683-690` still contradicts it. |
| 22 | **E-09 addendum** — the within-Gemini voting analogue | Not H15. Report the existence of the mixed pool if the provenance thread is settled; do **not** present it as discharging H15. |
| 23 | **A-05** BIBD | Registered *conditionally*; the condition (k ≤ 10) was not met at k = 17. One sentence. |
| 24 | **E-14** H3's 512 px image-track K=30 | Superseded by E53; re-running would yield an off-pipeline number that cannot be pooled with anything current. Disclose the substitution and the loss of matched-scope cross-track comparison. |
| 25 | **E-15** K=10 replication | Superseded by E36; restoring K=10 at the 60-tile scope would be a deliberate power regression. Disclose, and **rewrite every "K=10 independent runs" sentence inherited from `preregistration.md:315`**. |
| 26 | **E-17** H10 sequencing constraint | Cannot be un-done — the reserve set has been drawn on. Disclose, and correct `preregistration.md:76`'s "Untouched" characterisation in the paper. |
| 27 | **T-06** H12 trigger override | Already well documented in E52; move it from the errata file into the paper's deviations passage. |
| 28 | **T-02** H7 lower limb | Arguably discharged by the floor of the parameter space. One sentence. |
| 29 | **A-13** H7 temperature × voting | Substantively discharged by `phase3a-consensus-calibration`; needs labelling, not work. |
| 30 | **A-25** pricing documentation | Partially discharged; assemble the supplementary table from the 2026-06-12 rebuild and note the superseded figures. |
| 31 | **A-22 time-on-task limb** | Never tracked prospectively; a retrospective figure would be an estimate presented as a measurement. Withdraw explicitly rather than reconstruct. |

---

## 6. Calls I think are genuinely arguable

1. **T-03 / E-10 — did the M/E-sensitivity trigger actually fire?** *For*: the registered trigger
   names Scale-4 as a qualifying example, and Scale-4 is H8 v2's optimum at the primary operating
   point. H8 v1's optimum (`plus-hp`) was also a different library size. *Against*: all seven H8 v2
   contrasts are null with a 0.040 F1 spread and fully overlapping CIs, the ranking is unstable
   across vote thresholds (scale-8 leads at t=3, `results/h8-v2/analysis_summary.md:113,121-122`),
   and under the secondary WBF aggregation scale-8 leads (`:134`). One can argue that with no
   statistically distinguishable optimum, "H8 optimal ≠ Scale-8" is undefined. **My call**: the
   trigger is written on point estimates, not significance, and the registration named Scale-4
   explicitly — so it fired, and 3 cells at ~$50 is a cheap way to remove the argument entirely.
   But a PI who reads the trigger as presupposing a *meaningful* optimum has a real position.

2. **E-01 to E-05 — is re-running H6 at the registered spec worth $48?** *For*: it is confirmatory,
   the scaffolding is intact, and the current state is the worst of both worlds — H6 is neither
   reported nor disclosed. *Against*: E40 means Gemini 3.1 Pro **cannot** run `thinking_level=minimal`,
   so a re-run still confounds model capability with thinking budget and still cannot deliver the
   registered "matched configuration" baseline. Spending $48 to produce a result that carries the
   same headline caveat as the existing Pro work is arguably worse than a clean disclosure plus the
   $0 analyses in Tier 1 item 2. **My call**: do Tier 1 item 2 first, then decide. If the $0 analyses
   yield a defensible partial-transfer statement, the re-run may be unnecessary.

3. **E-07 — is H13 "run if time" or "run now"?** It is the cheapest unexecuted registered experiment
   in the study (~$6-8 on the drafters' own estimate) and has the weakest decision trail of any item
   here. That combination argues for Tier 1. I placed it in Tier 2 only because it needs a re-tiling
   pass and deduplication validation, which is real work rather than a config change. A PI who
   weights disclosure exposure over effort should promote it.

4. **E-12 vs A-02 — restore the registered instruction text, or run the 3×3 as it now stands?**
   Running four cells with the current (E28-trimmed) text makes the interaction estimable but tests a
   slightly different H5 factor than registered. Restoring the text makes it faithful but creates a
   third instruction lineage. There is no clean answer; whichever is chosen must be stated.

5. **E-06 — does the stale premise argue for or against running H2-C?** The registered pilot note
   (`preregistration.md:484`) rests on 1024 px achieving only 37 % recall, measured on a much earlier
   model. Model drift plausibly invalidates that premise, which is an argument *for* running C. It is
   also an argument that C's registered rationale no longer describes the experiment one would run —
   i.e. that C should be disclosed as superseded rather than executed. Reasonable people differ.

6. **E-09 — should the mixed Flash/Pro pool be analysed at all?** It is free and interesting, but the
   authoritative provenance fields are absent for those passes and E57 explicitly forbids relying on
   `config.model`. Analysing it before the billing reconciliation risks a second E57. **My call**:
   settle provenance first; the analysis is worth little if it cannot be labelled.

---

## 7. What I could not verify

| # | Item | What would settle it |
|---|---|---|
| 1 | Whether the H9 per-pass example assignments are recoverable (gates A-03, A-04, A-21, T-04) | Read `outputs/retest/phase3c/track{1,2}-*/study_manifest.json` and the per-pass configs for an example-assignment record |
| 2 | Whether A-12 (H1-optimal vs H5-optimal comparison) exists somewhere | Targeted search of `results/**` for an H1-optimal-vs-H5-optimal contrast |
| 3 | Whether A-17 (H11 crowded-area) is discharged inside `results/h11-tile-size-results.md` §§ 8-9 | Full read of those sections (§§ 2-7 are retracted as citable material) |
| 4 | Whether A-18 (H12 error-profile interaction) is discharged inside `results/h12-v2/analysis_summary.txt` or `permutation-t4/` | Full read of both |
| 5 | Whether H1's and H4's registered one-tailed conventions were applied | Read `scripts/evaluate_retest_all.py` for how `significant` and `f1_p_value` are derived |
| 6 | Whether `pv-diag-384::pro-high-text-n5-text-t0.7` runs 1-5 were dispatched as Flash or Pro | The billing records E57 cites; the batch metadata carries neither `pricing_used` nor `per_item_metadata` (verified: `model_version` is `null`, tokens and cost are zero) |
| 7 | Current 1024 px crop pricing for E-06 | A short pricing run; **do not extrapolate the audited 384 px figures** (`results/analyses-manifest.md:24`) — 1024 px is ~7× the pixel area |
| 8 | Whether any of the Jan-2026 costings (`execution-plan.md:707-734`, `studies/phase4-transfer.yaml:160-165`) still hold | Re-price against current Gemini rates; all were computed at 512 px Flash/Pro before flex tier and context caching entered the pipeline |

## 8. One adjacent finding, outside the register's scope

`results/phase2b-carry-forward-parameters.md:69-70`, `results/retest/phase2b/analysis_summary.md:174-175`,
and `results/phase2e-carry-forward-parameters.md:58` all attribute a decision rule to the
preregistration — *"If T=1.0 (default) is within 0.02 F1 of best, prefer T=1.0 for simplicity"* — that
**is not in the preregistration**. `grep "0\.02" preregistration.md` returns only three unrelated hits
(`:1628`, `:2124`, `:2131`). The rule lives in the study YAMLs (`studies/phase2b-h7-temperature.yaml:125`,
`studies/phase2b-h7-temperature-text-only.yaml:136`, `studies/retest/phase2b-h7-temperature.yaml:109`,
and the ordering analogue at `studies/phase2e-h4-ordering.yaml:128`) and in
`docs/methodology/preregistration/tasks/phase2-remaining-tasks.md:38`. It did not change any outcome
here — T=1.0 was far outside 0.02 on both tracks — but the phrase "the preregistered decision rule"
should be corrected wherever it appears, since a reader checking the OSF record will not find it.
