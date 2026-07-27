# Walkthrough: the unexecuted hypotheses H13, H14, H15

**Repository**: `/home/shawn/Code/map-reader-llm` (read-only inspection; no edits, no commits).
**Compiled**: 2026-07-27. Canonical preregistration:
`docs/methodology/preregistration/osf/preregistration.md` (v4.7, registration date 2026-01-31 per
commit `bd65c007f`, subject `docs(preregistration): Update date to 2026-01-31 for registration`).

Every checkable specific below carries a re-verifiable anchor. Quotations are verbatim. Where a
question could not be settled from committed artefacts it is marked **UNVERIFIED** with a note on
what would settle it.

---

## 0. Read this first: the hypotheses were renumbered, and it changes what "silence" means

The hypotheses were renumbered at preregistration **v4.0**. The restructure landed in commit
`af486fa56` (2026-01-08, `docs(preregistration): Update to v4.2 with pilot context and pooling
methodology`; 583 insertions / 522 deletions). The last pre-v4.0 text is commit `fbca6b454`
(2026-01-07, v3.7), at path `docs/methodology/preregistration/preregistration.md` — the file moved
to `osf/` later, at `3b245c689` (2026-01-23).

Hypothesis headings in the v3.7 text (`git show fbca6b454:docs/methodology/preregistration/preregistration.md`,
lines 921, 985, 1023, 1063, 1099) versus the current numbering give this mapping for our three:

| Current | Pre-v4.0 identifier | Title then | Title now |
|---|---|---|---|
| **H13** | *none* — **new at v4.0**; drafted as **"H18"** | — | Overlap/Stride Effects |
| **H14** | **H12** | Cross-Model Consistency | Cross-Model Consistency |
| **H15** | **H13** | Cross-Model Consensus Voting | Cross-Model Consensus Voting |

Three consequences, and they are the reason this section comes first:

1. **The trap.** Pre-v4.0, **"H13" *was* cross-model consensus voting**. Any search of material
   written before 2026-01-08 that keys on "H13" returns cross-model-voting hits, not overlap/stride
   hits. Symmetrically, pre-v4.0 "H12" is cross-model consistency, whereas *current* H12 is the
   HP:HN ratio hypothesis (pre-v4.0 "H17").
2. **H13 has a third identifier.** In the drafting document the overlap hypothesis was called
   **H18** before it was called H13:
   `archive/preregistration/document-revisions/cc-prereg-simplifications.md:17` reads
   `8. Add H18 (overlap/stride) as Tier B exploratory`, and the same file's mapping table at
   `:725-727` reads:

   > `| H18 | **H13** | Exploratory (Tier B) | Overlap/stride |`
   > `| H12 | **H14** | Exploratory (Tier C) | Cross-model consistency (deferred) |`
   > `| H13 | **H15** | Exploratory (Tier C) | Cross-model voting (deferred) |`

3. **H13 cannot have a pre-v4.0 decision trail**, because it did not exist before 2026-01-08. The
   preregistration's own v4.0 changelog entry confirms it: `preregistration.md:2402` includes
   `new H13 added (overlap/stride)`. So for H13, absence of pre-2026-01-08 discussion is expected
   and is *not* evidence of a silent drop; absence of post-2026-01-08 discussion is.

**Identifiers searched, per hypothesis** (so the negative findings are auditable):

| Hypothesis | Identifiers searched | Corpora |
|---|---|---|
| H13 | `H13`, `H18`, `overlap/stride`, `Overlap/Stride`, `overlap`, `stride` | repo tree; git history; `~/cc-archives/map-reader-llm` (74 sessions, from 2025-12-22) and `~/cc-archives/vlm-burial-mound-detection` (25 sessions, 2026-05-23 → 2026-06-12) via the indexed searcher |
| H14 | `H14`, pre-v4.0 `H12`, `cross-model`, `Claude`, `GPT`, `anthropic`, `openai` | same |
| H15 | `H15`, pre-v4.0 `H13`, `cross-model voting` | same |

---

## 1. H13 — Overlap/Stride Effects on Detection Performance

### 1.1 As registered

Source: `docs/methodology/preregistration/osf/preregistration.md`, lines 1014–1048.

Heading (`:1014`):

> `### H13: Overlap/Stride Effects on Detection Performance`

Status (`:1016`):

> **Status**: Exploratory (Tier B)

Background (`:1018`):

> **Background**: Current tiling uses 64px overlap (12.5% of 512px tile, 448px stride). Higher
> overlap increases redundant coverage, potentially catching symbols near tile edges that might be
> missed or poorly detected. However, it also increases API costs proportionally.

Registered as a **Question, not a Prediction** (`:1020`):

> **Question**: Does increasing tile overlap improve detection performance, and is the cost
> justified?

Design arms (`:1024-1028`), verbatim:

| Condition | Overlap | Stride | Overlap % | Tiles (×) | API Cost (×) |
| --------- | ------- | ------ | --------- | --------- | ------------ |
| A | 64px | 448px | 12.5% | 1× | 1× |
| B | 128px | 384px | 25% | ~1.4× | ~1.4× |
| C | 256px | 256px | 50% | ~2× | ~2× |

