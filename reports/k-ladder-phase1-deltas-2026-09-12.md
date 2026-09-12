# K-ladder Phase 1: claims with anchors, and what did not change

> **Last revised**: 2026-09-12 (original publication — step 7 of the K-ladder
> Phase-1 run, `planning/k-ladder-phase1-run-2026-09-12.md`). Controlling card:
> `planning/k-ladder-review-2026-09-11.md` § 6. See [§ Changelog](#changelog).

Layout follows `reports/r7-gaps-deltas-2026-09-11.md`: every number this run put
in a document, the file / key / line it was read from, and — as its own section —
what did NOT move. **Zero API calls.** Every scoring, permutation, bootstrap,
clustering and tiering step ran on sapphire (`ssh sapphire`,
`~/Code/map-reader-llm`, its own `.venv`), never on the local workstation.

## 1. Step 1 — the inventory

| # | Claim | Anchor |
|---|---|---|
| 1.1 | 187 (run, pool, verifier, frame, reference) groups hold at least one verified condition; 24 carry ≥ 2 rungs; 8 carry ≥ 3 of {1, 3, 5, 10} | `results/k-ladder-2026-09-12/inventory.json`, `n_families`, and a recount over `families[].rungs_present` |
| 1.2 | The 96 (family, K) cells of those 24 families classify 61 committed / 30 needs-verifier-pass / 3 zero-usd-inherited / 2 no-passes; **0 zero-usd-exact** | same file, `families[].gaps[].class` |
| 1.3 | The only complete K = 1/3/5/10 ladder on the gold standard is `stride-phaseb-2026-08-25` pool `g384_ov128`, F1@20 0.8677 / 0.8911 / 0.8856 / 0.8982, tile-MCC 0.7894 / 0.7814 / 0.7805 / 0.8022, n 411 / 380 / 394 / 387 | `results/stride-2026-08-25/conditions-verified/{g384_ov128-ladder-n1,-n3,-n5,g384_ov128}/eval/evaluation.json`, `summary.buffers[buffer_metres=20].f1` and `summary.tile_classification.mcc.point` |
| 1.4 | Each of those rungs carries an EXACT re-verification of its own first-N union | each row's `_note` in `results/run-conditions.json`: "Winner-ladder exact rung (first-N passes, exact re-verification…)" |
| 1.5 | R1's verifier is four recorded fields, and `verify_adversarial-text` is a shorthand, not a filename | `prompts/system-instructions/` holds `verify_adversarial.md`, `verify_adversarial_v2.md`, `verify_brief.md`, `verify_checklist.md`, `verify_comparative.md` — and no `verify_adversarial-text.md`; the shorthand appears in the `_note` of every stride-phaseb ladder row |
| 1.6 | A 5-pass sub-pool union is not a positional prefix of the 10-pass union, and most of its centroids are not in the longer union at all: 6 probed pairs, **0 covered**, 82–412 of 1,123–2,954 indices agreeing, 300–1,805 points present anywhere | `results/k-ladder-2026-09-12/subpool-coverage-probe.json`, `probes[]`, tolerance 0.2 m, coordinates reprojected to EPSG:32635 |
| 1.7 | The mechanism is the mean centroid | `scripts/merge_passes.py:289-292`, `mean_centroid = (sum(xs) / len(xs), sum(ys) / len(ys))` in `cluster_across_passes` |
| 1.8 | The controlling card's expectation that the Gemini 3 MINIMAL text family was "complete or nearly so" is wrong: every Gemini 3 `pv-diag-384` family holds exactly K = 5 and K = 10, at each of T 0.3 / 0.7 / 1.0 | `inventory.json`, the twelve `pv-diag-384` families' `rungs_present`; `planning/k-ladder-review-2026-09-11.md` § 3 step 1 for the expectation |
| 1.9 | The card's K = 1 (24) and K = 3 (6) counts were over all 128 `pv-diag-384` conditions, not the verified ones | `results/conditions-manifest.json`; filtered to `aggregation == "verified"` the K = 3 cells are the two T = 0.0 `-opmax` rows plus `n1-outstanding-384::pv-n1-image-t0-n3-opmax` |

**A correction to this report's own instrument.** The coverage probe's first run
compared WGS84 degrees against a metre tolerance — the committed
`consensus_t*.geojson` files carry degrees and no `crs` member, because
`merge_passes.apply_threshold` reprojects 32635 → 4326 before writing, so
"0.01 m" was about 1.1 km of slack. The positional verdict survived it (the
mismatching indices are kilometres apart) but the set-containment figure did not,
and that figure is the one that would have mis-classified up to 30 gaps as US$0
fillable. Fixed at commit `75110d3b1`; the corrected numbers are claim 1.6.

## 2. Step 2 — the 27 first-N twins

| # | Claim | Anchor |
|---|---|---|
| 2.1 | 9 distinct rungs serve the 27 blocked rows, because rows sharing a (pool, N, k) share one twin | `results/uplift-supplement/verifier-pairing-worklist.csv`, the 27 rows of basis `first-n-recluster`, grouped on `proposer_pool`, `N`, `min_votes` |
| 2.2 | Every rung's full-K rebuild reproduced its committed union exactly: 38,713 (A), 57,482 (B), 12,715 (3.7 arms), max centroid drift 0.069 m against the verifier manifests | each twin's `_materialised.gates` in `results/uplift-supplement/verifier-pairing/first-n/*/twin.geojson` (`committed_union_n`, `full_k_rebuild_n`, `full_k_max_centroid_distance_m`) |
| 2.3 | Every shell's feature count equals the rung's recorded pre-verifier count at prob_t = 0.0 — A 18,162 / 16,808 / 12,682 / 13,862; B 24,923 / 16,706 / 14,889; arms 8,372 / 6,261 | `results/55map-final-board-2026-08-27/sweep_{A,B}-N*.csv` and `results/55map-final-board-r2-2026-09-06/sweep_{A,B,ARM1}-N*.csv`, the `prob_t = 0.0` row at each `min_votes`; reproduced in each twin's `_materialised.recorded_count` |
| 2.4 | No rung hit a STOP state | 9 of 9 gate passes in `/tmp/kladder-twins/*.log` on sapphire, each also recorded in its twin's `_materialised` block |
| 2.5 | The worklist's `blocked` count is **0**; 170 rows, 53 `ready`, 104 `ready-after-materialise`, 13 `already-registered` | `results/uplift-supplement/verifier-pairing-worklist.csv`, a recount of `status` |
| 2.6 | Row count 172 → 170, which is not 172 of 172 | three rows left the supplement because step 4 promoted the three K = 3 `-opmax` cells to board members and the supplement excludes board-frame cells by design; one row joined, the September recovery pair. 172 − 3 + 1 = 170 |
| 2.7 | 170 of 170 F1 pairs computed, 0 pending; 169 of 170 on MCC | `results/uplift-supplement/verifier-uplift.csv` and `verifier-uplift-mcc.csv`, generator stdout and a recount |
| 2.8 | The one MCC pending is pre-existing: `retest-phase2b::verified-adv-text-t0.0`, "unverified side has no score" | `verifier-uplift-mcc.csv`, that row's `notes` |
| 2.9 | All 27 new pairs are positive on both metrics: F1 median **+0.4089**, range +0.0667 to +0.5265; MCC median **+0.5620**, range +0.1182 to +0.6576 | both CSVs, the 27 rows whose worklist basis is `first-n-recluster` |
| 2.10 | The largest is +0.5265: `stride-55map-2026-08-25::g384-ov192-55map-n1-verified37-oracle-p0.96-k1-r2-gt`, verified 0.8352 against a twin of 0.3087 | `verifier-uplift.csv`, that row |
| 2.11 | 27 of 27 scorings succeeded | `/tmp/twin-scoring.log` on sapphire, "27 succeeded, 0 failed"; each row's own `evaluation.json` under its `output_dir` |

**Figures for the SIGNED `verifier-uplift-pairing` row's amendment** — recorded
here, NOT applied.

**The baseline is the row as it stands, not as `r7-gaps-deltas` § 5.1 described
it.** That report's table is the 2026-09-10 signature (85 of 172, 86 blocked,
median +0.212). The PI has since AMENDED and re-signed the row:
`results/run-analyses.json`, `manually_verified_at` **`2026-09-11T07:03:41Z`**,
`_signature_note` "Amended and re-signed 2026-09-11T07:03:41Z by the PI (S153
ruling B1 …): counts 85 → 145 computed / 86 → 27 blocked". Using the older
figures as the "before" column would have overstated this session's delta by two
amendments, so the comparison below is against the row's current signed state.

