# Map Reader LLM: Archaeological Feature Extraction

**Automated Pipeline for Extracting Burial Mounds from Soviet Topographic Maps using Multimodal LLMs.**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![DOI](https://img.shields.io/badge/DOI-Pending-orange.svg)](CITATION.cff)

**Authors**: Shawn Ross, Adela Sobotkova (Tundzha Regional Archaeology Project)  
**Funding**: Supported by the Australian Research Council (ARC) Linkage scheme, The America for Bulgaria Foundation, UNSW, University of Michigan, and Macquarie University.

---

## Overview

Map Reader LLM is a modular, FAIR4RS-compliant pipeline designed to identify archaeological feature symbols (specifically "Burial Mounds" or *Tumuli*) on historical maps. It leverages **Google Gemini 3 Pro** (Multimodal LLM) to visually scan map tiles and extract features as geospatial data.

### Key Capabilities
*   **Visual Few-Shot Learning**: Does not require fine-tuning. Uses a "Reference Library" of cropped symbols to teach the model what to look for at runtime.
*   **Geospatial Awareness**: Automatically preserves spatial reference systems (EPSG:32635) from input GeoTIFFs to output GeoJSONs.
*   **Reproducibility**: Features a rigorous configuration versioning system (`prompts/versions/*.json`) to ensure every experiment is traceable.

---

## Repository Structure

*   **`scripts/`**: The Python source code.
    *   `preprocess_tiling.py`: Tiles large maps + generates World Files.
    *   `4_detect_mounds_batch.py`: The V3 Inference Engine.
    *   `3_georeference_and_visualize.py`: Post-processing & deduplication.
*   **`prompts/`**: Configuration and System Instructions.
    *   `versions/`: JSON configs for specific experiments.
    *   `text/`: Static system instruction files.
*   **`inputs/`**: Analysis inputs.
    *   `rasters/`: Source GeoTIFFs.
    *   `vectors/`: Source Vector overlays.
    *   `tiles/`: Pre-processed png tiles.
    *   `references/`: Few-shot example images.
*   **`outputs/`**: Generated results vs metadata.
*   **`archive/`**: Legacy code and results from previous project phases.
*   **`methodology/`**: Open Science methodological records (Project Logs).

---

## Methodological Records (Open Science)
To ensure transparency, this project archives AI interaction logs (`conversations/*.pb`) and planning artifacts (`task.md`, `implementation_plan.md`).
To update the archive:
```bash
python scripts/archive_methodology.py
```


---

## Setup & Usage

### 1. Installation
```bash
git clone https://github.com/saross/map-reader-llm.git
cd map-reader-llm
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root:
```bash
GOOGLE_API_KEY=your_key_here
```

### 3. Running the Pipeline
**Step 1: Tiling**
To tile maps from `inputs/rasters/`:
```bash
python scripts/preprocess_tiling.py
```

**Step 2: Detection (Using V3.1 Baseline)**
```bash
python scripts/4_detect_mounds_batch.py --config prompts/versions/v3.1_baseline.json
```
*   *Note: This creates results in `outputs/results/v3.1_baseline/`*
*   *Note: Results include a `.meta.json` sidecar for full traceability.*

**Step 3: Post-Processing**
```bash
python scripts/3_georeference_and_visualize.py
```

---

## License & Citation
*   **Code**: Apache 2.0 License
*   **Documentation**: CC-BY 4.0 International
*   **Citation**: Please refer to `CITATION.cff` for citing this software.
