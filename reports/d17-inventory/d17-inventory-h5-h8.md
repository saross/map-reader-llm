# Preregistration inventory — H5, H6, H7, H8

**Compiled**: 2026-07-27 (read-only audit; no repository files were modified)
**Repository**: `/home/shawn/Code/map-reader-llm` @ `main`, commit `c8b679eb3`
**Purpose**: evidence base for reclassifying the `preregistered` field in
`results/analyses-manifest.json`, which currently records `"exploratory"` for all
18 registered analyses (verified: `results/analyses-manifest.json` lines 34, 94,
142, 194, 229, 261, 296, 362, 497, 560, 595, 637, 680, 725, 768, 819, 854, 893 —
every one reads `"preregistered": "exploratory"`).

## Scope note on the allowed vocabulary

`docs/manifest-schemas/analyses-manifest.schema.json:46-49` defines:

```json
"preregistered": {
  "type": ["string", "null"],
  "enum": ["preregistered", "exploratory", "preregistered-with-deviation", null],
  "description": "HUMAN-authored preregistration status."
}
```

**`not-executed` is NOT a permitted enum value.** Where this inventory proposes
"not-executed" as the substantive finding, the schema-legal encoding would have
to be either `null` (with the run simply having no analysis row) or a schema
amendment. This needs a PI decision — see § Cross-cutting discrepancies.

---

## H5 — Negative Text Treatment

### 1. As registered

**Heading**: `docs/methodology/preregistration/osf/preregistration.md:578`

> ### H5: Negative Text Treatment

**Research question** (`preregistration.md:580`):

> **Research question**: Given that hard negatives are included in the library,
> what is the optimal level of text support for negative examples?

**Test design** (`preregistration.md:586-592`) — a 3-level factor:

| Level | Condition | HN Images | Exclusion Text |
| --- | --- | --- | --- |
| A | Minimal | Yes | "Negative" label only |
| B | Terse | Yes | Brief exclusion guidance |
| C | Verbose | Yes | Detailed exclusion guidance |

**Predicted outcome** (`preregistration.md:613-618`), quoted verbatim:

> **Predictions**:
>
> 1. Adding terse exclusion text will improve precision vs minimal labels
> 2. Verbose exclusion text will show minimal additional benefit over terse (diminishing returns)
> 3. Optimal negative text level may differ from optimal positive text level (H1)
> 4. The M/E × H5 interaction will be non-significant, indicating that optimal negative text level is consistent across positive elaboration levels

**Execution parameters registered** (`preregistration.md:620-628`): M/E level =
"All image-based conditions (Image-only, Brief-text+image, Verbose-text+image)"
(line 622); library = Scale-8 or H8 optimum (line 625); temperature = H7 optimum
(line 626); ordering = canonical-first (line 627); "**K**: 10 independent runs per
condition" (line 628).

**Analysis registered** (`preregistration.md:630-636`):

> - **Primary**: Pairwise bootstrap comparisons across 3 H5 levels on precision (95% CIs, FDR-corrected; within each M/E level)
> - **Planned contrasts**: Minimal vs Terse; Terse vs Verbose
> - **Secondary**: Parallel analysis on recall to confirm no significant harm
> - **Tertiary**: Analysis on F1 to assess net benefit
> - **Cross-hypothesis (H1/H5)**: Compare optimal positive text level (H1) vs optimal negative text level (H5) — if they differ, indicates asymmetric elaboration requirements

Plus an M/E × H5 bootstrap difference-of-differences interaction test
(`preregistration.md:638-645`), and the summary-table test type
(`preregistration.md:1156`): "Bootstrap interaction test (3 M/E × 3 H5)".

`docs/methodology/preregistration/analysis-summary.md:96-100` restates:
"**Primary metric**: Precision (with recall as safety check)."

**Advance criterion** (`preregistration.md:647`):

> **Advance to Stage 2 if**: Significant H5 effect on precision (FDR-corrected p < 0.05) AND recall does not significantly decrease.

### 2. Registered status — CONFIRMATORY

H5 has no per-hypothesis `**Status**:` line (a grep for `^\*\*Status\*\*` in
`preregistration.md` returns lines 11, 453, 536, 707, 739, 843, 906, 946, 982,
1016, 1058, 1076, 1098, 1123 — none inside the H5 block, 578–648). Its
confirmatory status is established structurally and by three explicit statements:

- Section header `preregistration.md:398`: `## 5. Confirmatory Hypotheses` (H5
  sits inside this section).
- `preregistration.md:1148`: `### 7.1 Confirmatory Hypotheses (H1-H8)`, with the
  H5 row at line 1156.
- `preregistration.md:1985`: `**Confirmatory Hypotheses (H1-H8)**:`, H5 row at
  line 1993 marked "✅ Ready | Factorial factor (h5_level)".
- `preregistration.md:274`: "With 8 confirmatory hypotheses tested on 60 tiles…"

### 3. Execution — EXECUTED, but at reduced factorial scope

**Run**: `retest-phase2d` — `results/runs-manifest.json:692` is the `run_id` line;
the record reads `"primary_hypothesis": "H5"`,
`"directory_path": "outputs/retest/phase2d"`, `"tile_size_px": 512`,
`"test_set_id": "era-1-340"`, `"n_test_tiles": 340`.

**Conditions** (4, from `results/conditions-manifest.json`):

| condition_id | F1@20 m | Precision | Recall | MCC |
| --- | --- | --- | --- | --- |
| `retest-phase2d::image-terse` | 0.6052 | 0.5136 | 0.7365 | 0.2239 |
| `retest-phase2d::image-verbose` | 0.6027 | 0.5202 | 0.7161 | 0.2810 |
| `retest-phase2d::text-terse` | 0.5984 | 0.4850 | 0.7811 | 0.0000 |
| `retest-phase2d::text-verbose` | 0.5834 | 0.4887 | 0.7236 | 0.0665 |

