# Batch-vs-flex probe, 2026-09-19

Phase-gate validation before the Gemini 3 55-map verifier legs (arm 2 on the
Batch API, chunked). 200 candidates of the 3.7 K = 5 union (seed 42), whose
flex arm 2 probabilities are in `../verify_k5_arm2`, re-verified on batch in
four 50-candidate chunks (`gemini-3.7-flash`, `low`, T 0.0). Four jobs, all
SUCCEEDED, 200/200, usage booked from every response, audited US$0.2248
(US$0.001124/candidate).

| comparison | n | identical p | flips at 0.90 | abs dp > 0.5 |
|---|---:|---:|---:|---:|
| flex K5 vs flex K3 twin (same route, near-identical crop) | 171 | 61 % | 3.5 % | 5 |
| batch K5 vs flex K5 (same crop, route differs) | 171 | 60 % | 5.3 % | 6 |
| batch K5 vs flex K3 twin | 171 | 61 % | 4.1 % | 7 |

The twin baseline is the same verifier re-invoked on flex against the K = 3
union's crop of the same mound (matched within 5 m, median 0.57 m). The
batch route's drift is indistinguishable from the route's own re-invocation
drift (E89): no route effect. Verdict: PASS; the multi-chunk mechanics
(`run_pv.py --mode batch --max-batch-candidates`) proven on four jobs.
