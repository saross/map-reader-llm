# Tile-MCC on PI ruling D51's clipped basis: tier E and six Phase 2 ladders

> **Last revised**: 2026-10-30 (original publication). See [§ Changelog](#changelog) for revision history.

**What this is.** Tile-level Matthews correlation coefficient (tile-MCC: a
tile-by-tile "does this tile contain a mound" score) computed on the
Principal Investigator's (PI's) ruling D51 basis, where a ladder's rungs are
compared on the area every rung searched. It covers the seven ladders whose
tile-MCC the clipped tables withheld: tier E (the grid study's 384 px / 50 %
overlap MINIMAL text ladder) and the six Gemini 3 Phase 2 ladders marked ‡ in
`../findings.md` § 4.3. The K-ladder tile-MCC permutation test and the Hsu
multiple-comparisons-with-the-best (MCB) sets were then re-run on the clipped
cells. Cost US$0; no model was called. The full account, gates, and claims
affected are in `reports/s166-agent-records/clipped-tile-mcc.md`.

**Basis and reference.** D51 option 1, exactly as the committed clipped F1:
each rung's detections are clipped to the ladder's common assessed area; the
board frame `era2-b-487` (487 tiles) and the 435 curator reference mounds
inside it are kept whole. A reference mound in the clipped-away band therefore
counts against every clipped rung, in F1 and in tile-MCC alike. The
consensus-only side of § 8.6 is scored against a different set, the 428
mounds on the grid study's common footprint.

## The answer for § 8.6

| stage (384 px, 50 % overlap, K = 1 → 10) | ΔF1@20 | Δtile-MCC |
|---|---:|---:|
| consensus only | +0.0660 | **+0.0444** |
| verified, D51 clipped (this job) | +0.0338 | **−0.0161** (BH p 1.0000) |
| verified, as evaluated | +0.0262 | −0.0238 (BH p 0.8094) |

**The sign reversal survives the clip.** Clipped, K's tile-MCC effect after
the verifier is −0.0161, about a third smaller in size than as evaluated, so
the swing is **0.0604** rather than 0.0682. The F1 reduction stays 48.7 %. As
before, neither verified Δtile-MCC is statistically separated (BH is the
Benjamini–Hochberg false discovery rate adjustment within the ladder's six
pairs), so the claim is about the shift between stages.

Clipped tier E tile-MCC per rung: **0.8133 / 0.8089 / 0.8063 / 0.7973**
(K = 1 / 3 / 5 / 10; as evaluated 0.8211 / 0.8167 / 0.8139 / 0.7973). It
still falls at every step.

## Per ladder, clipped beside as evaluated

Tile-MCC from K = 1 to the ladder's best F1 rung, with its BH-adjusted p, and
the tile-MCC Hsu MCB admissible set (the rungs that cannot be ruled out as
best at simultaneous 95 %).

| ladder | detections clipped (K = 1/3/5/10) | clipped: Δtile-MCC (BH p) | as evaluated: Δtile-MCC (BH p) | MCC MCB set, clipped / committed |
|---|---|---:|---:|---|
| MINIMAL text T 0.3 (K1 → K5) | 0 / 0 / 0 / 0 | −0.0251 (0.6044) | −0.0251 (0.6044) | {1, 3, 10} / {1, 3, 10} |
| MINIMAL text T 1.0 (K1 → K10) | 0 / 0 / 0 / 0 | −0.0214 (0.5760) | −0.0214 (0.5760) | {1, 3, 5, 10} / same |
| HIGH text T 1.0 (K1 → K10) | 0 / 3 / 3 / 3 | **−0.0290** (0.5529) | −0.0252 (0.8065) | {1, 3, 5, 10} / same |
| MINIMAL image T 0.3 (K1 → K10) | 0 / 0 / 0 / 0 | −0.0065 (0.9954) | −0.0065 (0.9954) | {1, 3, 5, 10} / same |
| MINIMAL image T 0.7 (K1 → K10) | 0 / 2 / 2 / 2 | **−0.0253** (0.8191) | −0.0214 (0.9768) | {1, 3, 5, 10} / same |
| MINIMAL image T 1.0 (K1 → K10) | 0 / 0 / 0 / 0 | −0.0282 (0.6072) | −0.0282 (0.6072) | {1, 3, 5, 10} / same |
| tier E (K1 → K5) | 29 / 29 / 27 / 0 | −0.0071 (1.0000) | −0.0071 (1.0000) | {1, 3, 5, 10} / same |

All seven fall on the clipped basis, as they did as evaluated; none
separates; every F1 and tile-MCC admissible set equals the committed one. On
four ladders the clip removes nothing, so clipped equals as evaluated
exactly. Where it removes detections, it turns one true-positive tile into a
false-negative tile per affected rung (two on tier E's K = 1, 3, 5). It
deepens the decline where the higher rungs searched the extra area (HIGH
text T 1.0, MINIMAL image T 0.7). It shrinks tier E's K = 1 → 10 decline,
where the lower rungs did.

## Gates (all passed)

1. D51 area gate over all 14 Phase 2 ladders and tier E, with no
   undetermined-area escape: every area determined; exactly the expected 7
   Phase 2 ladders and tier E clip; every common area equals its committed
   record.
2. Every rung's clipped F1@20 reproduces the committed clipped value, from
   the written file and from its evaluation (`gate.json`). Tier E's K = 1, 3,
   5 match at 6 dp (0.860360 / 0.890187 / 0.896797).
3. After the instruments: rebuilt micro-F1 equals each evaluation's F1, and
   every cell passed the confusion gate. Where nothing was clipped, the tile
   confusion equals the as-evaluated one.

## Files

- `summary.json`: every number above, with both bases and all six pairs
  per ladder.
- `prepare.json`, `gate.json`: the area gate, the clip and the two F1 gates.
- `cells/`, `materialised/`, `areas/`: the clipped evaluations, the clipped
  detections (verbatim subsets of the as-evaluated files), and each
  ladder's common area.
- `mcc-test/`, `mcb/`: the two instruments' outputs. Their analysis ids
  carry the driver's fixed `2026-09-12` stem.
- `source-commit.txt`: the commit the whole-tree copy on sapphire was
  archived from. The artefacts' own `git_commit` fields read `unknown`
  because the copy was a `git archive`.
- Generator: `scripts/k_ladder_clipped_cells.py` (`prepare`, `collect`,
  `report`), with `scripts/k_ladder_mcc_test.py --conditions` and
  `scripts/k_ladder_mcb.py --registry`.

## Changelog

### 2026-10-30 — Original publication

First computation of tile-MCC on D51's clipped basis for tier E and the six
Gemini 3 Phase 2 ladders, with their MCC tests and MCB sets (Session 166,
PI ruling D69 decision C). Generated at `4970cb53f` on sapphire, committed at
`6546feed3`; written to disk by the main session from the sub-agent's
hand-back.