Analysis plan (`:1042-1046`):

> **Analysis**:
>
> - F1 as function of overlap
> - Cost-efficiency: F1 improvement per additional API dollar
> - Edge-detection analysis: Does overlap specifically help symbols near original tile boundaries?

Trigger (`:1048`) — quoted verbatim including the source's stray space before the full stop:

> **Trigger**: Run if significant edge-effect errors observed in Stage 2 holdout evaluation or if
> disappointing F1 performance warrants testing multiple perspectives on the same location .

Corroborating tier anchors: `:1169` (`| H13 (overlap/stride) | B | Does increased overlap improve
edge detection? | F1 vs overlap, cost analysis |`); `:2006` (`| H13 | Overlap/stride | B |
📋 Planned | Tile overlap parameter |`); `:2176` (`- **H13** (overlap/stride) — Tier B exploratory`).
The preregistration also flags a planned interaction at `:2280`: "**Rationale**: H11 (tile size) and
H13 (overlap/stride) may interact—smaller tiles may require different overlap ratios than larger
tiles."

#### 1.1a The trigger was silently broadened after v4.0 — and the added clause is arguably satisfied

At `af486fa56` (v4.2, 2026-01-08) the trigger was a single clause:

> **Trigger**: Run if significant edge-effect errors observed in Stage 2 holdout evaluation.

The second clause — `or if disappointing F1 performance warrants testing multiple perspectives on
the same location` — was added in commit `ce17da492` (2026-01-09,
`docs(preregistration): Update to v4.3 with pure-positive baseline`). That commit's changelog entry
(`preregistration.md:2399`, the v4.3 line) describes only the pure-positive baseline change; **the
trigger broadening is not mentioned in the changelog**. Verified by
`git log -S "disappointing F1 performance" -- docs/methodology/preregistration/`, which returns
`ce17da492` alone.

This matters for the disclosure. The registered trigger is a **disjunction**, and the study's
single-pass F1 was in fact "disappointing" by the project's own standard — `hypothesis-tracking.md:81`
records the single-stage baseline at F1=0.660, and the project responded to that disappointment
exactly as the clause anticipates, by "testing multiple perspectives on the same location" — but via
consensus voting (H3) and proposer–verifier cascades (H2) rather than via overlap. So the honest
statement is *not* "the trigger was not met"; it is closer to "the first trigger clause was never
evaluated, and the second was arguably met but answered by a different mechanism". See §1.4 for why
this matters: the only recorded characterisation says "not triggered".

#### 1.1b The registered H13 is weaker than the drafted H13

The drafting document `archive/preregistration/document-revisions/cc-prereg-simplifications.md`
(Change 8, `:415-465`) proposed a version with **directional predictions** and a different analysis:

> **Predictions**: Based on literature, expect:
> - Medium (25%) to show improvement over Current (12.5%)
> - High (50%) to show diminishing returns over Medium
> - Optimal likely in 25-50% range

> **Analysis**:
>
> - Primary: One-way ANOVA across 3 overlap conditions

and a different trigger and a costing:

> **Trigger**: Run after main factorial if budget allows (~$8 additional)
>
> **Cost**: 3 conditions × K=10 × variable tiles ≈ 3,800 calls average (~$6)

The predictions and the ANOVA did not survive into the registered text; the registered H13 carries a
bare Question and a descriptive analysis plan. **The ~$6–8 costing is the material fact here**: on
the drafters' own estimate H13 was among the cheapest tests in the programme, which substantially
weakens "budget" as an explanation for not running it (see §1.4).

### 1.2 Execution status

**Not executed as a contrast.** No run, condition, or analysis in the repository references H13.

Independently re-verified (all negative):

| Check | Target | Result |
|---|---|---|
| Analyses register | `results/analyses-manifest.json` — 18 analyses, every `hypothesis_refs` array enumerated | Census: `H1`×3, `H2`×6, `H3`×9, `H4`×2, `H5`×2, `H6`×1, `H7`×3, `H8`×2, `H9`×2, `H11`×2, empty×2. **H13, H14, H15 all absent.** |
| Errata | `grep -c "H13" docs/methodology/preregistration/protocol-errata.md` | **0** |
| Decisions log | `grep -c "H13" docs/methodology/preregistration/decisions-log.md` | **0** |
| Session log | `grep -c "H13" docs/notes/reflections/session-log.md` | **0** |
| Working notes | `grep -c "H13" docs/notes/working-notes.md` | **0** |
| Either spelling of the factor | `grep -c "overlap/stride"` and `"Overlap/Stride"` in all four files above | **0** in every case |

### 1.3 Can the fixed 12.5 % tiling be called "arm A"? — No, and the overstatement has two distinct parts

Overlap ratio was held at 12.5 % at **every** tile size the study ran. I verified this three ways,
including by computing tile-origin spacing directly from the manifests rather than trusting prose:

