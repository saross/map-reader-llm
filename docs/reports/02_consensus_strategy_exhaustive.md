# Statistical Variability Report: Optimal Consensus Strategies
**Date**: December 19, 2025
**Model**: Gemini 3 Pro (v3.2 Prompt)
**Dataset**: 10 Independent Runs (N=10 Pool)

## 1. Executive Summary
We performed an **exhaustive combinatorial simulation** to determine the most robust production strategy. By simulating every possible combination of runs for different pool sizes (N=3, 5, 10), we identified the "Pareto Frontier" of cost vs. accuracy.

**Key Findings:**
1.  **Cost-Effective Optimal**: **[Pool 5, Vote 2] (40% Agreement)**.
    *   **Mean F1**: **0.898**.
    *   **Stability**: **[0.874, 0.922]** (Very stable).
    *   *Why*: It matches the performance of expensive strategies while keeping compute costs moderate.
2.  **Absolute Best Performance**: **[Pool 10, Vote 4]**.
    *   **F1**: **0.918** (The highest score achieved).
    *   *Why*: If budget is unlimited, running 10 times and filtering for 40% agreement yields the best map.
3.  **Refutation**: The "2 of 3" strategy (Claude's suggestion) performs poorly (**F1 0.806**) compared to the single-run baseline (**F1 0.867**).

## 2. The N=10 Drop-Off Curve
We tested the impact of strictness on the full 10-run set. The results show a classic bell curve where F1 peaks at T=4 (40%) and collapses after T=5.

| Agreement Required | Threshold (T) | Mean F1 | Precision | Recall | Insight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Loose** | 1/10 | 0.685 | Low | High | Huge noise (False Positives). |
| | 2/10 | 0.857 | Good | High | Better, but still noisy. |
| **Balanced** | 3/10 | 0.911 | High | High | Excellent. |
| **Strict** | **4/10** | **0.918** 🏆 | **Very High** | **High** | **PEAK PERFORMANCE**. |
| | 5/10 | 0.805 | High | Dropping | Recall regression begins. |
| **Too Strict** | 6/10 | 0.649 | High | Low | Valid mounds consistently missed. |
| | 7/10 | 0.535 | Max | Very Low | |
| | 8/10 | 0.493 | Max | Very Low | |
| | 9/10 | 0.323 | Max | Poor | |
| | 10/10 | 0.271 | Max | Terrible | Unanimity is impossible. |

## 3. Exhaustive Simulation Results (Subsets)
For N=3 and N=5, we simulated **all** possible combinations (${_10}C_3=120$, ${_10}C_5=252$) to quantify risk.

| Strategy (Runs / Votes) | Agreement % | Mean F1 | 95% CI (Stability) | Min F1 | Max F1 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Single Run (Control)** | - | **0.867** | [0.820, 0.906] | 0.812 | 0.911 |
| | | | | | |
| Pool 3 / Vote 1 | 33% | 0.824 | [0.786, 0.860] | 0.777 | 0.865 |
| **Pool 3 / Vote 2** | 66% | 0.806 | **[0.735, 0.872]** | 0.721 | 0.887 |
| Pool 3 / Vote 3 | 100% | 0.464 | [0.374, 0.575] | 0.323 | 0.613 |
| | | | | | |
| Pool 5 / Vote 1 | 20% | 0.775 | [0.739, 0.817] | 0.731 | 0.831 |
| **Pool 5 / Vote 2** | 40% | **0.898** | **[0.874, 0.922]** | **0.865** | **0.931** |
| Pool 5 / Vote 3 | 60% | 0.780 | [0.709, 0.841] | 0.691 | 0.857 |
| Pool 5 / Vote 4 | 80% | 0.543 | [0.448, 0.632] | 0.424 | 0.667 |
| Pool 5 / Vote 5 | 100% | 0.348 | [0.271, 0.424] | 0.267 | 0.448 |

## 4. Recommendation
*   **Production Standard**: **Pool 5 / Vote 2**. It is essentially as good as the N=10 strategies (0.898 vs 0.918) but costs half as much. It is significantly more stable (CI width 0.05) than single runs (CI width 0.09).
*   **Gold Standard**: **Pool 10 / Vote 4**. Use this for creating reference datasets or settling difficult tiles.
