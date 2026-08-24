# The stride programme: overlap/stride × tile size, discharged to a decision

> **Last revised**: 2026-08-24 (original publication; PI-directed S142,
> spend NOT yet authorised — every API phase is individually gated).
> See [§ Changelog](#changelog) for revision history.

**Status**: PROPOSED. The PI directed the programme on 2026-08-24
("we need to discharge the entire overlap/stride study across
different tile sizes") and set the exit criterion; per-phase spend
still requires the standing API gate (`/phase-gate`, `/audit-config`,
explicit approval of model / mode / call count / cost).

## Why this programme, now

The grid's post-verifier board
(`results/grid-2026-08-18/findings.md` § "The verifier stage, run") is
a clean **stride ladder**: best verified F1 is monotone in stride
(192 → 0.8961, 256 → 0.8815, 336 → 0.8677, 448 → 0.8311 at 20 m), as
is union recall — and no two grid cells share a stride, so *stride
density* and *tile size at fixed stride* are confounded by
construction. Meanwhile the ladder's top cell (384 px / 50 %,
stride 192) matches the study's incumbent best within noise at
roughly a fifth of the cost:

| Cell | F1@20 m | F1@30 m | All-in flex |
|---|---:|---:|---:|
| 384/50 verified (MINIMAL, T = 0.7, K = 10, n = 1 verifier) | 0.8961 | 0.9034 | ~$10.7 |
| opmax (`verifier-robustness::verified-384-16of30-t0-3-n5-opmax`) | 0.8951 | 0.9161 | ~$50-class (top Pareto rung) |
| headline (`pv-diag-384::verified-adv-text-consensus-16of30`) | 0.8902 | 0.9044 | ~$50-class |

(The 30 m grid values were computed S142 from the committed verified
sets with `lib_advanced_metrics.score_detection_set` on the common
footprint; the 20 m values reproduce the registered evaluations
exactly. Footprint caveat: common intersection, 428 refs, vs the
incumbents' era-2-487 scope, 435 refs — Phase A removes this caveat.)

**The PI's exit criterion (2026-08-24)**: run until a clear winner or
a plateau with a reasonable number of tied leaders; then a 55-map
proposal goes to the PI, authorised **only if** the programme is
pushing towards new F1 highs.

## Phase A — make the incumbent bar exact ($0, no gate needed)

Re-score the incumbent leaders on the grid's common footprint so the
"dethrone" comparison is on ONE evaluation: opmax, the registered
headline, and the cheap rungs min11/min6, each first re-scored on its
own scope to reproduce its registered F1 (gate), then clipped through
`grid_analysis.as_gdf` to the common carrier and scored at 20/30 m
with tile MCC. Adds the incumbents as rows on the grid board and
settles whether 384/50 already leads like-for-like. Compute on
sapphire; zero API.

## Phase B — the iso-stride decomposition (gated API)

Hold stride constant, vary tile size; everything else in-family with
the grid (detect_brief-text, MINIMAL, T = 0.7, K = 10, adversarial
text verifier n = 1 over the K = 10 union, common-footprint scoring,
B = 10,000):

| New cell | Stride | Iso-stride partner(s) already run | Est. tiles/pass | Est. K = 10 proposer flex | Est. verifier flex |
|---|---:|---|---:|---:|---:|
| 512 px / 62.5 % | 192 | 384/50 (0.8961) | ~1,490 | ~$9.0 | ~$2.5 |
| 256 px / 25 % | 192 | 384/50, 512/62.5 | ~1,490 | ~$9.0 | ~$3.5 |
| 384 px / 33.3 % | 256 | 512/50 (0.8815) | ~840 | ~$5.1 | ~$1.5 |
| 512 px / 34.4 % | 336 | 384/12.5 (0.8677) | ~490 | ~$3.0 | ~$1.0 |

Tile counts from the grid-verified invariant tiles × stride² ≈ 55 M
(edge effects ±5 %); proposer $/call from the grid's audited flex
range $0.000597–0.000643; verifier estimated from the grid's measured
union-size-to-cost ratios (256 px unions run larger). **Phase B
aggregate: ~26,000 proposer calls + ~12,000 verifier calls ≈ $34–38
flex**, a few hours wall-clock at grid-run concurrency. Settles: at
fixed stride, does tile size matter at all post-verifier — i.e. is
stride the real lever? The stride-192 trio is the headline cell of the
design (three tile sizes, one stride).

## Phase C — extend the ladder to the plateau (gated API)

Only if Phase B says stride is the lever (or leaves 384 px ahead at
fixed stride, in which case descend on 384 px):

| Cell | Stride | Est. tiles/pass | Est. K = 10 + verifier flex |
|---|---:|---:|---:|
| 384 px / 62.5 % | 144 | ~2,650 | ~$16 + ~$4 |
| 256 px / 50 % | 128 | ~3,360 | ~$20 + ~$6 |

**Stop rule**: descend one stride rung at a time; stop at the first
rung whose best verified F1 fails to beat the previous rung's by more
than the paired-bootstrap CI (the plateau), or reverses (the
turnover). Phase C aggregate if both cells run: ~$46 flex.

## Programme aggregate and the decision

Worst case all phases: **~$85–90 flex** (~60,000 proposer +
~20,000 verifier calls) on the 4-map GS corpus, staged across three
individually-gated approvals, with Phase A free and first. Exit: a
winner-or-plateau board on one footprint at 20/30 m → the 55-map
proposal card (cost scales ~×17.5 by area; a stride-192 55-map K = 10
run would be ~$150-class — priced properly in that card, not here) →
PI authorises iff new F1 highs.

## Design notes and hazards

- **Footprint rule**: the grid's common intersection stays the fixed
  reference footprint; every new cell's union is clipped to it (new
  denser tilings cover it by construction; verify, not assume — the
  grid's Surprise 3 precedent). New tilings are generated locally
  ($0) and their manifests committed before any run.
- **Union gates**: exact-count materialisation gates and the
  join-witness manifest commit are standing practice
  (`materialise_grid_unions.py` pattern; audit S142).
- **K**: held at 10 for comparability. The K-economics question
  (does one dense-stride pass beat ten sparse ones — the grid's
  "$0.53 single pass" result) rides along free from the sweep data.
- **Selection caveat carries**: best-F1 operating points remain
  GT-selected; the paired contrasts remain the instrument; any
  "new high" claim quotes the CI, not the point estimate alone
  (audit C1 lesson).
- 256 px cells inherit the Era-1 "verifier rescues 256" prior
  (Obs 352) but at a different scope — treat as hypothesis, not
  expectation.

## Changelog

### 2026-08-24 — Original publication

S142, written to the PI's direction and exit criterion of the same
day, immediately after the grid post-verifier audit corrections
(`864b203c7`). Costs are planning estimates anchored to the grid's
audited spend; no API has been committed under this document.
