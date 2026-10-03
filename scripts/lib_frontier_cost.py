#!/usr/bin/env python3
"""
The frontier cost axis: configuration costs at one uniform tier, from the register.

Why this module exists
----------------------
The project's Pareto frontiers rank configurations by cost against
detection quality, and the frontier is a paper result. Until 2026-10-04
every frontier's cost axis was hand-entered (``FAMILY_COST`` in
``scripts/final_board_build.py``; per-pass and per-call constants in
``scripts/build_pareto_v2.py`` and the K-ladder builders), on a mixed basis.
This module derives each cost from the passes register
(``results/passes-manifest.json``), so every figure traces to named
register rows.

The PI's ruling D19 (amended 2026-10-04,
``planning/pi-decisions-2026-09-20.md``): every configuration's own tokens
are priced at ONE uniform discounted tier, so no configuration is penalised
for how it happened to be billed (the cached-path defect, or runs made
before the project knew of discounts). Flex and batch carry identical input
and output rates for every model on the rate card (Gemini 3.5 Flash's
cached input differs by half a hundredth of a cent per million tokens; no
configuration here runs it), so the uniform tier is ``flex``. The
register's own ``cost_usd`` (as billed) is untouched; this is a second,
counterfactual price of the same tokens.

Units
-----
- **Proposer pass**: a register pass's own fragments, each re-priced at the
  uniform tier with its own model and date, read exactly as the register
  reads them (``lib_pass_cost.fragment_usage``: recovery fragments
  included, recovery-merged metas from their per-item sums).
- **Verifier call**: a leg's fragments re-priced the same way, divided by
  the verifications it produced: the entries of its ``probabilities.json``,
  ONE PER CALL (a multi-iteration leg keys them per iteration,
  ``candidate_00005_iter1`` to ``_iter5``), less any merged in from a leg
  whose cost this row does not carry. Retries are spend, so they stay in
  the numerator: T03's leg made 10,539 requests for 9,910 results. A rung
  of N candidates is N x the leg's iterations calls.

Floors
------
A leg whose main record a cleanup overwrote is a lower bound in the
register (``audited-lower-bound``). D19: such a floor is completed from
comparable legs' per-candidate cost, labelled as such. The comparables are
NOMINATED per floor in the mapping file
(``data/pricing/frontier-configurations.json``), never discovered: a blind
search pooled 96 legs across corpora and campaigns (and, before the
effective temperature was read, two legs at temperature 0.5 and 1.0). Each
nominee must have complete tokens (``audited`` or ``audited-upper-bound``,
whose only unknown is the billed tier, irrelevant here) and an IDENTICAL
verifier configuration (model, effective temperature, thinking level,
system-instruction hash, prompt version), or it is refused. The unit is
pooled: the nominees' summed cost over their summed verifications.
Design: ``planning/wp4b-frontier-cost-design-2026-10-04.md``.

Usage::

    from scripts.lib_frontier_cost import FrontierCoster
    coster = FrontierCoster()
    coster.proposer_unit("stride-55map-2026-08-25", "g384_ov128_55map").usd
    coster.configuration_cost(spec)       # a mapping entry, see that method

Created: 2026-10-04 (WP4b of the cost accounting plan)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import gzip
import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from scripts.lib_cost import is_unrecorded, price_usage, resolve_model
from scripts.lib_pass_cost import fragment_usage

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REGISTER = PROJECT_ROOT / "results" / "passes-manifest.json"
MAPPING = PROJECT_ROOT / "data" / "pricing" / "frontier-configurations.json"

#: The gold-standard (GS) and 55-map corpora, in tiles: a 55-map pass unit is
#: carried to GS scale by GS/55-map (the June audit's convention).
TILES_GS = 487
TILES_55MAP = 8541

#: The one tier every configuration is priced at (D19, amended 2026-10-04).
UNIFORM_TIER = "flex"

#: Register bases whose tokens are the leg's whole spend. An upper bound's
#: only unknown is the BILLED tier, which the uniform tier makes irrelevant.
COMPLETE_BASES = ("audited", "audited-upper-bound")

#: The configuration fields two verifier legs must share to be comparable.
FINGERPRINT_FIELDS = ("model", "temperature", "thinking_level", "system_instruction_hash",
                      "version")


class FrontierCostError(ValueError):
    """A configuration cost that cannot be derived honestly from the register."""


@dataclass(frozen=True)
class Priced:
    """A cost at the uniform tier, with the register rows it came from.

    Attributes:
        usd: The cost in US dollars.
        sources: The register ``pass_id``s that priced it.
        basis: ``measured`` (the rows' own tokens) or ``completed`` (a floor
            leg's verifications at comparable legs' unit, D19).
        notes: How it was reached, for the mapping's provenance.
    """

    usd: float
    sources: tuple[str, ...]
    basis: str = "measured"
    notes: tuple[str, ...] = ()

    def __add__(self, other: Priced) -> Priced:
        basis = "completed" if "completed" in (self.basis, other.basis) else "measured"
        return Priced(self.usd + other.usd, self.sources + other.sources, basis,
                      self.notes + other.notes)


@dataclass
class Leg:
    """A verifier leg at the uniform tier.

    Attributes:
        pass_id: Its register key.
        usd: Its fragments re-priced at the uniform tier.
        verifications: Verifier calls it produced: its results entries (one per
            call), less those merged in from a leg this row does not price.
        iterations: Calls per candidate (``probabilities.json`` ``iterations``).
        complete: Whether its tokens are its whole spend (not a floor).
        fingerprint: Its verifier configuration, for the comparables test.
    """

    pass_id: str
    usd: float
    verifications: int
    complete: bool
    iterations: int = 1
    fingerprint: tuple[Any, ...] = field(default=())


def _load(path: Path) -> Any:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as fh:
        return json.load(fh)


class FrontierCoster:
    """Prices frontier configurations at the uniform tier from the register.

    Args:
        register_path: The passes register (tests pass a fixture).
        repo_root: Where the register's repository-relative paths resolve.
    """

    def __init__(self, register_path: Path = REGISTER, repo_root: Path = PROJECT_ROOT) -> None:
        self.root = repo_root
        self.rows: dict[str, dict[str, Any]] = {
            r["pass_id"]: r for r in _load(register_path)["passes"]}
        # Memoised per instance: the comparables scan reads every leg once.
        self._pass_usd: dict[str, float] = {}
        self._legs: dict[tuple[str, str], Leg] = {}

    # -- passes --------------------------------------------------------------

    def pass_usd(self, pass_id: str) -> float:
        """One register pass's own fragments, re-priced at the uniform tier.

        Raises:
            FrontierCostError: When a fragment recorded no usage or cannot be
                priced: the pass's cost would be silently short.
        """
        if pass_id in self._pass_usd:
            return self._pass_usd[pass_id]
        row = self.rows[pass_id]
        total = 0.0
        for frag in (row.get("cost_source") or {}).get("fragments") or []:
            meta = _load(self.root / frag["meta"])
            usage, _ = fragment_usage(meta)
            # A usage block of zeros is unrecorded (D12), not free: refuse it
            # as firmly as a missing one.
            if not usage or is_unrecorded(usage) or frag.get("unpriceable") \
                    or not frag.get("priced_at"):
                raise FrontierCostError(f"{pass_id}: fragment {frag['meta']} has no priceable "
                                        "usage, so the pass cannot be priced whole")
            model = frag.get("model") or resolve_model(frag["model_recorded"])
            total += price_usage(usage, model, UNIFORM_TIER,
                                 at=frag["priced_at"])["total_cost_usd"]
        if not (row.get("cost_source") or {}).get("fragments"):
            raise FrontierCostError(f"{pass_id}: no fragments to price")
        self._pass_usd[pass_id] = total
        return total

    def pool_passes(self, run_id: str, pool: str) -> list[str]:
        """The register's proposer passes for a run's pool, in pass order."""
        ids = [pid for pid, r in self.rows.items()
               if r["run_id"] == run_id and r["proposer_pool"] == pool
               and r.get("n_candidates_verified") is None]
        if not ids:
            raise FrontierCostError(f"no register passes for {run_id}::{pool}")
        short = [pid for pid in ids if self.rows[pid].get("cost_basis") not in COMPLETE_BASES]
        if short:
            # A published, floored or unrecorded pass's metas are not its whole
            # spend: re-pricing them would price the pass short (audit lens A).
            raise FrontierCostError(f"{run_id}::{pool} has passes whose tokens are not "
                                    f"complete: {short}")
        return sorted(ids, key=lambda p: self.rows[p].get("pass_n") or 0)

    def proposer_unit(self, run_id: str, pool: str) -> Priced:
        """The mean pass of a pool at the uniform tier."""
        ids = self.pool_passes(run_id, pool)
        usd = sum(self.pass_usd(p) for p in ids) / len(ids)
        return Priced(usd, tuple(ids), notes=(f"mean of {len(ids)} passes of {run_id}::{pool}",))

    def proposer_cost(self, run_id: str, pool: str, passes: int | None = None) -> Priced:
        """``passes`` passes of a pool: the mean pass times ``passes`` (all if None).

        A rung of N passes from a K-pass run is costed as N mean passes, the
        convention the stride and 3.7 ladders already use.
        """
        ids = self.pool_passes(run_id, pool)
        n = len(ids) if passes is None else passes
        if not 1 <= n <= len(ids):
            raise FrontierCostError(f"{run_id}::{pool} has {len(ids)} passes, asked for {n}")
        unit = self.proposer_unit(run_id, pool)
        return Priced(unit.usd * n, unit.sources,
                      notes=(f"{n} x mean pass of {run_id}::{pool} ({len(ids)} passes)",))

    # -- verifier legs -------------------------------------------------------

    def _leg_row(self, run_id: str, pool: str) -> dict[str, Any]:
        rows = [r for r in self.rows.values()
                if r["run_id"] == run_id and r["proposer_pool"] == pool
                and r.get("n_candidates_verified") is not None]
        if len(rows) != 1:
            raise FrontierCostError(f"expected one verifier leg for {run_id}::{pool}, "
                                    f"found {len(rows)}")
        return rows[0]

    def leg(self, run_id: str, pool: str) -> Leg:
        """A verifier leg's uniform-tier cost, verifications and configuration.

        The leg's verifications (calls) are read from the
        ``probabilities.json`` beside its primary meta (results times
        iterations), never from the register's request-count fallback.
        A floor's fragments may lack usage; it is still a leg, priced by
        :meth:`leg_cost` from its comparables.
        """
        if (run_id, pool) in self._legs:
            return self._legs[(run_id, pool)]
        row = self._leg_row(run_id, pool)
        frags = (row.get("cost_source") or {}).get("fragments") or []
        if not frags:
            raise FrontierCostError(f"{row['pass_id']}: no fragments")
        primary = self.root / frags[0]["meta"]
        prob = primary.parent / "probabilities.json"
        if not prob.exists():
            raise FrontierCostError(f"{row['pass_id']}: no probabilities.json beside "
                                    f"{frags[0]['meta']}, so its verifications are unknown")
        doc = _load(prob)
        # One entry per CALL: a multi-iteration leg keys its results per
        # iteration, so the iterations are already in the count (audit lens A,
        # 2026-10-04: multiplying again counted the June opmax leg 5x over).
        verifications = len(doc.get("results") or {})
        priced = {(self.root / f["meta"]).resolve() for f in frags}
        for merge in doc.get("cleanup_merges") or []:
            # Results a cleanup merged in, from a leg whose cost this row does
            # not carry, would be priced at nothing: leave them out
            # (55maps-generalisation: 26 from verified-cleanup, no register row).
            source_meta = (self.root / merge["source"]).parent / "run.meta.json"
            if source_meta.resolve() not in priced:
                verifications -= int(merge.get("added") or 0)
        iterations = max(int(doc.get("iterations") or 1), 1)
        complete = row.get("cost_basis") in COMPLETE_BASES
        config = dict(_load(primary).get("configuration") or {})
        if config.get("model"):
            # One spelling per model ("gemini-3-flash" is "gemini-3-flash-preview").
            config["model"] = resolve_model(config["model"])
        if config.get("temperature_effective") is not None:
            # E55: where a CLI override changed the temperature, the meta's
            # ``temperature`` is the config file's and the run's is here
            # (verifier-t-pilot's t0-5 and t1-0 legs record 0.0 beside it).
            config["temperature"] = config["temperature_effective"]
        fingerprint = tuple(config.get(k) for k in FINGERPRINT_FIELDS)
        usd = self.pass_usd(row["pass_id"]) if complete else 0.0
        leg = Leg(pass_id=row["pass_id"], usd=usd, verifications=verifications,
                  complete=complete, fingerprint=fingerprint, iterations=iterations)
        self._legs[(run_id, pool)] = leg
        return leg

    def eligible_comparables(self, fingerprint: tuple[Any, ...]) -> list[Leg]:
        """Every complete verifier leg with this exact configuration (for review, not pooling)."""
        if not fingerprint or any(v is None for v in fingerprint):
            raise FrontierCostError(f"incomplete verifier configuration {fingerprint}")
        out = []
        for row in self.rows.values():
            if row.get("n_candidates_verified") is None or \
                    row.get("cost_basis") not in COMPLETE_BASES:
                continue
            try:
                leg = self.leg(row["run_id"], row["proposer_pool"])
            except FrontierCostError:
                continue
            if leg.fingerprint == fingerprint and leg.verifications:
                out.append(leg)
        return sorted(out, key=lambda leg: leg.pass_id)

    def _nominees(self, floor: Leg, comparables: list[dict[str, str]] | None) -> list[Leg]:
        """The nominated comparables for a floor, each checked; refuses any that do not qualify."""
        if not comparables:
            raise FrontierCostError(f"{floor.pass_id} is a floor: nominate comparable legs "
                                    "to complete it (D19)")
        if any(v is None for v in floor.fingerprint):
            raise FrontierCostError(f"{floor.pass_id}: incomplete verifier configuration "
                                    f"{floor.fingerprint}, so no leg can be shown comparable")
        out = []
        for ref in comparables:
            leg = self.leg(ref["run_id"], ref["pool"])
            if not leg.complete:
                raise FrontierCostError(f"nominated comparable {leg.pass_id} is itself a floor")
            if leg.fingerprint != floor.fingerprint:
                raise FrontierCostError(
                    f"nominated comparable {leg.pass_id} has configuration {leg.fingerprint}, "
                    f"not the floor's {floor.fingerprint}")
            if not leg.verifications:
                raise FrontierCostError(f"nominated comparable {leg.pass_id}: no verifications")
            out.append(leg)
        return out

    def candidate_unit(self, run_id: str, pool: str,
                       comparables: list[dict[str, str]] | None = None) -> Priced:
        """US$ per verifier call for a leg: its own, or its nominees' pooled.

        A complete leg's own unit is measured (``comparables`` is ignored). A
        floor's is completed from the nominated comparables (D19), labelled
        ``completed``.
        """
        leg = self.leg(run_id, pool)
        if leg.complete:
            if not leg.verifications:
                raise FrontierCostError(f"{leg.pass_id}: no verifications")
            return Priced(leg.usd / leg.verifications, (leg.pass_id,),
                          notes=(f"{leg.pass_id}: own unit, {leg.verifications:,} "
                                 "verifications",))
        comps = self._nominees(leg, comparables)
        usd = sum(c.usd for c in comps) / sum(c.verifications for c in comps)
        return Priced(usd, tuple(c.pass_id for c in comps), "completed",
                      (f"{leg.pass_id} is a floor: unit pooled over the nominated "
                       f"{', '.join(c.pass_id for c in comps)}",))

    def leg_cost(self, run_id: str, pool: str,
                 comparables: list[dict[str, str]] | None = None) -> Priced:
        """A whole verifier leg: its own cost, or (a floor) its verifications at its nominees' unit."""
        leg = self.leg(run_id, pool)
        if leg.complete:
            return Priced(leg.usd, (leg.pass_id,),
                          notes=(f"{leg.pass_id}: own cost, {leg.verifications:,} "
                                 "verifications",))
        unit = self.candidate_unit(run_id, pool, comparables)
        return Priced(leg.verifications * unit.usd, (leg.pass_id,) + unit.sources, "completed",
                      unit.notes + (f"{leg.verifications:,} verifications x pooled unit",))

    # -- configurations --------------------------------------------------------

    def configuration_cost(self, spec: dict[str, Any]) -> Priced:
        """A frontier configuration's cost from its mapping entry.

        Args:
            spec: ``{"proposer": [{"run_id", "pool", "passes"?}, ...],
                "verifier": {"leg": {"run_id", "pool"}}}`` for a full run, or
                ``"verifier": {"unit_from": {"run_id", "pool"},
                "candidates": int}`` for a rung whose union of ``candidates``
                would be verified at that leg's unit. Either verifier form
                takes ``"comparables": [{"run_id", "pool"}, ...]``, required
                when the leg is a floor.

        Returns:
            The summed cost with every register row it used.
        """
        total: Priced | None = None
        for part in spec.get("proposer") or []:
            cost = self.proposer_cost(part["run_id"], part["pool"], part.get("passes"))
            total = cost if total is None else total + cost
        ver = spec.get("verifier")
        if ver:
            comps = ver.get("comparables")
            if "leg" in ver:
                cost = self.leg_cost(ver["leg"]["run_id"], ver["leg"]["pool"], comps)
            else:
                ref = ver["unit_from"]
                unit = self.candidate_unit(ref["run_id"], ref["pool"], comps)
                n = int(ver["candidates"])
                calls = n * self.leg(ref["run_id"], ref["pool"]).iterations
                cost = Priced(unit.usd * calls, unit.sources, unit.basis,
                              unit.notes + (f"{n:,} union candidates, {calls:,} calls x unit",))
            total = cost if total is None else total + cost
        if total is None:
            raise FrontierCostError(f"configuration has neither proposer nor verifier: {spec}")
        return total


    def unit(self, spec: dict[str, Any]) -> Priced:
        """A named unit cost from the mapping's ``units`` section.

        Args:
            spec: ``{"kind": "mean_pass", "pools": [{"run_id", "pool"}, ...]}``
                for the mean pass over every listed pool's passes (the June
                audit's "ten measured minimal passes" spans two runs), or
                ``{"kind": "pooled_candidate", "legs": [{"run_id", "pool"}, ...]}``
                for the pooled per-candidate unit of complete legs that share
                ONE verifier configuration.

        Raises:
            FrontierCostError: For an unknown kind, a floor among the legs, or
                legs of different configurations.
        """
        if spec.get("kind") == "mean_pass":
            ids = [pid for ref in spec["pools"] for pid in self.pool_passes(ref["run_id"],
                                                                             ref["pool"])]
            usd = sum(self.pass_usd(p) for p in ids) / len(ids)
            return Priced(usd, tuple(ids), notes=(f"mean of {len(ids)} passes",))
        if spec.get("kind") == "pooled_candidate":
            legs = [self.leg(ref["run_id"], ref["pool"]) for ref in spec["legs"]]
            floors = [leg.pass_id for leg in legs if not leg.complete]
            if floors:
                raise FrontierCostError(f"pooled unit over floors: {floors}")
            if len({leg.fingerprint for leg in legs}) != 1:
                raise FrontierCostError("pooled unit over legs of different configurations: "
                                        f"{sorted({leg.fingerprint for leg in legs}, key=str)}")
            usd = sum(leg.usd for leg in legs) / sum(leg.verifications for leg in legs)
            return Priced(usd, tuple(leg.pass_id for leg in legs),
                          notes=(f"pooled over {len(legs)} complete legs",))
        raise FrontierCostError(f"unknown unit kind {spec.get('kind')!r}")


