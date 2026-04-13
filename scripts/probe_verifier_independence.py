#!/usr/bin/env python3
# ============================================================================
# probe_verifier_independence.py
# ----------------------------------------------------------------------------
# Verifier-independence probe for the H10/H12 null result.
#
# Background
# ----------
# H10/H12 found that 5 library compositions converge to F1=0.885 after the
# adversarial verifier is applied, despite a +0.039 F1 spread at the proposer
# stage (Obs 227). Three mechanisms could produce this null:
#
#   H-A  Set divergence:        configs propose different candidates; the
#                               verifier scores each pool independently and
#                               equivalence is averaged-out, not pointwise.
#   H-B  Pointwise equivalence: spatially matched candidates receive
#                               near-identical verifier probabilities across
#                               configs. The verifier is genuinely
#                               proposer-blind for the same physical feature.
#   H-C  Threshold compensation: matched candidates receive correlated but
#                               offset probabilities, and the F1 sweep selects
#                               different optimal thresholds that cancel.
#
# Discriminating logic
# --------------------
#   * High shared fraction (>=0.6 of total candidates), ICC >= 0.9, identical
#     optimal thresholds  -> H-B (verifier dominates).
#   * High shared fraction, ICC 0.6-0.9, divergent optimal thresholds  -> H-C.
#   * Shared fraction < 0.6 of pooled candidates                       -> H-A.
#
# Inputs
# ------
#   * outputs/h10/verifier-crops/pool_*/candidate_manifest.json
#   * outputs/h10/verified/pool_*/probabilities.json
#   * results/h10/sweep_results.json (for per-config optimal thresholds)
#
# Outputs
# -------
#   * results/h10/verifier_independence_probe.json (all statistics)
#   * results/h10/verifier_independence_probe.md   (interpretation + verdict)
#
# No API calls. Pure spatial join + statistical comparison. Runs in seconds.
# ============================================================================

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

DEFAULT_CONFIGS = (
    "pool_160_hp4hn4",
    "pool_160_hp2hn6",
    "pool_160_hp6hn2",
    "pool_160_hp8hn8",
    "pool_160_hp16hn16",
)

DEFAULT_BUFFER_M = 20.0  # matches the evaluation buffer used elsewhere

# ----------------------------------------------------------------------------
# Loaders
# ----------------------------------------------------------------------------


def load_config_table(
    h10_dir: Path,
    config: str,
) -> pd.DataFrame:
    """Join the candidate manifest to the verifier probabilities for a config.

    Returns one row per candidate with columns:
        config, candidate_id, x, y, vote_count, mound_probability
    """
    manifest_path = h10_dir / "verifier-crops" / config / "candidate_manifest.json"
    probs_path = h10_dir / "verified" / config / "probabilities.json"

    manifest = json.loads(manifest_path.read_text())
    probs = json.loads(probs_path.read_text())["results"]

    rows: list[dict] = []
    for entry in manifest["candidates"]:
        cid = entry["candidate_id"]
        prob_key = f"candidate_{cid:05d}"
        prob_entry = probs.get(prob_key)
        if prob_entry is None:
            continue
        rows.append(
            {
                "config": config,
                "candidate_id": cid,
                "x": float(entry["centroid_x"]),
                "y": float(entry["centroid_y"]),
                "vote_count": int(entry["properties"].get("vote_count", 0)),
                "mound_probability": float(prob_entry["mound_probability"]),
            }
        )

    return pd.DataFrame(rows)


def load_sweep_optima(sweep_path: Path) -> dict[str, dict]:
    """Return the per-config (vote_t, prob_t, F1) maximum from the sweep."""
    rows = json.loads(sweep_path.read_text())
    by_config: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_config[row["config"]].append(row)

    optima: dict[str, dict] = {}
    for config, config_rows in by_config.items():
        best = max(config_rows, key=lambda r: r["f1"])
        optima[config] = {
            "vote_t": best["vote_t"],
            "prob_t": best["prob_t"],
            "f1": best["f1"],
            "p": best["p"],
            "r": best["r"],
        }
    return optima


