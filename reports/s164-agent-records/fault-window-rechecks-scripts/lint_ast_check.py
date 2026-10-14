#!/usr/bin/env python3
"""Show that a lint pass changed formatting only (fault-window re-checks, S164).

The comparison drivers in this directory were linted with ``ruff`` AFTER they
had produced the committed comparisons (long lines wrapped, one-line
``a; b`` statements split). This script proves those edits are behaviour
preserving: for each pair (pre-lint copy, linted file) it parses both,
removes module, class, and function docstrings, and compares
``ast.dump`` of the two trees. Equal dumps mean the same program.

Usage::

    python lint_ast_check.py <pre-lint dir> <linted dir> <relative path> ...

Exits 0 when every pair is equal.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path


def strip_docstrings(tree: ast.AST) -> ast.AST:
    """Remove the leading docstring expression from every docstring-bearing node."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = node.body
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                node.body = body[1:] or [ast.Pass()]
    return tree


def dump(path: Path) -> str:
    """Return the docstring-free AST dump of ``path``."""
    return ast.dump(strip_docstrings(ast.parse(path.read_text())))


def main() -> int:
    """Compare each named pair and report."""
    old_root, new_root = Path(sys.argv[1]), Path(sys.argv[2])
    bad = 0
    for rel in sys.argv[3:]:
        same = dump(old_root / rel) == dump(new_root / rel)
        bad += not same
        print(f"{rel}: {'AST-EQUAL' if same else 'AST-DIFFERS'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
