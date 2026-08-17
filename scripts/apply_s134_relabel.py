#!/usr/bin/env python3
"""Apply the S134 D17 vocabulary-v2 relabelling to results/run-analyses.json.

One-shot migration: sets the new `preregistered` value on all 24 rows,
completes deviations arrays where an inventory or erratum attests the set,
adds H2 to era1-leaderboard's hypothesis_refs (attested manifest defect),
and records a per-row `_prereg_rationale` (generator-ignored sidecar field)
so every label carries its source anchors.

Run from the repo root. Idempotent; refuses to run twice.
"""

import json
from pathlib import Path

SIDECAR = Path("results/run-analyses.json")

# analysis_id -> (new label, deviations or None to keep, rationale)
EDITS: dict[str, tuple[str, list[str] | None, str]] = {
    "n1-baseline-matrix-384": (
        "post-hoc", None,
        "post-hoc: the 18-cell ranked board was not in the registered analysis "
        "plan (docs/methodology/n1-baseline-matrix.md:412-424 — the argued "
        "exception, preserved per the D17 ruling); H1/H6/H7 are recapitulated "
        "as convergent evidence only."),
    "pv-diag-384-consensus-calibration": (
        "post-hoc", None,
        "post-hoc: implements the registered H3 sweep method "
        "(osf/preregistration.md:519-521) but over unregistered production "
        "carry-forward pools (HIGH thinking is fixed at minimal by "
        "osf:1211-1212 and osf:2135); calibration material, no finding "
        "asserted. PI walk item S134."),
    "diversity-dividend-384": (
        "confirmatory-with-deviation", None,
        "confirmatory-with-deviation: executes the registered H3 comparison "
        "(osf:501, 519-521) and supplies the family BH-FDR H3 headline "
        "contrast (reports/verification/family-fdr-registration.md:698, "
        "SELECTED); the thinking-dividend claim in the same row is "
        "post-registration (D17 sweep U5) — outcome-prose fence pending the "
        "S134 PI walk."),
    "phase3a-consensus-calibration": (
        "registered-exploratory", ["E32", "E36", "E53"],
        "registered-exploratory: the registered H3 threshold-sweep "
        "characterisation (osf:519-521; pooling osf:325-327; N=30 osf:512) on "
        "the registered design modulo corpus (E36); carries no confirmatory "
        "contrast. First-N sub-pooling partially unlicensed (D17 sweep U2)."),
    "phase3a-high-consensus-calibration": (
        "post-hoc", ["E32", "E36", "E53"],
        "post-hoc: registered sweep machinery, but the HIGH-thinking arm it "
        "sweeps is unregistered (osf:1211-1212, osf:2135; D17 sweep U5/U6). "
        "PI walk item S134."),
    "phase3a-replication-thinking-calibration": (
        "post-hoc", ["E32", "E36", "E53"],
        "post-hoc: the HIGH-vs-MINIMAL thinking contrast is an unregistered "
        "factor (osf:1211-1212, osf:2135). PI walk item S134."),
    "phase3c-diversity-calibration": (
        "registered-exploratory", ["E12", "E32", "E63"],
        "registered-exploratory: implements the registered H9 five-condition "
        "design with the registered 5 replications and analyses "
        "(osf:855-896); H9 is registered exploratory Tier A (osf:843). "
        "Replication grouping rule unregistered (D17 sweep U8)."),
    "era1-single-pass-baseline-matrix": (
        "post-hoc", ["E25", "E27", "E28", "E29", "E30", "E31", "E36"],
        "post-hoc: constructed 36-cell board; the registered H1/H4/H5/H7/H8 "
        "tests are pairwise-bootstrap analyses (osf:434-443, 568-572, "
        "630-636, 725-729, 819-824) adjudicated at "
        "family-bh-fdr-confirmatory; this board is their characterisation "
        "home. Constituent-phase errata attached per D17 inventory "
        "(h1-h4:357-359; h5-h8:226-231)."),
    "era1-leaderboard": (
        "post-hoc", ["E25", "E27", "E28", "E29", "E30", "E31", "E36", "E37", "E58"],
        "post-hoc: constructed 82-cell board; carries the registered H2 "
        "contrast's characterisation (PV vs single-stage-with-voting — H2 "
        "added to hypothesis_refs per D17 inventory h1-h4:476-484, 617-619); "
        "the confirmatory H2 adjudication lives at "
        "family-bh-fdr-confirmatory. PV-cell errata E37/E58 attached. "
        "PI walk item S134."),
    "tile-size-sweep": (
        "registered-exploratory", ["E36", "E41", "E43", "E44", "E57"],
        "registered-exploratory: H11 is registered exploratory Tier B "
        "(osf:946); trigger met (osf:948 — every 512 px cell < 0.85); the "
        "registered 512-vs-384 core executed (osf:954-976); the 256 px arm "
        "and the architecture-interaction framing are post-hoc extensions "
        "(D17 inventory h9-h12:749-784); deviations per inventory "
        "recommendation (h9-h12:781) plus E36."),
    "verifier-robustness-matrix": (
        "post-hoc", ["E56", "E62"],
        "post-hoc: E62 names verifier-robustness among the unregistered PV "
        "extension studies; no registered verifier-parameter sweep exists; "
        "E56 governs its in-sample operating points."),
    "pass-budget-pareto": (
        "post-hoc", ["E56"],
        "post-hoc: PV-ladder cost board; the nearest registered text is the "
        "H3 cost-efficiency bullet (osf:524-528) but the priced object is "
        "the unregistered PV ladder; tiering apparatus unregistered (D17 "
        "sweep FALSE-9)."),
    "min-vs-high-thinking-pv": (
        "post-hoc", ["E56"],
        "post-hoc: MINIMAL-vs-HIGH thinking is an unregistered factor "
        "(osf:1211-1212, osf:2135); rejects an internal expectation "
        "(Obs 141), not a registered hypothesis."),
    "pass-budget-pareto-v2": (
        "post-hoc", ["E56"],
        "post-hoc: as pass-budget-pareto; the measured-token costing axis "
        "additionally has no registered basis."),
    "flash35-model-roles": (
        "post-hoc", ["E56", "E62"],
        "post-hoc: E62 names flash35-pv-2x2 among the unregistered PV "
        "extension studies; Gemini 3.5 Flash is outside the registered model "
        "roster (osf:1199-1201); not H14 evidence (D17 inventory "
        "h13-h15:305)."),
    "unswept-pools-completeness": (
        "post-hoc", ["E56"],
        "post-hoc: completeness sweep over in-sample PV operating points "
        "(E56); the Pro-verifier +0.015 is post-hoc cross-model "
        "verification, never to be cited as H15 (D17 inventory "
        "h13-h15:463-467)."),
    "55map-canonical-leaderboard-50m": (
        "post-hoc", None,
        "post-hoc: the 55-map corpus appears nowhere in the registration "
        "(grep-verified, D17 evidence pass 2026-08-17); 50 m is a registered "
        "supplementary tolerance only (osf:294); deployment board."),
    "55map-canonical-leaderboard-mcc-50m": (
        "post-hoc", None,
        "post-hoc: tile-MCC is a registered secondary outcome metric "
        "(osf:379-394), but the board, corpus, headline buffer, and tiering "
        "method are all outside the registration."),
    "h1-cmt0106-pooled-modality": (
        "confirmatory-with-deviation", None,
        "confirmatory-with-deviation: the registered H1 pooled-modality "
        "planned contrast (osf:441) by the registered two-tailed bootstrap "
        "method (osf:434-443); E36 is a material design deviation "
        "(corpus/K), E45/E54/E64 contextual; strictness rule applied "
        "(non-empty deviations -> -with-deviation)."),
    "family-bh-fdr-confirmatory": (
        "confirmatory-with-deviation", None,
        "confirmatory-with-deviation: the registered family inference itself "
        "(BH-FDR q=0.05 across confirmatory hypotheses, osf:270), "
        "registration-before-compute; the twelve attached E-numbers include "
        "six-plus material design deviations."),
    "e43-matched-temperature": (
        "post-hoc", None,
        "post-hoc: E72 classifies the lineage as an unregistered exploratory "
        "analysis (no registered hypothesis affected); the row itself "
        "disclaims registered standing."),
    "obs280-shared-reference": (
        "post-hoc", None,
        "post-hoc: the 55-map corpus and the standardised reference are "
        "post-registration constructs; no registered F1-vs-MCC divergence "
        "analysis exists."),
    "55map-standardised-leaderboard-50m": (
        "post-hoc", None,
        "post-hoc: unregistered corpus, reference, and tiering; robustness "
        "replication of the canonical board."),
    "55map-standardised-leaderboard-mcc-50m": (
        "post-hoc", None,
        "post-hoc: unregistered corpus, reference, and tiering; robustness "
        "replication of the canonical MCC board."),
}

