#!/usr/bin/env python3
"""
Stage 5 documentation builder for the per-arch 12-stratum leaderboard.

Generates:
  - Per-stratum READMEs (7 populated + 5 stub = 12 total)
  - Top-level README.md replacement
  - headlines.md (top-3 per stratum, both metrics)

Inputs:
  - leaderboard_tiers_*.json from Stage 2
  - tier_stability_*.md from Stage 3
  - cross-architecture-*.md from Stage 4

Usage::

    python scripts/build_per_arch_documentation.py
"""
from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PER_ARCH_DIR = PROJECT_ROOT / "results" / "leaderboard" / "per-architecture"
LOGGER = logging.getLogger(__name__)

POPULATED_STRATA = [
    ("era1", "single-pass"),
    ("era1", "consensus"),
    ("era2", "single-pass"),
    ("era2", "consensus"),
    ("era2", "single-pass+PV"),
    ("era2", "pv"),
    ("era3", "consensus"),
]
EMPTY_STRATA = [
    ("era1", "single-pass+PV"),
    ("era1", "pv"),
    ("era3", "single-pass"),
    ("era3", "single-pass+PV"),
    ("era3", "pv"),
]

ERA_DESCRIPTIONS = {
    "era1": "340 tiles, 512 px, full Era-1 evaluation bounds",
    "era2": "487 tiles, 384 px, full Era-2 evaluation bounds",
    "era3": "327 tiles, 384 px, h10 test bounds (subset of Era 2)",
}
ARCH_DESCRIPTIONS = {
    "single-pass": (
        "One stochastic detection pass per tile (K=1). No "
        "consensus, no verifier."
    ),
    "consensus": (
        "K stochastic passes + greedy-voting consensus at threshold "
        "vote_t. No verifier."
    ),
    "single-pass+PV": (
        "One detection pass + one verifier pass. The detection "
        "GeoJSON is post-thresholded by the verifier's binary cut."
    ),
    "pv": (
        "K passes + greedy consensus + verifier pass, materialised "
        "at the 20 m-optimal (vote_t, prob_t) pair per cell."
    ),
}


def _safe_load(path: Path) -> dict | None:
    if not path.is_file():
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _top_n_conditions(payload: dict, metric: str, n: int = 3) -> list[dict]:
    """Return the top-N conditions in tier 1 by score."""
    tiers = payload.get("tiers", [])
    if not tiers:
        return []
    tier1 = tiers[0].get("conditions", [])
    score_key = "f1" if metric == "f1" else "tile_mcc"

    def _score(c):
        if score_key == "f1":
            return float(
                c.get("evaluations", {}).get("20", {}).get("f1", 0.0)
            )
        return float(c.get("tile_mcc", 0.0))

    sorted_tier = sorted(tier1, key=_score, reverse=True)
    return sorted_tier[:n]


