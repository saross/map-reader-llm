
import json
import pandas as pd
from pathlib import Path
import numpy as np

STUDY_DIR = Path("outputs/results/variability_study_v3.2")
metrics = []

print(f"Aggregating results from {STUDY_DIR}...")
for f in sorted(STUDY_DIR.glob("run_*_metrics.json")):
    try:
        with open(f, 'r') as fp:
            m = json.load(fp)
            m['run'] = f.stem
            metrics.append(m)
    except Exception as e:
        print(f"Skipping {f}: {e}")

if not metrics:
    print("No metrics found.")
else:
    df = pd.DataFrame(metrics)
    print("\n--- Partial Results (N={}) ---".format(len(df)))
    stats = df[['f1', 'precision', 'recall']].describe()
    print(stats)
    print("\n--- Detailed ---")
    print(df[['run', 'f1', 'precision', 'recall']])