| field | signed value (2026-09-11) | current value |
|---|---|---|
| computed / total, F1 | 145 of 172 | **170 of 170** |
| computed / total, MCC | 144 of 172 | **169 of 170** |
| blocked | 27 | **0** |
| F1 uplift median | +0.201 | **+0.2631** |
| F1 uplift range | −0.0366 to +0.486 (2 negative) | **−0.0366 to +0.5265** (2 negative) |
| MCC uplift median | +0.427 | **+0.4975** (3 negative, min −0.0230, max +0.8410) |
| `conditions_compared` length | 145 | **170** |

The 27 that were blocked are exactly the 27 this session derived, and the signed
outcome names them: "all first-N ladder rungs whose universe was never
committed". The one MCC pair the signed text calls "undefined because its twin's
MCC is undefined" is the pair still pending at § 2.8.

By frame, computed pairs:

| frame | n (F1) | F1 median | n (MCC) | MCC median |
|---|---:|---:|---:|---:|
| `55maps-8541` | 86 | +0.3685 | 86 | +0.5708 |
| `era-2-487` | 51 | +0.1322 | 51 | +0.3221 |
| `grid-common-487` | 21 | +0.1935 | 21 | +0.3348 |
| `era-1-340` | 5 | +0.0366 | 4 | +0.2893 |
| `era-3-327` | 4 | +0.0047 | 4 | +0.0633 |
| `px256-1032` | 3 | +0.3983 | 3 | +0.5921 |