The **H5=Minimal** cells are not in `retest-phase2d`; they are reused baselines,
per `docs/methodology/preregistration/hypothesis-tracking.md:158-161`
("Track 1 … H5=Minimal | Reuse Phase 2c"; "Track 2 … H5=Minimal | Reuse Phase 2b
T=0.0"). Those map to `retest-phase2c::image-plus-hp` (F1 0.5985, P 0.5084) and
`retest-phase2b::text-t0.0` (F1 0.6055, P 0.4872).

**Analyses** carrying `H5` in `hypothesis_refs`:

- `era1-single-pass-baseline-matrix` (`results/analyses-manifest.json:315`;
  `hypothesis_refs` at 355; `"preregistered": "exploratory"` at 362)
- `era1-leaderboard` (`results/analyses-manifest.json:402`; refs at 488;
  `"preregistered": "exploratory"` at 497)

**Earlier 60-tile pass** (superseded by E36 but still on disk):
`results/phase2d-track1-image-analysis.{md,json}` and
`results/phase2d-track2-text-analysis.{md,json}`, generated 2026-02-11, K=10,
n_tiles=60, n_bootstrap=1000.

**What was NOT executed**: the registered 3 image-based M/E × 3 H5 factorial (9
cells). Executed instead: 2 tracks (brief-text-image, brief-text) × 3 H5 levels =
6 cells, of which 4 new. Consequently the **M/E × H5 interaction test — the test
type named in `preregistration.md:1156` — was never run**, and prediction 4
is untested. The Image-only and Verbose-text+image M/E levels have no H5
variants. This is documented as E28 (see § 5).

### 4. Outcome — prediction 1 CONTRADICTED

**On the registered primary metric (precision), 60-tile K=10 pass**
(recomputed from `results/phase2d-track1-image-analysis.json` and
`results/phase2d-track2-text-analysis.json`, field `precision_difference`; sign
convention is `minimal − other`):

| Track | Contrast | Δprecision | 95 % CI | FDR sig (F1) |
| --- | --- | --- | --- | --- |
| image | minimal vs terse | +0.0226 | [−0.0337, +0.0780] | no |
| image | minimal vs verbose | +0.0231 | [−0.0247, +0.0822] | no |
| image | terse vs verbose | +0.0006 | [−0.0509, +0.0564] | no |
| text | minimal vs terse | +0.0575 | [−0.0282, +0.1585] | no |
| text | minimal vs verbose | **+0.0822** | **[+0.0228, +0.1376]** | **yes** |
| text | terse vs verbose | +0.0247 | [−0.0817, +0.1207] | no |

Every contrast points the **opposite way to prediction 1**: minimal has higher
precision than terse and verbose in both tracks. The text-track minimal-vs-verbose
precision CI excludes zero.

**F1 result, 60-tile pass** (`results/phase2d-track2-text-analysis.md:21`):

> | minimal vs verbose | +0.1140 | [+0.048, +0.174] | ✓ | ✓ |

**Carry-forward statement** (`results/phase2d-carry-forward-parameters.md:45`):

> **H5 = minimal (no exclusion guidance) selected for both tracks.**

and `results/phase2d-carry-forward-parameters.md:112-113`:

> - **Exclusion guidance hurts, not helps.** Both modalities perform best with
>   no exclusion text.

**340-tile retest** (`results/retest/retest-production-summary.md:125, 134`):

> **Key finding**: No significant difference (ΔF1 = +0.003, p = 0.85). Negation
> text style has negligible effect on the image track.

> **Key finding**: No significant F1 difference (ΔF1 = +0.016, p = 0.376), though
> terse negation text achieves significantly higher recall (p = 0.001).

**Era-1 statistical tiering** (`results/paper-eval/n1/512px-14buf-mcc/tiering/tiering_20m.md`):
all four H5 cells and both minimal baselines fall in **Tier 1** (ranks 6, 7, 10,
11, 14, 20 of 36) — statistically inseparable.

**Verdict**: the registered prediction 1 is **contradicted** (direction reversed,
significant on the text track at the 60-tile K=10 pass on the registered primary
metric). Prediction 2 is trivially consistent (verbose adds nothing over terse).
Prediction 4 **fails to resolve** — the interaction was never tested.
Prediction 3 (cross-hypothesis H1 vs H5 optimum comparison) — UNVERIFIED; I found
no artefact performing this comparison. Would need a grep of
`results/**` for an H1-optimal-vs-H5-optimal contrast to settle.

### 5. Deviations

| E | Type | Relevance to H5 |
| --- | --- | --- |
| **E28** (`protocol-errata.md:643`) | **Deviation** | The core H5 deviation. Three changes: (1) terse/verbose instruction files trimmed of HN-image references because HN images were dropped after Phase 2c selected `plus-hp`; (2) "the preregistered 3×3 factorial (3 M/E levels × 3 H5 levels) is replaced by single-factor OFAT testing H5 at the carried-forward optimal M/E level per track" (line 659); (3) text-only Track 2 activated. Protocol impact assessed "Moderate. … The OFAT simplification reduces statistical power for detecting M/E × H5 interactions" (line 665). |
| E27 (`protocol-errata.md:617`) | Deviation | Dual-track carry-forward from Phase 2a; states at line 628 "Phase 2d (H5) explicitly excludes text-only M/E levels" and that Phase 2d was initially deferred for the text track. |
| E9 (`protocol-errata.md:222`) | Clarification | Centre-pointing sentence added to all detection prompts; line 216 notes it "is applied uniformly across all H5 conditions (Minimal, Terse, Verbose) to preserve factor orthogonality". |
| E16 (`protocol-errata.md:335`) | Clarification | Prompt wording shifted from cartographic naming to visual descriptions; line 349: "The changes were applied uniformly across all H5 conditions." |
| E18 (`protocol-errata.md:374`) | Clarification | Config naming: the unsuffixed config *is* the H5=Minimal variant; `_terse`/`_verbose` suffixes for the other levels (lines 383-385). |
| E14 (`protocol-errata.md:294`) | Clarification | Verbose instruction word count (779 words) exceeds the preregistered brief:verbose ratio; touches `detect_verbose-*` "and their terse/verbose exclusion variants". |
| E17 (`protocol-errata.md:355`) | Correction | Stale `passes: 5` multiplier in `studies/phase2d-h5-negtext.yaml` among others (file list at line 361). |
| E25 (`protocol-errata.md:543`) | Correction | Text-only conditions were receiving example images; fixed via `include_example_images`. Affects the Track 2 (text) H5 cells' prompt content. |
| E31 (`protocol-errata.md:726`) | Deviation | Deterministic-run copying; cites Phase 2d as the empirical evidence for byte-identical replicates at T=0.0 ("Session 32: terse=134, verbose=128 detections in every replicate", line 737). |
| E36 (`protocol-errata.md:878`) | Deviation | The 340-tile retest supersedes the 60-tile holdout; K reduced 10 → 1–3 for single-pass conditions. This is why `retest-phase2d` has K=1. |
| E45 / E47 / E54 | Deviation / Reversion / Clarification | Analysis-layer: micro-average permutation statistic (E45), buffer reverted to the preregistered 20 m (E47), bootstrap iteration counts (E54). |

### 6. Proposed classification — `preregistered-with-deviation`

**For**: the factor, its three levels, the direction of the planned contrasts, the
registered primary metric (precision, with recall safety check), FDR correction,
and bootstrap CIs were all executed as registered. Every departure is
errata-documented (E28 above all) and dated *before* results were seen for the
levels concerned. The paper draft itself asserts the point:
`docs/paper/results-draft.md:88-89` — "each hypothesis was tested as registered".

**Against**: the registered *test type* in the summary table
(`preregistration.md:1156`) is "Bootstrap interaction test (3 M/E × 3 H5)", and
that test was **never run**. One could argue that what was run is a different,
simpler test — a single-factor OFAT — and so should be `exploratory` for the
interaction limb. The conservative reading is that the **H5 main effect** is
`preregistered-with-deviation` and the **M/E × H5 interaction** is `not-executed`.

Because the analyses manifest has no row dedicated to H5 (H5 rides on two
multi-hypothesis leaderboards), the practical recommendation is: mark
`era1-single-pass-baseline-matrix` and `era1-leaderboard` as
`preregistered-with-deviation`, add `E28`, `E27`, `E36` to their `deviations`
arrays (currently `[]` for both — `results/analyses-manifest.json`), and state in
the paper that the interaction limb was not executed.

### 7. Source discrepancies

- `hypothesis-tracking.md:17` records H5 "Complete | 2026-02-12" — **correct** for
  the 60-tile K=10 pass, but predates the 340-tile retest (E36) and so understates
  what exists. `hypothesis-tracking.md:163-164` is honest about the design change:
  "**Preregistered design was**: 3×3 factorial … Simplified to single-factor OFAT
  at carried-forward M/E per Decision 17."
- `analyses-manifest.json` says `exploratory`. I believe the preregistration +
  E28, not the manifest: the manifest field is demonstrably a blanket default (all
  18 rows identical) and the errata record shows a deliberately-tracked deviation
  from a live preregistration.
- `docs/methods-outline.md:337-345` lists H10 and H12 as not executed; both were
  executed under E51/E52. That table is stale in the same family as
  `hypothesis-tracking.md`; treat neither as authority.

### 8. Where reported

`docs/paper/results-draft.md:85` § R2 "Single-pass baselines: a broad statistical
tie at modest performance". H5 is named at line 88 (in the list "H1, H4, H5, H7,
H8") and line 102 ("negative-text treatment (H5)"). There is **no dedicated H5
subsection**; the draft explicitly compresses the single-factor hypotheses into a
board-led narrative (lines 87-93) and sends the per-hypothesis tables to
supplementary material.

---

## H6 — Optimisations Transfer from Gemini 3 Flash to Pro

> **This is the contested case. Short answer: the preregistered H6 protocol was
> never executed. A materially different Pro-vs-Flash comparison was executed and
> is reported under `n1-baseline-matrix-384`. Both `hypothesis-tracking.md`
> ("Not started") and the manifest (`hypothesis_refs` including H6) are
> defensible statements about different things.**

### 1. As registered

**Heading**: `preregistration.md:651`

> ### H6: Optimisations Transfer from Gemini 3 Flash to Pro

**Predicted outcome** (`preregistration.md:655`), verbatim:

> **Prediction**: The Flash-optimal configuration will perform well on Pro, with at most minor factor adjustments needed.

**Registered protocol** — four phases:

- **Phase 1 Baseline Comparison** (`preregistration.md:659-664`): "Run
  Flash-optimal configuration on Pro: - K=10 runs on 20 stratified holdout tiles
  (subset of 60, preserving density distribution)".
- **Phase 2 OFAT Factor Sensitivity** (`preregistration.md:666-677`): a 4-factor
  table — M/E (2 adjacent levels), **H5 (2 alternatives)**, T (2 adjacent
  temperatures), **O (2 alternative orderings)** — with the decision rule "If
  alternative outperforms Flash-optimal by ≥0.03 F1, flag factor for adjustment."
- **Phase 3 Voting Analysis** (`preregistration.md:679-683`): compare Pro optimal
  vote threshold to Flash's; note differences >10 % relative.
- **Phase 4 Refinement (conditional)** (`preregistration.md:685-689`).

**Success criteria** (`preregistration.md:695-699`): all factors within 0.03 →
full transfer; 1–2 factors need adjustment → partial; ≥3 → poor transfer.

**Advance criterion** (`preregistration.md:701`): "Transfer confirmed (full or partial)."

Summary-table entry (`preregistration.md:1157`): "H6 (Flash→Pro transfer) |
Effects replicate on Pro | OFAT sensitivity | Transfer confirmed".
`analysis-summary.md:102-106` restates the ≥0.03 F1 decision rule.

### 2. Registered status — CONFIRMATORY

Same structural evidence as H5: no per-hypothesis `**Status**:` line, but H6 sits
inside `## 5. Confirmatory Hypotheses` (`preregistration.md:398`), is row 6 of
`### 7.1 Confirmatory Hypotheses (H1-H8)` (line 1157), and is row 6 of the
`**Confirmatory Hypotheses (H1-H8)**` implementation table
(`preregistration.md:1994`: "H6 | Flash→Pro transfer | ✅ Ready | Runtime model
parameter"). The execution plan is explicit:
`docs/methodology/preregistration/execution-plan.md:743` — "H9 is exploratory; H2
and H6 remain confirmatory".

### 3. Execution — resolving the tracking-vs-manifest contradiction

**Evidence that the preregistered Phase-4 protocol was NOT executed:**

1. `studies/phase4-transfer.yaml` exists but still contains **13 occurrences of
   the literal string `PLACEHOLDER`** (verified by `grep -c`); its header comment
   reads "Prerequisites: … Phase 4 validation manifest exists (20-tile stratified
   subset)".
2. The 20-tile stratified subset was never generated. `ls inputs/tiles/ | grep -i
   phase4` returns nothing; `docs/methodology/preregistration/tasks/phase4-remaining-tasks.md:35-38`
   lists "Generate Phase 4 validation manifest … ☐ Pending" and "Generate Phase 4
   validation bounds … ☐ Pending".
3. `scripts/analyse_phase4_transfer.py` — the analysis script the protocol
   requires — was never created (`phase4-remaining-tasks.md:38` "☐ Pending"; `ls
   scripts/ | grep -i phase4` returns only `lib_phase4_transfer.py` and
   `select_tiles_phase4.py`, the pre-built scaffolding).
4. No `outputs/phase4*` or `outputs/h6*` directory exists.
5. `phase4-remaining-tasks.md:44-49` shows all four OFAT alternative-level
   selections (M/E, **H5**, T, **ordering**) still "☐ Pending".
6. `docs/methodology/preregistration/execution-checklist.md:108` — the
   "Phase 4: H6 Pro Transfer" row is empty.
7. `docs/methods-outline.md:341`: "H6 (Flash → Pro transfer) | Not started; budget
   prioritised for Flash experiments".

**Evidence that a DIFFERENT Pro-vs-Flash comparison WAS executed:**

1. Analysis `n1-baseline-matrix-384` (`results/analyses-manifest.json:7`) carries
   `hypothesis_refs` `["H1","H6","H7"]` (line 29-33) and `deviations: ["E57"]`.
2. Its 18 `conditions_compared` include eight Pro cells across three runs —
   `pv-diag-384::baseline-pro-{image,text}-{high-t-0-7,medium-t-0-0}` and
   `n1-pro-rerun-384::baseline-pro-{image,text}-{high-t-0-0,medium-t-0-7}`
   (verified in `results/conditions-manifest.json`).
3. Run records: `results/runs-manifest.json:349` `"run_id": "n1-pro-rerun-384"`
   (4 conditions) and `:484` `"run_id": "pv-diag-384"` (68 conditions).
4. The study YAMLs that produced the Pro runs are labelled `hypothesis: "H11"`,
   not H6 — verified at `studies/h11-384-pro-medium-text-baseline.yaml:19`.
   The H6 linkage was made **post hoc** in the analyses manifest.

**The two claims are therefore compatible, describing different objects:**

- `hypothesis-tracking.md:18` ("H6 | … | 4 | Not started | —") and
  `hypothesis-tracking.md:168-171` ("### H6: Flash→Pro Transfer (Phase 4) — NOT
  STARTED … This is the only untested confirmatory hypothesis") are **true of the
  preregistered Phase-4 OFAT protocol**.
- `results/analyses-manifest.json:7,29-33` is **true of the Pro-vs-Flash
  comparison that was actually run** — a different experiment on a different
  evaluation set at a different tile size.

**E41 states this explicitly** (`protocol-errata.md:960-972`):

> **Description**: The preregistered H6 (Flash→Pro transfer, §3.6) specifies a
> 20-tile stratified holdout subset at 512px tile size. Our Pro comparison uses
> 487 tiles at 384px …
>
> **Protocol impact**: The Pro comparison is best characterised as an exploratory
> extension rather than a strict implementation of H6. … H6 Phase 1 (20-tile
> holdout at 512px) remains available for future execution if a strict
> preregistration-compliant comparison is needed.

**Which of the four registered OFAT factors were varied on Pro?**

| Registered factor | Varied on Pro? | Evidence |
| --- | --- | --- |
| M/E (2 adjacent levels) | Partly — text vs image only, not the 5-level M/E ladder | `n1-baseline-matrix.md:26` "modality — text …, image …" |
| **H5 (2 alternatives)** | **No** | No Pro condition varies `h5_level`; `phase4-remaining-tasks.md:47` still pending |
| T (2 adjacent temperatures) | Yes — T=0.0 vs T=0.7 | tiering table, `n1-baseline-matrix.md:363-364` |
| **O (2 alternative orderings)** | **No** | `phase4-remaining-tasks.md:48` still pending |

Thinking level (minimal/medium/high) was varied instead — a factor **not** in the
registered OFAT set, forced by E40 (see § 5). The ≥0.03 F1 per-factor decision
rule and the three-way success-criteria classification were **not applied**; no
artefact I found computes them.

**Phase 3 (voting analysis on Pro)**: partially available but not analysed as H6.
Pro consensus and Pro proposer-verifier conditions exist —
`n1-outstanding-384::pro-{text,image}-high-t0-consensus-{1,2,3}of3` and
`pv-diag-384::verified-adv-pro-*` (verified in `results/conditions-manifest.json`)
— but no analysis compares Pro's optimal vote threshold to Flash's per
`preregistration.md:679-683`.

### 4. Outcome

The manifest's own `outcome` field (`results/analyses-manifest.json`,
`n1-baseline-matrix-384`) states:

> At the preregistered 20 m buffer the best single pass for mound localisation is
> genuine Gemini 3 Pro text at T=0.0. Tier 1 — the tie_set — is a two-member
> statistical tie between pro-text-high-t-0-0 (F1 0.804) and pro-text-medium-t-0-0
> (F1 0.792) … The top four cells are all Pro text and the top six all genuine Pro
> … (All eight Pro cells are genuine Gemini 3 Pro at n>=3; see deviations E57 and
> docs/methodology/n1-baseline-matrix.md for board provenance.)

`docs/methodology/n1-baseline-matrix.md:396-401`:

> - **H6 (Pro vs Flash) holds at the top and uniformly.** The top six cells are all
>   genuine Pro; every Pro-text cell beats the best Flash cell
>   (`flash-image-minimal-t-0-0`, F1 0.600), and the genuine Pro-image cells match
>   Flash on F1 while dominating MCC.

Tier structure (`docs/methodology/n1-baseline-matrix.md:363-369`): Tier 1
`pro-text-high-t-0-0` 0.804 / `pro-text-medium-t-0-0` 0.792; Tier 2 the two
Pro-text T=0.7 cells; best Flash cell `flash-image-minimal-t-0-0` at 0.600 in
Tier 4.

**Relation to the registered prediction**: the registered prediction was about
*transfer of optimisations* — that the Flash-optimal configuration would carry
over to Pro with at most minor factor adjustments, assessed by a ≥0.03 F1 OFAT
rule. What was measured instead is *which model is better at a shared set of
corners*. Pro ≥ Flash at every corner is **consistent with, but does not test,**
the registered claim: a model can outperform at every tested corner while still
having a different optimum on an untested factor (H5, ordering). So the result
**fails to resolve** the registered prediction, while being weakly supportive.

There is also a **countervailing Pro finding elsewhere in the corpus** that H6 as
registered would have had to weigh: `docs/paper/results-draft.md:195-197` —

> - **Proposer and verifier model upgrades.** Neither Gemini Pro 3.1 nor
>   Flash 3.5 wins any role. Pro is a genuinely better *bare* proposer but a
>   worse PV partner — its near-deterministic sampling caps pool recall.

### 5. Deviations

| E | Type | Relevance to H6 |
| --- | --- | --- |
| **E40** (`protocol-errata.md:944`) | **Deviation** | "Gemini 3.1 Pro requires MEDIUM thinking — deviation from §8.2/§8.9". The preregistration specifies `thinking_level=minimal` for both models; 3.1 Pro's floor is MEDIUM, and MINIMAL causes silent batch failures. Impact (line 956): "Pro results are not directly comparable to Flash at a matched thinking level. The comparison confounds model capability with thinking budget." |
| **E41** (`protocol-errata.md:960`) | **Deviation** | 384 px / 487 tiles instead of the registered 512 px / 20-tile stratified holdout. Explicitly reclassifies the Pro comparison as "an exploratory extension rather than a strict implementation of H6" (line 972). |
| E42 (`protocol-errata.md:976`) | Correction | `configuration.model` in `meta.json` reports the config default, not the resolved model — the metadata bug that made Pro provenance hard to establish. Lists the four confirmed genuine-Pro proposer runs at lines 1006-1009. |
| **E57** (`protocol-errata.md:1782`) | **Metadata correction + billing reconciliation (finding-affecting)** | The only errata entry named in `n1-baseline-matrix-384`'s `deviations`. Four `n1-outstanding-384` "Pro" cells were **dispatched and billed as Flash** (line 1818); a genuine-Pro re-run (`n1-pro-rerun-384`) replaced them. Line 1844: "H6 (Pro ≥ Flash) now holds uniformly at the top (top six cells all genuine Pro)." Before→after table at lines 1834-1839 (e.g. Pro text HIGH T=0.0: 0.494 → **0.804**). |
| E36 (`protocol-errata.md:878`) | Deviation | 60-tile holdout replaced by larger corpora — the general precondition for E41's 487-tile scope. |
| E45 / E47 | Deviation / Reversion | Micro-average permutation statistic; 20 m buffer restored. Both govern how the n1 board is tiered. |
| Decision 21 (`decisions-log.md:1010`) | Decision | "Abandon Flash-Lite Transfer Pathway" — a *different* transfer question (Flash → Flash-Lite), abandoned after a capability-gate failure (F1 0.097–0.126). Not H6, but adjacent, and worth a line in any transfer discussion. |

### 6. Proposed classification — `not-executed` for H6 as registered; `exploratory` for the analysis that exists

**Justification.** The registered H6 is a *protocol*, not a comparison: a 20-tile
stratified holdout, four named OFAT factors, a ≥0.03 F1 decision rule, a voting-
threshold comparison, and a three-way transfer verdict. None of the five was
delivered. Two of the four OFAT factors (H5, ordering) were never varied on Pro
at all. The evaluation set, tile size, and thinking level all differ, the last of
these by model constraint (E40) in a way that **confounds the comparison** by the
errata's own admission.

Conversely, the analysis that exists (`n1-baseline-matrix-384`) is correctly
`exploratory` and was **argued** there, not defaulted —
`docs/methodology/n1-baseline-matrix.md:405-411`:

> It is framed **`exploratory`** (`hypothesis_refs` H1 / H6 / H7): the within-board
> contrasts recapitulate preregistered directions as convergent evidence, but the
> 18-cell ranked board was not itself in the preregistered analysis plan — it
> operationalises the **single-pass baseline arm** …

**Arguing the other side.** A defender of `preregistered-with-deviation` would
say: H6's *scientific* question is "does Pro do at least as well as Flash under
Flash-tuned settings?", the answer is a clean and statistically resolved yes at
every corner tested, and E41 documents the scope change in advance of the
finding. That reading is not unreasonable — but it requires accepting a
substitution of a two-level model contrast for a four-factor OFAT sensitivity
protocol, on a different test set, at a confounded thinking level. **I do not
recommend it.** The honest disposition is: H6 as registered is not-executed;
report the Pro comparison as an exploratory extension (which is what E41 already
says); state the non-execution explicitly in the paper.

**Schema note**: `not-executed` is not a legal enum value
(`docs/manifest-schemas/analyses-manifest.schema.json:48`). Since no analysis row
claims to *be* H6, the cleanest encoding is to **remove `H6` from
`n1-baseline-matrix-384`'s `hypothesis_refs`** (or retain it with the `exploratory`
label and an explicit note), and record H6's non-execution in
`hypothesis-tracking.md` and the paper's limitations rather than in the analyses
manifest. That is a PI call.

