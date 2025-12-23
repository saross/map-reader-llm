# User Guide

## 1. Adding New Maps
To run the pipeline on new survey data:

1.  **Place GeoTIFFs**: Copy your `.tif` files into `inputs/rasters/`.
    *   *Note: Ensure they are projected in EPSG:32635 (UTM Zone 35N) or a compatible metric system for best results.*
2.  **Run Tiling**:
    ```bash
    python scripts/preprocess_tiling.py
    ```
    This will generate a folder in `inputs/tiles/` for each map.

## 2. Running Detection (Standard)
1.  **Select a Configuration**: Choose a JSON file from `prompts/configs/`.
    *   Use `detect_image-only.json` for general purpose (recommended).
2.  **Define a Manifest (Optional)**: If you only want to run specific tiles, create a json list in `inputs/manifests/my_run.json`.
    *   Format: `["K-35-101-1_1_1", "K-35-101-1_1_2"]`
    *   If no manifest is provided, some scripts may process all available tiles or default to `training_manifest.json`.
3.  **Execute**:
    ```bash
    python scripts/4_detect_mounds_batch.py --config prompts/configs/detect_image-only.json
    ```

## 3. Running Verification (Two-Stage)
If you have a `candidates.geojson` from Stage 1:

```bash
python scripts/5_verify_crops.py \
  --candidates outputs/results/propose_image-only/candidates.geojson \
  --output outputs/results/propose_image-only/verified.geojson \
  --config prompts/configs/verify_image-only.json \
  --iterations 1 \
  --model gemini-2.5-pro
```
*   `--iterations`: Increase this (e.g., to 3 or 5) to use "Consensus Verification" (voting).
*   `--model`: Override the model defined in the JSON (e.g. use `gemini-2.5-pro` for harder cases).

## 4. Customising Prompts
To create your own experiment:
1.  **Duplicate a Config**: Copy `prompts/configs/detect_image-only.json` to a new file like `detect_image-only_experiment.json`.
2.  **Edit Examples**: Change the `"examples"` list to point to different images in `inputs/references/`.
3.  **Run with new Config**: The system automatically logs results under the config name (`outputs/results/detect_image-only_experiment/`).

## 5. View Results
*   **QGIS / ArcGIS**: Drag and drop the output `.geojson` files directly into your GIS software. They are fully georeferenced.
