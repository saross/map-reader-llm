# Fresh-context audit 2 of the r2 recompute block (post-S149-b contract)

> **Last revised**: 2026-09-07 (S149-c disposition: 3 blockers and 6 majors
> fixed, 11 minors dispositioned). See [§ Changelog](#changelog) for revision
> history.

Audit of `planning/reference-revision-2026-09-06.md` §§ 4 / 4a against the code
they name, at git HEAD `1e457d83f` on `main`, working tree clean. Stance: naive
reviewer — "if an operator ran this block exactly as written, would it run, and
would it produce what the finish line says?" No step of the block was run; zero
API spend; nothing written outside `/tmp` and this report.

Corrections below are **claims, not verdicts**. Each says what was opened and
what was executed. Where I disagree with the contract I have re-read the source
file inside this pass rather than relying on the earlier report.

## Denominator

**Contract opened**: `planning/reference-revision-2026-09-06.md` lines 140–864
(§§ 3, 3a, 3b, 4, 4a, 5, and both amending changelog entries) — 725 of 864 lines.
**Prior report opened**: `reports/r2-chain-pre-run-audit-2026-09-06.md`, all 364
lines (Denominator, Findings, Clean probes, Disposition, Changelog).

**Scripts opened** (23; lines, F = in full, P = in part):
`build_55map_leaderboard.py` 471 F; `final_board_sweeps.py` 524 F;
`final_board_build.py` 770 F; `final_board_n3_carried.py` 140 F;
`register_r2_conditions.py` 285 F; `stride55_score.py` 274 F;
`pin_pass_provenance.py` 297 P; `mcc_tiering_55map.py` 569 P;
`stride55_ladder.py` 319 P; `gemini37_arm_ladder.py` 245 P;
`gemini37_sweep_oracle.py` 383 P; `register_standardised_gt_conditions.py` 416 P;
`score_55maps_standardised_reference.py` 863 P; `lib_uplift_supplement.py` 1762 P;
`evaluate_detections.py` 2488 P (`--help` + the D40 git-state block);
`compute_corrected_f1_multi_buffer.py` 1485 P (`--help` + output paths);
`register_pass2_author.py` 246 P; `pairwise_permutation_test.py` P;
`lib_advanced_metrics.py` P; `empty_tile_adjudicate.py` P;
`materialise_best_available_gt.py` P; `derive_audit_revision_instructions.py` P;
`tests/test_r2_chain_hardenings.py` 372 P.

**Data opened** (18): `results/run-conditions.json` (whole register, 41 runs);
`results/55map-final-board-2026-08-27/{cells_manifest.json, final_board_50m.json,
sweeps.json}`; `results/55map-final-board-2026-08-27/cells/A-N1-oracle/evaluation.json`;
`results/55maps-standardised-ref-2026-08-14/IM-k4/evaluation.json`;
`results/stride55-2026-08-27/ladder.json`;
`results/stride55-2026-08-27/g384_ov192_55map/primary/eval/evaluation.json`;
`results/gemini37-55map-2026-08-31/ladder/ladder.json`;
`results/gemini37-fourth-cell/55map/g384_ov192_55map/ladder.json`;
the three 3.7 committed primaries' `verified_detections.geojson`;
the three 3.7 `standardised-ref/evaluation.json`;
`inputs/vectors/references/best-available-gt-55maps-r2.geojson`;
the three committed pins under `inputs/**/*_passes.json` (via `verify`).

**Claims checked**: 26. **Probes**: 10 (a–j), all read-only.

**NOT checked**: `register_gemini37_author.py` (the r1 3.7 registrar — I checked
its *output* rows in `run-conditions.json` instead of its code);
`build_tiered_leaderboard.py` and the split-out GS Era-2 leg; §§ 2 / 2b estimator
arithmetic; `tests/test_reference_revision_r2.py`; `marking_campaign_gates.py`;
`verify_run_conditions.py` source (run only); `render_figure` output; steps 5, 6,
8 and 9 beyond the existence of their scripts; any scoring, sweep or board run.

## Findings

3 BLOCKER · 6 MAJOR · 11 MINOR.

### Blockers

**BLOCKER 1 — § 4 orders 4b before 4c, but 4c materialises two of the 31 cells
4b must score.** The declared hard order is `1 → 2 → 3 → 7a-i → 4a → 4b → 4c →
4d → 7a-ii → {5, 6} → 7b → 8`
(`planning/reference-revision-2026-09-06.md:460`), and § 1 (3) / step 4b assign
"the 31 sweep-derived cells" to 4b (`:349`, `:288-293`). But
`final_board_n3_carried.py:115-124` is what writes
`<board home>/cells/A-N3-carried/detections.geojson` and
`.../B-N3-carried/detections.geojson` and appends both to `cells_manifest.json`
— they do not exist until 4c has run. `final_board_build.py:482-497` then
requires `out/"cells"/<label>/"evaluation.json"` for **every** manifest cell with
`committed_eval: False`. *Failure*: 4b can only score 29 of 31; 4d dies with
`FileNotFoundError` on `results/55map-final-board-r2-2026-09-06/cells/A-N3-carried/evaluation.json`
after the full r2 sweep and 29 bootstrap scorings have burned most of a day of
sapphire time, and the § 2 (3) count lands at 39, not 41. The r1 chain evidently
ran sweeps → n3 → stage 2 → build: `results/55map-final-board-2026-08-27/cells/A-N3-carried/`
holds `detections.geojson` *and* `evaluation.json` (probe f). Correct order is
`4a → 4c → 4b → 4d`.

**BLOCKER 2 — `--require-clean-inputs` at step 4b refuses every one of the 31
board cells.** § 3 makes it a stop-state that "`input_git_state.inputs` all
`clean` or `ignored` on every evaluation written (steps 3 and 4b run
`--require-clean-inputs`)" (`:436-439`). `evaluate_detections.py:541` defines
`_DIRTY_INPUT_STATES = {"modified", "untracked"}`, `:518` and `:533` classify a
file that is neither tracked nor gitignored as `untracked`, and `:568-572` raises
`SystemExit(4)` — "REFUSING to score against dirty inputs" — when
`require_clean` is set. The detections 4b scores are written seconds earlier by
`final_board_sweeps.py:498-500` into
`results/55map-final-board-r2-2026-09-06/cells/<label>/detections.geojson`, which
is not gitignored (probe g: `git check-ignore` returns rc 1 on that path; the r1
equivalent is *tracked*, not ignored). *Failure*: all 31 stage-2 invocations exit
4 until the operator commits the 31 detection files — a step the contract never
states. The r1 precedent confirms the flag was not used there: A-N1-oracle's
`_metadata.cli_args.require_clean_inputs` is `false` (probe c). Step 3 is
unaffected — all nine of its detection inputs are tracked and clean (probe h).

**BLOCKER 3 — the step-3 → step-4 sequencing gate is unsatisfiable.** § 3 reads
"step 4 never starts before step 3's count is **36/36** and step 7a has
registered every `-r2-gt` row" (`:448-449`). After S149-b's restructure step 3
produces **nine** evaluations, not 36 — the same document says so 40 lines
earlier ("9 in the r2 scoring home (step 3)", `:407`), and the derivation
(`build_55map_leaderboard.NAMES` ∪ `final_board_build.COMMITTED_CARRIED`) gives
exactly nine (probe a). The "36" is S149's pre-split total carried forward.
*Failure*: an operator honouring the stop gate literally never starts step 4;
one who overrides it has just overridden the block's only sequencing gate.

### Majors

**MAJOR 4 — H15 is false for one of the three scripts it names: `final_board_n3_carried.py`
has no `--force-r1` and no refusal.** H15 states that
"`final_board_sweeps.py`, `final_board_build.py` and `final_board_n3_carried.py`
refuse `--reference standardised` when the committed r1 home exists unless
`--force-r1`" (`:663-668`), and § 5 repeats it ("the r1 homes are REFUSED without
`--force-r1`", `:487-488`). Verified: the guard exists in
`final_board_sweeps.py:331-344` and `final_board_build.py:381-399`, but
`final_board_n3_carried.py`'s argparse (`:134-139`) has only `--reference`, and
`main()` (`:77-130`) has no existence check at all. *Failure*:
`python scripts/final_board_n3_carried.py` with no arguments overwrites
`results/55map-final-board-2026-08-27/cells/{A,B}-N3-carried/detections.geojson`
and rewrites the r1 `cells_manifest.json` (`:127`, unconditional) — the r1
artefacts G3 reads.

**MAJOR 5 — the G3/G4 gate target itself is unprotected, so "the r1 homes are
read-only throughout" (§ 4 (iv)) is false.** `final_board_build.py:112-113`
pins `COMMITTED_BOARD` to `results/55map-leaderboard/55map_leaderboard_50m_standardised.json`
and `:418`, `:431-443` compares F1, all 28 pairwise p-values and tier membership
against it at 1e-9; `final_board_sweeps.py:361-364` reads the same file for G4.
`build_55map_leaderboard.py:340-346`, `:444-446` writes exactly that file under
`--reference standardised` with **no guard of any kind** — no `--force-r1`, no
existence check. Two smaller writers of r1 homes remain likewise unguarded:
`register_standardised_gt_conditions.py:307-308` overwrites each
`results/55maps-standardised-ref-2026-08-14/<cell>/evaluation.json` in place
(default `--reference standardised`), and `mcc_tiering_55map.py:406-407,451`
rewrites `results/metric-leaderboards/55map-mcc-tiering-standardised.{json,md}`.
*Failure*: an operator who regenerates the r1 board for the drift table silently
rewrites the very file G3/G4 prove the mechanism against, and both regression
gates become tautologies.

**MAJOR 6 — the leaderboard's own missing-row message sends the operator to the
wrong registrar, which then dies.** `build_55map_leaderboard.py:378-381` exits
with "Run `register_standardised_gt_conditions.py --reference {reference}` first
(step 7a before step 4)". H12 replaced that route with
`register_r2_conditions.py` (`:751-762`). Following the message,
`register_standardised_gt_conditions.main("r2")` calls `adapt_one` for all eight
`CELLS` (`:369-370`), and `adapt_one:220` reads
`results/55maps-r2-ref-2026-09-06/<cell>/summary.json` — a Track-2 artefact that
step 3 (which runs `evaluate_detections.py`) never writes. *Failure*:
`FileNotFoundError` at the first cell; and even had it worked it registers 8 of
the 9 scoring-home rows (`REGISTRATIONS`, `:106-124`, has no IM-k4 entry).
Worse, the same command with its **default** `--reference standardised`
overwrites the r1 evaluations (MAJOR 5).

**MAJOR 7 — the two steps that produce 40 of the 41 evaluations have no driver,
and § 5's resumability describes tooling that does not exist.** No script in
`scripts/` writes into `results/55maps-r2-ref-2026-09-06/`
(probe b, repo-wide grep — the only hits are the registrar/board/MCC constants),
and there is no stage-2 driver: `grep -l cells_manifest scripts/` returns only
`final_board_sweeps.py`, `final_board_build.py`, `final_board_n3_carried.py`,
`register_pass2_author.py` and `register_r2_conditions.py`.
`score_55maps_standardised_reference.py` is not it: it has no `--reference`
argument (its argparse block is `:696-730`), `census_checks()` is called at
`:772` with the r1 default so the `r2` branch at `:288-289` is unreachable, its
`CELLS` list is eight cells (no IM-k4), and it scores with the Track-2 engine,
not the `evaluate_detections.py` H14 mandates. *Failure*: steps 3 and 4b are 40
hand-assembled command lines; § 5's "a cell with an existing `evaluation.json` is
skipped, so a halted step 3 resumes" (`:479-481`) and § 4's "within step 3, cells
are independent (workers)" (`:475`) are both false of any tool in the repo. The
per-command spec in § 4 is complete enough to script by hand — that is why this
is MAJOR and not a blocker — but the resumability and visibility guarantees are
not backed by code.

**MAJOR 8 — the companion sub-step has no position in the dependency graph, is
filed under a step that precedes the artefact it consumes, and its registration
route is unnamed.** § 1 (3) places the companion inside step 3's inventory
(`:355-370`) while its input is `cells/B-N5-carried/detections.geojson` from the
**r2 sweep** (4a); § 4's hard order (`:460`) never mentions it. Its evaluation is
declared "the 41st file of the chain" (`:369-370`) and its 1e-6 miss is a
stop-state (`:444-445`), so the finish line depends on a step with no slot.
Additionally the row it must register (`g384-ov192-55map-n5-carried-p0.15-k5-canonical-gt`)
would point at a `compute_corrected_f1_multi_buffer.py` output — that engine
writes `summary.json`, `corrected-f1.csv` and `report_autogen.md`
(`:1375-1384`), not the `evaluation.json` the register expects; the r1 precedent
inserted an adapter (`results/stride55-2026-08-27/g384_ov192_55map/primary/eval/evaluation.json`
carries `_metadata.adapted_by: "scripts/register_pass1_adapt.py"`, probe i),
which the contract never names.

**MAJOR 9 — the r2 board's markdown would ship r1 provenance and an r1
changelog.** `final_board_build.py:700-748` appends a hard-coded "Provenance and
gates" section ("G4 scorer gate ×9 exact; identity gates ×9 exact counts;
mechanism gates ×5"; "the 8-cell committed standardised board reproduced
exactly ... all 28 pairwise p-values") and a Changelog whose last entry is
"### 2026-08-27 — Original publication / Built by Session 143". On an r2 run
those tallies are wrong (12 G4 checks, 12 identity gates, 8 mechanism gates
under `include_g37`) and the changelog contradicts the banner two hundred lines
above it, which correctly says `BUILD_DATE_R2 = "2026-09-07"` (`:116`, `:539-540`).
The run-table prose also still says "Tiers from the 21-cell board above"
(`:581`) on a 35-cell board. *Failure*: `final-board-50m.md` is a citable
results document under the project's revision policy; it would state gate counts
never performed and a publication date four months stale.

### Minors

**MINOR 10** — § 4 says 7a-ii authors "the 31 board-home rows" (`:464`). Probe d
(a synthetic full 35-cell r2 manifest through `register_r2_conditions.author_board_rows`,
nothing written) returns 31 plan entries but **28 `add` + 3 `coincident`** when
the r2 argmaxes for TH7/IM/UPL land on their committed points — matching the r1
register exactly (16 board-home rows for 19 non-committed r1 cells). § 2 (7)'s
"`-r2-gt` condition rows for every re-scored cell" is therefore unattainable for
the three coincident oracles' board-home evaluations by design.

**MINOR 11** — § 2 (3) counts "41 evaluation files ... with
`tile_classification.confusion` populated" (`:405-408`). The 41st is the
canonical companion, which is a Track-2 `summary.json`, not an `evaluation.json`,
and is not on r2 — the same paragraph says so. The countable finish state should
be 40 + 1.

**MINOR 12** — § 2 (7)'s "`verify_run_conditions.py` green" cannot be met.
Probe e: it exits 1 today — "41 run(s): 8 pass, 29 partial, 4 fail" — and
`stride-55map-2026-08-25`, the run 7a-ii adds ~16 rows to, is one of the four
FAILs (four `eval-detections-mismatch` errors on its pre-existing `-canonical-gt`
rows, whose adapted evaluations carry `input_files: null`). The gate needs a
scoped form ("no new errors on the runs this chain touches").

**MINOR 13** — H3 claims `score_55maps_standardised_reference.census_checks("r2")`
landed (`:559-562`). The function exists (`:281-289`) but is dead code: the only
call site is `:772`, with the r1 default, and there is no CLI flag to reach it.

**MINOR 14** — the companion command as prose ("`compute_corrected_f1_multi_buffer.py`
with the canonical review, buffers 20/30/50, B = 10,000, seed 42, MCC",
`:364-367`) omits `--review-yesterday`, which that engine requires in legacy
ring-gated mode. `stride55_score.py:163-177,189` supplies a header-only CSV;
the committed one is `results/stride55-2026-08-27/empty-yesterday-review.csv`
(git-tracked). Passing the real yesterday review would change the phantom set
and blow the 1e-6 gate.

**MINOR 15** — the companion scores a file that has been round-tripped through
EPSG:4326 GeoJSON (`final_board_sweeps.py:500`, `sub.to_crs("EPSG:4326").to_file(...)`),
whereas the ladder's `0.8437752627324171` was computed on the in-memory UTM
frame (`stride55_ladder.py:267-270`). The project's own geometry gate budgets
0.01 m for exactly that round-trip (`final_board_sweeps.py:448`); the companion
gate is 1e-6 on F1, where a single flipped 50 m match moves F1 by ~1e-4.

**MINOR 16** — on a 35-cell board `compact_letters` (`final_board_build.py:191-225`)
runs unpivoted Bron–Kerbosch over 35 nodes and falls back to `z1, z2, …` past 26
maximal cliques (`:222`); the docstring still says "21 nodes" and
`render_figure`'s `figsize=(13.5, 8.5)` (`:333`) was sized for 21 rows.

**MINOR 17** — the 3.7 legs of G4, the mechanism gate and the geometry gate have
never been executed. The inputs check out at source (probe j: identity counts
5,229 / 5,003 / 4,246 are the committed primaries' exact feature counts; F1@50
0.8550 / 0.8825 / 0.8732 are their `standardised-ref/evaluation.json` values),
but whether the light micro-F1 scorer agrees with the engine's corrected-F1
within `MECHANISM_BOUND = 0.003` on those three cells is unmeasured — the 0.003
bound was calibrated on the eight legacy cells + IM-k4.

**MINOR 18** — the § 3 tripwire "a 3.7 rung out of monotone order with its N = 5
cell" (`:443-444`) has no committed reference point: `gemini37_arm_ladder.py:99`
sets `NS = (1, 3)`, so the arm ladders carry no N = 5 oracle, and on the
canonical chain arm 1's N = 3 oracle (0.864478) already exceeds its N = 5
carried value (0.8494 per the campaign card). The comparison exists only inside
the r2 sweep, and comparing an oracle to a carried point is not monotonicity.

**MINOR 19** — § 3's environment line assigns "sapphire only for steps 3–4 ...
the local machine only for the $0 minute-scale steps 6, 7a, 7b, 9" (`:452-453`)
and gives the companion — a 10,000-iteration bootstrap over ~4,700 detections at
three buffers — no environment. Step 5 ("re-measure the reference-dependent
analyses ... the uplift-supplement pairing sets; the sensitivity/MDE appendix")
names no tooling at all.

**MINOR 20** — `scripts/estimated_correction.py` (step 6) and
`scripts/student_baseline_reestimate.py` (step 9) do not exist. § 1 flags both as
new, so this is disclosure-complete, but two unwritten scripts sit inside a block
described as deterministic, resumable and countable.

## Disposition (S149-c, 2026-09-07)

Every finding re-verified at source before adjudication (the three
blockers and five majors by re-reading the cited lines and re-running
the cited probes; the minors against the scripts and the register).
**All 20 hold**; one (MINOR 14) was initially mis-dispositioned as a
dispute and corrected on re-reading `stride55_score.py:163-189`.

| # | Disposition | What changed |
| --- | --- | --- |
| B1 | FIX (contract) | step 4 re-ordered and renumbered: 4a sweep → 4b N=3 carried → 4c commit → 4d scoring → 4e boards → 4f companion |
| B2 | FIX (contract) | 4c commits the materialised cells before 4d scores them (the r1 board's cells are tracked, so this is the r1 pattern); `--require-clean-inputs` kept, provenance meaningful |
| B3 | FIX (contract) | § 3 sequencing restated per stage with derived counts; "36/36" gone |
| M4 | FIX (code) | `final_board_n3_carried.py --force-r1` guard (`882c72a31`) |
| M5 | FIX (code) | `build_55map_leaderboard.py`, `mcc_tiering_55map.py`, `register_standardised_gt_conditions.py` refuse to rewrite committed r1 artefacts without `--force-r1` — the G3/G4 gate target included |
| M6 | FIX (code) | the missing-row message names `register_r2_conditions.py --write` under r2 |
| M7 | FIX (code) | `scripts/r2_score_cells.py`: `--stage fixed` (9) / `--stage board` (31), IM-k4 recipe verbatim against r2, resume, `--require-clean-inputs` + post-run gate, `--dry-run` with derived counts (H16) |
| M8 | FIX (contract) | companion is 4f, on sapphire, consumes 4a's `B-N5-carried`, registered via `register_pass1_adapt.py` |
| M9 | FIX (code) | r2 board provenance derived from the run (families swept, the G3 reproduction performed, each coincidence verdict); own changelog; "21-cell" derived |
| M10 | FIX (wording) | "up to 31 rows; coincident oracles excluded by design" |
| M11 | FIX (wording) | the 41st file is a Track-2 `summary.json` |
| M12 | FIX-PENDING | pre-existing register debt (four runs; eleven unclaimed `uplift-supplement/k1-gapfill` evaluations) recorded as a pre-7b item; not r2 work, does not block steps 2–4 |
| M13 | ACCEPT | `census_checks("r2")` is unreachable from the CLI and unused by the chain (the chain's engine is `evaluate_detections.py`); retained, harmless |
| M14 | FIX (contract) | the header-only `--review-yesterday` CSV is named; the real yesterday review would change the phantom set |
| M15 | ACCEPT + rule | a one-count miss at the 1e-6 companion gate → the 4326 round-trip is the first hypothesis; escalate, never widen |
| M16 | ACCEPT | letters roll to `z1…` past 26 cliques by design; figure sizing is checked at 4e — a cramped figure is a presentation defect, not a number |
| M17 | ACCEPT | the 3.7 identity counts are being validated on sapphire before the chain; G4/mechanism/geometry on the 3.7 cells run at 4a and ARE the gate; if a 3.7 cell misses 0.003, escalate — the bound is not widened |
| M18 | FIX (wording) | the tripwire compares each rung's r2 oracle with its family's N=K r2 oracle from the same sweep |
| M19 | FIX (contract) | companion on sapphire; step-5 tooling recorded as pre-step-5 work |
| M20 | ACCEPT | the two step-6/9 scripts are declared new in § 1; written at their steps |

**Tally**: FIX 14 (12 landed, M12 pending as pre-7b debt) · ACCEPT 5 ·
DISPUTE 0.

## Clean probes

- **(a) Step 3 / step 4 split — CLEAN.** `final_board_build.py:475` retargets the
  four carried incumbents' `ev_path` through `retarget()` (`:98-111`) into
  `results/55maps-r2-ref-2026-09-06/`, while `:476` reads their *detections* from
  the unretargeted path — correct, detections do not move between vintages, and
  IM-k4's detection file legitimately lives inside the r1 home. Manifest cells
  are read from `out/"cells"/<label>/evaluation.json` where `out = board_home(r2)`
  (`:393`, `:485`). G3 stays on `STD_REF_DIR` unretargeted (`:423`), G4 on
  `standardised_gt()` (`final_board_sweeps.py:353, 374, 416`). § 1 (3) and step
  4b describe the code correctly. `NAMES` (8 cells) ∪ `COMMITTED_CARRIED` (4)
  = the nine cells step 3 lists, exactly.
- **(b) Counts — CLEAN, derived from code.** r2 sweep families = 13 r1-pattern +
  9 3.7 = 22 (`build_families:217-256` + `build_g37_families:280-297`);
  materialised = 22 oracles + 7 carried (`:506-513`) = 29; + 4 committed carried
  = 33 manifest cells; + 2 from `final_board_n3_carried` = **35 board cells**;
  non-committed = **31 board-home evaluations**; + 9 scoring-home + 1 companion
  = **41**. The r1 manifest independently confirms the base: 23 cells, 4 with
  `committed_eval: true`, 19 `cells/` directories.
- **(c) Sweep reference split — CLEAN.** Under `--reference r2` the pool is
  `ref = reference_gt("r2")` (`final_board_sweeps.py:354`, passed to the workers
  at `:465`) while G4 (`:374`) and the mechanism gates (`:416`) use `gate_ref =
  standardised_gt()`; identity (`:393-401`) and geometry (`:438-452`) gates are
  reference-independent by construction. Oracle = argmax on r2 for every family,
  uniformly (`:507-510`).
- **(d) 7a-i dry run — CLEAN.** `register_r2_conditions.py` with no `--write`
  plans exactly **9** rows, one per step-3 cell (IM-k3, IM-k4, TH7-k3/k4,
  T03-k3/k4, TM-k3/k4, TM-n10-k5), each `eval_path` =
  `results/55maps-r2-ref-2026-09-06/<cell>/evaluation.json` — precisely where
  step 3 writes. All eight `(run_id, label)` pairs `NAMES_R2` resolves are
  covered, so `build_55map_leaderboard --reference r2` will find every row.
- **(e) 7a-ii coverage — CLEAN (see MINOR 10 for the count).** Driving
  `author_board_rows` with a synthetic 35-cell r2 manifest resolves every family
  scheme: stride A/B and rungs, the post-hoc N = 3 carried cells, the five
  incumbent oracles, ARM1/ARM2 with their N = 1 / N = 3 rungs, and FOURTH with
  its rungs. Labels mirror the r1 registrars exactly, and no two rows collide
  *within a run* (`verified-oracle-p0.20-k3-r2-gt` appears in two different runs,
  which is the r1 pattern).
- **(f) Pass pins — CLEAN.** `pin_pass_provenance.py verify --all`: 3/3 OK
  (`g37:g384_ov192_55map_g37` K = 5, 11 files; both stride cells K = 10, 19
  files). Both loaders gate: `stride55_ladder.py:134-135` and
  `gemini37_arm_ladder.py:110-111`. `verify_pin` (`:222-252`) checks per-position
  `run_id`, the exact file set, every SHA-256, and any `run_<j>` beyond K, so a
  swap or a stray pass raises. Residual gap: a pass whose `meta.json` is absent
  pins `run_id: null` and skips that half of the check (`:232`) — hashes still
  gate.
- **(g) r2 reference gates — CLEAN.** Reading the committed file: 5,018 records =
  4,726 `student_standardised` + 278 `extension_standardised` + 14
  `audit_reviewed`; `gt_id` unique; minimum separation **15.48 m** (3.1× the 5 m
  `DEDUP_TOLERANCE_M`). § 3, § 3b and `r2_gt()`'s three invariants all agree.
  `source_map` is present, which `compute_per_tile_tp_fp_fn` requires
  (`lib_advanced_metrics.py:988-995`).
- **(h) 3.7 anchors — CLEAN.** Identity counts and F1@50 anchors verified at
  source, not from prose (see MINOR 17 for what is *not* verified).
- **(i) Companion detection set — CLEAN.** `final_board_sweeps.build_families:245-253`
  reproduces `stride55_ladder.main:228-233` line for line (`cluster_first_n(passes, 5)`,
  nearest-neighbour probability inheritance from the K = 10 union, `d <=
  INHERIT_TOL_M`), and materialises B-N5-carried at the identity point (0.15, k5)
  gated to 4,736 features — which is exactly `ladder.json`'s
  `runs.g384_ov192_55map.N.5.carried.n_detections`, whose `corrected_f1` is
  `0.8437752627324171`. So the contract's "the SAME detection set" holds, modulo
  MINOR 15's 4326 round-trip. The 3.7 ladders carry `oracle` **only** at N = 1
  and N = 3 (no `carried` key at any rung), as the contract states.
- **(j) MCC board on r2 — CLEAN.** It tiers the eight cells of
  `mcc_tiering_55map.CELLS:95-104`, reads them from `TRACK2_R2` (`:78`, `:451`),
  and `_load_cell_inputs:260-271` falls back to `evaluation.json` when no
  `summary.json` exists, flattening `tile_classification.mcc.point` /
  `.ci_lower` / `.ci_upper` and `confusion` — the exact shape
  `evaluate_detections.py` writes (verified against IM-k4's committed
  `evaluation.json`). Output stem `55map-mcc-tiering-r2` matches § 1 (4).
- **Also clean**: `evaluate_detections.py --help` carries every flag step 3 names
  (`--buffers`, `--ground-truth`, `--bootstrap`, `--seed`, `--mcc`,
  `--require-clean-inputs`, and a `--batch`/`--workers` route the contract does
  not use); `compute_corrected_f1_multi_buffer.py --help` carries every flag the
  companion names; `lib_uplift_supplement` resolves r2 by filename, by `-r2-gt`
  suffix and by run facts, records 5,018, and **raises** on an unknown
  `best-available-gt-55maps*` vintage; `empty_tile_adjudicate.GT_FILES:88` has
  its r2 entry; both r2 scripts use `os.path.relpath`; `ruff check` is clean on
  the eight chain scripts plus the test file; `pytest -m tier1
  tests/test_r2_chain_hardenings.py` — 25 passed in 7.05 s.

## Verdict

**NO-GO** on BLOCKERs 1–3. Blockers 1 and 3 are contract edits (swap 4b/4c;
replace 36/36 with the derived 9). Blocker 2 needs a ruling: either commit the
31 r2 detection GeoJSONs between 4c and 4b, or drop `--require-clean-inputs`
from 4b and keep it on step 3 (the r1 chain did the latter). MAJORs 4–6 are
small code changes; MAJOR 7 is the decision whether to write the two drivers or
accept 40 hand-run commands; MAJORs 8–9 are a sub-step slot and a
vintage-aware markdown tail.

## Changelog

### 2026-09-07 (S149-c) — Disposition

All 20 findings adjudicated: 14 fix (12 landed — contract revision
"S149-c" and commit `882c72a31`; M12 pending as pre-existing register
debt), 5 accept, 0 dispute. MINOR 14 was first marked disputed on the
argparse default and corrected on re-reading `stride55_score.py`, which
passes a header-only yesterday review because the engine's legacy mode
needs one.

### 2026-09-07 — Original publication

Second fresh-context audit (H7), run against `planning/reference-revision-2026-09-06.md`
as amended by the 2026-09-06 (S149) and 2026-09-07 (S149-b) changelog entries, at
HEAD `1e457d83f`. Three BLOCKER, six MAJOR and eleven MINOR claims with file:line
evidence; ten read-only probes, all reported. No step of the block was run; zero
API spend. Prior pass and its disposition:
`reports/r2-chain-pre-run-audit-2026-09-06.md` — none of its fifteen findings is
re-reported here; each was re-checked at source and each landed fix verified,
except H15 (MAJOR 4) and the r1-home guards (MAJOR 5), which are recorded as
incomplete rather than wrong.
