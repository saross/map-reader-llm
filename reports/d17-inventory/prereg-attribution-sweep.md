# Preregistration Attribution Sweep

**Date**: 2026-07-28
**Repository**: `/home/shawn/Code/map-reader-llm` @ `8eea4bd4d751e50eae301c6fb7a55c8fcf4f53d3`
**Scope swept**: `docs/**`, `reports/**` (excl. `reports/d17-inventory/`), `results/**.md`,
`planning/**`, `README.md`, docstrings/comments in `scripts/**`. Excluded: `archive/**`.

## Authority used

| Role | Document | Evidence it is authority |
| :--- | :--- | :--- |
| Canonical | `docs/methodology/preregistration/osf/preregistration.md` | Lodged v4.7 |
| Canonical | `docs/methodology/preregistration/osf/preregistration-appendix-prompts.md` | `osf/README.md:3,9-11` |
| Canonical | `docs/methodology/preregistration/osf/preregistration-coverage.md` | `osf/README.md:3,9-11` |
| Amendments | `docs/methodology/preregistration/protocol-errata.md` (E1–E57) | `protocol-errata.md:3-5` |

**Load-bearing scoping fact**: `osf/README.md:3` reads *"This registration contains **three**
documents comprising the complete preregistration"* and `osf/README.md:9-11` names them.
`docs/methodology/preregistration/analysis-summary.md` is **not** among them — it sits one
directory above `osf/`. Several documents cite it as the preregistration (see U4).

## Method note on absence claims

Every "the preregistration does not say X" verdict below was established twice: once by
line-based `grep`, and once by a whitespace-normalised whole-file scan
(`tr 'A-Z' 'a-z' | tr -s ' \n\t' ' ' | grep -o`) which cannot produce a false negative from
line wrapping. Multiple synonyms were tried for each term. Where a term genuinely appears,
the appearing contexts are quoted so the reader can judge relevance rather than take a count.

Key normalised counts across `preregistration.md` + `preregistration-coverage.md` +
`preregistration-appendix-prompts.md`:

| Term | Count | Note |
| :--- | ---: | :--- |
| `permutation` | 0 in `preregistration.md` | 2 hits in appendix, both about example-ordering seed shuffles |
| `percentile` | 0 | — |
| `dawid` / `skene` / `annotator` | 0 | also 0 in `protocol-errata.md`, `decisions-log.md`, `analysis-summary.md` |
| `1,000` / `1 000` iterations | 0 | `1000` appears only as coordinate range `0-1000` and cost `21,000` |
| `wbf` / `weighted box` / `box fusion` | 0 | — |
| `carry-forward` / `carry forward` | 0 | concept present as prose in §8.4.7, phrase absent |
| `four-stage` | 0 | — |
| `full corpus` | 0 | — |
| `1:25,000` / `kazanlak` | 0 | `1:50,000` ×8, `thracian` ×1 |
| `40-60` / `40–60` | 0 | — |
| `rank by f1` / `prefer canonical` / `select condition` / `select ordering` / `for simplicity` | 0 each | — |
| `decision rule` | 2 | `preregistration.md:677` (H6, ≥0.03 F1) and `:1590` (frequency cap) only |
| `stopping rule` | 1 | `preregistration.md:491` (H2, ≥0.05 F1) only |

---

# FALSE

## FALSE-1 — H6 deferral reason attributed to a budget decision that does not exist

**Claim** — `docs/methods-outline.md:341`:

> `| H6 (Flash → Pro transfer) | Not started; budget prioritised for Flash experiments |`

The row sits under the heading `### What the Preregistration Planned but Was Not Executed`
(`docs/methods-outline.md:337`).

**What the registration says**: `preregistration.md:1841` costs the whole confirmatory
programme at *"~$286 for confirmatory tests (26 cells × ~$11/cell)"*. H6 is not in that
26-cell table (`preregistration.md:1826-1837`) at all. Nothing in the registered text
subordinates H6 to a Flash budget.

**Verdict**: FALSE. Also arithmetically self-defeating — `reports/key-findings-summary-2026-06-23.md`
and the continuity log record far larger spend on the post-registration work that displaced H6.

**Severity**: **Reaches the paper.** This is the drafting note for the Methods section's
deviations table; a reviewer checking the OSF record will find no budget rationale.

**Proposed correction**: `| H6 (Flash → Pro transfer) | Not executed as registered (20-tile
holdout at 512 px); superseded by the exploratory 487-tile/384 px Pro comparison, erratum E41 |`.
Note that E41 (`protocol-errata.md:960-972`) already documents exactly this, and E57's Update
(`protocol-errata.md:1844`) reports genuine-Pro results — so the row is also stale (see STALE-7).

---

## FALSE-2 — H2 Condition C omission justified by a rationale the registered design forbids

**Claim** — `docs/methodology/preregistration/hypothesis-tracking.md:86-87`:

> **Note**: Fine-to-coarse (H2-C) was not tested — the coarse-to-fine results
> were strong enough that context expansion was deprioritised.

**What the registration says** — `preregistration.md:461`:

> **Prediction**: Neither two-stage architecture will improve F1 over single-stage detection with voting.

and `preregistration.md:491`:

> **Stopping rule**: Two-stage architectures will only be pursued further if either demonstrates
> F1 at least 0.05 higher than single-stage.

**Verdict**: FALSE. The registered prediction is a null for *both* architectures, so a strong
coarse-to-fine result does not bear on fine-to-coarse — it *falsifies* the prediction and, under
the registered stopping rule, is precisely the trigger to pursue two-stage architectures further,
not to stop. Condition C is one of three registered H2 conditions (`preregistration.md:466-469`).

**No erratum licenses it.** `grep -i 'fine-to-coarse\|context expansion\|condition c'` over
`protocol-errata.md` returns only three unrelated hits (lines 489, 1434, 1566). The omission of a
registered confirmatory condition has no errata entry at all.

**Severity**: **Reaches the paper.** H2 is confirmatory; an untested registered condition
reported without an erratum is the kind of thing a reviewer of preregistered work looks for first.

**Proposed correction**: replace with *"Fine-to-coarse (H2 Condition C, `preregistration.md:469`)
was not executed. This is an unexecuted confirmatory condition and requires a Deviation-class
erratum."* — and write that erratum.

---

## FALSE-3 — "the preregistered decision rule" for T=1.0 (three results documents)

**Claims**:

- `results/phase2b-carry-forward-parameters.md:69-70` — `The preregistered decision rule: *"If T=1.0 (default) is within 0.02 F1` / `of best, prefer T=1.0 for simplicity."*`
- `results/retest/phase2b/analysis_summary.md:174-175` — same quotation, same attribution
- `results/phase2e-carry-forward-parameters.md:56-58` — `The preregistered decision rule states: "Select ordering with highest mean F1."` … `specifies: if config-default is within 0.02 F1 of the best, prefer`

**What the registration says**: nothing. `within 0.02`, `for simplicity`, `prefer canonical`,
`select ordering`, `rank by f1` and `highest F1` all return **zero** normalised hits across all
three canonical documents. `prefer` appears three times in `preregistration.md` — at `:390`
(MCC preferred over accuracy) and `:672`/`:674` (H6 questions "Does Pro prefer more/less text?").
The only registered decision rules are `preregistration.md:677` (H6, ≥0.03 F1) and `:1590`
(hard-example frequency cap).

**Actual source**: the study YAMLs — `studies/phase2b-h7-temperature.yaml:125`,
`studies/phase2b-h7-temperature-text-only.yaml:136`, `studies/retest/phase2b-h7-temperature.yaml:109`,
`studies/retest/phase2b-h7-temperature-text-only.yaml:124`, `studies/phase2e-h4-ordering.yaml:127-128`,
`studies/retest/phase2e-h4-ordering.yaml:105-107` — plus the root cause at FALSE-7.

**Verdict**: FALSE. **Severity**: **Reaches the paper** — carry-forward parameter selection is
the spine of the OFAT chain, and presenting a post-hoc tie-break as registered is a
researcher-degrees-of-freedom claim a reviewer can falsify in one search of the OSF record.

**Proposed correction**: `The decision rule declared in the Phase 2b study YAML
(studies/phase2b-h7-temperature.yaml:125) — "If T=1.0 (default) is within 0.02 F1 of best,
prefer T=1.0 for simplicity" — is an operational tie-break adopted at execution time. The
preregistration specifies no carry-forward tie-break rule.`

---

## FALSE-4 — fabricated quotation attributed to the preregistration (H8 carry-forward)

**Claim** — `results/phase2c-carry-forward-parameters.md:54-55`:

> The preregistered decision rule states: "Rank by F1; if best differs from
> canonical by < 0.02, prefer canonical for simplicity."

**Verdict**: FALSE, and stronger than "unlicensed". A repo-wide search
(`grep -rn "Rank by F1"` and `grep -rn "prefer canonical for simplicity"` across `*.md`,
`*.yaml`, `*.yml`, `*.py`, `*.json`, including `archive/`) returns **this line and no other**.
The quoted text does not exist in the preregistration, in the Phase 2c study YAML, or anywhere
else. `studies/phase2c-h8-library.yaml:188-193` declares a *different* rule:
`Select library with highest mean F1.` / `If multiple libraries have overlapping 95% CIs with
the best,` / `prefer smaller library (fewer examples) for parsimony.`

**Severity**: **Reaches the paper** — this is the stated basis for selecting `plus-hp` as the
carried-forward library. A quotation with no source anywhere is the worst case of this error class.

**Proposed correction**: replace with the actual YAML rule, quoted verbatim and attributed to
`studies/phase2c-h8-library.yaml:189-191`, framed as an execution-time rule rather than a
registered one.

---

## FALSE-5 — fabricated quotation attributed to the preregistration (H5 carry-forward)

**Claim** — `results/phase2d-carry-forward-parameters.md:49`:

> The preregistered decision rule states: "Select condition with highest F1."

**Verdict**: FALSE. `grep -rn "Select condition with highest F1"` across the whole repository
(including `archive/`) returns this line only. `studies/phase2d-h5-negtext.yaml:133-139`
declares a materially different rule with an explicit non-significance branch:
`If no significant differences:` / `Use Minimal (simplest) as default — Occam's razor.`
That branch matters, because H5 returned no significant differences — so the *actual* basis for
selecting Minimal was the Occam's-razor fallback, not "highest F1".

**Severity**: **Reaches the paper.** The misquotation hides the fact that the carried-forward
H5 level was chosen by a simplicity default under a null, not by a performance criterion.

**Proposed correction**: quote `studies/phase2d-h5-negtext.yaml:137-138` and state that Minimal
was selected under the no-significant-difference branch.

---

## FALSE-6 — H4 carry-forward rule attributed to the preregistration

