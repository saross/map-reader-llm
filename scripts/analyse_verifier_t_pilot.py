"""Compute failure rates and Wilson 95% CIs for the Stage A verifier-temperature pilot.

Reads three ``probabilities.json`` outputs (T=0.0 baseline reused; T=0.5 and T=1.0
freshly run) plus the canonical 4-of-5 consensus GeoJSON, and reports per-T
failure counts using the Obs 281-corrected formula:

    n_failures = len(consensus_candidates) - len(probabilities['results'])

Failure rate = n_failures / n_candidates, with a Wilson 95% confidence interval
from ``scipy.stats.binomtest``.

Usage
-----
    python3 scripts/analyse_verifier_t_pilot.py

Outputs a Markdown table to stdout and writes ``results/verifier-t-pilot/per-t-stats.json``.
"""

from __future__ import annotations

import json
from pathlib import Path

from scipy.stats import binomtest

# Repository root assumed to be the script's grandparent (scripts/ -> repo).
REPO = Path(__file__).resolve().parent.parent

CONSENSUS_GEOJSON = REPO / "outputs/gs/gold-standard-v2/consensus/consensus-4of5.geojson"

PROB_PATHS: dict[str, Path] = {
    "0.0": REPO / "outputs/gs/gold-standard-v2/verified-v1/probabilities.json",
    "0.5": REPO / "outputs/verifier-t-pilot/T0.5/probabilities.json",
    "1.0": REPO / "outputs/verifier-t-pilot/T1.0/probabilities.json",
}

META_PATHS: dict[str, Path] = {
    "0.0": REPO / "outputs/gs/gold-standard-v2/verified-v1/run.meta.json",
    "0.5": REPO / "outputs/verifier-t-pilot/T0.5/run.meta.json",
    "1.0": REPO / "outputs/verifier-t-pilot/T1.0/run.meta.json",
}

OUTPUT_DIR = REPO / "results/verifier-t-pilot"
STATS_JSON = OUTPUT_DIR / "per-t-stats.json"


def count_candidates(geojson_path: Path) -> int:
    """Return the number of features in a GeoJSON FeatureCollection."""
    with geojson_path.open() as fh:
        data = json.load(fh)
    return len(data["features"])


def count_successes(prob_path: Path) -> int:
    """Return the number of successful verifier entries in a probabilities.json file.

    The pipeline writes only successful entries to the ``results`` mapping; missing
    candidates are treated as failures per Obs 281.
    """
    with prob_path.open() as fh:
        data = json.load(fh)
    return len(data["results"])


def get_cost(meta_path: Path) -> float | None:
    """Return total cost in USD from a run.meta.json, or ``None`` if absent."""
    if not meta_path.exists():
        return None
    with meta_path.open() as fh:
        meta = json.load(fh)
    cost = meta.get("cost_estimate", {}).get("total_cost_usd")
    return float(cost) if cost is not None else None


def wilson_ci(failures: int, total: int) -> tuple[float, float]:
    """Compute the Wilson 95% CI for a binomial proportion via ``scipy.stats.binomtest``."""
    result = binomtest(failures, total)
    ci = result.proportion_ci(method="wilson")
    return ci.low, ci.high


def main() -> None:
    """Compute and report per-T failure statistics for the Stage A pilot."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    n_candidates = count_candidates(CONSENSUS_GEOJSON)
    print(f"Consensus 4-of-5 candidate count: {n_candidates}")

    rows: list[dict[str, object]] = []
    for t_str, prob_path in PROB_PATHS.items():
        if not prob_path.exists():
            print(f"  [skip] T={t_str}: {prob_path} missing")
            continue
        n_success = count_successes(prob_path)
        n_failures = n_candidates - n_success
        rate = n_failures / n_candidates
        low, high = wilson_ci(n_failures, n_candidates)
        cost = get_cost(META_PATHS[t_str])
        rows.append({
            "temperature": float(t_str),
            "n_candidates": n_candidates,
            "n_success": n_success,
            "n_failures": n_failures,
            "failure_rate": rate,
            "wilson_ci_low": low,
            "wilson_ci_high": high,
            "cost_usd": cost,
        })

    print()
    print("| T   | candidates | success | failures | rate    | Wilson 95% CI       | cost USD |")
    print("|-----|------------|---------|----------|---------|---------------------|----------|")
    for row in rows:
        cost_str = f"${row['cost_usd']:.4f}" if row["cost_usd"] is not None else "n/a"
        print(
            f"| {row['temperature']:.1f} | {row['n_candidates']:>10} | {row['n_success']:>7} "
            f"| {row['n_failures']:>8} | {row['failure_rate']:.4%} "
            f"| [{row['wilson_ci_low']:.4%}, {row['wilson_ci_high']:.4%}] | {cost_str:>8} |"
        )

    # Decision-rule output.
    print()
    if len(rows) == 3:
        rates = [r["failure_rate"] for r in rows]
        cis = [(r["wilson_ci_low"], r["wilson_ci_high"]) for r in rows]
        # Pairwise overlap test: do all three CIs share at least one common value?
        # We approximate "all overlapping" as max(low) <= min(high).
        all_overlap = max(c[0] for c in cis) <= min(c[1] for c in cis)
        max_rate = max(rates)
        min_rate = min(r for r in rates if r > 0) if any(r > 0 for r in rates) else 0.0
        ratio = max_rate / min_rate if min_rate > 0 else float("inf")
        print(f"Pairwise CI overlap (all three): {all_overlap}")
        print(f"Max/min rate ratio (excluding zeros): {ratio:.2f}")
        if all_overlap and ratio < 2.0:
            verdict = "NOT supported (CIs overlap, no >2x ratio): close pilot."
        elif ratio >= 2.0:
            verdict = "Stage B candidate: one T point > 2x another's rate. Flag for Shawn (do NOT auto-launch)."
        else:
            verdict = "Borderline: CIs overlap but a directional trend is visible. Describe and recommend; let Shawn decide."
        print(f"Decision: {verdict}")
    else:
        print("Decision skipped: not all three T points present.")

    with STATS_JSON.open("w") as fh:
        json.dump({"rows": rows}, fh, indent=2)
    print()
    print(f"Wrote {STATS_JSON.relative_to(REPO)}")


if __name__ == "__main__":
    main()
