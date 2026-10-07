# Run B, the modality bridging pair: first findings

> **Last revised**: 2026-10-07 (original publication, first scoring; Session 163).
> See [§ Changelog](#changelog) for revision history.

**Status: FIRST SCORING, FOR THE PRINCIPAL INVESTIGATOR'S (PI'S) REVIEW.**
Point estimates and tile-swap p-values, every run behind the six-cell
anchor gate. Not yet computed: the D45/D46 replicate floors, the tile-level
interaction permutation for the gap change, and Matthews correlation
coefficient (MCC) gaps. Scored with the scorer on `main` at `aa1746fbd`; the
D50/D51 scorer change (pull request #26, not merged) may move cells slightly
when it is merged and the re-score is approved.

## 1. What ran

Run B re-ran the four proposer arms of the modality claim (R7.3-22/23) on one
day, 2026-10-07, on the Batch API, with their original configurations (PI
ruling D49), plus three arms the PI added that day (D52; Stage 1 card
`planning/modality-bridge-2026-10-07.md` § 4.8):

- **The fifth leg** (`g37-image-cache`): Gemini 3.7 image through the explicit
  context cache, the Gemini 3 image arm's request shape.
- **A temperature-matched Gemini 3 pair** (`g3-text-temp1`, `g3-image-temp1`):
  text and image at temperature (T) 1.0 and K = 5. Gemini 3.7 samples at its
  default, 1.0, whatever is sent (`planning/temperature-probe-2026-10-07.md`
  §§ 7, 8.5).

All 45 proposer passes landed at exact coverage (1,398 tiles each). Ten
verifier legs followed on the same UTC day (Stage 2 card
`planning/modality-bridge-2026-10-07-stage2.md`). Unions, verifier settings
and every check are recorded in the two cards and their commits.

## 2. Cells (F1 at 20 m, 487-tile frame)

| Cell | Bridge F1 (point) | Original F1 | Bridge − original | MCC |
|---|---:|---:|---:|---:|
| Gemini 3 text, K = 10, Gemini 3 verifier | 0.8916 (0.15, k10) | 0.8961 | −0.0045 | 0.7939 |
| Gemini 3 image, K = 10, Gemini 3 verifier | 0.8331 (0.15, k9); best 0.8393 | 0.8412 | −0.0081 | 0.7954 |
| 3.7 text, K = 5, Gemini 3 verifier | 0.9154 (0.10, k5) | 0.9139 | +0.0015 | 0.8069 |
| 3.7 text, K = 5, 3.7 verifier | 0.9265 (0.80, k5) | 0.9265 | 0.0000 | 0.8116 |
| 3.7 image, K = 5, Gemini 3 verifier | 0.9160 (0.10, k5) | 0.9254 | −0.0094 | 0.8184 |
| 3.7 image, K = 5, 3.7 verifier | 0.9288 (0.90, k5) | 0.9308 | −0.0020 | 0.8368 |
| 3.7 image **cached**, Gemini 3 verifier | 0.9318 (0.10, k5) | — | — | 0.8184 |
| 3.7 image **cached**, 3.7 verifier | 0.9352 (0.90, k5); best 0.9363 | — | — | 0.8223 |
| Gemini 3 text, **T 1.0**, K = 5 | best 0.8824 (0.15, k5) | — | — | — |
| Gemini 3 image, **T 1.0**, K = 5 | best 0.8242 (0.15, k5) | — | — | — |

Source: `*/analysis.json` (`operating_point`, `image_best`). "Bridge −
original" is date plus serving mode (batch against the originals' real-time
tiers), never date alone (Stage 1 card § 9 item 6).

## 3. Gaps, text − image (tile-swap permutation, 10,000, 487 tiles)

| Pair | Bridge gap (p) | Original gap (p) |
|---|---:|---:|
| Gemini 3, K = 10 | **+0.0523 (0.0029)** | +0.0549 (0.0010) |
| Gemini 3, K = 5 (inherited rung) | +0.0609 (0.0002) | — |
| Gemini 3, **T 1.0**, K = 5 | **+0.0582 (0.0002)** | — |
| 3.7, Gemini 3 verifier | −0.0006 (0.95) | −0.0115 (0.25) |
| 3.7, 3.7 verifier | −0.0023 (0.75) | −0.0043 (0.68) |
| 3.7 text − **cached** image, Gemini 3 verifier | −0.0164 (0.074) | — |
| 3.7 text − **cached** image, 3.7 verifier | −0.0098 (0.25) | — |

Gap change against Gemini 3 (descriptive; no interaction permutation yet):
−0.0529 (3.7, Gemini 3 verifier) and −0.0547 (all 3.7). Sources:
`gap_test.json` (best points, as the originals), `k5/gap_test.json`,
`additions/gap_test.json`.

## 4. What it says (to be read against the floors once computed)

1. **The modality result replicates on one day, on one serving mode.**
   Gemini 3 keeps a text advantage of about +0.05 F1 (p 0.003). Gemini 3.7
   shows none, under either verifier. Each bridge cell sits within 0.01 F1
   of its original.
2. **Temperature does not explain it.** At T 1.0, the temperature 3.7
   actually samples at, the Gemini 3 text advantage is +0.058 (p 0.0002), as
   large as at T 0.7.
3. **Nor does the request shape.** Sent through the explicit cache, as
   Gemini 3 image is, 3.7 image still shows no text advantage. If anything,
   image leads, by −0.016 (p 0.074) and −0.010 (p 0.25). The cached 3.7 image
   cells score a little above the inline ones (0.9318 against 0.9160;
   0.9352 against 0.9288).
4. With temperature, request structure, tier, K and day matched, the family
   difference (R7.3-22's "parity or inversion") is an inversion that remains
   once only the model and its thinking level differ.

## 5. Flags

- **The Gemini 3 image K = 10 union is 15.0 % smaller than the original**
  (3,456 against 4,065; the passes agree more; Stage 2 card § 8, F-cal). Its F1
  moved by −0.0081 only. Raised as a surprise; the chain that built it rebuilds
  the original unions byte for byte, so it is not a pipeline artefact.
- T 1.0 text passes lost more tiles to flex-retry failures (31 across five
  passes against 11 across ten at T 0.7), all recovered in round 1.
- The original Gemini 3 image leg's six recovery tiles went inline (Stage 2
  card § 8); negligible here.
- Batch metas do not book thinking tokens separately; the audited costs
  carry them.

## 6. Cost (audited, batch)

Stage 1: Gemini 3 text US$8.39, Gemini 3 image US$19.52, 3.7 text US$8.64,
3.7 image US$18.93, fifth leg US$12.33, T 1.0 text US$4.26, T 1.0 image
US$9.76 (US$81.83). Stage 2, ten legs: US$12.69. In all, US$94.52, plus the
cache storage (shortened by deleting each cache once its pass landed,
D52). The 3.7 cache reads are priced at the rate card's US$0.0375/M. At the
US$0.075/M the September invoices show, add about US$9.

## Changelog

### 2026-10-07 — Original publication (Session 163)

First scoring of Run B (`aeff1e207`, driver
`scripts/modality-bridge-2026-10-07-score.sh`), written overnight under the
PI's delegation, for review.
