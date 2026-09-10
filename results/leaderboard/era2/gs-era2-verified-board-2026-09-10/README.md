# The GS Era-2 verified board on one frame — `gs-era2-verified-board-2026-09-10`

> **Last revised**: 2026-09-10 (later: the symmetry fix — the archived Era-2 PV board's 40 sweep-optimal Gemini 3 cells joined as `-opmax` rows, 39 → 79 cells, re-tiered, MCB recomputed last; earlier the same day: original publication). Card: `planning/gs-era2-verified-board-2026-09-08.md`. Frame: `inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson` (`era2-b-487`; the Era-2 carrier tiles clipped to the B tiling's union, 487 tiles, 1,402.4 km², 435 curator reference mounds). Instrument: scripts/era1_leaderboard_tiering.py (round-robin tile-swap micro-F1 permutation, BH q = 0.05, greedy clique, 20 m); Tier-1 membership is the MCB admissible set (E83). See [§ Changelog](#changelog).

79 cells; 1853/3081 pairs significant; 7 tiers; tie set 5; MCB admissible 28.

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
| 11 | `pv-diag-384::pv-high-text-t0.3-n5-opmax` | 2 | ● | 0.8863 | 0.8863 | +0.0000 | 0.7759 |
| 12 | `pv-diag-384::session-78-text-comparative-opmax` | 2 | ● | 0.8846 | 0.8846 | +0.0000 | 0.7947 |
| 13 | `pv-diag-384::verified-adv-text-min-6of10` | 2 | ● | 0.8835 | 0.8835 | +0.0000 | 0.8068 |
| 14 | `pv-diag-384::session-78-text-adversarial-opmax` | 2 | ● | 0.8833 | 0.8833 | +0.0000 | 0.7947 |
| 15 | `pv-diag-384::pv-high-text-t1.0-n10-opmax` | 2 | ● | 0.8804 | 0.8804 | +0.0000 | 0.791 |
| 16 | `pv-diag-384::verified-adv-text-pro-vf-4of5` | 2 | ● | 0.8792 | 0.8792 | +0.0000 | 0.7947 |
| 17 | `pv-diag-384::verified-adv-text-min-true-3of5` | 2 | ● | 0.8784 | 0.8784 | +0.0000 | 0.7903 |
| 18 | `pv-diag-384::verified-adv-text-t03-4of5` | 2 | ● | 0.8783 | 0.8783 | +0.0000 | 0.7834 |
| 19 | `pv-diag-384::session-78-text-checklist-opmax` | 2 | ● | 0.8783 | 0.8783 | +0.0000 | 0.7759 |
| 20 | `pv-diag-384::pv-min-text-t0.3-n5-opmax` | 2 | ● | 0.8778 | 0.8778 | +0.0000 | 0.7735 |
| 21 | `pv-diag-384::pv-min-text-t1.0-n10-opmax` | 2 | ● | 0.8771 | 0.8771 | +0.0000 | 0.7815 |
| 22 | `pv-diag-384::verified-adv-text-6of10` | 3 | ● | 0.8769 | 0.8769 | +0.0000 | 0.7903 |
| 23 | `verifier-robustness::verified-384-ge3of5-t0-3-high-n5` | 3 | ● | 0.8764 | 0.8764 | +0.0000 | 0.789 |
| 24 | `pv-diag-384::session-78-text-brief-opmax` | 3 | ● | 0.8762 | 0.8762 | +0.0000 | 0.7659 |
| 25 | `pv-diag-384::pv-high-text-t0.7-n10-opmax` | 3 | ● | 0.8744 | 0.8744 | +0.0000 | 0.7641 |
| 26 | `verifier-robustness::verified-384-ge3of5-t0-3-n5` | 3 | ● | 0.8739 | 0.8739 | +0.0000 | 0.7713 |
| 27 | `verifier-robustness::verified-384-ge3of5-t0-7-high-n5` | 3 | ● | 0.8739 | 0.8739 | +0.0000 | 0.7927 |
| 28 | `pv-diag-384::pv-min-text-t0.7-n5-opmax` | 3 | ● | 0.8732 | 0.8732 | +0.0000 | 0.7862 |
| 29 | `pv-diag-384::pv-min-text-t0.7-n10-opmax` | 3 |  | 0.8726 | 0.8726 | +0.0000 | 0.7768 |
| 30 | `verifier-robustness::verified-384-union-t0-0-n5` | 3 |  | 0.8722 | 0.8722 | +0.0000 | 0.7621 |
| 31 | `pv-diag-384::pv-high-text-t0.3-n10-opmax` | 3 |  | 0.8722 | 0.8722 | +0.0000 | 0.7872 |
| 32 | `pv-diag-384::pv-min-text-t1.0-n5-opmax` | 3 |  | 0.8714 | 0.8714 | +0.0000 | 0.7797 |
| 33 | `verifier-robustness::verified-384-ge3of5-t0-7-n5` | 3 |  | 0.8709 | 0.8709 | +0.0000 | 0.7713 |
| 34 | `pv-diag-384::verified-adv-text-min-n30lineage-4of5` | 3 |  | 0.8708 | 0.8708 | +0.0000 | 0.7873 |
| 35 | `flash35-pv-2x2::f3prop-f35vf-6of10` | 3 |  | 0.8689 | 0.8689 | +0.0000 | 0.7666 |
| 36 | `pv-diag-384::pv-min-text-t0.3-n10-opmax` | 3 |  | 0.8682 | 0.8682 | +0.0000 | 0.7731 |
| 37 | `pv-diag-384::verified-adv-text-4of5` | 4 |  | 0.8641 | 0.8641 | +0.0000 | 0.7693 |
| 38 | `pv-diag-384::session-78-text-checklist-text-opmax` | 4 |  | 0.8639 | 0.8639 | +0.0000 | 0.7561 |
| 39 | `pv-diag-384::pv-high-text-t0.7-n5-opmax` | 4 |  | 0.8634 | 0.8634 | +0.0000 | 0.7684 |
| 40 | `pv-diag-384::pv-high-text-t1.0-n5-opmax` | 4 |  | 0.8607 | 0.8607 | +0.0000 | 0.7567 |
| 41 | `pv-diag-384::session-78-text-adversarial-text-opmax` | 4 |  | 0.8603 | 0.8603 | +0.0000 | 0.7534 |
| 42 | `verifier-t-pilot::verified-t0-5` | 4 |  | 0.8561 | 0.8561 | +0.0000 | 0.7714 |
| 43 | `pv-diag-384::verified-adv-text-medium-vf-4of5` | 4 |  | 0.8545 | 0.8545 | +0.0000 | 0.7208 |
| 44 | `pv-diag-384::verified-adv-text-high-vf-4of5` | 4 |  | 0.8519 | 0.8519 | +0.0000 | 0.6992 |
| 45 | `pv-diag-384::session-78-text-brief-text-opmax` | 4 |  | 0.8519 | 0.8519 | +0.0000 | 0.7582 |
| 46 | `verifier-t-pilot::verified-t0-0` | 4 |  | 0.8507 | 0.8507 | +0.0000 | 0.7778 |
| 47 | `pv-diag-384::verified-adv-pro-text-pro-vf-3of5` | 4 |  | 0.8506 | 0.8506 | +0.0000 | 0.7302 |
| 48 | `pv-diag-384::verified-adv-pro-text-medium-vf-3of5` | 4 |  | 0.8495 | 0.8495 | +0.0000 | 0.7302 |
| 49 | `pv-diag-384::verified-adv-pro-text-flash-vf-3of5` | 4 |  | 0.8491 | 0.8491 | +0.0000 | 0.7302 |
| 50 | `flash35-pv-2x2::f35prop-f3vf-4of10` | 4 |  | 0.8480 | 0.8480 | +0.0000 | 0.7675 |
| 51 | `verifier-t-pilot::verified-t1-0` | 4 |  | 0.8422 | 0.8422 | +0.0000 | 0.7562 |
| 52 | `flash35-pv-2x2::f35prop-f35vf-4of10` | 4 |  | 0.8362 | 0.8362 | +0.0000 | 0.7369 |
| 53 | `image-b-gs-2026-08-28::g384-ov192-image-min-k10-verified-p0.15-k9` | 4 |  | 0.8341 | 0.8412 | -0.0071 | 0.7927 |
| 54 | `image-b-gs-2026-08-28::g384-ov192-image-high-k10-verified-p0.20-k8` | 5 |  | 0.8263 | 0.8333 | -0.0070 | 0.7937 |
| 55 | `pv-diag-384::verified-adv-image-min-6of10` | 5 |  | 0.7890 | 0.7890 | +0.0000 | 0.8032 |
| 56 | `pv-diag-384::pv-min-image-t0.7-n10-opmax` | 5 |  | 0.7881 | 0.7881 | +0.0000 | 0.8223 |
| 57 | `pv-diag-384::pv-high-image-t0.7-n5-opmax` | 5 |  | 0.7868 | 0.7868 | +0.0000 | 0.8359 |
| 58 | `pv-diag-384::session-78-image-adversarial-opmax` | 5 |  | 0.7866 | 0.7866 | +0.0000 | 0.8306 |
| 59 | `pv-diag-384::session-78-image-comparative-opmax` | 5 |  | 0.7857 | 0.7857 | +0.0000 | 0.8306 |
| 60 | `pv-diag-384::session-78-image-checklist-text-opmax` | 5 |  | 0.7852 | 0.7852 | +0.0000 | 0.8217 |
| 61 | `pv-diag-384::session-78-image-brief-opmax` | 5 |  | 0.7844 | 0.7844 | +0.0000 | 0.83 |
| 62 | `pv-diag-384::session-78-image-checklist-opmax` | 5 |  | 0.7830 | 0.7830 | +0.0000 | 0.8172 |
| 63 | `pv-diag-384::pv-min-image-t0.3-n10-opmax` | 5 |  | 0.7819 | 0.7819 | +0.0000 | 0.8377 |
| 64 | `pv-diag-384::session-78-image-brief-text-opmax` | 6 |  | 0.7782 | 0.7782 | +0.0000 | 0.8199 |
| 65 | `pv-diag-384::verified-adv-image-3of5` | 6 |  | 0.7778 | 0.7778 | +0.0000 | 0.8268 |
| 66 | `pv-diag-384::pv-min-image-t0.3-n5-opmax` | 6 |  | 0.7767 | 0.7767 | +0.0000 | 0.8416 |
| 67 | `pv-diag-384::pv-high-image-t0.7-n10-opmax` | 6 |  | 0.7761 | 0.7761 | +0.0000 | 0.7969 |
| 68 | `pv-diag-384::pv-min-image-t0.7-n5-opmax` | 6 |  | 0.7734 | 0.7734 | +0.0000 | 0.8383 |
| 69 | `pv-diag-384::session-78-image-adversarial-text-opmax` | 6 |  | 0.7718 | 0.7718 | +0.0000 | 0.7973 |
| 70 | `pv-diag-384::pv-high-image-t0.3-n10-opmax` | 6 |  | 0.7689 | 0.7689 | +0.0000 | 0.8154 |
| 71 | `pv-diag-384::pv-scale4-optimal-n10-opmax` | 6 |  | 0.7683 | 0.7683 | +0.0000 | 0.8154 |
| 72 | `pv-diag-384::verified-adv-image-min-3of5` | 6 |  | 0.7673 | 0.7673 | +0.0000 | 0.8461 |
| 73 | `pv-diag-384::pv-high-image-t1.0-n10-opmax` | 6 |  | 0.7633 | 0.7633 | +0.0000 | 0.8002 |
| 74 | `pv-diag-384::pv-scale4-optimal-n5-opmax` | 6 |  | 0.7629 | 0.7629 | +0.0000 | 0.8352 |
| 75 | `pv-diag-384::pv-high-image-t0.3-n5-opmax` | 6 |  | 0.7475 | 0.7475 | +0.0000 | 0.8049 |
| 76 | `pv-diag-384::pv-min-image-t1.0-n10-opmax` | 7 |  | 0.7409 | 0.7409 | +0.0000 | 0.8105 |
| 77 | `pv-diag-384::pv-min-image-t1.0-n5-opmax` | 7 |  | 0.7384 | 0.7384 | +0.0000 | 0.8021 |
| 78 | `pv-diag-384::pv-high-image-t1.0-n5-opmax` | 7 |  | 0.7337 | 0.7337 | +0.0000 | 0.823 |
| 79 | `pv-diag-384::verified-adv-pro-image-pro-vf-3of5` | 7 |  | 0.7112 | 0.7112 | +0.0000 | 0.8499 |

Δ frame = board-frame F1 minus the committed evaluation's F1 (gate G6; the committed frame is the Era-2 frame for the incumbents and grid-common for the B-geometry cells; for the `-opmax` rows it is the Era-2-frame reproduction of the archived board's score). Full pairwise table: `tiering_20m.json`; gates: `gates.json`, `opmax/gates.json`, `g1-regression.json`, `frame-deltas.md`; per-cell evaluations: `cells/`; reproduction evaluations: `g2/`, `opmax/g2/`.

