"""Copy the April e47 1of5 crop manifest with vote_count filled from proposer_votes (exact: cumulative counts 4358/1654/1072/753/487)."""
import json
from pathlib import Path
src = Path('outputs/h11/e47-propose-brief/crops/flash-high-text-1of5/candidate_manifest.json')
m = json.loads(src.read_text())
cands = m['candidates']
items = cands if isinstance(cands, list) else list(cands.values())
for c in items:
    p = c.setdefault('properties', {})
    p['vote_count'] = p['proposer_votes']
out = Path('/tmp/resweeps-s151/e47-april-crops'); out.mkdir(parents=True, exist_ok=True)
m['_note'] = 'S151 temporary copy: vote_count := proposer_votes for sweep_f1_greedy_pv.py; source manifest untouched'
(out / 'candidate_manifest.json').write_text(json.dumps(m))
print('mapped', len(items), 'candidates')