**Claim** — `results/phase2e-carry-forward-parameters.md:56`:

> The preregistered decision rule states: "Select ordering with highest mean F1."

**What the registration says**: `preregistration.md:570-574` gives H4's analysis as pairwise
bootstrap comparisons with an *"Advance to Stage 2 if"* criterion — no selection rule.

**Actual source**: `studies/phase2e-h4-ordering.yaml:127` (`Select ordering with highest mean F1.`)
and `studies/retest/phase2e-h4-ordering.yaml:105`.

**Verdict**: FALSE (attribution). The quotation is accurate — to a study YAML, not the registration.

**Severity**: Reaches the paper via the same carry-forward chain. **Proposed correction**: as FALSE-3.

---

## FALSE-7 — the root of the decision-rule family: a heading that misattributes five rules

**Claim** — `docs/methodology/preregistration/tasks/phase2-remaining-tasks.md:35`:

> ### Decision Rules (from preregistration)

followed by five rules (lines 37–41), of which none appears in any canonical document:

| Line | Rule | In registration? |
| :--- | :--- | :--- |
| 37 | `Select M/E with highest mean F1. If tied (overlapping 95% CIs), prefer simpler (image-only > brief > verbose).` | No |
| 38 | `Select temperature with highest mean F1. If T=1.0 within 0.02 F1 of best, prefer T=1.0.` | No |
| 39 | `Select library with highest mean F1. If tied, prefer smaller library.` | No |
| 40 | `If H5 main effect significant, select best H5 level. If M/E×H5 interaction, select best at optimal M/E. If neither, use Minimal.` | No |
| 41 | `Select ordering with highest F1. If canonical-first within 0.02 of best, prefer canonical-first.` | No |

**Verdict**: FALSE. This heading is the single upstream source that made FALSE-3 through FALSE-6
look legitimate: it is filed inside `docs/methodology/preregistration/`, which lends it the
appearance of registered authority.

**Severity**: High as a *cause*, low as a direct paper claim (a task-tracking file).

**Proposed correction**: rename the heading to `### Decision Rules (operational, declared in the
Phase 2 study YAMLs — not preregistered)` and add a one-line note that the preregistration
specifies no carry-forward selection rules.

---

## FALSE-8 — E37: "the preregistration did not include a two-stage Proposer-Verifier pipeline"

**Claim** — `docs/methodology/preregistration/protocol-errata.md:904`:

> **Description**: The preregistration did not include a two-stage Proposer-Verifier pipeline.

**What the registration says** — `preregistration.md:466-468`:

> | Condition | Architecture | Description |
> | A (baseline) | Single-stage | Optimal config with consensus voting |
> | B | Coarse-to-fine | Liberal proposer → strict verifier |

with implementation detail at `preregistration.md:471-476` (*"Stage 1: Detection with lower
confidence threshold" / "Stage 2: Crop candidate regions, verify with focused prompt"*), and the
verifier's own prompt lodged in the registered appendix at
`preregistration-appendix-prompts.md:1088-1128` (§1.6.2 `verify_brief.md`), plus its config at
`preregistration-appendix-prompts.md:1622-1640`. `preregistration.md:1990` lists H2 as
`✅ Ready | Separate pipelines (coarse-to-fine, fine-to-coarse)`.

**Verdict**: FALSE. PV is registered as H2 Condition B. What was genuinely new post-registration
is the *scale and role* of PV (crop size, adversarial framing, production deployment) — not the
architecture.

**Severity**: **Reaches the paper**, and inverts the study's strongest result. As written, the
headline PV finding is framed as unregistered exploratory work when it is in fact a confirmatory
hypothesis whose registered null prediction was falsified — a much stronger claim.

**Proposed correction**: rewrite E37's description as *"The preregistration registered a
coarse-to-fine proposer-verifier architecture as H2 Condition B (`preregistration.md:468`), with
the verifier prompt in the registered appendix (§1.6.2). This erratum records deviations in the
PV *implementation* — crop extraction from source rasters, adversarial prompt framing, crop size,
and production-scale deployment — not the introduction of the architecture."* Reclassify the
headline result as *confirmatory, prediction falsified*.

---

## FALSE-9 — E45: permutation test attributed to §3.5

**Claim** — `docs/methodology/preregistration/protocol-errata.md:1103` (`| Preregistration ref | Section 3.5 |`)
and `:1107-1111`:

> **Description**: The preregistered pairwise permutation test (Section 3.5)
> specifies tile-level resampling with a sign-flip permutation on per-tile
> F1 differences.

**What §3.5 actually says** — `preregistration.md:290-296`, in full:

> ### 3.5 Reporting
> - All preregistered analyses reported **regardless of outcome**
> - Report **effect sizes** (F1 difference, precision difference, recall difference) with 95% bootstrapped CIs
> - **Spatial tolerance sensitivity**: All primary results reported at 20m; robustness checks at 10m, 30m, and 50m included in supplementary materials
> - Report both uncorrected and FDR-corrected p-values
> - Exploratory analyses clearly labelled and interpreted cautiously

**Verdict**: FALSE. `permutation` appears **zero** times in `preregistration.md` (normalised
whole-file scan). §3.5 is a five-bullet reporting section that mentions no permutation test, no
sign-flip, no resampling unit and no macro-average. There was never a preregistered permutation
test for E45 to deviate *from*.

**Severity**: **Reaches the paper — highest severity in this sweep.** The tile-swap permutation
test is the inference method behind *every* leaderboard, tiering, and significance claim in the
project (`scripts/pairwise_permutation_test.py`, `n1_baseline_leaderboard_tiering.py`,
`era1_leaderboard_tiering.py`, `consensus_vs_baseline_tiering.py`, `mcc_tiering_55map.py`). E45
makes the whole inference chain look like a documented amendment to a registered method when it
is an unregistered substitution for the registered method (bootstrap CIs + BH-FDR).
`docs/paper/results-outline.md:486-493` independently reached the same conclusion.

**Proposed correction**: reclassify E45 from a "test statistic changed" deviation to an
"unregistered inference method adopted" deviation: *"The preregistration specifies bootstrap
CIs with BH-FDR (§3.5, §3.1) and does not specify any permutation test. Permutation-based
inference was adopted post-registration. It is defensible and arguably better-powered for this
design, but it must be reported as unregistered, and the registered bootstrap+FDR analysis must
be reported alongside it for the confirmatory hypotheses."*

---

## FALSE-10 — permutation attributed to §3.5 in code

**Claim** — `scripts/analyse_diversity.py:18`:

> permutation tests on tile-level F1 scores (preregistration Section 3.5).

**Verdict**: FALSE, same basis as FALSE-9.

**Severity**: Moderate — this is the H9 diversity analysis script, and H9 conclusions are cited
in `hypothesis-tracking.md` and the results draft. **Proposed correction**: `paired permutation
tests on tile-level F1 scores (unregistered inference method; see protocol erratum E45).`

---

## FALSE-11 — "the preregistered method (sign-flip with macro-average)" in the notes

**Claims**:

- `docs/notes/reflections/session-reflection.md:5789-5790` — `…a fundamentally different statistical approach (bootstrap` / `with micro-average) from the preregistered method (sign-flip with` / `macro-average)…`
- `docs/notes/reflections/abductive-reasoning.md:2629` — `test (like the preregistered method) but uses the micro-average`

**Verdict**: FALSE, same basis as FALSE-9. These are the reasoning traces that hardened the belief
into E45. **Severity**: Low direct paper reach (reflection logs), high diagnostic value — they show
the error propagating from working memory into the errata register.

**Proposed correction**: leave the historical reflections intact (they are a record of reasoning)
but append a dated correction note pointing to the corrected E45.

---

## FALSE-12 — the Dawid–Skene family: an entire analysis described as preregistered

**Claims** (all assert D-S was preregistered):

| File:line | Quoted text |
| :--- | :--- |
| `results/limitations-consolidation/report.md:15` | `D-S is retained as a preregistered comparator but cannot be used a…` |
| `results/limitations-consolidation/report.md:78` | `D-S retained as preregistered comparator with explicit inadequacy-disclosure` |
| `results/limitations-consolidation/report.md:82` | `the paper must state that the preregistered D-S analysis is **structurally inadequate for item-level ranking**` |
| `results/limitations-consolidation/report.md:296` | `**§2.4 Dawid-Skene 2-annotator inadequacy** (Obs 273) — the preregistered aggregate method…` |
| `results/limitations-consolidation/report.md:309` | `> Second, the preregistered Dawid-Skene (D-S) aggregate-posterior analysis is structurally unable to rank individual VLM-only candidates on this slice.` … `We retain D-S as a preregistered comparator` |
| `results/55maps-ds-summary-v2/report.md:21` | `**Aggregator**: \`scripts/analyse_dawid_skene.py\` (canonical), preregistered` |
| `results/55maps-ds-summary-v2/report.md:291` | `truth, while D-S uses only the preregistered fixed prior.` |
| `results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/report.md:21` | `replaces the preregistered 5 % student-FN prior` |
| `results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/report.md:120` | `> The preregistered Dawid-Skene analysis used a 5 % student-false-negative prior (Sobotkova et al. 2023).` |
| `results/meta-findings-summary.md:947` | `D-S posterior at the preregistered prior showing the single-value` |
| `results/documentation-audit/verification-2026-04-21.md:179` | `"the preregistered student-FN prior of 0.05 is mis-specified"` |
| `docs/notes/working-notes.md:12925` | `Dawid-Skene aggregate estimation was evaluated at the preregistered 5 % student-FN prior…` |
| `docs/notes/working-notes.md:14380` | `Under the preregistered fixed 5 % student-FN prior, D-S systematically under-states…` |
| `docs/notes/working-notes.md:14394` | `D-S aggregation under a fixed 5 % student-FN prior (preregistered) systematically under-counts…` |

**What the registration says**: nothing whatsoever. `dawid`, `skene` and `annotator` each return
**zero** normalised hits across `preregistration.md`, `preregistration-coverage.md`,
`preregistration-appendix-prompts.md` **and** `protocol-errata.md`. Also zero in
`decisions-log.md`, `analysis-summary.md` and `execution-plan.md` — the method has no
documentary basis anywhere in the preregistration lineage. The 5% student-false-negative prior
is attributed by `dawid-skene-v2-data-driven-prior/report.md:120` itself to Sobotkova et al. (2023),
i.e. a prior paper, not this study's registration.

**Verdict**: FALSE, across the whole family.

**Severity**: **Reaches the paper directly and in the most exposed place.**
`results/limitations-consolidation/report.md:309` is drafted Limitations prose (block-quoted for
lifting), and `:19` labels its neighbourhood a *"One-line paper claim for the Limitations section
opener"*. Claiming a preregistered analysis was structurally inadequate is a self-inflicted
credibility wound that is also false: the method was never registered.

**Proposed correction**: replace every `preregistered` qualifier on D-S with `post-hoc` or
`adopted for the 55-map ground-truth reconciliation`, and attribute the 5% prior to
Sobotkova et al. (2023). The finding (D-S is structurally unable to rank items on a
single-response-pattern slice) stands on its own merits and is arguably more interesting as a
post-hoc discovery than as a registered failure.

---

## FALSE-13 — Decision 26: "the preregistration … NOT the specific clustering algorithm"

**Claim** — `docs/methodology/preregistration/decisions-log.md:1173` (Decision 26, begins at `:1159`):

> 1. **The preregistration specifies the 20 m matching tolerance (Hungarian evaluation buffer) and
> the consensus voting framework (N passes, vote threshold sweep), but NOT the specific clustering
> algorithm that merges per-pass detections into voted candidates.** See
> `docs/methodology/preregistration/analysis-summary.md`.

Restated in `docs/notes/working-notes.md:7847-7850` and `:8113-8115`
(*"No protocol erratum required (the preregistration specifies the Hungarian tolerance and
consensus voting framework, not the clustering algorithm)"*).

**What the registration says** — `preregistration.md:1875-1885`, §8.5 *Spatial Clustering Algorithm*,
step 4 verbatim:

> 4. **Cluster detections** using distance threshold matching the F1 evaluation tolerance (20m):
>    - Detections within 20m of each other are candidates for the same cluster
>    - **Greedy clustering**: for each unclustered detection, find all others within 20m and matching label; group as cluster

**Verdict**: FALSE. The registration specifies the clustering algorithm explicitly, by name, as a
seven-step procedure. The claim rests on `analysis-summary.md`, which is not a registered document
(see U4) and which — being a plain-language summary — omits §8.5's detail. This is the clearest
case in the sweep of a non-authority being consulted *in place of* the authority.

**Severity**: **Reaches the paper.** The conclusion drawn is that swapping greedy-ball for WBF
"is not a protocol deviation" and needs no erratum. Under §8.5 it *is* a deviation and does need
one. The user's own standing preference records greedy consensus as the headline aggregation with
WBF variant C reported alongside, so both methods appear in H-series results.

**Proposed correction**: amend Decision 26 rationale 1 to *"The preregistration specifies greedy
clustering at 20 m as the consensus aggregation algorithm (§8.5 step 4, `preregistration.md:1882`).
Retaining greedy as primary is therefore protocol-compliant; reporting WBF alongside is a
post-registration robustness analysis and is recorded as such in an erratum."* This makes the
project's actual practice (greedy primary) *better* supported, not worse.

---

## FALSE-14 — wrong map scale and wrong region attributed to the registered corpus

**Claim** — `reports/experimental-progression.md:48-51`:

> The preregistration specified a sequential OFAT design testing five
> prompt engineering factors on a 60-tile holdout set drawn from four
> Soviet **1:25,000** topographic map sheets covering the **Kazanlak Valley**,
> Bulgaria.

**What the registration says**: `1:25,000` and `Kazanlak` return **zero** normalised hits across
all three canonical documents; `1:50,000` appears eight times and `Thracian` once.
`preregistration.md:19`: *"Soviet-era 1:50,000 topographic maps of Bulgaria"*;
`preregistration.md:42`: *"four manually annotated Soviet-era topographic map sheets from Bulgaria
(Thracian Plain and surrounding areas)"*; `preregistration.md:1919-1920`: *"4 Soviet 1:50,000
topographic maps (Bulgaria) — K-35-052-4_32635, K-35-053-3_Elenovo, K-35-062-2_Rakovski,
K-35-078-1_Lesovo"*.

**Verdict**: FALSE on both particulars.

**Severity**: **Reaches the paper.** Map scale is load-bearing for the whole study — the 20 m
tolerance rationale at `preregistration.md:355` is explicitly derived from symbol size *"at
1:50,000 scale"*. A 2× scale error would invalidate that rationale, and the region error
misidentifies the study area.

**Proposed correction**: `…drawn from four Soviet 1:50,000 topographic map sheets covering the
Thracian Plain and surrounding areas, Bulgaria (K-35-052-4_32635, K-35-053-3_Elenovo,
K-35-062-2_Rakovski, K-35-078-1_Lesovo).`

---

## FALSE-15 — fabricated quotation licensing the corpus expansion

**Claim** — `reports/experimental-progression.md:120-122`:

> 3. **Preregistration accommodation**: The preregistration anticipated
>    the possibility of expanding the evaluation set (Section 3.5:
>    "robustness checks on the full corpus")

**What §3.5 actually says** — `preregistration.md:294`:

> - **Spatial tolerance sensitivity**: All primary results reported at 20m; robustness checks at
>   10m, 30m, and 50m included in supplementary materials

**Verdict**: FALSE. `full corpus` returns zero normalised hits in the canonical documents. The
only "robustness checks" in §3.5 are *spatial tolerance* robustness checks; they have nothing to
do with evaluation-set size. The quotation marks enclose text that does not exist.

**Severity**: **Reaches the paper.** This is offered as one of three justifications for the
60→340 tile expansion — the largest single deviation in the study. The expansion is legitimately
documented as a Deviation in E36 (`protocol-errata.md:878-890`); dressing it up as something the
registration anticipated is both false and unnecessary.

**Proposed correction**: delete the fabricated quotation and cite E36 instead:
*"3. **Documented deviation**: the expansion is recorded as a Deviation-class erratum (E36,
`protocol-errata.md:878`); the preregistration did not anticipate evaluation-set expansion —
it reserved the 281-tile pool for Stage 2 (`preregistration.md:76`, `:2185`)."*
Note that E36's own framing correctly calls this a Deviation.

