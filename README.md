# Map Reader LLM: Archaeological Feature Extraction

**Automated Pipeline for Extracting Burial Mounds from Soviet Topographic Maps using Multimodal LLMs.**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![DOI](https://img.shields.io/badge/DOI-Pending-orange.svg)](CITATION.cff)

**Authors**: Shawn Ross, Adela Sobotkova (Tundzha Regional Archaeology Project)  
**Funding**: Supported by the Australian Research Council (ARC) Linkage scheme, The America for Bulgaria Foundation, UNSW, University of Michigan, and Macquarie University.

---

## 🚀 Overview

Map Reader LLM is a modular, FAIR4RS-compliant pipeline designed to identify archaeological feature symbols (specifically "Burial Mounds" or *Tumuli*) on historical maps. It leverages **Google Gemini 3 Flash** (Multimodal LLM) to visually scan map tiles and extract features as geospatial data.

### Key Capabilities
*   **Visual Few-Shot Learning**: Does not require fine-tuning. Uses a "Reference Library" of cropped symbols to teach the model what to look for at runtime.
*   **Geospatial Awareness**: Automatically preserves spatial reference systems (EPSG:32635) from input GeoTIFFs to output GeoJSONs.
*   **Reproducibility**: Features a rigorous configuration versioning system (`prompts/versions/*.json`) to ensure every experiment is traceable.
*   **Active Pipelines**: diverse strategies for detection, from high-speed single-stage (v3.5) to rigorous two-stage Recall+Verification (v4.1 + v4.6).

---

## 📚 Documentation

Detailed documentation is available in the `docs/` directory:

*   **[Pipelines Guide](docs/PIPELINES.md)**: Detailed breakdown of the active analysis pipelines (v3.2, v3.5, v4.1/4.6). **Start here to understand the methodology.**
*   **[User Guide](docs/USER_GUIDE.md)**: Step-by-step instructions for running scripts, configuring prompts, and managing data.
*   **[Architecture](docs/ARCHITECTURE.md)**: High-level system architecture, data flow diagrams, and component descriptions.

---

## ⚡ Quick Start

### 1. Installation
```bash
git clone https://github.com/saross/map-reader-llm.git
cd map-reader-llm
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root directory with your Google API Key:
```bash
GOOGLE_API_KEY=your_key_here
```

### 3. Run the "Clean" Pipeline (v3.5)
This is the recommended baseline for general detection (high speed, balanced accuracy).

**Step 1: Tile Input Maps**
Tiles maps located in `inputs/rasters/`.
```bash
python scripts/preprocess_tiling.py
```

**Step 2: Run Detection**
```bash
python scripts/4_detect_mounds_batch.py --config prompts/versions/v3.5_clean.json
```
Results will be saved to `outputs/results/v3.5_clean/`.

---

## 📂 Repository Structure

*   **`scripts/`**: Python source code.
    *   `preprocess_tiling.py`: Tiles large maps + generates World Files.
    *   `4_detect_mounds_batch.py`: Main Inference Engine (Stage 1).
    *   `5_verify_crops.py`: Verification Engine (Stage 2).
    *   `7_analyze_consensus.py`: Analysis & Scoring tools.
    *   `benchmark_variability.py`: Stability & Variability analysis.
*   **`prompts/`**: Configuration and System Instructions.
    *   `versions/`: **Active Pipeline Configs** (JSON).
    *   `text/`: Static system instruction text files.
*   **`inputs/`**: Analysis inputs.
    *   `rasters/`: Source GeoTIFF maps.
    *   `manifests/`: JSON lists defining tile sets for experiments.
    *   `references/`: The few-shot image library.
*   **`outputs/`**: Generated results, logs, and run metadata.
*   **`docs/`**: Project Documentation.

---

## Methodological Records (Open Science)
To ensure transparency, this project archives AI interaction logs (`conversations/*.pb`) and planning artifacts (`task.md`, `implementation_plan.md`).
To update the archive:
```bash
python scripts/archive_methodology.py
```

---

## License & Citation
*   **Code**: Apache 2.0 License
*   **Documentation**: CC-BY 4.0 International
*   **Citation**: Please refer to `CITATION.cff` for citing this software.
