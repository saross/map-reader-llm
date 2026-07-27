# H6 — forensic walkthrough

**Prepared**: 2026-07-27 · **Repository HEAD at time of writing**: `38a5e598f5764c9bfe320fc9fb42019709e2d522`
(`docs(prereg): D17 per-hypothesis inventory + outline correction`) · **Working tree**: clean · **Mode**: read-only

> Every checkable specific below carries a re-verifiable anchor — a file path with line number, a
> commit hash, a memory ID, a transcript file with UTC timestamp, or a manifest key. Where I could
> not verify something, it is marked **UNVERIFIED**. Transcript evidence is volatile; each transcript
> quote is followed by a note on whether a durable artefact corroborates it.

---

## 0. The short version

The preregistered H6 — a four-factor one-factor-at-a-time (OFAT) transfer protocol on a 20-tile
stratified holdout at 512 px — **was never executed, and no one ever decided not to execute it**.
It was deferred once, in a single sentence, on 2026-03-11, in favour of a paper deadline; the
programme then pivoted to a different research agenda and Phase 4 simply never came back onto the
agenda. Six weeks later a genuinely informative but structurally different Gemini 3 Pro vs Flash
comparison was run at 384 px on 487 tiles, and acquired the label `H6-exploratory` through an
assistant-authored field in a study YAML — not through a research decision. That comparison has
since been re-run, re-scored, and corrected (erratum E57) and is a solid finding in its own right;
it is simply not H6.

**One important qualification, which improves the project's position.** On 2026-06-03 Shawn was
asked directly how to frame the Pro leaderboard against the preregistration, and he approved a
carefully-argued proposal that lists H6 in `hypothesis_refs` **while labelling the analysis
`exploratory` and expressly denying it is H6's confirmatory test** (§ 5.6). So the H6 reference that
survives in the manifests today is not an unexamined post hoc claim — it is a dated, human-approved
provenance decision. What was never approved, and never happened, is the proposition "we ran H6".

There is one further wrinkle the PI should know about: the reason now most often cited for H6's
non-execution — "budget prioritised for Flash experiments" — appears **nowhere in Shawn's own
words** and is arithmetically implausible. See § 5.3.

---

## 1. H6 as registered

### 1.1 A numbering caveat before anything else

The Flash→Pro transfer hypothesis was **numbered H8 before preregistration v4.0**, and became H6 at
the v4.0 renumbering. This matters for any archival search: a pre-January-2026 document or
transcript discussing "H6" is almost certainly discussing something else (prompt/text diversity).

- `docs/methodology/preregistration/osf/preregistration.md:2402` (v4.0 changelog): "Hypotheses
  renumbered H1-H15 (8 confirmatory, 7 exploratory) … **H6+H11 merged into exploratory H9**
  (diversity mechanisms with 5 conditions)" — i.e. old H6 was diversity, not transfer.
- `preregistration.md:2408` (v3.1 changelog) refers to "**H8 transfer approach**".
- Memory `2026-01-03-e81ebf637844` (created 2026-01-03T04:45:32.944Z): "**H8 (Flash→Pro
  transferability) uses OFAT (One-Factor-At-a-Time) approach on 20-tile stratified subset** instead
  of full factorial crossing."
- Memory `2026-01-06-626d63d35ac3` (created 2026-01-06T22:04:26.089Z) records the post-renumber
  authoritative mapping: "… H5=Hard negatives (3 levels), **H6=Flash→Pro**, H7=Temperature …".
- Transcript corroboration: cc-archive `map-reader-llm/2026-01-06T22-04_f4cb3541`, turn 394, shows
  the renumbering table row "| H8 | «H6» | Renumber |", and turn 521 records
  "1.6: **Renumbered H8 → «H6» (Transfer)**".

### 1.2 The registered specification, quoted

