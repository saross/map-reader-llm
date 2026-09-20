# PI decision log — Session 156 (2026-09-19/20)

One entry per decision the PI is asked to make, with the bottom line the
terminal scrolled past. Status moves to **RULED** with the ruling text and
the commit that executed it. Read top to bottom; open items first.

## Open

### D8 — Measure the E89 floor for the Gemini 3 verifier (row B arm 1)

- **Need**: a second, independent invocation of `gemini-3-flash-preview` (minimal, T 0) over a union it has already verified. Cheapest clean pair: replicate row A's arm 1 K = 5 leg (`verify_k5_arm1`, 9,173 candidates, audited US$6.49 on flex) on the Batch API — same union as the arm 2 floor's replicate, so both verifiers' floors sit on one candidate set. Row B's own arm 1 K = 5 leg would cost ≈ US$31.5.
- **Decide**: approve ≈ US$6.5 (9,173 calls, batch, `gemini-3-flash-preview`)?

### D6 — Board follow-ups

- Register the 17 addendum cells in `results/run-conditions.json`? (precedent: FOURTH-N5-oracle was registered separately.)
- How to present MCC oracles: on all 23 families the tile-MCC argmax sits at the lowest vote count on offer, paying 0.06–0.18 of F1 where k = 1 is available; an MCC oracle is a vote-threshold choice wearing a metric's name, not a like-for-like companion of the F1 oracle. Option with no compute: an MCC-argmax over prob_t at the family's CARRIED k, readable from the committed CSVs.

### D7 — Legacy vote-count divergence (June-grid note § 7, f859646ba)

- **Cause**: the 2026-05-03 recovery re-merged the consensus and re-cut crops with an incremental extractor that never refreshes matched entries' properties; five April/May 2026 manifests carry votes one low on 15–110 candidates each. The current chain (both image rows, all six rungs) has zero disagreements.
- **Decide**: (a) rebuild `IM-k4` on the consensus votes (+3 detections, F1 0.7398 → 0.7402; $0, a board cell); (b) the one never-verified 4-vote candidate in `55maps-text-high-generalisation` (two clusters 17.29 m apart matched to one manifest entry) — verify it (one call) or minute it.

## Ruled

### D5 — Audit items — RULED 2026-09-20: all four as recommended — M2 both halves (default `--iterations` from the leg AND refuse an all-miss leg), M4/m10 (margin = one maximum chunk; PROCESSING uploads charged at that size), m7 (non-SUCCEEDED terminal states count as failed chunks, partial results kept), and the proposer/verifier cost auditors read the model from the meta and refuse to price without one. Implementation in progress

### D2 — Verifier-ladder method — RULED 2026-09-20: INHERITANCE is the project's ladder method (one verifier leg over the top-rung union, lower rungs by ≤ 10 m match); the image rows' per-rung legs were a departure. Head-to-head DONE on the 3.7 image row (62b13e6fd…557b4e881; `results/gemini37-image-55map-2026-09-13/inheritance-2026-09-20/`): inherited vs own-leg differs by 0.0002–0.0021 F1 and 0.0005–0.0027 tile-MCC, all p ≥ 0.07, signs mixed — no more than the verifier disagrees with itself; the dropped-candidate precision bias is undetectable (drops 50 of 6,985 at K = 1, 2 of 8,337 at K = 3). Inheritance is SAFE to adopt on this evidence. Bonus: the pure-inheritance K3→K5 tile-MCC contrast is readable (+0.0039, p 0.006) where own-leg pairing left it in the drift band. Gemini 3 row DONE (2ba1914b6…b1408b0ed; `results/gemini3-image-55map-2026-09-16/inheritance-2026-09-20/`): at K = 3 no difference beyond drift (row A reproduced); at K = 1 the dropped-candidate precision bias IS real and claimable on F1 (inherited cells smaller and more precise by +0.006/+0.009 F1, 3.0/5.9 null SDs, both arms; drops 566 of 22,785 = 2.5 %), null on tile-MCC. Density does not create matching ambiguity (0 exact ties; the 20 m dedup radius, twice the 10 m match radius, is the invariant to keep). RULES THAT FOLLOW: inheritance stays the method; an inherited K = 1 cell must not be read beside an own-leg K = 1 cell; K1→K3 claims must name the method; any pool unioned at a dedup radius ≤ 10 m must re-measure

### D1 — Rows A and B — RULED 2026-09-20: row A signed as drafted 2026-09-13, scope limited to the K = 1/K = 3 rungs, later rungs get a new row (93c935d91); row B signed as drafted with its outcome authored at signing (f749fe9a1). Tally 44 signed, 25 unsigned, 1 by design

### D3 — T5 matched comparator — RULED 2026-09-20: T5m added as an additional test (3783e0e03; instrument d985a5e51, cells 2bd86154e, tests c9abda52e). Result: micro-F1 REVERSES (−0.0696, p < 0.0001) — the declared T5's F1 null cannot be read as reproduction; tile-MCC consistent-sign small positive (+0.0125 to +0.0237, uncorrected)

### D4 — E89 floor — RULED 2026-09-20: revised in the declaration § 5 caveat 1 (73a4f09df): 2.46 % flips, Wilson [2.17 %, 2.80 %]; drift-only +0.0008 F1 / −0.0005 MCC; rule = claimable only if the effect clearly exceeds the drift contrast; T3's tile-MCC null now read as uninformative; no measured floor for the Gemini 3 verifier

### D6a — MCC sweep of the remaining 13 families — RULED 2026-09-20: done (03b8496ed; 2,048 points, all 23 families carry mcc_argmax; no cells materialised). Finding: every one of the 23 families puts its tile-MCC argmax at the LOWEST vote count its sweep offers (13 of 13 that offered k = 1 collapsed to it; the five incumbents sit at their k = 3 floor); F1 lost 0.06–0.18 where the collapse is possible

### K3→K5 F1 gain — CONFIRMED claimable by the PI 2026-09-20 (replicate: +0.0079 vs drift-only +0.0008; `results/gemini37-image-55map-2026-09-13/replicate-k5-arm2-batch-2026-09-20/`)
