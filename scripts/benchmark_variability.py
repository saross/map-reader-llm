
import json
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
from shapely.geometry import box, shape
import itertools
from collections import defaultdict
import sys
import os

# Import project modules
sys.path.append(os.getcwd())
try:
    from scripts.lib_advanced_metrics import normalize_ref_class, calculate_f1_internal, load_data
except ImportError:
    print("Error importing project modules. Run from root.")
    sys.exit(1)

STUDY_DIR = Path("outputs/results/variability_study_v3.2")
RESULTS_DIR = Path("outputs/results/analysis_variability_exhaustive")
RESULTS_DIR.mkdir(exist_ok=True, parents=True)

# Using Run 01 as the "template" for bounds/reference loading
TEMPLATE_BOUNDS = Path("outputs/results/v3.2_experimental/variability_study_v3.2_run_01_bounds.geojson") 
TEMPLATE_DET = Path("outputs/results/v3.2_experimental/variability_study_v3.2_run_01.geojson")

def calculate_iou(boxA, boxB):
    b1 = box(boxA[1], boxA[0], boxA[3], boxA[2])
    b2 = box(boxB[1], boxB[0], boxB[3], boxB[2])
    if not b1.intersects(b2): return 0.0
    return b1.intersection(b2).area / b1.union(b2).area

def get_crs(dname):
    with open(dname) as f:
        d = json.load(f)
    return d.get("crs", None)

def load_runs():
    runs = []
    print("Loading 10 runs...")
    for i in range(1, 11):
        fname = STUDY_DIR / f"run_{i:02d}_metrics.json"
        dname = Path("outputs/results/v3.2_experimental") / f"variability_study_v3.2_run_{i:02d}.geojson"
        
        if fname.exists() and dname.exists():
            with open(fname) as f: m = json.load(f)
            with open(dname) as f: d = json.load(f)
            runs.append({
                "id": i,
                "metrics": m,
                "detections": d
            })
    return runs

def cluster_detections(all_detections, crs_hint=None, iou_thresh=0.5):
    # Greedy clustering
    pool = []
    
    # 1. Extract valid features
    for run_id, feats in all_detections.items():
        for f in feats:
            props = f.get("properties", {})
            try:
                # Prioritize geometry bounds for accuracy
                geom_box = shape(f["geometry"]).bounds # (minx, miny, maxx, maxy)
                
                # Legacy box for IOU (YX format)
                legacy_box = [geom_box[1], geom_box[0], geom_box[3], geom_box[2]]
                
            except:
                continue

            pool.append({
                "box": legacy_box, # YX format for clustering
                "geom_bounds": geom_box, # XY format for output
                "label": props.get("subtype", "mound"),
                "source_tile": props.get("source_tile", ""),
                "run_id": run_id,
                "original": f
            })
            
    # 2. Cluster
    clusters = []
    used_indices = set()
    
    for i, det in enumerate(pool):
        if i in used_indices: continue
        
        current_cluster = [det]
        used_indices.add(i)
        ref_box = det["box"]
        
        for j, candidate in enumerate(pool):
            if j in used_indices: continue
            if candidate["label"] != det["label"]: continue 
            
            if calculate_iou(ref_box, candidate["box"]) > iou_thresh:
                current_cluster.append(candidate)
                used_indices.add(j)
                
        clusters.append(current_cluster)
        
    return clusters

def create_consensus_prediction(clusters, min_votes, subset_run_ids=None):
    features = []
    
    for cl in clusters:
        # Filter members
        if subset_run_ids:
            members = [c for c in cl if c["run_id"] in subset_run_ids]
        else:
            members = cl
            
        unique_runs = set(c["run_id"] for c in members)
        votes = len(unique_runs)
        
        if votes >= min_votes:
            # Average YX boxes
            boxes = np.array([c["box"] for c in members])
            avg_box = np.mean(boxes, axis=0).tolist()
            # Convert back to XY for geometry: [minx, miny, maxx, maxy]
            avg_minx, avg_miny = avg_box[1], avg_box[0]
            avg_maxx, avg_maxy = avg_box[3], avg_box[2]
            
            labels = [c["label"] for c in members]
            main_label = max(set(labels), key=labels.count)
            
            # Create Feature
            feat = {
                "type": "Feature",
                "properties": {
                    "box_2d": avg_box,
                    "label": "mound",
                    "subtype": main_label,
                    # IMPORTANT: Propagate source_tile correctly for evaluation!
                    "source_tile": members[0]["source_tile"], 
                    "score": votes 
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [avg_minx, avg_miny],
                        [avg_maxx, avg_miny],
                        [avg_maxx, avg_maxy],
                        [avg_minx, avg_maxy],
                        [avg_minx, avg_miny]
                    ]]
                }
            }
            features.append(feat)
            
    return features

