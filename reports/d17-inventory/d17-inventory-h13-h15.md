# D17 — Inventory of H13, H14, H15

**Task**: Per-hypothesis reconciliation for the confirmatory/exploratory manifest pass (decision
D17, `docs/paper/results-outline.md:416-450`).

**Repository**: `/home/shawn/Code/map-reader-llm` (read-only inspection; no edits made).

**Compiled**: 2026-07-27. Every checkable specific below carries a file path and, where practical,
a line number. Quotations are verbatim from the cited line.

**Canonical preregistration document**: `docs/methodology/preregistration/osf/preregistration.md`
(the only preregistration text in the tree; `docs/methodology/preregistration/` itself holds only
derived documents — tracking matrix, execution plan, decisions log, errata, analysis summary).

---

## 0. Executive summary

| Hypothesis | Registered status | Executed? | Proposed manifest classification |
|---|---|---|---|
| H13 — Overlap/Stride Effects | Exploratory, Tier B (`preregistration.md:1016`) | **No** — baseline arm only; no overlap contrast exists | `not-executed` |
| H14 — Cross-Model Consistency | Exploratory, Tier C — deferred (`preregistration.md:1058`) | **No** — no non-Google model was ever called | `not-executed` |
| H15 — Cross-Model Consensus Voting | Exploratory, Tier C — deferred (`preregistration.md:1076`) | **No** — every voting pool in the study is single-model | `not-executed` |

**Note on the vocabulary.** `not-executed` is *not* currently a permitted value of the
`preregistered` field. The schema at `docs/manifest-schemas/analyses-manifest.schema.json:46-50`
enumerates exactly `["preregistered", "exploratory", "preregistered-with-deviation", null]`. None of
H13/H14/H15 has an `analyses-manifest.json` entry at all (verified below), so strictly there is
nothing to reclassify — the disclosure problem is one of **absence**, not mislabelling. If the PI
wants these hypotheses represented in the register (recommended, so the register can generate the
promised hypothesis-outcome table), the schema needs either a fourth enum value (`not-executed`) or
a separate registered-but-unexecuted list. **This is a schema decision, not a data decision, and it
should be made before the manifest pass.**

---

## 1. H13 — Overlap/Stride Effects on Detection Performance

### 1.1 As registered

Source: `docs/methodology/preregistration/osf/preregistration.md`, lines 1014–1048.

Heading (line 1014):

> `### H13: Overlap/Stride Effects on Detection Performance`

Status (line 1016):

> **Status**: Exploratory (Tier B)

Background (line 1018):

> **Background**: Current tiling uses 64px overlap (12.5% of 512px tile, 448px stride). Higher
> overlap increases redundant coverage, potentially catching symbols near tile edges that might be
> missed or poorly detected. However, it also increases API costs proportionally.

Research question (line 1020) — **note this is a Question, not a Prediction**:

> **Question**: Does increasing tile overlap improve detection performance, and is the cost
> justified?

Registered test matrix (lines 1024–1028):

| Condition | Overlap | Stride | Overlap % | Tiles (×) | API Cost (×) |
| --------- | ------- | ------ | --------- | --------- | ------------ |
| A | 64px | 448px | 12.5% | 1× | 1× |
| B | 128px | 384px | 25% | ~1.4× | ~1.4× |
| C | 256px | 256px | 50% | ~2× | ~2× |

Registered analysis (lines 1042–1046):

> **Analysis**:
>
> - F1 as function of overlap
> - Cost-efficiency: F1 improvement per additional API dollar
> - Edge-detection analysis: Does overlap specifically help symbols near original tile boundaries?

Registered trigger (line 1048), quoted verbatim including its source typo (space before full stop):

> **Trigger**: Run if significant edge-effect errors observed in Stage 2 holdout evaluation or if
> disappointing F1 performance warrants testing multiple perspectives on the same location .

Registered implementation notes (lines 1036–1040) specify "Uses optimal configuration from
Stages 1-2", "Spatial deduplication applied to handle redundant detections", and "Ground truth
matching accounts for symbols detected in multiple overlapping tiles".

### 1.2 Registered status and tier