### 7. Source discrepancies

- **`hypothesis-tracking.md:18, 168-171` vs `analyses-manifest.json:7,29-33`** —
  resolved above: not a contradiction but two true statements about different
  objects. **I believe `hypothesis-tracking.md` on the question "was the
  preregistered H6 executed?" (no) and the manifest on the question "is there Pro
  data bearing on H6?" (yes).** The decisive independent evidence is the state of
  `studies/phase4-transfer.yaml` (13 PLACEHOLDERs), the missing Phase-4 validation
  manifest, and E41's own "best characterised as an exploratory extension".
- `hypothesis-tracking.md` is stale (2026-04-15, per its line 5) — but on H6 its
  staleness does **not** bite: nothing about Phase 4 changed after that date; only
  the H11/n1 Pro work accumulated, and that was never Phase 4.
- `docs/paper/results-outline.md:448` lists H6 among "registered-but-not-executed
  hypotheses (H6, H10, H13 per the tracking matrix)" and warns: "Silence on these
  is the specific thing a reviewer checking the OSF record will catch." Note that
  H10 and H12 in that same list *were* subsequently executed (E51/E52), so the
  outline is stale on those; on H6 it agrees with my finding.

### 8. Where reported

**Not currently reported.** `grep -n "H6" docs/paper/results-draft.md` returns
nothing. Pro appears only in § R5 "Verifier robustness"
(`docs/paper/results-draft.md:190-207`), where the framing is cost-effectiveness
of model roles, not transfer. The `n1-baseline-matrix-384` board itself feeds § R2
implicitly via the single-pass baseline narrative but the Pro cells are not
discussed there.

