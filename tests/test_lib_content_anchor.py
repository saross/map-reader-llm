"""
Tests for ``scripts/lib_content_anchor.py`` — the shared content-anchor helpers.

Covers the three guarantees the audit's fix 7 depends on
(``reports/name-keyed-cache-audit-2026-09-12.md`` § 5 fix 7, candidate row 26):

1. :func:`git_blob_hash` returns exactly what ``git hash-object`` prints, so a
   provenance record written by this helper is comparable with one written by
   ``scripts/materialise_opmax_cells.py``.
2. :func:`config_hash` is order-independent and ``Path``-tolerant.
3. A ``.done`` marker records the config hash of the work it marks, and the
   checker treats a legacy (empty, ``touch``-ed) marker as unknown provenance
   — never as a match.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_content_anchor import (  # noqa: E402
    MATCH,
    MISMATCH,
    MISSING,
    UNKNOWN_PROVENANCE,
    config_hash,
    config_hash_of_files,
    done_marker_matches,
    git_blob_hash,
    main,
    read_done_marker,
    write_done_marker,
)

pytestmark = pytest.mark.tier1


# ---------------------------------------------------------------------------
# git_blob_hash
# ---------------------------------------------------------------------------


def test_git_blob_hash_matches_git_hash_object(tmp_path: Path) -> None:
    """The pure-Python hash equals ``git hash-object`` byte for byte."""
    target = tmp_path / "sample.geojson"
    target.write_text('{"type": "FeatureCollection", "features": []}\n', encoding="utf-8")

    expected = subprocess.run(
        ["git", "hash-object", str(target)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    assert git_blob_hash(target) == expected


def test_git_blob_hash_changes_with_content(tmp_path: Path) -> None:
    """Same name, different bytes — a different anchor. This is the whole point."""
    target = tmp_path / "detections.geojson"
    target.write_text("one", encoding="utf-8")
    first = git_blob_hash(target)
    target.write_text("two", encoding="utf-8")
    assert git_blob_hash(target) != first


def test_git_blob_hash_missing_and_directory_are_none(tmp_path: Path) -> None:
    """Absent paths and directories yield ``None`` rather than raising."""
    assert git_blob_hash(tmp_path / "absent.json") is None
    assert git_blob_hash(tmp_path) is None


# ---------------------------------------------------------------------------
# config_hash
# ---------------------------------------------------------------------------


def test_config_hash_is_key_order_independent() -> None:
    """Dict ordering must not change a configuration's identity."""
    assert config_hash({"a": 1, "b": [2, 3]}) == config_hash({"b": [2, 3], "a": 1})


def test_config_hash_tolerates_paths_and_distinguishes_values() -> None:
    """``Path`` values hash as their string form; a changed value changes the hash."""
    as_path = config_hash({"config": Path("prompts/configs/x.json")})
    as_str = config_hash({"config": "prompts/configs/x.json"})
    assert as_path == as_str
    assert as_path != config_hash({"config": "prompts/configs/y.json"})


def test_config_hash_of_files_is_content_keyed(tmp_path: Path) -> None:
    """Two files' contents define the hash; editing either changes it."""
    a = tmp_path / "a.json"
    b = tmp_path / "b.md"
    a.write_text("{}", encoding="utf-8")
    b.write_text("instructions", encoding="utf-8")

    first = config_hash_of_files([a, b])
    assert config_hash_of_files([b, a]) == first, "order must not matter"

    b.write_text("instructions, revised", encoding="utf-8")
    assert config_hash_of_files([a, b]) != first


def test_config_hash_of_files_records_a_missing_file(tmp_path: Path) -> None:
    """A missing input changes the hash instead of being silently skipped."""
    a = tmp_path / "a.json"
    a.write_text("{}", encoding="utf-8")
    with_missing = config_hash_of_files([a, tmp_path / "absent.md"])
    assert with_missing != config_hash_of_files([a])


# ---------------------------------------------------------------------------
# .done markers
# ---------------------------------------------------------------------------


def test_done_marker_round_trips(tmp_path: Path) -> None:
    """A written marker records the hash and matches it back."""
    marker = tmp_path / "pass" / ".done"
    write_done_marker(marker, "abc123", extra={"pass": "run_07"})

    payload = read_done_marker(marker)
    assert payload is not None
    assert payload["config_hash"] == "abc123"
    assert payload["pass"] == "run_07"
    assert done_marker_matches(marker, "abc123") == (True, MATCH)


def test_done_marker_mismatch_is_not_a_match(tmp_path: Path) -> None:
    """A marker written under a different config must not license a skip."""
    marker = tmp_path / ".done"
    write_done_marker(marker, "abc123")
    assert done_marker_matches(marker, "def456") == (False, MISMATCH)


def test_missing_marker_reports_missing(tmp_path: Path) -> None:
    """An absent marker is ``missing``, not an error."""
    assert done_marker_matches(tmp_path / ".done", "abc123") == (False, MISSING)


def test_legacy_touched_marker_is_unknown_provenance(tmp_path: Path) -> None:
    """An empty ``touch``-ed marker is unknown provenance, never a match.

    Backwards compatibility with the existing shell drivers' markers
    (audit candidate row 26) must not degrade into treating "something
    ran" as "this config ran".
    """
    marker = tmp_path / ".done"
    marker.touch()
    assert done_marker_matches(marker, "abc123") == (False, UNKNOWN_PROVENANCE)
    assert read_done_marker(marker) is None


def test_non_json_marker_is_unknown_provenance(tmp_path: Path) -> None:
    """A marker holding arbitrary text is unknown provenance, not a crash."""
    marker = tmp_path / ".done"
    marker.write_text("completed 2026-03-01\n", encoding="utf-8")
    assert done_marker_matches(marker, "abc123") == (False, UNKNOWN_PROVENANCE)


# ---------------------------------------------------------------------------
# CLI (the surface a shell driver uses)
# ---------------------------------------------------------------------------


def test_cli_write_then_check_round_trip(tmp_path: Path, capsys) -> None:
    """``write-done`` then ``check-done`` exits 0; editing the config exits 1."""
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps({"temperature": 0.3}), encoding="utf-8")
    marker = tmp_path / ".done"

    assert main(["write-done", str(marker), "--config", str(cfg)]) == 0
    capsys.readouterr()
    assert main(["check-done", str(marker), "--config", str(cfg)]) == 0

    cfg.write_text(json.dumps({"temperature": 0.7}), encoding="utf-8")
    assert main(["check-done", str(marker), "--config", str(cfg)]) == 1
    assert MISMATCH in capsys.readouterr().out


def test_cli_check_done_on_legacy_marker_exits_nonzero(tmp_path: Path) -> None:
    """A legacy marker must not let a driver skip the work."""
    cfg = tmp_path / "config.json"
    cfg.write_text("{}", encoding="utf-8")
    marker = tmp_path / ".done"
    marker.touch()
    assert main(["check-done", str(marker), "--config", str(cfg)]) == 1


def test_cli_hash_config_prints_a_stable_digest(tmp_path: Path, capsys) -> None:
    """``hash-config`` prints the same digest the marker records."""
    cfg = tmp_path / "config.json"
    cfg.write_text("{}", encoding="utf-8")
    assert main(["hash-config", "--config", str(cfg)]) == 0
    printed = capsys.readouterr().out.strip()
    assert printed == config_hash_of_files([cfg])
