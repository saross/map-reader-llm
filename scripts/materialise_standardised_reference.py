#!/usr/bin/env python3
"""Materialise the standardised 55-map reference from the instruction set.

The final step of ruling-21 application
(`planning/ruling21-application-spec.md`): apply
`ruling21-instructions.csv` — derived from the point-marking campaign
and PI-ratified on 2026-08-10/14 — to emit the standardised reference
as NEW artefacts. No source layer is mutated; the campaign layers stay
exactly as the closing gates pinned them.

Outputs, written to ``<canonical-gt>/standardised/``:

- ``student-mounds-55maps-standardised.geojson`` — 4,731 features:
  4,746 original student records minus 4 false positives, minus 1
  contradicted-merge centroid, minus 12 duplicate records, plus the 2
  restored pre-merge originals. Survivors of marked clusters sit at
  their marked centres; claimed out-of-queue records inherit the
  claimant's mark (proxy confirmation); everything else keeps its
  as-digitised position. Original properties are preserved; the
  standardisation adds ``std_*`` provenance fields.
- ``extension-mounds-standardised.csv`` — 279 records: the 278
  surviving model-detected mounds (of 773 reviewed) at their marked
  centres, plus the one marking-pass extra. The legacy ring-gating
  column (``buffer_metres``, the Obs 371 defect) is replaced by
  ``nearest_student_m`` computed against the standardised student
  layer — the exact-position result ruling 20(d) step 3 asked for.
- ``README.md`` — the artefact header ruling 21(b) requires: scope,
  confidence grades, the two opposing reference biases, and the
  mixed-provenance statement with measured jitter figures.

The script cross-checks every census figure against
``ruling21-summary.json`` and fails loudly on any mismatch, so a stale
instruction set cannot silently materialise.

Usage (from the repository root)::

    .venv/bin/python scripts/materialise_standardised_reference.py
    # paths overridable; see --help

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
from pyproj import Transformer

_DEFAULT_GT_DIR = Path("results/deployment-oracle-2026-06-06/canonical-gt")
_DEFAULT_STUDENT_GT = Path(
    "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
)

_TO_WGS84 = Transformer.from_crs("EPSG:32635", "EPSG:4326", always_xy=True)


def load_instructions(gt_dir: Path) -> tuple[list[dict], dict]:
    """Load the instruction set and its census summary."""
    with open(gt_dir / "ruling21-instructions.csv", encoding="utf-8") as fh:
        instructions = list(csv.DictReader(fh))
    with open(gt_dir / "ruling21-summary.json", encoding="utf-8") as fh:
        summary = json.load(fh)
    return instructions, summary


def build_student_layer(
    instructions: list[dict], summary: dict, student_gt: Path, gt_dir: Path,
) -> dict:
    """Apply the instruction set to the student GeoJSON.

    Records named in the instructions follow their action; every other
    feature is the implicit default — kept as digitised, grade
    ``out_of_scope`` (the contract stated in the instruction file's
    spec and summary JSON).
    """
    with open(student_gt, encoding="utf-8") as fh:
        collection = json.load(fh)
    with open(gt_dir / "superseded-marking-queue.csv", encoding="utf-8") as fh:
        superseded = list(csv.DictReader(fh))

    by_record = {i["record"]: i for i in instructions}
    removed = {
        int(i["record"].split(":")[1])
        for i in instructions
        if i["record"].startswith("student:")
        and i["action"] in ("remove_fp", "remove_duplicate",
                            "remove_contradicted_merge")
    }

    features = []
    for index, feature in enumerate(collection["features"]):
        if index in removed:
            continue
        instruction = by_record.get(f"student:{index}")
        properties = dict(feature["properties"])
        geometry = feature["geometry"]
        if instruction:
            x, y = float(instruction["final_x"]), float(instruction["final_y"])
            geometry = {"type": "Point", "coordinates": [x, y]}
            lon, lat = _TO_WGS84.transform(x, y)
            properties["Longitude"], properties["Latitude"] = lon, lat
            properties["std_confidence_grade"] = instruction["confidence_grade"]
            properties["std_position_source"] = instruction["position_source"]
            properties["std_symbol_type"] = (
                instruction["symbol_type"] or "burial_mound"
            )
        else:
            properties["std_confidence_grade"] = "out_of_scope"
            properties["std_position_source"] = "as_digitised"
            properties["std_symbol_type"] = (
                properties.get("_reviewed_subtype") or "burial_mound"
            )
        properties["std_provenance"] = "student_digitised"
        properties["std_source_index"] = index
        features.append({
            "type": "Feature", "properties": properties, "geometry": geometry,
        })

    # Restored pre-merge originals: student digitisation that the
    # contradicted merge (corrected_student:4172) had replaced. They
    # inherit the centroid's descriptive properties with a derived,
    # clearly-suffixed uuid — traceable, not fabricated.
    centroid_properties = collection["features"][4172]["properties"]
    for instruction in instructions:
        if instruction["action"] != "restore_premerge":
            continue
        superseded_index = int(instruction["record"].split(":")[1])
        x, y = float(instruction["final_x"]), float(instruction["final_y"])
        lon, lat = _TO_WGS84.transform(x, y)
        properties = dict(centroid_properties)
        properties["uuid"] = (
            f"{centroid_properties.get('uuid')}-restored-{superseded_index}"
        )
        properties["Longitude"], properties["Latitude"] = lon, lat
        properties["_merged"] = False
        properties["std_confidence_grade"] = instruction["confidence_grade"]
        properties["std_position_source"] = instruction["position_source"]
        properties["std_symbol_type"] = (
            instruction["symbol_type"] or "burial_mound"
        )
        properties["std_provenance"] = "restored_premerge"
        properties["std_source_index"] = None
        features.append({
            "type": "Feature", "properties": properties,
            "geometry": {"type": "Point", "coordinates": [x, y]},
        })
        # Confirm the restored position is anchored to a genuine
        # pre-merge point: exactly at it when restored as recorded, or
        # within the 15 m distinct-mound floor when it inherits a
        # claimant's mark (superseded #46 takes promoted_phantom:389's
        # mark, 7.9 m from the pre-merge original).
        source = superseded[superseded_index]
        offset = float(np.hypot(float(source["x"]) - x, float(source["y"]) - y))
        tolerance = 0.01 if instruction["position_source"] == "as_recorded" else 15.0
        if offset > tolerance:
            raise SystemExit(
                f"restored point {superseded_index} sits {offset:.1f} m from "
                "the superseded layer — instruction set is stale"
            )

    expected = summary["final_student_layer"]["after"]
    if len(features) != expected:
        raise SystemExit(
            f"student layer has {len(features)} features, census says {expected}"
        )
    return {
        "type": "FeatureCollection",
        "name": "student-mounds-55maps-standardised",
        "crs": collection["crs"],
        "features": features,
    }


def build_extension_layer(
    instructions: list[dict], summary: dict, gt_dir: Path,
    student_layer: dict, extras_csv: Path,
) -> list[dict]:
    """Emit the surviving model-detected mounds plus the marking-pass extra.

    ``nearest_student_m`` is computed against the standardised student
    layer — the exact-position replacement for the legacy ring-gated
    ``buffer_metres`` column (Obs 371).
    """
    with open(gt_dir / "canonical-review.csv", encoding="utf-8") as fh:
        phantoms = list(csv.DictReader(fh))
    with open(extras_csv, encoding="utf-8") as fh:
        extras = {r["extra_id"]: r for r in list(csv.DictReader(fh))}
    student_points = np.array([
        f["geometry"]["coordinates"][:2] for f in student_layer["features"]
    ])

    rows = []
    for instruction in instructions:
        if instruction["action"] == "keep_phantom_extension":
            phantom = phantoms[int(instruction["record"].split(":")[1])]
            identifier = phantom["candidate_id"]
            map_name = phantom["map_name"]
            provenance = "model_detection"
        elif instruction["action"] == "add_marking_pass_extra":
            extra_id = instruction["record"].split(":", 1)[1]
            identifier = f"extra:{extra_id}"
            # The nested pair shares student #3207's sheet.
            map_name = extras[extra_id].get("map_name") or "K-35-066-1"
            provenance = "marking_pass_extra"
        else:
            continue
        x, y = float(instruction["final_x"]), float(instruction["final_y"])
        nearest = float(np.min(np.hypot(
            student_points[:, 0] - x, student_points[:, 1] - y,
        )))
        rows.append({
            "candidate_id": identifier,
            "x": x,
            "y": y,
            "map_name": map_name,
            "symbol_type": instruction["symbol_type"] or "burial_mound",
            "confidence_grade": instruction["confidence_grade"],
            "position_source": instruction["position_source"],
            "provenance": provenance,
            "nearest_student_m": round(nearest, 2),
        })

    expected = (
        summary["final_extension_layer"]["phantom_survivors"]
        + summary["final_extension_layer"]["marking_pass_extras"]
    )
    if len(rows) != expected:
        raise SystemExit(
            f"extension layer has {len(rows)} rows, census says {expected}"
        )
    return rows


def grade_tallies(student_layer: dict, extension: list[dict]) -> dict:
    """Count confidence grades for the README and the consistency check."""
    student = {}
    for feature in student_layer["features"]:
        grade = feature["properties"]["std_confidence_grade"]
        student[grade] = student.get(grade, 0) + 1
    ext = {}
    for row in extension:
        ext[row["confidence_grade"]] = ext.get(row["confidence_grade"], 0) + 1
    return {"student": student, "extension": ext}


def write_readme(
    out_dir: Path, summary: dict, tallies: dict, n_extension: int,
) -> None:
    """Write the ruling-21(b) artefact header."""
    student = tallies["student"]
    n_student = summary["final_student_layer"]["after"]
    text = f"""# Standardised 55-map reference — ruling-21 application

