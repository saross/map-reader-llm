#!/usr/bin/env python3
"""Shared machinery for the uplift-supplement corpus dataset.

This module is the common floor under the three build steps of the
uplift-supplement card (``planning/uplift-supplement-2026-08-28.md``):

1. the **flatten** (:mod:`scripts.build_uplift_supplement`),
2. the **K = 1 gap-fill worklist** (:mod:`scripts.build_k1_gapfill_worklist`),
3. the **with/without-verifier pairing worklist**
   (:mod:`scripts.build_verifier_pairing_worklist`).

It carries four responsibilities that all three share.

**Loaders.** Thin, typed readers over the project's committed source-of-truth
artefacts. Nothing here recomputes a metric: every value is lifted from a file
whose path is recorded on the row that carries it.

**Stratum keys.** The card's central safeguard. A ``stratum_id`` is the
composite key *corpus × reference × buffer × frame*; comparisons within one
stratum are like-for-like, comparisons across strata are not, and the dataset
makes the difference machine-checkable rather than a matter of care.

**The refusal.** :func:`refuse_cross_stratum` raises
:class:`CrossStratumAggregationError` for any derived aggregate whose rows span
more than one ``stratum_id`` unless the caller passes ``transfer=True``. That
flag is the *only* route to a cross-stratum number, and it lands the result in
the transfer-pairs table rather than in a headline mean.

**Notation-key validation.** Every column written by any of the three builders
is checked against the canonical key ``docs/methodology/notation-key.md``
(§§ 6-7), which the key itself requires ("New tables and dataset builders must
conform to it or extend it here first"). Names the key does not sanction must
appear in :data:`COLUMN_EXTENSIONS` with the section they derive from and a
one-line justification; anything else raises :class:`UnknownColumnError`. The
extension table is emitted as ``notation-extension-proposal.md`` so the PI can
fold it into the key rather than have a builder edit the key unilaterally.

Anti-confabulation
------------------
Values that cannot be read from a committed file are ``None``, never inferred.
Where a value is *derived* (geometry from a pool name, reference from a ground
-truth path), the row carries a ``*_basis`` column naming the rule that fired,
so a reader can re-verify the derivation without re-reading this module.

Usage::

    from scripts.lib_uplift_supplement import (
        CorpusSources, StratumKey, refuse_cross_stratum, validate_columns,
    )

    sources = CorpusSources.load(repo_root)
    key = StratumKey(corpus="4-map-gs", reference="curator",
                     buffer_m=20, frame_id="era-2-487")

Created: 2026-08-29 (uplift-supplement card, Build order steps 1-3)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

__all__ = [
    "COLUMN_EXTENSIONS",
    "ColumnExtension",
    "CorpusSources",
    "CrossStratumAggregationError",
    "NotationKey",
    "PRIMARY_BUFFER_BY_CORPUS",
    "REFERENCE_BY_FILENAME",
    "ScoringRecipe",
    "StratumKey",
    "UnknownColumnError",
    "iter_condition_specs",
    "read_scoring_recipe",
    "refuse_cross_stratum",
    "resolve_basis",
    "resolve_geometry",
    "resolve_reference",
    "validate_columns",
    "write_csv",
]

#: Repository root (this file lives in ``<repo>/scripts/``).
REPO_ROOT: Path = Path(__file__).resolve().parents[1]

#: Canonical notation key. §§ 6-7 are the column-name authority.
NOTATION_KEY_PATH = Path("docs/methodology/notation-key.md")

#: Source-of-truth artefacts, all relative to the repository root.
RUN_REGISTRY_PATH = Path("results/run-registry.json")
RUN_FACTS_PATH = Path("results/run-facts.json")
RUN_CONDITIONS_PATH = Path("results/run-conditions.json")
CONDITIONS_MANIFEST_PATH = Path("results/conditions-manifest.json")
PASSES_MANIFEST_PATH = Path("results/passes-manifest.json")
SENSITIVITY_PATH = Path("results/sensitivity-mde-2026-08-28/sensitivity.json")

#: Reference vocabulary, keyed by the BASENAME of the ground-truth GeoJSON an
#: evaluation actually consumed. Basenames rather than full paths because nine
#: committed evaluations ran against a frozen scratch copy under
#: ``/home/shawn/cc-scratch/tmp/.../frozen/`` (replay harness), whose basename
#: is identical to the in-repo file. Terms follow notation key § 4; the feature
#: counts are the committed files' own, read 2026-08-29.
REFERENCE_BY_FILENAME: dict[str, str] = {
    "mounds-reference.geojson": "curator",
    "student-mounds-55maps-reviewed.geojson": "student",
    "canonical-gt-55maps-r50.geojson": "canonical",
    "best-available-gt-55maps.geojson": "standardised",
}

#: Reference-mound counts, read from the committed GeoJSONs (2026-08-29).
#: ``canonical`` is per-buffer gated (notation key § 4), so its count is the
#: R = 50 m materialisation and is NOT invariant across buffers — the strata
#: table records that caveat alongside the number.
REFERENCE_N_MOUNDS: dict[str, int] = {
    "curator": 569,
    "student": 4746,
    "canonical": 5161,
    "standardised": 5010,
}

#: Path of the reference file each vocabulary term names (the re-verify anchor).
REFERENCE_PATH: dict[str, str] = {
    term: f"inputs/vectors/references/{name}"
    for name, term in REFERENCE_BY_FILENAME.items()
}

#: The headline buffer per corpus (notation key § 1, symbol **R**: "GS-primary
#: 20 m; 55-map operational 50 m"). The master conditions table carries one row
#: per registered condition AT this buffer; the by-buffer companion carries the
#: full sweep.
PRIMARY_BUFFER_BY_CORPUS: dict[str, int] = {
    "4-map-gs": 20,
    "55-map": 50,
}

#: Basis vocabulary (notation key § 3) as it appears in condition labels. Order
#: matters: ``carried-posthoc`` must be tested before ``carried``.
_BASIS_LABEL_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"carried-posthoc"), "carried (post-hoc)"),
    (re.compile(r"(?<![a-z])carried(?![a-z])"), "carried"),
    (re.compile(r"(?<![a-z])oracle(?![a-z])"), "oracle"),
)

#: Geometry encoded in a proposer-pool name or a condition label, e.g.
#: ``g384_ov192`` / ``g384-ov128-55map-...``. Notation key § 2 defines the form.
_GEOMETRY_RE = re.compile(r"g(\d+)[-_]ov(\d+)")

#: H13's arms record overlap as a PERCENTAGE in the label (``arm-a-overlap-12-5``
#: = 12.5 %). ``results/h13-overlap-2026-08-18/findings.md`` (the arm table)
#: states the corresponding stride in pixels — 448 px for arm A at 512 px tiles,
#: i.e. 64 px overlap — so the conversion below is arithmetic over two recorded
#: values, not an inference. Rows converted this way carry
#: ``geometry_basis = "label-overlap-percent"``.
_OVERLAP_PCT_RE = re.compile(r"overlap-(\d+)(?:-(\d+))?")

#: Anchor for re-relativising an absolute path recorded by a scoring engine.
#: Matches the first top-level project directory segment, so a path recorded in
#: the main checkout re-relativises correctly from a worktree (whose directory
#: is named for the branch, not the repository).
_REPO_RELATIVE_RE = re.compile(
    r"/((?:inputs|results|outputs|prompts|scripts|docs|configs|studies)/)"
)


# --------------------------------------------------------------------------- #
# Errors
# --------------------------------------------------------------------------- #


class UnknownColumnError(ValueError):
    """A column name is sanctioned by neither the notation key nor the extensions.

    Raised loudly and early: the card requires the CSV builder to validate its
    columns against ``docs/methodology/notation-key.md`` §§ 6-7, and a silent
    pass-through would let an ad-hoc name into a published dataset.
    """


class CrossStratumAggregationError(ValueError):
    """A derived aggregate spans more than one ``stratum_id`` without ``transfer``.

    The corpus mixes buffers (20 / 50 m), references (curator / student /
    canonical / standardised), and frames (340 / 487 / 8,541 tiles) whose
    instruments have different noise floors. A mean across those is not a
    number about anything, so the builder refuses it. Cross-stratum comparisons
    exist only as explicit source ↔ target pairs in ``transfer-pairs.csv``.
    """


# --------------------------------------------------------------------------- #
# Notation-key validation
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ColumnExtension:
    """One column the notation key does not yet name, declared with its warrant.

    Attributes:
        column: The column name as written to CSV.
        derives_from: The notation-key section whose vocabulary it extends
            (e.g. ``"§ 1"``), or ``"§ 6 (new)"`` where the key has no entry.
        rationale: One line saying what the column holds and why the key's
            existing names do not cover it.
    """

    column: str
    derives_from: str
    rationale: str


def _ext(column: str, derives_from: str, rationale: str) -> ColumnExtension:
    """Build a :class:`ColumnExtension` (keeps the table below readable)."""
    return ColumnExtension(column=column, derives_from=derives_from, rationale=rationale)


#: Columns this dataset adds to the canonical key, each with the section it
#: extends and a justification. ``build_uplift_supplement.py`` renders this
#: table to ``notation-extension-proposal.md`` for the PI to fold into
#: ``docs/methodology/notation-key.md`` § 7 — a builder must not amend the
#: canonical key unilaterally.
COLUMN_EXTENSIONS: dict[str, ColumnExtension] = {
    e.column: e
    for e in (
        # -- identity ------------------------------------------------------ #
        _ext("condition_id", "§ 7 (registry ids)",
             "The `run_id::label` composite spelled as a column name."),
        _ext("run_id", "§ 7 (registry ids)",
             "Foreign key to the run registry; the key names the composite, not the part."),
        # -- stratum ------------------------------------------------------- #
        _ext("corpus", "§ 6",
             "First component of stratum_id: 4-map-gs or 55-map, from run-facts.json."),
        _ext("reference", "§ 4",
             "Second component: curator / student / canonical / standardised."),
        _ext("reference_path", "§ 4",
             "The ground-truth GeoJSON the evaluation consumed (the re-verify anchor)."),
        _ext("reference_basis", "§ 4",
             "Which rule resolved `reference`: eval-ground-truth, label-suffix, or run-facts."),
        _ext("buffer_m", "§ 1 (R / R_m)",
             "Third component, as an integer column; `R_m` is the corrected-F1 CSV's name."),
        _ext("frame_id", "§ 6",
             "Fourth component: the evaluation frame id (era-1-340, era-2-487, ...)."),
        _ext("is_primary_buffer", "§ 1 (R)",
             "True where buffer_m is the corpus headline buffer (20 m GS / 50 m 55-map)."),
        _ext("n_refs", "§ 4",
             "Reference mounds in the stratum's reference file; the key gives no column name."),
        # -- factors ------------------------------------------------------- #
        _ext("geometry", "§ 2 (geometry cell)",
             "The geometry cell label the key defines, as a column."),
        _ext("tile_px", "§ 2 (geometry cell)",
             "Tile size in pixels, the first half of the geometry cell."),
        _ext("overlap_px", "§ 2 (geometry cell)",
             "Overlap in pixels, the second half of the geometry cell."),
        _ext("stride_px", "§ 2 (geometry cell)",
             "tile_px - overlap_px, which the key defines as the stride."),
        _ext("geometry_basis", "§ 2",
             "Which rule resolved the geometry: pool-name, label, or run-facts-tile-size."),
        _ext("modality", "§ 2 (image / text)",
             "Proposer input modality; the key names the values, not a column."),
        _ext("thinking", "§ 2 (MIN / HIGH / low)",
             "Thinking level; the key names the levels, not a column."),
        _ext("temperature", "§ 1 (T)",
             "Sampling temperature. `T` alone is too short to be a safe CSV header."),
        _ext("K", "§ 1 (K)",
             "Passes RUN in the pool. The key defines the symbol; this is the column."),
        _ext("architecture", "conditions-manifest schema",
             "single-pass / consensus / proposer-verifier — the evaluable architecture."),
        _ext("aggregation", "conditions-manifest schema",
             "none / greedy / wbf / consensus / verified."),
        _ext("proposer_pool", "§ 7 (registry ids: run_id::pool::runN)",
             "The pool component of the pass id, as a column."),
        _ext("verified", "§ 2 (PV)",
             "Boolean: a verifier stage ran. The key names the architecture, not a flag."),
        _ext("verifier_variant", "§ 2 (PV)",
             "Verifier variant id from the condition's verifier_config."),
        _ext("model_used", "passes-manifest schema",
             "Authoritative model identity, read from per-item metadata, never a name."),
        # -- metrics ------------------------------------------------------- #
        _ext("ci_method", "§ 5 (CI, BCa, percentile)",
             "The CI method the source evaluation recorded; omitted where it recorded none."),
        _ext("ci_unreliable", "conditions-manifest schema",
             "The measured D28/E72 reliability verdict carried through from the source."),
        # -- context ------------------------------------------------------- #
        _ext("cost_basis", "§ 8 (audited / list / flex)",
             "Which cost basis `cost_usd` carries; NOT the audited basis (see build report)."),
        _ext("metrics_source", "anti-confabulation",
             "conditions-manifest or evaluation-json — where this row's metrics were read."),
        _ext("eval_path", "anti-confabulation",
             "The evaluation artefact the metrics came from."),
        _ext("detections_path", "anti-confabulation",
             "The detection set scored."),
        _ext("notes", "anti-confabulation",
             "Free text recording any gap or caveat attached to this row."),
        # -- strata table -------------------------------------------------- #
        _ext("n_conditions", "§ 6",
             "How many registered conditions resolve into the stratum."),
        _ext("mde_50", "§ 5 (MDE 50 %/80 %)",
             "Minimum detectable effect at 50 % power, joined from sensitivity.json."),
        _ext("mde_80", "§ 5 (MDE 50 %/80 %)",
             "Minimum detectable effect at 80 % power, joined from sensitivity.json."),
        _ext("mde_instrument", "§ 5",
             "The named permutation instrument the MDE and null SD describe."),
        _ext("mde_source", "§ 5",
             "The artefact the instrument's null SD was measured from."),
        _ext("mde_join_basis", "§ 5",
             "The join key used (n_tiles + buffer_m) and any ambiguity it carries."),
        _ext("null_sd_lo", "§ 5 (null SD)",
             "Low end of the instrument's observed null-SD range."),
        _ext("null_sd_hi", "§ 5 (null SD)",
             "High end of the instrument's observed null-SD range."),
        _ext("n_comparisons", "§ 5",
             "Pairwise comparisons the instrument's null SD was measured over."),
        # -- transfer-pairs table ------------------------------------------ #
        _ext("pair_id", "§ 6 (stratum_id)",
             "Primary key of a transfer pair; the key defines the object, not the column."),
        _ext("source_condition_id", "§ 7 (registry ids)",
             "The cell a calibration or claim came FROM."),
        _ext("source_stratum_id", "§ 6",
             "Its stratum — necessarily different from the target's."),
        _ext("target_condition_id", "§ 7 (registry ids)",
             "The cell the claim was carried TO."),
        _ext("target_stratum_id", "§ 6",
             "The target cell's stratum; the delta is a transfer across the two."),
        _ext("metric", "§ 5",
             "Which metric the delta is on (F1, MCC, precision, recall)."),
        _ext("source_value", "§ 5",
             "The metric's value in the source cell."),
        _ext("target_value", "§ 5",
             "The metric's value in the target cell."),
        _ext("delta", "§ 3 (transfer tax)",
             "target_value - source_value; a transfer tax when the sign is negative."),
        _ext("tax_kind", "§ 3 (transfer tax)",
             "Which tax the pair isolates: geometry, reference, corpus, buffer, or frame."),
        _ext("transfer", "heterogeneity design § 3",
             "Always TRUE here: the flag that licenses a cross-stratum number."),
        _ext("rationale", "anti-confabulation",
             "Why this pair is a meaningful comparison despite spanning strata."),
        _ext("registered_analysis_id", "analyses-manifest schema",
             "The registered analysis this pair belongs to, where one exists."),
        # -- worklists (steps 2 and 3) ------------------------------------- #
        _ext("job_id", "anti-confabulation",
             "Primary key of a scoring job in a worklist."),
        _ext("rung", "§ 1 (N)",
             "Which ladder rung the job scores (N = 1 for the K = 1 gap-fill)."),
        _ext("status", "anti-confabulation",
             "ready / blocked / already-registered — whether the job can run at all."),
        _ext("blocked_reason", "anti-confabulation",
             "Why a blocked job cannot run; never a placeholder, always a measured fact."),
        _ext("engine", "anti-confabulation",
             "Which scorer the job needs: evaluate_detections or corrected_f1_multi_buffer."),
        _ext("command", "anti-confabulation",
             "The exact invocation the operator runs on sapphire."),
        _ext("source_condition", "§ 7 (registry ids)",
             "The K >= 3 consensus cell whose K = 1 rung this job supplies."),
        _ext("verified_condition_id", "§ 7 (registry ids)",
             "The verified cell of a with/without-verifier pair."),
        _ext("unverified_detections_path", "anti-confabulation",
             "The pre-verifier consensus set at the same vote threshold."),
        _ext("verifier_min_vote_seen", "§ 1 (k)",
             "Lowest vote_count the verifier actually saw, measured from the crop manifest."),
        _ext("verifier_crop_manifest", "anti-confabulation",
             "The candidate manifest that measurement came from."),
        _ext("k1_with_verifier", "§ 2 (PV)",
             "derivable / blocked / not-applicable — the card's disclosed K = 1 PV anchor."),
        _ext("k1_with_verifier_reason", "anti-confabulation",
             "The measured ground for that verdict; never an approximation."),
        _ext("pairing_basis", "anti-confabulation",
             "Which rule located the pre-verifier twin: registered, consensus-file, union."),
        _ext("unverified_condition_id", "§ 7 (registry ids)",
             "The registered pre-verifier cell, where one already exists."),
        _ext("unverified_eval_path", "anti-confabulation",
             "That cell's committed evaluation, where one already exists."),
        _ext("union_path", "anti-confabulation",
             "The committed vote >= 1 union the vote shell must be filtered out of."),
        _ext("materialise_filter", "§ 1 (k)",
             "The vote_count predicate that turns the union into the paired shell."),
        _ext("bounds_path", "§ 6",
             "The evaluation bounds defining the frame."),
        _ext("output_dir", "anti-confabulation",
             "Where the job writes its evaluation."),
        _ext("uplift", "§ 3",
             "verified minus unverified on the same metric, same stratum."),
        _ext("uplift_metric", "§ 5",
             "Which metric the uplift column is computed on."),
        _ext("verified_value", "§ 5",
             "The verified cell's metric value."),
        _ext("unverified_value", "§ 5",
             "The paired unverified cell's metric value."),
    )
}


class NotationKey:
    """The canonical key's §§ 6-7 vocabulary, harvested from the Markdown source.

    The key is the authority; this class does not restate it. It reads
    ``docs/methodology/notation-key.md``, slices §§ 6-7, and harvests every
    backticked identifier plus the frame-id column of the § 6 table. Tokens
    that are plainly not column names (filenames, glob patterns, ``::``
    composites, array notation) are dropped.

    The key's corrected-F1 inventory names CIs compositionally — "``precision``
    /``recall``/``F1`` with ``_CI_lo``/``_CI_hi``, ``MCC`` + CI" — so the
    harvest expands those products rather than requiring the key to spell all
    eight out.
    """

    def __init__(self, path: Path) -> None:
        """Load and harvest the key.

        Args:
            path: Absolute path to ``notation-key.md``.

        Raises:
            FileNotFoundError: If the key is absent — a builder must never
                fall back to a hard-coded vocabulary when its authority is
                missing.
            ValueError: If §§ 6-7 cannot be located in the document.
        """
        self.path = path
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^## 6\..*?(?=^## 8\.)", text, re.M | re.S)
        if match is None:
            raise ValueError(
                f"{path}: could not locate §§ 6-7 (expected '## 6.' through '## 8.'). "
                "The key's structure changed; update the harvester rather than "
                "hard-coding a vocabulary."
            )
        self.section_text = match.group(0)
        self.sanctioned = self._harvest(self.section_text)

    @staticmethod
    def _harvest(section: str) -> frozenset[str]:
        """Extract sanctioned column names from the §§ 6-7 text.

        Args:
            section: The raw Markdown of §§ 6-7.

        Returns:
            Every identifier the key sanctions as a column name.
        """
        tokens = set(re.findall(r"`([^`]+)`", section))
        # The § 6 table's first column holds frame ids and ``stratum_id``,
        # which the key writes unbackticked.
        tokens |= set(re.findall(r"^\|\s*([a-z0-9][a-z0-9_\-]*)\s*\|", section, re.M))
        names: set[str] = set()
        suffixes: set[str] = set()
        for token in tokens:
            token = token.strip()
            if not token:
                continue
            if token.startswith("_CI_"):
                suffixes.add(token)
                continue
            # Filenames, globs, array notation, and id composites are not columns.
            if any(ch in token for ch in "./*[]") or "::" in token:
                continue
            names.add(token)
        # Expand the key's compositional CI naming.
        for stem in ("precision", "recall", "F1", "MCC"):
            for suffix in suffixes or {"_CI_lo", "_CI_hi"}:
                names.add(f"{stem}{suffix}")
        return frozenset(names)

    def validate(self, columns: Sequence[str]) -> None:
        """Fail loudly on any column the key and the extensions do not sanction.

        Args:
            columns: The column names about to be written.

        Raises:
            UnknownColumnError: On the first unsanctioned name, listing every
                offender so a single run surfaces the whole problem.
        """
        unknown = [
            c for c in columns
            if c not in self.sanctioned and c not in COLUMN_EXTENSIONS
        ]
        if unknown:
            raise UnknownColumnError(
                f"{len(unknown)} column(s) sanctioned by neither "
                f"{self.path.name} §§ 6-7 nor COLUMN_EXTENSIONS: "
                f"{', '.join(sorted(unknown))}. Extend the notation key (and "
                "COLUMN_EXTENSIONS with it) before publishing these columns."
            )


def validate_columns(columns: Sequence[str], repo_root: Path = REPO_ROOT) -> None:
    """Validate a column list against the canonical notation key.

    Convenience wrapper for callers that do not hold a :class:`NotationKey`.

    Args:
        columns: Column names to check.
        repo_root: Repository root holding ``docs/methodology/notation-key.md``.

    Raises:
        UnknownColumnError: If any name is unsanctioned.
    """
    NotationKey(repo_root / NOTATION_KEY_PATH).validate(columns)


# --------------------------------------------------------------------------- #
# Stratum keys and the refusal
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class StratumKey:
    """The composite key *corpus × reference × buffer × frame*.

    The card's mandatory grouping key (notation key § 6). Two cells share a
    stratum when, and only when, all four components agree — which is the
    condition under which their metrics were produced by the same instrument
    against the same reference at the same tolerance over the same tiles.

    Attributes:
        corpus: ``4-map-gs`` or ``55-map``.
        reference: ``curator`` / ``student`` / ``canonical`` / ``standardised``.
        buffer_m: Evaluation buffer radius in metres.
        frame_id: Evaluation frame id, e.g. ``era-2-487``.
    """

    corpus: str
    reference: str
    buffer_m: int
    frame_id: str

    @property
    def stratum_id(self) -> str:
        """Return the canonical string form, e.g. ``4-map-gs|curator|20m|era-2-487``.

        The pipe separator is chosen because no component vocabulary contains
        one, so the id round-trips through :meth:`parse` without ambiguity.
        """
        return f"{self.corpus}|{self.reference}|{self.buffer_m}m|{self.frame_id}"

    @classmethod
    def parse(cls, stratum_id: str) -> StratumKey:
        """Rebuild a key from its string form.

        Args:
            stratum_id: A value produced by :attr:`stratum_id`.

        Returns:
            The reconstructed key.

        Raises:
            ValueError: If the id does not have exactly four pipe-separated
                components with an ``<int>m`` buffer.
        """
        parts = stratum_id.split("|")
        if len(parts) != 4:
            raise ValueError(
                f"stratum_id {stratum_id!r} has {len(parts)} components, expected 4 "
                "(corpus|reference|<n>m|frame)."
            )
        corpus, reference, buffer_token, frame_id = parts
        if not buffer_token.endswith("m") or not buffer_token[:-1].isdigit():
            raise ValueError(
                f"stratum_id {stratum_id!r}: buffer component {buffer_token!r} "
                "must look like '20m'."
            )
        return cls(corpus, reference, int(buffer_token[:-1]), frame_id)

    def __str__(self) -> str:  # pragma: no cover - trivial
        """Return :attr:`stratum_id`."""
        return self.stratum_id


def refuse_cross_stratum(
    rows: Iterable[Mapping[str, Any]],
    *,
    transfer: bool = False,
    what: str = "aggregate",
) -> str:
    """Guard every derived aggregate against silently spanning strata.

    Call this before computing any mean, difference, ranking, or other derived
    number over a set of dataset rows. It is the machine-enforced half of the
    card's heterogeneity design: an aggregate over rows from more than one
    stratum is refused unless the caller explicitly declares it a transfer.

    Args:
        rows: Dataset rows, each carrying a ``stratum_id``.
        transfer: Set ``True`` only for a deliberate cross-stratum comparison,
            which must then be recorded as a transfer pair rather than a
            headline number.
        what: Name of the aggregate, quoted in the error message.

    Returns:
        The single ``stratum_id`` shared by all rows, or — when ``transfer`` is
        ``True`` and the rows do span strata — the pipe-joined sorted set of
        ids, so the caller can label the result honestly.

    Raises:
        CrossStratumAggregationError: If the rows span strata and ``transfer``
            is ``False``, or if any row lacks a ``stratum_id``.
    """
    materialised = list(rows)
    if not materialised:
        raise CrossStratumAggregationError(
            f"refusing to compute {what}: no rows were supplied, so the "
            "stratum cannot be established."
        )
    missing = [i for i, r in enumerate(materialised) if not r.get("stratum_id")]
    if missing:
        raise CrossStratumAggregationError(
            f"refusing to compute {what}: {len(missing)} row(s) carry no "
            f"stratum_id (first at index {missing[0]}). The key is mandatory."
        )
    strata = sorted({str(r["stratum_id"]) for r in materialised})
    if len(strata) == 1:
        return strata[0]
    if not transfer:
        raise CrossStratumAggregationError(
            f"refusing to compute {what} across {len(strata)} strata "
            f"({', '.join(strata)}). These cells were measured against "
            "different references, buffers, or frames, whose instruments have "
            "different noise floors. Record the comparison as an explicit "
            "transfer pair, or pass transfer=True and label the result as one."
        )
    return "|+|".join(strata)


# --------------------------------------------------------------------------- #
# Resolvers
# --------------------------------------------------------------------------- #


def resolve_reference(
    eval_metadata: Mapping[str, Any] | None,
    label: str,
    run_gt_reference: str | None,
) -> tuple[str | None, str | None, str]:
    """Resolve which ground-truth reference a condition was scored against.

    Three rules, tried in order of authority:

    1. **eval-ground-truth** — the path the evaluation itself recorded. This is
       the only rule that reads what actually happened, so it wins.
    2. **label-suffix** — an explicit ``-canonical-gt`` / ``-standardised-gt``
       suffix on the registered label. Applied only to those exact suffixes:
       labels such as ``greedy-canonical`` and ``canonical-first`` use the word
       for a CONFIG, not a reference, and must not be caught.
    3. **run-facts** — the run's nominal ``gt_reference``, mapped from the
       manifest's schema classes (``combined`` is the canonical extended GT,
       notation key § 4).

    Args:
        eval_metadata: The evaluation's ``_metadata`` block, if available.
        label: The registered condition label.
        run_gt_reference: ``gt_reference`` from ``run-facts.json``.

    Returns:
        ``(reference, reference_path, basis)``. ``reference`` is ``None`` only
        when no rule fires, and ``basis`` then reads ``unresolved``.
    """
    meta = eval_metadata or {}
    gt = (
        (meta.get("input_files") or {}).get("ground_truth")
        or (meta.get("cli_args") or {}).get("ground_truth")
        or meta.get("gt_reference")
    )
    if gt:
        term = REFERENCE_BY_FILENAME.get(Path(str(gt)).name)
        if term:
            return term, str(gt), "eval-ground-truth"

    if label.endswith("-standardised-gt"):
        return "standardised", REFERENCE_PATH["standardised"], "label-suffix"
    if label.endswith("-canonical-gt"):
        return "canonical", REFERENCE_PATH["canonical"], "label-suffix"

    schema_class = {"combined": "canonical"}.get(
        run_gt_reference or "", run_gt_reference or ""
    )
    if schema_class in REFERENCE_N_MOUNDS:
        return schema_class, REFERENCE_PATH.get(schema_class), "run-facts"
    return None, str(gt) if gt else None, "unresolved"


def resolve_geometry(
    proposer_pool: str | None,
    label: str,
    tile_size_px: int | None,
) -> dict[str, Any]:
    """Resolve the geometry cell (tile size, overlap, stride) for a condition.

    Rules, in order:

    1. **pool-name** — the pool encodes ``g<px>_ov<o>`` (the stride and 55-map
       deployment programmes).
    2. **label** — the condition label encodes ``g<px>-ov<o>`` (the grid
       campaign, whose pool name is generic).
    3. **label-overlap-percent** — an H13-style ``overlap-<pct>`` label
       combined with the run's recorded tile size.
    4. **run-facts-tile-size** — tile size only; overlap is not machine-recorded
       for the pre-geometry-programme runs, so it stays ``None`` rather than
       inheriting ``config.OVERLAP``, which is a tiling default and not a
       per-run record.

    Args:
        proposer_pool: The condition's proposer pool name.
        label: The registered condition label.
        tile_size_px: ``tile_size_px`` from ``run-facts.json``.

    Returns:
        A dict with ``geometry``, ``tile_px``, ``overlap_px``, ``stride_px``,
        and ``geometry_basis``.
    """

    def _pack(tile: int | None, overlap: int | None, basis: str) -> dict[str, Any]:
        geometry = (
            f"g{tile}_ov{overlap:03d}" if tile is not None and overlap is not None
            else None
        )
        stride = tile - overlap if tile is not None and overlap is not None else None
        return {
            "geometry": geometry,
            "tile_px": tile,
            "overlap_px": overlap,
            "stride_px": stride,
            "geometry_basis": basis,
        }

    for text, basis in ((proposer_pool or "", "pool-name"), (label, "label")):
        found = _GEOMETRY_RE.search(text)
        if found:
            return _pack(int(found.group(1)), int(found.group(2)), basis)

    pct = _OVERLAP_PCT_RE.search(label)
    if pct and tile_size_px:
        whole, frac = pct.group(1), pct.group(2)
        percent = float(f"{whole}.{frac}") if frac else float(whole)
        return _pack(tile_size_px, round(tile_size_px * percent / 100.0),
                     "label-overlap-percent")

    return _pack(tile_size_px, None, "run-facts-tile-size" if tile_size_px else "unresolved")


def resolve_basis(label: str) -> str | None:
    """Resolve the basis vocabulary term (notation key § 3) from a label.

    Only ``carried``, ``carried (post-hoc)``, and ``oracle`` are encoded in
    labels across the committed corpus. Everything else returns ``None`` rather
    than a guess — ``as-shipped`` and ``comparability`` are editorial
    judgements recorded in findings documents, not in label text.

    Args:
        label: The registered condition label.

    Returns:
        The basis term, or ``None`` where the label encodes none.
    """
    for pattern, term in _BASIS_LABEL_RULES:
        if pattern.search(label):
            return term
    return None


# --------------------------------------------------------------------------- #
# Loaders
# --------------------------------------------------------------------------- #


@dataclass
class CorpusSources:
    """Every committed source-of-truth artefact the builders read, loaded once.

    Attributes:
        repo_root: Repository root the paths were resolved against.
        registry: ``run-registry.json`` entries, keyed by ``run_id``.
        facts: ``run-facts.json`` per-run facts, keyed by ``run_id``.
        decomposition: ``run-conditions.json`` per-run condition specs.
        conditions: ``conditions-manifest.json`` rows, keyed by ``condition_id``.
        passes: ``passes-manifest.json`` rows, keyed by ``(run_id, pool)``.
        sensitivity: ``sensitivity.json`` as loaded.
        notation: The parsed canonical notation key.
        vintages: ``generated_at`` of each generated manifest, for the report.
    """

    repo_root: Path
    registry: dict[str, dict[str, Any]]
    facts: dict[str, dict[str, Any]]
    decomposition: dict[str, dict[str, Any]]
    conditions: dict[str, dict[str, Any]]
    passes: dict[tuple[str, str], list[dict[str, Any]]]
    sensitivity: dict[str, Any]
    notation: NotationKey
    vintages: dict[str, str | None] = field(default_factory=dict)

    @classmethod
    def load(cls, repo_root: Path = REPO_ROOT) -> CorpusSources:
        """Read every source artefact from disk.

        Args:
            repo_root: Repository root.

        Returns:
            A populated :class:`CorpusSources`.

        Raises:
            FileNotFoundError: If any required artefact is missing. There is no
                fallback: a builder that cannot read its inputs must stop.
        """

        def _read(rel: Path) -> Any:
            path = repo_root / rel
            if not path.exists():
                raise FileNotFoundError(
                    f"required source artefact missing: {path}. The uplift "
                    "supplement is a derivation over committed artefacts and "
                    "has no fallback for an absent input."
                )
            return json.loads(path.read_text(encoding="utf-8"))

        registry_doc = _read(RUN_REGISTRY_PATH)
        facts_doc = _read(RUN_FACTS_PATH)
        run_conditions_doc = _read(RUN_CONDITIONS_PATH)
        conditions_doc = _read(CONDITIONS_MANIFEST_PATH)
        passes_doc = _read(PASSES_MANIFEST_PATH)
        sensitivity_doc = _read(SENSITIVITY_PATH)

        passes: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for row in passes_doc["passes"]:
            passes.setdefault((row["run_id"], row["proposer_pool"]), []).append(row)
        for bucket in passes.values():
            bucket.sort(key=lambda r: r["pass_n"])

        return cls(
            repo_root=repo_root,
            registry={e["run_id"]: e for e in registry_doc["registry"]},
            facts=facts_doc["facts"],
            decomposition=run_conditions_doc["decomposition"],
            conditions={c["condition_id"]: c for c in conditions_doc["conditions"]},
            passes=passes,
            sensitivity=sensitivity_doc,
            notation=NotationKey(repo_root / NOTATION_KEY_PATH),
            vintages={
                "run-registry.json": registry_doc.get("generated_at"),
                "conditions-manifest.json": conditions_doc.get("generated_at"),
                "passes-manifest.json": passes_doc.get("generated_at"),
            },
        )

    def pool_modality(self, run_id: str, pool: str) -> str | None:
        """Return the hand-authored modality of a proposer pool, if recorded.

        ``run-conditions.json`` records pools in two shapes: the older entries
        map the pool name straight to a modality string, the newer ones to a
        ``{modality, path}`` dict. Both are hand-authored and outrank anything
        inferred from a config snapshot.

        Args:
            run_id: The run.
            pool: The proposer pool name.

        Returns:
            ``"image"``/``"text"``, or ``None`` where the run records no pools.
        """
        pools = (self.decomposition.get(run_id) or {}).get("proposer_pools") or {}
        spec = pools.get(pool)
        if isinstance(spec, str):
            return spec
        if isinstance(spec, Mapping):
            value = spec.get("modality")
            return str(value) if value else None
        return None

    def pool_directory(self, run_id: str, pool: str) -> Path | None:
        """Locate a proposer pool's output directory on disk.

        The decomposition records pool paths in two shapes (a bare modality
        string in the older entries, a ``{modality, path}`` dict in the newer
        ones), and six runs record no pools at all while their conditions still
        name one. The fallbacks below cover the conventional layouts; an
        unresolved pool returns ``None`` and the caller records it as blocked
        rather than guessing a path.

        Args:
            run_id: The run.
            pool: The proposer pool name.

        Returns:
            The absolute pool directory, or ``None`` if none of the candidate
            layouts exists.
        """
        entry = self.registry.get(run_id)
        if entry is None:
            return None
        run_dir = self.repo_root / entry["directory_path"]
        pools = (self.decomposition.get(run_id) or {}).get("proposer_pools") or {}
        spec = pools.get(pool)
        candidates: list[Path] = []
        if isinstance(spec, Mapping) and spec.get("path"):
            candidates.append(run_dir / str(spec["path"]))
        candidates += [run_dir / "proposer" / pool, run_dir / pool]
        for candidate in candidates:
            if candidate.is_dir():
                return candidate
        return None


@dataclass(frozen=True)
class ScoringRecipe:
    """How a committed evaluation was produced, recovered from its own artefact.

    A gap-fill rung must be scored exactly the way its parent cell was, or the
    two are not comparable and the "uplift" between them measures the scorer as
    much as the model. Rather than inventing a recipe, the worklist builders
    read the source evaluation's recorded invocation and swap only the
    detections path and the output directory.

    Attributes:
        engine: ``evaluate_detections`` or ``corrected_f1_multi_buffer``.
        buffers: Buffer radii in metres the source evaluation reported.
        bootstrap: Bootstrap iterations.
        seed: Random seed.
        ground_truth: The reference the source consumed (``evaluate_detections``).
        bounds: The evaluation bounds — the frame.
        extra: Engine-specific inputs (the corrected-F1 review CSVs, etc.).
        recovered_from: The artefact the recipe was read out of.
    """

    engine: str
    buffers: tuple[int, ...]
    bootstrap: int | None
    seed: int | None
    ground_truth: str | None
    bounds: str | None
    extra: Mapping[str, str] = field(default_factory=dict)
    recovered_from: str = ""


def read_scoring_recipe(
    repo_root: Path, eval_path: str | None, document: Mapping[str, Any] | None
) -> tuple[ScoringRecipe | None, str | None]:
    """Recover the scoring recipe behind a committed evaluation.

    Two shapes are recognised, in order:

    1. **Direct** — ``_metadata.cli_args`` written by
       ``scripts/evaluate_detections.py``.
    2. **Adapted** — ``_metadata.source`` / ``_metadata.source_summary`` naming a
       corrected-F1 engine summary, whose ``metadata.input_paths`` block carries
       the real invocation. The adapters are deterministic transforms, so the
       summary is the authority.

    Args:
        repo_root: Repository root, for resolving the summary hop.
        eval_path: Repo-relative path of the evaluation (for provenance).
        document: The parsed evaluation document.

    Returns:
        ``(recipe, blocked_reason)``. Exactly one is ``None``.
    """
    if document is None:
        return None, "the condition spec records no readable evaluation artefact"
    meta = document.get("_metadata") or {}
    buffers = tuple(
        int(b["buffer_metres"]) for b in (document.get("summary") or {}).get("buffers", [])
    )

    cli = meta.get("cli_args")
    if cli:
        bootstrap = meta.get("bootstrap") or {}
        return ScoringRecipe(
            engine="evaluate_detections",
            buffers=tuple(cli.get("buffers") or buffers),
            bootstrap=cli.get("bootstrap") or bootstrap.get("n_iterations"),
            seed=cli.get("seed") or bootstrap.get("seed"),
            ground_truth=str(cli["ground_truth"]) if cli.get("ground_truth") else None,
            bounds=str(cli["bounds"]) if cli.get("bounds") else None,
            recovered_from=eval_path or "",
        ), None

    summary_rel = meta.get("source") or meta.get("source_summary")
    if not summary_rel:
        return None, (
            "the source evaluation records neither a CLI invocation nor an "
            "engine summary, so its recipe cannot be reproduced"
        )
    summary_path = repo_root / str(summary_rel)
    if not summary_path.exists():
        return None, f"the named engine summary is missing: {summary_rel}"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    block = summary.get("metadata") or {}
    paths = block.get("input_paths") or {}
    if not paths:
        return None, f"{summary_rel} records no input_paths block"

    def _rel(value: str | None) -> str | None:
        """Make an absolute recorded path repo-relative where possible.

        The corrected-F1 engine records absolute paths. Re-relativising on the
        repository directory NAME fails inside a worktree (whose directory is
        named for the branch, not the repo), so the anchor is the first
        top-level project directory segment instead — stable wherever the
        checkout lives.
        """
        if not value:
            return None
        text = str(value).replace("\\", "/")
        match = _REPO_RELATIVE_RE.search(text)
        return text[match.start(1):] if match else text

    return ScoringRecipe(
        engine="corrected_f1_multi_buffer",
        buffers=buffers,
        bootstrap=block.get("bootstrap_n"),
        seed=block.get("seed"),
        ground_truth=_rel(paths.get("student_gt")),
        bounds=_rel(paths.get("bounds")),
        extra={
            name: _rel(paths[name]) or ""
            for name in ("review_yesterday", "review_today", "extension_csv")
            if paths.get(name)
        },
        recovered_from=str(summary_rel),
    ), None


def iter_condition_specs(
    sources: CorpusSources,
) -> Iterable[tuple[str, str, dict[str, Any]]]:
    """Yield every registered condition spec in registry order.

    The spine of the flatten. ``run-conditions.json`` is the hand-authored
    source of truth for what a condition IS; ``conditions-manifest.json`` is the
    generated metrics carrier and lags it whenever runs land between
    regenerations. Iterating the spec rather than the manifest is what makes
    the gap visible instead of invisible.

    Args:
        sources: Loaded corpus sources.

    Yields:
        ``(run_id, condition_id, spec)`` triples.
    """
    for run_id in sources.registry:
        entry = sources.decomposition.get(run_id)
        if entry is None:
            continue
        for spec in entry.get("conditions", []):
            yield run_id, f"{run_id}::{spec['label']}", spec


# --------------------------------------------------------------------------- #
# CSV writing
# --------------------------------------------------------------------------- #


def write_csv(
    path: Path,
    rows: Sequence[Mapping[str, Any]],
    columns: Sequence[str],
    notation: NotationKey,
) -> None:
    """Validate columns against the notation key, then write a CSV.

    Validation happens before the file is opened, so a rejected column list
    never leaves a half-written artefact behind.

    Args:
        path: Destination file; parent directories are created.
        rows: Row mappings. Missing keys are written as the empty string.
        columns: Column order, and the set validated against the key.
        notation: The loaded canonical key.

    Raises:
        UnknownColumnError: If any column is unsanctioned.
    """
    notation.validate(columns)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({c: _csv_value(row.get(c)) for c in columns})


def _csv_value(value: Any) -> Any:
    """Render a Python value for CSV in a stable, re-readable form.

    Booleans become ``true``/``false`` (lower case, so the column reads the same
    in Python, R, and a spreadsheet); ``None`` becomes the empty string, which
    every reader treats as missing rather than as zero.

    Args:
        value: The value to render.

    Returns:
        The CSV cell contents.
    """
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return value
