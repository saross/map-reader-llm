# The GS Era-2 verified board on one frame — `gs-era2-verified-board-2026-09-10`

> **Last revised**: 2026-09-13 (later still — **NOTE ONLY, still nothing rebuilt or re-signed**: the K = 3 cell's own `evaluation.json` is no longer blocked. The tile-join invariant now **withholds** a refused cell's per-tile statistics instead of aborting the cell, so `g37-text-k3-verified-opmax` was re-scored and its artefacts and register row read F1@20 **0.8860** / **495 detections**, with the tile block and every confidence interval marked WITHHELD. Two figures in the tables below still read `0.8870` and are correct as they stand: this board's `withheld_cells` row and `re_sign_pending.proposed_outcome` are signature-bearing and the PI restates them at the rebuild. Earlier that day — the recovery-fragment fix `75d7c8d4c` rebuilt five consensus unions that four of this board's cells read. Only `g37-text-k3-verified-opmax` moves — F1@20 0.8870 → **0.8860**, one added false positive — and it is one of the three cells already withheld; the single **tiered** cell of the four, `g384-ov192-k5-verified-opmax` at rank 9, re-scores **dict-identically** on every arm, so no rank, tier, pairwise test, BH family, MCB set or signature field changes. Per the PI's ruling the next rebuild picks these up; the pending record is `provenance.json` → `re_sign_pending.cells_pending_rescore` and the changelog entry below. Earlier that day: PI ruling 2026-09-13, item 1: the 46 Phase 2 rungs and the 4 tier E rungs of the K-ladder review admitted by route (a) — a `k-ladder/membership.json` the builder defers to by condition id — so 103 → **153 cells admitted**, of which **150 tiered** and **3 withheld** by the tile-join invariant; re-tiered and the MCB recomputed last; **Tier 1 and its five members unchanged**. The board's analysis row is again NOT amended and the board **awaits the PI's re-signature**, `provenance.json` → `re_sign_pending`; the resolved S153 block is preserved inside it as `previous_resolved`. Deltas: `reports/k-ladder-admission-deltas-2026-09-13.md`. Prior: 2026-09-12, PI ruling R3 — K = 1 admitted, 79 → 103 cells, re-signed 2026-09-12T06:04:30Z; 2026-09-11, off-board `pv-high-text-t0.0-n3` re-examined, nothing on the board changed; 2026-09-10 later still, nine `-opmax` cells re-materialised and re-tiered; later, the symmetry fix 39 → 79 cells; earlier that day, original publication). Card: `planning/gs-era2-verified-board-2026-09-08.md`. Frame: `inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson` (`era2-b-487`; the Era-2 carrier tiles clipped to the B tiling's union, 487 tiles, 1,402.4 km², 435 curator reference mounds). Instrument: scripts/era1_leaderboard_tiering.py (round-robin tile-swap micro-F1 permutation, BH q = 0.05, greedy clique, 20 m); Tier-1 membership is the MCB admissible set (E83). See [§ Changelog](#changelog).

**153 cells admitted**, of which **150 are tiered** and **3 withheld** (listed below the table); 7961/11175 pairs significant; 14 tiers; tie set 5; MCB admissible 65 of 150. 50 cell(s) admitted by `k-ladder/membership.json` with their board-frame evaluations as-is (PI ruling 2026-09-13).

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
| 9 | `grid-2026-08-18::g384-ov192-k5-verified-opmax` | 2 | ● | 0.8905 | 0.8905 | +0.0000 | 0.8139 |
| 10 | `pv-diag-384::verified-adv-text-consensus-16of30` | 2 | ● | 0.8902 | 0.8902 | +0.0000 | 0.7903 |
| 11 | `grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10` | 2 | ● | 0.8886 | 0.8961 | -0.0075 | 0.7903 |
| 12 | `pv-diag-384::pv-high-text-t0.3-n5-opmax` | 2 | ● | 0.8873 | 0.8873 | +0.0000 | 0.7805 |
| 13 | `pv-diag-384::session-78-text-comparative-opmax` | 2 | ● | 0.8846 | 0.8846 | +0.0000 | 0.7947 |
| 14 | `grid-2026-08-18::g384-ov192-k3-verified-opmax` | 3 | ● | 0.8840 | 0.8840 | +0.0000 | 0.8167 |
| 15 | `pv-diag-384::verified-adv-text-min-6of10` | 3 | ● | 0.8835 | 0.8835 | +0.0000 | 0.8068 |
| 16 | `pv-diag-384::session-78-text-adversarial-opmax` | 3 | ● | 0.8833 | 0.8833 | +0.0000 | 0.7947 |
| 17 | `pv-diag-384::pv-high-text-t1.0-n10-opmax` | 3 | ● | 0.8804 | 0.8804 | +0.0000 | 0.791 |
| 18 | `pv-diag-384::verified-adv-text-pro-vf-4of5` | 3 | ● | 0.8792 | 0.8792 | +0.0000 | 0.7947 |
| 19 | `pv-diag-384::verified-adv-text-min-true-3of5` | 3 | ● | 0.8784 | 0.8784 | +0.0000 | 0.7903 |
| 20 | `pv-diag-384::verified-adv-text-t03-4of5` | 3 | ● | 0.8783 | 0.8783 | +0.0000 | 0.7834 |
| 21 | `pv-diag-384::pv-high-text-t0.3-n3-opmax` | 3 | ● | 0.8783 | 0.8783 | +0.0000 | 0.8053 |
| 22 | `pv-diag-384::session-78-text-checklist-opmax` | 3 | ● | 0.8783 | 0.8783 | +0.0000 | 0.7759 |
| 23 | `pv-diag-384::pv-min-text-t1.0-n10-opmax` | 3 | ● | 0.8781 | 0.8781 | +0.0000 | 0.7881 |
| 24 | `pv-diag-384::pv-min-text-t0.3-n5-opmax` | 3 | ● | 0.8778 | 0.8778 | +0.0000 | 0.7735 |
| 25 | `pv-diag-384::verified-adv-text-6of10` | 3 | ● | 0.8769 | 0.8769 | +0.0000 | 0.7903 |
| 26 | `verifier-robustness::verified-384-ge3of5-t0-3-high-n5` | 3 | ● | 0.8764 | 0.8764 | +0.0000 | 0.789 |
| 27 | `pv-diag-384::session-78-text-brief-opmax` | 3 | ● | 0.8762 | 0.8762 | +0.0000 | 0.7659 |
| 28 | `pv-diag-384::pv-high-text-t0.7-n10-opmax` | 3 | ● | 0.8744 | 0.8744 | +0.0000 | 0.7641 |
| 29 | `verifier-robustness::verified-384-ge3of5-t0-3-n5` | 4 | ● | 0.8739 | 0.8739 | +0.0000 | 0.7713 |
| 30 | `verifier-robustness::verified-384-ge3of5-t0-7-high-n5` | 4 | ● | 0.8739 | 0.8739 | +0.0000 | 0.7927 |
| 31 | `pv-diag-384::pv-min-text-t0.7-n5-opmax` | 4 | ● | 0.8739 | 0.8739 | +0.0000 | 0.7957 |
| 32 | `pv-diag-384::pv-min-text-t0.3-n10-opmax` | 4 | ● | 0.8730 | 0.8730 | +0.0000 | 0.791 |
| 33 | `pv-diag-384::pv-min-text-t0.7-n10-opmax` | 4 | ● | 0.8726 | 0.8726 | +0.0000 | 0.7768 |
| 34 | `pv-diag-384::pv-min-text-t0.7-n3-opmax` | 4 | ● | 0.8725 | 0.8725 | +0.0000 | 0.791 |
| 35 | `verifier-robustness::verified-384-union-t0-0-n5` | 4 | ● | 0.8722 | 0.8722 | +0.0000 | 0.7621 |
| 36 | `pv-diag-384::pv-high-text-t0.3-n10-opmax` | 4 | ● | 0.8722 | 0.8722 | +0.0000 | 0.7872 |
| 37 | `pv-diag-384::pv-min-text-t1.0-n5-opmax` | 4 | ● | 0.8714 | 0.8714 | +0.0000 | 0.7797 |
| 38 | `verifier-robustness::verified-384-ge3of5-t0-7-n5` | 4 | ● | 0.8709 | 0.8709 | +0.0000 | 0.7713 |
| 39 | `pv-diag-384::verified-adv-text-min-n30lineage-4of5` | 4 | ● | 0.8708 | 0.8708 | +0.0000 | 0.7873 |
| 40 | `pv-diag-384::pv-min-text-t0.3-n3-opmax` | 4 | ● | 0.8708 | 0.8708 | +0.0000 | 0.804 |
| 41 | `flash35-pv-2x2::f3prop-f35vf-6of10` | 4 | ● | 0.8689 | 0.8689 | +0.0000 | 0.7666 |
| 42 | `pv-diag-384::pv-high-text-t1.0-n5-opmax` | 4 | ● | 0.8688 | 0.8688 | +0.0000 | 0.7857 |
| 43 | `pv-diag-384::pv-min-text-t1.0-n3-opmax` | 4 | ● | 0.8647 | 0.8647 | +0.0000 | 0.804 |
| 44 | `pv-diag-384::verified-adv-text-4of5` | 5 | ● | 0.8641 | 0.8641 | +0.0000 | 0.7693 |
| 45 | `pv-diag-384::session-78-text-checklist-text-opmax` | 5 | ● | 0.8639 | 0.8639 | +0.0000 | 0.7561 |
| 46 | `pv-diag-384::pv-high-text-t0.7-n5-opmax` | 5 | ● | 0.8634 | 0.8634 | +0.0000 | 0.7684 |
| 47 | `pv-diag-384::pv-min-text-t0.7-n3-carried-p0.15-k3` | 5 | ● | 0.8629 | 0.8629 | +0.0000 | 0.7665 |
| 48 | `pv-diag-384::pv-min-text-t0.0-n3-opmax` | 5 | ● | 0.8623 | 0.8623 | +0.0000 | 0.7834 |
| 49 | `pv-diag-384::session-78-text-adversarial-text-opmax` | 5 | ● | 0.8603 | 0.8603 | +0.0000 | 0.7534 |
| 50 | `pv-diag-384::pv-min-text-t0.3-n3-carried-p0.15-k3` | 5 | ● | 0.8586 | 0.8586 | +0.0000 | 0.7556 |
| 51 | `pv-diag-384::pv-min-text-t0.7-n1-opmax` | 5 | ● | 0.8575 | 0.8575 | +0.0000 | 0.7881 |
| 52 | `verifier-t-pilot::verified-t0-5` | 5 | ● | 0.8561 | 0.8561 | +0.0000 | 0.7714 |
| 53 | `pv-diag-384::pv-min-text-t0.3-n1-opmax` | 5 | ● | 0.8555 | 0.8555 | +0.0000 | 0.7986 |
| 54 | `grid-2026-08-18::g384-ov192-k1-verified-opmax` | 5 | ● | 0.8546 | 0.8546 | +0.0000 | 0.8211 |
| 55 | `pv-diag-384::verified-adv-text-medium-vf-4of5` | 5 | ● | 0.8545 | 0.8545 | +0.0000 | 0.7208 |
| 56 | `pv-diag-384::pv-high-text-t1.0-n3-opmax` | 5 | ● | 0.8541 | 0.8541 | +0.0000 | 0.7986 |
| 57 | `grid-2026-08-18::g384-ov192-k1-verified-p0.15-k1` | 5 | ● | 0.8540 | 0.8540 | +0.0000 | 0.8079 |
| 58 | `pv-diag-384::verified-adv-text-high-vf-4of5` | 5 | ● | 0.8519 | 0.8519 | +0.0000 | 0.6992 |
| 59 | `pv-diag-384::session-78-text-brief-text-opmax` | 5 | ● | 0.8519 | 0.8519 | +0.0000 | 0.7582 |
| 60 | `pv-diag-384::pv-high-text-t0.0-n3-recovery-2026-09-08-opmax` | 5 | ● | 0.8508 | 0.8508 | +0.0000 | 0.7857 |
| 61 | `verifier-t-pilot::verified-t0-0` | 5 | ● | 0.8507 | 0.8507 | +0.0000 | 0.7778 |
| 62 | `pv-diag-384::verified-adv-pro-text-pro-vf-3of5` | 5 | ● | 0.8506 | 0.8506 | +0.0000 | 0.7302 |
| 63 | `pv-diag-384::verified-adv-pro-text-medium-vf-3of5` | 5 | ● | 0.8495 | 0.8495 | +0.0000 | 0.7302 |
| 64 | `pv-diag-384::pv-high-text-t0.7-n3-opmax` | 5 | ● | 0.8492 | 0.8492 | +0.0000 | 0.7979 |
| 65 | `pv-diag-384::verified-adv-pro-text-flash-vf-3of5` | 5 | ● | 0.8491 | 0.8491 | +0.0000 | 0.7302 |
| 66 | `flash35-pv-2x2::f35prop-f3vf-4of10` | 5 |  | 0.8480 | 0.8480 | +0.0000 | 0.7675 |
| 67 | `verifier-t-pilot::verified-t1-0` | 5 |  | 0.8422 | 0.8422 | +0.0000 | 0.7562 |
| 68 | `pv-diag-384::pv-high-text-t0.7-n3-carried-p0.15-k3` | 6 |  | 0.8408 | 0.8408 | +0.0000 | 0.7762 |
| 69 | `flash35-pv-2x2::f35prop-f35vf-4of10` | 6 |  | 0.8362 | 0.8362 | +0.0000 | 0.7369 |
| 70 | `image-b-gs-2026-08-28::g384-ov192-image-min-k10-verified-p0.15-k9` | 6 |  | 0.8341 | 0.8412 | -0.0071 | 0.7927 |
| 71 | `pv-diag-384::pv-high-text-t0.3-n1-opmax` | 6 |  | 0.8314 | 0.8314 | +0.0000 | 0.8068 |
| 72 | `pv-diag-384::pv-high-text-t0.3-n1-carried-p0.15-k1` | 6 |  | 0.8301 | 0.8301 | +0.0000 | 0.8022 |
| 73 | `pv-diag-384::pv-min-text-t1.0-n3-carried-p0.15-k3` | 6 |  | 0.8279 | 0.8279 | +0.0000 | 0.7413 |
| 74 | `image-b-gs-2026-08-28::g384-ov192-image-high-k10-verified-p0.20-k8` | 6 |  | 0.8263 | 0.8333 | -0.0070 | 0.7937 |
| 75 | `pv-diag-384::verified-adv-text-baseline-pro-vf` | 6 |  | 0.8263 | 0.8263 | +0.0000 | 0.8328 |
| 76 | `pv-diag-384::verified-adv-text-baseline-medium-vf` | 6 |  | 0.8244 | 0.8244 | +0.0000 | 0.8372 |
| 77 | `pv-diag-384::pv-min-text-t1.0-n1-opmax` | 6 |  | 0.8235 | 0.8235 | +0.0000 | 0.8095 |
| 78 | `pv-diag-384::pv-high-text-t0.0-n3-opmax` | 6 |  | 0.8234 | 0.8234 | +0.0000 | 0.775 |
| 79 | `pv-diag-384::pv-min-text-t1.0-n1-carried-p0.15-k1` | 6 |  | 0.8228 | 0.8228 | +0.0000 | 0.7961 |
| 80 | `pv-diag-384::pv-high-text-t1.0-n3-carried-p0.15-k3` | 6 |  | 0.8220 | 0.8220 | +0.0000 | 0.7443 |
| 81 | `pv-diag-384::verified-adv-text-baseline` | 6 |  | 0.8142 | 0.8142 | +0.0000 | 0.8328 |
| 82 | `pv-diag-384::pv-high-text-t0.7-n1-opmax` | 7 |  | 0.8009 | 0.8009 | +0.0000 | 0.7737 |
| 83 | `pv-diag-384::verified-adv-image-min-6of10` | 7 |  | 0.7890 | 0.7890 | +0.0000 | 0.8032 |
| 84 | `pv-diag-384::pv-min-image-t0.7-n10-opmax` | 7 |  | 0.7881 | 0.7881 | +0.0000 | 0.8223 |
| 85 | `pv-diag-384::pv-high-image-t0.7-n5-opmax` | 7 |  | 0.7868 | 0.7868 | +0.0000 | 0.8359 |
| 86 | `pv-diag-384::session-78-image-adversarial-opmax` | 7 |  | 0.7866 | 0.7866 | +0.0000 | 0.8306 |
| 87 | `pv-diag-384::verified-adv-pro-text-baseline-pro-vf` | 7 |  | 0.7861 | 0.7861 | +0.0000 | 0.7908 |
| 88 | `pv-diag-384::session-78-image-comparative-opmax` | 7 |  | 0.7857 | 0.7857 | +0.0000 | 0.8306 |
| 89 | `pv-diag-384::session-78-image-checklist-text-opmax` | 7 |  | 0.7852 | 0.7852 | +0.0000 | 0.8217 |
| 90 | `pv-diag-384::session-78-image-brief-opmax` | 7 |  | 0.7844 | 0.7844 | +0.0000 | 0.83 |
| 91 | `pv-diag-384::verified-adv-pro-text-baseline-medium-vf` | 7 |  | 0.7842 | 0.7842 | +0.0000 | 0.7872 |
| 92 | `pv-diag-384::session-78-image-checklist-opmax` | 7 |  | 0.7830 | 0.7830 | +0.0000 | 0.8172 |
| 93 | `pv-diag-384::pv-min-image-t0.3-n10-opmax` | 7 |  | 0.7819 | 0.7819 | +0.0000 | 0.8377 |
| 94 | `pv-diag-384::pv-high-text-t1.0-n1-opmax` | 7 |  | 0.7810 | 0.7810 | +0.0000 | 0.8162 |
| 95 | `pv-diag-384::pv-high-text-t1.0-n1-carried-p0.15-k1` | 7 |  | 0.7788 | 0.7788 | +0.0000 | 0.8071 |
| 96 | `pv-diag-384::session-78-image-brief-text-opmax` | 7 |  | 0.7782 | 0.7782 | +0.0000 | 0.8199 |
| 97 | `pv-diag-384::verified-adv-image-3of5` | 7 |  | 0.7778 | 0.7778 | +0.0000 | 0.8268 |
| 98 | `pv-diag-384::pv-min-image-t0.3-n3-opmax` | 7 |  | 0.7774 | 0.7774 | +0.0000 | 0.8178 |
| 99 | `pv-diag-384::pv-min-image-t0.3-n5-opmax` | 7 |  | 0.7767 | 0.7767 | +0.0000 | 0.8416 |
| 100 | `pv-diag-384::pv-high-image-t0.7-n10-opmax` | 7 |  | 0.7765 | 0.7765 | +0.0000 | 0.798 |
| 101 | `pv-diag-384::pv-min-image-t0.7-n5-opmax` | 7 |  | 0.7734 | 0.7734 | +0.0000 | 0.8383 |
| 102 | `pv-diag-384::session-78-image-adversarial-text-opmax` | 8 |  | 0.7718 | 0.7718 | +0.0000 | 0.7973 |
| 103 | `pv-diag-384::pv-high-image-t0.3-n10-opmax` | 8 |  | 0.7705 | 0.7705 | +0.0000 | 0.8294 |
| 104 | `pv-diag-384::verified-adv-pro-text-baseline` | 8 |  | 0.7696 | 0.7696 | +0.0000 | 0.7823 |
| 105 | `pv-diag-384::pv-scale4-optimal-n10-opmax` | 8 |  | 0.7683 | 0.7683 | +0.0000 | 0.8154 |
| 106 | `pv-diag-384::pv-min-image-t0.3-n1-opmax` | 8 |  | 0.7680 | 0.7680 | +0.0000 | 0.8443 |
| 107 | `pv-diag-384::verified-adv-image-min-3of5` | 8 |  | 0.7673 | 0.7673 | +0.0000 | 0.8461 |
| 108 | `n1-outstanding-384::pv-n1-image-t0-n3-opmax` | 8 |  | 0.7673 | 0.7673 | +0.0000 | 0.8397 |
| 109 | `pv-diag-384::pv-high-image-t0.7-n3-opmax` | 8 |  | 0.7666 | 0.7666 | +0.0000 | 0.8435 |
| 110 | `pv-diag-384::pv-min-image-t0.3-n1-carried-p0.15-k1` | 8 |  | 0.7654 | 0.7654 | +0.0000 | 0.8475 |
| 111 | `pv-diag-384::pv-scale4-optimal-n5-opmax` | 8 |  | 0.7635 | 0.7635 | +0.0000 | 0.8306 |
| 112 | `pv-diag-384::pv-high-image-t1.0-n10-opmax` | 8 |  | 0.7633 | 0.7633 | +0.0000 | 0.8002 |
| 113 | `pv-diag-384::pv-min-image-t0.7-n3-opmax` | 8 |  | 0.7599 | 0.7599 | +0.0000 | 0.8377 |
| 114 | `pv-diag-384::pv-min-image-t0.7-n3-carried-p0.15-k3` | 8 |  | 0.7522 | 0.7522 | +0.0000 | 0.7994 |
| 115 | `pv-diag-384::pv-high-image-t0.3-n5-opmax` | 8 |  | 0.7475 | 0.7475 | +0.0000 | 0.8049 |
| 116 | `pv-diag-384::pv-min-image-t1.0-n10-opmax` | 8 |  | 0.7428 | 0.7428 | +0.0000 | 0.8078 |
| 117 | `pv-diag-384::pv-min-image-t1.0-n5-opmax` | 8 |  | 0.7384 | 0.7384 | +0.0000 | 0.8021 |
| 118 | `pv-diag-384::pv-high-image-t1.0-n5-opmax` | 9 |  | 0.7337 | 0.7337 | +0.0000 | 0.823 |
| 119 | `pv-diag-384::verified-adv-image-baseline-pro-vf` | 9 |  | 0.7309 | 0.7309 | +0.0000 | 0.8887 |
| 120 | `pv-diag-384::verified-adv-image-baseline-medium-vf` | 9 |  | 0.7300 | 0.7300 | +0.0000 | 0.8848 |
| 121 | `pv-diag-384::pv-scale4-optimal-n3-opmax` | 9 |  | 0.7296 | 0.7296 | +0.0000 | 0.8443 |
| 122 | `pv-diag-384::pv-min-image-t1.0-n3-opmax` | 9 |  | 0.7288 | 0.7288 | +0.0000 | 0.8178 |
| 123 | `pv-diag-384::pv-min-image-t0.7-n1-opmax` | 9 |  | 0.7252 | 0.7252 | +0.0000 | 0.8437 |
| 124 | `pv-diag-384::pv-high-image-t1.0-n3-opmax` | 9 |  | 0.7245 | 0.7245 | +0.0000 | 0.8294 |
| 125 | `pv-diag-384::pv-high-image-t0.3-n3-opmax` | 9 |  | 0.7215 | 0.7215 | +0.0000 | 0.8237 |
| 126 | `pv-diag-384::pv-high-image-t0.3-n3-carried-p0.15-k3` | 9 |  | 0.7207 | 0.7207 | +0.0000 | 0.7788 |
| 127 | `pv-diag-384::verified-adv-image-baseline` | 10 |  | 0.7167 | 0.7167 | +0.0000 | 0.8766 |
| 128 | `pv-diag-384::verified-adv-pro-image-pro-vf-3of5` | 10 |  | 0.7112 | 0.7112 | +0.0000 | 0.8499 |
| 129 | `pv-diag-384::pv-high-image-t0.7-n3-carried-p0.15-k3` | 10 |  | 0.7046 | 0.7046 | +0.0000 | 0.7621 |
| 130 | `pv-diag-384::pv-min-image-t1.0-n1-opmax` | 10 |  | 0.7044 | 0.7044 | +0.0000 | 0.836 |
| 131 | `pv-diag-384::pv-scale4-optimal-n3-carried-p0.15-k3` | 10 |  | 0.7019 | 0.7019 | +0.0000 | 0.7354 |
| 132 | `pv-diag-384::pv-min-image-t1.0-n3-carried-p0.15-k3` | 10 |  | 0.7016 | 0.7016 | +0.0000 | 0.7629 |
| 133 | `pv-diag-384::pv-high-image-t1.0-n3-carried-p0.15-k3` | 10 |  | 0.6955 | 0.6955 | +0.0000 | 0.7389 |
| 134 | `pv-diag-384::pv-high-image-t0.3-n1-opmax` | 10 |  | 0.6925 | 0.6925 | +0.0000 | 0.827 |
| 135 | `pv-diag-384::pv-high-image-t0.7-n1-opmax` | 10 |  | 0.6909 | 0.6909 | +0.0000 | 0.8435 |
| 136 | `pv-diag-384::pv-scale4-optimal-n1-opmax` | 11 |  | 0.6376 | 0.6376 | +0.0000 | 0.8726 |
| 137 | `pv-diag-384::pv-scale4-optimal-n1-carried-p0.15-k1` | 11 |  | 0.6350 | 0.6350 | +0.0000 | 0.8599 |
| 138 | `pv-diag-384::verified-adv-pro-image-baseline-medium-vf` | 11 |  | 0.6281 | 0.6281 | +0.0000 | 0.8328 |
| 139 | `pv-diag-384::verified-adv-pro-image-baseline` | 11 |  | 0.6196 | 0.6196 | +0.0000 | 0.8232 |
| 140 | `pv-diag-384::verified-adv-pro-image-baseline-pro-vf` | 12 |  | 0.6178 | 0.6178 | +0.0000 | 0.8328 |
| 141 | `pv-diag-384::pv-high-image-t1.0-n1-opmax` | 12 |  | 0.6119 | 0.6119 | +0.0000 | 0.864 |
| 142 | `pv-diag-384::pv-high-image-t1.0-n1-carried-p0.15-k1` | 12 |  | 0.6098 | 0.6098 | +0.0000 | 0.8601 |
| 143 | `proposer-verifier-384::verified-checklist-image` | 12 |  | 0.5309 | 0.5309 | +0.0000 | 0.3873 |
| 144 | `proposer-verifier-384::verified-checklist-text` | 13 |  | 0.5214 | 0.5214 | +0.0000 | 0.3154 |
| 145 | `proposer-verifier-384::verified-brief-image` | 13 |  | 0.5204 | 0.5204 | +0.0000 | 0.3402 |
| 146 | `proposer-verifier-384::verified-brief-text` | 13 |  | 0.5142 | 0.5142 | +0.0000 | 0.3953 |
| 147 | `proposer-verifier-384::verified-cascade-adversarial-checklist` | 13 |  | 0.5036 | 0.5036 | +0.0000 | 0.4313 |
| 148 | `proposer-verifier-384::verified-cascade-checklist-adversarial` | 13 |  | 0.4950 | 0.4950 | +0.0000 | 0.4121 |
| 149 | `proposer-verifier-384::verified-adversarial-image` | 13 |  | 0.4943 | 0.4943 | +0.0000 | 0.416 |
| 150 | `proposer-verifier-384::verified-adversarial-text` | 14 |  | 0.4708 | 0.4708 | +0.0000 | 0.4313 |

**Admitted but WITHHELD** — the tile-join invariant refuses these cells' per-tile table on this frame (their `source_tile` vocabulary is not the frame's), so they are ranked nowhere above and enter no BH family and no admissible set. Their whole-frame F1 is unaffected by the tile join and is quoted for reference; their committed tile-MCC is the pre-invariant value and is NOT published. Admission is the PI's ruling of 2026-09-13; the withholding follows the same ruling's "withhold and list, never abort the board", and is lifted only by the corpus-wide tile-join decision (close-out question 4).

