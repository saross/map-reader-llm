#!/usr/bin/env python3
"""Derive every registered condition's PROPOSER modality from what was sent.

Why this script exists
----------------------
Modality (few-shot exemplars transmitted as **images** versus as **text
labels only**) is a preregistered factor of this study — H1, confirmatory,
"modality and elaboration level". It is therefore not safe for any artefact
to *assert* a condition's modality: the label has to be derivable from the
bytes the model was sent.

On 2026-09-13 the null-exemplar sensitivity job
(`results/null-exemplar-sensitivity-2026-09-13/findings.md`) found seven
Era-2 board cells whose recorded `track` field disagreed with what their
proposer actually transmitted. The mechanism is
`scripts/build_gs_era2_board.py`, which assigned

    "track": "image" if "image" in label else "text"

— a substring test on the condition *label*. That is wrong in two ways:

1. a label may name the **verifier's** modality over a text proposer
   (`proposer-verifier-384::verified-brief-image` runs a
   `detect_brief-text` proposer with ``include_example_images: false``), and
2. a label may carry **no** modality token at all, in which case the
   substring test silently returns ``"text"``
   (`pv-diag-384::pv-scale4-optimal-n1-opmax`, whose proposer config is
   ``detect_h8_scale-4_v2`` with ``include_example_images: true``).

This script establishes the ground truth corpus-wide, independently of every
label, and tabulates it against every field that records a modality so that a
disagreement is visible rather than inferred.

What "modality" means mechanically
----------------------------------
The detection pipeline (`scripts/4_detect_mounds_batch.py`) reads
``include_example_images`` from the proposer config and, when it is false,
prints "Text-only modality: skipping example images" and transmits no example
pixels (line 901); when it is true it attaches one
``types.Part.from_bytes`` per existing example image. The key **defaults to
True** (line 885), so a config without it sent the images. The map tile under
test is always sent as an image — it is a vision task — so modality is a
property of the *exemplar library*, not of the tile.

A condition is therefore derived **image** when at least one of its proposer
passes ran a configuration with ``include_example_images`` true AND a
non-empty ``examples`` list, and **text** otherwise.

Derivation routes, in precedence order
--------------------------------------
Every route that can speak is recorded, so disagreement is visible. Only the
first three read the transmitted configuration; the last two are assertions
and are labelled as such.

A. ``pass-metadata`` — the ``provenance.source_files`` of every pass in
   ``results/passes-manifest.json`` matching the condition's
   ``(run_id, proposer_pool)``. The tightest binding available: the manifest
   itself names the meta files the pass was extracted from.
B. ``run-metadata`` — every ``*.meta.json`` under the proposer pool's output
   directory, located by name (with vote-fraction and aggregation suffixes
   normalised away, e.g. ``flash-high-text-1of5`` -> ``flash-high-text-n5``).
C. ``config-file`` — ``prompts/configs/<pool>.json`` or
   ``prompts/configs/detect_<pool>.json``, for pool keys that ARE config
   names.
D. ``register`` — ``results/run-conditions.json``
   ``decomposition.<run>.proposer_pools.<pool>.modality``. An assertion made
   at authoring time, not a derivation.
E. ``pool-name-token`` — an ``image``/``text`` token in the pool key. The
   weakest source, recorded only so the report can say which conditions rest
   on it.

Usage
-----
    # Derive, and write the table + mismatch list
    python3 scripts/derive_condition_modality.py \
        --out results/modality-track-audit-2026-09-14

    # Gate: exit non-zero if any recorded label disagrees with a derivation
    python3 scripts/derive_condition_modality.py --check

Outputs (under ``--out``)
-------------------------
``derived-modality.json``
    One record per registered condition: every route's verdict, every
    recorded label, and the resolved derivation with its basis.
``derived-modality.csv``
    The same, flattened, one row per condition.
``mismatches.json``
    Only the disagreements, each with the artefact, the field, the recorded
    value, the derived value, and the mechanism that produced the error.
``artefact-summary.json``
    Per-artefact record counts and mismatch counts — the "count per
    artefact" the audit brief asks for.
"""

from __future__ import annotations

import argparse
import collections
import csv
import functools
import glob
import gzip
import json
import re
import sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent

#: `include_example_images` defaults to TRUE in the pipeline —
#: scripts/4_detect_mounds_batch.py:885. A config without the key sent images.
PIPELINE_INCLUDE_IMAGES_DEFAULT = True

#: Registers read.
CONDITIONS_MANIFEST = "results/conditions-manifest.json"
RUN_CONDITIONS = "results/run-conditions.json"
PASSES_MANIFEST = "results/passes-manifest.json"

#: Roots a proposer pool's output directory may sit under.
POOL_ROOTS = ["outputs/h11", "outputs", "outputs/retest"]

#: Suffixes a pool KEY may carry that its output DIRECTORY does not: vote
#: fractions (``-4of5``), union/consensus markers, and the operating-point
#: markers minted by the board builders.
POOL_SUFFIX_RE = re.compile(
    r"(-(?:ge)?\d+of\d+|-union|-consensus-\d+of\d+|-consensus|-opmax"
    r"|-carried-p[\d.]+-k\d+|-p[\d.]+-k\d+)+$")

#: Artefacts that record a per-cell modality and are checked here.
ERA2_BOARD = "results/leaderboard/era2/gs-era2-verified-board-2026-09-10"
BOARD_MEMBERSHIP = f"{ERA2_BOARD}/membership.json"
BOARD_OPMAX_MEMBERSHIP = f"{ERA2_BOARD}/opmax/membership.json"

#: Artefacts keyed by ``condition_id`` that record a modality, as
#: ``(path, list-path, field)``. ``list-path`` is a dotted route to the list
#: of records; "" means the document IS the list.
CONDITION_KEYED_JSON = [
    ("results/working-precision/gs-plateau-characterisation.json",
     "conditions", "modality"),
]