- **Exploratory**, **Tier B**. Anchors: `preregistration.md:1016` (per-hypothesis Status line);
  `preregistration.md:1169` (summary table §7.2 row `| H13 (overlap/stride) | B | Does increased
  overlap improve edge detection? | F1 vs overlap, cost analysis |`);
  `preregistration.md:2006` (implementation table row `| H13 | Overlap/stride | B | 📋 Planned |
  Tile overlap parameter |`); `preregistration.md:2176` (`- **H13** (overlap/stride) — Tier B
  exploratory`).
- H13 sits inside the block headed **"### 7.2 Exploratory Hypotheses (H9-H15)"**
  (`preregistration.md:1161`), distinct from **"### 7.1 Confirmatory Hypotheses (H1-H8)"**
  (`preregistration.md:1148`). The confirmatory/exploratory line is therefore drawn by the
  preregistration itself, exactly as the task brief states.
- Execution-plan priority: lowest tier. `execution-plan.md:702` reads
  `5. **H11, H13**: Lower priority, if budget allows`.

### 1.3 Execution

**Not executed. No run, condition, or analysis anywhere in the repository references H13.**

Verification performed (all negative):

| Check | Command / target | Result |
|---|---|---|
| Analyses register | `results/analyses-manifest.json` (18 entries; every `hypothesis_refs` array enumerated) | H13 absent. Refs used: H1, H2, H3, H4, H5, H6, H7, H8, H9, H11 — and two entries with `[]` |
| Any results file | `grep -rl "H13\|H14\|H15" results/` | **NONE** |
| Any study YAML | `grep -rl "H13\|H14\|H15" studies/` | **NONE** |
| Any prompt config | `grep -rl "H13\|H14\|H15" prompts/` | **NONE** |
| Any script | `grep -rl "H13\|H14\|H15" scripts/` | **NONE** |
| Errata | `grep -c "H13\|H14\|H15" docs/methodology/preregistration/protocol-errata.md` | **0** |

**Incidental evidence check — did anything vary overlap?** No. Overlap **ratio was held constant at
12.5% across every tile size the study ran**, so overlap was never manipulated:

| Tile size | Overlap (px) | Stride (px) | Overlap % | Anchor |
|---|---|---|---|---|
| 512 | 64 | 448 | 12.5% | `config.py:66-68` (`TILE_SIZE = 512`, `OVERLAP = 64`, `STRIDE = TILE_SIZE - OVERLAP`); `studies/h11-384-single-pass.yaml:57-58` |
| 384 | 48 | 336 | 12.5% | `studies/h11-384-single-pass.yaml:51-52`; `studies/h11-384-consensus.yaml:53-54`; `studies/h11-384-proposer-verifier.yaml:73-74` |
| 256 | 32 | 224 | 12.5% | derived from tile-origin spacing in `inputs/tiles_256/full_evaluation_manifest.json` (x-origins 0, 224, 448, 672, … ⇒ stride 224 ⇒ overlap 32) |

Corroborated in prose at `results/h11-tile-size-results.md:14-15`, which describes the H11
comparison as "(384×384, stride 336, 12.5% overlap) … compared to the standard 512×512 tiles
(stride 448, 12.5% overlap)".

So the tile-size sweep (`analyses-manifest.json` analysis_id `tile-size-sweep`,
`hypothesis_refs: ["H11"]`, lines 518–580) varied **absolute** overlap (32/48/64 px) only as an
arithmetic consequence of tile size, with the **ratio deliberately fixed**. That is the opposite of
H13's design, which holds tile size at 512 px and varies the ratio (12.5% → 25% → 50%). H13
condition **A is the study's standing tiling configuration** and was used throughout — but a
single-arm baseline is not a contrast, and there is no B or C to compare it against.

**Incidental evidence check — was the H13 "edge-detection analysis" ever run?** No. Searches for
tile-edge/edge-effect analyses (`grep -rln "tile.edge\|edge effect\|edge-effect\|near tile boundar"`)
return only: crop-extraction scripts (`scripts/extract_candidates.py`, `scripts/5_verify_crops.py`
— these concern verifier crop truncation, i.e. E33, not detection edge effects), evaluation-scoping
discussions (`protocol-errata.md` E7), and narrative mentions in reflections. `results/h11-tile-size-results.md`
mentions "edge" only twice (lines 74 and 554) and neither is an edge-effect analysis. **There is no
artefact that answers "does overlap specifically help symbols near original tile boundaries?"**

