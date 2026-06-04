#!/usr/bin/env python3
"""Generate the experimental manifests (and, later, per-run post-run reports).

This is the **Phase 1 generator** for the four-entity manifest model resolved in
``planning/manifest-schema-design.md``. It is the *only* writer of the machine-
extracted manifests (``runs`` / ``conditions`` / ``passes`` / ``run-registry``):
humans edit the *source-of-truth* files (``*.meta.json``, ``evaluation/*.json``,
YAML configs) and a small set of human-authored fields; the generator
re-extracts everything else.

Design references
-----------------
* Entity model + field lists: ``planning/manifest-schema-design.md`` (§§ 1A, 2).
* Machine-readable contract: ``docs/manifest-schemas/*.schema.json`` (draft
  2020-12). These are authoritative; this module validates every row it emits
  against them before writing.
* Anti-confabulation rule (``~/.claude/CLAUDE.md``): every extracted value must
  trace to a source file recorded in ``provenance.source_files``; a value that
  cannot be read is ``null``, never guessed. In particular ``model_used`` is
  read from ``per_item_metadata.model_used`` and NEVER inferred from a
  directory name (erratum-backed gotcha: a ``pro-``named condition ran Flash).

Build status
------------
This commit lands the **scaffold**: schema loading with cross-file ``$ref``
resolution, single-row and whole-manifest validation, a provenance builder, and
a ``--self-test`` that proves the harness round-trips. The per-entity extractors
(passes → conditions → runs row → registry) are built in the following steps,
starting with the ``gold-standard-v2`` vertical slice.

Usage
-----
    # prove the validation harness loads all schemas and round-trips a row
    python scripts/generate_post_run_report.py --self-test

    # (later) extract and validate the manifests for one run, writing nothing
    python scripts/generate_post_run_report.py --run gold-standard-v2 --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonschema
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

#: Repository root (this file lives in ``<repo>/scripts/``).
REPO_ROOT: Path = Path(__file__).resolve().parents[1]

#: Directory holding the six JSON Schema files (the output contract).
SCHEMA_DIR: Path = REPO_ROOT / "docs" / "manifest-schemas"

#: Semantic version of THIS generator script. Written into every row's
#: ``provenance.extractor_version`` (tracks the script, distinct from the
#: manifest *format* ``schema_version``). Bump on an extraction-logic change OR a
#: batch-emission milestone. The 0.3.0 bump (Session 95, 2026-06-02) is the latter:
#: no extractor-logic change, but it marks the first decomposition batch landing —
#: the 4 non-gs runs (e47-propose-brief, n1-outstanding-384,
#: retest-h11-single-pass-384-t0, consensus-384-t1-0; 88 conditions) published into
#: the manifest from the hand-authored ``run-conditions.json`` sidecar. 0.4.0
#: (Session 96, 2026-06-02) is an extraction-logic change bundling two additions: the
#: generator now emits a fifth manifest, ``analyses`` (sub-step 3c), from the
#: hand-authored ``run-analyses.json`` sidecar; and ``extract_passes`` honours a
#: per-pool ``model_of_record`` override (E57) for pools whose recorded meta carries a
#: model template-default. Landed alongside the N=1 baseline-matrix + batch-pass
#: publishing.
GENERATOR_VERSION: str = "0.4.0"

#: Manifest format version embedded at the top of each emitted manifest. Must
#: match the ``schema_version`` const in the schema files.
SCHEMA_VERSION: str = "1.0"

#: Map of manifest name → schema filename. The per-row item definition is
#: derived from each schema (see :func:`_row_def_name`) rather than hard-coded,
#: so a schema rename cannot silently desynchronise this module.
MANIFEST_SCHEMAS: dict[str, str] = {
    "runs": "runs-manifest.schema.json",
    "conditions": "conditions-manifest.schema.json",
    "passes": "passes-manifest.schema.json",
    "analyses": "analyses-manifest.schema.json",
    "run-registry": "run-registry.schema.json",
}


# --------------------------------------------------------------------------- #
# Schema loading and validation
# --------------------------------------------------------------------------- #


def load_schema_registry(schema_dir: Path = SCHEMA_DIR) -> tuple[Registry, dict[str, dict]]:
    """Load every ``*.schema.json`` into a ``referencing`` registry.

    Each schema is registered under its own ``$id`` so the relative cross-file
    references in the schemas (e.g. ``common-defs.schema.json#/$defs/provenance``)
    resolve against the referring schema's base URI.

    Args:
        schema_dir: Directory containing the schema files.

    Returns:
        A ``(registry, contents_by_id)`` pair, where ``contents_by_id`` maps each
        schema's ``$id`` to its parsed JSON (handy for introspection).

    Raises:
        FileNotFoundError: If ``schema_dir`` contains no schema files.
    """
    schema_files = sorted(schema_dir.glob("*.schema.json"))
    if not schema_files:
        raise FileNotFoundError(f"No *.schema.json files found in {schema_dir}")

    resources: list[tuple[str, Resource]] = []
    contents_by_id: dict[str, dict] = {}
    for path in schema_files:
        contents = json.loads(path.read_text(encoding="utf-8"))
        schema_id = contents["$id"]
        contents_by_id[schema_id] = contents
        resources.append((schema_id, Resource.from_contents(contents, default_specification=DRAFT202012)))

    registry = Registry().with_resources(resources)
    return registry, contents_by_id


def _schema_id(manifest: str) -> str:
    """Return the ``$id`` of the given manifest's schema file."""
    contents = json.loads((SCHEMA_DIR / MANIFEST_SCHEMAS[manifest]).read_text(encoding="utf-8"))
    return contents["$id"]


def _row_def_name(manifest: str) -> str:
    """Derive the ``$defs`` name of a manifest's per-row item schema.

    Reads the manifest schema, finds its single top-level array property (``runs``
    / ``passes`` / ``conditions`` / ``analyses`` / ``registry``), and returns the
    ``$defs`` key its ``items.$ref`` points at (e.g. ``run``, ``pass``, ``entry``).
    Deriving this avoids hard-coding the mapping, so a schema edit cannot silently
    desync the validator.
    """
    contents = json.loads((SCHEMA_DIR / MANIFEST_SCHEMAS[manifest]).read_text(encoding="utf-8"))
    for prop in contents.get("properties", {}).values():
        if isinstance(prop, dict) and prop.get("type") == "array":
            ref = prop.get("items", {}).get("$ref", "")
            if ref.startswith("#/$defs/"):
                return ref.rsplit("/", 1)[-1]
    raise ValueError(f"Could not locate the per-row array definition in {manifest} schema")


def make_row_validator(manifest: str, registry: Registry) -> jsonschema.Draft202012Validator:
    """Build a validator for a single *row* of the given manifest.

    The schema files validate a whole manifest object (``{schema_version, runs:
    [...]}``); to validate one extracted row in isolation we point a validator at
    the per-row ``$defs`` entry via the registry, which keeps the row's relative
    ``common-defs`` references resolvable.

    Args:
        manifest: One of :data:`MANIFEST_SCHEMAS` keys.
        registry: A registry from :func:`load_schema_registry`.

    Returns:
        A draft 2020-12 validator with date-time format checking enabled.
    """
    ref = f"{_schema_id(manifest)}#/$defs/{_row_def_name(manifest)}"
    return jsonschema.Draft202012Validator(
        {"$ref": ref},
        registry=registry,
        format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER,
    )


def validate_row(manifest: str, row: dict, registry: Registry) -> list[str]:
    """Validate one extracted row; return a list of human-readable error strings.

    An empty list means the row conforms. Errors are sorted by JSON path so the
    output is stable across runs.

    Args:
        manifest: Which manifest the row belongs to.
        row: The extracted row object.
        registry: A registry from :func:`load_schema_registry`.

    Returns:
        Sorted error messages (``"<path>: <message>"``); empty if valid.
    """
    validator = make_row_validator(manifest, registry)
    errors = sorted(validator.iter_errors(row), key=lambda e: list(e.path))
    return [f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}" for e in errors]


# --------------------------------------------------------------------------- #
# Provenance
# --------------------------------------------------------------------------- #


def utc_now_iso() -> str:
    """Return the current UTC time as an ISO 8601 string (seconds precision)."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_provenance(source_files: list[str], extracted_at: str | None = None) -> dict[str, Any]:
    """Build a ``provenance`` object for an extracted row.

    Args:
        source_files: Repository-relative paths every value in the row was read
            from. Must be non-empty (the schema requires ``minItems: 1``); a row
            with no traceable source should not be emitted.
        extracted_at: ISO 8601 timestamp; defaults to now (UTC). Passed in
            explicitly by batch runs so all rows share one extraction timestamp.

    Returns:
        A ``{source_files, last_extracted_at, extractor_version}`` dict matching
        ``common-defs.schema.json#/$defs/provenance``.
    """
    if not source_files:
        raise ValueError("provenance.source_files must list at least one source file")
    return {
        "source_files": source_files,
        "last_extracted_at": extracted_at or utc_now_iso(),
        "extractor_version": GENERATOR_VERSION,
    }


# --------------------------------------------------------------------------- #
# Extraction inputs (the irreducibly-human decomposition)
# --------------------------------------------------------------------------- #
#
# The per-run DECOMPOSITION (which scored results are conditions, and how the
# proposer/verifier passes enumerate) is hand-authored in the sidecar
# ``results/run-conditions.json`` (sub-step 3b, decision Q3). It is loaded by
# :func:`load_run_conditions` and merged with the registry entry + the per-run
# facts into the single dict the extractors read (:func:`build_extraction_context`).
# Run-level facts (corpus, scope, gt_reference, study tags) live in the sibling
# ``results/run-facts.json`` and are never duplicated into the decomposition.
# gold-standard-v2 was the inline vertical slice; its decomposition migrated
# verbatim to the sidecar in the Session 94 refactor (behaviour-preserving).


def _load_json(path: Path) -> dict:
    """Load a JSON file (UTF-8)."""
    return json.loads(path.read_text(encoding="utf-8"))


def _repo_rel(path: Path) -> str:
    """Repository-relative POSIX path string (for provenance)."""
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def _tokens_from_usage(usage: dict) -> dict | None:
    """Map a meta.json ``usage_stats`` block to the schema's ``pass.tokens`` shape."""
    if not usage:
        return None
    return {
        "input_billed": usage.get("total_input_tokens", 0),
        "input_cached": usage.get("total_cached_tokens", 0),
        "output": usage.get("total_output_tokens", 0),
        "thinking": usage.get("total_thoughts_tokens", 0),
        "total": usage.get("total_tokens", 0),
    }


def _timestamps(meta: dict) -> dict | None:
    """Extract ``{start, end}`` from a meta.json ``timestamp`` block, if present."""
    ts = meta.get("timestamp")
    if isinstance(ts, dict) and ts.get("start") and ts.get("end"):
        return {"start": ts["start"], "end": ts["end"]}
    return None


def _pool_spec(value: Any) -> tuple[Any, str | None]:
    """Normalise a ``proposer_pools`` / ``verifier_passes`` entry.

    Two accepted forms:

    * compact string — the value IS the modality; the directory path is left to the
      caller's convention (``proposer/<label>`` for proposer pools, ``<label>`` for
      verifier passes), which keeps the gold-standard-v2 slice unchanged.
    * explicit dict — ``{"modality": ..., "path": "<rel-to-run-dir>"}`` for runs
      whose pools are not under ``proposer/`` (most runs put pool dirs directly under
      the run) or whose verifier metas are nested (e.g. pv-diag-384's deep
      ``verified/<config>/`` tree). The explicit path means the extractor never
      guesses a layout.

    Returns ``(modality, explicit_path_or_None)``.
    """
    if isinstance(value, dict):
        return value.get("modality"), value.get("path")
    return value, None


def _effective_temperature(cfg: dict) -> Any:
    """Return the verifier/proposer temperature, preferring the E55-corrected value.

    A CLI ``--temperature`` override was not always serialised into
    ``configuration.temperature`` (erratum E55, GAP-10): the corrected metas carry
    the real value in ``configuration.temperature_effective``. Prefer it; fall back
    to the base field. (``run.log`` is the deeper source if neither is present — not
    parsed here, since the affected metas were corrected non-destructively.)

    Uses an explicit ``is not None`` check, not ``.get(k, fallback)``: the latter
    would NOT fall back when ``temperature_effective`` is present but JSON-``null``.
    """
    effective = cfg.get("temperature_effective")
    return effective if effective is not None else cfg.get("temperature")


def extract_passes(facts: dict, at: str | None = None) -> list[dict]:
    """Extract pass rows (proposer + verifier) for one run.

    Proposer passes are read from each pool's ``run_N/*.meta.json``. Two meta shapes
    are handled: the newer shape carries ``per_item_metadata`` (the AUTHORITATIVE
    source of ``model_used``, never inferred from a directory name); the older Era-1
    batch-API shape has no per-item record, so ``configuration.model`` is the best
    available authoritative value and the tile count comes from
    ``execution_stats.items_processed`` (GAP-9). The pool directory is resolved from
    the spec's explicit ``path`` or, for the compact string form, the conventional
    ``proposer/<label>``. Verifier passes are read from ``<path-or-label>/run.meta.json``
    — the explicit path also covers deeply-nested verifier trees (GAP-7).

    Args:
        facts: an extraction context (see :func:`build_extraction_context`):
            ``run_id``, ``directory_path``, and the ``proposer_pools`` /
            ``verifier_passes`` decomposition hints.
        at: ISO timestamp stamped on every row's provenance (one per run).

    Returns:
        Pass rows conforming to the passes-manifest item schema.
    """
    run_id = facts["run_id"]
    run_dir = REPO_ROOT / facts["directory_path"]
    rows: list[dict] = []

    # --- proposer passes ---
    for pool, spec in facts.get("proposer_pools", {}).items():
        modality, path = _pool_spec(spec)
        # Model-of-record override (E57): the authoritative model when the recorded
        # meta is an unreliable template default (see below). Authored in the sidecar
        # from the study YAML; None for the normal case (trust the meta).
        model_of_record = spec.get("model_of_record") if isinstance(spec, dict) else None
        pool_dir = run_dir / (path or f"proposer/{pool}")
        for run_n_dir in sorted(pool_dir.glob("run_*")):
            suffix = run_n_dir.name.split("_", 1)[1] if "_" in run_n_dir.name else ""
            if not suffix.isdigit():
                print(f"WARNING: skipping non-numeric pass dir {_repo_rel(run_n_dir)}",
                      file=sys.stderr)
                continue
            meta_files = list(run_n_dir.glob("*.meta.json"))
            if not meta_files:
                continue
            pass_n = int(suffix)
            meta_path = meta_files[0]
            meta = _load_json(meta_path)
            pim = meta.get("per_item_metadata") or []
            cfg = meta.get("configuration", {})
            es = meta.get("execution_stats", {})
            if pim:
                # Newer shape: authoritative per-item model identity + tile count.
                n_proc = len(pim)
                model_used = next((it.get("model_used") for it in pim if it.get("model_used")), "")
                model_requested = next(
                    (it.get("model_requested") for it in pim if it.get("model_requested")), None)
                model_version = next(
                    (it.get("model_version") for it in pim if it.get("model_version")), None)
            else:
                # Era-1 batch-API shape (GAP-9): no per-item record. configuration.model
                # is the best available authoritative value (the verifier path uses the
                # same fallback); the tile count is in execution_stats. `or 0` guards an
                # explicit-null items_processed (which would break the n_proc==0 status
                # test and the schema's integer requirement).
                n_proc = es.get("items_processed") or 0
                model_used = cfg.get("model", "")
                model_requested = cfg.get("model")
                model_version = None
            # E57: a few pools carry a flash template-default in BOTH config.model AND
            # per_item_metadata.model_used even though the study YAML dispatched a
            # different model. When the sidecar declares model_of_record, it is the
            # authoritative identity and overrides the (unreliable) meta value; the
            # study-YAML source is cited via the sidecar in provenance.
            if model_of_record:
                model_used = model_of_record
                model_requested = model_of_record
            prov_sources = [_repo_rel(meta_path)]
            if model_of_record:
                prov_sources.append("results/run-conditions.json")
            failed = es.get("items_failed", 0)
            status = "failed" if n_proc == 0 else ("ok" if failed == 0 else "partial")
            rows.append({
                "pass_id": f"{run_id}::{pool}::run{pass_n}",
                "run_id": run_id,
                "proposer_pool": pool,
                "pass_n": pass_n,
                "model_used": model_used,
                "model_requested": model_requested,
                "model_version": model_version,
                "modality": modality,
                "thinking_level": cfg.get("thinking_level"),
                "temperature": _effective_temperature(cfg),
                "instruction_hash": cfg.get("instruction_hash") or cfg.get("system_instruction_hash"),
                "library_hash": cfg.get("library_hash"),
                "status": status,
                "n_tiles_processed": n_proc,
                "tokens": _tokens_from_usage(meta.get("usage_stats", {})),
                "cost_usd": (meta.get("cost_estimate") or {}).get("total_cost_usd"),
                "wall_clock_s": (meta.get("timestamp") or {}).get("duration_seconds"),
                "timestamps": _timestamps(meta),
                "retries": es.get("retries_total", 0),
                "provenance": build_provenance(prov_sources, at),
            })

    # --- verifier passes ---
    for vdir, spec in facts.get("verifier_passes", {}).items():
        modality, path = _pool_spec(spec)
        # Two on-disk shapes for a verifier pass's run metadata:
        #   * dir form    — ``<base>/run.meta.json`` (gold-standard-v2, verifier-t-pilot);
        #   * sidecar form — ``<base>.meta.json`` next to the verified geojson
        #     (the proposer-verifier strategy runs pv-384 / pv-512, which write one
        #     ``verified-<strategy>.meta.json`` per strategy rather than a per-pass dir).
        # Prefer the dir form so the gold-standard-v2 extraction stays byte-identical,
        # then fall back to the sidecar.
        base = path or vdir
        dir_meta = run_dir / base / "run.meta.json"
        sidecar_meta = run_dir / f"{base}.meta.json"
        if dir_meta.exists():
            meta_path = dir_meta
        elif sidecar_meta.exists():
            meta_path = sidecar_meta
        else:
            continue
        meta = _load_json(meta_path)
        cfg = meta.get("configuration", {})
        usage = meta.get("usage_stats", {})
        # Model-of-record (E57 / feedback_model_version_consistency): when the meta
        # carries per-item identity, it is authoritative over configuration.model
        # (which is a template default on some runs — gemini-3-flash where the API
        # actually dispatched gemini-3-flash-preview). gold-standard-v2's verifier meta
        # has no per_item_metadata, so it falls straight back to cfg.model (unchanged).
        pim = meta.get("per_item_metadata") or []
        model_used = (
            next((it.get("model_used") for it in pim if it.get("model_used")), None)
            or next((it.get("model_version") for it in pim if it.get("model_version")), None)
            or cfg.get("model", "")
        )
        model_requested = (
            next((it.get("model_requested") for it in pim if it.get("model_requested")), None)
            or cfg.get("model")
        )
        model_version = next((it.get("model_version") for it in pim if it.get("model_version")), None)
        # GAP-8 carry-forward: request_count is per-candidate-crop, not tiles — kept
        # and documented until the true tile count is derived or this field is nulled.
        req_count = (usage.get("by_provider", {}).get("google_gemini", {}) or {}).get("request_count", 0)
        rows.append({
            "pass_id": f"{run_id}::{vdir}::run1",
            "run_id": run_id,
            "proposer_pool": vdir,
            "pass_n": 1,
            "model_used": model_used,
            "model_requested": model_requested,
            "model_version": model_version,
            "modality": modality,
            "thinking_level": cfg.get("thinking_level"),
            "temperature": _effective_temperature(cfg),
            "instruction_hash": cfg.get("system_instruction_hash"),
            "library_hash": cfg.get("library_hash"),
            "status": "ok",
            "n_tiles_processed": req_count,
            "tokens": _tokens_from_usage(usage),
            "cost_usd": (meta.get("cost_estimate") or {}).get("total_cost_usd"),
            "wall_clock_s": (meta.get("timestamp") or {}).get("duration_seconds"),
            "timestamps": _timestamps(meta),
            "retries": (meta.get("execution_stats", {}) or {}).get("retries_total", 0),
            "provenance": build_provenance([_repo_rel(meta_path)], at),
        })

    return rows


def _normalise_detections_path(path: str) -> str:
    """Bridge the H11 reorganisation so evals recorded under old paths match.

    Evaluations written before the reorganisation cite the old ``outputs/h11/...``
    locations of files now under ``outputs/gs/`` or ``outputs/wbf/``. Normalising
    both sides to the current path lets the eval→condition mapping survive the
    move (the stable-identity principle the manifest design rests on).
    """
    return (
        path.replace("outputs/h11/gold-standard-v2", "outputs/gs/gold-standard-v2")
        .replace("outputs/h11/wbf", "outputs/wbf")
    )


def _build_eval_index() -> dict[str, list[tuple[str, dict, str | None]]]:
    """Index every ``results/**/evaluation.json`` by the detections it scored.

    Returns a map ``normalised-detections-path → [(eval_path, summary, bounds), …]``.
    The eval→condition link is read from ``_metadata.input_files.detections`` (and
    its ``cli_args`` bounds), never inferred — anti-confabulation.
    """
    index: dict[str, list[tuple[str, dict, str | None]]] = {}
    for eval_file in (REPO_ROOT / "results").rglob("evaluation.json"):
        try:
            doc = _load_json(eval_file)
        except (json.JSONDecodeError, OSError):
            continue
        meta = doc.get("_metadata", {})
        inf = meta.get("input_files", {}) or {}
        dets = inf.get("detections") or []
        if isinstance(dets, str):
            dets = [dets]
        bounds = inf.get("bounds") or (meta.get("cli_args") or {}).get("bounds")
        for det in dets:
            index.setdefault(_normalise_detections_path(det), []).append(
                (_repo_rel(eval_file), doc.get("summary", {}), bounds)
            )
    return index


def _point(value: Any) -> Any:
    """Return the ``point`` estimate from a metric block, or the value itself."""
    return value.get("point") if isinstance(value, dict) else value


def _metrics_from_eval(summary: dict, n_iter: int = 10000, seed: int = 42) -> dict:
    """Transform an ``evaluation.json`` summary into the schema's ``metrics`` shape.

    Produces the two-part block: per-buffer detection metrics (keyed by buffer
    radius in metres, each with an F1 bootstrap CI) plus the buffer-agnostic
    tile-classification block (MCC + confusion counts). The eval stores its CI
    bounds as ``f1_ci_lower``/``f1_ci_upper``; the bootstrap parameters
    (n_iter/seed/resampling) are the project standard, recorded explicitly.
    """
    per_buffer: dict[str, dict] = {}
    for b in summary.get("buffers", []):
        ci = None
        if b.get("f1_ci_lower") is not None and b.get("f1_ci_upper") is not None:
            ci = {
                "low": b["f1_ci_lower"],
                "high": b["f1_ci_upper"],
                "method": b.get("f1_ci_method", "BCa"),
                "n_iter": n_iter,
                "seed": seed,
                "resampling": "tile-level",
            }
        per_buffer[str(b["buffer_metres"])] = {
            "f1": b.get("f1"),
            "precision": b.get("precision"),
            "recall": b.get("recall"),
            "ci": ci,
            "coverage": None,  # eval records a coverage dict, not the scalar this field wants
            "ci_unreliable": bool(b.get("ci_unreliable", False)),
        }
    tc = summary.get("tile_classification", {})
    conf = tc.get("confusion", {})
    tile = {
        "mcc": _point(tc.get("mcc")),
        "sensitivity": _point(tc.get("sensitivity")),
        "specificity": _point(tc.get("specificity")),
        "tp": conf.get("tp"),
        "tn": conf.get("tn"),
        "fp": conf.get("fp"),
        "fn": conf.get("fn"),
    }
    return {"per_buffer": per_buffer, "tile_classification": tile}


#: Keys every condition spec must carry before the extractor reads them — a missing
#: one in the hand-authored sidecar should fail with a clear message, not an opaque
#: KeyError mid-build.
_REQUIRED_CONDITION_KEYS: tuple[str, ...] = (
    "label", "architecture", "aggregation", "proposer_pool", "n_passes",
)


def _require_condition_keys(spec: dict, run_id: str) -> None:
    """Validate a hand-authored condition spec carries the keys the extractor reads.

    Raises a descriptive ``ValueError`` (naming the run and the offending label) so a
    sidecar typo is caught at the spec rather than as an opaque ``KeyError`` deep in
    the row build. A condition must also carry an eval source — an explicit
    ``eval_path`` or a ``detections`` path for the auto-matcher.
    """
    missing = [k for k in _REQUIRED_CONDITION_KEYS if k not in spec]
    if "eval_path" not in spec and "detections" not in spec:
        missing.append("eval_path-or-detections")
    if missing:
        raise ValueError(
            f"condition spec in run '{run_id}' (label={spec.get('label', '?')}) "
            f"is missing required key(s): {', '.join(missing)}"
        )


def extract_conditions(facts: dict, at: str | None = None) -> list[dict]:
    """Extract condition rows (the evaluable scored results) for one run.

    Each condition's metrics come from its scoring evaluation, resolved one of two
    ways: an explicit ``eval_path`` in the spec (preferred — unambiguous, and the
    only correct option when the auto-matcher would pick the wrong eval, e.g. a
    buffer-rich F1-only sibling over the complete with-MCC eval at the nominal
    scope); or, with no ``eval_path``, an auto-match from the detection geojson via
    the results/ eval index, preferring the eval whose bounds match the run's nominal
    scope (gold-standard-v2 uses this path). A condition with no resolvable eval is
    skipped with a warning — the schema cannot represent a metric-less condition, so
    an unscored aggregation output is not a condition.

    Args:
        facts: an extraction context with a ``conditions`` list and a ``scope``.
        at: ISO timestamp stamped on every row's provenance.

    Returns:
        Condition rows conforming to the conditions-manifest item schema.
    """
    run_id = facts["run_id"]
    scope_bounds = facts.get("scope", {}).get("bounds_path")
    index: dict | None = None  # built lazily, only if a spec needs the auto-matcher
    rows: list[dict] = []

    for spec in facts.get("conditions", []):
        _require_condition_keys(spec, run_id)
        if spec.get("eval_path"):
            # explicit eval: the human/drafter names exactly which eval scores this.
            # A named-but-missing eval is an authoring error — fail loud with context
            # (unlike the auto-match miss below, where no eval can be legitimate).
            eval_file = REPO_ROOT / spec["eval_path"]
            if not eval_file.exists():
                raise FileNotFoundError(
                    f"condition '{spec['label']}' in run '{run_id}': "
                    f"eval_path {spec['eval_path']} does not exist"
                )
            summary = _load_json(eval_file).get("summary", {})
            eval_sources = [spec["eval_path"]]
        else:
            if index is None:
                index = _build_eval_index()
            det_norm = _normalise_detections_path(spec["detections"])
            candidates = index.get(det_norm, [])
            # prefer evals on the run's nominal scope; among those, the most complete
            scope_match = [c for c in candidates if c[2] == scope_bounds]
            chosen = scope_match or candidates
            if not chosen:
                print(
                    f"WARNING: no evaluation found for condition {spec['label']} "
                    f"({spec['detections']}); skipping (cannot emit metric-less condition).",
                    file=sys.stderr,
                )
                continue
            eval_path, summary, _bounds = max(chosen, key=lambda c: len(c[1].get("buffers", [])))
            # provenance cites the normalised detections path (what the match used),
            # not the raw spec path, so it always names a file that exists on disk
            eval_sources = [eval_path, det_norm]
        rows.append({
            "condition_id": f"{run_id}::{spec['label']}",
            "run_id": run_id,
            "label": spec["label"],
            "architecture": spec["architecture"],
            "aggregation": spec["aggregation"],
            "proposer_pool": spec["proposer_pool"],
            "n_passes": spec["n_passes"],
            "vote_threshold": spec.get("vote_threshold"),
            "prob_threshold": spec.get("prob_threshold"),
            "verifier_config": spec.get("verifier_config"),
            "scope_override": spec.get("scope_override"),
            "metrics": _metrics_from_eval(summary),
            "n_detections": summary.get("n_detections"),
            "n_candidates": spec.get("n_candidates"),
            "n_reference_mounds": spec.get("n_reference_mounds"),
            "provenance": build_provenance(eval_sources, at),
        })
    return rows


def build_run_row(run_id: str, directory_path: str, facts: dict,
                  conditions: list[dict], at: str | None = None) -> dict:
    """Assemble a runs-manifest row from the registry entry + per-run facts.

    The registry supplies ``run_id`` and the mutable ``directory_path``; ``facts``
    (one entry of ``results/run-facts.json``) supplies the irreducibly-human fields
    (corpus, GT, scope, study tags, aliases, headline pointer). ``run_type`` is
    DERIVED from the conditions' architectures when conditions are available (a
    single family, or ``mixed`` when they span families — gold-standard-v2 has both
    consensus and proposer-verifier conditions); it is ``null`` for runs whose
    per-run conditions have not yet been extracted (Phase 3b). Provenance anchors
    on the facts file, the scope bounds, and a representative pass meta if present.
    """
    run_dir = REPO_ROOT / directory_path
    archs = {c["architecture"] for c in conditions}
    run_type = (next(iter(archs)) if len(archs) == 1 else "mixed") if conditions else None

    sources = ["results/run-facts.json"]
    bounds_path = (facts.get("scope") or {}).get("bounds_path")
    if bounds_path:
        sources.append(bounds_path)
    proposer_dir = run_dir / "proposer"
    if proposer_dir.exists():
        metas = sorted(proposer_dir.rglob("*.meta.json"))
        if metas:
            sources.append(_repo_rel(metas[0]))

    prr = run_dir / "post_run_report.md"
    return {
        "run_id": run_id,
        "directory_path": directory_path,
        "primary_hypothesis": facts.get("primary_hypothesis"),
        "also_informs": facts.get("also_informs", []),
        "purpose": facts.get("purpose"),
        "run_type": run_type,
        "tile_size_px": facts["tile_size_px"],
        "corpus": facts["corpus"],
        "gt_reference": facts["gt_reference"],
        "scope": facts["scope"],
        "headline_condition_id": facts.get("headline_condition_id"),
        "headline_rationale": facts.get("headline_rationale"),
        "post_run_report_path": _repo_rel(prr) if prr.exists() else None,
        "working_notes_obs": facts.get("working_notes_obs", []),
        "historical_aliases": facts.get("historical_aliases", []),
        "provenance": build_provenance(sources, at),
    }


def load_run_registry(path: Path | None = None) -> dict:
    """Load the hand-authored run registry — the generator's INPUT (decision B1).

    The registry is the source-of-truth enumeration of runs (``run_id`` →
    ``directory_path``); the generator READS it and never synthesises it. Returns
    the whole manifest object (envelope + ``registry`` list) so the caller can both
    iterate the runs and re-render the Markdown view.
    """
    return _load_json(path or REPO_ROOT / "results" / "run-registry.json")


def load_run_facts(path: Path | None = None) -> dict[str, dict]:
    """Load the per-run human-authored facts — the generator's other INPUT.

    Returns a ``{run_id: facts}`` mapping. Each entry carries the irreducibly-human
    fields (corpus, gt_reference, scope, study tags, historical aliases, headline
    pointer). Underscore-prefixed annotations (the human provenance for the scope
    choice) are retained in the file but ignored by the extractor.
    """
    return _load_json(path or REPO_ROOT / "results" / "run-facts.json").get("facts", {})


def load_run_conditions(path: Path | None = None) -> dict[str, dict]:
    """Load the per-run decomposition sidecar — the generator's third INPUT (3b, Q3).

    Returns a ``{run_id: decomposition}`` mapping, where each decomposition carries
    ``proposer_pools`` (dir→modality), ``verifier_passes`` (dir→modality), and
    ``conditions`` (the evaluable scored-result specs). Kept separate from
    ``run-facts.json`` so the high-churn decomposition stays isolated from the locked
    run-level facts (decision Q3). A run absent from the sidecar yields no
    conditions/passes yet (its ``run_type`` stays ``null``).
    """
    return _load_json(
        path or REPO_ROOT / "results" / "run-conditions.json"
    ).get("decomposition", {})


def load_run_analyses(path: Path | None = None) -> list[dict]:
    """Load the hand-authored ANALYSIS specs — the generator's 3c INPUT (sub-step 3c).

    An analysis is a comparison/finding OVER conditions (a leaderboard, a hypothesis
    test, a sweep). The sidecar ``results/run-analyses.json`` holds one spec per
    analysis; the generator validates them, attaches provenance, and emits
    ``results/analyses-manifest.json``. The manifest is **hybrid**: the spec carries
    the machine-fillable keys (``analysis_id``, ``type``, ``conditions_compared``,
    ``output_path``) and any human-authored fields (``outcome``, ``hypothesis_refs``,
    ``preregistered`` linkage, ``tie_set``, …), which may be null until authored per
    the schema's lenient back-fill. Returns ``[]`` when the sidecar is absent (the
    expected state before 3c authoring begins).
    """
    p = path or REPO_ROOT / "results" / "run-analyses.json"
    if not p.exists():
        return []
    return _load_json(p).get("analyses", [])


#: Machine-fillable keys an analysis spec must carry; the human-authored fields are
#: all nullable (schema lenient back-fill), so a stub validates before a human writes
#: the finding / prereg linkage.
_REQUIRED_ANALYSIS_KEYS: tuple[str, ...] = (
    "analysis_id", "type", "conditions_compared", "output_path",
)


def _require_analysis_keys(spec: dict) -> None:
    """Validate an analysis spec carries the required machine-fillable keys.

    Raises a descriptive ``ValueError`` naming the offending analysis so a sidecar
    typo fails clearly rather than as an opaque ``KeyError`` mid-build.
    """
    missing = [k for k in _REQUIRED_ANALYSIS_KEYS if k not in spec]
    if missing:
        raise ValueError(
            f"analysis spec (analysis_id={spec.get('analysis_id', '?')}) "
            f"is missing required key(s): {', '.join(missing)}"
        )


def build_analyses(specs: list[dict], at: str | None = None) -> list[dict]:
    """Build analyses-manifest rows from the hand-authored specs.

    Each spec's schema-allowed fields are copied through (human-authored fields kept
    verbatim — the generator never invents a finding); array fields default to ``[]``
    and the optional human fields to ``null``. Provenance anchors on the sidecar and,
    when it exists on disk, the analysis ``output_path`` artefact. ``additionalProperties``
    is ``false`` on the emitted row, so only the known keys are copied (a sidecar
    ``_note`` is ignored).

    Args:
        specs: the ``analyses`` list from :func:`load_run_analyses`.
        at: ISO timestamp stamped on every row's provenance.

    Returns:
        Analysis rows conforming to the analyses-manifest item schema.
    """
    rows: list[dict] = []
    for spec in specs:
        _require_analysis_keys(spec)
        out_path = spec["output_path"]
        sources = ["results/run-analyses.json"]
        if out_path and (REPO_ROOT / out_path).exists():
            sources.append(out_path)
        rows.append({
            "analysis_id": spec["analysis_id"],
            "type": spec["type"],
            "conditions_compared": spec["conditions_compared"],
            "hypothesis_refs": spec.get("hypothesis_refs", []),
            "preregistered": spec.get("preregistered"),
            "deviations": spec.get("deviations", []),
            "predicted_outcome": spec.get("predicted_outcome"),
            "tie_set": spec.get("tie_set", []),
            "outcome": spec.get("outcome"),
            "paper_section": spec.get("paper_section"),
            "output_path": out_path,
            "working_notes_obs": spec.get("working_notes_obs", []),
            "manually_verified_at": spec.get("manually_verified_at"),
            "provenance": build_provenance(sources, at),
        })
    return rows


def build_extraction_context(entry: dict, run_facts: dict, decomposition: dict) -> dict:
    """Merge a run's three input sources into the single dict the extractors read.

    :func:`extract_passes` and :func:`extract_conditions` consume one dict carrying
    identity (``run_id``, ``directory_path``), the nominal ``scope`` (for matching an
    evaluation to the run's bounds), and the decomposition hints (``proposer_pools``,
    ``verifier_passes``, ``conditions``). Those come from, respectively: the registry
    entry (identity/location), the per-run facts (scope), and the run-conditions
    sidecar (decomposition). Assembling them here means no field is duplicated across
    the input files.
    """
    return {
        "run_id": entry["run_id"],
        "directory_path": entry["directory_path"],
        "scope": run_facts.get("scope", {}),
        "proposer_pools": decomposition.get("proposer_pools", {}),
        "verifier_passes": decomposition.get("verifier_passes", {}),
        "conditions": decomposition.get("conditions", []),
    }


def extraction_context(
    run_id: str,
    registry_obj: dict | None = None,
    facts: dict[str, dict] | None = None,
    decomposition: dict[str, dict] | None = None,
) -> dict:
    """Convenience: build one run's extraction context, loading inputs lazily.

    A thin wrapper over :func:`build_extraction_context` that resolves the run's
    registry entry by ``run_id`` and pulls its facts/decomposition. The three inputs
    are loaded from disk when not supplied (so a caller — e.g. a test — can ask for a
    single run's context with just its id). A run with no sidecar entry returns a
    context with empty decomposition (zero passes/conditions extracted).

    Raises:
        KeyError: if ``run_id`` is not in the run registry.
    """
    registry_obj = registry_obj if registry_obj is not None else load_run_registry()
    facts = facts if facts is not None else load_run_facts()
    decomposition = decomposition if decomposition is not None else load_run_conditions()
    entry = next(
        (e for e in registry_obj.get("registry", []) if e["run_id"] == run_id), None
    )
    if entry is None:
        raise KeyError(f"run '{run_id}' is not in the run registry")
    return build_extraction_context(entry, facts.get(run_id, {}), decomposition.get(run_id, {}))


def drift_check(
    registry: list[dict],
    facts: dict[str, dict],
    conditions: dict[str, dict] | None = None,
) -> list[str]:
    """Warn when the input files disagree on the run set (the B1 guard, extended to 3b).

    A registry run with no facts entry cannot produce a complete run row; a facts
    entry with no registry row will never be emitted. When ``conditions`` (the
    decomposition sidecar) is supplied, also flags any decomposed run that is missing
    from the registry or the facts — an *orphan* decomposition that would never emit.
    The reverse is intentionally NOT flagged: a registry run with no decomposition is
    the expected mid-fan-out state (it simply has no conditions/passes yet). An empty
    list means the inputs are in sync.
    """
    reg_ids = {e["run_id"] for e in registry}
    fact_ids = set(facts)
    warnings = [f"registry run '{rid}' has NO facts entry" for rid in sorted(reg_ids - fact_ids)]
    warnings += [f"facts run '{rid}' is NOT in the registry" for rid in sorted(fact_ids - reg_ids)]
    if conditions is not None:
        cond_ids = set(conditions)
        warnings += [
            f"run-conditions run '{rid}' is NOT in the registry"
            for rid in sorted(cond_ids - reg_ids)
        ]
        warnings += [
            f"run-conditions run '{rid}' has NO facts entry"
            for rid in sorted(cond_ids - fact_ids)
        ]
    return warnings


# --------------------------------------------------------------------------- #
# Manifest assembly, whole-manifest validation, and rendering
# --------------------------------------------------------------------------- #

#: Where each manifest's JSON source-of-truth is written (the .md sibling is
#: rendered alongside). Per the schema-design brief, manifests live in results/.
MANIFEST_FILES: dict[str, str] = {
    "runs": "results/runs-manifest.json",
    "conditions": "results/conditions-manifest.json",
    "passes": "results/passes-manifest.json",
    "analyses": "results/analyses-manifest.json",
    "run-registry": "results/run-registry.json",
}


def _array_key(manifest: str) -> str:
    """Return a manifest schema's top-level array property name (runs/passes/…)."""
    contents = json.loads((SCHEMA_DIR / MANIFEST_SCHEMAS[manifest]).read_text(encoding="utf-8"))
    for name, prop in contents.get("properties", {}).items():
        if isinstance(prop, dict) and prop.get("type") == "array":
            return name
    raise ValueError(f"no top-level array property in {manifest} schema")


def validate_manifest(manifest: str, obj: dict, registry: Registry) -> list[str]:
    """Validate a whole assembled manifest object against its top-level schema."""
    validator = jsonschema.Draft202012Validator(
        {"$ref": _schema_id(manifest)},
        registry=registry,
        format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER,
    )
    errors = sorted(validator.iter_errors(obj), key=lambda e: list(e.path))
    return [f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}" for e in errors]


def assemble_manifest(manifest: str, rows: list[dict], at: str) -> dict:
    """Wrap extracted rows in the manifest envelope.

    Only includes the top-level fields the schema actually declares — the
    run-registry schema, unlike runs/conditions/passes, has no
    ``generator_version`` and is ``additionalProperties: false``, so the envelope
    is built from the schema's own properties rather than a fixed shape.
    """
    props = json.loads(
        (SCHEMA_DIR / MANIFEST_SCHEMAS[manifest]).read_text(encoding="utf-8")
    ).get("properties", {})
    obj: dict[str, Any] = {"schema_version": SCHEMA_VERSION}
    if "generated_at" in props:
        obj["generated_at"] = at
    if "generator_version" in props:
        obj["generator_version"] = GENERATOR_VERSION
    obj[_array_key(manifest)] = rows
    return obj


def _md_table(headers: list[str], rows: list[list]) -> str:
    """Render a GitHub-flavoured Markdown table."""
    lines = ["| " + " | ".join(headers) + " |",
             "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        lines.append("| " + " | ".join("—" if c is None else str(c) for c in r) + " |")
    return "\n".join(lines)


def _coverage_note(manifest: str, n_rows: int) -> str:
    """Human-readable coverage line for a manifest's rendered Markdown header."""
    return {
        "runs": f"all {n_rows} runs (run-level facts; conditions/passes added as 3b batches land)",
        "conditions": f"{n_rows} condition(s) across the decomposed runs (sub-step 3b in progress)",
        "passes": f"{n_rows} pass(es) across the decomposed runs (sub-step 3b in progress)",
        "analyses": f"{n_rows} analysis(es) over conditions (sub-step 3c; hybrid human-authored)",
        "run-registry": f"all {n_rows} runs (hand-verified input)",
    }.get(manifest, f"{n_rows} row(s)")


def render_manifest(manifest: str, obj: dict, json_rel: str) -> str:
    """Render a human-readable Markdown view of a manifest (do-not-edit)."""
    rows = obj[_array_key(manifest)]
    titles = {
        "runs": "Runs manifest", "conditions": "Conditions manifest",
        "passes": "Passes manifest", "analyses": "Analyses manifest",
        "run-registry": "Run registry",
    }
    head = (
        f"<!-- GENERATED FILE — DO NOT EDIT. Rendered from {json_rel} by "
        f"scripts/generate_post_run_report.py v{GENERATOR_VERSION}. Edit the "
        f"source-of-truth files and regenerate. -->\n\n"
        f"# {titles[manifest]}\n\n"
        f"> Generated {obj['generated_at']} · {len(rows)} row(s) · schema "
        f"v{obj['schema_version']}.\n>\n"
        f"> **Coverage**: {_coverage_note(manifest, len(rows))}.\n\n"
    )
    if manifest == "runs":
        table = _md_table(
            ["run_id", "type", "tile_px", "corpus", "gt", "scope", "headline"],
            [[r["run_id"], r["run_type"], r["tile_size_px"], r["corpus"], r["gt_reference"],
              r["scope"]["test_set_id"], r["headline_condition_id"]] for r in rows])
    elif manifest == "conditions":
        table = _md_table(
            ["condition_id", "arch", "agg", "vote", "n", "F1@20m", "MCC", "n_det"],
            [[r["condition_id"], r["architecture"], r["aggregation"], r["vote_threshold"],
              r["n_passes"], r["metrics"]["per_buffer"].get("20", {}).get("f1"),
              r["metrics"]["tile_classification"]["mcc"], r["n_detections"]] for r in rows])
    elif manifest == "passes":
        table = _md_table(
            ["pass_id", "model", "modality", "think", "T", "status", "tiles", "cost_usd"],
            [[r["pass_id"], r["model_used"], r["modality"], r["thinking_level"], r["temperature"],
              r["status"], r["n_tiles_processed"], r["cost_usd"]] for r in rows])
    elif manifest == "analyses":
        table = _md_table(
            ["analysis_id", "type", "#conditions", "preregistered", "paper_section", "outcome"],
            [[r["analysis_id"], r["type"], len(r["conditions_compared"]),
              r["preregistered"], r["paper_section"], r["outcome"]] for r in rows])
    else:  # run-registry
        table = _md_table(
            ["run_id", "directory_path", "status"],
            # status is schema-optional (default "active"); don't assume it's present
            [[r["run_id"], r["directory_path"], r.get("status", "active")] for r in rows])
    return head + table + "\n"


def write_manifests(bundles: dict[str, list[dict]], at: str, registry: Registry) -> dict[str, tuple]:
    """Validate and write each manifest (JSON + rendered MD); never write an invalid one.

    Args:
        bundles: manifest name → its extracted rows.
        at: shared generation timestamp.
        registry: schema registry.

    Returns:
        manifest → (n_rows, errors, json_rel) — errors empty on success.
    """
    out: dict[str, tuple] = {}
    for manifest, rows in bundles.items():
        obj = assemble_manifest(manifest, rows, at)
        errors = validate_manifest(manifest, obj, registry)
        json_rel = MANIFEST_FILES[manifest]
        if not errors:
            json_path = REPO_ROOT / json_rel
            json_path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
            json_path.with_suffix(".md").write_text(
                render_manifest(manifest, obj, json_rel), encoding="utf-8")
        out[manifest] = (len(rows), errors, json_rel)
    return out


# --------------------------------------------------------------------------- #
# Self-test (proves the harness round-trips before any extractor is wired in)
# --------------------------------------------------------------------------- #


def _self_test() -> int:
    """Validate that all schemas load and a minimal hand-written row round-trips.

    Returns a process exit code (0 = pass).
    """
    registry, contents_by_id = load_schema_registry()
    print(f"Loaded {len(contents_by_id)} schema files from {SCHEMA_DIR.relative_to(REPO_ROOT)}")
    for manifest in MANIFEST_SCHEMAS:
        print(f"  {manifest:13s} → row def '$defs/{_row_def_name(manifest)}'")

    # A minimal valid run-registry entry exercises the row validator + the
    # slug pattern; a deliberately invalid one proves errors are caught.
    good_entry = {"run_id": "gold-standard-v2", "directory_path": "outputs/gs/gold-standard-v2"}
    bad_entry = {"run_id": "Gold/Standard", "directory_path": "outputs/gs/gold-standard-v2"}

    good_errors = validate_row("run-registry", good_entry, registry)
    bad_errors = validate_row("run-registry", bad_entry, registry)

    print("\nSelf-test:")
    print(f"  valid registry entry  → {len(good_errors)} errors (expect 0)")
    print(f"  invalid run_id slug    → {len(bad_errors)} errors (expect ≥1): {bad_errors or 'NONE'}")

    # A provenance object must validate against the common-defs sub-schema by
    # validating a full run row that embeds it would be heavier; here we confirm
    # the builder produces the required keys.
    prov = build_provenance(["docs/manifest-schemas/run-registry.schema.json"])
    prov_ok = set(prov) == {"source_files", "last_extracted_at", "extractor_version"}
    print(f"  provenance builder keys → {'ok' if prov_ok else 'WRONG: ' + str(set(prov))}")

    passed = not good_errors and bool(bad_errors) and prov_ok
    print(f"\n{'PASS' if passed else 'FAIL'} — validation harness {'round-trips' if passed else 'is broken'}")
    return 0 if passed else 1


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def build_arg_parser() -> argparse.ArgumentParser:
    """Construct the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Generate experimental manifests from source-of-truth files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Validate that all schemas load and the validation harness round-trips, then exit.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Build every run in results/run-registry.json: a run-level row for each, plus "
             "conditions/passes for runs decomposed in results/run-conditions.json.",
    )
    parser.add_argument(
        "--run",
        metavar="RUN_ID",
        help="Build just the named run (filters --all to one run_id; for inspection).",
    )
    parser.add_argument(
        "--draft-run",
        metavar="RUN_ID",
        help="Propose a decomposition skeleton for one run (proposer pools, verifier passes, "
             "and scored-eval condition candidates) as JSON on stdout, for human verification "
             "before pasting into results/run-conditions.json. Writes nothing.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the full extracted rows as JSON (extract + validate, write nothing).",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write the validated manifests (JSON + rendered MD) to results/. Refuses to write "
             "if any row or manifest fails validation. Never rewrites run-registry.json (the "
             "hand-authored input) — only its rendered .md view.",
    )
    return parser


def build_manifests(at: str, only: str | None = None) -> tuple:
    """Build all manifest rows from the registry + facts + decomposition INPUTS.

    Iterates ``results/run-registry.json`` (the hand-authored run list); for each
    run builds a runs-manifest row from its ``results/run-facts.json`` entry. A run
    that has a decomposition entry in ``results/run-conditions.json`` also yields
    conditions + passes (extracted from its source files), which in turn fix that
    run's derived ``run_type``; a run not yet decomposed gets a run row only (its
    ``run_type`` stays ``null``).

    Args:
        at: shared extraction timestamp stamped on every provenance block.
        only: if set, restrict the build to this single ``run_id``.

    Returns:
        ``(registry_obj, run_rows, conditions, passes, analyses, drift_warnings)``.
    """
    registry_obj = load_run_registry()
    facts = load_run_facts()
    decomposition = load_run_conditions()
    entries = registry_obj.get("registry", [])
    warnings = drift_check(entries, facts, decomposition)

    run_rows: list[dict] = []
    conditions_all: list[dict] = []
    passes_all: list[dict] = []
    for entry in entries:
        run_id, directory_path = entry["run_id"], entry["directory_path"]
        if only and run_id != only:
            continue
        run_facts = facts.get(run_id, {})
        conditions: list[dict] = []
        if run_id in decomposition:
            # Decomposed runs: the extractors read the run-conditions sidecar (which
            # scored results are conditions, how passes enumerate) merged with the
            # registry entry + facts. Runs absent from the sidecar are not yet
            # decomposed and emit a run row only.
            ctx = build_extraction_context(entry, run_facts, decomposition[run_id])
            passes_all.extend(extract_passes(ctx, at))
            conditions = extract_conditions(ctx, at)
            conditions_all.extend(conditions)
        run_rows.append(build_run_row(run_id, directory_path, run_facts, conditions, at))

    # Analyses (sub-step 3c) are global — comparisons OVER conditions, not run-scoped.
    analyses_all = build_analyses(load_run_analyses(), at)
    # FK guard: warn on any conditions_compared id absent from the built conditions.
    # Only meaningful on a full build (a --run filter yields a partial condition set,
    # which would mis-flag cross-run analyses), so skip the check when filtering.
    if only is None:
        known = {c["condition_id"] for c in conditions_all}
        for a in analyses_all:
            for cid in a["conditions_compared"]:
                if cid not in known:
                    warnings.append(
                        f"analysis '{a['analysis_id']}' references unknown "
                        f"condition_id '{cid}'"
                    )
    return registry_obj, run_rows, conditions_all, passes_all, analyses_all, warnings


# --------------------------------------------------------------------------- #
# Auto-drafter — the "I-draft" half of the I-draft-you-verify decomposition
# --------------------------------------------------------------------------- #


def _slug(name: str) -> str:
    """Slug-safe label (keeps the pass_id / condition_id middle-segment alphabet).

    Lowercases and replaces any character outside ``[a-z0-9._-]`` (notably the path
    separator) with a hyphen, so a nested directory path becomes a unique label.
    """
    return "".join(ch if (ch.isalnum() or ch in "._-") else "-" for ch in name.lower())


def _infer_modality(rel_path: str) -> str | None:
    """Best-effort modality guess from a pool/verifier path (``image`` / ``text``).

    A keyword scan only — the drafter's output is a PROPOSAL the human verifies, so
    an unguessable case returns ``None`` for a human to fill rather than guessing.
    """
    low = rel_path.lower()
    if "image" in low:
        return "image"
    if "text" in low:
        return "text"
    return None


def _add_unique(target: dict[str, dict], label: str, value: dict, kind: str) -> None:
    """Insert ``label → value``, warning (not silently dropping) on a slug collision.

    Two distinct directory paths can slug to the same label; a plain dict assignment
    would silently overwrite one, which is exactly the silent drop the drafter must
    avoid. The first entry is kept and the clash is reported to stderr (the drafter's
    JSON goes to stdout, so the warning does not corrupt it).
    """
    if label in target:
        print(
            f"WARNING: draft_run: {kind} label '{label}' collides with an existing "
            f"entry (path {value['path']}); keeping the first — rename during verification.",
            file=sys.stderr,
        )
        return
    target[label] = value


def draft_run(run_id: str) -> dict:
    """Propose a decomposition skeleton for one run (the I-draft half of 3b).

    Walks the run's directory to enumerate **proposer pools** (dirs whose ``run_N``
    children hold ``*.meta.json``) and **verifier passes** (dirs holding a
    ``run.meta.json``), and lists every evaluation that scored a detection file under
    the run as a **condition candidate**. This is a PROPOSAL for human verification,
    never written into the sidecar automatically: modality is keyword-guessed, the
    pass/condition grain is the human's call (Q2: vote-threshold sweeps are
    conditions, probability-threshold sweeps collapse to one operating point), and
    cross-run conditions (GAP-6) are not detected here. Labels are derived from the
    directory path and are expected to be renamed during verification.

    Args:
        run_id: a run in ``results/run-registry.json``.

    Returns:
        A dict with the proposed ``proposer_pools`` / ``verifier_passes`` and a
        ``condition_candidates`` list (each: detections, eval_path, bounds,
        n_detections, has_mcc, buffers).

    Raises:
        KeyError: if ``run_id`` is not in the registry.
    """
    registry_obj = load_run_registry()
    entry = next(
        (e for e in registry_obj.get("registry", []) if e["run_id"] == run_id), None)
    if entry is None:
        raise KeyError(f"run '{run_id}' is not in the run registry")
    run_dir = REPO_ROOT / entry["directory_path"]

    proposer_pools: dict[str, dict] = {}
    verifier_passes: dict[str, dict] = {}
    seen_pool_dirs: set = set()
    for meta_path in sorted(run_dir.rglob("*.meta.json")):
        parent = meta_path.parent
        parts = parent.name.split("_", 1)
        if parts[0] == "run" and len(parts) == 2 and parts[1].isdigit():
            # proposer pass: <pool>/run_N/<*.meta.json> → the pool is run_N's parent
            pool_dir = parent.parent
            if pool_dir in seen_pool_dirs:
                continue
            seen_pool_dirs.add(pool_dir)
            rel = pool_dir.relative_to(run_dir).as_posix()
            _add_unique(proposer_pools, _slug(rel),
                        {"modality": _infer_modality(rel), "path": rel}, "proposer pool")
        elif meta_path.name == "run.meta.json":
            # verifier pass: <vdir>/run.meta.json (vdir may be nested several levels)
            rel = parent.relative_to(run_dir).as_posix()
            _add_unique(verifier_passes, _slug(rel),
                        {"modality": _infer_modality(rel), "path": rel}, "verifier pass")

    # condition candidates: every indexed eval that scored a detection under this run
    dir_prefix = _normalise_detections_path(entry["directory_path"].rstrip("/") + "/")
    candidates: list[dict] = []
    for det_path, evals in sorted(_build_eval_index().items()):
        if not det_path.startswith(dir_prefix):
            continue
        for eval_rel, summary, bounds in evals:
            candidates.append({
                "detections": det_path,
                "eval_path": eval_rel,
                "bounds": bounds,
                "n_detections": summary.get("n_detections"),
                "has_mcc": bool(summary.get("tile_classification")),
                "buffers": [b.get("buffer_metres") for b in (summary.get("buffers") or [])],
            })

    return {
        "run_id": run_id,
        "directory_path": entry["directory_path"],
        "proposed_decomposition": {
            "proposer_pools": proposer_pools,
            "verifier_passes": verifier_passes,
            "conditions": [],  # author from condition_candidates per the Q2 grain
        },
        "condition_candidates": candidates,
    }


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    args = build_arg_parser().parse_args(argv)

    if args.self_test:
        return _self_test()

    if args.draft_run:
        try:
            print(json.dumps(draft_run(args.draft_run), indent=2))
        except KeyError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0

    if args.all or args.run:
        schema_reg, _ = load_schema_registry()
        at = utc_now_iso()
        registry_obj, run_rows, conditions, passes, analyses, warnings = build_manifests(
            at, only=args.run)

        if args.run and not run_rows:
            print(f"No run '{args.run}' in results/run-registry.json.", file=sys.stderr)
            return 2

        if warnings:
            print("=== registry ↔ facts drift ===")
            for w in warnings:
                print(f"  WARN: {w}")
            print()

        all_valid = True

        print(f"=== {len(run_rows)} run rows ===")
        for r in run_rows:
            errors = validate_row("runs", r, schema_reg)
            all_valid = all_valid and not errors
            print(
                f"  [{'ok ' if not errors else 'BAD'}] {r['run_id']:34s} "
                f"type={str(r['run_type']):16s} {str(r['tile_size_px']):>3}px "
                f"{r['corpus']:8s} {r['gt_reference']:7s} {r['scope']['test_set_id']}"
            )
            for e in errors:
                print(f"        - {e}")

        if conditions:
            bad = [c for c in conditions if validate_row("conditions", c, schema_reg)]
            all_valid = all_valid and not bad
            print(f"\n=== {len(conditions)} conditions — "
                  f"{len(conditions) - len(bad)} valid ===")
            for c in bad:
                for e in validate_row("conditions", c, schema_reg):
                    print(f"  [BAD] {c['condition_id']}: {e}")

        if passes:
            bad = [p for p in passes if validate_row("passes", p, schema_reg)]
            all_valid = all_valid and not bad
            print(f"=== {len(passes)} passes — "
                  f"{len(passes) - len(bad)} valid ===")
            for p in bad:
                for e in validate_row("passes", p, schema_reg):
                    print(f"  [BAD] {p['pass_id']}: {e}")

        if analyses:
            bad = [a for a in analyses if validate_row("analyses", a, schema_reg)]
            all_valid = all_valid and not bad
            print(f"=== {len(analyses)} analyses — "
                  f"{len(analyses) - len(bad)} valid ===")
            for a in bad:
                for e in validate_row("analyses", a, schema_reg):
                    print(f"  [BAD] {a['analysis_id']}: {e}")

        print(
            f"\n{'ALL VALID' if all_valid else 'VALIDATION FAILED'} "
            f"({len(run_rows)} runs + {len(conditions)} conditions + {len(passes)} passes "
            f"+ {len(analyses)} analyses vs schemas)"
        )

        if args.dry_run:
            for name, payload in [("runs", run_rows), ("conditions", conditions),
                                  ("passes", passes), ("analyses", analyses)]:
                print(f"\n--- {name} ---")
                print(json.dumps(payload, indent=2))

        if args.write:
            if not all_valid:
                print("\nRefusing to write: validation failed above.", file=sys.stderr)
                return 1
            if args.run:
                print("\nRefusing to write a single-run subset; use --all to write manifests.",
                      file=sys.stderr)
                return 1
            bundles = {"runs": run_rows, "conditions": conditions, "passes": passes,
                       "analyses": analyses}
            written = write_manifests(bundles, at, schema_reg)
            # The registry JSON is the hand-authored INPUT — never rewritten; only
            # its Markdown view is regenerated from it (read → render).
            reg_path = REPO_ROOT / MANIFEST_FILES["run-registry"]
            reg_path.with_suffix(".md").write_text(
                render_manifest("run-registry", registry_obj, MANIFEST_FILES["run-registry"]),
                encoding="utf-8")
            print("\n=== wrote manifests ===")
            for manifest, (n, errors, json_rel) in written.items():
                status = f"{n} row(s) → {json_rel} (+ .md)" if not errors else f"NOT WRITTEN: {errors}"
                print(f"  {manifest:13s} {status}")
                all_valid = all_valid and not errors
            print(f"  {'run-registry':13s} {len(registry_obj['registry'])} row(s) → "
                  f"{MANIFEST_FILES['run-registry']} (.md only; JSON is the input)")

        return 0 if all_valid else 1

    build_arg_parser().print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
