# Planning stub — LLM-assisted preregistration: a methods paper

> **Status**: PI-prioritised 2026-09-03 (Session 147 follow-up), on the
> strength of the AB+ tail's automation-cell finding. A stub, not a
> plan: it records the claim, the evidence base, the pitfalls, and the
> ties to prior work so the paper can be scoped after the ISPRS
> manuscript is out. See [§ Changelog](#changelog).

## The claim to stake

Across the 30 preregistration and open-science sources verified in the
AB+ corpus (`outputs/ab-plus/`, tail report
`reports/ab-plus-tail-report-2026-09-02.md`), nothing implements or
evaluates a large language model (LLM) that authors or checks a
preregistration. The nearest neighbours are proposals: Pu et al. 2019
(a "declaration of match … could even be partially or fully
automated"); Thomas et al. 2026 §6 (autonomous AI-scientist systems
should commit to procedure and eligible-model set before the
confirmatory model exists). The ISPRS paper stakes the territory in
its Methods (§ M.12 slot) and Discussion (D.9); this paper works it.

## What it would report

1. **The practice**: how an LLM in the loop authored, revised, and
   checked a registration and its errata log, classified analysis
   register, and hypothesis-outcome table across ~150 sessions, with
   the human ruling on every registered commitment. Archive-backed:
   session transcripts (`~/cc-archives/`, both project names) and the
   repository history are the primary data.
2. **The problems it solves**: composition friction (the cost Sarafoglou
   2022 measures — "better science but more work"); the checking gap Pu
   2019 documents (registrations "verge on being write-only media"; only
   authors check thoroughly); contemporaneous deviation logging where
   Ofosu 2023 finds 1 of 14 deviations disclosed; the timing/reason axes
   Willroth 2024's schema asks for and most registers lack.
3. **The pitfalls**, each with a receipt from this project:
   - **Over-specification** — the over-bake with receipts (Seed 7): an
     LLM lowers the marginal cost of a registered clause to near zero,
     so the register grows past what the study can honour; grain, not
     volume, is the diagnosis. The PI's own priority.
   - **Self-flattering drift** — a model drafting toward a thesis drifts
     toward it in small, systematic, quote-accurate steps (claude-obs
     86; the AB+ verifier layer caught it in every entry). A registration
     drafted by the same model that will interpret the results inherits
     the drift unless an independent reader checks it.
   - **The self-report objection** — Thomas 2026 dismisses checklist
     assistance because it "relies solely on self-report"; the answer is
     machine-checked layers (errata file, classified register, generated
     outcome table), not more prose.
   - **Unprotected commitments** — a registration written against models
     that already exist is the commitment Thomas 2026 argues is
     unprotected; the "preregister for the next model" device is the
     comparison case.
   - **Registry mismatch** — registries host static preregistrations,
     not updatable living documents (Gerasimova 2024), which pushes the
     mutable logs into the repository and off the registry's timestamp.

## Ties to prior work by the PI

- Ross & Ballsun-Stanton 2022 (`outputs/ab-plus/ross_introducing_2022.md`):
  the discipline-facing case for preregistration in archaeology, the
  four-of-304,904 OSF baseline (keyword search, 19 March 2020), the
  data-model and data-workflow registrable objects, the best-effort
  standard conditioned on an abductive discipline. This paper is the
  executed sequel: the chapter issued the call and placed writing a
  protocol beyond its scope.
- The ISPRS paper's registration apparatus and retrospective (D.9).

## Evidence base (AB+ entries, page-anchored)

Srivastava 2018; Nosek 2018, 2019; Pu 2019; Crüwell 2021; van den Akker
2021; van Miltenburg 2021; Willroth 2022, 2024; Ioannidis 2022; Lakens
2024; Ofosu 2023; Sarafoglou 2022, 2023; Gerasimova 2024; Gould 2026;
Thomas 2026; Vaccaro 2026; Strobl 2026; MacCoun 2015; Dwork 2015;
Fafchamps 2017; Lin 2016; Gamble 2017; Hekler 2016; Liu 2020; Chambers
2021; Ross 2022. Each has a verified entry under `outputs/ab-plus/`.

## Open questions for scoping

- Venue and register: meta-science (e.g. the journals the cluster
  publishes in) versus a digital-archaeology methods venue.
- Whether to run a small prospective test of the practice on a new
  registration (the GT-free protocol's registration is the candidate).
- How much of the session archive to publish as supplementary evidence,
  and under what redaction.

## Changelog

### 2026-09-03 — Original publication

Stub written at the PI's direction after the AB+ tail report.
