<!-- GENERATED FILE — DO NOT EDIT. Rendered from results/analyses-manifest.json by scripts/generate_post_run_report.py v0.4.0. Edit the source-of-truth files and regenerate. -->

# Analyses manifest

> Generated 2026-06-04T04:41:31Z · 1 row(s) · schema v1.0.
>
> **Coverage**: 1 analysis(es) over conditions (sub-step 3c; hybrid human-authored).

| analysis_id | type | #conditions | preregistered | paper_section | outcome |
|---|---|---|---|---|---|
| n1-baseline-matrix-384 | leaderboard | 18 | exploratory | Results | At the preregistered 20 m buffer the best single pass for mound localisation is genuine Gemini 3 Pro text at T=0.0. Tier 1 -- the tie_set -- is a two-member statistical tie between pro-text-high-t-0-0 (F1 0.804) and pro-text-medium-t-0-0 (F1 0.792): a round-robin tile-swap permutation (BH-FDR q=0.05; 129/153 pairs significant -> 7 tiers) cannot separate them, and both are significantly clear of the Tier-2 pair -- the two Pro-text T=0.7 cells, pro-text-medium-t-0-7 (0.755) and pro-text-high-t-0-7 (0.745). So at T=0.0 the thinking level (HIGH vs MEDIUM) does not significantly matter, and T=0.0 beats T=0.7 (Tier 1 vs Tier 2) at matched model and modality (H7). The top four cells are all Pro text and the top six all genuine Pro; the text-over-image advantage holds at matched settings (best Pro text 0.804 vs best Pro image 0.666). The F1 leaders are NOT the tile-level discrimination (MCC) leader: genuine Pro IMAGE wins MCC -- pro-image-medium-t-0-7 (MCC +0.911, but 9th on F1) and pro-image-high-t-0-0 (+0.868) -- while Pro text leads F1, so the best single-pass configuration is metric-dependent. (All eight Pro cells are genuine Gemini 3 Pro at n>=3; see deviations E57 and docs/methodology/n1-baseline-matrix.md for board provenance.) |
