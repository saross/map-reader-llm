"""
Tests for ``scripts/lib_config_validation.py`` and its two entry points.

An inert configuration field is an error, not a no-op (tracker W6.2). The
first rule is the text-track transmission gap (erratum E90): an ``examples``
list under ``include_example_images: false`` transmits nothing from the
library, neither images nor labels. These tests pin the rule, the
historical-reproduction opt-out (``--allow-inert-fields``), its wiring into
``4_detect_mounds_batch.py`` (real-time and batch paths) and ``run_phase2.py``
(launch check and the flag passed through to the detector), and the set of
committed configurations the rule now refuses.

All tier 1: synthetic configurations, no API client is ever created (the
detector's client constructor is replaced by a sentinel that stops the run).
"""

from __future__ import annotations

import argparse
import glob
import importlib.util
import json
import logging
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from scripts.lib_config_validation import (  # noqa: E402
    OPT_OUT_FLAG,
    InertConfigurationError,
    find_inert_fields,
    validate_no_inert_fields,
)

pytestmark = pytest.mark.tier1

_EXAMPLES = [{"path": "neutral-naming/example_01.png", "label": "Positive",
              "category": "canonical_positive"},
             {"path": "neutral-naming/example_09.png", "label": "Negative",
              "category": "canonical_negative"}]


def _text_config() -> dict:
    """A text-only configuration that still lists an example library."""
    return {"version": "t-text", "model": "gemini-3-flash",
            "instruction_file": "detect_brief-text.md",
            "include_example_images": False, "examples": list(_EXAMPLES)}


def _image_config() -> dict:
    """An image configuration: the example list is transmitted."""
    return {**_text_config(), "version": "t-image", "include_example_images": True}


# ── the rule ─────────────────────────────────────────────────────────────

def test_a_text_only_config_with_examples_fails() -> None:
    """The E90 case raises, naming the field, the silencing setting and the
    opt-out."""
    with pytest.raises(InertConfigurationError) as info:
        validate_no_inert_fields(_text_config(), source="prompts/configs/t.json")
    message = str(info.value)
    assert "examples is inert under include_example_images: false" in message
    assert "2 example(s)" in message
    assert "prompts/configs/t.json" in message
    assert OPT_OUT_FLAG in message
    assert [f.field for f in info.value.findings] == ["examples"]


def test_the_opt_out_passes_and_logs_loudly(caplog, capsys) -> None:
    """With the opt-out the launch proceeds; the finding is logged as a
    warning and printed in a banner, never swallowed."""
    with caplog.at_level(logging.WARNING, logger="scripts.lib_config_validation"):
        findings = validate_no_inert_fields(
            _text_config(), source="t.json", allow_inert_fields=True)
    assert [f.field for f in findings] == ["examples"]
    assert OPT_OUT_FLAG in caplog.text and "examples is inert" in caplog.text
    printed = capsys.readouterr().out
    assert OPT_OUT_FLAG in printed and "historical reproduction" in printed


def test_an_image_config_passes() -> None:
    """Example images on: the list reaches the model, nothing is inert."""
    assert validate_no_inert_fields(_image_config()) == []


def test_the_pipeline_default_is_images_on() -> None:
    """A config WITHOUT include_example_images sent its examples (the
    pipeline defaults the key to true), so it is not a finding."""
    cfg = _text_config()
    del cfg["include_example_images"]
    assert find_inert_fields(cfg) == []


def test_a_text_only_config_without_examples_passes() -> None:
    """Text-only with nothing configured to send has nothing inert."""
    assert find_inert_fields({**_text_config(), "examples": []}) == []


def test_the_configuration_is_not_changed() -> None:
    """A reproduction's recorded configuration must stay byte-comparable with
    the original's, so the validator never mutates its input."""
    cfg = _text_config()
    before = json.dumps(cfg, sort_keys=True)
    validate_no_inert_fields(cfg, allow_inert_fields=True, warn=None)
    assert json.dumps(cfg, sort_keys=True) == before


#: The committed configurations the rule refuses as of 2026-10-06: the
#: historical text-only proposer configurations, every one of which lists an
#: exemplar library it never sent (E90). Reproducing a run from one of them
#: needs the opt-out; a new configuration of this shape turns this red.
REFUSED_COMMITTED_CONFIGS = {
    "detect_brief-text-high.json", "detect_brief-text-safemode.json",
    "detect_brief-text.json", "detect_brief-text_high-recall.json",
    "detect_brief-text_high-recall_nulls-minimal-t0.json",
    "detect_brief-text_high-recall_nulls-minimal.json",
    "detect_brief-text_high-recall_nulls.json", "detect_brief-text_terse.json",
    "detect_brief-text_verbose.json", "detect_verbose-text.json",
    "library_canonical-text.json", "library_plus-hp-text.json",
    "library_pure-positive-canon-text.json", "library_scale-4-text.json",
    "library_scale-8-text.json", "phase3c-t2-h9A.json", "phase3c-t2-h9B-v1.json",
    "phase3c-t2-h9B-v2.json", "phase3c-t2-h9B-v3.json", "phase3c-t2-h9B-v4.json",
    "phase3c-t2-h9B-v5.json", "propose_brief-text.json",
}