---

## FALSE-16 — H7's registered prediction inverted

**Claim** — `docs/methodology/n1-baseline-matrix.md:401-403`:

> **H7's preregistered
> T=0.0 optimum is cleanly supported within Pro text**: the two Tier-1 cells are both
> T=0.0 and the two Tier-2 cells are both T=0.7 — a clear T=0.0 > T=0.7 ordering.

**What the registration says** — `preregistration.md:711`:

> **Prediction**: T=1.0 (vendor recommended) will yield optimal or near-optimal performance.
> **Lower temperatures will degrade performance**; higher temperatures may increase variance
> without improving mean F1.

and the summary table, `preregistration.md:1158`: `| H7 (temperature) | T=1.0 optimal | …`.

**Verdict**: FALSE — it attributes to the preregistration the exact opposite of what it predicted.
T=0.0 is the *empirical* optimum found in Phase 2b; the registration predicted it would be among
the worst. T=0.0 is a registered *level* (`preregistration.md:716`), not a registered optimum.

**Severity**: **Reaches the paper.** The n1 baseline matrix is a paper board, and this sentence
converts the study's most publishable finding — a falsified vendor-recommendation hypothesis —
into a mundane confirmation. This is precisely the calibration failure `CLAUDE.md` § "Research
Finding Calibration" warns about.

**Proposed correction**: `**H7's registered prediction is falsified, and the direction is
consistent across Pro text**: the preregistration predicted T=1.0 optimal with lower temperatures
degrading performance (`preregistration.md:711`); both Tier-1 cells are T=0.0 and both Tier-2
cells are T=0.7 — a clear T=0.0 > T=0.7 ordering, reversing the registered prediction.`

---

## FALSE-17 — "the preregistered t=4 primary operating point"

**Claim** — `results/h8-v2/analysis_summary.md:219-220`:

> The "best library" depends
> on which consensus threshold one picks, and the preregistered t=4
> primary operating point gives a different winner than t=3.

**What the registration says** — `preregistration.md:1908`, the H3 parameter table:

> | T (threshold) | 1 to N | Full grid search; **no a priori threshold selection** |

**And the errata**: `protocol-errata.md:1555-1556` states *"Greedy consensus at t = 4 is the
primary / headline aggregation method for H12 (**user preference**, 2026-04-15)"*.

**Verdict**: FALSE. The registration explicitly disclaims a priori threshold selection; t=4 is a
2026-04-15 operational choice that the errata themselves attribute to user preference.

**Severity**: **Reaches the paper.** The sentence's own point is that the winner changes with
threshold — so labelling the chosen threshold "preregistered" is exactly the wrong protection
against a reviewer's threshold-shopping objection.

**Proposed correction**: `…and the production operating point t=4 (adopted 2026-04-15, E52) gives
a different winner than t=3. The preregistration specifies a full threshold grid search with no
a priori selection (`preregistration.md:1908`), so t=4 is a post-hoc reporting choice; the full
sweep is reported.`

---

## FALSE-18 — "the preregistered greedy-vs-WBF equivalence test"

**Claim** — `scripts/filter_detections_by_vote.py:16-17`:

> the apples-to-apples comparator used by the
> preregistered greedy-vs-WBF equivalence test, ``vote_t = 4`` at K = 5).

**What the registration says**: `wbf`, `weighted box` and `box fusion` return **zero** normalised
hits across all three canonical documents. WBF originates in Decision 26 (2026 audit, Obs 228),
well after lodgement.

**Verdict**: FALSE. Compounds FALSE-13 and FALSE-17 in a single clause.

**Severity**: Moderate — a docstring, but in a script whose outputs feed the WBF-variant results
reported alongside the greedy headline.

**Proposed correction**: `…the apples-to-apples comparator used by the post-hoc greedy-vs-WBF
equivalence check (Decision 26; ``vote_t = 4`` at K = 5).`

---

## FALSE-19 — the published reproducibility-kit pipeline called preregistered

**Claim** — `scripts/run_generalisation.py:6-9`:

> End-to-end publishable launcher for a single map-reader-llm generalisation
> run. Orchestrates the preregistered four-stage pipeline
> (proposer → consensus → verifier → evaluation) with comprehensive
> reproducibility metadata and cost tracking.

**Verdict**: FALSE. `four-stage` returns zero normalised hits in the canonical documents. More
substantively, the pipeline described is the PV production architecture, which E37
(`protocol-errata.md:908`) itself characterises as *"an extension beyond the preregistered design"*.
The erratum and the docstring contradict each other. (E37's own framing is separately wrong —
see FALSE-8 — but neither version supports "preregistered four-stage pipeline".)

**Severity**: **Reaches the paper's public artefacts.** The same docstring says *"Published
alongside the paper as part of the reproducibility kit"* (`scripts/run_generalisation.py:11`), so
this text ships to readers.

**Proposed correction**: `Orchestrates the production four-stage pipeline (proposer → consensus →
verifier → evaluation). The proposer and consensus stages implement the preregistered detection
and voting protocol (§§8.5, 3.8); the verifier stage implements H2 Condition B at production
scale (see erratum E37).`

