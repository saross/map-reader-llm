"""Compare the February 60-tile analyses: archived (pseudo-p) vs D42 re-run."""
import json
import pandas as pd
from pathlib import Path
A = Path.home() / "Code/map-reader-llm/archive/outputs-pre-retest-60-tile"
N = Path("/tmp/d42/feb")
pairs = {"phase2a": A / "phase2a/analysis_report.json",
         "phase2b-track1": A / "phase2b/phase2b-track1-image-analysis.json",
         "phase2b-track2": A / "phase2b/phase2b-track2-text-analysis.json",
         "phase2e": A / "phase2e/analysis_report.json"}
csvs = {"phase2c-track1": A / "phase2c/track1-image/per_run_metrics.csv",
        "phase2c-exploratory": A / "phase2c/track1-image-exploratory/per_run_metrics.csv",
        "phase2d-track1": A / "phase2d/track1-image/per_run_metrics.csv",
        "phase2d-track2": A / "phase2d/track2-text/per_run_metrics.csv"}
summary = {}
for name in ["phase2a", "phase2b-track1", "phase2b-track2", "phase2c-track1",
             "phase2c-exploratory", "phase2d-track1", "phase2d-track2", "phase2e"]:
    new = json.load(open(N / f"{name}.json"))
    newc = {k: v["point_estimate"]["f1"] for k, v in new["per_condition_metrics"].items()}
    print(f"== {name}: {len(new['pairwise_comparisons'])} contrasts")
    if name in pairs:
        old = json.load(open(pairs[name]))
        oldc = {k: v["point_estimate"]["f1"] for k, v in old["per_condition_metrics"].items()}
        dmax = max(abs(oldc[k] - newc[k]) for k in oldc)
        print(f"   per-condition mean F1, max |old-new| = {dmax:.2e}")
        oldp = {(c["condition_a"], c["condition_b"]): c for c in old["pairwise_comparisons"]}
    else:
        df = pd.read_csv(csvs[name])
        means = df.groupby("condition")["f1"].mean().to_dict()
        dmax = max(abs(means[k] - newc[k]) for k in means)
        print(f"   per-condition mean F1 vs archived per_run_metrics.csv, max |diff| = {dmax:.2e}")
        oldp = {}
    rows = []
    for c in new["pairwise_comparisons"]:
        key = (c["condition_a"], c["condition_b"])
        o = oldp.get(key)
        rows.append({
            "a": key[0], "b": key[1],
            "delta": round(c["f1_difference"]["mean"], 4),
            "ci": [round(c["f1_difference"]["ci_lower"], 4), round(c["f1_difference"]["ci_upper"], 4)],
            "perm_p": c["f1_difference"]["p_value"],
            "bh_p": round(c["fdr_adjusted_p"], 4),
            "new_raw": c["initially_significant"], "new_fdr": c["fdr_significant"],
            "old_raw": None if o is None else o.get("initially_significant"),
            "old_fdr": None if o is None else o.get("fdr_significant"),
            "k": c.get("permutation", {}).get("n_discordant_tiles"),
        })
    for r in rows:
        flag = ""
        if r["old_fdr"] is not None and r["old_fdr"] != r["new_fdr"]:
            flag = "  <-- FDR VERDICT CHANGES"
        print(f"   {r['a']:>18} vs {r['b']:<18} d={r['delta']:+.4f} CI{r['ci']} p={r['perm_p']:.4f} "
              f"BH={r['bh_p']:.4f} new={r['new_fdr']} old={r['old_fdr']}{flag}")
    summary[name] = rows
json.dump(summary, open("/tmp/d42/feb_compare.json", "w"), indent=1)
