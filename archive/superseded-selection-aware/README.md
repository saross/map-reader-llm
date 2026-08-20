# Superseded selection-aware artefacts

Moved here 2026-08-20 (Session 138, audit remediation). These two m-out-of-n
sensitivity artefacts were produced by the pre-Hsu vintage of
`scripts/selection_aware_intervals.py` (2026-08-19, before the Hsu constrained
construction and the buffer-stamped filename convention were added). They were
re-emitted at the current code vintage as
`results/selection-aware/g512_ov064_K10_b20_m{0.5,0.25}.json` — all shared
stochastic values (optimism, two-sided band width, band membership) reproduce
identically; the re-emissions add the Hsu fields and the `_b20` buffer stamp.
