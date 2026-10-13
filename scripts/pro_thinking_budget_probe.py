#!/usr/bin/env python3
"""Can an explicit thinking budget make Gemini 3.1 Pro think? (D64 add-on probe)

Gemini 3.1 Pro asked for ``thinking_level`` HIGH delivers no thought tokens on
this task (June 2026, invoice-confirmed; the 2026-10-12 probe at T 0.0, 0.7,
and 1.0). This probe asks whether an explicit ``thinking_budget`` does better.
It runs the project's own runner (``scripts/4_detect_mounds_batch.py``) so the
request is byte-for-byte the production one, with ONE change: the runner's
``types.ThinkingConfig`` is replaced, for this process only, by one that sends
``thinking_budget=N`` instead of ``thinking_level``. Everything else (config
``detect_brief-text.json``, model ``gemini-3.1-pro``, 384 px tiles, the
10-tile seeded subset, T 0.7, real-time standard tier, up to 3 attempts) is
fixed. Each request's ``thoughts_tokens`` lands in the run's
``per_item_metadata``.

If the API refuses ``thinking_budget`` for this model, the refusal is itself
the answer, and it is recorded in the meta.

Usage::

    python scripts/pro_thinking_budget_probe.py --budget 1024 \\
        --output-dir outputs/pro-2x2-replication-2026-10-13/probe/budget-1024
    python scripts/pro_thinking_budget_probe.py --budget 0 \\
        --output-dir outputs/pro-2x2-replication-2026-10-13/probe/level-high

``--budget 0`` is the control: the runner's own ``thinking_level`` HIGH.
"""
from __future__ import annotations

import argparse
import json
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

MANIFEST = ROOT / "outputs/pro-2x2-replication-2026-10-13/tiles-10-smoke-seed42.json"


def main() -> int:
    """Run the 10-tile probe with the requested thinking control."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--budget", type=int, required=True,
                    help="thinking_budget to send; 0 = the control (thinking_level high)")
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    spec = importlib.util.spec_from_file_location(
        "detect_runner", ROOT / "scripts" / "4_detect_mounds_batch.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)

    if args.budget > 0:
        real = runner.types.ThinkingConfig

        def budget_config(**_kwargs):
            """Send thinking_budget in place of the configured thinking_level."""
            return real(thinking_budget=args.budget)

        runner.types.ThinkingConfig = budget_config  # this process only

    runner.detect_mounds_versioned(
        str(ROOT / "prompts/configs/detect_brief-text.json"),
        manifest_path=str(MANIFEST),
        output_dir=args.output_dir,
        model_override="gemini-3.1-pro",
        temperature_override=0.7,
        thinking_level_override="high",
        tile_size=384,
        tiles_dir_override=str(ROOT / "inputs/tiles_384"),
        workers=4,
        max_retries=3,
        service_tier=None,  # real-time standard
        skip_intent_check=True,
        allow_inert_fields=True,
    )
    # The meta records the configured thinking_level; record what was sent.
    note = {"thinking_control_sent": (f"thinking_budget={args.budget}" if args.budget > 0
                                      else "thinking_level=high (control)"),
            "script": "scripts/pro_thinking_budget_probe.py", "ruling": "D64"}
    (Path(args.output_dir) / "probe_note.json").write_text(json.dumps(note, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
