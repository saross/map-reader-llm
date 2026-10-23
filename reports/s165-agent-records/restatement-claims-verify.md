# PR #52 restatement pass § 6: claim-row verification

- **Verifier**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), read-only sub-agent. 2026-10-18.
- **Reviewed**: `reports/s164-agent-records/restatement-pass.md` § 6
  (§ 6.1 table, 39 rows; § 6.2; § 6.3) in the worktree
  `/home/shawn/worktrees/map-reader-llm/claude-pr52-restate`, branch
  `restatement-pass-s164` (PR #52).
- **Revisions read**: branch point `718d0ee08` (BASE) and HEAD. HEAD moved
  during the check from `c24d5a04f` to `26deb34a3`; the two new commits add
  only `reports/s165-agent-records/k-ladder-redraft/`, so every `results/`
  file read is identical at both. § 6 says it was built from `0fc2d6389`;
  three later commits bear on it (`94d5815b3` rounding, `92a66089d` five
  more lapses, `c24d5a04f` the PI-approved register texts, D69).
- **Method**: every Quoted value re-read in
  `docs/paper/results-claims-inventory-2026-09-12.md` (unchanged between
  BASE and HEAD); every regenerated and BASE value re-read with
  `git show <rev>:<path>` and small Python reads; no model call, no
  re-computation beyond arithmetic on committed numbers. Nothing in the
  worktree was written.
- **Cause codes** used below: (a) origin route, D62 (1); (b) re-verification
  of the wrong-sheet candidates, D62 (1), 2026-10-13; (c) the D50 scorer
  (S9 cells); (d) D60 (3) consensus route; (e) D42 permutation p; and two
  the brief did not list but the rows need: **(f) the D51 clip** to the
  common assessed area (Phase 2 ladders) and **(g) the 2026-09-13/14 board
  rebuilds** (membership, for the stale rows). Attribution follows the
  COMMITTED → ORIGIN → REPAIRED columns of
  `reports/s164-agent-records/rescore-repaired-gs.md` §§ 3–4.

## Problems found, most important first

1. **R3-11's proposed range is wrong.** "About US$0.21 to about US$22 per
   0.001 F1" takes Phase 2's range (K-ladder findings § 7.4) for a claim
   about all 23 ladders. The two 55-map 3.7 arms' last steps (K = 3 → 5)
   cost about US$27 and US$26 per 0.001 F1@50 (findings § 3.4 table:
   +0.0022 for $58.85, +0.0023 for $59.55), are untouched by the pass, are
   the dearest step on their ladders, and are now the dearest last steps in
   the corpus. The upper end is about **US$27**. The § 6.1 cell's "the next
   dearest last step is unchanged (55-map stride B, about US$17)" is wrong
   for the same reason, and the restated findings § 7.4 at HEAD already say
   so. The pass's own § 4.12 draft outcome reads "about US$0.20 to US$27",
   so § 6.1 and § 4.12 disagree. The lower end is US$0.21 over the 17
   ladders whose last step is dearest (MINIMAL image T 0.7, $3.09 for
   +0.0147); it is US$0.20 if the exceptions count (GS stride A's last step
   is now $2.7389 for +0.0138, US$0.198).
2. **R7.3-22 and R7.3-24 round the all-3.7 gap the wrong way.**
   `results/gemini37-image-gs-2026-09-01/gap_test.json` → `pairs.all-3.7`
   at HEAD: `observed_diff` −0.00435 (f1 0.936416 against 0.940767, so
   −0.004351). At four decimals that is **−0.0044**, not −0.0043 (BASE was
   −0.004345, which is −0.0043). Commit `94d5815b3` made this fix in the
   documents after § 6 was built, the restated findings (lines 71 and 146)
   read +0.0044, and the PI-approved register text (`c24d5a04f`) reads
   −0.0044. R7.3-24's wording is also internally inconsistent: 0.9408 −
   0.9364 = 0.0044.
3. **R4-04's "0.817" is double-rounded.** The consensus 26-of-30 arm is
   0.816471 (`results/diversity-dividend-384/tiering-champions/tiering_20m.json`
   rank 1, `observed_micro_f1`; `results/family-fdr/family_fdr.md`
   changelog), which is **0.816** at three decimals; 0.8165 → 0.817 rounds
   twice. 0.890 − 0.816 = 0.074 then matches the rider. The same slip is in
   § 6.2's R4-12 note ("its anchor's 0.814 is now 0.817") and in
   `results/diversity-dividend-384/diversity-dividend-analysis.md` line 84
   (0.817).
4. **New, not flagged anywhere: R6-18's board-grain note (Obs 482)
   partly fails.** At HEAD the top F1 cell
   (`g37-image-k5-verified-swap37-p0.90-k5`) is in tile-MCC Tier 1 (MCC
   rank 21, tile-MCC 0.8376): `tiering_20m.json` →
   `mcc_permutation.tiers[0]` (34 members) intersects F1 Tier 1 in that one
   cell, and the board README's MCC table row 21 shows it. At BASE the
   intersection was empty and MCC Tier 1 (33) came from F1 tiers 6–12; at
   HEAD it comes from F1 tiers 1 and 6–12. So "no F1 Tier-1 cell is in
   tile-MCC Tier 1" and "drawn entirely from F1 tiers 6–12" no longer hold.
   § 6.2 lists R6-18 as holding and says the overlap "was not recomputed";
   I recomputed it from the two MCB files (`hsu_not_ruled_out`): the F1 and
   MCC admissible sets share **9 of 52 and 60** (9 of 65 and 59 at BASE,
   reproducing Obs 482's count). The inventory's cross-section text (lines
   1408–1410 and 1528) rests on the same reading. The board README's
   2026-10-15 changelog records the count changes (2,982 → 3,001, tie set
   33 → 34) but not this.
5. **R1b-16's wording claims more than the values support.** "Which share
   its 20 m tier but not a 30 m shelf" asserts a separation at 30 m where
   no test exists, and the 30 m gap (opmax 0.9173 against the best geometry
   cell's 0.9124, 0.0049) is smaller than the 20 m gap the same sentence
   calls one tier (+0.0116, p 0.380). The failure verdict (the "~0.903,
   all three equal" shelf is gone) stands; the wording should say the 30 m
   point estimates no longer agree, not that the cells are on different
   shelves. The cause matters for the PI: the 30 m failure is driven by
   (a) on the incumbents (opmax 0.9031 → 0.9173 already in ORIGIN), and
   (b) on the geometry cells partly closes it.
6. **R1b-09's wording invites a contrast the data do not support.** "At
   512 px but not at 384 px" reads as a size difference; the interaction
   test does not separate the two sizes (`verifier_analysis.json` →
   `interaction` −0.0246 [−0.0613, +0.0114], p 0.1831). Add it. The failure
   is entirely cause (b): in ORIGIN the 384 px contrast is unchanged
   (−0.0285, p 0.0235), and the PI-approved register text already says "a
   move due to the re-verified candidates".
7. **R4-28's column and § 6.3 note 8 are stale against HEAD.** Since
   `92a66089d` the `gs-era2-verified-board-2026-09-10` and
   `k-ladder-2026-09-12` rows read `signature.status: re-sign-pending`
   (`results/run-analyses.json`), not "still signed"; only
   `stride-plateau-2026-08-25` remains signed. The proposed R4-28 wording
   itself is right.
8. **R3-14 / R6-17: the "partly stale" attribution is wrong.** The 68.8 %
   the column attributes to "S9's drift alone" is the re-score's ORIGIN
   reading, which also carries (a) on the consensus-only side (+0.0572 →
   +0.0660). S9 alone (committed consensus side, +0.05722) gives
   1 − 0.020614 / 0.05722 = **64.0 %**; ORIGIN on unrounded values is
   1 − 0.020614 / 0.065954 = **68.7 %**. Neither branch-point file
   (`tension/grid-overlap.json`, `tier-e/ladder.json` at `718d0ee08`)
   differed from the quote, so these rows are not "stale" in § 6's own
   sense. On the known clipped share: the unrounded inputs (clipped K = 1
   0.860360 from
   `reports/scorer-frames-d50-d51-2026-10-08-scripts/out/ladders_new.json`
   → `tier_e.rungs[0].points.opmax.d51_clipped.f1`; K = 10 0.894173 =
   752/841 from the K = 10 evaluation; consensus +0.065954) give
   **48.7 %**; the 48.8 % in note 4, § 1.4 (line 267), § 10 (line 2325) and
   findings § 8.6 (line 1551) comes from four-decimal inputs. The 60.3 %
   reproduces on unrounded inputs (60.33 %).
9. **R3-13: +0.0130 is right, but the record disagrees with itself.**
   `mcc-test/summary.json` → `gs-stride-a.mcc_direction_k1_to_best`
   0.013043. § 3 (line 635), the § 4.12 draft outcome, the re-score and
   findings line 382 say +0.0131 (a difference of rounded endpoints);
   findings line 472 and 1625 say +0.0130. The BASE value was 0.013419
   (+0.0134), so the inventory's +0.0135 was itself a rounded-endpoint
   figure. Use +0.0130 throughout.
10. **No wording names a cause.** The PI's approved register texts (D69,
    `c24d5a04f`) add a dated clause naming each move's cause; none of the
    39 § 6.1 wordings does. Per-row causes are in the tables below.
11. **Smaller wording points**: R1b-17 "within 0.008" for a gap of 0.0083
    (0.907543 − 0.899263) — say "0.008 below" or "within 0.01"; R4-21
    "every Gemini 3 cell" should exclude or name the fourth cell (Gemini 3
    proposer, 3.7 verifier; rank 7, 0.9141, Tier 2), and tier E's K = 5
    move (0.8905 → 0.9046) is entirely (c); R6-16 "the 3.7 family's" is now
    ambiguous (the 55-map 3.7 arms' last steps cost more) — say "the 3.7
    gold-standard text ladder's K = 5 → 10"; R3-15, R3-11 and R6-16 use
    D51's clipped basis while R3-14 / R6-17 use tier E unclipped, and the
    restated findings § 8.2 table reads as-evaluated (+0.0629) — each
    wording should name its basis; R1b-11, R1b-12 and R1b-14 quote
    384/12.5's argmax 0.8761 without saying it is not the registered 0.8752
    (§ 6.3 note 6's own rule; R1b-08 does say it).
12. **Jargon an outside reader cannot parse**: "opmax", "incumbents",
    "registered headline", "grid winner" (R1b-15, R1b-16); "tier E"
    (R4-21, R4-23, R4-24); "`-opmax` cells" (R4-22; also id-based, so it
    includes at least one committed incumbent, the inventory's own R4-21
    note); "Hsu MCB" (R4-20); "BH-adjusted" (R4-23, R4-24); "board frame"
    (R4-25); "F1@20", "tile-MCC" (R3-14, R6-17); "GS" (R1b-15, R7.3-04);
    "I1", "I2", "text-side gain" (R7.3-21, R7.3-22); "MDE80" (R7.3-24; the
    approved register text glosses it); "(0.20, k7)", "512/50 %", "K = 10"
    notation (the R1b block); "all-3.7 stack" (R7.3-11); "union recall
    ceilings", "stacked optimum", "pure-verifier k = 1 board" (R1b-11,
    R1b-12).

**Clean rows** (every value and verdict confirmed, wording numbers right;
only the cause clause and glossing to add): R1b-02, R1b-03, R1b-04,
R1b-05, R1b-06, R1b-07, R1b-08, R1b-10, R1b-11, R1b-12, R1b-14, R3-14 and
R6-17 (wording; their column attribution is item 8), R3-13 (wording;
item 9), R4-17, R4-18, R4-19, R4-20, R4-22, R4-23, R4-24, R4-25, R7.3-01,
R7.3-04, R7.3-11, R7.3-12, R7.3-21. **Rows needing a change**: R3-11,
R7.3-22, R7.3-24, R4-04, R1b-16, R1b-09, R1b-17, R4-21, R6-16, R4-28
(column only), R1b-15 (column word "now" only; see its detail), R3-15
(basis only).

## Summary table

"Values" counts the distinct figures re-read (quote, BASE, HEAD). OK means
every one matched its source.

### The 3 failures

| Row | Values checked | Mismatches | Verdict OK? | Wording issues | Cause to state |
|---|---|---|---|---|---|
| R1b-09 | 4 quoted, 8 BASE (incl. CI), 8 HEAD (incl. CI) | none | yes: 384 px p 0.0541, CI to +0.0001; 512 px holds | add interaction p 0.1831 (item 6) | (b) for the failure; (a) baselines; (e) p |
| R1b-15 | 9 | none in values; column says best cell "now above every incumbent", but it was already above at BASE (0.8982 vs 0.8842) | yes: 30 m sentence fails; 6 of 78 and tiers verbatim (same six pairs) | "opmax", "GS", "incumbents" unglossed | 30 m: (a) incumbents, (b) geometry; 6 of 78 went to 8 in ORIGIN (a) and back in (b) |
| R1b-16 | 6 | none | yes (shelf at ~0.903 gone) | "not a 30 m shelf" overreaches (item 5) | (a) incumbents, (b) geometry cell |

### The 8 already-stale rows

| Row | Values checked | Mismatches | Verdict OK? | Wording issues | Cause to state |
|---|---|---|---|---|---|
| R4-17 | 4 | none | yes (stale; unmoved) | none | (g) |
| R4-18 | 6 | none | yes | none | (g); then (c) 7,961 → 8,014 and (b) → 8,075 |
| R4-20 | 3 | none | yes | gloss "Hsu MCB" | (b) (65 → 65 → 52) |
| R4-21 | 8 | none | yes ("Tier 2 or below" holds) | "every Gemini 3 cell" vs the fourth cell; "tier E" | (g); tier E K = 5 entirely (c) |
| R4-22 | 6 | none | yes | "`-opmax`" undefined and id-based | (b) + (c) |
| R4-23 | 10 | none | yes (raw p 0.0381 known) | "tier E", "BH-adjusted" | (b) lowest Tier-1 cell; (c) tier E cell; (g) |
| R4-24 | 10 | none | yes | as R4-23 | as R4-23 |
| R4-28 | 2 | column "register still reads signed" is stale (item 7) | yes | none | signature lapse |

### The 28 restating rows

| Row | Values checked | Mismatches | Verdict OK? | Wording issues | Cause to state |
|---|---|---|---|---|---|
| R1b-02 | 4 + CIs | none | yes | none | (a) |
| R1b-03 | 3 + BASE p | none | yes | label p as permutation | (a); (e) |
| R1b-04 | 7 | none | yes | none | (a) |
| R1b-05 | 8 | none | yes | none | (a) |
| R1b-06 | 8 | none | yes | none | (a) |
| R1b-07 | 6 | none | yes | none | (a) |
| R1b-08 | 9 | none | yes | none | (b) |
| R1b-10 | 8 + BASE p | none | yes | label p | (a) baselines, (b) verified, (e) |
| R1b-11 | 10 | none | yes | pre-existing "where consensus-only was worst" is loose (see detail) | (a) ceilings; (a) lowers and (b) raises the gains |
| R1b-12 | 6 | none | yes | gloss terms | (b) |
| R1b-14 | 10 + BASE p | none | yes | argmax 0.8761, not registered | (b); (e) |
| R1b-17 | 12 | none | yes | "within 0.008" for 0.0083 | (b) |
| R3-11 | 10 | **range upper end wrong**; "next dearest" wrong (item 1) | yes (17 of 23 holds) | US$22 → about US$27 | (b) 3.7 last step; (c)+(f) 3.7 share |
| R3-13 | 3 | none at source (+0.0130); record inconsistent (item 9) | yes | none | (b) |
| R3-14 | 10 | none in values; attribution of 68.8 % wrong (item 8) | yes | none | (a) consensus side, (c) K = 1, (b) K = 10 |
| R3-15 | 5 | none | yes | name the basis (D51 clipped) | (f); (b) GS stride A |
| R6-16 | 5 | none | yes | "the 3.7 family's" ambiguous | (b) 3.7 step; (f) HIGH text T 1.0 |
| R6-17 | 6 | as R3-14 | yes | none | as R3-14 |
| R4-04 | 4 | **0.817 should be 0.816** | yes (+0.074 ≥ 0.05) | rounding (item 3) | (d) |
| R4-19 | 5 | none | yes | none | (b) |
| R4-25 | 4 | none | yes | gloss "board frame"; two rows' corrected F1 is from the argmax | (b), with (a) from `92889e0e5` |
| R7.3-01 | 3 (+2 UNCHECKED) | none | yes | none | (a) moved the argmax, (b) moved it back and raised it |
| R7.3-04 | 4 | none | yes | "GS" | (b) |
| R7.3-11 | 6 | none | yes | "all-3.7 stack" | (b) |
| R7.3-12 | 2 (+2 UNCHECKED) | none | yes | none | (b) |
| R7.3-21 | 8 | none | yes | "I1", "text-side gain" | (a) + (b) |
| R7.3-22 | 13 | **−0.0043 should be −0.0044** | yes (parity) | rounding (item 2); "I2" | carried gap (a) then (b); G3 gap (b) |
| R7.3-24 | 4 | **+0.0043 should be +0.0044** | yes | rounding; "MDE80" | (b) |

## Per-row detail

Paths are under the worktree. "BASE" = `718d0ee08`; "HEAD" = `26deb34a3`
(results identical to `c24d5a04f`).

### Failures

**R1b-09.** Quote matches inventory line 280. BASE
`results/grid-2026-08-18/verifier_analysis.json` → `bootstrap_contrasts`:
512 px −0.05041, p 0.0003; 384 px −0.02845 [−0.05304, −0.00449], p 0.0235;
`bootstrap_contrasts_consensus_k10_baseline`: −0.07582, p 0.0008; −0.07300,
p 0.0032 — all OK. HEAD: 512 px −0.05017, p 0.0003; **384 px −0.02558
[−0.05171, +0.00008], p 0.0541**; baselines −0.07663, p 0.0006 and
−0.07183, p 0.0037 — all OK. Ratio at 512 px 0.0502 / 0.0766 = 0.655 → 0.66
(OK; it was 0.665 at BASE, so "about half" was already loose). Verdict
follows. Wording: numbers right; add the interaction (−0.0246, p 0.1831,
same file); name cause (b).

**R1b-15.** Quote matches line 286. `results/stride-2026-08-25/plateau_analyses.json`
→ `board_13cell`: 6 of 78 at both revisions, and the significant pair set
is identical (all six against `g512_ov064`); tiers 12 + 1, same members.
256 vs 192: BASE +0.0020, p 0.8662; HEAD +0.0059 (0.005864), p 0.6395 — OK.
Best cell against opmax at 20 m: BASE +0.0140, p 0.2908; HEAD +0.0116,
p 0.3801 — OK. Incumbents at 20 m (common footprint,
`results/grid-2026-08-18/incumbents_common_footprint.json`): opmax 0.8842 →
0.8960, headline 0.8838 → 0.8910 — OK. 30 m:
`stride_verifier_analysis.json` → `boards.*.f1_30m` g384_ov128 0.90307 →
0.91241, g384_ov192 0.90338 → 0.90887; opmax 30 m 0.9031 → 0.9173 — OK.
20 m shelf 0.9017–0.9075 → "~0.902–0.908" OK. The column's "now above every
incumbent" misleads: at BASE 0.8982 already exceeded 0.8842. Wording
numbers right.

**R1b-16.** Quote matches line 287. Tiles 820 / 1,398 and costs unchanged
(stride findings changelog "What did NOT change"). 30 m: opmax 0.9031 →
0.9173, headline (`verified-adv-text-consensus-16of30`) 0.8958 → 0.9054,
best geometry 0.9031 → 0.9124 — all OK. Wording: see item 5.

### Already stale

**R4-17.** Quote matches line 567. Board README line 5 at BASE and HEAD:
153 admitted, 150 tiered, 3 withheld; `tiering_20m.json` `n_cells` 150,
`n_cells_withheld` 3 at both — OK.

**R4-18.** Quote matches line 568. `tiering_20m.json` pairwise: BASE 11,175
pairs, 7,961 significant, 14 tiers; HEAD 11,175, **8,075**, 14 — OK.

**R4-20.** Quote matches line 570. `mcb/…_b20_m1.json` → `hsu_not_ruled_out`
length: BASE 65, HEAD 52 — OK.

**R4-21.** Quote matches line 571. BASE README: 16-of-30 0.8951 rank 8;
tier E K = 5 (`g384-ov192-k5-verified-opmax`) 0.8905 rank 9; HIGH text T0.3
K = 5 0.8873 rank 12 — OK. HEAD README: tier E K = 5 0.9046 rank 8 Tier 2;
16-of-30 0.8951 rank 10 Tier 2; HIGH text T0.3 K = 5 0.8873 rank 13 Tier 3 —
OK. Tier 1 is the five 3.7 / 3.8 cells, so "Tier 2 or below" holds.

**R4-22.** Quote matches line 572. Counted from HEAD and BASE
`tiering_20m.json` (74 `-opmax` ids in the ranking; significant and
positive against the reference cell): BASE 59 / 74 below the lowest Tier-1
cell, 73 / 74 below the top; HEAD 70 / 74 and 74 / 74 — OK.

**R4-23.** Quote matches line 573. Lowest Tier-1 cell
(`g37-text-k10-verified-carried-p0.10-k10`) against `pv-high-text-t0.3-n5-opmax`:
BASE +0.019453, p 0.1783, BH 0.219777; HEAD +0.029552, p 0.0381, BH
0.052506; against tier E K = 5: BASE +0.016301, p 0.2505; HEAD +0.012265,
p 0.3931, BH 0.449539 — all OK; wording roundings (+0.030, 0.038, 0.053;
+0.012, 0.39) OK.

**R4-24.** Quote matches line 574. Top cell against the HIGH text cell:
BASE +0.035949, p 0.0158, BH 0.023433; HEAD +0.045872, p 0.0016, BH
0.002696; against tier E K = 5: BASE +0.032796, p 0.0112, BH 0.016994; HEAD
+0.028586, p 0.0304, BH 0.042454 — all OK. (The inventory's anchor BH
0.0284 predates the 2026-09-13/14 rebuilds; BASE 0.0234 is right.)

**R4-28.** Quote matches line 578. BASE `results/run-analyses.json` →
`signature.signed_at` 2026-09-16T02:58:00Z — OK. HEAD: `signature.status`
**re-sign-pending**, `signed_at` null (since `92a66089d`) — the column's
"register still reads signed" is stale; the wording is right.

### Restating

**R1b-02.** Quote matches line 273. `results/grid-2026-08-18/grid_analysis.json`
→ `contrasts`: BASE 0.12001 / 0.13482 / −0.08239 / −0.09719; HEAD 0.12072 /
0.13807 / −0.08030 / −0.09764; every HEAD CI excludes zero — OK. (The
claim's "paired tile bootstrap" now labels only the CIs; p is permutation.)

**R1b-03.** Quote matches line 274. `interaction`: BASE −0.01481 [−0.0552,
+0.0268], p 0.4681; HEAD −0.01735 [−0.0580, +0.0248], p 0.4033 — OK.

**R1b-04.** Quote matches line 275. `corroboration_profile.share_corroborated`
0.0698 / 0.0773 / 0.4079 / 0.4171 at both — OK. HEAD sweep K = 10 c ≥ 2
k ≥ 1: recall 0.8785 (512/50) and 0.9089 (384/50) → "0.88–0.91"; precision
0.1590 → 0.5364 (512) and 0.1250 → 0.3744 (384) — OK; BASE values from BASE
grid `findings.md` lines 117–120 — OK.

**R1b-05.** Quote matches line 276. Best K = 10 per cell from `sweep`:
BASE 0.75176 / 0.72052 / 0.67594 / 0.64752; HEAD 0.76112 / 0.72926 /
0.68449 / 0.65743 — OK; order unchanged.

**R1b-06.** Quote matches line 277. HEAD
`cost_efficiency.passes_versus_overlap`: union recall 0.91121 vs 0.94159,
best F1 0.65743 vs 0.75000, Δrecall −0.03037, ΔF1 −0.09257, flex $2.906 vs
$1.602 — OK. BASE frontier: 0.8925 / 0.6475; 0.9229 / 0.7429 — OK.

**R1b-07.** Quote matches line 278. `frontier` K = 1 512/50: BASE 0.7121,
HEAD 0.7186 ($0.534); K = 10 12.5 % cells 0.6845 ($1.902) and 0.6574
($2.906) — OK.

**R1b-08.** Quote matches line 279. `verifier_analysis.json` → `board_best`:
BASE 0.83107 / 0.88148 / 0.86768 (0.20, k7) / 0.89614; HEAD 0.83681 /
0.88698 / 0.87610 (0.15, k7) / 0.90168; `conditions` registered
`g384-ov048-k10-verified-p0.20-k7` rescored 0.8752 — OK.

**R1b-10.** Quote matches line 281. Baseline block BASE p 0.2975 / 0.0939
and verified block p 0.0373 / 0.2353 (→ 0.298 / 0.094 / 0.037 / 0.235);
HEAD −0.02707, p 0.3081; −0.03187, p 0.0862; +0.03929, p 0.0266; +0.01470,
p 0.2454 — OK.

**R1b-11.** Quote matches line 282. `verifier_gain_over_consensus` HEAD
0.1523 / 0.1259 / 0.2187 / 0.1724 → +0.126 to +0.219, 384 px +0.219 and
+0.172 (still the two largest); ceilings from `frontier` K = 10 union
recall: HEAD 0.9112 / 0.9696 against 0.8879 / 0.9603 — OK. Pre-existing
(not the pass's): the consensus-only board's two worst cells are the two
12.5 % cells, not the two 384 px cells; the claim holds only read as "worst
at each overlap".

**R1b-12.** Quote matches line 283. Best points k 5, 9, 7, 10 at HEAD;
`board_pure_verifier_k1` max 0.81869 → 0.8187; lead (board_best − pure)
0.0574–0.2074 → 0.057–0.207; BASE 0.0524–0.2029 — OK.

**R1b-14.** Quote matches line 285. `stride_verifier_analysis.json`:
ladder 0.8761 / 0.9075 / 0.9017 / 0.8938 at HEAD; `ladder384: 256 − 336`
+0.03145 [+0.00569, +0.05769], p 0.0197; `bar: 384/33.3 − grid winner`
+0.00586, p 0.6395; `ladder384: 144 − 256` −0.01373, p 0.2231;
`rung144` −0.00786, p 0.4807; BASE p 0.0215 / 0.8662 / 0.2837 / 0.3522 —
all OK.

**R1b-17.** Quote matches line 288. `plateau_analyses.json` →
`winner_ladder_exact` HEAD 0.87367 / 0.89926 / 0.89372 (all-in $1.38 /
$2.64 / $3.81), K = 10 0.90754 ($6.56); gap 0.00828 (BASE 0.0071). Board
frame (`results/k-ladder-2026-09-12/board-frame/stride-phaseb__g384-ov128-*/evaluation.json`,
20 m): BASE 0.8605 / 0.8834 / 0.8782 / 0.8905; HEAD 0.8665 / 0.8916 /
0.8862 / 0.8999; tax −0.0072 / −0.0077 / −0.0075 / −0.0076 — OK. 2.64 /
6.56 = 40 %; 50 / 2.64 ≈ 19 — OK.

**R3-11.** Quote matches line 459. `results/k-ladder-2026-09-12/phase2/ladders.json`
(opmax `f1_20`, `all_in_flex_usd`): 3.7 GS K = 5 → 10 BASE 0.9066 → 0.9068
for $8.68 (US$43.4 per 0.001); HEAD 0.9165 → 0.9169 (US$21.7) — OK.
`summary.share_at_k3` 3.7: 0.6545 → 0.8029 (clipped) — OK. GS stride A
(`ladders.json`, grid-common frame) 0.767 → 0.757 (77 % → 76 %; the
re-score's 76 % → 75 % is the board frame) — OK. Phase 2 shares stay in
0.372–0.915; MINIMAL image T 0.7 (0.552 → 0.530) and HIGH text T 1.0
(0.735 → 0.724) also move (clipped), unlisted but inside the range. Cost
shares unchanged. Last-step-dearest count re-derived for the 14 Phase 2
ladders (12, with the same two exceptions), GS stride A (still an
exception: its K = 3 → 5 step loses F1, −0.0056) and tier E (its K = 5 → 10
step loses F1 at both revisions, 0.8905 → 0.8886 and 0.9046 → 0.8942, so it
stays among the 17); the 55-map ladders are untouched — 17 of 23 holds.
The range's upper end: item 1.

**R3-13.** Quote matches line 461. `mcc-test/summary.json` → `gs-stride-a`:
BASE 0.013419, BH 0.7678; HEAD 0.013043, BH 0.76332 — OK (+0.0130, 0.7633).

**R3-14.** Quote matches line 462. `tension/grid-overlap.json` g384_ov192:
BASE K = 1 0.663304, K = 10 0.720524, ΔMCC 0.044361; HEAD K = 10 0.729258
(+0.065954), ΔMCC 0.044361. `tier-e/ladder.json`: BASE 0.8546 / 0.8886,
MCC 0.8211 / 0.7903; HEAD 0.8680 / 0.8942, MCC 0.8211 / 0.7973. Exact:
K = 10 F1 752 / 841 = 0.894173 (n 406, P 0.9261, 435 references); MCC from
the tile tables (191/246/12/38 and 196/247/11/33) 0.797257 and 0.821093,
Δ −0.023837, swing 0.068198; share 60.33 % — all OK. Attribution: item 8.

**R3-15.** Quote matches line 463. `phase2/ladders.json` summary MINIMAL
image T 0.7 gain 0.0629 → 0.06 (clipped; `historical_as_evaluated` 0.0629);
GS stride A +0.0305 → +0.0338 (grid-common frame) with BH p 0.0072 → 0.0024
(the board-frame test, `mcc-test/summary.json`, where ΔF1 is 0.0300 →
0.0334; the findings § 8.2 table pairs them the same way); deployment
+0.0192 / +0.0547 unchanged — OK; still inside.

**R6-16.** Quote matches line 725. 3.7 step as R3-11; HIGH text T 1.0
K = 5 → 10 BASE +0.0116, HEAD +0.0117 (clipped) for $12.23 → US$1.05 — OK;
55-map stride B US$17 unchanged (findings § 5).

**R6-17.** Quote matches line 726. As R3-14 — OK.

**R4-04.** Quote matches line 554. Champions `tiering_20m.json` rank 1:
BASE 0.814118, HEAD 0.816471; `family_fdr.md` rider 0.076083 → 0.073730 —
OK. Wording "0.817" → 0.816 (item 3).

**R4-19.** Quote matches line 569. Board README rows 1–5 HEAD 0.9332 /
0.9289 / 0.9282 / 0.9278 / 0.9169, same ids and order as BASE (0.9233 /
0.9190 / 0.9182 / 0.9179 / 0.9068); row 4 is the carried arm's registered
(0.10, k5) set — OK.

**R4-25.** Quote matches line 575. `optimism/README.md` board-frame rows:
BASE +0.0006 to +0.0035, corrected 0.9027 to 0.9215; HEAD +0.0008
(text K = 5 carried) to +0.0039 (grid verified37), corrected 0.9104 (grid
verified37) to 0.9314 (image swap37) — OK. Two HEAD board rows have no
gate ("—"): the image carried arm (argmax 0.9306 against the board cell's
0.9278) and grid verified37 (0.9144 against 0.9141), so their corrected
values are from the argmax.

**R7.3-01.** Quote matches line 1005. `results/gemini37-screen-2026-08-28/analysis.json`
→ `image_best` BASE 0.91389 (0.10, k5); HEAD 0.92378 (0.10, k5), 451
detections; union 791 (`gemini38-screen-2026-09-04/armV/pair_test.json`
`union`) — OK. Unanimity 59 % and ~$7.4: UNCHECKED (proposer-side, no
regenerated artefact; not plausibly moved).

**R7.3-04.** Quote matches line 1008 (a fragment). `head_to_head_20m` BASE
−0.017757, p 0.1697; HEAD −0.022098, p 0.0971 → +0.022, p 0.097 — OK.
Deployment figures (arm 1 0.8494, p 0.35, MDE80 0.013): the
`gemini37-55map-grid-2026-08-31` row is still signed and untouched — OK.

**R7.3-11.** Quote matches line 1015. `armV/pair_test.json` → `all-3.7`:
BASE −0.000693, p 0.7769, null SD 0.00379; HEAD 0.935823 vs 0.936416,
−0.000594, p 0.7769, null SD 0.003745; 2.8 σ 0.010486 → "about 0.010" — OK.

**R7.3-12.** Quote matches line 1016. Board README row 3 HEAD 0.9282, Tier 1
— OK. 76 / 106 tokens and ~$0.85: UNCHECKED beyond the restated register
outcome, which keeps "76 … against … 106".

**R7.3-21.** Quote matches line 1025. `arm1/analysis.json` → `image_best`
BASE 0.92541 (0.10, k5), HEAD 0.93807 (0.05, k5); `arm2/analysis.json`
0.93083 → 0.94077 (0.90, k5); registered (0.10, k5) 0.9353 (findings line
32); anchor `image-b-gs-2026-08-28/analysis.json` → `image_best` 0.84121 →
0.84578; gains +0.0923 / +0.0950; text-side gain +0.0221; ratios 4.2 and
4.3 — OK.

**R7.3-22.** Quote matches line 1026. `gemini37-image-gs-2026-09-01/gap_test.json`:
G3 gap 0.0549, p 0.001 → 0.0559, p 0.0005; carried −0.011516, p 0.2533 →
−0.014296, p 0.158; all-3.7 −0.004345 → **−0.00435** (−0.0044), p 0.6767.
Bridge `modality-bridge-2026-10-07/gap_test.json`: g3 +0.052332, p 0.0029 →
+0.053618, p 0.0018; carried −0.000584, p 0.9467 → −0.002581, p 0.766;
all-3.7 −0.002334 → −0.002315, p 0.7477. `floors/gap_change.json` −0.05292 /
−0.05467 → −0.05620 / −0.05593; interaction p 0.0060 / 0.0031 (bridge
findings lines 101–102, 181–182) — all OK apart from the rounding.

**R7.3-24.** Quote matches line 1028. 0.940767 vs 0.936416, +0.00435
(+0.0044), p 0.6767; `sensitivity-mde-2026-08-28/sensitivity-mde.md`
line 116 MDE80 0.024301 → 0.024632 (0.025) — OK apart from the rounding.

## § 6.2 spot-checks (rows said to hold)

| Row | Check | Result |
|---|---|---|
| R0-05 | HEAD board `tiering_20m.json`: `n_permutations` 10000, `seed` 42, `fdr_q` 0.05 | holds |
| R1-11 | same file `buffer_metres` 20, `n_tiles` 487 | holds |
| R1b-01 | `grid_analysis.json` `configuration` unchanged; `costs.total_calls` 30130, `total_flex_usd` 18.5302 | holds |
| R1b-13 | `stride_verifier_analysis.json` iso contrasts HEAD p 0.1392, 0.2448, 0.8626, 0.0839, 0.7851 (smallest 0.084); 384 px at or above at 192, 256, 336 | holds |
| R1b-18 | `plateau_analyses.json` `k_curves`: g384_ov128 0.15, best 8, [6, 7, 8, 9]; g384_ov192 0.15, best 10, [10] | holds |
| R1b-22 | 580 verifier-sweep rows (120–160 per cell) against 30 consensus K = 10 rows per cell: 4–5.3× | holds |
| R2-09, R2-10, R2-11, R3-01, R4-03 | `results/family-fdr/family_fdr.json` unchanged BASE → HEAD (only the `.md` changed); H1 0.125, H4 0.191, H5 / H8 0.834, H7 0.00047, H2 / H3 0.00035 | hold |
| R3-02 | champions lifts +0.4294 (0.8165 − 0.3871) to +0.1291 (0.6825 − 0.5534) | holds (+0.13 to +0.43) |
| R3-12 | `mcb/summary.json` roll-up HEAD: K = 3 in 12 F1 sets; no set excludes K = 10; K = 1 MCC-admissible on 22 | holds on the not-re-run Phase 2 tests (note 5) |
| R4-12 | anchor 0.814 → 0.816471 | claim status as before; § 6.2's "0.817" should read 0.816 |
| R4-27 | HEAD README Δ frame −0.0070 to −0.0079 for the B-geometry and screen cells, +0.0000 for every incumbent | holds |
| R6-18 | claim holds (ladder grain); note's board grain | **note fails in part** (item 4); MCB overlap 9 of 52 and 60 |
| R7.3-03 | HEAD register `gemini37-fourth-cell-gs-leg-2026-08-31`: 0.9220 at (0.98, k10) | holds |
| R7.3-20 | Tier 1 = the five 3.7 / 3.8 cells; the fourth cell (Gemini 3 proposer) rank 7, Tier 2 | holds |
| R7.3-23 | Gemini 3 gap +0.0559, p 0.0005; 3.7 gaps −0.0143 (p 0.158), −0.0044 (p 0.677); bridge +0.0536 (p 0.0018) against −0.0026, −0.0023 | holds |

Fifteen rows across all groups were checked; fourteen hold and R6-18's note
partly fails. R4-12's claim text still holds, but its restated anchor value
is mis-rounded.

## Other observations on § 6.3

- Note 1, the grid Phase A paragraph: min6 against the winner BASE
  +0.0339, p 0.0196 → HEAD +0.0226, p 0.1107
  (`incumbents_common_footprint.json`) — confirmed.
- Note 5's widths: `mcb/gs-stride-a` `hsu_w_upper` 0.0160 → 0.0168 and
  `mcb/tier-e` 0.0151 → 0.0159 — confirmed.
- Note 6's registered-against-argmax pairs — confirmed (stride findings
  changelog; gemini37-image findings line 32; optimism README).
- Note 2 / S7 (fourth cell p 0.0563 → 0.0311): confirmed in the restated
  register outcome; I found no claim row quoting it.
- Completeness: a search of every inventory claim for 60-odd moved values
  found no further row whose claim text quotes a moved value. Only R4-12's
  anchor and R6-18's note were missed, and both are listed in § 6.2.
