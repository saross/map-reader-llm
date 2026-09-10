# The GS Era-2 verified board on one frame — `gs-era2-verified-board-2026-09-10`

> **Last revised**: 2026-09-10 (original publication). Card: `planning/gs-era2-verified-board-2026-09-08.md`. Frame: `inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson` (`era2-b-487`; the Era-2 carrier tiles clipped to the B tiling's union, 487 tiles, 1,402.4 km², 435 curator reference mounds). Instrument: scripts/era1_leaderboard_tiering.py (round-robin tile-swap micro-F1 permutation, BH q = 0.05, greedy clique, 20 m); Tier-1 membership is the MCB admissible set (E83). See [§ Changelog](#changelog).

39 cells; 375/741 pairs significant; 6 tiers; tie set 5; MCB admissible 11.

| rank | cell | tier | MCB | F1@20 (board frame) | committed F1@20 | Δ frame | tile-MCC |
|---:|---|---:|:---:|---:|---:|---:|---:|
| 1 | `gemini37-image-gs-2026-09-01::g37-image-k5-verified-swap37-p0.90-k5` | 1 | ● | 0.9233 | 0.9308 | -0.0075 | 0.8264 |
| 2 | `gemini37-screen-2026-08-28::g37-text-k5-verified-swap37-p0.80-k5` | 1 | ● | 0.9190 | 0.9265 | -0.0075 | 0.7937 |
| 3 | `gemini37-screen-2026-08-28::g37-text-k5-verified-swap38-p0.88-k5` | 1 | ● | 0.9182 | 0.9258 | -0.0076 | 0.8079 |
| 4 | `gemini37-image-gs-2026-09-01::g37-image-k5-verified-carried-p0.10-k5` | 1 | ● | 0.9179 | 0.9254 | -0.0075 | 0.8133 |
| 5 | `gemini37-screen-2026-08-28::g37-text-k10-verified-carried-p0.10-k10` | 1 | ● | 0.9068 | 0.9142 | -0.0074 | 0.7675 |
| 6 | `gemini37-screen-2026-08-28::g37-text-k5-verified-carried-p0.10-k5` | 2 | ● | 0.9066 | 0.9139 | -0.0073 | 0.7651 |
| 7 | `grid-2026-08-18::g384-ov192-k10-verified37-p0.98-k10` | 2 | ● | 0.9062 | 0.9140 | -0.0078 | 0.8102 |
| 8 | `verifier-robustness::verified-384-16of30-t0-3-n5-opmax` | 2 | ● | 0.8951 | 0.8951 | +0.0000 | 0.7941 |
| 9 | `pv-diag-384::verified-adv-text-consensus-16of30` | 2 | ● | 0.8902 | 0.8902 | +0.0000 | 0.7903 |
| 10 | `grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10` | 2 | ● | 0.8886 | 0.8961 | -0.0075 | 0.7903 |
| 11 | `pv-diag-384::verified-adv-text-min-6of10` | 2 | ● | 0.8835 | 0.8835 | +0.0000 | 0.8068 |
| 12 | `pv-diag-384::verified-adv-text-pro-vf-4of5` | 2 |  | 0.8792 | 0.8792 | +0.0000 | 0.7947 |
| 13 | `pv-diag-384::verified-adv-text-min-true-3of5` | 2 |  | 0.8784 | 0.8784 | +0.0000 | 0.7903 |
| 14 | `pv-diag-384::verified-adv-text-t03-4of5` | 2 |  | 0.8783 | 0.8783 | +0.0000 | 0.7834 |
| 15 | `pv-diag-384::verified-adv-text-6of10` | 2 |  | 0.8769 | 0.8769 | +0.0000 | 0.7903 |
| 16 | `verifier-robustness::verified-384-ge3of5-t0-3-high-n5` | 2 |  | 0.8764 | 0.8764 | +0.0000 | 0.789 |
| 17 | `verifier-robustness::verified-384-ge3of5-t0-3-n5` | 2 |  | 0.8739 | 0.8739 | +0.0000 | 0.7713 |
| 18 | `verifier-robustness::verified-384-ge3of5-t0-7-high-n5` | 2 |  | 0.8739 | 0.8739 | +0.0000 | 0.7927 |
| 19 | `verifier-robustness::verified-384-union-t0-0-n5` | 3 |  | 0.8722 | 0.8722 | +0.0000 | 0.7621 |
| 20 | `verifier-robustness::verified-384-ge3of5-t0-7-n5` | 3 |  | 0.8709 | 0.8709 | +0.0000 | 0.7713 |
| 21 | `pv-diag-384::verified-adv-text-min-n30lineage-4of5` | 3 |  | 0.8708 | 0.8708 | +0.0000 | 0.7873 |
| 22 | `flash35-pv-2x2::f3prop-f35vf-6of10` | 3 |  | 0.8689 | 0.8689 | +0.0000 | 0.7666 |
| 23 | `pv-diag-384::verified-adv-text-4of5` | 3 |  | 0.8641 | 0.8641 | +0.0000 | 0.7693 |
| 24 | `verifier-t-pilot::verified-t0-5` | 3 |  | 0.8561 | 0.8561 | +0.0000 | 0.7714 |
| 25 | `pv-diag-384::verified-adv-text-medium-vf-4of5` | 4 |  | 0.8545 | 0.8545 | +0.0000 | 0.7208 |
| 26 | `pv-diag-384::verified-adv-text-high-vf-4of5` | 4 |  | 0.8519 | 0.8519 | +0.0000 | 0.6992 |
| 27 | `verifier-t-pilot::verified-t0-0` | 4 |  | 0.8507 | 0.8507 | +0.0000 | 0.7778 |
| 28 | `pv-diag-384::verified-adv-pro-text-pro-vf-3of5` | 4 |  | 0.8506 | 0.8506 | +0.0000 | 0.7302 |
| 29 | `pv-diag-384::verified-adv-pro-text-medium-vf-3of5` | 4 |  | 0.8495 | 0.8495 | +0.0000 | 0.7302 |
| 30 | `pv-diag-384::verified-adv-pro-text-flash-vf-3of5` | 4 |  | 0.8491 | 0.8491 | +0.0000 | 0.7302 |
| 31 | `flash35-pv-2x2::f35prop-f3vf-4of10` | 4 |  | 0.8480 | 0.8480 | +0.0000 | 0.7675 |
| 32 | `verifier-t-pilot::verified-t1-0` | 4 |  | 0.8422 | 0.8422 | +0.0000 | 0.7562 |
| 33 | `flash35-pv-2x2::f35prop-f35vf-4of10` | 4 |  | 0.8362 | 0.8362 | +0.0000 | 0.7369 |
| 34 | `image-b-gs-2026-08-28::g384-ov192-image-min-k10-verified-p0.15-k9` | 4 |  | 0.8341 | 0.8412 | -0.0071 | 0.7927 |
| 35 | `image-b-gs-2026-08-28::g384-ov192-image-high-k10-verified-p0.20-k8` | 4 |  | 0.8263 | 0.8333 | -0.0070 | 0.7937 |
| 36 | `pv-diag-384::verified-adv-image-min-6of10` | 5 |  | 0.7890 | 0.7890 | +0.0000 | 0.8032 |
| 37 | `pv-diag-384::verified-adv-image-3of5` | 5 |  | 0.7778 | 0.7778 | +0.0000 | 0.8268 |
| 38 | `pv-diag-384::verified-adv-image-min-3of5` | 6 |  | 0.7673 | 0.7673 | +0.0000 | 0.8461 |
| 39 | `pv-diag-384::verified-adv-pro-image-pro-vf-3of5` | 6 |  | 0.7112 | 0.7112 | +0.0000 | 0.8499 |

Δ frame = board-frame F1 minus the committed evaluation's F1 (gate G6; the committed frame is the Era-2 frame for the incumbents and grid-common for the B-geometry cells). Full pairwise table: `tiering_20m.json`; gates: `gates.json`, `g1-regression.json`, `frame-deltas.md`; per-cell evaluations: `cells/`; reproduction evaluations: `g2/`.

## Changelog

### 2026-09-10 — Original publication

Built on sapphire per the card; all gates recorded in `provenance.json`.
