#!/usr/bin/env python3
"""
topup_batch_failed_tiles.py — top up a batch pass's failed tiles in BATCH mode
==============================================================================

Why this exists
---------------
Wave 3 of the D64 same-day Gemini 3.1 Pro replication (image runs 4-6, ruling
D66 (4); data commit ``9664f1094``) finished with 152 tiles failed as
``batch_api_error`` in eight of its twelve passes (HIGH T0.0 runs 4/5/6:
9/2/0; HIGH T0.7: 5/3/7; MEDIUM T0.0: 19/83/0; MEDIUM T0.7: 24/0/0). PI
ruling D67 (1) (2026-10-15, Session 164) approved topping them up in BATCH
mode, the passes' own mode. D64 was designed to remove the date and mode
confounds; these failures cluster in the MEDIUM corners, where the image
surprises sit; and a real-time top-up would leave one pass 17 % real-time
(83 of its 487 tiles).

Why a new tool
--------------
``4_detect_mounds_batch.py`` resumes a batch pass per CHUNK ("Skip chunks
whose output already exists"), so re-running a 487-tile single-chunk pass
sends nothing. Tile-level resume exists only on the real-time path, and
``lib_batch_api.patch_failed_tiles`` (used by the real-time top-up of
2026-10-13, ``scripts/topup_pro_2x2_failed_tiles.py``) retries synchronously.
This tool sends each pass's failed tiles as their own Batch API job with the
pass's own command, then merges the result into the pass.

What it does, per pass with failed tiles
----------------------------------------
1. Scope gate: the pass sidecar's ``failed`` list must equal its meta's
   ``failed_items`` and the approved count, or nothing is sent.
2. Writes a manifest of exactly those tiles, in the format and order of
   ``inputs/tiles_384/full_evaluation_manifest.json``.
3. Runs ``4_detect_mounds_batch.py`` with the pass's own arguments (as
   ``run_pass`` in ``scripts/run_pro_2x2_replication.sh`` gives them) except
   ``--manifest <failed tiles>`` and ``--output-dir <scratch work dir>``. The
   one other difference: ``run_pass`` also passed ``--workers 4``, which the
   batch path never reads (``4_detect_mounds_batch.py`` dispatches batch mode
   before ``workers`` is used), so it is left out.
4. Deletes the context cache the top-up created once its job is terminal.
   The batch path creates one per pass with a 24-hour time to live and never
   deletes it; at the Gemini 3.1 Pro storage rate (US$4.50 per million tokens
   per hour, ``data/pricing/gemini-rate-card.json``) a 14,549-token cache
   left for its full day costs about US$1.57 (ruling D52: delete caches no
   longer needed).
5. Parameter-control gate: the top-up meta's model version, system-instruction
   hash, library hash, temperature, thinking level,
   ``include_example_images``, and caching (cached tokens per response) must
   equal the pass's, together with the project's other cleanup gate fields
   and the execution mode; the request file actually sent is checked against
   the pass's generation settings and cache use. Any difference: nothing is
   merged.
6. Archives the pass's pre-top-up ``.geojson``, ``.meta.json`` and
   ``.tiles.json`` to ``archive/pre-topup-2026-10-15/<corner>__<config>__run_<n>/``,
   then merges: top-up features appended, ``processed_tiles`` unioned, the
   sidecar's ``completed``/``failed`` updated, and the meta merged with the
   project's resume merge (``lib_llm_metadata.merge_meta_into_existing``),
   whose ``recovery_history`` entry gains the mode, batch job name, request
   file, and context cache. The top-up's own outputs and manifest are kept
   beside the archive (``topup-batch-outputs/``), outside ``outputs/``, so no
   tool that sums every ``*.meta.json`` under a run directory counts the
   top-up twice.

Single round: tiles still failing are reported, not retried.

Usage (repository root, on the machine that runs the top-up)::

    # Dry run (the default): scope gate, manifests, the exact commands, and a
    # detector --dry-run per pass (a free models.list call; no cache, no
    # upload, no batch job). Writes only under --work-dir.
    python scripts/topup_batch_failed_tiles.py --work-dir ~/scratch/topup

    # The trial pass alone, then the rest (two detector processes at a time)
    python scripts/topup_batch_failed_tiles.py --work-dir ~/scratch/topup \\
        --live --only image-high-t0.0/run_5
    python scripts/topup_batch_failed_tiles.py --work-dir ~/scratch/topup --live

    # After the topped-up outputs are committed: release the request uploads
    python scripts/topup_batch_failed_tiles.py --work-dir ~/scratch/topup \\
        --release-uploads

Outputs: the merged passes in place; the record
``outputs/pro-2x2-replication-2026-10-13/topup-2026-10-15.json``; the tool
log ``_run_log_topup-2026-10-15.txt`` and per-pass detector logs
``<corner>.run_<n>.topup-2026-10-15.log`` beside the wave logs; the archive
under ``archive/pre-topup-2026-10-15/``.

Created: 2026-10-15 (Session 164)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import concurrent.futures
import copy
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.lib_batch_api import locate_pass_files  # noqa: E402
from scripts.lib_llm_metadata import (  # noqa: E402
    CLEANUP_GATE_FIELDS,
    compare_configurations,
    merge_meta_into_existing,
)
from scripts.merge_recovery_meta import refuse_cumulative  # noqa: E402

logger = logging.getLogger("topup_batch_failed_tiles")

# ─────────────────────────────────────────────────────────────────────
# The D64 wave-3 top-up (ruling D67 (1))
# ─────────────────────────────────────────────────────────────────────

#: The replication's output root.
BASE: Path = REPO_ROOT / "outputs" / "pro-2x2-replication-2026-10-13"
#: The image corners' config (``run_pass``'s ``CORNERS`` table).
CONFIG_NAME = "library_plus-hp"
CONFIG_PATH = "prompts/configs/library_plus-hp.json"
#: The model as ``run_pass`` passes it (resolved to ``gemini-3.1-pro-preview``).
MODEL_CLI = "gemini-3.1-pro"
TILES_DIR = "inputs/tiles_384"
TILE_SIZE = "384"
FULL_MANIFEST: Path = REPO_ROOT / TILES_DIR / "full_evaluation_manifest.json"
#: The service tier of the detector's synchronous parse-failure retries, as
#: ``run_pass`` sets it (the batch itself bills at the batch tier).
RETRY_SERVICE_TIER = "flex"

#: corner -> (temperature as ``run_pass`` passes it, thinking level).
CORNERS: dict[str, tuple[str, str]] = {
    "image-high-t0.0": ("0.0", "high"),
    "image-high-t0.7": ("0.7", "high"),
    "image-medium-t0.0": ("0.0", "medium"),
    "image-medium-t0.7": ("0.7", "medium"),
}
WAVE3_RUNS: tuple[int, ...] = (4, 5, 6)

#: Failed tiles per wave-3 pass as committed in ``9664f1094`` (152 in all).
#: The scope gate refuses a pass whose sidecar disagrees.
APPROVED_FAILED: dict[str, int] = {
    "image-high-t0.0/run_4": 9, "image-high-t0.0/run_5": 2, "image-high-t0.0/run_6": 0,
    "image-high-t0.7/run_4": 5, "image-high-t0.7/run_5": 3, "image-high-t0.7/run_6": 7,
    "image-medium-t0.0/run_4": 19, "image-medium-t0.0/run_5": 83,
    "image-medium-t0.0/run_6": 0,
    "image-medium-t0.7/run_4": 24, "image-medium-t0.7/run_5": 0,
    "image-medium-t0.7/run_6": 0,
}

ARCHIVE_DIR: Path = REPO_ROOT / "archive" / "pre-topup-2026-10-15"
#: Subfolder of :data:`ARCHIVE_DIR` that keeps each top-up's own outputs.
RAW_ARCHIVE_SUBDIR = "topup-batch-outputs"
RECORD_PATH: Path = BASE / "topup-2026-10-15.json"
TOOL_LOG: Path = BASE / "_run_log_topup-2026-10-15.txt"
LOG_TAG = "topup-2026-10-15"
TOOL_NAME = "scripts/topup_batch_failed_tiles.py"
RULING = "D67 (1)"
#: Stop rule from the brief: no further pass is launched once the top-up's
#: cumulative cost would exceed this.
COST_CAP_USD = 2.00

# ─────────────────────────────────────────────────────────────────────
# The gate's field sets
# ─────────────────────────────────────────────────────────────────────

#: The fields D67 (1) names, read from each meta's ``configuration`` block.
REQUIRED_GATE_FIELDS: tuple[str, ...] = (
    "model",
    "system_instruction_hash",
    "library_hash",
    "temperature",
    "thinking_level",
    "include_example_images",
)
#: The project's other cleanup gate fields (``CLEANUP_GATE_FIELDS``) and two
#: that qualify the library hash. Held to strict equality as well.
EXTRA_GATE_FIELDS: tuple[str, ...] = tuple(
    f for f in CLEANUP_GATE_FIELDS if f not in REQUIRED_GATE_FIELDS
) + ("library_hash_basis", "example_count")

_MISSING = "<missing>"

#: Detector log lines.
JOB_RE = re.compile(r"Submitted batch job: (batches/\S+)")
RELEASED_RE = re.compile(r"Released request file (files/\S+)")
#: Failure signatures, matched case-insensitively (project watcher rule).
FAILURE_RE = re.compile(
    r"traceback|failed to lodge|partial|completeness gap|error|failed:", re.IGNORECASE,
)


class TopupError(RuntimeError):
    """A check failed; nothing was merged into the pass."""


@dataclass(frozen=True)
class PassSpec:
    """One pass of the replication and the arguments it was run with.

    Attributes:
        corner: Corner directory name, e.g. ``image-high-t0.0``.
        run: Pass number.
        temperature: Temperature exactly as ``run_pass`` passed it.
        thinking_level: Thinking level as ``run_pass`` passed it.
        base: Replication output root.
        config_name: Config version (the pool directory name).
        config_path: Config file, relative to the repository root.
        model: Model as ``run_pass`` passed it.
        use_cache: Whether ``run_pass`` passed ``--use-cache`` (image: yes).
    """

    corner: str
    run: int
    temperature: str
    thinking_level: str
    base: Path = BASE
    config_name: str = CONFIG_NAME
    config_path: str = CONFIG_PATH
    model: str = MODEL_CLI
    use_cache: bool = True

    @property
    def key(self) -> str:
        """Short pass key, e.g. ``image-high-t0.0/run_5``."""
        return f"{self.corner}/run_{self.run}"

    @property
    def pass_dir(self) -> Path:
        """The pass directory in the replication tree."""
        return self.base / self.corner / self.config_name / f"run_{self.run}"

    @property
    def archive_name(self) -> str:
        """Archive folder name, ``<corner>__<config>__run_<n>``."""
        return f"{self.corner}__{self.config_name}__run_{self.run}"


def wave3_specs(base: Path = BASE) -> list[PassSpec]:
    """The twelve wave-3 image passes, in corner and run order.

    Args:
        base: Replication output root (tests pass a synthetic one).

    Returns:
        One :class:`PassSpec` per corner and run.
    """
    return [PassSpec(corner=corner, run=run, temperature=temp, thinking_level=think,
                     base=base)
            for corner, (temp, think) in CORNERS.items() for run in WAVE3_RUNS]


def pass_rel(spec: PassSpec) -> str:
    """The pass's path under the replication root, ``<corner>/<config>/run_<n>``."""
    return f"{spec.corner}/{spec.config_name}/run_{spec.run}"


