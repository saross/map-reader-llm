# Fresh-context audit of the r2 recompute block

> **Last revised**: 2026-09-07 (wording correction; MINOR 13/14 closed). See [§ Changelog](#changelog)
> for revision history.

Audit of `planning/reference-revision-2026-09-06.md` §§ 4/4a against the code.
No step of the block was run; zero API spend.

## Denominator

**Opened** (18 scripts; lines, P = in part): contract 490;
`build_55map_leaderboard.py` 316; `final_board_sweeps.py` 385; `final_board_build.py` 632 P;
`final_board_n3_carried.py` 117; `stride55_score.py` 274;
`register_standardised_gt_conditions.py` 267; `materialise_best_available_gt.py` 316;
`score_55maps_standardised_reference.py` 816 P; `lib_uplift_supplement.py` 1737 P;
`build_tiered_leaderboard.py` 2345 P; `evaluate_detections.py` 2488 (help);
`derive_audit_revision_instructions.py` 166 P; `empty_tile_adjudicate.py` 578 P;
`stride55_ladder.py`, both `gemini37_*_ladder.py`, `compute_corrected_f1_multi_buffer.py` P.
**Data** (8): `ladder.json`, `final_board_50m.json`, `cells_manifest.json`, IM-k4
`evaluation.json`, a stride55 `summary.json`, `audit-revision-instructions.csv`,
`condition-inventory.json`, the manifest schemas.
**Claims checked**: 21. **Probes**: 6 (a–f).

**NOT checked**: the § 2/§ 2b estimator arithmetic and intervals;
`tests/test_reference_revision_r2.py`; `marking_campaign_gates.py`;
`verify_run_conditions.py` and the manifest generators; whether the 3.7/3.8 GS
evaluations exist; `planning/55map-final-board-2026-08-27.md`; any scoring run.

## Findings

**BLOCKER 1 — step 3's cell count is wrong by seven; the 29/29 gate passes on a
mixed-vintage board.** The contract says "the 16 final-board cells" and
"16 + 3 + 3 + 6 + 1 = 29". `results/55map-final-board-2026-08-27/final_board_50m.json`
tiers **23** cells, `cells_manifest.json` lists 23, `cells/` holds 19 directories (the four
carried incumbents' detections sit outside it). The true total is 36. *Failure*: step 3
stops at 29, § 5's "step 4 never starts before 29/29" reads green, and step 4 tiers seven
cells still on r1 — the mixed-vintage board the count gate exists to prevent.

**BLOCKER 2 — step 4 depends on step 7; the declared order (4 → {5,6} → 7) is inverted.**
`build_55map_leaderboard.py:63` reads `results/run-conditions.json`; `:228–234` resolves
each cell by `label` and takes F1, CI, MCC and `n_detections` from its `eval_path`. The
`-r2-gt` labels are written by `register_standardised_gt_conditions.register_one`
(`run-conditions.json`, `:242`) — step 7. *Failure*: `StopIteration` on the label lookup,
or a board silently built from r1 eval paths if the clone is careless.

**BLOCKER 3 — the § 4a companion command cannot run, and would score the wrong set.**
`stride55_score.py` has no `--compute-mcc` (probe d; MCC is unconditional at `:197`).
`materialise_primary:105` gates the crop manifest's count, which is the **K=10** union
57,482, so `--union-n 43909` (ladder B N=5) aborts. `--min-votes 5` filters that K=10
union, whereas 0.843775 comes from `cluster_first_n(passes, 5)` with inherited
probabilities. No path in the script materialises a first-N rung.

**BLOCKER 4 — the r1 regression gates halt any r2 run, and G4's bound is tighter than the
contract's band.** `final_board_build.py:317–345` (G3) demands the eight legacy cells
reproduce the committed r1 board to **1e-9** on F1, every pairwise p-value and tier
membership, reading evals from hard-wired `STD_REF_DIR` (`:79`).
`final_board_sweeps.py:236–252` (G4) checks the same board at `MECHANISM_BOUND = 0.003`
(`:99`) — below the contract's own 0.005 drift band. With `standardised_gt()` on r2 both
fail by design, and "G4 red → stop" makes that unrecoverable.

**MAJOR 5 — H1 contradicts the IM-k4 template.** IM-k4's
`_metadata.cli_args.ground_truth` is `best-available-gt-55maps.geojson` — the merged file,
passed to `evaluate_detections.py --ground-truth`, which takes one path (probe a). That is
why the merged artefact exists. H1 forbids it and requires "the r2 layers (student,
extension, audit) via `build_extended_gt`" — but that function takes **two** frames
(`compute_corrected_f1_multi_buffer.py:386–389`) and `--vintage r2` emits **only** the
merged geojson/csv. No r2 layer files exist.

**MAJOR 6 — the r1 homes are not read-only by construction.** `final_board_sweeps.py:359`
writes `OUT/cells/<label>/detections.geojson` and `:376–378` rewrites `sweeps.json` and
`cells_manifest.json`; `final_board_n3_carried.py:98,111` writes the same tree;
`register_standardised_gt_conditions.adapt_one` overwrites each
`results/55maps-standardised-ref-2026-08-14/<cell>/evaluation.json` in place. All are
module constants with no override flag: an r2 run before H2 destroys what the regression
gate reads.

**MAJOR 7 — the 3.7 rungs cannot be materialised by the derivation the contract names.**
`final_board_sweeps.build_families` covers A/B plus TH7/T03/TM/IM/UPL only, and
`stride55_ladder.load_deduped_passes:122` hard-codes `range(1, 11)`. The real 3.7
derivations (`gemini37_arm_ladder.py`, K_TOTAL=5, arms 1/2; `gemini37_fourth_cell_ladder.py`,
`verify_37`) inherit the right probabilities but score against the **canonical** extended
GT and write **only** `ladder.json`. H5's "no rung registered from sweep numbers alone"
describes exactly what today's code produces.

**MAJOR 8 — H8's GS rank-change tripwire is false by construction, and the boards it names
do not exist.** `build_tiered_leaderboard.py:1512` applies BH across the whole pair family
and `:1040` a top-N=20 inclusion filter, so adding seven cells moves adjusted p-values and
tiers legitimately — a rank change is not evidence of a mechanism error. Also
`results/leaderboard/era2/` is empty and git-tracks zero files; no leaderboard spec YAML
exists in the repo; `planning/condition-inventory.json` (190 entries, 80 era-2) has zero
3.7/3.8 entries. The GS reference is unaffected (`DEFAULT_GROUND_TRUTH:114` is
`mounds-reference.geojson`), so these are new builds, not rebuilds.

**MAJOR 9 — r2 references resolve to "unresolved" silently.**
`lib_uplift_supplement.py:733` looks up by **basename**; `…-r2.geojson` is absent from
`REFERENCE_BY_FILENAME:130`, the fallbacks at `:742–749` know only
`-standardised-gt`/`-canonical-gt`, and `:757` returns
`ReferenceResolution(None, None, "unresolved")` without raising. `REFERENCE_N_MOUNDS:141`
is a separate literal H3's one-line fix would not populate.

**MINOR 10** — `score_55maps_standardised_reference.py:111–112` hard-gates 4731/279; r2 is
4,726 / 278 / 14. **MINOR 11** — `empty_tile_adjudicate.py:82` has no r2 entry, so step 7's
closure check has no reference. **MINOR 12** — both r2 scripts crash on an out-of-repo
`--out-dir` (`materialise_best_available_gt.py:284`,
`derive_audit_revision_instructions.py:161`), the first *before* writing the geojson.
**MINOR 13** — the engine gate's target was built at `4ac0eeedf`, `script_git_status:
"dirty"`. **MINOR 14** — pass order is committed only by `run_<i>` naming; the N=5 union
gate constrains the set, not the order. **MINOR 15** — `runs-manifest.schema.json:65`
enumerates `gt_reference` as `["curator","student","combined"]`.

## Clean probes

- **(a)** Every flag in IM-k4's `cli_args` exists today; the one new flag
  (`--require-clean-inputs`) defaults off, so replay is unaffected.
- **(b)** `--vintage r2` (run out-of-tree, per MINOR 12): all three outputs
  **byte-identical**; 5,018 = 4,726 + 278 + 14. § 3b's counts check out.
- **(c)** `derive_audit_revision_instructions.py`: both outputs **byte-identical**;
  6 removes, 14 adds.
- **(e)** `--spec`, `--inventory`, `--era`, `--track`, `--ground-truth`, `--top-n`,
  `--metric` all present.
- **(f)** `--reference r2` rejected (`invalid choice: 'r2'`) — H3 is a real gap.
- `summary.json` **does** carry a per-buffer tile confusion matrix and MCC with CIs
  (stride55 B, R=50: mcc, mcc_CI, tp/tn/fp/fn), so "companion deferred for want of a tile
  matrix" no longer holds. The ladder's B N=5 carried value is 0.8437752627324171 — the
  contract's 0.843775 is accurate.

## Disposition (S149, 2026-09-06)

Every finding was **re-verified against the named file before adjudication** —
the audit is a claim set, not an authority. All 15 hold. Three carry line-ref
or framing corrections (recorded below); one is **disputed in part**. The
re-verification denominator: 13 scripts re-opened at the cited lines, 6 data
files re-read (`final_board_50m.json`, `cells_manifest.json`, IM-k4
`evaluation.json`, `ladder.json`, the g384_ov192 crop manifest,
`condition-inventory.json`), and 5 filesystem probes.

Legend: **FIX** = the contract or the code changes; **ACCEPT** = the finding
stands and is recorded as a known constraint, no change; **DISPUTE** = the
finding is wrong in whole or part.

### Blockers

**B1 — cell count 29 → 36. FIX (contract).** Re-verified: `final_board_50m.json`
tiers **23** cells, `cells_manifest.json` lists **23**, `cells/` holds **19**
directories; the four carried incumbents (`IM-k4`, `T03-k4`, `TH7-k4`, `TM-k4`)
are board cells with no `cells/` directory. The contract's "16" matches no
artefact. Corrected finish line: **23 + 3 + 3 + 6 + 1 = 36**. § 4a § 2's
separate "all 22 cells (16 + 3 + 3)" is the same error and becomes **32** board
cells (23 + 3 carried + 3 oracle + 3 rungs on-board). Both numbers are amended,
and the count gate becomes a *derived* assertion — the re-score set is
enumerated from `cells_manifest.json` plus the membership ruling at run time,
never from a literal in prose.

**B2 — step 7 precedes step 4. FIX (contract).** Re-verified and *stronger* than
the audit stated: `build_55map_leaderboard.py:224` reads
`results/run-conditions.json`; `:228` resolves each cell with a bare
`next(c for c in ... if c["label"] == label)` (StopIteration, no default); and
`:242` reads the board's F1/CI/MCC/`n_detections` from `cond["eval_path"]` — the
register row is the board's *data pointer*, not just its index. `NAMES_STANDARDISED`
(`:86–88`) is derived by string replacement from `NAMES`, so an r2 board needs a
`NAMES_R2` on the same pattern. Declared order becomes **1 → 2 → 3 → 7 → 4 →
{5, 6} → 8**, with step 7 split: **7a** register the `-r2-gt` condition rows
(before 4), **7b** the audit-adjudication closure check and the single manifest
regeneration (after 6). H6 ("step 7 is the only manifest writer") survives
intact on 7b.

**B3 — the companion command. FIX (contract + code).** Re-verified with two
line corrections to the audit: `--compute-mcc` at `stride55_score.py:195` is an
argument *the script passes down to* `evaluate_detections.py`, not a flag of its
own — the argparse block (`:216–230`) has none, so the contract's command dies
at argument parsing. The union gate is at `:108–112`, not `:105` (`:105` is
docstring). The substance is confirmed and the numbers are exact: the crop
manifest for `g384_ov192_55map` holds **57,482** candidates (the K=10 union)
while ladder B N=5 `union_n` is **43,909**, so `--union-n 43909` raises. And
`--min-votes 5` filters the K=10 union, which is not the first-5 rung.
Disposition: drop `--compute-mcc` (MCC is already unconditional), and route the
companion through the first-N derivation rather than the union path — the same
code the rung fix (M7) needs. **Confirmed clean:** the ladder's B N=5 carried
value is `0.8437752627324171`, so the contract's 1e-6 gate against `0.843775`
is sound.

**B4 — the regression gates. FIX in the main, DISPUTE in part.**
*Confirmed:* G3 (`final_board_build.py:316–345`) reads the hard-wired r1 home
`STD_REF_DIR` (`:79`) and demands F1, every pairwise p-value and tier
membership reproduce the committed board to **1e-9**; G4
(`final_board_sweeps.py:236–253`) checks the same board at `MECHANISM_BOUND =
0.003` (`:99`); and both scripts take their reference from `standardised_gt()`
(`:308` and `:225` respectively), so switching that function to r2 fails both by
construction.
*Disputed:* "G4's bound is tighter than the contract's band" is a category
error. `MECHANISM_BOUND` bounds *micro-F1 recomputed by the light scorer against
the committed evaluation's F1, under one reference* — a mechanism-agreement
tolerance. The contract's 0.005 bounds *r1 → r2 movement of the point estimate* —
a scientific drift band. They measure different quantities and do not conflict;
0.003 is not "tighter than" 0.005 in any comparable sense.
*Fix:* the regression gates are pinned to r1 and made reference-independent —
G3/G4 always build their gate reference from the r1 layers regardless of the
run's target vintage, so "the mechanism still reproduces the committed r1 board"
stays a live check *during* the r2 build instead of being disabled by it. See
PI fork 3.

### Majors

**M5 — H1 contradicts the template. FIX (H1 re-specified).** Confirmed exactly:
IM-k4's `_metadata.cli_args.ground_truth` is the single merged path
`inputs/vectors/references/best-available-gt-55maps.geojson`;
`build_extended_gt` (`compute_corrected_f1_multi_buffer.py:386–389`) takes **two**
frames; `materialise_best_available_gt.py --vintage r2` writes one merged
geojson + csv (stem `best-available-gt-55maps-r2`, `:274`) and no layer files.
H1 as written is unbuildable. Its *intent* — the 5 m channel-duplicate audit must
apply to the r2 reference, and the engine must never be handed a reference built
by an unaudited path — is correct and survives; only the mechanism is
re-specified. See PI fork 1.

**M6 — r1 homes are not read-only. FIX (code).** Confirmed: `OUT` is a module
constant in `final_board_sweeps.py` (writes `cells/<label>/detections.geojson`
at `:359`, rewrites `sweeps.json` and `cells_manifest.json` at `:376–378`) and in
`final_board_n3_carried.py` (`:98`, `:74`); `OUT_BASE`
(`register_standardised_gt_conditions.py:53`) is a constant and `adapt_one`
overwrites `<cell>/evaluation.json` in place (`:110`, `:214`). No override flag
exists on any of them. H2 is therefore not merely a convention to follow — it is
code that must be written *before* step 3, or the first r2 run destroys the
artefacts G3 reads. Elevated to a **pre-step-3 blocker** in the amended
contract.

**M7 — the 3.7 rungs. FIX (contract).** Confirmed. Amplification: a first-N
derivation *does* exist in the script the contract names —
`final_board_sweeps.py:196` calls `cluster_first_n(passes, n, index)` for
n ∈ (1, 3, 5) — but it is bound to the stride A/B cells (`:187`), and its pass
loader `stride55_ladder.load_deduped_passes` hard-codes `range(1, 11)`
(`:122`). The 3.7 arms are K=5 with their own loaders
(`gemini37_arm_ladder.py:93` `K_TOTAL = 5`, `:153` `cluster_first_n(passes,
K_TOTAL, ...)`), score against `build_extended_gt(student, phantoms)` (`:140`) —
the canonical extended GT — and emit only `ladder.json` (`:227`). So the
contract names a real derivation that cannot reach the 3.7 passes. H5's "no rung
registered from sweep numbers alone" is right and currently unsatisfiable; the
3.7 rung materialisation is promoted to its own contract sub-step with named
inputs.

**M8 — H8's tripwire is false. FIX (H8 replaced) + scope escalation.** Confirmed
on both legs. BH is applied across the whole pair family
(`build_tiered_leaderboard.py:1512`) and a top-N filter (default 20) at `:1040`,
so adding seven cells moves adjusted p-values and tier membership *legitimately*
— a rank change is not evidence of a mechanism error, and gating on it would
halt a correct run. Replacement gate: the pre-existing cells' **raw** F1, MCC
and **raw** pairwise p-values must reproduce to 1e-9 (these are invariant to the
cell set), while BH-adjusted p-values and tiers are **reported as a diff table,
not gated**. The r1 anchor (image-b 0.8961) is retained.
*Scope escalation:* `results/leaderboard/era2/` holds only a `.cache` directory
and git-tracks **zero** files; no leaderboard spec YAML exists anywhere in the
repo; `planning/condition-inventory.json` has 190 entries and **zero** 3.7/3.8
ones. The GS reference is untouched by r2 (`DEFAULT_GROUND_TRUTH:114` is
`mounds-reference.geojson`). The GS leg is therefore a **build from scratch that
r2 does not require** — it is riding inside a recompute chain it has no
data dependency on. See PI fork 2.

**M9 — silent "unresolved". FIX (code).** Confirmed:
`lib_uplift_supplement.py:733` resolves by basename against
`REFERENCE_BY_FILENAME` (`:130–135`, four entries, no r2); the label-suffix
fallbacks (`:742–749`) know only `-standardised-gt` / `-canonical-gt`; `:760`
returns `ReferenceResolution(None, None, "unresolved")` without raising. And
`REFERENCE_N_MOUNDS` (`:141–146`) is a separate literal — note it records
`standardised: 5010` against r2's 5,018, so a one-line filename fix would leave
the supplement quoting the wrong mound count. Fix is three-part: both dict
entries, plus an `-r2-gt` label-suffix fallback, plus **"unresolved" raises** for
any `best-available-gt-*` basename instead of degrading silently.

### Minors

**M10 — ACCEPT → FIX (one-line).** Confirmed: `N_STUDENT_STD = 4731`,
`N_EXTENSION_STD = 279` (`score_55maps_standardised_reference.py:111–112`)
against r2's 4,726 / 278 / 14. The gate becomes vintage-aware rather than
literal.

**M11 — FIX (one-line).** Confirmed: `empty_tile_adjudicate.py` `GT_FILES`
(`:81–84`) has `standardised` and `canonical` only. Step 7b's closure check
needs an `r2` entry.

**M12 — FIX (two-line).** Confirmed and the ordering matters:
`materialise_best_available_gt.py:283–284` calls
`removed_path.relative_to(PROJECT_ROOT)` inside a logger call that runs
*before* the geojson write at `:290`, so an out-of-repo `--out-dir` loses the
artefact, not just the log line. Same pattern at
`derive_audit_revision_instructions.py:160–161`. Both become `os.path.relpath`.

**M13 — ACCEPT.** Confirmed: IM-k4's `_metadata` carries `script_git_commit:
4ac0eeedf`, `script_git_status: "dirty"`. The engine gate's target was built
from an uncommitted tree, so an exact reproduction is not guaranteed by
provenance alone. Recorded as a stop-state caveat: if step 2 misses at 4 dp, the
dirty stamp is the **first** hypothesis to test, not a mechanism failure.

**M14 — ACCEPT.** Pass order is carried only by `run_<i>` naming and
`load_deduped_passes` gates on tile-set equality, not order. No change; recorded
in stop states (the first-N derivation must read the committed `run_<i>`
sequence).

**M15 — ACCEPT (deferred).** Confirmed:
`docs/manifest-schemas/runs-manifest.schema.json:65–67` enumerates
`gt_reference` as `["curator", "student", "combined"]`. The r2 rows register at
condition level with a `-r2-gt` label, not at run level, so no schema change is
required by this block. Flagged for the schema's next revision.

### Tally

**FIX 11** (B1, B2, B3, B4-main, M5, M6, M7, M8, M9, M10, M11, M12 — 12 items,
B4 counted once) · **ACCEPT 3** (M13, M14, M15) · **DISPUTE 1, in part**
(B4's 0.003-vs-0.005 comparison).

### Open to the PI (three forks the adjudication cannot settle)

1. **How r2 enters the board chain** (H1's replacement mechanism).
2. **Whether the GS Era-2 board leg stays inside this block** (M8's scope
   escalation).
3. **How the r1 regression gates behave during an r2 build** (B4's fix).

The chain stays **NO-GO** until these are ruled, H1–H3 land as code, and the PI
gives a formal go with stop conditions in his own words.

## Changelog

### 2026-09-07 (S149-b) — Wording correction to the disposition

The disposition's "16th finding" said `apply_audit_revision` had no
spatial de-duplication "at all"; the card's § 3b shows a "no pair
within 15 m" check was run by hand in S148. Accurate wording:
*unenforced in code or tests*, not *unguarded*. The gate landed in
`fc54feac6` stands. Also recorded: the engine-gate target (MINOR 13)
reproduced exactly in a scratch pre-flight (Δ = 0 over 14 buffers × 5
fields), closing that caveat; and MINOR 14 is closed by committed pass
pins (`7caccb4be`).

### 2026-09-06 (later) — Disposition of all 15 findings

Every finding re-verified against the named source file before adjudication
(13 scripts re-opened at the cited lines, 6 data files re-read, 5 filesystem
probes). **All 15 hold.** Disposition: 11 FIX, 3 ACCEPT, 1 DISPUTE-in-part.

| Finding | Disposition | Note |
| --- | --- | --- |
| B1 count | FIX | 29 → **36**; § 4a's "22" → **32**; count derived, not literal |
| B2 order | FIX | step 7 splits 7a/7b; order → 1→2→3→**7a**→4→{5,6}→**7b**→8 |
| B3 companion | FIX | drop `--compute-mcc`; route via first-N, not the K=10 union |
| B4 gates | FIX + **DISPUTE in part** | gates pin to r1; 0.003-vs-0.005 is a category error |
| M5 H1 | FIX | H1 re-specified; intent survives, mechanism does not |
| M6 r1 homes | FIX | **elevated to a pre-step-3 blocker** (code, not convention) |
| M7 3.7 rungs | FIX | own sub-step; the named derivation cannot reach K=5 passes |
| M8 H8 | FIX + scope | gate raw stats, report BH/tier diffs; GS leg is a new build |
| M9 unresolved | FIX | 3-part: both dicts + `-r2-gt` suffix + raise, not degrade |
| M10–M12 | FIX | vintage-aware gate; r2 `GT_FILES` entry; `relpath` (before write) |
| M13–M15 | ACCEPT | dirty-stamp caveat; pass-order note; schema deferred |

Corrections to the audit's own references, recorded so the report stays
citable: B3's `--compute-mcc` is at `:195` (a pass-through argument, not a CLI
flag) and the union gate at `:108–112`, not `:105`; M7's named derivation
*does* exist (`final_board_sweeps.py:196`) but is bound to the stride A/B cells.
Three forks referred to the PI: H1's replacement mechanism, whether the GS
Era-2 leg belongs in this block, and how G3/G4 behave during an r2 build.
Chain remains **NO-GO**.

### 2026-09-06 — Original publication

Fresh-context audit of the nine-step r2 recompute queue and hardenings H1–H9, run before
any step of the block. Four BLOCKER, five MAJOR and six MINOR claims with file:line
evidence; six probes, five clean.
