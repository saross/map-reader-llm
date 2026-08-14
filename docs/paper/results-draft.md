# Results — working draft

> **Last revised**: 2026-08-14 (Session 132, queue item 5: every 55-map
> figure moved to the ruling-21 standardised reference; both boards
> re-tiered with IDENTICAL tier structures, so no conclusion moved;
> blind-verifier corrections applied). Prior: 2026-06-13 (Session 114:
> draft notes resolved; § R9 added; § R7 lesson (iii) strengthened with
> the registered MCC tiering). See [§ Changelog](#changelog) for
> revision history.

**Status**: first full-prose draft for collaborative revision. Every number
is anchored to a registered manifest condition or analysis
(`results/conditions-manifest.md`, `results/analyses-manifest.md`), except
§ R9, which is anchored to its committed findings document and results
JSON (`results/gtfree-selection/`); section
order follows the study's evidential arc rather than run chronology.
`[DRAFT NOTE: …]` marks points needing Shawn's decision, a figure, or
numbers still to be pulled; `[Resolved …]` marks decisions taken in
Session 114 and recorded in the Changelog — Shawn retains the veto on
review. Companion outline: `docs/methods-outline.md` (cost-reporting
basis now specified there as § 5.4).

---

## R0. Reading guide: instruments, metrics, and statistical conventions

Two evaluation instruments run through everything that follows, and the
distinction governs how each result may be read. The **gold-standard (GS)
instrument** — four Soviet 1:50,000 sheets, curator-adjudicated ground
truth — is the *characterisation* instrument: it measures how well a
configuration can localise burial-mound symbols against known ground truth,
at each configuration's own best operating point, per the preregistered
H-series analysis plan. The **55-map instrument** — 8,541 tiles, the
ruling-21 standardised extended reference: 4,731 standardised student
digitisations plus 279 human-confirmed extension mounds, the
773-candidate phantom pool adjudicated down to distinct real mounds.
Positions are mixed-provenance by design: the 641 reviewed student
records and all 279 extension mounds carry hand-marked centres
(±2.5 m); the 4,090 out-of-scope student records keep as-digitised
positions (median 8.6 m from the true centre). It is the *deployment*
instrument: it measures what a configuration
calibrated on the GS sheets actually delivers on a large, diverse,
unseen corpus. Results on the first instrument are
reported as characterisations, not in-sample claims to hedge; results on
the second carry the calibrate-then-deploy interpretation, including its
failures (§ R6).

Headline metrics are buffered F1 at an empirically derived **working
precision** per instrument (§ R1), reported alongside tile-level Matthews
correlation coefficient (MCC) wherever the inputs support it. Statistical
comparison uses one machinery throughout: paired tile-swap micro-F1
permutation tests (10,000 permutations, seed 42, two-sided),
Benjamini–Hochberg false-discovery-rate (FDR) correction at q = 0.05, and
greedy-clique tiering, so that "Tier 1" always means "statistically
inseparable from the board leader". Tile sets differ by instrument and tile
size (GS 512 px: 340 tiles; GS 384 px: 487; GS 256 px: 1,032; 55-map:
8,541), so cross-era comparison is descriptive while within-era tiers carry
the statistics.

[DRAFT NOTE: cross-reference the Methods subsections for GT construction,
the matching algorithm (Hungarian, per map), and bootstrap CIs once Methods
prose lands.]

## R1. Working precisions are empirical properties of the system, not free parameters

Buffer radius is the analyst's largest free parameter, so we derived it
from the data rather than asserting it. On the GS instrument, plateau-onset
analysis of all 259 conditions with full buffer curves (every later step
≤ 0.005 F1) puts the **text pipeline's localisation plateau at 30 m**
(~6 px at map scale) — proposer–verifier (PV) architectures plateau at
30 m, consensus at 35 m, single-pass at 40 m — while **image-modality
localisation plateaus at 75 m**, roughly 2.5× looser; modality, not
architecture, is the dominant factor
(`results/working-precision/gs-plateau-characterisation.{json,md}`). For
the production text-PV family the buffer curve is flat between 30 m and
50 m, so GS headline values are insensitive to the choice within that
range.

On the 55-map instrument three independent lines converge on a **50 m
operational buffer**: (i) a complete-spatial-randomness null shows chance
matching is negligible at every canonical radius (null F1 ≤ 0.015 even at
150 m); (ii) observed marginal gains die at 50 m while chance creep
continues; and (iii) the attribution-ambiguity bound bites first — the
ground truth's 10th-percentile nearest-neighbour spacing is 65 m, so 21 %
of mounds are already at cross-match risk at 50 m and 42 % at 125 m
(`results/working-precision/55maps-csr-noise-floor.{json,log}`). The 50 m
buffer is also ~2× the measured student digitisation jitter. GS results
are therefore quoted at 20 m (the preregistered radius) or 30 m (the
plateau), and all 55-map results at 50 m.

## R2. Single-pass baselines: a broad statistical tie at modest performance

This subsection compresses the preregistered single-factor results
(H1, H4, H5, H7, H8) into one board-led narrative: each hypothesis was
tested as registered, the per-hypothesis detail tables go to
supplementary material, and the body reports the pattern they share —
because that shared pattern, not any single-factor effect, is the
finding. [Resolved 2026-06-13: board-led compression adopted; see
Changelog.]

No single-pass configuration separates from the pack. On the Era-1 board
(512 px, 340 tiles, curator GT, F1@20 m) the 36 single-pass cells resolve
into only four tiers, and Tier 1 is a 20-cell statistical tie spanning
F1 0.583–0.631, led numerically by a few-shot-ordering variant
(`canonical-last`, F1 0.631, MCC 0.213; analysis
`era1-single-pass-baseline-matrix`, 227/630 pairs significant). The
single-factor manipulations the study preregistered — modality and prompt
elaboration (H1), example ordering (H4), negative-text treatment (H5),
temperature (H7), example-library composition (H8) — all land inside or
near that tie: the GS instrument cannot separate the stronger single-pass
configs from one another. Two robust patterns do emerge: text-modality
prompts dominate image-only prompts at the bottom of the board, and a
metric trade-off recurs in which text cells reach F1 ≈ 0.60 at
near-zero MCC while image cells trade F1 for far better tile
discrimination. Single-pass performance, at best ~0.63 F1, is the floor
every architectural intervention below is measured against.

## R3. Consensus voting buys real performance; its mechanism is pass diversity

Consensus voting over repeated passes (H3) delivers the study's first
large, statistically clean gain. Pooling N independent passes and
thresholding on cross-pass vote count lifts the text pipeline from the
single-pass tie (~0.63) to 0.69–0.77 at each pool's best (N, threshold)
operating point — and the size of the lift depends on *pass diversity*,
not merely pass count. HIGH-thinking passes, which sample more diversely,
reach ~0.77 where minimal-thinking passes reach ~0.69 at matched N (the
"diversity dividend"; analysis `diversity-dividend-384` — consensus-beats-
single-pass is preregistered H3, confirmed; the thinking-level diversity
claim is a post-registration discovery, the registration having fixed
thinking at MINIMAL (§8.9) — D17 audit U5; replication +0.067 F1,
+0.234 MCC). Deliberately engineered diversity, however, adds nothing on
the one registered mechanism actually tested: H9's temperature-diversity
arm (H9-D, exercised incidentally via Phase 3c cross-variant pooling)
found no significant gain over a same-variant baseline pool (all p > 0.37
image, > 0.06 text; registered H9-B/C/E — text and image diversity — were
never run, D17 audit U12) — temperature sampling already supplies what engineering was
supposed to add. Strict unanimity hurts; permissive-to-mid thresholds win.
The consensus-era reading of these results — buy diversity with HIGH
thinking — is revised, but not contradicted, by the verifier results in
§ R5: the dividend is real for consensus-*only* architectures and obsolete
once a verifier stage exists.

## R4. The proposer–verifier architecture is the best architecture on every tile size

Adding an adversarial verification stage (H2) — an independent
text-prompted pass that re-examines a crop around each candidate and
assigns an acceptance probability — is the single best architectural move
in the study, on every tile size tested.

On the Era-1 definitive board (82 cells: 36 single-pass + 42 consensus + 4
clean PV cells), the sole Tier-1 leader is HIGH-thinking text consensus
*plus* the adversarial verifier (F1 0.792, MCC 0.676), statistically clear
of everything below — the verifier's lift (0.775 → 0.792) is what breaks
the old six-way consensus tie (analysis `era1-leaderboard`, 2,351/3,321
pairs significant, 10 tiers). Just as consequentially for budgets, a
MINIMAL single-pass plus verifier — two calls per tile — reaches the same
tier as the 30-call HIGH-thinking consensus (0.770), beating it on MCC.

The verifier also interacts strongly with tile size (H11). The tile-size
optimum is architecture-dependent: single-pass climbs monotonically with
tile size (256 px 0.342 < 384 px 0.520 < 512 px 0.606 in the clean
isolation), because without any false-positive filter larger tiles give
cleaner context; consensus prefers 384 px; and under consensus + verifier
the ordering is **384 (0.890) > 256 (0.856) > 512 (0.792)** (analysis
`tile-size-sweep`). The most striking single number is the verifier's
rescue of 256 px: the same 256 px consensus pool scores 0.460 bare and
0.856 verified (+0.396) — small tiles flood the proposer with false
positives that the verifier is then very good at pruning.

The study headline follows: **F1@20 m 0.890 / MCC 0.790** on the GS 384 px
instrument, from 30 HIGH-thinking text passes, a ≥16-of-30 consensus vote,
and a single adversarial verifier pass
(`pv-diag-384::verified-adv-text-consensus-16of30`). A completeness sweep
of all 18 never-swept proposer pools later confirmed this is the global
optimum of the 30-pass union, not an artefact of the operating points
swept (analysis `unswept-pools-completeness`, Obs 363).

## R5. Verifier robustness: every cheaper option ties, so the cheap stack wins

A dedicated robustness programme (≈ $54 flex as-run, recorded at run
time) stress-tested every parameter
of the production verifier (gemini-3-flash, adversarial text, minimal
thinking, T = 0.0, n = 1). The summary is uniform: **nothing more expensive
is measurably better** (citable home:
`results/verifier-robustness/verifier-robustness-findings.md`).

- **Determinism / n = 1.** Five-fold verifier replication shows single-run
  SD of 0.0025–0.0072 F1 with consensus ≈ mean — the n = 1 production
  verifier is vindicated (Obs 354).
- **Temperature and thinking.** A thinking × temperature matrix at N = 5 is
  one statistical tier (0/10 pairs significant, F1 0.8709–0.8764); only
  single-pass HIGH thinking *drops* a tier (0.8519) — more deliberation
  makes a lone adversarial pass more spuriously rejecting (analysis
  `verifier-robustness-matrix`).
- **Verifier consensus.** Even at the headline's 30-pass proposer, an N = 5
  verifier consensus lifts F1 only +0.0049 (0.8951 vs 0.8902), p = 0.363 —
  a numerical high, not a new ceiling (analysis `pass-budget-pareto`).
- **Compute allocation.** At equal call budget, proposer passes beat
  verifier passes (10-proposer + 1-verifier 0.8769 ≥ 5 + 5 0.8739–0.8764).
- **Verifier model.** A Pro-class verifier ties the Flash verifier on the
  pools that matter and costs more; one refinement from the completeness
  sweep is that on *high-recall* pools the Pro verifier shows a small
  post-hoc advantage (0.8792, raw p = 0.019, not multiplicity-controlled),
  itself dominated on cost (Obs 363).
- **Proposer and verifier model upgrades.** Neither Gemini Pro 3.1 nor
  Flash 3.5 wins any role. Pro is a genuinely better *bare* proposer but a
  worse PV partner — its near-deterministic sampling caps pool recall. The
  Flash 3.5 2×2×2 (proposer × verifier × n; ~$34) ties bare (0.6196 vs
  0.6204), loses as PV proposer (−0.0355, p = 0.035 — the one
  statistically resolved role gap), and ties as verifier at 3× the price
  (p = 0.17 / 0.10), so the cost rule decides against it (analysis
  `flash35-model-roles`).

These results crystallised into the programme's meta-rule: **on a
within-noise tie, take the cheaper configuration** (Obs 357) — and on the
GS instrument the cheaper option pointed the same way on every axis tested
(n = 1 over consensus, minimal over high, Flash over Pro and Flash 3.5,
proposer passes over verifier passes). Section R6 qualifies the rule's
scope.

The mechanism unifying these findings is that **the verifier shifts the
binding constraint from precision to pool recall** (Obs 359). Once a
verifier prunes false positives, what limits F1 is whether the proposer
pool *contains* the mounds at all. Temperature-sampled diversity is the
cheapest way to raise reachable recall: minimal-thinking T = 0.7 passes
saturate Flash's recall ceiling at 0.9195 within ~5 passes (passes 6–10
add zero new ground-truth mounds, only vote evidence); HIGH thinking adds
volume (union growth per pass 2.46 vs 1.44) but only +0.023 of ceiling;
and a zero-diversity anchor (a single T = 0.0 pass + verifier) scores
0.8142 — temperature diversity is worth +0.057, about 60 % of it via the
ceiling lift. The consensus-era diversity dividend (§ R3) is thereby
*explained and retired* for PV architectures: at equal pass count,
minimal-thinking proposers reach statistical parity with HIGH (min6 0.8784
vs high6 0.8641, p = 0.66; min11 0.8835 vs high11 0.8769, p = 0.59; min11
vs the 31-pass headline, p = 0.56; analysis `min-vs-high-thinking-pv`) —
on the GS instrument. The same comparison reverses at deployment (§ R6).

