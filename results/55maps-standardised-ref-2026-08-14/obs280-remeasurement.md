# Obs 280 re-measurement — F1-vs-MCC divergence on the shared reference

> **Last revised**: 2026-08-14 (blind-verifier corrections applied —
> including a substantive mechanism correction). See
> [§ Changelog](#changelog) for revision history.

**What this is.** Queue item 4 of
`reports/verification/reference-standardisation-queue.md`. The Obs
280/292 finding — text configurations win F1 while the image
configuration wins tile MCC — was originally measured across metrics
that did **not** share a reference: corrected F1 against per-run
extended ground truth, MCC against the student layer alone
(`results/55maps-mcc-v2-summary/report.md` § 1). Ruling 20(a) flagged
that an unknown share of the divergence could be reference effect.
With items 2–3 complete, both metrics live on the ruling-21
standardised reference; this document re-measures the divergence
there.

**Method.** Deterministic lift from committed artefacts by
`scripts/analyse_obs280_shared_reference.py`; JSON artefact
`obs280-shared-reference.json` beside this file. No recompute, no
API, US$0. Cells follow the Obs 292 / mcc-v2 § 2 carried-config
comparison (T03-k4, TH7-k4, IM-k3, TM-k4 — one deployment operating
point per configuration, detection inputs identical to the mcc-v2 § 2
rows; Obs 292 itself compared three configs, mcc-v2 added text-MIN),
with the full 8-cell board as a secondary view.

## Verdict: the divergence survives — it is metric behaviour, not reference effect

On the standardised reference (both metrics, one reference):

| cell | F1 @ 50 m | MCC | F1 rank | MCC rank |
|------|-----------|-----|---------|----------|
| T03-k4 | 0.8303 | 0.6690 | 1 | 2 |
| TH7-k4 | 0.8169 | 0.6650 | 2 | 3 |
| IM-k3 | 0.8010 | 0.7120 | 3 | **1** |
| TM-k4 | 0.7833 | 0.6401 | 4 | 4 |

The F1 leader (T=0.3 text) is not the MCC leader (image); image sits
**third of four on F1 while leading MCC**, and both metrics agree
text-MIN is last (the four-way agreement is mcc-v2 § 4's finding;
Obs 292 compared three configs). This is the Obs 280/292 pattern
intact, measured for the first time with no reference asymmetry. The marginal 95 %
CIs of the two headline gaps do not overlap (F1: T03-k4
[0.8210, 0.8394] vs IM-k3 [0.7911, 0.8105]; MCC: IM-k3
[0.6987, 0.7248] vs T03-k4 [0.6550, 0.6822] —
`consolidated-standardised.csv`), which is conservative evidence of
significance in both directions; the formal paired re-tiering is
queue item 5.

## How much of the original divergence was reference effect?

The image-minus-(F1-leader) MCC gap, stepped across references
(`obs280-shared-reference.json → mcc_gap_image_minus_f1_leader`):

| Reference for MCC | Gap (IM-k3 − T03-k4) |
|-------------------|----------------------|
| Student layer alone (legacy; the Obs 292 convention) | +0.0386 |
| Legacy canonical-extended at 50 m (S105) | +0.0393 |
| Standardised (shared) | +0.0430 |

The reference axis moves the MCC gap by **+0.004 of ~0.043 (≈ 10 %)**
— and in the direction of *widening* image's lead. The
mixed-reference original therefore slightly **understated** the
divergence; ≈ 90 % of it is genuine metric behaviour. The mechanism
on this board (verifier-derived from the cell confusion matrices,
third-re-derived): F1 rewards the text configs' **precision** lead
(0.893 vs image's 0.829 at essentially equal detection recall,
0.776 vs 0.775); MCC rewards image's higher **tile sensitivity**
(0.705 vs 0.651) — image's 335 extra false-positive detections
concentrate in already-flagged tiles (tile FP 178 vs 176) while its
true positives reach 191 more distinct tiles (2,486 vs 2,295). This
is the mcc-v2 § 4 mechanism (precision-vs-sensitivity); Obs 280's
matrix-tree framing ("text high-recall, image selective/high-TN")
does **not** describe this board — image here has the lowest tile TN
and specificity of the four cells.

On the F1 side (`f1_gap_f1_leader_minus_image`): text's lead over
image is +0.0372 on the legacy extended reference (A1) and +0.0293 on
the standardised reference — narrowed by the reference move but still
≈ 3 F1 points. Note the once-reported near-parity (mcc-v2 §§ 3–4's
image 0.8333 vs T=0.3 0.8437, gap 0.010) came from the per-run
self-referential phantom sets that the S105 canonical GT replaced;
on any single shared reference since, the F1 gap is ~3–4 points.

## Secondary views

- **Full-board rank concordance** (8 cells, standardised reference):
  Spearman ρ = 0.476 (p = 0.233, n = 8) between F1 @ 50 m and MCC —
  weak, non-significant concordance. The two metrics genuinely order
  the board differently; neither is a proxy for the other.
- **Strongest form of the contrast**: against the best text cell
  overall (T03-k3, F1 0.8393), image trails by −0.0383 on F1 while
  leading by +0.0232 on MCC — the divergence is not an artefact of
  comparing image against a weak text operating point.
- **Rank stability**: the four-cell MCC order is identical on all
  three references (image > T0.3 > T0.7 > MIN), and the F1 order is
  identical on both extended references (T0.3 > T0.7 > image > MIN).
  Reference standardisation changed magnitudes, never orders.

## Status of Obs 280 / Obs 292

Both observations' headline claims are **confirmed and strengthened**
on the shared reference: the divergence survives with the reference
asymmetry removed, image's MCC lead is slightly larger than
originally reported, and the paper-structure implication (report F1
and MCC as parallel narratives) stands. One qualification: Obs 280's
mechanism WORDING (image as the "selective profile with high TN")
belongs to the 12-stratum matrix tree and does not transfer to this
board, where the operative contrast is text precision vs image tile
sensitivity (see § reference-effect above); cite the mechanism from
mcc-v2 § 4 rather than Obs 280 when writing about the 55-map cells. The Obs 292 sub-finding that
image overtakes text on F1 at R ≥ 75 m was a product of the per-run
reference vintage and does not carry to the shared reference: T03-k4
stays above IM-k3 at every buffer (0.8323 vs 0.8165 at 75 m; 0.8355
vs 0.8239 at 150 m — image narrows the gap from −0.029 to −0.012 but
never crosses; `consolidated-standardised.csv`). The crossover claim
should not be cited from Obs 292 without this caveat.

## Changelog

### 2026-08-14 (b) — Blind-verifier corrections applied

Fresh-context blind verifier (mandatory for this item):
89 claims identified / 83 re-derived / 80 confirmed / 3 corrections.
Every headline number, rank, CI, the vintage ladder, the Spearman,
and the crossover reversal re-derived independently (the committed
JSON reproduced bit-for-bit from a reimplementation). Corrections
applied:

1. **Substantive — the mechanism sentence was backwards for this
   board.** The draft asserted Obs 280's matrix-tree mechanism
   ("text high-recall; image selective/high-TN") "unchanged"; the
   cell confusion matrices show text wins F1 on PRECISION (0.893 vs
   0.829) at dead-heat recall (0.776 vs 0.775), and image wins MCC
   on tile SENSITIVITY (0.705 vs 0.651) while carrying the lowest
   TN/specificity of the four cells. Replaced with the mcc-v2 § 4
   mechanism; third-re-derived per the disagreement rule. A
   caution added to § Status against citing Obs 280's mechanism
   wording for the 55-map cells.
2. Provenance: the four-cell set is Obs 292 / mcc-v2 § 2's (Obs 292
   itself compared three configs; text-MIN entered via mcc-v2).
3. The near-parity citation pointer corrected to mcc-v2 §§ 3–4 with
   4-dp values (0.8333 vs 0.8437).

What did NOT change: every number, rank, gap, CI, and the verdict.

### 2026-08-14 — Original publication

Session 132, queue item 4, executed after items 2–3 under the
standing contract ($0), commit `bfaeb1c17`.