#: CSV artefacts keyed by ``condition_id`` that record a modality, as
#: ``(path, column)``.
CONDITION_KEYED_CSV = [
    ("results/uplift-supplement/conditions.csv", "modality"),
    ("results/uplift-supplement/conditions-by-buffer.csv", "modality"),
]

#: Artefacts whose modality-carrying records are nested at arbitrary depth
#: but identify their condition by a ``ref`` or ``condition_id`` field. Walked
#: recursively: any dict carrying BOTH an id field and a modality field is a
#: checkable record.
REF_WALKED_JSON = [
    "results/tile-size-sweep/tile_size_sweep.json",
    "results/k-ladder-2026-09-12/tension/effect-sizes.json",
    "results/diversity-dividend-384/tiering-champions/tiering_20m.json",
    "results/diversity-dividend-384/tiering-with-deployable/tiering_20m.json",
]

#: Field names that identify a condition in a walked record.
ID_FIELDS = ("condition_id", "ref")

#: Field names that record a modality in a walked record.
MODALITY_FIELDS = ("modality", "track")

#: Artefacts keyed by ``(run_id, <pool field>)`` that record a modality, as
#: ``(path, list-path, run field, pool field, modality field)``.
POOL_KEYED_JSON = [
    ("results/k-ladder-2026-09-12/phase2/ladders.json",
     "ladders", "run_id", "proposer_pool", "modality"),
    ("results/k-ladder-2026-09-12/phase2/unions.json",
     "rungs", "run_id", "pool_slug", "modality"),
    ("results/k-ladder-2026-09-12/tier-e/unions.json",
     "rungs", "run_id", "pool_slug", "modality"),
]


# ── reading what was sent ────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def read_meta(path: str | Path) -> dict[str, Any] | None:
    """Read one ``*.meta.json``'s exemplar-transmission state.

    Args:
        path: Repository-relative or absolute path to a meta file written by
            the detection pipeline.

    Returns:
        ``{"config", "include_example_images", "n_examples",
        "n_null_examples", "meta_path"}``, or None when the file is absent,
        unreadable, or carries no ``configuration`` block.
    """
    p = Path(path)
    if not p.is_absolute():
        p = BASE_DIR / p
    if not p.exists():
        return None
    try:
        raw = p.read_bytes()
        # Some archived metas are gzipped in place under their .json name.
        if raw[:2] == b"\x1f\x8b":
            raw = gzip.decompress(raw)
        cfg = json.loads(raw.decode("utf-8")).get("configuration") or {}
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    if not cfg:
        return None
    snapshot = cfg.get("full_config_snapshot") or {}
    include = cfg.get("include_example_images")
    if include is None:
        include = snapshot.get("include_example_images")
    if include is None:
        include = PIPELINE_INCLUDE_IMAGES_DEFAULT
    examples = snapshot.get("examples") or []
    return {
        "config": cfg.get("version") or snapshot.get("version"),
        "include_example_images": bool(include),
        "n_examples": len(examples),
        "n_null_examples": sum(1 for e in examples
                               if isinstance(e, dict) and e.get("category") == "null"),
        "meta_path": str(p.relative_to(BASE_DIR)) if p.is_relative_to(BASE_DIR) else str(p),
    }


def modality_of(metas: list[dict[str, Any]]) -> str | None:
    """Collapse a set of proposer configurations into one modality.

    Args:
        metas: Records from :func:`read_meta` or :func:`config_file_state`.

    Returns:
        "image" when ANY configuration transmitted example pixels, "text"
        when none did, None when the list is empty. "Any" is the right
        quantifier: a pool whose passes disagree exposed the model to images,
        and :func:`derive` flags such a pool separately as ``mixed``.
    """
    if not metas:
        return None
    return "image" if any(m["include_example_images"] and m["n_examples"] > 0
                          for m in metas) else "text"


