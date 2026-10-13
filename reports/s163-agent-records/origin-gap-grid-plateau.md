# D62 (1): the origin gap in the grid, plateau, and Image-B chains (re-scored, not published)

> **Last revised**: 2026-10-13 (original publication). See
> [§ Changelog](#changelog) for revision history.

- **Executed by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), an overnight subagent of the main Session 163
  session (workstream `origin-gap-grid-plateau`). Every number below was
  read from the run records in
  [`origin-gap-grid-plateau-scripts/`](origin-gap-grid-plateau-scripts/)
  or from the committed artefacts at `33b96d22b`.
- **Date**: 2026-10-13 (UTC).
- **Repository**: `map-reader-llm`, branch `origin-gap-grid-plateau` from
  `origin/main` at `33b96d22b`; the route fix is commit `11a0bd980`.
- **Ruling**: principal investigator (PI) ruling D62 (1) (`planning/pi-decisions-2026-09-20.md`):
  fix the route so each cluster carries its contributing tiles into
  scoring, rebuild clusters from the passes where pooled results record no
  members, re-score the affected boards on sapphire, and report how they
  move before any document or signature changes. The finding it rules on
  is § 3 and § 9.3 of `reports/s163-agent-records/scorer-restatement-inventory.md`
  (branch `scorer-restatement-sweep`, PR #39), reproduced on `main` in
  `reports/s163-agent-records/plateau-recorded-sheet-check-2026-10-13/`.
- **Scope**: the gold-standard (GS) grid, stride, plateau, and Image-B
  chains. The H13 chain and the library copies (`prepare_h13_scoring.py`,
  `h13_*`, `lib_consensus`, `analyse_diversity.py`, W2.7) belong to another
  workstream and were not edited; `h13_k_sensitivity.cluster_votes` is
  imported, never changed.
- **Guarantees**: no model Application Programming Interface (API) call;
  nothing merged; no committed result, document, or register row
  regenerated or edited; sapphire's shared checkout read only (the
  verifier crops in § 7 were read there, never written); at most three
  chain processes at a time against a budget of five.

## Bottom line

1. **The route is fixed.** Every scored detection in the four chains now
   carries the tiles it was seen on into
   `lib_advanced_metrics.assign_primary_tiles_on_origin_sheet` and the
   shared scorer. Committed verified unions, which record no members, are
   rebuilt from their passes under a row-for-row gate and get their
   members attached without disturbing the verifier's candidate keys. The
   four plateau incumbents keep the `source_tile` their files record.