### 1.4 Outcome

**None.** No result exists.

### 1.5 Deviations (errata)

**None.** No erratum in `protocol-errata.md` (E1–E57) mentions H13 (verified: `grep -c` returns 0).
The nearest neighbours are E41 (`protocol-errata.md:960`, 384 px tile size adopted for the Pro
comparison) and E51 (`protocol-errata.md:1366`, H8 v2 at 384 px / stride 336) — both change tile
size and therefore absolute stride, but neither touches the overlap **ratio** and neither cites H13.

### 1.6 Proposed classification

**`not-executed`** (schema extension required — see §0).

Justification: H13 was registered with a full three-condition design and a stated analysis plan; its
trigger ("significant edge-effect errors observed in Stage 2 holdout evaluation") was never
formally evaluated; and no arm beyond the standing baseline was run. Labelling it `exploratory`
would falsely imply an executed exploratory analysis. Labelling it `preregistered` would be worse.

### 1.7 Source discrepancies

1. **Registered as a Question, not a Prediction.** H13 (line 1020) and H15 (line 1080) state
   *Questions*; H14 (line 1062) states a *Prediction*. Confirmatory H1–H8 all carry predictions
   (`preregistration.md:1150-1159`). Worth a sentence in Methods: H13/H15 were registered without
   directional predictions, which is consistent with their exploratory status but should not be
   described as "predictions that were not tested".
2. **Tracking matrix wording vs execution-plan wording.** `hypothesis-tracking.md:32` records H13 as
   `Not started (low priority)`; `hypothesis-tracking.md:291` records
   `Phase 5: Exploratory (H10-H15 as triggered)   ○ H10-H13 not started`. `docs/methods-outline.md:344`
   gives a *different* reason: `| H13 (Overlap/stride) | Low priority; would require re-tiling |`.
   Both are defensible, but the paper should pick one and use it consistently. The
   "would require re-tiling" framing is the more informative and is corroborated by the fact that
   the repo does hold three distinct tile trees (`inputs/tiles/`, `inputs/tiles_256/`,
   `inputs/tiles_384/`) — re-tiling was demonstrably affordable, so "requires re-tiling" is a cost
   statement, not an impossibility statement.
3. **`hypothesis-tracking.md` is stale.** Its banner reads `**Last updated**: 2026-04-15`
   (`hypothesis-tracking.md:5`) and its last commit is `4be2d68a3` (2026-04-16, subject
   `feat(h12-v2): H12 HP:HN ratio experiment setup + protocol-errata E52`). Everything in the
   manifests post-dates it by two to three months (`results/analyses-manifest.json` last commit
   `45d0148cd`, 2026-07-27). For H13 the staleness is harmless — the status has not changed — but
   the same document's H6 row (`hypothesis-tracking.md:18`, `Not started`) is *contradicted* by
   `analyses-manifest.json` analysis `n1-baseline-matrix-384` (lines 7–56), whose `hypothesis_refs`
   include `"H6"` and whose `outcome` (line 43) asserts `H6 holds strongly and uniformly`. **Do not
   treat the tracking matrix as an authority for any hypothesis's execution status.** It is a
   pointer to be re-verified against the manifests.
4. **Manifest silence.** H13 has no manifest row at all, so the manifest neither asserts nor denies
   anything about it. The `preregistered: "exploratory"` blanket applies only to the 18 analyses
   that exist.

### 1.8 Disclosure obligation — draft paper text

> H13 (tile overlap/stride) was registered as a Tier B exploratory hypothesis comparing 12.5%,
> 25%, and 50% tile overlap at 512 px. Its registered trigger — evidence of edge-effect errors in
> holdout evaluation — was never met, and testing the additional overlap ratios would have required
> regenerating and re-running the full tile corpus at each ratio; it was therefore not executed. All
> reported results use the baseline 12.5% overlap (condition A), which was held constant across
> every tile size tested, so tile overlap is a fixed parameter of this study rather than a
> manipulated factor. H13 remains available as future work.

