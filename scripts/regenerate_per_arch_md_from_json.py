#!/usr/bin/env python3
"""
Regenerate Per-Architecture Leaderboard Markdown Tables from JSON
==================================================================

Fixes Task #13 (the per-architecture leaderboard MD tier-table
overwrite bug). Stage 1 of the per-buffer F1 re-tiering work
(commits up to ``ccc320ea``) ran ``build_tiered_leaderboard.py``
once per (stratum, primary buffer, q-level), passing
``--buffers 20 30 40 50 100`` on every invocation. The MD writer
loops over *all* listed buffers each pass, so every later pass
overwrites the earlier passes' MD files with its own primary-buffer
tiering — but with each MD's own buffer-specific F1 column. Net
effect: per-stratum MD files at non-final-pass buffers display the
LAST pass's tier composition with the LOCAL buffer's F1 metrics.

The corresponding JSON files are correct (each pass writes only one
JSON, named for that pass's primary buffer). This script reads each
JSON, reconstructs ``SelectedCondition`` instances, and re-renders
the MD so formatting matches a fresh build.

Ownership (defect D35, Phase 6)
-------------------------------

Two generators used to write the per-architecture markdown, so the
last one to run won. ``results/leaderboard/per-architecture/**``
``leaderboard_tiers_<buffer>m.md`` boards are now owned by
``scripts/enrich_per_arch_markdown.py`` (the richer, later writer:
provenance header naming the source tier JSON, git commit, and
bounds, plus proposer/config/verifier/threshold metadata columns).
The bare writer in ``build_tiered_leaderboard.py`` refuses those
paths. Consequences for this script:

- **Owned boards** (``leaderboard_tiers_<buffer>m.md``) render through
  the owner, from the stratum's 20 m tier JSON — the source the owner
  records in its header, and the source of the tiering that the
  per-buffer boards display metrics against. ``--write`` refuses them.
- **Unowned boards** in the same tree — the ``_mcc`` and ``_q01``
  variants, which the owner does not render — keep the bare renderer
  and remain writable here.

Verification (defect D35)
-------------------------

``--verify`` used to fall through to the write loop and then compare
the files it had just written against the JSON it had just rendered:
"140 OK, 0 mismatch" was structurally guaranteed, and running it
overwrote 140 tracked files, 28 of which lost the owner's header and
columns. ``--verify`` now renders into a temporary directory outside
the repository, compares the rendered text against the committed file,
reports per-file match/mismatch, and exits non-zero on any drift —
**writing nothing** into the working tree. The ``**Generated**``
stamp is normalised out of the comparison (it is "now" on every
render, and carries no content).

Scope:

- Walks the 7 populated per-architecture strata
  (era1/single-pass, era1/consensus, era2/single-pass,
  era2/consensus, era2/single-pass+PV, era2/pv, era3/consensus).
- For each stratum, covers every ``leaderboard_tiers*.md`` for
  which a sibling ``.json`` exists: F1 q=0.05, F1 q=0.01, MCC
  q=0.05, and MCC q=0.01 at every buffer the JSON exists for.
- The ``leaderboard_all_evaluations.json`` file is left untouched —
  it has no MD sibling.

The MCC MDs at non-20 m buffers do not have a sibling JSON, but they
were also written by the buggy loop. Because MCC tier composition is
buffer-invariant in this codebase, the MCC MDs at all 5 buffers
share the same tier composition; the per-buffer F1 column rightly
varies. Those MDs are rendered by reading the 20 m MCC JSON and
re-rendering at each buffer it appeared at.

Usage::

    python scripts/regenerate_per_arch_md_from_json.py --verify
    python scripts/regenerate_per_arch_md_from_json.py --dry-run
    python scripts/regenerate_per_arch_md_from_json.py --write

Exit codes::

    0  all good
    2  --verify found drift
    3  --write was asked to write an owner-held board

Author: Claude Code (Opus 4.7)
Created: 2026-04-26
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from build_tiered_leaderboard import (  # noqa: E402
    PER_ARCH_OWNER,
    PerArchitectureOwnershipError,
    SelectedCondition,
    is_per_architecture_owned_markdown,
    write_leaderboard_markdown,
)
from enrich_per_arch_markdown import (  # noqa: E402
    load_inventory,
    write_enriched_markdown,
)

# The 7 strata that have full per-buffer leaderboards. The remaining
# 5 directories under ``results/leaderboard/per-architecture/`` exist
# as placeholders only (1 file each — typically a README) and are
# excluded.
POPULATED_STRATA = [
    Path("era1") / "single-pass",
    Path("era1") / "consensus",
    Path("era2") / "single-pass",
    Path("era2") / "consensus",
    Path("era2") / "single-pass+PV",
    Path("era2") / "pv",
    Path("era3") / "consensus",
]

PER_ARCH_ROOT = (
    PROJECT_ROOT / "results" / "leaderboard" / "per-architecture"
)

DEFAULT_INVENTORY = PROJECT_ROOT / "planning" / "condition-inventory-with-s78.json"

# All buffers used in the per-arch builds. The MCC JSON is only
# written at 20 m (one MCC pass per stratum), but the buggy loop
# wrote MCC MDs at all 5 buffers; so when the MCC JSON exists, we
# re-render MD at every buffer in this list.
ALL_BUFFERS = [20, 30, 40, 50, 100]

#: The owner renders every per-buffer board from the stratum's 20 m tier
#: JSON — tiering is established at 20 m and the other buffers re-display
#: the same tier composition with their own metrics.
OWNER_SOURCE_JSON_NAME = "leaderboard_tiers_20m.json"

#: The generation stamp is "now" on every render and carries no content, so
#: it is normalised out before comparing a render against the committed file.
_GENERATED_LINE_RE = re.compile(r"^\*\*Generated\*\*:.*$", re.MULTILINE)

#: The owner stamps the commit it was run at. On a verify pass we reuse the
#: committed value so a provenance-only difference is not reported as drift.
_GIT_COMMIT_LINE_RE = re.compile(r"^\*\*Git commit\*\*: `(.+)`$", re.MULTILINE)


def reconstruct_selected_conditions(
    tier_dict_list: list[dict],
) -> list[SelectedCondition]:
    """Rebuild ``SelectedCondition`` instances from a JSON tier list.

    JSON serialises ``evaluations`` keys as strings (because JSON
    object keys are strings); the renderer expects ``int`` keys, so
    we convert them back here. ``geojson_path`` is rebuilt as a
    ``Path``.

    Args:
        tier_dict_list: One element of ``leaderboard_tiers_*m.json``
            ``tiers[].conditions`` array.

    Returns:
        List of ``SelectedCondition`` ready for
        ``write_leaderboard_markdown``.
    """
    out: list[SelectedCondition] = []
    for c in tier_dict_list:
        evaluations_int_keys = {
            int(k): v for k, v in c.get("evaluations", {}).items()
        }
        out.append(
            SelectedCondition(
                label=c["label"],
                geojson_path=Path(c["geojson"]),
                best_threshold=int(c["best_threshold"]),
                era=int(c["era"]),
                track=str(c["track"]),
                category=str(c["category"]),
                k=int(c["k"]),
                evaluations=evaluations_int_keys,
                condition_id="",  # Not stored in JSON; not needed by MD writer.
                # Erratum E81: ``null`` means the tile MCC is
                # undefined for this condition; preserve it as
                # ``None`` so the renderer prints "undefined"
                # rather than crashing on ``float(None)`` or
                # reporting a chance-level 0.000.
                tile_mcc=(
                    None if c.get("tile_mcc") is None
                    else float(c["tile_mcc"])
                ),
            )
        )
    return out


# Filename pattern parses out the q-level infix ("" or "_q01") and
# the buffer in metres, matching the writer-side template:
#   leaderboard_tiers{metric_infix}{fdr_infix}_{buf_m}m.{md|json}
# where metric_infix is "" for F1 and "_mcc" for MCC, and fdr_infix
# is "" for q=0.05 and "_q01" for q=0.01.
_PATTERN_JSON = re.compile(
    r"^leaderboard_tiers"
    r"(?P<metric_infix>(?:_mcc)?)"
    r"(?P<fdr_infix>(?:_q\d{2})?)"
    r"_(?P<buf>\d+)m\.json$"
)


def discover_md_targets_for_stratum(
    stratum_dir: Path,
) -> list[tuple[Path, Path, int]]:
    """Find every (json_source, md_target, buffer_metres) to render.

    For each JSON file in the stratum:

    - F1 JSON at buffer B → render MD at buffer B (one target).
    - MCC JSON at buffer B → render MD at every buffer in
      ``ALL_BUFFERS`` (because the buggy loop wrote MCC MDs at all
      5 buffers from a single MCC pass; we restore the same set,
      but with correct content).

    Args:
        stratum_dir: The per-architecture stratum directory.

    Returns:
        List of (json_path, md_path, buffer_metres_to_render) tuples.
        ``buffer_metres_to_render`` may differ from the JSON's own
        buffer in the MCC case.
    """
    targets: list[tuple[Path, Path, int]] = []
    if not stratum_dir.is_dir():
        return targets

    for json_path in sorted(stratum_dir.glob("leaderboard_tiers*.json")):
        m = _PATTERN_JSON.match(json_path.name)
        if not m:
            # ``leaderboard_all_evaluations.json`` and other files
            # do not match the per-buffer pattern — skip silently.
            continue
        metric_infix = m.group("metric_infix")
        fdr_infix = m.group("fdr_infix")
        json_buf = int(m.group("buf"))

        # The MD filename mirrors the JSON filename with .md suffix
        # at each rendered buffer.
        if metric_infix == "_mcc":
            buffers_to_render = ALL_BUFFERS
        else:
            buffers_to_render = [json_buf]

        for buf_m in buffers_to_render:
            md_name = (
                f"leaderboard_tiers{metric_infix}{fdr_infix}_{buf_m}m.md"
            )
            md_path = stratum_dir / md_name
            targets.append((json_path, md_path, buf_m))

    return targets


def normalise_for_compare(text: str, git_commit: str | None = None) -> str:
    """Strip volatile provenance so two renders compare on content.

    Args:
        text: Markdown body.
        git_commit: When given, rewrite the ``**Git commit**`` line to this
            value, so a render made at a different checkout is not reported
            as content drift.

    Returns:
        The body with the generation stamp blanked and, optionally, the
        commit line pinned.
    """
    out = _GENERATED_LINE_RE.sub("**Generated**: <normalised>", text)
    if git_commit is not None:
        out = _GIT_COMMIT_LINE_RE.sub(
            f"**Git commit**: `{git_commit}`", out
        )
    return out


def committed_git_commit(md_path: Path) -> str:
    """Return the ``**Git commit**`` value recorded in a committed board.

    Args:
        md_path: Board to read (may not exist).

    Returns:
        The recorded hash, or ``"(uncommitted)"`` — the owner's own default
        — when the file is absent or carries no such line.
    """
    if not md_path.is_file():
        return "(uncommitted)"
    m = _GIT_COMMIT_LINE_RE.search(md_path.read_text(encoding="utf-8"))
    return m.group(1) if m else "(uncommitted)"


def stratum_era_arch(md_path: Path) -> tuple[int, str]:
    """Derive (era, architecture) from a per-architecture board path.

    Args:
        md_path: A board under ``.../per-architecture/era<N>/<arch>/``.

    Returns:
        Tuple of era number and architecture key.

    Raises:
        ValueError: If the path does not carry an ``era<N>`` component.
    """
    arch = md_path.parent.name
    era_dir = md_path.parent.parent.name
    if not era_dir.startswith("era"):
        raise ValueError(f"cannot derive era from {md_path}")
    return int(era_dir[len("era"):]), arch


def render_markdown(
    json_path: Path,
    md_path: Path,
    buffer_metres: int,
    tmp_dir: Path,
    inventory: dict[str, dict] | None = None,
) -> str:
    """Render one board into ``tmp_dir`` and return its text.

    Nothing is written inside the repository: the destination handed to
    the renderer is a scratch path, which is also why the ownership guard
    in ``write_leaderboard_markdown`` does not fire here.

    Owner-held boards (``leaderboard_tiers_<buffer>m.md`` under
    ``results/leaderboard/per-architecture/``) render through
    ``enrich_per_arch_markdown``, from the stratum's 20 m tier JSON;
    everything else renders through the bare writer from ``json_path``.

    Args:
        json_path: Source JSON for the bare renderer.
        md_path: The real destination — used to decide ownership, to derive
            era/architecture, and to carry the committed commit hash forward.
        buffer_metres: Buffer whose metrics fill the score columns.
        tmp_dir: Scratch directory to render into.
        inventory: Condition inventory for the owner's metadata columns.
            Loaded on demand when omitted.

    Returns:
        The rendered markdown text.
    """
    scratch_md = tmp_dir / md_path.name

    if is_per_architecture_owned_markdown(md_path):
        owner_json = md_path.parent / OWNER_SOURCE_JSON_NAME
        era, arch = stratum_era_arch(md_path)
        if inventory is None:
            inventory = load_inventory(DEFAULT_INVENTORY)
        write_enriched_markdown(
            owner_json,
            buffer_metres,
            era,
            arch,
            inventory,
            scratch_md,
            tmp_dir / f"rows_{buffer_metres}m.json",
            committed_git_commit(md_path),
            repo_root=PROJECT_ROOT,
            stabilise=False,
        )
        return scratch_md.read_text(encoding="utf-8")

    with json_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    metadata = dict(payload.get("metadata", {}))
    tiers = [
        reconstruct_selected_conditions(t.get("conditions", []))
        for t in payload.get("tiers", [])
    ]
    write_leaderboard_markdown(
        tiers=tiers,
        buffer_metres=buffer_metres,
        output_path=scratch_md,
        metadata=metadata,
    )
    return scratch_md.read_text(encoding="utf-8")


def verify_targets(
    targets: list[tuple[Path, Path, int]],
    inventory: dict[str, dict] | None = None,
) -> tuple[int, int, int, list[str]]:
    """Compare every target's committed board against a fresh render.

    Renders into a temporary directory and never writes into the working
    tree — the defect this function exists to close is a "verify" that
    wrote its own expected output first.

    Args:
        targets: Tuples from :func:`discover_md_targets_for_stratum`.
        inventory: Condition inventory, loaded on demand when omitted.

    Returns:
        Tuple of (n_ok, n_mismatch, n_missing, per-file report lines).
    """
    n_ok = n_mismatch = n_missing = 0
    report: list[str] = []
    seen: set[Path] = set()

    with tempfile.TemporaryDirectory(prefix="per-arch-verify-") as tmp:
        tmp_dir = Path(tmp)
        for json_path, md_path, buf in targets:
            if md_path in seen:
                continue
            seen.add(md_path)

            try:
                rel = md_path.relative_to(PROJECT_ROOT)
            except ValueError:
                rel = md_path

            if not md_path.is_file():
                n_missing += 1
                report.append(f"  MISSING   {rel}")
                continue

            rendered = render_markdown(
                json_path, md_path, buf, tmp_dir, inventory=inventory
            )
            committed = md_path.read_text(encoding="utf-8")
            if normalise_for_compare(rendered) == normalise_for_compare(committed):
                n_ok += 1
                report.append(f"  OK        {rel}")
            else:
                n_mismatch += 1
                report.append(f"  MISMATCH  {rel}")

    return n_ok, n_mismatch, n_missing, report


def write_targets(
    targets: list[tuple[Path, Path, int]],
) -> tuple[int, int, list[str]]:
    """Write every writable target, refusing owner-held boards.

    Args:
        targets: Tuples from :func:`discover_md_targets_for_stratum`.

    Returns:
        Tuple of (n_written, n_refused, per-file report lines).
    """
    n_written = n_refused = 0
    report: list[str] = []
    for json_path, md_path, buf in targets:
        try:
            rel = md_path.relative_to(PROJECT_ROOT)
        except ValueError:
            rel = md_path

        if is_per_architecture_owned_markdown(md_path):
            n_refused += 1
            report.append(f"  REFUSED   {rel} — owned by {PER_ARCH_OWNER}")
            continue

        with json_path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        metadata = dict(payload.get("metadata", {}))
        tiers = [
            reconstruct_selected_conditions(t.get("conditions", []))
            for t in payload.get("tiers", [])
        ]
        try:
            write_leaderboard_markdown(
                tiers=tiers,
                buffer_metres=buf,
                output_path=md_path,
                metadata=metadata,
            )
        except PerArchitectureOwnershipError as exc:
            # Belt and braces: the pre-check above should have caught it.
            n_refused += 1
            report.append(f"  REFUSED   {rel} — {exc}")
            continue
        n_written += 1
        report.append(f"  wrote     {rel}")
    return n_written, n_refused, report


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. See the module docstring for exit codes."""
    parser = argparse.ArgumentParser(
        description="Regenerate or verify per-arch leaderboard MDs from JSON.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="List the files in scope without rendering or writing.",
    )
    mode.add_argument(
        "--verify",
        action="store_true",
        help=(
            "Render to a temporary directory and compare against the "
            "committed boards. Writes nothing; exits 2 on any drift."
        ),
    )
    mode.add_argument(
        "--write",
        action="store_true",
        help=(
            "Write the boards this script still owns. Per-architecture "
            f"leaderboard_tiers_<buffer>m.md boards belong to "
            f"{PER_ARCH_OWNER} and are refused."
        ),
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=DEFAULT_INVENTORY,
        help="Condition inventory used for the owner's metadata columns.",
    )
    args = parser.parse_args(argv)

    all_targets: list[tuple[Path, Path, int]] = []
    for stratum in POPULATED_STRATA:
        all_targets.extend(
            discover_md_targets_for_stratum(PER_ARCH_ROOT / stratum)
        )

    print(f"Discovered {len(all_targets)} MD targets across "
          f"{len(POPULATED_STRATA)} populated strata.")

    if args.dry_run:
        for json_path, md_path, buf in all_targets:
            owner = (
                PER_ARCH_OWNER
                if is_per_architecture_owned_markdown(md_path)
                else "scripts/build_tiered_leaderboard.py"
            )
            print(f"  {md_path.relative_to(PROJECT_ROOT)} @ {buf}m  "
                  f"<-  {json_path.name}  [owner: {owner}]")
        return 0

    if args.verify:
        inventory = load_inventory(args.inventory)
        n_ok, n_mismatch, n_missing, report = verify_targets(
            all_targets, inventory=inventory
        )
        for line in report:
            print(line)
        print(f"Verification: {n_ok} OK, {n_mismatch} mismatch, "
              f"{n_missing} missing (of {n_ok + n_mismatch + n_missing} boards). "
              "Nothing written.")
        return 2 if (n_mismatch or n_missing) else 0

    if not args.write:
        parser.error("choose one of --verify, --write, or --dry-run")

    n_written, n_refused, report = write_targets(all_targets)
    for line in report:
        print(line)
    print(f"Wrote {n_written} MD files; refused {n_refused}.")
    if n_refused:
        print(
            f"Refused boards are owned by {PER_ARCH_OWNER} — run that "
            "generator to rebuild them.",
            file=sys.stderr,
        )
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