---

## FALSE-20 — E10: recognition-vs-localisation distinction attributed to §8.4.2

**Claim** — `docs/methodology/preregistration/protocol-errata.md:231`:

> **Description**: The preregistration (§8.4.2) specifies that hard positive examples are drawn
> from recognition failures — false negatives where the model failed to detect a mound — rather
> than localisation errors where the model detected the mound but placed it inaccurately.

**What §8.4.2 actually says** — `preregistration.md:1510`, the sole HP row of the library table:

> | Hard positive | HP | FN mining | Cover difficult positive cases | Top K by frequency (target K=4) |

and §8.4.1 Step 2, `preregistration.md:1450`:

> - **False Negatives (FNs)**: Ground truth mounds missed in ≥3/5 passes

**Verdict**: FALSE. `recognition` appears once in `preregistration.md` (`:2137`, about visual
pattern recognition) and `localisation` once (`:347`, the 10 m buffer label *"Strict localisation"*).
Neither establishes a failure-type distinction. Under the registered definition — an unmatched
reference at the 20 m tolerance — a mound detected but mislocalised **is** an FN and **is** an
eligible HP candidate. E10 narrows the registered HP pool; it does not clarify it.
The project's own notes agree: `docs/notes/working-notes.md:1471` describes recognition-vs-localisation
as *"a distinction the preregistration did not anticipate"* — directly contradicting E10.

**Severity**: **High, and cascading.** The 50 m threshold shrank the HP pool to 4, which drove
three further deferrals that are all documented as consequences: E11 (Scale-16/Scale-32 deferred,
`protocol-errata.md:239-254`), E12 (H9 image diversity reduced to HN-only, `:258-271`), and E13
(H12 deferred, `:275-290`). An unlicensed narrowing of a registered definition removed two
registered H8 conditions and hollowed out two exploratory hypotheses.

**Proposed correction**: reclassify E10 from **Clarification** to **Deviation** and rewrite the
description: *"The preregistration draws hard positives from false negatives (`preregistration.md:1450`,
`:1510`) without distinguishing recognition failures from localisation errors. This erratum records
the post-hoc adoption of a 50 m threshold separating the two, restricting HP selection to
recognition failures. Justification: [distributional cliff evidence]. Consequence: the HP pool is
reduced to 4, triggering E11, E12 and E13."* Note that E51 (`protocol-errata.md:1413-1417`) later
re-mined 108 HP under a v2 definition and re-enabled Scale-16/32 — so the cascade is partly undone
and the paper can say so.

---

## FALSE-21 — "the preregistered setting was T = 0.7"

**Claim** — `results/limitations-consolidation/report.md:155`:

> the consensus-384 runs were executed at T = 1.0 due to a YAML-propagation failure; the
> preregistered setting was T = 0.7.

**What the registration says**: `preregistration.md:1216` fixes `temperature: 1.0` as the default
API parameter, and H7 (`preregistration.md:713-721`) tests five *levels* including 0.7. There is no
registered setting of T=0.7 for any consensus study. E43 (`protocol-errata.md:1048-1054`) is precise
about the actual source: *"The study YAML specified `fixed.temperature: 0.7` and
`carried_forward.optimal_temperature: 0.7`"*.

**Verdict**: FALSE. T=0.7 was the study-YAML intent and a production carry-forward, not a
registered setting.

**Severity**: Moderate — this is a Limitations-section source document, so it reaches the paper,
but the substantive point (runs executed at the wrong temperature) is unaffected.

**Proposed correction**: `…the intended setting, declared in the study YAML and carried forward
from production, was T = 0.7 (E43).`

---

## FALSE-22 — "preregistered estimate (40-60 symbols)"

**Claim** — `docs/methodology/reports/tile-selection-observations.md:70`:

> - Toward lower end of preregistered estimate (40-60 symbols)

**What the registration says**: `40-60`, `40–60` and `40 to 60` return **zero** normalised hits.
`preregistration.md:234` states the holdout contains 79 mounds across 60 tiles.

**Verdict**: FALSE. The document is also stale — its line 68 says *"28 mounds in holdout set"*,
which corresponds to the pre-expansion 20-tile holdout (cf. `reports/gs-tile-pool-mapping-2026-05-28.md:97`,
commit `4d011a83`, *"Expand holdout set from 20"*).

**Severity**: Low — an internal observations file, superseded by the lodged design.
**Proposed correction**: add a stale-document banner recording that it predates the holdout
expansion, and drop the "preregistered estimate" attribution.

---

# UNLICENSED

## U1 — bootstrap parameters attributed to §3.5 (10+ sites)

**Claims** (all attribute iteration count / percentile method / resampling unit to §3.5):

| File:line | Quoted text |
| :--- | :--- |
| `protocol-errata.md:1682` (E54) | `The preregistration (Section 3.5) specifies bootstrap resampling at **1 000 iterations** with the percentile method (2.5th / 97.5th) and tile-level resampling.` |
| `protocol-errata.md:1694` (E54) | `**The preregistration locks 1 000 for primary evaluation**` |
| `protocol-errata.md:491` (E22) | `This preserves the tile as the resampling unit (per preregistration §3.5)` |
| `protocol-errata.md:615` (E26) | `The preregistered statistical method (bootstrap with tile-level resampling, §3.5) is unchanged.` |
| `protocol-errata.md:869-870` (E35) | `The preregistration specifies bootstrap resampling at the tile level (Section 3.5)` |
| `scripts/lib_advanced_metrics.py:1035` | `* **Resampling unit**: tiles (the preregistered unit of analysis).` |
| `scripts/lib_advanced_metrics.py:1319` | `This preserves tiles as the resampling unit (per preregistration` |
| `scripts/lib_advanced_metrics.py:1841` | `Aligned with preregistration Section 3.5: tile-level resampling with` |
| `scripts/compute_corrected_f1_multi_buffer.py:338` | `the preregistered tile-resampling convention.` |
| `results/limitations-consolidation/report.md:185` | `1,000 iterations for preregistered primary F1; 10,000 for post-hoc narrow-effect analyses` |
| `results/limitations-consolidation/report.md:187` | `the preregistered bootstrap iteration count was 1,000.` |
| `docs/methods-outline.md:7` | `(6) **statistical methods** — 95% bootstrap confidence intervals (1,000 iterations)…` (under a document framed at `:4` as reflecting "the preregistered design") |

**What is registered**: `preregistration.md:293` — *"Report **effect sizes** … with 95%
bootstrapped CIs"*. That is all. `1,000`/`1 000` iterations: zero hits. `percentile`: zero hits.
`iteration` appears once in the whole document, at `:74`, in an unrelated table cell
(*"Prompt engineering, iteration"*). "Tile-level resampling" as a specified unit: absent.

**Actual source**: `docs/methodology/preregistration/decisions-log.md:337` (Decision 10, dated
2026-01-22), which tabulates *"Confidence intervals | Bootstrap resampling (tile-level) | 1000
iterations, percentile method (2.5th/97.5th)"*. Decision 10 predates lodgement, and its parameters
were **not carried into the registered text** — this is the bright line: pre-lodgement planning
documents do not license "the preregistration says". E54's own reference list gives the game away
at `protocol-errata.md:1704`: `Preregistration Section 3.5: docs/methodology/preregistration/decisions-log.md:337`.

**Verdict**: UNLICENSED — the practice is real, documented and defensible; the attribution is not.

**Severity**: **Reaches the paper.** E54 supplies suggested Methods wording
(`protocol-errata.md:1700`) that begins *"…(preregistered Section 3.5, percentile method 2.5th / 97.5th)"*,
and `results/limitations-consolidation/report.md` is Limitations source text.

**Proposed correction**: everywhere, replace "preregistered Section 3.5 specifies N iterations /
percentile / tile-level resampling" with *"the preregistration specifies 95% bootstrapped CIs
(§3.5); the iteration count (1,000), percentile method and tile-level resampling unit were fixed
pre-lodgement in Decision 10 (`decisions-log.md:337`) but do not appear in the registered text.
They are reported here as pre-specified analysis parameters."* This is still a strong claim —
pre-specified before data collection — just not a registered one.

---

## U2 — "first-N convention (preregistration Section 3.8)" (36 results files + 6 script sites)

**Claim** (boilerplate, verbatim in 36 files under `results/`, e.g.
`results/paper-eval/flash-high-image-20m/consensus-analysis-summary.md:50`):

> Pool selection follows the first-N convention (preregistration Section 3.8): N=5 uses runs 1-5,
> N=10 uses runs 1-10, etc.

Script sources: `scripts/analyse_consensus_sweep.py:329`, `:556`, `:973`;
`scripts/consensus-sweep-phase3a-high-text.py:12`, `:89`;
`scripts/build_phase3_subpool_consensus.py:25`.

**What §3.8 says** — `preregistration.md:325-327`:

> - N=5 voting: runs 1-5 as one pool, **runs 6-10 as another (two independent estimates)**
> - N=10 voting: all runs as single pool
> - Multiple thresholds computed for each N

**Verdict**: UNLICENSED (partial). For N=5 and N=10 drawn from a K=10 pool the convention matches
§3.8's first pool. Two things are not registered: (a) the `etc.` generalisation — these files
sweep N=5, N=10 **and N=30** (confirmed by `grep -oE 'N=[0-9]+'` across
`results/paper-eval/*/consensus-analysis-summary.md`), and §3.8 says nothing about sub-pooling a
30-run pool; (b) more importantly, "first-N" silently discards §3.8's *second* N=5 pool
(runs 6–10), which was registered specifically to give **two independent estimates**. Reporting one
pool where the registration specified two is a real, if small, loss of the registered design.

**Severity**: Low-moderate but very widespread (36 paper-evaluation summaries). Does not change
any headline number; does misdescribe the registered protocol in a document class that ships as
supplementary material.

**Proposed correction**: `Pool selection uses the first-N convention: N=5 uses runs 1-5, N=10 uses
runs 1-10, and larger N take the first N runs. The preregistration (§3.8) specifies first-N pooling
for N=5 and N=10 within a K=10 design and additionally specifies a second N=5 pool (runs 6-10) for
an independent estimate; sub-pooling of the K=30 runs is an unregistered extension.`

---

## U3 — Phase-4 transfer thresholds partly invented

**Claims**:

- `scripts/lib_phase4_transfer.py:22` — header comment `# Constants (from preregistration)` over
  `BASELINE_TRANSFER_THRESHOLD = 0.05`, `BASELINE_INVESTIGATE_THRESHOLD = 0.10`,
  `FACTOR_ADJUSTMENT_THRESHOLD = 0.03`, `VOTING_THRESHOLD_DIFFERENCE = 0.10`,
  `VOTING_EXTENDED_TEST_THRESHOLD = 0.20`
