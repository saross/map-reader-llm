#!/usr/bin/env python3
"""
Generalisation-Run Pipeline Orchestrator
========================================

End-to-end publishable launcher for a single map-reader-llm generalisation
run. Orchestrates the preregistered four-stage pipeline
(proposer → consensus → verifier → evaluation) with comprehensive
reproducibility metadata and cost tracking.

Published alongside the paper as part of the reproducibility kit. The
headline paper run is invoked as a single command::

    python scripts/run_generalisation.py all \\
        --run-config configs/run-configs/55maps_image_generalisation.yaml \\
        --run-name 55maps-image-generalisation

Subcommands
-----------
- ``proposer`` — run K proposer passes via ``4_detect_mounds_batch.py``
- ``consensus`` — merge per-pass detections at a vote threshold via ``merge_passes.py``
- ``extract`` — crop candidate images via ``run_pv.py extract``
- ``verify`` — score candidates via ``run_pv.py verify``
- ``evaluate`` — compute F1 at multiple buffers via ``evaluate_detections.py``
- ``aggregate-cost`` — (re)build ``cost_manifest.json`` by scanning meta files
- ``all`` — run every stage in order (default)

Design
------
- YAML run-configs (e.g., ``configs/run-configs/<run>.yaml``) capture the
  full parameter set for a study. CLI flags override individual fields.
- Each subcommand is a thin orchestrator that invokes the corresponding
  existing pipeline script via ``subprocess.run`` — no pipeline logic is
  duplicated here.
- Reproducibility: git commit SHA, input-file SHA256s, and the resolved
  configuration are recorded to ``launch_manifest.json`` at startup.
- Cost tracking: per-run ``*.meta.json`` outputs are aggregated into a
  single ``cost_manifest.json`` covering totals, stage breakdowns,
  per-map cost, and unit-cost metrics.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import dataclasses
import getpass
import hashlib
import json
import logging
import os
import platform
import re
import shlex
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - dev setup guard
    raise SystemExit(
        "PyYAML is required. Install with: pip install pyyaml"
    ) from exc

__version__ = "1.0.0"

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_ROOT = BASE_DIR / "outputs"
DEFAULT_SEED = 42

# Script dispatch targets (absolute paths so subprocess.cwd stays at repo root)
PROPOSER_SCRIPT = BASE_DIR / "scripts" / "4_detect_mounds_batch.py"
MERGE_SCRIPT = BASE_DIR / "scripts" / "merge_passes.py"
RUN_PV_SCRIPT = BASE_DIR / "scripts" / "run_pv.py"
EVAL_SCRIPT = BASE_DIR / "scripts" / "evaluate_detections.py"

# Python interpreter used for subprocess dispatch. Inherits the calling
# interpreter so users get the same venv automatically.
PYTHON = sys.executable

# Required top-level YAML keys for a run-config. Validated on load.
REQUIRED_YAML_KEYS: tuple[str, ...] = (
    "run_name",
    "proposer",
    "consensus",
    "extract",
    "verify",
    "evaluate",
)

# Buffer values that must appear in the evaluation stage for publishable
# results. Listed here for a defensive sanity check; the launcher does
# not enforce them (CLI / YAML retains full control) but logs a warning
# if any are missing.
RECOMMENDED_BUFFERS: tuple[int, ...] = (20, 30, 40, 50)

# Proposer exit codes (from 4_detect_mounds_batch.py):
#   0 = success
#   1 = setup error (abort immediately)
#   2 = partial tile failure (log and continue)
# Anything else = unexpected; log and continue, but record in manifest.
PROPOSER_PARTIAL_EXIT = 2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclasses.dataclass
class StageTiming:
    """Wall-clock timing for a single pipeline stage."""

    started_at: str
    completed_at: str
    duration_seconds: float


@dataclasses.dataclass
class ResolvedRunConfig:
    """Fully resolved run configuration (YAML + CLI merged)."""

    run_name: str
    output_dir: Path
    proposer: dict[str, Any]
    consensus: dict[str, Any]
    extract: dict[str, Any]
    verify: dict[str, Any]
    evaluate: dict[str, Any]
    global_opts: dict[str, Any]


# ---------------------------------------------------------------------------
# Config loading / merging
# ---------------------------------------------------------------------------
def load_yaml_config(path: Path) -> dict[str, Any]:
    """Load a YAML run-config file and validate top-level keys.

    Args:
        path: Path to the YAML file.

    Returns:
        Loaded config dict.

    Raises:
        SystemExit: If the file is missing or top-level keys are absent.
    """
    if not path.is_file():
        raise SystemExit(f"Run-config not found: {path}")

    with path.open(encoding="utf-8") as fh:
        config = yaml.safe_load(fh)
    if not isinstance(config, dict):
        raise SystemExit(
            f"Run-config must be a YAML mapping at the top level: {path}"
        )

    missing = [k for k in REQUIRED_YAML_KEYS if k not in config]
    if missing:
        raise SystemExit(
            f"Run-config {path} is missing required top-level keys: "
            f"{', '.join(missing)}"
        )
    return config


def merge_cli_overrides(
    config: dict[str, Any], cli: argparse.Namespace,
) -> dict[str, Any]:
    """Apply CLI overrides on top of a YAML config.

    CLI flags that are None are treated as "not provided" and do not
    override. Flags that appear on subcommands map to the corresponding
    stage section. A small number of global flags override top-level
    keys (``run_name``, ``output_root``).

    Args:
        config: Loaded YAML config (modified in place).
        cli: Parsed CLI namespace.

    Returns:
        The merged config dict (same object as input).
    """
    # Flag → (section, key) mapping. Each entry names a CLI attribute
    # and where it lands in the config dict. None values are skipped
    # so unspecified flags do not clobber YAML values.
    section_overrides: dict[str, tuple[str, str]] = {
        # proposer
        "proposer_config": ("proposer", "config"),
        "tiles_dir": ("proposer", "tiles_dir"),
        "manifest": ("proposer", "manifest"),
        "tile_size": ("proposer", "tile_size"),
        "temperature": ("proposer", "temperature"),
        "thinking_level": ("proposer", "thinking_level"),
        "passes": ("proposer", "passes"),
        "proposer_workers": ("proposer", "workers"),
        "max_retries": ("proposer", "max_retries"),
        # consensus
        "vote_threshold": ("consensus", "vote_threshold"),
        "dedup_radius_m": ("consensus", "dedup_radius_m"),
        # extract
        "padding": ("extract", "padding"),
        "rasters_dir": ("extract", "rasters_dir"),
        # verify
        "verifier_config": ("verify", "config"),
        "verify_mode": ("verify", "mode"),
        "verify_workers": ("verify", "workers"),
        # evaluate
        "prob_threshold": ("evaluate", "prob_threshold"),
        "buffers": ("evaluate", "buffers"),
        "bootstrap": ("evaluate", "bootstrap"),
        "seed": ("evaluate", "seed"),
        "ground_truth": ("evaluate", "ground_truth"),
        "bounds": ("evaluate", "bounds"),
    }
    for cli_attr, (section, key) in section_overrides.items():
        val = getattr(cli, cli_attr, None)
        if val is not None:
            config.setdefault(section, {})[key] = val

    # Global overrides
    if getattr(cli, "run_name", None) is not None:
        config["run_name"] = cli.run_name
    if getattr(cli, "output_root", None) is not None:
        config["output_root"] = str(cli.output_root)

    # service_tier can live at the top level (convenience) or per-stage.
    # Precedence: CLI > per-stage YAML > top-level YAML > default (flex).
    cli_tier = getattr(cli, "service_tier", None)
    top_tier = config.get("service_tier")
    for section in ("proposer", "verify"):
        config.setdefault(section, {})
        if cli_tier is not None:
            # CLI wins over any YAML value
            config[section]["service_tier"] = cli_tier
        elif "service_tier" not in config[section] and top_tier is not None:
            # No per-stage value; fall back to top-level
            config[section]["service_tier"] = top_tier
    return config


def resolve_run_config(
    config: dict[str, Any], cli: argparse.Namespace,
) -> ResolvedRunConfig:
    """Materialise a ResolvedRunConfig from a merged config dict.

    Raises on missing required fields so the launcher fails fast before
    spending any API budget.
    """
    run_name = config["run_name"]
    output_root = Path(config.get("output_root", DEFAULT_OUTPUT_ROOT))
    output_dir = output_root / run_name

    # Validate required per-stage fields; surface clear error messages.
    required: dict[str, tuple[str, ...]] = {
        "proposer": ("config", "manifest", "tiles_dir", "temperature",
                     "thinking_level", "passes"),
        "consensus": ("vote_threshold",),
        "extract": ("padding", "rasters_dir"),
        "verify": ("config",),
        "evaluate": ("prob_threshold", "buffers", "ground_truth", "bounds"),
    }
    missing: list[str] = []
    for section, keys in required.items():
        section_cfg = config.get(section, {})
        for k in keys:
            if section_cfg.get(k) in (None, ""):
                missing.append(f"{section}.{k}")
    if missing:
        raise SystemExit(
            "Resolved config is missing required fields: "
            + ", ".join(missing)
        )

    return ResolvedRunConfig(
        run_name=run_name,
        output_dir=output_dir,
        proposer=dict(config["proposer"]),
        consensus=dict(config["consensus"]),
        extract=dict(config["extract"]),
        verify=dict(config["verify"]),
        evaluate=dict(config["evaluate"]),
        global_opts={
            "output_root": str(output_root),
            "service_tier": config.get("proposer", {}).get(
                "service_tier", "flex",
            ),
        },
    )


# ---------------------------------------------------------------------------
# Reproducibility helpers
# ---------------------------------------------------------------------------
def sha256_file(path: Path) -> str:
    """Return the hex SHA256 of a file, or ``"(missing)"`` if absent."""
    if not path.is_file():
        return "(missing)"
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_directory_listing(directory: Path) -> str:
    """Return SHA256 of a sorted directory listing.

    Used as a cheap fingerprint for raster directories (SHAing 2.4 GB
    of rasters is overkill; the listing changes whenever files are
    added / removed / renamed, which is what we actually care about).
    """
    if not directory.is_dir():
        return "(missing)"
    listing = "\n".join(
        sorted(p.name for p in directory.iterdir() if p.is_file())
    )
    return hashlib.sha256(listing.encode("utf-8")).hexdigest()


def git_status() -> dict[str, Any]:
    """Return git commit SHA, branch, and dirty flag for the repo.

    "Dirty" counts only modifications to tracked files, not untracked
    paths. Running the launcher against a pristine clone always produces
    a fresh ``outputs/<run-name>/`` directory that is not yet under
    version control; flagging that as dirty would block every launch.
    Untracked-file status is still captured in ``untracked_files`` for
    audit purposes but does not feed the abort decision.
    """
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=BASE_DIR, capture_output=True, text=True, check=True,
        ).stdout.strip()
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=BASE_DIR, capture_output=True, text=True, check=True,
        ).stdout.strip()
        # --porcelain --untracked-files=no reports only modifications
        # to tracked files (what we care about for reproducibility).
        porcelain_tracked = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=BASE_DIR, capture_output=True, text=True, check=True,
        ).stdout
        # Capture untracked count separately for the manifest record.
        porcelain_all = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=BASE_DIR, capture_output=True, text=True, check=True,
        ).stdout
        untracked = [
            ln[3:] for ln in porcelain_all.splitlines()
            if ln.startswith("?? ")
        ]
        return {
            "commit_sha": commit,
            "branch": branch,
            "dirty": bool(porcelain_tracked.strip()),
            "untracked_file_count": len(untracked),
        }
    except subprocess.CalledProcessError:
        return {
            "commit_sha": "(unknown)", "branch": "(unknown)",
            "dirty": False, "untracked_file_count": 0,
        }
    except FileNotFoundError:
        return {
            "commit_sha": "(unknown)", "branch": "(unknown)",
            "dirty": False, "untracked_file_count": 0,
        }


def now_iso() -> str:
    """Return the current UTC time in ISO 8601 with trailing Z."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def monotonic_seconds_since(start: float) -> float:
    """Return elapsed monotonic seconds since ``start``, rounded."""
    return round(time.monotonic() - start, 3)