# ----------------------------------------------------------------------------
# Cross-config spatial clustering
# ----------------------------------------------------------------------------


class UnionFind:
    """Standard union-find with path compression and union by rank."""

    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, i: int) -> int:
        while self.parent[i] != i:
            self.parent[i] = self.parent[self.parent[i]]
            i = self.parent[i]
        return i

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1


def cluster_across_configs(
    pooled: pd.DataFrame,
    buffer_m: float,
) -> pd.DataFrame:
    """Single-link spatial clustering of all candidates across all configs.

    Returns the input DataFrame with a new ``cluster_id`` column. Within a
    single config, candidates are already deduplicated by the upstream
    consensus pipeline, so cross-config edges are the only ones that should
    fire at small buffers.
    """
    coords = pooled[["x", "y"]].to_numpy()
    tree = cKDTree(coords)
    pairs = tree.query_pairs(r=buffer_m)

    uf = UnionFind(len(pooled))
    for a, b in pairs:
        uf.union(a, b)

    cluster_ids = np.array([uf.find(i) for i in range(len(pooled))])
    out = pooled.copy()
    out["cluster_id"] = cluster_ids
    return out


# ----------------------------------------------------------------------------
# Set-overlap statistics
# ----------------------------------------------------------------------------


def cluster_membership_table(
    clustered: pd.DataFrame,
    configs: Iterable[str],
) -> pd.DataFrame:
    """Pivot to one row per cluster, columns = configs, values = probability.

    If a config contributes more than one candidate to a cluster (which would
    be unusual given upstream deduplication), the maximum probability is
    retained and a warning column is set.
    """
    configs = list(configs)
    grouped = clustered.groupby(["cluster_id", "config"]).agg(
        mound_probability=("mound_probability", "max"),
        n_in_config=("mound_probability", "size"),
    )
    wide = grouped["mound_probability"].unstack(level="config")
    counts = grouped["n_in_config"].unstack(level="config").fillna(0).astype(int)

    for c in configs:
        if c not in wide.columns:
            wide[c] = np.nan
        if c not in counts.columns:
            counts[c] = 0

    wide = wide[configs]
    wide["n_configs"] = wide.notna().sum(axis=1)
    wide["intra_config_collisions"] = (counts[configs] > 1).any(axis=1)
    wide["mean_prob"] = wide[configs].mean(axis=1)
    return wide.reset_index()


def overlap_summary(
    membership: pd.DataFrame,
    configs: list[str],
) -> dict:
    """Counts of clusters by sharing pattern (1..k configs)."""
    n_total_clusters = len(membership)
    by_n = membership["n_configs"].value_counts().sort_index().to_dict()
    by_n = {int(k): int(v) for k, v in by_n.items()}

    n_all = int((membership["n_configs"] == len(configs)).sum())
    n_unique = int((membership["n_configs"] == 1).sum())

    pooled_total = int(membership[configs].notna().sum().sum())
    shared_fraction = n_all * len(configs) / pooled_total if pooled_total else 0.0

    return {
        "n_clusters": n_total_clusters,
        "n_pooled_candidates": pooled_total,
        "clusters_by_sharing": by_n,
        "n_shared_by_all": n_all,
        "n_unique_to_one": n_unique,
        "fraction_pooled_in_full_overlap": shared_fraction,
        "intra_config_collision_count": int(
            membership["intra_config_collisions"].sum()
        ),
    }


# ----------------------------------------------------------------------------
# Pointwise probability comparison
# ----------------------------------------------------------------------------


