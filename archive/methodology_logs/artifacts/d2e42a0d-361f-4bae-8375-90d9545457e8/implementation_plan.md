# Implementation Plan: Pipeline Validation

## Goal
Validate the optimized "Propose-and-Verify" pipeline on the Holdout Set (Reserve) to confirm generalization.

## Current Best Configuration (SOTA)
*   **Proposer (Stage 1)**: Gemini 3 Flash (v4.2 Prompt, Temp 0.7, Union of 5 Runs).
*   **Verifier (Stage 2)**: Gemini 2.0 Flash (v4.6 Prompt, Temp 0.0, Single Pass).
    *   **Prompt**: Text-Free, Image-First, 48-Shot Library.
    *   **Metrics**: F1 0.874 (Training Set).

## Research Status (Optimization Phase)
*   **Grid Overlays**: Failed (Recall 0.53).
*   **Consensus**: Failed (Recall < 0.20).
*   **Gemini 3 Flash (Verifier)**: Underperforms (F1 0.865) vs Gemini 2.0.

## Validation Phase (Next Steps)
1.  **Generate Candidates**: Run `v4.2` Proposer on Holdout Manifest.
2.  **Verify Candidates**: Run `v4.6` Verifier (Gemini 2.0 Flash) on the resulting crops.
3.  **Analyze**:
    *   **Target**: F1 > 0.85 on unseen data.

## Final Integration
1.  **End-to-End Test**: Run the full pipeline on a complete map sheet.
2.  **Documentation**: Finalize `research_paper.md`.
