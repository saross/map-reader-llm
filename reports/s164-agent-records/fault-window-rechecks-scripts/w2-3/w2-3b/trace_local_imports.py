#!/usr/bin/env python3
"""List the repository modules a driver script imports, transitively.

Fault-window re-check W2-3, part B (sub-agent w2-3b), 2026-10-15. Run from a
replay tree's root; it walks ``scripts/<name>.py`` imports (both
``scripts.x`` and bare ``x`` forms) so the hard-coded-path grep can be
limited to the modules a replay actually loads.

Usage: python trace_local_imports.py <module> [<module> ...]
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path("scripts")


def local_imports(path: Path) -> set[str]:
    """Return the repository modules imported by one file."""
    found: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text())):
        names: list[str] = []
        if isinstance(node, ast.ImportFrom) and node.module:
            names = [node.module]
        elif isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        for name in names:
            if name.startswith("scripts."):
                found.add(name.split(".", 1)[1])
            elif (ROOT / f"{name}.py").exists():
                found.add(name)
    return found


def walk(module: str, seen: set[str]) -> None:
    """Depth-first walk of the import graph from ``module``."""
    if module in seen:
        return
    seen.add(module)
    path = ROOT / f"{module}.py"
    if path.exists():
        for child in local_imports(path):
            walk(child, seen)


def main() -> None:
    """Print the sorted transitive closure for the named modules."""
    seen: set[str] = set()
    for module in sys.argv[1:]:
        walk(module, seen)
    print(sorted(seen))


if __name__ == "__main__":
    main()