## R6. The cost frontier, and what deployment does to it

Re-pricing the pass ladder in dollars (per-item token metadata at June
2026 flex rates, thinking tokens billed at the output rate; a
HIGH-thinking deployment pass costs ~8.6× a minimal one — token-load
audit, 2026-06-12) collapses the frontier onto four rungs (analysis
`pass-budget-pareto-v2`; all seven rungs remain one statistical F1 tier,
0/21 pairs):

| rung | F1@20 m (GS) | GS run cost | 55-map production (est.) | frontier |
|---|---:|---:|---:|---|
| min6 (5 minimal passes + vf) | 0.8784 | $2.43 | ~$43 | efficient |
| min11 (10 minimal passes + vf) | 0.8835 | $4.00 | ~$70 | efficient |
| high6 | 0.8641 | $14.04 | ~$246 | dominated |
| high5+5vf | 0.8739 | $14.41 | ~$253 | dominated |
| high11 | 0.8769 | $26.97 | ~$473 | dominated |
| high31 (headline) | 0.8902 | $69.21 | ~$1,214 | efficient |
| high35 (opmax) | 0.8951 | $71.23 | ~$1,249 | efficient |

Read naively, the table says: buy minimal thinking; the entire HIGH ladder
is dominated. **Deployment says otherwise, and this is one of the study's
central findings.** The min6 recipe had already run at production scale as
the 55-map text-minimal deployment: on the 55-map standardised board it
scores 0.8109 (Tier 3), two tiers below the HIGH-thinking equivalent at
the matched threshold (TH7-k3, 0.8387, Tier 1) — the GS tie, where minimal
was numerically *ahead*, reverses by −0.028 on the instrument with the
statistical power to resolve it (Obs 362). The transfer table makes the
pattern systematic — every configuration degrades from GS to deployment,
and they do not degrade equally (GS F1@50 m → 55-map F1@50 m,
standardised reference):

