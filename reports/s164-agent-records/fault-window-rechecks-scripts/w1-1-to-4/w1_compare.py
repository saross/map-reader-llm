"""Compare regenerated files with their committed versions (fault-window re-check W1-1 to W1-4).

Usage:
    python w1_compare.py OUT.json [--ignore KEY ...] [--unordered-list KEY ...] \
        LABEL=LOCAL_PATH=COMMIT:REPO_PATH ...

For each spec: SHA-256 of the regenerated file and of `git show COMMIT:REPO_PATH`
(byte-for-byte verdict); if they differ and both parse as JSON, a recursive
leaf diff in which a leaf is ignored only when a key on its path is in
--ignore (timestamps and machine paths, named per call), and lists under a
key named in --unordered-list are compared after sorting by their JSON text
(for results gathered in worker-completion order). Also reports whether
today's committed file (origin/main 90294a283) equals the generating commit's
version, and if not, the commits between that changed it.
Git is read from the main re-check worktree; nothing is written but OUT.json.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

GIT = str(Path.home() / "scratch/s164-fw-recheck-2026-10-14/wt")
TODAY = "90294a283"


def git_bytes(spec):
    r = subprocess.run(["git", "-C", GIT, "show", spec], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def sha(b):
    return None if b is None else hashlib.sha256(b).hexdigest()


def normalise(x, unordered):
    if isinstance(x, dict):
        return {k: normalise(v, unordered) if k not in unordered else
                sorted((normalise(i, unordered) for i in v),
                       key=lambda i: json.dumps(i, sort_keys=True))
                if isinstance(v, list) else normalise(v, unordered)
                for k, v in x.items()}
    if isinstance(x, list):
        return [normalise(i, unordered) for i in x]
    return x


def leaves(x, path=()):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from leaves(v, path + (str(k),))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from leaves(v, path + (f"[{i}]",))
    else:
        yield path, x


def main():
    out = Path(sys.argv[1])
    args = sys.argv[2:]
    ignore, unordered, specs = set(), set(), []
    i = 0
    while i < len(args):
        if args[i] == "--ignore":
            ignore.add(args[i + 1])
            i += 2
        elif args[i] == "--unordered-list":
            unordered.add(args[i + 1])
            i += 2
        else:
            specs.append(args[i])
            i += 1
    report = {"ignored_keys": sorted(ignore), "unordered_lists": sorted(unordered),
              "files": []}
    for spec in specs:
        label, local, gspec = spec.split("=", 2)
        commit, rpath = gspec.split(":", 1)
        lb = Path(local).read_bytes() if Path(local).exists() else None
        cb = git_bytes(gspec)
        tb = git_bytes(f"{TODAY}:{rpath}")
        rec = {"label": label, "local": local, "committed": gspec,
               "sha256_regenerated": sha(lb), "sha256_committed": sha(cb),
               "byte_identical": lb is not None and lb == cb,
               "today_equals_generating_commit": tb == cb}
        if tb != cb:
            rec["later_commits"] = subprocess.run(
                ["git", "-C", GIT, "log", "--format=%h %ad %s", "--date=short",
                 f"{commit}..{TODAY}", "--", rpath],
                capture_output=True, text=True).stdout.splitlines()
        if not rec["byte_identical"] and lb is not None and cb is not None:
            try:
                a, b = json.loads(cb), json.loads(lb)
            except ValueError:
                rec["json"] = False
            else:
                a, b = normalise(a, unordered), normalise(b, unordered)
                la, lb_ = dict(leaves(a)), dict(leaves(b))
                diffs, ign, maxabs = [], [], 0.0
                for k in sorted(set(la) | set(lb_)):
                    va, vb = la.get(k, "<absent>"), lb_.get(k, "<absent>")
                    if va == vb and type(va) is type(vb):
                        continue
                    row = ["/".join(k), va, vb]
                    if any(seg in ignore for seg in k):
                        ign.append(row)
                    else:
                        diffs.append(row)
                        if isinstance(va, (int, float)) and isinstance(vb, (int, float)) \
                                and not isinstance(va, bool):
                            maxabs = max(maxabs, abs(va - vb))
                rec.update({"json": True, "n_leaves_committed": len(la),
                            "n_leaves_regenerated": len(lb_),
                            "equal_ignoring_key_order": (json.dumps(a, sort_keys=True)
                                                         == json.dumps(b, sort_keys=True)),
                            "n_differing_leaves": len(diffs),
                            "n_ignored_differing_leaves": len(ign),
                            "max_abs_numeric_diff": maxabs,
                            "first_differences": diffs[:25], "ignored_differences": ign[:25]})
        report["files"].append(rec)
        status = "BYTE-IDENTICAL" if rec["byte_identical"] else (
            f"json diffs={rec.get('n_differing_leaves')} "
            f"ignored={rec.get('n_ignored_differing_leaves')}")
        print(f"{label}: {status}; today==gen: {rec['today_equals_generating_commit']}")
    out.write_text(json.dumps(report, indent=1, default=str) + "\n")


if __name__ == "__main__":
    main()
