# Pairwise contrasts on the drifted single-pass arms, re-run 2026-10-15

> **Last revised**: 2026-10-15 (original publication). See
> [§ Changelog](#changelog) for revision history.

## What this directory holds

Today's runs of the paired tile-swap permutation contrasts in which one arm
is a single-pass Flash text consensus set at temperature 0.0: the 5-of-5
and 10-of-10 sets of `outputs/retest/h11-single-pass-384-t0` (condition
`brief-text-t0`). Each file sits at the same relative path as the committed
March 2026 file it stands beside, which stays where it is as a historical
record.

| Here | Beside (March 2026, historical record) | Files |
|---|---|---:|
| `20m/group_1_architecture/` | `results/pairwise/20m/group_1_architecture/` | 2 |
| `30m/group_1_architecture/` | `results/pairwise/30m/group_1_architecture/` | 2 |
| `leaderboard-20m/group_8/` | `results/pairwise/leaderboard-20m/group_8/` | 49 |
| `leaderboard-30m/group_8/` | `results/pairwise/leaderboard-30m/group_8/` | 47 |

## Why the March files stay

The single-pass pass files changed after the March runs read them and
before they were first tracked (commit `3d22184d6`, 2026-04-15), so the
inputs as scored cannot be recovered. Replaying the March code on today's
files gives 954 detections for the 5-of-5 set, where the March outputs
record 951, and 901 for the 10-of-10 set, where they record 898
(principal investigator (PI) ruling D61 (2);
`reports/s163-agent-records/d60-3-consensus-route.md` § 1). Under ruling
D58 Q2 the March files therefore stay as historical records, and today's
runs go here, beside them, labelled.

Today's runs also carry the consensus-route fix of ruling D60 (3) (commit
`4e9d659ab`): each consensus cluster keeps the tiles that contributed to
it, so the scorer attributes it to its own sheet.

## How these files were made

From the repository root, with 10,000 permutations and seed 42, each with
the committed run's flags:

```bash
python scripts/run_pairwise_tests.py --config configs/pairwise-comparisons.yaml \
    --buffer-metres 20 --n-permutations 10000 --seed 42 --quiet \
    --output-dir results/pairwise/20m
python scripts/run_pairwise_tests.py --config configs/pairwise-comparisons.yaml \
    --buffer-metres 30 --n-permutations 10000 --seed 42 --quiet \
    --output-dir results/pairwise/30m
python scripts/run_pairwise_tests.py --leaderboard configs/condition-registry.yaml \
    --metrics results/paper-tables/metrics_master.csv --top-n 26 \
    --buffer-metres 20 --n-permutations 10000 --seed 42 \
    --output-dir results/pairwise/leaderboard-20m
git show 71d81cd5e:results/paper-tables/metrics_master.csv > metrics_master-71d81cd5e.csv
python scripts/run_pairwise_tests.py --leaderboard configs/condition-registry.yaml \
    --metrics metrics_master-71d81cd5e.csv --top-n 25 \
    --buffer-metres 30 --n-permutations 10000 --seed 42 --quiet \
    --output-dir results/pairwise/leaderboard-30m
```

Each run was followed by
`python scripts/apply_fdr_correction.py --results-dir <dir> --output-dir <dir>/fdr`.
The 30 m leaderboard reads the metrics table as it stood when that board
first ran (`71d81cd5e`): the table gained four rows on 2026-03-29, and with
them the top 25 conditions at 30 m would no longer be the board's 25.

The runs wrote every contrast under `results/pairwise/`; the files listed
above were then moved here and the March files restored at their paths.
Each directory's `run_manifest.json` and `fdr/` under `results/pairwise/`
belong to today's complete run, so their entries for these contrasts equal
the files here, not the March files beside them. The Benjamini–Hochberg
false discovery rate (FDR) correction is applied over that complete run.

## Changelog

### 2026-10-15 — Original publication

First version, written with the S164 restatement pass
(`reports/s164-agent-records/restatement-pass.md` § 1.5).
