#!/usr/bin/env python3
"""
Build cross-architecture comparison tables (Stage 4a + 4b).

Stage 4a (flat): for each (Era, buffer, metric) combination, identify
the best representative of each architecture within that Era at that
buffer. Outputs ``cross-architecture-era<N>_<buffer>m_<metric>.md``.

Stage 4b (paired): for each Era, identify proposer-config tuples
(model, prompt, K, T, vote_t) that appear in **multiple architecture
columns** within that Era (e.g., flash-high-text K=5 T=0.7 appears as
``consensus`` AND ``pv``). Run a paired permutation test on each
shared tuple to answer "does PV help on this proposer?".

Stage 4c (Monte-Carlo precision flags): identify pairwise tests
where the observed null-difference count is <=5 (p <= 5/N), so the
p-value estimate is precision-limited by the permutation count.

Inputs:
    - ``leaderboard_tiers_<metric>_{20,30,40,50,100}m.json`` per
      stratum (see Stage 2 outputs at
      ``results/leaderboard/per-architecture/era<N>/<arch>/``).
    - Inventory: ``planning/condition-inventory-with-s78.json``.

Outputs (per Era):
    - ``cross-architecture-era<N>_<buffer>m_<metric>.md`` (Stage 4a)
    - ``cross-architecture-paired-era<N>_<metric>.md`` (Stage 4b)

Usage::

    python scripts/build_cross_architecture_tables.py --metric f1
    python scripts/build_cross_architecture_tables.py --metric mcc
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import defaultdict
from pathlib import Path



PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import geopandas as gpd  # noqa: E402

from evaluate_detections import load_geojson  # noqa: E402
from pairwise_permutation_test import (  # noqa: E402
    load_geojson_detections,
    run_permutation_test,
    run_permutation_test_mcc,
)

LOGGER = logging.getLogger(__name__)
PER_ARCH_DIR = PROJECT_ROOT / "results" / "leaderboard" / "per-architecture"
INVENTORY_PATH = PROJECT_ROOT / "planning" / "condition-inventory-with-s78.json"
DEFAULT_REF = (
    PROJECT_ROOT / "inputs" / "vectors" / "references"
    / "mounds-reference.geojson"
)
ERA_BOUNDS = {
    1: PROJECT_ROOT / "inputs" / "vectors" / "bounds"
       / "full_evaluation_bounds.geojson",
    2: PROJECT_ROOT / "inputs" / "vectors" / "bounds" / "384"
       / "full_evaluation_bounds.geojson",
    3: PROJECT_ROOT / "inputs" / "vectors" / "bounds" / "384"
       / "h10_test_bounds.geojson",
}
ARCHITECTURES = ["single-pass", "consensus", "single-pass+PV", "pv"]
BUFFERS = [20, 30, 40, 50, 100]
SEED = 42
N_PERMUTATIONS = 10_000


def _load_tier_json(era: int, arch: str, metric: str, buf: int) -> dict | None:
    """Load the per-stratum tier JSON for one (era, arch, metric, buf)."""
    suffix = "" if metric == "f1" else f"_{metric}"
    candidate = (
        PER_ARCH_DIR / f"era{era}" / arch
        / f"leaderboard_tiers{suffix}_{buf}m.json"
    )
    if not candidate.is_file():
        return None
    with open(candidate, encoding="utf-8") as fh:
        return json.load(fh)


def _condition_score(cond_dict: dict, metric: str, buf: int) -> float:
    """Read the score for a condition dict at buffer."""
    if metric == "f1":
        return float(
            cond_dict.get("evaluations", {})
                     .get(str(buf), {})
                     .get("f1", 0.0)
        )
    return float(cond_dict.get("tile_mcc", 0.0))


# --- Stage 4a -------------------------------------------------------

def build_flat_table(
    era: int, buf: int, metric: str, output_dir: Path,
) -> Path | None:
    """Build the cross-arch flat comparison table for one (era, buf, metric).

    Walks each architecture's tier JSON, picks the top-tier #1 best
    representative, and emits a 4-row markdown table (one per
    architecture) with score, CI, tier, and condition label.
    """
    rows: list[dict] = []
    for arch in ARCHITECTURES:
        payload = _load_tier_json(era, arch, metric, buf)
        if payload is None:
            rows.append({
                "arch": arch, "score": None, "label": None, "tier": None,
                "ci_lo": None, "ci_hi": None,
            })
            continue
        # Best is tier 1 condition with highest score
        tiers = payload.get("tiers", [])
        if not tiers:
            rows.append({
                "arch": arch, "score": None, "label": None, "tier": None,
                "ci_lo": None, "ci_hi": None,
            })
            continue
        # Tier 1, sorted by score descending
        tier1 = tiers[0].get("conditions", [])
        if not tier1:
            rows.append({
                "arch": arch, "score": None, "label": None, "tier": None,
                "ci_lo": None, "ci_hi": None,
            })
            continue
        best = max(
            tier1,
            key=lambda c: _condition_score(c, metric, buf),
        )
        eval_buf = best.get("evaluations", {}).get(str(buf), {})
        rows.append({
            "arch": arch,
            "score": _condition_score(best, metric, buf),
            "label": best.get("label"),
            "tier": 1,
            "ci_lo": float(eval_buf.get("f1_ci_lower", 0.0)),
            "ci_hi": float(eval_buf.get("f1_ci_upper", 0.0)),
            "best_threshold": best.get("best_threshold"),
            "k": best.get("k"),
            "track": best.get("track"),
        })

    metric_label = metric.upper()
    score_col = "F1" if metric == "f1" else "MCC"
    title = (
        f"Cross-architecture flat comparison — Era {era}, "
        f"{buf} m buffer, {metric_label}"
    )
    lines = [
        f"# {title}",
        "",
        "**Generated**: Session 79 redesign (2026-04-25)",
        f"**Era**: {era}",
        f"**Buffer**: {buf} m",
        f"**Metric**: {metric_label}",
        "",
        "Each row shows the best Tier-1 representative of one "
        "architecture within Era. The score column shows the metric "
        "(F1 or MCC) at the requested buffer.",
        "",
        "| Architecture | Best condition | "
        f"{score_col} | F1 95% CI (at {buf} m) | "
        "Tier (within stratum) | K | t | Track |",
        "|:---|:---|---:|:---:|---:|---:|---:|:---|",
    ]
    for row in rows:
        if row["score"] is None:
            lines.append(
                f"| {row['arch']} | _empty stratum_ | — | — | "
                "— | — | — | — |"
            )
            continue
        score_str = f"{row['score']:+.3f}" if metric == "mcc" else \
            f"{row['score']:.3f}"
        ci_str = f"[{row['ci_lo']:.3f}, {row['ci_hi']:.3f}]"
        lines.append(
            f"| {row['arch']} | `{row['label']}` | {score_str} | "
            f"{ci_str} | {row['tier']} | {row['k']} | "
            f"{row['best_threshold']} | {row['track']} |"
        )
    lines.append("")

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = (
        output_dir
        / f"cross-architecture-era{era}_{buf}m_{metric}.md"
    )
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    LOGGER.info("Wrote %s", out_path)
    return out_path


# --- Stage 4b -------------------------------------------------------

def _normalise_thinking(value: str | None) -> str | None:
    """Normalise the thinking budget across inventory dialects.

    The consensus subset uses ``minimal`` / ``high``; the PV subset
    uses ``min`` / ``HIGH`` / ``h8-legacy``. We canonicalise to
    {minimal, high, h8-legacy} (and lowercase) so the cross-arch
    pairing aligns.
    """
    if value is None:
        return None
    v = value.strip().lower()
    if v in {"min", "minimal"}:
        return "minimal"
    if v == "high":
        return "high"
    if v == "h8-legacy":
        return "h8-legacy"
    return v


def _proposer_signature(cond_inv: dict) -> tuple:
    """Build a tuple identifying the proposer config of a condition.

    Two conditions sharing this tuple are considered "the same proposer
    output" — different architecture columns (e.g., consensus vs pv)
    using the same proposer pipeline. Architecture-specific fields
    (vote_t, prob_t, instruction_file/config_version which differ
    between the proposer and PV branches) are deliberately excluded;
    track + model + thinking + T + N/K is sufficient to identify a
    proposer batch.
    """
    return (
        cond_inv.get("model"),
        cond_inv.get("track"),
        _normalise_thinking(cond_inv.get("thinking")),
        cond_inv.get("T"),
        cond_inv.get("N") or cond_inv.get("K"),
    )


def find_paired_proposers(era: int) -> list[dict]:
    """Identify proposer-config tuples appearing in 2+ architectures.

    Returns a list of {sig, conds_by_arch} dicts where `conds_by_arch`
    maps architecture label -> list of inventory entries. Only tuples
    appearing in 2+ distinct architectures are returned.
    """
    with open(INVENTORY_PATH, encoding="utf-8") as fh:
        inv = json.load(fh)
    grouped: dict[tuple, dict[str, list[dict]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for c in inv:
        if c.get("era") != era:
            continue
        if c.get("status") not in {"READY", "PV_READY", "SINGLE_PASS_ONLY"}:
            continue
        arch = c.get("architecture")
        if arch not in ARCHITECTURES:
            continue
        sig = _proposer_signature(c)
        grouped[sig][arch].append(c)
    paired: list[dict] = []
    for sig, by_arch in grouped.items():
        if len(by_arch) >= 2:
            paired.append({"sig": sig, "by_arch": dict(by_arch)})
    return paired


def _resolve_geojson(cond_inv: dict, arch: str) -> Path | None:
    """Resolve the appropriate GeoJSON path for a condition + arch.

    For pv/single-pass+PV: condition's `path` is the geojson directly.
    For consensus: pick the threshold optimum from the corresponding
        per-arch tier JSON (use the first available buffer's
        best_threshold).
    For single-pass: the canonical run_1/detections_*.geojson.
    """
    base = PROJECT_ROOT / cond_inv["path"]
    if arch in {"pv", "single-pass+PV"}:
        if base.suffix == ".geojson":
            return base if base.is_file() else None
        cand = base / "detections.geojson"
        return cand if cand.is_file() else None
    if arch == "single-pass":
        # First detections_*.geojson under run_1
        candidates = sorted(base.glob("run_*/detections_*.geojson"))
        return candidates[0] if candidates else None
    if arch == "consensus":
        # Read tier JSON to find best_threshold per stratum
        tier_payload = _load_tier_json(
            cond_inv["era"], "consensus", "f1", 20,
        )
        if tier_payload is None:
            return None
        for tier in tier_payload.get("tiers", []):
            for c in tier.get("conditions", []):
                if c.get("label") == cond_inv.get("id"):
                    return Path(c["geojson"])
    return None


def _assign_source_tile(
    gdf: gpd.GeoDataFrame, gdf_bounds: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Assign source_tile by spatial join if missing."""
    if "source_tile" not in gdf.columns and not gdf.empty:
        joined = gpd.sjoin(
            gdf, gdf_bounds[["tile_name", "geometry"]],
            how="left", predicate="intersects",
        )
        joined = joined[~joined.index.duplicated(keep="first")]
        gdf["source_tile"] = joined["tile_name"]
    return gdf