Source: `docs/methodology/preregistration/osf/preregistration.md`, lines 651–701. The section
carries **no `**Status**:` line** of its own (contrast H7 at line 707, "**Status**: Confirmatory
(Strand 1)"); its confirmatory status comes from
`docs/methodology/preregistration/execution-plan.md:743` — "H9 is exploratory; **H2 and H6 remain
confirmatory**".

| Anchor | Registered text (verbatim) |
| --- | --- |
| `:651` | "### H6: Optimisations Transfer from Gemini 3 Flash to Pro" |
| `:653` | "**Background**: Development and optimisation is conducted on Gemini 3 Flash for cost efficiency. For this approach to be valid, effects observed on Flash should replicate on Pro without requiring complete re-optimisation." |
| `:655` | "**Prediction**: The Flash-optimal configuration will perform well on Pro, with at most minor factor adjustments needed." |
| `:657` | "**Transfer testing approach**: Stepwise adjustment from Flash-optimal using one-factor-at-a-time (OFAT) sensitivity testing, rather than independent full optimisation." |

**Phase 1 — Baseline Comparison** (`:659–664`):

> "Run Flash-optimal configuration on Pro:
> - K=10 runs on 20 stratified holdout tiles (subset of 60, preserving density distribution)
> - Compare Pro vs Flash performance at matched configuration
> - Establish baseline for factor sensitivity testing"

**Phase 2 — OFAT Factor Sensitivity** (`:666–677`). The four factors to be varied on Pro, verbatim
from the table at `:670–675`:

| Factor | Tests | Purpose |
| ------ | ----- | ------- |
| M/E | 2 adjacent levels | Does Pro prefer more/less text? |
| H5 | 2 alternatives | Does Pro need different hard negative approach? |
| T | 2 adjacent temperatures | Does Pro prefer different temperature? |
| O | 2 alternative orderings | Does ordering effect transfer? |

**The decision rule** (`:677`, verbatim): "**Decision rule**: If alternative outperforms
Flash-optimal by ≥0.03 F1, flag factor for adjustment." Restated at
`docs/methodology/preregistration/analysis-summary.md:106` — "**Decision rule**: Adjust factor if
Δ ≥ 0.03 F1".

**Phase 3 — Voting Analysis** (`:679–683`):

> "Compute voting curves from Phase 1-2 runs (no additional API calls):
> - Compare Pro optimal threshold to Flash optimal threshold
> - Note any differences >10% relative"

**Phase 4 — Refinement (Conditional)** (`:685–689`):

> "If Phase 2 identifies factors needing adjustment:
> - Test one additional level in the indicated direction
> - For voting: if threshold differs >20%, run N=30 at Pro-adjusted config"

**Scope limitation** (`:691`): "Full per-model optimisation only if Pro demonstrates substantially
superior cost-effectiveness (≥20% higher F1 at comparable cost, OR comparable F1 at ≤50% cost)."

**The three-way transfer verdict** (`:693–699`, verbatim):

| Outcome | Interpretation |
|---------|----------------|
| All factors within 0.03 of Flash-optimal | Full transfer; report unified recommendation |
| 1-2 factors need adjustment | Partial transfer; report Flash-optimal with Pro adjustments |
| ≥3 factors need adjustment | Poor transfer; consider Pro-specific optimisation (out of scope) |

**Advance criterion** (`:701`): "**Advance to Stage 2 if**: Transfer confirmed (full or partial).
Pro-specific adjustments, if any, documented for deployment guidance."

### 1.3 Corroborating registered statements elsewhere in the prereg

- `preregistration.md:1157` (summary table): "| H6 (Flash→Pro transfer) | Effects replicate on Pro |
  OFAT sensitivity | Transfer confirmed |"
- `preregistration.md:1994` (implementation-readiness table): "| H6 | Flash→Pro transfer | ✅ Ready |
  Runtime model parameter |"
- `preregistration.md:2168`: "- **H6** (Flash→Pro transfer) — validates development approach"
- `analysis-summary.md:102–106`: "**Design**: OFAT sensitivity testing of each factor · **Analysis**:
  Compare Pro performance at Flash-optimal vs adjusted settings · **Decision rule**: Adjust factor if
  Δ ≥ 0.03 F1"

### 1.4 What the registered protocol was operationalised as

`studies/phase4-transfer.yaml` (created 2026-01-23, commit `35743ea12`) is a complete executable
skeleton: four sub-phases (4a baseline, 4b OFAT, 4c voting, 4d conditional refinement) at lines
58–99; decision thresholds at `:65–67`, `:84`, `:91`; the three-way outcome classification at
`:179–188`; a five-step `decision_rule` block at `:189–194`. Its declared inputs are
`inputs/tiles/phase4_validation_manifest.json` (`:109`) and
`inputs/vectors/bounds/phase4_validation_bounds.geojson` (`:111`); its declared analysis script is
`scripts/analyse_phase4_transfer.py` (`:120`, annotated "# To be created"); its declared budget is
1,600 API calls / **US$48 maximum** (`:159`, `:165`), corroborated by
`execution-plan.md:723` — "| Phase 4: H6 Pro Transfer | — | ~1,400-1,600 | **~$42-48** |".

---

## 2. What was actually run instead

### 2.1 No run claims H6 as its primary hypothesis

`results/runs-manifest.json` holds 31 runs. **Not one has `primary_hypothesis: "H6"`.** Two rows
touch Pro:

| `run_id` | `primary_hypothesis` | `also_informs` | corpus | tiles | `run_type` |
| --- | --- | --- | --- | --- | --- |
| `n1-pro-rerun-384` | `H11` | `["H6"]` | 4-map-gs | 384 px, `era-2-487` (487) | single-pass |
| `pv-diag-384` | `H11` | `["H3","H8","pv-strategy","consensus-n-sweep","flash-vs-pro"]` | 4-map-gs | 384 px, `era-2-487` (487) | mixed |

`n1-pro-rerun-384`'s `purpose` field reads: "Genuine-Pro re-run (E57): re-dispatch of the four
anti-diagonal Pro corners as genuine gemini-3.1-pro-preview after the n1-outstanding originals were
found to have billed as Flash. Supplies the four Pro anti-diagonal cells of the
n1-baseline-matrix-384 leaderboard." A third run, `n1-outstanding-384` (`primary_hypothesis: "H11"`),
contributed four cells that were *intended* as Pro and turned out to be Flash (E57).

### 2.2 The study YAMLs and their hypothesis fields

| Study YAML | `created` | `hypothesis:` field | line |
| --- | --- | --- | --- |
| `studies/h11-384-pro-medium-text-baseline.yaml` | 2026-03-23 | `"H11"` | `:18` |
| `studies/h11-384-pro-medium-image-baseline.yaml` | 2026-03-23 | `"H11"` | `:18` |
| `studies/h11-384-pro-high-text-n5.yaml` | 2026-03-24 | `"H6-exploratory"` | `:21` |
| `studies/h11-384-pro-high-image-n5.yaml` | 2026-03-24 | `"H6-exploratory"` | `:21` |
| `studies/h11-384-pro-high-text-n10.yaml` | 2026-03-29 | `"H6-exploratory"` | `:23` |
| `studies/h11-384-pro-medium-t07.yaml` | 2026-03-27 | `H1` | `:8` |

So the brief's premise is confirmed and sharpened: the Pro studies declare **`H11`**,
**`H6-exploratory`**, and **`H1`** — three different labels across six files, none of them a clean
`H6`. Provenance: `H6-exploratory` first entered the repository in commit `6812e8a47`
(2026-03-24, "feat(studies): add Pro pilot and consensus comparison study YAMLs"), verified by
`git log -S "H6-exploratory"`.

### 2.3 What was varied, on what corpus

All Pro work sits on the **4-map gold-standard corpus at 384 px, `era-2-487` (487 test tiles)** —
not the registered 20-tile stratified subset of the 60-tile validation set at 512 px. The registered
`inputs/tiles/validation_manifest.json` does exist and contains **60** entries; the Phase-4 20-tile
derivative does not exist (§ 3).

Factors actually crossed on Pro: **modality** (text-only vs image), **thinking level**
(MEDIUM vs HIGH), **temperature** (T=0.0 vs T=0.7). That is a 2×2×2 corner design, not the
registered OFAT ladder.

### 2.4 The conditions and the results

Eighteen `baseline-*` cells make up the N=1 single-pass leaderboard. F1 at the preregistered 20 m
buffer, from `results/conditions-manifest.json` (`.metrics.per_buffer["20"].f1`):

| `condition_id` | F1@20 m | P | R |
| --- | ---: | ---: | ---: |
| `n1-pro-rerun-384::baseline-pro-text-high-t-0-0` | **0.8045** | 0.7970 | 0.8123 |
| `pv-diag-384::baseline-pro-text-medium-t-0-0` | **0.7921** | 0.7772 | 0.8077 |
| `n1-pro-rerun-384::baseline-pro-text-medium-t-0-7` | 0.7555 | 0.7311 | 0.7816 |
| `pv-diag-384::baseline-pro-text-high-t-0-7` | 0.7450 | 0.7428 | 0.7473 |
| `n1-pro-rerun-384::baseline-pro-image-high-t-0-0` | 0.6658 | 0.5969 | 0.7525 |
| `pv-diag-384::baseline-pro-image-medium-t-0-0` | 0.6555 | 0.5837 | 0.7479 |
| `pv-diag-384::baseline-flash-image-minimal-t-0-0` | 0.5995 | 0.4745 | 0.8138 |
| `n1-outstanding-384::baseline-flash-image-minimal-t-0-0-487-tiles` | 0.5984 | 0.4736 | 0.8123 |
| `n1-pro-rerun-384::baseline-pro-image-medium-t-0-7` | 0.5950 | 0.5363 | 0.6682 |
| `pv-diag-384::baseline-pro-image-high-t-0-7` | 0.5908 | 0.5207 | 0.6828 |

The registered analysis of these cells is the leaderboard `n1-baseline-matrix-384`
(`results/run-analyses.json` and `results/analyses-manifest.json`), which is explicitly flagged
`"preregistered": "exploratory"`, `"hypothesis_refs": ["H1","H6","H7"]`,
`"deviations": ["E57"]`, `"manually_verified_at": "2026-06-04T02:05:31Z"`. Its `outcome` field
(verbatim, opening sentence):

> "At the preregistered 20 m buffer the best single pass for mound localisation is genuine Gemini 3
> Pro text at T=0.0."

Its `predicted_outcome` field frames the H6 relevance (verbatim excerpt):

> "H6 (Phase 4, the only untested confirmatory hypothesis) expected the stronger Pro model to
> transfer/match-or-exceed Flash … Board result (genuine Pro, all Pro cells n>=3): H6 holds strongly
> and uniformly -- the top six cells are all genuine Pro, every Pro-text cell beats the best Flash
> cell (flash-image-minimal-t-0-0, F1 0.600) …"

Tier structure, from `docs/methodology/n1-baseline-matrix.md:363–369`: Tier 1 = the `tie_set`,
`pro-text-high-t-0-0` (0.804) and `pro-text-medium-t-0-0` (0.792); Tier 2 = the two Pro-text T=0.7
cells; best Flash cell `flash-image-minimal-t-0-0` (0.600) sits in Tier 4. Method: round-robin
tile-swap permutation (replicate-mean per tile, 10k permutations, seed 42, two-sided) with
Benjamini–Hochberg FDR at q=0.05 and greedy-clique tiering → 7 tiers, 129/153 pairs significant
(`results/run-analyses.json`, `n1-baseline-matrix-384._note`).

### 2.5 The correction that reshaped this result (E57)

`docs/methodology/preregistration/protocol-errata.md:1782` ff. Four `n1-outstanding-384` "Pro"
cells were **dispatched and billed as Flash**, not Pro (`:1818`); a genuine-Pro re-run
(`n1-pro-rerun-384`) replaced them. The before→after table at `:1834–1839`:

| Corner | Flash (mis-dispatch) F1@20 m | Genuine Pro F1@20 m |
|---|---:|---:|
| Pro text HIGH T=0.0 | 0.494 | **0.804** |
| Pro text MEDIUM T=0.7 | 0.416 | 0.755 |
| Pro image HIGH T=0.0 | 0.528 | 0.666 |
| Pro image MEDIUM T=0.7 | 0.452 | 0.595 |

`:1844` (verbatim): "The earlier 'Flash image-MINIMAL beats weak Pro' reading was an **artefact of
the mis-dispatch** … **H6 (Pro ≥ Flash) now holds uniformly at the top** (top six cells all genuine
Pro)." Cross-referenced to working-notes Obs 336, 337, 338, 339
(`docs/notes/working-notes.md:17189`, `:17255`, `:17281`, and the Obs 339 top-up narrative), and to
commits `e1f20da4`, `59727c8a`, `c06aceee`, `1cdf9438`, `309e08de`, `c07c5776`, `28c8438a`,
`0f32ec00`, `e857c7b5` (as listed in the erratum at `:1788` and `:1849`).

### 2.6 A countervailing Pro finding the registered H6 would have had to weigh

`docs/paper/results-draft.md:195–197` (verbatim):

> "- **Proposer and verifier model upgrades.** Neither Gemini Pro 3.1 nor
>   Flash 3.5 wins any role. Pro is a genuinely better *bare* proposer but a
>   worse PV partner — its near-deterministic sampling caps pool recall."

So "Pro ≥ Flash" is true for the *single-pass proposer* role and **false** for the
proposer-verifier role. The registered H6 verdict was a single three-way classification; the
evidence that exists is role-dependent. Note also that `grep -n "H6" docs/paper/results-draft.md`
returns **no hits** — H6 is currently invisible in the draft Results.

---

## 3. The gap, itemised

Every claim in this section was re-verified at source on 2026-07-27.

| # | Registered component | Status | Evidence |
| --- | --- | --- | --- |
| 1 | 20-tile stratified validation manifest | **Not generated** | `inputs/tiles/phase4_validation_manifest.json` absent (`ls inputs/tiles/` → `calibration_manifest.json`, `full_evaluation_manifest.json`, `tile_selection_metadata.json`, `validation_manifest.json`, `verification_manifest.json`, plus four per-map dirs). The 60-tile parent exists and has 60 entries. |
| 2 | Phase-4 validation bounds | **Not generated** | `inputs/vectors/bounds/phase4_validation_bounds.geojson` absent |
| 3 | Study YAML populated with carry-forward optima | **Not done** | `studies/phase4-transfer.yaml` contains **13** literal `PLACEHOLDER` strings, at lines 28, 31, 32, 35, 38, 41, 44, 47, 48, 103, 104, 105, 106 |
| 4 | `scripts/analyse_phase4_transfer.py` | **Never written** | absent from `scripts/` |
| 5 | Any Phase-4 output | **None** | `outputs/phase4*` does not exist. Two empty archive stubs exist and contain only `.gitkeep`: `archive/results-60-tile-validation/phase4-transfer/` and `archive/outputs-pre-retest-60-tile/phase4-transfer/` |
| 5b | The 20-tile manifest in *any* git history | **Never existed** | `git log --all --oneline -- inputs/tiles/phase4_validation_manifest.json` → **0 commits**. It was not created and later removed; it was never made |
| 6 | Phase-4 row in the execution checklist | **Blank** | `docs/methodology/preregistration/execution-checklist.md:108` — `\| Phase 4: H6 Pro Transfer \| \| \| \|` (start date, end date, notes all empty; the Phase 5 row at `:109` is likewise blank) |
| 7 | OFAT factor **M/E** varied on Pro | **Partly** — text vs image only, not the registered 5-level M/E ladder | `docs/methodology/n1-baseline-matrix.md:363–369`; conditions in § 2.4 |
| 8 | OFAT factor **H5** (negative text) varied on Pro | **NO** | `grep -l "h5\|ordering" studies/h11-384-pro-*.yaml studies/h11-384-n1-outstanding.yaml` → **no matches**. `docs/methodology/preregistration/tasks/phase4-remaining-tasks.md:44` still "☐ Pending" |
| 9 | OFAT factor **T** varied on Pro | **Yes** — T=0.0 vs T=0.7 | tier table, `n1-baseline-matrix.md:363–364` |
| 10 | OFAT factor **O** (ordering) varied on Pro | **NO** | same grep as #8; `phase4-remaining-tasks.md:46` still "☐ Pending" |
| 11 | The ≥0.03 F1 per-factor decision rule | **Never computed** | no artefact in `results/` applies it; `scripts/lib_phase4_transfer.py` implements the logic but was never fed data |
| 12 | Phase 3 voting-threshold comparison (Pro vs Flash optimal threshold, >10% relative) | **Never computed** | Pro consensus cells exist (`n1-outstanding-384::pro-{text,image}-high-t0-consensus-{1,2,3}of3`) and Pro PV cells exist (`pv-diag-384::verified-adv-pro-*`), but no analysis compares Pro's optimal vote threshold to Flash's |
| 13 | Three-way transfer verdict (full / partial / poor) | **Never computed** | no artefact classifies the result under `preregistration.md:695–699` |

**Confirming the brief's claim, with one correction.** The brief cited
`docs/methodology/preregistration/tasks/phase4-remaining-tasks.md:35-38` for the un-generated
manifest. The correct anchors are **lines 34–37** (34 = validation manifest, 35 = validation bounds,
36 = YAML population, 37 = `analyse_phase4_transfer.py`); line 38 is blank. All four rows are
"☐ Pending". The document as a whole has been touched **exactly once**, at creation
(commit `3b245c689`, 2026-01-23) — it has never been updated.

**Nuance worth recording.** The Phase-4 *decision logic* was written and tested and still passes as
code: `scripts/lib_phase4_transfer.py` (baseline / factor-sensitivity / voting-threshold evaluation),
`scripts/select_tiles_phase4.py` (the 20-tile stratified selector, whose docstring at lines 3–17
names exactly the two missing input artefacts as its outputs), and three test files —
`tests/test_select_tiles_phase4.py`, `tests/test_analyse_phase4_transfer.py` (which imports
`lib_phase4_transfer`, not the never-written driver), `tests/test_integration_phase4.py`. The
scaffolding note at `phase4-remaining-tasks.md:26` records "**Total new tests**: 51". So this is not
a case of a hypothesis nobody prepared for. **Everything was built except the twenty-tile manifest,
the driver script, and the experiment.**

---

## 4. Where the record already says this

Independent of the D17 inventory, four durable artefacts in the repository already state that H6 was
not executed:

- `docs/methodology/preregistration/hypothesis-tracking.md:18` — "| H6 | Flash→Pro Transfer | Model |
  4 | **Not started** | — |"; `:168` — "### H6: Flash→Pro Transfer (Phase 4) — **NOT STARTED**";
  `:171` — "This is **the only untested confirmatory hypothesis**"; `:289` —
  "Phase 4: H6 (Flash→Pro Transfer)  ○ NOT STARTED". (This document's own header says
  "**Last updated**: 2026-04-15" — three months stale, but on H6 nothing has changed since.)
- `docs/methods-outline.md:341` — "| H6 (Flash → Pro transfer) | Not started; budget prioritised for
  Flash experiments |" (see § 5.3 for why the second clause is doubtful).
- `docs/planning/future-work.md:47` — "Non-Gemini API clients deferred until needed for H6/H14
  (Phase 4-5)."
- Erratum **E41**, `docs/methodology/preregistration/protocol-errata.md:960–972`. Verbatim, `:970`:
  "The preregistered H6 (Flash→Pro transfer, §3.6) specifies a 20-tile stratified holdout subset at
  512px tile size. Our Pro comparison uses 487 tiles at 384px — the optimal tile size identified by
  the H11 diagnostic (Obs 181)." And `:972`: "**The Pro comparison is best characterised as an
  exploratory extension rather than a strict implementation of H6.** … H6 Phase 1 (20-tile holdout at
  512px) **remains available for future execution** if a strict preregistration-compliant comparison
  is needed."
- Erratum **E40**, `protocol-errata.md:944–956`, adds a second, model-imposed obstacle:
  "Gemini 3.1 Pro requires MEDIUM thinking — deviation from §8.2/§8.9" (`:944`), and at `:956`:
  "**Pro results are not directly comparable to Flash at a matched thinking level. The comparison
  confounds model capability with thinking budget.** This is an inherent constraint of the model
  (not a design choice)."

---

## 5. The decision trail

This is the part the PI asked for. The finding is that **there is no recorded decision to abandon
Phase 4** — there is a recorded *deferral*, a programme pivot, and then silence.

### 5.1 Timeline of what is on the record

| Date | Event | Anchor | Class of evidence |
| --- | --- | --- | --- |
| 2026-01-06/07 | Transfer hypothesis renumbered **H8 → H6** | memory `2026-01-06-626d63d35ac3`; cc-archive `map-reader-llm/2026-01-06T22-04_f4cb3541` turns 394, 521 | memory (durable) + transcript |
| 2026-01-23 | Phase-4 scaffolding built | commits `35743ea12`, `3b245c689`; memory `2026-01-20-484c02f2e9c7` | commits (durable) |
| 2026-02-08 | An audit subagent's report rates H6 "| H6 (Flash→Pro) | Pending | Phase 4 | **Correctly deferred** |" | cc-archive `map-reader-llm/2026-02-08T03-52_cbeb120b` turn 592 | **agent** characterisation inside a task-notification — *not* Shawn, no durable corroboration |
| 2026-02-09 | Last ever edit to `studies/phase4-transfer.yaml` | commit `69d9fdff1`, "refactor(studies): Remove workers field from study YAML files" | commit (durable) — **mechanical, not population** |
| 2026-02-11 | Programme sequence recorded, Phase 4 still in it | memory `2026-02-11-b7b68c93bdf3`: "Phase 3 … can run in parallel; **Phase 4 (Flash→Pro transfer)**; Phase 5 (exploratory hypotheses)" | memory (durable) |
| **2026-03-11** | **The deferral** — see § 5.2 | cc-archive `map-reader-llm/2026-03-11T04-33_b21c542c` turns 44 (assistant), **49 (USER)**; memories `2026-03-11-22b4c90ac9b4`, `2026-03-11-c59a4b4a22a6`, `2026-03-11-e045555f3fff` (all created 2026-03-11T05:19:35.987348+00:00) | transcript + **durable memory corroboration of the pivot** |
| 2026-03-17 | `docs/methods-outline.md` first records H6 as not started | commit `3caae99a0`; raw transcript `08acb023-6d14-45f4-9551-f23755502868.jsonl` @ 2026-03-17T06:03:13.180Z (USER); memory `2026-03-17-beb66e3f2447` | commit + transcript + memory |
| 2026-03-23 | Shawn opens the Pro line of work as a **cost investigation**: "I'm looking for the 'budget' option to test on Gemini 3.1 Pro" (04:56:13.151Z) and "How much would it cost to run our top-performing text and image track results using the Pro batch API?" (07:49:37.054Z) | raw transcript `f1927ab0-…jsonl` lines 100, 839 (USER) | transcript — **no durable corroboration** |
| 2026-03-23 | First Pro study YAMLs written, labelled `hypothesis: "H11"` | `studies/h11-384-pro-medium-{text,image}-baseline.yaml:18–19` | file (durable) |
| **2026-03-24 01:43–02:04 UTC** | **The informed divergence** — see § 5.4 | raw transcript `f1927ab0-0805-4a87-9360-1cb7bf68cb7a.jsonl`; memories `2026-03-24-bfb38dec2337`, `2026-03-24-88d1fb197b83` (both 2026-03-24T01:48:51.082424+00:00) | transcript + **durable memory** + errata E40/E41 |
| 2026-03-24 02:55 UTC | Assistant writes `hypothesis: "H6-exploratory"` into two new study YAMLs | raw transcript `f1927ab0-…jsonl` @ 2026-03-24T02:55:41.630Z and 02:55:50.947Z; commit `6812e8a47` | transcript + commit |
| 2026-03-24 03:04 UTC | Assistant writes erratum **E41** inside a bulk documentation sweep authorised in aggregate ("yes, please work through all documentation - it's a long list, so plan first", 03:01:26.479Z USER) | raw transcript `f1927ab0-…jsonl` lines 2044, 2094; commit `f01b84a6b`, "docs(errata): E40-E41 — Pro thinking level and evaluation scope" | transcript + commit (durable) |
| 2026-03-24 06:30 UTC | Shawn asks for a to-do: "a thorough audit of all completed runs against preregistration" | raw transcript `f1927ab0-…jsonl` @ 2026-03-24T06:30:56.984Z (USER) | transcript — **no durable to-do artefact located; UNVERIFIED whether it was ever created** |
| 2026-04-11 | Shawn corrects Claude, asserting H6 **"was already completed"** | memory `2026-04-11-7a365a4725c7` | **memory only** — the session transcript is missing from both corpora (§ 6.3) |
| **2026-06-03** | **The only human ratification of the H6 linkage** — and it is explicitly `exploratory`. See § 5.6 | cc-archive `vlm-burial-mound-detection/2026-06-03T00-21_establish-expected-single-pass-baseline-and`, turns 104 (USER), 106 (assistant), **115 (USER)**, 118 | transcript + **durable manifest artefact** (`results/analyses-manifest.json`) |
| 2026-06-03 | E57 billing reconciliation flips the H6 narrative | `protocol-errata.md:1812–1851`; memories `2026-06-03-b513714eb91d`, `-44270c8ad922`, `-a8dc69e03763`, `-017a60a58c24`; Obs 336–339 | errata + memories + observations (durable) |
| 2026-07-27 | D17 inventory reaches the current finding | commit `38a5e598f`; `reports/d17-inventory/d17-inventory-h5-h8.md:259` ff. | commit (durable) |

### 5.2 The deferral, 2026-03-11 — Shawn's own words

Archive `~/cc-archives/map-reader-llm/2026-03-11T04-33_b21c542c` ("Establish research programme
status and log parallel optimisation strategies"). Shawn opened the session (turn 3) with "Hi CC,
welcome back - we just finished experiment E (I think completely, including documentation), and I
was wondering what is next in our preregistered programme."

The assistant answered at turn 44 (verbatim excerpts):

> "### Phase 4: H6 — Flash→Pro Transfer (next in sequence)
>
> This is the next preregistered step. It tests whether the Flash-optimal configuration transfers to
> Gemini Pro using OFAT sensitivity testing across 4 factors (M/E, H5, T, ordering), with a
> Δ ≥ 0.03 F1 adjustment threshold. This would require access to Gemini Pro and would cost more per
> API call."

and closed with the direct question:

> "Given that your current focus is the **LLM-History-Paper results write-up with a deadline in 2
> days**, the question is whether Phase 4 (Flash→Pro) is something you want to run before the paper
> deadline, or whether the paper will use the results you already have (Phases 2–3d). … What's your
> thinking?"

Shawn's reply, turn 49, **role = user**, verbatim opening:

> "**no, this can wait, I need to work on the LLM-History-Paper, I just wanted to get it clear in my
> mind where we are.** Please /remember that we need to optimise four parallel approaches to present
> as viable options (bearing in mind that VLMs will improve, and as they improve I think any of these
> approaches might end up being viable / superior: (1) optimal single-pass (no consensus voting)
> configuration (2) optimal consensus-voting configuration … (3) optimal image + text configuration
> … (4) optimal two-phase proposer-verifier configuration
>
> We should also undertake at least H10-H12 I think."

**This is the whole of the decision.** It is a deferral ("this can wait"), explicitly for a
competing deadline, and in the same breath it re-scopes the programme onto four architecture
comparisons plus H10–H12 plus a full-corpus production run — an agenda in which Phase 4 does not
appear.

**Durable corroboration**: three memories written at 2026-03-11T05:19:35.987348+00:00 capture the
*pivot* — `2026-03-11-22b4c90ac9b4` (the four parallel approaches, category `decision`),
`2026-03-11-c59a4b4a22a6` (the production run), `2026-03-11-e045555f3fff` (H10/H11/H12). **No
memory, no session-log entry, and no decisions-log entry captures the Phase-4 deferral itself.**
Specifically:

- `docs/notes/reflections/session-log.md` has **no entry for 2026-03-11**. It runs Session 48
  (2026-03-10, `:2590`) → Session 50 (2026-03-15, `:2675`). The only session-log mention of Phase 4
  in the whole 7,409-line file before the Pro work is a single line at `:3124`, in Session 55's
  "Pending" list: "- Phase 4 (H6 Flash→Pro transfer): not started".
- `docs/methodology/preregistration/decisions-log.md` mentions H6 **once**, at `:33`, and it is not a
  decision about Phase 4 — it is the implementation note under Decision 1 (the choice of Flash as the
  development model): "**Implementation**: H6 tests whether Flash-optimal configuration transfers to
  Pro."

The contrast that makes this a finding rather than an oversight: the project **did** have a
convention for recording an abandoned pathway, and used it two weeks later. `decisions-log.md:1010`
is "## Decision 21: Abandon Flash-Lite Transfer Pathway" (dated 2026-03-15), a full entry with
rationale, a results table, alternatives considered, implications, and evidence. **Phase 4 got no
such entry.**

### 5.3 The "budget" rationale — assistant-authored, uncorroborated, and arithmetically doubtful

`docs/methods-outline.md:341` says H6 was "Not started; **budget prioritised for Flash
experiments**". `git log -S "budget prioritised for Flash experiments"` shows this text entered in
commit `3caae99a0` (2026-03-17, "docs: draft methods section outline for publication").

That session is archived at `~/cc-archives/map-reader-llm/vlm-burial-mound-detection/2026-03-17T05-51_draft-methods-section-outline-for-vlm-burial`;
its `session.meta.json` records a 21-minute session (`started_at` 2026-03-17T05:51:01.573Z,
`ended_at` 2026-03-17T06:12:27.769Z) whose `three_ps.prompt_summary` reads: "User requested a
comparison between the original preregistration and actual experimental execution to draft a
structured methods section outline for an upcoming academic paper."

The raw transcript for that session (`08acb023-6d14-45f4-9551-f23755502868.jsonl`, 321 lines) shows
the assistant reporting at 2026-03-17T05:59:04.408Z: "**Not executed**: H6 (Pro transfer), H10
(training pool size), H12–H15 — these belong in limitations/future work". Shawn's only response
touching the topic, at 2026-03-17T06:03:13.180Z, **role = user**, verbatim:

> "**Hold off on the deferred hypotheses, I'm still running a few more, I just wanted to get started
> on the section while we wait for results.**"

He did not give a reason, and he did not say "budget". **The budget rationale appears only in the
assistant's drafted table.** Its durable corroboration is memory `2026-03-17-beb66e3f2447`
(2026-03-17T06:05:33.552000+00:00) — but note what that memory actually says: "Defer **treatment of**
non-executed hypotheses (H6, H10, H12–H15) pending completion of ongoing runs. Will address in
limitations or future work section once remaining experiments conclude." That is a decision about
*how to write about* them, not about whether to run them, and it too gives no budget reason.

**And the arithmetic does not support it.** The registered Phase 4 was costed at **US$48 maximum**
(`studies/phase4-transfer.yaml:159, :165`) / **~$42–48** (`execution-plan.md:723`) against a
confirmatory total of ~$399–405 (`execution-plan.md:724`). The Pro work that was run instead spanned
487 tiles × many passes on the more expensive model, plus a full genuine-Pro re-run of 8 passes ×
487 tiles = 3,896 calls (`protocol-errata.md:1823` and Obs 337 at
`docs/notes/working-notes.md:17257`). **Phase 4 was not skipped because it was expensive.** I would
recommend the paper not repeat that claim.

### 5.4 2026-03-24 — the informed divergence that became E40 and E41

This is the one place where the divergence from H6 was consciously surfaced to Shawn and he made a
call. Raw transcript `f1927ab0-0805-4a87-9360-1cb7bf68cb7a.jsonl`.

**Shawn**, 2026-03-24T01:43:12.672Z (verbatim): "can you look back at the preregistration, the
section on comparing Pro outputs, and see if we specified?"

**Assistant**, 01:44:13.913Z (verbatim excerpts):

> "**H6 (§3.6)**: Flash→Pro transfer test. Uses the Flash-optimal config on Pro with
> **`thinking_level=minimal`** — same as Flash. …
> **But there's a problem**: Gemini 3.1 Pro doesn't support `minimal` thinking. …
> 1. **Thinking level**: … **Running at HIGH would be a deliberate departure from H6's design.**
> 2. **The preregistration doesn't call for consensus on Pro** — H6 Phase 1 is K=10 runs on a 20-tile
>    holdout subset, with consensus computed post-hoc (Phase 3). **Our N=5 on 487 tiles is a different
>    scope.**
> 3. **512px vs 384px**: The preregistration assumed 512px … The 384px results are a post-registration
>    optimisation."

**Shawn**, 01:49:17.652Z: "isn't there anything about an exploratory or optional test with high/max
thinking if high thinking proved helpful (which it did under certain circumstances)"

**Assistant**, 01:50:15.374Z: "No — the preregistration doesn't contain any conditional or
exploratory test for HIGH/MAX thinking. … There's no 'if HIGH proves helpful, then...' clause."

**Shawn**, 02:04:07.977Z (verbatim): "**we just ran medium, which is fine - but our experiments found
that high helped during consensus voting, so we want to do that. Let's go forward with 'high'
thinking**, if it helps, we might have to at least do an N=5 text 'Max thinking' run, but let's see
the results of high first"

**Durable corroboration** — two memories written five minutes into that exchange, at
2026-03-24T01:48:51.082421+00:00 / .082424+00:00:

- `2026-03-24-bfb38dec2337` (category `methodology`): "Preregistration specified
  `thinking_level=minimal` for both Gemini Flash and Pro in H6 (§3.6, §8.2). However, Gemini 3.1 Pro
  does not support `minimal` thinking level—only `MEDIUM` and `HIGH`. Protocol deviation must be
  documented …" → became **E40** (`protocol-errata.md:944`, dated 2026-03-24).
- `2026-03-24-88d1fb197b83` (category `decision`): "H6 Phase 1 design uses K=10 runs on a 20-tile
  holdout subset with consensus computed post-hoc in Phase 3. **Current plan (N=5 on 487 tiles)
  represents a different scope than preregistered. This scope change should be explicitly noted in
  methods.**" → became **E41** (`protocol-errata.md:960`, dated 2026-03-24).

Two further human turns bracket the launch. At 2026-03-23T04:56:13.151Z Shawn framed the entire Pro
line of work as a cost question — "what's the highest x-of-5 + PV (F1)? **I'm looking for the
'budget' option to test on Gemini 3.1 Pro**" — and at 07:49:37.054Z, "while we are waiting, I think
its time to start investiganting Gemini 3.1 Pro. **How much would it cost** to run our
top-performing text and image track results using the Pro batch API?" At 2026-03-24T02:55:04.630Z he
gave the go-ahead in two words: "**approved, go**" — approving an itemised API spend, nothing about
hypothesis labelling.

**Reading**: Shawn was told, in specific terms, that what he was about to run was not H6, and he
proceeded — knowingly, with the deviations documented. That is honest practice. He framed it
throughout as a *model-cost investigation within the H11 384 px era*, never as Phase 4. What did
*not* happen is anyone saying "…and therefore H6 itself is cancelled / postponed to a named point".

**Erratum E41 was itself assistant-authored inside a bulk sweep.** Nine minutes after "approved, go",
at 2026-03-24T03:01:26.479Z, Shawn authorised a documentation pass in aggregate: "yes, please work
through all documentation - it's a long list, so plan first". The assistant wrote E41 — including
the sentence the project now leans on, "The Pro comparison is best characterised as an exploratory
extension rather than a strict implementation of H6" — at 03:04:40.484Z as one item in that sweep
(commit `f01b84a6b`, "docs(errata): E40-E41 — Pro thinking level and evaluation scope"). E41 is
therefore an accurate and creditable self-assessment, but it was **not individually discussed or
signed off**. Worth knowing if the paper cites it as a considered protocol judgement.

### 5.5 How the H6 label attached itself

Fifty-one minutes after the "let's go forward with 'high' thinking" instruction, the assistant wrote
the two new study YAMLs. Raw transcript `f1927ab0-…jsonl` @ 2026-03-24T02:55:41.630Z
(`studies/h11-384-pro-high-text-n5.yaml`) and 02:55:50.947Z
(`studies/h11-384-pro-high-image-n5.yaml`) — both `Write` tool calls whose payloads contain
`hypothesis: "H6-exploratory"`. Committed as `6812e8a47` the same day.

I found **no turn in which Shawn proposed, reviewed, or approved the `H6-exploratory` label.** It
originated as an assistant-authored YAML field written in the course of executing an instruction
about thinking level. From there it propagated: into `results/runs-manifest.json`
(`n1-pro-rerun-384.also_informs = ["H6"]`), into `results/analyses-manifest.json` and
`results/run-analyses.json` (`n1-baseline-matrix-384.hypothesis_refs = ["H1","H6","H7"]`), into
`docs/methodology/n1-baseline-matrix.md:396`, and into working-notes Obs 336/338
(`docs/notes/working-notes.md:17189`, `:17301`).

Its most consequential effect is recorded in memory `2026-04-11-7a365a4725c7`
(2026-04-11T04:27:16.417977+00:00, category `error_mode`):

> "Claude referenced incomplete/inaccurate project memory state, listing **H6 as low-priority and not
> yet started when it was already completed**; also listed production run as not started when it had
> been completed as the 55-map generalisation study. **User corrected with evidence of Pro results
> and sapphire Pro verifier analysis scripts.**"

By 2026-04-11, i.e. within three weeks, the post hoc label had become the working belief — and the
belief was Shawn's, not just the assistant's. **This memory is the single most important item in the
decision trail for the PI to see**, because it explains how a hypothesis with 13 `PLACEHOLDER`
strings in its study file came to be regarded as done.

**Corroboration status**: this memory has **no transcript backing available** — see § 6.3. It is a
durable artefact in its own right (`~/personal-assistant/memories/memories.jsonl`), but the
underlying exchange cannot currently be re-read.

### 5.6 2026-06-03 — the one place Shawn ratified the H6 reference, and the terms he ratified it on

This materially softens the "post hoc label, never approved" reading, and the PI should have it.

Archive `~/cc-archives/vlm-burial-mound-detection/2026-06-03T00-21_establish-expected-single-pass-baseline-and`
("Establish expected single-pass baseline and …"). Shawn opened the question himself at turn 104
(**role = user**, verbatim):

> "how would you approach the preregistration framing? I think these runs shed light on it, but we
> hadn't anticipated focused examination of each *architecture* of run (e.g., N-1 runs) - but
> architecture has proven to be a very important lever to pull, so the deeper dive is justified.
> Thoughts?"

The assistant's answer at turn 106 drew exactly the distinction the paper now needs (verbatim
excerpts):

> "**'The deeper dive is justified' and 'this is confirmatory' are orthogonal.** … An exploratory
> analysis can be fully rigorous, important, and worth a headline. Labelling it exploratory costs it
> nothing in weight; it just tells the reader 'we found this by looking, not by pre-committing.'"

and, on the H6 reference specifically:

> "1. **The within-board contrasts** — Pro > Flash on localisation (H6), text vs image for Pro (H1),
> low-temp > high-temp (H7). These directions *are* preregistered. The leaderboard recapitulates them
> as a **convergent line of evidence**, but it is not their confirmatory test — those live in their
> own controlled single-lever phases. This is why bare `exploratory` *undersells* it and
> `preregistered` *oversells* it."

with the concrete recommendation:

> "- `preregistered: \"exploratory\"` — the honest provenance label for *this analysis*. …
> - `hypothesis_refs: [\"H1\", \"H6\", \"H7\"]` — the contrasts the board actually examines."

Shawn's approval, turn 115 (**role = user**, verbatim in full):

> "**yes, this is perfect, thank you. Agree it should serve as a template, please document that.
> Proceed using this plan**"

**How to read this.** Shawn *did* approve H6 appearing in `hypothesis_refs` — but explicitly under an
`exploratory` provenance label, and on an argument that expressly denies the board is H6's
confirmatory test. This is the ratification the earlier YAML label never received, and it is a
defensible position. It is **not** an approval of the proposition "we ran H6". The durable output is
`results/analyses-manifest.json` / `results/run-analyses.json` (`n1-baseline-matrix-384`:
`"preregistered": "exploratory"`, `"hypothesis_refs": ["H1","H6","H7"]`), plus the argued
justification preserved at `docs/methodology/n1-baseline-matrix.md:405–411`.

**Consequence for the paper**: the honest disclosure is not "we mislabelled an experiment". It is
"the registered H6 protocol was not executed; a differently-scoped Pro-vs-Flash comparison was run
and is reported, by explicit prior decision, as exploratory convergent evidence."

---

## 6. Where the record is silent

1. **No decision to abandon.** There is no entry in `decisions-log.md` for Phase 4 — only the
   Decision-1 implementation note at `:33`. The project demonstrably had the convention (Decision 21,
   `:1010`, "Abandon Flash-Lite Transfer Pathway", 2026-03-15) and did not apply it here. **If the
   PI's question is "when did we decide not to run Phase 4?", the honest answer is: never. It was
   deferred once, on 2026-03-11, and then the agenda changed.**

2. **No session-log entry for 2026-03-11.** `docs/notes/reflections/session-log.md` skips from
   Session 48 (2026-03-10) to Session 50 (2026-03-15). The session in which the deferral happened was
   never written up. The `/reflect` ritual did not run that day, or ran and was not committed —
   **UNVERIFIED which**.

3. **No erratum records H6's non-execution.** E41 records that the *Pro comparison* is not H6. No
   erratum records that *H6 itself* was not run. That asymmetry is exactly what a reviewer checking
   the OSF record would notice.

4. **No Observation covers it.** `docs/notes/working-notes.md` (21,671 lines, 371 Observations)
   discusses H6 only in the E57/leaderboard context — Obs 336 (`:17189`), Obs 337 (`:17255`),
   Obs 338 (`:17281`), Obs 339. There is no Observation on the deferral, the substitution, or the
   labelling.

5. **`phase4-remaining-tasks.md` was never updated.** Created 2026-01-23 (`3b245c689`), one commit
   ever, still headed "**Status**: Scaffolding complete — awaiting Phase 2-3 results" (line 4). Phases
   2 and 3 completed in March; the document was never revisited.

6. **`hypothesis-tracking.md` is three months stale** (its line 5: "**Last updated**: 2026-04-15") —
   though on H6 specifically its staleness does not bite, because nothing about Phase 4 changed after
   that date.

7. **The paper currently says nothing.** `grep -n "H6" docs/paper/results-draft.md` → no hits.
   `docs/paper/results-outline.md:448–453` flags the exposure: "registered-but-unexecuted hypotheses.
   **Silence on these is the specific thing a reviewer checking the OSF record will catch.**" and,
   as corrected on 2026-07-27, "The genuinely unexecuted set is **H6, H13, H14, H15** (plus H2
   Condition C)."

### 6.1 Archive coverage gaps that limit what can still be recovered

These are properties of the evidence base, and the PI should know them before asking for more digging.

| Corpus | Coverage | Gap |
| --- | --- | --- |
| `~/cc-archives/map-reader-llm/` (74 sessions, indexed for full-text search) | 2025-12-22 → **2026-03-11** | stops the day of the deferral |
| `~/cc-archives/vlm-burial-mound-detection/` (25 sessions, indexed) | 2026-05-23 → 2026-06-12 | — |
| `~/cc-archives/map-reader-llm/vlm-burial-mound-detection/` (101 non-agent sessions, legacy nested layout) | 2025-12-22 → 2026-05-06, incl. 2026-03-17, 03-23, 03-24, 04-12, 04-13 | **present on disk but NOT in the full-text search index** — `search-sessions.py` returned no hits from this window in any query I ran |
| `/home/shawn/.claude/projects/-home-shawn-Code-map-reader-llm/` (59 raw `.jsonl`) | 2026-03-14 → 2026-07-27 | **no file covers 2026-04-03 → 2026-04-13** |

Practical consequences:

- The 2026-03-11 deferral is recoverable **only** via the indexed cc-archive (which I used).
- The 2026-03-17 and 2026-03-24 exchanges are recoverable **only** via the raw JSONL (which I used) —
  they are invisible to `search-sessions.py`.
- The **2026-04-11 "it was already completed" exchange is not recoverable from either corpus.** It
  survives as memory `2026-04-11-7a365a4725c7` alone. If the PI wants that exchange verbatim, the only
  remaining hope is `~/cc-archives/map-reader-llm/vlm-burial-mound-detection/2026-04-10T…` (a legacy
  archive that may straddle the AEDT/UTC boundary) — **UNVERIFIED; I did not decompress it**, per the
  documented instruction not to decompress `.gz` at query time.

### 6.2 Corrections — three traps in this evidence base

**(i) The prior inventory's line reference.** The brief cited `phase4-remaining-tasks.md:35-38` for
the un-generated 20-tile manifest. The correct range is **34–37**. The substance is unaffected — all
four rows read "☐ Pending".

**(ii) The 2026-02-08 "Correctly deferred" line is not Shawn.** The string
"| H6 (Flash→Pro) | Pending | Phase 4 | **Correctly deferred** |" surfaces readily in transcript
search indexed as `role = user`, in `~/cc-archives/map-reader-llm/2026-02-08T03-52_cbeb120b` turn
592. I retrieved it: it is the body of a **subagent audit report** delivered inside a
`task-notification` envelope ("Agent 'Audit preregistration completeness' completed"). It is
assistant-authored. **Do not cite it as a human judgement that the deferral was correct.**

**(iii) The 2026-04-22 "wait to phase 4" line is not about Phase 4.** A user turn at
2026-04-22T22:03:04.467Z (`8c1bb83d-9bb7-4748-8b4c-ca8442426acd.jsonl` line 341) reads "4.6 Maybe
undertake an inventory now? Or wait to phase 4? Your call". I retrieved the full turn: it is a
numbered reply to a work-plan list, and closes "I'll let you make the call about what your
re-inventory now and what you defer to setp 4" — i.e. **step 4 of that session's plan**, not
preregistered Phase 4. It is *not* evidence that Phase 4 was still live in April. I flag it because
it is the kind of hit a keyword sweep will surface and mis-read.

**(iv) Pre-v4.0 "H6" hits are about diversity, not transfer.** Per § 1.1. For example
`~/cc-archives/map-reader-llm/2025-12-31T01-34_85c5dc6e` turn 840 (USER) — "I believe that for H6 we
deferred creation of the text varients and image variants" — is about *prompt diversity* (old H6,
merged into H9 at v4.0), **not** the Flash→Pro transfer. Do not cite it as a transfer deferral.

