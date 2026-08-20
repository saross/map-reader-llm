# Session 137 audit report

> **Last revised**: 2026-08-20 (evening: remediation campaign recorded — every Part F item
> and all register-facing findings executed same day; see the Changelog). Original
> publication earlier the same day.

**Auditor**: Claude (Fable 5), Session 138, 2026-08-20, working from the self-contained brief
`planning/session-137-audit-brief.md` written by the Session 137 instance. Four parallel
Opus-class subagent auditors hunted the brief's § 2 error classes (code-side, data-shape,
regeneration/reproducibility, and prose/consistency); the main instance re-derived the § 1
claims, ran the D24 coverage simulation, and independently re-verified every headline finding
below before including it. Findings verified only by a subagent are marked as such.

**Environment**: zbook, away from the home network — sapphire unreachable (connection timed out;
verified before starting). Everything below ran locally at US$0 API spend. Tier-1 suite
re-confirmed green on zbook before work began: 1,593 passed, 1 skipped, 3 xfailed. Tier-2
(never run in Session 137) was also run — result in § Checked and confirmed.

**Scope**: commits `2907713f3`..`8dc01fca4` on parent `3abec641a`. Per the brief: findings are
classified **wrong** (the claim fails), **unsupported** (may be true, evidence does not
establish it), or **fragile** (true now, will break). Nothing was fixed; the working tree is
clean at `8dc01fca4`. Scratch artefacts (verification scripts, captured diffs, the coverage
simulation) live in the session scratchpad, quoted inline where needed.

## Verdict in three sentences

Session 137's core corrections are sound: the Hsu MCB re-tiering is internally consistent
(all fourteen register tie sets exactly equal their committed artefacts), the 49-evaluation
re-run moved no deterministic point estimate, the clique argument reproduces exactly, and the
D24 coverage simulation run for this audit finds the bootstrap critical value **conservative,
not anti-conservative**, on all three boards tested. The audit nevertheless found one committed
register value that does not survive the project's own standard (the `n1-baseline-matrix-384`
tie set was computed at B = 200 and shrinks from 4 to 3 members at B = 10,000), and a
systematic pattern in which Session 137's corrections landed in code but not in the committed
artefacts, and in primary documents but not in the summaries derived from them. The error
classes the brief predicted would recur did recur — most consequentially in the paper-facing
prose, the register outcome texts, and the provenance metadata.

---

## Part A — Findings

Ranked by consequence. Class numbers refer to the brief's § 2.

### F1 — WRONG. The `n1-baseline-matrix-384` tie set was computed at B = 200 and does not survive B = 10,000: it is 3 members, not 4

`results/selection-aware/n1-baseline-matrix-384_b20_m1.json` records `"bootstrap": 200` — every
other board artefact records 10,000 (one supplementary MCC artefact records 2,000). The D24
statistician brief (`docs/methodology/mcb-critical-value-open-question.md:58`) states B = 10,000
for all fourteen boards. The fourth admissible member, `baseline-pro-text-high-t-0-7`, clears
admissibility by **+0.0004** on a critical value that is the 190th of 200 order statistics.

**Settled by re-run** (this audit, zbook, $0). The board's per-tile counts were rebuilt through
the session's own loader — every cell reproducing its committed evaluation F1 — and the exact
sequential procedure re-run. At the committed B = 200, seed 42, the artefact reproduces
exactly (`w_upper` 0.059911, set {8, 9, 15, 16}), confirming this is a real property of the
committed artefact and not a loader difference. At **B = 10,000** the admissible set is
**{9, 15, 16}** — `baseline-pro-text-{medium-t-0-0, high-t-0-0, medium-t-0-7}` — stable across
seeds 42, 1, and 2 (`w_upper` 0.0571–0.0582; the dropped cell is excluded by 0.001–0.002 at
every seed). The register's published revision 2 → 4 should have been **2 → 3**.

