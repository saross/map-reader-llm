# D17 — Evidence inventory for preregistered hypotheses H1–H4

**Compiled**: 2026-07-27. **Scope**: H1, H2, H3, H4 only.
**Repository**: `/home/shawn/Code/map-reader-llm` (read-only inspection; no files changed).

**Purpose**: Provide the evidence base for reclassifying the `preregistered`
field in `results/analyses-manifest.json`, which currently records
`"exploratory"` for all 18 registered analyses.

**Anchoring convention**: every checkable specific below carries
`path:line`. Quotations are verbatim from the file at that line unless
marked as paraphrase. Where I could not verify something inside this pass,
the text says **UNVERIFIED** and names the check that would settle it.

---

## Cross-cutting facts (apply to all four hypotheses)

### The preregistration's own confirmatory/exploratory partition

- `docs/methodology/preregistration/osf/preregistration.md:398` —
  section heading: `## 5. Confirmatory Hypotheses`. H1 (`:400`), H2
  (`:451`), H3 (`:497`) and H4 (`:534`) all sit inside this section, which
  runs to `:831`.
- `docs/methodology/preregistration/osf/preregistration.md:833–835` —
  `## 6. Exploratory Hypotheses` followed by
  *"These analyses will be conducted and reported but are not confirmatory.
  Results will be interpreted cautiously and framed as hypothesis-generating.
  Not included in FDR correction."* H1–H4 are **not** in this section.
- `docs/methodology/preregistration/osf/preregistration.md:1148` — table
  heading `### 7.1 Confirmatory Hypotheses (H1-H8)`, with H1–H4 at
  `:1152`–`:1155`.
- `docs/methodology/preregistration/osf/preregistration.md:274` — *"With 8
  confirmatory hypotheses tested on 60 tiles (79 mound symbols), statistical
  power is adequate…"* — i.e. the count of confirmatory hypotheses is 8
  (= H1–H8).
- `docs/methodology/preregistration/osf/preregistration.md:1985` —
  `**Confirmatory Hypotheses (H1-H8)**`, with H1–H4 rows at `:1989`–`:1992`.

**Conclusion**: on the preregistration's own classification, H1, H2, H3 and
H4 are unambiguously **confirmatory**. The manifest's blanket `"exploratory"`
is not supported by the registered document for any of the four.

### Registered statistical conventions (all four)

`docs/methodology/preregistration/osf/preregistration.md:268–270`:

> - **Per-hypothesis α**: 0.05
> - **Direction**: One-tailed for directional predictions; two-tailed for equivalence tests (H1)
> - **Multiple comparison correction**: Benjamini-Hochberg FDR at q = 0.05 across confirmatory hypotheses

`…:292` — *"All preregistered analyses reported **regardless of outcome**"*.
`…:294` — *"**Spatial tolerance sensitivity**: All primary results reported at 20m…"*.

### Corpus / K deviation affecting *every* Phase 2–3a result (E36)

`docs/methodology/preregistration/protocol-errata.md:878–890` — **E36**,
Type **Deviation** (`:883`), 2026-03-17, commit `f06afb7` (`:884`):

> The preregistered Phase 3 evaluation used a 60-tile holdout set. … The
> evaluation corpus was expanded to 340 tiles (569 ground truth mounds across
> 4 map sheets) to achieve adequate statistical power. All Phase 2a–3a
> conditions were re-run from scratch on the full corpus. K was reduced from
> 10 to 1–3 for single-pass conditions (340 tiles provide sufficient power)
> and retained at K=30 for consensus voting. (`:888`)

This single erratum means **no** currently-reported H1/H4 (and most H3)
result is at the preregistered K=10 / 60-tile design. It is the strongest
single argument for `preregistered-with-deviation` rather than
`preregistered` on H1, H3 and H4.

### FDR correction status (all four)

- `results/retest/pairwise-bootstrap-comparisons.json` `metadata.note`:
  *"Raw p-values — FDR correction deferred until all data available"*
  (file has `n_comparisons: 70`, `bootstrap_iterations: 1000`,
  `random_seed: 42`).
- `results/retest/retest-production-summary.md:209` — *"24 significant
  comparisons (p < 0.05, raw) out of 70 total pairwise tests. FDR correction
  is **deferred** until all experimental data are available."*
- `results/retest/retest-production-summary.md:278` (caveat 2) — *"FDR-corrected
  contrasts are **not yet in this doc**; they appear in per-phase permutation
  analyses…"*

So the registered BH-FDR-across-confirmatory-hypotheses correction was
**never completed as a single family**. The later leaderboard analyses apply
BH-FDR within their own round-robin boards instead. This is a live,
unresolved deviation that touches H1, H3 and H4 equally, and it is not
recorded as an E-number that I could find.

### Buffer changes affecting all four (E46 → E47)

- `…/protocol-errata.md:1163–1233` — **E46**, Type **Deviation** (`:1168`),
  2026-03-27: primary buffer changed 20 m → 30 m.
- `…/protocol-errata.md:1236–1288` — **E47**, Type
  *"Reversion (restores preregistered value)"* (`:1241`), 2026-03-29,
  `Supersedes | E46` (`:1243`): primary reverted to the preregistered 20 m.

Net effect on the current headline numbers: none — all H1–H4 headline values
below are at 20 m. E46/E47 are transient and cancel.

### Test-statistic change affecting all boards (E45)

`…/protocol-errata.md:1097–1159` — **E45**, Type **Deviation** (`:1102`),
2026-03-26: *"Pairwise permutation test statistic changed from macro-average
to micro-average F1"*. Preregistration ref Section 3.5 (`:1103`). All the
tiered leaderboards (`era1-*`, `n1-*`, `diversity-dividend-384`) use the
micro-average tile-swap statistic; the earlier per-phase bootstrap
comparisons do not.

### Bootstrap iteration count (E54)

`…/protocol-errata.md:1673–1680` — **E54**, Type **Clarification** (`:1678`),
2026-04-21, `Impact | None (preregistered methodology unchanged)` (`:1680`):
1 000 iterations for primary F1, 10 000 for narrow-effect post-hoc analyses.
The H1/H4 bootstraps used 1 000 (`results/retest/phase2a-evaluation.metadata.json`,
`in_script_constants.BOOTSTRAP_ITERATIONS: 1000`, `RANDOM_SEED: 42`).

### Schema note

`docs/manifest-schemas/analyses-manifest.schema.json:46–50` defines
`preregistered` with
`"enum": ["preregistered", "exploratory", "preregistered-with-deviation", null]`.
**`not-executed` is not a permitted value.** Where my proposal below is
"not executed", the schema-legal encoding is `null` (or omission), with the
fact recorded in prose — or the schema must be amended first.

---

## H1 — Modality and Elaboration Level Affects Detection Performance

### 1. As registered

**Heading**: `docs/methodology/preregistration/osf/preregistration.md:400` —
`### H1: Modality and Elaboration Level Affects Detection Performance`

**Predictions**, verbatim (`…:404–408`):

> **Predictions**:
>
> 1. Text modality will not significantly affect detection performance for this novel domain task
> 2. Verbose text will not significantly improve F1 compared to brief text
> 3. Image-based conditions will outperform text-only conditions

**Test** (`…:410–418`): five modality/elaboration levels — Image-only,
Brief-text, Brief-text+image, Verbose-text, Verbose-text+image (table at
`:412–418`). Brief-text and Verbose-text are text-only (`Images | No`).

**Registered analysis** (`…:434–443`), verbatim:

> **Analysis**:
>
> - Primary: Pairwise bootstrap comparisons across 5 M/E levels (95% CIs, FDR-corrected)
> - Planned contrasts:
>   - Image-only vs Brief+image (does adding text help?)
>   - Brief+image vs Verbose+image (does more detail help?)
>   - Brief-text vs Brief+image (do images help?)
>   - Text-only conditions vs Image-using conditions (modality effect)
> - Two-tailed tests for modality comparisons
> - One-tailed for elaboration: H0: verbose ≤ brief; H1: verbose > brief

**Advance rule** (`…:447`): *"**Advance to Stage 2 if**: Significant
differences detected between levels, suggesting modality/elaboration choices
matter for this domain."*

**Summary-table row** (`…:1152`):
`| H1 (M/E level) | Text modality no effect; verbose no benefit | Planned contrasts | Significant M/E effect or interaction |`

Plain-language restatement in
`docs/methodology/preregistration/analysis-summary.md:72` (`### H1:
Modality/Elaboration Level`), body at `:74–76` — design 5 conditions; analysis
*"Pairwise bootstrap comparisons across 5 levels (95% CIs, FDR-corrected)"*;
three planned contrasts.

### 2. Registered status

**Confirmatory.** H1 sits under `## 5. Confirmatory Hypotheses`
(`preregistration.md:398`) and appears in
`### 7.1 Confirmatory Hypotheses (H1-H8)` at `:1152`, and in the
implementation-mapping table `**Confirmatory Hypotheses (H1-H8)**` at
`:1985` with the H1 row at `:1989`. H1 also has a bespoke mention in the
statistical plan — *"two-tailed for equivalence tests (H1)"*
(`preregistration.md:269`).

### 3. Execution

**Run**: yes, twice — once on the 60-tile holdout (Phase 2a, 2026-02-05/06)
and then re-run from scratch on the 340-tile corpus under E36.

- Run ID: **`retest-phase2a`** — `results/runs-manifest.json:593`,
  `"primary_hypothesis": "H1"` (`:595`), `directory_path`
  `outputs/retest/phase2a` (`:594`), `run_type` `single-pass` (`:598`),
  `tile_size_px` 512 (`:599`), scope `era-1-340`, `n_test_tiles` 340
  (`:603`, `:605`).
