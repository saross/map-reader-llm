"""Per-map failure attribution in ``scripts/run_generalisation.py``.

Phase 7 of the Session 137 audit remediation (defect D37, audit finding
F15c): ``aggregate_cost_manifest`` built its two failure totals from
different readings of the same field. The run-level ``tiles_failed``
sums ``execution_stats.items_failed`` (which counts every entry), while
the per-map attribution iterated ``execution_stats.failed_items`` and
kept only ``isinstance(entry, str)`` entries — silently dropping the
canonical dict shape ``{"item_id": ..., "reason": ..., "timestamp": ...}``
that ``4_detect_mounds_batch.py`` and ``run_pv.py`` actually write. The
committed 55-map cost manifest therefore published two failure counts
that disagreed by one tile.

Tests cover:

1. ``failed_item_name`` across every shape the corpus contains — dict
   with ``item_id``, the three tolerated aliases, a bare string, and the
   unattributable cases that must return ``None`` rather than a guess.
2. The real committed proposer meta still carries the dict shape this
   fix exists for (a key-drift tripwire, not a value assertion).
3. End-to-end: with dict-shaped ``failed_items`` the per-map
   ``tiles_failed`` column sums to the run-level ``tiles_failed``.

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

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_generalisation import (  # noqa: E402
    build_arg_parser,
    cmd_aggregate_cost,
    failed_item_name,
)

pytestmark = pytest.mark.tier1

#: A tracked proposer meta from the 55-map generalisation run whose
#: ``failed_items`` list holds the dict shape. Relative to the repo root.
REAL_META = Path(
    "outputs/55maps-generalisation/proposer/detect_brief-text/run_3/"
    "detections-detect_brief-text-3-flash-2026-04-10.meta.json"
)


# =============================================================================
# 1. failed_item_name — one reader for every shape in the corpus
# =============================================================================


def test_dict_entry_yields_its_item_id() -> None:
    """The canonical schema: the name lives under ``item_id``."""
    entry = {
        "item_id": "K-35-062-4_Asenovgrad_4326_x3696_y2352.png",
        "reason": "Retries Exhausted / Invalid Finish Reason",
        "timestamp": "2026-04-10T01:18:30.338679+00:00",
    }
    assert failed_item_name(entry) == (
        "K-35-062-4_Asenovgrad_4326_x3696_y2352.png"
    )


def test_bare_string_entry_is_returned_unchanged() -> None:
    """The legacy shape stores the tile name directly."""
    assert failed_item_name("K-35-042-3_x336_y672.png") == (
        "K-35-042-3_x336_y672.png"
    )


@pytest.mark.parametrize("key", ["item", "filename", "tile"])
def test_alias_keys_are_tolerated(key: str) -> None:
    """The aliases ``rederive_manifest_fields.py`` already accepts.

    Two readers of the same field disagreeing about what a failure entry
    looks like is how this defect class recurs; keep them aligned.
    """
    assert failed_item_name({key: "map-A_x0_y0.png"}) == "map-A_x0_y0.png"


@pytest.mark.parametrize(
    "entry",
    [
        {},                                   # no identifier at all
        {"reason": "timeout"},                # reason only
        {"item_id": ""},                      # empty identifier
        {"item_id": 42},                      # non-string identifier
        "",                                   # empty legacy string
        None,
        7,
    ],
)
def test_unattributable_entries_return_none(entry: Any) -> None:
    """No identifier means no attribution — never a fabricated map id."""
    assert failed_item_name(entry) is None


def test_item_id_wins_over_aliases() -> None:
    """``item_id`` is canonical; aliases are only a fallback."""
    entry = {"item_id": "canonical.png", "filename": "alias.png"}
    assert failed_item_name(entry) == "canonical.png"


# =============================================================================
# 2. The committed corpus still carries the shape this fix exists for
# =============================================================================


def test_real_committed_meta_uses_the_dict_shape() -> None:
    """Key-drift tripwire against the tracked 55-map proposer meta.

    If the writer ever renames ``item_id``, this fails here rather than
    silently reintroducing the split-total defect downstream.
    """
    meta_path = PROJECT_ROOT / REAL_META
    if not meta_path.is_file():  # pragma: no cover - artefact absent
        pytest.skip(f"{REAL_META} not present in this checkout")
    stats = json.loads(meta_path.read_text(encoding="utf-8"))[
        "execution_stats"
    ]
    entries = stats["failed_items"]
    assert entries, "expected at least one recorded failure"
    assert all(isinstance(e, dict) for e in entries)
    names = [failed_item_name(e) for e in entries]
    assert all(isinstance(n, str) and n.endswith(".png") for n in names)
    # The two totals are built from the same entries.
    assert len(names) == int(stats["items_failed"])


# =============================================================================
# 3. End-to-end: the two failure totals agree in the cost manifest
# =============================================================================


def _meta_with_failures(
    failed_items: list[Any],
    *,
    items_processed: int = 3,
) -> dict[str, Any]:
    """A minimal proposer ``*.meta.json`` carrying the given failures."""
    return {
        "run_id": "test-run-id",
        "timestamp": {
            "start": "2026-01-01T00:00:00Z",
            "end": "2026-01-01T00:00:00Z",
            "duration_seconds": 1.0,
        },
        "execution_stats": {
            "items_processed": items_processed,
            "items_failed": len(failed_items),
            "completed_items": [
                f"map-A_x0_y{i}.png" for i in range(items_processed)
            ],
            "failed_items": failed_items,
        },
        "usage_stats": {
            "total_input_tokens": 100,
            "total_output_tokens": 20,
            "total_cached_tokens": 0,
            "total_thoughts_tokens": 0,
            "total_tokens": 120,
        },
        "cost_estimate": {
            "input_cost_usd": 0.6,
            "output_cost_usd": 0.4,
            "total_cost_usd": 1.0,
            "pricing_used": {
                "model": "gemini-3-flash-preview",
                "input_per_1m": 0.5,
                "output_per_1m": 3.0,
            },
        },
    }


def _seed_run(tmp_path: Path, failed_items: list[Any]) -> tuple[Path, Path]:
    """Write a minimal run-config plus one proposer pass; return paths.

    Returns:
        ``(config_path, output_dir)``.
    """
    proposer_config = tmp_path / "proposer_config.json"
    proposer_config.write_text(
        json.dumps({
            "include_example_images": False,
            "instruction_file": "detect_brief-text.md",
        }),
        encoding="utf-8",
    )
    (tmp_path / "verifier_config.json").write_text("{}", encoding="utf-8")
    (tmp_path / "manifest.json").write_text("[]", encoding="utf-8")
    (tmp_path / "tiles").mkdir(exist_ok=True)
    (tmp_path / "rasters").mkdir(exist_ok=True)
    empty_fc = json.dumps({"type": "FeatureCollection", "features": []})
    (tmp_path / "gt.geojson").write_text(empty_fc, encoding="utf-8")
    (tmp_path / "bounds.geojson").write_text(empty_fc, encoding="utf-8")

    output_root = tmp_path / "outputs"
    config = {
        "run_name": "failure-attribution",
        "output_root": str(output_root),
        "proposer": {
            "config": str(proposer_config),
            "manifest": str(tmp_path / "manifest.json"),
            "tiles_dir": str(tmp_path / "tiles"),
            "temperature": 0.0,
            "thinking_level": "minimal",
            "passes": 1,
        },
        "consensus": {"vote_threshold": 1},
        "extract": {"padding": 50, "rasters_dir": str(tmp_path / "rasters")},
        "verify": {"config": str(tmp_path / "verifier_config.json")},
        "evaluate": {
            "prob_threshold": 0.5,
            "buffers": [20],
            "ground_truth": str(tmp_path / "gt.geojson"),
            "bounds": str(tmp_path / "bounds.geojson"),
        },
    }
    config_path = tmp_path / "run_config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    output_dir = output_root / "failure-attribution"
    run_dir = output_dir / "proposer" / "proposer_config" / "run_1"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "detections.meta.json").write_text(
        json.dumps(_meta_with_failures(failed_items)), encoding="utf-8",
    )
    crops_dir = output_dir / "crops"
    crops_dir.mkdir(parents=True, exist_ok=True)
    (crops_dir / "candidate_manifest.json").write_text(
        json.dumps({"candidates": []}), encoding="utf-8",
    )
    return config_path, output_dir


def _aggregate(tmp_path: Path, monkeypatch, failed_items: list[Any]) -> dict:
    """Run ``aggregate-cost`` over a seeded run and return the manifest."""
    monkeypatch.setattr(
        "scripts.run_generalisation.git_status",
        lambda: {
            "commit_sha": "test", "branch": "main",
            "dirty": False, "untracked_file_count": 0,
        },
    )
    config_path, output_dir = _seed_run(tmp_path, failed_items)
    args = build_arg_parser().parse_args([
        "aggregate-cost", "--run-config", str(config_path), "--yes",
    ])
    assert cmd_aggregate_cost(args) == 0
    return json.loads(
        (output_dir / "cost_manifest.json").read_text(encoding="utf-8")
    )


def test_dict_failures_reach_the_per_map_totals(tmp_path, monkeypatch) -> None:
    """The regression: dict entries must be attributed, not dropped.

    Before the D37 fix the per-map column summed to 0 while the stage
    total said 2 — the shape of the one-tile disagreement in the
    committed 55-map report.
    """
    data = _aggregate(tmp_path, monkeypatch, [
        {"item_id": "map-A_x9_y9.png", "reason": "Retries Exhausted"},
        {"item_id": "map-B_x1_y1.png", "reason": "Safety Block"},
    ])
    stage_total = data["by_stage"]["proposer"]["tiles_failed"]
    per_map_total = sum(r["tiles_failed"] for r in data["per_map"])
    assert stage_total == 2
    assert per_map_total == stage_total, (
        "per-map failure attribution disagrees with the stage total "
        f"({per_map_total} != {stage_total})"
    )
    by_map = {r["map_id"]: r["tiles_failed"] for r in data["per_map"]}
    assert by_map["map-A"] == 1
    assert by_map["map-B"] == 1
    assert data["_metadata"]["unattributed_failed_items"] == []


def test_mixed_and_string_failures_both_attribute(
    tmp_path, monkeypatch,
) -> None:
    """A pool straddling both writers still reconciles."""
    data = _aggregate(tmp_path, monkeypatch, [
        {"item_id": "map-B_x1_y1.png", "reason": "Safety Block"},
        "map-C_x2_y2.png",
    ])
    per_map_total = sum(r["tiles_failed"] for r in data["per_map"])
    assert per_map_total == data["by_stage"]["proposer"]["tiles_failed"] == 2
    by_map = {r["map_id"]: r["tiles_failed"] for r in data["per_map"]}
    assert by_map["map-B"] == 1 and by_map["map-C"] == 1


def test_unattributable_failure_is_warned_not_guessed(
    tmp_path, monkeypatch,
) -> None:
    """An entry with no identifier is surfaced, never silently binned."""
    data = _aggregate(tmp_path, monkeypatch, [{"reason": "unknown"}])
    assert sum(r["tiles_failed"] for r in data["per_map"]) == 0
    gaps = data["_metadata"]["unattributed_failed_items"]
    assert any("no item identifier" in w for w in gaps), gaps
