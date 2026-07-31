# Phase 3a Verifier Completeness Audit (2026-05-03)

> **Superseded figures (2026-07-31)**: this document records the
> audited 2026-05-03 state and its body is preserved unedited (it is a
> historical record and a C6 attestation source). The May–July 2026
> recovery and completion campaigns closed the audited completeness
> gaps (35 gap figures below no longer reproduce; current gap 0), and
> several consensus pools were later rebuilt with recovered passes
> without re-running their verified-v1 diagnostic outputs, so five
> pv-diag-384 `flash-high-text-n5` cells that audited complete now
> show a pool↔verifier count difference on disk. Era-current values
> and per-row adjudications:
> `reports/verification/c4-triage/mismatch-triage-2026-07-31.json`
> (round-2/3 addendum) and the C4 ledger.

## Executive summary

- **Cells audited:** 210 verifier cells across `outputs/` and `results/leaderboard/`
  (8 unmatched, 202 with confident input/output pairing).
- **Cells with `gap > 0`:** 31 (one is a cleanup-pass artefact, leaving **30 genuine
  gap-positive cells**).
- **Cumulative dropped candidates:** 9,751 (or **835 excluding the
  `verified-cleanup` artefact, whose 8,916 figure is structural, not a
  silent-drop**).
- **Paper/leaderboard impact:** **19 of the 30 real cells feed the leaderboard
  or production analyses, with a cumulative paper-feeding gap of 773
  candidates.** Affected: session-78 matrix (7 cells, gap 1–41),
  `flash-high-image-n5` matrix (4 cells, gap 1–460), `scale-4-optimal-487`
  (gap 1), `e47-propose-brief` greedy production (5 cells, gap 9–57),
  `h8-v2/wbf/scale-4` (gap 15), and `55maps-generalisation/verified-v2`
  (gap 3, but the canonical `verified/` is gap=0). One additional cell
  (`h11/proposer-verifier-384/verified-adversarial-text-v1-prompt`, gap 1)
  was inspected but does not appear to be referenced from any current script
  or analysis output, so it is classified as non-paper.
- **Recommendation:** **Action needed.** Run targeted `run_pv.py cleanup` on the
  19 paper-feeding cells before the paper outline; the largest single offender
  (gap=460 in `flash-high-image-n5/image-t0.0/verified-v1-n10`) is the most
  likely to shift tier rankings. The 11 non-paper diagnostic cells in
  `pv-diag-384/verified/` (cumulative gap 62) are legacy exploratory runs that
  do not feed the leaderboard and may be deferred or skipped.

## Methodology

### What constitutes a "cell"

A cell is a directory containing a `probabilities.json` produced by the verifier
stage of the proposer-verifier pipeline (`run_pv.py`). The audit walked
`outputs/` and `results/leaderboard/` and treated every distinct `probabilities.json`
under those roots (excluding `archive/`, `.git/`, `.claude/`) as a candidate cell.
Note that `outputs/retest/phase3a/track1-image/` and `track2-text/` were
inspected but contain only proposer-stage artefacts (run-level detection
GeoJSONs and consensus geojsons) — there is **no `probabilities.json` under
`outputs/retest/phase3a/`**, so the phase3a tracks themselves are not directly
verifier-affected. The verifier stage cells that *populate* the phase3a
leaderboards live under `outputs/h11/` (notably `pv-diag-384/`).

### What was compared

For every cell:

```text
gap = expected_input − len(probabilities.results)
```

`expected_input` is the candidate count that the verifier was *meant* to
evaluate, drawn from the most specific candidate-source file available (in
priority order):

1. `candidate_manifest.json` co-located with `probabilities.json`
2. `crops/candidate_manifest.json` or `candidates/candidate_manifest.json`
   inside the cell directory
3. Sibling `crops/candidate_manifest.json` or `candidates/candidate_manifest.json`
4. Name-based parent-crops manifest (e.g.
   `verified/text-4of10/probabilities.json` ↔
   `crops/text-4of10/candidate_manifest.json`)
5. WBF candidate geojson (`wbf_candidates_vote2plus.geojson` or
   `wbf_candidates.geojson`)
6. Consensus_t1 geojson for `verified-v*-n*` sweep cells
7. Suffix-stripped fuzzy match for `<base>-<verifier>-verifier` naming
   (e.g. `pro-image-1of5-pro-verifier` ↔ `crops/pro-image-1of5`)
8. `shared-crops/` manifest in nested matrix runs

For consensus-mode probabilities (`iterations > 1`), the expected count is
`n_manifest × iterations` because keys are encoded as `candidate_NNNNN_iter<K>`.
All gap-positive cells in this audit have `iterations = 1`.

### Schema variants encountered

- `probabilities.json` always has top-level keys
  `{iterations, mode, results, total_results, verifier_config, version}`;
  some have `cleanup_history` after a `run_pv.py cleanup` pass.
- `results` is a `dict` keyed by `candidate_NNNNN` (with `_iter<K>` suffix in
  consensus mode). The values are
  `{mound_probability, reasoning, best_alternative, alternative_evidence}`.
- `total_results` is just `len(results)` (not a planned/expected count) — it
  cannot detect gaps on its own.
- `candidate_manifest.json` has a top-level `candidates` array; each entry has
  `{candidate_id, crop_file, source_tile, centroid_x, centroid_y, ...}`.
- WBF cells substitute `wbf_candidates*.geojson` for the manifest. The
  vote-2-plus filtered variant is preferred when present.
- `verifier-t-pilot/T*/` and several `pv-diag-384/verified/<x>-<y>-verifier/`
  cells lack any traceable input-set file (8 cells unmatched — see
  "Unmatched cells" below).

## Full results table

Sorted by `gap` descending. `n_consensus` is the expected input count
(`n_manifest × iterations`). Only cells with `gap != null` appear here; the 8
unmatched cells are listed separately below.

