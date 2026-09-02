# The 3.7 image screen: the modality gap is eliminated

> **Last revised**: 2026-09-02 (original publication). See
> [§ Changelog](#changelog) for revision history.

**Classification**: registered-by-card GS screen
(`planning/gemini37-image-gs-2026-08-30.md`; expectations I1–I5
committed at PI go). Instruments: the image-B campaign machinery
(union → both verifier arms → sweep at 20 m vs the curated GS
reference), per-tile tile-swap micro-F1 permutation (10,000, seed
42) for every head-to-head. All gates green throughout (coverage
1,398/1,398 ×5 after recovery; verifier arms 674/674 with zero
failures each; every replication gate 1e-3 or better).

## Headlines

| Cell | Best @20 m | Point | P | R | MCC |
|---|---:|---|---:|---:|---:|
| 3.7-image + carried G3 verifier (arm 1) | **0.9254** | (0.10, k5) | 0.9233 | 0.9276 | 0.8192 |
| 3.7-image + 3.7 verifier (arm 2) | **0.9308** | (0.90, k5) | 0.9341 | 0.9276 | 0.8322 |
| 3.7-text screen best (committed) | 0.9139 | (0.10, k5) | — | — | — |
| all-3.7 text swap best (committed) | 0.9265 | (0.80, k5) | — | — | — |
| G3 image anchor (committed) | 0.8412 | (0.15, k9) | 0.8741 | 0.8107 | 0.7985 |

Union: 674 candidates, 66 % unanimous (vs the text screen's 791 at
59 % — the image proposer proposes fewer, more consensual
candidates; per-pass raw detections varied under 1 % across the five
passes).

## The gap test (I2) — the campaign's question, answered

Within-family (text − image) at 20 m, tile-swap paired
(`gap_test.json`):

| Family | text − image | p | Verdict |
|---|---:|---:|---|
| Gemini 3 (committed) | **+0.0549** | 0.001 | text significantly ahead |
| Gemini 3.7, carried-verifier pair | −0.0115 | 0.253 | statistically zero |
| Gemini 3.7, all-3.7 pair | −0.0043 | 0.677 | statistically zero |

**The modality gap is ELIMINATED at 3.7** (gap change −0.059 to
−0.066, roughly 2.5× the GS verified-set resolution). The nominal
sign flip is not significant — the honest claim is parity, not
inversion. I2 predicted "narrower by more than the resolution
(< ~0.031)"; the outcome overshoots the prediction to zero.

## Verdicts I1–I5

| # | Prediction | Verdict |
|---|---|---|
| I1 | 3.7-image above the G3 image anchor 0.8412 | **CONFIRMED at ~5× the text-side gain** — +0.0842 (arm 1) / +0.0896 (arm 2); the vision upgrade concentrated on the image track |
| I2 | Gap narrower than 0.0549 by > resolution | **CONFIRMED, overshot to parity** (above) |
| I3 | Lattices: carried arm prob 0.10–0.20; 3.7 arm ≥ 0.6 | **CONFIRMED exactly** — (0.10, k5) and (0.90, k5) |
| I4 | Thinking < 1,000, ≈ text's 276 | **CONFIRMED, lighter** — 88–157 t/call (clean passes ~155) |
| I5 | Caching ≥ 90 % of input | **INFORMATIVE FAILURE** — 79.5 % at scale (probe 16 % parallel-cold / 54 % sequential); cost still under projection ($22.50 token-basis all-in proposer vs $32–36 projected) |

## The escalation question (PI economics rule)

All-3.7 image 0.9308 vs the all-3.7 text swap 0.9265: **+0.0043, not
significant** (and under the MDE80 ≈ 0.024). There is **no
resolvable new F1 high**, so the pre-agreed trigger for considering
the expensive 55-map image extension is NOT met. (Arm 2's image MCC
0.8322 likewise does not approach the committed GS MCC crown.) The
finding stands on the GS instrument: parity, at image-track prices
that caching makes comparable to text.

## Operational notes (runner-fix queue; paper cost section)

Two flex-era lessons from execution: image mode at WORKERS=400 blew
the default fd ulimit (17 example images per call; passes died in
fd/SSL storms — fixed with ulimit 8192 + a 150-worker image cap,
`scripts/gemini37-image-gs-driver.sh`), and the daily ~13:00–19:00
UTC flex-storm window consumed two pass attempts before the
storm-resilient recovery driver swept all 4,288 residual tiles in
one 74-minute clear-window round. Total proposer spend including
every retry and recovery: $22.50 token-basis.

## Changelog

### 2026-09-02 — Original publication

Full screen executed and analysed (Session 145): five passes +
recovery to exact coverage, union 674, both verifier arms clean,
sweeps, the corrected within-family gap test (the campaign script's
built-in head-to-head pairs against the G3 anchor by design and was
not used for I2), verdicts I1–I5. Data commit `ada9822fe`.
