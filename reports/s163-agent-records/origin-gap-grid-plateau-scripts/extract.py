"""Pull every board number the delta report needs from one tree (or a git ref).

Usage: python extract.py <tree|git:REF:REPO> <out_json>

The same named quantities are read from the committed artefacts and from
each re-scored copy, so the report's before -> after tables and the
run A = run B integrity check are computed on identical keys.
"""

import json
import subprocess
import sys
from pathlib import Path

SPEC = sys.argv[1]
CELLS = ["g512_ov064", "g512_ov256", "g384_ov048", "g384_ov192"]
FDR_Q = 0.05


def load(rel):
    if SPEC.startswith("git:"):
        _, ref, repo = SPEC.split(":", 2)
        out = subprocess.run(
            ["git", "-C", repo, "show", f"{ref}:{rel}"], capture_output=True, check=True
        ).stdout
        return json.loads(out)
    return json.loads((Path(SPEC) / rel).read_text())


out = {}

# ---- GS grid, consensus-only (grid_analysis.json; R1b-02..07, R1b-05) ----
g = load("results/grid-2026-08-18/grid_analysis.json")
for cell in CELLS:
    rows = [r for r in g["sweep"] if r["cell"] == cell and r["K"] == 10]
    best = max(rows, key=lambda r: r["f1"])
    out[f"grid/k10best/{cell}"] = {
        k: best[k]
        for k in (
            "f1",
            "precision",
            "recall",
            "mcc",
            "n_detections",
            "min_corroboration",
            "min_votes",
        )
    }
    union = next(r for r in rows if r["min_corroboration"] == 1 and r["min_votes"] == 1)
    out[f"grid/k10union/{cell}"] = {k: union[k] for k in ("f1", "recall", "n_detections")}
    sp = g["single_pass"][cell]
    out[f"grid/single/{cell}"] = {"f1": sp["mean"]["f1"], "mcc": sp["mcc_mean"]}
for name, c in g["contrasts"].items():
    out[f"grid/contrast/{name}"] = {
        k: c[k] for k in ("delta", "ci_lower", "ci_upper", "p_two_sided")
    }
out["grid/interaction"] = {
    k: g["interaction"][k]
    for k in ("difference_of_differences", "ci_lower", "ci_upper", "p_two_sided")
}
pvo = g["cost_efficiency"]["passes_versus_overlap"]
out["grid/passes_vs_overlap"] = {
    "verdict": pvo["verdict"],
    "challenger_union_recall": pvo["more_passes_less_overlap"]["union_recall"],
    "challenger_best_f1": pvo["more_passes_less_overlap"]["best_f1"],
    "incumbent_union_recall": pvo["fewer_passes_more_overlap"]["union_recall"],
    "incumbent_best_f1": pvo["fewer_passes_more_overlap"]["best_f1"],
}
k1 = {r["cell"]: r for r in g["cost_efficiency"]["frontier"] if r["K"] == 1}
out["grid/frontier_k1_best_f1/g512_ov256"] = k1["g512_ov256"]["best_f1"]

# ---- registered consensus conditions (grid_conditions.json) ----
gc = load("results/grid-2026-08-18/conditions/grid_conditions.json")
for c in gc["cells"]:
    out[f"grid/condition/{c['cell']}"] = {
        k: c[k]
        for k in (
            "rescored_f1_at_20m",
            "f1_ci_lower",
            "f1_ci_upper",
            "tile_mcc",
            "n_detections",
            "min_corroboration",
            "min_votes",
        )
    }

# ---- GS grid, post-verifier (verifier_analysis.json; R1b-08..12) ----
v = load("results/grid-2026-08-18/verifier_analysis.json")
for cell in CELLS:
    b = v["board_best"][cell]
    out[f"pv/best/{cell}"] = {
        k: b[k] for k in ("f1", "precision", "recall", "mcc", "n_detections", "prob_t", "min_votes")
    }
    out[f"pv/pure_k1/{cell}"] = v["board_pure_verifier_k1"][cell]["f1"]
    out[f"pv/gain/{cell}"] = v["verifier_gain_over_consensus"][cell]
    out[f"pv/consensus_committed/{cell}"] = v["board_consensus_only_committed"][cell]["f1"]
for name, c in v["bootstrap_contrasts"].items():
    out[f"pv/contrast/{name}"] = {k: c[k] for k in ("delta", "ci_lower", "ci_upper", "p_two_sided")}
for name, c in v["bootstrap_contrasts_consensus_k10_baseline"].items():
    out[f"pv/baseline/{name}"] = {k: c[k] for k in ("delta", "ci_lower", "ci_upper", "p_two_sided")}
out["pv/interaction"] = {
    k: v["interaction"][k]
    for k in ("difference_of_differences", "ci_lower", "ci_upper", "p_two_sided")
}
for c in v.get("conditions", []):
    out[f"pv/condition/{c['cell']}"] = {
        k: c[k]
        for k in ("rescored_f1_at_20m", "f1_ci_lower", "f1_ci_upper", "tile_mcc", "n_detections")
    }