def write_per_stratum_readme(era: str, arch: str) -> Path | None:
    """Write the README for one populated stratum."""
    stratum_dir = PER_ARCH_DIR / era / arch
    if not stratum_dir.is_dir():
        return None

    f1_payload = _safe_load(stratum_dir / "leaderboard_tiers_20m.json")
    mcc_payload = _safe_load(stratum_dir / "leaderboard_tiers_mcc_20m.json")

    n_conditions = (
        f1_payload.get("n_conditions", 0) if f1_payload else 0
    )
    n_tiers_f1 = (
        f1_payload.get("n_tiers", 0) if f1_payload else 0
    )
    n_tiers_mcc = (
        mcc_payload.get("n_tiers", 0) if mcc_payload else 0
    )

    lines = [
        f"# Per-stratum leaderboard — Era {era[-1]} {arch}",
        "",
        f"**Generated**: {datetime.now(tz=timezone.utc).date()} "
        "(Session 79 redesign)",
        f"**Era**: {era[-1]} ({ERA_DESCRIPTIONS[era]})",
        f"**Architecture**: {arch} — {ARCH_DESCRIPTIONS[arch]}",
        f"**Conditions**: {n_conditions}",
        f"**F1 tiers** (q=0.05): {n_tiers_f1}",
        f"**MCC tiers** (q=0.05): {n_tiers_mcc}",
        "",
        "## Files in this directory",
        "",
        "**Tier tables (q=0.05 base)**:",
        "",
    ]
    for buf in (20, 30, 40, 50, 100):
        lines.append(f"- `leaderboard_tiers_{buf}m.md` — F1 at {buf} m")
    for buf in (20, 30, 40, 50, 100):
        lines.append(f"- `leaderboard_tiers_mcc_{buf}m.md` — MCC at {buf} m")
    lines.append("")
    lines.append("**Tier tables (q=0.01 sensitivity)**:")
    lines.append("")
    for buf in (20, 30, 40, 50, 100):
        lines.append(
            f"- `leaderboard_tiers_q01_{buf}m.md` — F1 at q=0.01"
        )
    for buf in (20, 30, 40, 50, 100):
        lines.append(
            f"- `leaderboard_tiers_mcc_q01_{buf}m.md` — MCC at q=0.01"
        )
    lines.append("")
    lines.append("**Tier-stability tables**:")
    lines.append("")
    lines.append("- `tier_stability.md` — Spearman rho across buffers (F1)")
    lines.append("- `tier_stability_mcc.md` — Spearman rho across buffers (MCC)")
    lines.append("")
    lines.append("**Sweep + JSON sidecars**:")
    lines.append("")
    lines.append(
        "- `leaderboard_all_evaluations.json` — full threshold x "
        "buffer evaluation sweep"
    )
    lines.append(
        "- `leaderboard_tiers_20m.json` — primary-buffer F1 tier JSON "
        "(includes pairwise tests)"
    )
    lines.append(
        "- `leaderboard_tiers_mcc_20m.json` — primary-buffer MCC tier JSON"
    )
    lines.append("")

    # Top-3 per metric
    top_f1 = _top_n_conditions(f1_payload, "f1", n=3) if f1_payload else []
    top_mcc = _top_n_conditions(mcc_payload, "mcc", n=3) if mcc_payload else []

    if top_f1:
        lines.append("## Top-3 by F1 (Tier 1, 20 m)")
        lines.append("")
        lines.append("| # | Condition | F1 [95% CI] | MCC |")
        lines.append("|--:|:---|:---|---:|")
        for i, c in enumerate(top_f1, 1):
            e = c.get("evaluations", {}).get("20", {})
            f1 = e.get("f1", 0)
            ci_lo = e.get("f1_ci_lower", 0)
            ci_hi = e.get("f1_ci_upper", 0)
            mcc = c.get("tile_mcc", 0)
            lines.append(
                f"| {i} | `{c['label']}` | "
                f"{f1:.3f} [{ci_lo:.3f}, {ci_hi:.3f}] | {mcc:+.3f} |"
            )
        lines.append("")

    if top_mcc:
        lines.append("## Top-3 by MCC (Tier 1)")
        lines.append("")
        lines.append("| # | Condition | MCC | F1@20 m |")
        lines.append("|--:|:---|---:|---:|")
        for i, c in enumerate(top_mcc, 1):
            mcc = c.get("tile_mcc", 0)
            f1 = c.get("evaluations", {}).get("20", {}).get("f1", 0)
            lines.append(
                f"| {i} | `{c['label']}` | {mcc:+.3f} | {f1:.3f} |"
            )
        lines.append("")

    lines.append("## See also")
    lines.append("")
    lines.append("- Top-level `../README.md` for cross-stratum methodology")
    lines.append(
        "- `../headlines.md` for top-3 leaders across all strata"
    )
    lines.append(
        "- `../cross-architecture-era*_*m_*.md` for flat cross-arch "
        "comparisons within Era"
    )
    lines.append(
        "- `../cross-architecture-paired-era*.md` for paired tests "
        "(does PV help on this proposer?)"
    )
    lines.append(
        "- `../mc-precision-flags.md` for permutation-precision-limited tests"
    )
    lines.append("")

    out_path = stratum_dir / "README.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    LOGGER.info("Wrote %s", out_path)
    return out_path