def pairwise_correlations(
    membership: pd.DataFrame,
    configs: list[str],
) -> dict:
    """Pearson r and mean absolute difference for each pair of configs.

    Restricted per pair to clusters where both configs have a probability.
    """
    out: dict[str, dict] = {}
    for a, b in combinations(configs, 2):
        sub = membership[[a, b]].dropna()
        if len(sub) < 2:
            out[f"{a}__vs__{b}"] = {
                "n": int(len(sub)),
                "pearson_r": float("nan"),
                "mean_abs_diff": float("nan"),
                "mean_diff": float("nan"),
            }
            continue
        x = sub[a].to_numpy()
        y = sub[b].to_numpy()
        if x.std() == 0 or y.std() == 0:
            r = float("nan")
        else:
            r = float(np.corrcoef(x, y)[0, 1])
        out[f"{a}__vs__{b}"] = {
            "n": int(len(sub)),
            "pearson_r": r,
            "mean_abs_diff": float(np.mean(np.abs(x - y))),
            "mean_diff": float(np.mean(x - y)),
        }
    return out


def icc_2_1_absolute(matrix: np.ndarray) -> float:
    """ICC(2,1) absolute-agreement, two-way random effects, single rater.

    Parameters
    ----------
    matrix : (n_subjects, n_raters)
        Complete-case probability matrix; rows are clusters, columns are
        configs. NaNs are not allowed.

    Returns
    -------
    float
        ICC(2,1) absolute-agreement coefficient. NaN if degenerate.
    """
    if matrix.ndim != 2:
        raise ValueError("matrix must be 2-D")
    n, k = matrix.shape
    if n < 2 or k < 2:
        return float("nan")

    grand_mean = matrix.mean()
    row_means = matrix.mean(axis=1)
    col_means = matrix.mean(axis=0)

    ss_total = ((matrix - grand_mean) ** 2).sum()
    ss_rows = k * ((row_means - grand_mean) ** 2).sum()
    ss_cols = n * ((col_means - grand_mean) ** 2).sum()
    ss_err = ss_total - ss_rows - ss_cols

    df_rows = n - 1
    df_cols = k - 1
    df_err = (n - 1) * (k - 1)

    if df_rows <= 0 or df_err <= 0:
        return float("nan")

    ms_rows = ss_rows / df_rows
    ms_cols = ss_cols / df_cols
    ms_err = ss_err / df_err

    denom = ms_rows + (k - 1) * ms_err + k * (ms_cols - ms_err) / n
    if denom <= 0:
        return float("nan")
    return float((ms_rows - ms_err) / denom)


def complete_case_stats(
    membership: pd.DataFrame,
    configs: list[str],
) -> dict:
    """ICC and descriptive stats restricted to clusters present in all configs."""
    full = membership[membership["n_configs"] == len(configs)].copy()
    matrix = full[configs].to_numpy()
    if len(full) == 0:
        return {
            "n_complete_clusters": 0,
            "icc_2_1": float("nan"),
            "per_config_mean": {},
            "per_config_std": {},
            "max_pairwise_mean_abs_diff": float("nan"),
        }

    icc = icc_2_1_absolute(matrix)
    per_mean = {c: float(full[c].mean()) for c in configs}
    per_std = {c: float(full[c].std(ddof=1)) for c in configs}

    max_mad = 0.0
    for a, b in combinations(configs, 2):
        max_mad = max(max_mad, float(np.mean(np.abs(full[a] - full[b]))))

    return {
        "n_complete_clusters": int(len(full)),
        "icc_2_1": icc,
        "per_config_mean": per_mean,
        "per_config_std": per_std,
        "max_pairwise_mean_abs_diff": max_mad,
    }


# ----------------------------------------------------------------------------
# Verdict
# ----------------------------------------------------------------------------


