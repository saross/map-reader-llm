# D57 (4) re-score, Phase 3: the S3 deltas

> **Last revised**: 2026-10-10 (original publication). See
> [§ Changelog](#changelog) for revision history.

- **Executed by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), a subagent of the main Session 163 session, on
  sapphire, 2026-10-09 12:29–13:54 UTC (84 minutes of wall clock; the
  reduced-frame tiering took 4,325 s per tree).
- **Repository**: `map-reader-llm`.
- **Trees**: NEW is a detached worktree at `e1e8f444a` (draft PR #29's data
  head); OLD is `git archive b3c52591d`; a third, untracked
  `git archive e1e8f444a` ("chain tree") was used only where a driver must
  read a NEW upstream artefact from a fixed path
  (`phase3-out/newchain-placement.txt` lists what was placed there).
- **Plan**: `planning/d57-4-rescore-plan-2026-10-09.md` § 4; rulings D58.
- **Where the outputs are**: `~/scratch/d57-4-rescore-2026-10-09/phase3-out/`
  on sapphire — `old/` and `new/` (outputs per test), `diffs/*.txt` (one
  comparison file per test), `logs/` and `pids/` (49 runs, every exit code
  0), `trace/` (read sets), `committed/` (snapshots of the committed
  artefacts), and `bin/` (helpers).
- **Guarantees**: no model Application Programming Interface (API) was
  called; nothing was committed or copied into a tracked tree; no document
  was edited. Sapphire's shared checkout read HEAD `8988f3f17` with the same
  122 porcelain lines (identical SHA-256) before and after.

**Convention.** "OLD reproduces" means the old scorer regenerates the
committed artefact, so NEW − OLD isolates the D50 effect. Values below are
committed → NEW unless marked otherwise.

## Session checks of this report (2026-10-10)

The main session re-read these at source before publishing:

- All 49 `pids/*.rc` files read 0.
- `diffs/h13.txt`: committed vs OLD rerun, 0 differing leaves; arm A − B
  `p_two_sided` 0.0385 → 0.0237, primary 95% confidence interval (CI)
  [0.000945, 0.070750] → [0.005455, 0.077534].
- `diffs/uplift.txt:444`: `pair::55maps-image-generalisation::verified-k3-r2-gt`
  uplift 0.2014 → 0.1632.
- `diffs/null-exemplar.txt:175,178,245`: tie set and Tier 1 4 → 5 (joined
  `grid-2026-08-18::g384-ov192-k5-verified-opmax`); significant pairs
  7905 → 7959.
- `diffs/h3.txt:23,44`: H3 headline 0.427 → 0.4294, p 0.0, significant.
- `diffs/e45-fdr-h8.txt`: `family_fdr.json`, its metadata, and
  `h1_cmt0106_pooled_modality.json` have 0 differing leaves under both
  scorers.