| cell | F1@20 (whole frame) | committed tile-MCC (NOT published) | refusal |
|---|---:|---:|---|
| `g37-text-k1-verified-carried-p0.10-k1` | 0.8338 | 0.1422 | per-tile TP/FP/FN table refused: 22 of 526 in-frame detections were credited to a tile under the 'id' tile join, a shortfall of 504. (tile_join_detection_shortfall) Most often the cell's source_tile vocabulary is not this frame's; re-run with a geometric tile_join. |
| `g37-text-k1-verified-opmax` | 0.8495 | 0.1337 | per-tile TP/FP/FN table refused: 21 of 475 in-frame detections were credited to a tile under the 'id' tile join, a shortfall of 454. (tile_join_detection_shortfall) Most often the cell's source_tile vocabulary is not this frame's; re-run with a geometric tile_join. |
| `g37-text-k3-verified-opmax` | 0.8870 | 0.1337 | per-tile TP/FP/FN table refused: 20 of 467 in-frame detections were credited to a tile under the 'id' tile join, a shortfall of 447. (tile_join_detection_shortfall) Most often the cell's source_tile vocabulary is not this frame's; re-run with a geometric tile_join. |

Δ frame = board-frame F1 minus the committed evaluation's F1 (gate G6; the committed frame is the Era-2 frame for the incumbents and grid-common for the B-geometry cells; for the `-opmax` rows it is the Era-2-frame reproduction of the archived board's score, or — for the nine re-materialised on 2026-09-10 — of the materialisation registry's registered point). For the K-ladder rows it is +0.0000 by construction: their committed evaluation IS the board-frame evaluation, so G2 is an identity rather than a reproduction. Full pairwise table: `tiering_20m.json`; gates: `gates.json`, `opmax/gates.json`, `g1-regression.json`, `frame-deltas.md`; per-cell evaluations: `cells/`; reproduction evaluations: `g2/`, `opmax/g2/`.