---

## H7 — Temperature Affects Detection Performance

### 1. As registered

**Heading**: `preregistration.md:705`. **Status line**: `preregistration.md:707` —

> **Status**: Confirmatory (Strand 1)

**Predicted outcome** (`preregistration.md:711`), verbatim:

> **Prediction**: T=1.0 (vendor recommended) will yield optimal or near-optimal performance. Lower temperatures will degrade performance; higher temperatures may increase variance without improving mean F1.

**Test** (`preregistration.md:713-721`): five levels — 0.0, 0.3, 0.7, 1.0, 1.3.
T=0.3 was added on the strength of Humphries (2025) (`preregistration.md:723`).

**Analysis registered** (`preregistration.md:725-729`):

> - Pairwise bootstrap comparisons across 5 temperature levels (95% CIs, FDR-corrected)
> - Planned contrasts: T=1.0 vs each other level
> - Examine temperature × voting interaction via post-hoc analysis

**Escalation trigger** (`preregistration.md:731`), verbatim:

> **Temperature escalation trigger**: If T=1.3 yields higher F1 than T=1.0 (point estimate, same M/E and H5 condition), exploratory testing at T=1.6 and T=2.0 will be conducted at the optimal configuration to characterise the upper bound of the temperature-performance curve. If T=0.3 or T=0.7 improves performance (alone or in ensembles), further testing at low temperatures will be conducted at the optimal configuration to characterise the lower bound of the temperature-performance curve.

