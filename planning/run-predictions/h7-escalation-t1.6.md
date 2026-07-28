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

*Not yet run. To be completed after execution — do not edit the Prediction
section above.*