- `docs/methodology/preregistration/simulations/phase4-execution-simulation.md:326` — `### Decision Thresholds (from preregistration)`, table rows `| 4a Baseline | \|Δ F1\| ≤ 0.05 | Transfer success, proceed |` and `| 4a Baseline | \|Δ F1\| > 0.10 | Large degradation, investigate |`
- `docs/methodology/preregistration/tasks/phase4-remaining-tasks.md:67` — `## Decision Thresholds (From Preregistration)`, same two rows

**What is registered** — H6, `preregistration.md:651-701`: `≥0.03 F1` (`:677`, `:697`),
`>10% relative` (`:683`), `>20%` (`:689`), `≥20% higher F1 / ≤50% cost` (`:691`). A line-scan of
the whole H6 section for `0.0x`/`0.1x`/`%` returns no 0.05 baseline-transfer threshold and no 0.10
investigate threshold. Additionally, `AND CI excludes 0` is appended to the 0.03 rule in both docs
and in the code comment; `preregistration.md:677` has no CI condition.

**Verdict**: UNLICENSED — three of five constants are registered, two are not, and one is
augmented, all under a blanket "from preregistration" header.

**Severity**: Low in practice — H6/Phase 4 was never executed (`hypothesis-tracking.md:18`), so no
result depends on these. Worth fixing before any future H6 run.

**Proposed correction**: split the tables into "Registered (H6, `preregistration.md:677/683/689/697`)"
and "Operational, added at implementation" rows.

---

## U4 — `analysis-summary.md` cited as the preregistration

**Claims**:

| File:line | Quoted text |
| :--- | :--- |
| `protocol-errata.md:1772` (E56 Update) | `The preregistered H3 analysis plan (\`analysis-summary.md\` §H3) is *"compare voted F1 vs single-pass mean F1"*…` |
| `protocol-errata.md:1778` (E56 Update) | `No preregistration amendment is required: H3's swept-optimal reporting was preregistered (\`analysis-summary.md\` §H3).` |
| `results/diversity-dividend-384/diversity-dividend-analysis.md:101-102` | `The preregistered H3 analysis plan` / `(\`analysis-summary.md\` §H3) is "compare voted F1 vs single-pass mean F1"…` |
| `results/diversity-dividend-384/diversity-dividend-analysis.md:152` | `preregistered H3 characterisation (\`analysis-summary.md\` §H3)` |
| `results/analyses-manifest.md:13` | `Per the preregistered H3 analysis plan (analysis-summary.md: 'compare voted F1 vs …` |
| `decisions-log.md:1173` | `See \`docs/methodology/preregistration/analysis-summary.md\`.` (see FALSE-13) |
| `docs/notes/reflections/abductive-reasoning.md:5289` | `**Probe**: read the preregistered H3 analysis plan (\`analysis-summary.md\` §H3). It says, verbatim,` |
| `planning/paper-writeup-continuity.md:372` | `best (N, threshold) vs test-tile GT IS the preregistered H3 method (\`analysis-summary.md\` §…` |

**The problem**: `osf/README.md:3,9-11` names exactly three lodged documents;
`analysis-summary.md` is not one of them and does not live in `osf/`. Its own header
(`analysis-summary.md:3`) describes it as *"Plain-language overview of the statistical analysis
plan for non-specialist readers"*.

**Mitigating fact, verified**: for H3 the substance *is* registered. `preregistration.md:519-521`:

> - Compare single-pass mean F1 vs voted F1 at each (N, threshold) combination
> - Generate threshold sweep curves (F1, precision, recall vs threshold for each N)
> - Identify optimal (N, threshold) balancing performance and cost

So the swept-optimal reporting defence survives — it just needs the right citation.

**Verdict**: UNLICENSED (citation). The claims are true of the registration; the source cited is
not the registration.

**Severity**: Moderate, and structurally risky: `protocol-errata.md:1778` waives the need for a
preregistration amendment on the authority of a non-registered document (and `decisions-log.md:1173`
uses the same non-authority to reach a conclusion that the actual registration contradicts —
FALSE-13). One correct outcome and one incorrect outcome from the same substitution is exactly the
pattern that makes this worth systematically fixing.

**Proposed correction**: re-point every one of these to `osf/preregistration.md:519-521` and quote
the registered text. Add a note to `analysis-summary.md`'s header: *"Not part of the OSF
lodgement (see `osf/README.md`). Cite `osf/preregistration.md` for any claim about what was
registered."*

---

## U5 — the diversity-dividend test labelled "preregistered hypothesis H3"

**Claim** — `results/diversity-dividend-384/diversity-dividend-analysis.md:6`:

> The **diversity-dividend test** (preregistered hypothesis **H3**) asks two
> linked questions about consensus voting over multiple Vision Language Model
> (VLM) proposer passes:

The two questions (`:10-14`) are (1) does HIGH-thinking consensus beat minimal-thinking consensus,
and (2) does consensus beat single-pass.

**Assessment**: Question 2 is squarely registered H3 (`preregistration.md:501`). Question 1 is not
registered anywhere. Thinking level is a **fixed** parameter in the registration —
`preregistration.md:1211-1212` sets `thinking_level: minimal` for both Flash and Pro, and §8.9
concludes at `:2135` *"**Decision:** Use `thinking_level=minimal` for main experiment."* Nor is it
registered H9: H9's three diversity mechanisms (`preregistration.md:857-863`) are text, images and
temperature — thinking level is not among them.

**Verdict**: UNLICENSED for the headline claim. The analysis's own manifest row
(`results/analyses-manifest.md:13`) correctly marks it `exploratory`, so the framing is
inconsistent between the analysis document and the manifest.

**Severity**: **Reaches the paper.** `docs/paper/results-draft.md:121` cites the diversity dividend
as *"both preregistered"*. The finding is strong and genuinely novel — labelling it registered when
it is a post-registration discovery understates it and exposes it to a reviewer challenge.

**Proposed correction**: `The **diversity-dividend test** asks two linked questions. The second —
does consensus voting beat single-pass? — is preregistered H3 (`preregistration.md:501`). The
first — does HIGH-thinking consensus beat minimal-thinking consensus? — is a post-registration
question: the preregistration fixes `thinking_level=minimal` (§8.2, §8.9) and registered H9's
diversity mechanisms are text, image and temperature only.`

**Related gap**: no erratum documents the systematic post-registration use of HIGH thinking on
Flash. E40 (`protocol-errata.md:944-956`) covers only Gemini 3.1 Pro's inability to run MINIMAL.
`reports/experimental-progression.md:145` and `:253` attribute the HIGH-thinking deviation to
**E32**, which is about temperature (T=0.3/0.7 vs T=0.0) and says nothing about thinking level —
a wrong E-number on a deviation that has no erratum of its own. Recommend writing one.

---

## U6 — E53 calls a study YAML "the preregistered Phase 3a study"

**Claim** — `protocol-errata.md:1590-1593`:

> **Description**: The preregistered Phase 3a study
> (`studies/retest/phase3a-h3-voting-track1-high.yaml`) defined K = 30
> consensus voting experiments for the image track at 512 px (Era 1, 340
> tiles) with HIGH thinking at T = 0.3, T = 0.7, and T = 1.0.

