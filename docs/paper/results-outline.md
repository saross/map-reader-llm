# Results — structural outline (strawman, decisions OPEN)

> **Status**: working strawman for collaborative structure work (Session 114,
> 2026-06-14). This is a decision-forward outline, **not** prose: every
> structural call is flagged `▸ Dn` and left OPEN, with my recommendation
> marked `(REC)` but not baked in. We redline this together; prose drafting
> waits until the relevant section's structure is agreed. The existing
> `docs/paper/results-draft.md` is the **zero-draft** reference (claims and
> anchors live there) — it is not extended until this outline lands.

## How to read this

- **Part A** holds the spine-level calls (section ordering, what's stated
  where, cross-cutting threads). These shape everything below.
- **Part B** walks the sections at subsection/claim granularity: each
  carries its *purpose*, its *load-bearing claims* (with the evidence
  anchor), and any *in-section decisions*.
- **Decision register** at the very bottom lists all `Dn` in one place with
  my lean, so the easy ones are quick to wave through and the contested
  ones are easy to find.

---

## Part A — spine & cross-cutting decisions

The current zero-draft spine is **architecture-ascending**: build the
pipeline up, then deploy it.

```text
R0 reading guide → R1 precisions → R2 single-pass → R3 consensus →
R4 proposer–verifier → R5 verifier robustness → R6 cost frontier →
R7 deployment board → R8 GT epistemics → R9 GT-free selection
```

**▸ D1 — the overall spine.**

- **A (REC)**: keep architecture-ascending, but make the GS→deployment
  seam explicit (one instrument characterises, the other deploys; R0 sets
  this up). Reads as a build-up to the headline, then a reality check.
- **B**: question-driven (best config? how robust? what cost? does it
  deploy? can you pick without GT?). More reader-friendly, less faithful to
  how the work accreted.
- **C**: characterise-then-deploy — *all* GS results first, then *all*
  55-map results. Cleanest instrument separation, but splits the cost
  story (GS frontier vs deployment economics) across two homes.
- *Lean A*: the ascending build is how the evidence actually layers, and
  the two-instrument seam is the honest place for the deployment reversal.

**▸ D2 — where the headline result lands.**

- **A (REC)**: state the headline once, early (a single sentence at the end
  of R0 or a 2-line "principal result" stub), then derive it in full at R4.
- **B**: keep it only at R4's climax (current draft).
- *Lean A*: readers skim for the headline number; making them reach R4 to
  find 0.890/0.790 is a cost with no benefit.

**▸ D3 — the F1-vs-MCC (metric-dependent-winner) theme.** It recurs at R2
(text wins F1, image wins MCC), R4 (PV lifts MCC), and R7 (image is the
*registered* sole-Tier-1 MCC cell at deployment).

- **A (REC)**: distributed but *threaded* — name it once at R2, call back
  explicitly at R4 and R7, so the reader tracks one recurring theme rather
  than three coincidences.
- **B**: consolidate into its own short cross-cutting subsection.
- **C**: leave distributed, no explicit thread (current draft).
- *Lean A*: it's a genuine secondary finding (and the basis of the
  "tiles-as-a-deliverable" Discussion seed), but it doesn't carry a whole
  subsection on its own.

**▸ D4 — the GS-cost / deployment-economics split** (touches R6+R7). The
cost frontier (R6) is a *GS-characterisation* result; the deployment
reversal + transfer table are *deployment* results, but the current draft
fuses them in R6 and then partly re-tells the reversal in R7.

- **A (REC)**: split — R6 = the cost frontier as a GS result; move the
  transfer table + reversal + "buyable gap" into the deployment block (R7),
  so the reversal is told once, where the board is.
- **B**: keep fused (current draft).
- *Lean A*: removes the double-telling of the min→HIGH reversal and keeps
  each result on its own instrument.

---

## Part B — section by section

### R0 — Reading guide: instruments, metrics, conventions

- **Purpose**: orient the reader to the two instruments (GS characterisation
  vs 55-map deployment) and the one statistical machinery, so each later
  result can be read correctly.
- **Claims**: two-instrument framing; headline metric = buffered F1 at an
  empirical working precision + tile-MCC; tile-swap permutation + BH-FDR +
  greedy-clique tiering throughout. Anchor: §R0 of the zero-draft.
- **▸ D5**: keep R0 as a Results subsection, or fold the stats-convention
  detail into Methods and leave only a 2–3 line orientation here?
  **(REC: trim — orientation stays, convention detail → Methods)** to avoid
  duplicating Methods.

### R1 — Working precisions are empirical, not free parameters

- **Purpose**: justify the buffer radii (GS 30 m text / 75 m image; 55-map
  50 m) as data-derived properties, not analyst choices.
- **Claims**: text plateau 30 m, image 75 m, modality dominates architecture
  (`gs-plateau-characterisation`); 55-map 50 m from three converging lines
  (`55maps-csr-noise-floor`). Anchor: §R1.
