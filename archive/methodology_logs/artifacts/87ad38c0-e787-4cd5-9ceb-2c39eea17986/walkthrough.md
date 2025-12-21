# Walkthrough - Overnight Experiments & Consensus Analysis

## Experiments Overview
This session focused on completing the "Overnight Experiments" suite and performing a Consensus Analysis on Job A.

### Job A: Gemini 3 Pro (v3.5 Single Stage)
- **Goal**: N=5 runs to assess variability and consensus.
- **Config**: `prompts/versions/v3.5_clean_pro.json` (Temp 0.3).
- **Status**: **Completed**.
    - Runs 1-3: Completed previously (Temp 0.3).
    - Run 4: Re-run successfully (Temp 0.3, F1 0.87).
    - Run 5: Re-run successfully (Temp 0.3).
- **Consensus Analysis**:
    - Performed N-of-5 analysis on the corrected 5 runs.
    - **Optimal Threshold**: **2 of 5 votes**.
    - **Result**: **F1 0.914** (vs Mean Single Run F1 0.886).

### Job C: Gemini 3 Pro (v4.6 Two-Stage Verifier)
- **Goal**: N=1 Verify candidate pool.
- **Status**: **Completed**.
    - Output: `outputs/overnight/job_c_pro_verifier/verified_v4.6_pro.geojson`.
    - 69 candidates verified.

## Key Results

### Consensus Analysis (Job A)
Using 5 runs of Gemini 3 Pro (Temp 0.3):

| Strategy | F1 Score | Precision | Recall | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Consensus 2/5** | **0.9143** | **0.914** | **0.914** | **Best Performance** |
| Single Run (Mean) | 0.8856 | 0.877 | 0.894 | Baseline |
| Consensus 1/5 | 0.8099 | 0.810 | 0.810 | High Noise |
| Consensus 3/5 | 0.8602 | 0.860 | 0.860 | Strict |

> [!TIP]
> **Consensus 2/5** offers a huge boost in stability and performance, pushing F1 over 0.91. This suggests "At least 2 models agree" is the sweet spot for this prompt configuration.

## Files Created
- `scripts/rerun_4_5.sh`: Temporary script for re-runs.
- `scripts/generate_metrics_for_consensus.py`: Utility to generate metrics.json.
- `scripts/generate_validation_bounds.py`: Utility to generate bounds file.
- `inputs/vectors/validation_bounds.geojson`: Bounds file for analysis.
- `outputs/results/analysis_variability_exhaustive/variability_report.md`: Detailed consensus report.

## Next Steps
- Implement the "2-of-5" consensus strategy in the production pipeline if cost permits (5x inference cost).
- Analyze "Job C" Verifier results deeper to see if it outperforms the 2/5 Consensus.
    - **Update**: Job C (Verifier) analysis completed. resulted in F1 0.716.
    - **Conclusion**: Consensus strategy (F1 0.914) significantly outperforms the current Verifier (F1 0.716) which is too conservative (Recall ~0.57).
