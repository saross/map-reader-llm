# PI decision log — Session 156 (2026-09-19/20)

One entry per decision the PI is asked to make, with the bottom line the
terminal scrolled past. Status moves to **RULED** with the ruling text and
the commit that executed it. Read top to bottom; open items first.

## Open

### D1 — Sign rows A and B in the analyses register

- **Where**: `results/run-analyses.json`, analyses 68 (`gemini37-image-55map-2026-09-13`, row A) and 69 (`gemini3-image-55map-2026-09-16`, row B). Fields per row: `signature.status` ("unsigned" → "signed"), `signature.signed_at`, `signature.attests` (what is approved and what is not), `signature.presentation`, `manually_verified_at`; row B also `outcome` (null until the PI adjudicates the K = 3 primary reading).
- **Afterwards**: `scripts/generate_post_run_report.py --all --write` copies the signature into `results/analyses-manifest.json`.
- **Bottom line**: row A's outcome text was authored on 2026-09-13 and left unsigned by the card; it predates the K = 5 rung, the 2x2, and today's replicate. Row B's outcome is deliberately blank.

### D2 — Verifier-ladder method for the benchmark and cross-model comparisons

- **Options**: (i) inheritance — one verifier leg over the top-rung union, lower rungs derived by ≤ 10 m match (the text track's method; rung contrasts free of re-invocation drift; one leg's cost; drops unmatched candidates, 0.6–2.6 %, biasing lower-rung precision upward by an unmeasured amount; lower rungs are not deployments). (ii) Own leg per rung (the image rows' method; deployment-faithful; ~2.7× the cost for three rungs; rung contrasts below the drift band untestable without a replicate).
- **Recommendation**: inheritance for the benchmark; first derive the image rows' K = 1/K = 3 from their K = 5 legs at $0 to MEASURE the inheritance bias against the own-leg cells that already exist; keep own-leg cells as replicates. Cross-model comparisons at the same rung are unaffected by the choice as long as it is one method.

### D5 — Audit items still open (`reports/code-audit-2026-09-20-storage-preflight.md` § 6)

- **M2**: `batch-recover --iterations` defaults to 1; recovering a multi-iteration leg without it writes an empty `probabilities.json` beside a stale `consensus.json`. Options: default from the leg's own `probabilities.json` `iterations` (recommended) / refuse to book an all-miss leg.
- **M4 + m10**: the 5 % storage margin is 1 GiB, smaller than one proposer chunk (~1.3 GB); PROCESSING uploads report no size and count as zero. Options: margin = one maximum chunk and charge PROCESSING uploads at that size (recommended) / keep 5 %.
- **m7**: a FAILED/CANCELLED/EXPIRED/PARTIALLY_SUCCEEDED batch job is retrieved like a success and not counted in `failed_chunks`; completeness gates still catch missing keys. Option: count non-SUCCEEDED terminal states as failed while keeping partial results.
- **New (registration agent)**: `scripts/audit_proposer_cost.py` never reads the model from the run meta; its 3.7 default prices a Gemini 3 pool 48 % high unless `--model` is passed. Option: read the model from the meta and refuse to price without one.

### D6 — Board follow-ups

- Register the 17 addendum cells in `results/run-conditions.json`? (precedent: FOURTH-N5-oracle was registered separately.)
- How to present MCC oracles: on every family with a choice of k the tile-MCC argmax sits at k = 1 and pays 0.06–0.18 of F1; an MCC oracle is not a like-for-like companion of the F1 oracle.

## Ruled

### D3 — T5 matched comparator — RULED 2026-09-20: add T5m as an ADDITIONAL test at K = 3 (G3 K = 5 pool at 3 votes vs IM-k3), keep the declared T5. In progress.

### D4 — E89 floor — RULED 2026-09-20: revise to the full-scale measurement (2.46 % flips at 0.90 on 9,173 candidates; drift-only contrasts +0.0008 F1 / −0.0005 MCC). In progress.

### D6a — MCC sweep of the remaining 13 families — RULED 2026-09-20: yes. In progress.

### K3→K5 F1 gain — CONFIRMED claimable by the PI 2026-09-20 (replicate: +0.0079 vs drift-only +0.0008; `results/gemini37-image-55map-2026-09-13/replicate-k5-arm2-batch-2026-09-20/`)