**Advance criterion** (`preregistration.md:733`): "Any temperature significantly
outperforms T=1.0, or if escalation trigger activates…"

Summary table (`preregistration.md:1158`): "H7 (temperature) | T=1.0 optimal |
Bootstrap pairwise (5 levels) | Any temperature outperforms 1.0".

### 2. Registered status — CONFIRMATORY (explicit)

`preregistration.md:707` — "**Status**: Confirmatory (Strand 1)". Corroborated at
`preregistration.md:1148/1158` and `1985/1995`.

### 3. Execution — EXECUTED IN FULL (all 5 levels, both tracks), twice

**Primary run**: `retest-phase2b` — `results/runs-manifest.json:626`,
`"primary_hypothesis": "H7"`, `directory_path: outputs/retest/phase2b`,
`tile_size_px: 512`, `test_set_id: era-1-340`, `n_test_tiles: 340`.

**Conditions** (10 single-pass temperature cells, K=3 each, from
`results/conditions-manifest.json`):

| condition_id | F1@20 m | P | R | MCC |
| --- | --- | --- | --- | --- |
| `retest-phase2b::image-t0.0` | 0.5862 | 0.4976 | 0.7130 | 0.1496 |
| `retest-phase2b::image-t0.3` | 0.5750 | 0.4881 | 0.6994 | 0.1226 |
| `retest-phase2b::image-t0.7` | 0.5366 | 0.4521 | 0.6599 | 0.1731 |
| `retest-phase2b::image-t1.0` | 0.5269 | 0.4396 | 0.6574 | 0.1815 |
| `retest-phase2b::image-t1.3` | 0.4921 | 0.4074 | 0.6215 | 0.2104 |
| `retest-phase2b::text-t0.0` | 0.6055 | 0.4872 | 0.7996 | 0.0000 |
| `retest-phase2b::text-t0.3` | 0.6065 | 0.4908 | 0.7935 | 0.0443 |
| `retest-phase2b::text-t0.7` | 0.5842 | 0.4606 | 0.7984 | 0.0000 |
| `retest-phase2b::text-t1.0` | 0.5335 | 0.4148 | 0.7483 | 0.0222 |
| `retest-phase2b::text-t1.3` | 0.5442 | 0.4252 | 0.7557 | 0.0665 |

**Analyses**: `era1-single-pass-baseline-matrix` and `era1-leaderboard` (both
list `H7` in `hypothesis_refs`), plus `n1-baseline-matrix-384` (H7 in refs,
`results/analyses-manifest.json:29-33`), which re-tests T=0.0 vs T=0.7 at 384 px
on Pro.

**Dedicated artefact**: `results/phase2b-carry-forward-parameters.md` (created
2026-04-24), which cites `results/retest/phase2b/analysis_summary.md` as primary.

**Pre-retest 60-tile K=10 pilot**: archived at
`archive/outputs-pre-retest-60-tile/phase2b/` per
`results/phase2b-carry-forward-parameters.md:11,151`; described as
"qualitatively identical … but with less statistical power" (lines 22-27).

**One registered element NOT executed**: the escalation to T=1.6 / T=2.0. See § 4.

### 4. Outcome — registered prediction CONTRADICTED (cleanly, with FDR support)

`results/phase2b-carry-forward-parameters.md:41-45` (image track):

> **FDR-significant comparisons**: 6/10. T=0.0 significantly better than T=0.7
> (ΔF1 = +0.050, p = 0.002), T=1.0 (+0.064, p = 0.001), and T=1.3 (+0.085,
> p = 0.001). … T=0.0 vs T=0.3 not significant (ΔF1 = +0.015, p = 0.30).

`results/phase2b-carry-forward-parameters.md:57-61` (text track):

> **FDR-significant comparisons**: 5/10. T=0.0 significantly better than T=1.0
> (ΔF1 = +0.093, p = 0.001) and T=1.3 (+0.057, p = 0.004). … T=0.0 vs T=0.3 not
> significant (ΔF1 = −0.002, p = 0.862, essentially tied).

`results/phase2b-carry-forward-parameters.md:65`:

> **T=0.0 (deterministic decoding) selected for both tracks.**

Era-1 tiering (`results/paper-eval/n1/512px-14buf-mcc/tiering/tiering_20m.md`)
independently corroborates: `text-t0.3` (rank 4), `text-t0.0` (6), `image-t0.0`
(17), `text-t0.7` (18) are **Tier 1**; `text-t1.3` **Tier 2**; `image-t0.7`,
`text-t1.0`, `image-t1.0` **Tier 3**; `image-t1.3` **Tier 4**.

384 px / Pro replication (`results/analyses-manifest.json`,
`n1-baseline-matrix-384` `outcome`):

> … and T=0.0 beats T=0.7 (Tier 1 vs Tier 2) at matched model and modality (H7).

