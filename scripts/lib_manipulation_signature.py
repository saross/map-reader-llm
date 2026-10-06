"""
The manipulation signature: what one pass meta says reached the model.

Why this module exists
----------------------
``scripts/check_manipulation.py`` (tracker W6.1) refuses an analysis whose
arms differ in configuration but not in what was transmitted. Its per-meta
field extraction and its signature were first borrowed from the 2026-10-05
check's scratch scripts: the gate loaded
``reports/manipulation-check-2026-10-05-scripts/harvest.py`` at import and
copied four functions from ``arms.py`` beside it. A production gate that
executes a report's scratch script breaks the moment the report directory
is archived, and its tests break with it (PR #24 review, finding 4). This
module holds both pieces in ``scripts/``. The report scripts are left as
they are: they are the record of what the 2026-10-05 check ran.

Provenance of the copies
------------------------
- :func:`harvest_meta` (with :func:`_dig` and :func:`_stats`) is
  ``harvest()`` from ``reports/manipulation-check-2026-10-05-scripts/
  harvest.py`` (commit ``97d2afaf1``, 2026-10-05), with three changes:
  reading the file is split into :func:`harvest`, so a caller that already
  holds the parsed meta does not parse it again (PR #24 review, finding 9:
  the gate parsed each meta up to three times); the record gains
  ``max_output_tokens`` and ``dispatched_ids``, the two fields the gate
  re-read the file for; and the reader is :func:`load_meta`, which reads a
  gzipped meta (finding 6).
- :func:`signature`, :func:`model_of_record` and :func:`eff_temp` are
  ``signature()``, ``_model_of_record()`` and ``eff_temp()`` from
  ``arms.py`` there (same commit), as extended in ``check_manipulation.py``
  (commit ``61d8e0dca``) by ``max_output_tokens`` and ``inputs``.
  :func:`is_verifier_record` is ``signature()``'s inline verifier test,
  named.
- :func:`dispatched_ids`, :func:`inputs_fingerprint`,
  :data:`SIGNATURE_VERSION` and :data:`SIGNATURE_FIELDS` move here from
  ``check_manipulation.py`` (commit ``61d8e0dca``) unchanged, since they
  define the signature's ``inputs`` field.

The signature definition (``manipulation-signature/1``) and its rationale
are documented in ``check_manipulation.py``'s module docstring, which
map-reader-bench shares.

Usage
-----
    from scripts.lib_manipulation_signature import harvest, signature

    record = harvest("outputs/run/pool/run_1/detections-x.meta.json")
    if "error" not in record:
        print(signature(record))
"""

from __future__ import annotations

import hashlib
import json
import os
import statistics
from pathlib import Path
from typing import Any

from scripts.derive_condition_modality import load_meta_json

#: The signature definition's version (see ``check_manipulation.py``).
SIGNATURE_VERSION = "manipulation-signature/1"

#: The fields of a transmitted signature, in order.
SIGNATURE_FIELDS = ("stage", "model", "temperature_eff", "thinking", "sys_hash",
                    "examples_sent", "tile_size", "max_output_tokens", "inputs")


# ── reading a meta ───────────────────────────────────────────────────────

def load_meta(path: str | Path) -> Any:
    """Parse one ``*.meta.json`` file, gzipped or not.

    The reading is ``derive_condition_modality.load_meta_json``, the gzip
    handling its ``read_meta`` already had. The 2026-10-05 harvester used a
    plain ``open``, so a gzipped meta (one registered pass cites
    ``run_3/....meta.json.gz``) came back as an error record and its pass
    was silently dropped from every arm's signature (PR #24 review,
    finding 6).

    Args:
        path: The meta's path.

    Returns:
        The parsed JSON value (a dict for any meta the pipeline wrote).

    Raises:
        OSError: The file cannot be read, or is a corrupt gzip stream.
        EOFError: The gzip stream is truncated.
        ValueError: The content is not valid UTF-8 JSON.
    """
    return load_meta_json(path)


# ── the harvester (copied from harvest.py; see the module docstring) ──────