# ─────────────────────────────────────────────────────────────────────
# Small file helpers
# ─────────────────────────────────────────────────────────────────────


def now_utc() -> str:
    """The current UTC time as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> Any:
    """Load a JSON file."""
    with open(path) as f:
        return json.load(f)


def write_json_atomic(path: Path, obj: Any, indent: int | None) -> None:
    """Write JSON through a ``.tmp`` sibling and a rename (no truncation on kill).

    Args:
        path: Destination.
        obj: JSON-serialisable object.
        indent: ``None`` for the compact form the GeoJSON writer uses, 2 for
            the sidecar and meta.
    """
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=indent)
    tmp.replace(path)


def rel(path: Path) -> str:
    """A path relative to the repository root when inside it, else absolute."""
    try:
        return str(Path(path).resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def pass_files(pass_dir: Path) -> dict[str, Path]:
    """The one GeoJSON, tiles sidecar, and meta that are the pass in *pass_dir*.

    Args:
        pass_dir: A pass directory (``.../run_<n>``).

    Returns:
        ``{"geojson", "tiles", "meta"}`` paths.

    Raises:
        TopupError: The directory does not hold exactly one of each
            (``lib_batch_api.locate_pass_files`` refuses chunk-only or
            ambiguous layouts).
    """
    located = locate_pass_files(pass_dir)
    if located is None:
        raise TopupError(f"{pass_dir}: no single geojson/tiles/meta set")
    geojson, tiles, meta = located
    return {"geojson": geojson, "tiles": tiles, "meta": meta}


def failed_item_ids(meta: dict[str, Any]) -> list[str]:
    """The ids in a meta's ``execution_stats.failed_items`` (dicts or strings)."""
    out: list[str] = []
    for item in (meta.get("execution_stats") or {}).get("failed_items") or []:
        out.append(str(item.get("item_id") if isinstance(item, dict) else item))
    return out


# ─────────────────────────────────────────────────────────────────────
# Scope gate and manifest
# ─────────────────────────────────────────────────────────────────────


def scope_failed_tiles(pass_dir: Path, approved: int | None) -> list[str]:
    """The pass's failed tiles, checked against its meta and the approved count.

    Args:
        pass_dir: The pass directory.
        approved: The approved failed-tile count, or ``None`` to skip that
            comparison.

    Returns:
        The failed tile names, sorted.

    Raises:
        TopupError: The sidecar and the meta disagree, a tile appears twice,
            or the count differs from the approved one.
    """
    files = pass_files(pass_dir)
    sidecar = list(read_json(files["tiles"]).get("failed") or [])
    from_meta = failed_item_ids(read_json(files["meta"]))
    if len(set(sidecar)) != len(sidecar):
        raise TopupError(f"{pass_dir}: the sidecar lists a failed tile twice")
    if sorted(sidecar) != sorted(from_meta):
        raise TopupError(
            f"{pass_dir}: scope gate: sidecar lists {len(sidecar)} failed tiles, the meta "
            f"{len(from_meta)}, and they differ")
    if approved is not None and len(sidecar) != approved:
        raise TopupError(
            f"{pass_dir}: scope gate: {len(sidecar)} failed tiles, {approved} approved")
    return sorted(sidecar)