**Verdict**: the registered prediction ("T=1.0 will yield optimal or near-optimal
performance. Lower temperatures will degrade performance") is **contradicted in
both limbs** and with FDR-corrected significance. T=1.0 is significantly *worse*
than T=0.0 on both tracks; lower temperatures *improved* rather than degraded
performance. This is one of the study's cleanest confirmatory results and its
main practitioner claim — `results/retest/retest-production-summary.md:306-308`
§ 14.2 "Practitioner message — change the Gemini API default".

**Escalation-trigger anomaly (flagged for PI judgement).** The trigger reads "If
T=1.3 yields higher F1 than T=1.0 (point estimate, same M/E and H5 condition)".
On the **text track** that condition is met: T=1.3 F1 = 0.5442 > T=1.0 F1 = 0.5335
(verified twice — `results/conditions-manifest.json` and
`results/phase2b-carry-forward-parameters.md:54-55`). Yet **no T=1.6 or T=2.0 runs
exist anywhere** (`find outputs -type d -name "*1.6*" -o -name "*2.0*"` returns
nothing; grep for "T=1.6"/"T=2.0" across `docs/methodology` and `results/` returns
only the preregistration itself at line 731 and its restatement at
`analysis-summary.md:112`). On the image track the trigger does *not* fire
(T=1.3 0.4921 < T=1.0 0.5269), so a reading of "the optimal configuration" as the
image track would leave the trigger unfired — but that reading is not the one the
text of the trigger supports ("same M/E and H5 condition"). **There is no errata
entry covering this.** Recommend either an errata entry or an explicit sentence in
the paper.

### 5. Deviations

| E | Type | Relevance to H7 |
| --- | --- | --- |
| E27 (`protocol-errata.md:617`) | Deviation | Dual-track carry-forward: adds ~5 cells to Phase 2b (line 639) — i.e. H7 was tested twice over, once per track, rather than once at a single optimal M/E. This is a *scope expansion*, not a contraction. |
| E36 (`protocol-errata.md:878`) | Deviation | 340-tile retest supersedes the 60-tile holdout; K reduced 10 → 3 for Phase 2b (`results/phase2b-carry-forward-parameters.md:15-18`). |
| E31 (`protocol-errata.md:726`) | Deviation | Deterministic-run copying at T=0.0 (Phase 2e; empirically grounded in Phase 2d). Relevant because T=0.0 near-determinism is what makes K=3 defensible. |
| E32 (`protocol-errata.md:747`) | Deviation | "Phase 3a uses T=0.3/T=0.7 instead of carry-forward T=0.0" — consensus voting requires run-to-run variation, so the H7 optimum was deliberately *not* carried into Phase 3a. |
| **E43** (`protocol-errata.md:1039`) | **Deviation** | `consensus-384` executed at T=1.0 instead of T=0.7 (30 runs × 487 tiles) — a config-propagation failure. `results/phase2b-carry-forward-parameters.md:117-141` is explicit that the paper must distinguish "T=1.0 as a preregistered test condition" from "T=1.0 as an accidental deployment (E43)". |
| **E44** (`protocol-errata.md:1070`) | **Deviation** | `single-pass-384` executed at T=1.0 instead of T=0.0 (10 runs × 240 tiles); archived to `archive/h11-unintended-t1.0/`, "Not used in any published analysis". |
| E49 / E51 / E52 | Deviation | Library-axis re-runs use the *production* carry-forward T=0.7, not the H7 optimum T=0.0 (`protocol-errata.md:1385`, `1526`). Not a deviation from H7 itself, but it means downstream phases do not honour H7's carry-forward. |
| E45 / E47 / E54 | Deviation / Reversion / Clarification | Analysis-layer, as above. |
| **No erratum** | — | The un-executed T=1.6 / T=2.0 escalation (see § 4). |

### 6. Proposed classification — `preregistered` (or `preregistered-with-deviation` if the escalation gap is counted)

**For `preregistered`**: all five registered levels were run; the registered
analysis (pairwise bootstrap, 95 % CIs, BH-FDR at q=0.05, planned contrasts T=1.0
vs each other level) was performed as specified; the result is reported against
the registered prediction and contradicts it. The deviations that apply (E27,
E36) both *increase* power and coverage relative to the registration; E31/E32/
E43/E44 concern adjacent phases rather than the H7 test itself.

**For `preregistered-with-deviation`**: (a) K was reduced from the registered 10
to 3 under E36; (b) the registered escalation trigger fired on the text track and
was not honoured; (c) H7's registered carry-forward (T=0.0 into subsequent
phases) was later abandoned in favour of T=0.7 under E49/E51/E52.

**My recommendation**: `preregistered-with-deviation`, citing E36 (K and corpus
change) and noting the un-executed escalation. The scientific claim is
unambiguously confirmatory-grade; the label just needs to carry the errata. If
the PI prefers to treat E36 as a power-increasing amendment rather than a
deviation, `preregistered` is defensible — but the escalation gap should then be
errata'd first.

### 7. Source discrepancies

- `hypothesis-tracking.md:19` and `:182-198` record H7 "Complete | 2026-02-08"
  with "T=0.0 optimal for both tracks. FDR-significant pairwise differences: 6/10
  (Track 1), 4/10 (Track 2)". The retest gives **6/10 and 5/10**
  (`results/phase2b-carry-forward-parameters.md:41,57`). The tracking matrix is
  reporting the archived 60-tile pilot; the retest is the current authority
  (`results/phase2b-carry-forward-parameters.md:22-27` says so explicitly). **I
  believe the retest.**
- `analyses-manifest.json` says `exploratory` for all three analyses touching H7.
  I believe the preregistration: `preregistration.md:707` is an explicit
  "Confirmatory (Strand 1)" declaration.
- `results/retest/retest-production-summary.md:320` § 14.5 contains a drafting
  error — it describes the retest as using "Gemini 2.0 Flash", which is corrected
  in that same document's own caveat 3 (line 279: "this retest used
  **`gemini-3-flash`** … The earlier claim that this retest used
  `gemini-2.0-flash` was an unsourced prose error"). Do not cite § 14.5's suggested
  paper text verbatim.

### 8. Where reported