# ---------------------------------------------------------------------------
# Tile → map attribution
# ---------------------------------------------------------------------------
# Tile names follow ``<map_id>_x<col>_y<row>.png``. The map_id may itself
# contain underscores (e.g., ``K-35-052-4_32635``). We split on the last
# ``_x`` that is followed by digits to locate the coordinate suffix.
_TILE_COORD_RE = re.compile(r"^(.*)_x\d+_y\d+\.png$")


def tile_to_map(tile_name: str) -> str:
    """Return the map identifier for a tile filename.

    Example: ``K-35-042-3_x336_y672.png`` → ``K-35-042-3``;
             ``K-35-052-4_32635_x0_y0.png`` → ``K-35-052-4_32635``.
    """
    match = _TILE_COORD_RE.match(tile_name)
    if match:
        return match.group(1)
    # Fall back to the literal name if it doesn't match (rare; better
    # than an exception that could kill cost aggregation).
    return tile_name


# ---------------------------------------------------------------------------
# Stage runners — thin subprocess wrappers around existing scripts
# ---------------------------------------------------------------------------
def _run_subprocess(
    cmd: list[str],
    *,
    log_path: Path,
    allowed_exits: tuple[int, ...] = (0,),
) -> int:
    """Run ``cmd``, tee stdout+stderr to ``log_path``, return exit code.

    Raises CalledProcessError-style SystemExit on unexpected exits so
    the pipeline fails fast. Exit codes in ``allowed_exits`` are
    returned without raising.
    """
    logger.info("Running: %s", " ".join(shlex.quote(c) for c in cmd))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log_fh:
        log_fh.write(f"\n\n==== {now_iso()} ====\n")
        log_fh.write("$ " + " ".join(shlex.quote(c) for c in cmd) + "\n")
        log_fh.flush()
        # Inherit environment; subprocess handles its own API key, logging
        proc = subprocess.run(
            cmd, cwd=BASE_DIR, stdout=log_fh, stderr=subprocess.STDOUT,
            check=False,
        )
    rc = proc.returncode
    logger.info("Exit code: %d  (log: %s)", rc, log_path)
    if rc not in allowed_exits:
        raise SystemExit(
            f"Stage aborted: command exited with code {rc} "
            f"(expected one of {allowed_exits}). See log: {log_path}"
        )
    return rc