---

## 2. H14 — Cross-Model Consistency

### 2.1 As registered

Source: `docs/methodology/preregistration/osf/preregistration.md`, lines 1052–1070. Note that H14
sits under a section heading at line 1052:

> `### Tier C: Deferred to future work`
>
> *Tests requiring cross-provider API access, deferred to future work.*

Heading (line 1056):

> `### H14: Cross-Model Consistency`

Status (line 1058):

> **Status**: Exploratory (Tier C — deferred)

Background (line 1060):

> **Background**: Results obtained on Gemini 3 Flash / Pro may not generalise to other VLM
> architectures. Testing across Claude and GPT validates that findings reflect task properties
> rather than Gemini-specific behaviours.

Predicted outcome (line 1062):

> **Prediction**: The Flash-optimal configuration will perform similarly on Claude and GPT models,
> with at most minor factor adjustments needed.

Registered reasons for deferral (lines 1064–1068):

> **Scope**: This hypothesis is deferred to future work due to:
>
> 1. Budget constraints for cross-provider API costs
> 2. Need to first establish robust findings on single provider
> 3. Complexity of managing multiple API integrations

Registered analysis / protocol (line 1070):

> **Brief protocol**: Stepwise adjustment from Flash-optimal using OFAT sensitivity testing,
> mirroring H6 protocol. Each model tested independently on same holdout set.

Registered model roster (`preregistration.md:1201`):

> **Secondary (for H14)**: Claude 4.5 Haiku, Sonnet, Opus; GPT-5.2 Thinking, Pro

(Primary roster at line 1199: `**Primary**: Gemini 3 Flash, Gemini 3 Pro`.)

### 2.2 Registered status and tier

- **Exploratory**, **Tier C — deferred**, and *registered as deferred from the outset*. Anchors:
  `preregistration.md:1052` (section heading "Tier C: Deferred to future work" with the gloss
  "*Tests requiring cross-provider API access, deferred to future work.*"); `preregistration.md:1058`;
  `preregistration.md:1170` (§7.2 row `| H14 (cross-model) | C | Do effects generalise across
  providers? | Deferred to future work |`); `preregistration.md:2007` (`| H14 | Cross-model
  consistency | C | 📋 Deferred | Runtime model parameter (Claude, GPT) |`);
  `preregistration.md:2177` (`- **H14, H15** (cross-model) — Tier C, deferred to future work`).
- **This is materially different from H13.** H13 was registered as a *planned* Tier B test that was
  subsequently not run. H14 and H15 were registered as *already deferred*. The disclosure burden is
  correspondingly lighter — the preregistration itself, not a later decision, is the source of the
  deferral — and the paper should say so, because it converts an apparent omission into a
  registered scope statement.

### 2.3 Execution

**Not executed as registered. No non-Google model was ever called.**

Model census across the full pass register (`results/passes-manifest.md`, 1,132 rows; 1,131 with a
model label):

| Model string | Pass rows |
|---|---:|
| `gemini-3-flash` | 784 |
| `gemini-3-flash-preview` | 305 |
| `gemini-3.1-pro-preview` | 30 |
| `gemini-3.5-flash` | 12 |

Cross-checked against `results/passes-manifest.json` (same four strings: 1568 / 837 / 78 / 34
occurrences) and `results/run-conditions.json` (70 / 11 / 2 occurrences of the flash-preview,
pro-preview, and 3.5-flash strings). **Zero occurrences of any `claude*` or `gpt*` model string in
any manifest.**

Client-side confirmation: `docs/planning/future-work.md:41-47` records the Anthropic and OpenAI
clients as `⏸️ Deferred`, with the note "Non-Gemini API clients deferred until needed for H6/H14
(Phase 4-5)". `requirements.txt` contains no `anthropic` or `openai` entry (grep returns nothing).
The only Anthropic/OpenAI references in code are two docstrings in
`scripts/lib_llm_metadata.py:770` and `:858` describing hypothetical response objects — dead
scaffolding, not a live integration.