def write_failed_manifest(failed: list[str], full_manifest: Path, out_path: Path) -> list[str]:
    """Write a manifest of exactly *failed*, in the full manifest's format and order.

    The format is the one ``inputs/tiles_384/full_evaluation_manifest.json``
    uses (a JSON list of tile file names, two-space indent), so the detector
    reads it exactly as it reads the full manifest.

    Args:
        failed: The tiles to send.
        full_manifest: The manifest the pass was run on.
        out_path: Where to write.

    Returns:
        The tiles as written, in manifest order.

    Raises:
        TopupError: A failed tile is not in the full manifest, *failed* holds
            a duplicate, or the written file does not read back as *failed*.
    """
    order = read_json(full_manifest)
    if not isinstance(order, list):
        raise TopupError(f"{full_manifest}: not a list manifest")
    if len(set(failed)) != len(failed):
        raise TopupError("failed-tile list holds a duplicate")
    unknown = sorted(set(failed) - set(order))
    if unknown:
        raise TopupError(f"tiles not in {full_manifest.name}: {unknown}")
    wanted = set(failed)
    seen: set[str] = set()
    tiles: list[str] = []
    for tile in order:
        if tile in wanted and tile not in seen:
            tiles.append(tile)
            seen.add(tile)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(tiles, indent=2) + "\n")
    if sorted(read_json(out_path)) != sorted(failed):
        raise TopupError(f"{out_path}: manifest does not read back as the failed tiles")
    return tiles


# ─────────────────────────────────────────────────────────────────────
# The detector command and its by-products
# ─────────────────────────────────────────────────────────────────────


def detector_command(spec: PassSpec, manifest: Path, output_dir: Path, *,
                     python: str, dry_run: bool) -> list[str]:
    """The pass's own detector command, aimed at the failed tiles only.

    Mirrors ``run_pass`` in ``scripts/run_pro_2x2_replication.sh`` argument by
    argument, except ``--manifest`` and ``--output-dir`` (and ``--workers``,
    which the batch path never reads; see the module docstring).

    Args:
        spec: The pass.
        manifest: The failed-tile manifest.
        output_dir: Where the detector writes ``<config>/run_<n>/...``.
        python: Interpreter to run the detector with.
        dry_run: Add ``--dry-run`` (no cache, no upload, no batch job).

    Returns:
        The argument vector (run from the repository root).
    """
    cmd = [
        python, "scripts/4_detect_mounds_batch.py",
        "--config", spec.config_path,
        "--model", spec.model,
        "--temperature", spec.temperature,
        "--thinking-level", spec.thinking_level,
        "--manifest", str(manifest),
        "--tiles-dir", TILES_DIR,
        "--tile-size", TILE_SIZE,
        "--output-dir", str(output_dir),
        "--mode", "batch",
        "--run", str(spec.run),
    ]
    if spec.use_cache:
        cmd.append("--use-cache")
    cmd += ["--skip-intent-check", "--allow-inert-fields",
            "--service-tier", RETRY_SERVICE_TIER]
    if dry_run:
        cmd.append("--dry-run")
    return cmd


def topup_unit_dir(spec: PassSpec, output_dir: Path) -> Path:
    """Where the detector writes the top-up pass (``<out>/<config>/run_<n>``)."""
    return output_dir / spec.config_name / f"run_{spec.run}"


def request_file_path(spec: PassSpec, output_dir: Path) -> Path:
    """The request JSONL the detector builds for the top-up (kept on disc)."""
    return (topup_unit_dir(spec, output_dir) / "batch_working"
            / f"detections_{spec.config_name}_run{spec.run:02d}.jsonl")


