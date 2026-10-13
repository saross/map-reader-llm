"""Format the tier-0 before/after table from summarise_h13.py's JSON (scratch helper)."""
import json
import sys

s = json.load(open(sys.argv[1]))
for r in s["tier0"]["cells"]:
    d = r["detections"]
    print(f"| {r['arm'][-1]} | {r['min_corroboration']} | {r['min_votes']} | "
          f"{r['n_detections_new']:,} | {d['sheet_changed']} | "
          f"{r['f1_old']:.4f} [{r['f1_ci_lower_old']:.4f}, {r['f1_ci_upper_old']:.4f}] | "
          f"{r['f1_new']:.4f} [{r['f1_ci_lower_new']:.4f}, {r['f1_ci_upper_new']:.4f}] | "
          f"{r['f1_new'] - r['f1_old']:+.4f} |")