# ---- stride board (stride_verifier_analysis.json; R1b-13, R1b-14) ----
s = load("results/stride-2026-08-25/stride_verifier_analysis.json")
for cell, b in s["boards"].items():
    out[f"stride/best/{cell}"] = {
        k: b.get(k) for k in ("f1", "f1_30m", "mcc", "n_detections", "prob_t", "min_votes")
    }
for name, c in s["contrasts"].items():
    out[f"stride/contrast/{name}"] = {
        k: c[k] for k in ("delta", "ci_lower", "ci_upper", "p_two_sided")
    }

# ---- Phase A incumbents on the common footprint ----
inc = load("results/grid-2026-08-18/incumbents_common_footprint.json")
for r in inc["incumbents"]:
    out[f"phaseA/{r['condition_id'].split('::')[1]}"] = {
        "f1_20": r["common_footprint_20m"]["f1"],
        "f1_30": r["common_footprint_30m"]["f1"],
        "mcc_20": r["common_footprint_20m"]["mcc"],
        "n": r["n_detections_common"],
        "vs_winner_delta": r["paired_contrast_vs_grid_winner_20m"]["delta"],
        "vs_winner_p": r["paired_contrast_vs_grid_winner_20m"]["p_two_sided"],
    }

# ---- plateau board (plateau_analyses.json; R1b-15..18) ----
p = load("results/stride-2026-08-25/plateau_analyses.json")
b13 = p["board_13cell"]
out["plateau/f1"] = b13["f1"]
out["plateau/order"] = b13["order"]
out["plateau/tiers"] = b13["tiers"]
out["plateau/n_pairs_significant"] = b13["n_pairs_significant"]
out["plateau/n_pairs"] = b13["n_pairs"]
out["plateau/significant_pairs"] = sorted(
    k for k, r in b13["pairwise"].items() if r["significant_bh"]
)
for cell, kc in p["k_curves"].items():
    out[f"plateau/k_curve/{cell}"] = {k: kc[k] for k in ("prob_t", "best_k", "k_within_0p005")}
for cell, lad in p["first_n_ladder"].items():
    for n, row in lad["N"].items():
        out[f"plateau/first_n/{cell}/N{n}"] = {
            k: row["best"][k] for k in ("f1", "prob_t", "min_votes")
        }
for n, row in p["winner_ladder_exact"]["N"].items():
    out[f"plateau/exact/N{n}"] = {
        "f1": row["best"]["f1"],
        "mcc": row["best"]["mcc"],
        "prob_t": row["best"]["prob_t"],
        "min_votes": row["best"]["min_votes"],
        "f1_30m": row["f1_30m"],
        "all_in": row["all_in_flex_usd"],
    }

# ---- Image-B (analysis.json, high/, pair verdicts; signed image-b-modality) ----
for tag, rel in (
    ("min", "results/image-b-gs-2026-08-28/analysis.json"),
    ("high", "results/image-b-gs-2026-08-28/high/analysis.json"),
):
    a = load(rel)
    out[f"imageb/{tag}/best"] = {
        k: a["image_best"][k]
        for k in ("f1", "precision", "recall", "mcc", "n_detections", "prob_t", "min_votes")
    }
    out[f"imageb/{tag}/anchor_f1"] = a["anchor"]["f1_20"]
    out[f"imageb/{tag}/head"] = {
        k: a["head_to_head_20m"][k] for k in ("f1_a", "f1_b", "observed_diff", "p_value")
    }
    for buf in ("20", "30", "50", "75"):
        out[f"imageb/{tag}/curve/{buf}"] = {
            "text": a["buffer_curves"]["text"][buf]["f1"],
            "image": a["buffer_curves"]["image"][buf]["f1"],
            "text_mcc": a["buffer_curves"]["text"][buf]["mcc"],
            "image_mcc": a["buffer_curves"]["image"][buf]["mcc"],
        }
    for n, row in a["ladder"].items():
        out[f"imageb/{tag}/ladder/N{n}"] = {
            k: row["best"][k] for k in ("f1", "prob_t", "min_votes")
        }
        out[f"imageb/{tag}/ladder/N{n}/union_n"] = row["union_n"]
    for key in ("saturation_N5_vs_N10", "saturation_N3_vs_N10"):
        if key in a:
            out[f"imageb/{tag}/{key}"] = {k: a[key][k] for k in ("observed_diff", "p_value")}
pv = load("results/image-b-gs-2026-08-28/high/pair_verdicts.json")
out["imageb/pair/hp1"] = {
    k: pv["hp1_high_vs_min_20m"][k] for k in ("f1_a", "f1_b", "observed_diff", "p_value")
}
out["imageb/pair/hp2"] = pv["hp2_union"]
out["imageb/pair/hp3"] = pv["hp3_mcc"]
out["imageb/pair/hp4"] = pv["hp4_points"]

Path(sys.argv[2]).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
print(f"{len(out)} keys -> {sys.argv[2]}")
