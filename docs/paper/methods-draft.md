# Methods — draft sections

> **Status**: ZERO-DRAFT (concept skeletons at target density, per the
> drafting contract — Shawn edits voice). First section drafted S134
> (2026-08-17): the D16 preregistration subsection. Remaining Methods
> sections follow `docs/methods-outline.md`; the cost-basis section
> (§ 5.4) already exists there. See [§ Changelog](#changelog).

## M.x Preregistration, amendments, and analysis status

The study was preregistered on the Open Science Framework
(preregistration v4.7, lodged 2026-01-31) with fifteen hypotheses:
eight confirmatory (H1–H8) and seven exploratory (H9–H15), the latter
registered as hypothesis-generating and excluded from
false-discovery-rate (FDR) correction. The registration committed to
a two-stage trial framework over a 361-tile corpus drawn from four
map sheets, per-hypothesis analysis plans, and Benjamini–Hochberg FDR
at q = 0.05 across the confirmatory family. We report execution
against that registration in three machine-checked layers: a
protocol-errata file, a classified analysis register, and a
hypothesis-outcome table generated from the register.

Deviations are recorded in a numbered errata file (E1–E78). Under the
file's declared three-way scheme, entries with bare labels tally 22
corrections (implementation brought back into line with the
registered protocol), 16 deviations (substantive departures, each
with stated justification), and 12 clarifications (interpretations of
ambiguous registered text). The remaining 28 entries carry composite
or qualified labels, including the entries that record omissions
rather than changes (E59, E74, E75, E78). Any headline count of "deviations" depends on the
counting rule adopted, so we cite entries individually rather than
aggregating them [unverified: final counting rule pending an errata
census update at E78 vintage. The E1–E57 census recommended stating
the rule explicitly].

Every analysis in the study carries one of five preregistration
statuses in a schema-validated register. An analysis is
*confirmatory* when it implements a registered confirmatory test as
registered, *confirmatory-with-deviation* when disclosed errata apply
to its execution, and *registered-exploratory* when it implements an
analysis the registration classed as exploratory. An analysis is
*post-hoc* when it was not in the registered plan, and the criterion
is discharge, not resemblance: a second application of a registered
method to an unregistered factor, corpus, or pass pool does not
inherit registered status, because the registered obligation is
discharged elsewhere. The verifier-parameter matrices, the
cost-frontier boards, and every cross-configuration leaderboard are
post-hoc under this rule, even where they reuse registered sweep
machinery. Registered obligations that were never executed carry a
fifth status (*not-executed*) as first-class register entries, so the
hypothesis-outcome table (Table [N], Results) derives every cell from
the register and none by hand. The register holds 32 entries: 3
confirmatory-with-deviation, 5 registered-exploratory, 18 post-hoc,
and 6 not-executed.

The registered inference method and the method used in practice
differ, and we disclose rather than conflate them (erratum E45). The
registration specifies bootstrap confidence intervals with BH-FDR
across confirmatory hypotheses. The leaderboards and tier structures
throughout Results instead use paired tile-swap micro-F1 permutation
tests (10,000 permutations, seed 42, two-sided) with BH-FDR within
each board, an inference method the registration nowhere names.
Permutation testing is arguably better suited to the paired
tile-level structure of the data, but it cannot be presented as
registered, so wherever a confirmatory claim rests on a permutation
result we report the registered bootstrap construction alongside it.
The registered family-level correction was executed on 2026-07-30 as
a single family: one primary p-value per confirmatory hypothesis,
m = 7 (H6 excluded as never run), with the one input that had never
been computed (H1's pooled modality contrast) reconstructed under a
rule fixed before computation. The family rejects {H2, H3, H7} at
q = 0.05 (adjusted p = 0.00035, 0.00035, and 0.00233 respectively)
and retains H4 (adjusted p = 0.217), H1 (0.248), H5 (0.834), and H8
(0.834). Two of the three rejections read against their registered
predictions: H2's registered prediction was that two-stage
architectures would not improve detection, so its rejection is a
falsification in the study's favour (Results § R4), and H7's
registered expectation of a vendor-default temperature optimum was
reversed in direction (Results § R2).

Five registered obligations were never executed, and we account for
each rather than leaving silence for a registry reader to find. H6
(the Flash-to-Pro transfer protocol) was deferred under a competing
deadline and the deferral never ratified. The Pro comparison we do
report is an exploratory extension at a different scope, not H6
(errata E41, E74). H13 (overlap/stride) was registered in scope and
silently dropped. Tile overlap was a fixed parameter throughout,
never a manipulated factor (E75). H14 and H15 (cross-model
consistency and cross-model voting) were registered as deferred at
lodgement, and the deferral was honoured: no non-Google model was
ever called, so every generalisation claim in this paper is scoped to
Gemini (E76, E77). H2's Condition C (fine-to-coarse context
expansion) was never built, so H2 conclusions are phrased over the
coarse-to-fine architecture only (E59). Finally, a registered
post-experiment verification of the minimal-thinking decision
(§ 8.9 of the registration) was not executed as registered. Its
latency component has no coverage anywhere, so the registration's
anticipated "equivalent at a third the latency" finding is not
claimed (E78).

Interpretation of what this preregistration record implies about
LLM-assisted registration practice is taken up in Discussion
[cross-ref: prereg retrospective, Seed 7].

## Changelog

### 2026-08-17 — Original publication

M.x drafted (S134, immediately after the D17 reconciliation block and
its PI walk closed) as the first Methods prose. Sources: the lodged
registration (osf/preregistration.md v4.7), protocol-errata.md
(E1–E78), the analyses register (results/run-analyses.json, 32 rows,
vocabulary v2), the family-FDR row and registration
(reports/verification/family-fdr-registration.md), and the S134 walk
rulings (reports/s134-relabel-walk-dossier.md § 8). One deliberate
[unverified] flag: the deviation counting rule awaits an errata
census refresh at E78 vintage.