| config | GS @50 m | 55-map @50 m | transfer delta |
|---|---:|---:|---:|
| text HIGH T0.7 | 0.8908 | 0.8387 | −0.052 |
| text HIGH T0.3 | 0.9045 | 0.8393 | −0.065 |
| image HIGH T0.7 | 0.8771 | 0.8010 | −0.076 |
| text MIN T0.7 | 0.8996 | 0.8109 | −0.089 |

(GS side: `results/55map-leaderboard/gs-vs-55map-transfer.md` — note
that document's 55-map column is the canonical-reference vintage; the
55-map side of THIS table is the standardised board. The GS T0.3 cell —
the deployment champion's proposer, characterised at $2.06 — completed
the table.) The deployment champion *started higher on GS and degraded
more*; HIGH-T0.7 transfers best. GS clustering at 0.88–0.90 concealed
differential deployment robustness.

Two consequences follow. First, the cost meta-rule (Obs 357) is
**scope-qualified**: it holds only where the tie's instrument could have
detected a difference of consequence — the 487-tile GS instrument cannot
resolve ±0.03, and deployment evidence overrides characterisation ties.
Second, the gap is partly *buyable*: doubling the minimal pass count
(Run B; as-run ≈ $35 at audited flex rates) closes about half of it. The
10-minimal-pass uplift cell scores 0.8279 at 50 m — significantly above
the 5-pass minimal deployment (+0.0170, p < 10⁻⁴) and significantly below
the HIGH-thinking cell (−0.0108, BH p = 0.018) — converting the thinking
choice at deployment into a priced cost/quality trade (~$58 for 0.828 vs
~$207 for 0.839 at audited production rates) rather than a tie (Obs 364;
run `55maps-text-min-n10-uplift`). The confusion-matrix decomposition of
the frontier steps (Obs 365, re-measured on the standardised reference
with Obs 365's own endpoints) shows the two purchases differ in kind:
the pass-count step (min5 → min10) is a strict improvement (+113 mounds
*and* −31 false positives for ~$26), while the step from the uplift
cell to the board-leading HIGH configuration (T0.3 × 3-of-5, which
moves thinking level, temperature, and threshold together) trades
precision for recall (+282 mounds at +262 false positives for ~$203 at
the audited production rate).

## R7. Deployment: the 55-map standardised board

The deployment board (ruling-21 standardised reference, 50 m, eight
cells, 24/28 pairs significant, five tiers; analysis
`55map-standardised-leaderboard-50m` — tier structure identical to its
canonical-reference predecessor, so the reference standardisation moved
magnitudes, never conclusions) is ordered by F1 because it is the board;
**the study's primary deployment claim is the carry-forward row**
(0.8169) — the operating point actually committed to before deployment,
per the calibrate-then-deploy protocol. Every row above it relaxes at
least one carried-forward setting (vote threshold, temperature, or pass
count) after seeing deployment results; those rows are reported not as
achieved performance but as the measured deployment gap — what better
calibration transfer would have bought (lesson i below), with the joint
oracle (+0.022) as its upper bound:

| rank | cell | tier | F1@50 | tile-MCC |
|---:|---|---:|---:|---:|
| 1 | text HIGH T0.3, vote 3-of-5 (oracle) | 1 | 0.8393 | 0.689 |
| 2 | text HIGH T0.7, vote 3-of-5 | 1 | 0.8387 | 0.680 |
| 3 | text HIGH T0.3, vote 4-of-5 | 2 | 0.8303 | 0.669 |
| 4 | text MIN, 10 passes, vote 5-of-10 (uplift) | 2 | 0.8279 | 0.671 |
| 5 | text HIGH T0.7, vote 4-of-5 (carry-forward) | 3 | 0.8169 | 0.665 |
| 6 | text MIN, vote 3-of-5 | 3 | 0.8109 | 0.657 |
| 7 | image, vote 3-of-5 | 4 | 0.8010 | **0.712** |
| 8 | text MIN, vote 4-of-5 | 5 | 0.7833 | 0.640 |

Three deployment lessons sit in this table. **(i) The calibrate→deploy gap
is a threshold-transfer failure, not a model failure** (Obs 358): the
configuration carried forward from GS calibration (T0.7 × 4-of-5) left
+0.022 F1 on the table against the joint oracle (T0.3 × 3-of-5, 0.8393,
p < 0.001), and the threshold axis alone accounts for most of it — vote
3-of-5 beats the carried 4-of-5 for all three text configurations
(+0.009 to +0.028, all BH p ≤ 0.001). On the GS sheets those thresholds
had sat on a statistical plateau; at deployment scale the plateau
resolves, and it resolves *looser* — a pattern that recurred when the
uplift cell's best deployment threshold (5-of-10) again sat looser than
its GS optimum (6-of-10). **(ii) Thinking level is a priced trade**
(§ R6). **(iii) The F1/MCC trade-off recurs at deployment, and it is
statistically resolved**: the image configuration ranks seventh on F1
but carries the board's best tile-MCC (0.712), and re-tiering the same
eight cells on the MCC statistic — the identical permutation machinery,
applied to the present/not-present tile signal rather than coordinate
F1 — makes the image cell the **sole Tier-1 cell** on that axis,
statistically clear of all seven others including the F1 co-leaders
(ΔMCC +0.023 vs the MCC runner-up, BH p = 0.0014; analysis
`55map-standardised-leaderboard-mcc-50m`, 20/28 pairs significant, five
tiers — tier structure and significant-pair set identical to the
canonical-reference board). The MCC tier order inverts the F1 board's
top while the six text-only cells keep their F1 ordering, so the
reversal is a modality effect rather than noise; the item-4 re-measurement
(`results/55maps-standardised-ref-2026-08-14/obs280-remeasurement.md`)
shows it is ≈90 % metric behaviour, not reference effect. For survey
prioritisation, where tile-level discrimination matters more than exact
counts, the image pipeline is not the loser the F1 column suggests — it
is the resolved best instrument, at two calls per tile.

[Resolved 2026-06-13: carry-forward primary, oracle as the measured
deployment gap, table F1-ordered as the board — implemented in the
subsection lead; see Changelog.]

## R8. What the ground truth can and cannot support

Because every metric above is bounded by the reference data, we measured
the reference data's own error structure rather than assuming it away
(Obs 361, Obs 396). **Precision is review-verified and
position-marked**: the standardised 55-map reference absorbed a human
review of every cross-configuration detection cluster — the
773-candidate phantom pool was adjudicated point by point (278 of the
773 confirmed as distinct real mounds the students missed, plus one
marking-pass extra; the rest resolved as duplicates of student records
or non-mounds) and every
reviewed position hand-marked to the mound centre (±2.5 m) — so
reported precision is robust to GT omissions. **Recall is a measured
upper bound with quantified opposing biases**: on the GS sheets, where
a curator reference exists, configurations miss mounds the GT contains
at a rate implying reported 55-map recall is inflated by ~2.4–2.7 %;
because the double-miss correlation between independent configurations
is only 1.5–1.7× (4/435 GS double-misses), mounds missed by *every*
configuration — invisible to detection-led review — are rare but
non-zero. In the opposite direction, an estimated ~370 residual
long-range duplicate records among the unreviewed student majority
deflate measured F1 by ≈ 0.03 at a balanced operating point; the net
reference bias at point estimates is ≈ −0.017, rank-preserving to
first order (Obs 396). We therefore present deployment recall with a
+3 %/+5 % sensitivity band rather than a point correction, the band
chosen wide because the correlation estimate rests on four events
(`results/working-precision/gs-miss-correlation.*`).

[Resolved 2026-06-13: stays in Results as a results-of-validation
subsection — everything above is a measured quantity (review-verified
precision, the measured recall bound, the double-miss correlation), and
§ R9 and the deployment claims depend on it. The *implications* (what GT
scarcity means for survey practice) move to Discussion; see Changelog.]

## R9. Selecting a configuration without ground truth

Production discovery runs — the use case this pipeline exists for — land
on map corpora with no reference data at all. The study's closing
analysis asks whether the deployment lessons of §§ R6–R7 can be applied
there, and the answer has three parts (citable home:
`results/gtfree-selection/gtfree-selection-findings.md`; this thread is
anchored to its committed findings document and
`gtfree_selection.json` rather than to a manifest-registered analysis).

First, building a bigger calibration reference is not the realistic
alternative. The permutation machinery's noise scaling (null SD
∝ 1/√N_tiles, validated at both ends of the corpus) prices the
counterfactual: grounding the decisions the GS instrument got wrong
would have needed ~10–20 sheets (~900–1,900 mounds) per decision axis at
80 % power — up to roughly a third of the eventual deployment corpus,
curated up front — and, decisively, sheets sampled from the *deployment
population*: the vote-threshold direction actually reversed on the
curated GS sheets, so more tiles of the same sheets would have converged
confidently on the wrong answer. Representativeness, not size, was the
binding failure (Obs 366 § 2).

