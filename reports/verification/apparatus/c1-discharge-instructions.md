# C1/C2 discharge-mapping instructions

**Version**: 1.0 (2026-07-29). **Controller**: `planning/audit-charter.md`
§ 7 Phase 1. **Task**: propose a status for each assigned commitment in
`results/commitments.json` — the execution side of the commitment spine.

## Verdicts

- **discharged** — the obligation was executed/reported. Evidence
  REQUIRED: run/condition/analysis ids from the manifests
  (`results/runs-manifest.json`, `results/conditions-manifest.json`,
  `results/analyses-manifest.json`) and/or a results artefact path.
  Configuration commitments discharge against the prompt/config files
  actually used (`prompts/`, `studies/*.yaml`) — name the file.
- **waived** — an erratum formally licenses non-execution or amendment.
  Evidence REQUIRED: the E-number, checked against
  `reports/verification/c2-census/errata-licence-register.json`
  (its `waives_execution` and `licences` fields).
- **open** — neither: promised, not evidenced as done, not waived. This
  is the DEFAULT whenever evidence is not found; never guess a
  discharge. Items joined to the unexecuted register
  (scratchpad `register-commitment-join.json`) are presumptively open
  unless an erratum in the register row says waived.

## Rules

1. **Evidence or open.** A discharge without a resolvable manifest id or
   artefact path is invalid. Partial execution = open, with a note
   describing what ran and what did not (cite the register id where one
   exists).
2. **Disclosures**: a disclosure commitment (an exclusion/caveat the
   registration itself states) is `discharged` if the study respected
   it and it needs no further action; if later practice contradicts it,
   leave `open` with a note — contradiction hunting is Phase 4 work.
3. **Triggers**: assess the trigger's own obligation. Fired-and-honoured
   or legitimately-not-fired = discharged (evidence: the outcome data /
   analysis id showing the firing condition's state). Fired-but-not-run
   or indeterminate = open (cite the register where it lists the item).
4. Use the evidence pack: `hypothesis-execution-footprint.json`
   (scratchpad) maps hypotheses to runs/conditions/analyses counts;
   the errata licence register maps E-numbers to what they license.
5. Do not edit the ledger. Output proposals only.

## Output

JSON array to your assigned file:
`[{"commitment_id": "CMT-....", "status": "discharged|waived|open",
"discharged_by": {"runs": [...], "conditions": [...], "analyses": [...],
"evidence": "..."} or null, "waiver": "E.." or null,
"note": "<one sentence of reasoning; UK English>"}]`
One entry per assigned commitment — full enumeration. Final message: one
line: `discharge-N: n mapped (d discharged, w waived, o open)`.
