
"""
Mound Detection Variability & Consensus Analysis Engine
=====================================================

This script analyzes the statistical variability of mound detection models by simulating
various "n of x" consensus strategies (e.g., "Pool 10, Vote 4"). It calculates
F1 Score, Precision, and Recall for different strategies using either exhaustive
checks (for small pool sizes) or random sampling (for large pools/iterations).

The core idea is to simulate how the performance (F1 score) of a detection system
changes when detections from multiple individual runs are combined using a consensus
mechanism. This helps understand the robustness and variability of the models.

Usage:
------
To run the script, execute it from the project root directory.

1.  **Run on a standard N=10 Pro study (exhaustive method):**
    This will simulate all possible combinations for the specified pool sizes.
    ```bash
    python scripts/benchmark_variability.py --pools 3 5 10 --method exhaustive
    ```

2.  **Run on a large N=30 Flash study (random sampling method):**
    For larger numbers of runs or pool sizes, exhaustive simulation becomes
    computationally expensive. Use random sampling to estimate performance.
    ```bash
    python scripts/benchmark_variability.py \
        --pools 5 10 30 \
        --method random \
        --samples 1000 \
        --run_dir outputs/results/variability_study_v3.2_flash_30 \
        --det_dir outputs/results/v3.2_experimental
    ```

Arguments:
----------
--pools    : List of integer pool sizes to simulate (e.g., `3 5 10`).
             These represent 'x' in "n of x" consensus.
--method   : 'exhaustive' (simulates all combinations) or 'random' (uses Monte Carlo sampling).
             Defaults to 'exhaustive'.
--samples  : Number of random samples to take if `method` is 'random'.
             Defaults to 100.
--run_dir  : Directory containing the per-run metrics JSON files (e.g., `run_01_metrics.json`).
             Defaults to `outputs/results/variability_study_v3.2`.
--det_dir  : Directory containing the per-run GeoJSON detection files (e.g., `run_01.geojson`).
             Defaults to `outputs/results/v3.2_experimental`.

Metrics:
--------
The script outputs a table and a CSV file with the following statistics for each
simulated strategy (Pool size, Vote threshold):
- Mean F1 Score
- Standard Deviation of F1 Score
- 95% Confidence Intervals (2.5th to 97.5th percentile)
- Minimum F1 Score observed
- Maximum F1 Score observed
- Number of simulations performed for that strategy.

"""


import json
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
from shapely.geometry import box, shape
import itertools
import random
import math
import sys
import os
import argparse
import traceback

# Import project modules
sys.path.append(os.getcwd())
try:
    from scripts.lib_advanced_metrics import calculate_f1_internal, load_data, calculate_per_class_f1
except ImportError:
    print("Error importing scripts.lib_advanced_metrics. Ensure you are running from the project root.")
    sys.exit(1)

# Default paths (Fallbacks)
DEFAULT_RUN_DIR = Path("outputs/results/variability_study_v3.2")
DEFAULT_DET_DIR = Path("outputs/results/v3.2_experimental")
RESULTS_DIR = Path("outputs/results/analysis_variability_exhaustive")
RESULTS_DIR.mkdir(exist_ok=True, parents=True)

# Using Run 01 as the "template" for bounds/reference loading
# Ideally this should be dynamic, but for now we look for *any* valid run to get ground truth.
TEMPLATE_FILENAME_PATTERN = "variability_study_v3.2_run_01"

def calculate_iou(boxA, boxB):
    """
    Calculates Intersection over Union (IoU) between two bounding boxes.

    Args:
        boxA (list): A list representing the first bounding box in YX format
                     [ymin, xmin, ymax, xmax].
        boxB (list): A list representing the second bounding box in YX format
                     [ymin, xmin, ymax, xmax].

    Returns:
        float: The IoU value, ranging from 0.0 to 1.0. Returns 0.0 if boxes do not intersect.
    """
    b1 = box(boxA[1], boxA[0], boxA[3], boxA[2]) # Convert YX to XY for shapely: (minx, miny, maxx, maxy)
    b2 = box(boxB[1], boxB[0], boxB[3], boxB[2])
    if not b1.intersects(b2): return 0.0
    return b1.intersection(b2).area / b1.union(b2).area

