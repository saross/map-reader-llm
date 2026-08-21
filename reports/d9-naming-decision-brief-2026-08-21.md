# D.9 naming decision brief: what to call the analysis-grain, LLM-supported registration recipe

> **Last revised**: 2026-08-21 (original publication). See
> [§ Changelog](#changelog) for revision history.

**Status**: decision **DEFERRED to prose time** (PI, Session 139,
2026-08-21) — the PI wants to read Gould et al. (2026) in full and
discuss before ruling. This brief records everything that fed into the
options as presented, so the discussion can resume without
reconstruction.

**The decision**: the Discussion's preregistration retrospective (D.9,
Seed 7) proposes a registration recipe — a lean upfront registration
(design-level commitments, a few sharp confirmatory hypotheses,
procedural rules) plus just-in-time, LLM-supported mini-registrations
authored outcome-blind at each analysis boundary. The project record
calls this "micro-registration". The S139 lit-scout novelty check
(verified 31/31 rows, 155/155 claims,
`docs/methodology/research/lit-scout-micro-registration-2026-08-21.md`)
found near prior art, so the name and framing need a deliberate ruling.

## The verified evidence

**Verdict: (b) ADJACENT BUT DISTINCT — the margin is thin and one
paper old.** A qualified novelty claim survives; an unqualified one
will not. Element by element (from the verified report):

| Proposal element | Status | Nearest prior art |
|---|---|---|
| Unit-of-registration shrinkage (project → analysis) | NAMED PRIOR ART | Gould et al. (2026) "interim preregistrations"; the SAP tradition (Gamble et al. 2017; Hemming et al. 2020); secondary-data templates (Van den Akker et al. 2021; Willroth et al. 2022) |
| Just-in-time timing (authored at the boundary) | NAMED PRIOR ART | Gould et al. (2026) — registration "in parallel with modelling… as different parts of the data are observed"; Ioannidis (2022) reportedly floats per-step registration [characterisation UNVERIFIED — read the PDF first] |
| Outcome-blind commitment before the run it governs | MATURE PRIOR ART, different tradition | SAP finalised before unblinding; blind analysis (MacCoun & Perlmutter 2015); analysis blinding (Sarafoglou et al. 2023) |
| Lean upfront layer + procedural rules | ADJACENT | Gould et al. "registered flexibility" (decision trees); Lin & Green (2016) SOPs; Strobl et al. (2026) SIMP2L "Statement of Intent" |
| Waterfall-to-agile framing applied to registration | NOT FOUND | "Agile science" exists (Hekler et al. 2016) but has never been pointed at preregistration |
| **LLM-supported authoring of the registrations** | **NOT FOUND — the empty cell** | Zero hits; the entire LLM/preregistration intersection is "preregistering studies *of* models" (Vaccaro 2026; Thomas et al. 2026; van Miltenburg et al. 2021), never models *writing* registrations |
| The term "micro-registration" | UNOCCUPIED | No hits for micro-/mini-/modular (pre)registration; "just-in-time preregistration" also unoccupied |

