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

## M.2 Evaluation corpora and scopes (outline target: new § 2.5; MD2)

The registration allocated the 361-tile four-sheet corpus as 20
calibration tiles (contaminated by prompt development, excluded from
evaluation), a 60-tile stratified holdout (30 empty, 18 sparse, 12
dense, carrying 79 mound symbols), and a 281-tile reserve. Execution
departed from this allocation (erratum E36): confirmatory-phase
evaluation ran on the full non-calibration corpus at reduced
replication, and later phases re-tiled it, so results accrue on three
nested evaluation scopes rather than the registered holdout. Era 1
(the H1–H9 retest programme) evaluates 340 tiles at 512 px carrying
539 ground-truth mounds. Era 2 (the tile-size study, the
proposer–verifier diagnostic, and the consensus sweeps) evaluates 487
tiles at 384 px carrying 435 mounds. Era 3 (the library-design axis:
H8 v2, H10 v2, H12 v2) evaluates 327 tiles at 384 px carrying 319
mounds. Scope membership is manifest-defined and the nesting was
verified by zero-tolerance spatial intersection
(`results/evaluation-scopes.md`). Since the registered power analysis
assumed the 60-tile holdout, the executed scopes carry more tiles per
comparison. The cost is that per-condition replication fell from the
registered K = 10 to K = 1–3 in the retest programme (E36). Two
further tile sets are not eras and are never compared as if they
were: a 240-tile validation pool inside Era 2 (its hard scoring rule
is registered as erratum E72), and the 55-map deployment corpus of
8,541 tiles, which is spatially disjoint from the four-sheet corpus
entirely. Within-era comparisons carry the statistics, and cross-era
comparison is descriptive only (Results § R0).

## M.3 The 55-map deployment reference (outline target: new § 2.6; MD3)

The deployment instrument's reference was built from student
digitisations and hardened by targeted human review, and we report
its provenance structure because every deployment metric is bounded
by it. The base layer is 4,731 student mound records across the 55
sheets, positionally standardised under a fixed adjudication ruling
[PENDING: one-sentence description of the Dawid–Skene
standardisation step and ruling 21, drafted at S135 with the D-S
report open]. Two human-review layers were added. First, 641 student
records received individual review with hand-marked symbol centres
(±2.5 m marking precision). The remaining 4,090 out-of-scope records
keep their as-digitised positions, whose median offset from the true
centre is 8.6 m. Second, a 773-candidate "phantom" pool (model
detections absent from the student layer, pooled across
configurations) was adjudicated point by point, confirming 279
extension mounds the students had missed. These carry hand-marked
centres and enter the reference as first-class records. The resulting
standardised reference is therefore mixed-provenance by design, and
deployment scoring uses a corrected-F1 estimator that accounts for
residual student-layer incompleteness [PENDING: estimator sentence +
the two-corrections convergence result (within 0.004 on every run),
S135 with the D-S report § 4]. What the reference can and cannot
support (its precision and recall epistemics) is characterised in
Results § R8 rather than assumed here.

## M.4 Statistical analysis (outline target: § 5.3 rewrite; MD4)

The registered inference is bootstrap estimation with family-level
FDR control: 95 % confidence intervals from tile-level resampling
(1,000 iterations, percentile method, parameters fixed pre-lodgement
in Decision 10), with Benjamini–Hochberg FDR at q = 0.05 across the
confirmatory hypotheses. Narrow-effect analyses later raised the
iteration count to 10,000, a post-hoc parameter change disclosed as
erratum E54. The inference actually used for every leaderboard, tier
structure, and pairwise comparison in Results is different, and is
disclosed as unregistered (E45): paired tile-swap micro-F1
permutation tests (10,000 permutations, seed 42, two-sided), BH-FDR
at q = 0.05 within each comparison board, and greedy-clique tiering,
under which "Tier 1" means statistically inseparable from the board
leader. Permutation testing suits the paired tile-level structure of
the data, but the registration nowhere names it, so no permutation
result is presented as registered. The registered family-level
correction was executed once, as a single family, on 2026-07-30: one
primary p-value per confirmatory hypothesis, m = 7 with H6 excluded
as never run, under a construction registered before computation.
Wherever a confirmatory claim in Results rests on a permutation
input, the registered bootstrap construction is reported alongside it
[PENDING × 2: the H2 and H3 bootstrap pairings, queued as $0
analyses]. The registered power statement (minimum detectable effect
~0.07–0.09 F1 at 80 % power on the 60-tile holdout) predates the E36
scope change. Executed comparisons run on 340–487 tiles at lower
replication, so per-comparison power differs from the registered
figure in both directions and is not restated as registered.

## M.5 Deployment execution (outline target: new § 4.5; MD5)