> **Last revised**: 2026-08-14 (initial materialisation). See
> [§ Changelog](#changelog) for revision history.

**This is a best-possible reference, NOT a gold standard** (ruling
21b). Mounds that both the students and every model missed are not
economically recoverable without a fresh survey of the map sheets, so
they are absent from this reference entirely. Treat every recall and
F1 computed against it accordingly (see § Known biases).

Produced by `scripts/materialise_standardised_reference.py` from the
PI-ratified instruction set
(`../ruling21-instructions.csv`, spec
`planning/ruling21-application-spec.md`). The source campaign layers
are unchanged; regenerate by re-running the script.

## Layers

| File | Records | What it is |
|------|---------|------------|
| `student-mounds-55maps-standardised.geojson` | {n_student} | Student digitisation, standardised: 4,746 − 4 FP − 1 contradicted merge − 12 duplicates + 2 restored pre-merge originals |
| `extension-mounds-standardised.csv` | {n_extension} | Confirmed mounds the students missed: 278 model-detected survivors (of 773 reviewed) + 1 marking-pass extra, all at marked centres |

## Confidence grades (student layer)

| Grade | Records | Meaning | Positional quality |
|-------|---------|---------|--------------------|
| `directly_reviewed` | {student.get("directly_reviewed", 0)} | Opened as a queue item and adjudicated | marked centre, ±2.5 m |
| `proxy_confirmed` | {student.get("proxy_confirmed", 0)} | Confirmed as a claimed partner from a reviewed mark; position inherited from the claimant's mark | marked centre, ±2.5 m |
| `out_of_scope` | {student.get("out_of_scope", 0)} | Never examined (ruling 21c boundary) | as digitised: median 8.6 m, p90 18.3 m, max 30.0 m from the true centre (measured on the 89-item jitter sample) |

Every extension record is `directly_reviewed`.

## Known biases (Obs 396; both directions must travel together)

- **Deflation**: an estimated ~370 residual long-range duplicates
  (95% CI ≈ 200–660, hard ceiling 549) remain among the out-of-scope
  records — attractor-displaced second records of mounds 72–100 m
  away. They deflate measured recall ~7% and measured F1 by ≈ 0.03
  at a balanced ~0.85 operating point, rank-preserving to first
  order. A displaced detection can match a displaced ghost record,
  which differentially favours attractor-susceptible configurations.
- **Inflation**: joint student+model false negatives are absent from
  the reference (Obs 361): measured recall is inflated ≈ +2.4–2.7%,
  F1 ≈ +0.011–0.012 absolute.
- **Net at point estimates ≈ −0.017**: measured F1 modestly
  understates true performance; the intervals span near-zero.

## Mixed provenance (a documented property, not an oversight)

Ruling 21(c) scoped marking to the reviewed subset. Positions are
therefore mixed: {student.get("directly_reviewed", 0) + student.get("proxy_confirmed", 0)}
student records and all {n_extension} extension records carry marked
centres (±2.5 m); the {student.get("out_of_scope", 0)} out-of-scope
student records keep their as-digitised positions (jitter figures
above). The `std_position_source` field states each record's source.

## Replaces

The pre-standardisation pairing of
`inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
(4,746) with `../canonical-review.csv` (773, ring-gated
`buffer_metres` — the Obs 371 defect). The extension layer's
`nearest_student_m` is computed against the standardised student
layer, so per-buffer gating can be done exactly (ruling 20d step 3).

## Changelog

### 2026-08-14 — Initial materialisation

All seven spec decisions resolved (2026-08-10 and 2026-08-14); the
six-claim walk landed at `b2692f188`. Census cross-checked against
`../ruling21-summary.json` at build time.
"""
    with open(out_dir / "README.md", "w", encoding="utf-8") as fh:
        fh.write(text)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Materialise the standardised reference (new files only).",
    )
    parser.add_argument(
        "--canonical-gt-dir", type=Path, default=_DEFAULT_GT_DIR,
        help="Directory holding the campaign layers and instruction set.",
    )
    parser.add_argument(
        "--student-gt", type=Path, default=_DEFAULT_STUDENT_GT,
        help="Reviewed student-mound GeoJSON (the layer being standardised).",
    )
    parser.add_argument(
        "--out-dir", type=Path, default=None,
        help="Output directory (default: <canonical-gt-dir>/standardised).",
    )
    return parser.parse_args(argv)


def main() -> int:
    """Build the standardised reference artefacts."""
    args = parse_args()
    gt_dir = args.canonical_gt_dir
    out_dir = args.out_dir or gt_dir / "standardised"
    out_dir.mkdir(parents=True, exist_ok=True)

    instructions, summary = load_instructions(gt_dir)
    student_layer = build_student_layer(
        instructions, summary, args.student_gt, gt_dir,
    )
    extension = build_extension_layer(
        instructions, summary, gt_dir, student_layer,
        gt_dir / "extra-review-items.csv",
    )
    tallies = grade_tallies(student_layer, extension)

    student_path = out_dir / "student-mounds-55maps-standardised.geojson"
    with open(student_path, "w", encoding="utf-8") as fh:
        json.dump(student_layer, fh)
        fh.write("\n")
    extension_path = out_dir / "extension-mounds-standardised.csv"
    with open(extension_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(extension[0].keys()))
        writer.writeheader()
        writer.writerows(extension)
    write_readme(out_dir, summary, tallies, len(extension))

    print(f"wrote {student_path} ({len(student_layer['features'])} features)")
    print(f"wrote {extension_path} ({len(extension)} rows)")
    print(f"wrote {out_dir / 'README.md'}")
    print(f"grades: {tallies}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