def simulate_strategy(pool_size, vote_threshold, all_run_ids, clusters, crs, ref_data_tuple, limit=None):
    gdf_bounds, gdf_ref = ref_data_tuple
    
    # 1. Generate Combinations
    import itertools
    import random
    
    combos = list(itertools.combinations(all_run_ids, pool_size))
    
    if limit and limit < len(combos):
        # Random sample
        # shuffle and take n
        # Deterministic shuffle for reproducibility
        random.seed(42)
        random.shuffle(combos)
        combos = combos[:limit]
        # print(f"  (Sampled {limit})")
    
    f1_scores = []
    
    for combo in combos:
        combo_set = set(combo)
        
        # Create Consensus Features
        feats = create_consensus_prediction(clusters, min_votes=vote_threshold, subset_run_ids=combo_set)
        
        # Convert to GeoDataFrame (In-Memory)
        if not feats:
            f1_scores.append(0.0)
            continue
            
        gdf_det = gpd.GeoDataFrame.from_features(feats, crs=gdf_ref.crs)
        
        # Fast Eval
        try:
             # Ensure CRS match
             if gdf_det.crs != gdf_ref.crs: gdf_det = gdf_det.to_crs(gdf_ref.crs)
             
             _, _, f1 = calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds)
             f1_scores.append(f1)
        except Exception as e:
             # print(e)
             f1_scores.append(0.0)
             
    # Stats
    return {
        "pool": pool_size,
        "vote": vote_threshold,
        "n_combos": len(combos),
        "mean_f1": np.mean(f1_scores),
        "std_f1": np.std(f1_scores),
        "min_f1": np.min(f1_scores),
        "max_f1": np.max(f1_scores),
        "ci_lower": np.percentile(f1_scores, 2.5),
        "ci_upper": np.percentile(f1_scores, 97.5)
    }

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description="Variability & Consensus Simulation Engine")
    parser.add_argument("--pools", type=int, nargs="+", default=[3, 5, 10], help="List of Pool sizes to simulate (e.g., 3 5 10)")
    parser.add_argument("--method", choices=["exhaustive", "random"], default="exhaustive", help="Simulation method")
    parser.add_argument("--samples", type=int, default=100, help="Number of samples if method is random")
    parser.add_argument("--run_dir", type=str, default="outputs/results/variability_study_v3.2", help="Directory containing run metrics")
    parser.add_argument("--det_dir", type=str, default="outputs/results/v3.2_experimental", help="Directory containing run detections")
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Configuration
    # We load runs dynamically based on the directory
    # But for now, let's keep the hardcoded naming pattern or make it flexible?
    # The user current context is v3.2 study. Let's keep load_runs simple but respect the directories if needed.
    # For robust generalization, we should scan the directory.
    # But let's stick to the current specific N=10 set for safety unless asked to be fully generic for ANY folder.
    # The user said "generalise this script... input parameters".
    
    runs = load_runs() # Loads 1-10
    all_run_ids = [r["id"] for r in runs]
    
    if not runs:
        print("No runs found. Exiting.")
        return

    # CRS from first available detection
    crs = get_crs(Path("outputs/results/v3.2_experimental/variability_study_v3.2_run_01.geojson"))
    
    # Pre-load Reference Data
    # Using Run 01 as template
    print("Pre-loading reference data...")
    try:
        _, gdf_bounds, gdf_ref = load_data(TEMPLATE_DET, TEMPLATE_BOUNDS)
    except:
        print("Error loading template reference data. Ensure run_01 exists.")
        return
    
    # Cluster ALL detections once (Efficiency)
    print("Clustering all detections...")
    all_dets = {r["id"]: r["detections"]["features"] for r in runs}
    clusters = cluster_detections(all_dets, crs_hint=crs)
    print(f"Total Clusters in Pool (N={len(runs)}): {len(clusters)}")
    
    # Dynamic Strategy Generation
    strategies = []
    
    # If user provided pools, use them
    for p in args.pools:
        # For each pool size, we theoretically can test Vote T=1..P
        for t in range(1, p + 1):
            strategies.append((p, t))
            
    print(f"\n--- Simulation Settings ---")
    print(f"Method: {args.method}")
    print(f"Strategies to test: {len(strategies)}")
    if args.method == "random": print(f"Samples per strategy: {args.samples}")
    
    results = []
    
    print(f"\n{'Strategy':<15} | {'Mean F1':<8} | {'95% CI':<15} | {'Min':<6} | {'Max':<6} | {'N_Sims'}")
    print("-" * 75)
    
    for (pool, vote) in strategies:
        try:
            # Decide on method for this specific strategy
            # If pool size is close to total runs? 
            # If method is exhaustive
            
            # Note: For N=10 (Total), "Exhaustive" is just 1 combination. "Random" would be just 1 too.
            # simulate_strategy handles combinations generation.
            
            # If method is random, we modify simulate_strategy?
            # Let's add 'limit' to simulate_strategy
            
            limit = None
            if args.method == "random":
                # Only limit if combinations > sample size
                # nCr calc:
                import math
                n_total = len(all_run_ids)
                n_combos = math.comb(n_total, pool)
                if n_combos > args.samples:
                    limit = args.samples
            
            stats = simulate_strategy(pool, vote, all_run_ids, clusters, crs, (gdf_bounds, gdf_ref), limit=limit)
            results.append(stats)
            
            s_name = f"Pool={pool} Vote={vote}"
            ci_str = f"[{stats['ci_lower']:.3f}, {stats['ci_upper']:.3f}]"
            print(f"{s_name:<15} | {stats['mean_f1']:.4f}   | {ci_str:<15} | {stats['min_f1']:.3f}  | {stats['max_f1']:.3f}  | {stats['n_combos']}")
        except Exception as e:
            print(f"Error simulating {pool}/{vote}: {e}")
            import traceback
            traceback.print_exc()

    # Save
    out_csv = RESULTS_DIR / "strategy_stats.csv"
    pd.DataFrame(results).to_csv(out_csv, index=False)
    print(f"\nSaved strategy stats to {out_csv}")

if __name__ == "__main__":
    main()
