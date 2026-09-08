# April image verifier stage — sweep of the COMPLETE 802 probabilities (2026-09-08, S151)

The April stage `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10`
carries a `sweep_2d.json` computed on 2026-04-17 (`b8961e56f`) when 342 of its
802 candidates had been verified; the remaining 460 were verified in the
2026-05-06 cleanup pass (`c6b5e6b10`, `cleanup_history` in `probabilities.json`)
and the sweep was never re-run. That April sweep is therefore a partial-verification
artefact (best F1 at 20 m 0.2739, recall 0.175), not a comparator for the refreshed
stage built on the recovered passes.

This directory holds the like-for-like comparator: the same sweep script
(`scripts/sweep_f1_greedy_pv.py`, buffers 20/30/40/50 m, `full_evaluation_bounds`)
run on the April stage's COMPLETE `probabilities.json` (802 of 802 with a
probability) and its committed `crops/candidate_manifest.json`. Run on sapphire,
2026-09-08, $0. The stage directory itself is untouched (preserve and compare —
`planning/verifier-stage-refresh-2026-09-08.md` § 5.2).

Comparison: `reports/recovery-consistency-audit-2026-09-08.md` § 6.1.
