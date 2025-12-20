
import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
import time
import geojson
from geojson import FeatureCollection, Feature, Point
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union
import rasterio
from rasterio.windows import Window
import google.generativeai as genai
from PIL import Image
import concurrent.futures
from threading import Lock

# Setup Project Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

try:
    import config
except ImportError:
    print("Error: config.py not found.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global Lock for thread safety if needed (logging is thread-safe)
file_lock = Lock()

def load_candidates(candidates_path: Path) -> List[Feature]:
    """Loads candidate features from GeoJSON."""
    with open(candidates_path, 'r') as f:
        fc = geojson.load(f)
    return fc.get("features", [])

def get_tile_path(tile_id: str) -> Path:
    """Resolves tile ID to absolute path."""
    tiles_dir = config.TILES_DIR
    found = list(tiles_dir.glob(f"**/{tile_id}")) 
    if not found:
        found = list(tiles_dir.glob(f"**/{tile_id}.png"))
    
    if found:
        return found[0]
    return None

def crop_candidate(raster_path: Path, geom: Dict, context_px: int = 512) -> Image.Image:
    """Crops the raster around the candidate geometry."""
    with rasterio.open(raster_path) as src:
        bounds = shape(geom).bounds
        cx = (bounds[0] + bounds[2]) / 2
        cy = (bounds[1] + bounds[3]) / 2
        
        row, col = src.index(cx, cy)
        half_size = context_px // 2
        window = Window(col - half_size, row - half_size, context_px, context_px)
        
        try:
            arr = src.read(window=window)
            if arr.shape[0] == 0: return None
            img_data = arr.transpose(1, 2, 0)
            return Image.fromarray(img_data)
        except Exception as e:
            return None

def construct_verifier_prompt(prompt_config: Dict, refs_dir: Path) -> List[Any]:
    """Constructs the Multimodal Prompt."""
    prompt_parts = []
    
    # 1. Image Library (Federated)
    for ex in prompt_config.get("examples", []):
        img_path = refs_dir / ex["path"]
        if img_path.exists():
            img = Image.open(img_path)
            prompt_parts.append(f"Example: {ex['label']}")
            prompt_parts.append(img)
        else:
            logging.warning(f"Missing reference: {img_path}")

    # 2. Instructions 
    # v4.6 Optimization: Load from external file if specified
    instruction_file = prompt_config.get("instruction_file")
    if instruction_file:
        instr_path = Path("prompts") / instruction_file
        if instr_path.exists():
            with open(instr_path) as f:
                instructions = f.read()
            # logging.info(f"Loaded instructions from {instr_path}")
        else:
            logging.warning(f"Instruction file not found: {instr_path}. Using default.")
            instructions = None
    else:
        instructions = None

    if not instructions:
        # Fallback Default (v4.5 style)
        instructions = """
        **Task:** Verification.
        **Process:**
        1. **SCAN**: List visual features of the candidate object in the center.
        2. **DISCRIMINATE**: Check for Hard Negatives (Is it a Benchmark? Triangulation Point? Text?).
        3. **FACTORS**: List 3 specific factors that REDUCE your confidence.
        4. **SCORE**: Assign a Probability Score (0.0 to 1.0) that this is a BURIAL MOUND.
        
        **Rubric**:
        * 0.9-1.0: Clear, circular, 3D relief. Verified.
        * 0.6-0.8: Likely mound, fuzziness/intersection present.
        * 0.2-0.5: Ambiguous, random blob, or competing symbol.
        * 0.0-0.1: Rejection (Text, Box, Line).
        
        Output JSON: {"reasoning": "...", "mound_probability": 0.X}
        """
    
    prompt_parts.append(instructions)
    return prompt_parts

def process_single_candidate(args_tuple: Tuple) -> Feature:
    """Helper for parallel processing."""
    feat, base_prompt, model_name, iterations = args_tuple
    
    # Reload model inside thread/process? No, client is thread safe usually. But GenAI python client? 
    # Better to instantiate standard client.
    # Actually google.generativeai client is stateless rest wrapper.
    model = genai.GenerativeModel(model_name)
    
    props = feat.get("properties", {})
    tile_id = props.get("tile_id") or props.get("source_tile")
    
    if not tile_id:
        return None
        
    tile_path = get_tile_path(tile_id)
    if not tile_path:
        return None
        
    crop_img = crop_candidate(tile_path, feat["geometry"])
    if not crop_img:
        return None
        
    try:
        full_content = base_prompt + ["**Target Candidate:**", crop_img]
        
        iteration_results = []
        votes = 0
        total_score_sum = 0.0
        
        for _ in range(iterations):
            try:
                response = model.generate_content(full_content)
                txt = response.text.replace("```json", "").replace("```", "").strip()
                # print(f"DEBUG Response: {txt}") 
                result = json.loads(txt)
                
                score = result.get("mound_probability", 0.0)
                reason = result.get("reasoning", "")
                
                is_verified = score >= 0.5
                if is_verified: votes += 1
                total_score_sum += score
                
                iteration_results.append({
                    "score": score,
                    "reason": reason,
                    "verified": is_verified
                })
            except Exception as e:
                print(f"DEBUG Error: {e} | Raw: {response.text if 'response' in locals() else 'No response'}")
                continue

        if not iteration_results: return None
        
        # Aggregate
        feat["properties"]["verifier_results"] = iteration_results
        feat["properties"]["verifier_votes"] = votes
        feat["properties"]["verifier_avg_score"] = total_score_sum / len(iteration_results)
        feat["properties"]["iterations"] = iterations
        # Verified if Majority Vote
        feat["properties"]["verified"] = votes >= (iterations / 2)
        
        return feat
    except Exception as e:
        # logging.error(f"Inference failed: {e}")
        return None

def run_verification(candidates_path: str, output_path: str, config_path: str, workers: int = 5, iterations: int = 1):
    """Main loop with parallelism."""
    
    with open(config_path) as f:
        prompt_cfg = json.load(f)
    
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model_name = prompt_cfg.get("model", "gemini-1.5-flash")
    
    candidates = load_candidates(Path(candidates_path))
    logging.info(f"Loaded {len(candidates)} candidates. Concurrent Workers: {workers}. Iterations per candidate: {iterations}")
    
    refs_dir = config.REFERENCES_DIR
    base_prompt = construct_verifier_prompt(prompt_cfg, refs_dir)
    
    verified_features = []
    
    # Prepare args
    process_args = [(c, base_prompt, model_name, iterations) for c in candidates]
    
    completed = 0
    total = len(candidates)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_cand = {executor.submit(process_single_candidate, arg): arg for arg in process_args}
        
        for future in concurrent.futures.as_completed(future_to_cand):
            completed += 1
            if completed % 5 == 0:
                logging.info(f"Progress: {completed}/{total}")
                
            try:
                result = future.result()
                if result:
                    verified_features.append(result)
            except Exception as e:
                logging.error(f"Worker exception: {e}")
    
    logging.info(f"Saving {len(verified_features)} verified results to {output_path}")
    fc = FeatureCollection(verified_features)
    with open(output_path, 'w') as f:
        geojson.dump(fc, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--iterations", type=int, default=1)
    args = parser.parse_args()
    
    run_verification(args.candidates, args.output, args.config, args.workers, args.iterations)
