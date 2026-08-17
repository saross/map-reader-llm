#!/usr/bin/env python3
"""Add the five not-executed disposition rows (S134 D17 reconciliation, Item 4b).

The register's semantics widened to 'registered obligations and their
dispositions' (PI-approved 2026-08-17): every registered-but-unexecuted
hypothesis carries a disposition row so the hypothesis-outcome table
generates purely from the manifest. Each row cites its disclosure erratum.

Run from the repo root after E74-E77 and the vocabulary-v2 migration landed.
"""

import json
from pathlib import Path

SIDECAR = Path("results/run-analyses.json")
UNEXEC_REGISTER = "reports/d17-inventory/unexecuted-register.md"


def disposition(analysis_id: str, hyp: str, deviations: list[str],
                outcome: str, predicted: str | None, rationale: str) -> dict:
    """Build one not-executed disposition row in sidecar spec form."""
    return {
        "analysis_id": analysis_id,
        "type": "disposition",
        "_note": (
            "Disposition row (vocabulary v2, S134 D17 reconciliation "
            "2026-08-17): records the non-execution of a registered "
            "obligation; it is not a performed analysis. Disposition "
            "(run vs formally close) pends the S134 unexecuted-set "
            "adjudication gate "
            "(planning/s134-d17-reconciliation-block-2026-08-17.md, "
            "hardening 7)."
        ),
        "_prereg_rationale": rationale,
        "conditions_compared": [],
        "hypothesis_refs": [hyp],
        "preregistered": "not-executed",
        "deviations": deviations,
        "predicted_outcome": predicted,
        "predicted_outcome_amended": None,
        "tie_set": [],
        "outcome": outcome,
        "paper_section": "Methods",
        "output_path": UNEXEC_REGISTER,
        "working_notes_obs": [],
        "manually_verified_at": None,
    }


NEW_ROWS = [
    disposition(
        "h6-phase4-transfer", "H6", ["E40", "E41", "E74"],
        "NOT EXECUTED — the registered four-phase Flash→Pro transfer "
        "protocol (osf/preregistration.md:651-701) never ran: 13 "
        "PLACEHOLDER strings remain in studies/phase4-transfer.yaml, the "
        "20-tile holdout manifest was never created, and only one of four "
        "registered OFAT factors was ever varied on Pro. The substitute "
        "487-tile/384 px Pro comparison is an exploratory extension (E41), "
        "not H6. The only registered confirmatory hypothesis with no "
        "result; excluded and disclosed from the family BH-FDR (m=7). "
        "Full disclosure: E74.",
        "The Flash-optimal configuration will perform well on Pro, with "
        "at most minor factor adjustments needed "
        "(osf/preregistration.md:655) — never tested as registered.",
        "not-executed: registered confirmatory (osf:1157, 1994); the "
        "deferral (2026-03-11, competing deadline) was never ratified as "
        "an abandonment (E74). Re-execution remains available at ~US$48 "
        "subject to the E40 thinking-level confound."),
    disposition(
        "h13-overlap-stride", "H13", ["E64", "E75"],
        "NOT EXECUTED — the registered three-arm overlap/stride contrast "
        "(osf/preregistration.md:1024-1028) never ran: arms B (25%) and C "
        "(50%) were never built, and overlap was a fixed parameter (12.5% "
        "at every tile size), never a manipulated factor, so no registered "
        "H13 analysis (all comparative) is computable. Silently dropped "
        "with no dated decision; cannot shelter under the Tier C "
        "'registered as deferred' framing. Full disclosure: E75.",
        "The registration poses a question, not a directional prediction: "
        "does increasing tile overlap improve detection performance, and "
        "is the cost justified? (osf/preregistration.md:1020) — never "
        "tested.",
        "not-executed: registered exploratory Tier B, in scope at "
        "lodgement (osf:1016); trigger clause 2 arguably fired (baseline "
        "F1 0.660) and was answered by different mechanisms (E75)."),
    disposition(
        "h14-cross-model-consistency", "H14", ["E76"],
        "NOT EXECUTED — registered as deferred at lodgement "
        "(osf/preregistration.md:1052-1068), the honest case: the "
        "deferral and its reasons are in the registration itself. "
        "Positively verified: all 1,131 model-labelled passes are Gemini; "
        "no Anthropic or OpenAI client was ever a dependency. Every "
        "generalisation claim is scoped to Gemini; within-Google "
        "comparisons are never H14 evidence. Qualifications (deferral "
        "provenance, execution-plan contradiction, coverage-document "
        "overstatement): E76.",
        "The Flash-optimal configuration will perform similarly on Claude "
        "and GPT models, with at most minor factor adjustments needed "
        "(osf/preregistration.md:1062) — never tested.",
        "not-executed: registered exploratory Tier C, deferred at "
        "registration (osf:1058); deferral honoured, disclose-only "
        "disposition per the unexecuted register (Tier 3, item 21)."),
    disposition(
        "h15-cross-model-voting", "H15", ["E77"],
        "NOT EXECUTED — registered as deferred with a dependency on H14 "
        "as its first ground (osf/preregistration.md:1082-1086); H14 "
        "never ran, so H15 was gated, not skipped. Positively verified: "
        "no scored condition aggregates votes across models (123 distinct "
        "proposer pools, all single-model). The cross-model cascades that "
        "exist (Pro/Flash-3.5 verifiers over Flash pools) test "
        "verification, not voting, and must never be cited as H15. Full "
        "disclosure incl. the mixed-pool provenance hazard: E77.",
        "The registration poses a question, not a directional prediction: "
        "does cross-model voting outperform within-model voting at "
        "equivalent total passes? (osf/preregistration.md:1080) — never "
        "tested.",
        "not-executed: registered exploratory Tier C, deferred at "
        "registration (osf:1076), precondition (H14) never satisfied; "
        "disclose-only disposition per the unexecuted register."),
    disposition(
        "h2-condition-c-fine-to-coarse", "H2", ["E59"],
        "NOT EXECUTED — H2's registered Condition C (fine-to-coarse "
        "context expansion, osf/preregistration.md:478-482) never ran: no "
        "expand_* config or system instruction was ever created (the "
        "registered mapping at osf:2015 names them), and the registered "
        "one-tailed test, ≥0.05 stopping rule, and advance criterion are "
        "unevaluable for that architecture. H2's registered test is "
        "two-thirds executed; every H2 conclusion must be phrased over "
        "coarse-to-fine, never 'two-stage architectures' generally. The "
        "archived Strategy-10 approximation does not discharge it. Full "
        "disclosure: E59 (+ 2026-08-17 update).",
        "Neither two-stage architecture will improve F1 over single-stage "
        "detection with voting (osf/preregistration.md:461) — for "
        "Condition C, never tested (Condition B falsified the registered "
        "null; see family-bh-fdr-confirmatory).",
        "not-executed: one registered confirmatory condition of H2 "
        "(osf:453, 465-469); dropped at drafting time and never ratified "
        "(E59); disposition decision scheduled for the S134 adjudication "
        "gate, closing the open decision E59 records."),
]


def main() -> None:
    data = json.loads(SIDECAR.read_text())
    existing = {r["analysis_id"] for r in data["analyses"]}
    for row in NEW_ROWS:
        if row["analysis_id"] in existing:
            raise SystemExit(f"{row['analysis_id']} already present — refusing.")
    data["analyses"].extend(NEW_ROWS)
    SIDECAR.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    print(f"Added {len(NEW_ROWS)} disposition rows; sidecar now "
          f"{len(data['analyses'])} entries.")


if __name__ == "__main__":
    main()
