#!/usr/bin/env python3
"""
extract_trial.py — print the bridge findings' §§ 5, 6, 7, 7a numbers, OLD → NEW.

OLD is a committed results directory (floors/, verifier-sd/); NEW a trial
output directory with the same two subdirectories. Read only.

Usage: extract_trial.py <old_results_dir> <new_trial_dir> [--json OUT]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load(root: Path) -> dict:
    """Read the seven JSON files a floors + verifier-SD run writes."""
    f, v = root / "floors", root / "verifier-sd"
    return {
        "gc": json.loads((f / "gap_change.json").read_text()),
        "dc": json.loads((f / "date_component.json").read_text())["cells"],
        "fl": json.loads((f / "floors.json").read_text()),
        "vs": json.loads((v / "verifier_sd.json").read_text()),
        "fv": json.loads((v / "floors_with_verifier.json").read_text())["contrasts"],
    }


def r(x, n=4):
    """Round a float or return it as is."""
    return round(x, n) if isinstance(x, (int, float)) else x


def main() -> int:
    """Print every quantity as old -> new and optionally dump the NEW extract."""
    old, new = load(Path(sys.argv[1])), load(Path(sys.argv[2]))
    out: dict = {}

    print("== § 5 gap change (estimate, CI95, p modality, p family, BH)")
    for lab in new["gc"]:
        o, n = old["gc"].get(lab, {}), new["gc"][lab]
        row = {k: [r(o.get(k)), r(n.get(k))] for k in
               ("gap_change", "p_modality_swap", "p_family_swap", "p_bh_all_ten")}
        row["ci95"] = [[r(x) for x in o.get("ci95", [])], [r(x) for x in n["ci95"]]]
        out[f"gc/{lab}"] = row
        print(lab, row)

    print("== § 6 date component")
    for cell, rec in new["dc"].items():
        o = old["dc"].get(cell, {})
        for name in ("at_original_point", "at_oracle"):
            a, b = o.get(name, {}), rec[name]
            fo, fn = a.get("flips", {}), b["flips"]
            row = {"bridge_point": [a.get("bridge_point"), b["bridge_point"]],
                   "bridge_f1": [r(a.get("bridge_f1")), r(b["bridge_f1"])],
                   "original_f1": [r(o.get("original_f1")), r(rec["original_f1"])],
                   "difference": [r(a.get("difference")), r(b["difference"])],
                   "p": [r(a.get("p_tile_swap")), r(b["p_tile_swap"])],
                   "discordant": [fo.get("discordant"), fn["discordant"]],
                   "fixed/broken": [[fo.get("fixed"), fo.get("broken")],
                                    [fn["fixed"], fn["broken"]]],
                   "d_tp/d_fp": [[fo.get("d_tp"), fo.get("d_fp")], [fn["d_tp"], fn["d_fp"]]]}
            fd_o = old["fl"]["date_components"].get(cell, {}).get(name, {})
            fd_n = new["fl"]["date_components"][cell][name]
            we_o, we_n = fd_o.get("within_execution_flips", {}), fd_n["within_execution_flips"]
            row["within_med/p95"] = [[r(we_o.get("discordant_rate_median")),
                                      r(we_o.get("discordant_rate_p95"))],
                                     [r(we_n["discordant_rate_median"]),
                                      r(we_n["discordant_rate_p95"])]]
            row["of_floor"] = [r(fd_o.get("ratio"), 2), r(fd_n["ratio"], 2)]
            row["of_s3"] = [r(fd_o.get("s3_ratio"), 2), r(fd_n["s3_ratio"], 2)]
            out[f"dc/{cell}/{name}"] = row
            print(cell, name, row)

    print("== § 7 cell SDs (sd, upper, direct)")
    for key, c in new["fl"]["cells"].items():
        o = old["fl"]["cells"].get(key, {})
        row = {"point": [o.get("point"), c["point"]], "f1": [r(o.get("f1")), r(c["f1"])],
               "sd": [r(o.get("sd")), r(c["sd"])],
               "sd_upper": [r(o.get("sd_upper")), r(c["sd_upper"])],
               "sd_direct": [r(o.get("sd_direct")), r(c["sd_direct"])]}
        out[f"cell/{key}"] = row
        print(key, row)
    for kind in ("gaps", "gap_changes"):
        print(f"== § 7 {kind}")
        for lab, g in new["fl"][kind].items():
            o = old["fl"][kind].get(lab, {})
            row = {k: [r(o.get(k), 4 if "floor" in k or k == "estimate" else 2),
                       r(g[k], 4 if "floor" in k or k == "estimate" else 2)]
                   for k in ("estimate", "floor", "floor_upper", "ratio", "ratio_upper",
                             "floor_direct", "ratio_direct", "s3_floor", "s3_ratio")}
            out[f"{kind}/{lab}"] = row
            print(lab, row)

    print("== § 7a cells (F1 reps, SD, CI, split)")
    for key, c in new["vs"]["cells"].items():
        o = old["vs"]["cells"].get(key, {})
        row = {"point": [o.get("point"), c["point"]],
               "f1": [[r(o.get("f1", {}).get(s)) for s in "123"], [r(c["f1"][s]) for s in "123"]],
               "sd": [r(o.get("sd")), r(c["sd"])],
               "ci95": [[r(x) for x in o.get("sd_ci95", [])], [r(x) for x in c["sd_ci95"]]],
               "split": [[o.get("flips", {}).get("split", {}).get("count"),
                          o.get("flips", {}).get("n")],
                         [c["flips"]["split"]["count"], c["flips"]["n"]]],
               "rep1_minus_later": [r(o.get("rep1_minus_mean_later")),
                                    r(c["rep1_minus_mean_later"])]}
        out[f"vcell/{key}"] = row
        print(key, row)
    print("== § 7a pooled")
    for fam, p in new["vs"]["pooled"].items():
        o = old["vs"]["pooled"].get(fam, {})
        row = {"sd": [r(o.get("sd")), r(p["sd"])], "df": [o.get("df"), p["df"]],
               "ci95": [[r(x) for x in o.get("sd_ci95", [])], [r(x) for x in p["sd_ci95"]]]}
        out[f"pooled/{fam}"] = row
        print(fam, row)
    print("== § 7a unions (prob changed share, text identical share)")
    for key, u in new["vs"]["unions"].items():
        o = old["vs"]["unions"].get(key, {})
        row = {"prob_changed": [{k: r(v, 3) for k, v in o.get("prob_changed_share", {}).items()},
                                {k: r(v, 3) for k, v in u["prob_changed_share"].items()}],
               "text_identical": [{k: r(v, 3)
                                   for k, v in o.get("text_identical_share", {}).items()},
                                  {k: r(v, 3) for k, v in u["text_identical_share"].items()}]}
        out[f"union/{key}"] = row
        print(key, row)
    print("== § 7a contrasts")
    for lab, g in new["fv"].items():
        o = old["fv"].get(lab, {})
        oc, nc = o.get("committed", {}), g["committed"]
        ow, nw = o.get("with_verifier", {}), g["with_verifier"]
        row = {"estimate": [r(o.get("estimate")), r(g["estimate"])],
               "band floor (ratio)": [[r(oc.get("floor")), r(oc.get("ratio"), 2)],
                                      [r(nc["floor"]), r(nc["ratio"], 2)]],
               "measured floor (ratio)": [[r(ow.get("floor")), r(ow.get("ratio"), 2)],
                                          [r(nw["floor"]), r(nw["ratio"], 2)]],
               "upper band->meas": [[r(oc.get("ratio_upper"), 2), r(ow.get("ratio_upper"), 2)],
                                    [r(nc["ratio_upper"], 2), r(nw["ratio_upper"], 2)]],
               "direct band->meas": [[r(oc.get("ratio_direct"), 2), r(ow.get("ratio_direct"), 2)],
                                     [r(nc["ratio_direct"], 2), r(nw["ratio_direct"], 2)]],
               "s3 without->with": [[r(oc.get("s3_ratio"), 2), r(ow.get("s3_ratio"), 2)],
                                    [r(nc["s3_ratio"], 2), r(nw["s3_ratio"], 2)]],
               "pooled / pooled upper / each upper":
                   [[r(ow.get("ratio_verifier_pooled"), 2),
                     r(ow.get("ratio_verifier_pooled_upper"), 2),
                     r(ow.get("ratio_verifier_upper"), 2)],
                    [r(nw["ratio_verifier_pooled"], 2), r(nw["ratio_verifier_pooled_upper"], 2),
                     r(nw["ratio_verifier_upper"], 2)]],
               "break_even": [r(o.get("break_even_verifier_sd")), r(g["break_even_verifier_sd"])]}
        out[f"contrast/{lab}"] = row
        print(lab, row)
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(out, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
