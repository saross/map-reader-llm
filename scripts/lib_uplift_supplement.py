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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

__all__ = [
    "COLUMN_EXTENSIONS",
    "ORIGINAL_PUBLICATION_DATE",
    "ColumnExtension",
    "CorpusSources",
    "CrossStratumAggregationError",
    "NotationKey",
    "PRIMARY_BUFFER_BY_CORPUS",
    "REFERENCE_BY_FILENAME",
    "ScoringRecipe",
    "StratumKey",
    "UnknownColumnError",
    "VerifierManifest",
    "collect_verifier_manifests",
    "condition_stratum",
    "lineage_match_count",
    "path_matches_lineage",
    "generated_doc_banner",
    "iter_condition_specs",
    "match_verifier_manifest",
    "read_scoring_recipe",
    "refuse_cross_stratum",
    "resolve_basis",
    "resolve_geometry",
    "resolve_reference",
    "resolve_scope",
    "shell_strip",
    "validate_columns",
    "write_csv",
]

#: Date the generated documents in ``results/uplift-supplement/`` were first
#: published. PINNED, not ``datetime.now``: the project's Document Revision
#: Policy wants an "Original publication" entry that stays put, and a builder
#: that restamps it on every rebuild destroys exactly the baseline the policy
#: exists to preserve. The regeneration timestamp is stamped separately.
ORIGINAL_PUBLICATION_DATE = "2026-08-29"

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
        _ext("reference_consumed_path", "anti-confabulation",
             "The path the evaluation literally recorded, where it differs from the anchor."),
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
        _ext("verifier_floor_basis", "anti-confabulation",
             "How the cell's verifier stage was matched: lineage, shell, sole, or ambiguous."),
        _ext("verified_stratum_id", "§ 6",
             "The verified cell's own stratum, keyed from its own evidence."),
        _ext("unverified_stratum_id", "§ 6",
             "The twin's stratum, keyed independently; a tripwire, not a lineage check."),
        _ext("unverified_stratum_basis", "anti-confabulation",
             "Whether the twin's stratum was derived from its own cell or from the recipe."),
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


@dataclass(frozen=True)
class ReferenceResolution:
    """Which ground-truth reference a condition was scored against, and how.

    Attributes:
        term: The § 4 vocabulary term (``curator`` / ``student`` / ``canonical``
            / ``standardised``), or ``None`` when no rule fires.
        path: The IN-REPO reference file the term names — the re-verifiable
            anchor a reader can open. Always canonical, never the machine-local
            copy an old replay happened to consume.
        basis: Which rule fired (``eval-ground-truth`` / ``label-suffix`` /
            ``run-facts`` / ``unresolved``).
        consumed_path: The path the evaluation literally recorded, kept verbatim
            when it differs from :attr:`path`. Nine committed evaluations ran
            against a frozen replay copy under a machine-local scratch tree that
            no longer exists; publishing that as the anchor would hand a reader
            a dead path, so it is preserved here and the anchor stays canonical.
    """

    term: str | None
    path: str | None
    basis: str
    consumed_path: str | None = None


