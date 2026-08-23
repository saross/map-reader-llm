# Superseded: the mislabelled "IM-k4" cell (Session 138)

These three evaluation siblings were minted on 2026-08-21 as the
"Track-3 IM-k4 gap cell" but score the WRONG detection set: the image
run's production consensus is 3-of-5
(`outputs/55maps-image-generalisation/consensus/consensus-3of5.geojson`;
`resolved_config.yaml` `vote_threshold: 3`), so
`verified/verified_detections.geojson` — the file these evaluations
consumed — is the k3 set already registered as
`55maps-image-generalisation::verified-k3-standardised-gt`. The
identical headline values (n_det 4,680, F1@50 0.801, MCC 0.712 =
IM-k3's rounded values) betray the duplication. Discovered during
E82 Item D (Session 140, 2026-08-23) by the feature-count
cross-check; never registered as a condition.

The genuine IM-k4 (4-of-5 re-vote of the same verified pool, 3,541
detections) replaces it at
`results/55maps-standardised-ref-2026-08-14/IM-k4/` — see
`scripts/derive_im_k4_verified.py` and the E82 contract changelog
(PI ruling 2026-08-23).