### 6.3 One thing I could not resolve

Shawn asked on 2026-03-24T06:30:56.984Z for a to-do item "in `planning/` (we should have an active
to-do list there) that, in a new session, we should do a thorough audit of all completed runs against
preregistration". Whether that to-do was ever created, and whether the audit ever ran, is
**UNVERIFIED** — I did not locate a `planning/` artefact containing it. Given that the D17 inventory
of 2026-07-27 is arguably that audit, four months late, this may be worth a line in the collaboration
narrative.

---

## 7. Draft disclosure sentences for the paper

Pick one of the two variants; both are defensible and both are honest. Anchors are given so the
claims can be checked, but should be stripped for the manuscript.

**Variant A — three sentences, factual, minimal editorialising.**

> H6 as preregistered — a one-factor-at-a-time transfer protocol testing four factors (modality/
> elaboration, negative-text treatment, temperature, and example ordering) on Gemini 3 Pro at the
> Flash-optimal configuration, over a twenty-tile stratified holdout at 512 px, with a ≥0.03 F1
> per-factor adjustment rule and a three-way transfer verdict — was not executed. It was deferred on
> 11 March 2026 in favour of a competing writing deadline, and the research programme subsequently
> re-scoped toward architecture comparison (single-pass, consensus, proposer-verifier) and tile-size
> optimisation; no decision to cancel it was ever recorded. What was run instead was a Gemini 3 Pro
> versus Gemini 3 Flash single-pass comparison at 384 px over 487 tiles, crossing modality, thinking
> level, and temperature, which we report as an exploratory extension (erratum E41) rather than as a
> test of H6; two of the four registered factors (negative-text treatment and example ordering) were
> never varied on Pro, and neither the ≥0.03 F1 decision rule nor the transfer verdict was computed.