def run_detector(cmd: list[str], log_path: Path, cwd: Path = REPO_ROOT) -> int:
    """Run the detector with all three descriptors redirected; return its exit code.

    Exit codes (``4_detect_mounds_batch.py``): 0 every tile landed, 1 setup
    error, 2 some tiles still failed.
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as log, open(os.devnull) as devnull:
        log.write(f"=== {now_utc()} START {' '.join(cmd)}\n")
        log.flush()
        proc = subprocess.run(cmd, cwd=cwd, stdin=devnull, stdout=log,
                              stderr=subprocess.STDOUT, check=False)
        log.write(f"\n=== {now_utc()} END exit={proc.returncode}\n")
    return proc.returncode


def parse_detector_log(text: str) -> dict[str, list[str]]:
    """Batch job names, released request files, and failure lines in a log.

    Args:
        text: The detector log.

    Returns:
        ``{"batch_jobs", "request_files", "failure_lines"}``. Failure lines are
        matched case-insensitively; "Accepting partial result" is among them
        by design, so the reader sees every partial outcome.
    """
    return {
        "batch_jobs": JOB_RE.findall(text),
        "request_files": RELEASED_RE.findall(text),
        "failure_lines": [line.strip() for line in text.splitlines()
                          if FAILURE_RE.search(line)],
    }


def read_request_file(jsonl_path: Path) -> dict[str, Any]:
    """What a request file actually asked for: keys, caches, generation settings.

    Args:
        jsonl_path: The batch request JSONL.

    Returns:
        ``{"keys", "cached_content", "uncached_lines", "generation_configs"}``;
        ``cached_content`` lists the distinct cache names, and
        ``generation_configs`` the distinct ``generation_config`` blocks.
    """
    keys: list[str] = []
    caches: set[str] = set()
    uncached = 0
    configs: dict[str, dict[str, Any]] = {}
    with open(jsonl_path) as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            keys.append(entry["key"])
            request = entry.get("request") or {}
            cache = request.get("cached_content")
            if cache:
                caches.add(cache)
            else:
                uncached += 1
            gen = request.get("generation_config") or {}
            configs[json.dumps(gen, sort_keys=True)] = gen
    return {"keys": keys, "cached_content": sorted(caches), "uncached_lines": uncached,
            "generation_configs": list(configs.values())}


# ─────────────────────────────────────────────────────────────────────
# Parameter-control gate
# ─────────────────────────────────────────────────────────────────────


def caching_signature(meta: dict[str, Any]) -> dict[str, Any]:
    """Whether a pass read a context cache, and how many tokens per response.

    An explicit cache of the same prefix yields the same cached-token count
    on every response (14,549 for these passes), so equal per-response counts
    mean the top-up read the same cached prefix.

    Args:
        meta: A pass meta.

    Returns:
        ``{"cached", "cached_tokens_per_response", "n_responses_with_usage"}``.
    """
    usage = meta.get("usage_stats") or {}
    n = usage.get("n_responses_with_usage") or 0
    cached = usage.get("total_cached_tokens") or 0
    return {"cached": cached > 0,
            "cached_tokens_per_response": round(cached / n, 3) if n else None,
            "n_responses_with_usage": n}


def execution_mode(meta: dict[str, Any]) -> str | None:
    """``"batch"`` when the meta records a Batch API pass on both markers."""
    billing = (meta.get("billing") or {}).get("service_tier")
    marker = (meta.get("batch_api") or {}).get("execution_mode")
    return "batch" if billing == "batch" and marker == "batch" else (billing or marker)


def parameter_gate(pass_meta: dict[str, Any], topup_meta: dict[str, Any]) -> dict[str, Any]:
    """Compare a top-up's recorded configuration with its pass's.

    Strict equality on every field; a field missing from either meta fails.
    The model must match exactly (both record the resolved name).

    Args:
        pass_meta: The pass meta (before the merge).
        topup_meta: The top-up meta.

    Returns:
        ``{"passed", "fields": {name: {"pass", "topup", "equal"}},
        "advisory_config_diff"}``. The advisory list is the full
        configuration-fingerprint diff (``compare_configurations``), recorded
        but not blocking, as the project's cleanup gate treats it.
    """
    pass_cfg = pass_meta.get("configuration") or {}
    topup_cfg = topup_meta.get("configuration") or {}
    fields: dict[str, dict[str, Any]] = {}
    for name in REQUIRED_GATE_FIELDS + EXTRA_GATE_FIELDS:
        a = pass_cfg.get(name, _MISSING)
        b = topup_cfg.get(name, _MISSING)
        fields[name] = {"pass": a, "topup": b,
                        "equal": a != _MISSING and b != _MISSING and a == b}
    a_cache = caching_signature(pass_meta)
    b_cache = caching_signature(topup_meta)
    cache_equal = (a_cache["cached"] == b_cache["cached"]
                   and (not a_cache["cached"]
                        or (a_cache["cached_tokens_per_response"] is not None
                            and a_cache["cached_tokens_per_response"]
                            == b_cache["cached_tokens_per_response"])))
    fields["caching"] = {"pass": a_cache, "topup": b_cache, "equal": cache_equal}
    a_mode, b_mode = execution_mode(pass_meta), execution_mode(topup_meta)
    fields["execution_mode"] = {"pass": a_mode, "topup": b_mode,
                                "equal": a_mode == b_mode == "batch"}
    return {"passed": all(f["equal"] for f in fields.values()), "fields": fields,
            "advisory_config_diff": compare_configurations(pass_meta, topup_meta)}


def request_gate(jsonl_path: Path | None, manifest_tiles: list[str],
                 pass_meta: dict[str, Any]) -> dict[str, Any]:
    """Check the request file actually sent against the pass's settings.

    Args:
        jsonl_path: The top-up's request JSONL, or ``None`` when it is absent.
        manifest_tiles: The tiles the top-up was meant to send.
        pass_meta: The pass meta.

    Returns:
        ``{"passed", "problems", "context_cache", "n_lines"}``.
    """
    if jsonl_path is None or not Path(jsonl_path).exists():
        return {"passed": False, "problems": ["request file missing"],
                "context_cache": None, "n_lines": 0}
    shape = read_request_file(Path(jsonl_path))
    cfg = pass_meta.get("configuration") or {}
    expected = {"temperature": cfg.get("temperature"),
                "max_output_tokens": cfg.get("max_output_tokens"),
                "thinking_level": str(cfg.get("thinking_level")).upper()}
    problems: list[str] = []
    if sorted(shape["keys"]) != sorted(manifest_tiles):
        problems.append("request keys differ from the failed-tile manifest")
    for gen in shape["generation_configs"]:
        got = {"temperature": gen.get("temperature"),
               "max_output_tokens": gen.get("max_output_tokens"),
               "thinking_level": (gen.get("thinking_config") or {}).get("thinking_level")}
        if got != expected:
            problems.append(f"generation_config {got} differs from the pass's {expected}")
    if caching_signature(pass_meta)["cached"]:
        if shape["uncached_lines"] or len(shape["cached_content"]) != 1:
            problems.append("the pass read a cache; not every request names one cache")
    elif shape["cached_content"]:
        problems.append("the pass was uncached; the top-up requests name a cache")
    return {"passed": not problems, "problems": problems,
            "context_cache": shape["cached_content"][0] if shape["cached_content"] else None,
            "n_lines": len(shape["keys"])}


# ─────────────────────────────────────────────────────────────────────
# Structure checks, archive, and merge
# ─────────────────────────────────────────────────────────────────────


def topup_outcome(manifest_tiles: list[str], files: dict[str, Path]) -> tuple[list[str], list[str]]:
    """Recovered and still-failing tiles of a top-up, after structural checks.

    Args:
        manifest_tiles: The tiles the top-up sent.
        files: The top-up's ``{"geojson", "tiles", "meta"}``.

    Returns:
        ``(recovered, still_failing)``, each sorted.

    Raises:
        TopupError: The top-up covers other tiles than the manifest, lists a
            tile as both completed and failed, its meta disagrees with its
            sidecar, a feature comes from a tile it did not complete, or its
            detection count disagrees with its features.
    """
    tiles = read_json(files["tiles"])
    meta = read_json(files["meta"])
    geo = read_json(files["geojson"])
    completed = list(tiles.get("completed") or [])
    failed = list(tiles.get("failed") or [])
    universe = set(manifest_tiles)
    problems: list[str] = []
    if len(set(completed)) != len(completed) or len(set(failed)) != len(failed):
        problems.append("a tile is listed twice")
    if set(completed) & set(failed):
        problems.append("a tile is both completed and failed")
    if set(completed) | set(failed) != universe:
        problems.append("completed + failed differ from the manifest")
    if tiles.get("total_tiles") != len(universe):
        problems.append(f"total_tiles {tiles.get('total_tiles')} != {len(universe)}")
    es = meta.get("execution_stats") or {}
    if sorted(es.get("completed_items") or []) != sorted(completed):
        problems.append("meta completed_items differ from the sidecar")
    if sorted(failed_item_ids(meta)) != sorted(failed):
        problems.append("meta failed_items differ from the sidecar")
    if set(geo.get("processed_tiles") or []) != set(completed):
        problems.append("geojson processed_tiles differ from the sidecar")
    strays = {f["properties"].get("source_tile") for f in geo.get("features") or []}
    if strays - set(completed):
        problems.append(f"features from tiles not completed: {sorted(strays - set(completed))}")
    total = (meta.get("results_summary") or {}).get("total_detections")
    if total != len(geo.get("features") or []):
        problems.append(f"total_detections {total} != {len(geo.get('features') or [])} features")
    if problems:
        raise TopupError("top-up structure: " + "; ".join(problems))
    return sorted(completed), sorted(failed)


def verify_merged_pass(geo: dict[str, Any], tiles: dict[str, Any], meta: dict[str, Any],
                       universe: set[str]) -> list[str]:
    """Structural problems in a merged pass (empty when it is sound).

    Args:
        geo: The merged GeoJSON.
        tiles: The merged sidecar.
        meta: The merged meta.
        universe: Every tile of the pass (completed and failed before the top-up).

    Returns:
        A list of problems; empty means the counts and ids agree everywhere.
    """
    completed = set(tiles.get("completed") or [])
    failed = set(tiles.get("failed") or [])
    es = meta.get("execution_stats") or {}
    features = geo.get("features") or []
    problems: list[str] = []
    if completed & failed:
        problems.append("a tile is both completed and failed")
    if completed | failed != universe:
        problems.append("completed + failed differ from the pass's tiles")
    if tiles.get("total_tiles") != len(universe):
        problems.append("total_tiles changed")
    if set(geo.get("processed_tiles") or []) != completed:
        problems.append("processed_tiles differ from completed")
    if set(es.get("completed_items") or []) != completed:
        problems.append("meta completed_items differ from completed")
    if set(failed_item_ids(meta)) != failed:
        problems.append("meta failed_items differ from failed")
    if es.get("items_failed") != len(failed):
        problems.append("meta items_failed differs from failed")
    if es.get("items_processed") != len(completed):
        problems.append("meta items_processed differs from completed")
    if (meta.get("results_summary") or {}).get("total_detections") != len(features):
        problems.append("total_detections differs from the feature count")
    if {f["properties"].get("source_tile") for f in features} - completed:
        problems.append("a feature comes from a tile not completed")
    return problems


def archive_files(files: list[Path], dest: Path) -> Path:
    """Copy *files* into *dest*, refusing to overwrite a different copy.

    Args:
        files: Files to preserve.
        dest: Archive folder (created).

    Returns:
        *dest*.

    Raises:
        TopupError: *dest* already holds a different file of the same name,
            or a copy does not match its source byte for byte.
    """
    dest.mkdir(parents=True, exist_ok=True)
    for src in files:
        target = dest / src.name
        if target.exists():
            if target.read_bytes() != src.read_bytes():
                raise TopupError(f"{target} exists and differs from {src}")
            continue
        shutil.copy2(src, target)
        if target.read_bytes() != src.read_bytes():
            raise TopupError(f"archive copy of {src} does not match")
    return dest


def already_topped_up(meta: dict[str, Any]) -> bool:
    """Whether a pass meta records a top-up by this tool."""
    return any(entry.get("tool") == TOOL_NAME
               for entry in meta.get("recovery_history") or [])


def merge_topup(pass_dir: Path, topup_dir: Path, manifest_tiles: list[str],
                archive_dest: Path, history_extra: dict[str, Any], *,
                request_file: Path | None = None,
                require_request_file: bool = True) -> dict[str, Any]:
    """Gate a landed top-up and, if it passes, merge it into its pass.

    Order: structure checks, the parameter gate, the request gate, and the
    cumulative-meta guard; then the merged files are built in memory and
    verified; then the pass's three files are archived; then each is written
    atomically and verified again from disc. A refusal anywhere before the
    archive leaves the pass byte for byte as it was.

    Args:
        pass_dir: The pass to top up.
        topup_dir: The top-up's pass directory (``<out>/<config>/run_<n>``).
        manifest_tiles: The tiles the top-up sent.
        archive_dest: Folder for the pass's pre-top-up files.
        history_extra: Keys added to the ``recovery_history`` entry
            (``mode``, ``batch_job_name``, ...).
        request_file: The request JSONL the top-up sent.
        require_request_file: Refuse when the request file is absent (the
            live path); tests of the meta gate alone pass ``False``.

    Returns:
        A result dict: ``merged`` (bool), ``reason``, ``recovered``,
        ``still_failing``, ``features_added``, ``gate``, ``request_gate``,
        ``archived_to``, and the top-up's ``usage``, ``cost_estimate``, and
        ``retry_usage``.

    Raises:
        TopupError: The pass no longer lists exactly the manifest's tiles as
            failed, the top-up's structure is unsound, or the merged pass
            fails its structural verification.
    """
    pfiles = pass_files(pass_dir)
    tfiles = pass_files(topup_dir)
    pass_meta = read_json(pfiles["meta"])
    topup_meta = read_json(tfiles["meta"])
    pass_failed = scope_failed_tiles(pass_dir, None)
    if pass_failed != sorted(manifest_tiles):
        raise TopupError(f"{pass_dir}: the pass's failed tiles are not the manifest's")
    recovered, still_failing = topup_outcome(manifest_tiles, tfiles)

    result: dict[str, Any] = {
        "merged": False, "reason": None, "recovered": recovered,
        "still_failing": still_failing, "features_added": 0,
        "gate": parameter_gate(pass_meta, topup_meta),
        "request_gate": None, "archived_to": None,
        "usage": topup_meta.get("usage_stats"),
        "cost_estimate": topup_meta.get("cost_estimate"),
        "retry_usage": topup_meta.get("retry_usage"),
        "topup_run_id": topup_meta.get("run_id"),
    }
    if request_file is not None or require_request_file:
        result["request_gate"] = request_gate(request_file, manifest_tiles, pass_meta)
    if not result["gate"]["passed"]:
        result["reason"] = "parameter gate failed"
        return result
    if result["request_gate"] is not None and not result["request_gate"]["passed"]:
        result["reason"] = "request gate failed"
        return result
    try:
        refuse_cumulative(pass_meta, topup_meta)
    except SystemExit as exc:
        result["reason"] = f"cumulative-meta guard: {exc}"
        return result
    if not recovered:
        result["reason"] = "nothing recovered"
        return result

    # ── Build the merged pass in memory ───────────────────────────────
    pass_geo = read_json(pfiles["geojson"])
    topup_geo = read_json(tfiles["geojson"])
    if pass_geo.get("crs") != topup_geo.get("crs"):
        raise TopupError("the top-up GeoJSON's CRS differs from the pass's")
    pass_tiles = read_json(pfiles["tiles"])
    universe = set(pass_tiles.get("completed") or []) | set(pass_failed)
    if len(universe) != pass_tiles.get("total_tiles"):
        raise TopupError(f"{pass_dir}: completed + failed != total_tiles before the merge")
    if set(pass_geo.get("processed_tiles") or []) != set(pass_tiles.get("completed") or []):
        raise TopupError(f"{pass_dir}: processed_tiles != completed before the merge")
    already = {f["properties"].get("source_tile") for f in pass_geo.get("features") or []}
    if already & set(manifest_tiles):
        raise TopupError("the pass already holds features from a failed tile")
    new_features = list(topup_geo.get("features") or [])
    merged_geo = dict(pass_geo)
    merged_geo["features"] = list(pass_geo.get("features") or []) + new_features
    merged_geo["processed_tiles"] = sorted(
        set(pass_geo.get("processed_tiles") or []) | set(recovered))

    stamp = now_utc()
    merged_tiles = dict(pass_tiles)
    merged_tiles["completed"] = sorted(set(pass_tiles.get("completed") or []) | set(recovered))
    merged_tiles["failed"] = sorted(still_failing)
    # The keys patch_failed_tiles writes, so readers of either top-up agree.
    merged_tiles["patched"] = sorted(recovered)
    merged_tiles["patch_timestamp"] = stamp

    # The project's resume merge. "service_tier" is what merge_meta records
    # as the recovery's tier (patch_failed_tiles passes it the same way).
    fresh = copy.deepcopy(topup_meta)
    fresh["service_tier"] = "batch"
    merged_meta = merge_meta_into_existing(pfiles["meta"], fresh)
    # merge_meta keeps the original results_summary; patch_failed_tiles adds
    # the new detections so the count keeps matching the GeoJSON.
    summary = dict(merged_meta.get("results_summary") or {})
    summary["total_detections"] = (
        ((pass_meta.get("results_summary") or {}).get("total_detections") or 0)
        + ((topup_meta.get("results_summary") or {}).get("total_detections") or 0))
    merged_meta["results_summary"] = summary
    history = list(merged_meta.get("recovery_history") or [])
    if not history:
        raise TopupError("merge_meta wrote no recovery_history entry")
    history[-1] = {**history[-1], **history_extra, "tool": TOOL_NAME}
    merged_meta["recovery_history"] = history

    problems = verify_merged_pass(merged_geo, merged_tiles, merged_meta, universe)
    if problems:
        raise TopupError("merged pass (in memory): " + "; ".join(problems))

    # ── Archive first, then write ─────────────────────────────────────
    archive_files([pfiles["geojson"], pfiles["meta"], pfiles["tiles"]], archive_dest)
    write_json_atomic(pfiles["geojson"], merged_geo, indent=None)
    write_json_atomic(pfiles["tiles"], merged_tiles, indent=2)
    write_json_atomic(pfiles["meta"], merged_meta, indent=2)

    problems = verify_merged_pass(read_json(pfiles["geojson"]), read_json(pfiles["tiles"]),
                                  read_json(pfiles["meta"]), universe)
    if problems:
        raise TopupError("merged pass (on disc): " + "; ".join(problems))
    result.update({"merged": True, "reason": "merged", "features_added": len(new_features),
                   "archived_to": rel(archive_dest)})
    return result


# ─────────────────────────────────────────────────────────────────────
# Cost
# ─────────────────────────────────────────────────────────────────────


def _hours_between(start: str | None, end: str | None) -> float | None:
    """Hours from *start* to *end* (ISO strings), or ``None``."""
    if not start or not end:
        return None
    try:
        a = datetime.fromisoformat(str(start).replace("Z", "+00:00"))
        b = datetime.fromisoformat(str(end).replace("Z", "+00:00"))
    except ValueError:
        return None
    return max((b - a).total_seconds() / 3600.0, 0.0)


def topup_cost(cost_estimate: dict[str, Any] | None, retry_usage: list[dict[str, Any]] | None,
               cache: dict[str, Any] | None, model: str) -> dict[str, Any]:
    """The top-up's cost: batch tokens, in-batch retries, and its context cache.

    The batch tokens are the top-up meta's audited block. The retries'
    usage is priced at their own tier. The cache is an ESTIMATE (it reaches no
    meta): its tokens once at the standard input rate for creation, plus
    storage at the card's hourly rate from creation to deletion.

    Args:
        cost_estimate: The top-up meta's ``cost_estimate``.
        retry_usage: The top-up meta's ``retry_usage`` blocks.
        cache: The cache record from :func:`delete_cache`.
        model: The model the top-up recorded.

    Returns:
        ``{"batch_tokens_usd", "in_batch_retries_usd", "cache_estimate_usd",
        "total_usd"}``.
    """
    from scripts.lib_cost import price_usage, rates_for

    batch = (cost_estimate or {}).get("total_cost_usd") or 0.0
    retries = 0.0
    for block in retry_usage or []:
        usage = block.get("usage_stats") or {}
        if usage:
            retries += price_usage(usage, model, block.get("service_tier") or "standard",
                                   tier_source="topup retry_usage").get("total_cost_usd") or 0.0
    cache_usd = 0.0
    if cache and cache.get("tokens"):
        rates = rates_for(model, "standard")
        hours = _hours_between(cache.get("create_time"), cache.get("deleted_at")
                               or cache.get("expire_time"))
        cache_usd = cache["tokens"] / 1e6 * rates["input_fresh"]
        if hours is not None:
            cache_usd += cache["tokens"] / 1e6 * rates["cache_storage_per_1m_hour"] * hours
    return {"batch_tokens_usd": round(batch, 6), "in_batch_retries_usd": round(retries, 6),
            "cache_estimate_usd": round(cache_usd, 6),
            "total_usd": round(batch + retries + cache_usd, 6)}


def estimate_pass_cost(pass_meta: dict[str, Any], n_tiles: int) -> float:
    """A pre-launch estimate: the pass's own cost per tile, plus a cache margin."""
    cost = (pass_meta.get("cost_estimate") or {}).get("total_cost_usd") or 0.0
    done = (pass_meta.get("execution_stats") or {}).get("items_processed") or 1
    return cost / done * n_tiles + 0.10


