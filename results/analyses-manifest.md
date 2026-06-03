<!-- GENERATED FILE — DO NOT EDIT. Rendered from results/analyses-manifest.json by scripts/generate_post_run_report.py v0.4.0. Edit the source-of-truth files and regenerate. -->

# Analyses manifest

> Generated 2026-06-03T08:27:45Z · 1 row(s) · schema v1.0.
>
> **Coverage**: 1 analysis(es) over conditions (sub-step 3c; hybrid human-authored).

| analysis_id | type | #conditions | preregistered | paper_section | outcome |
|---|---|---|---|---|---|
| n1-baseline-matrix-384 | leaderboard | 18 | exploratory | Results | At the preregistered 20 m buffer the best single pass for mound localisation is genuine Gemini 3 Pro text with HIGH thinking at T=0.0 (baseline-pro-text-high-t-0-0, run n1-pro-rerun-384; F1 0.804), the SOLE Tier-1 leader: the round-robin tile-swap permutation (BH-FDR q=0.05; 120/153 pairs significant -> 7 tiers) separates it from every other configuration. It is significantly clear of a Tier-2 trio of mutually-indistinguishable Pro-text passes -- pro-text-medium-t-0-7 (F1 0.764), pro-text-medium-t-0-0 (0.763), pro-text-high-t-0-7 (0.745). The top four cells are all Pro text and the top five all genuine Pro; the text-over-image advantage that recurs throughout the paper holds at matched settings (best Pro text 0.804 vs best Pro image 0.666). The F1 leader is NOT the tile-level discrimination (MCC) leader, however: genuine Pro IMAGE wins MCC -- pro-image-medium-t-0-7 (MCC +0.913, but only 10th on F1) and pro-image-high-t-0-0 (MCC +0.868) -- while Pro text leads F1, so the best single-pass configuration is metric-dependent. This board SUPERSEDES the pre-E57 version (whose Tier 1 was a two-member tie at 0.763/0.745): the four anti-diagonal 'Pro' cells there were Flash misdispatches (E57); re-dispatched as genuine Pro they score 0.59-0.80, and pro-text-high-t-0-0 takes the outright lead. |
