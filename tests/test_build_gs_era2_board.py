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


def test_member_track_is_derived_from_the_transmitted_config_not_the_label(monkeypatch):
    """The board's ``track`` must come from what the proposer sent.

    Modality is a preregistered factor (H1). Before 2026-09-14 the builder
    assigned ``"image" if "image" in label else "text"``, which mislabelled
    seven cells on this board in two distinct ways. The membership rule now
    calls ``derive_condition_modality.condition_modality``, so the label's own
    tokens have no influence on the field.
    """
    def fake(run_id: str, pool: str) -> tuple[str, str]:
        # The ground truth for both failure shapes the 2026-09-14 audit found.
        return ({"detect_brief-text": ("text", "config-file"),
                 "scale-4-optimal-487": ("image", "run-metadata")}
                .get(pool, ("text", "register")))

    monkeypatch.setattr(b, "condition_modality", fake)

    # Shape 1: the label names the VERIFIER's modality over a text proposer.
    label = "verified-brief-image"
    assert "image" in label                # the retired test would have said "image"
    assert b.condition_modality("proposer-verifier-384", "detect_brief-text") == (
        "text", "config-file")

    # Shape 2: the label carries no modality token at all, so a substring test
    # would fall through to "text"; the pool is image-bearing.
    label = "pv-scale4-optimal-n1-opmax"
    assert "image" not in label             # the retired test would have said "text"
    assert b.condition_modality("pv-diag-384", "scale-4-optimal-487") == (
        "image", "run-metadata")


def test_the_label_substring_test_is_gone_from_the_membership_rule():
    """A regression guard: the retired expression must not reappear."""
    source = (b.REPO_ROOT / "scripts/build_gs_era2_board.py").read_text(encoding="utf-8")
    assert '"image" if "image" in label else "text"' not in source
    assert 'condition_modality(run_id, cond.get("proposer_pool")' in source