## Changelog

### 2026-09-10 (later) — Symmetry fix: both families at both levels; 79 cells

**Trigger**: PI, 2026-09-10 — the 3.7/3.8 cells are the screens' sweep-best
points (in-sample optima, E56 class) while the Gemini 3 incumbents were
committed operating points (only the 16of30 opmax a sweep optimum). Fix:
the archived per-architecture Era-2 PV board's sweep-optimal Gemini 3 cells
registered as `-opmax` rows (`scripts/build_gs_era2_board_opmax.py`;
`opmax/membership.json`, gates in `opmax/gates.json`: 40/40 archived scores
reproduce on the Era-2 frame, every board evaluation on the board frame,
opmax cells identical on both frames), 43 rows minted, 40 join under the
card's K ≥ 5 rule; re-tiered by the same chain; the Hsu MCB set recomputed
LAST on the final membership (PI rule: the admissible set is a property of
the candidate set, so only the final one is cited).

| Quantity | 39-cell board | 79-cell board |
|---|---:|---:|
| Pairs significant at BH q = 0.05 | 375 / 741 | 1,853 / 3,081 |
| Tiers | 6 | 7 |
| Tier 1 (greedy clique) | the five 3.7/3.8 cells | **the same five** |
| Best Gemini 3 sweep optimum | — | `pv-high-text-t0.3-n5-opmax` 0.8863, rank 11, Tier 2 |
| Hsu MCB admissible set | 11 (band 22; w_upper 0.0439) | 28 (band 39; w_upper 0.0501) |
| Board argmax optimism (Efron–Gong over the board) | +0.0051 → corrected 0.9182 | +0.0051 → corrected 0.9181 |

