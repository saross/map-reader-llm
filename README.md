# Map Reader LLM

**Map Reader LLM** is an automated pipeline for extracting archaeological features (specifically "Burial Mounds" or *Tumuli*) from historical Soviet 1:50,000 topographic maps using Multimodal Large Language Models (Google Gemini).

The system seamlessly handles large GeoTIFF maps by tiling them, running VLM inference, and re-assembling the results into geospatial data formats ready for GIS analysis.

## Features

- **Automated Tiling**: Splits massive GeoTIFFs into manageable 512x512 tiles while preserving spatial metadata (World Files & Aux XML).
- **VLM Inference**: Uses Google's Gemini models (e.g., Gemini 3 Pro, Flash) to visually identify symbols.
- **Geospatial Awareness**: Outputs valid GeoJSON with correct CRS (EPSG:32635) derived immediately from tile metadata.
- **Cost Control**: Built-in limits (`TEST_LIMIT`) to prevent runaway API costs during testing.
- **Post-Processing**: Deduplicates overlapping detections and exports final results to OGC GeoPackage (`.gpkg`).

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/saross/map-reader-llm.git
    cd map-reader-llm
    ```

2.  **Install Dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Environment Configuration:**
    Create a `.env` file in the root directory and add your Google Gemini API key:
    ```bash
    GOOGLE_API_KEY=your_api_key_here
    ```

## Usage

The pipeline consists of three sequential scripts located in `scripts/`.

### 1. Preprocessing (Tiling)
Splits source maps (`inputs/*.tif`) into tiles.
```bash
python scripts/preprocess_tiling.py
```
*Output*: `outputs/tiles/<map_name>/*.{png,pgw,png.aux.xml}`

### 2. Inference (Detection)
Runs the Gemini model on the tiles to detect mounds.
```bash
python scripts/2_detect_mounds.py
```
*Output*: `outputs/results/detections-YYYY-MM-DD-Model.geojson`

> **Note**: This script respects the `TEST_LIMIT` in `config.py`. Set it to `MO` (or Remove) to process all tiles.

### 3. Post-Processing
Deduplicates overlapping detections and creates a GIS-ready layer.
```bash
python scripts/3_georeference_and_visualize.py
```
*Output*: `outputs/results/mounds-YYYY-MM-DD-Model.gpkg`

## Configuration (`config.py`)

You can adjust the pipeline settings in `config.py`:

- **`MODEL_NAME`**: Switch between Gemini versions (e.g., `gemini-3-pro-preview`, `gemini-flash-latest`).
- **`TEST_LIMIT`**: Number of tiles to process (set to `5` for testing, or set to `0`/`None` for full runs).
- **`TILE_SIZE`** & **`OVERLAP`**: Adjust tiling parameters (default 512px / 64px overlap).

## Outputs

All results are saved in the `outputs/` directory:
- `outputs/tiles/`: Generated map tiles.
- `outputs/results/`: Final GeoJSON and GeoPackage files, timestamped for version control.