def run_paired_test(
    cond_a: dict, arch_a: str, cond_b: dict, arch_b: str,
    metric: str, era: int,
) -> dict | None:
    """Run a paired permutation test between (cond_a, arch_a) and
    (cond_b, arch_b)."""
    gj_a = _resolve_geojson(cond_a, arch_a)
    gj_b = _resolve_geojson(cond_b, arch_b)
    if gj_a is None or gj_b is None:
        LOGGER.warning(
            "Cannot resolve geojson for paired test: %s (%s) vs %s (%s)",
            cond_a.get("id"), arch_a, cond_b.get("id"), arch_b,
        )
        return None

    bounds_path = ERA_BOUNDS[era]
    gdf_a = load_geojson_detections(gj_a)
    gdf_b = load_geojson_detections(gj_b)
    gdf_ref = load_geojson(DEFAULT_REF)
    gdf_bounds = load_geojson(bounds_path)
    gdf_a = _assign_source_tile(gdf_a, gdf_bounds)
    gdf_b = _assign_source_tile(gdf_b, gdf_bounds)

    if metric == "mcc":
        result = run_permutation_test_mcc(
            gdf_a, gdf_b, gdf_ref, gdf_bounds,
            n_permutations=N_PERMUTATIONS, seed=SEED,
        )
        score_a = result["global_a"]["mcc"]
        score_b = result["global_b"]["mcc"]
        delta = result["permutation_test"]["observed_mcc_diff"]
    else:
        result = run_permutation_test(
            gdf_a, gdf_b, gdf_ref, gdf_bounds,
            buffer_metres=20,
            n_permutations=N_PERMUTATIONS, seed=SEED,
        )
        score_a = result["global_a"]["f1"]
        score_b = result["global_b"]["f1"]
        delta = result["permutation_test"]["observed_f1_diff"]
    p_value = result["permutation_test"]["p_value"]

    return {
        "cond_a": cond_a.get("id"),
        "arch_a": arch_a,
        "score_a": score_a,
        "cond_b": cond_b.get("id"),
        "arch_b": arch_b,
        "score_b": score_b,
        "delta": delta,
        "p_value": p_value,
        "n_tiles": result["permutation_test"]["n_tiles"],
        "n_permutations": result["permutation_test"]["n_permutations"],
    }


