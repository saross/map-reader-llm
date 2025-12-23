
import json
import numpy as np
import pandas as pd
from pathlib import Path
from shapely.geometry import box, shape
import itertools
from collections import defaultdict
import sys
import os

# Import project modules
sys.path.append(os.getcwd())
try:
    from scripts.run_v3_1_benchmark import evaluate_performance, get_map_name
    from scripts.lib_advanced_metrics import normalize_ref_class
except ImportError:
    # Quick fix for import if needed
    sys.path.append(str(Path.cwd() / "scripts"))
    from run_v3_1_benchmark import evaluate_performance, get_map_name
    from lib_advanced_metrics import normalize_ref_class

STUDY_DIR = Path("outputs/results/variability_study_v3.2")
RESULTS_DIR = Path("outputs/results/analysis_variability")
RESULTS_DIR.mkdir(exist_ok=True, parents=True)

BOUNDS_FILE = Path("outputs/results/v3.2_experimental/variability_study_v3.2_run_01_bounds.geojson") # Bounds are same for all

def calculate_iou(boxA, boxB):
    # box: [ymin, xmin, ymax, xmax] - normalized? 
    # shapely expects (minx, miny, maxx, maxy)
    # Our box_2d is [ymin, xmin, ymax, xmax]
    
    # Convert to shapely
    # raw values are 0-1000 usually
    b1 = box(boxA[1], boxA[0], boxA[3], boxA[2])
    b2 = box(boxB[1], boxB[0], boxB[3], boxB[2])
    
    if not b1.intersects(b2):
        return 0.0
    return b1.intersection(b2).area / b1.union(b2).area

def load_runs():
    runs = []
    # Load Run 01 to Run 10
    for i in range(1, 11):
        fname = STUDY_DIR / f"run_{i:02d}_metrics.json"
        # Detections are in the Version directory
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

def get_crs(dname):
    # Extract CRS from a geojson file
    with open(dname) as f:
        d = json.load(f)
    return d.get("crs", None)

def cluster_detections(all_detections, iou_thresh=0.5):
    # Greedy clustering
    # Each detection: {box, label, run_id}
    # Result: List of Clusters. Each Cluster: List of detections.
    
    clusters = []
    
    # Flatten source
    pool = []
    for run_id, feats in all_detections.items():
        for f in feats:
            props = f.get("properties", {})
            # Use geometry bounds
            # shape(..).bounds -> (minx, miny, maxx, maxy)
            try:
                geom_box = shape(f["geometry"]).bounds
            except:
                continue

            pool.append({
                "box": geom_box,
                "label": props.get("subtype", "mound"), # Use subtype for clustering precision
                "source_tile": props.get("source_tile", ""),
                "run_id": run_id,
                "original": f
            })
    print(f"DEBUG: Pool size: {len(pool)}")
            
    # Greedy assign
    # Sort by nothing in particular? Or confidence? We don't have conf.
    # Just iterate.
    
    used_indices = set()
    
    for i, det in enumerate(pool):
        if i in used_indices: continue
        
        current_cluster = [det]
        used_indices.add(i)
        
        # Determine Reference Box for this cluster (the first one)
        ref_box = det["box"]
        
        # Check all others
        for j, candidate in enumerate(pool):
            if j in used_indices: continue
            
            # Label Match?
            if candidate["label"] != det["label"]: continue
            
            # IOU Match?
            if calculate_iou(ref_box, candidate["box"]) > iou_thresh:
                current_cluster.append(candidate)
                used_indices.add(j)
                
        clusters.append(current_cluster)
        
    return clusters