| Tile size | Overlap (px) | Stride (px) | Ratio | How verified |
|---|---:|---:|---:|---|
| 512 | 64 | 448 | 12.5 % | `config.py:66-68` — `TILE_SIZE = 512`, `OVERLAP = 64`, `STRIDE = TILE_SIZE - OVERLAP`; and `studies/h11-384-single-pass.yaml:57-58` (`overlap: 64`, `stride: 448`) |
| 384 | 48 | 336 | 12.5 % | `studies/h11-384-single-pass.yaml:51-52` (`overlap: 48`, `stride: 336`) |
| 256 | 32 | 224 | 12.5 % | derived from tile-origin spacing (below) |

Computed from the tile manifests (minimum consecutive difference between distinct x-origins, which
equals the stride):

| Manifest | Tiles | Tile size | Stride observed | Implied overlap | Ratio |
|---|---:|---:|---:|---:|---:|
| `inputs/tiles_256/full_evaluation_manifest.json` | 1032 | 256 | 224 | 32 | 12.5 % |
| `inputs/tiles_384/full_evaluation_manifest.json` | 487 | 384 | 336 | 48 | 12.5 % |
| `inputs/tiles/full_evaluation_manifest.json` | 340 | 512 | 448 | 64 | 12.5 % |

**Why "arm A ran" would overstate, part 1 — a baseline is not a contrast.** The registered analysis
plan (`:1042-1046`) is entirely comparative: "F1 as function of overlap", "F1 improvement per
additional API dollar", and an edge-detection comparison. Every one of those requires at least two
arms. One arm yields no value for any registered quantity. The tile-size sweep varied *absolute*
overlap (32/48/64 px) only as an arithmetic consequence of tile size, with the **ratio deliberately
fixed** — that is the opposite of H13's design, which fixes tile size at 512 px and varies the ratio.

**Why "arm A ran" would overstate, part 2 — arm A is specified in pixels, not as a ratio.** This is
a sharper point and it is worth getting right. Registered arm A is `| A | 64px | 448px | 12.5% |`
(`:1026`) — an absolute specification. **Only the 512 px corpus matches it.** The 384 px and 256 px
corpora preserve the 12.5 % *ratio* but run 48 px and 32 px overlap respectively, so they satisfy
neither arm A's overlap nor its stride. A claim of the form "arm A was run across the study" is
therefore wrong twice over; the defensible claim is narrower: *the 512 px tiling coincides with arm
A's parameters, and was used as the study's fixed baseline rather than as one level of a
manipulated factor.*

### 1.4 The decision trail — **no dated decision is recorded**

This is the finding the paper must handle carefully. H13 appears **zero** times in all four
decision-trail documents (§1.2). The only places it is mentioned outside the preregistration itself
are status assertions, not decisions, and they do not agree with each other:

| Source | Text | Character |
|---|---|---|
| `docs/methodology/preregistration/execution-plan.md:702` | `5. **H11, H13**: Lower priority, if budget allows` | Priority ranking, undated |
| `docs/methodology/preregistration/hypothesis-tracking.md:32` | `\| H13 \| Overlap/Stride Effects \| Tile overlap \| B \| Not started (low priority) \| — \|` | Status, **date column empty** |
| `docs/methodology/preregistration/hypothesis-tracking.md:291` | `Phase 5: Exploratory (H10-H15 as triggered)            ○ H10-H13 not started` | Status |
| `docs/methods-outline.md:344` | `\| H13 (Overlap/stride) \| Low priority; would require re-tiling \|` | A **different** reason — re-tiling cost |
| `docs/planning/future-work.md:29` | `\| H13 \| Overlap/stride effects \| 5 \|` | Phase listing only |

Note the reasons diverge: "budget", "low priority", and "would require re-tiling". None is dated,
none is attributed, and none is recorded as a decision. Two of them are also weak on the evidence:
the drafters costed H13 at ~$6 (§1.1b), and the repository demonstrably holds **three** independently
generated tile trees (`inputs/tiles/`, `inputs/tiles_256/`, `inputs/tiles_384/`), so re-tiling was
affordable and routinely done. "Would require re-tiling" is a statement of cost, not of
impossibility.

**The nearest thing to a decision is in the transcripts, and it is oblique.** Session
`2026-03-11T04-33_b21c542c`, turn 44 (**assistant**), lists programme status:

> - **H13** (Overlap/Stride) — not triggered
> - **H14–H15** (Cross-Model) — deferred to future work

Shawn replies at turn 49 (**user** — his own words):

> no, this can wait, I need to work on the LLM-History-Paper, I just wanted to get it clear in my
> mind where we are. […] We should also undertake at least H10-H12 I think.

Two things follow, and they should be reported separately because they are different kinds of
evidence:

1. **Shawn's own scoping** — presented with the full H10–H15 list, he named "at least H10-H12",
   which leaves H13, H14 and H15 outside the intended work. This is the strongest user-level
   evidence available. But "at least" is permissive, and he did not say "drop H13". It is a
   **scoping remark, not a recorded deferral**, and the paper should not upgrade it into one.