def resolve_reference(
    eval_metadata: Mapping[str, Any] | None,
    label: str,
    run_gt_reference: str | None,
) -> ReferenceResolution:
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
        run_gt_reference: ``gt_reference`` from ``run-facts.json``. A value the
            § 4 vocabulary does not recognise resolves to ``None`` rather than
            being welded into a ``stratum_id`` as an unknown term — an
            unrecognised reference must surface as ``unresolved``, not as a
            plausible-looking stratum nobody can interpret.

    Returns:
        A :class:`ReferenceResolution`.
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
            canonical = REFERENCE_PATH[term]
            consumed = str(gt)
            return ReferenceResolution(
                term, canonical, "eval-ground-truth",
                consumed if consumed != canonical else None,
            )

    if label.endswith("-standardised-gt"):
        return ReferenceResolution(
            "standardised", REFERENCE_PATH["standardised"], "label-suffix"
        )
    if label.endswith("-canonical-gt"):
        return ReferenceResolution(
            "canonical", REFERENCE_PATH["canonical"], "label-suffix"
        )

    schema_class = {"combined": "canonical"}.get(
        run_gt_reference or "", run_gt_reference or ""
    )
    if schema_class in REFERENCE_N_MOUNDS:
        return ReferenceResolution(
            schema_class, REFERENCE_PATH[schema_class], "run-facts"
        )
    return ReferenceResolution(None, None, "unresolved", str(gt) if gt else None)


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
        # Explicit None checks throughout: `seed` is legitimately 0 in some
        # recipes and `bootstrap` could be, and an `or` chain silently replaces
        # a recorded 0 with the project default — which is a different
        # experiment, quietly.
        bootstrap_block = meta.get("bootstrap") or {}
        recorded_bootstrap = cli.get("bootstrap")
        if recorded_bootstrap is None:
            recorded_bootstrap = bootstrap_block.get("n_iterations")
        recorded_seed = cli.get("seed")
        if recorded_seed is None:
            recorded_seed = bootstrap_block.get("seed")
        recorded_buffers = cli.get("buffers")
        return ScoringRecipe(
            engine="evaluate_detections",
            buffers=tuple(recorded_buffers if recorded_buffers else buffers),
            bootstrap=recorded_bootstrap,
            seed=recorded_seed,
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


def resolve_scope(
    sources: CorpusSources, run_id: str, condition_id: str
) -> dict[str, Any]:
    """Resolve the evaluation scope (frame) that actually applies to a condition.

    The run's nominal scope is the default, but a condition may override it: the
    conditions manifest carries ``scope_override`` for the ~2 % of cells
    evaluated on a different frame from their run (two ``verifier-robustness``
    cells run at 256 px on the 1,032-tile frame while the run is nominally
    era-2-487). Reading the run's scope alone puts those cells in the wrong
    stratum, which is the one error the whole design exists to prevent — so all
    three builders resolve the frame through this one function.

    Args:
        sources: Loaded corpus sources.
        run_id: The run.
        condition_id: The condition, as ``run_id::label``.

    Returns:
        The scope block: ``test_set_id``, ``bounds_path``, ``n_test_tiles``, …
    """
    override = (sources.conditions.get(condition_id) or {}).get("scope_override")
    if override:
        return dict(override)
    return dict(sources.facts.get(run_id, {}).get("scope") or {})


def condition_stratum(
    sources: CorpusSources,
    run_id: str,
    condition_id: str,
    spec: Mapping[str, Any],
    eval_metadata: Mapping[str, Any] | None,
) -> tuple[StratumKey, ReferenceResolution, dict[str, Any]]:
    """Build one condition's stratum key from its own evidence.

    The single place a ``stratum_id`` is constructed. Every builder calls it, so
    a cell lands in the same stratum whichever table it appears in — and, in the
    pairing worklist, so that the two sides of a pair are keyed INDEPENDENTLY
    and the cross-stratum guard has something real to check.

    Args:
        sources: Loaded corpus sources.
        run_id: The run.
        condition_id: The condition, as ``run_id::label``.
        spec: The condition spec from ``run-conditions.json``.
        eval_metadata: The condition evaluation's ``_metadata`` block, if read.

    Returns:
        ``(key, reference_resolution, scope)``.
    """
    facts = sources.facts.get(run_id, {})
    reference = resolve_reference(
        eval_metadata, str(spec["label"]), facts.get("gt_reference")
    )
    scope = resolve_scope(sources, run_id, condition_id)
    corpus = facts.get("corpus")
    key = StratumKey(
        corpus=corpus or "unknown",
        reference=reference.term or "unknown",
        buffer_m=PRIMARY_BUFFER_BY_CORPUS.get(corpus or "", 0),
        frame_id=scope.get("test_set_id") or "unknown",
    )
    return key, reference, scope


# --------------------------------------------------------------------------- #
# Verifier coverage
# --------------------------------------------------------------------------- #

#: Path-segment PREFIXES marking a smoke-test tree. Their manifests describe
#: 12-candidate rehearsals, not the campaign, and one of them
#: (``_smoke/384-...-1of5-union``) carries a vote-1 candidate that would drag a
#: real stage's measured floor to 1 and flip a blocked verdict to derivable. A
#: prefix rule rather than an allowlist: a new ``smoke-`` tree must be excluded
#: the day it lands, not the day someone remembers to extend a list.
_SMOKE_SEGMENT_PREFIXES = ("_smoke", "smoke-")

#: Property keys under which a candidate manifest records the vote count its
#: candidate arrived with. Two vocabularies are in the committed corpus:
#: ``vote_count`` in most campaigns and ``proposer_votes`` in the
#: ``e47-propose-brief`` ladder. Reading only the first excluded eight real
#: stages under a reason that was not true of them.
_VOTE_COUNT_KEYS = ("vote_count", "proposer_votes")

#: A consensus shell named in a condition label: ``union``, ``4of5``, ``ge3of5``,
#: ``16of30``. This is the token that separates two verifier stages sharing one
#: proposer pool, which the pool name alone cannot do.
_SHELL_TOKEN_RE = re.compile(r"(?:^|-)(union|ge\d+of\d+|\d+of\d+)(?:-|$)")

#: Delimiters a shell token must sit between when matched against a path or a
#: source name. Unbounded containment makes ``3of5`` match ``ge3of5`` and
#: ``13of50``, which silently merges distinct stages.
_DELIMITERS = "-_/."

#: Tokens too generic to identify a verifier lineage. Deliberately NARROW:
#: modality and thinking words ("text", "image", "high", "minimal") look
#: generic but are exactly what separates one verifier stage from another in
#: the pv-diag-384 tree, so they stay available as tokens. Only words that
#: describe the CELL rather than its lineage are removed.
_LINEAGE_STOPWORDS = frozenset({
    "verified", "verify", "verifier", "adv", "adversarial", "paired", "gt",
    "canonical", "standardised", "carried", "oracle", "posthoc", "consensus",
    "best", "primary", "full", "scope", "opmax",
})

#: Trailing vote-shell suffix on a proposer-pool name (``flash-high-text-1of5``
#: → stem ``flash-high-text``). The pool is named for the shell it was BUILT
#: at, while its verifier stage is named for the shell it was VERIFIED at, so
#: the stem is what the two have in common.
_POOL_STEM_RE = re.compile(r"^(.*?)-(?:ge)?\d+of\d+$")


@dataclass(frozen=True)
class VerifierManifest:
    """One verifier stage's candidate manifest, summarised.

    Attributes:
        path: Repo-relative path of the ``candidate_manifest.json``.
        source_basename: Basename of the pre-verifier set it cropped from.
        min_vote: Lowest ``vote_count`` the verifier actually processed.
        max_vote: Highest.
        n_candidates: How many candidates it cropped.
    """

    path: str
    source_basename: str
    min_vote: int
    max_vote: int
    n_candidates: int


def collect_verifier_manifests(
    run_dir: Path, repo_root: Path
) -> tuple[list[VerifierManifest], list[str]]:
    """Summarise every real candidate manifest under a run.

    Args:
        run_dir: The run's output directory.
        repo_root: Repository root, so paths are recorded relative.

    Returns:
        ``(manifests, skipped)``. ``manifests`` holds only those recording
        integer vote counts, smoke trees excluded. ``skipped`` names every
        manifest that could not be read or carried no vote counts, with the
        reason — a silently dropped manifest can RAISE a measured floor and
        flip a verdict, so the count is published rather than swallowed.
    """
    manifests: list[VerifierManifest] = []
    skipped: list[str] = []
    for path in sorted(run_dir.rglob("candidate_manifest.json")):
        relative = str(path.relative_to(repo_root))
        smoke = [
            segment for segment in path.parts
            if segment.lower().startswith(_SMOKE_SEGMENT_PREFIXES)
        ]
        if smoke:
            skipped.append(
                f"{relative}: smoke-test tree (path segment {smoke[0]!r}), "
                "excluded by design"
            )
            continue
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            skipped.append(f"{relative}: unreadable ({type(error).__name__})")
            continue

        candidates = document.get("candidates", [])
        votes: list[int] = []
        for key in _VOTE_COUNT_KEYS:
            votes = [
                candidate.get("properties", {}).get(key)
                for candidate in candidates
            ]
            votes = [v for v in votes if isinstance(v, int)]
            if votes:
                break
        if not votes:
            # DIAGNOSTIC, not boilerplate. An earlier build asserted "a
            # single-pass verifier stage crops from a raw pass" of every
            # exclusion, which was false of eight e47-propose-brief stages that
            # simply used a different key. State what was actually there.
            observed = sorted({
                key
                for candidate in candidates[:200]
                for key in (candidate.get("properties") or {})
            })
            skipped.append(
                f"{relative}: no integer vote count under any of "
                f"{', '.join(_VOTE_COUNT_KEYS)}; {len(candidates)} candidate(s) "
                f"carry properties {observed or '(none)'}"
            )
            continue

        manifests.append(VerifierManifest(
            path=relative,
            source_basename=Path(str(document.get("source_geojson") or "")).name,
            min_vote=min(votes),
            max_vote=max(votes),
            n_candidates=len(candidates),
        ))
    return manifests, skipped


def _lineage_tokens(label: str, pool: str, geometry: str | None) -> list[str]:
    """Derive the tokens that identify one condition's verifier lineage.

    Args:
        label: The registered condition label.
        pool: The proposer pool name.
        geometry: The geometry cell, where resolved.

    Returns:
        Distinct tokens, longest first, with generic vocabulary removed.
    """
    tokens = {geometry or "", pool or ""}
    stem = _POOL_STEM_RE.match(pool or "")
    if stem:
        tokens.add(stem.group(1))
    for segment in re.split(r"[-_.]", label):
        if len(segment) >= 3 and segment.lower() not in _LINEAGE_STOPWORDS:
            tokens.add(segment)
    return sorted({t for t in tokens if len(t) >= 3}, key=len, reverse=True)


def match_verifier_manifest(
    manifests: Sequence[VerifierManifest],
    label: str,
    pool: str,
    geometry: str | None,
    n_passes: int,
    siblings: Sequence[tuple[str, str | None]] = (),
    pool_dir: str | None = None,
) -> tuple[VerifierManifest | None, str]:
    """Match a verified condition to the candidate manifest of ITS verifier stage.

    Verifier coverage is a property of a verifier STAGE, not of a run. Taking a
    run's minimum across every stage is wrong wherever a run verified several
    shells: ``verifier-robustness`` ran a vote >= 1 union stage alongside three
    vote >= 3 stages and one vote >= 16 stage, so the run minimum of 1 declared
    a K = 1 PV anchor derivable for cells whose verifier never saw a candidate
    below vote 3, citing a manifest belonging to a different condition.

    Three ordered filters, each narrowing the candidate set:

    1. **Union shell** — a manifest whose source is ``union_k<N>.geojson``
       belongs to the N-pass ladder rung of that name; keep only the matching N.
       Matched on the exact basename, because ``union_k1`` is a substring of
       ``union_k10``.
    2. **Consensus shell** — a ``union`` / ``<k>of<N>`` / ``ge<k>of<N>`` token in
       the condition label names the shell its verifier consumed.
    3. **Pool subtree** — where the pool verified inside its own directory,
       only those stages are its own.
    4. **Lineage tokens** — geometry, pool, and the label's own distinctive
       segments, matched by equality at segment/stem boundaries. A unique
       strict maximum wins.

    Args:
        manifests: The run's real manifests.
        label: The condition label.
        pool: The proposer pool.
        geometry: The geometry cell, where resolved.
        n_passes: N.
        siblings: Every (pool, geometry) lineage the run registers. Used
            only by the sole-manifest rule, to detect a stage that belongs
            to a DIFFERENT lineage than this cell's.
        pool_dir: Repo-relative proposer-pool directory. Where the pool
            verified inside its own subtree, those stages take precedence
            over run-level ones, which belong to whichever lineage built
            them.

    Returns:
        ``(manifest, basis)``. ``manifest`` is ``None`` when no unique match
        exists, and ``basis`` then says why — an unmatched lineage is disclosed
        as such, never resolved to the run minimum.
    """
    tokens = _lineage_tokens(label, pool, geometry)
    if not manifests:
        return None, "no-manifest"
    if len(manifests) == 1:
        # A lone manifest is not automatically THIS cell's. n1-outstanding-384
        # holds seven pools and exactly one verifier stage, sitting under the
        # `image-t0` pool directory, and the short circuit handed that image
        # stage's manifest to text cells as their evidence.
        #
        # The test is CONTRADICTION, not confirmation. Many stages name no pool
        # at all — gold-standard-v2 crops at run level from a
        # `consensus-4of5.geojson` that carries no lineage in its name — and
        # requiring positive confirmation would reject those correct matches.
        # So: reject only when the manifest positively belongs to one of the
        # run's OTHER lineages and not to this one.
        forms = _boundary_forms(manifests[0])
        mine = lineage_match_count(forms, tokens)
        theirs = max(
            (lineage_match_count(forms, _lineage_tokens("", p, g))
             for p, g in (siblings or ())
             if (p, g) != (pool, geometry)),
            default=0,
        )
        if theirs > mine:
            return None, "sole-manifest-lineage-mismatch"
        return manifests[0], "sole-manifest"

    # Union shells NARROW the field; they never terminate the search. An
    # earlier build returned `unmatched-union-shell` the moment no manifest
    # carried this cell's exact N, which discarded the eight stride-55map
    # N = 3 / N = 5 rungs even though each one's lineage directory identifies
    # its stage uniquely.
    suffix = ""
    unions = [m for m in manifests if m.source_basename.startswith("union_k")]
    others = [m for m in manifests if m not in unions]
    if unions:
        exact = [
            m for m in unions if m.source_basename == f"union_k{n_passes}.geojson"
        ]
        if exact:
            candidates = exact + others
        else:
            # No stage cropped the N-pass union. The K-pass union's candidate
            # set is a SUPERSET of the N-pass one (a candidate found in any of
            # the first N passes is found in any of K >= N), so its floor is
            # still informative about this rung — but it is a different set,
            # and the basis says so rather than passing the number off as the
            # rung's own measurement.
            candidates = unions + others
            widest = max(
                (m.source_basename for m in unions),
                key=lambda name: int(name[len("union_k"):].split(".")[0] or 0),
            )
            suffix = f"-via-{Path(widest).stem}-superset"
    else:
        candidates = list(manifests)

    if len(candidates) == 1:
        return candidates[0], f"matched-union-shell{suffix}"

    # Fusion family, applied symmetrically: a WBF-verified cell belongs to the
    # WBF verifier stage, and a greedy-verified cell belongs to a stage that is
    # NOT under the WBF tree. h8-v2 verified both fusions of the same pool, so
    # without this the two cells tie on every other token.
    wants_wbf = "wbf" in label.lower()
    by_fusion = [m for m in candidates if ("wbf" in m.path.lower()) == wants_wbf]
    if len(by_fusion) == 1:
        return by_fusion[0], f"matched-fusion-family{suffix}"
    if by_fusion:
        candidates = by_fusion

    # A pool that verified inside its OWN subtree owns those stages. Run-level
    # stages belong to whichever lineage built them, and in pv-diag-384 they
    # belong to different pools entirely: `verified/image-6of10` cropped
    # `consensus/image-1of10.geojson`, while the `flash-high-image-n5/image-t1.0`
    # pool cropped its own `image-t1.0/consensus/consensus_t1.geojson`. Token
    # scoring cannot separate those — both are image, both carry the shell —
    # so containment in the pool directory decides it.
    #
    # This runs AFTER the fusion filter, deliberately. The h8-v2 WBF stages sit
    # in a parallel `wbf/` tree outside the proposer pool directory, so a
    # subtree rule applied first would have pulled a WBF-verified cell back
    # onto the greedy stage.
    if pool_dir:
        prefix = pool_dir.rstrip("/") + "/"
        inside = [m for m in candidates if m.path.startswith(prefix)]
        if len(inside) == 1:
            return inside[0], f"matched-pool-subtree{suffix}"
        if inside:
            candidates = inside

    shell = _SHELL_TOKEN_RE.search(label)
    if shell:
        narrowed = [
            m for m in candidates
            if _shell_at_boundary(shell.group(1), m.path)
            or _shell_at_boundary(shell.group(1), m.source_basename)
        ]
        if len(narrowed) == 1:
            return narrowed[0], f"matched-consensus-shell{suffix}"
        if narrowed:
            candidates = narrowed

    scored = [(lineage_match_count(_boundary_forms(m), tokens), m)
              for m in candidates]
    best = max(score for score, _ in scored)
    winners = [m for score, m in scored if score == best]
    if best > 0 and len(winners) == 1:
        return winners[0], f"matched-lineage{suffix}"
    return None, "ambiguous-lineage"


def shell_strip(name: str) -> str:
    """Strip a trailing vote-shell suffix from an identifier.

    ``flash-high-text-1of5`` → ``flash-high-text``. A pool is named for the
    shell it was BUILT at and its verifier stage for the shell it was VERIFIED
    at, so the stems are what the two legitimately share.

    Args:
        name: The identifier.

    Returns:
        The stem, or the name unchanged when it carries no shell suffix.
    """
    match = _POOL_STEM_RE.match(name)
    return match.group(1) if match else name


def _boundary_forms(manifest: VerifierManifest) -> frozenset[str]:
    """Every identifier a token may legitimately be EQUAL to.

    Matching is equality against this set, never containment. Unbounded
    containment is what let the pool ``text-1of10`` claim the stage whose source
    was ``flash-high-text-1of10.geojson`` — a different pool that merely ends
    the same way — and cite its manifest as evidence for a cell it never
    verified. Two identifiers that are not equal at a boundary are two
    identifiers.

    Args:
        manifest: The manifest under test.

    Returns:
        Path segments and the source stem, each also in shell-stripped form.
    """
    forms = set(Path(manifest.path).parts)
    if manifest.source_basename:
        forms.add(Path(manifest.source_basename).stem)
    return frozenset(forms | {shell_strip(f) for f in forms})


def lineage_match_count(forms: Iterable[str], tokens: Sequence[str]) -> int:
    """Count a cell's tokens that match an identifier set at a boundary.

    Args:
        forms: Candidate identifiers (see :func:`_boundary_forms`).
        tokens: The cell's lineage tokens.

    Returns:
        How many distinct tokens match, by equality or by shell-stripped
        equality.
    """
    haystack = set(forms)
    return sum(
        1 for t in tokens
        if t in haystack or shell_strip(t) in haystack
    )


def path_matches_lineage(path: str, tokens: Sequence[str]) -> bool:
    """Whether a file path carries a cell's lineage at a segment boundary.

    The same rule as :func:`lineage_match_count`, for the pairing builder's
    consensus and union searches, which had their own unbounded ``in`` tests.

    Args:
        path: The path under test.
        tokens: The cell's lineage tokens.

    Returns:
        True when at least one token matches a whole segment or a stem.
    """
    parts = set(Path(path).parts)
    parts |= {Path(p).stem for p in parts}
    forms = parts | {shell_strip(p) for p in parts}
    return lineage_match_count(forms, tokens) > 0


def _shell_at_boundary(shell: str, haystack: str) -> bool:
    """Whether a shell token appears in ``haystack`` delimited on both sides.

    Unbounded containment makes ``3of5`` match ``ge3of5`` and ``13of50``, which
    merges stages that verified different vote shells.

    Args:
        shell: The shell token, e.g. ``ge3of5``.
        haystack: A path or source basename.

    Returns:
        True when the token sits between delimiters or at a string edge.
    """
    return re.search(
        rf"(?:^|[{re.escape(_DELIMITERS)}]){re.escape(shell)}"
        rf"(?:[{re.escape(_DELIMITERS)}]|$)",
        haystack,
    ) is not None


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


def generated_doc_banner(reason: str, generator: str) -> list[str]:
    """Render the revision banner every generated document in the set carries.

    Two dates, each in its proper place. **Last revised** carries the date this
    build ran, because that is what a reader asking "is this current?" needs —
    the body IS revised whenever the corpus moves. **First published** carries
    :data:`ORIGINAL_PUBLICATION_DATE`, pinned, so the changelog's
    original-publication stub keeps the baseline later revisions diff against.

    An earlier build had these the wrong way round: the banner froze at the
    original date while the body changed underneath it, which is precisely the
    "is this current?" failure the policy exists to prevent.

    Args:
        reason: Short parenthetical describing what the document is.
        generator: The script that writes it.

    Returns:
        Banner lines, ready to join with newlines.
    """
    stamped = datetime.now(timezone.utc)
    return [
        f"> **Last revised**: {stamped.date().isoformat()} (regenerated from "
        f"committed artefacts by `{generator}`; {reason}). "
        "See [§ Changelog](#changelog) for revision history.",
        ">",
        f"> **First published**: {ORIGINAL_PUBLICATION_DATE}. Regenerated "
        f"{stamped.strftime('%Y-%m-%dT%H:%M:%SZ')}. This document is generated "
        "in full from committed artefacts, so its body always reflects the "
        "current corpus; git carries the content history.",
    ]


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