## Changelog

### 2026-09-13 (later still) — the K = 3 cell's evaluation written; NOTE ONLY, the board is still not rebuilt

**Trigger**: the previous entry recorded one thing as *blocked* rather than
merely deferred — `g37-text-k3-verified-opmax`'s own `evaluation.json` could
not be regenerated, because the tile-join invariant refused its per-tile table
and, since the F1 bootstrap resamples **tiles**, the refusal aborted the whole
evaluation. Under checklist item 6a
(`planning/documentation-foundation-checklist-2026-09-13.md`) the invariant was
softened to match the PI's ruling of 2026-09-13 (S153 ruling 6): a refused cell
**withholds** its per-tile table, tile confusion, tile-MCC and every bootstrap
interval — naming the reason, the shortfall counts and both tile vocabularies —
and **reports its whole-frame F1, precision and recall in full**.

| artefact | before | after |
|---|---|---|
| the cell's `evaluation.json` F1@20 | 0.8870 (stale, unwritable) | **0.8860** |
| the cell's detections | 494 | **495** |
| the cell's tile-MCC | 0.1337 | **withheld**, reason named |
| the cell's bootstrap CIs | reported | **withheld** (they resample tiles) |
| `results/conditions-manifest.json` row | 0.8870 / 494 | **0.8860 / 495** |
| this board's `withheld_cells` row | 0.8870 | **0.8870 — unchanged, by design** |
| `re_sign_pending.proposed_outcome` | quotes 0.8870 | **unchanged, by design** |

