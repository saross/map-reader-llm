# Archive note: 55maps-generalisation verified-cleanup (2026-04-10)

Archive note: 26 of 8942 (gap=8916) April-10 partial-cleanup staging dir, never run through run_pv.py cleanup (no cleanup_history field). Superseded by outputs/55maps-generalisation/verified-v2/ which was cleaned 2026-05-06. Archived 2026-05-06 during Tier-2/3 closure audit (Session 87).

Correction (2026-10-05, Session 160 register repair, D38): this leg's 26
results WERE merged into the live leg: `outputs/55maps-generalisation/verified/probabilities.json`
records `cleanup_merges` from `outputs/55maps-generalisation/verified-cleanup/probabilities.json`
(merged 2026-04-10T03:32:55Z, added 26), and all 26 values are identical to
this directory's. Its spend (26 requests) is real spend of the `verified`
leg, carried in the passes register as
`55maps-generalisation::verified-cleanup-20260410::run1`.