def write_empty_stratum_readme(era: str, arch: str) -> Path:
    """Write a stub README for an empty stratum."""
    stratum_dir = PER_ARCH_DIR / era / arch
    stratum_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Per-stratum leaderboard — Era {era[-1]} {arch} (EMPTY)",
        "",
        f"**Generated**: {datetime.now(tz=timezone.utc).date()} "
        "(Session 79 redesign)",
        f"**Era**: {era[-1]} ({ERA_DESCRIPTIONS[era]})",
        f"**Architecture**: {arch} — {ARCH_DESCRIPTIONS[arch]}",
        "**Conditions**: 0",
        "",
        "## Why this stratum is empty",
        "",
    ]
    if era == "era1" and arch in {"single-pass+PV", "pv"}:
        lines.append(
            "The Era 1 PV pipeline was never run on the 512 px tile "
            "scope. PV materialisation began with the H11 384 px tile "
            "redesign (Era 2). Cross-grid PV would require a re-tiling "
            "pass not in scope for this study."
        )
    elif era == "era3" and arch == "single-pass":
        lines.append(
            "Era 3 (327-tile h10 test bounds) is a post-hoc subset of "
            "Era 2; no single-pass conditions were materialised at "
            "this scope. Era 2 single-pass cells could be re-evaluated "
            "on the Era 3 bounds, but the existing Era 3 inventory has "
            "only consensus runs from the H8/H10/H12 library-design "
            "comparability sweeps."
        )
    elif era == "era3" and arch == "single-pass+PV":
        lines.append(
            "No single-pass+PV conditions were run at the Era 3 "
            "(327-tile) scope. The existing single-pass+PV cells "
            "(8 H11 verifier-prompt variants) target the Era 2 "
            "(487-tile) scope."
        )
    elif era == "era3" and arch == "pv":
        lines.append(
            "No PV conditions were materialised on the Era 3 "
            "(327-tile) scope. PV cells live in Era 2 (487 tiles)."
        )
    else:
        lines.append(
            "No conditions match this (era, architecture) combination "
            "in the inventory."
        )
    lines.append("")
    lines.append(
        "Empty strata receive this stub for completeness; they do not "
        "produce tier tables."
    )
    lines.append("")
    out_path = stratum_dir / "README.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    LOGGER.info("Wrote %s", out_path)
    return out_path