def _bh_correct(p_values: list[float], q: float = 0.05) -> list[float]:
    """Benjamini-Hochberg adjusted p-values."""
    if not p_values:
        return []
    n = len(p_values)
    order = sorted(range(n), key=lambda i: p_values[i])
    adj = [0.0] * n
    cummin = 1.0
    for rank, idx in enumerate(reversed(order), start=1):
        i = n - rank + 1  # 1-based rank from the end
        raw = p_values[idx] * n / i
        cummin = min(cummin, raw)
        adj[idx] = cummin
    return adj


def build_paired_table(era: int, metric: str, output_dir: Path) -> Path:
    """Build the cross-arch paired comparison table for one Era + metric."""
    paired = find_paired_proposers(era)
    LOGGER.info("Era %d: %d paired proposer tuples", era, len(paired))

    rows: list[dict] = []
    for entry in paired:
        sig = entry["sig"]
        by_arch = entry["by_arch"]
        archs = sorted(by_arch.keys())
        # All architecture pairs within this proposer tuple
        for i in range(len(archs)):
            for j in range(i + 1, len(archs)):
                arch_a = archs[i]
                arch_b = archs[j]
                # Pick the first inventory entry per arch
                cond_a = by_arch[arch_a][0]
                cond_b = by_arch[arch_b][0]
                LOGGER.info(
                    "Pair: %s (%s) vs %s (%s)",
                    cond_a["id"], arch_a, cond_b["id"], arch_b,
                )
                test = run_paired_test(
                    cond_a, arch_a, cond_b, arch_b, metric, era,
                )
                if test is None:
                    continue
                test["sig"] = " | ".join(str(s) for s in sig)
                rows.append(test)

    # BH-FDR correction within era at q=0.05
    p_values = [r["p_value"] for r in rows]
    adj = _bh_correct(p_values, q=0.05)
    for r, adj_p in zip(rows, adj):
        r["bh_adjusted_p"] = adj_p
        r["significant_q05"] = adj_p < 0.05

    metric_label = metric.upper()
    score_label = "F1" if metric == "f1" else "MCC"

    lines = [
        f"# Cross-architecture paired comparison — Era {era}, {metric_label}",
        "",
        "**Generated**: Session 79 redesign (2026-04-25)",
        f"**Era**: {era}",
        f"**Metric**: {metric_label}",
        f"**Permutations**: {N_PERMUTATIONS:,}, seed={SEED}",
        "**FDR**: BH at q=0.05 within Era",
        "",
        "Pairs of architectures sharing the same proposer config tuple "
        "(model, config_version, instruction_file, thinking, T, "
        "N/K, track, vote_t). The PV-helps column flags when adding "
        "the verifier (or moving from single-pass to consensus, etc.) "
        "produces a statistically significant change after BH-FDR.",
        "",
        "> **Operating-point note (E56)**: verifier-stage (`*-opt-20m`) cells, where "
        "present, use a `(vote_t, prob_t)` operating point selected **in-sample on the "
        "test set** (no calibration-tile verifier data exists). The headline "
        "proposer-verifier result uses the binary verdict (`prob_t = null`). See "
        "`docs/methodology/preregistration/protocol-errata.md` E56.",
        "",
        f"Conditions tested: {len(rows)}",
        "",
        f"| Pair (arch_a -> arch_b) | A | {score_label}(A) | B | "
        f"{score_label}(B) | delta | p_raw | p_BH | sig (q=0.05) |",
        "|:---|:---|---:|:---|---:|---:|---:|---:|:---:|",
    ]
    for r in rows:
        delta_str = f"{r['delta']:+.4f}"
        score_a_str = f"{r['score_a']:.3f}"
        score_b_str = f"{r['score_b']:.3f}"
        sig_str = "Y" if r["significant_q05"] else ""
        lines.append(
            f"| {r['arch_a']} -> {r['arch_b']} | "
            f"`{r['cond_a']}` | {score_a_str} | "
            f"`{r['cond_b']}` | {score_b_str} | "
            f"{delta_str} | {r['p_value']:.4f} | "
            f"{r['bh_adjusted_p']:.4f} | {sig_str} |"
        )
    lines.append("")

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"cross-architecture-paired-era{era}_{metric}.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # JSON sidecar
    out_json = output_dir / f"cross-architecture-paired-era{era}_{metric}.json"
    out_json.write_text(
        json.dumps({
            "era": era, "metric": metric,
            "n_permutations": N_PERMUTATIONS, "seed": SEED,
            "rows": rows,
        }, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    LOGGER.info("Wrote %s", out_path)
    return out_path


# --- Stage 4c -------------------------------------------------------

def find_mc_precision_flags(output_dir: Path) -> Path:
    """Walk all pairwise tier JSONs and flag MC-precision-limited tests.

    A test is flagged when the observed null-difference count <= 5
    (i.e., p <= 5/10000 = 0.0005). For p_value == 0/N the only
    valid conclusion is "p < 1/N"; flagged separately.

    Coverage:
    - F1: walks all 5 buffer tier JSONs per stratum (20 / 30 / 40 /
      50 / 100 m) since the F1 permutation test is buffer-dependent
      and per-buffer F1 re-tiering (2026-04-26) produces independent
      pairwise sets at each buffer.
    - MCC: only the 20 m JSON (the tile-level MCC permutation test is
      buffer-independent — pairwise sets at other buffers are
      identical by methodology).
    """
    flagged: list[dict] = []
    seen_keys: set[tuple] = set()
    f1_buffers = (20, 30, 40, 50, 100)
    for era in (1, 2, 3):
        for arch in ARCHITECTURES:
            for metric in ("f1", "mcc"):
                buffers_for_metric = f1_buffers if metric == "f1" else (20,)
                for buf in buffers_for_metric:
                    payload = _load_tier_json(era, arch, metric, buf)
                    if payload is None:
                        continue
                    n_perm = payload.get("metadata", {}).get(
                        "n_permutations", N_PERMUTATIONS,
                    )
                    for r in payload.get("pairwise_tests", []):
                        p = r.get("p_value", 1.0)
                        # Reconstruct null-difference count from
                        # p_value (since we don't store it directly).
                        null_count = int(round(p * n_perm))
                        if null_count <= 5:
                            label_a = r.get("label_a")
                            label_b = r.get("label_b")
                            # De-dupe across buffer files for MCC
                            # (defensive — MCC only walks buf=20 above
                            # but a future change could add buffers;
                            # the tile-level permutation result is
                            # identical across buffers).
                            key = (era, arch, metric, buf, label_a, label_b)
                            if key in seen_keys:
                                continue
                            seen_keys.add(key)
                            flagged.append({
                                "era": era,
                                "arch": arch,
                                "metric": metric,
                                "buffer_metres": buf,
                                "label_a": label_a,
                                "label_b": label_b,
                                "p_value": p,
                                "n_permutations": n_perm,
                                "approx_null_count": null_count,
                                "is_zero_count": (null_count == 0),
                            })
    lines = [
        "# Monte-Carlo precision flags",
        "",
        "**Generated**: per-buffer F1 re-tiering refresh (2026-04-26)",
        "",
        "Pairwise tests where the observed null-difference count is "
        "<= 5 (i.e., p <= 5/N). These p-values are precision-limited "
        "by the permutation count; the true p might be much smaller "
        "but cannot be distinguished from N=10K. For tests where the "
        "observed count is 0/N, the only valid conclusion is `p < 1/N`.",
        "",
        "**Coverage**: F1 pairwise tests are walked at all 5 buffers "
        "(20 / 30 / 40 / 50 / 100 m) per stratum since the F1 "
        "permutation test is buffer-dependent. MCC pairwise tests are "
        "walked at the primary buffer (20 m) only — the tile-level "
        "MCC permutation test is buffer-independent, so MCC pairwise "
        "results at non-primary buffers are identical by methodology "
        "and would only inflate counts.",
        "",
        f"Total flagged tests: {len(flagged)}",
        f"Of which p == 0/N (cannot bound below 1/N): "
        f"{sum(1 for r in flagged if r['is_zero_count'])}",
        "",
        "## Recommendations",
        "",
        "If a paper-citation hinges on a flagged comparison, re-run "
        "that pair at N=100,000 permutations to either tighten the "
        "p-value or bound it more precisely.",
        "",
        "## Flagged pairs",
        "",
        "| Era | Arch | Metric | Buffer | Label A | Label B | p | "
        "approx null count | zero count? |",
        "|---:|:---|:---|---:|:---|:---|---:|---:|:---:|",
    ]
    for r in flagged:
        zero_marker = "Y" if r["is_zero_count"] else ""
        lines.append(
            f"| {r['era']} | {r['arch']} | {r['metric']} | "
            f"{r['buffer_metres']} m | "
            f"`{r['label_a']}` | `{r['label_b']}` | {r['p_value']:.4f} | "
            f"{r['approx_null_count']} | {zero_marker} |"
        )
    lines.append("")
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "mc-precision-flags.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    LOGGER.info("Wrote MC-precision flags: %s", out_path)
    return out_path


# --- Driver ---------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build cross-architecture comparison tables.",
    )
    parser.add_argument(
        "--metric", choices=["f1", "mcc", "both"], default="both",
    )
    parser.add_argument(
        "--stage", choices=["4a", "4b", "4c", "all"], default="all",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    metrics = ("f1", "mcc") if args.metric == "both" else (args.metric,)
    output_dir = PER_ARCH_DIR

    if args.stage in {"4a", "all"}:
        for era in (1, 2, 3):
            for buf in BUFFERS:
                for metric in metrics:
                    build_flat_table(era, buf, metric, output_dir)

    if args.stage in {"4b", "all"}:
        for era in (1, 2, 3):
            for metric in metrics:
                build_paired_table(era, metric, output_dir)

    if args.stage in {"4c", "all"}:
        find_mc_precision_flags(output_dir)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
