# The stride programme: nine geometries, one verdict

> **Last revised**: 2026-10-15 (restated with the re-verified wrong-sheet
> rows and the incumbents on their recorded sheets, PI ruling D65 (2):
> every board value moves; the 30 m reading of Question 3 now fails).
> Prior: 2026-10-05 (p-values from the paired permutation test, PI ruling
> D42; no verdict changed); 2026-08-25, twice (original publication, then
> the plateau follow-ups: corrected 13-cell board, k-curves, the free
> N-ladder, and the EXACT re-verification of the winner's ladder). See
> [§ Changelog](#changelog) for revision history.

**What this is.** The execution of
`planning/stride-programme-2026-08-24.md` Phases B and C(part),
PI-approved 2026-08-25: five new proposer-verifier geometry cells on
the Gold-Standard 4-map corpus, K = 10 passes each
(`detect_brief-text`, gemini-3-flash-preview, MINIMAL, T = 0.7,
real-time flex), K = 10 unions verified by the carry-forward
adversarial text verifier (T = 0.0, MINIMAL, n = 1), scored with the
grid's machinery on the grid's common footprint (487 clipped carrier
tiles, 428 references, 20 m matching; 30 m reported alongside).
E41-class post-hoc throughout. Every gate in the chain passed: exact
manifest coverage on all 50 passes (four one-tile recovery fragments),
16,966/16,966 candidates verified with zero failures, all join gates
clean.

**Spend (audited from the metas)**: proposers 66,080 calls, list
$79.88 → **$39.94 expected flex**; verifiers 16,966 calls, list
$23.20 → **$11.60 expected flex**; total ≈ **$51.5 flex**, within
every approved ceiling (B proposer ~$25.6 approved; C-144 ≤ $17;
verifiers ≤ $15.6 / $7.4 pre-approved, measured $8.03 / $3.57).

## The nine-cell board (verified best-F1@20 m operating points)

| Rank | Cell | Tile px | Overlap | Stride | F1@20 m | F1@30 m | P | R | MCC |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | **384 / 33.3 % (new)** | 384 | 33.3 % | 256 | **0.9075** | 0.9124 | 0.9467 | 0.8715 | 0.8134 |
| 2 | 384 / 50 % (grid) | 384 | 50 % | 192 | 0.9017 | 0.9089 | 0.9261 | 0.8785 | 0.8037 |
| 3 | 384 / 62.5 % (new, Phase C) | 384 | 62.5 % | 144 | 0.8938 | 0.8985 | 0.8928 | 0.8949 | 0.8029 |
| 4 | 256 / 25 % (new) | 256 | 25 % | 192 | 0.8876 | 0.9015 | 0.8805 | 0.8949 | 0.8033 |
| 5 | 512 / 50 % (grid) | 512 | 50 % | 256 | 0.8870 | 0.8993 | 0.9352 | 0.8435 | 0.8087 |
| 6 | 512 / 62.5 % (new) | 512 | 62.5 % | 192 | 0.8854 | 0.9023 | 0.9152 | 0.8575 | 0.8100 |
| 7 | 384 / 12.5 % (grid) | 384 | 12.5 % | 336 | 0.8761 | 0.8836 | 0.9434 | 0.8178 | 0.7852 |
| 8 | 512 / 34.4 % (new) | 512 | 34.4 % | 336 | 0.8718 | 0.8864 | 0.9130 | 0.8341 | 0.8078 |
| 9 | 512 / 12.5 % (grid) | 512 | 12.5 % | 448 | 0.8368 | 0.8613 | 0.8811 | 0.7967 | 0.8011 |

Each row is the cell's best point. Since the 2026-10-15 restatement
two cells' best points are not their registered conditions' points,
which keep them under PI ruling D65 (3): 512 / 34.4 % is best at
(0.15, k7), 0.8718, while `g512-ov176-k10-verified-p0.15-k6` scores
0.8714 [0.8377, 0.8984] (396 detections); 384 / 12.5 % is best at
(0.15, k7), 0.8761, while the grid's `g384-ov048-k10-verified-p0.20-k7`
scores 0.8752.

## The three questions, answered

**1. Is stride the real lever? NO — the pure-stride reading dies.**
The grid's stride-monotone ladder was an artefact of having only one
cell per stride. With three tile sizes at stride 192, 384 px leads
both others (−0.0163 vs 512 px, p = 0.139; −0.0141 vs 256 px,
p = 0.245; the two others tie, +0.0022, p = 0.863); at stride 256,
384 px leads 512 px (+0.0206, p = 0.084); at stride 336 the pair is
a dead tie (p = 0.785). No single iso-stride contrast is significant,
but the direction is consistent: **at fixed stride, 384 px is at or
above every alternative, never below** — the study's long-standing
384 px preference survives its sharpest test yet.

**2. Where is the optimum? An interior plateau at 384 px, strides
192–256.** The 384 px ladder reads 0.8761 (336) → 0.9075 (256) →
0.9017 (192) → 0.8938 (144): the climb 336 → 256 is **significant**
(+0.0314 [+0.0057, +0.0577], p = 0.020), the top is flat
(256 vs 192: +0.0059, p = 0.640), and the Phase C rung falls away
(144 vs 256: −0.0137, p = 0.223; 144 vs 192: −0.0079, p = 0.481).
**The stop rule fires at stride 144**: the descent is over.

**3. Does anything beat the incumbent bar? NO — the plateau is the
answer.** The best new cell (384/33.3, 0.9075) sits +0.0059 above the
grid winner (p = 0.640), a statistical tie. One new cell is
significantly *below* the bar (512/34.4: −0.0299, p = 0.031). **No
statistically new F1 high comes from geometry on this corpus**: the
best geometry cell's point estimate now sits above every incumbent's
at 20 m (+0.0116 over opmax's 0.8960, p = 0.380), but the 13-cell
board still places it in one twelve-cell tier with all four
incumbents. The 20 m shelf is ~0.902–0.908.

**This answer's 30 m sentence fails since the 2026-10-15
restatement.** It read that the top three at 30 m (0.9031 / 0.9034
and Phase A's opmax 0.9031) were indistinguishable to the third
decimal, on a shelf of ~0.903. They now read 0.9124 (384/33.3) and
0.9089 (384/50) against opmax's 0.9173, which sits 0.0048 above the
best geometry cell. No paired test exists at 30 m, so that lead is a
point estimate, but the three no longer agree to the third decimal.

## What the programme DID buy: the cost frontier

The new leader-by-a-hair, 384/33.3 (stride 256), runs **820 tiles per
pass** against the grid winner's 1,398 — the same performance at
~59 % of the calls. All-in on this footprint (K = 10 proposer +
union verifier, flex): **≈ $6.6** vs ≈ $10.7 (384/50) vs ~$50-class
(the HIGH-thinking incumbents). The cheapest known member of the
leading shelf, by a wide margin. That shelf is the 20 m one. At 30 m
the HIGH-thinking incumbents no longer share a shelf with the
geometry cells (2026-10-15), with opmax at 0.9173 above the best
geometry cell's 0.9124 and the registered headline at 0.9054 below
it (point estimates; no paired test exists at 30 m). If a 55-map
deployment case is ever made, it is a **cost case, not an F1 case**,
and 384/33.3 is its configuration.

## Recommendation on the 256/50 cell (stride 128) — DO NOT RUN

Commissioned by the PI ("have a recommendation once you've seen
results"). Three independent reasons:

1. **The stop rule has fired.** Stride 144 is already past the
   optimum at the strongest tile size (−0.0137 vs the peak); stride
   128 descends further on a falling surface.
2. **The tile size is wrong.** At stride 192, 256 px trails 384 px
   (−0.0141) and ties 512 px; descending the *weaker* tile size past
   the optimum compounds two headwinds.
3. **Nothing it could show would change a decision.** A ~$25 cell
   whose optimistic outcome is "joins the plateau from below" moves
   neither the paper's geometry claim nor the deployment
   configuration.

## Method

Chain identical to the grid post-verifier analysis
(`results/grid-2026-08-18/findings.md` § "The verifier stage, run"):
E80 within-pass 20 m dedup, E72 exact-coverage gates against the
committed manifests (`inputs/stride-phaseb-2026-08-25/`), K = 10
c = 1 unions with per-cluster vote counts, join gates per the S142
audit standard (counts, contiguous keys, carrier reassignment; the
candidate manifests — join witnesses — are committed), prob_t × k
sweeps (750 rows), best-F1@20 m operating points, paired tile
bootstrap CIs at B = 10,000, seed 42 (Decision 10 / E82), with p-values
from the paired tile-swap permutation test (PI ruling D42, 2026-10-05).
Selection caveat as on the grid: operating points are F1-selected on
the scored tiles; the paired contrasts are the instrument. Undefined
MCC stays null (E81; none occurred at any best point).

## Artefacts

- `stride_verifier_analysis.json` — boards, contrasts, verifier
  billing; the source for this document.
- `stride_verifier_sweep.csv` — the full prob_t × k sweep (750 rows).
- `outputs/stride-phaseb-2026-08-25/` and
  `outputs/stride-phasec-2026-08-25/` — 50 committed passes + 4
  recovery fragments, prepared dedup passes under `scoring/`, unions,
  crops manifests, and verifier outputs under `verifier/`.
- Register rows: queued (S142 overnight close; to land with the
  morning session).

## See also

- **Preceding**: `results/grid-2026-08-18/findings.md` (the 2×2 and
  its post-verifier board); `planning/stride-programme-2026-08-24.md`
  (design, approval trail, exit criterion).
- **Decisions / Errata**: E41 (post-hoc class), E72, E80, E81, E82,
  Decision 10.

## Changelog

### 2026-10-15 — Restated with the re-verified rows (PI ruling D65 (2))

**Refresh trigger**: PI ruling D65 (2) (`planning/pi-decisions-2026-09-20.md`),
executed by the S164 restatement pass
(`reports/s164-agent-records/restatement-pass.md`). The legacy
nearest-tile rule had cut some candidates' verifier crops from the
neighbouring sheet's raster, past the edge of its map; PR #43
(`0e8a1fa7a`) re-verified those candidates on crops from their own
sheet, and the reader routing (`9c843b980`) reads the re-verified rows.
PR #42 (`dddfcc0af`) had already put every detection, and the four
Phase A incumbents, on the sheet it was seen on. `stride_verifier_analysis.py`
and `stride_plateau_analyses.py` (and the condition and winner-ladder
materialisation) were re-run on sapphire in two independent copies
that agree apart from timestamps and run roots, and committed at `f6f10d605`. The
board reads each grid cell's best-point set
(`results/grid-2026-08-18/verified-best/`), as it reads each stride
cell's. Every value equals the REPAIRED column of the 2026-10-13
re-score (`reports/s164-agent-records/rescore-repaired-gs.md` §§ 3–4).

**One reading fails, and the text now says so**: Question 3's 30 m
sentence (the top three no longer agree at 30 m; opmax leads), and with
it the cost frontier's implication that the HIGH-thinking incumbents
share the 30 m shelf.

| Quantity | Before | After |
|---|---|---|
| Board F1 @ 20 m: 384/33.3, 384/50, 384/62.5, 512/50, 512/62.5, 256/25, 384/12.5, 512/34.4, 512/12.5 | 0.8982, 0.8961, 0.8860, 0.8815, 0.8800, 0.8795, 0.8677, 0.8655, 0.8311 | 0.9075, 0.9017, 0.8938, 0.8870, 0.8854, 0.8876, 0.8761, 0.8718, 0.8368 |
| Board F1 @ 30 m (same order) | 0.9031, 0.9034, 0.8907, 0.8938, 0.8970, 0.8936, 0.8728, 0.8802, 0.8557 | 0.9124, 0.9089, 0.8985, 0.8993, 0.9023, 0.9015, 0.8836, 0.8864, 0.8613 |
| Board precision (same order) | 0.9457, 0.9275, 0.8913, 0.9346, 0.9144, 0.8806, 0.9525, 0.9077, 0.8799 | 0.9467, 0.9261, 0.8928, 0.9352, 0.9152, 0.8805, 0.9434, 0.9130, 0.8811 |
| Board recall (same order) | 0.8551, 0.8668, 0.8808, 0.8341, 0.8481, 0.8785, 0.7967, 0.8271, 0.7874 | 0.8715, 0.8785, 0.8949, 0.8435, 0.8575, 0.8949, 0.8178, 0.8341, 0.7967 |
| Board tile MCC (same order) | 0.8022, 0.7965, 0.7910, 0.8011, 0.8023, 0.7959, 0.7751, 0.7964, 0.7937 | 0.8134, 0.8037, 0.8029, 0.8087, 0.8100, 0.8033, 0.7852, 0.8078, 0.8011 |
| Ranks 4–6 | 512/50, 512/62.5, 256/25 | 256/25, 512/50, 512/62.5 |
| Best points that moved | 512/34.4 (0.15, k6); 384/12.5 (0.20, k7) | (0.15, k7) each; the registered conditions keep (0.15, k6) at 0.8714 [0.8377, 0.8984] and (0.20, k7) at 0.8752 (D65 (3)) |
| iso192: 512 − 384; 256 − 384; 256 − 512 | −0.0161, p 0.137; −0.0166, p 0.178; −0.0005, p 0.968 | −0.0163, p 0.139; −0.0141, p 0.245; +0.0022, p 0.863 |
| iso256: 384 − 512; iso336 | +0.0167, p 0.154; −0.0022, p 0.885 | +0.0206, p 0.084; −0.0043, p 0.785 |
| 384 px ladder, 336 → 256 | +0.0305 [+0.0052, +0.0564], p 0.022 | +0.0314 [+0.0057, +0.0577], p 0.020 |
| 256 vs 192; 144 vs 256; 144 vs 192 | +0.0020, p 0.866; −0.0121, p 0.284; −0.0101, p 0.352 | +0.0059, p 0.640; −0.0137, p 0.223; −0.0079, p 0.481 |
| Bar: 512/34.4 − grid winner | −0.0306, p 0.022 | −0.0299, p 0.031 |
| **30 m: 384/33.3, 384/50, opmax** | 0.9031, 0.9034, 0.9031 ("indistinguishable to the third decimal") | **0.9124, 0.9089, 0.9173 (fails; opmax leads by 0.0048)** |
| 30 m: registered headline | 0.8958 | 0.9054 |
| Shelf @ 20 m; @ 30 m | ~0.896–0.898; ~0.903 | ~0.902–0.908; no common 30 m shelf |
| Best geometry cell against opmax @ 20 m (13-cell board) | +0.0140, p 0.2908 | +0.0116, p 0.3801 |
| 13-cell board F1, the four incumbents (opmax, headline, min11, min6) | 0.8842, 0.8838, 0.8719, 0.8623 | 0.8960, 0.8910, 0.8842, 0.8790 |
| 13-cell board order | opmax fourth | opmax third, above 384/62.5 |
| Exact winner ladder N = 1, 3, 5, K = 10: F1 @ 20 m | 0.8677, 0.8911, 0.8856, 0.8982 | 0.8737, 0.8993, 0.8937, 0.9075 |
| Exact ladder F1 @ 30 m | 0.8820, 0.8960, 0.8929, 0.9031 | 0.8878, 0.9042, 0.9010, 0.9124 |
| Exact ladder precision; recall | 0.8856, 0.9474, 0.9239, 0.9457; 0.8505, 0.8411, 0.8505, 0.8551 | 0.8831, 0.9482, 0.9250, 0.9467; 0.8645, 0.8551, 0.8645, 0.8715 |
| N = 3 below K = 10 ("within 0.007") | 0.0071 | 0.0083 |
| Inheritance estimates against the exact ladder | within ±0.008 | within ±0.010 |
| k-curve best k, 512/34.4 | 6 | 7 (flat top 6–9 unchanged) |

Sources: `stride_verifier_analysis.json` (`boards`, `contrasts`),
`plateau_analyses.json` (`board_13cell`, `k_curves`, `first_n_ladder`,
`winner_ladder_exact`), `conditions-verified/stride_verified_conditions.json`,
and `results/grid-2026-08-18/incumbents_common_footprint.json` (the
incumbents at 30 m), each read at `718d0ee08` (before) and at the
pass's head (after).

**What did NOT change**: the verdict of each question (stride is not
the lever; an interior plateau at 384 px, strides 192–256; nothing
beats the bar, and the stop rule fires at stride 144); the 13-cell
board's structure (6 of 78 pairs significant, the same six, all with
512/12.5 %; Tier 1 the other twelve); the k-curve shapes (the
winner's top flat at k 6–9; the k = 10-edge cells sharp); the all-in
costs ($1.38 / $2.64 / $3.81 / $6.56) and every spend figure; the
sweep (750 rows); the 256/50 recommendation. Older changelog entries
keep the figures they reported.

**Commits**: `385877de0` (the board reads the grid cells' best-point
sets); `f6f10d605` (the regenerated stride and plateau outputs); this
document refresh in the restatement pass's document commit.

### 2026-10-05 — p-values from the permutation test (PI ruling D42)

**Refresh trigger**: PI ruling D42 (`planning/pi-decisions-2026-09-20.md`).
`stride_verifier_analysis.py` takes p from the paired tile-swap permutation
test (through `h13_overlap_analysis.paired_bootstrap`); its JSON was
regenerated on sapphire (`5986316b5`). The script also gained the two
`ladder384` contrasts its JSON held but its contrast list lacked
(`7aef6d2ff`).

| Contrast | Before | After |
|---|---:|---:|
| iso192: 512 − 384 / 256 − 384 / 256 − 512 | 0.127 / 0.167 / 0.978 | 0.137 / 0.178 / 0.968 |
| iso256: 384 − 512 | 0.151 | 0.154 |
| iso336 | 0.885 | 0.885 (0.8845) |
| ladder384: 256 − 336 | 0.020 | 0.022 |
| ladder384: 144 − 256 | 0.297 | 0.284 |
| 144 − 192 (rung) / 256 − 192 (bar) | 0.360 / 0.862 | 0.352 / 0.866 |
| bar: 512/34.4 − grid winner | 0.021 | 0.022 |

**What did NOT change**: every Δ, CI and verdict at 0.05.

### 2026-08-25 (later) — Plateau follow-ups and the exact winner ladder

*The figures in this entry are those of 2026-08-25; the 2026-10-15
entry gives the restated values.*

**Trigger**: the PI's morning commission (pairwise plateau
characterisation, k-curves, x-of-5/N-ladder) and the approved ~$3.4
exact re-verification. Artefacts: `plateau_analyses.json` (board,
curves, ladder, and the `winner_ladder_exact` section).

- **13-cell tiered board** (verbatim board instrument, after a BH
  wiring fix caught by cross-instrument contradiction — commit
  `fe3bbe5bd`): **6/78 pairs significant, all involving 512/12.5 %**;
  Tier 1 holds the other twelve cells including all four incumbents.
- **k-curves**: the winner's top is flat (k 6–9 within 0.005);
  the k = 10-edge cells are sharp at the edge.
- **Exact winner ladder** (384/33.3; 4,958/4,958 verified, zero
  failures, $3.407 flex measured vs $3.41 priced):

  | N | F1@20 m (exact) | F1@30 m | P | R | All-in flex |
  |---:|---:|---:|---:|---:|---:|
  | 1 | 0.8677 | 0.8820 | 0.8856 | 0.8505 | $1.38 |
  | 3 | **0.8911** | 0.8960 | 0.9474 | 0.8411 | **$2.64** |
  | 5 | 0.8856 | 0.8929 | 0.9239 | 0.8505 | $3.81 |
  | 10 | 0.8982 | 0.9031 | 0.9457 | 0.8551 | $6.56 |

  Inheritance estimates were accurate to ±0.008; the N = 3/N = 5
  ordering swaps within that tolerance (a noise-level, not
  substantive, inversion — CI half-widths ≈ ±0.025). The efficiency
  reading: **N = 3 reaches 0.8911 for $2.64 — within 0.007 of the
  full K = 10 winner at 40 % of its cost, ~19× cheaper than the
  $50-class incumbents.** N ∈ {3, 5, 10} are one statistical point.

**What did NOT change**: the nine-cell board, the programme verdict
(plateau, no new high), and the 256/50 recommendation.

### 2026-08-25 — Original publication

S142 overnight execution: Phase B (four cells) + Phase C (stride-144
only, per the PI's restriction) run, verified, and scored end to end
under PI-approved gates; the 256/50 recommendation delivered as
commissioned. Total spend ≈ $51.5 flex against the ~$63 approved
envelope.
