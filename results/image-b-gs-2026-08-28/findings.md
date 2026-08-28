# Image on the leading geometry: modality and thinking, both answered

> **Last revised**: 2026-08-28 (original publication). See
> [§ Changelog](#changelog) for revision history.

**Classification**: registered-by-commit exploratory extension (card:
`planning/image-b-gs-2026-08-28.md`, § 3 predictions IP1–IP5 committed
before the MINIMAL launch, § 5a predictions HP1–HP5 committed before
the HIGH launch; PI approvals in-session 2026-08-28). Two cells on the
Gold Standard (GS) 4-map corpus, both byte-matched to the committed
text-B anchor (`results/grid-2026-08-18/conditions-verified/
g384_ov192`, F1@20 m 0.8961) except the declared bundle:

- **image-MINIMAL**: `detect_brief-text-image` (the 17-example twin of
  the leading text config), K = 10, T = 0.7, explicit context caching.
- **image-HIGH**: identical plus one flag (`--thinking-level high`).

## Headline results (F1@20 m, common footprint, curator GT)

| Cell | Verified best | Point | P | R | tile-MCC | Union | All-in flex (audited) |
|---|---:|---|---:|---:|---:|---:|---:|
| text-B (committed anchor) | **0.8961** | — | 0.9275 | 0.8668 | 0.7965 | 3,319 | — |
| image-MINIMAL | 0.8412 | (0.15, k9) | 0.8741 | 0.8107 | **0.7985** | 4,065 | ~$25 |
| image-HIGH | 0.8333 | (0.20, k8) | 0.8625 | 0.8061 | 0.7993 | 9,189 | ~$65 |

## The modality verdict (IP1–IP5)

| # | Bet | Observed | Verdict |
|---|---|---|---|
| IP1 | text > image at ≤ 30 m | +0.0549 @20 m, **p = 0.0010**; +0.0379 @30 m | **CONFIRMED** — large enough to clear even GS resolution |
| IP2 | gap narrows monotonically 20 → 75 m | 0.0549 → 0.0379 → 0.0282 → 0.0258 | **CONFIRMED** |
| IP3 | image MCC within ±0.02 | 0.7985 vs 0.7965 (+0.002, nominally higher) | **CONFIRMED** |
| IP4 | prob_t ∈ {0.15, 0.20} | 0.15 | **CONFIRMED** |
| IP5 | image saturates slower (N3 outside noise of N10) | N3 − N10 = −0.0159, p = 0.069; N5 − N10 = −0.0030, p = 0.745 | **NOT confirmed at GS power** — suggestive, in the GS indeterminate zone (see the sensitivity appendix) |

Buffer curves (text minus image-MINIMAL): the deficit halves from
20 m to 75 m, so much of image's loss is coarse localisation rather
than failure to find mound neighbourhoods — and tile-MCC parity says
the neighbourhood-level signal is fully intact. The historical image
profile (MCC-strong, localisation-weak), reproduced on the new
geometry at MINIMAL thinking with everything matched.

Image needs the ensemble far more than text: its N = 1 rung collapses
to 0.6974 (text N = 1: 0.8594, the committed GS ladder), consensus
rescues it by +0.14, and its best point sits at near-unanimity.

## The thinking verdict (HP1–HP5)

| # | Bet | Observed | Verdict |
|---|---|---|---|
| HP1 | HIGH ≈ MINIMAL at verified best | 0.8333 vs 0.8412; ΔF1 −0.0079, p = 0.62 | **CONFIRMED** — HIGH nominally WORSE |
| HP2 | union ≥ +20 % | 4,065 → 9,189 (**+126 %**), growth concentrated in singletons (1,938 → 6,751) | **CONFIRMED** |
| HP3 | MCC ± 0.02 | +0.0008 | **CONFIRMED** |
| HP4 | lattice point | (0.20, k8) | **CONFIRMED** |
| HP5 | proposer cost 3.0–3.5× | 2.91× ($59.07 vs $20.3 audited) | narrow miss, just under |

**The mechanism, now demonstrated on both tracks**: HIGH thinking buys
enormous proposer-side diversity that the carry-forward verifier then
entirely absorbs — at the verified operating point the thinking
dividend is gone. This is the S111 recall-ceiling finding (text, GS)
reproduced as a matched pair on the image track. Image-HIGH also
saturates completely by N = 5 (N5 − N10 = −0.0002, p = 0.97). The
pre-named informative failure (HIGH > MIN by > 0.03) did not occur.

## What the paper can now say

1. **Text is stronger than image for mound localisation under the
   leading configuration** (+0.055 at 20 m, p = 0.001, matched
   everything), while **image matches text on tile-level
   discrimination** (MCC parity) — the deficit is localisation, not
   detection.
2. **Under a proposer–verifier architecture, MINIMAL thinking
   suffices in both modalities**; the ~3× thinking premium buys
   pre-verifier diversity the verifier discards (−0.008 ns at the
   verified best).
3. The verified-set GS instrument resolves these effects cleanly
   (null σ ≈ 0.0087 — see
   `results/sensitivity-mde-2026-08-28/sensitivity-mde.md`); the one
   indeterminate result (IP5) sits exactly in the GS indeterminate
   zone and is stated as such.

## Method and gates

- Proposer runs: 2 × 13,980 calls (1,398 tiles × K = 10), real-time
  flex, explicit context caching (~94 % of input tokens cached),
  E72 coverage exact after single-tile recoveries (6 MINIMAL,
  5 HIGH). Configs verified by dry-run + live pricing probes; the
  `include_example_images` key made explicit after an audit-config
  blocker (H10/H12 error class).
- Unions: the stride/grid chain unchanged (E80 20 m within-pass
  dedup, carrier clip, c = 1 with `vote_count`).
- Verifier: carry-forward `verify_adversarial-text`, T = 0.0, MINIMAL,
  n = 1; 4,065 + 9,189 calls, zero failures, key sets exact.
- Analysis (`image_b_analysis.py`, `image_b_pair.py`): join +
  reassignment gates; **anchor gate** — the committed text-B set
  re-scored through the analysis path reproduces its registered
  0.8961 exactly; sweeps at the GS-primary 20 m; first-N ladders with
  inherited K = 10 verification; board-chain paired tile-swap
  permutations (10,000, seed 42).
- Costs (audited flex rates, token-load audit § 3.4): MINIMAL ~$25
  all-in; HIGH ~$65 (the § 5a interim "~$37" under-estimate is
  corrected in the card — the pricing probe's 5 tiles
  under-represented corpus thinking volume). Billing console remains
  ground truth.

## Artefacts

- `analysis.json`, `sweep_20m.csv`, `verified_best_20m.geojson` —
  the MINIMAL cell; `high/` — the same for HIGH, plus
  `high/pair_verdicts.json`.
- Proposer/union/verifier data: `outputs/image-b-gs-2026-08-28/`.
- Card with registered predictions and outcomes:
  `planning/image-b-gs-2026-08-28.md`.

## Changelog

### 2026-08-28 — Original publication

Both cells complete (Session 143): MINIMAL ($25) and HIGH ($65) with
IP1–IP5 and HP1–HP5 assessed against their pre-launch registrations.