def run_proposer(
    rcfg: ResolvedRunConfig, *, limit: int | None, skip_intent: bool,
) -> dict[str, Any]:
    """Run K proposer passes. Returns a summary dict (per-pass records)."""
    p = rcfg.proposer
    k = int(p["passes"])
    output_base = rcfg.output_dir / "proposer" / Path(p["config"]).stem
    output_base.mkdir(parents=True, exist_ok=True)

    per_pass: list[dict[str, Any]] = []
    stage_start = time.monotonic()
    failed_passes = 0
    for i in range(1, k + 1):
        run_dir = output_base / f"run_{i}"
        if run_dir.is_dir() and list(run_dir.glob("*.geojson")):
            logger.info(
                "Proposer run %d/%d already has outputs; skipping. "
                "Remove %s to force re-run.", i, k, run_dir,
            )
            per_pass.append({
                "pass": i, "status": "skipped-existing",
                "output_dir": str(run_dir),
            })
            continue
        cmd = [
            PYTHON, str(PROPOSER_SCRIPT),
            "--config", p["config"],
            "--manifest", p["manifest"],
            "--tiles-dir", p["tiles_dir"],
            "--output-dir", str(run_dir),
            "--temperature", str(p["temperature"]),
            "--thinking-level", p["thinking_level"],
            "--mode", p.get("mode", "realtime"),
            "--service-tier", p.get("service_tier", "flex"),
            "--workers", str(p.get("workers", 60)),
        ]
        if p.get("tile_size"):
            cmd += ["--tile-size", str(p["tile_size"])]
        if p.get("max_retries") is not None:
            cmd += ["--max-retries", str(p["max_retries"])]
        if p.get("use_cache", True):
            cmd += ["--use-cache"]
        if skip_intent:
            cmd += ["--skip-intent-check"]
        if limit is not None:
            cmd += ["--limit", str(limit)]

        pass_start = time.monotonic()
        rc = _run_subprocess(
            cmd,
            log_path=rcfg.output_dir / "run.log",
            allowed_exits=(0, PROPOSER_PARTIAL_EXIT),
        )
        pass_duration = monotonic_seconds_since(pass_start)
        per_pass.append({
            "pass": i, "status": "partial" if rc == PROPOSER_PARTIAL_EXIT else "ok",
            "exit_code": rc, "duration_seconds": pass_duration,
            "output_dir": str(run_dir),
        })
        if rc == PROPOSER_PARTIAL_EXIT:
            failed_passes += 1

    if failed_passes >= 3:
        raise SystemExit(
            f"Proposer stage aborted: {failed_passes}/{k} passes had "
            f"partial failures (threshold=3 per scripts/55maps-overnight.sh)."
        )
    return {
        "output_base": str(output_base),
        "passes": k,
        "per_pass": per_pass,
        "stage_duration_seconds": monotonic_seconds_since(stage_start),
    }


def run_consensus(rcfg: ResolvedRunConfig) -> dict[str, Any]:
    """Merge per-pass detections at the configured vote threshold."""
    p = rcfg.proposer
    c = rcfg.consensus
    proposer_output = rcfg.output_dir / "proposer" / Path(p["config"]).stem
    consensus_dir = rcfg.output_dir / "consensus"
    consensus_dir.mkdir(parents=True, exist_ok=True)

    k = int(p["passes"])
    vote_t = int(c["vote_threshold"])
    consensus_file = consensus_dir / f"consensus-{vote_t}of{k}.geojson"

    cmd = [
        PYTHON, str(MERGE_SCRIPT),
        "--input-dir", str(proposer_output),
        "--output", str(consensus_file),
        "--threshold", str(vote_t),
    ]
    start = time.monotonic()
    _run_subprocess(cmd, log_path=rcfg.output_dir / "run.log")
    duration = monotonic_seconds_since(start)

    # Record a small metadata file summarising the consensus parameters
    meta = {
        "vote_threshold": vote_t,
        "total_passes": k,
        "dedup_radius_m": c.get("dedup_radius_m", 20.0),
        "consensus_file": consensus_file.name,
        "stage_duration_seconds": duration,
    }
    (consensus_dir / "consensus_meta.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8",
    )
    return {
        "consensus_file": str(consensus_file),
        "stage_duration_seconds": duration,
    }


def run_extract(rcfg: ResolvedRunConfig) -> dict[str, Any]:
    """Extract candidate crops from the consensus GeoJSON."""
    p = rcfg.proposer
    c = rcfg.consensus
    e = rcfg.extract
    k = int(p["passes"])
    vote_t = int(c["vote_threshold"])

    consensus_file = (
        rcfg.output_dir / "consensus"
        / f"consensus-{vote_t}of{k}.geojson"
    )
    crops_dir = rcfg.output_dir / "crops"

    cmd = [
        PYTHON, str(RUN_PV_SCRIPT), "extract",
        "--proposer", str(consensus_file),
        "--output-dir", str(crops_dir),
        "--padding", str(e["padding"]),
        "--rasters-dir", e["rasters_dir"],
    ]
    if e.get("tiles_dir"):
        cmd += ["--tiles-dir", e["tiles_dir"]]
    start = time.monotonic()
    _run_subprocess(cmd, log_path=rcfg.output_dir / "run.log")
    return {
        "crops_dir": str(crops_dir),
        "stage_duration_seconds": monotonic_seconds_since(start),
    }


def run_verify(rcfg: ResolvedRunConfig) -> dict[str, Any]:
    """Score candidates via the adversarial verifier."""
    v = rcfg.verify
    crops_dir = rcfg.output_dir / "crops"
    verified_dir = rcfg.output_dir / "verified"

    cmd = [
        PYTHON, str(RUN_PV_SCRIPT), "verify",
        "--crops-dir", str(crops_dir),
        "--verifier-config", v["config"],
        "--output-dir", str(verified_dir),
        "--mode", v.get("mode", "realtime"),
        "--workers", str(v.get("workers", 20)),
        "--service-tier", v.get("service_tier", "flex"),
    ]
    start = time.monotonic()
    _run_subprocess(cmd, log_path=rcfg.output_dir / "run.log")
    return {
        "verified_dir": str(verified_dir),
        "stage_duration_seconds": monotonic_seconds_since(start),
    }