def render_verdict(
    overlap: dict,
    complete: dict,
    optima: dict[str, dict],
) -> dict:
    """Apply the discriminating rule to overlap + ICC + threshold convergence."""
    shared_frac = overlap["fraction_pooled_in_full_overlap"]
    icc = complete["icc_2_1"]

    threshold_keys = {
        (round(o["vote_t"], 4), round(o["prob_t"], 4)) for o in optima.values()
    }
    thresholds_identical = len(threshold_keys) == 1

    if shared_frac < 0.6:
        verdict = "H-A"
        verdict_long = (
            "Set divergence: configs propose substantially different candidate "
            "pools; equivalence is averaged-out at the F1 level rather than "
            "pointwise."
        )
    elif not math.isnan(icc) and icc >= 0.9 and thresholds_identical:
        verdict = "H-B"
        verdict_long = (
            "Pointwise equivalence: spatially matched candidates receive "
            "near-identical verifier probabilities across all configs and the "
            "optimal threshold is the same. The verifier is proposer-blind for "
            "the same physical feature."
        )
    elif not math.isnan(icc) and icc >= 0.6:
        verdict = "H-C"
        verdict_long = (
            "Threshold compensation: matched candidates receive correlated but "
            "non-identical probabilities; the F1 sweep selects thresholds that "
            "cancel the residual differences."
        )
    else:
        verdict = "INCONCLUSIVE"
        verdict_long = (
            "The probe falls outside the discriminating regions: shared "
            "fraction is high but ICC is low, suggesting noisy verifier "
            "scoring even on the same crop. Worth a deeper look."
        )

    return {
        "verdict": verdict,
        "verdict_long": verdict_long,
        "shared_fraction": shared_frac,
        "icc_2_1": icc,
        "thresholds_identical": thresholds_identical,
        "distinct_threshold_count": len(threshold_keys),
    }


# ----------------------------------------------------------------------------
# Markdown rendering
# ----------------------------------------------------------------------------


def render_markdown(
    overlap: dict,
    pairwise: dict,
    complete: dict,
    optima: dict[str, dict],
    verdict: dict,
    configs: list[str],
    buffer_m: float,
) -> str:
    """Render the human-readable interpretation document."""
    lines: list[str] = []
    lines.append("# Verifier Independence Probe — H10/H12")
    lines.append("")
    lines.append(
        f"Buffer for cross-config spatial clustering: **{buffer_m:.0f} m** "
        "(matches the evaluation buffer)."
    )
    lines.append("")
    lines.append(f"## Verdict: **{verdict['verdict']}**")
    lines.append("")
    lines.append(verdict["verdict_long"])
    lines.append("")
    lines.append("## Set overlap")
    lines.append("")
    lines.append(f"- Total cross-config clusters: **{overlap['n_clusters']}**")
    lines.append(
        f"- Pooled per-config candidate rows: **{overlap['n_pooled_candidates']}**"
    )
    lines.append(
        f"- Clusters present in all {len(configs)} configs: "
        f"**{overlap['n_shared_by_all']}**"
    )
    lines.append(
        f"- Clusters unique to a single config: **{overlap['n_unique_to_one']}**"
    )
    lines.append(
        f"- Fraction of pooled rows lying in full-overlap clusters: "
        f"**{overlap['fraction_pooled_in_full_overlap']:.3f}**"
    )
    if overlap["intra_config_collision_count"]:
        lines.append(
            f"- Intra-config collisions (>1 candidate from a config in one "
            f"cluster): **{overlap['intra_config_collision_count']}**"
        )
    lines.append("")
    lines.append("### Sharing distribution")
    lines.append("")
    lines.append("| Configs sharing | Cluster count |")
    lines.append("|---|---|")
    for k in sorted(overlap["clusters_by_sharing"]):
        lines.append(f"| {k} | {overlap['clusters_by_sharing'][k]} |")
    lines.append("")
    lines.append("## Pointwise probability comparison (complete cases)")
    lines.append("")
    lines.append(f"- Complete-case clusters: **{complete['n_complete_clusters']}**")
    lines.append(f"- ICC(2,1) absolute agreement: **{complete['icc_2_1']:.4f}**")
    lines.append(
        f"- Maximum pairwise mean absolute difference: "
        f"**{complete['max_pairwise_mean_abs_diff']:.4f}**"
    )
    lines.append("")
    lines.append("### Per-config probability moments (complete cases)")
    lines.append("")
    lines.append("| Config | Mean | SD |")
    lines.append("|---|---|---|")
    for c in configs:
        m = complete["per_config_mean"].get(c, float("nan"))
        s = complete["per_config_std"].get(c, float("nan"))
        lines.append(f"| {c} | {m:.4f} | {s:.4f} |")
    lines.append("")
    lines.append("### Pairwise correlations and differences")
    lines.append("")
    lines.append("| Pair | n | Pearson r | Mean abs diff | Mean diff |")
    lines.append("|---|---|---|---|---|")
    for key, stats in pairwise.items():
        a, b = key.split("__vs__")
        lines.append(
            f"| {a} vs {b} | {stats['n']} | {stats['pearson_r']:.4f} | "
            f"{stats['mean_abs_diff']:.4f} | {stats['mean_diff']:+.4f} |"
        )
    lines.append("")
    lines.append("## Per-config sweep optima")
    lines.append("")
    lines.append("| Config | vote_t | prob_t | F1 | P | R |")
    lines.append("|---|---|---|---|---|---|")
    for c in configs:
        o = optima.get(c)
        if not o:
            continue
        lines.append(
            f"| {c} | {o['vote_t']} | {o['prob_t']:.2f} | {o['f1']:.4f} | "
            f"{o['p']:.4f} | {o['r']:.4f} |"
        )
    lines.append("")
    lines.append(
        f"Distinct (vote_t, prob_t) optima across configs: "
        f"**{verdict['distinct_threshold_count']}**"
    )
    lines.append("")
    return "\n".join(lines)


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