**Incidental evidence check — is any of the within-provider model work partial evidence for H14?**

This is the substantive judgement call, so state it carefully. Three bodies of within-Google
cross-model data exist:

| Body of work | Where | Models compared | Does it bear on H14? |
|---|---|---|---|
| Flash 3 vs Gemini 3.1 Pro single-pass baseline matrix | `results/analyses-manifest.json:7-56` (analysis_id `n1-baseline-matrix-384`), `hypothesis_refs: ["H1","H6","H7"]`, `deviations: ["E57"]` | `gemini-3-flash*` vs `gemini-3.1-pro-preview` | **No — this is H6**, and it is claimed as H6 by the manifest itself. H6 is a *confirmatory* within-Google transfer test (`preregistration.md:1157`); H14 is explicitly the *cross-provider* question. |
| Flash 3.5 role permutations | `results/analyses-manifest.json:756-791` (analysis_id `flash35-model-roles`), `hypothesis_refs: ["H2"]` | `gemini-3.5-flash` vs `gemini-3-flash*` as proposer and as verifier | **Closest in spirit, but not H14.** It tests whether a different model preserves the pipeline's performance shape — the H14 *logic* — but within one provider, at one role granularity, and it is registered against H2. It cannot support any claim about architecture-independence across providers. |
| Flash-Lite transfer pilot | `decisions-log.md:1010-1035` (Decision 21, dated 2026-03-15); cost trace `results/paper-tables/cost_retrospective.json:27` (`gemini-3.1-flash-lite-preview`, 180 calls, $0.04) | `gemini-3.1-flash-lite-preview` vs Flash | **No.** A capability gate that the model failed (F1 0.097–0.126 across three variants, `decisions-log.md:1026-1030`); abandoned. Not in the manifests. |

**Verdict: there is no partial evidence for H14 as registered.** Every model the study ran is a
Google/Gemini model, so the registered claim — that findings "reflect task properties rather than
Gemini-specific behaviours" — is untested in the exact respect it was designed to test. The
within-Google model variation is genuinely informative about *model-capability* sensitivity and the
paper should use it, but it must not be presented as cross-provider generalisation. Doing so would
be the specific overclaim H14 exists to guard against.

One nuance worth preserving for the Discussion: `decisions-log.md:1041-1043` records that
"**Try other cheaper models (Claude Haiku, GPT-4o-mini)**: Deferred to H14 cross-model testing.
Models with MMMU Pro < 77% are likely to fail similarly." — i.e. the project formed a *prediction*
about cross-provider transfer (capability-threshold-driven) from the Flash-Lite failure, without
testing it. That is a legitimate, citable hypothesis-generating observation, provided it is framed
as such.

### 2.4 Outcome

**None.** No result exists for H14 as registered.

### 2.5 Deviations (errata)

**None.** No erratum mentions H14. Adjacent-but-distinct entries the paper may confuse with it:

- **E40** (`protocol-errata.md:944`, Deviation, 2026-03-24) — Gemini 3.1 Pro cannot run MINIMAL
  thinking, so Pro results use MEDIUM/HIGH. This is an **H6** confound (model capability × thinking
  budget), not H14.
- **E41** (`protocol-errata.md:960`, Deviation, 2026-03-24) — the Pro comparison ran at 384 px on
  487 tiles rather than the preregistered 20-tile 512 px H6 holdout. Again **H6**.
- **E57** (`protocol-errata.md:1782`, Metadata correction + billing reconciliation, 2026-06-02 rev.
  2026-06-03) — four "Pro" cells were dispatched as Flash. **H6/H1/H7**, not H14.

### 2.6 Proposed classification

**`not-executed`** (schema extension required — see §0), with the qualifier
**"registered as deferred"**.

Justification: H14 is not a hypothesis the study abandoned; it is a hypothesis the preregistration
itself placed outside scope, with three stated reasons (`preregistration.md:1064-1068`). Any manifest
representation should preserve that distinction from H13, which was registered as in-scope and
subsequently dropped.

### 2.7 Source discrepancies