Second, deploying the calibration *tie-set* instead is affordable.
Because threshold sweeps are free post hoc (verify a permissive band
once, sweep vote/probability thresholds on the recorded verifier
probabilities) and pass pools nest (a 10-pass campaign contains its
5-pass rung under the first-N rule), the end-of-calibration tie-set —
thinking level, temperature, modality, pass count — collapses to four
proposer pools: ~25 passes, ~$733 audited flex on the 8,541-tile corpus.
That is within ~2 % of what the study's five deployment campaigns
actually spent (≈ $722, audit § 6) — the programme converged on the
minimal covering design incrementally, without having planned it
(Obs 367).

Third — the new result — the best run can then be identified **from the
runs alone**. A leave-one-family-out (LOFO) consensus pseudo-ground-truth
— union the *other three* configuration families' detections,
single-linkage cluster at 50 m, keep clusters supported by ≥ 2 distinct
families, score each cell against its own family's held-out reference —
ranks the eight deployment cells at **Spearman ρ = +0.881** against the
true board (measured against the canonical-reference board; the
standardised re-tiering preserved the full rank order, so ρ is
unchanged), with no cell ever evaluated against a reference
containing its own family's detections. The GT-free top pick (TH7-k3)
is statistically tied with the true winner on the real board (p = 0.127
on the canonical reference; the tie deepens to p = 0.857 on the
standardised one):
the "miss" sits inside a tie the 8,541-tile instrument itself cannot
resolve, and the cost meta-rule then breaks the residual tie at exactly
the scope § R6 qualified it to. Two boundary conditions frame the
result. The consensus must be permissive: requiring unanimity of the
other families *inverts* the ranking (ρ = −0.095), because a unanimous
reference amplifies the double-miss blind spot § R8 measures for the
real GT — the pseudo-ranking is therefore precision-tilted, and the
practitioner should keep the recall-permissive lean that the
threshold-transfer lesson (§ R7) independently recommends. And the
validation is a retrodiction on one corpus, one symbol type, and eight
cells; a prospective, preregistered application to a new corpus is the
natural test. The four-step field protocol (deploy the tie-set → rank by
LOFO vote ≥ 2 agreement → break the residual tie by cost with a
recall-permissive lean → sanity-check with the free vote-distribution
and density diagnostics) is specified in the findings document, § 5.

