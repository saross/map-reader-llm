# The three withheld Gemini 3.7 cells — eligibility table (W1.4, recorded in W1.0)

> **Last revised**: 2026-11-18 (original publication, before the cells' sheet-specific scores exist). See [§ Changelog](#changelog) for revision history.

- **Written by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), Wave 1 census agent (work item W1.0), on amd-tower,
  branch `tile-join-wave-1-w10` from `main` at `e92d1c5d7`.
- **Specification**: `planning/tile-join-wave-1-spec-2026-11-01.md`, W1.0
  ("The 3.7 eligibility table") and W1.4 (the rule). Ruling: D73 (4) in
  `planning/pi-decisions-2026-09-20.md`.
- **What this is**: one row per (cell, family) pair, fixed **before the
  cells' sheet-specific scores exist**. No score under any new join was
  computed for these cells by this agent.
- **Geometric scores were already on record.** Frame-wide geometric
  tile-MCC values for all three cells have been committed since
  2026-09-12: `reports/tile-mcc-geometric-join-2026-09-12.md:247–249`
  (§ 4.3), under `geometric-primary` 0.9535 / 0.9059 / 0.9121 and under
  `geometric-contains` 0.9262 / 0.8761 / 0.8903, for K = 1 opmax / K = 1
  carried / K = 3 opmax (the same cells' disclosure-only readings recur in
  `results/tile-join-audit/era2-board-mcc-tiering-2026-10-30/README.md:89–95`).
  So this rule is fixed before the sheet-specific scores exist, **not**
  before any geometric score was seen. That changes no verdict: the rule's
  inputs are recorded exclusion reasons, never scores, and no score enters
  any row below.
- Every path, line number, and count below was read from the file named
  beside it at `e92d1c5d7`.

## 1. The rule (W1.4, quoted)

A cell re-enters every family it otherwise qualifies for if, and only if:

1. its *only* recorded reason for exclusion was the tile-join refusal
   (`tile_join_detection_shortfall` or `tile_join_reference_shortfall`);
2. no other technical refusal or frame problem stands (absence of a
   vocabulary shortfall alone is insufficient; Astra, R5);
3. it scores successfully under the new defaults.

Its scores, favourable or not, play no part. Criterion 3 cannot be tested
until the Wave 1 code exists; it is tested in the smoke run (W1.5). Every
verdict below is therefore **eligible subject to criterion 3**, or not
eligible, or unresolved.

## 2. The three cells and their committed exclusion evidence

| Cell (register condition id) | Committed evaluation (the register's `eval_path`, `results/run-conditions.json`) | F1@20 in the evaluation and in the board's `withheld_cells` |
|---|---|---:|
| `gemini37-screen-2026-08-28::g37-text-k1-verified-carried-p0.10-k1` | `results/k-ladder-2026-09-12/phase2/cells/gemini37-screen-2026-08-28__g37-text-k1-verified-carried-p0_10-k1/evaluation.json` | 0.8616 / 0.8616 |
| `gemini37-screen-2026-08-28::g37-text-k1-verified-opmax` | `results/k-ladder-2026-09-12/phase2/cells/gemini37-screen-2026-08-28__g37-text-k1-verified-opmax/evaluation.json` | 0.8747 / 0.8747 |
| `gemini37-screen-2026-08-28::g37-text-k3-verified-opmax` | `results/k-ladder-2026-09-12/phase2/cells/gemini37-screen-2026-08-28__g37-text-k3-verified-opmax/evaluation.json` | 0.9135 / 0.9135 |

What each cell's own evaluation records (all three alike; field paths in
`summary`):

