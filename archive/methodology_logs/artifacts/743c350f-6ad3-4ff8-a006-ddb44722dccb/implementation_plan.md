# Documentation Plan

## Goal Description
The objective is to fully document the `map-reader-llm` repository to make it accessible for both humans and LLMs. The focus will be on the three active pipelines: v3.2, v3.5, and v4.1/4.2 + v4.6 (Two Stage). This involves updating existing READMEs, creating new guides for architecture and usage, and ensuring FAIR4RS compliance.

## User Review Required
> [!IMPORTANT]
> **Pipeline Confirmation**: I am assuming "v4.5 two stage" refers to the `v4.6_verifier.json` configuration or a recently modified version of it, as I found `v4.6_verifier.json` but no explicit `v4.5` config file. Please confirm if `v4.5` exists elsewhere or if `v4.6` is the intended verifier.

## Proposed Changes

### Documentation Structure
I will restructure the documentation to be more modular and comprehensive.

#### [MODIFY] [README.md](file:///home/shawn/Code/map-reader-llm/README.md)
- Update the **Overview** to reflect the current state (removing "experimental" where appropriate if stable).
- Add a **Quick Start** section for the most common use case (e.g., v3.5).
- Add a **Active Pipelines** section briefly describing v3.2, v3.5, and the Two-Stage approach.
- Update **Setup & Usage** to be more robust.

#### [NEW] [docs/ARCHITECTURE.md](file:///home/shawn/Code/map-reader-llm/docs/ARCHITECTURE.md)
- **High-Level Flow**: Tiling -> Detection -> Verification -> Analysis.
- **Data Flow Diagram** (Mermaid).
- **Component Description**:
    - **Tiling**: `preprocess_tiling.py`
    - **Inference**: `4_detect_mounds_batch.py`
    - **Verification**: `5_verify_crops.py`
    - **Analysis**: `7_analyze...` scripts.

#### [NEW] [docs/USER_GUIDE.md](file:///home/shawn/Code/map-reader-llm/docs/USER_GUIDE.md)
- **Detailed Script Usage**: Flags and arguments for key scripts.
- **Prompt Engineering**: How to use `prompts/versions/`.
- **Manifests**: Explanation of `inputs/manifests/`.

#### [NEW] [docs/PIPELINES.md](file:///home/shawn/Code/map-reader-llm/docs/PIPELINES.md)
- **v3.2**: Description of the "Standard" or legacy experimental pipeline.
- **v3.5**: The "Clean" pipeline (Image-only? Pro?).
- **v4.1/4.2 + v4.6 (Two Stage)**:
    - Stage 1: High recall (v4.1/v4.2).
    - Stage 2: Verification (v4.6/v4.5).
    - Explanation of why this split exists (Recall vs Precision).

### Code & Metadata
#### [MODIFY] [CITATION.cff](file:///home/shawn/Code/map-reader-llm/CITATION.cff)
- Ensure all fields are filled and accurate.

#### [MODIFY] [LICENSE](file:///home/shawn/Code/map-reader-llm/LICENSE)
- Confirm Apache 2.0 is correctly applied.

#### [MODIFY] [Scripts](file:///home/shawn/Code/map-reader-llm/scripts/)
- Add/Update docstrings to `4_detect_mounds_batch.py`, `5_verify_crops.py`, and `benchmark_variability.py` to ensure automated tools (like LLMs) can understand them.

## Verification Plan

### Automated Verification
- **Link Checking**: I will verify that all internal links in the new markdown files work.
- **Command Testing**: I will dry-run the example commands provided in `README.md` and `USER_GUIDE.md` (using `--help` or small sample data if available) to ensure they are valid.

### Manual Verification
- **User Review**: You will review the generated markdown files for accuracy, especially the pipeline descriptions.