**Variant A+ — Variant A with the provenance decision made explicit.** Recommended if the Results
section leans on the Pro leaderboard at all, because it converts a vulnerability into a transparency
credit and is backed by a dated, human-approved decision (§ 5.6).

> H6 as preregistered — a one-factor-at-a-time transfer protocol testing four factors (modality/
> elaboration, negative-text treatment, temperature, and example ordering) on Gemini 3 Pro at the
> Flash-optimal configuration, over a twenty-tile stratified holdout at 512 px, with a ≥0.03 F1
> per-factor adjustment rule and a three-way transfer verdict — was not executed; it was deferred
> under a competing deadline in March 2026 and overtaken by a re-scoped programme, and two of its
> four registered factors were never varied on Pro. A differently-scoped Gemini 3 Pro versus Flash
> comparison (487 tiles at 384 px, crossing modality, thinking level, and temperature) was run
> instead, and is reported here — by explicit prior decision — as **exploratory convergent evidence
> rather than as a confirmatory test of H6**: the preregistered direction it recapitulates is
> genuine, but the ranked eighteen-cell board was not in the preregistered analysis plan, and
> because Gemini 3.1 Pro does not support the preregistered minimal thinking level the comparison
> confounds model capability with thinking budget (errata E40, E41).

**Variant B — two sentences, tighter, for a constrained limitations paragraph.**