- Condition IDs (5), from `results/conditions-manifest.json` (queried
  programmatically; all `architecture: single-pass`, `n_passes: 3`):
  `retest-phase2a::image-only`, `::brief-text`, `::brief-text-image`,
  `::verbose-text`, `::verbose-text-image`.
- Analysis IDs that carry `"H1"` in `hypothesis_refs`
  (`results/analyses-manifest.json`), exhaustively — there are exactly three:
  1. **`n1-baseline-matrix-384`** — id at `:7`; `hypothesis_refs` `["H1","H6","H7"]`
     at `:29–33`; `preregistered: "exploratory"` at `:34`; `deviations: ["E57"]`
     at `:35–37`.
  2. **`era1-single-pass-baseline-matrix`** — id at `:315`; `hypothesis_refs`
     `["H1","H4","H5","H7","H8"]` at `:355–361`; `preregistered: "exploratory"`
     at `:362`; `deviations: []` at `:363`.
  3. **`era1-leaderboard`** — id at `:402`; `hypothesis_refs`
     `["H1","H3","H4","H5","H7","H8","H9"]` at `:488–496`;
     `preregistered: "exploratory"` at `:497`; `deviations: []` at `:498`.

**Important**: none of these three is *the registered H1 test*. They are
multi-hypothesis leaderboards. The registered pairwise-bootstrap H1 analysis
lives outside the analyses manifest, in:

- `results/retest/phase2a-evaluation.json` — per-condition F1/P/R plus a
  `pairwise` array of all 10 pairwise contrasts with bootstrap CIs and a
  `significant` boolean. Sidecar `results/retest/phase2a-evaluation.metadata.json`
  records `generated_by_script: scripts/evaluate_retest_all.py`,
  1 000 bootstrap iterations, seed 42, percentile method, tile-level resampling.
- `results/retest/pairwise-bootstrap-comparisons.json` — 10 comparisons tagged
  `"phase": "Phase 2a: H1 Modality"`, with raw p-values.
- `results/retest/retest-production-summary.md:40–50` (§3 Phase 2a table) and
  `:211–217` (§11.1 pairwise highlights).

**Partial-execution caveats**: (a) the five M/E cells were executed, so the
factor is complete; (b) K=3 not K=10 (E36); (c) the *first* execution of
brief-text and verbose-text was invalid (E25, below) and was re-run.

### 4. Outcome

**340-tile retest, F1@20 m** (`results/retest/retest-production-summary.md:44–48`,
cross-checked against `results/conditions-manifest.json` metrics for the same
five conditions — values agree to 4 dp):

| Condition | F1 | 95 % CI | P | R | K |
|---|---:|:---:|---:|---:|---:|
| brief-text | 0.5518 | [0.477, 0.595] | 0.4336 | 0.7588 | 3 |
| brief-text-image | 0.5220 | [0.469, 0.564] | 0.4392 | 0.6432 | 3 |
| verbose-text | 0.5016 | [0.443, 0.556] | 0.3928 | 0.6939 | 3 |
| verbose-text-image | 0.5169 | [0.467, 0.560] | 0.4343 | 0.6382 | 3 |
| image-only | 0.4693 | [0.401, 0.502] | 0.3829 | 0.6061 | 3 |

Pairwise contrasts (from `results/retest/pairwise-bootstrap-comparisons.json`,
raw p; 3 of 10 significant):

- brief-text > image-only, ΔF1 +0.0878, p = 0.004 — **significant (raw)**
- brief-text-image > image-only, ΔF1 +0.0654, p = 0.006 — **significant (raw)**
- image-only < verbose-text-image, ΔF1 −0.0632, p = 0.004 — **significant (raw)**
- brief-text vs brief-text-image, ΔF1 +0.0225, p = 0.38 — ns
- brief-text vs verbose-text, ΔF1 +0.0369, p = 0.106 — ns
- brief-text-image vs verbose-text-image, ΔF1 +0.0021, p = 0.94 — ns
- image-only vs verbose-text, ΔF1 −0.0510, p = 0.066 — ns
- brief-text vs verbose-text-image, +0.0246, p = 0.428 — ns
- brief-text-image vs verbose-text, +0.0144, p = 0.558 — ns
- verbose-text vs verbose-text-image, −0.0122, p = 0.658 — ns

Narrative (`results/retest/retest-production-summary.md:50`): *"Text-only
conditions outperform image-only… The brief-text vs image-only difference is
significant (ΔF1 = +0.088, p = 0.004). Adding images to text does not improve
F1 and tends to reduce recall. No significant difference between brief-text
and verbose-text (p = 0.106)…"*

**Verdict against the three registered predictions:**

1. *"Text modality will not significantly affect detection performance"* —
   **contradicted**. Text-only vs image-only is significant at raw p; the
   modality effect is real and in the direction opposite to prediction 3.
2. *"Verbose text will not significantly improve F1 compared to brief text"* —
   **supported** (brief > verbose numerically; p = 0.106 ns). Note the
   registered one-tailed direction was H1: verbose > brief; verbose is
   *lower*, so H0 is retained comfortably.
3. *"Image-based conditions will outperform text-only conditions"* —
   **contradicted, decisively and in the reverse direction**. This is the
   study's first substantive scientific surprise, logged as
   `docs/notes/working-notes.md:1833` (Observation 103, *"Text-only
   outperforms visual few-shot — a foundational assumption challenged"*),
   with the 60-tile numbers at `:1837–1843` (brief-text 0.5425 top,
   image-only 0.4252 bottom) and the explicit statement at `:1845`:
   *"This result contradicts the H1 prediction that image-based conditions
   would outperform text-only conditions."*

**Later, larger-instrument corroboration**: the Era-2 384 px single-pass board
(`analysis n1-baseline-matrix-384`, outcome at `results/analyses-manifest.json:43`)
finds *"the text-over-image advantage holds at matched settings (best Pro text
0.804 vs best Pro image 0.666)"*, but with the important qualifier that
*"H1 resolves metric-dependently — text wins F1@20 m localisation … while image
wins MCC tile-discrimination"* (`:38`).

### 5. Deviations touching H1