- **▸ D6 — Results or Methods?** Deriving the buffer is data-driven but
  reads as methodology.
  - **A (REC)**: Methods (the derivation) + a one-line Results recap of the
    chosen radii.
  - **B**: keep wholly in Results (current).
  - *Lean A*: it's a calibration decision; Results should consume it, not
    derive it. But it's a genuine empirical result, so the call is real.

### R2 — Single-pass baselines: a floor, and which factors moved it

- **Purpose**: establish the ~0.63 single-pass floor and report what the
  preregistered single-factor sweep did and did not separate.
- **Claims**:
  - Floor: 36 single-pass cells → 4 tiers, a broad 20-cell Tier-1 tie
    (F1 0.583–0.631); the GS set cannot separate the stronger configs
    (`era1-single-pass-baseline-matrix`). **Load-bearing.**
  - Modality: no clean F1 win, but drives the F1↔MCC trade (text→F1,
    image→MCC) — forward-ref §R1 precision gap and §R7 deployment MCC.
  - Temperature: T=0.0 > T=0.7, a clean Tier-1/Tier-2 split
    (`n1-baseline-matrix-384`, Pro).
  - Inert: prompt elaboration (H1), ordering (H4), negative-text (H5),
    example-library (H8) — all inside the tie.
  - Signpost: thinking level is inert-to-harmful at single pass; its effect
    arrives under consensus (→ R3).
- **▸ D7 — the factor split** (the one we discussed). Group the four inert
  factors in one sentence; pull out modality (as a trade) and temperature
  (T=0 best); route thinking level forward to R3. **(REC: yes — this
  version.)**
- **▸ D8 — board basis.** The floor lives on the Flash 512 px board; the
  temperature signal lives on the Pro 384 px matrix.
  - **A (REC)**: lead with the Flash board (the floor), bring in the Pro
    matrix for the temperature result and the genuine-Pro context.
  - **B**: one board only (drop the temperature claim or relocate it).
  - *Lean A*: temperature is a real single-pass signal worth keeping; it
    just needs its correct (Pro) home named.

### R3 — Consensus voting buys performance; the mechanism is pass diversity

- **Purpose**: the first large clean gain (single-pass → 0.69–0.77) and its
  mechanism (diversity, not pass count).
- **Claims**: diversity dividend — HIGH-thinking consensus ≫ minimal at
  matched N (`diversity-dividend-384`); engineered diversity adds nothing
  (H9 rejected); permissive thresholds win, unanimity hurts; the
  consensus-era "buy HIGH thinking" reading is revised by R5. Anchor: §R3.
- **▸ D9 — the dividend's "retirement" under PV** is asserted here but only
  demonstrated at R5. Keep the forward-reference, or move the
  retirement next to the dividend? **(REC: keep forward-ref + a one-line
  signpost)** — the retirement needs the verifier machinery R4/R5 build.

### R4 — Proposer–verifier is the best architecture on every tile size

- **Purpose**: the key architectural move (H2) and the study headline.
- **Claims**:
  - PV is the sole Tier-1 Era-1 leader; the verifier's lift breaks the
    consensus tie (`era1-leaderboard`). **Load-bearing.**
  - Cheap PV (minimal single-pass + verifier, 2 calls/tile) reaches the
    30-call HIGH tier, beating it on MCC (→ D3 thread).
  - Tile size × verifier (H11): architecture-dependent optimum; verifier
    *rescues* 256 px (0.460→0.856) (`tile-size-sweep`).
  - **Headline**: F1@20 m 0.890 / MCC 0.790, global optimum confirmed
    (`unswept-pools-completeness`). **Load-bearing.**
