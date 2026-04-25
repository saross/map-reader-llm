# Cross-architecture paired comparison — Era 1, F1

**Generated**: Session 79 redesign (2026-04-25)
**Era**: 1
**Metric**: F1
**Permutations**: 10,000, seed=42
**FDR**: BH at q=0.05 within Era

Pairs of architectures sharing the same proposer config tuple (model, config_version, instruction_file, thinking, T, N/K, track, vote_t). The PV-helps column flags when adding the verifier (or moving from single-pass to consensus, etc.) produces a statistically significant change after BH-FDR.

Conditions tested: 0

| Pair (arch_a -> arch_b) | A | F1(A) | B | F1(B) | delta | p_raw | p_BH | sig (q=0.05) |
|:---|:---|---:|:---|---:|---:|---:|---:|:---:|