def _dig(d: Any, *keys: str) -> Any:
    """Return the first non-None value found at any of the dotted keys.

    Args:
        d: A parsed JSON document.
        *keys: Dotted key paths, tried in order.

    Returns:
        The first value present and not None, else None.

    Examples:
        >>> _dig({"a": {"b": 1}}, "a.c", "a.b")
        1
    """
    for k in keys:
        cur = d
        ok = True
        for part in k.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                ok = False
                break
        if ok and cur is not None:
            return cur
    return None


def _stats(vals: list[Any]) -> dict[str, Any] | None:
    """Summary statistics over the numeric values of a list.

    Args:
        vals: Values; non-numeric ones are ignored.

    Returns:
        ``{"n", "min", "median", "max", "n_distinct"}``, or None when no
        value is numeric.

    Examples:
        >>> _stats([3, None, 1, 3])["median"]
        3
    """
    vals = [v for v in vals if isinstance(v, (int, float))]
    if not vals:
        return None
    return {
        "n": len(vals),
        "min": min(vals),
        "median": statistics.median(vals),
        "max": max(vals),
        "n_distinct": len(set(vals)),
    }


def dispatched_ids(meta: dict[str, Any]) -> frozenset[str]:
    """The ids of every item a pass dispatched (its tiles, or its candidates).

    Args:
        meta: A parsed ``*.meta.json``.

    Returns:
        ``execution_stats`` ``completed_items`` plus ``failed_items`` ids.

    Examples:
        >>> sorted(dispatched_ids({"execution_stats": {"completed_items": ["b", "a"],
        ...     "failed_items": [{"item_id": "c"}]}}))
        ['a', 'b', 'c']
    """
    stats = meta.get("execution_stats") or {}
    ids = {str(i) for i in stats.get("completed_items") or [] if i is not None}
    for f in stats.get("failed_items") or []:
        item = f.get("item_id") if isinstance(f, dict) else f
        if item is not None:
            ids.add(str(item))
    return frozenset(ids)