---

## Changelog

### 2026-08-14 (b) — Blind-verifier corrections applied

Fresh-context blind verifier over the item-5 refresh: 764 claims
identified / 752 re-derived / 747 confirmed / 5 corrections. All
applied: (1) SUBSTANTIVE — the Obs 365 thinking-step figures had
silently switched comparator (uplift → TH7-k3, ≈ $149) while keeping
Obs 365's T03-k3 price (~$206); restored Obs 365's own endpoint with
the standardised numbers (+282 mounds / +262 false positives for
~$203, third-re-derived from the CSV and the token-load audit) and
named what the step moves (thinking + temperature + threshold);
(2) the revision banner updated (it still read 2026-06-13); (3) an
in-text vintage note added at the transfer-table pointer
(`gs-vs-55map-transfer.md` remains canonical-vintage); (4) the R8
phantom census corrected to 278-of-773 + 1 marking-pass extra;
(5) the standardised MCC board's `condition_dir` provenance fixed in
the harness and the board regenerated (values unchanged). Also: R0
now states the reference's mixed positional provenance (641 + 279
marked vs 4,090 as-digitised), and R7's "text family" tightened to
"the six text-only cells". The previous entry's Obs 365 changelog
row should be read with correction (1): its "now" column mixed a
reference move with an endpoint change; the corrected step is
+282/+262. Prior entry landed at `a4dc67e3d`.

