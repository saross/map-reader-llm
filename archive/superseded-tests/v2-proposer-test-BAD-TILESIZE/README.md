# v2-proposer-test-BAD-TILESIZE (archived 2026-05-31)

A zbook-only paid Gemini run (proposer `647fc5b9`, verifier `3686d01e`,
2026-04-08): a complete `propose_brief_v2` proposer + `adversarial-text-v2`
verifier pair on the **standard 487-tile `tiles_384` set** (384 px, T=1.0).

**The "-BAD-TILESIZE" suffix is misleading** — a contemporaneous self-annotation
NOT corroborated by metadata. Every sizing parameter (`tiles_384`, 150×150 crops,
10,876 image-tokens/tile, identical 487-tile set) matches the kept
`archive/superseded-tests/v2-proposer-test/`; the only difference is a stochastic
detection count (721 vs 693 ≈ 4 % T=1.0 run-to-run noise). It is therefore a
**stochastic replicate**, not a distinct tile-size condition.

Retained (per the "preserve API-run outputs" / "archive, never delete" policy) as
(a) an independent T=1.0 replicate — a proposer-variance data point at this exact
configuration — and (b) a v2-verifier-family artefact (cf. Obs 273 quarantine,
commit `3ec25e68`). **Not for analytical use as a distinct tile-size condition.**

The 721 crop PNGs (regeneratable via `extract_candidates.py`, no API) were NOT
archived. Investigated by a dedicated agent (2026-05-31) before archival.