def harvest_meta(m: Any, path: str) -> dict[str, Any]:
    """Extract the signature fields of one parsed meta.

    Args:
        m: The parsed meta.
        path: The meta's path (recorded, and sized for ``bytes``).

    Returns:
        The harvested record; ``error`` is set when ``m`` is not a dict.
        Beyond the 2026-10-05 harvester's fields: ``max_output_tokens``
        (from ``configuration`` or its snapshot) and ``dispatched_ids``
        (:func:`dispatched_ids`, sorted).
    """
    rec: dict = {"path": path}
    if not isinstance(m, dict):
        rec["error"] = "not a dict"
        return rec
    cfg = m.get("configuration") or {}
    snap = cfg.get("full_config_snapshot") or {}
    env = m.get("environment") or {}
    rec["script"] = env.get("script")
    rec["git_commit"] = env.get("git_commit")
    rec["start"] = _dig(m, "timestamp.start")
    rec["version"] = cfg.get("version") or snap.get("version")
    rec["model"] = cfg.get("model")
    rec["snap_model"] = snap.get("model")
    rec["instruction_file"] = cfg.get("instruction_file") or snap.get("instruction_file")
    rec["sys_hash"] = cfg.get("system_instruction_hash")
    rec["library_hash"] = cfg.get("library_hash")
    rec["temperature"] = cfg.get("temperature")
    rec["temperature_effective"] = cfg.get("temperature_effective")
    rec["snap_temperature"] = snap.get("temperature")
    rec["thinking_level"] = cfg.get("thinking_level")
    rec["snap_thinking_level"] = snap.get("thinking_level")
    rec["tile_size"] = cfg.get("tile_size")
    rec["cfg_include_example_images"] = cfg.get("include_example_images")
    # Raw snapshot value: absent means the runner default (True)
    rec["snap_include_example_images"] = snap.get(
        "include_example_images", "ABSENT"
    ) if snap else "NO_SNAPSHOT"
    rec["example_count"] = cfg.get("example_count")
    rec["ordering_override"] = cfg.get("ordering_override") or snap.get("ordering_override")
    rec["ordering_seed"] = cfg.get("ordering_seed") if cfg.get("ordering_seed") is not None \
        else snap.get("ordering_seed")
    exs = snap.get("examples")
    if exs is None:
        exs = cfg.get("library_manifest")
    if isinstance(exs, list):
        rec["examples"] = [
            (e.get("path"), e.get("label"), e.get("category"))
            if isinstance(e, dict) else (str(e), None, None)
            for e in exs
        ]
    else:
        rec["examples"] = None
    rec["text_only_labels"] = snap.get("text_only_labels")
    rec["crop_label"] = snap.get("crop_label")
    # Other snapshot keys that might carry a manipulation
    rec["snap_keys"] = sorted(k for k in snap.keys() if k != "examples")
    for k in ("calibration_set_id", "pool_source", "library", "library_id",
              "pool", "crop_size", "hypothesis", "description"):
        if k in snap:
            rec["snap_" + k] = snap[k] if not isinstance(snap[k], (dict, list)) \
                else json.dumps(snap[k])[:300]
    # Usage
    us = m.get("usage_stats") or {}
    rec["total_input_tokens"] = us.get("total_input_tokens")
    rec["total_cached_tokens"] = us.get("total_cached_tokens")
    rec["n_responses_with_usage"] = us.get("n_responses_with_usage")
    rec["request_count"] = _dig(us, "by_provider.google_gemini.request_count")
    rec["usage_source"] = us.get("usage_source")
    rec["batch_mode"] = _dig(m, "batch_api.execution_mode")
    rec["chunked"] = bool(m.get("chunked_run"))
    pim = m.get("per_item_metadata") or []
    if isinstance(pim, list) and pim:
        ins, cached, models = [], [], set()
        for it in pim:
            if not isinstance(it, dict):
                continue
            tok = it.get("tokens") or {}
            ins.append(tok.get("input_tokens"))
            c = tok.get("cached_tokens")
            if c is None:
                c = tok.get("cached_content_tokens")
            cached.append(c)
            mu = it.get("model_used") or it.get("model_version")
            if mu:
                models.add(mu)
        rec["pim_n"] = len(pim)
        rec["pim_input"] = _stats(ins)
        rec["pim_cached"] = _stats(cached)
        rec["pim_models"] = sorted(models)
    else:
        rec["pim_n"] = 0
    ex = m.get("execution_stats") or {}
    rec["items_processed"] = ex.get("items_processed")
    rec["pricing_model"] = _dig(m, "cost_estimate.pricing_used.model")
    rec["manifest_path"] = snap.get("manifest_path") or cfg.get("manifest_path")
    rec["n_completed_items"] = len(ex.get("completed_items") or [])
    # A transmitted-library fingerprint: only meaningful when images sent
    inc = rec["snap_include_example_images"]
    sent_images = (inc is True or inc == "ABSENT")
    rec["images_sent_by_config"] = sent_images
    if sent_images and rec["examples"]:
        lib = json.dumps([(p, lab) for p, lab, _ in rec["examples"]])
        rec["sent_library_fp"] = hashlib.sha256(lib.encode()).hexdigest()[:12]
        rec["sent_example_n"] = len(rec["examples"])
    else:
        rec["sent_library_fp"] = "NONE"
        rec["sent_example_n"] = 0
    if rec["examples"]:
        lib = json.dumps([(p, lab) for p, lab, _ in rec["examples"]])
        rec["listed_library_fp"] = hashlib.sha256(lib.encode()).hexdigest()[:12]
        rec["listed_example_n"] = len(rec["examples"])
    else:
        rec["listed_library_fp"] = "NONE"
        rec["listed_example_n"] = 0
    # Added here (PR #24 review, finding 9): the two fields the gate re-read
    # each meta for.
    rec["max_output_tokens"] = cfg.get("max_output_tokens", snap.get("max_output_tokens"))
    rec["dispatched_ids"] = sorted(dispatched_ids(m))
    try:
        rec["bytes"] = os.path.getsize(path)
    except OSError:
        pass
    return rec


def harvest(path: str) -> dict[str, Any]:
    """Read one meta file and extract its signature fields.

    Args:
        path: The meta's path.

    Returns:
        :func:`harvest_meta`'s record, or ``{"path", "error"}`` when the file
        cannot be read or parsed (recorded, as the 2026-10-05 harvester did,
        so one bad meta does not stop a sweep).
    """
    try:
        m = load_meta(path)
    except Exception as exc:  # noqa: BLE001 - record and move on
        return {"path": path, "error": repr(exc)[:200]}
    return harvest_meta(m, path)