def run_evaluate(rcfg: ResolvedRunConfig) -> dict[str, Any]:
    """Build the final (vote + prob) filtered GeoJSON and evaluate it.

    Produces ``verified/verified_detections.geojson`` and per-buffer
    metrics under ``evaluation/``.
    """
    ev = rcfg.evaluate
    verified_dir = rcfg.output_dir / "verified"
    crops_dir = rcfg.output_dir / "crops"
    eval_dir = rcfg.output_dir / "evaluation"
    eval_dir.mkdir(parents=True, exist_ok=True)

    # Build the final detection GeoJSON locally (no subprocess) so we
    # don't need to replicate all the sweep logic of sweep_f1_greedy_pv.
    final_geojson = _build_verified_geojson(
        crops_dir=crops_dir,
        verified_dir=verified_dir,
        vote_threshold=int(rcfg.consensus["vote_threshold"]),
        prob_threshold=float(ev["prob_threshold"]),
        output=verified_dir / "verified_detections.geojson",
    )

    # Call evaluate_detections.py with multiple buffers in one go.
    # The script writes per-file outputs in the output_dir.
    cmd = [
        PYTHON, str(EVAL_SCRIPT),
        "--detections", str(final_geojson),
        "--buffers", *[str(b) for b in ev["buffers"]],
        "--bootstrap", str(ev.get("bootstrap", 1000)),
        "--seed", str(ev.get("seed", DEFAULT_SEED)),
        "--ground-truth", ev["ground_truth"],
        "--bounds", ev["bounds"],
        "--output-dir", str(eval_dir),
        "--label", rcfg.run_name,
    ]
    start = time.monotonic()
    _run_subprocess(cmd, log_path=rcfg.output_dir / "run.log")
    return {
        "eval_dir": str(eval_dir),
        "final_geojson": str(final_geojson),
        "stage_duration_seconds": monotonic_seconds_since(start),
    }


def _build_verified_geojson(
    *,
    crops_dir: Path,
    verified_dir: Path,
    vote_threshold: int,
    prob_threshold: float,
    output: Path,
) -> Path:
    """Compose the final (vote + prob)-filtered detection GeoJSON.

    The verifier produces probabilities keyed by crop/candidate id; the
    candidate manifest maps candidate_id back to a spatial centroid and
    vote count. We filter candidates that pass BOTH thresholds and emit
    a GeoJSON in the same UTM CRS (EPSG:32635) the pipeline uses.
    """
    manifest = json.loads(
        (crops_dir / "candidate_manifest.json").read_text(encoding="utf-8"),
    )
    probs = json.loads(
        (verified_dir / "probabilities.json").read_text(encoding="utf-8"),
    )
    results = probs.get("results", {})

    features: list[dict[str, Any]] = []
    for cand in manifest.get("candidates", []):
        cid = cand["candidate_id"]
        vote = cand.get("properties", {}).get("vote_count", 0)
        key = f"candidate_{cid:05d}"
        entry = results.get(key)
        if entry is None:
            continue
        prob = entry.get("mound_probability")
        if prob is None:
            continue
        if vote < vote_threshold or prob < prob_threshold:
            continue
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [cand["centroid_x"], cand["centroid_y"]],
            },
            "properties": {
                "candidate_id": cid,
                "vote_count": vote,
                "probability": prob,
                "source_tile": cand.get("source_tile"),
            },
        })

    gj = {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {"name": "EPSG:32635"},
        },
        "features": features,
    }
    output.write_text(json.dumps(gj, indent=2), encoding="utf-8")
    logger.info(
        "Wrote %d verified detections to %s "
        "(vote_t=%d, prob_t=%.3f)",
        len(features), output, vote_threshold, prob_threshold,
    )
    return output


# ---------------------------------------------------------------------------
# Cost manifest aggregation
# ---------------------------------------------------------------------------
def _read_meta(path: Path) -> dict[str, Any]:
    """Read a *.meta.json or run.meta.json file; return empty dict on miss."""
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        logger.warning("Could not parse meta file: %s", path)
        return {}


# Mapping from our token-bucket keys to the actual field names in
# usage_stats (as written by lib_llm_metadata.AggregatedUsage). Gemini
# thinking tokens are stored as ``total_thoughts_tokens`` (not
# ``total_thinking_tokens``) and the aggregate total is ``total_tokens``
# (not ``total_total_tokens``); expressing the mapping explicitly
# prevents the f-string-double-prefix bug found in audit.
_USAGE_STAT_FIELDS: dict[str, str] = {
    "input_tokens": "total_input_tokens",
    "output_tokens": "total_output_tokens",
    "cached_tokens": "total_cached_tokens",
    "thinking_tokens": "total_thoughts_tokens",
    "total_tokens": "total_tokens",
}


def _read_token_counts(usage: dict[str, Any]) -> dict[str, int]:
    """Return a token-count dict keyed by our canonical names."""
    return {
        our_key: int(usage.get(meta_key, 0) or 0)
        for our_key, meta_key in _USAGE_STAT_FIELDS.items()
    }


