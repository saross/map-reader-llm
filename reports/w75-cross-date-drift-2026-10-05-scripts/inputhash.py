import hashlib
import json
from pathlib import Path

root = Path.home() / "Code/map-reader-llm"
tiles = json.load(open(root / "inputs/tiles_384/full_evaluation_manifest.json"))
idx = {p.name: p for p in (root / "inputs/tiles_384").rglob("*.png")}
h = hashlib.sha256()
for t in sorted(tiles):
    h.update(t.encode())
    h.update(idx[t].read_bytes())
cfg = json.load(open(root / "prompts/configs/library_plus-hp.json"))
e = hashlib.sha256()
for ex in cfg["examples"]:
    e.update(ex["label"].encode())
    e.update((root / "inputs/examples" / ex["path"]).read_bytes())
si = hashlib.sha256(
    (root / "prompts/system-instructions" / cfg["instruction_file"]).read_bytes()
).hexdigest()
cf = hashlib.sha256((root / "prompts/configs/library_plus-hp.json").read_bytes()).hexdigest()
print(
    "tiles",
    len(tiles),
    h.hexdigest()[:16],
    "examples",
    len(cfg["examples"]),
    e.hexdigest()[:16],
    "instr",
    si[:12],
    "config",
    cf[:12],
)