def dedupe(metas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collapse metas to one record per distinct configuration.

    Args:
        metas: Records from :func:`read_meta`.

    Returns:
        One record per distinct
        ``(config, include_example_images, n_examples, n_null_examples)``.
    """
    seen: dict[tuple, dict[str, Any]] = {}
    for m in metas:
        seen.setdefault((m["config"], m["include_example_images"],
                         m["n_examples"], m["n_null_examples"]), m)
    return list(seen.values())


def is_proposer_meta(meta: dict[str, Any]) -> bool:
    """True when a meta records a PROPOSER pass, not a verifier pass.

    A ``verify_*`` configuration transmits no exemplar library at all, so it
    says nothing about the proposer's modality and would otherwise be
    mistaken for it (a pool directory usually contains a ``verified/``
    subtree).

    Args:
        meta: A record from :func:`read_meta`.

    Returns:
        True when the configuration version does not start ``verify_``.
    """
    return bool(meta.get("config")) and not str(meta["config"]).startswith("verify_")


# ── route A: the passes manifest's own source files ──────────────────────

def passes_index(passes: list[dict[str, Any]]) -> dict[tuple, list[dict[str, Any]]]:
    """Index the passes manifest by ``(run_id, proposer_pool)``.

    Args:
        passes: ``results/passes-manifest.json``'s ``passes`` list.

    Returns:
        A mapping from ``(run_id, proposer_pool)`` to the passes it holds.
    """
    idx: dict[tuple, list[dict[str, Any]]] = collections.defaultdict(list)
    for p in passes:
        idx[(p.get("run_id"), p.get("proposer_pool"))].append(p)
    return idx


def route_pass_metadata(passes: list[dict[str, Any]]) -> dict[str, Any]:
    """Derive modality from the meta files the passes manifest names.

    Args:
        passes: The passes matching one condition's ``(run_id, pool)``.

    Returns:
        ``{"modality", "configs", "recorded_pass_modality", "n_passes",
        "n_metas_read"}``. ``recorded_pass_modality`` is the manifest's own
        ``modality`` field — a RECORDED label, kept for comparison.
    """
    metas = []
    for p in passes:
        for f in (p.get("provenance") or {}).get("source_files") or []:
            m = read_meta(f)
            if m and is_proposer_meta(m):
                metas.append(m)
    metas = dedupe(metas)
    recorded = sorted({p.get("modality") for p in passes if p.get("modality")})
    return {
        "modality": modality_of(metas),
        "configs": metas,
        "recorded_pass_modality": recorded,
        "n_passes": len(passes),
        "n_metas_read": len(metas),
    }


# ── route B: the proposer pool's output directory ────────────────────────

def pool_dir_candidates(run: str, pool: str, pool_path: str | None) -> list[str]:
    """Candidate directory BASENAMES for a proposer pool key.

    A pool key often names a derived set rather than a directory — the union
    ``flash-high-text-1of5`` is drawn from the pool directory
    ``flash-high-text-n5`` — so the vote-fraction and aggregation suffixes
    are normalised away and the ``-n<K>`` form is offered alongside.

    Args:
        run: Run id.
        pool: The pool key as the register names it.
        pool_path: The pool's registered relative path, when it has one.

    Returns:
        Candidate basenames, most specific first, de-duplicated.
    """
    out: list[str] = []
    for name in (pool_path, pool):
        if not name:
            continue
        out.append(name)
        fraction = re.search(r"-(?:ge)?(\d+)of(\d+)$", name)
        stripped = POOL_SUFFIX_RE.sub("", name)
        if stripped and stripped != name:
            out.append(stripped)
            if fraction:
                out.append(f"{stripped}-n{fraction.group(2)}")
        if fraction:
            out.append(f"{name[:fraction.start()]}-n{fraction.group(2)}")
    return [x for i, x in enumerate(out) if x and x not in out[:i]]


@functools.lru_cache(maxsize=None)
def pool_output_dir(run: str, pool: str, pool_path: str | None) -> tuple[str | None, str | None]:
    """Locate a proposer pool's output directory under ``outputs/``.

    Args:
        run: Run id.
        pool: Pool key.
        pool_path: The pool's registered relative path, when it has one.

    Returns:
        ``(repository-relative directory, the basename that matched)``, or
        ``(None, None)``.
    """
    for name in pool_dir_candidates(run, pool, pool_path):
        cands: list[str] = []
        for root in POOL_ROOTS:
            cands += [f"{root}/{run}/{name}", f"{root}/{name}"]
        if run.startswith("retest-"):
            suffix = run[len("retest-"):]
            cands += [f"outputs/retest/{suffix}/{name}",
                      f"outputs/retest/{suffix}/track1-image/{name}",
                      f"outputs/retest/{suffix}/track2-text/{name}"]
        for cand in cands:
            if (BASE_DIR / cand).is_dir():
                return cand, name
    return None, None


@functools.lru_cache(maxsize=None)
def route_run_metadata(run: str, pool: str, pool_path: str | None) -> dict[str, Any]:
    """Derive modality from every proposer meta under the pool directory.

    Args:
        run: Run id.
        pool: Pool key.
        pool_path: The pool's registered relative path, when it has one.

    Returns:
        ``{"modality", "configs", "pool_output_dir", "matched_basename"}``.
    """
    pool_dir, matched = pool_output_dir(run, pool, pool_path)
    if pool_dir is None:
        return {"modality": None, "configs": [], "pool_output_dir": None,
                "matched_basename": None}
    root = BASE_DIR / pool_dir
    paths = sorted(set(glob.glob(str(root / "*.meta.json"))
                       + glob.glob(str(root / "*/*.meta.json"))
                       + glob.glob(str(root / "*/*/*.meta.json"))
                       + glob.glob(str(root / "*/*/*/*.meta.json"))))
    metas = []
    for p in paths:
        tail = p[len(str(root)):]
        # A pool directory's own verified/ and crops/ subtrees belong to the
        # verifier stage, which transmits no exemplar library.
        if "/verified" in tail or "/crops" in tail:
            continue
        m = read_meta(p)
        if m and is_proposer_meta(m):
            metas.append(m)
    metas = dedupe(metas)
    return {"modality": modality_of(metas), "configs": metas,
            "pool_output_dir": pool_dir, "matched_basename": matched}


# ── route C: the proposer config file ────────────────────────────────────

@functools.lru_cache(maxsize=1)
def config_index() -> dict[str, str]:
    """Index every proposer config under ``prompts/configs/`` by file stem.

    Built once: the tree is deep and ``--check`` would otherwise re-glob it
    per condition. Shallower paths win, so a top-level
    ``prompts/configs/detect_brief-text.json`` outranks a nested copy of the
    same stem.

    Returns:
        A mapping from file stem to repository-relative path.
    """
    index: dict[str, str] = {}
    paths = sorted(glob.glob(str(BASE_DIR / "prompts/configs/**/*.json"), recursive=True),
                   key=lambda p: (p.count("/"), p))
    for path in paths:
        index.setdefault(Path(path).stem, str(Path(path).relative_to(BASE_DIR)))
    return index


@functools.lru_cache(maxsize=None)
def config_file_state(pool: str) -> dict[str, Any] | None:
    """Read a proposer config by name from ``prompts/configs/``.

    Args:
        pool: The pool key — some pool keys ARE config version names
            (``detect_brief-text``).

    Returns:
        The shape of :func:`read_meta`, or None when no such config exists.
    """
    index = config_index()
    for stem in (pool, f"detect_{pool}"):
        path = index.get(stem)
        if path is None:
            continue
        cfg = json.loads((BASE_DIR / path).read_text(encoding="utf-8"))
        include = cfg.get("include_example_images", PIPELINE_INCLUDE_IMAGES_DEFAULT)
        examples = cfg.get("examples") or []
        return {
            "config": cfg.get("version") or stem,
            "include_example_images": bool(include),
            "n_examples": len(examples),
            "n_null_examples": sum(1 for e in examples if isinstance(e, dict)
                                   and e.get("category") == "null"),
            "meta_path": path,
        }
    return None


# ── route E: the name token (the mechanism that produced the error) ──────

def name_token(text: str) -> str | None:
    """Classify a pool key or condition label by its image/text token.

    This reproduces the *failure mode* under audit: it is what
    ``scripts/build_gs_era2_board.py`` used as a modality. It is recorded,
    never trusted.

    Args:
        text: A pool key or condition label.

    Returns:
        "image", "text", "both", or None when neither token appears.
    """
    has_image, has_text = "image" in text, "text" in text
    if has_image and has_text:
        return "both"
    if has_image:
        return "image"
    if has_text:
        return "text"
    return None


def token_as_modality(token: str | None) -> str | None:
    """Read a name token as a modality the way a substring test would.

    Args:
        token: Output of :func:`name_token`.

    Returns:
        "image" for "image" or "both" (a text+image config DID send pixels),
        "text" for "text", None when the token is absent.
    """
    if token in ("image", "both"):
        return "image"
    if token == "text":
        return "text"
    return None


# ── the register's own assertion ─────────────────────────────────────────

#: Recorded values that name a modality. ``text+image`` is a REFINEMENT, not
#: a third level: a config that narrates the exemplars AND sends their pixels
#: is image-bearing under the binary preregistered factor, so it compares
#: equal to a derived "image".
RECORDED_AS_MODALITY = {"image": "image", "text": "text", "text+image": "image"}


def comparable(recorded: Any) -> str | None:
    """Map a recorded modality value onto the binary factor for comparison.

    Args:
        recorded: A value read out of an artefact.

    Returns:
        "image" or "text" when the value names a modality, else None.
    """
    return RECORDED_AS_MODALITY.get(recorded) if isinstance(recorded, str) else None


def register_pool_spec(decomposition: dict[str, Any], run: str,
                       pool: str) -> dict[str, Any]:
    """Look up a pool's registered spec, tolerating both recorded shapes.

    Early runs record ``proposer_pools`` as ``{name: "text"}``; later ones as
    ``{name: {"modality": ..., "path": ...}}``. A pool may also be keyed by
    its path rather than its name.

    Args:
        decomposition: ``results/run-conditions.json``'s ``decomposition``.
        run: Run id.
        pool: Pool key.

    Returns:
        A dict with at least ``modality`` and ``path`` where recorded;
        ``{}`` when the register does not name the pool.
    """
    pools = (decomposition.get(run) or {}).get("proposer_pools") or {}
    spec = pools.get(pool)
    if isinstance(spec, str):
        return {"modality": spec, "path": pool}
    if isinstance(spec, dict):
        return spec
    for value in pools.values():
        if isinstance(value, dict) and value.get("path") == pool:
            return value
    return {}


def register_verifier_modality(decomposition: dict[str, Any], run: str,
                               label: str) -> str | None:
    """The registered modality of the verifier pass a condition's label names.

    Verifier modality matters to the audit because it is what a
    label-substring test sometimes picked up INSTEAD of the proposer's.

    Args:
        decomposition: ``results/run-conditions.json``'s ``decomposition``.
        run: Run id.
        label: Condition label.

    Returns:
        "image" or "text" when exactly one registered verifier-pass key is a
        substring of the label; None otherwise.
    """
    vpasses = (decomposition.get(run) or {}).get("verifier_passes") or {}
    hits = set()
    for key, spec in vpasses.items():
        if key and key in label:
            hits.add(spec if isinstance(spec, str) else spec.get("modality"))
    hits.discard(None)
    return hits.pop() if len(hits) == 1 else None


# ── the public one-condition API (used by the board builder) ─────────────

@functools.lru_cache(maxsize=1)
def _decomposition() -> dict[str, Any]:
    """Load and cache ``results/run-conditions.json``'s decomposition.

    Returns:
        The decomposition mapping, keyed by run id.
    """
    return json.loads(
        (BASE_DIR / RUN_CONDITIONS).read_text(encoding="utf-8"))["decomposition"]


@functools.lru_cache(maxsize=1)
def _passes_index() -> dict[tuple, list[dict[str, Any]]]:
    """Load and cache the passes manifest, indexed by ``(run_id, pool)``.

    Returns:
        The index :func:`passes_index` builds.
    """
    return passes_index(json.loads(
        (BASE_DIR / PASSES_MANIFEST).read_text(encoding="utf-8"))["passes"])


@functools.lru_cache(maxsize=None)
def condition_modality(run_id: str, proposer_pool: str) -> tuple[str | None, str]:
    """Derive one condition's proposer modality from what its passes sent.

    The single-condition entry point for other scripts, so that no artefact
    has to infer modality from a label. Routes are tried in the precedence
    order the module docstring gives; every route that reads a transmitted
    configuration is preferred over any assertion.

    Args:
        run_id: The condition's run id.
        proposer_pool: The condition's ``proposer_pool`` key.

    Returns:
        ``(modality, basis)`` where modality is "image", "text", or None when
        no source can speak, and basis names the route that decided it
        ("pass-metadata", "run-metadata", "config-file", "register",
        "pool-name-token", or "undetermined").

    Examples:
        >>> condition_modality("proposer-verifier-384", "detect_brief-text")
        ('text', 'config-file')
    """
    decomposition = _decomposition()
    spec = register_pool_spec(decomposition, run_id, proposer_pool)
    route_a = route_pass_metadata(_passes_index().get((run_id, proposer_pool)) or [])
    if route_a["modality"]:
        return route_a["modality"], "pass-metadata"
    route_b = route_run_metadata(run_id, proposer_pool, spec.get("path"))
    if route_b["modality"]:
        return route_b["modality"], "run-metadata"
    cfg = config_file_state(proposer_pool)
    if cfg:
        return modality_of([cfg]), "config-file"
    registered = comparable(spec.get("modality"))
    if registered:
        return registered, "register"
    token = token_as_modality(name_token(proposer_pool))
    if token:
        return token, "pool-name-token"
    return None, "undetermined"


# ── recorded labels harvested from artefacts ─────────────────────────────

def harvest_recorded() -> dict[str, dict[str, str]]:
    """Collect every per-condition modality label recorded in an artefact.

    Returns:
        ``{artefact_key: {condition_id: recorded_value}}``. ``artefact_key``
        is ``"<repository-relative path>::<field>"`` so the report can name
        both the file and the field.
    """
    out: dict[str, dict[str, str]] = {}

    def add(key: str, cid: str | None, value: Any) -> None:
        if cid and comparable(value):
            out.setdefault(key, {})[cid] = value

    membership = BASE_DIR / BOARD_MEMBERSHIP
    if membership.exists():
        doc = json.loads(membership.read_text(encoding="utf-8"))
        for m in doc.get("members") or []:
            add(f"{BOARD_MEMBERSHIP}::track", m.get("condition_id"), m.get("track"))

    opmax = BASE_DIR / BOARD_OPMAX_MEMBERSHIP
    if opmax.exists():
        doc = json.loads(opmax.read_text(encoding="utf-8"))
        for m in doc.get("members") or []:
            cid = m.get("condition_id") or (
                f"{m.get('run_id')}::{m.get('label')}" if m.get("run_id") else None)
            add(f"{BOARD_OPMAX_MEMBERSHIP}::track", cid, m.get("track"))
            add(f"{BOARD_OPMAX_MEMBERSHIP}::modality", cid, m.get("modality"))

    for path, list_path, field in CONDITION_KEYED_JSON:
        p = BASE_DIR / path
        if not p.exists():
            continue
        doc = json.loads(p.read_text(encoding="utf-8"))
        for rec in (doc.get(list_path) if list_path else doc) or []:
            add(f"{path}::{field}", rec.get("condition_id"), rec.get(field))

    for path, column in CONDITION_KEYED_CSV:
        p = BASE_DIR / path
        if not p.exists():
            continue
        with p.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                add(f"{path}::{column}", row.get("condition_id"), row.get(column))

    for path in REF_WALKED_JSON:
        p = BASE_DIR / path
        if not p.exists():
            continue
        for cid, field, value in walk_for_modality(
                json.loads(p.read_text(encoding="utf-8"))):
            add(f"{path}::{field}", cid, value)

    return out


def walk_for_modality(node: Any) -> list[tuple[str, str, Any]]:
    """Walk a document for records that name both a condition and a modality.

    Args:
        node: Any JSON value.

    Returns:
        ``(condition_id, field name, recorded value)`` for every dict that
        carries one of :data:`ID_FIELDS` and one of :data:`MODALITY_FIELDS`.
    """
    found: list[tuple[str, str, Any]] = []
    if isinstance(node, dict):
        cid = next((node[f] for f in ID_FIELDS if isinstance(node.get(f), str)), None)
        if cid and "::" in cid:
            for field in MODALITY_FIELDS:
                if field in node:
                    found.append((cid, field, node[field]))
        for value in node.values():
            found += walk_for_modality(value)
    elif isinstance(node, list):
        for value in node:
            found += walk_for_modality(value)
    return found


def harvest_pool_keyed() -> dict[str, dict[tuple[str, str], str]]:
    """Collect modality labels recorded against a ``(run, pool)`` rather than a cell.

    The K-ladder family artefacts label a whole proposer pool, not one
    condition, so they are checked against the pool's derivation directly.

    Returns:
        ``{artefact_key: {(run_id, pool): recorded_value}}``.
    """
    out: dict[str, dict[tuple[str, str], str]] = {}
    for path, list_path, run_field, pool_field, field in POOL_KEYED_JSON:
        p = BASE_DIR / path
        if not p.exists():
            continue
        doc = json.loads(p.read_text(encoding="utf-8"))
        for rec in (doc.get(list_path) if list_path else doc) or []:
            run, pool, value = rec.get(run_field), rec.get(pool_field), rec.get(field)
            if run and pool and comparable(value):
                out.setdefault(f"{path}::{field}", {})[(run, pool)] = value
    return out


#: Why a recorded label disagrees with the derivation. Keyed by
#: (recorded, derived, label token, pool token) shape; resolved in order.
def mechanism_for(rec: dict[str, Any], recorded: str) -> str:
    """Explain how a recorded modality came to disagree with the derivation.

    Args:
        rec: A per-condition record from :func:`derive`.
        recorded: The recorded value that disagrees.

    Returns:
        A one-clause mechanism, for the mismatch table.
    """
    derived = rec["derived"]["modality"]
    label_token = rec["recorded"]["label_token"]
    verifier = rec["recorded"]["register_verifier_modality"]
    pool = rec["proposer_pool"]
    if token_as_modality(label_token) == recorded and verifier == recorded:
        return (f"label substring test: the label's {label_token!r} token names the "
                f"VERIFIER's modality, not the proposer's (pool {pool!r} is "
                f"{derived})")
    if token_as_modality(label_token) == recorded:
        return (f"label substring test: the label's {label_token!r} token does not "
                f"describe the proposer pool {pool!r} ({derived})")
    if label_token is None and recorded == "text":
        return ("label substring test with no modality token in the label: "
                f"`'image' in label` was false, so the test fell through to its "
                f"'text' default (pool {pool!r} is {derived})")
    if rec["recorded"]["register_pool_modality"] == recorded:
        return (f"inherited from the register's proposer_pools[{pool!r}].modality, "
                f"which itself disagrees with the transmitted configuration")
    return "unclassified — recorded value matches no known assignment mechanism"


# ── derivation ───────────────────────────────────────────────────────────

def derive() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Derive modality for every registered condition and every labelled pool.

    Returns:
        ``(condition records, pool records)``. A condition record covers one
        row of ``results/conditions-manifest.json``; a pool record covers one
        ``(run, pool)`` labelled by a pool-keyed artefact.
    """
    conditions = json.loads(
        (BASE_DIR / CONDITIONS_MANIFEST).read_text(encoding="utf-8"))["conditions"]
    decomposition = json.loads(
        (BASE_DIR / RUN_CONDITIONS).read_text(encoding="utf-8"))["decomposition"]
    passes = json.loads(
        (BASE_DIR / PASSES_MANIFEST).read_text(encoding="utf-8"))["passes"]
    p_index = passes_index(passes)
    recorded_by_artefact = harvest_recorded()

    records: list[dict[str, Any]] = []
    for cond in conditions:
        run = cond["run_id"]
        label = cond["label"]
        cid = cond["condition_id"]
        pool = cond.get("proposer_pool") or ""
        spec = register_pool_spec(decomposition, run, pool)

        route_a = route_pass_metadata(p_index.get((run, pool)) or [])
        route_b = route_run_metadata(run, pool, spec.get("path"))
        cfg = config_file_state(pool)
        route_c = {"modality": modality_of([cfg] if cfg else []),
                   "configs": [cfg] if cfg else []}
        register_modality = spec.get("modality")
        pool_token = name_token(pool)
        label_token = name_token(label)

        resolved, basis = None, None
        for candidate, name in ((route_a["modality"], "pass-metadata"),
                                (route_b["modality"], "run-metadata"),
                                (route_c["modality"], "config-file"),
                                (comparable(register_modality), "register"),
                                (token_as_modality(pool_token), "pool-name-token")):
            if candidate:
                resolved, basis = candidate, name
                break

        # Every route that read a transmitted configuration must agree.
        transmitted = [m for m in (route_a["modality"], route_b["modality"],
                                   route_c["modality"]) if m]
        record: dict[str, Any] = {
            "condition_id": cid,
            "run_id": run,
            "label": label,
            "architecture": cond.get("architecture"),
            "aggregation": cond.get("aggregation"),
            "proposer_pool": pool,
            "derived": {
                "modality": resolved,
                "basis": basis,
                "from_transmitted_configuration": basis in (
                    "pass-metadata", "run-metadata", "config-file"),
                "routes_disagree": len(set(transmitted)) > 1,
                "pass_metadata": route_a,
                "run_metadata": route_b,
                "config_file": route_c,
            },
            "recorded": {
                "register_pool_modality": register_modality,
                "register_verifier_modality": register_verifier_modality(
                    decomposition, run, label),
                "passes_manifest_modality": route_a["recorded_pass_modality"],
                "pool_token": pool_token,
                "label_token": label_token,
            },
            "mismatches": [],
        }

        # Artefact-recorded labels.
        for artefact_key, mapping in recorded_by_artefact.items():
            if cid in mapping:
                record["recorded"][artefact_key] = mapping[cid]

        records.append(record)

    # Second pass: mismatch classification, now that `derived` is settled.
    for rec in records:
        derived = rec["derived"]["modality"]
        if not derived:
            continue
        checks: list[tuple[str, str, Any]] = [
            (RUN_CONDITIONS + "::proposer_pools.modality", "modality",
             rec["recorded"]["register_pool_modality"]),
        ]
        for pm in rec["recorded"]["passes_manifest_modality"]:
            checks.append((PASSES_MANIFEST + "::passes[].modality", "modality", pm))
        for key, value in rec["recorded"].items():
            if "::" in key:
                checks.append((key, key.split("::")[-1], value))
        for artefact, field, value in checks:
            if comparable(value) and comparable(value) != derived:
                rec["mismatches"].append({
                    "artefact": artefact.split("::")[0],
                    "field": field,
                    "recorded": value,
                    "derived": derived,
                    "mechanism": mechanism_for(rec, value),
                })

    # Pool-keyed artefacts: one record per (run, pool) they label.
    pool_records: list[dict[str, Any]] = []
    for artefact_key, mapping in harvest_pool_keyed().items():
        for (run, pool), recorded in sorted(mapping.items()):
            spec = register_pool_spec(decomposition, run, pool)
            route_a = route_pass_metadata(p_index.get((run, pool)) or [])
            route_b = route_run_metadata(run, pool, spec.get("path"))
            cfg = config_file_state(pool)
            derived = (route_a["modality"] or route_b["modality"]
                       or modality_of([cfg] if cfg else []))
            basis = ("pass-metadata" if route_a["modality"] else
                     "run-metadata" if route_b["modality"] else
                     "config-file" if derived else None)
            pool_records.append({
                "artefact": artefact_key.split("::")[0],
                "field": artefact_key.split("::")[-1],
                "run_id": run,
                "proposer_pool": pool,
                "recorded": recorded,
                "recorded_as_binary_factor": comparable(recorded),
                "derived": derived,
                "basis": basis,
                "mismatch": bool(derived and comparable(recorded) != derived),
                "refinement": recorded != comparable(recorded),
            })
    return records, pool_records


# ── the verifier stage's own modality ────────────────────────────────────

def verify_stage_dirs(run: str, key: str, spec: Any) -> list[str]:
    """Locate a registered verifier stage's output directory.

    Args:
        run: Run id.
        key: The ``verifier_passes`` key.
        spec: Its recorded spec (a bare modality string or a dict with ``path``).

    Returns:
        Existing repository-relative directories, most specific first.
    """
    path = spec.get("path") if isinstance(spec, dict) else None
    cands: list[str] = []
    for name in ([path] if path else []) + [key]:
        if not name:
            continue
        for root in POOL_ROOTS:
            cands.append(f"{root}/{run}/{name}")
        if run.startswith("retest-"):
            cands.append(f"outputs/retest/{run[len('retest-'):]}/{name}")
    return [c for c in cands if (BASE_DIR / c).is_dir()]


def verifier_pass_audit() -> list[dict[str, Any]]:
    """Audit the register's ``verifier_passes[...].modality`` against two readings.

    The field turns out to be ambiguous across runs, and the audit of
    2026-09-14 reports the ambiguity rather than resolving it (what the field
    means is the PI's to settle). The two candidate readings are:

    * **verifier** — the modality of the verify config the stage ran, by the
      same rule the proposer uses (``include_example_images`` and a non-empty
      exemplar list). ``verify_{adversarial,brief,checklist,comparative}``
      carry six exemplars; their ``*-text`` variants carry none.
    * **track** — the modality of the PROPOSER pool the stage sits beneath,
      i.e. which arm of the experiment the pass belongs to.

    Returns:
        One record per registered verifier stage, with the recorded value, both
        readings, and which of them it matches.
    """
    decomposition = _decomposition()
    conditions = json.loads(
        (BASE_DIR / CONDITIONS_MANIFEST).read_text(encoding="utf-8"))["conditions"]
    by_run: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for cond in conditions:
        by_run[cond["run_id"]].append(cond)

    rows: list[dict[str, Any]] = []
    for run, entry in decomposition.items():
        for key, spec in (entry.get("verifier_passes") or {}).items():
            recorded = spec if isinstance(spec, str) else spec.get("modality")
            metas: list[dict[str, Any]] = []
            for stage_dir in verify_stage_dirs(run, key, spec):
                root = BASE_DIR / stage_dir
                for p in sorted(glob.glob(str(root / "*.meta.json"))
                                + glob.glob(str(root / "*/*.meta.json"))):
                    meta = read_meta(p)
                    if meta and str(meta.get("config") or "").startswith("verify_"):
                        metas.append(meta)
            metas = dedupe(metas)
            verifier_reading = modality_of(metas)

            # The track: the modality of every proposer pool whose conditions
            # name this stage, plus the pool the stage's path sits under.
            pools = set()
            head = (spec.get("path") or "").split("/")[0] if isinstance(spec, dict) else ""
            if head:
                pools.add(head)
            for cond in by_run.get(run, []):
                if key in cond["label"]:
                    pools.add(cond.get("proposer_pool") or "")
            derived = {condition_modality(run, p)[0] for p in pools if p}
            derived.discard(None)
            track_reading = derived.pop() if len(derived) == 1 else None

            rows.append({
                "run_id": run,
                "stage": key,
                "recorded": recorded,
                "verify_configs": sorted({str(m["config"]) for m in metas}),
                "verifier_reading": verifier_reading,
                "track_reading": track_reading,
                "matches_verifier_reading": (
                    None if not verifier_reading or not comparable(recorded)
                    else comparable(recorded) == verifier_reading),
                "matches_track_reading": (
                    None if not track_reading or not comparable(recorded)
                    else comparable(recorded) == track_reading),
            })
    return rows


# ── reporting ────────────────────────────────────────────────────────────

CSV_COLUMNS = [
    "condition_id", "run_id", "label", "proposer_pool", "architecture",
    "aggregation", "derived_modality", "derivation_basis",
    "from_transmitted_configuration", "routes_disagree",
    "register_pool_modality", "register_verifier_modality",
    "passes_manifest_modality", "pool_token", "label_token",
    "board_membership_track", "board_opmax_track", "board_opmax_modality",
    "n_mismatches",
]


def csv_row(rec: dict[str, Any]) -> dict[str, Any]:
    """Flatten one record for ``derived-modality.csv``.

    Args:
        rec: A record from :func:`derive`.

    Returns:
        A dict keyed by :data:`CSV_COLUMNS`.
    """
    r = rec["recorded"]
    return {
        "condition_id": rec["condition_id"],
        "run_id": rec["run_id"],
        "label": rec["label"],
        "proposer_pool": rec["proposer_pool"],
        "architecture": rec["architecture"],
        "aggregation": rec["aggregation"],
        "derived_modality": rec["derived"]["modality"] or "",
        "derivation_basis": rec["derived"]["basis"] or "",
        "from_transmitted_configuration": rec["derived"]["from_transmitted_configuration"],
        "routes_disagree": rec["derived"]["routes_disagree"],
        "register_pool_modality": r["register_pool_modality"] or "",
        "register_verifier_modality": r["register_verifier_modality"] or "",
        "passes_manifest_modality": "|".join(r["passes_manifest_modality"]),
        "pool_token": r["pool_token"] or "",
        "label_token": r["label_token"] or "",
        "board_membership_track": r.get(f"{BOARD_MEMBERSHIP}::track", ""),
        "board_opmax_track": r.get(f"{BOARD_OPMAX_MEMBERSHIP}::track", ""),
        "board_opmax_modality": r.get(f"{BOARD_OPMAX_MEMBERSHIP}::modality", ""),
        "n_mismatches": len(rec["mismatches"]),
    }


def artefact_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Count records and mismatches per artefact.

    Args:
        records: Records from :func:`derive`.

    Returns:
        ``{artefact: {"records_carrying_a_modality", "checked_against_a_derivation",
        "mismatches"}}``.
    """
    summary: dict[str, dict[str, int]] = {}

    def bump(artefact: str, key: str) -> None:
        summary.setdefault(artefact, {"records_carrying_a_modality": 0,
                                      "checked_against_a_derivation": 0,
                                      "mismatches": 0})[key] += 1

    for rec in records:
        derived = rec["derived"]["modality"]
        r = rec["recorded"]
        present: list[tuple[str, Any]] = [
            (RUN_CONDITIONS, r["register_pool_modality"]),
            (PASSES_MANIFEST, r["passes_manifest_modality"][0]
             if r["passes_manifest_modality"] else None),
        ]
        present += [(k.split("::")[0], v) for k, v in r.items() if "::" in k]
        for artefact, value in present:
            if comparable(value):
                bump(artefact, "records_carrying_a_modality")
                if derived:
                    bump(artefact, "checked_against_a_derivation")
        for mm in rec["mismatches"]:
            bump(mm["artefact"], "mismatches")
    return summary


def main() -> int:
    """Command-line entry point.

    Returns:
        0 on success; 1 under ``--check`` when any mismatch remains.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default="results/modality-track-audit-2026-09-14",
                    help="Output directory for the table, mismatch list and summary.")
    ap.add_argument("--check", action="store_true",
                    help="Exit non-zero if any recorded modality disagrees with a "
                         "derivation; writes nothing.")
    args = ap.parse_args()

    records, pool_records = derive()
    verifier_rows = verifier_pass_audit()
    mismatched = [r for r in records if r["mismatches"]]
    pool_mismatched = [r for r in pool_records if r["mismatch"]]
    summary = artefact_summary(records)
    for rec in pool_records:
        entry = summary.setdefault(rec["artefact"], {
            "records_carrying_a_modality": 0,
            "checked_against_a_derivation": 0, "mismatches": 0})
        entry["records_carrying_a_modality"] += 1
        if rec["derived"]:
            entry["checked_against_a_derivation"] += 1
        if rec["mismatch"]:
            entry["mismatches"] += 1

    basis = collections.Counter(r["derived"]["basis"] for r in records)
    print(f"conditions: {len(records)}")
    for name, n in basis.most_common():
        print(f"  basis {name or 'UNDERIVABLE'}: {n}")
    print(f"derived from a transmitted configuration: "
          f"{sum(1 for r in records if r['derived']['from_transmitted_configuration'])}")
    print(f"routes disagreeing internally: "
          f"{sum(1 for r in records if r['derived']['routes_disagree'])}")
    print(f"conditions with a recorded/derived mismatch: {len(mismatched)}")
    print(f"pool-keyed labels checked: {len(pool_records)}, "
          f"mismatched: {len(pool_mismatched)}")
    print(f"registered verifier stages: {len(verifier_rows)} — "
          f"agree with the VERIFIER reading "
          f"{sum(1 for r in verifier_rows if r['matches_verifier_reading'] is True)}, "
          f"contradict it "
          f"{sum(1 for r in verifier_rows if r['matches_verifier_reading'] is False)}; "
          f"agree with the TRACK reading "
          f"{sum(1 for r in verifier_rows if r['matches_track_reading'] is True)}, "
          f"contradict it "
          f"{sum(1 for r in verifier_rows if r['matches_track_reading'] is False)}")
    for artefact, counts in sorted(summary.items()):
        print(f"  {artefact}: {counts['records_carrying_a_modality']} recorded, "
              f"{counts['checked_against_a_derivation']} checkable, "
              f"{counts['mismatches']} mismatched")
    for rec in mismatched:
        for mm in rec["mismatches"]:
            print(f"  MISMATCH {rec['condition_id']} [{mm['artefact']}."
                  f"{mm['field']}] recorded {mm['recorded']} != derived "
                  f"{mm['derived']}")

    for rec in pool_mismatched:
        print(f"  MISMATCH pool {rec['run_id']}::{rec['proposer_pool']} "
              f"[{rec['artefact']}.{rec['field']}] recorded {rec['recorded']} "
              f"!= derived {rec['derived']}")

    if args.check:
        return 1 if (mismatched or pool_mismatched) else 0

    out = BASE_DIR / args.out
    out.mkdir(parents=True, exist_ok=True)
    (out / "derived-modality.json").write_text(json.dumps({
        "_README": (
            "Ground-truth proposer modality for every registered condition, "
            "derived from the transmitted configuration (include_example_images "
            "and a non-empty examples list) rather than from any label, and "
            "tabulated against every field that records a modality. Written by "
            "scripts/derive_condition_modality.py for the modality-track audit "
            "of 2026-09-14."),
        "generated_by": "scripts/derive_condition_modality.py",
        "include_example_images_pipeline_default": PIPELINE_INCLUDE_IMAGES_DEFAULT,
        "n_conditions": len(records),
        "derivation_basis_counts": dict(basis),
        "conditions": records,
    }, indent=1) + "\n", encoding="utf-8")
    (out / "mismatches.json").write_text(json.dumps({
        "_README": ("Every recorded modality label that disagrees with the "
                    "derivation, with the mechanism that produced it."),
        "n_conditions_with_a_mismatch": len(mismatched),
        "conditions": mismatched,
        "n_pool_labels_with_a_mismatch": len(pool_mismatched),
        "pool_labels": pool_mismatched,
    }, indent=1) + "\n", encoding="utf-8")
    (out / "pool-labels.json").write_text(json.dumps({
        "_README": ("Modality labels recorded against a whole proposer pool "
                    "rather than one condition (the K-ladder family "
                    "artefacts), each checked against the pool's own "
                    "transmitted configuration."),
        "n_pool_labels": len(pool_records),
        "pool_labels": pool_records,
    }, indent=1) + "\n", encoding="utf-8")
    (out / "artefact-summary.json").write_text(
        json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    (out / "verifier-pass-modality.json").write_text(json.dumps({
        "_README": (
            "The register's verifier_passes[...].modality field under both "
            "candidate readings — the VERIFIER's own exemplar modality, and "
            "the TRACK (the proposer pool's modality) the stage belongs to. "
            "Reported, not resolved: the field's meaning is inconsistent "
            "across runs and settling it is the PI's."),
        "n_stages": len(verifier_rows),
        "n_matching_verifier_reading": sum(
            1 for r in verifier_rows if r["matches_verifier_reading"] is True),
        "n_contradicting_verifier_reading": sum(
            1 for r in verifier_rows if r["matches_verifier_reading"] is False),
        "n_matching_track_reading": sum(
            1 for r in verifier_rows if r["matches_track_reading"] is True),
        "n_contradicting_track_reading": sum(
            1 for r in verifier_rows if r["matches_track_reading"] is False),
        "stages": verifier_rows,
    }, indent=1) + "\n", encoding="utf-8")
    with (out / "derived-modality.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for rec in records:
            writer.writerow(csv_row(rec))
    print(f"wrote {out}/derived-modality.{{json,csv}}, mismatches.json, "
          f"artefact-summary.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