def aggregate_cost_manifest(rcfg: ResolvedRunConfig) -> Path:
    """Scan per-run meta files and write ``cost_manifest.json``.

    Called at the end of ``all`` and available as its own subcommand for
    re-building the manifest without rerunning anything.
    """
    p = rcfg.proposer
    proposer_output = rcfg.output_dir / "proposer" / Path(p["config"]).stem
    verified_dir = rcfg.output_dir / "verified"
    crops_dir = rcfg.output_dir / "crops"
    eval_dir = rcfg.output_dir / "evaluation"

    # ---- Proposer aggregation ----
    per_pass: list[dict[str, Any]] = []
    proposer_cost = 0.0
    proposer_tokens: dict[str, int] = {k: 0 for k in _USAGE_STAT_FIELDS}
    proposer_wall_s = 0.0
    tiles_processed = 0
    tiles_failed = 0

    # Track per-map tile allocation and (where available) per-tile cost
    # contribution. We conservatively assign proposer cost per run by
    # the tile count that run processed — per-map proposer cost is then
    # proportional to the tiles from each map.
    per_map_tile_count: dict[str, int] = {}
    per_map_failed: dict[str, int] = {}

    for run_dir in sorted(proposer_output.glob("run_*")):
        meta_files = sorted(run_dir.glob("*.meta.json"))
        if not meta_files:
            continue
        meta = _read_meta(meta_files[0])
        cost = (
            meta.get("cost_estimate", {}).get("total_cost_usd", 0.0) or 0.0
        )
        usage = meta.get("usage_stats", {})
        proposer_cost += cost
        pass_tokens = _read_token_counts(usage)
        for k, v in pass_tokens.items():
            proposer_tokens[k] += v
        ts = meta.get("timestamp", {})
        duration = ts.get("duration_seconds") or 0.0
        proposer_wall_s += duration
        exec_stats = meta.get("execution_stats", {})
        items_proc = int(exec_stats.get("items_processed", 0))
        items_fail = int(exec_stats.get("items_failed", 0))
        tiles_processed += items_proc
        tiles_failed += items_fail

        # Per-map tile attribution
        for tile_name in exec_stats.get("completed_items", []):
            m = tile_to_map(tile_name)
            per_map_tile_count[m] = per_map_tile_count.get(m, 0) + 1
        for tile_name in exec_stats.get("failed_items", []):
            if isinstance(tile_name, str):
                m = tile_to_map(tile_name)
                per_map_failed[m] = per_map_failed.get(m, 0) + 1

        per_pass.append({
            "pass": _parse_pass_index(run_dir.name),
            "cost_usd": round(cost, 4),
            "duration_seconds": duration,
            "tokens": pass_tokens,
            "tiles_processed": items_proc,
            "tiles_failed": items_fail,
        })

    # ---- Verifier aggregation ----
    verifier_meta = _read_meta(verified_dir / "run.meta.json")
    verifier_cost = (
        verifier_meta.get("cost_estimate", {}).get("total_cost_usd", 0.0)
        or 0.0
    )
    v_usage = verifier_meta.get("usage_stats", {})
    verifier_tokens = _read_token_counts(v_usage)
    verifier_wall_s = (
        verifier_meta.get("timestamp", {}).get("duration_seconds") or 0.0
    )
    v_exec = verifier_meta.get("execution_stats", {})
    cands_processed = int(v_exec.get("items_processed", 0))
    cands_failed = int(v_exec.get("items_failed", 0))

    # ---- Totals ----
    total_cost = round(proposer_cost + verifier_cost, 4)
    total_tokens = {
        k: proposer_tokens[k] + verifier_tokens[k]
        for k in proposer_tokens
    }
    total_wall_s = proposer_wall_s + verifier_wall_s
    # Cache hit rate: cached_tokens is a subset of input_tokens (Gemini's
    # prompt_token_count already includes cached content), so the
    # correct denominator is just input_tokens, not input+cached.
    input_total = total_tokens["input_tokens"]
    cache_rate = (
        total_tokens["cached_tokens"] / input_total
        if input_total > 0 else 0.0
    )

    # ---- Final detection count ----
    final_geojson = verified_dir / "verified_detections.geojson"
    final_count = 0
    if final_geojson.is_file():
        try:
            final_count = len(
                json.loads(final_geojson.read_text(encoding="utf-8"))
                .get("features", [])
            )
        except json.JSONDecodeError:
            pass

    # ---- Per-map breakdown ----
    # Proposer cost is attributed per map proportionally to processed
    # tiles. Verifier cost is attributed per map proportionally to
    # candidate count (determined via the candidate manifest).
    total_tiles_seen = sum(per_map_tile_count.values()) or 1
    manifest = _read_meta(crops_dir / "candidate_manifest.json")
    per_map_candidates: dict[str, int] = {}
    for cand in manifest.get("candidates", []):
        src = cand.get("source_tile") or ""
        if src:
            m = tile_to_map(src)
            per_map_candidates[m] = per_map_candidates.get(m, 0) + 1
    total_candidates = sum(per_map_candidates.values()) or 1

    per_map_rows: list[dict[str, Any]] = []
    all_maps = sorted(
        set(per_map_tile_count) | set(per_map_candidates) | set(per_map_failed)
    )
    for m in all_maps:
        tiles = per_map_tile_count.get(m, 0)
        cands = per_map_candidates.get(m, 0)
        p_cost = proposer_cost * tiles / total_tiles_seen
        v_cost = verifier_cost * cands / total_candidates
        per_map_rows.append({
            "map_id": m,
            "tiles": tiles,
            "tiles_failed": per_map_failed.get(m, 0),
            "candidates": cands,
            "proposer_cost_usd": round(p_cost, 4),
            "verifier_cost_usd": round(v_cost, 4),
            "total_cost_usd": round(p_cost + v_cost, 4),
        })

    # ---- Unit costs ----
    unique_tiles = len(set(
        tile for tile in _iter_all_tiles(proposer_output)
    ))
    tile_count = unique_tiles or tiles_processed // max(
        1, int(rcfg.proposer["passes"]),
    )
    map_count = len(set(per_map_tile_count))
    ref_mounds = _count_reference_mounds(Path(rcfg.evaluate["ground_truth"]))
    manifest_path = Path(rcfg.proposer["manifest"])
    try:
        manifest_tiles = len(
            json.loads(manifest_path.read_text(encoding="utf-8"))
        )
    except (json.JSONDecodeError, FileNotFoundError):
        manifest_tiles = tile_count

    unit_costs = {
        "cost_per_tile": round(
            total_cost / manifest_tiles, 6,
        ) if manifest_tiles else 0.0,
        "cost_per_map": round(
            total_cost / map_count, 4,
        ) if map_count else 0.0,
        "cost_per_detection": round(
            total_cost / final_count, 6,
        ) if final_count else 0.0,
        "cost_per_reference_mound": round(
            total_cost / ref_mounds, 6,
        ) if ref_mounds else 0.0,
        "tile_count": manifest_tiles,
        "map_count": map_count,
        "reference_mound_count": ref_mounds,
        "final_detection_count": final_count,
    }

    manifest_out = {
        "run_name": rcfg.run_name,
        "generated_at": now_iso(),
        "script_version": __version__,
        "totals": {
            "cost_usd": total_cost,
            **total_tokens,
            "cache_hit_rate": round(cache_rate, 4),
            "wall_clock_seconds": round(total_wall_s, 3),
        },
        "by_stage": {
            "proposer": {
                "cost_usd": round(proposer_cost, 4),
                "wall_clock_seconds": round(proposer_wall_s, 3),
                "tokens": proposer_tokens,
                "tiles_processed": tiles_processed,
                "tiles_failed": tiles_failed,
                "failure_rate": round(
                    tiles_failed / max(1, tiles_processed + tiles_failed),
                    4,
                ),
                "per_pass": per_pass,
            },
            "verifier": {
                "cost_usd": round(verifier_cost, 4),
                "wall_clock_seconds": round(verifier_wall_s, 3),
                "tokens": verifier_tokens,
                "candidates_processed": cands_processed,
                "candidates_failed": cands_failed,
            },
            "extract_crops": {
                "candidates_extracted": len(
                    manifest.get("candidates", []),
                ),
            },
            "consensus": {},
            "evaluate": {"eval_dir": str(eval_dir)},
        },
        "unit_costs": unit_costs,
        "per_map": per_map_rows,
    }
    out_path = rcfg.output_dir / "cost_manifest.json"
    out_path.write_text(
        json.dumps(manifest_out, indent=2), encoding="utf-8",
    )
    logger.info("Cost manifest: %s", out_path)
    return out_path


_PASS_INDEX_RE = re.compile(r"^run_(\d+)")


def _parse_pass_index(dir_name: str) -> int:
    """Return the integer pass index from a run_N-style directory name.

    Returns 0 on failure rather than raising, so a malformed subdir
    name does not abort cost aggregation.
    """
    match = _PASS_INDEX_RE.match(dir_name)
    return int(match.group(1)) if match else 0


def _iter_all_tiles(proposer_output: Path):
    """Yield every tile name referenced in per-run meta files (deduped)."""
    for run_dir in proposer_output.glob("run_*"):
        for meta_file in run_dir.glob("*.meta.json"):
            meta = _read_meta(meta_file)
            for tile in (
                meta.get("execution_stats", {}).get("completed_items", [])
            ):
                yield tile