| E | Type | Line | One-line summary |
|---|---|---|---|
| **E14** | Clarification | `protocol-errata.md:294`, type at `:299` | Verbose instruction grew to 779 words, ~80 above the registered range; noted as *"conservative deviation"* that could only **amplify** the H1 M/E effect (`:307`). |
| **E16** | Clarification | `:335`, type at `:340` | All 10 `detect_*.md` prompts reworded from cartographic feature names to visual descriptions; *"factor design (H5 levels, M/E levels) … unchanged"* (`:349`). |
| **E17** | Correction | `:355`, type at `:360` | Erroneous `passes: 5` multiplier removed from `studies/phase2a-h1-modality.yaml` and four siblings; restores the registered single-pass protocol (`:370` *"Protocol impact: None"*). |
| **E18** | Clarification | `:374` | Config-naming convention: the unsuffixed config *is* the H5=Minimal variant (`:385` cites *"H1 baseline. M/E=Image-only, H5=Minimal"`). |
| **E25** | **Correction** | `:543`, type at `:548` | **The material one.** *"Modality manipulation not implemented — text-only conditions received images"*: `4_detect_mounds_batch.py` sent all 17 example images regardless of condition, so brief-text and verbose-text were not text-only. 20 runs invalidated (`:550`), 1 200 API calls (`:566`); fixed via `include_example_images` and **re-run** (`:568–574`); *"Protocol impact: None. The preregistered design is unchanged"* (`:576`). |
| **E26** | Correction | `:582`, type at `:587` | Bootstrap CIs were systematically deflated by reference de-duplication on resampled tiles; 7 bootstrap functions refactored; point estimates unaffected (`:606`). Affects the CIs quoted for H1. |
| **E27** | **Deviation** | `:617`, type at `:622`, Decision 16 | Dual-track carry-forward *because of* the H1 result: preregistered OFAT specifies a single optimal M/E carried forward; two were carried (brief-text-image Track 1, brief-text Track 2). Downstream, not upstream, of the H1 test itself. |
| **E36** | **Deviation** | `:878`, type at `:883` | 60-tile holdout → 340-tile corpus; K 10 → 1–3 for single-pass. All Phase 2a conditions re-run. |
| **E45** | Deviation | `:1097` | Permutation statistic macro → micro average (affects the leaderboard-era H1 boards, not the phase2a bootstrap). |
| **E46 / E47** | Deviation / Reversion | `:1163` / `:1236` | Primary buffer 20 → 30 m, then reverted to the registered 20 m. Net zero. |
| **E54** | Clarification | `:1673` | Bootstrap iterations: 1 000 primary (as used here), 10 000 for narrow-effect post-hoc. |
| **E57** | Metadata correction + billing reconciliation | `:1782`, impact at `:1789` | Four "Pro" cells in the 384 px N=1 board were dispatched as Flash; genuine-Pro re-run `n1-pro-rerun-384` replaced them. Listed as the sole `deviations` entry on `n1-baseline-matrix-384` (`results/analyses-manifest.json:36`). Touches the Era-2 H1 board, not the Era-1 registered test. |

Not found: any erratum recording that the registered
BH-FDR-across-confirmatory-hypotheses correction was never applied.

### 6. Proposed classification

**`preregistered-with-deviation`.**

*For `preregistered`*: the five registered M/E cells were run; the registered
analysis (pairwise bootstrap with 95 % CIs across all 5 levels) was executed
and is on disk; all three planned contrasts that the analysis-summary names
are computable and reported; the outcome is reported regardless of its being
contrary to prediction (satisfying `preregistration.md:292`).

*For `preregistered-with-deviation`* (which I prefer): three separate,
errata-documented departures apply to the numbers actually reported —
E36 (corpus 60 → 340 tiles and K 10 → 3, a change to the registered
evaluation protocol at `preregistration.md:315`), E25 (the first execution
was invalid and had to be re-run; a correction, but one the reader must know
about to interpret the run history), and E14 (verbose text out of registered
word-count range, biasing the brief-vs-verbose contrast). Additionally the
registered FDR correction across confirmatory hypotheses was deferred and,
as far as I can verify, never completed — so the reported p-values are raw.

*Against `exploratory`*: nothing in the preregistration supports it. The
current manifest value is unjustified.

**Caveat on which analysis row gets the label.** The three H1-tagged manifest
rows are all leaderboards, not the registered H1 test. If the manifest is to
carry an honest `preregistered-with-deviation` for H1, the cleanest fix is
to register the Phase 2a pairwise-bootstrap analysis
(`results/retest/phase2a-evaluation.json`) as its own analysis row. Failing
that, `era1-single-pass-baseline-matrix` is the closest existing home
(it contains all five `retest-phase2a::*` conditions:
`results/analyses-manifest.json:318–322`).

### 7. Source discrepancies

1. **Manifest vs preregistration** — manifest says `exploratory` on all three
   H1 rows; preregistration says confirmatory. **Believe the preregistration**
   (it is the registered, timestamped document; OSF registration
   2026-01-31 23:54 UTC per `execution-checklist.md:61`).
2. **`hypothesis-tracking.md:13`** — `| H1 | Modality/Elaboration Level | M/E | 2a | Complete | 2026-02-06 |`,
   under the heading `## Confirmatory Hypotheses (H1-H8)` (`:9`). This
   **agrees** with the preregistration and **contradicts** the manifest. The
   doc is stale (`**Last updated**: 2026-04-15`, `:5`) and its H1 detail block
   (`:40–53`) predates E36 — it says *"Status (2026-02-08): Phase 2a complete"*
   with no mention of the 340-tile re-run. Believe it on classification;
   do not believe it on execution detail.
3. **`hypothesis-tracking.md:44`** says the H1 optimal level was *"identified
   and carried forward"* — this is only true modulo E27's dual-track
   deviation, which the tracking doc does not mention in the H1 block.
4. **`era1-single-pass-baseline-matrix` `deviations: []`**
   (`results/analyses-manifest.json:363`) — factually wrong: E36 at minimum,
   and E25/E29/E30/E31 for the constituent phases, apply.

### 8. Where reported

`docs/paper/results-draft.md` § R2 (`:85–110`), specifically:

- `:88` — *"This subsection compresses the preregistered single-factor results
  (H1, H4, H5, H7, H8) into one board-led narrative"*.
- `:102–104` — *"The single-factor manipulations the study preregistered —
  modality and prompt elaboration (H1), example ordering (H4), … — all land
  inside or near that tie"*.
- `:105–107` — *"Two robust patterns do emerge: text-modality prompts dominate
  image-only prompts at the bottom of the board…"* (the H1 finding, unlabelled).

**Gap**: the H1 *contradiction of the registered prediction* is not stated in
the draft. § R2 reports the pattern but does not say "H1 prediction 3 was
contradicted". Given `preregistration.md:292` ("all preregistered analyses
reported regardless of outcome") this is worth surfacing explicitly.

---

## H2 — Two-Stage Pipelines Do Not Improve Detection

### 1. As registered

**Heading**: `preregistration.md:451` — `### H2: Two-Stage Pipelines Do Not Improve Detection`

**Status line**, verbatim (`…:453`): `**Status**: Confirmatory (architectural)`

**Prediction**, verbatim (`…:461`):

> **Prediction**: Neither two-stage architecture will improve F1 over single-stage detection with voting.

**Test** (`…:463–469`): three conditions —
`A (baseline) | Single-stage | Optimal config with consensus voting`;
`B | Coarse-to-fine | Liberal proposer → strict verifier`;
`C | Fine-to-coarse | Standard detection → context-expanded re-query for uncertain cases`.

**Registered analysis** (`…:486–491`), verbatim:

> **Analysis**:
>
> - One-tailed tests: H0: two-stage ≥ single-stage; H1: two-stage < single-stage
> - Prediction is that H0 will not be rejected for either architecture
>
> **Stopping rule**: Two-stage architectures will only be pursued further if
> either demonstrates F1 at least 0.05 higher than single-stage. …

**Advance rule** (`…:493`): *"Either two-stage approach shows F1 improvement of
at least 0.05 over single-stage (would contradict preliminary findings)."*

**Summary-table row** (`…:1153`):
`| H2 (two-stage) | Neither architecture improves over single-stage | Compare F1 | Either direction shows ≥0.05 F1 improvement |`

**Implementation mapping** (`…:2015`): H2 →
`propose_*.json` + `verify_*.json` (coarse-to-fine);
`detect_*.json` + `expand_*.json` (fine-to-coarse).

### 2. Registered status

**Confirmatory**, and uniquely among H1–H4 it says so in its own body text:
`preregistration.md:453` — `**Status**: Confirmatory (architectural)`.
Reinforced by `docs/methodology/preregistration/execution-plan.md:743` —
*"H9 is exploratory; H2 and H6 remain confirmatory"* — and by that document's
version history at `:814`: *"fixed H2/H6 status (confirmatory, not exploratory)"*.

### 3. Execution

**Condition B (coarse-to-fine): executed, extensively, and far beyond the
registered scope.**
**Condition C (fine-to-coarse): NOT executed.**

Evidence for C not being executed:

- `docs/methodology/preregistration/hypothesis-tracking.md:86–87` —
  *"**Note**: Fine-to-coarse (H2-C) was not tested — the coarse-to-fine results
  were strong enough that context expansion was deprioritised."*
- Corroboration in the filesystem: `prompts/configs/` contains
  `propose_*.json` and `verify_*.json` families but **no `expand_*.json`**;
  `prompts/system-instructions/` contains `propose_brief.md`,
  `verify_*.md` but **no `expand_*.md`**. The registered implementation
  mapping at `preregistration.md:2015` requires `expand_*.json` for
  fine-to-coarse. (Verified by directory listing this session.)
- The execution plan's own Phase 3d design (`execution-plan.md:585–592`)
  already reduces the test to two conditions — *"Condition A: Single-stage
  detection… Condition B: Proposer → Verifier pipeline"* — no C.
- The fine-to-coarse *prompt* does exist in the appendix
  (`preregistration-appendix-prompts.md:1132`, *"Status: Confirmatory —
  prompt to be used in H2 fine-to-coarse direction testing"*), so this is a
  non-execution, not a non-registration.

Runs and conditions for Condition B:

- Run IDs with `primary_hypothesis: "H2"` in `results/runs-manifest.json`:
  **`verifier-t-pilot`** (`:923`) and **`verifier-robustness`** (`:956`,
  `also_informs: ["H3"]`). Both 384 px, `era-2-487` scope.
- The main PV runs are registered under H11, not H2:
  `proposer-verifier-384` (`:382`, `primary_hypothesis: "H11"`,
  `also_informs: ["pv-strategy"]`), `proposer-verifier-512` (`:418`, same),
  `pv-diag-384` (`:484`, `primary_hypothesis: "H11"`,
  `also_informs: ["H3","H8","pv-strategy","consensus-n-sweep","flash-vs-pro"]`),
  `pv-diag-256` (`:453`), `flash35-pv-2x2` (`:989`).
- Analysis IDs carrying `"H2"` in `hypothesis_refs`
  (`results/analyses-manifest.json`), exhaustively — six:
  1. `verifier-robustness-matrix` — id `:582`, refs `["H2"]` `:592–594`,
     `preregistered: "exploratory"` `:595`, `deviations: []` `:596`.
  2. `pass-budget-pareto` — id `:624`, refs `["H2","H3"]` `:633–635`,
     `"exploratory"` `:637`.
  3. `min-vs-high-thinking-pv` — id `:665`, refs `["H2","H3"]` `:676–679`,
     `"exploratory"` `:680`.
  4. `pass-budget-pareto-v2` — id `:710`, refs `["H2","H3"]` `:721–724`,
     `"exploratory"` `:725`.
  5. `flash35-model-roles` — id `:756`, refs `["H2"]` `:765–767`,
     `"exploratory"` `:768`.
  6. `unswept-pools-completeness` — id `:793`, refs `["H2","H11"]` `:815–818`,
     `"exploratory"` `:819`.

**Critical structural finding**: *none of those six is the registered H2
contrast.* Every one is an internal-to-PV robustness, cost, model-role or
completeness study — legitimately exploratory. The analysis that actually
performs the registered comparison (two-stage vs single-stage-with-voting) is
**`era1-leaderboard`** (id `results/analyses-manifest.json:402`), whose
`hypothesis_refs` at `:488–496` are `["H1","H3","H4","H5","H7","H8","H9"]` —
**H2 is missing**. Its outcome text at `:503` states
*"PROPOSER-VERIFIER IS THE SINGLE BEST ERA-1 ARCHITECTURE"*. That is the H2
result, sitting on a row that does not claim H2.

### 4. Outcome

**The registered prediction is contradicted, by a wide margin.**

Chronologically:

- **Pilot (Phase 3c/3d, 60-tile holdout)**:
  `results/phase3d-pilot-results.md:1` (`# Phase 3d Pilot Results — H2
  Two-Stage Pipeline`), `:91–93` — *"All three verifier strategies beat the
  single-stage baseline on both tracks. The improvement exceeds the
  preregistered stopping criterion of ≥0.05 ΔF1 by a wide margin (+0.086 to
  +0.138)."* Go/No-Go at `:140` — *"**GO for full Phase 3d.**"*.
  Recorded in `execution-checklist.md:106`:
  *"Phase 3c: H2 Two-Stage | 2026-03-08 | 2026-03-09 | Pilot: adversarial
  verifier improves F1 by +0.086 to +0.138 vs single-stage baseline; GO for
  full experiment"*.
  **Caveat**: these pilot numbers are superseded — E33 (`protocol-errata.md:768`,
  Type Correction `:773`) lists *"Phase 3d pilot (Session 43)"* among affected
  results (`:783`) and requires re-run (`:791`).
- **Era-1 definitive board** (`era1-leaderboard`, outcome at
  `results/analyses-manifest.json:503`): 82 cells (36 single-pass + 42
  consensus + 4 verified-PV), tile-swap permutation, 10 000 perms, seed 42,
  BH-FDR q = 0.05, 2 351/3 321 pairs significant → 10 tiers. Tier 1 is a
  **sole** leader: `verified-adv-text-high-t1.0-n30-23of30`, F1 0.792,
  MCC 0.676; *"the verifier lifts the consensus champion (0.775 -> 0.792)
  just enough to break the old 6-way HIGH-consensus tie"*.
- **Study headline** (`tile-size-sweep` outcome,
  `results/analyses-manifest.json:564`): consensus + verifier at 384 px
  = **0.890** vs consensus-only 0.814 and single-pass 0.520 at the same size;
  and the 256 px rescue, *"256 consensus jumps from 0.460 consensus-only …
  to 0.856 consensus+PV (+0.396)"*.

Against the registered stopping rule (*"F1 at least 0.05 higher than
single-stage"*, `preregistration.md:491`): the observed lift is roughly
+0.06 to +0.40 F1 depending on tile size and baseline. **H0 is rejected;
the prediction fails.** By the registered logic (`:493`) this "advances to
Stage 2", which is exactly what the project did (the entire PV programme).

**Fine-to-coarse (Condition C)**: **unresolved — not executed.** No statement
can be made about it.

### 5. Deviations touching H2

| E | Type | Line | One-line summary |
|---|---|---|---|
| **E33** | Correction | `:768`, type `:773` | Verifier crops read from tile PNGs, not source GeoTIFFs → edge-truncated crops; all Phase 3d PV results affected (`:781–787`) and re-run; originals archived to `archive/phase3d-pre-e33/` (`:791`). |
| **E37** | **Deviation** | `:894`, type `:899` | *"Proposer-Verifier (PV) pipeline introduced as post-hoc extension"* — *"The preregistration did not include a two-stage Proposer-Verifier pipeline"* (`:904`); *"an extension beyond the preregistered design, not a replacement. All preregistered analyses (H1–H9) are evaluated independently of PV"* (`:908`). **See discrepancy note below — this framing is contestable.** |
| **E38** | Clarification | `:912`, type `:917` | Dual-mode (batch/real-time) API architecture for the PV pipeline; *"no effect on results"* (`:924`). |
| **E39** | Clarification/(see doc) | `:928` | Verifier strategy equivalence confirmed at production scale. |
| **E55** | (see doc) | `:1711`, impact `:1718` | Verifier-t-pilot T0.5/T1.0 metadata under-recorded the swept temperature; *"Impact | Low — exploratory pilot (H2)"*. |
| **E56** | (see doc) | `:1746` | Verifier probability-threshold operating points are in-sample (test-set-selected), not calibrated; blast radius listed at `:1761`; **headline binary-verdict PV results NOT affected** (`:1761`, `:1765`). |
| **E36** | Deviation | `:878` | The 340-tile corpus change also governs the Era-1 PV cells. |
| **E45/E46/E47/E54** | as above | | Statistic, buffer, and bootstrap-iteration errata apply to the PV boards as to everything else. |

Also relevant though not an E-number: `execution-plan.md:585–592` silently
reduces H2 from three conditions to two (drops fine-to-coarse). That
reduction is *not* recorded in `protocol-errata.md` under any E-number I could
find — **this looks like an undocumented protocol deviation.**

### 6. Proposed classification

**Split verdict. I recommend recording H2 as two distinct things:**

- **H2 Condition B (coarse-to-fine / proposer–verifier) vs Condition A
  (single-stage with voting): `preregistered-with-deviation`.**
- **H2 Condition C (fine-to-coarse / context expansion): not executed**
  (schema-legal encoding: `null`, with a prose note; see the schema caveat in
  the cross-cutting section).

*For `preregistered-with-deviation` on B*: the registered prediction, the
registered comparison (two-stage vs single-stage-with-voting), and the
registered decision rule (≥ 0.05 ΔF1) were all specified in advance and all
were actually evaluated. The prediction failed and the decision rule fired.
That is a confirmatory test with a null-refuting result — the most valuable
kind to own. The deviations are E33 (implementation correction requiring
re-run), E36 (corpus/K), E37 (the *specific* verifier design was developed
post hoc, even though the *architecture class* was registered), and the
undocumented drop of Condition C.

*Arguing the other side, honestly*: E37 (`protocol-errata.md:908`) itself
asserts *"The PV pipeline is an extension beyond the preregistered design…
The PV results are reported as an additional finding"* — i.e. the project's
own erratum frames PV as post-hoc, which supports `exploratory`. I think that
framing is **too modest and partly wrong**: `preregistration.md:468` registers
Condition B as *"Coarse-to-fine | Liberal proposer → strict verifier"*, and
`:471–474` registers the implementation as *"Stage 1: Detection with lower
confidence threshold; Stage 2: Crop candidate regions, verify with focused
prompt"* — which is precisely the PV pipeline. What was post hoc is the
adversarial prompt framing, the probability-score output, and the tuning
programme; not the architecture or the hypothesis. So: the *architectural
contrast* is preregistered; the *specific verifier optimisation* is
exploratory.

*The six currently H2-tagged analyses*: I would **leave all six as
`exploratory`** — they genuinely are (verifier temperature/thinking matrices,
pass-budget Pareto frontiers, model-role 2×2s, completeness sweeps). None of
them tests the registered H2 proposition. The reclassification should instead
attach to `era1-leaderboard` (and/or `tile-size-sweep`), which is where the
registered contrast actually lives — and those rows need `"H2"` added to
`hypothesis_refs` first.

### 7. Source discrepancies

1. **`analysis-summary.md:82`** — under `### H2: Two-Stage Pipeline` (`:78`):
   *"**Note**: Treated as exploratory due to preliminary evidence of no
   benefit"*. This **directly contradicts** `preregistration.md:453`
   (`**Status**: Confirmatory (architectural)`) and `execution-plan.md:743`
   (*"H2 and H6 remain confirmatory"*).
   **Believe the preregistration.** `analysis-summary.md` is described as a
   *"Plain-language overview … for non-specialist readers"* (`:3`), is dated
   `**Last updated**: 2026-01-31` (`:5`), and `execution-plan.md:814`
   explicitly records a prior fix of exactly this error elsewhere
   (*"fixed H2/H6 status (confirmatory, not exploratory)"*) — the
   analysis-summary evidently did not receive that fix. **This is the single
   most likely origin of the manifest's `exploratory` value for H2, and it is
   a documented, already-corrected-elsewhere error.**
2. **`preregistration-coverage.md:77–84`** — `### 3.2 H2 Analysis (Contrasts
   within Factorial)` describes H2 as brief-vs-verbose *elaboration*
   contrasts, which is a different hypothesis entirely. Yet the same document
   at `:162` has `| Pipeline architecture | P | 2 (single-stage, two-stage) | H2 |`.
   The coverage doc is internally inconsistent; `:264` (v2.1 changelog) shows
   the numbering was resequenced and §3.2 was evidently not updated.
   **Believe `preregistration.md` and coverage `:162`.**
3. **`hypothesis-tracking.md:14`** — `| H2 | Two-Stage Pipelines | Architecture | 3c/3d | **Complete** | 2026-03-11 |`
   and `:61–64`: *"The preregistered null prediction (two-stage will not
   improve) was **contradicted** with large effect size."* This is right on
   direction but stale on magnitude: `:75–77` quotes *"F1=0.796 (adversarial
   verifier, text-only, 512 tiles)"* and a *"corrected v2 result (F1=0.732)"*,
   both superseded by the Era-1 board (0.792) and the 384 px headline (0.890).
   Also `:14` says "Complete" without flagging that Condition C was never run
   — the caveat is only 70 lines later at `:86`.
4. **`era1-leaderboard` omits `"H2"` from `hypothesis_refs`**
   (`results/analyses-manifest.json:488–496`) despite its outcome being the
   H2 result. Manifest defect.
5. `results/retest/retest-production-summary.md:320` (§14.5 suggested paper
   text) still says *"Gemini 2.0 Flash"*, which that document's own changelog
   at `:279`/`:379` corrects to `gemini-3-flash`. Out of scope for H2 but
   worth a fix while the file is open.

### 8. Where reported

`docs/paper/results-draft.md` § R4, `:133–166`:

- `:133` — heading: *"R4. The proposer–verifier architecture is the best
  architecture on every tile size"*.
- `:135–138` — *"Adding an adversarial verification stage (H2) … is the single
  best architectural move in the study, on every tile size tested."*
- `:140–147` — Era-1 board: sole Tier-1 leader F1 0.792 / MCC 0.676;
  `era1-leaderboard` cited.
- `:160–166` — study headline F1@20 m 0.890 / MCC 0.790.

**Gap**: the draft nowhere states that H2's registered prediction was
*"Neither two-stage architecture will improve F1"* and was refuted. Framing
this as a preregistered prediction that failed is stronger than framing it as
a discovery. Nor does the draft note that fine-to-coarse was never tested.

---

## H3 — Consensus Voting Improves F1

### 1. As registered

**Heading**: `preregistration.md:497` — `### H3: Consensus Voting Improves F1`

**Prediction**, verbatim (`…:501`):

> **Prediction**: Consensus voting will improve F1 compared to single-pass detection.

**Test** (`…:503–515`): primary data source is *"The K=10 independent runs from
the main factorial"*; pool sizes N=5 (runs 1–5 or 6–10) and N=10 (all runs),
thresholds 1…N (table `:507–510`); plus *"**Extended voting (N=30)**:
Additional 20 runs at optimal configuration"* (`:512`) enabling an N=30
threshold sweep and cost-benefit characterisation (`:514–515`).

**Registered analysis** (`…:517–522`), verbatim:

> **Analysis**:
>
> - Compare single-pass mean F1 vs voted F1 at each (N, threshold) combination
> - Generate threshold sweep curves (F1, precision, recall vs threshold for each N)
> - Identify optimal (N, threshold) balancing performance and cost
> - One-tailed test for primary comparison: H0: voting ≤ single-pass; H1: voting > single-pass

Plus cost-efficiency analysis (`…:524–528`) and
*"**Advance to Stage 2 if**: Significant improvement confirmed."* (`…:530`).

**Summary-table row** (`…:1154`):
`| H3 (consensus voting) | Voting improves over single-pass | One-tailed | Significant improvement |`

**Evaluation-protocol integration** (`…:329`): *"**H3 integration**: The K=10
protocol directly supports H3 analysis. Additional N=30 runs are conducted at
the optimal configuration to extend the voting characterisation."*
Rationale for independent runs (`…:317`): *"Independent runs provide unbiased
estimates of each factor's effect without assuming voting (which is itself
under test in H3)."*