2. **The "not triggered" claim is an assistant characterisation that was never checked.** It appears
   in an assistant turn, not in any committed artefact, and it addresses only the first trigger
   clause. Per §1.1a the registered trigger is a disjunction whose second clause is arguably
   satisfied. No artefact anywhere in `results/` reports an edge-effect assessment: searches for
   tile-edge/edge-effect analyses surface only verifier crop-truncation code and evaluation-scoping
   discussion, and `results/h11-tile-size-results.md` does not test it.

**Verdict for H13: a silent drop.** The hypothesis was registered in-scope with a full three-arm
design, a stated analysis plan, and a disjunctive trigger. It was never run, the trigger was never
formally evaluated, and **no dated, attributed decision to defer or drop it exists in any committed
artefact**. The paper must disclose it as such, and must not borrow H14/H15's "registered as
deferred" cover — that cover does not extend to H13.

### 1.5 Draft disclosure text

> H13 (tile overlap/stride) was registered as a Tier B exploratory hypothesis comparing 12.5 %, 25 %
> and 50 % overlap at 512 px, with a registered trigger of edge-effect errors in holdout evaluation
> or disappointing F1 warranting multiple perspectives on the same location. It was not executed,
> and we record that no dated decision to defer it appears in our project documentation: the
> hypothesis is marked "not started (low priority)" in our tracking matrix without a rationale or a
> date, and the registered edge-effect analysis was never performed. All reported results use a
> fixed 12.5 % overlap, held constant at every tile size tested, so tile overlap is a fixed
> parameter of this study rather than a manipulated factor; the 512 px tiling coincides with the
> parameters of registered condition A but was never contrasted against conditions B or C. H13
> remains open as future work.

---

## 2. H14 — Cross-Model Consistency

### 2.1 As registered

Source: `preregistration.md`, lines 1052–1070, under a section heading at `:1052`:

> `### Tier C: Deferred to future work`
>
> *Tests requiring cross-provider API access, deferred to future work.*

Heading (`:1056`): `### H14: Cross-Model Consistency`

Status (`:1058`):

> **Status**: Exploratory (Tier C — deferred)

Background (`:1060`):

> **Background**: Results obtained on Gemini 3 Flash / Pro may not generalise to other VLM
> architectures. Testing across Claude and GPT validates that findings reflect task properties
> rather than Gemini-specific behaviours.

This one carries a **Prediction**, not a Question (`:1062`):

> **Prediction**: The Flash-optimal configuration will perform similarly on Claude and GPT models,
> with at most minor factor adjustments needed.

Registered precondition / reasons for deferral (`:1064-1068`):

> **Scope**: This hypothesis is deferred to future work due to:
>
> 1. Budget constraints for cross-provider API costs
> 2. Need to first establish robust findings on single provider
> 3. Complexity of managing multiple API integrations

Protocol (`:1070`):

> **Brief protocol**: Stepwise adjustment from Flash-optimal using OFAT sensitivity testing,
> mirroring H6 protocol. Each model tested independently on same holdout set.

Model roster (`:1201`): `**Secondary (for H14)**: Claude 4.5 Haiku, Sonnet, Opus; GPT-5.2 Thinking, Pro`
(primary at `:1199`: `**Primary**: Gemini 3 Flash, Gemini 3 Pro`). Further tier anchors: `:1170`,
`:2007`, `:2177`.

**Important qualification introduced by the renumbering.** Pre-v4.0, this hypothesis (as **H12**)
was **not** deferred. Its status line at `git show fbca6b454:…/preregistration.md` read:

> **Status**: Exploratory but important for generalisability claims. Cross-architecture transfer
> (Gemini → Claude/GPT) is less certain than cross-tier transfer (Flash → Pro) due to fundamental
> architectural differences.

and it carried a detailed four-phase protocol (baseline comparison, OFAT factor sensitivity, voting
analysis, conditional refinement) with explicit success criteria. **The deferral was introduced
during the v4.0 restructure on 2026-01-07/08**, one day before registration-track edits, and it was
in place by `af486fa56`. So the deferral is genuinely registered — but it was a decision taken
shortly before registration, not a property the hypothesis always had. The paper can say either; it
should not imply the hypothesis was always out of scope.

### 2.2 Execution status

**Not executed. No non-Google model was ever called.** Re-verified independently rather than taken
from the prior inventory.

Model census over `results/passes-manifest.md` (1,132 data rows; column 2), recounted from source:

| Model string | Pass rows |
|---|---:|
| `gemini-3-flash` | 784 |
| `gemini-3-flash-preview` | 305 |
| `gemini-3.1-pro-preview` | 30 |
| `gemini-3.5-flash` | 12 |
| *(blank)* | 1 |

Case-insensitive occurrence counts for `claude`, `gpt`, `anthropic`, `openai` across
`results/passes-manifest.md`, `results/passes-manifest.json`, `results/run-conditions.json`,
`results/conditions-manifest.json`, `results/runs-manifest.md`, `results/analyses-manifest.json`:
**zero in all six files, for all four strings.**