- `diffs/e43.txt:90–93`: the four `CELLS` pins listed below.
- **The tier-0 aggregation sweep's CI failure predates D50.** The committed
  `results/h13-overlap-2026-08-18/tier0-aggregation/tier0_sweep.json` was
  added in `dccee3362` (2026-08-18 11:53 +1000), before the
  BCa-adapter fix `122104b8a` (2026-08-19 08:41 +1000, "stop transposing
  scipy's resample batch in BCa adapter"); it has had no later commit. Its
  54 CI bounds are therefore from the defective adapter, and today's
  intervals are wider (e.g. cell 0 [0.4348, 0.5092] → [0.4086, 0.5314]).
  The sweep's Markdown shows no intervals. The attribution to `122104b8a`
  rests on dates and the fix's subject, not on a replay at that commit.
- **Flag 4's defect is confirmed** at `scripts/analyse_null_exemplar_sensitivity.py:1312–1316`:
  `admissible()` zips the candidate list with `hsu_not_ruled_out`, which
  `scripts/selection_aware_intervals.py:368` writes as a list of indices
  (committed `reduced_f1_b20_m1.json` begins `[1, 2, 3, 4, 5, 6]`, with 150
  candidates). The zip keeps the first *n* candidates, not the indexed
  ones. Counts are right unless the list contains index 0.

## Bottom line

**Wherever OLD reproduces, the conclusions hold under NEW.** No p value
crosses 0.05, no CI starts to include zero, no H3 tier changes, and the
confirmatory Benjamini–Hochberg false discovery rate (BH-FDR) family is
byte-identical. Three exceptions:

1. **The null-exemplar reduced Era-2 board moves** — Tier 1 4 → 5,
   significant pairs 7,905 → 7,959 — partly as a mixed-vintage artefact
   (flag 1).
2. **The F1 verifier uplift falls by up to 0.0382**, where the plan
   predicted at most 0.0033 (flag 2).
3. **Five lines fail OLD reproduction** for reasons that predate D50
   (§ Stopped lines).

## Per test

1. **h13 A − B** (`h13_overlap_analysis.py`). OLD reproduces exactly.
   - A − B: Δ +0.0380 [+0.0009, +0.0708], p 0.0385 →
     **+0.0432 [+0.0055, +0.0775], p 0.0237**. The B = 10,000
     sensitivity interval goes [+0.0015, +0.0741] → [+0.0060, +0.0795].
   - A − C 0.1554 → 0.1617; B − C 0.1174 → 0.1185; both p = 0.0.
   - Arm micro-F1: A 0.5578 → 0.5733, B 0.5198 → 0.5301, C 0.4025 → 0.4116.
   - Low-margin recall is unchanged; overall recall rises. No conclusion
     changes. The 0.0434 quoted in D57 is the per-pass cell mean; the
     analysis's pooled micro-F1 gives 0.0432.
2. **h13 sub-analyses.** `h13_k_sensitivity` and
   `h13_tilesize_overlap_grid`: OLD reproduces; NEW identical. The
   aggregation sweep is a stopped line (above and below); NEW equals the
   OLD rerun bit for bit.
3. **H2** (`run_pairwise_tests.py`, group 1, 20 m). The primary (16-of-30
   + proposer–verifier (PV) vs 26-of-30) reproduces under OLD in both forms
   (`--quiet` and the e45 rerun); **NEW is identical** (Δ 0.076083, p 0.0,
   per-tile block included). Two other group-1 contrasts do not reproduce
   under OLD: their shared B arm, "single-pass text 5-of-5", has drifted
   from 951 to 954 detections. NEW equals OLD there.
4. **H3** (`consensus_vs_baseline_tiering.py`, champions and
   with-deployable). OLD reproduces every statistic, p, tier, and BH call.
   - One carried Matthews correlation coefficient (MCC) column does not
     reproduce: `pv-diag-384::baseline-flash-image-minimal-t-0-7` reads
     0.3295 → 0.3296, changed by the E82 re-emission (`43ea31b26`,
     2026-08-22). No test reads that column; ruling pending (§ Decisions).
   - NEW: primary (26-of-30 vs text baseline T 0.7) Δ 0.4270 → 0.4294,
     p 0.0. Diversity-dividend contrasts: text 0.1530 → 0.1533, image
     0.0697 → 0.0699. Flash HIGH vs Pro leader 0.0096 → 0.0120, p
     0.6163 → 0.5266 (not significant).
   - **No tier, rank, tie-set, or significance changes**: 197 of 231
     significant before and after; deployable 268 of 325.
5. **e45** (`e45_bootstrap_pairings.py`). OLD reproduces (only the rerun
   argument's path differs). Against the committed H3 file the NEW H3 gate
   refuses (0.816471 vs 0.814118); run in the chain tree against the NEW
   H3 artefact, both gates pass. H2 unchanged. H3 Δ 0.427340 → 0.429693;
   B = 1,000 CI [0.389640, 0.468082] → [0.392114, 0.470439]; B = 10,000 CI
   [0.385608, 0.469544] → [0.388060, 0.472072]; p unchanged.
6. **Family BH-FDR** (`compute_family_fdr.py`). OLD reproduces exactly;
   **NEW is byte-identical in values**. Gate A passes; H1 Δ +0.0238, p
   0.0715; the rejection set stays {H2, H3, H7}; the H2 = H3 = 0.0 pins
   hold. Extra check: H8's family input `results/h8-v2/permutation-t4/`
   replayed on all 7 contrasts on the 327-tile `h10_test_bounds` — OLD
   reproduces, NEW unchanged, Simes 0.8344 holds.
7. **h6** (`h6_registered_analyses.py`).
   - A-07: OLD reproduces. NEW raises the Flash comparator curves (text
     0.4634/0.5203/0.5748 → 0.4647/0.5217/0.5764; image
     0.5614/0.5760/0.5854 → 0.5631/0.5778/0.5873) and the Pro text curve
     (0.8602/0.8558/0.8494 → 0.8626/0.8582/0.8519). Optimal k, fragility
     flags, and verdicts are unchanged; the Pro text margin is
     0.004457 → 0.004423.
   - A-06 and A-09: stopped lines (below).
8. **e43.** `regen_e43_board.py` reads only the March pairwise JSONs:
   OLD and NEW identical apart from the commit stamp. The matched-temperature
   analysis's 12 F1 permutation tests all reproduce under OLD; under NEW
   both arms rise by about 0.002. p: n5-20m 0.3352 → 0.3293; n5-30m
   0.3577 → 0.3486; n10-20m 0.0815 unchanged; n10-30m 0.0963 → 0.0976.
   The near-threshold T 0.3 vs T 1.0 rungs stay at 0.0624 and 0.0563. No
   crossings.
9. **Tile-size sweep.** OLD reproduces. NEW moves only the 384 px consensus
   cells (+0.0019 to +0.0025; text HIGH 0.8141 → 0.8165, image
   0.7500 → 0.7524). No best-size direction flips.
10. **Uplift chain.**
    - Verifier uplift: OLD reproduces both CSVs byte for byte. F1 changes in
      30 of 170 pairs, all from the unverified side and all decreases
      (−0.0001 to −0.0382), with no sign change.
    - MCC uplift: 18 pairs change by ±0.0003. **Two pairs go computed →
      pending**: the stride ov128 n10 k7 r2-gt and standardised-gt twins
      (0.0121 and 0.0122) now have their MCC withheld by the tile-join
      invariant.
    - Flatten: a stopped line (below).
11. **Null-exemplar** (filter, signature, override, swap, and assemble
    stages; `era1_leaderboard_tiering --permute-mcc`;
    `selection_aware_intervals --board` for F1 and MCC).
    - OLD reproduces every committed artefact: manifest, signature, swap,
      tiering, both multiple-comparisons-with-the-best (MCB) results, and
      `analysis.json`. The override files differ only through register
      growth; the board's 153 members are identical apart from `_note` and
      `verifier_config` in 6.
    - Signature: Era-2 observed −0.088143 → −0.08906, p 0.0; the Era-1
      boards are unchanged.
    - Swap: no p crosses 0.05; full-vs-reduced verdict flips stay at 6 of
      118. On the reduced Era-1 frame, 9 image-minus-text ΔF1 values change
      sign, all at p > 0.75.
    - Reduced F1 tiering: 13 tiers unchanged; **Tier 1 / tie set 4 → 5**
      (`grid-2026-08-18::g384-ov192-k5-verified-opmax` joins); significant
      pairs 7,905 → 7,959 (82 flips); Spearman 0.998852 → 0.998091;
      largest rank shift 8 → 14; cells moving more than one tier 2 → 4.
      The MCC family is unchanged.
    - F1 MCB: argmax cell and the 66-member admissible set unchanged;
      optimism 0.0056 → 0.0064. MCC MCB unchanged.
    - Per cell: Era-1 `text-high-t0.3-n10-8of10` −0.0245 → −0.0142; Era-2
      excluding ladder cells −0.0074 → −0.0068.

## Stopped lines (OLD does not reproduce; causes predate D50)

| Line | Why OLD fails | NEW vs OLD rerun |
|---|---|---|
| h13 aggregation sweep | 54 CI bounds from before `122104b8a` (§ Session checks) | identical |
| H2, 2 other group-1 contrasts | shared B arm drifted 951 → 954 detections | identical |
| h6 A-06 | committed file still carries pre-D42 bootstrap p fields | identical |
| h6 A-09 | 18 cost fields on the audited basis (D11–D16); today's costs flip the matched text limb "fires: true → false" (registered gate verdict unaffected) | F1 ratios −0.0036 to +0.0027 |
| Uplift flatten | 66 conditions registered since the 2026-09-12 build; `cost_usd` changed in 332 rows | exactly the 61 registered rows change (F1, its CI, P, and R) |

## Flags

1. **Mixed vintage in the null-exemplar analysis.** The cells that move it
   are the seven held ladder cells (three `g37-text` K-ladder cells and
   four `grid-2026-08-18` tier-E cells). Their full-frame evaluations — the
   "before", and the Era-2 board's tiering and MCB — are held for Phase 6 on
   the OLD scorer; their reduced-frame twins were regenerated in Phase 2 on
   NEW, unclipped. Their per-cell deltas flip sign (e.g.
   `g37-text-k1-carried` −0.0071 → +0.0279), and they drive the Tier 1 and
   rank-stability changes. The null-exemplar figures cannot be read
   consistently until Phase 6.
2. **The plan's uplift prediction was ten times too small.** Nine pairs
   fall by at least 0.01; the four largest are 55-map pairs (e.g.
   `55maps-image-generalisation::verified-k3-r2-gt` 0.2014 → 0.1632, its
   unverified twin's F1@50 0.5994 → 0.6376 with 513 origins restored). The
   S2 gate matched these cell values, so the plan's figure (§ 4: "up to
   −0.0033") is what is wrong.
3. **H2 and H3 now score the 26-of-30 set differently.** H2 rebuilds the set
   itself and stays at 0.814118; H3 and the re-scored cell give 0.8165.
4. **A defect independent of D50** in the null-exemplar assemble stage
   (§ Session checks). The signed findings therefore misname the moved
   cells. Read by index, the committed artefacts give: F1 admits
   `flash35-pv-2x2::f35prop-f3vf-4of10-era2b`, not
   `pv-high-image-t0.3-n3-carried-p0.15-k3`; tile-MCC admits 1 and drops 3,
   not "0 admitted, 2 dropped". Nothing was changed.
5. **Full-frame ladder cells already move under NEW.** In the signature
   stage the four `grid-2026-08-18` cells gain TP_rest +6 and lose
   FP_rest −6, so the Era-2 board will move in Phase 6.

## Register rows and signatures

Under `docs/methodology/signature-policy.md` ("any change to the row's
numbers"), these lapse:

- The expected six: `h13-overlap-2026-08-18`,
  `null-exemplar-sensitivity-2026-09-13`, `e45-bootstrap-pairings`,
  `h6-a07-voting-thresholds`, `uplift-supplement-flatten`, and
  `verifier-uplift-pairing`. The null-exemplar attested text quotes figures
  that change (7,905 pairs, Spearman 0.998852, shift 8, 2 cells, −0.088143,
  and the Tier-1 size).
- Also `h6-a09-cost-gate`: D50 moves its F1 ratios, and it already fails OLD
  reproduction on costs.
- Not lapsing from D50: `h6-a06-decision-rule` (NEW equals OLD; its D42
  vintage is a separate issue), `family-bh-fdr-confirmatory`, and
  `h1-cmt0106-pooled-modality`.
- Unsigned rows that move: `diversity-dividend-384`, `tile-size-sweep`, and
  `e43-matched-temperature`.

## Pinned constants (nothing edited)

- `scripts/author_e43_matched_temperature.py` `CELLS` (from findings § 3,
  `6176b985e`): t07-n5-5of5 0.6397 → **0.6415**; t10-n5-5of5 0.6610 →
  **0.6631**; t07-n10-10of10 0.6332 → **0.6352**; t10-n10-9of10 0.6667 →
  **0.6687**. Under NEW only gate 3 refuses; MCC and `n_detections` are
  unchanged. Its `ANALYSIS_OUTCOME` prose would also shift (e.g. −0.021,
  p 0.335 → −0.022, p 0.329; p 0.096 → 0.098). These are the two tier-1
  failures on draft PR #29.
- `scripts/h13_k_sensitivity.py:249` hard-codes `committed_f1: 0.6667` for
  the same 9-of-10 cell, now 0.6687. The output is not gated, so the file is
  unchanged under NEW, but the decomposition note goes stale.

## D58 Q2: does any test read a drifted cell?

Every NEW driver ran under an audit hook that recorded each file it opened;
the reduced tiering and MCB were checked statically (all 153 evaluation
paths point at reduced cells). **None of the 25 drifted or pinned cells, or
their detection files, is read by any test.** The only watched reads are the
seven ladder cells in the null-exemplar stages (flag 1). No driver read from
the shared checkout.

## Not run

- The e43 paired-MCC tests (`paired_mcc_permutation.py`): their cells' MCC
  is unchanged, so they are not expected to move, but that is unverified.
- The stopped lines' D50 deltas beyond "NEW vs OLD rerun".
- The ladder cells and the Era-2 board (Phase 6).

## Decisions this raises

1. Rule on the H3 carried-MCC column (0.3295 vs 0.3296, E82 vintage): a
   failure by the letter, read by no test.
2. Whether to re-run the five stopped lines on today's inputs as their own
   refresh (they are stale for reasons other than D50).
3. Whether H2 should read the re-scored 26-of-30 cell rather than rebuild
   it (flag 3).
4. Fix the null-exemplar `admissible()` defect (flag 4) and correct the
   signed findings' member names.

## Changelog

### 2026-10-10 — Original publication

The Phase 3 agent's hand-back, with the main session's checks at source
added (§ Session checks), including the dating of the tier-0 sweep's CI
failure and confirmation of the `admissible()` defect.
