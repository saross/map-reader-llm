"""
Tests for ``scripts/check_manipulation.py`` (tracker W6.1).

The guard refuses an analysis whose arms differ in configuration but not in
the transmitted signature (a null manipulation). The synthetic tests write
pairs of minimal pass metas and judge them:

- two text-only arms listing different libraries → identical signatures →
  REFUSE (the Phase 2c text-track shape, erratum E90);
- the same pair with images on in one arm → signatures differ → PASS;
- a replicate of one configuration → PASS (identical configuration);
- one configuration on two different tile sets → PASS (different inputs);
- an arm with no readable metadata → UNVERIFIABLE, or out of scope with the
  opt-out.

One test runs the CLI on a registered analysis and pins the 2026-10-05
finding: the Era-1 single-pass matrix carries the Phase 2c text replicates.

Tier 2: the tests read and write meta files, and the last reads the
committed register and metas.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import check_manipulation as cm

pytestmark = pytest.mark.tier2

_LIBRARY_A = [{"path": f"neutral-naming/example_{i:02d}.png", "label": "Positive",
               "category": "canonical_positive"} for i in range(1, 10)]
_LIBRARY_B = _LIBRARY_A[:7]


def _meta(path: Path, version: str, examples: list[dict], include_images: bool,
          tiles: list[str] | None = None, temperature: float = 0.0) -> str:
    """Write a minimal proposer pass meta in the pipeline's shape.

    Args:
        path: Where to write it.
        version: The configuration version.
        examples: The listed example library.
        include_images: ``include_example_images``.
        tiles: The dispatched tile ids (completed items).
        temperature: The configured temperature.

    Returns:
        The path, as a string.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "environment": {"script": "4_detect_mounds_batch.py", "git_commit": "abc"},
        "configuration": {
            "version": version, "model": "gemini-3-flash-preview",
            "instruction_file": "detect_brief-text.md",
            "system_instruction_hash": "e169b7237b853eeaad990fc2e54f",
            "temperature": temperature, "thinking_level": "minimal",
            "max_output_tokens": 8192, "tile_size": None,
            "include_example_images": include_images,
            "full_config_snapshot": {"version": version, "examples": examples,
                                     "include_example_images": include_images},
        },
        "execution_stats": {"items_processed": len(tiles or ["t1.png"]),
                            "completed_items": tiles or ["t1.png", "t2.png"],
                            "failed_items": []},
        "usage_stats": {},
    }))
    return str(path)


def test_identical_requests_under_different_configurations_refuse(tmp_path) -> None:
    """Two text-only arms with different listed libraries sent the same
    request: the analysis compares replicates, and the guard refuses."""
    a = cm.arm_from_metas("A", [_meta(tmp_path / "a.meta.json", "library_a-text",
                                      _LIBRARY_A, include_images=False)])
    b = cm.arm_from_metas("B", [_meta(tmp_path / "b.meta.json", "library_b-text",
                                      _LIBRARY_B, include_images=False)])
    judgement = cm.judge([a, b])
    assert judgement["verdict"] == cm.REFUSE
    (pair,) = judgement["null_pairs"]
    assert pair["arms"] == ["A", "B"]
    assert pair["config_fields_differing"] == ["listed_library", "version"]


def test_a_recovery_fragment_does_not_hide_a_null_manipulation(tmp_path) -> None:
    """A recovery fragment re-sends a few of its pass's tiles; the arm's
    inputs are the union over its passes, so a fragment in one arm and not
    the other does not make two identical requests look different."""
    tiles = ["x0_y0.png", "x1_y0.png", "x2_y0.png"]
    a = cm.arm_from_metas("A", [
        _meta(tmp_path / "a" / "run_1.meta.json", "library_a-text", _LIBRARY_A, False,
              tiles=tiles[:2]),
        _meta(tmp_path / "a" / "run_1_recovery.meta.json", "library_a-text", _LIBRARY_A,
              False, tiles=tiles[2:])])
    b = cm.arm_from_metas("B", [_meta(tmp_path / "b.meta.json", "library_b-text",
                                      _LIBRARY_B, False, tiles=tiles)])
    assert cm.judge([a, b])["verdict"] == cm.REFUSE