Of the 40 opmax cells, 31 are significantly below the LOWEST Tier-1 cell
(`g37-text-k10-verified-carried-p0.10-k10`, 0.9068) and all 40 below the
top cell (0.9233); the nine not separable from the lowest Tier-1 cell are
text sweep optima at 0.8744–0.8863 (best: Δ +0.0205, p = 0.16). Nine of
the 39 incumbents moved down one tier as the opmax cells interleaved
(none moved up; Tiers 1–2 membership among incumbents unchanged). The
28-cell admissible set holds the seven 3.7/3.8 cells, ten Gemini 3
committed cells, the 16of30 opmax, and ten text sweep optima: the band
widened from 0.0439 to 0.0501 as 40 near-tied candidates were added, the
behaviour the PI's rule anticipates. **Sweep optimism of the screen cells**
(`optimism/README.md`, `scripts/selection_aware_intervals.py --sweep-union`,
gates reproduce each screen's committed sweep row for row): +0.0006 to
+0.0035 for the seven 3.7/3.8 cells (corrected board-frame F1 0.9027 to
0.9215), +0.0018 to +0.0056 for the three Gemini 3 B-geometry sweep cells.
G1 re-read the same day: the archived board's one moved cell was a stale
label-keyed cache, not instrument drift (`g1-regression.json` `bisect`,
`g1-confirmatory-rebuild.json`: 44/44 from the inputs actually scored). The
39-cell artefacts are snapshotted under
`archive/superseded-leaderboards/gs-era2-verified-board-2026-09-10-39cell/`.
The analysis row remains UNSIGNED; the publication ruling is the PI's.

### 2026-09-10 — Original publication

Built on sapphire per the card; all gates recorded in `provenance.json`.
