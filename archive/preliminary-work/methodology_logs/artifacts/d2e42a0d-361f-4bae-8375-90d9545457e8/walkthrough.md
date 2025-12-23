# Stage 2 Verifier (v4.5) Results

## Executive Summary
We have implemented the **Precision Verifier (v4.5)** using a **29-shot Federated Library**.
Validation on the Training Set shows a **+10% boost in Precision** (0.67 -> 0.77).

## Metrics Comparison (Training Set)

| Metric | Stage 1 (Proposer) | Stage 2 (Verifier) | Delta |
| :--- | :--- | :--- | :--- |
| **Precision** | 0.6714 | **0.7679** | **+0.0965** |
| **Recall** | 0.9216 | **0.8431** | -0.0785 |
| **F1 Score** | 0.7769 | **0.8037** | +0.0268 |

> [!NOTE]
> The Verifier removed **43% of False Positives** (10/23), sacrificing only 4 True Positives.

## Consensus Optimization (Experiment)
To determine the pipeline's performance ceiling, we tested a **Proposer Union + Verifier Consensus** strategy (N=5 runs).

| Strategy | Logic | Recall | Precision | F1 Score | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Baseline** | Single Run (Temp 0.7) -> Verifier (1-pass) | **0.84** | 0.77 | **0.80** | **Best F1** 🏆 |
| **Consensus A** | Proposer Vote $\ge$ 3 -> Verifier Vote $\ge$ 1 | 0.75 | 0.75 | 0.75 | Lower F1. |
| **Consensus B** | Proposer Vote $\ge$ 3 -> Verifier Vote $\ge$ 3 | 0.59 | **0.94** | 0.72 | Max Precision. |

**Conclusion**: The **Single-Run Pipeline** is the most efficient and balanced approach (F1 0.80). Consensus strategies trade too much Recall for Precision gains. We will proceed with the Single-Run architecture.