| cell_path | n_consensus | n_probabilities | gap | input_kind |
|---|---|---|---|---|
| `outputs/55maps-generalisation/verified-cleanup` | 8942 | 26 | 8916 | manifest-sibling-crops |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10` | 802 | 342 | 460 | manifest-in-crops-subdir |
| `outputs/h11/e47-propose-brief/verified/flash-high-text-1of5` | 4358 | 4301 | 57 | manifest-same-dir |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-adversarial-text` | 3736 | 3695 | 41 | shared-manifest |
| `outputs/h11/e47-propose-brief/verified/flash-high-text-2of5` | 1654 | 1626 | 28 | manifest-same-dir |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-brief-text` | 3736 | 3709 | 27 | shared-manifest |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-adversarial-text` | 2017 | 1991 | 26 | shared-manifest |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-checklist-text` | 3736 | 3715 | 21 | shared-manifest |
| `outputs/h11/pv-diag-384/verified/text-baseline-pro-verifier` | 1047 | 1026 | 21 | manifest-fuzzy-suffix-strip |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-checklist-text` | 2017 | 1998 | 19 | shared-manifest |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-brief-text` | 2017 | 1998 | 19 | shared-manifest |
| `outputs/h11/e47-propose-brief/verified/flash-high-text-3of5` | 1072 | 1053 | 19 | manifest-same-dir |
| `outputs/h8-v2/wbf/scale-4/verified` | 1114 | 1099 | 15 | manifest-sibling-crops |
| `outputs/h11/e47-propose-brief/verified/flash-high-text-4of5` | 753 | 739 | 14 | manifest-same-dir |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3/verified-v1-n5` | 2190 | 2179 | 11 | manifest-in-crops-subdir |
| `outputs/h11/pv-diag-384/verified/pro-medium-image-baseline-pro-verifier` | 519 | 509 | 10 | manifest-fuzzy-suffix-strip |
| `outputs/h11/e47-propose-brief/verified/flash-high-text-5of5` | 487 | 478 | 9 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-1of5` | 841 | 833 | 8 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/pro-high-image-1of5-pro-verifier` | 841 | 833 | 8 | manifest-fuzzy-suffix-strip |
| `outputs/55maps-generalisation/verified-v2` | 8942 | 8939 | 3 | manifest-sibling-crops |
| `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-5of5` | 297 | 294 | 3 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-3of5` | 471 | 468 | 3 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-2of5` | 583 | 580 | 3 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-4of5` | 391 | 388 | 3 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-medium-vf-1of5` | 3736 | 3735 | 1 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-1of5-flash-medium-verifier` | 3736 | 3735 | 1 | manifest-fuzzy-suffix-strip |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/verified-v1-n5` | 2017 | 2016 | 1 | manifest-in-crops-subdir |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-checklist` | 2017 | 2016 | 1 | shared-manifest |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0/verified-v1-n5` | 2840 | 2839 | 1 | manifest-in-crops-subdir |
| `outputs/h11/pv-diag-384/scale-4-optimal-487/verified-v1-n10` | 3601 | 3600 | 1 | manifest-in-crops-subdir |
| `outputs/h11/proposer-verifier-384/verified-adversarial-text-v1-prompt` | 572 | 571 | 1 | manifest-sibling-candidates |
| `outputs/55maps-text-high-t0.3-generalisation/verified` | 9910 | 9910 | 0 | manifest-sibling-crops |
| `outputs/h10/evaluation-v2/pool_020_hp4hn4/verified` | 1763 | 1763 | 0 | manifest-sibling-crops |
| `outputs/h10/evaluation-v2/pool_160_hp4hn4/verified` | 1454 | 1454 | 0 | manifest-sibling-crops |
| `outputs/55maps-image-generalisation/verified` | 7878 | 7878 | 0 | manifest-sibling-crops |
| `outputs/55maps-text-min-generalisation/verified` | 10170 | 10170 | 0 | manifest-sibling-crops |
| `outputs/h8-v2/wbf/scale-8/verified` | 1002 | 1002 | 0 | manifest-sibling-crops |
| `outputs/h8-v2/scale-4/verified` | 1551 | 1551 | 0 | manifest-sibling-crops |
| `outputs/55maps-text-high-generalisation/verified` | 9205 | 9205 | 0 | manifest-sibling-crops |
| `outputs/55maps-generalisation/verified` | 8942 | 8942 | 0 | manifest-sibling-crops |
| `outputs/h11/pv-diag-384/image-n5/image-t0.3/verified-v1-n10` | 1114 | 1114 | 0 | manifest-in-crops-subdir |
| `outputs/h11/pv-diag-384/image-n5/image-t0.3/verified-v1-n5` | 987 | 987 | 0 | manifest-in-crops-subdir |
| `outputs/h11/pv-diag-384/image-n5/image-t0.7/verified-v1-n10` | 1450 | 1450 | 0 | manifest-in-crops-subdir |
| `outputs/h11/pv-diag-384/image-n5/image-t0.7/verified-v1-n5` | 1123 | 1123 | 0 | manifest-in-crops-subdir |
| `outputs/h11/pv-diag-384/image-n5/image-t1.0/verified-v1-n10` | 1975 | 1975 | 0 | manifest-in-crops-subdir |
| `outputs/h11/pv-diag-384/image-n5/image-t1.0/verified-v1-n5` | 1443 | 1443 | 0 | manifest-in-crops-subdir |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/verified-v1-n10` | 5866 | 5866 | 0 | consensus-t1 |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/verified-v1-n5` | 3736 | 3736 | 0 | consensus-t1 |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-brief` | 3736 | 3736 | 0 | shared-manifest |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-checklist` | 3736 | 3736 | 0 | shared-manifest |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-comparative` | 3736 | 3736 | 0 | shared-manifest |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-adversarial` | 3736 | 3736 | 0 | shared-manifest |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.0/verified-v1-n3` | 1256 | 1256 | 0 | consensus-t1 |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.3/verified-v1-n10` | 4313 | 4313 | 0 | consensus-t1 |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.3/verified-v1-n5` | 2954 | 2954 | 0 | consensus-t1 |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t1.0/verified-v1-n10` | 5920 | 5920 | 0 | consensus-t1 |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t1.0/verified-v1-n5` | 3760 | 3760 | 0 | consensus-t1 |
| `outputs/h11/pv-diag-384/verified/flash-high-text-1of5-pro-verifier` | 3736 | 3736 | 0 | manifest-fuzzy-suffix-strip |
| `outputs/h11/pv-diag-384/verified/flash-high-text-6of30` | 1713 | 1713 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/text-4of10` | 1075 | 1075 | 0 | manifest-name-grandparent-crops |
| `outputs/h11/pv-diag-384/verified/image-5of5` | 427 | 427 | 0 | manifest-name-grandparent-crops |
| `outputs/h11/pv-diag-384/verified/flash-high-text-3of30` | 3072 | 3072 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-1of5` | 3736 | 3736 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-image-5of5` | 282 | 282 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-4of5` | 584 | 584 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/pro-high-text-flash-min-vf-1of5` | 504 | 504 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-2of30` | 4543 | 4543 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-23of30` | 491 | 491 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-19of30` | 607 | 607 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-11of30` | 1070 | 1070 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-7of10` | 590 | 590 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-5of10` | 879 | 879 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-17of30` | 682 | 682 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/pro-high-text-pro-vf-4of5` | 337 | 337 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-30of30` | 256 | 256 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-27of30` | 390 | 390 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-pro-vf-2of5` | 1376 | 1376 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-16of30` | 729 | 729 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-2of10` | 2215 | 2215 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-5of30` | 1991 | 1991 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/pro-high-text-flash-min-vf-4of5` | 337 | 337 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/image-10of10` | 361 | 361 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/pro-high-text-1of5` | 504 | 504 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/text-9of10` | 708 | 708 | 0 | manifest-name-grandparent-crops |
| `outputs/h11/pv-diag-384/verified/text-5of5` | 295 | 295 | 0 | manifest-name-grandparent-crops |
| `outputs/h11/pv-diag-384/verified/flash-high-image-3of5` | 506 | 506 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-15of30` | 789 | 789 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/text-4of5` | 395 | 395 | 0 | manifest-name-grandparent-crops |
| `outputs/h11/pv-diag-384/verified/flash-high-image-1of5` | 2017 | 2017 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/text-2of10` | 1350 | 1350 | 0 | manifest-name-grandparent-crops |
| `outputs/h11/pv-diag-384/verified/flash-high-text-high-vf-5of5` | 415 | 415 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/text-7of10` | 851 | 851 | 0 | manifest-name-grandparent-crops |
| `outputs/h11/pv-diag-384/verified/image-baseline` | 746 | 746 | 0 | manifest-name-grandparent-crops |
| `outputs/h11/pv-diag-384/verified/text-8of10` | 771 | 771 | 0 | manifest-name-grandparent-crops |
| `outputs/h11/pv-diag-384/verified/flash-high-text-pro-vf-3of5` | 855 | 855 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-21of30` | 536 | 536 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-12of30` | 975 | 975 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/pro-medium-text-baseline-pro-verifier` | 430 | 430 | 0 | manifest-fuzzy-suffix-strip |
| `outputs/h11/pv-diag-384/verified/image-9of10` | 442 | 442 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/pro-high-text-pro-vf-5of5` | 306 | 306 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-image-2of5` | 741 | 741 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/pro-high-text-1of5-pro-verifier` | 504 | 504 | 0 | manifest-fuzzy-suffix-strip |
| `outputs/h11/pv-diag-384/verified/image-4of5` | 523 | 523 | 0 | manifest-name-grandparent-crops |
| `outputs/h11/pv-diag-384/verified/flash-minimal-text-t07-4of5` | 807 | 807 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-1of5-flash-high-verifier` | 3736 | 3736 | 0 | manifest-fuzzy-suffix-strip |
| `outputs/h11/pv-diag-384/verified/pro-high-text-flash-min-vf-3of5` | 367 | 367 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-1of10` | 5866 | 5866 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-high-vf-2of5` | 1376 | 1376 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-2of5` | 1376 | 1376 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/image-baseline-pro-verifier` | 746 | 746 | 0 | manifest-fuzzy-suffix-strip |
| `outputs/h11/pv-diag-384/verified/flash-high-text-9of30` | 1271 | 1271 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-medium-vf-3of5` | 855 | 855 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-4of30` | 2363 | 2363 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-5of5` | 415 | 415 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-13of30` | 907 | 907 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/text-5of10` | 999 | 999 | 0 | manifest-name-grandparent-crops |
| `outputs/h11/pv-diag-384/verified/pro-high-text-pro-vf-3of5` | 367 | 367 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/image-3of5` | 617 | 617 | 0 | manifest-name-grandparent-crops |
| `outputs/h11/pv-diag-384/verified/flash-high-text-25of30` | 441 | 441 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/text-baseline` | 1047 | 1047 | 0 | manifest-name-grandparent-crops |
| `outputs/h11/pv-diag-384/verified/flash-high-text-9of10` | 431 | 431 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-8of10` | 511 | 511 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-26of30` | 415 | 415 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/image-2of5` | 754 | 754 | 0 | manifest-name-grandparent-crops |
| `outputs/h11/pv-diag-384/verified/text-3of10` | 1177 | 1177 | 0 | manifest-name-grandparent-crops |
| `outputs/h11/pv-diag-384/verified/pro-high-text-flash-min-vf-5of5` | 306 | 306 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-high-vf-4of5` | 584 | 584 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-4of10` | 1104 | 1104 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/image-5of10` | 627 | 627 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/pro-high-text-pro-vf-1of5` | 504 | 504 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/text-2of5` | 616 | 616 | 0 | manifest-name-grandparent-crops |
| `outputs/h11/pv-diag-384/verified/flash-high-text-pro-vf-1of5` | 3736 | 3736 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-minimal-text-t07-1of5` | 1593 | 1593 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-medium-vf-4of5` | 584 | 584 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/text-1of10` | 1939 | 1939 | 0 | manifest-name-grandparent-crops |
| `outputs/h11/pv-diag-384/verified/flash-high-text-6of10` | 727 | 727 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-10of30` | 1161 | 1161 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/pro-high-text-5of5` | 306 | 306 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/text-6of10` | 929 | 929 | 0 | manifest-name-grandparent-crops |
| `outputs/h11/pv-diag-384/verified/flash-high-text-10of10` | 345 | 345 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/pro-high-text-3of5` | 367 | 367 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/image-4of10` | 698 | 698 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-7of30` | 1536 | 1536 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/image-1of5` | 1123 | 1123 | 0 | manifest-name-grandparent-crops |
| `outputs/h11/pv-diag-384/verified/image-2of10` | 954 | 954 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/text-10of10` | 616 | 616 | 0 | manifest-name-grandparent-crops |
| `outputs/h11/pv-diag-384/verified/flash-high-text-high-vf-3of5` | 855 | 855 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/pro-high-text-1of5-flash-minimal-verifier` | 504 | 504 | 0 | manifest-fuzzy-suffix-strip |
| `outputs/h11/pv-diag-384/verified/pro-high-text-4of5` | 337 | 337 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/image-7of10` | 536 | 536 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-14of30` | 850 | 850 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-29of30` | 327 | 327 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-medium-vf-5of5` | 415 | 415 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/text-3of5` | 484 | 484 | 0 | manifest-name-grandparent-crops |
| `outputs/h11/pv-diag-384/verified/pro-high-text-flash-min-vf-2of5` | 409 | 409 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-18of30` | 637 | 637 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/text-1of5` | 974 | 974 | 0 | manifest-name-grandparent-crops |
| `outputs/h11/pv-diag-384/verified/flash-high-text-24of30` | 469 | 469 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-1of30` | 11771 | 11771 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/image-1of10` | 1444 | 1444 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-pro-vf-4of5` | 584 | 584 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-20of30` | 571 | 571 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-28of30` | 361 | 361 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/image-6of10` | 577 | 577 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-high-vf-1of5` | 3736 | 3736 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-3of5` | 855 | 855 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/pro-high-text-pro-vf-2of5` | 409 | 409 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-3of10` | 1493 | 1493 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/pro-high-text-2of5` | 409 | 409 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-8of30` | 1387 | 1387 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-minimal-text-t07-3of5` | 950 | 950 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-minimal-text-t07-2of5` | 1104 | 1104 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-image-4of5` | 388 | 388 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/image-3of10` | 777 | 777 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-22of30` | 510 | 510 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-medium-vf-2of5` | 1376 | 1376 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-high-text-pro-vf-5of5` | 415 | 415 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/image-8of10` | 493 | 493 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/verified/flash-minimal-text-t07-5of5` | 653 | 653 | 0 | manifest-same-dir |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3/verified-v1-n10` | 3412 | 3412 | 0 | manifest-in-crops-subdir |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/verified-v1-n10` | 3211 | 3211 | 0 | manifest-in-crops-subdir |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-brief` | 2017 | 2017 | 0 | shared-manifest |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-comparative` | 2017 | 2017 | 0 | shared-manifest |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-adversarial` | 2017 | 2017 | 0 | shared-manifest |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0/verified-v1-n10` | 4638 | 4638 | 0 | manifest-in-crops-subdir |
| `outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.7/verified-v1-n10` | 1953 | 1953 | 0 | consensus-t1 |
| `outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.7/verified-v1-n5` | 1593 | 1593 | 0 | consensus-t1 |
| `outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.0/verified-v1-n3` | 1087 | 1087 | 0 | consensus-t1 |
| `outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.3/verified-v1-n10` | 1575 | 1575 | 0 | consensus-t1 |
| `outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.3/verified-v1-n5` | 1388 | 1388 | 0 | consensus-t1 |
| `outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t1.0/verified-v1-n10` | 2472 | 2472 | 0 | consensus-t1 |
| `outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t1.0/verified-v1-n5` | 1926 | 1926 | 0 | consensus-t1 |
| `outputs/h11/pv-diag-384/scale-4-optimal-487/verified-v1-n5` | 2198 | 2198 | 0 | manifest-in-crops-subdir |
| `outputs/h11/propose-brief-v1-test/verified-adversarial-text-v1` | 745 | 745 | 0 | manifest-sibling-candidates |
| `outputs/h11/e47-propose-brief/verified/text-baseline` | 1180 | 1180 | 0 | manifest-name-grandparent-crops |
| `outputs/h11/gold-standard-v2/verified-v1` | 608 | 608 | 0 | manifest-sibling-crops |
| `outputs/h11/wbf/fh-text-n30/verified` | 5862 | 5862 | 0 | manifest-sibling-crops |
| `outputs/h11/wbf/gold-standard-v2-detect/verified-v1` | 1318 | 1318 | 0 | wbf-candidates |
| `outputs/h11/wbf/e47-propose-brief-n5/verified-v2` | 3890 | 3890 | 0 | wbf-candidates |
| `outputs/h11/wbf/e47-propose-brief-n5/verified-v1` | 3890 | 3890 | 0 | wbf-candidates |
| `outputs/h11/wbf/fh-text-n5/verified` | 2724 | 2724 | 0 | manifest-sibling-crops |
| `outputs/h11/n1-outstanding-384/image-t0/verified-v1-n3` | 690 | 690 | 0 | manifest-in-crops-subdir |