def run_probe(
    h10_dir: Path,
    sweep_path: Path,
    output_json: Path,
    output_md: Path,
    buffer_m: float,
    configs: list[str],
) -> dict:
    """End-to-end probe: load, cluster, summarise, render, write outputs."""
    tables = [load_config_table(h10_dir, c) for c in configs]
    pooled = pd.concat(tables, ignore_index=True)
    if pooled.empty:
        raise RuntimeError("No candidates loaded — check the H10 directory.")

    clustered = cluster_across_configs(pooled, buffer_m=buffer_m)
    membership = cluster_membership_table(clustered, configs=configs)

    overlap = overlap_summary(membership, configs=configs)
    pairwise = pairwise_correlations(membership, configs=configs)
    complete = complete_case_stats(membership, configs=configs)
    optima = load_sweep_optima(sweep_path)
    verdict = render_verdict(overlap, complete, optima)

    payload = {
        "buffer_m": buffer_m,
        "configs": configs,
        "overlap": overlap,
        "pairwise": pairwise,
        "complete_case": complete,
        "sweep_optima": optima,
        "verdict": verdict,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2))

    md = render_markdown(
        overlap=overlap,
        pairwise=pairwise,
        complete=complete,
        optima=optima,
        verdict=verdict,
        configs=configs,
        buffer_m=buffer_m,
    )
    output_md.write_text(md)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--h10-dir",
        type=Path,
        default=Path("outputs/h10"),
        help="Root H10 outputs directory.",
    )
    parser.add_argument(
        "--sweep",
        type=Path,
        default=Path("results/h10/sweep_results.json"),
        help="Per-config (vote_t, prob_t, F1) sweep results JSON.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("results/h10/verifier_independence_probe.json"),
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("results/h10/verifier_independence_probe.md"),
    )
    parser.add_argument(
        "--buffer-m",
        type=float,
        default=DEFAULT_BUFFER_M,
        help="Cross-config spatial clustering radius in metres.",
    )
    parser.add_argument(
        "--configs",
        nargs="+",
        default=list(DEFAULT_CONFIGS),
        help="Pool config directory names under verifier-crops/ and verified/.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_probe(
        h10_dir=args.h10_dir,
        sweep_path=args.sweep,
        output_json=args.output_json,
        output_md=args.output_md,
        buffer_m=args.buffer_m,
        configs=list(args.configs),
    )
    v = payload["verdict"]
    print(
        f"Verdict: {v['verdict']}  shared_frac={v['shared_fraction']:.3f}  "
        f"ICC={v['icc_2_1']:.4f}  thresholds_identical={v['thresholds_identical']}"
    )
    print(f"Wrote {args.output_json}")
    print(f"Wrote {args.output_md}")


if __name__ == "__main__":
    main()