> The preregistered H6 transfer protocol — four-factor OFAT sensitivity testing on Gemini 3 Pro over
> a twenty-tile stratified holdout at 512 px, adjudicated by a ≥0.03 F1 per-factor rule — was not
> executed; it was deferred in March 2026 under deadline pressure and was overtaken by a
> re-scoped programme, without a recorded decision to abandon it. The Pro-versus-Flash comparison we
> do report (487 tiles at 384 px, crossing modality, thinking level, and temperature) is an
> exploratory extension rather than an implementation of H6: it omits two of the four registered
> factors, uses a different evaluation set and tile size, and — because Gemini 3.1 Pro does not
> support the preregistered minimal thinking level — confounds model capability with thinking budget
> (errata E40, E41).

**A sentence to add if the Results section reports the Pro leaderboard as evidence bearing on H6**
(recommended, because the direction of the finding is role-dependent):

> The comparison supports the *direction* H6 predicted at the single-pass proposer stage — genuine
> Gemini 3 Pro occupies the top six cells of the 384 px baseline board and every Pro text
> configuration exceeds the best Flash configuration — but it does not resolve the registered
> question, since a model can dominate at every tested corner while still having a different optimum
> on an untested factor; and the advantage reverses in the proposer-verifier role, where Pro's
> near-deterministic sampling caps pool recall.

