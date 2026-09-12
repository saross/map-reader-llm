# The GS Era-2 verified board on one frame — `gs-era2-verified-board-2026-09-10`

> **Last revised**: 2026-09-12 (PI ruling R3: K = 1 admitted, 79 → 103 cells, re-tiered and the MCB recomputed last — Tier 1 and its five members unchanged; **the board's analysis row is NOT amended and the board awaits the PI's re-signature**, `provenance.json` → `re_sign_pending`. Prior: 2026-09-11, off-board `pv-high-text-t0.0-n3` re-examined, nothing on the board changed; 2026-09-10 later still, nine `-opmax` cells re-materialised and re-tiered; later, the symmetry fix 39 → 79 cells; earlier that day, original publication). Card: `planning/gs-era2-verified-board-2026-09-08.md`. Frame: `inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson` (`era2-b-487`; the Era-2 carrier tiles clipped to the B tiling's union, 487 tiles, 1,402.4 km², 435 curator reference mounds). Instrument: scripts/era1_leaderboard_tiering.py (round-robin tile-swap micro-F1 permutation, BH q = 0.05, greedy clique, 20 m); Tier-1 membership is the MCB admissible set (E83). See [§ Changelog](#changelog).

103 cells; 3651/5253 pairs significant; 12 tiers; tie set 5; MCB admissible 49.

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
| 11 | `pv-diag-384::pv-high-text-t0.3-n5-opmax` | 2 | ● | 0.8873 | 0.8873 | +0.0000 | 0.7805 |
| 12 | `pv-diag-384::session-78-text-comparative-opmax` | 2 | ● | 0.8846 | 0.8846 | +0.0000 | 0.7947 |
| 13 | `pv-diag-384::verified-adv-text-min-6of10` | 2 | ● | 0.8835 | 0.8835 | +0.0000 | 0.8068 |
| 14 | `pv-diag-384::session-78-text-adversarial-opmax` | 2 | ● | 0.8833 | 0.8833 | +0.0000 | 0.7947 |
| 15 | `pv-diag-384::pv-high-text-t1.0-n10-opmax` | 2 | ● | 0.8804 | 0.8804 | +0.0000 | 0.791 |
| 16 | `pv-diag-384::verified-adv-text-pro-vf-4of5` | 2 | ● | 0.8792 | 0.8792 | +0.0000 | 0.7947 |
| 17 | `pv-diag-384::verified-adv-text-min-true-3of5` | 2 | ● | 0.8784 | 0.8784 | +0.0000 | 0.7903 |
| 18 | `pv-diag-384::verified-adv-text-t03-4of5` | 2 | ● | 0.8783 | 0.8783 | +0.0000 | 0.7834 |
| 19 | `pv-diag-384::session-78-text-checklist-opmax` | 2 | ● | 0.8783 | 0.8783 | +0.0000 | 0.7759 |
| 20 | `pv-diag-384::pv-min-text-t1.0-n10-opmax` | 2 | ● | 0.8781 | 0.8781 | +0.0000 | 0.7881 |
| 21 | `pv-diag-384::pv-min-text-t0.3-n5-opmax` | 2 | ● | 0.8778 | 0.8778 | +0.0000 | 0.7735 |
| 22 | `pv-diag-384::verified-adv-text-6of10` | 3 | ● | 0.8769 | 0.8769 | +0.0000 | 0.7903 |
| 23 | `verifier-robustness::verified-384-ge3of5-t0-3-high-n5` | 3 | ● | 0.8764 | 0.8764 | +0.0000 | 0.789 |
| 24 | `pv-diag-384::session-78-text-brief-opmax` | 3 | ● | 0.8762 | 0.8762 | +0.0000 | 0.7659 |
| 25 | `pv-diag-384::pv-high-text-t0.7-n10-opmax` | 3 | ● | 0.8744 | 0.8744 | +0.0000 | 0.7641 |
| 26 | `verifier-robustness::verified-384-ge3of5-t0-3-n5` | 3 | ● | 0.8739 | 0.8739 | +0.0000 | 0.7713 |
| 27 | `verifier-robustness::verified-384-ge3of5-t0-7-high-n5` | 3 | ● | 0.8739 | 0.8739 | +0.0000 | 0.7927 |
| 28 | `pv-diag-384::pv-min-text-t0.7-n5-opmax` | 3 | ● | 0.8739 | 0.8739 | +0.0000 | 0.7957 |
| 29 | `pv-diag-384::pv-min-text-t0.3-n10-opmax` | 3 | ● | 0.8730 | 0.8730 | +0.0000 | 0.791 |
| 30 | `pv-diag-384::pv-min-text-t0.7-n10-opmax` | 3 | ● | 0.8726 | 0.8726 | +0.0000 | 0.7768 |
| 31 | `verifier-robustness::verified-384-union-t0-0-n5` | 3 | ● | 0.8722 | 0.8722 | +0.0000 | 0.7621 |
| 32 | `pv-diag-384::pv-high-text-t0.3-n10-opmax` | 3 | ● | 0.8722 | 0.8722 | +0.0000 | 0.7872 |
| 33 | `pv-diag-384::pv-min-text-t1.0-n5-opmax` | 3 | ● | 0.8714 | 0.8714 | +0.0000 | 0.7797 |
| 34 | `verifier-robustness::verified-384-ge3of5-t0-7-n5` | 3 | ● | 0.8709 | 0.8709 | +0.0000 | 0.7713 |
| 35 | `pv-diag-384::verified-adv-text-min-n30lineage-4of5` | 3 | ● | 0.8708 | 0.8708 | +0.0000 | 0.7873 |
| 36 | `flash35-pv-2x2::f3prop-f35vf-6of10` | 3 | ● | 0.8689 | 0.8689 | +0.0000 | 0.7666 |
| 37 | `pv-diag-384::pv-high-text-t1.0-n5-opmax` | 3 | ● | 0.8688 | 0.8688 | +0.0000 | 0.7857 |
| 38 | `pv-diag-384::verified-adv-text-4of5` | 4 | ● | 0.8641 | 0.8641 | +0.0000 | 0.7693 |
| 39 | `pv-diag-384::session-78-text-checklist-text-opmax` | 4 | ● | 0.8639 | 0.8639 | +0.0000 | 0.7561 |
| 40 | `pv-diag-384::pv-high-text-t0.7-n5-opmax` | 4 | ● | 0.8634 | 0.8634 | +0.0000 | 0.7684 |
| 41 | `pv-diag-384::pv-min-text-t0.0-n3-opmax` | 4 | ● | 0.8623 | 0.8623 | +0.0000 | 0.7834 |
| 42 | `pv-diag-384::session-78-text-adversarial-text-opmax` | 4 | ● | 0.8603 | 0.8603 | +0.0000 | 0.7534 |
| 43 | `verifier-t-pilot::verified-t0-5` | 4 | ● | 0.8561 | 0.8561 | +0.0000 | 0.7714 |
| 44 | `pv-diag-384::verified-adv-text-medium-vf-4of5` | 4 | ● | 0.8545 | 0.8545 | +0.0000 | 0.7208 |
| 45 | `pv-diag-384::verified-adv-text-high-vf-4of5` | 4 | ● | 0.8519 | 0.8519 | +0.0000 | 0.6992 |
| 46 | `pv-diag-384::session-78-text-brief-text-opmax` | 4 | ● | 0.8519 | 0.8519 | +0.0000 | 0.7582 |
| 47 | `pv-diag-384::pv-high-text-t0.0-n3-recovery-2026-09-08-opmax` | 4 | ● | 0.8508 | 0.8508 | +0.0000 | 0.7857 |
| 48 | `verifier-t-pilot::verified-t0-0` | 4 | ● | 0.8507 | 0.8507 | +0.0000 | 0.7778 |
| 49 | `pv-diag-384::verified-adv-pro-text-pro-vf-3of5` | 4 | ● | 0.8506 | 0.8506 | +0.0000 | 0.7302 |
| 50 | `pv-diag-384::verified-adv-pro-text-medium-vf-3of5` | 4 |  | 0.8495 | 0.8495 | +0.0000 | 0.7302 |
| 51 | `pv-diag-384::verified-adv-pro-text-flash-vf-3of5` | 4 |  | 0.8491 | 0.8491 | +0.0000 | 0.7302 |
| 52 | `flash35-pv-2x2::f35prop-f3vf-4of10` | 4 |  | 0.8480 | 0.8480 | +0.0000 | 0.7675 |
| 53 | `verifier-t-pilot::verified-t1-0` | 4 |  | 0.8422 | 0.8422 | +0.0000 | 0.7562 |
| 54 | `flash35-pv-2x2::f35prop-f35vf-4of10` | 4 |  | 0.8362 | 0.8362 | +0.0000 | 0.7369 |
| 55 | `image-b-gs-2026-08-28::g384-ov192-image-min-k10-verified-p0.15-k9` | 4 |  | 0.8341 | 0.8412 | -0.0071 | 0.7927 |
| 56 | `image-b-gs-2026-08-28::g384-ov192-image-high-k10-verified-p0.20-k8` | 5 |  | 0.8263 | 0.8333 | -0.0070 | 0.7937 |
| 57 | `pv-diag-384::verified-adv-text-baseline-pro-vf` | 5 |  | 0.8263 | 0.8263 | +0.0000 | 0.8328 |
| 58 | `pv-diag-384::verified-adv-text-baseline-medium-vf` | 5 |  | 0.8244 | 0.8244 | +0.0000 | 0.8372 |
| 59 | `pv-diag-384::pv-high-text-t0.0-n3-opmax` | 5 |  | 0.8234 | 0.8234 | +0.0000 | 0.775 |
| 60 | `pv-diag-384::verified-adv-text-baseline` | 5 |  | 0.8142 | 0.8142 | +0.0000 | 0.8328 |
| 61 | `pv-diag-384::verified-adv-image-min-6of10` | 5 |  | 0.7890 | 0.7890 | +0.0000 | 0.8032 |
| 62 | `pv-diag-384::pv-min-image-t0.7-n10-opmax` | 5 |  | 0.7881 | 0.7881 | +0.0000 | 0.8223 |
| 63 | `pv-diag-384::pv-high-image-t0.7-n5-opmax` | 5 |  | 0.7868 | 0.7868 | +0.0000 | 0.8359 |
| 64 | `pv-diag-384::session-78-image-adversarial-opmax` | 5 |  | 0.7866 | 0.7866 | +0.0000 | 0.8306 |
| 65 | `pv-diag-384::verified-adv-pro-text-baseline-pro-vf` | 5 |  | 0.7861 | 0.7861 | +0.0000 | 0.7908 |
| 66 | `pv-diag-384::session-78-image-comparative-opmax` | 5 |  | 0.7857 | 0.7857 | +0.0000 | 0.8306 |
| 67 | `pv-diag-384::session-78-image-checklist-text-opmax` | 5 |  | 0.7852 | 0.7852 | +0.0000 | 0.8217 |
| 68 | `pv-diag-384::session-78-image-brief-opmax` | 5 |  | 0.7844 | 0.7844 | +0.0000 | 0.83 |
| 69 | `pv-diag-384::verified-adv-pro-text-baseline-medium-vf` | 5 |  | 0.7842 | 0.7842 | +0.0000 | 0.7872 |
| 70 | `pv-diag-384::session-78-image-checklist-opmax` | 5 |  | 0.7830 | 0.7830 | +0.0000 | 0.8172 |
| 71 | `pv-diag-384::pv-min-image-t0.3-n10-opmax` | 6 |  | 0.7819 | 0.7819 | +0.0000 | 0.8377 |
| 72 | `pv-diag-384::session-78-image-brief-text-opmax` | 6 |  | 0.7782 | 0.7782 | +0.0000 | 0.8199 |
| 73 | `pv-diag-384::verified-adv-image-3of5` | 6 |  | 0.7778 | 0.7778 | +0.0000 | 0.8268 |
| 74 | `pv-diag-384::pv-min-image-t0.3-n5-opmax` | 6 |  | 0.7767 | 0.7767 | +0.0000 | 0.8416 |
| 75 | `pv-diag-384::pv-high-image-t0.7-n10-opmax` | 6 |  | 0.7765 | 0.7765 | +0.0000 | 0.798 |
| 76 | `pv-diag-384::pv-min-image-t0.7-n5-opmax` | 6 |  | 0.7734 | 0.7734 | +0.0000 | 0.8383 |
| 77 | `pv-diag-384::session-78-image-adversarial-text-opmax` | 6 |  | 0.7718 | 0.7718 | +0.0000 | 0.7973 |
| 78 | `pv-diag-384::pv-high-image-t0.3-n10-opmax` | 6 |  | 0.7705 | 0.7705 | +0.0000 | 0.8294 |
| 79 | `pv-diag-384::verified-adv-pro-text-baseline` | 6 |  | 0.7696 | 0.7696 | +0.0000 | 0.7823 |
| 80 | `pv-diag-384::pv-scale4-optimal-n10-opmax` | 6 |  | 0.7683 | 0.7683 | +0.0000 | 0.8154 |
| 81 | `pv-diag-384::verified-adv-image-min-3of5` | 6 |  | 0.7673 | 0.7673 | +0.0000 | 0.8461 |
| 82 | `n1-outstanding-384::pv-n1-image-t0-n3-opmax` | 6 |  | 0.7673 | 0.7673 | +0.0000 | 0.8397 |
| 83 | `pv-diag-384::pv-scale4-optimal-n5-opmax` | 6 |  | 0.7635 | 0.7635 | +0.0000 | 0.8306 |
| 84 | `pv-diag-384::pv-high-image-t1.0-n10-opmax` | 6 |  | 0.7633 | 0.7633 | +0.0000 | 0.8002 |
| 85 | `pv-diag-384::pv-high-image-t0.3-n5-opmax` | 6 |  | 0.7475 | 0.7475 | +0.0000 | 0.8049 |
| 86 | `pv-diag-384::pv-min-image-t1.0-n10-opmax` | 7 |  | 0.7428 | 0.7428 | +0.0000 | 0.8078 |
| 87 | `pv-diag-384::pv-min-image-t1.0-n5-opmax` | 7 |  | 0.7384 | 0.7384 | +0.0000 | 0.8021 |
| 88 | `pv-diag-384::pv-high-image-t1.0-n5-opmax` | 7 |  | 0.7337 | 0.7337 | +0.0000 | 0.823 |
| 89 | `pv-diag-384::verified-adv-image-baseline-pro-vf` | 7 |  | 0.7309 | 0.7309 | +0.0000 | 0.8887 |
| 90 | `pv-diag-384::verified-adv-image-baseline-medium-vf` | 7 |  | 0.7300 | 0.7300 | +0.0000 | 0.8848 |
| 91 | `pv-diag-384::verified-adv-image-baseline` | 8 |  | 0.7167 | 0.7167 | +0.0000 | 0.8766 |
| 92 | `pv-diag-384::verified-adv-pro-image-pro-vf-3of5` | 8 |  | 0.7112 | 0.7112 | +0.0000 | 0.8499 |
| 93 | `pv-diag-384::verified-adv-pro-image-baseline-medium-vf` | 9 |  | 0.6281 | 0.6281 | +0.0000 | 0.8328 |
| 94 | `pv-diag-384::verified-adv-pro-image-baseline` | 9 |  | 0.6196 | 0.6196 | +0.0000 | 0.8232 |
| 95 | `pv-diag-384::verified-adv-pro-image-baseline-pro-vf` | 10 |  | 0.6178 | 0.6178 | +0.0000 | 0.8328 |
| 96 | `proposer-verifier-384::verified-checklist-image` | 10 |  | 0.5309 | 0.5309 | +0.0000 | 0.3873 |
| 97 | `proposer-verifier-384::verified-checklist-text` | 11 |  | 0.5214 | 0.5214 | +0.0000 | 0.3154 |
| 98 | `proposer-verifier-384::verified-brief-image` | 11 |  | 0.5204 | 0.5204 | +0.0000 | 0.3402 |
| 99 | `proposer-verifier-384::verified-brief-text` | 11 |  | 0.5142 | 0.5142 | +0.0000 | 0.3953 |
| 100 | `proposer-verifier-384::verified-cascade-adversarial-checklist` | 11 |  | 0.5036 | 0.5036 | +0.0000 | 0.4313 |
| 101 | `proposer-verifier-384::verified-cascade-checklist-adversarial` | 11 |  | 0.4950 | 0.4950 | +0.0000 | 0.4121 |
| 102 | `proposer-verifier-384::verified-adversarial-image` | 11 |  | 0.4943 | 0.4943 | +0.0000 | 0.416 |
| 103 | `proposer-verifier-384::verified-adversarial-text` | 12 |  | 0.4708 | 0.4708 | +0.0000 | 0.4313 |

Δ frame = board-frame F1 minus the committed evaluation's F1 (gate G6; the committed frame is the Era-2 frame for the incumbents and grid-common for the B-geometry cells; for the `-opmax` rows it is the Era-2-frame reproduction of the archived board's score, or — for the nine re-materialised on 2026-09-10 — of the materialisation registry's registered point). Full pairwise table: `tiering_20m.json`; gates: `gates.json`, `opmax/gates.json`, `g1-regression.json`, `frame-deltas.md`; per-cell evaluations: `cells/`; reproduction evaluations: `g2/`, `opmax/g2/`.

## Changelog

### 2026-09-12 — K = 1 admitted (PI ruling R3): 79 → 103 cells; Tier 1 unchanged

**Trigger**: ruling R3 of the K-ladder review
(`planning/k-ladder-review-2026-09-11.md` § 4): "the ladder carries K = 1, AND a
K = 1 cell that earns a place on a board is admitted … under 'ladder, then
board' the board takes every verified cell on its frame regardless of K". The
board's twenty single-pass exclusions were a scope choice of the inventory
builder (architecture class), not a statistical one.

**What was excluded twice.** `scripts/build_gs_era2_board.py` held K = 1 out by
run and label (`proposer-verifier-384`, every `*baseline*` label) AND by a
generic `K >= 5` gate, so removing the first alone would have changed nothing.
`MIN_K` is now **1** in both builders. A row whose K cannot be read at all is
still excluded: an unknown pass count is not a K of 1.

**The two builders also needed an explicit divide.** Until now it was
accidental — every `-opmax` row carried a board-frame evaluation and so failed
the main builder's frame rule, and the three K = 3 `-opmax` rows left on the
Era-2 frame were held out by the K gate. With `MIN_K = 1` those three would have
joined twice, with different recorded K, because the main builder's label parser
reads `-n1-` out of `pv-n1-image-t0-n3-opmax` and returns 1 for a K = 3 cell. The
main builder now reads `opmax/membership.json` and defers to it **by condition
id**, not by a `-opmax` suffix — that suffix is also sanctioned for rows this
builder owns, such as the September `-recovery-<date>-opmax` pair.

**The 24 cells that joined**: twenty single-pass proposer + verifier cells (eight
of `proposer-verifier-384`, twelve `pv-diag-384::verified-adv-*-baseline*`), the
three K = 3 archived sweep optima promoted from off-board
(`pv-min-text-t0.0-n3-opmax`, `pv-high-text-t0.0-n3-opmax`,
`pv-n1-image-t0-n3-opmax`), and
`pv-diag-384::pv-high-text-t0.0-n3-recovery-2026-09-08-opmax`, the September
re-verification registered this session under rulings B2 and R4. All 48 scoring
jobs ran on sapphire with the board's own recipe; 0 failures.

| Quantity | before | after |
|---|---:|---:|
| Cells | 79 | **103** |
| — of which `-era2b` / `-opmax` | 39 / 40 | **60 / 43** |
| Pairs significant at BH q = 0.05 | 1,845 / 3,081 | **3,651 / 5,253** |
| Tiers (count) | 7 | **12** |
| Tier 1 (greedy clique) | the five 3.7/3.8 cells | **the same five, same order, same F1** |
| Tie set | 5 | 5 |
| Top cell | `g37-image-k5-verified-swap37-p0.90-k5` 0.9233 | **the same cell, 0.9233** |
| Hsu MCB admissible set | 28 of 79 (w_upper 0.05011) | **49 of 103 (w_upper 0.0736)** |
| Two-sided MCB band | 40 | 55 |
| Gates | G2 0 / G3 0 / G4 39+40 | **G2 0 / G3 0 / G4 60 + 43** |
| G6 max abs frame delta | 0.0078 | 0.0078 |

**What did NOT change**: Tier 1 and its five members; the tie set; the top cell
and its F1; every gate's verdict; G6's maximum frame delta; the frame, the
reference, the instrument, the seed and the permutation count. No incumbent cell
left the board and none changed its F1.

**One result to read carefully, and it is a property of the method.** The Hsu
admissible set grew from 28 of 79 to 49 of 103, and its upper width from 0.0501
to 0.0736 — it became *more* permissive as the candidate set gained cells that are
much WEAKER (the twenty K = 1 cells score F1@20 0.4708–0.8263, against a board
top of 0.9233). That is the multiple-comparisons-with-the-best construction
behaving as designed: widening the simultaneous band to cover more candidates
admits more of them. The 2026-09-10 entry below anticipated the direction when 40
near-tied cells were added; the effect is larger here because the added cells are
far from the best, not near it. It is an argument for stating which candidate set
an admissible set was computed over — never for reporting the more flattering of
two sets.

**The analysis row was NOT amended, and the board is NOT re-signed.** The row is
PI-signed (`manually_verified_at` 2026-09-10T12:34:56Z), and amending a signed
row's membership, note or outcome is the PI's call — the precedent is
`reports/r7-gaps-deltas-2026-09-11.md` § 5.1. So: the tiering and the MCB read
their membership from `tiering-input/run-analyses.json`, a board-local copy with
one field substituted (`scripts/build_board_tiering_input.py`); `signed_at` and
`gates.G1.pi_ruling` are carried forward into `provenance.json` rather than
rebuilt away; and the proposed outcome text sits under
`provenance.json` → `re_sign_pending` for the PI to apply. The 79-cell artefacts
are snapshotted under
`archive/superseded-leaderboards/gs-era2-verified-board-2026-09-10-79cell-pre-k1/`.

**One defect fixed while rebuilding** (Finding 2 and fix 3 of
`reports/name-keyed-cache-audit-2026-09-12.md`): `archived_cells()` read each
archived cell's `n_detections` from the Obs 464 label-keyed cache, which has no
content key. For `pv-high-image-t0.3-n5` the cache's stale 372 agreed with the
registry's 372 and so SUPPRESSED the `differs` verdict the file's real 373
features should have raised — and that verdict is what decides whether a row is
re-pointed at a re-materialised file. `archived_n` is now counted from the file
the row names. Exactly one of the 44 archived rows changes verdict:
`pv-high-image-t0.3-n5`, `"match"` → `"differs: registry F1 0.746 n 372 vs
archived board F1 0.746 n 373"`. Its `detections` path does not move (no
re-materialised file exists for it), the G2 gate already used the bisect's
expected 373, and no F1 anywhere changed. Four tier-1 tests pin the behaviour.

### 2026-09-11 — Off-board `pv-high-text-t0.0-n3`: a rebuilt union, not a stale sweep; board untouched

**Nothing on this board changed.** The row is off-board (K = 3 < 5), so no
cell, rank, tier, tie set or MCB member moved; the 79-cell table above stands
as published.

The 2026-09-10 entry below reported one `-opmax` row whose filter gave 410
detections against a registered 403, and classed it as a stale sweep (Obs 461).
It is not. The union at its `consensus_path` was re-materialised on 2026-07-30
from 1,256 features to 1,319 **in a different order** — only 994 of the 1,256
original positions still hold the same point — so joining union index *i* to
probability key `candidate_{i:05d}` pairs 262 probabilities with the wrong
geometry. The 410 is a cross-vintage join artefact.

The sweep itself reproduces exactly: rebuilt from the union blob at `09fe46a7f`
and swept against the stage's own probabilities with the stage's own tool, it
matches the committed `sweep_2d.json` in all 240 rows, at the registered
(vote_t 3, prob_t 0.15), n 403, F1@20 0.8234. The argmax also holds on the
current vintage — the complete 2026-09-08 re-verification of the rebuilt union
gives (3, 0.15) at n 423, Era-2-frame F1@20 0.8508, tile-MCC 0.7857 (against
0.8234 / 0.7750). The row was **not** repointed: on its own vintage it is
correct, and repointing would change it from the archived board's April cell to
a September re-verification. That call is the PI's; both sweeps, the comparison
cell and its score are at `opmax/staleness-2026-09-11/`.

A vintage guard now runs before the filter
(`scripts/materialise_opmax_cells.py`, `check.json` field `vintage`;
`scripts/check_pv_sweep_vintage.py survey`): over the 30 registry cells, 24
`same-vintage`, 4 `probabilities-grew` (join sound, sweep stale — the true
Obs 461 class, all four already re-swept 2026-09-08), 1 `union-rebuilt` (this
cell, join invalid, no count published), 1 `manifest-mode`. `opmax/gates.json`
re-run: G2 0 / G3 0 / G4 40/40 PASS, unchanged.

### 2026-09-10 (later still) — Nine `-opmax` cells re-materialised; re-tiered; Tier 1 and the admissible set unchanged

**Trigger**: the nine `-opmax` rows flagged in the entry below as carrying a
`sweep_2d.json` best point that "differs from the materialised file" were
re-examined. The diagnosis reverses that reading: the sweep is right and the
2026-04-19 materialisation (`bd24293d4`) is wrong. Re-applying the
materialisation registry's own filter — join the proposer pool union
(`consensus_path`) to the verifier stage's `probabilities.json` by candidate
index (union feature *i* ↔ key `candidate_{i:05d}`), keep
`vote_count >= vote_t AND mound_probability >= prob_t` at the registered point
— reproduces the registry's detection count **exactly for all nine**, while
the archived file holds a different set (up to 50 detections apart). The
unions, probabilities and sweeps are unchanged since 2026-04-17/18; only the
materialisation moved. The nine were rebuilt from their registered stage
(`scripts/materialise_opmax_cells.py`, provenance sidecar per cell recording
every input's git blob hash) and re-scored on both frames with the board's
recipe. Running the same filter over the other 34 rows: 33 reproduce their
archived file exactly; the one that does not is off-board (see below).

| cell | rank | tier | n | F1@20 |
|---|---|---|---|---|
| `pv-high-text-t0.3-n5-opmax` | 11 → 11 | 2 → 2 | 409 → 408 | 0.8863 → 0.8873 |
| `pv-min-text-t1.0-n10-opmax` | 21 → 20 | 2 → 2 | 395 → 410 | 0.8771 → 0.8781 |
| `pv-min-text-t0.7-n5-opmax` | 28 → 28 | 3 → 3 | 385 → 382 | 0.8732 → 0.8739 |
| `pv-min-text-t0.3-n10-opmax` | 36 → 29 | 3 → 3 | 392 → 431 | 0.8682 → 0.8730 |
| `pv-high-text-t1.0-n5-opmax` | 40 → 37 | 4 → **3** | 376 → 426 | 0.8607 → 0.8688 |
| `pv-high-image-t0.7-n10-opmax` | 67 → 67 | 6 → 6 | 351 → 348 | 0.7761 → 0.7765 |
| `pv-high-image-t0.3-n10-opmax` | 70 → 70 | 6 → 6 | 400 → 432 | 0.7689 → 0.7705 |
| `pv-scale4-optimal-n5-opmax` | 74 → 73 | 6 → 6 | 396 → 398 | 0.7629 → 0.7635 |
| `pv-min-image-t1.0-n10-opmax` | 76 → 76 | 7 → **6** | 364 → 397 | 0.7409 → 0.7428 |

All nine move up, by +0.0004 to +0.0081 — the direction the diagnosis
predicts, since the registered point is its sweep's F1@20 argmax while the
superseded file held some other set. Each cell's Era-2-frame F1@20 now equals
the registry's `best_at_20m.f1` exactly (`opmax/gates.json`: G2 0 failures, G3
0, G4 40/40), and board-frame equals Era-2-frame as for every `-opmax` cell.

**Board effects** (re-tiered by the same chain, MCB recomputed last):

| Quantity | before | after |
|---|---:|---:|
| Cells | 79 | 79 |
| Pairs significant at BH q = 0.05 | 1,853 / 3,081 | 1,845 / 3,081 |
| Tiers (sizes) | 7 (5/16/15/17/10/12/4) | 7 (5/16/16/16/10/14/2) |
| Tier 1 (greedy clique) | the five 3.7/3.8 cells | **the same five** |
| Tie set | 5 | 5 |
| Best Gemini 3 sweep optimum | `pv-high-text-t0.3-n5-opmax` 0.8863, rank 11, Tier 2 | **the same cell** 0.8873, rank 11, Tier 2 |
| `-opmax` cells significantly below the lowest Tier-1 cell | 31 of 40 | 30 of 40 |
| `-opmax` cells significantly below the top cell | 40 of 40 | 40 of 40 |
| Hsu MCB admissible set | 28 (w_upper 0.05012) | 28, **the same members** (w_upper 0.05011) |
| Two-sided MCB band | 39 | 40 (`pv-high-text-t1.0-n5-opmax` joins) |
| Board argmax optimism (Efron–Gong) | +0.0051 → corrected 0.9181 | +0.0051 → corrected 0.9181 |

**What did NOT change**: Tier 1 and its five members; the tie set; the top
five cells and their F1; the Hsu admissible set's size AND membership; the
board argmax's optimism and corrected F1; every `-era2b` incumbent's tier
(no incumbent moved). Three cells changed tier, all `-opmax`: two of the nine
moved up (`pv-high-text-t1.0-n5-opmax` 4 → 3, `pv-min-image-t1.0-n10-opmax`
7 → 6) and `pv-min-image-t1.0-n5-opmax` followed them up 7 → 6 as Tier 7
shrank to two members. The sweep-optimism analysis (`optimism/`) covers the
3.7/3.8 screen cells and the three Gemini 3 B-geometry sweep cells, none of
them among the nine, and is unaffected.

**One row deliberately left alone**: the same filter over
`pv-high-text-t0.0-n3` (off-board, K = 3) yields 410 against 403 in both its
registry row and its archived file. Its proposer consensus union was
re-materialised on 2026-07-30 (`f6116cba0`, `77bb342b4`) — the union is newer
than both the sweep and the materialisation, the opposite direction from the
nine. It is reported in `opmax/materialised/check.json`, not rewritten: it is
off-board, its registry and its file agree with one another, and the call is
the PI's. The superseded evaluations and a note on the diagnosis are under
`archive/superseded-leaderboards/gs-era2-verified-board-2026-09-10-opmax-stale-materialisation/`;
the 79-cell artefacts built on the stale materialisation are under
`archive/superseded-leaderboards/gs-era2-verified-board-2026-09-10-79cell-stale-materialisation/`.
The analysis row remains UNSIGNED; the publication ruling is the PI's.

### 2026-09-10 (evening) — Signed

The PI ruled G1 satisfied on the true-input reproduction and signed the analysis row at 2026-09-10T12:34:56Z; the ruling text is in `provenance.json` under `gates.G1.pi_ruling` and in the card's § 9.

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