### Unmatched cells (no traceable input-set file)

These 8 cells have no co-located, sibling, or fuzzy-name-matched candidate
manifest. They appear to be legacy exploratory verifier-variant runs (mostly
under `pv-diag-384/verified/` with `<base>-<verifier_variant>-verifier`
naming) and a 2026-Q1 verifier-temperature pilot. None feed the
leaderboard or any paper analysis to my knowledge. They are listed for
completeness only.

| cell_path | n_probabilities | input lookup |
|---|---|---|
| `outputs/verifier-t-pilot/T0.5/probabilities.json` | 607 | (no manifest located) |
| `outputs/verifier-t-pilot/T1.0/probabilities.json` | 607 | (no manifest located) |
| `outputs/h11/pv-diag-384/verified/pro-image-minimal-verifier/probabilities.json` | 519 | (no manifest located) |
| `outputs/h11/pv-diag-384/verified/pro-text-medium-verifier/probabilities.json` | 430 | (no manifest located) |
| `outputs/h11/pv-diag-384/verified/flash-minimal-image-medium-verifier/probabilities.json` | 746 | (no manifest located) |
| `outputs/h11/pv-diag-384/verified/pro-text-minimal-verifier/probabilities.json` | 430 | (no manifest located) |
| `outputs/h11/pv-diag-384/verified/flash-minimal-text-medium-verifier/probabilities.json` | 1047 | (no manifest located) |
| `outputs/h11/pv-diag-384/verified/pro-image-medium-verifier/probabilities.json` | 519 | (no manifest located) |