*Anchors for the above, for internal checking only:* deferral —
`~/cc-archives/map-reader-llm/2026-03-11T04-33_b21c542c` turn 49; non-execution —
`studies/phase4-transfer.yaml` (13 `PLACEHOLDER`), missing
`inputs/tiles/phase4_validation_manifest.json`, missing `scripts/analyse_phase4_transfer.py`,
`execution-checklist.md:108`; E41 — `protocol-errata.md:972`; E40 — `protocol-errata.md:956`;
factors not varied — no `h5`/`ordering` key in any `studies/h11-384-pro-*.yaml`; Pro leaderboard —
`docs/methodology/n1-baseline-matrix.md:363–369`; role reversal —
`docs/paper/results-draft.md:195–197`.

**What I would NOT write:** "budget prioritised for Flash experiments"
(`docs/methods-outline.md:341`). It is an assistant-authored drafting note from 2026-03-17,
uncorroborated by anything Shawn said, and contradicted by the registered cost of Phase 4 (US$48 max,
`studies/phase4-transfer.yaml:165`) against the far larger spend on the Pro work that replaced it.

---

## 8. Open questions for the PI

1. **Do you want to run it?** E41 says so itself (`protocol-errata.md:972`): "H6 Phase 1 (20-tile
   holdout at 512px) remains available for future execution." The scaffolding is intact —
   `scripts/select_tiles_phase4.py` generates the manifest and bounds in one command;
   `scripts/lib_phase4_transfer.py` already implements the baseline, factor-sensitivity, and
   voting-threshold decision logic with 51 tests behind it. What is missing is the twenty-tile
   manifest, a thin driver script, and ~1,600 API calls at a registered cost of ~US$48. **However**:
   E40 means a matched-thinking Flash/Pro comparison is no longer possible on Gemini 3.1 Pro, so even
   a re-run would be a deviation. That is a judgement call only you can make, and it is a
   phase-gate-shaped decision.