Plain-language version, `analysis-summary.md:84` (`### H3: Consensus Voting`),
body at `:86–88`: *"**Analysis**: Compare voted F1 vs single-pass mean F1"* /
*"**Output**: Threshold sweep curves showing optimal (N, threshold)
combinations"* — this exact wording is later invoked as the licence for
best-operating-point reporting (see E56 Update below).

### 2. Registered status

**Confirmatory.** Under `## 5. Confirmatory Hypotheses`
(`preregistration.md:398`); row in `### 7.1 Confirmatory Hypotheses (H1-H8)`
at `:1154`; implementation-mapping row under `**Confirmatory Hypotheses
(H1-H8)**` at `:1991`. H3 has no explicit in-body `**Status**:` line (unlike
H2 and H4), so its classification rests on section placement and the tables.

### 3. Execution

**Run: yes, and more thoroughly than registered** (multiple eras, multiple
thinking levels, N up to 30).

Run IDs with `primary_hypothesis: "H3"` (`results/runs-manifest.json`):

- **`retest-phase3a`** — `:758`, 512 px, `era-1-340`, `run_type: mixed`.
- **`retest-phase3a-high`** — `:791`, 512 px, `era-1-340`.
- **`retest-phase3a-replication`** — `:824`, 512 px, `era-1-340`,
  `run_type: consensus`.

