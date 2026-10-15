# S164 restatement pass: document sweep for stale moved values

Read-only audit, 2026-10-16, Claude (Opus, sub-agent of lead 2), over
`~/scratch/s164-restate-2026-10-15/wt` at NEW = `0fc2d6389` against
BASE = `718d0ee08`. No file in the worktree was written; no model
Application Programming Interface (API) calls were made.

Abbreviations: GS = Gold Standard (the 487-tile evaluation corpus); MCC =
Matthews correlation coefficient (tile level); MCB = multiple comparisons
with the best; BH = Benjamini–Hochberg; MDE = minimum detectable effect.

## Method

1. **Moved values.** Diffed every changed JSON/CSV under `results/`
   (902 files, 123,435 moved numeric leaves; `moved.tsv`), then built a
   curated headline list (`head.tsv`, 86 strings) from (i) the 32 GS
   conditions whose 20 m F1/CI/MCC/precision/recall/count moved in
   `results/conditions-manifest.json`, keyed by `condition_id`
   (`cond-moved.tsv`), and (ii) the before/after tables in the newest
   changelog entry of each restated document (grid, stride, image-B,
   3.7 image GS, e45, selection-aware, sensitivity-MDE, Era-2 board,
   diversity dividend, family FDR, factor analysis, leaderboard-20m), plus
   the 55-map extended-reference cells (`TRACK2-SUMMARY.md`) and the
   regenerated screen analyses (`gemini37-screen-2026-08-28/**/analysis.json`,
   `gemini38-screen-2026-09-04/armV/{analysis,pair_test}.json`).
2. **Search.** Every tracked `results/**.md`, `reports/**.md`,
   `planning/*.md` and `README.md` at NEW (3,396 documents), excluding the
   eleven documents of `d6e2f40e8`, the Era-2 board README, every `results/`
   Markdown file changed BASE → NEW, the modality-bridge and K-ladder
   findings, `reports/s16*-agent-records/**` and `archive/**`. Exact 4-dp
   strings (and 6-dp for e45/MDE), a 3-dp pass restricted to lines with GS
   context, and a label detector (moved cell label plus one of its old
   values on one line). 233 documents hit; each hit in a document last
   committed on or after 2026-08-18 was read in context. Hits in documents
   older than the moved family, or in rows naming other cells, were
   discarded as coincidences (for example `0.8333`, `0.7500`, the 55-map
   K-ladder tables, the h11 threshold sweeps).

## (a) Documents that present a moved number as a current finding and are not yet restated

