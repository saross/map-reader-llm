#!/usr/bin/env python3
"""Flatten the whole run corpus into the uplift-supplement dataset (card step 1).

Build order step 1 of ``planning/uplift-supplement-2026-08-28.md``: one row per
registered condition, carrying the experimental factors (geometry, modality,
thinking, temperature, K, operating point), the metrics (F1 / P / R / MCC with
confidence intervals where the source recorded them), and the stratum context
that says what the numbers may legitimately be compared with.

What it emits (all under ``results/uplift-supplement/``)
-------------------------------------------------------
``conditions.csv``
    The master long-form table: one row per registered condition, scored at its
    stratum's headline buffer (20 m on the gold standard, 50 m on the 55-map
    corpus — notation key § 1, symbol **R**). Carries the mandatory
    ``stratum_id``.

``conditions-by-buffer.csv``
    The same conditions expanded over every buffer their evaluation reports, so
    nothing in the committed sweep is lost to the headline choice. Also
    ``stratum_id``-keyed, because the buffer is part of the key.

``strata.csv``
    One row per stratum: tile count, reference-mound count, the permutation
    instrument's null SD, and MDE at 50 % and 80 % power joined from
    ``results/sensitivity-mde-2026-08-28/sensitivity.json``. Every rendered
    table's caption is meant to state its stratum's resolution from this file.

``transfer-pairs.csv``
    The schema for cross-stratum comparison, emitted with its header and no
    rows. Cross-stratum numbers exist ONLY here, as explicit source ↔ target
    pairs with a delta and a stated tax kind — never as an aggregate.

``column-spec.json``
    The machine-readable column contract: which names the notation key
    sanctions, which are declared extensions, and the warrant for each.

``notation-extension-proposal.md``
    The extension table rendered for the PI to fold into
    ``docs/methodology/notation-key.md`` § 7. This builder deliberately does not
    amend the canonical key itself.

``build-report.md``
    Coverage, gaps, and every decision that needed a judgement call.

Sources (all committed, all read at build time)
-----------------------------------------------
``results/run-registry.json`` (the run spine), ``results/run-facts.json``
(corpus / reference / frame), ``results/run-conditions.json`` (the condition
specs — the row spine), ``results/conditions-manifest.json`` (generated
metrics), ``results/passes-manifest.json`` (per-pass factors and cost), and the
per-condition ``evaluation.json`` each spec points at.

Zero API. Light manifest parsing; safe to run anywhere.

Usage::

    python scripts/build_uplift_supplement.py
    python scripts/build_uplift_supplement.py --out-dir /tmp/preview

Created: 2026-08-29 (uplift-supplement card, Build order step 1)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_detection_paths import (  # noqa: E402
    AmbiguousPassError,
    PassCountMismatch,
    resolve_pool_passes,
)
from scripts.lib_uplift_supplement import (  # noqa: E402
    COLUMN_EXTENSIONS,
    ORIGINAL_PUBLICATION_DATE,
    PRIMARY_BUFFER_BY_CORPUS,
    REFERENCE_N_MOUNDS,
    CorpusSources,
    StratumKey,
    condition_stratum,
    generated_doc_banner,
    iter_condition_specs,
    resolve_basis,
    resolve_geometry,
    write_csv,
)

#: Default output directory (new tree; touches nothing existing).
DEFAULT_OUT_DIR = Path("results/uplift-supplement")

#: Master conditions table, in reading order: identity, stratum, factors,
#: operating point, metrics, context, provenance.
CONDITION_COLUMNS: tuple[str, ...] = (
    "condition_id", "run_id", "label",
    "stratum_id", "corpus", "reference", "buffer_m", "frame_id", "n_tiles",
    "n_refs", "is_primary_buffer",
    "geometry", "tile_px", "overlap_px", "stride_px", "geometry_basis",
    "modality", "thinking", "temperature", "model_used",
    "architecture", "aggregation", "proposer_pool", "K", "N",
    "prob_t", "min_votes", "verified", "verifier_variant", "basis",
    "F1", "F1_CI_lo", "F1_CI_hi", "ci_method", "ci_unreliable",
    "precision", "recall",
    "MCC", "sensitivity", "specificity",
    "tile_TP", "tile_TN", "tile_FP", "tile_FN",
    "n_detections", "cost_usd", "cost_basis",
    "metrics_source", "eval_path", "detections_path", "reference_path",
    "reference_basis", "reference_consumed_path", "notes",
)

#: Strata table.
STRATUM_COLUMNS: tuple[str, ...] = (
    "stratum_id", "corpus", "reference", "buffer_m", "frame_id",
    "n_tiles", "n_refs", "n_conditions",
    "null_std", "null_sd_lo", "null_sd_hi", "n_comparisons",
    "mde_50", "mde_80", "mde_instrument", "mde_source", "mde_join_basis",
    "notes",
)

#: Transfer-pairs table (schema only — rows are authored, never derived).
TRANSFER_PAIR_COLUMNS: tuple[str, ...] = (
    "pair_id",
    "source_condition_id", "source_stratum_id", "source_value",
    "target_condition_id", "target_stratum_id", "target_value",
    "metric", "delta", "tax_kind", "transfer",
    "rationale", "registered_analysis_id",
)


# --------------------------------------------------------------------------- #
# Row construction
# --------------------------------------------------------------------------- #


def _load_eval(repo_root: Path, eval_path: str | None) -> dict[str, Any] | None:
    """Read a condition's evaluation artefact, or return ``None`` if absent.

    Args:
        repo_root: Repository root.
        eval_path: Repo-relative path recorded on the condition spec.

    Returns:
        The parsed document, or ``None`` when the spec records no path or the
        file is missing.
    """
    if not eval_path:
        return None
    path = repo_root / eval_path
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _per_buffer_from_manifest(condition: dict[str, Any]) -> dict[int, dict[str, Any]]:
    """Normalise the conditions-manifest metrics block into per-buffer rows.

    Args:
        condition: A ``conditions-manifest.json`` row.

    Returns:
        Buffer radius in metres mapped to a flat metric dict.
    """
    out: dict[int, dict[str, Any]] = {}
    metrics = condition.get("metrics") or {}
    for buffer_text, block in (metrics.get("per_buffer") or {}).items():
        ci = block.get("ci") or {}
        out[int(buffer_text)] = {
            "F1": block.get("f1"),
            "precision": block.get("precision"),
            "recall": block.get("recall"),
            "F1_CI_lo": ci.get("low"),
            "F1_CI_hi": ci.get("high"),
            "ci_method": ci.get("method"),
            "ci_unreliable": block.get("ci_unreliable"),
        }
    return out


def _per_buffer_from_eval(document: dict[str, Any]) -> dict[int, dict[str, Any]]:
    """Normalise an ``evaluation.json`` summary into per-buffer rows.

    Field names follow ``generate_post_run_report._metrics_from_eval``, which is
    the generator's own reader, so a fallback row is constructed exactly as the
    manifest row would have been had the manifest been regenerated.

    Args:
        document: The parsed evaluation document.

    Returns:
        Buffer radius in metres mapped to a flat metric dict.
    """
    out: dict[int, dict[str, Any]] = {}
    for block in (document.get("summary") or {}).get("buffers", []):
        out[int(block["buffer_metres"])] = {
            "F1": block.get("f1"),
            "precision": block.get("precision"),
            "recall": block.get("recall"),
            "F1_CI_lo": block.get("f1_ci_lower"),
            "F1_CI_hi": block.get("f1_ci_upper"),
            "ci_method": block.get("f1_ci_method"),
            "ci_unreliable": block.get("ci_unreliable"),
        }
    return out


def _tile_block(
    condition: dict[str, Any] | None, document: dict[str, Any] | None
) -> dict[str, Any]:
    """Lift the buffer-agnostic tile-classification block.

    MCC lives once per condition, not once per buffer (conditions-manifest
    schema). A ``None`` MCC is carried through as ``None`` and never as 0.0
    (erratum E81).

    Args:
        condition: The manifest row, if present.
        document: The evaluation document, if present.

    Returns:
        Tile-level columns, all ``None`` where no source carries them.
    """
    if condition is not None:
        tile = (condition.get("metrics") or {}).get("tile_classification") or {}
        return {
            "MCC": tile.get("mcc"),
            "sensitivity": tile.get("sensitivity"),
            "specificity": tile.get("specificity"),
            "tile_TP": tile.get("tp"), "tile_TN": tile.get("tn"),
            "tile_FP": tile.get("fp"), "tile_FN": tile.get("fn"),
        }
    tile = ((document or {}).get("summary") or {}).get("tile_classification") or {}
    mcc = tile.get("mcc")
    if isinstance(mcc, dict):
        mcc = mcc.get("point")
    confusion = tile.get("confusion") or {}
    return {
        "MCC": mcc,
        "sensitivity": tile.get("sensitivity"),
        "specificity": tile.get("specificity"),
        "tile_TP": confusion.get("tp"), "tile_TN": confusion.get("tn"),
        "tile_FP": confusion.get("fp"), "tile_FN": confusion.get("fn"),
    }


def _meta_fallback_factors(
    sources: CorpusSources, run_id: str, pool: str
) -> dict[str, Any]:
    """Recover generation factors for a pool absent from the passes manifest.

    Six registered runs post-date the last manifest regeneration, so their
    passes carry no manifest rows and their factor columns would otherwise be
    empty — exactly the newest and most cited cells. This reads the committed
    artefacts directly instead:

    * **K** — the number of committed passes in the pool, resolved with
      ``lib_detection_paths.resolve_pool_passes`` (which knows both filename
      conventions and excludes ``run_N_recovery`` fragments).
    * **modality / thinking / temperature / model** — from the FIRST pass's
      sibling ``*.meta.json`` ``configuration`` block. A proposer pool *is* one
      generation config, so these are pool-invariant by construction; reading
      one pass keeps the build light (each meta file is ~1.4 MB).

    Cost is deliberately NOT recovered here: summing it would mean parsing every
    pass's meta across every affected pool, and the resulting figure would still
    be the runner's live estimator rather than the notation key § 8 audited
    basis. The row says so in ``cost_basis``.

    Args:
        sources: Loaded corpus sources.
        run_id: The run.
        pool: The proposer pool.

    Returns:
        Whatever could be read; every key ``None`` when the pool is unresolvable.
    """
    empty = {"modality": sources.pool_modality(run_id, pool), "thinking": None,
             "temperature": None, "model_used": None, "K": None}
    pool_dir = sources.pool_directory(run_id, pool)
    if pool_dir is None:
        return empty
    try:
        # No expected_passes here, deliberately: this branch runs only for pools
        # ABSENT from the passes manifest, so K is the quantity being measured
        # and there is no independent count to assert against. Asserting the
        # answer against itself would be theatre.
        passes = resolve_pool_passes(pool_dir, allow_multiple=False)
    except (AmbiguousPassError, PassCountMismatch):
        return empty
    if not passes:
        return empty
    empty["K"] = len(passes)
    meta_path = passes[0].with_suffix("").with_suffix(".meta.json")
    if not meta_path.exists():
        meta_path = passes[0].parent / (passes[0].stem + ".meta.json")
    if not meta_path.exists():
        return empty
    config = json.loads(meta_path.read_text(encoding="utf-8")).get("configuration") or {}
    if empty["modality"] is None and "include_example_images" in config:
        empty["modality"] = "image" if config["include_example_images"] else "text"
    empty["thinking"] = config.get("thinking_level")
    empty["temperature"] = config.get("temperature")
    empty["model_used"] = config.get("model")
    return empty


def _pass_factors(
    sources: CorpusSources, run_id: str, pool: str, n_passes: int
) -> dict[str, Any]:
    """Lift generation factors and spend from the passes the condition consumed.

    Passes belong to the run, not the condition: an N-sweep shares one pool, so
    the condition consumes the first ``n_passes`` of it (passes-manifest schema).
    K is the pool's FULL pass count and N is the prefix consumed — the notation
    key's central case distinction (§ 1).

    ``cost_usd`` is the sum of the consumed passes' recorded ``cost_usd``, which
    the generator reads from ``meta.cost_estimate.total_cost_usd`` — the
    RUNNER'S LIVE ESTIMATOR. The notation key (§ 8) is explicit that this
    over-records cached-heavy runs and that the citable figure is the audited
    recomputation. The row therefore states its basis rather than claiming the
    audited one.

    Args:
        sources: Loaded corpus sources.
        run_id: The run.
        pool: The proposer pool.
        n_passes: N, the prefix length consumed.

    Returns:
        Factor and cost columns, ``None`` where the pool has no committed passes.
    """
    bucket = sources.passes.get((run_id, pool)) or []
    if not bucket:
        return {
            **_meta_fallback_factors(sources, run_id, pool),
            "cost_usd": None,
            "cost_basis": (
                "unavailable (pool absent from passes-manifest; per-pass "
                "meta not summed — see build report § Decisions)"
            ),
        }
    consumed = bucket[:n_passes]
    costs = [p.get("cost_usd") for p in consumed if p.get("cost_usd") is not None]
    first = consumed[0] if consumed else bucket[0]
    return {
        "modality": first.get("modality"),
        "thinking": first.get("thinking_level"),
        "temperature": first.get("temperature"),
        "model_used": first.get("model_used"),
        "K": len(bucket),
        "cost_usd": round(sum(costs), 6) if costs else None,
        "cost_basis": (
            "runner-estimator (passes-manifest cost_usd; "
            f"sum over N={len(consumed)} proposer passes; NOT the § 8 audited basis)"
            if costs else "unavailable (passes record no cost_estimate)"
        ),
    }


def build_condition_rows(sources: CorpusSources) -> tuple[list[dict], list[dict]]:
    """Build the master and by-buffer condition tables.

    Iterates the hand-authored condition specs (374 across 38 runs) rather than
    the generated manifest (342), so conditions that landed after the last
    manifest regeneration appear as rows with their metrics read straight from
    their evaluation artefact — and any condition with neither source appears
    with null metrics and a note, rather than silently vanishing.

    Args:
        sources: Loaded corpus sources.

    Returns:
        ``(master_rows, by_buffer_rows)``. The master carries one row per
        condition at its corpus's headline buffer; the companion carries one row
        per (condition × evaluated buffer).
    """
    master: list[dict[str, Any]] = []
    by_buffer: list[dict[str, Any]] = []

    for run_id, condition_id, spec in iter_condition_specs(sources):
        facts = sources.facts.get(run_id, {})
        manifest_row = sources.conditions.get(condition_id)
        document = _load_eval(sources.repo_root, spec.get("eval_path"))

        if manifest_row is not None:
            buffers = _per_buffer_from_manifest(manifest_row)
            metrics_source = "conditions-manifest"
        elif document is not None:
            buffers = _per_buffer_from_eval(document)
            metrics_source = "evaluation-json"
        else:
            buffers, metrics_source = {}, "none"

        stratum_key, reference, scope = condition_stratum(
            sources, run_id, condition_id, spec, (document or {}).get("_metadata")
        )
        frame_id = scope.get("test_set_id")
        n_tiles = scope.get("n_test_tiles")
        corpus = facts.get("corpus")
        geometry = resolve_geometry(
            spec.get("proposer_pool"), spec["label"], facts.get("tile_size_px")
        )
        factors = _pass_factors(
            sources, run_id, spec.get("proposer_pool") or "", int(spec["n_passes"])
        )
        tile = _tile_block(manifest_row, document)
        verifier_config = spec.get("verifier_config") or {}

        notes: list[str] = []
        if metrics_source == "none":
            notes.append("no metrics source: absent from conditions-manifest and "
                         "the spec records no readable evaluation")
        elif metrics_source == "evaluation-json":
            notes.append("metrics read from the evaluation artefact: this "
                         "condition post-dates the last manifest regeneration")
        if reference.basis == "unresolved":
            notes.append("reference unresolved from eval metadata, label, or run facts")
        if reference.consumed_path:
            notes.append(
                "scored against a replay copy of the reference; "
                "reference_path is the canonical in-repo anchor and "
                "reference_consumed_path records what the evaluation read"
            )

        manifest_detections = (manifest_row or {}).get("n_detections")
        if manifest_detections is None:
            manifest_detections = ((document or {}).get("summary") or {}).get(
                "n_detections"
            )

        shared = {
            "condition_id": condition_id,
            "run_id": run_id,
            "label": spec["label"],
            "corpus": corpus,
            "reference": reference.term,
            "frame_id": frame_id,
            "n_tiles": n_tiles,
            "n_refs": REFERENCE_N_MOUNDS.get(reference.term or ""),
            "architecture": spec.get("architecture"),
            "aggregation": spec.get("aggregation"),
            "proposer_pool": spec.get("proposer_pool"),
            "N": spec.get("n_passes"),
            "prob_t": spec.get("prob_threshold"),
            "min_votes": spec.get("vote_threshold"),
            "verified": spec.get("aggregation") == "verified",
            "verifier_variant": verifier_config.get("variant"),
            "basis": resolve_basis(spec["label"]),
            "n_detections": manifest_detections,
            "metrics_source": metrics_source,
            "eval_path": spec.get("eval_path"),
            "detections_path": spec.get("detections"),
            "reference_path": reference.path,
            "reference_basis": reference.basis,
            "reference_consumed_path": reference.consumed_path,
            "notes": "; ".join(notes) or None,
            **geometry,
            **factors,
            **tile,
        }

        primary_buffer = PRIMARY_BUFFER_BY_CORPUS.get(corpus or "")
        for buffer_m, metrics in sorted(buffers.items()):
            # The stratum key comes from condition_stratum (the single
            # constructor) with only the buffer varied, so a by-buffer row and
            # its master row cannot disagree about corpus, reference, or frame.
            key = replace(stratum_key, buffer_m=buffer_m)
            row = {
                **shared, **metrics,
                "buffer_m": buffer_m,
                "stratum_id": key.stratum_id,
                "is_primary_buffer": buffer_m == primary_buffer,
            }
            by_buffer.append(row)
            if buffer_m == primary_buffer:
                master.append(row)

        if primary_buffer not in buffers:
            # The condition has no row at its corpus's headline buffer. Emit it
            # into the master anyway, with null metrics and the reason: a
            # missing row is a fact about the corpus, not a reason to drop a
            # registered condition from the census.
            key = replace(stratum_key, buffer_m=primary_buffer or 0)
            reason = (
                f"no evaluation row at the corpus headline buffer "
                f"({primary_buffer} m); evaluated buffers: "
                f"{sorted(buffers) or 'none'}"
            )
            master.append({
                **shared,
                "buffer_m": primary_buffer,
                "stratum_id": key.stratum_id,
                "is_primary_buffer": True,
                "notes": "; ".join([*notes, reason]),
            })

    return master, by_buffer


# --------------------------------------------------------------------------- #
# Strata table
# --------------------------------------------------------------------------- #


def build_strata_rows(
    by_buffer: list[dict[str, Any]], sensitivity: dict[str, Any]
) -> list[dict[str, Any]]:
    """Build one row per stratum, joining the sensitivity/MDE results.

    The MDE join key is ``(n_tiles, buffer_m)``: the sensitivity table names its
    instruments by tile count and buffer, and both are recorded on every stratum.
    Where two frames share a tile count the join is ambiguous — ``era-2-487`` and
    ``grid-common-487`` both have 487 tiles, and the committed instrument was
    measured on the grid common footprint — so the row records the instrument's
    own name and source verbatim and flags the ambiguity in ``mde_join_basis``.

    Args:
        by_buffer: The by-buffer condition rows.
        sensitivity: The parsed ``sensitivity.json``.

    Returns:
        Stratum rows, sorted by ``stratum_id``.
    """
    instruments: dict[tuple[int, int], dict[str, Any]] = {}
    ambiguous: set[tuple[int, int]] = set()
    for entry in sensitivity.get("mde_table", []):
        buffer_m = 50 if entry["n_tiles"] == 8541 else 20
        join_key = (entry["n_tiles"], buffer_m)
        if join_key in instruments:
            ambiguous.add(join_key)
        instruments.setdefault(join_key, entry)

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    frames_by_tile_count: dict[tuple[int, int], set[str]] = defaultdict(set)
    for row in by_buffer:
        grouped[row["stratum_id"]].append(row)
        if row["n_tiles"] is not None and row["frame_id"]:
            frames_by_tile_count[(row["n_tiles"], row["buffer_m"])].add(row["frame_id"])

    rows: list[dict[str, Any]] = []
    for stratum_id, members in sorted(grouped.items()):
        key = StratumKey.parse(stratum_id)
        tile_counts = {m["n_tiles"] for m in members if m["n_tiles"] is not None}
        n_tiles = next(iter(tile_counts)) if len(tile_counts) == 1 else None
        instrument = instruments.get((n_tiles or -1, key.buffer_m))

        notes: list[str] = []
        if len(tile_counts) > 1:
            notes.append(f"members disagree on n_tiles ({sorted(tile_counts)})")
        if key.reference == "canonical":
            notes.append("canonical GT is per-buffer gated; n_refs is the R = 50 m "
                         "materialisation and is not invariant across buffers")
        if instrument is None:
            notes.append("no committed permutation instrument matches "
                         f"(n_tiles={n_tiles}, buffer={key.buffer_m} m); MDE unavailable")

        join_basis = "n_tiles+buffer_m"
        if instrument is None:
            join_basis = "unjoined"
        elif (n_tiles or -1, key.buffer_m) in ambiguous or (
            len(frames_by_tile_count.get((n_tiles or -1, key.buffer_m), set())) > 1
        ):
            join_basis += (
                " (AMBIGUOUS: "
                + ", ".join(sorted(frames_by_tile_count[(n_tiles or -1, key.buffer_m)]))
                + " share this tile count; the instrument was measured on one of "
                "them — see mde_source)"
            )

        null_range = (instrument or {}).get("null_sd_range") or [None, None]
        rows.append({
            "stratum_id": stratum_id,
            "corpus": key.corpus, "reference": key.reference,
            "buffer_m": key.buffer_m, "frame_id": key.frame_id,
            "n_tiles": n_tiles,
            "n_refs": REFERENCE_N_MOUNDS.get(key.reference),
            "n_conditions": len(members),
            "null_std": (instrument or {}).get("null_sd_median"),
            "null_sd_lo": null_range[0], "null_sd_hi": null_range[1],
            "n_comparisons": (instrument or {}).get("n_comparisons"),
            "mde_50": (instrument or {}).get("mde_50pc_power"),
            "mde_80": (instrument or {}).get("mde_80pc_power"),
            "mde_instrument": (instrument or {}).get("instrument"),
            "mde_source": (instrument or {}).get("source"),
            "mde_join_basis": join_basis,
            "notes": "; ".join(notes) or None,
        })
    return rows


# --------------------------------------------------------------------------- #
# Reports
# --------------------------------------------------------------------------- #


def _md_cell(value: Any) -> str:
    """Escape a value for use inside a Markdown table cell.

    ``stratum_id`` uses ``|`` as its component separator, which is also the
    Markdown table delimiter — an unescaped id silently splits one cell into
    four (markdownlint MD056).

    Args:
        value: The value to render.

    Returns:
        The cell text, with pipes escaped.
    """
    return str(value).replace("|", r"\|")


def render_extension_proposal(sanctioned: int) -> str:
    """Render the notation-key extension proposal.

    The canonical key requires new builders to "conform to it or extend it here
    first". A builder amending the key by itself would defeat the point of a
    single PI-commissioned authority, so the extensions are rendered here for
    the PI to paste into § 7.

    Args:
        sanctioned: How many names the key itself sanctions.

    Returns:
        The Markdown document.
    """
    lines = [
        "# Notation-key extension proposal — uplift supplement",
        "",
        *generated_doc_banner(
            "original publication; proposed § 7 additions",
            "scripts/build_uplift_supplement.py",
        ),
        "",
        "The canonical key `docs/methodology/notation-key.md` requires that",
        "\"new tables and dataset builders must conform to it or extend it here",
        "first\". The uplift-supplement builder validates every column it writes",
        f"against §§ 6-7, which sanction {sanctioned} names. The columns below are",
        "the ones the dataset needs that §§ 6-7 do not yet name. A builder must",
        "not amend the canonical key unilaterally, so they are proposed here for",
        "the PI to fold into § 7.",
        "",
        "Until they land in the key, they are declared in",
        "`scripts/lib_uplift_supplement.py` (`COLUMN_EXTENSIONS`), which is what",
        "the builder validates against — so an undeclared column still fails",
        "loudly.",
        "",
        "## Proposed additions to § 7",
        "",
        "| Column | Extends | Rationale |",
        "|---|---|---|",
    ]
    for extension in sorted(COLUMN_EXTENSIONS.values(), key=lambda e: e.column):
        lines.append(
            f"| `{extension.column}` | {extension.derives_from} | {extension.rationale} |"
        )
    lines += [
        "",
        "## Also worth the PI's eye: the § 6 frame table is incomplete",
        "",
        "§ 6 names three frames (`era-1-340`, `grid-common-487`, `55maps-8541`).",
        "`results/run-facts.json` uses four more across the registered runs:",
        "`era-2-487`, `era-3-327`, `h13-common-338`, and `px256-1032`. The",
        "dataset's `frame_id` column carries whichever the run records, so the",
        "gap is visible in the data; closing it in the key would make the",
        "vocabulary checkable rather than merely observable.",
        "",
        "## Changelog",
        "",
        f"### {ORIGINAL_PUBLICATION_DATE} — Original publication",
        "",
        "Generated with the first build of the uplift-supplement dataset",
        "(card `planning/uplift-supplement-2026-08-28.md`, Build order step 1).",
        "",
    ]
    return "\n".join(lines)


def render_build_report(
    sources: CorpusSources,
    master: list[dict[str, Any]],
    by_buffer: list[dict[str, Any]],
    strata: list[dict[str, Any]],
) -> str:
    """Render the human-readable coverage and decisions report.

    Args:
        sources: Loaded corpus sources (for artefact vintages).
        master: Master condition rows.
        by_buffer: By-buffer condition rows.
        strata: Stratum rows.

    Returns:
        The Markdown document.
    """
    sources_count = Counter(r["metrics_source"] for r in master)
    with_ci = sum(1 for r in master if r.get("F1_CI_lo") is not None)
    with_f1 = sum(1 for r in master if r.get("F1") is not None)
    with_mcc = sum(1 for r in master if r.get("MCC") is not None)
    with_cost = sum(1 for r in master if r.get("cost_usd") is not None)
    unjoined = [s for s in strata if s["mde_50"] is None]

    lines = [
        "# Uplift supplement — build report",
        "",
        *generated_doc_banner(
            "original publication; the flatten's coverage and decisions",
            "scripts/build_uplift_supplement.py",
        ),
        "",
        "Generated by `scripts/build_uplift_supplement.py` from committed",
        "artefacts only. Zero API calls; nothing is recomputed.",
        "",
        "## Coverage",
        "",
        "| Quantity | Count |",
        "|---|---:|",
        f"| Runs in `results/run-registry.json` | {len(sources.registry)} |",
        f"| Registered conditions (rows in `conditions.csv`) | {len(master)} |",
        f"| Condition × buffer rows (`conditions-by-buffer.csv`) | {len(by_buffer)} |",
        f"| Strata (`strata.csv`) | {len(strata)} |",
        f"| Conditions with an F1 at the headline buffer | {with_f1} |",
        f"| …of those, with a bootstrap CI on F1 | {with_ci} |",
        f"| Conditions with a tile-level MCC | {with_mcc} |",
        f"| Conditions with a proposer cost | {with_cost} |",
        "",
        "### Factor coverage",
        "",
        "| Factor | Resolved | Unresolved |",
        "|---|---:|---:|",
    ]
    for factor in ("geometry", "modality", "thinking", "temperature", "K",
                   "prob_t", "min_votes", "basis"):
        resolved = sum(1 for r in master if r.get(factor) is not None)
        lines.append(f"| `{factor}` | {resolved} | {len(master) - resolved} |")

    lines += [
        "",
        "`geometry`, `modality`, `thinking`, `temperature`, and `K` are",
        "unresolved for the pools whose output directory the registry's",
        "`directory_path` does not reach under any conventional layout — the",
        "builder records `None` there rather than guessing a path. `prob_t`,",
        "`min_votes`, and `basis` are legitimately absent on single-pass and",
        "consensus cells that have no verifier, no vote threshold, or no basis",
        "term in their registered label.",
        "",
        "### Strata carrying the master table's rows",
        "",
        "| `stratum_id` | Conditions | `n_tiles` | `n_refs` | MDE(80 %) |",
        "|---|---:|---:|---:|---:|",
    ]
    master_strata = {r["stratum_id"] for r in master}
    for stratum in strata:
        if stratum["stratum_id"] not in master_strata:
            continue
        mde = stratum["mde_80"]
        lines.append(
            f"| `{_md_cell(stratum['stratum_id'])}` "
            f"| {sum(1 for r in master if r['stratum_id'] == stratum['stratum_id'])} "
            f"| {stratum['n_tiles'] or '—'} | {stratum['n_refs'] or '—'} "
            f"| {round(mde, 4) if mde is not None else '—'} |"
        )

    lines += [
        "",
        "### Where each row's metrics came from",
        "",
        "| `metrics_source` | Conditions |",
        "|---|---:|",
    ]
    for source, count in sorted(sources_count.items()):
        lines.append(f"| `{source}` | {count} |")

    lines += [
        "",
        "### Source-artefact vintages",
        "",
        "| Artefact | `generated_at` |",
        "|---|---|",
    ]
    for name, vintage in sources.vintages.items():
        lines.append(f"| `results/{name}` | {vintage or '—'} |")

    lines += [
        "",
        "The generated manifests lag the hand-authored registry: conditions",
        "registered after the last regeneration have their metrics read straight",
        "from the evaluation artefact the spec points at, using the same reader",
        "shape as `generate_post_run_report._metrics_from_eval`. Rows say which",
        "route they took in `metrics_source`.",
        "",
        "## Decisions a reader should know about",
        "",
        "1. **Row spine.** `conditions.csv` iterates `results/run-conditions.json`",
        "   (the hand-authored condition specs), not the generated conditions",
        "   manifest. A registered condition the generator has not yet seen is a",
        "   row with null metrics and a note, never an absence.",
        "2. **One row per condition, at the corpus headline buffer.** 20 m on the",
        "   gold standard, 50 m on the 55-map corpus (notation key § 1, **R**).",
        "   The full sweep lives in `conditions-by-buffer.csv`; nothing is lost.",
        "3. **`cost_usd` is NOT the audited basis.** It sums the consumed passes'",
        "   `cost_usd` from the passes manifest, which the generator reads from",
        "   `meta.cost_estimate.total_cost_usd` — the runner's live estimator.",
        "   Notation key § 8 states this over-records cached-heavy runs and that",
        "   the citable figure is the token-load-audit recomputation. That",
        "   recomputation exists only inside per-analysis artefacts",
        "   (`scripts/grid_analysis.py::audited_costs`,",
        "   `scripts/h13_overlap_analysis.py::audited_costs`,",
        "   `results/verifier-robustness/pareto/pareto_v2.json`), not as a",
        "   corpus-wide per-condition table. Every row states its basis in",
        "   `cost_basis`.",
        "4. **Overlap is not machine-recorded for the pre-geometry runs.** Where",
        "   the pool name or label encodes `g<px>_ov<o>` the geometry is exact;",
        "   H13's arms encode overlap as a percentage and are converted against",
        "   the run's recorded tile size; everything else carries a tile size and",
        "   a null overlap. `geometry_basis` names the rule that fired. The",
        "   project tiling default (`config.OVERLAP = 64`) is deliberately NOT",
        "   used as a fallback: it is a default, not a per-run record.",
        "5. **Reference resolution reads the evaluation, not the label.** The",
        "   ground-truth path the evaluation actually consumed wins; the",
        "   `-canonical-gt` / `-standardised-gt` label suffixes are the fallback",
        "   and are matched as whole suffixes only, because labels such as",
        "   `greedy-canonical` and `canonical-first` use the word for a config.",
        "6. **`reference_path` is the canonical in-repo anchor, always.** Nine",
        "   committed evaluations ran against a frozen replay copy under a",
        "   machine-local scratch tree that no longer exists. Publishing that as",
        "   the anchor would hand a reader a dead path, so the anchor is the",
        "   in-repo file the basename names and the literal consumed path is",
        "   preserved in `reference_consumed_path`.",
        "7. **The frame comes from `resolve_scope`, which honours",
        "   `scope_override`.** Two `verifier-robustness` cells run at 256 px on",
        "   the 1,032-tile frame while their run is nominally era-2-487. All",
        "   three builders resolve the frame through that one function, so a",
        "   cell cannot sit in one stratum in the master table and another in a",
        "   worklist.",
        "8. **Generated documents pin their original-publication date.** These",
        "   documents are regenerated in full, so restamping the changelog on",
        "   every build would destroy the revision-policy baseline it exists to",
        "   provide. The original date is a constant; the regeneration time is",
        "   stamped separately in the banner and is not a revision claim.",
        "",
        "## Gaps and open questions for the PI",
        "",
    ]

    no_metrics = [r for r in master if r["metrics_source"] == "none"]
    if no_metrics:
        lines.append(
            f"- **{len(no_metrics)} condition(s) carry no metrics source at all**:"
        )
        for row in no_metrics:
            lines.append(f"  - `{row['condition_id']}`")
    else:
        lines.append(
            "- **Every registered condition resolved to a metrics source.** No row "
            "is a placeholder."
        )
    headline_unjoined = [
        s for s in unjoined
        if s["buffer_m"] == PRIMARY_BUFFER_BY_CORPUS.get(s["corpus"])
    ]
    lines += [
        f"- **{len(unjoined)} of {len(strata)} strata have no MDE**: no committed",
        "  permutation instrument matches their (tile count, buffer) pair. Most",
        "  are off-headline buffers, for which no instrument was ever run.",
        f"  {len(headline_unjoined)} of them "
        + ("sits" if len(headline_unjoined) == 1 else "sit")
        + " at a corpus HEADLINE buffer, where",
        "  the master table's own rows live:",
    ]
    for stratum in headline_unjoined:
        lines.append(
            f"  - `{stratum['stratum_id']}` "
            f"({stratum['n_conditions']} condition(s), n_tiles={stratum['n_tiles']})"
        )
    ambiguous = [s for s in strata if "AMBIGUOUS" in (s["mde_join_basis"] or "")]
    if ambiguous:
        lines += [
            f"- **{len(ambiguous)} strata joined an MDE ambiguously**: several",
            "  frames share a tile count, so the (tile count, buffer) join key does",
            "  not pick one instrument. The row carries the instrument's own name",
            "  and source so the reader can judge the fit, and `mde_join_basis`",
            "  names the competing frames.",
        ]
        for stratum in ambiguous:
            lines.append(
                f"  - `{stratum['stratum_id']}` → {stratum['mde_instrument']}"
            )
    lines += [
        "- **The § 6 frame vocabulary is incomplete** — see",
        "  `notation-extension-proposal.md`.",
        "",
        "## Known and accepted limitations",
        "",
        "Surfaced by the 2026-08-29 audit and left as they are, deliberately:",
        "",
        "- **`h13-common-338` records `n_test_tiles: 338` under a frame id of",
        "  338 but `run-facts.json` gives 340**, so it joins the 340-tile",
        "  instrument. The disagreement is a fact about the registry, not",
        "  something this builder should paper over; `strata.csv` records the",
        "  count it was given.",
        "- **`geometry` is unresolved for 335 of 374 conditions.** Overlap was",
        "  not machine-recorded before the geometry programmes. Recovering it",
        "  would mean parsing tile grids, which is a separate job.",
        "- **Per-condition audited cost does not exist corpus-wide.** See",
        "  decision 3; `cost_usd` states its basis on every row.",
        "- **19 `pv-diag-384` cells cannot be matched to their own verifier",
        "  stage** (`ambiguous-lineage` in the K = 1 worklist). Their labels and",
        "  pool names do not distinguish stages that differ only in verifier",
        "  configuration. They are disclosed as unmeasurable rather than given a",
        "  neighbouring stage's floor.",
        "",
        "## Changelog",
        "",
        f"### {ORIGINAL_PUBLICATION_DATE} — Original publication",
        "",
        "First build of the uplift-supplement flatten (card",
        "`planning/uplift-supplement-2026-08-28.md`, Build order step 1).",
        "",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    """Build the uplift-supplement dataset.

    Args:
        argv: Command-line arguments (defaults to ``sys.argv[1:]``).

    Returns:
        Process exit code: 0 on success.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=PROJECT_ROOT,
                        help="Repository root (default: this script's parent).")
    parser.add_argument("--out-dir", type=Path, default=None,
                        help=f"Output directory (default: {DEFAULT_OUT_DIR}).")
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    out_dir = (args.out_dir or (repo_root / DEFAULT_OUT_DIR)).resolve()

    sources = CorpusSources.load(repo_root)
    master, by_buffer = build_condition_rows(sources)
    strata = build_strata_rows(by_buffer, sources.sensitivity)

    write_csv(out_dir / "conditions.csv", master, CONDITION_COLUMNS, sources.notation)
    write_csv(out_dir / "conditions-by-buffer.csv", by_buffer, CONDITION_COLUMNS,
              sources.notation)
    write_csv(out_dir / "strata.csv", strata, STRATUM_COLUMNS, sources.notation)
    write_csv(out_dir / "transfer-pairs.csv", [], TRANSFER_PAIR_COLUMNS,
              sources.notation)

    spec = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "notation_key": str(sources.notation.path.relative_to(repo_root)),
        "sanctioned_by_notation_key": sorted(sources.notation.sanctioned),
        "declared_extensions": {
            name: {"extends": e.derives_from, "rationale": e.rationale}
            for name, e in sorted(COLUMN_EXTENSIONS.items())
        },
        "tables": {
            "conditions.csv": list(CONDITION_COLUMNS),
            "conditions-by-buffer.csv": list(CONDITION_COLUMNS),
            "strata.csv": list(STRATUM_COLUMNS),
            "transfer-pairs.csv": list(TRANSFER_PAIR_COLUMNS),
        },
    }
    (out_dir / "column-spec.json").write_text(
        json.dumps(spec, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "notation-extension-proposal.md").write_text(
        render_extension_proposal(len(sources.notation.sanctioned)), encoding="utf-8"
    )
    (out_dir / "build-report.md").write_text(
        render_build_report(sources, master, by_buffer, strata), encoding="utf-8"
    )

    print(f"conditions.csv            {len(master):>5} rows")
    print(f"conditions-by-buffer.csv  {len(by_buffer):>5} rows")
    print(f"strata.csv                {len(strata):>5} rows")
    print("transfer-pairs.csv            0 rows (schema only)")
    print(f"written to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
