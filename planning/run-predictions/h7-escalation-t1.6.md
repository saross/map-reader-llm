# Pre-run prediction — H7 escalation, T=1.6

> **Committed before execution.** This document exists so the prediction
> carries a git timestamp that precedes the data. Do not edit the Prediction
> section after the run; record the result in `## Outcome` and, if the
> prediction was wrong, say so there.

## Registered basis

`docs/methodology/preregistration/osf/preregistration.md:731`:

> "**Temperature escalation trigger**: If T=1.3 yields higher F1 than T=1.0
> (point estimate, same M/E and H5 condition), exploratory testing at **T=1.6
> and T=2.0** will be conducted at the optimal configuration to characterise
> the upper bound of the temperature-performance curve."

Verified 2026-07-28: single unambiguous mention; the registered escalation
levels are **T=1.6 and T=2.0**, with a ceiling at T=2.0 (`:885`). The natural
continuation of the existing ladder (0.0, 0.3, 0.7, 1.0, 1.3) would be 1.7;
the registration says 1.6, and 1.6 is what will be run. No deviation is being
spent on a 0.1 difference.

**Registered status**: the trigger describes "exploratory testing". These
cells are **registered-exploratory**, not confirmatory. They characterise the
upper bound of the curve; they do not retest H7's primary prediction, which is
already falsified (the registration predicted T=1.0 optimal at `:711`; T=0.0
won).

## Why only T=1.6, not T=2.0

Sequential. If F1 at T=1.6 continues the decline established across
T=0.3 → T=1.3, the upper bound is characterised and T=2.0 adds nothing. T=2.0
will be run only if T=1.6 is **higher** than T=1.3, which would indicate a
non-monotone curve and leave the upper bound genuinely open.

## Evidence the trigger fired on noise

The trigger is written on a point estimate and fired as specified. But the
triggering difference does not survive replication. Paired tile-swap
permutations (10k, seed 42, 20 m buffer, 340-tile Era-1 corpus, curator GT;
`results/h7-escalation-check/`):

| run | ΔF1 (T=1.0 − T=1.3) | p | favours |
|---|---:|---:|---|
| run01 | −0.0362 | 0.247 | T=1.3 |
| run02 | +0.0022 | 0.910 | T=1.0 |
| run03 | +0.0020 | 0.926 | T=1.0 |

None significant, and **the sign is not consistent across replicates of the
same condition**. The aggregate that fired the trigger is carried entirely by
run01. The registered instrument (paired bootstrap, `osf:270`) agrees:
ΔF1 −0.0357, 95 % CI [−0.0908, +0.0137], p = 0.204.

The run therefore proceeds to discharge a registered obligation, not because
the evidence suggests an optimum above T=1.3 exists.

## Prediction

**Primary**: F1 at T=1.6 will be **lower than T=1.3** (text track, 340-tile
Era-1 corpus, F1@20 m), continuing the monotone decline observed from T=0.3
onward. Point prediction ~0.50–0.54, i.e. at or below T=1.3's 0.544, and
clearly below the T=0.3 optimum of 0.606.

**Secondary**: the T=1.6 vs T=1.3 difference will **not** be significant under
the registered paired bootstrap, on the pattern established across the upper
half of the curve where no adjacent pair separates.

**Tertiary**: precision will fall faster than recall, continuing the pattern
across T=0.7 → T=1.3 (precision 0.461 → 0.425; recall 0.798 → 0.756).

**What would falsify this**: F1 at T=1.6 exceeding T=1.3, which would indicate
a non-monotone temperature-performance curve and require running T=2.0 to
characterise the upper bound as registered.

**Consequence either way**: the escalation trigger is discharged. If the
prediction holds, the registered question — is there benefit above the vendor
default? — is answered in the negative with a directly measured upper bound
rather than an extrapolation.

## Run parameters (to be confirmed at the API gate)

| parameter | value | source |
|---|---|---|
| model | `gemini-3-flash` | matches the registered H7 runs (`detections_T1.3_run01.meta.json`) |
| config | `detect_brief-text` | text track, the track on which the trigger fired |
| corpus | 340 tiles, Era-1 512 px | `inputs/vectors/bounds/full_evaluation_bounds.geojson` |
| K | 3 runs | `study_manifest.json` `runs_per_condition: 3` |
| calls | 1,020 (3 × 340) | derived |
| buffer | 20 m | registered GS precision |

**Deviation to note in the erratum**: the registered H7 ran on the 60-tile
holdout; this runs on the 340-tile Era-1 corpus, per E36, which moved all
Phase 2–3 work to that corpus. Consistent with every other H7 cell it will be
compared against.

## Outcome

**Executed 2026-08-28 (Session 143), PI-approved ("yes, let's run it at
that cost"). BOTH registered levels run — T=1.6 AND T=2.0 — so the
obligation is discharged at the letter; the sequential shortcut above
was not exercised and no deviation entry is needed for it.** Six
single passes (3 per level), 2,040 calls, real-time flex, ~$1.37
total (the registered runs used the Batch API — both bill at 50 % of
list; execution-infrastructure note, not a parameter change).
Replication gate: the committed T1.0-vs-T1.3 check reproduced exactly
(ΔF1 −0.036229, p = 0.247, 340 tiles) before any new comparison was
trusted; frame = Era-1 340-tile 512 px bounds
(`inputs/vectors/bounds/full_evaluation_bounds.geojson`), curator GT,
20 m — the E36 corpus, as § Run parameters declared.

| level | run | F1 | P | R | ΔF1 vs T=1.3 (same replicate) | p |
|---|---|---:|---:|---:|---:|---:|
| T=1.6 | 1 | 0.4806 | 0.362 | 0.714 | −0.0658 | 0.0061 |
| T=1.6 | 2 | 0.4884 | 0.369 | 0.722 | −0.0480 | 0.0846 |
| T=1.6 | 3 | 0.4524 | 0.338 | 0.683 | −0.0974 | 0.0002 |
| T=2.0 | 1 | 0.4752 | 0.359 | 0.703 | −0.0712 | 0.0017 |
| T=2.0 | 2 | 0.4714 | 0.350 | 0.720 | −0.0649 | 0.0064 |
| T=2.0 | 3 | 0.4765 | 0.357 | 0.714 | −0.0733 | 0.0013 |

**Primary prediction CONFIRMED**: every T=1.6 replicate sits below its
T=1.3 counterpart, inside the predicted 0.50–0.54… in fact below it
(0.452–0.488) — the decline continued and steepened.
**Secondary prediction WRONG, informatively**: the T=1.6 differences
were predicted non-significant on the adjacent-pair pattern; five of
six escalation comparisons are significant (p = 0.0002–0.0085 band) —
the curve separates from T=1.3 at 1.6 in a way no earlier adjacent
pair did. **Tertiary CONFIRMED**: precision falls faster than recall
(P 0.429 → ~0.35, R 0.75 → ~0.71).
**The registered question is answered**: there is no benefit above the
vendor default; the temperature-performance curve declines monotonically
from the T=0.3 optimum (0.6065) through T=1.3 (0.544) to a degraded
plateau ≈ 0.47 at T=1.6–2.0 (T=2.0 ≈ T=1.6; no further collapse).
Artefacts: `outputs/h7-escalation-2026-08-28/`,
`results/h7-escalation-2026-08-28/`.
