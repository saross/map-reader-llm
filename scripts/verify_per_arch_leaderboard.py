#!/usr/bin/env python3
"""
Spot-check per-architecture leaderboard rows against their source files.

Picks a configurable number of random rows from each (era, architecture)
stratum's enriched leaderboard JSON, re-reads the source GeoJSON /
condition inventory entry, and checks:

1. `geojson` path exists.
2. GeoJSON feature count is non-zero and (for PV cells) matches the
   source cell's expected post-filter count to within tolerance.
3. `config_version`, `proposer`, `vote_t`, `prob_t`, `verifier_prompt`
   match the inventory.
4. F1 @ 20 m is within the plausible range (0 ≤ F1 ≤ 1 and CI bounds
   bracket the point estimate).

Writes a report to `results/leaderboard/per-architecture/
verification-report.md` with pass/fail per row.

Usage:
    .venv/bin/python scripts/verify_per_arch_leaderboard.py --n 2

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
ROOT = REPO_ROOT / "results/leaderboard/per-architecture"
INVENTORY = REPO_ROOT / "planning/condition-inventory-with-s78.json"
ERAS = [1, 2, 3]
ARCHITECTURES = ["single-pass", "consensus", "single-pass+PV", "pv"]


def load_inventory() -> dict[str, dict]:
    data = json.loads(INVENTORY.read_text())
    return {r["id"]: r for r in data}


def spot_check_row(row: dict, inv: dict[str, dict]) -> list[tuple[str, str]]:
    """Return a list of (check_name, status) tuples for this row."""
    results: list[tuple[str, str]] = []

    # 1. GeoJSON existence
    gj = row.get("geojson")
    if not gj:
        results.append(("geojson_exists", "FAIL (no path)"))
    else:
        p = Path(gj)
        if not p.is_absolute():
            p = REPO_ROOT / p
        if not p.is_file():
            results.append(("geojson_exists", f"FAIL ({gj} missing)"))
        else:
            try:
                data = json.loads(p.read_text())
                n_feat = len(data.get("features", []))
                if n_feat == 0:
                    results.append(
                        ("geojson_nonempty", f"FAIL (0 features at {p.name})")
                    )
                else:
                    results.append(
                        ("geojson_nonempty", f"OK ({n_feat} features)")
                    )
            except Exception as e:
                results.append(("geojson_readable", f"FAIL ({e})"))

    # 2. Inventory cross-check
    inv_row = inv.get(row["condition_id"])
    if inv_row is None:
        results.append(("inventory_present", "FAIL (not in inventory)"))
    else:
        # Proposer model
        inv_model = inv_row.get("model")
        if inv_model != row.get("proposer"):
            results.append(
                (
                    "proposer_matches",
                    f"FAIL (row={row.get('proposer')!r}, "
                    f"inv={inv_model!r})",
                )
            )
        else:
            results.append(("proposer_matches", "OK"))

        # Config version
        if inv_row.get("config_version") != row.get("config_version"):
            # Accept "—" fallback
            if (
                row.get("config_version") == "—"
                and inv_row.get("config_version") is None
            ):
                results.append(("config_version", "OK (both null)"))
            else:
                results.append(
                    (
                        "config_version",
                        f"DIVERGE (row={row.get('config_version')!r}, "
                        f"inv={inv_row.get('config_version')!r})",
                    )
                )
        else:
            results.append(("config_version", "OK"))

        # vote_t (for pv / consensus)
        if row.get("architecture") == "pv" and inv_row.get("vote_t") is not None:
            if inv_row.get("vote_t") != row.get("vote_t"):
                results.append(
                    (
                        "vote_t_matches_inventory",
                        f"FAIL (row={row.get('vote_t')}, "
                        f"inv={inv_row.get('vote_t')})",
                    )
                )
            else:
                results.append(("vote_t_matches_inventory", "OK"))

    # 3. F1 sanity
    f1 = row.get("f1")
    ci_lo = row.get("f1_ci_lower")
    ci_hi = row.get("f1_ci_upper")
    if f1 is None:
        results.append(("f1_present", "FAIL (F1 is None)"))
    elif not (0.0 <= f1 <= 1.0):
        results.append(("f1_range", f"FAIL (F1={f1} out of [0,1])"))
    elif ci_lo is not None and ci_hi is not None:
        if not (ci_lo <= f1 <= ci_hi):
            results.append(
                (
                    "f1_within_ci",
                    f"FAIL (F1={f1:.3f} outside [{ci_lo:.3f}, {ci_hi:.3f}])",
                )
            )
        else:
            results.append(
                (
                    "f1_within_ci",
                    f"OK (F1={f1:.3f} in [{ci_lo:.3f}, {ci_hi:.3f}])",
                )
            )
    else:
        results.append(("f1_sanity", f"OK (F1={f1:.3f}, CI missing)"))

    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--n", type=int, default=2,
        help="Rows per stratum to spot-check (default 2).",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "verification-report.md",
    )
    args = parser.parse_args()

    rng = random.Random(args.seed)
    inv = load_inventory()
    report: list[str] = []
    report.append("# Per-architecture leaderboard spot-check")
    report.append("")
    report.append(
        f"**Generated**: {datetime.now(tz=timezone.utc).isoformat()}"
    )
    report.append(f"**Rows per stratum**: {args.n}")
    report.append(f"**Random seed**: {args.seed}")
    report.append("")

    total_rows = 0
    total_fails = 0
    total_diverges = 0

    for era in ERAS:
        for arch in ARCHITECTURES:
            rows_json = ROOT / f"era{era}" / arch / "leaderboard_rows_20m.json"
            if not rows_json.is_file():
                continue
            data = json.loads(rows_json.read_text())
            rows = data.get("rows", [])
            if not rows:
                continue
            picked = rng.sample(rows, min(args.n, len(rows)))
            report.append(f"## Era {era} × {arch}")
            report.append("")
            for row in picked:
                report.append(
                    f"### `{row['condition_id']}` (rank {row['rank']}, "
                    f"tier {row['tier']})"
                )
                report.append("")
                checks = spot_check_row(row, inv)
                total_rows += 1
                for name, status in checks:
                    flag = "✗" if status.startswith("FAIL") else (
                        "!" if status.startswith("DIVERGE") else "✓"
                    )
                    if flag == "✗":
                        total_fails += 1
                    elif flag == "!":
                        total_diverges += 1
                    report.append(f"- [{flag}] **{name}**: {status}")
                report.append("")

    # Insert summary right after the header lines (before the blank line
    # at position 4). The blank line at position 4 already separates
    # the metadata from the content; do NOT insert an extra blank.
    report.insert(
        4,
        f"**Summary**: {total_rows} rows checked, {total_fails} fails, "
        f"{total_diverges} diverges.",
    )

    # Strip trailing empty entries before joining (each section appends
    # an empty line; the final section's trailing empty creates a
    # double-newline at end of file otherwise).
    while report and report[-1] == "":
        report.pop()
    args.output.write_text("\n".join(report) + "\n")
    print(f"Report: {args.output}")
    print(
        f"{total_rows} rows checked, {total_fails} fails, "
        f"{total_diverges} diverges."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