## Gap-positive cells, expanded

For each cell with `gap > 0`, the absolute paths of the probabilities and input
manifest, and a sample of candidate IDs that appear in the input set but not in
`probabilities.results` (so a future `run_pv.py cleanup` can target them).

> **Note on the `verified-cleanup` artefact (gap 8916):** This is *not* a silent
> drop in the same sense as the others. `outputs/55maps-generalisation/verified-cleanup/`
> is the **output directory of an earlier cleanup pass that re-verified only
> the 26 missing candidates**, so by construction it contains 26 results
> against the 8,942-candidate manifest. The canonical cell
> (`outputs/55maps-generalisation/verified/probabilities.json`) is gap=0; the
> partial cleanup output should be archived rather than re-run. It is included
> in the table for full transparency, but excluded from the "835 cumulative
> dropped candidates" headline figure.

### `outputs/55maps-generalisation/verified-cleanup/probabilities.json` — gap 8916

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/55maps-generalisation/verified-cleanup/probabilities.json` (26 entries)
- **Input set (manifest-sibling-crops)**: `/home/shawn/Code/map-reader-llm/outputs/55maps-generalisation/crops/candidate_manifest.json` (8942 expected)
- **Sample missing candidate IDs** (first 10 of 8916): `candidate_00000`, `candidate_00001`, `candidate_00002`, `candidate_00003`, `candidate_00004`, `candidate_00005`, `candidate_00006`, `candidate_00007`, `candidate_00008`, `candidate_00009`

### `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10/probabilities.json` — gap 460

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10/probabilities.json` (342 entries)
- **Input set (manifest-in-crops-subdir)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10/crops/candidate_manifest.json` (802 expected)

### `outputs/h11/e47-propose-brief/verified/flash-high-text-1of5/probabilities.json` — gap 57

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/e47-propose-brief/verified/flash-high-text-1of5/probabilities.json` (4301 entries)
- **Input set (manifest-same-dir)**: `/home/shawn/Code/map-reader-llm/outputs/h11/e47-propose-brief/verified/flash-high-text-1of5/candidate_manifest.json` (4358 expected)
- **Sample missing candidate IDs** (first 10 of 57): `candidate_00109`, `candidate_00112`, `candidate_00200`, `candidate_00304`, `candidate_00307`, `candidate_00334`, `candidate_00361`, `candidate_00363`, `candidate_00380`, `candidate_00398`

