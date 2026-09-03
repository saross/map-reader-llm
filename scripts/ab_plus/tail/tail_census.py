"""Promoted 2026-09-03 from the S147 scratch driver.

Census of the AB+ tail run from manifest + verdict JSONs (read-only).

Usage: python3 census.py
Prints: status counts, verdict distribution, per-point verdict tallies, edit
counts, summary word counts for rendered entries.
"""
import json
import os
import statistics
from collections import Counter
R='/home/shawn/Code/map-reader-llm'
M=f'{R}/outputs/ab-plus/manifests/tail-2026-09-02.json'
W=f'{R}/outputs/ab-plus/_work'
d=json.load(open(M))
rows=d['sources']
print('status:', dict(Counter(r['status'].split(':')[0] for r in rows)))
overall=Counter(); pp=Counter(); nedits=[]; unsupported=[]; words=[]; nkp=Counter(); hooks=0
for r in rows:
    k=r['citekey']
    vp=f'{W}/{k}.verdict.json'
    if os.path.exists(vp):
        v=json.load(open(vp)); overall[v.get('overall')]+=1
        for p in v.get('per_point',[]):
            pp[p.get('verdict')]+=1
            if p.get('verdict')=='UNSUPPORTED': unsupported.append((k,p.get('index'),(p.get('note') or '')[:120]))
        nedits.append(len(v.get('edits',[])))
    ep=f'{W}/{k}.entry.json'
    if os.path.exists(ep):
        e=json.load(open(ep)); words.append(len(e['summary'].split())); nkp[len(e['key_points'])]+=1; hooks+=bool(e.get('framing_hook'))
print('overall:', dict(overall)); print('per_point:', dict(pp))
print('edits per verdict: n=%d median=%s min=%d max=%d total=%d'%(len(nedits),statistics.median(nedits) if nedits else None,min(nedits,default=0),max(nedits,default=0),sum(nedits)))
print('summary words: n=%d median=%s min=%d max=%d'%(len(words),statistics.median(words) if words else None,min(words,default=0),max(words,default=0)))
print('key points per entry:', dict(sorted(nkp.items())), 'hooks:', hooks)
print('UNSUPPORTED points:'); [print('  ',u) for u in unsupported]
print('gate:', dict(Counter(r.get('gate','?').split(' ')[0] for r in rows)))
print('cluster:', dict(Counter(r.get('cluster','?') for r in rows)))