The last two are the point of the entry. Both are **signature-bearing** and
were deliberately left alone: the PI restates them at the rebuild that picks
these cells up. Sixteen signature-bearing paths in `provenance.json` were
asserted byte-equal before and after the note was amended
(`results/k-ladder-2026-09-12/recovery-fix-2026-09-13/harness/resolve_board_note_block.py`),
and `re_sign_pending.cells_pending_rescore.blocked_artefact` was replaced by a
`resolved` record that states the discrepancy rather than papering over it.

**The previous CI is withdrawn, not superseded.** This cell used to carry a BCa
interval on F1@20 of [0.3684, 0.7732]. It was resampled from a per-tile table
the invariant refuses, so it is not replaced by a better interval — there is no
interval for this cell on this frame, and the artefact says so.

**What did NOT change**: every rank, tier, pairwise test, BH family, MCB
admissible set and signature field on this board; the 153 admitted / 150 tiered
counts and the 3-cell withheld list; the 14 tiers, 7961/11175 significant
pairs, tie set 5 and 65-of-150 MCB set; Tier 1 and its five members; and the
other three cells of the recovery-fragment set, whose live artefacts were not
rewritten.

### 2026-09-13 (later) — Four cells pending re-score after the recovery-fragment fix; NOTE ONLY, the board is not rebuilt