Client side: `requirements.txt` lists `google-generativeai` and `google-genai>=1.69.0` and contains
no `anthropic` or `openai` entry (grep across `requirements.txt`, `requirements-lock.txt`, `uv.lock`,
`pyproject.toml` returns nothing). `docs/planning/future-work.md:41-47` records both clients as
`⏸️ Deferred` with the note `Non-Gemini API clients deferred until needed for H6/H14 (Phase 4-5)`.

### 2.3 Partial or incidental evidence — three bodies of work, none of them H14

Being fair in both directions here matters, because there *is* genuinely informative model-variation
data; it simply does not answer the registered question.

| Body of work | Anchor | Models compared | Bears on H14? |
|---|---|---|---|
| Flash → Gemini 3.1 Pro single-pass baseline matrix | `results/analyses-manifest.json`, analysis `n1-baseline-matrix-384`, `hypothesis_refs: ["H1","H6","H7"]`, `deviations: ["E57"]` | `gemini-3-flash*` vs `gemini-3.1-pro-preview` | **No — this is H6**, and the manifest claims it as H6. H6 is within-Google tier transfer; H14 is explicitly cross-*provider*. |
| Flash 3.5 role permutations | `results/analyses-manifest.json`, analysis `flash35-model-roles`, `hypothesis_refs: ["H2"]` | `gemini-3.5-flash` vs `gemini-3-flash*` as proposer and as verifier | **Closest in spirit, but not H14.** It tests whether swapping the model preserves the pipeline's performance shape — H14's *logic* — but within one provider and registered against H2. Its recorded outcome ("Flash 3.5 wins in NO role at the minimal operating point") is a model-capability result, not an architecture-independence result. |
| Flash-Lite transfer pilot | `docs/methodology/preregistration/decisions-log.md`, "Decision 21: Abandon Flash-Lite Transfer Pathway", **Date: 2026-03-15** | `gemini-3.1-flash-lite-preview` vs Flash | **No.** A capability gate the model failed (F1 0.111 / 0.126 / 0.097 across three variants). Abandoned; absent from the analyses manifest. |

**Verdict: no partial evidence for H14 as registered.** Every model called in this study is a Gemini
model. The registered claim — that findings "reflect task properties rather than Gemini-specific
behaviours" — is untested in precisely the respect it was designed to test. The within-Google
variation is real evidence about *model capability* and the paper should use it; presenting it as
cross-provider generalisation would be the specific overclaim H14 exists to prevent.

**One nuance worth carrying into the Discussion.** The project formed a cross-provider *prediction*
from the Flash-Lite failure without testing it. `decisions-log.md:1041-1043`:

> 2. **Try other cheaper models (Claude Haiku, GPT-4o-mini)**: Deferred to
>    H14 cross-model testing. Models with MMMU Pro < 77% are likely to fail
>    similarly.

and `docs/notes/working-notes.md:3259` frames the same gap from the other side:

> Cross-provider testing (H14) would directly address this.

That is a legitimate, citable hypothesis-generating observation provided it is framed as such.

### 2.4 The decision trail — recorded, and traceable to a durable artefact

Unlike H13, H14's deferral **is** recorded, in three independent places:

1. **In the registered preregistration itself** — `:1052` (section heading), `:1058` (status),
   `:1064-1068` (three numbered reasons), `:1170`, `:2007`, `:2177`. This is the strongest form: the
   registered artefact states the scope boundary.
2. **In the drafting document that produced it** —
   `archive/preregistration/document-revisions/cc-prereg-simplifications.md:529-534`:

   > `### Tier C: Deferred to Future Work`
   >
   > These hypotheses are beyond the scope of the current study. See Section 12 for discussion.
   >
   > - **H14**: Cross-model consistency (Claude, GPT)
   > - **H15**: Cross-model voting

   with the rationale at `:553-559` (written under the *old* numbers, hence easy to miss):

   > `### 12.1 Cross-Model Generalization (H12, H13)`
   > […]
   > *Deferred to potential Paper 2: "Do VLM symbol extraction strategies generalize across
   > architectures?"*

3. **In the preregistration's own Future Directions section** — `:2238` (`## 12. Future Directions`),
   `:2242` (`### 12.1 Cross-Model Generalisation`). The deferral therefore survived into the
   registered text as a positive statement of future scope, not merely as an omission.

Two wording caveats worth knowing. The deferral target was originally "Paper 2" —
`af486fa56` reads `### Tier C: Deferred to Paper 2` and `**Scope**: This hypothesis is deferred to
Paper 2 due to:`. It was generalised to "future work" in commit `ce17da492` (2026-01-09), the same
commit that broadened H13's trigger (§1.1a) and likewise without a changelog note.

**One live contradiction the paper should be aware of.** The execution plan promotes H14 to *first*
priority in Phase 5 — `docs/methodology/preregistration/execution-plan.md:683-686`:

> 1. **H14 (cross-model consistency)**: Most important for generalisability
>    - Test Flash-optimal configuration on Claude 4.5 Sonnet and GPT-5.2 Thinking
>    - OFAT sensitivity testing per factor (same protocol as H6)
>    - ~$40-60 (depends on provider pricing)