## 3. Step 3 — the September pair

| # | Claim | Anchor |
|---|---|---|
| 3.1 | Registered as `pv-diag-384::pv-high-text-t0.0-n3-recovery-2026-09-08-opmax`, n 423, Era-2-frame F1@20 0.8508, tile-MCC 0.7857 | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/opmax/staleness-2026-09-11/current-vintage/era2-eval/evaluation.json`; the registered row in `results/run-conditions.json` |
| 3.2 | Against the April cell's 403 / 0.8234 / 0.7750 | the same directory's `README.md` comparison table |
| 3.3 | The argmax does not move between vintages: both sweeps put it at (vote_t 3, prob_t 0.15), each reproducing its committed `sweep_2d.json` in all 240 rows | that README, and `…/staleness-2026-09-11/{original,current}-vintage/sweep_2d.json` |
| 3.4 | The verifier stage was already paid for: US$1.82, stage `verified-v1-n3-recovery-2026-09-08`, commit `43516df9a` | the same README; the stage's own directory |
| 3.5 | The April row is registered and unchanged | `results/run-conditions.json`, `pv-high-text-t0.0-n3-opmax`; its `_note` and `detections` are as they were, except the board-admission sentence step 4 added |
| 3.6 | The `-recovery-<date>` suffix is sanctioned notation | `docs/methodology/notation-key.md` § 7.2, new this session |
| 3.7 | `generate_post_run_report.py --all` validates clean: 41 runs + 542 conditions + 1,286 passes + 66 analyses | generator stdout, "ALL VALID"; `scripts/verify_run_conditions.py` exits 0 with 22 pass / 19 partial / 0 fail |

## 4. Step 4 — the board, before → after

| # | Claim | Anchor |
|---|---|---|
| 4.1 | Cells 79 → **103**; `-era2b` 39 → 60; `-opmax` 40 → 43 | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/provenance.json`, `membership` (`n`, `n_era2b`, `n_opmax`); `membership.txt` first line; `opmax/membership.json`, `n_members` |
| 4.2 | Pairs significant 1,845 / 3,081 → **3,651 / 5,253**; tiers 7 → **12** | `provenance.json`, `tiering`; `tiering_20m.json`, `pairwise` |
| 4.3 | **Tier 1 is the same five 3.7/3.8 cells, in the same order, at the same F1**; the tie set is 5 as before | `tiering_20m.json`, `tiers[0].members` and `tie_set`, against `archive/superseded-leaderboards/gs-era2-verified-board-2026-09-10-79cell-pre-k1/tiering_20m.json` |
| 4.4 | The top cell is unchanged: `g37-image-k5-verified-swap37-p0.90-k5` at 0.9233 | `tiering_20m.json`, `ranking[0]` |
| 4.5 | Hsu MCB admissible 28 of 79 (w_upper 0.05011) → **49 of 103 (w_upper 0.0736)**; two-sided band 40 → 55 | `/tmp/mcb.log` on sapphire and `mcb/gs-era2-verified-board-2026-09-10_b20_m1.json`; the before values from the archived `provenance.json` |
| 4.6 | Gates all pass: main G2 0 / G3 0 / G4 60 of 60; opmax G2 0 / G3 0 / G4 43 of 43; G6 max abs delta 0.0078, unchanged | `gates.json`, `opmax/gates.json`, `frame-deltas.md` |
| 4.7 | The 24 cells that joined: 20 single-pass PV, 3 K = 3 archived sweep optima promoted from off-board, 1 September recovery pair | the diff of `membership.txt` against the archived copy; `opmax/membership.json`, the three rows that were `off_board` |
| 4.8 | Admitting K = 1 needed TWO rules relaxed | `scripts/build_gs_era2_board.py`: `MIN_K` (was the literal 5 in `k is None or k < 5`) and the removed `run_id == SINGLE_PASS_PV_RUN or "baseline" in label` branch; `scripts/build_gs_era2_board_opmax.py`, `MIN_K` |
| 4.9 | The two builders' memberships are now disjoint by condition id, not by suffix | `scripts/build_gs_era2_board.py`, `opmax_owned()`; the exclusion line of `membership.txt`, "43 × minted and scored by scripts/build_gs_era2_board_opmax.py" |
| 4.10 | 48 scoring jobs, 0 failures | `/tmp/board-jobs.log` on sapphire, "48 succeeded, 0 failed" |
| 4.11 | The signed analysis row was NOT amended | `git status results/run-analyses.json` clean across the whole run; the proposed outcome text is at `provenance.json` → `re_sign_pending.proposed_outcome` |
| 4.12 | `signed_at` `2026-09-10T12:34:56Z` and `gates.G1.pi_ruling` survive the rebuild | `provenance.json`, plus `_carried_forward.fields` = `["signed_at", "gates.G1.pi_ruling"]` |