### 2026-08-14 — All 55-map figures moved to the standardised reference (queue item 5)

**Refresh trigger**: the reference-standardisation queue's items 2–5
(ruling 21) — the eight board cells re-scored against the standardised
reference (`results/55maps-standardised-ref-2026-08-14/`), both boards
re-tiered (analyses `55map-standardised-leaderboard-50m` /
`-mcc-50m`), and every 55-map figure in this draft re-verified.
**Tier structures are IDENTICAL on both boards**, so no conclusion
moved; magnitudes did:

| figure | was (canonical ref) | now (standardised) |
|---|---|---|
| carry-forward TH7-k4 | 0.8152 | 0.8169 |
| oracle T03-k3 | 0.8476 | 0.8393 |
| joint oracle gap | +0.032 | +0.022 |
| threshold axis (k3 over k4) | +0.012…+0.030 | +0.009…+0.028 |
| TH7-k3 | 0.8425 | 0.8387 |
| TM-k3 / min-vs-HIGH reversal | 0.8127 / −0.030 | 0.8109 / −0.028 |
| uplift cell | 0.8290 (+0.0163/−0.0134) | 0.8279 (+0.0170/−0.0108) |
| Obs 365 steps | +111/−29; +319/+225 | +113/−31; +229/+196 |
| image IM-k3 | 0.7987 / MCC 0.710 | 0.8010 / MCC 0.712 |
| image MCC sole-T1 margin | +0.020, BH p=0.006 | +0.023, BH p=0.0014 |
| transfer deltas (T0.7/T0.3/img/MIN) | −0.048/−0.057/−0.078/−0.087 | −0.052/−0.065/−0.076/−0.089 |