RETIRED = {"preregistered", "exploratory", "preregistered-with-deviation"}


def main() -> None:
    data = json.loads(SIDECAR.read_text())
    rows = data["analyses"]
    ids = {r["analysis_id"] for r in rows}
    missing = set(EDITS) - ids
    if missing:
        raise SystemExit(f"EDITS references unknown analysis_ids: {missing}")
    already = [r["analysis_id"] for r in rows
               if r.get("preregistered") not in RETIRED]
    if len(already) == len(rows):
        raise SystemExit("Nothing to do — all rows already migrated.")

    for row in rows:
        aid = row["analysis_id"]
        if aid not in EDITS:
            raise SystemExit(f"No adjudication recorded for {aid}")
        label, deviations, rationale = EDITS[aid]
        row["preregistered"] = label
        if deviations is not None:
            row["deviations"] = deviations
        row["_prereg_rationale"] = rationale
        if aid == "era1-leaderboard" and "H2" not in row.get("hypothesis_refs", []):
            row["hypothesis_refs"] = ["H2"] + row["hypothesis_refs"]

    SIDECAR.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    labels = {}
    for r in rows:
        labels[r["preregistered"]] = labels.get(r["preregistered"], 0) + 1
    print("Migrated", len(rows), "rows:", labels)


if __name__ == "__main__":
    main()