Two knock-ons. (a) E82's own rule — paper-facing text must not quote a value until the cell
behind it is re-emitted at B = 10,000 — was violated by the session's own new instrument on
this board. (b) The correct 3-member set **still spans both temperatures** (medium-T0.7 stays
in), so the results-draft sentence at `docs/paper/results-draft.md:179-181` ("the two Tier-1
cells run at T = 0.0 and the two Tier-2 cells at T = 0.7"), which supports the H7 reversal
narrative, fails under the corrected set too — see F2.

Found by the prose auditor (class 13); settled numerically by the coordinator.

### F2 — WRONG. The results-draft E83 banner misstates what was done, and the four `[E83]` flags are not the complete set

Two parts, both in paper-facing documents.

**(a) The banner.** `docs/paper/results-draft.md:9-10` says "Four 55-map boards and two others
could not be recomputed and remain on the superseded instrument — see E83." E83 itself says
all fourteen boards are on MCB (`protocol-errata.md:4802`, "ten revised, four confirmed
unchanged"; the two `--batch` boards recovered in `85a442e96`, the four 55-map boards re-tiered
in `1908d7917`). The banner was written at `ee0a381ff` (the eight-board stage) and never
revisited. It tells a future reader six boards are still on a known-defective instrument.

**(b) Flag completeness** (the check the brief's § 4 asked for). The four flags at lines 70,
141, 230, and 247 are **not** the complete set. Affected but unflagged in `results-draft.md`:

- **Lines 179–181** — the `n1-baseline-matrix-384` temperature-split sentence (see F1). The
  two cells the sentence assigns to "Tier 2" are precisely the cells MCB admits.
- **Lines 347–349** — "all seven rungs remain one statistical F1 tier, 0/21 pairs"
  (`pass-budget-pareto-v2` is now 6 of 7; `verified-adv-text-4of5` is ruled out).
- **Lines 307–314** — "the one statistically resolved role gap" (`flash35-model-roles` is now
  2 → 3, and the added member is exactly the Flash-3.5-as-PV-proposer cell that sentence
  declares resolved against).
- Arguably the two architecture-ranking headings at lines 219 and 278.

`docs/paper/results-outline.md` carries **six** affected claims and **zero** flags, including
"PV is the sole Tier-1 Era-1 leader … Load-bearing." (line 236 — the retracted headline) and
"a broad 20-cell Tier-1 tie" (line 197 — now 15). `docs/paper/discussion-seeds.md` was checked
and is **clean** — its tier claims all rest on the 55-map boards, whose sets did not change.

Found by the prose auditor; the F1-dependent item re-verified by the coordinator.

### F3 — WRONG. Five register rows still carry outcome prose their own revised `tie_set` contradicts

E83 appended revision notes to the register rows but left body prose in place, and both render
into `results/analyses-manifest.md`. The worst is `era1-leaderboard`, whose body still reads
"Tier 1 is now a SOLE leader … PROPOSER-VERIFIER IS THE SINGLE BEST ERA-1 ARCHITECTURE …
break[s] the old 6-way HIGH-consensus tie (now Tier 2)" — the exact sentence E83 quotes as
unsupported — beside a `tie_set` of 10 that includes all six HIGH-consensus cells. Also:
`n1-baseline-matrix-384` ("two-member … clear of the Tier-2 pair — the two Pro-text T=0.7
cells", now 4 including both, and per F1 correctly 3 including one),
`era1-single-pass-baseline-matrix` ("20-of-36-cell tie", now 15), `pass-budget-pareto` ("ONE
statistical tier", now 3 of 5), and `pass-budget-pareto-v2` ("All seven rungs … ONE statistical
tier", now 6 of 7). The project's own precedent for this — an inline `[REVISED … erratum E81]`
marker on the superseded clause — exists in the `era1-single-pass-baseline-matrix` row and was
not applied by E83.

Found by the prose auditor; membership diffs re-verified by the coordinator against
`git show 3abec641a:results/run-analyses.json`.

### F4 — WRONG as a statement of published state. The `ci_unreliable` retirement reached no committed artefact, and the vintage marker exists nowhere

The code change is correct (see Part C, claim 4): `assess_ci_reliability` now flags on measured
exclusion or E72 partial coverage, and adds `ci_flag_basis` so an artefact is readable "without
knowing its vintage". But the commit deliberately re-emitted nothing, so:

- `grep -rl ci_flag_basis results/` returns **0 files** — the disambiguating key exists only in
  code paths never yet run to completion against the corpus.
- The committed register (`results/conditions-manifest.json`) still publishes
  `ci_unreliable: true` on **1,041 of 4,299 buffer-rows across 91 of 337 conditions at 20 m —
  identical to the pre-session state** — including the paper's headline gold-standard cell,
  for a pathology the session's own measurement established never occurs (1,041/1,041 contain
  their point estimate; independently re-derived by this audit, and it reproduces exactly).
- The manifest generator (`generate_post_run_report.py:734`) copies the flag verbatim and does
  not copy `ci_flag_basis`, so even a re-emitted evaluation would surface in the register as an
  unmarked boolean.
- Corpus-wide: every one of the 5,798 `ci_unreliable: true` buffer-rows under `results/`
  co-occurs with `coverage_status: "sparse_cross_grid"` — all of them are the retired rule.

The handoff's phrase "retired a reliability flag on 91 of 337 conditions" describes the code,
not any published artefact. Whether to re-emit is a PI decision the session explicitly
deferred ("mixed-vintage by design"); the finding is that the design leaves the register
asserting a health warning the project now believes is false, with no machine-readable marker.

Found independently by the coordinator and the code auditor.

### F5 — WRONG (the stated rationale). The `uuid`-is-a-symbol-code diagnosis is false; the values are float64-mangled record identifiers, and the false diagnosis is published in two Session 137 ground-truth references

D21 recorded that `uuid` in the 55-map student layer is not unique (4,746 records, 839 values)
and explained it as "a SYMBOL CODE … it encodes the map-symbol type … Nothing is corrupt and
there is nothing to repair" (`scripts/materialise_best_available_gt.py:92-101`). The data
auditor tested that explanation against the upstream digitisation exports and it fails:

- The five largest buckets (`100005e13` ×1,152, `100006e13` ×778, …) are **rounding tiers, not
  a taxonomy**; the real symbol field `MapSymbol` has 6 distinct values, and each `uuid` bucket
  fans out across 3–5 of them. A symbol code that crosses symbols is not a symbol code.
- **Mechanism verified directly**: of 2,054 intact 19-digit uuids in
  `inputs/vectors/MapMoundsDigitised/data/Entity-2018*.csv`, **421 (20.5 %) round-trip through
  float64 exactly onto a published token** (e.g. `1000081538111813966` → `1000081538111814e3`);
  raw-string matches are 0. One upstream export (`MapDig_ALLfixedNE.csv`) has uuid =
  `1.00E+18` on all 8,343 rows while its sibling `ID` column is fully unique.
- The repo already held the correct diagnosis: `scripts/build_student_mounds_gs4.py:238-240`
  ("uuid in the raw shapefile is float64 … lost precision").

No committed metric depends on it (matching is positional; nothing joins on `symbol_code`), so
the numbers stand. What is wrong is the *published semantic*: both Session 137 references
(`best-available-gt-55maps.*`, `canonical-gt-55maps-r50.*`) carry the field under the name
`symbol_code`, asserting a meaning the data does not have, and "nothing to repair" forecloses a
recovery the intact upstream keys would support. The column also mixes three string formats
(SCI 4,208 / INT 478 / STR 60 in the canonical CSV) and survives numeric-inference corruption
only because 60 string values force pandas to `object` dtype.

Verified by the data auditor with corrected figures (it re-measured and corrected two counts
from its own sub-sweep before reporting); coordinator spot-checked the claim structure, not the
counts.

### F6 — WRONG. A bootstrap-resample mean is published under the name `mcc`, and on one artefact family it is the ranking key

The evaluation JSONs keep the observed tile statistic (`point`) and the bootstrap-resample mean
(`mean`) separate. Two writer families collapse that distinction:

- **The CSV/Markdown layer**: `evaluate_detections.py:1169` and `:1471` publish
  `mcc.get("mean")` (and sensitivity/specificity likewise) under the bare column name `mcc` in
  every `evaluation.csv`, `batch_summary.csv`, and `evaluation.md`. Consequence, verified by
  direct diff: in the D17 commit (`60f83e571`), the `mcc`, `sensitivity`, and `specificity`
  columns of the 49 re-run evaluations' CSVs **moved** (e.g. 0.8906 → 0.8894), while F1,
  precision, and recall held to the digit. The defect-register changelog's "no point estimate,
  no F1, precision, recall, or tile-MCC value moved" is therefore false at the artefact layer
  readers actually open; the JSON `point` fields did hold, and the 1e-9 gate — by its own
  `gate` text — covered F1/precision/recall only.
- **The legacy leaderboard family**: `build_tiered_leaderboard.py:931-937` lifts `mcc.mean`
  into the condition record and `get_condition_score:276` **ranks** MCC boards on it, while the
  F1 branch of the same function uses the point estimate. Re-ranking the committed boards on
  `point` (recomputed from each evaluation's own committed confusion matrix) changes the
  occupant of **18 of 86 positions** on `results/leaderboard/combined/era1/…mcc.json`,
  including a rank-4/5 swap. Scoped by the coordinator: this family is legacy — the paper
  draft never cites `results/leaderboard/`, and the current `metric-leaderboards` family reads
  `mcc.get("point")` (`build_metric_leaderboards.py:115`) and is clean; the 55-map MCC tiering
  publishes point MCC (verified 16/16 exact from committed confusion matrices).

Found by the coordinator (CSV layer) and the code auditor (ranking key); both verified at
source by the coordinator.

### F7 — WRONG in every derived summary. "Ten of fourteen boards were wrong" — the correct count is eight

Membership diff of all fourteen `tie_set` fields, `3abec641a` versus HEAD: **8 boards changed
membership, 6 returned identical sets** (`verifier-robustness-matrix` 5→5 and
`diversity-dividend-384` 3→3 are member-identical, alongside the four 55-map boards). The
count drifted upward as it propagated: E83's Impact field says "eight of fourteen" (correct);
E83's body says "ten revised, four confirmed unchanged" (defensible — "revised" tracks
re-tiering, not change — but reads as change); the audit brief says "Ten of fourteen board tie
sets were wrong"; the continuity block says "ten changed, four (55-map) identical"; and the D24
statistician brief says "Ten of the fourteen boards changed membership" (`:136`), which is
flatly wrong by two. Cosmetic sibling: E83's own header still says "eight boards' tie sets
revised" from the eight-board stage, now inconsistent with its body's "ten revised".

Found by the coordinator; independently found by the prose auditor.

### F8 — WRONG. The D24 statistician brief — the one document written for an outside reader — carries three factual errors

`docs/methodology/mcb-critical-value-open-question.md`: (a) "micro-F1 (10 boards) or tile MCC
(4 boards)" at line 33 — its own table counts **12 F1 boards and 2 MCC boards**; the "4" is the
55-map board count welded onto the MCC slot. (b) "B = 10,000" stated for all boards at
line 58 — false for `n1-baseline-matrix-384` (B = 200; see F1) and, among supplementary
artefacts, `verifier-robustness-matrix_mcc` (B = 2,000). (c) "Ten of the fourteen boards
changed membership" at line 136 (see F7). The fourteen `w_upper` values and set sizes in its
table were all verified against the artefacts and reproduce to 4 d.p. — the frame is wrong,
not the numbers. Since Shawn is actively recruiting a statistician with this document, these
three are worth fixing before it is sent (PI decision; not fixed by this audit).

Found by the prose auditor; (b) settled by the coordinator's re-run.

### F9 — WRONG/FRAGILE family. Reproducibility of committed evaluations from their own metadata (class 8), including damage done by Session 137's own fixes

- **Static census** (regeneration auditor): of 1,741 committed `evaluation.json`, **54 carry no
  usable reproduction recipe** (40 with no `cli_args` at all, of which 24 record no detections
  input anywhere; 14 with recipe paths absent from disk). Two register-backing cells were
  **confirmed unreproducible by actually running the scorer**:
  `results/gold-standard-extended-buffer-sweep-era2/evaluation.json` (backs
  `gold-standard-v2::verified-v1`; its recorded detections path `outputs/h11/…` has moved to
  `outputs/gs/…`) and `results/55maps-standardised-ref-2026-08-14/TM-k3/evaluation.json`
  (its `ground_truth` is a prose sentence, not a path — a shape shared by 16 register
  conditions). Twelve `deployment-oracle` cells point at consensus files that no longer exist.
- **The D17 replay overwrote provenance**: the 49 re-run evaluations' `cli_args.output_dir` now
  records the replay's temp dir (`/home/shawn/cc-scratch/tmp/tmp…`, 49 files) and
  `cli_args.glob` was nulled (47 files). The detections input survived, so the cells remain
  reproducible — but the artefacts now describe an invocation whose output location never
  persisted. The fix for one metadata defect (D17) degraded a neighbouring metadata field.
- **The 55-map selection-aware artefacts record no ground-truth or bounds override** — for
  adapter boards the override is mandatory, so the four artefacts under the register's
  fourteen-board instrument are not reproducible from their own metadata. Settled empirically
  by this audit: the standardised board reproduces exactly against
  `best-available-gt-55maps.geojson` (thetas and apparent F1 match to 6 d.p.), the canonical
  boards' cells match `canonical-gt` evaluations; the identification should be recorded, not
  rediscovered.
- **The D22 fallback lives in one loader of five**: `era1_leaderboard_tiering.py` has it;
  `rescore_tile_mcc_e81.py` raises `KeyError` on the 40 no-`cli_args` cells;
  `build_bca_migration_queue.py` silently skips them.
- **The BCa migration queue is built from argparse defaults, not from what ran**
  (`build_bca_migration_queue.py:129-130` reads `cli_args.buffers`, which for batch cells holds
  the unoverridden default `[20]`): all 22 queued rows carry `buffers=20` and empty detections
  columns, so executing the queue as written would re-score 14-buffer cells at one buffer with
  no input. Verified never yet run (`git diff` on the target tree is empty) — a loaded gun,
  not a fired one. This is D17's class (a default published as a measurement) on a different
  field, propagated into a work queue.

### F10 — WRONG (class 2). The E81-era hand edit to the era-2 leaderboards is undeclared on two boards, missing from a third, and none is re-derivable from its cited source

Commit `7ab7d7fa1` hand-inserted a `gold-standard-v2-greedy-v1-487` Tier-1 row into three era-2
boards. Only the 20 m file is declared `hand_edited: true` in the generated-file registry; the
30 m and 50 m files are classified as generator-owned and **regeneration would silently revert
them** — the exact D18 mechanism, still live. The 40 m board never received the edit, so four
sibling boards disagree about whether a Tier-1 condition exists (20-in-7 / 20-in-7 / **19-in-6**
/ 20-in-7). All four cite `leaderboard_tiers_20m.json` as source, which holds 19 conditions in
6 tiers with no such label — no edited board reproduces from its own recorded source.

Reported by the regeneration auditor; not independently re-derived by the coordinator.

### F11 — WRONG (class 3, mechanised). `regenerate_per_arch_md_from_json.py --verify` writes 140 tracked files before "verifying" them, and its verification can never fail

`--dry-run` returns early; `--verify` falls through to the write loop and then compares the
files it just wrote against the JSON it just rendered — "140 OK, 0 mismatch" is structurally
guaranteed. Running it overwrote 140 tracked files, 28 of which lost their provenance headers
and metadata columns because the committed versions were written by a *different, richer*
generator (`enrich_per_arch_markdown.py`). Running the correct generator reproduces 130 of 165
boards; 28 differ only in a bounds-path line (JSON rebuilt after the MD); and the seven
`leaderboard_tiers_20m.md` files — the primary board of every stratum — are committed in the
wrong generator's format because both scripts contest the same path (a last-writer collision,
timestamps confirm). Related: `reports/verification/generated-file-registry.json` — the
apparatus built to catch exactly this class — is stale at `df1725345` (2026-08-17) and does not
register **28 Session 137 artefacts**, including every headline findings document of the session
under audit.

Reported by the regeneration auditor; the 140-file write observed and its diff captured by the
coordinator during cleanup (the tree was restored; `git status` clean).

### F12 — WRONG/UNSUPPORTED family. CI-method labelling: prose and metadata assert "BCa" where the computation is percentile or unrecorded

- The two 55-map F1 leaderboards' `PAIRED_CI_NOTE` states the per-cell intervals "are marginal
  per-cell **BCa** bootstrap intervals"; the CI code behind them is plain
  `np.percentile(arr, [2.5, 97.5])` (`compute_corrected_f1_multi_buffer.py:566-570`), and the
  adapters honestly record `"f1_ci_method": "percentile"`. The same shared string is correct on
  the two MCC boards. Committed at `results/55map-leaderboard/55map-leaderboard-50m*.md:19`.
- `results/conditions-manifest.json` asserts `ci.method = "BCa"` on **308 per-buffer cells (22
  conditions)** whose source evaluations record no method at all — the write-side literal D15
  flagged, surfacing on the read side. `build_bca_migration_queue.py` cannot distinguish
  "already BCa" from "method unrecorded" for these.
- `_metadata.bootstrap.method: "BCa"` (the known literal) is contradicted by 162 per-metric
  `method` values (`percentile_fallback` ×127, `undefined` ×35) inside 58 committed files, and
  the same constant-in-a-measured-dict shape recurs at seven sites in `lib_advanced_metrics.py`
  plus three `.get(..., "BCa")` defaults.

Reported by the code and data auditors; the 55-map percentile trace re-checked by the
coordinator at source.

### F13 — WRONG, pre-existing, live. The `h13-overlap-2026-08-18` register row quotes cost-efficiency at list price — exactly 2× the billed figures its own findings document corrected

Every dollar figure and per-dollar slope on the row is exactly half/double the corrected billed
basis in `results/h13-overlap-2026-08-18/findings.md` (D13: flex carries a 50 % discount).
Re-derivation: −0.0380/0.1882 = −0.2019 against the row's −0.1011. The sibling row registered
in Session 137 (`grid-tilesize-overlap-2026-08-18`) correctly quotes "$18.53 billed", so the
register is internally inconsistent on cost basis. Not introduced by Session 137 — but it is
the D9/D13 class sitting in a register row, unfixed.

Found by the prose auditor; arithmetic re-checked by the coordinator.

### F14 — FRAGILE. Knife-edge tie-set memberships, and a membership relativity nothing documents

- `55map-standardised-leaderboard-50m`: the third cell misses admissibility by **0.00017** at
  B = 10,000. This audit re-ran the board at five seeds: the published 2-member set holds at
  every seed (margins −0.00005 to −0.00026), so it is seed-stable — but a hair's breadth from a
  3-member set, and the brief's § 3 instinct about "four for four" was sound.
- `pass-budget-pareto` excludes `verified-384-ge3of5-t0-3-n5` by −0.00059 while
  `pass-budget-pareto-v2` admits the same condition (+0.00177): correct behaviour for a
  simultaneous procedure (the critical value widens with k), but no document warns that MCB
  membership is a property of the candidate set, not the condition — a reader comparing the two
  register rows sees a contradiction.
- `min-vs-high-thinking-pv` excludes one cell by 0.00087.

### F15 — FRAGILE bundle (one WRONG of magnitude one tile). Data-shape residue in the classes 9–11 family

Verified counts by the data auditor unless noted: (a) 47 committed evaluations carry an MCC
block with **no `point` key** (three shapes beyond the two known ones; same split on
sensitivity/specificity); five consumers read `point` and would silently get `None`; none of
the 47 is manifest-cited today. (b) `author_e43_matched_temperature.py:207` raises on the
bare-float MCC shape and its `or {}` chain resurrects the E81 falsy-zero defect.
(c) `run_generalisation.py:1285` counts dict-shaped `failed_items` in one total and skips them
in the per-map total — the committed 55-map report's two failure counts disagree by 1 tile of
7,833 (**wrong**, magnitude 1). (d) `candidate_id` is `'135.0'`-format in one canonical-GT file
and `'0'`-format in its two siblings — raw-string join intersection 0/773. (e) A column named
`temperature` holds the tile size 384 in four files and config labels in 32; a column named
`threshold` holds probabilities, vote counts, or `'3/5'` strings depending on family.
(f) Four committed `script_git_commit` prefixes are valid float literals (`0e980055` → 0.0).
(g) `label` is non-unique in the manifest (300/337) and four scripts build last-wins dicts
keyed on it — currently safe because every committed board is single-run-scoped.
(h) Adapter-written evaluations hard-code `ci_unreliable: False` on 224 rows — accurate today
(0/224 measured exclusions) but computed by nothing, and the E72 ground is never evaluated for
them (**unsupported**).

### F16 — FRAGILE. Cross-scope and notation residue in prose (class 12/6)

(a) The paper draft's tile-size ordering "384 (0.890) > 256 (0.856) > 512 (0.792)"
(`results-draft.md:264`) remains a cross-scope comparison (487 vs 1,032 vs 340 tiles) — Phase
0.3 corrected a *different* 256-vs-384 pairing, and its confound finding (pass count, vote
threshold) applies to this one too; the register row carries the caveat, the draft sentence
does not. (b) The `pass-budget-pareto-v2` transfer-delta chain writes a magnitude ordering
with a value operator ("−0.048 < −0.057 < …" — backwards as values), and the register row does
not state which reference vintage its deltas are on (they are canonical; the draft's table is
standardised; they differ by up to 0.008). (c) H13's "2.7× FP increase for 2.9× tiles"
divides a common-footprint count by a native-footprint count.

### F17 — FRAGILE. Instrument-adjacent residue

(a) `selection_aware_intervals.py --evals` ignores `--buffer` while stamping it into the
filename and metadata (`build_evals_tile_counts` hard-codes 20 m for scoring and for the
`eval_f1` read) — no committed artefact is wrong (the only `--evals` artefact is a 20 m curve),
but the path defeats the exact ambiguity-safeguard the session added. (b) The two m-out-of-n
sensitivity artefacts predate both the Hsu fields and the buffer-stamp filename convention —
`results/selection-aware/` holds three artefact vintages, distinguishable only by field
presence; the findings doc's m-out-of-n table correctly quotes the two-sided band (Hsu is null
there — checked, not an omission). (c) The degenerate-resample concern in the MCB critical
value (a resample with < 2 defined candidates would silently drop from the quantile, an
anti-conservative direction) **never fires**: 0 of 10,000 resamples on the reachable
69-candidate MCC set; 8,372 resamples have ≥ 1 undefined candidate, which excludes those
candidates from that resample's max — empirically dominated by the conservative coverage in
Part B. (d) `mcc_tiering_55map.py` writes its gate verdict "8/8 (exact)" as a fixed string
decoupled from `len(CELLS)` — substance verified real (16/16 cells reproduce from committed
confusion matrices, max |Δ| = 0). (e) **Found via the tier-2 run**: the Obs 280 tier-2 test
invokes `analyse_obs280_shared_reference.py`, which writes its output **into the committed
results directory** (`:307`), so any tier-2 run mutates a tracked artefact — and the current
generator emits four fields the committed file lacks (`mcc_undefined_standardised`,
`n_board_cells`, `excluded_mcc_undefined`, `mcc_undefined_legacy_extended`), i.e. the committed
artefact is one generator-vintage stale (class 2). The registered values themselves are
unchanged by regeneration (rho 0.476, leaders, `divergence_survives` all identical); the
finding is the in-place write and the schema lag, and it is the probable mechanism of the flaky
failure noted in Part D. The mutation was caught by a post-run `git status` and restored.

---

## Part B — The D24 coverage simulation (the standing item)

The brief called a coverage assessment "the single most valuable thing you could do". One was
run for this audit (`scratchpad/coverage/coverage_sim.py`; results in `coverage_results.json`
there). **Design**: empirically calibrated Monte Carlo. The population is the empirical joint
distribution of per-tile (TP, FP, FN) vectors across candidates for a real committed board;
truth is the full-data statistic vector and the true best is its argmax; each of S = 400
simulated datasets draws n tiles with replacement; on each, the Hsu procedure runs exactly as
`selection_aware_intervals.py` runs it (inner bootstrap critical value, 95th percentile of the
max signed deviation); we record whether the true best survives into the admissible set
(nominal ≥ 95 %).

**Gate first** (the session's own class-13 lesson): before any simulation, the re-implementation
reproduced each committed artefact exactly — same seed, same B, sequential RNG —
matching `hsu_w_upper` to 6 d.p., the admissible set exactly, and the apparent F1 to 6 d.p. on
all three boards. This doubles as an independent reproduction of the committed instruments.

| Board | k | n tiles | P(true best in Hsu set) | P(all θ in Hsu intervals) | Mean set size under truth |
|---|---:|---:|---:|---:|---:|
| `h12-v2-hp-hn-ratio` | 6 | 327 | 0.995 ± 0.007 | 0.983 ± 0.013 | 4.5 |
| `era1-single-pass-baseline-matrix` | 36 | 340 | 1.000 | 0.930 ± 0.025 | 14.2 |
| `era1-leaderboard` | 82 | 340 | 1.000 | 0.980 ± 0.014 | 10.6 |

Robustness: h12 re-run at the committed inner count (B = 10,000, S = 300, fresh seed) gives
0.990 ± 0.011 — the picture is not an artefact of the cheaper inner loop.

**Reading**: on all three boards tested, the operative guarantee — the true best is not ruled
out at simultaneous 95 % — **over-covers**. The bootstrap substitution for Dunnett's critical
value errs **conservative** here: if anything the published admissible sets are slightly too
wide, which is the safe direction for E83's corrections (nothing wrongly excluded). The § 3
worry that `h12-v2` going 6-of-6 admissible signalled an over-wide critical value is confirmed
in kind (mean set size under truth is 4.5 of 6) but it is conservatism, not error. The full
simultaneous-interval statement sits at or near nominal, with one board (era1-single-pass)
marginally under at 0.930 ± 0.025 — the published claims do not rest on that statement.

**Limits, stated plainly**: this is a within-model check. The simulation's truth is the
empirical tile distribution, and tiles are drawn iid — it can detect failures of the
critical-value substitution, and did not; it **cannot** test the iid-tile exchangeability
assumption itself, nor spatial dependence between tiles. S = 400 puts ±0.02 on the estimates.
It narrows D24 (direction now measured: conservative on three real boards); it does not close
it, and the external statistical review should proceed — with the F8 corrections applied to
the brief first.

---

## Part C — The brief's § 1 claims, verdicts

| # | Claim | Verdict | The check |
|---|---|---|---|
| 1 | Ten of fourteen tie sets wrong, corrected via Hsu MCB | **Count wrong (8, not 10 — F7); correction itself sound** | Membership diff old→new on all 14 boards; all 14 register `tie_set` fields exactly equal their committed Hsu artefacts (by ref); both MCC boards tiered on tile-MCC with matching outcome text |
| 2 | `era1-leaderboard` leader's clique has six members | **Confirmed** | Re-derived from the artefact's `pairwise`: rank 2 significant at BH 0.0482 (raw 0.0340) closes the greedy tier; 5 cells non-significant vs leader by BOTH raw and BH columns (no column confusion); all 15 pairs among the six non-significant, 0 violations |
| 3 | 49 re-runs at B = 10,000 moved no point estimate | **Confirmed for F1/P/R and JSON `point` fields; false at the CSV/MD layer (F6); gate covered F1/P/R only** | Structural diff of all 67 JSONs in `60f83e571` (132 changed leaf-path patterns, classified); CSV diffs; the gate report's own `gate` text |
| 4 | `ci_unreliable` measured; E72 preserved; 1,041/1,041 | **Code confirmed; published state not retired (F4)** | Read `assess_ci_reliability` and callsite (`ci` keyed by metric — the exclusion test is real; flag = partial-coverage OR exclusion); 1,041/1,041 containment independently re-derived from the committed manifest and reproduces exactly; flagged-row counts identical pre/post session |
| 5 | Selection optimism ≤ +0.0137; replay re-selects | **Construction confirmed; committed values reproduce** | Code review: `nanargmax` inside each resample, optimism = in-resample winner in-resample minus same candidate on full data, interval location-shifted; θ property brute-force tested on 6 edge cases (exact); all 14 `w_upper`/set sizes in the D24 brief reproduce to 4 d.p.; 3 boards' full artefacts reproduced exactly by sequential re-run |
| 6 | Four 55-map boards return published tie sets | **Confirmed, with one knife-edge (F14)** | All four artefacts at `buffer_metres: 50`, B = 10,000; all 16 F1-board cells reproduce committed F1 to 0.000000 (θ arithmetic); standardised board re-loaded from scratch against `best-available-gt` — thetas match, set {0, 2} stable across 5 seeds; third cell misses by 0.00017 |
| 7 | Phase 0.3: 256 px deficit survives; "swamping" does not | **Confirmed by full re-run** | `phase0_3_tilesize_common_footprint.py` re-run on zbook to scratch: scope identical (1,032/481 carriers, **420 reference mounds under both** — genuinely common), all 8 cells' P/R/F1 match committed to 1e-9; the 256 cell is worse on both margins under both carriers; the findings doc itself flags the pass-count confound |

## Part D — Checked and confirmed (coverage, not silence)

Beyond Part C: **Hsu ⊆ two-sided band on every committed candidate set** (22 artefacts —
membership, not just size; the § 4 gap now closed, and the claimed bracketing holds).
**E82's census arithmetic** reproduces (1,583 + 114 + 52 = 1,749 tracked evaluations;
69,663 + 840 + 5,901 = 76,404 BCa intervals). **E82 completeness**: 0 of 337 manifest
conditions cite a source below 10,000 iterations — the 49 were the complete set. **The D17
gate report** recounts exactly (49 files, 0 point moves, 46 widened / 3 narrowed, all three
narrowed cells at n = 1,032, max ratio 1.79 on an n = 340 cell; ratios track √(B_old/n)).
**Register integrity**: condition and analysis ids unique; all 415 `conditions_compared` refs
resolve; exactly 14 non-empty tie sets. **The four manifests regenerate byte-identically**
(`generate_post_run_report.py --all --dry-run`, then row-diff and re-render — D18 is genuinely
fixed where it was fixed). **Six of nine sampled evaluations reproduce exactly** from their own
metadata by re-running the scorer (plus one batch cell that reproduces once the recipe is
supplied manually). **The clique-audit artefact** (11 tiering artefacts, 3 understated, all
era1-leaderboard) reproduces. **`tile-mcc-explained.md`'s** worked example is exact both ways
(0.8978 wrong / 0.7903 right). **The 37 register rows' signed contrasts** were traced to
sources; one rounding wobble (+0.014 vs 0.0130), no sign inversions beyond the one already
fixed in `0611ce58a`. **Phase 0.3 internal arithmetic** closes completely (areas, percentages,
detection counts, both gaps). **Class-7 sweep**: no active hard-coded-scope instance found
across ~290 scripts (all buffer/CRS/tile-size constants verified against their populations;
"14buf" is 14 buffer values, not 14 m). **Flag sweep**: all other artefact-writing flags live
and firing correctly or correct-by-design. **The 36 consensus-analysis summaries**
hand-corrected in `1844e5887` are now generator-aligned. **`discussion-seeds.md`** needs no
E83 flags (all its tier claims rest on unchanged 55-map sets; the +0.0224 uplift re-derives).
**Tier-1 suite** green on zbook (1,593); **tier-2 suite** run for the first time this cycle —
green (27 passed). One tier-2 test (`test_analyse_obs280_shared_reference.py::
test_real_artefacts_reproduce_registered_finding`) failed once in the first run, then passed in
isolation and in a clean suite re-run — non-reproducible, flagged as flaky rather than as a
defect. Marker-arithmetic note: of 1,727 collected tests, 1,597 are tier1 and 27 tier2, so
**103 tests carry neither marker** and are selected by neither tier; all 103 pass (2.3 s), but
if operational practice runs only the tiered selections they are never exercised.

## Part E — Not checked, and what it would take

- **Whether regenerating the tiering/leaderboard families changes published tiers** (the F6/F11
  families were diagnosed at the writer level; a full `build_tiered_leaderboard.py` re-run per
  stratum is hours of permutation compute, on sapphire).
- **Coverage of the BCa intervals themselves** (D15/E82's instrument) — only the MCB critical
  value was simulated. A parallel empirically calibrated simulation would take a day of design
  plus hours of compute.
- **The 142 committed leaderboard JSONs carrying pre-10k intervals** (18 stale interval blocks
  found under `results/leaderboard/combined/era2/`) were not regenerated — the register itself
  is current (49/49 verified), the derived family is not.
- **`outputs/**` at scale**: `.meta.json` invariance and per-tile artefacts were sampled, not
  swept (58 GB). `archive/**` deliberately excluded, mirroring E82's scope.
- **The 12 broken-path deployment-oracle cells** were classified statically, not chased to
  their moved inputs.
- **Sub-agent findings not independently re-derived by the coordinator** are marked in place
  (F10 notably); everything in F1–F9 headline claims was either found or re-verified by the
  coordinator directly.
- **The iid-tile assumption** under every bootstrap instrument in the study — outside what any
  within-model simulation can test; one for the statistician.

## Part F — Cheapest close-outs (PI decisions; nothing here was executed)

1. **F1**: re-emit `n1-baseline-matrix-384_b20_m1.json` at B = 10,000 (minutes, $0), update the
   register row 2→3, and fix the three F8 errors in the D24 brief before it goes to the
   statistician. The audit's re-run gives the expected result: {medium-T0.0, high-T0.0,
   medium-T0.7}, seed-stable.
2. **F2/F3**: sweep `results-draft.md` and `results-outline.md` against E83's table (the
   unflagged lines are enumerated above); apply the E81-style inline `[REVISED]` marker to the
   five register rows' superseded clauses.