2. **Did you regard H6 as complete in April 2026?** Memory `2026-04-11-7a365a4725c7` records you
   correcting Claude on precisely this point. Do you recall the basis — was it the Pro results as a
   substitute, or a genuine belief that Phase 4 had run? Your answer determines whether the paper's
   disclosure reads as a deliberate substitution or as a labelling drift that went unnoticed.

2b. **Does the 2026-06-03 framing decision settle it for you?** You approved `exploratory` +
   `hypothesis_refs: ["H1","H6","H7"]` on an argument that explicitly separates "justified deep dive"
   from "confirmatory". If you still stand by that, the paper's disclosure is straightforward and
   Variant A+ in § 7 is ready to use. If on reflection you would rather the board not reference H6 at
   all, that is a one-line manifest change plus a note.

3. **Where should H6's non-execution be encoded?** `not-executed` is not a legal enum value in
   `docs/manifest-schemas/analyses-manifest.schema.json:48`. Options: (a) remove `"H6"` from
   `n1-baseline-matrix-384.hypothesis_refs` and record non-execution only in
   `hypothesis-tracking.md` plus the paper's limitations; (b) retain the ref with an explicit note;
   (c) extend the schema. Note that `n1-baseline-matrix-384`'s `exploratory` label was *argued*, not
   defaulted (`docs/methodology/n1-baseline-matrix.md:405–411`), so it should not be swept up in any
   bulk relabelling.

