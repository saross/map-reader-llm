"""Promoted 2026-09-03 from the S147 scratch driver.

Census of the overflow structuring batch (read-only).

Usage: python3 ocensus.py — prints manifest status counts, sidecar item
statistics, and checks every rendered tail entry for an Overflow section.
"""
import json
import os
import statistics
import re
from collections import Counter
R='/home/shawn/Code/map-reader-llm'
m=json.load(open(f'{R}/outputs/ab-plus/manifests/overflow-2026-09-03.json'))
rows=m['sources']
print('status:', dict(Counter(r['status'] for r in rows)))
n_items=[]; missing=[]; noapp=[]; withheld=0
for r in rows:
    k=r['citekey']; p=f'{R}/outputs/ab-plus/_work/{k}.overflow.json'
    if not os.path.exists(p): missing.append(k); continue
    o=json.load(open(p)); n_items.append(len(o['items']))
    md=f'{R}/outputs/ab-plus/{k.lower()}.md'
    t=open(md).read() if os.path.exists(md) else ''
    if '## Overflow' not in t: noapp.append(k)
    mm=re.search(r'Overflow span check: \*\*(\d+)/(\d+) passed', t)
    if mm and mm.group(1)!=mm.group(2): withheld+=int(mm.group(2))-int(mm.group(1))
print('sidecars:',len(n_items),'items total:',sum(n_items),'median:',statistics.median(n_items) if n_items else None,'min:',min(n_items,default=0),'max:',max(n_items,default=0),'at cap (12):',sum(1 for x in n_items if x==12))
print('missing sidecar:',missing); print('rendered without Overflow section:',noapp); print('withheld items across corpus:',withheld)