**Trigger**: the recovery-fragment fix
`75d7c8d4cd55b6ec8d2a40abff70a31f62b67725` rebuilt five committed
`merge_passes.py` consensus unions whose builder had been silently skipping
`run_<N>_recovery` fragments. Four cells on this board read them. Measured:
`results/k-ladder-2026-09-12/recovery-fix-2026-09-13/`; reported:
`reports/recovery-drop-fix-2026-09-13.md`.

**PI ruling 2026-09-13**: do **not** rebuild this board and do **not** re-tier
for this. The next board rebuild — the one that also adds the tile-MCC
permutation family — picks these cells up. Nothing here is re-signed, re-ranked
or re-gated; this entry and `provenance.json` →
`re_sign_pending.cells_pending_rescore` are the pending record.

| cell | F1@20 before | after | Δ | on this board |
|---|---:|---:|---:|---|
| `g37-text-k1-verified-opmax` | 0.8495 | 0.8495 | 0.0000 | withheld (not tiered) |
| `g37-text-k1-verified-carried-p0.10-k1` | 0.8338 | 0.8338 | 0.0000 | withheld (not tiered) |
| `g37-text-k3-verified-opmax` | 0.8870 | **0.8860** | **−0.0010** | withheld (not tiered) |
| `grid-2026-08-18::g384-ov192-k5-verified-opmax` | 0.8905 | 0.8905 | 0.0000 | **tiered — rank 9, tier 2, MCB-admissible** |

