# Stock-Taking Implementation Plan

## Goal
Compile a comprehensive CSV and Markdown report of all model runs using prompts v3.0+, detailing performance metrics, strategies, and symbol-specific breakdowns.

## 1. Data Aggregation Strategy
I will create a script `scripts/compile_stock_taking.py` to:
1.  **Scan Directories**: `outputs/results`, `archive/results`, `outputs/overnight`.
2.  **Filter**: Path matching `v3.*`, `v4.*`.
3.  **Detect Metrics**:
    *   Look for `*_metrics.json`, `*_advanced_metrics.json`.
    *   Look for `*.meta.json` (for prompt config).
    *   Look for `variability_report.md` (for consensus results).
    *   Look for `strategy_stats.csv` (for consensus results).
4.  **On-Demand Calculation**:
    *   If metrics are missing but `_bounds.geojson` + `.geojson` exist, calculate basic F1/Precision/Recall using `lib_advanced_metrics.py`.
5.  **Output**: `stock_taking.csv`.

## 2. Reporting
I will generate `reports/stock_taking_report.md` synthesizing the data:
*   **Table of Contents**: By Prompt Version.
*   **Performance Matrices**: F1/Prec/Rec tables.
*   **Symbol Analysis**: Deep dive into symbol-specific performance where available.
*   **Consensus vs Single**: Comparison of strategies.

## 3. Verification
*   Check that `v3.5_clean_pro` (Consensus) is correctly captured.
*   Check that `job_c_pro_verifier` is captured.
*   Check that `variability_study_v3.2` is captured.

## 4. Execution
*   Run the script.
*   Review CSV.
*   Write the report.
