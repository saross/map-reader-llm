"""
Backup-merge tests for ``aggregate_cost_manifest`` in
``scripts/run_generalisation.py``.

Regression guard for the cleanup-overwrites-meta pattern surfaced during
the T=0.7 generalisation recovery (Session 82). When ``run_pv.py
cleanup`` re-runs the verifier on a small set of missed candidates, it
overwrites ``verified/run.meta.json`` with only the cleanup batch's
(small) cost. The original verifier meta — recording the real ~$13
spend — is preserved (per Session 80 convention) as
``run.meta.json.pre-recovery-<TIMESTAMP>.backup``. The aggregator must
sum both into the cost manifest so the audit trail is correct.

Tests cover:

1. Verifier directory with ``run.meta.json`` plus one
   ``.pre-recovery-*.backup`` — aggregator sums both and records the
   backup path under ``_metadata.cleanup_recovery_metas_merged``.
2. Verifier directory with ``run.meta.json`` only (no backup) —
   aggregator behaves as before (no merge, no provenance entry).
3. Proposer per-pass directory with ``*.meta.json`` plus a
   ``.pre-recovery-*.backup`` — same merge logic applies.
4. Verifier directory with both ``.pre-recovery-*`` and
   ``.pre-cleanup-*`` backups — both glob patterns are matched and
   summed.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

# Make ``scripts.run_generalisation`` importable without installing
# the package — same pattern as ``test_aggregate_cost_idempotency``.
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_generalisation import (  # noqa: E402
    build_arg_parser,
    cmd_aggregate_cost,
)


# =============================================================================
# Helpers
# =============================================================================


def _make_meta(
    *,
    total_cost_usd: float,
    input_tokens: int = 0,
    output_tokens: int = 0,
    duration_seconds: float = 0.0,
    items_processed: int = 0,
    items_failed: int = 0,
    completed_items: list[str] | None = None,
) -> dict[str, Any]:
    """Build a minimal ``run.meta.json``-compatible dict for testing.

    Only the fields read by ``aggregate_cost_manifest`` are populated.
    ``completed_items`` defaults to a generated list of ``items_processed``
    synthetic tile names (``map-A_x0_y{n}``) so per-map attribution
    receives a sensible value.
    """
    if completed_items is None:
        completed_items = [
            f"map-A_x0_y{i}.png" for i in range(items_processed)
        ]
    return {
        "run_id": "test-run-id",
        "timestamp": {
            "start": "2026-01-01T00:00:00Z",
            "end": "2026-01-01T00:00:00Z",
            "duration_seconds": duration_seconds,
        },
        "execution_stats": {
            "items_processed": items_processed,
            "items_failed": items_failed,
            "completed_items": completed_items,
            "failed_items": [],
        },
        "usage_stats": {
            "total_input_tokens": input_tokens,
            "total_output_tokens": output_tokens,
            "total_cached_tokens": 0,
            "total_thoughts_tokens": 0,
            "total_tokens": input_tokens + output_tokens,
        },
        "cost_estimate": {
            "input_cost_usd": round(total_cost_usd * 0.6, 6),
            "output_cost_usd": round(total_cost_usd * 0.4, 6),
            "total_cost_usd": total_cost_usd,
            "pricing_used": {
                "model": "gemini-3-flash-preview",
                "input_per_1m": 0.5,
                "output_per_1m": 3.0,
            },
        },
    }


def _write_minimal_run_config(
    run_dir: Path,
    *,
    run_name: str,
    output_root: Path,
) -> Path:
    """Write a minimal YAML run-config to disk and return its path.

    Matches the helper in ``test_aggregate_cost_idempotency`` so the
    two test files exercise the same CLI surface. The auxiliary files
    (manifest, ground truth, …) only need to exist for
    ``aggregate_cost_manifest`` to read them — they may be empty.
    """
    proposer_config = run_dir / "proposer_config.json"
    proposer_config.write_text(
        json.dumps({
            "include_example_images": False,
            "instruction_file": "detect_brief-text.md",
        }),
        encoding="utf-8",
    )
    verifier_config = run_dir / "verifier_config.json"
    verifier_config.write_text(json.dumps({}), encoding="utf-8")

    manifest = run_dir / "manifest.json"
    manifest.write_text(json.dumps([]), encoding="utf-8")

    tiles_dir = run_dir / "tiles"
    tiles_dir.mkdir(exist_ok=True)
    rasters_dir = run_dir / "rasters"
    rasters_dir.mkdir(exist_ok=True)

    ground_truth = run_dir / "gt.geojson"
    ground_truth.write_text(
        json.dumps({"type": "FeatureCollection", "features": []}),
        encoding="utf-8",
    )
    bounds = run_dir / "bounds.geojson"
    bounds.write_text(
        json.dumps({"type": "FeatureCollection", "features": []}),
        encoding="utf-8",
    )

    config = {
        "run_name": run_name,
        "output_root": str(output_root),
        "proposer": {
            "config": str(proposer_config),
            "manifest": str(manifest),
            "tiles_dir": str(tiles_dir),
            "temperature": 0.3,
            "thinking_level": "high",
            "passes": 5,
        },
        "consensus": {"vote_threshold": 3},
        "extract": {"padding": 50, "rasters_dir": str(rasters_dir)},
        "verify": {"config": str(verifier_config)},
        "evaluate": {
            "prob_threshold": 0.5,
            "buffers": [20, 30, 40, 50],
            "ground_truth": str(ground_truth),
            "bounds": str(bounds),
        },
    }
    config_path = run_dir / "run_config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    return config_path


def _seed_run_outputs(
    output_dir: Path,
    *,
    proposer_config_stem: str = "proposer_config",
    proposer_meta: dict[str, Any] | None = None,
    proposer_backup: dict[str, Any] | None = None,
    verifier_meta: dict[str, Any] | None = None,
    verifier_backups: list[tuple[str, dict[str, Any]]] | None = None,
) -> dict[str, Path]:
    """Pre-populate ``output_dir`` with proposer + verifier meta files.

    Args:
        output_dir: Run output directory (created if absent).
        proposer_config_stem: Stem of the proposer config so the
            per-pass dir matches what ``aggregate_cost_manifest`` looks
            up via ``proposer_output = output_dir/proposer/<stem>``.
        proposer_meta: Primary ``*.meta.json`` for the single proposer
            pass. ``None`` skips the proposer entirely.
        proposer_backup: Optional ``.pre-recovery-*.backup`` sibling for
            the proposer meta. ``None`` skips the backup.
        verifier_meta: Primary ``run.meta.json`` for the verifier.
            ``None`` skips it.
        verifier_backups: List of ``(suffix, content)`` pairs for
            verifier backup siblings. ``suffix`` is the backup-name
            tail (e.g., ``"pre-recovery-20260502T235106"``) — the
            ``.backup`` extension is appended automatically. ``None`` or
            empty list means no backups.

    Returns:
        Dict of paths actually written, keyed by role
        (``proposer_meta``, ``proposer_backup``, ``verifier_meta``,
        ``verifier_backup_<suffix>``). Useful for assertions.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}

    # --- Proposer -----------------------------------------------------
    if proposer_meta is not None:
        run_dir = output_dir / "proposer" / proposer_config_stem / "run_1"
        run_dir.mkdir(parents=True, exist_ok=True)
        meta_path = run_dir / "detections.meta.json"
        meta_path.write_text(json.dumps(proposer_meta), encoding="utf-8")
        written["proposer_meta"] = meta_path
        if proposer_backup is not None:
            backup_path = meta_path.with_name(
                f"{meta_path.name}.pre-recovery-20260502T235106.backup"
            )
            backup_path.write_text(json.dumps(proposer_backup), encoding="utf-8")
            written["proposer_backup"] = backup_path

    # --- Verifier -----------------------------------------------------
    if verifier_meta is not None:
        verified_dir = output_dir / "verified"
        verified_dir.mkdir(parents=True, exist_ok=True)
        meta_path = verified_dir / "run.meta.json"
        meta_path.write_text(json.dumps(verifier_meta), encoding="utf-8")
        written["verifier_meta"] = meta_path
        for suffix, content in (verifier_backups or []):
            backup_path = meta_path.with_name(f"{meta_path.name}.{suffix}.backup")
            backup_path.write_text(json.dumps(content), encoding="utf-8")
            written[f"verifier_backup_{suffix}"] = backup_path

    # --- Crops manifest (required by aggregate_cost_manifest) ---------
    crops_dir = output_dir / "crops"
    crops_dir.mkdir(parents=True, exist_ok=True)
    (crops_dir / "candidate_manifest.json").write_text(
        json.dumps({"candidates": []}), encoding="utf-8",
    )

    return written


