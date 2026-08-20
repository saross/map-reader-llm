#!/usr/bin/env python3
"""
Enrich per-architecture leaderboard markdown with metadata columns
====================================================================

Post-processor for `build_tiered_leaderboard.py` output. Reads the
tier JSON files at `results/leaderboard/per-architecture/era<N>/<arch>/
leaderboard_tiers_<buffer>m.json`, joins each condition's metadata from
the condition inventory (proposer model, config_version, verifier prompt,
vote_t, prob_t, etc.), and re-writes the per-buffer markdown tables
with the required columns:

    | # | Condition | Era | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC | Tier |

Also writes a README-adjacent summary JSON per stratum:
    leaderboard_rows_enriched.json

**Ownership** (defect D35, Phase 6): this script is the sole owner of the
per-architecture ``leaderboard_tiers_<buffer>m.md`` boards. The bare-format
writer in ``build_tiered_leaderboard.py`` refuses those paths — see
``build_tiered_leaderboard.PER_ARCH_OWNER`` and
``PerArchitectureOwnershipError``. Before that guard existed the two
generators contested the same seven 20 m paths and the last writer won,
leaving those boards committed in the bare format (audit finding F11).

Usage:
    .venv/bin/python scripts/enrich_per_arch_markdown.py \\
        --root results/leaderboard/per-architecture \\
        --inventory planning/condition-inventory-with-s78.json

Run after `run_per_arch_leaderboards.sh` completes.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

BUFFERS = [20, 30, 40, 50, 100]
ARCHITECTURES = ["single-pass", "consensus", "single-pass+PV", "pv"]
ERAS = [1, 2, 3]

# Architecture display labels for table headers.
ARCH_DISPLAY = {
    "single-pass": "Single-pass (raw)",
    "consensus": "Consensus (no PV)",
    "single-pass+PV": "Single-pass + PV",
    "pv": "Consensus + PV",
}

# Stratum-level notes (printed under each stratum heading).
STRATUM_NOTES = {
    (1, "single-pass+PV"): (
        "**Data sparsity**: No Era-1 single-pass + verifier conditions in "
        "the inventory. The verifier was only introduced at the 384-px "
        "(Era 2 / Era 3) stage of the project."
    ),
    (1, "pv"): (
        "**Data sparsity**: No Era-1 consensus + verifier conditions in "
        "the inventory. The verifier was only introduced at the 384-px "
        "(Era 2 / Era 3) stage of the project."
    ),
    (3, "single-pass"): (
        "**Data sparsity**: No Era-3 single-pass conditions in the "
        "inventory. Era 3 was exclusively used for K=5 consensus "
        "library-design ablations (H8 v2 / H10 v2 / H12 v2)."
    ),
    (3, "single-pass+PV"): (
        "**Data sparsity**: No Era-3 single-pass + verifier conditions "
        "in the inventory."
    ),
    (3, "pv"): (
        "**Data sparsity**: No Era-3 consensus + verifier conditions "
        "in the inventory."
    ),
}


# Timestamp stabilisation — keep no-op regenerations byte-identical.
#
# Mirrors the idea in ``generate_post_run_report.py`` (§ "Timestamp
# stabilisation"): a field stamped to "now" on every run is carried forward
# from the on-disk artefact whenever the *substantive* content is unchanged,
# so a regeneration that corrects one line touches only that line instead of
# re-stamping every board. Without it a no-op re-run rewrites all 60 boards
# and destroys git diff/blame legibility on this family.
_MD_TIMESTAMP_PREFIX = "**Generated**: "

#: Placeholder written into the render before stabilisation decides whether
#: to keep the on-disk stamp or mint a fresh one. Never reaches disk.
_TS_PLACEHOLDER = "\x00TIMESTAMP\x00"


def _strip_md_timestamp(text: str) -> str:
    """Blank the ``**Generated**:`` line so two renders compare on content.

    Args:
        text: Full markdown body.

    Returns:
        The body with the generation stamp replaced by a constant.
    """
    return "\n".join(
        _MD_TIMESTAMP_PREFIX + _TS_PLACEHOLDER
        if line.startswith(_MD_TIMESTAMP_PREFIX)
        else line
        for line in text.split("\n")
    )


def _existing_md_timestamp(path: Path) -> str | None:
    """Return the ``**Generated**:`` value already on disk, if any.

    Args:
        path: Candidate markdown file (may not exist).

    Returns:
        The timestamp string, or None when the file is absent or carries
        no generation stamp.
    """
    if not path.is_file():
        return None
    try:
        for line in path.read_text(encoding="utf-8").split("\n")[:10]:
            if line.startswith(_MD_TIMESTAMP_PREFIX):
                return line[len(_MD_TIMESTAMP_PREFIX):].strip()
    except OSError:
        return None
    return None


def stabilise_markdown(body: str, out_md: Path, now: str,
                       stabilise: bool = True) -> str:
    """Resolve the timestamp placeholder in a rendered board.

    Carries the on-disk stamp forward when the new render is
    content-identical to what is already committed; otherwise mints
    ``now``. This is the markdown analogue of
    ``generate_post_run_report._stabilise_timestamps``.

    Args:
        body: Rendered markdown containing ``_TS_PLACEHOLDER``.
        out_md: Destination path (read, never written, by this function).
        now: Fresh ISO-8601 stamp to use when content changed.
        stabilise: When False, always mint ``now`` (``--fresh-timestamps``).

    Returns:
        The markdown with the placeholder replaced.
    """
    if stabilise and out_md.is_file():
        old = _existing_md_timestamp(out_md)
        try:
            old_body = out_md.read_text(encoding="utf-8")
        except OSError:
            old_body = None
        if old is not None and old_body is not None:
            if _strip_md_timestamp(old_body) == body:
                return body.replace(_TS_PLACEHOLDER, old)
    return body.replace(_TS_PLACEHOLDER, now)


def load_inventory(path: Path) -> dict[str, dict]:
    """Return condition lookup indexed by id."""
    data = json.loads(path.read_text())
    return {row["id"]: row for row in data}


def fmt_value(x, ndigits=3, default="—"):
    """Format a numeric value or fall back to a placeholder."""
    if x is None:
        return default
    if isinstance(x, float):
        return f"{x:.{ndigits}f}"
    return str(x)


def fmt_ci(lo, hi, ndigits=3, default="n/a"):
    """Format a bootstrap 95% CI as `[lo, hi]`."""
    if lo is None or hi is None:
        return default
    return f"[{lo:.{ndigits}f}, {hi:.{ndigits}f}]"


def build_row(
    rank: int,
    cond_dict: dict,
    inv_row: dict,
    buffer_metres: int,
    tier_idx: int,
) -> dict:
    """Assemble one enriched markdown-table row for a condition."""
    evals = cond_dict.get("evaluations", {})
    # evaluations keys may be strings or ints depending on serialisation.
    ev = evals.get(str(buffer_metres)) or evals.get(buffer_metres) or {}

    # Numeric fields
    f1 = ev.get("f1")
    ci_lo = ev.get("f1_ci_lower")
    ci_hi = ev.get("f1_ci_upper")
    p = ev.get("precision")
    r = ev.get("recall")
    mcc = ev.get("mcc")  # may be absent — evaluate_detections exposes it when inputs permit

    # Metadata fields
    meta = inv_row or {}
    track = cond_dict.get("track") or meta.get("track")
    k = cond_dict.get("k") or meta.get("K")
    arch_label = meta.get("architecture", cond_dict.get("category"))
    vote_t = cond_dict.get("best_threshold")
    prob_t = meta.get("prob_t")
    # For PV cells the inventory already stores the vote_t baked into the
    # materialised GeoJSON; override.
    inv_vote = meta.get("vote_t")
    if arch_label == "pv" and inv_vote is not None:
        vote_t = inv_vote
    proposer = meta.get("model") or "—"
    config_version = meta.get("config_version") or "—"
    # Verifier prompt defaults: S78 cells supply verifier_prompt directly.
    # For PV cells sourced from the legacy `verified-v1-n{5,10}` pipeline
    # the verifier is the "canonical" v1 prompt (adversarial-text).
    # For single-pass+PV the `config_version` string already encodes the
    # variant (e.g. `verified-adversarial-image`), so derive from that.
    verifier_prompt = meta.get("verifier_prompt")
    if verifier_prompt is None:
        if arch_label == "pv":
            verifier_prompt = "v1 (adversarial-text canonical)"
        elif arch_label == "single-pass+PV" and config_version != "—":
            # e.g. "verified-adversarial-image" → "adversarial-image"
            if config_version.startswith("verified-"):
                verifier_prompt = config_version[len("verified-"):]
            else:
                verifier_prompt = config_version
        else:
            verifier_prompt = "—"

    # n_detections lives at the evaluation's top level in the cache,
    # but build_tiered_leaderboard serialises evaluations per-buffer only.
    # Fall back to the condition-level field if set (via augmentation).
    n_detections = ev.get("n_detections") or cond_dict.get("n_detections")

    return {
        "rank": rank,
        "tier": tier_idx,
        "condition_id": cond_dict.get("label") or cond_dict.get("condition_id"),
        "era": cond_dict.get("era"),
        "track": track,
        "architecture": arch_label,
        "k": k,
        "vote_t": vote_t,
        "prob_t": prob_t,
        "proposer": proposer,
        "config_version": config_version,
        "verifier_prompt": verifier_prompt,
        "buffer_m": buffer_metres,
        "n_detections": n_detections,
        "f1": f1,
        "f1_ci_lower": ci_lo,
        "f1_ci_upper": ci_hi,
        "precision": p,
        "recall": r,
        "mcc": mcc,
        "geojson": cond_dict.get("geojson"),
        "source_cell": meta.get("pv_sweep_source"),
        "status_inventory": meta.get("status"),
        "notes_inventory": meta.get("notes"),
    }


def write_enriched_markdown(
    tier_json_path: Path,
    buffer_metres: int,
    era: int,
    arch: str,
    inventory: dict[str, dict],
    out_md: Path,
    out_rows_json: Path,
    git_commit: str,
    repo_root: Path | None = None,
    stabilise: bool = True,
) -> int:
    """Read a tier JSON and write the enriched markdown table.

    Args:
        tier_json_path: Source ``leaderboard_tiers_20m.json`` for the stratum.
        buffer_metres: Buffer whose per-buffer metrics fill the score columns.
        era: Era number, for the board heading.
        arch: Architecture key, for the board heading.
        inventory: Condition-inventory lookup from :func:`load_inventory`.
        out_md: Destination board.
        out_rows_json: Destination machine-readable row dump.
        git_commit: Commit hash recorded in the provenance header.
        repo_root: Root the provenance paths are expressed relative to.
            Defaults to the real repository root; overridden by
            ``--repo-root`` so the generator can be exercised against a
            scratch tree without the provenance strings changing.
        stabilise: Carry an unchanged board's existing ``**Generated**``
            stamp forward instead of re-stamping it (see
            :func:`stabilise_markdown`).

    Returns:
        The number of rows written (0 if the input has no tiers /
        no conditions — the caller then writes a stub instead).
    """
    root = repo_root or REPO_ROOT
    data = json.loads(tier_json_path.read_text())
    tiers = data.get("tiers", [])
    metadata = data.get("metadata", {})

    enriched_rows: list[dict] = []
    rank = 0
    for tier_block in tiers:
        tier_idx = tier_block["tier"]
        for cond in tier_block["conditions"]:
            rank += 1
            inv_row = inventory.get(cond["label"], {})
            row = build_row(rank, cond, inv_row, buffer_metres, tier_idx)
            row["source_tier_json"] = str(
                tier_json_path.relative_to(root)
            )
            row["source_git_commit"] = git_commit
            enriched_rows.append(row)

    if not enriched_rows:
        return 0

    now = datetime.now(tz=timezone.utc).isoformat()

    # Write enriched rows as machine-readable JSON (one file per buffer).
    # The ``generated`` stamp is carried forward when the row payload is
    # unchanged, for the same diff-legibility reason as the markdown.
    rows_payload = {
        "script": "enrich_per_arch_markdown.py",
        "generated": now,
        "era": era,
        "architecture": arch,
        "buffer_m": buffer_metres,
        "source_tier_json": str(tier_json_path.relative_to(root)),
        "source_git_commit": git_commit,
        "n_rows": len(enriched_rows),
        "rows": enriched_rows,
    }
    if stabilise and out_rows_json.is_file():
        try:
            old_rows = json.loads(out_rows_json.read_text())
        except (OSError, json.JSONDecodeError):
            old_rows = None
        if isinstance(old_rows, dict):
            if {**old_rows, "generated": now} == rows_payload:
                rows_payload["generated"] = old_rows.get("generated", now)
    out_rows_json.parent.mkdir(parents=True, exist_ok=True)
    out_rows_json.write_text(json.dumps(rows_payload, indent=2))

    # Write enriched markdown.
    arch_display = ARCH_DISPLAY.get(arch, arch)
    lines: list[str] = []
    lines.append(
        f"# Leaderboard — Era {era}, {arch_display}, {buffer_metres} m buffer"
    )
    lines.append("")
    lines.append(f"{_MD_TIMESTAMP_PREFIX}{_TS_PLACEHOLDER}")
    lines.append(f"**Source tier JSON**: `{tier_json_path.relative_to(root)}`")
    lines.append(f"**Git commit**: `{git_commit}`")
    lines.append(
        f"**Conditions**: {len(enriched_rows)} in {len(tiers)} tier(s). "
        f"Bounds: `{metadata.get('bounds', '—')}`."
    )
    lines.append("")
    lines.append(
        "Tiering at 20 m: greedy-clique BH-FDR on tile-level paired "
        "permutation tests (10,000 permutations, seed 42) at q=0.05. "
        "Bootstrap 95% CIs (1,000 iterations) recomputed per buffer."
    )
    if (era, arch) in STRATUM_NOTES:
        lines.append("")
        lines.append(STRATUM_NOTES[(era, arch)])
    lines.append("")

    # Group rows by tier and emit per-tier sections.
    tier_groups: dict[int, list[dict]] = {}
    for row in enriched_rows:
        tier_groups.setdefault(row["tier"], []).append(row)

    for tier_idx in sorted(tier_groups.keys()):
        rows = tier_groups[tier_idx]
        f1_vals = [r["f1"] for r in rows if r["f1"] is not None]
        f1_min = min(f1_vals) if f1_vals else 0.0
        f1_max = max(f1_vals) if f1_vals else 0.0

        lines.append(
            f"## Tier {tier_idx} (F1: {f1_min:.3f}–{f1_max:.3f})"
        )
        lines.append("")
        lines.append(
            "| # | Condition | Track | K | Vote t | Proposer | "
            "Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |"
        )
        lines.append(
            "|--:|-----------|:-----:|--:|:-----:|:---------|"
            ":-------|:--------:|:-----:|:-----------:|---:|---:|---:|"
        )

        for row in rows:
            f1_str = fmt_value(row["f1"], 3, "—")
            ci_str = fmt_ci(row["f1_ci_lower"], row["f1_ci_upper"])
            p_str = fmt_value(row["precision"], 3, "—")
            r_str = fmt_value(row["recall"], 3, "—")
            mcc_str = fmt_value(row["mcc"], 3, "—")
            vote_t_str = fmt_value(row["vote_t"], 0, "—")
            prob_t_str = fmt_value(row["prob_t"], 2, "—")
            lines.append(
                f"| {row['rank']} | {row['condition_id']} | {row['track']} | "
                f"{row['k']} | {vote_t_str} | "
                f"{row['proposer']} | {row['config_version']} | "
                f"{row['verifier_prompt']} | {prob_t_str} | "
                f"{f1_str} {ci_str} | {p_str} | {r_str} | {mcc_str} |"
            )
        lines.append("")

    # Add footnotes
    lines.append("---")
    lines.append("")
    lines.append("### Column reference")
    lines.append("")
    lines.append(
        "- **Vote t** — proposer-consensus vote threshold selected (the "
        "`t` value at which this condition's F1 at 20 m is maximal; "
        "for `single-pass` and `single-pass+PV` this is always 1)."
    )
    lines.append(
        "- **Proposer** — proposer model (Gemini 3 Flash for the vast "
        "majority of the corpus)."
    )
    lines.append(
        "- **Config** — the `config_version` string from the condition "
        "inventory — identifies the prompt library and major variant."
    )
    lines.append(
        "- **Verifier** — for PV pipelines, the verifier prompt label "
        "(`v1` = the canonical adversarial-text verifier; "
        "`session-78-<variant>` = one of the 7 S78 matrix verifiers)."
    )
    lines.append(
        "- **Prob t** — verifier probability threshold (optimal at 20 m "
        "for each PV cell; `—` for non-PV architectures)."
    )
    lines.append(
        "- **MCC** — Matthews Correlation Coefficient at the buffer. "
        "`—` when `evaluate_detections.py` did not emit MCC for this "
        "condition (legacy evaluation outputs, primarily Era 1)."
    )
    lines.append("")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(
        stabilise_markdown("\n".join(lines), out_md, now, stabilise=stabilise)
    )
    return len(enriched_rows)


def write_stub_markdown(
    era: int, arch: str, buffer_metres: int, out_md: Path, reason: str,
    stabilise: bool = True,
) -> None:
    """Emit a placeholder markdown for empty strata.

    Args:
        era: Era number.
        arch: Architecture key.
        buffer_metres: Buffer the stub stands in for.
        out_md: Destination path.
        reason: Sparsity explanation shown under the heading.
        stabilise: Carry an unchanged stub's existing stamp forward.
    """
    arch_display = ARCH_DISPLAY.get(arch, arch)
    lines = [
        f"# Leaderboard — Era {era}, {arch_display}, {buffer_metres} m buffer",
        "",
        f"{_MD_TIMESTAMP_PREFIX}{_TS_PLACEHOLDER}",
        "",
        "## No conditions",
        "",
        reason,
        "",
    ]
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(
        stabilise_markdown(
            "\n".join(lines),
            out_md,
            datetime.now(tz=timezone.utc).isoformat(),
            stabilise=stabilise,
        )
    )


def main() -> int:
    """Enrich every per-architecture tier JSON into a paper-ready markdown."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT / "results/leaderboard/per-architecture",
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=REPO_ROOT / "planning/condition-inventory-with-s78.json",
    )
    parser.add_argument(
        "--git-commit",
        type=str,
        default="(uncommitted)",
        help="Git commit hash to record in the row provenance.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help=(
            "Root that provenance paths are expressed relative to. Override "
            "only to exercise the generator against a scratch tree."
        ),
    )
    parser.add_argument(
        "--fresh-timestamps",
        action="store_true",
        help=(
            "Re-stamp every board even when its content is unchanged "
            "(default: carry the on-disk stamp forward, so a no-op "
            "regeneration is byte-identical)."
        ),
    )
    args = parser.parse_args()

    stabilise = not args.fresh_timestamps
    inventory = load_inventory(args.inventory)

    summary_rows: list[dict] = []

    for era in ERAS:
        for arch in ARCHITECTURES:
            strat_dir = args.root / f"era{era}" / arch
            strat_dir.mkdir(parents=True, exist_ok=True)

            tier_json = strat_dir / f"leaderboard_tiers_{20}m.json"
            for buf in BUFFERS:
                out_md = strat_dir / f"leaderboard_tiers_{buf}m.md"
                out_rows_json = strat_dir / f"leaderboard_rows_{buf}m.json"

                if not tier_json.is_file():
                    # No tier JSON — stub the output.
                    reason = STRATUM_NOTES.get(
                        (era, arch),
                        (
                            "No conditions resolved for this "
                            f"(Era {era}, {arch}) stratum. The inventory "
                            "contains no matching entries."
                        ),
                    )
                    write_stub_markdown(
                        era, arch, buf, out_md, reason, stabilise=stabilise
                    )
                    summary_rows.append(
                        {
                            "era": era,
                            "arch": arch,
                            "buffer_m": buf,
                            "status": "STUB",
                            "n_rows": 0,
                        }
                    )
                    continue

                n = write_enriched_markdown(
                    tier_json,
                    buf,
                    era,
                    arch,
                    inventory,
                    out_md,
                    out_rows_json,
                    args.git_commit,
                    repo_root=args.repo_root,
                    stabilise=stabilise,
                )
                summary_rows.append(
                    {
                        "era": era,
                        "arch": arch,
                        "buffer_m": buf,
                        "status": "OK" if n > 0 else "EMPTY",
                        "n_rows": n,
                    }
                )
                print(
                    f"  era{era}/{arch}/buffer={buf}m: {n} rows → {out_md.name}"
                )

    # Write overall enrichment summary (timestamp stabilised, as above).
    summary_path = args.root / "enrichment_summary.json"
    now = datetime.now(tz=timezone.utc).isoformat()
    summary_payload = {
        "script": "enrich_per_arch_markdown.py",
        "generated": now,
        "strata": summary_rows,
    }
    if stabilise and summary_path.is_file():
        try:
            old_summary = json.loads(summary_path.read_text())
        except (OSError, json.JSONDecodeError):
            old_summary = None
        if isinstance(old_summary, dict):
            if {**old_summary, "generated": now} == summary_payload:
                summary_payload["generated"] = old_summary.get("generated", now)
    summary_path.write_text(json.dumps(summary_payload, indent=2))
    print(f"\nSummary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
