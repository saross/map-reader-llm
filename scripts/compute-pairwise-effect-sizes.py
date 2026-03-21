#!/usr/bin/env python3
"""
Pairwise Bootstrap Effect Size Comparisons
===========================================

Computes bootstrap 95% confidence intervals for effect sizes (F1, precision,
recall differences) between pairs of detection conditions. Designed to run on
sapphire (12C/24T) with multiprocessing.

Covers 52 comparisons across 7 groups:
  A: PV-filtered vs proposer-only (26 comparisons)
  B: PV vs best non-PV consensus (6 comparisons)
  C: Top PV vs each other (6 comparisons)
  D: Cost-efficiency (4 comparisons)
  E: Track effect under PV (4 comparisons)
  F: Thinking level under PV (3 comparisons)
  G: Verifier strategy (3 comparisons)

Each comparison uses bootstrap_effect_size_ci() methodology: paired tile-level
bootstrap with 1000 iterations, seed=42, two-sided p-values for False Discovery
Rate (FDR) correction.

Usage:
    python scripts/compute-pairwise-effect-sizes.py \\
        --data-dir /path/to/data \\
        --pv-dir /path/to/pv-data \\
        --output /path/to/pairwise-effect-sizes.json \\
        --workers 20

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import argparse
import json
import logging
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import geopandas as gpd

# ---------------------------------------------------------------------------
# Library imports
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.lib_advanced_metrics import (  # noqa: E402
    bootstrap_effect_size_ci,
)
from scripts.lib_consensus import (  # noqa: E402
    build_pv_gdf,
    generate_consensus_gdf,
    load_geojson_gdf,
    load_shared_data,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(processName)s] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# N=30 source run directories (relative to data-dir's retest/)
N30_TRACKS = {
    "text": "retest/phase3a/track2-text/T0.7",
    "image": "retest/phase3a/track1-image/T0.7",
    "high": "retest/phase3a-replication/high",
    "minimal": "retest/phase3a-replication/minimal",
}


# ===================================================================
# Comparison definitions
# ===================================================================

def define_all_comparisons(
    data_dir: Path,
    pv_dir: Path,
) -> list[dict]:
    """
    Define all 52 pairwise comparisons.

    Each comparison is a dict with:
      - name: Human-readable comparison name
      - group: Group letter (A-G)
      - condition_a: Dict describing condition A
      - condition_b: Dict describing condition B

    Condition types:
      - "pv": PV-filtered results (needs pv_results_dir, manifest_dir, sweep_dir)
      - "geojson": Direct GeoJSON file (needs geojson_path)
      - "consensus_n30": On-the-fly consensus from N=30 runs (needs track, threshold)

    Args:
        data_dir: Base data directory (references, bounds, retest, consensus-proposers).
        pv_dir: Directory containing PV experiment data (results, crops, sweeps).

    Returns:
        List of comparison definition dicts.
    """
    comparisons = []

    # --- PV experiment definitions ---
    # Maps PV short name to (pv_results_dir, manifest_dir, sweep_dir) relative paths
    pv_experiments = {
        "pv-01-adversarial-text": {
            "results": pv_dir / "results" / "adversarial-text-150" / "text-n1-t0.0-minimal",
            "manifest": pv_dir / "crops" / "text-n1-t0.0-minimal",
            "sweep": pv_dir / "sweeps" / "phase1" / "adversarial-text-150" / "text-n1-t0.0-minimal",
        },
        "pv-02-canonical-last": {
            "results": pv_dir / "results" / "phase2" / "02-canonical-last",
            "manifest": pv_dir / "crops" / "02-canonical-last",
            "sweep": pv_dir / "sweeps" / "phase2" / "02-canonical-last",
        },
        "pv-03-high-text-t0.3": {
            "results": pv_dir / "results" / "phase2" / "03-high-text-t0.3",
            "manifest": pv_dir / "crops" / "03-high-text-t0.3",
            "sweep": pv_dir / "sweeps" / "phase2" / "03-high-text-t0.3",
        },
        "pv-04-rep-high": {
            "results": pv_dir / "results" / "phase2" / "04-rep-high",
            "manifest": pv_dir / "crops" / "04-rep-high",
            "sweep": pv_dir / "sweeps" / "phase2" / "04-rep-high",
        },
        "pv-05-image-terse": {
            "results": pv_dir / "results" / "phase2" / "05-image-terse",
            "manifest": pv_dir / "crops" / "05-image-terse",
            "sweep": pv_dir / "sweeps" / "phase2" / "05-image-terse",
        },
        "pv-06-text-1of10": {
            "results": pv_dir / "results" / "phase2" / "06-text-1of10",
            "manifest": pv_dir / "crops" / "06-text-1of10",
            "sweep": pv_dir / "sweeps" / "phase2" / "06-text-1of10",
        },
        "pv-07-text-2of10": {
            "results": pv_dir / "results" / "phase2" / "07-text-2of10",
            "manifest": pv_dir / "crops" / "07-text-2of10",
            "sweep": pv_dir / "sweeps" / "phase2" / "07-text-2of10",
        },
        "pv-08-text-3of10": {
            "results": pv_dir / "results" / "phase2" / "08-text-3of10",
            "manifest": pv_dir / "crops" / "08-text-3of10",
            "sweep": pv_dir / "sweeps" / "phase2" / "08-text-3of10",
        },
        "pv-09-text-5of10": {
            "results": pv_dir / "results" / "phase2" / "09-text-5of10",
            "manifest": pv_dir / "crops" / "09-text-5of10",
            "sweep": pv_dir / "sweeps" / "phase2" / "09-text-5of10",
        },
        "pv-10-image-1of10": {
            "results": pv_dir / "results" / "phase2" / "10-image-1of10",
            "manifest": pv_dir / "crops" / "10-image-1of10",
            "sweep": pv_dir / "sweeps" / "phase2" / "10-image-1of10",
        },
        "pv-11-image-2of10": {
            "results": pv_dir / "results" / "phase2" / "11-image-2of10",
            "manifest": pv_dir / "crops" / "11-image-2of10",
            "sweep": pv_dir / "sweeps" / "phase2" / "11-image-2of10",
        },
        "pv-12-image-3of10": {
            "results": pv_dir / "results" / "phase2" / "12-image-3of10",
            "manifest": pv_dir / "crops" / "12-image-3of10",
            "sweep": pv_dir / "sweeps" / "phase2" / "12-image-3of10",
        },
        "pv-13-image-5of10": {
            "results": pv_dir / "results" / "phase2" / "13-image-5of10",
            "manifest": pv_dir / "crops" / "13-image-5of10",
            "sweep": pv_dir / "sweeps" / "phase2" / "13-image-5of10",
        },
        "pv-14-rep-min-1of10": {
            "results": pv_dir / "results" / "phase2" / "14-rep-min-1of10",
            "manifest": pv_dir / "crops" / "14-rep-min-1of10",
            "sweep": pv_dir / "sweeps" / "phase2" / "14-rep-min-1of10",
        },
        "pv-15-text-t0.7": {
            "results": pv_dir / "results" / "phase2" / "15-text-t0.7",
            "manifest": pv_dir / "crops" / "15-text-t0.7",
            "sweep": pv_dir / "sweeps" / "phase2" / "15-text-t0.7",
        },
        "pv-16-text-t1.0": {
            "results": pv_dir / "results" / "phase2" / "16-text-t1.0",
            "manifest": pv_dir / "crops" / "16-text-t1.0",
            "sweep": pv_dir / "sweeps" / "phase2" / "16-text-t1.0",
        },
        "pv-17-image-t0.0": {
            "results": pv_dir / "results" / "phase2" / "17-image-t0.0",
            "manifest": pv_dir / "crops" / "17-image-t0.0",
            "sweep": pv_dir / "sweeps" / "phase2" / "17-image-t0.0",
        },
        "pv-18-high-text-t0.7": {
            "results": pv_dir / "results" / "phase2" / "18-high-text-t0.7",
            "manifest": pv_dir / "crops" / "18-high-text-t0.7",
            "sweep": pv_dir / "sweeps" / "phase2" / "18-high-text-t0.7",
        },
        "pv-19-brief-text": {
            "results": pv_dir / "results" / "phase2" / "19-brief-text",
            "manifest": pv_dir / "crops" / "19-brief-text",
            "sweep": pv_dir / "sweeps" / "phase2" / "19-brief-text",
        },
        "pv-20-image-t0.7-n1": {
            "results": pv_dir / "results" / "phase2" / "20-image-t0.7-n1",
            "manifest": pv_dir / "crops" / "20-image-t0.7-n1",
            "sweep": pv_dir / "sweeps" / "phase2" / "20-image-t0.7-n1",
        },
        "pv-21-text-25of30": {
            "results": pv_dir / "results" / "phase2" / "21-text-25of30",
            "manifest": pv_dir / "crops" / "21-text-25of30",
            "sweep": pv_dir / "sweeps" / "phase2" / "21-text-25of30",
        },
        "pv-22-text-1of30": {
            "results": pv_dir / "results" / "phase2" / "22-text-1of30",
            "manifest": pv_dir / "crops" / "22-text-1of30",
            "sweep": pv_dir / "sweeps" / "phase2" / "22-text-1of30",
        },
        "pv-23-image-20of30": {
            "results": pv_dir / "results" / "phase2" / "23-image-20of30",
            "manifest": pv_dir / "crops" / "23-image-20of30",
            "sweep": pv_dir / "sweeps" / "phase2" / "23-image-20of30",
        },
        "pv-24-image-1of30": {
            "results": pv_dir / "results" / "phase2" / "24-image-1of30",
            "manifest": pv_dir / "crops" / "24-image-1of30",
            "sweep": pv_dir / "sweeps" / "phase2" / "24-image-1of30",
        },
        "pv-25-high-20of30": {
            "results": pv_dir / "results" / "phase2" / "25-high-20of30",
            "manifest": pv_dir / "crops" / "25-high-20of30",
            "sweep": pv_dir / "sweeps" / "phase2" / "25-high-20of30",
        },
        "pv-26-high-25of30": {
            "results": pv_dir / "results" / "phase2" / "26-high-25of30",
            "manifest": pv_dir / "crops" / "26-high-25of30",
            "sweep": pv_dir / "sweeps" / "phase2" / "26-high-25of30",
        },
        # Phase 1 verifier experiments (same proposer, different verifier)
        "pv-brief-text-150": {
            "results": pv_dir / "results" / "brief-text-150" / "text-n1-t0.0-minimal",
            "manifest": pv_dir / "crops" / "text-n1-t0.0-minimal",
            "sweep": pv_dir / "sweeps" / "phase1" / "brief-text-150" / "text-n1-t0.0-minimal",
        },
        "pv-checklist-text-150": {
            "results": pv_dir / "results" / "checklist-text-150" / "text-n1-t0.0-minimal",
            "manifest": pv_dir / "crops" / "text-n1-t0.0-minimal",
            "sweep": pv_dir / "sweeps" / "phase1" / "checklist-text-150" / "text-n1-t0.0-minimal",
        },
    }

    # --- Proposer GeoJSON definitions ---
    # Maps proposer short name to GeoJSON path (relative to data_dir)
    proposer_geojsons = {
        "proposer-text-t0.0": data_dir / "retest" / "phase2b" / "track2-text" / "T0.0" / "run_1" / "detections_T0.0_run01.geojson",
        "proposer-canonical-last": data_dir / "retest" / "phase2e" / "canonical-last" / "run_1" / "detections_canonical-last_run01.geojson",
        "proposer-high-t0.3": data_dir / "retest" / "phase3a-high" / "track2-text" / "T0.3" / "run_1" / "detections_T0.3_run01.geojson",
        "proposer-rep-high": data_dir / "retest" / "phase3a-replication" / "high" / "run_1" / "detections_high_run01.geojson",
        "proposer-image-terse": data_dir / "retest" / "phase2d" / "track1-image" / "terse" / "run_1" / "detections_terse_run01.geojson",
        "proposer-text-t0.7": data_dir / "retest" / "phase2b" / "track2-text" / "T0.7" / "run_1" / "detections_T0.7_run01.geojson",
        "proposer-text-t1.0": data_dir / "retest" / "phase2b" / "track2-text" / "T1.0" / "run_1" / "detections_T1.0_run01.geojson",
        "proposer-image-t0.0": data_dir / "retest" / "phase2b" / "track1-image" / "T0.0" / "run_1" / "detections_T0.0_run01.geojson",
        "proposer-high-t0.7": data_dir / "retest" / "phase3a-high" / "track2-text" / "T0.7" / "run_1" / "detections_T0.7_run01.geojson",
        "proposer-brief-text": data_dir / "retest" / "phase2a" / "brief-text" / "run_1" / "detections_brief-text_run01.geojson",
        "proposer-image-t0.7": data_dir / "retest" / "phase3a" / "track1-image" / "T0.7" / "run_1" / "detections_T0.7_run01.geojson",
    }

    # Consensus proposer GeoJSONs (pre-built)
    consensus_geojsons = {
        "consensus-text-1of10": data_dir / "consensus-proposers" / "3a-text-t0.7-1of10.geojson",
        "consensus-text-2of10": data_dir / "consensus-proposers" / "3a-text-t0.7-2of10.geojson",
        "consensus-text-3of10": data_dir / "consensus-proposers" / "3a-text-t0.7-3of10.geojson",
        "consensus-text-5of10": data_dir / "consensus-proposers" / "3a-text-t0.7-5of10.geojson",
        "consensus-image-1of10": data_dir / "consensus-proposers" / "3a-image-t0.7-1of10.geojson",
        "consensus-image-2of10": data_dir / "consensus-proposers" / "3a-image-t0.7-2of10.geojson",
        "consensus-image-3of10": data_dir / "consensus-proposers" / "3a-image-t0.7-3of10.geojson",
        "consensus-image-5of10": data_dir / "consensus-proposers" / "3a-image-t0.7-5of10.geojson",
        "consensus-rep-min-1of10": data_dir / "consensus-proposers" / "3a-rep-minimal-1of10.geojson",
        "consensus-text-25of30": data_dir / "consensus-proposers" / "3a-text-t0.7-25of30.geojson",
        "consensus-text-1of30": data_dir / "consensus-proposers" / "3a-text-t0.7-1of30.geojson",
        "consensus-image-20of30": data_dir / "consensus-proposers" / "3a-image-t0.7-20of30.geojson",
        "consensus-image-1of30": data_dir / "consensus-proposers" / "3a-image-t0.7-1of30.geojson",
        "consensus-high-20of30": data_dir / "consensus-proposers" / "3a-rep-high-20of30.geojson",
        "consensus-high-25of30": data_dir / "consensus-proposers" / "3a-rep-high-25of30.geojson",
        "consensus-high-1of30": data_dir / "consensus-proposers" / "3a-rep-high-1of30.geojson",
    }

    # ---------------------------------------------------------------
    # GROUP A: PV vs proposer-only (26 comparisons: 01-26)
    # Each PV experiment vs its unfiltered proposer
    # ---------------------------------------------------------------
    group_a_pairs = [
        # (pv_name, proposer_or_consensus_name)
        ("pv-01-adversarial-text", "proposer-text-t0.0"),
        ("pv-02-canonical-last", "proposer-canonical-last"),
        ("pv-03-high-text-t0.3", "proposer-high-t0.3"),
        ("pv-04-rep-high", "proposer-rep-high"),
        ("pv-05-image-terse", "proposer-image-terse"),
        ("pv-06-text-1of10", "consensus-text-1of10"),
        ("pv-07-text-2of10", "consensus-text-2of10"),
        ("pv-08-text-3of10", "consensus-text-3of10"),
        ("pv-09-text-5of10", "consensus-text-5of10"),
        ("pv-10-image-1of10", "consensus-image-1of10"),
        ("pv-11-image-2of10", "consensus-image-2of10"),
        ("pv-12-image-3of10", "consensus-image-3of10"),
        ("pv-13-image-5of10", "consensus-image-5of10"),
        ("pv-14-rep-min-1of10", "consensus-rep-min-1of10"),
        ("pv-15-text-t0.7", "proposer-text-t0.7"),
        ("pv-16-text-t1.0", "proposer-text-t1.0"),
        ("pv-17-image-t0.0", "proposer-image-t0.0"),
        ("pv-18-high-text-t0.7", "proposer-high-t0.7"),
        ("pv-19-brief-text", "proposer-brief-text"),
        ("pv-20-image-t0.7-n1", "proposer-image-t0.7"),
        ("pv-21-text-25of30", "consensus-text-25of30"),
        ("pv-22-text-1of30", "consensus-text-1of30"),
        ("pv-23-image-20of30", "consensus-image-20of30"),
        ("pv-24-image-1of30", "consensus-image-1of30"),
        ("pv-25-high-20of30", "consensus-high-20of30"),
        ("pv-26-high-25of30", "consensus-high-25of30"),
    ]

    for pv_name, baseline_name in group_a_pairs:
        pv_def = pv_experiments[pv_name]
        condition_a = {
            "type": "pv",
            "label": pv_name,
            **pv_def,
        }
        if baseline_name in proposer_geojsons:
            condition_b = {
                "type": "geojson",
                "label": baseline_name,
                "geojson_path": proposer_geojsons[baseline_name],
            }
        else:
            condition_b = {
                "type": "geojson",
                "label": baseline_name,
                "geojson_path": consensus_geojsons[baseline_name],
            }
        comparisons.append({
            "name": f"A:{pv_name}_vs_{baseline_name}",
            "group": "A",
            "condition_a": condition_a,
            "condition_b": condition_b,
        })

    # ---------------------------------------------------------------
    # GROUP B: PV vs best non-PV consensus (6 comparisons)
    # ---------------------------------------------------------------
    group_b_pairs = [
        ("pv-09-text-5of10", "consensus-high-25of30"),
        ("pv-08-text-3of10", "consensus-high-20of30"),
        ("pv-25-high-20of30", "consensus-high-25of30"),
        ("pv-07-text-2of10", "consensus-high-25of30"),
        ("pv-21-text-25of30", "consensus-text-25of30"),
        ("pv-26-high-25of30", "consensus-high-25of30"),
    ]
    for pv_name, consensus_name in group_b_pairs:
        pv_def = pv_experiments[pv_name]
        comparisons.append({
            "name": f"B:{pv_name}_vs_{consensus_name}",
            "group": "B",
            "condition_a": {"type": "pv", "label": pv_name, **pv_def},
            "condition_b": {
                "type": "geojson",
                "label": consensus_name,
                "geojson_path": consensus_geojsons[consensus_name],
            },
        })

    # ---------------------------------------------------------------
    # GROUP C: Top PV vs each other (6 comparisons)
    # ---------------------------------------------------------------
    group_c_pairs = [
        ("pv-09-text-5of10", "pv-08-text-3of10"),
        ("pv-09-text-5of10", "pv-25-high-20of30"),
        ("pv-08-text-3of10", "pv-07-text-2of10"),
        ("pv-09-text-5of10", "pv-07-text-2of10"),
        ("pv-08-text-3of10", "pv-25-high-20of30"),
        ("pv-25-high-20of30", "pv-07-text-2of10"),
    ]
    for pv_a, pv_b in group_c_pairs:
        pv_def_a = pv_experiments[pv_a]
        pv_def_b = pv_experiments[pv_b]
        comparisons.append({
            "name": f"C:{pv_a}_vs_{pv_b}",
            "group": "C",
            "condition_a": {"type": "pv", "label": pv_a, **pv_def_a},
            "condition_b": {"type": "pv", "label": pv_b, **pv_def_b},
        })

    # ---------------------------------------------------------------
    # GROUP D: Cost-efficiency (4 comparisons)
    # PV single-pass vs heavy consensus
    # ---------------------------------------------------------------
    group_d_pairs = [
        # PV text T=0.0 N=1 (2 passes) vs Consensus text 25-of-30 (30 passes)
        ("pv-01-adversarial-text", "consensus-text-25of30"),
        # PV text T=0.7 N=1 (2 passes) vs Consensus text 15-of-30 (30 passes)
        ("pv-15-text-t0.7", "consensus_n30:text/15"),
        # PV text T=0.0 N=1 (2 passes) vs Consensus text 10-of-30 (30 passes)
        ("pv-01-adversarial-text", "consensus_n30:text/10"),
        # PV text 3-of-10 (11 passes) vs Consensus HIGH 25-of-30 (30 passes)
        ("pv-08-text-3of10", "consensus-high-25of30"),
    ]
    for pv_name, baseline in group_d_pairs:
        pv_def = pv_experiments[pv_name]
        condition_a = {"type": "pv", "label": pv_name, **pv_def}
        if baseline.startswith("consensus_n30:"):
            # On-the-fly consensus generation
            parts = baseline.split(":")[-1].split("/")
            track = parts[0]
            threshold = int(parts[1])
            condition_b = {
                "type": "consensus_n30",
                "label": f"consensus-{track}-{threshold}of30",
                "track": track,
                "threshold": threshold,
            }
        elif baseline in consensus_geojsons:
            condition_b = {
                "type": "geojson",
                "label": baseline,
                "geojson_path": consensus_geojsons[baseline],
            }
        else:
            raise ValueError(f"Unknown baseline: {baseline}")
        comparisons.append({
            "name": f"D:{pv_name}_vs_{condition_b['label']}",
            "group": "D",
            "condition_a": condition_a,
            "condition_b": condition_b,
        })

    # ---------------------------------------------------------------
    # GROUP E: Track effect under PV (4 comparisons)
    # text vs image at same vote threshold
    # ---------------------------------------------------------------
    group_e_pairs = [
        ("pv-09-text-5of10", "pv-13-image-5of10"),
        ("pv-08-text-3of10", "pv-12-image-3of10"),
        ("pv-07-text-2of10", "pv-11-image-2of10"),
        ("pv-06-text-1of10", "pv-10-image-1of10"),
    ]
    for pv_a, pv_b in group_e_pairs:
        pv_def_a = pv_experiments[pv_a]
        pv_def_b = pv_experiments[pv_b]
        comparisons.append({
            "name": f"E:{pv_a}_vs_{pv_b}",
            "group": "E",
            "condition_a": {"type": "pv", "label": pv_a, **pv_def_a},
            "condition_b": {"type": "pv", "label": pv_b, **pv_def_b},
        })

    # ---------------------------------------------------------------
    # GROUP F: Thinking level under PV (3 comparisons)
    # HIGH vs minimal thinking at matched proposer conditions
    # ---------------------------------------------------------------
    group_f_pairs = [
        # PV HIGH 20-of-30 vs PV text 5-of-10 (HIGH+PV vs minimal+PV)
        ("pv-25-high-20of30", "pv-09-text-5of10"),
        # PV HIGH N=1 T=0.3 vs PV text N=1 T=0.0 (single-pass comparison)
        ("pv-03-high-text-t0.3", "pv-01-adversarial-text"),
        # PV HIGH N=1 T=0.7 vs PV text N=1 T=0.7 (same temp, different thinking)
        ("pv-18-high-text-t0.7", "pv-15-text-t0.7"),
    ]
    for pv_a, pv_b in group_f_pairs:
        pv_def_a = pv_experiments[pv_a]
        pv_def_b = pv_experiments[pv_b]
        comparisons.append({
            "name": f"F:{pv_a}_vs_{pv_b}",
            "group": "F",
            "condition_a": {"type": "pv", "label": pv_a, **pv_def_a},
            "condition_b": {"type": "pv", "label": pv_b, **pv_def_b},
        })

    # ---------------------------------------------------------------
    # GROUP G: Verifier strategy (3 comparisons)
    # All on the same proposer (text T=0.0 N=1)
    # ---------------------------------------------------------------
    group_g_pairs = [
        ("pv-01-adversarial-text", "pv-checklist-text-150"),
        ("pv-01-adversarial-text", "pv-brief-text-150"),
        ("pv-checklist-text-150", "pv-brief-text-150"),
    ]
    for pv_a, pv_b in group_g_pairs:
        pv_def_a = pv_experiments[pv_a]
        pv_def_b = pv_experiments[pv_b]
        comparisons.append({
            "name": f"G:{pv_a}_vs_{pv_b}",
            "group": "G",
            "condition_a": {"type": "pv", "label": pv_a, **pv_def_a},
            "condition_b": {"type": "pv", "label": pv_b, **pv_def_b},
        })

    # NOTE: Former Group H (cost-efficiency headline) was removed — its
    # entries duplicated comparisons already present in Groups B and D.

    return comparisons


# ===================================================================
# Worker function (runs in subprocess)
# ===================================================================

def run_one_comparison(
    comparison: dict,
    data_dir_str: str,
    n_iterations: int,
    random_seed: int,
) -> tuple[str, dict]:
    """
    Worker function: build GDFs for both conditions and compute effect size.

    This function runs in a subprocess. It loads shared data from file paths
    (cannot share GeoDataFrames across processes), builds condition GDFs, and
    computes the pairwise bootstrap effect size CI.

    Args:
        comparison: Comparison definition dict.
        data_dir_str: String path to base data directory.
        n_iterations: Bootstrap iterations.
        random_seed: Random seed for reproducibility.

    Returns:
        Tuple of (comparison_name, result_dict).
    """
    name = comparison["name"]
    t0 = time.time()

    try:
        # Load shared data in each subprocess
        data_dir = Path(data_dir_str)
        gdf_ref, gdf_bounds = load_shared_data(data_dir)

        # Build condition A GeoDataFrame
        cond_a = comparison["condition_a"]
        gdf_a = _build_condition_gdf(cond_a, data_dir)
        n_det_a = len(gdf_a)

        # Build condition B GeoDataFrame
        cond_b = comparison["condition_b"]
        gdf_b = _build_condition_gdf(cond_b, data_dir)
        n_det_b = len(gdf_b)

        if gdf_a.empty:
            return name, {"error": f"Condition A ({cond_a['label']}) produced empty GDF"}
        if gdf_b.empty:
            return name, {"error": f"Condition B ({cond_b['label']}) produced empty GDF"}

        # Both conditions use the same bounds
        result = bootstrap_effect_size_ci(
            gdf_det_a=gdf_a,
            gdf_bounds_a=gdf_bounds,
            gdf_det_b=gdf_b,
            gdf_bounds_b=gdf_bounds,
            gdf_ref=gdf_ref,
            n_iterations=n_iterations,
            random_seed=random_seed,
            return_p_values=True,
        )

        elapsed = time.time() - t0
        result["condition_a"] = cond_a["label"]
        result["condition_b"] = cond_b["label"]
        result["n_detections_a"] = n_det_a
        result["n_detections_b"] = n_det_b
        result["group"] = comparison["group"]
        result["elapsed_seconds"] = round(elapsed, 1)

        f1_diff = result.get("f1_difference", {})
        logger.info(
            "DONE %s — dF1=%.3f [%.3f, %.3f] p=%.4f (%d vs %d det, %.1fs)",
            name,
            f1_diff.get("mean", 0),
            f1_diff.get("ci_lower", 0),
            f1_diff.get("ci_upper", 0),
            f1_diff.get("p_value", 1),
            n_det_a,
            n_det_b,
            elapsed,
        )
        return name, result

    except Exception as e:
        elapsed = time.time() - t0
        logger.error("FAILED %s after %.1fs: %s", name, elapsed, e)
        return name, {"error": str(e), "elapsed_seconds": round(elapsed, 1)}


def _build_condition_gdf(
    condition: dict,
    data_dir: Path,
) -> gpd.GeoDataFrame:
    """
    Build a GeoDataFrame from a condition definition.

    Args:
        condition: Condition dict with 'type' and type-specific keys.
        data_dir: Base data directory.

    Returns:
        GeoDataFrame with 'source_tile' column and correct CRS.
    """
    cond_type = condition["type"]

    if cond_type == "pv":
        return build_pv_gdf(
            pv_results_dir=Path(condition["results"]),
            manifest_dir=Path(condition["manifest"]),
            sweep_dir=Path(condition["sweep"]),
        )

    elif cond_type == "geojson":
        return load_geojson_gdf(Path(condition["geojson_path"]))

    elif cond_type == "consensus_n30":
        track = condition["track"]
        threshold = condition["threshold"]
        track_rel_path = N30_TRACKS[track]
        track_dir = data_dir / track_rel_path
        run_dirs = sorted(track_dir.glob("run_*"))
        return generate_consensus_gdf(run_dirs, threshold)

    else:
        raise ValueError(f"Unknown condition type: {cond_type}")


# ===================================================================
# Main orchestration
# ===================================================================

def validate_paths(comparisons: list[dict]) -> list[str]:
    """
    Validate that all required files exist before running comparisons.

    Args:
        comparisons: List of comparison definitions.

    Returns:
        List of error messages for missing files (empty if all OK).
    """
    errors = []
    checked = set()

    for comp in comparisons:
        for cond_key in ("condition_a", "condition_b"):
            cond = comp[cond_key]
            cond_type = cond["type"]

            if cond_type == "pv":
                for path_key in ("results", "manifest", "sweep"):
                    p = Path(cond[path_key])
                    if str(p) not in checked:
                        checked.add(str(p))
                        if not p.exists():
                            errors.append(f"Missing {path_key}: {p}")
                        else:
                            # Check specific files
                            if path_key == "results":
                                prob_f = p / "probabilities.json"
                                if not prob_f.exists():
                                    errors.append(f"Missing probabilities.json in {p}")
                            elif path_key == "manifest":
                                man_f = p / "candidate_manifest.json"
                                if not man_f.exists():
                                    errors.append(f"Missing candidate_manifest.json in {p}")
                            elif path_key == "sweep":
                                sw_f = p / "threshold_sweep.json"
                                if not sw_f.exists():
                                    errors.append(f"Missing threshold_sweep.json in {p}")

            elif cond_type == "geojson":
                p = Path(cond["geojson_path"])
                if str(p) not in checked:
                    checked.add(str(p))
                    if not p.exists():
                        errors.append(f"Missing GeoJSON: {p}")

            elif cond_type == "consensus_n30":
                # Will be validated at runtime
                pass

    return errors


def main() -> None:
    """Main entry point: define comparisons, validate, run in parallel."""
    parser = argparse.ArgumentParser(
        description="Pairwise bootstrap effect size comparisons for PV pipeline.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        required=True,
        help="Base data directory (references/, bounds/, retest/, consensus-proposers/).",
    )
    parser.add_argument(
        "--pv-dir",
        type=Path,
        required=True,
        help="PV experiment data directory (results/, crops/, sweeps/).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output JSON file path.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=20,
        help="Number of parallel workers (default: 20).",
    )
    parser.add_argument(
        "--bootstrap",
        type=int,
        default=1000,
        help="Number of bootstrap iterations (default: 1000).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42).",
    )
    args = parser.parse_args()

    # Define all comparisons
    comparisons = define_all_comparisons(args.data_dir, args.pv_dir)
    logger.info("Defined %d pairwise comparisons", len(comparisons))

    # Count by group
    group_counts = Counter(c["group"] for c in comparisons)
    for group, count in sorted(group_counts.items()):
        logger.info("  Group %s: %d comparisons", group, count)

    # Validate paths
    errors = validate_paths(comparisons)
    if errors:
        logger.error("Path validation failed with %d errors:", len(errors))
        for err in errors:
            logger.error("  %s", err)
        sys.exit(1)
    logger.info("All paths validated OK")

    # Serialise comparison dicts (convert Path objects to strings)
    serialised_comparisons = []
    for comp in comparisons:
        sc = {
            "name": comp["name"],
            "group": comp["group"],
            "condition_a": _serialise_condition(comp["condition_a"]),
            "condition_b": _serialise_condition(comp["condition_b"]),
        }
        serialised_comparisons.append(sc)

    # Run comparisons in parallel
    results = {}
    t_start = time.time()

    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {}
        for comp in serialised_comparisons:
            future = executor.submit(
                run_one_comparison,
                comp,
                str(args.data_dir),
                args.bootstrap,
                args.seed,
            )
            futures[future] = comp["name"]

        completed = 0
        total = len(futures)

        for future in as_completed(futures):
            completed += 1
            comp_name = futures[future]
            try:
                name, result = future.result()
                results[name] = result
            except Exception as e:
                logger.error("Exception for %s: %s", comp_name, e)
                results[comp_name] = {"error": str(e)}

            if completed % 5 == 0 or completed == total:
                elapsed = time.time() - t_start
                rate = completed / (elapsed / 60) if elapsed > 0 else 0
                remaining = total - completed
                eta = remaining / rate * 60 if rate > 0 else 0
                logger.info(
                    "Progress: %d/%d (%.0f%%) — %.1f tasks/min — ETA %.0fs",
                    completed, total, 100 * completed / total, rate, eta,
                )

    # Write output
    elapsed_total = time.time() - t_start
    output_data = {
        "metadata": {
            "n_comparisons": len(results),
            "n_iterations": args.bootstrap,
            "random_seed": args.seed,
            "total_elapsed_seconds": round(elapsed_total, 1),
            "workers": args.workers,
        },
        "comparisons": results,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    logger.info(
        "COMPLETE: %d comparisons in %.1fs, written to %s",
        len(results), elapsed_total, args.output,
    )

    # Summary of errors
    n_errors = sum(1 for r in results.values() if "error" in r)
    if n_errors:
        logger.warning("%d comparisons had errors", n_errors)
        for name, result in sorted(results.items()):
            if "error" in result:
                logger.warning("  %s: %s", name, result["error"])


def _serialise_condition(condition: dict) -> dict:
    """Convert Path objects in a condition dict to strings for pickling."""
    result = {}
    for key, value in condition.items():
        if isinstance(value, Path):
            result[key] = str(value)
        else:
            result[key] = value
    return result


if __name__ == "__main__":
    main()