2. **The plateau verdict survives; two of its sentences do not.** The
   13-cell board is still two tiers, twelve cells and 512 px / 12.5 %
   alone, with every significant pair involving 512 px / 12.5 %, but
   there are **8 of 78** significant pairs, not 6. The four incumbents
   rise by +0.0072 to +0.0168 F1 at 20 m (exactly the independent
   reproduction's values), and at 30 m the high-thinking `opmax`
   incumbent now scores **0.9173**, above the geometry cells' 0.9031 and
   0.9034, so "at 30 m the top three are indistinguishable" (R1b-15) and
   "the HIGH-thinking incumbents share the 30 m shelf" (R1b-16) fail.
3. **The consensus-only grid board moves; its verdict survives.** Every
   K = 10 cell gains +0.0086 to +0.0099 F1 and the K = 10 union recall
   gains 0.016 to 0.019, but the ranking (R1b-05) and the single-pass and
   passes-versus-overlap verdicts (R1b-02, R1b-03, R1b-06, R1b-07) stand.
4. **No verified board moves, and the reason is a second defect.** The
   grid's post-verifier board (R1b-08), the stride board, the exact winner
   ladder (R1b-17), the k-curves (R1b-18), and Image-B are unchanged
   except one Image-B HIGH ladder rung. **The legacy re-key also sent
   every re-keyed union candidate's verifier crop to the neighbouring
   sheet's raster, past the edge of its map**: those crops are 59 % to
   100 % black no-data (other crops: 0.18 % to 0.35 %), and the verifier
   gave 331 of the 332 a probability below 0.15 and the last exactly 0.15
   (other candidates: 15 % to 41 % at or above it). The scoring fix
   cannot repair those probabilities; only re-verification on crops cut
   from the origin sheet can (§ 7, for the PI). If every such candidate
   had been verified a mound, the boards' best points would gain at most
   +0.0025 to +0.0098 F1.
5. **Integrity.** Two fixed runs agree byte for byte except timestamps;
   a legacy control at `33b96d22b` reproduces every committed score; the
   two outputs the branch now computes but the committed files carried
   by hand (the exact winner ladder and the Image-B N3-versus-N10 test)
   replay to the committed values on the legacy path; the kernel
   bad-page count was 0 before and after.

## Verdicts

| Claim | What it says | Before | After (fixed, twice) | Verdict |
|---|---|---|---|---|
| R1b-05 | K = 10 consensus-only ranking: 512/50 > 384/50 > 512/12.5 > 384/12.5 | 0.7518 / 0.7205 / 0.6759 / 0.6475 | 0.7611 / 0.7293 / 0.6845 / 0.6574 | Survives; numbers restate |
| R1b-08 | Post-verifier ranking: 384/50 > 512/50 > 384/12.5 > 512/12.5 | 0.8961 / 0.8815 / 0.8677 / 0.8311 | unchanged | Survives as a number, but conditional on § 7 |
| R1b-15 | Plateau, not winner: 6 of 78 pairs significant, all with 512/12.5; Tier 1 the other twelve; at 30 m the top three indistinguishable | 6 of 78; tiers 12 + 1; 30 m: 0.9034 / 0.9031 / 0.9031 | 8 of 78, all with 512/12.5; tiers 12 + 1, same membership; 30 m: `opmax` 0.9173 against 0.9034 / 0.9031 | Plateau verdict survives; "6 of 78" becomes 8; the 30 m sentence fails |
| R1b-16 | Geometry bought cost, not F1; the HIGH-thinking incumbents share the 30 m shelf | `opmax` / headline at 30 m: 0.9031 / 0.8958 | 0.9173 / 0.9054 | Cost claim survives at 20 m; "share the 30 m shelf" fails (both now above it; no 30 m test exists) |
| R1b-17 | Exact winner ladder 0.8677 / 0.8911 / 0.8856 / 0.8982 | as stated | unchanged | Survives, conditional on § 7 |
| R1b-18 | k-curves: A argmax k = 8, flat top 6–9; B argmax k = 10 | as stated | unchanged | Survives |
| Image-B (signed) | IP1–IP4 confirmed (+0.0549 at 20 m, p = 0.0010; gap 0.0549 → 0.0258; tile Matthews correlation coefficient (MCC) 0.7985 against 0.7965; probability 0.15); IP5 indeterminate (N3 − N10 −0.0159, p = 0.0689); HP1–HP5 | as stated | unchanged; HIGH N5 rung 0.8331 → 0.8348; HIGH N5 − N10 p 0.9683 → 0.9073 | Survives, conditional on § 7 |

Secondary claims: R1b-02 and R1b-03 (single-pass contrasts and
interaction), R1b-06 and R1b-07 (passes against overlap), R1b-09 and
R1b-10 (post-verifier contrasts and the consensus baseline), R1b-11
(verifier gain), and R1b-12 (pure verifier) all keep their verdicts; § 4
and § 5 give the moved numbers. One unnumbered passage does not survive:
the grid findings' Phase A paragraph
(`results/grid-2026-08-18/findings.md:432-455`) says the grid's stride-192
cell is "the point-estimate leader at both buffers and statistically
clears min6"; after the fix `opmax` ties it at 20 m (+0.0002, p = 0.9858)
and leads at 30 m, and min6 is no longer cleared (p 0.0196 → 0.2383).

## 1. The route fix

`scripts/lib_cluster_origins.py` (new) supplies the link the chains
lacked:

- `cluster_votes_with_members` is `h13_k_sensitivity.cluster_votes`
  statement for statement (greedy star clustering at 20 m, centroid the
  member mean, votes the distinct passes) and also returns each cluster's
  member tiles, the union of its members' recorded `source_tiles`. A
  tier-1 test pins its centroids and votes equal to `cluster_votes` at
  four corroboration levels.
- `points_on_origin` and `tile_on_origin` record each point's origin in
  `origin_tiles` (one of the scorer's `ORIGIN_TILE_COLUMNS`) and book it to
  the nearest carrier tile on its own sheet; a point on no tile of its
  own sheet is dropped, as the D50 scorer drops it.
- `attach_union_origins` and `union_on_origin` serve the committed
  verified unions. Each union is rebuilt from the passes it was clustered
  from, filtered by the legacy rule it was written under, and gated row
  for row: count, per-row `vote_count`, and centroid within 1 mm (the
  measured round-trip displacement through EPSG:4326 is about 2 nm). The
  members are then attached to the committed rows, whose order is the
  verifier's `candidate_NNNNN` key.

Every committed union in the four chains passes that gate, and none loses
a row to the origin rule (no re-keyed row lies off its own sheet's tiles):

| Union | Rows | Rows the legacy rule re-keyed |
|---|---:|---:|
| grid 512/12.5, 512/50, 384/12.5, 384/50 (K = 10) | 1,402 / 2,585 / 1,827 / 3,319 | 25 / 29 / 14 / 22 |
| stride 512/34.4, 384/33.3, 256/25, 512/62.5, 384/62.5 (K = 10) | 1,981 / 2,387 / 3,570 / 3,778 / 5,250 | 24 / 11 / 22 / 38 / 19 |
| winner ladder 384/33.3, N = 1, 3, 5 | 1,290 / 1,700 / 1,968 | 11 / 11 / 11 |
| Image-B MINIMAL and HIGH (K = 10) | 4,065 / 9,189 | 31 / 64 |

The callers changed: `grid_analysis.as_gdf` (takes `origins`; its
single-pass, per-tile, and sweep paths pass them),
`materialise_grid_unions.union_with_votes` (and through it the stride and
Image-B materialisers),
`grid_materialise_conditions.py`, `grid_verifier_analysis.py` (and its
`materialise_condition` writes `origin_tiles`), `stride_verifier_analysis.py`,
`stride_plateau_analyses.py`, `materialise_winner_ladder.py`,
`grid_incumbent_rescore.py`, `image_b_analysis.py`, `image_b_pair.py`, and
`selection_aware_intervals.py`'s `--cell` path. Two outputs that were
folded into committed artefacts by hand now have a generator:
`stride_plateau_analyses.winner_ladder_exact` and Image-B's
`saturation_N3_vs_N10`. `image_b_pair.py` names its union, because the
MINIMAL cell's directory gained K = 3 and K = 5 unions after 2026-08-28 and
the old glob refused to load it.

**Tests** (`tests/test_lib_cluster_origins.py`, new; additions to
`tests/test_grid_analysis.py`, `tests/test_materialise_grid_unions.py`, and
`tests/test_grid_verifier_analysis.py`): the clustering equality, the
overlap point kept on its origin sheet, the off-sheet point dropped, the
rebuild gate refusing a union with a row dropped, a vote changed, or a
centroid moved, and two real-data sentinels: the g512_ov064 K = 10 union
rebuilt by `union_with_votes` equals its committed geometry and votes, with
exactly 25 rows changing tile; and the four incumbents score 0.895981 /
0.891018 / 0.884236 / 0.879042 at 20 m (the reproduction's
`output.txt`), while the legacy bare-centroid path still gives the
committed board's F1. A copied (not linked) harness confirmed the tests go
red under five deliberate breakages: the incumbents' origin removed, votes
counted per member, the union built without members, the rebuild gate
disabled, and `as_gdf` ignoring its origins.

## 2. How the boards were re-scored

Three disposable copies under `~/scratch/scorer-restatement-sweep-2026-10-12/ogp/`
on sapphire, each a `git archive` of the inputs, scripts, and results the
chain reads (565 MB each): `runA` and `runB` at `11a0bd980` (the fix),
`runL` at `33b96d22b` (the legacy control). `tools/chain.sh` ran, one
process per copy, single-threaded:
`grid_analysis.py --bootstrap 10000` → `grid_materialise_conditions.py` →
`grid_verifier_analysis.py --materialise-conditions` →
`stride_verifier_analysis.py` → `grid_incumbent_rescore.py` →
`image_b_analysis.py` (MINIMAL, then HIGH) → `image_b_pair.py` →
`stride_plateau_analyses.py`. Each step regenerates the files the next
reads, so every board saw the fixed upstream. The fixed runs pass the
re-scored text-B F1 as Image-B's anchor (it did not move: 0.8961352657).
`image_b_pair.py` was not run in the legacy copy: at `33b96d22b` it cannot
load the MINIMAL union (the glob defect above).

- **runA against runB**: of 92 output files, 71 are identical byte for
  byte and the other 21 differ only in their `generated_at_utc` and
  `timestamp` fields or, for the eight evaluation renders, their
  `Generated` line (`integrity-runA-vs-runB.txt`). The extracted numbers
  and the § 7 measurements are byte-identical files.
- **runL against the committed files**: every scored number reproduces.
  All 114 CSV and GeoJSON outputs are byte-identical; the JSON
  differences are timestamps, the provenance and D50 `detection_scope`
  blocks the evaluator now writes, `grid_analysis.json`'s
  `verifier_costing` (its cost-model input changed after 2026-10-05; not a
  score), and the two hand-folded outputs the legacy scripts never wrote
  (`integrity-runL-vs-committed*.txt`). So every before → after below is
  the fix alone.
- **The hand-folded outputs**: `tools/legacy_extras.py`, run in both fixed
  copies before the chain, replays the new `winner_ladder_exact` and the
  Image-B N3-versus-N10 test with the origin step removed; both reproduce
  the committed values exactly, in both copies.
- **Memory integrity**: `journalctl -k -b | grep -c -i "bad page"` was 0
  before (04:23 UTC) and after (04:52 UTC) the runs.

## 3. The plateau board (claims R1b-15 to R1b-18)

`results/stride-2026-08-25/plateau_analyses.json`, `board_13cell`: F1 at
20 m, tile-swap permutation (10,000, seed 42), Benjamini–Hochberg (BH)
q = 0.05, greedy cliques. Only the incumbents move; the nine geometry
cells are verified sets, unchanged for the reason in § 7.

| Rank after | Cell | F1 before | F1 after | Tier before → after |
|---:|---|---|---|---|
| 1 | g384_ov128 | 0.8982 | 0.8982 | 1 → 1 |
| 2 | g384_ov192 | 0.8961 | 0.8961 | 1 → 1 |
| 3 | opmax | 0.8842 | 0.8960 | 1 → 1 |
| 4 | headline | 0.8838 | 0.8910 | 1 → 1 |
| 5 | g384_ov240 | 0.8860 | 0.8860 | 1 → 1 |
| 6 | min11 | 0.8719 | 0.8842 | 1 → 1 |
| 7 | g512_ov256 | 0.8815 | 0.8815 | 1 → 1 |
| 8 | g512_ov320 | 0.8800 | 0.8800 | 1 → 1 |
| 9 | g256_ov064 | 0.8795 | 0.8795 | 1 → 1 |
| 10 | min6 | 0.8623 | 0.8790 | 1 → 1 |
| 11 | g384_ov048 | 0.8677 | 0.8677 | 1 → 1 |
| 12 | g512_ov176 | 0.8655 | 0.8655 | 1 → 1 |
| 13 | g512_ov064 | 0.8311 | 0.8311 | 2 → 2 |

**Significant pairs: 6 → 8 of 78.** The two new ones are min11 against
g512_ov064 (Δ 0.0408, p = 0.0194 → Δ 0.0532, p = 0.0018) and min6 against
g512_ov064 (0.0312, p = 0.0766 → 0.0480, p = 0.0042). All eight still
involve g512_ov064, so "plateau, not winner" holds. The leader's margins
over the incumbents shrink: g384_ov128 against `opmax` 0.0140, p = 0.2908
→ 0.0022, p = 0.87; against min6 0.0359, p = 0.0049 → 0.0191, p = 0.1377.

**The 30 m shelf (R1b-15, R1b-16).** The Phase A rescore
(`results/grid-2026-08-18/incumbents_common_footprint.json`) supplies the
incumbents' 30 m values; the geometry cells' come from the stride board
(unchanged: 384/33.3 0.9031, 384/50 0.9034).

| Incumbent | F1 @ 20 m | F1 @ 30 m | Tile MCC @ 20 m | Grid winner − incumbent @ 20 m (p) |
|---|---|---|---|---|
| opmax (16-of-30 HIGH, n = 5 verifier) | 0.8842 → 0.8960 | 0.9031 → 0.9173 | 0.8255 → 0.8177 | +0.0120 (0.3523) → +0.0002 (0.9858) |
| headline (16-of-30 HIGH, n = 1 verifier) | 0.8838 → 0.8910 | 0.8958 → 0.9054 | 0.8139 | +0.0123 (0.3128) → +0.0051 (0.6789) |
| min11 (MINIMAL 6-of-10) | 0.8719 → 0.8842 | 0.8892 → 0.9015 | 0.8040 → 0.8002 | +0.0242 (0.0894) → +0.0119 (0.401) |
| min6 (MINIMAL 3-of-5) | 0.8623 → 0.8790 | 0.8743 → 0.8910 | 0.7887 → 0.7848 | +0.0339 (0.0196) → +0.0171 (0.2383) |

At 20 m the shelf is unchanged (~0.896–0.898, now with `opmax` on it).
At 30 m `opmax` (0.9173) leads the best geometry cell (384/50, 0.9034) by 0.0139, and the
headline (0.9054) leads it by 0.0020; no paired test exists at 30 m, so
"above the shelf" is a point estimate.

**Unchanged**: the k-curves (R1b-18: g384_ov128 argmax k = 8 with 6–9
within 0.005; g384_ov192 k = 10), the exact winner ladder (R1b-17: 0.8677 /
0.8911 / 0.8856 at N = 1, 3, 5; all-in $1.38 / $2.64 / $3.81), and the
inherited first-N ladder for all nine cells.

## 4. The GS grid, consensus-only (claims R1b-02 to R1b-07)

`results/grid-2026-08-18/grid_analysis.json`, `sweep.csv`, and the
registered conditions under `conditions/` (evaluated at B = 10,000; CI95
is the evaluator's 95 % bias-corrected and accelerated, BCa, bootstrap
interval). The best operating point of every cell is unchanged; every F1
rises.

| Cell | Operating point (c, k) | F1 @ 20 m | Precision | Recall | Tile MCC | Registered CI95 |
|---|---|---|---|---|---|---|
| 512 px / 12.5 % | c ≥ 1, k ≥ 8 | 0.6759 → 0.6845 | 0.6233 → 0.6312 | 0.7383 → 0.7477 | 0.5383 → 0.5431 | [0.6239, 0.7237] → [0.6336, 0.7313] |
| 512 px / 50 % | c ≥ 2, k ≥ 8 | 0.7518 → 0.7611 | 0.7535 → 0.7629 | 0.7500 → 0.7593 | 0.5897 → 0.5853 | [0.7026, 0.7938] → [0.7126, 0.8023] |
| 384 px / 12.5 % | c ≥ 1, k ≥ 10 | 0.6475 → 0.6574 | 0.5619 → 0.5704 | 0.7640 → 0.7757 | 0.3137 → 0.3066 | [0.5935, 0.6966] → [0.6038, 0.7056] |
| 384 px / 50 % | c ≥ 2, k ≥ 10 | 0.7205 → 0.7293 | 0.6762 → 0.6844 | 0.7710 → 0.7804 | 0.4909 | [0.6749, 0.7618] → [0.6841, 0.7686] |

| Cell | Single-pass F1 (mean of ten) | Single-pass tile MCC | K = 10 union recall | K = 10 union F1 |
|---|---|---|---|---|
| 512 px / 12.5 % | 0.5871 → 0.5956 | 0.4415 → 0.4484 | 0.8715 → 0.8879 | 0.4077 → 0.4153 |
| 512 px / 50 % | 0.4672 → 0.4750 | 0.3096 → 0.3255 | 0.9416 → 0.9603 | 0.2675 → 0.2728 |
| 384 px / 12.5 % | 0.5049 → 0.5155 | 0.1452 → 0.1555 | 0.8925 → 0.9112 | 0.3388 → 0.3459 |
| 384 px / 50 % | 0.3700 → 0.3773 | 0.2321 → 0.2404 | 0.9509 → 0.9696 | 0.2172 → 0.2215 |

| Single-pass contrast (B = 10,000) | ΔF1 | CI95 | p |
|---|---|---|---|
| overlap at 512 px (12.5 % − 50 %) | +0.1200 → +0.1207 | [+0.0872, +0.1531] → [+0.0874, +0.1543] | 0.0 → 0.0 |
| overlap at 384 px (12.5 % − 50 %) | +0.1348 → +0.1381 | [+0.1058, +0.1636] → [+0.1085, +0.1671] | 0.0 → 0.0 |
| tile size at 12.5 % (384 − 512) | −0.0824 → −0.0803 | [−0.1243, −0.0429] → [−0.1236, −0.0394] | 0.0002 → 0.0005 |
| tile size at 50 % (384 − 512) | −0.0972 → −0.0976 | [−0.1196, −0.0753] → [−0.1206, −0.0752] | 0.0 → 0.0 |
| interaction (difference of differences) | −0.0148 → −0.0173 | [−0.0552, +0.0268] → [−0.0580, +0.0248] | 0.4681 → 0.4033 |

- **R1b-05** (ranking 512/50 > 384/50 > 512/12.5 > 384/12.5): survives.
- **R1b-02, R1b-03**: all four contrasts still exclude zero with the same
  signs; the interaction is still unresolved.
- **R1b-06** (passes do not substitute for overlap): 384/12.5 at K = 10
  (union recall 0.8925 → 0.9112, best F1 0.6475 → 0.6574) still loses to
  512/50 at K = 3 (0.9229 → 0.9416, 0.7429 → 0.7500); the union-recall gap
  stays 0.0304 and the F1 gap goes 0.0953 → 0.0926.
- **R1b-07**: one pass of 512/50 (best F1 0.7121 → 0.7186) still beats ten
  passes of either 12.5 % cell (0.6845, 0.6574).

All the movement comes from detections seen on one sheet and booked to
its neighbour (§ 7 names the edge). The union-recall gain shows that
about eight mounds were reachable only through those detections.

## 5. The GS grid, post-verifier (claims R1b-08 to R1b-12)

`results/grid-2026-08-18/verifier_analysis.json`: the board, the
post-verifier contrasts, the interaction, the pure-verifier board, and
the four registered verified conditions and their evaluations are
unchanged to the last digit. What moves is the consensus-only side
those values are compared with:

| Like-for-like K = 10 consensus baseline | ΔF1 | p |
|---|---|---|
| overlap at 512 px (12.5 % − 50 %) | −0.0758 → −0.0766 | 0.0008 → 0.0006 |
| overlap at 384 px (12.5 % − 50 %) | −0.0730 → −0.0718 | 0.0032 → 0.0037 |
| tile size at 12.5 % (384 − 512) | −0.0284 → −0.0271 | 0.2975 → 0.3081 |
| tile size at 50 % (384 − 512) | −0.0312 → −0.0319 | 0.0939 → 0.0862 |

| Cell | Verified best F1 (unchanged) | Consensus-only K = 10 best | Verifier gain |
|---|---|---|---|
| 512 px / 12.5 % | 0.8311 | 0.6759 → 0.6845 | +0.1551 → +0.1466 |
| 512 px / 50 % | 0.8815 | 0.7518 → 0.7611 | +0.1297 → +0.1204 |
| 384 px / 12.5 % | 0.8677 | 0.6475 → 0.6574 | +0.2202 → +0.2103 |
| 384 px / 50 % | 0.8961 | 0.7205 → 0.7293 | +0.1756 → +0.1669 |

R1b-09 (overlap reversal survives at about half the margin), R1b-10 (the
baseline tile-size contrasts are both non-significant), R1b-11 (the gain
is largest for the 384 px cells; now +0.120 to +0.210, not +0.130 to
+0.220; the 384 px union-recall ceilings 0.9112 / 0.9696 still exceed
512 px's 0.8879 / 0.9603), and R1b-12 (pure verifier 0.8153) all keep their
verdicts. The p-values the claims quote for the R1b-09 and R1b-10
baselines (0.0004, 0.0026, 0.281, 0.089) differ from the committed file's
(0.0008, 0.0032, 0.2975, 0.0939), which the D42 regeneration wrote
(`5986316b5`, 2026-10-05); the "before" column is the committed file.

## 6. Image-B (signed `image-b-modality-2026-08-28`)

`results/image-b-gs-2026-08-28/analysis.json`, `high/analysis.json`, and
`high/pair_verdicts.json`. Everything the register row and the claims
quote is unchanged: the MINIMAL image best (0.8412 at probability 0.15,
k = 9, MCC 0.7985), the text-B anchor (0.8961), text − image at 20 m
(+0.0549, p = 0.0010), the buffer gaps (0.0549, 0.0379, 0.0282, 0.0258 at
20, 30, 50, 75 m), the ladder (0.6974 / 0.8253 / 0.8382), N5 − N10
(−0.0030, p = 0.745), N3 − N10 (−0.0159, p = 0.0689), and HP1 to HP4
(−0.0079, p = 0.6216; union 4,065 → 9,189; MCC 0.7985 against 0.7993;
(0.15, k9) and (0.20, k8)). IP1 to IP5 and HP1 to HP5 keep their
verdicts.

Two HIGH numbers move: the N = 5 inherited rung, 0.8331 at (0.15, k5) →
0.8348 at (0.10, k5), and with it N5 − N10, −0.0002, p = 0.9683 → +0.0014,
p = 0.9073 ("HIGH saturates by N = 5" stands). The script also now writes
an N3 − N10 test for HIGH, which no committed file holds: −0.0305,
p = 0.0022, on an N = 3 rung the fix did not move. It says HIGH has not
saturated by N = 3; it is new, not a change.

## 7. Surprising: the re-key also blinded the verifier

**This is a second defect, larger in kind than the first, and it is why
no verified board moved.** The union materialisers wrote each cluster's
legacy `source_tile` into the verifier's input, and the crop extractor
cuts each candidate's crop from the raster of the sheet that tile names
(`candidate_manifest.json`: `cropped_from` "raster", `rasters_dir`
`inputs/rasters`). For a re-keyed cluster that is the neighbouring sheet,
and the point lies past the edge of that sheet's map, so the crop is
mostly no-data. Measured on the crops in sapphire's shared checkout
(`tools/rekeyed_verifier_inputs.py`, run on both fixed copies, identical
output):

| Union | Rows | Re-keyed | Highest probability among them | Within 20 m of a mound | Black share of their crops (median; lowest) | Black share, 200 other crops (median) | F1 at best point | If verified as mounds | Bound |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|
| grid/g384_ov048 | 1,827 | 14 | 0.10 | 8 | 1.000; 0.644 | 0.0030 | 0.8677 | 0.8769 | +0.0092 |
| grid/g384_ov192 | 3,319 | 22 | 0.10 | 8 | 1.000; 0.599 | 0.0027 | 0.8961 | 0.9021 | +0.0060 |
| grid/g512_ov064 | 1,402 | 25 | 0.05 | 8 | 1.000; 0.651 | 0.0018 | 0.8311 | 0.8368 | +0.0057 |
| grid/g512_ov256 | 2,585 | 29 | 0.05 | 10 | 1.000; 0.651 | 0.0032 | 0.8815 | 0.8870 | +0.0055 |
| imageb/high | 9,189 | 64 | 0.15 | 12 | 0.994; 0.592 | 0.0035 | 0.8333 | 0.8403 | +0.0070 |
| imageb/min | 4,065 | 31 | 0.05 | 8 | 1.000; 0.638 | 0.0020 | 0.8412 | 0.8438 | +0.0025 |
| stride/g256_ov064 | 3,570 | 22 | 0.10 | 8 | 0.996; 0.598 | 0.0020 | 0.8795 | 0.8848 | +0.0053 |
| stride/g384_ov128 | 2,387 | 11 | 0.10 | 8 | 1.000; 0.644 | 0.0025 | 0.8982 | 0.9078 | +0.0096 |
| stride/g384_ov240 | 5,250 | 19 | 0.10 | 8 | 1.000; 0.612 | 0.0034 | 0.8860 | 0.8933 | +0.0073 |
| stride/g512_ov176 | 1,981 | 24 | 0.05 | 7 | 1.000; 0.651 | 0.0028 | 0.8655 | 0.8730 | +0.0075 |
| stride/g512_ov320 | 3,778 | 38 | 0.10 | 8 | 1.000; 0.611 | 0.0032 | 0.8800 | 0.8843 | +0.0043 |
| winner/N1 | 1,290 | 11 | 0.10 | 8 | 1.000; 0.651 | 0.0019 | 0.8677 | 0.8753 | +0.0076 |
| winner/N3 | 1,700 | 11 | 0.10 | 8 | 1.000; 0.644 | 0.0019 | 0.8911 | 0.9009 | +0.0098 |
| winner/N5 | 1,968 | 11 | 0.10 | 8 | 1.000; 0.644 | 0.0022 | 0.8856 | 0.8953 | +0.0097 |

332 candidates across the fourteen unions; one (Image-B HIGH) reached
probability 0.15, every other was below it, against 15 % to 41 % of the
other candidates per union. In g384_ov192 all 22 were seen on
`K-35-053-3_Elenovo` and booked to the east column (`x4032`) of
`K-35-052-4`; candidate 245, ten votes and 14.6 m from a curator mound,
was verified at probability 0.00 on a crop that is black except for a
sliver at its left edge. The "Bound" column is optimistic by
construction: it sets every re-keyed candidate's probability to 1.0 and
re-scores the cell's current best point, so it is the most any
re-verification could add there, not an estimate of what it would add.

What follows:

- The verified boards' numbers are conditional on these candidates having
  been rejected for want of a picture. The scoring fix leaves them
  rejected; only cutting new crops from the origin sheet and
  re-verifying them can say what they are. That is a model API spend
  (about 330 calls; at the grid verifier's audited ~$0.0007 per call that
  is of the order of $0.25 flex, an estimate only) and needs the PI.
- The bound is of the same size as the differences the plateau's claims
  rest on (g384_ov128 now leads `opmax` by 0.0022, p = 0.87, and min6 by
  0.0191, p = 0.1377): 384/33.3 at K = 10 would reach at most 0.9078, and
  the exact ladder's N = 3 at most 0.9009.
- Other verified unions built the same way were not measured: the
  K-ladder re-verifications under `outputs/grid-2026-08-18/verifier/*/`
  (`k-ladder/`, `verify_37/`), the Gemini 3.7 screens, the Gemini 3.7
  image GS cells, and the modality-bridge unions
  (`modality_bridge_union.py` uses `union_with_votes`). Any union whose
  `source_tile` came from the legacy nearest-tile rule is exposed.

## 8. What was not done, and what remains

- **Nothing published.** No committed result, document, or register row
  was regenerated or edited. On publication, the signed rows whose quoted
  numbers move would lapse: `grid-tilesize-overlap-2026-08-18` (every
  board value, contrast, and CI it quotes) and
  `grid-postverifier-2026-08-18` (its quoted single-pass −0.0824, the
  union-recall ceilings, the gain range, and the baseline contrasts).
  `stride-plateau-2026-08-25`'s row text ("12 of 13 cells one statistical
  tier") survives verbatim, though the 30 m statements in the findings
  and claims R1b-15 and R1b-16 do not. `stride-winner-ladder-exact-2026-08-25`
  and `image-b-modality-2026-08-28` quote no moved number.
- **Not fixed here (owned elsewhere or out of the brief)**: the H13
  chain and the library copies of D62 (1); the modality-bridge chain's
  own loaders (`modality_bridge_anchors.py`, `modality_bridge_floors.py`,
  `modality_bridge_verifier_sd.py` call `reassign_gate` directly and stay
  on the stored tile), whose six-cell anchors therefore still hold the
  legacy numbers; and `selection_aware_intervals.py`'s image-union path.
- **Fixed but not re-scored**: `selection_aware_intervals.py`'s `--cell`
  path (`results/selection-aware/`), and the materialisers
  (`materialise_grid_unions.py`, `materialise_winner_ladder.py`, and
  through them the stride, Image-B, and modality-bridge union writers),
  which will now record `origin_tiles` and an origin-sheet `source_tile`
  in any union they write. Their committed unions were not rewritten.
- **Note for any later regeneration**: `image_b_analysis.py` and
  `image_b_pair.py` now need each union's prepared passes (they rebuild
  its members), including on the `--no-ladder` path; the modality-bridge
  campaigns that call `image_b_analysis.py` must have theirs in place.

## 9. For the PI

1. **Re-verification of the 332 blinded candidates** (§ 7): whether to
   cut their crops from the origin sheet and re-verify them, which is the
   only way to know whether R1b-08, R1b-17, the stride board, and Image-B
   move. It needs an API spend decision.
2. **The exposure beyond these chains** (§ 7, last item): whether to
   measure the same crop defect on the K-ladder, Gemini 3.7, and
   modality-bridge unions before #35 and #38 regenerate.
3. **Publication of this re-score**: the restatements in the verdict
   table (R1b-05's numbers, R1b-15's "6 of 78" and its 30 m sentence,
   R1b-16's 30 m shelf, the grid findings' Phase A paragraph) and the two
   signature lapses in § 8, once you rule.

## Changelog

### 2026-10-13 — Original publication

First version: the route fix (`11a0bd980`), the re-score of the GS grid,
stride, plateau, and Image-B boards in two fixed runs and a legacy
control on sapphire, and the measurement of the re-keyed verifier inputs.
No committed output changed. The run records and scripts are in
[`origin-gap-grid-plateau-scripts/`](origin-gap-grid-plateau-scripts/)
(`records/` holds the extracted numbers, integrity diffs, step logs, and
bad-page counts; three of the scripts were reformatted with `ruff format`
after the runs, a cosmetic change re-checked by regenerating the extract
and the tables byte for byte).
