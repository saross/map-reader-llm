# Deprecated Scripts

This directory contains scripts that have been superseded or are no longer in active use.

## Archived Scripts

| Script | Date Archived | Reason |
|--------|---------------|--------|
| `7_analyze_consensus_runs.py` | 2026-01-17 | Superseded by `7_analyze_consensus.py` which provides more sophisticated 2D grid search on proposer + verifier vote thresholds |
| `archive_cc_sessions.py` | 2024-12-23 | Superseded by `archive_cc_session.py` with v1.1 schema support |
| `archive_methodology.py` | 2024-12-21 | One-off script for initial methodology archival |
| `benchmark_single_wrapper.py` | 2024-12-23 | Experimental benchmarking script |
| `check_holdout_expansion_feasibility.py` | 2026-01-08 | One-off analysis for holdout set expansion decision |
| `check_resolution.py` | 2024-12-20 | Simple debugging script |
| `generate_overnight_configs.py` | 2024-12-23 | Experimental config generator |
| `list_models.py` | 2024-12-20 | Simple utility to list available models |
| `carry_probabilities-recovery-fix-harness.py` | 2026-09-13 | **Promoted, not deprecated.** Written as `results/k-ladder-2026-09-12/recovery-fix-2026-09-13/harness/carry_probabilities.py` for the recovery-fragment fix and promoted to `scripts/carry_probabilities.py` under checklist item 6a: re-keying verifier probabilities onto a rebuilt union's candidate numbering is a general need, and deciding coverage on the integer crop window rather than on metric distance is the lesson of `reports/recovery-drop-fix-2026-09-13.md` § 6.1. The promoted copy has the same matching and window logic, refactored into testable functions with an injectable window resolver, a `--dry-run` coverage census, and `tests/test_carry_probabilities.py` (13 tier-1 tests). Kept here because the recovery-fix job's committed `carry_provenance.json` files were produced by *this* file. |