def test_the_committed_configs_refused_are_the_historical_text_configs() -> None:
    """Exactly the 22 historical text-only configurations are refused; every
    image and verifier configuration launches as before."""
    refused = set()
    for path in glob.glob(str(PROJECT_ROOT / "prompts" / "configs" / "**" / "*.json"),
                          recursive=True):
        cfg = json.loads(Path(path).read_text())
        if isinstance(cfg, dict) and find_inert_fields(cfg):
            refused.add(str(Path(path).relative_to(PROJECT_ROOT / "prompts" / "configs")))
    assert refused == REFUSED_COMMITTED_CONFIGS


# ── the detector entry point (4_detect_mounds_batch.py) ─────────────────

_spec = importlib.util.spec_from_file_location(
    "detect_mounds_batch_w62", PROJECT_ROOT / "scripts" / "4_detect_mounds_batch.py")
_detect = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_detect)


class _ClientCreated(Exception):
    """Raised in place of creating an API client: the run got past launch."""


def _stop_at_client(monkeypatch) -> None:
    """Make the detector stop where it would create its API client."""
    def _refuse(*_args, **_kwargs):
        raise _ClientCreated
    monkeypatch.setattr(_detect, "GOOGLE_API_KEY", "test-key")
    monkeypatch.setattr(_detect.genai, "Client", _refuse)


def test_the_realtime_path_refuses_before_any_client(tmp_path, monkeypatch) -> None:
    """detect_mounds_versioned refuses the text config at launch."""
    _stop_at_client(monkeypatch)
    path = tmp_path / "t.json"
    path.write_text(json.dumps(_text_config()))
    with pytest.raises(InertConfigurationError):
        _detect.detect_mounds_versioned(str(path), dry_run=True)


def test_the_realtime_path_with_the_opt_out_proceeds(tmp_path, monkeypatch) -> None:
    """With allow_inert_fields the launch gets as far as the client."""
    _stop_at_client(monkeypatch)
    path = tmp_path / "t.json"
    path.write_text(json.dumps(_text_config()))
    with pytest.raises(_ClientCreated):
        _detect.detect_mounds_versioned(str(path), dry_run=True,
                                        allow_inert_fields=True)


def test_the_realtime_path_launches_an_image_config(tmp_path, monkeypatch) -> None:
    """An image config is not refused (it reaches the client as before)."""
    _stop_at_client(monkeypatch)
    path = tmp_path / "i.json"
    path.write_text(json.dumps(_image_config()))
    with pytest.raises(_ClientCreated):
        _detect.detect_mounds_versioned(str(path), dry_run=True)


def _batch_args(config_path: Path, allow: bool) -> argparse.Namespace:
    """Minimal parsed arguments for the detector's batch path."""
    return argparse.Namespace(
        config=str(config_path), temperature=None, thinking_level=None, model=None,
        tile_size=None, tiles_dir=None, manifest=str(config_path.parent / "absent.json"),
        allow_inert_fields=allow)


def test_the_batch_path_refuses_and_the_opt_out_proceeds(tmp_path, monkeypatch) -> None:
    """_detect_mounds_batch refuses at launch; with the opt-out it proceeds
    to the next launch step (here a missing manifest, which returns None)."""
    _stop_at_client(monkeypatch)
    path = tmp_path / "t.json"
    path.write_text(json.dumps(_text_config()))
    with pytest.raises(InertConfigurationError):
        _detect._detect_mounds_batch(_batch_args(path, allow=False))
    assert _detect._detect_mounds_batch(_batch_args(path, allow=True)) is None


# ── the study runner (run_phase2.py) ─────────────────────────────────────

def test_run_phase2_refuses_an_inert_condition_at_launch(tmp_path) -> None:
    """Every condition's configuration is checked before any unit runs; the
    opt-out clears the check."""
    from scripts.run_phase2 import validate_condition_configs
    text, image = tmp_path / "t.json", tmp_path / "i.json"
    text.write_text(json.dumps(_text_config()))
    image.write_text(json.dumps(_image_config()))
    conditions = [{"name": "a", "config": str(text)},
                  {"name": "b", "config": str(image)}]
    errors = validate_condition_configs(conditions)
    assert len(errors) == 1 and "examples is inert" in errors[0]
    assert validate_condition_configs(conditions, allow_inert_fields=True) == []
    assert validate_condition_configs([conditions[1]]) == []


def test_run_phase2_passes_the_opt_out_to_the_detector(capsys) -> None:
    """A concurrent-mode unit launched with the opt-out passes it on, or the
    detector subprocess would refuse the configuration the study allowed."""
    from scripts.run_phase2 import run_execution_unit
    unit = {"condition_name": "T0.0", "run": 1,
            "config": "prompts/configs/detect_brief-text.json",
            "temperature": 0.0, "ordering": None}
    config = {"inputs": {"manifest": "inputs/tiles/m.json"},
              "execution": {"workers": 1, "output_dir": "outputs/x"}}
    run_execution_unit(unit, config, Path("/tmp"), dry_run=True,
                       allow_inert_fields=True)
    assert OPT_OUT_FLAG in capsys.readouterr().out
    run_execution_unit(unit, config, Path("/tmp"), dry_run=True)
    assert OPT_OUT_FLAG not in capsys.readouterr().out