def test_a_manipulation_that_reached_the_request_passes(tmp_path) -> None:
    """With images on, the library reaches the request: the signatures
    differ and the analysis passes."""
    a = cm.arm_from_metas("A", [_meta(tmp_path / "a.meta.json", "library_a",
                                      _LIBRARY_A, include_images=True)])
    b = cm.arm_from_metas("B", [_meta(tmp_path / "b.meta.json", "library_b",
                                      _LIBRARY_B, include_images=True)])
    assert a["signature"] != b["signature"]
    assert cm.judge([a, b])["verdict"] == cm.PASS


def test_a_replicate_of_one_configuration_passes(tmp_path) -> None:
    """Identical configuration and identical request: a replicate, not a
    null manipulation (e.g. two aggregations of one pool)."""
    a = cm.arm_from_metas("A", [_meta(tmp_path / "a.meta.json", "library_a-text",
                                      _LIBRARY_A, include_images=False)])
    b = cm.arm_from_metas("B", [_meta(tmp_path / "b.meta.json", "library_a-text",
                                      _LIBRARY_A, include_images=False)])
    assert cm.judge([a, b])["verdict"] == cm.PASS


def test_different_inputs_are_different_requests(tmp_path) -> None:
    """One configuration on two tile sets sent different tiles: not a null
    manipulation, even when the version names differ."""
    a = cm.arm_from_metas("A", [_meta(tmp_path / "a.meta.json", "v-384", _LIBRARY_A,
                                      False, tiles=["x0_y0.png", "x1_y0.png"])])
    b = cm.arm_from_metas("B", [_meta(tmp_path / "b.meta.json", "v-512", _LIBRARY_A,
                                      False, tiles=["x0_y0.png"])])
    assert cm.judge([a, b])["verdict"] == cm.PASS


def test_a_configured_temperature_that_was_sent_passes(tmp_path) -> None:
    """A temperature manipulation reaches the request (temperature_eff)."""
    a = cm.arm_from_metas("A", [_meta(tmp_path / "a.meta.json", "v", _LIBRARY_A,
                                      False, temperature=0.0)])
    b = cm.arm_from_metas("B", [_meta(tmp_path / "b.meta.json", "v", _LIBRARY_A,
                                      False, temperature=0.7)])
    assert cm.judge([a, b])["verdict"] == cm.PASS


def test_an_arm_without_metadata_is_unverifiable_not_passed(tmp_path) -> None:
    """No readable meta is a named absence: UNVERIFIABLE unless allowed."""
    a = cm.arm_from_metas("A", [_meta(tmp_path / "a.meta.json", "v", _LIBRARY_A, False)])
    b = cm.arm_from_metas("B", [str(tmp_path / "absent.meta.json")])
    judgement = cm.judge([a, b])
    assert judgement["verdict"] == cm.UNVERIFIABLE
    assert judgement["unverifiable"][0]["arm"] == "B"
    assert cm.judge([a, b], allow_unverifiable=True)["verdict"] == cm.PASS


def test_the_signature_carries_exactly_the_shared_fields(tmp_path) -> None:
    """The signature is the definition shared with map-reader-bench:
    its keys are SIGNATURE_FIELDS, no more and no fewer."""
    rec = cm.meta_record(_meta(tmp_path / "a.meta.json", "v", _LIBRARY_A, True))
    assert tuple(cm.signature(rec)) == cm.SIGNATURE_FIELDS
    assert tuple(cm.configuration_identity(rec)) == cm.CONFIG_FIELDS


def test_the_registered_era1_matrix_is_refused(capsys) -> None:
    """The 2026-10-05 finding, pinned: the Era-1 single-pass matrix compares
    the retest's Phase 2c text arms (five libraries, one request) and the
    Phase 2b image arm with its 2c scale-8 twin."""
    assert cm.main(["era1-single-pass-baseline-matrix"]) == 2
    out = capsys.readouterr().out
    assert out.startswith("REFUSE era1-single-pass-baseline-matrix")
    assert "retest-phase2c::text-canonical vs retest-phase2c::text-plus-hp" in out
    assert "retest-phase2b::image-t0.0 vs retest-phase2c::image-scale-8" in out
