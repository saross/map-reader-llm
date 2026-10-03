#!/usr/bin/env python3
"""Phase 2 (C3) — independent field-level re-derivation of the manifests.

For every row of the five verifiable manifests, re-derive each field
from the row's own cited raw sources (``provenance.source_files``,
``results/run-conditions.json``, ``results/run-facts.json``, the
filesystem) using FRESH extraction code — nothing is imported from
``generate_post_run_report.py``, whose extraction logic is the thing
under test (audit-charter § 7 Phase 2; § 5 rule 1: verify against the
least-writable artefact).

Per-field verdicts:

- ``MATCH``          — independently re-derived value equals the manifest value.
- ``MISMATCH``       — values differ (goes to LLM triage).
- ``SOURCE_SILENT``  — the cited source carries no value for this field
                       (e.g. the retest-era empty ``usage_stats`` wall).
- ``STRUCTURAL``     — identifier/derived fields not independently
                       re-derivable from raw sources (ids, pool slugs).
- ``MISSING_SOURCE`` — a cited provenance file does not exist.

Output: ``reports/verification/c3-rederivation/rederivation-report.json``
with per-row detail and a summary block. Deterministic; run on sapphire
for the official enumeration (charter § 8).

Usage::

    python3 scripts/rederive_manifest_fields.py [--limit N] [--out PATH]
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
# The ONE cost function (PI ruling D18). Importing it is not importing the
# generator's extraction logic: the claim under test is that the register
# applied this function to the cited tokens, so the function is the contract
# and the generator's tier inference is what it must not borrow.
from scripts.lib_cost import (  # noqa: E402
    RateCardError,
    UnknownModelError,
    is_unrecorded,
    price_usage,
    resolve_model,
)
DEFAULT_OUT = (
    REPO_ROOT / "reports" / "verification" / "c3-rederivation"
    / "rederivation-report.json"
)


def load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def dig(obj: Any, *paths: str) -> Any:
    """Return the first non-None value at any dotted path in obj."""
    for path in paths:
        cur = obj
        ok = True
        for key in path.split("."):
            if isinstance(cur, dict) and key in cur:
                cur = cur[key]
            else:
                ok = False
                break
        if ok and cur is not None:
            return cur
    return None


def close(a: Any, b: Any, tol: float = 1e-6) -> bool:
    """Equality with float tolerance (costs, seconds, metric values)."""
    if isinstance(a, float) or isinstance(b, float):
        try:
            return abs(float(a) - float(b)) <= tol
        except (TypeError, ValueError):
            return False
    return a == b


def agree(a: Any, b: Any, tol: float = 1e-6) -> bool:
    """Definedness-first comparison for a possibly-undefined metric cell.

    Erratum E81 (2026-08-18): a tile metric that is not computable —
    the 2 x 2 tile confusion matrix is degenerate — is now serialised
    as ``null`` rather than coerced to ``0.0``. ``None`` therefore
    carries meaning and must be compared, not skipped: two ``None``
    values agree (both say "no measurement"), and a ``None`` against a
    number disagrees no matter how small the number is. Only when both
    sides carry a value does the float tolerance apply, so a genuine
    0.0 is still compared as a number.

    :func:`close` cannot express this on its own: ``close(0.0, None)``
    reaches ``float(None)`` and returns ``False`` through its exception
    handler, while ``close(None, None)`` returns ``True`` through the
    non-float branch — right answers, but by accident rather than by
    stated intent.

    Args:
        a: First value, or ``None`` when undefined/absent.
        b: Second value, or ``None`` when undefined/absent.
        tol: Absolute tolerance applied when both values are present.

    Returns:
        ``True`` when the two agree on definedness and (when defined)
        on value within ``tol``.
    """
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return close(a, b, tol=tol)


def verdict_row(field: str, manifest_val: Any, derived: Any,
                silent_ok: bool = False) -> dict:
    """Build one field-verdict record."""
    if derived is None:
        if manifest_val is None:
            return {"field": field, "verdict": "MATCH", "manifest": None,
                    "derived": None, "note": "null == null"}
        return {"field": field, "verdict": "SOURCE_SILENT",
                "manifest": manifest_val, "derived": None}
    v = "MATCH" if close(manifest_val, derived) else "MISMATCH"
    return {"field": field, "verdict": v, "manifest": manifest_val,
            "derived": derived}


# --------------------------------------------------------------------------- #
# Passes
# --------------------------------------------------------------------------- #

#: manifest token field -> candidate meta usage_stats keys
TOKEN_MAP = {
    "input_billed": ("usage_stats.total_input_tokens",),
    "input_cached": ("usage_stats.total_cached_tokens",),
    "output": ("usage_stats.total_output_tokens",),
    "thinking": ("usage_stats.total_thoughts_tokens",
                 "usage_stats.total_reasoning_tokens"),
    "total": ("usage_stats.total_tokens",),
}

STRUCTURAL_PASS_FIELDS = ("pass_id", "run_id", "proposer_pool", "pass_n",
                          "modality")


def is_verifier_pass(row: dict, decomposition: dict) -> bool:
    """Is this pass row a verifier pass rather than a proposer pass?

    Read from the hand-authored ``run-conditions.json`` sidecar, which lists
    each run's ``verifier_passes`` directories. The sidecar is an INPUT that
    both this re-deriver and the generator consume; consulting it does not
    breach the charter's independence rule (§ 5 rule 1), which forbids
    importing the *extraction logic* under test, not reading the same
    declared inputs.

    The distinction matters for tile accounting (E72): a verifier operates
    on candidate crops and its meta records candidate ids, so its
    ``execution_stats`` counts are crop-scale and there is no tile count in
    the source to re-derive.

    Args:
        row: A passes-manifest row.
        decomposition: The ``decomposition`` block of
            ``results/run-conditions.json``.

    Returns:
        True when the row's ``proposer_pool`` is one of its run's declared
        verifier-pass directories.
    """
    fam = decomposition.get(row.get("run_id"), {}) or {}
    return row.get("proposer_pool") in (fam.get("verifier_passes") or {})


def _is_meta(rel: str) -> bool:
    """A cited pass meta: ``*.meta.json(.gz)`` or a preserved ``run.meta.*.json``.

    ``run.meta.main-2026-09-04.json`` (a verifier leg's preserved main leg)
    does not end in ``.meta.json``; a suffix test alone missed it (re-audit
    round 3).
    """
    name = rel.rsplit("/", 1)[-1]
    return (name.endswith((".meta.json", ".meta.json.gz"))
            or (name.startswith("run.meta.") and name.endswith(".json")))


def _load_meta(rel: str) -> dict:
    """A cited meta, plain or gzipped."""
    path = REPO_ROOT / rel
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            return json.load(fh)
    return load(path)


def _billed_usage(meta: dict) -> dict:
    """A meta's usage, undoing the 2026-05-02 recovery-merge double count.

    Independent of the generator's ``fragment_usage`` by design: the merge
    summed the original run's usage into the cumulative usage, which shows as
    ``items_processed`` far above the unique completed items in a meta that
    carries ``recovery_history``; there the per-item token records, one per
    tile, are the usage (token-load-audit-2026-06-12 §§ 3.2, 3.4).
    """
    es = meta.get("execution_stats") or {}
    done = len(set(es.get("completed_items") or []))
    items = meta.get("per_item_metadata") or []
    if not (meta.get("recovery_history") and done
            and (es.get("items_processed") or 0) > 1.5 * done and items
            and all(isinstance(i.get("tokens"), dict) for i in items)):
        return meta.get("usage_stats") or {}
    field = {"total_input_tokens": "input_tokens", "total_cached_tokens": "cached_input_tokens",
             "total_output_tokens": "output_tokens", "total_thoughts_tokens": "thoughts_tokens",
             "total_tokens": "total_tokens"}
    out = {k: sum(int(i["tokens"].get(v) or 0) for i in items) for k, v in field.items()}
    out["n_responses_with_usage"] = len(items)
    return out


def _unpriceable_reason(row: dict, metas: list[dict]) -> str | None:
    """Why a row's cited metas cannot be priced, re-derived; None if they can."""
    for meta in metas:
        usage = meta.get("usage_stats")
        if not usage or is_unrecorded(usage):
            continue
        stamp = meta.get("timestamp") or {}
        if not (stamp.get("end") or stamp.get("start")):
            return "a cited meta with usage has no timestamp"
        own = next((i.get("model_used") for i in (meta.get("per_item_metadata") or [])
                    if i.get("model_used")), None)
        when = (stamp.get("end") or stamp.get("start"))[:10]
        for model in sorted({row.get("model_used"), own} - {None}):
            try:
                resolve_model(model)
                price_usage(usage, model, "standard", at=when)
            except UnknownModelError:
                return f"no rate card entry for {model!r}"
            except RateCardError:
                return f"no rate card row for {model!r} on {when}"
    return None


def _partial_reasons(row: dict, metas: list[dict], sources: list[str]) -> list[str]:
    """Why the cited metas cover only part of a pass, re-derived independently.

    An override listing the pass as a lower bound; a cited meta that recorded
    no usage beside one that did; or a verifier meta accounting for fewer than
    90 % of its leg's probabilities.json results (the cleanup-overwrite
    signature).
    """
    why = []
    if _overrides().get(row.get("pass_id"), {}).get("basis") == "audited-lower-bound":
        why.append("override")
    used = [bool(m.get("usage_stats")) and not is_unrecorded(m["usage_stats"])
            for m in metas if "usage_stats" in m]
    if used and any(used) and not all(used):
        why.append("unrecorded fragment")
    first = next((s for s in sources if _is_meta(s)), None)
    if first and row.get("n_tiles_processed") is None:  # a verifier row (E72)
        prob = REPO_ROOT / first
        prob = prob.parent / "probabilities.json"
        if prob.exists():
            doc = load(prob)
            results = len(doc.get("results") or {})
            rounds = max(int(doc.get("iterations") or 1), 1)
            accounted = 0
            for meta in metas:
                if "usage_stats" not in meta:
                    continue  # results/run-conditions.json and the like
                es = meta.get("execution_stats") or {}
                usage = meta.get("usage_stats") or {}
                done = len(set(es.get("completed_items") or []))
                calls = max(int(((usage.get("by_provider") or {}).get("google_gemini") or {})
                                .get("request_count") or 0),
                            int(usage.get("n_responses_with_usage") or 0))
                accounted += done or int(es.get("items_processed") or 0) or calls // rounds
            if results and accounted < 0.9 * results:
                why.append("verifier coverage")
    return why


def _overrides() -> dict:
    """The committed cost overrides (data, not generator code), keyed by pass_id."""
    path = REPO_ROOT / "data" / "pricing" / "cost-overrides.json"
    return load(path).get("entries", {}) if path.exists() else {}


def _fragment_tiers(frag: dict) -> list[str]:
    """The tiers a ``cost_source`` fragment says it was priced at.

    A pinned fragment names one tier; an upper-bound fragment lists its
    candidates (published at the highest); a tier-indifferent fragment names
    its candidates in its method (they price alike to half a cent).
    """
    if frag.get("tier"):
        return [frag["tier"]]
    if frag.get("candidates"):
        return list(frag["candidates"])
    method = str(frag.get("tier_method") or "")
    if method.startswith("tier-indifferent:"):
        return method.split(":", 1)[1].strip().split("|")
    return []


def rederive_cost(row: dict, sources: list[str], metas: list[dict]) -> list[dict]:
    """Re-derive ``cost_usd`` on the audited basis (WP3; PI ruling D11).

    The claim certified is: ``cost_usd`` equals :func:`scripts.lib_cost.price_usage`
    applied to each cited meta's own ``usage_stats``, at the tier its
    ``cost_source`` fragment records (the HIGHEST candidate when the basis is
    ``audited-upper-bound``), on the fragment's pricing date, summed. The
    fragments priced must be exactly the metas the row cites. Which tier the
    evidence supports is the generator's inference and is not re-derived here;
    it is cited in ``cost_source`` for a reader to check.

    Before WP3 this claim was "equals the meta's cost_estimate", which
    certified the runner's estimate as correct because the register had
    copied it (plan § 1.4). The meta's own block is still compared, as a
    REPORTED field: a disagreement over US$0.01 is listed, never certified.

    Args:
        row: The passes-manifest row.
        sources: Its ``provenance.source_files``.
        metas: Those files, parsed (same order).

    Returns:
        Field verdicts for ``cost_usd``, ``cost_source.fragments`` and
        ``cost_usd.meta_block``.
    """
    claim, basis = row.get("cost_usd"), row.get("cost_basis")
    source = row.get("cost_source") or {}
    meta_costs = [dig(mm, "cost_estimate.total_cost_usd", "cost_estimate.total_usd")
                  for mm in metas]
    meta_costs = [c for c in meta_costs if c is not None]
    meta_sum = round(sum(meta_costs), 6) if meta_costs else None
    if basis is None:  # a row written before generator 0.8.0: the old claim
        return [verdict_row("cost_usd", claim, meta_sum)]
    out: list[dict] = []
    if basis == "published":
        # The figure is a report's, not the metas'; what C3 can certify is that
        # the register carries the figure the overrides file records, and a
        # published row the file does not list is a MISMATCH, never silence.
        entry = _overrides().get(row.get("pass_id"), {})
        ok = entry.get("basis") == "published" and close(claim, entry.get("cost_usd"))
        out.append({"field": "cost_usd", "verdict": "MATCH" if ok else "MISMATCH",
                    "manifest": claim, "derived": entry.get("cost_usd"),
                    "note": f"published: {source.get('published')}"})
    elif basis == "unpriceable":
        # Certified only if a cited meta really cannot be priced: no date, or a
        # model the card does not know. A priceable pass wrongly nulled fails.
        why = _unpriceable_reason(row, metas)
        out.append({"field": "cost_usd",
                    "verdict": "MATCH" if (claim is None and why) else "MISMATCH",
                    "manifest": claim, "derived": None,
                    "note": f"unpriceable: {why or 'no cited meta is unpriceable'}"})
    elif basis == "unrecorded":
        silent = all(not any(v for v in (mm.get("usage_stats") or {}).values()
                             if isinstance(v, (int, float))) for mm in metas)
        out.append({"field": "cost_usd", "verdict": "MATCH" if (claim is None and silent)
                    else "MISMATCH", "manifest": claim, "derived": None,
                    "note": "unrecorded: null over usage blocks that record nothing (D12)"})
    else:
        frags = source.get("fragments") or []
        cited = sorted(s for s in sources if _is_meta(s))
        priced = sorted(f.get("meta") for f in frags)
        out.append({"field": "cost_source.fragments",
                    "verdict": "MATCH" if priced == cited else "MISMATCH",
                    "manifest": priced, "derived": cited})
        total = low = high = 0.0
        spread = False  # does any fragment's price depend on an unresolved tier?
        stamp_errors = []
        for frag in frags:
            meta = _load_meta(frag["meta"])
            usage = _billed_usage(meta)
            # The model and the date are re-derived from the sources, not taken
            # from the claim under test: the date is the meta's own end (else
            # start) timestamp, the model the row's, or the fragment's own
            # per-item record where a recovery ran on another model.
            stamp = meta.get("timestamp") or {}
            when = ((stamp.get("end") or stamp.get("start") or "")[:10]) or None
            own = next((i.get("model_used") for i in (meta.get("per_item_metadata") or [])
                        if i.get("model_used")), None)
            if frag.get("priced_at") != when:
                stamp_errors.append(f"{frag['meta']}: priced_at {frag.get('priced_at')} vs {when}")
            if frag.get("model_recorded") not in {row.get("model_used"), own}:
                stamp_errors.append(f"{frag['meta']}: model {frag.get('model_recorded')} vs "
                                    f"{row.get('model_used')}/{own}")
            tiers = _fragment_tiers(frag)
            if not tiers:
                # A fragment priced at nothing must really have recorded nothing.
                if usage and not is_unrecorded(usage) and not frag.get("unpriceable"):
                    stamp_errors.append(f"{frag['meta']}: claims no usage, meta records usage")
                continue
            try:
                prices = [price_usage(usage, frag["model_recorded"], t,
                                      at=when)["total_cost_usd"] or 0.0
                          for t in tiers]
            except (RateCardError, UnknownModelError) as exc:
                # A claim this ledger cannot price is a finding, never a crash.
                stamp_errors.append(f"{frag['meta']}: cannot price as claimed ({exc})")
                continue
            total += max(prices)
            spread = spread or (max(prices) - min(prices) >= 0.005)
            # Only an unresolved fragment spans a range. A pinned or
            # tier-indifferent one has one cost (its highest candidate, which
            # the half-cent rule makes equal to the rest), counted in both bounds.
            low += min(prices) if frag.get("candidates") else max(prices)
            high += max(prices)
        out.append({"field": "cost_source.fragments.stamps",
                    "verdict": "MISMATCH" if stamp_errors else "MATCH",
                    "manifest": len(frags), "derived": stamp_errors or None})
        partial = _partial_reasons(row, metas, sources)
        # A partial pass publishes its floor (each fragment's lowest candidate);
        # a whole one its total. The label must follow the re-derived facts.
        out.append(verdict_row("cost_usd", claim, round(low if partial else total, 6)))
        # The whole label, re-derived: a floor iff the metas cover part of the
        # pass; else an upper bound iff some fragment's price depends on an
        # unresolved tier; else audited (re-audit round 2: only the lower-bound
        # case was checked, so an upper bound relabelled audited certified).
        expect = ("audited-lower-bound" if partial
                  else "audited-upper-bound" if spread else "audited")
        out.append({"field": "cost_basis", "verdict": "MATCH" if basis == expect else "MISMATCH",
                    "manifest": basis, "derived": expect,
                    "note": f"partial: {', '.join(partial)}" if partial else None})
        if basis == "audited-upper-bound":
            bounds = source.get("bounds_usd") or {}
            out.append(verdict_row("cost_source.bounds_usd.low", bounds.get("low"),
                                   round(low, 6)))
            out.append(verdict_row("cost_source.bounds_usd.high", bounds.get("high"),
                                   round(high, 6)))
    note = "runner estimate in the cited metas; reported, never certified (D11)"
    if meta_sum is not None and claim is not None and abs(meta_sum - claim) > 0.01:
        note += f"; differs from the audited figure by US${meta_sum - claim:+.4f}"
    out.append({"field": "cost_usd.meta_block", "verdict": "STRUCTURAL",
                "manifest": claim, "derived": meta_sum, "note": note})
    return out


def rederive_pass(row: dict, decomposition: dict | None = None) -> dict:
    """Re-derive one passes-manifest row from its cited meta file(s).

    Args:
        row: A passes-manifest row to re-derive.
        decomposition: Optional ``decomposition`` block from
            ``results/run-conditions.json``, used only to tell verifier
            passes from proposer passes for the E72 tile-count rule.
            Omitting it treats every row as a proposer pass (the pre-E72
            behaviour).
    """
    fields: list[dict] = []
    verifier = is_verifier_pass(row, decomposition or {})
    sources = row.get("provenance", {}).get("source_files", [])
    metas = []
    for s in sources:
        p = REPO_ROOT / s
        if not p.exists():
            return {"pass_id": row["pass_id"], "error": "MISSING_SOURCE",
                    "missing": s, "fields": []}
        # Every cited source must exist, but only JSON ones are parsed: a
        # verifier row cites its run.log for the E55 temperature correction,
        # and a gzipped meta must be read as such. Parsing every source as
        # plain JSON crashed this script on both (found 2026-10-03; the last
        # complete run was 2026-07-29, before either kind was cited).
        if _is_meta(s):
            metas.append(_load_meta(s))
        elif s.endswith(".json"):
            metas.append(load(p))
    meta = metas[0] if metas else {}

    for f in STRUCTURAL_PASS_FIELDS:
        fields.append({"field": f, "verdict": "STRUCTURAL",
                       "manifest": row.get(f), "derived": None})

    fields.append(verdict_row(
        "model_requested", row.get("model_requested"),
        dig(meta, "configuration.model", "model_requested")))
    fields.append(verdict_row(
        "model_used", row.get("model_used"),
        dig(meta, "model_used", "api_metadata.model_version")))
    fields.append(verdict_row(
        "model_version", row.get("model_version"),
        dig(meta, "model_version", "api_metadata.model_version")))
    fields.append(verdict_row(
        "thinking_level", row.get("thinking_level"),
        dig(meta, "configuration.thinking_level", "thinking_level")))
    fields.append(verdict_row(
        "temperature", row.get("temperature"),
        # temperature_effective carries the E55-corrected value where a
        # serialisation bug left configuration.temperature stale (triage
        # ruling T1, 2026-07-30); prefer it when present.
        dig(meta, "configuration.temperature_effective",
            "configuration.temperature", "temperature")))
    fields.append(verdict_row(
        "instruction_hash", row.get("instruction_hash"),
        dig(meta, "configuration.system_instruction_hash",
            "configuration.instruction_hash", "instruction_hash")))
    fields.append(verdict_row(
        "library_hash", row.get("library_hash"),
        dig(meta, "configuration.library_hash", "library_hash",
            "hashes.library")))
    # Aggregate execution stats across ALL cited metas — a pass row may
    # cite several source files (checkpoint segments); the manifest value
    # is the aggregate, so the re-derivation must aggregate too.
    # Aggregate semantics: checkpoint-segment metas can overlap, so the
    # correct processed count is the UNION of completed_items where the
    # lists exist; sums are the fallback. An execution_stats block that is
    # entirely zero with empty item lists is a recorder gap (same class as
    # the empty usage_stats wall) -> SOURCE_SILENT, not a false mismatch.
    completed: set[str] = set()
    failed_items: set[str] = set()
    all_have_lists = bool(metas)
    agg_processed = agg_failed = agg_retries = 0
    have_ex = ex_all_zero = False
    for mm in metas:
        exs = mm.get("execution_stats") or {}
        if not exs:
            all_have_lists = False
            continue
        have_ex = True
        agg_processed += exs.get("items_processed") or 0
        agg_failed += exs.get("items_failed") or 0
        agg_retries += exs.get("retries_total") or 0
        ci, fi = exs.get("completed_items"), exs.get("failed_items")
        if isinstance(ci, list):
            completed.update(ci)
        else:
            all_have_lists = False
        if isinstance(fi, list):
            for item in fi:
                if isinstance(item, dict):
                    # failed_items entries may be {item/filename: ..., error: ...}
                    # run_pv writes item_id (re-audit round 3: without it a
                    # failure the cleanup recovered never matched).
                    name = (item.get("item") or item.get("item_id") or item.get("filename")
                            or item.get("tile") or json.dumps(item, sort_keys=True))
                    failed_items.add(str(name))
                else:
                    failed_items.add(str(item))
    ex_all_zero = (have_ex and agg_processed == 0 and agg_failed == 0
                   and not completed and not failed_items)
    if have_ex and not ex_all_zero:
        n_proc = len(completed) if all_have_lists and completed else agg_processed
        n_fail = (len(failed_items - completed)
                  if all_have_lists and (completed or failed_items)
                  else agg_failed)
        if n_proc > 0 and n_fail == 0:
            derived_status = "ok"
        elif n_proc > 0:
            derived_status = "partial"
        else:
            derived_status = "failed"
        fields.append(verdict_row("status", row.get("status"), derived_status))
        if verifier:
            # E72: a verifier meta's execution_stats count candidate crops
            # (its completed_items are cand_NNNN ids), so the source is
            # silent on tiles. Re-deriving n_proc here and calling the
            # manifest's null a MISMATCH would assert a tile count the
            # source never made. The crop count is checked separately.
            fields.append({
                "field": "n_tiles_processed",
                "verdict": "SOURCE_SILENT",
                "manifest": row.get("n_tiles_processed"),
                "derived": None,
                "note": ("verifier pass: meta records candidate crops, not "
                         "tiles — no tile count in source (E72)"),
            })
            fields.append(verdict_row("n_candidates_verified",
                                      row.get("n_candidates_verified"),
                                      n_proc))
        else:
            fields.append(verdict_row("n_tiles_processed",
                                      row.get("n_tiles_processed"), n_proc))
    elif ex_all_zero:
        for f in ("status", "n_tiles_processed"):
            fields.append({"field": f, "verdict": "SOURCE_SILENT",
                           "manifest": row.get(f), "derived": None,
                           "note": "recorder gap: execution_stats all-zero"})
    else:
        fields.append(verdict_row("status", row.get("status"),
                                  dig(meta, "status", "run_status")))
        if verifier:
            # Same E72 rule on the no-execution_stats path: the fallback
            # source (usage_stats request_count) is an API-request count
            # over candidate crops, never a tile count.
            fields.append({
                "field": "n_tiles_processed",
                "verdict": "SOURCE_SILENT",
                "manifest": row.get("n_tiles_processed"),
                "derived": None,
                "note": ("verifier pass: meta records candidate crops, not "
                         "tiles — no tile count in source (E72)"),
            })
        else:
            fields.append(verdict_row(
                "n_tiles_processed", row.get("n_tiles_processed"),
                dig(meta, "n_tiles_processed", "tiles_processed")))

    # tokens: the retest-era wall — usage blocks present but all-zero are
    # treated as SILENT when the manifest also records zeros/nulls, and as
    # a MISMATCH source otherwise (a zero source against a non-zero claim
    # is a real discrepancy, not silence).
    usage = meta.get("usage_stats") or {}
    usage_empty = all(
        not any(v > 0 for v in (mm.get("usage_stats") or {}).values()
                if isinstance(v, (int, float)))
        for mm in metas) and bool(usage)
    man_tokens = row.get("tokens") or {}
    # Token claims are on the billed usage: a recovery-merged meta's doubled
    # usage_stats are replaced by its per-item sums (see _billed_usage).
    billed = [{**mm, "usage_stats": _billed_usage(mm)} if mm.get("usage_stats") else mm
              for mm in metas]
    for mf, cands in TOKEN_MAP.items():
        vals = [dig(mm, *cands) for mm in billed]
        vals = [v for v in vals if v is not None]
        derived = sum(vals) if vals else None
        man_val = man_tokens.get(mf)
        if usage_empty:
            if not man_val:
                fields.append({"field": f"tokens.{mf}", "verdict": "SOURCE_SILENT",
                               "manifest": man_val, "derived": None,
                               "note": "era-wall: usage_stats unpopulated"})
            else:
                fields.append({"field": f"tokens.{mf}", "verdict": "MISMATCH",
                               "manifest": man_val, "derived": 0,
                               "note": "manifest non-zero over empty usage block"})
        else:
            fields.append(verdict_row(f"tokens.{mf}", man_val, derived))

    fields.extend(rederive_cost(row, sources, metas))
    durs = [dig(mm, "timestamp.duration_seconds", "wall_clock_s")
            for mm in metas]
    durs = [x for x in durs if x is not None]
    fields.append(verdict_row(
        "wall_clock_s", row.get("wall_clock_s"),
        sum(durs) if durs else None))
    man_ts = row.get("timestamps") or {}
    starts = [dig(mm, "timestamp.start", "start_time") for mm in metas]
    ends = [dig(mm, "timestamp.end", "end_time") for mm in metas]
    starts = [s for s in starts if s]
    ends = [e for e in ends if e]
    # As instants, not strings: offsets differ across meta eras (re-audit round 4).
    fields.append(verdict_row("timestamps.start", man_ts.get("start"),
                              min(starts, key=datetime.fromisoformat) if starts else None))
    fields.append(verdict_row("timestamps.end", man_ts.get("end"),
                              max(ends, key=datetime.fromisoformat) if ends else None))
    fields.append(verdict_row(
        "retries", row.get("retries"),
        agg_retries if have_ex else dig(meta, "retries")))

    return {"pass_id": row["pass_id"], "fields": fields}


# --------------------------------------------------------------------------- #
# Conditions
# --------------------------------------------------------------------------- #

FACTOR_FIELDS = ("architecture", "aggregation", "proposer_pool", "n_passes",
                 "vote_threshold", "prob_threshold", "verifier_config",
                 "scope_override")


def rederive_condition(row: dict, decomposition: dict) -> dict:
    """Re-derive one conditions row from its eval JSON + the decomposition."""
    fields: list[dict] = []
    for f in ("condition_id", "run_id", "label"):
        fields.append({"field": f, "verdict": "STRUCTURAL",
                       "manifest": row.get(f), "derived": None})

    # factor fields against the decomposition sidecar (independent load)
    fam = decomposition.get(row["run_id"], {})
    cond = next((c for c in fam.get("conditions", [])
                 if c.get("label") == row.get("label")), None)
    for f in FACTOR_FIELDS:
        if cond is None:
            fields.append({"field": f, "verdict": "SOURCE_SILENT",
                           "manifest": row.get(f), "derived": None,
                           "note": "no matching decomposition condition"})
        elif f == "scope_override":
            fields.append(verdict_row(f, row.get(f), cond.get(f),
                                      silent_ok=True))
        else:
            fields.append(verdict_row(f, row.get(f), cond.get(f)))

    # metrics against the cited eval JSON
    sources = row.get("provenance", {}).get("source_files", [])
    eval_path = next((s for s in sources if s.endswith(".json")), None)
    if eval_path is None or not (REPO_ROOT / eval_path).exists():
        fields.append({"field": "metrics", "verdict": "MISSING_SOURCE",
                       "manifest": "(block)", "derived": None,
                       "missing": eval_path})
        return {"condition_id": row["condition_id"], "fields": fields}
    ev = load(REPO_ROOT / eval_path)

    fields.append(verdict_row(
        "n_detections", row.get("n_detections"),
        dig(ev, "summary.n_detections", "n_detections")))

    man_pb = (row.get("metrics") or {}).get("per_buffer") or {}
    raw_buffers = dig(ev, "summary.buffers", "per_buffer", "buffers") or []
    if isinstance(raw_buffers, list):
        ev_pb = {}
        for b in raw_buffers:
            key = str(b.get("buffer_metres"))
            ev_pb[key] = {
                "f1": b.get("f1"), "precision": b.get("precision"),
                "recall": b.get("recall"),
                "ci": {"low": b.get("f1_ci_lower"),
                       "high": b.get("f1_ci_upper")},
            }
    else:
        ev_pb = raw_buffers
    n_match = n_mismatch = n_silent = 0
    mismatches: list[str] = []
    for buf, man_m in man_pb.items():
        ev_m = ev_pb.get(buf) or ev_pb.get(str(buf)) or {}
        for metric in ("f1", "precision", "recall"):
            mv, dv = man_m.get(metric), ev_m.get(metric)
            if dv is None:
                n_silent += 1
            elif close(mv, dv, tol=5e-5):
                n_match += 1
            else:
                n_mismatch += 1
                mismatches.append(f"{buf}m/{metric}: {mv} vs {dv}")
        man_ci, ev_ci = man_m.get("ci") or {}, ev_m.get("ci") or {}
        for cf in ("low", "high"):
            mv, dv = man_ci.get(cf), ev_ci.get(cf)
            if dv is None:
                n_silent += 1
            elif close(mv, dv, tol=5e-5):
                n_match += 1
            else:
                n_mismatch += 1
                mismatches.append(f"{buf}m/ci.{cf}: {mv} vs {dv}")
    fields.append({
        "field": "metrics.per_buffer",
        "verdict": "MISMATCH" if n_mismatch else
                   ("MATCH" if n_match else "SOURCE_SILENT"),
        "n_values_match": n_match, "n_values_mismatch": n_mismatch,
        "n_values_silent": n_silent,
        "mismatches": mismatches[:20],
    })

    man_tc = (row.get("metrics") or {}).get("tile_classification")
    ev_tc = dig(ev, "summary.tile_classification", "tile_classification")
    if man_tc is not None:
        if ev_tc is None:
            fields.append({"field": "metrics.tile_classification",
                           "verdict": "SOURCE_SILENT",
                           "manifest": "(block)", "derived": None})
        else:
            def flat(tc: dict) -> dict:
                """Flatten a tile_classification block to comparable cells.

                Only cells the block actually **carries** appear in the
                result. Erratum E81: ``None`` now means "this metric is
                undefined" (degenerate tile confusion matrix), so a
                recorded ``null`` and an absent field are different
                assertions and must not collapse into one another —
                the first has to be matched, the second has nothing to
                match against.
                """
                conf = tc.get("confusion") or {}
                out: dict = {}
                for cell in ("tp", "tn", "fp", "fn"):
                    if cell in conf:
                        out[cell] = conf[cell]
                    elif cell in tc:
                        out[cell] = tc[cell]
                for metric in ("mcc", "sensitivity", "specificity"):
                    if metric not in tc:
                        continue
                    value = tc[metric]
                    if isinstance(value, dict):
                        if "point" in value:
                            out[metric] = value["point"]
                    else:
                        out[metric] = value
                return out
            man_flat, ev_flat = flat(man_tc), flat(ev_tc)
            # Erratum E81: the old test was
            # ``all(close(...) for k in man_flat if man_flat.get(k) is
            # not None)``, which SKIPPED every cell the manifest
            # recorded as ``None`` — so an undefined manifest MCC
            # agreed with any derived value at all. Definedness is now
            # compared first, and the disagreeing cells are named.
            tc_mismatches = sorted(
                k for k in man_flat
                if not agree(man_flat.get(k), ev_flat.get(k), tol=5e-5)
            )
            same = not tc_mismatches
            fields.append({"field": "metrics.tile_classification",
                           "verdict": "MATCH" if same else "MISMATCH",
                           "mismatched_cells": tc_mismatches,
                           "manifest": man_tc if not same else "(block)",
                           "derived": ev_tc if not same else "(block)"})
    return {"condition_id": row["condition_id"], "fields": fields}


# --------------------------------------------------------------------------- #
# Runs, analyses, registry (the +890 GATE 0 extension)
# --------------------------------------------------------------------------- #

def rederive_simple() -> list[dict]:
    """Existence/consistency checks for runs, analyses, and the registry."""
    out: list[dict] = []
    registry = load(REPO_ROOT / "results/run-registry.json")["registry"]
    for e in registry:
        exists = (REPO_ROOT / e["directory_path"]).exists()
        planned = e.get("status") == "planned"
        out.append({"row": f"registry::{e['run_id']}",
                    "verdict": "MATCH" if (exists or planned) else "MISMATCH",
                    "detail": f"directory_path exists={exists}, "
                              f"status={e.get('status')}"})
    runs = load(REPO_ROOT / "results/runs-manifest.json")["runs"]
    for r in runs:
        exists = (REPO_ROOT / r["directory_path"]).exists()
        prr = r.get("post_run_report_path")
        prr_ok = prr is None or (REPO_ROOT / prr).exists()
        v = "MATCH" if exists and prr_ok else "MISMATCH"
        out.append({"row": f"runs::{r['run_id']}", "verdict": v,
                    "detail": f"dir={exists}, post_run_report={prr_ok}"})
    analyses = load(REPO_ROOT / "results/analyses-manifest.json")["analyses"]
    cond_ids = {c["condition_id"] for c in
                load(REPO_ROOT / "results/conditions-manifest.json")["conditions"]}
    for a in analyses:
        op = a.get("output_path")
        op_ok = op is None or (REPO_ROOT / op).exists()
        fks = [c for c in (a.get("conditions_compared") or [])
               if c not in cond_ids]
        v = "MATCH" if op_ok and not fks else "MISMATCH"
        out.append({"row": f"analyses::{a['analysis_id']}", "verdict": v,
                    "detail": f"output_path={op_ok}, unresolved FKs={fks}"})
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Phase 2 C3 manifest field re-derivation.")
    parser.add_argument("--limit", type=int, default=None,
                        help="Restrict passes/conditions to the first N rows "
                             "(local smoke testing).")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    passes = load(REPO_ROOT / "results/passes-manifest.json")["passes"]
    conditions = load(REPO_ROOT / "results/conditions-manifest.json")["conditions"]
    decomposition = load(
        REPO_ROOT / "results/run-conditions.json")["decomposition"]
    if args.limit:
        passes, conditions = passes[:args.limit], conditions[:args.limit]

    pass_results = [rederive_pass(r, decomposition) for r in passes]
    cond_results = [rederive_condition(r, decomposition) for r in conditions]
    simple_results = rederive_simple()

    def tally(results: list[dict]) -> dict[str, int]:
        t: dict[str, int] = {}
        for r in results:
            if r.get("error"):
                t["MISSING_SOURCE"] = t.get("MISSING_SOURCE", 0) + 1
                continue
            for f in r["fields"]:
                t[f["verdict"]] = t.get(f["verdict"], 0) + 1
        return t

    report = {
        "_README": "Phase 2 C3 field-level re-derivation (audit-charter § 7). "
                   "Fresh extraction code, no imports from the generator. "
                   "Verdict vocabulary in scripts/rederive_manifest_fields.py.",
        "summary": {
            "n_passes": len(pass_results),
            "n_conditions": len(cond_results),
            "n_simple_rows": len(simple_results),
            "passes_verdicts": tally(pass_results),
            "conditions_verdicts": tally(cond_results),
            "simple_verdicts": {
                v: sum(1 for r in simple_results if r["verdict"] == v)
                for v in ("MATCH", "MISMATCH")},
        },
        "passes": pass_results,
        "conditions": cond_results,
        "simple": simple_results,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1)
        fh.write("\n")
    print(json.dumps(report["summary"], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
