# Archived: the 2026-08-29 twin evaluation that scored F1 = 0 (CRS-less projected input)

The pairing twin for `55maps-generalisation::verified-paired` was scored on
2026-08-29 (`5bd514542`) straight from the committed
`outputs/55maps-generalisation/consensus/consensus-4of5.geojson`, which carries
projected EPSG:32635 coordinates and no `crs` member. RFC 7946 readers treat a
CRS-less GeoJSON as WGS84, so every point landed in the wrong place and the
evaluation read F1 = 0 at every buffer, which surfaced in the uplift table as an
"uplift" of 0.7921. Re-scored on 2026-09-09 from a copy with the CRS declared
(`scripts/materialise_pairing_twin.py --consensus … --declare-crs EPSG:32635`;
the pairing builder now routes projected CRS-less twins through it). This
directory preserves the artefact (archive, never delete).