3. **F4**: decide whether the register should carry the stale flags unmarked; if mixed-vintage
   stays, teach the manifest generator to copy `ci_flag_basis` (one line) so the vintage is at
   least machine-readable.
4. **F5**: rename `symbol_code` → `source_id_lossy` (or similar) in the two references and
   correct the comment block; D21's operational handling needs no change.
5. **F9**: record the 55-map board↔reference identification (one line each in the four
   artefacts or the findings doc); re-point the two broken register-backing recipes.
6. **F11**: make `--verify` compare against a temp render without writing; regenerate the
   generated-file registry.

## Changelog

### 2026-08-20 (evening) — Remediation campaign executed

The PI approved a same-day remediation campaign covering every finding in this
report, with four scoping rulings (full `ci_unreliable` migration; an E83
correction block; `symbol_code` → `source_id_lossy`; full-corpus re-emission
for the mean-vs-point layer). Executed across eight phases (coordinator plus
three Opus subagents; ~30 commits; tier-1 grew 1,593 → 1,713+ tests, all
green). Register-facing outcomes: the F1 board correction landed (the
`n1-baseline-matrix-384` tie set is 3 at B = 10,000, register and E83
corrected); the register's 1,041 stale reliability flags are retired with a
vintage basis on every row (F4); the `symbol_code` semantic is corrected in
both references (F5); the CSV/MD layer publishes observed points corpus-wide
(F6; 2,165 files); the E83 flag set is complete and the banner true (F2); the
five contradicted register outcomes carry inline revision markers (F3); the
counting drift is reconciled in E83's correction block (F7); the D24 brief is
corrected (F8); recipes are loadable for every register-backing cell (F9).
Two corrections to this report's own figures, found during execution: the
method-silent manifest cells number **619 across 47 conditions** (F12 quoted
308/22, one family's slice), and one register-backing cell
(`gold-standard-extended-buffer-sweep-era2`) carried pre-fix D15-defective
intervals that the F9 re-emission corrected (~4.6× wider, points identical).
Defect register rows D25–D39 track per-finding status; still open there: the
E82 corpus-wide re-emission campaign (~1,520 pre-fix B = 10,000 evaluations,
sapphire-scale), the legacy leaderboard family's re-ranking decision, and D24
itself (external review, now with the coverage evidence in Part B).

### 2026-08-20 — Original publication

Produced on zbook at $0 API spend (sapphire unreachable), Session 138, in response to
`planning/session-137-audit-brief.md`. Four Opus-class subagent auditors (classes 1/3/4/5/7,
9/10/11, 2/8, and 6/12/13 + flag completeness) plus coordinator re-derivations and the D24
coverage simulation. Working tree clean at `8dc01fca4` throughout; no fixes applied.