Additional runs that inform H3 via `also_informs`:

- **`pv-diag-384`** — `:484`, `also_informs` includes `"H3"` and
  `"consensus-n-sweep"`, 384 px, `era-2-487`.
- **`verifier-robustness`** — `:956`, `also_informs: ["H3"]`.

Analysis IDs carrying `"H3"` in `hypothesis_refs`
(`results/analyses-manifest.json`), exhaustively — nine:

1. **`pv-diag-384-consensus-calibration`** — id `:58`, refs `["H3"]` `:91–93`,
   `"exploratory"` `:94`, `deviations: []` `:95`. 29 configs, sweep.
2. **`diversity-dividend-384`** — id `:113`, refs `["H3"]` `:139–141`,
   `"exploratory"` `:142`, `deviations` (three prose entries) `:143–147`.
3. **`phase3a-consensus-calibration`** — id `:169`, refs `["H3"]` `:191–193`,
   `"exploratory"` `:194`. 18 configs, Era-1.
4. **`phase3a-high-consensus-calibration`** — id `:213`, refs `["H3"]`
   `:226–228`, `"exploratory"` `:229`. 9 HIGH-thinking text configs.
5. **`phase3a-replication-thinking-calibration`** — id `:248`, refs `["H3"]`
   `:258–260`, `"exploratory"` `:261`.
6. **`era1-leaderboard`** — id `:402`, refs include `"H3"` `:488–496`,
   `"exploratory"` `:497`.
7. **`pass-budget-pareto`** — id `:624`, refs `["H2","H3"]`, `"exploratory"` `:637`.
8. **`min-vs-high-thinking-pv`** — id `:665`, refs `["H2","H3"]`, `"exploratory"` `:680`.
9. **`pass-budget-pareto-v2`** — id `:710`, refs `["H2","H3"]`, `"exploratory"` `:725`.

Condition IDs: too numerous to list exhaustively; representative registered
consensus cells include `retest-phase3a::text-t0.7-n30-24of30`,
`retest-phase3a::image-t0.7-n30-18of30` (both in
`results/analyses-manifest.json:186`, `:177`),
`retest-phase3a-replication::text-high-t0.7-n30-21of30` (`:253`),
`retest-phase3a-replication::text-minimal-t0.7-n30-25of30` (`:256`), and the
Era-2 champions `pv-diag-384::flash-high-text-n5-text-t0.7-consensus-26of30`
(`:116`) and `pv-diag-384::flash-minimal-text-n30-t07-text-t0.7-consensus-29of30`
(`:118`).

**The registered "voting vs single-pass" comparison itself** is on disk at
`results/retest/pairwise-bootstrap-comparisons.json` as
`"phase": "Phase 3a vs Best Single-Pass"` (1 comparison), and is summarised in
`results/retest/retest-production-summary.md:272`.

### 4. Outcome

**The registered prediction is supported, strongly.**

- Direct registered contrast (`results/retest/pairwise-bootstrap-comparisons.json`,
  phase `Phase 3a vs Best Single-Pass`):
  `consensus_T0.7_18of30_image` vs `single_pass_canonical_last`,
  ΔF1 = **+0.0600**, p = **0.001**, `significant_raw: true`.
  Also at `results/retest/retest-production-summary.md:272`.
- Overall Era-1 magnitude (`results/retest/retest-production-summary.md:171`):
  *"Consensus voting consistently improves over single-run baselines
  (+0.11 to +0.21 ΔF1)."*
- Best Era-1 consensus (`…:159`, `…:172`): Replication HIGH 21-of-30,
  **F1 = 0.7705** [0.725, 0.811], *"the highest F1 in the entire study
  (non-PV)"*.
- Era-2 384 px statistical test (`diversity-dividend-384` outcome,
  `results/analyses-manifest.json:154`): *"(2) CONSENSUS vs SINGLE-PASS —
  every consensus champion significantly beats its matched within-pool
  single-pass baseline (+0.13 to +0.43 F1, all BH-p<0.001), and the lift
  persists at the production N=5 operating point … (+0.09 to +0.33 F1)."*
- Era-1 definitive board (`era1-leaderboard` outcome, `:503`):
  *"Consensus still dominates bare single-pass (every consensus cell > every
  bare single-pass)."*

**Beyond the registered prediction** — the *diversity dividend*, an
unregistered mechanism finding that emerged from H3 data:
`diversity-dividend-384` (`:154`): *"HIGH-thinking consensus significantly
exceeds minimal-thinking consensus at matched modality: text +0.153 F1
(BH-p<0.001; MCC +0.239) and image +0.070 F1 (BH-p<0.001; MCC +0.272)"*;
replicated by `phase3a-replication-thinking-calibration` (`:265`):
HIGH 0.7705 vs MINIMAL 0.7033 at N=30, *"+0.067 F1 and +0.234 MCC"*.
Original observation: `docs/notes/working-notes.md:2239` (Observation 140,
*"High thinking improves consensus voting despite hurting individual-run
efficiency — the diversity dividend"*) and `:2281` (Observation 141, on the
accidental-error provenance).

**Scope qualification the PI should note**: `min-vs-high-thinking-pv` outcome
(`results/analyses-manifest.json:691`) reports the dividend is
*"OBSOLETE under PV (Obs 359)"* — real for consensus-only architectures,
not once a verifier stage exists. This does not affect the H3 verdict, only
its downstream reading.

### 5. Deviations touching H3