This contradicts the preregistration's "deferred to future work" framing. **The preregistration is
the registered artefact and governs.** Relatedly, `docs/notes/reflections/session-log.md:2808`
carries an **unchecked, never-closed** to-do:

> `- [ ] Cross-model comparison design (H14, using MMMU Pro leaderboard)`

so intent to run H14 was live at some point during the project even though the registered document
had deferred it. That is worth a sentence, because it is honest and it explains the execution plan.

Finally, `docs/methodology/preregistration/osf/preregistration-coverage.md:163` lists a factor
`| Model tier | MT | 4+ (Flash, Pro, Claude, GPT) | H6, H14 |` — i.e. the coverage document counts
Claude and GPT as levels of a realised factor. Only Flash and Pro were realised, so that document
overstates coverage and needs a one-line correction if published as a supplement.

### 2.5 Draft disclosure text

> H14 (cross-model consistency) was registered as a Tier C exploratory hypothesis and was explicitly
> deferred to future work at registration, on three recorded grounds: cross-provider API cost, the
> need to establish robust findings on a single provider first, and the complexity of managing
> multiple API integrations. It was not executed, and no non-Google model was called at any point in
> this study: all 1,131 model-labelled inference passes used Gemini 3 Flash, Gemini 3.1 Pro or
> Gemini 3.5 Flash, and no Anthropic or OpenAI client was ever added to the codebase. The
> within-Google model comparisons we do report — the Flash→Pro transfer test (H6) and the Flash 3.5
> role permutations — therefore speak to model capability rather than to architecture- or
> provider-independence, and we make no claim that our findings generalise beyond Gemini. H14
> remains future work.

---

## 3. H15 — Cross-Model Consensus Voting

### 3.1 As registered

Source: `preregistration.md`, lines 1074–1088, in the same Tier C block opened at `:1052`.

Heading (`:1074`): `### H15: Cross-Model Consensus Voting`

Status (`:1076`):

> **Status**: Exploratory (Tier C — deferred)

Background (`:1078`):

> **Background**: Within-model consensus voting (H3) improves performance by averaging across
> passes. Voting across architecturally different models may provide more independent error
> patterns.

Again a **Question**, not a Prediction (`:1080`):

> **Question**: Does cross-model voting outperform within-model voting at equivalent total passes?

Registered precondition and reasons for deferral (`:1082-1086`) — **note item 1, the precondition**:

> **Scope**: This hypothesis is deferred to future work due to:
>
> 1. Dependency on H14 results (need to know if models perform comparably)
> 2. Cross-provider API coordination complexity
> 3. Budget constraints

Protocol (`:1088`):

> **Brief protocol**: Compare N=6 pass voting: 6× single model vs 2× each of three models.

Tier anchors: `:1171`, `:2008`, `:2177`. The pre-v4.0 version (as **H13**) specified the arms
explicitly — A: 6× Flash; B: 6× Sonnet; C: 6× GPT-5.2 Thinking; D: 2× Flash + 2× Sonnet + 2×
Thinking, at threshold 4/6 — and, like old H12, was **not** marked deferred; its status read
"Exploratory. Tests whether architectural diversity in ensembles provides benefits beyond
single-model voting."

**H15's registered precondition was never satisfied**, because H14 was itself never executed. This
is the cleanest disclosure available for any of the three: H15 was not skipped by choice at analysis
time, it was gated on a test that was registered as deferred.

### 3.2 Execution status

**Not executed. No scored condition aggregates votes across models.**

`results/conditions-manifest.json` holds **322 conditions** with **123 distinct `proposer_pool`
values**. Verifier models across those conditions are `gemini-3-flash-preview` (66),
`gemini-3.1-pro-preview` (7), `gemini-3.5-flash` (2), and `null` (247) — all Gemini.

I did not rely on pool *names* for this. The decisive check joins pass records to pools by the model
actually recorded per pass: over `results/passes-manifest.json` (1,132 pass records, each carrying
`run_id`, `proposer_pool` and `model_used`), there are **265 distinct `(run_id, proposer_pool)`
pairs**, of which **exactly one** spans more than one model — see §3.3. Every other pool is
single-model on both `model_used` and `model_requested`.

The four conditions that involve two models at once separate them **by pipeline stage**, not within
a voting pool. Example, from `results/conditions-manifest.json` (run `flash35-pv-2x2`):

| condition_id | proposer pool | n passes | vote threshold | verifier model |
|---|---|---:|---:|---|
| `flash35-pv-2x2::f35prop-bare-10of10` | `flash35-min-text-1of10` | 10 | 10 | *(none)* |
| `flash35-pv-2x2::f35prop-f3vf-4of10` | `flash35-min-text-1of10` | 10 | 4 | `gemini-3-flash-preview` |
| `flash35-pv-2x2::f35prop-f35vf-4of10` | `flash35-min-text-1of10` | 10 | 4 | `gemini-3.5-flash` |
| `flash35-pv-2x2::f3prop-f35vf-6of10` | `f3-min-text-1of10` | 10 | 6 | `gemini-3.5-flash` |