def get_crs(dname):
    """
    Extracts the Coordinate Reference System (CRS) from a GeoJSON file.

    Args:
        dname (Path or str): The path to the GeoJSON file.

    Returns:
        dict or None: The CRS dictionary if found, otherwise None.
    """
    with open(dname) as f:
        d = json.load(f)
    return d.get("crs", None)

def load_runs(run_dir, det_dir):
    """
    Loads run data (metrics and detections) from the specified directories.
    Matches metric files (e.g., `run_X_metrics.json`) with detection files (e.g., `run_X.geojson`).
    Also loads `run_X_advanced_metrics.json` if available.

    Args:
        run_dir (Path or str): Directory containing the per-run metrics JSON files.
        det_dir (Path or str): Directory containing the per-run GeoJSON detection files.

    Returns:
        list: A list of dictionaries, where each dictionary represents a run
              and contains its 'id', 'metrics', 'advanced_metrics', and 'detections'.
    """
    runs = []
    run_dir_path = Path(run_dir)
    det_dir_path = Path(det_dir)
    
    if not run_dir_path.exists():
        print(f"Error: Run directory does not exist: {run_dir_path}")
        return []

    run_files = sorted(run_dir_path.glob("run_*_metrics.json"))
    print(f"Loading {len(run_files)} runs from {run_dir_path.name}...")
    
    for fname in run_files:
        # Skip advanced metrics files from being loaded as primary
        if "advanced" in fname.name:
            continue
            
        # Extract run ID (e.g. "run_01") from "run_01_metrics.json"
        run_name = fname.stem.replace("_metrics", "") 
        try:
            # 1. Strict Match Strategy: Try to match the exact study ID prefix first
            # e.g. "variability_study_v3.2_flash_30_run_01.geojson"
            study_name = run_dir_path.name
            strict_pattern = f"{study_name}_{run_name}.geojson"
            det_candidates = list(det_dir_path.glob(strict_pattern))
            
            # 2. Fallback to loose match: "variability_study_v3.2_run_01.geojson"
            if not det_candidates:
                # This handles cases where detections are in a generic folder
                det_candidates = list(det_dir_path.glob(f"*{run_name}.geojson"))
            
            if not det_candidates:
                print(f"Warning: No detection file found for {run_name} in {det_dir}")
                continue
            
            # Match found
            dname = det_candidates[0]
            
            with open(fname) as f: m = json.load(f)
            with open(dname) as f: d = json.load(f)
            
            # Try load advanced metrics
            adv_m = {}
            adv_fname = run_dir_path / f"{run_name}_advanced_metrics.json"
            if adv_fname.exists():
                with open(adv_fname) as f: adv_m = json.load(f)

            runs.append({
                "id": run_name,
                "metrics": m,
                "advanced_metrics": adv_m,
                "detections": d
            })
        except Exception as e:
            print(f"Error loading {run_name}: {e}")

    return runs

