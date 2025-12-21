# Stock-Taking Report: Maps Reader LLM (Prompts v3.0+)

**Generated**: 2025-12-22
**Scope**: All runs and experiments using prompt versions v3.0 or later.

## 1. Executive Summary

We have evaluated a wide strategy space, ranging from single-shot Flash runs to expensive "Pro Consensus" ensembles.

*   **Top Performer (Accuracy)**: **Flash Swarm 10/30** (F1 0.920) and **Pro 2/5 Consensus** (F1 0.914).
*   **Most Efficient**: **Flash 2/5 Consensus** (F1 0.86). Matches single-shot Pro performance at specific fraction of the cost.
*   **Best Single-Shot**: **Gemini 3 Pro v3.5 Clean** (F1 0.886).
*   **Failed Experiments**: "Two-Stage Verifier" (High Precision, Low Recall) and "Image-Only Flash Swarm" (Total Collapse).

---

## 2. Strategy Performance Matrix

| Prompt / Strategy | Model | F1 Score | Recall | Precision | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **v3.2 (N=30 Swarm)** | Flash | **0.920** | **0.92** | **0.92** | **The Ceiling.** High volume voting (10/30) eliminates noise. |
| **v3.5 Clean (Consensus 2/5)** | Pro | **0.914** | **0.914** | **0.914** | **SOTA Recommendation.** Stable, high accuracy strategy. |
| **v3.2 (Consensus 2/5)** | Pro | **0.898** | 0.92 | 0.88 | Previous SOTA. Slightly lower precision than v3.5 Clean. |
| **v3.5 Clean (Single Run)** | Pro | 0.886 | 0.894 | 0.877 | Strong baseline. |
| **v4.6 (Verifier)** | Pro | 0.716 | 0.57 | **0.97** | **Precision Specialist.** useful only if FPs are unacceptable. Recall is poor. |
| **v3.5 Clean (Swarm N=30)** | Flash | 0.00 | 0.00 | 0.00 | **Critical Failure.** Image-Only prompt collapsed at high temp/volume. |

---

## 3. Notable Experiments & Observations

### A. The "Clean Prompt" Victory (v3.5)
Removing text constraints ("No spikes", "No numbers") and relying purely on visual examples improved Pro performance.
*   **v3.2 (Text Constraints)**: F1 0.85 (Single), 0.90 (Consensus).
*   **v3.5 (Image Only)**: F1 0.89 (Single), 0.91 (Consensus).
*   **Insight**: Text constraints introduce "Modality Interference", causing the model to second-guess valid visual patterns.

### B. The "Consensus" vs "Verifier" Showdown
We explicitly tested whether it is better to "Vote" (Consensus) or "Judge" (Two-Stage Verifier).
*   **Consensus (2/5)**: F1 0.91. Simple, robust.
*   **Verifier (v4.6)**: F1 0.72. Complex, brittle.
*   **Verdict**: Voting is superior. Stochastic agreement across runs is a stronger signal than logical deduction on a single crop.

### C. The "Flash Swarm" Anomaly
*   **v3.2 (Text+Image) Swarm**: F1 0.92.
*   **v3.5 (Image-Only) Swarm**: F1 0.00.
*   **Insight**: Flash *requires* text scaffolding to maintain coherence at high temperatures (1.0). Without text, it hallucinates wildly. Pro does not suffer from this dependency.

### D. Symbol-Specific Performance (v3.5 Pro)
Breakdown of the optimal v3.5 Clean (Single Run) performance:

| Symbol | F1 Score | Notes |
| :--- | :--- | :--- |
| **Burial Mound** | 0.88 | High stability (Std Dev ±0.04). |
| **Benchmark** | 0.88 | Surprisingly high. Hard Negatives worked. |
| **Triangulation** | 0.69 | Lower stability. Often missed or confused. |

---

## 4. Recommendations
1.  **Production**: Deploy **Gemini 3 Pro + v3.5 Clean Prompt + 2/5 Consensus**.
2.  **High-Volume**: Investigate why `v3.5` failed on Flash. If fixed, Flash Swarm fits the budget better.
3.  **Archive**: Deprecate v4.x (Two-Stage) pipelines. The complexity is not justified by the performance.