| Check | Record | Bearing on criteria 1 and 2 |
|---|---|---|
| `tile_classification.withheld_reason` and `tile_join_withheld.reason` | `tile_join_detection_shortfall` in all three; the join recorded is `id` (`_metadata.cli_args.tile_join`), references by `geometric-contains` | criterion 1: the refusal named is the tile-join refusal |
| every `buffers[].ci_withheld_reason` (14 buffers each) | `tile_join_detection_shortfall` in all 14, `coverage_status` `withheld` | the withheld intervals and coverage are consequences of the same refusal, not separate refusals |
| any other refusal name anywhere in the file | none: a search of each file for `tile_join_*`, `*_shortfall`, and `*refus*` finds only `tile_join_detection_shortfall` and its describer fields | criterion 2: no second refusal recorded |
| `detection_scope` (D50) | rule `origin-sheet-geometric`, applied; origin column `source_tiles`; `n_unattributed` 0, `n_unattributed_in_frame` 0, every `n_origin_*` counter 0, `n_out_of_frame_cross_sheet` 0; `n_out_of_frame` 32 / 27 / 28 (ordinary out-of-frame exclusions, not refusals) | criterion 2: every in-frame detection carries an attributable sheet, so the W1.1 named refusal (`tile_join_unattributed_detection`) is not expected; this is a reading of the committed record, not a test of the new code |
| detection diagnostics under `id` | 526 / 475 / 467 in-frame points, 0 outside the frame's union, 22 / 21 / 20 booked | the shortfall is the name join's, not a frame-coverage loss |
| vocabularies (`tile_join_withheld.vocabularies`) | detections name 333 / 302 / 290 distinct tiles, of which 12 / 11 / 11 are in the frame's 487-name vocabulary; map prefixes are the frame's four sheets | the vocabulary mismatch **is** the cause of the tile-join refusal (the proposer ran on the `ov192` tiling, `scripts/k_ladder_mcb.py:224–227`), not a separate problem; a sheet-specific join books by geometry and reads the sheet from D50's scope, not from tile names |
| inputs | detections, references (`inputs/vectors/references/mounds-reference.geojson`), and bounds (`inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson`) all `clean` in `_metadata.input_git_state`; scorer `8654d741f`, `script_git_status` `dirty` | `dirty` is not specific to these cells: the K = 5 sibling (`results/k-ladder-2026-09-12/phase2/g37-opmax/cells/gemini37-screen-2026-08-28__g37-text-k5-verified-opmax/evaluation.json`, scored at `64382beea`) records the same; it is not a refusal |
| frame | the register names `era2-b-487`, `inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson`, 487 tiles, for all three (`results/run-conditions.json`, each condition's `scope_override`) | the board's own frame; no frame mismatch with the board |

## 3. The table

Families are those in which the committed record lists these cells as
excluded. "Inclusion criteria" cites where the family says who belongs in
it; "exclusion evidence" cites where it records why these cells are out.
Each row's verdict applies the rule's criteria 1 and 2 to that evidence.

### 3.1 Gold-standard (GS) Era-2 verified board, `gs-era2-verified-board-2026-09-10`

The board's four families share one candidate loader,
`scripts/era1_leaderboard_tiering.py` `load_cells` (`:953`). Its only
withholding branch is `:1082–1103`: a cell is withheld **only** if
`is_tile_join_refusal(error)` is true; any other error re-raises and aborts
the board (`:1083–1084`). So no other reason could have produced a
withholding here.

| # | Cell | Family | Inclusion criteria (path:line) | Committed exclusion evidence (path:line) | Verdict |
|---|---|---|---|---|---|
| 1 | K = 1 carried | Board F1 permutation family (BH, the preregistered tiering) | Candidates are the analysis's `conditions_compared` (`results/leaderboard/era2/gs-era2-verified-board-2026-09-10/tiering-input/run-analyses.json:2315`); admitted by the K-ladder route, `…/k-ladder/membership.json:18` (route (a), PI ruling 2026-09-13; `"refused": []` at `:418`); the board's README counts it among 153 admitted (`…/README.md:5`) | `…/tiering_20m.json:10–13, :25` (`n_cells_withheld` 3; `reason` `tile_join_detection_shortfall`); README `:160`, `:164` | **Eligible**, subject to criterion 3 |
| 2 | K = 1 opmax | Board F1 permutation family | `…/tiering-input/run-analyses.json:2316`; `…/k-ladder/membership.json:26` | `…/tiering_20m.json:112, :124`; README `:165` | **Eligible**, subject to criterion 3 |
| 3 | K = 3 opmax | Board F1 permutation family | `…/tiering-input/run-analyses.json:2317`; `…/k-ladder/membership.json:34` | `…/tiering_20m.json:211, :223`; README `:166` | **Eligible**, subject to criterion 3 |
| 4 | K = 1 carried | Board tile-MCC permutation family (reported beside the tiering, S153 ruling 7) | The same candidate set as row 1 (README `:226`: "Cells the tile-join invariant withholds are excluded from this family exactly as they are from the F1 one") | README `:160` ("enter neither BH family"), `:226`; `…/tiering_20m.json:158801–158803` (`n_cells_with_mcc` 150, MCC-arm `withheld` empty: the cells never reached the MCC arm because the F1 arm refused them) | **Eligible**, subject to criterion 3 |
| 5 | K = 1 opmax | Board tile-MCC permutation family | as row 4 | as row 4 | **Eligible**, subject to criterion 3 |
| 6 | K = 3 opmax | Board tile-MCC permutation family | as row 4 | as row 4 | **Eligible**, subject to criterion 3 |
| 7 | K = 1 carried | Board F1 multiple comparisons with the best (MCB) admissible set (`scripts/selection_aware_intervals.py --board`) | `scripts/selection_aware_intervals.py:463–466`: the candidate set is the tiering's, through the same `load_cells`; `…/mcb/gs-era2-verified-board-2026-09-10_b20_m1.json` names `analyses_override` `…/tiering-input/run-analyses.json` | `scripts/selection_aware_intervals.py:470–481` (withheld cells logged and excluded); `…/mcb/gs-era2-verified-board-2026-09-10_b20_m1.json:3` (`n_candidates` 150 of 153 admitted); README `:160` ("neither admissible set") | **Eligible**, subject to criterion 3 |
| 8 | K = 1 opmax | Board F1 MCB admissible set | as row 7 | as row 7 | **Eligible**, subject to criterion 3 |
| 9 | K = 3 opmax | Board F1 MCB admissible set | as row 7 | as row 7 | **Eligible**, subject to criterion 3 |
| 10 | K = 1 carried | Board tile-MCC MCB admissible set | as row 7 | `…/mcb/gs-era2-verified-board-2026-09-10_mcc_b20_m1.json:3` (`n_candidates` 150); `scripts/selection_aware_intervals.py:541–552`; README `:160` | **Eligible**, subject to criterion 3 |
| 11 | K = 1 opmax | Board tile-MCC MCB admissible set | as row 10 | as row 10 | **Eligible**, subject to criterion 3 |
| 12 | K = 3 opmax | Board tile-MCC MCB admissible set | as row 10 | as row 10 | **Eligible**, subject to criterion 3 |

### 3.2 The K-ladder review, the 3.7 GS text ladder (`g384_ov192_g37`, four rungs K = 1, 3, 5, 10)

The three cells are this ladder's K = 1 and K = 3 rungs (its K = 5 and K = 10
rungs score and are tiered on the board). The ladder's own record is
`results/k-ladder-2026-09-12/phase2/ladders.json:7000` (family "Gemini 3.7
text, GS B geometry", `n_rungs` 4).

| # | Cell | Family | Inclusion criteria (path:line) | Committed exclusion evidence (path:line) | Verdict |
|---|---|---|---|---|---|
| 13 | K = 1 carried | K-ladder within-ladder permutation test, Phase 2 (F1 and tile-MCC on one swap stream), as evaluated | A ladder with at least three of {1, 3, 5, 10} (the review's three-rung bar: `results/k-ladder-2026-09-12/findings.md:950–952`; `planning/k-ladder-review-2026-09-11.md:304`, "All thirteen now carry four rungs, and so does the 3.7 gold-standard screen"); 13 of the 14 Phase 2 ladders are tested (`planning/k-ladder-review-2026-09-11.md:300`) | `results/k-ladder-2026-09-12/findings.md:1083–1086` (§ 7.3: "this family is **excluded from the permutation testing**", because the refused tile table would make its MCC meaningless); `scripts/k_ladder_mcb.py:66–77` ("they enter no permutation family and no admissible set") | **Eligible**, subject to criterion 3; see note A |
| 14 | K = 1 opmax | K-ladder Phase 2 permutation test | as row 13 | as row 13 | **Eligible**, subject to criterion 3; note A |
| 15 | K = 3 opmax | K-ladder Phase 2 permutation test | as row 13 | as row 13 | **Eligible**, subject to criterion 3; note A |
| 16 | K = 1 carried | K-ladder MCB admissible sets (F1 and tile-MCC), as evaluated (`results/k-ladder-2026-09-12/mcb/`) | The three-rung bar (as row 13); `scripts/k_ladder_mcb.py:147–151` (the as-evaluated MCB deliberately includes the ladders reported on the D51 clipped basis) | `results/k-ladder-2026-09-12/mcb/summary.json:76–93` (`withheld`: the three cells; `why`: the tile-join invariant, which leaves "two sound rungs of four — below the review's three-rung bar"; `lifted_by`: "the corpus-wide tile-join decision"); the same record as code at `scripts/k_ladder_mcb.py:212–240`; `results/k-ladder-2026-09-12/findings.md:913–922` | **Eligible**, subject to criterion 3; with all four rungs scoreable the ladder meets the three-rung bar. Note A |
| 17 | K = 1 opmax | K-ladder MCB admissible sets, as evaluated | as row 16 | as row 16 | **Eligible**, subject to criterion 3; note A |
| 18 | K = 3 opmax | K-ladder MCB admissible sets, as evaluated | as row 16 | as row 16 | **Eligible**, subject to criterion 3; note A |
| 19 | K = 1 carried (its D51-clipped counterpart) | K-ladder tile-MCC and MCB on D51's clipped basis (`results/k-ladder-2026-09-12/clipped-mcc-2026-10-30/`) — the reported basis for this ladder (D67 (5)) | Every ladder "whose tile-MCC the clipped tables withheld" (`results/k-ladder-2026-09-12/clipped-mcc-2026-10-30/summary.md:8–11`); the D51 area gate selected the 3.7 ladder as clipping (`reports/s166-agent-records/clipped-tile-mcc.md:88–89`, `:102`: common area 1,364.4713 km², excess 37.9354 km²) | `reports/s166-agent-records/clipped-tile-mcc.md:330–331` ("gated but not rebuilt: the tile-join invariant still withholds its K = 1 and K = 3 tile-MCC") | **Eligible**, subject to criterion 3, applied to the **clipped** detections (the clipped cell has never been scored for tile outcomes: `results/k-ladder-2026-09-12/phase2/ladders.json` K = 1 rung `opmax.withheld`, "not regenerated on the clipped detections") |
| 20 | K = 1 opmax (clipped counterpart) | K-ladder D51-clipped tile-MCC and MCB | as row 19 | as row 19 | **Eligible**, subject to criterion 3 on the clipped detections |
| 21 | K = 3 opmax (clipped counterpart) | K-ladder D51-clipped tile-MCC and MCB | as row 19 | as row 19 | **Eligible**, subject to criterion 3 on the clipped detections |

**Note A — the D51 assessed-area difference was checked, and does not stand
as an exclusion in rows 13–18.** The ladder's K = 1 and K = 3 pools searched
the whole board frame, its K = 5 and K = 10 pools only grid-common, a
difference of 37.9354 km² (`results/k-ladder-2026-09-12/phase2/ladders.json:7639–7687`;
D51; D67 (5) reports this ladder on the clipped basis). That is an area
difference *between rungs*, which D51 resolves by clipping (rows 19–21). It
is not a problem with any one cell's scoring on the frame, and the
as-evaluated families include ladders with the same difference: tier E
(identical 37.9354 km² excess, `reports/s166-agent-records/clipped-tile-mcc.md:103`)
is a member of the as-evaluated K-ladder MCB (`results/k-ladder-2026-09-12/mcb/summary.json`,
ladder `tier-e`), and `scripts/k_ladder_mcb.py:147–151` states that the
as-evaluated MCB keeps the D51-clipped ladders on purpose. **This is the one
judgement in this table**; it is flagged for the main session. If it is ruled
the other way, rows 13–18 become "not eligible on the as-evaluated basis",
rows 19–21 are unchanged, and no row becomes unresolved.

### 3.3 Null-exemplar sensitivity, reduced frame (`results/null-exemplar-sensitivity-2026-09-13/`)

| # | Cell | Family | Inclusion criteria (path:line) | Committed exclusion evidence (path:line) | Verdict |
|---|---|---|---|---|---|
| 22 | K = 1 carried | Reduced-frame F1 and tile-MCC tiering (a sensitivity analysis beside the board, not the board) | The board's candidate set on the frame without the 20 exposed tiles (`results/leaderboard/era2/gs-era2-verified-board-2026-09-10/README.md:176–180`); the cell is not exposed (`results/null-exemplar-sensitivity-2026-09-13/analysis.json:1126`, `"exposed": false`) | `results/null-exemplar-sensitivity-2026-09-13/tiering-reduced/tiering_20m.json:10–13, :25` (`reason` `tile_join_detection_shortfall`) | **Eligible**, subject to criterion 3 |
| 23 | K = 1 opmax | Reduced-frame tiering | as row 22 (`analysis.json:1138`) | `…/tiering-reduced/tiering_20m.json:112, :124` | **Eligible**, subject to criterion 3 |
| 24 | K = 3 opmax | Reduced-frame tiering | as row 22 (`analysis.json:1150`) | `…/tiering-reduced/tiering_20m.json:211, :223` | **Eligible**, subject to criterion 3 |

The sensitivity analysis read the cells' pre-D50 evaluations (its per-cell
`f1_before` 0.8338, 0.8495, 0.886 at `analysis.json:1125–1158`, against
the current 0.8616, 0.8747, 0.9135). That staleness is a property of the
sensitivity artefact as a whole, not an exclusion of these cells, and is
left to Wave 3.

## 4. Considered and not entered as families

| Artefact | Why it is not a row |
|---|---|
| K-ladder Phase 2 F1 ladder tables (`results/k-ladder-2026-09-12/phase2/ladder-tables.md:178–231`) | The cells are **not excluded**: the F1 ladder is reported in full (`findings.md:1086`). Its tile-MCC column is withheld at every rung of this ladder under D67 (5) (clipped basis), which row 19's family supersedes |
| S166 historical tile-join comparisons: `results/tile-join-audit/era2-board-mcc-tiering-2026-10-30/` (the three cells' disclosure-only readings at `README.md:89–95`) and `results/k-ladder-2026-09-12/mcc-join-2026-10-30/*/mcb/summary.json` (the same `withheld` block) | Frame-wide comparison readings, historical under D73 (2), not families; their exclusion record is the same tile-join refusal. Whether Wave 3 relabels them is outside W1.4 |
| Uplift supplement (`results/uplift-supplement/build-report.md:26–37`) | Excludes every board-frame condition by its own rule (PI rule 2026-09-10), not for the join; the cells do not otherwise qualify |
| Working-precision plateau characterisation (`results/working-precision/gs-plateau-characterisation.json:7855–7905`) | The cells are present (F1-only analysis); not excluded |

## 5. Outcome

- **24 rows; 24 eligible subject to criterion 3; 0 not eligible; 0
  unresolved.** No row stops the wave (spec § 5).
- Criterion 1 holds for every row: every family's committed exclusion
  record names the tile-join refusal (`tile_join_detection_shortfall`) and
  nothing else, and the board's loader cannot withhold for any other reason.
- Criterion 2 holds for every row on the committed records of § 2; the D51
  area difference is recorded and judged in note A.
- Criterion 3 is open for every row until the W1.5 smoke run, where each
  cell's legacy replay must end in its recorded refusal and the cell must
  then score under the new defaults. For rows 19–21 the cell scored must be
  the D51-clipped counterpart, which W1.5's smoke cells do not include; Wave
  3 owes that score before the clipped family is recomputed.

## Changelog

### 2026-11-18 — Original publication

Written by the Wave 1 census agent (W1.0) before the cells'
sheet-specific scores exist. Their frame-wide geometric tile-MCC has been
on record since 2026-09-12 (`reports/tile-mcc-geometric-join-2026-09-12.md:247–249`);
no score is an input to any verdict. 24 rows over three cells and eight
families; all eligible subject to criterion 3; one flagged judgement (note
A, the D51 area difference in the as-evaluated K-ladder families).