def cluster_detections(all_detections, iou_thresh=0.5):
    """
    Groups detections from ALL runs into clusters representing unique physical objects.
    Uses greedy clustering based on IoU > `iou_thresh`.

    Args:
        all_detections (dict): A dictionary where keys are run IDs (str) and values
                               are lists of GeoJSON feature dictionaries for detections.
        iou_thresh (float): The Intersection over Union threshold to consider two
                            detections as belonging to the same cluster.

    Returns:
        list: A list of clusters. Each cluster is a list of dictionaries, where each
              dictionary represents a detection with its 'box', 'geom_bounds', 'label',
              'source_tile', 'run_id', and 'original' GeoJSON feature.
    """
    pool = []
    
    # 1. Flatten all detections into a single pool
    for run_id, feats in all_detections.items():
        for f in feats:
            props = f.get("properties", {})
            try:
                # We prioritize geometry bounds for accuracy [minx, miny, maxx, maxy]
                geom_box = shape(f["geometry"]).bounds 
                # Legacy box for IOU (YX format: [ymin, xmin, ymax, xmax])
                legacy_box = [geom_box[1], geom_box[0], geom_box[3], geom_box[2]]
            except:
                # Skip detections with invalid geometry
                continue

            pool.append({
                "box": legacy_box, 
                "geom_bounds": geom_box,
                "label": props.get("subtype", "mound"),
                "source_tile": props.get("source_tile", ""), # Critical for per-tile evaluation
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
    """
    Generates a consensus FeatureCollection from clusters.
    A cluster becomes a prediction ONLY if it has members from >= `min_votes` distinct runs
    within the `subset_run_ids`. The bounding box of the consensus prediction is the
    average of its constituent detections' bounding boxes.

    Args:
        clusters (list): A list of detection clusters, as returned by `cluster_detections`.
        min_votes (int): The minimum number of distinct run votes required for a cluster
                         to be considered a consensus prediction.
        subset_run_ids (set, optional): A set of run IDs to consider for the current
                                        simulation. If None, all runs in the cluster
                                        are considered. Defaults to None.

    Returns:
        list: A list of GeoJSON feature dictionaries representing the consensus predictions.
    """
    features = []
    
    for cl in clusters:
        # Filter members to only those in the current simulation subset
        if subset_run_ids:
            members = [c for c in cl if c["run_id"] in subset_run_ids]
        else:
            members = cl
            
        unique_runs = set(c["run_id"] for c in members)
        votes = len(unique_runs)
        
        if votes >= min_votes:
            # Average the bounding boxes
            boxes = np.array([c["box"] for c in members])
            avg_box = np.mean(boxes, axis=0).tolist()
            # Convert YX back to XY for geometry: [minx, miny, maxx, maxy]
            avg_minx, avg_miny = avg_box[1], avg_box[0]
            avg_maxx, avg_maxy = avg_box[3], avg_box[2]
            
            labels = [c["label"] for c in members]
            main_label = max(set(labels), key=labels.count)
            
            # Create GeoJSON Feature
            feat = {
                "type": "Feature",
                "properties": {
                    "box_2d": avg_box,
                    "label": "mound", # Assuming all clustered items are mounds
                    "subtype": main_label,
                    "source_tile": members[0]["source_tile"], # Take source tile from first member
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

def simulate_strategy(pool_size, vote_threshold, all_run_ids, clusters, ref_data_tuple, limit=None):
    """
    Simulates performance for a specific (Pool Size, Vote Threshold) consensus strategy.
    
    Args:
        pool_size (int): The number of runs to include in each combination (P in "P of V").
        vote_threshold (int): The minimum number of votes required for a detection to be
                              considered a consensus (V in "P of V").
        all_run_ids (list): A list of all available run IDs.
        clusters (list): Pre-clustered detections from all runs.
        ref_data_tuple (tuple): A tuple containing (gdf_bounds, gdf_ref) for F1 calculation.
        limit (int, optional): If set, randomly samples 'limit' combinations instead of
                               running exhaustively. Defaults to None.

    Returns:
        dict: A dictionary containing performance statistics for the simulated strategy,
              including mean F1, standard deviation, min/max F1, and confidence intervals.
    """
    gdf_bounds, gdf_ref = ref_data_tuple
    
    # 1. Generate Combinations
    combos = list(itertools.combinations(all_run_ids, pool_size))
    
    if limit and limit < len(combos):
        # Random sample for large N
        random.seed(42) # For reproducibility
        random.shuffle(combos)
        combos = combos[:limit]
    
    f1_scores = []
    per_class_scores = {} # "burial_mound": [f1, f1, ...], ...
    
    for combo in combos:
        combo_set = set(combo)
        
        # Create Consensus Features
        feats = create_consensus_prediction(clusters, min_votes=vote_threshold, subset_run_ids=combo_set)
        
        # Handle empty case (no consensus detections)
        if not feats:
            f1_scores.append(0.0)
            continue
            
        gdf_det = gpd.GeoDataFrame.from_features(feats, crs=gdf_ref.crs)
        
        # Calculate F1 Score
        try:
             # Ensure CRS match
             if gdf_det.crs != gdf_ref.crs: gdf_det = gdf_det.to_crs(gdf_ref.crs)
             
             _, _, f1 = calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds)
             f1_scores.append(f1)
             
             # Calculate Per-Class
             pc_res = calculate_per_class_f1(gdf_det, gdf_ref, gdf_bounds)
             for item in pc_res:
                 c_name = item["class"]
                 if c_name not in per_class_scores: per_class_scores[c_name] = []
                 per_class_scores[c_name].append(item["f1"])
                 
        except Exception as e:
             print(f"Warning: Error calculating F1 for combo {combo}: {e}")
             f1_scores.append(0.0) # Append 0.0 on error to avoid breaking simulation
             
    # Aggregate Per-Class
    per_class_aggregated = {}
    for c_name, scores in per_class_scores.items():
        if scores:
            per_class_aggregated[c_name] = {
                "mean_f1": np.mean(scores),
                "std_f1": np.std(scores)
            }
             
    # Return Stats
    return {
        "pool": pool_size,
        "vote": vote_threshold,
        "n_combos": len(combos),
        "mean_f1": np.mean(f1_scores),
        "std_f1": np.std(f1_scores),
        "min_f1": np.min(f1_scores),
        "max_f1": np.max(f1_scores),
        "ci_lower": np.percentile(f1_scores, 2.5),
        "ci_upper": np.percentile(f1_scores, 97.5),
        "per_class": per_class_aggregated
    }


def analyze_base_variability(runs, output_dir):
    """
    Analyzes and saves statistics for the base model (N=1) performance.
    Breakdown by Overall and Per-Class.
    """
    print("\n=== Base Model Variability (N=1) ===")
    
    # 1. Overall Metrics
    print("\n--- Overall Performance ---")
    base_metrics = [r["metrics"] for r in runs]
    df_base = pd.DataFrame(base_metrics)
    
    cols = ['precision', 'recall', 'f1']
    if all(c in df_base.columns for c in cols):
        stats = df_base[cols].describe()
        print(stats)
        stats.to_csv(output_dir / "base_variability_stats.csv")
    else:
        print("Warning: Metrics keys missing. Skipping base analysis.")

    # 2. Per-Class Metrics
    print("\n--- Per-Class Performance ---")
    
    class_data = {} # class_name -> list of dicts (precision, recall, f1)
    
    for r in runs:
        adv = r.get("advanced_metrics", {})
        per_class = adv.get("per_class_performance", [])
        
        for item in per_class:
            c_name = item["class"]
            if c_name not in class_data:
                class_data[c_name] = []
            
            class_data[c_name].append({
                "precision": item.get("precision", 0.0),
                "recall": item.get("recall", 0.0),
                "f1": item.get("f1", 0.0)
            })
            
    if class_data:
        class_summary = []
        for c_name, data_list in class_data.items():
            df_c = pd.DataFrame(data_list)
            stats_c = df_c.describe()
            
            mean_f1 = stats_c.loc['mean', 'f1']
            std_f1 = stats_c.loc['std', 'f1']
            mean_p = stats_c.loc['mean', 'precision']
            mean_r = stats_c.loc['mean', 'recall']
            
            print(f"\nClass: {c_name:<20} | F1: {mean_f1:.4f} ± {std_f1:.4f}")
            
            class_summary.append({
                "class": c_name,
                "mean_f1": mean_f1,
                "std_f1": std_f1,
                "mean_precision": mean_p,
                "mean_recall": mean_r
            })
            
        # Save Per Class Summary
        pd.DataFrame(class_summary).to_csv(output_dir / "base_variability_by_class.csv", index=False)
        print(f"\nPer-class stats saved to {output_dir / 'base_variability_by_class.csv'}")
    else:
        print("No per-class data found in advanced metrics.")


def generate_markdown_report(output_dir, strategy_results):
    """
    Generates a human-readable Markdown report from the calculated statistics.
    """
    import datetime
    
    report_path = output_dir / "variability_report.md"
    
    with open(report_path, "w") as f:
        f.write(f"# Mound Detection Variability Report\n")
        f.write(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 1. Base Variability (Read from CSV)
        f.write("## 1. Base Model Variability (N=1)\n")
        f.write("_Performance stability of a single run, averaged across all iterations._\n\n")
        
        base_csv = output_dir / "base_variability_stats.csv"
        if base_csv.exists():
            df = pd.read_csv(base_csv, index_col=0)
            f.write("| Metric | Mean | Std Dev | Min | Max |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- |\n")
            
            for metric in ['f1', 'precision', 'recall']:
                if metric in df.columns:
                    mean = df.loc['mean', metric]
                    std = df.loc['std', metric]
                    min_v = df.loc['min', metric]
                    max_v = df.loc['max', metric]
                    name = metric.capitalize() if metric != 'f1' else "F1 Score"
                    f.write(f"| **{name}** | {mean:.4f} | ±{std:.4f} | {min_v:.4f} | {max_v:.4f} |\n")
            f.write("\n")
        else:
            f.write("> Base variability stats not found.\n\n")

        # 2. Per-Class Variability
        class_csv = output_dir / "base_variability_by_class.csv"
        if class_csv.exists():
            f.write("### Per-Class Breakdown (N=1)\n")
            df_c = pd.read_csv(class_csv)
            f.write("| Symbol Class | F1 Score | Precision | Recall |\n")
            f.write("| :--- | :--- | :--- | :--- |\n")
            
            for _, row in df_c.iterrows():
                f.write(f"| **{row['class']}** | {row['mean_f1']:.4f} (±{row['std_f1']:.2f}) | {row['mean_precision']:.4f} | {row['mean_recall']:.4f} |\n")
            f.write("\n")

        # 3. Strategy Analysis
        f.write("## 2. Consensus Strategy Analysis ('n of x')\n")
        f.write("_Simulation of voting strategies to improve stability and performance._\n\n")
        
        if strategy_results:
            f.write("| Strategy (N/Votes) | Mean F1 | 95% CI | Min | Max |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- |\n")
            
            # Sort by F1 descending
            sorted_res = sorted(strategy_results, key=lambda x: x['mean_f1'], reverse=True)
            
            for res in sorted_res:
                pool = res['pool']
                vote = res['vote']
                ci = f"[{res['ci_lower']:.3f}, {res['ci_upper']:.3f}]"
                
                # Highlight "Super-Majority" vs "Plurality" roughly
                # format: Pool=30 Vote=10
                name = f"**{pool}/{vote}**"
                if res == sorted_res[0]: name += " 🏆"
                
                f.write(f"| {name} | **{res['mean_f1']:.4f}** | {ci} | {res['min_f1']:.3f} | {res['max_f1']:.3f} |\n")
            f.write("\n")

            # 4. Per-Class Consensus (New)
            f.write("### Per-Class Consensus Breakdown\n")
            f.write("_Impact of consensus strategies on specific symbol types._\n\n")
            
            for res in sorted_res:
                 pool = res['pool']
                 vote = res['vote']
                 pc = res.get('per_class', {})
                 
                 if pc:
                     f.write(f"#### Strategy: {pool}/{vote}\n")
                     f.write("| Symbol | Mean F1 | Std Dev |\n")
                     f.write("| :--- | :--- | :--- |\n")
                     for c_name, scores in pc.items():
                         f.write(f"| {c_name} | {scores['mean_f1']:.4f} | ±{scores['std_f1']:.4f} |\n")
                     f.write("\n")

        else:
            f.write("> No strategy results available.\n")
            
    print(f"\nReport generated: {report_path}")

def parse_args():
    parser = argparse.ArgumentParser(description="Variability & Consensus Simulation Engine")
    parser.add_argument("--pools", type=int, nargs="+", default=[3, 5, 10], help="List of Pool sizes to simulate (e.g., 3 5 10)")
    parser.add_argument("--method", choices=["exhaustive", "random"], default="exhaustive", help="Simulation method ('exhaustive' or 'random')")
    parser.add_argument("--samples", type=int, default=100, help="Number of random samples to take if method is 'random'")
    parser.add_argument("--run_dir", type=str, default=str(DEFAULT_RUN_DIR), help="Directory containing run metrics JSON files")
    parser.add_argument("--det_dir", type=str, default=str(DEFAULT_DET_DIR), help="Directory containing run GeoJSON detection files")
    return parser.parse_args()

def main():
    """
    Main function to orchestrate the variability and consensus simulation.
    It loads data, clusters detections, simulates various consensus strategies,
    and reports the performance statistics.
    """
    args = parse_args()
    
    print(f"=== Mound Detection Variability Benchmark Tool ===")
    print(f"Reading Runs from: {args.run_dir}")
    print(f"Reading Detections from: {args.det_dir}")
    
    # 1. Load Runs
    runs = load_runs(args.run_dir, args.det_dir)
    all_run_ids = [r["id"] for r in runs]
    
    if not runs:
        print("No runs found. Exiting.")
        return

    # 2. Get CRS and Reference Data
    # Use first valid detection file to determine CRS and as a template for load_data
    try:
        # Attempt to find a specific detection file based on run_dir name and first run ID
        sample_det_file = Path(args.det_dir) / f"{Path(args.run_dir).name}_{runs[0]['id']}.geojson"
        # If strict match fails, try a more generic approach (any geojson in det_dir)
        if not sample_det_file.exists():
             geojson_files = list(Path(args.det_dir).glob("*.geojson"))
             if not geojson_files:
                 raise FileNotFoundError(f"No GeoJSON files found in {args.det_dir} to determine CRS or template.")
             sample_det_file = geojson_files[0]
        
        crs = get_crs(sample_det_file)
        
        # Load Reference Data (Ground Truth)
        # The benchmark wrapper creates bounds files.
        # Find the bounds file associated with the template detection
        template_bounds_candidates = list(Path(args.det_dir).glob(f"*{TEMPLATE_FILENAME_PATTERN}*bounds.geojson"))
        if not template_bounds_candidates:
            # Fallback to any bounds file if specific template not found
            template_bounds_candidates = list(Path(args.det_dir).glob("*bounds.geojson"))
        
        if not template_bounds_candidates:
            raise FileNotFoundError(f"No bounds.geojson file found in {args.det_dir} for reference data.")
        
        template_bounds = template_bounds_candidates[0]
        
        # Use the sample_det_file as the template for detections for load_data
        template_det = sample_det_file
        
        print(f"Pre-loading reference data (Template Bounds: {template_bounds.name})...")
        _, gdf_bounds, gdf_ref = load_data(template_det, template_bounds)
        
    except Exception as e:
        print(f"Error initializing reference data: {e}")
        traceback.print_exc()
        return
    
    # 3. Cluster ALL detections once (Efficiency)
    print("Clustering all detections...")
    all_dets = {r["id"]: r["detections"]["features"] for r in runs}
    clusters = cluster_detections(all_dets, iou_thresh=0.5)
    print(f"Total Clusters in Pool (N={len(runs)}): {len(clusters)}")
    
    # 4. Base Variability Analysis
    analyze_base_variability(runs, RESULTS_DIR)

    # 5. Define Strategies
    strategies = []
    for p in args.pools:
        # Check if we have enough runs for this pool size
        if p > len(runs):
            print(f"Skipping Pool={p} (Not enough runs available: {len(runs)})")
            continue
        # Test Vote T=1..P (from 1 vote up to the pool size)
        for t in range(1, p + 1):
            strategies.append((p, t))
            
    print(f"\n--- Simulation Settings ---")
    print(f"Method: {args.method}")
    print(f"Strategies to test: {len(strategies)}")
    if args.method == "random": print(f"Samples per strategy: {args.samples}")
    
    results = []
    print(f"\n{'Strategy':<15} | {'Mean F1':<8} | {'95% CI':<15} | {'Min':<6} | {'Max':<6} | {'N_Sims'}")
    print("-" * 75)
    
    # 6. Execute Simulation
    for (pool, vote) in strategies:
        try:
            # Determine limit for Random Sampling
            limit = None
            if args.method == "random":
                n_total = len(all_run_ids)
                n_combos = math.comb(n_total, pool)
                if n_combos > args.samples:
                    limit = args.samples
            
            stats = simulate_strategy(pool, vote, all_run_ids, clusters, (gdf_bounds, gdf_ref), limit=limit)
            results.append(stats)
            
            s_name = f"Pool={pool} Vote={vote}"
            ci_str = f"[{stats['ci_lower']:.3f}, {stats['ci_upper']:.3f}]"
            print(f"{s_name:<15} | {stats['mean_f1']:.4f}   | {ci_str:<15} | {stats['min_f1']:.3f}  | {stats['max_f1']:.3f}  | {stats['n_combos']}")
        except Exception as e:
            print(f"Error simulating {pool}/{vote}: {e}")
            traceback.print_exc()

    # 7. Save Results
    out_csv = RESULTS_DIR / "strategy_stats.csv"
    pd.DataFrame(results).to_csv(out_csv, index=False)
    print(f"\nSaved strategy stats to {out_csv}")
    
    # 8. Generate Report
    generate_markdown_report(RESULTS_DIR, results)

if __name__ == "__main__":
    main()
