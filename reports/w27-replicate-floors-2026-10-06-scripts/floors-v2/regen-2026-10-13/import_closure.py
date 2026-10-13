"""Transitive closure of project-local imports for given entry scripts (static, AST-based).

Usage: python import_closure.py <repo> <entry.py> [...]
Resolves `import X` / `from X import Y` against <repo>/X.py, <repo>/scripts/X.py, the entry's
own directory, and dotted package paths; prints every project file reached.
"""
import ast
import sys
from pathlib import Path

repo = Path(sys.argv[1]).resolve()
todo = [Path(p).resolve() for p in sys.argv[2:]]
seen: set[Path] = set()


def resolve(mod: str, here: Path) -> list[Path]:
    parts = mod.split(".")
    cands = []
    for base in (repo, here.parent, repo / "scripts"):
        p = base.joinpath(*parts)
        cands += [p.with_suffix(".py"), p / "__init__.py"]
    return [c for c in cands if c.is_file()]


while todo:
    f = todo.pop()
    if f in seen:
        continue
    seen.add(f)
    tree = ast.parse(f.read_text())
    for node in ast.walk(tree):
        mods = []
        if isinstance(node, ast.Import):
            mods = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            mods = [node.module] + [f"{node.module}.{a.name}" for a in node.names]
        elif isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "import_module":
            if node.args and isinstance(node.args[0], ast.Constant):
                mods = [node.args[0].value]
        for m in mods:
            for p in resolve(m, f):
                if p not in seen:
                    todo.append(p)
for p in sorted(seen):
    print(p.relative_to(repo))