def create_consensus_prediction(clusters, min_votes):
    # Convert clusters to a GeoJSON format for evaluation
    # Averaging boxes (WBF ish)
    
    features = []
    
    for cl in clusters:
        unique_runs = set(c["run_id"] for c in cl)
        votes = len(unique_runs)
        
        if votes >= min_votes:
            # WBF: Average coordinates
            boxes = np.array([c["box"] for c in cl])
            avg_box = np.mean(boxes, axis=0).astype(int).tolist()
            
            # Take mode label
            labels = [c["label"] for c in cl]
            main_label = max(set(labels), key=labels.count)
            
            # Create Feature
            # We need to construct the GeoJSON feature structure expected by evaluate_performance
            # We need 'properties': {'box_2d': ..., 'label': ...}
            # BUT wait, evaluate_performance expects the standard map-reader output format 
            # which is just a list of features?
            # Actually detect_mounds outputs a FeatureCollection where features have properties.
            # properties has 'box_2d'.
            
            feat = {
                "type": "Feature",
                "properties": {
                    "box_2d": avg_box,
                    "label": "mound", # Generic
                    "subtype": main_label,
                    "source_tile": cl[0]["source_tile"], # Propagate from first match
                    "score": votes / 10.0 # Hack confidence
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [avg_box[0], avg_box[1]],
                        [avg_box[2], avg_box[1]],
                        [avg_box[2], avg_box[3]],
                        [avg_box[0], avg_box[3]],
                        [avg_box[0], avg_box[1]]
                    ]]
                }
            }
            features.append(feat)
            
    return {"type": "FeatureCollection", "features": features}

def create_consensus_prediction_with_crs(clusters, min_votes, crs):
    d = create_consensus_prediction(clusters, min_votes)
    if crs:
        d["crs"] = crs
    return d