@lru_cache(maxsize=1)
def default_coster() -> FrontierCoster:
    """The coster over the committed register, built once per process."""
    return FrontierCoster()


@lru_cache(maxsize=1)
def gs_units() -> dict[str, Priced]:
    """The GS-scale unit costs the Pareto v2 and K-ladder builders share.

    Returns:
        ``min_pass`` and ``high_pass`` (the 55-map Gemini 3 Flash pass units
        scaled by 487/8,541), ``g37_pass`` (the GS 3.7 screen pool's own
        mean pass) and ``vf_call`` (the Gemini 3 Flash verifier per
        candidate), each with the register rows it came from.
    """
    units = json.loads(MAPPING.read_text(encoding="utf-8"))["units"]
    coster = default_coster()
    scale = TILES_GS / TILES_55MAP

    def scaled(name: str) -> Priced:
        u = coster.unit(units[name])
        return Priced(u.usd * scale, u.sources, u.basis,
                      u.notes + (f"x {TILES_GS}/{TILES_55MAP} to GS scale",))

    return {"min_pass": scaled("min_pass_55map"), "high_pass": scaled("high_pass_55map"),
            "g37_pass": coster.unit(units["g37_pass_gs"]),
            "vf_call": coster.unit(units["g3_verifier_candidate"])}


@lru_cache(maxsize=1)
def phase2_pass_units() -> dict[str, tuple[Priced, str]]:
    """Each Phase 2 K-ladder family's GS pass unit and its anchor label.

    PI ruling 2026-10-04: a family is priced at its OWN measured GS passes
    where the register records them; a T0.7 text family (no recorded GS
    tokens) at the 55-map T0.7 measurement of the same configuration, scaled;
    a T0.7 image family at the mean of its own T0.3 and T1.0 passes,
    labelled interpolated.

    Returns:
        ``{family: (unit, anchor)}`` from the mapping's
        ``k_ladder_phase2_pass_units``.
    """
    specs = json.loads(MAPPING.read_text(encoding="utf-8"))["k_ladder_phase2_pass_units"]
    coster, named = default_coster(), gs_units()
    out = {}
    for family, spec in specs.items():
        unit = named[spec["unit"]] if spec["kind"] == "named" else coster.unit(spec)
        out[family] = (unit, spec["anchor"])
    return out
