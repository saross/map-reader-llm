# The stride programme: nine geometries, one verdict

> **Last revised**: 2026-08-25, twice (original publication, then the
> plateau follow-ups: corrected 13-cell board, k-curves, the free
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
| 1 | **384 / 33.3 % (new)** | 384 | 33.3 % | 256 | **0.8982** | 0.9031 | 0.9457 | 0.8551 | 0.8022 |
| 2 | 384 / 50 % (grid) | 384 | 50 % | 192 | 0.8961 | 0.9034 | 0.9275 | 0.8668 | 0.7965 |
| 3 | 384 / 62.5 % (new, Phase C) | 384 | 62.5 % | 144 | 0.8860 | 0.8907 | 0.8913 | 0.8808 | 0.7910 |
| 4 | 512 / 50 % (grid) | 512 | 50 % | 256 | 0.8815 | 0.8938 | 0.9346 | 0.8341 | 0.8011 |
| 5 | 512 / 62.5 % (new) | 512 | 62.5 % | 192 | 0.8800 | 0.8970 | 0.9144 | 0.8481 | 0.8023 |
| 6 | 256 / 25 % (new) | 256 | 25 % | 192 | 0.8795 | 0.8936 | 0.8806 | 0.8785 | 0.7959 |
| 7 | 384 / 12.5 % (grid) | 384 | 12.5 % | 336 | 0.8677 | 0.8728 | 0.9525 | 0.7967 | 0.7751 |
| 8 | 512 / 34.4 % (new) | 512 | 34.4 % | 336 | 0.8655 | 0.8802 | 0.9077 | 0.8271 | 0.7964 |
| 9 | 512 / 12.5 % (grid) | 512 | 12.5 % | 448 | 0.8311 | 0.8557 | 0.8799 | 0.7874 | 0.7937 |

## The three questions, answered

**1. Is stride the real lever? NO — the pure-stride reading dies.**
The grid's stride-monotone ladder was an artefact of having only one
cell per stride. With three tile sizes at stride 192, 384 px leads
both others (−0.0161 vs 512 px, p = 0.127; −0.0166 vs 256 px,
p = 0.167; the two others are identical, p = 0.978); at stride 256,
384 px leads 512 px (+0.0167, p = 0.151); at stride 336 the pair is
a dead tie (p = 0.885). No single iso-stride contrast is significant,
but the direction is consistent: **at fixed stride, 384 px is at or
above every alternative, never below** — the study's long-standing
384 px preference survives its sharpest test yet.

**2. Where is the optimum? An interior plateau at 384 px, strides
192–256.** The 384 px ladder reads 0.8677 (336) → 0.8982 (256) →
0.8961 (192) → 0.8860 (144): the climb 336 → 256 is **significant**
(+0.0305 [+0.0052, +0.0564], p = 0.020), the top is flat
(256 vs 192: +0.0020, p = 0.862), and the Phase C rung falls away
(144 vs 256: −0.0121, p = 0.297; 144 vs 192: −0.0101, p = 0.360).
**The stop rule fires at stride 144**: the descent is over.

**3. Does anything beat the incumbent bar? NO — the plateau is the
answer.** The best new cell (384/33.3, 0.8982) sits +0.0020 above the
grid winner (p = 0.862) — a dead statistical tie — and at 30 m the
top three (0.9031/0.9034 and Phase A's opmax 0.9031) are
indistinguishable to the third decimal. One new cell is significantly
*below* the bar (512/34.4: −0.0306, p = 0.021). **No new F1 high
exists on this corpus from geometry**: the leading shelf remains
~0.896–0.898 @20 m / ~0.903 @30 m.

## What the programme DID buy: the cost frontier

The new leader-by-a-hair, 384/33.3 (stride 256), runs **820 tiles per
pass** against the grid winner's 1,398 — the same performance at
~59 % of the calls. All-in on this footprint (K = 10 proposer +
union verifier, flex): **≈ $6.6** vs ≈ $10.7 (384/50) vs ~$50-class
(the HIGH-thinking incumbents). The cheapest known member of the
leading shelf, by a wide margin. If a 55-map deployment case is ever
made, it is a **cost case, not an F1 case**, and 384/33.3 is its
configuration.

## Recommendation on the 256/50 cell (stride 128) — DO NOT RUN

Commissioned by the PI ("have a recommendation once you've seen
results"). Three independent reasons:

1. **The stop rule has fired.** Stride 144 is already past the
   optimum at the strongest tile size (−0.0121 vs the peak); stride
   128 descends further on a falling surface.
2. **The tile size is wrong.** At stride 192, 256 px trails 384 px
   (−0.0166) and ties 512 px; descending the *weaker* tile size past
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
bootstrap contrasts at B = 10,000, seed 42 (Decision 10 / E82).
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

### 2026-08-25 (later) — Plateau follow-ups and the exact winner ladder

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
