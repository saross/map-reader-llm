# Map Reader LLM Walkthrough

This project automates the extraction of burial mounds from Soviet 1:50k maps using Gemini.

## 1. Setup
### Dependencies
All dependencies are in `requirements.txt`.
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configuration
- Add your `GOOGLE_API_KEY` to `.env`.
- Images go in `inputs/`.
- `config.py` controls tile sizing.

## 2. Using the Pipeline

### Step 1: Tiling
Cuts the large map into 512x512 tiles with geospatial metadata (World Files & Aux XML).
```bash
python scripts/preprocess_tiling.py
```
*Output: `outputs/tiles/<map_name>/*.{png,pgw,png.aux.xml}`*

### Step 2: Inference (Gemini)
Runs the LLM over every tile to find mounds.
```bash
python scripts/2_detect_mounds.py
```
*Output: `outputs/all_detections.geojson` (GeoJSON with EPSG:32635)*

### Step 3: Post-processing
Deduplicates overlapping detections from the GeoJSON.
```bash
python scripts/3_georeference_and_visualize.py
```
*Output: `outputs/results/mounds-YYYY-MM-DD-Model.geojson` (Deduplicated points)*

## 3. Results Verification
- **Test Mode**: `scripts/test_gemini_inference.py` runs 5 random tiles.
- **GeoJSON**: `scripts/convert_to_geojson.py` converts the test output for quick viewing.
