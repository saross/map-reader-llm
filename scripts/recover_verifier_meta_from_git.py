#!/usr/bin/env python3
"""
Recover pre-overwrite verifier metadata from git history.

Why this script exists
----------------------
Before 2026-09-14 a second pass over a verifier stage (``run_pv.py cleanup``,
or ``run_pv.py verify`` re-invoked over the same output directory) rewrote
``run.meta.json`` with only that pass's usage, destroying the main pass's
token load. ``reports/cleanup-meta-fix-2026-09-14.md`` section 4 censuses the
damage: 29 stages, of which 26 hold nothing on disc from which the main pass
can be reconstructed.

The repository commits ``outputs/**``, so a stage committed *before* the
overwrite still carries the pre-overwrite metadata as a git blob. This script
walks history for every damaged stage, extracts every historical blob of every
metadata-shaped file in the stage directory, and decides per stage:

    RECOVERED-FROM-GIT   a historical blob carries a pass with non-zero
                         ``usage_stats`` that accounts for the shortfall
    PARTIALLY-RECOVERED  such a blob exists but covers less than the
                         shortfall
    NOT-IN-HISTORY       no historical blob carries the main pass's tokens,
                         either because the meta was overwritten before the
                         stage's first commit, or because the main pass ran
                         through the Batch Application Programming Interface
                         (API), which returns no per-response usage and so
                         recorded an all-zero meta that was never wrong

Output is a **recovery register** — the file
``outputs/verifier-meta-recovery-2026-09-14.json`` — which
``scripts/audit_verifier_cost.py`` reads as a third source of passes, after
the fixed merged schema and the legacy backup convention. No committed
``run.meta.json`` is ever rewritten: the register sits beside the stages and
records what history holds.

Two reconstructions, clearly separated
--------------------------------------
* ``recovered_passes`` carry a blob's ``usage_stats`` **verbatim**, so the
  money is exact. Only the item count is reconstructed: the pre-2026-05
  tracker did not increment ``items_processed``, counting outcomes in
  ``finish_reason_counts`` instead, and that count can exceed the stage's
  missing-candidate count by one to three where a call succeeded but its
  result was superseded. ``items_processed_source`` names the field used.
* ``residual_estimate`` is an **estimate, never an audit**: the missing
  candidates priced at the per-candidate token rates of the pass that DID
  survive in the same stage, under the same configuration over the same
  crops. It is recorded for the stages history cannot recover and is never
  counted into any audited total.

Billing-export planning
-----------------------
For a stage history cannot recover, a project-filtered Google Cloud daily
export can still bound the cost when the day's spend on that model is
otherwise accounted for. The register therefore records, per unrecoverable
stage, the candidate billing days (Pacific time, which is the basis the
project's billing exports use — ``reports/billing-reconciliation-2026-09-11.md``
section 3.1) and every other run of the same model on those days, flagged by
whether its own metadata records its tokens.

Usage
-----
::

    # 1. Census the damage (on a machine holding outputs/)
    python scripts/audit_verifier_cost.py --sweep outputs --json > sweep.json

    # 2. Recover what history holds (on a machine holding the git history)
    python scripts/recover_verifier_meta_from_git.py \\
        --sweep sweep.json --repo . \\
        --out outputs/verifier-meta-recovery-2026-09-14.json

    # Restrict to named stages (default: every UNRECOVERABLE stage in the
    # sweep), e.g. to exclude stages already recovered by sibling
    # adjudication:
    python scripts/recover_verifier_meta_from_git.py \\
        --sweep sweep.json --stages-file stages.txt --out register.json

Author: Claude Code, for Shawn Ross
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

__version__ = "1.0.0"

#: Schema tag written into the register, so a reader can tell which
#: reconstruction contract the file was produced under.
REGISTER_SCHEMA = "verifier-meta-recovery/1"

#: Name fragments that mark a file in a stage directory as metadata-shaped
#: and therefore worth extracting from history.
META_NAME_FRAGMENTS: tuple[str, ...] = (
    "meta", "backup", ".log", ".nohup", "usage", "cost",
)

#: The four token fields the audited cost basis needs
#: (``reports/token-load-audit-2026-06-12.md`` section 2), plus the total.
USAGE_FIELDS: tuple[str, ...] = (
    "total_input_tokens",
    "total_cached_tokens",
    "total_output_tokens",
    "total_thoughts_tokens",
    "total_tokens",
)

#: Offset of the Pacific billing day from Coordinated Universal Time (UTC).
#: Google bills daily spend on Pacific days and the project's exports are on
#: that basis; every stage window in this repository is recorded in UTC. The
#: offset is Pacific Daylight Time, which covers every date this register
#: touches (March to September 2026); a winter date would need -8.
PACIFIC_OFFSET = timedelta(hours=-7)


def git(repo: Path, *args: str) -> str:
    """Run a read-only git command in *repo* and return its stdout.

    Args:
        repo: Repository (or worktree) to run in.
        *args: Arguments after ``git``.

    Returns:
        Standard output, empty on failure (the caller decides whether an
        empty result is fatal).
    """
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0 and not result.stdout:
        print(
            f"warning: git {' '.join(args[:3])} failed: "
            f"{result.stderr.strip()[:200]}",
            file=sys.stderr,
        )
    return result.stdout


def stage_history(
    repo: Path, stages: list[str],
) -> dict[str, list[dict[str, str]]]:
    """Every commit touching any file under each stage directory.

    One history walk covers every stage: this repository carries more than
    140,000 commits over a 25 GB tree, and a walk per stage would be an hour
    of work for the same answer.

    Args:
        repo: Repository holding the history.
        stages: Stage directories, repository-relative.

    Returns:
        Stage path to a list of ``{commit, date, subject, status, path}``
        rows, newest first (git log order).
    """
    out = git(
        repo, "log", "--all", "--date-order", "-M",
        "--pretty=format:@@@|%H|%cI|%s", "--name-status", "--", *stages,
    )
    rows: dict[str, list[dict[str, str]]] = {stage: [] for stage in stages}
    commit: dict[str, str] | None = None
    for line in out.splitlines():
        if line.startswith("@@@|"):
            _, sha, date, subject = line.split("|", 3)
            commit = {"commit": sha, "date": date, "subject": subject}
            continue
        if not line.strip() or commit is None:
            continue
        fields = line.split("\t")
        status, paths = fields[0], fields[1:]
        for path in paths:
            for stage in stages:
                if path.startswith(stage.rstrip("/") + "/"):
                    rows[stage].append(
                        {**commit, "status": status, "path": path},
                    )
    return rows


def blob_at(repo: Path, commit: str, path: str) -> str | None:
    """Blob hash of *path* at *commit*, or None when the path is absent."""
    return git(repo, "rev-parse", f"{commit}:{path}").strip() or None


def read_blob(repo: Path, blob: str) -> dict[str, Any]:
    """Parse one blob as a JSON object, or return an empty dict."""
    raw = git(repo, "cat-file", "blob", blob)
    try:
        loaded = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def coverage_of(meta: dict[str, Any]) -> tuple[int, str]:
    """Candidates a pass covered, and the field the count came from.

    ``execution_stats.items_processed`` is authoritative when positive. The
    pre-2026-05 tracker left it at zero and counted outcomes in
    ``finish_reason_counts`` instead, so that is the fallback; a blob with
    neither records no coverage at all.

    Args:
        meta: A run metadata object.

    Returns:
        The count, and a human-readable provenance string.
    """
    execution = meta.get("execution_stats") or {}
    processed = execution.get("items_processed") or 0
    if processed > 0:
        return processed, "execution_stats.items_processed"
    success = (execution.get("finish_reason_counts") or {}).get("success") or 0
    if success > 0:
        return success, "execution_stats.finish_reason_counts.success"
    requests = (
        ((meta.get("usage_stats") or {}).get("by_provider") or {})
        .get("google_gemini") or {}
    ).get("request_count") or 0
    return 0, f"none recorded (api requests: {requests})"


def usage_of(meta: dict[str, Any]) -> dict[str, int]:
    """The token fields the audited basis needs, zero-filled."""
    usage = meta.get("usage_stats") or {}
    return {field: usage.get(field) or 0 for field in USAGE_FIELDS}


def pacific_day(timestamp: str | None) -> str | None:
    """The Pacific billing day a UTC timestamp falls on.

    Args:
        timestamp: An ISO-8601 UTC timestamp, or None.

    Returns:
        ``YYYY-MM-DD`` in Pacific time, or None when the input is unusable.
    """
    if not timestamp:
        return None
    try:
        moment = datetime.fromisoformat(timestamp)
    except ValueError:
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return (moment.astimezone(timezone.utc) + PACIFIC_OFFSET).strftime(
        "%Y-%m-%d",
    )


def residual_estimate(
    surviving: dict[str, Any], missing: int,
) -> dict[str, Any] | None:
    """Estimate the missing candidates' token load from the surviving pass.

    The surviving pass ran the same configuration over crops from the same
    pool, so its per-candidate token rates are the best available estimator
    for the candidates whose load was destroyed. This is an ESTIMATE and is
    never counted into an audited total.

    Args:
        surviving: The stage's surviving ``run.meta.json`` contents.
        missing: Candidates no pass on disc accounts for.

    Returns:
        The estimate, or None when the surviving pass covers nothing.
    """
    covered, _ = coverage_of(surviving)
    usage = usage_of(surviving)
    if not covered or not usage["total_input_tokens"]:
        return None
    per_candidate = {
        field: usage[field] / covered for field in USAGE_FIELDS
    }
    return {
        "basis": (
            "the stage's surviving pass, scaled by candidate count: "
            f"{covered} candidates at "
            f"{per_candidate['total_input_tokens']:.1f} input, "
            f"{per_candidate['total_output_tokens']:.1f} output and "
            f"{per_candidate['total_thoughts_tokens']:.1f} thinking tokens "
            "each"
        ),
        "is_estimate": True,
        "counted_in_audits": False,
        "missing_candidates": missing,
        "usage_stats": {
            field: int(round(per_candidate[field] * missing))
            for field in USAGE_FIELDS
        },
    }


def index_metas(root: Path) -> list[dict[str, Any]]:
    """Index every metadata file under *root* by day, model and usage.

    Args:
        root: Tree to walk (normally ``outputs``).

    Returns:
        One row per metadata file, carrying its Pacific billing day, model,
        item count and recorded input tokens.
    """
    rows: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for pattern in ("run.meta.json", "*.meta.json", "run.meta.*.json"):
        for path in root.rglob(pattern):
            if path in seen or not path.is_file():
                continue
            seen.add(path)
            try:
                meta = json.loads(path.read_text())
            except (OSError, json.JSONDecodeError, UnicodeDecodeError):
                continue
            if not isinstance(meta, dict):
                continue
            start = (meta.get("timestamp") or {}).get("start")
            usage = meta.get("usage_stats") or {}
            rows.append({
                "path": str(path),
                "start_utc": start,
                "pacific_day": pacific_day(start),
                "model": (meta.get("configuration") or {}).get("model"),
                "items_processed": (
                    meta.get("execution_stats") or {}
                ).get("items_processed"),
                "input_tokens": usage.get("total_input_tokens") or 0,
            })
    return rows


def billing_plan(
    stage: str,
    surviving: dict[str, Any],
    index: list[dict[str, Any]],
    damaged: set[str],
    main_pass_window: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """What a daily billing export would have to separate for this stage.

    A project-filtered daily export bounds an unrecoverable stage only when
    every other run of the same model on the same billing day has its own
    tokens on record, so their audited cost can be subtracted from the day.

    Args:
        stage: The stage directory.
        surviving: The stage's surviving metadata.
        index: The tree-wide metadata index from :func:`index_metas`.
        damaged: Stage directories known to carry the overwrite signature.
        main_pass_window: The main pass's own ``timestamp`` block where
            history records one — the anchor to prefer, because the surviving
            metadata dates the LATER pass. A Batch API main pass leaves an
            all-zero meta that still carries its window, which is how the Pro
            verifier stages' March date is known at all.

    Returns:
        The candidate day, the same-model inventory on it, and a verdict of
        ``sole-run``, ``boundable-by-subtraction`` or ``not-boundable``.
    """
    model = (surviving.get("configuration") or {}).get("model")
    main_day = pacific_day((main_pass_window or {}).get("start"))
    day = main_day or pacific_day(
        (surviving.get("timestamp") or {}).get("start"),
    )
    same_day = [
        row for row in index
        if row["pacific_day"] == day and row["model"] == model
        and str(Path(row["path"]).parent) != stage
    ]
    unrecorded = [row for row in same_day if not row["input_tokens"]]
    if not same_day:
        verdict = "sole-run"
    elif unrecorded or any(
        str(Path(row["path"]).parent) in damaged for row in same_day
    ):
        verdict = "not-boundable"
    else:
        verdict = "boundable-by-subtraction"
    return {
        "model": model,
        "export_pacific_day": day,
        "day_anchor": (
            "the main pass's own recorded window" if main_day
            else "the surviving (later) pass's window — the main pass may have "
                 "started on the previous Pacific day, so export both"
        ),
        "surviving_pass_pacific_day": pacific_day(
            (surviving.get("timestamp") or {}).get("start"),
        ),
        "main_pass_pacific_day": main_day,
        "same_model_same_day_runs": len(same_day),
        "same_model_same_day_without_recorded_tokens": len(unrecorded),
        "verdict": verdict,
        "inventory": sorted(
            (
                {
                    "path": row["path"],
                    "start_utc": row["start_utc"],
                    "items_processed": row["items_processed"],
                    "input_tokens": row["input_tokens"],
                    "tokens_recorded": bool(row["input_tokens"]),
                }
                for row in same_day
            ),
            key=lambda row: row["start_utc"] or "",
        ),
    }


def build_register(
    repo: Path,
    sweep_rows: list[dict[str, Any]],
    stages: list[str],
    index: list[dict[str, Any]],
) -> dict[str, Any]:
    """Assemble the recovery register.

    Args:
        repo: Repository holding the history.
        sweep_rows: ``audit_verifier_cost.py --sweep --json`` output.
        stages: Stage directories to recover.
        index: Tree-wide metadata index, for the billing plan. May be empty.

    Returns:
        The register, ready to serialise.
    """
    sweep = {row["stage"]: row for row in sweep_rows}
    damaged = {row["stage"] for row in sweep_rows}
    history = stage_history(repo, stages)
    register: dict[str, Any] = {
        "schema": REGISTER_SCHEMA,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": f"scripts/recover_verifier_meta_from_git.py {__version__}",
        "report": "reports/verifier-meta-recovery-2026-09-14.md",
        "contract": (
            "recovered_passes carry a git blob's usage_stats VERBATIM and are "
            "counted by scripts/audit_verifier_cost.py as a third source of "
            "passes, after the fixed merged schema and the legacy backup "
            "convention. items_processed is reconstructed from the blob's own "
            "counters (items_processed_source names which). residual_estimate "
            "is an estimate, never an audit, and is never counted. No "
            "committed run.meta.json was rewritten."
        ),
        "stages": {},
    }
    for stage in stages:
        row = sweep[stage]
        rows = history.get(stage, [])
        stage_dir = Path(stage)
        meta_rows = [
            entry for entry in rows
            if any(
                fragment in Path(entry["path"]).name
                for fragment in META_NAME_FRAGMENTS
            )
        ]
        blobs: list[dict[str, Any]] = []
        seen_blobs: set[str] = set()
        for entry in meta_rows:
            if entry["status"] == "D":
                continue
            blob = blob_at(repo, entry["commit"], entry["path"])
            if blob is None or blob in seen_blobs:
                continue
            seen_blobs.add(blob)
            meta = read_blob(repo, blob)
            covered, basis = coverage_of(meta)
            blobs.append({
                "blob": blob,
                "path": entry["path"],
                "commit": entry["commit"],
                "commit_date": entry["date"],
                "commit_subject": entry["subject"],
                "meta": meta,
                "items_covered": covered,
                "items_processed_source": basis,
                "usage": usage_of(meta),
            })
        blobs.sort(key=lambda blob: blob["commit_date"])
        surviving_meta = json.loads(
            (stage_dir / "run.meta.json").read_text(),
        ) if (stage_dir / "run.meta.json").exists() else (
            blobs[-1]["meta"] if blobs else {}
        )

        sources: list[dict[str, Any]] = []
        recovered: list[dict[str, Any]] = []
        notes: list[str] = []
        for blob in blobs[:-1]:
            sources.append({
                "kind": "git-blob",
                "path": blob["path"],
                "blob": blob["blob"],
                "commit": blob["commit"],
                "commit_date": blob["commit_date"],
                "commit_subject": blob["commit_subject"],
                "items_covered": blob["items_covered"],
                "items_processed_source": blob["items_processed_source"],
                "input_tokens": blob["usage"]["total_input_tokens"],
            })
            if not blob["usage"]["total_input_tokens"]:
                notes.append(
                    f"blob {blob['blob'][:10]} "
                    f"({blob['commit_date'][:10]}) records ZERO tokens: the "
                    "pass it describes ran through the Batch API, which "
                    "returns no per-response usage, so the main pass's token "
                    "load was never in any metadata and the overwrite "
                    "destroyed nothing",
                )
                continue
            configuration = blob["meta"].get("configuration") or {}
            recovered.append({
                "source": f"git-blob:{blob['blob']}",
                "kind": "main",
                "path": blob["path"],
                "commit": blob["commit"],
                "commit_date": blob["commit_date"],
                "run_id": blob["meta"].get("run_id"),
                "timestamp": blob["meta"].get("timestamp"),
                "items_processed_source": blob["items_processed_source"],
                "configuration": {
                    key: configuration.get(key) for key in (
                        "model", "temperature", "thinking_level",
                        "system_instruction_hash",
                    )
                },
                "execution_stats": {"items_processed": blob["items_covered"]},
                "usage_stats": blob["usage"],
                "cost_estimate_recorded_at_run_time": blob["meta"].get(
                    "cost_estimate",
                ),
            })

        items_recovered = sum(
            entry["execution_stats"]["items_processed"] for entry in recovered
        )
        still_missing = max(
            0, row["results"] - row["items_processed"] - items_recovered,
        )
        if not recovered:
            verdict = "NOT-IN-HISTORY"
            reason = (
                "batch-main-pass-recorded-no-tokens"
                if any(not src["input_tokens"] for src in sources)
                else "no-pre-overwrite-blob-in-history"
            )
        elif still_missing:
            verdict = "PARTIALLY-RECOVERED"
            reason = (
                f"recovered passes cover {items_recovered} of the "
                f"{row['shortfall']} missing candidates"
            )
        else:
            verdict = "RECOVERED-FROM-GIT"
            reason = "a pre-overwrite blob accounts for every result"

        entry_out: dict[str, Any] = {
            "verdict": verdict,
            "reason": reason,
            "results": row["results"],
            "surviving_meta_items_processed": row["items_processed"],
            "shortfall": row["shortfall"],
            "main_pass_covered_per_cleanup_history": row["main_pass_covered"],
            "items_recovered": items_recovered,
            "items_still_unaccounted": still_missing,
            "historical_blob_count": len(blobs),
            "first_commit": (
                {
                    key: rows[-1][key]
                    for key in ("commit", "date", "subject")
                } if rows else None
            ),
            "first_commit_files": (
                [
                    line.strip() for line in git(
                        repo, "ls-tree", "-r", "--name-only",
                        f"{rows[-1]['commit']}:{stage}",
                    ).splitlines() if line.strip()
                ] if rows else []
            ),
            "deleted_files_in_history": [
                {
                    key: entry[key]
                    for key in ("commit", "date", "subject", "path")
                }
                for entry in rows if entry["status"] == "D"
            ],
            "sources": sources,
            "recovered_passes": recovered,
            "notes": notes,
        }
        if recovered:
            main = recovered[0]
            main_items = main["execution_stats"]["items_processed"]
            surviving_usage = usage_of(surviving_meta)
            surviving_items = row["items_processed"]
            entry_out["cross_check"] = {
                "what": (
                    "input tokens per candidate, recovered main pass against "
                    "the surviving pass: equality is strong evidence that the "
                    "blob is this stage's own earlier self"
                ),
                "main_pass_input_per_candidate": round(
                    main["usage_stats"]["total_input_tokens"] / main_items, 1,
                ) if main_items else None,
                "surviving_pass_input_per_candidate": round(
                    surviving_usage["total_input_tokens"] / surviving_items, 1,
                ) if surviving_items else None,
            }
        else:
            estimate = residual_estimate(surviving_meta, still_missing)
            if estimate is not None:
                entry_out["residual_estimate"] = estimate
            # Where history holds any earlier blob — including the all-zero
            # meta a Batch API main pass writes — its window dates the main
            # pass, which no file in the working tree does.
            main_window = blobs[0]["meta"].get("timestamp") if len(blobs) > 1 \
                else None
            entry_out["main_pass_window_from_history"] = main_window
            if index:
                entry_out["billing_export"] = billing_plan(
                    stage, surviving_meta, index, damaged,
                    main_pass_window=main_window,
                )
        register["stages"][stage] = entry_out

    counts: dict[str, int] = defaultdict(int)
    for entry in register["stages"].values():
        counts[entry["verdict"]] += 1
    register["verdict_counts"] = dict(sorted(counts.items()))
    return register


def main(argv: list[str] | None = None) -> int:
    """Entry point.

    Args:
        argv: Argument vector, for testing.

    Returns:
        0 on success, 2 on a usage error.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Recover pre-overwrite verifier metadata from git history and "
            "write the recovery register."
        ),
    )
    parser.add_argument(
        "--sweep", type=Path, required=True,
        help="JSON from 'audit_verifier_cost.py --sweep outputs --json'",
    )
    parser.add_argument(
        "--repo", type=Path, default=Path("."),
        help="Repository or worktree holding the history (default: .)",
    )
    parser.add_argument(
        "--stages-file", type=Path, default=None,
        help=(
            "One stage path per line; default is every UNRECOVERABLE stage "
            "in the sweep"
        ),
    )
    parser.add_argument(
        "--index-root", type=Path, default=Path("outputs"),
        help=(
            "Tree to index for the billing-export plan; pass a missing path "
            "to skip the plan"
        ),
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    sweep_rows = json.loads(args.sweep.read_text())
    if args.stages_file is not None:
        stages = [
            line.strip() for line in args.stages_file.read_text().splitlines()
            if line.strip()
        ]
    else:
        stages = [
            row["stage"] for row in sweep_rows
            if row["classification"] == "UNRECOVERABLE"
        ]
    known = {row["stage"] for row in sweep_rows}
    unknown = [stage for stage in stages if stage not in known]
    if unknown:
        print(
            f"error: stages absent from the sweep: {unknown}", file=sys.stderr,
        )
        return 2

    index = index_metas(args.index_root) if args.index_root.is_dir() else []
    register = build_register(args.repo, sweep_rows, stages, index)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(register, indent=2) + "\n")
    print(f"wrote {args.out}: {register['verdict_counts']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