**Assessment**: K=30 extended voting *is* registered (`preregistration.md:512`, *"Additional 20 runs
at optimal configuration"*). HIGH thinking is not (see U5). A study YAML is not the preregistration
under any reading.

**Verdict**: UNLICENSED. **Severity**: Low-moderate (an errata entry, not paper prose, but errata
are the amendment record). **Proposed correction**: `The Phase 3a image-track study YAML
(`studies/retest/phase3a-h3-voting-track1-high.yaml`), which implements registered H3 extended
voting (`preregistration.md:512`) with an unregistered HIGH-thinking factor, defined…`

---

## U7 — E49 lists an implementation choice in a "Preregistered" column

**Claim** — `protocol-errata.md:1327-1332`, table headed `| Parameter | Preregistered | H10 v2 |`,
including the row `| Crop size | 128px | 150px (aligned with verifier standard) |`.

**Assessment**: crop size is not registered. E8 (`protocol-errata.md:182`) states plainly that
*"The preregistration (§8.4.2) specifies hard example selection criteria but does not prescribe how
example crops are spatially extracted"*, and E8 `:195` records 128×128 as a choice made at
implementation. The same table's thinking-level row is honest (`(unspecified, implied minimal)`),
which makes the crop-size row's inclusion under "Preregistered" an inconsistency within one table.

**Verdict**: UNLICENSED. **Severity**: Low. **Proposed correction**: `| Crop size | 128 px
(implementation choice, E8) | 150 px (v2, verifier-aligned) |`.

---

## U8 — "the preregistered grouping rule" sourced to study YAMLs

**Claims**:

- `scripts/analyse_diversity.py:10-13` — `Implements the consensus_diversity analysis method specified in the` / `Phase 3c study YAMLs …` / `groups sub-conditions into replications using the preregistered rule:` / `Replication k = {run_k from sub-condition p1, run_k from p2, ..., run_k from p5}`
- `scripts/materialise_phase3c_consensus.py:15` — `Per the preregistered grouping rule (studies/phase3c-h9-diversity-track*.yaml,`

**What is registered**: `preregistration.md:894` — *"**Replication**: Each condition run 5 times to
provide symmetric variance estimates."* That is the whole of H9's replication specification. The
run_k-across-sub-conditions grouping rule is not in it, and both docstrings name the study YAMLs as
the actual source in the same breath as calling it preregistered.

**Verdict**: UNLICENSED. **Severity**: Low-moderate — governs how H9 replications are formed, and
H9 conclusions are reported. **Proposed correction**: `…using the grouping rule declared in the
Phase 3c study YAMLs (not preregistered; the registration specifies only that each condition is
run 5 times, `preregistration.md:894`):`

---

## U9 — "all preregistered tests were executed on Track 1"

**Claim** — `docs/methods-outline.md:166`:

> This is additive — all preregistered tests were executed on Track 1;

**Assessment**: three registered items were not executed on Track 1 or anywhere:
H2 Condition C (FALSE-2); the registered 3×3 M/E × H5 factorial, collapsed to single-factor OFAT
by E28 (`protocol-errata.md:659`, *"The preregistered 3×3 factorial … is replaced by single-factor
OFAT"*); and H8 Scale-16/Scale-32, deferred by E11 (`protocol-errata.md:239-254`) — later
re-enabled at 384 px by E51, but not on Track 1 at 512 px.

**Verdict**: UNLICENSED (over-claim). Two of the three are properly errata-documented, so the fix
is easy and costs nothing.

**Severity**: **Reaches the paper** — it is the sentence that defends the dual-track deviation as
"additive". **Proposed correction**: `This is additive — Track 1 followed the full preregistered
OFAT sequence, with three documented reductions in scope (H5's 3×3 factorial collapsed to OFAT,
E28; H8 Scale-16/32 deferred, E11, later re-run under E51; H2 Condition C not executed) — while
Track 2 added scope to explore the unexpected finding.`

---

## U10 — "512 px selected based on N=1 performance"

**Claim** — `reports/experimental-progression.md:181-182`:

> The preregistered tile-size calibration (Phase 0, 2026-01-07) selected
> 512px tiles based on N=1 performance.

and the inference built on it at `:194-196`: *"This crossover was invisible to the preregistered
N=1 screening…"*.

**What the registration says** — `preregistration.md:100` records only *"Tile size validated by
calibration pilot (2026-01-07) comparing 256px, 512px, and 1024px. 512px retained as optimal
precision-recall balance"*. §12.2, `preregistration.md:2256`, describes the pilot as
*"256px (160 tiles), 512px (40 tiles), and 1024px (10 tiles), each with **K=5 detection passes**"*,
and reports its scale characteristics *"(at 2/5 voting threshold)"* (`:2262`). The registered
description is therefore K=5 with voting, not N=1.

**Verdict**: UNLICENSED — not supported by the registered text, and apparently contradicted by it.

**Severity**: Moderate. The N=1 framing is load-bearing for the report's tile-size×architecture
narrative, which is a paper finding.

**What would settle it definitively**: `archive/pilot-tile-size/outputs/pilot_decision.md` and
`archive/pilot-tile-size/outputs/pilot_results.json` (both listed at `preregistration.md:2099-2101`)
— specifically whether the single-scale decision used K=1 or K=5. The registered *description* is
K=5 either way, so the sentence needs rewording regardless.

**Proposed correction**: `The preregistered tile-size calibration (2026-01-07) selected 512 px on
single-scale precision-recall balance (`preregistration.md:100`); the registered multi-scale pilot
was run at K=5 with a 2-of-5 voting threshold (§12.2). Neither pilot evaluated the consensus+PV
architecture that later reversed the ranking.`

---

## U11 — "ONE preregistered pair — no multiple-comparison correction applies"

**Claim** — `scripts/permutation_opmax_vs_headline.py:28-29` and `:201`:

> # permutation test (10k, seed 42, two-sided). ONE preregistered pair — no
> # multiple-comparison correction applies.

**Assessment**: the test is a permutation test (unregistered — FALSE-9), and the opmax-vs-headline
comparison is a post-hoc contrast between two production operating points, not a registered
planned contrast. The registered planned contrasts are enumerated per hypothesis
(`preregistration.md:437-441`, `:570-572`, `:727-728`, `:775-798`). Waiving multiple-comparison
correction on the grounds that a pair was "preregistered" is the substantive risk here.

**Verdict**: UNLICENSED. **Severity**: Moderate — an unregistered single-comparison exemption from
FDR is exactly the kind of thing a reviewer probes.

**Proposed correction**: `# ONE pre-specified contrast chosen before the test was run (not
preregistered); reported without multiple-comparison correction, and labelled post-hoc.`

---

## U12 — H9 recorded as COMPLETE with a null result on a design that was not run

**Claims** — `docs/methodology/preregistration/hypothesis-tracking.md`:

- `:28` — `| H9 | Diversity Mechanisms | Text/Image/Temp diversity | A | Complete (implicit) | 2026-03-07 |`
- `:245` — `Prompt/parameter diversity does not improve consensus — confirmed null result.`
- `:246-248` — `The formal H9-A through H9-E conditions were not run as separate experiments;` / `the finding emerged from Phase 3a's multi-temperature, multi-run design which` / `inherently tested temperature diversity (H9-D).`
- `:284` — `├── Phase 3c: H9 (Diversity — implicit)            ✓ COMPLETE`

**Assessment**: the document is admirably explicit at `:246` that the registered conditions were
not run — but then records H9 as COMPLETE with a "confirmed null result". The registered H9 design
(`preregistration.md:855-863`) is five conditions A–E varying text, image and temperature
diversity. By the file's own account only the temperature arm (H9-D) was incidentally exercised;
text diversity (H9-B), image diversity (H9-C) and full diversity (H9-E) were not tested — and E12
(`protocol-errata.md:258-271`) separately records that H9-C could only ever have run as
HN-diversity-only.

**Verdict**: UNLICENSED — a null asserted for a registered hypothesis on evidence covering one of
its three mechanisms.

**Severity**: **Reaches the paper.** `docs/paper/results-draft.md:123` states *"engineered
diversity, however, adds nothing: the preregistered H9 test of…"*. Note also the tension with the
diversity-dividend finding (U5), which reports a large, significant diversity effect from a
mechanism H9 did not register.

**Proposed correction**: change the status to `Partially tested (H9-D only; H9-B/C/E not run)` and
reword `:245` to *"Temperature diversity does not improve consensus (H9-D, tested incidentally via
Phase 3a). Text diversity (H9-B), image diversity (H9-C) and full diversity (H9-E) were not
tested."* Then reconcile against the diversity-dividend result, which shows a different diversity
mechanism (thinking level) *does* help.

---

# STALE

| # | File:line | Claim | Current truth |
| :--- | :--- | :--- | :--- |
| S1 | `docs/methods-outline.md:16` | `- Preregistered, stranded-factorial study (OSF registration, 2026-01-31)` | Stranded factorial was the **v3.5** design (`preregistration.md:2404`). Lodged v4.7 is sequential OFAT (`preregistration.md:1705`, `preregistration-coverage.md:58-69`). The same error is in `CLAUDE.md:7` and was already diagnosed as a confabulation risk in `docs/notes/working-notes.md:1141` and `:1153`. Reaches the paper. |
| S2 | `reports/experimental-progression.md:26` | `sequential design (OSF registration v4.6, 2026-01-14) that was` | Lodged v4.7, 2026-01-31 (`protocol-errata.md:5`; E1 at `:30` corrected exactly this stale date elsewhere). Note the lodged file's own header (`preregistration.md:9-10`) and footer (`:2388`) still say v4.6 / 2026-01-14 while its changelog top entry is v4.7 — see UD-2. |
| S3 | `reports/experimental-progression.md:39` | `errata (47 entries, E1–E47) maintained alongside the preregistration` | E1–E57 (`protocol-errata.md:1782`). |
| S4 | `docs/methodology/documentation-index.md:17` | `\| Deviations, corrections, clarifications \| EN \| E1–E34 \|` | E1–E57. |
| S5 | `results/limitations-consolidation/report.md:301`, `:330` | `**§4 Methodological deviations (E1–E54)**` / `E1 – E54 errata register.` | E1–E57; E55–E57 include the finding-affecting E57 billing reconciliation. Reaches the paper (Limitations). |
| S6 | `docs/planning/future-work.md:7`, `:13`, `:148` | `the preregistration document (… v4.2)` / `All 15 hypotheses are formalised in the preregistration (v4.2)` / `**Preregistration finalised** (v4.2)` | v4.7. Hypothesis content changed substantially between v4.2 and v4.7 (`preregistration.md:2394-2402`). |
| S7 | `docs/methodology/preregistration/hypothesis-tracking.md:18` | `\| H6 \| Flash→Pro Transfer \| Model \| 4 \| Not started \| — \|` | E41 (`protocol-errata.md:960-972`) ran a Pro comparison as an exploratory extension, and E57's Update (`protocol-errata.md:1844`) reports *"H6 (Pro ≥ Flash) now holds uniformly at the top"* from the genuine-Pro re-run. File last updated 2026-04-15 (`hypothesis-tracking.md:5`), E57 Update dated 2026-06-03. Reaches the paper via `docs/methods-outline.md:341`. |
| S8 | `docs/methodology/reports/tile-selection-observations.md:68` | `- 28 mounds in holdout set` | Lodged design: 60 holdout tiles, 79 mounds (`preregistration.md:234`). Predates the holdout expansion (`reports/gs-tile-pool-mapping-2026-05-28.md:97`, commit `4d011a83`). See also FALSE-22. |
| S9 | `docs/planning/interaction-triggers-for-followup.md:12` | `The main experiment uses a sequential OFAT design (preregistration v4.6):` | v4.7. Low severity — design description is still correct. |

---

# UNDETERMINABLE

## UD-1 — the preregistration contradicts itself on the H11 trigger

`preregistration.md:948` (H11's own trigger):

> **Trigger**: Run if detection performance on 512×512 tiles shows room for improvement (**F1 < 0.85**)
> or if processing speed is a concern for deployment.

`preregistration.md:2225` (the preregistration checklist):

> - [x] Specify success threshold: **F1 ≥ 0.85** triggers H11 tile size testing

These are mutually exclusive. `reports/experimental-progression.md:182-183` cites the H11-section
version (*"a preregistered conditional hypothesis (to be tested if F1 < 0.85)"*), which is the
substantive one — but any document citing "the preregistered H11 trigger" inherits an ambiguous
source, and a reviewer reading the OSF record will find both.

**What would settle it**: nothing inside the repository — both readings are in the lodged text.
Retrieve the OSF registration record to confirm the repo copy matches what was lodged; then handle
it as a documented internal inconsistency in the Methods section (the honest move: report both
lines and state that H11 was run under the §H11 trigger).

## UD-2 — the lodged file's own version metadata is inconsistent

`preregistration.md:9-10` reads `**Document version**: 4.6` / `**Last updated**: 2026-01-14`;
`:2388` reads `*Document version: 4.6*`; `:2390` reads `*Updated: 2026-01-31*`; and `:2394` is a
v4.7 changelog entry. `osf/README.md:22` and `protocol-errata.md:5` both assert v4.7 (2026-01-31),
and E1 (`protocol-errata.md:21-32`) records correcting this exact stale date in the companion
README — but not in the primary document's header.

**Consequence**: S2 (`reports/experimental-progression.md:26`, "v4.6, 2026-01-14") is defensible
if read off the lodged file's header and wrong if read off the errata. Both are internal.

**What would settle it**: the OSF registration page's version and timestamp. If OSF shows v4.7 /
2026-01-31, an erratum should record the primary document's stale header the way E1 recorded the
README's.

## UD-3 — the registered baseline pass count is internally inconsistent

`preregistration.md:815` states hard examples are drawn *"from failures across **K=10** baseline
runs"*, while §8.4.1 Step 1 (`preregistration.md:1443`) specifies *"Passes: **5** × 20 training
tiles = 100 API calls"* and Step 2 (`:1450`) thresholds at *"≥3/5 passes"*. E15
(`protocol-errata.md:311-331`) addresses the same inconsistency in the *appendix* and resolves it
to K=5, but does not mention `preregistration.md:815`.

**Consequence**: any claim of the form "the preregistered baseline K was N" is citing an ambiguous
source. No current claim in scope depends on it, so this is prophylactic.

**What would settle it**: extend E15 to cover `preregistration.md:815` explicitly, recording K=5
as operative (which matches execution) and the K=10 reference as a drafting residue.

## UD-4 — E11's quotation is a hybrid of two registered lines

`protocol-errata.md:250` quotes *"If fewer than 16 distinct HPs or HNs are available, Scale-32
(and possibly Scale-16) will be capped at the maximum available **while preserving 1:1 ratio**"*
and attributes it to `preregistration line 815`. Line 815 ends *"…capped at the maximum available,
**maintaining 1:1 ratio**"*; the phrase *"while preserving 1:1 ratio"* comes from
`preregistration.md:773` (the H8 table footnote), which lacks the *"(and possibly Scale-16)"* clause.

**Verdict**: the substance is registered twice over and the erratum's conclusion is correct — this
is a quotation-hygiene defect, not a false attribution. Flagged because the sweep's standard is
that quotation marks mean verbatim.

**Proposed correction**: quote `preregistration.md:815` verbatim, and cite `:773` separately.

---

# SOUND — summary table

Sampled and verified against the canonical text. This is the large majority of substantive
attributions in the repository.

| File:line | Claim (abridged) | Registered at | Note |
| :--- | :--- | :--- | :--- |
| `protocol-errata.md:364` (E17) | `§3.8 … "K=10 independent **single-pass** runs"` + `"without assuming voting (which is itself under test in H3)"` | `preregistration.md:315`, `:317` | Both quotations verbatim and correctly located |
| `protocol-errata.md:552-560` (E25) | H1 M/E factor has 5 levels, text-only receives no images | `preregistration.md:412-418` | Line numbers exact; section label "4.1.1" is off (it is §5/H1) but harmless |
| `protocol-errata.md:1498-1499` (E52) | `H12's preregistered trigger is "run if H8 shows library size matters" (preregistration line 1010)` | `preregistration.md:1010` | Exact quote at the exact line — model citation |
| `protocol-errata.md:1300-1306` (E48) | §8.4.1 M=3 vs §8.4.2 4:2:4:4:3 and 1:1 ratio | `preregistration.md:1460`, `:1514`, `:813`, `:769` | Every anchor checked and correct |
| `protocol-errata.md:1352-1357` (E50) | 60-tile H10 holdout; pools 20/40/80/160 as registered | `preregistration.md:914-919` | Correct |
| `protocol-errata.md:1416-1417` (E51) | `Scale-16 and Scale-32 were preregistered` | `preregistration.md:770-771` | Correct |
| `protocol-errata.md:182` (E8) | §8.4.2 does not prescribe crop extraction | `preregistration.md:1502-1521` | Correct negative claim |
| `protocol-errata.md:431` (E20) | `Preregistration uses "holdout tiles" (§2.1)` | `preregistration.md:75` | Correct |
| `protocol-errata.md:888` (E36) | preregistered Phase 3 used a 60-tile holdout | `preregistration.md:75`, `:150-234` | Correct; properly classified Deviation |
| `protocol-errata.md:952-954` (E40) | §8.2 specifies `thinking_level=minimal` for Flash and Pro | `preregistration.md:1211-1212` | Correct |
| `protocol-errata.md:970` (E41) | H6 specifies a 20-tile stratified holdout subset | `preregistration.md:662` | Correct; `§3.6` label is off (that is Power Considerations) |
| `protocol-errata.md:1254` (E47) | `The preregistered primary tolerance is 20 m (Section 3.5)` | `preregistration.md:294`, `:341` | Correct — and the reversion restores registered alignment |
| `protocol-errata.md:1322-1323` (E49) | calibration = image-only baseline, T=1.0, K=5 passes | `preregistration.md:1442-1445` | Correct on all three |
| `hypothesis-tracking.md:61-64` | registered null prediction contradicted; GO criterion ΔF1 ≥ 0.05 exceeded | `preregistration.md:461`, `:491`, `:493` | Correct and well-calibrated |
| `hypothesis-tracking.md:129-131` | H4b trigger = H4 significant; not triggered | `preregistration.md:1100` | Correct |
| `hypothesis-tracking.md:163` | `**Preregistered design was**: 3×3 factorial (3 image-using M/E × 3 H5)` | `preregistration.md:1333-1340` | Correct, and correctly attributes the simplification to Decision 17 / E28 |
| `hypothesis-tracking.md:173-178` | H6 decision rule `Adjust if Δ ≥ 0.03 F1` | `preregistration.md:677` | Correct |
| `results/phase2a-carry-forward-parameters.md:33` | preregistered OFAT specified single-best carry-forward | `preregistration.md:1705-1734`, `:1688-1693` | Correct |
| `results/phase2a-carry-forward-parameters.md:63-64` | Scale-8 and canonical-first as preregistered defaults | `preregistration.md:1760`, `:627`, `:1852` | Correct |
| `results/phase2b-carry-forward-parameters.md:122-125` | preregistration specified testing T=0.0, 0.3, 0.7, 1.0, 1.3 | `preregistration.md:715-721` | Correct |
| `results/phase3d-pilot-results.md:92` | `exceeds the preregistered stopping criterion of ≥0.05 ΔF1` | `preregistration.md:491`, `:493` | Correct |
| `results/h8-v2/analysis_summary.md:228-230` | six directional predictions, `prereg lines 799–806` | `preregistration.md:801-806` | Correct, well-anchored |
| `results/h8-v2/analysis_summary.md:11`, `:357` | BH-FDR at q=0.05 over 7 preregistered contrasts | `preregistration.md:270`, `:775-798` | Correct (C1–C3, S1–S3, B1 = 7) |
| `results/h12-v2/analysis_summary.md:19`, `:109` | 3 preregistered pairwise contrasts; directional prediction at `prereg lines 988–989` | `preregistration.md:996-1000`, `:987-989` | Correct; H12 has no formal "Predictions" heading, so "prediction" reads Background text — acceptable |
| `results/h12-v2/analysis_summary.md:20`, `:150` | preregistered directional prediction **falsified** | `preregistration.md:987-989` | Correct, and correctly flagged as contradicting the registration |
| `results/h10/analysis_summary.md:234-241` | E49 deviation from the preregistered image-only baseline | `preregistration.md:1442-1445` | Correct |
| `results/factor-analysis/factor_analysis_results.md:77` | 20 m is the preregistered primary tolerance | `preregistration.md:294` | Correct |
| `results/h11-tile-size-results.md:65` | `20 m (preregistered default)` | `preregistration.md:341` | Correct |
| `docs/methodology/n1-baseline-matrix.md:90`, `:95`, `:104` | 20 m preregistered headline; tile-level MCC per `preregistration §4.2` | `preregistration.md:294`, `:379-394` | Correct |
| `docs/methodology/n1-baseline-matrix.md:408-411` | board framed `exploratory`; "not itself in the preregistered analysis plan" | — | Model of correct framing |
| `docs/methods-outline.md:173` | `K=10 independent single-pass runs per condition per phase (preregistered)` | `preregistration.md:315` | Correct (E36 later reduced K; noted there) |
| `docs/methods-outline.md:352` | `Two-stage improvement (H2): Contradicted preregistered null` | `preregistration.md:461` | Correct |
| `docs/methods-outline.md:276` | registered at OSF prior to confirmatory data collection (2026-01-31) | `protocol-errata.md:5`; `osf/README.md:22` | Correct |
| `scripts/merge_passes.py:6`, `:144`, `:229`, `:328`, `:349` | voting algorithm per §8.5, steps 1–6 and consensus output | `preregistration.md:1861-1894` | Every step reference checked and correct |
| `scripts/lib_advanced_metrics.py:1187-1189` | quotes §3.5 effect-size bullet verbatim | `preregistration.md:293` | Verbatim-accurate |
| `scripts/lib_advanced_metrics.py:1723` | `Implements preregistration Section 4.2: Tile-level Discrimination (MCC)` | `preregistration.md:379-394` | Correct |
| `scripts/lib_advanced_metrics.py:17`, `:1537` | M/E × H5 bootstrap interaction test | `preregistration.md:638-645` | Correct |
| `scripts/analyse_study_effects.py:7-13` | quotes §3.5 and §4.2 | `preregistration.md:293`, `:379` | Verbatim-accurate |
| `scripts/n1_baseline_leaderboard_tiering.py:98` | `HEADLINE_BUFFER_M = 20  # preregistered headline buffer` | `preregistration.md:294`, `:341` | Correct |
| `scripts/lib_consensus.py:20-21` | 20 m threshold consistent with the preregistered design | `preregistration.md:1880`, `:1909` | Correct |
| `scripts/lib_calibration.py:38`, `:139`, `:223` | density strata and tile-selection strategy from the preregistration | `preregistration.md:1934-1946` | Correct |
| `scripts/select_tiles_phase2.py:519` | different dates with different seeds per preregistration | `preregistration.md:1944` | Correct |
| `scripts/lib_hypothesis_requirements.py:239` | `preregistered levels (0.0, 0.3, 0.7, 1.0, 1.3)` | `preregistration.md:1421`, `:715-721` | Correct |
| `scripts/summarise_h12v2.py:138` | `Preregistered prediction: HN-heavy -> higher P, HP-heavy -> higher R` | `preregistration.md:987-989` | Directionally correct against Background text |
| `docs/notes/working-notes.md:1471` | recognition-vs-localisation is `a distinction the preregistration did not anticipate` | `preregistration.md:1450`, `:1510` | Correct — and contradicts E10 (FALSE-20) |
| `docs/notes/working-notes.md:8542` | `The preregistration specifies 20 m` | `preregistration.md:294` | Correct |
| `docs/notes/working-notes.md:16700` | tile-level MCC per threshold as `preregistered-secondary (§4.2)` | `preregistration.md:379` | Correct |
| `docs/notes/working-notes.md:10086` | H12 `technically fails the preregistered trigger` | `preregistration.md:1010` | Correct, honestly stated |
| `docs/paper/results-outline.md:486-493` | flags E45 as mis-describing permutation as preregistered; `grep -c -i permutation … returns 0` | independently reproduced in this sweep | Correct — the project's own audit reached FALSE-9 first |
| `docs/paper/results-outline.md:475-477` | `analysis-summary.md:82` vs `osf/preregistration.md:453` on H2 status | — | Correctly identifies `osf/` as the authority |
| `docs/methodology/preregistration/execution-plan.md:405`, `:600` | K=10 per §3.8; H2 stopping rule ≥0.05 F1 | `preregistration.md:315`, `:491` | Correct |
| `results/phase2e-carry-forward-parameters.md:23` | `E30: Phase 2e tests 4 ordering conditions instead of preregistered 3` | `preregistration.md:550-554`; E30 | Correct |
| `results/retest/phase2b/analysis_summary.md:151`, `:159` | preregistered five-temperature sweep at 340 tiles | `preregistration.md:715-721`; E36 | Correct |
| `reports/adversarial-audit-report.md:224`, `:260`, `:280` | F1 > 0.9 holds at 30 m but not at the preregistered 20 m | `preregistration.md:294` | Correct, and appropriately conservative |
| `reports/configuration-audit-2026-04-15-h8-v2.md:25`, `:173` | seven library conditions at `§H8 line 764`; diminishing-returns prediction | `preregistration.md:763-771`, `:806` | Correct |
| `reports/experimental-progression.md:70`, `:255` | 4 orderings vs preregistered 3; 20 m primary restored | E30; `preregistration.md:294` | Correct |
| `planning/leaderboard-construction-plan.md:533`, `:543` | reasoning about when `exploratory` vs `preregistered-with-deviation` applies | — | Model of careful attribution discipline |

---

# Addendum — `docs/notes/**` sweep (246 candidates triaged)

The reflection and working-notes corpus was swept separately. It is largely **SOUND** and in
places is the most careful writing in the repository — `working-notes.md:1471` correctly states
the preregistration *did not* anticipate the recognition/localisation distinction (contradicting
E10, FALSE-20); `working-notes.md:16697-16701` records a deliberately unprimed registration-status
check that correctly classifies the H3 sweep as registered, tile-MCC as registered-secondary, and
the verifier value-add as exploratory; `abductive-reasoning.md:2486` correctly limits §8.9's
MINIMAL conclusion to single-pass detection; and `llm-observations.md:1808-1811` is a self-caught
confabulation of exactly this class, corrected in place.

Three additions to the findings above.

## FALSE-18 is a family, not a single site — "the preregistered greedy≈WBF equivalence"

Additional sites beyond `scripts/filter_detections_by_vote.py:17`:

| File:line | Quoted text |
| :--- | :--- |
| `docs/notes/reflections/session-reflection.md:8343` | `0.39 gap that flatly contradicts the project's *own* preregistered greedy≈WBF equivalence. The` |
| `docs/notes/reflections/llm-observations.md:6121` | `transcription would have shipped it next to greedy's 0.71, making the preregistered greedy≈WBF` |
| `docs/notes/reflections/llm-observations.md:6129` | `established result (here, a preregistered equivalence), treat it as evidence the *pipeline* is` |
| `docs/notes/reflections/abductive-reasoning.md:5046` | `preregistered equivalence. The "WBF fails" reading was an artefact of an apples-to-oranges` |
| `docs/notes/working-notes.md:17406` | `would have appeared to contradict the preregistered greedy≈WBF robustness claim recorded in \`docs/methodology/preregistration/decisions-log.md\`` |

`wbf`, `weighted box` and `box fusion` return zero normalised hits across all three canonical
documents. The equivalence check originates in Decision 26 (`decisions-log.md:1159`, 2026-04) —
which itself rests on FALSE-13. **Verdict**: FALSE across the family. **Severity**: notable because
`working-notes.md:17373` and `:17406` record that the belief "this contradicts a *preregistered*
equivalence" was the heuristic that caught a real data-pipeline bug (Obs 340). The heuristic worked;
its stated warrant is wrong. Correction: `the greedy≈WBF equivalence established in Decision 26`.

## FALSE-17 is a family — "the preregistered vote threshold"

| File:line | Quoted text |
| :--- | :--- |
| `docs/notes/working-notes.md:17417` | `This is the preregistered vote threshold; no new calibration was introduced.` |
| `docs/notes/working-notes.md:8178` | `anchor_vote_threshold adjusted from 6 (10-pass) to **4** to match the 5-pass pipeline's preregistered 4-of-5 voting optimum` |
| `docs/notes/reflections/session-reflection.md:6465` | `refinement that matches the preregistered vote threshold as the` |

Against `preregistration.md:1908` (`| T (threshold) | 1 to N | Full grid search; **no a priori
threshold selection** |`). **Verdict**: FALSE. A registered *sweep* has been converted into a
registered *value*.

**Related, UNLICENSED**: `protocol-errata.md:1755` (E56) states *"The preregistered
calibrate-then-test split governs the **consensus vote threshold** (Phase 1 baseline calibration on
the 20 held-out calibration tiles, ≥3/5)"*, restated at `session-log.md:6328`,
`abductive-reasoning.md:4869` and `session-reflection.md:8091`. The registered ≥3/5 threshold
(`preregistration.md:1450-1451`) governs **hard-example mining** in §8.4.1 Step 2 — which FNs and
FPs qualify as HP/HN candidates — not consensus vote-threshold calibration. The distinction matters
because E56's three-way provenance split rests on it.

## NEW — an orphan erratum under a duplicate number: the registered proposer prompt was never used

`docs/notes/working-notes.md:6556` declares:

> ## Erratum E47: Proposer Prompt Substitution — `detect_brief-text` Used Instead of Preregistered `propose_brief` (2026-04-08)

and at `:6560`: *"The preregistration (§ Appendix, Config Files table) specifies `propose_*.json` +
`verify_*.json` for H2"* — which is **correct**: `preregistration.md:2015` reads
`| H2 | \`propose_*.json\` + \`verify_*.json\` (coarse-to-fine); … |`, and the prompt itself is
lodged at `preregistration-appendix-prompts.md:1042-1086`. `:6636` records that *"The `propose_brief`
prompt was written, preregistered, refined (5e7601d7), and **never used**"*.

**Three problems**:

1. **Number collision.** The canonical register's E47 (`protocol-errata.md:1236`) is
   *"Primary spatial matching buffer reverted to preregistered 20 m"*. Two different deviations
   share E47.
2. **Not in the canonical register at all.** `grep -i 'propose_brief\|proposer prompt substitution'`
   over `protocol-errata.md` returns **zero hits**. A reader following the errata register — the
   amendment record a reviewer trusts — will never learn that the registered H2 proposer prompt
   was not used in any PV experiment.
3. **The one cross-reference has a broken anchor.**
   `results/documentation-audit/results-audit-2026-04-21.md:430` cites it as
   `docs/notes/reflections/working-notes.md line 6553`. That path **does not exist** (the file is
   `docs/notes/working-notes.md`) and line 6553 is blank; the heading is at 6556.

**Verdict**: this is not a false attribution — the underlying claim is correct and unusually
well-evidenced (`working-notes.md:6603-6605` quantifies the difference; `:6786` reports the honest
conclusion that the substitution *"was accidentally the right design choice"*). It is a
**register-integrity defect** in the amendment trail, and it sits on the same H2 material as
FALSE-8.

**Proposed correction**: promote it to the canonical register as **E58**, cross-referencing the
working-notes analysis; add a "superseded numbering" note at `working-notes.md:6556`; and fix the
path and line in `results-audit-2026-04-21.md:430`.

## Also noted (lower severity)

- `docs/notes/working-notes.md:17189` repeats the FALSE-16 error class in its pre-E57 form
  (`H7's preregistered T=0.0 optimum does not reappear cleanly at the top`). Same correction.
- `docs/notes/working-notes.md:8616` puts a paraphrase inside quotation marks: *"The preregistration
  picked 20 m "to account for georeferencing imprecision and symbol size""*. The registered text
  (`preregistration.md:352-355`) is a three-item bulleted list, not that sentence. Quote-hygiene only;
  the substance is right. The same paragraph's substantive finding — that the registered 20 m buffer
  systematically under-rates the image track — is a genuine and well-argued methodological point.
- `docs/notes/working-notes.md:11241` uses `preregistered` loosely to mean "pre-planned"
  (`This was preregistered as the cross-modality pair of the prior text-based 55-map run`). The
  55-map generalisation runs are not in the registration. Reword to `pre-planned`.
- The D-S family (FALSE-12) has four further sites in the notes: `working-notes.md:12875`, `:12877`,
  `:12893`, and `abductive-reasoning.md:3945` (all `preregistered 5 % student-FN prior` / `preregistered v1`).
- The `analysis-summary.md`-as-registration family (U4) has six further sites:
  `working-notes.md:18074`, `session-reflection.md:8568`, `abductive-reasoning.md:5289`,
  `llm-observations.md:6259`, `session-log.md:6880`, `user_observations.md:202` and `:205`.
- The clustering-algorithm claim (FALSE-13) has two further sites: `session-log.md:4028` and `:4107`.

---

# Cross-cutting observations

1. **The dominant failure mode is source substitution, not invention.** Most non-SOUND findings
   trace to a non-registered document being consulted in place of the registration: Decision 10 for
   bootstrap parameters (U1), study YAMLs for decision rules (FALSE-3/4/5/6/7), and
   `analysis-summary.md` for H3 and clustering (U4, FALSE-13). Only four claims appear to be
   invented outright: FALSE-4, FALSE-5, FALSE-15, and the D-S family (FALSE-12).

2. **Directory location confers false authority.** `decisions-log.md`, `hypothesis-tracking.md`,
   `execution-plan.md`, `analysis-summary.md`, `tasks/` and `simulations/` all live under
   `docs/methodology/preregistration/`, one level above the actual lodgement in `osf/`. Every
   decision-rule misattribution originates in that directory. A `NOT-REGISTERED.md` marker or a
   header banner on each non-lodged file would close most of this class structurally.

3. **The errata register is itself a source of false attributions.** E10, E37, E45 and E54 each
   misdescribe what the preregistration says — and E37 and E45 do so in the direction that makes
   the study look *weaker* than it is (a registered hypothesis reported as unregistered; a
   registered method reported as the one being deviated from). Errata are the amendment record a
   reviewer trusts most, so errors there are disproportionately costly.

4. **Three findings are stronger than the documents claim.** Correcting FALSE-8 upgrades the PV
   result from "post-hoc extension" to "confirmatory hypothesis, registered null falsified";
   correcting FALSE-16 upgrades T=0.0 from "confirms H7" to "falsifies the registered
   vendor-recommendation prediction"; correcting FALSE-12 removes a self-inflicted Limitations
   admission about an analysis that was never registered. The corrections make the paper better,
   not worse.

5. **Two errata-coverage gaps surfaced.** The omission of H2 Condition C (FALSE-2) and the
   systematic use of HIGH thinking on Flash (U5) are both real protocol deviations with no
   erratum. `reports/experimental-progression.md:145` and `:253` attribute the latter to E32,
   which concerns temperature.
