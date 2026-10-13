#!/usr/bin/env python3
"""
Script-level hash-seed replay (ruling D63).

Runs one analysis script, from a disposable ``git archive`` copy of a given
git ref, under several ``PYTHONHASHSEED`` values, and saves the files it
writes after each run so that they can be compared across seeds (does the
output vary?) and across refs (before -> after the fix). The copy is built
under ``--work`` and never inside a checkout, so committed outputs are not
touched.

Usage::

    python script_replay.py --name sd-v1 --ref origin/main \\
        --archive scripts config.py results/secondary-effects \\
        --copy-from ~/Code/map-reader-llm --copy outputs/some/input \\
        --cmd "python scripts/analyse_consensus_sd_shrinkage.py" \\
        --output results/secondary-effects-consensus-sd/sd_shrinkage.json \\
        --seeds 0 1 2 3 --work /tmp/d63-runs

``--copy`` paths are gitignored inputs copied (``cp -a``, never symlinked)
from ``--copy-from``, read-only. Each run's outputs land in
``<work>/<name>/<ref-slug>/seed-<N>/``, and a ``digests.json`` beside them
records each output's SHA-256 after volatile keys (timestamps, git heads,
absolute paths) are dropped from JSON outputs; the dropped keys are listed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

# JSON keys whose values legitimately differ between two runs of the same
# code on the same inputs (when or where it ran), so they are dropped before
# comparison and listed in the record.
VOLATILE_KEY = re.compile(
    r"(generated|timestamp|run_at|created|_at$|^date$|git_head|git_commit|"
    r"source_commit|commit$|elapsed|duration|runtime|wall|hostname|python_executable)",
    re.IGNORECASE,
)

ISO_TS = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(\.\d+)?(\+00:00|Z)?")


def _strip(obj: Any, dropped: set[str]) -> Any:
    """Drop volatile keys from a JSON value, recording which were dropped."""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if VOLATILE_KEY.search(str(k)):
                dropped.add(str(k))
                continue
            out[k] = _strip(v, dropped)
        return out
    if isinstance(obj, list):
        return [_strip(v, dropped) for v in obj]
    return obj


def digest(path: Path) -> tuple[str, list[str]]:
    """SHA-256 of a file; for JSON, of its canonical form without volatile keys."""
    if path.suffix == ".json":
        try:
            dropped: set[str] = set()
            data = _strip(json.loads(path.read_text()), dropped)
            text = json.dumps(data, sort_keys=False)
            return hashlib.sha256(text.encode()).hexdigest(), sorted(dropped)
        except json.JSONDecodeError:
            pass
    if path.suffix in (".md", ".txt", ".csv"):
        # ISO-8601 timestamps (e.g. a "Generated:" line) are run-time, not data.
        text = ISO_TS.sub("<timestamp>", path.read_text())
        return hashlib.sha256(text.encode()).hexdigest(), ["<iso-timestamps in text>"]
    return hashlib.sha256(path.read_bytes()).hexdigest(), []


def build_copy(repo: Path, ref: str, archive: list[str], dest: Path,
               copy_from: Path | None, copies: list[str]) -> None:
    """Materialise ``ref``'s ``archive`` paths (plus copied inputs) at ``dest``."""
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    tar = subprocess.run(["git", "-C", str(repo), "archive", ref, *archive],
                         check=True, capture_output=True).stdout
    subprocess.run(["tar", "-x", "-C", str(dest)], input=tar, check=True)
    for rel in copies:
        src = (copy_from or repo) / rel
        tgt = dest / rel
        tgt.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["cp", "-rL", "--preserve=mode,timestamps", str(src), str(tgt.parent) + "/"],
                       check=True)


def main() -> int:
    """Build the copy, run the command under each hash seed, record digests."""
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    p.add_argument("--name", required=True)
    p.add_argument("--repo", type=Path, default=Path.cwd())
    p.add_argument("--ref", required=True)
    p.add_argument("--archive", nargs="+", required=True)
    p.add_argument("--copy-from", type=Path)
    p.add_argument("--copy", nargs="*", default=[])
    p.add_argument("--cmd", required=True)
    p.add_argument("--output", nargs="+", required=True)
    p.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2, 3])
    p.add_argument("--work", type=Path, required=True)
    p.add_argument("--python", default=sys.executable)
    p.add_argument("--tag", default="", help="suffix for the run folder (e.g. run2)")
    args = p.parse_args()

    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", args.ref) + (f"-{args.tag}" if args.tag else "")
    base = args.work / args.name / slug
    copy = base / "tree"
    build_copy(args.repo.resolve(), args.ref, args.archive, copy, args.copy_from, args.copy)
    head = subprocess.run(["git", "-C", str(args.repo), "rev-parse", args.ref],
                          check=True, capture_output=True, text=True).stdout.strip()
    record: dict[str, Any] = {"ref": args.ref, "commit": head, "cmd": args.cmd,
                              "seeds": {}, "dropped_keys": []}
    dropped_all: set[str] = set()
    for seed in args.seeds:
        out_dir = base / f"seed-{seed}"
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True)
        env = dict(os.environ, PYTHONHASHSEED=str(seed), PYTHONPATH=str(copy),
                   MPLBACKEND="Agg")
        # A bare leading ``python`` (also after ``;``/``&&``) means the given interpreter.
        cmd = re.sub(r"(^|[;&|]\s*)python ", lambda m: m.group(1) + args.python + " ",
                     args.cmd)
        with open(out_dir / "log.txt", "w") as log:
            rc = subprocess.run(cmd, shell=True, cwd=copy, env=env, stdout=log,
                                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL).returncode
        seed_rec: dict[str, Any] = {"returncode": rc, "outputs": {}}
        for rel in args.output:
            src = copy / rel
            if not src.exists():
                seed_rec["outputs"][rel] = "MISSING"
                continue
            tgt = out_dir / rel
            tgt.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, tgt)
            h, dropped = digest(src)
            dropped_all.update(dropped)
            seed_rec["outputs"][rel] = h
        record["seeds"][str(seed)] = seed_rec
        print(f"seed {seed}: rc={rc} " + " ".join(
            f"{Path(k).name}={str(v)[:12]}" for k, v in seed_rec["outputs"].items()), flush=True)
    record["dropped_keys"] = sorted(dropped_all)
    varies = {rel: len({record["seeds"][str(s)]["outputs"][rel] for s in args.seeds}) > 1
              for rel in args.output}
    record["varies"] = varies
    (base / "digests.json").write_text(json.dumps(record, indent=1) + "\n")
    for rel, v in varies.items():
        print(f"{'VARIES' if v else 'stable'} {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
