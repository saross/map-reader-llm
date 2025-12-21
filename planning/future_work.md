# Future Work & Maintenance

This document tracks long-term maintenance and methodological tasks for the Map Reader LLM project.

## Methodological Records
- [x] **Log Retention Strategy**: `~/.gemini/antigravity/` logs are not purged effectively, but should be treated as research data.
    - Action: Review logs in `conversations/` and artifacts in `brain/`.
    - Action: Set up a cron job or script to copy relevant `*.pb` and `*.md` files into a dedicated `methodology/logs/` directory in this repository.

## Open Science Standards
- [x] **FAIR4RS Compliance**: Upgrade the repository to fully meet FAIR (Findable, Accessible, Interoperable, Reusable) principles for Research Software.
    - [x] Add `CITATION.cff`
    - [x] Ensure comprehensive license coverage
    - [x] Improve documentation for reusability (containerization, etc.)

## Planned Experiments & Optimizations
- [ ] **Diagnose v3.2 Swarm Failure**: Investigate why `v3.5` (Image-Only) collapsed in the N=30 "Swarm" setting compared to the success of `v3.2` (Text + Image).
    - Double-check all parameters (Temperature, Recalls, etc.) to rule out configuration error.
    - Test hypothesis: Does image-only reasoning require a stronger model (Pro) to maintain coherence without text rails?
- [ ] **Optimize Top 3 Approaches**: Systematically optimize the three most promising architecture candidates:
    1.  **v3.2 (Text + Image)**: The "Elaborate" Baseline (Proven Swarm Success).
    2.  **v3.5 (Image-Only)**: The "Clean" Baseline (Visual-First).
    3.  **v4.x (Two-Stage)**: The Pipeline approach (Recall Proposer + Verifier).
- [ ] **Holdout Benchmarking**: Run all three optimized approaches on the **Holdout Test Set** (20 unseen tiles) to measure true generalization.
- [ ] **Data Scaling**: Analyze whether the current training corpus (20 tiles) is sufficient for generalization.
    - Expand training and test sets if variance remains high or generalization is poor.
- [ ] **Automated Prompt Engineering**: Develop a pipeline to generate image-based prompts from first principles (Map Image + Legend Crop -> Prompt) without human manual tuning.