def _count_reference_mounds(path: Path) -> int:
    """Count features in the ground-truth GeoJSON."""
    try:
        return len(
            json.loads(path.read_text(encoding="utf-8"))
            .get("features", [])
        )
    except (json.JSONDecodeError, FileNotFoundError):
        return 0


# ---------------------------------------------------------------------------
# Launch manifest + intent check
# ---------------------------------------------------------------------------
def _locate_pre_launch_audit(config_path: Path | None) -> Path | None:
    """Return the sibling `<config_stem>_pre_launch_audit.md` if present.

    Convention: when a YAML run-config has an accompanying audit file,
    name it ``<stem>_pre_launch_audit.md`` in the same directory. The
    launcher copies it into the run output directory and records its
    SHA256 in ``launch_manifest.json``.
    """
    if config_path is None:
        return None
    audit = config_path.parent / f"{config_path.stem}_pre_launch_audit.md"
    return audit if audit.is_file() else None


def write_launch_manifest(
    rcfg: ResolvedRunConfig,
    cli_argv: list[str],
    config_path: Path | None,
    *,
    expected_cost_usd: float | None,
) -> Path:
    """Write ``launch_manifest.json`` at the start of a run."""
    git = git_status()
    proposer_cfg = Path(rcfg.proposer["config"])
    verify_cfg = Path(rcfg.verify["config"])
    manifest_path = Path(rcfg.proposer["manifest"])

    audit_path = _locate_pre_launch_audit(config_path)
    if audit_path is not None:
        # Copy the audit into the run dir so it travels with the outputs.
        dest = rcfg.output_dir / "pre_launch_audit.md"
        shutil.copy2(audit_path, dest)

    manifest = {
        "run_name": rcfg.run_name,
        "started_at": now_iso(),
        "status": "in_progress",
        "git": git,
        "hostname": socket.gethostname(),
        "user": getpass.getuser(),
        "python_version": platform.python_version(),
        "cli_invocation": cli_argv,
        "script_version": __version__,
        "resolved_config": {
            "proposer": _stringify_paths(rcfg.proposer),
            "consensus": _stringify_paths(rcfg.consensus),
            "extract": _stringify_paths(rcfg.extract),
            "verify": _stringify_paths(rcfg.verify),
            "evaluate": _stringify_paths(rcfg.evaluate),
            "global_opts": rcfg.global_opts,
        },
        "config_file_path": str(config_path) if config_path else None,
        "config_file_sha256": (
            sha256_file(config_path) if config_path else None
        ),
        "pre_launch_audit": (
            {
                "path": str(audit_path),
                "sha256": sha256_file(audit_path),
                "copied_to": str(rcfg.output_dir / "pre_launch_audit.md"),
            }
            if audit_path is not None else None
        ),
        "input_sha256": {
            "manifest": sha256_file(manifest_path),
            "ground_truth": sha256_file(
                Path(rcfg.evaluate["ground_truth"])
            ),
            "bounds": sha256_file(Path(rcfg.evaluate["bounds"])),
            "proposer_config": sha256_file(proposer_cfg),
            "verifier_config": sha256_file(verify_cfg),
            "rasters_dir_listing": sha256_directory_listing(
                Path(rcfg.extract["rasters_dir"]),
            ),
        },
        "seed": rcfg.evaluate.get("seed", DEFAULT_SEED),
        "service_tier": rcfg.global_opts.get("service_tier", "flex"),
        "expected_cost_usd": expected_cost_usd,
    }
    out = rcfg.output_dir / "launch_manifest.json"
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return out


def write_experiment_intent(
    rcfg: ResolvedRunConfig, expected_cost_usd: float | None,
) -> Path:
    """Write a human-readable run description for audit trail."""
    p, c, e, v, ev = (
        rcfg.proposer, rcfg.consensus, rcfg.extract,
        rcfg.verify, rcfg.evaluate,
    )
    lines = [
        f"# Experiment intent: {rcfg.run_name}",
        "",
        f"Generated: {now_iso()}",
        f"Script: `scripts/run_generalisation.py` v{__version__}",
        "",
        "## Pipeline",
        "",
        "1. **Proposer** "
        f"(`{p['config']}`, thinking={p['thinking_level']}, "
        f"T={p['temperature']}, K={p['passes']})",
        "2. **Consensus** "
        f"(greedy, {c.get('dedup_radius_m', 20.0)} m radius, "
        f"vote_t={c['vote_threshold']})",
        "3. **Extract** (padding "
        f"{e['padding']} px, rasters: {e['rasters_dir']})",
        "4. **Verify** "
        f"(`{v['config']}`, mode={v.get('mode', 'realtime')})",
        f"5. **Evaluate** (prob_t={ev['prob_threshold']}, "
        f"buffers={ev['buffers']} m, bootstrap={ev.get('bootstrap', 1000)})",
        "",
        "## Data",
        "",
        f"- Tile manifest: `{p['manifest']}`",
        f"- Ground truth: `{ev['ground_truth']}`",
        f"- Evaluation bounds: `{ev['bounds']}`",
        "",
        "## Expected cost",
        "",
        (
            f"- ~${expected_cost_usd:.0f} (Flex tier estimate)"
            if expected_cost_usd is not None
            else "- (not estimated)"
        ),
        "",
        "## Outputs",
        "",
        "- `launch_manifest.json` — reproducibility metadata",
        "- `cost_manifest.json` — full cost accounting",
        "- `consensus/` — voted candidate GeoJSON",
        "- `verified/` — verifier probabilities + final filtered GeoJSON",
        "- `evaluation/` — per-buffer F1 / P / R with bootstrap CIs",
    ]
    out = rcfg.output_dir / "experiment_intent.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def confirm_intent(intent_path: Path, auto_yes: bool) -> None:
    """Print the intent file and require a yes/no confirmation."""
    logger.info("Wrote experiment intent: %s", intent_path)
    print("\n" + "=" * 72)
    print(intent_path.read_text(encoding="utf-8"))
    print("=" * 72)
    if auto_yes:
        logger.info("--yes supplied: skipping interactive confirmation.")
        return
    try:
        answer = input(
            "Proceed with this run? Type 'yes' to confirm: ",
        ).strip().lower()
    except EOFError:
        answer = ""
    if answer not in ("yes", "y"):
        raise SystemExit("Aborted by user at intent-check.")


# ---------------------------------------------------------------------------
# Top-level subcommand dispatch
# ---------------------------------------------------------------------------
def _dry_run_banner(rcfg: ResolvedRunConfig) -> None:
    """Log a compact description of what would be executed."""
    logger.info("=" * 70)
    logger.info("[DRY RUN] No subprocesses or API calls will execute.")
    logger.info("[DRY RUN] Output dir: %s", rcfg.output_dir)
    logger.info("[DRY RUN] Proposer: %s, K=%s, T=%s, thinking=%s",
                rcfg.proposer["config"], rcfg.proposer["passes"],
                rcfg.proposer["temperature"],
                rcfg.proposer["thinking_level"])
    logger.info("[DRY RUN] Consensus: vote_t=%s, dedup=%s m",
                rcfg.consensus["vote_threshold"],
                rcfg.consensus.get("dedup_radius_m", 20.0))
    logger.info("[DRY RUN] Verifier: %s, prob_t=%s",
                rcfg.verify["config"], rcfg.evaluate["prob_threshold"])
    logger.info("[DRY RUN] Buffers: %s m", rcfg.evaluate["buffers"])
    logger.info("[DRY RUN] Inspect: %s/launch_manifest.json, "
                "experiment_intent.md, resolved_config.yaml",
                rcfg.output_dir)
    logger.info("=" * 70)