**The key comparator**: Gould et al. (2026), "'But I can't preregister
my research': Improving the reproducibility and transparency of
ecology and conservation with adaptive preregistration for model-based
research", *Methods in Ecology and Evolution*, 10.1111/2041-210x.70311.
Zero citations at query time; published months before the check. Their
two components — *registered flexibility* (preregistered decision
trees: what information is needed, what analysis generates it, which
result triggers which branch) and *interim preregistrations*
(versioned registrations marking key phases as parts of the data are
observed) — map onto the proposal's procedural rules and just-in-time
mini-registrations respectively. Their interims are **phase-based**;
the proposal's are **per-analysis** — the sharpest point of contrast,
per the scout. The genuine companion preprint is 10.32942/X2DQ0K
("A Framework for Questionable Research Practices in Ecological
Modelling"); 10.32942/X2GW66 is the preprint of the same paper, not a
companion (verifier correction).

## The options as presented (AskUserQuestion, S139)

1. **"Just-in-time preregistration"** *(the scout's and verifier's
   suggestion, and the recommended option as presented)*: unoccupied,
   descriptive, and names exactly what distinguishes the variant from
   Gould et al.'s phase-based interims. Cite and contrast Gould et al.
   explicitly; the LLM-support element carries the novelty.
2. **Adopt "adaptive preregistration" + modifier** (e.g. LLM-assisted
   adaptive preregistration): most field-friendly; avoids two coinages
   for one mechanism; cedes the name but keeps priority on the LLM
   element, which is the clean novelty anyway.
3. **Keep "micro-registration"**: unoccupied and already used in the
   project record — but competes with a published journal article that
   will likely win priority for the shared parts.
4. **Defer to prose time** ← **TAKEN** (PI): rule after reading Gould
   et al. in full — the contrast may be sharper or weaker than the
   abstract suggests.

**Field-hygiene consideration** (scout, Gaps § 5): "micro-registration"
is free, but so was "adaptive preregistration" until months ago; two
competing coinages for one mechanism is a worse outcome for the field
than adopting the incumbent term with a modifier or choosing a name
that marks a real distinction.

## The framing recommendation (independent of naming; verified report)

Reframe D.9's recipe from *proposal* to **convergent independent
proposal plus cross-domain generalisation**: cite Gould et al. as the
closest published statement and adopt or explicitly contrast their
vocabulary; cite the SAP tradition (Gamble et al. 2017,
10.1001/jama.2017.18556; Hemming et al. 2020, 10.1186/s13063-020-04828-8)
to convert the idea from speculation to proven-pattern import; locate
the paper's contribution in (i) the LLM-support element, (ii) the
agile framing, and (iii) the worked instance in a computational
evaluation setting. Two secondary contributions are available
regardless of naming: bridging the adaptive-preregistration and SAP
literatures, which do not cite each other (verified structural hole);
and arguing unit-shrinkage *on principle*, where the secondary-data
literature shrinks the unit only because circumstance forces it.

## The PI's inputs so far (S139, recorded in Seed 7)

- **Good-outcome reading**: the parallel literature's recency signals
  convergent recognition of the need — plausibly driven by the same
  tooling shift; the underplayed LLM/AI element is the opening.
- **The friction argument**: LLM assistance collapses both composition
  and update/revision friction (automated OSF updates alone save
  perhaps half an hour of interface overhead per amendment, after all
  text is composed). Low friction is the mechanism that makes
  analysis-grain registration practicable — it ties the LLM claim to
  the unit-shrinkage claim.
- **Genre-appropriateness**: preregistration is a genre where
  AI-generated text is appropriate (with a style guide intercepting
  tics) because the document is a procedural instrument valued for
  commitment and verifiability, not authorial voice — unlike journal
  articles or blog posts.
- **First-person anchor**: Ross and Ballsun-Stanton (2022),
  "Introducing Preregistration of Research Design to Archaeology",
  University Press of Florida, 10.5744/florida/9780813069302.003.0002
  (SocArXiv preprint 2021, 10.31235/osf.io/sbwcq) argued the *why* at
  a time of high friction; the friction collapse realises that
  ambition.

## Reading before the discussion

1. **Gould et al. (2026)**, 10.1111/2041-210x.70311 — in full; the
   decision-determining read. Also the genuine companion,
   10.32942/X2DQ0K.
2. **Gamble et al. (2017)** and **Hemming et al. (2020)** — the SAP
   timing structure and content guidelines.
3. **Ioannidis (2022)**, 10.1016/j.mbs.2022.108782 — obtain the PDF
   via institutional access; the per-step-registration sentence is
   uncorroborated by any accessible source (verifier advisory note 1)
   and must not be cited without it.
4. **Lakens (2024)**, 10.1525/collabra.117094 — the incumbent
   deviation-repair position the recipe claims to dominate.

## Questions to resolve in the discussion

1. Adopt, extend, or contrast Gould et al.'s vocabulary — and which
   name, if any, does the paper put forward?
2. How prominently does the LLM-support element lead (the scout's
   inverted finding: the element the project treated as incidental is
   the only clean novelty)?
3. Does D.9 claim the C1↔C3 bridge (adaptive-prereg ↔ SAP
   non-citation) as a secondary contribution?
4. Does the prospective GT-free test (D.10 headline item) and any
   future preregistration adopt the chosen name, so the paper's own
   practice demonstrates the recipe under its final label?

## Pointers

- Verified novelty report:
  `docs/methodology/research/lit-scout-micro-registration-2026-08-21.md`
- Seed 7 (with the S139 augmentations):
  `docs/paper/discussion-seeds.md`
- Outline home and gate status: `docs/paper/discussion-outline.md`
  (D.9; gate register at the foot of the file)

## Changelog

### 2026-08-21 — Original publication

Written at the PI's request when the naming ruling was deferred to
prose time (Session 139): records the verified evidence table, the
four options as presented, the framing recommendation, the PI's
inputs to date, the pre-discussion reading list, and the open
questions, so the decision can be taken up after the Gould et al.
read without reconstruction.