### `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-adversarial-text/probabilities.json` — gap 41

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-adversarial-text/probabilities.json` (3695 entries)
- **Input set (shared-manifest)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/shared-crops/candidate_manifest.json` (3736 expected)
- **Sample missing candidate IDs** (first 10 of 41): `candidate_00012`, `candidate_00069`, `candidate_00111`, `candidate_00116`, `candidate_00313`, `candidate_00325`, `candidate_00436`, `candidate_00686`, `candidate_00828`, `candidate_00845`

### `outputs/h11/e47-propose-brief/verified/flash-high-text-2of5/probabilities.json` — gap 28

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/e47-propose-brief/verified/flash-high-text-2of5/probabilities.json` (1626 entries)
- **Input set (manifest-same-dir)**: `/home/shawn/Code/map-reader-llm/outputs/h11/e47-propose-brief/verified/flash-high-text-2of5/candidate_manifest.json` (1654 expected)
- **Sample missing candidate IDs** (first 10 of 28): `candidate_00109`, `candidate_00200`, `candidate_00304`, `candidate_00307`, `candidate_00334`, `candidate_00363`, `candidate_00380`, `candidate_00398`, `candidate_00433`, `candidate_00464`

### `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-brief-text/probabilities.json` — gap 27

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-brief-text/probabilities.json` (3709 entries)
- **Input set (shared-manifest)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/shared-crops/candidate_manifest.json` (3736 expected)
- **Sample missing candidate IDs** (first 10 of 27): `candidate_00023`, `candidate_00031`, `candidate_00064`, `candidate_00102`, `candidate_00546`, `candidate_00553`, `candidate_00572`, `candidate_00593`, `candidate_00630`, `candidate_00649`

### `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-adversarial-text/probabilities.json` — gap 26

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-adversarial-text/probabilities.json` (1991 entries)
- **Input set (shared-manifest)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/shared-crops/candidate_manifest.json` (2017 expected)
- **Sample missing candidate IDs** (first 10 of 26): `candidate_00313`, `candidate_00331`, `candidate_00352`, `candidate_00461`, `candidate_00465`, `candidate_00467`, `candidate_00510`, `candidate_00512`, `candidate_00513`, `candidate_00523`

### `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-checklist-text/probabilities.json` — gap 21

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-checklist-text/probabilities.json` (3715 entries)
- **Input set (shared-manifest)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/shared-crops/candidate_manifest.json` (3736 expected)
- **Sample missing candidate IDs** (first 10 of 21): `candidate_00013`, `candidate_00022`, `candidate_00486`, `candidate_00578`, `candidate_00843`, `candidate_00917`, `candidate_00949`, `candidate_01058`, `candidate_01373`, `candidate_01510`

### `outputs/h11/pv-diag-384/verified/text-baseline-pro-verifier/probabilities.json` — gap 21

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/verified/text-baseline-pro-verifier/probabilities.json` (1026 entries)
- **Input set (manifest-fuzzy-suffix-strip)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/crops/text-baseline/candidate_manifest.json` (1047 expected)
- **Sample missing candidate IDs** (first 10 of 21): `candidate_00056`, `candidate_00069`, `candidate_00134`, `candidate_00158`, `candidate_00168`, `candidate_00172`, `candidate_00228`, `candidate_00258`, `candidate_00427`, `candidate_00483`

### `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-checklist-text/probabilities.json` — gap 19

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-checklist-text/probabilities.json` (1998 entries)
- **Input set (shared-manifest)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/shared-crops/candidate_manifest.json` (2017 expected)
- **Sample missing candidate IDs** (first 10 of 19): `candidate_00297`, `candidate_00310`, `candidate_00324`, `candidate_00335`, `candidate_00386`, `candidate_00445`, `candidate_00623`, `candidate_00646`, `candidate_00666`, `candidate_00831`

### `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-brief-text/probabilities.json` — gap 19

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-brief-text/probabilities.json` (1998 entries)
- **Input set (shared-manifest)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/shared-crops/candidate_manifest.json` (2017 expected)
- **Sample missing candidate IDs** (first 10 of 19): `candidate_00201`, `candidate_00295`, `candidate_00319`, `candidate_00343`, `candidate_00374`, `candidate_00436`, `candidate_00515`, `candidate_00606`, `candidate_00617`, `candidate_00826`

### `outputs/h11/e47-propose-brief/verified/flash-high-text-3of5/probabilities.json` — gap 19

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/e47-propose-brief/verified/flash-high-text-3of5/probabilities.json` (1053 entries)
- **Input set (manifest-same-dir)**: `/home/shawn/Code/map-reader-llm/outputs/h11/e47-propose-brief/verified/flash-high-text-3of5/candidate_manifest.json` (1072 expected)
- **Sample missing candidate IDs** (first 10 of 19): `candidate_00109`, `candidate_00200`, `candidate_00304`, `candidate_00334`, `candidate_00363`, `candidate_00398`, `candidate_00433`, `candidate_00464`, `candidate_00483`, `candidate_00793`

