# Task List: Mounds Detection Pipeline

## 1. Recall Proposer (Stage 1)
- [x] **Design v4.0 Proposer**: Remove all object negatives to maximize recall.
- [x] **Verify v4.0**: Run variability study (N=5). Result: R=0.83, P=0.53.
- [x] **Fix Analysis Tools**: Debug `analyze_fp_crops.py` to support False Negative mining.
- [x] **Mine Hard Positives**: Extract "False Negative" crops from v4.0 runs.
- [x] **Design v4.1 Augmented**: Create `v4.1_recall_augmented` with mined examples.
- [x] **Verify v4.1**: Run variability study (N=5). Result: **Max Recall 0.89**.
- [x] **Validate Generalization**: Run v4.1 on stratified Holdout Set (N=20). Result: **Mean Recall 0.81**, **Union Recall 0.92**.
- [x] **Optimize Temperature**: Test v4.2 (Temp 0.7) on Training Set. Result: **Union Recall 0.94**.
- [x] **Test Saturation**: Test v4.3 (Temp 1.0) to model Recall/Precision curve. Result: **Saturation at 0.94 Recall**. Precision collapses. Revert to 0.7.

## 2. Precision Verifier (Stage 2) - **IN PROGRESS**
- [x] **Design Verifier Prompt (v4.5)**: Create strict prompt with Hard Negatives (Objects) + Chain of Thought.
- [x] **Implement Verification Script**: Create `5_verify_crops.py` to process candidates and save results.
- [x] **Optimize Consensus Strategy**: Run "N of 5" Voting Consensus experiment. Result: **F1 0.75 (Lower)**. Decision: Revert to Single-Run Pipeline (F1 0.80).
    - [x] Merge Proposer Runs (Union).
    - [x] Run 5-pass Verification.
    - [x] Analyze Thresholds (1/5 to 5/5) to maximize F1.
- [x] **Analyze Proposer Consensus**: Test "Proposer 2-of-5" -> Verifier. Result: F1 0.75 (Inferior).
- [x] **Optimize Stage 2 Verifier (v4.6)**: Refine Two-Stage Pipeline (F1 0.87 achieved with Gemini 2).
    - [x] **Mine Examples**: Analyzed failures. Extracted 21 Hard Cases (13 FP, 8 FN).
    - [x] **Design v4.6 Prompt**: Text-Free, Image-First, Confidence-Calibrated (48-Shot).
    - [x] **Verify v4.6 (Gemini 2)**: F1 0.874.
    - [x] **Verify v4.6 (Gemini 3)**: F1 0.865. (Underperformed slightly).
    - [x] **Analyze & Compare**: Gemini 2.0 Wins. Proceeding to Holdout.
- [x] **Optimize Gemini 3 Flash (v4.7)**: Apply "Visual Scaffolding" (Grid Overlays).
    - [x] **Implement Grid**: Add 100m Cyan grid (20px spacing).
    - [x] **Verify v4.7**: F1 0.65. **FAIL**.
    - [x] **Compare**: Grid caused massive recall drop. Reverting to v4.6.
- [x] **Optimize Stage 2 Consensus (v4.8)**: "Self-Consistency" Voting stability.
    - [x] **Configure**: Set `iterations=3` (Majority Vote) for **Gemini 3 Flash** (v4.6 prompt).
    - [x] **Verify v4.8**: 0 Verified. **FAIL**.
    - [x] **Analyze**: High Temp Divergence caused total rejection.
    - [x] **Retry v4.8**: Re-run with `temperature=0.7`.
    - [x] **Analyze Retry**: Still 0 Verified. **FAIL**.
    - [x] **Final Decision**: Revert to Gemini 2.0 Flash (v4.6). Best F1 (0.874).
- [x] **Experiment v4.9: Outer-Loop Consensus**: Run N=1 Verifier 5 times and aggregate.
    - [x] **Configure**: Gemini 3 Flash, Temp 0.7, v4.6 Prompt (Text-Free).
    - [x] **Execute**: 5 Independent Runs.
    - [x] **Analyze**: Total Unique: 9. Max Votes: 3. **FAIL**.
    - [x] **Retry v4.9 (Low Temp)**: Re-run Outer Loop with **Temp 0.2**.
    - [x] **Analyze Retry**: Total Unique: 9. Identical Failure.
- [ ] **Overnight Experiment Suite** (Running in Background):
    - [x] **Setup**: Created `scripts/overnight_experiments.sh`.
    - [/] **Job A**: Gemini 3 Pro | v3.5 (Single Stage) | N=5.
    - [x] **Job B**: Gemini 3 Flash | v3.5 (Single Stage) | N=30 (Swarm) - **FAILED** (Temp 0.3 & 1.0).
    - [ ] **Job B Retry**: Replicate v3.2 Swarm (Text+Image). (Added to Future Work).
    - [ ] **Job C**: Gemini 3 Pro | v4.6 (Verifier) | N=1.
- [ ] **Validate on Holdout Set**: Run Final Consensus Configuration (Flash 2/5) on Holdout Data.
- [ ] **End-to-End Test**: Verify final pipeline Recall/Precision.
    - [ ] Input: Candidate crops from Stage 1 (Proposer).
    - [ ] Process: Run v5.0 inference on each crop.
    - [ ] Output: Filtered GeoJSON (High Precision).
- [ ] **Verify Pipeline**: Run full end-to-end test (Stage 1 -> Stage 2).

## 3. Documentation & Housekeeping
- [x] **Repository Cleanup**: Archived superseded Prompts, Scripts, and Results.
- [x] **Documentation Update**: Updated READMEs, Manifests, and Comments.
- [x] **Working Notes**: Document v4.0 and v4.1 results.
- [x] **Final Report (Observation 44)**: Summarize architecture decisions.
