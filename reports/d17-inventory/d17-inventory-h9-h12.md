# D17 reconciliation inventory — H9, H10, H11, H12

**Prepared**: 2026-07-27. **Repo**: `/home/shawn/Code/map-reader-llm` (branch `main`, clean at
session start, HEAD `c8b679eb3`).
**Mode**: READ-ONLY. No repository files were created, edited, or committed.

**Anchoring convention**: every checkable specific below carries a file path and, where
practical, a line number, verified by direct read within this session. Where a claim could
not be verified at source it is marked `UNVERIFIED`.

**Headline for the impatient**: all four hypotheses in this block were **executed**. None is
`not-executed`. The stale `hypothesis-tracking.md` is wrong about H10 (says "Not started"; it
ran and returned a null) and about H12 (says "In progress"; it completed), and misdescribes
H9 (says the formal A–E conditions "were not run as separate experiments"; they were run
twice). H10 and H12 have full analysis summaries in `results/` but **no entry in
`results/analyses-manifest.json` and no appearance in `docs/paper/results-draft.md`** — the
single largest disclosure gap in this block.

---

## Cross-cutting context (applies to all four)

### The preregistration's own confirmatory/exploratory classification

`docs/methodology/preregistration/osf/preregistration.md:833-835`:

> ## 6. Exploratory Hypotheses
>
> *These analyses will be conducted and reported but are not confirmatory. Results will be
> interpreted cautiously and framed as hypothesis-generating. Not included in FDR correction.*

H9–H15 sit under this Section 6 heading. The classification is repeated in three further
places in the same file:

- `preregistration.md:1161-1168` — "### 7.2 Exploratory Hypotheses (H9-H15)" summary table
  with tier assignments.
- `preregistration.md:1998-2005` — "**Exploratory Hypotheses (H9-H15)**" implementation table,
  all four marked "📋 Planned".
- `preregistration.md:2170-2176` — "### Tier 4: If Resources Allow (Exploratory)", listing
  "**H9** (diversity) — refines H3; Tier A exploratory", "**H10** (training pool size) — Tier
  B exploratory", "**H11** (tile size) — Tier B exploratory", "**H12** (HP:HN ratio) — Tier B
  (conditional on H8)".

And in the companion narrative, `docs/methodology/preregistration/osf/narrative-summary.md:5`:

> Seven exploratory hypotheses (H9–H15) are also documented.

**Conclusion**: the exploratory classification for H9–H12 is confirmed at source. The
`preregistered: "exploratory"` value currently in `results/analyses-manifest.json` is
**correct** for the two analyses in this block that carry it
(`phase3c-diversity-calibration`, `tile-size-sweep`) — but it is *under-informative*, because
it does not distinguish "registered as exploratory and executed" from "post-hoc, no registered
basis". See § "Terminology problem" below.

### Terminology problem — the manifest schema has no way to say what the PI wants said

`docs/manifest-schemas/analyses-manifest.schema.json`,
`/$defs/analysis/properties/preregistered`:

```json
{"type": ["string", "null"],
 "enum": ["preregistered", "exploratory", "preregistered-with-deviation", null],
 "description": "HUMAN-authored preregistration status."}
```

The enum has **no `not-executed` member**, and no member that distinguishes
"registered-exploratory" from "post-hoc". For this block that is survivable (nothing here is
`not-executed`), but the D17 reconciliation will need either a schema amendment or a separate
hypothesis-level table. Note also that `hypothesis_refs` is documented as "Controlled
vocabulary: H1..H15 plus documented named programmes."

### Cross-cutting errata touching all four hypotheses' *reported numbers*

These are not hypothesis-specific but change the numbers under which each is reported:

| E | Type | One line |
|---|---|---|
| E36 (`protocol-errata.md:878`) | Deviation | 340-tile production retest replaces the 60-tile holdout evaluation; all Phase 2–3 conditions re-run from scratch. Directly governs H9's reported scope. |
| E45 (`protocol-errata.md:1097`) | Deviation | Pairwise permutation statistic changed macro-average → micro-average F1. Governs H10's and H12's permutation p-values. |
| E46 (`protocol-errata.md:1163`) | Deviation | Primary matching buffer 20 m → 30 m. |
| E47 (`protocol-errata.md:1236`) | Reversion (restores preregistered value) | Buffer reverted to the preregistered 20 m; supersedes E46. All four hypotheses are reported at 20 m, i.e. at the preregistered value. |
| E54 (`protocol-errata.md:1673`) | Clarification | Bootstrap 1 000 iterations for primary F1 (as preregistered); 10 000 post-hoc for narrow-effect work. |
| E56 (`protocol-errata.md:1746`) | Methodological clarification | Verifier probability-threshold operating points are test-set-selected (in-sample). Relevant to H10's PV comparison and H11's consensus+PV rows. |

---

# H9 — Diversity Mechanisms Improve Consensus Voting

## 1. As registered

**Source**: `docs/methodology/preregistration/osf/preregistration.md:841-896`.

Heading (line 841):

> ### H9: Diversity Mechanisms Improve Consensus Voting

Prediction (line 853), verbatim:

> **Prediction**: At least one diversity mechanism will improve F1 compared to fully identical
> passes.

Specified test (line 855, table at 857-863):

> **Test**: 5-condition design comparing diversity mechanisms:
>
> | Condition | Text | Images | Temperature | Description |
> | A | Fixed | Fixed | Fixed | Baseline: identical across all passes |
> | B | Varied | Fixed | Fixed | Text diversity only |
> | C | Fixed | Varied | Fixed | Image diversity only |
> | D | Fixed | Fixed | Varied | Temperature diversity only |
> | E | Varied | Varied | Varied | Full diversity |

Specified analysis (lines 888-896):

> **Analysis**:
>
> - Compare F1 across all 5 conditions
> - Test whether effects are additive (E ≈ sum of B, C, D effects) or synergistic (E > sum)
> - Examine whether mechanisms are redundant (multiple mechanisms produce similar gains)
>
> **Replication**: Each condition run 5 times to provide symmetric variance estimates.
>
> **Advance to further exploration if**: Any diversity mechanism significantly improves F1 over
> baseline.

Implementation detail also registered: text diversity = 5 semantically equivalent instruction
variants (`preregistration.md:865-871`, with the full specification at §8.3.2–8.3.3, lines
1358-1383); image diversity = frequency-capped cross-pass resampling (lines 873-878, method at
§8.4.4, line 1560); temperature diversity = a 5-pass sequence centred on the Phase 2 optimum,
`T_opt + {-0.3, -0.15, 0, +0.15, +0.3}` (lines 880-886).

The 7.2 summary table (`preregistration.md:1165`) records the analysis as "5-condition
comparison".

## 2. Registered status

**Exploratory, Tier A.** `preregistration.md:843`:

> **Status**: Exploratory (Tier A)

Corroborated at `preregistration.md:1165` ("| H9 (diversity) | A | ... |") and
`preregistration.md:2172` ("**H9** (diversity) — refines H3; Tier A exploratory"). H9 is the
*only* Tier A exploratory hypothesis — the preregistration calls Tier A "Essential
Exploratory" (`preregistration.md:837`).

## 3. Execution — what "Complete (implicit)" actually means

**It was executed explicitly, twice. The word "implicit" is wrong, not merely stale.**

`docs/methodology/preregistration/hypothesis-tracking.md:244-248` asserts:

> **Status (2026-03-07)**: Implicitly tested via Phase 3a parameter variation.
> Prompt/parameter diversity does not improve consensus — confirmed null result.
> The formal H9-A through H9-E conditions were not run as separate experiments;
> the finding emerged from Phase 3a's multi-temperature, multi-run design which
> inherently tested temperature diversity (H9-D).

That claim is contradicted by the artefacts:

**Execution 1 — 60-tile pilot (2026-03-07/08).**
`results/phase3c-diversity/phase3c-comprehensive-results-report.md:1-6` is titled "Phase 3c
Comprehensive Results Report: Diversity Testing Across Consensus Voting Passes (H9)", dated
2026-03-08. Its §1.5 execution summary records Track 1 (Image) 125 units / 60 tiles / 7,500
API calls, and Track 2 (Text-Only) 100 units / 60 tiles / 6,000 API calls — i.e. the formal
A–E conditions were run as separate experiments, 5 conditions × 5 sub-conditions × 5 runs.
Git: first committed `650fe9019` (2026-03-08, "chore: track Phase 3c diversity analysis
results"), with `f9094cbaf` (2026-03-08) adding the additivity/redundancy section "to
discharge preregistration".

**Execution 2 — 340-tile retest (Era 1).** Study YAMLs
`studies/retest/phase3c-h9-diversity-track1.yaml` and `...-track2.yaml`, first committed
`f06afb7ac` (2026-03-15). Analysis reports
`results/phase3c-diversity/track1-image/diversity-analysis-report.json` and
`.../track2-text/diversity-analysis-report.json`, generated 2026-03-25T07:28–07:29Z, both
recording `"bounds": "inputs/vectors/bounds/full_evaluation_bounds.geojson"` — verified in this
session to contain **340 features**.

**Timing point that matters**: the string "Complete (implicit)" was introduced into
`hypothesis-tracking.md` by commit `7fb1d0b47` (2026-03-15, "docs: update hypothesis tracking
to reflect current completion status") — a full week *after* the formal Phase 3c experiment
was committed. So this is a documentation error, not a description of a state that was once
true.

**IDs (all anchored):**

| Artefact | ID / path |
|---|---|
| `run_id` | `retest-phase3c` — `results/runs-manifest.json`, record has `"primary_hypothesis": "H9"`, `"directory_path": "outputs/retest/phase3c"`, `"tile_size_px": 512`, `"scope": {"test_set_id": "era-1-340", "n_test_tiles": 340}` |
| `condition_id`s (9) | `retest-phase3c::image-h9-{a,b,c,d,e}-diversity-3of5` and `retest-phase3c::text-h9-{a,b,d,e}-diversity-4of5` — `results/conditions-manifest.json` |
| `analysis_id` | `phase3c-diversity-calibration` — `results/analyses-manifest.json`, `hypothesis_refs: ["H9"]`, `output_path: results/rescore-2026-06-07/phase3c` |
| Secondary `analysis_id` | `era1-leaderboard` — `hypothesis_refs` include `"H9"` (`results/analyses-manifest.json`) |

**Partial-execution note**: Track 2 (text-only) omits Condition C. Reason recorded at
`results/phase3c-diversity/phase3c-comprehensive-results-report.md:22-23` ("C omitted — image
rotation is degenerate when `include_example_images=false`"). So 9 of the 10 nominal
track × condition cells were run; the missing cell is definitionally inapplicable.

## 4. Outcome

**H9 is rejected.** No diversity mechanism produces a significant gain on either track.

Manifest `outcome` field, `results/analyses-manifest.json`, analysis
`phase3c-diversity-calibration`, verbatim excerpt:

> H9 is REJECTED: at the best-F1@20m operating point each diverse condition is statistically
> indistinguishable from the identical-pass baseline A. Image (vote 3-of-5): baseline A
> F1=0.6640 (MCC 0.6603) vs diverse B 0.6682 / C 0.6713 / D 0.6688 / E 0.6705 (MCC 0.648-0.664)
> — all within ~0.007 F1 of baseline (original paired-permutation p>0.37 for every comparison).
> Text (vote 4-of-5): baseline A F1=0.7171 (MCC 0.4420) vs B 0.6862 / D 0.7301 / E 0.6943
> (MCC 0.44-0.48); only temperature-diversity D edges baseline (+0.013) and even that was not
> significant (p~0.06).

Primary (preregistered permutation) evidence,
`results/phase3c-diversity/track1-image/diversity-analysis-summary.md:31-37` (image track,
x*=3, paired permutation, 10 000 iterations):

| Comparison | ΔF1 | p | Significant? |
|---|---|---|---|
| B vs A | +0.0042 | 0.6893 | No |
| C vs A | +0.0073 | 0.6213 | No |
| D vs A | +0.0052 | 0.3750 | No |
| E vs A | +0.0069 | 0.3754 | No |

`results/phase3c-diversity/track2-text/diversity-analysis-summary.md:31-36` (text track, x*=4):

| Comparison | ΔF1 | p | Significant? |
|---|---|---|---|
| B vs A | −0.0301 | 0.0610 | No |
| D vs A | +0.0138 | 0.1812 | No |
| E vs A | −0.0221 | 0.0610 | No |

The preregistered secondary analyses (additivity/synergy, redundancy) were explicitly
discharged and reported as uninformative — see
`results/phase3c-diversity/phase3c-comprehensive-results-report.md` §2.4 ("Additivity and
Redundancy (Preregistered Analyses)"), which also records the preregistered advance criterion
as **"Not met."**

**Relation to the registered prediction**: the prediction ("at least one diversity mechanism
will improve F1") **fails**. This is a clean, well-powered negative result on the preregistered
prediction, not a failure to resolve.

## 5. Deviations

| E | Type | Summary |
|---|---|---|
| **E12** (`protocol-errata.md:258-271`) | **Clarification** | "H9 image diversity runs as HN-diversity-only (HP frozen)". Because the v1 HP pool was exhausted at 4 recognition failures (E11), the HP channel is frozen and only HN examples rotate across passes for Condition C. "H9-C tests HN rotation only; HP diversity is untestable" (line 265). |
| **E11** (`protocol-errata.md:239-254`) | Clarification | Upstream cause of E12 — HP pool structurally exhausted at 4 recognition failures. |
| **E32** (`protocol-errata.md:747-764`) | Deviation | Phase 3a uses T=0.3/T=0.7 instead of the carry-forward T=0.0. This is why H9's temperature-diversity ladder is centred on 0.7 (`T=[0.4, 0.55, 0.7, 0.85, 1.0]`, `phase3c-comprehensive-results-report.md` §1.1) rather than on the H7 optimum T=0.0 as the preregistration's adaptive-centring rule (`preregistration.md:882-886`) would imply. Indirect but load-bearing for H9-D. |
| **E36** (`protocol-errata.md:878-890`) | Deviation | 340-tile production retest replaces the 60-tile holdout. The citable H9 numbers are the 340-tile retest; the 60-tile pilot is superseded. |
| **E45, E46, E47, E54** | see cross-cutting table | Statistic and buffer conventions; E47 restores the preregistered 20 m. |

**Not covered by any erratum** (candidate gap): the omission of Condition C on the text-only
track, and the dual-track structure itself. The dual-track split traces to Decision 16
(`docs/methodology/preregistration/decisions-log.md:700`, "Dual-Track Carry-Forward After
Unexpected H1 Result"), and the C-omission rationale is stated only in the results report, not
in `protocol-errata.md`. Under the "modulo errata and amendments" framing this arguably wants
an errata entry, or at least an explicit cross-reference in the paper's deviations table.

## 6. Proposed classification

**`preregistered-with-deviation`.**

*Case for*: H9 was registered (Section 6, Tier A), its 5-condition design was executed as
specified with the preregistered 5 replications per condition, its preregistered primary and
both secondary analyses were run and reported, and its preregistered advance criterion was
evaluated and found not met. It carries at least one hypothesis-specific documented deviation
(E12, HN-only image diversity) plus a materially relevant indirect one (E32, temperature
centring). "Registered as exploratory" is not the same as "post-hoc": there is a dated,
public design that the execution matches.

*Case against / the conservative alternative*: `exploratory` is what the manifest currently
says and it is not *false* — the preregistration itself frames H9's results as
hypothesis-generating and excludes them from FDR correction (`preregistration.md:835`). If the
project chooses to reserve `preregistered*` values for the confirmatory H1–H8 block, then
`exploratory` is the right value and the registered-but-exploratory status must be carried in
prose instead.

*Recommendation*: use `preregistered-with-deviation` **and** retain an explicit
tier/confirmatory field, so the two orthogonal facts ("was it registered?" and "was it
confirmatory?") stop being collapsed into one enum. If the schema cannot be amended, keep
`exploratory` and record the E-numbers in `deviations` — which is currently `[]` and should
not be (see § 7).

## 7. Source discrepancies

1. **`hypothesis-tracking.md:246-248` vs the Phase 3c artefacts.** The tracking matrix says
   the formal A–E conditions "were not run as separate experiments". They were — twice.
   **Believe the artefacts** (`phase3c-comprehensive-results-report.md`, the two
   `diversity-analysis-report.json` files, the two study YAMLs, and `retest-phase3c` in
   `runs-manifest.json`). The tracking text post-dates the experiment by a week and was never
   corrected.
2. **`execution-checklist.md:105` repeats the same error** ("Phase 3b: H9 Diversity |
   2026-03-07 | 2026-03-08 | Implicit testing via Phase 3a parameter variation"). Note it also
   labels H9 **Phase 3b**, whereas `hypothesis-tracking.md:240`, the results directory
   (`results/phase3c-diversity/`), and the study YAMLs all label it **Phase 3c**. Phase
   labelling for H9 is inconsistent across the methodology docs.
3. **`execution-plan.md:534-543` describes H9 as a 2×2 four-condition design (A–D)**, not the
   registered five-condition A–E design. `preregistration-coverage.md:262` records the fix
   ("fixed H9 design from 4 conditions to 5 conditions (added temperature diversity condition
   D)") in prereg v2.2, but `execution-plan.md` was never updated. **Believe
   `preregistration.md:857-863`** (five conditions) — which is also what was executed.
4. **`deviations: []` in the manifest.** `phase3c-diversity-calibration` records no deviations,
   yet E12 (and arguably E32/E36) apply. Believe the errata; the manifest field is
   under-populated.
5. **Numeric discrepancy in the manifest `outcome` text**: it states that text-track
   temperature diversity D "was not significant (p~0.06)". The source permutation result for
   D vs A is **p = 0.1812**
   (`results/phase3c-diversity/track2-text/diversity-analysis-summary.md:34`); p = 0.0610 is
   the value for **B vs A and E vs A** (both *worse* than baseline). Believe the analysis
   summary. The conclusion (nothing significant) is unaffected, but the sentence as written
   mis-attributes a p-value and should be corrected before it is quoted into the paper.
6. **Baseline F1 differs slightly between layers**: manifest / conditions-manifest give
   text-A F1@20 m = 0.7171 and image-A = 0.6640; the 2026-03-25 replicate-mean summaries give
   0.7163 and 0.6640. The manifest figure comes from the 2026-06-07 rescore
   (`output_path: results/rescore-2026-06-07/phase3c`); the summary figure is a replicate mean.
   Both are defensible; they must not be mixed in one sentence.
7. **`cross-track-comparison.md` §4 says "At full scale (487 tiles)"**
   (`results/phase3c-diversity/cross-track-comparison.md`, "Variance stabilisation did not
   replicate at scale"). The retest scope is **340** tiles — verified: the analysis metadata
   points at `inputs/vectors/bounds/full_evaluation_bounds.geojson`, which has 340 features
   (the 487-tile file is `inputs/vectors/bounds/384/full_evaluation_bounds.geojson`). Believe
   340. This is a factual error in a document that carries a revision banner and is otherwise
   well maintained.

## 8. Where reported

**Reported.** `docs/paper/results-draft.md:123-127`, § R3:

> Deliberately engineered diversity, however, adds nothing: the preregistered H9 test of
> cross-variant pooling (prompt/modality/temperature mixtures) found no significant gain over
> a same-variant baseline pool (all p > 0.37 image, > 0.06 text) — temperature sampling already
> supplies what engineering was supposed to add.

Also in the outline at `docs/paper/results-outline.md:213` ("(H9 rejected)").

Note the draft describes H9 as "cross-variant pooling", which is a fair gloss but not the
registered vocabulary ("diversity mechanisms", conditions A–E). Note also that the draft's
parenthetical "all p > 0.37 image, > 0.06 text" is correct as a floor but reads as though 0.06
were the *closest* result of interest; the closest-to-baseline *improvement* (D) has p = 0.181.

---

# H10 — Training Pool Size Effects on Library Quality

## 1. As registered

**Source**: `docs/methodology/preregistration/osf/preregistration.md:904-940`.

Heading (line 904):

> ### H10: Training Pool Size Effects on Library Quality

H10 is registered as a **question**, not a directional prediction. Line 910, verbatim:

> **Question**: How does training pool size affect detection performance on held-out tiles?

Background (line 908):

> **Background**: Few-shot library construction (Section 8.4.1) identifies hard examples from
> training tile evaluation. A larger training pool may surface more diverse or representative
> hard examples, improving the resulting library's effectiveness.

Specified test (line 912, table 914-919):

> **Test**: Construct few-shot libraries from progressively larger training pools:
>
> | Condition | Training Tiles | Holdout Tiles | Notes |
> | A | 20 | 60 | Current design |
> | B | 40 | 60 | 2× training |
> | C | 80 | 60 | 4× training |
> | D | 160 | 60 | 8× training |

Specified implementation (lines 921-926): nested pools (A ⊂ B ⊂ C ⊂ D), same holdout across
all conditions, identical library-construction procedure, documented library composition per
condition.

Specified analysis (lines 928-932), verbatim:

> **Analysis**:
>
> - F1 on holdout as function of training pool size
> - Characterise diminishing returns curve
> - Compare library composition across conditions (do larger pools find different hard
>   examples?)

Constraints (lines 934-938): 361 total tiles, holdout fixed at 60, maximum training pool ~301.
Sequencing (line 940): "Conducted after Stage 2 completion but before generalisation to
out-of-sample maps."

The 7.2 summary table (`preregistration.md:1166`) records the analysis as "F1 vs pool size
curve".

## 2. Registered status

**Exploratory, Tier B.** `preregistration.md:906`:

> **Status**: Exploratory (Tier B)

Tier B is defined at `preregistration.md:900-902` as "Budget-Dependent Exploratory — *Tests
conducted if budget permits and triggered by Stage 1-2 results.*" Corroborated at
`preregistration.md:1166` and `preregistration.md:2173`.

**Note**: unlike H11 and H12, H10 carries **no explicit trigger condition** in the
preregistration — only the budget/sequencing framing.

## 3. Execution — resolving E50 vs "not started"

**H10 was executed, on 2026-04-15, as "H10 v2". `hypothesis-tracking.md` is simply wrong.**

The contradiction the brief flagged resolves cleanly in favour of E50: the erratum describes a
real, completed run, and the tracking matrix row was never updated. Evidence:

| Layer | Evidence |
|---|---|
| Run register | `results/runs-manifest.json`, `run_id: "h10"` — `"primary_hypothesis": "H10"`, `"directory_path": "outputs/h10"`, `"tile_size_px": 384`, `"corpus": "4-map-gs"`, `"gt_reference": "curator"`, `"scope": {"test_set_id": "era-3-327", "bounds_path": "inputs/vectors/bounds/384/h10_test_bounds.geojson", "n_test_tiles": 327, "calibration_set_id": "pool_160", "n_calibration_tiles": 160}` |
| Conditions | `results/conditions-manifest.json` — `h10::greedy-pool-020`, `h10::greedy-pool-040`, `h10::greedy-pool-080`, `h10::greedy-pool-160`, `h10::verified-pool-160` (5 conditions, all `n_passes: 5`, `vote_threshold: 4`) |
| Results tree | `results/h10/analysis_summary.md` (371 lines per `wc -l`, dated 2026-04-15 at lines 3-4), plus `h10_consensus_only_20m.json`, `h10_pool_020_pv_20m.json`, `h10_pool_160_pv_20m.json`, `h10_pv_permutation_020_vs_160.json`, `h10_wbf_consensus_20m.json`, and `results/h10/with-mcc/pool_{020,040,080,160}/evaluation.{csv,json,md}` |
| Working notes | Obs 236, `docs/notes/working-notes.md:9764` — "Observation 236: H10 Pool Size Is a Null — 20-Tile Calibration Matches 160-Tile Under PV (2026-04-15)" |
| Errata | E49 (`protocol-errata.md:1313`) and E50 (`protocol-errata.md:1343`), both dated 2026-04-15, both describing execution parameters of a run that happened |

**`analysis_id`: NONE.** There is no entry for H10 in `results/analyses-manifest.json` or in
its hand-authored source `results/run-analyses.json` — verified by enumerating all 18 analyses
in each; no `hypothesis_refs` array contains `"H10"`, and no `conditions_compared` entry has
the `h10::` prefix. The H10 conditions are registered; the H10 *analysis* is not.

**Why the tracking matrix says "not started"**: the H10 row has never been edited. `git log`
shows `hypothesis-tracking.md` was last touched by commit `4be2d68a3` (2026-04-16, "feat(h12-v2):
H12 HP:HN ratio experiment setup + protocol-errata E52"); the diff of that commit changes only
the `**Last updated**` line and the H12 row. The "Not started (HP pool exhausted)" text for
H10 predates the v2 pool mining that made H10 runnable.

**Partial execution — a real caveat.** The PV (proposer-verifier) leg was run for **two** of
the four pools only. `results/h10/analysis_summary.md:228-233`:

> 1. **Pool-size PV test is pool_020 vs pool_160 only.** Pool_040 and pool_080 have
>    consensus-only data but no PV 2D sweep. Obs 236 treats the three smaller pools as
>    indistinguishable at consensus (ΔF1 < 0.01) and therefore unlikely to separate under PV.
>    This is a reasonable assumption given the 020 vs 160 null, but it has not been directly
>    tested and is a minor limitation of the study.

All four pools **were** run at the consensus stage, so the preregistered "F1 vs pool size
curve" is complete; it is only the PV extension (itself post-hoc, E37) that is 2-of-4.

**Retracted v1 arm.** An earlier H10/H12 pass (2026-04-11, K=10, text-only) was formally
retracted because the proposer configs carried `include_example_images: false`, so the
few-shot library was never transmitted to the API. Retraction: Obs 235,
`docs/notes/working-notes.md:9399` ("Observation 235: Formal Retraction of H10/H12 'Findings'
(Obs 227, Obs 234) — Config-Intent Mismatch, Process Failure, and Rules Added to Prevent
Recurrence (2026-04-14)"). Preserved, not deleted, under
`archive/h10-h12-v1-retracted-probe/` — enumerated at `results/h10/analysis_summary.md:181-189`
with an explicit "must not be cited" instruction.

## 4. Outcome

**Null: calibration-pool size does not matter under the PV pipeline.**

`results/h10/analysis_summary.md:29-43`:

> ## Headline result — pool-size null under PV
>
> Four nested calibration pools (20 ⊂ 40 ⊂ 80 ⊂ 160) produce post-verifier F1s
> indistinguishable within sampling noise:
>
> | Comparison | F1 (a → b) | ΔF1 | p | Signif? |
> | pool_020 PV vs pool_160 PV | 0.727 → 0.722 | +0.005 | 0.845 | no |

Re-verified at source, `results/h10/h10_pv_permutation_020_vs_160.json`:
`observed_f1_diff = 0.004651`, `p_value = 0.8453`, `n_permutations = 10000`, `n_tiles = 327`,
`wins_a = 35`, `losses_a = 33`, `ties = 259`; `global_a.f1 = 0.726974` (vote_t 3, prob_t 0.15),
`global_b.f1 = 0.722323` (vote_t 4, prob_t 0.05).

Consensus-only leg (`results/h10/analysis_summary.md:76-81`, each pool at its own best
threshold):

| Pool | Best T | F1 | Precision | Recall | n detections |
|---|---|---|---|---|---|
| 020 | T=3 | 0.697 | 0.672 | 0.724 | 344 |
| 040 | T=3 | 0.694 | 0.669 | 0.721 | 344 |
| 080 | T=3 | 0.688 | 0.666 | 0.712 | 341 |
| **160** | **T=4** | **0.717** | **0.843** | **0.624** | **236** |

(For cross-reference: at the *fixed* t=4 operating point recorded in
`results/conditions-manifest.json`, the same conditions read `h10::greedy-pool-020` F1@20 m
0.6934, `-040` 0.6809, `-080` 0.6618, `-160` 0.7171, `h10::verified-pool-160` 0.7223. Do not
mix the "each pool at its own best T" table with the fixed-t=4 table.)

**Relation to the registered question**: H10 registered a *question*, not a direction, so the
result cannot "contradict" a prediction. It **answers** the question: the F1-vs-pool-size
curve is flat under PV, with a consensus-stage +0.020 F1 lead for pool_160 that the verifier
compresses to +0.005 (n.s.). The preregistered "diminishing returns curve" is characterised —
as essentially no returns. The preregistered third analysis ("do larger pools find different
hard examples?") is addressed qualitatively via the operating-point shift (pool_160 is more
precise / less recall-y, `analysis_summary.md:83-87`) rather than by a formal
library-composition comparison.

**Practical claim the PI may want in the paper** (`results/h10/analysis_summary.md:264-270`):
a new deployment can calibrate on ~20 tiles and match 160-tile calibration under PV.

## 5. Deviations

| E | Type | Summary |
|---|---|---|
| **E49** (`protocol-errata.md:1313-1339`) | **Deviation** | "H10 calibration uses cold-start production config instead of preregistered image-only baseline." Changes T (1.0 → 0.7), thinking (implied minimal → HIGH), instruction file (image-only → `detect_brief-text-image`), examples (full 17-item baseline library → cold-start legend + nulls, 9), crop size (128 px → 150 px). Explicitly changes *which examples are identified as hard*. |
| **E50** (`protocol-errata.md:1343-1362`) | **Deviation** | "H10 holdout expanded from 60 to 327 tiles." Consequence of the 384 px move (E36/H11), which raised total tiles from 361 to 487; 487 − 160 calibration = 327. The preregistered calibration pool sizes (20/40/80/160) are unchanged. Impact: increased statistical power. |
| **E13** (`protocol-errata.md:275-291`) | Deviation | Indirect: defers H12 to post-H10, i.e. names H10 as the unblocking step. Establishes H10's role in the sequence. |
| **E11** (`protocol-errata.md:239-254`) | Clarification | Upstream: HP pool exhaustion at 4 recognition failures, the condition H10's pool expansion was meant to relieve. |
| **E51** (`protocol-errata.md:1366-1466`) | Deviation | H8 v2 re-run; reuses the H10 v2 `pool_160_hp4hn4` run directly as its Scale-8 condition (lines 1397-1404) and shares H10's 327-tile evaluation manifest. Binds H8 v2 and H10 v2 into one pipeline. |
| **E37** (`protocol-errata.md:894-908`) | Deviation | PV pipeline is a post-hoc extension beyond the preregistered design. H10's *headline* is the PV comparison, so this matters: the PV leg is not preregistered even though the consensus leg is. |
| **E45** (`protocol-errata.md:1097`) | Deviation | Micro-average F1 permutation statistic — the method used for the 0.845 p-value. |
| **E54, E47** | see cross-cutting table | 1 000-iteration bootstrap; 20 m buffer. |

Also relevant, though logged as a decision rather than an erratum: **Decision 11**
(`docs/methodology/preregistration/decisions-log.md:363`, "50m Recognition/Localisation
Threshold and HP Pool Exhaustion"), whose §"Implications for H9 (diversity) and H12 (ratio)"
(line 442) is the origin of the post-H10 deferrals.

## 6. Proposed classification

**`preregistered-with-deviation`.**

*Case for*: the four preregistered pool sizes (20/40/80/160) were built as nested pools and
evaluated on a common disjoint holdout, exactly as registered; the preregistered primary
analysis (F1 vs pool size) was performed; both documented departures (E49, E50) are logged,
dated, and justified. Neither departure is design-breaking — E50 *increases* power on the
preregistered design, and E49 changes the calibration config while preserving the manipulated
factor.

*Case against*: E49 is not cosmetic. It changes the config under which hard examples are
mined, which is the *mechanism* H10 is about ("A larger training pool may surface more diverse
or representative hard examples"). `results/h10/analysis_summary.md:234-244` says so plainly:

> The v2 null is a NULL for the production pipeline, not for the preregistered image-only
> baseline. This is a deliberate, defensible deviation, but readers should not read "H10 v2
> null" as "calibration-pool size is null under the original prereg settings".

A reviewer could reasonably argue this makes H10 v2 a *different experiment* that answers the
registered question under different conditions — i.e. `exploratory`. There is also the
headline-provenance problem: the *headline* (PV null) rests on a non-preregistered
architecture (E37), and the PV leg covers 2 of 4 pools.

*Recommendation*: `preregistered-with-deviation`, with `deviations: ["E49", "E50", "E13",
"E37", "E45"]`, and a Results/Methods sentence carrying the `analysis_summary.md:234-244`
caveat verbatim. If the PI prefers maximal conservatism, an acceptable alternative is to split
it: consensus-stage leg = `preregistered-with-deviation`; PV-stage leg = `exploratory`.

**Explicitly NOT `not-executed`.** The E50-vs-"not started" contradiction resolves in favour
of execution on five independent lines of evidence (run register, conditions register, results
tree, working notes, errata).

## 7. Source discrepancies

1. **`hypothesis-tracking.md:29` says "Not started (HP pool exhausted)"; the run happened on
   2026-04-15.** **Believe the artefacts.** The row was never edited (git-verified: the only
   post-2026-04-15 edit to that file, commit `4be2d68a3`, touched the H12 row and the
   date line only).
2. **`hypothesis-tracking.md:291` execution-dependency chain says "Phase 5: Exploratory
   (H10-H15 as triggered) ○ H10-H13 not started"** — same error, same cause.
3. **`docs/paper/results-outline.md:424` and `:448` inherit the error**, listing H10 among
   "registered-but-not-executed hypotheses (H6, H10, H13 per the tracking matrix)". This is the
   most consequential propagation: it would put a false disclosure in the paper. **H10 must be
   removed from that list.** (H6 and H13 are outside this brief and unverified here.)
4. **No `analysis_id` exists for H10** despite conditions being registered and a 371-line
   analysis summary existing. The analyses register and the results tree disagree about whether
   this analysis exists. Believe the results tree; the register is incomplete.
5. **Holdout tile count**: preregistration says 60 (`preregistration.md:914-919`, :937); actual
   is 327. E50 documents this. Believe E50 + the bounds file
   (`inputs/vectors/bounds/384/h10_test_bounds.geojson`, verified 327 features).
6. **Minor**: `results/h10/analysis_summary.md` lacks the `> **Last revised**` banner and
   `## Changelog` section required by the repo's Document Revision Policy for `results/**.md`.
   Back-fill on touch.

## 8. Where reported

**NOT CURRENTLY REPORTED. This is a disclosure obligation.**

- `docs/paper/results-draft.md`: no mention. Grep for `H10`, `pool size`, `pool-size`,
  `calibration pool`, `hard positive`, `hard negative`, `hard-example`, `library`, `few-shot`
  returns only § R2's reference to H8 (`results-draft.md:88`, `:103`) and a passing "few-shot"
  at `:98` — all of which refer to the Era-1 512 px single-pass H8, not the Era-3 library axis.
- `docs/paper/results-outline.md`: H10 appears only in the D17 decision block
  (`:424`, `:448`) **and there it is listed as not executed** — i.e. the one place it is
  mentioned states the opposite of the truth.

**Compounding finding**: no analysis in `results/analyses-manifest.json` references *any*
condition from the `h10`, `h12-v2`, or `h8-v2` runs. Verified by enumerating the run prefixes
across all `conditions_compared` arrays: the set is `{55maps-image-generalisation,
55maps-text-high-generalisation, 55maps-text-high-t0-3-generalisation,
55maps-text-min-generalisation, 55maps-text-min-n10-uplift, flash35-pv-2x2,
n1-outstanding-384, n1-pro-rerun-384, pv-diag-256, pv-diag-384,
retest-h11-single-pass-384-t0, retest-phase2a, retest-phase2b, retest-phase2c,
retest-phase2d, retest-phase2e, retest-phase3a, retest-phase3a-high,
retest-phase3a-replication, retest-phase3c, verifier-robustness}`. The **entire Era-3
library-design axis** (H8 v2 + H10 v2 + H12 v2, three preregistered factors, ~$34+ of API
spend on H12 alone) is absent from both the analysis register and the paper draft.

---

# H11 — Tile Size Effects on Detection Performance

## 1. As registered

**Source**: `docs/methodology/preregistration/osf/preregistration.md:944-976`.

Heading (line 944):

> ### H11: Tile Size Effects on Detection Performance

Trigger (line 948), verbatim:

> **Trigger**: Run if detection performance on 512×512 tiles shows room for improvement
> (F1 < 0.85) or if processing speed is a concern for deployment.

Question (line 952):

> **Question**: Does reducing tile size from 512×512 improve detection performance?

Specified test (line 954, table 956-959):

> **Test**: Apply optimal configuration from Stages 1-2 across tile sizes:
>
> | Condition | Tile Size | Area Multiplier | API Calls (×) | Symbol:Pixel Ratio |
> | A | 512×512 | 1× (baseline) | 1× | Lower |
> | B | 384×384 | 0.56× | ~1.8× | Higher |

The rationale note (line 963) explicitly considers and *rejects* testing 1024×1024 and
2048×2048, and reports 256 px and 1024 px pilot behaviour (256 px: recall 0.90, precision 0.10
at 2/5 consensus; 1024 px: precision 0.28, recall 0.37).

Specified implementation (lines 965-970): optimal config from Stages 1–2; 64 px overlap;
few-shot library images regenerated at 384×384; ground truth regenerated for the smaller tile
boundaries.

Specified analysis (lines 972-976), verbatim:

> **Analysis**:
>
> - F1 as function of tile size
> - Cost-efficiency analysis: F1 improvement vs API call increase
> - Qualitative assessment: Does smaller size help with crowded areas?

The 7.2 summary table (`preregistration.md:1167`) records the analysis as "Compare F1,
cost-efficiency".

Related registered material: `preregistration.md:2225` — "Specify success threshold: F1 ≥ 0.85
triggers H11 tile size testing" (checklist item, marked `[x]`); `preregistration.md:2280` —
H11 and H13 may interact.

## 2. Registered status

**Exploratory, Tier B.** `preregistration.md:946`:

> **Status**: Exploratory (Tier B)

Corroborated at `preregistration.md:1167` and `preregistration.md:2174`.

**Trigger status: met.** The registered trigger fires if 512 px F1 < 0.85. The best 512 px
result anywhere in the study is F1 = 0.792 (`era1-leaderboard` Tier-1 sole leader,
`verified-adv-text-high-t1.0-n30-23of30`; `results/tile-size-sweep/tile_size_sweep.md:50`).
Every 512 px cell is below 0.85, so the trigger condition is satisfied. (This is one of only
two hypotheses in the block with a formal trigger; H12's, by contrast, was *not* met — see
below.)

## 3. Execution

**Executed, and over-delivered on the registered design.** The registered design is a two-arm
comparison (512 vs 384); the study ran a **three-way** comparison (256 / 384 / 512) across
three architectures.

| Layer | Evidence |
|---|---|
| `analysis_id` | `tile-size-sweep` — `results/analyses-manifest.json`, `hypothesis_refs: ["H11"]`, `output_path: results/tile-size-sweep`, `manually_verified_at: 2026-06-09T01:52:52Z`, 35 conditions in `conditions_compared` |
| Secondary `analysis_id` | `unswept-pools-completeness` — `hypothesis_refs: ["H2", "H11"]` |
| `run_id`s (H11-primary) | `retest-h11-single-pass-384-t0` (`results/runs-manifest.json`: `"primary_hypothesis": "H11"`, `tile_size_px: 384`, `test_set_id: "era-2-487"`, `n_test_tiles: 487`, `purpose: "H11 single-pass 384px baseline (T=0)."`) |
| `run_id`s (supporting) | `pv-diag-384` and `pv-diag-256` (both in `results/runs-manifest.json`); 20 `studies/h11-384-*.yaml` and 2 `studies/h11-256-*.yaml` study definitions on disk |
| Results tree | `results/h11/analysis_summary.md` (306 lines per `wc -l`, paper-citation layer); `results/h11-tile-size-results.md` (646 lines, `wc -l`-verified; the comprehensive narrative); `results/h11-384-pv-diagnostic/` (137 entries, verified by `ls | wc -l`);
`results/h11-384-single-pass-t0-rerun/`; `results/tile-size-sweep/tile_size_sweep.{json,md}` |
| Working notes | Obs 179 (`working-notes.md:3833`), Obs 180 (`:3930`), Obs 181 (`:3968`), Obs 351 (`:18681`), Obs 352 (`:18844`) |

**Two-stage execution history**:

1. **Pilot (2026-03-15), 60-tile scope — conclusion retracted.**
   `results/h11/analysis_summary.md:50-58`: the pilot concluded "384 proposer-verifier does not
   improve F1" (pilot F1 0.684 at 384 PV vs 0.796 at 512 PV); Obs 179 retracted this as
   underpowered (MDE ≈ 0.09; the real effect was +0.06). "The paper's tile-size claim must cite
   the 487-tile production result, not the pilot" (line 71-72).
2. **Production (2026-03-22 onward), 487-tile scope**, plus a 256 px diagnostic at 1 032 tiles
   (2026-03-23), plus the 2026-06-08 three-way `tile-size-sweep` re-analysis.

## 4. Outcome

**The registered question is answered: yes, 384 px beats 512 px — but the optimum is
architecture-dependent.**

H11-specific headline, `results/h11/analysis_summary.md:22-32` (487-tile production footprint,
435 reference mounds, 20 m buffer):

| Tile size | Best config | F1 | Paired Δ vs 384 px best | p | Scope |
|---|---|---|---|---|---|
| 256 px | text 5-of-5 + PV | 0.844 | −0.005 | 0.816 | 1 032 tiles, 431 mounds |
| **384 px** | **text 6-of-10 + PV** | **0.883** | — | — | **487 tiles, 435 mounds** |
| 512 px | text 5-of-10 + PV | 0.831 | −0.063 | **0.002** | 487 tiles, 435 mounds |

Key claim (`analysis_summary.md:36-39`): "**384 px significantly outperforms 512 px** by +0.063
F1 in a paired comparison (p = 0.002). The effect holds across six paired comparisons ... at
p ≤ 0.008 for all six."

Current manifest `outcome` (`results/analyses-manifest.json`, `tile-size-sweep`), key excerpt:

> The optimal tile size is ARCHITECTURE-DEPENDENT ... CLEAN ISOLATION (hold architecture x
> modality x thinking x temperature constant, vary only size): single-pass text climbs
> monotonically with tile size (256=0.342 < 384=0.520 < 512=0.606) ... Text MINIMAL consensus
> still prefers 512 ... Text HIGH consensus FLIPS to 384 (T0.7 0.814 > 512 0.773 ...)
> CONSENSUS+VERIFIER head-to-head ...: 384=0.890 > 256=0.856 > 512=0.793 -- best=384px

Source artefact `results/tile-size-sweep/tile_size_sweep.md:39`:

> | text | consensus+PV | 0.856 | 0.890 | 0.792 | best=384px (Δ-0.063 over 256→512) |

The registered *cost-efficiency* analysis is discharged qualitatively rather than as a formal
F1-per-API-call figure: `results/h11/analysis_summary.md:171-179` argues 384 over 256 on
false-positive density and verifier-precision grounds, and `:200-203` reports that N=5
consensus suffices at 384 px (recall saturates ~0.92), which is the study's main cost claim.
The registered *qualitative* analysis ("does smaller size help with crowded areas?") is, as far
as I can find, **not discharged as a standalone analysis** — `UNVERIFIED: would need a full
read of results/h11-tile-size-results.md §§8–9 to confirm whether crowded-area behaviour is
addressed there.`

**Relation to the registered question**: **supports** the implied direction (384 < 512 in
pixels is better in F1), with the important refinement that this holds only once a
false-positive filter (HIGH-thinking consensus, or a verifier) exists; bare single-pass prefers
*larger* tiles.

## 5. Deviations

| E | Type | Summary |
|---|---|---|
| **E41** (`protocol-errata.md:960-972`) | **Deviation** | "384px tile size and full evaluation set used for Pro comparison." Nominally an H6 erratum, but it is the entry that records H11's 384 px pathway as the production lock-in ("the optimal tile size identified by the H11 diagnostic (Obs 181)"). Cited by `results/h11/analysis_summary.md:6` as one of H11's governing errata. |
| **E43** (`protocol-errata.md:1039-1067`) | **Deviation** | "consensus-384 executed at T=1.0 instead of T=0.7." 30 runs × 487 tiles at the wrong temperature, caused by `detect_brief-text.json` hard-coding `"temperature": 1.0` and `run_phase2.py` preferring the config default over the YAML override. Data preserved as `outputs/h11/consensus-384-UNINTENDED-T1.0/`; corrected baseline at `outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/`. |
| **E44** (`protocol-errata.md:1070-1093`) | **Deviation** | "single-pass-384 executed at T=1.0 instead of T=0.0." Same root cause; 10 runs × 240 tiles. Archived to `archive/h11-unintended-t1.0/single-pass-384-UNINTENDED-T1.0/`; corrected rerun is `outputs/retest/h11-single-pass-384-t0/` (10 runs, 487 tiles). |
| **E57** (`protocol-errata.md:1782-1851`) | **Metadata correction + billing reconciliation** | "H11 384px Pro/baseline detection metadata — model template default and output_dir overrides." Impact revised 2026-06-03 from "Low — provenance only" to "Medium–High": four "Pro" cells in `n1-outstanding-384` were dispatched and billed as `gemini-3-flash-preview`. Changed the N=1 leaderboard finding. Affects H11-hosted pools, though the affected *analysis* is `n1-baseline-matrix-384` (`hypothesis_refs: ["H1","H6","H7"]`), not `tile-size-sweep`. |
| **E36** (`protocol-errata.md:878-890`) | Deviation | 340-tile retest replaces 60-tile holdout — the change that produced the 487-tile 384 px footprint (E50 cites "the move to 384px tiles (E36/H11)"). |
| **E53** (`protocol-errata.md:1581-1670`) | Deviation | Phase 3a-HIGH image track moved 512 px → 384 px. Primarily an **H3** erratum, but it is executed "using the existing H11 infrastructure" (line 1621) and cites H11 as "the tile-size bridge (384 px vs 512 px) for cross-era comparison" (line 1641). Include as an H11-adjacent entry, not an H11-primary one. |
| **E51, E52** (`:1366`, `:1468`) | Deviation | Both cite H11's 384 px closure as the reason H8 v2 / H12 v2 re-ran at 384 px. H11 is upstream of the entire Era-3 axis. |
| **E56** (`protocol-errata.md:1746`) | Methodological clarification | Verifier probability thresholds are in-sample; H11's consensus+PV rows use best-`prob_t` per cell. |

**Undocumented-in-errata deviations from the registered H11 design** (candidates for the
paper's deviations table):

- **A third tile size (256 px) was tested**, which the preregistration explicitly did *not*
  register (it registered only A=512, B=384; `preregistration.md:956-959`). 256 px appears in
  the registered *rationale* note as a pilot observation (line 963), not as a condition.
- **Tile overlap**: the registered implementation says "Tiles generated from source maps with
  64px overlap" (`preregistration.md:968`); the production 384 px stack uses 336 px stride =
  **48 px** overlap (12.5 %) — see `results/h11/analysis_summary.md:145-147` and
  `protocol-errata.md:1384` ("| Stride | 448 px | 336 px |"). The *percentage* (12.5 %) is
  preserved; the absolute pixel overlap is not. I could not find an erratum covering this.
  `UNVERIFIED as a deviation: would need a search of protocol-errata.md and decisions-log.md
  for a stride/overlap entry I may have missed, plus confirmation that 64 px was intended as
  absolute rather than as "12.5 % of tile".`

## 6. Proposed classification

**`preregistered-with-deviation`.**

*Case for*: the registered trigger was met; the registered two-arm comparison (512 vs 384) was
executed at scale on a common map corpus and curator GT; the registered primary analysis
("F1 as function of tile size") is the headline; the registered cost-efficiency analysis is
discharged in substance. Multiple hypothesis-specific errata apply (E43, E44, E57, plus E41 as
the lock-in record), which is exactly what `preregistered-with-deviation` is for.

*Case against*: (a) the *reported* result is a three-size, three-architecture interaction study
whose framing ("the optimum is architecture-dependent", Obs 351) is a post-hoc refinement, not
the registered question; the manifest's own `predicted_outcome` field says so — "The refined
hypothesis (Obs 351)". (b) The 256 px arm has no registered basis. (c) Tile size is confounded
with tile set (1 032 / 487 / 340 tiles), acknowledged in the manifest `outcome`
("tile size is confounded with tile set ... so F1@20m is the cross-size headline and tile-MCC
is reported per size, never differenced").

*Recommendation*: `preregistered-with-deviation` for the 512-vs-384 core, with the 256 px arm
and the architecture-interaction framing explicitly flagged in prose as post-hoc extensions.
Populate `deviations` with `["E41","E43","E44","E57","E36"]` (currently `[]`). If the PI wants
a single value that covers the whole `tile-size-sweep` analysis as reported, `exploratory` is
defensible — but it under-sells a hypothesis whose trigger, comparison, and primary analysis
were all registered in advance.

## 7. Source discrepancies

1. **`hypothesis-tracking.md:30` says "Complete (384 pathway closed) | 2026-03-15"** — the
   date is the **pilot** date, and the pilot's conclusion was **retracted**
   (`results/h11/analysis_summary.md:50-58`, Obs 179, 2026-03-22). The row is directionally
   right ("Complete") but its date points at superseded work. Believe
   `results/h11/analysis_summary.md`.
2. **Manifest `outcome` says 512 px consensus+PV = 0.793; the source artefact says 0.792**
   (`results/tile-size-sweep/tile_size_sweep.md:39`), as does `docs/paper/results-draft.md:154`
   and `results/tile-size-sweep/tile_size_sweep.md:50`
   (`verified-adv-text-high-t1.0-n30-23of30`, 0.792). Believe **0.792**; the manifest text has
   a one-digit typo.
3. **Two different "H11 headline" numbers are in circulation**: 0.883 (`results/h11/
   analysis_summary.md:31`, 384 text 6-of-10 + PV, 487-tile) and 0.890
   (`tile-size-sweep` View 3 / `results-draft.md:160`, `pv-diag-384::verified-adv-text-
   consensus-16of30`, GS 384 px instrument). They are different cells under different
   scoring vintages, both legitimate. The paper must not present them as the same number.
4. **`results/h11-tile-size-results.md` §§2–7 are formally retracted as citable material**
   (`results/h11/analysis_summary.md:164-170`) while remaining in the working tree. Anyone
   citing that file must cite §§8–9 only.
5. **`deviations: []`** on `tile-size-sweep` despite E41/E43/E44/E57 all applying. Believe the
   errata.
6. **`hypothesis-tracking.md:73`** lists "H11 factorial (Session 50): 3 strategies × 2 tracks
   at 384 tiles" under **H2**, not under H11 — the H11/H2 boundary in the tracking matrix is
   blurred. Minor, but relevant to any per-hypothesis attribution.

## 8. Where reported

**Reported.** `docs/paper/results-draft.md:149-158`, § R4:

> The verifier also interacts strongly with tile size (H11). The tile-size optimum is
> architecture-dependent: single-pass climbs monotonically with tile size (256 px 0.342 <
> 384 px 0.520 < 512 px 0.606 in the clean isolation) ... and under consensus + verifier the
> ordering is **384 (0.890) > 256 (0.856) > 512 (0.792)** (analysis `tile-size-sweep`).

Also `docs/paper/results-outline.md:228` ("Tile size × verifier (H11): architecture-dependent
optimum") and `:232` (decision D10 — whether tile size stays folded into R4 or gets its own
subsection, still OPEN per the register at `:467`).

**Caveat for the PI**: as drafted, H11 is reported *as an aspect of the verifier story*, not as
a preregistered hypothesis with a registered trigger and a registered two-arm comparison. The
registered 512-vs-384 comparison and its p = 0.002 paired result
(`results/h11/analysis_summary.md:36-39`) do not appear in the draft at all; what appears is
the post-hoc three-way architecture interaction. If the paper wants credit for H11 as
preregistered work, the registered comparison needs its own sentence.

---

# H12 — Hard Positive to Hard Negative Ratio

## 1. As registered

**Source**: `docs/methodology/preregistration/osf/preregistration.md:980-1010`.

Heading (line 980):

> ### H12: Hard Positive to Hard Negative Ratio

Prerequisite (line 984):

> **Prerequisite**: H8 (library size) complete; optimal library size determined

Directional expectations, background (lines 986-990), verbatim:

> **Background**: The main factorial (H8) uses a 1:1 ratio of hard positives to hard negatives
> across all library sizes. However, optimal ratio may differ:
>
> - Higher HP:HN ratio may improve recall (more positive guidance)
> - Lower HP:HN ratio may improve precision (more exclusion examples)
> - Optimal ratio may depend on library size or baseline error profile

Research question (line 992):

> **Research question**: Does the ratio of hard positives to hard negatives affect detection
> performance, holding total hard example count constant?

Specified test (line 994, table 996-1000):

> **Test**: At optimal library size from H8 (selecting from A-D only; Pure Positive
> Canon/Canonical excluded as they have no empirical hard examples), compare ratios while
> holding total hard example count constant:
>
> | Condition | HP | HN | Total Hard | Ratio |
> | R1 | 2 | 6 | 8 | 1:3 (HN-heavy) |
> | R2 | 4 | 4 | 8 | 1:1 (balanced) |
> | R3 | 6 | 2 | 8 | 3:1 (HP-heavy) |

Specified analysis (lines 1004-1008), verbatim:

> **Analysis**:
>
> - Compare F1, precision, and recall across ratio conditions
> - Test whether ratio affects precision vs recall differentially
> - Identify whether ratio interacts with baseline error profile (FP-heavy vs FN-heavy tiles)

Trigger (line 1010), verbatim:

> **Trigger**: Run if H8 shows library size matters

The 7.2 summary table (`preregistration.md:1168`) records the analysis as "Compare ratios at
fixed total". The H8 section also forward-references H12: `preregistration.md:813` — "Ratio
exploration is addressed in H12 (exploratory)."

## 2. Registered status

**Exploratory, Tier B — and conditional.** `preregistration.md:982`:

> **Status**: Exploratory (Tier B)

`preregistration.md:2175` adds the conditionality explicitly:

> - **H12** (HP:HN ratio) — Tier B (conditional on H8)

Corroborated at `preregistration.md:1168`.

**Trigger status: NOT met.** This is important and is disclosed in the errata rather than
hidden. `protocol-errata.md:1498-1504`:

> **Trigger deviation**: H12's preregistered trigger is "run if H8 shows library size matters"
> (preregistration line 1010). H8 v2 (completed 2026-04-15, Observation 238) returned a null
> result: all seven library-composition contrasts (C1, C2, C3, B1, S1, S2, S3) null after
> Benjamini–Hochberg FDR correction at q = 0.05, with an F1 spread of only 0.040 across all
> seven conditions at greedy consensus threshold t = 4. Strictly read, the trigger is not met.

The stated justification (lines 1506-1518) is orthogonality (size ≠ balance; the registered
secondary analysis predicts a directional effect even under an overall F1 null) plus
publishability of nulls.

## 3. Execution — did h12-v2 ever complete?

**Yes. It completed on 2026-04-16.** `hypothesis-tracking.md`'s "In progress" is a launch-time
status that was never closed out.

| Layer | Evidence |
|---|---|
| Run register | `results/runs-manifest.json`, `run_id: "h12-v2"` — `"primary_hypothesis": "H12"`, `"directory_path": "outputs/h12-v2"`, `"run_type": "consensus"`, `"tile_size_px": 384`, `"scope": {"test_set_id": "era-3-327", "n_test_tiles": 327, "calibration_set_id": "pool_160"}` |
| Conditions | `results/conditions-manifest.json` — `h12-v2::greedy-{r1-hn-heavy,r2-balanced,r3-hp-heavy}` and `h12-v2::wbf-{r1-hn-heavy,r2-balanced,r3-hp-heavy}` (6 conditions, all `n_passes: 5`, `vote_threshold: 4`) |
| Results tree | `results/h12-v2/analysis_summary.md` (205 lines per `wc -l`; header line 4: "**Date**: 2026-04-16 (runs launched 2026-04-15). **Polish level-up**: 2026-04-24"); `analysis_summary.txt`; `fdr_summary.txt`; `permutation-t4/`; `permutation-wbf/`; `greedy/{r1,r2,r3}/t{1..5}/evaluation.{csv,json,md}`; `wbf/`; `wbf-mcc/`; `with-mcc/` |
| Working notes | Obs 239, `docs/notes/working-notes.md:10075` — "Observation 239: H12 v2 HP:HN Ratio Is a Null — All Three Pairwise Contrasts Fail After BH-FDR; Library-Design Story Closed (2026-04-16)" |
| Execution summary | `results/h12-v2/analysis_summary.md:154-166`: conditions launched R1, R3 (R2 reused); 5 passes/condition; 327 tiles/pass; 3 270 new API calls; ~26 min wall time; 250 workers; realtime + flex + context cache; ~$34.00 total |

**`analysis_id`: NONE.** As with H10, there is no H12 entry in `results/analyses-manifest.json`
or `results/run-analyses.json`.

**R2 was not re-launched.** `protocol-errata.md:1535-1544`: R2 (4 HP + 4 HN) is byte-identical
to H8 v2 Scale-8, itself the existing H10 v2 `pool_160_hp4hn4` run; prefix-nestedness verified
by `sha256sum` on 2026-04-15 across `pool_160_hp4hn4/hp8hn8/hp16hn16` for `hp_01..hp_04` and
`hn_01..hn_04`. Analysis references `outputs/h10/evaluation-v2/pool_160_hp4hn4/run_{1..5}/`
directly. This is design-intentional reuse, but it means R2's CI is not an independent sample —
flagged at `results/h12-v2/analysis_summary.md:148`.

**Two transient failures** (`results/h12-v2/analysis_summary.md:168-180`): R3 run_3 tile
`K-35-053-3_Elenovo_x672_y3360.png` and R3 run_5 tile
`K-35-062-2_Rakovski_x4032_y336.png`, both Gemini 3 Flash JSON parse errors; each affected tile
drops 5→4 votes and still qualifies at the t=4 primary operating point.

**Why the tracking matrix says "In progress"**: git-verified. Commit `4be2d68a3` (2026-04-16
15:38, "feat(h12-v2): H12 HP:HN ratio experiment setup + protocol-errata E52") changed the H12
row from "Deferred (post-H10; HP pool exhausted)" to "In progress — h12-v2 ...". That is the
**last** edit to the file. The status was set at launch and never advanced to Complete.

## 4. Outcome

**Three-way null after BH-FDR — and the registered directional prediction is falsified.**

`results/h12-v2/analysis_summary.md:34-38`, re-verified against `results/h12-v2/fdr_summary.txt`
(tile-level permutation, greedy t = 4, 10 000 permutations, seed 42, BH-FDR q = 0.05 over 3
contrasts):

| Code | Contrast | F1 (a → b) | ΔF1 | raw p | BH-adj p | Signif? |
|---|---|---|---|---|---|---|
| R12 | R1 HN-heavy vs R2 balanced | 0.708 → 0.717 | −0.0087 | 0.7168 | 0.7168 | no |
| R23 | R2 balanced vs R3 HP-heavy | 0.717 → 0.688 | +0.0295 | 0.1667 | 0.5001 | no |
| R13 | R1 HN-heavy vs R3 HP-heavy | 0.708 → 0.688 | +0.0208 | 0.4060 | 0.6090 | no |

`fdr_summary.txt` closing block:

> ZERO contrasts are significant after BH-FDR correction at q=0.05. All three H12 v2 pairwise
> contrasts are NULL.

Per-condition metrics at greedy t = 4 (`results/h12-v2/analysis_summary.md:67-71`; matches
`results/conditions-manifest.json` `h12-v2::greedy-*` to 4 dp: 0.7084 / 0.7171 / 0.6876):

| Condition | HP:HN | F1 [95 % CI] | Precision | Recall | n detections |
|---|---|---|---|---|---|
| r1-hn-heavy | 2:6 | 0.708 [0.643, 0.761] | 0.825 | 0.621 | 240 |
| **r2-balanced** | **4:4** | **0.717 [0.661, 0.768]** | **0.843** | **0.624** | **236** |
| r3-hp-heavy | 6:2 | 0.688 [0.637, 0.740] | 0.776 | 0.618 | 254 |

**The registered directional prediction is contradicted.**
`results/h12-v2/analysis_summary.md:107-127` quotes the preregistration back at itself
(prereg lines 988-989: "Higher HP:HN ratio may improve recall ... Lower HP:HN ratio may improve
precision") and finds:

> R3's recall is **identical** to R1 and R2 (0.618 vs 0.621 vs 0.624), while its precision is
> **lower** by 0.05–0.07. Adding more hard positives does not increase recall in any direction
> we can see — it just adds more candidates, most of which are false positives. The mechanism
> the preregistration hypothesised (more HPs → more recognition → higher recall) is not
> supported by the data.

So: **fails to support** the null-of-no-difference being rejected (i.e. an overall null on F1),
**and separately contradicts** the registered directional mechanism. Both facts are reportable;
the second is arguably the more interesting one because a null on F1 plus a falsified mechanism
is stronger evidence than a null alone.

The registered secondary analysis ("Test whether ratio affects precision vs recall
differentially") **was** performed — see the P−R column at `analysis_summary.md:116-120`
(+0.204 / +0.219 / +0.158). The registered tertiary analysis ("Identify whether ratio interacts
with baseline error profile (FP-heavy vs FN-heavy tiles)") is, as far as I can find, **not
discharged**. `UNVERIFIED: would need a full read of results/h12-v2/analysis_summary.txt and
the permutation-t4 subtree to confirm no FP-heavy/FN-heavy stratification exists.`

**Cross-hypothesis closure**: `results/cross-hypothesis-library/permutation-t4/fdr_summary.json`
— verified in this session: `"n_conditions": 10`, `"n_pairs": 45`, `"operating_point": "greedy
t=4, 20 m buffer, 327-tile h10-384 test set"`, conditions spanning H8 v2's seven library
conditions plus H12 v2's three ratio conditions. `results/h12-v2/analysis_summary.md:22` states
"zero significant pairwise differences (min adj. p = 0.966)".

## 5. Deviations

| E | Type | Summary |
|---|---|---|
| **E13** (`protocol-errata.md:275-291`) | **Deviation** | "H12 (HP:HN ratio) deferred to post-H10." Original deferral (2026-02-02): with HP capped at 4, only HP-constant/HN-varying ratios were testable, confounding ratio with total count. "Moderate protocol impact." |
| **E52** (`protocol-errata.md:1468-1577`) | **Deviation + deferral resolution** | "H12 HP:HN ratio re-run under production carry-forward (384 px / v2 pipeline)." Resolves E13 (v2 register yields 108 HP / 57 HN, above the HP ≥ 6 needed for the 3:1 extreme); **relaxes the preregistered trigger** (H8 v2 was null); and applies ten parameter deviations to match H8 v2 / H10 v2 (tile 512→384 px, stride 448→336 px, T 0.0→0.7, thinking minimal→HIGH, K 10→5, standard→flex tier, caching off→on, crop 128→150 px, 60-tile holdout→327-tile manifest). |
| **E11** (`protocol-errata.md:239-254`) | Clarification | HP pool exhaustion — the upstream cause of E13. |
| **E49, E50** (`:1313`, `:1343`) | Deviation | Inherited via E52's "applied to match H8 v2 and H10 v2, per E49/E50/E51" (line 1520): H12 v2 uses H10's cold-start-mined pools and H10's 327-tile holdout. |
| **E51** (`protocol-errata.md:1366-1466`) | Deviation | H8 v2 re-run; supplies R2 (= Scale-8) and the shared pipeline. The **edge-of-raster exclusion fix** (lines 1451-1466) is what produced the 108 HP / 57 HN register H12 draws R1/R3 crops from. |
| **E45** (`protocol-errata.md:1097`) | Deviation | Micro-average F1 permutation statistic used for all three contrasts. |
| **E47, E54** | see cross-cutting table | 20 m buffer restored; 1 000-iteration bootstrap. |
| **Decision 11** (`decisions-log.md:363`, §"Implications for H9 (diversity) and H12 (ratio)" at `:442-450`) | Decision | The formal deferral record E13 implements. |
| **Decision 26** (`decisions-log.md:1159-1174`, "Retain Greedy-Ball Consensus Clustering as Primary; Validate via Weighted Boxes Fusion", dated 2026-04-13) | Decision | Greedy-ball 20 m retained as primary aggregation for all preregistered phases including H10/H12; equivalence validated on the H10/H12 `hp4hn4` configuration (ΔF1 = 0.0053, p = 0.6019, 327 tiles, 10 000 iterations). E52 line 1555 records greedy t = 4 as H12's headline aggregation per user preference (2026-04-15), with WBF variant C alongside. |

## 6. Proposed classification

**`preregistered-with-deviation`.**

*Case for*: the exact registered condition matrix was executed — R1 (2:6), R2 (4:4), R3 (6:2),
total hard = 8, matching `preregistration.md:996-1000` row for row. The registered primary
analysis (compare F1/P/R across ratios) and the registered secondary analysis (precision vs
recall differential) were both performed, with the three registered pairwise contrasts
FDR-corrected. Every departure is documented in E52 with a before/after parameter table. This
is about as clean a "registered design, executed, deviations logged" case as the study has.

*Case against*: two things give a reviewer purchase. (a) **The trigger was not met** — E52 says
so in terms ("Strictly read, the trigger is not met"). A hypothesis run in violation of its own
registered trigger is running outside its registered decision rule, which some reviewers treat
as taking it out of the preregistered frame entirely. (b) **The parameter deviations are
numerous and substantial** (ten rows in E52's table, including thinking level and K), and
crucially R2 is not a fresh run but a re-used H8 v2 / H10 v2 arm — so one third of the design
is a shared anchor rather than an independent replicate.

*Recommendation*: `preregistered-with-deviation`, `deviations: ["E13","E52","E49","E50","E51",
"E45"]`, with the trigger deviation stated in the paper's own words, not buried in a cited
erratum. `results/h12-v2/analysis_summary.md:147` already gives the honest framing to reuse:

> **Three-way null is preregistered-but-post-errata**: H12 v2 deviated from the preregistered
> H12 trigger ... The null is real; the framing as preregistered-closure requires the E52
> disclosure.

I do **not** recommend `exploratory` here: it would obscure the fact that the exact registered
matrix was executed, and it would let the falsified directional prediction — the most
interesting thing H12 produced — be read as an unregistered observation when it is a registered
mechanism failing at source.

## 7. Source discrepancies

1. **`hypothesis-tracking.md:31` says "In progress — h12-v2 ... | 2026-04-15"; the study
   completed 2026-04-16.** Believe `results/h12-v2/analysis_summary.md:4`, Obs 239
   (`working-notes.md:10075`), and `results/h12-v2/fdr_summary.txt`. Git-verified that the row
   was written at launch and never updated.
2. **`hypothesis-tracking.md:291`** ("H10-H13 not started") contradicts its own H12 row two
   screens earlier. The file is internally inconsistent.
3. **`docs/paper/results-outline.md:424`** records H12 as "in progress" (inherited from the
   tracking matrix). Stale by ~2 months.
4. **No `analysis_id` for H12** despite six registered conditions and a full results subtree.
   Same gap as H10.
5. **Trigger**: preregistration says run only if H8 shows library size matters
   (`preregistration.md:1010`); it was run despite an H8 v2 null. Believe **E52** — the
   deviation is disclosed and argued, not concealed. But the paper must say it in the paper.
6. **Aggregation-method framing**: E52 line 1555-1559 says greedy t = 4 is H12's
   primary/headline and WBF variant C the secondary "so H12 results remain directly comparable
   to H8 v2 and H10 v2 (both of which were analysed under WBF variant C as the primary
   method)". So H12's primary differs from its comparators' primary. Both are reported
   (`analysis_summary.md` §5 greedy, §6 WBF), and the WBF absolute F1s are not comparable
   across studies by design (§6, line 97: "Absolute WBF F1s here are not directly comparable to
   H8 v2 or H10 v2 greedy numbers"). Not an error, but a trap for anyone assembling a
   cross-study table.
7. **Minor**: `results/h12-v2/analysis_summary.md` lacks the revision banner / `## Changelog`
   required by the repo's Document Revision Policy for `results/**.md`, despite recording a
   "Polish level-up: 2026-04-24" in its header. Back-fill on touch.

## 8. Where reported

**NOT CURRENTLY REPORTED. This is a disclosure obligation.**

- `docs/paper/results-draft.md`: no mention of H12, HP:HN ratio, hard positives/negatives, or
  the library axis beyond § R2's Era-1 H8 reference.
- `docs/paper/results-outline.md`: H12 appears only in the D17 decision block (`:424`), and
  there it is described as "in progress".

The H12 summary itself supplies ready-to-use paper text
(`results/h12-v2/analysis_summary.md:61-63`, § 3.1 "Suggested paper text (Results — Era 3
library-design closure)"), which has never been used.

---

## Consolidated action list for the PI

**Corrections to `hypothesis-tracking.md`** (all four rows in this block are wrong or
misleading):

| Row | Current | Should be |
|---|---|---|
| H9 | "Complete (implicit) \| 2026-03-07" | Complete — explicit 5-condition (Track 1) / 4-condition (Track 2) experiment; 60-tile pilot 2026-03-08, 340-tile retest 2026-03-25; H9 rejected. Delete the "not run as separate experiments" paragraph (`:246-248`). |
| H10 | "Not started (HP pool exhausted) \| —" | Complete (H10 v2) 2026-04-15; null under PV; E49 + E50. |
| H11 | "Complete (384 pathway closed) \| 2026-03-15" | Complete — but the citable result is the 487-tile production evaluation (2026-03-22+), not the retracted 2026-03-15 pilot. |
| H12 | "In progress — h12-v2 \| 2026-04-15" | Complete (H12 v2) 2026-04-16; three-way null after BH-FDR; directional prediction falsified; E13 + E52. |

Plus `hypothesis-tracking.md:291` ("H10-H13 not started") and `execution-checklist.md:105`
(H9 "implicit", and "Phase 3b" vs "Phase 3c") and `execution-checklist.md:109` (Phase 5 blank).

**Corrections to `docs/paper/results-outline.md`**: `:424` and `:448` must stop listing H10 as
not-executed and H12 as in-progress.

**Register gaps**: create `analysis_id`s for H10 and H12 (and, outside this brief's scope, for
H8 v2), or record an explicit decision that the Era-3 library axis is out of scope for the
paper. As it stands the study has three preregistered factors with completed, null,
paid-for results that appear in no register and no draft.

**Schema**: `preregistered` enum has no `not-executed` value and cannot express
"registered-exploratory vs post-hoc". Amend, or carry the distinction in a separate
hypothesis-level table (D17 option A).

**Small factual fixes**: manifest `phase3c-diversity-calibration` outcome mis-attributes
p ≈ 0.06 to condition D (true value 0.1812); manifest `tile-size-sweep` outcome says 512 px
consensus+PV = 0.793 where the artefact says 0.792; `results/phase3c-diversity/
cross-track-comparison.md` § 4 says "487 tiles" where the scope is 340.