1. **Tracking matrix vs preregistration — a wording trap.** `hypothesis-tracking.md:33` records
   H14's status as `Deferred to future work`, which reads as a project decision. The preregistration
   already said this at registration time (`preregistration.md:1058`, `:1170`, `:2007`). If the paper
   sources its disclosure from the tracking matrix it will under-claim, describing as a deviation
   something that was a registered scope boundary.
2. **Execution plan promotes H14 to first priority in Phase 5** — `execution-plan.md:683-686`:
   `1. **H14 (cross-model consistency)**: Most important for generalisability`, with a costed
   protocol ("Test Flash-optimal configuration on Claude 4.5 Sonnet and GPT-5.2 Thinking … ~$40-60").
   This **contradicts the preregistration's own "deferred to future work" framing** at
   `preregistration.md:1052` and `:1170`. The execution plan (v2.5 per `execution-plan.md:814`) treats
   H14 as a live Phase 5 item; the preregistration treats it as out of scope. **The preregistration is
   the registered artefact and should govern.** Flag this in Methods only if the paper cites the
   execution plan as a companion document; otherwise it is internal noise.
3. **`docs/methods-outline.md:345`** already drafts the deferral (`| H14 (Cross-model consistency) |
   Deferred to future work |`) under a heading "What the Preregistration Planned but Was Not
   Executed" (`methods-outline.md:337`). That heading is slightly wrong for H14/H15 — the
   preregistration did *not* plan them, it deferred them. Suggest splitting that table into
   "registered and planned but not executed" (H6, H10, H13) and "registered as deferred" (H14, H15).
4. **`preregistration-coverage.md:163`** lists a factor `| Model tier | MT | 4+ (Flash, Pro, Claude,
   GPT) | H6, H14 |` — i.e. the coverage document counts Claude and GPT as levels of a registered
   factor. Since only Flash and Pro were realised, the coverage document overstates realised factor
   coverage. Worth a one-line correction if that document is published as a supplement.

### 2.8 Disclosure obligation — draft paper text

> H14 (cross-model consistency) was registered as a Tier C hypothesis and was explicitly deferred to
> future work at registration, on grounds of cross-provider API cost, the need to establish findings
> on a single provider first, and multi-provider integration complexity. No non-Google model was
> called in this study: all 1,131 recorded inference passes used Gemini 3 Flash, Gemini 3.1 Pro, or
> Gemini 3.5 Flash. The within-Google model comparisons we do report (Flash→Pro, H6; and the Flash
> 3.5 role permutations) therefore speak to model capability, not to architecture- or
> provider-independence, and we make no claim that our findings generalise beyond Gemini. H14
> remains future work.

---

## 3. H15 — Cross-Model Consensus Voting

### 3.1 As registered

Source: `docs/methodology/preregistration/osf/preregistration.md`, lines 1074–1088 (same
"Tier C: Deferred to future work" section opened at line 1052).

Heading (line 1074):

> `### H15: Cross-Model Consensus Voting`

Status (line 1076):

> **Status**: Exploratory (Tier C — deferred)

Background (line 1078):

> **Background**: Within-model consensus voting (H3) improves performance by averaging across
> passes. Voting across architecturally different models may provide more independent error
> patterns.

Research question (line 1080) — again a Question, not a Prediction:

> **Question**: Does cross-model voting outperform within-model voting at equivalent total passes?

Registered reasons for deferral (lines 1082–1086):

> **Scope**: This hypothesis is deferred to future work due to:
>
> 1. Dependency on H14 results (need to know if models perform comparably)
> 2. Cross-provider API coordination complexity
> 3. Budget constraints

Registered analysis / protocol (line 1088):

> **Brief protocol**: Compare N=6 pass voting: 6× single model vs 2× each of three models.

Execution-plan restatement (`execution-plan.md:688-690`):

> 2. **H15 (cross-model voting)**: Novel contribution
>    - 6-pass voting: 6×Flash vs 6×Sonnet vs 6×GPT vs 2×each
>    - ~$15-25

### 3.2 Registered status and tier