- **▸ D10 — tile size (H11)**: keep folded into R4 (it's a PV story), or
  give it its own subsection? **(REC: keep folded.)**
- (Headline placement = D2.)

### R5 — Verifier robustness: every cheaper option ties, so the cheap stack wins

- **Purpose**: stress-test the production verifier; establish the cost
  meta-rule and the recall-ceiling mechanism.
- **Claims** (currently six axes — determinism, temp/thinking, verifier
  consensus, compute allocation, verifier model, model upgrades): all tie;
  nothing dearer is better; meta-rule "on a within-noise tie, take the
  cheaper config" (Obs 357). Mechanism: the verifier shifts the binding
  constraint precision→pool recall (Obs 359). Anchor: §R5.
- **▸ D11 — compress the six axes** into the meta-rule + a summary table
  (per-axis detail → supplement)? **(REC: yes — meta-rule + table;** the six
  bullets are dense and individually minor.)
- **▸ D12 — elevate the recall-ceiling mechanism.** It explains R3 (why
  diversity helps), R4 (why the verifier wins) *and* R6 (why minimal ties
  HIGH on GS). Keep it as R5's closing paragraph, or pull it into its own
  short mechanism subsection the others point back to? **(REC: elevate)** —
  it is the conceptual hub of the pipeline story.

### R6 — The cost frontier (GS)

- **Purpose**: price the pass ladder; show the efficient set.
- **Claims**: audited flex re-pricing collapses the frontier to four rungs;
  all seven rungs one F1 tier on GS (`pass-budget-pareto-v2`). Anchor: §R6
  front half. **Cost basis = audited (token-load audit); cite audited
  dollars only.**
- (Deployment transfer/reversal moves out per **D4** → R7.)

### R7 — Deployment: the 55-map board (+ transfer, reversal, buyable gap)

- **Purpose**: what a GS-calibrated config actually delivers on a large
  unseen corpus, and the three deployment lessons.
- **Claims**:
  - Board: 8 cells, 5 tiers, 24/28 sig (`55map-canonical-leaderboard-50m`).
  - The min→HIGH reversal: GS tie reverses −0.030 on the instrument with
    power to resolve it (Obs 362); cost meta-rule scope-qualified.
  - Transfer table: every config degrades, unequally; HIGH-T0.7 transfers
    best. Buyable gap: +pass-count closes ~half (Obs 364).
  - Lesson (i) threshold-transfer failure (Obs 358); (ii) thinking is a
    priced trade; (iii) F1/MCC trade → image is the **registered sole
    Tier-1 MCC cell** (`55map-canonical-leaderboard-mcc-50m`; → D3 thread).
- **▸ D13 — carry-forward vs oracle ordering** (original decision).
  - **A (REC)**: carry-forward (0.8152) is the primary deployment claim;
    oracle + relaxed rows = the measured deployment gap (+0.032 upper
    bound); table F1-ordered.
  - **B**: oracle-led (0.8476 as best-achievable; carry-forward as a
    sensitivity row).
  - *Lean A*: preregistration honesty — the oracle is post-hoc threshold
    selection; lead with what the protocol committed to.

### R8 — What the ground truth can and cannot support

- **Purpose**: bound every metric above by measuring the reference data's
  own error structure.
- **Claims**: precision review-verified; recall a measured upper bound
  (+2.4–2.7 %); double-miss correlation 1.5–1.7×; present a +3 %/+5 % band
  (Obs 361). Anchor: §R8.
- **▸ D14 — Results or Discussion** (original decision).
  - **A (REC)**: Results as results-of-validation (measured quantities R9
    and the deployment claims depend on); implications → Discussion.
  - **B**: move the whole subsection to Discussion as a validity passage.
  - *Lean A*: it reports measurements, not interpretation.

### R9 — Selecting a configuration without ground truth

- **Purpose**: complete the production story — deploy, rank GT-free,
  tie-break by cost — for corpora with no reference data.
- **Claims**: calibration-corpus power analysis (Obs 366 §2); the ~$733
  covering design ≈ $722 as-run (Obs 367); LOFO consensus ranks at
  ρ = +0.881, permissive-only, retrodiction caveat (Obs 368). Anchor: §R9,
  `gtfree-selection-findings.md`.
- **▸ D15 — Results or Discussion?** It carries a measured result
  (ρ = +0.881) but is framed as a falsifiable *proposal*.
  - **A**: Results (it has a result).
  - **B**: Discussion (it's a proposed method / future-facing).
  - **C (REC?)**: split — the validation result stays in Results, the
    protocol + prospective-test framing go to Discussion.
  - *Genuinely undecided* — this is the call I'd most want your read on.

---

## Decision register (at a glance)

| Dn | section | the call | my lean |
|---|---|---|---|
| D1 | spine | architecture-ascending vs question-driven vs characterise-then-deploy | **A** ascending |
| D2 | spine | state headline early vs only at R4 | **A** early |
| D3 | spine | F1-vs-MCC theme: threaded vs own subsection vs distributed | **A** threaded |
| D4 | R6/R7 | split GS-cost from deployment, or keep fused | **A** split |
| D5 | R0 | trim reading guide (convention → Methods) vs keep | **A** trim |
| D6 | R1 | working precisions: Methods+recap vs all-Results | **A** Methods+recap |
| D7 | R2 | factor split (inert group + pull out modality/temp; thinking → R3) | **A** yes |
| D8 | R2 | Flash board lead + Pro matrix for temperature, vs one board | **A** both |
| D9 | R3 | dividend-retirement: forward-ref vs co-locate | **A** forward-ref |
| D10 | R4 | tile size folded into R4 vs own subsection | **A** folded |
| D11 | R5 | compress six robustness axes to meta-rule + table | **A** compress |
| D12 | R5 | elevate the recall-ceiling mechanism to its own hub subsection | **A** elevate |
| D13 | R7 | carry-forward primary vs oracle-led | **A** carry-forward |
| D14 | R8 | Results (validation) vs Discussion | **A** Results |
| D15 | R9 | Results vs Discussion vs split | **C?** split — least sure |

**The three you originally flagged map to D7 (§R2), D13 (§R7), D14 (§R8).**
D15 (§R9) is the new one I'm least sure about. The rest (D1–D6, D8–D12) are
the structural calls that surfaced from thinking about the spine — most have
a clear lean and should be quick to wave through or veto.
