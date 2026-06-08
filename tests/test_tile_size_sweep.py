"""
Tier-1 tests for ``scripts.tile_size_sweep`` — the Stage C tile-size
characterisation harness (256/384/512 px). All synthetic; no I/O.

Pinned behaviours:
  1. ``parse_modality_temp`` — text/image inference + temperature extraction.
  2. ``_direction`` — flat vs best-size annotation from per-size F1.
  3. ``best_consensus_per_size`` — best-F1 per size for a fixed
     (modality, thinking, temperature), holding architecture=consensus.
  4. ``best_per_size_architecture`` — the FLASH-only ceiling (Pro excluded into
     ``pro_note``), so per-size ceilings are model-matched, not Pro-vs-Flash.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.tile_size_sweep import (  # noqa: E402
    _direction,
    best_consensus_per_size,
    best_per_size_architecture,
    parse_modality_temp,
)


# --------------------------------------------------------------------------- #
# 1. parse_modality_temp
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
@pytest.mark.parametrize("label,pool,exp_mod,exp_temp", [
    ("text-t0.0", "brief-text", "text", "0.0"),
    ("image-t0.7-n5-4of5", "track1-image-t0.7", "image", "0.7"),
    ("flash-high-text-n5-text-t1.0-consensus-9of10", "", "text", "1.0"),
    ("canonical-last", "", "text", None),  # no temp encoded
])
def test_parse_modality_temp(label, pool, exp_mod, exp_temp) -> None:
    """Modality + temperature are parsed from the label/pool."""
    mod, temp = parse_modality_temp(label, pool)
    assert mod == exp_mod
    assert temp == exp_temp


# --------------------------------------------------------------------------- #
# 2. _direction
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_direction_bigger_wins() -> None:
    """A clear gain toward the larger tile names that size as best."""
    d = _direction({256: 0.342, 384: 0.520, 512: 0.606})
    assert "best=512px" in d


@pytest.mark.tier1
def test_direction_flip_to_384() -> None:
    """When 384 leads, the annotation names 384."""
    d = _direction({384: 0.814, 512: 0.773})
    assert "best=384px" in d


@pytest.mark.tier1
def test_direction_flat_within_threshold() -> None:
    """Sub-0.015 spread is reported flat, not as a winner."""
    d = _direction({384: 0.600, 512: 0.590})
    assert d.startswith("flat")


@pytest.mark.tier1
def test_direction_single_size() -> None:
    """One size only cannot have a direction."""
    assert _direction({384: 0.75}) == "single-size"


# --------------------------------------------------------------------------- #
# 3. best_consensus_per_size
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_best_consensus_per_size_picks_max_per_size() -> None:
    """For fixed (modality, thinking, temp), the max-F1 cell per size is kept."""
    cells = [
        {"architecture": "consensus", "modality": "text", "thinking": "high",
         "temperature": "0.7", "size": 512, "f1": 0.77, "ref": "a"},
        {"architecture": "consensus", "modality": "text", "thinking": "high",
         "temperature": "0.7", "size": 512, "f1": 0.74, "ref": "b"},  # lower, dropped
        {"architecture": "consensus", "modality": "text", "thinking": "high",
         "temperature": "0.7", "size": 384, "f1": 0.81, "ref": "c"},
        {"architecture": "consensus", "modality": "image", "thinking": "high",
         "temperature": "0.7", "size": 384, "f1": 0.90, "ref": "wrong-modality"},
    ]
    best = best_consensus_per_size(cells, "text", "high", "0.7")
    assert best[512]["ref"] == "a"
    assert best[384]["ref"] == "c"
    assert set(best) == {512, 384}


# --------------------------------------------------------------------------- #
# 4. best_per_size_architecture — Flash ceiling, Pro split out
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_best_per_size_architecture_excludes_pro_from_ceiling() -> None:
    """Pro cells go to pro_note; the flash ceiling stays model-matched."""
    cells = [
        {"architecture": "single-pass", "modality": "text", "model": "flash",
         "size": 512, "f1": 0.63, "label": "flash-512"},
        {"architecture": "single-pass", "modality": "text", "model": "pro",
         "size": 384, "f1": 0.79, "label": "pro-384"},
        {"architecture": "single-pass", "modality": "text", "model": "flash",
         "size": 384, "f1": 0.52, "label": "flash-384"},
    ]
    out = best_per_size_architecture(cells)
    # The 384 flash ceiling is the flash cell (0.52), NOT the better Pro (0.79).
    assert out["by_arch_modality"][384]["single-pass/text"]["label"] == "flash-384"
    assert out["by_arch_modality"][512]["single-pass/text"]["label"] == "flash-512"
    # Pro is recorded separately.
    assert out["pro_note"]["384/single-pass/text"]["label"] == "pro-384"