- **Exploratory**, **Tier C — deferred**, registered as deferred. Anchors: `preregistration.md:1052`
  (section heading), `:1076` (Status), `:1171` (§7.2 row `| H15 (cross-model voting) | C | Does
  cross-model voting outperform within-model? | Deferred to future work |`), `:2008`
  (`| H15 | Cross-model voting | C | 📋 Deferred | Multi-model ensemble voting |`), `:2177`.
- **Explicitly dependent on H14** (`preregistration.md:1084`). Since H14 was not executed, H15's own
  stated precondition was never satisfied. This is the cleanest disclosure available: H15 was not
  skipped by choice at analysis time, it was gated on a test that was itself registered as deferred.

### 3.3 Execution

**Not executed. Every voting pool in the study is single-model.**

The decisive check: `results/conditions-manifest.json` holds 322 conditions, each carrying a
`proposer_pool` field and (where applicable) a `verifier_config.model`. Enumerating every distinct
`proposer_pool` value (123 distinct values) shows **no pool that mixes models**. The four conditions
that involve two models at once separate them **by role**, not within a voting pool:

| condition_id | proposer pool | n passes | vote threshold | verifier model |
|---|---|---:|---:|---|
| `flash35-pv-2x2::f35prop-bare-10of10` | `flash35-min-text-1of10` (all Flash 3.5) | 10 | 10 | *(none — bare)* |
| `flash35-pv-2x2::f35prop-f3vf-4of10` | `flash35-min-text-1of10` (all Flash 3.5) | 10 | 4 | `gemini-3-flash-preview` |
| `flash35-pv-2x2::f35prop-f35vf-4of10` | `flash35-min-text-1of10` (all Flash 3.5) | 10 | 4 | `gemini-3.5-flash` |
| `flash35-pv-2x2::f3prop-f35vf-6of10` | `f3-min-text-1of10` (all Flash 3) | 10 | 6 | `gemini-3.5-flash` |

Similarly the Pro-verifier cells in `pv-diag-384` (`verified-adv-text-pro-vf-4of5`,
`verified-adv-image-baseline-pro-vf`, `verified-adv-pro-text-pro-vf-3of5`, and four siblings) pair a
single-model proposer pool with a `gemini-3.1-pro-preview` verifier.

This is a **cross-model cascade** (proposer stage in one model, verifier stage in another) — an
architecturally different thing from H15's design, which pools *votes* from heterogeneous models
within one aggregation step ("6× single model vs 2× each of three models", `preregistration.md:1088`).
The cascade does not produce the independent-error-pattern averaging that H15 predicts. It is,
however, a genuinely interesting adjacent finding the paper already reports —
`analyses-manifest.json:823` (analysis `unswept-pools-completeness`) records that "the PRO verifier
over the Flash-HIGH 5-pass union scores 0.8792 (4of5/pt0.25) — +0.015 over the Flash verifier on the
same pool (raw p=0.019, POST-HOC, not multiplicity-controlled)". **That is cross-model *verification*,
not cross-model *voting*, and the distinction must be maintained in the write-up.**

Cross-check: the run-level `model` column in `results/runs-manifest.md` records `mixed` for
`flash35-pv-2x2` (line 40), `pv-diag-384` (line 25), `gold-standard-v2` (line 16) and others.
"`mixed`" at run level means *the run touched more than one model across its stages*, not that any
single voting pool mixed models — the condition-level evidence above settles that.

### 3.4 Outcome

**None.** No result exists for H15 as registered.

### 3.5 Deviations (errata)

**None.** No erratum mentions H15.

### 3.6 Proposed classification

**`not-executed`** (schema extension required — see §0), with the qualifier
**"registered as deferred; precondition (H14) also not executed"**.

### 3.7 Source discrepancies

1. **`hypothesis-tracking.md:34`** records `Deferred to future work` with no date and no note of the
   H14 dependency. The dependency (`preregistration.md:1084`) is the strongest justification
   available and should be surfaced.
2. **Execution plan again promotes it** — `execution-plan.md:688` calls H15 a "Novel contribution"
   with a $15–25 budget line and a concrete four-arm design, contradicting the preregistration's
   deferral. Same resolution as §2.7 item 2: the preregistration governs.