# ─────────────────────────────────────────────────────────────────────
# Gemini side: caches and uploads
# ─────────────────────────────────────────────────────────────────────


def make_client() -> Any:
    """A ``google.genai`` client configured as the detector configures it."""
    from google import genai

    from config import GOOGLE_API_KEY

    return genai.Client(api_key=GOOGLE_API_KEY, http_options={"api_version": "v1alpha"})


def delete_cache(client: Any, name: str | None) -> dict[str, Any] | None:
    """Record and delete one context cache this top-up created.

    Called only after the detector process has exited, so its batch job is
    terminal (or was never submitted) and nothing can still read the cache.

    Args:
        client: A ``google.genai`` client, or ``None`` to skip.
        name: The cache resource name from the top-up's request file.

    Returns:
        ``{"name", "create_time", "expire_time", "tokens", "deleted_at"}``
        (with ``*_error`` keys on failure), or ``None`` without a name.
    """
    if not name or client is None:
        return None
    info: dict[str, Any] = {"name": name}
    try:
        cache = client.caches.get(name=name)
        info["create_time"] = str(getattr(cache, "create_time", None) or "") or None
        info["expire_time"] = str(getattr(cache, "expire_time", None) or "") or None
        um = getattr(cache, "usage_metadata", None)
        info["tokens"] = getattr(um, "total_token_count", None) if um else None
    except Exception as exc:  # noqa: BLE001 - recorded, deletion still tried
        info["get_error"] = f"{type(exc).__name__}: {exc}"
    try:
        client.caches.delete(name=name)
        info["deleted_at"] = now_utc()
    except Exception as exc:  # noqa: BLE001 - recorded for the report
        info["delete_error"] = f"{type(exc).__name__}: {exc}"
    return info


