"""A dry run of the proposer runner must not create a context cache.

A context cache is billed storage from the moment it exists. Until
2026-10-12 ``detect_mounds_versioned`` created the cache before its dry-run
exit and deleted it only at the end of a real pass, so every
``--use-cache --dry-run`` left a cache alive for its whole TTL (24 hours by
default). The test drives a real dry run through a fake client that records
every call and refuses ``caches.create``; it skips when the tracked inputs
it needs are absent.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.tier1

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))  # the runner imports its siblings bare

CONFIG = ROOT / "prompts" / "configs" / "library_plus-hp.json"
TILES_DIR = ROOT / "inputs" / "tiles_384"
TILE = "K-35-052-4_32635_x0_y0.png"


def _load_runner():
    """Import ``scripts/4_detect_mounds_batch.py`` (its name starts with a digit)."""
    spec = importlib.util.spec_from_file_location(
        "detect_mounds_batch_dry_run", ROOT / "scripts" / "4_detect_mounds_batch.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _FakeCaches:
    """Records cache calls; creating one is the defect under test."""

    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def create(self, **kwargs):
        self.calls.append("caches.create")
        raise AssertionError("a dry run created a context cache")

    def delete(self, **kwargs):
        self.calls.append("caches.delete")


class _FakeModels:
    """Answers the free model-name resolution with the model it is asked for."""

    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def list(self):
        self.calls.append("models.list")
        return [SimpleNamespace(name="models/gemini-3.1-pro-preview")]


def _fake_client_factory(calls: list[str]):
    def factory(*args, **kwargs):
        return SimpleNamespace(caches=_FakeCaches(calls), models=_FakeModels(calls))
    return factory


@pytest.mark.skipif(not (CONFIG.exists() and (TILES_DIR / TILE.split("_x")[0] / TILE).exists()),
                    reason="needs the tracked image config and one 384 px tile")
def test_dry_run_with_cache_makes_no_cache_call(tmp_path, monkeypatch, capsys):
    """``--use-cache --dry-run`` validates and exits without touching the cache API."""
    runner = _load_runner()
    calls: list[str] = []
    monkeypatch.setattr(runner.genai, "Client", _fake_client_factory(calls))
    # The runner reads the key as a module constant imported from config.
    monkeypatch.setattr(runner, "GOOGLE_API_KEY", "test-key-not-real")
    manifest = tmp_path / "one-tile.json"
    manifest.write_text(f'["{TILE}"]')

    runner.detect_mounds_versioned(
        str(CONFIG), manifest_path=str(manifest), output_dir=str(tmp_path / "out"),
        model_override="gemini-3.1-pro", thinking_level_override="high",
        tile_size=384, tiles_dir_override=str(TILES_DIR),
        use_cache=True, dry_run=True, skip_intent_check=True,
    )

    assert not [c for c in calls if c.startswith("caches.")]
    assert "not created (dry run)" in capsys.readouterr().out