| Document | Line(s) | Stale text | New value | Source |
|---|---|---|---|---|
| `results/null-exemplar-sensitivity-2026-09-13/findings.md` (rendered; last revised 2026-10-05) | 227, 228–229, 232, 233, 235, 237 | full-frame column: 7961 pairs significant; 14 tiers, tie set 5; F1 MCB 65; tile-MCC pairs 2982; MCC tie set 33; MCC MCB 59 | 8,075; 14, 5; **52**; 3,001; 34; 60 | Era-2 board README changelog 2026-10-15 |
| same | 19, 24, 29–31, 129, 136, 166–168, 183, 241–248, 313 | every reduced-frame figure (FP-rate ratio 0.561 vs 0.685; max move 0.0074 F1 / 0.0120 MCC; Tier 1 five → four, demoted cell 0.9002, rank 5 0.9013; 7961 → 7905; 2982 → 3118; 33 → 28) | not derivable by editing: the analysis scored the pre-pass board cells | re-run `scripts/analyse_null_exemplar_sensitivity.py` (it renders `findings.md`, `analysis.json`, `tiering-reduced/tiering_20m.md`) |
| `results/null-exemplar-sensitivity-2026-09-13/tiering-reduced/tiering_20m.md` (generated) | whole file (104 moved cell values, e.g. Tier 1 list, line 8 "11175 (7905 significant) -> 13 tiers") | per-cell F1/MCC of the pre-pass Era-2 cells | regenerate with the re-run above | — |
| `results/student-baseline-2026-09-01/per-student-gs4/findings.md` (last revised 2026-09-01) | 31–32 | "0.9190 vs 0.9265 @20 swap; 0.9066 vs 0.9139 screen" | 0.9289 vs 0.9364; 0.9165 vs 0.9238 | Era-2 board cells (below); `conditions-manifest.json` |
| same | 42 | all-3.7 model @ 20 m P 0.9254 / R 0.9126 / F1 0.9190 | 0.9268 / 0.9310 / 0.9289 | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/cells/gemini37-screen-2026-08-28__g37-text-k5-verified-swap37-p0_80-k5/evaluation.json` (the footprint basis equals the board frame exactly at BASE) |
| same | 43 | 3.7 text screen model @ 20 m 0.8984 / 0.9149 / 0.9066 | 0.9002 / 0.9333 / 0.9165 | `…/cells/gemini37-screen-2026-08-28__g37-text-k5-verified-carried-p0_10-k5/evaluation.json` |
| same | 51, 52 | @ 50 m: all-3.7 0.9394 / 0.9264 / 0.9329; screen 0.9120 / 0.9287 / 0.9203 | 0.9405 / 0.9448 / 0.9427; 0.9135 / 0.9471 / 0.9300 | same two files |
| same | 54–60, 67–92 | per-zone model F1 and the `significance.json` tests (model vs students) | re-score needed; the rankings hold (model leads at 20 m, students at 50 m, 0.9753 > 0.9427) | re-run the per-student GS-4 scorer on the restated cells |
| `results/working-precision/gs-plateau-characterisation.md` (generated from `results/conditions-manifest.json`; last regenerated 2026-09-14) | 113 (and header aggregates, 4–12) | `g37-text-k1-verified-opmax` F1@20 0.8495 (onset, F1@onset, drift derived from the pre-pass row) | F1@20 0.8747; other columns by regeneration | `scripts/characterise_gs_plateau.py` against the NEW manifest |
| `results/k-ladder-2026-09-12/inventory.md` (hand-written; last revised 2026-09-12) | 74–77 | stride `g384_ov128` ladder K = 1/3/5/10: F1@20 0.8677 / 0.8911 / 0.8856 / 0.8982; tile-MCC 0.7894 / 0.7814 / 0.7805 / 0.8022; n 411 / 380 / 394 / 387 | 0.8737 / 0.8993 / 0.8937 / 0.9075; 0.8010 / 0.7927 / 0.7918 / 0.8134; 419 / 386 / 400 / 394 | `conditions-manifest.json`; matches the regenerated `inventory-tables.md` (may fall to the K-ladder lane) |
| `results/gemini3-image-55map-2026-09-16/findings.md` § 6 (last revised 2026-09-21) | 300, 301 | row A GS F1 @ 20 m, K = 5 arm 1 0.9254 (gap 0.0823); arm 2 0.9308 (gap 0.0757) | arm 1 at its registered (0.10, k5) 0.9353 (gap 0.0922; best point 0.9381); arm 2 0.9408 (gap 0.0857) | `conditions-manifest.json`; `results/gemini37-image-gs-2026-09-01/findings.md` changelog |
| `results/paper-tables/leaderboard_tiers_20m.md` (paper table, 2026-08-02) | rows #6, #9, #11–#14, #17–#26 (e.g. 62 "#9 FH text 26/30 0.814"; 69 "#11 0.797"; 70 "#12 0.779") | 3-dp F1 of the sixteen consensus/single-pass rows | +0.002 to +0.003 each (#9 0.816, #11 0.799, #12 0.781, #6 0.843, #23 0.547 …); #9 now above #8 in Tier 3 | its sibling `leaderboard-20m-annotated.md` already carries the D60 (3) "Restated figures" banner and a full changelog; copy the banner |
| `results/paper-tables/leaderboard_tiers.md` (30 m, 2026-08-02) | 53 and the other consensus rows | "FH text 26/30 0.826" | 0.828 (consensus rows +0.002 to +0.003; no proposer–verifier row moves) | `results/pairwise/leaderboard-30m/` (regenerated) |
| `results/paper-tables/pairwise_hypothesis_table.md` (30 m, 2026-08-02) | 27, 50, 95 | 26/30 at 0.826; 29/30 0.669; 9/10 0.811; PV − consensus Δ 0.079 | 0.828 (0.8282); 0.6715; 0.813 (0.8129); Δ 0.076 (0.0785 → 0.0761); N30 − N10 raw p 0.0671 → 0.0668; verdicts unchanged | `results/pairwise/30m/fdr/pairwise_results_fdr.json` |

## (b) Documents left as dated records or deltas reports (for the record's § 9)

These quote moved values as what was measured or planned on their date.

**Reports:** `reports/frames-blast-radius-2026-10-07.md`,
`reports/scorer-frames-d50-d51-2026-10-08.md`,
`reports/k-ladder-frames-2026-10-07.md`,
`reports/k-ladder-phase1-deltas-2026-09-12.md`,
`reports/k-ladder-closeout-deltas-2026-09-12.md`,
`reports/k-ladder-admission-deltas-2026-09-13.md`,
`reports/k-ladder-phase2-deltas-2026-09-12.md`,
`reports/modality-rulings-deltas-2026-09-14.md`,
`reports/results-rulings-deltas-2026-09-12.md`,
`reports/r7-gaps-deltas-2026-09-11.md`,
`reports/era2-board-mcc-family-2026-09-13.md`,
`reports/recovery-drop-fix-2026-09-13.md`,
`reports/tile-mcc-geometric-join-2026-09-12.md`,
`reports/google-temperature-notice-2026-10-07.md`,
`reports/w27-replicate-floors-2026-10-06.md` (and
`-scripts/claims-inventory-2026-10-06.md`, `-scripts/floors-v2/results/tables.md`),
`reports/d51-ladder-provenance-2026-10-08.md` (and `-scripts/out/summary.md`),
`reports/d42-implementation-2026-10-05.md`, `reports/input-drift-2026-10-07.md`,
`reports/stale-register-notes-2026-10-07.md`,
`reports/r2-chain-pre-run-audit-2026-09-06.md`,
`reports/gemini37-image-55map-costing-2026-09-10.md`,
`reports/scoring-sensitivity-review-2026-08-18.md`,
`reports/dedup-correction-worklist-2026-08-18.md`,
`reports/recovery-consistency-audit-2026-09-08.md`,
`reports/defect-register-2026-08-18.md`, `reports/bca-axis-defect-2026-08-18.md`,
`reports/verification/family-fdr-registration.md`.

**Results-side dated records:** `results/tile-join-audit/board-era2-2026-09-12.md`,
`results/tile-join-audit/k-ladder-phase2-2026-09-12.md`,
`results/tile-join-audit/k-ladder-phase2-cells-2026-09-12.md`,
`results/k-ladder-2026-09-12/recovery-fix-2026-09-13/README.md`,
`results/k-ladder-2026-09-12/tier-e/pre_launch_audit.md`,
`results/modality-track-audit-2026-09-14/recomputation.md` and
`recomputed/**/gs-plateau-characterisation.md`,
`results/dedup-metric-impact-2026-08-18/findings.md` (line 90: the
diversity-dividend Tier 1 at 0.8141 as of 2026-08-18).

**Planning cards (dated, closed or superseded; not in the revision-policy
scope):** `planning/gs-era2-verified-board-2026-09-08.md` (cell table
148–155, top cell 0.9233 at 602), `planning/gemini37-screen-2026-08-28.md`,
`planning/gemini38-screen-2026-09-04.md`,
`planning/gemini37-image-gs-2026-08-30.md`, `planning/image-b-gs-2026-08-28.md`,
`planning/stride-programme-2026-08-24.md` (65: "+0.0339, p = 0.015" against
min6, a claim that now fails), `planning/recall-levers-programme-2026-08-19.md`,
`planning/gemini37-register-rows-proposal-2026-09-03.md`,
`planning/gemini37-55map-2026-08-29.md`, `planning/gemini37-image-55map-2026-09-13.md`
(49–50: 0.9233 / 0.9190 as Tier 1 and "the paper's F1 headline"),
`planning/reference-revision-2026-09-06.md`, `planning/k-ladder-review-2026-09-11.md`,
`planning/documentation-foundation-checklist-2026-09-13.md`,
`planning/s135-analysis-block-2026-08-17.md`, and
`planning/paper-writeup-continuity.md` (dated session blocks; the one open
item, line 538, quotes 0.9265 as the 3.7 text headline, now 0.9364).

## (c) Quoted historically or as an as-run gate value (correct as written)

- Anchor gates that read legs as run (`GATE_POLICY = "fixed"`):
  `planning/modality-bridge-2026-10-07-stage2.md` 404–412,
  `planning/modality-bridge-2026-10-07.md` 625–626,
  `planning/d57-4-rescore-plan-2026-10-09.md` 256,
  `results/gemini3-image-55map-2026-09-16/findings.md` 291,
  `results/k-ladder-2026-09-12/tier-e/pre_launch_audit.md` 40.
- `results/analyses-manifest.md` (changed BASE → NEW, so outside the search,
  but checked): the outcome text of the ten rows `ed91d2df8` lapsed
  (grid-postverifier, gemini37-screen, gemini38-screen-armv,
  gemini37-image-gs, image-b-modality, e45 …) still quotes 0.9139, 0.9265,
  0.0549, 0.0304, 0.1697, 0.2076, 0.0969 by design: re-sign-pending, with
  redrafts going to the PI.
- `planning/pi-decisions-2026-09-20.md` (decision log) and
  `planning/wording-changes-register.md` (row F1 cites
  `results/k-ladder-2026-09-12/findings.md:602` "0.8495 → 0.9068"; its
  pointer and wording need updating once the K-ladder lane lands).

## Notes

1. **The two screens have no restated narrative home.** The pass
   regenerated `gemini37-screen-2026-08-28/{,k10/,swap37/}analysis.json` and
   `gemini38-screen-2026-09-04/armV/{analysis,pair_test}.json`, but their
   findings live only in the closed planning cards and the lapsed register
   rows. Moved tests: all-3.7 swap vs the G3 anchor +0.0304, p 0.0105 →
   +0.0347, p 0.0065; K = 5 carried vs anchor +0.0178, p 0.1697 → +0.0221,
   p 0.0971; K = 10 vs anchor p 0.2076 → 0.1231; N5 − N10 p 0.7928 →
   0.7921; 3.7 ladder N = 1/3/5/10 0.8588 / 0.9018 / 0.9131 / 0.9142 →
   0.8652 / 0.9118 / 0.9231 / 0.9243; Arm V vs anchor p 0.0106 → 0.0055;
   Arm V vs carried-G3 +0.0119, p 0.0969 → +0.0120, p 0.0764; Arm V vs all-3.7
   −0.0007 → −0.0006 (p unchanged); Arm V ladder 0.8874 / 0.9173 / 0.9258 →
   0.8973 / 0.9273 / 0.9358. Every verdict holds. A PI call: card revision
   notes, or leave them to the register redrafts.
2. **The 55-map extended-reference seam.** D67 (6) moved the eight
   extended-reference cells by +8e-05 to +9e-05 at 50 m, flipping the fourth
   decimal on six (0.8476 → 0.8477, 0.8359 → 0.8360, 0.8152 → 0.8153,
   0.8127 → 0.8128, 0.7987 → 0.7988, 0.7831 → 0.7832). The registered
   canonical-GT conditions were not regenerated, so
   `results/55map-leaderboard/55map-leaderboard-50m.md`,
   `results/55map-leaderboard/gs-vs-55map-transfer.md`,
   `results/stride55-2026-08-27/findings.md`,
   `results/gtfree-selection/gtfree-selection-findings.md`,
   `results/metric-leaderboards/55map-canonical-50m.md` and
   `reports/key-findings-summary-2026-06-23.md` agree with their sources but
   disagree with `TRACK2-SUMMARY.md` in the fourth decimal. Not stale under
   § 1.1 item 5; whether D67 (6) propagates is a PI decision.
3. **Pre-D50 champion values in unregenerated Phase 3 renders.** 0.8141
   (FH text 26-of-30, now 0.8165 in `diversity-dividend-384`), 0.6803 and
   0.6611 remain in `results/paper-eval/*/consensus-analysis-summary.md`,
   `results/retest/**`, `results/secondary-effects-token-efficiency/report.md`
   and `results/e43-matched-temperature/findings.md`. Their own artefacts did
   not move, and the E72/e43 board is held for the PI (§ 1.5), so they are
   listed here rather than under (a).
4. **Collisions make find-and-replace unsafe.** 0.0761 is the old 20 m H2
   ΔF1 and the new 30 m H2 Δ; 0.8842 is the old 13-cell opmax and the new
   min11; 0.8860 is the old 3.7 K = 3 and the old stride 384/62.5; 0.8677 is
   both grid 384/12.5 and stride ladder N = 1; 0.9233 is also the old
   precision of the 3.7 image carried cell.
5. **Possibly affected but not checked:** the GS calibration legs
   `results/gemini37-image-55map-2026-09-13/gs-calibration/` and
   `results/gemini3-image-55map-2026-09-16/gs-calibration/` (K = 3 GS F1
   0.9197 / 0.9245; row B 0.8200 / 0.8408 / 0.8431 / 0.8551) verify GS pools
   whose registered siblings the pass re-verified. If they read the same
   wrong-sheet crops, § 6 of the Gemini 3 image findings moves beyond the
   two K = 5 rows in (a).
6. `results/hypothesis-outcome-table/hypothesis-outcome-table.md` is
   generated from `results/analyses-manifest.json`, which changed (status and
   signature fields only). It probably does not move; its generator's check
   mode would confirm.
7. **Verdict flips the pass made** (the grid's 384 px overlap effect now
   fails, p 0.0541; the grid winner against min6 fails, p 0.111; I3 fails on
   the carried arm; the Era-2 F1 MCB set 65 → 52; opmax leads at 30 m). The
   sweep found these old verdicts only in restated documents, dated records,
   the lapsed register rows and the stride programme card.

Working files: `moved.tsv`, `cond-moved.tsv`, `head.tsv`, `hits4.tsv`,
`label-hits.tsv`, and the scripts `moved.py`, `cond.py`, `scan4.py`,
`labels.py`, `scan3dp.py`, `ctx.sh`, all in this directory.