Similarly, seven `pv-diag-384` conditions pair a single-model proposer pool with a
`gemini-3.1-pro-preview` verifier (`verified-adv-text-pro-vf-4of5`,
`verified-adv-image-baseline-pro-vf`, `verified-adv-text-baseline-pro-vf`,
`verified-adv-pro-text-pro-vf-3of5`, `verified-adv-pro-image-pro-vf-3of5`,
`verified-adv-pro-text-baseline-pro-vf`, `verified-adv-pro-image-baseline-pro-vf`).

This is a **cross-model cascade** — proposer in one model, verifier in another — which is
architecturally different from H15's design of pooling *votes* from heterogeneous models within one
aggregation step. The cascade cannot produce the independent-error-pattern averaging H15 asks about.
It is nonetheless a real and interesting adjacent finding the project already reports: the analysis
`unswept-pools-completeness` (`results/analyses-manifest.json`, `hypothesis_refs: ["H2","H11"]`)
records that "the PRO verifier over the Flash-HIGH 5-pass union scores 0.8792 (4of5/pt0.25) — +0.015
over the Flash verifier on the same pool (raw p=0.019, POST-HOC, not multiplicity-controlled)".
**That is cross-model verification, not cross-model voting**, it is flagged post-hoc in its own
outcome text, and the distinction must be maintained in the write-up — a reader could easily mistake
it for H15.

### 3.3 A finding beyond the prior inventory: one mixed-model pass pool exists, unaggregated

The prior inventory concluded that "every one of 322 conditions has a single-model proposer pool",
reasoning over the 123 distinct pool *names*. That is a name-level check. The model-level check
finds one exception, and it deserves recording because it is the only place in the entire study
where passes from two different models sit under a single pool label.

Pool `pro-high-text-n5-text-t0.7` in run `pv-diag-384` holds **10 passes**:

| Passes | `model_used` = `model_requested` | Thinking | T | Tiles |
|---|---|---|---|---:|
| `…::run1` – `…::run5` | `gemini-3-flash` | high | 0.7 | 487 each |
| `…::run6` – `…::run10` | `gemini-3.1-pro-preview` | high | 0.7 | 487 each |

Re-verified at source, not from the manifest: the per-run batch metadata at
`outputs/h11/pv-diag-384/pro-high-text-n5/text-t0.7/run_{1..10}/detections_text-t0.7_run{01..10}.meta.json`
carries `configuration.model = gemini-3-flash` for runs 1–5 and `gemini-3.1-pro-preview` for runs
6–10.

**Three qualifications, all of which cut against reading this as H15 evidence:**

1. **No scored condition aggregates the mixed span.** Conditions drawing on this pool declare
   `n_passes: 1` (`baseline-pro-text-high-t-0-7`) or `n_passes: 5`
   (`verified-adv-pro-text-{flash,pro,medium}-vf-3of5`, pool label `pro-high-text-1of5`). Nothing
   votes over all ten. So no reported number anywhere in the study is the output of a cross-model
   vote.