**Only one cell's F1 moves, and it is one of the three already withheld.** The
single tiered cell of the four re-scores **dict-identically** on every arm —
F1@20 0.8905, tile-MCC 0.8139, confusion 193/248/10/36, BCa CI
[0.8595, 0.9149], 435 detections — because the candidate the fix promoted to 5
votes carries probability 0.10 against that rung's prob ≥ 0.15 gate. So no rank,
no tier, no pairwise comparison, no BH family and no MCB admissible set on this
board is affected by any number that has actually changed.

`g37-text-k3-verified-opmax`'s −0.0010 comes from one added false positive
(494 → 495 detections; precision 0.8340 → 0.8323, recall unchanged at 0.9471).
Its `withheld_cells` entry still reads `eval_f1: 0.8870` and will until the
rebuild.

**Why this entry exists as well as the provenance block.** `finalise()` rebuilds
`provenance.json` from scratch and, while the `re_sign_pending` block is
`PENDING`, overwrites it outright rather than nesting it as
`previous_resolved` (`scripts/build_gs_era2_board.py:690-694`). A hand-added key
inside that block therefore does **not** survive the next rebuild, whereas
`finalise()` explicitly preserves an existing `## Changelog`
(`scripts/build_gs_era2_board.py:772-779`). This entry is the durable copy.