`docs/paper/results-draft.md:85` § R2, named at lines 88 and 103 ("temperature
(H7)"). No dedicated subsection; folded into the board-led compression. The
practitioner claim derived from H7 (change the Gemini default) is staged in
`results/retest/retest-production-summary.md:306-308` but I did **not** find it in
the current `results-draft.md` — that appears to be an unlanded paper claim worth
flagging to the PI.

---

## H8 — Library Composition and Scaling

### 1. As registered

**Heading**: `preregistration.md:737`. **Status line**: `preregistration.md:739` —

> **Status**: Confirmatory (Strand 2)

**Test** (`preregistration.md:761-771`): seven library conditions —

| ID | Condition | Canon+ | Canon− | HP | HN | Nulls | Total |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Pure Positive Canon | 4 | 0 | 0 | 0 | 3 | 7 |
| 2 | Canonical | 4 | 2 | 0 | 0 | 3 | 9 |
| 3 | +HP | 4 | 2 | 4 | 0 | 3 | 13 |
| 4 | Scale-4 | 4 | 2 | 2 | 2 | 3 | 13 |
| 5 | Scale-8 | 4 | 2 | 4 | 4 | 3 | 17 |
| 6 | Scale-16 | 4 | 2 | 8 | 8 | 3 | 25 |
| 7 | Scale-32 | 4 | 2 | 16 | 16 | 3 | 41 |

**Planned contrasts** (`preregistration.md:775-797`): C1 (Pure Positive Canon →
Canonical), C2 (Canonical → +HP), C3 (+HP → Scale-8); S1 (Scale-4 → Scale-8), S2
(Scale-8 → Scale-16), S3 (Scale-16 → Scale-32); B1 (+HP vs Scale-4).

**Predicted outcome** (`preregistration.md:799-806`), verbatim:

> **Predictions**:
>
> 1. F1 will increase from Pure Positive Canon → Canonical (Canon- helps distinguish confusable symbols)
> 2. F1 will increase from Canonical → +HP (hard positives improve recall)
> 3. F1 will increase from +HP → Scale-8 (hard negatives improve precision)
> 4. F1 will increase from Scale-4 → Scale-8, with moderate marginal gain
> 5. F1 will increase from Scale-8 → Scale-16, with smaller marginal gain
> 6. F1 increase from Scale-16 → Scale-32 will show minimal or no improvement (diminishing returns)

**Availability contingency pre-registered** (`preregistration.md:815`): "If fewer
than 16 distinct HPs or HNs are available, Scale-32 (and possibly Scale-16) will
be capped at the maximum available, maintaining 1:1 ratio."

**Analysis registered** (`preregistration.md:819-824`): pairwise bootstrap
comparisons across 7 conditions (95 % CIs, FDR-corrected); the planned contrasts;
diminishing-returns curve; cost-efficiency analysis.

**Fixed parameters** (`preregistration.md:817`): "Optimal verbosity (from H1),
optimal temperature (from H7)."

Summary table (`preregistration.md:1159`): "H8 (library composition) | Sequential
addition + diminishing returns | Bootstrap pairwise (7 levels) + contrasts |
Significant composition effect identified".

### 2. Registered status — CONFIRMATORY (explicit)

`preregistration.md:739` — "**Status**: Confirmatory (Strand 2)". Corroborated at
`preregistration.md:1148/1159` and `1985/1996`.

### 3. Execution — EXECUTED TWICE; the complete execution has NO analysis row

**Execution v1 — Phase 2c / `retest-phase2c`** (512 px, Era 1):

- Run record `results/runs-manifest.json:659` — `"primary_hypothesis": "H8"`,
  `outputs/retest/phase2c`, 512 px, `era-1-340`, 340 tiles.
- 13 conditions in `results/conditions-manifest.json`, comprising 5 image library
  cells (`image-{pure-positive-canon, canonical, plus-hp, scale-4, scale-8}`), 5
  **text** library cells (same five names, `text-` prefix), and 3 exploratory
  pure-positive-HP variants.
- **Only 5 of 7 registered levels.** Scale-16 and Scale-32 were deferred under
  E11 (see § 5). Contrasts S2 and S3 therefore not testable in v1.
- Original 60-tile K=10 analysis: `results/phase2c-track1-image-analysis.md`
  (2026-02-09), carry-forward at `results/phase2c-carry-forward-parameters.md`.
- Analyses referencing it: `era1-single-pass-baseline-matrix`
  (`results/analyses-manifest.json:315`) and `era1-leaderboard` (`:402`), both
  `"preregistered": "exploratory"`, both `deviations: []`.

**Execution v2 — `h8-v2`** (384 px, Era 3) — **the complete execution**:

- Run record `results/runs-manifest.json:558` — `"run_id": "h8-v2"`,
  `"primary_hypothesis": "H8"`, `directory_path: outputs/h8-v2`, 384 px,
  `test_set_id: era-3-327`, `n_test_tiles: 327`, `historical_aliases: ["Era 3"]`.
- **All seven registered conditions executed**, including the previously deferred
  Scale-16 and Scale-32. Verified in `results/conditions-manifest.json`: 17
  `h8-v2::` conditions = 7 greedy + 7 WBF + 3 verified.
- Greedy t=4 (primary operating point), F1@20 m from the conditions manifest:
  pure-positive-canon 0.6970, canonical 0.7071, plus-hp 0.7051, scale-4 0.7326,
  scale-8 0.7100, scale-16 0.6930, scale-32 0.7130.
- Full analysis document: `results/h8-v2/analysis_summary.md` (dated 2026-04-15).
- **Critical gap: NO analysis in `results/analyses-manifest.json` references any
  `h8-v2::` condition.** Verified programmatically: the union of all
  `conditions_compared` run prefixes across the 18 analyses is
  {`55maps-*` ×5, `flash35-pv-2x2`, `n1-outstanding-384`, `n1-pro-rerun-384`,
  `pv-diag-256`, `pv-diag-384`, `retest-h11-single-pass-384-t0`,
  `retest-phase2a…2e`, `retest-phase3a`, `retest-phase3a-high`,
  `retest-phase3a-replication`, `retest-phase3c`, `verifier-robustness`} —
  `h8-v2` is absent. Runs with no analysis row at all: `55maps-generalisation`,
  `gold-standard-v2`, `h10`, `consensus-384-t1-0`, `e47-propose-brief`,
  `proposer-verifier-384`, `proposer-verifier-512`, `h12-v2`, **`h8-v2`**,
  `verifier-t-pilot`.

### 4. Outcome — all six directional predictions unsupported; the seven-contrast test is a clean null

**v2 (the complete, all-seven-levels execution)** —
`results/h8-v2/analysis_summary.md:13-19`:

> ## Headline result — seven-contrast null
>
> All seven preregistered pairwise contrasts are **null** after
> Benjamini–Hochberg FDR correction at q = 0.05. At the primary operating point
> (greedy t=4) the seven conditions cluster in a tight 0.693–0.733 F1 band with
> fully overlapping 95 % bootstrap confidence intervals.

Contrast table (`results/h8-v2/analysis_summary.md:21-29`): C1 raw p 0.659 / BH
0.923; C2 0.932 / 0.932; C3 0.854 / 0.932; B1 0.164 / 0.834; S1 0.330 / 0.834;
S2 0.477 / 0.834; S3 0.394 / 0.834.

`results/h8-v2/analysis_summary.md:31-38`:

> Zero of seven contrasts reach significance after BH-FDR at q=0.05. … Three of
> the six directional predictions from the preregistration (§H8, prereg lines
> 799–806) point in the wrong direction within noise (C2, S1, S2); the other
> three point in the predicted direction within noise (C1, C3, S3).

`results/h8-v2/analysis_summary.md:235-240`:

> The preregistered mechanism "more hard examples → more recognition → higher
> recall" is not supported in the data: the largest library (scale-32, 41
> examples) has lower recall (0.627) than the smallest (pure-positive-canon, 7
> examples; recall 0.649).

**Cross-hypothesis closure** — independently verified from
`results/cross-hypothesis-library/permutation-t4/fdr_summary.json`:
`n_conditions: 10`, `n_pairs: 45`, `operating_point: "greedy t=4, 20 m buffer,
327-tile h10-384 test set"`, `any_significant: false`; minimum BH-adjusted
p = 0.9657 (minimum raw p = 0.043).

**v1 (Era-1)** — `results/retest/retest-production-summary.md:92`:

> **Key finding**: No significant pairwise F1 differences among any image-track
> library conditions (all p > 0.19).

and line 104 (text track): "The only significant comparison is plus-hp vs scale-4
(ΔF1 = −0.013, p = 0.001)". Era-1 tiering places every library cell in Tier 1 or
Tier 2 (`results/paper-eval/n1/512px-14buf-mcc/tiering/tiering_20m.md`, ranks 2, 3,
8, 9, 11, 12, 15, 16, 19 in Tier 1; 21, 23, 25, 26 in Tier 2).