2. **The evidence for the mix is the field the project's own erratum says never to trust.** E57
   (`docs/methodology/preregistration/protocol-errata.md:1782`, "H11 384px Pro/baseline detection
   metadata", 2026-06-02 rev. 2026-06-03) states: "**The authoritative field for *what ran* is
   `per_item_metadata.model_version` / `pricing_used.model` — NEVER `config.model`**". In these ten
   batch-API metadata files both authoritative fields are **absent** (`pricing_used` and
   `per_item_metadata` are not present; `usage_stats` totals are zero). So the mix is *recorded* but
   not *authoritative*.
3. **E57 asserts the opposite for this pool.** It lists `pro-high-text-n5` among four `pv-diag-384`
   cells that "ARE genuinely Pro: `pricing_used.model = gemini-3.1-pro-preview` at $2/$12 rates".
   That claim and the run-1–5 metadata cannot both be complete descriptions of all ten passes.

**UNVERIFIED — would need**: (a) the billing/pricing records E57 cites, to establish which of runs
1–10 were dispatched as Pro; and (b) the build provenance of the 5-pass `pro-high-text-1of5` pool
(its evaluation records only a materialised
`results/verifier-robustness/condition-sets/pro-pro-vf-3of5.geojson`, and
`results/run-conditions.json` defines `pro-high-text-n5-text-t0.7` but not `pro-high-text-1of5`), to
establish whether those three "pro" PV conditions draw runs 1–5 or runs 6–10. If they draw runs 1–5,
three conditions currently labelled "pro" would rest on Flash proposals — an E57-class mislabel that
E57 itself does not cover, since E57 addressed the N=1 baseline matrix and `n1-outstanding-384`
rather than the verifier-robustness PV cells.

**This does not change the H15 conclusion** — no cross-model vote was scored, so H15 remains
unexecuted — but it is a live data-integrity thread for the PI, and it is exactly the kind of
"unexpected data" the project's own CLAUDE.md asks to be preserved and compared rather than tidied
away. It also means the raw material for a small, unplanned cross-model voting comparison (5 Flash +
5 Pro passes over the same 487 tiles at matched thinking and temperature) already exists on disk, at
zero additional API cost, should the PI want an opportunistic partial answer to H15's question.

### 3.4 The decision trail — recorded via H14, essentially silent on its own account

H15's deferral is recorded in the same places and the same act as H14's (§2.4): the registered
preregistration (`:1052`, `:1076`, `:1082-1086`, `:1171`, `:2008`, `:2177`), the drafting document
(`cc-prereg-simplifications.md:529-534`, rationale at `:553-559`), and Future Directions (`:2242`).

Independently of H14, however, H15 is almost invisible in the project record: `grep -c "H15"` returns
**0** in `docs/notes/reflections/session-log.md`, **0** in `decisions-log.md`, **0** in
`protocol-errata.md`, and **1** in `docs/notes/working-notes.md` — that single hit being
`working-notes.md:9554`, which is the range expression "preregistered hypothesis ID (H1-H15)", not a
substantive mention. The execution plan again contradicts the deferral,
`execution-plan.md:688-690`:

> 2. **H15 (cross-model voting)**: Novel contribution
>    - 6-pass voting: 6×Flash vs 6×Sonnet vs 6×GPT vs 2×each
>    - ~$15-25

Same resolution as for H14: the preregistration governs.

**A search hazard to record in the methods.** A text search for "H15 confirmatory" in the
preregistration's changelog hits `preregistration.md:2403` — "H15 implementation status updated to
confirmatory" (v3.6) and "H15 promoted to confirmatory with Pure/Canonical/A-D library conditions"
(v3.5). Both refer to the **old** H15, the few-shot library hypothesis, which under v4.0+ numbering
is **H8**. Do not let those lines contaminate the reconciliation.

### 3.5 Draft disclosure text

> H15 (cross-model consensus voting) was registered as a Tier C exploratory hypothesis, explicitly
> deferred to future work at registration, and conditioned on H14 — which was itself deferred, so
> H15's registered precondition was never satisfied. It was not executed: every consensus pool we
> report draws all of its passes from a single model. Where we do combine models we do so across
> pipeline *stages* — a Gemini 3.1 Pro or Gemini 3.5 Flash verifier applied to a Gemini 3 Flash
> proposal pool — which tests cross-model *verification* rather than the heterogeneous-vote
> averaging H15 specifies, and which we report as such. H15 remains future work.

---

## 4. Cross-cutting notes

1. **Two different disclosure situations, and they must not be flattened.** H14 and H15 were
   *registered as deferred*, with three numbered reasons each, carried into the registered document's
   Future Directions section. H13 was *registered in scope* with a full design and was then dropped
   with no recorded decision. `docs/methods-outline.md:337` currently files all three under one
   heading, "What the Preregistration Planned but Was Not Executed", which is wrong for H14/H15 —
   the preregistration did not plan them, it deferred them. Suggest splitting into "registered and
   planned but not executed" (H13, plus H6 and H10 which are outside this brief) and "registered as
   deferred" (H14, H15).
2. **No manifest presence at all.** None of H13, H14, H15 appears in `results/analyses-manifest.json`
   (18 analyses; census in §1.2). The `preregistered` enum at
   `docs/manifest-schemas/analyses-manifest.schema.json` has no value meaning "registered, not
   executed", so the register currently cannot represent them. That is a schema decision for the PI,
   not a data question.
3. **`hypothesis-tracking.md` is stale and should not be used as an authority.** Its banner reads
   `**Last updated**: 2026-04-15` (`:5`). Its H6 row (`:18`, `Not started`) is contradicted by
   `results/analyses-manifest.json` analysis `n1-baseline-matrix-384`, whose `hypothesis_refs`
   include `H6` and whose outcome asserts a substantive H6 result. For H13/H14/H15 the staleness is
   harmless, but the document is a pointer, not a source.
4. **Nothing here required new compute or any API call.** Every claim was settled by reading
   committed artefacts, git history, and the session archives.

## 5. Open questions this walkthrough could not settle

| Question | What would settle it |
|---|---|
| Were `pv-diag-384` `pro-high-text-n5/text-t0.7` runs 1–5 dispatched as Flash or as Pro? | The billing/pricing records cited by E57 (`protocol-errata.md:1782`); the batch metas carry neither `pricing_used` nor `per_item_metadata`. |
| Do the three `verified-adv-pro-text-*-3of5` conditions draw runs 1–5 or runs 6–10? | The build provenance of the `pro-high-text-1of5` condition-set; `results/run-conditions.json` does not define that pool. |
| Was H13's first trigger clause (edge-effect errors in holdout evaluation) ever evaluated and found negative, or simply never evaluated? | No artefact in `results/` reports an edge-effect assessment, and `results/h11-tile-size-results.md` does not test it. Absent new evidence the honest statement is "never evaluated". |
| Did Shawn ever explicitly decide to drop H13? | Not found. The closest evidence is the 2026-03-11 scoping remark (§1.4), which is permissive ("at least H10-H12") rather than a deferral. |
