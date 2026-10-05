# ruff: noqa  (kept verbatim as provenance of reports/phase2e-ordering-check-2026-10-05.md)
"""
Per-tile output agreement between retest runs (read-only on the repo's GeoJSONs).

For each pair of runs, over tiles processed by both:
  exact  = share of tiles whose detection set (rounded box coordinates, sorted) is identical
  count  = share of tiles with the same number of detections
  mad    = mean absolute difference in per-tile detection count
  presence = share of tiles agreeing on "any detection"
"""
import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path
R = Path('/home/shawn/Code/map-reader-llm/outputs/retest')
runs = {
    'E-config-default': 'phase2e/config-default/run_1/detections_config-default_run01.geojson',
    'E-canonical-first': 'phase2e/canonical-first/run_1/detections_canonical-first_run01.geojson',
    'E-canonical-last': 'phase2e/canonical-last/run_1/detections_canonical-last_run01.geojson',
    'E-random': 'phase2e/random/run_1/detections_random_run01.geojson',
    'C-plus-hp': 'phase2c/track1-image/plus-hp/run_1/detections_plus-hp_run01.geojson',
    'B-T0.0-r1': 'phase2b/track1-image/T0.0/run_1/detections_T0.0_run01.geojson',
    'B-T0.0-r2': 'phase2b/track1-image/T0.0/run_2/detections_T0.0_run02.geojson',
    'B-T0.0-r3': 'phase2b/track1-image/T0.0/run_3/detections_T0.0_run03.geojson',
    'C-scale-8': 'phase2c/track1-image/scale-8/run_1/detections_scale-8_run01.geojson',
    'C-ppc': 'phase2c/track1-image/pure-positive-canon/run_1/detections_pure-positive-canon_run01.geojson',
    'X-ppc': 'phase2c/track1-image-exploratory/pure-positive-canon/run_1/detections_pure-positive-canon_run01.geojson',
    'C-scale-4': 'phase2c/track1-image/scale-4/run_1/detections_scale-4_run01.geojson',
    'C-canonical': 'phase2c/track1-image/canonical/run_1/detections_canonical_run01.geojson',
}
data = {}
for name, rel in runs.items():
    g = json.load(open(R / rel))
    per = defaultdict(list)
    for f in g['features']:
        xs = [round(c[0], 1) for c in f['geometry']['coordinates'][0]]
        ys = [round(c[1], 1) for c in f['geometry']['coordinates'][0]]
        per[f['properties']['source_tile']].append((min(xs), min(ys), max(xs), max(ys), f['properties'].get('subtype')))
    tiles = set(g['processed_tiles'])
    data[name] = (tiles, {t: tuple(sorted(per.get(t, []))) for t in tiles}, len(g['features']))

def compare(a, b):
    ta, da, _ = data[a]; tb, db, _ = data[b]
    common = sorted(ta & tb)
    n = len(common)
    exact = sum(da[t] == db[t] for t in common) / n
    cnt = sum(len(da[t]) == len(db[t]) for t in common) / n
    mad = sum(abs(len(da[t]) - len(db[t])) for t in common) / n
    pres = sum((len(da[t]) > 0) == (len(db[t]) > 0) for t in common) / n
    # detection-level: share of boxes in a that appear exactly in b on the same tile
    tot = sum(len(da[t]) for t in common) + sum(len(db[t]) for t in common)
    shared = sum(2 * len(set(da[t]) & set(db[t])) for t in common)
    return dict(n=n, exact=exact, count=cnt, mad=mad, presence=pres, box_overlap=shared / tot)

groups = {
    'ordering arms (Phase 2e, 6 pairs)': list(itertools.combinations(['E-config-default', 'E-canonical-first', 'E-canonical-last', 'E-random'], 2)),
    'replicates: 2b T0.0 x3 + 2c scale-8 (17 ex, canonical-first under code; 6 pairs)': list(itertools.combinations(['B-T0.0-r1', 'B-T0.0-r2', 'B-T0.0-r3', 'C-scale-8'], 2)),
    'replicates: 2c ppc vs exploratory ppc (7 ex; 1 pair)': [('C-ppc', 'X-ppc')],
    'C-plus-hp (2c, fixed canonical-first) vs each 2e arm': [('C-plus-hp', e) for e in ['E-canonical-first', 'E-config-default', 'E-canonical-last', 'E-random']],
    'different libraries, same order rule (2c image, for scale)': [('C-plus-hp', 'C-scale-4'), ('C-plus-hp', 'C-canonical'), ('C-plus-hp', 'C-scale-8'), ('C-scale-4', 'C-canonical')],
}
out = {}
print('detections:', {k: v[2] for k, v in data.items()})
for gname, pairs in groups.items():
    print('\n##', gname)
    for a, b in pairs:
        r = compare(a, b); out[f'{a}|{b}'] = r
        print(f"  {a:18s} vs {b:18s} n={r['n']} exact-tile={r['exact']:.3f} same-count={r['count']:.3f} "
              f"MAD={r['mad']:.3f} presence={r['presence']:.3f} box-overlap={r['box_overlap']:.3f}")
json.dump(out, open(sys.argv[1], 'w'), indent=1)
