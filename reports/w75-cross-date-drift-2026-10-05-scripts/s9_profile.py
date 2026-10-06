"""Profile per-request metadata for the S-9 replicate groups (W7.5)."""

import glob
import json
import statistics as st
from collections import Counter

GROUPS = {
    "G4 n1-outstanding image-t03": "outputs/h11/n1-outstanding-384/image-t03/run_*/*.meta.json",
    "G4 pv-diag image-n5 T0.3": "outputs/h11/pv-diag-384/image-n5/image-t0.3/run_*/*.meta.json",
    "G5 n1-outstanding pro-image-high-t0": "outputs/h11/n1-outstanding-384/pro-image-high-t0/run_*/*.meta.json",
    "G5 pv-diag flash-high-image T0.0": "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/run_*/*.meta.json",
}


def med(x):
    return round(st.median(x), 1) if x else None


for name, pat in GROUPS.items():
    metas = sorted(glob.glob(pat))
    mv, tt, fp, dates, commits = Counter(), Counter(), Counter(), Counter(), Counter()
    thoughts, outp, inp, img, cached = [], [], [], [], []
    thinking_cfg = Counter()
    for m in metas:
        d = json.load(open(m))
        commits[d.get("environment", {}).get("git_commit", "")[:9]] += 1
        cfg = d.get("configuration", {})
        thinking_cfg[str({k: cfg.get(k) for k in cfg if "think" in k.lower()})] += 1
        for it in d.get("per_item_metadata", []) or []:
            mv[it.get("model_version")] += 1
            tt[it.get("traffic_type")] += 1
            fp[it.get("system_fingerprint")] += 1
            ts = (it.get("request_timestamp") or "")[:10]
            dates[ts] += 1
            t = it.get("tokens") or {}
            if t.get("thoughts") is not None:
                thoughts.append(t.get("thoughts"))
            elif t.get("thoughts_tokens") is not None:
                thoughts.append(t.get("thoughts_tokens"))
            for key, lst in (
                ("output_tokens", outp),
                ("input_tokens", inp),
                ("cached_input_tokens", cached),
            ):
                if t.get(key) is not None:
                    lst.append(t[key])
            mb = it.get("modality_breakdown") or {}
            for e in (mb.get("prompt") or []) if isinstance(mb, dict) else []:
                if "IMAGE" in str(e.get("modality")):
                    img.append(e.get("count"))
    print(f"== {name}: {len(metas)} metas; commits {dict(commits)}")
    print(f"   dates {dict(sorted(dates.items()))}")
    print(f"   model_version {dict(mv)}; traffic {dict(tt)}; fingerprints {len(fp)}")
    print(f"   thinking config {dict(thinking_cfg)}")
    print(
        f"   per-request median: input {med(inp)}, cached {med(cached)}, image {med(img)}, thoughts {med(thoughts)}, output {med(outp)} (n={len(thoughts)})"
    )