def cmd_all(args: argparse.Namespace) -> int:
    """Run every pipeline stage in order."""
    rcfg = _prepare_run(args)
    if args.dry_run:
        _dry_run_banner(rcfg)
        return 0

    resumed = _load_resume_state(rcfg.output_dir) if args.resume else {}

    if "proposer" not in resumed:
        summary = run_proposer(
            rcfg,
            limit=args.limit,
            skip_intent=True,  # wrapper-level intent check supersedes
        )
        _save_resume_state(rcfg.output_dir, "proposer", summary)
    if "consensus" not in resumed:
        _save_resume_state(
            rcfg.output_dir, "consensus", run_consensus(rcfg),
        )
    if "extract" not in resumed:
        _save_resume_state(rcfg.output_dir, "extract", run_extract(rcfg))
    if "verify" not in resumed:
        _save_resume_state(rcfg.output_dir, "verify", run_verify(rcfg))
    if "evaluate" not in resumed:
        _save_resume_state(rcfg.output_dir, "evaluate", run_evaluate(rcfg))

    aggregate_cost_manifest(rcfg)
    _finalise_launch_manifest(rcfg)
    logger.info("Run complete: %s", rcfg.output_dir)
    return 0


def cmd_proposer(args: argparse.Namespace) -> int:
    rcfg = _prepare_run(args)
    if args.dry_run:
        _dry_run_banner(rcfg)
        return 0
    run_proposer(rcfg, limit=args.limit, skip_intent=True)
    return 0


def cmd_consensus(args: argparse.Namespace) -> int:
    rcfg = _prepare_run(args, skip_intent_check=True)
    if args.dry_run:
        _dry_run_banner(rcfg)
        return 0
    run_consensus(rcfg)
    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    rcfg = _prepare_run(args, skip_intent_check=True)
    if args.dry_run:
        _dry_run_banner(rcfg)
        return 0
    run_extract(rcfg)
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    rcfg = _prepare_run(args, skip_intent_check=True)
    if args.dry_run:
        _dry_run_banner(rcfg)
        return 0
    run_verify(rcfg)
    return 0


def cmd_evaluate(args: argparse.Namespace) -> int:
    rcfg = _prepare_run(args, skip_intent_check=True)
    if args.dry_run:
        _dry_run_banner(rcfg)
        return 0
    run_evaluate(rcfg)
    return 0


def cmd_aggregate_cost(args: argparse.Namespace) -> int:
    rcfg = _prepare_run(args, skip_intent_check=True)
    if args.dry_run:
        _dry_run_banner(rcfg)
        return 0
    aggregate_cost_manifest(rcfg)
    return 0


def _prepare_run(
    args: argparse.Namespace, *, skip_intent_check: bool = False,
) -> ResolvedRunConfig:
    """Shared setup: load config, enforce git-clean check, write manifests."""
    config: dict[str, Any] = {}
    config_path: Path | None = None
    if args.run_config is not None:
        config_path = Path(args.run_config)
        config = load_yaml_config(config_path)
    merged = merge_cli_overrides(config, args)
    rcfg = resolve_run_config(merged, args)

    if rcfg.output_dir.exists() and not args.resume:
        logger.warning(
            "Output dir already exists (%s). Use --resume to continue "
            "an existing run, or remove the directory to start fresh.",
            rcfg.output_dir,
        )
    rcfg.output_dir.mkdir(parents=True, exist_ok=True)

    # Snapshot resolved config for the audit trail.
    # ``yaml.safe_dump`` cannot serialise ``Path`` objects (which CLI
    # overrides introduce into the merged config), so stringify them
    # first.
    snapshot = {
        "run_name": rcfg.run_name,
        "output_root": rcfg.global_opts["output_root"],
        "proposer": _stringify_paths(rcfg.proposer),
        "consensus": _stringify_paths(rcfg.consensus),
        "extract": _stringify_paths(rcfg.extract),
        "verify": _stringify_paths(rcfg.verify),
        "evaluate": _stringify_paths(rcfg.evaluate),
    }
    (rcfg.output_dir / "resolved_config.yaml").write_text(
        yaml.safe_dump(snapshot, sort_keys=False),
        encoding="utf-8",
    )

    # Warn if evaluation buffers drop any of the paper standard.
    missing_buffers = [
        b for b in RECOMMENDED_BUFFERS
        if b not in rcfg.evaluate.get("buffers", [])
    ]
    if missing_buffers:
        logger.warning(
            "Evaluation buffers %s missing from run config; paper "
            "standard is %s.",
            missing_buffers, list(RECOMMENDED_BUFFERS),
        )

    # Git-clean check
    git = git_status()
    if git["dirty"] and not args.allow_dirty:
        raise SystemExit(
            "Refusing to launch: working tree is dirty. Commit or stash "
            "changes, or re-run with --allow-dirty (not recommended for "
            "publishable runs)."
        )

    # Reproducibility manifest + intent file (always written so dry-run
    # users can inspect what would happen). Confirmation prompt is only
    # shown for real (non-dry) runs.
    expected_cost = _estimate_cost(rcfg)
    write_launch_manifest(
        rcfg, sys.argv, config_path, expected_cost_usd=expected_cost,
    )
    intent_path = write_experiment_intent(rcfg, expected_cost)
    if args.dry_run:
        logger.info(
            "[dry-run] Intent written to %s; no API calls will be made.",
            intent_path,
        )
    elif not skip_intent_check:
        confirm_intent(intent_path, auto_yes=args.yes)

    return rcfg


def _estimate_cost(rcfg: ResolvedRunConfig) -> float | None:
    """Rough cost estimate from manifest tile count and K.

    Based on Phase 3a image matrix empirical ratio of ~$0.0082/tile/pass
    for plus-hp HIGH + T=0.7 + Flex. Handles both list-form manifests
    (newer scripts emit a plain JSON array) and dict-form manifests
    (``{"tiles": [...]}``) for older writers.
    Returns ``None`` if the manifest is unreadable.
    """
    try:
        raw = Path(rcfg.proposer["manifest"]).read_text(encoding="utf-8")
        manifest = json.loads(raw)
    except (json.JSONDecodeError, FileNotFoundError, OSError):
        return None
    if isinstance(manifest, list):
        tiles = len(manifest)
    elif isinstance(manifest, dict):
        for key in ("tiles", "manifest", "items"):
            val = manifest.get(key)
            if isinstance(val, list):
                tiles = len(val)
                break
        else:
            logger.warning(
                "Manifest %s has unexpected shape; cost estimate skipped.",
                rcfg.proposer["manifest"],
            )
            return None
    else:
        return None
    k = int(rcfg.proposer.get("passes", 1))
    per_tile_usd = 0.0082  # empirical; text verifier adds ~$5 flat
    return round(tiles * k * per_tile_usd + 5.0, 2)