| E | Type | Line | One-line summary |
|---|---|---|---|
| **E17** | Correction | `:355`, type `:360` | Removed the erroneous `passes: 5` within-run multiplier; explicitly cites §3.8's *"K=10 independent **single-pass** runs … without assuming voting (which is itself under test in H3)"* (`:364`) and confirms H3 voting is post-hoc re-pooling (`:366`). |
| **E21** | Correction | `:452` | Stale `passes: int = 5` parameter in the analysis script (post-E17 remnant). |
| **E32** | **Deviation** | `:747`, type `:751`, severity Low `:752` | **Phase 3a uses T=0.3/T=0.7 instead of carry-forward T=0.0**: at T=0.0 output is near-deterministic so *"Applying consensus voting to identical runs is meaningless"* (`:754`). The comparison baseline is therefore the T=0.0 single-run mean, not same-temperature single-pass (`:762`). This is the single most consequential H3 deviation. |
| **E36** | Deviation | `:878` | 60-tile → 340-tile corpus; K retained at 30 for consensus (`:888`). |
| **E43** | (see doc) | `:1039` | `consensus-384` executed at T=1.0 instead of T=0.7; directory renamed `consensus-384-UNINTENDED-T1.0` (`:1045`, `:1063`). Preserved rather than deleted. |
| **E44** | (see doc) | `:1070` | `single-pass-384` executed at T=1.0 instead of T=0.0 (the matched single-pass baseline). |
| **E53** | **Deviation** | `:1581`, type `:1586` | **Phase 3a-HIGH image track moved from 512 px (Era 1) to 384 px (Era 2)**: the registered 512 px image-track K=30 study *"was never launched"* (`:1595`); replaced by a 2×4 thinking × temperature matrix at 384 px / 487 tiles with K=10 (`:1619–1630`, parameter table `:1650–1659`). **Impact line `:1588`: "H3 image-track consensus analysis reported on Era 2 scope (487 tiles, 384 px) rather than Era 1 (340 tiles, 512 px)".** |
| **E45** | Deviation | `:1097` | Macro → micro-average permutation statistic. |
| **E46/E47** | Deviation / Reversion | `:1163` / `:1236` | 20 → 30 m and back to 20 m. |
| **E54** | Clarification | `:1673` | Bootstrap iterations 1 000 / 10 000. |
| **E56** | (see doc) | `:1746`; **Update at `:1772`** | The in-sample verifier-threshold rule is explicitly scoped **away from** H3: *"This erratum governs the **verifier probability-threshold** diagnostics only. It does **not** make the **H3 consensus-voting characterisation** … an 'in-sample' limitation"* (`:1772`); *"H3's swept-optimal reporting was preregistered (`analysis-summary.md` §H3)"* (`:1778`). Directly relevant to classification — the project already argued in writing that H3's method is the preregistered one. |
| **E49/E51** | (cited, not read in full) | `:1313` / `:1366` | Cited in `diversity-dividend-384`'s `deviations` array (`results/analyses-manifest.json:145`) as the T=0.7 / HIGH-thinking production carry-forward. |

### 6. Proposed classification

**`preregistered-with-deviation`** — and of the four hypotheses this one has
the strongest claim to being owned as confirmatory.

*For `preregistered`*: every element of the registered analysis plan was
executed — voted-vs-single-pass comparison, full threshold sweep curves at
N = 5/10/30, identification of the optimal (N, threshold), and cost-benefit
characterisation (`pass-budget-pareto`, `pass-budget-pareto-v2`). The
registered prediction was directional and was confirmed with p = 0.001 and
BH-p < 0.001 across two independent instruments. The project has already
argued in writing (E56 Update, `protocol-errata.md:1772–1778`) that the
best-operating-point reporting *is* the preregistered method rather than a
post-hoc hedge.

*For `preregistered-with-deviation`* (my recommendation): three substantive
errata bite — **E32** (the tested temperature is not the carry-forward
temperature, and the comparison baseline is asymmetric: voted F1 at T > 0
against single-run F1 at T = 0), **E53** (the registered 512 px image-track
K=30 study was never launched and was replaced by a different design at a
different tile size and different K), and **E36** (corpus and K). Each is
individually defensible; collectively they mean the reported H3 result is not
the registered experiment executed as written.

*Against `exploratory`*: indefensible. This is a directional confirmatory
prediction, tested, confirmed.

**Which rows to change.** The nine H3-tagged rows are not equivalent:

- `pv-diag-384-consensus-calibration`, `phase3a-consensus-calibration`,
  `phase3a-high-consensus-calibration` — these are *calibration material*
  (their own outcome text says so: e.g. `:198` *"This registers the consensus
  calibration material; the preregistered statistical comparison against
  single-pass lives in results/retest/phase3a-consensus/"*). They are the
  registered *threshold sweep curves* output, so `preregistered-with-deviation`
  is defensible; `exploratory` is not obviously wrong for the HIGH-thinking one
  (`phase3a-high-consensus-calibration`), whose HIGH arm is unregistered.
- `diversity-dividend-384`, `phase3a-replication-thinking-calibration` — these
  carry *both* the registered consensus-vs-single-pass claim **and** the
  unregistered diversity-dividend claim. Cleanest honest label:
  `preregistered-with-deviation` for the H3 component, with the diversity
  dividend explicitly flagged as exploratory in the outcome prose (which it
  partly already is).
- `pass-budget-pareto`, `pass-budget-pareto-v2`, `min-vs-high-thinking-pv` —
  these are PV-era cost/architecture studies. **Leave `exploratory`.**
- `era1-leaderboard` — mixed board; see H1/H4 note.

### 7. Source discrepancies

1. **Manifest vs preregistration**: nine rows say `exploratory`; the
   preregistration says confirmatory. Believe the preregistration.
2. **`hypothesis-tracking.md:15`** — `| H3 | Consensus Voting | N, threshold | 3a | Complete | 2026-03-07 |`
   and `:96–98`: *"Complete. Consensus voting confirmed to improve over
   single-run baseline for both tracks. N=30 at T=0.7 optimal."*
   Direction agrees with the manifest outcomes. But it is **stale on scope**:
   its detail block (`:108–112`) still lists the registered N=5/N=10/N=30
   pool structure and does not mention E53 (image track never run at 512 px)
   or E32 (temperature substitution). Its note at `:100–106` about the
   `thinking_level: minimal` metadata bug and the 2026-03-15 clean replication
   (*"HIGH F1=0.735 vs minimal F1=0.699 (+3.6 pp)"*) is superseded by the
   re-scored figures in `phase3a-replication-thinking-calibration`
   (`results/analyses-manifest.json:265`: HIGH 0.7705 vs MINIMAL 0.7033).
   **Believe the manifest/analysis artefacts on numbers; believe
   hypothesis-tracking only on the confirmatory/exploratory column.**
3. **`hypothesis-tracking.md:112`** lists `N=30 | Extended (20 additional runs)`
   consistent with `preregistration.md:512`. That N=30 extension *was* run
   (Era-1 phase3a at K=30), so this element is faithful.
4. `phase3a-consensus-calibration` and siblings carry `deviations: []`
   (`results/analyses-manifest.json:195`, `:230`, `:262`) despite E32, E36 and
   E53 plainly applying. Manifest defect.

### 8. Where reported

`docs/paper/results-draft.md` § R3, `:112–131`:

- `:112` — heading *"R3. Consensus voting buys real performance; its mechanism
  is pass diversity"*.
- `:114–118` — *"Consensus voting over repeated passes (H3) delivers the
  study's first large, statistically clean gain. Pooling N independent passes
  and thresholding on cross-pass vote count lifts the text pipeline from the
  single-pass tie (~0.63) to 0.69–0.77…"*.
- `:119–122` — the diversity dividend, citing `diversity-dividend-384`,
  *"both preregistered claims confirmed; replication +0.067 F1, +0.234 MCC"*.
- `:128–131` — the scope revision under PV.

H3 is the best-reported of the four. The draft even uses the phrase *"both
preregistered claims confirmed"* (`:121`) — which is flatly inconsistent with
the manifest calling the same analysis `exploratory`.

---

## H4 — Example Ordering Affects Performance (Canonical Placement)

### 1. As registered

**Heading**: `preregistration.md:534` —
`### H4: Example Ordering Affects Performance (Canonical Placement)`

**Status line**, verbatim (`…:536`): `**Status**: Confirmatory (Strand 2)`

**Research question** (`…:538`): *"Does the positioning of canonical
(legend-derived) examples relative to hard (empirically-derived) examples
affect detection performance?"*

**Prediction**, verbatim (`…:542`):

> **Prediction**: Canonical-last ordering will produce higher F1 than
> canonical-first ordering. Random ordering will perform between the two.

**Directional hypothesis**, verbatim (`…:546`):

> **Directional hypothesis**: H0: canonical-last ≤ canonical-first; H1: canonical-last > canonical-first

**Test** (`…:548–554`): three ordering conditions at optimal M/E —
Canonical-first (positions 1–6), Canonical-last (final positions), Random
(shuffled).

**Fixed parameters** (`…:566`): *"Optimal M/E (from H1), optimal H5 (from H5),
optimal library (from H8), optimal temperature (from H7)."*

**Registered analysis** (`…:568–572`), verbatim:

> **Analysis**:
>
> - **Primary**: Pairwise bootstrap comparisons across 3 ordering conditions (95% CIs, FDR-corrected)
> - **Planned contrasts**: Canonical-first vs Canonical-last; Optimal vs Random
> - **Secondary**: Effect size estimation for ordering benefit

**Advance rule** (`…:574`): *"Significant ordering effect detected
(FDR-corrected p < 0.05)."*

**Trigger for H4b** (`…:564`, and `:1177`): *"HP/HN ordering within the hard
block is tested separately in exploratory H4b if H4 main effect is
significant."* Table row `:1177`:
`| H4b (HP/HN ordering) | H4 significant (p < 0.05) | Does HP vs HN position within hard block matter? | 2 |`

**Summary-table row** (`…:1155`):
`| H4 (example ordering) | Canonical-last > canonical-first | One-tailed | Significant ordering effect |`

Plain-language restatement, `analysis-summary.md:90` (`### H4: Example
Ordering`), body at `:92–94`: design 3 conditions; *"Pairwise bootstrap
comparisons (95% CIs, FDR-corrected); planned contrast canonical-first vs
canonical-last"*; *"**Prediction**: Canonical-last > canonical-first (recency
effect)"*.

### 2. Registered status

**Confirmatory**, stated in its own body: `preregistration.md:536` —
`**Status**: Confirmatory (Strand 2)`. Also under `## 5. Confirmatory
Hypotheses` (`:398`), in `### 7.1 Confirmatory Hypotheses (H1-H8)` at `:1155`,
and in the implementation-mapping table under `**Confirmatory Hypotheses
(H1-H8)**` at `:1992`.

### 3. Execution

**Run: yes**, as Phase 2e, with an added fourth condition.

- Run ID: **`retest-phase2e`** — `results/runs-manifest.json:725`,
  `primary_hypothesis: "H4"` (verified by programmatic extraction),
  `directory_path` `outputs/retest/phase2e`, `run_type` `single-pass`,
  512 px, `era-1-340` scope.
- Condition IDs (4), from `results/conditions-manifest.json` (all
  `architecture: single-pass`, **`n_passes: 1`**):
  `retest-phase2e::canonical-first`, `::canonical-last`, `::config-default`,
  `::random`. The fourth (`config-default`) is the E30 addition.
- Analysis IDs carrying `"H4"` in `hypothesis_refs`
  (`results/analyses-manifest.json`), exhaustively — exactly two:
  1. **`era1-single-pass-baseline-matrix`** — id `:315`, refs
     `["H1","H4","H5","H7","H8"]` `:355–361`, `"exploratory"` `:362`,
     `deviations: []` `:363`. Contains all four phase2e conditions at
     `:350–353`.
  2. **`era1-leaderboard`** — id `:402`, refs include `"H4"` `:488–496`,
     `"exploratory"` `:497`, `deviations: []` `:498`.

As with H1, **neither is the registered H4 test**. The registered
pairwise-bootstrap analysis is at:

- `results/retest/phase2e-evaluation.json` — four condition summaries plus a
  `pairwise` array of all six contrasts with bootstrap CIs and `significant`
  booleans; sidecar `results/retest/phase2e-evaluation.metadata.json`
  (script `scripts/evaluate_retest_all.py`, 1 000 iterations, seed 42,
  percentile bootstrap, `resampling_unit: tile_level_multi_run`).
- `results/retest/pairwise-bootstrap-comparisons.json` — 6 comparisons tagged
  `"phase": "Phase 2e: H4 Ordering"`.
- `results/retest/retest-production-summary.md:136–145` (§7) and `:246–251`
  (§11.5).

**Partial execution / scope notes**:

- **Image-using track only.** `execution-checklist.md:103`: *"Phase 2e: H4
  Ordering | 2026-02-12 | 2026-02-12 | Single-track (image-using only;
  text-only has nothing to reorder); 4 conditions × K=10; no significant
  effect after FDR correction; retrospective carry-forward 2026-03-09"*.
  Under E27's dual-track regime, Track 2 (text-only) did not receive H4.
- **K**: the checklist says K=10 at the original 60-tile execution; the
  340-tile retest ran **K=1** (`results/conditions-manifest.json` `n_passes: 1`;
  corroborated `results/retest/retest-production-summary.md:140–143` "K" column
  = 1, and caveat 5 at `:281`: *"Phase 2c / 2d / 2e use K = 1 (single replicate)
  per condition; the per-condition CIs are tile-level only, not
  replicate-level."*).
- **Fixed parameters as registered?** Partially — the registered fixed set
  (`preregistration.md:566`) is optimal M/E + H5 + library + temperature.
  Phase 2e ran after 2a–2d in the OFAT chain (`execution-checklist.md:99–103`),
  so the carry-forward was applied, but on the Track-1 (brief-text-image) leg
  only, under E27. **UNVERIFIED**: I did not open `studies/phase2e-h4-ordering.yaml`
  to byte-check the four fixed parameters against the Phase 2b/2c/2d optima.
  That is the check that would close this point.

### 4. Outcome

**340-tile retest, F1@20 m** (`results/retest/retest-production-summary.md:140–143`;
cross-checked against `results/retest/phase2e-evaluation.json` and
`results/conditions-manifest.json` — agree to 4 dp):

| Condition | F1 | 95 % CI | P | R | K |
|---|---:|:---:|---:|---:|---:|
| canonical-last | 0.6314 | [0.587, 0.672] | 0.5325 | 0.7755 | 1 |
| config-default | 0.6047 | [0.559, 0.653] | 0.5193 | 0.7236 | 1 |
| canonical-first | 0.5983 | [0.546, 0.646] | 0.5091 | 0.7254 | 1 |
| random | 0.5710 | [0.519, 0.618] | 0.4732 | 0.7199 | 1 |

Pairwise contrasts (`results/retest/pairwise-bootstrap-comparisons.json`,
raw p; and CI-based `significant` flags from
`results/retest/phase2e-evaluation.json`):

| Contrast | ΔF1 | bootstrap CI | raw p | significant |
|---|---:|:---:|---:|---|
| canonical-first vs canonical-last | −0.0316 | [−0.0749, +0.0117] | 0.124 | **no** |
| canonical-first vs config-default | −0.0051 | [−0.0372, +0.0256] | 0.678 | no |
| canonical-first vs random | +0.0286 | [−0.0082, +0.0655] | 0.138 | no |
| canonical-last vs config-default | +0.0265 | [−0.0089, +0.0654] | 0.158 | no |
| **canonical-last vs random** | **+0.0602** | [+0.0233, +0.0955] | **0.002** | **yes (raw)** |
| config-default vs random | +0.0337 | [−0.0021, +0.0718] | 0.046 | yes (raw, marginal) |

**Verdict against the registered prediction:**

- **Directional ordering is as predicted**: canonical-last (0.6314) >
  config-default (0.6047) > canonical-first (0.5983) > random (0.5710).
  Canonical-last is numerically the best single-pass condition in the whole
  Era-1 retest (`retest-production-summary.md:145`, *"the highest
  non-consensus score in the entire production retest"*; also
  `era1-single-pass-baseline-matrix` outcome, `results/analyses-manifest.json:387`,
  *"Tier 1 (tie_set) is a BROAD 20-of-36-cell statistical tie … led by
  canonical-last (phase2e few-shot ordering, F1 0.631, MCC 0.213)"*).
- **The registered primary contrast fails to reach significance**:
  canonical-first vs canonical-last, ΔF1 = −0.0316, raw p = 0.124, CI spans
  zero. The registered advance rule (`preregistration.md:574`, FDR-corrected
  p < 0.05) is **not met**. `retest-production-summary.md:145`:
  *"Canonical-last vs config-default and canonical-first are not significant
  (p = 0.158 and p = 0.124 respectively)."*
- **A non-registered contrast does reach significance**: canonical-last >
  random (+0.060, p = 0.002). The prediction that random would sit *between*
  the two is **contradicted** — random is worst.
- Narrative claim at `retest-production-summary.md:145` — *"Placing the
  canonical example last in the few-shot sequence improves performance,
  consistent with recency bias"* — and at `:300` (§14.1) — *"Example ordering:
  **canonical-last** (Phase 2e; F1 = 0.631 single-pass; ΔF1 = +0.060 vs random,
  p = 0.002)"* — **overstate the registered test**: the registered contrast
  (canonical-last vs canonical-first) is null; only the vs-random contrast
  is significant. **This is a finding-calibration issue the PI should see.**
- **H4b trigger**: not fired. `hypothesis-tracking.md:129–131`:
  *"**Triggered exploratory (H4b)**: … **Not triggered** — H4 showed no
  significant effect (2026-02-12)."* Consistent with the registered trigger
  logic.

**Net**: H4 is a **directionally-supported but statistically unresolved**
confirmatory test on its primary contrast. Under
`preregistration.md:284` this is exactly the "non-significant but consistent
directional improvement" case that the preregistration says *"may be flagged
for Stage 2 investigation with lowest priority if theoretically motivated"*.

### 5. Deviations touching H4

| E | Type | Line | One-line summary |
|---|---|---|---|
| **E17** | Correction | `:355`, type `:360` | Erroneous `passes: 5` multiplier removed from `studies/phase2e-h4-ordering.yaml` (named at `:361`). |
| **E27** | **Deviation** | `:617`, type `:622` | Dual-track carry-forward; *"Phase 2e (H4) tests example image ordering"* is named at `:628` as structurally incompatible with a text-only winner, so H4 ran on the image track only; Track 2 H4 *"deferred"* (`:633`). |
| **E29** | **Correction** | `:669`, type `:674` | *"`reorder_examples()` canonical-first was a no-op"* — it returned config-file order `[C+, HP, C−, null]` rather than the intended `[C+, C−, HP, null]` (`:678`). Discovered during Phase 2e design review (`:680`). *"Protocol impact: None"* for prior phases (`:689`); the fix is what made H4 testable at all. |
| **E30** | **Deviation** | `:695`, type `:700`, Decision 18 | *"Phase 2e tests 4 ordering conditions instead of preregistered 3"* — adds `config-default` as an explicit baseline (`:705`, condition table `:709–714`). `config-default` reuses Phase 2c plus-hp outputs via symlinks (`:716`), so no extra API cost for those runs. *"Protocol impact: Minor."* (`:720`). |
| **E31** | **Deviation** | `:726`, Phase 2e (H4 — Ordering) at `:729`, Type Deviation `:730`, Severity Low `:731` | *"Deterministic runs at T=0.0 copied instead of re-executed"* — for 4 units (`canonical-first/run_1`, `canonical-last/run_{3,6,8}`) detection outputs were **copied** rather than re-dispatched, on the argument that T=0.0 Flash is byte-deterministic (`:735`, `:737`). *"Impact on analysis: None."* (`:739`). Files listed at `:741`. |
| **E36** | Deviation | `:878` | 60-tile → 340-tile; K reduced to 1 for Phase 2e. |
| **E45** | Deviation | `:1097` | Macro → micro-average statistic (affects the Era-1 board that ranks canonical-last, not the phase2e bootstrap). |
| **E46/E47** | Deviation / Reversion | `:1163` / `:1236` | Buffer 20 → 30 → 20 m. |
| **E54** | Clarification | `:1673` | Bootstrap iterations. |

Not recorded as an erratum, but a real departure: the registered *"One-tailed"*
test type (`preregistration.md:1155`, `:546`) versus the two-sided bootstrap CI
/ two-sided p actually computed. **UNVERIFIED** — I did not read
`scripts/evaluate_retest_all.py` to confirm the tail convention; the check
that would settle it is to inspect how `significant` and `f1_p_value` are
derived in that script. If the reported p-values are two-sided, the registered
one-tailed test on canonical-last > canonical-first would have p ≈ 0.06,
still non-significant, so the substantive verdict does not change.

### 6. Proposed classification

**`preregistered-with-deviation`.**

*For `preregistered`*: the hypothesis, the direction, the three conditions,
the primary contrast and the analysis method (pairwise bootstrap with 95 % CIs)
were all registered in advance and all were executed. The result is reported
regardless of being null on the primary contrast.

*For `preregistered-with-deviation`* (my recommendation): four errata bite
directly — **E30** (four conditions, not the registered three), **E31**
(4 of the K units were copied, not executed — defensible at T=0.0 but it is a
protocol departure the reader must be told about), **E27** (single-track only;
the registered design does not restrict H4 to image-using conditions, it
restricts it to "optimal M/E", and E27 created two optima), and **E36**
(K = 1 rather than K = 10, which materially weakens the replicate-level CIs —
see `retest-production-summary.md:281`). Add the missing FDR correction.

*Against `exploratory`*: unsupportable. H4 has an explicit
`**Status**: Confirmatory (Strand 2)` line in the registered document
(`preregistration.md:536`).

**Genuinely arguable point**: one could argue for `preregistered` on the view
that E29/E30/E31 are all *corrections and additions that strengthen* the test
rather than compromise it (the added `config-default` arm is strictly more
information; the copied runs are provably identical; the E29 fix is what made
the canonical-first arm honest). I still prefer
`preregistered-with-deviation`, because E36's K = 1 is not a strengthening —
it removes the replicate-level variance component the registered design
depended on, and the primary contrast's null verdict is exactly the kind of
result whose interpretation turns on power.

**Which row to change.** As with H1, the two H4-tagged manifest rows are
leaderboards. Either register
`results/retest/phase2e-evaluation.json` as its own analysis row, or attach
the label to `era1-single-pass-baseline-matrix`, which contains all four
phase2e conditions.

### 7. Source discrepancies

1. **Manifest vs preregistration**: both H4 rows say `exploratory`; the
   preregistration says `Confirmatory (Strand 2)` in its own body. Believe
   the preregistration.
2. **`hypothesis-tracking.md:16`** — `| H4 | Example Ordering | Ordering | 2e | Complete | 2026-02-12 |`
   under `## Confirmatory Hypotheses (H1-H8)`. Agrees with the
   preregistration; contradicts the manifest.
3. **`hypothesis-tracking.md:120–121`** — *"Status (2026-02-12): Complete. No
   significant ordering effect after FDR correction. Config-default
   (canonical-first) ordering carried forward."*
   Two problems: (a) it asserts *"after FDR correction"* when the retest
   artefacts say FDR was **deferred** (`results/retest/retest-production-summary.md:209`,
   `:278`) — the "after FDR correction" claim presumably refers to the earlier
   60-tile analysis and I could not verify an FDR-corrected H4 artefact;
   (b) it parenthesises *"Config-default (canonical-first)"* as if they were
   the same thing, which E29 (`protocol-errata.md:678`) established they are
   **not**. Its condition table at `:123–127` lists only three conditions and
   omits `config-default` entirely — i.e. it does not reflect E30.
   **Believe the retest artefacts and the errata; the tracking doc's H4 block
   is the least reliable of the four.**
4. **`retest-production-summary.md:145` and `:300`** overstate the ordering
   effect (see Outcome above): they lead with the significant vs-random
   contrast and the recency-bias interpretation, where the *registered*
   contrast is null. Worth a calibration fix when that document is next
   revised.
5. `era1-single-pass-baseline-matrix` and `era1-leaderboard` both carry
   `deviations: []` (`results/analyses-manifest.json:363`, `:498`) despite
   E29/E30/E31/E36 applying to their phase2e constituents. Manifest defect.

### 8. Where reported

`docs/paper/results-draft.md` § R2, `:85–110`:

- `:88` — H4 named among the preregistered single-factor results compressed
  into § R2.
- `:97–100` — *"Tier 1 is a 20-cell statistical tie spanning F1 0.583–0.631,
  led numerically by a few-shot-ordering variant (`canonical-last`, F1 0.631,
  MCC 0.213; analysis `era1-single-pass-baseline-matrix`, 227/630 pairs
  significant)."*
- `:102–104` — H4 listed among the manipulations that *"all land inside or
  near that tie"*.
- `:448` (Changelog) — *"**§ R2 (framing)**: board-led compression of the
  H1/H4/H5/H7/H8 …"*.

**Gap**: the draft reports canonical-last's numerical leadership but does not
state the registered prediction, does not report the canonical-first vs
canonical-last contrast, and does not say the registered contrast was null.
It also does not mention that H4b was registered as a triggered exploratory
and did not trigger. For a preregistered study this is the sort of omission a
reviewer will find.

---

## Summary table

| H | Registered status (with anchor) | Executed? | Registered prediction verdict | Proposed classification |
|---|---|---|---|---|
| H1 | Confirmatory — `preregistration.md:398`, `:1152`, `:1989` | Yes (`retest-phase2a`, 5 conditions, K=3) | Prediction 2 supported; **predictions 1 and 3 contradicted** | `preregistered-with-deviation` |
| H2 | Confirmatory — `preregistration.md:453` (`**Status**: Confirmatory (architectural)`) | Condition B yes; **Condition C never run** | **Contradicted** — two-stage improves by far more than the 0.05 stopping rule | B: `preregistered-with-deviation`; C: not executed (`null`) |
| H3 | Confirmatory — `preregistration.md:398`, `:1154`, `:1991` | Yes, extensively (3 dedicated runs + PV-era) | **Supported** (ΔF1 +0.060, p = 0.001; +0.13–0.43, BH-p < 0.001) | `preregistered-with-deviation` |
| H4 | Confirmatory — `preregistration.md:536` (`**Status**: Confirmatory (Strand 2)`) | Yes (`retest-phase2e`, 4 conditions, K=1) | Direction as predicted; **primary contrast null** (p = 0.124); random-between-the-two contradicted | `preregistered-with-deviation` |

---

## Open questions requiring the PI's judgement

1. **The manifest has no row for the registered H1 and H4 tests.** The
   pairwise-bootstrap analyses live in `results/retest/phase2a-evaluation.json`
   and `results/retest/phase2e-evaluation.json` and are not registered as
   analyses. Should new manifest rows be created for them, or should the
   labels be attached to the leaderboard rows that merely *contain* the
   conditions?
2. **`era1-leaderboard` does not claim H2** but reports the H2 result. Add
   `"H2"` to its `hypothesis_refs`?
3. **The registered BH-FDR correction across the 8 confirmatory hypotheses
   was deferred and appears never to have been completed as one family.** Is
   that a deviation to be written up as a new E-number, or is the per-board
   BH-FDR that the leaderboard analyses apply the accepted substitute? This
   affects the honest wording of every `preregistered-with-deviation` label.
4. **H2 Condition C (fine-to-coarse) was dropped without an erratum.** The
   drop is visible in `execution-plan.md:585–592` and stated in
   `hypothesis-tracking.md:86`, but has no E-number. Should it get one?
5. **`analysis-summary.md:82`** (*"Treated as exploratory"* for H2) is the
   most plausible origin of the blanket `exploratory` value. It contradicts
   the preregistration and an already-applied fix elsewhere
   (`execution-plan.md:814`). Correct it, or does it record a deliberate
   pre-registration downgrade the preregistration failed to carry through?
6. **`retest-production-summary.md:145`, `:300`** describe H4 as showing that
   canonical-last *"improves performance, consistent with recency bias"* when
   the registered contrast is null. This reads as a calibration overstatement
   and should probably be softened when that document is next revised.
7. **Tail convention for H4 (and H1's elaboration contrast).** Registered as
   one-tailed (`preregistration.md:546`, `:1155`); the artefacts report
   two-sided CIs. Confirming the convention in
   `scripts/evaluate_retest_all.py` would let the paper state the tail
   honestly. (Does not change either verdict.)
8. **Schema limitation.** `not-executed` is not a permitted `preregistered`
   value (`docs/manifest-schemas/analyses-manifest.schema.json:48`). If H2-C
   or any other unexecuted registered test needs a manifest presence, the
   schema needs a new enum member or an explicit `null`-plus-prose convention.
