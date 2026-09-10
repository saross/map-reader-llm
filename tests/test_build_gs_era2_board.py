"""Tier-1 tests for ``scripts/build_gs_era2_board.py`` (the GS Era-2 verified board).

The membership rule's label parser and the derived-artefact helpers are pure
functions; these tests pin the K-from-label rules the rule depends on and the
gate arithmetic, without touching the register or the board directory.
"""

from __future__ import annotations

import pytest

from scripts import build_gs_era2_board as b

pytestmark = pytest.mark.tier1


@pytest.mark.parametrize(
    "label, n_passes, expected",
    [
        ("verified-adv-text-consensus-16of30", 1, 30),      # kofN wins over the register's n_passes
        ("verified-adv-text-4of5", 5, 5),
        ("f3prop-f35vf-6of10", 10, 10),
        ("g37-text-k5-verified-swap37-p0.80-k5", 5, 5),     # -kN-verified (3.7 screens)
        ("g384-ov192-k10-verified37-p0.98-k10", 10, 10),    # grid B cell
        ("verified-384-union-t0-0-n5", 5, 5),               # -nN (verifier-robustness)
        ("verified-384-16of30-t0-3-n5-opmax", 1, 30),       # kofN before -nN
        ("verified-t0-5", 5, 5),                            # no K in the label: n_passes
        ("verified-adv-image-baseline", 1, 1),
    ],
)
def test_pool_k_reads_the_proposer_pool_size(label, n_passes, expected):
    assert b.pool_k(label, n_passes) == expected


def test_slug_is_filesystem_safe_and_reversible_enough():
    assert b.slug("gemini37-screen-2026-08-28::g37-text-k5-verified-swap37-p0.80-k5") == (
        "gemini37-screen-2026-08-28__g37-text-k5-verified-swap37-p0_80-k5")


def test_f1_at_reads_either_buffer_key():
    doc = {"summary": {"buffers": [{"buffer_metres": 20, "f1": 0.91}, {"buffer_m": 30, "f1": 0.93}]}}
    assert b.f1_at(doc, 20) == 0.91 and b.f1_at(doc, 30) == 0.93 and b.f1_at(doc, 50) is None
    assert b.f1_at(None) is None


def test_membership_constants_name_the_signed_frame():
    assert b.FRAME.endswith("era2_b_intersection_bounds.geojson")
    assert b.FRAME_ID == "era2-b-487" and b.FRAME_TILES == 487
    assert b.SUFFIX == "-era2b"
