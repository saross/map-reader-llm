# Flash Variability Study (N=30): The "Law of Large Numbers" Effect
**Date**: December 19, 2025
**Model**: Gemini 3 Flash Preview (v3.2 Prompt)
**Dataset**: 30 Independent Runs (N=30 Pool)

## 1. Executive Summary
We performed a massive N=30 variability study on the cheaper **Gemini 3 Flash** model to test if high-volume consensus could rival **Gemini 3 Pro**.

**The Answer: YES.**

*   **Peak Performance**: **F1 0.920** (at 10/30 Votes).
    *   This statistically matches the Pro N=10 Peak (F1 0.918).
*   **Cost Efficiency**: 
    *   Flash is estimated to be ~1/10th to 1/20th the price of Pro.
    *   Running Flash 30 times is largely cheaper than running Pro 5-10 times.

## 2. The Flash Drop-Off Curve (N=30)
Unlike Pro, which peaked at 40% agreement, Flash peaks slightly earlier at **33% (10/30)**.

| Votes (T) | Agreement | F1 Score | Insight |
| :--- | :--- | :--- | :--- |
| 1/30 | 3% | 0.191 | Noise explosion. |
| ... | | | |
| 8/30 | 26% | 0.893 | Strong. |
| 9/30 | 30% | 0.902 | |
| **10/30** | **33%** | **0.920** 🏆 | **Global Maximum**. Matches Pro Peak. |
| 11/30 | 36% | 0.909 | |
| 12/30 | 40% | 0.896 | |
| ... | | | |
| 30/30 | 100% | 0.111 | Impossible. |

## 3. Comparative Analysis (Pro vs Flash)

| Strategy | Model | Total Runs | Agreement Rule | F1 Score | Est. Cost Unit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Daily Driver** | **Pro** | 5 | 2/5 (40%) | **0.898** | **5x** |
| | Flash | 5 | 2/5 (40%) | 0.855 | 0.5x |
| | | | | | |
| **Gold Standard** | **Pro** | 10 | 4/10 (40%) | **0.918** | **10x** |
| **Swarm** | **Flash** | 30 | 10/30 (33%) | **0.920** | **~1.5x?** |

## 4. Conclusion
*   **For Small Batches (N=5)**: **Pro Wins**. Flash is too noisy (0.85 vs 0.90).
*   **For High Precision (Gold Standard)**: **Flash Swarm (N=30) Wins**. It achieves the same accuracy as Pro N=10 but is drastically cheaper.

**Recommendation**:
If api rate limits allows, replacing the N=10 Pro "Gold Standard" strategy with an N=30 Flash "Swarm" strategy is far more economical for the same quality.