def _stringify_paths(section: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of ``section`` with Path values converted to strings.

    ``yaml.safe_dump`` refuses ``Path`` objects; CLI overrides install
    them wherever a path-typed flag is supplied (``--tiles-dir``,
    ``--manifest``, etc.). We normalise here so the resolved_config
    snapshot and launch_manifest stay YAML/JSON-clean.
    """
    return {
        k: (str(v) if isinstance(v, Path) else v)
        for k, v in section.items()
    }


def _save_resume_state(output_dir: Path, stage: str, summary: dict) -> None:
    """Record stage completion for --resume."""
    state_file = output_dir / ".resume_state.json"
    state = (
        json.loads(state_file.read_text(encoding="utf-8"))
        if state_file.is_file() else {}
    )
    state[stage] = {"completed_at": now_iso(), "summary": summary}
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _load_resume_state(output_dir: Path) -> dict[str, Any]:
    """Return the set of stages already marked complete."""
    state_file = output_dir / ".resume_state.json"
    if not state_file.is_file():
        return {}
    try:
        return json.loads(state_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _finalise_launch_manifest(rcfg: ResolvedRunConfig) -> None:
    """Update launch_manifest.json status to 'completed' with completion time."""
    path = rcfg.output_dir / "launch_manifest.json"
    if not path.is_file():
        return
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    manifest["status"] = "completed"
    manifest["completed_at"] = now_iso()
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Argparse
# ---------------------------------------------------------------------------
def build_arg_parser() -> argparse.ArgumentParser:
    """Build the top-level parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="run_generalisation.py",
        description=(
            "End-to-end generalisation-run launcher for map-reader-llm. "
            "Orchestrates proposer, consensus, verifier, and evaluation "
            "stages with full reproducibility metadata and cost tracking."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__version__}",
    )

    sub = parser.add_subparsers(dest="command", required=False)

    # Shared flags added to each subcommand
    def add_shared(p: argparse.ArgumentParser) -> None:
        p.add_argument("--run-config", type=Path, help="YAML run-config path")
        p.add_argument("--run-name", type=str, help="Output subdir name")
        p.add_argument(
            "--output-root", type=Path,
            help="Parent directory for output (default: outputs/)",
        )
        p.add_argument("--dry-run", action="store_true",
                       help="Plan the run without API calls")
        p.add_argument("--resume", action="store_true",
                       help="Skip stages with existing outputs")
        p.add_argument("--allow-dirty", action="store_true",
                       help="Permit launch with uncommitted changes")
        p.add_argument("--yes", action="store_true",
                       help="Auto-confirm intent check")
        p.add_argument("--service-tier",
                       choices=["flex", "standard"], default=None)

    def add_proposer_flags(p: argparse.ArgumentParser) -> None:
        p.add_argument("--proposer-config", type=Path)
        p.add_argument("--tiles-dir", type=Path)
        p.add_argument("--manifest", type=Path)
        p.add_argument("--tile-size", type=int)
        p.add_argument("--temperature", type=float)
        p.add_argument("--thinking-level",
                       choices=["minimal", "low", "medium", "high"])
        p.add_argument("--passes", type=int, help="K proposer passes")
        p.add_argument("--proposer-workers", type=int)
        p.add_argument("--max-retries", type=int)
        p.add_argument("--limit", type=int,
                       help="Process only first N tiles "
                            "(for --dry-run / single-tile live test)")

    def add_consensus_flags(p: argparse.ArgumentParser) -> None:
        p.add_argument("--vote-threshold", type=int)
        p.add_argument("--dedup-radius-m", type=float)

    def add_extract_flags(p: argparse.ArgumentParser) -> None:
        p.add_argument("--padding", type=int)
        p.add_argument("--rasters-dir", type=Path)

    def add_verify_flags(p: argparse.ArgumentParser) -> None:
        p.add_argument("--verifier-config", type=Path)
        p.add_argument("--verify-mode", choices=["realtime", "batch"])
        p.add_argument("--verify-workers", type=int)

    def add_evaluate_flags(p: argparse.ArgumentParser) -> None:
        p.add_argument("--prob-threshold", type=float)
        p.add_argument("--buffers", type=int, nargs="+",
                       help="Evaluation buffer radii in metres")
        p.add_argument("--bootstrap", type=int)
        p.add_argument("--seed", type=int)
        p.add_argument("--ground-truth", type=Path)
        p.add_argument("--bounds", type=Path)

    # Build each subcommand with just the flags it needs.
    all_p = sub.add_parser("all", help="Run every stage in order")
    add_shared(all_p)
    add_proposer_flags(all_p)
    add_consensus_flags(all_p)
    add_extract_flags(all_p)
    add_verify_flags(all_p)
    add_evaluate_flags(all_p)
    all_p.set_defaults(func=cmd_all)

    prop_p = sub.add_parser("proposer", help="Run proposer passes only")
    add_shared(prop_p)
    add_proposer_flags(prop_p)
    prop_p.set_defaults(func=cmd_proposer)

    cons_p = sub.add_parser("consensus", help="Build consensus only")
    add_shared(cons_p)
    add_proposer_flags(cons_p)
    add_consensus_flags(cons_p)
    cons_p.set_defaults(func=cmd_consensus)

    ext_p = sub.add_parser("extract", help="Extract candidate crops")
    add_shared(ext_p)
    add_proposer_flags(ext_p)
    add_consensus_flags(ext_p)
    add_extract_flags(ext_p)
    ext_p.set_defaults(func=cmd_extract)

    ver_p = sub.add_parser("verify", help="Run verifier on crops")
    add_shared(ver_p)
    add_proposer_flags(ver_p)
    add_consensus_flags(ver_p)
    add_extract_flags(ver_p)
    add_verify_flags(ver_p)
    ver_p.set_defaults(func=cmd_verify)

    eval_p = sub.add_parser("evaluate", help="Compute F1 at multiple buffers")
    add_shared(eval_p)
    add_proposer_flags(eval_p)
    add_consensus_flags(eval_p)
    add_extract_flags(eval_p)
    add_verify_flags(eval_p)
    add_evaluate_flags(eval_p)
    eval_p.set_defaults(func=cmd_evaluate)

    agg_p = sub.add_parser(
        "aggregate-cost", help="(Re)build cost_manifest.json",
    )
    add_shared(agg_p)
    add_proposer_flags(agg_p)
    add_consensus_flags(agg_p)
    add_extract_flags(agg_p)
    add_verify_flags(agg_p)
    add_evaluate_flags(agg_p)
    agg_p.set_defaults(func=cmd_aggregate_cost)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        # Default to 'all' if no subcommand given.
        parser.parse_args(["all", "--help"])
        return 2
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