def job_state(client: Any, job_name: str) -> tuple[str, str | None]:
    """A batch job's state name and its request file."""
    from scripts.lib_batch_api import _get_state_name

    job = client.batches.get(name=job_name)
    src = getattr(job, "src", None)
    file_name = src if isinstance(src, str) else getattr(src, "file_name", None)
    return _get_state_name(getattr(job, "state", "")), file_name


# ─────────────────────────────────────────────────────────────────────
# The record
# ─────────────────────────────────────────────────────────────────────

_record_lock = threading.Lock()


def load_record(path: Path = RECORD_PATH) -> dict[str, Any]:
    """The top-up record, or a fresh one."""
    if path.exists():
        return read_json(path)
    return {
        "ruling": (f"{RULING}, PI-approved 2026-10-15 (Session 164): the wave-3 tiles that "
                   "failed as batch_api_error topped up in BATCH mode with each pass's own "
                   "command"),
        "tool": TOOL_NAME,
        "mode": "batch",
        "passes": {},
        "untouched": [],
        "invocations": [],
    }


def update_record(key: str, entry: dict[str, Any], path: Path = RECORD_PATH) -> dict[str, Any]:
    """Store one pass's result and recompute the totals (thread-safe).

    Returns:
        The record as written.
    """
    with _record_lock:
        record = load_record(path)
        record["passes"][key] = entry
        record["totals"] = record_totals(record)
        write_json_atomic(path, record, indent=1)
        return record


def record_totals(record: dict[str, Any]) -> dict[str, Any]:
    """Totals over the record's passes."""
    passes = record.get("passes", {}).values()
    return {
        "passes_topped_up": sum(1 for p in passes if p.get("merged")),
        "failed_before": sum(len(p.get("failed_before") or []) for p in passes),
        "recovered": sum(len(p.get("recovered") or []) for p in passes if p.get("merged")),
        "still_failing": sum(len(p.get("still_failing") or []) for p in passes
                             if p.get("merged")),
        "cost_usd": round(sum((p.get("cost_usd") or {}).get("total_usd") or 0.0
                              for p in passes), 6),
    }


# ─────────────────────────────────────────────────────────────────────
# One pass, end to end
# ─────────────────────────────────────────────────────────────────────


