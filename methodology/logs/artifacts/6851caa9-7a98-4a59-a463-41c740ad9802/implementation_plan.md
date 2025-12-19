# Implementation Plan - Statistical & Strategy Upgrade

**Goal**: Elevate the analysis pipeline from simple metrics to rigorous statistical modeling. This involves refactoring the benchmarking scripts to support exhaustive simulation of consensus strategies (e.g., "2 of 3", "3 of 5") and integrating 95% Confidence Intervals and Spatial Tolerance Curves into all reports.

## User Review Required
> [!NOTE]
> **No API Calls Required**: We will re-analyze the existing N=10 variability dataset. No new quota will be consumed.

## Proposed Changes

### 1. Unified Benchmark Wrapper
#### [NEW] [benchmark_single.py](file:///home/shawn/Code/map-reader-llm/scripts/benchmark_single.py)
A standardized wrapper for `run_v3_1_benchmark.py` that ensures consistent configuration and report generation for single runs.
*   **Inputs**: Config path, Tile manifest.
*   **Outputs**: `_metrics.json` AND `_advanced_metrics.json` (Spatial Tolerance, Bootstrap CI).

### 2. The Variability Engine (Analysis Upgrade)
#### [NEW] [benchmark_variability.py](file:///home/shawn/Code/map-reader-llm/scripts/benchmark_variability.py)
*Replaces/Upgrades `scripts/7_deep_variability_analysis.py`*

**New Features**:
1.  **Exhaustive Simulation**:
    *   Instead of random sampling, exhaustively simulate **ALL** combinations for small pools:
        *   **N=3** (Pool Size): Test thresholds T=1..3. (Combinations: ${_10}C_3 = 120$).
        *   **N=5** (Pool Size): Test thresholds T=1..5. (Combinations: ${_10}C_5 = 252$).
        *   **N=10** (Pool Size): Test thresholds T=3,5,7,10. (Combinations: 1).
2.  **Advanced Metrics Integration**:
    *   For every "winning" consensus result (e.g., the consensus set from a N=3 T=2 vote), run `lib_advanced_metrics.generate_report`.
    *   This provides **Spatial Tolerance Curves** (F1 at 10px vs 20px) for the *consensus* output, answering "Does voting recover precision at strict tolerances?".
3.  **Confidence Intervals**:
    *   Calculate 95% CIs for the consensus strategies (e.g., "The Mean F1 of a 2-of-3 strategy is 0.77 ± 0.05").

### 3. Reporting
*   **Output**: `docs/statistical_variability_report.md`
*   **Visuals**: Tables comparing "Single Run" vs "3-Run Consensus" vs "5-Run Consensus".

## Verification Plan
1.  **Execute**: Run `scripts/benchmark_variability.py` on the `outputs/results/v3.2_experimental` data.
2.  **Verify**: Check that the output report answers the user's specific questions:
    *   "Is 1 of 3 better than 2 of 3?"
    *   "Confidence Intervals included?"