Deployment ran the gold-standard pipeline unchanged on the 55-map
corpus: the same prompt configurations, consensus machinery, and
verifier, applied to 8,541 tiles per pass through the asynchronous
batch API with a token-per-minute governor managing concurrency.
Five campaigns were executed (four proposer configurations, carried
forward from the gold-standard programme at their calibrated
operating points, plus verification), with audited per-pass costs of
$4.66 (minimal text) to $50.82 (HIGH-thinking text at T = 0.3) and a
corrected total of ≈ $722 at flex-tier rates (§ 5.4 states the
audited cost basis and its billing-console corroboration). Batch
failures were recovered by targeted re-dispatch. One out-of-band
recovery campaign (127 passes, 350 tiles) is disclosed as erratum
E70, and clean token loads are lower bounds because retry spend is
not recorded on disk. The deployment cells reported in Results § R7
are the four carried configurations at two consensus thresholds
each, evaluated against the standardised reference (§ M.3) at the
50 m operational buffer (§ R1).

## M.6 Production verifier specification (outline target: § 3.5 expansion; MD6)

The registered two-stage design (H2 Condition B) specified a liberal
proposer followed by a strict verifier, with proposer and verifier
prompts lodged verbatim. The production implementation kept the
registered architecture and departed from its parts, and the lineage
is disclosed rather than smoothed over: the registered proposer
prompt was never used (the standard detection prompt was substituted
in all proposer–verifier experiments, erratum E58), the registered
verifier prompt was edited after lodgement (E65), and the production
verifier's adversarial framing (instructing the model to attempt to
reject each candidate) is a post-registration development (E37
records the production implementation). As deployed, the verifier is
gemini-3-flash with a text-only adversarial instruction at minimal
thinking, T = 0.0, and a single pass per candidate (n = 1), reading a
150 × 150 px crop centred on each candidate (75 px context padding)
and returning an acceptance probability that is thresholded at an
operating point selected on the test set (in-sample, disclosed as
E56). This configuration was carried forward unchanged from its
selection through every subsequent programme. The robustness
programme in Results § R5 then stress-tested each of its parameters
and found no cheaper-or-dearer variant that measurably improves on
it, including the single-pass choice (five-fold replication puts
single-run SD at 0.0025–0.0072 F1).

## M.7 Working-precision derivation (outline target: new § 5.x; D6 rider)

The spatial matching buffer is the evaluation's largest free
parameter, so both instruments derive it empirically rather than
asserting it (the derived values and their consequences are recapped
in Results § R1 per the settled D6 convention). On the gold-standard
instrument, plateau-onset analysis over all 259 conditions with full
buffer curves identifies the radius beyond which further widening
buys ≤ 0.005 F1 per step: text-pipeline localisation plateaus at
30 m (about 6 px at map scale, with proposer–verifier architectures
at 30 m, consensus at 35 m, and single-pass at 40 m), while
image-modality localisation plateaus at 75 m, roughly 2.5× looser,
making modality rather than architecture the dominant factor in
localisation precision
(`results/working-precision/gs-plateau-characterisation.{json,md}`).
On the 55-map instrument three independent derivations converge on a
50 m operational buffer: a complete-spatial-randomness null shows
chance matching is negligible at every canonical radius (null
F1 ≤ 0.015 even at 150 m), observed marginal gains die at 50 m while
chance creep continues, and the attribution-ambiguity bound bites
first, since the reference's 10th-percentile nearest-neighbour
spacing is 65 m and 21 % of mounds are already at cross-match risk
at 50 m (`results/working-precision/55maps-csr-noise-floor.{json,log}`).
Gold-standard results are therefore quoted at the registered 20 m or
the derived 30 m plateau, and all deployment results at 50 m. The
boundary is that a buffer is a property of the instrument and
reference, not of the detector: the derived radii do not transfer to
other map series or reference constructions without re-derivation.

## Changelog

### 2026-08-17 (later still) — M.7 working-precision derivation

Added per the settled D6 rider (Methods carries the derivation, R1
recaps values). Anchored to the two committed derivation artefacts
and R1's blind-verified passage; closes the D6 implementation note
from the MD mechanical-fix list.

### 2026-08-17 (later) — M.2–M.6 drafted under the MD rulings

Five subsections added after the PI settled MD1–MD6 (all = A,
in-session walk): evaluation corpora and scopes (M.2), the 55-map
reference (M.3, two [PENDING] slots for the D-S standardisation and
corrected-F1 estimator sentences), the statistics rewrite (M.4, two
[PENDING] slots for the queued H2/H3 bootstrap pairings), deployment
execution (M.5), and the production verifier specification (M.6).
Sources: results/evaluation-scopes.md, the results-draft R0/R8
verified passages, § 5.4's audited cost basis, errata E36/E37/E45/
E54/E56/E58/E65/E70/E72, scripts/extract_candidates.py (crop
padding), and the verifier-robustness findings.

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