### `outputs/h8-v2/wbf/scale-4/verified/probabilities.json` — gap 15

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h8-v2/wbf/scale-4/verified/probabilities.json` (1099 entries)
- **Input set (manifest-sibling-crops)**: `/home/shawn/Code/map-reader-llm/outputs/h8-v2/wbf/scale-4/crops/candidate_manifest.json` (1114 expected)
- **Sample missing candidate IDs** (first 10 of 15): `candidate_00031`, `candidate_00036`, `candidate_00060`, `candidate_00123`, `candidate_00133`, `candidate_00139`, `candidate_00146`, `candidate_00150`, `candidate_00158`, `candidate_00165`

### `outputs/h11/e47-propose-brief/verified/flash-high-text-4of5/probabilities.json` — gap 14

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/e47-propose-brief/verified/flash-high-text-4of5/probabilities.json` (739 entries)
- **Input set (manifest-same-dir)**: `/home/shawn/Code/map-reader-llm/outputs/h11/e47-propose-brief/verified/flash-high-text-4of5/candidate_manifest.json` (753 expected)
- **Sample missing candidate IDs** (first 10 of 14): `candidate_00109`, `candidate_00200`, `candidate_00304`, `candidate_00334`, `candidate_00363`, `candidate_00398`, `candidate_00433`, `candidate_00464`, `candidate_00483`, `candidate_00793`

### `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3/verified-v1-n5/probabilities.json` — gap 11

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3/verified-v1-n5/probabilities.json` (2179 entries)
- **Input set (manifest-in-crops-subdir)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3/verified-v1-n5/crops/candidate_manifest.json` (2190 expected)

### `outputs/h11/pv-diag-384/verified/pro-medium-image-baseline-pro-verifier/probabilities.json` — gap 10

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/verified/pro-medium-image-baseline-pro-verifier/probabilities.json` (509 entries)
- **Input set (manifest-fuzzy-suffix-strip)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/crops/pro-medium-image-baseline/candidate_manifest.json` (519 expected)
- **Sample missing candidate IDs** (first 10 of 10): `candidate_00134`, `candidate_00147`, `candidate_00178`, `candidate_00203`, `candidate_00224`, `candidate_00237`, `candidate_00271`, `candidate_00294`, `candidate_00452`, `candidate_00459`

### `outputs/h11/e47-propose-brief/verified/flash-high-text-5of5/probabilities.json` — gap 9

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/e47-propose-brief/verified/flash-high-text-5of5/probabilities.json` (478 entries)
- **Input set (manifest-same-dir)**: `/home/shawn/Code/map-reader-llm/outputs/h11/e47-propose-brief/verified/flash-high-text-5of5/candidate_manifest.json` (487 expected)
- **Sample missing candidate IDs** (first 9 of 9): `candidate_00109`, `candidate_00200`, `candidate_00304`, `candidate_00334`, `candidate_00398`, `candidate_00433`, `candidate_00483`, `candidate_01406`, `candidate_01522`

### `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-1of5/probabilities.json` — gap 8

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-1of5/probabilities.json` (833 entries)
- **Input set (manifest-same-dir)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-1of5/candidate_manifest.json` (841 expected)
- **Sample missing candidate IDs** (first 8 of 8): `candidate_00310`, `candidate_00480`, `candidate_00490`, `candidate_00590`, `candidate_00606`, `candidate_00690`, `candidate_00771`, `candidate_00839`

### `outputs/h11/pv-diag-384/verified/pro-high-image-1of5-pro-verifier/probabilities.json` — gap 8

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/verified/pro-high-image-1of5-pro-verifier/probabilities.json` (833 entries)
- **Input set (manifest-fuzzy-suffix-strip)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/crops/pro-high-image-1of5/candidate_manifest.json` (841 expected)
- **Sample missing candidate IDs** (first 8 of 8): `candidate_00310`, `candidate_00480`, `candidate_00490`, `candidate_00590`, `candidate_00606`, `candidate_00690`, `candidate_00771`, `candidate_00839`

### `outputs/55maps-generalisation/verified-v2/probabilities.json` — gap 3

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/55maps-generalisation/verified-v2/probabilities.json` (8939 entries)
- **Input set (manifest-sibling-crops)**: `/home/shawn/Code/map-reader-llm/outputs/55maps-generalisation/crops/candidate_manifest.json` (8942 expected)
- **Sample missing candidate IDs** (first 3 of 3): `candidate_02113`, `candidate_04047`, `candidate_04437`

### `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-5of5/probabilities.json` — gap 3

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-5of5/probabilities.json` (294 entries)
- **Input set (manifest-same-dir)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-5of5/candidate_manifest.json` (297 expected)
- **Sample missing candidate IDs** (first 3 of 3): `candidate_00310`, `candidate_00480`, `candidate_00490`

### `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-3of5/probabilities.json` — gap 3

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-3of5/probabilities.json` (468 entries)
- **Input set (manifest-same-dir)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-3of5/candidate_manifest.json` (471 expected)
- **Sample missing candidate IDs** (first 3 of 3): `candidate_00310`, `candidate_00480`, `candidate_00490`

