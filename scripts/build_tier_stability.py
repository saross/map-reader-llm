#!/usr/bin/env python3
"""
Build tier-stability tables with Spearman rank correlation across buffers.

Stage 3 of the per-arch leaderboard 12-stratum redesign
(Session 79, 2026-04-25). For each populated stratum, generates
``tier_stability_<metric>.md`` showing each condition's tier
assignment per buffer, plus the Spearman rank correlation between
``tier@20m`` and ``tier@<buf>m`` for buf in {30, 40, 50, 100}.

Inputs:
    - ``leaderboard_tiers_<metric>_{20,30,40,50,100}m.json`` per
      stratum at ``results/leaderboard/per-architecture/era<N>/<arch>/``

Outputs:
    - ``tier_stability_<metric>.md`` (per stratum)

Usage::

    python scripts/build_tier_stability.py --metric f1 \\
        --stratum-dir results/leaderboard/per-architecture/era1/consensus/

    python scripts/build_tier_stability.py --metric mcc --all
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr


LOGGER = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PER_ARCH_DIR = PROJECT_ROOT / "results" / "leaderboard" / "per-architecture"
BUFFERS = [20, 30, 40, 50, 100]
DEFAULT_PRIMARY = 20

# Rendered wherever a score is not computable (erratum E81). Matches
# ``evaluate_detections.UNDEFINED_DISPLAY`` so every table in the
# project spells an undefined metric the same way.
UNDEFINED_DISPLAY = "undefined"

# Strata definitions (mirror of Stage 2 driver). Empty strata are
# skipped; their stub READMEs are produced separately.
POPULATED_STRATA = [
    ("era1", "single-pass"),
    ("era1", "consensus"),
    ("era2", "single-pass"),
    ("era2", "consensus"),
    ("era2", "single-pass+PV"),
    ("era2", "pv"),
    ("era3", "consensus"),
]


def _load_tier_json(stratum_dir: Path, metric: str, buf: int) -> dict | None:
    """Load the tier JSON for one (stratum, metric, buffer) triple.

    Per-buffer F1 re-tiering (2026-04-26) writes a tier JSON for F1 at
    every buffer; the script reads ``leaderboard_tiers_{buf}m.json``
    for F1 and falls back to the 20 m primary JSON only if the
    per-buffer file is absent (e.g. for strata that haven't been
    re-run yet).

    MCC tier construction is buffer-independent (the tile-level MCC
    permutation test does not take a buffer argument), so MCC writes
    only one JSON per stratum at the primary buffer
    (``leaderboard_tiers_mcc_20m.json``). For MCC at non-primary
    buffers the script always falls back to the 20 m JSON; this is
    correct by methodology, not a degenerate output.

    Returns None if even the primary-buffer JSON is missing.
    """
    if metric == "f1":
        candidate = stratum_dir / f"leaderboard_tiers_{buf}m.json"
    else:
        candidate = stratum_dir / f"leaderboard_tiers_{metric}_{buf}m.json"
    if candidate.is_file():
        with open(candidate, encoding="utf-8") as fh:
            return json.load(fh)
    # Fall back to primary-buffer JSON
    if metric == "f1":
        primary = stratum_dir / "leaderboard_tiers_20m.json"
    else:
        primary = stratum_dir / f"leaderboard_tiers_{metric}_20m.json"
    if primary.is_file():
        with open(primary, encoding="utf-8") as fh:
            payload = json.load(fh)
        # Mark that this is a fall-back load
        payload["__fallback_from_primary__"] = True
        return payload
    LOGGER.warning("Missing tier file (and primary fallback): %s", candidate)
    return None


def _condition_tier_map(tiers_payload: dict) -> dict[str, int]:
    """Return {condition_label: tier_index} from a tier JSON file."""
    mapping: dict[str, int] = {}
    for tier_idx, tier in enumerate(tiers_payload.get("tiers", []), 1):
        for cond in tier.get("conditions", []):
            mapping[cond["label"]] = tier_idx
    return mapping


def _fmt_score(val: float | None, digits: int = 3) -> str:
    """Format a possibly-undefined score for a Markdown cell.

    Mirrors ``evaluate_detections._fmt_metric``. Kept local so this
    script stays importable without the heavier evaluation stack.

    Args:
        val: The score, or ``None`` when it is undefined (erratum
            E81 — a degenerate 2 x 2 tile confusion matrix leaves the
            Matthews Correlation Coefficient (MCC) with no value).
        digits: Decimal places for the numeric case.

    Returns:
        The formatted number, or :data:`UNDEFINED_DISPLAY` for
        ``None``. A genuine zero still renders as ``'0.000'``.

    Examples:
        >>> _fmt_score(0.0)
        '0.000'
        >>> _fmt_score(None)
        'undefined'
    """
    if val is None:
        return UNDEFINED_DISPLAY
    return f"{val:.{digits}f}"


def _read_condition_mcc(cond: dict) -> float | None:
    """Read a condition's tile-level MCC from the first source that carries it.

    Sources are consulted in preference order: the condition-level
    ``tile_mcc`` key written by the Session-79 builder, then
    ``evaluations[20m].mcc``, then ``tile_classification.mcc.mean``.

    A source *carries* the metric when the key is **present**, even
    when its value is JSON ``null``. Erratum E81: ``null`` is the
    builder saying "this coefficient is undefined for this
    condition", which is an answer, not a missing field — falling
    through to a later source on ``null`` would let some other
    source's number stand in for a non-measurement.

    Args:
        cond: One element of a tier JSON's ``tiers[].conditions``.

    Returns:
        The MCC, or ``None`` when it is undefined or no source
        carries it.
    """
    evals_at_primary = cond.get("evaluations", {}).get(
        str(DEFAULT_PRIMARY), {},
    )
    tile_class_mcc = cond.get("tile_classification", {}).get("mcc", {})
    for container, key in (
        (cond, "tile_mcc"),
        (evals_at_primary, "mcc"),
        (tile_class_mcc, "mean"),
    ):
        if isinstance(container, dict) and key in container:
            value = container[key]
            return None if value is None else float(value)
    return None


def _condition_score_map(
    tiers_payload: dict, score_key: str,
) -> dict[str, float | None]:
    """Return {condition_label: score} from a tier JSON file.

    For F1 the score is read from ``evaluations[20m].f1``; for MCC it
    is read by :func:`_read_condition_mcc`.

    Erratum E81 (2026-08-18): the MCC lookup used to be an ``or``
    chain ending in ``0.0``, wrapped in ``float(score or 0.0)``. That
    carried two defects at once. An *undefined* MCC (now serialised
    as JSON ``null``) was published as 0.0, which § 4.2 of the
    preregistration reads as chance-level performance. And a
    *legitimate* MCC of exactly 0.0 was falsy, so it fell through to
    the next fallback source — landing on the right number only by
    the accident of the chain terminating in 0.0, and on a different
    source's number whenever one was present. Both are fixed by
    explicit key-presence and ``is None`` tests.

    Args:
        tiers_payload: Parsed ``leaderboard_tiers*.json`` payload.
        score_key: ``"f1"`` or ``"mcc"``.

    Returns:
        Mapping from condition label to score, where ``None`` means
        the score is undefined (MCC) or unavailable. Callers must
        render ``None`` as ``undefined`` and must not rank it as 0.
    """
    mapping: dict[str, float | None] = {}
    for tier in tiers_payload.get("tiers", []):
        for cond in tier.get("conditions", []):
            score: float | None
            if score_key == "f1":
                # F1 is always computable; 0.0 for "nothing matched"
                # is a measurement, not a placeholder.
                score = float(
                    cond.get("evaluations", {})
                        .get(str(DEFAULT_PRIMARY), {})
                        .get("f1", 0.0)
                )
            elif score_key == "mcc":
                score = _read_condition_mcc(cond)
            else:
                score = None
            mapping[cond["label"]] = score
    return mapping


def build_stability_table(
    stratum_dir: Path, metric: str,
) -> tuple[Path, dict] | None:
    """Build the tier-stability table for one stratum + metric.

    Returns ``(output_path, summary_dict)`` on success, or ``None`` if
    the stratum has no tier files for this metric.
    """
    # Load all 5 buffer tier JSONs
    payloads: dict[int, dict] = {}
    for buf in BUFFERS:
        payload = _load_tier_json(stratum_dir, metric, buf)
        if payload is not None:
            payloads[buf] = payload
    if not payloads:
        LOGGER.warning("No tier JSONs for %s metric=%s", stratum_dir, metric)
        return None

    if DEFAULT_PRIMARY not in payloads:
        LOGGER.warning(
            "Missing primary buffer (%dm) tier file in %s",
            DEFAULT_PRIMARY, stratum_dir,
        )
        return None

    # Collect tier-per-buffer maps
    tier_maps: dict[int, dict[str, int]] = {
        buf: _condition_tier_map(p) for buf, p in payloads.items()
    }

    # Score map at primary buffer (for table sort)
    score_key = "f1" if metric == "f1" else "mcc"
    score_map = _condition_score_map(payloads[DEFAULT_PRIMARY], score_key)

    # All conditions across the union of buffers
    all_conditions = sorted(
        {
            label
            for buf_map in tier_maps.values()
            for label in buf_map
        },
        # Erratum E81: sort defined scores descending and push
        # undefined ones to the end of the table rather than ranking
        # them at 0.0 (which the MCC scale reads as chance). The
        # leading 0/1 flag does the partitioning; the second element
        # orders within the defined group.
        key=lambda lbl: (
            (0, -score_map[lbl])
            if score_map.get(lbl) is not None
            else (1, 0.0)
        ),
    )

    # Per-other-buffer Spearman rho between tier@20m and tier@buf
    primary_tiers = tier_maps[DEFAULT_PRIMARY]
    spearman: dict[int, tuple[float, float]] = {}
    for buf in BUFFERS:
        if buf == DEFAULT_PRIMARY or buf not in tier_maps:
            continue
        other_tiers = tier_maps[buf]
        common = sorted(set(primary_tiers) & set(other_tiers))
        if len(common) < 2:
            spearman[buf] = (float("nan"), float("nan"))
            continue
        x = np.array([primary_tiers[c] for c in common])
        y = np.array([other_tiers[c] for c in common])
        if x.std() == 0 or y.std() == 0:
            # All conditions in one tier on one side → undefined.
            spearman[buf] = (1.0 if (x == y).all() else float("nan"), 1.0)
            continue
        rho, p = spearmanr(x, y)
        spearman[buf] = (float(rho), float(p))

    # Build markdown
    metric_label = metric.upper()
    score_col = "F1@20m" if metric == "f1" else "MCC@20m"

    # Track the legacy "fallback to primary JSON" state for the JSON
    # sidecar. With Option A re-tiering (2026-04-26) the F1 stability
    # tables are built from genuinely independent per-buffer JSONs;
    # MCC tables continue to fall back by methodology. The count is no
    # longer surfaced in the markdown but is preserved in the JSON for
    # downstream auditing.
    fallback_count = sum(
        1 for buf, p in payloads.items()
        if buf != DEFAULT_PRIMARY and p.get("__fallback_from_primary__")
    )
    n_other = len([b for b in BUFFERS if b != DEFAULT_PRIMARY])

    # Methodology text branches by metric. F1 tiers are constructed
    # independently at each buffer (Option A re-tiering, 2026-04-26):
    # per-cell thresholds are fixed at the primary buffer (20 m) via
    # --threshold-buffer, and pairwise tests + tier construction run
    # at each of 20 / 30 / 40 / 50 / 100 m. Spearman rho is therefore
    # substantive. MCC tiers are identical across buffers by methodology
    # — the tile-level MCC permutation test does not take a buffer
    # argument — so rho = 1.0 is correct, not degenerate.
    if metric == "mcc":
        methodology_paragraph = (
            "**MCC tiers are buffer-independent by methodology.** The "
            "MCC permutation test (`run_permutation_test_mcc`) operates "
            "on tile-level binary classifications which do not depend "
            "on the buffer used for spatial matching during F1 "
            "evaluation. The greedy-clique tiering also sorts by a "
            "single buffer-independent MCC value per condition. "
            "Therefore the tier assignments at 20 / 30 / 40 / 50 / "
            "100 m are identical, and Spearman rho across buffers is "
            "1.0 by construction. This is not a degenerate output; it "
            "correctly reflects that MCC at the tile level summarises "
            "the entire confusion matrix without buffer-dependent "
            "matching geometry."
        )
    else:
        methodology_paragraph = (
            "**F1 tiers are constructed independently at each buffer.** "
            "Per-cell thresholds are fixed at the primary buffer "
            f"({DEFAULT_PRIMARY} m) via the `--threshold-buffer` flag of "
            "`build_tiered_leaderboard.py`; pairwise permutation tests "
            "and greedy-clique tier construction then run at each of "
            f"{BUFFERS} m using those fixed thresholds (Option A "
            "semantics). Spearman rho values reported below are "
            "therefore substantive — they surface buffer-dependent "
            "tier reorganisations rather than a tautology."
        )

    lines = [
        f"# Tier stability ({metric_label}) — "
        f"{stratum_dir.parent.name} {stratum_dir.name}",
        "",
        f"**Metric**: {metric_label}",
        f"**Stratum**: {stratum_dir.parent.name} / {stratum_dir.name}",
        f"**Conditions**: {len(all_conditions)}",
        "",
        "## Methodology",
        "",
        f"For each condition the table records the tier index "
        f"assigned at each of the 5 buffer tier tables ({BUFFERS} m). "
        f"Spearman's rho is computed between the rank vector of "
        f"tier assignments at {DEFAULT_PRIMARY} m and that at each "
        "other buffer. A rho of 1.0 means perfect rank-stability "
        "(no condition crosses a tier boundary across that buffer "
        "change); lower values surface buffer-dependent tier "
        "reorganisations.",
        "",
        methodology_paragraph,
        "",
        "Note: ties (all conditions in one tier) make Spearman's rho "
        "undefined; the rho column reports `nan` in that case.",
        "",
        "## Spearman rank correlation summary",
        "",
        "| vs buffer | Spearman rho | p-value |",
        "|---:|---:|---:|",
    ]
    for buf in BUFFERS:
        if buf == DEFAULT_PRIMARY:
            continue
        rho, p = spearman.get(buf, (float("nan"), float("nan")))
        rho_str = f"{rho:+.4f}" if not np.isnan(rho) else "nan"
        p_str = f"{p:.4f}" if not np.isnan(p) else "nan"
        lines.append(f"| {buf} m | {rho_str} | {p_str} |")
    lines.append("")

    lines.append("## Per-condition tier assignments")
    lines.append("")
    header_buffers = " | ".join(f"tier@{b}m" for b in BUFFERS)
    sep_buffers = " | ".join(["---:"] * len(BUFFERS))
    lines.append(
        f"| condition | {score_col} | {header_buffers} | spearman vs 20m |"
    )
    lines.append(
        f"|:---|---:| {sep_buffers} |---:|"
    )

    for cond in all_conditions:
        score = score_map.get(cond)
        tier_assignments = [
            tier_maps.get(buf, {}).get(cond, "—") for buf in BUFFERS
        ]
        # Per-condition Spearman doesn't really make sense (Spearman
        # is computed across the population). Show the row-level
        # marker: "stable" if tier@20m == tier@all other buffers,
        # "shift" otherwise.
        primary = tier_maps.get(DEFAULT_PRIMARY, {}).get(cond)
        stable = all(
            tier_maps.get(b, {}).get(cond) == primary
            for b in BUFFERS if b != DEFAULT_PRIMARY
        )
        marker = "stable" if stable else "shift"
        score_str = _fmt_score(score)
        tier_strs = " | ".join(str(t) for t in tier_assignments)
        lines.append(
            f"| `{cond}` | {score_str} | {tier_strs} | {marker} |"
        )
    suffix = "" if metric == "f1" else f"_{metric}"
    output_path = stratum_dir / f"tier_stability{suffix}.md"
    # A trailing `""` element plus the joined newline emitted two blank
    # lines at end of file, which markdownlint flags as MD012. The single
    # trailing newline below is all a well-formed Markdown file needs.
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    LOGGER.info("Wrote tier-stability table: %s", output_path)

    # JSON sidecar for downstream consumers. ``methodology_note`` is
    # the metric-specific short form of the markdown methodology
    # paragraph; ``fallback_count`` records the legacy
    # primary-JSON-fallback state (always 0 for F1 post-Option-A, equal
    # to the non-primary buffer count for MCC by methodology).
    if metric == "mcc":
        methodology_note = (
            "MCC tiers are buffer-independent by methodology — the "
            "tile-level MCC permutation test does not take a buffer "
            "argument. Spearman rho across buffers is 1.0 by "
            "construction; this is correct, not degenerate."
        )
    else:
        methodology_note = (
            "F1 tiers constructed independently at each buffer using "
            f"per-cell thresholds fixed at the primary buffer "
            f"({DEFAULT_PRIMARY} m) via --threshold-buffer (Option A). "
            "Spearman rho values are substantive."
        )
    summary = {
        "stratum_dir": str(stratum_dir),
        "metric": metric,
        "primary_buffer": DEFAULT_PRIMARY,
        "buffers": BUFFERS,
        "methodology_note": methodology_note,
        "fallback_from_primary_count": fallback_count,
        "n_other_buffers": n_other,
        "spearman": {
            f"{buf}_vs_20": {"rho": rho, "p_value": p}
            for buf, (rho, p) in spearman.items()
        },
        "n_conditions": len(all_conditions),
    }
    output_json = stratum_dir / f"tier_stability{suffix}.json"
    output_json.write_text(
        json.dumps(summary, indent=2, default=str) + "\n",
        encoding="utf-8",
    )

    return output_path, summary


def main() -> int:
    """Build tier-stability tables for one or all populated strata."""
    parser = argparse.ArgumentParser(
        description="Build tier-stability tables (Spearman rank "
                    "correlation across buffers) per stratum + metric.",
    )
    parser.add_argument(
        "--metric", choices=["f1", "mcc"], required=True,
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument(
        "--stratum-dir", type=Path,
        help="Path to stratum directory "
             "(e.g. results/leaderboard/per-architecture/era1/consensus/)",
    )
    target.add_argument(
        "--all", action="store_true",
        help="Build for all 7 populated strata.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if args.all:
        results: list[dict] = []
        for era, arch in POPULATED_STRATA:
            stratum_dir = PER_ARCH_DIR / era / arch
            if not stratum_dir.is_dir():
                LOGGER.warning("Skipping missing stratum: %s", stratum_dir)
                continue
            outcome = build_stability_table(stratum_dir, args.metric)
            if outcome is not None:
                _, summary = outcome
                results.append(summary)
        LOGGER.info("Stability tables built for %d strata", len(results))
    else:
        if not args.stratum_dir.is_dir():
            LOGGER.error("Stratum dir not found: %s", args.stratum_dir)
            return 2
        outcome = build_stability_table(args.stratum_dir, args.metric)
        if outcome is None:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
