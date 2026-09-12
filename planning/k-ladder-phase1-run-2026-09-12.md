# K-ladder Phase 1 run card — $0, no API calls (2026-09-12)

> **Last revised**: 2026-09-12 (original publication, written before any
> step ran). Controlling card: `planning/k-ladder-review-2026-09-11.md`
> (§ 4 rulings R1–R5, § 5 the B3 ruling). See [§ Changelog](#changelog).

**Scope.** Phase 1 of the K-ladder review: everything that costs US$0 in
API calls. **No API call of any kind is made.** Any step that would need
one stops there, is recorded in the Phase 2 costing table
(`reports/k-ladder-phase2-costing-2026-09-12.md`), and the remaining steps
continue. All scoring, permutation, bootstrap, tiering and consensus
building runs on **sapphire**; nothing compute-intensive runs locally.

**Branch**: `worktree-agent-a51feb87262e915a2`, pushed to `origin` only so
sapphire can fetch it. Never merged or pushed to `main`. No PI signature
field (`manually_verified_at`, `_signature_note`, `gates.G1.pi_ruling`) is
altered anywhere.

## 1. Dependency order

```text
Step 0  card (this file)                       — no dependencies
Step 1  inventory                              — needs Step 0
Step 2  27 first-N twins (B3)                  — needs Step 1 (§ 3 pointers only)
Step 3  September pair registered (B2/R4)      — needs Step 1
Step 4  K = 1 admitted, board re-tiered (R3)   — needs Step 3 (the new cell joins)
Step 5  K ladders                              — needs Steps 1, 3, 4 (board instrument)
Step 6  Phase 2 costing                        — needs Step 1 (the gap list)
Step 7  deltas report + tests                  — needs whatever landed
```

Steps 2 and 3 are independent of each other and of Step 4's compute.
Step 6 can be written from Step 1 alone, so it survives a stop in 2/4/5.

## 2. Artefacts and finished states

| Step | Artefacts | "Done" means |
|---|---|---|
| 0 | `planning/k-ladder-phase1-run-2026-09-12.md` | this file, committed |
| 1 | `results/k-ladder-2026-09-12/inventory.md` + `.json` | one table per family; every K ∈ {1,3,5,10} cell either named with its condition id or marked a gap; every gap classed `fillable-at-$0` or `needs-verifier-pass`, with the evidence for a `$0` classification recorded per gap (which existing `probabilities.json`, and the candidate-position match that proves coverage) |
| 2 | `scripts/materialise_first_n_ladder_twin.py`; `results/uplift-supplement/verifier-pairing/<slug>/twin*.geojson` + `evaluation.json` per rung; regenerated `verifier-pairing-worklist.csv`, `verifier-uplift.csv`, `verifier-uplift-mcc.csv`; a `notation-key.md` § 7 entry | each of the 9 distinct rungs materialised, its feature count equal to the final-board sweep CSV's `prob_t = 0.0` row at that rung's `min_votes`; the worklist shows `blocked` 0 and F1 pairs computed 172 of 172 |
| 3 | a new condition row `pv-diag-384::pv-high-text-t0.0-n3-recovery-2026-09-08-opmax` in `results/run-conditions.json`; regenerated `results/conditions-manifest.json`/`.md`; a `notation-key.md` § 7 entry for the `-recovery-<date>` suffix | the row exists with provenance at stage `verified-v1-n3-recovery-2026-09-08`, its `eval_path` is the committed current-vintage Era-2 evaluation, its `_note` says the April cell remains the archived board's cell, and `generate_post_run_report.py --all` drift check is clean |
| 4 | edited `scripts/build_gs_era2_board.py` (+ the opmax builder's K gate); rebuilt `membership.json`/`.txt`; new `cells/`, `g2/` evaluations; `tiering_20m.json`, `mcb/`, `gates.json`, `provenance.json`, `README.md` | the board's cell count rises by the admitted cells, every gate G2/G3/G4/G6 passes, the README carries a before→after changelog entry, and `provenance.json` carries a `re_sign_pending` note. Signature fields untouched |
| 5 | `results/k-ladder-2026-09-12/findings.md`, `figures/*.png`, one UNSIGNED analysis row `k-ladder-2026-09-12` | every family with ≥ 3 rungs has a ladder table at both operating points with cost per rung and a 55-map projection; `generate_hypothesis_outcome_table.py --check` is clean |
| 6 | `reports/k-ladder-phase2-costing-2026-09-12.md` | every rung lacking a verifier output is listed with its union size and USD at the audited per-candidate rate; a total against the US$50 ceiling; a recommended order |
| 7 | `reports/k-ladder-phase1-deltas-2026-09-12.md`; `tests/` additions | every number in every document written this job has a file:line / register-id / JSON-key anchor; `python -m pytest -m tier1 -q` run and reported |

## 3. Stop states — halt the step, commit what is sound, report

1. **A ladder family whose rungs do not share fixed parameters.** If two
   rungs of a nominal ladder differ in anything but K (verifier model,
   thinking level, temperature, instruction file, geometry, reference,
   frame), the family is not a ladder: it is recorded in the inventory as
   `not-a-ladder` with the differing field named, and it is **not** scored
   in Step 5.
2. **A materialised twin whose feature count disagrees with its rung's
   `n_detections` at `prob_t = 0.0` in the final-board sweep CSVs.** That
   rung is not registered, not scored, and not counted towards the 172;
   the mismatch (expected vs got) is reported. Other rungs continue.
3. **A board re-tier that changes Tier 1.** The step is finished and
   committed, and the change is flagged at the top of the final report.
   Tier 1 is the MCB admissible set's greedy clique (E83) and its five
   3.7/3.8 members are a signed result; a change there is a PI matter.
4. **A test failure I did not cause.** `tests/test_per_arch_md_ownership.py`
   is a known environment-only failure fixed on `main`; it is reported and
   ignored. Any other new failure stops the commit that caused it.
5. **A step that needs an API call.** Stop the step; record the call, its
   union size and its audited cost in the Step 6 table; continue.
6. **A verifier `probabilities.json` that cannot be shown to cover a
   sub-pool's candidates by candidate-position matching.** The gap is
   reclassified `needs-verifier-pass` and moves to Phase 2. Coverage is
   never assumed from counts alone.
7. **Sapphire unreachable.** Stop every compute step; the documentation
   steps (0, 1 where it is register reads, 6, 7) continue, and the report
   says which numbers are missing and why. No bootstrap or permutation
   runs locally.

## 4. Partial-completion semantics

Every step is independently committable, and the commit is made as soon as
the step's artefacts reach their finished state — before the next step
starts. A step that stops leaves its predecessors committed and intact.
`planning/k-ladder-review-2026-09-11.md` is updated at the end with a
per-step landed / stopped line, and the same table is the spine of the
final report. Nothing in this job depends on a later step having run, with
one exception recorded in § 1: Step 4's board includes the Step 3 cell, so
a stop in Step 3 means the board is rebuilt without it and says so.

## 5. Verification at each step

- **Step 1** — every condition id quoted is re-read from
  `results/conditions-manifest.json` in the same session; the K counts are
  recomputed, not carried from the controlling card.
- **Step 2** — the count gate of § 3.2 per rung; the twin's CRS is
  declared (EPSG:32635) and every kept feature carries a non-empty
  `source_tile` (the existing `materialise_pairing_twin.py` gates,
  reproduced); the regenerated worklist's `blocked` count is read from the
  file, not predicted.
- **Step 3** — the registered `n_detections` equals the committed
  current-vintage GeoJSON's feature count (the
  `feedback_feature_count_crosscheck` rule); the drift check after
  `generate_post_run_report.py --all` is clean.
- **Step 4** — gates G2 (committed F1 reproduces to 1e-6 and the feature
  count matches), G3 (every cell's evaluation names the board frame), G4
  (cell count equals membership), G6 (frame-delta table); MCB recomputed
  LAST on the final membership (the PI's rule).
- **Step 5** — each rung's board-frame F1 is read back from its own
  `evaluation.json`; the hypothesis-outcome table's `--check` is clean.
- **Step 6** — every rate is re-read from
  `reports/billing-reconciliation-2026-09-11.md` § 3 /
  `reports/r7-gaps-deltas-2026-09-11.md` § 2.3 in the same session.
- **Step 7** — `python -m pytest -m tier1 -q`.

## 6. Two interpretation notes, recorded because they are choices

1. **Admitting K = 1 needs two rules relaxed, not one.**
   `scripts/build_gs_era2_board.py` excludes K = 1 twice: once by run and
   label (`SINGLE_PASS_PV_RUN`, `"baseline"`) and once by the generic
   `k is None or k < 5` gate. Removing only the first leaves all 20 cells
   excluded by the second, so R3 ("the board takes every verified cell on
   its frame regardless of K") requires the `MIN_K`-style gate to drop to
   1 in both this builder and `scripts/build_gs_era2_board_opmax.py`
   (`MIN_K`), which is what admits the three off-board `-opmax` K = 3
   cells and the Step 3 cell. Recorded as an interpretation of R3, not a
   silent change.
2. **"Best available per configuration" applies to the board, not the
   register.** Step 3 registers the September cell and leaves the April
   `pv-diag-384::pv-high-text-t0.0-n3-opmax` row registered and unchanged.
   Where both would otherwise sit on the board for one configuration, the
   September cell is the representative and the board's changelog says so.

## Changelog

### 2026-09-12 — Original publication

Written before any step of the Phase-1 run, as the job's Step 0. Sources
read for it this session: `planning/k-ladder-review-2026-09-11.md` in
full; `planning/uplift-supplement-2026-08-28.md` (banner and "The 27 that
stay blocked"); `results/uplift-supplement/verifier-pairing-worklist.csv`
(status counts and the 27 blocked rows); `scripts/stride55_ladder.py`;
`scripts/materialise_pairing_twin.py`;
`scripts/build_gs_era2_board.py`; the Era-2 board's `README.md`,
`membership.txt`, `provenance.json`, `tiering_20m.json` and
`score-commands.sh`; `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/opmax/staleness-2026-09-11/README.md`;
`reports/r7-gaps-deltas-2026-09-11.md` §§ 2 and 5; `tests/README.md`.
No compute, no API, no register change.