def process_pass(spec: PassSpec, failed: list[str], work_dir: Path, *,
                 run_command: Callable[[list[str], Path], int] = run_detector,
                 client: Any = None, python: str = sys.executable,
                 archive_dir: Path = ARCHIVE_DIR,
                 log_dir: Path | None = None,
                 full_manifest: Path = FULL_MANIFEST) -> dict[str, Any]:
    """Send one pass's failed tiles as a batch job and merge the result.

    Args:
        spec: The pass.
        failed: Its failed tiles (from :func:`scope_failed_tiles`).
        work_dir: Scratch root (outside ``outputs/``).
        run_command: Runs the detector; tests inject a fake.
        client: ``google.genai`` client for the cache deletion (``None``
            skips it).
        python: Interpreter for the detector.
        archive_dir: Archive root.
        log_dir: Where the detector log goes (default: the replication
            root, beside the wave logs).
        full_manifest: The manifest the pass was run on.

    Returns:
        The record entry for the pass.
    """
    started = now_utc()
    manifest = work_dir / "manifests" / f"{spec.corner}__run_{spec.run}.json"
    tiles = write_failed_manifest(failed, full_manifest, manifest)
    out_dir = work_dir / "runs" / spec.corner
    unit_dir = topup_unit_dir(spec, out_dir)
    if unit_dir.exists() and any(unit_dir.glob("*.geojson")):
        raise TopupError(f"{unit_dir} already holds top-up outputs; refusing to re-send")
    cmd = detector_command(spec, manifest, out_dir, python=python, dry_run=False)
    log_path = (log_dir or spec.base) / f"{spec.corner}.run_{spec.run}.{LOG_TAG}.log"
    logger.info("%s: sending %d tiles: %s", spec.key, len(tiles), " ".join(cmd))
    exit_code = run_command(cmd, log_path)
    log_info = parse_detector_log(log_path.read_text() if log_path.exists() else "")
    request_file = request_file_path(spec, out_dir)
    cache_name = None
    if request_file.exists():
        cache_name = read_request_file(request_file)["cached_content"]
        cache_name = cache_name[0] if cache_name else None
    cache = delete_cache(client, cache_name)
    logger.info("%s: detector exit %s; job %s; cache %s", spec.key, exit_code,
                log_info["batch_jobs"], cache)

    entry: dict[str, Any] = {
        "pass": pass_rel(spec),
        "started_utc": started, "finished_utc": None,
        "failed_before": tiles, "recovered": [], "still_failing": list(tiles),
        "command": cmd, "exit_code": exit_code, "log": rel(log_path),
        "log_failure_lines": log_info["failure_lines"],
        "batch_job": log_info["batch_jobs"][-1] if log_info["batch_jobs"] else None,
        "request_file": (log_info["request_files"][-1] if log_info["request_files"]
                         else None),
        "context_cache": cache, "merged": False, "reason": None,
    }
    raw_dest = archive_dir / RAW_ARCHIVE_SUBDIR / spec.archive_name
    if locate_pass_files(unit_dir) is None:
        entry["reason"] = "no top-up outputs (see the detector log)"
        entry["finished_utc"] = now_utc()
        return entry
    tfiles = pass_files(unit_dir)
    archive_files([manifest, tfiles["geojson"], tfiles["meta"], tfiles["tiles"]], raw_dest)
    entry["raw_outputs_archived_to"] = rel(raw_dest)

    history_extra = {
        "mode": "batch", "batch_job_name": entry["batch_job"],
        "request_file": entry["request_file"],
        "context_cache": cache_name, "ruling": RULING,
        "topup_outputs": rel(raw_dest),
    }
    try:
        result = merge_topup(spec.pass_dir, unit_dir, tiles,
                             archive_dir / spec.archive_name, history_extra,
                             request_file=request_file, require_request_file=True)
    except TopupError as exc:
        # Refused before any write: the pass is untouched, but the top-up's
        # spend is still recorded.
        topup_meta = read_json(tfiles["meta"])
        entry.update({
            "reason": f"refused: {exc}", "usage": topup_meta.get("usage_stats"),
            "cost_usd": topup_cost(topup_meta.get("cost_estimate"),
                                   topup_meta.get("retry_usage"), cache,
                                   (topup_meta.get("configuration") or {}).get("model")
                                   or "gemini-3.1-pro-preview"),
            "finished_utc": now_utc()})
        return entry
    model = ((read_json(tfiles["meta"]).get("configuration") or {}).get("model")
             or "gemini-3.1-pro-preview")
    entry.update({
        "merged": result["merged"], "reason": result["reason"],
        "recovered": result["recovered"], "still_failing": result["still_failing"],
        "features_added": result["features_added"], "gate": result["gate"],
        "request_gate": result["request_gate"], "archived_to": result["archived_to"],
        "topup_run_id": result["topup_run_id"], "usage": result["usage"],
        "retry_usage": result["retry_usage"],
        "cost_usd": topup_cost(result["cost_estimate"], result["retry_usage"], cache, model),
        "finished_utc": now_utc(),
    })
    return entry


# ─────────────────────────────────────────────────────────────────────
# Planning, dry run, live run, release
# ─────────────────────────────────────────────────────────────────────


def plan(specs: list[PassSpec], approved: dict[str, int],
         only: list[str] | None = None) -> tuple[list[tuple[PassSpec, list[str]]], list[str]]:
    """Which passes to top up, after the scope gate.

    Args:
        specs: Candidate passes.
        approved: Approved failed-tile count per pass key.
        only: Restrict to these pass keys.

    Returns:
        ``(todo, untouched)``: ``todo`` pairs a pass with its failed tiles;
        ``untouched`` names passes with no failed tiles or already topped up
        by this tool.

    Raises:
        TopupError: Any pass fails the scope gate (nothing is sent at all).
    """
    todo: list[tuple[PassSpec, list[str]]] = []
    untouched: list[str] = []
    for spec in specs:
        if only and spec.key not in only:
            continue
        meta = read_json(pass_files(spec.pass_dir)["meta"])
        if already_topped_up(meta):
            failed = scope_failed_tiles(spec.pass_dir, None)
            untouched.append(f"{spec.key} (already topped up; {len(failed)} still failing)")
            continue
        failed = scope_failed_tiles(spec.pass_dir, approved.get(spec.key))
        if not failed:
            untouched.append(f"{spec.key} (no failed tiles)")
            continue
        todo.append((spec, failed))
    return todo, untouched


def dry_run(todo: list[tuple[PassSpec, list[str]]], work_dir: Path,
            detector_dry_run: bool) -> int:
    """Write manifests, print commands, and (optionally) run detector dry runs.

    Returns:
        0 when every detector dry run exited 0 (or none ran), else 1.
    """
    status = 0
    for spec, failed in todo:
        manifest = work_dir / "dry-run" / "manifests" / f"{spec.corner}__run_{spec.run}.json"
        tiles = write_failed_manifest(failed, FULL_MANIFEST, manifest)
        out_dir = work_dir / "dry-run" / "runs" / spec.corner
        cmd = detector_command(spec, manifest, out_dir, python=sys.executable,
                               dry_run=detector_dry_run)
        print(f"\n{spec.key}: {len(tiles)} tiles -> {manifest}")
        print("  " + " ".join(cmd))
        if detector_dry_run:
            log_path = work_dir / "dry-run" / "logs" / f"{spec.corner}.run_{spec.run}.log"
            code = run_detector(cmd, log_path)
            info = parse_detector_log(log_path.read_text())
            print(f"  detector --dry-run exit {code}; log {log_path}")
            for line in info["failure_lines"]:
                print(f"    ! {line}")
            if code != 0:
                status = 1
    return status