**Also pending, and blocked rather than merely deferred** — ⚠ **resolved later
the same day; see the entry above this one**:
`g37-text-k3-verified-opmax`'s own `evaluation.json` could not be regenerated —
the tile-join invariant refuses its per-tile table at HEAD and the F1 bootstrap
resamples tiles, so the whole evaluation aborts. Its
`results/conditions-manifest.json` row therefore still reads 0.8870 / 494.
Refreshing it needs the tile-join ruling
(`reports/tile-mcc-geometric-join-2026-09-12.md`, still carrying a STOP).

**What did NOT change**: every signature field — `signed_at` is still
`2026-09-12T06:04:30Z`, `signature_history` untouched, `gates.G1.pi_ruling`
untouched, `re_sign_pending.status` still `PENDING — the PI re-signs`; the whole
`tiering` and `membership` blocks; all 153 admitted and 150 tiered counts; the
3-cell withheld list; the 14 tiers, 7961/11175 significant pairs, tie set 5 and
65-of-150 MCB admissible set; and Tier 1 with its five members.

### 2026-09-13 — The K-ladder cohort admitted (PI ruling, route (a)): 103 → 153 cells admitted, 150 tiered; Tier 1 unchanged

**Trigger**: the PI's ruling of 2026-09-13 (morning) on question 1 of
`reports/k-ladder-closeout-deltas-2026-09-12.md` § 10 — **route (a)**: a third
membership source this builder defers to by condition id, exactly as it already
defers to `opmax/membership.json`. The cohort is the **46 Phase 2 rungs** and the
**4 tier E rungs** of `planning/k-ladder-review-2026-09-11.md`, all 50 of which
`derive_membership()` had refused on two rules that are correct for the rows they
were written for but that refuse these cells **for already being on the board's
own frame**.