What did NOT change: every tier assignment on both boards, the F1/MCC
divergence lesson (now backed by the item-4 re-measurement — ≈90 %
metric behaviour), the carry-forward-primary framing, the R9 GT-free ρ
(rank order preserved), and all GS-instrument figures (curator GT,
out of ruling-21 scope). § R0's instrument description and § R8's
reference-epistemics paragraph now describe the standardised layers
(4,731 + 279 at marked centres) and carry Obs 396's opposing-bias
band. The T03-k3-vs-TH7-k3 top pair remains statistically tied (p
0.127 → 0.857); T03-k3 keeps rank 1 on points. Landed with this
revision's commit.

### 2026-06-13 (later) — § R7 lesson (iii) given statistical backing

**Refresh trigger**: Shawn requested the alternate-metric permutation
with CIs. The MCC re-tiering of the deployment board
(`results/metric-leaderboards/55map-mcc-tiering.{md,json}`; now the
registered analysis `55map-canonical-leaderboard-mcc-50m`) lands IM-k3
as the sole Tier-1 cell on the tile axis (significant vs all seven,
incl. the F1 oracle at BH p = 0.006). Lesson (iii) was upgraded from a
numerical MCC lead to a resolved sole-Tier-1 statistical claim; no other
result changed. See Obs 369/370.