### `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-2of5/probabilities.json` — gap 3

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-2of5/probabilities.json` (580 entries)
- **Input set (manifest-same-dir)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-2of5/candidate_manifest.json` (583 expected)
- **Sample missing candidate IDs** (first 3 of 3): `candidate_00310`, `candidate_00480`, `candidate_00490`

### `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-4of5/probabilities.json` — gap 3

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-4of5/probabilities.json` (388 entries)
- **Input set (manifest-same-dir)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-4of5/candidate_manifest.json` (391 expected)
- **Sample missing candidate IDs** (first 3 of 3): `candidate_00310`, `candidate_00480`, `candidate_00490`

### `outputs/h11/pv-diag-384/verified/flash-high-text-medium-vf-1of5/probabilities.json` — gap 1

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/verified/flash-high-text-medium-vf-1of5/probabilities.json` (3735 entries)
- **Input set (manifest-same-dir)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/verified/flash-high-text-medium-vf-1of5/candidate_manifest.json` (3736 expected)
- **Sample missing candidate IDs** (first 1 of 1): `candidate_03486`

### `outputs/h11/pv-diag-384/verified/flash-high-text-1of5-flash-medium-verifier/probabilities.json` — gap 1

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/verified/flash-high-text-1of5-flash-medium-verifier/probabilities.json` (3735 entries)
- **Input set (manifest-fuzzy-suffix-strip)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/crops/flash-high-text-1of5/candidate_manifest.json` (3736 expected)
- **Sample missing candidate IDs** (first 1 of 1): `candidate_03486`

### `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/verified-v1-n5/probabilities.json` — gap 1

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/verified-v1-n5/probabilities.json` (2016 entries)
- **Input set (manifest-in-crops-subdir)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/verified-v1-n5/crops/candidate_manifest.json` (2017 expected)

### `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-checklist/probabilities.json` — gap 1

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-checklist/probabilities.json` (2016 entries)
- **Input set (shared-manifest)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/shared-crops/candidate_manifest.json` (2017 expected)
- **Sample missing candidate IDs** (first 1 of 1): `candidate_01563`

### `outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0/verified-v1-n5/probabilities.json` — gap 1

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0/verified-v1-n5/probabilities.json` (2839 entries)
- **Input set (manifest-in-crops-subdir)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0/verified-v1-n5/crops/candidate_manifest.json` (2840 expected)

### `outputs/h11/pv-diag-384/scale-4-optimal-487/verified-v1-n10/probabilities.json` — gap 1

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/scale-4-optimal-487/verified-v1-n10/probabilities.json` (3600 entries)
- **Input set (manifest-in-crops-subdir)**: `/home/shawn/Code/map-reader-llm/outputs/h11/pv-diag-384/scale-4-optimal-487/verified-v1-n10/crops/candidate_manifest.json` (3601 expected)

### `outputs/h11/proposer-verifier-384/verified-adversarial-text-v1-prompt/probabilities.json` — gap 1

- **Probabilities (output)**: `/home/shawn/Code/map-reader-llm/outputs/h11/proposer-verifier-384/verified-adversarial-text-v1-prompt/probabilities.json` (571 entries)
- **Input set (manifest-sibling-candidates)**: `/home/shawn/Code/map-reader-llm/outputs/h11/proposer-verifier-384/candidates/candidate_manifest.json` (572 expected)
- **Sample missing candidate IDs** (first 1 of 1): `candidate_00567`

## Recovery effort estimate

### Headline numbers

- **Total cells with gap > 0 (genuine):** 30 (excludes the `verified-cleanup`
  partial-output artefact).
- **Cumulative dropped candidates (genuine):** 835.
- **Paper-feeding subset:** 19 cells, cumulative gap **773 candidates**.
- **Non-paper / legacy diagnostic:** 11 cells, cumulative gap 62 candidates
  (10 cells under `pv-diag-384/verified/` plus the unreferenced
  `proposer-verifier-384/verified-adversarial-text-v1-prompt`).

### Paper-feeding cells (priority for cleanup)

| Group | Cells affected | Cumulative gap | Notes |
|---|---|---|---|
| `flash-high-image-n5` matrix (`pv-diag-384/`) | 4 | 473 | Drives the image-temperature sweep cells `flash-high-image-n5-t{0.3,0.7,1.0}-greedy-v1-487tile.json`. The image-t0.0 cell with gap=460 is the largest single offender in the entire audit and should be cleaned first. |
| `e47-propose-brief/verified/flash-high-text-{1..5}of5` | 5 | 127 | Per-pass production verifier outputs feeding `compare_wbf_vs_greedy_production.py` and the e47 leaderboard cells. |
| `pv-diag-384/.../session-78-matrix/verified-*-text` | 7 | 154 | Drives the `session-78-*-487tile.json` leaderboard cells (image and text adversarial/brief/checklist matrices). |
| `h8-v2/wbf/scale-4/verified` | 1 | 15 | h8-v2 production cell, scale-4 WBF variant. |
| `55maps-generalisation/verified-v2` | 1 | 3 | Note: canonical `verified/` is gap=0; v2 appears to be a partially-re-verified copy. Investigate whether `verified-v2` is in active use. |
| `pv-diag-384/scale-4-optimal-487/verified-v1-n10` | 1 | 1 | Trivial single-candidate gap. |
| `pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-checklist` | (already counted in session-78 row) | | |
| **Total paper-feeding** | **19** | **773** | |

### Non-paper / legacy cells (defer or skip)

The remaining 11 cells (cumulative gap 62) live under
`pv-diag-384/verified/` and `proposer-verifier-384/`. They are small (gaps of
1–21) and are the products of cross-verifier exploratory runs (e.g.
`pro-verifier`, `medium-verifier`, `flash-medium-verifier` suffixes) that were
not used in any leaderboard or production analysis. Recommendation: defer
recovery, archive the cells, and document this audit in the H11 reflection
log so the gaps are traceable.

### Recovery mechanics

The recovery pattern is identical to today's GS-v2 / 55-maps cleanup:

```bash
python scripts/run_pv.py cleanup \
  --crops-dir <CROPS_DIR_FROM_TABLE> \
  --verified-dir <DIR_CONTAINING_PROBABILITIES_JSON> \
  --verifier-config <THE_CELL'S_ORIGINAL_VERIFIER_CONFIG> \
  --max-attempts 3 \
  --safe-mode-tokens 4096   # only on final attempt