**The mechanism, and what it did not relax.**
`k-ladder/membership.json` names the 50 ids with a reason each, derived from the
register by `scripts/author_k_ladder_board_membership.py` (every verified
condition whose committed `eval_path` is under `results/k-ladder-2026-09-12/` and
whose `scope_override` names `era2-b-487`, with each evaluation opened and its
bounds checked; 0 refused). The deferral is checked **before** the frame and
`scope_override` rules, and **both rules still apply to every other row** — the
exclusion list still records 160 refusals with their reasons, 60 of them the
frame rule on this builder's own `-era2b` rows. **Nothing was re-scored** (these
evaluations already carry the board frame, the curator reference, 14 buffers, a
10,000-draw bootstrap, seed 42 and `--mcc`), and **no `-era2b` row was minted**:
that suffix records a second scoring, there is none here, and two register rows
must not claim one evaluation file — so the cohort joins under its own condition
ids. G2 is therefore an identity and G6's delta is 0.0000 by construction for
these 50 cells; G3 is still read off each file.

| Quantity | before | after |
|---|---:|---:|
| Cells **admitted** | 103 | **153** |
| Cells **tiered** | 103 | **150** |
| Cells **withheld** | 0 | **3** |
| — by builder source | 60 `-era2b` + 43 `-opmax` | **60 `-era2b` + 50 K-ladder + 43 `-opmax`** |
| Pairs significant at BH q = 0.05 | 1,845 / 3,081 → 3,651 / 5,253 | **7,961 / 11,175** |
| Tiers (count) | 12 | **14** |
| Tier 1 (greedy clique) | the five 3.7/3.8 cells | **the same five, same order, same F1** |
| Tie set | 5 | **5** |
| Top cell | `g37-image-k5-verified-swap37-p0.90-k5` 0.9233 | **the same cell, 0.9233** |
| Hsu MCB admissible set | 49 of 103 (w_upper 0.0736) | **65 of 150 (w_upper 0.0749)** |
| Two-sided MCB band | 55 | **70** |
| Gates | G2 0 / G3 0 / G4 60 + 43 | **G2 0 / G3 0 / G4 110 / 110** |
| G6 max abs frame delta | 0.0078 | 0.0078 |

**Three cells are admitted and WITHHELD, and this is not what the close-out
predicted.** That report expected the three Gemini 3.7 gold-standard text rungs
to abort the tiering through an uncaught `ConfusionGateError` on the MCC arm, so
that catching it would leave their F1 intact with tile-MCC withheld. They in fact
abort earlier, on the **F1** arm, in `compute_per_tile_tp_fp_fn`, with a plain
`ValueError` stamped `tile_join_detection_shortfall` — `assign_source_tiles`
preserves a non-null `source_tile` column instead of re-joining it to the frame,
so a stale vocabulary reaches the booking step and 20–22 of 467–526 in-frame
detections are credited to a tile. Their whole **per-tile table** is therefore
unavailable on this frame: no permutation test, no BH family, no admissible set.
Their whole-frame F1 is unaffected (F1 is scored map-scoped) and is quoted in the
table below the ranking; their committed tile-MCC is the pre-invariant value and
is **not** published. Measured across all 50 admitted cells, exactly these three
refuse: the four tier E cells carry **no** `source_tile` and are joined
geometrically from the frame, and the 43 `pv-diag-384` cells already speak the
frame's vocabulary. Lifting the withholding needs the corpus-wide tile-join
decision (close-out question 4, still open).

**The MCB grew again, and again because the candidate set did.** 49 of 103 → 65
of 150, upper width 0.0736 → 0.0749. The 2026-09-12 entry below explains the
mechanism: a simultaneous band widened to cover more candidates admits more of
them. The added cells here are a mixture rather than uniformly weak, so the width
moved much less than it did when the twenty K = 1 cells joined.

**Two instrument choices, recorded because a later reader will ask.** (1) The
tiering was run **without** `--permute-mcc`, exactly as the committed 2026-09-12
run was: the tile-MCC column here is read from each cell's evaluation, and adding
an MCC permutation family to a signed board is a change the PI did not rule.
(2) `finalise` now carries `signature_history` forward and nests the **resolved**
`re_sign_pending` inside the fresh PENDING one — without that fix this rebuild
would have destroyed the record of the board's original 2026-09-10 signature.
The run's own output confirms it: "carried forward from the previous
provenance.json: signed_at, signature_history, re_sign_pending (resolved, nested
as previous_resolved), gates.G1.pi_ruling".

**What did NOT change**: Tier 1 and its five members; the tie set; the top cell
and its F1; every gate's verdict; G6's maximum frame delta; the frame, the
reference, the instrument, the seed and the permutation count; and every
signature field. No incumbent cell left the board and none changed its F1. The
analysis row was not amended — the tiering and the MCB read their membership from
`tiering-input/run-analyses.json` (153 ids) — so the board awaits the PI's
re-signature.

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
The analysis row remains UNSIGNED; the publication ruling is the PI's. [Superseded the same evening: signed 2026-09-10T12:34:56Z — see the "Signed" entry above.]

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
The analysis row remains UNSIGNED; the publication ruling is the PI's. [Superseded the same evening: signed 2026-09-10T12:34:56Z — see the "Signed" entry above.]

### 2026-09-10 — Original publication

Built on sapphire per the card; all gates recorded in `provenance.json`.
