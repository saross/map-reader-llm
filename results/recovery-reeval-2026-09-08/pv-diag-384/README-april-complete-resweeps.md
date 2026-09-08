# April pv-diag image verifier stages re-swept on their complete probabilities (S151, 2026-09-08)

The sweep-staleness survey (`reports/sweep-staleness-survey-2026-09-08.md`) found
five `pv-diag-384` image verifier stages whose committed `sweep_2d.json` predates
the 2026-05-06 Tier-2 cleanup pass (`c6b5e6b10`) that completed their
`probabilities.json`. On the PI's ruling ("yes, re-sweep", 2026-09-08) the four
not yet re-swept were re-run with the stages' own script and settings
(`scripts/sweep_f1_greedy_pv.py`, buffers 20/30/40/50 m,
`full_evaluation_bounds`, the in-stage `crops/candidate_manifest.json`) on
sapphire, $0. The committed sweeps are untouched (preserve, do not swap); these
directories hold the complete-set record. The fifth stage (image t0.0
`verified-v1-n10`, gap 460) is in `image-t0.0-verified-v1-n10-april-complete-resweep/`.

| stage (`outputs/h11/pv-diag-384/…`) | gap | committed sweep: best F1 at 20 m (operating point) | complete re-sweep | best at 50 m: committed → complete |
| --- | ---: | --- | --- | --- |
| `flash-high-image-n5/image-t0.3/verified-v1-n5` | 11 | 0.7460 (vote ≥ 4, p ≥ 0.15, n 372) | 0.7475 (same point, n 373) | 0.8598 → 0.8611 |
| `flash-high-image-n5/image-t0.7/verified-v1-n5` | 1 | 0.7868 (vote ≥ 3, p ≥ 0.15, n 414) | 0.7868 (identical) | 0.8810 → 0.8810 |
| `flash-high-image-n5/image-t1.0/verified-v1-n5` | 1 | 0.7337 (vote ≥ 3, p ≥ 0.15, n 410) | 0.7337 (identical) | 0.8615 → 0.8615 |
| `scale-4-optimal-487/verified-v1-n10` | 1 | 0.7683 (vote ≥ 5, p ≥ 0.15, n 411) | 0.7683 (identical) | 0.8582 → 0.8582 |

Reading: the four committed sweeps were materially sound — the cleanup's
candidates were single, low-vote crops that no operating point kept. The
staleness class matters only where the gap is large (the t0.0 stage, 342 of
802 swept). Comparison and disclosure:
`reports/recovery-consistency-audit-2026-09-08.md` § 6.1.
