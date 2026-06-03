<!-- GENERATED FILE — DO NOT EDIT. Rendered from results/analyses-manifest.json by scripts/generate_post_run_report.py v0.4.0. Edit the source-of-truth files and regenerate. -->

# Analyses manifest

> Generated 2026-06-03T02:25:49Z · 1 row(s) · schema v1.0.
>
> **Coverage**: 1 analysis(es) over conditions (sub-step 3c; hybrid human-authored).

| analysis_id | type | #conditions | preregistered | paper_section | outcome |
|---|---|---|---|---|---|
| n1-baseline-matrix-384 | leaderboard | 18 | exploratory | Results | At the preregistered 20 m buffer the best single pass for mound localisation is Gemini 3 Pro text at low temperature: baseline-pro-text-medium-t-0-0 (F1 0.763) and baseline-pro-text-high-t-0-7 (F1 0.745) form a two-member statistical tie (round-robin tile-swap permutation, BH-FDR q=0.05; pair BH-adjusted p=0.50) significantly clear of all 16 other single-pass configurations. The text-over-image advantage that recurs throughout the paper holds here at matched settings: the best text pass beats the best image pass (pro-image-medium-t-0-0, F1 0.606) by 0.157 F1 with model, thinking and temperature held constant (both Pro, MEDIUM thinking, T=0.0 -- modality is the only difference), a significant gap (BH-adjusted p=0.0000). The F1 leaders are not the tile-level discrimination (MCC) leader, however (pro-image-high-t-0-7, MCC +0.852, 7th on F1), so the best single-pass configuration is metric-dependent. |