4. **Should the `H6-exploratory` string in the three study YAMLs be corrected?** It is a faithful
   record of what was written at the time (the "archive, never delete" principle argues for leaving
   it), but it is also the origin of the mislabelling. A note in the errata pointing at those three
   files would preserve both the record and the correction.

5. **Do you want the 2026-04-11 session recovered?** It is absent from both search corpora and
   survives only as a memory. Recovering it would mean decompressing a legacy `.gz` archive —
   against the documented guidance — so it needs your explicit go-ahead.

6. **Should the 2026-03-24 audit request be closed out?** You asked for a to-do to audit all completed
   runs against the preregistration "in a new session". I could not verify that a `planning/`
   artefact was ever created. The D17 inventory may be its belated fulfilment; if so, that is worth
   saying in the collaboration methods subsection.

---

## 9. Verification appendix — every claim in the brief, re-checked

| Claim in the brief | Verdict | Evidence |
| --- | --- | --- |
| `studies/phase4-transfer.yaml` contains 13 literal `PLACEHOLDER` strings | **CONFIRMED** | `grep -c PLACEHOLDER` → 13, at lines 28, 31, 32, 35, 38, 41, 44, 47, 48, 103, 104, 105, 106 |
| The 20-tile stratified validation manifest was never generated | **CONFIRMED** | `inputs/tiles/phase4_validation_manifest.json` absent; `inputs/vectors/bounds/phase4_validation_bounds.geojson` absent |
| Cited at `phase4-remaining-tasks.md:35-38` | **CORRECTED** → lines **34–37** (line 38 is blank) | `grep -n ""` on the file |
| `scripts/analyse_phase4_transfer.py` was never written | **CONFIRMED** | file absent. *But* `scripts/lib_phase4_transfer.py`, `scripts/select_tiles_phase4.py`, and three Phase-4 test files DO exist |
| No `outputs/phase4*` exists | **CONFIRMED** | `ls -d outputs/phase4*` → no such file. Two `.gitkeep`-only archive stubs exist |
| `execution-checklist.md:108` is blank | **CONFIRMED** | `\| Phase 4: H6 Pro Transfer \| \| \| \|` |
| A different Pro-vs-Flash experiment was labelled H6 post hoc | **CONFIRMED and dated** | assistant-authored `hypothesis: "H6-exploratory"` written 2026-03-24T02:55:41.630Z, committed `6812e8a47` |
| E41 at `protocol-errata.md:972` states the Pro comparison "is best characterised as an exploratory extension rather than a strict implementation of H6" | **CONFIRMED, verbatim** | line 972 |
| The decision rule is ≥0.03 F1 | **CONFIRMED** | `preregistration.md:677`; `analysis-summary.md:106`; `studies/phase4-transfer.yaml:84`, `:129` |
| Some Pro study YAMLs declare `hypothesis: "H11"` | **CONFIRMED** | `h11-384-pro-medium-{text,image}-baseline.yaml:18`. Also found: `"H6-exploratory"` ×3 and `H1` ×1 |
| Two of four OFAT factors (H5, ordering) never varied on Pro | **CONFIRMED** | no `h5` or `ordering` key in any `studies/h11-384-pro-*.yaml` or `studies/h11-384-n1-outstanding.yaml` |
| Decision rule and transfer verdict never computed | **CONFIRMED** | no artefact in `results/` applies either |
| No recorded deliberate decision to abandon Phase 4 | **CONFIRMED** | no `decisions-log.md` entry; no session-log entry for 2026-03-11; only the turn-49 deferral. Negative sweeps: "descope"/"de-scope" → no hits in either project corpus; "abandon" in relation to Phase 4 → no hits |
| *Beyond the brief:* the H6 manifest reference was human-approved on 2026-06-03, under an explicit `exploratory` label | **NEW FINDING, verified verbatim** | cc-archive `vlm-burial-mound-detection/2026-06-03T00-21_establish-expected-single-pass-baseline-and` turns 104, 106, 115, 118 |
| *Beyond the brief:* the 20-tile manifest never existed in git history | **NEW, verified** | `git log --all -- inputs/tiles/phase4_validation_manifest.json` → 0 commits |
| *Beyond the brief:* E41 was written by the assistant inside a bulk-authorised doc sweep, not individually reviewed | **NEW, verified** | raw transcript `f1927ab0-…jsonl` lines 2044 (USER, 03:01:26.479Z), 2094 (assistant Write, 03:04:40.484Z); commit `f01b84a6b` |
| *Beyond the brief:* the "budget prioritised for Flash" rationale is assistant-invented and contradicted by the registered US$48 cost | **NEW, verified** | `docs/methods-outline.md:341` via commit `3caae99a0`; `studies/phase4-transfer.yaml:159, :165`; `execution-plan.md:723`; no supporting user turn found |
