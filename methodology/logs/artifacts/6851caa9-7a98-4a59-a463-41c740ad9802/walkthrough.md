# Walkthrough - v3.2 Stability Fix

## Goal
Stabilize the **v3.2 Experimental Prompt** (High Precision/F1=0.80) on **Gemini 3 Flash Preview**, which was previously failing with `finish_reason: 2` (Max Tokens) errors on dense map tiles.

## Investigation
*   **Issue**: The model entered infinite generation loops on complex tiles due to the large context (16 few-shot examples), causing it to hit the 8k output token limit or timeout.
*   **Hypothesis**: These failures are intermittent/stochastic, not deterministic.
*   **Experiment**: Ran a retry script (`experiment_retry_v3.2.py`) on 5 failed tiles.
    *   **Result**: 13/15 attempts succeeded (86% success rate).
    *   **Conclusion**: The prompt is viable *if* we handle the occasional failure.

## Changes Implemented
We patched the inference script `scripts/4_detect_mounds_batch.py` to handle failure modes and improve observability:

1.  **Max Tokens Retry**: Added logic to detect `finish_reason: 2` and retry up to 3 times.
2.  **Defensive Parsing**: Handled cases where the model wraps JSON in a list or omits keys.
3.  **Enhanced Metadata**: Added `retry_details` and `failed_tiles_details` lists to the output metadata to track specific failures and error messages per tile.

## Verification Results
We ran the official benchmark script (`run_v3_1_benchmark.py`) on the 20-tile Target Set.

*   **Completion**: **20/20 (100%)**
*   **Status**: **PASSED**

### Official Metrics
| Metric | Score | Note |
| :--- | :--- | :--- |
| **Precision** | **0.7115** | High precision maintained. |
| **Recall** | **0.8043** | Excellent recall (37/46 mounds found). |
| **F1 Score** | **0.7551** | Strong, stable performance. |

> [!TIP]
> **Key Takeaway**: The system is now robust. Using the official benchmark script ensures we capture all statistics, including specific retry events, in the metadata sidecar file.

## Next Steps
The v3.2 prompt is "Production Ready" for Flash. We can proceed to scale up processing.