def write_top_level_readme() -> Path:
    """Write the top-level README replacing the prior agent's version."""
    lines = [
        "# Per-architecture x per-era tier leaderboards",
        "",
        f"**Generated**: {datetime.now(tz=timezone.utc).date()} "
        "(Session 79 redesign)",
        "**Scope**: 12-stratum matrix (3 eras x 4 architectures)",
        "",
        "## Overview",
        "",
        "This tree stratifies the burial-mound-detection corpus into a "
        "12-cell matrix of (Era x Architecture) and builds parallel F1 "
        "and MCC tier leaderboards within each populated stratum, plus "
        "cross-architecture comparisons within and across Eras.",
        "",
        "**Populated strata**: 7 (see directories below). **Empty "
        "strata**: 5 (with stub READMEs explaining the absence).",
        "",
        "| Era | single-pass | consensus | single-pass+PV | pv |",
        "|:---:|:---:|:---:|:---:|:---:|",
        "| **1** | populated | populated | empty | empty |",
        "| **2** | populated | populated | populated | populated |",
        "| **3** | empty | populated | empty | empty |",
        "",
        "## Methodology",
        "",
        "### Tier-building algorithm",
        "",
        "Each populated stratum runs the following pipeline (driver: "
        "`scripts/build_per_arch_redesign.sh`, library: "
        "`scripts/build_tiered_leaderboard.py`):",
        "",
        "1. **Resolve conditions** from "
        "`planning/condition-inventory-with-s78.json`.",
        "2. **Evaluate** each condition at all 5 buffers "
        "(20, 30, 40, 50, 100 m) with 1,000 stratified bootstrap "
        "iterations for F1/P/R 95% CIs and tile-level MCC + "
        "sensitivity + specificity (also 1,000 iterations).",
        "3. **Select thresholds**: per condition, choose the consensus "
        "threshold maximising F1 at the 20 m primary buffer "
        "(metric-independent: F1 at 20 m is the operational point even "
        "when MCC is the tier-building metric).",
        "4. **Pairwise permutation tests**: all C(N, 2) pairs with "
        "10,000 permutations, seed=42, paired tile-swap (F1 path) or "
        "per-tile (TP, TN, FP, FN) classification swap (MCC path). "
        "MCC null distribution validated symmetric and zero-centred "
        "in `docs/methodology/mcc-permutation-validation-2026-04-25.md`.",
        "5. **BH-FDR correction**: Benjamini-Hochberg adjusted "
        "p-values at q=0.05 (base) and q=0.01 (sensitivity).",
        "6. **Greedy-clique tiering**: conditions sorted by score "
        "descending; each appended to the current tier if "
        "indistinguishable (BH-adjusted p >= q) from all current "
        "members; otherwise a new tier starts. Tier inheritance from "
        "the primary buffer (20 m) propagates across the 5 buffer "
        "files.",
        "",
        "See `planning/leaderboard-construction-plan.md` for the full "
        "methodology rationale.",
        "",
        "### F1 + MCC parallel tiers",
        "",
        "Each populated stratum produces parallel tier tables under "
        "F1 and MCC. F1 is the canonical detection-quality metric "
        "(precision-recall harmonic mean at the matching buffer); MCC "
        "is the binary-classification metric over tile presence "
        "(buffer-invariant in this codebase). The pair is reported "
        "per the project's `feedback_mcc_with_f1` policy: report "
        "tile-level MCC alongside F1 wherever inputs support it.",
        "",
        "MCC threshold selection still uses F1 at 20 m for "
        "cross-metric alignment — both F1 and MCC tier tables for the "
        "same stratum read off the same operational threshold per "
        "condition.",
        "",
        "### Why the parallel tier tables can disagree",
        "",
        "F1 and MCC weight detections differently. F1 counts mound-"
        "level matching (TP within buffer of GT mound) and is "
        "buffer-aware; MCC counts tile-level presence (any detection "
        "in any tile that has any GT mound) and is buffer-invariant. "
        "Strata where the bottom of the F1 ranking has high tile "
        "presence but low mound-level matching will see those "
        "conditions descend into MCC's lower tiers, while top-F1 "
        "conditions usually align with top-MCC.",
        "",
        "### Tier stability across buffers",
        "",
        "Each stratum has a `tier_stability_<metric>.md` showing "
        "Spearman rank correlation between tier@20m and tier@30/40/50/"
        "100m. High rho (close to 1.0) indicates that buffer choice "
        "does not change the tier ordering; low rho indicates "
        "buffer-dependent ranking changes worth flagging.",
        "",
        "MCC tables show identical tier orderings across buffers (MCC "
        "is buffer-invariant by construction in this codebase).",
        "",
        "### q=0.01 sensitivity pass",
        "",
        "Each tier table at q=0.05 has a parallel tier table at "
        "q=0.01 (`leaderboard_tiers_q01_<buf>m.md`). Larger Tier 1 "
        "sets at q=0.05 benefit from a stricter q=0.01 directional "
        "inspection — the tighter cut groups together only the "
        "conditions that pass a stricter test of indistinguishability.",
        "",
        "### Within-stratum vs cross-stratum FDR",
        "",
        "BH-FDR is applied **within stratum**: each (Era x "
        "Architecture x Buffer x Metric) family is corrected "
        "independently. Cross-stratum claims (e.g. \"Era 1 best vs "
        "Era 2 best\") have **inflated family-wise error rate** and "
        "are not statistically grounded. Use within-stratum claims "
        "for paper citations; treat cross-stratum claims as "
        "descriptive.",
        "",
        "Also note that the Era 1 vs Era 2/3 comparison is across "
        "different tile grids (512 px vs 384 px); paired permutation "
        "is impossible without re-tiling. Era 2 vs Era 3 share the "
        "same grid (Era 3 is a 327-tile subset of Era 2's 487 tiles).",
        "",
        "### Greedy clique vs alternatives",
        "",
        "Greedy clique was chosen because it stops a tier at the "
        "first significant difference -- a more conservative grouping "
        "than the alternative connected-components algorithm "
        "(transitive closure of indistinguishability). Greedy clique "
        "matches the standard leaderboard-reporting convention used "
        "across the project's other tier tables. Alternatives exist; "
        "the choice is a point of methodological consistency rather "
        "than absolute correctness.",
        "",
        "### Monte-Carlo precision",
        "",
        "Pairwise tests at p <= 5/N (where N=10,000) are precision-"
        "limited; the true p might be much smaller. See "
        "`mc-precision-flags.md` for the catalog. If a paper-citation "
        "hinges on a flagged comparison, re-run that pair at "
        "N=100,000 to tighten the bound.",
        "",
        "### Cross-architecture paired comparisons",
        "",
        "Within each Era, proposer-config tuples (model, "
        "config_version, instruction_file, thinking, T, N, track, "
        "vote_t) that appear in 2+ architecture columns are tested "
        "pairwise on the shared tiles. The output answers the "
        "question \"does adding the verifier (or moving from "
        "single-pass to consensus) help on this proposer?\". See "
        "`cross-architecture-paired-era<N>_<metric>.md` per Era.",
        "",
        "## Era definitions",
        "",
        "| Era | Tiles | Tile size | Stride | GT mounds | Bounds file |",
        "|:---:|:-----:|:---------:|:------:|:---------:|:-----------|",
        "| **1** | 340 | 512 px | 448 px | 539 | "
        "`inputs/vectors/bounds/full_evaluation_bounds.geojson` |",
        "| **2** | 487 | 384 px | 336 px | 435 | "
        "`inputs/vectors/bounds/384/full_evaluation_bounds.geojson` |",
        "| **3** | 327 | 384 px | 336 px | 319 | "
        "`inputs/vectors/bounds/384/h10_test_bounds.geojson` |",
        "",
        "## Architecture definitions",
        "",
        "| Architecture | Description | Threshold sweep |",
        "|:---|:---|:---|",
    ]
    for arch in ("single-pass", "consensus", "single-pass+PV", "pv"):
        if arch == "consensus":
            sweep = "vote_t in {1..K}"
        elif arch == "pv":
            sweep = "Optimised both vote_t and prob_t"
        else:
            sweep = "—"
        lines.append(f"| `{arch}` | {ARCH_DESCRIPTIONS[arch]} | {sweep} |")
    lines.append("")

    lines.extend([
        "## File guide",
        "",
        "| File pattern | Description |",
        "|:---|:---|",
        "| `era<N>/<arch>/leaderboard_tiers_<buf>m.md` | "
        "F1 tier table at q=0.05 |",
        "| `era<N>/<arch>/leaderboard_tiers_q01_<buf>m.md` | "
        "F1 tier table at q=0.01 (sensitivity) |",
        "| `era<N>/<arch>/leaderboard_tiers_mcc_<buf>m.md` | "
        "MCC tier table at q=0.05 |",
        "| `era<N>/<arch>/leaderboard_tiers_mcc_q01_<buf>m.md` | "
        "MCC tier table at q=0.01 (sensitivity) |",
        "| `era<N>/<arch>/leaderboard_tiers_<...>.json` | "
        "Machine-readable tier JSONs (with pairwise tests) |",
        "| `era<N>/<arch>/leaderboard_all_evaluations.json` | "
        "Full threshold x buffer sweep for the stratum |",
        "| `era<N>/<arch>/tier_stability.md` | "
        "Spearman rho across buffers (F1) |",
        "| `era<N>/<arch>/tier_stability_mcc.md` | "
        "Spearman rho across buffers (MCC) |",
        "| `cross-architecture-era<N>_<buf>m_<metric>.md` | "
        "Flat cross-arch comparison within Era at buffer |",
        "| `cross-architecture-paired-era<N>_<metric>.md` | "
        "Paired test of shared proposer-config tuples within Era |",
        "| `mc-precision-flags.md` | "
        "Pairwise tests where p <= 5/N (precision-limited) |",
        "| `headlines.md` | "
        "Top-3 leaders per (Era, arch, metric, q=0.05) cell |",
        "",
        "## See also",
        "",
        "- `planning/leaderboard-construction-plan.md` -- methodology "
        "rationale and the 2026-04-25 redesign addendum",
        "- "
        "`docs/methodology/mcc-permutation-validation-2026-04-25.md` "
        "-- proof that the MCC null distribution is valid",
        "- `docs/methodology/data-reproduction-2026-04-25.md` -- "
        "Session 78 shared-crops re-derivation provenance "
        "(prerequisite for the Era 2 PV stratum)",
        "",
    ])

    out_path = PER_ARCH_DIR / "README.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    LOGGER.info("Wrote %s", out_path)
    return out_path


