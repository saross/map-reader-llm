# Statistical Verification & Metrics Strategy

## 1. Core Principles
To move beyond anecdotal observation, all production benchmarks must quantify two types of uncertainty:
1.  **Spatial Uncertainty (Single Run)**: How robust is the detection map to the specific random subset of tiles? (Measured via Bootstrap Resampling of tiles).
2.  **Strategy Uncertainty (Multi-Run)**: How robust is the *strategy* (e.g. "Vote 2/3") to the specific random subset of runs? (Measured via Exhaustive/Combinatorial Simulation).

## 2. Methodology

### A. Single Run Analysis (`benchmark_single_wrapper.py`)
For any single inference run, we calculate:
*   **Standard Metrics**: Precision, Recall, F1 (Global).
*   **Spatial Tolerance Curve**: F1 scores at buffer distances [10m, 20m, 30m, 50m]. Answer: "Is the model just missing slightly?"
*   **Bootstrap 95% CI**: Resample the 20 test tiles with replacement (N=1000) to generate a distribution of F1 scores. Answer: "Was this run lucky?"

### B. Variability & Consensus Analysis (`benchmark_variability.py`)
To determine the optimal production strategy (e.g., "Run 3 times, keep agreements"), we simulate all possibilities from our available N=10 variability pool.

#### Simulation Parameters
*   **Pool Sizes (N)**: 3, 5, 10.
*   **Voting Thresholds (T)**: 1 to N.

#### Workflow
For a given Strategy (Pool=N, Vote=T):
1.  **Generate Combinations**: Create all unique combinations of N runs from the Total Pool (Size 10).
    *   *Example (N=3)*: ${_10}C_3 = 120$ combinations.
2.  **Compute Consensus**: For each combination, generate a consensus map (features present in $\ge T$ runs).
3.  **Evaluate**: Calculate F1 for each consensus map.
4.  **Strategy Statistics**: report the Mean, Median, Min, Max, and 95% CI of the resulting F1 distribution.

### C. Definitions
*   **F1 Score**: Harmonic mean of Precision and Recall.
*   **Consensus Feature**: A bounding box formed by averaging the coordinates of overlapping detections from at least $T$ participating runs.
*   **Confidence Interval (CI)**: The range [2.5th percentile, 97.5th percentile] of the distribution.

## 3. Reporting Format
Results will be presented in comparative tables to identify the "Pareto Frontier" of strategies (maximizing F1 while minimizing compute cost).

| Strategy | Mean F1 | 95% CI | Precision | Recall | Cost (Runs) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Single Run** | 0.85 | [0.80, 0.89] | 0.86 | 0.83 | 1x |
| **5-Run (Vote 2)** | 0.90 | [0.87, 0.92] | 0.86 | 0.93 | 5x |
