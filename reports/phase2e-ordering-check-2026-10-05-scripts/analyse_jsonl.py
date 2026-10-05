# ruff: noqa  (kept verbatim as provenance of reports/phase2e-ordering-check-2026-10-05.md)
"""Decode the replayed Phase 2e request JSONLs: example order, body hashes, invariants."""
import base64, hashlib, json, sys
from pathlib import Path
root = Path(sys.argv[1])
ex_dir = root / 'inputs/examples/neutral-naming'
# Map image SHA-256 -> example name (resolve symlinks to bytes)
sha2name = {}
for p in sorted(ex_dir.glob('example_*.png')):
    sha2name[hashlib.sha256(p.read_bytes()).hexdigest()] = p.stem.replace('example_', 'ex')
cfg = json.loads((root / 'prompts/configs/library_plus-hp.json').read_text())
cat = {Path(e['path']).stem.replace('example_', 'ex'): e['category'] for e in cfg['examples']}
abbrev = {'canonical_positive': 'C+', 'canonical_negative': 'C-', 'hard_positive': 'HP', 'null': 'null'}
arms = ['config-default', 'canonical-first', 'canonical-last', 'random']
summary = {}
for arm in arms:
    f = root / f'outputs/retest/phase2e/{arm}/run_1/batch_working/detections_{arm}_run01.jsonl'
    lines = [json.loads(l) for l in f.read_text().splitlines()]
    seqs, ref_hashes, gen, sysi = [], set(), set(), set()
    for ln in lines:
        parts = ln['request']['contents'][0]['parts']
        # parts: preamble, (label, image)*, transition, tile
        ref = parts[1:-2]
        seq = []
        for i in range(0, len(ref), 2):
            lab = ref[i]['text']; img = ref[i + 1]['inline_data']['data']
            h = hashlib.sha256(base64.b64decode(img)).hexdigest()
            seq.append((sha2name.get(h, '??' + h[:8]), lab))
        seqs.append(tuple(seq))
        ref_hashes.add(hashlib.sha256(json.dumps(parts[:-1]).encode()).hexdigest())
        gen.add(json.dumps(ln['request']['generation_config'], sort_keys=True))
        sysi.add(hashlib.sha256(ln['request']['system_instruction']['parts'][0]['text'].encode()).hexdigest()[:10])
    assert len(set(seqs)) == 1, f'{arm}: example sequence varies across lines'
    seq = seqs[0]
    summary[arm] = dict(n_lines=len(lines), n_examples=len(seq), ref_block_sha=list(ref_hashes)[0][:16],
                        n_distinct_ref_blocks=len(ref_hashes), gen=list(gen), sys=list(sysi),
                        order=[s[0] for s in seq], cats=[abbrev[cat[s[0]]] for s in seq],
                        labels=[s[1] for s in seq], keys=[l['key'] for l in lines])
for arm, s in summary.items():
    print(f"== {arm}: {s['n_lines']} lines, {s['n_examples']} examples, prefix-block sha {s['ref_block_sha']} "
          f"(distinct across lines: {s['n_distinct_ref_blocks']}), system {s['sys']}")
    print('   order :', ' '.join(s['order']))
    print('   cats  :', ' '.join(s['cats']))
    print('   labels:', ' '.join(x[0] for x in s['labels']))
print('generation_config identical across arms:', len({json.dumps(s['gen']) for s in summary.values()}) == 1, summary['config-default']['gen'])
print('system instruction identical across arms:', len({json.dumps(s['sys']) for s in summary.values()}) == 1)
print('tile keys identical across arms:', len({json.dumps(s['keys']) for s in summary.values()}) == 1)
print('same multiset of examples in every arm:', len({tuple(sorted(s['order'])) for s in summary.values()}) == 1)
print('distinct prefix blocks across the four arms:', len({s['ref_block_sha'] for s in summary.values()}))
json.dump(summary, open(root.parent / 'replay-summary.json', 'w'), indent=1)