def main():
    runs = load_runs()
    
    # 1. Individual Stats (Best/Worst)
    print("\n=== 1. Individual Run Performance (N=10) ===")
    print(f"Loaded {len(runs)} runs.")
    if not runs:
        print("No runs found!")
        return

    df = pd.DataFrame([r["metrics"] for r in runs])
    df["run_id"] = [r["id"] for r in runs]
    
    # Debug
    print("DataFrame Columns:", df.columns)
    print(df.head())

    # Sort
    if "f1" in df.columns:
        df_sorted = df.sort_values("f1", ascending=False)
    elif "f1_score" in df.columns:
        df_sorted = df.sort_values("f1_score", ascending=False)
    else:
        print("Error: No f1 column found.")
        return
    best = df_sorted.iloc[0]
    worst = df_sorted.iloc[-1]
    
    print(f"Mean F1: {df['f1'].mean():.4f} (Std: {df['f1'].std():.4f})")
    print(f"Best Run (Run {int(best['run_id'])}): F1={best['f1']:.4f} P={best['precision']:.4f} R={best['recall']:.4f}")
    print(f"Worst Run (Run {int(worst['run_id'])}): F1={worst['f1']:.4f} P={worst['precision']:.4f} R={worst['recall']:.4f}")
    
    # 2. Per-Symbol Variability
    # Count subtypes per run
    counts = []
    for r in runs:
        c = defaultdict(int)
        for feat in r["detections"]["features"]:
             st = feat["properties"].get("subtype", "unknown")
             c[st] += 1
        c["run_id"] = r["id"]
        counts.append(c)
    
    cdf = pd.DataFrame(counts).fillna(0)
    print("\n=== 2. Symbol Count Variability ===")
    print(cdf.describe().T[["mean", "std", "min", "max"]])
    
    # 3. Consensus Analysis
    # Prepare Dict[RunID] -> list of features
    all_dets = {r["id"]: r["detections"]["features"] for r in runs}
    
    # Cluster
    clusters = cluster_detections(all_dets)
    print(f"\nTotal Unique Clusters (Union of all runs): {len(clusters)}")
    
    # Thresholds
    thresholds = [3, 5, 7, 10]
    consensus_results = []
    
    # Get CRS from Run 1
    crs = get_crs(Path("outputs/results/v3.2_experimental/variability_study_v3.2_run_01.geojson"))

    print("\n=== 3. Global Consensus Thresholds (N=10) ===")
    for t in thresholds:
        cons_geo = create_consensus_prediction_with_crs(clusters, min_votes=t, crs=crs)
        
        # Save temp
        fname = RESULTS_DIR / f"consensus_t{t}.geojson"
        with open(fname, 'w') as f: json.dump(cons_geo, f)
        
        # Eval
        # We need to capture the text output or structured return?
        # evaluate_performance prints. We can capture it or refactor.
        # Let's trust evaluate_performance writes a metrics file if we give it a prefix?
        # evaluate_performance(detection_file, bounds_file, output_prefix)
        prefix = str(RESULTS_DIR / f"consensus_t{t}")
        evaluate_performance(fname, BOUNDS_FILE, prefix)
        
        # Read result
        try:
            with open(prefix + "_metrics.json") as f:
                m = json.load(f)
                m["threshold"] = t
                consensus_results.append(m)
                print(f"Require {t}/10 Agreement: F1={m['f1']:.4f} P={m['precision']:.4f} R={m['recall']:.4f}")
        except:
            print(f"Failed to eval T={t}")

    # 4. Ensemble Simulation (Claude's Suggestion: 3 Runs, 2 Votes)
    # We have 10 runs. 
    # Combinations of 3 runs = 120.
    # For each combo, we take the 3 runs, filter clusters that have >= 2 detections FROM THAT SUBSET.
    
    print("\n=== 4. Ensemble Simulation (Sample 3, Vote 2) ===")
    run_indices = list(all_dets.keys())
    combos = list(itertools.combinations(run_indices, 3))
    print(f"Simulating {len(combos)} ensembles...")
    
    sim_metrics = []
    
    # Optimization: Pre-map clusters to runs
    # cluster_map[cluster_idx] = set of run_ids
    cluster_run_map = []
    for cl in clusters:
        cluster_run_map.append(set(c["run_id"] for c in cl))
        
    # We can score efficiently? No, we need to run eval logic which involves spatial matching to Ground Truth.
    # That is slow (120 * eval time). 
    # Let's perform a "Smart Eval". 
    # We know the Ground Truth boxes (from manifest?).
    # Actually, evaluate_performance loads GT maps.
    
    # To avoid running full eval 120 times (20 mins?), let's just generate the consensus objects
    # and maybe run a sample? Or run 10 random samples?
    # User asked for "Results". Exhaustive is better if fast.
    # If calculate_metrics is fast...
    
    # Let's try 10 random ensembles first.
    import random
    random.seed(42)
    sample_combos = random.sample(combos, 10)
    
    print("Running 10 random ensemble samples (Representative)...")
    
    for combo in sample_combos:
        # Build consensus for this triplet
        # Valid cluster = it has run_ids intersect combo >= 2
        subset_clusters = []
        combo_set = set(combo)
        
        # Re-filter clusters
        # We can reuse the main clusters? Yes.
        # If a cluster has run_id 1 and 2, and our combo is (1, 2, 8), it counts.
        
        # Subset detections to create a "Virtual Consensus"
        
        # Faster way: 
        # For this triplet, just take the features from those 3 runs.
        # Re-cluster ONLY those 3 runs? Yes, strictly that's cleaner.
        # But slow.
        
        # Approx: Use global clusters. If a global cluster has members from >=2 of the triplet, keep it.
        # Calculate centroids from just the triplet members? Yes.
        
        valid_feats = []
        for cl in clusters:
            members_in_combo = [c for c in cl if c["run_id"] in combo_set]
            if len(members_in_combo) >= 2:
                # Average box
                boxes = np.array([c["box"] for c in members_in_combo])
                avg_box = np.mean(boxes, axis=0).astype(int).tolist()
                labels = [c["label"] for c in members_in_combo]
                main_label = max(set(labels), key=labels.count)
                
                valid_feats.append({
                    "type": "Feature",
                    "properties": {
                        "box_2d": avg_box, 
                        "subtype": main_label,
                        "source_tile": members_in_combo[0]["source_tile"]
                    },
                    "geometry": {"type": "Polygon", "coordinates": [[
                        [avg_box[0], avg_box[1]],
                        [avg_box[2], avg_box[1]],
                        [avg_box[2], avg_box[3]],
                        [avg_box[0], avg_box[3]],
                        [avg_box[0], avg_box[1]]
                    ]]}
                })
        
        # Save and Eval
        c_name = "-".join(map(str, combo))
        fname = RESULTS_DIR / f"ensemble_{c_name}.geojson"
        
        # Add CRS
        out_obj = {"type": "FeatureCollection", "features": valid_feats}
        if crs: out_obj["crs"] = crs

        with open(fname, 'w') as f: 
            json.dump(out_obj, f)
            
        prefix = str(RESULTS_DIR / f"ensemble_{c_name}")
        evaluate_performance(fname, BOUNDS_FILE, prefix)
        
        try:
            with open(prefix + "_metrics.json") as f:
                sim_metrics.append(json.load(f))
        except: pass
        
    sdf = pd.DataFrame(sim_metrics)
    print("\nSimulated Ensemble Results (Vote 2/3, N=10 samples):")
    print(sdf[['f1', 'precision', 'recall']].describe())


if __name__ == "__main__":
    main()
