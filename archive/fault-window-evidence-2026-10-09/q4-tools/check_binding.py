"""Confirm which tree the inheritance module's frames are read from (scratch)."""
import importlib.util
import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import scripts.gemini37_image_55map_r2 as r2  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "inheritance_ladder",
    ROOT / "results/gemini37-image-55map-2026-09-13/inheritance-2026-09-20/inheritance_ladder.py")
inh = importlib.util.module_from_spec(spec)
sys.modules["inheritance_ladder"] = inh
spec.loader.exec_module(inh)
inh.bind_campaign("g3")
print("r2 file:", r2.__file__)
print("inh.rung_frame module file:", sys.modules[inh.rung_frame.__module__].__file__)
print("campaign root:", r2.CAMPAIGN_ROOT)
print("inh.HOME:", inh.HOME)
f = inh.rung_frame("arm2", 5)
for cid in ("candidate_21916", "candidate_26911", "candidate_35350"):
    print(cid, f.loc[f["candidate_key"] == cid, "mound_probability"].tolist()
          if "candidate_key" in f.columns else "(no candidate_key column)")
print(sorted(f.columns))