@pytest.fixture
def patched_run(tmp_path: Path, monkeypatch):
    """Build CLI args + isolated run dir for ``cmd_aggregate_cost`` tests.

    Returns a callable that seeds the run with given meta files and
    returns ``(args, output_dir, written_paths)``. Callers invoke it
    like ``run = patched_run(...)`` then call ``cmd_aggregate_cost`` on
    the args. The ``git_status`` patch keeps the dirty-tree guard from
    aborting the test.
    """
    output_root = tmp_path / "outputs"

    monkeypatch.setattr(
        "scripts.run_generalisation.git_status",
        lambda: {
            "commit_sha": "test", "branch": "main",
            "dirty": False, "untracked_file_count": 0,
        },
    )

    def _build(
        *,
        run_name: str = "test-run",
        proposer_meta: dict[str, Any] | None = None,
        proposer_backup: dict[str, Any] | None = None,
        verifier_meta: dict[str, Any] | None = None,
        verifier_backups: list[tuple[str, dict[str, Any]]] | None = None,
    ):
        config_path = _write_minimal_run_config(
            tmp_path, run_name=run_name, output_root=output_root,
        )
        output_dir = output_root / run_name
        written = _seed_run_outputs(
            output_dir,
            proposer_meta=proposer_meta,
            proposer_backup=proposer_backup,
            verifier_meta=verifier_meta,
            verifier_backups=verifier_backups,
        )
        parser = build_arg_parser()
        args = parser.parse_args([
            "aggregate-cost",
            "--run-config", str(config_path),
            "--yes",
        ])
        return args, output_dir, written

    return _build