**The MCB grew more permissive, and that is worth stating rather than burying.**
28 of 79 (35 %) became 49 of 103 (48 %), with the upper width 0.0501 → 0.0736. The
cells added are far BELOW the best (the twenty K = 1 cells score F1@20
0.4708–0.8263 against a board top of 0.9233), and widening a simultaneous band to
cover more candidates admits more of them. The 2026-09-10 entry predicted the
direction for 40 near-tied additions; the magnitude here is larger because these
additions are not near-tied. It is an argument for naming the candidate set an
admissible set was computed over, never for quoting the more flattering of two.

**One defect fixed in passing** — Finding 2 / fix 3 of
`reports/name-keyed-cache-audit-2026-09-12.md`:

| # | Claim | Anchor |
|---|---|---|
| 4.13 | `archived_cells()` took `n_detections` from the Obs 464 label-keyed cache for all 44 archived cells, because the archived board JSON records none | `scripts/build_gs_era2_board_opmax.py` before this change, the fallback at the former lines 171–173; the audit's Finding 2 |
| 4.14 | Exactly **one** of the 44 rows changes verdict: `pv-high-image-t0.3-n5`, `"match"` → `"differs: registry F1 0.746 n 372 vs archived board F1 0.746 n 373"` | a `derive_membership()` diff against the committed `opmax/membership.json`, run on sapphire; the cache's 372 against the file's 373 |
| 4.15 | The other 43 rows' cache values agree with their files | the same diff, `archived_cache_agrees` true on 43 of 44 |
| 4.16 | Nothing downstream moved: the row's `detections` path is unchanged (no re-materialised file exists for it), the G2 gate already expected 373 via the `BISECTED` override, and no F1 anywhere changed | `opmax/membership.json`, that row; `scripts/build_gs_era2_board_opmax.py`, `BISECTED`; `opmax/gates.json`, G2 0 failures |
| 4.17 | Four tier-1 tests pin the new behaviour | `tests/test_build_gs_era2_board_opmax_archived_counts.py`, 4 passed |