# ── the signature (copied from arms.py; see the module docstring) ─────────

def eff_temp(r: dict[str, Any]) -> Any:
    """Effective temperature of a record: ``temperature_effective`` if set (E55).

    Args:
        r: A harvested meta record.

    Returns:
        The effective temperature, else the configured one.
    """
    t = r.get("temperature_effective")
    return t if t is not None else r.get("temperature")


def model_of_record(r: dict[str, Any]) -> Any:
    """What ran: per-item model_version, else pricing model, else config (E57).

    Args:
        r: A harvested meta record.

    Returns:
        The model of record.
    """
    pm = r.get("pim_models") or []
    if len(pm) == 1:
        return pm[0]
    if r.get("pricing_model"):
        return r["pricing_model"]
    return r.get("model")


def is_verifier_record(r: dict[str, Any]) -> bool:
    """True for a verifier pass's meta (verify config or verifier script).

    Args:
        r: A harvested meta record.

    Returns:
        Whether the record is a verifier pass.
    """
    return str(r.get("version") or "").startswith("verify_") or \
        r.get("script") in ("run_pv.py", "5_verify_crops.py")


def inputs_fingerprint(ids: frozenset[str] | set[str], manifest_path: str | None = None) -> str:
    """The ``inputs`` signature field for a set of dispatched ids.

    Args:
        ids: Dispatched item ids (one pass's, or the union over an arm).
        manifest_path: The recorded manifest path, used when no ids are.

    Returns:
        ``"<first 12 hex of sha256 over the sorted ids>/<n>"``; else
        ``"manifest:<path>"``; else ``"unrecorded"``.

    Examples:
        >>> inputs_fingerprint(frozenset({"a", "b"})).endswith("/2")
        True
        >>> inputs_fingerprint(frozenset())
        'unrecorded'
    """
    if ids:
        digest = hashlib.sha256(json.dumps(sorted(ids)).encode()).hexdigest()
        return f"{digest[:12]}/{len(ids)}"
    if manifest_path:
        return f"manifest:{manifest_path}"
    return "unrecorded"


def signature(r: dict[str, Any]) -> dict[str, Any]:
    """Transmitted signature of one meta record (:data:`SIGNATURE_FIELDS`).

    Args:
        r: A harvested meta record, with ``inputs`` set by the caller
            (``check_manipulation.meta_record``).

    Returns:
        The signature dict.

    Examples:
        >>> sig = signature({"version": "detect_x", "temperature": 0.7,
        ...     "images_sent_by_config": False, "listed_example_n": 17,
        ...     "listed_library_fp": "abc", "sys_hash": "e169b7237b85ffff"})
        >>> (sig["stage"], sig["examples_sent"], sig["sys_hash"])
        ('proposer', 'none', 'e169b7237b85')
    """
    if is_verifier_record(r):
        # lib_verifier.build_reference_items: text_only_labels win; else
        # every listed example is sent as an image (no include flag read).
        tl = r.get("text_only_labels") or []
        if tl:
            sent = "text-labels:" + str(len(tl))
        elif r.get("listed_example_n"):
            sent = "images:" + r["listed_library_fp"] + f"/{r['listed_example_n']}"
        else:
            sent = "none"
    else:
        if r.get("images_sent_by_config") and r.get("listed_example_n"):
            sent = "images:" + r["listed_library_fp"] + f"/{r['listed_example_n']}"
        else:
            sent = "none"
    return {
        "stage": "verifier" if is_verifier_record(r) else "proposer",
        "model": model_of_record(r),
        "temperature_eff": eff_temp(r),
        "thinking": r.get("thinking_level"),
        "sys_hash": (r.get("sys_hash") or "")[:12] or None,
        "examples_sent": sent,
        "tile_size": r.get("tile_size"),
        "max_output_tokens": r.get("max_output_tokens"),
        "inputs": r.get("inputs"),
    }


__all__ = ["SIGNATURE_FIELDS", "SIGNATURE_VERSION", "dispatched_ids", "eff_temp", "harvest",
           "harvest_meta", "inputs_fingerprint", "is_verifier_record", "load_meta",
           "model_of_record", "signature"]