```

Each cleanup creates a `.pre-cleanup-<timestamp>.backup` of the prior
`probabilities.json` and appends a `cleanup_history` entry to the new file.
Compute load is small: 773 candidates @ ~1–2 verifier calls each = roughly
1,000 verifier API calls total, distributed over ~19 cleanup invocations.
Most cells need <30 calls. The single largest cell
(`flash-high-image-n5/image-t0.0/verified-v1-n10`, gap=460) will dominate
elapsed time but is still small relative to a fresh full verifier pass.

### Risk to leaderboard / Obs framings

- **Tier rankings most at risk:** the 4 `flash-high-image-n5` matrix cells
  (gap 1, 1, 11, 460). The image-t0.0/v1-n10 cell sits at the lowest verifier
  threshold; its 460-candidate gap (57% of the input pool) is large enough
  that recovery may shift its F1 / MCC rankings appreciably. The other three
  have gap ≤ 11 against pools of ~2,000–3,000, so the F1 movement is likely
  in the 0.001–0.005 range. Comparable to the GS-v2 +0.013 correction landed
  today.
- **WBF-vs-greedy comparison (Obs 277/280):** the 5 e47 production cells (gap
  9–57 against pools of 487–4,358) and `h8-v2/wbf/scale-4` (gap 15) feed
  this comparison. Recovery is expected to shift greedy-side F1s by
  ≤ 0.005 across the comparison, but the specific direction cannot be
  predicted without running cleanup.
- **Session-78 matrix (Obs 297):** 7 cells with gaps of 1–41 against
  pools of ~2,000–3,800. Movement should be small but non-zero.
- **GS-v2 production cell:** already cleaned today (gap=0 confirmed in this
  audit, line 196 of the full table).

## Provenance

- Audit script: `/tmp/verifier_audit.py` (read-only file inspection; no API or
  filesystem mutation).
- Missing-IDs script: `/tmp/missing_ids.py` (computes the set difference
  between input candidate IDs and `probabilities.results` keys).
- Run on amd-tower (cwd `/home/shawn/Code/map-reader-llm`) at the start of
  Session 85, immediately after the GS-v2 / 55-maps cleanup landed in
  Session 84.

## Recovery status (annotated post-execution, partial — 2026-05-06)

Annotated after the Tier-1 propagation closure landed in Session 86 / 87
(zbook, post-travel). See **Obs 323** (commit `64974ec5`) for the full
campaign-closure write-up.

### Cleanup phase — completed 2026-05-03 / 04 overnight

- **17 of 20 cells cleaned** during the unattended sapphire run, 530
  candidates recovered, total cleanup-phase API spend $0.905. Ground truth
  in `logs/phase3a-recovery-overnight-resume/launch-summary.md`.
- **3 cells skipped**, all with `reason: missing_crops_gitignored` (the
  bulk crop PNGs are gitignored intermediates not present on every machine):
  - `e47-flash-high-text-1of5` (Tier 1, gap 57) — schema-transformation
    diagnostic in the launch-summary § "Surprise"; data-integrity question
    first.
  - `55maps-gen-verified-v2` (Tier 2, gap 3) — clean-cut; regenerate crops
    + re-run.
  - `proposer-verifier-384-adversarial-text-v1-prompt` (Tier 3, gap 1) —
    clean-cut; regenerate crops + re-run.

### Propagation status

- **Tier 1 (Session-78 6 cells)**: COMPLETE. Per-arch tier composition
  rebuilt (commit `c067bca4`); combined Era-2 leaderboard + tier stability
  rebuilt (commit `a8f4b7f8`). Audit anchor: 38 unchanged Era-2-pv cells
  byte-identical F1 vs pre-recovery `b4c28d5b`; 6 cleaned cells show
  expected ΔF1 in range −0.0007 to +0.0103 absolute. One tier flip in
  combined view (`session-78-image-brief-text` 5→4, an improvement); other
  13 Session-78 cells preserved tier rank.
- **Tier 2 / Tier 3 propagation**: NOT LANDED on `origin/main`. Beyond
  `b3ed509e` (Tier-1 materialise + calibration on 2026-05-03), no further
  recovery commits exist on origin. Sapphire was off-network during user
  travel; whatever local state sapphire holds is unknown. **Campaign-wide
  closure deferred** until sapphire is reachable and Tier-2/3 propagation
  can be confirmed or re-run.

### Methodological note — wrong-driver detour

The Tier-1 per-architecture rebuild on 2026-05-05 evening initially used
`scripts/run_per_arch_leaderboards.sh` (default `--top-n 20`) instead of
the canonical `scripts/build_per_arch_redesign.sh` (`--top-n 0`),
silently thinning three strata (era1/consensus 72→37, era2/consensus
29→22, era2/pv 44→26). The operator caught this via spot-check; an
overnight investigation agent traced the cause to a convention-propagation
failure inherited from commit `03bf71c8`. Fixes landed in commits
`baa271bf` (runner now passes `--top-n 0` + `--seed 42`) and `ef3ec4fe`
(runbook § 6.1 / 6.2 corrected: tier rebuild now separated from
post-processing). Investigation report at
`archive/investigations/session-86-tier-regression-investigation.md`. Another instance
of the project's documented "convention-propagation failure" pattern
(E19/E20 lineage). Worth flagging because the original Phase3a recovery
runbook itself directed the wrong driver — readers of this audit who
follow the runbook should ensure they invoke the corrected runner.

### Outstanding work

1. **Reach sapphire and verify Tier-2/3 cleanup status** — whatever was
   committed locally on sapphire during the unattended overnight run.
2. **Resolve the 3 skipped cells**: e47 needs the schema-integrity
   investigation first; the other two are clean-cut crop-regen + cleanup.
3. **Tier-2 + Tier-3 propagation** through their leaderboard strata once
   their cleanup state is known.
4. **Campaign-wide closure Obs** (Obs 324 or later) once the above lands.
