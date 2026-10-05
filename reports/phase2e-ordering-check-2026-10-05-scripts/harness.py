"""
Offline replay of the retest Phase 2e batch preparation at commit 5a57f586e.

Purpose:
    Drive the real ``run_phase2.run_phase2()`` (batch mode, dry run) from a
    ``git archive`` snapshot of 5a57f586e so that the actual reorder and the
    actual JSONL builder run on the actual study YAML and prompt config, with
    NO network access. The google-genai client is replaced by a stub that
    raises on any use other than the guarded ``models.list()`` call (which the
    runner wraps in try/except), so no request can leave the machine.

Usage:
    HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 \
        GOOGLE_API_KEY=offline-dummy python harness.py <snapshot-root> <limit>
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
LIMIT = int(sys.argv[2])


class _Refuse:
    """Any attribute access or call raises: proves no API path is taken."""

    def __getattr__(self, name):
        raise RuntimeError(f"offline stub: attribute {name!r} refused")


class _Models:
    def list(self):
        raise RuntimeError("offline stub: models.list refused")


class StubClient:
    """Stand-in for google.genai.Client; records construction, refuses I/O."""

    instances: list = []

    def __init__(self, *args, **kwargs):
        StubClient.instances.append(kwargs)
        self.models = _Models()
        self.files = _Refuse()
        self.batches = _Refuse()


# Install the stub BEFORE the runner's lazy ``from google import genai``.
import google  # noqa: E402  (real namespace package)

stub = types.ModuleType("google.genai")
stub.Client = StubClient
sys.modules["google.genai"] = stub
google.genai = stub

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import run_phase2  # noqa: E402  (the 5a57f586e copy)

assert Path(run_phase2.__file__).resolve().is_relative_to(ROOT), run_phase2.__file__

result = run_phase2.run_phase2(
    study_path=ROOT / "studies/retest/phase2e-h4-ordering.yaml",
    dry_run=True,
    resume=False,
    limit=LIMIT,
    verbose=True,
    mode="batch",
)
print("RESULT:", result)
print("STUB CLIENT CONSTRUCTIONS:", StubClient.instances)