3. **Risk of conflation with the PV cascade.** The study's most eye-catching cross-model result (Pro
   verifier over a Flash pool, +0.015 F1, `analyses-manifest.json:823`) is precisely the kind of
   finding a reader might mistake for H15. Since that analysis is registered against
   `hypothesis_refs: ["H2","H11"]` (`analyses-manifest.json:815-818`) and is flagged in its own
   `outcome` text as "POST-HOC, not multiplicity-controlled", the paper should (a) not cite it near
   H15, and (b) keep the post-hoc caveat attached wherever it is cited.
4. **Version-history noise.** `preregistration.md:2403` (the v3.6 changelog line) contains the string
   "H15 implementation status updated to confirmatory" — this refers to an *older numbering scheme*
   in which H15 was the library-composition hypothesis (the same line's v3.5 entry describes "H15
   promoted to confirmatory with Pure/Canonical/A-D library conditions"). Under the current v4.0+
   numbering (`preregistration.md:2402`, "Hypotheses renumbered H1-H15 (8 confirmatory, 7
   exploratory)") that hypothesis is **H8**. **Do not let a text search for "H15 confirmatory" in the
   changelog contaminate the reconciliation** — it is a stale identifier from a superseded numbering.

### 3.8 Disclosure obligation — draft paper text

> H15 (cross-model consensus voting) was registered as a Tier C hypothesis, explicitly deferred to
> future work at registration, and conditioned on H14 — which was itself deferred. It was not
> executed: every consensus pool reported here draws all of its passes from a single model. Where we
> do combine models, we do so across pipeline *stages* (a Gemini 3 Pro or Gemini 3.5 Flash verifier
> applied to a Gemini 3 Flash proposal pool), which tests cross-model *verification* rather than the
> heterogeneous-vote averaging H15 specifies. H15 remains future work.

---

## 4. Cross-cutting notes for the manifest pass

1. **The schema is the blocker, not the evidence.** Evidence for all three hypotheses is
   unambiguous and quickly re-verifiable. The open question is representational: the enum at
   `docs/manifest-schemas/analyses-manifest.schema.json:48` has no way to say "registered, not
   executed". Recommend adding `"not-executed"` to the enum *and* a companion boolean or note field
   distinguishing "registered as deferred" (H14, H15) from "registered as planned, then dropped"
   (H13). Without that distinction the register flattens two ethically different situations.
2. **`hypothesis-tracking.md` should be marked stale in-place, not trusted.** It is 3+ months behind
   the manifests and demonstrably wrong for H6. If the project's Document Revision Policy
   (`CLAUDE.md`, "Document Revision Policy") is applied on touch, this file is a strong candidate.
3. **Three of the fifteen hypotheses have no manifest presence at all** among those inspected here
   (H13, H14, H15); the D17 note at `docs/paper/results-outline.md:448` also names H6 and H10 as
   registered-but-unexecuted per the tracking matrix — but H6 *does* have manifest presence and an
   asserted outcome (see §1.7 item 3). **H6 and H10 are outside this brief and should be checked by
   whoever holds them**; do not carry the tracking matrix's "Not started" forward for H6 without
   re-reading `results/analyses-manifest.json:7-56`.
4. **Nothing here requires new compute.** Every claim in this document was settled by reading
   committed artefacts.

---

## 5. Open questions this inventory could not settle

| Question | What would settle it |
|---|---|
| Should `not-executed` become a fourth enum value, or should unexecuted registrations live in a separate list outside `analyses`? | A PI decision on `docs/manifest-schemas/analyses-manifest.schema.json`; both are defensible. The enum route keeps one table; the separate-list route avoids rows with null `conditions_compared`. |
| Was H13's trigger ("significant edge-effect errors observed in Stage 2 holdout evaluation") ever *evaluated and found negative*, or simply never evaluated? | UNVERIFIED — would need a search of session reflections for an explicit edge-effect assessment. No artefact in `results/` reports one, and `results/h11-tile-size-results.md` does not test it. Absent such evidence the honest statement is "never evaluated", which is what §1.8 drafts. |
| Does the project intend to claim any cross-model generalisation at all in the paper? | A PI decision. If yes, it must be scoped to Gemini and cite H6 / `flash35-model-roles`, never H14. |
