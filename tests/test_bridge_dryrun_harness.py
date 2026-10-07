#!/usr/bin/env python3
"""
Tier-1 tests for ``scripts/bridge_dryrun_harness.py``.

The harness exists to prove that a proposer rehearsal reaches no server, so
the guards are the critical path: the socket block must refuse a connection
and record it, and the stub client must expose model listing and nothing
else. The guards patch process-global state (the socket module, the SDK's
``Client``), so they are exercised in a child interpreter and never in the
test process itself.

The request summaries are then checked on synthetic batch lines: the tile is
elided so that every line of one arm shares one signature, the tile-set
digest is order-independent, and a cached request is told apart from an
inline one.
"""

from __future__ import annotations

import base64
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import bridge_dryrun_harness as h  # noqa: E402

pytestmark = pytest.mark.tier1

REPO_ROOT = Path(__file__).resolve().parent.parent


def _line(key: str, tile: bytes, cached: bool = False) -> dict:
    """Build one synthetic batch JSONL line shaped like build_jsonl_file's.

    Args:
        key: Tile name.
        tile: Tile image bytes.
        cached: Whether the line names a context cache.

    Returns:
        The parsed line.
    """
    parts = [] if cached else [{"text": "Here are the Reference Symbols you must find:"}]
    parts += [{"text": "Now, find detection instances ..."},
              {"inline_data": {"mime_type": "image/png",
                               "data": base64.b64encode(tile).decode()}}]
    req = {"contents": [{"parts": parts, "role": "user"}],
           "generation_config": {"temperature": 0.7, "max_output_tokens": 8192,
                                 "response_mime_type": "application/json",
                                 "thinking_config": {"thinking_level": "MINIMAL"}}}
    if cached:
        req["cached_content"] = "cachedContents/X"
    else:
        req["system_instruction"] = {"parts": [{"text": "SYSTEM"}]}
    return {"key": key, "request": req}


@pytest.mark.parametrize("attempt", [
    # A numeric address skips name resolution, so this exercises connect().
    "socket.socket().connect(('127.0.0.1', 9))",
    "socket.getaddrinfo('example.invalid', 443)",
    "socket.create_connection(('example.invalid', 443))",
])
def test_socket_block_refuses_and_records_in_a_child(attempt: str) -> None:
    """Each network entry point raises after block_network() and is recorded."""
    code = (
        "import sys; sys.path.insert(0, 'scripts')\n"
        "import socket, bridge_dryrun_harness as h\n"
        "h.block_network()\n"
        "try:\n"
        f"    {attempt}\n"
        "except h.NetworkBlocked:\n"
        "    print('BLOCKED', len(h.BREACHES))\n"
        "except Exception as exc:\n"
        "    print('ESCAPED', type(exc).__name__)\n"
    )
    out = subprocess.run([sys.executable, "-c", code], cwd=REPO_ROOT,
                         capture_output=True, text=True, timeout=60)
    assert out.stdout.strip() == "BLOCKED 1", out.stdout + out.stderr


def test_stub_client_lists_only_the_pinned_model() -> None:
    """models.list() reports the pinned name in the SDK's 'models/' form."""
    client = h.make_stub_client(["gemini-3.7-flash"])()
    assert [m.name for m in client.models.list()] == ["models/gemini-3.7-flash"]


@pytest.mark.parametrize("attr", ["files", "batches", "caches"])
def test_stub_client_forbids_every_other_surface(attr: str) -> None:
    """Uploads, batch jobs and caches all raise outside capture mode."""
    client = h.make_stub_client(["m"])()
    with pytest.raises(h.StubCalled):
        getattr(getattr(client, attr), "create")


def test_stub_generate_content_is_forbidden_without_capture() -> None:
    """A rehearsal (no capture sink) can never reach generate_content."""
    client = h.make_stub_client(["m"])()
    with pytest.raises(h.StubCalled):
        client.models.generate_content(model="m", contents=[], config=None)


def test_capture_mode_records_then_stops() -> None:
    """Capture mode records the request and raises the deliberate stop."""
    sink: list = []
    client = h.make_stub_client(["m"], sink)()
    with pytest.raises(h.StubCalled, match="captured"):
        client.models.generate_content(model="m", contents="c", config="g")
    assert sink == [{"kind": "generate_content", "model": "m",
                     "contents": "c", "config": "g"}]


def test_elided_signature_ignores_only_the_tile() -> None:
    """Two lines differing only in tile share one elided signature."""
    a = h.summarise_jsonl_line(_line("a.png", b"AAA"))
    b = h.summarise_jsonl_line(_line("b.png", b"BBB"))
    assert a["parts"][-1] != b["parts"][-1]
    assert h.elide_tile(a) == h.elide_tile(b)


def test_cached_line_differs_from_inline_line() -> None:
    """A cached request has no preamble or system instruction in the line."""
    inline = h.summarise_jsonl_line(_line("a.png", b"A"))
    cached = h.summarise_jsonl_line(_line("a.png", b"A", cached=True))
    assert inline["system_instruction_sha256"] is not None
    assert cached["system_instruction_sha256"] is None
    assert cached["cached_content"] == "cachedContents/X"
    assert h.elide_tile(inline) != h.elide_tile(cached)


def test_tile_set_digest_is_order_independent() -> None:
    """The digest depends on the (name, hash) pairs, not their order."""
    rows = [("a.png", "1"), ("b.png", "2")]
    assert h.tile_set_digest(rows) == h.tile_set_digest(list(reversed(rows)))
    assert h.tile_set_digest(rows) != h.tile_set_digest([("a.png", "1")])


def test_summarise_build_checks_keys_against_the_manifest(tmp_path: Path) -> None:
    """Line count, key order and one signature are read from the file."""
    path = tmp_path / "x.jsonl"
    path.write_text("\n".join(json.dumps(_line(k, k.encode())) for k in
                              ["a.png", "b.png", "c.png"]) + "\n")
    s = h.summarise_build(path, ["a.png", "b.png", "c.png"])
    assert s["n_lines"] == 3
    assert s["keys_match_manifest_slice"] is True
    assert list(s["elided_signatures"].values()) == [3]
    assert h.summarise_build(path, ["c.png", "b.png", "a.png"])[
        "keys_match_manifest_slice"] is False


def test_pinned_model_prefers_the_cli_pin(tmp_path: Path) -> None:
    """--model wins; unpinned, the config's model resolves to -preview."""
    cfg = tmp_path / "c.json"
    cfg.write_text(json.dumps({"model": "gemini-3-flash"}))
    assert h._pinned_model(["--config", str(cfg), "--model", "x"]) == ["x"]
    assert h._pinned_model(["--config", str(cfg)]) == ["gemini-3-flash-preview"]
