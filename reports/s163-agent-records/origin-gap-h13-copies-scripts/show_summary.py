"""Print the H13 summary tables (D62 (1) workstream; scratch helper)."""
import json
import sys

s = json.load(open(sys.argv[1]))
what = sys.argv[2]
if what == "tier0":
    t = s["tier0"]
    print("TIER0 moved", t["n_moved"], "of", len(t["cells"]))
    for r in t["cells"]:
        d = r["detections"]
        print(f"{r['arm']} c{r['min_corroboration']} k{r['min_votes']} "
              f"n {r['n_detections_old']}->{r['n_detections_new']} "
              f"P {r['precision_old']:.4f}->{r['precision_new']:.4f} "
              f"R {r['recall_old']:.4f}->{r['recall_new']:.4f} "
              f"F1 {r['f1_old']:.4f}->{r['f1_new']:.4f} "
              f"CI [{r['f1_ci_lower_old']:.4f},{r['f1_ci_upper_old']:.4f}]->"
              f"[{r['f1_ci_lower_new']:.4f},{r['f1_ci_upper_new']:.4f}] "
              f"sheet {d['sheet_changed']} null {d['now_null']} tile {d['tile_changed']}")
    for side in ("best_old", "best_new"):
        for g, r in t[side].items():
            print(side, g, r["min_corroboration"], r["min_votes"],
                  round(r["f1_" + side[5:]], 4))
elif what == "ksens":
    k = s["ksens"]
    for pool in ("minimal-t1.0", "minimal-t0.7"):
        p = k[pool]
        print(pool, "moved", p["n_moved"], "of", len(p["cells"]),
              "max|dF1|", round(p["max_abs_df1"], 4), "profile_same", p["profile_same"])
        for side in ("best_old", "best_new"):
            for g, r in p[side].items():
                print(" ", side, "K", g, "c", r["min_corroboration"], "k", r["min_votes"],
                      round(r["f1_" + side[5:]], 4),
                      "INTERIOR" if r["min_votes"] < int(g) else "edge")
    for side in ("old", "new"):
        d = k["decomposition"][side]
        print("decomp", side, {x: d[x] for x in ("native_scope_deduped_f1", "precision",
                                                 "recall", "n_detections")})
elif what == "tilesize":
    t = s["tilesize"]
    print("TILESIZE moved", t["n_moved"], "of", len(t["cells"]), "scope_same", t["scope_same"])
    for side in ("best_old", "best_new"):
        for g, r in t[side].items():
            print(side, g, "c", r["min_corroboration"], "k", r["min_votes"],
                  round(r["f1_" + side[5:]], 4), "n", r["n_detections_" + side[5:]])
    big = sorted(t["cells"], key=lambda r: -abs(r["f1_new"] - r["f1_old"]))[:8]
    for r in big:
        print("  largest", r["cell"], r["K_label"], r["min_corroboration"], r["min_votes"],
              round(r["f1_old"], 4), "->", round(r["f1_new"], 4), r["detections"])
