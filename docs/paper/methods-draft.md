# Methods — draft sections

> **Status**: ZERO-DRAFT (concept skeletons at target density, per the
> drafting contract — Shawn edits voice). First section drafted S134
> (2026-08-17): the D16 preregistration subsection. **The outline is now
> FULLY CONVERTED** (S140, 2026-08-23): §§ 1–4 and § 6 landed as
> M.8–M.12, joining M.x and M.2–M.7; the cost-basis section (§ 5.4)
> already exists in `docs/methods-outline.md`. The § 4.3 phase table
> was regenerated from the analyses register in S142 (2026-08-24; five
> register-vs-old-table disagreements flagged in place); one [DRAFT
> NOTE] item gates finalisation: the § 6.3 session-count refresh.
>
> **Last revised**: 2026-09-13 (corpus size corrected to 340/360 and the
> clean-holdout claim qualified, under errata E86 and E87).
> See [§ Changelog](#changelog).

## M.x Preregistration, amendments, and analysis status

The study was preregistered on the Open Science Framework
(preregistration v4.7, lodged 2026-01-31) with fifteen hypotheses:
eight confirmatory (H1–H8) and seven exploratory (H9–H15), the latter
registered as hypothesis-generating and excluded from
false-discovery-rate (FDR) correction. The registration committed to
a two-stage trial framework over a four-sheet corpus of 360 tiles
(the registration says 361; erratum E64 (ii) adjudicates the
discrepancy in favour of the 360 tiles that physically exist),
per-hypothesis analysis plans, and Benjamini–Hochberg FDR
at q = 0.05 across the confirmatory family. We report execution
against that registration in three machine-checked layers: a
protocol-errata file, a classified analysis register, and a
hypothesis-outcome table generated from the register.

Deviations are recorded in a numbered errata file (E1–E87). Under the
file's declared three-way scheme, entries with bare labels tally 22
corrections (implementation brought back into line with the
registered protocol), 18 deviations (substantive departures, each
with stated justification), and 12 clarifications (interpretations of
ambiguous registered text). The remaining 35 entries carry composite
or qualified labels, including the three entries explicitly labelled
as recording omissions rather than changes (E74, E75, E78); E59
likewise records an unexecuted registered condition, under a bare
deviation label. Any headline count of "deviations" depends on the
counting rule adopted (defensible tallies at this vintage run from 18
to 31), so we cite entries individually rather than aggregating them.

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
the register and none by hand. The register holds 67 entries: 47
post-hoc, 11 registered-exploratory, 4 confirmatory-with-deviation,
and 5 not-executed. No analysis carries the bare *confirmatory*
status: every registered confirmatory test that ran did so under at
least one disclosed erratum. Sixty-six of the 67 rows carry a human
signature attesting their outcome prose; the single unsigned row is
unsigned by design, holding the consensus-calibration curve retained
as calibration material rather than as a result
(`results/run-analyses.json`).

Three reporting conventions settled during analysis govern how the
artefacts this section points at may be read, and are stated here
rather than left implicit. First, **generated projections carry
provenance, not a hand revision trail**: a Markdown artefact emitted
by a generator from registered inputs — the hypothesis-outcome table
is the type case — is exempt from the project's hand
banner-and-changelog requirement and instead carries a
do-not-hand-edit banner naming its generator, the source commit of the
inputs it was projected from, and a `--check` drift guard run by an
automated test, so "is this current?" is answered by the drift test;
a hand-added changelog would break the guard, which is why the
exemption exists (`docs/methodology/output-directory-standard.md`
§ "Documents in Revision Policy Scope", ruling of 2026-09-11).
Second, **tile-level MCC uses the name-based tile join**: a detection
is assigned to the tile whose identifier it records, not to the tile
whose polygon contains it, because tile-level MCC scores the
pipeline's decision on the tile the model was shown and the
identifier records that exactly. The alternative is not available as
a single metric — the evaluation frames overlap (384 px tiles at a
336 px step, a 12.5 % overlap), so a median 30.6 % of a cell's
detections lie inside more than one frame tile, "the tile containing
this point" is not a function, and the two defensible geometric rules
differ from each other by up to 0.05 MCC. A scorer-level invariant
refuses to emit a tile-level confusion whose join the frame's
geometry contradicts; three cells of one condition family are refused
on that basis and are **disclosed rather than dropped** — their
whole-frame F1, which the tile join does not touch, is reported in
full, and their per-tile table and tile-level MCC are withheld with a
named reason (`reports/tile-mcc-geometric-join-2026-09-12.md`).
Third, **a carried operating point means the calibration ladder's own
vote shell**: where a condition's operating point is carried from the
calibration corpus rather than optimised in place, the carried point
is that ladder's vote shell (k = 1 / 3 / 4 / 8 at K = 1 / 3 / 5 / 10)
and the literal reading k = K is reported beside it as a disclosed
column. Both readings are computed and committed and they coincide at
K ≤ 3; above it the literal reading costs up to 0.2566 F1 where the
shell reading costs at most 0.0735, so any transfer cost quoted on
the literal reading is an upper bound
(`results/k-ladder-2026-09-12/findings.md` § 7.5).

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
Two further departures from the registered inferential specification
are disclosed on the same principle. The registered
confidence-interval procedure is a 1,000-iteration percentile
bootstrap (Decision 10); the corpus runs bias-corrected and
accelerated (BCa) bootstrap at 10,000 iterations — a substitution made
in April 2026 for a stated statistical reason, undisclosed until
erratum E82, and defective in its vectorised adapter for sixteen weeks
thereafter. No point estimate and no published significance verdict
changes, because the registered rule is defined on difference
intervals and no difference interval reaches the defective wrapper;
what moves is the width of single-condition intervals, in both
directions, across essentially the whole corpus. Separately, the rule
deciding which conditions are published as statistically
indistinguishable from the best was an order-dependent sequential rule
rather than the clique its own documentation promised. It is replaced
throughout by Hsu's multiple-comparisons-with-the-best procedure,
which revised published tie-set membership on eight boards in both
directions and cost one board a claim to a sole leader it does not
have (E83), again with no point estimate changed. Where both a
pairwise BH-corrected family and the simultaneous procedure are
available we report where they disagree, because a non-significant
pairwise family is not licence to claim that any of its members could
be the best one.
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
(errata E41, E74). H14 and H15 (cross-model
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

One registered obligation was disclosed as dropped and then
discharged, which the register records and this section states so the
two do not disagree. H13 (overlap/stride) was registered as a
three-arm overlap contrast and, for the first six months of execution,
only the study's fixed baseline tiling ever ran: arms B and C were
never executed, tile overlap was a fixed parameter at 12.5 % rather
than a manipulated factor, and no edge-effect assessment existed
anywhere. Erratum E75 records that omission, dated 2026-08-17. The
arms were then built and the three registered H13 analyses executed on
2026-08-17/18, so H13 is a *registered-exploratory* analysis with a
result rather than a not-executed obligation, and it carries the
omission's erratum alongside two others (E54, E66, E75). The
correction is a late execution, not a late claim: the result is
reported for the single carried configuration the registration frames
the contrast within, under the project's plateau rule.

Interpretation of what this preregistration record implies about
LLM-assisted registration practice is taken up in Discussion
[cross-ref: prereg retrospective, Seed 7].

## M.2 Evaluation corpora and scopes (outline target: new § 2.5; MD2)

The registration allocated the four-sheet corpus — 360 tiles, 90 per
sheet, which the registration states as 361 (E64 (ii)) — as 20
calibration tiles (contaminated by prompt development, excluded from
evaluation), a 60-tile stratified holdout (registered as 30 empty, 18
sparse and 12 dense, carrying 79 mound symbols; those strata and that
count come from a superseded approximation of each sheet's
georeferencing and are corrected by erratum E87, which puts 97
reference symbols in the 60 tiles and moves 27 of them between
strata — the sample itself is unchanged, because those are the strata
the registered seeds drew from), and the remaining 280 tiles as a
reserve (registered as 281, the same off-by-one). Execution
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
(ruling 21) that froze the reference before any dependent analysis
re-ran. Applying the ruling's single PI-ratified instruction set,
derived from the centre-marking campaign, removed four false
positives, twelve duplicates, and one contradicted merge and
restored two pre-merge originals, taking 4,746 records to 4,731
without mutating any source layer. Two human-review layers were
added. First, 641 student
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
residual student-layer incompleteness. The estimator extends the
reference with the adjudicated human-review mound calls at each
buffer radius and Hungarian-matches detections against that extended
reference, so a correct detection of a student-missed mound scores
as a true positive rather than a false positive. An independent
correction from a two-annotator Dawid–Skene latent-truth model (a
fixed-prior expectation-maximisation over candidate-grain votes)
converges with this estimator to within 0.004 F1 on every deployment
run once both are computed on the standardised reference, and to
within 0.001 on three of the four. The agreement holds at the
composite-metric level only, because the two methods reach it with
compensating precision and recall differences. What the reference can and cannot
support (its precision and recall epistemics) is characterised in
Results § R8 rather than assumed here.

Two targeted audits then examined the standardised reference directly.
A 500-tile empty-tile audit (tiles no channel had marked) found five
mounds missed by both students and every model — 1.06 % of the 470
empty tiles reviewed (95 % CI 0.35–2.47 %), extrapolating to ≈ 50
unseen mounds across the 4,676-tile empty frame — and a complete census
of the 719 mounds in clusters found six reference points that are not
mounds, six model-found mounds the reference lacked, one mound the
model had proposed but the vote gate removed, and two further
double-misses. Applied as a single deterministic instruction set, the
adjudications remove six records and add fourteen, giving revision r2
(5,018 records: 4,726 student, 278 extension, and 14 audit-reviewed,
the last two classes at marked centres). Every 55-map figure in this
paper is measured against r2; re-measurement moved no cell's F1 by
more than 0.0009 and changed no tier among the previously reported
cells. Because the audits sample the reference rather than exhaust it,
we also report an estimated correction for the error they did not see
(§ R7), propagated from the audit rates by Monte Carlo and shown
beside — never in place of — each point estimate.

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
input, the registered bootstrap construction is reported alongside
it. For the two contrasts that entered the family on permutation
floors, the registered instrument corroborates both rejections: the
H2 architecture contrast carries a bootstrap ΔF1 of +0.076 (95 % CI
+0.052 to +0.105) and the H3 consensus contrast +0.427 (95 % CI
+0.390 to +0.468), tile-level percentile intervals at the registered
1,000 iterations, with the 10,000-iteration sensitivity agreeing.
H8's null also rests on a permutation input (a Simes minimum over
seven contrasts, for which a paired bootstrap difference is not
defined) and is reported as permutation-based under the same
disclosure. The registered power statement (minimum detectable effect
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
audited cost basis and its billing-console corroboration). The whole
study's Gemini API spend, every campaign from December 2025 to
11 September 2026 including calibration, screens, and re-runs, was
A$6,740 before tax on the project's invoices, US$4,695 at the monthly
invoice exchange rates (`reports/billing/gemini-spend-by-sku.csv`);
the token-basis audits reproduce the invoiced SKU rates exactly and
reconcile to the invoices within 2 % where a campaign can be isolated
to its billing days (`reports/billing-reconciliation-2026-09-11.md`).
[DRAFT, S153 — inserted on the PI's instruction 2026-09-12 so the
figure is not lost; placement to be settled in the outline pass] Batch
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

## M.8 Study design overview (outline § 1)

The study is a preregistered, sequential one-factor-at-a-time (OFAT)
evaluation of Vision Language Model (VLM) detection of burial-mound
symbols on historical topographic maps, registered on the Open Science
Framework on 2026-01-31 with fifteen hypotheses — eight confirmatory
(H1–H8) and seven exploratory (H9–H15). An earlier stranded-factorial
design (protocol v3.5) was superseded before lodgement; the registered
design fixes one factor per phase and carries the winning level forward
to every subsequent phase. We chose OFAT over a full factorial on cost
grounds: at ten runs per cell over a 60-tile evaluation set, the
factorial crossing of the § M.10 factors would have required upwards of
54 cells against a budget ceiling of roughly US$250, whereas the
sequential design covers every factor's main effect within it. The
design's known cost — blindness to interactions — is mitigated where it
mattered by targeted exploratory tests (temperature-by-voting cells in
Phase 3a, and the two-stage pipeline sweeps), and its central execution
risk — a carry-forward decision that forecloses later phases —
materialised once and was handled by an additive protocol extension
rather than a substitution: the dual-track carry-forward described in
§ M.11, documented as erratum E27.

## M.9 Study area and materials (outline § 2)

**Cartographic sources.** Four Soviet General Staff 1:50,000
topographic map sheets covering part of the Thracian Plain in
south-eastern Bulgaria — K-35-052-4, K-35-053-3 (Elenovo), K-35-062-2
(Rakovski), and K-35-078-1 (Lesovo) — georeferenced in EPSG:32635 (UTM
zone 35N) at a native scan resolution of ~5.02 m per pixel. The target
feature is the standardised Soviet burial-mound symbol: a small
sunburst of radiating hachures around a central mark, printed at
~1.4 mm diameter (a measured median ground footprint of ~73 m across
38 sampled symbols; radius ~36 m —
`reports/symbol-footprint-measurement-2026-08-22.md`), so the 20–30 m
evaluation buffers of § 5 demand localisation within the printed
symbol's own face.

**Tile generation.** Sheets were cut into 512 × 512-pixel tiles with a
64-pixel overlap (stride 448 px), each covering roughly 2.57 × 2.57 km
of ground; tiles more than 75 % background were filtered out, leaving
**360 tiles** across the four sheets — 90 per sheet. Removing the 20
calibration tiles from these leaves the **340-tile Era-1 evaluation
frame** of § M.2, an exact set difference with no exceptions in either
direction. The registration states the corpus as 361; erratum E64 (ii)
adjudicates that against the registration's own "~360" and adopts the
360 tiles that exist.

**Ground truth.** 569 mound symbols were annotated across the corpus:
an initial student annotation campaign using the FAIMS v2.6 mobile
data-capture application, followed by comprehensive review and
verification by the primary researcher. Burial mounds, settlement
mounds, and mounds carrying benchmark or triangulation marks are all
treated as positive detections, since the printed symbol family is what
the detector sees. The reference is stored as GeoJSON in EPSG:32635.
The later evaluation corpora that extend beyond this design-time
reference — the Era-2/Era-3 gold-standard scopes and the 55-map
deployment references — are specified in § M.2 and § M.3.

**Data allocation.** Twenty tiles (five per sheet) formed the
calibration set used for prompt development and hard-example selection;
they are contaminated by construction and excluded from every
evaluation. The confirmatory instrument is a 60-tile holdout (fifteen
per sheet), stratified by mound density — registered as thirty empty,
eighteen sparse (one to two mounds), and twelve dense (three or more),
carrying 79 mound symbols. The remaining 280 tiles were held untouched
as a reserve pool for later validation. Tile selection used documented
random seeds within the density strata, applied to those strata as
registered; the strata and the 79 are corrected by erratum E87 (the
counts came from a bounding-box approximation of each sheet's
georeferencing that did not read the raster affine), so they describe
how the selection was made rather than the tiles' mound content.

**One qualification on the exclusion.** The calibration exclusion is
not quite a clean holdout, and the exception is documented as erratum
E86. Three of the seventeen few-shot examples are whole empty tiles —
the "null" exemplars, present to establish a no-mounds baseline — and
they were selected from a training set that was re-selected under a new
seed on 2026-01-04 without the null manifest being regenerated. They
are therefore not members of the committed calibration set, were never
entered into the exclusion geometry, and are themselves tiles of the
340-tile Era-1 frame. Counting each frame's tiles that share any pixel
with one of the three: 25 of 340 at Era 1 (including the three tiles
themselves), 3 of the registered 60-tile holdout, 20 of 487 at Era 2,
and 13 of 327 at Era 3. The leakage is bounded in three ways. It
carries **no reference information**: none of the 569 reference symbols
falls inside a null window, so no precision, recall, F1 or MCC value is
computed over leaked positives. It is confined to the **image
modality** — of the forty-one configurations that transmit example
images, thirty-seven include the nulls, while the twenty-two text-only
configurations carry them as labels alone and the verifier's
six-example library contains none — so text cells, every verifier stage
and all 55-map deployment cells are unaffected. And its direction is
conservative: what the model saw, labelled "no mounds here", is ground
it was later scored on, which can only suppress detections there. The
affected tile identifiers are published in
`inputs/examples/null-tiles/null_overlap_by_frame.json`, and the
sensitivity re-score with them excluded is reported in Results.

## M.10 VLM detection pipeline (outline § 3)

**Model.** All detection runs used Gemini 3 Flash (Google; model
identifier `gemini-3-flash-preview`), at `thinking_level: minimal`
except where thinking level was itself the manipulated factor. The
single-model focus was a deliberate scope decision: free-tier and
low-cost access made high-replication designs (up to thirty passes per
condition) affordable, and pilot work showed the model sufficiently
capable that detection quality would be limited by prompt and
aggregation design rather than raw model capacity. The registered
design is single-model throughout; later exploratory cross-model
comparisons (Gemini 3 Flash 3.5 role permutations and a Gemini Pro
2 × 2) are reported in Results and do not alter the pipeline
described here.

**Prompt architecture.** Each request assembles a system instruction
(task definition, target-symbol description, and output-format
specification), a configurable library of few-shot examples, and the
target tile as a 512 × 512 px PNG. Examples are drawn from labelled
calibration tiles in positive, negative, and null categories, and are
presented as images, text descriptions, or both, according to the
modality condition. (The three null exemplars are the exception to
"calibration tiles": see the qualification on the exclusion in § M.9
and erratum E86.) Content is assembled as sequential `types.Part`
objects via the google-genai SDK (v1alpha), with JSON output forced
through `response_mime_type="application/json"` and an 8,192-token
output ceiling that accommodates thinking tokens alongside the
detection payload. The model returns detections as normalised
bounding boxes on a 0–1000 coordinate scale.

**Experimental factors.** The manipulated factors, their levels, and
their phases: modality/elaboration (five levels from image-only to
verbose-text-plus-image; Phase 2a), temperature (0.0–1.3 in five
levels; Phase 2b), example-library composition (seven levels; Phase
2c), negative-text treatment (three levels; Phase 2d), example
ordering (four levels; Phase 2e), consensus pool size (5, 10, 30;
Phase 3a), and single-stage versus proposer–verifier architecture
(Phase 3d).

**Output processing.** Detections are converted from normalised to
pixel to UTM coordinates via each tile's georeferencing and saved
incrementally as per-tile GeoJSON features, so an interrupted run
resumes without re-querying completed tiles.

**Two-stage proposer–verifier pipeline (H2).** The two-stage
architecture couples a high-recall proposer pass with an independent
verification stage: each candidate is cropped from the original raster
at higher resolution and judged by the VLM under a diagnostic
checklist prompt, with multiple verification passes (typically five)
and a vote threshold. The registration treated this as an exploratory
hypothesis with an expected null (single-stage at least as good as
two-stage); the expectation did not survive contact with the data, as
Results reports.

**Consensus voting (H3).** Detection passes are aggregated in three
steps: greedy within-pass deduplication at 20 m (removing duplicates
from overlapping tiles), cross-pass clustering of the pooled
detections at 20 m Euclidean distance, and a vote threshold retaining
clusters supported by at least T distinct passes, swept over the full
T ∈ [1, K] range. Voting was tested at multiple temperatures (0.0,
0.3, 0.7) and pool sizes (5, 10, 30).

## M.11 Execution protocol (outline § 4)

**Sequential OFAT with a dual-track extension.** The registered design
prescribes a single carry-forward path. Phase 2a broke it in an
instructive way: the text-only condition (`brief-text`, F1 = 0.543)
outperformed the best image-using condition (`brief-text-image`,
F1 = 0.462), contradicting the foundational assumption that visual
few-shot examples help. Following the carry-forward rule literally
would have selected a winner for which Phases 2c (library composition)
and 2e (example ordering) are undefined, since both factors operate on
image examples. Rather than truncate the registered pipeline, we
carried both winners forward as independent tracks (erratum E27):
Track 1 (`brief-text-image`) ran the full registered sequence
2b → 2c → 2d → 2e, preserving the preregistered pipeline intact, and
Track 2 (`brief-text`) ran temperature testing and passed directly to
the Phase 3a voting study, the image-dependent phases being
inapplicable rather than skipped. The extension is additive — Track 1
is the registered design, executed with three documented scope
reductions (H5's 3 × 3 factorial collapsed to OFAT, E28; the H8
scale-16/32 cells deferred under E11 and later re-run under E51; H2's
condition C not executed, E59) — and its marginal cost (~US$55 of
additional temperature cells) bought the study its most consequential
finding: the text-only pathway.

**Runs per condition.** Ten independent single-pass runs per condition
per phase, as registered; thirty for the Phase 3a voting study. All
Phase 2–3 runs score against the same 60-tile holdout.

**Phase execution summary.** The table below is regenerated from the
analyses register (S142, per the outline's own S134 note), replacing
the outline's § 4.3 table, whose values predated the Era-1
re-scoring. Each factor was executed twice: the registered K = 10
single-pass runs per condition on the 60-tile holdout, then a
re-execution on the full 340-tile corpus (E36) with replication
scaled to the factor's observed variance — three runs where the
60-tile stage found a live effect, one where it found none
(sufficient for confirmation, and deterministic at the carried
T = 0.0), thirty for the consensus study (the rationale table is in
`reports/experimental-progression.md` § "What was re-run"). Register
outcomes are on the Era-1 340-tile, 14-buffer + MCC basis; the
identifiers in parentheses key into `results/analyses-manifest.json`.

| Phase | Hypothesis | Cells | Runs/cell (60 → 340 tiles) | Carried forward | Register outcome (Era-1 340-tile basis) |
|---|---|---|---|---|---|
| 2a | H1 modality/examples | 5 | 10 → 3 | Both track winners (E27): `brief-text-image` (Track 1), `brief-text` (Track 2) | Pooled modality effect NULL — text +0.024 F1, p = 0.177, not in the FDR rejection set; the extreme pairs are individually significant (brief-text > image-only, p = 0.004) (`h1-cmt0106-pooled-modality`) |
| 2b | H7 temperature | 5 × 2 tracks | 10 → 3 | T = 0.0, both tracks | H7 in the confirmatory rejection set (p ≤ 0.001, BH-adjusted 0.002) (`family-bh-fdr-confirmatory`) |
| 2c | H8 library composition | 5 × 2 tracks, + 3 exploratory image cells; scale-16/32 deferred (E11), executed as run `h8-v2` (E51) | 10 → 1 | plus-hp (13 examples; reused downstream, e.g. Phase 2e's baseline) | H8 not rejected (Simes p = 0.834) (`family-bh-fdr-confirmatory`; cells sit on `era1-single-pass-baseline-matrix`) |
| 2d | H5 negative-example text | 2 × 2 tracks (the registered 3 × 3 factorial collapsed to OFAT, E28) | 10 → 1 | Minimal treatment | H5 not rejected (p = 0.756) (`family-bh-fdr-confirmatory`) |
| 2e | H4 example ordering | 4 | 10 → 1 | No effect to carry | H4 not rejected (p = 0.124, adjusted 0.217); `canonical-last` is nonetheless the single-pass point-estimate leader (F1 0.631) (`era1-single-pass-baseline-matrix`) |
| 3a | H3 consensus voting | 2 tracks × 3 temperatures × N ∈ {5, 10, 30}, + 3 HIGH-thinking text cells and a HIGH-vs-MINIMAL replication pair | 30 | Consensus pooling into the two-stage pipeline | H3 rejected (p < 1e-4, `family-bh-fdr-confirmatory`). Best per track at the best-F1@20 m vote threshold: text T = 0.3, N = 30, 23-of-30, F1 0.692; image T = 0.7, N = 30, 18-of-30, F1 0.691; HIGH thinking beats MINIMAL under consensus (+0.067 F1) (`phase3a-consensus-calibration`, `phase3a-replication-thinking-calibration`) |
| 3d | H2 two-stage (proposer-verifier) | Verifier variants over consensus pools; the Era-1 board carries 4 verified-PV cells | Verifier n = 1 over pooled proposals | Adversarial text-only verifier, T = 0.0, MINIMAL | H2 rejected as a FALSIFIED directional prediction — two-stage improves F1 by +0.076 where the registration predicted against improvement at the ≥ 0.05 stopping threshold; the verified-PV cell is the Era-1 point-estimate leader (F1 0.792, MCC 0.676, within a 10-member MCB admissible set), and a MINIMAL single-pass + verifier reaches F1 0.770 at 2 calls/tile (`family-bh-fdr-confirmatory`, `era1-leaderboard`) |

[DRAFT NOTE — register-vs-old-table disagreements, flagged per the
S142 commission. (i) Replication: the outline's table implied 10
runs/cell throughout; that was the 60-tile stage only — the citable
340-tile re-execution used 3 (2a, 2b) and 1 (2c–2e), per the E36
rationale. (ii) 2c cells: the outline's "4 × 2 tracks" undercounts —
the register decomposes 5 registered library variants per track plus
3 exploratory image cells. (iii) 2d cells: "3 × 2 tracks" was never
executed — 2 × 2 after the E28 collapse. (iv) 3a optimum: the
outline's "N=30, T=0.7, F1=0.751" does not reproduce as any register
headline; on the current basis the text-track optimum is T = 0.3
(0.692) and the image-track T = 0.7 (0.691) — the 0.751 is a
pre-re-scoring value at a different scope, and it also survives at
`docs/methods-outline.md` line 462. (v) 3d: the outline's
"+0.09–0.14 F1" does not reproduce — the registered instrument gives
+0.076, and the progression report's Flash-range figure is +0.05 to
+0.09.]

**Errata affecting execution.** Two implementation errors affected
data collection and analysis method respectively, both detected and
corrected before results were interpreted. E25: the batch detection
script failed to skip example images for text-only conditions in
Phase 2a, sending identical images to all five modality conditions;
the anomalously clustered results this produced are what prompted the
investigation, and the phase was corrected and fully re-run. E26:
reference deduplication inside bootstrap resampling produced
confidence intervals that could exclude their own point estimates,
fixed by pre-computing per-tile TP/FP/FN counts before resampling. The
complete errata log — 85 entries at the time of drafting, E1–E85, with
the by-class accounting and its counting-rule caveat in § M.x — is
supplied in the supplementary materials alongside the registration.

## M.12 Reproducibility and transparency (outline § 6)

**Preregistration.** The protocol was registered at the Open Science
Framework on 2026-01-31 (12:54 UTC), before confirmatory data
collection. The registered content is protocol v4.7 with a versioned
changelog; the posted file's header retains a stale v4.6 label, itself
disclosed in the errata. Every deviation is documented in a living
errata log (85 entries at drafting) carrying a classification and an
impact assessment, and § M.x describes the three machine-checked
layers — errata file, classified analysis register, and generated
hypothesis-outcome table — through which execution is reported against
the registration.

**LLM assistance in the registration apparatus [PENDING — PI ruling
2026-09-03: stake this territory].** The registration, its errata log,
the classified analysis register, and the hypothesis-outcome table were
authored and checked with a large language model in the loop (Claude
Code sessions, archived per § M.12 below), with the human investigator
ruling on every registered commitment. The AB+ corpus (113 verified
sources; `reports/ab-plus-tail-report-2026-09-02.md`) finds no published
implementation or evaluation of LLM-assisted authoring or checking of a
preregistration — the nearest are proposals (Pu 2019; Thomas 2026 §6) —
so this paragraph describes the practice as unreported rather than
novel-by-assertion, names the two pitfalls the project met
(over-specification, and the self-flattering drift a model exhibits when
drafting toward a thesis it holds), and states the Thomas 2026 objection
(checklist-style assistance "relies solely on self-report") with the
machine-checked layers as the answer. Prose slot; sources attested in
the AB+ entries named in D.9.

**Software and data.** The detection pipeline is Python against the
google-genai SDK; evaluation uses a custom spatial-matching library
built on scipy (Hungarian assignment), geopandas, and shapely. Prompt
configurations, system instructions, and study YAML definitions are
version-controlled, as are the ground truth, tile manifests, and
prompt text. Every API request logs tokens, latency, cost, a
configuration snapshot, and retry counts, and committed evaluations
carry a self-describing `_metadata` block (schema, bootstrap
parameters, input files with their git states at scoring time, and
the spatial reference).

**Human–AI collaborative development.** The pipeline, evaluation
framework, and statistical analysis were developed collaboratively
between the primary researcher and an LLM-based coding assistant
(Claude Code, Anthropic). [DRAFT NOTE: the outline's "50+ documented
sessions over approximately six weeks" is the S134 figure; at drafting
the archive records 140 sessions over roughly eight months — regenerate
the final count from the session archive when this section is
finalised.] The division of responsibility is the load-bearing claim:
the human researcher held hypothesis formulation, experimental design,
protocol-deviation judgements, domain calibration (recognising when a
result contradicted archaeological or methodological priors), and
interpretation; the assistant held pipeline implementation, prompt and
configuration management, systematic error detection (the E25 modality
bug and E26 bootstrap bias among them), statistical analysis code, and
metadata logging. The collaboration enabled iteration and systematic
checking at a scale impractical for a solo researcher — tens of
configuration files, an errata log in the dozens, per-request metadata
on every call — and living documentation, with session transcripts and
structured reflections archived for transparency. What it could not
replace is equally part of the record: domain expertise for
calibrating expectations, scientific judgement on deviation decisions,
and design choices that require understanding the research question
rather than the implementation. Session transcripts are archived at
[Zenodo DOI TBD]; a fuller analysis of the collaboration process is
planned as a separate contribution.

## Changelog

### 2026-09-13 (later) — corpus size corrected to 340/360, and the clean-holdout claim qualified (E86, E87)

**Trigger**: errata **E86** and **E87**, filed the same day from the
`map-reader-bench` Stage 1 provenance audit. E86 found that the three
null few-shot exemplars were selected from a training set that was
re-selected under a new seed on 2026-01-04 without the null manifest
being regenerated, so they were never entered into the calibration
exclusion geometry and are themselves Era-1 evaluation tiles. E87
found that the registration's per-tile mound counts came from a
bounding-box approximation of each sheet's georeferencing that never
reads the raster affine. Both bear on Methods: the first on § M.9's
exclusion claim, the second on the corpus and holdout figures § M.x,
§ M.2 and § M.9 carry forward from the registration.

**Before → after table for numerical claims that moved**:

| Claim | Before | After | Source recounted |
|---|---|---|---|
| Corpus size (§§ M.x, M.2, M.9) | 361 tiles | **360 tiles** (90 per sheet), with the 361 named as the registration's figure and E64 (ii) as the adjudication | `ls inputs/tiles/*/*.png`; E64 (ii) |
| Era-1 evaluation frame in § M.9 | not stated | **340** = 360 − 20 calibration, verified as an exact set difference with 0 exceptions either way | `inputs/tiles/full_evaluation_manifest.json` against `calibration_manifest.json` |
| Reserve pool | 281 tiles | **280** tiles, with 281 named as the same off-by-one | arithmetic on the 360 |
| Holdout mound symbols | 79 (unqualified) | **79 as registered, corrected to 97 by E87**; 27 of the 60 tiles change density stratum | `docs/methodology/preregistration/osf/tile-mound-counts-recomputed-2026-09-13.json` |
| Errata range | E1–E85 | **E1–E87** | `protocol-errata.md`, 87 `### E<n>` entries |
| Composite or qualified labels | 33 | **35** | same; bare tallies 22 / 18 / 12 and the 18-to-31 deviations range are unchanged, both recounted |

**What was added, not corrected**: a new "One qualification on the
exclusion" paragraph in § M.9, because the draft's "they are
contaminated by construction and excluded from every evaluation"
implied a clean holdout that E86 shows is not quite clean. It states
the per-frame overlap (25 of 340 at Era 1, 3 of the registered
60-tile holdout, 20 of 487 at Era 2, 13 of 327 at Era 3) and the three
bounds on it: no reference symbol lies in a null window, the exposure
is the image modality only (37 of 41 image configurations carry the
nulls; the 22 text configurations carry labels alone and the verifier's
library carries none), and the direction is conservative. § M.10's
"Examples are drawn from labelled calibration tiles … null categories"
takes a cross-reference to it.

**What did NOT change**: no metric, no scope membership, no
hypothesis outcome, and no sentence about the executed evaluation
frames — the Era-1/2/3 tile counts (340 / 487 / 327) and their mound
counts (539 / 435 / 319) in § M.2 are measured against the reference
layer directly, never against the registered strata, so E87 does not
reach them. The "36 mounds" of the registration's § H8 availability
constraint appears **nowhere** in any paper draft (grep across
`docs/paper/` and `paper/`), so E87 had no other paper-facing count to
correct.

Landed in the commit that carries this entry.

### 2026-09-13 (S153) — § M.x brought current to E85 and to the S153 reporting rulings

Trigger: item 4 of `planning/documentation-foundation-checklist-2026-09-13.md`
— § M.x had been drafted at the E78 errata vintage and the 32-row
register vintage, and three reporting conventions settled in S153 bear
on Methods. Every count below was recounted from the artefact this
session rather than carried from the prior text.

**Before → after table for numerical claims that moved**:

| Claim | Before | After | Source recounted |
|---|---|---|---|
| Errata range | E1–E78 | **E1–E85** | `docs/methodology/preregistration/protocol-errata.md`, 85 `### E<n>` entries |
| Bare-label tallies | 22 / 18 / 12 | **22 / 18 / 12** (unchanged) | same; the two bullet-format entries E31 and E32 counted with the table-format ones |
| Composite or qualified labels | 26 | **33** | same |
| Defensible "deviations" range | 18 to 30 | **18 to 31** | same; upper bound is every Type mentioning "Deviation" |
| Analysis register rows | 32 | **67** | `results/run-analyses.json` |
| — post-hoc | 18 | **47** | same |
| — registered-exploratory | 5 | **11** | same |
| — confirmatory-with-deviation | 3 | **4** | same |
| — not-executed | 6 | **5** | same |
| Errata log count in § M.12 | 83 entries, E1–E83 | **85 entries, E1–E85** | same errata file (two places in § M.12, kept consistent with § M.x) |

**One stale claim corrected, and it was load-bearing.** The
not-executed paragraph asserted that "H13 (overlap/stride) was
registered in scope and silently dropped" and that tile overlap was
"never a manipulated factor (E75)". That was true when § M.x was
drafted on 2026-08-17 and false the next day: the three arms were built
and all three registered H13 analyses executed on 2026-08-17/18
(`results/h13-overlap-2026-08-18/findings.md`), so the register holds
H13 as **registered-exploratory with a result** (row
`h13-overlap-2026-08-18`, deviations E54, E66, E75) and the generated
hypothesis-outcome table prints H13 as **executed**. § M.x asserts
elsewhere that the table derives every cell from the register, so the
document was contradicting a projection it vouches for. The claim is
replaced by a paragraph that states the omission, its erratum, and its
discharge in order, and H13 is removed from the list of five
never-executed obligations — which now lists exactly five accounts
(H6, H14, H15, H2 Condition C, the § 8.9 verification), matching the
register's five `not-executed` rows one for one.

**Prose added.** (1) The signature layer: 66 of the 67 rows signed, the
one unsigned row unsigned by design, and the observation the counts
themselves support — that no row carries the bare *confirmatory*
status, so every registered confirmatory test that ran did so under at
least one disclosed erratum. (2) Two further departures from the
registered inferential specification, in the paragraph that already
discloses the permutation-for-bootstrap substitution: **E82** (BCa
replaced the registered 1,000-iteration percentile bootstrap
undisclosed, at 10,000 iterations, its vectorised adapter defective for
sixteen weeks; no point estimate or significance verdict moves, single-
condition interval widths move in both directions) and **E83** (the
tie-set rule replaced by Hsu multiple-comparisons-with-the-best; eight
boards' membership revised in both directions, one sole-leader claim
withdrawn), with the rule that a non-significant pairwise family is not
licence to claim any member could be best. (3) A new paragraph carrying
the three S153 reporting conventions, each with an inline anchor:
generated projections carry provenance not a hand revision trail
(`docs/methodology/output-directory-standard.md`
§ "Documents in Revision Policy Scope", 2026-09-11); the name-based
tile join as the published tile-MCC convention, with the frame-overlap
reason it is not merely a default (384 px tiles at a 336 px step,
median 30.6 % of detections in more than one tile, the two geometric
rules up to 0.05 MCC apart) and the refused-cell disclosure — whole-
frame F1 in full, per-tile table and tile-MCC withheld with a named
reason (ruling 6; `reports/tile-mcc-geometric-join-2026-09-12.md`);
and the carried-point convention — the stride ladder's own vote shell
is the carried point with `k = K` disclosed beside it, the two
coinciding at K ≤ 3 and diverging to −0.2566 against −0.0735 above it,
so literal-reading transfer costs are upper bounds
(`results/k-ladder-2026-09-12/findings.md` § 7.5).

**What did NOT change**: the preregistration facts (v4.7, lodged
2026-01-31, fifteen hypotheses, eight confirmatory and seven
exploratory); the cite-individually counting rule and its standing as
a queued PI call; the five-status definitions and the discharge
criterion for *post-hoc*; the family-level BH-FDR execution and all
eight adjusted p-values; the five not-executed accounts (H6, H13, H14
and H15, H2 Condition C, the § 8.9 minimal-thinking verification) and
their errata; the Discussion cross-reference; and every other section
of this document, § M.12's two errata counts excepted. The § 6.3
session-count [DRAFT NOTE] still gates finalisation.

### 2026-09-07 (S150) — M.3: the r2 audit paragraph (erratum E84)

Trigger: reference revision r2 (card
`planning/reference-revision-2026-09-06.md`; erratum E84). Added one
paragraph to § M.3 after the ruling-21 paragraph: the two PI audits,
the −6 / +14 instruction set, the r2 record counts, the re-measurement
bound (max |ΔF1@50| 0.0009, no tier moves among the r1 cells), and the
estimated-correction column's existence. Numbers read from
`results/reference-revision-r2/audit-revision-instructions.csv`,
`results/55map-final-board-r2-2026-09-06/`, and
`results/empty-tile-audit/adjudication.md`. No other section changed.

### 2026-09-03 (S147, later) — M.12 LLM-assistance slot opened (PI ruling)

Trigger: the AB+ tail report's automation-cell finding. Added a
[PENDING] paragraph to § M.12 describing LLM assistance in the
registration apparatus as unreported practice, with the two pitfalls
and the Thomas 2026 objection to answer. No numbers changed. Companion
planning stub for the follow-up methods paper:
`planning/llm-assisted-preregistration-methods-paper.md`.

### 2026-08-24 (S142) — § 4.3 phase table regenerated from the register

The M.11 [PENDING] block becomes the phase execution summary table,
regenerated from `results/analyses-manifest.json` (38 analyses) with
run decomposition from `results/run-conditions.json` and
`results/passes-manifest.json`, per the outline's own S134 note and
the PI's 2026-08-24 commission. The table reports the register's
citable values (Era-1 340-tile, 14-buffer + MCC basis) and makes the
two-stage execution explicit: registered K = 10 on the 60-tile
holdout, then the E36 340-tile re-execution at 3/3/1/1/1/30
replications. Five register-vs-old-table disagreements are flagged in
a [DRAFT NOTE] for the PI rather than silently corrected: uniform-10
replication, the 2c and 2d cell counts, the 3a "F1=0.751" optimum
(irreproducible from the register; the current per-track optima are
text T0.3 0.692 / image T0.7 0.691), and 3d's "+0.09–0.14" (the
registered instrument gives +0.076). What did NOT change: every other
M.11 claim, and the § 6.3 session-count [DRAFT NOTE], which still
gates finalisation.

### 2026-08-23 (S140) — Outline §§ 1–4 and § 6 converted: M.8–M.12

The four-session-queued scaffold conversions landed overnight on PI
direction ("proceed with as much of your unblocked work as you can"):
M.8 study design overview, M.9 study area and materials, M.10 VLM
detection pipeline, M.11 execution protocol, and M.12 reproducibility
and transparency — zero-draft prose at the established density, every
number carried from the S134-curated outline except where re-verified
this session (symbol footprint ~73 m from the 2026-08-22 measurement
report; errata count updated 78 → 83, E1–E83; the metadata description
extended to the D40 input-git-state stamp landed the same night).
Deliberately NOT resolved, marked in place: the § 4.3 phase-summary
table (the outline's own S134 note says regenerate from the analyses
register before prose), the § 6.3 session count (S134's "50+ sessions
/ six weeks" vs ~140 sessions / eight months at drafting), the
cross-model forward-reference question in M.10, and the Zenodo DOI.
With § 5's slots already drafted (M.4, M.7, and the outline's § 5.4),
every outline section now has draft prose.

### 2026-08-17 (S135, later) — M.4 pairings + M.x tally: all slots closed

The S135 analysis block's outputs land: the M.4 [PENDING × 2]
becomes the H2/H3 registered-instrument sentence (anchors:
`results/e45-bootstrap-pairings/e45_bootstrap_pairings.json`,
blind-verified bit-for-bit; scoping includes the H8
permutation-source disclosure per the verification round) and the
M.x [unverified] tally is corrected against the refreshed errata
census (bare deviations 16 → 18 at E78 scope, composites 28 → 26,
the omission-qualifier set narrowed to E74/E75/E78 with E59 named
separately under its bare label; census recount verified twice
independently plus a third derivation). The cite-individually
counting rule stands as drafted; adopting an aggregate rule instead
(census options 18/27/30) remains a queued PI call. No [PENDING] or
[unverified] markers remain in this document.

### 2026-08-17 (S135) — M.3 [PENDING] slots filled from the D-S report

The two M.3 slots drafted with the D-S report open, per the in-file
notes: the ruling-21 standardisation sentences (instruction-set
arithmetic 4,746 → 4,731, no source layer mutated; anchored to
`scripts/materialise_standardised_reference.py` and
`reports/verification/reference-standardisation-queue.md`) and the
corrected-F1 estimator + Dawid–Skene convergence passage (within
0.004 on every run, 0.001 on three of four; compensating
precision/recall boundary; anchored to
`results/55maps-ds-summary-v2/report.md` § 4.3). One wording note:
the slot's phrase "Dawid–Skene standardisation" was a misnomer — the
standardisation is the ruling-21 marking/adjudication campaign; the
D-S model is the independent latent-truth diagnostic, and the fill
reflects that division. The M.4 [PENDING × 2] and M.x [unverified]
slots remain, awaiting the S135 analysis block.

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