**Verdict**: all six registered directional predictions are **unsupported**; three
point the wrong way. The registered advance criterion ("Significant main effect of
library composition") is **not met**. This is a well-powered, well-documented
null on a confirmatory hypothesis — arguably the study's most citable
preregistered negative result.

### 5. Deviations

| E | Type | Relevance to H8 |
| --- | --- | --- |
| **E11** (`protocol-errata.md:239`) | **Clarification** | "Scale-16 and Scale-32 library conditions capped". HP pool structurally exhausted at 4 recognition failures. "H8 conditions 6–7 deferred; scaling contrasts S2 and S3 deferred to post-H10" (line 246). Protocol impact assessed as **"None. This is activation of a preregistered contingency path, not a deviation"** (line 254), citing `preregistration.md:815`. |
| **E51** (`protocol-errata.md:1366`) | **Deviation** | "H8 library composition re-run under production carry-forward (384 px / v2 pipeline)". The parameter-change table (lines 1381-1395) lists 13 changed parameters: 512→384 px, stride 448→336, T=0.0→T=0.7, thinking minimal→HIGH, K 10→5, standard→flex tier, no caching→caching, crop 128→150 px, v1→v2 hard-case register, Scale-16 and Scale-32 **re-enabled**, and evaluation manifest 60 tiles @512 px → 327 tiles @384 px. Scale-8 is reused byte-identically from H10 v2 `pool_160_hp4hn4` (lines 1397-1404). |
| E48 (`protocol-errata.md:1291`) | Correction | §8.4.1's "target M=3" for HN selection is inconsistent with Scale-8's HN=4; resolved as a drafting error in favour of HN=4. Internal to the preregistration; no data impact. |
| E27 (`protocol-errata.md:617`) | Deviation | Dual-track carry-forward; line 633 states "Phase 2c skipped" for the text track. **But the 340-tile retest ran 5 text-track library cells anyway** (see § 7). |
| E36 (`protocol-errata.md:878`) | Deviation | 340-tile retest; K reduced to 1 for Phase 2c cells (`results/retest/retest-production-summary.md:281` caveat 5). |
| E49 (`protocol-errata.md:1313`) | Deviation | H10 calibration uses cold-start production config; changes which examples are mined as "hard", i.e. what fills the H8 v2 library slots. |
| E52 (`protocol-errata.md:1468`) | Deviation | H12 v2 (HP:HN ratio) re-run; explicitly relaxes H12's "run if H8 shows library size matters" trigger (lines 1498-1519) *because* H8 v2 was null. Relevant as documentation that a preregistered trigger was deliberately overridden. |
| E12 (`protocol-errata.md:258`) / E13 (`:275`) | Clarification | Downstream consequences of the same HP-pool exhaustion (H9-C runs HN-only; H12 deferred). |
| E45 / E47 / E54 | Deviation / Reversion / Clarification | Analysis-layer, as above. |

### 6. Proposed classification — `preregistered-with-deviation`

**For.** H8 v2 executed **all seven registered conditions**, ran **all seven
registered contrasts** (C1–C3, S1–S3, B1) with the registered statistical
apparatus (bootstrap CIs at 1 000 iterations seed 42, tile-level paired
permutation at 10 000 iterations, BH-FDR at q = 0.05 — see
`results/h8-v2/analysis_summary.md:349-358`), and reported the result against the
registered predictions. The deviations are enumerated in advance in E51 and are
mostly pipeline-alignment (384 px, production temperature/thinking) rather than
design changes. The pre-launch configuration audit
(`reports/configuration-audit-2026-04-15-h8-v2.md`) was run before spend.
`results/retest/retest-production-summary.md:314-316` § 14.4 makes the claim
directly: "**Library-composition null is preregistered (not exploratory)**".

**Against.** E51 changes temperature away from the H7 optimum the preregistration
mandated as a fixed parameter (`preregistration.md:817` "optimal temperature (from
H7)") and changes thinking level, tile size, evaluation set, and K. A strict
reader could say the H8 that was completed is not the H8 that was registered — it
is H8 re-asked at a different operating point. The counter is that E51 documents
exactly this and justifies it (`protocol-errata.md:1406-1429`), and that the
Era-1 v1 execution *did* use the registered T=0.0/minimal/512 px settings and
returned the same null — so the finding is robust across both parameterisations.
That robustness is the strongest single argument for `preregistered-with-deviation`
over `exploratory`.

**Blocking issue.** There is currently **no analyses-manifest row to label**. The
manifest cannot be corrected for H8's principal execution until an analysis row
for `h8-v2` is authored. This should be treated as the top action item.

### 7. Source discrepancies

1. **`hypothesis-tracking.md:20` records H8 "Complete | 2026-02-09"** and
   `:219-226` marks Scale-16 / Scale-32 "**DEFERRED**" with the note "Deferred to
   post-H10 when calibration tile expansion may yield additional recognition
   failures." **This is superseded**: E51 (2026-04-15) re-enabled and executed
   both. The tracking matrix is stale (its own header says 2026-04-15, so it was
   updated the same day E51 was written but not for this row). **I believe E51 and
   `results/h8-v2/analysis_summary.md`**, which are corroborated by seven
   `h8-v2::greedy-*` conditions on disk in `results/conditions-manifest.json`.
2. **`analyses-manifest.json` has no `h8-v2` row at all** — so H8's complete
   execution is invisible to the manifest layer that the paper's provenance story
   depends on. This is a coverage gap, not merely a mislabel. (The same gap
   affects `h10` and `h12-v2`, both outside this brief.)
3. **`docs/methods-outline.md:341-345`** lists H10 and H12 as not executed —
   stale; both ran under E49/E51/E52.
4. **E27 says the text track skipped Phase 2c** (`protocol-errata.md:633`) and
   `results/phase2c-carry-forward-parameters.md:14-20` explains why ("library
   composition is inherently visual … all library conditions collapse to
   functionally identical prompts"). **Yet the 340-tile retest ran five text-track
   library conditions** (`retest-phase2c::text-{pure-positive-canon, canonical,
   plus-hp, scale-4, scale-8}` in `results/conditions-manifest.json`), and they are
   **not** identical — F1@20 m spans 0.5969 (`text-plus-hp`) to 0.6094
   (`text-scale-4`) in `results/conditions-manifest.json` (0.5963–0.6089 in the
   pre-re-score table at `results/retest/retest-production-summary.md:98-102`), and
   one contrast is significant
   (`results/retest/retest-production-summary.md:104,244`: "scale-4 > plus-hp,
   ΔF1 = +0.013, p = 0.001"). I found **no erratum** covering this reactivation.
   Recommend an errata entry, and note that the stated rationale for skipping
   ("functionally identical prompts") is empirically falsified by the retest data.
5. **`results/h8-v2/analysis_summary.md:5` says "E51 (15 deviations)"** but the
   E51 parameter table (`protocol-errata.md:1383-1395`) has **13** rows. Minor,
   but it is a checkable number in a document the paper will cite — worth
   reconciling.

### 8. Where reported

`docs/paper/results-draft.md:85` § R2, named at lines 88 and 103
("example-library composition (H8)"). No dedicated subsection. The H8 v2
seven-contrast null and the 45-pair cross-hypothesis library closure — arguably
the strongest preregistered negative result in the study — do **not** appear in
`results-draft.md` at all (grep for "h8-v2", "library-axis", "Scale-32" in that
file returns nothing beyond line 103's passing mention). `results/h8-v2/analysis_summary.md:321-345`
§ "Paper implications" lists three concrete claims it is meant to support; none
has landed in the draft. Flag to PI.

---

## Cross-cutting discrepancies and open questions for the PI

1. **The `exploratory` label is a blanket default, with one documented exception.**
   All 18 rows read `exploratory`. But for `n1-baseline-matrix-384` the label was
   *argued*, not defaulted — `docs/methodology/n1-baseline-matrix.md:405-411`
   reasons that the 18-cell ranked board "was not itself in the preregistered
   analysis plan". Any reclassification pass must not silently overwrite that
   reasoning; the board-level framing can stay `exploratory` even while the
   underlying hypothesis tests are confirmatory.

2. **`not-executed` is not a legal schema value**
   (`docs/manifest-schemas/analyses-manifest.schema.json:48`). H6's disposition
   needs somewhere to live. Options: (a) amend the schema; (b) drop `H6` from
   `n1-baseline-matrix-384`'s `hypothesis_refs` and record non-execution in
   `hypothesis-tracking.md` + paper limitations; (c) keep the ref with
   `exploratory` and an explanatory note. PI call.

3. **H8's complete execution has no analysis row.** `h8-v2` (7/7 registered
   conditions, 7/7 registered contrasts, 327 tiles) is in the runs and conditions
   manifests but in no analysis. Same for `h10` and `h12-v2`. Until an
   `h8-v2` analysis row exists, the manifest cannot represent H8 correctly at all.

4. **The M/E × H5 interaction test — the registered test type for H5
   (`preregistration.md:1156`) — was never run.** E28 documents the simplification
   but the paper needs to say so.

5. **The H7 escalation trigger fired on the text track and was not honoured**
   (T=1.3 0.5442 > T=1.0 0.5335). No T=1.6/T=2.0 runs exist; no erratum covers it.

6. **The Phase 2c text track was skipped per E27 but subsequently run in the
   retest, with no erratum**, and the stated rationale for skipping is falsified
   by the resulting data.

7. **Three governance documents are stale in the same way**:
   `docs/methodology/preregistration/hypothesis-tracking.md` (2026-04-15),
   `docs/methods-outline.md:337-345`, and `docs/paper/results-outline.md:448`.
   All three predate or ignore E51/E52. Only on **H6** do they agree with the
   evidence; on H8/H10/H12 they are wrong.

8. **Nothing in this block is currently reported at hypothesis granularity in the
   paper.** § R2 (`docs/paper/results-draft.md:85-110`) deliberately compresses
   H1/H4/H5/H7/H8 into one board-led paragraph and defers per-hypothesis tables to
   supplementary material — a defensible editorial choice, but it means the
   supplementary tables must exist and must carry the confirmatory/exploratory
   labels this inventory is meant to fix.