### 2026-06-13 — Draft notes resolved; § R9 added (Session 114)

**Refresh trigger**: the Session-114 continuity plan (resolve the three
draft notes, fold in the S113 closing-chain material). All three
decisions are Claude's, taken under the S114 "resolve" instruction, and
each is marked `[Resolved …]` in place so Shawn can veto on review:

- **§ R2 (framing)**: board-led compression of the H1/H4/H5/H7/H8
  single-factor results adopted; per-hypothesis detail tables to
  supplementary material. Rationale: the hypotheses share one outcome
  (inside or near the Tier-1 tie) — serial reporting would repeat
  "no separation" five times.
- **§ R7 (oracle ordering)**: carry-forward (0.8152) is the primary
  deployment claim; the oracle and other relaxed rows are the measured
  deployment gap, upper-bounded by the joint oracle's +0.032. Table
  stays F1-ordered as the board. Rationale: preregistration framing —
  the carried operating point is what the protocol committed to.
- **§ R8 (placement)**: stays in Results as results-of-validation
  (measured quantities); implications move to Discussion.
- **§ R9 added**: the GT-free selection protocol (calibration-corpus
  power analysis → deploy-and-evaluate covering design → LOFO consensus
  ranking, ρ = +0.881, vote ≥ 3 inversion, retrodiction caveat).
  Anchored to `results/gtfree-selection/` (not a manifest analysis);
  preamble anchoring claim qualified accordingly.
- **§ R5**: programme cost "~$53 flex" corrected to "≈ $54 flex as-run"
  (sum of the recorded run costs $21.93 + $20.86 + $8.71 + $2.54).
- Methods cost-reporting basis written up as `docs/methods-outline.md`
  § 5.4 (audited basis, billing corroboration, lower-bound caveat,
  write-time gate).

### 2026-06-12 — § R6 dollars rebuilt from the token-load audit

**Refresh trigger**: the token-load audit
(`reports/token-load-audit-2026-06-12.md`) found the prior cost model
sat on a 2× double-counted manifest with thinking tokens unbilled.
§ R6's Pareto table and the production trade were rebuilt at audited
flex rates (min:HIGH ratio 3× → 8.6×; trade ~$105 vs ~$150 → ~$58 vs
~$207; high31 production ~$856 → ~$1,214), and the Obs 365
confusion-matrix decomposition of the frontier steps was added. The
frontier's efficient set, every F1 value, and all statistical claims
are unchanged.

### 2026-06-11 — Original publication

First prose draft (Session 113), written immediately after the
second-wave manifest registration closed the evidential skeleton:
findings doc §§ 1–17, the transfer table, working precisions, GT
epistemics, Pareto v2, and the refreshed 8-cell 55-map board. All
numbers anchored to registered conditions/analyses as of manifest state
31 runs / 306 conditions / 17 analyses (commit `a17d6bba3`).
