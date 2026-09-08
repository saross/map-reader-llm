# April e47 1-of-5 verifier stage — first sweep, on its complete 4,358 probabilities (S151, 2026-09-08)

`outputs/h11/e47-propose-brief/verified/flash-high-text-1of5` (verified 2026-04-09,
`52b0215a6`; 57-crop gap closed 2026-05-06, `6683952ac`) was never swept. On the
PI's ruling ("yes", 2026-09-08) it was swept here with the stages' script
(`scripts/sweep_f1_greedy_pv.py`, buffers 20/30/40/50 m, `full_evaluation_bounds`)
on sapphire, $0. Its tracked crop manifest
(`outputs/h11/e47-propose-brief/crops/flash-high-text-1of5/candidate_manifest.json`)
records the vote count as `proposer_votes`, which the sweep script reads as
`vote_count`; `map_votes.py` (beside this file) made the temporary copy with
`vote_count := proposer_votes` — exact, since the cumulative counts
(4,358 / 1,654 / 1,072 / 753 / 487 at vote ≥ 1…5) equal the stage's derived
`2of5`–`5of5` subsets. The source manifest is untouched.

| stage | candidates | best F1 at 20 m (P / R; n kept) | operating point | best at 50 m |
| --- | ---: | --- | --- | ---: |
| April `verified/flash-high-text-1of5` (this sweep) | 4,358 | 0.7953 (0.745 / 0.853; 498) | vote ≥ 3, p ≥ 0.20 | 0.8189 |
| refreshed `verified/flash-high-text-1of5-recovery-2026-09-08` | 4,149 | 0.8735 (0.928 / 0.825; 387) | vote ≥ 4, p ≥ 0.15 | 0.9028 |

**Not a like-for-like.** The two candidate sets are different constructions,
not the same clustering before and after recovery: the April set has 209 more
vote ≥ 1 clusters and more at every vote tier (vote ≥ 2: 1,654 vs 1,537;
≥ 3: 1,072 vs 998; ≥ 4: 753 vs 699; ≥ 5: 487 vs 455) although it was built from
passes with FEWER detections (pre-recovery), and the audit
(`reports/recovery-consistency-audit-2026-09-08.md` § 2.3) had already found the
April e47 consensus irreproducible at any vintage (pre-D6 resolver; `run_5` then
held both filename conventions). The 0.078 gap at 20 m is almost all precision
(0.745 → 0.928) at a looser vote tier, which is what looser April vote counts
would produce; it cannot be attributed to the recovery. The refreshed stage is
the pool's only sweep on a reproducible candidate set.
