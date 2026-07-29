# C1 extraction instructions — commitment decomposition of the lodged text

**Version**: 1.1 (2026-07-29; v1.0 same day). **Controller**:
`planning/audit-charter.md` § 7 Phase 1. **Schema**:
`docs/manifest-schemas/commitments.schema.json`. **Consumers**: extraction
agents (one per chunk); the assembly step renumbers ids and validates with
`scripts/validate_commitments.py`.

**v1.1 convention** (adjudication ruling, see
`c1-adjudication-2026-07-29.md`): pure phase-carry-forward selection rules
("use the X-optimal from phase Y") are `condition` rows; carry-forward
rules with an outcome-conditional branch ("…or default if no significant
effect") are `trigger` rows with five-element blocks.

## Task

Read ONLY your assigned line range of your assigned lodged document and
enumerate EVERY commitment in it — full enumeration, no sampling
(charter § 5 rule 3). When in doubt whether something is a commitment,
include it and flag the doubt in `notes`. Missing a real obligation is
the failure mode this programme exists to catch; over-inclusion is
cheap to prune at adjudication.

A **commitment** is any statement that obliges the study to do, run,
measure, report, exclude, or decide something: registered hypotheses
and their tests, conditions that must be executed, factor/level
definitions constraining execution, decision rules (triggers),
statistical procedures and reporting promises, and explicit exclusions
or caveats (disclosures).

## Output

Write a JSON array to your assigned output file. Each entry uses the
schema's commitment shape EXCEPT `commitment_id` (omit it — assigned at
assembly). Set `status` to `"open"`, `discharged_by` and `waiver` to
`null` (discharge mapping is a separate step). Return a one-line count
summary as your final message, not the JSON.

## Hard rules

1. **`statement` is a VERBATIM contiguous span** copied
   character-for-character from the source — never paraphrase, never
   stitch non-contiguous text. Use the minimal span that carries the
   obligation; widen only when the obligation is inseparable from its
   context. `source.lines` (1-indexed, inclusive) must bound the span.
2. **Five-element trigger rule** (`kind: "trigger"`): fill `statistic`,
   `comparison_scope`, `uncertainty_criterion`, `evaluation_moment`,
   and `evaluation_corpus` from the lodged text. If the text does not
   state an element, write `"ABSENT — <what is missing>"` in that field
   and flag it in `notes`. **Do not invent or infer a value.** An
   absent element is itself a finding (the H7 lesson) and must surface,
   not be repaired silently.
3. `decision_statistic` / `uncertainty_treatment`: from the text; `null`
   where genuinely not applicable (e.g. most disclosures); `"ABSENT —
   <note>"` where applicable but unstated.
4. **§ 7 summary-table lines duplicate §§ 5–6 detail**: record the
   detailed-section commitment as the row; cite the summary line in
   `notes`. Do not double-count. (Applies to the agent holding § 7.)
5. **Appendix-prompts grain**: one commitment per prompt variant or
   configuration block — the obligation is "condition X uses exactly
   this text/configuration". `statement` = a short verbatim identifying
   span (heading or config line); record the full block's line range in
   `notes` as `full committed block: lines A–B`.
6. **Coverage-document grain**: each tested factorial cell or cell
   family is a `condition` commitment; each explicit exclusion is a
   `disclosure` (capture its rationale span); interaction-coverage
   promises are `analysis` or `condition` as worded.
7. Attribute nothing from outside your assigned range; if your range
   references another section, note the reference, do not chase it.
8. UK English in free-text fields you author (`normalised_obligation`,
   `notes`); verbatim fields follow the source exactly.