def write_headlines() -> Path:
    """Write headlines.md with top-3 per (era, arch, metric, q=0.05)."""
    lines = [
        "# Headlines — top-3 per stratum",
        "",
        f"**Generated**: {datetime.now(tz=timezone.utc).date()} "
        "(Session 79 redesign)",
        "",
        "Top-3 conditions in Tier 1 of each populated (era, "
        "architecture) stratum at q=0.05, separately for F1 and MCC. "
        "Buffer = 20 m for F1 (primary); MCC is buffer-invariant.",
        "",
    ]
    for era, arch in POPULATED_STRATA:
        stratum_dir = PER_ARCH_DIR / era / arch
        f1_payload = _safe_load(stratum_dir / "leaderboard_tiers_20m.json")
        mcc_payload = _safe_load(
            stratum_dir / "leaderboard_tiers_mcc_20m.json"
        )

        lines.append(f"## Era {era[-1]} / {arch}")
        lines.append("")
        if f1_payload:
            lines.append("### F1 (20 m)")
            lines.append("")
            lines.append("| # | Condition | F1 [95% CI] |")
            lines.append("|--:|:---|:---|")
            for i, c in enumerate(_top_n_conditions(f1_payload, "f1"), 1):
                e = c.get("evaluations", {}).get("20", {})
                f1 = e.get("f1", 0)
                ci_lo = e.get("f1_ci_lower", 0)
                ci_hi = e.get("f1_ci_upper", 0)
                lines.append(
                    f"| {i} | `{c['label']}` | "
                    f"{f1:.3f} [{ci_lo:.3f}, {ci_hi:.3f}] |"
                )
            lines.append("")

        if mcc_payload:
            lines.append("### MCC")
            lines.append("")
            lines.append("| # | Condition | MCC | F1@20m |")
            lines.append("|--:|:---|---:|---:|")
            for i, c in enumerate(_top_n_conditions(mcc_payload, "mcc"), 1):
                mcc = c.get("tile_mcc", 0)
                f1 = c.get("evaluations", {}).get("20", {}).get("f1", 0)
                lines.append(
                    f"| {i} | `{c['label']}` | {mcc:+.3f} | {f1:.3f} |"
                )
            lines.append("")

    out_path = PER_ARCH_DIR / "headlines.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    LOGGER.info("Wrote %s", out_path)
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build per-arch documentation (Stage 5)."
    )
    parser.add_argument(
        "--what", choices=["all", "stratum", "top", "headlines"],
        default="all",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if args.what in {"all", "stratum"}:
        for era, arch in POPULATED_STRATA:
            write_per_stratum_readme(era, arch)
        for era, arch in EMPTY_STRATA:
            write_empty_stratum_readme(era, arch)
    if args.what in {"all", "top"}:
        write_top_level_readme()
    if args.what in {"all", "headlines"}:
        write_headlines()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