## 5. Step 5 — the ladders, and the analysis row that was not authored

Every number in `results/k-ladder-2026-09-12/findings.md` is anchored in that
document beside itself; the machine-readable form is `ladders.json`. The three
figures worth repeating here:

| # | Claim | Anchor |
|---|---|---|
| 5.1 | The gold-standard ladder on the board frame reads 0.8605 / 0.8834 / 0.8782 / 0.8905 with tile-MCC 0.7834 / 0.7762 / 0.7751 / 0.7969 at n 411 / 380 / 394 / 387 | `results/k-ladder-2026-09-12/board-frame/*/evaluation.json`, scored this run on sapphire: `era2_b_intersection_bounds.geojson`, curator reference, 14 buffers, `--bootstrap 10000 --seed 42 --mcc` |
| 5.2 | The frame tax is uniform, −0.0072 to −0.0077, inside the board's own −0.0070 to −0.0078 for grid-geometry cells | those evaluations against `results/stride-2026-08-25/conditions-verified/*/eval/evaluation.json`; the board `README.md`'s Δ frame column for the comparison range |
| 5.3 | K = 3 takes 49–93 % of each ladder's total F1 gain for 38–64 % of the top rung's cost; tile-MCC falls on five of the eight ladders | a re-derivation over `ladders.json`; the per-ladder figures are the § 4 table of the findings document |
| 5.4 | The 8,541 / 487 projection overstates this geometry's 55-map cost by 10.7 % ($115.05 projected against $103.91 measured at K = 10) | `results/stride-2026-08-25/findings.md` for the $6.56 and the 820 tiles per pass; `results/55map-final-board-r2-2026-09-06/final_board_50m.json`, `A-N10-oracle.cost_usd` |

**The analysis row `k-ladder-2026-09-12` is NOT authored.** Drafted here for
authoring once the permutation testing lands (findings § 6.1):

- `analysis_id` `k-ladder-2026-09-12`; `type` `comparison`;
  `preregistered` `post-hoc`.
- `hypothesis_refs` **`["H3"]`**, checked rather than assumed. H3 is
  "Consensus Voting — Design: multiple pool sizes (N = 5, 10, 30) and
  thresholds; Analysis: compare voted F1 vs single-pass mean F1"
  (`docs/methodology/preregistration/analysis-summary.md:93-97`), which is the
  pass-count question these ladders ask.
  `scripts/lib_hypothesis_requirements.py` carries **no** H3 entry — its table
  holds H1, H5, H7, H8, H10 and H12, the hypotheses with parameter-control
  requirements — so there is no requirement for this row to satisfy there, and
  saying the file "confirms H3" would overstate it.
- `conditions_compared`: the **44** rung rows of the eight ladders — 44 distinct
  condition ids, because a rung with both a carried and an oracle operating point
  is two registered cells (counted from `ladders.json`,
  `ladders[].rungs[].condition_id`).
- `output_path` `results/k-ladder-2026-09-12/findings.md`.
- `outcome`: to be written from the tiering, and **this is why the row waits** —
  its headline claim is which rungs are separable, and that was not measured.
- No `manually_verified_at`. The PI signs.

## 6. Step 6 — the Phase-2 costing

Every figure is anchored inside
`reports/k-ladder-phase2-costing-2026-09-12.md`. The three that matter:

| # | Claim | Anchor |
|---|---|---|
| 6.1 | 28 rungs, 35,844 candidates, **US$24.84** at US$0.000693 per candidate | `results/k-ladder-2026-09-12/first-n-union-sizes.json` for every union size (measured on sapphire with the canonical consensus chain); `reports/token-load-audit-2026-06-12.md` § 5 `VF_CALL_USD` for the rate |
| 6.2 | The R4 re-verification exposure is **nil** | `scripts/check_pv_sweep_vintage.py survey`, re-run on sapphire this session: 24 same-vintage, 4 probabilities-grew (re-swept 2026-09-08, no API call needed), 1 union-rebuilt (already re-verified for US$1.82 and registered in step 3), 1 manifest-mode |
| 6.3 | Tier A — the two T 0.7 pools the registered pass-budget Pareto rests on — is US$4.50 | the same costing report § 5; 6,492 candidates × 0.000693 |