# =============================================================================
# Tests
# =============================================================================


@pytest.mark.tier1
def test_verifier_with_backup_sums_costs(patched_run) -> None:
    """``aggregate-cost`` sums verifier ``run.meta.json`` and one
    ``.pre-recovery-*.backup`` sibling — the headline T=0.7 case.

    Mirrors the cleanup-overwrite scenario: the cleanup batch wrote a
    small ($0.10) primary meta over the original ($12.74) meta; the
    backup preserves the original. The aggregator should report the
    sum ($12.84) and list the backup under provenance.
    """
    args, output_dir, written = patched_run(
        verifier_meta=_make_meta(
            total_cost_usd=0.10168,
            input_tokens=132608,
            output_tokens=11792,
            duration_seconds=14.640159,
            items_processed=74,
        ),
        verifier_backups=[(
            "pre-recovery-20260502T235106",
            _make_meta(
                total_cost_usd=12.738616,
                input_tokens=16362752,
                output_tokens=1519080,
                duration_seconds=1382.878424,
                items_processed=9131,
            ),
        )],
    )

    rc = cmd_aggregate_cost(args)
    assert rc == 0, f"cmd_aggregate_cost returned {rc}, expected 0."

    cost_manifest = output_dir / "cost_manifest.json"
    data = json.loads(cost_manifest.read_text(encoding="utf-8"))

    # Sum should equal primary + backup, allowing for rounding.
    expected_sum = round(0.10168 + 12.738616, 4)
    assert data["by_stage"]["verifier"]["cost_usd"] == expected_sum, (
        f"Expected verifier cost {expected_sum}, "
        f"got {data['by_stage']['verifier']['cost_usd']}."
    )

    # Token counts should also be summed.
    v_tokens = data["by_stage"]["verifier"]["tokens"]
    assert v_tokens["input_tokens"] == 132608 + 16362752
    assert v_tokens["output_tokens"] == 11792 + 1519080

    # Wall-clock duration should be summed.
    assert data["by_stage"]["verifier"]["wall_clock_seconds"] == round(
        14.640159 + 1382.878424, 3,
    )

    # Provenance: the merged backup must be listed.
    merged = data["_metadata"]["cleanup_recovery_metas_merged"]
    assert len(merged) == 1, (
        f"Expected exactly one merged backup, got {merged}."
    )
    assert "pre-recovery-20260502T235106.backup" in merged[0], (
        f"Backup name not recorded in provenance: {merged}."
    )
    # Path should be relative to the run output dir.
    assert "verified/run.meta.json.pre-recovery" in merged[0]


