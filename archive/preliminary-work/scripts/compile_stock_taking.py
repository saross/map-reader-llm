
import os
import json
import pandas as pd
from pathlib import Path
import sys
import numpy as np

# Add parent directory to path
sys.path.append(os.getcwd())
try:
    from scripts.lib_advanced_metrics import calculate_f1_internal, calculate_per_class_f1, load_data
except ImportError:
    pass # functionality might be limited if imports fail

def get_symbol_metrics(adv_metrics):
    """Extracts per-class metrics if available."""
    symbols = {}
    if "per_class_performance" in adv_metrics:
        for item in adv_metrics["per_class_performance"]:
            cls = item["class"]
            symbols[f"{cls}_f1"] = item["f1"]
            symbols[f"{cls}_p"] = item["precision"]
            symbols[f"{cls}_r"] = item["recall"]
    return symbols

def get_spatial_metrics(adv_metrics):
    """Extracts spatial tolerance metrics."""
    spatial = {}
    if "spatial_tolerance" in adv_metrics:
        for item in adv_metrics["spatial_tolerance"]:
            buff = item["buffer"]
            if buff in [10, 30, 50]: # Key buffers
                spatial[f"f1_{buff}m"] = item["f1"]
    return spatial

def get_ci(adv_metrics):
    """Extracts CI."""
    ci = {}
    if "bootstrap_ci" in adv_metrics and adv_metrics["bootstrap_ci"]:
        b = adv_metrics["bootstrap_ci"]
        ci["ci_lower"] = b.get("ci_lower")
        ci["ci_upper"] = b.get("ci_upper")
        ci["ci_mean"] = b.get("mean")
    return ci

def scan_directory(base_dir):
    records = []
    base_dir = Path(base_dir)
    if not base_dir.exists(): return []

    print(f"Scanning {base_dir}...")
    
    # 1. Variability/Consensus Studies (Prioritize Folders with Reports)
    # These often contain 'variability_report.md' or 'strategy_stats.csv'
    # We want to capture the "Strategies" tested here.
    
    for root, dirs, files in os.walk(base_dir):
        root_path = Path(root)
        
        # Check for Strategy Stats (Consensus)
        if "strategy_stats.csv" in files:
            print(f"  Found Consensus Study: {root_path.name}")
            try:
                df_strat = pd.read_csv(root_path / "strategy_stats.csv")
                # Load metadata from one of the runs to get prompt info
                # Usually runs are in the same dir or passed as args. 
                # We'll look for *meta.json in the same dir or up one level
                meta_files = list(root_path.glob("*.meta.json"))
                if not meta_files: meta_files = list(root_path.glob("run_*.meta.json"))
                
                prompt_ver = "Unknown"
                temp = "Unknown"
                if meta_files:
                    with open(meta_files[0]) as f:
                        m = json.load(f)
                        prompt_ver = m.get("configuration", {}).get("version", "Unknown")
                        temp = m.get("configuration", {}).get("temperature", "Unknown")
                else:
                    # Try to guess from folder name
                    prompt_ver = root_path.name

                for _, row in df_strat.iterrows():
                    rec = {
                        "job_name": root_path.name,
                        "prompt_version": prompt_ver,
                        "strategy": f"Consensus {row.get('vote_threshold', '?')}/{row.get('pool_size', '?')}",
                        "temperature": temp,
                        "f1": row.get("f1"),
                        "precision": row.get("precision"),
                        "recall": row.get("recall"),
                        "ci_lower": row.get("ci_lower"),
                        "ci_upper": row.get("ci_upper"),
                        "notes": "Consensus Simulation"
                    }
                    records.append(rec)
            except Exception as e:
                print(f"    Error reading strategy stats in {root_path.name}: {e}")

        # Check for Standard Metrics/Advanced Metrics (Single Runs)
        # We look for *.meta.json files
        meta_files = [f for f in files if f.endswith(".meta.json") and not f.startswith("benchmark_variability")]
        
        for mf in meta_files:
            try:
                meta_path = root_path / mf
                with open(meta_path) as f:
                    meta = json.load(f)
                
                run_id = meta.get("run_id", mf)
                config = meta.get("configuration", {})
                ver = config.get("version", "Unknown")
                temp = config.get("temperature", "Unknown")
                
                # Look for metrics file
                base_name = mf.replace(".meta.json", "")
                metrics_file = root_path / f"{base_name}_metrics.json"
                adv_metrics_file = root_path / f"{base_name}_advanced_metrics.json"
                
                f1, p, r = None, None, None
                extra_metrics = {}
                
                if metrics_file.exists():
                    with open(metrics_file) as f:
                        met = json.load(f)
                        f1 = met.get("f1")
                        p = met.get("precision")
                        r = met.get("recall")
                
                if adv_metrics_file.exists():
                    with open(adv_metrics_file) as f:
                        adv = json.load(f)
                        extra_metrics.update(get_symbol_metrics(adv))
                        extra_metrics.update(get_spatial_metrics(adv))
                        extra_metrics.update(get_ci(adv))
                        
                # If metrics missing, try to scrape from 'results_summary' in meta?
                # Usually that's just counts, not accuracy.
                
                # Filter strict for v3.0+
                if "v1" in ver or "v2" in ver: continue
                
                rec = {
                    "job_name": root_path.name,
                    "prompt_version": ver,
                    "strategy": "Single Run",
                    "temperature": temp,
                    "f1": f1,
                    "precision": p,
                    "recall": r
                }
                rec.update(extra_metrics)
                records.append(rec)
                
            except Exception as e:
                print(f"    Error processing {mf}: {e}")

    return records

def compile_all():
    all_records = []
    
    dirs_to_scan = [
        "outputs/results",
        "archive/results",
        "outputs/overnight"
    ]
    
    for d in dirs_to_scan:
        all_records.extend(scan_directory(d))
        
    df = pd.DataFrame(all_records)
    
    # Clean up column order
    cols_order = ["prompt_version", "job_name", "strategy", "temperature", "f1", "precision", "recall", 
                  "ci_lower", "ci_upper",
                  "burial_mound_f1", "benchmark_mound_f1", "triangulation_mound_f1",
                  "f1_10m", "f1_30m", "f1_50m", "notes"]
    
    # ensure cols exist
    for c in cols_order:
        if c not in df.columns: df[c] = None
        
    # Reorder
    df = df[cols_order + [c for c in df.columns if c not in cols_order]]
    
    # Sort
    df.sort_values(by=["prompt_version", "f1"], ascending=[True, False], inplace=True)
    
    out_path = "stock_taking.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved compiled records to {out_path}")

if __name__ == "__main__":
    compile_all()
