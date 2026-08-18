# Recall levers: tile size versus overlap — research programme

> **Last revised**: 2026-08-19 (original publication; PI-approved 2026-08-19).
> See [§ Changelog](#changelog) for revision history.

**Status**: approach approved by the PI. Phase 0 ($0) to run immediately;
Phases 1+ carry API spend and go through `/audit-config` and the standing API
gate first.

## Why this programme exists

The study has two levers that raise proposer recall — **smaller tiles** and
**more overlap** — and neither is understood well enough to choose between
them. The Session 136 grid established that 512 px beats 384 px at every
overlap and every K, but **only at the proposer stage, with no precision
filter downstream**. Since 384 px loses to 512 px entirely on precision while
carrying the higher recall ceiling (0.9509 versus 0.9229 at 50 % overlap,
K = 10), that ranking is conditional and may invert once a verifier prunes.

Three questions, in the PI's framing:

- **(a)** Are tile size and overlap *strictly equivalent* routes to recall, or
  *qualitatively different*?
- **(b)** What are the individual and combined F1 optima? Known: 384 px is
  optimal for tile size in the PV pipeline with overlap held at 12.5 %.
  Unknown: overlap alone at fixed tile size, and the joint optimum.
- **(c)** If (b) is a plateau, what is the most cost-efficient way to reach the
  highest F1?

## The reframing that organises the design: stride is the cost variable

Per-call cost is almost flat across tile size, because image input tokens are a
constant 1,502 per call regardless of tile dimensions (measured: $0.000597/call
at 384 px, $0.000643 at 512 px). Spend is therefore set by **tile count**, and
tile count by **stride**:

```text
stride = tile_px x (1 - overlap_fraction)
tiles  ∝ 1 / stride^2
```

Verified against the grid — `tiles x stride^2` is constant to within edge
effects (1.000 / 0.918 / 0.925 / 0.867 across the four cells).

**Tile size and overlap are not independent levers. They are two ways of moving
one variable, and cost sees only the product.** Two consequences:

1. **Small tiles are structurally expensive.** Stride cannot exceed tile size,
   so 256 px at *zero* overlap already costs about 3x a 512 px / 12.5 % run.
   There is no cheap way to buy small tiles.
2. **The Session 136 2x2 is cost-confounded.** 512/50 % (stride 256) and
   384/12.5 % (stride 336) differ 1.7x in cost, so that comparison mixes
   geometry with sampling density.

## The mechanistic hypothesis under test

**H-A: the two levers produce qualitatively different false positives.**

- *Small-tile FPs are systematic.* A feature ambiguous through context
  starvation is ambiguous every time — the context deficit is stable — so
  repeated looks reproduce it.
- *Overlap FPs are stochastic.* Each look reframes the same ground at a
  different position, so a spurious detection at one framing need not recur at
  another.

If true: overlap FPs are removable by corroboration and possibly by a verifier;
small-tile FPs are removable by neither. This would explain the 256 px
observation without implying that high overlap fails the same way, and would
make the two levers non-substitutable.

**H-A is refutable by Phase 0.1 and should be treated as a hypothesis, not a
premise, until then.**

## Phase 0 — $0, run immediately

### 0.1 FP character: are overlap FPs stochastic?

**Method.** For each Session 136 grid cell, match deduplicated detections to
ground truth (20 m, Hungarian, per map) and split into TP and FP. Compare the
`cluster_size` distributions (cross-tile corroboration, already recorded per
detection by `scripts/grid_prepare_scoring.py`).

**Inputs**: `outputs/grid-2026-08-18/scoring/`, `inputs/vectors/references/mounds-reference.geojson`.

**Prediction under H-A**: FP corroboration sits well below TP corroboration in
the 50 % cells, and the TP/FP separation is *worse* at 384 px than 512 px.

**Refutation**: if TP and FP corroboration distributions overlap heavily, or if
384 px separates as well as 512 px, H-A is wrong and the levers may be
substitutable after all.

**Report**: separation statistic per cell, plus the recall/precision cost of
each `c` threshold.

### 0.2 Where is the swamping line?

**Method.** On the existing 256 px proposer-verifier data, rank candidates by
vote fraction and plot the verifier's **marginal** precision against rank.
Swamping is the point at which the marginal candidate's true-positive rate
falls below what the verifier can discriminate — this converts an impression
into a number.

**Inputs**: `outputs/h11/pv-diag-256/`, its committed verifier probabilities.

**Report**: the marginal-precision curve, the rank at which marginal precision
crosses the accept threshold, and the same curve for a 384 px and a 512 px
cell for comparison.

### 0.3 Re-score the 256 px premise on a common footprint — DO THIS FIRST

**The pessimism about the high-recall direction rests on a cross-scope
comparison.** `pv-diag-256::verified-adv-text-consensus-5of5` scores F1 0.8558
on scope `px256-1032` (1,032 tiles), while the 384 px PV frontier's 0.8835 sits
on `era-2-487` (487 tiles) — *different footprints, different ground-truth
denominators*. This is the same confound corrected repeatedly in Session 136,
and it has not been corrected here.

Note also that the gap is 0.028, not a collapse. "256 px overwhelmed the
verifier" may be materially overstated.

**Method.** Re-score the 256 px PV cell and its 384 px counterpart on their
common footprint, following `scripts/h13_tilesize_overlap_grid.py`.

**Why first**: if the 256 px deficit shrinks or vanishes on a common footprint,
the premise motivating caution about high recall weakens, and (c) opens up.

## Phase 1 — verifier on the existing grid (~$6.33, gated)

Run the standard verifier (v1, `verify_adversarial.md`,
`gemini-3-flash-preview`, MINIMAL, T = 0.0, 1 iteration) over the K = 10 unions
of all four grid cells. $6.33 for all four; $4.09 for the two 50 % cells alone.
Prices on the flex-discounted `pareto_v2.json` basis (`vf_call_usd` 0.000693).

**Settles**: whether the 512 px > 384 px ranking survives a precision stage,
and whether the overlap reversal survives. Both current headline findings are
conditional on "no precision stage" until this runs.

**Design note**: verify the **unions**, not consensus-pruned sets — pruning
before verification discards the recall the verifier exists to exploit. But
also test corroboration (`c >= 2`) as a **pre-filter**: a swamped verifier has
two problems, per-candidate discrimination and sheer load, and corroboration
addresses the second for free. At 50 % overlap `c >= 2` retained about 93 % of
recall while cutting the candidate set substantially. Corroboration and the
verifier may be **complementary rather than redundant**.

## Phase 2 — the iso-stride test of (a) (~$2.9 + verifier, gated)

**Hold stride constant, vary only tile size.** At stride 336:

| Cell | Tile px | Overlap | Stride | Tiles | Status |
|---|---:|---:|---:|---:|---|
| existing | 384 | 12.5 % | 336 | 487 | already run (grid) |
| **new** | 512 | **34.4 %** | 336 | ~490 | to run |

Same tile count, same cost, same ground sampled per call — different tile size
and different look-multiplicity. **Any performance difference is purely the
qualitative effect (a) asks about**, with cost and sampling density controlled.

This is a sharper instrument than adding corners to the 2x2, and has not been
run. ~490 tiles x 10 passes ≈ $2.9 proposer, plus verifier.

Pin the exact overlap by tiling: choose the overlap whose realised tile count
most nearly matches 487 under
`scripts/build_footprint_manifest.py --footprint <era-2-487 bounds>`.

## Phase 3 — contingent

Run only if Phases 0-2 leave (b)/(c) open:

- **Overlap alone at fixed tile size, in PV**: the registered-unknown half of
  (b). Grid Phase 1 gives 12.5 % and 50 % at two tile sizes; a 25 % point would
  resolve curvature if the two known points are not enough.
- **Verifier work for high-recall proposers**: the consensus verifier was
  previously tested only on an already-optimal 384 px / 12.5 % run, where it
  did not help. It has never been tested on a *high-recall, low-precision*
  proposer, which is the regime where extra verification effort should pay.
  Options: a consensus verifier (k-of-n accept), a raised `prob_threshold`, or
  a cheap-filter-then-expensive-verifier cascade.
- **Cost-efficiency frontier for (c)**: with cost = k / stride^2, the
  efficient frontier is computable analytically once F1 is known at a few
  strides. If (b) is a plateau, report the *cheapest* stride achieving
  plateau-level F1 rather than the highest-F1 configuration.

## Standing constraints

- All API phases go through `/audit-config` and the API review gate (model,
  mode, call count, cost) before spend. Re-pin the smoke after **any**
  parameter change — the Session 135 lesson, re-earned when T = 0.7 produced
  44 % more output per call than T = 1.0.
- Every cross-configuration comparison must sit on **one evaluation footprint**.
  Session 136 corrected this confound four separate times; assume it is present
  until measured.
- Report **tile-level MCC alongside F1**, and never publish an undefined MCC as
  `0.0` (E81).
- These are **post-hoc (E41-class)** extensions. They need their own register
  rows and must not be reported under a registered hypothesis.

## Blocking dependency

**D15 (the BCa axis defect) should be resolved before any inference here is
trusted.** Session 136 measured BCa-path intervals as 1.66x too narrow at
B = 1,000 and 5.50x at B = 10,000. Point estimates are unaffected, and the
paired bootstraps in `scripts/h13_overlap_analysis.py` and
`scripts/grid_analysis.py` implement their own resampling and are unaffected —
so Phase 0 can proceed. Anything routed through `evaluate_detections.py` must
wait. See `reports/bca-axis-defect-2026-08-18.md`.

## See also

- **Preceding experiment(s)**: `results/grid-2026-08-18/findings.md` — the
  tile-size x overlap grid this programme extends.
- **Preceding experiment(s)**: `results/h13-overlap-2026-08-18/findings.md` —
  H13, where the overlap reversal under aggregation was first seen.
- **Follow-up experiment(s)**: None yet.
- **Run output directory**: `outputs/grid-2026-08-18/` (Phase 0 inputs).
- **Working-notes Observations**: None yet — candidates pending.
- **Decisions / Errata**: E41 — post-hoc extension classification. E81 —
  undefined tile MCC. D15 — the BCa defect, in
  `reports/defect-register-2026-08-18.md`.

## Changelog

### 2026-08-19 — Original publication

Written after the PI approved the approach. Records the stride reframing
(verified against grid costs), hypothesis H-A on FP character, and a four-phase
programme with Phase 0 at $0. Adds Phase 0.3 — the 256 px "swamping" premise
rests on a cross-scope comparison (0.8558 on `px256-1032` against 0.8835 on
`era-2-487`) and a 0.028 gap, so it needs re-scoring on a common footprint
before it constrains the design.