@pytest.mark.tier1
def test_verifier_without_backup_unchanged_behaviour(patched_run) -> None:
    """``aggregate-cost`` with no backup produces the unchanged result.

    The empty ``cleanup_recovery_metas_merged`` list is the explicit
    signal that no backup was found — this is the expected state for a
    fresh run that never needed recovery.
    """
    args, output_dir, _ = patched_run(
        verifier_meta=_make_meta(
            total_cost_usd=12.5,
            input_tokens=10_000,
            output_tokens=2_000,
            duration_seconds=600.0,
            items_processed=100,
        ),
    )

    rc = cmd_aggregate_cost(args)
    assert rc == 0

    data = json.loads((output_dir / "cost_manifest.json").read_text())
    # No backup → cost reflects only the primary meta.
    assert data["by_stage"]["verifier"]["cost_usd"] == 12.5
    # Provenance must be empty (sentinel for "no merge happened").
    assert data["_metadata"]["cleanup_recovery_metas_merged"] == []


@pytest.mark.tier1
def test_proposer_with_backup_sums_costs(patched_run) -> None:
    """The same merge logic applies to proposer per-pass meta files.

    Future-proofs the (currently-hypothetical) case where a proposer
    recovery script writes a ``.pre-recovery-*.backup`` of an
    individual ``*.meta.json`` instead of merging in-place.
    """
    args, output_dir, _ = patched_run(
        proposer_meta=_make_meta(
            total_cost_usd=1.0,
            input_tokens=1_000,
            output_tokens=200,
            duration_seconds=10.0,
            items_processed=10,
        ),
        proposer_backup=_make_meta(
            total_cost_usd=20.0,
            input_tokens=20_000,
            output_tokens=4_000,
            duration_seconds=200.0,
            items_processed=200,
        ),
        verifier_meta=_make_meta(
            total_cost_usd=0.0, items_processed=0,
        ),
    )

    rc = cmd_aggregate_cost(args)
    assert rc == 0

    data = json.loads((output_dir / "cost_manifest.json").read_text())
    proposer = data["by_stage"]["proposer"]
    assert proposer["cost_usd"] == 21.0, (
        f"Expected proposer cost 21.0 (1.0 + 20.0), got {proposer['cost_usd']}."
    )
    # tiles_processed sums across primary + backup (210)
    assert proposer["tiles_processed"] == 210

    merged = data["_metadata"]["cleanup_recovery_metas_merged"]
    # One proposer backup recorded; verifier had no backup.
    assert len(merged) == 1
    assert "proposer/" in merged[0]
    assert merged[0].endswith(".backup")


@pytest.mark.tier1
def test_verifier_with_two_backup_patterns(patched_run) -> None:
    """Both ``.pre-recovery-*`` and ``.pre-cleanup-*`` patterns merge.

    Defensive coverage of the second glob pattern. The cleanup script in
    ``run_pv.py`` already writes ``.pre-cleanup-*.backup`` for
    ``probabilities.json``; if a future patch extends that to back up
    ``run.meta.json`` the aggregator will pick it up automatically
    without any further code changes.
    """
    args, output_dir, _ = patched_run(
        verifier_meta=_make_meta(
            total_cost_usd=0.10, items_processed=10,
        ),
        verifier_backups=[
            (
                "pre-recovery-20260502T235106",
                _make_meta(total_cost_usd=12.0, items_processed=100),
            ),
            (
                "pre-cleanup-20260503T000000",
                _make_meta(total_cost_usd=2.0, items_processed=20),
            ),
        ],
    )

    rc = cmd_aggregate_cost(args)
    assert rc == 0

    data = json.loads((output_dir / "cost_manifest.json").read_text())
    # 0.10 + 12.0 + 2.0 = 14.10
    assert data["by_stage"]["verifier"]["cost_usd"] == 14.10
    # Both backups recorded in provenance.
    merged = data["_metadata"]["cleanup_recovery_metas_merged"]
    assert len(merged) == 2
    assert any("pre-recovery" in m for m in merged)
    assert any("pre-cleanup" in m for m in merged)