## 7. What did NOT change

- **No API call was made**, and no run was authorised by anything in this batch.
- **`results/run-analyses.json` was not modified at any point.** Verified
  structurally, not by eye: a field-by-field comparison of all 66 rows between
  `origin/main` and `HEAD` finds **0 signature fields and 0 other fields
  changed**, and no row added or removed. The board's proposed outcome and the
  uplift row's amendment figures are recorded for the PI in `provenance.json` →
  `re_sign_pending` and § 2 above.
- **One apparent exception, which is not one.** The GENERATED
  `results/analyses-manifest.json` does move on
  `verifier-uplift-pairing.manually_verified_at`
  (`2026-09-10T22:55:40Z` → `2026-09-11T07:03:41Z`), `conditions_compared`
  (85 → 145) and `outcome`. That is **pre-existing drift being materialised**: the
  register already held the 2026-09-11 values — the PI's own re-signature — and the
  committed manifest was stale at the 2026-09-10 ones. Regenerating the manifest
  propagated the register's values into it. Nothing in the register moved, and no
  signature value was authored by this run. The same regeneration also refreshed
  several other rows' `conditions_compared` for the same reason.
- **Tier 1 of the GS Era-2 board, and its five members.** Same cells, same order,
  same F1. So are the tie set, the top cell, every gate's verdict, and G6's
  maximum frame delta (0.0078).
- **No incumbent board cell's F1 moved**, and none left the board.
- **The April cell `pv-diag-384::pv-high-text-t0.0-n3-opmax` still points at its
  403-feature April detection file** and still records F1@20 0.8234. Only its
  `_note`, `eval_path` and `scope_override` changed, and only because R3 made it a
  board member — the `_note` says what it used to be.
- **Every registered condition that existed before this run still exists**, with
  the same `detections`. 21 `-era2b` rows were added, 3 were repointed at the
  board frame, 24 G2 waivers were added, and nothing was removed
  (verified by a structural diff of `results/run-conditions.json` against
  `HEAD`, not by reading the textual diff).
- **The registered ladder analyses** `pass-budget-pareto-v2`,
  `stride-winner-ladder-exact-2026-08-25` and `stride55-ladder-2026-08-27` are
  untouched, and so is the E83 MCB ruling. The findings document adds a column to
  their story; it re-opens none of them.
- **The 55-map ladders' committed significance results** (`p7_saturation`,
  the final boards' `pairwise` tables) are cited, not recomputed.
- **`docs/methodology/notation-key.md`** gained § 7.2 and one value in § 7.1's
  `pairing_basis` row. No existing entry's meaning changed.
- **The 79-cell board is not lost**: every superseded artefact is at
  `archive/superseded-leaderboards/gs-era2-verified-board-2026-09-10-79cell-pre-k1/`.

## 8. Tests

`python -m pytest -m tier1 -q`, run at the end of the batch in this worktree:

| run | result |
|---|---|
| mid-batch | 2 failed, 2,242 passed, 1 skipped, 3 xfailed — both failures `tests/test_selection_aware_intervals.py`, **caused by this run** (the `--board` stub had a fixed signature and the MCB gained `analyses_path` / `conditions_path`) |
| after fixing them and extending the test | **2,245 passed, 1 skipped, 27 deselected, 3 xfailed, 0 failed** in 226.56 s |

`tests/test_per_arch_md_ownership.py`, the known environment-only failure the run
card said to expect, did **not** fail here — its 20 tests pass in this worktree.

New tier-1 tests this run: `tests/test_build_gs_era2_board_opmax_archived_counts.py`
(4) and `test_board_membership_source_override_is_recorded` (1).

## Changelog

### 2026-09-12 — Original publication (Session 154, K-ladder Phase 1 step 7)

Written from the artefacts each claim names, re-read in the same session. Two of
this run's own errors are recorded rather than quietly fixed: the coverage probe's
degrees-as-metres tolerance (§ 1), and the findings document's first-draft
arithmetic on how much of each ladder's gain K = 3 takes (§ 5.3 and the findings
changelog).
