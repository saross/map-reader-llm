# The 55-map deployment portfolio: two geometries, one measurement contract

> **Last revised**: 2026-08-25 (original publication; awaiting PI
> sign-off — nothing runs until it is given). See
> [§ Changelog](#changelog) for revision history.

**Status**: PREPARED FOR SIGN-OFF. The PI confirmed the portfolio on
2026-08-25 ("I confirm this portfolio at K = 10 as you propose, let's
settle it once and for all. Please prep and I'll sign off"). This card
is the prep: the measurement contract is declared here BEFORE any call
runs, per the PI's direction ("we'll specify what we are going to
measure before we start").

## 1. The portfolio

Two configurations, both at K = 10 passes over the full 55-map corpus,
both with the carry-forward verifier over their K = 10 unions:

| Run | Geometry | Stride | Role in the design |
|---|---|---:|---|
| A | **384 px / 33.3 %** (overlap 128) | 256 | The GS plateau's point-leader and cost pole; precision pole of the P/R dial |
| B | **384 px / 50 %** (overlap 192) | 192 | The recall pole; overlap-transfer test within the winning tile size |

Carrier config identical to the stride programme and the grid:
`detect_brief-text` (byte-identical since `fe623a555`),
gemini-3-flash-preview, MINIMAL thinking, **T = 0.7 CLI override**,
real-time **flex**, tile size inferred from the tiles (the S142
runner contract). Verifier: `verify_adversarial-text`, T = 0.0,
MINIMAL, n = 1, real-time flex, one call per K = 10 union candidate.

**Explicitly excluded**: 256 px (trailed at matched stride on GS, no
deployment case); the K = 30-class configs (the incumbents' existing
55-map results are the comparison anchors and are not re-run).
**Gated contingency**: 512/50 at K = 3–5 (~$50–60), to be proposed
separately ONLY if Runs A/B show config-sensitive transfer.

## 2. Corpus and tilings

The 55-map rasters (`inputs/rasters/Russian1981_32635/`, 55 sheets),
tiled full-extent with manifest = every tile — the same rule as the
production 8,541-tile / stride-336 corpus (verified 2026-08-25:
`tiles_384_55maps` manifest equals its tree exactly; no footprint
filter). New tilings `tiles_384_ov128_55maps` and
`tiles_384_ov192_55maps`, cut 2026-08-25.

- Run A tiles/pass: **14,160** (manifest committed, no duplicate
  names, dims verified, dry-run PASSED with tile-size inference)
- Run B tiles/pass: **24,561** (ditto)

## 3. The measurement contract (declared before launch)

**Classification**: post-hoc, E41-class deployment extension — not a
registered hypothesis. Evaluated against the **canonical adjudicated
extended GT** (773 reviewed mounds, per-buffer gated), on the
established 55-map two-reference protocol.

**PRIMARY (the carry-forward discipline — S104 lesson: GS-selected
thresholds have failed to transfer before, so the headline is
committed now, not tuned there):**

- Run A headline = corrected-F1 at **50 m** (the 55-map working
  precision) at the GS-selected operating point **prob_t ≥ 0.15,
  k ≥ 8**, with tile-MCC alongside.
- Run B headline = the same at **prob_t ≥ 0.15, k ≥ 10**.
- These two numbers are the deployment claims, whatever the sweep
  later shows. 20 m and 30 m reported alongside for cross-corpus
  continuity; precision and recall reported per the P/R-dial thread.

**SECONDARY (oracle and calibration, clearly labelled as such):**

1. Full (prob_t × k) sweep per run — the deployment oracle and the
   threshold-transfer analysis (does the GS point sit on the 55-map
   plateau, as 4-of-5 did not in S104?).
2. The K-subset ladder N ∈ {1, 3, 5, 10} by the preregistered
   first-N rule, verifier probabilities inherited from the K = 10
   verification (method validated at ±0.008 on GS, 2026-08-25);
   exact re-verification of at most two finalist rungs gated at
   ≤ $10 additional.
3. The N-ladder cost curve → the deployment Pareto board, folding in
   the existing 55-map cells.

**Comparisons and instruments**: against the existing 55-map board
(carry-forward 0.8152, oracle 0.8476, image, min variants — committed
anchors, not re-run) and between Runs A/B, using the established
55-map machinery: fixed-union corrected-F1 comparisons and per-sheet
paired permutation/bootstrap at B = 10,000, seed 42 (Decision 10 /
E82), BH-FDR q = 0.05 across the declared comparison family. Tile-MCC
reported wherever inputs support it (standing rule). Undefined MCC
stays null (E81).

**The questions this settles** (pre-declared):

1. Does the GS geometry plateau TRANSFER to deployment? (Runs A/B vs
   the incumbent 55-map cells, primary points.)
2. Does the overlap/stride choice matter at deployment? (A vs B.)
3. Does the pass-count saturation (N = 3 within noise of N = 10 on
   GS) hold at deployment? (The ladders.)
4. Where does the deployment Pareto frontier now sit, and which
   configuration should a practitioner run? (The synthesis — the
   paper's deployment recommendation.)

## 4. Cost (to be finalised with exact tile counts)

| Stage | Run A (stride 256) | Run B (stride 192) |
|---|---:|---:|
| Proposer calls, K = 10 | 141,600 | 245,610 |
| Proposer flex (audited $0.000546/tile) | **$77.31** | **$134.10** |
| Verifier est. (GS densities; upper bound) | ~$28.3 (~41,200 calls) | ~$40.0 (~58,200 calls) |
| **All-in (est.)** | **~$106** | **~$174** |

Portfolio total **≈ $280 flex** (~$560 list on the metas): proposers
$211.42 EXACT-count-priced; verifier ~$68 estimated (launches at
MEASURED union sizes under a **2× ceiling = $137**). Wall-clock:
387,210 proposer calls ≈ 20–30 h at WORKERS=20 (the overnight runs
sustained ~3.7 calls/s at 12 workers with zero 429s and large TPM
headroom); the driver is idempotent and resumable across nights.
Anchors: the audited $0.000546/tile MIN-thinking 55-map rate
(token-load audit 2026-06-12) scaled by stride²; verifier at the
measured $0.000687/call with union sizes scaled from GS candidate
densities (the pareto_v2 note says 55-map runs sparser, so verifier
estimates are slight upper bounds). Exact proposer figures land with
the tile counts; the verifier stage is priced at MEASURED union sizes
after the proposers finish and launches only within a pre-approved
ceiling of **2× the estimate above** (the established pattern).

## 5. Execution plan

The overnight-driver pattern, hardened by the S142 incidents:
idempotent `.done` resume; per-pass failure logged, never fatal;
tile-size inferred from tiles; cheapest run first (A); one-tile
recovery fragments for residual gaps before any union is built; exact
manifest-coverage gates at preparation; union counts gated at
materialisation; candidate manifests (join witnesses) committed with
every verifier stage; per-stage commits from sapphire. `/audit-config`
runs on the final configs before launch; launch requires the PI's
sign-off on this card with the exact counts filled in.

## 6. Sign-off

- [ ] Exact tile counts filled in (§ 2, § 4)
- [ ] `/audit-config`: READY
- [ ] **PI sign-off** — model gemini-3-flash-preview, real-time flex,
  call counts and costs as finalised in § 4, the § 3 contract as the
  binding analysis plan

## Changelog

### 2026-08-25 — Original publication

S142, prepared to the PI's same-day portfolio confirmation. Estimates
anchored to the audited 55-map per-tile rate and measured verifier
rate; exact counts pending the two tilings then final sign-off.