def live_run(todo: list[tuple[PassSpec, list[str]]], work_dir: Path, max_parallel: int,
             cost_cap: float) -> int:
    """Run the top-ups, at most *max_parallel* detector processes at once.

    A pass is not launched once a gate has failed, or when the record's cost
    so far plus the pass's estimate would pass *cost_cap*.

    Returns:
        0 when every launched pass merged, else 1.
    """
    client = make_client()
    stop = threading.Event()
    lock = threading.Lock()
    in_flight: dict[str, float] = {}

    def one(spec: PassSpec, failed: list[str]) -> dict[str, Any]:
        with lock:
            spent = (load_record().get("totals") or {}).get("cost_usd") or 0.0
            estimate = estimate_pass_cost(read_json(pass_files(spec.pass_dir)["meta"]),
                                          len(failed))
            if stop.is_set():
                return {"key": spec.key, "skipped": "stopped after a failure or the cap"}
            if spent + sum(in_flight.values()) + estimate > cost_cap:
                stop.set()
                return {"key": spec.key,
                        "skipped": (f"cost cap: spent {spent:.4f} + in flight "
                                    f"{sum(in_flight.values()):.4f} + estimate {estimate:.4f}")}
            in_flight[spec.key] = estimate
        try:
            entry = process_pass(spec, failed, work_dir, client=client)
        except TopupError as exc:
            entry = {"pass": pass_rel(spec), "merged": False, "reason": f"refused: {exc}",
                     "failed_before": failed}
        finally:
            with lock:
                in_flight.pop(spec.key, None)
        record = update_record(spec.key, entry)
        cost = (entry.get("cost_usd") or {}).get("total_usd")
        logger.info("%s: merged=%s reason=%s recovered=%d still_failing=%d cost=%s",
                    spec.key, entry.get("merged"), entry.get("reason"),
                    len(entry.get("recovered") or []), len(entry.get("still_failing") or []),
                    cost)
        # A gate failure, a refusal, or a run without outputs stops further
        # launches; a pass whose tiles all failed again does not.
        if ((not entry.get("merged") and entry.get("reason") != "nothing recovered")
                or record["totals"]["cost_usd"] > cost_cap):
            stop.set()
        return {"key": spec.key, **entry}

    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel) as pool:
        futures = [pool.submit(one, spec, failed) for spec, failed in todo]
        for fut in concurrent.futures.as_completed(futures):
            results.append(fut.result())
    for res in sorted(results, key=lambda r: r["key"]):
        if "skipped" in res:
            logger.warning("%s: NOT LAUNCHED (%s)", res["key"], res["skipped"])
    return 0 if all(r.get("merged") for r in results) else 1


def committed(paths: list[Path]) -> bool:
    """Whether every path is tracked and unchanged against HEAD."""
    for path in paths:
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", str(path)],
                                 cwd=REPO_ROOT, capture_output=True, check=False)
        clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", str(path)],
                               cwd=REPO_ROOT, check=False)
        if tracked.returncode != 0 or clean.returncode != 0:
            return False
    return True


def release_uploads(record_path: Path = RECORD_PATH) -> int:
    """Delete the top-up request uploads once the outputs are committed.

    A file is deleted only when the record and the merged pass files are
    committed, its batch job is terminal, and no non-terminal batch job on
    the project names it as its source.

    Returns:
        0 when every upload was released (or none remained), else 1.
    """
    from scripts.lib_batch_api import (
        _TERMINAL_STATES,
        active_batch_input_files,
        cleanup_batch_files,
    )

    record = load_record(record_path)
    to_check = [record_path] + [
        p for key in record["passes"] for p in pass_files(
            BASE / record["passes"][key]["pass"]).values()]
    if not committed(to_check):
        logger.error("record or pass files not committed; nothing released")
        return 1
    client = make_client()
    active = active_batch_input_files(client)
    status = 0
    for key, entry in record["passes"].items():
        if entry.get("upload_released") or not entry.get("batch_job"):
            continue
        state, src = job_state(client, entry["batch_job"])
        name = entry.get("request_file") or src
        if state not in _TERMINAL_STATES or not name or name in active:
            logger.warning("%s: %s not released (job %s, in use %s)", key, name, state,
                           name in active)
            status = 1
            continue
        deleted, errors = cleanup_batch_files(client, [name], label="topup-input")
        entry["upload_released"] = {"file": name, "job_state": state, "deleted": deleted == 1,
                                    "errors": errors, "at": now_utc()}
        logger.info("%s: released %s (deleted %d, errors %d)", key, name, deleted, errors)
        if deleted != 1:
            status = 1
        update_record(key, entry, record_path)
    return status


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--work-dir", type=Path, required=True,
                        help="scratch root for manifests and top-up outputs (outside outputs/)")
    parser.add_argument("--live", action="store_true",
                        help="send the batch jobs and merge (default: dry run)")
    parser.add_argument("--only", action="append", default=None,
                        help="pass key to include, e.g. image-high-t0.0/run_5 (repeatable)")
    parser.add_argument("--max-parallel", type=int, default=2,
                        help="detector processes at once in a live run (default 2)")
    parser.add_argument("--cost-cap", type=float, default=COST_CAP_USD,
                        help=f"stop launching above this cumulative US$ (default {COST_CAP_USD})")
    parser.add_argument("--no-detector-dry-run", action="store_true",
                        help="dry run without the detector's own --dry-run")
    parser.add_argument("--release-uploads", action="store_true",
                        help="delete the committed top-up's request uploads, then exit")
    args = parser.parse_args()

    work_dir = args.work_dir.expanduser().resolve()
    if work_dir.is_relative_to(REPO_ROOT / "outputs"):
        parser.error("--work-dir must be outside outputs/ (its metas would be counted twice)")
    work_dir.mkdir(parents=True, exist_ok=True)
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if args.live or args.release_uploads:
        handlers.append(logging.FileHandler(TOOL_LOG))
    logging.basicConfig(level=logging.INFO, handlers=handlers,
                        format="%(asctime)s %(levelname)s %(message)s")

    if args.release_uploads:
        return release_uploads()

    try:
        todo, untouched = plan(wave3_specs(), APPROVED_FAILED, args.only)
    except TopupError as exc:
        logger.error("scope gate: %s; nothing sent", exc)
        return 1
    print(f"{len(todo)} pass(es) to top up, {sum(len(f) for _, f in todo)} tiles; "
          f"live={args.live}")
    for spec, failed in todo:
        print(f"  {spec.key}: {len(failed)}")
    for line in untouched:
        print(f"  untouched: {line}")
    if not args.live:
        return dry_run(todo, work_dir, detector_dry_run=not args.no_detector_dry_run)

    pid_file = work_dir / "topup.pid"
    pid_file.write_text(f"{os.getpid()}\n")
    try:
        with _record_lock:
            record = load_record()
            record["untouched"] = sorted(set(record.get("untouched") or [])
                                         | {u.split(" ")[0] for u in untouched
                                            if "no failed tiles" in u})
            record.setdefault("invocations", []).append(
                {"started_utc": now_utc(), "passes": [s.key for s, _ in todo],
                 "max_parallel": args.max_parallel, "cost_cap_usd": args.cost_cap})
            write_json_atomic(RECORD_PATH, record, indent=1)
        status = live_run(todo, work_dir, args.max_parallel, args.cost_cap)
        totals = load_record().get("totals")
        logger.info("TOPUP %s: totals %s", "COMPLETE" if status == 0 else "STOPPED", totals)
        return status
    finally:
        pid_file.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
